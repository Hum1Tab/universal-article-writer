# Comparison: prompt vs. protocol

Most “article writing” prompts optimize for output. This project optimizes for
**defensibility**: can a skeptical reader trace each load-bearing claim to a
source, understand the warrant, and see what would change the conclusion?

## At a glance

| Dimension | Typical one-shot prompt | Chain-of-thought prompt | Universal Article Writer |
|---|---|---|---|
| Primary goal | Produce text quickly | Improve reasoning on a task | Produce an evidence package plus text |
| Source state | In the model's context or memory | Same | External `sources.csv` with verification status |
| Claim state | Implicit in prose | Implicit in reasoning | Explicit `claims.csv` with evidence IDs and falsifiers |
| Argument structure | Whatever the model defaults to | Reasoning chain | Toulmin map with warrant and qualifier |
| Inference audit | None | Implicit in the chain | Explicit type, hidden premises, counterexample, falsifier |
| Evidence synthesis | Stack summaries | Usually absent | Independence, heterogeneity, publication bias |
| Value premises | Treated as opinion | Usually absent | Explicit values, distribution, opposing values |
| Counterargument | “Include a counterargument” | Usually absent | Strongest objection plus frame critique |
| Sycophancy guard | None | None | Concession Threshold; user preference is not evidence |
| Citation check | Often none | Often none | Marker audit, retraction status, locator and DOI checks |
| Review | Model says “looks good” | Model checks itself | Six roles, seven gates, three deterministic audits |
| Portability | Vendor-specific | Vendor-specific | One core prompt plus adapters |
| Failure visibility | Hidden in fluent prose | Hidden in plausible reasoning | Written down and mechanically checked where possible |
| Overhead | Lowest | Low | Higher: ledgers, review, audit |
| Best for | Low-stakes drafts | Math/logic puzzles | Research-based articles, reviews, fact-checks |

## What is actually different

### 1. It separates sources from claims

A bibliography is not evidence. A source can exist and still not support the
sentence it is attached to. The claim ledger forces an explicit link:

```text
C03 → S02 (p. 14) → warrant: the trial measured the same outcome in the same population
```

If that link is missing, the claim is marked unsupported. If the link is weak,
the confidence drops. This is a structural fix, not a stylistic one.

### 2. It treats the user's preferred conclusion as a hypothesis

A prompt that begins “write an article arguing X” invites sycophancy. This
protocol can still write a persuasive article, but it must first check whether
the evidence supports X, state the strongest case for not-X, and weaken the
thesis if needed. The user can reject the result, but the model should not
pretend the evidence changed.

### 3. It makes the review step adversarial

“Review your answer” tends to produce cosmetic edits. The protocol freezes the
draft and assigns different reviewers to evidence, logic, opposition, values,
practice, and readability. The goal is to find a Critical issue before delivery,
not to produce a reassuring self-assessment.

### 3.1 It separates inference from evidence and from values

A citation can be real and still not support the conclusion. An inference can be
valid and still rest on a false premise. A normative conclusion can be coherent
and still smuggle in an unstated value. The protocol treats these as three
different layers and checks each one.

### 3.2 It counts evidence, not papers

Ten papers that reuse one dataset are not ten independent findings. The synthesis
engine asks for the unit of evidence, the overlap between studies, and the
heterogeneity that remains. This is the difference between a literature review
and a bibliography with paragraphs.

### 4. It treats missing capabilities as first-class states

A chat-only model cannot write `sources.csv`. It can still produce an inline
source table. A model without web search cannot verify a DOI; it can say so. The
protocol is designed around honest degradation rather than pretending every host
is the same.

### 5. It is auditable

The output includes the evidence package, not just the article. A reviewer can
ask:

- Which claims are load-bearing?
- Which source supports each one?
- What is the warrant?
- What would falsify it?
- What was not verified?
- What did the red team find?

That is a different product from “here is a 2,000-word article.”

## When this is overkill

Use a simpler approach when:

- the task is a short personal reflection with no factual claims
- the output is fiction, poetry, or brand copy where evidence is not the point
- you need a quick brainstorm, not a defensible argument
- the source base is one document and the claim is a direct summary
- the deadline does not allow verification and the cost of being wrong is low

The protocol can run in `quick` mode, but it still imposes evidence discipline.
If that discipline is irrelevant, a normal prompt is better.

## What this is not

- **Not a search engine.** It can use search, but it does not replace one.
- **Not a fact-checking oracle.** It structures verification; it does not
  guarantee truth.
- **Not a plagiarism checker.** It encourages attribution; it does not detect
  copying.
- **Not a substitute for domain expertise.** It can ask better questions, not
  become a statistician, lawyer, or clinician.
- **Not a guarantee of good writing.** It can produce stiff, over-documented
  prose if used mechanically. Voice still matters.

## The honest trade-off

This protocol costs more tokens, more time, and more attention. It buys:

- fewer unsupported claims
- fewer citation-theater sentences
- a visible strongest objection
- a review trail
- a package a skeptical reader can inspect

If those are not worth the cost for your task, do not use it. The project is
opinionated about when the trade-off is worth making.
