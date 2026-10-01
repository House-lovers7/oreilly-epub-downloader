#!/usr/bin/env python3
"""domain-pack 互換の source-pack.jsonl / manifest.json を doc_id 許可リストに限定して作る。
使い方: python3 scripts/domain_pack_filtered.py game-design --kb-dir knowledge-base --docs docs-game.txt \
        --query "core loop" --query "game balance" --max-chunks 160 --limit-per-query 40 [--output-dir DIR] [--like-fallback]
docs ファイル: 1 行 1 doc_id（# コメント可）
--like-fallback: FTS が 0 件の query だけ LIKE（空白区切り各語の AND）で拾う。LIKE 行は score 0.0 で FTS 行の後ろに並び、
  LIKE 内は query ごとの順位（語の出現回数合計の降順 → chunk_id 昇順）で交互に並べ、特定 query への偏りを避ける。
  行に matched_via="like" を残す。"""
import argparse, json, sqlite3, re, datetime as dt
from pathlib import Path

def fts(q):
    return " AND ".join('"' + t.replace('"', '') + '"' for t in re.split(r"\s+", q.strip()) if t)

def like_terms(q):
    return [t for t in re.split(r"\s+", q.strip()) if t]

def esc_like(t):
    return t.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

def like_rows(con, docs, q, limit):
    """LIKE（各語 AND）で一致する chunk を、語の出現回数合計の降順 → chunk_id 昇順で limit 件。"""
    terms = like_terms(q)
    if not terms:
        return []
    ph = ",".join("?" * len(docs))
    hay = "(c.title || ' ' || c.heading || ' ' || c.text)"
    cond = " AND ".join(f"{hay} LIKE ? ESCAPE '\\'" for _ in terms)
    hits = " + ".join(f"(length({hay}) - length(replace({hay}, ?, ''))) / length(?)" for _ in terms)
    sql = f"""SELECT c.chunk_id, c.doc_id, c.title, c.heading, c.source_ref, c.text, ({hits}) AS hits
              FROM chunks c WHERE c.doc_id IN ({ph}) AND {cond} ORDER BY hits DESC, c.chunk_id LIMIT ?"""
    params = [x for t in terms for x in (t, t)] + list(docs) + ["%" + esc_like(t) + "%" for t in terms] + [limit]
    return con.execute(sql, params).fetchall()

def query_recall(con, docs, queries):
    """query ごとの FTS 件数と LIKE 件数（doc 許可リスト内、LIMIT なし）。LIKE は空白区切り各語の AND。"""
    ph = ",".join("?" * len(docs)); out = []
    for q in queries:
        fts_count = con.execute(f"SELECT COUNT(*) FROM chunks_fts WHERE chunks_fts MATCH ? AND doc_id IN ({ph})",
                                (fts(q), *docs)).fetchone()[0]
        terms = like_terms(q)
        cond = " AND ".join("(c.title || ' ' || c.heading || ' ' || c.text) LIKE ? ESCAPE '\\'" for _ in terms)
        like_count = con.execute(f"SELECT COUNT(*) FROM chunks c WHERE c.doc_id IN ({ph}) AND {cond}",
                                 (*docs, *("%" + esc_like(t) + "%" for t in terms))).fetchone()[0] if terms else 0
        out.append({"query": q, "fts_count": fts_count, "like_count": like_count})
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("domain")
    ap.add_argument("--kb-dir", required=True); ap.add_argument("--docs", required=True)
    ap.add_argument("--query", action="append", required=True)
    ap.add_argument("--limit-per-query", type=int, default=40); ap.add_argument("--max-chunks", type=int, default=160)
    ap.add_argument("--output-dir"); ap.add_argument("--like-fallback", action="store_true"); a = ap.parse_args()
    kb = Path(a.kb_dir).resolve()
    docs = [l.strip() for l in Path(a.docs).read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    con = sqlite3.connect((kb / "index" / "library.sqlite").as_uri() + "?mode=ro", uri=True); ph = ",".join("?" * len(docs)); best = {}
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
    like_queries = []
    if a.like_fallback:
        fts_hit = {q for r in best.values() for q in r["matched_queries"]}
        like_queries = [q for q in a.query if q not in fts_hit]
        for q in like_queries:
            for rank, (cid, did, title, heading, ref, text, hits) in enumerate(like_rows(con, docs, q, a.limit_per_query)):
                e = best.get(cid)
                if e is None:
                    best[cid] = {"chunk_id": cid, "doc_id": did, "title": title, "heading": heading, "source_ref": ref,
                                 "score": 0.0, "matched_queries": [q], "matched_via": "like", "like_rank": rank, "text": text}
                else:
                    e["matched_queries"].append(q)
                    if "like_rank" in e: e["like_rank"] = min(e["like_rank"], rank)
    rows = sorted(best.values(), key=lambda r: (r["score"], r.get("like_rank", 0), r["chunk_id"]))[: a.max_chunks]
    for r in rows: r.pop("like_rank", None)
    out = Path(a.output_dir).resolve() if a.output_dir else kb / "cards" / a.domain
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "source-pack.jsonl", "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    manifest = {"domain": a.domain, "queries": a.query, "doc_filter": docs, "chunk_count": len(rows),
                "book_count": len({r["doc_id"] for r in rows}),
                "query_recall": query_recall(con, docs, a.query), "generated_at": dt.datetime.now().astimezone().isoformat(),
                "kb_dir": str(kb), "pack_path": str(out / "source-pack.jsonl"),
                "policy": "Local distillation material only. Cards derived from this pack must be reconstructions (decision criteria, procedures, pitfalls), not long quotations."}
    if a.like_fallback:
        manifest["like_fallback_queries"] = like_queries
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "manifest": manifest}, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
