# Tyche calibration ledger

Currency: 2026-09-29. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently. Empty at creation:
the seat has made no calls.

date | call made | what was true | corrected by | changed practice
2026-09-30 | v0 compute "< 1 core-hour" (PREREG s6) | stopped attempt used 13.0 core-hours by gen 34/40; BLAS oversubscription (16 workers x openblas threads) plus ecology growth the 2-epoch pilot never reached | seat's own measurement (PREREG_AMENDMENT_1.md) | pin BLAS to 1 thread per worker; pilot must reach the largest ecology size a campaign can reach; campaigns carry a compute guard
2026-09-30 | H1 PASS with P1, P3, P4, P5 solved (PREREG s4) | H1 INDETERMINATE: P3, P4, P6 VOID (random lenses had access), P1 never solved | v0 REPORT.json | measure initial access over the whole initial population before freezing controls; use only zero-marginal laws as "inaccessible" controls
2026-09-30 | H3 residual shift PASS | FAIL: err residual fell on negative worlds with no accuracy change (organism decorrelation) | v0 REPORT.md F1 | every residual definition ships with its own negative control (flat on TSD/PRF as the ecology grows)
2026-09-30 | H4 redundancy PASS | FAIL: tab attention budget displaced raw channels; lenses re-supplying them were admitted | v0 REPORT.md F2 | no organism input set may depend on ecology order; cheat control for manufactured residuals
2026-09-30 | ADV_decoy solved | not solved (best val 0.114 transient, admitted lens +0.039) | v0 REPORT.md | xor-type structure is a separate, harder class; do not predict it from the planted-control reasoning
2026-09-30 | v1 P1 gate 6 PASS on Z1, Z2 both seeds | FAIL: no Z world met the predicate | v1 REPORT_v1.md | treat a counterfactual arm's "would have died" as a hypothesis to measure, not a design assumption
2026-09-30 | v1 P2 V0 solves no Z world (from my v0 reading "blind when both precursors absent") | V0 solved 3 of 10 Z cells: noisy many-case lexicase preserved useless lineages; soft precursors gave footholds | v1 F1/F2 trace | v0's P1 failure was a 40-generation budget/luck outcome, not an ontological wall; say so
2026-09-30 | v1 P4 DENR <= half of DE | DENR 2 cells vs DE 1 | v1 REPORT_v1.md | pair evaluation cost units; equal-unit budgets penalise combination arms
2026-09-30 | WORK_STATE "running: []" during the v1 runs | 26 processes live on M2 (Cyclops #1061) | Cyclops observability audit | commit `running` before launch, clear after
2026-09-30 | v1 F1: V0's Z1 lineage "survived on noise-level lexicase wins" | V0 included v0's 14-slot novelty/random reserve and its membership was not logged; mechanism unresolved | self, while designing v2 | log every preservation channel's membership; never attribute survival to one channel when two were active and only one was logged
2026-09-30 | v2 Block R memory: planned 27 concurrent workers with per-world caches sized for v1 | ~15 GB resident, host at 4.6 GB free, harness stop; runner + run processes survived the stop | seat's process audit after the stop | budget memory per worker x workers before launch; measure a pilot's peak resident size; runners must kill their process tree
2026-09-30 | v2 Block R RH1-RH4 (reserve > lexicase > strict on option value and storage; broad faster; shared precursor faster) | all FALSE: adaptation ~absent (2/72 cells); lexicase stored more fragments than the reserve; complete precursor sets never stored | REPORT_BLOCK_R.md | predict storage of precursor SETS, not fragments, as the quantity that matters; 30 post-switch generations was too short to separate arms
2026-09-30 | option-value clock design | missed coalition-built adaptations (reads population best val only) | self, analysis | clocks must read every admission route
