# X-MAT-INTERNALIZE: result

**Verdict: ENDOGENOUS**, by the preregistered rule (PREREG.md @ c3e9eae9e).

## Replay gate and compute

- The replay gate passed: all 26 replays reproduced their C-A3-INTERNALIZE records exactly, with 0 mismatches.
- Compute was 28,225 CPU-s, about 7.8 core-h, run locally under lease lse-e39dab75e9bd (skullport:cpu8, now released).

## Primary endpoint: 8 EVENT runs, state-free competent organisms inside L

All 8 events are ENDOGENOUS_MATERIAL. The median X is 0.020, and the largest is 0.107.

X is the XENO share of the attributed bytes, meaning bytes that were already in organisms outside L at D0, or that such organisms computed later.

| run | epoch | orgs | X | attributed | MUT |
|---|---|---|---|---|---|
| 7ae3 27000023 | 2000 | 101 | 0.000 | 0.955 | 0.045 |
| ffa6 27000012 | 1600 | 1 | 0.107 | 0.438 | 0.563 |
| ffa6 27000020 | 2000 | 19 | 0.025 | 0.569 | 0.431 |
| ffa6 27000024 | 1900 | 1 | 0.000 | 0.922 | 0.078 |
| ffa6 27000046 | 2000 | 84 | 0.027 | 0.574 | 0.427 |
| ffa6 27000048 | 2000 | 194 | 0.000 | 0.571 | 0.429 |
| ffa6 27000051 | 1200 | 11 | 0.061 | 0.814 | 0.186 |
| ffa6 27000052 | 1600 | 9 | 0.015 | 0.479 | 0.521 |

## Descriptive comparison: 18 REPLACEMENT runs

These runs are not decisive. In each of them, the state-free genomes sit outside L and have X between 0.90 and 1.00, with a median of 1.00. So the XENO tag class is populated, and it dominates where the label says the material is foreign. That is agreement between two readouts; it is not a planted-transplant control. This experiment has no test showing that a transplant *into* L would be detected (corrected per Harmonia #1057).

## Reading

- The internalization C-A3-INTERNALIZE confirmed is not a pair-tape bookkeeping artifact. The state-free genomes inside L are made of D0 founder material and of values L organisms computed.
- Almost nothing in them came from organisms outside L: their share of the attributed bytes is at most 11%, and at most 3% in 6 of the 8 runs.
- This closes the transplant/bookkeeping alternative for this claim.

## Limits

These limits were declared in the preregistration and are restated here:

1. **Mutation-made bytes are a large neutral share.** They are 18–56% of the bytes in 6 of the 8 runs. Their maker class is unknown, so the result says: *of the bytes whose maker is known, nearly all are from L*. Mutation arising inside L is endogenous by any reading. A non-L mutation that was later copied into L would be missed, but it would have to pass through a non-L-to-L copy, and the XENO share of copies is itself near 0.
2. **Two events rest on a single organism** (ffa6 27000012 and 27000024).
3. **Whole genomes, not the register-setting bytes specifically.** The endpoint is read over whole genomes.
4. **This does not test** whether the organization is task-coupled or input-gated. That remains open for the next discriminating experiment.

## Disclosures (added after Harmonia's audit, #1057)

1. **The pilot began before the freeze.** The single-core pilot (7ae3 27000023) was started before the preregistration commit c3e9eae9e (04:41:11 -04:00). It finished after it: PASS was reported at b742b3132, 04:49:00, and the pilot ran 1050 s. PREREG.md describes the pilot in the future tense. The pilot computed tags but printed only replay identity, wall time, depth and checkpoint count. No endpoint was read, and its result file was deleted before the production run. The verdict is unaffected, but the order was not as written.
2. **The verdict-bearing commit is ae38658fe.** e3f0c43d8, cited in #1054 and #1055, is the merge of that commit into main.
3. **WORK_STATE `updated_at_utc` values were wrong** at b742b3132 (11:05Z) and ae38658fe (12:40Z). They ran ahead of the true commit times, 08:49Z and 10:02Z. The values are now taken from the clock.
