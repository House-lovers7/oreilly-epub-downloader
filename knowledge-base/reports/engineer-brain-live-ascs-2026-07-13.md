# engineer-brain ライブ実行: ASCS 4層合成スタックの設計妥当性

> 実施日: 2026-07-13
> 目的: engineer-brain skill のフル手順実走（Step 1〜6）+ 新設「Design Patterns / Code Structure」レンズの初回実戦投入
> 対象: /Users/tg/projects/app_development/agent-session-control-stack（project_map 未登録 → unmapped 経路）
> 実行形態: レンズ3本を sonnet サブエージェント並列 fan-out、統合判断はメイン。各レンズは対象 repo の実ファイルを行番号まで読んで裏取り済み

鮮度判定: mixed — 原理（信頼境界・合成パターン・復旧設計）は KB。Claude Code hook 仕様は同日実装・テスト済みの一次情報を使用（追加 docs 取得不要）
使用レンズ: Security / Observability・SRE / Design Patterns・Code Structure（新設）

## 統合判断

**ASCS の4層合成は、パターン的にも運用的にも筋の良い設計。3レンズが独立に同じ核心を指した: 「誠実な申告（UNVERIFIED / fail-open / 運用規約）」で止まっている箇所を、read-only・fork 禁止の制約内で「機械的検証・記録」へ一段格上げする余地がある。**

3レンズの収斂点（独立に同一箇所を指摘）:

1. **申告 → 検証への格上げ**: Security は「service identity UNVERIFIED を恒久化せず、脅威モデルの ADR 明文化 or Unix ドメインソケット等へ」（sec-p-005 / sec-t-005）、SRE は「fail-open がサイレント — PreCompact 発火実績の記録・SLI がない」（risk-register R2 自認と一致）、Design Patterns は「単独決定者ルールが運用規約+事後診断のみで担保 — フォーク禁止とのトレードオフである旨の明記を」。三者とも「診断の誠実さは実装済み、次は検証可能性」という同じ方向。
2. **doctor の exit code 3値化 / --json**: SRE（CI ゲートには CONFLICT=1 / WARNING=0 が粗い）と Design Patterns（CI/hook 接続の素地はある）が接続。
3. **適用しない判断も明確に出た**（カードの機械適用でない証拠）: sre-p-008 の不変アーティファクト化は「state=仮説・source=真実」という設計意図に**反する**ため適用外 / mTLS 一律強化は単一ユーザー開発機前提なら sec-t-005 の許容トレードオフ / classify・report の完全分離は300行 read-only スクリプトには過剰レイヤ化リスク。

**レンズ間 tradeoff**: Security「検証を強めよ（ゼロトラスト）」vs Design Patterns「フォーク禁止制約下では運用規約+事後診断が合理的な許容解」。統合: **脅威モデルを ADR で明文化するのが最安の一手**（両レンズの要求を同時に満たし、単一ユーザーマシン前提なら現状維持を正当化、共有環境を許容するなら技術強化の判断基準になる）。

推奨アクション優先順:
1. 脅威モデル ADR（単一ユーザー開発機前提か、共有ホスト/CI も許容か）— sec-t-005 の「判断基準の明文化」
2. doctor exit code 3値化（WARNING=2）または --json 出力 — CI ゲート化の素地
3. PreCompact 発火実績（成功/失敗）の軽量ログ + doctor での表示 — サイレント fail-open の可視化
4. Unix ドメインソケット等の身元検証強化 — 共有環境要求が実際に出た時点で（今は過剰投資）

## レンズ別要点

### Security（確度: 中）
- 適合: UNVERIFIED の一貫申告・sanitize_base_url の境界検証・fail-closed パースは sec-p-008 に適合（ascs_doctor.py:78-104, 51-75 で裏取り）。state-trust-contract は sec-p-005 のゼロトラスト姿勢を文書レベルで満たす
- 改善: loopback TCP は同一マシン別ユーザーからも到達可能で、恒久 UNVERIFIED のままにしない選択肢（UDS+0600 / UID 確認 / 脅威モデル ADR）を提示。pxpipe-safety の secret 除外が運用規律依存である点も残リスクとして明示
- 適用条件: sec-p-005 の when_not_to_apply（単一プロセス完結）に ASCS 層1は該当しない（loopback HTTP 通信が現存）

### Observability / SRE（確度: 中）
- 適合: 層ごとの独立着脱=バルクヘッド、単独決定者は sre-a-003（過剰保証の回避）に整合、fail-open でセッション継続性は担保
- 改善5点: サイレント fail-open の SLI 欠如 / exit code 2値の粗さ（ascs_doctor.py:291-328 裏取り）/ 課金バックエンド（claude -p / codex exec）が復旧経路のクリティカルパスに入る際の失敗切り分けログ欠如 / transcripts バックアップの保持期限未定義 / 復元検証がメタデータのみ（HEAD 一致チェックの追加案）
- 適用外: sre-p-008 の不変アーティファクト化は state=仮説の設計意図に反するため不適用。sre-p-007 は緩い類推まで（カナリア比較の直接適用は不可）

### Design Patterns / Code Structure（確度: 中、新設レンズ初回実走）
- 命名: 全体=Ports & Adapters（docs/adapter-interface.md の契約/binding 語彙とほぼ同型・確度高）/ 層1=Proxy・Decorator / 層2=Single Writer Principle（Mediator ではない点を区別）/ 層3+4=Memento のイベント駆動実装 / doctor=Facade（いずれもモデル知識と明示、KB 抜粋は一般的背景として参照）
- 白眉: 「構成（何を入れないか）による off スイッチ」= 設定でなく構成で競合を解消、という単独決定者の実装評価
- 改善: classify/report 分離が report_compression / report_single_decider で未完（ただし300行スクリプトには分離強行は過剰の留保付き）/ 層3+4 が1プラグインに束ねられ Port と Adapter の粒度不一致（透明に文書化済みだが運用者に伝わりにくい）
- 適用条件: Hexagonal 等の重い語彙は複数 runtime 拡張の実要求（Codex binding 現存）があって初めて複雑さに見合う。単一 runtime なら過剰設計（arch-t-003 when_not_to_apply に整合）

## 反対意見・適用条件（統合）

- 単一ユーザーの開発ワークステーション専用と割り切るなら、Security の技術強化（UDS/mTLS 相当）は運用コストだけ増やす過剰適用になりうる（sec-t-005 when_not_to_apply）。その割り切り自体を ADR にするのが本レビューの主提案
- read-only・フォーク禁止という自己制約は、構造的強制（真の排他制御）と本質的に競合する。「許容解として選んでいる」ことの明記が正しい着地で、制約撤廃の推奨ではない

## Sources

- カード: sec-p-005 / sec-p-008 / sec-t-005（security）、sre-p-007 / sre-p-008 / sre-a-003（sre）、arch-t-003（architecture）
- Layer2 FTS（design-patterns ドメイン未整備のためフォールバック）: JavaScriptデザインパターンを学ぶ 第2版 chunk sec-0073 / sec-0074（GoF 定義・3分類）、Cloud Native Go chunk sec-0444 / sec-0461（in-process vs RPC 分離 plugin 語彙）
- 実コード裏取り: plugins/ascs/scripts/ascs_doctor.py（51-75 / 78-104 / 107-112 / 238-328）、docs/architecture.md（114-163）、docs/adapter-interface.md、docs/state-trust-contract.md、docs/hook-responsibilities.md、docs/risk-register.md
- 需要記録: agent-company-os/logs/kb-fallback.log へフォールバック行を追記済み（クエリ: plugin pattern / デザインパターン 選定・適用、候補domain: design-patterns。集計側の正はログファイルのみ — 本レポートには集計対象のマーカー書式を書かない）

確度: 中 — レンズ報告は全て一次ファイル読了に基づくが、pxpipe 本体（上流）の実装と実運用の fail-open 発生頻度は未確認。未確認の残リスク: 47821 番ポートへの偽装リクエストが実際に何を引き起こせるか（上流実装依存）

## 運用メモ（3層システムの学び）

- 新設レンズ（Design Patterns）はカード未整備でも FTS + モデル知識明示のハイブリッドで初回から機能した。パターン名の当てはめは「モデル知識」と明示させる出力契約が効いた
- design-patterns ドメインの蒸留需要が今回初めて実測ログに載った（kb-fallback.log 1件目）。ユーザーからの明示要望もあり、R3（次ドメイン蒸留）の最有力候補
- レンズ agent は各3〜5 tool uses で完走（「検証最小限・報告優先」指示が有効、既知の教訓どおり）
