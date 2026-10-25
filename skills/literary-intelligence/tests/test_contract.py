#!/usr/bin/env python3
"""Behavioral invariants for the report validator; no claim to test literary quality."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("literary_validator", ROOT / "scripts" / "validate_report.py")
module = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(module)

class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample = json.loads((ROOT / "examples" / "sample-report.json").read_text(encoding="utf-8"))
        cls.manuscript = (ROOT / "examples" / "manuscript.txt").read_text(encoding="utf-8")

    def test_sample_valid(self):
        self.assertEqual(module.validate(self.sample, self.manuscript), [])

    def test_quote_hallucination_caught(self):
        doc = copy.deepcopy(self.sample)
        doc["evidence"][0]["quote"] = "この台詞は原稿に存在しない"
        self.assertTrue(any("not found in manuscript" in error for error in module.validate(doc, self.manuscript)))

    def test_universal_score_disallowed(self):
        doc = copy.deepcopy(self.sample)
        doc["universal_score"] = 92
        self.assertTrue(any("universal_score" in error for error in module.validate(doc, self.manuscript)))

    def test_numeric_score_requires_user_choice(self):
        doc = copy.deepcopy(self.sample)
        doc["quality"]["Q1"]["score"] = 3
        self.assertTrue(any("no score" in error for error in module.validate(doc, self.manuscript)))

    def test_missing_evidence_id_rejected(self):
        doc = copy.deepcopy(self.sample)
        doc["claims"][0]["evidence_ids"] = ["E-NOT-PRESENT"]
        self.assertTrue(any("unknown evidence id" in error for error in module.validate(doc, self.manuscript)))

    def test_reader_prediction_not_misreported_as_measured(self):
        doc = copy.deepcopy(self.sample)
        doc["reader_effects"][0]["measured_source"] = "fictional study"
        self.assertTrue(any("predicted must not claim measurement" in error for error in module.validate(doc, self.manuscript)))

    def test_missing_lens_rejected(self):
        doc = copy.deepcopy(self.sample)
        doc["lenses"] = doc["lenses"][:-1]
        self.assertTrue(any("all L1..L8" in error for error in module.validate(doc, self.manuscript)))

    def test_numeric_anchors_in_range(self):
        doc = copy.deepcopy(self.sample)
        doc["numeric_requested"] = True
        doc["quality"]["Q1"]["score"] = 7
        self.assertTrue(any("score must be integer 0..4" in error for error in module.validate(doc, self.manuscript)))

if __name__ == "__main__":
    unittest.main()
