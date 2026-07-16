<!-- generated-by: scripts/generate_engineering_docs.py -->
# oreilly-epub-downloader — 技術スタック比較

> 生成日: 2026-07-16 / 対象: `oreilly-epub-downloader` / 確度: [高]
> 実装・manifest・既存資料の静的棚卸しに基づく。外部サービスの稼働状態と本番構成は未検証。

## 観測された採用スタック

Python

## Package / workspace

| Package | Manifest |
|---|---|
| package manifest未検出 | - |

## トレードオフ

| 対象 | 現在 | 比較候補 | 現在案の利点 | 注意点 |
|---|---|---|---|---|
| 実装言語 | Python | Go / TypeScript | データ処理と自動化の資産を使いやすい | 配布・型境界の追加設計 |

> [中] 比較候補は現行実装を理解するための対照であり、移行提案ではない。当時の採用理由は既存ADRがあればそちらを正典とする。

## 判断を更新する条件

- manifest: `pyproject.toml`
- quality config: 未検出
- framework更新時はlockfile、build、typecheck、主要test、runtime smokeを同じ変更で確認する。
