#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_sources.py — 論理記事工房の書誌・出典台帳監査

依存ライブラリなし。Python 3.9+ で動作する。
ネットワーク検証は任意（--online）。失敗しても停止しない。

主な検査:
  - sources.csv の必須列・ID・重複
  - DOI / arXiv / URL / 出版年の形式
  - アクセス日の形式
  - verification の値と、撤回済み出典の使用
  - 同一 DOI / URL / タイトルの重複
  - 本文が参照する出典IDの存在
  - （--online）Crossref / doi.org / URL の存在確認

このスクリプトは「書誌が実在する」ことを保証しない。
オンライン確認は到達性の確認であり、内容・版・撤回の最終確認ではない。

使い方:
  python scripts/verify_sources.py --sources sources.csv
  python scripts/verify_sources.py --sources sources.csv --article article.md --out source-report.json
  python scripts/verify_sources.py --sources sources.csv --online --fail-on major

終了コード:
  0  監査完了（--fail-on の閾値未満）
  2  --fail-on の閾値に達した
  3  入力エラー
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "3.0.1"

SEVERITY_ORDER = {"critical": 0, "major": 1, "minor": 2, "info": 3}

ALLOWED_VERIFICATION = {
    "verified",
    "partial",
    "abstract-only",
    "secondary-only",
    "unverified",
    "retracted",
}
WEAK_VERIFICATION = {"abstract-only", "secondary-only", "unverified"}

ALLOWED_TYPES = {
    "journal",
    "preprint",
    "book",
    "chapter",
    "report",
    "dataset",
    "news",
    "web",
    "primary",
    "secondary",
    "interview",
    "law",
    "statistics",
    "other",
}

REQUIRED_COLUMNS = {"id", "title", "year", "verification"}
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
ARXIV_RE = re.compile(r"(arxiv[:\s]*)(\d{4}\.\d{4,5}(?:v\d+)?)", re.IGNORECASE)
ISBN10_RE = re.compile(r"\b\d{9}[\dX]\b", re.IGNORECASE)
ISBN13_RE = re.compile(r"\b97[89]\d{10}\b")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def configure_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_csv_rows(path: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = [name.strip() for name in (reader.fieldnames or [])]
        rows: List[Dict[str, str]] = []
        for raw in reader:
            row: Dict[str, str] = {}
            for key, value in raw.items():
                if key is None:
                    continue
                row[key.strip().lower()] = (value or "").strip()
            rows.append(row)
    return rows, fieldnames


def canonical_id(raw: str) -> Optional[str]:
    digits = re.sub(r"\D", "", raw or "")
    if not digits:
        return None
    return "S{}".format(int(digits))


def display_id(key: str) -> str:
    return "S{:02d}".format(int(key[1:]))


def isbn10_valid(value: str) -> bool:
    digits = re.sub(r"[^0-9Xx]", "", value)
    if len(digits) != 10:
        return False
    total = sum((10 - index) * (10 if char.upper() == "X" else int(char)) for index, char in enumerate(digits))
    return total % 11 == 0


def isbn13_valid(value: str) -> bool:
    digits = re.sub(r"\D", "", value)
    if len(digits) != 13:
        return False
    total = sum(int(char) * (1 if index % 2 == 0 else 3) for index, char in enumerate(digits))
    return total % 10 == 0


class Verifier:
    def __init__(self, sources_path: Path, article_path: Optional[Path], online: bool) -> None:
        self.sources_path = sources_path
        self.article_path = article_path
        self.online = online
        self.rows: List[Dict[str, str]] = []
        self.fieldnames: List[str] = []
        self.sources: Dict[str, Dict[str, str]] = {}
        self.findings: List[Dict[str, Any]] = []
        self.checks_run: List[str] = []
        self.online_results: List[Dict[str, Any]] = []

    def add(
        self,
        check: str,
        severity: str,
        message: str,
        source_id: Optional[str] = None,
        detail: str = "",
        repair: str = "",
    ) -> None:
        self.findings.append(
            {
                "check": check,
                "severity": severity,
                "source_id": source_id,
                "message": message,
                "detail": detail,
                "repair": repair,
            }
        )

    # -- offline ---------------------------------------------------------

    def load(self) -> None:
        self.checks_run.append("parse")
        self.rows, self.fieldnames = read_csv_rows(self.sources_path)
        missing = sorted(REQUIRED_COLUMNS - set(self.fieldnames))
        if missing:
            self.add(
                "columns-missing",
                "critical",
                "sources.csv に必須列がない: {}".format(", ".join(missing)),
                repair="assets/source-ledger.csv のヘッダーを使う。",
            )

    def check_rows(self) -> None:
        self.checks_run.append("rows")
        if not self.rows:
            self.add("sources-empty", "critical", "sources.csv にデータ行がない。")
            return

        seen_doi: Dict[str, str] = {}
        seen_url: Dict[str, str] = {}
        seen_title: Dict[str, str] = {}

        for index, row in enumerate(self.rows, start=2):
            key = canonical_id(row.get("id", ""))
            label = display_id(key) if key else "row {}".format(index)
            if not key:
                self.add("source-id-missing", "critical", "CSV {} 行目: id がない。".format(index))
                continue
            if key in self.sources:
                self.add(
                    "source-id-duplicate",
                    "critical",
                    "出典ID {} が重複している。".format(label),
                    source_id=label,
                )
                continue
            self.sources[key] = row

            title = row.get("title", "")
            if not title:
                self.add("source-title-missing", "major", "出典 {} の title が空。".format(label), source_id=label)

            year = row.get("year", "")
            if not year:
                self.add("source-year-missing", "major", "出典 {} の year が空。".format(label), source_id=label)
            elif not re.fullmatch(r"\d{4}", year):
                self.add(
                    "source-year-format",
                    "minor",
                    "出典 {} の year '{}' は4桁の西暦ではない。".format(label, year),
                    source_id=label,
                )
            elif not (1500 <= int(year) <= 2100):
                self.add(
                    "source-year-range",
                    "minor",
                    "出典 {} の year '{}' が想定範囲外。".format(label, year),
                    source_id=label,
                )

            verification = row.get("verification", "").lower()
            if not verification:
                self.add(
                    "source-verification-missing",
                    "major",
                    "出典 {} の verification が空。".format(label),
                    source_id=label,
                    repair="verified / partial / abstract-only / secondary-only / unverified / retracted のいずれかを書く。",
                )
            elif verification not in ALLOWED_VERIFICATION:
                self.add(
                    "source-verification-invalid",
                    "minor",
                    "出典 {} の verification '{}' は許容値ではない。".format(label, verification),
                    source_id=label,
                )

            source_type = row.get("type", "").lower()
            if source_type and source_type not in ALLOWED_TYPES:
                self.add(
                    "source-type-unknown",
                    "info",
                    "出典 {} の type '{}' は既知の分類ではない。".format(label, source_type),
                    source_id=label,
                )

            doi = row.get("doi", "").strip()
            if doi:
                normalized = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
                if not DOI_RE.match(normalized):
                    self.add(
                        "doi-format",
                        "minor",
                        "出典 {} の DOI '{}' が形式に合わない。".format(label, doi),
                        source_id=label,
                        repair="10.xxxx/yyyy の形式で書く（doi.org の URL は url 列へ）。",
                    )
                elif normalized.lower() in seen_doi:
                    self.add(
                        "doi-duplicate",
                        "major",
                        "出典 {} の DOI が {} と重複している。".format(label, display_id(seen_doi[normalized.lower()])),
                        source_id=label,
                        repair="同じ文献なら1行に統合する。",
                    )
                else:
                    seen_doi[normalized.lower()] = key

            url = row.get("url", "").strip()
            if url:
                parsed = urllib.parse.urlparse(url)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    self.add(
                        "url-format",
                        "minor",
                        "出典 {} の URL '{}' が http(s) の絶対URLではない。".format(label, url),
                        source_id=label,
                    )
                else:
                    normalized_url = url.rstrip("/").lower()
                    if normalized_url in seen_url:
                        self.add(
                            "url-duplicate",
                            "major",
                            "出典 {} の URL が {} と重複している。".format(label, display_id(seen_url[normalized_url])),
                            source_id=label,
                        )
                    else:
                        seen_url[normalized_url] = key

                if "doi.org/" in url.lower() and doi:
                    embedded = url.split("doi.org/", 1)[1].strip().lower()
                    if embedded != doi.lower():
                        self.add(
                            "doi-url-mismatch",
                            "minor",
                            "出典 {} の DOI と doi.org URL が一致しない。".format(label),
                            source_id=label,
                        )

            accessed = row.get("accessed", "")
            if accessed and not DATE_RE.match(accessed):
                self.add(
                    "accessed-format",
                    "minor",
                    "出典 {} の accessed '{}' は YYYY-MM-DD 形式ではない。".format(label, accessed),
                    source_id=label,
                )
            elif not accessed and (url or source_type in {"web", "news"}):
                self.add(
                    "accessed-missing",
                    "minor",
                    "出典 {} に accessed 日がない。".format(label),
                    source_id=label,
                )

            normalized_title = re.sub(r"\s+", " ", title.strip().lower())
            if normalized_title:
                if normalized_title in seen_title:
                    self.add(
                        "title-duplicate",
                        "major",
                        "出典 {} の title が {} と重複している。".format(label, display_id(seen_title[normalized_title])),
                        source_id=label,
                    )
                else:
                    seen_title[normalized_title] = key

            # arXiv ID の形式（url または venue に含まれる場合）
            haystack = " ".join([url, row.get("venue", ""), doi])
            arxiv_match = ARXIV_RE.search(haystack)
            if "arxiv" in haystack.lower() and not arxiv_match:
                self.add(
                    "arxiv-id-format",
                    "minor",
                    "出典 {} は arXiv を名乗るが、arXiv ID を確認できない。".format(label),
                    source_id=label,
                )

            # ISBN（notes / doi / url に含まれる場合のみ）
            if source_type in {"book", "chapter"}:
                for candidate in [doi, url, row.get("notes", "")]:
                    for isbn in ISBN10_RE.findall(candidate) + ISBN13_RE.findall(candidate):
                        if len(re.sub(r"\D", "", isbn)) == 10 and not isbn10_valid(isbn):
                            self.add(
                                "isbn-checksum",
                                "minor",
                                "出典 {} の ISBN-10 '{}' がチェックディジット不一致。".format(label, isbn),
                                source_id=label,
                            )
                        if len(re.sub(r"\D", "", isbn)) == 13 and not isbn13_valid(isbn):
                            self.add(
                                "isbn-checksum",
                                "minor",
                                "出典 {} の ISBN-13 '{}' がチェックディジット不一致。".format(label, isbn),
                                source_id=label,
                            )

    def check_article_usage(self) -> None:
        if not self.article_path:
            return
        self.checks_run.append("article-usage")
        article = read_text(self.article_path)
        cited = {canonical_id(m.group(1)) for m in re.finditer(r"\[S(\d+)", article, flags=re.IGNORECASE)}
        cited.discard(None)
        for key in sorted(cited, key=lambda value: int(value[1:])):
            if key not in self.sources:
                self.add(
                    "cited-source-missing",
                    "critical",
                    "本文が参照する出典 {} が sources.csv にない。".format(display_id(key)),
                    source_id=display_id(key),
                )
                continue
            verification = self.sources[key].get("verification", "").lower()
            if verification == "retracted":
                self.add(
                    "retracted-source-cited",
                    "critical",
                    "撤回済みの出典 {} を本文が引用している。".format(display_id(key)),
                    source_id=display_id(key),
                    repair="撤回・訂正を確認し、引用を外すか、撤回を明記して議論する。",
                )
            elif verification in WEAK_VERIFICATION:
                self.add(
                    "weak-source-cited",
                    "major",
                    "出典 {} は verification='{}' のまま本文で引用されている。".format(
                        display_id(key), verification
                    ),
                    source_id=display_id(key),
                    repair="一次資料を確認して verified にするか、主張を弱める。",
                )

        uncited = [key for key in self.sources if key not in cited]
        if uncited:
            self.add(
                "sources-not-cited",
                "info",
                "{} 件の出典が本文で引用されていない。".format(len(uncited)),
                detail=", ".join(display_id(key) for key in uncited[:20]),
            )

    # -- online ----------------------------------------------------------

    def check_online(self) -> None:
        if not self.online:
            return
        self.checks_run.append("online")
        for key in self.sources:
            row = self.sources[key]
            doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", row.get("doi", "").strip(), flags=re.IGNORECASE)
            url = row.get("url", "").strip()
            target = "https://doi.org/{}".format(doi) if doi else url
            if not target:
                continue
            result: Dict[str, Any] = {"id": display_id(key), "target": target}
            try:
                request = urllib.request.Request(
                    target,
                    method="HEAD",
                    headers={"User-Agent": "universal-article-writer/3.0 (bibliographic verification)"},
                )
                with urllib.request.urlopen(request, timeout=8) as response:
                    result["status"] = response.status
                    result["ok"] = 200 <= response.status < 400
            except urllib.error.HTTPError as exc:
                result["status"] = exc.code
                result["ok"] = False
            except Exception as exc:  # noqa: BLE001 - ネットワーク失敗は監査を止めない
                result["status"] = None
                result["ok"] = None
                result["error"] = str(exc)[:160]
            self.online_results.append(result)
            if result.get("ok") is False:
                self.add(
                    "online-not-found",
                    "major",
                    "出典 {} のオンライン確認が失敗した（HTTP {}）。".format(
                        display_id(key), result.get("status")
                    ),
                    source_id=display_id(key),
                    detail=target,
                    repair="URL/DOI を確認する。一時的な失敗の可能性もあるため、再試行する。",
                )
            elif result.get("ok") is None:
                self.add(
                    "online-unchecked",
                    "info",
                    "出典 {} のオンライン確認ができなかった（ネットワーク）。".format(display_id(key)),
                    source_id=display_id(key),
                    detail=str(result.get("error", ""))[:160],
                )

    # -- summary ---------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        counts = Counter(f["severity"] for f in self.findings)
        if counts.get("critical", 0):
            verdict = "FAIL"
        elif counts.get("major", 0):
            verdict = "REVIEW"
        elif counts.get("minor", 0):
            verdict = "PASS_WITH_NOTES"
        else:
            verdict = "PASS"

        return {
            "verdict": verdict,
            "sources": len(self.sources),
            "critical": counts.get("critical", 0),
            "major": counts.get("major", 0),
            "minor": counts.get("minor", 0),
            "info": counts.get("info", 0),
            "online_checked": len(self.online_results),
            "checks_run": self.checks_run,
            "limitations": [
                "書誌の実在・内容の正しさを保証しない。",
                "オンライン確認は到達性のみで、版・撤回・訂正の最終確認ではない。",
                "DOI の解決先が正しい文献かを判定しない。",
                "CSV の意味的な正しさ（主張との対応）は判定しない。",
            ],
        }

    def run(self) -> Dict[str, Any]:
        self.load()
        self.check_rows()
        self.check_article_usage()
        self.check_online()

        for index, finding in enumerate(
            sorted(self.findings, key=lambda f: SEVERITY_ORDER.get(f["severity"], 9)),
            start=1,
        ):
            finding["id"] = "V{:03d}".format(index)

        return {
            "tool": "verify_sources.py",
            "version": VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "inputs": {
                "sources": self.sources_path.as_posix(),
                "article": self.article_path.as_posix() if self.article_path else None,
                "online": self.online,
            },
            "summary": self.summary(),
            "online_results": self.online_results,
            "findings": self.findings,
        }


def render_text(report: Dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "=== Universal Article Writer — Source Verification v{} ===".format(report["version"]),
        "Sources : {}".format(report["inputs"]["sources"]),
        "Article : {}".format(report["inputs"]["article"] or "(not provided)"),
        "Online  : {}".format("yes" if report["inputs"]["online"] else "no"),
        "",
        "--- Summary ---",
        "Verdict  : {}".format(summary["verdict"]),
        "Sources  : {}".format(summary["sources"]),
        "Findings : Critical {} / Major {} / Minor {} / Info {}".format(
            summary["critical"], summary["major"], summary["minor"], summary["info"]
        ),
        "",
    ]
    if report["findings"]:
        lines.append("--- Findings ---")
        for finding in report["findings"]:
            source = " [{}]".format(finding["source_id"]) if finding.get("source_id") else ""
            lines.append(
                "[{:<8}] {:<28}{}".format(finding["severity"].upper(), finding["check"], source)
            )
            lines.append("  {}".format(finding["message"]))
            if finding.get("detail"):
                lines.append("  detail: {}".format(finding["detail"]))
            if finding.get("repair"):
                lines.append("  repair: {}".format(finding["repair"]))
        lines.append("")
    else:
        lines.extend(["--- Findings ---", "No findings.", ""])

    lines.append("--- Limitations ---")
    for limitation in summary["limitations"]:
        lines.append("- {}".format(limitation))
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="論理記事工房の書誌・出典台帳監査。DOI/URL/重複/撤回/本文引用を点検する。",
    )
    parser.add_argument("--sources", required=True, help="出典台帳の CSV")
    parser.add_argument("--article", help="本文の Markdown（引用IDの照合に使う）")
    parser.add_argument("--out", help="JSON レポートの出力先")
    parser.add_argument("--format", choices=["text", "json", "both"], default="text")
    parser.add_argument("--online", action="store_true", help="DOI/URL の到達性を確認する（任意）")
    parser.add_argument(
        "--fail-on",
        choices=["none", "critical", "major", "minor"],
        default="none",
        help="この重大度以上があれば終了コード 2（既定: none）",
    )
    parser.add_argument("--version", action="version", version="verify_sources.py {}".format(VERSION))
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    configure_stdout()
    args = build_parser().parse_args(argv)

    sources_path = Path(args.sources)
    article_path = Path(args.article) if args.article else None
    if not sources_path.exists():
        print("ERROR: sources file not found: {}".format(sources_path), file=sys.stderr)
        return 3
    if article_path is not None and not article_path.exists():
        print("ERROR: article file not found: {}".format(article_path), file=sys.stderr)
        return 3

    try:
        verifier = Verifier(sources_path, article_path, args.online)
        report = verifier.run()
    except Exception as exc:  # noqa: BLE001
        print("ERROR: source verification failed: {}".format(exc), file=sys.stderr)
        return 3

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.format in {"text", "both"}:
        print(render_text(report))
    if args.format in {"json", "both"}:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    summary = report["summary"]
    threshold = {"none": 99, "critical": 0, "major": 1, "minor": 2}[args.fail_on]
    if args.fail_on != "none":
        worst = min(
            [SEVERITY_ORDER[s] for s, count in [
                ("critical", summary["critical"]),
                ("major", summary["major"]),
                ("minor", summary["minor"]),
            ] if count]
            or [99]
        )
        if worst <= threshold:
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
