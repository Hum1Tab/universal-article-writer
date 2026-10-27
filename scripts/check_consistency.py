#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cross-artifact consistency checks for Universal Article Writer.

`SKILL.md` is the canonical source for rule IDs, phases, modes, red-team roles,
and forbidden-pattern IDs. This script parses those identifiers from `SKILL.md`
and checks that the other artifacts agree.

It is deliberately narrow. It proves that the encoded relations hold, not that
the protocol is correct, that a model follows it, or that an article is good.
See `docs/design-notes.md` §3.

Usage:
    python scripts/check_consistency.py
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


def _root() -> Path:
    """Allow a copied repository to be checked without touching the original.

    Usage: ``check_consistency.py --root /path/to/copy``. The mutation test
    uses this; normal CI does not.
    """
    argv = sys.argv[1:]
    for index, arg in enumerate(argv):
        if arg == "--root" and index + 1 < len(argv):
            return Path(argv[index + 1]).resolve()
        if arg.startswith("--root="):
            return Path(arg.split("=", 1)[1]).resolve()
    return Path(__file__).resolve().parent.parent


ROOT = _root()
PYTHON = sys.executable


class Report:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0
        self.failures: List[str] = []

    def ok(self, message: str) -> None:
        self.passed += 1
        print("  PASS  {}".format(message))

    def fail(self, message: str, detail: str = "") -> None:
        self.failed += 1
        self.failures.append(message)
        print("  FAIL  {}".format(message))
        if detail:
            for line in detail.splitlines():
                print("        {}".format(line))


R = Report()


def read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8-sig")


def fail_detail(message: str, detail: str) -> None:
    R.fail(message, detail)


def section(text: str, start: str, end: str) -> Optional[str]:
    start_at = text.find(start)
    if start_at < 0:
        return None
    end_at = text.find(end, start_at + len(start))
    if end_at < 0:
        return None
    return text[start_at:end_at]


def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = value.lower().replace("　", " ")
    value = re.sub(r"[^a-z0-9 ]+", "", value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_title(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = value.lower()
    return re.sub(r"[\s、。，．・：:；;（）()「」『』\"'`]", "", value)


# ---------------------------------------------------------------------------
# 1. Frontmatter and scope
# ---------------------------------------------------------------------------


def check_description() -> None:
    text = read("SKILL.md")
    match = re.match(r"^\ufeff?---\s*\r?\n(.*?)\r?\n---", text, re.S)
    if not match:
        R.fail("SKILL.md has no frontmatter")
        return
    fm = match.group(1)
    desc_match = re.search(r"(?ms)^description:\s*(.+?)(?=^license:)", fm)
    if not desc_match:
        R.fail("description is missing")
        return
    description = desc_match.group(1)

    in_scope = ["論考", "ファクトチェック", "設計判断"]
    missing = [word for word in in_scope if word not in description]
    if missing:
        R.fail("description does not name the intended scope", "missing: {}".format(", ".join(missing)))
    else:
        R.ok("description names evidence-bearing scope")

    # The v3.0 description fired on light copy-editing requests. Keep those
    # exact trigger phrases out of the description so the skill is not loaded
    # for low-loss edits.
    forbidden = ["読みやすくして", "見出しを強くして", "文体を整えて", "推敲して", "note に合う形"]
    hits = [phrase for phrase in forbidden if phrase in description]
    if hits:
        R.fail("description still contains low-loss editing triggers", "\n".join(hits))
    else:
        R.ok("description has no low-loss editing triggers")


# ---------------------------------------------------------------------------
# 2. Rule IDs
# ---------------------------------------------------------------------------


def extract_rule_ids(text: str, start: str, end: str) -> List[str]:
    block = section(text, start, end)
    if block is None:
        return []
    return re.findall(r"(?m)^\s*\d+\.\s+\*\*(R\d{2})[ 　]", block)


def check_rules() -> None:
    skill = read("SKILL.md")
    ids = extract_rule_ids(skill, "## 1. 絶対規則", "\n## 2.")
    expected = ["R{:02d}".format(i) for i in range(1, len(ids) + 1)]
    if len(ids) < 10:
        R.fail("SKILL.md has too few absolute rules", "found: {}".format(", ".join(ids)))
    elif ids != expected:
        R.fail("rule IDs are not contiguous R01..Rnn", "found: {}".format(", ".join(ids)))
    elif len(set(ids)) != len(ids):
        R.fail("rule IDs are duplicated", "found: {}".format(", ".join(ids)))
    else:
        R.ok("SKILL.md defines {} contiguous rule IDs (R01–{})".format(len(ids), ids[-1]))

    lite = read("UNIVERSAL-PROMPT-LITE.md")
    lite_ids = extract_rule_ids(lite, "## 1. 絶対規則", "\n## 2.")
    if not lite_ids:
        R.fail("UNIVERSAL-PROMPT-LITE.md has no rule IDs")
    elif set(lite_ids) != set(ids):
        R.fail(
            "LITE rule IDs differ from SKILL.md",
            "only in SKILL: {}\nonly in LITE: {}".format(
                ", ".join(sorted(set(ids) - set(lite_ids))) or "-",
                ", ".join(sorted(set(lite_ids) - set(ids))) or "-",
            ),
        )
    else:
        R.ok("LITE carries the same {} rule IDs".format(len(ids)))

    agents = read("AGENTS.md")
    if "R01–{}".format(ids[-1]) in agents or "R01-{}".format(ids[-1]) in agents:
        R.ok("AGENTS.md points at the canonical rule range")
    else:
        R.fail("AGENTS.md does not point at the canonical rule range (R01–{})".format(ids[-1]))


# ---------------------------------------------------------------------------
# 3. Phases
# ---------------------------------------------------------------------------


def extract_skill_phases(text: str) -> List[str]:
    block = section(text, "## 4. フェーズと出口条件", "\n## 5.")
    if block is None:
        return []
    return re.findall(r"(?m)^\|\s*(\d+(?:\.\d+)?)\s", block)


def check_phases() -> None:
    skill = read("SKILL.md")
    phases = extract_skill_phases(skill)
    if not phases:
        R.fail("SKILL.md has no '### Phase N' headings")
        return
    if len(set(phases)) != len(phases):
        R.fail("SKILL.md phase headings are duplicated", ", ".join(phases))
    else:
        R.ok("SKILL.md defines phases {}".format(", ".join(phases)))

    arch = read("docs/architecture.md")
    table_block = section(arch, "## 3. Phases and gates", "## 4.")
    if table_block is None:
        R.fail("architecture.md has no phase table")
        return
    table_phases = re.findall(r"(?m)^\|\s*(\d+(?:\.\d+)?)\.?\s", table_block)
    if set(table_phases) != set(phases):
        R.fail(
            "architecture phase table differs from SKILL.md",
            "SKILL: {}\nTABLE: {}".format(", ".join(phases), ", ".join(table_phases)),
        )
    else:
        R.ok("architecture phase table matches SKILL.md")

    # The diagram deliberately omits Phase 0 (intake), so it is checked as a
    # subset. It must not invent a phase, and it must agree on Phase 3.5.
    diagram_phases = re.findall(r"Phase (\d+(?:\.\d+)?)", arch)
    phantom = sorted(set(diagram_phases) - set(phases), key=float)
    if phantom:
        R.fail("architecture diagram contains phases absent from SKILL.md", ", ".join(phantom))
    elif ("3.5" in diagram_phases) != ("3.5" in phases):
        R.fail("architecture diagram and SKILL.md disagree about Phase 3.5")
    else:
        R.ok("architecture diagram agrees with SKILL.md (no phantom phases)")

    orch = read("references/orchestration.md")
    pipeline = section(orch, "## 2. パイプライン", "## 3.")
    if pipeline is None:
        R.fail("orchestration.md has no pipeline")
        return
    orch_phases = re.findall(r"Phase (\d+(?:\.\d+)?)", pipeline)
    if set(orch_phases) != set(phases):
        R.fail(
            "orchestration pipeline phase set differs from SKILL.md",
            "SKILL: {}\nORCH:  {}".format(", ".join(phases), ", ".join(sorted(set(orch_phases), key=float))),
        )
    else:
        R.ok("orchestration pipeline matches SKILL.md")

    if "3.5" in phases:
        R.ok("Phase 3.5 exists in SKILL.md (not only in the diagram)")
    else:
        R.fail("Phase 3.5 is missing from SKILL.md")


# ---------------------------------------------------------------------------
# 4. Red-team roles
# ---------------------------------------------------------------------------


def check_roles() -> None:
    skill = read("SKILL.md")
    block = section(skill, "### 6.2", "### 6.3")
    if block is None:
        R.fail("SKILL.md has no §6.2 red-team section")
        return
    skill_roles = [normalize_name(name) for name in re.findall(r"(?m)^\|\s*\*\*([^*]+)\*\*\s*\|", block)]
    if len(skill_roles) != 6:
        R.fail("SKILL.md must list exactly 6 red-team roles", "found: {}".format(", ".join(skill_roles)))
    else:
        R.ok("SKILL.md lists 6 red-team roles")

    arch = read("docs/architecture.md")
    arch_block = section(arch, "## 4. The six red-team roles", "## 5.")
    arch_roles = (
        [normalize_name(name) for name in re.findall(r"(?m)^\|\s*\*\*([^*]+)\*\*\s*\|", arch_block)]
        if arch_block
        else []
    )

    orch = read("references/orchestration.md")
    orch_block = section(orch, "### 1.8", "### 1.9")
    orch_roles = []
    if orch_block:
        for line in orch_block.splitlines():
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) != 2:
                continue
            name = cells[0]
            if not re.fullmatch(r"[A-Za-z][A-Za-z ]+", name):
                continue
            orch_roles.append(normalize_name(name))

    if set(arch_roles) != set(skill_roles):
        R.fail(
            "architecture role set differs from SKILL.md",
            "SKILL: {}\nARCH:  {}".format(", ".join(sorted(skill_roles)), ", ".join(sorted(arch_roles))),
        )
    else:
        R.ok("architecture role set matches SKILL.md")

    if set(orch_roles) != set(skill_roles):
        R.fail(
            "orchestration role set differs from SKILL.md",
            "SKILL: {}\nORCH:  {}".format(", ".join(sorted(skill_roles)), ", ".join(sorted(orch_roles))),
        )
    else:
        R.ok("orchestration role set matches SKILL.md")

    five_role_hits = []
    for rel_path in ["SKILL.md", "docs/architecture.md", "references/orchestration.md"]:
        text = read(rel_path)
        if re.search(r"5役|five roles|5 roles", text):
            five_role_hits.append(rel_path)
    if five_role_hits:
        R.fail("artifact still describes a five-role red team", "\n".join(five_role_hits))
    else:
        R.ok("no artifact describes a five-role red team")


# ---------------------------------------------------------------------------
# 5. Modes
# ---------------------------------------------------------------------------


def extract_modes(text: str) -> List[str]:
    return re.findall(r"(?m)^\|\s*`([a-z][a-z-]+)`\s*\|", text)


def check_modes() -> None:
    skill = read("SKILL.md")
    skill_block = section(skill, "## 3. モード選択", "### 3.1")
    modes = extract_modes(skill_block or "")
    if "decision" not in modes:
        R.fail("SKILL.md does not define the decision mode")
    else:
        R.ok("SKILL.md defines {} modes including decision".format(len(set(modes))))

    lite = read("UNIVERSAL-PROMPT-LITE.md")
    lite_block = section(lite, "## 3", "## 4")
    lite_modes = extract_modes(lite_block or "")
    if set(lite_modes) != set(modes):
        R.fail(
            "LITE mode set differs from SKILL.md",
            "only in SKILL: {}\nonly in LITE: {}".format(
                ", ".join(sorted(set(modes) - set(lite_modes))) or "-",
                ", ".join(sorted(set(lite_modes) - set(modes))) or "-",
            ),
        )
    else:
        R.ok("LITE mode set matches SKILL.md")


# ---------------------------------------------------------------------------
# 6. Forbidden patterns
# ---------------------------------------------------------------------------


def check_patterns() -> None:
    skill = read("SKILL.md")
    block = section(skill, "## 8. 禁止パターン", "## 9.")
    if block is None:
        R.fail("SKILL.md has no forbidden-pattern section")
        return
    pairs = re.findall(r"(?m)^\s*\d+\.\s+\*\*(P\d{2})[ 　]([^*]+?)\*\*", block)
    ids = [pid for pid, _ in pairs]
    expected = ["P{:02d}".format(i) for i in range(1, len(ids) + 1)]
    if ids != expected:
        R.fail("pattern IDs are not contiguous P01..Pnn", "found: {}".format(", ".join(ids)))
        return
    titles = [normalize_title(title) for _, title in pairs]
    duplicates = sorted({title for title in titles if titles.count(title) > 1})
    if duplicates:
        R.fail("forbidden patterns contain duplicate titles", "\n".join(duplicates))
    else:
        R.ok("{} forbidden patterns with unique titles".format(len(ids)))


# ---------------------------------------------------------------------------
# 7. Phase traceability
# ---------------------------------------------------------------------------


def check_traceability() -> None:
    """Every phase needs an observable exit condition and a readable detail file.

    This is the fallback contract: if the references cannot be read, the model
    still has the exit conditions. A phase without either is a hole.
    """
    skill = read("SKILL.md")
    block = section(skill, "## 4. フェーズと出口条件", "\n## 5.")
    if block is None:
        R.fail("SKILL.md has no phase table")
        return

    rows = [line for line in block.splitlines() if re.match(r"^\|\s*\d", line)]
    problems: List[str] = []
    for row in rows:
        cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
        if len(cells) < 4:
            problems.append("malformed row: {}".format(row[:60]))
            continue
        phase, exit_condition, detail = cells[0], cells[2], cells[3]
        if len(exit_condition) < 10:
            problems.append("{} has no observable exit condition".format(phase))
        paths = re.findall(r"`([^`]+)`", detail)
        if not paths:
            problems.append("{} names no detail file".format(phase))
        for path in paths:
            candidates = [
                ROOT / path,
                ROOT / "references" / path,
                ROOT / "assets" / path,
                ROOT / "scripts" / path,
            ]
            if not any(candidate.exists() for candidate in candidates):
                problems.append("{} names a missing detail file: {}".format(phase, path))

    if problems:
        R.fail("phase traceability is incomplete", "\n".join(problems))
    else:
        R.ok("every phase has an exit condition and an existing detail file")

    if "読めない" in skill and "明記" in skill:
        R.ok("SKILL.md states the degraded path when references are unreadable")
    else:
        R.fail("SKILL.md does not state what to do when references are unreadable")


# ---------------------------------------------------------------------------
# 8. Artifact contract and gates
# ---------------------------------------------------------------------------


def check_contracts() -> None:
    skill = read("SKILL.md")
    required = [
        "article.md",
        "decision-memo.md",
        "sources.csv",
        "claims.csv",
        "dossier.md",
        "logic-report.md",
    ]
    missing = [name for name in required if "`{}`".format(name) not in skill]
    if missing:
        R.fail("output contract is missing required artifacts", ", ".join(missing))
    else:
        R.ok("output contract names all required artifacts")

    gates = re.findall(r"(?m)^\|\s*(G[0-7])\s", skill)
    if gates == ["G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7"]:
        R.ok("G0–G7 are defined once, in order")
    else:
        R.fail("gate table is incomplete or out of order", "found: {}".format(", ".join(gates)))


# ---------------------------------------------------------------------------
# 9. Reference files
# ---------------------------------------------------------------------------


def check_references() -> None:
    skill = read("SKILL.md")
    block = section(skill, "## 7. 参照ファイル", "## 8.")
    if block is None:
        R.fail("SKILL.md has no reference table")
        return
    named = set(re.findall(r"`((?:references|assets|scripts)/[^`]+)`", block))
    missing = sorted(path for path in named if not (ROOT / path).exists())
    if missing:
        R.fail("SKILL.md names files that do not exist", "\n".join(missing))
    else:
        R.ok("all {} named reference/asset/script files exist".format(len(named)))

    actual = {path.relative_to(ROOT).as_posix() for path in (ROOT / "references").glob("*.md")}
    unnamed = sorted(actual - named)
    if unnamed:
        R.fail("reference files are not listed in SKILL.md §7", "\n".join(unnamed))
    else:
        R.ok("all {} reference files are listed in SKILL.md".format(len(actual)))


# ---------------------------------------------------------------------------
# 8. Counts
# ---------------------------------------------------------------------------


def check_counts() -> None:
    try:
        evals = json.loads(read("evals/evals.json"))
    except Exception as exc:
        R.fail("evals/evals.json does not parse", str(exc))
        return
    cases = evals.get("cases", [])
    count = len(cases)
    ids = [case.get("id") for case in cases]
    expected_ids = ["E{:02d}".format(i) for i in range(1, count + 1)]
    if ids != expected_ids:
        R.fail("eval case IDs are not contiguous E01..Enn", "found: {}".format(", ".join(map(str, ids))))
        return
    R.ok("evals/evals.json has {} cases (E01–E{:02d})".format(count, count))

    benchmark = read("docs/benchmark.md")
    bench_count = len(re.findall(r"(?m)^\| E\d{2} \|", benchmark))
    if bench_count != count:
        R.fail("benchmark case table does not match evals.json", "table: {} / json: {}".format(bench_count, count))
    else:
        R.ok("benchmark case table has {} rows".format(count))

    patterns = {
        "README.md": [r"\*\*(\d+) behavioral cases", r"evals-(\d+)%20cases"],
        "README.ja.md": [r"(\d+)の行動評価", r"evals-(\d+)%20cases"],
        "README.zh-CN.md": [r"(\d+) 个行为评", r"evals-(\d+)%20cases"],
        "docs/guide.ja.md": [r"(\d+)の行動評価ケース"],
    }
    for rel_path, regexes in patterns.items():
        text = read(rel_path)
        for regex in regexes:
            found = [int(value) for value in re.findall(regex, text)]
            if not found:
                R.fail("{}: cannot find a documented case count for {!r}".format(rel_path, regex))
            elif any(value != count for value in found):
                R.fail(
                    "{}: documented case count is stale for {!r}".format(rel_path, regex),
                    "found: {} / expected: {}".format(found, count),
                )
            else:
                R.ok("{}: documented case count = {}".format(rel_path, count))

    check_repo = read("scripts/check_repo.py")
    match = re.search(r"range\(1, (\d+)\)", check_repo)
    if not match:
        R.fail("check_repo.py has no expected eval range")
    elif int(match.group(1)) - 1 != count:
        R.fail(
            "check_repo.py expects a different number of cases",
            "range: {} / json: {}".format(int(match.group(1)) - 1, count),
        )
    else:
        R.ok("check_repo.py expects the same number of cases")


# ---------------------------------------------------------------------------
# 9. Size claims
# ---------------------------------------------------------------------------


def check_size_claim() -> None:
    skill_lines = len(read("SKILL.md").splitlines())
    if skill_lines <= 500:
        R.ok("SKILL.md is {} lines (<= 500)".format(skill_lines))
    else:
        R.fail("SKILL.md is {} lines, above the 500-line budget".format(skill_lines))

    stack = read("references/skill-stack.md")
    match = re.search(r"(\d+)行以下の本体", stack)
    if not match:
        R.fail("skill-stack.md makes no size claim")
    elif skill_lines > int(match.group(1)):
        R.fail(
            "skill-stack.md claims a size that SKILL.md exceeds",
            "claim: <= {} / actual: {}".format(match.group(1), skill_lines),
        )
    else:
        R.ok("skill-stack.md size claim holds (<= {} lines)".format(match.group(1)))


# ---------------------------------------------------------------------------
# 10. Generated prompt
# ---------------------------------------------------------------------------


def check_generated_prompt() -> None:
    builder = ROOT / "scripts" / "build_universal.py"
    if not builder.is_file():
        R.fail("build_universal.py is missing")
        return
    proc = subprocess.run(
        [PYTHON, str(builder), "--check"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode == 0:
        R.ok("UNIVERSAL-PROMPT.md is in sync with SKILL.md")
    else:
        R.fail("UNIVERSAL-PROMPT.md is stale", (proc.stdout + proc.stderr).strip())


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    print("Universal Article Writer — cross-artifact consistency")
    print("Root: {}".format(ROOT))

    check_description()
    check_rules()
    check_phases()
    check_roles()
    check_modes()
    check_patterns()
    check_traceability()
    check_contracts()
    check_references()
    check_counts()
    check_size_claim()
    check_generated_prompt()

    print("\n== Summary ==")
    print("  passed: {}".format(R.passed))
    print("  failed: {}".format(R.failed))
    if R.failed:
        print("\nConsistency checks failed.")
        return 1
    print("\nAll consistency checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
