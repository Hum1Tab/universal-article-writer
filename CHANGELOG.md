# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/).

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
