# Semantic Ledger and Complexity Contract

Load this reference for a diagram with repeated review/recreation, a benchmark
comparison, more than one branch/loop, or long technical identifiers. The ledger
is a small renderer-neutral input contract. It prevents invented topology and
late layout surprises; it does not replace SVG/PNG geometry audits or visual
inspection.

## Required ledger shape

```json
{
  "kind": "workflow",
  "source": {
    "question": "How does repeat execution reach its final report?",
    "revision": "<repository revision>",
    "paths": ["docs/manual/en/modules/workflow.md"]
  },
  "nodes": [
    {"id": "start", "label": "Repeat flow starts", "source": "workflow.md"},
    {"id": "work", "label": "Execute work", "source": "workflow.md"}
  ],
  "edges": [
    {"id": "start-work", "from": "start", "to": "work", "kind": "flow", "source": "workflow.md"}
  ],
  "behavior": {"branches": 1, "loops": 1},
  "repairs": [
    {"target": "context", "reason": "move label outside work card", "touches": 1}
  ]
}
```

Required fields are `kind`, `source.question`, `source.revision`, one or more
`source.paths`, unique node `id`/`label`/`source`, and edge `id`/`from`/`to`/
`kind`/`source`. Keep technical identifiers intact. A long label is a layout
problem, not permission to invent an abbreviation. Use a subtitle, legend,
split view, or a larger card and record that repair.

Run the validator before authoring/rendering:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bluetape-diagram/scripts/diagram-semantic-audit.py" \
  --repo-root <repository-root> --json <diagram>.semantic.json
```

The command exits non-zero for missing source evidence, duplicate IDs, unknown
edge endpoints, malformed repair receipts, or a complexity budget overrun. A
passing ledger still needs the normal source, render, geometry, and PNG gates.

## Default complexity budgets

Budgets are a split signal, not a license to delete source-backed concepts.
Override a value only when the reader question and the evidence ledger explain
why the view remains readable.

| Kind | Nodes | Edges | Branches | Loops |
| --- | ---: | ---: | ---: | ---: |
| architecture | 16 | 20 | 4 | 2 |
| class | 14 | 24 | 4 | 2 |
| ERD | 14 | 20 | 4 | 2 |
| sequence | 10 | 18 | 3 | 2 |
| workflow | 10 | 14 | 3 | 1 |
| state | 10 | 16 | 4 | 2 |
| chart | 20 | 8 | 0 | 0 |

If a budget is exceeded, choose one of these repairs in order: remove
reader-irrelevant detail with a source note; split the view into source-
equivalent assets; move detail into a subtitle/legend; or enlarge the canvas.
Do not shrink type below the applicable kind rule and do not shorten a source
identifier only to satisfy the budget.

## Repair receipt

Every repair after the first valid ledger records `target`, `reason`, and a
positive `touches` count. Count a touch when a label, route, card/frame,
connector port, or canonical asset is changed. Keep the receipt beside the
source ledger, not inside reader-facing art. This makes repeated recreation
measurable and distinguishes a semantic repair from a purely cosmetic redraw.

## Checklist

Apply `bluetape-workflow/references/checklist-contract.md`.

- [ ] **DIA-SEM-01 — Prove source evidence**
  - **Action:** Fill the reader question, revision, paths, node sources, and edge sources before drawing.
  - **Evidence:** Passing `diagram-semantic-audit.py` report with source paths.
  - **Failure:** Stop before rendering; do not infer topology from an old raster.
- [ ] **DIA-SEM-02 — Prove closed topology**
  - **Action:** Keep IDs unique and every edge endpoint declared.
  - **Evidence:** `SEM-NODE-ID=0`, `SEM-EDGE-ENDPOINT=0`, and no invented relationships.
  - **Failure:** Repair the ledger and rerun the audit.
- [ ] **DIA-SEM-03 — Prove the complexity decision**
  - **Action:** Compare node/edge/branch/loop counts to the kind budget and record split/subtitle/legend decisions.
  - **Evidence:** Counts, budget, and documented decision.
  - **Failure:** Keep the asset in repair; never silently shorten identifiers.
- [ ] **DIA-SEM-04 — Prove repair history**
  - **Action:** Record changed target, reason, and positive touch count for every layout repair.
  - **Evidence:** Valid `repairs[]` entries and a before/after asset reference.
  - **Failure:** Do not claim reproducible improvement.
