import argparse
import importlib.util
import json
import math
import re
import sys
from pathlib import Path


_SKILL_REFERENCE = re.compile(r"\$[a-z0-9-]+")
_LOCAL_REFERENCE = re.compile(
    r"`((?:references|templates|scripts)/[^`\s]+)`"
)
_OMX_DEPENDENCY = re.compile(r"\.omx/|\bomx\s+team\b|\bOMX_[A-Z0-9_]+\b")
_GUIDANCE_VIOLATIONS = (
    (
        "native_spawn_order",
        re.compile(r"spawn_agent\b.*\bbefore\b.*\blane-create\b", re.IGNORECASE),
        "record lane-create and lane-start before native spawn",
    ),
    (
        "heartbeat_as_completion",
        re.compile(r"heartbeat\s+(?:proves|is)\s+completion", re.IGNORECASE),
        "heartbeat may prove only liveness",
    ),
    (
        "native_interrupt_order",
        re.compile(r"interrupt_agent\b.*\bbefore\b.*\bprobe-sent\b", re.IGNORECASE),
        "probe and authority evidence must precede native interrupt",
    ),
    (
        "replacement_identity",
        re.compile(r"reus(?:e|ing)\s+the\s+same\s+replacement\s+lane\s+id", re.IGNORECASE),
        "replacement lanes require distinct identities",
    ),
    (
        "direct_runtime_json",
        re.compile(r"(?:writes?|edits?)\s+\.bluetape/(?:lanes|heartbeats)/?[^ ]*\s+directly", re.IGNORECASE),
        "runtime JSON must be written only through guarded commands",
    ),
    (
        "completion_check_missing",
        re.compile(r"(?:mark|marks)\s+topology\s+complete\s+without\s+completion-check", re.IGNORECASE),
        "completion-check must precede complete",
    ),
    (
        "python_native_tool_claim",
        re.compile(r"python\s+invokes?\s+native\s+(?:spawn_agent|send_message|interrupt_agent|wait_agent)", re.IGNORECASE),
        "Python cannot execute native collaboration tools",
    ),
    (
        "owner_fencing_exposure",
        re.compile(r"--owner-token|\bowner_token\b[^\n]*\bjson\b", re.IGNORECASE),
        "owner fencing values must stay in owner files",
    ),
    (
        "unsafe_write_scope",
        re.compile(r"accepts?\s+(?:a\s+)?symlinked\s+noncanonical\s+write\s+scope", re.IGNORECASE),
        "write scope must be canonical and symlink-safe",
    ),
    (
        "same_session_dogfood",
        re.compile(r"apply\s+new\s+guidance.*native\s+dogfood.*same\s+session", re.IGNORECASE),
        "native dogfood requires a fresh session handoff",
    ),
)
_ROUTER_ID = re.compile(r"\bWF-[0-9]+[A-Z]?\b")
_TOKEN_START = re.compile(
    r"^\s*<!--\s*bluetape-token:start\s+([a-z0-9-]+)\s*-->\s*$"
)
_TOKEN_END = re.compile(
    r"^\s*<!--\s*bluetape-token:end\s+([a-z0-9-]+)\s*-->\s*$"
)

_PHASE2_COMMANDS = {
    "run-approve", "run-start", "run-recovery-start", "run-recovery-finish",
    "run-fail", "run-block", "run-cancel", "lane-create", "lane-start",
    "startup-ack", "stall-record", "stall-clear", "probe-ack", "lane-complete",
    "lane-fail", "lane-block", "lane-cancel", "heartbeat", "liveness-check",
    "probe-sent", "interrupt-result", "lane-reassign", "replacement-repair",
    "replacement-block", "replacement-close", "resume-check", "resume",
    "lane-resolve",
    "receipt-diagnose", "recovery-run-create", "handoff-create",
    "live-report-create", "topology-register", "topology-remove", "check-result",
    "component-evidence", "completion-check", "complete",
}
_BASE_COMMANDS = {"state-root", "init", "verify", "rebuild"}


def _load_runtime():
    runtime_path = Path(__file__).with_name("bluetape_runtime.py")
    spec = importlib.util.spec_from_file_location(
        "bluetape_runtime_contracts", runtime_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _frontmatter(lines):
    if not lines or lines[0].strip() != "---":
        return None, 0
    values = {}
    for index in range(1, len(lines)):
        line = lines[index]
        if line.strip() == "---":
            return values, index + 1
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip("'\"")
    return None, 0


def _active_lines(lines):
    active = []
    fence = None
    for line_number, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        marker = None
        if stripped.startswith("```"):
            marker = "```"
        elif stripped.startswith("~~~"):
            marker = "~~~"
        if marker is not None:
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence is None:
            active.append((line_number, line))
    return active


def _relative_path(path, root):
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _issue(code, path, line, message):
    return {"code": code, "path": path, "line": line, "message": message}


def _discover_skill_names(skills_root):
    names = set()
    for skill_file in Path(skills_root).rglob("SKILL.md"):
        lines = skill_file.read_text(encoding="utf-8").splitlines()
        frontmatter, _ = _frontmatter(lines)
        if frontmatter and frontmatter.get("name"):
            names.add(frontmatter["name"])
        else:
            names.add(skill_file.parent.name)
    return names


def _skill_directories(skill_root):
    root = Path(skill_root)
    if (root / "SKILL.md").is_file():
        return [root] if root.name.startswith("bluetape-") else []
    return sorted(
        path
        for path in root.iterdir()
        if path.is_dir()
        and path.name.startswith("bluetape-")
        and (path / "SKILL.md").is_file()
    )


def _local_target_exists(skill_dir, relative_path):
    target = skill_dir / relative_path
    if target.exists():
        return True
    path = Path(relative_path)
    if path.parts and path.parts[0] == "scripts":
        executable = skill_dir / "scripts" / ("executable_" + path.name)
        return executable.exists()
    return False


def _guarded_cli_path(skill_dir):
    scripts_dir = skill_dir / "scripts"
    source_path = scripts_dir / "executable_bluetape-flow.py"
    if source_path.is_file():
        return source_path
    rendered_path = scripts_dir / "bluetape-flow.py"
    if rendered_path.is_file():
        return rendered_path
    return source_path


def _is_direct_state_mutation(line):
    if ".bluetape" not in line or "bluetape-flow.py" in line:
        return False
    return bool(
        re.search(r">{1,2}\s*[^`\s]*\.bluetape", line)
        or re.search(r"\b(?:rm|rmdir|unlink)\b[^\n]*\.bluetape", line)
    )


def _line_containing(lines, value):
    for line_number, line in enumerate(lines, start=1):
        if value in line:
            return line_number
    return 1


def _resolve_local_schema_ref(schema, value):
    current = value
    visited = set()
    while isinstance(current, dict) and set(current) == {"$ref"}:
        reference = current["$ref"]
        if not isinstance(reference, str) or not reference.startswith("#/"):
            raise ValueError("receipt schema uses a non-local reference")
        if reference in visited:
            raise ValueError("receipt schema reference cycle")
        visited.add(reference)
        current = schema
        for part in reference[2:].split("/"):
            current = current[part.replace("~1", "/").replace("~0", "~")]
    return current


def _validate_receipt_schema(skill_dir, skills_root, manifest, issues):
    schema_path = skill_dir / "references" / "receipt-schema.json"
    relative_schema = _relative_path(schema_path, skills_root)
    if not schema_path.is_file():
        issues.append(
            _issue(
                "receipt_schema_missing",
                relative_schema,
                1,
                "receipt schema is missing",
            )
        )
        return
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        required = set(schema["required"])
        properties = schema["properties"]
        event_types = properties["event_type"]["enum"]
        evidence_schema = _resolve_local_schema_ref(
            schema, properties["evidence_refs"]
        )
        evidence_items = _resolve_local_schema_ref(
            schema, evidence_schema["items"]
        )
        evidence_properties = set(evidence_items["properties"])
        if schema.get("additionalProperties") is not False:
            raise ValueError("receipt events must reject additional properties")
        if evidence_items.get("additionalProperties") is not False:
            raise ValueError("receipt evidence must reject additional properties")
        if not {"sequence", "previous_checksum", "checksum"} <= required:
            raise ValueError("receipt checksum chain fields must be required")
        if evidence_properties != {
            "kind",
            "summary",
            "path",
            "checksum",
            "exit_status",
        }:
            raise ValueError("receipt evidence allowlist mismatch")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        issues.append(
            _issue(
                "receipt_schema_invalid",
                relative_schema,
                1,
                "receipt schema is invalid: " + str(error),
            )
        )
        return
    if event_types != manifest["receipt"]["event_types"]:
        issues.append(
            _issue(
                "receipt_event_drift",
                relative_schema,
                _line_containing(
                    schema_path.read_text(encoding="utf-8").splitlines(),
                    '"event_type"',
                ),
                "receipt schema event types do not match the manifest",
            )
        )


def _load_cli_commands(skill_dir):
    cli_path = _guarded_cli_path(skill_dir)
    scripts_path = str(cli_path.parent)
    inserted = scripts_path not in sys.path
    imported_names = ("bluetape_coordinator", "bluetape_runtime")
    previous_modules = {
        name: sys.modules.get(name) for name in imported_names
    }
    for name in imported_names:
        sys.modules.pop(name, None)
    if inserted:
        sys.path.insert(0, scripts_path)
    try:
        spec = importlib.util.spec_from_file_location(
            "bluetape_flow_contracts", cli_path
        )
        if spec is None or spec.loader is None:
            raise ValueError("guarded CLI cannot be loaded")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        parser = module.build_parser()
        subparsers = next(
            action
            for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)
        )
        return set(subparsers.choices)
    finally:
        for name in imported_names:
            sys.modules.pop(name, None)
            if previous_modules[name] is not None:
                sys.modules[name] = previous_modules[name]
        if inserted:
            sys.path.remove(scripts_path)


def _validate_phase2_surface(skill_dir, skills_root, issues):
    relative_skill = _relative_path(skill_dir / "SKILL.md", skills_root)
    cli_path = _guarded_cli_path(skill_dir)
    coordinator_path = skill_dir / "scripts" / "bluetape_coordinator.py"
    required_docs = (
        skill_dir / "SKILL.md",
        skill_dir / "references" / "liveness-contract.md",
        skill_dir / "references" / "topology-contract.md",
    )
    if not cli_path.is_file():
        issues.append(
            _issue("guarded_cli_missing", relative_skill, 1, "guarded CLI is missing")
        )
        return
    if not coordinator_path.is_file():
        issues.append(
            _issue(
                "coordinator_missing",
                _relative_path(coordinator_path, skills_root),
                1,
                "Phase 2 coordinator implementation is missing",
            )
        )
    try:
        commands = _load_cli_commands(skill_dir)
    except (ImportError, OSError, RuntimeError, StopIteration, ValueError) as error:
        issues.append(
            _issue(
                "guarded_cli_invalid",
                _relative_path(cli_path, skills_root),
                1,
                "guarded CLI is invalid: " + str(error),
            )
        )
        return
    expected_commands = _BASE_COMMANDS | _PHASE2_COMMANDS
    if commands != expected_commands:
        issues.append(
            _issue(
                "cli_command_drift",
                _relative_path(cli_path, skills_root),
                1,
                "guarded CLI commands do not match the Phase 2 command contract",
            )
        )
    missing_docs = [path for path in required_docs if not path.is_file()]
    if missing_docs:
        for path in missing_docs:
            issues.append(
                _issue(
                    "phase2_guidance_missing",
                    _relative_path(path, skills_root),
                    1,
                    "Phase 2 guidance document is missing",
                )
            )
        return
    guidance = "\n".join(path.read_text(encoding="utf-8") for path in required_docs)
    for command in sorted(_PHASE2_COMMANDS):
        if command not in guidance:
            issues.append(
                _issue(
                    "cli_command_guidance_missing",
                    relative_skill,
                    1,
                    "Phase 2 guidance omits command: " + command,
                )
            )
    required_markers = {
        "owner_file_only_missing": "--owner-file",
        "scope_verification_missing": "git status --porcelain=v1 -z",
        "fresh_session_handoff_missing": "fresh-session handoff",
        "report_mode_missing": "contained 0600",
        "receipt_head_link_missing": "receipt head",
    }
    lowered_guidance = guidance.lower()
    for code, marker in required_markers.items():
        if marker.lower() not in lowered_guidance:
            issues.append(_issue(code, relative_skill, 1, "missing guidance marker: " + marker))
    cli_source = cli_path.read_text(encoding="utf-8")
    if re.search(r"\b(?:spawn_agent|send_message|list_agents|wait_agent|interrupt_agent)\s*\(", cli_source):
        issues.append(
            _issue(
                "native_tool_adapter_dependency",
                _relative_path(cli_path, skills_root),
                1,
                "guarded CLI must not invoke native collaboration tools",
            )
        )
    if "--owner-token" in cli_source or "owner_token" in guidance:
        issues.append(
            _issue(
                "owner_fencing_exposure",
                relative_skill,
                1,
                "Phase 2 accepts owner authority only from owner files",
            )
        )
    if coordinator_path.is_file():
        coordinator_source = coordinator_path.read_text(encoding="utf-8")
        for marker in ("create_bound_report", "0o600", "report_receipt_head", "report_checksum"):
            if marker not in coordinator_source:
                issues.append(
                    _issue(
                        "report_contract_drift",
                        _relative_path(coordinator_path, skills_root),
                        1,
                        "report contract implementation is missing: " + marker,
                    )
                )
        manifest_path = skill_dir / "references" / "workflow-manifest.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            event_types = manifest["receipt"]["event_types"]
        except (KeyError, OSError, TypeError, json.JSONDecodeError):
            event_types = []
        for event_type in event_types:
            if '"' + event_type + '"' not in coordinator_source:
                issues.append(
                    _issue(
                        "coordinator_event_missing",
                        _relative_path(coordinator_path, skills_root),
                        1,
                        "coordinator omits manifest event: " + event_type,
                    )
                )


def _validate_router_manifest(skill_dir, skills_root, known_names, active, issues):
    manifest_path = skill_dir / "references" / "workflow-manifest.json"
    relative_manifest = _relative_path(manifest_path, skills_root)
    if not manifest_path.is_file():
        issues.append(
            _issue("manifest_missing", relative_manifest, 1, "workflow manifest is missing")
        )
        return
    manifest_lines = manifest_path.read_text(encoding="utf-8").splitlines()
    try:
        manifest = json.loads("\n".join(manifest_lines))
        _load_runtime().validate_manifest(manifest)
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        issues.append(
            _issue(
                "manifest_invalid",
                relative_manifest,
                1,
                "workflow manifest is invalid: " + str(error),
            )
        )
        return

    _validate_receipt_schema(skill_dir, skills_root, manifest, issues)

    for routes in manifest["workflow_routes"].values():
        for route in routes:
            if route not in known_names:
                issues.append(
                    _issue(
                        "manifest_route_missing",
                        relative_manifest,
                        _line_containing(manifest_lines, '"' + route + '"'),
                        "manifest route skill is missing: " + route,
                    )
                )

    router_occurrences = {}
    for line_number, line in active:
        for checklist_id in _ROUTER_ID.findall(line):
            router_occurrences.setdefault(checklist_id, []).append(line_number)
    declared = set(manifest["router_checklist_ids"])
    for checklist_id in manifest["router_checklist_ids"]:
        occurrences = router_occurrences.get(checklist_id, [])
        if not occurrences:
            issues.append(
                _issue(
                    "router_checklist_missing",
                    _relative_path(skill_dir / "SKILL.md", skills_root),
                    1,
                    "router checklist id is missing: " + checklist_id,
                )
            )
        elif len(occurrences) > 1:
            issues.append(
                _issue(
                    "router_checklist_duplicate",
                    _relative_path(skill_dir / "SKILL.md", skills_root),
                    occurrences[1],
                    "router checklist id appears more than once: " + checklist_id,
                )
            )
    for checklist_id in sorted(set(router_occurrences) - declared):
        issues.append(
            _issue(
                "router_checklist_drift",
                _relative_path(skill_dir / "SKILL.md", skills_root),
                router_occurrences[checklist_id][0],
                "router checklist id is absent from manifest: " + checklist_id,
            )
        )


def validate_skill_tree(skill_root, skills_root):
    root = Path(skill_root)
    all_skills_root = Path(skills_root)
    known_names = _discover_skill_names(all_skills_root)
    issues = []
    for skill_dir in _skill_directories(root):
        skill_file = skill_dir / "SKILL.md"
        relative_skill = _relative_path(skill_file, all_skills_root)
        lines = skill_file.read_text(encoding="utf-8").splitlines()
        frontmatter, _ = _frontmatter(lines)
        if frontmatter is None:
            issues.append(
                _issue(
                    "frontmatter_missing",
                    relative_skill,
                    1,
                    "SKILL.md must start with a closed frontmatter block",
                )
            )
        elif frontmatter.get("name") != skill_dir.name:
            issues.append(
                _issue(
                    "frontmatter_name_mismatch",
                    relative_skill,
                    2,
                    "frontmatter name must match skill directory",
                )
            )

        active = _active_lines(lines)
        for line_number, line in active:
            for reference in _SKILL_REFERENCE.findall(line):
                skill_name = reference[1:]
                if skill_name not in known_names:
                    issues.append(
                        _issue(
                            "unknown_skill_reference",
                            relative_skill,
                            line_number,
                            "unknown skill reference: " + reference,
                        )
                    )
            for relative_path in _LOCAL_REFERENCE.findall(line):
                if not _local_target_exists(skill_dir, relative_path):
                    issues.append(
                        _issue(
                            "missing_local_reference",
                            relative_skill,
                            line_number,
                            "missing local reference: " + relative_path,
                        )
                    )
            if _is_direct_state_mutation(line):
                issues.append(
                    _issue(
                        "direct_state_mutation",
                        relative_skill,
                        line_number,
                        "state mutation must use bluetape-flow.py",
                    )
                )
            if _OMX_DEPENDENCY.search(line):
                issues.append(
                    _issue(
                        "omx_dependency",
                        relative_skill,
                        line_number,
                        "Bluetape workflow guidance must not depend on OMX state",
                    )
                )
            for code, pattern, message in _GUIDANCE_VIOLATIONS:
                if pattern.search(line):
                    issues.append(
                        _issue(code, relative_skill, line_number, message)
                    )

        if skill_dir.name == "bluetape-workflow":
            _validate_router_manifest(
                skill_dir, all_skills_root, known_names, active, issues
            )
            _validate_phase2_surface(skill_dir, all_skills_root, issues)
    return sorted(
        issues, key=lambda issue: (issue["path"], issue["line"], issue["code"])
    )


def _ignored_audit_file(path, skill_dir):
    relative = path.relative_to(skill_dir)
    return (
        "__pycache__" in relative.parts
        or path.name == ".DS_Store"
        or path.suffix in {".pyc", ".tmp"}
    )


def _baseline_rows(baseline):
    if baseline is None:
        return {}
    if isinstance(baseline, (str, Path)):
        value = json.loads(Path(baseline).read_text(encoding="utf-8"))
    elif isinstance(baseline, dict):
        value = baseline
    else:
        raise ValueError("baseline must be a JSON object or path")
    rows = value.get("skills")
    if not isinstance(rows, list):
        raise ValueError("baseline skills must be a list")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("skill"), str):
            raise ValueError("baseline skill row is invalid")
        byte_count = row.get("bytes")
        token_count = row.get("approx_tokens")
        if not isinstance(byte_count, int) or byte_count < 0:
            raise ValueError("baseline byte count is invalid")
        if token_count is None:
            token_count = math.ceil(byte_count / 4)
        if not isinstance(token_count, int) or token_count < 0:
            raise ValueError("baseline token count is invalid")
        result[row["skill"]] = {
            "bytes": byte_count,
            "approx_tokens": token_count,
        }
    return result


def _marker_diagnostic(code, skill, path, line, message):
    return {
        "code": code,
        "skill": skill,
        "path": path,
        "line": line,
        "message": message,
    }


def _audit_markers(skill, skill_dir, path, data):
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return [], []
    relative_path = str(path.relative_to(skill_dir))
    blocks = []
    diagnostics = []
    active = None
    for line_number, line in enumerate(text.splitlines(keepends=True), start=1):
        marker_line = line.rstrip("\r\n")
        start_match = _TOKEN_START.match(marker_line)
        end_match = _TOKEN_END.match(marker_line)
        if start_match:
            if active is not None:
                diagnostics.append(
                    _marker_diagnostic(
                        "nested_token_marker",
                        skill,
                        relative_path,
                        line_number,
                        "token markers may not nest",
                    )
                )
            else:
                active = {
                    "name": start_match.group(1),
                    "line": line_number,
                    "bytes": 0,
                }
            continue
        if end_match:
            if active is None:
                diagnostics.append(
                    _marker_diagnostic(
                        "unmatched_token_end",
                        skill,
                        relative_path,
                        line_number,
                        "token end marker has no matching start",
                    )
                )
            elif end_match.group(1) != active["name"]:
                diagnostics.append(
                    _marker_diagnostic(
                        "mismatched_token_end",
                        skill,
                        relative_path,
                        line_number,
                        "token end marker name does not match active block",
                    )
                )
            else:
                blocks.append(
                    {
                        "skill": skill,
                        "path": relative_path,
                        "name": active["name"],
                        "bytes": active["bytes"],
                        "approx_tokens": math.ceil(active["bytes"] / 4),
                    }
                )
                active = None
            continue
        if active is not None:
            active["bytes"] += len(line.encode("utf-8"))
    if active is not None:
        diagnostics.append(
            _marker_diagnostic(
                "unmatched_token_start",
                skill,
                relative_path,
                active["line"],
                "token start marker has no matching end",
            )
        )
    return blocks, diagnostics


def audit_token_budget(skills_root, baseline=None):
    root = Path(skills_root)
    baseline_by_skill = _baseline_rows(baseline)
    rows = []
    marked_blocks = []
    diagnostics = []
    skill_dirs = sorted(
        path
        for path in root.iterdir()
        if path.is_dir()
        and path.name.startswith("bluetape-")
        and (path / "SKILL.md").is_file()
    )
    for skill_dir in skill_dirs:
        byte_count = 0
        for path in sorted(skill_dir.rglob("*")):
            if (
                not path.is_file()
                or path.is_symlink()
                or _ignored_audit_file(path, skill_dir)
            ):
                continue
            data = path.read_bytes()
            byte_count += len(data)
            blocks, file_diagnostics = _audit_markers(
                skill_dir.name, skill_dir, path, data
            )
            marked_blocks.extend(blocks)
            diagnostics.extend(file_diagnostics)
        token_count = math.ceil(byte_count / 4)
        baseline_row = baseline_by_skill.get(
            skill_dir.name, {"bytes": byte_count, "approx_tokens": token_count}
        )
        rows.append(
            {
                "skill": skill_dir.name,
                "bytes": byte_count,
                "approx_tokens": token_count,
                "byte_delta": byte_count - baseline_row["bytes"],
                "token_delta": token_count - baseline_row["approx_tokens"],
            }
        )
    marked_blocks.sort(key=lambda row: (row["skill"], row["path"], row["name"]))
    return {
        "schema_version": 1,
        "estimator": "utf8-bytes-div-4-ceil",
        "skills": rows,
        "totals": {
            "bytes": sum(row["bytes"] for row in rows),
            "approx_tokens": sum(row["approx_tokens"] for row in rows),
        },
        "marked_blocks": marked_blocks,
        "diagnostics": diagnostics,
    }
