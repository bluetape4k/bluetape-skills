import importlib
import json
import multiprocessing
import os
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
MANIFEST_PATH = SKILL_ROOT / "references" / "workflow-manifest.json"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _concurrent_lane_create(run_dir, owner_file, expected_head, barrier, results):
    runtime = importlib.import_module("bluetape_runtime")
    barrier.wait()
    try:
        runtime.mutate_receipt(
            run_dir,
            owner_file,
            lambda _state: [
                {
                    "event_type": "lane_created",
                    "lane_id": "concurrent",
                    "agent_id": "agent-concurrent",
                    "to_state": "pending",
                    "evidence_refs": [
                        {"kind": "test", "summary": "concurrent create"}
                    ],
                    "metadata": {
                        "owner_epoch": 1,
                        "assignment": "exercise receipt CAS",
                        "write_scope": [],
                        "fallback": "main session",
                        "startup_ack_deadline": "2026-07-14T00:01:00Z",
                        "command_deadline": "2026-07-14T01:00:00Z",
                        "parent_lane_id": None,
                        "replacement_count": 0,
                    },
                }
            ],
            expected_head=expected_head,
        )
        results.put("ok")
    except Exception as error:
        results.put(type(error).__name__)


def _concurrent_stale_reclaim(lock_dir, barrier, acquired, release, results):
    runtime = importlib.import_module("bluetape_runtime")
    barrier.wait()
    try:
        with runtime.state_lock(
            lock_dir,
            pid_probe=lambda pid: "dead" if pid == 424242 else "alive",
        ):
            acquired.set()
            release.wait(5)
        results.put("ok")
    except Exception as error:
        results.put(type(error).__name__)


class LaneReplayTest(unittest.TestCase):
    def setUp(self):
        self.runtime = importlib.import_module("bluetape_runtime")
        self.coordinator = importlib.import_module("bluetape_coordinator")
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.state_root = root / ".bluetape"
        self.repo_root = root / "repo"
        self.repo_root.mkdir()
        self.owner_file = self.state_root / "handles" / "phase2.owner"
        self.initialized = self.runtime.initialize_run(
            self.state_root,
            workflow_type="A",
            repo_root=self.repo_root,
            component_ids=["runtime"],
            owner_file=self.owner_file,
            manifest_path=MANIFEST_PATH,
        )
        self.run_dir = self.state_root / "runs" / self.initialized["run_id"]

    def tearDown(self):
        self.temp.cleanup()

    def append(self, event_type, **kwargs):
        metadata = kwargs.pop("metadata", {"owner_epoch": 1})
        return self.runtime.append_receipt_event(
            self.run_dir,
            event_type,
            owner_handle=self.owner_file,
            manifest_hash=self.initialized["manifest_hash"],
            evidence_refs=kwargs.pop(
                "evidence_refs", [{"kind": "test", "summary": event_type}]
            ),
            metadata=metadata,
            **kwargs,
        )

    def running_events_with_pending_lane(self):
        self.append(
            "plan_approved",
            from_state="planned",
            to_state="approved",
            timestamp="2026-07-14T00:00:01Z",
        )
        self.append(
            "run_started",
            from_state="approved",
            to_state="running",
            timestamp="2026-07-14T00:00:02Z",
        )
        self.append(
            "lane_created",
            lane_id="review",
            agent_id="agent-1",
            to_state="pending",
            timestamp="2026-07-14T00:00:03Z",
            metadata={
                "owner_epoch": 1,
                "assignment": "Review the Phase 2 diff",
                "write_scope": [],
                "fallback": "main session",
                "startup_ack_deadline": "2026-07-14T00:00:30Z",
                "command_deadline": "2026-07-14T00:10:00Z",
                "parent_lane_id": None,
                "replacement_count": 0,
            },
        )
        return self.runtime.verify_receipt(self.run_dir)

    def test_replay_builds_owner_run_and_lane_state(self):
        events = self.running_events_with_pending_lane()
        manifest_snapshot = self.runtime.load_run_manifest_snapshot(self.run_dir)

        state = self.coordinator.replay_coordinator_state(
            events, manifest_snapshot
        )

        self.assertEqual(1, state["owner_epoch"])
        self.assertRegex(state["owner_fingerprint"], "^[0-9a-f]{64}$")
        self.assertEqual("running", state["run_state"])
        self.assertEqual("pending", state["lanes"]["review"]["state"])
        self.assertEqual([], state["incomplete_replacements"])

    def test_duplicate_lane_and_missing_lane_id_name_first_bad_sequence(self):
        events = self.running_events_with_pending_lane()
        manifest_snapshot = self.runtime.load_run_manifest_snapshot(self.run_dir)
        duplicate = dict(events[-1])
        duplicate["sequence"] = len(events) + 1
        events.append(duplicate)
        with self.assertRaisesRegex(
            self.coordinator.CoordinatorCorrupt, "sequence 5"
        ):
            self.coordinator.replay_coordinator_state(events, manifest_snapshot)

        missing = dict(events[-2])
        missing["lane_id"] = None
        with self.assertRaisesRegex(
            self.coordinator.CoordinatorCorrupt, "sequence 4"
        ):
            self.coordinator.replay_coordinator_state(
                events[:-2] + [missing], manifest_snapshot
            )

    def test_rebuild_preserves_receipt_and_writes_versioned_lane_cache(self):
        self.running_events_with_pending_lane()
        before = (self.run_dir / "receipt.jsonl").read_bytes()

        snapshot = self.runtime.rebuild_coordinator_snapshots(self.run_dir)

        self.assertEqual(before, (self.run_dir / "receipt.jsonl").read_bytes())
        self.assertEqual(1, snapshot["coordinator"]["cache_version"])
        lane_cache = json.loads(
            (self.run_dir / "lanes" / "review.json").read_text(encoding="utf-8")
        )
        self.assertEqual("pending", lane_cache["state"])

    def test_mutation_appends_one_event_and_stale_cas_changes_nothing(self):
        events = self.running_events_with_pending_lane()
        expected_head = events[-1]["checksum"]

        state = self.runtime.mutate_receipt(
            self.run_dir,
            self.owner_file,
            lambda _state: [
                {
                    "event_type": "lane_started",
                    "lane_id": "review",
                    "agent_id": "agent-1",
                    "from_state": "pending",
                    "to_state": "starting",
                    "evidence_refs": [{"kind": "test", "summary": "start lane"}],
                }
            ],
            expected_head=expected_head,
        )

        self.assertEqual("starting", state["lanes"]["review"]["state"])
        self.assertEqual(5, state["last_sequence"])
        before = (self.run_dir / "receipt.jsonl").read_bytes()
        before_cache = (self.run_dir / "run.json").read_bytes()
        with self.assertRaises(self.coordinator.CoordinatorConflict):
            self.runtime.mutate_receipt(
                self.run_dir,
                self.owner_file,
                lambda _state: [
                    {
                        "event_type": "startup_ack",
                        "lane_id": "review",
                        "agent_id": "agent-1",
                        "from_state": "starting",
                        "to_state": "running",
                        "evidence_refs": [
                            {"kind": "test", "summary": "startup ack"}
                        ],
                    }
                ],
                expected_head=expected_head,
            )
        self.assertEqual(before, (self.run_dir / "receipt.jsonl").read_bytes())
        self.assertEqual(before_cache, (self.run_dir / "run.json").read_bytes())

    def test_heartbeat_and_lease_use_one_transaction_envelope(self):
        self.running_events_with_pending_lane()
        self.append(
            "lane_started",
            lane_id="review",
            agent_id="agent-1",
            from_state="pending",
            to_state="starting",
            timestamp="2026-07-14T00:00:04Z",
        )
        self.append(
            "startup_ack",
            lane_id="review",
            agent_id="agent-1",
            from_state="starting",
            to_state="running",
            timestamp="2026-07-14T00:00:05Z",
        )
        old_events = self.runtime.verify_receipt(self.run_dir)

        state = self.runtime.mutate_receipt(
            self.run_dir,
            self.owner_file,
            lambda _state: [
                {
                    "event_type": "heartbeat_observed",
                    "lane_id": "review",
                    "agent_id": "agent-1",
                    "from_state": "running",
                    "to_state": "running",
                    "timestamp": "2026-07-14T00:00:06Z",
                    "evidence_refs": [{"kind": "test", "summary": "heartbeat"}],
                    "metadata": {"owner_epoch": 1, "evidence_digest": "a" * 64},
                },
                {
                    "event_type": "lease_renewed",
                    "lane_id": "review",
                    "agent_id": "agent-1",
                    "from_state": "running",
                    "to_state": "running",
                    "timestamp": "2026-07-14T00:00:06Z",
                    "evidence_refs": [{"kind": "test", "summary": "lease"}],
                    "metadata": {
                        "owner_epoch": 1,
                        "silence_lease_deadline": "2026-07-14T00:05:06Z",
                        "evidence_digest": "a" * 64,
                    },
                },
            ],
            expected_head=old_events[-1]["checksum"],
        )

        events = self.runtime.verify_receipt(self.run_dir)
        self.assertEqual(len(old_events) + 1, len(events))
        self.assertEqual("transaction_committed", events[-1]["event_type"])
        self.assertEqual(
            "2026-07-14T00:05:06Z",
            state["lanes"]["review"]["silence_lease_deadline"],
        )

    def test_incomplete_tail_reports_last_trusted_head(self):
        events = self.running_events_with_pending_lane()
        with (self.run_dir / "receipt.jsonl").open("ab") as stream:
            stream.write(b'{"event_type":')

        with self.assertRaises(self.runtime.ReceiptCorrupt) as raised:
            list(self.runtime.iter_verified_receipt(self.run_dir))

        self.assertEqual(4, raised.exception.last_trusted_sequence)
        self.assertEqual(events[-1]["checksum"], raised.exception.last_trusted_checksum)
        self.assertEqual("blocked", raised.exception.effective_state)

    def test_two_processes_with_one_head_have_one_cas_winner(self):
        events = self.running_events_with_pending_lane()
        context = multiprocessing.get_context("fork")
        barrier = context.Barrier(2)
        results = context.Queue()
        processes = [
            context.Process(
                target=_concurrent_lane_create,
                args=(
                    str(self.run_dir),
                    str(self.owner_file),
                    events[-1]["checksum"],
                    barrier,
                    results,
                ),
            )
            for _ in range(2)
        ]
        for process in processes:
            process.start()
        for process in processes:
            process.join(10)
            self.assertEqual(0, process.exitcode)

        outcomes = sorted(results.get(timeout=2) for _ in processes)
        self.assertEqual("ok", outcomes[-1])
        self.assertIn(outcomes[0], {"CoordinatorConflict", "StateLockBusy"})
        final_events = self.runtime.verify_receipt(self.run_dir)
        self.assertEqual(5, len(final_events))
        self.assertEqual("lane_created", final_events[-1]["event_type"])

    def test_phase1_rebuild_preserves_every_existing_run_cache_value(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir) / "legacy-run"
            run_dir.mkdir()
            manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
            manifest["manifest_version"] = "1.0.0"
            manifest["receipt"]["event_types"] = list(
                self.runtime.PHASE1_EVENT_TYPES
            )
            manifest.pop("compatible_manifest_versions", None)
            manifest.pop("resource_limits", None)
            manifest_hash = self.runtime.manifest_hash(manifest)
            (run_dir / "manifest.json").write_text(
                self.runtime.canonical_json(manifest) + "\n", encoding="utf-8"
            )
            for event_type, source, target in (
                ("run_created", None, "planned"),
                ("plan_approved", "planned", "approved"),
                ("run_started", "approved", "running"),
            ):
                self.runtime.append_receipt_event(
                    run_dir,
                    event_type,
                    owner_token="legacy-owner",
                    manifest_hash=manifest_hash,
                    evidence_refs=(
                        []
                        if event_type == "run_created"
                        else [{"kind": "test", "summary": event_type}]
                    ),
                    from_state=source,
                    to_state=target,
                    timestamp="2026-07-14T00:00:00Z",
                )
            cache_path = run_dir / "run.json"
            original_cache = json.loads(cache_path.read_text(encoding="utf-8"))
            original_cache["phase1_only"] = {"keep": [1, 2, 3]}
            cache_path.write_text(
                self.runtime.canonical_json(original_cache) + "\n",
                encoding="utf-8",
            )
            receipt_before = (run_dir / "receipt.jsonl").read_bytes()

            rebuilt = self.runtime.rebuild_coordinator_snapshots(run_dir)

            for key, value in original_cache.items():
                self.assertEqual(value, rebuilt[key])
            self.assertEqual(1, rebuilt["coordinator"]["cache_version"])
            self.assertEqual(
                receipt_before, (run_dir / "receipt.jsonl").read_bytes()
            )

    def test_phase1_diagnosis_accepts_legacy_events_without_evidence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_root = Path(temp_dir) / ".bluetape"
            runs_root = state_root / "runs"
            run_dir = runs_root / "legacy-run"
            run_dir.mkdir(parents=True)
            for directory in (state_root, runs_root, run_dir):
                os.chmod(directory, 0o700)
            manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
            manifest["manifest_version"] = "1.0.0"
            manifest["receipt"]["event_types"] = list(self.runtime.PHASE1_EVENT_TYPES)
            manifest.pop("compatible_manifest_versions", None)
            manifest.pop("resource_limits", None)
            manifest_hash = self.runtime.manifest_hash(manifest)
            (run_dir / "manifest.json").write_text(
                self.runtime.canonical_json(manifest) + "\n", encoding="utf-8"
            )
            for event_type, source, target in (
                ("run_created", None, "planned"),
                ("plan_approved", "planned", "approved"),
                ("run_started", "approved", "running"),
            ):
                self.runtime.append_receipt_event(
                    run_dir,
                    event_type,
                    owner_token="legacy-owner",
                    manifest_hash=manifest_hash,
                    evidence_refs=[],
                    from_state=source,
                    to_state=target,
                    timestamp="2026-07-14T00:00:00Z",
                )

            diagnosis = self.coordinator.inspect_resume(run_dir)

            self.assertEqual("running", diagnosis["run_state"])
            self.assertEqual(3, diagnosis["last_sequence"])

    def test_semantic_corruption_returns_a_blocked_diagnosis(self):
        events = self.running_events_with_pending_lane()
        self.append(
            "plan_approved",
            from_state="running",
            to_state="approved",
            timestamp="2026-07-14T00:00:04Z",
        )

        diagnosis = self.coordinator.inspect_resume(self.run_dir)

        self.assertEqual("blocked", diagnosis["effective_state"])
        self.assertEqual(5, diagnosis["first_bad_sequence"])
        self.assertEqual(4, diagnosis["last_trusted_sequence"])
        self.assertEqual(events[-1]["checksum"], diagnosis["last_trusted_checksum"])

    def test_two_stale_lock_reclaimers_cannot_remove_the_winner(self):
        lock_dir = self.state_root / "locks" / "stale"
        lock_dir.mkdir(parents=True)
        os.chmod(lock_dir, 0o700)
        (lock_dir / "owner.json").write_text(
            json.dumps({"pid": 424242, "token": "stale"}), encoding="utf-8"
        )
        os.chmod(lock_dir / "owner.json", 0o600)
        context = multiprocessing.get_context("fork")
        barrier = context.Barrier(2)
        acquired = context.Event()
        release = context.Event()
        results = context.Queue()
        processes = [
            context.Process(
                target=_concurrent_stale_reclaim,
                args=(str(lock_dir), barrier, acquired, release, results),
            )
            for _ in range(2)
        ]
        for process in processes:
            process.start()
        self.assertTrue(acquired.wait(5))
        release.set()
        for process in processes:
            process.join(10)
            self.assertEqual(0, process.exitcode)

        outcomes = sorted(results.get(timeout=2) for _ in processes)
        self.assertEqual(["StateLockBusy", "ok"], outcomes)
        self.assertFalse(lock_dir.exists())

    def test_public_run_and_lane_lifecycle_requires_explicit_ack(self):
        approved = self.coordinator.approve_run(
            self.run_dir,
            self.owner_file,
            decided_at="2026-07-14T01:00:00Z",
            evidence_refs=[{"kind": "approval", "summary": "user approved"}],
        )
        self.assertEqual("approved", approved["run_state"])
        running = self.coordinator.start_run(
            self.run_dir,
            self.owner_file,
            decided_at="2026-07-14T01:00:01Z",
            evidence_refs=[{"kind": "plan", "summary": "approved plan"}],
        )
        self.assertEqual("running", running["run_state"])

        created = self.coordinator.create_lane(
            self.run_dir,
            lane_id="review",
            agent_id="agent-1",
            owner_handle=self.owner_file,
            assignment="Review the exact Phase 2 diff",
            write_scope=[],
            fallback="main-session review",
            observed_at="2026-07-14T01:00:02Z",
            startup_ack_deadline="2026-07-14T01:00:30Z",
            command_deadline="2026-07-14T01:10:00Z",
            evidence_refs=[{"kind": "plan", "summary": "approved lane assignment"}],
        )
        self.assertEqual("pending", created["state"])
        started = self.coordinator.transition_lane(
            self.run_dir,
            lane_id="review",
            agent_id="agent-1",
            owner_handle=self.owner_file,
            intent="start",
            decided_at="2026-07-14T01:00:03Z",
            evidence_refs=[{"kind": "dispatch", "summary": "native agent spawned"}],
        )
        self.assertEqual("starting", started["state"])

        replayed = self.coordinator.load_coordinator_state(self.run_dir)[1]
        self.assertEqual("starting", replayed["lanes"]["review"]["state"])
        acknowledged = self.coordinator.transition_lane(
            self.run_dir,
            lane_id="review",
            agent_id="agent-1",
            owner_handle=self.owner_file,
            intent="ack",
            decided_at="2026-07-14T01:00:31Z",
            evidence_refs=[{"kind": "ack", "summary": "startup acknowledged"}],
        )
        self.assertEqual("running", acknowledged["state"])

    def test_lane_completion_enforces_canonical_pinned_write_scope(self):
        self.repo_root.joinpath("scripts").mkdir()
        outside = self.repo_root.parent / "outside"
        outside.mkdir()
        self.repo_root.joinpath("link").symlink_to(outside, target_is_directory=True)
        self.coordinator.approve_run(
            self.run_dir,
            self.owner_file,
            decided_at="2026-07-14T01:00:00Z",
            evidence_refs=[{"kind": "approval", "summary": "user approved"}],
        )
        self.coordinator.start_run(
            self.run_dir,
            self.owner_file,
            decided_at="2026-07-14T01:00:01Z",
            evidence_refs=[{"kind": "plan", "summary": "approved plan"}],
        )
        self.coordinator.create_lane(
            self.run_dir,
            lane_id="build",
            agent_id="agent-1",
            owner_handle=self.owner_file,
            assignment="Build the runtime",
            write_scope=["scripts"],
            fallback="main session",
            observed_at="2026-07-14T01:00:02Z",
            startup_ack_deadline="2026-07-14T01:00:30Z",
            command_deadline="2026-07-14T01:10:00Z",
            evidence_refs=[{"kind": "plan", "summary": "build assigned"}],
        )
        for intent, decided_at in (
            ("start", "2026-07-14T01:00:03Z"),
            ("ack", "2026-07-14T01:00:04Z"),
        ):
            self.coordinator.transition_lane(
                self.run_dir,
                lane_id="build",
                agent_id="agent-1",
                owner_handle=self.owner_file,
                intent=intent,
                decided_at=decided_at,
                evidence_refs=[{"kind": "test", "summary": intent}],
            )

        receipt = self.run_dir / "receipt.jsonl"
        invalid = (
            (ValueError, None),
            (self.coordinator.CoordinatorConflict, {"changed_paths": ["README.md"]}),
            (ValueError, {"changed_paths": ["scripts/../README.md"]}),
            (ValueError, {"changed_paths": ["link/escape.py"]}),
        )
        for error_type, metadata in invalid:
            with self.subTest(metadata=metadata):
                before = receipt.read_bytes()
                with self.assertRaises(error_type):
                    self.coordinator.transition_lane(
                        self.run_dir,
                        lane_id="build",
                        agent_id="agent-1",
                        owner_handle=self.owner_file,
                        intent="complete",
                        decided_at="2026-07-14T01:00:05Z",
                        evidence_refs=[{"kind": "result", "summary": "complete"}],
                        metadata=metadata,
                    )
                self.assertEqual(before, receipt.read_bytes())

        completed = self.coordinator.transition_lane(
            self.run_dir,
            lane_id="build",
            agent_id="agent-1",
            owner_handle=self.owner_file,
            intent="complete",
            decided_at="2026-07-14T01:00:05Z",
            evidence_refs=[{"kind": "result", "summary": "complete"}],
            metadata={"changed_paths": ["scripts/runtime.py"]},
        )
        self.assertEqual("completed", completed["state"])
        self.assertEqual(["scripts/runtime.py"], completed["changed_paths"])

    def test_lane_api_rejects_invalid_assignment_scope_owner_and_deadlines(self):
        self.append(
            "plan_approved",
            from_state="planned",
            to_state="approved",
            timestamp="2026-07-14T01:00:00Z",
        )
        self.append(
            "run_started",
            from_state="approved",
            to_state="running",
            timestamp="2026-07-14T01:00:01Z",
        )
        receipt = self.run_dir / "receipt.jsonl"
        for name, overrides in (
            ("empty-assignment", {"assignment": ""}),
            ("escape-scope", {"write_scope": ["../outside"]}),
            (
                "deadline-order",
                {"startup_ack_deadline": "2026-07-14T00:59:59Z"},
            ),
            ("unbounded", {"command_deadline": None}),
        ):
            with self.subTest(name=name):
                before = receipt.read_bytes()
                arguments = {
                    "assignment": "Review",
                    "write_scope": [],
                    "fallback": "main session",
                    "startup_ack_deadline": "2026-07-14T01:00:30Z",
                    "command_deadline": "2026-07-14T01:10:00Z",
                }
                arguments.update(overrides)
                with self.assertRaises(ValueError):
                    self.coordinator.create_lane(
                        self.run_dir,
                        lane_id="invalid-" + name,
                        agent_id="agent-1",
                        owner_handle=self.owner_file,
                        observed_at="2026-07-14T01:00:02Z",
                        evidence_refs=[{"kind": "test", "summary": name}],
                        **arguments,
                    )
                self.assertEqual(before, receipt.read_bytes())

        self.coordinator.create_lane(
            self.run_dir,
            lane_id="owned",
            agent_id="agent-1",
            owner_handle=self.owner_file,
            assignment="Owned lane",
            write_scope=[],
            fallback="main session",
            observed_at="2026-07-14T01:00:02Z",
            startup_ack_deadline="2026-07-14T01:00:30Z",
            command_deadline="2026-07-14T01:10:00Z",
            evidence_refs=[{"kind": "test", "summary": "create"}],
        )
        before = receipt.read_bytes()
        with self.assertRaises(self.coordinator.CoordinatorConflict):
            self.coordinator.transition_lane(
                self.run_dir,
                lane_id="owned",
                agent_id="agent-2",
                owner_handle=self.owner_file,
                intent="start",
                decided_at="2026-07-14T01:00:03Z",
                evidence_refs=[{"kind": "test", "summary": "wrong owner"}],
            )
        self.assertEqual(before, receipt.read_bytes())

    def test_planned_or_terminal_run_rejects_lane_mutation_without_bytes(self):
        receipt = self.run_dir / "receipt.jsonl"
        before = receipt.read_bytes()
        with self.assertRaises(self.coordinator.CoordinatorConflict):
            self.coordinator.create_lane(
                self.run_dir,
                lane_id="too-early",
                agent_id="agent-1",
                owner_handle=self.owner_file,
                assignment="Too early",
                write_scope=[],
                fallback="main session",
                observed_at="2026-07-14T01:00:00Z",
                startup_ack_deadline="2026-07-14T01:00:30Z",
                command_deadline="2026-07-14T01:10:00Z",
                evidence_refs=[{"kind": "test", "summary": "planned"}],
            )
        self.assertEqual(before, receipt.read_bytes())

        self.coordinator.approve_run(
            self.run_dir,
            self.owner_file,
            decided_at="2026-07-14T01:00:00Z",
            evidence_refs=[{"kind": "test", "summary": "approved"}],
        )
        self.coordinator.start_run(
            self.run_dir,
            self.owner_file,
            decided_at="2026-07-14T01:00:01Z",
            evidence_refs=[{"kind": "test", "summary": "running"}],
        )
        blocked = self.coordinator.terminate_run(
            self.run_dir,
            self.owner_file,
            intent="block",
            decided_at="2026-07-14T01:00:02Z",
            evidence_refs=[{"kind": "test", "summary": "blocked"}],
            reason="test blocker",
        )
        self.assertEqual("blocked", blocked["run_state"])
        before = receipt.read_bytes()
        with self.assertRaises(self.coordinator.CoordinatorConflict):
            self.coordinator.create_lane(
                self.run_dir,
                lane_id="too-late",
                agent_id="agent-1",
                owner_handle=self.owner_file,
                assignment="Too late",
                write_scope=[],
                fallback="main session",
                observed_at="2026-07-14T01:00:03Z",
                startup_ack_deadline="2026-07-14T01:00:30Z",
                command_deadline="2026-07-14T01:10:00Z",
                evidence_refs=[{"kind": "test", "summary": "terminal"}],
            )
        self.assertEqual(before, receipt.read_bytes())

    def test_reducer_tables_cover_manifest_approved_lifecycle_triples(self):
        expected_run = {
            "approve": ("plan_approved", {"planned"}, "approved"),
            "start": ("run_started", {"approved"}, "running"),
            "recovery_start": (
                "run_recovery_started",
                {"running"},
                "recovering",
            ),
            "recovery_finish": (
                "run_recovery_finished",
                {"recovering"},
                "running",
            ),
            "fail": ("run_failed", {"running", "recovering"}, "failed"),
            "block": ("run_blocked", {"running", "recovering"}, "blocked"),
            "cancel": (
                "run_cancelled",
                {"planned", "approved", "running", "recovering"},
                "cancelled",
            ),
        }
        expected_lane = {
            "start": ("lane_started", {"pending"}, "starting"),
            "ack": ("startup_ack", {"starting"}, "running"),
            "stall": (
                "stall_suspected",
                {"starting", "running"},
                "suspected_stall",
            ),
            "clear_stall": (
                "lane_recovered",
                {"suspected_stall"},
                "running",
            ),
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
        self.assertEqual(expected_run, self.coordinator.RUN_INTENT_TRANSITIONS)
        self.assertEqual(expected_lane, self.coordinator.LANE_INTENT_TRANSITIONS)

        manifest = self.runtime.load_run_manifest_snapshot(self.run_dir)["manifest"]
        fingerprint = self.initialized["owner_fingerprint"]
        for intent, (event_type, sources, target) in expected_run.items():
            for source in sources:
                with self.subTest(kind="run", intent=intent, source=source):
                    state = self.coordinator.empty_coordinator_state(
                        {
                            "owner_fingerprint": fingerprint,
                            "owner_epoch": 1,
                            "component_ids": [],
                        }
                    )
                    state["run_state"] = source
                    state["last_sequence"] = 1
                    self.coordinator.apply_event(
                        state,
                        {
                            "sequence": 2,
                            "event_type": event_type,
                            "from_state": source,
                            "to_state": target,
                            "timestamp": "2026-07-14T01:00:00Z",
                            "owner_token": fingerprint,
                            "checksum": "a" * 64,
                            "evidence_refs": [
                                {"kind": "test", "summary": intent}
                            ],
                            "metadata": {"owner_epoch": 1},
                        },
                        manifest,
                    )
                    self.assertEqual(target, state["run_state"])

        for intent, (event_type, sources, target) in expected_lane.items():
            for source in sources:
                with self.subTest(kind="lane", intent=intent, source=source):
                    state = self.coordinator.empty_coordinator_state(
                        {
                            "owner_fingerprint": fingerprint,
                            "owner_epoch": 1,
                            "component_ids": [],
                        }
                    )
                    state["run_state"] = "running"
                    state["last_sequence"] = 1
                    state["lanes"]["lane"] = {
                        "id": "lane",
                        "state": source,
                        "agent_id": "agent-1",
                        "evidence_refs": [],
                    }
                    self.coordinator.apply_event(
                        state,
                        {
                            "sequence": 2,
                            "event_type": event_type,
                            "lane_id": "lane",
                            "agent_id": "agent-1",
                            "from_state": source,
                            "to_state": target,
                            "timestamp": "2026-07-14T01:00:00Z",
                            "owner_token": fingerprint,
                            "checksum": "b" * 64,
                            "evidence_refs": [
                                {"kind": "test", "summary": intent}
                            ],
                            "metadata": {"owner_epoch": 1},
                        },
                        manifest,
                    )
                    self.assertEqual(target, state["lanes"]["lane"]["state"])

    def test_ack_requires_evidence_and_invalid_transition_changes_no_bytes(self):
        self.running_events_with_pending_lane()
        self.coordinator.transition_lane(
            self.run_dir,
            lane_id="review",
            agent_id="agent-1",
            owner_handle=self.owner_file,
            intent="start",
            decided_at="2026-07-14T01:00:04Z",
            evidence_refs=[{"kind": "test", "summary": "started"}],
        )
        receipt = self.run_dir / "receipt.jsonl"
        before = receipt.read_bytes()
        with self.assertRaises(ValueError):
            self.coordinator.transition_lane(
                self.run_dir,
                lane_id="review",
                agent_id="agent-1",
                owner_handle=self.owner_file,
                intent="ack",
                decided_at="2026-07-14T01:00:05Z",
                evidence_refs=[],
            )
        self.assertEqual(before, receipt.read_bytes())
        with self.assertRaises(self.coordinator.CoordinatorConflict):
            self.coordinator.transition_lane(
                self.run_dir,
                lane_id="review",
                agent_id="agent-1",
                owner_handle=self.owner_file,
                intent="start",
                decided_at="2026-07-14T01:00:05Z",
                evidence_refs=[{"kind": "test", "summary": "duplicate start"}],
            )
        self.assertEqual(before, receipt.read_bytes())

    def test_stale_owner_epoch_is_rejected_before_receipt_mutation(self):
        owner = json.loads(self.owner_file.read_text(encoding="utf-8"))
        owner["epoch"] = 2
        self.owner_file.write_text(json.dumps(owner), encoding="utf-8")
        receipt = self.run_dir / "receipt.jsonl"
        before = receipt.read_bytes()
        with self.assertRaises(self.runtime.StateLockBusy):
            self.coordinator.approve_run(
                self.run_dir,
                self.owner_file,
                decided_at="2026-07-14T01:00:00Z",
                evidence_refs=[{"kind": "test", "summary": "stale"}],
            )
        self.assertEqual(before, receipt.read_bytes())


if __name__ == "__main__":
    unittest.main()
