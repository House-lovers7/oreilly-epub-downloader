from __future__ import annotations

import json
import unittest
from pathlib import Path


class EvalAssetTests(unittest.TestCase):
    def test_utility_case_set_has_required_positive_and_negative_coverage(self) -> None:
        root = Path(__file__).resolve().parents[1]
        cases = json.loads(
            (root / "evals" / "skill-utility-cases.json").read_text(encoding="utf-8")
        )

        self.assertEqual(len(cases), 12)
        self.assertEqual(len({case["task_id"] for case in cases}), 12)
        self.assertGreaterEqual(
            sum(case["should_use_library"] is False for case in cases), 4
        )
        for case in cases:
            self.assertIn(case["expected_first_source"], {"codebase", "library", "official_docs"})
            self.assertTrue(case["acceptance_notes"])

    def test_eval_protocol_and_observation_schema_are_versioned(self) -> None:
        root = Path(__file__).resolve().parents[1]
        schema = json.loads(
            (root / "evals" / "utility-observation.schema.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIn("task_id", schema["required"])
        self.assertTrue((root / "evals" / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
