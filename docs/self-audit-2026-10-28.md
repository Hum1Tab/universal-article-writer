# Self-audit — 2026-10-28

This note applies the protocol's own gates to the protocol's audit rules. The
target is not an article; it is the question **"does each deterministic check
enforce the rule it claims to enforce?"**

## 1. Method

- Take `R01–R15` and `G0–G7` as the specification.
- For each check in `scripts/audit_article.py`, compare its severity with the
  rule it claims to test.
- Falsify with fixtures: a check that cannot make a case `NOT READY` for a
  Critical rule is not enforcing that rule.
- Fix the rule or the severity, then re-run `check_repo.py`.

## 2. Findings

| Finding | Why it matters | Fix |
|---|---|---|
| A disclosed `【未確認】` was **Major** | R02 requires the marker when a fact is unconfirmed. Penalizing it rewards hiding and forces `CONDITIONAL` on honest work. | Marker is now **Minor**. A claim with `status=unverified` and **no** marker is **Major** (`unverified-not-disclosed`). |
| A missing counterargument was **Minor** | R04 and G4 require the strongest objection. An article could be `READY` without one. | `counterargument-missing` is now **Major**. |
| `major-article.md` only produced a Major through the old `【未確認】` severity | After the fix, R04 (`--strict`) stopped testing the strict path. | The fixture now omits the counterargument, so R04 still exits 2. |
| The docs said "flags unresolved `【未確認】`" without saying the severity | A reader could not predict whether an honest marker makes a report `CONDITIONAL`. | `docs/architecture.md` §8.1 now states the severity and the new check. |

The first two are the substantive ones. Both were **perverse incentives**: the
rule said "disclose uncertainty" and "write the strongest objection", while the
audit punished the first and ignored the second.

## 3. Verification

- `R01` good fixture → `READY`, exit 0.
- `R02` bad fixture → `NOT READY`, exit 2, expected checks present.
- `R04` major fixture + `--strict` → `CONDITIONAL`, exit 2.
- `unverified-article.md` + `unverified-claims.csv` → `CONDITIONAL`, with
  `unverified-not-disclosed`.
- `dossier-good.md` → `READY`; `dossier-bad.md` → `NOT READY`.
- `logic-report-good.md` → `READY`; `logic-report-bad.md` → `NOT READY`.
- `package-good/` → `READY`; `package-bad/` → `NOT READY`.
- `check_repo.py` → 77/77.
- `check_consistency.py` → 36/36.
- `selftest_consistency.py` → 7/7.

## 4. Second pass — the dossier was required but unchecked

`dossier.md` is part of the output contract, but `audit_article.py` never reads
it, and `check_repo.py` only checked the quick example. A hollow dossier could
still ship with a `READY` article. This is the same gap as the decision memo
before `audit_decision.py`.

Fix:

- `scripts/audit_dossier.py` checks the conclusion, strongest objection, limits,
  unverified items, AI disclosure, and audit results; missing conclusion /
  objection / limits are Critical, the other sections are Major, an empty
  section is Major, and `TODO`/`TBD` is Minor.
- `dossier-good.md` / `dossier-bad.md` fixtures, wired into `check_repo.py` as
  D03/D04.

The check verifies presence and non-emptiness, not whether the objection is
strong or the limits are honest. Those remain human judgments.

## 5. Third pass — `logic-report.md` was required but unchecked

`logic-report.md` is the Phase 2.5 artifact, but no script read it either. A
report could be missing premises, inference types, or falsifiers and still pass.

Fix:

- `scripts/audit_logic_report.py` checks the conclusion, premises (with
  `[TEXT]`/`[CONV]`/`[ANALYST]` tags), inference type, counterexample or
  alternative explanation, falsifiers, and open questions.
- If `--claims` is given, a load-bearing claim must be referenced by ID or by
  the phrase "荷重主張".
- `logic-report-good.md` / `logic-report-bad.md` fixtures, wired into
  `check_repo.py` as D05/D06.

The check verifies structure, not whether the inference is valid or whether the
falsifier is adequate.

## 6. Fourth pass — the package itself was not checked

Every artifact had an audit, but no script checked that the artifacts agree with
each other. A package could have a claim citing `S09` when `sources.csv` stops
at `S08`, or a load-bearing claim that never appears in `logic-report.md`.

Fix:

- `scripts/audit_package.py` checks required files, claim-evidence IDs,
  article-citation IDs, load-bearing claims in the logic report, ambiguous
  article/decision packages, and disclosure of a missing machine audit.
- `package-good/` / `package-bad/` fixtures, wired into `check_repo.py` as
  D07/D08.

This approximates phase order only by **artifact presence**. It does not verify
that the phases ran in order, and it cannot detect a convincing backfilled
ledger.

## 7. What this self-audit did not fix

- **Phase order is not verified.** The scripts see final artifacts, not whether
  Phase 1–3 were executed. A model can backfill a clean ledger. The protocol
  says the audit checks structure, not process; this remains a limit.
- **`partial` sources are still Minor.** A load-bearing claim supported only by
  an abstract-level source is allowed. The example is deliberately `READY` with
  three partial sources, so changing this would require re-rating the example.
- **`G5` prose quality is not machine-checked.** "One paragraph, one job" and
  "the promise is collected" remain human judgments.
- **Concession Threshold is still self-scored.** The rubric reduces
  arbitrariness, not the correlation between author and scorer.

These are recorded as limits, not silently fixed.
