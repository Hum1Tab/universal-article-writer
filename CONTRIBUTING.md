# Contributing

Thanks for helping make evidence-first writing easier to do well.

This project is a **protocol**, not a content farm. Contributions are judged by
whether they make the protocol more truthful, more portable, or easier to
verify.

## Ways to contribute

- **Bug reports** — a rule is ambiguous, an adapter is wrong, the audit script
  misses a case, or the docs contradict each other.
- **New adapters** — instructions for a tool or model family that is not covered.
- **Eval cases** — a realistic failure mode with a clear pass condition.
- **Reference material** — a well-sourced addition to evidence appraisal,
  argumentation, citation checking, or red-team review.
- **Translations** — keep the READMEs in English, Japanese, and Simplified
  Chinese in sync when behavior changes.
- **Examples** — a small, reproducible article or review that demonstrates one
  mechanism.

## Ground rules

1. **No fabricated citations.** Every factual claim in a contribution needs a
   real source, or an explicit `【未確認】` / `unverified` marker.
2. **Separate evidence from design rationale.** If a research finding motivates
   a rule, say what it supports and what it does not prove.
3. **Do not add a rule that cannot fail.** A quality gate needs an observable
   pass condition and at least one failure example.
4. **Keep the protocol portable.** The core must work without a specific vendor,
   file system, browser, or API.
5. **Do not copy large portions of other skills or prompts.** Link, summarize,
   and respect the original license. See `references/skill-stack.md`.

## Development setup

Requirements: Python 3.9+ and Git. The audit script uses only the standard
library. `scripts/check_repo.py` also uses only the standard library.

```bash
git clone <your-fork-url>
cd universal-article-writer
python scripts/build_universal.py
python scripts/check_repo.py
```

If you edit `SKILL.md`, regenerate the portable prompt:

```bash
python scripts/build_universal.py
python scripts/build_universal.py --check
```

## Checks before a pull request

```bash
python scripts/build_universal.py --check
python -m py_compile scripts/audit_article.py scripts/build_universal.py scripts/check_repo.py
python scripts/check_repo.py
```

`check_repo.py` verifies:

- required files and frontmatter
- no stale `UNIVERSAL-PROMPT.md`
- valid JSON and CSV fixtures
- audit regression behavior (`READY`, `NOT READY`, `CONDITIONAL`, `--strict`, missing input)
- relative Markdown links
- eval case count and IDs
- no leftover old skill ID

You can also run the audit manually:

```bash
python scripts/audit_article.py \
  --article evals/fixtures/good-article.md \
  --sources evals/fixtures/good-sources.csv \
  --claims evals/fixtures/good-claims.csv
```

## Adding an adapter

1. Copy the structure of an existing file in `adapters/`.
2. State the exact setup steps, limitations, and the minimum prompt size.
3. Explain what to do when file access, web search, or code execution is absent.
4. Add the adapter to the table in all three READMEs.
5. Test the instructions in the actual product if possible. If you cannot test,
   say so in the pull request.

## Adding an eval case

Add a case to `evals/evals.json` with:

- a realistic prompt
- `must_do`
- `must_not_do`
- expected artifacts
- one observable pass condition

Prefer cases that expose a failure mode over cases that reward verbosity. If the
case can be checked mechanically, add a fixture and a regression entry.

## Pull request checklist

- [ ] The change is scoped and explained.
- [ ] `python scripts/check_repo.py` passes.
- [ ] New factual claims have real sources.
- [ ] New rules have a failure condition.
- [ ] READMEs and adapters are updated if behavior changed.
- [ ] No old skill ID, placeholder URL, or fabricated citation is introduced.

## Review standard

A contribution can be rejected even if it is well written, if it makes the
system less honest, less portable, or harder to audit. That is intentional.
