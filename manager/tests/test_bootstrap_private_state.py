"""Public-safe private-state bootstrap behavior tests: never publishes real queues."""
import tempfile
import unittest
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location
ROOT=Path(__file__).resolve().parents[1]
spec=spec_from_file_location("bootstrap_private_state",ROOT/"scripts/bootstrap_private_state.py")
mod=module_from_spec(spec)
spec.loader.exec_module(mod)

class BootstrapTests(unittest.TestCase):
    def test_init_empty_private_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/"state"
            result=mod.bootstrap(dest)
            self.assertEqual(result,dest)
            self.assertTrue((dest/"PROJECT_QUEUE.md").exists())
            self.assertTrue((dest/"FACTORY_POLICY.md").exists())
            self.assertNotIn("https://github.com/ahpa5246-lgtm/",(dest/"PROJECT_QUEUE.md").read_text())
            self.assertIn("No executions",(dest/"WORK_LOG.md").read_text())
            with self.assertRaises(ValueError):
                mod.bootstrap(dest)
    def test_reject_symlink_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);existing=p/"real";existing.mkdir()
            alias=p/"alias";alias.symlink_to(existing,target_is_directory=True)
            with self.assertRaises(ValueError):
                mod.bootstrap(alias)
            self.assertEqual(list(existing.iterdir()),[])

if __name__=="__main__":
    unittest.main()
