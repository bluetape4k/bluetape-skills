import errno
import copy
import hashlib
import importlib.util
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path


class StateLockBusy(RuntimeError):
    pass


class ReceiptCorrupt(RuntimeError):
    def __init__(self, message, last_trusted_sequence=0, last_trusted_checksum=""):
        super().__init__(message)
        self.last_trusted_sequence = last_trusted_sequence
        self.last_trusted_checksum = last_trusted_checksum
        self.first_bad_sequence = last_trusted_sequence + 1
        self.effective_state = "blocked"


class IncompatibleManifest(RuntimeError):
    code = "incompatible_manifest"


_COMMAND_MUTATION = ContextVar("bluetape_command_mutation", default=None)


PHASE1_EVENT_TYPES = (
    "run_created",
    "plan_approved",
    "run_started",
    "topology_registered",
    "lane_created",
    "lane_started",
    "startup_ack",
    "heartbeat_observed",
    "lease_renewed",
    "stall_suspected",
    "probe_sent",
    "probe_acknowledged",
    "agent_interrupted",
    "lane_reassigned",
    "lane_recovered",
    "evidence_attached",
    "check_passed",
    "check_failed",
    "lane_completed",
    "lane_failed",
    "run_completed",
    "run_blocked",
    "candidate_proposed",
    "candidate_validated",
    "candidate_rejected",
)

PHASE2_EVENT_TYPES = (
    "run_created",
    "plan_approved",
    "run_started",
    "run_recovery_started",
    "run_recovery_finished",
    "run_failed",
    "run_blocked",
    "run_cancelled",
    "run_resumed",
    "topology_registered",
    "topology_component_removed",
    "lane_created",
    "lane_started",
    "startup_ack",
    "heartbeat_observed",
    "lease_renewed",
    "stall_suspected",
    "stall_cleared",
    "probe_sent",
    "probe_acknowledged",
    "agent_interrupted",
    "lane_reassigned",
    "replacement_repaired",
    "replacement_blocked",
    "replacement_lineage_closed",
    "lane_recovered",
    "evidence_attached",
    "check_passed",
    "check_failed",
    "lane_completed",
    "lane_failed",
    "lane_blocked",
    "lane_cancelled",
    "handoff_recorded",
    "live_report_recorded",
    "main_verification",
    "run_completed",
    "transaction_committed",
    "candidate_proposed",
    "candidate_validated",
    "candidate_rejected",
)

_EVENT_TYPES = set(PHASE2_EVENT_TYPES)
_EVIDENCE_KEYS = {"kind", "summary", "path", "checksum", "exit_status"}
_REQUIRED_RECEIPT_EVENT_KEYS = {
    "schema_version",
    "run_id",
    "lane_id",
    "agent_id",
    "sequence",
    "event_type",
    "from_state",
    "to_state",
    "timestamp",
    "owner_token",
    "manifest_hash",
    "previous_checksum",
    "checksum",
    "evidence_refs",
    "reason",
}
_OPTIONAL_RECEIPT_EVENT_KEYS = {"metadata"}
_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_UTC_PATTERN = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?Z$"
)

RESOURCE_LIMITS = {
    "max_receipt_line_bytes": 65536,
    "max_input_json_bytes": 1048576,
    "max_evidence_refs": 8,
    "max_components": 8,
    "max_lanes": 64,
    "max_component_checks": 8,
    "max_component_dependencies": 8,
    "max_write_scopes": 32,
    "max_identifier_chars": 128,
    "max_evidence_kind_chars": 32,
    "max_evidence_path_chars": 256,
    "max_evidence_summary_chars": 256,
    "max_description_chars": 500,
    "max_assignment_chars": 500,
}

_RECOVERY_FIELDS = {
    "recovery_original_run_id",
    "recovery_diagnose_checksum",
    "recovery_manifest_version",
    "recovery_manifest_hash",
    "recovery_quarantine_path",
    "recovery_quarantine_hash",
    "recovery_first_bad_sequence",
    "recovery_trusted_sequence",
    "recovery_trusted_checksum",
}

_ALLOWED_METADATA_BY_EVENT = {
    "run_created": _RECOVERY_FIELDS,
    "lane_created": {
        "assignment",
        "write_scope",
        "fallback",
        "startup_ack_deadline",
        "command_deadline",
        "replacement_count",
        "parent_lane_id",
    },
    "heartbeat_observed": {"evidence_digest"},
    "lease_renewed": {"silence_lease_deadline", "evidence_digest"},
    "lane_completed": {"changed_paths"},
    "probe_sent": {"probe_deadline"},
    "lane_reassigned": {
        "replacement_count",
        "previous_agent_id",
        "replacement_lane_id",
        "replacement_agent_id",
        "replacement_assignment",
        "replacement_write_scope",
        "replacement_fallback",
        "replacement_startup_ack_deadline",
        "replacement_command_deadline",
        "checkpoint_digest",
    },
    "replacement_repaired": {
        "original_lane_id",
        "replacement_lane_id",
        "checkpoint_digest",
    },
    "replacement_blocked": {
        "original_lane_id",
        "replacement_lane_id",
        "checkpoint_digest",
    },
    "replacement_lineage_closed": {
        "original_lane_id",
        "replacement_lane_id",
        "replacement_terminal_state",
    },
    "run_resumed": {"new_owner_fingerprint"},
    "transaction_committed": {"intents"},
    "handoff_recorded": {
        "report_kind",
        "report_path",
        "report_checksum",
        "report_receipt_head",
    },
    "live_report_recorded": {
        "report_kind",
        "report_path",
        "report_checksum",
        "report_receipt_head",
    },
    "topology_registered": {"components"},
    "topology_component_removed": {"component_id"},
    "check_passed": {"component_id", "check_id"},
    "check_failed": {"component_id", "check_id"},
    "evidence_attached": {"component_id", "coverage_state"},
}

_REQUIRED_METADATA_BY_EVENT = {
    "lane_created": {
        "assignment",
        "write_scope",
        "fallback",
        "startup_ack_deadline",
        "command_deadline",
        "parent_lane_id",
        "replacement_count",
    },
    "heartbeat_observed": {"evidence_digest"},
    "lease_renewed": {"silence_lease_deadline", "evidence_digest"},
    "lane_completed": {"changed_paths"},
    "probe_sent": {"probe_deadline"},
    "lane_reassigned": {
        "replacement_count",
        "previous_agent_id",
        "replacement_lane_id",
    },
    "replacement_repaired": {
        "original_lane_id",
        "replacement_lane_id",
        "checkpoint_digest",
    },
    "replacement_blocked": {
        "original_lane_id",
        "replacement_lane_id",
        "checkpoint_digest",
    },
    "replacement_lineage_closed": {
        "original_lane_id",
        "replacement_lane_id",
        "replacement_terminal_state",
    },
    "run_resumed": {"new_owner_fingerprint"},
    "transaction_committed": {"intents"},
    "handoff_recorded": {
        "report_kind",
        "report_path",
        "report_checksum",
        "report_receipt_head",
    },
    "live_report_recorded": {
        "report_kind",
        "report_path",
        "report_checksum",
        "report_receipt_head",
    },
    "topology_registered": {"components"},
    "topology_component_removed": {"component_id"},
    "check_passed": {"component_id", "check_id"},
    "check_failed": {"component_id", "check_id"},
    "evidence_attached": {"component_id", "coverage_state"},
}

_TRANSACTION_PAIRS = {
    ("heartbeat_observed", "lease_renewed"),
    ("lane_reassigned", "lane_created"),
    ("replacement_repaired", "lane_created"),
    ("main_verification", "run_completed"),
}

_INTENT_KEYS = {
    "event_type",
    "timestamp",
    "owner_epoch",
    "from_state",
    "to_state",
    "lane_id",
    "agent_id",
    "reason",
    "evidence_refs",
    "metadata",
}


def canonical_json(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def file_identity(path):
    target = Path(path)
    if target.is_symlink() or not target.is_file():
        raise ValueError("file identity requires a regular non-symlink file")
    digest = hashlib.sha256()
    size = 0
    with target.open("rb") as stream:
        while True:
            chunk = stream.read(64 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def file_sha256(path):
    return file_identity(path)[0]


@contextmanager
def coordinator_command(expected_head=None):
    if expected_head is not None and not _is_checksum(expected_head):
        raise ValueError("expected receipt head must be lowercase SHA-256")
    command = {"expected_head": expected_head, "state": None}
    token = _COMMAND_MUTATION.set(command)
    try:
        yield command
    finally:
        _COMMAND_MUTATION.reset(token)


def manifest_hash(manifest):
    return hashlib.sha256(canonical_json(manifest).encode("utf-8")).hexdigest()


def _manifest_family(version):
    if not isinstance(version, str):
        raise IncompatibleManifest("unsupported manifest version")
    parts = version.split(".")
    if len(parts) < 2 or not parts[0].isdigit() or not parts[1].isdigit():
        raise IncompatibleManifest("unsupported manifest version")
    family = parts[0] + "." + parts[1]
    if family not in {"1.0", "1.1"}:
        raise IncompatibleManifest("unsupported manifest version")
    return family


def validate_identifier(value, field="identifier"):
    if not isinstance(value, str) or _IDENTIFIER_PATTERN.fullmatch(value) is None:
        raise ValueError(field + " must match the identifier contract")
    return value


def _reject_symlink_components(path):
    candidate = Path(path).expanduser()
    if candidate.is_symlink():
        raise ValueError("state path contains a symlink")


def _reject_symlink_below(root, relative):
    current = Path(root)
    for part in Path(relative).parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("contained path includes a symlink")


def validate_state_path(root, relative):
    root_path = Path(root).expanduser()
    if root_path.is_symlink():
        raise ValueError("state root must not be a symlink")
    if not isinstance(relative, (str, os.PathLike)):
        raise ValueError("state path must be relative")
    relative_path = Path(relative)
    text = str(relative)
    if (
        relative_path.is_absolute()
        or not text
        or text in {".", ".."}
        or "\\" in text
        or any(part in {"", ".", ".."} for part in relative_path.parts)
        or any(ord(character) < 32 for character in text)
    ):
        raise ValueError("state path must be a contained canonical relative path")
    candidate = root_path / relative_path
    _reject_symlink_below(root_path, relative_path)
    root_resolved = root_path.resolve(strict=False)
    candidate_resolved = candidate.resolve(strict=False)
    try:
        candidate_resolved.relative_to(root_resolved)
    except ValueError as error:
        raise ValueError("state path escapes the selected root") from error
    return candidate_resolved


def validate_run_directory(run_dir):
    run_path = Path(run_dir).expanduser()
    validate_identifier(run_path.name, "run id")
    if run_path.is_symlink():
        raise ValueError("run directory must not be a symlink")
    runs_root = run_path.parent
    if runs_root.name != "runs":
        raise ValueError("run directory must be a direct child of state-root runs")
    state_root = runs_root.parent
    validate_secure_mode(state_root, 0o700, "state root")
    validate_secure_mode(runs_root, 0o700, "runs directory")
    validate_secure_mode(run_path, 0o700, "run directory")
    resolved = run_path.resolve(strict=True)
    if resolved.parent != runs_root.resolve(strict=True):
        raise ValueError("run directory escapes state-root runs")
    return resolved


def canonicalize_write_scope(repo_root, scopes, *, limits=None):
    limits = RESOURCE_LIMITS if limits is None else limits
    root = Path(repo_root).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("repo_root must be a directory")
    if not isinstance(scopes, list) or len(scopes) > limits["max_write_scopes"]:
        raise ValueError("write_scope must be a bounded list")
    canonical = []
    for scope in scopes:
        if (
            not isinstance(scope, str)
            or not scope
            or len(scope) > limits["max_evidence_path_chars"]
            or scope.startswith("/")
            or "\\" in scope
            or "*" in scope
            or "?" in scope
            or "[" in scope
            or any(ord(character) < 32 for character in scope)
        ):
            raise ValueError("write scope must be canonical and relative")
        path = Path(scope)
        if any(part in {"", ".", ".."} for part in path.parts):
            raise ValueError("write scope must not contain traversal")
        candidate = root / path
        _reject_symlink_below(root, path)
        resolved = candidate.resolve(strict=False)
        try:
            relative = resolved.relative_to(root)
        except ValueError as error:
            raise ValueError("write scope escapes repo_root") from error
        normalized = relative.as_posix()
        if normalized not in canonical:
            canonical.append(normalized)
    return canonical


def validate_secure_mode(path, expected_mode, kind="path"):
    target = Path(path)
    if target.is_symlink():
        raise ValueError(kind + " must not be a symlink")
    info = target.stat()
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise ValueError(kind + " must be owned by the current uid")
    if stat.S_IMODE(info.st_mode) != expected_mode:
        raise ValueError(kind + " does not have the required secure mode")
    return target


def _ensure_secure_directory(path):
    target = Path(path)
    _reject_symlink_components(target)
    if target.exists():
        if not target.is_dir():
            raise ValueError("secure directory path is not a directory")
        validate_secure_mode(target, 0o700, "directory")
        return target
    target.mkdir(mode=0o700, parents=False)
    os.chmod(target, 0o700)
    return validate_secure_mode(target, 0o700, "directory")


def _write_json_atomic(path, value):
    target = Path(path)
    if target.is_symlink():
        raise ValueError("atomic target must not be a symlink")
    temporary_path = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            dir=str(target.parent), prefix="." + target.name + ".", suffix=".tmp"
        )
        temporary_path = Path(temporary_name)
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as temporary:
            temporary.write(canonical_json(value))
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(str(temporary_path), str(target))
        os.chmod(target, 0o600)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def _create_owner_handle(owner_file, run_id, epoch=1):
    owner_path = Path(owner_file).expanduser()
    validate_identifier(owner_path.stem, "owner handle id")
    parent = owner_path.parent
    validate_secure_mode(parent, 0o700, "owner handle directory")
    if owner_path.exists() or owner_path.is_symlink():
        raise ValueError("owner handle already exists")
    token = uuid.uuid4().hex
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(str(owner_path), flags, 0o600)
    try:
        os.fchmod(descriptor, 0o600)
        payload = canonical_json({"run_id": run_id, "epoch": epoch, "token": token})
        os.write(descriptor, (payload + "\n").encode("utf-8"))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return {
        "path": owner_path,
        "token": token,
        "fingerprint": hashlib.sha256(token.encode("utf-8")).hexdigest(),
        "epoch": epoch,
    }


def read_owner_handle(owner_file, expected_run_id=None):
    owner_path = Path(owner_file).expanduser()
    validate_secure_mode(owner_path, 0o600, "owner handle")
    try:
        payload = json.loads(owner_path.read_text(encoding="utf-8"))
    except (OSError, TypeError, json.JSONDecodeError) as error:
        raise ValueError("owner handle is invalid") from error
    if not isinstance(payload, dict) or set(payload) != {"run_id", "epoch", "token"}:
        raise ValueError("owner handle fields are invalid")
    validate_identifier(payload["run_id"], "owner run id")
    if expected_run_id is not None and payload["run_id"] != expected_run_id:
        raise ValueError("owner handle belongs to another run")
    epoch = payload["epoch"]
    if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 1:
        raise ValueError("owner epoch must be a positive integer")
    token = payload["token"]
    if not isinstance(token, str) or not token:
        raise ValueError("owner handle token is invalid")
    return {
        "path": owner_path,
        "token": token,
        "fingerprint": hashlib.sha256(token.encode("utf-8")).hexdigest(),
        "epoch": epoch,
    }


def _read_contained_owner_handle(run_path, owner_file):
    run_dir = Path(run_path)
    handles_root = run_dir.parent.parent / "handles"
    validate_secure_mode(handles_root, 0o700, "owner handle directory")
    owner_path = Path(owner_file).expanduser()
    if owner_path.parent.resolve(strict=False) != handles_root.resolve(strict=True):
        raise ValueError("owner handle must be a direct child of state-root handles")
    validate_identifier(owner_path.stem, "owner handle id")
    return read_owner_handle(owner_path, expected_run_id=run_dir.name)


def discover_state_root(start=None, state_root=None, env=None, home=None):
    environment = os.environ if env is None else env
    home_path = Path.home() if home is None else Path(home)
    if state_root is not None:
        selected = Path(state_root).expanduser()
        if selected.is_symlink():
            raise ValueError("state root must not be a symlink")
        return selected.resolve()
    explicit = environment.get("BLUETAPE_STATE_ROOT")
    if explicit:
        selected = Path(explicit).expanduser()
        if selected.is_symlink():
            raise ValueError("state root must not be a symlink")
        return selected.resolve()
    current = Path.cwd() if start is None else Path(start)
    current = current.resolve()
    for candidate in (current,) + tuple(current.parents):
        state = candidate / ".bluetape"
        if (state / "config.json").is_file():
            return state.resolve()
    managed_workspace = home_path / "work" / "bluetape4k"
    if managed_workspace.is_dir():
        return (managed_workspace / ".bluetape").resolve()
    xdg = Path(environment.get("XDG_STATE_HOME", str(home_path / ".local" / "state")))
    return (xdg / "bluetape-skills").expanduser().resolve()


def _probe_pid(pid):
    try:
        os.kill(pid, 0)
        return "alive"
    except OSError as error:
        if error.errno == errno.ESRCH:
            return "dead"
        return "unknown"


def _write_exclusive_json(path, value):
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(str(path), flags, 0o600)
    try:
        os.fchmod(descriptor, 0o600)
        encoded = (canonical_json(value) + "\n").encode("utf-8")
        offset = 0
        while offset < len(encoded):
            written = os.write(descriptor, encoded[offset:])
            if written <= 0:
                raise OSError("exclusive JSON write made no progress")
            offset += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _claim_initializer(initializer_path, owner, probe):
    for _attempt in range(2):
        try:
            _write_exclusive_json(initializer_path, owner)
            return
        except FileExistsError as error:
            if initializer_path.is_symlink() or not initializer_path.is_file():
                raise StateLockBusy("state lock initializer is unsafe") from error
            validate_secure_mode(initializer_path, 0o600, "state lock initializer")
            age = datetime.now(timezone.utc).timestamp() - initializer_path.stat().st_mtime
            try:
                existing = json.loads(initializer_path.read_text(encoding="utf-8"))
                pid = existing.get("pid")
            except (OSError, TypeError, json.JSONDecodeError, AttributeError):
                pid = None
            if age < 30 or (
                isinstance(pid, int)
                and not isinstance(pid, bool)
                and probe(pid) != "dead"
            ):
                raise StateLockBusy("state lock initialization is active") from error
            retired = initializer_path.with_name(
                initializer_path.name + ".stale." + uuid.uuid4().hex
            )
            try:
                os.rename(str(initializer_path), str(retired))
            except FileNotFoundError as lost:
                raise StateLockBusy("state lock initializer changed") from lost
            retired.unlink(missing_ok=True)
    raise StateLockBusy("state lock initializer could not be claimed")


@contextmanager
def state_lock(lock_dir, pid_probe=None):
    lock_path = Path(lock_dir)
    owner_path = lock_path / "owner.json"
    initializer_path = lock_path.with_name("." + lock_path.name + ".initializing.json")
    probe = _probe_pid if pid_probe is None else pid_probe
    token = uuid.uuid4().hex
    owner = {
        "pid": os.getpid(),
        "session_id": os.getsid(0) if hasattr(os, "getsid") else None,
        "token": token,
        "created_at": _utc_now(),
    }
    if not lock_path.parent.exists():
        lock_path.parent.mkdir(mode=0o700, parents=True)
        os.chmod(lock_path.parent, 0o700)
    else:
        validate_secure_mode(lock_path.parent, 0o700, "lock parent directory")

    acquired = False
    if not lock_path.exists():
        _claim_initializer(initializer_path, owner, probe)
        try:
            lock_path.mkdir(mode=0o700)
            os.chmod(lock_path, 0o700)
            os.rename(str(initializer_path), str(owner_path))
            acquired = True
        except FileExistsError:
            initializer_path.unlink(missing_ok=True)

    if not acquired:
        if lock_path.is_symlink() or owner_path.is_symlink():
            raise StateLockBusy("state lock path is unsafe")
        try:
            validate_secure_mode(lock_path, 0o700, "state lock directory")
            if owner_path.exists():
                validate_secure_mode(owner_path, 0o600, "state lock owner")
        except (OSError, ValueError) as error:
            raise StateLockBusy("state lock path is insecure") from error
        empty_lock = False
        try:
            existing = json.loads(owner_path.read_text(encoding="utf-8"))
        except (OSError, TypeError, json.JSONDecodeError) as error:
            if initializer_path.exists() or initializer_path.is_symlink():
                if initializer_path.is_symlink() or not initializer_path.is_file():
                    raise StateLockBusy(
                        "state lock initializer is unsafe"
                    ) from error
                try:
                    validate_secure_mode(
                        initializer_path, 0o600, "state lock initializer"
                    )
                    initializer = json.loads(
                        initializer_path.read_text(encoding="utf-8")
                    )
                    initializer_pid = initializer.get("pid")
                except ValueError as unsafe:
                    raise StateLockBusy(
                        "state lock initializer is unsafe"
                    ) from unsafe
                except (OSError, TypeError, json.JSONDecodeError, AttributeError):
                    initializer_pid = None
                if (
                    isinstance(initializer_pid, int)
                    and not isinstance(initializer_pid, bool)
                    and probe(initializer_pid) != "dead"
                ):
                    raise StateLockBusy("state lock initialization is active") from error
            try:
                age_seconds = (
                    datetime.now(timezone.utc).timestamp() - lock_path.stat().st_mtime
                )
            except FileNotFoundError as lost:
                raise StateLockBusy("state lock changed during recovery") from lost
            if owner_path.exists() or age_seconds < 30:
                raise StateLockBusy("state lock owner is not readable yet") from error
            existing = None
            empty_lock = True
        if existing is not None:
            pid = existing.get("pid") if isinstance(existing, dict) else None
            if not isinstance(pid, int) or isinstance(pid, bool) or probe(pid) != "dead":
                raise StateLockBusy("state lock owner is live or unknown")

        claim_path = lock_path / ".reclaim.json"
        claim = {
            "pid": os.getpid(),
            "session_id": os.getsid(0) if hasattr(os, "getsid") else None,
            "nonce": token,
            "created_at": _utc_now(),
        }
        try:
            _write_exclusive_json(claim_path, claim)
        except FileNotFoundError as error:
            raise StateLockBusy("state lock recovery lost its election") from error
        except FileExistsError as error:
            try:
                if claim_path.is_symlink() or not claim_path.is_file():
                    raise StateLockBusy(
                        "state lock recovery claim is unsafe"
                    ) from error
                validate_secure_mode(claim_path, 0o600, "state lock recovery claim")
                claim_age = (
                    datetime.now(timezone.utc).timestamp()
                    - claim_path.stat().st_mtime
                )
                prior_claim = json.loads(claim_path.read_text(encoding="utf-8"))
                prior_pid = prior_claim.get("pid")
            except FileNotFoundError as lost:
                raise StateLockBusy("state lock recovery claim changed") from lost
            except (OSError, TypeError, json.JSONDecodeError, AttributeError):
                prior_pid = None
            if claim_age < 30 or (
                isinstance(prior_pid, int)
                and not isinstance(prior_pid, bool)
                and probe(prior_pid) != "dead"
            ):
                raise StateLockBusy("state lock recovery is already claimed") from error
            retired_claim = lock_path / (".reclaim.stale." + uuid.uuid4().hex)
            try:
                os.rename(str(claim_path), str(retired_claim))
            except FileNotFoundError as lost:
                raise StateLockBusy("state lock recovery claim changed") from lost
            retired_claim.unlink(missing_ok=True)
            try:
                _write_exclusive_json(claim_path, claim)
            except FileExistsError as lost:
                raise StateLockBusy("state lock recovery claim was reacquired") from lost

        try:
            confirmed = (
                json.loads(owner_path.read_text(encoding="utf-8"))
                if owner_path.exists()
                else None
            )
        except FileNotFoundError as lost:
            claim_path.unlink(missing_ok=True)
            raise StateLockBusy("state lock owner changed during recovery") from lost
        if confirmed != existing or (empty_lock and owner_path.exists()):
            claim_path.unlink(missing_ok=True)
            raise StateLockBusy("state lock owner changed during recovery")
        _claim_initializer(initializer_path, owner, probe)
        retired = lock_path.with_name(lock_path.name + ".retired." + uuid.uuid4().hex)
        try:
            os.rename(str(lock_path), str(retired))
            lock_path.mkdir(mode=0o700)
            os.chmod(lock_path, 0o700)
            os.rename(str(initializer_path), str(owner_path))
            acquired = True
        except FileNotFoundError as error:
            raise StateLockBusy("state lock recovery lost its election") from error
        except FileExistsError as error:
            raise StateLockBusy("state lock was reacquired during recovery") from error
        finally:
            initializer_path.unlink(missing_ok=True)
            if retired.exists():
                shutil.rmtree(retired)

    try:
        yield owner
    finally:
        if owner_path.is_file():
            current = json.loads(owner_path.read_text(encoding="utf-8"))
            if current.get("token") == token:
                shutil.rmtree(lock_path)


def _utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _validate_timestamp(value, field="timestamp", nullable=False):
    if value is None and nullable:
        return
    if not isinstance(value, str) or _UTC_PATTERN.fullmatch(value) is None:
        raise ValueError(field + " must be a UTC ISO-8601 timestamp ending in Z")


def _validate_evidence_refs(evidence_refs, limits=None):
    limits = RESOURCE_LIMITS if limits is None else limits
    if not isinstance(evidence_refs, list):
        raise ValueError("evidence_refs must be a list")
    if len(evidence_refs) > limits["max_evidence_refs"]:
        raise ValueError("evidence_refs must contain at most 8 entries")
    for evidence in evidence_refs:
        if not isinstance(evidence, dict):
            raise ValueError("evidence reference must be an object")
        if set(evidence) - _EVIDENCE_KEYS:
            raise ValueError("evidence reference contains unsupported fields")
        kind = evidence.get("kind")
        summary = evidence.get("summary")
        if (
            not isinstance(kind, str)
            or not kind
            or len(kind) > limits["max_evidence_kind_chars"]
        ):
            raise ValueError("evidence kind must be a bounded non-empty string")
        if (
            not isinstance(summary, str)
            or len(summary) > limits["max_evidence_summary_chars"]
        ):
            raise ValueError("evidence summary must be at most 256 characters")
        if "path" in evidence and (
            not isinstance(evidence["path"], str)
            or len(evidence["path"]) > limits["max_evidence_path_chars"]
        ):
            raise ValueError("evidence path must be a bounded string")
        if "checksum" in evidence and not _is_checksum(evidence["checksum"]):
            raise ValueError("evidence checksum must be lowercase SHA-256")
        if "exit_status" in evidence and (
            not isinstance(evidence["exit_status"], int)
            or isinstance(evidence["exit_status"], bool)
        ):
            raise ValueError("evidence exit_status must be an integer")


def evidence_digest(evidence_refs):
    _validate_evidence_refs(evidence_refs)
    return hashlib.sha256(canonical_json(evidence_refs).encode("utf-8")).hexdigest()


def _is_checksum(value):
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _event_checksum(event):
    payload = dict(event)
    payload.pop("checksum", None)
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _validate_topology_component(component, limits=None):
    limits = RESOURCE_LIMITS if limits is None else limits
    required_fields = {
        "id",
        "required",
        "description",
        "owner_lane",
        "required_checks",
        "dependencies",
        "evidence_refs",
        "coverage_state",
    }
    if not isinstance(component, dict) or set(component) != required_fields:
        raise ValueError("component metadata fields do not match contract")
    validate_identifier(component["id"], "component id")
    if not isinstance(component["required"], bool):
        raise ValueError("component required must be a boolean")
    description = component["description"]
    if (
        not isinstance(description, str)
        or not description
        or len(description) > limits["max_description_chars"]
    ):
        raise ValueError("component description is invalid")
    validate_identifier(component["owner_lane"], "component owner lane")
    for field, maximum in (
        ("required_checks", limits["max_component_checks"]),
        ("dependencies", limits["max_component_dependencies"]),
    ):
        values = component[field]
        if not isinstance(values, list) or len(values) > maximum:
            raise ValueError("component " + field + " exceeds its limit")
        for value in values:
            validate_identifier(value, "component " + field)
        if len(values) != len(set(values)):
            raise ValueError("component " + field + " contains duplicates")
    if component["evidence_refs"] != []:
        raise ValueError("topology snapshot evidence_refs must be empty")
    if component["coverage_state"] not in {"missing", "partial", "covered"}:
        raise ValueError("component coverage_state is invalid")


def _validate_recovery_provenance(metadata):
    validate_identifier(metadata["recovery_original_run_id"], "recovery run id")
    for field in (
        "recovery_diagnose_checksum",
        "recovery_manifest_hash",
        "recovery_quarantine_hash",
        "recovery_trusted_checksum",
    ):
        if not _is_checksum(metadata[field]):
            raise ValueError(field + " must be lowercase SHA-256")
    if (
        not isinstance(metadata["recovery_manifest_version"], str)
        or len(metadata["recovery_manifest_version"]) > 32
    ):
        raise ValueError("recovery manifest version is invalid")
    path = metadata["recovery_quarantine_path"]
    if (
        not isinstance(path, str)
        or len(path) > 256
        or Path(path).is_absolute()
        or ".." in Path(path).parts
        or not path.startswith("quarantine/")
    ):
        raise ValueError("recovery quarantine path must be contained")
    for field, minimum in (
        ("recovery_first_bad_sequence", 1),
        ("recovery_trusted_sequence", 0),
    ):
        value = metadata[field]
        if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
            raise ValueError(field + " is invalid")


def _validate_transaction_intents(intents, current_owner_epoch, limits=None):
    if not isinstance(intents, list) or len(intents) != 2:
        raise ValueError("transaction intents must contain exactly two events")
    pair = tuple(intent.get("event_type") if isinstance(intent, dict) else None for intent in intents)
    if pair not in _TRANSACTION_PAIRS:
        raise ValueError("transaction intent pair is unsupported")
    for intent in intents:
        if not isinstance(intent, dict) or set(intent) != _INTENT_KEYS:
            raise ValueError("transaction intent fields do not match contract")
        if intent["event_type"] == "transaction_committed":
            raise ValueError("transaction intent cannot contain a nested envelope")
        if intent["owner_epoch"] != current_owner_epoch:
            raise ValueError("transaction intent owner epoch does not match")
        _validate_timestamp(intent["timestamp"])
        for field in ("lane_id", "agent_id"):
            if intent[field] is not None:
                validate_identifier(intent[field], "transaction " + field)
        for field in ("from_state", "to_state"):
            value = intent[field]
            if value is not None and (not isinstance(value, str) or len(value) > 32):
                raise ValueError("transaction state is invalid")
        reason = intent["reason"]
        if reason is not None and (not isinstance(reason, str) or len(reason) > 500):
            raise ValueError("transaction reason is invalid")
        _validate_evidence_refs(intent["evidence_refs"], limits=limits)
        metadata = intent["metadata"]
        _validate_event_metadata(
            intent["event_type"],
            metadata,
            manifest_version="1.1",
            current_owner_epoch=current_owner_epoch,
            nested=True,
            limits=limits,
        )


def _validate_event_metadata(
    event_type,
    metadata,
    manifest_version="1.1",
    current_owner_epoch=None,
    nested=False,
    limits=None,
):
    limits = RESOURCE_LIMITS if limits is None else limits
    family = manifest_version if manifest_version in {"1.0", "1.1"} else _manifest_family(manifest_version)
    if family == "1.0":
        if metadata is not None:
            raise ValueError("manifest 1.0 event metadata is unsupported")
        return
    if not isinstance(metadata, dict):
        raise ValueError("manifest 1.1 event metadata is required")
    allowed = _ALLOWED_METADATA_BY_EVENT.get(event_type, set()) | {"owner_epoch"}
    unknown = sorted(set(metadata) - allowed)
    if unknown:
        raise ValueError("unsupported metadata fields: " + ", ".join(unknown))
    epoch = metadata.get("owner_epoch")
    if (
        not isinstance(epoch, int)
        or isinstance(epoch, bool)
        or epoch < 1
        or epoch != current_owner_epoch
    ):
        raise ValueError("owner_epoch must match the current positive epoch")
    required = _REQUIRED_METADATA_BY_EVENT.get(event_type, set()) | {"owner_epoch"}
    missing = sorted(required - set(metadata))
    if missing:
        raise ValueError("required metadata fields missing: " + ", ".join(missing))
    present_recovery = set(metadata) & _RECOVERY_FIELDS
    if event_type == "run_created":
        if present_recovery and present_recovery != _RECOVERY_FIELDS:
            raise ValueError("recovery run provenance must be complete")
        if present_recovery:
            _validate_recovery_provenance(metadata)
    for field in (
        "startup_ack_deadline",
        "silence_lease_deadline",
        "command_deadline",
        "probe_deadline",
        "replacement_startup_ack_deadline",
        "replacement_command_deadline",
    ):
        if field in metadata:
            _validate_timestamp(metadata[field], field, nullable=field == "command_deadline")
    for scope_field in ("write_scope", "replacement_write_scope", "changed_paths"):
        if scope_field not in metadata:
            continue
        values = metadata[scope_field]
        if not isinstance(values, list) or len(values) > limits["max_write_scopes"]:
            raise ValueError(scope_field + " must be a bounded list")
        for value in values:
            if not isinstance(value, str) or not value or len(value) > 256:
                raise ValueError(scope_field + " must contain bounded strings")
    for field in (
        "assignment",
        "fallback",
        "replacement_assignment",
        "replacement_fallback",
    ):
        if field in metadata and (
            not isinstance(metadata[field], str)
            or len(metadata[field]) > limits["max_assignment_chars"]
        ):
            raise ValueError(field + " must be at most 500 characters")
    if "replacement_count" in metadata and (
        not isinstance(metadata["replacement_count"], int)
        or isinstance(metadata["replacement_count"], bool)
        or metadata["replacement_count"] < 0
    ):
        raise ValueError("replacement_count must be a non-negative integer")
    for field in (
        "previous_agent_id",
        "replacement_agent_id",
        "original_lane_id",
        "replacement_lane_id",
        "parent_lane_id",
        "component_id",
        "check_id",
    ):
        if field in metadata and metadata[field] is not None:
            validate_identifier(metadata[field], field)
    for field in (
        "evidence_digest",
        "checkpoint_digest",
        "new_owner_fingerprint",
        "report_checksum",
        "report_receipt_head",
    ):
        if field in metadata and metadata[field] is not None and not _is_checksum(metadata[field]):
            raise ValueError(field + " must be lowercase SHA-256")
    if "replacement_terminal_state" in metadata and metadata["replacement_terminal_state"] not in {
        "completed",
        "failed",
        "blocked",
        "cancelled",
    }:
        raise ValueError("replacement terminal state is invalid")
    if "coverage_state" in metadata and metadata["coverage_state"] not in {
        "missing",
        "partial",
        "covered",
    }:
        raise ValueError("coverage_state is invalid")
    if "report_kind" in metadata and metadata["report_kind"] not in {
        "fresh_session_handoff",
        "live_apply",
    }:
        raise ValueError("report_kind is invalid")
    if "report_path" in metadata:
        path = metadata["report_path"]
        if (
            not isinstance(path, str)
            or len(path) > 256
            or Path(path).is_absolute()
            or ".." in Path(path).parts
            or not path.startswith("reports/")
        ):
            raise ValueError("report_path must be contained")
    if "components" in metadata:
        components = metadata["components"]
        if not isinstance(components, list) or len(components) > limits["max_components"]:
            raise ValueError("components must be a bounded list")
        for component in components:
            _validate_topology_component(component, limits=limits)
    if "intents" in metadata:
        if nested:
            raise ValueError("transaction intent cannot contain nested intents")
        _validate_transaction_intents(
            metadata["intents"], current_owner_epoch, limits=limits
        )


def _validate_receipt_event_contract(
    event,
    manifest_version="1.0",
    current_owner_epoch=None,
    allowed_event_types=None,
    limits=None,
):
    family = manifest_version if manifest_version in {"1.0", "1.1"} else _manifest_family(manifest_version)
    keys = set(event)
    if not _REQUIRED_RECEIPT_EVENT_KEYS <= keys or keys - (
        _REQUIRED_RECEIPT_EVENT_KEYS | _OPTIONAL_RECEIPT_EVENT_KEYS
    ):
        raise ValueError("receipt event fields do not match the schema")
    if family == "1.0" and keys != _REQUIRED_RECEIPT_EVENT_KEYS:
        raise ValueError("manifest 1.0 receipt fields do not match the schema")
    if event.get("schema_version") != 1:
        raise ValueError("receipt event schema version is unsupported")
    validate_identifier(event.get("run_id"), "receipt run id")
    for field in ("lane_id", "agent_id"):
        if event.get(field) is not None:
            validate_identifier(event[field], "receipt " + field)
    for field in ("from_state", "to_state"):
        value = event.get(field)
        if value is not None and (not isinstance(value, str) or len(value) > 32):
            raise ValueError("receipt state field is invalid")
    sequence = event.get("sequence")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        raise ValueError("receipt sequence must be a positive integer")
    event_type = event.get("event_type")
    allowed = _EVENT_TYPES if allowed_event_types is None else set(allowed_event_types)
    if event_type not in allowed:
        raise ValueError("receipt event type is unsupported")
    _validate_timestamp(event.get("timestamp"))
    if not isinstance(event.get("owner_token"), str) or not event["owner_token"]:
        raise ValueError("receipt owner token must be a non-empty string")
    if family == "1.1" and not _is_checksum(event["owner_token"]):
        raise ValueError("receipt owner fingerprint is invalid")
    if not _is_checksum(event.get("manifest_hash")):
        raise ValueError("receipt manifest hash is invalid")
    previous_checksum = event.get("previous_checksum")
    if previous_checksum != "" and not _is_checksum(previous_checksum):
        raise ValueError("receipt previous checksum is invalid")
    if not _is_checksum(event.get("checksum")):
        raise ValueError("receipt checksum is invalid")
    _validate_evidence_refs(event.get("evidence_refs"), limits=limits)
    reason = event.get("reason")
    if reason is not None and (not isinstance(reason, str) or len(reason) > 500):
        raise ValueError("receipt reason must be at most 500 characters")
    _validate_event_metadata(
        event_type,
        event.get("metadata"),
        family,
        current_owner_epoch=current_owner_epoch,
        limits=limits,
    )


def _snapshot_from_events(events):
    if not events:
        raise ReceiptCorrupt("receipt contains no events")
    state = "planned"
    inferred_states = {
        "run_created": "planned",
        "plan_approved": "approved",
        "run_started": "running",
        "run_recovery_started": "recovering",
        "run_recovery_finished": "running",
        "run_completed": "completed",
        "run_failed": "failed",
        "run_blocked": "blocked",
        "run_cancelled": "cancelled",
    }
    for event in events:
        if event.get("lane_id") is None:
            if event.get("to_state") is not None:
                state = event["to_state"]
            elif event["event_type"] in inferred_states:
                state = inferred_states[event["event_type"]]
    latest = events[-1]
    return {
        "schema_version": 1,
        "run_id": latest["run_id"],
        "manifest_hash": latest["manifest_hash"],
        "state": state,
        "last_event_type": latest["event_type"],
        "last_sequence": latest["sequence"],
        "last_checksum": latest["checksum"],
        "updated_at": latest["timestamp"],
    }


def _append_json_line(path, event):
    target = Path(path)
    if target.is_symlink():
        raise ValueError("receipt path must not be a symlink")
    encoded = (canonical_json(event) + "\n").encode("utf-8")
    flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(str(target), flags, 0o600)
    try:
        os.fchmod(descriptor, 0o600)
        offset = 0
        while offset < len(encoded):
            written = os.write(descriptor, encoded[offset:])
            if written <= 0:
                raise OSError("receipt append made no progress")
            offset += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def append_receipt_event(
    run_dir,
    event_type,
    owner_token=None,
    manifest_hash=None,
    evidence_refs=None,
    from_state=None,
    to_state=None,
    lane_id=None,
    agent_id=None,
    reason=None,
    timestamp=None,
    metadata=None,
    owner_handle=None,
):
    run_path = Path(run_dir)
    receipt_path = run_path / "receipt.jsonl"
    lock_path = run_path / "locks" / "receipt"
    manifest_snapshot = load_run_manifest_snapshot(run_path)
    family = _manifest_family(manifest_snapshot["manifest"]["manifest_version"])
    limits = manifest_snapshot["manifest"].get("resource_limits", RESOURCE_LIMITS)
    allowed_events = manifest_snapshot["manifest"]["receipt"]["event_types"]
    if event_type not in allowed_events:
        raise ValueError("run manifest does not allow event")
    if manifest_snapshot["manifest_hash"] != manifest_hash:
        raise ReceiptCorrupt("run manifest hash does not match receipt event")
    if family == "1.1":
        if owner_token is not None:
            raise ValueError("manifest 1.1 accepts owner credentials only from owner_file")
        if owner_handle is None:
            raise ValueError("manifest 1.1 requires owner_file")
        owner = _read_contained_owner_handle(run_path, owner_handle)
        run_owner = manifest_snapshot["run"] or {}
        if (
            owner["fingerprint"] != run_owner.get("owner_fingerprint")
            or owner["epoch"] != run_owner.get("owner_epoch")
        ):
            raise StateLockBusy("owner handle does not match the current run owner")
        receipt_owner = owner["fingerprint"]
        current_epoch = owner["epoch"]
    else:
        if not isinstance(owner_token, str) or not owner_token:
            raise ValueError("owner_token must be a non-empty string")
        receipt_owner = owner_token
        current_epoch = None
    evidence_refs = [] if evidence_refs is None else evidence_refs
    _validate_evidence_refs(evidence_refs, limits=limits)
    if reason is not None and (not isinstance(reason, str) or len(reason) > 500):
        raise ValueError("reason must be at most 500 characters")
    _validate_event_metadata(event_type, metadata, family, current_epoch)
    with state_lock(lock_path):
        events = verify_receipt(run_path) if receipt_path.is_file() else []
        previous = events[-1]["checksum"] if events else ""
        event = {
            "schema_version": 1,
            "run_id": run_path.name,
            "lane_id": lane_id,
            "agent_id": agent_id,
            "sequence": len(events) + 1,
            "event_type": event_type,
            "from_state": from_state,
            "to_state": to_state,
            "timestamp": timestamp or _utc_now(),
            "owner_token": receipt_owner,
            "manifest_hash": manifest_hash,
            "previous_checksum": previous,
            "checksum": "",
            "evidence_refs": evidence_refs,
            "reason": reason,
        }
        if metadata is not None:
            event["metadata"] = metadata
        event["checksum"] = _event_checksum(event)
        _validate_receipt_event_contract(
            event,
            manifest_version=family,
            current_owner_epoch=current_epoch,
            allowed_event_types=allowed_events,
            limits=limits,
        )
        encoded = canonical_json(event).encode("utf-8")
        if len(encoded) > limits["max_receipt_line_bytes"]:
            raise ValueError("receipt event exceeds max_receipt_line_bytes")
        _append_json_line(receipt_path, event)
        _write_json_atomic(run_path / "run.json", _snapshot_from_events(events + [event]))
        return event


def _iter_verified_receipt(run_path, manifest_snapshot):
    receipt_path = run_path / "receipt.jsonl"
    family = _manifest_family(manifest_snapshot["manifest"]["manifest_version"])
    limits = manifest_snapshot["manifest"].get("resource_limits", RESOURCE_LIMITS)
    allowed_events = manifest_snapshot["manifest"]["receipt"]["event_types"]
    if not receipt_path.is_file() or receipt_path.is_symlink():
        raise ReceiptCorrupt("receipt is missing or unsafe")
    expected_previous = ""
    expected_run_id = run_path.name
    expected_manifest_hash = manifest_snapshot["manifest_hash"]
    current_fingerprint = None
    current_epoch = None
    if family == "1.1":
        run_owner = manifest_snapshot["run"] or {}
        current_fingerprint = run_owner.get("owner_fingerprint")
        current_epoch = run_owner.get("initial_owner_epoch", 1)
    with receipt_path.open("rb") as stream:
        index = 0
        while True:
            line = stream.readline(limits["max_receipt_line_bytes"] + 2)
            if not line:
                break
            index += 1
            trusted_sequence = index - 1
            trusted_checksum = expected_previous
            if len(line) > limits["max_receipt_line_bytes"] + 1:
                raise ReceiptCorrupt(
                    "receipt corruption at sequence " + str(index) + ": event too large",
                    trusted_sequence,
                    trusted_checksum,
                )
            if not line.endswith(b"\n"):
                raise ReceiptCorrupt(
                    "receipt corruption at sequence "
                    + str(index)
                    + ": incomplete final event",
                    trusted_sequence,
                    trusted_checksum,
                )
            if len(line) - 1 > limits["max_receipt_line_bytes"]:
                raise ReceiptCorrupt(
                    "receipt corruption at sequence " + str(index) + ": event too large",
                    trusted_sequence,
                    trusted_checksum,
                )
            try:
                event = json.loads(line)
            except (TypeError, UnicodeDecodeError, json.JSONDecodeError) as error:
                raise ReceiptCorrupt(
                    "receipt corruption at sequence " + str(index) + ": invalid JSON",
                    trusted_sequence,
                    trusted_checksum,
                ) from error
            if not isinstance(event, dict):
                raise ReceiptCorrupt(
                    "receipt corruption at sequence " + str(index) + ": invalid event",
                    trusted_sequence,
                    trusted_checksum,
                )
            try:
                _validate_receipt_event_contract(
                    event,
                    manifest_version=family,
                    current_owner_epoch=current_epoch,
                    allowed_event_types=allowed_events,
                    limits=limits,
                )
            except ValueError as error:
                raise ReceiptCorrupt(
                    "receipt corruption at sequence "
                    + str(index)
                    + ": event contract mismatch",
                    trusted_sequence,
                    trusted_checksum,
                ) from error
            if event.get("sequence") != index:
                raise ReceiptCorrupt(
                    "receipt corruption at sequence " + str(index) + ": sequence mismatch",
                    trusted_sequence,
                    trusted_checksum,
                )
            if event.get("run_id") != expected_run_id:
                raise ReceiptCorrupt(
                    "receipt corruption at sequence " + str(index) + ": run id mismatch",
                    trusted_sequence,
                    trusted_checksum,
                )
            if event.get("manifest_hash") != expected_manifest_hash:
                raise ReceiptCorrupt(
                    "receipt corruption at sequence " + str(index) + ": manifest hash mismatch",
                    trusted_sequence,
                    trusted_checksum,
                )
            if family == "1.1" and event.get("owner_token") != current_fingerprint:
                raise ReceiptCorrupt(
                    "receipt corruption at sequence " + str(index) + ": owner mismatch",
                    trusted_sequence,
                    trusted_checksum,
                )
            if event.get("previous_checksum") != expected_previous:
                raise ReceiptCorrupt(
                    "receipt corruption at sequence "
                    + str(index)
                    + ": previous checksum mismatch",
                    trusted_sequence,
                    trusted_checksum,
                )
            if event.get("checksum") != _event_checksum(event):
                raise ReceiptCorrupt(
                    "receipt corruption at sequence " + str(index) + ": checksum mismatch",
                    trusted_sequence,
                    trusted_checksum,
                )
            expected_previous = event["checksum"]
            yield event
            if family == "1.1" and event["event_type"] == "run_resumed":
                current_fingerprint = event["metadata"]["new_owner_fingerprint"]
                current_epoch += 1


def iter_verified_receipt(run_dir):
    run_path = Path(run_dir)
    manifest_snapshot = load_run_manifest_snapshot(run_path)
    return _iter_verified_receipt(run_path, manifest_snapshot)


def verify_receipt(run_dir):
    events = list(iter_verified_receipt(run_dir))
    if not events:
        raise ReceiptCorrupt("receipt contains no events")
    return events


def verify_receipt_summary(run_dir):
    event_count = 0
    last_event = None
    for event in iter_verified_receipt(run_dir):
        event_count += 1
        last_event = event
    if last_event is None:
        raise ReceiptCorrupt("receipt contains no events")
    return {"event_count": event_count, "last_event": last_event}


def rebuild_run_snapshot(run_dir):
    run_path = Path(run_dir)
    snapshot = _snapshot_from_events(verify_receipt(run_path))
    _write_json_atomic(run_path / "run.json", snapshot)
    return snapshot


_COORDINATOR_MODULE = None


def _load_coordinator_module():
    global _COORDINATOR_MODULE
    if _COORDINATOR_MODULE is not None:
        return _COORDINATOR_MODULE
    if "bluetape_coordinator" in sys.modules:
        _COORDINATOR_MODULE = sys.modules["bluetape_coordinator"]
        return _COORDINATOR_MODULE
    module_path = Path(__file__).with_name("bluetape_coordinator.py")
    spec = importlib.util.spec_from_file_location(
        "bluetape_coordinator", module_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("coordinator module cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    _COORDINATOR_MODULE = module
    return _COORDINATOR_MODULE


def _public_coordinator_state(state):
    public = copy.deepcopy(state)
    public.pop("_receipt_owner_value", None)
    return public


def _run_snapshot_from_coordinator(run_path, manifest_snapshot, state):
    generated = {
        "schema_version": 1,
        "run_id": run_path.name,
        "manifest_hash": manifest_snapshot["manifest_hash"],
        "state": state["run_state"],
        "last_event_type": state["last_event_type"],
        "last_sequence": state["last_sequence"],
        "last_checksum": state["last_checksum"],
        "updated_at": state["updated_at"],
        "coordinator": {
            "cache_version": 1,
            "state": _public_coordinator_state(state),
        },
    }
    if _manifest_family(manifest_snapshot["manifest"]["manifest_version"]) != "1.0":
        return generated
    cache_path = run_path / "run.json"
    if not cache_path.is_file() or cache_path.is_symlink():
        return generated
    try:
        legacy = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, TypeError, json.JSONDecodeError) as error:
        raise ReceiptCorrupt("Phase 1 run cache is invalid") from error
    if not isinstance(legacy, dict):
        raise ReceiptCorrupt("Phase 1 run cache must be an object")
    preserved = copy.deepcopy(legacy)
    preserved["coordinator"] = generated["coordinator"]
    return preserved


def _write_changed_lane_caches(run_path, before, after):
    lanes_path = run_path / "lanes"
    _ensure_secure_directory(lanes_path)
    changed = {
        lane_id
        for lane_id in set(before) | set(after)
        if before.get(lane_id) != after.get(lane_id)
    }
    for lane_id in sorted(changed):
        validate_identifier(lane_id, "lane cache id")
        cache_path = lanes_path / (lane_id + ".json")
        if lane_id in after:
            _write_json_atomic(cache_path, after[lane_id])
        elif cache_path.is_file() and not cache_path.is_symlink():
            cache_path.unlink()


def _prepare_coordinator_cache_paths(run_path, lane_ids):
    run_cache = Path(run_path) / "run.json"
    if run_cache.exists() or run_cache.is_symlink():
        validate_secure_mode(run_cache, 0o600, "run cache")
    lanes_path = _ensure_secure_directory(Path(run_path) / "lanes")
    for lane_id in lane_ids:
        validate_identifier(lane_id, "lane cache id")
        cache_path = lanes_path / (lane_id + ".json")
        if cache_path.exists() or cache_path.is_symlink():
            validate_secure_mode(cache_path, 0o600, "lane cache")


def rebuild_coordinator_snapshots(run_dir):
    run_path = Path(run_dir)
    manifest_snapshot = load_run_manifest_snapshot(run_path)
    coordinator = _load_coordinator_module()
    state = coordinator.replay_coordinator_state(
        _iter_verified_receipt(run_path, manifest_snapshot), manifest_snapshot
    )
    snapshot = _run_snapshot_from_coordinator(run_path, manifest_snapshot, state)
    _write_json_atomic(run_path / "run.json", snapshot)
    lanes_path = run_path / "lanes"
    _ensure_secure_directory(lanes_path)
    for lane_id, lane in sorted(state["lanes"].items()):
        validate_identifier(lane_id, "lane cache id")
        _write_json_atomic(lanes_path / (lane_id + ".json"), lane)
    for cache_path in lanes_path.glob("*.json"):
        if cache_path.is_symlink() or not cache_path.is_file():
            continue
        lane_id = cache_path.stem
        try:
            validate_identifier(lane_id, "lane cache id")
        except ValueError:
            continue
        if lane_id not in state["lanes"]:
            cache_path.unlink()
    return snapshot


def _normalize_intent(intent, owner_epoch, limits=None):
    if not isinstance(intent, dict):
        raise ValueError("receipt mutation intent must be an object")
    normalized = {
        "event_type": intent.get("event_type"),
        "timestamp": intent.get("timestamp") or _utc_now(),
        "owner_epoch": intent.get("owner_epoch", owner_epoch),
        "from_state": intent.get("from_state"),
        "to_state": intent.get("to_state"),
        "lane_id": intent.get("lane_id"),
        "agent_id": intent.get("agent_id"),
        "reason": intent.get("reason"),
        "evidence_refs": intent.get("evidence_refs", []),
        "metadata": copy.deepcopy(intent.get("metadata", {"owner_epoch": owner_epoch})),
    }
    extra = set(intent) - set(normalized)
    if extra:
        raise ValueError("receipt mutation intent contains unsupported fields")
    if normalized["owner_epoch"] != owner_epoch:
        raise ValueError("receipt mutation intent owner epoch is stale")
    if normalized["metadata"].get("owner_epoch") != owner_epoch:
        raise ValueError("receipt mutation metadata owner epoch is stale")
    _validate_timestamp(normalized["timestamp"])
    _validate_evidence_refs(normalized["evidence_refs"], limits=limits)
    _validate_event_metadata(
        normalized["event_type"],
        normalized["metadata"],
        "1.1",
        owner_epoch,
        limits=limits,
    )
    return normalized


def mutate_receipt(run_dir, owner_handle, decide_events, *, expected_head=None):
    """Lock, replay once, CAS, append one event envelope, and rebuild caches."""
    run_path = validate_run_directory(run_dir)
    manifest_snapshot = load_run_manifest_snapshot(run_path)
    family = _manifest_family(manifest_snapshot["manifest"]["manifest_version"])
    if family != "1.1":
        raise IncompatibleManifest("coordinator mutation requires manifest 1.1")
    owner = _read_contained_owner_handle(run_path, owner_handle)
    coordinator = _load_coordinator_module()
    lock_path = run_path / "locks" / "receipt"
    receipt_path = run_path / "receipt.jsonl"
    command = _COMMAND_MUTATION.get()
    if expected_head is None and command is not None:
        expected_head = command["expected_head"]
    with state_lock(lock_path):
        state = coordinator.replay_coordinator_state(
            _iter_verified_receipt(run_path, manifest_snapshot), manifest_snapshot
        )
        if (
            owner["fingerprint"] != state["owner_fingerprint"]
            or owner["epoch"] != state["owner_epoch"]
        ):
            raise StateLockBusy("owner handle does not match the current run owner")
        if expected_head is not None and state["last_checksum"] != expected_head:
            raise coordinator.CoordinatorConflict("receipt head changed before mutation")
        before_lanes = copy.deepcopy(state["lanes"])
        decided = decide_events(copy.deepcopy(state))
        if not isinstance(decided, list) or len(decided) not in {1, 2}:
            raise ValueError("coordinator mutation must return one or two intents")
        limits = manifest_snapshot["manifest"]["resource_limits"]
        intents = [
            _normalize_intent(intent, owner["epoch"], limits=limits)
            for intent in decided
        ]
        if len(intents) == 2:
            _validate_transaction_intents(intents, owner["epoch"], limits=limits)
            event_type = "transaction_committed"
            lane_id = None
            agent_id = None
            from_state = None
            to_state = None
            reason = None
            evidence_refs = []
            timestamp = intents[-1]["timestamp"]
            metadata = {"owner_epoch": owner["epoch"], "intents": intents}
        else:
            intent = intents[0]
            event_type = intent["event_type"]
            lane_id = intent["lane_id"]
            agent_id = intent["agent_id"]
            from_state = intent["from_state"]
            to_state = intent["to_state"]
            reason = intent["reason"]
            evidence_refs = intent["evidence_refs"]
            timestamp = intent["timestamp"]
            metadata = intent["metadata"]
        allowed_events = manifest_snapshot["manifest"]["receipt"]["event_types"]
        if event_type not in allowed_events:
            raise ValueError("run manifest does not allow event")
        event = {
            "schema_version": 1,
            "run_id": run_path.name,
            "lane_id": lane_id,
            "agent_id": agent_id,
            "sequence": state["last_sequence"] + 1,
            "event_type": event_type,
            "from_state": from_state,
            "to_state": to_state,
            "timestamp": timestamp,
            "owner_token": owner["fingerprint"],
            "manifest_hash": manifest_snapshot["manifest_hash"],
            "previous_checksum": state["last_checksum"],
            "checksum": "",
            "evidence_refs": evidence_refs,
            "reason": reason,
            "metadata": metadata,
        }
        event["checksum"] = _event_checksum(event)
        _validate_receipt_event_contract(
            event,
            manifest_version="1.1",
            current_owner_epoch=owner["epoch"],
            allowed_event_types=allowed_events,
            limits=limits,
        )
        if len(canonical_json(event).encode("utf-8")) > limits["max_receipt_line_bytes"]:
            raise ValueError("receipt event exceeds max_receipt_line_bytes")
        next_state = copy.deepcopy(state)
        coordinator.apply_event(next_state, event, manifest_snapshot["manifest"])
        _prepare_coordinator_cache_paths(
            run_path, set(before_lanes) | set(next_state["lanes"])
        )
        _append_json_line(receipt_path, event)
        snapshot = _run_snapshot_from_coordinator(
            run_path, manifest_snapshot, next_state
        )
        try:
            _write_json_atomic(run_path / "run.json", snapshot)
            _write_changed_lane_caches(run_path, before_lanes, next_state["lanes"])
        except OSError:
            # Receipt is authoritative; derived caches are rebuilt on demand.
            pass
        public_state = _public_coordinator_state(next_state)
        if command is not None:
            command["state"] = copy.deepcopy(public_state)
        return public_state


def load_run_manifest_snapshot(run_dir):
    run_path = Path(run_dir)
    if run_path.is_symlink():
        raise ReceiptCorrupt("run directory snapshot is unsafe")
    manifest_path = run_path / "manifest.json"
    if manifest_path.is_symlink():
        raise ReceiptCorrupt("run manifest snapshot is unsafe")
    try:
        snapshot = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, TypeError, json.JSONDecodeError) as error:
        raise ReceiptCorrupt("run manifest snapshot is missing or invalid") from error
    if not isinstance(snapshot, dict):
        raise ReceiptCorrupt("run manifest snapshot must be an object")
    if snapshot.get("schema_version") != 1:
        raise IncompatibleManifest("unsupported manifest schema version")
    _manifest_family(snapshot.get("manifest_version"))
    contract = dict(snapshot)
    run_metadata = contract.pop("_run", None)
    try:
        validate_manifest(contract)
    except ValueError as error:
        raise ReceiptCorrupt("run manifest contract is invalid") from error
    contract_hash = manifest_hash(contract)
    if run_metadata is not None:
        if not isinstance(run_metadata, dict):
            raise ReceiptCorrupt("run manifest metadata is invalid")
        if run_metadata.get("manifest_hash") != contract_hash:
            raise ReceiptCorrupt("run manifest metadata hash mismatch")
    return {"manifest": contract, "manifest_hash": contract_hash, "run": run_metadata}


def initialize_run(
    state_root,
    workflow_type,
    repo_root,
    component_ids,
    owner_token=None,
    owner_file=None,
    manifest_path=None,
    recovery_provenance=None,
    initial_evidence_refs=None,
):
    source_path = (
        Path(__file__).resolve().parents[1] / "references" / "workflow-manifest.json"
        if manifest_path is None
        else Path(manifest_path)
    )
    manifest = json.loads(source_path.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    family = _manifest_family(manifest["manifest_version"])
    if workflow_type not in manifest["workflow_types"]:
        raise ValueError("unknown workflow type")
    if not isinstance(component_ids, list) or not component_ids:
        raise ValueError("at least one component id is required")
    if recovery_provenance is not None:
        if family != "1.1" or not isinstance(recovery_provenance, dict):
            raise ValueError("recovery provenance requires manifest 1.1 metadata")
        if set(recovery_provenance) != _RECOVERY_FIELDS:
            raise ValueError("recovery run provenance must be complete")
        _validate_recovery_provenance(recovery_provenance)
    initial_evidence_refs = (
        [] if initial_evidence_refs is None else initial_evidence_refs
    )
    _validate_evidence_refs(initial_evidence_refs)
    ordered_components = []
    for component_id in component_ids:
        validate_identifier(component_id, "component id")
        if component_id not in ordered_components:
            ordered_components.append(component_id)
    repo_path = Path(repo_root).expanduser().resolve(strict=True)
    if not repo_path.is_dir():
        raise ValueError("repo_root must be an existing directory")

    raw_state_path = Path(state_root).expanduser()
    _reject_symlink_components(raw_state_path)
    if raw_state_path.exists():
        state_path = raw_state_path.resolve()
        validate_secure_mode(state_path, 0o700, "state root")
    else:
        raw_state_path.mkdir(mode=0o700)
        os.chmod(raw_state_path, 0o700)
        state_path = raw_state_path.resolve()
        validate_secure_mode(state_path, 0o700, "state root")
    for directory in ("runs", "reports", "candidates", "locks", "handles", "quarantine"):
        child = state_path / directory
        if not child.exists():
            child.mkdir(mode=0o700)
            os.chmod(child, 0o700)
        validate_secure_mode(child, 0o700, directory + " directory")
    config_path = state_path / "config.json"
    if not config_path.exists():
        _write_json_atomic(
            config_path,
            {"schema_version": 1, "workspace": "bluetape4k", "runtime": "bluetape-workflow"},
        )

    owner_path = None
    if family == "1.1":
        if owner_token is not None:
            raise ValueError("manifest 1.1 accepts owner credentials only from owner_file")
        if owner_file is None:
            raise ValueError("manifest 1.1 requires owner_file")
        owner_path = Path(owner_file).expanduser()
        handles_root = state_path / "handles"
        try:
            owner_path.resolve(strict=False).relative_to(handles_root.resolve())
        except ValueError as error:
            raise ValueError("owner handle must be contained under state-root handles") from error
        if owner_path.parent.resolve(strict=False) != handles_root.resolve():
            raise ValueError("owner handle must be a direct child of handles")
        validate_identifier(owner_path.stem, "owner handle id")
        if owner_path.exists() or owner_path.is_symlink():
            raise ValueError("owner handle already exists")

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:8]
    validate_identifier(run_id, "run id")
    run_path = state_path / "runs" / run_id
    run_path.mkdir(mode=0o700)
    os.chmod(run_path, 0o700)
    staging_owner_path = None
    handle = None
    owner_published = False
    try:
        for directory in ("lanes", "heartbeats", "locks"):
            child = run_path / directory
            child.mkdir(mode=0o700)
            os.chmod(child, 0o700)

        if family == "1.1":
            staging_owner_path = handles_root / (
                "init-" + uuid.uuid4().hex + ".owner"
            )
            handle = _create_owner_handle(staging_owner_path, run_id, epoch=1)
            receipt_owner = handle["fingerprint"]
            owner_epoch = 1
        else:
            receipt_owner = owner_token or uuid.uuid4().hex
            if not isinstance(receipt_owner, str) or not receipt_owner:
                raise ValueError("owner token must be a non-empty string")
            owner_epoch = None

        contract_hash = manifest_hash(manifest)
        run_manifest = dict(manifest)
        run_metadata = {
            "manifest_hash": contract_hash,
            "workflow_type": workflow_type,
            "repo_root": str(repo_path),
            "component_ids": ordered_components,
        }
        if family == "1.1":
            run_metadata.update(
                {
                    "owner_fingerprint": receipt_owner,
                    "owner_epoch": owner_epoch,
                    "initial_owner_epoch": owner_epoch,
                }
            )
        else:
            run_metadata["owner_token"] = receipt_owner
        run_manifest["_run"] = run_metadata
        _write_json_atomic(run_path / "manifest.json", run_manifest)
        created = append_receipt_event(
            run_path,
            "run_created",
            owner_token=receipt_owner if family == "1.0" else None,
            owner_handle=handle["path"] if handle else None,
            manifest_hash=contract_hash,
            evidence_refs=initial_evidence_refs,
            to_state="planned",
            metadata=(
                {"owner_epoch": owner_epoch, **(recovery_provenance or {})}
                if family == "1.1"
                else None
            ),
        )
        if family == "1.1":
            try:
                os.link(
                    str(staging_owner_path),
                    str(owner_path),
                    follow_symlinks=False,
                )
            except FileExistsError as error:
                raise ValueError("owner handle already exists") from error
            owner_published = True
            staging_owner_path.unlink(missing_ok=True)
            handle["path"] = owner_path

        result = {
            "run_id": run_id,
            "run_dir": str(run_path),
            "manifest_hash": contract_hash,
            "workflow_type": workflow_type,
            "component_ids": ordered_components,
            "event": created,
        }
        if family == "1.0":
            result["owner_token"] = receipt_owner
        else:
            result.update(
                {
                    "owner_fingerprint": receipt_owner,
                    "owner_epoch": owner_epoch,
                    "owner_file": str(handle["path"]),
                }
            )
        return result
    except Exception:
        if not owner_published:
            if staging_owner_path is not None:
                staging_owner_path.unlink(missing_ok=True)
            shutil.rmtree(run_path, ignore_errors=True)
        raise


def validate_manifest(manifest):
    required = {
        "schema_version",
        "manifest_version",
        "workflow_types",
        "workflow_routes",
        "router_checklist_ids",
        "gate_dependencies",
        "run_states",
        "run_transitions",
        "lane_states",
        "lane_transitions",
        "transition_policy",
        "liveness",
        "topology",
        "completion",
        "receipt",
        "token_audit",
    }
    missing = sorted(required - set(manifest))
    if missing:
        raise ValueError("missing manifest fields: " + ", ".join(missing))
    family = _manifest_family(manifest["manifest_version"])
    if manifest["workflow_types"] != ["A", "B", "C", "D", "E", "P", "F"]:
        raise ValueError("workflow type order mismatch")
    if set(manifest["workflow_routes"]) != set(manifest["workflow_types"]):
        raise ValueError("workflow routes do not match workflow types")
    checklist_ids = manifest["router_checklist_ids"]
    if len(checklist_ids) != len(set(checklist_ids)):
        raise ValueError("duplicate router checklist id")
    if set(manifest["gate_dependencies"]) != set(checklist_ids):
        raise ValueError("gate dependencies do not match router checklist ids")
    for gate, dependencies in manifest["gate_dependencies"].items():
        if not set(dependencies) <= set(checklist_ids):
            raise ValueError("unknown gate dependency: " + gate)
    _validate_transitions("run", manifest["run_states"], manifest["run_transitions"])
    _validate_transitions("lane", manifest["lane_states"], manifest["lane_transitions"])
    _validate_transition_policy(
        "run", manifest["run_transitions"], manifest["transition_policy"]["run"]
    )
    _validate_transition_policy(
        "lane", manifest["lane_transitions"], manifest["transition_policy"]["lane"]
    )
    liveness = manifest["liveness"]
    for name in (
        "startup_ack_seconds",
        "monitor_interval_seconds",
        "suspected_stall_seconds",
        "max_silence_lease_seconds",
        "probe_grace_seconds",
        "max_replacements",
    ):
        if not isinstance(liveness.get(name), int) or liveness[name] < 0:
            raise ValueError("invalid liveness field: " + name)
    if liveness.get("heartbeat_is_completion_evidence") is not False:
        raise ValueError("heartbeat cannot be completion evidence")
    if manifest["token_audit"].get("hard_limit") is not False:
        raise ValueError("token audit must remain report-only")
    events = manifest["receipt"].get("event_types")
    if not isinstance(events, list) or len(events) != len(set(events)):
        raise ValueError("receipt event types must be a unique list")
    expected_events = set(PHASE1_EVENT_TYPES if family == "1.0" else PHASE2_EVENT_TYPES)
    if set(events) != expected_events:
        raise ValueError("receipt event type contract mismatch")
    if family == "1.1":
        limits = manifest.get("resource_limits")
        if not isinstance(limits, dict) or set(limits) != set(RESOURCE_LIMITS):
            raise ValueError("resource limit contract mismatch")
        for key, value in limits.items():
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise ValueError("invalid resource limit: " + key)
        if limits["max_identifier_chars"] != 128:
            raise ValueError(
                "max_identifier_chars must match the receipt schema contract"
            )
        compatible = manifest.get("compatible_manifest_versions")
        if compatible != ["1.0", "1.1"]:
            raise ValueError("compatible manifest version contract mismatch")
    return manifest


def _validate_transitions(kind, states, transitions):
    state_set = set(states)
    if set(transitions) != state_set:
        raise ValueError(kind + " transition keys do not match states")
    for source, targets in transitions.items():
        unknown = sorted(set(targets) - state_set)
        if unknown:
            raise ValueError(
                "unknown " + kind + " transition: " + source + " -> " + ",".join(unknown)
            )


def _validate_transition_policy(kind, transitions, policy):
    targets = {target for values in transitions.values() for target in values}
    documented = set(policy.get("evidence_by_target", {}))
    if documented != targets:
        raise ValueError(kind + " transition policy coverage mismatch")
    if not policy.get("required_arguments"):
        raise ValueError(kind + " transition arguments missing")
