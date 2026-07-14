# スキル有用性のペア評価

この評価は、カードやSkillの存在ではなく、同一タスクの `baseline` と `assisted` を比較して採用価値を判定します。現在のカードは評価未完了のため、すべて `candidate` です。過去成果物内のcard_id文字列は採用証拠に数えません。

## 実施手順

1. `skill-utility-cases.json` の12件を固定し、baselineでは技術ライブラリを無効にして実行する。
2. 同じruntime・モデル・入力・採点者でassistedを実行する。assistedだけSkill/Gatewayを有効にする。
3. 人間の採点者が各所見を採用/誤検知に分類し、引用先のchunk実在と主張整合を確認する。
4. 生のprompt、書籍本文、生成出力は観測JSONへ保存せず、`utility-observation.schema.json` の集計値だけを保存する。
5. 次を実行する。

```bash
techlib eval score \
  --cases evals/skill-utility-cases.json \
  --baseline /path/to/baseline-observations.json \
  --assisted /path/to/assisted-observations.json \
  --json
```

モデル/APIを追加実行する評価は課金・外部送信に該当しうるため、アカウント、APIキー、上限を明示したHuman Approval Gateを別途通します。このrepoは観測値を捏造せず、未実施なら未実施のまま扱います。

## 合格条件

- ケース数12以上、うち否定ケース4以上、task_idが完全一致
- 採用所見の増分が正
- 誤検知率10%以下
- 引用正確性100%
- 時間増分30%以下
- コンテキスト増分30%以下
- 漏洩イベント0
- 否定ケースでのライブラリ呼び出し0

全条件合格後に限り、対象カードを `techlib cards transition <card-id> active --basis "paired utility eval <run-id> passed"` で昇格します。失敗したカードはcandidateのまま改善し、廃止判断には根拠を残します。
