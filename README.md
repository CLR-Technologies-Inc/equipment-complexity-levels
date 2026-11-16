<!-- SPDX-License-Identifier: Apache-2.0 -->
# Equipment Complexity Levels

An open, machine-readable list of generic equipment classes, each rated with an **Equipment Complexity Level (ECL 1-5)**. ECL abstracts what a piece of equipment does into the tier of AI model, and the amount of human expertise, needed to reason about it.

The scale comes from [FoaMES](https://github.com/CLR-Technologies-Inc/foames). The full explanation, including how ECL maps onto existing industry classifications, is on the FoaMES wiki page [Equipment complexity levels](https://github.com/CLR-Technologies-Inc/foames/wiki/Explanation-Equipment-complexity-levels).

> **Status: initial draft.** Every entry is currently marked `reviewed_by: "ai-initial"`. The levels were drafted by an AI assistant as a starting point and have **not** been reviewed by people yet. Treat them as priors, not measured results, and please help review them (see [CONTRIBUTING](CONTRIBUTING.md)).

## The levels

| ECL | Equipment | Anchor example | Minimum model tier | Expert oversight |
| --- | --- | --- | --- | --- |
| 1 | Simple tool or apparatus | Torque wrench | Small open-weights model (Phi-class) | None |
| 2 | Single-function machine | Filler, capper, conveyor | Open weights, if they pass qualifying tasks | None |
| 3 | Configurable multi-step machine or work cell | CNC machining centre | Baseline hosted model | None |
| 4 | Coupled process equipment | Photomask (lithography plate) writer | Frontier | **Human Expert Recommended**: one expert |
| 5 | Frontier equipment | Lithography scanner | None adequate | **Expert Team Required**: a distributed team of experts |

The machine-readable form is [`data/levels.json`](data/levels.json).

## Data

One JSON file per category in [`data/equipment/`](data/equipment). Each entry:

```json
{
  "id": "torque-wrench",
  "name": "Torque wrench",
  "category": "hand-tools",
  "ecl": 1,
  "ecl_rationale": "Torque is force times lever arm; a click or reading at a set point.",
  "mappings": {"usp_1058": "B", "iec_61508": "A", "gamp5": null, "isa95": null},
  "human_expert_recommended": false,
  "expert_oversight": "none",
  "confidence": "high",
  "reviewed_by": "ai-initial"
}
```

| Field | Meaning |
| --- | --- |
| `id` | Stable kebab-case slug, unique across the list |
| `name` | Human-readable name |
| `category` | Category slug, the same as the file name |
| `ecl` | 1-5 |
| `ecl_rationale` | Why this level |
| `mappings.usp_1058` | USP <1058> group A / B / C. For non-laboratory equipment the group is applied by analogy |
| `mappings.iec_61508` | IEC 61508-2 element Type A (failure modes well defined) or B |
| `mappings.gamp5` | GAMP 5 software category 1, 3, 4 or 5, or `null` when there is no software |
| `mappings.isa95` | ISA-95 / ISA-88 equipment role: `control-module`, `equipment-module`, `work-unit`, `work-center`, or `null` for hand tools and loose apparatus |
| `human_expert_recommended` | `true` at ECL 4-5 |
| `expert_oversight` | `none` at ECL 1-3, `single` at ECL 4, `team` at ECL 5 |
| `confidence` | `low`, `medium` or `high` |
| `reviewed_by` | `ai-initial` (unreviewed) or the GitHub handle of the reviewer |

ECL measures complexity, not criticality. A pressure relief valve is ECL 1 and can still be safety-critical, so keep criticality in your own maintenance ranking.

Rate the equipment the agent will actually reason about. A CNC machine with a fixed cycle may be ECL 2, and a "simple" press with adaptive force control may be ECL 3. The entries describe typical equipment of each class.

## Validate

```bash
python tools/validate.py --stats
python -m unittest discover -s tests
```

The validator uses only the standard library. The JSON Schema in [`schema/`](schema/equipment-class.schema.json) is there for consumers who prefer schema tooling; CI runs both.

## Use it

Consume a tagged release or the raw files rather than copying them, so you pick up reviews. FoaMES plans to read this list to pre-fill the ECL field on its Machine record.

## Scope rules

- Classes of publicly available, catalogue (SKU-bound) equipment, intended for use with FoaMES. Custom or bespoke equipment built for one manufacturer is out of scope; rate it yourself from the level definitions.
- Generic, public equipment classes only. No company, site or customer names.
- No claims that a specific vendor's model is adequate for a class.

## License

- Code (`tools/`, `tests/`, `schema/`, CI): [Apache-2.0](LICENSE)
- Data (`data/`): [CC-BY-4.0](LICENSE-DATA). Credit "Equipment Complexity Levels, CLR Technologies Inc. and contributors" with a link to this repository.

See [NOTICE](NOTICE).
