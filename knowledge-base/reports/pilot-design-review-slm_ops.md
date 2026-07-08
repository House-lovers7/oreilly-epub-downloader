# パイロット設計レビュー: slm_ops 本番運用ループ (`/api/execute` → ルーティング → SLM実行 → machineCheckゲート → fallback)

> 実施日: 2026-07-08
> 目的: 書籍ナレッジ3層システムの実タスク検証（skills/engineering/book-knowledge-pack の手順に準拠）
> 使用ドメイン: architecture / sre / performance / api-design（各 `get_domain_checklist` + `search_practice_cards` で取得）
> レビュー対象: `src/app/api/execute/route.ts`（APIルート）, `src/lib/ops.ts`（本番運用ループ本体）, `src/lib/routing.ts`（モデル選択の純関数）, `src/lib/db/schema.ts`（スキーマ）, `src/lib/gateway/index.ts` + `ollama.ts` + `google.ts`（外部呼び出しアダプタ）

## General Practices（カード由来の一般論）

- **arch-p-012 部分障害を前提とした分散システム設計と冪等リトライ**: ネットワークと複数ノードが絡む処理は「時々失敗する」「成功したか不明」を前提に置く。クライアント側リトライとサーバー側の冪等設計はセットで初めて成立する。
- **arch-t-010 LLMリフレクションの深さはコストと品質で調整する**: ラウンド数を上げる前に品質改善の見込みと追加コスト・レイテンシ（特にテール遅延）を用途ごとに見積もる。全用途に一律のリフレクション/リトライ段数を適用しない。
- **sre-p-003 アラートは「何が悪いか」だけを伝える（SLOベースアラート）**: アラートの責務を「ユーザー影響のある劣化が起きている」通知に限定し、内部メトリクスの静的閾値でアラームを量産しない。
- **perf-t-001 レイテンシ vs スループット（バッチ化・多層処理）**: ユースケースごとに「1件の応答時間」と「単位時間の処理量」のどちらが価値かを明示してから、バッチ化・集約の粒度を決める。
- **api-p-019 APIメトリクスのラベルはカーディナリティを見積もって設計する**: メトリクスラベルは endpoint / method / status のような有限で少数の値を取る次元に限定し、リクエスト単位の値をラベルにしない。

## Apply to Current Project（slm_ops への適用判断）

| 判定 | 内容 |
|------|------|
| ✅ 既に適合 | **fallback は1段限定のバウンドリトライ**（`src/lib/ops.ts:126,145-160`、コメント「primary 実行 → ゲート → 必要なら fallback へ1回だけリトライ」）。arch-t-010 が戒める「全ユースケースに一律の深いリフレクション」を避け、段数を明示的に1に固定している |
| ✅ 既に適合 | **バッチ処理と即時処理の分離**（`/api/execute` = 単発低レイテンシ処理 vs `dataset:run`/`compare:run` スクリプト = バッチ評価スイープ）。perf-t-001 が推奨する「ユースケースごとにレイテンシ/スループットどちらを取るか決めてから粒度を決める」を、API系とスクリプト系で明確に使い分けている |
| ⚠️ 指摘1（高） | **外部呼び出しにタイムアウトが無く、primary がハングすると fallback にも到達しない**。`src/lib/gateway/ollama.ts:16-28`（`fetch(...OLLAMA_BASE_URL.../api/generate)`）と `src/lib/gateway/google.ts:19-26`（`ai.models.generateContent(...)`）はいずれも `AbortController`/`signal` なしの素の呼び出し。`src/lib/ops.ts:135-140` の primary 実行と `147-160` の fallback 実行は**逐次**（primaryのtry/catchが終わるまでfallbackは走らない）。Ollamaのモデルロード詰まりやネットワーク切断でprimaryがハングすると、fallbackという安全網自体が発火しない。`src/app/api/execute/route.ts` にも `maxDuration` の指定が無く、Next.jsランタイム既定に委ねている。arch-p-012 が要求する「タイムアウトへの投資」が両アダプタとも未実装 |
| ⚠️ 指摘2（中） | **`/api/execute` の本番運用ループにリクエスト単位の冪等キーが無い**。`src/lib/db/schema.ts:69-93` の `runs` テーブルは `cacheKey` UNIQUE（80行目）でバッチ実行（`dataset:run`/`compare:run`）の再開・重複排除を保証しているが、`opsRequests` テーブル（`schema.ts:175-203`）には対応する一意キーが無い。`src/lib/ops.ts:180-200` は呼ばれるたびに新規 insert するだけで、`src/app/api/execute/route.ts:14-42` もクライアント冪等キー（`Idempotency-Key`相当）を受け取らない。クライアント側タイムアウト後の再送で同一入力の二重モデル実行・二重コスト（Gemini無料枠の消費含む）・重複ログ行が発生し得る。arch-p-012「クライアント側リトライ＋サーバー側冪等はセットで初めて成立する」の後半（サーバー側冪等）が本番ループでは未整備 |
| ⚠️ 指摘3（低） | **quota消費が実行成功より先行し、失敗時に無料枠だけ消費して結果が残らない**。`src/lib/ops.ts:32-40` の `defaultExec` は `consumeQuota`（34行目）を `adapter.execute`（42行目）呼び出しの前に完了させる。`adapter.execute` が例外を投げた場合、`ops.ts:138-140` で catch されて `error` に積まれるだけで、消費済みのGemini無料枠（1日20件/モデル）は戻らない。ローカル単独ユーザー用途では実害は小さいが、「本日分の無料枠なし」表示（`ops.ts:36-38`）の裏で無駄撃ちが起き得る |
| ❌ 今は適用しない | **sre-p-003（SLOベースアラート）**: 撤退基準チェックは `pnpm health:check`（`scripts/health-check.ts` 経由 `src/lib/health.ts`）によるオンデマンドpull型で、cron常駐のpush型アラートは存在しない。README記載の通りローカルファースト・単独ユーザー運用が前提であり、能動的アラートの費用対効果が薄い。運用ループが定期実行（cron）化される、または複数ユーザー/顧客提供フェーズに進む時点が再判断ポイント |
| ❌ 今は適用しない | **api-p-019（メトリクスのカーディナリティ）**: `grep -rl "metrics\|prometheus\|alert"` で当たるのは `compare.ts`/`health-service.ts`/`runner.ts`/`schema.ts` 内のドメイン語としての "metrics"（比較指標・評価指標）のみで、Prometheus等の外部公開メトリクス系そのものが存在しない。ラベルのカーディナリティ問題は観測基盤を導入して初めて発生するため、現時点では前提が無い。observability導入時が再判断ポイント |

## Caveats

- カードは書籍由来の一般論。指摘1〜3はいずれも「ローカルファースト・単独ユーザーの営業/PoCワークベンチ」という製品性格（README記載）の下では発生頻度・実害が限定的であり、修正優先度はプロダクト化（複数ユーザー化・cron常駐化・顧客への直接提供）判断に従属する。特に指摘1（タイムアウト欠如）はfallbackという安全網自体を無効化し得るため、confidentialデータのローカル強制ルーティング（`routing.ts:101-124`）と組み合わせた本番運用フェーズに進む前に優先的に検討する価値がある。
- 本レビューはコード全体の監査ではなく、Context Pack（architecture/sre/performance/api-design）の適用検証を目的とした範囲限定レビュー（route/ops/routing/schema/gateway の5ファイルのみ）。`diagnosis-service.ts`、`llm-judge.ts`、UI層（`src/app/*/page.tsx`）、`scripts/*.ts` は対象外。

## 参照カード一覧

- arch-p-012（部分障害を前提とした分散システム設計と冪等リトライ）
- arch-t-010（LLMリフレクションの深さはコストと品質で調整する）
- sre-p-003（アラートは「何が悪いか」だけを伝える（SLOベースアラート））
- perf-t-001（レイテンシ vs スループット（バッチ化・多層処理））
- api-p-019（APIメトリクスのラベルはカーディナリティを見積もって設計する）
