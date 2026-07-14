# Liveness Contract

Observe active native sub-agents every 30 seconds. Silence becomes a suspected
stall after 120 seconds unless the lane holds a renewable silence lease. One
lease may cover at most 600 seconds and every renewal must carry fresh bounded
evidence and a reason. The 600-second value caps one lease, not useful work.

After suspected stall, allow a 60-second probe grace period. A lane may be
replaced at most once, and replacement requires the prior writer to be
interrupted or confirmed terminal plus recorded lineage. If safe recovery is
not available, the main session owns the fallback and preserves the last known
evidence.

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
