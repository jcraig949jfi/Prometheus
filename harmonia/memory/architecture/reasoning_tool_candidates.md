# Reasoning-Tool Candidate Catalog

## Seed population for a two-level evolutionary search over reasoning instruments

> **Companions:** [`topological_falsification_engine.md`](topological_falsification_engine.md)
> (the doctrine these candidates serve) and [`bottled_serendipity.md`](bottled_serendipity.md)
> (the per-claim thesis). Drafted by Harmonia_M2_B, 2026-05-27, from James's directive:
> *"literally build all VAR and NEW and simply score the results. Each tool becomes a genome to
> recombine with other ideas."*

---

## How to use this catalog (read before building)

This is not a to-do list; it is the **seed population of a two-level evolutionary system**:

- **Object level** — reasoning genomes (atoms → molecules → organisms) evolved *by* the tools.
- **Meta level** — the **tools themselves are genomes**: a tool-genome is a configuration over
  `(mutation operator, selection lens, KillVector basis, diversity scheme, assembly operator,
  coverage instrument)`. Recombination = swap components between configurations. This is literally
  candidate **#40 (hyper-heuristics)** applied to the entire catalog — the catalog eating itself.

**The build-all directive is sound; the scoring is the entire game.** Build cost ≈ 0, so building
all [VAR]+[NEW] is cheap and correct. But "*simply score the results*" is exactly where the doctrine's
knockouts bite:

- **Don't score on the current bar.** This whole catalog exists *because* the current selection bar
  (NCD compression, survival count, kill count) is rank-1 / Goodhart-prone (see engine-doctrine §6 Q2:
  the live KillVector basis is rank-1). Scoring 85 tools on one ruler breeds a **tool-monoculture** —
  every tool converges on whatever games the score.
- **Score each tool by its MARGINAL contribution to kill-space coverage / effective dimensionality.**
  A tool is good iff it produces deaths/structure *no other tool reaches*. This is the meta-version of
  the near-miss insight: it rewards orthogonality among tools and is the natural fitness for "each tool
  is a genome." It prevents the monoculture by construction.
- **Run MAP-Elites over tool-behavior**, not a single leaderboard — protect diverse tools (Invariant B).
- **Sequencing prerequisite:** build the shared harness FIRST (#23 domain-general basis, #26 multi-gate
  instrumentation, #83 cross-swarm KillVector bus, #84 eff-dim dashboard). Without a shared basis +
  coverage metric, 85 tools are scored in 85 incomparable units and cannot be ranked or recombined —
  the scores are noise.
- **The binding constraint moves from build-cost (~0) to eval-cost + eval-integrity.** That is where
  both the value and the Goodhart risk now live.

**Tags:** [NEW] new technique · [VAR] variation of existing · [OSS] wire in open source ·
[REV] reverse-engineer / sleeping-beauty. **Roles:** MUT mutation · SEL selection · BASIS kill-vector ·
DIV diversity · ASM assembly · COV coverage · META loop-closing.

---

## 1 — New mutation operators (near-miss generators · MUT)
1. [NEW] LLM near-miss operator — prompt for plausible-but-wrong candidates targeted just inside the first gate, so downstream falsifiers fire (direct test of the rank-1 audit's prediction).
2. [NEW] Constraint-conditioned hallucination — "satisfy G1, violate exactly one of G2…Gn" → forces candidates into each near-miss shell, lighting up individual KillVector axes.
3. [VAR] Forbidden-move prompting — MPA forbidden-move constraints (no named approaches, no literature) push mutations off the published manifold.
4. [VAR] Temperature × multi-model ensemble sweep — find the (novelty × survival) sweet spot; each model = a different prior shape.
5. [NEW] LLM semantic crossover — recombine two surviving atoms inheriting both load-bearing morphemes (vs syntactic splice).
6. [NEW] Representation-shuffle mutation — restate in a foreign representation (categorical/geometric/probabilistic) and mutate there (escapes Erebos M2→M4 lock).
7. [NEW] Kill-replay mutation — seed with a past kill-cluster ("here's how X died; mutate to survive that death") → voids bias mutation.
8. [VAR] Nemesis-as-mutator — adversary mutates atoms toward its own blind spots, not just makes traps.
9. [VAR] Diff/patch mutation on Forge atoms — Icarus-style git-diff mutation with apply-recount discipline.
10. [NEW] Grammar-constrained generation — constrain to the typed reasoning-morpheme grammar → fewer compile-error deaths, more semantic deaths.
11. [REV] Analogy-engine mutation — Hofstadter Copycat/Metacat "slippage" as a structured mutation operator.

## 2 — Selection / evaluators (incorruptible, anti-Goodhart · SEL)
12. [VAR] Shared deterministic Contract Lens — generalize Icarus's (cardinality/type/monotonicity/exception) into one non-LLM evaluator all machines call.
13. [NEW] Frame/null pre-check gate — Invariant A: block-shuffle / Pattern-4 / null_protocol BEFORE mechanism-knockout (F044 mirage guard).
14. [OSS] Formal-verification lens — Lean4+Mathlib, Coq, Z3/cvc5, E/Vampire as un-gameable selectors for formalizable claims.
15. [OSS] Property-based battery — Hypothesis/QuickCheck with shrinking → minimal counterexamples (KillVector-emitting).
16. [REV] Metamorphic-testing lens — metamorphic relations (Chen) as oracle-free correctness checks.
17. [OSS] Mutation-testing as selection — mutmut/cosmic-ray: does the suite kill injected bugs? Catches vacuous-pass.
18. [VAR] Ablation gate v2 — measure accuracy_delta not output_change (Apollo's fix); require lift over best single primitive.
19. [NEW] Hidden calibration anchors — model-invisible known truths/falsehoods catch any drifting channel.
20. [VAR] Cross-model jury w/ independence discount — 3+ seeds × 2+ families, shared-training-data correction.
21. [VAR] Process-supervision scorer — step-level reward; Theseus StepRecord already supports it.
22. [REV] Interventional (do-calculus) knockout — Coeus causal layer as causal ablation, stronger than correlational.

## 3 — KillVector basis / kill-space geometry (BASIS)
23. [NEW] Domain-general KillVector basis — replace the Lehmer-specific 12-component basis so math & reasoning share one.
24. [NEW] Basis orthogonalization pass — compute the deferred component covariance; prune/merge collinear axes (out_of_band≈F9); report effective dim.
25. [NEW] Learned KillVector embedding — autoencode "how it died" from failure traces → emergent higher-rank basis.
26. [NEW] Multi-gate instrumentation — record ALL falsifier margins per candidate (not first-failing) (the rank-1 fix).
27. [NEW] Reasoning-side KillVector — basis = failure_class × tier × detected_by (Icarus taxonomy); unify with math-side.
28. [NEW] Near-miss shell sampler — generate at controlled distance from each gate to densely sample each axis.

## 4 — Diversity / quality-diversity (anti-monoculture · DIV)
29. [NEW] MAP-Elites over the KillVector basis — niches = kill-space cells; monoculture structurally forbidden.
30. [OSS] Novelty search / NSLC — reward behavioral novelty, no objective; antidote to convergent Goodhart.
31. [OSS] pyribs (CMA-ME / CMA-MAE) — modern maintained QD archives.
32. [REV] Fitness sharing / crowding — classic Goldberg/Holland niching.
33. [OSS] POET — co-evolve traps and atoms so neither stagnates (Nemesis generalized).
34. [VAR] Diversity-as-admission-gate — Hephaestus Gate B, but distance in the KillVector basis not NCD.
35. [OSS] Lenia / Avida / Tierra — primordial-soup ALife substrates for emergence + order parameters.

## 5 — Assembly: atom→molecule→organism (ASM)
36. [VAR] Typed-state blackboard composer — Apollo Branch C (already beat gen-3551 elite 41% vs 36%); no Frankenstein seams.
37. [OSS] DreamCoder — wake-sleep library learning: builds molecules AND abstracts new atoms (the ratchet, automated).
38. [OSS] egg / egraphs — equality saturation; Rosette & Sketch for solver-aided synthesis.
39. [OSS] GP over typed atoms — DEAP, PushGP/Clojush, PonyGE2 (grammatical evolution).
40. [REV] Hyper-heuristics — evolve WHICH atoms to compose (Burke et al.). **= the organizing principle for build-all (see top).**
41. [NEW] Abstraction operator — after N survivors, mine recurring sub-compositions, promote to named atoms (DreamCoder "sleep" as a Forge-tier).
42. [OSS] Tactic/proof assembly — Lean tactic search / TacticToe / GPT-f behind a hard verifier.
43. [OSS] Hierarchical-RL option discovery — options / feudal nets: auto-discover reusable sub-policies.
44. [OSS] Compositional-generalization benchmarks — SCAN, COGS, CFQ, PCFG-SET (anti-Goodhart for assembly).

## 6 — Coverage / void cartography (COV)
45. [NEW] Coverage order-parameter — density on the KillVector basis → exhausted void vs thin void (fixes Ergon false-exhaustion).
46. [OSS] Persistent-homology void map — TDA (ripser/giotto-tda/GUDHI) on the kill-space cloud → holes = literal voids.
47. [OSS] Active-learning probe placement — BO/GP uncertainty places next mutation where the void map is least certain.
48. [VAR] Kill-cluster cartographer — Icarus kill_clusters generalized AND fed back into generation.
49. [NEW] Frontier/Pareto-shell tracker — track the moving always-dies ↔ sometimes-survives boundary.

## 7 — Variations on existing machines (VAR)
50. [VAR] Forge T4 — compose T1+T2+T3 through the KillVector basis instead of NCD lenses.
51. [VAR] Hephaestus void-mode — forge tools aimed at persistent failure modes, not random concept triples.
52. [VAR] Apollo fitness = kill-space dimensionality — train small LLMs to maximize eff-dim of the kill-space they produce (reward near-misses). Direct operationalization of the audit.
53. [VAR] Icarus invariant fixes — mandatory Skeptic-debt integration tests; move Generator/Integrator off LLM selection seats.
54. [VAR] Nous demand-driven mining — mine from VACUUM/EXHAUSTION signals (build where the void is thinnest).
55. [VAR] Nemesis↔atom POET loop — close coevolution on a shared archive.

## 8 — Open-source to wire in (OSS · capability → project)
56. Program synthesis: DreamCoder, egg, Rosette, Sketch, Barliman, PROSE.
57. Theorem proving / SMT: Lean4+Mathlib, Coq, Isabelle/Sledgehammer, Z3, cvc5, E, Vampire, ACL2.
58. ILP / logic induction: Popper, Metagol, Aleph, clingo (ASP).
59. GP / QD: DEAP, PushGP, PonyGE2, pyribs, PyGAD, Karoo GP.
60. Symbolic regression: PySR, Operon, gplearn.
61. Probabilistic program induction: Church/WebPPL, Gen.jl, NumPyro.
62. Cognitive architectures: Soar, ACT-R, OpenCog/AtomSpace, OpenNARS, CLARION.
63. Geometry/diagram: AlphaGeometry (open-sourced), GeoGebra discovery, JGEX.
64. Graph/combinatorics discovery: nauty, AutoGraphiX, Mace4/Prover9.
65. Testing oracles: Hypothesis, mutmut, cosmic-ray. TDA: ripser, giotto-tda, GUDHI.

## 9 — Sleeping beauties / zero-citation / abandoned code (REV — the rich vein)
*The algorithm is the asset, not the code. Reimplement each as a KillVector-emitting mutation operator or selection lens. Check provenance/licensing.*
66. AM & EURISKO (Lenat 1976–83) — canonical never-reproduced discovery system; reverse-engineer heuristics as mutation operators. The sleeping beauty.
67. Graffiti (Fajtlowicz 1986+) — made graph-theory conjectures mathematicians proved; original good-conjecture machine.
68. HR / HR3 (Colton) — automated theory formation; partial code; number-theory conjectures.
69. BACON / DALTON / STAHL / GLAUBER (Langley–Simon 1980s) — rediscovered physical laws from data; near-miss law generators.
70. Copycat / Metacat / Tabletop / Letter Spirit (Hofstadter & FARG) — fluid analogy under slippage; reimplementations to fork.
71. Schmidhuber lineage — OOPS, Gödel Machine, PowerPlay (invents its own problems), Levin/Universal Search → open-ended atom factories.
72. Holland LCS / XCS (Wilson) — rule discovery under credit assignment; orthogonal evolutionary substrate.
73. Logic Theorist & GPS (Newell–Simon) — means-ends analysis as an assembly operator.
74. Gelernter Geometry Machine (1959) — diagram-as-pruning-heuristic; a non-LLM near-miss filter.
75. NARS (Wang) — reasoning under insufficient knowledge/resources; alternative inference substrate.
76. Qualitative reasoning — de Kleer/Forbus QP theory; causal/qualitative engines as selection lenses.
77. Friedberg (1958) self-modifying programs / Fogel evolutionary programming (1966) — abandoned roots of program evolution.
78. Otter/EQP (McCune — solved Robbins conjecture) — paramodulation heuristics as reusable selection.
79. OEIS conjecture engines — superseeker / Sloane transforms; auto-conjecture over integer sequences.
80. Mining method — sleeping-beauty detection via citation-burst / "beauty coefficient" (Ke et al. 2015); scrape Bitsavers, SourceForge graveyards, university FTP, arXiv/DBLP; point Stygian/Pythia surveys at abandoned-code hunts.

## 10 — Meta-instruments (close the loop · META)
81. [VAR] Consolidator — the ROADMAP's #1 net-new agent: promote outputs into substrate (the missing consumer).
82. [NEW] Yield tracker — did an artifact trigger a downstream action? training signal for a learned scorer.
83. [NEW] Cross-swarm KillVector bus — one shared kill-space so all agents' deaths land in the same basis ("reactions, not nodes").
84. [NEW] Effective-dimensionality dashboard — track kill-space rank per machine over time (the order parameter, productionized).
85. [NEW] Tool-build autopilot — LLM scaffolds a new candidate + its tests + its KillVector emitter on request, born wired to the shared basis. The "1000 cheap machines" engine done right.

---

## Gradient (fastest-compounding given the rank-1 audit)

Minimal rig that turns the 1-D ruler into a real map and proves/kills the masterstroke:
**#1** (near-miss operator) + **#26** (multi-gate instrumentation) + **#29** (MAP-Elites over the
KillVector basis) + **#84** (eff-dim dashboard). Highest-variance / highest-novelty bet: the
sleeping-beauty vein, **#66 (AM/EURISKO)** especially.

## Build order for "build all and score"

1. **Shared substrate first:** #23 + #26 + #83 + #84 (basis, multi-gate, bus, dashboard). Without it,
   tool scores are incomparable.
2. **Coverage-based fitness:** #45 + #49 — define "marginal kill-space coverage" so a tool's score is
   *how much of the map it reaches that others don't*.
3. **Tool-genome encoding + MAP-Elites over tool-behavior:** #29 + #40 — recombine tool configs;
   protect diverse tools.
4. **Then mass-build [VAR]+[NEW]** as the seed population and let the meta-search run.
