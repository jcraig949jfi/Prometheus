# K. RECONSTRUCTION QUEUE

> **SUPERSEDED IN PART, 2026-09-03.** The ruling `roles/Herakles/prompts/RULING_V0_CONTINUE_HYPOTHESIS_DAMAGED_2026-09-03.txt` (sha256 `31816dc2...0811a`) replaces the flat ranking below with a two-track order: **recover the microscopes first, reconstruct the specimens second.** The per-specimen reasoning underneath remains valid and is retained.

## The execution order, as ruled

The old order (Avida, then EvCA, then RNA) is withdrawn. The phase splits into **historical microscope recovery** and **historical specimen reconstruction**.

### H1 — Recover the evolvability microscopes. NO COMPUTE.

Before running any Prometheus detector, deeply reconstruct what the field already built:

- **Altenberg 1994.** The exact evolvability quantity; what the Price-theorem derivation actually implies; what assumptions it requires; what constructional fitness is; and which parts were mathematical argument versus experimental measurement.
- **Mengistu, Lehman and Clune 2016.** Precisely how offspring behavioural diversity is calculated; how many offspring; what mutation distribution; what generalisation measure; what the metric detects and what it fails to detect.
- **Their antecedents from 2011 onward.**

These feed `Q_DETECTOR_PARTS_REGISTRY.md`. The governing rule: **do not invent a Prometheus-native measure before asking whether the field already has a better-developed quantity.**

### H2 — EvCA reconstruction. First actual archaeological specimen.

EvCA moves ahead of Avida, for a reason that emerged only after verification. The Physica D paper documents a **failure transition**: symmetry breaking produces short-term fitness improvement while blocking discovery of superior strategies. Short-term gain leading to a representational trap leading to reduced future reachable capability is precisely the shape this programme exists to detect.

The verified 7/300 rate in the PPSN III configuration gives a measurable event rate, and 10,000 repetitions yields hundreds of expected events if the historical rate reproduces. **Gated on artifact recovery** (see the hard gate below).

### H3 — Avida.

Ergon retains the deep Avida job. But Avida must not carry the whole Historical Collider thesis. It becomes the **historical dependency and precursor-circuit** specimen.

### The resulting detector suite

| Specimen | What it tests |
|---|---|
| EvCA | future-accessibility **collapse** |
| Avida | historical **accumulation** and stepping stones |
| Altenberg / Mengistu | evolvability **measurement itself** |

---

## HARD GATE ON COMPUTE (ruling authorisation 5)

> **No evolutionary compute runs until at least one specimen reaches `ARTIFACT_IN_HAND`, or a reconstruction is proven sufficiently exact.**

This binds the seat. A reconstruction is "proven sufficiently exact" only when its output distribution is checked against a published artifact of the original, which for EvCA means the hex rule tables and the reported transition rate. Reading the parameters from a paper is necessary and **not** sufficient.

Artifact recovery for the correct EvCA 7/300 configuration is authorised to proceed in parallel with H1 (authorisation 4) and is currently the critical path.

---

## The original per-specimen ranking, retained

Ranked historical experiments to rebuild inside SFE. **Scores are deliberately null.** The ten §18 criteria cannot be scored from model recall: eight of them (artifact quality, reconstructability, blindness, replication leverage, counterfactual availability, composability, simplicity, information gain) depend on facts about surviving material that nobody has checked yet. Assigning numbers now would manufacture precision, and a rubric filled from recall is a fit statistic for my own priors, not a measurement.

What follows is therefore a **provisional ordering with stated reasons**, to be replaced by scored rows after the primary-source pass.

Ranking is explicitly NOT by fame (§18). Two of the top four are workshop-scale or single-paper results.

---

| rank | spec_id | why here | provenance class attainable | first question to SFE | est. cost | blocking unknowns |
|---|---|---|---|---|---|---|
| 1 (H2) | `spec-evca-density` | **verified**: tiny physics, complete parameter set in print, documented failure transition (symmetry breaking traps the search), measured 7/300 event rate | REIMPLEMENTATION (parameters confirmed) | Does the transition recur at 7/300, and is the pre-transition state special? | CHEAP (CPU-days) | **artifact recovery for validation** (hex rule tables, code); GATED ON COMPUTE RULE |
| 2 | `spec-lindgren-ipd` | smallest physics in the registry; duplication operator is neutral at creation, which is the §14 shape exactly | REIMPLEMENTATION | Does a duplication event change the descendant mutation-effect distribution vs matched lineages? | TRIVIAL (CPU-hours) | population-dynamics details; noise model; frequency cutoff |
| 3 | `spec-rna-relay` | best original detector in the set (relay series = lineage); blindness is in replication and forks, not observation | APPROXIMATE unless era energy parameters recovered | Is transition probability position-dependent on the neutral set at 1e4 replicates? | CHEAP | 1990s ViennaRNA parameter set; exact flow-reactor protocol |
| 4 | `spec-neat-ablation` | the duplication x protection cell; original ablations measured fitness only | ORIGINAL_SPECIMEN (software) | Does speciation protection change descendant acquisition rate, not just final fitness? | CHEAP | whether original C++ NEAT builds; parameter parity |
| 2 (H3) | `spec-avida-equ-2003` | historical accumulation and precursor circuits; **must not carry the whole thesis** | ORIGINAL_SPECIMEN | Population-wide base rate of deleterious intermediates that led nowhere | MODERATE | assigned to Ergon; config parity; lineage data availability |
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
