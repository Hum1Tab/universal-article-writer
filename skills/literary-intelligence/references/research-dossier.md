# 調査ドシエ — Literary Intelligence

調査日：2026-10-26。目的：「小説の品質を唯一の点に還元せず、
文学的論証の精度と再検討可能性を最大化できるか」。
以下はこの日実際に見られた大学・出版社・学術論文の本文／書誌・抄録情報を使う。
「全文確認」ではなく、少なくともリンク先ページと抄録／概要を確認した状態。
一次研究でも全文精読していない場合、細部を事実として捏造しない。

## 出典台帳
| ID | 著者・機関／題名 | 確認した範囲 | URL |
|---|---|---|---|
| S01 | Cambridge Companion, Narrative Theory’s Longue Durée (story/discourse) | 論集章の概要 | https://www.cambridge.org/core/books/cambridge-companion-to-narrative-theory/narrative-theorys-longue-duree/D746AC4DF357E6A0D6CB86B4CE3D360F |
| S02 | Hamburg University, Living Handbook of Narratology (Meister) | 大学による概要・Narratology項 | https://www.slm.uni-hamburg.de/en/iaa/forschung/forschungsprojekte/handbook-of-diachronic-narratology.html |
| S03 | James Phelan, Narrative as Rhetoric, OSU Press | 出版社の書籍紹介 | https://ohiostatepress.org/books/BookPages/PhelanNarrative.htm |
| S04 | Routledge Encyclopedia of Modernism, Viktor Shklovsky | 学術百科事典の項目 | https://www.rem.routledge.com/articles/shklovsky-viktor-1893-1984 |
| S05 | Miall & Kuiken (1994), Foregrounding, defamiliarization, and affect | Poetics原著抄録、DOI | https://doi.org/10.1016/0304-422X(94)00011-5 |
| S06 | Internet Encyclopedia of Philosophy, Art and Interpretation | 論考ページ・対立する解釈論 | https://iep.utm.edu/art-and-interpretation/ |
| S07 | Stanford Encyclopedia of Philosophy, The Concept of the Aesthetic | 2026年改訂の論考ページ | https://plato.stanford.edu/entries/aesthetic-concept/ |
| S08 | Stanford Humanities Center, The Locations of Value(s) | 公開論考の要旨 | https://shc.stanford.edu/arcade/publications/dibur/locations-values/locations-values-introduction |
| S09 | Green & Brock (2000), Narrative Transportation | 心理学誌原著抄録 | https://pubmed.ncbi.nlm.nih.gov/11079236/ |
| S10 | Busselle et al. (2019), Narrative Engageability Scale | 著者・誌面概要 | https://ijoc.org/index.php/ijoc/article/view/8624 |
| S11 | Panero et al. (2016), attempted replication | PubMed原著抄録、792人の追試 | https://pubmed.ncbi.nlm.nih.gov/27642659/ |
| S12 | Kidd & Castano (2018/2019), preregistered replications | 誌面抄録、結果混合 | https://doi.org/10.1177/1948550618775410 |
| S13 | Four replications of fiction and mentalizing (2017) | PubMed原著抄録、計1006人 | https://pubmed.ncbi.nlm.nih.gov/28095740/ |
| S14 | Bizzoni et al. (2024), A Matter of Perspective | ACL Anthology論文ページ・抄録 | https://aclanthology.org/2024.lrec-main.71/ |
| S15 | Feldkamp et al. (2024), Measuring Literary Quality | Journal of Computational Literary Studies概要 | https://doi.org/10.48694/jcls.3908 |
| S16 | Fein et al. (2026), LitBench | EACL/ACL Anthology論文ページ・抄録 | https://aclanthology.org/2026.eacl-long.362/ |
| S17 | Lu et al. (2026), Rethinking Creativity Evaluation | EACL/ACL Anthology論文ページ・抄録 | https://aclanthology.org/2026.eacl-long.297/ |
| S18 | Zheng et al. (2023), Judging LLM-as-a-Judge | NeurIPS論文概要 | https://arxiv.org/abs/2306.05685 |
| S19 | ETS, Building and Justifying Interpretations of Texts (2020) | 学術報告抄録・解釈方法の記述 | https://doi.org/10.1002/ets2.12304 |
| S20 | University of Toronto, Critical Reading Towards Critical Writing | 大学の解説本文 | https://advice.writing.utoronto.ca/researching/critical-reading/ |
| S21 | Shi et al. (2025), Position Bias in LLM-as-a-Judge | ACL Anthology公開論文・抄録 | https://aclanthology.org/2025.ijcnlp-long.18/ |
| S22 | Bizzoni et al. (2024), Global Coherence, Local Uncertainty | 会議サイト抄録（短報、探索的） | https://2024.computational-humanities-research.org/papers/paper36/ |

S11/S12/S13は独立した研究集団・研究計画を含むが、同じ発端となる研究上の
問いを追っている点には注意。独立証拠の単純な票数としない。

## 主張台帳（文献の主張と本SKILL独自の設計を分離）

C01 TEXT THEORY: Storyとdiscourseの区別は物語分析の中核（S01,S02）。
DESIGN: 本SKILLでは両者の台帳を分離。これは有効性が実証された採点式ではない。

C02 RHETORICAL THEORY: 誰が誰に語るか、目的・認知・感情・価値判断を
同時に考えるモデルがある（S03）。DESIGN: 読者への判断の誘導を審査。

C03 FORMALISM: 異化は知覚の自動化をずらす（S04）。1994年の短編
読解研究では前景化と読書時間・印象・感情評定に関連（S05）。
LIMIT: 作品普遍の有効性や因果一般化はしない。

C04 HERMENEUTICS: 意図主義と反意図主義の緊張、文学の多義性（S06）。
DESIGN: 意図を観測できないときは「テキストの試み」と表記し、
複数の読解を競わせる。

C05 AESTHETIC: 美的価値には異論ある理論群が存在（S07,S08）。
DESIGN: 価値前提を宣言し、単一最大化関数を既定値にしない。
唯一の本質的尺度が絶対存在しないと科学的に証明した、とは言わない。

C06 READER-EMPIRICAL: 没入は注意・イメージ・感情に関わる（S09）、
読者の没入しやすさにも複数次元がある（S10）。
反面、短い文学的フィクションから心の理論が即座に向上するかは
追試により混合・否定的結果（S11,S12,S13）。
DESIGN: 実測していない感情効果を断定しない。

C07 RECEPTION: 英語圏の小説コーパスを対象とする研究では
専門家・大衆的な評価指標に差がある（S14,S15）。
DESIGN: 読者人気・受賞・正典を「美的価値」そのものとしない。

C08 LLM-META: LitBenchの特定条件で既製審査LLMの最良は
人間の対比較選好との一致が73%（S16）。創造性指標には
領域間不一致（S17）、LLM審査には位置・冗長性のバイアス（S18,S21）。
DESIGN: blind / role decomposition / 順序逆転 / 引用検証。
LIMIT: これらは本SKILLの性能保証・客観的文学尺度ではない。

C09 SCHOLARLY PRACTICE: 文学的読解にはパターン、異常、解釈の問題、
反復的再読、文脈、独自の本文根拠づけが含まれる（S19,S20）。
DESIGN: 評価カードに根拠・反対読解・修正可能性を必須化。

C10 EXPLORATORY: 局所の予測不能性と大局の整合を組み合わせる探索的研究（S22）。
DESIGN: 読者の意外さと物語の一貫性を対立させず両面を見る。
LIMIT: これをすべての小説に対する高品質の数式や新規性メトリクスとしない。

## 強い反対論
A「点を拒否すると実用性がない」：反論はもっとも。0〜4アンカーを
任意で提供する。ただし疑似精度を減らすため合計せず、根拠つきプロファイルを優先。

B「作者の意図が分からなければ内在的目的は評価不能」：作者意図は
未観測だが作品自身に反復・選択・位置という公開証拠がある。
作品が作る可能な読書経験に焦点を移し、異なる仮説を競わせる。

C「読者反応研究を取り込めば普遍的な良し悪しが測れる」：研究は
特定実験条件の傾向。作品・言語・集団・時代が違えば外挿は危険。

D「ポスト構造主義や倫理批評を入れたらどの読みも等価になる」：
等価ではない。本文証拠と反例で読みの強さを比較し、残る価値の対立は明記する。

E「文学性が測れないなら理論エンジン自体に意味はない」：
唯一のスコアを生む装置でなく、評価の理由を監査・更新する装置として
価値を位置付ける。ただし「この装置が人間より高精度」という証拠はない。

## 未検証の重要事項
- 各原著論文の全文の体系的レビューは未実施。抄録の外の細かな方法・効果量は言わない。
- 日本語の現代小説における信頼性・妥当性の独立検証は未実施。
- 著名作品と無名作品、翻訳文と原語文、不同文化・ジャンルでの安定性は不明。
- 本SKILLのユーザビリティ改善や人間評価一致率は実際にテストする必要がある。
- 数値プロフィールQ1〜Q10の重みはデータから推定していない。全て同一に足す設計は拒否。

## 論理監査の総括
結論：本文根拠＋反対読解＋価値前提を公開する設計は、
作品の批評を検証可能なものに近づける。
最強の反論：どんな基準でも小説の価値を完全に定義できない。
残された問い：創作形態と言語をまたぐ採点者間の一致率と、
既存の文学的評価バイアスをどの程度減らせるか。
本SKILLの品質・一致率の検証は未実施である。
