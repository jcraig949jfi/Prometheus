# TRANSFER-1 — REDESIGN. The generator worked; it found a defect in the scorer.

Preregistration `aporia/iq/PREREG_TRANSFER_1_2026-08-25.md` committed at **e7a9b314, before the
generator existed**. Corpus `sha256 e2e6898d...`, seed 20260825, deterministic.
Ledger: `aporia/iq/RESULT_TRANSFER_1.json`.

**This rung does not measure ΔE.** It measures per-task accuracy on generated strata. Quoting a
ΔE against the 120-task battery from generated tasks would be a category error.

---

## Terminal state

**REDESIGN**, from the preregistered table: T1 holds, T4 fails. The table was asserted to
partition all four T1×T4 cells in code.

**But the preregistration's gloss on REDESIGN is falsified.** It read *"the generator has a
degeneracy I did not stratify."* It does not. The branch fired for a different reason, and the
honest report is that the branch condition is right and its attached hypothesis is wrong.

## T1 — PASS. The stratification works.

    train 400 · test 200 · declared mix 0.70 / 0.15 / 0.15
    train strata  NONDEGENERATE 272 · NEAR_DEGENERATE 69 · DEGENERATE 59
    test strata   NONDEGENERATE 138 · NEAR_DEGENERATE 26 · DEGENERATE 36
    NONDEGENERATE draws whose target equals an operand:  0 of 410
    stratum-request mismatches: 0 · dropped records: 0

Uniform parameter draws put DEGENERATE near 2% — too thin to be the contamination channel the
prereg requires — so the stratum is sampled first and parameters drawn to satisfy it. Labels
asserted to partition by enumeration.

## T2 / T3 — the port transfers, and the shortfall is entirely surface

    NONDEGENERATE   train 0.6691   test 0.6957
    by surface      v0 0.9643   v1 0.9346   v2 0.0000   v3 0.9600

**There is no train/test gap** — test is marginally *higher*. The held-out parameter region
(T ∈ [61,200], never seen in train) costs nothing, so the port is not parameter-range-bound.

**v3 is the unseen combination** — it appears nowhere in train, only in test — and it scores
**0.96**, the joint highest. An unseen surface × unseen parameter-range cell is handled at the
same rate as the trained surfaces.

**v2 scores exactly 0.0000 on 197 tasks.** It reads *"A box held T items…"*, which the port's
`_RE_TOTAL` (`there were (\d+) items?`) cannot match, so the parser never fires and no scorer
routes. The entire gap between 0.67 and 0.95 is that one surface.

This is what separating surface from structure was for. Reported as two numbers rather than one:
**structural competence ≈ 0.95 on every surface the parser matches; parser coverage 3 of 4
surfaces.** A single number would have read as a mediocre capability; it is a good capability
behind a brittle regex.

## T4 — FAIL, and the mechanism is a substrate defect the canary could not show

    worst mutant on NONDEGENERATE   0.1366   (bar was < 0.10)
    port on NONDEGENERATE           0.6780

    M1_plus       0.1366      M2_off_by_one  0.0000
    M3_swapped    0.1366      M4_identity    0.0000
    M6_half_total 0.1268      M5_return_n    0.0000

Executed rather than inferred. On the 182 parser-firing NONDEGENERATE train tasks, `M1_plus`:

    emitted candidates[0] on 182 of 182  (100%)
    scored correct on 36 of 182          (0.1978)
    T+N was not among the candidates on 182 of 182 (100%)

> **`score_by_aggregate` falls through to `candidates[0]` when its value matches no candidate.**
> With four candidates that is free credit at 1-in-4, and it accrues to any rule that fires and
> produces a non-matching number.

That is the same `candidates[0]` pathology Lexis found in `score_by_max_value` (`fcdc91af`) —
but here it is in `score_by_aggregate__g`, a **guarded** scorer, which sits *inside* Apollo's
clean-routing pool. **So the clean-routing regime is not free of the guessing pathology; it only
excludes the unconditional form of it.** That is a correction to the qualifier I adopted from
Lexis one pass ago, found by running against 410 tasks instead of 5.

**Why the canary could not have shown this.** On the 5 canary tasks all four preregistered
mutants scored 0/5 and I recorded ΔE = 0 for all of them. At n = 410 the same mutants sit at
0.1366. Five tasks cannot distinguish 0.00 from 0.14.

**The distractor design worked exactly as specified, and is why two mutants score 0.0000.**
`M2_off_by_one` (target+1) and `M4_identity` (T) produce values that **are** candidates by
construction, so they match deterministically and pick a wrong one every time. The mutants that
score above zero are precisely those whose value is *never* a candidate and therefore fall
through to the guess. The requirement that distractors include the operands is doing real work.

## T5 — CONFIRMED, and it was a prediction against my own artifact

    set_membership   parser fires 0 / 100   acc 0.0000
    tabular          parser fires 0 / 100   acc 0.0000

The port's template-shaped regex fires **zero times** on both structurally different
construction routes. Stated in the preregistration in advance precisely so its confirmation
could not be presented as a surprise or as grounds to widen the parser.

**X-heldout is doing its job.** The relation is identical — remove N from T — and the port has
nothing to say about it. Whatever IQ-PORT-1 demonstrated, it was not a transferable capability.

## T6 — no mutant passes G and fails X

Empty, because no mutant passes G. Reported rather than omitted.

## What to redesign, and what not to

**Not the generator.** T1 passes, the strata are clean, the parameter partition transfers, the
unseen combination is handled, and the distractors discriminate. It found a real defect on its
first run, which is what an instrument is for.

**The scorer.** `score_by_aggregate`'s fall-through to `candidates[0]` gives non-matching rules a
1-in-4 floor. Any future ΔE or accuracy on a 4-candidate task carries that floor unless the
scorer abstains instead of guessing. **This is a change to `C`, which is byte-frozen, so it is
not made here** — it is recorded as a measured defect with a named consequence, and the decision
belongs to a preregistered rung of its own.

**Standing consequence for every reading taken on this substrate:** the null for a firing-but-wrong
rule on a k-candidate task is **1/k, not 0**. Any threshold placed at "near zero" is placed below
the achievable floor — the P138 failure in a new costume, and I placed exactly such a threshold
(< 0.10) in this rung's own preregistration.

## Cost-to-falsify

Six rows opened at `outcome: None` before the generator ran; closed with actual costs in
`aporia/iq/COST_TO_FALSIFY.jsonl`. T4's mechanism took one extra execution beyond its predicted
six — the probe that showed `candidates[0]` on 182/182.
