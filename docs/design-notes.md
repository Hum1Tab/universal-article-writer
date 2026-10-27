# Design notes: procedure weight, assurance, and consistency

## 日本語の要約

v3.1 の変更は「軽くした」だけではない。三つの主張を分けて扱うための変更である。

1. **発火範囲**は、語彙ではなく「誤ったときの被害の大きさ」で決める。手続きの費用が被害を上回る仕事には、このスキルを使わない（§1）。
2. **独立した検査の数**は、役割の数ではなく「誤りの種類の網羅」と「当たりやすさの非相関」で決まる。同じモデルの逐次役割は独立ではない。だから構造的に検査できるものはスクリプトへ移す（§2）。
3. **一貫性**は文章の努力ではなく、機械で検査できる不変量として保証する。保証できるのは符号化した関係だけであり、意味の正しさは保証しない（§3）。

以下の命題は、明示した仮定の下でのみ成り立つ。数値例は説明用であり、測定値ではない。

---

## 0. Status

This note justifies the v3.1 restructuring (description scope, `SKILL.md`
slimming, the `decision` mode, role/phase alignment, and the consistency
checker). It is a **design argument**, not an empirical result. The repository's
own rule applies here: a specification is not a measurement.

- Propositions are conditional on the assumptions stated with them.
- Numeric examples are illustrative, not estimates from data.
- The only claim that is mechanically verified is the invariant set in §3,
  and only to the extent that `scripts/check_consistency.py` encodes it.

### 0.1 Verdict on the external review

The review that prompted v3.1 was factually accurate on the points it checked.
Its recommendations were directionally right but under-specified in three
places.

| Claim | Status | Qualification |
|---|---|---|
| `SKILL.md` is about 700 lines | Confirmed (701) | — |
| The description fires on light copy-editing | Confirmed | The fix should be scoped by error cost, not by verb (§1.4) |
| Procedure detail duplicates `references/` | Confirmed | The detail was *already* in `references/`; the remedy is to stop restating it, not to move it to a new file |
| Red team is 5 roles in one file, 6 in others | Confirmed | The architecture phase table also lacked the 3.5 row |
| Phase 3.5 exists only in a diagram | Confirmed | It is now a conditional phase in every artifact |
| Forbidden patterns 4/27 and 6/24 overlap | Confirmed | 24 and 30 also overlapped; merged into P04 and P07 |
| §6 lists ~30 external skills | Confirmed (30 rows) | Moved to `references/skill-stack.md` §2.1 |
| The behavioral evals are a specification, not a measurement | Confirmed | CI covers only the R01–R09 structural regressions |
| Sequential role-play is not independent review | Confirmed | The docs said so, but the protocol still implied six checks |
| The author scores its own concessions | Confirmed | Replaced with observable predicates; residual bias remains |
| Narrow the description, slim the body, align roles, add `decision` | Directionally right | See the three corrections above and §1–§3 |

The one thing the review did not check is whether the narrow description
preserves recall on genuine evidence work. That is an empirical question and is
listed as a falsifier in §5.

---

## 1. When should a heavy procedure fire?

### 1.1 Setup

A task `t` is handled by one of two procedures: light (`L`) or heavy (`H`).
Let

- `C_m` = cost of procedure `m` (tokens, latency, attention),
- `p_m(t)` = probability that a material error survives procedure `m`,
- `V(t)` = loss if a material error ships (utility units).

Expected cost:

```text
E_m(t) = C_m + p_m(t) · V(t)
```

**Assumptions.**

- **A1.** `C_H > C_L ≥ 0`.
- **A2.** `0 ≤ p_H(t) ≤ p_L(t) ≤ 1`; the heavy procedure never increases the
  error probability (this is an assumption, not a theorem; §1.4 weakens it).
- **A3.** `V(t) ≥ 0` and finite.

### 1.2 Proposition 1 (break-even)

`H` is weakly better than `L` exactly when

```text
(p_L(t) − p_H(t)) · V(t) ≥ C_H − C_L
```

*Proof.* Subtract: `E_L − E_H = (p_L − p_H)V − (C_H − C_L)`. The sign
determines the comparison. ∎

Define the break-even loss `V* = (C_H − C_L) / (p_L − p_H)` when
`p_L > p_H`. `H` is justified above `V*`, `L` below it.

### 1.3 Proposition 2 (no universally optimal procedure)

If `V` ranges over `[0, ∞)` and `p_L > p_H`, then neither procedure is optimal
for all tasks.

*Proof.* As `V → 0`, `E_L − E_H → −(C_H − C_L) < 0`, so `L` is strictly
better. As `V → ∞`, `E_L − E_H → +∞` because `p_L > p_H`, so `H` is strictly
better. ∎

**Corollary 1.** A trigger rule should be a predicate on `V` and on the
expected error reduction, not on the surface verb of the request. "Make this
readable" is a low-`V` request even when the text is an article; "should we
migrate the index to BM25" is a high-`V` request even when the word "article"
never appears.

This is the principled form of the "narrow the description" recommendation:
scope by error cost, not by a list of synonyms.

### 1.4 Proposition 3 (routing with an imperfect trigger)

Let `π_H`, `π_L` be the prior probabilities of heavy and light tasks.
A broad trigger `B` fires on every heavy task and on a fraction `f` of light
tasks. A narrow trigger `N` fires on a fraction `r` of heavy tasks and on no
light task. Firing means paying `C_H` and getting `p_H`; not firing means
paying `C_L` and getting `p_L`.

```text
E_B − E_N = π_H (1 − r) [ (C_H − C_L) − (p_L − p_H) V_H ]
          + π_L f        [ (C_H − C_L) − (p_L − p_H) V_L ]
```

*Proof.* Expand the four cases and collect. ∎

Narrowing is optimal when

```text
π_L f [ (C_H − C_L) − (p_L − p_H) V_L ]
    > π_H (1 − r) [ (p_L − p_H) V_H − (C_H − C_L) ]
```

The left side is the ceremony cost imposed on light tasks; the right side is
the benefit of catching heavy tasks that the narrow trigger would miss.
**Narrowing is not universally right.** It is right when the heavy-task recall
loss is small relative to the light-task cost. That is an empirical question
about the task distribution, and it should be measured (see §5).

Illustrative values (not measurements):

| Quantity | Value |
|---|---|
| `C_H − C_L` | 9 units |
| `p_L − p_H` | 0.10 |
| `V_H` | 2,000 |
| `V_L` | 5 |
| `π_H`, `π_L` | 0.2, 0.8 |
| `1 − r` (heavy tasks missed by narrowing) | 0.05 |
| `f` (light tasks caught by broadening) | 0.60 |

```text
light-task ceremony cost = 0.8 × 0.60 × (9 − 0.5) = 4.08
heavy-task recall benefit = 0.2 × 0.05 × (200 − 9) = 1.91
```

The ceremony cost exceeds the recall benefit, so narrowing is favored **for
these values**. Change `f` to 0.05 and the conclusion reverses. The point is the
inequality, not the verdict.

### 1.5 Proposition 4 (finite optimal procedure size)

Assume the error probability under a procedure of size `C` is

```text
p(C) = p_min + a·e^(−λC) + b·max(0, C − C0)²
```

with `a, λ, b > 0`. Then the expected cost `E(C) = C + p(C)·V` has a finite
minimizer, and beyond `C0` additional procedure can increase the error
probability.

*Proof.* `E(C) ≥ C + p_min·V → ∞` as `C → ∞`; `E` is continuous; hence a
minimum exists on `[0, ∞)`. The quadratic term is increasing for `C > C0`. ∎

The exponential term alone (with `b = 0`) already yields diminishing returns:
each additional unit of procedure removes a smaller slice of the remaining
error probability. The quadratic term models a second effect — checklist
overload, ritualization, attention diverted from judgment. That effect is
plausible but **not established here**; treat `b > 0` as a design hypothesis.

**Consequence.** "More procedure is safer" is false in general. The useful
question is not "how do we enforce every rule?" but "which rules buy the
largest error reduction per unit of procedure?"

---

## 2. Assurance is coverage, not a role count

### 2.1 Setup

Partition errors into classes `c` with weights `w_c` (the share of expected
loss). A review pass `i` detects class `c` with probability `d_{i,c}`. With a
shared blind spot `ρ_c` (the part of class `c` that this model cannot see even
when prompted), the expected undetected mass is

```text
U = Σ_c w_c [ ρ_c + (1 − ρ_c) · Π_i (1 − d_{i,c}) ]
```

### 2.2 Proposition 5 (saturation)

If `k` passes are exchangeable with detection probability `d_c > 0`, then

```text
U_c(k) = w_c [ ρ_c + (1 − ρ_c)(1 − d_c)^k ]
```

is decreasing in `k`, bounded below by `w_c ρ_c`, and its marginal reduction
is `w_c (1 − ρ_c) d_c (1 − d_c)^(k−1)`, which decreases geometrically to zero.

*Proof.* Monotonicity and the limit follow from `0 < 1 − d_c < 1`; the
difference `U_c(k) − U_c(k+1)` is the stated expression. ∎

### 2.3 Proposition 6 (identical passes add nothing)

If pass 2 is the same model with the same prompt and the same evidence, then
`d_{2,c} = d_{1,c}` and the blind spot is shared. The second pass is not an
independent draw; it is a repeated draw from the same conditional distribution.
The detectable part does not grow as `1 − (1 − d)²`; it is bounded by the
first pass's information.

*Proof sketch.* The detection event depends on the model's representation of
the error. With identical conditioning, the event is the same event; repeating
it cannot change its probability. ∎

**Corollary 2.** Six roles are a **coverage** claim (different roles ask
different questions, so `d_{i,c}` differs by class), not an **independence**
claim. The protocol must not present sequential role-play as six independent
checks. It should present it as: six question sets, one correlated reviewer,
plus deterministic checks for the structural classes.

### 2.4 Proposition 7 (allocation)

With a fixed budget, the first check to add is the one with the largest
marginal reduction in `U` per unit cost. A deterministic checker for a
structural class has `d ≈ 1` on that class at low cost, so it dominates an
additional correlated reviewer for the same class.

This is why v3.1 moves effort from "more roles" to `check_repo.py`,
`check_consistency.py`, and the three audit scripts. Those checks are narrow:
they cover structure, not meaning. That is exactly what makes them reliable.

### 2.5 Self-scoring

If the Concession Threshold score is a function of the author's private
beliefs, two runs by the same author are correlated and the score is not
reproducible. v3.1 replaces the free 1–5 judgment with a rubric over public
predicates (does the objection contradict the thesis? does it falsify a
load-bearing premise? does it only ask for clarification?). This reduces
arbitrariness; it does not eliminate bias, because the same model still
applies the rubric. The protocol says so.

---

## 3. Consistency as invariants

### 3.1 Setup

Let `A` be the artifact set (SKILL, architecture, orchestration, LITE, READMEs,
AGENTS, evals, scripts). Let `K` be the canonical content: the rule IDs, the
phase set, the role set, the mode set, the pattern set, the reference file set,
and the documented case count. Let `R` be a family of relations over `A`
("the role set in SKILL equals the role set in architecture", ...).

### 3.2 Theorem 1 (soundness of a checker)

If `check_consistency.py` returns pass **and** each check implements exactly
one relation in `R`, then `R(A)` holds.

*Proof.* Each check is a total function from `A` to `{pass, fail}` that fails
when its relation is violated. The script fails if any check fails. Therefore
pass implies every relation holds. ∎

The theorem is trivial. Its value is the choice of `R` and the fact that CI
runs it. A guarantee that is not enforced is a wish.

### 3.3 Theorem 2 (drift grows with copies)

Suppose a rule's text appears in `n` artifacts, each edited independently per
release with stale probability `q`. Then

```text
P(at least one stale copy) = 1 − (1 − q)^n
```

which is increasing in `n`. If the other artifacts carry only the rule **ID**
and a pointer to the canonical copy, the number of independently edited copies
is 1, and the expression collapses to `q`.

*Proof.* The copies are independent by assumption; the complement of "all
fresh" is "at least one stale". ∎

**Design rule.** One canonical prose copy per rule. Other artifacts may repeat
an identifier, a one-line label, or be generated. This is the difference
between *repetition for compliance* (inside the always-loaded prompt, cheap and
bounded) and *duplication for documentation* (across artifacts, a drift
source).

### 3.4 What the checker cannot guarantee

- Semantic equivalence of two differently worded rules.
- That the model actually read a reference file.
- That a gate was applied in good faith.
- That the article is good.

The repository already says this about the audit scripts. The same limit
applies here, and the checker's docstring repeats it.

---

## 4. What changed

| Change | Invariant it protects | Enforced by |
|---|---|---|
| Description scoped to evidence-bearing work | The skill does not fire on low-loss edits | `check_consistency.py` (scope phrases) |
| `SKILL.md` reduced to rules, modes, phases, gates | Always-loaded content carries the contract | `check_consistency.py` (size, rule IDs) |
| Phase detail moved to existing references | One canonical copy per procedure | `check_consistency.py` (reference set) |
| `decision` mode added | Design judgments get a memo, not an article | eval `E23` |
| Six roles everywhere; Phase 3.5 restored | Role and phase sets agree | `check_consistency.py` (sets) |
| `P01–P28` de-duplicated | No two patterns with the same text | `check_consistency.py` (normalized titles) |
| Concession Threshold rubric | Score depends on public predicates | `references/adversarial-review.md` §5 |
| `UNIVERSAL-PROMPT.md` generated | No drift between skill and prompt | `build_universal.py --check` |

A self-audit of the audit severities (the protocol applied to its own checks) is
in [`self-audit-2026-10-28.md`](self-audit-2026-10-28.md). It found two perverse
incentives: a disclosed `【未確認】` was Major, and a missing counterargument was
Minor. Both are fixed.

---

## 5. What would falsify this design

The argument above is conditional. These observations would count against it:

1. **Trigger recall drops.** On a held-out set of prompts that genuinely need
   evidence discipline, the narrowed description fires less often than the old
   one, and the loss exceeds the ceremony saved. Measure with a prompt suite
   and a blinded judge.
2. **Gate compliance drops.** On `E01–E23`, the slim `SKILL.md` produces fewer
   passed gates than v3.0.1, especially at Phase 4 (drafting) and Phase 5
   (red team). Measure with independent raters, not the model itself.
3. **The reference files are not read.** If traces show the model skips
   `references/` and improvises the moved procedures, the slimming traded
   reliability for tokens. Mitigation would be to restore the specific section,
   not to re-inflate the whole file.
4. **The checker gives false confidence.** If a relation is encoded too
   loosely (for example, counting headings instead of comparing sets), the
   pass is vacuous. The checker's own tests should include a deliberately
   broken fixture.

Until those measurements exist, the claims in this repository remain claims
about mechanism and design. That is the same standard the project applies to
articles.
