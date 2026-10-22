# Skill Landscape — 既存スキルの調査と v3.0 の設計根拠

> 調査日：2026-10-22。リポジトリの内容・名称・ライセンスは変更されうる。
> 本リポジトリは、以下のスキルの**構造・手順・失敗様式**を参考にし、文章は本リポジトリ用に新しく書いた。
> 原文・プロンプト・図表の大量コピーはしていない。再配布・商用利用の前に、各リポジトリの最新 LICENSE を確認すること。

---

## 1. 何を調べたか

「記事・論文を読み、論理的に書き、反論に耐える」ために必要な能力を、次の6系統に分けて調査した。

1. **スキルの規格・設計**（Agent Skills、skill-creator、評価）
2. **研究・文献レビュー**（検索、スクリーニング、PRISMA、メタ分析）
3. **論理・批判的思考**（標準形、誤謬、形式論理、論理監査）
4. **弁証法・反論**（Toulmin、背理法、内在的批判、反計画）
5. **方法知・意思決定**（確率、認識論、倫理、システム思考）
6. **学術執筆・査読**（IMRaD、引用、査読、投稿前チェック）

---

## 2. 調査したスキル・リポジトリ

| # | 名前 | 出典 | ライセンス（確認時点） | 主に参考にした要素 | v3 での扱い |
|---|---|---|---|---|---|
| 1 | Agent Skills 規格 | https://agentskills.io/ | 仕様 | SKILL.md、progressive disclosure、trigger description | 構造の基礎 |
| 2 | `anthropics/skills` | https://github.com/anthropics/skills | 混在（skill ごとに要確認） | skill-creator、評価、description 設計、docx/pdf 等 | スキル設計・評価 |
| 3 | `K-Dense-AI/scientific-agent-skills` | https://github.com/K-Dense-AI/scientific-agent-skills | MIT（個別 skill は要確認） | 証拠に紐づく執筆、文献レビュー、批判的思考、査読、来歴 | 証拠層・査読層 |
| 4 | `Imbad0202/academic-research-skills` | https://github.com/Imbad0202/academic-research-skills | 要確認 | research → write → review → revise → finalize のパイプライン | 学術モード |
| 5 | `timpara/opencode-academic-research` | https://github.com/timpara/opencode-academic-research | CC-BY-NC 4.0 | frame-lock、sycophancy、Concession Threshold、引用幻覚、段階的ゲート | 反論・監査 |
| 6 | `obra/superpowers` | https://github.com/obra/superpowers | 要確認（MIT と記憶） | brainstorming、verification-before-completion | 発散・完了ゲート |
| 7 | `mattpocock/skills` | https://github.com/mattpocock/skills | 要確認 | research、grilling、writing-shape、writing-beats、writing-fragments | 読解・構成・段落 |
| 8 | `Halfofthesky/logic-reasoning-skills` | https://github.com/Halfofthesky/logic-reasoning-skills | CC BY-NC-SA 4.0 | argument-analyst、24+ 誤謬、標準形、enthymeme の由来タグ、IBE の7美徳、formal-logic-solver | 論理エンジン |
| 9 | `zhujiaozi/logic-audit-skill` | https://github.com/zhujiaozi/logic-audit-skill | MIT | 13+ の誤謬、証拠等級 E0–E5、重大度の校正、修正論証チェーン、误报抑制 | 論理監査 |
| 10 | `ajitta/dialectic-skills` | https://github.com/ajitta/dialectic-skills | MIT | Toulmin + Walton の批判的質問、背理法、内在的批判、反例（Lakatos）、反計画、refine/iterate | 弁証法・反論 |
| 11 | `human-avatar/skills-for-humanity` (`s4h`) | https://github.com/human-avatar/skills-for-humanity | 要確認 | 200+ の方法、確率較正、認識論的地位、三角測量、倫理評議会、システム思考 | 方法知・価値層 |
| 12 | `O0000-code/meta-analysis-skill` | https://github.com/O0000-code/meta-analysis-skill | PolyForm-NC + CC BY-NC-SA 4.0 | PRISMA 2020、GRADE、AMSTAR 2、二重スクリーニング、7つの人間ゲート、R による赤信号、引用検証 | 統合エンジン |
| 13 | `ysskrishna/ai-agent-skills` | https://github.com/ysskrishna/ai-agent-skills | MIT | 方法の選択、critical-thinking、ethical-thinking、pre-mortem、trade-off | モード選択 |
| 14 | `miketepUR/awesome-claude-skills` | https://github.com/miketepUR/awesome-claude-skills | 要確認（リスト） | スキルの分類、実装例の探索 | 調査入口 |
| 15 | `skills.sh` | https://skills.sh | レジストリ | 配布・インストールの慣行 | 配布 |
| 16 | `scientific-writing` | K-Dense 内 | MIT | 証拠との結び付け、不確実性、盗用・捏造防止 | 執筆 |
| 17 | `literature-review` | K-Dense 内 | MIT | 系統的検索、スクリーニング、テーマ統合 | 統合 |
| 18 | `scientific-critical-thinking` | K-Dense 内 | MIT | デザイン、バイアス、統計・因果の批判 | 証拠評価 |
| 19 | `hypothesis-generation` | K-Dense 内 | MIT | 主張タイプ、代替説明、反証条件 | 論証 |
| 20 | `citation-management` | K-Dense 内 | MIT | DOI/PMID/arXiv の検証、BibTeX | 書誌 |
| 21 | `peer-review` / `scholar-evaluation` | K-Dense 内 | MIT | Major/Minor、査読形式、スコアの誤用防止 | 監査 |
| 22 | `academic-paper` / `academic-paper-reviewer` | ARS 系 | CC-BY-NC 4.0 | IMRaD、Devil's Advocate、投稿前チェック | 学術 |
| 23 | `deep-research` | ARS / 各種 | 要確認 | 多段の調査、検索ログ、反証探索 | 調査 |
| 24 | `consciousness-council` | K-Dense 内 | MIT | 多視点の赤チーム、フレーム批判 | 赤チーム |
| 25 | `writing-shape` / `writing-beats` / `writing-fragments` | mattpocock | 要確認 | 概念のグラウンディング、1段落1仕事、断片からの構成 | 表現層 |
| 26 | `better-writing` / `brand-guidelines` / `internal-comms` | 各種 | 要確認 | 声のダイヤル、媒体適応、保存チェック | 声・媒体 |
| 27 | `verification-before-completion` | obra/superpowers | 要確認 | 証拠なき完了宣言の禁止 | 完了ゲート |
| 28 | `skill-creator` | anthropics/skills | 要確認 | description、評価、progressive disclosure | スキル設計 |

**「要確認」**：設計時に LICENSE を確認しきれなかったもの。本リポジトリはこれらの文章をコピーしていないが、再配布・商用利用の際は必ず原リポジトリの LICENSE を確認すること。
**CC-BY-NC / CC-BY-NC-SA**：非商用・継承の条件がある。本リポジトリは概念のみを参照し、原文を収録していない。商用利用を検討する場合は法的確認が必要である。

---

## 3. 見つかった設計パターン

### 3.1 スキル構造

- **progressive disclosure**：SKILL.md は短く、詳細は `references/` に置く。必要なときだけ読む。
- **trigger description**：ユーザーの言い回しを description に埋め込み、発火条件を明確にする。
- **単体で動く**：外部スキルがなくても完結する。外部スキルは追加視点。
- **評価ケース**：must_do / must_not_do / artifacts / pass condition を持つ。
- **スクリプト回帰**：正常系・異常系・欠落系を CI で検証する。

### 3.2 研究・統合

- **検索ログ**：検索式・日付・件数・データベースを残す。
- **二重スクリーニング**：独立2名、不一致の解消、κ の記録。
- **PRISMA 2020**：同定・スクリーニング・適格・採用の数。
- **GRADE / RoB 2 / ROBINS-I / AMSTAR 2**：デザインのラベルではなく、バイアス・非一貫性・非直接性・不精確さ・出版バイアスで評価する。
- **来歴ゲート**：数値・引用・変換式を、元データまで遡れるようにする。
- **人間の署名ゲート**：不可逆な判断の前に、人間が確認する。

### 3.3 論理・反論

- **標準形**：結論・前提・暗黙前提を分ける。
- **由来タグ**：`[TEXT]` / `[CONV]` / `[ANALYST]`。補った前提の責任を明示する。
- **charity ceiling**：相手の論証を強くしすぎない。
- **誤謬の「誤謬でない場合」**：過剰検出を防ぐ。
- **Toulmin + Walton**：Warrant と批判的質問をセットにする。
- **反例・背理法・内在的批判**：結論を壊す手続きを複数持つ。
- **Concession Threshold**：反論の強さを数値化し、連続譲歩を防ぐ。
- **frame-lock 検査**：問いの前提を疑う。

### 3.4 方法知・価値

- **方法の層**：知識でもツールでもなく「どう考えるか」を手順化する。
- **確率較正**：言葉の強さと確率の目安を対応させる。
- **認識論的地位**：知っている／信じている／仮定している／願っているを分ける。
- **三角測量**：独立した情報源で確認する。増幅と裏付けを区別する。
- **倫理評議会**：複数の規範理論で同じ問題を見る。
- **反計画（counterplan）**：同じ事実から、反対の前提で最良の代替案を作る。

### 3.5 監査

- **engine-computed red flags**：LLM の目視ではなく、スクリプトが数値から判定する。
- **重大度の校正**：情報欠落を重大度に混ぜない。過剰検出を抑える。
- **修正論証チェーン**：指摘だけでなく、修正後の論証を出す。
- **verification-before-completion**：監査していないのに「完了」と言わない。

---

## 4. v2.1 のギャップ

| 領域 | v2.1 の状態 | 問題 |
|---|---|---|
| 論理 | Toulmin と誤謬の一覧はあるが、形式妥当性・必要条件/十分条件・量化子・確率・因果識別が薄い | 「論理的」と言いながら、飛躍の型を特定できない |
| 統合 | 文献レビューの手順はあるが、証拠の独立性・メタ分析・GRADE・出版バイアスが薄い | 論文数を証拠数と誤認する |
| 規範 | 事実と価値の分離はあるが、倫理理論・政策分析・概念分析の手順がない | 倫理・哲学・政策の記事が「意見」になる |
| 分業 | 5役の赤チームはあるが、読解・抽出・統合・規範の役割分担がない | 大量資料で視点が混ざる |
| 機械監査 | 引用・主張・表現の監査のみ | 推論の飛躍と書誌の形式を検出できない |
| 評価 | 15ケース。論理・規範・統合のケースがない | 改善を回帰テストできない |
| バージョン | SKILL.md 2.1.0 / scripts 2.0.0 / evals 2.0.0 | リポジトリ内で不整合 |

---

## 5. v3.0 の設計

### 5.1 4つのエンジン

| エンジン | ファイル | 役割 |
|---|---|---|
| 論理 | `references/logic-and-inference.md` | 標準形、演繹・帰納・因果・確率・ACH、誤謬と修復 |
| 統合 | `references/knowledge-synthesis.md` | 多資料読解、独立性、PRISMA、メタ分析、不一致 |
| 規範 | `references/normative-and-conceptual.md` | 価値前提、倫理理論、政策、概念分析、文化 |
| 分業 | `references/orchestration.md` | 役割、ハンドオフ、並列化、長文脈、停止規則 |

### 5.2 3つのスクリプト

| スクリプト | 役割 | 出力 |
|---|---|---|
| `audit_article.py` | 引用・主張・表現・構造の監査 | `audit-report.json` |
| `argument_lint.py` | 相関→因果、非有意→効果なし、一般化、誤謬、規範的主張の監査 | `argument-lint.json` |
| `verify_sources.py` | 書誌形式、重複、DOI/URL、撤回、本文引用の監査 | `source-report.json` |

### 5.3 7つのゲート

G0 受付、G1 問いと結論、G2 証拠、G3 論理、G4 反論、G5 文章と読者、G6 完全性、G7 価値・規範。

### 5.4 評価

- 22の行動ケース（E01–E22）。論理・確率・因果・統合・規範・概念・迎合耐性を追加。
- 7つのスクリプト回帰（R01–R03、R06–R09）。

---

## 6. 採用しなかったもの

| 採用しなかったもの | 理由 |
|---|---|
| 完全自律の研究パイプライン | 人間の確認なしに論文を生成すると、捏造・フレームロック・引用幻覚のリスクが高い |
| 38エージェントの固定パイプライン | 小規模な記事には過剰 |
| 学術誌の0〜100点スコア | スコアが独り歩きし、Critical を平均で薄める |
| 特定の引用スタイルへの固定 | ユーザーの指定に従う |
| 長大なプロンプトの埋め込み | 保守が難しい。references に分ける |
| AI 検出器による判定 | 誤検知が多く、証拠にならない |
| 「人間らしく見せる」書き換え | 目的は品質であり、AI 利用の隠蔽ではない |
| メタ分析の自動実行 | 統計的妥当性の判断は人間の専門家が必要 |

---

## 7. 帰属

本リポジトリは、次のプロジェクトの知見に感謝する。

- Anthropic, *Agent Skills* — https://agentskills.io/ / https://github.com/anthropics/skills
- K-Dense AI, *Scientific Agent Skills* — https://github.com/K-Dense-AI/scientific-agent-skills (MIT)
- Matt Pocock, *skills* — https://github.com/mattpocock/skills
- Jesse Vincent, *Superpowers* — https://github.com/obra/superpowers
- Cheng-I Wu, *Academic Research Skills* — https://github.com/Imbad0202/academic-research-skills
- timpara, *opencode-academic-research* — https://github.com/timpara/opencode-academic-research (CC-BY-NC 4.0)
- Halfofthesky, *Logic & Reasoning Skills* — https://github.com/Halfofthesky/logic-reasoning-skills (CC BY-NC-SA 4.0)
- zhujiaozi, *Logic Audit Skill* — https://github.com/zhujiaozi/logic-audit-skill (MIT)
- ajitta, *Dialectic Skills* — https://github.com/ajitta/dialectic-skills (MIT)
- human-avatar, *skills-for-humanity* — https://github.com/human-avatar/skills-for-humanity
- O0000-code, *meta-analysis-skill* — https://github.com/O0000-code/meta-analysis-skill (PolyForm-NC + CC BY-NC-SA 4.0)
- ysskrishna, *Thinking Methods* — https://github.com/ysskrishna/ai-agent-skills (MIT)
- skills.sh — https://skills.sh

**本リポジトリのライセンス**：MIT。ただし、参照した第三者スキルのライセンスは、それぞれのリポジトリに従う。本リポジトリには、第三者の原文・プロンプト・図表を大量に含めていない。
