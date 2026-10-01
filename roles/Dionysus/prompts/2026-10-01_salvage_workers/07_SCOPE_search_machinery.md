# Scope 7: search, evolution and generation machinery

Slots to fill: the SEARCH protocol and its regimes (blind structural
variation, population search with a diversity archive, model-guided
proposals, gradient where the substrate allows), the adaptive staircase
curriculum, and the generator-divergence experiment P8
(RSE_ARCHITECTURE.md sections 6 to 8).

Requirement areas to read: section 1; SRCH-01 to SRCH-13; ANTI-01 to
ANTI-08; INF-02, INF-03, INF-05, INF-06; COMP-01, COMP-02.

Components:

1. Archaeon's GA harnesses on the Proteus VM (WSE, Campaigns 1 to 6), the
   Deep Frontier lineage scheduler (archaeon/frontier/), the reachability
   tables and the typed disposition ladder. Dossier:
   sisyphus/seats/Archaeon.md.
2. The PROTEUS-46 greedy walk (proteus/round2/falsifier_46.py) and
   whatever replaced it; the mutation-kernel crucible. Dossier:
   sisyphus/seats/Proteus.md.
3. Crius's accessibility-frontier search ((8+24) x 300) and neutral-path
   measurements. Dossier: sisyphus/seats/Crius.md.
4. Tyche's lexicase selection, cross-lineage graft and fusion, the reserve,
   and the natural-history tracer. Dossier: tantalus/seats/Tyche.md.
5. Theseus synth's QD archive and collision operator. Dossier:
   tantalus/seats/Theseus.md.
6. Apollo's routing-DAG and blackboard evolvers, crossover, the O1
   exhaustive enumerator, the E1 schedule analysis; Lexis's closure
   search. Dossiers: sisyphus/seats/Apollo.md, Lexis.md.
7. Ergon E4's GA with a persistent genotype library on the D-5 machine
   (random-walk library, shuffled-history library). Dossier:
   tantalus/seats/Ergon.md.
8. Aphrodite's enumerative search with escrow metering and paired common
   random numbers. Dossier: tantalus/seats/Aphrodite.md.
9. Ananke's GA (population 96 x 36 generations), its shaping terms, and
   the plants the search never found. Dossier: tantalus/seats/Ananke.md.
10. Model-in-the-loop generation: the Hephaestus forge and xpol_2026
    (floors.py, shape.py, knockout_ablation.py), Icarus (an LLM rewrites a
    dispatch file), Nous, and prometheus_llm (the single model-call
    module). Dossiers: ixion/seats/Hephaestus.md;
    tantalus/seats/Icarus.md, Nous.md.
11. Metis compose.py (model-free choice of the cheapest experiment that
    splits named rival explanations). Dossier: ixion/seats/Metis.md.

For each search system, answer from the source:

- the variation operators, the selection rule, and whether a child equal
  in fitness to its parent can be accepted (neutral moves);
- population size, generations and total evaluations in the largest run on
  record, and wall time, quoted from where they are recorded;
- evaluations per second, if derivable from recorded numbers;
- whether selection ever saw the worlds on which results were reported;
- whether seeds, founders and lineages are recorded so that independent
  lineages can be counted;
- whether the search is a library usable on a different organism type, or
  is welded to one organism;
- for model-in-the-loop systems: which model, what the prompt asks for,
  what filters the output, what was logged per call, and whether any arm
  without a model exists for comparison.

Also answer for the whole scope:

A. Budgets. Build one table: system, largest evaluation count on record,
   wall time, host, evaluations per second. This is to compare the
   historical budgets with the measured ceiling on M1 (about 5 billion
   toy-VM instructions per second; receipt in
   docs/phase3/design/FABLE-5.1/process/vm_throughput_bench.md).
B. Is there an adaptive staircase, or any curriculum that sets the next
   world from the organism's measured threshold? Say how you searched.
C. Is there any place where model-guided and model-free generation were
   run on the same task so their outputs can be compared?

The decision Dionysus has to make: whether to extract a shared search
library from these or write one, and what the historical budgets say about
how much reach was ever available.
