# Report Contract — 出力の仕様

## 通常出力

1. Scope: 作品名、版、全文or抜粋、実際の読み取り範囲、使用理論、作者情報を採点に使用したか。
2. Artistic hypotheses: 作品固有の目的の解釈を2〜3種類。本文で支持する箇所、代替。
3. Story map / Discourse map: 物語上の出来事と提示の技法を分離。
4. Claims: [TEXT] → [INTERPRETATION] → [VALUE PREMISE] → [EVALUATION]。
   最重要3〜7件は根拠位置、短い正確な引用、対抗読解、結論の限界。
5. 8レンズのトレードオフ（適用するものだけを記録、非適用に説明）。
6. Literary profile: Q1〜Q10、根拠、strong/mixed/limited/unknown、
   好意的解釈、厳しい解釈の最も強い衝突。
7. Possible reader experiences: テキストからの仮説と実測の分離。
8. Counterfactual edits: 改稿上位3つ、残すべき長所、改善の副作用。
9. Limits: 未読部分、未検証外部資料、解釈差、結論が変わる条件。

総評は「何が作品特有の達成で、何を犠牲にしているか」を1文に。
「面白かった」だけでは評価と呼ばない。
比較の場合は単一総合点の代わりに価値体系ごとの比較と逆転箇所を提出。

## JSON出力（スクリプト検証に対応）

- schema_version: "1.0.0"
- title: 文字列
- coverage: full または partial
- numeric_requested: boolean
- evidence: 配列。各レコード {id, locator, quote, observation, area}
- claims: 配列。{id, type, claim, evidence_ids, warrant, value_premise,
  counterreading, status, confidence, change_condition}
- quality: Q1..Q10のobject。各{status, rationale, evidence_ids, score, confidence}
  status は strong/mixed/limited/not_applicable/unknown。
  数値なしならscore=null。数値ありなら0..4整数かnull（not_applicable/unknown）。
- lenses: 配列。各{id, applicable, reasoning, opposing_reasoning}
- reader_effects: 配列。各{claim, kind, evidence_ids, measured_source}
  kind = predicted または measured。predictedならmeasured_source=null。
- revisions: 配列。各{locator, goal, proposal, preserved_strength, tradeoff, test}
- limitations: 文字列の配列
- universal_score: null 以外を認めない

JSONバリデータで検証すること:
- 参照した evidence_id が存在する
- 作品を読み切ったと偽ることをシステムは自動検出できないので、coverageは自己申告
- quote が原稿全文の文字列に実在するか --manuscript があれば機械検証
- 値の誤りと矛盾する score/status などを検出
- 文学的評価の真偽や著者意図の実在は機械検証しない

実装例は examples/sample-report.json。検証:
python scripts/validate_report.py examples/sample-report.json --manuscript examples/manuscript.txt
