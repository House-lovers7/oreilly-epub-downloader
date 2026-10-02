# Go Domain Checklist

> 由来: O'Reilly技術書からの蒸留カード（knowledge-base/cards/go/）。
> 各項目の詳細・出典は card_id で practices/antipatterns/tradeoffs.jsonl を引く。
> 2026-10-02: active カードのみ掲載（F2 昇格 39 枚）。candidate は精査パケット output/kb-promotion/2026-10-go.md を参照。

## ベストプラクティス（適用を検討したか）

- [ ] **外部に公開する構造体では sync.Mutex を埋め込まず非公開フィールドにする** (go-p-001): 外部に見せたくない mutex は `mu sync.Mutex` のように名前付きの非公開フィールドで持つ
- [ ] **go vet・errcheck・golangci-lint などの linter/formatter を CI や pre-commit で自動実行する** (go-p-002): 標準の go vet を常用し、shadow を vettool として連携させてシャドーイングを検出する
- [ ] **panic はプログラマーエラーと必須依存の初期化失敗に限り、通常の失敗は error を戻り値で返す** (go-p-003): panic はプログラマーエラー(例: 不正なステータスコード、nil の driver、二重登録)を知らせる場面に限定する
- [ ] **エラーを意図的に無視する場合は `_ =` で明示し、理由をコメントに書く** (go-p-004): 無視する error は `_ = notify()` のようにブランク識別子へ代入して、意図を明示する
- [ ] **defer で呼ぶ Close などのエラーも、明示的に無視するかログ・伝播のいずれかで扱う** (go-p-005): 最低限、`defer func() { _ = rows.Close() }()` のように無視を明示する
- [ ] **複数ゴルーチンが同じ変数を更新するときは atomic・Mutex・channel のいずれかで data race を防ぐ** (go-p-006): 単純な数値の更新は sync/atomic(例: atomic.AddInt64)で原子的に行う。対応型は int32/int64/uint32/uint64 で int には無い
- [ ] **ゴルーチンを起動するときは停止条件を決め、親が終了前に待てる設計にする** (go-p-007): `for v := range ch` で受信し続けるゴルーチンは、channel が確実に close される箇所があるかを確認する
- [ ] **mutex の fast path がインライン化できないときは、slow path を別関数へ切り出す** (go-p-012): fast path(例: CompareAndSwap が成功してロックが取れる)と slow path(すでにロック済み)を区別する
- [ ] **pprof のハンドラーはグローバル mux に任せず、専用の http.ServeMux に明示して登録する** (go-p-013): 新しい空の http.NewServeMux を作り、pprof.Index と pprof.Profile などを HandleFunc で登録する
- [ ] **ロック競合・ブロック待ちを見るには、既定で無効な block/mutex プロファイルを明示的に有効化する** (go-p-014): block プロファイルは runtime.SetBlockProfileRate(int) で非ゼロのレートを設定して有効化する(同期プリミティブ待ちの時間)
- [ ] **最適化の前後は pprof の -diff_base で比較し、差分を数値で確認する** (go-p-015): `go tool pprof -diff_base` で前後のプロファイルを比較し、関数の寄与の増減(正負のデルタ)を見る
- [ ] **channel の close は送信側だけが、終了の通知として行う** (go-p-016): 値を送り終えた送信側(生産者)が close(ch) を呼び、受信側は for-range または `v, ok := <-ch` の ok で終了を検出する
- [ ] **タイムアウト待ちの select では、結果 channel を 1 要素の buffered にして goroutine リークを防ぐ** (go-p-017): `results := make(chan int, 1)` のように 1 要素の buffer を持たせ、受信者がいなくても送信が完了するようにする
- [ ] **関数のシグネチャでは channel の方向(chan<- / <-chan)を指定する** (go-p-018): 送信するだけの関数の引数は `chan<- int`(send-only)にする
- [ ] **外部 HTTP 呼び出しのステータスコードは、クラス別の sentinel error に変換し %w でコードを添えて返す** (go-p-020): 200 のときだけ nil を返し、4xx(クライアント側)・5xx(サーバー側)・その他を別々の sentinel error(例: ErrClientSide)にする
- [ ] **mu.Lock() の直後に必ず defer mu.Unlock() を書く** (go-p-021): `mu.Lock()` の次の行に `defer mu.Unlock()` を置く
- [ ] **ゴルーチンの完了待ちは WaitGroup か errgroup を使い、エラー処理が要るかで選ぶ** (go-p-023): sync.WaitGroup は先に Add(n) を呼び、各ゴルーチンが Done を呼び、Wait で同期する
- [ ] **外部への HTTP 要求には http.Client の Timeout を設定し、応答のない相手を永久に待たない** (go-p-025): `http.Client{Timeout: 5 * time.Second}` のように Timeout を明示して使う(接続確立と応答取得の両方を制御できる)
- [ ] **CLI ツールは、具体的なエラーメッセージと意味のある終了コードで失敗を伝える** (go-p-028): 何が間違っていたかを具体的に示す(例: `--mode` は [full, basic] のいずれかでなければならない)。fmt.Errorf で文脈を足せる
- [ ] **複数の検証エラーは最初の 1 件で打ち切らず、errors.Join で 1 つの error にまとめて返す** (go-p-030): 無効なフィールドごとに error を []error へ append し、最後に `errors.Join(errs...)` を返す
- [ ] **独自のエラー型で原因を保持するなら Unwrap() を実装する** (go-p-031): エラー型に Err error フィールドを持たせ、引数なしで error を返すメソッド Unwrap を実装する
- [ ] **同じメッセージで複数のエラーをラップするときは、名前付き戻り値と defer でまとめる** (go-p-032): 戻り値(例: `(_ string, err error)`)に名前を付け、defer のクロージャ内で `if err != nil { err = fmt.Errorf("in DoSomeThings: %w", err) }` とする
- [ ] **並行コードを使うテストには goleak.VerifyNone を入れ、ゴルーチンリークをユニットテストで検出する** (go-p-035): 並行コードを含むユニット(またはテストファイル)ごとに、リークテストを用意する
- [ ] **エラーメッセージは小文字始まり・句読点なし・冗長な表現なしで、具体的な原因を書く** (go-p-036): 何が・なぜ・どのように失敗したかを具体的に書き、抽象的なメッセージにしない

## アンチパターン（該当していないか）

- [ ] **defer に変化する変数を値で渡して「最終値」を使えると誤解する** (go-a-001): 後で更新する値を defer 先で使うなら、`defer func(){ notify(status) }()` のようにクロージャで外部変数を参照させる(実行時に評価される)
- [ ] **同じエラーをログ出力したうえで return し、二重に処理する** (go-a-002): エラーは 1 回だけ処理する。ログ出力もエラー処理の一種なので、「ログする」か「返す」かのどちらかにする
- [ ] **HTTP リクエストの context を、レスポンス後も続く非同期処理へそのまま渡す** (go-a-003): context を伝播する前に、その context がいつキャンセルされるかを確認する
- [ ] **sync.Mutex などの sync 型を含む構造体を値レシーバや値渡しでコピーする** (go-a-004): sync.Mutex・RWMutex・WaitGroup・Once・Cond・Map・Pool を含む構造体のメソッドは、ポインタレシーバにする
- [ ] **Mutex を取得した状態で、同じ Mutex を取る String() などを呼ぶ文字列フォーマットを行う** (go-a-005): 入力検証は先に行い、問題が無い場合にだけ Lock を取るなど、ロックの範囲を狭める
- [ ] **ループの中で default 付き select を回して channel を非ブロックで確認し続ける** (go-a-006): select + default は「ブロックせず 1 回だけ確認する」用途(例: channel が close 済みかの判定)に限る
- [ ] **errors.As の第 2 引数にエラー型の変数を指すポインタでもインタフェースへのポインタでもない値を渡す** (go-a-009): 特定のインスタンスや値(センチネル)を探すときは errors.Is、特定の型を探すときは errors.As を使う
- [ ] **panic を recover して処理を継続する(ゼロ除算などをエラー返却でなく recover に頼る)** (go-a-010): ゼロ除算のような失敗しうる条件は、事前にチェックして error を返すのが「イディオム的」な処理
- [ ] **for ループの中で defer f.Close() を使い、全ループが終わるまでリソースを解放しない** (go-a-011): ループ内でリソースを取得するなら、使い終わった時点で明示的に Close() を呼ぶ(defer に任せない)

## トレードオフ（明示的に判断したか）

- [ ] **ジェネリクスは具体的なボイラープレートが現れてから使い、interface で足りる場面では使わない** (go-t-001): 型引数のメソッドを呼ぶだけ(例: io.Writer を受けて Write を呼ぶ)なら、ジェネリクスにせず interface を引数に直接使う
- [ ] **エラーの %w ラップはコンテキストを足せるが、元エラーを呼び出し側に晒して結合を生む** (go-t-002): 文脈を足しつつ元エラーを返したいときは fmt.Errorf の %w でラップする
- [ ] **channel は同期が必要なら unbuffered、buffered にするならサイズ 1 を既定にする** (go-t-003): ゴルーチン同士が既知の状態になる同期の保証が要るときは unbuffered channel を使う
- [ ] **sync.Mutex を既定にし、sync.RWMutex は性能問題が出てから計測して導入する** (go-t-006): 通常は sync.Mutex を使い、RWMutex は性能問題に直面したときにだけ検討する
- [ ] **共有状態の同期は、離散値の受け渡しには channel、大きなステートフル構造体には mutex と使い分ける** (go-t-007): データの所有権の受け渡し、作業単位の分配、非同期の結果通信など、多くの離散値を扱う場面は channel を使う
- [ ] **slice や map の容量を make で事前確保すると再割り当てを減らせるが、計測してから適用する** (go-t-009): 正確な長さが分かるなら `make([]int, n)`、最大量の見込みがつくなら `make([]int, 0, n)` のように容量だけ指定する
