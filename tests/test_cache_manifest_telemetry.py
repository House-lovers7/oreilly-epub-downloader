from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from techlib.cache import CacheManager
from techlib.manifest import build_source_manifest, manifest_is_stale
from techlib.telemetry import MetadataTelemetry


class ManifestTests(unittest.TestCase):
    def test_source_hash_detects_staleness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.epub"
            source.write_bytes(b"version-one")
            manifest = build_source_manifest(
                source, rights="personal-subscription", extractor_version="1"
            )

            self.assertEqual(len(manifest["source_sha256"]), 64)
            self.assertFalse(manifest_is_stale(manifest, source))

            source.write_bytes(b"version-two")
            self.assertTrue(manifest_is_stale(manifest, source))


class CacheTests(unittest.TestCase):
    def test_prune_plan_excludes_original_epubs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            raw = repo / "downloads" / "source.epub"
            old_cache = repo / "knowledge-base" / "books" / "old.md"
            embedding = repo / "knowledge-base" / "index" / "embeddings.npy"
            for path, data in (
                (raw, b"r" * 20),
                (old_cache, b"c" * 30),
                (embedding, b"e" * 40),
            ):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            os.utime(old_cache, (1, 1))

            manager = CacheManager(repo, soft_limit_bytes=50)
            status = manager.status()
            plan = manager.prune_plan(target_bytes=40)

            self.assertEqual(status.raw_bytes, 20)
            self.assertEqual(status.derived_bytes, 70)
            self.assertTrue(status.warning)
            self.assertIn(old_cache, plan)
            self.assertNotIn(raw, plan)
            self.assertTrue(raw.exists())


class TelemetryTests(unittest.TestCase):
    def test_raw_query_and_output_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            telemetry = MetadataTelemetry(Path(tmp) / "events.jsonl")
            with self.assertRaises(ValueError):
                telemetry.record(
                    {
                        "event": "search",
                        "stage": "fts",
                        "query": "private query text",
                        "output": "copyrighted excerpt",
                    }
                )

    def test_metadata_event_is_append_only_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            telemetry = MetadataTelemetry(path)
            telemetry.record(
                {
                    "event": "search",
                    "stage": "cards",
                    "result_count": 1,
                    "card_ids": ["arch-p-001"],
                    "accepted": True,
                }
            )
            payload = json.loads(path.read_text(encoding="utf-8").strip())
            self.assertEqual(payload["card_ids"], ["arch-p-001"])
            self.assertIn("recorded_at", payload)


if __name__ == "__main__":
    unittest.main()
