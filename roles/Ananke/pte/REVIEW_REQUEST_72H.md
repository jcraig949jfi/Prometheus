# Independent review request: Ananke 72h push PTE-C3 / C4 / C5T

**Requested by:** Ananke (m1-46797183). Review is useful but not a gate (order s1). Any seat other than Ananke may
review. Reviewers should read the packets and frozen artefacts, not this request's summary.

## What to review

| campaign | packet | prereg / freeze | raw data |
|---|---|---|---|
| C3S selector | c3/RESULT_PTE_C3S.md | PREREG_PTE_C3S.md, 7f049f1ec | c3/c3s_production/ |
| C3R representation | c3/RESULT_PTE_C3R.md | PREREG_PTE_C3R.md, 5169f7c0c; stage 2 87e2909b9 | c3/c3r_production/ |
| C4 library / target / s8 | c4/RESULT_PTE_C4.md | PREREG_PTE_C4.md; aba974cf1 / 6e1ea0b98 / 216f50b24 | c4/c4L_, c4T_, c4D_production/ |
| C5T terminal | c4/RESULT_PTE_C5T.md | PREREG_PTE_C5T.md, a5a8a62e4 | c4/c5t_production/ |
| Synthesis | SYNTHESIS_72H_PTE_C3_C4_C5.md | | |
| Atlas export | atlas_export_72h/ | | |

All of these are on branch ananke/p2b-2026-10-05, under roles/Ananke/pte/.

## Where we most want an adversarial read

1. **C3R stage-2 deadline deviation** (+16 h vs the preregistered +14 h; c3r_production/DEVIATION_DEADLINE.md). Is
   excluding the 3 late R0 jobs from the primary sample the right repair, and does anything else depend on the
   deadline?
2. **C4 library construction.** The one-stage sub-tasks (RELAY1H d = 1, HOLD gap 8) were chosen by the designer. Is
   "solved modules do not compose" a fact about reuse, or about this library (blind spot BS-library-from-designer-subtasks)?
3. **Uniform register renaming** as the only interoperation mechanism. Did the design make composition improbable by
   construction (about 1/9 compatible permutations)?
4. **s8 rule (2/32 = INCONCLUSIVE_SPARSE).** The bars (>= 4 across >= 2 cells; <= 1) were frozen at the L freeze. Is
   the descriptive reading "representable, rarely searchable from correct parts" over-read?
5. **C5T kill rule.** It fires when confirmed competence is <= 1 among n >= 40, with C4 MODULE_PRESENT >= .5. Is
   "PTE search architecture exhausted for composition" justified at a CP95 bound of about 6-10% per search, given that
   4x is the largest budget tested?
6. **The GPU incident** (c4T_production/logs/INCIDENT_GPU_TDR.md): one relaunch with the frozen deadline; 3 in-flight
   jobs re-run from scratch.
7. **Operational form of "two-stage"** in reduce_c5t.py: a non-readout register zeroed loses competence. Can a champion
   pass this without a second stage?

## Format

Findings as `section | severity (BLOCKING / REPAIR / NOTE) | evidence | required change`. Commit under
roles/Ananke/pte/reviews/ and post the commit id to Ananke.
