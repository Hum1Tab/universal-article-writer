# 論理記事工房：詳細ガイド

> GitHub のランディング README は [`../README.ja.md`](../README.ja.md)。
> このファイルは、運用の詳細・出力契約・トラブルシューティングをまとめた
> リファレンスである。

**どのAIでも使える、証拠と論証に基づく記事執筆プロトコル。**

記事・論文・PDF・URL・メモを読み込み、証拠台帳と論証マップを作ったうえで、
「問い→結論→根拠→反論→限定条件」が通った記事を書きます。

特定のAI、特定のツール、特定のファイル構成に依存しません。
ChatGPT、Claude、Gemini、Copilot、Cursor、Codex、Claude Code、Gemini CLI、OpenCode、
ローカルLLM、API のいずれでも動きます。

> **出典のない断定を書かない。反論のない結論を出さない。未確認を隠さない。**

---

## 1. 何ができるか

- 複数の論文・資料を読み、**主張と証拠の対応**を台帳にする。
- 研究デザイン・バイアス・統計・因果を評価し、**証拠の強さに合った結論**を導く。
- Toulmin モデルで論証を組み、**最強の反論**と**フレーム批判**を検討する。
- 読者の理解順に書き、**段落1仕事（CEAL）** を守る。
- 赤チーム監査で**自分の下書きを壊し**、Critical が0になってから納品する。
- 引用・数値・撤回・未確認を**機械監査**する。実行できない場合は手動で監査する。

対象は、日本語・英語・中国語などの論考、オピニオン、解説記事、文献レビュー、学術エッセイ、政策提言、批判的レビュー、既存原稿の監査、ファクトチェックです。

---

## 2. どのファイルを使うか

| ファイル | 使う場面 | 目安 |
|---|---|---|
| `UNIVERSAL-PROMPT.md` | どのAIでも。ファイル・Web・コード実行がある程度使える | 16kトークン以上 |
| `UNIVERSAL-PROMPT-LITE.md` | 小さい文脈のAI、指示欄の文字数上限が厳しい | 4k〜16kトークン |
| `SKILL.md` | Agent Skills 対応ホスト（Claude Code、Codex、OpenCode など） | ホストの基準 |
| `AGENTS.md` | コーディングエージェント（Codex、Cursor、Copilot など） | リポジトリ常駐 |
| `adapters/` | ChatGPT、Claude、Gemini、コーディングエージェント別の設定手順 | - |

**迷ったら `UNIVERSAL-PROMPT.md`。** 長すぎる場合は `UNIVERSAL-PROMPT-LITE.md`。

---

## 3. 最短の使い方

### チャットAI（ChatGPT、Claude、Gemini など）

1. `UNIVERSAL-PROMPT.md` を開き、全文をコピーする。
2. AI の **system prompt**、**custom instructions**、**project instructions** のいずれかに貼る。
3. 資料を添付し、依頼する。

```text
この論文を読んで、〇〇について論理的な記事を書いてください。
読者は△△、3000字、根拠と反論を含めてください。
```

### コーディングエージェント（Codex、Cursor、Copilot、OpenCode など）

1. `universal-article-writer/` をプロジェクト内に置く。
2. `AGENTS.md` の内容を、エージェントが読む指示ファイルに貼る。
3. 記事作成を依頼する。

### Agent Skills 対応ホスト

1. `universal-article-writer/` をスキルディレクトリにコピーする。
2. `SKILL.md` の `name` が `universal-article-writer` であることを確認する。
3. ホストを再起動し、スキル一覧に出れば成功。

```bash
# Claude Code
mkdir -p .claude/skills
cp -R universal-article-writer .claude/skills/

# Codex / 汎用 Agent Skills
mkdir -p .agents/skills
cp -R universal-article-writer .agents/skills/
```

---

## 4. AI別の設定

| AI | 手順 |
|---|---|
| ChatGPT | [adapters/chatgpt.md](../adapters/chatgpt.md) |
| Claude | [adapters/claude.md](../adapters/claude.md) |
| Gemini | [adapters/gemini.md](../adapters/gemini.md) |
| Codex / Cursor / Copilot / Windsurf / Cline / Roo Code / OpenCode | [adapters/coding-agents.md](../adapters/coding-agents.md) |
| その他のチャットAI・API・ローカルLLM | [adapters/generic-chat.md](../adapters/generic-chat.md) |

### ChatGPT の要点

- **Projects** に `UNIVERSAL-PROMPT.md` と資料をアップロードし、Project instructions から参照させる。
- **Custom GPT** の指示欄に収まらない場合は、Lite を貼り、Full を Knowledge に入れる。
- Web検索と Code Interpreter は必要に応じて有効にする。

### Claude の要点

- **Projects** の Knowledge に Full と references を入れる。
- **Claude Code** では `CLAUDE.md` から `AGENTS.md` を参照する。
- Agent Skills として使う場合は `.claude/skills/` に置く。

### Gemini の要点

- **Gem** の Instructions には Lite、Knowledge には Full を入れる。
- **AI Studio** では System instructions に Full を貼る。
- **Gemini CLI** では `GEMINI.md` から `AGENTS.md` を参照する。

### ローカルLLMの要点

- 16k未満なら Lite、16k以上なら Full。
- 資料は分割し、`S01`、`S02`… のIDを付ける。
- Phase ごとに依頼を分けると安定する。

---

## 5. フェーズ 0–6（2.5 と 3.5 を含む）

| Phase | やること | 主な出力 | ゲート |
|---|---|---|---|
| **0 受付** | 問い・読者・目的・長さ・立場・資料を固定 | 依頼メモ | 問い・読者・モードが言える |
| **1 収集** | 一次資料を探し、3パスで読み、出典台帳を作る | `sources.csv`, `search-log.md` | 主要主張の根拠がある。反証を1つ以上読んだ |
| **2 評価** | デザイン・バイアス・統計・因果を評価し、主張を抽出 | `claims.csv`, `contradictions.md` | 主張に証拠IDがある。弱い証拠を強いと書いていない |
| **2.5 推論** | 推論の型・隠れた前提・反例・反証条件を点検 | `logic-report.md` | 各荷重主張に型・Warrant・反証条件がある |
| **3 設計** | 結論を1文にし、Toulmin と反論とフレーム批判を組む | `argument-map.md`, `outline.md` | 最強の反論がある。各節に仕事がある |
| **3.5 規範**（条件付き） | 価値前提・分配・反対価値を点検（`normative`/`policy`） | `dossier.md` の価値前提 | 価値前提1文、理論2つ以上、分配、反対価値、濫用・資源配分・宗教/文化（該当時） |
| **4 執筆** | CEAL で段落を書き、概念を接地させる | `article-draft.md` | 全段落に仕事がある。未確認が明示されている |
| **5 監査** | 下書きを凍結し、7ゲート・6役割・3監査 | `review-report.md`, `logic-report.md`, `revision-log.md` | Critical 0。Major は修正済みか理由付き |
| **6 納品** | 修正し、3監査を通し、ドシエを付ける | `article.md`, `dossier.md`, `audit-report.json` ほか | 監査 pass。確認したこと／していないことを説明 |

### モード

| モード | 用途 | 目安 |
|---|---|---|
| `quick` | 短い論考、ブログ、社内メモ | 800〜2,000字（日本語・中国語）／400〜1,000語（英語）、出典3件 |
| `standard` | 一般向けの論考・解説・オピニオン | 3,000〜6,000字／1,500〜3,000語、出典8件 |
| `deep` | 長い評論、調査報告、複数分野の統合 | 8,000字以上／4,000語以上、出典20件 |
| `academic` | 学術エッセイ、文献レビュー、IMRaD | 分野の基準 |
| `synthesis` | 複数論文の統合、系統的レビュー | 出典15件（独立した証拠は別に数える） |
| `logic` | 論理監査、形式化、反例探索 | 事実主張には出典 |
| `normative` | 倫理・哲学・政策・「道」 | 出典5件＋規範理論 |
| `policy` | 政策提言、制度設計 | 出典10件＋実施根拠 |
| `review` | 既存原稿の論理監査 | 対象の全主張 |
| `fact-check` | 特定の主張の事実確認 | 主張ごと |
| `red-team` | 下書きを壊すことだけを行う | 対象の全主張 |
| `decision` | 設計判断・方針選択（記事を書かない） | 決定メモ1〜3頁 |

指定がなければ `standard`。`quick` でも絶対規則は同じです。`logic` は全モードに併走します。
軽い推敲はモードではありません。このスキルを使わず、通常の編集として答えます。

---

## 6. 出力

### ファイルが使える場合

```text
<slug>/
├── article.md
├── dossier.md
├── sources.csv
├── claims.csv
├── audit-report.json
├── argument-lint.json     # 推論監査
├── source-report.json     # 書誌監査
├── logic-report.md        # 論理監査
├── outline.md             # 任意
├── search-log.md          # deep/synthesis/academic
├── screening-log.csv      # synthesis/academic
├── contradictions.md      # 相反する証拠
├── review-report.md       # review/red-team
└── revision-log.md        # 任意
```

### ファイルが使えない場合

回答の冒頭に `【チャット出力モード】` と書き、次の順で出します。

1. 記事本文（`decision` では決定メモ）
2. 出典台帳（表）
3. 主張と証拠の対応（表）
4. 論理監査（結論・前提・推論・反例・反証条件）
5. 監査サマリー（Critical / Major / Minor、判定）
6. ドシエ（結論、最強の反論、限界、未確認、価値前提）

### 引用マーカー

- `[S01]`：出典ID
- `[S01: p.12]`：頁付き
- `[S01; S04]` — 複数出典
- `[C03]` — 主張ID（本文に残す場合のみ）

参考文献スタイルは、APA 7、Chicago、MLA、IEEE、Vancouver から指定に従います。指定がなければ APA 7 風。

---

## 7. 品質確認（G1〜G7）

Phase 5 の**7つの確認項目は G1〜G7**。G0 は受付です。

| ゲート | Pass の条件 | Fail の例 |
|---|---|---|
| **G0 受付** | 問い・読者・モード・資料範囲が明確 | 問いが「AIについて」のまま |
| **G1 問いと結論** | 問いに答え、結論が反論可能で範囲限定 | 結論が2つある、問いをずらしている |
| **G2 証拠** | 全事実主張に出典。主要反証を検討。証拠が独立 | 出典のない統計、撤回論文の引用、同一データの二重計上 |
| **G3 論理** | 推論の型・Warrant・反証条件が説明され、誤謬がない | 相関→因果、非有意→効果なし、必要条件の混同 |
| **G4 反論** | 最強の反論とフレーム批判を検討 | 弱い strawman だけ |
| **G5 文章と読者** | 段落1仕事、概念接地、読みやすい | 背景の羅列、用語の未定義 |
| **G6 完全性** | 引用・数値・未確認・開示が監査済み | 捏造引用、`TODO` 残り |
| **G7 価値・規範** | 価値前提・分配・反対価値を明示 | 事実から規範を導く、文化の本質主義 |

**Readiness**

- `READY` — Critical 0、Major 0、G1〜G7 が Pass、監査 pass。
- `CONDITIONAL` — Critical 0、Major が `Acknowledged limitations` に理由付きで残る。
- `NOT READY` — Critical 1以上、または監査 fail。

**Critical は平均で薄めません。** G2 が Fail なら、G5 が満点でも NOT READY です。

---

## 8. 機械監査スクリプト

依存ライブラリなし。Python 3.9+。3つのスクリプトを使います。

```bash
python scripts/audit_article.py \
  --article article.md \
  --sources sources.csv \
  --claims claims.csv \
  --out audit-report.json

python scripts/argument_lint.py \
  --article article.md \
  --claims claims.csv \
  --sources sources.csv \
  --out argument-lint.json --fail-on major

python scripts/verify_sources.py \
  --sources sources.csv \
  --article article.md \
  --out source-report.json
```

PowerShell では行末の `\` を `` ` `` に変えてください。

### audit_article.py が検査するもの

- 引用マーカー `[S01]` / `[S01: p.12]` / `[S01; S04]` の抽出
- 本文の出典IDが `sources.csv` に存在するか
- 撤回済み・未確認・抄録のみの出典を引用していないか
- 主張の証拠ID、確信度、反証条件（falsifier）
- 荷重主張の数（0個は Major、6個以上は Minor）
- 規範的主張の warrant、因果主張と横断研究の不一致
- DOI の重複（同じ文献の二重計上）
- 直接引用の頁・節の欠落
- 出典のない数値（ヒューリスティック）
- `【未確認】`、`TODO`、`TBD` の残り
- 過剰表現（`明らかに`、`証明された`、`絶対に` など）
- AI slop（`現代社会において`、`多岐にわたる`、`まとめると` など）
- 長すぎる段落・文、ラベルだけの見出し
- 反論・限界への言及の欠落

### argument_lint.py が検査するもの

- 相関・関連の記述と因果主張の同居（因果デザインの言及がない場合）
- 非有意を「効果なし」とする表現
- 少数例からの一般化、偽のジレンマ、権威への訴え
- 人身攻撃、滑坡、事実→価値、生存者バイアス、基礎率の無視
- 反論・限界の欠落、単一の出典への依存
- 荷重主張の反証条件・反対証拠・確信度
- 規範的主張の warrant、因果主張と横断研究の不一致

### verify_sources.py が検査するもの

- CSV の必須列、ID の形式・重複
- DOI、URL、arXiv ID、ISBN の形式
- 出版年、アクセス日
- DOI / URL / タイトルの重複
- 撤回済み・未確認の出典の使用
- 本文が参照する出典IDの欠落
- `--online` を付けた場合の到達性（失敗しても停止しない）

### 終了コード

| コード | 意味 |
|---|---|
| `0` | READY または CONDITIONAL |
| `2` | NOT READY（Critical あり、または `--strict` で Major あり） |
| `3` | 入力エラー |

### 限界

このスクリプトは**意味内容を保証しません**。

- 書誌・DOI・URL の実在は確認しません。
- 引用が主張を本当に支えているかは判定しません。
- 数値の分母・単位・期間・集団の正しさは判定しません。
- 論証の妥当性、反論の強さ、フレームの妥当性は判定しません。
- 日本語の文分割は近似です。

機械監査が通っても、Phase 5 の人間監査と、専門家の確認は必要です。
スクリプトを実行できないAIは、`UNIVERSAL-PROMPT.md` の「10. 完了前チェック」を手動で行い、その旨を明記してください。

---

## 9. テンプレートとリファレンス

| ファイル | 用途 |
|---|---|
| `assets/article-brief.md` | Phase 0。問い・読者・制約・完了条件。 |
| `assets/argument-map.md` | Phase 3。Toulmin、反論、フレーム批判、節の仕事。 |
| `assets/source-ledger.csv` | Phase 1。出典台帳の列と記入例。 |
| `assets/claim-evidence.csv` | Phase 2。主張と証拠の対応表。 |
| `assets/review-scorecard.md` | Phase 5。7ゲート、指摘一覧、Concession Threshold。 |
| `assets/dossier-template.md` | Phase 6。証拠ドシエ。 |

CSV は UTF-8（BOM 可）で保存してください。セルにカンマが入る場合は、`"..."` で囲みます。

| リファレンス | 内容 |
|---|---|
| `references/research-protocol.md` | 検索、3パス読解、出典台帳、反証探索、停止規則。 |
| `references/evidence-appraisal.md` | 研究デザイン、バイアス、統計、因果、GRADE 簡易版。 |
| `references/knowledge-synthesis.md` | 多資料読解、証拠の独立性、PRISMA、メタ分析、不一致。 |
| `references/logic-and-inference.md` | 標準形、演繹・帰納・因果・確率、ACH、誤謬と修復。 |
| `references/normative-and-conceptual.md` | 価値前提、倫理理論、政策、概念分析、文化と「道」。 |
| `references/orchestration.md` | 役割、ハンドオフ、並列化、長文脈、停止規則。 |
| `references/argument-architecture.md` | Toulmin、推論形式、反論、フレーム批判、構成、誤謬。 |
| `references/drafting-protocol.md` | CEAL、グラウンディング、引用、数値、文体、AI slop。 |
| `references/japanese-editing.md` | 日本語の7原則、意味保持、文長・読点、yomiyasu 連携。 |
| `references/adversarial-review.md` | 7ゲート、赤チーム、Concession Threshold、監査手順。 |
| `references/citation-and-provenance.md` | 出典台帳、引用マーカー、検証、撤回確認、引用スタイル。 |
| `references/skill-stack.md` | 既存スキルとの対応、採用要素、出典・ライセンス。 |

すべてを最初から読む必要はありません。Phase に応じて、必要なファイルだけ開きます。
ファイルが読めないAIは、`UNIVERSAL-PROMPT.md` の本文だけで動けます。

---

## 10. 設計のポイント

### 証拠台帳と主張台帳を分ける

`sources.csv` は「資料」、`claims.csv` は「主張」の台帳です。1つの資料が複数の主張を支え、1つの主張が複数の資料に支えられる関係を、IDで追えるようにします。

### 荷重主張を3〜5個に絞る

すべての主張を同じ強さで書くと、読者は何が重要かわかりません。それが崩れたら結論が崩れる「荷重主張」を3〜5個に絞り、それぞれに証拠・Warrant・反証条件を付けます。

### 最強の反論を先に受ける

反論を「弱い藁人形」にしないために、相手の立場を相手の言葉で書き、相手の最良の証拠を探し、相手が読んでも妥当と思う形にします。反論が正しければ、結論を弱めるか変えます。

### Concession Threshold で迎合を防ぐ

反論を受けたら、強さを1〜5で評価します。**4以上のみ実質的に譲歩**し、3以下は証拠を挙げて説明します。ユーザーの執拗さや権威を、反論の強さと混同しません。

### フレーム批判を必須にする

問いの前提を疑わずに、どれだけ内部的に整合した議論をしても、間違った問いへの良い答えにしかなりません。問いの前提を列挙し、別の問いを3つ作り、「問いが間違っている」可能性を1回は真剣に検討します。

### 未確認を隠さない

確認できないことは `【未確認：〜が必要】` と本文に残します。文章を滑らかにするために未確認を消しません。`dossier.md` にも残します。

### 能力に合わせて出力を変える

ファイルが使えるAIはファイルを作り、使えないAIはチャット内に同じ内容を出します。Web検索がなければ資料を求め、コード実行がなければ手動監査に切り替えます。**できないことを、できるふりにしない**のが設計の中心です。

### 日本語の推敲

日本語の記事は、`references/japanese-editing.md` の7原則で最終推敲します。主語と述語、修飾語の掛かる先、比喩動詞、擬人化、前置き、文長、読点を確認します。平均文長は30〜45文字、1文の読点は0〜2個を目安にします。意味・数値・否定・言い切りの強さは変えません。

yomiyasu が使える場合は、最終稿に `yomiyasu_lint.py` と `yomiyasu_diff.py` を実行します。候補は直すべき指示ではなく、文脈を読んで残すか決めます。点数や候補数を合否にしません。

---

## 11. 評価

`evals/evals.json` に、23の行動評価ケースと7つのスクリプト回帰テスト（R01–R03、R06–R09）があります。`scripts/check_repo.py` はさらに R04（`--strict`）と R05（入力なし）を検証します。

- 短い論考（quick）
- ユーザーの結論への迎合を拒否
- 不確かな書誌を捏造しない
- 全文が読めない論文の文献レビュー
- 相関→因果の原稿監査
- 公式統計のファクトチェック
- フレームロックの検出
- 撤回論文の検出と差し替え
- 学術論文の Introduction
- 対立する証拠の処理
- AI slop の除去
- 参考文献の捏造要求を拒否
- ファイルが使えないチャット環境
- Web検索がない環境
- 長い資料を分割して読む
- 必要条件と十分条件の混同
- 基礎率とベイズ推論
- 因果識別と交絡
- 独立でない証拠の統合
- 規範的論証と価値前提
- 概念分析と反例
- 圧力下でも結論を証拠に合わせる

### 回帰テスト

```bash
# 正常系: READY
python scripts/audit_article.py \
  --article evals/fixtures/good-article.md \
  --sources evals/fixtures/good-sources.csv \
  --claims evals/fixtures/good-claims.csv

# 異常系: NOT READY（終了コード 2）
python scripts/audit_article.py \
  --article evals/fixtures/bad-article.md \
  --sources evals/fixtures/bad-sources.csv \
  --claims evals/fixtures/bad-claims.csv

# 推論監査: REVIEW（終了コード 2）
python scripts/argument_lint.py \
  --article evals/fixtures/logic-bad-article.md \
  --claims evals/fixtures/logic-bad-claims.csv \
  --sources evals/fixtures/logic-bad-sources.csv \
  --fail-on major

# 書誌監査: FAIL（終了コード 2）
python scripts/verify_sources.py \
  --sources evals/fixtures/bad-sources.csv \
  --article evals/fixtures/bad-article.md \
  --fail-on major
```

`good-article.md` は READY、`bad-article.md` は NOT READY、`logic-bad-article.md` は REVIEW、`bad-sources.csv` は FAIL になることを確認済みです。

---

## 12. よくある失敗と、この指示書の対処

| 失敗 | 対処 |
|---|---|
| 資料の要約を並べるだけ | テーマで統合し、各主張に証拠を紐づける |
| 出典を付けたが、主張を支えていない | `claims.csv` で主張と証拠を対応させ、Phase 5 で引用監査 |
| 反対側の弱い主張だけを攻撃 | Steelman プロトコルと Contrarian 役 |
| 相関を因果と言う | 主張タイプを分類し、G3 で因果チェック |
| 非有意を「効果なし」と言う | 効果量と信頼区間を確認 |
| 平均だけを見て分布を無視 | 分布効果・最弱層を確認 |
| ユーザーの望む結論に合わせる | R07、Concession Threshold、赤チーム |
| 問いの前提を疑わない | フレーム批判を必須化 |
| 未確認を隠す | `【未確認】` マーカーと `dossier.md` |
| AI っぽい水増し | AI slop チェックリストと機械監査 |
| 監査せずに「完了」と言う | 監査スクリプトと完了前チェック |
| ファイルが読めないのに読んだふり | 「実行環境に応じた適応」と能力の明示 |
| 検索できないのに検索したふり | 資料を求める。`【未確認】` を付ける |
| 監査を実行できないのに pass と言う | 手動監査に切り替え、「未実行」と明記 |

---

## 13. 制約と注意

- **書誌の実在確認は自動ではありません。** DOI・URL・頁は、Crossref、PubMed、出版社などで人間が確認してください。
- **専門家の代替ではありません。** 医療・法務・政策・安全に関わる内容は、資格を持つ専門家の確認が必要です。
- **機械監査は意味を理解しません。** 引用が主張を支えているか、論証が妥当かは、Phase 5 の人間監査で確認してください。
- **すべての分野を網羅しません。** 分野固有の方法論（臨床試験、計量経済学、法解釈など）は、必要に応じて専門スキルや専門家を呼んでください。
- **Web の情報は変わります。** アクセス日を記録し、重要な数値は公開前にもう一度確認してください。
- **AI 利用の開示**が必要な場面では、`dossier.md` の「AI 利用の開示」を埋めてください。
- **プラットフォームの指示欄には文字数上限があります。** 超える場合は、ファイルをアップロードして短い指示から参照させるか、Lite を使ってください。

---

## 14. ファイル構成

```text
universal-article-writer/
├── README.md
├── UNIVERSAL-PROMPT.md          # どのAIでも使う完全版
├── UNIVERSAL-PROMPT-LITE.md     # 小さい文脈向け
├── SKILL.md                     # Agent Skills 対応ホスト用
├── AGENTS.md                    # コーディングエージェント用
├── adapters/
│   ├── chatgpt.md
│   ├── claude.md
│   ├── gemini.md
│   ├── coding-agents.md
│   └── generic-chat.md
├── references/                  # 14ファイル（4エンジン＋日本語推敲＋意思決定＋専門リファレンス）
├── docs/                        # 根拠・設計・比較・評価・スキル調査・FAQ・公開手順
├── examples/                    # quick / review / chat-only
├── assets/                      # 7テンプレート＋バナー＋ソーシャルプレビュー
├── scripts/
│   ├── audit_article.py
│   ├── argument_lint.py
│   ├── verify_sources.py
│   ├── build_universal.py       # UNIVERSAL-PROMPT.md の生成
│   ├── check_consistency.py     # 文書間の規則・フェーズ・役割・件数の検査
│   └── check_repo.py            # CI用の総合検査
├── evals/
│   ├── evals.json
│   └── fixtures/
└── .github/                     # CI・Issue/PRテンプレート
```

### プロンプトの再生成

`SKILL.md` を編集したら、次を実行して `UNIVERSAL-PROMPT.md` を更新します。

```bash
python scripts/build_universal.py
python scripts/build_universal.py --check
```

---

## 15. ライセンスと帰属

本指示書は **MIT** です（`SKILL.md` の `license` フィールド）。

設計時に、次のプロジェクトの知見を参照しました。文章・プロンプト・図表の大量コピーはしていません。

- K-Dense AI, *Scientific Agent Skills* — MIT
  https://github.com/K-Dense-AI/scientific-agent-skills
- Matt Pocock, *skills*
  https://github.com/mattpocock/skills
- Jesse Vincent, *Superpowers*
  https://github.com/obra/superpowers
- Anthropic, *skills*
  https://github.com/anthropics/skills
- Cheng-I Wu, *Academic Research Skills*
  https://github.com/Imbad0202/academic-research-skills
- timpara, *opencode-academic-research* — CC-BY-NC 4.0
  https://github.com/timpara/opencode-academic-research
- Halfofthesky, *Logic & Reasoning Skills* — CC BY-NC-SA 4.0
  https://github.com/Halfofthesky/logic-reasoning-skills
- zhujiaozi, *Logic Audit Skill* — MIT
  https://github.com/zhujiaozi/logic-audit-skill
- ajitta, *Dialectic Skills* — MIT
  https://github.com/ajitta/dialectic-skills
- human-avatar, *skills-for-humanity*
  https://github.com/human-avatar/skills-for-humanity
- O0000-code, *meta-analysis-skill* — PolyForm-NC + CC BY-NC-SA 4.0
  https://github.com/O0000-code/meta-analysis-skill
- ysskrishna, *Thinking Methods* — MIT
  https://github.com/ysskrishna/ai-agent-skills

**ARS は CC-BY-NC 4.0** です。ARS 由来の概念を商用利用する場合は、法的判断が必要になり得ます。本指示書には、ARS の原文・図表・プロンプトを大量に含めていません。

---

## 16. バージョン

- **3.1.0** — 発火範囲を証拠仕事に限定。`decision` モード、`SKILL.md` の圧縮、Phase 3.5 と6役の統一、`check_consistency.py` を追加。
- **3.0.1** — 日本語推敲層（yomiyasu の7原則）を追加。日本語の表記・比喩・文長・読点を最終推敲に組み込み、README と SKILL の日本語を整理。
- **3.0.0** — 論理・統合・規範・分業の4エンジン、日本語推敲層、7つの確認項目、3監査、22評価ケース。
- **2.0.0** — ユニバーサル版。特定のAI・ツールへの依存を外し、チャット出力モード、能力適応、Lite 版、プラットフォーム別アダプターを追加。
- **1.0.0** — 初版。7フェーズ、証拠台帳、赤チーム監査、監査スクリプト。
