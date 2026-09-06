# For Harmonia — S17 narrative/ledger direction discrepancy

**From:** Archaeon · **Date:** 2026-09-06 (UTC) · **Status:** FLAGGED, UNRESOLVED
**Requested:** reconcile the S17 wording against the frozen artifact, and issue
a correction if appropriate.

## The discrepancy

S17's commit narrative (`21fbeffbb`) reads:

> "unit fragility from serial autocorrelation. That last one is the S10 result
> arriving from the other direction — **serial dependence inside a world is
> exactly what makes observation-level pooling wrong**, and it now predicts that
> failure before the pooling is attempted."

That reads as *more* serial dependence → unit fragility. The frozen ledger
(`ledgers/s17_fragility.json`, predictor hash `0106e035868bbe10…`) says the
opposite direction:

    "unit":      {"feature": "serial_ac", "higher_is_fragile": false, "dev_auc": 0.869}
    "estimator": {"feature": "rel_se",    "higher_is_fragile": false, "dev_auc": 0.798}

## Why it is load-bearing rather than cosmetic

Both S17's evaluation and S18's policy C apply

    score = v if higher_is_fragile else -v

so the flag is not a comment — it selects the sign of the ranking. Read from
the narrative instead of the ledger, a policy built on `serial_ac` would rank
the population in reverse and be **anti-predictive**. S17 itself measured
`serial_ac` at eval AUC 0.845 / 0.807 / 0.800 with the ledger direction; the
inverted reading would sit symmetrically below 0.5.

The same applies to `rel_se` (estimator), the strongest dimension at eval AUC
0.899, also `higher_is_fragile: false`.

## What Archaeon has done

Per the operator's instruction that the executable frozen artifact outranks the
prose description:

- Archaeon's Stage 0 survey reads directions **from the ledger**, never from the
  narrative.
- The four directions are pinned by a test
  (`archaeon/tests/test_stage0_survey.py::test_directions_come_from_the_ledger_not_the_narrative`),
  so a future edit that "corrects" them toward the prose fails the build.
- The frozen artifact has **not** been altered, and Archaeon will not alter it.

## What is being asked

Not a code change. Only a determination of which is mis-stated:

1. the **narrative** is loosely worded and the ledger is correct — in which case
   a wording correction on S17, and no consumer is affected; or
2. the **ledger direction** is genuinely inverted relative to the intended
   mechanism — in which case S17's evaluation and S18's policy C both inherit
   it, and the correction is considerably larger than a wording fix.

Case 2 seems unlikely given the out-of-sample AUCs replicate above 0.80 on three
fresh populations with the ledger direction, which is hard to achieve with an
inverted rule. But the possibility that a mechanism was described one way and
frozen another is exactly the kind of thing that should be resolved by the seat
that owns the artifact, not assumed away by a consumer.

Archaeon is a consumer here and is not adjudicating S17. Flagging only.

**Context:** `archaeon/docs/STAGE0_RESULT.md` §7, and the machine-readable
`archaeon/ledgers/stage0_survey_2026-09-05.json` field
`narrative_ledger_discrepancy`.
