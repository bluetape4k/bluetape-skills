import importlib.util
import json
import os
import tempfile
import time
import unittest
from pathlib import Path


RUNTIME_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "bluetape_runtime.py"
)


def load_runtime():
    spec = importlib.util.spec_from_file_location("bluetape_runtime_lock", RUNTIME_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StateLockTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = load_runtime()

    def write_owner(self, lock_dir, pid=424242, token="stale-token"):
        lock_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(lock_dir, 0o700)
        (lock_dir / "owner.json").write_text(
            json.dumps({"pid": pid, "token": token}), encoding="utf-8"
        )
        os.chmod(lock_dir / "owner.json", 0o600)

    def test_live_owner_is_never_reaped(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            lock_dir = Path(temp_dir) / "state.lock"
            self.write_owner(lock_dir)

            with self.assertRaises(self.runtime.StateLockBusy):
                with self.runtime.state_lock(
                    lock_dir, pid_probe=lambda pid: "alive"
                ):
                    pass

            owner = json.loads(
                (lock_dir / "owner.json").read_text(encoding="utf-8")
            )
            self.assertEqual("stale-token", owner["token"])

    def test_permission_denied_owner_is_treated_as_busy(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            lock_dir = Path(temp_dir) / "state.lock"
            self.write_owner(lock_dir)

            with self.assertRaises(self.runtime.StateLockBusy):
                with self.runtime.state_lock(
                    lock_dir, pid_probe=lambda pid: "unknown"
                ):
                    pass

    def test_dead_owner_with_stable_token_is_recovered(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            lock_dir = Path(temp_dir) / "state.lock"
            self.write_owner(lock_dir)

            with self.runtime.state_lock(
                lock_dir, pid_probe=lambda pid: "dead"
            ) as owner:
                self.assertEqual(os.getpid(), owner["pid"])
                self.assertNotEqual("stale-token", owner["token"])
                self.assertTrue(lock_dir.is_dir())

            self.assertFalse(lock_dir.exists())

    def test_owner_token_change_blocks_recovery(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            lock_dir = Path(temp_dir) / "state.lock"
            self.write_owner(lock_dir)

            def change_owner(_pid):
                self.write_owner(lock_dir, token="replacement-token")
                return "dead"

            with self.assertRaises(self.runtime.StateLockBusy):
                with self.runtime.state_lock(lock_dir, pid_probe=change_owner):
                    pass

            owner = json.loads(
                (lock_dir / "owner.json").read_text(encoding="utf-8")
            )
            self.assertEqual("replacement-token", owner["token"])

    def test_owned_lock_is_removed_after_failure_in_context(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            lock_dir = Path(temp_dir) / "state.lock"

            with self.assertRaisesRegex(RuntimeError, "boom"):
                with self.runtime.state_lock(lock_dir):
                    raise RuntimeError("boom")

            self.assertFalse(lock_dir.exists())

    def test_old_empty_lock_directory_is_recovered(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            lock_dir = Path(temp_dir) / "state.lock"
            lock_dir.mkdir()
            os.chmod(lock_dir, 0o700)
            stale = time.time() - 60
            os.utime(lock_dir, (stale, stale))

            with self.runtime.state_lock(lock_dir) as owner:
                self.assertEqual(os.getpid(), owner["pid"])

            self.assertFalse(lock_dir.exists())

    def test_live_initializer_protects_delayed_empty_lock(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            lock_dir = Path(temp_dir) / "state.lock"
            lock_dir.mkdir()
            os.chmod(lock_dir, 0o700)
            stale = time.time() - 60
            os.utime(lock_dir, (stale, stale))
            initializer = Path(temp_dir) / ".state.lock.initializing.json"
            initializer.write_text(
                json.dumps({"pid": os.getpid(), "token": "initializing"}),
                encoding="utf-8",
            )
            os.chmod(initializer, 0o600)

            with self.assertRaises(self.runtime.StateLockBusy):
                with self.runtime.state_lock(
                    lock_dir, pid_probe=lambda pid: "alive"
                ):
                    pass

            self.assertTrue(lock_dir.is_dir())
            self.assertTrue(initializer.is_file())

    def test_stale_recovery_claim_is_reclaimed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            lock_dir = Path(temp_dir) / "state.lock"
            self.write_owner(lock_dir)
            claim = lock_dir / ".reclaim.json"
            claim.write_text(
                json.dumps({"pid": 424242, "nonce": "stale-claim"}),
                encoding="utf-8",
            )
            os.chmod(claim, 0o600)
            stale = time.time() - 60
            os.utime(claim, (stale, stale))

            with self.runtime.state_lock(
                lock_dir, pid_probe=lambda pid: "dead"
            ) as owner:
                self.assertEqual(os.getpid(), owner["pid"])

            self.assertFalse(lock_dir.exists())

    def test_insecure_existing_lock_or_owner_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            for insecure_target in ("lock", "owner"):
                with self.subTest(insecure_target=insecure_target):
                    lock_dir = Path(temp_dir) / (insecure_target + ".lock")
                    self.write_owner(lock_dir)
                    target = (
                        lock_dir
                        if insecure_target == "lock"
                        else lock_dir / "owner.json"
                    )
                    os.chmod(target, 0o755 if insecure_target == "lock" else 0o644)

                    with self.assertRaisesRegex(
                        self.runtime.StateLockBusy, "insecure"
                    ):
                        with self.runtime.state_lock(
                            lock_dir, pid_probe=lambda pid: "dead"
                        ):
                            pass

    def test_empty_lock_rejects_unsafe_initializer_before_read(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            external = root / "external.json"
            external.write_text(
                json.dumps({"pid": os.getpid(), "token": "external"}),
                encoding="utf-8",
            )
            os.chmod(external, 0o600)

            for kind in ("symlink", "insecure-mode"):
                with self.subTest(kind=kind):
                    lock_dir = root / (kind + ".lock")
                    lock_dir.mkdir(mode=0o700)
                    os.chmod(lock_dir, 0o700)
                    stale = time.time() - 60
                    os.utime(lock_dir, (stale, stale))
                    initializer = root / ("." + lock_dir.name + ".initializing.json")
                    if kind == "symlink":
                        initializer.symlink_to(external)
                    else:
                        initializer.write_text(
                            json.dumps(
                                {"pid": os.getpid(), "token": "insecure"}
                            ),
                            encoding="utf-8",
                        )
                        os.chmod(initializer, 0o644)

                    with self.assertRaisesRegex(
                        self.runtime.StateLockBusy, "initializer is unsafe"
                    ):
                        with self.runtime.state_lock(
                            lock_dir, pid_probe=lambda pid: "alive"
                        ):
                            pass

            self.assertEqual(
                {"pid": os.getpid(), "token": "external"},
                json.loads(external.read_text(encoding="utf-8")),
            )


if __name__ == "__main__":
    unittest.main()
