#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministic checks for a decision memo (`decision` mode).

This is not an article audit. It checks the structure that makes a decision
auditable: a one-sentence decision, at least three options including the status
quo, criteria fixed before evaluation, trade-offs, a recommendation, observable
exit conditions, reversibility, and visible unknowns.

It does not judge whether the decision is good, whether the evidence is true, or
whether the trade-off is acceptable. Those remain human work.

Usage:
    python scripts/audit_decision.py --memo decision-memo.md --out report.json
    python scripts/audit_decision.py --memo decision-memo.md --strict
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

VERSION = "3.1.0"

REQUIRED_SECTIONS = [
    ("決定", "決定"),
    ("選択肢", "選択肢"),
    ("評価基準", "評価基準"),
    ("トレードオフ", "トレードオフ"),
    ("推奨", "推奨"),
    ("撤退条件", "撤退条件"),
    ("未確認", "未確認"),
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


def section_bounds(lines: Sequence[str], keyword: str) -> Optional[tuple[int, int]]:
    all_headings = headings(lines)
    candidates = [
        (position, index, level, title)
        for position, (index, level, title) in enumerate(all_headings)
        if keyword in title
    ]
    if not candidates:
        return None

    def bare(title: str) -> str:
        return re.sub(r"^\d+(?:\.\d+)*[\.\s]*", "", title).strip()

    exact = [item for item in candidates if bare(item[3]) == keyword]
    position, index, level, _ = (exact or candidates)[-1]

    end = len(lines)
    for later_index, later_level, _ in all_headings[position + 1 :]:
        if later_level <= level:
            end = later_index
            break
    return index, end


def table_rows(lines: Sequence[str]) -> List[str]:
    rows = []
    for line in lines:
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        if all(re.fullmatch(r":?-{2,}:?", cell) for cell in cells):
            continue
        if cells[0] in {"ID", "案", "指標", "項目", "基準", "役割"}:
            continue
        rows.append(line)
    return rows


def first_content_line(lines: Sequence[str], start: int, end: int) -> str:
    for line in lines[start + 1 : end]:
        text = line.strip()
        if text and not text.startswith("#"):
            return text
    return ""


def audit(path: Path) -> Dict[str, object]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    findings: List[Finding] = []

    for keyword, label in REQUIRED_SECTIONS:
        if section_bounds(lines, keyword) is None:
            findings.append(Finding("missing-section", "Critical", "「{}」の見出しがない".format(label)))

    decision_bounds = section_bounds(lines, "決定")
    if decision_bounds:
        sentence = first_content_line(lines, *decision_bounds)
        if not sentence:
            findings.append(Finding("decision-empty", "Critical", "決定が空である"))
        elif len(sentence) > 300:
            findings.append(Finding("decision-too-long", "Major", "決定が長すぎる（300字超）"))
        elif not re.search(r"[。.!?]$", sentence):
            findings.append(Finding("decision-not-sentence", "Minor", "決定が1文で終わっていない"))

    options_bounds = section_bounds(lines, "選択肢")
    if options_bounds:
        option_rows = [
            row
            for row in table_rows(lines[options_bounds[0] : options_bounds[1]])
            if re.match(r"^\|\s*[A-Z]\s*\|", row)
        ]
        if len(option_rows) < 3:
            findings.append(
                Finding("options-too-few", "Major", "選択肢が3つ未満（{}行）".format(len(option_rows)))
            )
        if "現状維持" not in text:
            findings.append(Finding("status-quo-missing", "Major", "現状維持の選択肢がない"))
        for row in option_rows:
            cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
            if len([cell for cell in cells if cell]) < 4:
                findings.append(Finding("option-too-thin", "Minor", "選択肢の記述が薄い: {}".format(row[:60])))

    criteria_bounds = section_bounds(lines, "評価基準")
    evaluation_bounds = section_bounds(lines, "評価")
    if criteria_bounds and evaluation_bounds:
        if criteria_bounds[0] > evaluation_bounds[0]:
            findings.append(
                Finding("criteria-after-evaluation", "Major", "評価基準が評価表より後にある")
            )

    exit_bounds = section_bounds(lines, "撤退条件")
    if exit_bounds:
        exit_rows = table_rows(lines[exit_bounds[0] : exit_bounds[1]])
        if len(exit_rows) < 3:
            findings.append(
                Finding("exit-too-few", "Major", "撤退条件が3行未満（{}行）".format(len(exit_rows)))
            )
        observable = [
            row
            for row in exit_rows
            if re.search(r"\d", row) and re.search(r"%|pt|日|週|か月|20\d\d", row)
        ]
        if exit_rows and len(observable) < 3:
            findings.append(
                Finding(
                    "exit-not-observable",
                    "Major",
                    "指標・閾値・時点が揃った撤退条件が3行未満（{}行）".format(len(observable)),
                )
            )

    if "可逆性" not in text:
        findings.append(Finding("reversibility-missing", "Major", "可逆性の分類がない"))
    if "【未確認" not in text and "未確認" not in text:
        findings.append(Finding("unconfirmed-missing", "Minor", "未確認の記載がない"))

    critical = sum(1 for finding in findings if finding.severity == "Critical")
    major = sum(1 for finding in findings if finding.severity == "Major")
    minor = sum(1 for finding in findings if finding.severity == "Minor")
    readiness = "NOT READY" if critical else ("CONDITIONAL" if major else "READY")

    return {
        "version": VERSION,
        "memo": path.as_posix(),
        "summary": {
            "readiness": readiness,
            "critical": critical,
            "major": major,
            "minor": minor,
            "options": len(
                [
                    row
                    for row in table_rows(
                        lines[options_bounds[0] : options_bounds[1]] if options_bounds else []
                    )
                    if re.match(r"^\|\s*[A-Z]\s*\|", row)
                ]
            ),
        },
        "findings": [finding.as_dict() for finding in findings],
        "limitations": [
            "決定の内容・証拠の真偽・トレードオフの妥当性は判定しない。",
            "見出しと表の構造だけを見る。",
            "英語の見出しには対応していない（日本語テンプレート用）。",
        ],
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--memo", required=True, help="decision memo (Markdown)")
    parser.add_argument("--out", help="write a JSON report")
    parser.add_argument("--strict", action="store_true", help="exit 2 on Major as well as Critical")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    path = Path(args.memo)
    if not path.is_file():
        print("memo not found: {}".format(path), file=sys.stderr)
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
        print("=== Decision Memo Audit v{} ===".format(VERSION))
        print("Memo     : {}".format(path))
        print("Readiness: {}".format(summary["readiness"]))
        print(
            "Findings : Critical {} / Major {} / Minor {}".format(
                summary["critical"], summary["major"], summary["minor"]
            )
        )
        for finding in report["findings"]:
            print("[{:<8}] {:<24} {}".format(finding["severity"], finding["check"], finding["message"]))

    summary = report["summary"]
    if summary["critical"] or (args.strict and summary["major"]):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
