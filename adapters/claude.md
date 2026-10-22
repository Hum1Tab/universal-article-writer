# Claude で使う

## 方法 A：Claude Projects（claude.ai）

1. 新しい **Project** を作る。
2. **Project knowledge** に次をアップロードする。
   - `UNIVERSAL-PROMPT.md`
   - `UNIVERSAL-PROMPT-LITE.md`
   - `references/`（任意）
   - `assets/`（任意）
3. **Project instructions** に次を貼る。

   ```text
   このプロジェクトでは「論理記事工房」を使う。
   回答前に Project knowledge の UNIVERSAL-PROMPT.md を読み、その指示に従う。
   ファイルが読めない場合は UNIVERSAL-PROMPT-LITE.md に従う。
   出典のない事実主張、捏造引用、未確認の隠蔽を禁止する。
   ```

4. 資料（PDF、URL、メモ）も Project knowledge に入れる。
5. 依頼する。

## 方法 B：Claude Code

1. このパッケージをプロジェクト内に置く。
2. プロジェクト直下に `CLAUDE.md` を作り、`AGENTS.md` の内容を貼るか、次を書く。

   ```markdown
   @AGENTS.md
   ```

   vendor している場合は `@universal-article-writer/AGENTS.md`。
   `@` インポートが使えない場合は、`AGENTS.md` の内容をそのまま `CLAUDE.md` に貼る。

3. Agent Skills として使う場合は、パッケージを次にコピーする。

   ```bash
   mkdir -p .claude/skills
   cp -R universal-article-writer .claude/skills/
   ```

   `SKILL.md` の `name` は `universal-article-writer` で、ディレクトリ名と一致している。

4. Claude Code に依頼する。

   ```text
   この論文を読んで、〇〇について論理的な記事を書いてください。
   読者は△△、3000字。根拠と反論を含め、最後に監査結果を出してください。
   ```

## 方法 C：通常のチャット

1. 最初のメッセージに `UNIVERSAL-PROMPT.md` を貼る。
2. 資料を添付する。
3. 依頼する。

長い文脈が使えない場合は `UNIVERSAL-PROMPT-LITE.md` を使う。

## 注意

- Claude は指示間の矛盾に敏感だが、長いプロンプトでは後半の規則を落とすことがある。依頼の最後に「絶対規則と完了前チェックを再確認して」と添える。
- PDF の表や図が読めない場合がある。数値は本文テキストでも渡す。
- Web検索が無効な場合、資料を求めさせる。検索したふりをさせない。
- 監査スクリプトを実行できない場合、`UNIVERSAL-PROMPT.md` の手動チェックを行わせる。
