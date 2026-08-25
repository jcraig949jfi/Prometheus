# Schema fix — ADVANCE. And R1's falsifier fired against my own headline.

Ledger: `aporia/iq/RESULT_SCHEMA_FIX.json` — the first artifact in the arc written through
`result_schema.emit()`, which refuses to write a non-adjudicable result.

---

## The schema is binding. Three controls, each with its failing input.

    C1  rejects all 8 pre-R1 artifacts        PASS  (failing input: accepting one)
    C2  accepts a conforming artifact         PASS  (failing input: accepting none — a wall,
                                                     not a contract)
    C3  every required field load-bearing     PASS  (removed one at a time; each is caught)

**Existing artifacts were not retro-edited.** They stay non-conforming, which is the honest
record of how they were produced. Editing a result to satisfy a gate is retune-to-pass.

## R1's preregistered falsifier fired — against me

I wrote the falsifier in P168 before running it: *add the missing fields to a test artifact and
re-derive; if the verdict then matches, the artifact was the problem; if not, my rule is.*

    IQ-PORT-1        INADMISSIBLE -> INADMISSIBLE   (G-BRANCH still fires)
    IQ-NULL          INADMISSIBLE -> INADMISSIBLE   (G-BRANCH still fires)
    CEILING-ABSTAIN  INADMISSIBLE -> INADMISSIBLE   (G-MANDATORY: evaluation)

    flips attributable to ARTIFACT CONTENT      0 of 3
    flips attributable to MY DERIVATION RULE    3 of 3

## Correction to P168's headline

P168 reported *"4 of 6 rungs flip → the reviewer is confirmed by measurement"* and presented
those flips as evidence that artifact content was lossy. **That attribution was not established
and is now partly refuted.** Per-rung diagnosis, by inspecting which keys each artifact actually
carries:

    IQ-PORT-1        records `branch_table_partitions_36_cells`;
                     my rule looked for `branch_table_partitions`.
                     -> MY RULE. Key-name brittleness. The artifact records the fact.
    IQ-NULL          records NO partition key at all.
                     -> ARTIFACT. G-BRANCH fires correctly; the code asserted it, the
                        artifact never recorded it.
    CEILING-ABSTAIN  records `terminal_table_partitions` (my rule does check that), but carries
                     NO evaluator-hash key of any kind.
                     -> ARTIFACT. G-MANDATORY fires correctly on the evaluation falsifier.

**So the real split is 1 of 3 my rule, 2 of 3 artifact — MIXED**, not the wholesale
`MY_RULE_WAS_THE_PROBLEM` my own harness printed. That coarse verdict is itself a defective
readout: it asked only *"did adding the three schema fields flip it to ADMISSIBLE"*, and the
three fields were not the right ablation for the reasons that remained.

**Two corrections in one pass, both mine:** P168 over-attributed the flips to artifact content,
and this pass's harness under-attributed them by testing the wrong ablation. The per-rung
inspection above is the reading that survives both.

## What survives, and what does not

**Survives — the reviewer's structural point.** The gate was an instrument over my transcription;
that is true independently of how the flips are attributed, and it is why the schema exists.
Their ordering also survives: the fix belonged before another experimental run.

**Does not survive — my quantification of it.** "4 of 6, therefore confirmed by measurement" was
a confident number from an instrument whose attribution I had not tested. It is withdrawn and
replaced by the per-rung split.

**The pattern is now the arc's most frequent single failure**, on its fifth occurrence: a
confident reading produced by a probe that does not measure the thing it names. Threshold below
floor, vacuous footprint, shared probe state, perturbing discriminator, and now a key-name-brittle
derivation rule whose coarse verdict I nearly reported as-is.

## Still open, unchanged

- The derivation rule tests key **presence**, not outcome.
- BATTERY should split into design-admissibility and result-interpretation stages.
- Scorer permutation-invariance contracts for the rotation probe.
- TRANSFER-1's sampled draws need intervals; the exhaustive claims do not.

The immediate concrete task the falsifier creates: **make the derivation rule name-robust**, since
one third of the flips it produced were an artifact of exact key matching against artifacts whose
authors — me — used descriptive variants.
