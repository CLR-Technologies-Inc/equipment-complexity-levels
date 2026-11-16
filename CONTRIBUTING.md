<!-- SPDX-License-Identifier: Apache-2.0 -->
# Contributing

Thank you for helping rate equipment. The list is only useful if people who know the equipment check it.

## Review an entry

Most entries start as `reviewed_by: "ai-initial"`. To review one:

1. Read the `ecl_rationale` and the mappings against the level definitions in the [README](README.md) and [`data/levels.json`](data/levels.json).
2. If you agree, set `reviewed_by` to your GitHub handle and adjust `confidence`.
3. If you disagree, change `ecl` (and `expert_oversight` and `human_expert_recommended` to match), rewrite the rationale, and say in the pull request why.

One pull request may review many entries. Please only mark entries you actually know.

## Add an equipment class

- Use a generic, public class name, such as "Rotary tablet press", not a product or vendor name.
- Pick the category file it belongs to, or add a new `data/equipment/<category>.json` with `"category"` equal to the file name.
- Keep entries sorted by `id`. Ids are unique across all files.
- New AI-drafted entries must say `reviewed_by: "ai-initial"`.

## Rules the validator enforces

- `expert_oversight` is `none` at ECL 1-3, `single` at ECL 4 and `team` at ECL 5.
- `human_expert_recommended` is `true` exactly at ECL 4 and 5.
- `usp_1058` and `iec_61508` must be allowed at the entry's level (see `data/levels.json`).
- Every entry has a rationale of at least a sentence.

Run the checks before you open a pull request:

```bash
python tools/validate.py --stats
python -m unittest discover -s tests
```

## What not to include

- Names of companies, sites, customers or tenants.
- Confidential process details. Rate the class from public knowledge.
- Claims that a particular vendor's AI model is adequate for a class.

## Licensing of contributions

By contributing you agree that code is licensed under Apache-2.0 and data under CC-BY-4.0, as described in [NOTICE](NOTICE).
