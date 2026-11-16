#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 CLR Technologies Inc.
"""Validate the Equipment Complexity Level list.

Standard library only, so it runs anywhere Python 3.10+ does:

    python tools/validate.py            # validate data/
    python tools/validate.py --stats    # also print counts per level

Checks every category file in data/equipment/ against the rules in
schema/equipment-class.schema.json and data/levels.json, plus rules a
JSON Schema cannot express (unique ids, file name matches category).
Exits non-zero on any error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ENTRY_KEYS = {"id", "name", "category", "ecl", "ecl_rationale", "mappings",
              "human_expert_recommended", "expert_oversight", "confidence", "reviewed_by"}
MAPPING_KEYS = {"usp_1058", "iec_61508", "gamp5", "isa95"}
ISA95 = {None, "control-module", "equipment-module", "work-unit", "work-center"}
GAMP5 = {None, 1, 3, 4, 5}
CONFIDENCE = {"low", "medium", "high"}
OVERSIGHT = {1: "none", 2: "none", 3: "none", 4: "single", 5: "team"}


def load_levels(root: Path) -> dict[int, dict]:
    data = json.loads((root / "data" / "levels.json").read_text(encoding="utf-8"))
    return {lv["ecl"]: lv for lv in data["levels"]}


def check_entry(e: dict, where: str, levels: dict[int, dict], category: str) -> list[str]:
    errs: list[str] = []
    if not isinstance(e, dict):
        return [f"{where}: entry is not an object"]
    missing = ENTRY_KEYS - e.keys()
    extra = e.keys() - ENTRY_KEYS
    if missing:
        errs.append(f"{where}: missing fields {sorted(missing)}")
    if extra:
        errs.append(f"{where}: unknown fields {sorted(extra)}")
    if missing:
        return errs

    if not isinstance(e["id"], str) or not SLUG.match(e["id"]):
        errs.append(f"{where}: id must be a lowercase kebab-case slug")
    if not isinstance(e["name"], str) or len(e["name"].strip()) < 2:
        errs.append(f"{where}: name is required")
    if e["category"] != category:
        errs.append(f"{where}: category {e['category']!r} does not match file category {category!r}")
    ecl = e["ecl"]
    if not isinstance(ecl, int) or isinstance(ecl, bool) or ecl not in levels:
        errs.append(f"{where}: ecl must be an integer 1-5")
        return errs
    if not isinstance(e["ecl_rationale"], str) or len(e["ecl_rationale"].strip()) < 10:
        errs.append(f"{where}: ecl_rationale must explain the level (10+ characters)")

    lv = levels[ecl]
    m = e["mappings"]
    if not isinstance(m, dict) or set(m) != MAPPING_KEYS:
        errs.append(f"{where}: mappings must have exactly {sorted(MAPPING_KEYS)}")
    else:
        if m["usp_1058"] not in lv["usp_1058"]:
            errs.append(f"{where}: usp_1058 {m['usp_1058']!r} not allowed at ECL {ecl} (allowed {lv['usp_1058']})")
        if m["iec_61508"] not in lv["iec_61508"]:
            errs.append(f"{where}: iec_61508 {m['iec_61508']!r} not allowed at ECL {ecl} (allowed {lv['iec_61508']})")
        if m["gamp5"] not in GAMP5 or isinstance(m["gamp5"], bool):
            errs.append(f"{where}: gamp5 must be null, 1, 3, 4 or 5")
        if m["isa95"] not in ISA95:
            errs.append(f"{where}: isa95 must be one of {sorted(x for x in ISA95 if x)} or null")

    want = OVERSIGHT[ecl]
    if e["expert_oversight"] != want:
        errs.append(f"{where}: expert_oversight must be {want!r} at ECL {ecl}")
    if e["human_expert_recommended"] is not (ecl >= 4):
        errs.append(f"{where}: human_expert_recommended must be {ecl >= 4} at ECL {ecl}")
    if e["confidence"] not in CONFIDENCE:
        errs.append(f"{where}: confidence must be low, medium or high")
    if not isinstance(e["reviewed_by"], str) or len(e["reviewed_by"].strip()) < 2:
        errs.append(f"{where}: reviewed_by must be 'ai-initial' or a reviewer handle")
    return errs


def validate(root: Path = ROOT) -> tuple[list[str], Counter, Counter]:
    errs: list[str] = []
    by_level: Counter = Counter()
    by_review: Counter = Counter()
    levels = load_levels(root)
    if sorted(levels) != [1, 2, 3, 4, 5]:
        errs.append("data/levels.json must define ECL 1 to 5")
        return errs, by_level, by_review
    seen: dict[str, str] = {}
    files = sorted((root / "data" / "equipment").glob("*.json"))
    if not files:
        errs.append("no category files in data/equipment/")
    for f in files:
        rel = f.relative_to(root)
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errs.append(f"{rel}: invalid JSON ({exc})")
            continue
        category = doc.get("category")
        if category != f.stem:
            errs.append(f"{rel}: category {category!r} must match the file name {f.stem!r}")
        entries = doc.get("entries")
        if not isinstance(entries, list) or not entries:
            errs.append(f"{rel}: entries must be a non-empty list")
            continue
        ids = [e.get("id") for e in entries if isinstance(e, dict)]
        if ids != sorted(ids):
            errs.append(f"{rel}: entries must be sorted by id")
        for i, e in enumerate(entries):
            where = f"{rel}[{i}]" + (f" {e.get('id')}" if isinstance(e, dict) else "")
            errs.extend(check_entry(e, where, levels, f.stem))
            if isinstance(e, dict) and isinstance(e.get("id"), str):
                if e["id"] in seen:
                    errs.append(f"{where}: duplicate id, also in {seen[e['id']]}")
                seen[e["id"]] = str(rel)
                if isinstance(e.get("ecl"), int):
                    by_level[e["ecl"]] += 1
                by_review["ai-initial" if e.get("reviewed_by") == "ai-initial" else "reviewed"] += 1
    return errs, by_level, by_review


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--stats", action="store_true", help="print counts per level")
    args = ap.parse_args(argv)
    errs, by_level, by_review = validate(args.root)
    for msg in errs:
        print(f"error: {msg}", file=sys.stderr)
    if args.stats or not errs:
        total = sum(by_level.values())
        print(f"{total} equipment classes; " +
              ", ".join(f"ECL {k}: {by_level[k]}" for k in sorted(by_level)) +
              f"; {by_review['reviewed']} reviewed, {by_review['ai-initial']} ai-initial")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
