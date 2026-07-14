"""Optional mmap-backed vector search, loaded only after lexical miss."""
from __future__ import annotations

import heapq
import json
import sqlite3
from pathlib import Path
from typing import Any, Callable


class LazyVectorSearch:
    def __init__(
        self,
        kb_dir: Path,
        *,
        embed_query: Callable[[str, str], list[float]] | None = None,
        max_working_bytes: int = 256 * 1024 * 1024,
    ):
        self.kb_dir = Path(kb_dir)
        self.embed_query = embed_query
        self.max_working_bytes = max_working_bytes

    def __call__(self, query: str, limit: int) -> list[dict[str, Any]]:
        npy = self.kb_dir / "index" / "embeddings.npy"
        meta_path = self.kb_dir / "index" / "embeddings_meta.json"
        db = self.kb_dir / "index" / "library.sqlite"
        if not (npy.exists() and meta_path.exists() and db.exists()):
            return []
        try:
            import numpy as np

            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            chunk_ids = list(meta.get("chunk_ids", []))
            matrix = np.load(npy, mmap_mode="r")
            if matrix.ndim != 2 or matrix.shape[0] != len(chunk_ids):
                return []
            embed = self.embed_query or _ollama_embed_query
            query_vector = np.asarray(
                embed(query, str(meta.get("model", "bge-m3"))), dtype=np.float32
            )
            if query_vector.ndim != 1 or query_vector.shape[0] != matrix.shape[1]:
                return []
            query_norm = float(np.linalg.norm(query_vector))
            if query_norm == 0:
                return []
            query_vector /= query_norm

            bytes_per_row = max(1, matrix.shape[1] * 4 * 3)
            block_rows = max(256, min(8192, self.max_working_bytes // bytes_per_row))
            best: list[tuple[float, int]] = []
            for start in range(0, matrix.shape[0], block_rows):
                stop = min(start + block_rows, matrix.shape[0])
                block = np.asarray(matrix[start:stop], dtype=np.float32)
                norms = np.linalg.norm(block, axis=1)
                scores = block @ query_vector
                scores = np.divide(scores, norms, out=np.zeros_like(scores), where=norms > 0)
                local_count = min(limit, len(scores))
                if local_count == 0:
                    continue
                indices = np.argpartition(scores, -local_count)[-local_count:]
                for local_index in indices:
                    candidate = (float(scores[local_index]), start + int(local_index))
                    if len(best) < limit:
                        heapq.heappush(best, candidate)
                    elif candidate[0] > best[0][0]:
                        heapq.heapreplace(best, candidate)
            ranked = sorted(best, reverse=True)
            return _fetch_results(db, [(score, chunk_ids[index]) for score, index in ranked])
        except (OSError, ValueError, KeyError, sqlite3.Error):
            return []


def _ollama_embed_query(query: str, model: str) -> list[float]:
    import httpx

    response = httpx.post(
        "http://127.0.0.1:11434/api/embed",
        json={"model": model, "input": [query]},
        timeout=3.0,
        trust_env=False,
    )
    response.raise_for_status()
    payload = response.json()
    embeddings = payload.get("embeddings") or []
    if len(embeddings) != 1:
        raise ValueError("embedding backend returned an unexpected vector count")
    return list(embeddings[0])


def _fetch_results(db: Path, ranked: list[tuple[float, str]]) -> list[dict[str, Any]]:
    if not ranked:
        return []
    ids = [chunk_id for _, chunk_id in ranked]
    placeholders = ",".join("?" for _ in ids)
    with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            f"""
            SELECT chunk_id, doc_id, title, heading, source_ref, source_path,
                   source_type, text
            FROM chunks WHERE chunk_id IN ({placeholders})
            """,
            ids,
        ).fetchall()
    by_id = {row["chunk_id"]: dict(row) for row in rows}
    output: list[dict[str, Any]] = []
    for score, chunk_id in ranked:
        if chunk_id not in by_id:
            continue
        item = by_id[chunk_id]
        text = " ".join(str(item.pop("text", "")).split())
        item["excerpt"] = text[:700] + ("…" if len(text) > 700 else "")
        item["score"] = score
        output.append(item)
    return output
