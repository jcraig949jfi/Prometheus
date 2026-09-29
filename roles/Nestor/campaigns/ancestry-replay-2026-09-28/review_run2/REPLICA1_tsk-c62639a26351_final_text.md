# Review of NPE ancestry replay, production run 2 (base cef9cc1b9)

**Verdicts**
- **Run-2 integrity: HOLDS WITH NOTES.** I found no tampering, no files differing from the freeze, and no undeclared rule change after exposure. Two provenance claims can't be checked from git alone (F5). Tracer agreement on the production data is still outstanding (F4).
- **s4_run.py @ 68779d3e: DOES NOT CONFORM.** Most of it can be fixed by recomputing from the existing `S4_RESULTS.jsonl` rows. The exception is completeness (F7), which needs a re-run.

I only hashed and grepped; nothing was run. The full report is `out/REVIEW_RUN2_INTEGRITY.md`.

## What holds
- **Freeze:** all 11 TRACER_FREEZE v4 files match their hashes. The freeze file itself is c1ce6d93, `s4_run.py` is 68779d3e and `production_launch.py` is 1e2c4394. The v3→v4 diff changes `run_production.py` only, and the repair is the declared one-line fix. No tracer file changed between the start-receipt HEAD and cef9cc1b9.
- **Receipts:** START (13/13 checks), END, the index, the S4 summary, both sample manifests and all 11 births hashes are consistent with each other.
- **Lineage:** all 11 lineage hashes agree across PIN_REPRODUCE, Archaeon's NPE_T003_HASHES and the production index. result efba5535 matches. Every summary shows shadow_checked = interactions = 256000.
- **Duplicates:** exactly s9200006 C→A and s9200008 C→A. The A and C tallies are identical, giving 29 distinct births.
- **G2 fresh set 2:** Nestor's output hash equals the sealed 4f542a70. Both comparisons give 1.0 on every gated field.
- **Independence:** nothing in Nestor's tree references the reference tracer or its outputs. The adaptations after exposure (C9, C10) are declared, and the fresh set post-dates both freezes.
- **s4 sampling:** outcome-independent (hash of seed, run and child), fixed before run 1. 6 of 29 births were sampled.

## Findings

**BLOCKING** (for using the s4 tallies or starting synthesis, not for run-2 integrity)
- **F1** (`s4_run.py:84-92`): no 95% CI, no MARGINAL marking and no run-clustered bootstrap over the 9 simulations, which C4.4 and C7.4 require. It only pools ratios over loci.
- **F2** (`s4_run.py:48`): the class key is donor-relative (self = performer is the donor). R1 says "the executing organism", and G2 used performer = store_by (`compare_fresh.py:20`). Nobody has ruled on this, and addendum 1 did not check it.
  - Pooled prefix coverage is 223/735 = 0.303, so at least one class is below the 50% floor under any class key.
- **F3:** the NO_MATERIAL class and TIED handling are missing; ties go to whichever class appears first. Record 32 (s9200009) has no written ENTITY-MOVE loci but is classed "other".
- **F4:** there is no tracer agreement on production data yet, and the sample transfer is blocked. The 1% sample is picked by hash with no forced births, so it is expected to hold about 0.3 of the 34 births. The reference should be run on the 34 recorded birth pre-states. Also, only two-way agreement was done, although C5 says three-way.

**SHOULD-FIX**
- **F5:** "births byte-identical to run 1" can't be checked from git. The run-1 files are only in `_scratch/`, and run-1 summary hashes can't be compared because `summary.json` includes wall_s; all 11 differ. Committing the run-1 index, manifest and summaries would fix this.
- **F6** (`interventions.py:261`): `identified` uses the strict flip rule, not the gating C7.2 prefix rule; the comment at `:214` still says "PROPOSED". It can only over-identify. There are 0 FAILED under either rule, so no effect on this data.
- **F7** (`interventions.py:332`): the completeness leak test requires the full path to be unchanged. In NPE, copied loci are executed later, so a real leak changes the path and can't be counted. No applicability count is exported, so the 0.0 leak share is not evidence of completeness.
- **F8:** randomising the other entity suppressed the write or birth in all 8 draws on about 375 of 735 loci (19 of 29 births). On 22 loci every group had zero usable draws, yet they count as identified and have q8c = None. Synthesis must not treat None as 0.
- **F9** (`run_trace.py:220-237`): L3/L4 are built from the P-11 native parent pointer, so they are construction chains, but they are labelled as heredity. Under the CVT-R QUALIFICATION they need relabelling.
- **F10** (`production_launch.py`): the s4 hash is recorded but not enforced, the GO_FINAL hash is a constant nobody checks, the docstring is stale, and the frozen engine is not hashed in the receipt. The recorded values are correct, and lineage equality mitigates the engine gap.

**NOTE**
- **N1:** addendum 1's no-change rule was relaxed after the fact for the launcher's constants.
- **N2:** 34 only appears labelled next to n_duplicates, but summing the 11 summary files double-counts two simulations.
- **N3:** `source_diversity` is a raw count, so the <0.5 painting guard would be vacuous on it.
- **N4:** v5 R3 no longer says what a failed flip-coverage floor leads to.
- **N5:** the pin hashes are not newline-normalised, so they don't reproduce on Linux. There is no drift since the pin.
- **N6:** the prefix loop skips `assert_paired`.
- **N7:** only 6 births carry the per-byte arm.
- **N8:** the stale MUTATION_content diagnostic is covered by Archaeon's 212/212.