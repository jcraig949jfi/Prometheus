# R1 — machine-binding the gate. The reviewer was right, and the number is 4 of 6.

External review, blocking item: *the gate is an instrument over Aporia's transcription of primary
evidence, not over primary evidence.* Fixed here by deriving every claim field from the RESULT
artifacts themselves. Harness `aporia/iq/battery_claims.py`, ledger `RESULT_BATTERY_R1.json`.

**Result: `R1_transcription_was_lossy = True`.** Five verdict disagreements between my
hand-transcribed claim objects and the machine-derived ones.

    rung              hand-transcribed    machine-derived
    IQ-PORT-1         ADMISSIBLE          INADMISSIBLE
    IQ-NULL           ADMISSIBLE          INADMISSIBLE
    CEILING-ABSTAIN   ADMISSIBLE          INADMISSIBLE
    BATTERY           (not transcribed)   INADMISSIBLE
    SELECTOR-PREFLIGHT(not transcribed)   ADMISSIBLE
    PROVENANCE        ADMISSIBLE          ADMISSIBLE
    TRANSFER-1        ADMISSIBLE          ADMISSIBLE
    SCORER-FIX        ADMISSIBLE          ADMISSIBLE

**BATTERY's 6/6 was bookkeeping. Four of the six flip once the human step is removed.**

## The three defects the machine binding exposes

**1. Not one artifact records `intervention_class`.** Every RESULT json lacks it, and it is the
field `G-MANDATORY` — the gate's most important check — keys on. I supplied it by hand for all
six. So the gate's central test was reading a value I typed, for every claim it has ever
adjudicated. This is precisely the reviewer's "omitted qualifier", and it is total rather than
occasional.

**2. Identity mismatch in 2 of 8 artifacts.** Derived from each file's own `experiment` field
rather than its filename:

    RESULT_PROVENANCE.json        says "IQ-PORT-1-PROVENANCE"
    RESULT_CEILING_ABSTAIN.json   says "CEILING-UNDER-ABSTAIN"

Benign here — both are the rung they claim to be — but it is the **swapped experiment identity**
failure mode the reviewer named, and the gate had no way to detect it because the filename was
doing the identifying.

**3. CEILING-ABSTAIN's positive control is not in its artifact.** I ran it (the mutants dropping
0.1366 → 0.0000 under the wrapper) and reported it in prose. The RESULT json carries no
`positive_control_ran` field, so `G-INERT` fires correctly on a null result with no recorded
control. **The gate is right and my transcription was wrong** — I asserted a control the artifact
does not evidence.

## What this does and does not mean

**It does not overturn any measurement.** The INADMISSIBLE verdicts are about what the
**artifacts carry**, not about whether the falsifiers were run. IQ-PORT-1's injections, mutants
and knockouts all happened and are all in its RESULT json; what is missing is the class label the
mandatory-falsifier table needs.

**It does overturn BATTERY's validation claim.** "Six rungs admissible" was an artifact of me
filling in fields the artifacts do not contain. The honest statement is: **the RESULT schema is
underspecified for machine adjudication**, and until it is fixed, every gate verdict inherits my
typing.

**It vindicates the reviewer's ordering.** They said fix this before spending another
experimental run. Had ABLATION run first, its verdict would have entered the same unvalidated
gate and inherited the same hole.

## The fix, and what remains

Done: claim objects are now derived by fixed rule from artifact contents, identity is taken from
the artifact's own field, and **any underivable field is emitted as a note rather than guessed**
— an underivable field is a finding about the artifact, not a licence to fill it in.

Not done, and now the next concrete task: **amend the RESULT schema** so every rung records
`intervention_class`, `positive_control_ran`, and an explicit `n` per reading at write time. That
is a change to how results are emitted, not to any result already emitted.

## Deviation from my own scheduled plan, stated rather than silent

The loop instruction for this pass was to run ABLATION. I did not. The review I adopted last pass
made claim-object provenance **blocking** on further experimental runs, and ABLATION is an
experimental run. The instruction predates the review; the review supersedes it. Recording the
deviation because a scheduled plan quietly abandoned is indistinguishable from one forgotten.
