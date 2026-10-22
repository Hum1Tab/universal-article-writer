#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_article.py — 論理記事工房の機械監査スクリプト

依存ライブラリなし。Python 3.9+ で動作する。

主な検査:
  - 引用マーカー [S01] / [S01: p.12] / [S01; S04] の抽出
  - 出典台帳 (sources.csv) との照合
  - 撤回・未確認・抄録のみの出典の使用
  - 主張台帳 (claims.csv) の証拠ID・確信度・反証条件
  - 直接引用の位置情報 (頁・節) の欠落
  - 出典のない数値のヒューリスティック検出
  - 未確認マーカー、過剰表現、AI slop、長い段落・文

このスクリプトは「意味内容の正しさ」を保証しない。
書誌の実在、主張との対応、論証の妥当性は、人間が確認すること。

使い方:
  python scripts/audit_article.py --article article.md --sources sources.csv --claims claims.csv
  python scripts/audit_article.py --article article.md --sources sources.csv --out audit-report.json
  python scripts/audit_article.py --article article.md --strict

終了コード:
  0  READY または CONDITIONAL
  2  NOT READY（Critical あり、または --strict で Major あり）
  3  入力エラー
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

VERSION = "3.0.1"

ALLOWED_VERIFICATION = {
    "verified",
    "partial",
    "abstract-only",
    "unverified",
    "retracted",
    "secondary-only",
}
WEAK_VERIFICATION = {"abstract-only", "unverified", "secondary-only"}

ALLOWED_CLAIM_TYPES = {
    "descriptive",
    "causal",
    "predictive",
    "mechanistic",
    "evaluative",
    "interpretive",
    "conceptual",
    "policy",
}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}
ALLOWED_CLAIM_STATUS = {"supported", "partially-supported", "contested", "unverified"}

SEVERITY_ORDER = {"critical": 0, "major": 1, "minor": 2, "info": 3}

OVERCLAIM_PHRASES = [
    "明らかだ",
    "明らかに",
    "証明された",
    "証明する",
    "実証された",
    "絶対に",
    "必ず",
    "完全に",
    "誰もが",
    "万人が",
    "間違いなく",
    "確実に",
    "100%",
    "ありえない",
    "決定的に",
    "論争の余地はない",
    "疑いようがない",
]

SLOP_PHRASES = [
    "現代社会において",
    "多岐にわたる",
    "重要な示唆",
    "今後が期待される",
    "本質は",
    "より深く見ると",
    "驚くべきことに",
    "まとめると",
    "注目に値する",
    "非常に重要",
    "多くの専門家",
    "時代の変化",
    "グローバル化が進む",
    "デジタル化が進む",
    "さまざまな視点",
    "様々な視点",
]

HEADING_LABELS = {"背景", "考察", "まとめ", "はじめに", "序論", "本論", "先行研究"}

LOCATOR_PATTERN = re.compile(
    r"(p\.|pp\.|page|pages|§|para|paragraph|table|fig\.|figure|頁|ページ|節|段落|表|図)",
    re.IGNORECASE,
)

NUMERIC_PATTERN = re.compile(
    r"\d[\d,\.]*\s*(%|％|percent|パーセント|倍|ポイント|pp|円|ドル|ドル相当|人|件|万人|億人|万件|億件)"
)

COUNTERARGUMENT_PATTERN = re.compile(
    r"(反論|反対|批判|異論|objection|counterargument|critics?|ただし|とはいえ|もっとも|"
    r"一方で|It is tempting|does not prove|do not prove|however)",
    re.IGNORECASE,
)

LIMITS_PATTERN = re.compile(
    r"(限界|limitation|scope|適用範囲|一般化できない|generaliz|not prove|does not prove)",
    re.IGNORECASE,
)

CAUSAL_LANGUAGE_PATTERN = re.compile(
    r"(が原因|を引き起こ|をもたら|に起因|につながる|\bcaus(?:e|es|ed|ing|al)\b|"
    r"\bleads? to\b|\bresults? in\b|\bdrives?\b)",
    re.IGNORECASE,
)

CROSS_SECTIONAL_PATTERN = re.compile(
    r"(横断|cross[- ]sectional|correlational|相関研究|観察研究の相関)",
    re.IGNORECASE,
)

DESIGN_PATTERN = re.compile(
    r"(無作為|ランダム化|RCT|実験|介入|自然実験|差分の差分|回帰不連続|操作変数|"
    r"randomi[sz]ed|\btrial\b|\bexperiment\b|difference[- ]in[- ]differences|"
    r"regression discontinuity|instrumental variable|natural experiment|\bintervention\b)",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# ユーティリティ
# ---------------------------------------------------------------------------


def configure_stdout() -> None:
    """Windows の cp932 コンソールでも日本語を出せるようにする。"""
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


def canonical_id(kind: str, digits: str) -> str:
    """S01 / S1 / S001 を S1 に正規化する。"""
    return "{}{}".format(kind.upper(), int(digits))


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, max(0, index)) + 1


def strip_code_and_urls(text: str) -> str:
    """コードブロック・インラインコード・URL を空白に置換する（行番号は保持）。"""
    text = text.replace("［", "[").replace("］", "]")
    text = re.sub(
        r"```.*?```",
        lambda m: "\n" * m.group(0).count("\n"),
        text,
        flags=re.DOTALL,
    )
    text = re.sub(r"`[^`\n]*`", "", text)
    text = re.sub(r"https?://[^\s)>\]]+", "", text)
    return text


def truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "○", "〇", "load-bearing", "load_bearing"}


def split_ids(value: str, kind: str = "S") -> List[str]:
    digits = re.findall(r"\b{}(\d+)\b".format(kind), value or "", flags=re.IGNORECASE)
    return [canonical_id(kind, d) for d in digits]


def display_id(key: str) -> str:
    """S1 -> S01。2桁以上はそのまま。"""
    kind = key[0]
    num = key[1:]
    if len(num) < 2:
        return "{}{:02d}".format(kind, int(num))
    return key


# ---------------------------------------------------------------------------
# 監査
# ---------------------------------------------------------------------------


class Auditor:
    def __init__(
        self,
        article_path: Path,
        sources_path: Optional[Path],
        claims_path: Optional[Path],
    ) -> None:
        self.article_path = article_path
        self.sources_path = sources_path
        self.claims_path = claims_path

        self.raw_text = read_text(article_path)
        self.text = strip_code_and_urls(self.raw_text)
        self.findings: List[Dict[str, Any]] = []
        self.checks_run: List[str] = []
        self.sources: Dict[str, Dict[str, str]] = {}
        self.source_order: List[str] = []
        self.source_dois: Dict[str, str] = {}
        self.claims: Dict[str, Dict[str, str]] = {}
        self.claim_order: List[str] = []
        self.citations: List[Dict[str, Any]] = []
        self.claim_markers: List[Dict[str, Any]] = []

    # -- finding ---------------------------------------------------------

    def add(
        self,
        check: str,
        severity: str,
        gate: str,
        message: str,
        line: Optional[int] = None,
        detail: Optional[str] = None,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.findings.append(
            {
                "check": check,
                "severity": severity,
                "gate": gate,
                "line": line,
                "message": message,
                "detail": detail or "",
                "evidence": evidence or {},
            }
        )

    # -- load ------------------------------------------------------------

    def load_sources(self) -> None:
        self.checks_run.append("sources")
        if not self.sources_path:
            self.add(
                "sources-not-provided",
                "info",
                "G2",
                "sources.csv が指定されていないため、出典の照合をスキップした。",
                detail="出典の実在・検証状態・撤回は、この監査では確認されていない。",
            )
            return

        rows, _ = read_csv_rows(self.sources_path)
        if not rows:
            self.add("sources-empty", "critical", "G2", "sources.csv にデータ行がない。")
            return

        for row in rows:
            raw_id = row.get("id", "")
            digits = re.sub(r"\D", "", raw_id)
            if not digits:
                self.add(
                    "source-id-missing",
                    "critical",
                    "G2",
                    "sources.csv に id のない行がある。",
                    evidence={"row": row},
                )
                continue
            key = canonical_id("S", digits)
            if key in self.sources:
                self.add(
                    "source-duplicate-id",
                    "critical",
                    "G2",
                    "出典ID {} が重複している。".format(display_id(key)),
                    evidence={"id": display_id(key)},
                )
                continue
            self.sources[key] = row
            self.source_order.append(key)

            verification = row.get("verification", "").lower()
            if not verification:
                self.add(
                    "source-verification-missing",
                    "major",
                    "G2",
                    "出典 {} の verification が空である。".format(display_id(key)),
                    evidence={"id": display_id(key)},
                )
            elif verification not in ALLOWED_VERIFICATION:
                self.add(
                    "source-verification-invalid",
                    "minor",
                    "G2",
                    "出典 {} の verification '{}' は許容値ではない。".format(
                        display_id(key), verification
                    ),
                    evidence={"id": display_id(key), "value": verification},
                )

            if not row.get("title", ""):
                self.add(
                    "source-title-missing",
                    "minor",
                    "G2",
                    "出典 {} の title が空である。".format(display_id(key)),
                    evidence={"id": display_id(key)},
                )

            doi = re.sub(
                r"^https?://(?:dx\.)?doi\.org/",
                "",
                row.get("doi", "").strip(),
                flags=re.IGNORECASE,
            ).lower()
            if doi:
                if doi in self.source_dois:
                    self.add(
                        "source-duplicate-doi",
                        "major",
                        "G2",
                        "出典 {} の DOI が {} と重複している。同じ文献を二重に数えていないか確認する。".format(
                            display_id(key), display_id(self.source_dois[doi])
                        ),
                        evidence={"id": display_id(key), "doi": doi},
                    )
                else:
                    self.source_dois[doi] = key

    def load_claims(self) -> None:
        self.checks_run.append("claims")
        if not self.claims_path:
            self.add(
                "claims-not-provided",
                "info",
                "G3",
                "claims.csv が指定されていないため、主張と証拠の対応監査をスキップした。",
            )
            return

        rows, _ = read_csv_rows(self.claims_path)
        if not rows:
            self.add("claims-empty", "major", "G3", "claims.csv にデータ行がない。")
            return

        for row in rows:
            raw_id = row.get("claim_id", "") or row.get("id", "")
            digits = re.sub(r"\D", "", raw_id)
            if not digits:
                self.add(
                    "claim-id-missing",
                    "major",
                    "G3",
                    "claims.csv に claim_id のない行がある。",
                    evidence={"row": row},
                )
                continue
            key = canonical_id("C", digits)
            if key in self.claims:
                self.add(
                    "claim-duplicate-id",
                    "major",
                    "G3",
                    "主張ID {} が重複している。".format(display_id(key)),
                    evidence={"id": display_id(key)},
                )
                continue
            self.claims[key] = row
            self.claim_order.append(key)

            claim_text = row.get("claim", "")
            if not claim_text:
                self.add(
                    "claim-text-missing",
                    "major",
                    "G3",
                    "主張 {} の claim が空である。".format(display_id(key)),
                    evidence={"id": display_id(key)},
                )

            claim_type = row.get("claim_type", "").strip().lower()
            if not claim_type:
                self.add(
                    "claim-type-missing",
                    "minor",
                    "G3",
                    "主張 {} の claim_type が空である。".format(display_id(key)),
                    evidence={"id": display_id(key)},
                )
            elif claim_type not in ALLOWED_CLAIM_TYPES:
                self.add(
                    "claim-type-invalid",
                    "minor",
                    "G3",
                    "主張 {} の claim_type '{}' は許容値ではない。".format(
                        display_id(key), claim_type
                    ),
                    evidence={"id": display_id(key), "value": claim_type},
                )

            evidence_ids = split_ids(row.get("evidence_ids", ""), "S")
            load_bearing = truthy(row.get("load_bearing", ""))
            confidence = row.get("confidence", "").lower()
            status = row.get("status", "").lower()

            if confidence and confidence not in ALLOWED_CONFIDENCE:
                self.add(
                    "claim-confidence-invalid",
                    "minor",
                    "G2",
                    "主張 {} の confidence '{}' は high / medium / low ではない。".format(
                        display_id(key), confidence
                    ),
                    evidence={"id": display_id(key), "value": confidence},
                )
            if status and status not in ALLOWED_CLAIM_STATUS:
                self.add(
                    "claim-status-invalid",
                    "minor",
                    "G3",
                    "主張 {} の status '{}' は許容値ではない。".format(
                        display_id(key), status
                    ),
                    evidence={"id": display_id(key), "value": status},
                )
            if load_bearing and status == "contested":
                self.add(
                    "claim-load-bearing-contested",
                    "info",
                    "G4",
                    "荷重主張 {} は contested。本文で反論と限定条件を扱っているか確認する。".format(
                        display_id(key)
                    ),
                    evidence={"claim_id": display_id(key)},
                )

            if load_bearing and not evidence_ids:
                self.add(
                    "claim-load-bearing-without-evidence",
                    "major",
                    "G2",
                    "荷重主張 {} に証拠IDがない。".format(display_id(key)),
                    detail=claim_text,
                    evidence={"id": display_id(key)},
                )

            for sid in evidence_ids:
                if self.sources and sid not in self.sources:
                    self.add(
                        "claim-evidence-missing-source",
                        "critical",
                        "G2",
                        "主張 {} が参照する証拠 {} が sources.csv に存在しない。".format(
                            display_id(key), display_id(sid)
                        ),
                        evidence={"claim_id": display_id(key), "source_id": display_id(sid)},
                    )
                elif sid in self.sources:
                    verification = self.sources[sid].get("verification", "").lower()
                    if verification == "retracted":
                        self.add(
                            "claim-evidence-retracted",
                            "critical",
                            "G2",
                            "主張 {} が撤回済みの出典 {} を証拠にしている。".format(
                                display_id(key), display_id(sid)
                            ),
                            evidence={"claim_id": display_id(key), "source_id": display_id(sid)},
                        )

            if confidence == "high" and evidence_ids and self.sources:
                verifications = [
                    self.sources[sid].get("verification", "").lower()
                    for sid in evidence_ids
                    if sid in self.sources
                ]
                if verifications and all(v in WEAK_VERIFICATION for v in verifications):
                    self.add(
                        "claim-high-confidence-weak-evidence",
                        "major",
                        "G2",
                        "主張 {} は confidence=high だが、証拠がすべて未検証・抄録のみ・二次のみである。".format(
                            display_id(key)
                        ),
                        evidence={
                            "claim_id": display_id(key),
                            "verifications": verifications,
                        },
                    )

            if load_bearing and status == "unverified":
                self.add(
                    "claim-load-bearing-unverified",
                    "major",
                    "G2",
                    "荷重主張 {} の status が unverified である。".format(display_id(key)),
                    evidence={"claim_id": display_id(key)},
                )

            if load_bearing and not row.get("falsifier", ""):
                self.add(
                    "claim-falsifier-missing",
                    "major",
                    "G3",
                    "荷重主張 {} に falsifier（撤回条件）がない。".format(display_id(key)),
                    evidence={"claim_id": display_id(key)},
                )

            if claim_type in {"evaluative", "policy"} and not row.get("warrant", "").strip():
                self.add(
                    "claim-normative-without-warrant",
                    "major",
                    "G7",
                    "規範的主張 {} に warrant（価値前提・原則）がない。".format(display_id(key)),
                    detail=claim_text,
                    evidence={"claim_id": display_id(key)},
                )

            if confidence == "high" and status in {"contested", "unverified"}:
                self.add(
                    "claim-high-confidence-contested",
                    "major",
                    "G3",
                    "主張 {} は confidence=high だが status={} である。".format(
                        display_id(key), status
                    ),
                    evidence={"claim_id": display_id(key)},
                )

            if claim_type == "causal" and evidence_ids and self.sources:
                source_text = " ".join(
                    " ".join(
                        [
                            self.sources[sid].get("title", ""),
                            self.sources[sid].get("notes", ""),
                            self.sources[sid].get("type", ""),
                        ]
                    )
                    for sid in evidence_ids
                    if sid in self.sources
                )
                if CROSS_SECTIONAL_PATTERN.search(source_text) and not DESIGN_PATTERN.search(source_text):
                    self.add(
                        "claim-causal-cross-sectional-evidence",
                        "major",
                        "G3",
                        "因果主張 {} の証拠が横断・相関研究のみの可能性がある。".format(
                            display_id(key)
                        ),
                        detail=claim_text,
                        evidence={"claim_id": display_id(key)},
                    )

        load_bearing_count = sum(
            1 for row in self.claims.values() if truthy(row.get("load_bearing", ""))
        )
        if self.claims and load_bearing_count == 0:
            self.add(
                "claim-no-load-bearing",
                "major",
                "G3",
                "荷重主張（load_bearing）が1つもない。結論を支える主張を特定する。",
            )
        elif load_bearing_count > 5:
            self.add(
                "claim-too-many-load-bearing",
                "minor",
                "G3",
                "荷重主張が{}個ある。3〜5個に絞る。".format(load_bearing_count),
            )

    # -- citations -------------------------------------------------------

    def parse_markers(self) -> None:
        self.checks_run.append("citation-markers")
        for match in re.finditer(r"\[([^\[\]\n]{1,240})\]", self.text):
            group = match.group(1)
            if not re.search(r"\b[SC]\d", group, flags=re.IGNORECASE):
                continue
            found = False
            for marker in re.finditer(
                r"\b([SC])(\d+)\b(?:\s*:\s*([^;\]]+))?",
                group,
                flags=re.IGNORECASE,
            ):
                kind = marker.group(1).upper()
                key = canonical_id(kind, marker.group(2))
                locator = (marker.group(3) or "").strip().rstrip(",")
                item = {
                    "key": key,
                    "raw": match.group(0),
                    "locator": locator,
                    "line": line_of(self.text, match.start()),
                }
                if kind == "S":
                    self.citations.append(item)
                else:
                    self.claim_markers.append(item)
                found = True
            if not found:
                self.add(
                    "citation-malformed",
                    "minor",
                    "G2",
                    "引用マーカー '{}' を解析できなかった。".format(match.group(0)),
                    line=line_of(self.text, match.start()),
                )

        if not self.citations:
            self.add(
                "article-no-citations",
                "major",
                "G2",
                "本文に引用マーカーが1つもない。事実主張の根拠を確認できない。",
            )

    def audit_citations(self) -> None:
        self.checks_run.append("citation-sources")
        if not self.sources:
            return

        counts = Counter(c["key"] for c in self.citations)
        first_line: Dict[str, int] = {}
        for citation in self.citations:
            first_line.setdefault(citation["key"], citation["line"])

        for key, count in sorted(counts.items(), key=lambda item: (item[0])):
            line = first_line.get(key)
            if key not in self.sources:
                self.add(
                    "citation-source-missing",
                    "critical",
                    "G2",
                    "本文が参照する出典 {} が sources.csv に存在しない（{}回）。".format(
                        display_id(key), count
                    ),
                    line=line,
                    evidence={"source_id": display_id(key), "count": count},
                )
                continue

            verification = self.sources[key].get("verification", "").lower()
            title = self.sources[key].get("title", "")
            if verification == "retracted":
                self.add(
                    "citation-retracted-source",
                    "critical",
                    "G2",
                    "撤回済みの出典 {} を引用している（{}回）。".format(
                        display_id(key), count
                    ),
                    line=line,
                    detail=title,
                    evidence={"source_id": display_id(key), "count": count},
                )
            elif verification in WEAK_VERIFICATION:
                self.add(
                    "citation-weak-source",
                    "major",
                    "G2",
                    "出典 {} の検証状態が '{}' のまま引用されている（{}回）。".format(
                        display_id(key), verification, count
                    ),
                    line=line,
                    detail="主張の強さを落とすか、一次資料を確認すること。",
                    evidence={"source_id": display_id(key), "count": count},
                )
            elif verification == "partial":
                self.add(
                    "citation-partial-source",
                    "minor",
                    "G2",
                    "出典 {} は partial（一部のみ確認）である（{}回）。".format(
                        display_id(key), count
                    ),
                    line=line,
                    evidence={"source_id": display_id(key), "count": count},
                )

        cited_keys = set(counts)
        for key in self.source_order:
            if key not in cited_keys:
                self.add(
                    "source-not-cited",
                    "info",
                    "G2",
                    "出典 {} は sources.csv にあるが、本文で引用されていない。".format(
                        display_id(key)
                    ),
                    detail=self.sources[key].get("title", ""),
                    evidence={"source_id": display_id(key)},
                )

    def audit_claim_markers(self) -> None:
        """sources.csv の有無にかかわらず、主張マーカーを照合する。"""
        self.checks_run.append("claim-markers")
        for marker in self.claim_markers:
            if self.claims and marker["key"] not in self.claims:
                self.add(
                    "claim-marker-missing",
                    "major",
                    "G3",
                    "本文の主張マーカー {} が claims.csv に存在しない。".format(
                        marker["raw"]
                    ),
                    line=marker["line"],
                    evidence={"claim_id": display_id(marker["key"])},
                )

        if self.claims:
            marker_keys = {m["key"] for m in self.claim_markers}
            for key in self.claim_order:
                if marker_keys and key not in marker_keys:
                    self.add(
                        "claim-not-in-article",
                        "info",
                        "G3",
                        "主張 {} は claims.csv にあるが、本文に主張マーカーがない。".format(
                            display_id(key)
                        ),
                        evidence={"claim_id": display_id(key)},
                    )

        if self.citations and not re.search(
            r"^#{1,4}\s*(参考文献|References|Works Cited|Bibliography|引用文献)",
            self.text,
            flags=re.IGNORECASE | re.MULTILINE,
        ):
            self.add(
                "reference-section-missing",
                "info",
                "G2",
                "引用マーカーがあるが、「参考文献」に相当する見出しが見つからない。",
            )

    # -- text checks -----------------------------------------------------

    def iter_sentences(self) -> Iterable[Tuple[int, str]]:
        pattern = re.compile(r"[^。！？!?\n]+[。！？!?]?")
        for match in pattern.finditer(self.text):
            sentence = match.group(0).strip()
            if sentence:
                yield match.start(), sentence

    def audit_text(self) -> None:
        self.checks_run.append("text")

        # 直接引用の位置情報
        for start, sentence in self.iter_sentences():
            has_quote = ("「" in sentence) or ("」" in sentence) or ('"' in sentence) or ("“" in sentence)
            if not has_quote:
                continue
            citations = [
                c
                for c in self.citations
                if start <= self.text.find(c["raw"], start) < start + len(sentence)
            ]
            if not citations:
                continue
            if not any(LOCATOR_PATTERN.search(c["locator"]) for c in citations):
                self.add(
                    "quote-without-locator",
                    "minor",
                    "G2",
                    "直接引用に頁・節・段落などの位置情報がない。",
                    line=line_of(self.text, start),
                    detail=sentence[:120],
                )

        # 出典のない数値（ヒューリスティック）
        numeric_count = 0
        for start, sentence in self.iter_sentences():
            if numeric_count >= 20:
                break
            if not NUMERIC_PATTERN.search(sentence):
                continue
            if any(
                start <= self.text.find(c["raw"], start) < start + len(sentence)
                for c in self.citations
            ):
                continue
            if sentence.startswith("#") or sentence.startswith("|"):
                continue
            self.add(
                "numeric-claim-without-citation",
                "info",
                "G2",
                "数値を含む文に出典マーカーがない（ヒューリスティック）。",
                line=line_of(self.text, start),
                detail=sentence[:160],
            )
            numeric_count += 1

        # 過剰表現
        for phrase in OVERCLAIM_PHRASES:
            occurrences = [m.start() for m in re.finditer(re.escape(phrase), self.text)]
            if occurrences:
                self.add(
                    "overclaim-language",
                    "minor",
                    "G3",
                    "過剰表現 '{}' が {} 回ある。文脈を確認し、証拠の強さに合わせる。".format(
                        phrase, len(occurrences)
                    ),
                    line=line_of(self.text, occurrences[0]),
                    evidence={"phrase": phrase, "count": len(occurrences)},
                )

        # AI slop
        for phrase in SLOP_PHRASES:
            occurrences = [m.start() for m in re.finditer(re.escape(phrase), self.text)]
            if occurrences:
                self.add(
                    "ai-slop-language",
                    "info",
                    "G5",
                    "定型表現 '{}' が {} 回ある。具体化するか削る。".format(
                        phrase, len(occurrences)
                    ),
                    line=line_of(self.text, occurrences[0]),
                    evidence={"phrase": phrase, "count": len(occurrences)},
                )

        # 見出しがラベルだけ
        for match in re.finditer(r"^(#{1,4})\s*(.+?)\s*$", self.text, flags=re.MULTILINE):
            heading = match.group(2).strip()
            if heading in HEADING_LABELS:
                self.add(
                    "label-heading",
                    "info",
                    "G5",
                    "見出し '{}' が内容を表していない。主張型の見出しにする。".format(heading),
                    line=line_of(self.text, match.start()),
                )

        # 長い段落
        offset = 0
        for block in re.split(r"(\n\s*\n)", self.text):
            block_start = offset
            offset += len(block)
            stripped = block.strip()
            if not stripped:
                continue
            if stripped.startswith(("#", "|", "-", "*", ">")) or re.match(r"^\d+\.", stripped):
                continue
            if len(stripped) > 700:
                self.add(
                    "long-paragraph",
                    "minor",
                    "G5",
                    "段落が長すぎる（{}文字）。分割を検討する。".format(len(stripped)),
                    line=line_of(self.text, block_start),
                    detail=stripped[:100],
                )

        # 長い文
        long_sentences = 0
        for start, sentence in self.iter_sentences():
            if long_sentences >= 10:
                break
            if len(sentence) > 160:
                self.add(
                    "long-sentence",
                    "info",
                    "G5",
                    "文が長い（{}文字）。分割を検討する。".format(len(sentence)),
                    line=line_of(self.text, start),
                    detail=sentence[:100],
                )
                long_sentences += 1

        # 反論・限界の構造
        if not COUNTERARGUMENT_PATTERN.search(self.text):
            self.add(
                "counterargument-missing",
                "minor",
                "G4",
                "反論・反対意見への言及が見つからない。最強の反論を1節設ける。",
            )
        if not LIMITS_PATTERN.search(self.text):
            self.add(
                "limits-missing",
                "minor",
                "G6",
                "限界・適用範囲への言及が見つからない。確認していないことを書く。",
            )

        # 未確認・TODO
        for match in re.finditer(r"【未確認[^】]*】", self.text):
            self.add(
                "unresolved-unverified",
                "major",
                "G5",
                "未確認マーカーが残っている: {}".format(match.group(0)),
                line=line_of(self.text, match.start()),
            )
        for pattern, label in [
            (r"\bTODO\b", "TODO"),
            (r"\bTBD\b", "TBD"),
            (r"\[要出典\]", "[要出典]"),
            (r"\?\?", "??"),
        ]:
            matches = list(re.finditer(pattern, self.text))
            if matches:
                self.add(
                    "unresolved-placeholder",
                    "minor",
                    "G5",
                    "未解決のプレースホルダ '{}' が {} 回ある。".format(label, len(matches)),
                    line=line_of(self.text, matches[0].start()),
                )

    # -- summary ---------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        severity_counts = Counter(f["severity"] for f in self.findings)
        gate_counts: Dict[str, Counter] = {}
        for finding in self.findings:
            gate_counts.setdefault(finding["gate"], Counter())[finding["severity"]] += 1

        if severity_counts.get("critical", 0) > 0:
            readiness = "NOT READY"
        elif severity_counts.get("major", 0) > 0:
            readiness = "CONDITIONAL"
        else:
            readiness = "READY"

        if not self.sources:
            # 出典照合なしでは READY と言い切れない
            if readiness == "READY":
                readiness = "CONDITIONAL"

        chars = len(re.sub(r"\s+", "", self.raw_text))
        paragraphs = len(
            [
                p
                for p in re.split(r"\n\s*\n", self.text)
                if p.strip() and not p.strip().startswith(("#", "|", "-", "*", ">"))
            ]
        )

        return {
            "readiness": readiness,
            "critical": severity_counts.get("critical", 0),
            "major": severity_counts.get("major", 0),
            "minor": severity_counts.get("minor", 0),
            "info": severity_counts.get("info", 0),
            "citations": len(self.citations),
            "unique_sources_cited": len({c["key"] for c in self.citations}),
            "sources_in_ledger": len(self.sources),
            "claims": len(self.claims),
            "load_bearing_claims": sum(
                1 for row in self.claims.values() if truthy(row.get("load_bearing", ""))
            ),
            "chars": chars,
            "paragraphs": paragraphs,
            "gate_counts": {
                gate: dict(sorted(counts.items(), key=lambda item: SEVERITY_ORDER.get(item[0], 9)))
                for gate, counts in sorted(gate_counts.items())
            },
            "checks_run": self.checks_run,
            "limitations": [
                "書誌情報・DOI・URL の実在は確認しない。Crossref / PubMed / 出版社で人間が確認すること。",
                "引用が主張を本当に支えているかは判定しない。文脈の読解が必要である。",
                "撤回・訂正の有無は sources.csv の verification に依存する。",
                "数値の分母・単位・期間・集団の正しさは判定しない。",
                "過剰表現・AI slop・長文の検出は語彙と長さのヒューリスティックであり、文脈を理解しない。",
                "日本語の文分割は近似であり、英語の文分割は不完全である。",
                "論証の妥当性、フレーム批判、反論の強さは判定しない。argument_lint.py と Phase 5 の人間監査が必要である。",
                "価値前提の妥当性は判定しない。規範的主張は人間が確認すること。",
            ],
        }

    def run(self) -> Dict[str, Any]:
        if not self.raw_text.strip():
            self.add("article-empty", "critical", "G1", "記事本文が空である。")
        self.load_sources()
        self.load_claims()
        self.parse_markers()
        self.audit_citations()
        self.audit_claim_markers()
        self.audit_text()

        for index, finding in enumerate(
            sorted(
                self.findings,
                key=lambda f: (SEVERITY_ORDER.get(f["severity"], 9), f.get("line") or 0),
            ),
            start=1,
        ):
            finding["id"] = "F{:03d}".format(index)

        return {
            "tool": "audit_article.py",
            "version": VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "inputs": {
                "article": self.article_path.as_posix(),
                "sources": self.sources_path.as_posix() if self.sources_path else None,
                "claims": self.claims_path.as_posix() if self.claims_path else None,
            },
            "summary": self.summary(),
            "findings": self.findings,
        }


# ---------------------------------------------------------------------------
# 出力
# ---------------------------------------------------------------------------


def render_text(report: Dict[str, Any]) -> str:
    summary = report["summary"]
    lines: List[str] = []
    lines.append("=== Universal Article Writer — Article Audit v{} ===".format(report["version"]))
    lines.append("Article : {}".format(report["inputs"]["article"]))
    lines.append("Sources : {}".format(report["inputs"]["sources"] or "(not provided)"))
    lines.append("Claims  : {}".format(report["inputs"]["claims"] or "(not provided)"))
    lines.append("")
    lines.append("--- Summary ---")
    lines.append("Readiness : {}".format(summary["readiness"]))
    lines.append(
        "Findings  : Critical {} / Major {} / Minor {} / Info {}".format(
            summary["critical"],
            summary["major"],
            summary["minor"],
            summary["info"],
        )
    )
    lines.append(
        "Citations : {} (unique sources: {})".format(
            summary["citations"], summary["unique_sources_cited"]
        )
    )
    lines.append(
        "Claims    : {} (load-bearing: {})".format(
            summary["claims"], summary["load_bearing_claims"]
        )
    )
    lines.append("Length    : {} chars / {} paragraphs".format(summary["chars"], summary["paragraphs"]))
    lines.append("")

    if report["findings"]:
        lines.append("--- Findings ---")
        for finding in report["findings"]:
            location = " line {}".format(finding["line"]) if finding.get("line") else ""
            lines.append(
                "[{:<8}] {:<28} {}{}".format(
                    finding["severity"].upper(),
                    finding["check"],
                    finding["gate"],
                    location,
                )
            )
            lines.append("  {}".format(finding["message"]))
            if finding.get("detail"):
                lines.append("  detail: {}".format(finding["detail"]))
        lines.append("")
    else:
        lines.append("--- Findings ---")
        lines.append("No findings.")
        lines.append("")

    lines.append("--- Limitations ---")
    for limitation in summary["limitations"]:
        lines.append("- {}".format(limitation))
    lines.append("")
    lines.append("Note: this audit does not prove that the article is true or well-argued.")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="論理記事工房の機械監査。引用ID・未確認マーカー・過剰表現・主張と証拠の対応を点検する。",
    )
    parser.add_argument("--article", required=True, help="監査する記事の Markdown ファイル")
    parser.add_argument("--sources", help="出典台帳の CSV")
    parser.add_argument("--claims", help="主張と証拠の対応 CSV")
    parser.add_argument("--out", help="JSON レポートの出力先")
    parser.add_argument(
        "--format",
        choices=["text", "json", "both"],
        default="text",
        help="標準出力の形式（既定: text）",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="CONDITIONAL（Major あり）でも終了コード 2 にする",
    )
    parser.add_argument("--version", action="version", version="audit_article.py {}".format(VERSION))
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    configure_stdout()
    parser = build_parser()
    args = parser.parse_args(argv)

    article_path = Path(args.article)
    sources_path = Path(args.sources) if args.sources else None
    claims_path = Path(args.claims) if args.claims else None

    for label, path in [("article", article_path), ("sources", sources_path), ("claims", claims_path)]:
        if path is not None and not path.exists():
            print("ERROR: {} file not found: {}".format(label, path), file=sys.stderr)
            return 3

    try:
        auditor = Auditor(article_path, sources_path, claims_path)
        report = auditor.run()
    except Exception as exc:  # noqa: BLE001 - CLI は失敗を明示して終了する
        print("ERROR: audit failed: {}".format(exc), file=sys.stderr)
        return 3

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    if args.format in {"text", "both"}:
        print(render_text(report))
    if args.format in {"json", "both"}:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    readiness = report["summary"]["readiness"]
    if readiness == "NOT READY":
        return 2
    if args.strict and readiness == "CONDITIONAL":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
