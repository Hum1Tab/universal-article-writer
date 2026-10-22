# Gemini で使う

## 方法 A：Gem（gemini.google.com）

1. **Gems → New Gem** を開く。
2. **Instructions** に `UNIVERSAL-PROMPT-LITE.md` を貼る。
   - 文字数上限を超える場合は、次の短い指示だけを貼る。

     ```text
     回答前に、添付ファイルの UNIVERSAL-PROMPT.md を読み、その指示に従う。
     出典のない事実主張、捏造引用、未確認の隠蔽を禁止する。
     監査できない場合は「機械監査は未実行」と明記する。
     ```

3. **Knowledge / Files** に `UNIVERSAL-PROMPT.md`、`references/`、`assets/` をアップロードする。
4. 必要に応じて Google 検索やコード実行を有効にする。
5. 依頼する。

## 方法 B：Google AI Studio

1. 新しいプロンプトを作る。
2. **System instructions** に `UNIVERSAL-PROMPT.md` を貼る。
3. 資料をファイルまたはテキストで渡す。
4. Temperature は分析・監査なら低め（0.2〜0.4）、草案なら中程度（0.6〜0.8）にする。
5. 実行する。

## 方法 C：Gemini CLI

1. プロジェクト直下に `GEMINI.md` を作る。
2. `AGENTS.md` の内容を貼るか、次を書く。

   ```markdown
   @AGENTS.md
   ```

   vendor している場合は `@universal-article-writer/AGENTS.md`。

3. Gemini CLI を起動し、記事作成を依頼する。

## 方法 D：通常のチャット

1. 最初のメッセージに `UNIVERSAL-PROMPT.md` を貼る。
2. 資料を添付する。
3. 依頼する。

## 注意

- Gemini は検索結果を混ぜて回答することがある。引用ごとに「どの資料のどこか」を書かせる。
- 長い PDF は分割されることがある。頁番号を指定して引用させる。
- コード実行が使えない場合、監査スクリプトの実行を装わせない。「未実行」と明記させる。
- Gem の指示欄は文字数上限が厳しいことがある。Lite か、ファイル参照方式を使う。
