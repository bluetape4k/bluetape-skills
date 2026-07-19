import copy
import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path


class CoordinatorCorrupt(RuntimeError):
    """Raised when receipt replay violates coordinator invariants."""

    def __init__(self, message, first_bad_sequence=None):
        super().__init__(message)
        self.first_bad_sequence = first_bad_sequence


class CoordinatorConflict(RuntimeError):
    """Raised when a coordinator command observes stale state."""


class CompletionBlocked(RuntimeError):
    def __init__(self, details):
        super().__init__("required workflow completion evidence is missing")
        self.details = details


TERMINAL_LANE_STATES = {"completed", "failed", "blocked", "cancelled"}
TERMINAL_RUN_STATES = {"completed", "failed", "blocked", "cancelled"}
LIVENESS_EVENT_TYPES = {
    "heartbeat_observed",
    "lease_renewed",
    "stall_suspected",
    "lane_recovered",
    "probe_sent",
    "probe_acknowledged",
    "agent_interrupted",
}
LIVENESS_ACTIONS = {
    "continue",
    "suspect_stall",
    "observe_command",
    "send_probe",
    "await_probe",
    "interrupt",
    "main_takeover",
    "none",
}

RUN_INTENT_TRANSITIONS = {
    "approve": ("plan_approved", {"planned"}, "approved"),
    "start": ("run_started", {"approved"}, "running"),
    "recovery_start": ("run_recovery_started", {"running"}, "recovering"),
    "recovery_finish": ("run_recovery_finished", {"recovering"}, "running"),
    "fail": ("run_failed", {"running", "recovering"}, "failed"),
    "block": ("run_blocked", {"running", "recovering"}, "blocked"),
    "cancel": (
        "run_cancelled",
        {"planned", "approved", "running", "recovering"},
        "cancelled",
    ),
}

LANE_INTENT_TRANSITIONS = {
    "start": ("lane_started", {"pending"}, "starting"),
    "ack": ("startup_ack", {"starting"}, "running"),
    "stall": (
        "stall_suspected",
        {"starting", "running"},
        "suspected_stall",
    ),
    "clear_stall": ("lane_recovered", {"suspected_stall"}, "running"),
    "probe": ("probe_sent", {"suspected_stall"}, "recovering"),
    "probe_ack": ("probe_acknowledged", {"recovering"}, "running"),
    "interrupt": ("agent_interrupted", {"recovering"}, "recovering"),
    "complete": ("lane_completed", {"running"}, "completed"),
    "fail": (
        "lane_failed",
        {"starting", "running", "suspected_stall", "recovering"},
        "failed",
    ),
    "block": (
        "lane_blocked",
        {"starting", "running", "suspected_stall", "recovering"},
        "blocked",
    ),
    "cancel": (
        "lane_cancelled",
        {"pending", "starting", "running", "suspected_stall", "recovering"},
        "cancelled",
    ),
}

RUN_EVENT_TRANSITIONS = {
    "run_created": ({None, "planned"}, "planned"),
    "plan_approved": ({"planned"}, "approved"),
    "run_started": ({"approved"}, "running"),
    "run_recovery_started": ({"running"}, "recovering"),
    "run_recovery_finished": ({"recovering"}, "running"),
    "run_failed": ({"running", "recovering"}, "failed"),
    "run_blocked": ({"running", "recovering"}, "blocked"),
    "run_cancelled": ({"planned", "approved", "running", "recovering"}, "cancelled"),
    "run_completed": ({"running"}, "completed"),
}

LANE_EVENT_TRANSITIONS = {
    "lane_started": ({"pending"}, "starting"),
    "startup_ack": ({"starting"}, "running"),
    "heartbeat_observed": ({"running"}, "running"),
    "lease_renewed": ({"running"}, "running"),
    "stall_suspected": ({"starting", "running"}, "suspected_stall"),
    "stall_cleared": ({"suspected_stall"}, "running"),
    "lane_recovered": ({"suspected_stall", "recovering"}, "running"),
    "probe_sent": ({"suspected_stall"}, "recovering"),
    "probe_acknowledged": ({"recovering"}, "running"),
    "agent_interrupted": ({"recovering"}, "recovering"),
    "lane_reassigned": ({"recovering"}, "replaced"),
    "lane_completed": ({"running", "replaced"}, "completed"),
    "lane_failed": ({"starting", "running", "suspected_stall", "recovering", "replaced"}, "failed"),
    "lane_blocked": ({"starting", "running", "suspected_stall", "recovering", "replaced"}, "blocked"),
    "lane_cancelled": ({"pending", "starting", "running", "suspected_stall", "recovering", "replaced"}, "cancelled"),
}


def empty_coordinator_state(run_metadata):
    if not isinstance(run_metadata, dict):
        raise CoordinatorCorrupt("run metadata is missing")
    fingerprint = run_metadata.get("owner_fingerprint")
    epoch = run_metadata.get("initial_owner_epoch", run_metadata.get("owner_epoch"))
    if fingerprint is None and isinstance(run_metadata.get("owner_token"), str):
        fingerprint = hashlib.sha256(
            run_metadata["owner_token"].encode("utf-8")
        ).hexdigest()
        epoch = 0
    if not isinstance(fingerprint, str) or not isinstance(epoch, int):
        raise CoordinatorCorrupt("run owner metadata is invalid")
    return {
        "run_state": "planned",
        "owner_epoch": epoch,
        "owner_fingerprint": fingerprint,
        "lanes": {},
        "topology": {},
        "removed_components": [],
        "removed_component_records": {},
        "approved_component_ids": sorted(run_metadata.get("component_ids", [])),
        "checks": {},
        "check_history": {},
        "reports": {},
        "main_verified": False,
        "incomplete_replacements": [],
        "failure_resolutions": {},
        "last_sequence": 0,
        "last_checksum": "",
        "last_event_type": None,
        "updated_at": None,
        "_receipt_owner_value": run_metadata.get("owner_token", fingerprint),
    }


def _corrupt(sequence, message):
    raise CoordinatorCorrupt(
        "coordinator corruption at sequence " + str(sequence) + ": " + message,
        first_bad_sequence=sequence,
    )


def _require_evidence(event, sequence):
    if event["event_type"] != "run_created" and not event.get("evidence_refs"):
        _corrupt(sequence, "event evidence is missing")


def _apply_run_event(state, event, sequence):
    event_type = event["event_type"]
    allowed, target = RUN_EVENT_TRANSITIONS[event_type]
    source = state["run_state"]
    if event_type == "run_created" and state["last_sequence"] == 0:
        source = None
    if source not in allowed:
        _corrupt(sequence, "run transition source is invalid")
    if event.get("to_state") not in {None, target}:
        _corrupt(sequence, "run transition target is invalid")
    if event.get("from_state") not in {None, source}:
        _corrupt(sequence, "run transition from_state is invalid")
    state["run_state"] = target


def _new_lane(event, sequence):
    lane_id = event.get("lane_id")
    agent_id = event.get("agent_id")
    if lane_id is None or agent_id is None:
        _corrupt(sequence, "lane_created requires lane_id and agent_id")
    metadata = event.get("metadata") or {}
    return {
        "id": lane_id,
        "state": "pending",
        "agent_id": agent_id,
        "assignment": metadata.get("assignment"),
        "write_scope": list(metadata.get("write_scope", [])),
        "changed_paths": [],
        "fallback": metadata.get("fallback"),
        "startup_ack_deadline": metadata.get("startup_ack_deadline"),
        "silence_lease_deadline": metadata.get("silence_lease_deadline"),
        "command_deadline": metadata.get("command_deadline"),
        "probe_deadline": metadata.get("probe_deadline"),
        "evidence_digest": metadata.get("evidence_digest"),
        "parent_lane_id": metadata.get("parent_lane_id"),
        "replacement_count": metadata.get("replacement_count", 0),
        "replacement_lane_id": metadata.get("replacement_lane_id"),
        "last_evidence_digest": metadata.get("evidence_digest"),
        "last_reason": event.get("reason"),
        "liveness_evidence_refs": [],
        "liveness_evidence_digests": [],
        "last_event_type": event["event_type"],
        "terminal_sequence": None,
        "updated_at": event["timestamp"],
        "evidence_refs": list(event.get("evidence_refs", [])),
    }


def _apply_lane_event(state, event, sequence):
    event_type = event["event_type"]
    lane_id = event.get("lane_id")
    if lane_id is None:
        _corrupt(sequence, event_type + " requires lane_id")
    if event_type == "lane_created":
        if state["run_state"] not in {"running", "recovering"}:
            _corrupt(sequence, "lane cannot be created in current run state")
        if lane_id in state["lanes"]:
            _corrupt(sequence, "duplicate lane_created")
        state["lanes"][lane_id] = _new_lane(event, sequence)
        return
    lane = state["lanes"].get(lane_id)
    if lane is None:
        _corrupt(sequence, "lane event references an unknown lane")
    if event.get("agent_id") is not None and event["agent_id"] != lane["agent_id"]:
        _corrupt(sequence, "lane event agent does not own the lane")
    allowed, target = LANE_EVENT_TRANSITIONS[event_type]
    if lane["state"] not in allowed:
        _corrupt(sequence, "lane transition source is invalid")
    if event.get("from_state") not in {None, lane["state"]}:
        _corrupt(sequence, "lane transition from_state is invalid")
    if event.get("to_state") not in {None, target}:
        _corrupt(sequence, "lane transition target is invalid")
    lane["state"] = target
    lane["last_event_type"] = event_type
    lane["updated_at"] = event["timestamp"]
    if target in TERMINAL_LANE_STATES:
        lane["terminal_sequence"] = sequence
    metadata = event.get("metadata") or {}
    if event.get("evidence_refs"):
        evidence = list(event["evidence_refs"])
        if event_type in LIVENESS_EVENT_TYPES:
            lane["liveness_evidence_refs"] = evidence
            digest = _runtime().evidence_digest(evidence)
            digest_history = lane.setdefault("liveness_evidence_digests", [])
            if digest not in digest_history:
                digest_history.append(digest)
            if "evidence_digest" not in metadata:
                encoded = json.dumps(
                    evidence,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
                lane["last_evidence_digest"] = hashlib.sha256(encoded).hexdigest()
        else:
            lane["evidence_refs"] = evidence
    for field in (
        "silence_lease_deadline",
        "probe_deadline",
        "evidence_digest",
        "replacement_count",
        "replacement_lane_id",
    ):
        if field in metadata:
            lane[field] = metadata[field]
    if "evidence_digest" in metadata:
        lane["last_evidence_digest"] = metadata["evidence_digest"]
    if event_type == "lane_completed":
        lane["changed_paths"] = list(metadata.get("changed_paths", []))
    reservation_fields = {
        "replacement_lane_id",
        "replacement_agent_id",
        "replacement_assignment",
        "replacement_write_scope",
        "replacement_fallback",
        "replacement_startup_ack_deadline",
        "replacement_command_deadline",
        "replacement_count",
        "checkpoint_digest",
    }
    if event_type == "lane_reassigned" and reservation_fields <= set(metadata):
        lane["replacement_reservation"] = {
            field: copy.deepcopy(metadata[field]) for field in reservation_fields
        }
    if event.get("reason") is not None:
        lane["last_reason"] = event["reason"]


def _apply_logical_event(state, event, manifest, sequence):
    event_type = event.get("event_type")
    if event_type in RUN_EVENT_TRANSITIONS:
        _require_evidence(event, sequence)
        _apply_run_event(state, event, sequence)
    elif event_type == "run_resumed":
        metadata = event.get("metadata") or {}
        state["owner_epoch"] += 1
        if metadata.get("owner_epoch") != state["owner_epoch"] - 1:
            _corrupt(sequence, "resume old owner epoch is invalid")
        new_fingerprint = metadata.get("new_owner_fingerprint")
        if (
            not isinstance(new_fingerprint, str)
            or len(new_fingerprint) != 64
            or any(character not in "0123456789abcdef" for character in new_fingerprint)
        ):
            _corrupt(sequence, "resume owner fingerprint is invalid")
        state["owner_fingerprint"] = new_fingerprint
    elif event_type == "lane_created" or event_type in LANE_EVENT_TRANSITIONS:
        _require_evidence(event, sequence)
        if (
            event_type == "lane_created"
            and len(state["lanes"])
            >= manifest.get("resource_limits", {}).get("max_lanes", 64)
        ):
            _corrupt(sequence, "lane limit exceeded")
        _apply_lane_event(state, event, sequence)
    elif event_type == "replacement_repaired":
        metadata = event.get("metadata") or {}
        original_id = metadata.get("original_lane_id")
        replacement_id = metadata.get("replacement_lane_id")
        original = state["lanes"].get(original_id)
        if original is None or original["state"] != "replaced":
            _corrupt(sequence, "replacement repair original lane is invalid")
        if (
            event.get("lane_id") != original_id
            or event.get("agent_id") != original["agent_id"]
            or event.get("from_state") != "replaced"
            or event.get("to_state") != "replaced"
            or original.get("replacement_lane_id") != replacement_id
            or replacement_id in state["lanes"]
        ):
            _corrupt(sequence, "replacement repair identity is invalid")
        original["replacement_lane_id"] = replacement_id
        original["last_event_type"] = event_type
        original["updated_at"] = event.get("timestamp")
        original["evidence_refs"] = list(event.get("evidence_refs", []))
    elif event_type == "replacement_blocked":
        metadata = event.get("metadata") or {}
        original_id = metadata.get("original_lane_id")
        replacement_id = metadata.get("replacement_lane_id")
        original = state["lanes"].get(original_id)
        if original is None or original["state"] != "replaced":
            _corrupt(sequence, "replacement block original lane is invalid")
        if (
            event.get("lane_id") != original_id
            or event.get("agent_id") != original["agent_id"]
            or event.get("from_state") != "replaced"
            or event.get("to_state") != "blocked"
            or original.get("replacement_lane_id") != replacement_id
            or replacement_id in state["lanes"]
        ):
            _corrupt(sequence, "replacement block identity is invalid")
        original["state"] = "blocked"
        original["terminal_sequence"] = sequence
        original["last_event_type"] = event_type
        original["updated_at"] = event.get("timestamp")
        original["evidence_refs"] = list(event.get("evidence_refs", []))
    elif event_type == "replacement_lineage_closed":
        metadata = event.get("metadata") or {}
        original_id = metadata.get("original_lane_id")
        replacement_id = metadata.get("replacement_lane_id")
        terminal_state = metadata.get("replacement_terminal_state")
        original = state["lanes"].get(original_id)
        replacement = state["lanes"].get(replacement_id)
        if original is None or original["state"] != "replaced":
            _corrupt(sequence, "replacement close original lane is invalid")
        if (
            event.get("lane_id") != original_id
            or event.get("agent_id") != original["agent_id"]
            or event.get("from_state") != "replaced"
            or event.get("to_state") != terminal_state
            or original.get("replacement_lane_id") != replacement_id
            or replacement is None
            or replacement.get("state") != terminal_state
        ):
            _corrupt(sequence, "replacement close lineage is invalid")
        original["state"] = terminal_state
        original["terminal_sequence"] = sequence
        original["last_event_type"] = event_type
        original["updated_at"] = event.get("timestamp")
        original["evidence_refs"] = list(event.get("evidence_refs", []))
    elif (
        event_type == "candidate_validated"
        and (event.get("metadata") or {}).get("candidate_kind")
        == "failed_lane_resolution"
    ):
        _require_evidence(event, sequence)
        if _is_liveness_evidence(state, event["evidence_refs"]):
            _corrupt(sequence, "liveness evidence cannot resolve a failed lane")
        metadata = event.get("metadata") or {}
        original_id = metadata.get("original_lane_id")
        resolution_id = metadata.get("resolution_lane_id")
        original = state["lanes"].get(original_id)
        resolution = state["lanes"].get(resolution_id)
        if original is None or original["state"] != "failed":
            _corrupt(sequence, "failure resolution original lane is invalid")
        if (
            event.get("lane_id") != original_id
            or event.get("agent_id") != original["agent_id"]
            or event.get("from_state") != "failed"
            or event.get("to_state") != "failed"
            or resolution_id == original_id
            or resolution is None
            or resolution.get("state") != "completed"
            or (
                manifest.get("failure_resolution", {}).get("requires_parent")
                and resolution.get("parent_lane_id") != original_id
            )
            or not isinstance(original.get("terminal_sequence"), int)
            or not isinstance(resolution.get("terminal_sequence"), int)
            or resolution["terminal_sequence"] <= original["terminal_sequence"]
            or original_id in state["failure_resolutions"]
        ):
            _corrupt(sequence, "failure resolution lineage is invalid")
        required_digests = {
            _runtime().evidence_digest(original.get("evidence_refs", [])),
            _runtime().evidence_digest(resolution.get("evidence_refs", [])),
        }
        supplied_digests = {
            evidence.get("checksum")
            for evidence in event["evidence_refs"]
            if isinstance(evidence, dict)
        }
        if (
            metadata.get("original_evidence_digest") not in required_digests
            or metadata.get("resolution_evidence_digest") not in required_digests
            or metadata.get("original_evidence_digest")
            == metadata.get("resolution_evidence_digest")
            or not required_digests <= supplied_digests
        ):
            _corrupt(sequence, "failure resolution evidence binding is invalid")
        state["failure_resolutions"][original_id] = {
            "resolution_lane_id": resolution_id,
            "resolved_at": event.get("timestamp"),
            "evidence_refs": list(event.get("evidence_refs", [])),
        }
    elif event_type == "main_verification":
        _require_evidence(event, sequence)
        state["main_verified"] = True
    elif event_type == "topology_registered":
        _require_evidence(event, sequence)
        components = (event.get("metadata") or {}).get("components", [])
        registered = {
            component["id"]: copy.deepcopy(component) for component in components
        }
        for component_id, previous in state["topology"].items():
            if component_id in registered:
                registered[component_id]["coverage_state"] = previous[
                    "coverage_state"
                ]
                registered[component_id]["evidence_refs"] = copy.deepcopy(
                    previous["evidence_refs"]
                )
        state["topology"] = registered
    elif event_type == "topology_component_removed":
        _require_evidence(event, sequence)
        component_id = (event.get("metadata") or {}).get("component_id")
        if component_id not in state["topology"]:
            _corrupt(sequence, "topology removal references an unknown component")
        state["removed_component_records"][component_id] = copy.deepcopy(
            state["topology"][component_id]
        )
        del state["topology"][component_id]
        if component_id not in state["removed_components"]:
            state["removed_components"].append(component_id)
            state["removed_components"].sort()
    elif event_type in {"check_passed", "check_failed"}:
        _require_evidence(event, sequence)
        metadata = event.get("metadata") or {}
        component_id = metadata.get("component_id")
        check_id = metadata.get("check_id")
        component = state["topology"].get(component_id)
        if component is None or check_id not in component.get("required_checks", []):
            _corrupt(sequence, "check result references an unknown required check")
        record = {
            "passed": event_type == "check_passed",
            "evidence_refs": copy.deepcopy(event.get("evidence_refs", [])),
            "reason": event.get("reason"),
        }
        history = state["check_history"].setdefault(component_id, {}).setdefault(
            check_id, []
        )
        if history and history[-1] == record:
            _corrupt(sequence, "duplicate check result")
        history.append(record)
        state["checks"].setdefault(component_id, {})[check_id] = event_type == "check_passed"
    elif event_type == "evidence_attached":
        _require_evidence(event, sequence)
        metadata = event.get("metadata") or {}
        component = state["topology"].get(metadata.get("component_id"))
        if component is None:
            _corrupt(sequence, "component evidence references an unknown component")
        component["coverage_state"] = metadata.get("coverage_state")
        component["evidence_refs"] = list(event.get("evidence_refs", []))
    elif event_type in {
        "handoff_recorded",
        "live_report_recorded",
    }:
        metadata = copy.deepcopy(event.get("metadata") or {})
        report_kind = metadata.get("report_kind")
        previous = state["reports"].get(report_kind)
        if previous is not None and previous != metadata:
            _corrupt(sequence, "report kind is already bound to different evidence")
        state["reports"][report_kind] = metadata
        return
    elif event_type in {
        "candidate_proposed",
        "candidate_validated",
        "candidate_rejected",
    }:
        return
    else:
        _corrupt(sequence, "event type has no coordinator reducer")


def apply_event(state, event, manifest):
    if not isinstance(event, dict):
        _corrupt(state["last_sequence"] + 1, "event is not an object")
    sequence = event.get("sequence")
    if sequence != state["last_sequence"] + 1:
        _corrupt(sequence, "sequence is not contiguous")
    family = ".".join(str(manifest.get("manifest_version", "")).split(".")[:2])
    expected_owner = (
        state["owner_fingerprint"]
        if family == "1.1"
        else state["_receipt_owner_value"]
    )
    if event.get("owner_token") != expected_owner:
        _corrupt(sequence, "event owner fingerprint is stale")
    metadata = event.get("metadata") or {}
    if family == "1.1" and metadata.get("owner_epoch") != state["owner_epoch"]:
        _corrupt(sequence, "event owner epoch is stale")
    event_type = event.get("event_type")
    if state["run_state"] in TERMINAL_RUN_STATES:
        if event_type != "live_report_recorded" or state["run_state"] != "completed":
            _corrupt(sequence, "terminal run rejects further mutation")
    if event.get("event_type") == "transaction_committed":
        clone = copy.deepcopy(state)
        for intent in metadata.get("intents", []):
            logical = dict(intent)
            logical["owner_token"] = event["owner_token"]
            logical["manifest_hash"] = event["manifest_hash"]
            _apply_logical_event(clone, logical, manifest, sequence)
        state.clear()
        state.update(clone)
    else:
        _apply_logical_event(state, event, manifest, sequence)
    state["last_sequence"] = sequence
    state["last_checksum"] = event.get("checksum", state["last_checksum"])
    state["last_event_type"] = event.get("event_type")
    state["updated_at"] = event.get("timestamp")
    event_types = (
        {intent.get("event_type") for intent in metadata.get("intents", [])}
        if event_type == "transaction_committed"
        else {event_type}
    )
    if event_types & {
        "lane_created",
        "lane_reassigned",
        "replacement_repaired",
        "replacement_blocked",
        "replacement_lineage_closed",
    }:
        state["incomplete_replacements"] = sorted(
            lane_id
            for lane_id, lane in state["lanes"].items()
            if lane["state"] == "replaced"
            and lane.get("replacement_lane_id") not in state["lanes"]
        )


def replay_coordinator_state(events, manifest_snapshot):
    iterator = iter(events)
    try:
        first_event = next(iterator)
    except StopIteration as error:
        raise CoordinatorCorrupt("receipt contains no events") from error
    run_metadata = manifest_snapshot["run"]
    if run_metadata is None:
        run_metadata = {
            "owner_token": first_event.get("owner_token"),
            "component_ids": [],
        }
    state = empty_coordinator_state(run_metadata)
    apply_event(state, first_event, manifest_snapshot["manifest"])
    for event in iterator:
        apply_event(state, event, manifest_snapshot["manifest"])
    return state


def load_coordinator_state(run_dir):
    import bluetape_runtime as runtime

    run_path = Path(run_dir)
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_path)
    events = runtime.iter_verified_receipt(run_path)
    return manifest_snapshot, replay_coordinator_state(events, manifest_snapshot)


def _state_root_for_run(run_dir):
    run_path = _runtime().validate_run_directory(run_dir)
    state_root = run_path.parent.parent
    return run_path, state_root


def _lock_owner_status(run_path):
    lock_path = run_path / "locks" / "receipt"
    owner_path = lock_path / "owner.json"
    initializer_path = lock_path.with_name(
        "." + lock_path.name + ".initializing.json"
    )
    if not owner_path.exists():
        return (
            "locked_initializing"
            if lock_path.exists() or initializer_path.exists()
            else "unlocked"
        )
    if owner_path.is_symlink() or not owner_path.is_file():
        return "unsafe"
    try:
        owner = json.loads(owner_path.read_text(encoding="utf-8"))
        pid = owner.get("pid")
        if not isinstance(pid, int) or isinstance(pid, bool):
            return "invalid"
        return "locked_" + _runtime()._probe_pid(pid)
    except (OSError, TypeError, json.JSONDecodeError):
        return "invalid"


def diagnosis_checksum(diagnosis):
    if not isinstance(diagnosis, dict):
        raise ValueError("diagnosis must be an object")
    return hashlib.sha256(
        _runtime().canonical_json(diagnosis).encode("utf-8")
    ).hexdigest()


def inspect_resume(run_dir):
    """Replay verified state without writing receipt or derived caches."""
    runtime = _runtime()
    run_path = runtime.validate_run_directory(run_dir)
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_path)
    family = ".".join(
        manifest_snapshot["manifest"]["manifest_version"].split(".")[:2]
    )
    try:
        if family == "1.0":
            snapshot = runtime._snapshot_from_events(runtime.verify_receipt(run_path))
            return {
                "run_id": run_path.name,
                "run_state": snapshot["state"],
                "last_sequence": snapshot["last_sequence"],
                "last_checksum": snapshot["last_checksum"],
                "manifest_version": manifest_snapshot["manifest"]["manifest_version"],
                "manifest_hash": manifest_snapshot["manifest_hash"],
                "lock_owner_status": _lock_owner_status(run_path),
            }
        _, state = load_coordinator_state(run_path)
    except (runtime.ReceiptCorrupt, CoordinatorCorrupt) as error:
        if isinstance(error, CoordinatorCorrupt):
            first_bad = error.first_bad_sequence or 1
            last_trusted_sequence = max(0, first_bad - 1)
            last_trusted_checksum = ""
            for event in runtime.iter_verified_receipt(run_path):
                if event["sequence"] >= first_bad:
                    break
                last_trusted_checksum = event["checksum"]
        else:
            first_bad = error.first_bad_sequence
            last_trusted_sequence = error.last_trusted_sequence
            last_trusted_checksum = error.last_trusted_checksum
        receipt_path = run_path / "receipt.jsonl"
        receipt_hash, receipt_size = runtime.file_identity(receipt_path)
        return {
            "run_id": run_path.name,
            "effective_state": "blocked",
            "first_bad_sequence": first_bad,
            "last_trusted_sequence": last_trusted_sequence,
            "last_trusted_checksum": last_trusted_checksum,
            "manifest_version": manifest_snapshot["manifest"]["manifest_version"],
            "manifest_hash": manifest_snapshot["manifest_hash"],
            "lock_owner_status": _lock_owner_status(run_path),
            "receipt_hash": receipt_hash,
            "receipt_size": receipt_size,
        }
    active_states = {"starting", "running", "suspected_stall", "recovering"}
    topology_gaps = sorted(
        set(state["approved_component_ids"]) - set(state["topology"])
    )
    return {
        "run_id": run_path.name,
        "run_state": state["run_state"],
        "owner_epoch": state["owner_epoch"],
        "owner_fingerprint": state["owner_fingerprint"],
        "lanes_requiring_observation": sorted(
            lane_id
            for lane_id, lane in state["lanes"].items()
            if lane["state"] in active_states
        ),
        "incomplete_replacements": list(state["incomplete_replacements"]),
        "topology_gaps": topology_gaps,
        "last_sequence": state["last_sequence"],
        "last_checksum": state["last_checksum"],
        "manifest_version": manifest_snapshot["manifest"]["manifest_version"],
        "manifest_hash": manifest_snapshot["manifest_hash"],
        "lock_owner_status": _lock_owner_status(run_path),
    }


def _validate_new_owner_path(state_root, owner_handle, allow_existing=False):
    owner_path = Path(owner_handle).expanduser()
    handles_root = state_root / "handles"
    if owner_path.parent.resolve(strict=False) != handles_root.resolve(strict=True):
        raise ValueError("owner handle must be a direct child of state-root handles")
    _runtime().validate_identifier(owner_path.stem, "owner handle id")
    if owner_path.is_symlink() or (owner_path.exists() and not allow_existing):
        raise ValueError("owner handle already exists")
    return owner_path


def transfer_run_owner(
    run_dir,
    current_owner_handle,
    new_owner_handle,
    evidence_refs,
):
    runtime = _runtime()
    run_path, state_root = _state_root_for_run(run_dir)
    _require_evidence_refs(evidence_refs)
    manifest_snapshot, state = load_coordinator_state(run_path)
    require_run_owner(state, manifest_snapshot, current_owner_handle)
    require_run_state(state, {"planned", "approved", "running", "recovering"})
    if state["incomplete_replacements"]:
        raise CoordinatorConflict(
            "incomplete replacement must be repaired or blocked before owner transfer"
        )
    new_owner_path = _validate_new_owner_path(state_root, new_owner_handle)
    current_path = Path(current_owner_handle).expanduser().resolve(strict=True)
    if current_path == new_owner_path.resolve(strict=False):
        raise ValueError("new owner handle must differ from current owner handle")
    new_owner = runtime._create_owner_handle(
        new_owner_path, run_path.name, epoch=state["owner_epoch"] + 1
    )

    def decide(current):
        require_run_owner(current, manifest_snapshot, current_owner_handle)
        require_run_state(current, {"planned", "approved", "running", "recovering"})
        if current["incomplete_replacements"]:
            raise CoordinatorConflict(
                "incomplete replacement must be repaired or blocked before owner transfer"
            )
        return [
            {
                "event_type": "run_resumed",
                "timestamp": runtime._utc_now(),
                "evidence_refs": evidence_refs,
                "metadata": {
                    "owner_epoch": current["owner_epoch"],
                    "new_owner_fingerprint": new_owner["fingerprint"],
                },
            }
        ]

    try:
        resumed = runtime.mutate_receipt(run_path, current_owner_handle, decide)
    except Exception:
        try:
            orphan = runtime.read_owner_handle(
                new_owner_path, expected_run_id=run_path.name
            )
            if (
                orphan["fingerprint"] == new_owner["fingerprint"]
                and orphan["epoch"] == new_owner["epoch"]
            ):
                new_owner_path.unlink()
        except (OSError, ValueError):
            pass
        raise
    current = runtime.read_owner_handle(current_path, expected_run_id=run_path.name)
    if (
        current["fingerprint"] == state["owner_fingerprint"]
        and current["epoch"] == state["owner_epoch"]
    ):
        current_path.unlink()
    return resumed


def _write_quarantine(path, source, expected_hash, expected_size):
    runtime = _runtime()
    if path.exists() or path.is_symlink():
        runtime.validate_secure_mode(path, 0o600, "quarantine receipt")
        if runtime.file_identity(path) != (expected_hash, expected_size):
            raise CoordinatorConflict("existing quarantine receipt does not match")
        return
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(str(path), flags, 0o600)
    try:
        os.fchmod(descriptor, 0o600)
        with Path(source).open("rb") as stream:
            while True:
                chunk = stream.read(64 * 1024)
                if not chunk:
                    break
                offset = 0
                while offset < len(chunk):
                    written = os.write(descriptor, chunk[offset:])
                    if written <= 0:
                        raise OSError("quarantine copy made no progress")
                    offset += written
        os.fsync(descriptor)
    except Exception:
        path.unlink(missing_ok=True)
        raise
    finally:
        os.close(descriptor)
    if runtime.file_identity(path) != (expected_hash, expected_size):
        path.unlink(missing_ok=True)
        raise RuntimeError("quarantine receipt verification failed")


def _reuse_recovery_run(
    state_root,
    owner_path,
    provenance,
    original_run_metadata,
    approval_evidence,
    quarantine_path,
    damaged_hash,
    diagnosis_checksum_value,
):
    if not owner_path.exists():
        return None
    runtime = _runtime()
    runtime.validate_secure_mode(owner_path, 0o600, "recovery owner handle")
    try:
        owner_payload = json.loads(owner_path.read_text(encoding="utf-8"))
        run_id = owner_payload["run_id"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise CoordinatorConflict("existing recovery owner handle is invalid") from error
    runtime.validate_identifier(run_id, "recovery run id")
    existing_owner = runtime.read_owner_handle(owner_path, expected_run_id=run_id)
    try:
        recovery_run = runtime.validate_run_directory(
            state_root / "runs" / run_id
        )
        manifest_snapshot = runtime.load_run_manifest_snapshot(recovery_run)
        first_event = None
        for event in runtime.iter_verified_receipt(recovery_run):
            if first_event is None:
                first_event = event
    except (OSError, ValueError, runtime.ReceiptCorrupt) as error:
        raise CoordinatorConflict("existing recovery run is invalid") from error
    if first_event is None:
        raise CoordinatorConflict("existing recovery run receipt is empty")
    expected_metadata = {"owner_epoch": 1, **provenance}
    existing_run_metadata = manifest_snapshot["run"] or {}
    if (
        first_event.get("event_type") != "run_created"
        or first_event.get("metadata") != expected_metadata
        or first_event.get("evidence_refs") != approval_evidence
        or existing_run_metadata.get("workflow_type")
        != original_run_metadata.get("workflow_type")
        or existing_run_metadata.get("repo_root")
        != original_run_metadata.get("repo_root")
        or existing_run_metadata.get("component_ids")
        != original_run_metadata.get("component_ids")
        or existing_run_metadata.get("owner_fingerprint")
        != existing_owner["fingerprint"]
        or existing_run_metadata.get("owner_epoch") != existing_owner["epoch"]
    ):
        raise CoordinatorConflict("existing recovery run provenance does not match")
    return {
        "new_run_id": run_id,
        "owner_file": str(owner_path),
        "owner_epoch": 1,
        "quarantine_path": quarantine_path.relative_to(state_root).as_posix(),
        "quarantine_hash": damaged_hash,
        "diagnosis_checksum": diagnosis_checksum_value,
    }


def create_recovery_run(
    run_dir,
    diagnosis,
    diagnosis_checksum,
    new_owner_handle,
    approval_evidence,
):
    runtime = _runtime()
    run_path, state_root = _state_root_for_run(run_dir)
    _require_evidence_refs(approval_evidence)
    if diagnosis.get("effective_state") != "blocked":
        raise ValueError("recovery run requires a blocked receipt diagnosis")
    if diagnosis_checksum != globals()["diagnosis_checksum"](diagnosis):
        raise ValueError("receipt diagnosis checksum does not match")
    current_diagnosis = inspect_resume(run_path)
    if current_diagnosis != diagnosis:
        raise CoordinatorConflict("damaged run changed after receipt diagnosis")
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_path)
    run_metadata = manifest_snapshot["run"] or {}
    original_receipt = run_path / "receipt.jsonl"
    damaged_hash, damaged_size = runtime.file_identity(original_receipt)
    if (
        damaged_hash != diagnosis.get("receipt_hash")
        or damaged_size != diagnosis.get("receipt_size")
    ):
        raise CoordinatorConflict("damaged receipt bytes changed after diagnosis")
    new_owner_path = _validate_new_owner_path(
        state_root, new_owner_handle, allow_existing=True
    )
    quarantine_name = run_path.name + "-" + damaged_hash + ".receipt.jsonl"
    quarantine_root = runtime._ensure_secure_directory(state_root / "quarantine")
    quarantine_path = quarantine_root / quarantine_name
    relative_quarantine = quarantine_path.relative_to(state_root).as_posix()
    provenance = {
        "recovery_original_run_id": run_path.name,
        "recovery_diagnose_checksum": diagnosis_checksum,
        "recovery_manifest_version": manifest_snapshot["manifest"]["manifest_version"],
        "recovery_manifest_hash": manifest_snapshot["manifest_hash"],
        "recovery_quarantine_path": relative_quarantine,
        "recovery_quarantine_hash": damaged_hash,
        "recovery_first_bad_sequence": diagnosis["first_bad_sequence"],
        "recovery_trusted_sequence": diagnosis["last_trusted_sequence"],
        "recovery_trusted_checksum": diagnosis["last_trusted_checksum"],
    }
    lock_path = state_root / "locks" / ("recovery-" + run_path.name)
    with runtime.state_lock(lock_path):
        if inspect_resume(run_path) != diagnosis:
            raise CoordinatorConflict("damaged run changed before quarantine")
        _write_quarantine(
            quarantine_path,
            original_receipt,
            damaged_hash,
            damaged_size,
        )
        runtime.validate_secure_mode(quarantine_path, 0o600, "quarantine receipt")
        if runtime.file_identity(quarantine_path) != (damaged_hash, damaged_size):
            raise RuntimeError("quarantine receipt verification failed")
        reused = _reuse_recovery_run(
            state_root,
            new_owner_path,
            provenance,
            run_metadata,
            approval_evidence,
            quarantine_path,
            damaged_hash,
            diagnosis_checksum,
        )
        if reused is not None:
            return reused
        initialized = runtime.initialize_run(
            state_root,
            workflow_type=run_metadata["workflow_type"],
            repo_root=run_metadata["repo_root"],
            component_ids=run_metadata["component_ids"],
            owner_file=new_owner_path,
            recovery_provenance=provenance,
            initial_evidence_refs=approval_evidence,
        )
    return {
        "new_run_id": initialized["run_id"],
        "owner_file": initialized["owner_file"],
        "owner_epoch": initialized["owner_epoch"],
        "quarantine_path": relative_quarantine,
        "quarantine_hash": damaged_hash,
        "diagnosis_checksum": diagnosis_checksum,
    }


_HANDOFF_REPORT_FIELDS = {
    "canonical_sha",
    "agents_hash",
    "skill_hash",
    "manifest_hash",
    "run_id",
    "owner_epoch",
    "receipt_head",
    "target_hashes",
}
_LIVE_REPORT_FIELDS = _HANDOFF_REPORT_FIELDS | {
    "command_ids",
    "timestamps",
    "exit_status",
    "source_hash",
    "rendered_hash",
    "live_hash",
    "evidence_refs",
}
_FORBIDDEN_REPORT_TERMS = {
    "token",
    "password",
    "secret",
    "prompt",
    "raw_output",
    "fencing",
}


def _is_checksum(value):
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _validate_report_payload(report_kind, payload):
    expected = (
        _HANDOFF_REPORT_FIELDS
        if report_kind == "handoff"
        else _LIVE_REPORT_FIELDS
    )
    if not isinstance(payload, dict) or set(payload) != expected:
        raise ValueError("report fields do not match the fixed contract")
    encoded = _runtime().canonical_json(payload)
    lowered = encoded.lower()
    if any(term in lowered for term in _FORBIDDEN_REPORT_TERMS):
        raise ValueError("report contains forbidden secret or raw-output fields")
    for field in (
        "canonical_sha",
        "agents_hash",
        "skill_hash",
        "manifest_hash",
        "receipt_head",
    ):
        if not _is_checksum(payload[field]):
            raise ValueError(field + " must be lowercase SHA-256")
    if (
        not isinstance(payload["owner_epoch"], int)
        or isinstance(payload["owner_epoch"], bool)
        or payload["owner_epoch"] < 1
    ):
        raise ValueError("owner_epoch must be a positive integer")
    target_hashes = payload["target_hashes"]
    if (
        not isinstance(target_hashes, dict)
        or len(target_hashes) > 64
        or any(
            not isinstance(path, str)
            or not path
            or len(path) > 256
            or Path(path).is_absolute()
            or ".." in Path(path).parts
            or not _is_checksum(checksum)
            for path, checksum in target_hashes.items()
        )
    ):
        raise ValueError("target_hashes must contain bounded SHA-256 entries")
    if report_kind == "live":
        for field in ("source_hash", "rendered_hash", "live_hash"):
            if not _is_checksum(payload[field]):
                raise ValueError(field + " must be lowercase SHA-256")
        if (
            not isinstance(payload["command_ids"], list)
            or not 1 <= len(payload["command_ids"]) <= 64
            or not all(
                isinstance(command_id, str) and 0 < len(command_id) <= 128
                for command_id in payload["command_ids"]
            )
        ):
            raise ValueError("command_ids must be a bounded non-empty list")
        if (
            not isinstance(payload["timestamps"], list)
            or len(payload["timestamps"]) != len(payload["command_ids"])
        ):
            raise ValueError("timestamps must align with command_ids")
        for timestamp in payload["timestamps"]:
            _parse_timestamp(timestamp, "report timestamp")
        if not isinstance(payload["exit_status"], int) or isinstance(
            payload["exit_status"], bool
        ):
            raise ValueError("exit_status must be an integer")
        _runtime()._validate_evidence_refs(payload["evidence_refs"])
    return copy.deepcopy(payload)


def create_bound_report(run_dir, owner_handle, report_kind, payload):
    if report_kind not in {"handoff", "live"}:
        raise ValueError("report kind must be handoff or live")
    runtime = _runtime()
    run_path, state_root = _state_root_for_run(run_dir)
    manifest_snapshot, state = load_coordinator_state(run_path)
    require_run_owner(state, manifest_snapshot, owner_handle)
    expected_state = {"running", "recovering"} if report_kind == "handoff" else {"completed"}
    require_run_state(state, expected_state)
    validated = _validate_report_payload(report_kind, payload)
    if validated["run_id"] != run_path.name:
        raise ValueError("report run_id does not match")
    if validated["owner_epoch"] != state["owner_epoch"]:
        raise CoordinatorConflict("report owner epoch is stale")
    if validated["manifest_hash"] != manifest_snapshot["manifest_hash"]:
        raise CoordinatorConflict("report manifest hash is stale")
    runtime_kind = "fresh_session_handoff" if report_kind == "handoff" else "live_apply"
    report_bytes = (runtime.canonical_json(validated) + "\n").encode("utf-8")
    report_checksum = hashlib.sha256(report_bytes).hexdigest()
    report_name = (
        run_path.name + "-" + runtime_kind + "-" + report_checksum[:16] + ".json"
    )
    reports_root = runtime._ensure_secure_directory(state_root / "reports")
    report_path = reports_root / report_name
    relative_path = report_path.relative_to(state_root).as_posix()
    metadata = {
        "owner_epoch": state["owner_epoch"],
        "report_kind": runtime_kind,
        "report_path": relative_path,
        "report_checksum": report_checksum,
        "report_receipt_head": validated["receipt_head"],
    }
    existing = state["reports"].get(runtime_kind)
    if existing is not None:
        if existing != metadata:
            raise CoordinatorConflict("report kind is already bound")
        if not report_path.is_file() or report_path.is_symlink():
            raise CoordinatorConflict("bound report file is missing or unsafe")
        if hashlib.sha256(report_path.read_bytes()).hexdigest() != report_checksum:
            raise CoordinatorConflict("bound report file checksum differs")
        return {
            "report_path": relative_path,
            "report_checksum": report_checksum,
            "report_receipt_head": validated["receipt_head"],
        }
    if validated["receipt_head"] != state["last_checksum"]:
        raise CoordinatorConflict("report receipt head is stale")
    if report_path.exists() or report_path.is_symlink():
        runtime.validate_secure_mode(report_path, 0o600, "report")
        if report_path.read_bytes() != report_bytes:
            raise CoordinatorConflict("orphan report content differs")
    else:
        runtime._write_json_atomic(report_path, validated)
    evidence_refs = [
        {
            "kind": "report",
            "summary": "immutable report bound to receipt head",
            "checksum": report_checksum,
        }
    ]

    def decide(current):
        require_run_owner(current, manifest_snapshot, owner_handle)
        require_run_state(current, expected_state)
        if current["last_checksum"] != validated["receipt_head"]:
            raise CoordinatorConflict("report receipt head changed before commit")
        return [
            {
                "event_type": (
                    "handoff_recorded"
                    if report_kind == "handoff"
                    else "live_report_recorded"
                ),
                "evidence_refs": evidence_refs,
                "metadata": metadata,
            }
        ]

    runtime.mutate_receipt(run_path, owner_handle, decide)
    return {
        "report_path": relative_path,
        "report_checksum": report_checksum,
        "report_receipt_head": validated["receipt_head"],
    }


def _runtime():
    import bluetape_runtime as runtime

    return runtime


def _require_evidence_refs(evidence_refs):
    if not isinstance(evidence_refs, list) or not evidence_refs:
        raise ValueError("lifecycle transition requires evidence")


def require_run_state(state, allowed):
    if state["run_state"] not in set(allowed):
        raise CoordinatorConflict("run state does not allow this command")
    return state["run_state"]


def require_run_owner(state, manifest_snapshot, owner_handle):
    owner = _runtime().read_owner_handle(
        owner_handle,
        expected_run_id=manifest_snapshot["run"]["run_id"]
        if "run_id" in manifest_snapshot["run"]
        else None,
    )
    if (
        owner["fingerprint"] != state["owner_fingerprint"]
        or owner["epoch"] != state["owner_epoch"]
    ):
        raise CoordinatorConflict("owner handle is stale")
    return owner


def require_new_identifier(collection, identifier):
    _runtime().validate_identifier(identifier)
    if identifier in collection:
        raise CoordinatorConflict("identifier already exists")
    return identifier


def require_active_lane_owner(state, lane_id, agent_id):
    lane = state["lanes"].get(lane_id)
    if lane is None:
        raise CoordinatorConflict("lane does not exist")
    if lane["state"] in TERMINAL_LANE_STATES | {"replaced"}:
        raise CoordinatorConflict("lane is not active")
    if lane["agent_id"] != agent_id:
        raise CoordinatorConflict("agent does not own the lane")
    return lane


def _is_liveness_evidence(state, evidence_refs):
    digest = _runtime().evidence_digest(evidence_refs)
    for lane in state["lanes"].values():
        if digest in lane.get("liveness_evidence_digests", []):
            return True
    return False


def _require_completion_evidence(state, evidence_refs):
    _require_evidence_refs(evidence_refs)
    if _is_liveness_evidence(state, evidence_refs):
        raise ValueError("liveness evidence cannot satisfy completion evidence")
    digest = _runtime().evidence_digest(evidence_refs)
    return digest


def validate_topology(
    components,
    known_lane_ids,
    required_component_ids,
    limits,
):
    if (
        not isinstance(components, list)
        or not 1 <= len(components) <= limits["max_components"]
    ):
        raise ValueError("topology component count is outside the limit")
    by_id = {}
    for raw_component in components:
        component = copy.deepcopy(raw_component)
        _runtime()._validate_topology_component(component, limits)
        component_id = component["id"]
        if component_id in by_id:
            raise ValueError("duplicate component id: " + component_id)
        if component["owner_lane"] not in set(known_lane_ids):
            raise ValueError(
                "unknown topology owner lane: " + component["owner_lane"]
            )
        if component["coverage_state"] != "missing" or component["evidence_refs"]:
            raise ValueError("registered topology must begin without coverage evidence")
        by_id[component_id] = component
    known_ids = set(by_id)
    if known_ids != set(required_component_ids):
        raise ValueError("topology must match the approved component snapshot")
    indegree = {component_id: 0 for component_id in known_ids}
    dependents = {component_id: [] for component_id in known_ids}
    for component in components:
        unknown = sorted(set(component["dependencies"]) - known_ids)
        if unknown:
            raise ValueError(
                "unknown component dependencies: " + ", ".join(unknown)
            )
        component_id = component["id"]
        for dependency in component["dependencies"]:
            indegree[component_id] += 1
            dependents[dependency].append(component_id)
    ready = sorted(
        component_id for component_id, degree in indegree.items() if degree == 0
    )
    visited_count = 0
    while ready:
        current = ready.pop()
        visited_count += 1
        for dependent in dependents[current]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)
    if visited_count != len(known_ids):
        raise ValueError("topology dependency cycle")
    return [by_id[component_id] for component_id in sorted(by_id)]


def register_topology(
    run_dir,
    owner_handle,
    components,
    evidence_refs,
    reason=None,
):
    runtime = _runtime()
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_dir)
    _require_evidence_refs(evidence_refs)

    def decide(state):
        require_run_owner(state, manifest_snapshot, owner_handle)
        require_run_state(state, {"running", "recovering"})
        expected_ids = set(state["approved_component_ids"]) - set(
            state["removed_components"]
        )
        validated = validate_topology(
            components,
            set(state["lanes"]),
            expected_ids,
            manifest_snapshot["manifest"]["resource_limits"],
        )
        return [
            {
                "event_type": "topology_registered",
                "evidence_refs": evidence_refs,
                "reason": reason,
                "metadata": {
                    "owner_epoch": state["owner_epoch"],
                    "components": validated,
                },
            }
        ]

    return runtime.mutate_receipt(run_dir, owner_handle, decide)["topology"]


def remove_topology_component(
    run_dir,
    owner_handle,
    component_id,
    evidence_refs,
    reason=None,
):
    runtime = _runtime()
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_dir)
    runtime.validate_identifier(component_id, "component id")
    _require_evidence_refs(evidence_refs)
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("topology component removal requires a reason")

    def decide(state):
        require_run_owner(state, manifest_snapshot, owner_handle)
        require_run_state(state, {"running", "recovering"})
        if component_id not in state["topology"]:
            raise CoordinatorConflict("topology component does not exist")
        dependents = sorted(
            candidate_id
            for candidate_id, component in state["topology"].items()
            if component_id in component["dependencies"]
        )
        if dependents:
            raise CoordinatorConflict(
                "topology component still has dependents: " + ", ".join(dependents)
            )
        return [
            {
                "event_type": "topology_component_removed",
                "evidence_refs": evidence_refs,
                "reason": reason,
                "metadata": {
                    "owner_epoch": state["owner_epoch"],
                    "component_id": component_id,
                },
            }
        ]

    return runtime.mutate_receipt(run_dir, owner_handle, decide)["topology"]


def record_check_result(
    run_dir,
    owner_handle,
    component_id,
    check_id,
    passed,
    evidence_refs,
    reason=None,
):
    runtime = _runtime()
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_dir)
    runtime.validate_identifier(component_id, "component id")
    runtime.validate_identifier(check_id, "check id")
    if not isinstance(passed, bool):
        raise ValueError("check result passed must be a boolean")
    _require_evidence_refs(evidence_refs)

    def decide(state):
        require_run_owner(state, manifest_snapshot, owner_handle)
        require_run_state(state, {"running", "recovering"})
        component = state["topology"].get(component_id)
        if component is None or check_id not in component["required_checks"]:
            raise CoordinatorConflict("component check is not registered")
        history = state["check_history"].get(component_id, {}).get(check_id, [])
        record = {
            "passed": passed,
            "evidence_refs": copy.deepcopy(evidence_refs),
            "reason": reason,
        }
        if history and history[-1] == record:
            raise CoordinatorConflict("duplicate check result")
        if history and history[-1]["passed"] is False and passed:
            if not isinstance(reason, str) or not reason.strip():
                raise CoordinatorConflict(
                    "a recovered check requires a fresh result and reason"
                )
            if runtime.evidence_digest(history[-1]["evidence_refs"]) == runtime.evidence_digest(
                evidence_refs
            ):
                raise CoordinatorConflict(
                    "a recovered check requires fresh evidence"
                )
        return [
            {
                "event_type": "check_passed" if passed else "check_failed",
                "evidence_refs": evidence_refs,
                "reason": reason,
                "metadata": {
                    "owner_epoch": state["owner_epoch"],
                    "component_id": component_id,
                    "check_id": check_id,
                },
            }
        ]

    state = runtime.mutate_receipt(run_dir, owner_handle, decide)
    return state["checks"][component_id][check_id]


def attach_component_evidence(
    run_dir,
    owner_handle,
    component_id,
    evidence_refs,
):
    runtime = _runtime()
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_dir)
    runtime.validate_identifier(component_id, "component id")

    def decide(state):
        require_run_owner(state, manifest_snapshot, owner_handle)
        require_run_state(state, {"running", "recovering"})
        _require_completion_evidence(state, evidence_refs)
        component = state["topology"].get(component_id)
        if component is None:
            raise CoordinatorConflict("topology component does not exist")
        if component["coverage_state"] == "covered":
            raise CoordinatorConflict("component evidence is already attached")
        owner_lane = state["lanes"].get(component["owner_lane"])
        if owner_lane is None or owner_lane["state"] != "completed":
            raise CoordinatorConflict("component owner lane is not completed")
        failed_checks = [
            check_id
            for check_id in component["required_checks"]
            if state["checks"].get(component_id, {}).get(check_id) is not True
        ]
        if failed_checks:
            raise CoordinatorConflict("component required checks are incomplete")
        return [
            {
                "event_type": "evidence_attached",
                "evidence_refs": evidence_refs,
                "metadata": {
                    "owner_epoch": state["owner_epoch"],
                    "component_id": component_id,
                    "coverage_state": "covered",
                },
            }
        ]

    return runtime.mutate_receipt(run_dir, owner_handle, decide)["topology"][
        component_id
    ]


def evaluate_run_completion(state, manifest):
    approved_ids = set(state["approved_component_ids"])
    removed_records = state.get("removed_component_records", {})
    missing_topology = (
        approved_ids - set(state["topology"]) - set(removed_records)
    )
    missing_topology.update(
        component_id
        for component_id, component in removed_records.items()
        if component["required"]
    )
    required_components = {
        component_id: component
        for component_id, component in state["topology"].items()
        if component["required"]
    }
    resolved_failed_lanes = {
        lane_id
        for lane_id, resolution in state.get("failure_resolutions", {}).items()
        if state["lanes"].get(lane_id, {}).get("state") == "failed"
        and state["lanes"].get(resolution.get("resolution_lane_id"), {}).get("state")
        == "completed"
    }
    unresolved_failed_lanes = {
        lane_id
        for lane_id, lane in state["lanes"].items()
        if lane["state"] == "failed" and lane_id not in resolved_failed_lanes
    }
    incomplete_lanes = {
        lane_id
        for lane_id, lane in state["lanes"].items()
        if lane["state"] != "completed" and lane_id not in resolved_failed_lanes
    }
    incomplete_lanes.update(
        component["owner_lane"]
        for component in required_components.values()
        if state["lanes"].get(component["owner_lane"], {}).get("state")
        != "completed"
        and component["owner_lane"] not in resolved_failed_lanes
    )
    missing_components = set(missing_topology)
    missing_components.update(
        component_id
        for component_id, component in required_components.items()
        if component["coverage_state"] != "covered"
        or not component["evidence_refs"]
    )
    failed_checks = sorted(
        component_id + ":" + check_id
        for component_id, component in required_components.items()
        for check_id in component["required_checks"]
        if state["checks"].get(component_id, {}).get(check_id) is not True
    )
    result = {
        "missing_lanes": sorted(incomplete_lanes),
        "unresolved_failed_lanes": sorted(unresolved_failed_lanes),
        "resolved_failed_lanes": sorted(resolved_failed_lanes),
        "missing_components": sorted(missing_components),
        "failed_checks": failed_checks,
        "missing_main_verification": not state["main_verified"],
        "incomplete_replacements": list(state["incomplete_replacements"]),
    }
    result["complete"] = not any(
        (
            result["missing_lanes"],
            result["missing_components"],
            result["failed_checks"],
            result["missing_main_verification"],
            result["incomplete_replacements"],
        )
    )
    return result


def resolve_failed_lane(
    run_dir,
    lane_id,
    resolution_lane_id,
    owner_handle,
    decided_at,
    evidence_refs,
):
    runtime = _runtime()
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_dir)
    runtime.validate_identifier(lane_id, "lane id")
    runtime.validate_identifier(resolution_lane_id, "resolution lane id")
    parse_timestamp(decided_at)
    _require_evidence_refs(evidence_refs)

    def decide(state):
        require_run_owner(state, manifest_snapshot, owner_handle)
        require_run_state(state, {"running", "recovering"})
        original = state["lanes"].get(lane_id)
        resolution = state["lanes"].get(resolution_lane_id)
        if original is None or original["state"] != "failed":
            raise CoordinatorConflict("lane is not a failed lane")
        if lane_id == resolution_lane_id:
            raise ValueError("failed lane cannot resolve itself")
        if resolution is None or resolution["state"] != "completed":
            raise CoordinatorConflict("resolution lane is not completed")
        if (
            manifest_snapshot["manifest"]
            .get("failure_resolution", {})
            .get("requires_parent")
            and resolution.get("parent_lane_id") != lane_id
        ):
            raise CoordinatorConflict("resolution lane does not declare failed parent")
        if resolution.get("terminal_sequence", 0) <= original.get(
            "terminal_sequence", 0
        ):
            raise CoordinatorConflict("resolution lane did not complete after failure")
        if lane_id in state["failure_resolutions"]:
            raise CoordinatorConflict("failed lane is already resolved")
        _require_completion_evidence(state, evidence_refs)
        original_digest = runtime.evidence_digest(original.get("evidence_refs", []))
        resolution_digest = runtime.evidence_digest(resolution.get("evidence_refs", []))
        supplied_digests = {
            evidence.get("checksum")
            for evidence in evidence_refs
            if isinstance(evidence, dict)
        }
        if {original_digest, resolution_digest} - supplied_digests:
            raise ValueError(
                "resolution evidence must bind failed and completed lane evidence"
            )
        return [
            {
                "event_type": "candidate_validated",
                "lane_id": lane_id,
                "agent_id": original["agent_id"],
                "from_state": "failed",
                "to_state": "failed",
                "timestamp": decided_at,
                "evidence_refs": evidence_refs,
                "metadata": {
                    "owner_epoch": state["owner_epoch"],
                    "candidate_kind": "failed_lane_resolution",
                    "original_lane_id": lane_id,
                    "resolution_lane_id": resolution_lane_id,
                    "original_evidence_digest": original_digest,
                    "resolution_evidence_digest": resolution_digest,
                },
            }
        ]

    state = runtime.mutate_receipt(run_dir, owner_handle, decide)
    return state["failure_resolutions"][lane_id]


def complete_run(run_dir, owner_handle, evidence_refs):
    runtime = _runtime()
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_dir)

    def decide(state):
        require_run_owner(state, manifest_snapshot, owner_handle)
        require_run_state(state, {"running"})
        _require_completion_evidence(state, evidence_refs)
        candidate = copy.deepcopy(state)
        candidate["main_verified"] = True
        result = evaluate_run_completion(candidate, manifest_snapshot["manifest"])
        if not result["complete"]:
            raise CompletionBlocked(result)
        return [
            {
                "event_type": "main_verification",
                "evidence_refs": evidence_refs,
                "metadata": {"owner_epoch": state["owner_epoch"]},
            },
            {
                "event_type": "run_completed",
                "from_state": "running",
                "to_state": "completed",
                "evidence_refs": evidence_refs,
                "metadata": {"owner_epoch": state["owner_epoch"]},
            },
        ]

    return runtime.mutate_receipt(run_dir, owner_handle, decide)


def require_intent_transition(table, intent, current_state):
    transition = table.get(intent)
    if transition is None:
        raise ValueError("unknown lifecycle intent")
    event_type, allowed, target = transition
    if current_state not in allowed:
        raise CoordinatorConflict("current state does not allow lifecycle intent")
    return event_type, current_state, target


def _parse_timestamp(value, field):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(field + " must be a UTC timestamp")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as error:
        raise ValueError(field + " must be a UTC timestamp") from error


def require_deadline_order(observed_at, startup_ack_deadline, command_deadline):
    observed = _parse_timestamp(observed_at, "observed_at")
    startup = _parse_timestamp(startup_ack_deadline, "startup_ack_deadline")
    command = _parse_timestamp(command_deadline, "command_deadline")
    if not observed < startup <= command:
        raise ValueError(
            "deadlines must satisfy observed_at < startup_ack_deadline <= command_deadline"
        )


def _run_transition(run_dir, owner_handle, intent, decided_at, evidence_refs, reason=None):
    runtime = _runtime()
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_dir)
    _parse_timestamp(decided_at, "decided_at")
    _require_evidence_refs(evidence_refs)

    def decide(state):
        require_run_owner(state, manifest_snapshot, owner_handle)
        event_type, source, target = require_intent_transition(
            RUN_INTENT_TRANSITIONS, intent, state["run_state"]
        )
        return [
            {
                "event_type": event_type,
                "from_state": source,
                "to_state": target,
                "timestamp": decided_at,
                "evidence_refs": evidence_refs,
                "reason": reason,
            }
        ]

    return runtime.mutate_receipt(run_dir, owner_handle, decide)


def approve_run(run_dir, owner_handle, decided_at, evidence_refs):
    return _run_transition(
        run_dir, owner_handle, "approve", decided_at, evidence_refs
    )


def start_run(run_dir, owner_handle, decided_at, evidence_refs):
    return _run_transition(run_dir, owner_handle, "start", decided_at, evidence_refs)


def start_recovery(run_dir, owner_handle, decided_at, evidence_refs, reason=None):
    return _run_transition(
        run_dir,
        owner_handle,
        "recovery_start",
        decided_at,
        evidence_refs,
        reason,
    )


def finish_recovery(run_dir, owner_handle, decided_at, evidence_refs):
    return _run_transition(
        run_dir, owner_handle, "recovery_finish", decided_at, evidence_refs
    )


def terminate_run(
    run_dir, owner_handle, intent, decided_at, evidence_refs, reason=None
):
    if intent not in {"fail", "block", "cancel"}:
        raise ValueError("terminal run intent must be fail, block or cancel")
    return _run_transition(
        run_dir, owner_handle, intent, decided_at, evidence_refs, reason
    )


def create_lane(
    run_dir,
    lane_id,
    agent_id,
    owner_handle,
    assignment,
    write_scope,
    fallback,
    observed_at,
    startup_ack_deadline,
    command_deadline,
    evidence_refs,
    parent_lane_id=None,
    replacement_count=0,
):
    runtime = _runtime()
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_dir)
    runtime.validate_identifier(lane_id, "lane id")
    runtime.validate_identifier(agent_id, "agent id")
    if parent_lane_id is not None:
        runtime.validate_identifier(parent_lane_id, "parent lane id")
    if not isinstance(assignment, str) or not assignment.strip():
        raise ValueError("assignment must be non-empty")
    if not isinstance(fallback, str) or not fallback.strip():
        raise ValueError("fallback must be non-empty")
    if (
        not isinstance(replacement_count, int)
        or isinstance(replacement_count, bool)
        or replacement_count < 0
    ):
        raise ValueError("replacement_count must be a non-negative integer")
    scope = runtime.canonicalize_write_scope(
        manifest_snapshot["run"]["repo_root"],
        write_scope,
        limits=manifest_snapshot["manifest"]["resource_limits"],
    )
    require_deadline_order(observed_at, startup_ack_deadline, command_deadline)
    _require_evidence_refs(evidence_refs)

    def decide(state):
        require_run_owner(state, manifest_snapshot, owner_handle)
        require_run_state(state, {"running", "recovering"})
        require_new_identifier(state["lanes"], lane_id)
        if len(state["lanes"]) >= manifest_snapshot["manifest"]["resource_limits"][
            "max_lanes"
        ]:
            raise CoordinatorConflict("lane limit reached")
        return [
            {
                "event_type": "lane_created",
                "lane_id": lane_id,
                "agent_id": agent_id,
                "to_state": "pending",
                "timestamp": observed_at,
                "evidence_refs": evidence_refs,
                "metadata": {
                    "owner_epoch": state["owner_epoch"],
                    "assignment": assignment,
                    "write_scope": scope,
                    "fallback": fallback,
                    "startup_ack_deadline": startup_ack_deadline,
                    "command_deadline": command_deadline,
                    "parent_lane_id": parent_lane_id,
                    "replacement_count": replacement_count,
                },
            }
        ]

    state = runtime.mutate_receipt(run_dir, owner_handle, decide)
    return state["lanes"][lane_id]


def transition_lane(
    run_dir,
    lane_id,
    agent_id,
    owner_handle,
    intent,
    decided_at,
    evidence_refs,
    reason=None,
    metadata=None,
):
    runtime = _runtime()
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_dir)
    runtime.validate_identifier(lane_id, "lane id")
    runtime.validate_identifier(agent_id, "agent id")
    _parse_timestamp(decided_at, "decided_at")
    _require_evidence_refs(evidence_refs)
    supplied_metadata = {} if metadata is None else copy.deepcopy(metadata)
    if not isinstance(supplied_metadata, dict):
        raise ValueError("transition metadata must be an object")

    def decide(state):
        require_run_owner(state, manifest_snapshot, owner_handle)
        require_run_state(state, {"running", "recovering"})
        lane = require_active_lane_owner(state, lane_id, agent_id)
        event_type, source, target = require_intent_transition(
            LANE_INTENT_TRANSITIONS, intent, lane["state"]
        )
        if (
            intent == "complete"
            and runtime.evidence_digest(evidence_refs)
            == lane.get("last_evidence_digest")
        ):
            raise ValueError("liveness evidence cannot complete a lane")
        event_metadata = copy.deepcopy(supplied_metadata)
        if intent == "complete":
            if "changed_paths" not in event_metadata:
                raise ValueError("lane completion requires verified changed paths")
            changed_paths = runtime.canonicalize_write_scope(
                manifest_snapshot["run"]["repo_root"],
                event_metadata["changed_paths"],
                limits=manifest_snapshot["manifest"]["resource_limits"],
            )
            if changed_paths != event_metadata["changed_paths"]:
                raise ValueError("changed paths must already be canonical")
            allowed_scope = lane.get("write_scope", [])
            outside_scope = [
                path
                for path in changed_paths
                if not any(
                    path == allowed or path.startswith(allowed + "/")
                    for allowed in allowed_scope
                )
            ]
            if outside_scope:
                raise CoordinatorConflict("changed paths exceed the pinned lane scope")
            event_metadata["changed_paths"] = changed_paths
        event_metadata["owner_epoch"] = state["owner_epoch"]
        return [
            {
                "event_type": event_type,
                "lane_id": lane_id,
                "agent_id": agent_id,
                "from_state": source,
                "to_state": target,
                "timestamp": decided_at,
                "evidence_refs": evidence_refs,
                "reason": reason,
                "metadata": event_metadata,
            }
        ]

    state = runtime.mutate_receipt(run_dir, owner_handle, decide)
    return state["lanes"][lane_id]


def parse_timestamp(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("timestamp must be UTC ISO-8601 ending in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as error:
        raise ValueError("timestamp must be UTC ISO-8601 ending in Z") from error
    if parsed.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return parsed


def require_fresh_evidence(lane, evidence_refs, reason):
    if not evidence_refs:
        raise ValueError("liveness evidence is required")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("liveness reason is required")
    digest = _runtime().evidence_digest(evidence_refs)
    if (
        digest == lane.get("last_evidence_digest")
        and reason == lane.get("last_reason")
    ):
        raise ValueError("liveness evidence is unchanged")
    return digest


def record_heartbeat(
    run_dir,
    lane_id,
    agent_id,
    owner_handle,
    observed_at,
    silence_lease_deadline,
    evidence_refs,
    reason,
):
    runtime = _runtime()
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_dir)
    runtime.validate_identifier(lane_id, "lane id")
    runtime.validate_identifier(agent_id, "agent id")
    observed = parse_timestamp(observed_at)
    lease = parse_timestamp(silence_lease_deadline)

    def decide(state):
        require_run_owner(state, manifest_snapshot, owner_handle)
        require_run_state(state, {"running", "recovering"})
        lane = require_active_lane_owner(state, lane_id, agent_id)
        if lane["state"] != "running":
            raise CoordinatorConflict("heartbeat requires a running lane")
        command = parse_timestamp(lane.get("command_deadline"))
        if not observed < lease <= command:
            raise ValueError(
                "heartbeat deadlines must satisfy observed_at < lease <= command_deadline"
            )
        maximum = manifest_snapshot["manifest"]["liveness"][
            "max_silence_lease_seconds"
        ]
        if (lease - observed).total_seconds() > maximum:
            raise ValueError("silence lease exceeds manifest maximum")
        digest = require_fresh_evidence(lane, evidence_refs, reason)
        common = {
            "lane_id": lane_id,
            "agent_id": agent_id,
            "from_state": "running",
            "to_state": "running",
            "timestamp": observed_at,
            "evidence_refs": evidence_refs,
        }
        return [
            {
                **common,
                "event_type": "heartbeat_observed",
                "metadata": {
                    "owner_epoch": state["owner_epoch"],
                    "evidence_digest": digest,
                },
            },
            {
                **common,
                "event_type": "lease_renewed",
                "reason": reason,
                "metadata": {
                    "owner_epoch": state["owner_epoch"],
                    "silence_lease_deadline": silence_lease_deadline,
                    "evidence_digest": digest,
                },
            },
        ]

    state = runtime.mutate_receipt(run_dir, owner_handle, decide)
    return state["lanes"][lane_id]


def evaluate_lane_liveness(lane, manifest, now, command_alive=None):
    if not isinstance(lane, dict) or not isinstance(manifest, dict):
        raise ValueError("lane and manifest must be objects")
    if command_alive is not None and not isinstance(command_alive, bool):
        raise ValueError("command_alive must be true, false or unknown")
    observed = parse_timestamp(now) if isinstance(now, str) else now
    if not isinstance(observed, datetime) or observed.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    state = lane.get("state")
    if state in TERMINAL_LANE_STATES | {"replaced"}:
        return {"action": "none", "reason": "lane is terminal"}
    if state == "pending":
        return {"action": "continue", "reason": "lane awaits dispatch"}
    if state == "starting":
        ack_deadline = parse_timestamp(lane.get("startup_ack_deadline"))
        if observed < ack_deadline:
            return {"action": "continue", "reason": "startup ACK is pending"}
        return {"action": "suspect_stall", "reason": "startup ACK deadline elapsed"}
    if state == "running":
        fresh_until = None
        updated_at = lane.get("updated_at")
        if updated_at is not None:
            fresh_until = parse_timestamp(updated_at) + timedelta(
                seconds=manifest["liveness"]["suspected_stall_seconds"]
            )
        lease_value = lane.get("silence_lease_deadline")
        if lease_value is not None:
            lease_deadline = parse_timestamp(lease_value)
            fresh_until = (
                lease_deadline
                if fresh_until is None
                else max(fresh_until, lease_deadline)
            )
        if fresh_until is not None and observed < fresh_until:
            return {"action": "continue", "reason": "fresh evidence"}
        command_deadline = parse_timestamp(lane.get("command_deadline"))
        if command_alive is True and observed < command_deadline:
            return {
                "action": "observe_command",
                "reason": "command is alive within its deadline",
            }
        return {"action": "suspect_stall", "reason": "no fresh evidence"}
    if state == "suspected_stall":
        return {"action": "send_probe", "reason": "probe has not been sent"}
    if state == "recovering":
        probe_deadline = parse_timestamp(lane.get("probe_deadline"))
        command_deadline = parse_timestamp(lane.get("command_deadline"))
        if observed < probe_deadline or observed < command_deadline:
            return {"action": "await_probe", "reason": "a recovery deadline remains"}
        maximum = manifest["liveness"]["max_replacements"]
        if lane.get("replacement_count", 0) >= maximum:
            return {
                "action": "main_takeover",
                "reason": "replacement limit reached",
            }
        if command_alive is None:
            return {
                "action": "observe_command",
                "reason": "command state must be observed before interrupt",
            }
        return {"action": "interrupt", "reason": "recovery deadlines elapsed"}
    return {"action": "none", "reason": "lane state has no liveness action"}


def liveness_decision_checksum(decision):
    if (
        not isinstance(decision, dict)
        or decision.get("action") not in LIVENESS_ACTIONS
        or not isinstance(decision.get("reason"), str)
    ):
        raise ValueError("liveness decision is invalid")
    encoded = json.dumps(
        decision,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def record_stall(
    run_dir,
    lane_id,
    agent_id,
    owner_handle,
    decided_at,
    decision,
    evidence_refs,
    reason,
):
    runtime = _runtime()
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_dir)
    _require_evidence_refs(evidence_refs)
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("stall reason is required")
    if not isinstance(decision, dict) or decision.get("action") != "suspect_stall":
        raise ValueError("stall recording requires a suspect_stall decision")
    decision_checksum = liveness_decision_checksum(decision)
    if not any(
        evidence.get("checksum") == decision_checksum
        for evidence in evidence_refs
        if isinstance(evidence, dict)
    ):
        raise ValueError("stall evidence must bind the liveness decision checksum")
    parse_timestamp(decided_at)

    def decide(state):
        require_run_owner(state, manifest_snapshot, owner_handle)
        require_run_state(state, {"running", "recovering"})
        lane = require_active_lane_owner(state, lane_id, agent_id)
        current_decision = evaluate_lane_liveness(
            lane,
            manifest_snapshot["manifest"],
            decided_at,
            command_alive=None,
        )
        if current_decision != decision or reason != decision["reason"]:
            raise CoordinatorConflict("liveness decision is stale or mismatched")
        event_type, source, target = require_intent_transition(
            LANE_INTENT_TRANSITIONS, "stall", lane["state"]
        )
        return [
            {
                "event_type": event_type,
                "lane_id": lane_id,
                "agent_id": agent_id,
                "from_state": source,
                "to_state": target,
                "timestamp": decided_at,
                "evidence_refs": evidence_refs,
                "reason": reason,
                "metadata": {"owner_epoch": state["owner_epoch"]},
            }
        ]

    state = runtime.mutate_receipt(run_dir, owner_handle, decide)
    return state["lanes"][lane_id]


def clear_stall(
    run_dir,
    lane_id,
    agent_id,
    owner_handle,
    decided_at,
    evidence_refs,
    reason,
):
    runtime = _runtime()
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_dir)
    runtime.validate_identifier(lane_id, "lane id")
    runtime.validate_identifier(agent_id, "agent id")
    parse_timestamp(decided_at)

    def decide(state):
        require_run_owner(state, manifest_snapshot, owner_handle)
        require_run_state(state, {"running", "recovering"})
        lane = require_active_lane_owner(state, lane_id, agent_id)
        event_type, source, target = require_intent_transition(
            LANE_INTENT_TRANSITIONS, "clear_stall", lane["state"]
        )
        require_fresh_evidence(lane, evidence_refs, reason)
        return [
            {
                "event_type": event_type,
                "lane_id": lane_id,
                "agent_id": agent_id,
                "from_state": source,
                "to_state": target,
                "timestamp": decided_at,
                "evidence_refs": evidence_refs,
                "reason": reason,
                "metadata": {"owner_epoch": state["owner_epoch"]},
            }
        ]

    state = runtime.mutate_receipt(run_dir, owner_handle, decide)
    return state["lanes"][lane_id]


def record_probe_sent(
    run_dir,
    lane_id,
    agent_id,
    owner_handle,
    decided_at,
    probe_deadline,
    evidence_refs,
):
    runtime = _runtime()
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_dir)
    runtime.validate_identifier(lane_id, "lane id")
    runtime.validate_identifier(agent_id, "agent id")
    decided = parse_timestamp(decided_at)
    probe = parse_timestamp(probe_deadline)
    _require_evidence_refs(evidence_refs)

    def decide(state):
        require_run_owner(state, manifest_snapshot, owner_handle)
        require_run_state(state, {"running", "recovering"})
        lane = require_active_lane_owner(state, lane_id, agent_id)
        event_type, source, target = require_intent_transition(
            LANE_INTENT_TRANSITIONS, "probe", lane["state"]
        )
        grace = timedelta(
            seconds=manifest_snapshot["manifest"]["liveness"]["probe_grace_seconds"]
        )
        if not decided < probe or probe - decided > grace:
            raise ValueError(
                "probe deadline must be within the manifest probe grace"
            )
        return [
            {
                "event_type": event_type,
                "lane_id": lane_id,
                "agent_id": agent_id,
                "from_state": source,
                "to_state": target,
                "timestamp": decided_at,
                "evidence_refs": evidence_refs,
                "metadata": {
                    "owner_epoch": state["owner_epoch"],
                    "probe_deadline": probe_deadline,
                },
            }
        ]

    state = runtime.mutate_receipt(run_dir, owner_handle, decide)
    return state["lanes"][lane_id]


def record_interrupt_result(
    run_dir,
    lane_id,
    agent_id,
    owner_handle,
    decided_at,
    evidence_refs,
):
    runtime = _runtime()
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_dir)
    runtime.validate_identifier(lane_id, "lane id")
    runtime.validate_identifier(agent_id, "agent id")
    parse_timestamp(decided_at)
    _require_evidence_refs(evidence_refs)
    if not any(
        evidence.get("kind") == "tool"
        and "interrupt" in evidence.get("summary", "").lower()
        for evidence in evidence_refs
        if isinstance(evidence, dict)
    ):
        raise ValueError("native interrupt tool evidence is required")

    def decide(state):
        require_run_owner(state, manifest_snapshot, owner_handle)
        require_run_state(state, {"running", "recovering"})
        lane = require_active_lane_owner(state, lane_id, agent_id)
        if lane["state"] != "recovering":
            raise CoordinatorConflict("interrupt requires a recovering lane")
        liveness = evaluate_lane_liveness(
            lane,
            manifest_snapshot["manifest"],
            decided_at,
            command_alive=True,
        )
        if liveness["action"] != "interrupt":
            raise CoordinatorConflict("liveness policy does not authorize interrupt")
        event_type, source, target = require_intent_transition(
            LANE_INTENT_TRANSITIONS, "interrupt", lane["state"]
        )
        return [
            {
                "event_type": event_type,
                "lane_id": lane_id,
                "agent_id": agent_id,
                "from_state": source,
                "to_state": target,
                "timestamp": decided_at,
                "evidence_refs": evidence_refs,
                "reason": "native interrupt recorded",
            }
        ]

    state = runtime.mutate_receipt(run_dir, owner_handle, decide)
    return state["lanes"][lane_id]


def _scope_is_equal_or_narrower(original, replacement):
    if not original:
        return not replacement
    return all(
        any(candidate == allowed or candidate.startswith(allowed + "/") for allowed in original)
        for candidate in replacement
    )


def reassign_lane(
    run_dir,
    lane_id,
    replacement_lane_id,
    replacement_agent_id,
    owner_handle,
    decided_at,
    replacement_assignment,
    replacement_write_scope,
    replacement_startup_ack_deadline,
    replacement_command_deadline,
    evidence_refs,
):
    runtime = _runtime()
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_dir)
    for value, field in (
        (lane_id, "lane id"),
        (replacement_lane_id, "replacement lane id"),
        (replacement_agent_id, "replacement agent id"),
    ):
        runtime.validate_identifier(value, field)
    if lane_id == replacement_lane_id:
        raise ValueError("replacement lane id must differ from original")
    if not isinstance(replacement_assignment, str) or not replacement_assignment.strip():
        raise ValueError("replacement assignment must be non-empty")
    if "checkpoint" not in replacement_assignment.lower():
        raise ValueError("replacement assignment must identify recovered checkpoint context")
    _require_evidence_refs(evidence_refs)
    if not any(
        evidence.get("kind") == "recovery"
        and "checkpoint" in evidence.get("summary", "").lower()
        for evidence in evidence_refs
        if isinstance(evidence, dict)
    ):
        raise ValueError("checkpoint recovery evidence is required")
    replacement_scope = runtime.canonicalize_write_scope(
        manifest_snapshot["run"]["repo_root"],
        replacement_write_scope,
        limits=manifest_snapshot["manifest"]["resource_limits"],
    )
    require_deadline_order(
        decided_at,
        replacement_startup_ack_deadline,
        replacement_command_deadline,
    )

    def decide(state):
        require_run_owner(state, manifest_snapshot, owner_handle)
        require_run_state(state, {"running", "recovering"})
        original = require_active_lane_owner(
            state, lane_id, state["lanes"].get(lane_id, {}).get("agent_id")
        )
        if original["state"] != "recovering":
            raise CoordinatorConflict("replacement requires a recovering lane")
        if original.get("last_event_type") != "agent_interrupted":
            raise CoordinatorConflict("replacement requires interrupt evidence")
        if replacement_agent_id == original["agent_id"]:
            raise ValueError("replacement agent must differ from original")
        if replacement_assignment == original.get("assignment"):
            raise ValueError("replacement assignment must describe resumed work")
        if not _scope_is_equal_or_narrower(
            original.get("write_scope", []), replacement_scope
        ):
            raise ValueError("replacement write scope must be equal or narrower")
        require_new_identifier(state["lanes"], replacement_lane_id)
        replacement_count = original.get("replacement_count", 0) + 1
        maximum = manifest_snapshot["manifest"]["liveness"]["max_replacements"]
        if replacement_count > maximum:
            raise CoordinatorConflict("replacement limit reached")
        checkpoint_digest = runtime.evidence_digest(evidence_refs)
        common = {
            "timestamp": decided_at,
            "evidence_refs": evidence_refs,
        }
        return [
            {
                **common,
                "event_type": "lane_reassigned",
                "lane_id": lane_id,
                "agent_id": original["agent_id"],
                "from_state": "recovering",
                "to_state": "replaced",
                "reason": "replacement checkpoint accepted",
                "metadata": {
                    "owner_epoch": state["owner_epoch"],
                    "replacement_count": replacement_count,
                    "previous_agent_id": original["agent_id"],
                    "replacement_lane_id": replacement_lane_id,
                    "replacement_agent_id": replacement_agent_id,
                    "replacement_assignment": replacement_assignment,
                    "replacement_write_scope": replacement_scope,
                    "replacement_fallback": original.get("fallback") or "main session",
                    "replacement_startup_ack_deadline": replacement_startup_ack_deadline,
                    "replacement_command_deadline": replacement_command_deadline,
                    "checkpoint_digest": checkpoint_digest,
                },
            },
            {
                **common,
                "event_type": "lane_created",
                "lane_id": replacement_lane_id,
                "agent_id": replacement_agent_id,
                "to_state": "pending",
                "metadata": {
                    "owner_epoch": state["owner_epoch"],
                    "assignment": replacement_assignment,
                    "write_scope": replacement_scope,
                    "fallback": original.get("fallback") or "main session",
                    "startup_ack_deadline": replacement_startup_ack_deadline,
                    "command_deadline": replacement_command_deadline,
                    "parent_lane_id": lane_id,
                    "replacement_count": replacement_count,
                },
            },
        ]

    state = runtime.mutate_receipt(run_dir, owner_handle, decide)
    return {
        "original": state["lanes"][lane_id],
        "replacement": state["lanes"][replacement_lane_id],
        "incomplete_replacements": state["incomplete_replacements"],
    }


def close_replacement_lineage(
    run_dir,
    lane_id,
    replacement_lane_id,
    owner_handle,
    decided_at,
    evidence_refs,
):
    runtime = _runtime()
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_dir)
    runtime.validate_identifier(lane_id, "lane id")
    runtime.validate_identifier(replacement_lane_id, "replacement lane id")
    parse_timestamp(decided_at)
    _require_evidence_refs(evidence_refs)

    def decide(state):
        require_run_owner(state, manifest_snapshot, owner_handle)
        require_run_state(state, {"running", "recovering"})
        original = state["lanes"].get(lane_id)
        replacement = state["lanes"].get(replacement_lane_id)
        if original is None or original["state"] != "replaced":
            raise CoordinatorConflict("original lane is not awaiting lineage close")
        if original.get("replacement_lane_id") != replacement_lane_id:
            raise CoordinatorConflict("replacement lane does not match reservation")
        if replacement is None or replacement["state"] not in {
            "completed",
            "failed",
            "blocked",
            "cancelled",
        }:
            raise CoordinatorConflict("replacement lane is not terminal")
        return [
            {
                "event_type": "replacement_lineage_closed",
                "lane_id": lane_id,
                "agent_id": original["agent_id"],
                "from_state": "replaced",
                "to_state": replacement["state"],
                "timestamp": decided_at,
                "evidence_refs": evidence_refs,
                "metadata": {
                    "owner_epoch": state["owner_epoch"],
                    "original_lane_id": lane_id,
                    "replacement_lane_id": replacement_lane_id,
                    "replacement_terminal_state": replacement["state"],
                },
            }
        ]

    state = runtime.mutate_receipt(run_dir, owner_handle, decide)
    return state["lanes"][lane_id]


def block_incomplete_replacement(
    run_dir,
    lane_id,
    replacement_lane_id,
    owner_handle,
    decided_at,
    evidence_refs,
):
    runtime = _runtime()
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_dir)
    runtime.validate_identifier(lane_id, "lane id")
    runtime.validate_identifier(replacement_lane_id, "replacement lane id")
    parse_timestamp(decided_at)
    _require_evidence_refs(evidence_refs)

    def decide(state):
        require_run_owner(state, manifest_snapshot, owner_handle)
        require_run_state(state, {"running", "recovering"})
        original = state["lanes"].get(lane_id)
        if original is None or original["state"] != "replaced":
            raise CoordinatorConflict("lane has no incomplete replacement")
        if original.get("replacement_lane_id") != replacement_lane_id:
            raise CoordinatorConflict("replacement reservation does not match")
        if replacement_lane_id in state["lanes"]:
            raise CoordinatorConflict("replacement lane already exists")
        if lane_id not in state["incomplete_replacements"]:
            raise CoordinatorConflict("replacement reservation is complete")
        checkpoint_digest = runtime.evidence_digest(
            original.get("evidence_refs", [])
        )
        return [
            {
                "event_type": "replacement_blocked",
                "lane_id": lane_id,
                "agent_id": original["agent_id"],
                "from_state": "replaced",
                "to_state": "blocked",
                "timestamp": decided_at,
                "evidence_refs": evidence_refs,
                "reason": "incomplete replacement cannot be safely recreated",
                "metadata": {
                    "owner_epoch": state["owner_epoch"],
                    "original_lane_id": lane_id,
                    "replacement_lane_id": replacement_lane_id,
                    "checkpoint_digest": checkpoint_digest,
                },
            }
        ]

    state = runtime.mutate_receipt(run_dir, owner_handle, decide)
    return state["lanes"][lane_id]


def repair_replacement(
    run_dir,
    lane_id,
    replacement_lane_id,
    owner_handle,
    decided_at,
    evidence_refs,
):
    runtime = _runtime()
    manifest_snapshot = runtime.load_run_manifest_snapshot(run_dir)
    runtime.validate_identifier(lane_id, "lane id")
    runtime.validate_identifier(replacement_lane_id, "replacement lane id")
    parse_timestamp(decided_at)
    _require_evidence_refs(evidence_refs)

    def decide(state):
        require_run_owner(state, manifest_snapshot, owner_handle)
        require_run_state(state, {"running", "recovering"})
        original = state["lanes"].get(lane_id)
        if original is None or original["state"] != "replaced":
            raise CoordinatorConflict("lane has no repairable replacement")
        if replacement_lane_id in state["lanes"]:
            raise CoordinatorConflict("replacement lane already exists")
        reservation = original.get("replacement_reservation")
        if not isinstance(reservation, dict):
            raise CoordinatorConflict(
                "legacy reservation lacks exact child proof; block it explicitly"
            )
        if reservation.get("replacement_lane_id") != replacement_lane_id:
            raise CoordinatorConflict("replacement reservation does not match")
        checkpoint_digest = reservation["checkpoint_digest"]
        if not any(
            evidence.get("checksum") == checkpoint_digest
            for evidence in evidence_refs
            if isinstance(evidence, dict)
        ):
            raise ValueError("checkpoint verification evidence is missing")
        return [
            {
                "event_type": "replacement_repaired",
                "lane_id": lane_id,
                "agent_id": original["agent_id"],
                "from_state": "replaced",
                "to_state": "replaced",
                "timestamp": decided_at,
                "evidence_refs": evidence_refs,
                "metadata": {
                    "owner_epoch": state["owner_epoch"],
                    "original_lane_id": lane_id,
                    "replacement_lane_id": replacement_lane_id,
                    "checkpoint_digest": checkpoint_digest,
                },
            },
            {
                "event_type": "lane_created",
                "lane_id": replacement_lane_id,
                "agent_id": reservation["replacement_agent_id"],
                "to_state": "pending",
                "timestamp": decided_at,
                "evidence_refs": evidence_refs,
                "metadata": {
                    "owner_epoch": state["owner_epoch"],
                    "assignment": reservation["replacement_assignment"],
                    "write_scope": reservation["replacement_write_scope"],
                    "fallback": reservation["replacement_fallback"],
                    "startup_ack_deadline": reservation[
                        "replacement_startup_ack_deadline"
                    ],
                    "command_deadline": reservation[
                        "replacement_command_deadline"
                    ],
                    "parent_lane_id": lane_id,
                    "replacement_count": reservation["replacement_count"],
                },
            },
        ]

    state = runtime.mutate_receipt(run_dir, owner_handle, decide)
    return state["lanes"][replacement_lane_id]
