# 書籍ナレッジ3層システム アーキテクチャ設計図

> 目的: O'Reilly 218冊（2026-10-02 実測、74,277 チャンク）を「一流エンジニアの脳・知恵・経験を借りられる」判断材料へ変換し、AI開発工程へ自動供給する。
> 本書は **他モデル（Sonnet / Codex 等）が単独で実装を継続するための設計図**。運用原則の原本は ACOS `knowledge/engineering/technical-library-usage-principles.md`（本書は実装視点の補完であり、判断原則を再定義しない）。
> 最終更新: 2026-07-13（R3一巡目 design-patterns 蒸留まで反映）
> 2026-09〜10 のエンジニアリング基準線ブラッシュアップ（F0 無言劣化の封止、F1・F2 のカード精査と昇格、F3 のレビュー・実装工程への結線）の設計と実施記録は ACOS `docs/design/technical-library-engineering-baseline-brushup-2026-09.md`。本書の §3 工程結線・§4 不変条件より新しい内容はそちらが正。

## 1. 全体像（3層モデル）

```text
層2: 根拠層（全文）    218冊 / 74,277チャンク
  index/library.sqlite (FTS5 bm25, 336MB) + index/embeddings.npy (bge-m3 384次元, 123MB)
  検索 = Reciprocal Rank Fusion(K=60)。Ollama(127.0.0.1:11434)疎通不可時は keyword-only へ自動フォールバック
        │ 遅延蒸留（domain-pack で素材収集 → subagent 蒸留 → provenance 機械検証）
        ▼
層1: 規範層（カード）  9ドメイン 296カード
  cards/<domain>/{practices,antipatterns,tradeoffs}.jsonl + checklist.md + manifest.json
  カード必須フィールド: problem / recommendation / pitfalls / when_not_to_apply /
                        keywords / source_chunks / source_books / confidence / card_id
        │ project join（brief と突き合わせ）
        ▼
層3: 適用層（文脈）    cards/project_map.jsonl（32プロジェクト登録済み）
  {project, brief, domain_tags, relevant_domains, relevant_books, recommended_practices, note}
  + reports/（パイロットレビュー n=5、割当根拠ログ project-map-expansion-2026-07-12.jsonl）
```

- card_id 規約: `<prefix>-<p|a|t>-<3桁>`。prefix→domain: arch=architecture, api=api-design, db=database, dp=design-patterns, net=networking, perf=performance, sec=security, sre=sre, test=testing
- ドメインは現在9つ。追加時は `cards/<新domain>/` を作り、card_id prefix を `scripts/card_usage_report.py` の正規表現へ追加する（`validate_project_map.py` / gateway はディレクトリ自動認識）

## 2. コンポーネントと所在

| コンポーネント | 場所 | 役割 |
|---|---|---|
| エンジン | `app_development/_technical_library/technical_library.py` | build / search / embed / context-pack / domain-pack / cards / catalog。hybrid search は `search_rows()`（L652付近） |
| ラッパー | `scripts/technical_library.py`（本repo） | `--kb-dir knowledge-base` 前提の経路制御 |
| Tool Gateway | `app_development/_tool_gateway/tool_gateway.py` + `tools.yaml` | 下記5ツールを提供。KB既定パスは tools.yaml に定義 |
| 整合性検証 | `scripts/validate_project_map.py` | project_map の domain / card_id / brief見出し / 書名 / 重複を機械検証。**exit 0 + "OK" が完了条件** |
| 利用実績計測 | `scripts/card_usage_report.py` | レビュー成果物から card_id 引用を集計。使用/死蔵/ドメイン別カバレッジ/FTSフォールバック需要（`FTS-fallback:` 行）を出力 |

### Tool Gateway 5ツール（呼び出し契約）

```bash
python3 _tool_gateway/tool_gateway.py call <tool> --json '<args>'   # cwd: app_development/
```

| tool | 引数 | 挙動 |
|---|---|---|
| search_practice_cards | {domain, query, card_type?, limit?} | カード検索。**domain 省略時はドメイン一覧のみ返す**（カードは返らない点に注意） |
| get_domain_checklist | {domain} | checklist.md を返す（push型注入用） |
| search_technical_library | {query, limit?} | 全文 hybrid 検索（層2） |
| get_library_context_pack | {query, domain?, project_brief?} | 層1+層2統合の context pack。project_brief 指定で層3 join |
| list_technical_library_catalog | {} | 索引済み書籍一覧 |

## 3. 工程結線（どの工程で誰がKBを引くか）

| 工程 | 結線ファイル | 方式 |
|---|---|---|
| 設計・ADR | ACOS `skills/engineering/book-knowledge-pack/SKILL.md` | pull（tradeoff検索） |
| 実装ガード | ACOS `skills/engineering/{architect,data-db,test-qa,performance-cost,security,ops-release}-review/SKILL.md`（6件） | push（domain checklist） |
| PRレビュー | ACOS `agents/engineering/review-council/instructions.md` | push（project_map→relevant_domains→checklist、Finding に card_id 必須） |
| 日常レビュー | `~/.claude/agents/app-reviewer.md` 手順2 | push（project_map 登録プロジェクトのみ） |
| デバッグ・未知の問い | ACOS `skills/engineering/engineer-brain/SKILL.md` | pull（FTS直叩き、カード未整備ドメインのフォールバック） |
| ワークスペース導線 | `app_development/CLAUDE.md` 共通資産節 | 参照ルール明記（2026-07-12追加） |

## 4. 不変条件（実装時に壊してはならないもの）

1. **provenance**: カードの `source_chunks` は層2の実在チャンクIDを指す。蒸留・編集後は機械検証（chunk存在チェック）を通す。捏造ID・空provenanceのカードを追加しない
2. **著作権境界**: 書籍本文の長文引用を成果物へ貼らない。カードは再構成（判断基準・手順・落とし穴）のみ。KB内容を外部送信しない（ローカル個人利用）
3. **project_map の結合キー**: `project` は brief の `# PROJECT_BRIEF: <name>` 見出しと完全一致（不一致は join が静かに失敗するため validate で fail させている）
4. **カードは一般論**: 適用判断は必ず対象プロジェクトの実態と突き合わせる。レビュー指摘は file:line 裏取り + card_id 引用のセット
5. **原本境界**: 判断原則・Workflow・Skill の原本は ACOS。本repoは KB データとその検証・計測スクリプトの原本

## 5. 残実装ロードマップ（他モデル向け委譲契約）

実装順は R1 → R2 → R3。各タスクは独立して着手可能。**完走条件のコマンドが通るまで完了と報告しない。**

### R1: FTSフォールバック需要の計装（工数小）

- 目的: 「カードが無くて全文検索に落ちた質問」を記録し、次に蒸留すべきドメインを需要データで決められるようにする
- 範囲: ACOS `skills/engineering/engineer-brain/SKILL.md` と `skills/engineering/book-knowledge-pack/SKILL.md` に、カード0件で層2検索へフォールバックした際「作業ログまたは ACOS decision log に `FTS-fallback: <query>` の1行を残す」手順を追記する（スキル文書の変更のみ。コード変更なし）
- 触るなファイル: `scripts/card_usage_report.py`（集計側は `FTS-fallback:` 形式を既にパース可能。形式を変えない）
- 完走条件: 手動で試験行 `FTS-fallback: test query` を含む一時mdを `knowledge-base/reports/` に置き、`python3 scripts/card_usage_report.py` の「FTSフォールバック需要」節に表示されること（確認後に一時mdを削除）

### R2: 日常レビューでの実運用検証（工数小）

- 目的: 結線が「仕組み」でなく「実際に働く」ことの実証
- 範囲: project_map 登録済みプロジェクト（例: supabase-rls-guard, line-harness）で diff のあるものを選び、app-reviewer サブエージェントを1回実走。Finding に card_id 引用が含まれるか確認し、結果を `knowledge-base/reports/` に短く記録
- 完走条件: レビュー出力に実在 card_id が1件以上引用され、`card_usage_report.py` の使用実績に反映されること
- 注意: レビュー対象リポジトリのコードは変更しない（読み取り専用）

### R3: 需要駆動の次ドメイン蒸留（工数中・R1のデータが貯まってから）

> **1巡目完了（2026-07-13）**: design-patterns を蒸留（ユーザー明示要望 + kb-fallback.log 需要記録で選定、人間判断済み）。120チャンク→15カード（p9/a1/t5）、provenance 全数検証エラー0、gateway 疎通・validate_project_map 296 card_ids OK。歩留まりが低いのは「チャンクに無いことは書かない」規律で GoF 定義系（本文に pitfalls 記載なし）を見送ったため。2巡目以降の候補は下記のまま有効。

- 目的: 9ドメイン外（候補: frontend, llm-ops, data-engineering）の遅延蒸留
- 範囲: `card_usage_report.py` のフォールバック需要で頻出領域を1つ選び、既存手順（ACOS lesson `book-knowledge-lazy-distillation.md` の 素材pack→subagent蒸留→provenance全数検証）で `cards/<新domain>/` を作成
- 完走条件: 新domainのカードが manifest / checklist / provenance 検証込みで揃い、`search_practice_cards {domain:"<新domain>"}` が返すこと
- エスカレーション境界: どのドメインにするかの最終判断とカード品質基準の変更は上位モデルまたは人間へ

### R4: 既知の小修正（いつでも可）

- `reports/pilot-design-review-model-workbench.md` の card_id 誤記1件: 「キャッシュ前提の容量設計」を `arch-a-003` と記載しているが正は `arch-a-010`（arch-a-003 は外部キー制約の省略）。修正時は履歴が分かるよう修正注記を添える

## 6. 検証コマンド一覧（実装後の機械ゲート）

```bash
cd /Users/tg/projects/app_development/oreilly-epub-downloader
python3 scripts/validate_project_map.py                 # project_map 整合性（OK必須）
python3 scripts/card_usage_report.py                    # 利用実績・死蔵・フォールバック需要
python3 scripts/technical_library.py search "<query>" --kb-dir knowledge-base --limit 3 --mode hybrid   # 層2検索の疎通
cd /Users/tg/projects/app_development && python3 _tool_gateway/tool_gateway.py call search_practice_cards --json '{"domain":"architecture","query":"冪等 リトライ","limit":3}'   # 層1検索の疎通
```
