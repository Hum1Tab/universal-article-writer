#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministic cross-artifact checks for a delivered package.

Each artifact has its own audit. This checks that the artifacts agree with each
other: required files exist, claim evidence IDs exist in the source ledger,
article citations exist, load-bearing claims appear in the logic report, and a
missing machine audit is disclosed.

It does not verify phase order, semantic support, or article quality. Those are
process and human judgments.

Usage:
    python scripts/audit_package.py --dir out/ --out report.json
    python scripts/audit_package.py --dir out/ --strict
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set

VERSION = "3.1.0"

REQUIRED = ["sources.csv", "claims.csv", "dossier.md", "logic-report.md"]


class Finding:
    def __init__(self, check: str, severity: str, message: str) -> None:
        self.check = check
        self.severity = severity
        self.message = message

    def as_dict(self) -> Dict[str, object]:
        return {"check": self.check, "severity": self.severity, "message": self.message}


def read_csv(path: Path) -> List[Dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    except Exception:
        return []


def source_ids(rows: Sequence[Dict[str, str]]) -> Set[str]:
    return {str(row.get("id", "")).strip() for row in rows if str(row.get("id", "")).strip()}


def claim_ids(rows: Sequence[Dict[str, str]]) -> Set[str]:
    return {str(row.get("claim_id", "")).strip() for row in rows if str(row.get("claim_id", "")).strip()}


def evidence_ids(row: Dict[str, str]) -> Set[str]:
    raw = str(row.get("evidence_ids", ""))
    return {part.strip() for part in re.split(r"[;,]\s*", raw) if part.strip()}


def cited_sources(text: str) -> Set[str]:
    cited: Set[str] = set()
    for group in re.findall(r"\[([^\]]+)\]", text):
        for part in group.split(";"):
            match = re.match(r"\s*(S\d{2,})", part)
            if match:
                cited.add(match.group(1))
    return cited


def audit(directory: Path) -> Dict[str, object]:
    findings: List[Finding] = []

    for name in REQUIRED:
        if not (directory / name).is_file():
            findings.append(Finding("missing-artifact", "Critical", "必須ファイルがない: {}".format(name)))

    has_article = (directory / "article.md").is_file()
    has_decision = (directory / "decision-memo.md").is_file()
    if not has_article and not has_decision:
        findings.append(
            Finding("missing-deliverable", "Critical", "article.md も decision-memo.md もない")
        )
    elif has_article and has_decision:
        findings.append(
            Finding("ambiguous-mode", "Major", "article.md と decision-memo.md の両方がある")
        )

    sources = read_csv(directory / "sources.csv") if (directory / "sources.csv").is_file() else []
    claims = read_csv(directory / "claims.csv") if (directory / "claims.csv").is_file() else []
    source_set = source_ids(sources)
    claim_set = claim_ids(claims)

    if len(source_set) != len([row for row in sources if str(row.get("id", "")).strip()]):
        findings.append(Finding("duplicate-source-id", "Critical", "sources.csv の ID が重複している"))
    if len(claim_set) != len([row for row in claims if str(row.get("claim_id", "")).strip()]):
        findings.append(Finding("duplicate-claim-id", "Critical", "claims.csv の claim_id が重複している"))

    for row in claims:
        missing = evidence_ids(row) - source_set
        if missing:
            findings.append(
                Finding(
                    "claim-evidence-missing",
                    "Critical",
                    "主張 {} の証拠IDが sources.csv にない: {}".format(
                        row.get("claim_id", "?"), ", ".join(sorted(missing))
                    ),
                )
            )

    deliverable = directory / ("decision-memo.md" if has_decision else "article.md")
    if deliverable.is_file():
        missing = cited_sources(deliverable.read_text(encoding="utf-8")) - source_set
        if missing:
            findings.append(
                Finding(
                    "citation-source-missing",
                    "Critical",
                    "本文の引用IDが sources.csv にない: {}".format(", ".join(sorted(missing))),
                )
            )

    logic = directory / "logic-report.md"
    load_bearing = [
        row for row in claims if str(row.get("load_bearing", "")).strip().lower() in {"yes", "true", "1"}
    ]
    if logic.is_file() and load_bearing:
        text = logic.read_text(encoding="utf-8")
        if "荷重主張" not in text:
            unreferenced = [row.get("claim_id", "?") for row in load_bearing if row.get("claim_id") not in text]
            if unreferenced:
                findings.append(
                    Finding(
                        "load-bearing-not-in-logic-report",
                        "Major",
                        "荷重主張が logic-report にない: {}".format(", ".join(unreferenced)),
                    )
                )

    dossier = directory / "dossier.md"
    audit_report = directory / "audit-report.json"
    if dossier.is_file() and not audit_report.is_file():
        if "機械監査は未実行" not in dossier.read_text(encoding="utf-8"):
            findings.append(
                Finding(
                    "audit-status-undisclosed",
                    "Major",
                    "audit-report.json がないのに、dossier に「機械監査は未実行」がない",
                )
            )

    if audit_report.is_file():
        try:
            data = json.loads(audit_report.read_text(encoding="utf-8"))
            readiness = data.get("summary", {}).get("readiness")
            if readiness not in {"READY", "CONDITIONAL", "NOT READY"}:
                findings.append(Finding("audit-report-invalid", "Major", "audit-report.json の readiness が不正"))
        except Exception:
            findings.append(Finding("audit-report-invalid", "Major", "audit-report.json が読めない"))

    critical = sum(1 for finding in findings if finding.severity == "Critical")
    major = sum(1 for finding in findings if finding.severity == "Major")
    minor = sum(1 for finding in findings if finding.severity == "Minor")
    readiness = "NOT READY" if critical else ("CONDITIONAL" if major else "READY")

    return {
        "version": VERSION,
        "package": directory.as_posix(),
        "mode": "decision" if has_decision and not has_article else "article",
        "summary": {
            "readiness": readiness,
            "critical": critical,
            "major": major,
            "minor": minor,
            "sources": len(source_set),
            "claims": len(claim_set),
            "load_bearing_claims": len(load_bearing),
        },
        "findings": [finding.as_dict() for finding in findings],
        "limitations": [
            "フェーズの実行順序は検証しない。最終成果物の存在と相互参照だけを見る。",
            "引用が主張を支えているか、論証が妥当かは判定しない。",
        ],
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", required=True, help="package directory")
    parser.add_argument("--out", help="write a JSON report")
    parser.add_argument("--strict", action="store_true", help="exit 2 on Major as well as Critical")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    directory = Path(args.dir)
    if not directory.is_dir():
        print("package directory not found: {}".format(directory), file=sys.stderr)
        return 3

    try:
        report = audit(directory)
    except Exception as exc:
        print("failed to audit {}: {}".format(directory, exc), file=sys.stderr)
        return 3

    if args.out:
        Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        summary = report["summary"]
        print("=== Package Audit v{} ===".format(VERSION))
        print("Package  : {}".format(directory))
        print("Mode     : {}".format(report["mode"]))
        print("Readiness: {}".format(summary["readiness"]))
        print(
            "Findings : Critical {} / Major {} / Minor {}".format(
                summary["critical"], summary["major"], summary["minor"]
            )
        )
        for finding in report["findings"]:
            print("[{:<8}] {:<32} {}".format(finding["severity"], finding["check"], finding["message"]))

    summary = report["summary"]
    if summary["critical"] or (args.strict and summary["major"]):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
