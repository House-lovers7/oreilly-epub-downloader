#!/usr/bin/env python3
"""domain-pack 互換の source-pack.jsonl / manifest.json を doc_id 許可リストに限定して作る。
使い方: python3 scripts/domain_pack_filtered.py game-design --kb-dir knowledge-base --docs docs-game.txt \
        --query "core loop" --query "game balance" --max-chunks 160 --limit-per-query 40 [--output-dir DIR]
docs ファイル: 1 行 1 doc_id（# コメント可）"""
import argparse, json, sqlite3, re, datetime as dt
from pathlib import Path

def fts(q):
    return " AND ".join('"' + t.replace('"', '') + '"' for t in re.split(r"\s+", q.strip()) if t)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("domain")
    ap.add_argument("--kb-dir", required=True); ap.add_argument("--docs", required=True)
    ap.add_argument("--query", action="append", required=True)
    ap.add_argument("--limit-per-query", type=int, default=40); ap.add_argument("--max-chunks", type=int, default=160)
    ap.add_argument("--output-dir"); a = ap.parse_args()
    kb = Path(a.kb_dir).resolve()
    docs = [l.strip() for l in Path(a.docs).read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    con = sqlite3.connect(kb / "index" / "library.sqlite"); ph = ",".join("?" * len(docs)); best = {}
    for q in a.query:
        sql = f"""SELECT c.chunk_id, c.doc_id, c.title, c.heading, c.source_ref, c.text, bm25(chunks_fts) AS score
                  FROM chunks_fts JOIN chunks c ON c.chunk_id = chunks_fts.chunk_id
                  WHERE chunks_fts MATCH ? AND c.doc_id IN ({ph}) ORDER BY score LIMIT ?"""
        for cid, did, title, heading, ref, text, score in con.execute(sql, (fts(q), *docs, a.limit_per_query)):
            e = best.get(cid)
            if e is None:
                best[cid] = {"chunk_id": cid, "doc_id": did, "title": title, "heading": heading, "source_ref": ref,
                             "score": score, "matched_queries": [q], "text": text}
            else:
                e["matched_queries"].append(q); e["score"] = min(e["score"], score)
    rows = sorted(best.values(), key=lambda r: r["score"])[: a.max_chunks]
    out = Path(a.output_dir).resolve() if a.output_dir else kb / "cards" / a.domain
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "source-pack.jsonl", "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    manifest = {"domain": a.domain, "queries": a.query, "doc_filter": docs, "chunk_count": len(rows),
                "book_count": len({r["doc_id"] for r in rows}), "generated_at": dt.datetime.now().astimezone().isoformat(),
                "kb_dir": str(kb), "pack_path": str(out / "source-pack.jsonl"),
                "policy": "Local distillation material only. Cards derived from this pack must be reconstructions (decision criteria, procedures, pitfalls), not long quotations."}
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "manifest": manifest}, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
