# 論理記事工房 — Agent Instructions

このリポジトリで、記事・論文・文献レビュー・ファクトチェック・論理監査・倫理/政策の論述を依頼されたら、
`UNIVERSAL-PROMPT.md` を読み、その指示に従う。

長い文脈が使えない場合は `UNIVERSAL-PROMPT-LITE.md` を使う。
Agent Skills に対応したホストなら `SKILL.md` を使う。

> このリポジトリのルートは `universal-article-writer` パッケージである。
> 別リポジトリに vendor する場合は、以下のパスを `universal-article-writer/...` に読み替える。

## 最低限の契約

- 出典のない事実主張を書かない。確認できなければ `【未確認】` と書く。
- 存在しない出典、DOI、URL、引用文、数値を捏造しない。
- 相関を因果に、非有意を「効果なし」に変換しない。
- 証拠を二重に数えない。同じデータを共有する論文は独立した証拠ではない。
- 最強の反論を書き、フレーム批判を1回は検討する。
- 価値前提を隠さない。「〜すべきだ」には、どの価値・原則・誰の負担を前提にしているかを書く。
- ユーザーの望む結論に合わせない。証拠と衝突するなら結論を弱める。
- 納品前に監査し、確認したことと確認していないことを分けて述べる。

## 出力

ファイルが使える場合は、作業ディレクトリに次を作る。

```text
article.md
sources.csv
claims.csv
dossier.md
logic-report.md
audit-report.json       # 監査を実行できた場合
argument-lint.json      # 監査を実行できた場合
source-report.json      # 監査を実行できた場合
```

ファイルが使えない場合は、回答内に「記事」「出典台帳」「主張台帳」「論理監査」「監査サマリー」「ドシエ」を順に出す。

## 監査

Python が使える場合：

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
  --out argument-lint.json

python scripts/verify_sources.py \
  --sources sources.csv \
  --article article.md \
  --out source-report.json
```

- `argument_lint.py --fail-on major` は、重大な推論の飛躍があれば終了コード 2 を返す。
- `verify_sources.py --online` は任意。ネットワークがない環境では実行しない。
- 実行できない場合は `UNIVERSAL-PROMPT.md` の「10. 完了前チェック」を手動で行い、
  「機械監査は未実行」と明記する。監査は意味内容を保証しない。

## 納品メッセージ

必ず次を含める。

1. 結論を1文。
2. 最も強い反論を1文。
3. 未解決の論点を1つ。
4. 論理監査の総合判定（1行）。
5. 規範的主張がある場合、明示した価値前提（1文）。
6. 生成したファイルのパス、または回答内の該当セクション。

## プロンプトが読めない場合

`UNIVERSAL-PROMPT.md` を読めない環境では、次の原則だけでも守る。

- 主張ごとに出典IDを付ける。
- 証拠の強さに合った表現を使う。
- 推論の型（演繹・帰納・因果・確率・規範）を意識し、飛躍を隠さない。
- 反論と限界を書く。
- 未確認を隠さない。
- 監査していないのに「完成」と言わない。
