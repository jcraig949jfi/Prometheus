# A. PRIMARY SOURCE LEDGER

**Status: T0 IN FLIGHT. Nothing in this ledger is confirmed yet.**

Directive: `roles/Herakles/prompts/DIRECTIVE_HC_T01_TOUSSAINT_MISSING_CELL_2026-09-03.txt`
sha256 `5cc0241fe85567e71201416cd16a88fd0672ff5cc4ae921996606e33c30b0354`

Every row must eventually carry: `source_id`, exact title, year, venue, page/section/figure, the exact historical claim, `evidence_source`, and an artifact hash where held.

## Provenance of these candidates

The URLs below were read by a prior verified research pass on 2026-09-03 (`DETECTOR_SURVEY_2026-09-03.md`), which reported them at `PRIMARY_SOURCE_READ`. **For HC-T01 they are demoted to candidate leads**, because this seat has not itself fetched them and because the directive says plainly: do not cite titles from memory.

GATE-5 applies: a citation in a brief carries the same evidence tier as a registry row. This seat has already caught itself supplying two paper titles that exist in no author's bibliography, so every row below must resolve to a real bibliographic record before it is load-bearing.

| candidate | reported role | reported locator | status |
|---|---|---|---|
| Toussaint 2001, arXiv physics/0102009 | Monte Carlo estimate of exploration density over a tracked population | Figure 4; reported 10,000 samples per time step | AWAITING T0 |
| Toussaint PhD thesis 2003 | detector applied population-wide and longitudinally | section 1.5.3, Figure 1.6, "Features of the phenotypic exploration distribution averaged over the population"; reported 2,000 samples per individual per generation, 1000 generations | AWAITING T0 |
| Toussaint PhD thesis 2003 | THE ABLATION | reported "Experiment 2", second-type mutations at beta 0.1 vs 0, 10 trials per cell, described as 2x2 | AWAITING T0 -- the 2x2 claim is specifically doubted and must be checked |
| Toussaint, FOGA VII 2003, "On the evolution of phenotypic exploration distributions" | formal definition, sigma-embedding and sigma-evolution theorem | reported NO figures and NO simulation | AWAITING T0 |
| Toussaint, arXiv nlin/0212030, "The structure of evolutionary exploration" | theorems plus schematic figures | reported no measurement | AWAITING T0 |
| Toussaint & Igel, CEC 2002 | population-averaged quantity over 10,000 generations, with a fixed-parameter ablation | reported outcome is a unimodal 100-d sphere | AWAITING T0 -- if the outcome is optimisation speed rather than acquisition, T3 is unavailable |

## The two numbers under specific scrutiny

A prior pass reported **two different sample counts** in two different works: 10,000 samples per time step (2001 paper) and 2,000 samples per individual per generation (thesis). Both are being verified. They are not obviously the same estimator, and the cost model in `HC_T01_COMPUTE_MODEL.md` depends on which is correct and on what its unit is.

## Known trap recorded before it bites

A prior pass in this programme found that the two papers whose **titles** most directly promise exploration-distribution measurement contain none: they are pure derivation. Anyone grading this literature from titles would mis-rank it badly. The measurement lives in the 2001 paper and the thesis, not in the papers named after the concept.
