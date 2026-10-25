# 講評テンプレートとJSON契約

## 人が読む審査レポート

### 受付カード
作品名／読了範囲（全文・部分）／本文の版／応募先・開催回／公式要項を確認した日とURL（または未確認）／採用プロファイル／ネタバレ範囲。

### 総評
- 一行判定（例：「語りが独創的だが、転換の因果が薄い」）。
- 最も評価した一場面と理由。
- 最大の懸念と、それが意図的な選択である可能性。

### 8軸採点表
8軸それぞれの満点・評点（全文だけ）・2つ以上の本文位置・得点理由・対抗解釈・確信度。合計は整数100点満点、比較のための目安。

### 模擬合議
言葉／設計／独創性／編集・読者の4役が、推す理由・落とす理由・評定が変わる条件を述べる。意見が割れた要素を具体的に書く。

### ゲートと提出可能性
資格ゲート：valid / invalid / unknown と規定上の根拠。
作品ゲート：critical / major / minor ごとの問題と位置、創作的対抗解釈。
仮想審査上の扱い：質的な所見に限り、応募後の順位や確率を示さない。

### 改稿優先順位
1. 変更すべき箇所／どの読書体験を改善するか／具体策／守るべき長所／修正後のチェック。
2. 同上。
3. 同上。
未確認事項、採点の不確実性、想定しうる反対選評を末尾に残す。

## 機械可読JSON

スクリプトが受け取る形式は次の例を参照。profile に対応する max は references/rubrics.md と scripts/validate_report.py に一致させる。scope=partial では全 score と total は null。full では整数得点と合計が必要。

主要フィールド：
- version：1.0.0
- profile：general / literary / entertainment / mystery / light-novel / short / web
- scope：full / partial
- title：文字列
- contest：{name, rules_url, rules_verified, eligibility}
- dimensions：8軸それぞれ {max, score, evidence:[{locator,excerpt,reason}], alternative, confidence}
- total：全文のみ整数
- panel：4役の {support,concern,change_condition}
- blockers：[{severity,locator,reason,alternative}]
- revision_priorities：[{locator,goal,edit,protect,check}]
- limitations：[文字列]

機械検証は形式・合計・最低限の根拠の有無を調べるだけ。本文と抜粋が本当に一致するか、審査意見の適否を証明しない。
