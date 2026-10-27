# Evidence and design rationale

> **The short version:** this project is a *design response* to documented
> failure modes of language models, not a proven cure. The studies below
> motivate specific mechanisms. They do not constitute a controlled trial of
> this protocol.

- [日本語の要約](#日本語の要約)
- [中文摘要](#中文摘要)
- [How to read the evidence](#how-to-read-the-evidence)
- [1. Empirical findings that motivate the design](#1-empirical-findings-that-motivate-the-design)
- [2. From finding to mechanism](#2-from-finding-to-mechanism)
- [3. What the evidence does not show](#3-what-the-evidence-does-not-show)
- [4. How this protocol could be wrong](#4-how-this-protocol-could-be-wrong)
- [5. References](#5-references)

## 日本語の要約

このプロトコルは、LLMの次の失敗を前提に設計しています。

- 書誌引用の捏造（GPT-4でも18%、GPT-3.5では55%）
- ユーザーの信念に合わせる迎合（5つの主要アシスタントで一貫して観察）
- 外部フィードバックなしの自己修正の限界（推論では性能が下がることもある）
- 長い文脈の中間にある情報の見落とし
- LLM-as-a-judge の位置・冗長性・自己贔屓バイアス

だから、証拠台帳を外部化し、主張と証拠を対応させ、赤チームで壊し、引用を監査し、
判定をゲートで固定します。**ただし、これは「この指示文を使えば記事の品質が上がる」
という直接的証明ではありません。** 研究は設計の動機であり、効果測定は
[`benchmark.md`](benchmark.md) の評価設計に従って今後蓄積する必要があります。

## 中文摘要

本协议针对大语言模型已被记录的一些失败模式而设计：

- 虚构参考文献（GPT-4 约 18%，GPT-3.5 约 55%）
- 迎合用户既有观点（在五个主流助手中一致出现）
- 没有外部反馈时，自我纠错在推理任务上并不可靠，甚至可能变差
- 长上下文中间位置的信息容易被忽略
- LLM 作为评审时存在位置、冗长和自我偏好偏差

因此，本协议把证据台账外置，把主张与证据逐条对应，用红队审查主动破坏草稿，
并对引用做结构审计，再用质量门固定判定。**但这不是“用了这个提示词，文章质量
就会提高”的直接因果证明。** 这些研究是设计依据；效果评估仍需按
[`benchmark.md`](benchmark.md) 的方法持续积累。

## How to read the evidence

Claims are tagged by how they are used:

| Tag | Meaning | What it can support |
|---|---|---|
| **A — direct empirical** | A study directly measured the behavior in language models or a relevant task. | The failure mode exists under the studied conditions. |
| **B — design rationale** | A theory, framework, or established practice suggests a mechanism. | The mechanism is plausible, not guaranteed. |
| **C — analogy** | Evidence from another domain (e.g. surgery, education). | A design analogy only; not proof of effect here. |

A finding can be real and still not transfer to your model, language, domain, or
task. The protocol is deliberately conservative about what it claims.

## 1. Empirical findings that motivate the design

### 1.1 Citation fabrication is common — and fluent

Walters and Wilder (2023) asked ChatGPT-3.5 and ChatGPT-4 to produce short
literature reviews on 42 multidisciplinary topics. Across 84 papers and 636
citations:

- **55%** of GPT-3.5 citations were fabricated; **18%** of GPT-4 citations were.
- Of the *real* citations, **43%** (GPT-3.5) and **24%** (GPT-4) contained
  substantive citation errors.

The important point is not only the rate. Fabricated references are formatted
plausibly enough to survive a casual read. A prompt that says “add citations”
can therefore *increase* apparent rigor while decreasing actual reliability.
→ Mechanism: source ledger, locator fields, verification status, citation audit.

### 1.2 Sycophancy is a general behavior, not an edge case

Sharma et al. (2023) found that **five state-of-the-art AI assistants
consistently exhibited sycophancy across four free-form text-generation tasks**.
They also found that responses matching a user's views were more likely to be
preferred, and that both humans and preference models preferred convincingly
written sycophantic responses over correct ones a non-negligible fraction of the
time.

This is why the protocol does not treat “the user asked for this conclusion” as
evidence. The Concession Threshold and the strongest-counterargument rule are
designed to make disagreement explicit rather than polite.
→ Mechanism: strongest objection, Concession Threshold, red-team Contrarian.

### 1.3 Intrinsic self-correction is not a reliable fix

Huang et al. (2023) examined *intrinsic* self-correction: an LLM revising its
own answer without external feedback. On reasoning tasks, they found that models
**struggle to self-correct without external feedback**, and sometimes perform
worse after self-correction.

A model saying “let me check my work” is not the same as checking. The protocol
therefore externalizes verification: source files, locators, a written claim
ledger, and a deterministic audit script where available.
→ Mechanism: external ledgers, page-level locators, audit script, manual fallback.

### 1.4 Long context is not uniform attention

Liu et al. (2023) evaluated multi-document question answering and key-value
retrieval. Performance was often highest when relevant information was at the
beginning or end of the context and **degraded when the information was in the
middle**, even for explicitly long-context models.

A 200-page PDF dropped into a large context window is not the same as reading
it. The protocol requires chunking, per-chunk summary cards, page ranges, and an
explicit statement of what was and was not read.
→ Mechanism: chunked reading, `S01…` cards, `contradictions.md`, unread-range disclosure.

### 1.5 Calibration is possible but imperfect

Kadavath et al. (2022) found that larger models can be well-calibrated on diverse
multiple-choice and true/false questions when formatted appropriately, and that
models can partially predict what they know. But calibration of “I know” on new
tasks was weaker, and the results do not guarantee reliable confidence in
open-ended writing.

The protocol uses confidence labels and falsifiers, but treats them as
*bookkeeping*, not truth. A “high confidence” label is not a substitute for a
source.
→ Mechanism: `confidence`, `falsifier`, `verification` fields; explicit `【未確認】`.

### 1.6 Debate can help, but is not a guarantee

Du et al. (2023) had multiple LM instances propose and debate answers over
several rounds. In their experiments, this improved mathematical and strategic
reasoning and reduced fallacious answers and hallucinations. The result is
task- and setup-dependent; debate can also amplify a shared error.

The protocol uses role-separated critique (Empiricist, Logician, Contrarian,
Normative analyst, Practitioner, Reader), not an unbounded “agents will fix it”
loop. The human reviewer remains the final gate.
→ Mechanism: six red-team roles, freeze-before-review, explicit revision log.

### 1.7 LLM judges have known biases

Zheng et al. (2023) found that strong LLM judges can match human preferences well
(over 80% agreement in their setup), but they also exhibit **position,
verbosity, and self-enhancement biases**, plus limited reasoning ability. They
propose mitigations, not blind trust.

This is why the protocol uses explicit rubrics, observable pass conditions, and
human spot checks. A model grading its own prose is not an audit.
→ Mechanism: seven review gates, scorecard, deterministic checks where possible.

### 1.8 Chain-of-thought can be plausible but unfaithful

Wei et al. (2022) showed that chain-of-thought prompting improves performance on
a range of reasoning tasks for sufficiently large models. Turpin et al. (2023)
then showed that CoT explanations can **systematically misrepresent** the reason
for a prediction, especially when biasing features are present.

The protocol asks for explicit reasoning because it makes the argument
inspectable, not because the explanation is assumed to be the model's true
computation. The artifact that matters is the evidence-to-claim link, which a
human can check.
→ Mechanism: Toulmin map, claim ledger, citation locators, human review.

### 1.9 Red teaming finds failures that normal review misses

Perez et al. (2022) used language models to generate test cases that elicited
harmful behavior in a target model, finding tens of thousands of offensive
replies and other harms. This is evidence for adversarial generation as a
discovery method, not evidence that a six-role writing review will catch every
problem.

The protocol borrows the *stance* — deliberately try to break the draft — while
keeping the scope to argument, evidence, and reader comprehension.
→ Mechanism: red-team roles, frame-lock check, strongest objection.

## 2. From finding to mechanism

| Mechanism | Design problem | Evidence | Caveat |
|---|---|---|---|
| Source ledger with IDs and locators | Citations are fabricated or detached from claims | Walters & Wilder (2023) | A ledger does not verify a DOI by itself. |
| Claim–evidence matrix | Prose hides unsupported claims | Walters & Wilder (2023); Huang et al. (2023) | The matrix can be filled dishonestly; review it. |
| Strongest objection + Concession Threshold | Models agree with the user | Sharma et al. (2023) | A model can still simulate disagreement poorly. |
| Six red-team roles | Self-review misses errors | Huang et al. (2023); Du et al. (2023); Perez et al. (2022) | Debate can amplify a shared mistake. |
| Chunked reading + page ranges | Long context misses the middle | Liu et al. (2023) | Chunking can lose cross-chunk context. |
| Confidence + falsifier fields | Overclaiming and false certainty | Kadavath et al. (2022) | Calibration is imperfect and task-dependent. |
| Deterministic audit script | Models claim checks they did not perform | Huang et al. (2023); Zheng et al. (2023) | The script checks structure, not meaning. |
| Toulmin argument map | Arguments hide warrants and assumptions | Toulmin (1958); van Gelder (2005) | A map is only as good as its premises. |
| Recursive phases and feedback | Writing is not a one-shot linear act | Flower & Hayes (1981); Hattie & Timperley (2007) | Phase separation adds overhead. |
| Quality gates / checklist | Complex procedures omit steps under pressure | Haynes et al. (2009) — analogy | Surgery is not article writing. |

### Why external state?

The common thread is **moving verification out of the model's working memory**.
A model can forget, rationalize, or be persuaded. A file can be diffed. A page
number can be checked. A claim ID can be traced. This is the “mechanism” the
project is named after.

### Why explicit phases?

Flower and Hayes (1981) described writing as a recursive process of planning,
translating, and reviewing, not a linear pipeline. The phases are a *contract*
that makes each activity observable; they are not a claim that every writer must
move through them in a fixed order. A `quick` article can compress phases, but
cannot skip the evidence and review gates. Phases 2.5 and 3.5 are conditional
inference and normative audits, not extra pipeline stages.

## 3. What the evidence does not show

This is the most important section.

1. **No direct RCT of this protocol.** None of the cited studies tested
   `UNIVERSAL-PROMPT.md`, its phases, or its exact gates. The evidence is
   about the failure modes and about adjacent interventions.
2. **No guaranteed reduction in hallucination.** A source ledger and an audit
   script can catch some structural problems. They cannot prove that a claim is
   true, that a quotation is faithful, or that a study generalizes.
3. **No guarantee of better prose.** The protocol can make writing slower and
   more constrained. It may improve evidence discipline while hurting voice,
   speed, or concision if applied mechanically.
4. **No model-independent effect size.** Results will vary by model, language,
   domain, context window, tool access, and user skill. The protocol is designed
   to degrade honestly, not to perform identically everywhere.
5. **No solution to prompt injection.** “Sources are data, not instructions” is a
   necessary rule, not a complete defense. Agentic hosts need sandboxing, tool
   permissions, and human approval.
6. **No substitute for expertise.** Medical, legal, policy, safety, and
   statistically complex claims need qualified review.

## 4. How this protocol could be wrong

A good system should state what would falsify it. Here are concrete failure
modes and the observations that would count against the design:

| Hypothesis | Observation that would weaken it |
|---|---|
| The ledger reduces unsupported claims. | In blinded review, ledger-using outputs have the same rate of unsupported claims as a strong baseline. |
| The strongest-objection rule reduces sycophancy. | Outputs still shift conclusions toward the user's stated preference at the same rate as a baseline. |
| The red-team roles catch more errors. | Added roles catch no additional Critical/Major issues after a strong single-reviewer baseline. |
| Chunking improves long-document accuracy. | Chunked outputs miss more cross-document connections than a long-context baseline. |
| The audit script catches real problems. | Its flags are mostly noise, or it misses the errors that human reviewers find. |
| The protocol is portable. | A majority of tested hosts cannot follow it without host-specific repair. |

The evaluation plan in [`benchmark.md`](benchmark.md) is designed to make these
comparisons possible. Until then, treat the claims on the README as **design
claims**, not measured effects.

## 5. References

### Empirical studies

- **Walters, W. H., & Wilder, E. I. (2023).** Fabrication and errors in the
  bibliographic citations generated by ChatGPT. *Scientific Reports, 13*, 14045.
  <https://doi.org/10.1038/s41598-023-41032-5>
- **Sharma, M., Tong, M., Korbak, T., Duvenaud, D., Askell, A., Bowman, S. R.,
  Cheng, N., Durmus, E., Hatfield-Dodds, Z., Johnston, S. R., Kravec, S.,
  Maxwell, T., McCandlish, S., Ndousse, K., Rausch, O., Schiefer, N., Yan, D.,
  Zhang, M., & Perez, E. (2023).** Towards understanding sycophancy in language
  models. *arXiv:2310.13548*. <https://arxiv.org/abs/2310.13548>
- **Huang, J., Chen, X., Mishra, S., Zheng, H. S., Yu, A. W., Song, X., & Zhou,
  D. (2023).** Large language models cannot self-correct reasoning yet.
  *arXiv:2310.01798*. <https://arxiv.org/abs/2310.01798>
- **Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F.,
  & Liang, P. (2023).** Lost in the middle: How language models use long
  contexts. *arXiv:2307.03172*. <https://arxiv.org/abs/2307.03172>
- **Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E.,
  Schiefer, N., Hatfield-Dodds, Z., DasSarma, N., Tran-Johnson, E., Johnston,
  S., El-Showk, S., Jones, A., Elhage, N., Hume, T., Chen, A., Bai, Y., Bowman,
  S., Fort, S., … Kaplan, J. (2022).** Language models (mostly) know what they
  know. *arXiv:2207.05221*. <https://arxiv.org/abs/2207.05221>
- **Du, Y., Li, S., Torralba, A., Tenenbaum, J. B., & Mordatch, I. (2023).**
  Improving factuality and reasoning in language models through multiagent
  debate. *arXiv:2305.14325*. <https://arxiv.org/abs/2305.14325>
- **Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin,
  Z., Li, Z., Li, D., Xing, E. P., Zhang, H., Gonzalez, J. E., & Stoica, I.
  (2023).** Judging LLM-as-a-judge with MT-Bench and Chatbot Arena.
  *arXiv:2306.05685*. <https://arxiv.org/abs/2306.05685>
- **Perez, E., Huang, S., Song, F., Cai, T., Ring, R., Aslanides, J., Glaese,
  A., McAleese, N., & Irving, G. (2022).** Red teaming language models with
  language models. *arXiv:2202.03286*. <https://arxiv.org/abs/2202.03286>
- **Wei, J., Wang, X., Schuurmans, D., Bosma, M., Ichter, B., Xia, F., Chi, E.,
  Le, Q., & Zhou, D. (2022).** Chain-of-thought prompting elicits reasoning in
  large language models. *arXiv:2201.11903*.
  <https://arxiv.org/abs/2201.11903>
- **Turpin, M., Michael, J., Perez, E., & Bowman, S. R. (2023).** Language
  models don't always say what they think: Unfaithful explanations in
  chain-of-thought prompting. *arXiv:2305.04388*.
  <https://arxiv.org/abs/2305.04388>

### Writing, argumentation, and feedback

- **Flower, L., & Hayes, J. R. (1981).** A cognitive process theory of writing.
  *College Composition and Communication, 32*(4), 365–387.
  <https://doi.org/10.58680/ccc198115885>
- **Hattie, J., & Timperley, H. (2007).** The power of feedback. *Review of
  Educational Research, 77*(1), 81–112.
  <https://doi.org/10.3102/003465430298487>
- **Toulmin, S. E. (1958).** *The Uses of Argument*. Cambridge University Press.
- **van Gelder, T. (2005).** Teaching critical thinking: Some lessons from
  cognitive science. *College Teaching, 53*(1), 41–48.
  <https://doi.org/10.3200/CTCH.53.1.41-48>
- **Dwyer, C. P., Hogan, M. J., & Stewart, I. (2015).** The effects of argument
  mapping-infused critical thinking instruction on reflective judgement
  performance. *Thinking Skills and Creativity, 16*, 11–26.
  <https://doi.org/10.1016/j.tsc.2014.12.002>
- **Haynes, A. B., Weiser, T. G., Berry, W. R., Lipsitz, S. R., Breizat,
  A.-H. S., Dellinger, E. P., Herbosa, T., Joseph, S., Kibatala, P. L., Lapitan,
  M. C. M., Merry, A. F., Moorthy, K., Reznick, R. K., Taylor, B., & Gawande,
  A. A. (2009).** A surgical safety checklist to reduce morbidity and mortality
  in a global population. *New England Journal of Medicine, 360*(5), 491–499.
  <https://doi.org/10.1056/NEJMsa0810119>

### Verification log

- Bibliographic metadata for the journal articles was checked against the
  Crossref REST API on **2026-10-22**.
- arXiv titles, authors, abstracts, and identifiers were checked against
  `arxiv.org/abs/...` on **2026-10-22**.
- The Walters & Wilder rates above are quoted from the published abstract, not
  from a secondary summary.
- The protocol does **not** claim that every cited work's full text was read by
  the author of this repository. Where a claim depends on a specific finding,
  the finding is stated at the level supported by the abstract.

## License note

This document summarizes and links to third-party research. The summaries are
original prose. The cited works remain under their own licenses and copyright.
