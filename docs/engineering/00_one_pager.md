<!-- generated-by: scripts/generate_engineering_docs.py -->
# oreilly-epub-downloader — One Pager / オンボーディング概要

> 生成日: 2026-07-16 / 対象: `oreilly-epub-downloader` / 確度: [高]
> 実装・manifest・既存資料の静的棚卸しに基づく。外部サービスの稼働状態と本番構成は未検証。

## コンセプト

O'Reilly EPUB Downloader

## 誰の何を解くか

- 対象領域: 未分類 / 要確認
- 想定利用者: 実装・既存資料から未特定
- 価値仮説: 実装証拠を増やして具体化する必要がある。

## 現在地

| 項目 | 観測結果 |
|---|---|
| 技術スタック | Python |
| API | 0 endpoint signal |
| データモデル | 1 unique entity signal |
| 画面 | 0 route/screen signal |
| 実行基盤 | 構成ファイル未検出 |
| package / module | 2 component signal |
| tests | 0 file signal |

## ソースマップ

| Component | Path | 責務 |
|---|---|---|
| `src` | `src` | 中核実装。詳細は配下moduleを参照 |
| `cli` | `src/cli.py` | 実行entrypoint |

## 最初に使うコマンド

| 目的 | Command |
|---|---|
| `cli:oreilly-dl` | `oreilly-dl` |

## 変更箇所の入口

| 変更対象 | 最初に読むpath | 同時に確認するもの |
|---|---|---|
| データモデル | `src/epub.py` | migration、制約、seed、API型 |

## 引継ぎ時の未解決ギャップ

| Priority | Requirement | 状態・理由 | Evidence |
|---|---|---|---|
| - | 自動監査でP0/P1/P2の未解決ギャップなし | - | - |

## スコープ境界

- [高] productionの稼働、外部provider設定、secret値は未確認。
- [高] API・DB・画面が未検出の場合は推測せず、実装入口の追加を課題として残す。
- [中] 初回変更前に `07_traceability.md` の根拠と未確認事項を確認する。
