# H. CALIBRATION PARTICLE SET

Historical phenomena whose causal structure is reasonably established, used as **known particles** to test whether a Prometheus detector can find a precursor *blind* — without being told the outcome (directive §20). All rows `MODEL_RECALL_UNVERIFIED`; each must be verified against primary source before it is used to pass or fail a detector.

The test protocol for every particle:
1. Give the detector the run history **truncated before the outcome**.
2. Ask it to name the precursor and the generation window.
3. Score against the established answer.
4. A detector that only recognises the precursor when given the outcome is a post-hoc narrator and must be improved or killed.

---

| cal_id | phenomenon | system | established causal structure | what a detector must recover blind | status |
|---|---|---|---|---|---|
| cal-01 | Deleterious intermediate required for a complex feature | Avida EQU (fam-013a/b) | Reward-scaffold ablation removes EQU; specific mutation reversion breaks the lineage | the deleterious step, before EQU exists | UNVERIFIED |
| cal-02 | Gene duplication precedes functional divergence | Lindgren IPD (fam-051); GP ADFs (fam-060) | duplication is neutral at creation, divergence follows | the neutral duplication, before divergence | UNVERIFIED |
| cal-03 | Speciation protection sustains initially inferior structure | NEAT (fam-097) | component ablation degrades performance | the protected structure while it is still inferior | UNVERIFIED |
| cal-04 | Neutral drift changes accessible phenotypes | RNA flow reactor (fam-147) | relay series; position-dependent transitions | which neutral positions are innovation-adjacent | UNVERIFIED |
| cal-05 | Learning converts a needle into a gradient | Hinton-Nowlan (fam-041) | analytic; widely replicated | the plasticity-driven gradient, before assimilation | UNVERIFIED |
| cal-06 | Hitchhiking causes GA underperformance | Royal Road (fam-040) | Mitchell/Forrest/Holland analysis; RMHC control | the hitchhiking event as the cause of stall | UNVERIFIED |
| cal-07 | Survival of the flattest at high mutation rate | Avida (fam-013f) | replicated; analytic | the flatter lineage overtaking the fitter one | UNVERIFIED |
| cal-08 | Modularity from modularly varying goals | Kashtan-Alon (fam-161) | environment-switching causes modularity | modularity onset tied to the switching schedule | UNVERIFIED |
| cal-09 | Connection cost produces modularity and reduces forgetting | Clune-Mouret-Lipson (fam-104) | direct manipulation of the cost term | modularity as a consequence of the cost, not the task | UNVERIFIED |
| cal-10 | Ancestry collapse: population descends from few ancestors | McPhee-Hopper (fam-071) | measured directly | the collapse generation, from population data alone | UNVERIFIED |
| cal-11 | Coevolution with parasites raises evolvability | Avida (fam-013d) | treatment vs control | the evolvability change, not just the fitness change | UNVERIFIED |
| cal-12 | Environmental exaptation (evolved radio) | Bird-Layzell (fam-191) | the circuit fails when the RF source is removed | that the solution depends on an unmodelled channel | UNVERIFIED |

---

## Notes on selection

- Particles are chosen so that **at least one is a negative for our own framing**: cal-06 and cal-05 are cases where an exciting-looking dynamic has a mundane, established cause (hitchhiking; drift after selection vanishes). A detector that flags those as reasoning precursors is producing false positives, and its false-positive rate on this set is a reportable number.
- cal-12 is the detector-failure particle: the interesting fact is not in the genome at all. Any detector that only reads genomes cannot find it, and should report that it cannot rather than inventing a genomic story.
- Particles are NOT ranked by fame. cal-10 is an obscure workshop-scale result and is one of the sharpest blind tests here, because the answer is a specific generation number recoverable from population data alone.
