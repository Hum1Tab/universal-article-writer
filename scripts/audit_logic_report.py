#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministic checks for a logic report (`logic-report.md`).

`logic-report.md` is part of the output contract, but the article audit never
reads it. This checks that the report contains a conclusion, premises (including
hidden-premise tags), an inference type, a counterexample or alternative
explanation, falsifiers, and open questions.

It does not judge whether the inference is valid or whether the falsifier is
adequate. Those remain human work.

Usage:
    python scripts/audit_logic_report.py --report logic-report.md --out report.json
    python scripts/audit_logic_report.py --report logic-report.md --strict
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

VERSION = "3.1.0"

REQUIRED = [
    ("結論", ("結論", "conclusion", "thesis"), "Critical"),
    ("前提", ("前提", "premise"), "Critical"),
    ("推論の型", ("推論の型", "inference", "deductive", "inductive", "演繹", "帰納", "因果"), "Major"),
    ("反例・代替説明", ("反例", "代替説明", "counterexample", "alternative"), "Major"),
    ("反証条件", ("反証条件", "falsifier", "撤回条件", "撤回"), "Critical"),
    ("未解決", ("未解決", "open question", "unresolved"), "Major"),
]


class Finding:
    def __init__(self, check: str, severity: str, message: str, line: int = 0) -> None:
        self.check = check
        self.severity = severity
        self.message = message
        self.line = line

    def as_dict(self) -> Dict[str, object]:
        return {
            "check": self.check,
            "severity": self.severity,
            "message": self.message,
            "line": self.line,
        }


def headings(lines: Sequence[str]) -> List[tuple[int, int, str]]:
    result = []
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match:
            result.append((index, len(match.group(1)), match.group(2).strip()))
    return result


def find_heading(lines: Sequence[str], keywords: Sequence[str]) -> Optional[tuple[int, int]]:
    all_headings = headings(lines)
    for position, (index, level, title) in enumerate(all_headings):
        lowered = title.lower()
        if any(keyword.lower() in lowered for keyword in keywords):
            end = len(lines)
            for later_index, later_level, _ in all_headings[position + 1 :]:
                if later_level <= level:
                    end = later_index
                    break
            return index, end
    return None


def section_text(lines: Sequence[str], start: int, end: int) -> str:
    body = [line.strip() for line in lines[start + 1 : end] if line.strip() and not line.strip().startswith("#")]
    return "\n".join(body)


def audit(path: Path, claims_path: Optional[Path]) -> Dict[str, object]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    findings: List[Finding] = []

    for label, keywords, severity in REQUIRED:
        bounds = find_heading(lines, keywords)
        if bounds is None:
            findings.append(Finding("missing-section", severity, "「{}」に相当する見出しがない".format(label)))
            continue
        body = section_text(lines, *bounds)
        if len(body) < 20:
            findings.append(
                Finding(
                    "empty-section",
                    "Major",
                    "「{}」の内容が薄い（{}字）".format(label, len(body)),
                    line=bounds[0] + 1,
                )
            )

    tags = [tag for tag in ("[TEXT]", "[CONV]", "[ANALYST]") if tag in text]
    if not tags:
        findings.append(
            Finding(
                "premise-tags-missing",
                "Minor",
                "隠れた前提の由来タグ [TEXT] / [CONV] / [ANALYST] がない",
            )
        )

    load_bearing = 0
    if claims_path and claims_path.is_file():
        import csv

        try:
            with claims_path.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
        except Exception:
            rows = []
        load_bearing = sum(
            1 for row in rows if str(row.get("load_bearing", "")).strip().lower() in {"yes", "true", "1"}
        )
        if load_bearing and not re.search(r"\bC\d{2,}\b", text) and "荷重主張" not in text:
            findings.append(
                Finding(
                    "load-bearing-not-referenced",
                    "Major",
                    "荷重主張が{}件あるが、logic-report に主張IDも「荷重主張」もない".format(load_bearing),
                )
            )

    for pattern, label in [(r"\bTODO\b", "TODO"), (r"\bTBD\b", "TBD")]:
        matches = list(re.finditer(pattern, text))
        if matches:
            findings.append(
                Finding(
                    "placeholder",
                    "Minor",
                    "未解決のプレースホルダ '{}' が {} 回ある".format(label, len(matches)),
                    line=text[: matches[0].start()].count("\n") + 1,
                )
            )

    critical = sum(1 for finding in findings if finding.severity == "Critical")
    major = sum(1 for finding in findings if finding.severity == "Major")
    minor = sum(1 for finding in findings if finding.severity == "Minor")
    readiness = "NOT READY" if critical else ("CONDITIONAL" if major else "READY")

    return {
        "version": VERSION,
        "report": path.as_posix(),
        "summary": {
            "readiness": readiness,
            "critical": critical,
            "major": major,
            "minor": minor,
            "load_bearing_claims": load_bearing,
        },
        "findings": [finding.as_dict() for finding in findings],
        "limitations": [
            "推論の妥当性・反例の強さ・反証条件の十分性は判定しない。",
            "見出しと本文の有無だけを見る。",
        ],
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, help="logic-report.md")
    parser.add_argument("--claims", help="claims.csv (optional)")
    parser.add_argument("--out", help="write a JSON report")
    parser.add_argument("--strict", action="store_true", help="exit 2 on Major as well as Critical")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    path = Path(args.report)
    if not path.is_file():
        print("report not found: {}".format(path), file=sys.stderr)
        return 3

    try:
        report = audit(path, Path(args.claims) if args.claims else None)
    except Exception as exc:
        print("failed to audit {}: {}".format(path, exc), file=sys.stderr)
        return 3

    if args.out:
        Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        summary = report["summary"]
        print("=== Logic Report Audit v{} ===".format(VERSION))
        print("Report   : {}".format(path))
        print("Readiness: {}".format(summary["readiness"]))
        print(
            "Findings : Critical {} / Major {} / Minor {}".format(
                summary["critical"], summary["major"], summary["minor"]
            )
        )
        for finding in report["findings"]:
            print("[{:<8}] {:<26} {}".format(finding["severity"], finding["check"], finding["message"]))

    summary = report["summary"]
    if summary["critical"] or (args.strict and summary["major"]):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
