# Launch guide

This is a practical checklist for publishing the repository and giving it a fair
chance of being discovered. Stars are a lagging indicator of usefulness; the
goal is to make the value obvious in the first 30 seconds.

## 1. Repository metadata

| Setting | Recommended value |
|---|---|
| Repository name | `universal-article-writer` |
| Description | `Evidence-first article writing for any AI: source ledger, claim–evidence matrix, red-team review, citation audit. Works with ChatGPT, Claude, Gemini, Codex, Cursor, and local LLMs.` |
| Website | Leave blank until there is a demo page. |
| Topics | `ai`, `writing`, `prompt-engineering`, `llm`, `agents`, `research`, `citations`, `fact-checking`, `critical-thinking`, `chatgpt`, `claude`, `gemini`, `codex`, `productivity` |
| Social preview | Upload `assets/social-preview.png` (or the SVG source if PNG is unavailable). |
| Discussions | Enable, with categories for “Show your output”, “Adapters”, and “Evals”. |
| Issues | Enable bug and feature templates. |
| License | MIT (already in `LICENSE`). |

## 2. README above the fold

The first screen should answer:

1. **What is this?** A portable, evidence-first writing protocol.
2. **Who is it for?** Researchers, analysts, writers, and coding-agent users who
   need defensible articles, not just fluent text.
3. **Why now?** Citation fabrication and sycophancy are documented, measurable
   failure modes. A longer prompt alone does not fix them.
4. **What is different?** External ledgers, red-team review, gates, audit.
5. **How do I try it in 60 seconds?** Copy the prompt, attach a source, ask for a
   quick article.

The current READMEs are structured for this. Keep them in sync.

## 3. Release

Create a GitHub release `v3.0.0` with:

- title: `v3.0.0 — Logic-First Edition`
- short summary: any AI, seven phases, 4 engines, 7 gates, 3 audits, 22 evals
- link to `CHANGELOG.md`
- attach `UNIVERSAL-PROMPT.md` and `UNIVERSAL-PROMPT-LITE.md` as release assets
- note the known limitations and the manual-audit fallback

Tags and releases make the project look maintained. A stale repository loses
trust quickly.

## 4. Launch posts

Tailor each post. Do not paste the same announcement everywhere.

### Show HN

> **Show HN: Evidence-first article writing for any AI**
>
> I kept seeing the same failure: a model writes a confident article, and the
> citations are either fabricated or don't support the sentence. The research is
> grim — one 2023 study found 18% of GPT-4 citations were fabricated, and 24% of
> the real ones had substantive errors.
>
> This is a portable writing protocol, not a prompt pack. It makes the model
> externalize sources and claims, audit the inference, build a Toulmin argument
> map, run a six-role red-team review, and pass three deterministic audits before
> delivery. It works in chat, API, and coding-agent hosts, with explicit fallbacks
> when files/search/code are unavailable.
>
> The repo includes standard-library audit scripts, 22 behavioral eval cases,
> examples, and an honest evidence page that separates research findings from
> design claims. I'd especially value feedback on the eval design and on hosts
> where the protocol breaks.

### Reddit (r/LocalLLaMA, r/ClaudeAI, r/ChatGPT)

Use a title like “I built a portable evidence-first writing protocol for LLMs —
looking for failure cases.” Lead with the problem and a concrete before/after.
Link the repo once. Answer questions; do not post the same text in five
subreddits on the same day.

### X / LinkedIn

Short thread:

1. The failure: fluent article, fake citation.
2. The evidence: Walters & Wilder 2023; sycophancy; self-correction limits.
3. The mechanism: source ledger → claim matrix → argument map → red team → audit.
4. The demo: a real audit report.
5. The ask: try it on one source and tell me where it breaks.

### Japanese

Zenn / Qiita / note:

> **AIに記事を書かせる前に、証拠を台帳にしませんか**
>
> GPT-4でも参考文献の18%が捏造だったという研究があります。このリポジトリは、
> 出典台帳・主張台帳・論証マップ・赤チーム監査・引用監査を組み合わせた、
> どのAIでも使える記事執筆プロトコルです。プロンプト集ではなく、検証可能な
> 仕組みとして設計しました。22の評価ケースと、依存なしの監査スクリプト3本を同梱
> しています。

### Chinese

知乎 / 掘金:

> **别让 AI 直接写文章：一个可移植的“证据优先”写作协议**
>
> 研究显示，GPT-4 生成的参考文献中仍有约 18% 是虚构的；即使引用真实存在，
> 也有约 24% 包含实质性错误。这个项目把来源台账、主张—证据矩阵、论证地图、
> 红队审查和引用审计组合成一套可在任意 AI 上运行的写作流程。它不是提示词合集，
> 而是一套可检查、可复现的机制。

## 5. Distribution that is not spam

- Add the project to relevant “awesome” lists only if it genuinely fits their
  criteria. Follow each list's contribution rules.
- Share a concrete example, not just the repo link.
- Answer questions in the issue tracker and on the launch threads.
- Write one deep post (“How I audit citations with a 200-line Python script”)
  instead of ten promotional posts.
- Ask for failure cases. They are more useful than praise and produce better
  follow-up content.

## 6. First 30 days

| Week | Focus | Artifact |
|---|---|---|
| 1 | Launch and listen | release, Show HN, one Japanese post, one Chinese post |
| 2 | Fix the top failure | adapter or audit-script patch, changelog entry |
| 3 | Publish evidence | a small, honest eval report with 2–3 models |
| 4 | Community | merge an external PR, add an example from a user, write a retrospective |

## 7. Metrics that matter more than stars

- external pull requests
- issues that reproduce a real failure
- examples from users in different domains
- citation/DOI corrections
- adapter coverage
- eval results that include negative findings
- repeat users

Stars are useful for discovery. Trust comes from maintenance and honesty.

## 8. Star-worthy checklist

- [ ] README explains the problem in one screen.
- [ ] A 60-second quick start works without cloning.
- [ ] At least one real example with an audit report.
- [ ] CI is green and visible.
- [ ] License is present.
- [ ] Contributing guide is specific.
- [ ] Issue templates exist.
- [ ] The evidence page separates findings from claims.
- [ ] Limitations are easy to find.
- [ ] The repository is updated after launch.

## 9. What not to do

- Do not buy stars or use engagement pods.
- Do not claim a peer-reviewed effect that was not measured.
- Do not hide the audit script's limits.
- Do not post the same announcement to every community at once.
- Do not argue with criticism in the thread; fix the artifact and reply with the
  change.
