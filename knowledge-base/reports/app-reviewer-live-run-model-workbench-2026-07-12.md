# app-reviewer 実走検証: model_workbench（工程結線の実運用確認 R2）

> 実施日: 2026-07-12
> 目的: `~/.claude/agents/app-reviewer.md` 手順2（project_map 照合 → get_domain_checklist → card_id 引用）が日常レビューで実際に働くことの実証（ARCHITECTURE.md R2）
> 対象: model_workbench の未コミット diff 5ファイル（run-safety-sweep.ts / gateway/google.ts / gateway/types.ts / llm-judge.ts / safety-judge.ts）
> 実行: app-reviewer サブエージェント（sonnet, 読み取り専用）。初回はテスト実行に潜り込みツール上限付近で停止 → 完走督促1回で報告出力（既知の教訓 subagent-tooluse-cap-defeats-large-batches と同型）

## 結果: PASS

- **card_id 引用**: あり — sec-p-008（W1 入力検証）、db-p-009（S4 トランザクション境界）、arch-p-012（リトライ設計の妥当性確認に引用）
- **実指摘**: Warning 1件（`run-safety-sweep.ts:71` `--max-judge` に `Number()` 直変換のみで NaN 時に課金上限ガードが無条件無効化 = fail-open。`node -e` で動作確認済み・確度高）、Suggestion 4件（Gemini responseJsonSchema 実API未検証、thinkingConfig の非3系レベル収束、unsafe cast の将来耐性、Run再利用のトランザクション境界）
- **文脈判断**: Stripe観点は「diff に決済コードなし → 対象外」、Supabase/RLS観点は「Prisma+SQLite 使用を datasource で確認 → 対象外」と正しく棄却。カードの機械適用ではなく実態照合が働いた
- **機械検証**: レビュー中に tsc / eslint / テスト57件パスをエージェント自身が実行・確認

## 学び

- 結線（push型チェックリスト + card_id 引用義務）は日常レビュー工程で実際に機能する。使用実績は `scripts/card_usage_report.py` に反映される
- app-reviewer はツール実行上限（約25-30）があるため、テスト・型チェックまで自走させると報告前に停止しうる。レビュー依頼時は「検証は最小限、報告優先」を指示に含めるのが安全

## 指摘の修正適用状況

- W1（max-judge fail-open）: **修正適用済み（2026-07-12 同日）**。`argNonNegativeInt` ヘルパー導入で `--max-judge` / `--delay` を起動時検証（fail-closed）。tsc / 57テスト / 不正値拒否（課金API未到達）を検証済み。未コミット
- S1〜S4（Suggestion）: 未適用（S1 は Gemini 実API検証に課金を伴うため要承認）
