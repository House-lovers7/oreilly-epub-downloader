<!-- generated-by: scripts/generate_engineering_docs.py -->
# oreilly-epub-downloader — 非機能要件・SLO/SLI

> 生成日: 2026-07-16 / 対象: `oreilly-epub-downloader` / 確度: [高]
> 実装・manifest・既存資料の静的棚卸しに基づく。外部サービスの稼働状態と本番構成は未検証。

## 現在コード化されている品質ゲート

| Gate | Command | 根拠 |
|---|---|---|
| cli:oreilly-dl | `oreilly-dl` | manifest script |

- test files: 0（未検出）
- quality/CI config: 未検出
- security/resilience signal: auth/session (`src/cookie_auth.py`), auth/session (`src/client.py`), resilience (`src/client.py`), auth/session (`src/cli.py`)

## 計測すべきSLI

| Boundary | SLI | 最初の計測根拠 |
|---|---|---|
| CLI/Job | exit code・処理件数・失敗件数・処理時間 | `src/cli.py` |
| Data | migration成功・constraint違反・鮮度/欠損 | `src/epub.py` |

## SLOの状態

[高] 合意済みSLO数値はrepository内の実装・資料から確認できていない。任意の99%や2秒を現在要件として記載しない。利用者、運用時間帯、障害コスト、予算を確認してから、上記SLIごとにtarget/window/error budgetを決める。

## 運用境界

- runtime/config: 構成ファイル未検出
- required config names: example/sourceから未検出
- 外部integration: 静的検出なし
- rollbackはcode、schema、generated artifact、provider設定を分ける。production操作は人間承認後に行う。
