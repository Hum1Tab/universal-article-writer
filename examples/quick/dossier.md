# Evidence Dossier — Why Fluent Citations Are Not Evidence

## 1. Basic information

- **Mode:** `quick`
- **Language:** English
- **Length:** about 500 words
- **Date:** 2026-10-22
- **Audit:** `audit-report.json`

## 2. Question and thesis

- **Question:** What should a writer do when a language model can produce fluent,
  citation-shaped prose that may not be trustworthy?
- **Thesis:** For citation-bearing articles, verification should be external,
  locatable, and open to disagreement.
- **Strength:** design recommendation, not a proven causal effect.
- **Scope:** high-stakes articles that will be cited or used for decisions; not
  low-stakes memos.

## 3. Load-bearing claims

| ID | Claim | Evidence | Confidence | Status |
|---|---|---|---|---|
| C01 | GPT-3.5 fabricated 55%, GPT-4 18%, of citations in the studied reviews | S01 | medium | supported |
| C02 | Among real citations, 43% / 24% had substantive errors | S01 | medium | supported |
| C03 | Five assistants showed sycophancy across four tasks | S02 | medium | supported |
| C04 | Verification should be external, locatable, and open to disagreement | S01; S02; S03 | medium | supported as a design inference |

## 4. Strongest objection and response

- **Strongest objection:** A capable model with retrieval, a long context, and a
  careful one-shot prompt may catch most citation errors. External ledgers add
  overhead and can create a false sense of rigor.
- **Best opposing evidence:** Retrieval-augmented and tool-using systems can
  reduce fabrication compared with closed-book generation. The studies cited
  here test specific model versions and prompts, not every current system.
- **What we concede:** The protocol is not necessary for every task, and a
  well-designed retrieval system may outperform a hand-maintained ledger on
  simple fact lookup.
- **What we do not concede:** A fluent draft plus a model's self-review is not
  an adequate verification record when the citation itself is part of the
  product. The artifact must let a human check the link.
- **Objection strength:** 4/5. The thesis is narrowed to citation-bearing work
  and to the need for an inspectable record, not to a claim that this exact
  protocol is uniquely effective.

## 5. Frame critique

- **Premise in the question:** “What should a writer do?” assumes the writer is
  the right unit of analysis.
- **Alternative frame:** The problem may belong to publishing workflows: editors,
  journals, and platforms could require source-level provenance rather than
  asking individual writers to police model output.
- **Judgment:** both frames are valid. This article keeps the writer’s workflow
  as the unit, and notes that institutional verification is a complementary
  solution.

## 6. Evidence summary

| ID | Type | Design / nature | Main finding | Limits | Verification |
|---|---|---|---|---|---|
| S01 | journal article | Bibliographic audit of 84 model-generated literature reviews | 55% / 18% fabricated; 43% / 24% of real citations had substantive errors | Specific model versions and prompts; English | partial (metadata + abstract) |
| S02 | preprint | Behavioral evaluation across assistants and tasks | Sycophancy consistent across five assistants and four tasks | Tested models/tasks; not every model | partial (metadata + abstract) |
| S03 | preprint | Experiments on intrinsic self-correction | Models struggle to self-correct reasoning without external feedback | Reasoning tasks; not citation checking specifically | partial (metadata + abstract) |

- **Primary sources:** 3
- **Counter-evidence read:** retrieval/tool-use literature is relevant but not
  included in this quick example; that is a limitation, not a hidden assumption.
- **Inaccessible material:** full texts of S01–S03 were not read for this example.

## 7. Search scope

- **Databases:** Crossref, arXiv
- **Search date:** 2026-10-22
- **Selection:** known, highly relevant studies on citation fabrication,
  sycophancy, and self-correction
- **Coverage:** not exhaustive. This is a `quick` example, not a systematic
  review.

## 8. Limits and unresolved issues

### Limits

- The rates are from specific model versions and will change.
- The article does not test the proposed workflow against a baseline.
- The audit is structural; it does not verify that S01–S03 support each sentence.

### Unresolved

| Issue | Why unresolved | Effect on conclusion | What is needed |
|---|---|---|---|
| Does externalization reduce errors in practice? | No controlled test here | The thesis is a design recommendation, not an effect claim | A blinded comparison with human raters |
| Do the findings transfer to Japanese/Chinese? | Studies are English-language | Generalization is uncertain | Native-language replication |

## 9. Numbers

| Number | Meaning | Denominator | Period | Population | Uncertainty | Source |
|---|---|---|---|---|---|---|
| 55% | fabricated GPT-3.5 citations | 636 citations / 84 papers | 2023 study | 42 topics | not reported in abstract | S01 |
| 18% | fabricated GPT-4 citations | same | same | same | not reported in abstract | S01 |
| 43% | substantive errors in real GPT-3.5 citations | real citations only | same | same | not reported in abstract | S01 |
| 24% | substantive errors in real GPT-4 citations | real citations only | same | same | not reported in abstract | S01 |

## 10. Citation status

- Citation markers in article: 4
- Unique sources cited: 3
- `verified`: 0
- `partial`: 3
- `abstract-only`: 0
- `unverified`: 0
- `retracted`: 0

## 11. Revision log

| Date | Version | Change | Reason |
|---|---|---|---|
| 2026-10-22 | 1.0 | Initial example | Demonstrate a READY audit with honest partial-source warnings |

## 12. AI use disclosure

- **Tool:** example authored with AI assistance for this repository.
- **Human check:** bibliographic metadata and abstracts were checked against
  Crossref and arXiv on 2026-10-22.
- **Not checked:** full texts, semantic support for every sentence, and
  transfer to other languages.
- **Generated text used as-is?** No; it is a demonstration artifact, not a
  published article.

## 13. Audit result

- **Date:** 2026-10-22
- **Scripts:** `audit_article.py`, `argument_lint.py`, `verify_sources.py`
- **Article readiness:** `READY`
- **Inference verdict:** `PASS` (no findings)
- **Bibliography verdict:** `PASS` (no findings)
- **Critical:** 0
- **Major:** 0
- **Minor:** 3 (`citation-partial-source` for S01–S03)
- **Info:** 8 (`long-sentence` heuristic; English sentences are not segmented
  reliably by the current script)
- **Not checked:** bibliographic existence, semantic support, argument strength.

### 13.1 Inference and values

- **Inference types used:** descriptive (C01–C03), evaluative design inference
  (C04).
- **Hidden premise in C04:** external, inspectable verification is preferable for
  citation-bearing work because the citation itself is part of the product.
- **Value premise:** readers and editors should be able to check a claim without
  trusting the writer's or the model's self-report. This is a value commitment,
  not an empirical finding.
- **Distribution:** the protocol shifts review cost onto writers and editors; it
  does not eliminate the cost.
- **Strongest value objection:** a competent institution may prefer centralized
  post-publication review to per-writer ledgers, which can be inconsistent and
  performative.

## 14. Delivery message

- **Conclusion:** When citations are part of the product, verification should be
  external, locatable, and open to disagreement.
- **Strongest objection:** A strong retrieval system plus careful prompting may
  achieve similar reliability with less overhead.
- **Unresolved issue:** Whether this protocol reduces citation errors compared
  with a strong baseline has not been measured.
- **Logic verdict:** PASS; the thesis is a bounded design recommendation, not a
  causal claim.
- **Value premise:** verification should be inspectable by the reader, not only
  asserted by the writer.
- **Files:** `article.md`, `sources.csv`, `claims.csv`, `dossier.md`,
  `audit-report.json`, `argument-lint.json`, `source-report.json`.
