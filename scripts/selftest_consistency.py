"""Mutation test for scripts/check_consistency.py.

Each case copies the repository to a temporary directory, breaks exactly one
cross-artifact relation, and checks that the consistency checker fails for the
expected reason. A control case checks that the unmodified copy passes.

This is the falsification test for the "consistency is guaranteed" claim: a
checker that cannot fail is not a guarantee.

Usage:
    python scripts/selftest_consistency.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYTHON = sys.executable
CHECKER = ROOT / "scripts" / "check_consistency.py"

TOP_FILES = [
    "SKILL.md",
    "UNIVERSAL-PROMPT.md",
    "UNIVERSAL-PROMPT-LITE.md",
    "AGENTS.md",
    "README.md",
    "README.ja.md",
    "README.zh-CN.md",
]
DIRS = ["references", "assets", "docs", "evals", "scripts"]


def copy_repo(destination: Path) -> None:
    for name in TOP_FILES:
        shutil.copy2(ROOT / name, destination / name)
    for name in DIRS:
        shutil.copytree(
            ROOT / name,
            destination / name,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )


def run_checker(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, str(CHECKER), "--root", str(root)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError("mutation target not found: {!r} in {}".format(old, path.name))
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


def mutate_rule(root: Path) -> None:
    replace(root / "SKILL.md", "**R05 主張の種類を守る。**", "**R99 主張の種類を守る。**")


def mutate_phase_table(root: Path) -> None:
    path = root / "docs/architecture.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    kept = [line for line in lines if not line.startswith("| 3.5 Normative")]
    if len(kept) == len(lines):
        raise AssertionError("phase 3.5 row not found")
    path.write_text("\n".join(kept) + "\n", encoding="utf-8", newline="\n")


def mutate_role_count(root: Path) -> None:
    replace(root / "references/orchestration.md", "Red team（6役）", "Red team（5役）")


def mutate_eval_id(root: Path) -> None:
    path = root / "evals/evals.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["cases"] = [case for case in data["cases"] if case["id"] != "E12"]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def mutate_generated_prompt(root: Path) -> None:
    path = root / "UNIVERSAL-PROMPT.md"
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write("\n<!-- stale -->\n")


def mutate_duplicate_pattern(root: Path) -> None:
    replace(root / "SKILL.md", "**P03 偽の均衡**", "**P03 引用の飾り**")


CASES = [
    ("control (no mutation)", None, None),
    ("rule ID gap", mutate_rule, "not contiguous"),
    ("phase 3.5 row removed", mutate_phase_table, "architecture phase table differs"),
    ("five-role red team", mutate_role_count, "five-role"),
    ("eval case removed", mutate_eval_id, "not contiguous"),
    ("stale generated prompt", mutate_generated_prompt, "stale"),
    ("duplicate forbidden pattern", mutate_duplicate_pattern, "duplicate titles"),
]


def main() -> int:
    failures = 0
    scratch = ROOT / ".mutation-tmp"
    shutil.rmtree(scratch, ignore_errors=True)
    scratch.mkdir(parents=True)
    try:
        for name, mutate, expected in CASES:
            work = scratch / name.replace(" ", "-").replace("(", "").replace(")", "")
            work.mkdir()
            copy_repo(work)
            if mutate is not None:
                mutate(work)
            proc = run_checker(work)
            output = (proc.stdout or "") + (proc.stderr or "")

            if mutate is None:
                if proc.returncode == 0:
                    print("  PASS  control: unmodified copy passes")
                else:
                    print("  FAIL  control: unmodified copy failed")
                    print(output[-1500:])
                    failures += 1
            else:
                if proc.returncode == 1 and expected in output:
                    print("  PASS  mutation detected: {} (exit 1, {!r})".format(name, expected))
                else:
                    print("  FAIL  mutation not detected as expected: {}".format(name))
                    print("        exit={} expected substring={!r}".format(proc.returncode, expected))
                    print(output[-1500:])
                    failures += 1
            shutil.rmtree(work, ignore_errors=True)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    print("\n== Summary ==")
    print("  cases: {}".format(len(CASES)))
    print("  failed: {}".format(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
