# Topology Contract

Register one complete approved topology snapshot after lanes exist. Partial or
empty initial snapshots, duplicate ids, missing owner lanes, unknown
dependencies, dependency cycles, limit overflow, caller-supplied coverage, and
non-empty initial evidence are invalid. Each component record has these fields:

- `id`: stable identifier unique within the run;
- `required`: whether the component blocks run completion;
- `description`: bounded statement of the owned outcome;
- `owner_lane`: lane accountable for its evidence;
- `required_checks`: checks that must pass for the component;
- `dependencies`: component ids that must complete first;
- `evidence_refs`: bounded receipt evidence references;
- `coverage_state`: current evidence coverage.

Component removal is never implicit. Record any topology change and its reason
with `topology-remove`; silently dropping a required component or a component
that still has dependents is prohibited. Re-registration must include every
active approved component and preserves current checks, coverage, and evidence.

The completion rule is `weakest_required_component`: a run cannot be more
complete than its least-complete required component. Every required component
must have terminal lane state, required check results, and evidence before the
run can complete. `complete` atomically records main verification and
`run_completed` only after `completion-check` has no missing lane, component,
check, replacement, or main-verification proof.

A terminal `failed` lane remains immutable history. When a later correction or
rereview lane completes later with independent completion evidence,
`lane-resolve` appends a `candidate_validated` record whose
`candidate_kind=failed_lane_resolution` links the failed lane to that
successful lane. The evidence must bind the receipt digests of both terminal
lane results. `completion-check` reports `unresolved_failed_lanes` and
`resolved_failed_lanes` separately; only a replay-validated resolution to a
completed lane removes the original failure from `missing_lanes`. Failed,
blocked, cancelled, unknown, self-referential, duplicate, or liveness-only
resolution claims never satisfy completion. This semantic repair lineage is
separate from stalled-agent replacement lineage.

New manifest snapshots require the correction/rereview lane to declare the
failed lane as `parent_lane_id`. Pre-policy Phase 2 snapshots cannot add that
declaration retroactively, so their compatibility path relies on later
completion receipt sequence plus exact bindings to both terminal evidence
digests. In both
paths the owner supplies the semantic assertion; lane names are never treated
as proof.

## Resume and Recovery

Run `resume-check` before `resume`. Transfer creates a fresh contained 0600
owner handle, appends `run_resumed`, increments the epoch, and fences/removes
the old handle. Old owners and old agents cannot mutate current state. Inspect
and repair or block incomplete replacement reservations before transfer.

`receipt-diagnose` is read-only and reports the first bad sequence, trusted
prefix head, manifest identity, lock status, and damaged receipt hash. Recovery
never truncates, edits, or continues that chain. `recovery-run-create` verifies
the diagnosis checksum and approval evidence, writes an immutable 0600 copy
under `quarantine/`, and creates a distinct run with provenance in its first
event. In-place migration is unavailable.

Phase 1 snapshots support only `verify`, `rebuild`, and `receipt-diagnose`.
Healthy legacy runs must start a new Phase 2 run; damaged legacy runs use the
same diagnose/new-run rule.

## Guarded Command Contract

Every command accepts an explicit `--state-root`; when omitted, the fixed
workspace/XDG discovery contract selects it. A command other than `state-root`
or `init` requires `--run-id`. Mutation commands require `--owner-file`;
complex values use a regular non-symlink JSON file below one MiB. Timestamps
are UTC ISO-8601 values ending in `Z`. Read-only commands never write caches or
receipt.

| Command | Event or result | Allowed source | Target / next safe command |
|---|---|---|---|
| `run-approve` | `plan_approved` | planned | approved / `run-start` |
| `run-start` | `run_started` | approved | running / `lane-create` |
| `run-recovery-start` | `run_recovery_started` | running | recovering / repair |
| `run-recovery-finish` | `run_recovery_finished` | recovering | running |
| `run-fail`, `run-block`, `run-cancel` | matching terminal event | running or recovering | terminal |
| `lane-create` | `lane_created` | running or recovering | pending / `lane-start` |
| `lane-start` | `lane_started` | pending | starting / native spawn then `startup-ack` |
| `startup-ack` | `startup_ack` | starting | running |
| `heartbeat` | heartbeat and lease transaction | running | running / `liveness-check` |
| `liveness-check` | pure decision | active lane | named recommended action |
| `stall-record` | `stall_suspected` | starting or running | suspected stall / `probe-sent` |
| `stall-clear` | `lane_recovered` | suspected stall | running |
| `probe-sent` | `probe_sent` | suspected stall | recovering / native probe |
| `probe-ack` | `probe_acknowledged` | recovering | running |
| `interrupt-result` | `agent_interrupted` | recovering with authority | recovering / `lane-reassign` |
| `lane-reassign` | reassign and create transaction | interrupted recovery | old replaced, child pending |
| `lane-complete`, `lane-fail`, `lane-block`, `lane-cancel` | matching lane terminal event | manifest-approved active state | terminal |
| `replacement-repair` | repair and create transaction | incomplete reservation | child pending |
| `replacement-block` | `replacement_blocked` | incomplete reservation | original blocked |
| `replacement-close` | `replacement_lineage_closed` | replacement terminal | original same terminal |
| `lane-resolve` | `candidate_validated` failure-resolution record | failed original plus later completed correction/rereview | original history retained / `completion-check` |
| `resume-check` | read-only replay | any Phase 2 run | `resume` or repair |
| `resume` | `run_resumed` | nonterminal, complete lineage | epoch + 1 |
| `receipt-diagnose` | read-only trusted-prefix report | any snapshot | block or `recovery-run-create` |
| `recovery-run-create` | new run `run_created` | blocked diagnosis | independent planned run |
| `topology-register` | `topology_registered` | running or recovering | full active snapshot |
| `topology-remove` | `topology_component_removed` | registered leaf component | explicit removal evidence |
| `check-result` | `check_passed` or `check_failed` | registered required check | current last-write-wins result |
| `component-evidence` | `evidence_attached` | owner lane complete and checks pass | covered |
| `completion-check` | read-only weakest-component report | nonterminal | repair or `complete` |
| `complete` | main verification and completion transaction | running, all proof present | completed |
| `handoff-create` | `handoff_recorded` | running or recovering | fresh-session stop |
| `live-report-create` | `live_report_recorded` | completed | immutable live report |

The lifecycle aliases `lane-fail`, `lane-block`, and `lane-cancel` require a
reason. `lane-resolve` requires `--lane-id`, `--resolution-lane-id`, `--at`,
and non-liveness `--evidence`. `probe-ack` uses the same fixed lane transition
contract as `lane-start` and `startup-ack`. `verify` and `rebuild` are receipt
utilities, not arbitrary mutation surfaces.

The existing `candidate_validated` event type is intentionally used so frozen
Phase 2 `1.1.0` manifest snapshots can record the repair without weakening
their receipt whitelist or migrating the run in place. The owner makes the
semantic correction/rereview assertion; the coordinator enforces the snapshot's
parent policy when present, later completion, and exact receipt-evidence
bindings rather than inferring intent from lane names.

To build `lane-resolve --evidence`, compute the canonical SHA-256 digest of
each terminal lane's `evidence_refs` array and supply both digests as checksum
fields. The bundled runtime helper uses the same canonical JSON contract:

```python
from bluetape_runtime import evidence_digest

resolution_evidence = [
    {"kind": "failed-lane", "summary": "bind failed result", "checksum": evidence_digest(failed_lane["evidence_refs"])},
    {"kind": "resolution-lane", "summary": "bind successful result", "checksum": evidence_digest(resolution_lane["evidence_refs"])},
]
```

## Fixed JSON Shapes

Scalar-only commands take ids, UTC timestamps, reason, and `--evidence`.
Complex command files reject additional properties. Minimal shapes are:

```json
{"lane_id":"build","agent_id":"agent-1","assignment":"Build runtime","write_scope":[],"fallback":"main session","observed_at":"2026-07-14T01:00:00Z","startup_ack_deadline":"2026-07-14T01:00:30Z","command_deadline":"2026-07-14T01:10:00Z"}
```

```json
[{"id":"runtime","required":true,"description":"Coordinator runtime","owner_lane":"build","required_checks":["unit"],"dependencies":[],"evidence_refs":[],"coverage_state":"missing"}]
```

```json
{"component_id":"runtime","check_id":"unit","passed":true,"reason":"fresh rerun passed"}
```

```json
{"component_id":"runtime"}
```

Heartbeat input binds lane/agent, observation time, lease deadline, and reason.
Reassignment input binds old/new lane and agent, checkpoint assignment,
canonical scope, timestamps, and deadlines. Diagnosis input is the exact
`receipt-diagnose` JSON envelope. Handoff/live-report inputs use fixed hashes,
receipt head, owner epoch, affected targets, and bounded evidence; secret,
prompt, raw-output, or fencing fields are rejected. Reports are contained 0600
files whose SHA-256 and pre-event receipt head are bound in the receipt.
