# Review example — breaking a causal leap

This example demonstrates `review` mode on a short draft that turns a
cross-sectional correlation into a causal claim and a policy prescription.

```text
draft.md           the flawed draft
review-report.md   the logic audit and revision excerpt
```

## What the review does

- marks the correlation-to-causation move as **Critical**
- explains why sample size does not rescue the design
- asks for definitions of “SNS use” and “depression”
- steelmans the reverse-causation and common-cause objections
- reframes the question so null and beneficial effects are possible
- provides a revision that keeps the association but drops the causal claim

## What it does not do

It does not fact-check the fictional survey, search for real studies, or rewrite
the whole article. `review` mode audits the reasoning; it does not silently
replace the author's voice.

## Try it

Paste `draft.md` into a fresh session with `UNIVERSAL-PROMPT.md`, then ask:

```text
この原稿を review モードで監査してください。
Critical / Major / Minor に分け、最強の反論と修正案を出してください。
原稿は書き換えず、review-report.md としてください。
```
