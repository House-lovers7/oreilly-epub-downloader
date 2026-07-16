<!-- generated-by: scripts/generate_engineering_docs.py -->
# oreilly-epub-downloader — Engineering Handbook / Start Here

> 生成日: 2026-07-16 / 対象: `oreilly-epub-downloader` / 確度: [高]
> 実装・manifest・既存資料の静的棚卸しに基づく。外部サービスの稼働状態と本番構成は未検証。

## 60分で把握する

1. コンセプト: O'Reilly EPUB Downloader
2. classification: `project` / stack: Python
3. install: `python3 -m venv .venv && . .venv/bin/activate`, `python3 -m pip install -e .`
4. run/check: `oreilly-dl`
5. entrypoint: `src/cli.py`

## 実装スナップショット

| 項目 | 現在値 | 最初に読むpath |
|---|---:|---|
| package/component | 2 | `src` |
| API | 0 | 未検出 |
| entity | 1 | `src/epub.py` |
| screen/entry UI | 0 | 未検出 |
| test files | 0 | 未検出 |

## 最初に確認する既存の正典候補

- `README.md`

既存ADR、OpenAPI、schema、運用runbookがある場合は、下記generated docsより先に読む。

## 引継ぎblocking / partial

| Priority | Requirement | 状態・理由 | Evidence |
|---|---|---|---|
| - | 自動監査でP0/P1/P2の未解決ギャップなし | - | - |

## 読む順番

1. [One Pager](./00_one_pager.md)
2. [技術スタック比較](./01_stack_comparison.md)
3. [アーキテクチャ・システム構成](./02_architecture.md)
4. [ADR](./03_adrs/ADR-0001-current-implementation-baseline.md)
5. [API定義](./04_api.md)
6. [データモデル・ER図](./05_data_model.md)
7. [非機能要件・SLO/SLI](./05_nfr_slo.md)
8. [画面設計](./06_screen_design.md)
9. [P50/P90見積り](./06_estimation.md)
10. [実装トレーサビリティ](./07_traceability.md)
11. [学習・保守ロードマップ](./08_learning_roadmap.md)

## 使い方

- generated docsは実装発見用handbook。既存ADR、OpenAPI、schema、runbookがある場合は既存正典を優先する。
- path・数・versionは静的検出した事実。目的やpath由来の責務は `[中]` の推定を含む。
- production、external console、secret値、migration適用状態は未確認。
