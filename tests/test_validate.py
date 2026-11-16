# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 CLR Technologies Inc.
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import validate  # noqa: E402


def _entries(root, name="hand-tools"):
    return json.loads((root / "data" / "equipment" / f"{name}.json").read_text())


class RepoDataTest(unittest.TestCase):
    def test_repository_data_is_valid(self):
        errs, by_level, _ = validate.validate(ROOT)
        self.assertEqual(errs, [])
        self.assertEqual(sorted(by_level), [1, 2, 3, 4, 5])

    def test_anchors(self):
        anchors = {"torque-wrench": 1, "photomask-writer": 4, "lithography-scanner": 5}
        found = {}
        for f in (ROOT / "data" / "equipment").glob("*.json"):
            for e in json.loads(f.read_text())["entries"]:
                if e["id"] in anchors:
                    found[e["id"]] = e
        self.assertEqual({k: v["ecl"] for k, v in found.items()}, anchors)
        self.assertEqual(found["photomask-writer"]["expert_oversight"], "single")
        self.assertEqual(found["lithography-scanner"]["expert_oversight"], "team")

    def test_schema_file_is_json(self):
        json.loads((ROOT / "schema" / "equipment-class.schema.json").read_text())


class RuleTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(ROOT / "data", self.tmp / "data")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _write(self, doc, name="hand-tools"):
        (self.tmp / "data" / "equipment" / f"{name}.json").write_text(json.dumps(doc))

    def _mutate(self, fn):
        doc = _entries(self.tmp)
        fn(doc["entries"][0])
        self._write(doc)
        errs, _, _ = validate.validate(self.tmp)
        return errs

    def test_oversight_must_match_level(self):
        errs = self._mutate(lambda e: e.update(expert_oversight="single"))
        self.assertTrue(any("expert_oversight" in m for m in errs))

    def test_flag_must_match_level(self):
        errs = self._mutate(lambda e: e.update(human_expert_recommended=True))
        self.assertTrue(any("human_expert_recommended" in m for m in errs))

    def test_usp_group_must_fit_level(self):
        errs = self._mutate(lambda e: e["mappings"].update(usp_1058="C"))
        self.assertTrue(any("usp_1058" in m for m in errs))

    def test_unknown_field_rejected(self):
        errs = self._mutate(lambda e: e.update(vendor="x"))
        self.assertTrue(any("unknown fields" in m for m in errs))

    def test_duplicate_id_rejected(self):
        doc = _entries(self.tmp)
        other = _entries(self.tmp, "packaging")
        dup = copy.deepcopy(doc["entries"][0])
        dup["category"] = "packaging"
        other["entries"].append(dup)
        other["entries"].sort(key=lambda e: e["id"])
        self._write(other, "packaging")
        errs, _, _ = validate.validate(self.tmp)
        self.assertTrue(any("duplicate id" in m for m in errs))


if __name__ == "__main__":
    unittest.main()
