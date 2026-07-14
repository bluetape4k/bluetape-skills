import importlib.util
import json
import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = SKILL_ROOT / "scripts" / "bluetape_runtime.py"
MANIFEST_PATH = SKILL_ROOT / "references" / "workflow-manifest.json"


def load_runtime():
    spec = importlib.util.spec_from_file_location(
        "bluetape_runtime_security", RUNTIME_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class RuntimeSecurityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = load_runtime()

    def test_identifier_and_state_path_reject_escape(self):
        for value in ("", ".", "..", "../run", "/tmp/run", "a/b", "a\\b", "x\n"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.runtime.validate_identifier(value)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            with self.assertRaises(ValueError):
                self.runtime.validate_state_path(root, "../outside")

    def test_write_scope_is_canonical_and_contained(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            (repo / "safe").mkdir()
            self.assertEqual(
                ["safe"], self.runtime.canonicalize_write_scope(repo, ["safe"])
            )
            for scope in ("/tmp", "../escape", "safe/*", "safe\\alias"):
                with self.subTest(scope=scope):
                    with self.assertRaises(ValueError):
                        self.runtime.canonicalize_write_scope(repo, [scope])

    def test_write_scope_honors_pinned_manifest_limit(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            limits = dict(self.runtime.RESOURCE_LIMITS)
            limits["max_write_scopes"] = 1

            with self.assertRaisesRegex(ValueError, "bounded list"):
                self.runtime.canonicalize_write_scope(
                    repo, ["first", "second"], limits=limits
                )

    def test_initialize_run_uses_secure_modes_and_never_persists_raw_owner(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_root = Path(temp_dir) / ".bluetape"
            repo_root = Path(temp_dir) / "repo"
            repo_root.mkdir()
            owner_file = state_root / "handles" / "phase2.owner"

            initialized = self.runtime.initialize_run(
                state_root,
                workflow_type="A",
                repo_root=repo_root,
                component_ids=["runtime"],
                owner_file=owner_file,
                manifest_path=MANIFEST_PATH,
            )

            raw_owner = json.loads(owner_file.read_text(encoding="utf-8"))["token"]
            run_dir = state_root / "runs" / initialized["run_id"]
            self.assertEqual(0o600, stat.S_IMODE(owner_file.stat().st_mode))
            self.assertEqual(
                {owner_file}, set((state_root / "handles").iterdir())
            )
            for directory in (state_root, state_root / "runs", run_dir):
                self.assertEqual(0o700, stat.S_IMODE(directory.stat().st_mode))
            for path in (
                state_root / "config.json",
                run_dir / "manifest.json",
                run_dir / "receipt.jsonl",
                run_dir / "run.json",
            ):
                self.assertEqual(0o600, stat.S_IMODE(path.stat().st_mode))
                self.assertNotIn(raw_owner, path.read_text(encoding="utf-8"))
            self.assertNotIn("owner_token", initialized)

    def test_insecure_or_symlinked_state_root_is_rejected_before_mutation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            parent = Path(temp_dir)
            repo_root = parent / "repo"
            repo_root.mkdir()
            insecure = parent / "insecure"
            insecure.mkdir(mode=0o777)
            os.chmod(insecure, 0o777)
            with self.assertRaisesRegex(ValueError, "secure mode"):
                self.runtime.initialize_run(
                    insecure,
                    workflow_type="A",
                    repo_root=repo_root,
                    component_ids=["runtime"],
                    owner_file=insecure / "handles" / "insecure.owner",
                    manifest_path=MANIFEST_PATH,
                )

            target = parent / "target"
            target.mkdir()
            link = parent / "link"
            link.symlink_to(target, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                self.runtime.initialize_run(
                    link,
                    workflow_type="A",
                    repo_root=repo_root,
                    component_ids=["runtime"],
                    owner_file=link / "handles" / "symlink.owner",
                    manifest_path=MANIFEST_PATH,
                )

    def test_mutation_rejects_symlinked_lane_cache_parent_before_append(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_root = root / ".bluetape"
            repo_root = root / "repo"
            repo_root.mkdir()
            owner_file = state_root / "handles" / "phase2.owner"
            initialized = self.runtime.initialize_run(
                state_root,
                workflow_type="A",
                repo_root=repo_root,
                component_ids=["runtime"],
                owner_file=owner_file,
                manifest_path=MANIFEST_PATH,
            )
            run_dir = state_root / "runs" / initialized["run_id"]
            coordinator = self.runtime._load_coordinator_module()
            coordinator.approve_run(
                run_dir,
                owner_file,
                "2026-07-14T00:00:01Z",
                [{"kind": "approval", "summary": "approved"}],
            )
            coordinator.start_run(
                run_dir,
                owner_file,
                "2026-07-14T00:00:02Z",
                [{"kind": "plan", "summary": "started"}],
            )
            lanes = run_dir / "lanes"
            if lanes.exists():
                shutil.rmtree(lanes)
            outside = root / "outside"
            outside.mkdir()
            lanes.symlink_to(outside, target_is_directory=True)
            before = (run_dir / "receipt.jsonl").read_bytes()

            with self.assertRaisesRegex(ValueError, "symlink"):
                coordinator.create_lane(
                    run_dir,
                    "unsafe",
                    "agent-1",
                    owner_file,
                    "must not escape",
                    [],
                    "main session",
                    "2026-07-14T00:00:03Z",
                    "2026-07-14T00:00:30Z",
                    "2026-07-14T00:10:00Z",
                    [{"kind": "plan", "summary": "unsafe lane"}],
                )

            self.assertEqual(before, (run_dir / "receipt.jsonl").read_bytes())
            self.assertEqual([], list(outside.iterdir()))

    def test_mutation_rejects_owner_handle_outside_handles_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_root = root / ".bluetape"
            repo_root = root / "repo"
            repo_root.mkdir()
            owner_file = state_root / "handles" / "phase2.owner"
            initialized = self.runtime.initialize_run(
                state_root,
                workflow_type="A",
                repo_root=repo_root,
                component_ids=["runtime"],
                owner_file=owner_file,
                manifest_path=MANIFEST_PATH,
            )
            run_dir = state_root / "runs" / initialized["run_id"]
            outside_owner = root / "copied.owner"
            shutil.copyfile(owner_file, outside_owner)
            os.chmod(outside_owner, 0o600)
            before = (run_dir / "receipt.jsonl").read_bytes()

            with self.assertRaisesRegex(ValueError, "handles"):
                self.runtime.mutate_receipt(
                    run_dir,
                    outside_owner,
                    lambda _state: [],
                )

            self.assertEqual(before, (run_dir / "receipt.jsonl").read_bytes())

    def test_mutation_rejects_run_directory_replaced_by_symlink(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_root = root / ".bluetape"
            repo_root = root / "repo"
            repo_root.mkdir()
            owner_file = state_root / "handles" / "phase2.owner"
            initialized = self.runtime.initialize_run(
                state_root,
                workflow_type="A",
                repo_root=repo_root,
                component_ids=["runtime"],
                owner_file=owner_file,
                manifest_path=MANIFEST_PATH,
            )
            run_dir = state_root / "runs" / initialized["run_id"]
            outside_run = root / "outside-run"
            shutil.copytree(run_dir, outside_run)
            shutil.rmtree(run_dir)
            run_dir.symlink_to(outside_run, target_is_directory=True)
            before = (outside_run / "receipt.jsonl").read_bytes()
            coordinator = self.runtime._load_coordinator_module()

            with self.assertRaisesRegex(Exception, "symlink"):
                coordinator.inspect_resume(run_dir)

            with self.assertRaisesRegex(
                Exception, "snapshot is unsafe"
            ):
                coordinator.approve_run(
                    run_dir,
                    owner_file,
                    "2026-07-14T00:00:01Z",
                    [{"kind": "approval", "summary": "must remain contained"}],
                )

            self.assertEqual(before, (outside_run / "receipt.jsonl").read_bytes())

    def test_secure_artifact_directories_reject_symlink_targets(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            outside = root / "outside"
            outside.mkdir(mode=0o700)
            sentinel = outside / "sentinel"
            sentinel.write_text("unchanged", encoding="utf-8")

            for name in ("reports", "quarantine", "locks"):
                with self.subTest(name=name):
                    link = root / name
                    link.symlink_to(outside, target_is_directory=True)
                    with self.assertRaisesRegex(ValueError, "symlink"):
                        self.runtime._ensure_secure_directory(link)
                    link.unlink()

            self.assertEqual("unchanged", sentinel.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
