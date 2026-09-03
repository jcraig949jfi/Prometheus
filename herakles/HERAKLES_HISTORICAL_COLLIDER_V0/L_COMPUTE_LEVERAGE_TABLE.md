# L. COMPUTE-LEVERAGE TABLE

Where modern replication changes what can be *known*, not merely what can be run faster (directive §7, §8). Every number is an order-of-magnitude **estimate from model recall**, labelled EST, and is a target for verification, not a measurement.

Cost basis: one modern desktop CPU core-hour, single machine (M1). No cluster assumed.

---

| spec_id | original runs (EST) | original compute (EST) | modern cost/run (EST) | runs affordable in 1 CPU-day (EST) | question that becomes answerable | question that stays unanswerable |
|---|---|---|---|---|---|---|
| `spec-evca-density` | 1e2-1e3 | workstation-weeks | 1-10 core-sec (bit-packed) | 1e4-1e5 | transition rate with CI; seed vs init variance decomposition; conditional P(transition given ancestral structure); mass replay from pre-epoch checkpoints | whether the 1993 team's specific runs contained it (their seeds are gone) |
| `spec-lindgren-ipd` | 1-10 | workstation-hours | <1 core-sec | 1e5-1e6 | era-length distribution; P(new dominant strategy given duplication in ancestry); no-duplication counterfactual | the exact trajectory published (deterministic core, but mutation seeds unknown) |
| `spec-rna-relay` | 1-10 long runs | workstation-weeks | 1e-3 - 1e-2 core-sec per fold | 1e7-1e8 folds | position-dependence of transition probability; neutral-set geometry around the transition; 1e4 forked replicates from a single relay point | the original energy parameter set unless recovered (results are parameter-set dependent) |
| `spec-neat-ablation` | ~100 per config | hours | seconds | 1e4-1e5 | descendant acquisition rate under protection vs not; the duplication x protection 2x2 with an evolvability endpoint | nothing material |
| `spec-avida-equ-2003` | ~50/treatment | CPU-months (2003) | 10-100 core-sec | 1e3-1e4 | population-wide frequency of deleterious intermediates that never led anywhere (the false-positive base rate the original could not measure) | whether the original focal lineage is bit-identical (unless data recovered) |
| `spec-push-autoconstruction` | 10s | hours-days | 10-100 core-sec | 1e3-1e4 | collapse-rate distribution; whether collapse is predicted by size drift alone | original Pushpop behaviour if source is lost |
| `spec-aevol-ratchet` | 10s-100s | CPU-days | minutes | 1e2-1e3 | ratchet vs randomised-structure matched-fitness control | none material |
| `spec-mcphee-hopper-ancestry` | 10s | minutes | <1 core-sec | 1e5 | ancestry-collapse generation distribution; dependence on tournament size | none material |
| `spec-poet` | ~1-5 | GPU-months | GPU-days | 1-10 | almost nothing new at our budget | the matched-compute curriculum baseline (too expensive here) |
| `spec-thompson-xc6216` | 1 | weeks + hardware | **not reproducible** | 0 | nothing | everything: the substrate no longer exists |

---

## The three places leverage is real

1. **Anecdote → distribution.** EvCA, Lindgren, Push and McPhee-Hopper all published outcomes as narratives about a handful of runs. At 1e4-1e5 runs those become distributions with CIs. This is the cheapest genuine gain in the table.
2. **Base rates the original could not see.** The Avida line is the sharpest case: the 2003 experiment could measure the deleterious intermediate *on the successful lineage*, but not how often the same intermediate appeared and led nowhere. That false-positive base rate is what decides whether "deleterious stepping stone" is a mechanism or a survivorship story, and it costs us a CPU-day.
3. **Forks the era could not afford.** Mass replay from a pre-transition checkpoint (the Blount-style replay, fam-030) was economically impossible for every system in this table except at trivial scale. SFE's fork-by-reference makes it routine.

## The two places leverage is fake

- **Running an old experiment faster tells us nothing new.** Rerunning EvCA 1e4 times and reporting a better best-of-run fitness is not archaeology.
- **Where the original detector was already good, scale buys little.** The RNA relay-series work already recorded lineages. If our contribution there is only "more replicates", the honest finding may be "modern instrumentation adds nothing" (§26). That entry is in the table deliberately, so the seat can fail publicly on its own best case.
