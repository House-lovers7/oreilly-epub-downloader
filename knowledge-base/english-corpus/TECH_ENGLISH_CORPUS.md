# 技術英語学習コーパス（O'Reilly 49冊由来）

O'Reilly技術書49冊（英語、約306万トークン）から抽出した実例文をもとに構築した、技術英語をさらさら読む・書く・話すための学習リストです。全ての例文は購読コンテンツからの逐語引用のため、**個人の学習専用・非公開**です。外部送信・公開は行わないでください。

- 総項目数: 395（カテゴリ間の重複表現は優先度順に統合済み。優先順位: discourse > speaking > sub_technical > collocations）
- 各項目の例文は `knowledge-base/english-corpus/data/sentences.jsonl` からの逐語引用（創作なし）
- 機械検証: `scripts/verify_curation.py` で全項目のヘッダー・列数・空欄・引用の逐語一致・重複を検査済み

## サブテクニカル語彙（116項目）

カタカナ同根語を除く、日本人エンジニアにとって読解の壁になりやすい基本〜中級の一般語彙（副詞・接続詞・形容詞など）。

### accordingly
*副詞* — それに応じて

> Segmenting traces in this way helps you identify which user groups experience specific failures and allows you to build more realistic evaluation datasets, and improve your agents accordingly.
> —— *AI Agents: The Definitive Guide*

thereforeよりやや控えめで、前述の内容に応じて行動・対応することを示す

### adjacent
*形容詞* — 隣接する

> One last thing to mention regarding package documentation is that comments not adjacent to the declaration are omitted.
> —— *100 Go Mistakes and How to Avoid Them*

物理的・概念的に隣り合っている様子

### approximately
*副詞* — おおよそ、約

> The timeframe starts with user-level code; then a "stop the world" is executed, which occupies the four CPU cores for approximately 40 ms.
> —— *100 Go Mistakes and How to Avoid Them*

roughlyよりフォーマルで数値の前に置かれる

### arbitrary
*形容詞* — 任意の、恣意的な

> However, a string is a sequence of arbitrary bytes; it's not necessarily based on UTF-8.
> —— *100 Go Mistakes and How to Avoid Them*

規則性がなく自由に決められる、または独断的というニュアンスも

### arise
*動詞* — 生じる、発生する

> When designing an API, one question may arise: how do we deal with optional configurations?
> —— *100 Go Mistakes and How to Avoid Them*

問題や疑問が自然に生じる際に使う。riseと混同しやすい

### beneficial
*形容詞* — 有益な

> This kind of information is also beneficial if we suspect goroutine leaks.
> —— *100 Go Mistakes and How to Avoid Them*

usefulよりやや硬い書き言葉

### broadly
*副詞* — 大まかに、広く

> Broadly, there are users and there are builders.
> —— *An Illustrated Guide to AI Agents*

broadly speakingのように全体像を示す

### comparable
*形容詞* — 匹敵する、比較可能な

> Even though only a fraction of the parameters are updated, LoRA achieves performance comparable to full fine-tuning.
> —— *AI Agents: The Definitive Guide*

comparable to Xの形でXと同程度であることを示す

### compelling
*形容詞* — 説得力のある、魅力的な

> I'll focus particularly on one compelling category: adapter-based techniques.
> —— *AI Engineering*

議論や理由が強く人を納得させる様子

### comprehensive
*形容詞* — 包括的な、網羅的な

> This book offers a comprehensive, well-structured guide to the essential aspects of building generative AI systems.
> —— *AI Engineering*

抜け漏れなく全体をカバーしている様子

### concise
*形容詞* — 簡潔な

> Therefore, a package name should be short, concise, expressive, and, by convention, a single lowercase word.
> —— *100 Go Mistakes and How to Avoid Them*

無駄がなく要点を押さえた様子

### consequence
*名詞* — 結果、影響

> Rewards close the loop between action and consequence.
> —— *AI Agents: The Definitive Guide*

resultより「重大な帰結」のニュアンスを含むことが多い

### consequently
*副詞* — その結果として

> Consequently, if a function returns a slice, we shouldn't do as in other languages and return a non-nil collection for defensive reasons.
> —— *100 Go Mistakes and How to Avoid Them*

原因と結果の因果関係を明示するフォーマルな接続副詞

### considerable
*形容詞* — かなりの、相当な

> There is considerable confusion in the literature between a computer network and a distributed system.
> —— *Computer Networks, Fifth Edition*

名詞の前に置き量や程度の大きさを示す

### considerably
*副詞* — かなり、相当に

> Software engineering has evolved considerably during the past decades.
> —— *100 Go Mistakes and How to Avoid Them*

veryより書き言葉的

### contrast
*名詞* — 対比、対照

> In contrast, other goroutines will receive updates and print a message whenever a specific goal is reached (listener goroutines).
> —— *100 Go Mistakes and How to Avoid Them*

in contrastの形で頻出。対照的な違いを示す

### conversely
*副詞* — 逆に、反対に

> Conversely, if the gradients are large, they grow exponentially with each step, leading to instability in the learning process.
> —— *AI Engineering*

前文と対照的な内容を導入する書き言葉的な接続副詞

### convey
*動詞* — 伝える、示す

> It's not a dogmatic book: each solution is detailed to convey the context in which it should apply.
> —— *100 Go Mistakes and How to Avoid Them*

意味や意図を相手に伝達する様子

### crucial
*形容詞* — 決定的に重要な

> This step is crucial in ToT, as it ensures the agent doesn't simply proceed with the first idea but instead critically assesses the alternatives and chooses the most promising path to pursue.
> —— *AI Agents: The Definitive Guide*

importantより強い必須性を示す

### cumulative
*形容詞* — 累積的な

> The budget tracker checks the cumulative history of the run.
> —— *AI Agents: The Definitive Guide*

積み重なって増えていく様子

### denote
*動詞* — 示す、意味する

> For example, some languages, like Vietnamese, have pronouns to denote the relationship between the two speakers.
> —— *AI Engineering*

記号や用語が何を指すかを定義する際に使う

### desirable
*形容詞* — 望ましい

> Generally, having a nil pointer isn't a desirable state and means a probable bug.
> —— *100 Go Mistakes and How to Avoid Them*

理想として好ましい状態を示す

### distinct
*形容詞* — 明確に異なる、別個の

> A map provides an unordered collection of key-value pairs in which all the keys are distinct.
> —— *100 Go Mistakes and How to Avoid Them*

はっきり区別できる様子

### distinguish
*動詞* — 区別する

> Depending on your underlying language model, it may already have gathered experience, compared its own reasoning paths, and learned how to distinguish good decisions from poor ones.
> —— *AI Agents: The Definitive Guide*

distinguish A from Bの形で頻出

### downside
*名詞* — 欠点、マイナス面

> Another important downside is related to testing.
> —— *100 Go Mistakes and How to Avoid Them*

drawbackとほぼ同義でやや口語的

### dramatically
*副詞* — 劇的に

> KV caching speeds up inference dramatically, but at a cost.
> —— *AI Agents: The Definitive Guide*

変化の大きさ・急激さを強調する

### drawback
*名詞* — 欠点、短所

> The main drawback of this option is that following the copy and until the next garbage collection, we may consume twice the current memory for a short period.
> —— *100 Go Mistakes and How to Avoid Them*

デメリットを指すフォーマルな語

### entirely
*副詞* — 完全に

> Encoder-only architectures remove the decoder stack entirely and rely on bidirectional attention, which means every token can attend to every other token in the sequence.
> —— *AI Agents: The Definitive Guide*

completelyとほぼ同義だが書き言葉で好まれる

### essentially
*副詞* — 本質的には、要するに

> In a production-grade agentic system, you are essentially running two distinct types of "Correction Loops".
> —— *AI Agents: The Definitive Guide*

複雑な説明を簡潔にまとめる前置き

### eventually
*副詞* — 最終的に、いずれは

> If it's no longer referenced, it's eventually freed by the garbage collector (GC) if allocated on the heap.
> —— *100 Go Mistakes and How to Avoid Them*

時間が経過した末に至る結果を示す

### exclusively
*副詞* — もっぱら、排他的に

> The only data type that we omit is strings because a later chapter deals with this type exclusively.
> —— *100 Go Mistakes and How to Avoid Them*

他を除外して一つに限定するニュアンス

### explicit
*形容詞* — 明示的な

> LangGraph makes the stateful, graph based model explicit, while CrewAI presents a higher level framework around agents, crews, and flows.
> —— *AI Agents: The Definitive Guide*

暗黙でなく明確に述べられている様子。implicitの対義語

### explicitly
*副詞* — 明示的に

> For example, models such as Kimi K2, Llama 4, and Qwen3.6 are explicitly tuned for coding, tool use, and powering agentic systems.
> —— *AI Agents: The Definitive Guide*

implicitlyの対義語。暗黙でなく明確に示す様子

### extensive
*形容詞* — 広範な、大規模な

> Using a pointer can make the call more efficient, as doing so prevents making an extensive copy.
> —— *100 Go Mistakes and How to Avoid Them*

範囲・量が広く及ぶ様子

### extent
*名詞* — 程度、範囲

> That is the extent of your responsibility when it comes to implementing OAuth for your MCP server.
> —— *AI Agents with MCP*

to what extent、"to some extent"などの形で頻出

### facilitate
*動詞* — 促進する、容易にする

> Accompanied by concrete examples, it can help people learn new skills efficiently and facilitate remembering the context of a mistake and how to avoid it.
> —— *100 Go Mistakes and How to Avoid Them*

helpのフォーマルな言い換え

### fairly
*副詞* — かなり、まずまず

> It's fairly common to see interfaces being overused in Go projects.
> —— *100 Go Mistakes and How to Avoid Them*

fair（公正な）と語形が似るが無関係。程度を表すhedge語

### feasible
*形容詞* — 実行可能な

> If this isn't feasible, use an import alias to change the qualifier to differentiate the package name from the variable name, or think of a better name.
> —— *100 Go Mistakes and How to Avoid Them*

理論上でなく実際に実行できるかを問う語

### given
*前置詞* — 〜を踏まえると

> Given a task, the agent first reasons about what is missing or what step comes next, then takes actions by calling tools to retrieve data, run code, or check results.
> —— *AI Agents: The Definitive Guide*

Given X, Yの形で前提条件を示す

### gradually
*副詞* — 徐々に

> MCTS allows an LLM to explore a structured space of possible answers and gradually converge on the best one.
> —— *AI Agents: The Definitive Guide*

急激でなく段階的に変化する様子

### hence
*副詞* — それゆえに、従って

> Hence, it has strict compile-time rules, which ensure the code is type-safe in most cases.
> —— *100 Go Mistakes and How to Avoid Them*

論理的帰結を導く硬い書き言葉。文頭で使われることが多い

### ideally
*副詞* — 理想的には

> Ideally, you have already worked on an existing Go project at work or home.
> —— *100 Go Mistakes and How to Avoid Them*

現実とのギャップを含意しつつ望ましい状態を述べる

### implicit
*形容詞* — 暗黙の

> Routing decisions should never rely on implicit assumptions.
> —— *AI Agents: The Definitive Guide*

明示されていないが前提とされている様子

### inconsistent
*形容詞* — 一貫性のない

> This structure counters unstructured, one-shot prompts that often lead to inconsistent results with LLMs alone.
> —— *AI Agents: The Definitive Guide*

矛盾していたりばらつきがある様子

### increasingly
*副詞* — ますます

> Modern LLMs are not only capable of calling tools, they are increasingly trained and optimized specifically for agentic tasks.
> —— *AI Agents: The Definitive Guide*

時間とともに程度が増す様子を示す

### inherent
*形容詞* — 本質的に備わった、固有の

> These are just a few of the most popular use cases for agents, but agents' inherent flexibility and autonomy make the possibilities for their use nearly endless.
> —— *AI Agents with MCP*

外から付加されたものでなく元から備わる性質

### inherently
*副詞* — 本質的に、生まれつき

> This solution is inherently more straightforward than the first one (which was partial, as we didn't handle the error).
> —— *100 Go Mistakes and How to Avoid Them*

外部要因でなく内在する性質であることを示す

### intuitive
*形容詞* — 直感的な

> This might be intuitive: these are the main operations that could potentially return a large number of items, and so are the ones you'd most want to paginate.
> —— *AI Agents with MCP*

説明なしに理解・操作できる様子。UI文脈で頻出

### irrelevant
*形容詞* — 無関係な

> This flattens the distribution, reduces contrast between important and irrelevant tokens, and makes it harder for the model to identify key information.
> —— *AI Agents: The Definitive Guide*

relevantの対義語

### largely
*副詞* — 主として、大部分は

> Still, these actions were largely confined to the prompt.
> —— *AI Agents with MCP*

largeから意味を推測しにくい語。程度や割合を表す

### leverage
*動詞* — 活用する、てこにする

> Therefore, to leverage these architectures, concurrency has become critical for software developers.
> —— *100 Go Mistakes and How to Avoid Them*

useより「既存の資産を有利に使う」ニュアンスが強い

### likely
*形容詞* — 〜しそうな

> The discussions of most of the mistakes are accompanied by concrete examples to illustrate when we are likely to make such errors.
> —— *100 Go Mistakes and How to Avoid Them*

be likely to doの形で可能性の高さを示す

### likewise
*副詞* — 同様に

> Likewise, a traditional agent can reply only in text, but what if the situation requires it to have a voice instead?
> —— *An Illustrated Guide to AI Agents*

前述と同じパターンが当てはまることを示す

### mainly
*副詞* — 主に

> Type embedding is mainly used for convenience: in most cases, to promote behaviors.
> —— *100 Go Mistakes and How to Avoid Them*

largely/primarilyとほぼ同義でやや口語的

### malicious
*形容詞* — 悪意のある

> Otherwise, requests may be stuck forever due to an absence of time- outs or even malicious clients that exploit the fact that our server doesn't have any timeouts.
> —— *100 Go Mistakes and How to Avoid Them*

セキュリティ文脈で「悪意ある攻撃者・コード」を指す頻出語

### massive
*形容詞* — 膨大な、大規模な

> This is why we observed such a massive difference between the two benchmarks.
> —— *100 Go Mistakes and How to Avoid Them*

hugeより書き言葉的でインパクトを強調

### merely
*副詞* — 単に、ただ〜にすぎない

> This string merely represents the LLM's intention to take an action, but the action itself is not taken without outside intervention.
> —— *An Illustrated Guide to AI Agents*

onlyより硬く、過小評価・限定のニュアンスを含む

### mitigate
*動詞* — 緩和する、軽減する

> Let's look at a concrete example and then try to mitigate it.
> —— *100 Go Mistakes and How to Avoid Them*

リスクや問題の影響を和らげる際に使う

### moreover
*副詞* — さらに、その上

> Moreover, a key difference between traditional LLM usage and agentic systems is whether the workflow is stateless or stateful.
> —— *AI Agents: The Definitive Guide*

追加の論拠を重ねる接続副詞。furthermoreとほぼ同義

### namely
*副詞* — すなわち、具体的には

> Multi-turn conversations expose a vital flaw of LLMs, namely that they're forgetful entities and do not remember past conversations (Figure 1-9).
> —— *An Illustrated Guide to AI Agents*

直前の内容を具体的に言い換える際に使う

### naturally
*副詞* — 当然ながら

> Expressivity - We can define expressivity in a programming language by how naturally and intuitively we can write and read code.
> —— *100 Go Mistakes and How to Avoid Them*

文脈により「当然」と「自然に」の両義がある

### necessarily
*副詞* — 必ずしも（〜ない）

> They aren't necessarily adversarial, but emerge from execution under real conditions.
> —— *AI Agents: The Definitive Guide*

not necessarilyの形で部分否定を作る頻出パターン

### nevertheless
*副詞* — それにもかかわらず

> Nevertheless, there is considerable overlap between the two subjects.
> —— *Computer Networks, Fifth Edition*

howeverより強い譲歩のニュアンスを持つ

### notion
*名詞* — 概念、考え

> To understand the notion of an agent "harness", let's look at Example 1-5, programmed using the LangGraph Python SDK.
> —— *Agent Memory*

conceptよりやや軽い、漠然とした「考え」のニュアンス

### numerous
*形容詞* — 多数の

> Over the course of writing this book, I've seen three specification releases, numerous SDK updates, and at least one (as yet incomplete) major update to the Python SDK.
> —— *AI Agents with MCP*

manyのフォーマルな言い換え

### obviously
*副詞* — 明らかに

> This helps prevent obviously sensitive or malformed content from being persisted into long-term storage.
> —— *AI Agents: The Definitive Guide*

話者の確信を示す談話標識としても使われる

### partially
*副詞* — 部分的に

> The primary concern here is preventing untrusted or partially trusted code from accessing host resources, escaping its execution environment, or interfering with other workloads.
> —— *AI Agents: The Definitive Guide*

fullyの対義的な程度副詞

### particularly
*副詞* — 特に、とりわけ

> HSMs are particularly relevant to more advanced MAS.
> —— *AI Agents: The Definitive Guide*

一般論の中で強調したい点を導入する

### perspective
*名詞* — 視点、観点

> From an implementation perspective, this function is correct.
> —— *100 Go Mistakes and How to Avoid Them*

from a X perspectiveの形で頻出

### poorly
*副詞* — 不十分に、下手に

> A system that performs poorly with one technique might perform much better with another.
> —— *AI Engineering*

wellの対義語

### precisely
*副詞* — 正確に、まさに

> If a client can pass multiple options, but we want to handle precisely the case that a port is invalid, it makes error handling more complex.
> —— *100 Go Mistakes and How to Avoid Them*

exactlyよりやや硬い

### predictable
*形容詞* — 予測可能な

> These constraints are what make agents viable today: safe to deploy, predictable in behavior, and aligned with their intended goals.
> —— *AI Agents: The Definitive Guide*

結果が事前に見通せる様子

### primarily
*副詞* — 主に、第一に

> Sub-agents are primarily used to isolate context and to apply specialized instructions, so the main agent stays focused on high-level planning rather than implementation details.
> —— *AI Agents: The Definitive Guide*

複数要因のうち最も重要なものを示す

### prominent
*形容詞* — 顕著な、著名な

> We have seen two prominent cases, one to signal a programmer error and another where our application fails to create a mandatory dependency.
> —— *100 Go Mistakes and How to Avoid Them*

目立って際立っている様子

### prone
*形容詞* — 〜しがちな、〜の傾向がある

> This principle, called variable shadowing, is prone to common mistakes.
> —— *100 Go Mistakes and How to Avoid Them*

prone to Xの形で好ましくない傾向を述べる

### properly
*副詞* — 適切に、きちんと

> For the framework to work properly, you need to have a model callback.
> —— *AI Agents: The Definitive Guide*

correctlyより広く「本来あるべき形で」の意味

### provided
*形容詞* — 与えられた、提供された

> Hence, we also need to return an error if the provided type is unknown.
> —— *100 Go Mistakes and How to Avoid Them*

the provided Xの形でAPIドキュメント等に頻出。接続詞的に"provided that〜"（〜という条件で）の用法もある

### rarely
*副詞* — めったに〜ない

> First, let's note that it's rarely a necessity, and it means that whatever the use case, we can probably solve it as well without type embedding.
> —— *100 Go Mistakes and How to Avoid Them*

頻度が低いことを示す

### redundant
*形容詞* — 冗長な、不要な

> For example, GoLand, the Go JetBrains IDE, warns about a redundant type conversion.
> —— *100 Go Mistakes and How to Avoid Them*

重複していて余分・不要であることを指す

### regarding
*前置詞* — 〜に関して

> While working in this new context, I noticed some common patterns regarding Go coding mistakes.
> —— *100 Go Mistakes and How to Avoid Them*

aboutのフォーマルな言い換え

### relatively
*副詞* — 比較的

> In practice, it allows even relatively small models to perform complex tasks more reliably, while making their decision-making process transparent.
> —— *AI Agents: The Definitive Guide*

絶対的でなく相対的な評価であることを明示する

### relevant
*形容詞* — 関連する、妥当な

> HSMs are particularly relevant to more advanced MAS.
> —— *AI Agents: The Definitive Guide*

話題・文脈に直接関係している様子

### respectively
*副詞* — それぞれ

> There are two methods that set the perfect stage for you to understand the tradeoff between exploring more answers or going deeper into a specific answer: repeated sampling and sequential sampling, respectively.
> —— *AI Agents: The Definitive Guide*

複数の対象を列挙順に対応させる際に文末で使う

### roughly
*副詞* — おおよそ

> As the context grows, the denominator of Softmax, which sums over all token scores, becomes very large while each individual score stays roughly the same.
> —— *AI Agents: The Definitive Guide*

正確でないことを断る概数表現

### scope
*名詞* — 範囲、対象領域

> The scope of a variable refers to the places a variable can be referenced: in other words, the part of an application where a name binding is valid.
> —— *100 Go Mistakes and How to Avoid Them*

プロジェクトや変数の適用範囲を指す

### sensible
*形容詞* — 分別のある、賢明な

> While some companies chase the latest hype, sensible business decisions are still being made based on returns on investment, not hype.
> —— *AI Engineering*

sensitive（敏感な）と綴りが似ており混同注意

### significant
*形容詞* — 著しい、重要な

> A significant part of software complexity comes from the fact that, as developers, we strive to think about imaginary futures.
> —— *100 Go Mistakes and How to Avoid Them*

importantよりデータ・規模の大きさを含意することが多い

### significantly
*副詞* — 著しく、大幅に

> Then it grows significantly after having added 1 million elements to the map.
> —— *100 Go Mistakes and How to Avoid Them*

無視できない程度であることを示す

### similarly
*副詞* — 同様に

> Agents are similarly constrained by their workflows, operating only within the scope of the tools, permissions, and safeguards they are provided.
> —— *AI Agents: The Definitive Guide*

likewiseとほぼ同義でやや口語寄り

### slightly
*副詞* — わずかに

> Of these two solutions, we have seen that the second tends to be slightly faster.
> —— *100 Go Mistakes and How to Avoid Them*

程度がわずかであることを示す

### solely
*副詞* — もっぱら、〜のみ

> Because of this, early evaluation shouldn't rely solely on standardized benchmarks.
> —— *AI Agents: The Definitive Guide*

onlyの硬い言い換え。単一の要因を強調

### sophisticated
*形容詞* — 洗練された、高度な

> Later on, Claude Shannon used more sophisticated statistics to decipher enemies' messages during the Second World War.
> —— *AI Engineering*

技術・手法が高度で複雑に発達している様子

### span
*動詞* — （範囲に）またがる、及ぶ

> In more complex systems, tracing may span multiple services such as agent runtimes, MCP servers, or external APIs.
> —— *AI Agents: The Definitive Guide*

空間・時間・システムの範囲を横断することを示す

### specifically
*副詞* — 具体的には

> Handling an error multiple times is a mistake made frequently by developers, not specifically in Go.
> —— *100 Go Mistakes and How to Avoid Them*

一般論を絞り込んで詳細を述べる際に使う

### straightforward
*形容詞* — 分かりやすい、単純な

> However, building a mental model encompassing all the different cases is probably not a straightforward task.
> —— *100 Go Mistakes and How to Avoid Them*

複雑さがなく直接理解・実行できる様子

### strictly
*副詞* — 厳密に

> Strictly speaking, however, an AI agent does not need to involve a language model at all.
> —— *AI Agents: The Definitive Guide*

strictly speakingの形で用語の正確な定義を断る際に頻出

### subsequent
*形容詞* — その後の、後続の

> The system keeps track of which agent was last active so that subsequent interactions continue seamlessly with the right one.
> —— *AI Agents: The Definitive Guide*

followingのフォーマルな言い換え

### substantial
*形容詞* — かなりの、実質的な

> This example demonstrates how spatial locality can have a substantial impact on performance.
> —— *100 Go Mistakes and How to Avoid Them*

considerableと近いが「量・規模が大きい」を強調

### subtle
*形容詞* — 微妙な、繊細な

> There is a subtle difference between simple and easy.
> —— *100 Go Mistakes and How to Avoid Them*

気づきにくいほどわずかな違いを指す

### sufficient
*形容詞* — 十分な

> The term ML engineering won't be sufficient to capture this differentiation.
> —— *AI Engineering*

enoughのフォーマルな言い換え

### suitable
*形容詞* — 適した

> Observing how important concurrency is these days also demonstrates why Go is such a suitable language for the present and probably for the foreseeable future.
> —— *100 Go Mistakes and How to Avoid Them*

目的・条件に合っている様子

### surprisingly
*副詞* — 驚くほど、意外にも

> Surprisingly, the parallel version is almost an order of magnitude slower.
> —— *100 Go Mistakes and How to Avoid Them*

話者の予想に反する結果を導入する談話標識

### thus
*副詞* — このように、従って

> The otherwise valid generated JSONs can also be truncated, and thus not parsable, if the generation stops too soon, such as when it reaches the maximum output token length.
> —— *AI Engineering*

henceと同様に結論・要約を導く

### tightly
*副詞* — 密接に、きつく

> Their results showed that both forms of compute are tightly related.
> —— *An Illustrated Guide to AI Agents*

tightly coupledのように結合の強さを表す

### transparent
*形容詞* — （比喩的に）透明性のある、隠し立てのない

> To be transparent, I was also a decent source of inspiration regarding mistakes.
> —— *100 Go Mistakes and How to Avoid Them*

物理的な「透明」だけでなく「情報公開・正直」の意味でも頻出

### trivial
*形容詞* — 些細な、自明な

> We must also understand that allocating on the stack is faster for the Go runtime because it's trivial: a pointer references the following available memory address.
> —— *100 Go Mistakes and How to Avoid Them*

重要でない、またはCS文脈では「自明で証明不要」の意味でも使われる

### ubiquitous
*形容詞* — 至る所にある、遍在する

> Customer service agents are becoming ubiquitous.
> —— *AI Agents with MCP*

どこにでも存在し当たり前になっている様子

### ultimately
*副詞* — 最終的には

> No amount of internal hardening changes the fact that your agent ultimately depends on external systems you don't control.
> —— *AI Agents: The Definitive Guide*

一連のプロセスの結論を導く

### underlying
*形容詞* — 根底にある、基礎となる

> The transport is the underlying communication protocol that allows communication between the client and server.
> —— *AI Agents with MCP*

表面には現れない基盤・原因を指す

### unlikely
*形容詞* — ありそうにない

> Even though general-purpose foundation models can answer everyday questions about different domains, they are unlikely to perform well on domain-specific tasks, especially if they never saw these tasks during training.
> —— *AI Engineering*

likelyの対義語

### utilize
*動詞* — 活用する、利用する

> If you run attention naively on modern GPUs, you are paying for compute you cannot fully utilize.
> —— *AI Agents: The Definitive Guide*

useのフォーマルな言い換え

### variant
*名詞* — 変種、派生形

> Another popular variant of agents is the coding agent.
> —— *An Illustrated Guide to AI Agents*

元の形から派生した別バージョンを指す

### vital
*形容詞* — 不可欠な、極めて重要な

> However, remember that consistency is also vital to ease maintainability.
> —— *100 Go Mistakes and How to Avoid Them*

crucialとほぼ同義

### whereas
*接続詞* — 一方で〜

> Closed models remove infrastructure complexity and provide direct access, whereas open models might require infrastructure management.
> —— *AI Agents: The Definitive Guide*

2つの事柄を対比する。whileよりフォーマルで文書向き

### widespread
*形容詞* — 広範囲に及ぶ、普及した

> Forgetting to pass an appropriate value for both of these parameters when it makes sense is a widespread mistake.
> —— *100 Go Mistakes and How to Avoid Them*

広い範囲で一般的に見られる様子

### yield
*動詞* — （結果を）もたらす、生み出す

> Because a nil pointer is a valid receiver, converting the result into an interface won't yield a nil value.
> —— *100 Go Mistakes and How to Avoid Them*

produceのフォーマルな言い換え。「譲る」の意味もある多義語

## コロケーション（88項目）

技術文書に頻出する語の組み合わせ・定型的な言い回し（trade-off, edge case, rule of thumb 系統）。bigram/trigramのlog_dice（結合度）とdoc_freq（出現書籍数）に基づき選定。

### access control
*名詞句* — アクセス制御

> Organizations can implement granular access control, audit mechanisms, and on-prem encryption layers.
> —— *AI Agents: The Definitive Guide*

誰がどのリソースにアクセスできるかを管理する仕組み。

### ad hoc
*形容詞句* — その場限りの、場当たり的な

> Otherwise, and in most cases, we should handle initializations through ad hoc functions.
> —— *100 Go Mistakes and How to Avoid Them*

正式な設計ではなく、必要に応じて即席で対応することを指す。やや否定的なニュアンスを含むこともある。

### ask yourself
*動詞句* — 自問する

> You might ask yourself why I didn't introduce the models at the beginning.
> —— *AI Agents: The Definitive Guide*

読者に内省・自己確認を促すレトリカルな表現。

### at hand
*形容詞句* — 目下の、手元の

> The vendor incident writeup and billing notes in Google Drive are real working documents about the problem at hand.
> —— *Agent Memory*

“the problem at hand”のように、今まさに扱っている対象を指す定型表現。

### at scale
*副詞句* — 大規模に、スケールした状態で

> Instead, Go utilizes a few essential characteristics when adopting a language at scale for an organization.
> —— *100 Go Mistakes and How to Avoid Them*

小規模な検証ではなく、実運用規模で物事が成り立つかを議論する時に使う。

### automated testing
*名詞句* — 自動テスト

> Automated testing usually involves writing tests in code that can be run automatically to verify the correctness of the server's behavior.
> —— *AI Agents with MCP*

手動ではなくスクリプト等で自動的に実行されるテスト。

### back and forth
*副詞句* — 行き来して、往復して

> The handoff tools ensure the workflow can bounce back and forth when more sources are needed or when it's time to synthesize.
> —— *AI Agents: The Definitive Guide*

2つの主体・状態の間を繰り返し行き来する様子を表す。

### backward compatibility
*名詞句* — 後方互換性

> Technically, 802.3u is not a new standard, but an addendum to the existing 802.3 standard (to emphasize its backward compatibility).
> —— *Computer Networks, Fifth Edition*

新しいバージョンが旧バージョンの仕様・データと問題なく動作する性質。

### best practices
*名詞句* — ベストプラクティス、推奨手法

> Before you start to implement the MCP server, I want to cover some best practices.
> —— *AI Agents: The Definitive Guide*

経験的に効果が実証されている推奨のやり方。

### blast radius
*名詞句* — 影響範囲、被害範囲

> A governance layer decides what signals are allowed to pass, reducing blast radius and preventing unauthorized execution.
> —— *AI Agents: The Definitive Guide*

障害やセキュリティ侵害が起きた際に波及する範囲を爆発の比喩で表す。

### building blocks
*名詞句* — 構成要素、基本パーツ

> This highlights how these methods can become powerful building blocks once you integrate them into your overall agentic workflow.
> —— *AI Agents: The Definitive Guide*

より大きなシステムを組み立てる際の基礎となる部品・要素。

### business logic
*名詞句* — ビジネスロジック

> A memory methodology is the set of standing rules and business logic about your store and what it can contain.
> —— *Agent Memory*

アプリケーションの中核となる業務ルール・処理を指し、UIやインフラ層と対比される。

### by default
*副詞句* — デフォルトでは、初期設定では

> Therefore, the worst-case time complexity for these three operations is O(p), where p is the total number of elements in the buckets (one bucket by default, multiple buckets in case of overflows).
> —— *100 Go Mistakes and How to Avoid Them*

明示的に設定を変更しない限り適用される既定の挙動を示す。

### by design
*副詞句* — 設計上意図的に

> Their autonomy is bounded by design, which is precisely what makes them practical, safe, and deployable.
> —— *AI Agents: The Definitive Guide*

偶然ではなく、最初からそう作られている（意図された挙動である）ことを強調する。

### closely related
*形容詞句* — 密接に関連している

> All four metrics - cross entropy, perplexity, BPC, and BPB - are closely related.
> —— *AI Engineering*

複数の概念・指標が強い関連性を持つことを表す。

### cloud providers
*名詞句* — クラウド事業者

> This is usually the same schema for common cloud providers and is adapted from the Qwen documentation on deploying the model via vLLM.
> —— *AI Agents: The Definitive Guide*

AWS/GCP/Azureなどクラウドサービスを提供する企業を指す。

### command line
*名詞句* — コマンドライン

> NOTE We can also delve into profiling data via a command line.
> —— *100 Go Mistakes and How to Avoid Them*

テキストコマンドでコンピュータを操作するインターフェース。

### competitive advantage
*名詞句* — 競争優位性

> Goldman Sachs Research estimated that AI investment could approach $100 billion in the US and $200 billion globally by 2025.9 AI is often mentioned as a competitive advantage.
> —— *AI Engineering*

他社に対して優位に立てる強みを指すビジネス用語。

### computationally expensive
*形容詞句* — 計算コストが高い

> For a language model with a large vocabulary, this process is computationally expensive.
> —— *AI Engineering*

処理に多くの計算資源・時間を要することを表す。

### compute resources
*名詞句* — 計算リソース

> Second, training large language models (LLMs) requires data, compute resources, and specialized talent that only a few organizations can afford.
> —— *AI Engineering*

CPU/GPU/メモリなど処理に必要な計算資源。

### configuration files
*名詞句* — 設定ファイル

> It's common to use templates to generate documents that follow a specific structure, such as invoices, resumes, tax forms, bank statements, event agendas, product catalogs, contracts, configuration files, etc.
> —— *AI Engineering*

アプリケーションの動作設定を記述したファイル群。

### context window
*名詞句* — コンテキストウィンドウ

> In addition, you'll map context window tradeoffs to deployment strategies, and understand when specialization through fine-tuning or adapters pays off.
> —— *AI Agents: The Definitive Guide*

LLMが一度に処理できる入力トークンの範囲。

### continuous delivery
*名詞句* — 継続的デリバリー

> His topics of interest include software architecture, continuous delivery, functional programming, and cutting-edge software innovations.
> —— *Architecture as Code*

コード変更をいつでも本番リリース可能な状態に保つ開発プラクティス。

### continuous integration
*名詞句* — 継続的インテグレーション

> Many teams wire metrics tools into their continuous integration pipelines to gather code-level metrics.
> —— *Architecture as Code*

開発者の変更を頻繁に統合し自動テストする開発プラクティス。

### control plane
*名詞句* — コントロールプレーン、制御層

> Middleware forms the control plane of a deep agent.
> —— *AI Agents: The Definitive Guide*

システムの実際のデータ処理ではなく、その振る舞いを管理・制御する層を指す。

### current directory
*名詞句* — カレントディレクトリ

> In both cases, the period denotes the current directory.
> —— *Core Java, Vol. I: Fundamentals, 14th Edition*

コマンドやプロセスが現在作業している対象のディレクトリ。

### de facto
*形容詞句* — 事実上の（標準など）

> An empty struct is a de facto standard to convey an absence of meaning.
> —— *100 Go Mistakes and How to Avoid Them*

公式に定められたわけではないが、実質的にそう機能している状態を表す。“de facto standard”の形で頻出。

### decision making
*名詞句* — 意思決定

> Finally, communication is successful when the receiver not only understands the information but retains it and incorporates it into their decision making.
> —— *Communicating with Data*

情報をもとに判断・選択を行うプロセス。

### dig deeper
*動詞句* — さらに深掘りする

> We'll dig deeper into RLVR and various types of verifiers at multiple points in the book.
> —— *An Illustrated Guide to AI Agents*

dive deeperとほぼ同義。より探索的なニュアンスをやや含む。

### disk space
*名詞句* — ディスク容量

> These sandboxes have to be defined with certain limited resources (e.g., in memory, processor, or disk space).
> —— *An Illustrated Guide to AI Agents*

ストレージの空き容量を指す基本語彙。

### distributed systems
*名詞句* — 分散システム

> NOTE Internally, the race detector uses vector clocks, a data structure used to determine a partial ordering of events (and also used in distributed systems such as databases).
> —— *100 Go Mistakes and How to Avoid Them*

複数のマシンが協調して一つのシステムとして動作する構成。

### dive deeper into
*動詞句* — ~をより深く掘り下げる

> Chapter 3 outlines the common building blocks for AI platforms, and subsequent chapters dive deeper into specific capabilities.
> —— *Building AI Agent Platforms*

概要から一歩踏み込んで詳細に検討する際の前置きとして使う。

### domain experts
*名詞句* — ドメインエキスパート、業務専門家

> When you build agent systems, you usually start by iterating on prompts, tools, and workflows together with early test users or domain experts.
> —— *AI Agents: The Definitive Guide*

特定の業務領域について深い知識を持つ専門家。

### edge cases
*名詞句* — 境界値ケース、例外的な入力

> Conversely, the second version requires scanning down one column to see the expected execution flow and down the second column to see how the edge cases are handled, as figure 2.1 shows.
> —— *100 Go Mistakes and How to Avoid Them*

通常想定される範囲の端・境界にあたる特殊な入力やケースを指す開発用語。

### end to end
*形容詞句/副詞句* — 一連の流れを通して、エンドツーエンドで

> Example 3-9 runs one task end to end, allows tool use, records the final answer, and writes rewards and metrics on the trajectory for ART.
> —— *AI Agents: The Definitive Guide*

プロセスの最初から最後まで途切れなく扱うことを示す。

### environment variables
*名詞句* — 環境変数

> For that reason, some projects favor the approach of checking the test category using environment variables.
> —— *100 Go Mistakes and How to Avoid Them*

OS・実行環境が保持する設定値で、プログラムから参照できるもの。

### error handling
*名詞句* — エラーハンドリング

> Chapter 7, "Error management," walks through idiomatic and accurate error handling in Go.
> —— *100 Go Mistakes and How to Avoid Them*

プログラム中で発生するエラーを検知・処理する仕組み。

### failure modes
*名詞句* — 故障モード、失敗パターン

> Different models have different failure modes, and the Factory Pattern lets you tailor the "contract" to the specific strengths or weaknesses of the model you're calling at runtime.
> —— *AI Agents: The Definitive Guide*

システムやモデルがどのように失敗しうるかの類型を指す。

### fault tolerance
*名詞句* — 耐障害性

> Example 5-7 illustrates how you can use checkpointing as fault tolerance.
> —— *AI Agents: The Definitive Guide*

一部の障害が発生してもシステム全体が機能し続ける性質を指す。

### feedback loop
*名詞句* — フィードバックループ

> Like a developer's feedback loop, the environment provides signals such as errors, gaps, or confirmations that guide the next iteration.
> —— *AI Agents: The Definitive Guide*

結果を観測して次の行動に反映する循環的な仕組み。

### happy path
*名詞句* — 正常系（の処理フロー）

> Align the happy path to the left; you should quickly be able to scan down one column to see the expected execution flow.
> —— *100 Go Mistakes and How to Avoid Them*

エラーが起きない前提の、最も典型的な処理の流れを指すエンジニア用語。

### high availability
*名詞句* — 高可用性

> Production-grade systems will demand that these databases consider crucial non-functional needs such as high availability, scalability, and robust backup strategies.
> —— *Building AI Agent Platforms*

障害が起きてもサービスが継続して利用できる性質。

### high-level overview
*名詞句* — 概要、大局的な説明

> Figure 3-3 shows a high-level overview of how this process works.
> —— *AI Agents: The Definitive Guide*

詳細を省いた全体像の説明を指す。

### highly recommend
*動詞句* — 強く推奨する

> To run the examples in this chapter, I highly recommend you install and use MCP Inspector.
> —— *AI Agents with MCP*

“I highly recommend ~”の形で著者が読者に強く勧める時の定型表現。

### in depth
*副詞句* — 詳細に、深く

> Memory will be covered in depth in chapter Chapter 10.
> —— *AI Agents: The Definitive Guide*

表面的にではなく踏み込んで扱うことを示す。

### in isolation
*副詞句* — 単独で、切り離して

> Comparing several candidates is easier for a language model than grading one in isolation.
> —— *AI Agents: The Definitive Guide*

他の要素と組み合わせず、一つだけを対象にして評価・検討することを示す。

### in place
*副詞句* — 導入済みで、整った状態で

> Once you have a runnable app and checkpoints in place, the next step is to make its execution observable.
> —— *AI Agents: The Definitive Guide*

仕組みや対策がすでに設置・運用されている状態を表す。

### in the wild
*副詞句* — 実環境で、野放しの状態で

> Running agents that can execute tools or access files in the wild without sandboxes, execution boundaries, or governed tool usage is like free solo climbing.
> —— *AI Agents: The Definitive Guide*

テスト環境ではなく実際の本番・現実世界で動いている状態を指すやや口語的な表現。

### inner workings
*名詞句* — 内部の仕組み、動作原理

> Now that we've seen the inputs and outputs of the model and covered how the model gets trained, it's time to look inside the trained model and get a sense of the inner workings.
> —— *An Illustrated Guide to AI Agents*

システムやモデルが内部でどう機能しているかを指す。

### integration tests
*名詞句* — 結合テスト

> Although integration tests are helpful, that's not always what we want to do.
> —— *100 Go Mistakes and How to Avoid Them*

複数のコンポーネントを組み合わせた際の動作を検証するテスト。

### keep track of
*動詞句* — ~を把握し続ける、記録し続ける

> Create the state to keep track of the next worker.
> —— *AI Agents: The Definitive Guide*

状態や進捗を見失わないよう継続的に管理することを表す。

### knowledge base
*名詞句* — ナレッジベース

> MCP Inspector with the knowledge_base resource listed in the left panel and loaded in the right.
> —— *AI Agents with MCP*

検索・参照可能な形で蓄積された知識・情報の集合。

### moving parts
*名詞句* — 可動部分、変動要素

> In other words, context engineering is much an architectural problem that needs to be solved with lots of moving parts, like efficiently tracking, storing, and retrieving all existing and created information.
> —— *An Illustrated Guide to AI Agents*

比喩的に「動く・変化しうる構成要素の数」を表し、複雑さの目安として使われる。

### naming conventions
*名詞句* — 命名規則

> It does mean that your onboarding will need to dynamically create new buckets that conform to the naming conventions and uniqueness requirements of S3.
> —— *Building Multi-Tenant SaaS Architectures*

変数・関数・ファイルなどの名前の付け方に関する取り決め。

### object-oriented programming
*名詞句* — オブジェクト指向プログラミング

> This concept is actually a familiar one and is used throughout computer science, where it is variously known as information hiding, abstract data types, data encapsulation, and object-oriented programming.
> —— *Computer Networks, Fifth Edition*

クラス・オブジェクトを中心にプログラムを構成するパラダイム。

### on demand
*副詞句* — オンデマンドで、必要に応じて

> Execution environments are created on demand, scoped to a single task, session, or agent run, and destroyed immediately afterward.
> —— *AI Agents: The Definitive Guide*

事前に確保せず、必要になった時点でリソースや処理を生成することを示す。

### operating system
*名詞句* — オペレーティングシステム、OS

> Sandboxing coding agent execution isn't only about isolating code from the host operating system.
> —— *AI Agents: The Definitive Guide*

ハードウェアとアプリケーションの間に立つ基本ソフトウェア。

### pay attention to
*動詞句* — ~に注意を払う

> As we'll explain further later on, even commitment-based discount programs like SPs/RIs/CUDs don't pay attention to what server they're attached to.
> —— *Cloud FinOps, 2nd Edition*

特定の要素に意識を向けて注視することを促す表現。

### personally identifiable information
*名詞句* — 個人を特定できる情報（PII）

> A supervisor agent may only route tasks by category, while a retrieval agent queries raw PII (personally identifiable information) or financial records.
> —— *AI Agents: The Definitive Guide*

氏名・住所など個人を特定しうるデータを指す法務・プライバシー用語。

### prompt injection
*名詞句* — プロンプトインジェクション

> However, in this chapter you don't look into threats from the outside, and not how to safeguard your agents against prompt injection or malicious users.
> —— *AI Agents: The Definitive Guide*

悪意ある入力でLLMの指示・挙動を乗っ取ろうとする攻撃手法。

### race conditions
*名詞句* — 競合状態

> Enable SQLite WAL mode for better concurrency, and use atomic updates to prevent race conditions.
> —— *AI Agents: The Definitive Guide*

複数の処理が同じ資源に同時アクセスすることで結果が実行順序に依存してしまう不具合の温床。

### rate limiting
*名詞句* — レート制限

> At the input level, guardrails can include input validation mechanisms to prevent injection attacks, content filtering to block inappropriate content or sensitive data and rate limiting to prevent abuse.
> —— *Building AI Agent Platforms*

一定時間あたりのリクエスト数などを制限する仕組み。

### real world
*形容詞句* — 実世界の、実運用の

> Even as large generative models dominate headlines, encoder-only transformers continue to play a crucial role in real world systems.
> —— *AI Agents: The Definitive Guide*

理論・実験環境ではなく実際の運用環境を指す形容表現。

### regular expressions
*名詞句* — 正規表現

> Templates can also be used to generate data that follows a certain grammar and syntax, such as regular expressions and math equations.
> —— *AI Engineering*

文字列パターンを記述・照合するための表記法。

### relatively straightforward
*形容詞句* — 比較的単純な、わりと簡単な

> Given that gateways are relatively straightforward to implement, there are many off-the-shelf gateways.
> —— *AI Engineering*

難易度がそこまで高くないことを控えめに表現する言い方。

### separation of concerns
*名詞句* — 関心の分離

> For the direct access pattern to work effectively at scale, a clear separation of concerns is vital.
> —— *Building AI Agent Platforms*

異なる責務を持つコードやモジュールを分けて設計すべきというソフトウェア設計の基本原則。

### set up
*動詞句* — ~を構築する、セットアップする

> To complete the supervisor architecture, we need to set up a supervisor that can coordinate across all four research agents.
> —— *AI Agents: The Definitive Guide*

環境やシステムを準備・構成することを表す基本動詞句。

### shut down
*動詞句* — ~を停止する、シャットダウンする

> Cloud spend can drive more revenue, signal customer base growth, enable more product and feature release velocity, or even help shut down a data center.
> —— *Cloud FinOps, 2nd Edition*

システムやサービスの稼働を止めることを表す。

### side effects
*名詞句* — 副作用

> They take the current state, perform computation or side effects, and return an updated state.
> —— *AI Agents: The Definitive Guide*

主目的の処理に伴って生じる、意図していない状態変化や影響。

### slow down
*動詞句* — 減速する、ペースを落とす

> Simple tricks like asking the model to slow down and think step by step can yield surprising improvements.
> —— *AI Engineering*

処理速度や進行のペースを意図的・結果的に落とすことを表す。

### sql injection
*名詞句* — SQLインジェクション

> Security - This approach reduces the risks of SQL injection attacks.
> —— *100 Go Mistakes and How to Avoid Them*

不正なSQL文を注入してデータベースを不正操作する攻撃手法。

### starting point
*名詞句* — 出発点、起点

> Docker is the most common starting point to isolate your agent's execution.
> —— *AI Agents: The Definitive Guide*

議論や作業を始める際の基準・拠り所となる地点を指す。

### strongly recommend
*動詞句* — 強く推奨する

> H100) and model size (7B vs. 70B) creates a different bottleneck, so I strongly recommend you run your own benchmarks.
> —— *AI Agents: The Definitive Guide*

highly recommendとほぼ同義で置き換え可能。

### subject matter
*名詞句* — 対象分野、専門領域

> For that reason, I usually run two evaluation tracks in parallel while building the prototype: behavioral testing with subject matter experts (SMEs) and early vulnerability checks on the model and system setup.
> —— *AI Agents: The Definitive Guide*

“subject matter experts”の形で、扱っているテーマそのものを指す。

### take advantage of
*動詞句* — ~を活用する、~につけこむ

> While you should take advantage of available data, you should never fully trust it.
> —— *AI Engineering*

利用可能なものを積極的に使う意味。文脈次第で「弱点につけこむ」という否定的な意味にもなる。

### third party
*形容詞句/名詞句* — 第三者の、サードパーティの

> In the following year (2023), OpenAI introduced ChatGPT plugins: third party tools that could be directly exposed to ChatGPT.
> —— *AI Agents with MCP*

開発元・提供元とは別の外部の主体・製品を指す。

### tightly coupled
*形容詞句* — 密結合の

> Injects configuration and cache so planning and memoization are tightly coupled.
> —— *AI Agents: The Definitive Guide*

コンポーネント同士が強く依存し合い、切り離しにくい設計状態を指す。

### trial and error
*名詞句* — 試行錯誤

> What was once trial and error becomes deliberate improvement in your system.
> —— *AI Agents: The Definitive Guide*

体系的な方法ではなく、試して失敗を繰り返しながら進める手法を指す。

### under the hood
*副詞句* — 内部では、裏側では

> They're often decoder-based under the hood, but trained or prompted to use structured reasoning chains, planning traces, or tool-augmented reflection.
> —— *AI Agents: The Definitive Guide*

ユーザーからは見えない実装の内部動作を指す比喩表現。技術文書で頻出。

### unit tests
*名詞句* — 単体テスト

> Therefore, the init function in this example complicates writing unit tests.
> —— *100 Go Mistakes and How to Avoid Them*

関数やクラスなど最小単位の動作を個別に検証するテスト。

### up front
*副詞句* — 前もって、事前に

> If you do choose to just load all resources up front, you can take advantage of prompt caching in most popular models.
> —— *AI Agents with MCP*

作業や処理の開始前にあらかじめ済ませておくことを表す。

### use cases
*名詞句* — ユースケース、利用場面

> Since then, many organizations have adopted the language to support various use cases: APIs, automation, databases, CLIs (command-line interfaces), and so on.
> —— *100 Go Mistakes and How to Avoid Them*

実際にその機能・技術が使われる具体的な状況・目的。

### vector database
*名詞句* — ベクトルデータベース

> In agentic loops, moving data between a neocloud GPU and a hyperscale vector database sometimes costs more than the inference step itself.
> —— *AI Agents: The Definitive Guide*

埋め込みベクトルを保存し類似検索を行うためのデータベース。

### vice versa
*副詞句* — 逆もまた同様

> As of the 2026-07-28 spec, only clients can initiate requests to servers, and not vice versa.
> —— *AI Agents with MCP*

“and not vice versa”の形で、直前で述べた関係が逆方向にも成り立つことを一言で示す。フォーマルな文章でよく使う。

### virtual machine
*名詞句* — 仮想マシン

> Each sandbox is effectively a lightweight virtual machine dedicated to a single execution context.
> —— *AI Agents: The Definitive Guide*

ハードウェアを仮想化しOS単位で分離実行する環境。

### wait until
*動詞句* — ~まで待つ

> Let's wait until we are about to write boilerplate code to consider using generics.
> —— *100 Go Mistakes and How to Avoid Them*

ある条件・時点に達するまで処理や判断を保留することを表す。

### widely adopted
*形容詞句* — 広く採用されている

> Since then, the later steps in the training process were widely adopted to lead to a model that requires less prompt engineering and behaves more in line with how people (and agent scaffolds) expect it to behave.
> —— *An Illustrated Guide to AI Agents*

多くの組織・開発者に採用され普及していることを表す。

### widely used
*形容詞句* — 広く使われている

> This technique is probably less widely used than build tags, but it's worth knowing about because it presents some advantages, as we discussed.
> —— *100 Go Mistakes and How to Avoid Them*

widely adoptedと近いが、より一般的な「使用されている」ことを指す。

## 談話表現（読解・リスニング）（101項目）

文章・説明の流れを作る接続表現・談話標識。読解時に論理構造を掴む手がかりになる。

> **[中] キュレーション注記**: 本カテゴリの項目選定は、コーパス頻度（doc_freq・log_dice）だけでは機械的に判定できない部分を含む。「談話標識として機能するか」はワーカー（人間相当のsonnetサブエージェント）による意味的判断であり、頻度データからの直接測定はできない。例文はsentences.jsonlからの逐語引用で検証済みだが、カテゴリ分類そのものの妥当性は確度[中]として扱う。

### after this
*時間関係* — この後は／これ以降は

> Writing a book might be one of the hardest things I've undertaken in my life, so much so that I think I'm going to take a vow of silence for a while after this.
> —— *AI Agents with MCP*

直前に述べた出来事に続く時間関係を示す。文中・文末でも使われる。

### along the way
*時間関係* — その過程で／途中で

> Once you've committed to building an application with foundation models, evaluation will be an integral part of every step along the way.
> —— *AI Engineering*

プロセスの進行中に起こる付随的な事柄を示す際に使う。

### as a consequence
*因果* — その結果として

> As a consequence, the protocols in the OSI model are better hidden than in the TCP/IP model and can be replaced relatively easily as the technology changes.
> —— *Computer Networks, Fifth Edition*

as a resultよりやや硬い言い方で、前文の直接的な帰結を導入する。

### as a result
*因果* — その結果

> As a result, encoder-only transformers remain central to modern AI systems, quietly powering the understanding layer beneath today's most advanced agentic systems.
> —— *AI Agents: The Definitive Guide*

前文の原因・条件から生じた結果を導入する最も基本的な因果表現。

### as a rule
*一般化* — 経験則として／原則として

> As a rule of thumb, KV cache memory grows with sequence length × layers × KV heads × head dimension × 2 × precision in bytes.
> —— *AI Agents: The Definitive Guide*

as a rule of thumbの形で使われることが多く、目安・経験則を提示する前置き。

### as a whole
*総括* — 全体として

> Each agent can be designed as a domain expert, which boosts the system's performance as a whole.
> —— *AI Agents: The Definitive Guide*

個別要素ではなく対象全体を指して総括する際に使う。

### as always
*前置き* — いつものように

> As always, these can be found in the notebook on the associated GitHub repository.
> —— *An Illustrated Guide to AI Agents*

読者の既存の期待・慣習に沿うことを示す前置き表現。

### as before
*参照・比較* — 以前と同様に

> As before, I omit the rest of the code for the other nodes for brevity, but you can find the complete implementation in the book's repository.
> —— *AI Agents: The Definitive Guide*

既出の状況・方法を踏襲することを示す。

### as discussed
*参照* — 既に述べたように

> For genuinely untrusted code, nest it inside a stronger isolation tier, as discussed in Table 6-4.
> —— *AI Agents: The Definitive Guide*

前出の議論・図表を参照する際に使う。

### as expected
*評価* — 予想通り

> This helps you understand whether the system behaves as expected and produces useful results.
> —— *AI Agents: The Definitive Guide*

結果が事前の予測と一致したことを示す評価表現。

### as follows
*例示・列挙導入* — 次の通り

> Although there are different implementations with minor variations, the main idea is as follows:
> —— *100 Go Mistakes and How to Avoid Them*

直後に箇条書きや詳細な説明が続くことを予告する。

### as illustrated
*参照・例示* — 図示されているように

> This can include a short handoff phrase that signals the budget boundary, as illustrated in Example 4-3.
> —— *AI Agents: The Definitive Guide*

図表・例で示された内容を参照する。

### as mentioned
*参照* — 前述の通り

> As mentioned in Chapter 1, a model's training process is often divided into pre-training and post-training.
> —— *AI Engineering*

既出の内容を簡潔に呼び戻す際に使う汎用的な参照表現。

### as mentioned earlier
*参照* — 前に述べた通り

> As mentioned earlier, the MCPServer API automatically infers input and output schemas from the tool's function signature.
> —— *AI Agents with MCP*

as mentionedよりも時間的に前の言及であることを明確に示す。

### as noted
*参照* — 指摘した通り

> As noted in "The Direct Access Pattern", organizational accounts typically allow platform teams to configure rate limits and cost thresholds for individual team accounts.
> —— *Building AI Agent Platforms*

既に指摘・注記した内容を引き合いに出す。

### as opposed to
*対比* — 〜とは対照的に

> Note that this section focuses on evaluating open-ended responses (arbitrary text generation) as opposed to close-ended responses (such as classification).
> —— *AI Engineering*

二者を明確に対比させる際に使う、ややフォーマルな表現。

### as shown
*参照・例示* — 示されているように

> Now, to give the LLM access to the tool, you just bind the tools to the LLM as shown in Example 1-3.
> —— *AI Agents: The Definitive Guide*

図・例で示された内容への参照。

### as such
*結論* — それゆえ／そのようなものとして

> As such, we consider the following definition of AI agents meaningful through both the fundamentals and new advances in this field:
> —— *An Illustrated Guide to AI Agents*

直前の内容を受けて結論を導く。文脈により「それ自体としては」の意味にもなる。

### as usual
*前置き* — いつも通り

> After wiring the tools, you instantiate the LangGraph agent as usual and prompt the agent to search for data and plot the results inside the sandbox.
> —— *AI Agents: The Definitive Guide*

通常のやり方・慣例に従うことを示す。

### as we saw
*参照* — 見てきたように

> As we saw in Chapter 1, the LLM powers agents to go from observations to actions.
> —— *An Illustrated Guide to AI Agents*

既出の内容を読者と共に振り返る参照表現。

### as we will
*予告・時間関係* — これから見るように

> Networks come in many sizes, shapes and forms, as we will see later.
> —— *Computer Networks, Fifth Edition*

これから述べる内容を予告する（"as we will see"の形が多い）。

### as with
*比較* — 〜と同様に

> As with general hiring, you preselect here based on the capabilities and overall fit of the model for its final role in your agent system.
> —— *AI Agents: The Definitive Guide*

既知の事例と類似点があることを示して導入する。

### at this point
*時間関係* — この時点で

> At this point, your agent has the essential components for self improvement.
> —— *AI Agents: The Definitive Guide*

議論・プロセスの現在地点を示す。

### by definition
*定義補足* — 定義上

> We mentioned in the previous section that an empty slice has, by definition, a length of zero.
> —— *100 Go Mistakes and How to Avoid Them*

用語・概念の定義から自明に導かれることを補足する。

### either way
*結論* — どちらにしても

> Either way, this state also identifies tenants that could be candidates for additional outreach.
> —— *Building Multi-Tenant SaaS Architectures*

直前に示した2つの選択肢のいずれであっても結論が変わらないことを示す。

### even if
*譲歩* — たとえ〜でも

> Their autonomy is orchestrated rather than self-evolving, decisions happen within a framework of predefined states, transitions, and toolsets, even if the agent can adaptively choose among them at runtime.
> —— *AI Agents: The Definitive Guide*

仮定的な条件下でも結論が変わらないことを示す譲歩表現。

### even though
*譲歩* — 〜にもかかわらず

> This clearly shows that the agent successfully learned how to solve the countdown tasks, even though I just used a small split of the dataset.
> —— *AI Agents: The Definitive Guide*

事実として成立している逆接的条件を示す（even ifより事実性が高い）。

### first and foremost
*結論・強調* — まず何よりも

> First and foremost, FinOps is a cultural change that focuses on breaking down the silos between teams that historically haven't worked closely together.
> —— *Cloud FinOps, 2nd Edition*

最も重要な点を最初に提示する際の強い前置き。

### following this
*時間関係* — これに続いて

> Following this metaphor, that is what a platform should strive for.
> —— *Building AI Agent Platforms*

直前の内容を受けて次の展開に進むことを示す。

### for example
*例示* — 例えば

> For example, in pure reinforcement learning, agents can be trained directly through trial-and-error interaction with an environment.
> —— *AI Agents: The Definitive Guide*

最も一般的な具体例の導入表現。

### for instance
*例示* — 例えば

> For instance, what output from the outline generation state triggers the drafting state.
> —— *AI Agents: The Definitive Guide*

for exampleとほぼ同義でよりフォーマルな響きを持つ。

### for this purpose
*目的* — この目的のために

> Again, existing distributed tracing solutions from IDPs can be leveraged for this purpose.
> —— *Building AI Agent Platforms*

直前で述べた目的を受けて手段を示す。

### for this reason
*因果* — この理由で

> For this reason, the loop includes a short wrap-up instruction that forces a final assistant message if the run reaches the step limit after a tool observation.
> —— *AI Agents: The Definitive Guide*

直前に述べた理由を受けて結論・帰結を導く。

### given that
*条件・因果* — 〜であることを踏まえると

> Given that this function isn't performance sensitive, it was decided to favor the easiest option to read.
> —— *100 Go Mistakes and How to Avoid Them*

前提条件を明示してから結論を述べる。

### important to note
*補足・強調* — 注意すべき重要な点として

> It's important to note that completions are predictions, based on probabilities, and not guaranteed to be correct.
> —— *AI Engineering*

誤解されやすい点や見落としがちな点を強調する定番表現（it's important to note thatの形）。

### in a way
*言い換え* — ある意味では

> The agent follows instructions, selects tools, and updates memory, but does so in a way that leads to unintended outcomes.
> —— *AI Agents: The Definitive Guide*

断定を和らげたり、限定的な視点を示す際に使う。

### in addition
*追加* — 加えて

> In addition, the moment you need facts from outside training data, or you want the model to act (search, compute), you introduce tools.
> —— *AI Agents: The Definitive Guide*

前文の内容に情報を追加する基本的な表現。

### in any case
*結論* — いずれにせよ

> In any case, regulatory constraints and the need to avoid interference usually dictate the choice of frequencies.
> —— *Computer Networks, Fifth Edition*

前述の複数の可能性に関わらず成り立つ結論を示す。

### in comparison
*比較* — 比較すると

> It jumps off the page, especially in comparison to Figure 3-18.
> —— *Communicating with Data*

他の対象と比べた際の相対的な特徴を述べる。

### in contrast
*対比* — それとは対照的に

> In contrast, other goroutines will receive updates and print a message whenever a specific goal is reached (listener goroutines).
> —— *100 Go Mistakes and How to Avoid Them*

前文と明確に異なる性質・結果を提示する。

### in either case
*条件* — どちらの場合でも

> In either case, the domain still typically ends up playing some role in identifying the tenant that is accessing your system.
> —— *Building Multi-Tenant SaaS Architectures*

直前に述べた2つの場合いずれにも当てはまることを示す。

### in essence
*言い換え* — 要するに／本質的には

> In essence, a masked language model is trained to be able to fill in the blank.
> —— *AI Engineering*

複雑な説明を簡潔に言い換える際に使う。

### in fact
*強調* — 実際

> In fact, the use of verifiers resulted in approximately the same performance boost as a 30× model size increase.
> —— *AI Engineering*

前文の内容をさらに強調・補強する事実を提示する。

### in general
*一般化* — 一般的に

> In general, your hard checks should do as much of the work as possible.
> —— *AI Agents: The Definitive Guide*

個別事例ではなく全体的な傾向を述べる際の前置き。

### in many cases
*一般化* — 多くの場合

> Having humans in the loop for sanity checks is always helpful, and in many cases, human evaluation is essential.
> —— *AI Engineering*

例外を認めつつ大部分に当てはまることを示す。

### in most cases
*一般化* — ほとんどの場合

> In most cases, you will work with a curated subset rather than the full dataset.
> —— *AI Agents: The Definitive Guide*

in many casesよりやや強い一般化。

### in other words
*言い換え* — 言い換えれば

> In other words, your goal is to get the model to predict what comes next in the training data.
> —— *AI Engineering*

直前の内容を分かりやすく言い換える際の代表的な表現。

### in particular
*強調・例示* — 特に

> In particular, you will learn how to monitor agent behavior, trace system execution, and identify weaknesses or unexpected behaviors during development and after deployment.
> —— *AI Agents: The Definitive Guide*

一般的な内容の中から特定の点を取り上げて強調する。

### in practice
*対比* — 実際には

> In practice, nearly all real-world systems fall into the middle: they are agentic systems, not truly autonomous agents.
> —— *AI Agents: The Definitive Guide*

理論・建前と対比して現実の状況を述べる。

### in principle
*対比* — 原則として

> In principle, almost any software that you can self-host could also be provided as a cloud service,
> —— *Designing Data-Intensive Applications, 2nd Edition*

理屈の上では成り立つことを述べ、実際との対比を暗示する。

### in reality
*対比* — 実際には

> In reality, each new agent, tool, or provider adds another special case.
> —— *AI Agents: The Definitive Guide*

想定・理論と対比して現実を述べる。

### in relation to
*関連* — 〜との関連で

> The executive team sets the company's KPIs, which are important measures that, taken together, form a picture of how the company is performing in relation to its goals.
> —— *Communicating with Data*

二つの事柄の関係性を明示する。

### in short
*結論* — 要するに

> In short, this chapter will help you design the emergence of agency for your agents.
> —— *AI Agents: The Definitive Guide*

議論を簡潔にまとめる際の結論表現。

### in some cases
*条件* — 場合によっては

> These agents are used to do deep research on a topic, making use of memory, tools like web search, and in some cases, additional autonomous agents to pursue various avenues of research.
> —— *AI Agents with MCP*

一部の状況にのみ当てはまることを示す限定表現。

### in summary
*結論* — まとめると

> In summary, three numbers signal a model's scale:
> —— *AI Engineering*

議論全体を要約する際の代表的な結論表現。

### in that case
*条件* — その場合は

> In that case, you want the model to run the code in a minimal, capability-scoped interpreter embedded in the agent.
> —— *AI Agents: The Definitive Guide*

直前に述べた特定の条件が成立した場合の対応を示す。

### in the end
*結論* — 結局のところ

> What matters in the end isn't the number of mistakes we make, but our capacity to learn from them.
> —— *100 Go Mistakes and How to Avoid Them*

一連の議論の最終的な結論を述べる。

### in the meantime
*時間関係* — それまでの間

> I cover exception handling fully in Chapter 7, but in the meantime you will occasionally need to declare methods that can throw exceptions.
> —— *Core Java, Vol. I: Fundamentals, 14th Edition*

別の出来事が起こるまでの間の状況を示す。

### in theory
*対比* — 理論上は

> Due to its RNN nature, in theory, it doesn't have the same context length limitation that transformer-based models have.
> —— *AI Engineering*

実際とは異なる可能性を暗示しつつ理屈上の話をする。

### in this case
*条件* — この場合は

> In this case, the "roles" are workflow stages rather than independent agents.
> —— *AI Agents: The Definitive Guide*

直前に示した特定の状況に限定して述べる。

### in this context
*文脈限定* — この文脈では

> In this context, the LLM can be seen as part of a function to optimize.
> —— *An Illustrated Guide to AI Agents*

議論の前提となる文脈・状況を明示して限定する。

### in this regard
*関連* — この点に関して

> Knowledge in this regard has two components: subject-matter expertise and data skills.
> —— *Communicating with Data*

直前の話題を受けてその観点から補足する。

### in this way
*言い換え* — このようにして

> In this way, for any number M of LLMs, you just write N connectors, transforming the MxN problem into M+N.
> —— *AI Agents with MCP*

直前で述べた方法・手段を受けてその帰結を示す。

### in turn
*因果* — 今度は／それに伴って

> Foundation models emerged from large language models, which, in turn, originated as just language models.
> —— *AI Engineering*

連鎖的な因果関係・順序を示す。

### it is worth
*補足・強調* — 〜する価値がある

> It is worth noting that the opposite can be true as well.
> —— *Cloud FinOps, 2nd Edition*

it is worth noting/bearing in mindなどの形で重要な補足を導入する。

### it turns out
*結果・発見* — 実際には〜であることが分かる

> It turns out that tokenization can be much more efficient for some languages than others.
> —— *AI Engineering*

予想に反した、あるいは調査の結果判明した事実を導入する。

### just as
*比較* — ちょうど〜のように

> Just as individual skills eventually meet their limits, a single agent can only take a workflow so far before complexity demands coordination.
> —— *AI Agents: The Definitive Guide*

類似した状況を並べて論を展開する際の比較表現。

### just like
*比較* — 〜と同じように

> Just like The Hitchhiker's Guide to the Galaxy advises not to panic, I'll say the same here in my guide.
> —— *AI Agents: The Definitive Guide*

just asと同様、類似の事例を挙げて説明を導入する。

### keep in mind
*補足* — 心に留めておくこと

> Keep in mind that real agent failures rarely occur in calm, perfectly structured interactions.
> —— *AI Agents: The Definitive Guide*

読者に注意喚起する定番のフレーズ。

### last but
*結論・列挙* — 最後になるが（重要な点として）

> Last but not least, the scope of evaluation has expanded for general-purpose models.
> —— *AI Engineering*

通常"last but not least"の形で使われ、列挙の最後の項目が軽視されるべきではないことを示す。

### more importantly
*強調* — さらに重要なことに

> More importantly, you need to establish a policy and budget for monitoring, maintaining, and updating your model.
> —— *AI Engineering*

直前の内容よりも重要な点を追加する。

### more specifically
*詳細化* — より具体的には

> More specifically, it's the chat history of the LLM that is continuously fed back to the LLM.
> —— *An Illustrated Guide to AI Agents*

直前の一般的な説明を具体化・詳細化する。

### most importantly
*強調* — 最も重要なことに

> Most importantly, they give models the ability to directly interact with the world, enabling them to automate many aspects of our lives.
> —— *AI Engineering*

複数の論点の中で最重要のものを提示する。

### moving on to
*時間関係* — 次に移って

> development is done hand-in-hand with testing, allowing individual behaviors to be fully tested and validated on their own before moving on to the next one.
> —— *AI Agents with MCP*

話題やステップを次に進める際の移行表現。

### much like
*比較* — 〜とほとんど同じように

> Each step or branch in the reasoning process can be evaluated and compared, much like a human reviewing a line of argument or debugging code.
> —— *AI Agents: The Definitive Guide*

類似のたとえを挙げて説明を補強する。

### not only
*追加* — 〜だけでなく

> It will empower you to not only understand the concepts but to apply them effectively as you learn about more complex topics later in the book.
> —— *AI Agents: The Definitive Guide*

not only X but also Yの相関構文で範囲を拡張する。

### note that
*補足* — 〜に注意

> Note that I focus on the key code snippets here and omit helper functions or minor sections to highlight the core logic.
> —— *AI Agents: The Definitive Guide*

見落としやすい前提・注意点を読者に伝える。

### notice that
*補足* — 〜に気づくだろう

> You'll also notice that much of what you've learned so far comes together here.
> —— *AI Agents: The Definitive Guide*

note thatと似るが、読者自身が気づくという視点で述べる。

### on average
*一般化* — 平均して

> A LinkedIn survey from August 2023 shows that the number of professionals adding terms like "Generative AI," "ChatGPT," "Prompt Engineering," and "Prompt Crafting" to their profile increased on average 75% each month.
> —— *AI Engineering*

統計的な傾向・平均値を述べる際の表現。

### on top of
*追加* — それに加えて

> But on top of that, you have additional tools, such as MCP Inspector (which we've been using throughout the server chapters) which
> —— *AI Agents with MCP*

on top of thatの形で、既にある事柄にさらに追加することを示す。

### one way
*例示・列挙* — 一つの方法として

> One way to measure the amount of compute needed is by considering the number of machines, e.g., GPUs, CPUs, and TPUs.
> —— *AI Engineering*

複数ある方法のうち一つを提示する導入表現（"another way"と対で使われることが多い）。

### recall that
*参照* — 〜を思い出してほしい

> Recall that a softmax layer is used to compute the probability distribution over all possible values.
> —— *AI Engineering*

既出の知識を読者に想起させる。

### similarly to
*比較* — 〜と同様に

> You'll see how to use this in "Deep Agents: Planning Before Execution" for deep agents, which operate similarly to Claude Code and Manus.
> —— *AI Agents: The Definitive Guide*

既知の対象と類似点を示して説明を導入する。

### so far
*時間関係* — これまでのところ

> What's the rationale for breaking the rule we've discussed so far?
> —— *100 Go Mistakes and How to Avoid Them*

これまでの議論・進捗を振り返る際に使う。

### such as
*例示* — 〜のような

> Then comes action, such as searching for documentation, writing functions, or debugging errors.
> —— *AI Agents: The Definitive Guide*

具体例を列挙して直前の一般的な概念を補足する。

### that is
*言い換え* — すなわち

> That is, the ReAct agent alternates between reasoning traces and tool outputs, and those traces feed back into context.
> —— *AI Agents: The Definitive Guide*

直前の内容をより正確・具体的に言い換える。

### that said
*譲歩* — とはいえ

> That said, every concept will be grounded in code, so your knowledge becomes usable again without requiring you to dust off old textbooks.
> —— *AI Agents: The Definitive Guide*

直前の内容を認めた上で、それに対する留保・逆接を導入する。

### that way
*結果* — そうすることで

> That way, the answer is more difficult to score programmatically or using an exact match and instead requires a judge.
> —— *An Illustrated Guide to AI Agents*

直前の方法・行動がもたらす結果を示す（文頭で使う場合に談話標識として機能）。

### these days
*時間関係* — 近頃は

> Truly, with the capabilities of agents these days, it all boils down to iteratively calling an LLM until it decides to stop the loop.
> —— *An Illustrated Guide to AI Agents*

現在の状況を過去と対比しながら述べる際に使われることが多い。

### this means
*言い換え* — これはつまり〜ということだ

> This means that to support M models and N tools, agent developers had to write MxN connectors.
> —— *AI Agents with MCP*

直前の事実から導かれる意味・帰結を説明する。

### to be clear
*明確化* — はっきり言うと

> To be clear, routing and fallback strategies are vital architectural patterns when developing AI applications.
> —— *Building AI Agent Platforms*

誤解を避けるために主張を明確にする際の前置き。

### to clarify
*明確化* — 明確にすると

> It's also important to clarify the role of humans in the application.
> —— *AI Engineering*

曖昧になりがちな点を明らかにする際に使う。

### to illustrate
*例示* — 説明のために

> To illustrate, the next example uses the open source TreeQuest library to refine Python code for the Fibonacci sequence.
> —— *AI Agents: The Definitive Guide*

具体例を通して直前の説明を裏付ける。

### to summarize
*結論* — まとめると

> To summarize, the slice length is the number of available elements in the slice, whereas the slice capacity is the number of elements in the backing array.
> —— *100 Go Mistakes and How to Avoid Them*

議論全体を簡潔にまとめる際の結論表現。

### when it comes
*話題導入* — 〜のこととなると

> Let's first go into what exactly open source means when it comes to models, then discuss the pros and cons of these two approaches.
> —— *AI Engineering*

特定の話題・観点に絞って議論を導入する（多くは"when it comes to"の形）。

### which means
*言い換え* — つまり〜ということだ

> Encoder-only architectures remove the decoder stack entirely and rely on bidirectional attention, which means every token can attend to every other token in the sequence.
> —— *AI Agents: The Definitive Guide*

直前の事実がもたらす意味を非制限的関係節で説明する。

### while this
*譲歩* — 〜ではあるが

> While this example is in the context of a single agent, the same structure extends naturally into larger MAS.
> —— *AI Agents: The Definitive Guide*

一部の限定を認めた上で、それでも成り立つ一般的な主張を導入する譲歩表現。

### with respect to
*関連* — 〜に関して

> By looking at your FinOps practice through a variety of lenses, you can assess the strengths of each with respect to your broader organization as well as specific target groups within it.
> —— *Cloud FinOps, 2nd Edition*

特定の観点・基準を明示して論じる際に使う。

### with this
*参照・因果* — これによって

> With this small implementation, you now see exactly what the graph remembers, how it routed, and what the latest assistant state is for each branch.
> —— *AI Agents: The Definitive Guide*

直前に述べた内容・手段を受けて、その結果や次の展開を導入する。

### worth mentioning
*補足* — 言及する価値がある

> One further point worth mentioning here is that what it means to be on the Internet is changing.
> —— *Computer Networks, Fifth Edition*

追加の重要な情報を控えめに提示する際に使う。

### worth noting
*補足・強調* — 注目に値する

> On the topic of model performance given a compute budget, it's worth noting that the cost of achieving a given model performance is decreasing.
> —— *AI Engineering*

it's worth noting thatの形で、重要だが見落とされがちな点を補足する。

## スピーキング定型（90項目）

会話・発表で自分の考えを述べる際に使える定型フレーズ。

> **[中] キュレーション注記**: 本カテゴリはコーパス頻度から「話し言葉の定型表現か」を直接測定できないため、選定はワーカーによるキュレーション判断に依存する。例文自体はsentences.jsonlからの逐語引用で検証済みだが、「スピーキングで使える定型句」という分類の妥当性は確度[中]として扱う。

### another way to
*提案・意見* — 別の方法としては

> Next, let's look at another way to categorize tests: short mode.
> —— *100 Go Mistakes and How to Avoid Them*

one way toに続けて代案を出す際に使う表現。

### arguably the
*意見表明・強調* — 間違いなく〜と言える(最上級を伴うことが多い)

> Arguably, the smallest evaluation unit is a single LLM completion or a retrieval query against a vector store.
> —— *Building AI Agent Platforms*

断定を避けつつ強い主張をする際のヘッジ表現。arguably the bestのように最上級と共に使われることが多い。

### as an example
*例示* — 一例として

> As an example, if a model is trained to classify whether an email is spam or not, there are only two possible outcomes: spam and not spam.
> —— *AI Engineering*

文末や文頭に置いて具体例を示す表現。プレゼンのスライド説明でも使える。

### as shown in
*参照・指示* — 〜に示されている通り

> Now, to give the LLM access to the tool, you just bind the tools to the LLM as shown in Example 1-3.
> —— *AI Agents: The Definitive Guide*

図表やスライドを指し示す際の表現。プレゼンで資料を参照する時に使う。

### as we discussed
*参照・振り返り* — 先ほど議論したように

> As we discussed, interfaces are made to create abstractions.
> —— *100 Go Mistakes and How to Avoid Them*

会議やレビューで以前の議論内容を引用する際に使う。

### as we mentioned
*参照・振り返り* — 先ほど触れたように

> As we mentioned in Chapter 4, this could be anything from unblended costs or amortized costs or fully loaded costs.
> —— *Cloud FinOps, 2nd Edition*

as we discussedより軽く言及した内容を指す。

### at a glance
*比喩・要約* — 一目で、ぱっと見て

> They help you understand, at a glance, how your system is doing.
> —— *AI Engineering*

at first glanceと似るが、こちらは概観するというニュアンスでダッシュボードや図の説明に使われる。

### at first glance
*比喩・感想* — 一見すると

> At first glance, a stronger judge makes sense.
> —— *AI Engineering*

第一印象を述べたあとに、実は違うという展開へつなげる際によく使われる。

### at this stage
*時間関係* — この段階では

> At this stage, dataset management becomes a collaborative effort involving a broader audience beyond the engineering team.
> —— *Building AI Agent Platforms*

at this pointと近いが、プロセスの段階に焦点を当てる表現。

### before we can
*提案・前置き* — 〜できるようになる前に

> Before we can dig into defining SaaS, we need to understand where this journey started and the factors that have driven the momentum of the SaaS delivery model.
> —— *Building Multi-Tenant SaaS Architectures*

前提条件を先に説明する必要がある時に使う表現。

### before we dive
*提案・前置き* — 深く掘り下げる前に

> Before we dive more deeply into these topics, let's go over some important terminology, depicted in Figure 2-10.
> —— *Communicating with Data*

let's dive intoと対になる前置き表現。詳細な説明に入る前に使う。

### before we get
*提案・前置き* — 〜に入る前に

> But before we get into those details, we need to align on what exactly an agent even is.
> —— *Agent Memory*

before we startと同系統で、特定の話題に入る前の前置きに使う。

### before we start
*提案・前置き* — 始める前に

> Before we start making things more efficient, we need to understand how efficiency is measured.
> —— *AI Engineering*

本題に入る前の前置きとして使う表現。

### break down
*提案・説明* — 分解する、噛み砕いて説明する

> The orchestrator-worker workflow uses one LLM to break down a task, calls worker LLMs to work on the smaller tasks, and finally calls an aggregator LLM to put the results together.
> —— *AI Agents with MCP*

複雑な内容を要素ごとに分けて説明する動詞句。'Let's break down...'の形で導入にも使われる。

### by the end
*時間関係* — 〜の終わりまでには

> By the end, you'll know how to staff your team, assign the right tasks, and optimize for both performance and spend.
> —— *AI Agents: The Definitive Guide*

プレゼンや説明の到達目標を示す際の定番表現(By the end of this talk...)。

### by the time
*時間関係* — 〜する頃には

> By the time something looks wrong, the impact radius may already be significant.
> —— *AI Agents: The Definitive Guide*

時間的な前後関係を示す表現。進捗報告や見通しを語る際に使いやすい。

### feel free to
*提案・依頼* — 遠慮なく〜してください

> If you're primarily focused on building agents, feel free to proceed to the next chapter after reading Part 1 - you'll have everything you need.
> —— *An Illustrated Guide to AI Agents*

相手に行動を促す柔らかい許可表現。Q&Aや依頼の場面で多用。

### for sure
*強調・カジュアル* — 確実に、間違いなく

> We can't say this for sure because it's impossible to comb through the training data to verify whether it contains an idea.
> —— *AI Engineering*

of courseやno doubtよりカジュアルな口語表現。

### i believe
*意見表明* — 私は〜だと考えます

> However, in SaaS environments, I believe that successful teams are better off when they adopt a broader view of the scope of their operational model.
> —— *Building Multi-Tenant SaaS Architectures*

i thinkよりやや確信度が高く、フォーマルな場面にも使える。

### i mean
*意見表明・言い換え* — つまり、というのは

> Anyone, and I mean anyone, can now develop AI applications.
> —— *AI Engineering*

発言を補足・言い換える際のつなぎ言葉。カジュアルな口頭表現で頻出。

### i think
*意見表明* — 私は〜だと思います

> I think of agents as dynamic, collaborative systems rather than isolated components.
> —— *AI Agents: The Definitive Guide*

最も基本的な意見表明。断定を避けやわらかく主張する。

### i want to
*意見表明・提案* — 〜したいと思います

> I want to give you a blueprint for building LLM agents that are robust, reliable, and adaptable.
> —— *AI Agents: The Definitive Guide*

自分がこれから話す内容や意図を宣言する表現。プレゼンの冒頭にも使える。

### imagine that
*仮定・例示* — 〜だと想像してください

> Imagine that we have a model that has only two possible outputs: A and B.
> —— *AI Engineering*

聴衆に具体的な情景を思い描かせる導入表現。

### important thing to
*強調* — 重要なことは〜すること

> The important thing to note is to start thinking about what it means to have standardization, why it's required, and with what common methodologies it can be achieved.
> —— *An Illustrated Guide to AI Agents*

the important thing to note/rememberなどの形で使われ、要点を明示する。

### it's important to
*強調* — 〜することが重要です

> However, it's important to know that this chapter isn't meant as an introduction to the transformer architectures or to parameter-efficient fine-tuning (PEFT) methods.
> —— *AI Agents: The Definitive Guide*

important to noteより一般的で、行動や理解の重要性を述べる際に使う。

### it's worth noting
*強調* — 特筆すべき点として

> It's worth noting that this move to shared infrastructure also introduces a range of new challenges.
> —— *Building Multi-Tenant SaaS Architectures*

worth noting thatの主語付き完全形。プレゼンや説明の合間の強調に使いやすい。

### just want to
*意見表明・前置き* — ちょっと〜したいだけなのですが

> If you just want to learn and have fun, jump right in.
> —— *AI Engineering*

控えめに要望や補足を切り出す表現。i want toよりカジュアルで柔らかい。

### key takeaway
*要約・要点提示* — 重要な学び、要点

> The key takeaway is that you'll need to give careful consideration to determining how and where identity fits into your environment.
> —— *Building Multi-Tenant SaaS Architectures*

説明やプレゼンの締めくくりで要点をまとめる際に使う。

### let us
*提案・フォーマル* — 〜しましょう

> Let us take a quick look at some possibilities.
> —— *Computer Networks, Fifth Edition*

let'sのフォーマル版。講演やドキュメント調の話し方でやや硬めの印象を与える。

### let's assume that
*仮定・例示* — 〜と仮定しましょう

> For now, let's assume that you have a way to transform texts into embeddings.
> —— *AI Engineering*

議論を進めるための前提条件を置く時の定番。技術的な説明で頻出。

### let's consider
*提案* — 〜を考えてみましょう

> First, let's consider the following interface, which contains a method to get the coordinates from a given address:
> —— *100 Go Mistakes and How to Avoid Them*

let's think aboutよりやや形式的。具体例や前提を提示する前置きとして使う。

### let's define
*提案* — 〜を定義しましょう

> Now that you've developed your criteria and scoring rubrics, let's define what methods and data you want to use to evaluate your application.
> —— *AI Engineering*

用語や基準をはっきりさせる際の導入句。議論の前提をそろえる時に有効。

### let's discuss
*提案* — 〜について議論しましょう

> Let's discuss a few common uses where generics are recommended:
> —— *100 Go Mistakes and How to Avoid Them*

話し合いの開始を明示する表現。会議で使いやすい。

### let's dive into
*提案* — 〜に深く入っていきましょう

> Let's dive into a few specific cases to show the importance of live updates:
> —— *Communicating with Data*

本格的な説明・詳細な議論に入る合図。ややカジュアルだが技術系のトークでよく使われる。

### let's examine
*提案* — 〜を検討してみましょう

> Now, let's examine concrete cases where we should and shouldn't use generics.
> —— *100 Go Mistakes and How to Avoid Them*

let's lookよりやや形式的で、詳細に精査するニュアンス。技術レビューに向く。

### let's explore
*提案* — 〜を探ってみましょう

> Next, let's explore the impact of how a model is designed on its performance.
> —— *AI Engineering*

未知の領域やアイデアを掘り下げる際に使う、やや前向きなニュアンスの表現。

### let's go through
*提案* — 〜を順に見ていきましょう

> Let's go through a few examples to make things clearer.
> —— *100 Go Mistakes and How to Avoid Them*

walk throughとほぼ同義。リストや複数項目を一つずつ確認する際に使う。

### let's imagine
*仮定・例示* — 〜を想像してみましょう

> Let's imagine the object store represents a globally managed construct that holds information that is centrally managed for all tenants.
> —— *Building Multi-Tenant SaaS Architectures*

仮想的なシナリオを提示する際の表現。let's assumeより物語的・具体的なニュアンス。

### let's look at
*提案* — 〜を見てみましょう

> First, let's look at an example where using an init function can be considered inappropriate: holding a database connection pool.
> —— *100 Go Mistakes and How to Avoid Them*

資料・コード・図などに注意を向けさせる際の定番。プレゼンでスライドを指すときにも使う。

### let's move on
*話題転換* — 次に進みましょう

> Now that we've covered two key modeling decisions - architecture and scale - let's move on to the next critical set of design choices: how to align models with human preferences.
> —— *AI Engineering*

現在の話題を切り上げて次の話題へ移る合図。会議やプレゼンの進行でよく使う。

### let's say
*仮定・例示* — たとえば〜としましょう

> Let's say that you've pre-trained a foundation model using self-supervision.
> —— *AI Engineering*

仮の数値や状況を提示する際のカジュアルな定番表現。口頭説明で非常によく使われる。

### let's see
*提案・つなぎ* — 見てみましょう

> Let's see how different models read the same situation.
> —— *AI Agents: The Definitive Guide*

単独でも使えるつなぎ表現。次の行動に移る前のフィラー的用法もある。

### let's see how
*提案* — どのように〜するか見てみましょう

> Let's see how it works with a concrete example.
> —— *100 Go Mistakes and How to Avoid Them*

プロセスや仕組みの説明に入る前の定番導入句。

### let's see what
*提案* — 何が〜か見てみましょう

> Let's see what the receive end looks like:
> —— *AI Agents with MCP*

結果や中身を確認する場面で使う導入句。

### let's start by
*提案・導入* — まず〜することから始めましょう

> Let's start by looking into different kinds of tools a model can use.
> —— *AI Engineering*

let's start withと同義だが後ろに動名詞(-ing)が続く形。手順の最初のステップを示す時に使う。

### let's start with
*提案・導入* — 〜から始めましょう

> To answer these questions, let's start with a concrete example.
> —— *100 Go Mistakes and How to Avoid Them*

話や説明の冒頭で最初の話題・例を導入する際の定番表現。プレゼンや講義で頻出。

### let's talk about
*提案* — 〜について話しましょう

> Before covering informed ignoring within FinOps, let's talk about simply ignoring FinOps.
> —— *Cloud FinOps, 2nd Edition*

新しい話題を切り出す定番表現。ディスカッションの導入に使う。

### let's think about
*提案* — 〜について考えてみましょう

> Now, let's think about what it means to deliver this same application in a multi-tenant SaaS environment.
> —— *Building Multi-Tenant SaaS Architectures*

聴衆に一緒に考えるよう促す表現。問いかけの前に使うと効果的。

### let's try
*提案* — 試してみましょう

> Now, let's try this exercise again with the same function but implemented differently:
> —— *100 Go Mistakes and How to Avoid Them*

実演・実験を促す表現。デモやハンズオンで頻出。

### let's use the
*提案* — 〜を使いましょう

> To make these reasoning steps a bit more explicit, let's use the example we saw at the beginning of this chapter.
> —— *An Illustrated Guide to AI Agents*

既出の例やツールを使って説明を続ける際の表現。

### let's walk through
*提案* — 〜を一緒に順を追って見ていきましょう

> Let's walk through a simple example to examine the effect of temperature on probabilities.
> —— *AI Engineering*

手順やコードを一段階ずつ説明する際の定番。デモやコードレビューで多用。

### looks like
*感想・様子* — 〜のように見える

> Visually, in the figure, it looks like circular dependencies.
> —— *100 Go Mistakes and How to Avoid Them*

視覚的な情報に基づく感想を述べる際の表現。

### make sense to
*確認・同意* — 〜にとって理にかなう

> For businesses in commercial areas, it may make sense to lease a high-speed transmission line from the offices to the nearest ISP.
> —— *Computer Networks, Fifth Edition*

makes senseに前置詞toを伴う形。「〜するのが合理的だ」という判断を述べる際に使う。

### make sure
*確認・依頼* — 必ず〜するようにしてください

> But before delving into most topics, we make sure the foundations are clear.
> —— *100 Go Mistakes and How to Avoid Them*

行動を促す際の定番表現。指示・レビューコメントで頻出。

### make sure that
*確認・依頼* — 〜であることを確認してください

> I've mentioned model adaptation several times in this chapter, so before we move on, I want to make sure that we're on the same page about what model adaptation means.
> —— *AI Engineering*

make sureに接続詞thatを伴う形。認識をすり合わせる際にも使う。

### make sure you
*確認・依頼* — あなたが必ず〜するようにしてください

> Make sure you also account for the correct IAM permissions when mounting, otherwise you'll quickly find yourself debugging access errors instead of shipping.
> —— *AI Agents: The Definitive Guide*

相手に直接行動を促す時の表現。命令文的だが指導・レビューでは自然。

### makes sense
*確認・同意* — 納得できる、理にかなっている

> This parallel highlights why extending pure LLMs with tools makes sense.
> —— *AI Agents: The Definitive Guide*

相手の説明に同意・納得する際の短い相槌としても使われる。

### next step is
*話題転換・手順* — 次のステップは〜です

> Once you have a runnable app and checkpoints in place, the next step is to make its execution observable.
> —— *AI Agents: The Definitive Guide*

手順やロードマップを説明する際の定番表現。

### no doubt
*強調* — 間違いなく

> I have no doubt that these benchmarks will soon become saturated.
> —— *AI Engineering*

確信を強調する表現。文頭・文中どちらにも置ける。

### not necessarily
*意見表明・留保* — 必ずしも〜というわけではない

> Go is simple to learn but not necessarily easy to master.
> —— *100 Go Mistakes and How to Avoid Them*

相手の発言や一般論を穏やかに否定・留保する際の表現。

### now that we
*話題転換* — 〜した今となっては、〜したので

> Now that we have these SaaS mindset basics in place, we can start thinking about how these principles are mapped to more specific architectural patterns and constructs.
> —— *Building Multi-Tenant SaaS Architectures*

前段の内容を踏まえて次の話題に移る際のつなぎ表現。

### now that we've
*話題転換* — 〜し終えた今

> Now that we've updated our MCP client, we need to make sure our agent uses it.
> —— *AI Agents with MCP*

now that weの完了形版。ある作業や説明が終わったことを踏まえて次に進む際に使う。

### of course
*強調・同意* — もちろん

> Of course, it's impossible to be exhaustive, as there will always be edge cases, but this section's goal was to provide guidance to cover most cases.
> —— *100 Go Mistakes and How to Avoid Them*

同意や当然の事実を強調する際の定番表現。

### on the fly
*比喩・様子* — その場で、リアルタイムで

> Once you enforce that boundary, you gain control over execution: you can change your systems settings on the fly, resume from the last stable checkpoint, and avoid rerunning upstream agents.
> —— *AI Agents: The Definitive Guide*

計画せずその都度対応する様子を表す口語的表現。技術トークで頻出。

### one way to
*提案・意見* — 〜する一つの方法として

> One way to measure the amount of compute needed is by considering the number of machines, e.g., GPUs, CPUs, and TPUs.
> —— *AI Engineering*

複数ある解決策の一つを提示する際の柔らかい言い方。断定を避けたい時に有効。

### rule of thumb
*比喩・目安* — 経験則として

> As a rule of thumb, KV cache memory grows with sequence length × layers × KV heads × head dimension × 2 × precision in bytes.
> —— *AI Agents: The Definitive Guide*

厳密ではないが実務上役立つ目安を示す際の定番表現。as a rule of thumbの形で使われることが多い。

### seems like
*感想・様子* — 〜のように思われる

> While this seems like a complex process, it is largely a standard part of properly implementing OAuth in your code.
> —— *AI Agents with MCP*

sounds like/looks likeと同系統で、印象や推測を柔らかく述べる際に使う。

### sounds like
*感想・様子* — 〜のように聞こえる

> Even though this sounds like a simplistic rule, it's important to remember.
> —— *100 Go Mistakes and How to Avoid Them*

相手の発言に対する感想・反応を述べる際の表現。

### suppose that
*仮定・例示* — 〜だとしましょう

> Suppose that the network is down in Germany.
> —— *Computer Networks, Fifth Edition*

let's assumeと同様、仮定の状況を設定する表現。やや数学・論理的な文脈で好まれる。

### suppose we
*仮定・例示* — 私たちが〜だとしましょう

> Suppose we have a SaaS architecture that resembles the model shown in Figure 1-6.
> —— *Building Multi-Tenant SaaS Architectures*

主語を明示した仮定表現。設計議論やホワイトボードでの説明に向く。

### the idea behind
*要点提示* — 〜の背後にある考え方は

> The idea behind contextual retrieval is to augment each chunk with relevant context to make it easier to retrieve the relevant chunks.
> —— *AI Engineering*

設計思想やコンセプトの意図を説明する際に使う。

### the idea is
*要点提示* — 考え方としては、要は

> The idea is that for different questions, different methodologies might be needed to solve them.
> —— *An Illustrated Guide to AI Agents*

アイデアやアプローチの要旨を説明する際の表現。

### the key difference
*要点提示・比較* — 重要な違いは

> The key difference is that while prompt tokens are included in the input context, they are excluded from the loss computation so the model is trained on only the response tokens.
> —— *An Illustrated Guide to AI Agents*

比較を行う際に、最も重要な相違点を示す表現。

### the key idea
*要点提示* — 重要なアイデアは

> The key idea is to use one generation stage to propose multiple potential paths, an evaluation stage to score or select among them, and an execution stage to follow the chosen path.
> —— *AI Agents: The Definitive Guide*

コンセプトや発想の核心を紹介する際に使う。

### the key is
*要点提示* — 重要なのは〜だ

> The key is that whatever you use for your sandbox, MCP tool calls have to get back to the MCP client so that the server can execute them.
> —— *AI Agents with MCP*

話の核心・結論を一言で示す際の定番表現。

### the key to
*要点提示* — 〜の鍵は

> The key to good API design, however, is to think from the user's perspective.
> —— *Building AI Agent Platforms*

成功や理解のための重要な要素を示す表現。

### the point is
*要点提示* — 要するに、ポイントは〜だ

> The point is that the resource no longer belongs to any one consumer; it is a shared infrastructure that is consumed by any tenant of our system.
> —— *Building Multi-Tenant SaaS Architectures*

議論の核心・主張をまとめる際の表現。

### the point of
*要点提示・問いかけ* — 〜の目的・意義は

> What is the point of creating these abstractions?
> —— *100 Go Mistakes and How to Avoid Them*

What's the point of...?のように目的を問う疑問文でもよく使われる。

### to be fair
*譲歩* — 公平に言うと

> To be fair, this does make sense on some level.
> —— *Cloud FinOps, 2nd Edition*

反対意見や批判の前に、相手の立場も認める際に使う譲歩表現。

### to highlight the
*強調* — 〜を強調するために

> These questions aren't meant to criticize these public leaderboards but to highlight the challenge of selecting benchmarks to rank models.
> —— *AI Engineering*

特定のポイントを際立たせたい時に使う表現。

### to note that
*確認・強調* — 〜ということに触れておくと

> It's important to note that there are other types of AI agents in practice that do not utilize LLMs.
> —— *An Illustrated Guide to AI Agents*

important to noteよりやや軽い注意喚起・補足。

### to some extent
*譲歩・留保* — ある程度は

> Remember that your colleagues are probably already working with data to some extent, at different levels of data literacy.
> —— *Communicating with Data*

全面的な同意や否定を避け、部分的に認める際のヘッジ表現。

### to start with
*提案・導入* — まず最初に

> Before looking more closely at adaptive algorithms, it helps to start with two simpler strategies.
> —— *AI Agents: The Definitive Guide*

let's start withと同義だが主語なしでも使える柔軟な導入表現。

### to summarize the
*要約* — 〜をまとめると

> To summarize, the quality of a RAG system should be evaluated both component by component and end to end.
> —— *AI Engineering*

要約に入る際の定番表現。プレゼンの終盤で使われることが多い。

### turns out
*感想・様子* — 実は〜だった、〜ということが判明した

> It turns out that tokenization can be much more efficient for some languages than others.
> —— *AI Engineering*

意外な結果や真相を語る際のカジュアルな導入句。

### we can see
*参照・指示* — 私たちが見て分かるように

> In Figure 2-1, we can see this general workflow.
> —— *An Illustrated Guide to AI Agents*

you can seeより一緒に確認しているニュアンス。デモや共同作業で使いやすい。

### worth considering
*提案・強調* — 検討する価値がある

> However, it is worth considering as you're defining your data partitioning model.
> —— *Building Multi-Tenant SaaS Architectures*

選択肢や代案を提示する際に使う表現。

### worth noting that
*強調* — 〜ということは特筆すべきだ

> It's also worth noting that this book is not trying to include every permutation of SaaS.
> —— *Building Multi-Tenant SaaS Architectures*

worth notingに接続詞thatを伴う完全形。

### you can see
*参照・指示* — ご覧の通り、見て分かるように

> You can see how different OpenAI models tokenize text on the OpenAI website.
> —— *AI Engineering*

画面やスライド、図を指し示しながら説明する際の定番。

### you know
*フィラー・同意確認* — ご存知の通り

> You know by now that AI agents are not magic.
> —— *AI Agents: The Definitive Guide*

相手の理解を前提にした軽い確認・フィラー表現。多用は避けたい。
