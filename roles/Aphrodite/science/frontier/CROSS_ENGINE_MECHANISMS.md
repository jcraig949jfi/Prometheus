# Cross-engine mechanisms relevant to open-ended improvement -- survey for Aphrodite

Date: 2026-09-27. Read-only survey of C:\Prometheus (main checkout, not pulled) by a subagent
for the Aphrodite seat. Nothing was run. Every claim cites the seat's own file; the numbers
are as those files report them and were not re-derived. Pure ASCII.

Aphrodite baseline assumed here (from the caller): a tiny fixed integer DSL of fold programs
over lists; a donor learns hole-bearing schemas from its own successes and passes them to
descendants as a library. The recursion test ("does inherited schema G1 help discover a NEW
schema G2?") returned NO. Task supply is external, fixed and mostly additive. There is no
coevolution, no representation expansion, and the improvement mechanism is fixed.

Best maps of the engine ecology (read these first, they are short and current):
  roles/Archaeon/ENGINE_LANDSCAPE_2026-09-25.md          one table of 9 engines (lens, deps, borrowing)
  roles/Artemis/threads/sfe_retrospective/ENGINE_LENS_CARDS.md   lens cards incl. "How it has lied"
  roles/Artemis/threads/sfe_retrospective/notes/C_engines.md     ~40-row inventory + Ares/Crius notes
  (NPE = Nestor Primordial Engine; BEE = Bellerophon's Worlds Kernel + z80atlas. Both confirmed there.)

-----------------------------------------------------------------------------------------------
## 1. The five most useful findings for Aphrodite (ranked)

1. CRIUS: EXISTENCE vs ACCESSIBILITY -- the closest prior result to Aphrodite's recursion NO.
   Crius built a world where procedure reuse (record / invoke / compose) demonstrably PAYS
   (block control 46.1 vs 20.7; typed transplant 6/6/6 vs code-only 1/1/0), then showed that
   0 of 36 searches across a substrate ladder A-D ever REACHED it. The diagnosis was made by
   building the mechanism's parts by hand and pricing every partial: recorder alone -0.001,
   invoker alone -0.002, recorder+invoker +1.138 at 26 edits, everything +15.974 at 47 edits --
   "a one-link valley at B and a cliff at C". Selection kept donated parts' generic scaffolding
   (constants, loops) and dropped their typed links; it found "invocation without content"
   (a store invoked dozens of times with zero effect).
   (crius/CRIUS_C2_TERMINAL_REVIEW.md s3-s5; roles/Crius/)
   PORT (cheapest, high value): split Aphrodite's NO into existence vs accessibility. Hand-write
   a G2 that USES G1, confirm it pays (existence), then price its partials (G2 minus each
   component, G2 with G1 hole-filled vs raw) to draw the value landscape between the donor's
   library and G2. If G2-with-G1 pays but its partials are neutral or negative, the NO is an
   accessibility valley, not absence of recursion. Also log whether descendants invoke G1
   "without content" (called, no effect on success).

2. NESTOR/NPE E-8: THE DISCOVERY BARRIER IS ENCODING LENGTH.
   In the Z80 world, spontaneous replication from random bytes was 0/47 with every other
   barrier relieved; giving ALLOC/LDIR/BIRTH additional 1-byte encodings (same semantics, no
   program supplied) gave 13/40 vs 0/40 fresh cells (Fisher p = 3.8e-5). "The remaining
   probability mass is consumed by assembling a 6-byte ordered op chain; at 3 bytes it is found."
   (roles/Nestor/FINDINGS.md E-8; campaigns/c9x-explore-2026-09-24/c_dense_confirm/)
   This is the empirical case for "new primitive invention = shortening the encoding of a
   useful chain". An inherited schema is exactly such a shortening -- IF the search that looks
   for G2 enumerates over schemas as atoms. PORT: measure, for each candidate G2, its
   description length in (a) raw DSL tokens and (b) DSL + library-atoms. If G1 does not shorten
   G2's shortest encoding, the recursion test could not have succeeded by construction (a
   design check, not a new experiment). If it does shorten it and discovery still failed, the
   search is not treating G1 as an atom (a wiring defect -- see Nestor lesson 9 below).

3. HARMONIA B1 vs B2: "FLAT TERRAIN" vs "INSTRUMENT CANNOT EXPRESS IT".
   A recurring "0 novel laws" was shown to be an expressiveness ceiling: the miner found 2/2
   in-class catalogued laws and 0/12 out-of-class -- "perfect recall inside the class, zero
   possibility outside it". Fix = hypothesis-class diversity, not more search.
   (roles/Harmonia/AUDIT_20260622_instrument_monoculture.md; reusable script named there:
   harmonia/experiments/hypothesis_class_coverage_audit.py)
   PORT (cheap, analysis only): hand-curate ~15-20 known useful fold-program idioms beyond
   G1 (e.g. scan, zip-fold, nested fold, fold with pair accumulator). Classify each as
   expressible / not expressible by the schema grammar (holes, arity, nesting), then run
   discovery on the expressible ones. In-class all found + out-of-class none = B2: Aphrodite
   needs representation expansion, not a better improver. That is the direct test of whether
   "no representation expansion" is the binding constraint.

4. BELLEROPHON/BEE: MAINTENANCE vs ACQUISITION, and the YOKED control.
   Coupling computation to copy resources kept seeded task code alive in 6/6 tasks (ON ~0.77
   competent vs OFF/YOKED ~0), but genuine ACQUISITION from no task code happened only at the
   simplest rung (ECHO K40: 29/150 ON vs 6/150 in each control) and never from random soup
   (0/3,200). Heritability 99.9% was "copy fidelity ... not an evolved property". YOKED gets the
   ON run's total bonus tick by tick, spread evenly, and still goes extinct -- the effect needs
   CONTINGENCY, not supply. Its proposed next campaign asks exactly Aphrodite's question: can
   coupling carry copiers "up a task ladder beyond ECHO (acquisition of the next task given the
   previous one)".
   (roles/Bellerophon/coupling_2026-09-24/COUPLING_CAMPAIGN_REPORT.md s2, s5;
   NEXT_MULTIDAY_CAMPAIGN.md -- design only, not run)
   PORT: (a) report Aphrodite gains in two columns: MAINTENANCE (library preserves/re-solves what
   the donor solved) vs ACQUISITION (new schema not in the donor). Only the second is recursion.
   (b) add a YOKED library arm: same library size and invocation cost, schemas drawn from a
   donor that solved DIFFERENT tasks (or random hole-bearing schemas), so "any library helps"
   separates from "this library helps". Aphrodite already has SHAM/MEMORISE arms; check whether
   they are matched on library size and cost the way YOKED is.

5. ARCHAEON CAMPAIGN 3: A CURRICULUM LADDER THAT WORKED, AND A SUMMIT NO LADDER REACHED.
   Positive: a delay ladder (train delays 0/1/2/4) made 11/12 seeds general, and all 11 solved
   never-trained delays 8 and 16 at 1.0, vs matched-budget direct search 0/6 (d8) and 1/6 (d16).
   Negative: a K=2 "summit" needing a two-value keyed memory was reached 0 times in 24 + 54 runs,
   under reward shaping, and from mature seeds; measured geometry: 1 useful child in 4,800,
   0/58 second-stream gains kept the first stream, 0/480 greedy 3-step paths. Also: "IMPORT
   TAKEOVER IS MECHANICS, NOT CAPABILITY" -- opcode-permuted incompetent imports took over as
   often as mature solvers (12/12 vs 12/12).
   (archaeon/campaign3/CAMPAIGN_REPORT.md s0 items 1-5, s4)
   PORT: (a) a graded task ladder is the cheapest endogenous-curriculum substitute: order the
   existing task families so each rung is one schema-extension from the previous one, and
   compare ladder vs shuffled order at equal budget (the C3 design, directly). (b) the
   "permuted-import" control: pass descendants a library whose schemas are syntactically
   scrambled (same size, same holes, wrong semantics). If descendants adopt it as readily,
   adoption rate is not evidence of useful inheritance.

-----------------------------------------------------------------------------------------------
## 2. Per-engine entries

Format: WHAT (with paths) / MECHANISM bearing on open-ended improvement / WHAT IT FOUND (negative
findings and diagnosed cause first) / PORT to Aphrodite (cheapest form, or "no useful connection").

### 2.1 NPE -- Nestor Primordial Engine (Nestor, M1)
WHAT: primordial/ (~66k LOC, GPU swarm, CW01 declarative worlds) + roles/Nestor/campaigns/
  (Z80 x Atlas byte organisms that ALLOC/write/BIRTH their own child). Ledger:
  roles/Nestor/FINDINGS.md; status roles/Nestor/STATUS.md (window closed 2026-09-26).
MECHANISM: autonomous hypothesis graph (roles/Nestor/EXPERIMENT_GRAPH.jsonl, graph.py:
  SIGNAL -> CONFIRM; null -> localize/targeted/orthogonal) -- a self-generated research agenda
  with frozen confirm steps; P-11 causal-copy certificate (randomized-victim assay) for heredity.
FOUND:
  - Headline shrinkage: 1,031 "replicators" -> 57 under P-11; max causal depth 2 (E-3). 910 were
    splice artefacts: fidelity was read AFTER the world's own recombination operator (Z80A-D05).
  - E-6: non-pair heredity needs self-location; spontaneous DISCOVERY is the barrier.
  - E-7: depth-1 wall = newborn starvation (child starts with energy 0); conserved half-energy
    transfer at birth: 20/40 vs 4/40. A resource-inheritance fix, not a program fix.
  - E-8: discovery barrier is encoding length (see s1 item 2).
  - E-10: the recombination splice PREVENTS runaway heredity (7/150 runaways with splice off vs
    0/150 on); C-CRITICAL-MASS: 4 founders vs 1 raise depth>=5 from 5/80 to 41/80 --
    "establishment-limited". Lesson 12: an apparent superadditive founder effect vanished when
    the null's parameters were fitted on all arms (LRT p = 0.42).
  - C9 H1: four arms identical to the last decimal because a gate was never passed from world
    to task (C9-D16). Lesson 9: "Identical arms are a defect signature, not a null."
PORT:
  - Encoding length (s1 item 2). Cheapest: a static description-length table, no runs.
  - Critical mass: pass descendants libraries from k donors (k = 1 vs 4) instead of one. If
    G2 discovery is establishment-limited, multiple donors should move it. Fit the dose curve
    jointly before calling any effect superadditive (lesson 12).
  - Resource inheritance analogue (E-7): if descendants pay search budget to evaluate inherited
    schemas before they can exploit them, check whether that cost starves them at birth
    (a "newborn starvation" of search budget). Cheap to check from existing logs if per-
    descendant budget spend is recorded.
  - Lesson 9 audit: confirm the recursion-test arms actually differ in what the searcher sees
    (library present in the enumeration, not only in the object). A NO with arm outputs
    identical to the last decimal would be this defect, not a result.
  - Lesson 7 ("measure a copy where it happens"): if schema extraction reads programs after
    any mutation/canonicalisation step, the library may be crediting that step.

### 2.2 BEE -- Bellerophon Worlds Kernel + z80atlas (Bellerophon, M2)
WHAT: prometheus/toolbox (Experiment IR -> compile/execute/replay, wraps others' worlds),
  prometheus/z80atlas (256-byte tapes, real LDIR), roles/Bellerophon/coupling_2026-09-24/.
MECHANISM: coupling a useful-computation reward to the copy resource (computation ->
  resource -> reproduction -> heritable variation); controls ON / OFF / YOKED / SHUFFLED /
  RANDOM_REWARD / DELAYED / IRRELEVANT; replay 606/606 and 341/341.
FOUND: maintenance yes, acquisition only at the lowest rung; heritability = copier fidelity;
  P5 (protection of computation) unmeasurable at ceiling; 12/19 auto-candidates survived
  without coupling or task; earlier 72 h campaign: all five historical flag classes collapsed
  in forensics (roles/Bellerophon/forensics_2026-09-23/).
PORT: see s1 item 4 (MAINTENANCE vs ACQUISITION columns; YOKED library arm). The "task
  ladder beyond ECHO" in NEXT_MULTIDAY_CAMPAIGN.md is a design Aphrodite could run faster
  than BEE because its programs are deterministic and cheap.

### 2.3 AGE -- Aether (Aether, BUCKKEEP + RunPod)
WHAT: 2-D torus of executable matter, five uint8 fields per site, NO organism, NO birth
  primitive (Aether/AETHER_CONCEPT.md; Aether/AETH-03/PHYSICS_DESIGN_01_2026-09-26.md,
  PHYSICS_DESIGN_02_2026-09-26.md; roles/Aether/STATUS.md).
MECHANISM: one-change physics ladder (one assumption changed at a time, no added state,
  preregistered kill thresholds) and the twin / light-cone assay: fork two worlds differing by
  one bit and measure how far and how long the difference travels.
FOUND: "in all six laws, a single-bit difference stays within about one site of where it was
  made for 500 ticks ... the substrate lacks propagation, not only memory. History cannot
  matter hundreds of ticks later if an intervention cannot matter two sites away."
  Four of five one-change candidates made the world MORE static; the fifth (add) was 83%
  trivial counting. Ladder 2 (2026-09-26): mov/m4 killed, add closed, rcv = weak real
  propagation of activation timing. Also: +128% change rate came from a 250-tick-stale
  comparator (instrument defect).
PORT: the light-cone assay is the right diagnostic for "does G1 influence later discovery at
  all". Cheapest form: two descendant lineages identical except one library entry (G1 present
  / G1 removed, same seed), run K generations, and measure the divergence footprint: how many
  later-discovered schemas, tasks solved or search paths differ, as a function of generation.
  Footprint ~0 after one generation = "the library lacks propagation" in Aether's sense: G1
  is used but never changes what is discovered next. That localizes the NO better than a
  single end-of-run success count.

### 2.4 CWE -- Cosmos World-Graph Engine (Cosmos, M2)
WHAT: three hand-written executable worlds + CSPRNG-sealed holdout worlds D/E/F; a small law
  miner (prometheus/cosmos/; roles/Cosmos/).
MECHANISM: "change almost everything and measure what refuses to change"; predictions
  hash-receipted before holdout reveal; per-family location gate.
FOUND: law A held on sealed worlds (BA .983/.972/.930) but agreed 97.5% with the author's own
  task economics -- "rediscovery, not discovery"; active sampling did not beat random (.790 vs
  .788 at B=30; .807 vs .831 at B=60; roles/Cosmos/calibration/LEDGER.md: "treat random as the
  default until a sampler beats it"); one author wrote every substrate, hence holdout D sealed
  by Nestor (author separation).
PORT: author-separated sealed task families. Aphrodite's task supply is written by the same
  seat that designs the improver, the CWE failure mode. Cheapest: ask another seat (or a
  frozen generator with a sealed seed) for one held-out integer task family, used only to
  score G2 transfer. Also: any Aphrodite task-selection heuristic should be compared against
  random task order first (CWE P4 lost).

### 2.5 WTP / Tensor World Engine -- Ensorain (M2)
WHAT: World Genome JSON -> tensor-field worlds; organisms are bounded memory substrates
  (ensorain/; roles/Ensorain/STATUS.md; ensorain/E0_VERDICT.md; ENSORAIN_WTP02_REPORT.md;
  WTP02_OPERATOR_RULING.md; ENSORAIN_WTP03_REPORT.md).
MECHANISM: preregistered MECHANICAL scorer that emits EXPAND / DEEPEN / PARK; null ladder
  N0-N6; admission -> lineage -> mutants -> crossover -> hybrid chain.
FOUND:
  - E0 "CHOO CHOO": INDETERMINATE (positive control failed: planted learner R^2 0.007); F1:
    "The task rewards COARSE structure, not a faithful representation" -- learners with R^2 ~0
    harvested ~2x NOMEM; evolved gains were "generic tuning, not discovered physics" (class-0
    genome gained as much on class 1).
  - WTP-02: frozen scorer said EXPAND; the sole specimen was a one-float running mean; operator
    ruling "PARK/REDESIGN ... treats the discrepancy as the result": a post-hoc constant
    predictor explained the whole signal, which defined the next null class.
  - WTP-03: mechanical DEEPEN (9 flags, 4 lineages) = known bounded tensor completion; a
    post-data tuned same-class null (N6) beat every specimen. Crossovers 0/12 replicated;
    no superadditive hybrid. W2: "ADMISSION PRE-SELECTS THE PHENOMENON"; W3 founder
    concentration (174/181 admitted were mutants of 13 founders).
PORT:
  - N6-style null for Aphrodite: the best TUNED same-class baseline (e.g. an enumerator given
    the same total budget plus the best hand-written schema set of the same size) must be
    beaten before a descendant gain counts as improvement-of-improvement. Cheap if the
    enumerator already exists.
  - E0 F1 is a warning about Aphrodite's tasks: if tasks can be passed by coarse structure,
    schemas that "work" need not be faithful abstractions. Check a sample of solved tasks for
    solutions that pass tests without being the intended fold.
  - Recombination: WTP's 0/12 replicated crossovers is a prior against expecting schema
    recombination to help for free; if Aphrodite adds recombination of schemas, pre-register
    a replication check.

### 2.6 PTE -- Ananke Packet-Tensor Engine (Ananke, M1)
WHAT: integer sites exchanging lossy/delayed packets; genomes = 16-opcode straight-line
  programs under a GA (prometheus/ananke/; roles/Ananke/pte/C1_REPORT.md, C1_ERRATA.md).
MECHANISM: a capability ladder L1 perturbable -> L2 distal influence -> L3 discoverable ->
  L4 reuse/adaptation, and mechanism labels from ablation patterns.
FOUND: communication-dependent RELAY laws causally verified and size-free (0.875-0.893 up to
  N=2304) but rare (8/352), topology-bound (0.500 on a random graph) and 0 cross-family
  TRANSFER_SUPPORT; XOR/FLIP no signal. F3: "The PREREG labels missed two of the three most
  interesting mechanisms because the causal rules encoded the mechanism we expected. Opening:
  mechanism labels from the ablation PATTERN (a fingerprint over all controls)". F5: 22
  "transfers" were the same condition rerun. F6: promote by ablation-pattern novelty.
  Seeding in "living" cells gave no advantage.
PORT:
  - Novelty by ablation fingerprint (cheap, reusable): represent each discovered schema by the
    vector of task outcomes when it is removed / hole-randomized, not by its syntax. Two
    syntactically different schemas with the same fingerprint are the same mechanism; a new
    fingerprint is a new KIND. This is a better novelty measure for "new schema" than string
    or AST distance.
  - F5 check: verify that Aphrodite's "new task" variants actually change something the
    program reads (a variant that changes an unread parameter is a rerun, not transfer).
  - L4 reuse ladder is a ready vocabulary for grading G1 -> G2 (within-family reuse vs
    cross-family transfer).

### 2.7 Crius -- accessibility frontier (Crius, M2, CLOSED 2026-09-23)
WHAT: 4-tuple mod-16 hidden-op world, 8-register bytecode Player VM, costed workspace
  (crius/; crius/CRIUS_C2_TERMINAL_REVIEW.md; roles/Crius/).
MECHANISM: substrate ladder that makes each link of a reuse mechanism cheaper (typed
  procedures, mental application, recombination donors = frozen PARTS), gated by existence
  controls (block control, bytecode control) that separate "the world rewards it" from "search
  finds it"; paired common-random streams; sealed streams.
FOUND: see s1 item 1. Also: the invocation log recorded register R0 instead of the real
  argument (instrument defect, repaired with regression test).
PORT: s1 item 1. The PARTS-transplant pricing is directly implementable on fold programs.

### 2.8 Archaeon -- campaigns 1-6, causal lens, ENVGATE (Archaeon, M2)
WHAT: archaeon/campaign{1..6}, archaeon/wse, archaeon/frontier (DEEP FRONTIER lineage
  scheduler), archaeon/causal_lens (portable birth-attribution lens), archaeon/envgate*.
MECHANISM: environment as the manipulated variable with organism physics frozen; byte-level
  taint separating executor / executed material / contributors / host; paired sham arms on
  shared streams; import/transplant assays.
FOUND:
  - C3: ladder curriculum success + unreachable summit + permuted-import control (s1 item 5).
  - C4 (on Proteus's VM): "mutational damage is a cliff, not a slope -- 0/5,472 single edits
    and 0/2,280 multi-step edits improved a parent; large connected neutral network"
    (Artemis notes/C_engines.md, commit 8f1a82ced).
  - C5 "ESCAPE THE NEUTRAL CLIFF": a new representation created a real bounded-variation
    boundary but "no arm under either representation raised an elite's held-out reward ... in
    any of 96 cells" -- BOUNDARY_CREATED_NO_DISCOVERY_GAIN (archaeon/campaign5/CAMPAIGN_REPORT.md).
    I.e. a representation change alone changed how programs die, not what search discovers.
  - Causal lens: parent-chain tracing credited the HOST 8-42x more than genetic tracing;
    26/63 inert hosts "gave births" by foreign execution (roles/Artemis/.../ENGINE_LENS_CARDS.md).
PORT:
  - Attribution for inherited schemas: when a descendant solves a task with a library call,
    record which parts of the final program came from the schema vs from hole fills vs from
    fresh search (taint by token). Credit to "the library" should be the schema-authored
    share, not the fact that the library was consulted. Cheap if the program AST is kept.
  - C5 is a caution for representation expansion: measure discovery gain at equal compute,
    not just changed variation statistics.
  - RA-1 (Atlas proposal, s2.12) asks whether DEEP FRONTIER queue pools acted as a curriculum;
    no answer yet.

### 2.9 Ares -- pressure-engineering sandbox (Ares, M2, PARKED)
WHAT: generic graph organisms (ADD MUL MAX MIN THRESH GATE TANH DIFF CONST), GA P=128 G=120,
  worlds W1-W13 each run with pressure present / absent / shuffled (ares/DESIGN_C0.md,
  ares/ARES_CYCLE1_REPORT.md, ares/ARES_CYCLE2_REPORT.md; roles/Ares/STATUS.md).
MECHANISM: an abstract pressure in the WORLD (not in the objective) changes the kind of
  machinery a dumb search finds; forbid-arms force mechanism substitution.
FOUND: memory machinery appears under hidden-regime pressure (W4 champions 40/40, no-memory
  -> 2.6); function replicates 7/7 but structure is idiosyncratic; recurrence wins by BASIN
  WIDTH (14/23 viable) not peak (keep 33.75 in a 3/25 sliver); GA seeds 1-3 reproduced
  earlier lineages byte for byte, so "10 seeds" were 7 independent; a best-of-N swap statistic
  flipped a gate.
PORT: basin-width analysis explains which schemas a searcher finds: count, for each candidate
  G2, how many programs in the search neighbourhood reach it (viable-region width) vs how good
  it is. Cheap on an enumerable DSL. Also a seed-independence check (hash descendant libraries
  across seeds; identical libraries are not independent replicates).

### 2.10 Nyx -- mechanism archaeology / Chop Shop (Nyx, M3)
WHAT: nyx/ (atlas of 123 fossil systems, mechanism ledger, frozen prediction packets);
  roles/Nyx/STATUS.md; roles/Nyx/journal/2026-09-19.md;
  roles/Nyx/prompts/2026-09-19b_next_pipeline_direction/TO_HARMONIA_poet_packet_frozen.md.
MECHANISM: cuts published open-ended systems (POET, ASAL, Avida...) into organs, freezes
  exact predictions about each organ, and has another seat adjudicate them on the fossil's
  own bytes.
FOUND (MECH-POET-NOVELTY-ESTIMATOR-001, frozen 291a22ed, ruling still pending as of 09-25):
  POET's novelty estimator (novelty.py:18-62) (1) CHANGES WHAT IT MEASURES at archive size k
  (argsort()[:k] silently returns fewer than k: whole-archive dispersion below k, local density
  at/above k); (2) is SCALE-BLIND (normalize=False hardcoded, so the declared norm vector
  [8,8,8,3,3] is never applied; ratio 8/3 instead of 1.0); (3) conflates absence with zero;
  (4) deflates monotonically (0 increases over archive sizes 5..40, 2.89 -> 0.236) because the
  archive is never pruned while the active set is FIFO-pruned. Nyx explicitly does NOT claim
  these change POET's trajectory. MECH-ASAL-OE-SCORE is EVIDENCE_SUPPORTED: the ASAL scalar
  admits exploit turbulence as well as coherent life.
PORT: if Aphrodite adds a novelty score for schemas (k-nearest distance to an archive), avoid
  all four pathologies: fixed k with an explicit small-archive regime, normalised features,
  distinct encoding for absent vs zero, and a declared archive policy (a never-pruned archive
  makes novelty decline by construction -- a built-in "stagnation" signal that is an artefact).

### 2.11 Techne -- acquisition, fossil capsules, lineage relations (Techne, M3/M2)
WHAT: techne/ (fossil vault, capsule records with lineage_relations);
  roles/Techne/POET_ALIFE_AUTOPSY_LEDGER_2026-09-17.md.
MECHANISM: provenance-graded capsules for external systems; lineage_relations edges.
FOUND: (a) ASAL open-endedness score measured on synthetic frames: static 0.875, coherent
  drift 0.865, two-frame cycle 0.75, iid random 0.039 -- "iid random frames 22x more open-ended
  than coherent drift"; the metric rewards frame-to-frame dissimilarity and nothing else.
  (b) POET throws away parent ids, PATA-EC at admission, rejected children and their novelty
  ("thin fossils"). (c) TerraLingua's artifact phylogeny is inferred after the fact by text
  match or an LLM, not logged provenance. (d) Record defect found by Nyx: 46 lineage_relations
  use "target" where 112 use "to".
PORT: (a) any "open-endedness" or novelty scalar Aphrodite adopts must first pass the
  random-output cheat: a descendant that emits random / junk schemas must NOT score as more
  novel than a coherent lineage. (b) Log rejected candidate schemas and their scores, and the
  parent id of every schema, at creation time -- Aphrodite's lineage should be provenance,
  not reconstruction. Lineage-tracking libraries pinned by Techne: phylotrackpy, hstrat,
  alife-data-standards, MODES toolbox (s6 of the autopsy ledger).

### 2.12 Atlas -- cross-engine index and the prior-art experiment menu (Atlas, M1 PG)
WHAT: atlas/ (registry.json, harvesters, Postgres schema atlas); roles/Atlas/catalog/SCHEMA.md;
  roles/Atlas/proposals/2026-09-21_prior_art_raid/{PRIOR_ART_EXPERIMENT_MAP.md,EXPERIMENTS.jsonl}.
MECHANISM: a catalogue whose "pressure" field vocabulary includes novelty, quality_diversity,
  minimal_criterion, coevolution, environment_coevolution, curriculum_regret.
FOUND: none of the open-endedness experiments has been run (status counts: IDEA 15,
  NEEDS_DONOR 4, READY_FOR_DESIGN 15). Atlas indexes 5 of ~19 engines; Aphrodite is not in the
  registry (ENGINE_LANDSCAPE s4).
PORT: the menu contains Aphrodite-shaped questions nobody owns:
  - AL-1 "Fixed vs mutable interpreter" (does letting the copying/interpreting machinery mutate
    change dynamics?) -- the direct analogue of Aphrodite's fixed improvement mechanism.
  - UED-1 "Which environment-selection mechanism expands the reachable capability frontier
    fastest at equal compute?" (PLR / ACCEL / PAIRED / minimal criterion); UED-2 "Do
    learnability estimators create invisible selection bias?"
  - F5-5 "Self-generated tasks and rewards without evaluator collusion"; EV-8 "What fraction of
    apparent improvement is evaluator exploitation?"; F5-6 "new KINDS, not just better scores".
  Cheapest: register Aphrodite's runs with the lens triple (varies / holds fixed / observes) so
  convergence with other engines is visible, and claim AL-1 or UED-1 as a scoped Aphrodite
  experiment if the operator wants one.

### 2.13 Cyclops / Aporia -- Selective Irreversibility program (SI stewards, M2/M1)
WHAT: roles/Cyclops/prompts/2026-09-25_selective_irreversibility/01_OPERATOR_DIRECTIVE_verbatim.md;
  Ensorain's WTP-LM01 is the first engine campaign under it (ensorain/PREREG_WTP_LM01.md).
MECHANISM: fleet-wide hypothesis to FALSIFY: a bounded, reusable, generalizing adaptive system
  requires relevance-selective elimination of distinctions from accessible state; "A purported
  reversible counterexample does not count if it merely ... accumulates unpriced memory".
FOUND: no verdicts yet surveyed.
PORT: Aphrodite's library is additive and (as described) unpriced -- exactly the thing the
  directive says hides the question. Cheapest relevant experiment: cap the library at M
  schemas with a charged invocation/enumeration cost, compare pruning policies (FIFO, least-
  used, relevance-selective by ablation fingerprint, random) on G2 discovery. It would also
  be the first SI evidence from an improver (not a world) engine. Operator/steward
  authorization applies to SI campaigns (STATUS of Nestor/Ensorain: SI campaigns only on
  operator direction).

### 2.14 Ludus -- world foundry / bench (Ludus, M2)
WHAT: ludus/ (30 executable worlds, 1,338 catalogued); roles/Ludus/CYCLE_001_ceiling.md,
  CYCLE_002_stochastic_stopping.md, STATUS.md.
MECHANISM: before measuring anything in a world, test whether a measurable band exists
  between a trivial heuristic and the agent ("CEILING-1"); gate worlds by exhaustive depth
  profile; cheat controls on the instruments.
FOUND: Cycle 001 "the band is empty" (three worlds authored to be strategic could not separate
  an affordable agent from four plies of trivial search); GATE-W1 admitted Nim, which a
  four-line closed form solves; a sampled depth reading sat exactly on the gate where the
  exhaustive value was 0.240.
PORT: a band check for Aphrodite's tasks: for each task family, the gap between (i) a plain
  enumerator at budget B and (ii) the best library-equipped descendant. Families where the
  enumerator already solves everything (or nothing) cannot show recursion; drop them from the
  G1 -> G2 test. Cheap, uses existing runs.

### 2.15 SFE -- Serendipity Foundry Engine (Daedalus, M2, DORMANT)
WHAT: SerendipityFoundry/SerendipityFoundryEngine/ -- a provenance ledger, not a world.
MECHANISM: predictions sequenced before observations; loser-keeping selection families;
  executed-vs-requested config attestation.
FOUND: Campaign 1 transfer positives died at n >= 10 under common random numbers (0/10
  supported); 98% of row time was ledger round-trips.
PORT: Aphrodite already freezes an AMENDMENT before each step. The transferable piece is
  loser-keeping: record every candidate schema a donor considered and rejected, so "how many
  were tried before G1 was kept" is recoverable. Otherwise no useful connection.

### 2.16 Proteus -- Player Foundry (Proteus, M2)
WHAT: proteus/ (25-op player VM, mutation machinery); roles/Proteus/*REVIEW_PACKET*.txt.
FOUND: "zero marginal drift is not neutrality"; the mutation operator was not dynamically
  neutral (V0.6 packet). Its VM is where Archaeon measured the 0/5,472 mutational cliff.
PORT: if Aphrodite's search uses a mutation operator over fold programs, check that its
  stationary distribution over program shapes is not itself biasing which schemas appear
  (run the operator with no selection and compare schema frequencies). Low priority.

### 2.17 No useful connection found (checked, briefly)
  - Vivarium (roles/Vivarium/): data plane / runner / queue for SFE rows. Orchestration only.
  - Daedalus (roles/Daedalus/): SFE owner; see 2.15.
  - Theophrastus (roles/Theophrastus/): analysis lens on the SFE+PEW stack (crucible, specimen
    ledgers); nothing on improvement dynamics found in the excerpts read.
  - Harmonia beyond B1/B2: qualification / ruler harness; adjudicates others' packets.
  - Odysseus (odysseus/): sharded spiking circuit, "v0 is an instrument". No connection yet.
  - Herakles EVCA (herakles/evca): CA density-classification library; too little campaign
    evidence to assess.
  - docs/weekly_recap_2026-09-19.md and pivot/agent_roster_2026-09-27.md: the recap is a
    Campaign-6-era summary and the roster is a process/liveness list; neither maps engines
    usefully. Use ENGINE_LANDSCAPE and ENGINE_LENS_CARDS instead.

-----------------------------------------------------------------------------------------------
## 3. Prometheus-wide conventions Aphrodite should reuse

1. LENS TRIPLE: varies / holds fixed / observes (Archaeon ENGINE_LANDSCAPE s4; Artemis
   ENGINE_LENS_CARDS). Aphrodite's: varies the improvement process's inherited library; holds
   fixed DSL, task supply, improvement mechanism; observes paired saving vs SHAM/MEMORISE/
   POSITIVE. Publish it; Aphrodite is not yet in Atlas.
2. "HOW IT HAS LIED" field: every engine's headline was cut down by its own forensics (NPE
   1,031 -> 57; BEE 5/5 flag classes; Aether +128%; WTP 9/9 = known completion; CWE law A =
   author's economics; PTE missed readout tick). Keep a running list for Aphrodite.
3. EXISTENCE vs ACCESSIBILITY (Crius) and MAINTENANCE vs ACQUISITION (BEE): report any
   improvement claim in these two splits.
4. B1 vs B2 (Harmonia): before concluding "no recursion exists", measure the expressiveness
   coverage of the schema grammar against a hand-curated catalogue.
5. CONTROL VOCABULARY: OFF / YOKED (same total supply, no contingency) / SHUFFLED / RANDOM_REWARD
   (BEE); present / absent / shuffled pressure (Ares); permuted-import (Archaeon C3); sealed
   author-separated holdouts (CWE); best tuned same-class null N6 (WTP); planted-truth recovery
   (CWE 7/7). "A guard that cannot fire proves nothing" -- ship an injected-defect negative
   control with each test (Nestor lesson 1).
6. NOVELTY MEASUREMENT: there is NO accepted Prometheus novelty metric. What exists is a record
   of metric failures: ASAL score rewards iid noise 22x over coherent drift (Techne s3); POET's
   novelty estimator changes regime at k, ignores its own normalisation, conflates absence with
   zero and deflates against a never-pruned archive (Nyx 291a22ed). The positive proposal in
   the ecology is PTE's "mechanism labels from the ablation PATTERN" and "promote by
   ablation-pattern novelty". Recommend: schema novelty = new ablation fingerprint over a fixed
   task panel; any scalar must pass a random-junk cheat control.
7. STATISTICAL HYGIENE seen repeatedly: fit the null on all arms before calling an interaction
   (Nestor lesson 12); identical arms are a defect signature (lesson 9); check seed independence
   (Ares seeds 1-3 byte-identical); variants that change unread parameters are reruns (PTE F5);
   estimated means frozen as exact thresholds cause false fails (Nyx A7 lesson).

-----------------------------------------------------------------------------------------------
## 4. Cheapest ports, ordered by cost (all runnable on M4, pure Python)

  cost    port                                                  source          answers
  ------  ----------------------------------------------------  --------------  ------------------------------
  none    description-length table: G2 in raw DSL vs DSL+G1     NPE E-8         could G1 shorten G2 at all?
  none    lens triple + "how it has lied" list for Aphrodite    Archaeon/Artemis  convergence, honesty
  low     expressiveness coverage audit of schema grammar       Harmonia B1/B2  is the NO a B2 ceiling?
  low     band check per task family (enumerator vs best)       Ludus CEILING-1 which families can show recursion
  low     arm-identity / wiring audit of recursion test         NPE lesson 9    is the NO a defect?
  low     hand-built G2-using-G1 + priced partials              Crius           existence vs accessibility
  low     permuted-library and YOKED-library arms               Archaeon C3, BEE is adoption = useful inheritance?
  low     MAINTENANCE vs ACQUISITION split of existing results  BEE             is any gain recursion at all?
  medium  twin light-cone: G1 present/absent, divergence by gen Aether          does G1 propagate to later discovery?
  medium  graded task ladder vs shuffled order, equal budget    Archaeon C3     endogenous-curriculum substitute
  medium  k-donor libraries (k=1 vs 4), joint dose-curve fit    NPE critical mass  is G2 establishment-limited?
  medium  ablation-fingerprint novelty for schemas              PTE F3/F6       a novelty measure for "new kind"
  medium  bounded library + pruning policies, charged cost      SI directive    selective forgetting vs growth
  higher  mutable improvement mechanism (AL-1)                  Atlas menu      fixed-mechanism limitation
  higher  task generator with regret/learnability selection     Atlas UED-1/2   endogenous task supply

## 5. What the ecology suggests about Aphrodite's recursion NO

Three independent engines (Crius, Archaeon C3, NPE) found the same shape: the useful next
mechanism EXISTS and pays when built, but its partials are neutral or deleterious, so search
does not reach it (accessibility valley); the one clear positive in the ecology (NPE E-8) came
from shortening the encoding of the whole chain; and Archaeon C3's delay ladder is the one
clear curriculum success. Harmonia's B1/B2 audit says to rule out an expressiveness ceiling
before calling the terrain flat. So the first three things to check are, in order:
(1) is the NO a wiring defect (arms identical?), (2) is G2 expressible and shortened by G1
(B2 / encoding length), (3) does G2-with-G1 pay when built by hand, and what do its partials
cost (existence vs accessibility). Only if all three come out "G2 is expressible, shorter with
G1, pays, and has selectable partials" is the NO evidence against recursion itself.
