# パイロット設計レビュー: compatible_agent_workflow ワークフロー実行核 / DB スキーマ / テスト構成

> 実施日: 2026-07-08
> 目的: testing ドメインカードの初実戦検証（architecture / sre ドメインとの併用）
> 使用カード取得: `get_domain_checklist`(architecture / testing / sre) + `search_practice_cards`（推奨カード test-p-001, test-p-010, test-t-004, arch-p-013, sre-p-009 を本文取得）
> レビュー対象: `src/core/orchestrator/run.ts`（ワークフロー実行核・中断/再開）, `src/core/db/schema.ts`（drizzle スキーマ）, `src/core/db/client.ts`（DB接続層）, `src/core/db/repo/tasks.ts`（永続化・原子的クレーム）, `vitest.config.ts` + `test/setup.ts` + `test/*.test.ts`（テスト構成・6ファイル446行）, `src/core/model/providers/{mock,gateway}.ts`, `src/app/api/http.ts`, `src/app/api/stream/[runId]/route.ts`
> 範囲限定: 上記ファイルの読み取りのみ。対象プロジェクトへの書き込みは一切行っていない。

## General Practices（カード由来の一般論）

- **test-p-001 テストピラミッドに沿って層別の比率を設計する**: 土台に多数の高速な単体テスト、中間に少数の統合・サービステスト、頂点に最小限のE2Eという比率を基本形にする。上位層テストは保守費用が高く壊れやすい一方、下層だけでは相互作用の欠陥を捕捉できない。
- **test-p-010 統合ポイントは障害カテゴリ別にテスト方式を割り当てる**: 統合点ごとに障害モードを「構成」「権限」「ペイロード（契約）」に分類し、それぞれをテストでカバーするか明示的に判断する。構成・権限はインフラテストで、契約は契約テスト・単体テスト・静的解析で検証する。
- **test-t-004 テストダブル vs 実依存（どこまで本物を使うか）**: 単体テスト層はフェイク・スタブで速度と安定性を確保しつつ、軽量DB代替はSQL方言・トランザクション挙動の差異があるため、その差異が関心事のテストは本物で行う。フェイク実装も保守対象になる。
- **arch-p-013 長時間タスクは同期APIでなく分散オーケストレーションで扱う**: 処理時間がAPIのタイムアウト枠を超え得るステップは、同期呼び出しをやめてオーケストレーションパターン（状態機械/ワークフローエンジン）に載せ替え、「結果に依存して次に進む」ステップはコールバック/イベントで完了通知を受ける非同期契約にする。
- **sre-p-009 リクエストコンテキスト（トレースID・テナントID）を全ホップで伝搬する**: リクエストの発生源にできるだけ近い場所で一意な相関ID/トレースヘッダを付与し、以後の全サービス呼び出しに伝搬させる。マルチテナントではテナントコンテキストをサービス連鎖全体に渡し、ログ・メトリクスの共通キーにする。1つでも伝搬しないホップがあるとトレースが分断される。

## Apply to Current Project（compatible_agent_workflow への適用判断）

| 判定 | 内容 |
|------|------|
| ✅ 既に適合 | arch-p-013: `runs` テーブル（`src/core/db/schema.ts:143-164`）が durable な状態機械そのもので、`drive()` の PAUSE 分岐（`src/core/orchestrator/run.ts:315-350`）は「状態を永続化してコンピュートを解放し、コールバック（承認POST）で再開する」という非同期契約を正確に実装している。再開時の原子的クレーム（`claimSuspendedRun`, `src/core/db/repo/tasks.ts:149-160`）で二重処理も防いでいる。`run.ts:9-11` のコメントでも「本番では同じ形状が Vercel Workflow DevKit の createHook/await hook にマップする」と明記されており、カードの推奨をそのまま先取りした設計 |
| ✅ 既に適合 | test-t-004: モック/実依存の境界の切り方が適切。DB は `vitest.config.ts:15-18`（`PGLITE_DIR`）と `test/setup.ts:8-11` で全テスト共通の実 PGlite（Postgres方言互換）を使い続け、フェイク化しているのは非決定的な外部依存であるLLM呼び出しのみ（`AGENT_PROVIDER=mock` → `src/core/model/providers/mock.ts:47-66` の `MockProvider`）。カードが警告する「テストダブルの範囲が依存の依存まで広がる」ことを避け、DB層は本物のまま維持している |
| ⚠️ 指摘1（中） | test-p-010: 実際の統合点である AI Gateway（`src/core/model/providers/gateway.ts`）が、全テストから到達不能。`vitest.config.ts:15-18` で `AGENT_PROVIDER: "mock"` が固定されており、`test/*.test.ts` を全て確認したが `providers/gateway` を import するテストは存在しない（`grep` で0件）。構成（APIキー未設定）・権限（Gateway認証失敗）・ペイロード（AI SDK v6 のレスポンス形状変化）のいずれの障害カテゴリも自動テストでカバーされておらず、本番切り替え（`gateway.ts`）が動く保証はコードレビューの目視のみに依存している |
| ⚠️ 指摘2（中） | test-t-004: `src/core/db/client.ts:32-39` の `getClient()` は `DATABASE_URL` が設定されている場合に単に `throw` するだけで、本番Postgres（Neon等）ドライバは未配線（コメントで「MVPでは未配線」と明記）。一方 `src/core/db/schema.ts:8` は「PGliteでもNeon/Postgresでもゼロスキーマ変更で動く」と主張しているが、この等価性を検証するテストはリポジトリ内に存在しない。テストダブル（PGlite）が本物（本番Postgres）の代替として機能するという前提自体が未検証で、カードが警告する「軽量DB代替の方言・トランザクション挙動差異」のリスクが顕在化しても検出できない |
| ⚠️ 指摘3（中） | test-p-001: テストピラミッドが実質的に逆転している。`test/question-refinery.test.ts`（60行、純粋関数のみ）を除く5ファイル（`auth.test.ts` 87行, `hardening.test.ts` 84行, `ledger.test.ts` 35行, `loop.test.ts` 79行, `security.test.ts` 101行、計386/446行）は `startTask`/`resumeTask` 経由でパイプライン全体を実DB（PGlite）に対して走らせる形の統合テストとして書かれている。`src/core/governance/gate.ts`（`evaluateGate`）や `src/core/model/router.ts`（`selectModelForRole`）を直接importするテストは0件（`grep` で確認）で、これらのロジックはフルパイプライン実行を経由した間接カバレッジしか持たない。ロジックの分岐を単体で高速に確認する土台が薄く、`vitest.config.ts:12` の `fileParallelism: false` と合わせて、変更のたびにテスト全体（DB初期化込み）を待つ必要がある |
| ⚠️ 指摘4（低〜中） | sre-p-009: DB内の相関（`taskId`/`runId`/`tenantId` を全テーブルに持たせ、`traces` はハッシュチェーンで改ざん検知まで行う設計、`src/core/db/schema.ts:191-220`）は優れているが、これは単一プロセス内の相関に閉じている。外部サービス境界である AI Gateway 呼び出し（`src/core/model/providers/gateway.ts:22-35` の `generateText`/`embed`）にはヘッダ等でrunId/taskIdを伝搬する仕組みがなく、Gateway側の観測基盤とアプリ側の台帳を突き合わせる手段がない。唯一の `console.warn`（`src/core/rag/search.ts:60`）にも runId/taskId が含まれず、DBを見ずにログだけから障害箇所を特定できない。sre-p-009 の `when_not_to_apply`（単一プロセス・外部呼び出しがほぼない場合は価値が限定的）はこのプロジェクトには当てはまらない（AI Gatewayという実際の外部呼び出しが存在する） |
| ❌ 今は適用しない | arch-p-013 の「各マイクロサービスが自ドメイン内に自分のオーケストレータを持つ」入れ子オーケストレーションの部分: 現状は単一の Next.js モノリス内に単一の `drive()` オーケストレータしかなく、他サービスへの委譲は発生していない。再判断ポイント: テナントごとの実行を別サービス/ワーカーに分割する段階、または複数のワークフローエンジンを跨ぐ構成になった時点 |

## Caveats

- カードは O'Reilly書籍由来の一般論であり、書籍の文脈（大規模マイクロサービス、SaaS本番運用）とこのプロジェクトの文脈（MVP・単一テナントデモ中心・PGlite組み込みDB前提）には規模差がある。指摘1・2・4はいずれも「本番Postgres切り替え」「本番AI Gateway呼び出し」を見据えた段階での指摘であり、現状のローカルMVPデモとしての実害は限定的。
- 本レビューはコード全体監査ではなく、testing/architecture/sreドメインの推奨5カード（test-p-001, test-p-010, test-t-004, arch-p-013, sre-p-009）の適用検証を目的とした範囲限定レビュー（読んだファイルは冒頭に列挙した8ファイル程度）。`src/core/roles/*`（各AIロールの実装本体）や `src/core/governance/*` の内部ロジックまでは踏み込んでいない。
- testing ドメインカードの初実戦適用のため、カードの読み替え（「マイクロサービス統合点」→「AI Gateway/本番DB」）は本レビュー内での解釈であり、カード本文がこのプロジェクトのアーキテクチャを直接想定して書かれたものではない。

## 参照カード一覧

- test-p-001（テストピラミッドに沿って層別の比率を設計する）
- test-p-010（統合ポイントは障害カテゴリ別にテスト方式を割り当てる）
- test-t-004（テストダブル vs 実依存）
- arch-p-013（長時間タスクは同期APIでなく分散オーケストレーションで扱う）
- sre-p-009（リクエストコンテキストを全ホップで伝搬する）
