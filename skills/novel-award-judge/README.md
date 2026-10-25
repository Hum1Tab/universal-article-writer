# Novel Award Judge — 小説審査SKILL

文学賞・新人賞の公開資料を参考に、**小説本文に根拠を残して採点・模擬合議・改稿提案を行う**独立型Agent Skill。既存の universal-article-writer を母体とし、その出典台帳・論理監査・赤チームの手法を文学批評に転用。

**これは実在の審査員による審査でも、賞の非公開配点の復元でもありません。受賞確率を予測しません。**

## 使い方
Agent Skills対応ホストでは、このディレクトリを .agents/skills/novel-award-judge や .claude/skills/novel-award-judge にコピーする。SKILL.md を読めば単独でも動作する。母体リポジトリの他の参照資料が読める場合は追加利用できる。

依頼例：
「この全文を群像新人文学賞を想定して厳しめに模擬審査して。原稿のどの文が加減点に効いたか、4役の選評と改稿トップ3を出して。」
「冒頭3000字の一次審査だけをして。全文の採点・受賞予測はしないで。」
「旧稿と新稿を同じ文学系ルーブリックでブラインド比較して。」

## ファイル
- SKILL.md：ルーティング、審査6フェーズ、禁止事項
- references/rubrics.md：7種の独自配点、8軸定義、アンカー
- references/research.md：公表方針の出典台帳・推論・反論・限界
- references/report-template.md：人が読む講評とJSON出力仕様
- scripts/validate_report.py：機械可読レポートの構造・採点合計検証
- examples/sample-report.json：架空の例示データ（実作品を採点していない）
- evals/README.md：挙動検証のテスト計画

## デザイン上の約束
全文を読まない限り総合点を出さない。文学性の異質さを欠陥と決めつけない。減点は本文位置と反対解釈を併記する。実際の応募条件は常に現在の公式募集要項を確認する。
