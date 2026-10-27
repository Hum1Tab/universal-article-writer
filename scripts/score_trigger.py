"""Score a trigger-scope router run against evals/trigger-prompts.json.

Usage:
    python scripts/score_trigger.py decisions.json
    python scripts/score_trigger.py decisions.json evals/trigger-prompts-heldout.json

The decisions file must be JSON of the form
{"decisions": [{"id": 1, "decision": "LOAD"}, ...]}.

This is a measurement helper, not part of CI. The router is a language model;
the score is a measurement of that router on this prompt set, not a property of
the skill in general.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(path: str, suite_path: str = "evals/trigger-prompts.json") -> int:
    suite = json.loads((ROOT / suite_path).read_text(encoding="utf-8"))
    labels = {item["id"]: item["label"] for item in suite["prompts"]}

    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    decisions = {item["id"]: item["decision"].upper() for item in raw["decisions"]}

    missing = sorted(set(labels) - set(decisions))
    if missing:
        print("missing decisions for ids: {}".format(missing))
        return 2

    heavy = [i for i, label in labels.items() if label == "heavy"]
    light = [i for i, label in labels.items() if label == "light"]

    tp = sum(1 for i in heavy if decisions[i] == "LOAD")
    fn = len(heavy) - tp
    fp = sum(1 for i in light if decisions[i] == "LOAD")
    tn = len(light) - fp

    recall = tp / len(heavy) if heavy else 0.0
    specificity = tn / len(light) if light else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    accuracy = (tp + tn) / (len(heavy) + len(light))

    print("file: {}".format(path))
    print("heavy: {}  loaded={}  missed={}  recall={:.2f}".format(len(heavy), tp, fn, recall))
    print("light: {}  loaded={}  skipped={}  specificity={:.2f}".format(len(light), fp, tn, specificity))
    print("precision={:.2f}  accuracy={:.2f}".format(precision, accuracy))
    if fn:
        print("missed heavy ids: {}".format([i for i in heavy if decisions[i] != "LOAD"]))
    if fp:
        print("false-positive light ids: {}".format([i for i in light if decisions[i] == "LOAD"]))
    return 0


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(*sys.argv[1:]))
