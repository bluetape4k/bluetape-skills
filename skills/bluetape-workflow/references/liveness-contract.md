# Liveness Contract

In Codex App and plain Codex sessions without an independent wall-clock
supervisor, never call blocking `wait_agent`. Use non-blocking `list_agents` at
useful checkpoints while the main session continues productive work. Native
delegation must not become the user-visible critical path. Treat 90 seconds
without fresh material evidence as a stall, call `interrupt_agent`, and reclaim
the lane. Review-only agents have a five-minute total deadline; implementation
agents have a 15-minute total deadline.

Only an attached tmux/OMX session or another OS-timeboxed process may enable
blocking native waits. `CODEX_SUBAGENT_WATCHDOG_SUPERVISED=1` is reserved for a
launcher that actually supplies independent wall-clock supervision. In that
lane, observe active native sub-agents every 30 seconds. Silence becomes a
suspected stall after 120 seconds unless the lane holds a renewable silence
lease. One lease may cover at most 600 seconds and every renewal must carry
fresh bounded evidence and a reason. The 600-second value caps one lease, not
useful work.

After suspected stall, allow a 60-second probe grace period. A lane may be
replaced at most once, and replacement requires the prior writer to be
interrupted or confirmed terminal plus recorded lineage. If safe recovery is
not available, the main session owns the fallback and preserves the last known
evidence.

In an externally supervised lane, every native `wait_agent` call is bounded to
30-60 seconds. Five consecutive minutes of timed-out waits without mailbox
activity force `interrupt_agent` and main-session takeover. A native delegation
has an absolute 15-minute deadline even when heartbeat traffic continues;
long-running tests or CI must run as separately polled processes with fresh
execution evidence. The managed watchdog hook denies unsupervised waits and,
when supervised, enforces these ceilings and denies further waits after either
deadline.

A heartbeat proves only liveness. It is never progress, changed-path, check,
component, main-verification, or completion evidence.

## Main-Session Sequence

1. Record `lane-create` and `lane-start` before the main session calls a native
   spawn or send tool.
2. Record `startup-ack` only from the observed native result. Silence is not an
   ACK.
3. Use `liveness-check` as a pure recommendation. Record fresh heartbeat/lease
   evidence or `stall-record`; do not infer native execution from helper output.
4. Record `probe-sent` before the main session calls `send_message` or
   `list_agents`. Re-read the observed response.
5. Interrupt only after policy returns interrupt authority. The main session
   calls `interrupt_agent`, then records its bounded result with
   `interrupt-result`.
6. A replacement uses a distinct lane and agent, a canonical equal-or-narrower
   scope, one checkpoint, and explicit parent lineage. Late old-agent results
   are fenced.
7. Before `lane-complete`, the main session rereads evidence, collects NUL-safe
   Git status plus branch-diff changed paths, resolves them against pinned
   `repo_root`, rejects symlink/alias escape, and proves every path is within
   scope. Empty scope means no writes.
8. Record `lane-complete`, then check and component evidence. Run
   `completion-check` before `complete`.

Python never invokes native collaboration tools. It records intent before and
bounded observed evidence after each main-session action. Owner credentials
remain only in contained 0600 owner files and never appear in argv or JSON.
