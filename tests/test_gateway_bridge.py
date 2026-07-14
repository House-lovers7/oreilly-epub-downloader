from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.install_gateway_bridge import configure_bridge


class GatewayBridgeTests(unittest.TestCase):
    def test_dry_run_does_not_modify_gateway(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gateway = root / "_tool_gateway" / "tool_gateway.py"
            gateway.parent.mkdir(parents=True)
            original = 'TECH_LIBRARY_SCRIPT = ROOT / "_technical_library" / "technical_library.py"\n'
            gateway.write_text(original, encoding="utf-8")

            result = configure_bridge(gateway, write=False)

            self.assertTrue(result["change_required"])
            self.assertFalse(result["changed"])
            self.assertEqual(gateway.read_text(encoding="utf-8"), original)

    def test_write_and_rollback_are_atomic_and_reversible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gateway = root / "_tool_gateway" / "tool_gateway.py"
            gateway.parent.mkdir(parents=True)
            gateway.write_text(
                'TECH_LIBRARY_SCRIPT = ROOT / "_technical_library" / "technical_library.py"\n',
                encoding="utf-8",
            )

            applied = configure_bridge(gateway, write=True)
            self.assertTrue(applied["changed"])
            self.assertIn("oreilly-epub-downloader", gateway.read_text(encoding="utf-8"))

            rolled_back = configure_bridge(gateway, write=True, rollback=True)
            self.assertTrue(rolled_back["changed"])
            self.assertIn("_technical_library", gateway.read_text(encoding="utf-8"))

    def test_unknown_gateway_assignment_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gateway = Path(tmp) / "tool_gateway.py"
            gateway.write_text("TECH_LIBRARY_SCRIPT = custom_path\n", encoding="utf-8")

            with self.assertRaises(RuntimeError):
                configure_bridge(gateway, write=True)


if __name__ == "__main__":
    unittest.main()
