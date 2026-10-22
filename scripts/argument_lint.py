#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
argument_lint.py — 論理記事工房の推論監査スクリプト

依存ライブラリなし。Python 3.9+ で動作する。

主な検査:
  - 相関から因果への飛躍（デザイン言及がない場合）
  - 非有意を「効果なし」とする表現
  - 少数例からの一般化、偽のジレンマ、権威への訴え
  - 人身攻撃、滑坡、事実から価値、生存者バイアス、基礎率の無視
  - 反論・限界の欠落、単一 sourced への依存
  - claims.csv の荷重主張・反証条件・確信度・規範的主張
  - 横断研究を因果証拠として使っている主張

このスクリプトは「意味内容の正しさ」を保証しない。
文脈・皮肉・引用・反語を完全には理解しないため、検出結果は人間が確認すること。

使い方:
  python scripts/argument_lint.py --article article.md
  python scripts/argument_lint.py --article article.md --claims claims.csv --sources sources.csv
  python scripts/argument_lint.py --article article.md --out argument-lint.json --fail-on major

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
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

VERSION = "3.0.1"

SEVERITY_ORDER = {"critical": 0, "major": 1, "minor": 2, "info": 3}
SEVERITY_LABEL = {"critical": "Critical", "major": "Major", "minor": "Minor", "info": "Info"}

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

CAUSAL_RE = re.compile(
    r"(が原因|を引き起こ|をもたら|に起因|につながる|を増や|を減ら|を悪化|を改善|"
    r"を上げ|を下げ|を高め|を低め|を押し上げ|を押し下げ|"
    r"\bcaus(?:e|es|ed|ing|al)\b|\bleads? to\b|\bled to\b|\bresults? in\b|\bdrives?\b|"
    r"\bproduces?\b|\bincreases?\b|\bdecreases?\b|\bimproves?\b|\bworsens?\b)",
    re.IGNORECASE,
)
CORRELATION_RE = re.compile(
    r"(相関|関連|連動|比例|correlat|associat|linked to|related to)",
    re.IGNORECASE,
)
DESIGN_RE = re.compile(
    r"(無作為|ランダム化|RCT|実験|介入|自然実験|差分の差分|回帰不連続|操作変数|"
    r"傾向スコア|固定効果|パネルデータ|randomi[sz]ed|\btrial\b|\bexperiment\b|"
    r"difference[- ]in[- ]differences|regression discontinuity|instrumental variable|"
    r"natural experiment|\bintervention\b|fixed effects|panel data)",
    re.IGNORECASE,
)

NO_EFFECT_RE = re.compile(
    r"(効果(?:が|は)?(?:ない|無い|認められない)|効果なし|無効|"
    r"\bno effect\b|\bno impact\b|\bdoes not work\b|\bdid not work\b)",
    re.IGNORECASE,
)
NON_SIGNIFICANT_RE = re.compile(
    r"(非有意|有意差(?:が|は)?(?:ない|無い|認められない)|有意で(?:は)?ない|"
    r"\bnot significant\b|\bnon-significant\b|\bn\.s\.\b|p\s*[=≧>]\s*0?\.0[5-9])",
    re.IGNORECASE,
)
NO_EFFECT_GUARD_RE = re.compile(
    r"(効果がないわけではない|検出できなかった|とは限らない|not necessarily|could not detect|"
    r"undetected|不明である|判断できない)",
    re.IGNORECASE,
)

ANECDOTE_RE = re.compile(
    r"(一つの研究|1つの研究|ある研究|一事例|一例|一人の|事例では|"
    r"\bone study\b|\ba single study\b|\bsingle case\b|\banecdote\b|\bin one case\b)",
    re.IGNORECASE,
)
GENERALIZE_RE = re.compile(
    r"(すべて|全て|あらゆる|普遍|常に|必ず|誰でも|"
    r"\ball\b|\bevery\b|\balways\b|\buniversally\b|\banyone\b)",
    re.IGNORECASE,
)
GENERALIZE_GUARD_RE = re.compile(
    r"(限られ|範囲|条件|サンプル|とは限らない|not all|in this sample|under these conditions|"
    r"一般化できない|outside the scope)",
    re.IGNORECASE,
)

FALSE_DILEMMA_RE = re.compile(
    r"(二択|二者択一|しかない|以外に(?:方法|選択肢|道)はない|"
    r"\beither\b.+\bor\b|\bonly two (?:options|choices)\b|\bbinary choice\b)",
    re.IGNORECASE,
)
FALSE_DILEMMA_GUARD_RE = re.compile(
    r"(第三|別の選択肢|代替|折衷|両方|どちらも|"
    r"\bthird\b|\balternative\b|\bhybrid\b|\bboth\b|\bneither\b|\bspectrum\b)",
    re.IGNORECASE,
)

AUTHORITY_RE = re.compile(
    r"(専門家(?:は|が|の間では)|多くの専門家|科学者は|権威|ノーベル賞|著名な|"
    r"authorities agree|experts agree|scientists agree|everyone knows|誰もが知る)",
    re.IGNORECASE,
)
CITATION_RE = re.compile(r"\[[SC]\d", re.IGNORECASE)

AD_HOMINEM_RE = re.compile(
    r"(信者|トンデモ|バカ|馬鹿|素人|嘘つき|利権|御用学者|"
    r"\bidiot\b|\bshill\b|\bliar\b|\bcorrupt\b|\bmoron\b)",
    re.IGNORECASE,
)

SLIPPERY_RE = re.compile(
    r"(滑り坂|ドミノ|やがて|最終的には必ず|必ず.{0,20}(?:崩壊|破綻|終わる|独裁)|"
    r"\binevitably\b|\bslippery slope\b|\bnext thing\b)",
    re.IGNORECASE,
)
MECHANISM_RE = re.compile(
    r"(なぜなら|メカニズム|段階|各段階|仕組み|mechanism|because each step|step by step)",
    re.IGNORECASE,
)

IS_OUGHT_RE = re.compile(
    r"((?:自然|伝統|昔から|歴史|文化).{0,16}だから.{0,40}(?:べき|すべき|望ましい|正しい)|"
    r"自然に反するから|伝統に従うべき|"
    r"because it is natural.{0,40}should|it is natural therefore)",
    re.IGNORECASE,
)

SURVIVOR_RE = re.compile(
    r"(成功者(?:は|の).{0,30}(?:皆|すべて|必ず|共通)|生き残った.{0,30}(?:から|ので)|"
    r"\bsurvivors\b|\bsuccessful (?:people|companies|founders)\b.{0,40}\b(?:all|always)\b)",
    re.IGNORECASE,
)

BASE_RATE_RE = re.compile(
    r"((?:99|99\.9|95)\s*%|感度|特異度|\bsensitivity\b|\bspecificity\b)",
    re.IGNORECASE,
)
TEST_RE = re.compile(r"(検査|診断|陽性|\btest\b|\bpositive\b|\bscreening\b)", re.IGNORECASE)
BASE_RATE_GUARD_RE = re.compile(
    r"(有病率|基礎率|事前確率|\bprevalence\b|\bbase rate\b|\bprior\b)",
    re.IGNORECASE,
)

COUNTERARGUMENT_RE = re.compile(
    r"(反論|反対|批判|異論|objection|counterargument|critics?|ただし|とはいえ|もっとも|"
    r"一方で|It is tempting|A second|however)",
    re.IGNORECASE,
)
LIMITS_RE = re.compile(
    r"(限界|limitation|scope|適用範囲|一般化できない|generaliz|not prove|does not prove)",
    re.IGNORECASE,
)

CROSS_SECTIONAL_RE = re.compile(
    r"(横断|cross[- ]sectional|correlational|相関研究|観察研究の相関)",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# ユーティリティ
# ---------------------------------------------------------------------------


def configure_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        rows: List[Dict[str, str]] = []
        for raw in reader:
            row: Dict[str, str] = {}
            for key, value in raw.items():
                if key is None:
                    continue
                row[key.strip().lower()] = (value or "").strip()
            rows.append(row)
    return rows


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, max(0, index)) + 1


def truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "○", "〇", "load-bearing", "load_bearing"}


def split_ids(value: str) -> List[str]:
    return ["S{}".format(int(n)) for n in re.findall(r"\bS(\d+)\b", value or "", flags=re.IGNORECASE)]


def strip_code_and_urls(text: str) -> str:
    text = text.replace("［", "[").replace("］", "]")
    text = re.sub(r"```.*?```", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]*`", "", text)
    text = re.sub(r"https?://[^\s)>\]]+", "", text)
    return text


def paragraphs_with_offsets(text: str) -> List[Tuple[int, str]]:
    """段落と開始オフセットを返す。見出し・表・コードは除外しない（文脈判定に使う）。"""
    blocks: List[Tuple[int, str]] = []
    for match in re.finditer(r"(?:^|\n\s*\n)([^\n].*?)(?=\n\s*\n|\Z)", text, flags=re.DOTALL):
        block = match.group(1)
        start = match.start(1)
        if block.strip():
            blocks.append((start, block))
    if not blocks and text.strip():
        blocks.append((0, text))
    return blocks


def excerpt(text: str, limit: int = 160) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned[:limit] + ("…" if len(cleaned) > limit else "")


# ---------------------------------------------------------------------------
# 監査
# ---------------------------------------------------------------------------


class Linter:
    def __init__(
        self,
        article_path: Path,
        claims_path: Optional[Path],
        sources_path: Optional[Path],
    ) -> None:
        self.article_path = article_path
        self.claims_path = claims_path
        self.sources_path = sources_path

        self.raw_text = read_text(article_path)
        self.text = strip_code_and_urls(self.raw_text)
        self.paragraphs = paragraphs_with_offsets(self.text)
        self.findings: List[Dict[str, Any]] = []
        self.checks_run: List[str] = []
        self.claims: Dict[str, Dict[str, str]] = {}
        self.sources: Dict[str, Dict[str, str]] = {}
        self.citations: List[str] = [m.group(0) for m in re.finditer(r"\[([SC]\d+)", self.text, flags=re.IGNORECASE)]
        self.claim_order: List[str] = []

    # -- findings --------------------------------------------------------

    def add(
        self,
        check: str,
        severity: str,
        gate: str,
        message: str,
        line: Optional[int] = None,
        detail: str = "",
        repair: str = "",
    ) -> None:
        self.findings.append(
            {
                "check": check,
                "severity": severity,
                "gate": gate,
                "line": line,
                "message": message,
                "detail": detail,
                "repair": repair,
            }
        )

    def paragraph_at(self, index: int) -> str:
        return self.paragraphs[index][1]

    def nearby_has_design(self, index: int) -> bool:
        for offset in (-1, 0, 1):
            pos = index + offset
            if 0 <= pos < len(self.paragraphs):
                if DESIGN_RE.search(self.paragraph_at(pos)):
                    return True
        return False

    # -- rules -----------------------------------------------------------

    def scan_paragraphs(self) -> None:
        self.checks_run.append("reasoning-rules")
        for index, (start, paragraph) in enumerate(self.paragraphs):
            if paragraph.lstrip().startswith(("#", "|", ">")):
                continue
            line = line_of(self.text, start)

            # 1. 相関 → 因果
            if (
                CAUSAL_RE.search(paragraph)
                and CORRELATION_RE.search(paragraph)
                and not self.nearby_has_design(index)
            ):
                self.add(
                    "causal-leap",
                    "major",
                    "G3",
                    "相関・関連の記述から因果を主張しているように読める。デザインか反事実の説明がない。",
                    line=line,
                    detail=excerpt(paragraph),
                    repair="因果デザイン（RCT・自然実験・DiD・RD・IV など）と仮定を示すか、"
                    "「関連する」「予測する」に弱める。",
                )

            # 2. 非有意 → 効果なし
            if NO_EFFECT_RE.search(paragraph) and NON_SIGNIFICANT_RE.search(paragraph):
                if not NO_EFFECT_GUARD_RE.search(paragraph):
                    self.add(
                        "significance-as-no-effect",
                        "major",
                        "G3",
                        "非有意を「効果なし」と解釈している可能性がある。",
                        line=line,
                        detail=excerpt(paragraph),
                        repair="「統計的に有意な差は検出されなかった」と書き、信頼区間と検出力を示す。",
                    )

            # 3. 少数例からの一般化
            if ANECDOTE_RE.search(paragraph) and GENERALIZE_RE.search(paragraph):
                if not GENERALIZE_GUARD_RE.search(paragraph):
                    self.add(
                        "hasty-generalization",
                        "major",
                        "G3",
                        "少数の事例・単一研究から普遍的な結論を出している可能性がある。",
                        line=line,
                        detail=excerpt(paragraph),
                        repair="結論の範囲を限定するか、代表性のある証拠を追加する。",
                    )

            # 4. 偽のジレンマ
            if FALSE_DILEMMA_RE.search(paragraph) and not FALSE_DILEMMA_GUARD_RE.search(paragraph):
                self.add(
                    "false-dilemma",
                    "minor",
                    "G3",
                    "選択肢を二つに絞っている可能性がある。第三の選択肢を検討したか。",
                    line=line,
                    detail=excerpt(paragraph),
                    repair="現状維持・折衷・別制度などの代替案を列挙する。",
                )

            # 5. 権威への訴え
            if AUTHORITY_RE.search(paragraph) and not CITATION_RE.search(paragraph):
                self.add(
                    "appeal-to-authority",
                    "minor",
                    "G3",
                    "権威・専門家への言及に出典がない。",
                    line=line,
                    detail=excerpt(paragraph),
                    repair="具体的な出典・合意の範囲・根拠を示す。",
                )

            # 6. 人身攻撃
            if AD_HOMINEM_RE.search(paragraph) and "「" not in paragraph and '"' not in paragraph:
                self.add(
                    "ad-hominem",
                    "minor",
                    "G3",
                    "相手の属性・人格を攻撃する表現がある。主張の評価と分ける。",
                    line=line,
                    detail=excerpt(paragraph),
                    repair="相手の主張を最強版で再構成し、証拠と論理で評価する。",
                )

            # 7. 滑坡
            if SLIPPERY_RE.search(paragraph) and not MECHANISM_RE.search(paragraph):
                self.add(
                    "slippery-slope",
                    "minor",
                    "G3",
                    "連鎖的な悪化を、各段階の根拠なしに主張している可能性がある。",
                    line=line,
                    detail=excerpt(paragraph),
                    repair="各段階の確率と機制を示す。示せないなら結論を弱める。",
                )

            # 8. 事実 → 価値
            if IS_OUGHT_RE.search(paragraph):
                self.add(
                    "is-ought",
                    "major",
                    "G7",
                    "「自然・伝統・文化」から規範を導いている。価値前提が明示されていない。",
                    line=line,
                    detail=excerpt(paragraph),
                    repair="価値前提（何を善いとするか）を明示し、事実前提と分ける。",
                )

            # 9. 生存者バイアス
            if SURVIVOR_RE.search(paragraph):
                self.add(
                    "survivorship-bias",
                    "info",
                    "G3",
                    "生存した事例だけを見ている可能性がある。失敗例・脱落例を確認する。",
                    line=line,
                    detail=excerpt(paragraph),
                    repair="比較可能な失敗例・対照群を探す。",
                )

            # 10. 基礎率の無視
            if BASE_RATE_RE.search(paragraph) and TEST_RE.search(paragraph):
                if not BASE_RATE_GUARD_RE.search(paragraph):
                    self.add(
                        "base-rate-neglect",
                        "minor",
                        "G3",
                        "検査の精度を語る文脈で、有病率・事前確率への言及がない。",
                        line=line,
                        detail=excerpt(paragraph),
                        repair="有病率（基礎率）と自然頻度で事後確率を示す。",
                    )

    def scan_structure(self) -> None:
        self.checks_run.append("structure")

        if not COUNTERARGUMENT_RE.search(self.text):
            self.add(
                "counterargument-missing",
                "minor",
                "G4",
                "反論・反対意見への言及が見つからない。",
                repair="最強の反論を1節設け、応答する。",
            )

        if not LIMITS_RE.search(self.text):
            self.add(
                "limits-missing",
                "minor",
                "G6",
                "限界・適用範囲への言及が見つからない。",
                repair="確認できていないこと、一般化できない範囲を書く。",
            )

        counts = Counter(self.citations)
        total = sum(counts.values())
        if total >= 8:
            top_key, top_count = counts.most_common(1)[0]
            if top_count / total >= 0.75:
                self.add(
                    "single-source-dominance",
                    "minor",
                    "G2",
                    "引用の75%以上が単一の出典に依存している。証拠の独立性を確認する。",
                    detail="{} / {} citations are {}".format(top_count, total, top_key),
                    repair="独立した一次資料を追加するか、結論を弱める。",
                )

    def load_ledgers(self) -> None:
        if self.claims_path:
            self.checks_run.append("claims")
            for row in read_csv_rows(self.claims_path):
                raw_id = row.get("claim_id", "") or row.get("id", "")
                digits = re.sub(r"\D", "", raw_id)
                if not digits:
                    self.add("claim-id-missing", "major", "G3", "claims.csv に claim_id のない行がある。")
                    continue
                key = "C{}".format(int(digits))
                if key in self.claims:
                    self.add("claim-duplicate-id", "major", "G3", "主張ID {} が重複している。".format(key))
                    continue
                self.claims[key] = row
                self.claim_order.append(key)

        if self.sources_path:
            self.checks_run.append("sources")
            for row in read_csv_rows(self.sources_path):
                raw_id = row.get("id", "")
                digits = re.sub(r"\D", "", raw_id)
                if digits:
                    self.sources["S{}".format(int(digits))] = row

    def scan_claims(self) -> None:
        if not self.claims:
            return
        self.checks_run.append("claim-reasoning")

        load_bearing = [key for key in self.claim_order if truthy(self.claims[key].get("load_bearing", ""))]
        if not load_bearing:
            self.add(
                "no-load-bearing-claim",
                "major",
                "G3",
                "荷重主張（load_bearing）が1つもない。結論を支える主張を特定する。",
            )
        elif len(load_bearing) > 5:
            self.add(
                "too-many-load-bearing-claims",
                "minor",
                "G3",
                "荷重主張が{}個ある。3〜5個に絞る。".format(len(load_bearing)),
            )

        for key in self.claim_order:
            row = self.claims[key]
            claim_text = row.get("claim", "")
            claim_type = row.get("claim_type", "").strip().lower()
            warrant = row.get("warrant", "").strip()
            confidence = row.get("confidence", "").strip().lower()
            status = row.get("status", "").strip().lower()
            evidence_ids = split_ids(row.get("evidence_ids", ""))
            is_load_bearing = truthy(row.get("load_bearing", ""))

            if claim_type and claim_type not in ALLOWED_CLAIM_TYPES:
                self.add(
                    "claim-type-invalid",
                    "minor",
                    "G3",
                    "主張 {} の claim_type '{}' は許容値ではない。".format(key, claim_type),
                )

            if claim_type in {"evaluative", "policy"} and not warrant:
                self.add(
                    "normative-claim-without-warrant",
                    "major",
                    "G7",
                    "規範的主張 {} に warrant（価値前提・原則）がない。".format(key),
                    detail=excerpt(claim_text),
                    repair="価値前提と原則を warrant に書き、事実前提と分ける。",
                )

            if is_load_bearing and not row.get("falsifier", "").strip():
                self.add(
                    "load-bearing-without-falsifier",
                    "major",
                    "G3",
                    "荷重主張 {} に反証条件（falsifier）がない。".format(key),
                    detail=excerpt(claim_text),
                    repair="「何が観測されたら撤回するか」を書く。",
                )

            if is_load_bearing and not row.get("counterevidence", "").strip():
                self.add(
                    "load-bearing-without-counterevidence",
                    "info",
                    "G4",
                    "荷重主張 {} に反対証拠の記録がない。".format(key),
                    detail=excerpt(claim_text),
                    repair="反対証拠・反例を探し、counterevidence に書く。",
                )

            if confidence == "high" and status in {"contested", "unverified"}:
                self.add(
                    "high-confidence-contested",
                    "major",
                    "G2",
                    "主張 {} は confidence=high だが status={}。".format(key, status or "(empty)"),
                    repair="確信度を下げるか、追加の証拠を探す。",
                )

            if claim_type == "causal" and evidence_ids and self.sources:
                source_text = " ".join(
                    " ".join(
                        [
                            self.sources[sid].get("title", ""),
                            self.sources[sid].get("notes", ""),
                            self.sources[sid].get("type", ""),
                            self.sources[sid].get("venue", ""),
                        ]
                    )
                    for sid in evidence_ids
                    if sid in self.sources
                )
                if CROSS_SECTIONAL_RE.search(source_text) and not DESIGN_RE.search(source_text):
                    self.add(
                        "causal-claim-cross-sectional-evidence",
                        "major",
                        "G3",
                        "因果主張 {} の証拠が横断・相関研究のみの可能性がある。".format(key),
                        detail=excerpt(claim_text),
                        repair="因果デザインの証拠を追加するか、主張を「関連」に弱める。",
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
            "critical": counts.get("critical", 0),
            "major": counts.get("major", 0),
            "minor": counts.get("minor", 0),
            "info": counts.get("info", 0),
            "checks_run": self.checks_run,
            "limitations": [
                "文脈・皮肉・引用・反語を完全には理解しない。",
                "誤謬の指摘は、修復案とセットで人間が確認すること。",
                "書誌の実在・引用の妥当性・統計の正しさは判定しない。",
                "claims.csv の意味的な整合性は、人間の読解が必要である。",
            ],
        }

    def run(self) -> Dict[str, Any]:
        if not self.raw_text.strip():
            self.add("article-empty", "critical", "G1", "記事本文が空である。")
        self.scan_paragraphs()
        self.scan_structure()
        self.load_ledgers()
        self.scan_claims()

        for index, finding in enumerate(
            sorted(
                self.findings,
                key=lambda f: (SEVERITY_ORDER.get(f["severity"], 9), f.get("line") or 0),
            ),
            start=1,
        ):
            finding["id"] = "L{:03d}".format(index)

        return {
            "tool": "argument_lint.py",
            "version": VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "inputs": {
                "article": self.article_path.as_posix(),
                "claims": self.claims_path.as_posix() if self.claims_path else None,
                "sources": self.sources_path.as_posix() if self.sources_path else None,
            },
            "summary": self.summary(),
            "findings": self.findings,
        }


# ---------------------------------------------------------------------------
# 出力
# ---------------------------------------------------------------------------


def render_text(report: Dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "=== Universal Article Writer — Argument Lint v{} ===".format(report["version"]),
        "Article : {}".format(report["inputs"]["article"]),
        "Claims  : {}".format(report["inputs"]["claims"] or "(not provided)"),
        "Sources : {}".format(report["inputs"]["sources"] or "(not provided)"),
        "",
        "--- Summary ---",
        "Verdict   : {}".format(summary["verdict"]),
        "Findings  : Critical {} / Major {} / Minor {} / Info {}".format(
            summary["critical"], summary["major"], summary["minor"], summary["info"]
        ),
        "",
    ]
    if report["findings"]:
        lines.append("--- Findings ---")
        for finding in report["findings"]:
            location = " line {}".format(finding["line"]) if finding.get("line") else ""
            lines.append(
                "[{:<8}] {:<32} {}{}".format(
                    finding["severity"].upper(), finding["check"], finding["gate"], location
                )
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
    lines.append("Note: this lint catches patterns, not meaning. A human must verify context.")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="論理記事工房の推論監査。相関→因果、非有意→効果なし、一般化、誤謬の型を点検する。",
    )
    parser.add_argument("--article", required=True, help="監査する記事の Markdown ファイル")
    parser.add_argument("--claims", help="主張と証拠の対応 CSV")
    parser.add_argument("--sources", help="出典台帳の CSV")
    parser.add_argument("--out", help="JSON レポートの出力先")
    parser.add_argument("--format", choices=["text", "json", "both"], default="text")
    parser.add_argument(
        "--fail-on",
        choices=["none", "critical", "major", "minor"],
        default="none",
        help="この重大度以上があれば終了コード 2（既定: none）",
    )
    parser.add_argument("--version", action="version", version="argument_lint.py {}".format(VERSION))
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    configure_stdout()
    args = build_parser().parse_args(argv)

    article_path = Path(args.article)
    claims_path = Path(args.claims) if args.claims else None
    sources_path = Path(args.sources) if args.sources else None

    for label, path in [("article", article_path), ("claims", claims_path), ("sources", sources_path)]:
        if path is not None and not path.exists():
            print("ERROR: {} file not found: {}".format(label, path), file=sys.stderr)
            return 3

    try:
        linter = Linter(article_path, claims_path, sources_path)
        report = linter.run()
    except Exception as exc:  # noqa: BLE001
        print("ERROR: argument lint failed: {}".format(exc), file=sys.stderr)
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
