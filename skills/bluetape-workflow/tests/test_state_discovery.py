import importlib.util
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = SKILL_ROOT / "scripts" / "bluetape_runtime.py"


def load_runtime():
    spec = importlib.util.spec_from_file_location(
        "bluetape_runtime_state", MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class StateDiscoveryTest(unittest.TestCase):
    def setUp(self):
        self.runtime = load_runtime()
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def test_environment_override_wins(self):
        chosen = self.root / "explicit"
        result = self.runtime.discover_state_root(
            start=self.root,
            env={"BLUETAPE_STATE_ROOT": str(chosen)},
            home=self.home,
        )
        self.assertEqual(chosen.resolve(), result)

    def test_direct_override_wins_over_environment(self):
        direct = self.root / "direct"
        environment = self.root / "environment"
        result = self.runtime.discover_state_root(
            start=self.root,
            state_root=direct,
            env={"BLUETAPE_STATE_ROOT": str(environment)},
            home=self.home,
        )
        self.assertEqual(direct.resolve(), result)

    def test_nearest_workspace_config_wins(self):
        workspace = self.root / "workspace"
        nested = workspace / "repo" / "module"
        nested.mkdir(parents=True)
        state = workspace / ".bluetape"
        state.mkdir()
        (state / "config.json").write_text("{}\n", encoding="utf-8")
        result = self.runtime.discover_state_root(
            start=nested, env={}, home=self.home
        )
        self.assertEqual(state.resolve(), result)

    def test_managed_bluetape_workspace_precedes_xdg(self):
        workspace = self.home / "work" / "bluetape4k"
        workspace.mkdir(parents=True)
        result = self.runtime.discover_state_root(
            start=self.root,
            env={"XDG_STATE_HOME": str(self.root / "xdg")},
            home=self.home,
        )
        self.assertEqual((workspace / ".bluetape").resolve(), result)

    def test_xdg_is_the_final_fallback(self):
        result = self.runtime.discover_state_root(
            start=self.root,
            env={"XDG_STATE_HOME": str(self.root / "xdg")},
            home=self.home,
        )
        self.assertEqual((self.root / "xdg" / "bluetape-skills").resolve(), result)


if __name__ == "__main__":
    unittest.main()
