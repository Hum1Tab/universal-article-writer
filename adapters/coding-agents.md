# コーディングエージェントで使う

Codex、Claude Code、Cursor、GitHub Copilot、Windsurf、Cline、Roo Code、Gemini CLI、OpenCode など、
リポジトリの指示ファイルを読むエージェント向け。

## 共通の置き方

> このリポジトリ自体を作業ディレクトリにする場合は、以下の `universal-article-writer/`
> を付けない。別プロジェクトに vendor する場合だけ、パスを `universal-article-writer/...`
> に読み替える。

1. このパッケージをプロジェクト内に置く（vendor する場合）。
2. エージェントが読む指示ファイルに、次を書く。

   ```markdown
   記事・論文・文献レビュー・ファクトチェック・論理監査を依頼されたら、
   UNIVERSAL-PROMPT.md を読み、その指示に従う。
   長い文脈が使えない場合は UNIVERSAL-PROMPT-LITE.md を使う。
   ```

3. 監査スクリプトが使える場合：

   ```bash
   python scripts/audit_article.py \
     --article article.md \
     --sources sources.csv \
     --claims claims.csv \
     --out audit-report.json
   ```

   vendor している場合は `python universal-article-writer/scripts/audit_article.py`。

## エージェント別のファイル

| エージェント | 指示ファイル |
|---|---|
| Codex | `AGENTS.md`（プロジェクト直下） |
| OpenCode | `AGENTS.md`（プロジェクト直下） |
| Claude Code | `CLAUDE.md`（`@AGENTS.md`。vendor 時は `@universal-article-writer/AGENTS.md`） |
| Gemini CLI | `GEMINI.md` |
| Cursor | `.cursor/rules/article-writer.mdc` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Windsurf | `.windsurf/rules/article-writer.md` または `.windsurfrules` |
| Cline | `.clinerules` |
| Roo Code | `.roo/rules/article-writer.md` |

## Cursor のルール例

`.cursor/rules/article-writer.mdc`：

```markdown
---
description: 論理記事工房 — 証拠と論証に基づく記事執筆
globs: ["**/*.md"]
alwaysApply: false
---

記事・論文・文献レビュー・ファクトチェック・論理監査を依頼されたら、
UNIVERSAL-PROMPT.md を読み、その指示に従う。
出典のない事実主張、捏造引用、未確認の隠蔽を禁止する。
```

vendor している場合は `UNIVERSAL-PROMPT.md` を
`universal-article-writer/UNIVERSAL-PROMPT.md` に読み替える。

## GitHub Copilot の例

`.github/copilot-instructions.md`：

```markdown
記事・論文・文献レビュー・ファクトチェック・論理監査を依頼されたら、
UNIVERSAL-PROMPT.md を読み、その指示に従う。
出典のない事実主張、捏造引用、未確認の隠蔽を禁止する。
監査できない場合は「機械監査は未実行」と明記する。
```

vendor している場合は `UNIVERSAL-PROMPT.md` を
`universal-article-writer/UNIVERSAL-PROMPT.md` に読み替える。

## 注意

- エージェントは指示ファイルを毎回読むとは限らない。依頼時にも「UNIVERSAL-PROMPT.md を読んで」と明示する。
- エージェントがファイルを読めない場合、`AGENTS.md` の「最低限の契約」だけでも守らせる。
- 生成した記事は Git 管理下に置き、差分をレビューする。
- 監査スクリプトを CI に入れる場合は、`--strict` の扱いを決める。`--strict` は `CONDITIONAL` でも終了コード 2 を返す。
