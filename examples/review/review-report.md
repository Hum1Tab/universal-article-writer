# Logic review — SNSは若者の心を壊すのか

- **Mode:** `review`
- **Date:** 2026-10-22
- **Verdict:** `NOT READY`
- **Critical:** 1
- **Major:** 2
- **Minor:** 1

> This is a synthetic teaching example. The “survey” in the draft is fictional.
> The review demonstrates how to flag a causal leap, not a real fact-check.

## Findings

### C-01 — Correlation is presented as causation (Critical)

- **Location:** line 3, “したがって、SNSが抑うつの原因である”
- **Problem:** The only evidence is a cross-sectional correlation (r = 0.4).
  Cross-sectional data cannot establish temporal order, rule out common causes,
  or distinguish selection effects. The conclusion is causal; the evidence is
  associational.
- **Why Critical:** The thesis and the policy recommendation depend on the causal
  claim. If it falls, the prescription has no support.
- **Fix:** Either (a) weaken the thesis to an association, or (b) add longitudinal,
  quasi-experimental, or randomized evidence that identifies a causal effect.
  State the identifying assumption and the counterfactual.

### M-01 — The study is not described well enough to evaluate (Major)

- **Location:** line 5, “この調査は1万人を対象にしており、説得力がある”
- **Problem:** Sample size alone is not a quality marker. The draft does not give
  the population, sampling method, measures, response rate, model, or
  confounders. A large biased sample is still biased.
- **Fix:** Add design details, or remove the claim that the study is persuasive.

### M-02 — “SNS” and “抑うつ” are not defined (Major)

- **Location:** lines 3–5
- **Problem:** “SNS use” could mean minutes per day, passive scrolling, messaging,
  or problematic use. “Depression” could mean a validated scale, a diagnosis, or
  self-reported mood. The correlation depends on these choices.
- **Fix:** Define both constructs and the measures. Distinguish clinical
  depression from subclinical symptoms.

### m-01 — “若者” is overgeneralized (Minor)

- **Location:** line 3
- **Problem:** The age range is unspecified, and effects may differ by age,
  gender, platform, and baseline mental health.
- **Fix:** Specify the population and any subgroup differences.

## Strongest objection

The strongest alternative explanation is **reverse causation and common cause**:
adolescents who are already depressed may use social media more (or differently),
and factors such as sleep disruption, family conflict, loneliness, and academic
stress may drive both. A cross-sectional r = 0.4 is compatible with these
explanations. The draft does not rule them out.

A second objection is **effect-size interpretation**: r = 0.4 is not, by itself,
evidence of a large clinical effect, and it says nothing about the direction of
causality or the size of a policy-relevant effect.

## Frame critique

The question “SNSは若者の心を壊すのか” presupposes harm and a causal direction.
A better question is: **for which young people, under what patterns of use, and
through which mechanisms, is the association positive or negative?** That framing
allows for null, beneficial, and harmful effects, and makes the policy question
conditional rather than automatic.

## Revision excerpt

> 横断調査では、SNSの利用時間と抑うつ尺度の間に r = 0.4 の関連が報告されている。
> ただし、横断データは時間順序を特定せず、睡眠不足・孤独・家庭環境などの共通原因や、
> 抑うつ的な若者がSNSを多く使う逆因果を排除できない。したがって、この結果は
> 「関連がある」ことを示すが、「SNSが抑うつを引き起こす」ことを示すものではない。
> 因果効果を主張するには、縦断データや操作変数・自然実験・RCT など、識別戦略を伴う
> 証拠が必要である。

## Delivery message

- **Conclusion:** The draft's causal thesis is not supported by a single
  cross-sectional correlation.
- **Strongest objection:** Reverse causation and common causes can explain the
  association.
- **Unresolved issue:** Whether any well-identified study shows a causal effect
  for the specific population and pattern of use.
- **Verdict:** `NOT READY`. Rewrite as an association, or add causal evidence.
