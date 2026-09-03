# K. RECONSTRUCTION QUEUE

Ranked historical experiments to rebuild inside SFE. **Scores are deliberately null.** The ten §18 criteria cannot be scored from model recall: eight of them (artifact quality, reconstructability, blindness, replication leverage, counterfactual availability, composability, simplicity, information gain) depend on facts about surviving material that nobody has checked yet. Assigning numbers now would manufacture precision, and a rubric filled from recall is a fit statistic for my own priors, not a measurement.

What follows is therefore a **provisional ordering with stated reasons**, to be replaced by scored rows after the primary-source pass.

Ranking is explicitly NOT by fame (§18). Two of the top four are workshop-scale or single-paper results.

---

| rank | spec_id | why here | provenance class attainable | first question to SFE | est. cost | blocking unknowns |
|---|---|---|---|---|---|---|
| 1 | `spec-evca-density` | tiny physics; rule tables published; rare seed-dependent transition; three independent search physics found the same motif (fam-125) | REIMPLEMENTATION if GA fully specified, else APPROXIMATE | Does the particle-strategy transition recur, and at what rate with CI, over 1e4 faithful runs? | CHEAP (CPU-days) | exact GA parameters; IC sampling; whether original source survives; original transition rate |
| 2 | `spec-lindgren-ipd` | smallest physics in the registry; duplication operator is neutral at creation, which is the §14 shape exactly | REIMPLEMENTATION | Does a duplication event change the descendant mutation-effect distribution vs matched lineages? | TRIVIAL (CPU-hours) | population-dynamics details; noise model; frequency cutoff |
| 3 | `spec-rna-relay` | best original detector in the set (relay series = lineage); blindness is in replication and forks, not observation | APPROXIMATE unless era energy parameters recovered | Is transition probability position-dependent on the neutral set at 1e4 replicates? | CHEAP | 1990s ViennaRNA parameter set; exact flow-reactor protocol |
| 4 | `spec-neat-ablation` | the duplication x protection cell; original ablations measured fitness only | ORIGINAL_SPECIMEN (software) | Does speciation protection change descendant acquisition rate, not just final fitness? | CHEAP | whether original C++ NEAT builds; parameter parity |
| 5 | `spec-avida-equ-2003` | calibration particle; original detector already strong | ORIGINAL_SPECIMEN | Can a blind detector flag the deleterious intermediate before EQU? | MODERATE | config parity across Avida versions; lineage data availability |
| 6 | `spec-push-autoconstruction` | collapse frequency is an anecdote that should be a distribution | REIMPLEMENTATION / ORIGINAL | What is the collapse-rate distribution over 1e4 runs, and is it predicted by size drift alone? | MODERATE | original Pushpop availability; parameter set |
| 7 | `spec-aevol-ratchet` | ratchet is an unexplained-status anomaly with live source | ORIGINAL_SPECIMEN | Does the ratchet survive a matched-fitness randomised-structure control? | MODERATE | run lengths; config |
| 8 | `spec-mcphee-hopper-ancestry` | sharpest blind detector test in the set; trivial to rebuild | REIMPLEMENTATION | Can ancestry collapse be recovered from population data alone, blind? | TRIVIAL | exact GP parameters |
| 9 | `spec-royal-road` + `spec-hinton-nowlan` | calibration/negative pair; both trivial | REIMPLEMENTATION | Does our detector correctly attribute both to mundane causes? | TRIVIAL | none material |
| 10 | `spec-poet` | strongest modern reachability claim; expensive | ORIGINAL_SPECIMEN | Does the reachability gap survive a matched-compute curriculum baseline? | EXPENSIVE | compute budget; whether the baseline already exists in the paper |
| — | `spec-thompson-xc6216` | **NOT QUEUED.** Physics is gone (obsolete FPGA, analogue behaviour). Retained as a detector-archaeology case and as negative control neg-/cal-12. | CONCEPTUAL only | n/a | n/a | n/a |

---

## Ordering rationale in one line each

- 1 over 2 because EvCA has a **published artifact** (rule tables) that lets a reconstruction be checked against the original outcome, while Lindgren must be validated by dynamics alone.
- 3 above 4 because the RNA system's original detector was better, which makes it the sharper test of whether Prometheus instrumentation adds anything at all (directive §26 lists "modern instrumentation adds nothing" as a valid finding, and this is where we would find it).
- 5 is calibration, not excavation; it is queued to test **us**, not the 2003 experiment.
- 10 is last despite being the strongest reachability claim, because its cost buys the least archaeology per CPU-hour and the authors may already have run the decisive control.

## Promotion rule

No specimen advances from this queue to an SFE build until: primary source read, artifacts hunted and manifest rows written (or a documented "no artifact survives"), physics sheet complete with unspecified parameters enumerated, provenance class fixed, and the §25 sixteen questions answered without TBDs in the first five.
