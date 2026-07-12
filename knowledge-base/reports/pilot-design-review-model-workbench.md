# パイロット設計レビュー: model_workbench `/compare` 複数モデル一括実行と結果永続化

> 実施日: 2026-07-02
> 目的: 書籍ナレッジ3層システムの実タスク検証（skills/engineering/book-knowledge-pack の手順に準拠）
> 使用 Context Pack: query「並列実行 部分障害 リトライ 冪等 結果永続化 キャッシュ」/ domain=architecture / project_brief=portfolio_briefs/top30/03_model_workbench.md
> レビュー対象: `src/components/CompareRunner.tsx`(並列実行), `src/lib/runner.ts`(実行・永続化), `src/app/api/runs/route.ts`

## General Practices（カード由来の一般論）

- **arch-p-012 部分障害を前提とした分散システム設計と冪等リトライ**: 外部API呼び出しは「時々失敗する」「成功したか不明」を前提に、クライアント側リトライ + サーバー側冪等をセットで設計する。
- **arch-a-011 暗黙の分散トランザクションの見落とし**: DB更新と別ストレージ書き込み（ファイル等）が並ぶ処理は、中間障害での不整合パターンを列挙し整合性戦略を割り当てる。
- **arch-p-013 長時間タスクは同期APIでなく分散オーケストレーションで扱う**: 処理時間がタイムアウト枠を超え得るステップは非同期契約に載せ替える。
- **arch-t-014 メッセージキュー導入の便益と複雑性**: バッファリング・スケールの便益と、多重配送・順序入替のコストを比較して採否を決める。
- **arch-a-010 キャッシュ前提の容量設計**: キャッシュを SLO の暗黙依存にしない。依存にするなら明示する。（修正注記 2026-07-12: 当初は外部キー制約カードのIDと取り違えて誤記していたため訂正）

## Apply to Current Project（model_workbench への適用判断）

| 判定 | 内容 |
|------|------|
| ✅ 既に適合 | `cacheKey`(unique) による run の create/update 上書き（runner.ts:147-149）は再実行を安全にする冪等設計で、arch-p-012 の推奨と一致。手動/キャッシュ/ローカルの4実行モード分離も再現性の設計として良い |
| ✅ 既に適合 | キャッシュ再生は暗黙依存ではなく明示モード（executionMode="cache"）であり、arch-a-010 には該当しない |
| ⚠️ 指摘1（中） | **run行→artifact保存→run更新→機械評価の逐次書き込み**（runner.ts:147-158）は arch-a-011 の縮小版。artifact 保存や eval で落ちると「output はあるが artifactPath/評価が無い run」が残り、レポート生成(/reports)が欠損データを掴む。対策: 欠損を許容する読み手にする（表示側で artifactPath/eval の null を明示）か、失敗時に run.error へ追記する |
| ⚠️ 指摘2（中） | **同一 cacheKey の同時実行レース**: 並列 Promise.all（CompareRunner.tsx:132）でユーザーが同条件を二重送信すると、両方 create に進み unique 制約違反が生エラーとして返る。対策: P2002 捕捉時に update へフォールバック（冪等リトライの完成） |
| ⚠️ 指摘3（低） | **クライアント側 Promise.all に並列上限なし**: モデル数が増えると provider rate limit を同時に叩く。ローカル営業デモ（数モデル）では現状で十分。10+モデル比較を売りにする時点で p-limit 等の同時実行制御を入れる |
| ❌ 今は適用しない | arch-p-013（ジョブキュー化）と arch-t-014（キュー導入）: maxDuration 300s の同期APIは、ローカル単独ユーザーの営業デモという製品性格では複雑性が便益を上回る。SaaS 化・複数ユーザー同時利用の段階で再判断（brief の「共通基盤化」拡張時が再判断ポイント） |

## Caveats

- カードは書籍由来の一般論。指摘1・2は dev.db（SQLite + Prisma）のローカル前提では実害頻度が低く、修正優先度はプロダクト化判断に従属する。
- 本レビューはコード全体の監査ではなく、Context Pack の適用検証を目的とした範囲限定レビュー（runner/CompareRunner/route のみ）。
