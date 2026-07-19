#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path

import bluetape_coordinator as coordinator
import bluetape_runtime as runtime


EXIT_CONTRACT = 2
EXIT_RECEIPT_CORRUPT = 3
EXIT_INCOMPATIBLE_MANIFEST = 4
EXIT_COORDINATOR_CONFLICT = 5
EXIT_COMPLETION_BLOCKED = 6
EXIT_UNSUPPORTED_BY_RUN_MANIFEST = 7
MAX_INPUT_BYTES = 1024 * 1024

READ_ONLY_COMMANDS = {
    "state-root", "verify", "receipt-diagnose", "resume-check",
    "completion-check", "liveness-check",
}
PHASE1_COMMANDS = {"verify", "rebuild", "receipt-diagnose"}
SAFE_NEXT_COMMAND = {
    "state-root": "init or an explicit run command",
    "init": "run-approve",
    "verify": "rebuild or the manifest-supported inspection command",
    "rebuild": "verify",
    "receipt-diagnose": "recovery-run-create or init",
    "resume-check": "resume, replacement-repair, or replacement-block",
    "completion-check": "complete or repair the reported evidence gap",
    "run-approve": "run-start",
    "run-start": "lane-create",
    "run-recovery-start": "repair the diagnosed state",
    "run-recovery-finish": "resume normal lane work",
    "run-fail": "receipt-diagnose",
    "run-block": "receipt-diagnose",
    "run-cancel": "receipt-diagnose",
    "lane-create": "lane-start",
    "lane-start": "perform native spawn, then startup-ack",
    "startup-ack": "heartbeat or liveness-check",
    "heartbeat": "liveness-check",
    "liveness-check": "the recommended bounded lifecycle command",
    "stall-record": "probe-sent",
    "stall-clear": "heartbeat or liveness-check",
    "probe-sent": "perform the native probe, then probe-ack or interrupt-result",
    "probe-ack": "heartbeat or liveness-check",
    "interrupt-result": "lane-reassign",
    "lane-reassign": "lane-start for the replacement lane",
    "lane-complete": "check-result",
    "lane-fail": "lane-resolve or completion-check",
    "lane-block": "replacement-close or completion-check",
    "lane-cancel": "replacement-close or completion-check",
    "replacement-repair": "lane-start for the replacement lane",
    "replacement-block": "completion-check",
    "replacement-close": "completion-check",
    "lane-resolve": "completion-check",
    "resume": "resume-check",
    "recovery-run-create": "verify the new run",
    "topology-register": "check-result",
    "topology-remove": "completion-check",
    "check-result": "component-evidence",
    "component-evidence": "completion-check",
    "complete": "live-report-create after separately approved live apply",
    "handoff-create": "stop and continue in a fresh session",
    "live-report-create": "preserve the immutable report",
}


class UnsupportedByRunManifest(RuntimeError):
    pass


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


def _command_parser(commands, name):
    mode = "Read-only" if name in READ_ONLY_COMMANDS else "Mutation"
    capability = "Phase 1 and Phase 2" if name in PHASE1_COMMANDS else "Phase 2 only"
    if name in {"state-root", "init"}:
        capability = "workspace bootstrap"
    description = (
        mode + ". Capability: " + capability + ". Safe next: "
        + SAFE_NEXT_COMMAND[name] + ". In-place migration is unavailable."
    )
    return commands.add_parser(
        name,
        help=description,
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )


def _run_parser(commands, name, *, mutation=False, evidence=False):
    parser = _command_parser(commands, name)
    parser.add_argument("--run-id", required=True)
    if mutation:
        parser.add_argument("--owner-file", required=True)
        parser.add_argument("--expected-head")
    if evidence:
        parser.add_argument("--evidence", required=True)
    return parser


def _lane_parser(commands, name, *, reason=False, changed_paths=False):
    parser = _run_parser(commands, name, mutation=True, evidence=True)
    parser.add_argument("--lane-id", required=True)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--at", required=True)
    if reason:
        parser.add_argument("--reason", required=True)
    if changed_paths:
        parser.add_argument("--changed-paths", required=True)
    return parser


def build_parser():
    parser = JsonArgumentParser(
        prog="bluetape-flow.py",
        description="Guarded Bluetape receipt and coordinator command surface.",
        epilog=(
            "Required fields are shown per command. UTC timestamps end in Z. "
            "Read-only commands never mutate receipts. Phase 1 supports only "
            "verify, rebuild, and receipt-diagnose. Safe next commands appear "
            "in command help. In-place migration is unavailable."
        ),
    )
    parser.add_argument("--state-root")
    commands = parser.add_subparsers(dest="operation", required=True)

    _command_parser(commands, "state-root").add_argument("--start")
    init_parser = _command_parser(commands, "init")
    init_parser.add_argument("--workflow-type", required=True)
    init_parser.add_argument("--repo-root", required=True)
    init_parser.add_argument("--owner-file", required=True)
    init_parser.add_argument("--component", action="append", required=True)
    for name in ("verify", "rebuild", "receipt-diagnose", "resume-check", "completion-check"):
        _run_parser(commands, name)

    for name in ("run-approve", "run-start", "run-recovery-finish"):
        command = _run_parser(commands, name, mutation=True, evidence=True)
        command.add_argument("--at")
    for name in ("run-recovery-start", "run-fail", "run-block", "run-cancel"):
        command = _run_parser(commands, name, mutation=True, evidence=True)
        command.add_argument("--at")
        command.add_argument("--reason", required=True)

    for name in ("lane-create", "heartbeat", "lane-reassign", "topology-register", "check-result", "component-evidence"):
        command = _run_parser(commands, name, mutation=True, evidence=True)
        command.add_argument("--input", required=True)
    for name in ("lane-start", "startup-ack", "probe-ack"):
        _lane_parser(commands, name)
    _lane_parser(commands, "lane-complete", changed_paths=True)
    for name in ("lane-fail", "lane-block", "lane-cancel"):
        _lane_parser(commands, name, reason=True)

    stall = _lane_parser(commands, "stall-record", reason=True)
    stall.add_argument("--decision", required=True)
    _lane_parser(commands, "stall-clear", reason=True)
    probe = _lane_parser(commands, "probe-sent")
    probe.add_argument("--deadline", required=True)
    _lane_parser(commands, "interrupt-result")

    liveness = _run_parser(commands, "liveness-check")
    liveness.add_argument("--lane-id", required=True)
    liveness.add_argument("--at", required=True)
    liveness.add_argument("--command-status", choices=("alive", "dead", "unknown"), default="unknown")

    for name in ("replacement-repair", "replacement-block", "replacement-close"):
        command = _run_parser(commands, name, mutation=True, evidence=True)
        command.add_argument("--lane-id", required=True)
        command.add_argument("--replacement-lane-id", required=True)
        command.add_argument("--at", required=True)

    resolution = _run_parser(commands, "lane-resolve", mutation=True, evidence=True)
    resolution.add_argument("--lane-id", required=True)
    resolution.add_argument("--resolution-lane-id", required=True)
    resolution.add_argument("--at", required=True)

    resume = _run_parser(commands, "resume", mutation=True, evidence=True)
    resume.add_argument("--new-owner-file", required=True)
    recovery = _run_parser(commands, "recovery-run-create", evidence=True)
    recovery.add_argument("--input", required=True)
    recovery.add_argument("--owner-file", required=True)

    topology_remove = _run_parser(commands, "topology-remove", mutation=True, evidence=True)
    topology_remove.add_argument("--component-id", required=True)
    topology_remove.add_argument("--reason", required=True)
    complete = _run_parser(commands, "complete", mutation=True, evidence=True)
    complete.add_argument("--at")

    for name in ("handoff-create", "live-report-create"):
        command = _run_parser(commands, name, mutation=True)
        command.add_argument("--input", required=True)
    return parser


def _json_file(path, expected_type=None):
    target = Path(path).expanduser()
    if target.is_symlink() or not target.is_file():
        raise ValueError("JSON input must be a regular non-symlink file")
    if target.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("JSON input exceeds one MiB")
    try:
        value = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, TypeError, json.JSONDecodeError) as error:
        raise ValueError("JSON input is invalid") from error
    if expected_type is not None and not isinstance(value, expected_type):
        raise ValueError("JSON input has the wrong top-level type")
    return value


def _evidence(args):
    return _json_file(args.evidence, list)


def _require_fields(value, required, optional=()):
    required_fields = set(required)
    allowed_fields = required_fields | set(optional)
    missing = sorted(required_fields - set(value))
    unknown = sorted(set(value) - allowed_fields)
    if missing or unknown:
        raise ValueError("JSON input fields do not match the command contract")
    return value


def _head(run_dir):
    _, state = coordinator.load_coordinator_state(run_dir)
    return state


def _success(operation, state_root, **data):
    payload = {"ok": True, "operation": operation, "state_root": str(state_root)}
    payload.update(data)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


def _state_success(operation, state_root, run_id, state, **data):
    return _success(
        operation,
        state_root,
        run_id=run_id,
        sequence=state["last_sequence"],
        checksum=state["last_checksum"],
        run_state=state["run_state"],
        **data,
    )


def _failure(code, message, exit_status, **data):
    payload = {
        "ok": False,
        "error": code,
        "message": str(message)[:500],
        "retryable": exit_status in {EXIT_COORDINATOR_CONFLICT, EXIT_COMPLETION_BLOCKED},
    }
    payload.update(data)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True), file=sys.stderr)
    return exit_status


def _require_phase2(run_dir, operation):
    if operation in {"verify", "rebuild", "receipt-diagnose"}:
        return
    snapshot = runtime.load_run_manifest_snapshot(run_dir)
    version = snapshot["manifest"]["manifest_version"]
    if ".".join(version.split(".")[:2]) != "1.1":
        raise UnsupportedByRunManifest(
            "the selected run manifest does not support coordinator commands"
        )


def _transition_lane(args, run_dir, intent):
    metadata = None
    if args.operation == "lane-complete":
        changed = _json_file(args.changed_paths, list)
        if not all(isinstance(path, str) and path for path in changed):
            raise ValueError("changed paths must be non-empty strings")
        metadata = {"changed_paths": changed}
    return coordinator.transition_lane(
        run_dir,
        args.lane_id,
        args.agent_id,
        args.owner_file,
        intent,
        args.at,
        _evidence(args),
        reason=getattr(args, "reason", None),
        metadata=metadata,
    )


def _dispatch_command(args, state_root, run_dir, command):
    operation = args.operation
    evidence = _evidence(args) if hasattr(args, "evidence") else None
    now = getattr(args, "at", None) or runtime._utc_now()

    if operation == "run-approve":
        coordinator.approve_run(run_dir, args.owner_file, now, evidence)
    elif operation == "run-start":
        coordinator.start_run(run_dir, args.owner_file, now, evidence)
    elif operation == "run-recovery-start":
        coordinator.start_recovery(run_dir, args.owner_file, now, evidence, args.reason)
    elif operation == "run-recovery-finish":
        coordinator.finish_recovery(run_dir, args.owner_file, now, evidence)
    elif operation in {"run-fail", "run-block", "run-cancel"}:
        coordinator.terminate_run(run_dir, args.owner_file, operation[4:], now, evidence, args.reason)
    elif operation == "lane-create":
        value = _require_fields(
            _json_file(args.input, dict),
            {
                "lane_id", "agent_id", "assignment", "write_scope", "fallback",
                "observed_at", "startup_ack_deadline", "command_deadline",
            },
            {"parent_lane_id", "replacement_count"},
        )
        coordinator.create_lane(
            run_dir,
            value["lane_id"], value["agent_id"], args.owner_file,
            value["assignment"], value["write_scope"], value["fallback"],
            value["observed_at"], value["startup_ack_deadline"],
            value["command_deadline"], evidence,
            parent_lane_id=value.get("parent_lane_id"),
            replacement_count=value.get("replacement_count", 0),
        )
    elif operation in {"lane-start", "startup-ack", "probe-ack", "lane-complete", "lane-fail", "lane-block", "lane-cancel"}:
        intents = {
            "lane-start": "start", "startup-ack": "ack", "probe-ack": "probe_ack",
            "lane-complete": "complete", "lane-fail": "fail",
            "lane-block": "block", "lane-cancel": "cancel",
        }
        _transition_lane(args, run_dir, intents[operation])
    elif operation == "heartbeat":
        value = _require_fields(
            _json_file(args.input, dict),
            {
                "lane_id", "agent_id", "observed_at",
                "silence_lease_deadline", "reason",
            },
        )
        coordinator.record_heartbeat(
            run_dir, value["lane_id"], value["agent_id"], args.owner_file,
            value["observed_at"], value["silence_lease_deadline"], evidence,
            value["reason"],
        )
    elif operation == "stall-record":
        decision = _json_file(args.decision, dict)
        coordinator.record_stall(
            run_dir, args.lane_id, args.agent_id, args.owner_file, args.at,
            decision, evidence, args.reason,
        )
    elif operation == "stall-clear":
        coordinator.clear_stall(
            run_dir, args.lane_id, args.agent_id, args.owner_file, args.at,
            evidence, args.reason,
        )
    elif operation == "probe-sent":
        coordinator.record_probe_sent(
            run_dir, args.lane_id, args.agent_id, args.owner_file, args.at,
            args.deadline, evidence,
        )
    elif operation == "interrupt-result":
        coordinator.record_interrupt_result(
            run_dir, args.lane_id, args.agent_id, args.owner_file, args.at, evidence,
        )
    elif operation == "lane-reassign":
        value = _require_fields(
            _json_file(args.input, dict),
            {
                "lane_id", "replacement_lane_id", "replacement_agent_id",
                "decided_at", "replacement_assignment", "replacement_write_scope",
                "replacement_startup_ack_deadline", "replacement_command_deadline",
            },
        )
        coordinator.reassign_lane(
            run_dir, value["lane_id"], value["replacement_lane_id"],
            value["replacement_agent_id"], args.owner_file, value["decided_at"],
            value["replacement_assignment"], value["replacement_write_scope"],
            value["replacement_startup_ack_deadline"],
            value["replacement_command_deadline"], evidence,
        )
    elif operation == "replacement-repair":
        coordinator.repair_replacement(
            run_dir, args.lane_id, args.replacement_lane_id, args.owner_file,
            args.at, evidence,
        )
    elif operation == "replacement-block":
        coordinator.block_incomplete_replacement(
            run_dir, args.lane_id, args.replacement_lane_id, args.owner_file,
            args.at, evidence,
        )
    elif operation == "replacement-close":
        coordinator.close_replacement_lineage(
            run_dir, args.lane_id, args.replacement_lane_id, args.owner_file,
            args.at, evidence,
        )
    elif operation == "lane-resolve":
        coordinator.resolve_failed_lane(
            run_dir, args.lane_id, args.resolution_lane_id, args.owner_file,
            args.at, evidence,
        )
    elif operation == "topology-register":
        components = _json_file(args.input, list)
        coordinator.register_topology(run_dir, args.owner_file, components, evidence)
    elif operation == "topology-remove":
        coordinator.remove_topology_component(
            run_dir, args.owner_file, args.component_id, evidence, args.reason,
        )
    elif operation == "check-result":
        value = _require_fields(
            _json_file(args.input, dict),
            {"component_id", "check_id", "passed"},
            {"reason"},
        )
        coordinator.record_check_result(
            run_dir, args.owner_file, value["component_id"], value["check_id"],
            value["passed"], evidence, value.get("reason"),
        )
    elif operation == "component-evidence":
        value = _require_fields(
            _json_file(args.input, dict), {"component_id"}
        )
        coordinator.attach_component_evidence(
            run_dir, args.owner_file, value["component_id"], evidence,
        )
    elif operation == "complete":
        coordinator.complete_run(run_dir, args.owner_file, evidence)
    elif operation == "resume":
        coordinator.transfer_run_owner(
            run_dir, args.owner_file, args.new_owner_file, evidence,
        )
    elif operation in {"handoff-create", "live-report-create"}:
        result = coordinator.create_bound_report(
            run_dir,
            args.owner_file,
            "handoff" if operation == "handoff-create" else "live",
            _json_file(args.input, dict),
        )
        state = command["state"] or _head(run_dir)
        return _state_success(operation, state_root, args.run_id, state, **result)
    else:
        raise ValueError("unsupported coordinator operation")
    state = command["state"]
    if state is None:
        raise RuntimeError("mutation completed without a committed receipt state")
    extra = {}
    if operation == "resume":
        extra = {
            "owner_epoch": state["owner_epoch"],
            "owner_fingerprint": state["owner_fingerprint"],
        }
    return _state_success(operation, state_root, args.run_id, state, **extra)


def _dispatch(args, state_root, run_dir):
    with runtime.coordinator_command(args.expected_head) as command:
        return _dispatch_command(args, state_root, run_dir, command)


def run(args):
    state_root = runtime.discover_state_root(
        start=getattr(args, "start", None), state_root=args.state_root
    )
    if args.operation == "state-root":
        return _success("state-root", state_root)
    if args.operation == "init":
        initialized = runtime.initialize_run(
            state_root,
            workflow_type=args.workflow_type,
            repo_root=args.repo_root,
            component_ids=args.component,
            owner_file=args.owner_file,
        )
        return _success(
            "init", state_root, run_id=initialized["run_id"],
            sequence=initialized["event"]["sequence"],
            checksum=initialized["event"]["checksum"],
            workflow_type=initialized["workflow_type"],
            component_ids=initialized["component_ids"],
            owner_epoch=initialized["owner_epoch"],
        )
    runtime.validate_identifier(args.run_id, "run id")
    run_dir = Path(state_root) / "runs" / args.run_id
    if args.operation == "verify":
        summary = runtime.verify_receipt_summary(run_dir)
        last_event = summary["last_event"]
        return _success(
            "verify", state_root, run_id=args.run_id,
            event_count=summary["event_count"],
            sequence=last_event["sequence"], checksum=last_event["checksum"],
        )
    if args.operation == "rebuild":
        manifest = runtime.load_run_manifest_snapshot(run_dir)
        version = manifest["manifest"]["manifest_version"]
        snapshot = (
            runtime.rebuild_coordinator_snapshots(run_dir)
            if ".".join(version.split(".")[:2]) == "1.1"
            else runtime.rebuild_run_snapshot(run_dir)
        )
        return _success(
            "rebuild", state_root, run_id=args.run_id,
            sequence=snapshot["last_sequence"], checksum=snapshot["last_checksum"],
        )
    if args.operation == "receipt-diagnose":
        diagnosis = coordinator.inspect_resume(run_dir)
        if "effective_state" not in diagnosis:
            diagnosis = {
                "run_id": args.run_id,
                "effective_state": diagnosis["run_state"],
                "last_trusted_sequence": diagnosis["last_sequence"],
                "last_trusted_checksum": diagnosis["last_checksum"],
                "manifest_version": diagnosis["manifest_version"],
                "manifest_hash": diagnosis["manifest_hash"],
                "lock_owner_status": diagnosis["lock_owner_status"],
            }
        diagnosis["diagnosis_checksum"] = coordinator.diagnosis_checksum(diagnosis)
        return _success("receipt-diagnose", state_root, **diagnosis)
    _require_phase2(run_dir, args.operation)
    if args.operation == "resume-check":
        return _success("resume-check", state_root, **coordinator.inspect_resume(run_dir))
    if args.operation == "completion-check":
        manifest, state = coordinator.load_coordinator_state(run_dir)
        result = coordinator.evaluate_run_completion(state, manifest["manifest"])
        return _state_success(
            "completion-check", state_root, args.run_id, state, **result
        )
    if args.operation == "liveness-check":
        manifest, state = coordinator.load_coordinator_state(run_dir)
        lane = state["lanes"].get(args.lane_id)
        if lane is None:
            raise coordinator.CoordinatorConflict("lane does not exist")
        status = {"alive": True, "dead": False, "unknown": None}[args.command_status]
        decision = coordinator.evaluate_lane_liveness(
            lane, manifest["manifest"], args.at, command_alive=status
        )
        return _state_success(
            "liveness-check", state_root, args.run_id, state, **decision
        )
    if args.operation == "recovery-run-create":
        diagnosis = _json_file(args.input, dict)
        checksum = diagnosis.pop("diagnosis_checksum", None)
        for envelope_field in ("ok", "operation", "state_root"):
            diagnosis.pop(envelope_field, None)
        if checksum is None:
            checksum = coordinator.diagnosis_checksum(diagnosis)
        result = coordinator.create_recovery_run(
            run_dir, diagnosis, checksum, args.owner_file, _evidence(args)
        )
        return _success("recovery-run-create", state_root, **result)
    return _dispatch(args, state_root, run_dir)


def main(argv=None):
    try:
        return run(build_parser().parse_args(argv))
    except runtime.IncompatibleManifest as error:
        return _failure(error.code, error, EXIT_INCOMPATIBLE_MANIFEST, retryable=False)
    except (runtime.ReceiptCorrupt, coordinator.CoordinatorCorrupt) as error:
        return _failure(
            "receipt_corrupt",
            error,
            EXIT_RECEIPT_CORRUPT,
            retryable=False,
            next_command="receipt-diagnose",
        )
    except UnsupportedByRunManifest as error:
        return _failure(
            "unsupported_by_run_manifest", error,
            EXIT_UNSUPPORTED_BY_RUN_MANIFEST, retryable=False, next_command="init",
        )
    except coordinator.CompletionBlocked as error:
        missing = (
            error.details["missing_lanes"]
            + error.details["missing_components"]
            + error.details["failed_checks"]
            + error.details["incomplete_replacements"]
        )[:64]
        return _failure(
            "completion_blocked", error, EXIT_COMPLETION_BLOCKED,
            missing_ids=missing, next_command="completion-check",
        )
    except (coordinator.CoordinatorConflict, runtime.StateLockBusy) as error:
        return _failure(
            "coordinator_conflict", error, EXIT_COORDINATOR_CONFLICT,
            next_command="resume-check",
        )
    except (KeyError, TypeError, ValueError, OSError) as error:
        return _failure("contract_error", error, EXIT_CONTRACT, retryable=False)


if __name__ == "__main__":
    sys.exit(main())
