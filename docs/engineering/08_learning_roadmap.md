<!-- generated-by: scripts/generate_engineering_docs.py -->
# oreilly-epub-downloader — 学習・保守ロードマップ

> 生成日: 2026-07-16 / 対象: `oreilly-epub-downloader` / 確度: [高]
> 実装・manifest・既存資料の静的棚卸しに基づく。外部サービスの稼働状態と本番構成は未検証。

## Day 1: 起動と全体像

1. install候補: `python3 -m venv .venv && . .venv/bin/activate`, `python3 -m pip install -e .`
2. 最初の実行/検査: `oreilly-dl`
3. `src` を読み、中核実装。詳細は配下moduleを参照の境界を確認
4. `src/cli.py` を読み、実行entrypointの境界を確認

## Day 2–3: 主要契約

- APIがない/未検出であることを確認
- `src/epub.py` の 1 entityとmigration順序を確認
- CLI/API/docs入口の成功・失敗フィードバックを確認
- external/config: 外部integration未検出 / 設定名未検出

## 最初の変更前

- 変更対象に最も近いtest: test未検出。先にcharacterization testを検討
- 既存ADR/docs: `README.md`
- runtime: runtime構成未検出
- `07_traceability.md` の未確認事項をcloseまたはrisk acceptしてから変更する。

## Doneの定義

- build/type/lint/testのうち存在するgateが通る。
- API/data/UI/runtimeの変更に対応する文書とADRを更新する。
- rollback、秘密情報、外部送信、production影響をreviewで明示する。
