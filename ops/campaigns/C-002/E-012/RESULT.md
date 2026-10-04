# E-012 result -- frozen-energy lesion (rcv_sfz). CLOSED 2026-10-04.

Preregistration: ops/campaigns/C-002/E-012/EXPERIMENT.md @ 7b7dea59e (pushed before any run). Code pin 1b4fb4523ea764ee...
Reduction: `python Aether/observatory/aeth03_combinations_reduce.py ops/campaigns/C-002/E-012/attempts` -> REDUCTION.json.

Regression gate: **PASS**. rcv_str seed 4 at 1b4fb4523 (tsk-3e9b029b8340) gives 6d56b9b28a07c8ee..., identical to E-009, so
the edited assay module and variant module leave existing laws unchanged.

| law (seeds 4-7, OFF, 128 origins) | P_sust | per seed (of 32) |
|---|---|---|
| rcv_str (E-009; dynamic energy-steered aim) | 15/128 | 3 / 2 / 5 / 5 |
| **rcv_sfz (aim frozen at the warm-up energy snapshot)** | **6/128** | 0 / 2 / 1 / 3 |
| rcv_sfx (E-010; static random aim) | 4/128 | 2 / 0 / 0 / 2 |
| rcv alone | 4/128 | 1 / 2 / 1 / 0 |

**Verdict under the preregistered rule: DYNAMIC_COUPLING_REQUIRED.** S = 6/128 <= 6/128. P_content is 1/128.

Stated plainly: S lands EXACTLY on the boundary. One more sustained origin would have made it PARTIAL. This is the same
"passes by a tie" shape that R-05 criticised in Block D, and it is recorded the same way:
- the mechanical verdict is DYNAMIC_COUPLING_REQUIRED;
- the evidential reading is that freezing the aim at energy-correlated values leaves rcv_str at or within 2 origins of
  rcv's level, far below rcv_str's 15/128;
- static energy correlation recovers at most a small fraction of the effect.

Together with E-010 (static random aim, 4/128): rcv_str's super-additivity needs aim that keeps TRACKING energy as it
changes. Neither a static random aim nor a static energy-correlated aim reproduces it.

Execution: 5 Fabric Tasks on worker.ubu001.sci.
- Each result file's blob id equals its patch index; stdout result_sha256 equals the file; 0 locality violations.
- Code hashes differ from the c49f2ebad4 manifest only in observatory/aeth03_variants.py and
  observatory/aeth03_propagation.py, as expected.
- The analysis was delayed from 2026-09-30 to 2026-10-04 because the seat loop's wakeup did not fire; the units were
  complete and untouched in the meantime.
