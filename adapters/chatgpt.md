# ChatGPT で使う

## 方法 A：プロジェクト（おすすめ）

1. ChatGPT の **Projects** で新しいプロジェクトを作る。
2. **Project instructions** に次を貼る。

   ```text
   このプロジェクトでは「論理記事工房」を使う。
   回答前に、添付された UNIVERSAL-PROMPT.md を読み、その指示に従う。
   ファイルが読めない場合は UNIVERSAL-PROMPT-LITE.md に従う。
   出典のない事実主張、捏造引用、未確認の隠蔽を禁止する。
   ```

3. **Project files** に次をアップロードする。
   - `UNIVERSAL-PROMPT.md`
   - `UNIVERSAL-PROMPT-LITE.md`
   - `references/`（任意。深いレビューに使う）
   - `assets/`（任意。出力テンプレート）
4. 必要に応じて **Web search** と **Code interpreter / Python** を有効にする。
5. 記事を依頼するときは、資料（PDF、URL、メモ）も同じプロジェクトに添付する。

## 方法 B：Custom GPT

1. **Explore GPTs → Create** を開く。
2. **Configure → Instructions** に `UNIVERSAL-PROMPT-LITE.md` を貼る。
   - 指示欄の文字数上限を超える場合は、次の短い指示だけを貼る。

     ```text
     回答前に、Knowledge の UNIVERSAL-PROMPT.md を読み、その指示に従う。
     出典のない事実主張、捏造引用、未確認の隠蔽を禁止する。
     監査できない場合は「機械監査は未実行」と明記する。
     ```

3. **Knowledge** に `UNIVERSAL-PROMPT.md`、`references/`、`assets/` をアップロードする。
4. Web Browsing と Code Interpreter を必要に応じて有効にする。
5. 動作確認として、次を聞く。

   ```text
   次の主張を監査してください。結論、最強の反論、未確認事項を分けてください。
   「在宅勤務は生産性を必ず上げる」
   ```

## 方法 C：通常のチャット

1. 最初のメッセージに `UNIVERSAL-PROMPT.md` の全文を貼る。
2. その直後に依頼と資料を書く。
3. 長いセッションでは、要所で次を reminder として送る。

   ```text
   出典のない事実主張をしない。未確認は【未確認】と書く。
   最強の反論と限界を残す。
   ```

## 注意

- 指示欄の文字数上限はプラットフォーム側で変わる。超えたら、**ファイルをアップロードして短い指示から参照させる**方式に切り替える。
- Web検索が無効な場合、ChatGPT は検索したふりをすることがある。必ず「検索できない場合は資料を求める」と指示する。
- アップロードしたファイルを読めない場合、ChatGPT は内容を推測することがある。「読めない場合は読めないと言う」と明示する。
- 生成した `sources.csv` や `claims.csv` は、チャット上では表またはコードブロックで出させる。
