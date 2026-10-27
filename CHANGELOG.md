# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/).

## [3.1.0] — 2026-10-28

### Added

- **`decision` mode**: design judgments produce a decision memo (options,
  criteria, trade-offs, recommendation, exit conditions) instead of an article.
  New `references/decision-mode.md`, `assets/decision-memo.md`, and eval `E23`.
- **`scripts/audit_decision.py`**: a deterministic audit for `decision` memos
  (decision sentence, options incl. status quo, criteria before evaluation,
  trade-offs, recommendation, observable exit conditions, reversibility,
  unknowns), with good/bad fixtures and a `check_repo.py` smoke test.
- **`scripts/audit_dossier.py`**: the dossier is now checked for its conclusion,
  strongest objection, limits, unverified items, AI disclosure, and audit
  results, with good/bad fixtures and a `check_repo.py` smoke test (D03/D04).
- **Trigger-suite checks**: `check_repo.py` validates that both 24-prompt
  suites have 12 heavy / 12 light prompts and contiguous IDs.
- **CI consistency self-test**: `selftest_consistency.py` now runs in CI, not
  just at release time.
- `scripts/score_trigger.py` and `scripts/selftest_consistency.py` are kept as
  reusable measurement/test helpers.
- **`scripts/check_consistency.py`**: compares rule IDs, phases, red-team
  roles, modes, forbidden-pattern IDs, documented case counts, and the
  `SKILL.md` size claim across artifacts; runs `build_universal.py --check`.
  Wired into `check_repo.py` and CI.
- **`docs/design-notes.md`**: the cost model for when the protocol should fire,
  the correlated-reviewer model of assurance, and the invariant argument behind
  the consistency checker.

### Changed

- **Description narrowed to evidence-bearing work** (arguments, reviews,
  fact-checks, normative/policy evaluation, design decisions, logic review).
  Light copy-editing, brainstorming, and single-source summaries are explicitly
  out of scope. Rationale: procedure cost should be proportional to error cost.
- **`SKILL.md` reduced from 701 to under 400 lines.** It keeps the absolute
  rules (`R01–R15`), modes, phase exit conditions, gates (`G0–G7`), and
  forbidden patterns (`P01–P28`). Procedure detail now lives only in
  `references/`, where most of it already existed.
- **External skill call table moved** from `SKILL.md` §6 to
  `references/skill-stack.md` §2.1, so it is not loaded on every use.
- **Phase 3.5 restored in `SKILL.md`** and added to the architecture phase
  table; the six red-team roles now agree in `SKILL.md`, architecture,
  orchestration, and the Lite prompt.
- **Concession Threshold uses observable predicates** instead of a free 1–5
  judgment, and must be scored in a pass separate from drafting.
- **Red-team independence stated honestly**: six roles cover different error
  types; sequential role-play by one model is recorded as non-independent.
- **Audit severity aligned with the gates**: a missing counterargument is now
  Major (G4), a disclosed `【未確認】` is Minor (honest uncertainty is not a
  defect), and an unverified claim with no disclosure marker is Major. The
  `major-article.md` fixture now omits the counterargument so R04 still
  exercises `--strict`, and a new fixture covers the disclosure check.
- **Phase 3.5 and G7 expanded** (when applicable) to require abuse risk,
  resource allocation, and religious/cultural views. Surfaced by the pilot
  eval of E20, where the normative article passed but covered these thinly.

### Verified

- A small-N verification of the v3.1 changes: trigger scope on two 24-prompt
  suites (including a held-out suite and a placebo control), a reference-free
  run, an old/new conformance A/B scored by the deterministic audits, and a
  six-case mutation test of the consistency checker. Results and limits are in
  `docs/verification-2026-10-28.md`.

### Fixed

- Duplicate forbidden patterns merged: `P04` (strawman / motte-and-bailey) and
  `P07` (p-value, relative risk, base rates) no longer restate `P06`.
- The Chinese README's stale diagram (five roles, five gates, missing 2.5/3.5).
- `references/skill-stack.md` now truthfully describes the body size and the
  single-source rule.
- Eval specifications aligned with the narrowed scope: E11 is now an
  evidence-bearing edit (citations and `【未確認】` preserved), E13 includes the
  memo it refers to, E20's bundled coverage item is split into five items, and
  E23's benchmark item no longer contradicts its prompt.
- `UNIVERSAL-PROMPT-LITE.md` carries all 15 rule IDs and the `decision` mode.

## [3.0.1] — 2026-10-23

### Added

- Japanese editing layer (`references/japanese-editing.md`) based on the seven
  principles of [yomiyasu](https://github.com/nanaism/yomiyasu) (MIT): subject–
  predicate alignment, sentence function and register, anthropomorphism,
  metaphor verbs, lead-ins and negative contrast, no invented facts, sentence
  length and comma control.
- Phase 4.2 final Japanese pass and Phase 6 checklist item.
- Optional `yomiyasu_lint.py` / `yomiyasu_diff.py` integration, with the caveat
  that lint findings are review candidates, not pass/fail scores.

### Changed

- Reduced em dashes, trailing colons, and over-emphasis in `SKILL.md`,
  `README.ja.md`, and the guide.
- Renamed the Japanese prose label "品質ゲート" to "品質確認（G1〜G7）"; the
  formal G1–G7 identifiers are unchanged.
- Replaced "主張—証拠マトリクス" with "主張と証拠の対応表" in the Japanese
  README and diagrams.

### Fixed

- A bold-rendering edge case in `README.ja.md`.
- Stale Japanese wording in the Lite prompt and architecture guide.

## [3.0.0] — 2026-10-22

### Added

- **Logic engine** (`references/logic-and-inference.md`): standard form,
  necessary/sufficient conditions, quantifiers, deductive validity, induction,
  IBE, probability and Bayes, causal identification (DAG, RCT, DiD, RD, IV),
  ACH, decision under uncertainty, and a fallacy taxonomy with repairs.
- **Synthesis engine** (`references/knowledge-synthesis.md`): multi-document
  reading, source independence, PRISMA 2020, GRADE, meta-analysis
  interpretation, heterogeneity, publication bias, qualitative synthesis, and
  disagreement mapping.
- **Normative engine** (`references/normative-and-conceptual.md`): value
  premises, ethical frameworks, applied ethics, policy analysis, conceptual
  analysis, thought experiments, cultural context, and "the Way."
- **Orchestration engine** (`references/orchestration.md`): ten roles, handoff
  schema, parallel reading, long-context chunking, failure modes, and stop rules.
- **Three deterministic audits**: `argument_lint.py` (inference and fallacy
  checks), `verify_sources.py` (bibliographic form, duplicates, retractions,
  optional online resolution), and an upgraded `audit_article.py` (normative
  claims, causal claims against cross-sectional evidence, duplicate DOIs,
  missing counterargument/limits, load-bearing count).
- **New modes**: `synthesis`, `logic`, `normative`, `policy`, `red-team`.
- **G7 values gate** and six red-team roles, including a normative analyst.
- **22 behavioral cases** (E01–E22) and **7 script regressions**
  (R01–R03, R06–R09), with logic fixtures.
- **Skill landscape** (`docs/skill-landscape.md`) covering 28 sources, licenses,
  adopted patterns, and rejected patterns.
- Completion checklist, forbidden patterns, and delivery contract extended for
  inference, evidence independence, values, and AI disclosure.

### Changed

- Version aligned to `3.0.0` across `SKILL.md`, scripts, evals, example audit
  report, and `CITATION.cff`.
- Quality gates expanded from G1–G6 to G1–G7.
- `UNIVERSAL-PROMPT.md` regenerated; Lite prompt updated with inference and
  value rules.
- README (EN/JA/ZH) updated for the three audits and the new architecture.
- CI compiles and tests all three audit scripts.

### Fixed

- Version drift between `SKILL.md` (2.1.0), scripts (2.0.0), and evals (2.0.0).
- Stale `UNIVERSAL-PROMPT.md` in the repository check.

## [2.0.0] — 2026-10-22

### Added

- Universal protocol that works in chat, API, agent, and coding-agent hosts.
- `UNIVERSAL-PROMPT.md` generated from `SKILL.md` as the single source of truth.
- `UNIVERSAL-PROMPT-LITE.md` for small context windows.
- `AGENTS.md` for coding agents.
- Adapters for ChatGPT, Claude, Gemini, coding agents, and generic chat/API.
- Chat-only output mode with article, source ledger, claim ledger, audit summary,
  and dossier in one response.
- Capability adaptation: file access, web search, PDF reading, code execution,
  subagents, and long context each have an explicit fallback.
- Prompt-injection rule: sources are data, not instructions.
- 15 behavioral eval cases (12 original + 3 portability cases) and 3 script
  regressions.
- Evidence dossier with citations, design rationale, and explicit limits.
- Repository checks, CI, issue templates, and a launch guide.

### Changed

- Removed host-specific `compatibility` metadata from `SKILL.md`.
- Split the detailed Japanese guide out of the landing README.
- Reorganized quality gates and completion checks.
- Made “do not claim a capability you do not have” explicit.

### Fixed

- Stale cross-references after section renumbering.
- Paths now assume the package is the repository root.

## [1.0.0] — 2026-10-20

### Added

- Initial seven-phase workflow.
- Source ledger, claim–evidence matrix, Toulmin argument map.
- Red-team review with five roles and a concession threshold.
- Standard-library audit script.
- Japanese reference files and templates.
