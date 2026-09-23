# Candidate 3rd, 4th and 5th ecosystems (Atlas, 2026-09-19) -- PROPOSED

Operator request (verbatim): roles/Atlas/prompts/2026-09-19_alife_survey/.
Evidence: the ecosystem catalogue (roles/Atlas/catalog/ECOSYSTEMS.jsonl,
atlas.ecosystem on M1: 352 external systems + 4 Prometheus rows, 834
references, 642 marked VERIFIED by the surveyors). These are proposals for
the seats that run engines; Atlas runs none of them and admits nothing
(templates are admitted by a human; archaeon/templates/inbox/README.md).

## Where we are (catalogue matrix, world x organism)

All four Prometheus ecosystems sit in two cells: program_memory x
machine_code / tree-tape genomes (SFE campaigns, DEEP FRONTIER, NPE CW01)
and graph x policy (NPE GraphWorld). Environment generation is fixed or
procedural in all four; none co-evolves its worlds. The external field is
densest where we are absent:

    text_or_code x llm_program            25  (FunSearch, AlphaEvolve, OpenELM ...)
    discrete_grid x policy (UED)          22  (PAIRED, ACCEL, PLR, JaxUED, Craftax ...)
    program_memory x machine_code         17  (Tierra, Core War, BFF/cubff, Evochora ...)
    discrete_grid x ca_pattern            17  (von Neumann ... Evoloop, SproutLife ...)
    discrete_grid x neural_net            16  (Geb, NCA family, JaxLife ...)
    physics_3d x morphology+controller    13  (Sims, Framsticks, DERL, Revolve2 ...)
    continuous_field x kernel_params      12  (Flow-Lenia, Leniabreeder, ASAL++ ...)
    chemistry x reaction_rules             9  (Squirm3, Fraglets, AlChemy line ...)

## Recommended

    rank  ecosystem (catalogue id)   axes it adds                          why now
    ----  -------------------------  ------------------------------------  ----------------------------------------
    E3    bff-computational-life     program soup; IMPLICIT replication    closest to our organisms, opposite
          (cubff, Apache-2.0, GPU)   pressure                              pressure; known transition = controls;
                                                                           internal dossier 74
    E4    flow-lenia (JAX)           continuous field; intrinsic           Lenia specimen + Harmonia ASAL ruler
                                     multi-species evolution               already in house (techne, roles/Harmonia)
    E5    jaxued / accel (JAX)       grid worlds; environment              the POET line, cheap and maintained;
                                     CO-EVOLUTION                          POET specimens in house as the reference
    ref   avida (runnable fossil)    digital organisms in a task world     deepest internal coverage (Techne,
                                                                           Ergon, Nyx, Harmonia); comparator
    ref   evogym (MIT, CPU)          2D bodies + controllers               morphology axis, cheap

Alternates worth a smoke test: evochora (Java, 2025; program soup with
energy), aevol (genome structure, CPU), symbulation (symbiosis), leniabreeder
(QD over Lenia), craftax / xland-minigrid (open-ended RL benchmarks).

## The experiments (EXPERIMENTS.jsonl, XE-01..XE-12)

Each one transplants a named Prometheus finding (its parent keys and the
finding, verbatim, from the index) into one or more of these substrates.
Each carries the three controls of base role s2 (positive, negative,
cheat), a falsifier, a kill condition, a claim ceiling and what SURVIVED
would NOT license, in the shape the campaigns and inbox templates use.
Budgets are deliberately ESTIMATE only: measure-then-size with a smoke
test per substrate.

    XE-01 damage-cliff census across substrates          <- C4-01, C5-05, LIN-cb15a0ad
    XE-02 length-mediated robustness beyond the SFE      <- C5-08 (supersedes C4-07)
    XE-03 selection vs neutral drift on damage loss      <- T-ARCH4/M1 (CW01)
    XE-04 deleterious load at mutation-selection balance <- T-X18, T-X16 (CW01)
    XE-05 residue transport between co-evolving worlds   <- SFE-03, SFE-07
    XE-06 flat elite: equal-total-compute across searches<- LIN-ffc7ae5d (PROVISIONAL)
    XE-07 implicit vs explicit pressure, same substrate  <- C5-09, SFE campaigns
    XE-08 stasis and escape in a continuous ecology      <- CW01 loop
    XE-09 recombination rate and dominance direction     <- T-X14 (CW01)
    XE-10 historical transitions as detector calibration <- LIN-6071e54d, frontier detectors
    XE-11 co-evolution vs curriculum vs randomisation    <- catalogue matrix gap
    XE-12 chemistry organisations under our rulers       <- C4-01, C4-05

## Honest limits

- The catalogue is surveyor output. url_status is theirs; Atlas did not
  re-fetch 834 links. Classification axes are single labels per system and
  flatten hybrids.
- No proposal here has been sized, piloted or checked by the owning seat.
  Suggested owners are suggestions.
- XE-07's task-coupled arm cites a 2026 Z80 paper whose code is not public;
  the arm would be a cubff variant built here, not a reproduction.
