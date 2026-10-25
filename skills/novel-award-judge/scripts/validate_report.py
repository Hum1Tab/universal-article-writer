#!/usr/bin/env python3
"""Validate a mock fiction-award review. Structural checks only; NOT judge accuracy."""
from __future__ import annotations
import json
import sys
from pathlib import Path

KEYS = ("originality", "voice", "character", "structure", "theme", "setting", "consistency", "audience")
WEIGHTS = {
    "general": (16, 16, 16, 16, 14, 8, 8, 6),
    "literary": (22, 22, 12, 10, 18, 8, 5, 3),
    "entertainment": (15, 12, 18, 20, 10, 8, 10, 7),
    "mystery": (13, 10, 14, 20, 7, 8, 23, 5),
    "light-novel": (16, 9, 20, 20, 6, 7, 10, 12),
    "short": (20, 18, 12, 17, 14, 6, 9, 4),
    "web": (13, 9, 16, 23, 6, 7, 10, 16),
}
PANEL = ("language", "story", "originality", "editor")


def validate(doc: dict) -> list[str]:
    errors = []
    profile = doc.get("profile")
    scope = doc.get("scope")
    if profile not in WEIGHTS:
        return ["profile must be one of " + ", ".join(WEIGHTS)]
    if scope not in ("full", "partial"):
        errors.append("scope must be full or partial")
    dims = doc.get("dimensions", {})
    if not isinstance(dims, dict):
        return ["dimensions must be an object"]
    if set(dims) != set(KEYS):
        errors.append("dimensions must contain exactly the 8 rubric keys")
    total = 0
    for key, maximum in zip(KEYS, WEIGHTS[profile]):
        data = dims.get(key)
        if not isinstance(data, dict):
            errors.append(f"{key}: missing object")
            continue
        if data.get("max") != maximum:
            errors.append(f"{key}: expected max={maximum}")
        score = data.get("score")
        if scope == "full":
            if type(score) is not int or not 0 <= score <= maximum:
                errors.append(f"{key}: full scope requires integer score 0..{maximum}")
            else:
                total += score
        elif score is not None:
            errors.append(f"{key}: partial scope must use score=null")
        ev = data.get("evidence", [])
        if not isinstance(ev, list) or (scope == "full" and len(ev) < 2):
            errors.append(f"{key}: full scope requires >=2 evidence records")
        elif isinstance(ev, list):
            for j, item in enumerate(ev):
                if not isinstance(item, dict) or not all(isinstance(item.get(f), str) and item[f].strip()
                                                        for f in ("locator", "excerpt", "reason")):
                    errors.append(f"{key}: evidence[{j}] needs locator/excerpt/reason")
        if not isinstance(data.get("alternative"), str) or not data["alternative"].strip():
            errors.append(f"{key}: missing counterreading")
        if data.get("confidence") not in ("high", "medium", "low"):
            errors.append(f"{key}: confidence must be high/medium/low")
    reported = doc.get("total")
    if scope == "full" and (type(reported) is not int or reported != total):
        errors.append(f"total: expected {total}")
    if scope == "partial" and reported is not None:
        errors.append("partial scope requires total=null")
    contest = doc.get("contest", {})
    if not isinstance(contest, dict):
        errors.append("contest must be an object")
    else:
        if contest.get("eligibility") not in ("valid", "invalid", "unknown"):
            errors.append("contest.eligibility must be valid/invalid/unknown")
        if type(contest.get("rules_verified")) is not bool:
            errors.append("contest.rules_verified must be boolean")
        if contest.get("rules_verified") and not contest.get("rules_url"):
            errors.append("verified contest requires rules_url")
        if not contest.get("rules_verified") and contest.get("eligibility") != "unknown":
            errors.append("cannot verify eligibility without verified official rules")
    panel = doc.get("panel", {})
    if not isinstance(panel, dict) or set(panel) != set(PANEL):
        errors.append("panel must contain language/story/originality/editor")
    else:
        for name, item in panel.items():
            if not isinstance(item, dict) or not all(isinstance(item.get(f), str) and item[f].strip()
                                                     for f in ("support", "concern", "change_condition")):
                errors.append(f"panel.{name} needs support/concern/change_condition")
    for name in ("blockers", "revision_priorities", "limitations"):
        if not isinstance(doc.get(name), list):
            errors.append(f"{name}: required list")
    if scope == "full" and isinstance(doc.get("revision_priorities"), list) and len(doc["revision_priorities"]) < 3:
        errors.append("full scope requires 3 revision priorities")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python validate_report.py path/to/report.json", file=sys.stderr)
        return 3
    try:
        data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("JSON root must be an object")
        errors = validate(data)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"INPUT ERROR: {exc}", file=sys.stderr)
        return 3
    if errors:
        for err in errors:
            print("FAIL:", err)
        return 2
    print("PASS: structurally valid. Scores and prose are NOT verified against manuscript.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
