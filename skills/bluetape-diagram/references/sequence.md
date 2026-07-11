# Sequence Diagram Rules

Use with `common.md` for sequence, request/response, retry, branch, lifecycle,
lock, contention, and time-ordered diagrams.

## Reference Baseline

- Start from the current local best-practices sequence family.
- Open at least two full-size rendered reference PNGs before editing:
  - one best-practices catalog sequence
  - one approved repo-local sequence from the current or nearest module family
- Record both reference paths in the evidence ledger.
- If the user names a current reference, use that one as authoritative for the
  repo/chapter until a newer local lesson says otherwise.

## Required Visual Signals

- handwritten title
- participant headers with role/subtitle text when needed
- vertical lifelines
- activation bars
- horizontal message lanes
- visible numbered pill labels in execution order
- subdued `alt`/`else`/`loop` chronological frames
- branch-specific call/return colors
- solid fixed-size arrowheads whose color matches the line
- enough row height so labels do not cover lines

Reject generic flowchart cards, lifeline-only diagrams, hidden validator labels,
or stale palettes that do not match the opened references.

## Palette and Markers

- Use the muted bluetape4k sequence palette from the opened references.
- Normal calls should read as muted blue, success/state as olive green,
  external/metadata/cleanup as brown or amber, returns as teal, and errors as
  muted red.
- Avoid saturated default Tailwind/brand blue, purple, neon green, or vivid
  orange unless the opened reference uses that tone for the same semantic role.
- Message line, marker arrowhead, label border/text, and number badge stroke
  must belong to the same muted semantic color family.
- Define explicit per-color markers; do not reuse a blue marker for green,
  amber, red, purple, or return paths.

## Labels and Rows

- Every message/call/return label must be visible and numbered (`1`, `2`, `3`,
  ...), not hidden, off-canvas, one-pixel, transparent, or audit-only.
- Label pills sit above their own message line, normally with a `6-12px` gap.
- The call line must remain visibly continuous before and after the label.
- If labels overlap lines, `alt` text, borders, lifelines, or each other,
  increase row height and overall SVG/viewBox height.
- Do not solve cramped rows by shrinking text or hiding labels.

## Branch Frames

- `alt`/`else`/`loop` regions are chronological frames, not detached notes.
- Frame bodies are transparent (`fill="none"` or effective `fill-opacity:0`).
- Branch headers sit on or inside the frame.
- Branch content stays inside the frame with padding.
- Use divider lines for multiple branches.
- Branch calls use branch-specific colors that differ from the surrounding
  happy path.
- Footer/note boxes stay outside branch frames with clear whitespace.

## Evidence

Run the sequence style audit when available:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bluetape-diagram/scripts/diagram-sequence-style-audit.py" <diagram>.svg
```

Record:

- reference PNG paths
- palette parity result
- numbered visible label count
- label-over-line visual result
- branch frame transparency/result
- marker color parity result
- PNG full-size inspection result

## Blocking Sequence Checklist

- [ ] **DIA-SEQ-01 — Open two authoritative references**
  - **Action:** Inspect one best-practices and one nearest approved repo-local full-size sequence PNG.
  - **Evidence:** Both reference paths and chosen authority.
  - **Failure:** Do not design from a stale palette or generic flowchart convention.
- [ ] **DIA-SEQ-02 — Preserve sequence visual signals**
  - **Action:** Include participants, lifelines, activations, message lanes, visible numbered labels, chronological frames, role colors, and row height.
  - **Evidence:** Element counts and full-size PNG review.
  - **Failure:** Flowchart cards, hidden labels, missing activations, or cramped rows block PASS.
- [ ] **DIA-SEQ-03 — Verify palette and marker parity**
  - **Action:** Match muted semantic colors across line, arrowhead, label, and badge with explicit per-color markers.
  - **Evidence:** Palette comparison and marker color/size audit.
  - **Failure:** Saturated drift or reused mismatched markers require repair.
- [ ] **DIA-SEQ-04 — Verify every numbered message row**
  - **Action:** Keep labels visible above their own continuous line with sufficient gap and no overlap.
  - **Evidence:** Numbered label count, order, and label-over-line visual result.
  - **Failure:** Increase row/viewBox height; never hide or shrink labels to pass.
- [ ] **DIA-SEQ-05 — Verify branch frames**
  - **Action:** Keep alt/else/loop frames chronological, transparent, padded, divided, semantically colored, and clear of footer notes.
  - **Evidence:** Frame transparency/content/layout inspection.
  - **Failure:** Detached notes, opaque frames, or content outside frames block PASS.
- [ ] **DIA-SEQ-06 — Run sequence-specific proof**
  - **Action:** Run the sequence style audit and reconcile it with full-size PNG inspection.
  - **Evidence:** Audit counts/results plus reference, palette, labels, frames, markers, and PNG ledger rows.
  - **Failure:** PNG contradiction or weak/missing audit evidence returns to editing.
