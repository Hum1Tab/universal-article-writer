#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministic checks for an evidence dossier (`dossier.md`).

The dossier is the human-facing summary. The article audit does not read it, so
before this script a model could ship a hollow dossier and still get READY.
This checks that the dossier contains the sections a skeptical reader needs.

It does not judge whether the objection is strong, whether the limits are
honest, or whether the AI disclosure is complete. Those remain human work.

Usage:
    python scripts/audit_dossier.py --dossier dossier.md --out report.json
    python scripts/audit_dossier.py --dossier dossier.md --strict
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
    ("結論", ("結論", "thesis", "conclusion"), "Critical"),
    ("最強の反論", ("最強の反論", "strongest objection", "objection"), "Critical"),
    ("限界", ("限界", "limits", "limitation", "適用範囲"), "Critical"),
    ("未確認", ("未確認", "unverified", "uncertainty"), "Major"),
    ("AI 開示", ("AI 利用", "AI利用", "AI の関与", "AI disclosure", "disclosure"), "Major"),
    ("監査", ("監査", "audit", "readiness"), "Major"),
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


def audit(path: Path) -> Dict[str, object]:
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
        "dossier": path.as_posix(),
        "summary": {"readiness": readiness, "critical": critical, "major": major, "minor": minor},
        "findings": [finding.as_dict() for finding in findings],
        "limitations": [
            "反論の強さ・限界の誠実さ・AI 開示の完全性は判定しない。",
            "見出しと本文の有無だけを見る。",
            "英語の見出しは一部だけ対応している。",
        ],
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dossier", required=True, help="dossier.md")
    parser.add_argument("--out", help="write a JSON report")
    parser.add_argument("--strict", action="store_true", help="exit 2 on Major as well as Critical")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    path = Path(args.dossier)
    if not path.is_file():
        print("dossier not found: {}".format(path), file=sys.stderr)
        return 3

    try:
        report = audit(path)
    except Exception as exc:
        print("failed to audit {}: {}".format(path, exc), file=sys.stderr)
        return 3

    if args.out:
        Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        summary = report["summary"]
        print("=== Dossier Audit v{} ===".format(VERSION))
        print("Dossier  : {}".format(path))
        print("Readiness: {}".format(summary["readiness"]))
        print(
            "Findings : Critical {} / Major {} / Minor {}".format(
                summary["critical"], summary["major"], summary["minor"]
            )
        )
        for finding in report["findings"]:
            print("[{:<8}] {:<18} {}".format(finding["severity"], finding["check"], finding["message"]))

    summary = report["summary"]
    if summary["critical"] or (args.strict and summary["major"]):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
