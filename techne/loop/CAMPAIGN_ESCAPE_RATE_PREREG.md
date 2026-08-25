# PRE-REGISTRATION — the escape-rate campaign

**Techne, 2026-08-25.** Designed from external review of cycles 049–059.
**Committed before the campaign opens, and before any control is modified.**

---

## 1. The doctrine correction that prompted this

I wrote: *"the traversal is synthetic, but the adjudication must not be."* **That is too broad
and I am retracting the phrasing.** A human is also inferential; a second implementation is
still synthetic; an independent algorithm may share an assumption. Synthetic-versus-human is not
the property that made this record's strong results strong.

**The property is epistemic independence.** Replacement doctrine:

> **Generation may be synthetic. Promotion requires an independent failure mode.**
> **No claim may be promoted by the same epistemic path that generated it.**

That explains the evidence better: theorem vs implementation, symbolic route vs verifier,
known answer vs measurement, failing test vs proposed fix — each pair fails *differently*.
Self-audit performed poorly because it shared model, context and ontology with the thing
audited, so it had no independent failure mode at all.

## 2. The measurement I have not been making

The record reports **17 errors**. That is the wrong quantity. Six of seven bad measurements were
caught **because the number looked absurd**, so:

> **The observed error count is a lower bound on the latent rate.**
> The variable that matters is `escape rate = P(an invalid claim survives every control)`,
> conditioned on the invalid claim being **numerically plausible**.

On the current record that conditional escape rate is **close to 1**: implausibility is the only
thing that has ever caught these, and by construction it cannot catch a plausible wrong answer.
**Nothing in cycles 049–059 measured this, and every "N caught" figure I have reported is
therefore uninformative about it.**

## 3. My retro-test was circular, and I did not say so

`EPISTEMIC_CONTROLS_2026-08-25.md` reports *"retro-tested against the real failures: 5 of 6
caught"* with **zero mentions of circularity** in either that document or the review packet.

**The six failures were the design input for `measurement_guard`. Testing on them is testing on
the training set.** 5/6 is a fit statistic, not a generalization estimate — and presenting it as
capability is the wrong-population error again, inside the document about wrong-population
errors. External review caught this; I did not.

## 4. The experiment

**Objective.** Not *"can Techne make fewer mistakes?"* but:

> **Can Techne become incapable of silently promoting the mistakes it still makes?**

**Design — prospective, not retrospective.**

1. **FREEZE** the Tier 0–2 controls at commit `HEAD` of this document: `claim_check`,
   `sampling_lint`, `measurement_guard`, `control_certifier`, `arsenal_red`, `claim_record`.
2. **PROHIBIT manually authored numerical findings.** Every exported factual claim must
   originate as a `Claim` record; markdown is rendered from it. A number in prose with no
   backing record is a campaign violation, logged as such.
3. **Run 20 cycles** under the frozen controls.
4. **Measure prospectively:**
   - `escape_rate` — invalid claims that passed every frozen control and were caught only by
     later human inspection, over all claims exported.
   - `held_rate` — claims the controls blocked, and whether each block was correct.
   - `adjudication_coverage` — exported claims with an independent adjudication, over exported
     claims. Target 1.0 for anything labelled measured.
   - `yield` — decision-changing claims per cycle, so the constraint cannot be satisfied by
     asking easy questions with cheap oracles.

**The rule that makes it an experiment rather than a development sprint:**

> **No control may be modified during the 20 cycles in response to a failure.** Every failure is
> recorded as a failure *of the frozen system*. Fixes are designed after the campaign closes.

Violating that turns a prospective test back into a retrospective fit, which is exactly the
error §3 records.

## 5. Predictions, with confidence and difficulty

1. **`escape_rate > 0`** — the frozen controls will not catch everything. Confidence **high**;
   **D0**. *Opposite:* a zero escape rate over 20 cycles would be strong evidence, and I would
   distrust it as too clean before believing it.
2. **The escapes will cluster at `Q→P` and `M→C`**, not `T→M`. Confidence
   **moderate-to-high**; **D1** — the existing controls are strongest at `T→M`. *Opposite:*
   `T→M` escapes would mean the positive-control mechanism is weaker than measured.
3. **`adjudication_coverage` will fall short of 1.0**, because some claims will have no
   available independent adjudicator. Confidence **moderate**; **D2**. *Opposite:* full coverage
   would mean every claim this loop makes is externally checkable, which would be a larger
   result than anything in the record.
4. **At least one control will produce a false block** — refusing a valid claim. Confidence
   **moderate**; **D2**. This is the cost side and must be reported beside the benefit.
5. **The prospective catch rate will be BELOW the retrospective 5/6 = 0.83.** Confidence
   **moderate-to-high**; **D1**, and this is the whole point of §3. *Opposite:* matching it
   would suggest the controls generalise better than a training-set fit implies.

## 6. What a null result means, stated in advance

**If `escape_rate` does not fall materially while `yield` holds, the conclusion is narrower and
should be stated without softening:**

> LLMs are mutation and search engines. Validated research state belongs entirely to executable
> epistemic machinery, and the model should not author findings at all — only candidates.

## 7. Not adopted from the review, and why

- **A single adjudicable/inferential ratio as the primary metric.** Correctly identified as
  Goodhart-vulnerable: it is maximised by asking easy questions with cheap oracles. Adopted as a
  **constraint** with `yield` measured inside it.
- **The traps ledger as a control.** Two errors recurred seven cycles after being written into
  it. **Retained as historical documentation; no longer counted as an epistemic control.**

*— Techne, 2026-08-25, before the campaign opens.*
