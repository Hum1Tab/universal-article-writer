# FAQ

## Is this just a long prompt?

No. The prompt is one artifact. The system also includes:

- a source ledger and a claim–evidence matrix
- a Toulmin argument map and an inference audit
- a six-role red-team review
- explicit seven-gate readiness decisions
- three deterministic audit scripts
- adapters and honest fallbacks for hosts without files, search, or code

You can use only the prompt, but you lose the audit trail that makes the
protocol different.

## Does it guarantee fewer hallucinations?

No. It makes unsupported claims easier to see and gives a model a procedure for
marking uncertainty. It cannot verify that a source exists, that a quotation is
faithful, or that a study generalizes. The audit scripts check structure and
surface patterns, not truth.

## Does it work with small models?

Use `UNIVERSAL-PROMPT-LITE.md`. Small models can follow the core rules but are
more likely to skip steps, miscopy IDs, or produce shallow objections. Test on
your model and keep the human review. A smaller model with a strict checklist
can outperform a larger model with no process on narrow tasks, but that is a
hypothesis to test, not a promise.

## Why CSV and Markdown instead of JSON or a database?

- readable in any editor
- diffable in Git
- importable into spreadsheets
- no dependency on a runtime or vendor
- easy to paste into a chat when files are unavailable

JSON is better for machines; CSV is better for a human who has to scan 40
sources. The protocol optimizes for the human check.

## Can I use it commercially?

The repository is MIT-licensed. Third-party concepts and references remain under
their own licenses. If you reuse text, figures, or prompts from another project,
check that project's license. The design notes in `references/skill-stack.md`
describe the main influences; they are not a legal opinion.

## Is it an academic writing tool?

It has an `academic` mode and an IMRaD path, but it is not a substitute for
supervision, peer review, or journal-specific rules. Check your institution's
and target journal's policy on AI assistance and disclosure. Never submit a
model-generated claim without checking the source.

## Can it write in Chinese or English?

Yes. The core instructions are in Japanese, but the output language is a
parameter. The repository includes English and Simplified Chinese READMEs. The
quality of evidence handling depends more on the model and sources than on the
language of the prompt.

## How many sources do I need?

The mode table suggests 3 for `quick`, 8 for `standard`, and 20 for `deep`. Those
are starting points, not a quota. One high-quality randomized trial can be worth
more than ten opinion pieces. The real test is whether the load-bearing claims
have adequate evidence and whether counterevidence was sought.

## What if I cannot run Python?

Use the manual completion checklist in `SKILL.md` §9. State “machine audit not
run” in the delivery message. Do not claim a pass you did not run.

## What if the AI cannot browse the web?

Ask the user for sources. Use only what is provided. Mark unverifiable claims
`【未確認】`. Do not invent URLs, DOIs, or statistics.

## What if the document is longer than the context window?

Chunk it by chapter or section. Create a summary card for each chunk with the
page range, claims, evidence, and limits. Record contradictions. State which
parts were read and which were not. See the long-document path in
`UNIVERSAL-PROMPT.md` §2.

## Is the research in `docs/evidence.md` proof that this works?

No. It is evidence for the failure modes and for adjacent interventions. The
protocol is a design response. `docs/evidence.md` explicitly separates direct
empirical findings, design rationale, and analogy, and `docs/benchmark.md`
describes the evaluation that would be needed to support an effect claim.

## Why the name “論理記事工房”?

It means “logical article workshop.” The English package name is
`universal-article-writer`; the Japanese display name is kept because it captures
the craft-oriented intent. “Universal” refers to portability across AI hosts,
not to a claim of universal effectiveness.

## How can I contribute?

See `CONTRIBUTING.md`. The most useful contributions are realistic failure cases,
new adapters, evidence-backed reference material, and translations that stay in
sync with behavior changes.
