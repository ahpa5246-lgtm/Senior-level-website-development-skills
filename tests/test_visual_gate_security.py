"""Regression tests for competitive visual evidence input boundaries.

Run: python -m unittest discover -s tests -p 'test_visual_gate_security.py'
"""
import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "visual_quality_gate", ROOT / "scripts" / "visual_quality_gate.py"
)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class VisualGateSecurityTests(unittest.TestCase):
    def test_reference_url_rejects_credentials_and_unsafe_schemes(self):
        for value in (
            "http://example.org", "javascript:alert(1)",
            "https://user:pass@example.org/visual", "https://example.localhost/",
            "https://example.example/", "https://example.org@",
        ):
            with self.subTest(value=value):
                self.assertFalse(gate.valid_url(value))

    def test_screenshot_rejects_traversal_and_absolute_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in ("../outside.png", "/tmp/outside.png", "./capture.png", r"..\\outside.png"):
                with self.subTest(name=name):
                    self.assertFalse(gate.check_screenshot(directory, name))

    def test_screenshot_requires_real_image_file_with_size_bounds(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "small.png").write_bytes(b"x" * 99)
            (root / "valid.png").write_bytes(b"\\x89PNG\\r\\n\\x1a\\n" + b"x" * 92)
            (root / "invalid.txt").write_bytes(b"x" * 100)
            self.assertFalse(gate.check_screenshot(root, "small.png"))
            self.assertTrue(gate.check_screenshot(root, "valid.png"))
            (root / "fake.png").write_bytes(b"x" * 100)
            self.assertFalse(gate.check_screenshot(root, "fake.png"))
            self.assertFalse(gate.check_screenshot(root, "invalid.txt"))

    def test_safe_read_rejects_oversized_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            path.write_bytes(b"x" * (gate.MAX_BYTES + 1))
            with self.assertRaises(ValueError):
                gate.safe_read(path)


if __name__ == "__main__":
    unittest.main()
