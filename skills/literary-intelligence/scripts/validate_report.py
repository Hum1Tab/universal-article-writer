#!/usr/bin/env python3
"""Structural validation only. It cannot decide whether a literary judgment is true."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

KEYS = [f"Q{i}" for i in range(1, 11)]
LENSES = {f"L{i}" for i in range(1, 9)}
STATUSES = {"strong", "mixed", "limited", "not_applicable", "unknown"}
CONFIDENCES = {"high", "medium", "low"}
CLAIM_TYPES = {"textual", "interpretive", "evaluative", "empirical", "predicted"}
CLAIM_STATUSES = {"supported", "contested", "weak", "undetermined"}

def normalized(text: str) -> str:
    """Normalize whitespace only; never rewrite punctuation or semantic content."""
    return re.sub(r"\s+", " ", text).strip()

def validate(data: dict, manuscript: str | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root: expected object"]
    if data.get("schema_version") != "1.0.0":
        errors.append("schema_version: expected 1.0.0")
    if data.get("coverage") not in {"full", "partial"}:
        errors.append("coverage: expected full or partial")
    if type(data.get("numeric_requested")) is not bool:
        errors.append("numeric_requested: expected boolean")
    if data.get("universal_score", "MISSING") is not None:
        errors.append("universal_score must explicitly be null")
    if not isinstance(data.get("title"), str):
        errors.append("title: required string")

    evidence = data.get("evidence")
    if not isinstance(evidence, list):
        return errors + ["evidence: required list"]
    ids = set()
    source = normalized(manuscript) if manuscript is not None else None
    for n, item in enumerate(evidence):
        if not isinstance(item, dict):
            errors.append(f"evidence[{n}]: object required")
            continue
        ident = item.get("id")
        if not isinstance(ident, str) or not ident:
            errors.append(f"evidence[{n}].id required")
        elif ident in ids:
            errors.append(f"evidence[{n}].id duplicate: {ident}")
        else:
            ids.add(ident)
        for prop in ("locator", "quote", "observation", "area"):
            if not isinstance(item.get(prop), str) or not item[prop].strip():
                errors.append(f"evidence[{n}].{prop}: required string")
        if item.get("area") not in {"opening", "middle", "ending", "local"}:
            errors.append(f"evidence[{n}].area: invalid")
        if source is not None and isinstance(item.get("quote"), str):
            quote = normalized(item["quote"])
            if quote and quote not in source:
                errors.append(f"evidence[{n}]: quote not found in manuscript ({ident})")

    claims = data.get("claims")
    if not isinstance(claims, list):
        errors.append("claims: required list")
        claims = []
    if data.get("coverage") == "full" and not claims:
        errors.append("full coverage: at least one documented claim required")
    for n, item in enumerate(claims):
        if not isinstance(item, dict):
            errors.append(f"claims[{n}]: object required")
            continue
        if item.get("type") not in CLAIM_TYPES:
            errors.append(f"claims[{n}].type invalid")
        if item.get("status") not in CLAIM_STATUSES:
            errors.append(f"claims[{n}].status invalid")
        if item.get("confidence") not in CONFIDENCES:
            errors.append(f"claims[{n}].confidence invalid")
        for prop in ("id","claim","warrant","value_premise","counterreading","change_condition"):
            if not isinstance(item.get(prop), str) or not item[prop].strip():
                errors.append(f"claims[{n}].{prop}: required string")
        linked = item.get("evidence_ids")
        if not isinstance(linked, list) or not linked:
            errors.append(f"claims[{n}].evidence_ids: nonempty list required")
        else:
            for ev in linked:
                if ev not in ids:
                    errors.append(f"claims[{n}]: unknown evidence id {ev!r}")
        if item.get("type") == "empirical" and not item.get("measured_source"):
            errors.append(f"claims[{n}]: empirical claim requires measured_source")

    quality = data.get("quality")
    if not isinstance(quality, dict) or set(quality) != set(KEYS):
        errors.append("quality: exactly Q1..Q10 required")
    else:
        for key in KEYS:
            q = quality[key]
            if not isinstance(q, dict):
                errors.append(f"quality.{key}: object required")
                continue
            status = q.get("status")
            if status not in STATUSES:
                errors.append(f"quality.{key}.status invalid")
            if q.get("confidence") not in CONFIDENCES:
                errors.append(f"quality.{key}.confidence invalid")
            if not isinstance(q.get("rationale"), str) or not q["rationale"].strip():
                errors.append(f"quality.{key}.rationale required")
            score = q.get("score")
            if data.get("numeric_requested") is False and score is not None:
                errors.append(f"quality.{key}: no score without explicit numeric request")
            if score is not None:
                if type(score) is not int or not 0 <= score <= 4:
                    errors.append(f"quality.{key}: score must be integer 0..4")
                if status in {"not_applicable","unknown"}:
                    errors.append(f"quality.{key}: status does not allow score")
            evs = q.get("evidence_ids")
            if not isinstance(evs, list):
                errors.append(f"quality.{key}.evidence_ids required list")
            else:
                for ev in evs:
                    if ev not in ids:
                        errors.append(f"quality.{key}: unknown evidence id {ev!r}")
                if status in {"strong","mixed","limited"} and data.get("coverage") == "full" and not evs:
                    errors.append(f"quality.{key}: substantive judgment needs evidence")

    lenses = data.get("lenses")
    if not isinstance(lenses, list):
        errors.append("lenses: required list")
    else:
        seen = set()
        for n, item in enumerate(lenses):
            if not isinstance(item, dict) or item.get("id") not in LENSES:
                errors.append(f"lenses[{n}]: expected L1..L8 object")
                continue
            if item["id"] in seen:
                errors.append(f"lenses[{n}]: duplicate id")
            seen.add(item["id"])
            if type(item.get("applicable")) is not bool:
                errors.append(f"lenses[{n}].applicable: bool required")
            for prop in ("reasoning","opposing_reasoning"):
                if not isinstance(item.get(prop), str) or not item[prop].strip():
                    errors.append(f"lenses[{n}].{prop} required")
        if seen != LENSES:
            errors.append("lenses: all L1..L8 must have decision")

    effects = data.get("reader_effects")
    if not isinstance(effects, list):
        errors.append("reader_effects: required list")
    else:
        for n, item in enumerate(effects):
            if not isinstance(item, dict) or item.get("kind") not in {"predicted","measured"}:
                errors.append(f"reader_effects[{n}]: invalid kind")
                continue
            if item["kind"] == "predicted" and item.get("measured_source") is not None:
                errors.append(f"reader_effects[{n}]: predicted must not claim measurement")
            if item["kind"] == "measured" and not item.get("measured_source"):
                errors.append(f"reader_effects[{n}]: measured requires source")

    revisions = data.get("revisions")
    if not isinstance(revisions, list):
        errors.append("revisions: required list")
    elif data.get("coverage") == "full":
        if len(revisions) < 3:
            errors.append("full coverage: at least 3 revision hypotheses")
        for n, item in enumerate(revisions):
            if not isinstance(item, dict) or any(not isinstance(item.get(prop), str) or not item[prop].strip()
                   for prop in ("locator","goal","proposal","preserved_strength","tradeoff","test")):
                errors.append(f"revisions[{n}]: incomplete counterfactual")

    if not isinstance(data.get("limitations"), list):
        errors.append("limitations: required list")
    return errors

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("report", type=Path)
    ap.add_argument("--manuscript", type=Path)
    args = ap.parse_args()
    try:
        obj = json.loads(args.report.read_text(encoding="utf-8"))
        manuscript = args.manuscript.read_text(encoding="utf-8") if args.manuscript else None
        errors = validate(obj, manuscript)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("INPUT ERROR:", exc, file=sys.stderr)
        return 3
    if errors:
        for error in errors:
            print("FAIL:", error)
        return 2
    print("PASS: report shape, links and available quotations validated.")
    print("NOTE: literary interpretations and manuscript coverage are NOT verified by this script.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
