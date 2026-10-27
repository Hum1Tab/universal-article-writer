# Skill Stack

このスキルは、既存のスキル群の**構造・発想・失敗様式**を参考にし、文章と手順は本スキル用に新しく書いたものだ。原文の大量コピーはしていない。

> 参照時点：2026年10月。リポジトリの内容・ライセンス・スキル名は変更されうる。再配布・商用利用の前に、各リポジトリの最新の LICENSE を確認すること。

---

## 1. 設計方針

1. **単体で動く。** 既存スキルがなくても、フェーズ 0–6（2.5 と 3.5 を含む）と内蔵リファレンスで完結する。
2. **既存スキルがあれば専門家として呼ぶ。** ただし、呼び出しに失敗しても止まらない。
3. **構造を借り、文言は借りない。** ワークフロー、ゲート、失敗様式、評価観点を参考にする。
4. **監査可能性を最優先する。** 主張、証拠、推論、反論、引用状態をファイルに残す。
5. **過剰な自動化をしない。** 最終判断は人間に残す。AI が書いたことを隠さない。
6. **正本を1つにする。** 規則・フェーズ・役割・モードの本文は `SKILL.md` に置き、他は ID で参照する。
   呼び出し表（このファイル）と生成プロンプトだけが例外で、生成物は CI が同期を検査する。

---

## 2. 対応表

| 既存スキル | 出典 | ライセンス | 借りた要素 | 本スキルでの実装 |
|---|---|---|---|---|
| `scientific-writing` | K-Dense `scientific-agent-skills` | MIT | 証拠に紐づく執筆、不確実性の言語、盗用・捏造の防止 | Phase 4、`drafting-protocol.md` |
| `literature-review` | 同上 | MIT | 系統的検索、スクリーニング、テーマ統合、PRISMA 的記録 | Phase 1、`research-protocol.md` |
| `scientific-critical-thinking` | 同上 | MIT | 研究デザイン、バイアス、統計・因果の批判、GRADE 的格付け | Phase 2、`evidence-appraisal.md` |
| `hypothesis-generation` | 同上 | MIT | 主張タイプ、代替説明、反証条件、予測 | Phase 3、`argument-architecture.md` |
| `citation-management` | 同上 | MIT | DOI/PMID/arXiv の検証、書誌の一貫性、BibTeX 的発想 | `citation-and-provenance.md` |
| `peer-review` | 同上 | MIT | 査読形式の批判、Major/Minor の分類、具体的な修正要求 | Phase 5、`adversarial-review.md` |
| `scholar-evaluation` | 同上 | MIT | 根拠に基づく評価、スコアの誤用防止 | Phase 5 の重大度分類 |
| `consciousness-council` | 同上 | MIT | 多視点の赤チーム、フレーム批判 | Phase 5 の6役割 |
| `research` | mattpocock/skills | 要確認 | 一次資料への遡り、引用付きリサーチノート、読者への説明 | Phase 1、`research-protocol.md` |
| `grilling` / `grill-me` | 同上 | 要確認 | 問いと前提の深掘り、答える前に質問する | Phase 0、Phase 3 |
| `writing-shape` | 同上 | 要確認 | 概念のグラウンディング、読者の理解順、段落の順序 | Phase 4、`drafting-protocol.md` |
| `writing-beats` | 同上 | 要確認 | 段落のリズム、1段落1仕事、場面の切り替え | Phase 4 |
| `writing-fragments` | 同上 | 要確認 | 断片から構成を組む、書く前に素材を並べる | Phase 3、Phase 4 |
| `brainstorming` | obra/superpowers | 要確認 | 発散→収束、前提を疑う、選択肢を広げる | Phase 0、Phase 3 |
| `verification-before-completion` | 同上 | 要確認 | 証拠なき完了宣言の禁止、完了前の検証 | Phase 6、`SKILL.md` §9 |
| `skill-creator` | anthropics/skills | 一部 source-available | スキルの構造、description の最適化、評価の設計 | スキル設計、`evals/evals.json` |
| `deep-research` | timpara/opencode-academic-research（ARS） | CC-BY-NC 4.0 | 多段の調査、検索ログ、反証探索、引用検証 | Phase 1、`research-protocol.md` |
| `academic-paper` | 同上 | CC-BY-NC 4.0 | 学術論文の構成、引用スタイル、投稿前チェック | `academic` モード、`citation-and-provenance.md` |
| `academic-paper-reviewer` | 同上 | CC-BY-NC 4.0 | 多視点査読、Devil's Advocate、Concession Threshold | Phase 5、`adversarial-review.md` |
| `academic-pipeline` | 同上 | CC-BY-NC 4.0 | 段階的ゲート、整合性検証、来歴の記録 | 7フェーズ、`dossier.md` |
| `argument-analyst` / `fallacy-detector` / `formal-logic-solver` | Halfofthesky/logic-reasoning-skills | CC BY-NC-SA 4.0 | 標準形、enthymeme の由来タグ、24+ の誤謬、IBE の7美徳、真理表・証明 | Phase 2.5、`logic-and-inference.md` |
| `logic-audit` | zhujiaozi/logic-audit-skill | MIT | 13+ の誤謬、証拠等級 E0–E5、重大度の校正、修正論証チェーン | Phase 5、`argument_lint.py` |
| `dia-warrant` / `dia-reductio` / `dia-negative` / `dia-conjecture` / `dia-counterplan` | ajitta/dialectic-skills | MIT | Toulmin + Walton の批判的質問、背理法、内在的批判、反例、反計画 | Phase 2.5–5 |
| `s4h-*` | human-avatar/skills-for-humanity | 要確認 | 確率較正、認識論的地位、三角測量、倫理評議会、システム思考 | Phase 0–5 |
| `meta-analysis-skill` | O0000-code/meta-analysis-skill | PolyForm-NC + CC BY-NC-SA 4.0 | PRISMA 2020、GRADE、AMSTAR 2、二重スクリーニング、来歴ゲート | Phase 1–2、`knowledge-synthesis.md` |
| `thinking-methods` | ysskrishna/ai-agent-skills | MIT | 方法の選択、critical-thinking、ethical-thinking、pre-mortem、trade-off | Phase 0、Phase 3 |
| `yomiyasu` | nanaism/yomiyasu | MIT | 日本語の7原則、意味保持、主述・比喩・擬人化・文長・読点 | Phase 4.2、`japanese-editing.md` |

**「要確認」のライセンス**：設計時にリポジトリの LICENSE を確認しきれなかったもの。再配布する場合は、必ず各リポジトリの LICENSE を確認すること。本スキルは、これらのスキルの文章をコピーしていないため、アイデアの参照として扱っている。

### 2.1 呼び出し表

ホストにこれらのスキルがある場合だけ、専門家として呼ぶ。**なくても止まらない**（本文と参照ファイルに同等の手順を内蔵している）。呼び出し名・ライセンスは変わりうるので、実行時に存在を確認する。

| 既存スキル | 呼ぶ Phase | 借りるもの |
|---|---|---|
| `literature-review` | 1 | 系統的検索、スクリーニング、PRISMA、テーマ統合 |
| `research` | 1 | 一次資料への遡り、引用付きリサーチノート |
| `scientific-critical-thinking` | 2, 5 | 研究デザイン、バイアス、GRADE/RoB、統計批判 |
| `hypothesis-generation` | 3 | 主張タイプ、代替説明、反証条件、予測 |
| `scientific-writing` | 4, 6 | 証拠との結び付け、不確実性、盗用・捏造防止 |
| `doc-coauthoring` | 4 | 文脈収集、セクション単位の改善、読者テスト |
| `better-writing` | 4, 6 | 声のダイヤル、サンプル校正、保存チェック、クラスタ型 slop 監査 |
| `yomiyasu` | 4, 6 | 日本語の主述・比喩・擬人化・前置き・文長・読点の推敲、意味保持の検査 |
| `brand-guidelines` | 4 | 声・トーンの一貫性、ブランド表現 |
| `internal-comms` | 4 | 読者・目的・媒体に合う形式 |
| `creative-writing-skills` | 4 | 場面、緊張、ペース、視点（ノンフィクションの範囲で） |
| `academic-paper-skills` | 3, 4 | CARS、IMRaD、貢献、限界、投稿前チェック |
| `econ-writing-skill` | 3, 4 | 経済学の論証構成、識別戦略の書き方 |
| `writing-for-agents` | 設計時 | 情報階層、コンテキストポインタ、完了条件 |
| `citation-management` | 1, 5 | DOI/PMID/arXiv のメタデータ検証、BibTeX |
| `peer-review` | 5 | 査読形式の批判、Major/Minor の分類 |
| `scholar-evaluation` | 5 | 根拠に基づく評価、スコアの誤用防止 |
| `consciousness-council` | 5 | 多視点の赤チーム、フレーム批判 |
| `grilling` / `grill-me` | 0 | 問いと読者の深掘り |
| `writing-shape` / `writing-beats` | 4 | 概念のグラウンディング、段落の順序 |
| `verification-before-completion` | 6 | 証拠なき完了宣言の禁止 |
| `academic-paper` / `deep-research` | 1–6 | 大規模な学術パイプライン（任意） |
| `skill-creator` | 設計時 | スキルの構造、評価、記述の最適化 |
| `argument-analyst` / `fallacy-detector` / `formal-logic-solver` | 2.5, 5 | 標準形、隠れた前提、24+の誤謬、真理表・証明 |
| `logic-audit` | 5 | 13+の誤謬、証拠等級 E0–E5、重大度の校正 |
| `dia-warrant` / `dia-reductio` / `dia-negative` / `dia-conjecture` / `dia-counterplan` | 2.5, 3, 5 | Toulmin + Walton の批判的質問、背理法、内在的批判、反例、反計画 |
| `skills-for-humanity` (`s4h`) | 0, 2.5, 3, 5 | 確率較正、認識論的地位、三角測量、倫理評議会、システム思考 |
| `meta-analysis-skill` | 1, 2 | PRISMA 2020、GRADE、AMSTAR 2、二重スクリーニング、来歴ゲート |
| `thinking-methods` | 0, 3 | 方法の選択、意思決定、トレードオフ、事前検死 |
| `scientific-agent-skills` | 1, 2 | 証拠に紐づく執筆、分野別の方法論、来歴 |

**組み合わせ方は「積み重ね」ではなく「層」**：証拠層 → 統合層 → 推論層 → 価値層 → 構造層 → 段落層 → 声層 → 媒体層 → 完了層。上位層は下位層を上書きしない。特に、声や読みやすさは、事実・引用・不確実性・反論・価値前提を変更できない。

---

## 3. 特に採用した知見

### 3.1 ARS（Academic Research Skills）

timpara/opencode-academic-research は、Cheng-I Wu による academic-research-skills の OpenCode ポート。次の概念を採用した。

| 知見 | 元の文脈 | 本スキルでの実装 |
|---|---|---|
| **Frame-lock** | AI が与えられた問いの枠内で批判を繰り返し、前提そのものを疑えない | Phase 5 の frame-lock check。問いの前提を列挙し、別の問いを3つ作り、「問いが間違っている」結論を一度書く |
| **Sycophancy under pushback** | ユーザーに押されると、証拠が変わっていなくても譲歩する | Concession Threshold。反論の強さを1〜5で評価し、4以上のみ実質的に譲歩 |
| **Concession Threshold** | Devil's Advocate が反論をスコア化し、安易な譲歩を防ぐ | `adversarial-review.md` §5。連続譲歩の禁止、譲歩率の記録 |
| **Citation hallucination** | 実在する引用が、主張を支えていない／存在しない書誌 | Phase 5 の引用監査。書誌の実在確認と、主張対応の確認を分ける |
| **Claim-faithfulness** | 引用が主張を本当に支えているかの監査 | `claims.csv` の `claim` と `evidence_ids` の対応、`audit_article.py` の機械監査 |
| **段階的ゲート** | 各段階で人間の確認を挟み、整合性を検証する | 7フェーズのゲート、`READY` / `CONDITIONAL` / `NOT READY` |

**ライセンス注意**：ARS は CC-BY-NC 4.0。本スキルは、ARS の文章をコピーせず、概念を自分の言葉で再実装している。ただし、ARS 由来のアイデアを商用利用する場合は、法的判断が必要になる可能性がある。本スキル自体は MIT で配布するが、ARS の原文・図表・プロンプトをそのまま含めないこと。

### 3.2 K-Dense Scientific Agent Skills

177の科学的スキル群。次の点を採用した。

- **証拠に紐づく執筆**：文章の各主張を、出典と対応させる。
- **研究デザインの批判**：RCT、観察研究、質的研究を、デザインごとに評価する。
- **GRADE 的思考**：デザインのラベルではなく、バイアス・非一貫性・非直接性・不精確さ・出版バイアスで格付けする。
- **引用管理**：DOI、PMID、arXiv のメタデータを検証する。
- **査読形式**：Major / Minor に分け、具体的な修正を要求する。
- **多視点の議論**：異なる専門家の視点をぶつける。

### 3.3 mattpocock/skills

- **research**：一次資料に遡り、引用付きのノートを作る。
- **grilling**：答えを書く前に、問いと前提を掘る。
- **writing-shape**：読者が知っていることから始め、新しい概念を1つずつ導入する。
- **writing-beats**：段落のリズム、1段落1仕事。
- **writing-fragments**：構成を決める前に、素材を断片として集める。

### 3.4 obra/superpowers

- **brainstorming**：発散と収束を分ける。前提を疑う。
- **verification-before-completion**：「完了しました」と言う前に、証拠を確認する。監査していないのに完成と言わない。

### 3.5 anthropics/skills

- **skill-creator**：SKILL.md の構造、description の書き方、評価の設計。
- 本スキルでは、description に「使う仕事」を明示し、500行以下の本体（v3.1 では約360行）に保ち、
  必要時に読む `references/` に詳細を分けた。規則・フェーズ・役割の本文は本体に置き、
  他文書は ID で参照する（`scripts/check_consistency.py` が検査する）。

---

### 3.6 Halfofthesky — Logic & Reasoning Skills

- **argument-analyst**：論証の検出 → 標準形 → 妥当性 → 誤謬 → 説明の質 → 判定の6段階。
- **由来タグ**：補った前提を `[TEXTUAL]` / `[CONVENTIONAL]` / `[ANALYST]` に分ける。本スキルでは `[TEXT]` / `[CONV]` / `[ANALYST]` とした。
- **charity ceiling**：善意の解釈はするが、論者が言っていない論証に作り替えない。
- **24+ の誤謬**：4〜5家族に分類し、各誤謬に「誤謬でない場合」を付ける。
- **IBE の7美徳**：説明力、深さ、予測力、反証可能性、節度、単純性、保守性。
- **formal-logic-solver**：真理表、自然演繹、三段論法、量化子。形式化が有効な場面と無効な場面を分ける。

**ライセンス注意**：CC BY-NC-SA 4.0。本スキルは概念を参照し、文章・プロンプトをコピーしていない。商用利用を検討する場合は法的確認が必要である。

### 3.7 zhujiaozi — Logic Audit Skill

- **証拠等級 E0–E5**：断言・個別事例・非系統観察・相関・統制研究・複数一致。
- **重大度の校正**：情報欠落を重大度に混ぜない。著者が既に限定している表現を二重に減点しない。
- **誤報抑制**：善意の解釈で再確認してから指摘する。
- **修正論証チェーン**：指摘だけでなく、修正後の論証を公開する。
- **自審**：監査自体の監査（数字の捏造、過剰検出、越権的な再構成の防止）。

### 3.8 ajitta — Dialectic Skills

- **dia-warrant**：Toulmin の data / warrant / backing / qualifier / rebuttal を、Walton の批判的質問と対応させる。妥当性ではなく「弱いリンク」を特定する。
- **dia-reductio**：前提を明示し、矛盾を導出し、どの前提を捨てるかを選択肢として示す。
- **dia-negative**：対象自身の基準で内在的に批判する。外部の価値を持ち込まない。
- **dia-conjecture**：Lakatos の証明と反駁。反例ごとに、規則の修正（除外・条件追加・定義変更）を選ぶ。
- **dia-counterplan**：同じ事実から、反対の前提で最良の代替計画を作る。どちらが勝つかは裁定しない。
- **dia-refine / dia-iterate**：確認できた誤りだけを直す。反復は外部検証をゲートにする。

**採用した考え方**：反論は「相手を倒す」ためではなく、**どの前提が結論を支えているかを特定する**ために使う。

### 3.9 human-avatar — skills-for-humanity (`s4h`)

- **方法の層**：知識（training）でもツール（MCP）でもない、思考の手順をスキルにする。
- **確率較正**：言葉の強さと確率の目安を対応させる。
- **認識論的地位**：知っている／信じている／仮定している／願っているを分ける。
- **三角測量**：独立した情報源で確認する。増幅（amplification）と裏付け（corroboration）を区別する。
- **倫理評議会**：複数の規範理論で同じ問題を見て、一致点と真正の不一致を分ける。
- **システム思考**：フィードバックループ、レバレッジポイント、意図せぬ結果。

**ライセンス**：要確認。本スキルは概念のみを参照している。

### 3.10 O0000-code — meta-analysis-skill

- **PRISMA 2020 / PRISMA-S**：検索・スクリーニング・適格・採用の来歴。
- **二重スクリーニングと κ**：独立2名、不一致の解消。
- **R による赤信号**：I²、単一研究の寄与、PET の切片、ファンネルの非対称を、モデルの目視ではなく計算で判定する。
- **7つの人間署名ゲート**：不可逆な判断の前に、監査カードを人間が確認する。
- **引用検証**：OpenAlex / Crossref に対する HTTP 確認。
- **数値の忠実性ゲート**：出力のすべての数値が入力に由来することを確認する。

**採用した考え方**：統合の判断は「平均」ではなく、**異質性・バイアス・独立性・確信度**の4点で行う。本スキルはメタ分析を自動実行しない。解釈と執筆の手順として採用する。

**ライセンス注意**：PolyForm-NC + CC BY-NC-SA 4.0。概念のみを参照し、コード・文書をコピーしていない。

### 3.11 ysskrishna — Thinking Methods

- **方法のルーティング**：問題の型から方法を選ぶ。
- **critical-thinking / ethical-thinking / pre-mortem / trade-off**：判断の前に、弱点・価値・失敗・代替を確認する。
- **light path と worked example**：小さな問いには短い手順、大きな問いには例付きの手順。

### 3.12 nanaism — yomiyasu

- **7つの変換原則**：主述・修飾・条件、文の働きと文体、擬人化、比喩動詞、前置きと否定対比、情報の不増補、文長・読点・装飾。
- **意味の保持**：主張・比重・言い切りの強さ・文の働きを変えない。言い直しテストで6点を比較する。
- **文書の種類と読者**：12種類の文書と3段階の読者で、残す書き方を変える。
- **検査ツール**：`yomiyasu_lint.py`（表現・書式）、`yomiyasu_diff.py`（前後の比較）、`yomiyasu_check.py`（まとめ実行）。
- **限界の明示**：lint の候補は合否ではない。意味の保持と読みやすさは人間が確認する。

**ライセンス**：MIT。本スキルは原則を要約して再実装し、原文・プロンプト・検査コードを収録していない。

### 3.13 v3.0 で新しく採用した知見

1. **推論の型を明示する**（演繹・帰納・因果・最良説明・統計・規範・概念）。
2. **隠れた前提の由来タグ**と charity ceiling。
3. **証拠の独立性**（同じデータを二重に数えない）。
4. **確率・基礎率・ベイズ**を、言葉の強さと結びつける。
5. **因果識別**（反事実、交絡、DiD/RD/IV、感度分析）。
6. **ACH**（競合仮説分析）と診断的証拠。
7. **規範理論の複数適用**と価値前提の明示。
8. **概念分析**（必要十分条件、反例、文脈依存、操作的定義）。
9. **役割分担とハンドオフ**（読解・抽出・方法論・統合・論理・規範・赤チーム・編集・監査）。
10. **3つの機械監査**（記事・推論・書誌）。
11. **日本語推敲層**（yomiyasu の7原則）。

---

## 4. 採用しなかったもの

| 採用しなかったもの | 理由 |
|---|---|
| 完全自律の研究パイプライン | 人間の確認なしに論文を生成すると、捏造・フレームロック・引用幻覚のリスクが高い |
| 38エージェントの固定パイプライン | 小規模な記事には過剰。必要な役割だけを呼ぶ |
| 学術誌のスコアリング（0〜100点） | スコアが独り歩きし、平均で Critical を薄める危険がある |
| 特定の引用スタイルへの固定 | ユーザーの指定に従うべき |
| 長大なプロンプトの埋め込み | 保守が難しい。リファレンスを分け、必要時に読む |
| AI 検出器による判定 | 誤検知が多く、証拠にならない |
| 「人間らしく見せる」ための書き換え | 目的は品質であり、AI 利用の隠蔽ではない |

---

## 5. 本スキルの独自要素

既存スキルにない、または弱かった点として、次を追加した。

1. **証拠台帳と主張台帳の分離**：`sources.csv` と `claims.csv` を分け、主張ごとに証拠を紐づける。
2. **荷重主張の3〜5個制限**：論証を薄めない。
3. **反証条件の必須化**：各荷重主張に「何が観察されたら撤回するか」を書く。
4. **フレーム批判の必須化**：問いの前提を1回は疑う。
5. **Concession Threshold の明文化**：迎合を防ぐ。
6. **`【未確認】` マーカー**：不確実性を隠さず、本文に残す。
7. **3つの機械監査**：記事（`audit_article.py`）、推論（`argument_lint.py`）、書誌（`verify_sources.py`）。
8. **Readiness の3段階**：Critical を平均で薄めない。
9. **納品メッセージの契約**：結論、最強の反論、未解決の論点、論理判定、価値前提、ファイルパスを必ず含める。
10. **4つのエンジンと日本語推敲層**：論理・統合・規範・オーケストレーション、および yomiyasu 由来の日本語推敲を、単体で動く参照ファイルとして内蔵する。
11. **推論の型と価値層の分離**：事実・推論・価値・表現を層に分け、上位層が下位層を上書きしない。
12. **証拠の独立性の明示**：論文数ではなく、独立した研究・データセットを数える。
13. **7ゲート**：G7（価値・規範）を追加し、倫理・政策の記事でも監査できる。
14. **23の行動評価と7つのスクリプト回帰**：論理・確率・因果・統合・規範・概念・迎合耐性・設計判断を回帰テストする。
15. **横断的な一貫性検査**：規則ID・フェーズ・役割・モード・件数を `check_consistency.py` が比較する。
16. **`decision` モード**：設計判断を記事ではなく決定メモ（選択肢・基準・トレードオフ・撤退条件）にする。

---

## 6. メンテナンス

- 新しいスキルを追加する場合は、このファイルの対応表に追記する。
- ライセンスが不明なスキルは「要確認」と書き、確認したら更新する。
- 既存スキルの仕様が変わったら、Phase の対応を見直す。
- `scripts/audit_article.py` のチェック項目を増やしたら、`evals/evals.json` にテストを追加する。
- 本スキルのバージョンは `SKILL.md` の `metadata.version` で管理する。

---

## 7. 帰属

本スキルは、次のプロジェクトの知見に感謝する。

- K-Dense AI, *Scientific Agent Skills* — https://github.com/K-Dense-AI/scientific-agent-skills (MIT)
- Matt Pocock, *skills* — https://github.com/mattpocock/skills
- Jesse Vincent, *Superpowers* — https://github.com/obra/superpowers
- Anthropic, *skills* — https://github.com/anthropics/skills
- Cheng-I Wu, *Academic Research Skills* — https://github.com/Imbad0202/academic-research-skills
- timpara, *opencode-academic-research* — https://github.com/timpara/opencode-academic-research (CC-BY-NC 4.0)
- Halfofthesky, *Logic & Reasoning Skills* — https://github.com/Halfofthesky/logic-reasoning-skills (CC BY-NC-SA 4.0)
- zhujiaozi, *Logic Audit Skill* — https://github.com/zhujiaozi/logic-audit-skill (MIT)
- ajitta, *Dialectic Skills* — https://github.com/ajitta/dialectic-skills (MIT)
- human-avatar, *skills-for-humanity* — https://github.com/human-avatar/skills-for-humanity
- O0000-code, *meta-analysis-skill* — https://github.com/O0000-code/meta-analysis-skill (PolyForm-NC + CC BY-NC-SA 4.0)
- ysskrishna, *Thinking Methods* — https://github.com/ysskrishna/ai-agent-skills (MIT)
- nanaism, *yomiyasu* — https://github.com/nanaism/yomiyasu (MIT)
- skills.sh — https://skills.sh

**本スキルのライセンス**：MIT（`SKILL.md` の `license` フィールドに記載）。ただし、参照した第三者スキルのライセンスは、それぞれのリポジトリに従う。本スキルには、第三者の原文・プロンプト・図表を大量に含めていない。
