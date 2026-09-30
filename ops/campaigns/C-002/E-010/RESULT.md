# E-010 result -- steering lesion (rcv_sfx). CLOSED 2026-09-30.

Preregistration: ops/campaigns/C-002/E-010/EXPERIMENT.md, committed and pushed at 32c14e403 BEFORE any unit ran.
Code pin: 607fbe65c50d10dd25471d6e8c005072cf269670 (adds rcv_sfx; aeth03 test suite 58/58).
Reduction: `python Aether/observatory/aeth03_combinations_reduce.py ops/campaigns/C-002/E-010/attempts` -> REDUCTION.json.

## Regression gate: PASS

rcv_str seed 4 re-run at 607fbe65c (tsk-f188e8ee7b3c) gives result_sha256 6d56b9b28a07c8ee..., identical to E-009 (on both
of E-009's hosts). The lesion commit did not change any existing law. The unit is kept as
regression_E10-rcv_str-s4__A-001__fabric-*.json, outside attempts/.

## Verdict under the preregistered rule: **STEERING_REQUIRED**

| law (seeds 4-7, OFF, 128 origins) | P_sust | per seed (of 32) | P_content |
|---|---|---|---|
| rcv_str (E-009) | 15/128 = 0.117 | 3 / 2 / 5 / 5 | 0.078 |
| **rcv_sfx (lesion)** | **4/128 = 0.031** | 2 / 0 / 0 / 2 | **0.000** |
| rcv (component, E-009) | 4/128 = 0.031 | 1 / 2 / 1 / 0 | 0.016 |
| str (component, E-009) | 0/128 | 0 / 0 / 0 / 0 | 0 |

S = 4/128 <= 6/128, so STEERING_REQUIRED.
- The lesion returns sustained propagation exactly to rcv's level.
- Content differences at generation >= 5 and radius >= 5 disappear.
- Every trace of super-additivity is gone.
- The effect is lower in all four seeds (rcv_str 3/2/5/5 vs rcv_sfx 2/0/0/2). [Erratum 2026-09-30: this line first said "three of four seeds; seed 4 is 2 vs 3", but 2 < 3 is also lower. Caught by Harmonia evidence audit sample 3 (comms #1056, roles/Harmonia/audits/EVIDENCE_AUDIT_2026-09-30_SAMPLE3.md @8eafe8afe). The verdict is unaffected.]

What this establishes:
- The E-006 cause probe said rcv_str works by "activity re-routing activity via energy-steered aim". That statement is
  now supported by intervention, not only observation. Cutting the aim-energy coupling, with everything else in
  rcv_str unchanged, abolishes the effect.
- rcv_str's new behaviour is not a property of "rcv plus some other aiming rule". A static per-site re-aiming gives
  nothing beyond rcv.

What it does NOT establish (limits, stated before anyone asks):
- **Dynamic coupling vs static correlation.** The lesion removes both the tick-by-tick tracking of energy and any
  static correlation between aim and energy. A further lesion would separate them: steering by a frozen snapshot of
  each site's energy at the end of warm-up (energy-correlated but static).
- **Aim distribution.** The static offset is uniform on 0..3 (tested). rcv_str's energy>>6 term follows the energy
  distribution, which may not be uniform. The lesion therefore changes the aim distribution as well as the coupling.
  A lesion that samples offsets from the empirical energy>>6 distribution would remove this confound.
- 128 origins, one regime, OFF arm only, as in Block D.

Execution: 5 Fabric Tasks on worker.ubu001.sci (tsk-faf0ee2a8b99, tsk-a5b12c38c4fa, tsk-84d2971ced12, tsk-000a146f4107;
gate tsk-f188e8ee7b3c).
- Each result file's blob id equals its changes.patch index.
- stdout result_sha256 equals the file; 0 locality violations.
- code_sha256_lf differs from the c49f2ebad4 manifest only in observatory/aeth03_variants.py (the lesion), as
  expected.
- No native fallback was needed. About 45 min on one worker, under 1 CPU-hour.
