<!-- generated-by: scripts/generate_engineering_docs.py -->
# oreilly-epub-downloader — 見積り（オンボーディング・契約確認）

> 生成日: 2026-07-16 / 対象: `oreilly-epub-downloader` / 確度: [高]
> 実装・manifest・既存資料の静的棚卸しに基づく。外部サービスの稼働状態と本番構成は未検証。

## 前提

- 後発エンジニアが安全に最初の変更へ入るまでの確認作業を見積もる。
- 新機能実装、production変更、provider契約、データ移行そのものは含めない。
- P50/P90は静的に検出したAPI/entity/screen/test規模から算出した粗い時間幅。

| 作業 | P50 | P90 | 最初の根拠 | 完了条件 |
|---|---:|---:|---|---|
| ローカル再現 | 2h | 4h | `pyproject.toml` | 主要entrypointを起動またはbuild |
| データ契約確認（1 entity） | 2h | 4h | `src/epub.py` | field/relation/constraint/migrationを確認 |
| 回帰検査の入口整備 | 4h | 12h | `src/cli.py` | 最低1本の主要フロー検査を追加 |
| **合計** | **8h** | **20h** | - | 未確認事項をcloseまたはrisk accept |

> [低] 見積りは担当者の習熟度、依存サービス、fixture、実機、秘密情報の入手状況で変わる。最初の2時間でsetupを試し、失敗理由を反映して再見積りする。
