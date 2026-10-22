#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build UNIVERSAL-PROMPT.md from SKILL.md.

SKILL.md is the single source of truth. This script strips its YAML
frontmatter and prepends a short, host-neutral header so the result can be
pasted into any AI as a system prompt or custom instruction.

Usage:
    python scripts/build_universal.py
    python scripts/build_universal.py --check   # fail if the output is stale
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "SKILL.md"
TARGET = ROOT / "UNIVERSAL-PROMPT.md"

HEADER = """# 論理記事工房 — Universal Prompt

> これは、任意のAIのシステムプロンプト、カスタム指示、プロジェクト指示に
> 貼り付けて使う指示書である。ファイル・Web検索・コード実行がない環境でも、
> 「2. 実行環境に応じた適応」に従って動く。
> 深いリファレンスは `references/` にあるが、読めなくても本文だけで動く。

あなたは、証拠と論証を最優先するリサーチ・ライターとして振る舞う。
以下の指示に従う。

---

"""


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    match = re.match(r"\A---\r?\n.*?\r?\n---\r?\n", text, flags=re.S)
    if not match:
        raise ValueError("SKILL.md starts with '---' but the frontmatter is not closed")
    return text[match.end():]


def build() -> str:
    body = strip_frontmatter(SOURCE.read_text(encoding="utf-8"))
    return HEADER + body.lstrip("\ufeff")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit 1 if UNIVERSAL-PROMPT.md is out of date",
    )
    args = parser.parse_args()

    expected = build()
    if args.check:
        if not TARGET.exists():
            print("UNIVERSAL-PROMPT.md is missing", file=sys.stderr)
            return 1
        actual = TARGET.read_text(encoding="utf-8")
        if actual != expected:
            print("UNIVERSAL-PROMPT.md is stale; run scripts/build_universal.py", file=sys.stderr)
            return 1
        print("UNIVERSAL-PROMPT.md is up to date")
        return 0

    with TARGET.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(expected)
    print(f"wrote {TARGET} ({len(expected.splitlines())} lines, {len(expected)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
