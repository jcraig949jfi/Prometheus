# E-011 result -- trace lesion (rcv_adr). CLOSED 2026-09-30.

Preregistration: ops/campaigns/C-002/E-011/EXPERIMENT.md, committed and pushed at 1c7b3249d BEFORE any unit ran.
Code pin: 0fd9e6ca1196986eb7b93316a6abd19de34589af (adds rcv_adr; aeth03 test suite 61/61).
Reduction: `python Aether/observatory/aeth03_combinations_reduce.py ops/campaigns/C-002/E-011/attempts` -> REDUCTION.json.

## Regression gate: PASS

rcv_add seed 4 re-run at 0fd9e6ca1 (tsk-00d9b9adcb0e) gives result_sha256 0ac4a1cec53a3c22..., identical to E-009. No
existing law changed. The unit is kept as regression_E11-rcv_add-s4__A-001__fabric-*.json, outside attempts/.

## Verdict under the preregistered rule: **PARTIAL**

| law (seeds 4-7, OFF, 128 origins) | P_sust | per seed (of 32) | P_content |
|---|---|---|---|
| rcv_add (E-009) | 22/128 = 0.172 | 5 / 6 / 6 / 5 | 0.164 |
| **rcv_adr (lesion)** | **10/128 = 0.078** | 2 / 0 / 4 / 4 | 0.070 |
| rcv (component, E-009) | 4/128 | 1 / 2 / 1 / 0 | 0.016 |
| add (component, E-009) | 1/128 | 0 / 0 / 0 / 1 | 0.008 |

S = 10/128 lies between the TRACE_REQUIRED bound (<= 7/128, the additive null 5/128 plus 2) and the
TRACE_NOT_REQUIRED bound (>= 13/128). The result is **PARTIAL**, as preregistered, and no further seeds are run.
Descriptively:
- the lesion is lower than rcv_add in all four seeds;
- it removes about 12 of the 17 origins of super-additivity above the additive level (22 -> 10 against 5);
- it still sits above the additive level.

Reading at its width:
- Stopping relay-won writes from accumulating removes most of rcv_add's excess, so compounding relay traces carry a
  large share of the effect. The cause probe's "persistence of activity traces" is PARTLY supported by intervention.
- **The lesion is incomplete by construction.** It makes RELAY writes replace, but later WRITE-site writes still ADD
  onto whatever a relay wrote. A relay's trace can therefore still persist, carried forward by later add-writes.
- So the residual (10 against 5) cannot be read as "a second mechanism". It is at least partly this leak.
- A complete lesion would need add-writes onto relay-written values to replace too, which needs per-site provenance of
  the last writer. That is the value-provenance idea (rank 3), which exists nowhere in the code yet.
- The contrast with E-010 is informative. rcv_str's effect vanished completely when one coupling was cut.
  rcv_add's effect is spread across a mechanism that a one-rule lesion cannot fully isolate.
- 128 origins, one regime, OFF arm only, as in Block D.

Execution: 5 Fabric Tasks on worker.ubu001.sci (tsk-5e03e4878646, tsk-e3141de95e38, tsk-a3751385973c, tsk-ac21bf162439;
gate tsk-00d9b9adcb0e).
- Each result file's blob id equals its changes.patch index.
- stdout result_sha256 equals the file; 0 locality violations.
- code_sha256_lf differs from the c49f2ebad4 manifest only in observatory/aeth03_variants.py.
- No native fallback was needed. Under 1 CPU-hour.
