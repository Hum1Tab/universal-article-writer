# 任意のチャットAI・API・ローカルLLMで使う

## 方法 A：システムプロンプト / カスタム指示

1. `UNIVERSAL-PROMPT.md` を開く。
2. 全文をコピーし、AI の **system prompt**、**custom instructions**、**project instructions** のいずれかに貼る。
3. 文字数上限を超える場合は `UNIVERSAL-PROMPT-LITE.md` を使う。
4. 資料を添付するか、本文に貼る。
5. 依頼する。

```text
この論文を読んで、〇〇について論理的な記事を書いてください。
読者は△△、3000字。根拠と反論を含め、最後に監査結果を出してください。
```

## 方法 B：最初のメッセージに貼る

システムプロンプトを設定できないチャットでは、最初のメッセージにプロンプト全文を貼り、
その直後に依頼と資料を書く。

長い会話では、要所で次を reminder として送る。

```text
出典のない事実主張をしない。未確認は【未確認】と書く。
最強の反論と限界を残す。監査していないなら「未実行」と書く。
```

## 方法 C：API

```python
import os
from openai import OpenAI

prompt = open("UNIVERSAL-PROMPT.md", encoding="utf-8").read()
# vendor している場合は "universal-article-writer/UNIVERSAL-PROMPT.md"

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
response = client.chat.completions.create(
    model="YOUR_MODEL",
    temperature=0.3,
    messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": "この論文を読んで、〇〇について記事を書いてください。\n\n" + paper_text},
    ],
)
print(response.choices[0].message.content)
```

- 分析・監査では temperature を低め（0.2〜0.4）にする。
- 草案では中程度（0.6〜0.8）にする。
- 長い資料は、資料ごとに `S01`、`S02`… のIDを付けて渡す。

## 方法 D：ローカルLLM（Ollama、LM Studio など）

1. モデルのコンテキスト長を確認する。
2. **16k 未満**なら `UNIVERSAL-PROMPT-LITE.md`、**16k 以上**なら `UNIVERSAL-PROMPT.md` を使う。
3. システムプロンプトに貼る。
4. 資料は分割して渡し、各チャンクに `S01`… のIDを付ける。
5. 出力が切れる場合は、Phase ごとに分けて依頼する。

```text
Phase 1 だけ実行してください。資料を読み、出典台帳と検証状態を出してください。
```

## コンテキストが足りない場合

次の順で対処する。

1. `UNIVERSAL-PROMPT-LITE.md` に切り替える。
2. 資料を要約カードにする（各資料3〜5行、ID付き）。
3. Phase を分ける（収集 → 評価 → 設計 → 執筆 → 監査）。
4. それでも足りなければ、資料を絞る。網羅性より、主要主張の証拠を優先する。

## 注意

- ファイルを読めないAIは、添付資料の内容を推測することがある。「読めない場合は読めないと言う」と明示する。
- Web検索が無効なAIは、検索したふりをすることがある。「検索できない場合は資料を求める」と明示する。
- コード実行が無効なAIは、監査を実行したふりをすることがある。「実行できない場合は未実行と書く」と明示する。
- どのAIでも、最終的な書誌確認と専門家レビューは人間が行う。
