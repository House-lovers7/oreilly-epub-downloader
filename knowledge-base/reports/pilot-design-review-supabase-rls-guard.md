# パイロット設計レビュー: supabase-rls-guard（RLSミス静的検査CLI）の設計レビュー

> 実施日: 2026-07-08
> 目的: O'Reilly規範カード（security / database ドメイン）を使った実タスク設計レビュー（skills/engineering/book-knowledge-pack の手順に準拠）
> 使用カード取得: `get_domain_checklist`（security, database）+ `search_practice_cards`（sec-p-004, sec-p-014, sec-a-004, db-p-005, db-p-009）+ `get_library_context_pack`（query「RLS policy audit 最小権限」/ domain=security / project_brief=portfolio_briefs/top30/04_supabase-rls-guard.md）
> レビュー対象: `src/rules/policies.ts`（RLSポリシー検査ルール群）, `src/rules/rls-enablement.ts`（RLS有効化検査）, `src/rules/grants.ts`（GRANT/anon権限検査）, `src/rules/sensitive-columns.ts`（機密カラム検査）, `src/config/suppressions.ts` + `src/rules/util.ts`（抑制・アロー
リスト機構）

## General Practices（カード由来の一般論）

- **sec-p-004 認証と認可を分離し役割別に最小権限を設計する**: 認証（本人性）と認可（操作可否）を別関心事として明示的に分け、プリンシパル×アクション×リソースでポリシーを書く。レビューでは各エンドポイント/各リソースについて「認証チェックの次に認可チェックがあるか」を機械的に確認する。
- **sec-p-014 OWASP API Top 10 を3カテゴリでレビュー観点化する**: 認証認可カテゴリでは、トークンの失効・検証、認証フローの実装誤り、権限昇格経路の有無を確認する。
- **sec-a-004 コード・リポジトリへの平文シークレット混入**: diffだけでなく、コミット履歴・.env系ファイル・スクリプト内のハードコード資格情報を検出対象にする。プライベートリポジトリでも履歴・フォーク経由で漏洩しうる。
- **db-p-005 DBスキーマ変更はCIパイプラインで自動検証する**: スキーマ変更のコミットごとに、ビルド・マイグレーション適用・検証を自動実行するCIを構成し、「どの変更も機能・サービスレベル要件を壊さない」ことを保証する。
- **db-p-009 トランザクション境界でエラーハンドリングを単純化する**: 不可分であるべき一連の更新を1トランザクションにまとめ、全成功コミットか全ロールバックの二択に落とす。アプリのエラーハンドリングを「トランザクション失敗→リトライまたは失敗応答」に単純化する。

## Apply to Current Project（supabase-rls-guard への適用判断）

前提: supabase-rls-guard は "zero-DB" の静的解析CLIで、Supabaseのマイグレーション `.sql` を読み込みAST/正規表現でパースし、危険なRLS設定を検出するだけの読み取り専用ツール（実際のDBへの接続・書き込みは行わない）。そのため database ドメインの2カードは「ツール自身がDBを操作するか」ではなく「ツールが提供する検査価値」「将来の機能拡張時の再判断ポイント」として評価する。

| 判定 | 内容 |
|------|------|
| ✅ 既に適合 | **sec-p-004 / sec-p-014 の権限昇格チェックを自ら実装している**: `rls_references_user_metadata`（RLS009, `src/rules/policies.ts:117-143`）は、ユーザーが `updateUser()` で自由に書き換えられる `user_metadata` をポリシー述語が参照している場合を `critical` として検出する。これはsec-p-014の「権限昇格経路の有無を確認する」、sec-p-004の「認証済み＝全操作許可という暗黙の実装を避ける」を、ツール自身が対象アプリに対して機械的に強制する設計になっている。 |
| ✅ 既に適合 | **sec-a-004: リポジトリ内に平文シークレットが混入していない**: `src/config/defaults.ts:9-23` にある `password` / `secret` / `api_key` / `token` 等の文字列は、対象マイグレーションの「機密カラム名らしさ」を判定するためのキーワードリストであり、実際の資格情報値ではない。`src/rules/sensitive-columns.ts` もこのキーワードリストをRLS未設定テーブルの検出にのみ使っており、実クレデンシャルは扱わない。grep範囲（`src/`）でも実値らしきシークレットは検出されなかった。 |
| ✅ 既に適合 | **db-p-005: ツール自体がCIパイプライン組み込み型のスキーマ自動検証を製品として実現している**: `src/reporters/github.ts`・`src/reporters/sarif.ts`（GitHub Actions annotation / SARIF出力）と `docs/ci-integration.md` により、マイグレーションのコミットごとにCIでRLS検査を自動実行できる構成になっており、db-p-005が推奨する「スキーマ変更のコミットごとの自動検証」をまさに製品として提供している。 |
| ⚠️ 指摘1（中） | **アロー(publicTables)の名前一致がスキーマをまたいで過剰抑制されうる**（`src/rules/util.ts:11-18`）。`isAllowlisted` は `qualified`（`schema.name`）一致に加え、対象テーブルの `bare`（テーブル名のみ）一致でもtrueを返す。README・docs（`README.md:249`, `docs/rules.md:218`）の例は一貫して `"public.blog_posts"` のようなスキーマ修飾形式だが、ユーザーが慣習的に `"blog_posts"`（無修飾）を登録すると、`public.blog_posts` だけでなく `private.blog_posts` や `admin.blog_posts` 等、同名の別スキーマの全テーブルも黙って検査対象から外れる。sec-p-004の「最小権限はリソース単位で明示的に判定する」に反し、セキュリティ検査ツールにとって最も避けるべき「静かな偽陰性（false negative）」を生む設計。対策: `isAllowlisted` を既定でスキーマ修飾一致のみにする（無修飾一致は非推奨として警告付きで許容するか廃止する）、または無修飾エントリ使用時に `cfg.warnings` へ「この設定は全スキーマの同名テーブルに適用されます」という警告を出す。 |
| ❌ 今は適用しない | **db-p-009（トランザクション境界での all-or-nothing コミット）**: `src/cli.ts` にはマイグレーション適用や `--fix` の自動実行経路が存在せず（grep で "fix" 実行分岐なし）、findings の `fix` フィールドは修正SQLの提案文字列に過ぎない。ツールは実DBに対する書き込み・トランザクションを一切持たないため、db-p-009の「不可分な更新を1トランザクションにまとめる」は現状無関係。再判断ポイント: 将来 `--apply-fix` のようにDDL（`ALTER TABLE ... ENABLE ROW LEVEL SECURITY` 等）を対象DBに自動適用する機能を追加する場合、その適用シーケンスをdb-p-009に従い単一トランザクション化するかを再検討する。 |

## Caveats

- カードは書籍由来の一般論であり、対象プロジェクトの事情（zero-DB静的解析CLIという性格）に照らして再判断した。特にdatabaseドメインの2カードは「ツール自身がDBトランザクションを扱う場面がない」ため、db-p-005は「製品としての価値がカードの推奨形と一致する」、db-p-009は「現状不適用・将来の再判断ポイントとして記録」という異なる扱いにしている。
- 本レビューはコード全体の監査ではなく、コアなRLS検査ロジック・アローリスト機構に絞った範囲限定レビュー（`src/rules/policies.ts`, `src/rules/rls-enablement.ts`, `src/rules/grants.ts`, `src/rules/sensitive-columns.ts`, `src/config/suppressions.ts` / `src/rules/util.ts` のみ）。`src/parser/`（AST/regexパーサー本体）や `src/core/scan.ts`（実行オーケストレーション）は対象外。
- ⚠️指摘1は現状のドキュメント・README例が常にスキーマ修飾形式を推奨しているため実害の発生頻度は限定的だが、セキュリティ検査ツールにおける偽陰性は影響が大きいため中重大度とした。

## 参照カード一覧

- sec-p-004: 認証と認可を分離し役割別に最小権限を設計する
- sec-p-014: OWASP API Top 10 を3カテゴリでレビュー観点化する
- sec-a-004: コード・リポジトリへの平文シークレット混入
- db-p-005: DBスキーマ変更はCIパイプラインで自動検証する
- db-p-009: トランザクション境界でエラーハンドリングを単純化する
