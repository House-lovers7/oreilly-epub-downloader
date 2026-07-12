# O'Reilly EPUB/PDF Knowledge Base Plan

このディレクトリには、O'Reillyの専門書をAIが使いやすい検索コンテキストへ変換するための設計メモを置きます。

## 実装状況（2026-07-12 更新）

本メモの構想は3層モデルとして実装済み。運用原則の原本は ACOS `knowledge/engineering/technical-library-usage-principles.md`、Agent 入口は `skills/engineering/book-knowledge-pack` と `_tool_gateway`。

| 構想 | 状態 |
|------|------|
| EPUB extractor / chunks / FTS5 index / search CLI | 実装済み（`_technical_library/technical_library.py`、131冊・62,947チャンク） |
| context pack | 実装済み + `--domain`（規範カード添付）/ `--project`（PROJECT_BRIEF join）拡張済み |
| practice / concept card | **practice / antipattern / tradeoff カードとして実装**（`cards/<domain>/*.jsonl`、9ドメイン296カード。2026-07-13 に design-patterns 15枚を需要駆動で追加）。蒸留は `domain-pack` で素材収集 → セッション内 subagent → provenance 機械検証の遅延蒸留方式 |
| project mapping | `cards/project_map.jsonl`（top30 一括登録済み。検証: `scripts/validate_project_map.py`） |
| Tool Gateway 化 | `search_practice_cards` / `get_domain_checklist` を追加登録済み（既存3ツールと合わせ計5ツール） |
| embedding / hybrid search | **実装済み**（2026-07-08 embeddings 構築: bge-m3 384次元 + FTS5 bm25 の RRF 融合。Ollama 疎通不可時は keyword-only にフォールバック） |
| 工程結線 | ACOS 側 11ファイル（6×domain review skill / review-council / engineer-brain / book-knowledge-pack ほか）+ `~/.claude/agents/app-reviewer.md` + `app_development/CLAUDE.md` 導線 |
| 実戦検証 | パイロット設計レビュー n=5（`knowledge-base/reports/pilot-design-review-*.md`、provenance エラー0） |
| カード利用実績の計測 | `scripts/card_usage_report.py`（使用/死蔵カード集計。FTSフォールバック需要は `FTS-fallback:` 行の記録を集計、記録側は未計装） |

## 現状確認

確認日時: 2026-06-07

```text
root: /Users/tg/projects/app_development/oreilly-epub-downloader
EPUB: 131 files
PDF: 0 files detected
```

現時点で検出された本はPDFではなくEPUBです。これはむしろ好都合です。
PDFよりEPUBの方が、章・節・見出し・本文を構造化して抽出しやすく、AI向けの知識ベース化に向いています。

## 目的

O'Reilly本を丸ごと毎回LLMへ渡すのではなく、次のような検索可能な資産へ変換します。

```text
EPUB/PDF
  ↓ extract
book-level metadata
chapter markdown
section chunks
concept cards
practice cards
project mapping
keyword / vector / hybrid index
  ↓
Agentが必要な時だけ関連chunkを取り出す
```

## なぜPDF丸投げではなくKnowledge Base化するのか

PDFやEPUBをそのまま読む方式は、以下が弱いです。

- 毎回コンテキストが大きすぎる
- 目次から手動で辿るのが遅い
- 複数書籍横断で探しにくい
- 実務に使えるpracticeだけ抽出しにくい
- 「今のプロジェクトに関係ある知見」へ変換しづらい

目指すべき形は、全文保管ではなく、用途別に圧縮された検索単位です。

## 推奨ディレクトリ構成

```text
oreilly-epub-downloader/
  downloads/                         # 元EPUB/PDF。原本。
  knowledge-base/
    catalog.json                      # book metadata一覧
    books/
      <book_slug>/
        metadata.json
        toc.json
        chapters/
          001-title.md
        chunks.jsonl
        concepts.jsonl
        practices.jsonl
        project_map.jsonl
    index/
      sqlite.db                       # FTS5 keyword search
      embeddings/                     # optional vector index
    reports/
      extraction-report.md
  scripts/
    build_knowledge_base.py
    search_knowledge_base.py
```

## 変換レイヤー

### 1. Book Metadata

書籍単位で取る情報:

```json
{
  "title": "Designing Data-Intensive Applications, 2nd Edition",
  "authors": [],
  "source_file": "downloads/...epub",
  "topics": ["database", "distributed systems", "architecture"],
  "language": "en",
  "chapters": 12
}
```

### 2. Chapter Markdown

章ごとにMarkdown化します。

```text
# Chapter 3: Storage and Retrieval

## Key Ideas
...

## Body
...
```

章単位は人間が読むための単位です。

### 3. Section Chunks

Agent検索用には、章より小さいchunkにします。

推奨chunk:

```text
800〜1,500 tokens相当
見出し境界を優先
前後contextをmetadataとして保持
```

chunkの形:

```json
{
  "book": "designing-data-intensive-applications-2e",
  "chapter": "Storage and Retrieval",
  "section": "SSTables and LSM-Trees",
  "chunk_id": "ddia2e-ch03-008",
  "text": "...",
  "keywords": ["LSM-tree", "SSTable", "compaction"],
  "use_cases": ["database design", "write-heavy systems"],
  "source": "downloads/Designing Data-Intensive Applications, 2nd Edition.epub"
}
```

### 4. Concept Cards

概念単位に圧縮します。

```json
{
  "concept": "LSM Tree",
  "definition": "...",
  "when_to_use": ["write-heavy workloads", "append-friendly storage"],
  "tradeoffs": ["read amplification", "compaction cost"],
  "source_chunks": ["ddia2e-ch03-008"]
}
```

### 5. Practice Cards

実務で使える形に変換します。

```json
{
  "practice": "Use SLOs before alert rules",
  "domain": "SRE",
  "problem": "Alerting on raw metrics creates noise",
  "procedure": ["Define user-visible objective", "Set SLI", "Choose alert threshold"],
  "pitfalls": ["too many alerts", "implementation metrics only"],
  "source_chunks": ["sre-workbook-ch02-004"]
}
```

この `practice card` が一番重要です。

Agentに本の文章そのものを使わせるより、今の仕事に使える判断材料・手順・チェックリストに変換した方が速いです。

### 6. Project Mapping

既存プロジェクトに紐づけます。

```json
{
  "project": "MiruAI",
  "domain_tags": ["mobile", "security", "subscription", "observability"],
  "relevant_books": ["SRE Workbook", "Software Supply Chain Security"],
  "recommended_practices": ["secret scanning", "release checklist", "SLO before alert"]
}
```

## 検索方式

最初は3段階がおすすめです。

### Phase 1: SQLite FTS5 keyword search

標準ライブラリだけで実装しやすいです。

できること:

- タイトル検索
- 本文検索
- book / chapter / topic filter
- 日本語は完全ではないが実用開始できる

### Phase 2: Hybrid Search

キーワード検索 + embedding検索。

例:

```text
query: "Next.js SaaSでマルチテナント設計をどうする？"
keyword: SaaS, multi-tenant, architecture
vector: 意味的に近いchunk
```

### Phase 3: RAG Tool Gateway化

`_tool_gateway` に以下を追加します。

```text
search_oreilly_knowledge
get_oreilly_context_pack
extract_oreilly_practices
map_project_to_oreilly_practices
```

Agentはこう使えます。

```bash
python3 _tool_gateway/tool_gateway.py call search_oreilly_knowledge --json '{"query":"SaaS マルチテナント 認証 DB分離","limit":8}'
```

## Agentに渡すContext Packの形

検索結果をそのまま長文で渡すのではなく、context packにします。

```text
# O'Reilly Context Pack

## Query
SaaSでテナント分離をどう設計する？

## Top Practices
1. Tenant isolation modelを先に選ぶ
2. Noisy neighbor対策を設計に入れる
3. Metricsをtenant_idで切れるようにする

## Evidence Chunks
- Building Multi-Tenant SaaS Architectures / Chapter X / Section Y
- Cloud FinOps / Chapter Z / Section A

## Apply to Current Project
- MiruAIなら、user_idだけでなくtenant_id境界を検討
- 初期MVPでは物理DB分離よりlogical isolationから始める

## Caveats
- 書籍由来の一般論。現プロジェクトの実装・規約・コスト条件で再判断する。
```

## 重要な注意

O'Reillyの書籍本文は著作権コンテンツです。

おすすめは:

- ローカル個人利用の検索indexとして扱う
- 外部送信しない
- 長い本文をそのまま成果物に貼らない
- 回答では短い引用・要約・実務への適用を中心にする
- 顧客納品物には書籍本文ではなく、自分の判断・設計・チェックリストとして再構成する

## 実装優先順位

1. EPUB extractor
2. metadata / toc / chapter markdown生成
3. chunks.jsonl生成
4. SQLite FTS5 index
5. search CLI
6. practice card抽出
7. Tool Gatewayに `search_oreilly_knowledge` を追加
8. project mapping
9. embedding / hybrid search

## 最初のMVP

最初はこれだけで十分です。

```bash
python3 scripts/build_knowledge_base.py --input downloads --output knowledge-base
python3 scripts/search_knowledge_base.py "SRE エラーバジェット アラート" --limit 5
```

出力:

```text
book / chapter / section / score / excerpt / source path
```

そこからAgentに渡すcontext packを作ります。
