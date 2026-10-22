# Quick example — a READY article with honest warnings

This example shows the full package for a short English article:

```text
article.md          the article
sources.csv         three real sources, marked partial
claims.csv          four load-bearing claims with warrants and falsifiers
dossier.md          the skeptical-reader package
audit-report.json   a real article audit
argument-lint.json  a real inference audit
source-report.json  a real bibliography audit
```

## Run it

From the repository root:

```bash
python scripts/audit_article.py \
  --article examples/quick/article.md \
  --sources examples/quick/sources.csv \
  --claims examples/quick/claims.csv \
  --out examples/quick/audit-report.json

python scripts/argument_lint.py \
  --article examples/quick/article.md \
  --claims examples/quick/claims.csv \
  --sources examples/quick/sources.csv \
  --out examples/quick/argument-lint.json

python scripts/verify_sources.py \
  --sources examples/quick/sources.csv \
  --article examples/quick/article.md \
  --out examples/quick/source-report.json
```

Expected summaries:

```text
Article audit : READY
Findings      : Critical 0 / Major 0 / Minor 3 / Info 8
Inference     : PASS (0 findings)
Bibliography  : PASS (0 findings)
```

The three Minor findings are `citation-partial-source` for S01–S03. The sources
are real, and their metadata and abstracts were checked, but the full texts were
not read. The protocol records that rather than upgrading them to `verified`.

The eight Info findings are `long-sentence` flags. They are an artifact of the
script's English sentence segmentation, which is approximate. This is a useful
reminder that a clean audit is not the same as a good article.

## What to notice

1. **The thesis is bounded.** It recommends external verification for
   citation-bearing articles, not for every piece of writing.
2. **The numbers have a source and a denominator.** The article does not say
   “most citations are fake”; it reports the study's rates.
3. **The dossier includes the strongest objection.** A retrieval-heavy system
   may be enough, and the example concedes that.
4. **The audit is structural.** It confirms that every marker resolves and every
   load-bearing claim has evidence. It does not confirm that the evidence
   supports the sentence.

## Files are synthetic in one sense

The article and dossier were written as a demonstration. The three sources are
real and their bibliographic metadata was checked on 2026-10-22. Do not treat
this example as a peer-reviewed article or as an endorsement by the cited
authors.
