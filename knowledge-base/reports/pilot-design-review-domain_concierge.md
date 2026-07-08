# パイロット設計レビュー: domain_concierge 診断営業ワークスペース（Server Actions / knowledge.yaml 永続化）

> 実施日: 2026-07-08
> 目的: api-design ドメインカードの初実戦投入検証（skills/engineering/book-knowledge-pack の手順に準拠）
> 使用 Context Pack: query「API 設計 コンシューマ視点 契約」/ domain=api-design / project_brief=portfolio_briefs/top30/14_domain_concierge.md
> レビュー対象: `app/app/[industry]/actions.ts`（提案書生成・商談記録保存の Server Action）, `app/app/[industry]/edit/actions.ts`（knowledge.yaml 保存 Server Action）, `app/lib/repoFiles.ts`（ファイルI/O層）, `app/lib/domain/loader.ts`（knowledge.yaml 検証・永続化層）, `app/lib/industries.ts`（業界レジストリ／入力ホワイトリスト）

## General Practices（カード由来の一般論）

- **api-p-001 コンシューマ視点でAPIを設計し、実装を隠す抽象化を保つ**: 利用者が達成したいワークフロー単位でリソースと操作を設計する。ただし生産者・消費者が同一チームで密結合し常に同時更新される内部APIでは、契約の独立性という便益は小さい（when_not_to_apply）。
- **api-p-002 OpenAPI仕様をAPI契約として共有・公開する**: REST APIはOpenAPIで構造・認証要件・利用例を記述し利用チームへ共有する。
- **api-p-008 認証（誰か）と認可（何ができるか）を分離して設計する**: 認証を先に確立し、認証後に呼び出し元がアクセスできる範囲を認可として明示する。完全に閉じた単一利用者の内部ツールは適用除外の候補だが、公開境界に出た時点で必須になる。
- **api-p-011 防御的プログラミングで入力を多層検証する**: 「入力は無効か悪意がある可能性がある」を前提に、サニタイズ・バリデーション・認証・認可の複数レイヤーで構成する。
- **db-p-012 正規化は冗長性排除と将来のクエリ変化への保険として使う**: OLTPスキーマは3NFを既定とするが、ドキュメントDBで集約単位の読み書きが支配的な場合は同じ基準を機械適用しない（when_not_to_apply）。
- **db-a-003 下流に伝わらないスキーマ変更（JSON柔軟性の罠）**: スキーマ変更を下流の取り込み利用者へ通知するプロセスを設ける。下流消費者が存在しない閉じたDBでは通知プロセスは不要（when_not_to_apply の逆から見ると、下流消費者が存在する構成では必須）。
- **arch-t-004 API方式はデータの複雑さと呼び出し側コストで選ぶ**: データ構造が単純でリレーションの横断取得が不要ならREST（HTTP+JSON）を既定にする。「流行っていないから」ではなく要件充足で判断する。

## Apply to Current Project（domain_concierge への適用判断）

| 判定 | 内容 |
|------|------|
| ✅ 既に適合 | Server Actions のみでAPI層を構成し、REST/GraphQL/gRPCいずれも導入していない（`app/app/[industry]/actions.ts`, `app/app/[industry]/edit/actions.ts`）。フロント・バックエンドは同一Next.jsアプリ・同一チーム・同一デプロイ単位で密結合しており、arch-t-004の「単純さを既定にする」判断軸、api-p-001のwhen_not_to_apply（同一チーム密結合の内部APIでは契約独立性の便益が小さい）のいずれとも整合する。OpenAPI契約化（api-p-002）も同じ理由で不要と判断できる |
| ✅ 既に適合 | `industryId` はユーザー入力文字列をそのままファイルパスへ渡さず、`getIndustry(industryId)`（`app/lib/industries.ts:399-401`）でホワイトリスト配列 `INDUSTRIES` と照合し、未一致なら `{ ok: false }` で即座に弾いている（`app/app/[industry]/actions.ts:37-38`, `app/app/[industry]/edit/actions.ts:11-13`）。api-p-011の「信頼境界の入口で検証する」を満たしており、`repoFiles.ts`/`loader.ts` 側のパス組み立て（`path.join(repoRoot, "industries", dir, ...)`）に未検証の外部入力が到達しない設計になっている |
| ✅ 既に適合 | `saveCaselogFile`（`app/lib/repoFiles.ts:13-21`）は会社名由来のslugを `replace(/[^\p{L}\p{N}_-]+/gu, "-")` で許可文字だけに絞り、40文字に切り詰めてからファイル名に使用（`app/lib/repoFiles.ts:17`）。api-p-011の多層サニタイズが入力→ファイルシステム境界で実践されている |
| ✅ 既に適合 | `saveKnowledgeChecked`（`app/lib/domain/loader.ts:47-76`）は「YAML parse→zodスキーマ検証→dir一致検証→バックアップ→書き込み」の順を厳守し、検証失敗時は一切ファイルに触れず throw する。api-p-011の「バリデーション→リソース操作の段階分離」と一致する実装 |
| ⚠️ 指摘1（中） | **knowledge.yaml 更新後、下流生成物（L1_diagnosis-sheet.md の `<!-- GENERATED -->` マーカー節）が自動同期されない**。`saveKnowledgeChecked`（`app/lib/domain/loader.ts:47-76`）は knowledge.yaml への書き込みのみを行い、`app/package.json:11`（`"sync-l1": "tsx scripts/sync-l1.ts"`）で定義された再生成コマンドを呼ばない。編集UI側（`app/app/[industry]/edit/EditClient.tsx:14,30-36` → `app/app/[industry]/edit/actions.ts:19-23`）の保存成功メッセージも「旧版はバックアップへ退避」とだけ伝え、L1側が未反映である旨を警告しない。README（リポジトリルート `README.md:76`）には「L1側は `npm run sync-l1` で再生成する」と明記されているが、これはコードで強制されない運用ルール依存。db-a-003（下流に伝わらないスキーマ変更）の趣旨どおり、knowledge.yaml編集直後に商談ワークスペースが古いL1仮説・質問を表示し続けるリスクが生じる。対策: 保存成功時にsync-l1相当の処理を同一フローで呼ぶか、保存メッセージに「L1未反映。npm run sync-l1 を実行してください」の警告を追加する |
| ❌ 今は適用しない | api-p-008（認証・認可の分離）: `saveKnowledge`（`app/app/[industry]/edit/actions.ts:7-27`）、`saveCaselog`（`app/app/[industry]/actions.ts:32-80`）、`polishProposal`（`app/app/[industry]/actions.ts:9-29`、`ANTHROPIC_API_KEY` 課金呼び出しを伴う）はいずれも認証・認可なしで呼べる Server Action。README（リポジトリルート `README.md:94-95`）が明記する通り現状は `npm run dev` によるローカル単独ユーザー利用が前提であり、api-p-008のwhen_not_to_apply（完全に閉じた単一利用者の内部ツール）に該当する。再判断ポイント: Vercel等へデプロイして営業チーム複数人で共有する構成に変わった時点で、knowledge.yaml書き換え（`saveKnowledge`）と課金API呼び出し（`polishProposal`）の両方に認証・認可層を追加する |
| ❌ 今は適用しない | db-p-012（3NF正規化）: knowledge.yaml は `app/lib/domain/types.ts` の zod スキーマが定義するネスト構造（Workflow → PainPoint → AIUseCase の1:N入れ子）を持つドキュメント指向データであり、リレーショナルOLTPスキーマではない。db-p-012自身のwhen_not_to_apply「ドキュメントDBで集約単位の読み書きが支配的な場合」に該当し、3NF分解を機械適用する対象ではない |

## Caveats

- カードは書籍由来の一般論。指摘1は「ローカル単独ユーザー・手編集も許容する資産」という製品性格ではREADMEの運用ルール順守で回避可能な低頻度リスクであり、修正優先度はプロダクト化判断（❌2件の再判断ポイントが発生するタイミング）に従属する。
- 本レビューはコード全体の監査ではなく、api-design/database/architecture/security の4ドメインカードと Context Pack の適用検証を目的とした範囲限定レビュー（`actions.ts` / `edit/actions.ts` / `repoFiles.ts` / `loader.ts` / `industries.ts` の5ファイルのみ。`onePager.ts` / `pocGenerator.ts` / `questionGenerator.ts` / `proposal.ts` / `roi.ts` 等のドメインロジック本体は対象外）。
- security ドメインのカード（sec-p-001等）も確認したが、`ANTHROPIC_API_KEY` は `app/.env.local`（gitignore済み・リポジトリ内に実ファイルなし）で管理されており、平文シークレット混入の指摘事項はなし。

## 参照カード一覧

- api-p-001（コンシューマ視点でAPIを設計し、実装を隠す抽象化を保つ）
- api-p-002（OpenAPI仕様をAPI契約として共有・公開する）
- api-p-008（認証と認可を分離して設計する）
- api-p-011（防御的プログラミングで入力を多層検証する）
- db-p-012（正規化は冗長性排除と将来のクエリ変化への保険として使う）
- db-a-003（下流に伝わらないスキーマ変更／JSON柔軟性の罠）
- arch-t-004（API方式はデータの複雑さと呼び出し側コストで選ぶ）
