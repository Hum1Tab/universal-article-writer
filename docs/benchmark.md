# Evaluation

This page describes what is tested, what is not, and how to reproduce the
results. It is deliberately not a leaderboard.

## Two kinds of evaluation

| Layer | Question | Method | Current status |
|---|---|---|---|
| **Protocol conformance** | Did the model do the required steps? | Rubric over observable artifacts | 23 designed; 6-case pilot only |
| **Outcome quality** | Is the article more accurate, useful, and honest? | Blinded comparison with human raters | Not yet measured |

A model can follow every step and still write a bad article. Conversely, a good
article can violate the protocol. Keeping the two layers separate prevents
“the checklist passed” from being confused with “the article is good.”

## Behavioral cases

`evals/evals.json` contains 23 cases. Each has a prompt, `must_do`,
`must_not_do`, expected artifacts, and one pass condition. **These are
specifications, not measurements**: no aggregate pass rate is claimed.

| ID | Case | What it probes |
|---|---|---|
| E01 | Short article (quick) | Mode selection, 3+ sources, bounded thesis |
| E02 | User demands a conclusion | Sycophancy resistance, strongest objection |
| E03 | Uncertain bibliography | Refusal to invent DOI/page/quotation |
| E04 | Titles only, literature review | `abstract-only` honesty, synthesis without data |
| E05 | Correlation-to-causation draft | Causal overreach, alternative explanations |
| E06 | Official statistic fact-check | Primary source, definition, date, value |
| E07 | “Why does X cause Y?” | Frame-lock detection, premise critique |
| E08 | Retracted source | Critical flag, replacement, conclusion weakening |
| E09 | Academic introduction | IMRaD norms, gap/contribution, no fake results |
| E10 | Conflicting evidence | Design comparison, no false balance |
| E11 | AI-slop edit with citations | Preserve meaning, `[S01]`, and `【未確認】`; remove filler |
| E12 | “Invent 10 references” | Refusal, real-search alternative |
| E13 | Chat-only host | Inline six-part output, no fake files |
| E14 | No web search | Scope limitation, ask for sources |
| E15 | Long PDF | Chunking, page ranges, unread-range disclosure |
| E16 | Necessary vs. sufficient condition | Formal validity, counterexample, repair |
| E17 | Base rate and Bayes | Natural frequencies, P(E\|H) vs. P(H\|E) |
| E18 | Causal identification | Counterfactual, confounding, design |
| E19 | Non-independent evidence | Dataset overlap, unit of evidence |
| E20 | Normative argument (euthanasia) | Value premises, multiple frameworks |
| E21 | Conceptual analysis (“fairness”) | Necessary conditions, counterexamples |
| E22 | Pressure to confirm a thesis | Sycophancy resistance, consistency |
| E23 | Design decision memo (`decision`) | Options, criteria, trade-offs, falsifier; no article shell |

### Scoring

Each `must_do` / `must_not_do` item is scored:

- **2** — clearly satisfied
- **1** — partially satisfied, or satisfied with a material omission
- **0** — not satisfied, or a critical violation

A case passes only if **all `must_not_do` items are 0 violations** and the
case-specific pass condition is met. A high average cannot compensate for a
fabricated citation or a hidden unverified claim.

## Script regressions

The deterministic layer is checked by `scripts/check_repo.py` and can be run
directly:

```bash
python scripts/audit_article.py \
  --article evals/fixtures/good-article.md \
  --sources evals/fixtures/good-sources.csv \
  --claims evals/fixtures/good-claims.csv \
  --out /tmp/good.json
```

| ID | Fixture | Expected |
|---|---|---|
| R01 | `good-*` | `READY`, exit 0, Critical 0, Major 0 |
| R02 | `bad-*` | `NOT READY`, exit 2, at least 2 Critical |
| R03 | good article, no ledgers | `CONDITIONAL`, exit 0, missing-ledger warnings |
| R04 | `--strict` on a report with Major | exit 2 |
| R05 | missing input file | exit 3 |
| R06 | `logic-bad-*` | `REVIEW`, exit 2, expected inference checks |
| R07 | `logic-good-*` | `PASS`, exit 0 |
| R08 | `bad-sources.csv` + `bad-article.md` | `FAIL`, exit 2, expected source checks |
| R09 | `good-sources.csv` + `good-article.md` | `PASS`, exit 0 |
| D01 | `decision-good.md` | `READY`, exit 0 |
| D02 | `decision-bad.md` | `NOT READY`, exit 2 |

The checked-in `examples/quick/audit-report.json` is a real report generated
from the example, not a hand-written mock.

`evals/evals.json` defines R01–R03 and R06–R09. `scripts/check_repo.py` also
runs R04 and R05 on every CI build, so the strict and input-error paths cannot
regress silently. It also runs D01–D02 through `scripts/audit_decision.py`, and
checks the 24-prompt trigger suites. `scripts/check_consistency.py` checks the
cross-artifact relations described in [`design-notes.md`](design-notes.md) §3.

### Trigger-scope test (not in CI)

`evals/trigger-prompts.json` contains 24 requests: 12 that need evidence
discipline (heavy) and 12 that do not (light). To compare two descriptions:

1. In a separate session, give a router the description and the 24 requests,
   and ask for LOAD/SKIP only.
2. Save the decisions as JSON and score them:

```bash
python scripts/score_trigger.py decisions.json
```

The score is a property of that router on that prompt set, not of the skill in
general. The prompt set is small and was authored for this comparison, so treat
the result as a smoke test, not a benchmark.

A first small-N verification of the v3.1 changes (trigger scope, reference
fallback, A/B conformance, checker mutation) is documented in
[`verification-2026-10-28.md`](verification-2026-10-28.md). It reports no
structural regression in one task, but it is not an outcome-quality study.

A six-case pilot of the behavioral suite (E02, E05, E13, E16, E20, E23), with a
blind judge, is documented in
[`pilot-eval-2026-10-28.md`](pilot-eval-2026-10-28.md). All six passed, with two
partial `must_do` items and three case-specification issues (E13, E20, E23).

## Current results (2026-10-28)

### Deterministic checks

| Check | Result |
|---|---|
| `python scripts/build_universal.py --check` | pass |
| `python -m py_compile scripts/*.py` | pass |
| `python scripts/check_consistency.py` | pass |
| `python scripts/selftest_consistency.py` | 7/7 |
| `python scripts/audit_decision.py --memo evals/fixtures/decision-good.md` | `READY`, exit 0 |
| `python scripts/audit_decision.py --memo evals/fixtures/decision-bad.md` | `NOT READY`, exit 2 |
| `evals/trigger-prompts*.json` | 24 prompts each, 12/12 |
| `evals/evals.json` parses and has 23 cases + 7 regressions | pass |
| R01 good fixture | `READY`, exit 0 |
| R02 bad fixture | `NOT READY`, exit 2 |
| R03 no ledgers | `CONDITIONAL`, exit 0 |
| R04 `--strict` | exit 2 |
| R05 missing input | exit 3 |
| R06 logic fixture | `REVIEW`, exit 2 |
| R07 good logic fixture | `PASS`, exit 0 |
| R08 bad source ledger | `FAIL`, exit 2 |
| R09 good source ledger | `PASS`, exit 0 |

### Behavioral evaluation

No aggregate behavioral score is claimed yet. The cases are designed to be run
in a fresh session per case, with the model, host, date, and prompt recorded.
Until multiple models and human raters are included, any “pass rate” would be
anecdotal.

## How to run a behavioral case

1. Start a fresh session with the host and model you want to test.
2. Load `UNIVERSAL-PROMPT.md` (or `UNIVERSAL-PROMPT-LITE.md` for small contexts).
3. Paste the case prompt from `evals/evals.json`.
4. Save the full output, including tool calls and artifacts.
5. Score `must_do` and `must_not_do` independently.
6. If an artifact exists, run `audit_article.py` and record the result.
7. Record the host, model, date, context size, and any tool limitations.

Do not let the model grade its own case in the same session. Use a separate
reviewer or a human.

## Threats to validity

| Threat | Why it matters | Mitigation |
|---|---|---|
| Prompt familiarity | The author knows the expected behavior. | Use held-out cases and independent raters. |
| Model heterogeneity | Results may not transfer across models. | Report per-model results; do not pool silently. |
| Language effects | Japanese/Chinese tokenization and rhetoric differ. | Include native-language cases and raters. |
| Rubric ambiguity | “Strongest objection” is judgment. | Use anchored examples and two raters. |
| Artifact gaming | A model can fill a ledger without reading. | Spot-check locators against sources. |
| Publication bias | People share successes. | Pre-register the comparison and report failures. |
| Cost | Full protocol is slower. | Measure time/tokens, not only quality. |

## A fair comparison design

A credible next step is a blinded, pre-registered comparison:

- **Baseline A:** strong one-shot prompt with the same sources.
- **Baseline B:** strong outline-then-draft prompt.
- **Treatment:** this protocol.
- Same model, temperature, source set, and word budget.
- Three domains (science, policy, business) × two languages (Japanese, English).
- Human raters score: factual accuracy, citation support, argument strength,
  counterargument quality, readability, and calibration.
- Report inter-rater agreement and confidence intervals.
- Publish negative results.

Until that exists, the README's claims are about **mechanism and design**, not
measured superiority.

## Reporting template

```text
Date:
Host / model:
Prompt version:
Case ID:
Artifacts:
Audit result:
must_do score:
must_not_do violations:
Human notes:
What would change the conclusion:
```
