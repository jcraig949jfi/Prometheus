# The World-Graph Engine: what to build, where it runs, what already exists, and the MVP

Date 2026-09-23. Builds on `00_source_verbatim_2026-09-23.md` (the operator's passage, reproduced exactly there).
Every path below is a real file inspected today; every claim about an existing program is from that inspection,
not from memory. Nothing here has been run. This is a design, not a result.

Working label used in this document: **WGE** (world-graph engine). It is a label for this document only, not a
seat, not a directory, not a claim of existence.

---

## 0. The passage, restated as five mechanisms

The passage proposes one loop with five distinct mechanisms. Naming them separately matters because they have
different costs, different existing coverage in the repo, and different ways to fail.

| # | Mechanism | One-line definition | What it needs |
|---|-----------|--------------------|---------------|
| M1 | World graph | Nodes are worlds; edges are typed perturbations `W_i --delta--> W_j` | A substrate-neutral world coordinate and a digest per node |
| M2 | Phenomenon detection | A vector of P-detector verdicts per world, computed the same way on every substrate | Detectors that return FIRE / QUIET / UNABLE, with a published chance floor |
| M3 | Quotient | `W_i ~ W_j` iff same prediction vector; classes replace worlds; boundaries replace bulk | A frozen probe battery so the vector is comparable across nodes |
| M4 | Invariant mining + boundary search | Find `A and B and C => P` that survives across substrates; bisect edges where class flips | Base-rate nulls, leave-one-substrate-out, planted truths |
| M5 | Adjudication | An external source of observations prunes/reweights the graph | Real data, or an honest substitute until real data is wired in |

The passage's own doctrine, "maximize the number of independent ways the conjectured law can fail, not the
number of worlds," is exactly [[feedback_instrument_monoculture]] and [[feedback_diversity_is_an_unsafe_observable]]
in Prometheus's existing language. The engine is worth building only if M4 is held to that standard: a law
supported by 47,000 worlds that share one evaluator is one observation, not 47,000.

---

## 1. What already exists (surveyed today)

Five programs were surveyed. Four are directly usable. All five are pure-Python, CPU-only, multiprocess.

### 1.1 BEE = Bellerophon Emergence Engine = the Prometheus Worlds Kernel (`D:\Prometheus\prometheus\toolbox\`)

This is the closest thing to M1 that exists, and it is already the shared execution path for three ecosystems.

- **World contract** `core.world.v1` in `D:\Prometheus\prometheus\toolbox\contracts.py`: `reset(seed) / observe / legal_actions / step / trace_hash`. Substrate is a separate axis (`core.substrate.v1`): `flat, kv, stream, mailbox, artifact, kv_weather`. Reference worlds: `integer, integer_alt, integer_batch (numpy), grid, pendulum, wforge, c6`.
- **Experiment IR** in `D:\Prometheus\prometheus\toolbox\ir.py`: `Experiment(family, world, substrate, players, interventions, objective, observers, controls, transforms, sweep, seed_policy, budget)`. `digest()` is a content identity. `sweep_points()` expands a cartesian product over `world, substrate, interventions, budget, seed_policy, objective, players` and `at_point()` records `parent` + `sweep_point` in provenance. **A sweep is already a star of delta-edges from the parent IR.**
- **Interventions and transforms**: `interventions` (world_params, wrappers, schedule) and `transforms` (`transform.shuffle.v1` = the SHAM, `transform.fresh.v1` = the SCRATCH, `transform.relabel.v1` = metamorphic) in `D:\Prometheus\prometheus\toolbox\ref\transforms.py`. These are the passage's "remove a mechanism / introduce noise / alter the learning rule" edges, plus the controls that keep them honest.
- **Receipts** (`D:\Prometheus\prometheus\toolbox\receipt.py`): content-hashed JSONL with `prev_receipt_id` chaining and `replay_file()` re-execution. 38 committed receipt files replay with 0 divergence.
- **Cross-substrate transplant manifest** (Atlas->BEE pilot, `D:\Prometheus\roles\Bellerophon\atlas_bee\`): every adaptation carries a typed translation manifest with cells `IDENTICAL / ANALOGOUS / MODIFIED / OMITTED / UNREPRESENTABLE`. **This is the cross-substrate delta-edge, with loss made explicit.** The pilot's six verdicts (PRESERVED / CHANGED / INVERTED / ABSENT) are the first cross-world phenomenon comparisons the repo has.
- **Backends**: `local.py` (works), `sfe.py`, `npe.py` (UNAVAILABLE_INTERFACE by decision D-BELL-2; envelope pinned).

Compute: stdlib Python, single process, no numpy except `worlds_integer_batch.py`. `ext.batch.v1` groups same-digest runs behind one batched world and reproduces scalar receipts run for run. That batching seam is where a GPU substrate would plug in.

### 1.2 SFE science program = Archaeon campaigns on the WSE substrate (`D:\Prometheus\archaeon\wse\`, `campaign1..6`)

Two things share the name. The **service** (`D:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine`, SQLite+HTTP, schema 9) stores science and does not simulate. The **program** is Archaeon's campaigns on Proteus tape-VM organisms in an event-stream world.

What it contributes to WGE:

- **A world with every coordinate a knob**: `WorldSpec` in `D:\Prometheus\archaeon\wse\worlds.py` (`K, D, interleave, delay, ask_mode, ask_kind, ask_timing, fanout, expensive, op_mode, topology, n_defs, noise_rate, value_bits, Kd, retire_rate, delays, interfere, vocab, recycle`); `world_id()` = sha256 of grammar + knobs. `Regime(alpha, beta, gamma, delta)` in `economics.py` prices compute, persistent words, and I/O. **beta is the maintenance-cost axis and gamma the communication-cost axis the passage names.**
- **The boundary map** (`READOUT_ssf.md` section 0): three hand-written organisms (log everything / one slot per entity / last value only) scored under the economics **before any evolution**. This found both boundaries the directive asked for (too little cost: logger ties; too much cost: last-value wins; S1 region: selective wins by >= 0.10 on 7/7 cells). **This is a search-free phenomenon detector that classifies a world in seconds. It is the MVP's engine.**
- **Reachability table** (`reachability.py`): per (cell, budget, regime, foundry) rows with classes `COMMON / REACHABLE / RARE / OBSERVED_UNREACHABLE_AT_BUDGET / UNESTABLISHED` and reach levels FLOOR / SHELF / SUMMIT. This is a phenomenon graph for one phenomenon ("evolution reaches a solution").
- **Corridor table** (`corridor.py`): (source cell -> target cell) rows recording direct reuse and initialization reach. **This is a transition-operator table in the passage's sense: what is the minimum material that moves a solution across an edge.**
- **State interventions** (`interventions.py`): `ERASE_ALL, ERASE_REGS, ERASE_TAPE, SCRAMBLE_LOC, SCRAMBLE_VAL, SWAP_TWO, HALVE_CAP, RESET_IP, TRANSPLANT`; readout = reward delta per intervention = failure geometry.
- **Typed verdicts** (`states.py`): `ENGINE_FAILURE, INSTRUMENT_FAILURE, INTERVENTION_NOT_APPLIED, ..., CAPABLE_NEGATIVE, WEAK_POSITIVE, SUPPORTED_POSITIVE`.
- **Campaign 6** (`D:\Prometheus\archaeon\campaign6\`): a substrate-neutral evaluator (`substrate.py`, same five calls for tape-VM and graph organisms), a 16-field fingerprint (`schemas.py` FINGERPRINT_FIELDS, includes `memory_reads, memory_writes, communication_events, interaction_partners, env_dependencies`), eleven detectors with FIRE/QUIET/UNABLE outcomes, a composable-world generator with provenance (`worlds/generator.py`), and a planted-fixture calibration protocol. Currently at gate G6-0.

Hard negative results that constrain the design: de-novo evolution found no foothold in 0/60 naive rows across cycles 1-2, including at zero cost; W2_K2 summit unreachable in 24 x 300-generation runs, 54 corridor runs, and under all-or-nothing payoff. **Search, not economics, is the binding constraint for evolved phenomena on this substrate.** Any WGE that defines P as "evolution produced X" inherits that wall on day one.

Compute: pure Python, `multiprocessing.Pool`, `--procs` up to 26. Campaign 3 cost 6.1 h for ten slots. Campaign 5's ten slots ran in 51 minutes.

### 1.3 NPE = Nestor Primordial Engine (`D:\Prometheus\primordial\`, `D:\Prometheus\roles\Nestor\campaigns\z80atlas-2026-09-19\`)

- **Substrate**: Z8, a byte-addressable Z80-like VM with variable-length instructions (`z8.py`), so mutation shifts the reading frame. Deliberately unlike Proteus's fixed-width VM.
- **A factor grammar as the world coordinate** (`grammar.py` FACTORS): `world (PAIR_TAPE/SOUP_MEM/GRID/GRAPH), environment (STATIC/NONSTATIONARY_SHIFT/COEVO_ENV/RESOURCE_LIMITED), representation, reproduction (6 modes), self_location, copy_primitive, pressure (12 levels), structure (9), task_transform, read_order, bridge, seeding, mutation_operator, mutation_locality, mutation_rate, atlas_axis`. Grammar hash enforced at runtime. A cell = one point in the grammar; **every cell produces its own Hamming-distance-1 control.**
- **Scale already run**: 23,471 runs, 0 failed, 20,638 families, 10,741 pure matched pairs (frozen 2026-09-22). **This is the largest existing world graph in the repo: a factor hypercube with distance-1 edges, already populated.**
- **Post-run assays** (`assays.py`): `DAMAGE_CLIFF, LENGTH_ROBUSTNESS, DELETERIOUS_LOAD, RESIDUE_TRANSPORT, STASIS_ESCAPE, TRANSITION_DETECTOR, RECOMBINATION`.
- **Storage**: files under `observatory/` (INDEX.jsonl, per-run CONFIG/RESULT/series/lineage), harvested into Postgres schema `atlas` on M1.
- Verdicts as of 2026-09-23: A-1 spontaneous replicator NARROWED twice (all 1,031 admissible runs are `PAIR_EXECUTION`, zero endogenous); A-2 matched-pair effects HOLD; A-3 read-order OPEN, prior claim WITHDRAWN. Cycle 9 verification campaign built and gated, not launched (operator hard stop).

Compute: pure Python, `ProcessPoolExecutor`, `--workers 6`, 60 GB disk budget.

### 1.4 Aphrodite (`D:\Prometheus\roles\Aphrodite\`)

Not a world engine, but it holds three pieces WGE needs for M3 and M4 and has no equivalent elsewhere in the repo.

- **Denotational equivalence classes** (`engine\semantics.py`): identity of a program = its value vector over a frozen exhaustive probe battery (`PROBE_ACC x PROBE_V x PROBE_FIRST x PROBE_LAST`); AST normalization only names the representative. **This is the quotient operation, implemented, for one DSL. Lift the same idea from programs to worlds and M3 exists.**
- **Anti-unification** (`engine\organ_extract.py`, Plotkin LGG): computes a hole-bearing schema from two independently discovered structures. **This is "several completely different mechanisms instantiate X; extract X" as an algorithm rather than a narrative.** Tier 3C extends it to semantic classes.
- **Certify-before-search** (`certify_basis_separation.py, certify_reachability.py, certify_expressivity.py`): arms must express the same program set before a difference between them means anything. Nine standing invariants in `library\METHODOLOGY.md`; `conformance.py` ran 21,600 differential comparisons at 0 mismatches.
- **A planted-truth world table** (`science\campaign0\worlds.py` W1..W9): parameter perturbations off one generative model, with the assay never seeing the table. **This is the house pattern for calibrating any detector, and the pattern the MVP must copy.**
- **Closed-form phase boundaries paired with simulation** (`science\swarm\models.py`): branching-process outbreak threshold and herding cascade limit. A template for "boundary predicted, boundary measured."

Standing verdicts include BOUNDED_RECURSIVE_SELF_IMPROVEMENT = NO (Tiers 3A-3C, 2026-09-22) and one permanent validity scar (slice 2B). Compute: ~8,450 lines stdlib Python, `multiprocessing.Pool`, ~3,237 lineages/hour/core, 45 MB peak. GPU explicitly not authorised for that seat.

### 1.5 AGE = Aether's artificial-physics ecosystem (branch `origin/aether/aeth01-memwall-2026-09-22`, directory `Aether/`)

The expansion of "AGE" is never written out in the repo; the token names the Aether seat's lane (`roles/Aether/STATUS.md`) and its controller. **None of it is on `main` or in the `D:\Prometheus` working tree.** Read with `git show origin/aether/aeth01-memwall-2026-09-22:Aether/<path>`. `Aether/AETHER_CONCEPT.md` calls it "a fourth Prometheus experimental ecosystem, alongside BEE, NPE and SFE, developed independently of them, clean-room design."

- **Substrate** (`Aether/AETH-01/PHYSICS_SPEC_DRAFT.md`): a batched 2-D toroidal lattice, 5 uint8 fields per site (`opcode, arg0, arg1, payload, energy`), synchronous deterministic ticks in five phases (propose, arbitrate by SplitMix64 priority, commit, settle energy conservatively, perturb). One live opcode (WRITE); no birth or allocation primitive; no genome boundary; no player concept at all.
- **Parameters**: `WRITE_COST, MAINTENANCE_COST, REPLENISH_NUMER, REPLENISH_AMOUNT, MUT_NUMER`, plus seed, lattice size, ticks, soup density. `ECONOMICS.md` defines regimes A/B/C as points in that space. **`MAINTENANCE_COST` and `REPLENISH` are the passage's maintenance-cost and environmental-recurrence axes, at the physics level rather than the organism level.**
- **Compute**: NumPy CPU oracle plus a **CuPy GPU kernel, differentially verified 300/300 bit-exact** against the oracle. Single GPU, rented RunPod A40s through `age_controller.py` with a $3 sub-cap and a 900 s lifetime reaper. After a memory round: 128 B/site on device; 16384^2 = 268 M sites at 7.42 s/tick, 36.2 M sites/s; 32768^2 OOMs. A $0 CPU scout runs 128^2 x 1500 ticks.
- **Observatory** (`Aether/observatory/aeth01_observatory.py`): activity/write/starved density, per-field change rate, Shannon entropy per field, exact Gini on energy, spatial autocorrelation, zlib ratio vs random baseline, sha256 state digest, block maps. 18 known-answer tests. `component_track` and `perturbation_divergence` deliberately unimplemented.
- **Perturbation**: `MUT_NUMER` (Hamming-1 bit flip on winning writes, never on energy). Claim-ladder ablations specified in `REVIEW_PACKET_AGE_CLOSURE_2026-09-21.md` and `KILL_GATES_01.md`.
- **State** (First Light, 2026-09-22): 6/6 worlds at 4096^2 x 5,000 ticks, replay verified cross-backend, **no endogenous organization** (block-mean SD 1.107 vs 1.11 noise prediction); a measured irreducible energy leak of 3.04% per 5,000 ticks at zero cost. Claim ceiling: all fixtures `SEEDED_CONTROL`. Next round AETH-02 (native circuitry) not started.

For WGE this is the lockstep GPU substrate section 3 asks for, already built and already clean-room. Its cost is that it has no players, so every player-defined probe returns UNABLE on it; a phenomenon must be defined at the field level (a written pattern persisting under `MAINTENANCE_COST` against `REPLENISH`) before it can join a law's substrate count.

### 1.6 Atlas (`D:\Prometheus\atlas\`) is the graph store that already spans the ecosystems

Two-tier relational index in schema `atlas` on the M1 Postgres. Read-only against every engine; harvest adapters for SFE, NPE, Archaeon frontier, Vivarium, PEW. One typed edge table (`atlas.edge`, `roles\Atlas\MODEL.md` section 4) with vocabulary including `DEFORMATION_OF, REPLICATION_OF, TRANSPLANT_OF, SUPERSEDES, AMENDS, TESTS`, every edge with a declared basis; `atlas.fact / fact_evidence / conclusion / signal` tables; `descendants()` / `ancestors()` functions.

**WGE's three graphs already have homes here**: world graph edges = `DEFORMATION_OF` (within substrate) and `TRANSPLANT_OF` (across substrate); phenomenon graph = `fact` + `fact_evidence`; law graph = `conclusion` + `signal`. A new engine adds one harvest adapter (`roles\Atlas\MODEL.md` section 7) and its own ledger; it does not need a new database.

---

## 2. Mapping the passage onto the repo

| Passage concept | Existing object | Gap |
|---|---|---|
| World `W_i` | BEE `Experiment.digest()`; WSE `world_id()`; NPE grammar cell; AGE seed + run parameters + recipe; Aphrodite `World` | No single coordinate across all five. Needed: a **world manifest** that embeds any of them and declares its substrate family |
| Delta edge (same substrate) | BEE `sweep_points()/at_point()`; NPE Hamming-1 control pairs; Aphrodite W1..W9 | Edges are implicit in provenance; nothing enumerates or stores them as first-class rows |
| Delta edge (across substrate) | BEE transplant manifest (IDENTICAL..UNREPRESENTABLE) | Only 6 exist, hand-built |
| Phenomenon `P` | C6 eleven detectors; WSE boundary-map verdict; reachability class; NPE assays; BEE PRESERVED/CHANGED/INVERTED/ABSENT | Detectors are per-program; no shared verdict vector schema across substrates |
| Quotient `W_i ~ W_j` | Aphrodite `semantics.py` (over programs) | Never applied to worlds |
| `A and B and C => P` | Aphrodite certify-* invariants; Harmonia conditional-law doctrine | No miner over a world graph |
| Minimum delta that flips P | WSE corridor table; NPE matched pairs | No bisection along edges |
| Mechanism-level invariant | Aphrodite anti-unification | Only over its DSL |
| Reality prunes the graph | Aphrodite Tier 4 (empty); nothing else | **Absent.** MVP must use an honest substitute and say so |

---

## 3. Compute architecture: CPU, GPU, or hybrid

### 3.1 Hardware on hand (checked today on this machine)

| Resource | Value |
|---|---|
| GPU | NVIDIA GeForce RTX 5060 Ti, 16 GB, 712 MB in use |
| CPU threads | 28 |
| torch | 2.11.0+cu128, CUDA available |
| numba | blocked by an Application Control policy (DLL load refused) |
| cupy | not installed |

Fleet: M1 hosts Postgres and Redis; M2 has an RTX 5060 Ti and an SMR D: drive that must not hold a hot ledger (see [[project_m2_smr_disk_20260917]]); M3 runs the forge. BEE, SFE, NPE, and Aphrodite are CPU multiprocess. AGE is the exception: a CuPy kernel run on rented RunPod A40s with a dollar cap, with a NumPy oracle that runs locally at scout scale. CuPy is not installed on this machine, so AGE's kernel would need either a RunPod session or a torch port to use the local RTX 5060 Ti.

### 3.2 Where each layer belongs

**The substrates that exist are CPU-shaped and should stay there.** Proteus tape VM, Z8, graph organisms, and the Aphrodite DSL are interpretive, branchy, variable-length programs. On a GPU they run as divergent warps and lose most of the hardware. Porting them buys speed on substrates that have already been measured to their walls (0/60 naive footholds; W2_K2 unreachable; A-1 narrowed). [[feedback_instrument_monoculture]] says the marginal substrate is worth more than a faster existing one.

**The GPU earns its place by adding substrates that are lockstep by nature**, which is also what M4 needs: independent ways for a law to fail.

| Substrate class | Why GPU-native | Fixed-shape? | Shares code with CPU substrates? |
|---|---|---|---|
| **AGE's AETH-01 lattice (exists)** | 5 x uint8 fields per site, synchronous ticks, 36 M sites/s on an A40 | yes | no (clean-room by charter) |
| 1-D / 2-D cellular automata with a memory tax | thousands of worlds x seeds as one int32 tensor per step | yes | no |
| Random boolean networks / gene-regulatory nets | batched bitwise ops | yes | no |
| Reaction-network "chemistries" (mass-action or Gillespie-lite) | batched ODE / tau-leap | yes | no |
| Small fixed-width register machines in lockstep (same opcode per lane per step is NOT required if width is fixed and the ALU is a gather) | vectorized dispatch | yes | no |
| Tiny neural learners (linear / one hidden layer) under the same event-stream grammar | obvious | yes | no |

Each of those can be written to the BEE `core.world.v1` contract through the `ext.batch.v1` seam, so the receipts, replay, controls, and transplant manifests apply unchanged. Independence from the CPU substrates is by construction: no shared evaluator, no shared VM.

**The graph layer (M1, M3, M4) is small data, not big compute.** Two thousand to two hundred thousand nodes with a few hundred features each is a Postgres table and a numpy job. Invariant mining over it is minutes on one core. Boundary bisection is a scheduler that emits new world manifests to the CPU pool or the GPU batch. Nothing here needs CUDA.

**Verdict: hybrid, with a specific division.**

- CPU pool (M1/M2/M3, 28 threads here): the four existing substrates through their existing runners; BEE local backend; detectors and fingerprints.
- GPU (RTX 5060 Ti, torch): new lockstep substrates only, as batched BEE worlds. Not for porting old substrates.
- Postgres on M1 (schema `atlas` plus one new schema for WGE's own ledger): node, edge, verdict-vector, class, law tables.
- The M2 SMR D: drive holds nothing hot; WGE ledgers go on C: NVMe or M1.

For the MVP (section 5) the GPU is not used at all. That is a statement of fact about the MVP's size, not a design preference.

---

## 4. The engine, component by component

### 4.1 World manifest (M1 nodes)

One JSON record per node, digest = node id:

```
{ "schema": "wge.world.v1",
  "substrate_family": "proteus_tape_v0" | "proteus_graph_v1" | "bee_stream_statemachine" | "z8" | "ca1d_torch" | ...,
  "embedded": <BEE Experiment IR | WSE WorldSpec+Regime | NPE cell | ...>,
  "coordinates": { "recurrence": ..., "delay": ..., "maintenance_cost": ..., "interference": ..., "comm_cost": ..., ... },
  "coord_map_version": "..." }
```

`coordinates` is the substrate-neutral projection: each family declares a map from its own knobs to a shared,
versioned coordinate vocabulary. This is where the passage's `z_1..z_5` (memory pressure, coordination pressure,
branching pressure, nonstationarity, reuse opportunity) enter, as **declared, testable projections**, not as
discovered truths. The MVP will find out whether the declared projections carry any cross-substrate signal; if
they do not, that is the first result.

### 4.2 Edge generator (M1 edges)

Three edge kinds, each a row in the WGE ledger and later an `atlas.edge`:

- `DEFORMATION_OF` (within family): single-knob step. Enumerated from the coordinate lattice, not from provenance.
- `CONTROL_OF` (within family): SHAM / SCRATCH / RELABEL transforms from BEE, so every node has its own negative controls as neighbours.
- `TRANSPLANT_OF` (across family): same `coordinates`, different `substrate_family`, with the BEE translation manifest attached (IDENTICAL / ANALOGOUS / MODIFIED / OMITTED / UNREPRESENTABLE per coordinate). UNREPRESENTABLE coordinates are recorded, not dropped, so a law's "diversity of substrates" can be counted only over substrates where its conditions were actually representable.

### 4.3 Probe battery and verdict vector (M2)

Per node, one verdict vector, frozen schema, each entry FIRE / QUIET / UNABLE with score, threshold, and chance floor:

- **Economic probes** (search-free): hand-written reference players per family (WSE: logger / one-slot / last-value / CONST0 / echo; BEE: constant and statemachine references; each new family must ship its own three) scored under the node's economics. Verdict `SELECTIVE_PAYS`, `LOGGER_PAYS`, `LASTVALUE_PAYS`, plus their margins.
- **Structural fingerprints** (search-free): C6's 16 fields computed on the reference players.
- **Reach probes** (search-dependent, expensive, optional in MVP): reachability class of an evolved population at a declared budget.
- **Intervention probes** (on whatever player is present): the WSE nine, as reward deltas.

UNABLE is a first-class outcome. A probe that cannot run on a family says so, and the quotient treats UNABLE as its own symbol rather than as QUIET. This follows [[feedback_executing_lens_beats_reading_lens]].

### 4.4 Quotient (M3)

Class id = hash of the verdict vector restricted to a declared **relevance mask** (which entries count as "the predictions that matter"). Two masks at minimum: the full vector, and the MVP's target phenomenon alone. Reported per mask:

- number of classes vs number of nodes (compression ratio),
- boundary edges = edges whose endpoints differ in class,
- boundary edge fraction by edge kind (DEFORMATION vs TRANSPLANT).

If the quotient produces mostly singleton classes, the probes are measuring substrate identity, not phenomena. That is a kill condition for the probe battery, stated in section 5.4.

### 4.5 Invariant miner and boundary search (M4)

- **Conjunction search** over `coordinates` thresholds predicting the target verdict, evaluated with:
  - a base-rate null: shuffle verdicts across nodes within family, preserving family counts ([[feedback_base_rate_null_for_pattern_claims]]);
  - leave-one-family-out: fit on k-1 families, predict the held-out family, report accuracy against that family's chance floor;
  - a monoculture guard: a law's "substrate count" counts only families with disjoint evaluators.
- **Bisection**: for each boundary DEFORMATION edge, emit the midpoint world manifest, run, repeat to lattice resolution. Output: a table of minimal deltas per family per phenomenon, the passage's "transition operators."
- **Mechanism extraction** (later, not MVP): when two families both FIRE on `P` under the same conjunction, hand the two reference mechanisms to Aphrodite's anti-unifier and record the LGG schema as the candidate `X`.

### 4.6 Adjudication (M5)

The passage's arrow "observation -> prune" requires observations from outside the graph. The repo has none wired
in (Aphrodite Tier 4 is empty). Two honest substitutes, in order:

1. **Held-out family as pseudo-reality**: a law mined on families {A, B} makes a prediction `X => Q` on family C, which was not used in mining and shares no code. Whether Q appears in C is the MVP's adjudication. This is a real test of cross-substrate invariance and a fake test of physical reality, and the doc says so.
2. **Real data hookup** (post-MVP): a behavioural dataset with a known unexplained regularity, entered as a node with `substrate_family = "reality"` and a verdict vector filled by measurement, with every probe UNABLE except those that map to the dataset's observables. The graph then has exactly one node whose verdicts cannot be regenerated, and every law is scored on whether it predicts that node's non-UNABLE entries.

---

## 5. MVP: the smallest experiment that can kill the concept

### 5.1 The concept under test

Not "can we build a graph." The concept is the passage's central claim: **a phenomenon's occurrence, expressed
in substrate-neutral coordinates, compresses across genuinely different substrates, and the boundary of that
compression can be found by construction.** If that is false for the easiest phenomenon the repo has, the rest
of the passage is not reachable from here.

### 5.2 Choice of phenomenon and families

**Phenomenon**: `SELECTIVE_PAYS`, "persistent selective state is economically favoured," defined exactly as
the WSE boundary map defines it: the one-slot reference player beats both the logger and the last-value player by
>= 0.10 under the node's economics. Chosen because it is (a) the passage's own worked example (information
retained x recurrence / (maintenance cost + interference)), (b) already measured on one family at 7/7 cells, and
(c) search-free, so it sidesteps the 0/60 evolution wall. The evolved version of the same phenomenon is a
declared second layer, not the MVP.

**Families** (three, no shared evaluator):

| Family | Runner | Reference players | Status |
|---|---|---|---|
| F1 `proteus_tape_v0` | `archaeon.wse` evaluate on `WorldSpec` + `Regime` | existing logger / slot / last-value in `wse/controls.py` | exists |
| F2 `proteus_graph_v1` | `archaeon.campaign6.substrate.evaluate_any` on graph manifests | need three hand-written graph organisms | evaluator exists; players to write |
| F3 `bee_stream_statemachine` | BEE local backend, `stream` substrate, `statemachine.v3` players | need three hand-written state machines | kernel exists; world + players to write |

F1 and F2 share the world grammar but not the organism evaluator. F3 shares neither. That gives one
DEFORMATION lattice per family and TRANSPLANT edges between them with the translation manifest recording what
the BEE stream substrate cannot represent (for instance `expensive`, `topology = dag`).

A fourth family on the GPU is the first post-MVP addition and the first true "microscopic physics has nothing in
common" test. AGE's AETH-01 lattice is the candidate: it exists, it is clean-room, and its `MAINTENANCE_COST` /
`REPLENISH` parameters sit on two of the lattice's coordinates. It is not in the MVP because it has no players, so
`SELECTIVE_PAYS` is UNABLE on it by construction; a field-level persistence phenomenon has to be defined and
calibrated first, and its First Light showed no endogenous organization to anchor one.

### 5.3 The lattice

Coordinates and their per-family knobs, all discrete:

| Coordinate | F1/F2 knob | F3 knob | Levels |
|---|---|---|---|
| recurrence | `D` (PUTs per stream) | events per key | 1, 2, 4, 8 |
| delay | `delay` | delay ticks | 0, 4, 16 |
| interference | `Kd` x `interfere` | distractor keys | 0, 4, 16 |
| maintenance_cost | `beta` | persistent-state charge | 0, .05, .2 |
| comm_cost | `gamma` | read/write charge | 0, .02 |
| compute_cost | `alpha` | ops charge | 0, .002, .02 |
| streams | `K` | keys | 1, 2 |

4 x 3 x 3 x 3 x 2 x 3 x 2 = 1,296 nodes per family, 3,888 total, ~15,000 DEFORMATION edges, 2,592 TRANSPLANT
edges. Each node: 5 reference players x 16 episodes x 3 seeds = 240 episodes. Per-episode cost for a hand-written
player on WSE is in the low milliseconds; ~933,000 episodes total. **Estimated wall: single-digit hours on 28
CPU threads. No GPU.**

### 5.4 Precommitments, written to be lost

Each of these is a way the concept dies, stated before any row exists:

1. **Quotient failure.** Under the target mask, if the class count exceeds 50% of the node count, the verdict vector does not compress and "quotient the infinity" is not happening at this granularity. Kill the probe battery, not the concept, and say so.
2. **No cross-family law.** The best conjunction fit on any two families must predict the third with accuracy exceeding that family's chance floor by a margin the base-rate null puts below p = 0.01. If no conjunction clears this for any leave-one-out fold, the result is "three substrate-local laws, zero invariants" and the passage's central claim fails on its own worked example.
3. **Planted artifact recovered as invariant.** Before mining, plant a fourth pseudo-family F0 that is F1 with one extra knob (`value_bits`) wired so that `SELECTIVE_PAYS` flips on it alone. The miner must report that condition as family-local. If it reports it as invariant, the miner is fooled by a shared-code family and the monoculture guard is broken.
4. **Planted threshold not recovered.** F3's economics get a hand-set `beta*` where the slot player's margin crosses 0.10 by construction. Bisection must land within one lattice step of it in every seed. If not, boundary search is not working.
5. **Projection carries no signal.** If the shared `coordinates` predict the verdict no better than the family's raw knobs do on the held-out family, the projection is decorative and section 4.1's vocabulary is wrong.

Passing all five does not make the concept true. It makes it survive one instrument ([[feedback_positive_results_are_provisional]]).

### 5.5 Deliverables

- `wge/` (location to be assigned by the operator): `manifest.py`, `lattice.py`, `probes/` (one module per family, each with its three reference players and a chance-floor calculation), `quotient.py`, `mine.py`, `bisect.py`, `ledger/` (JSONL rows, content-hashed, replayable through BEE receipts where the family runs on BEE).
- A prereg file committed before the first row, containing section 5.3's lattice and section 5.4's five kill conditions verbatim.
- One Atlas harvest adapter so the nodes, edges, verdicts, and laws land in `atlas.edge / fact / conclusion` with basis declared.
- A review packet on close, whatever the outcome.

### 5.6 What the MVP deliberately does not do

- No evolution. The phenomenon is economic, not evolutionary, because the evolutionary version is known to be search-limited.
- No LLM-generated worlds. The lattice is exhaustive and LLM-free so the generator cannot steer the result.
- No GPU. The MVP fits in CPU hours.
- No claim about reality. M5 is the held-out family, and the write-up names that as a substitute.

---

## 6. After the MVP, in order

1. Fourth family on the GPU: AGE's AETH-01 lattice, wrapped to the BEE batch contract through its NumPy oracle at scout scale locally and its CuPy kernel on RunPod at scale. Requires a field-level phenomenon definition and its own planted calibration. This is the first test of the passage's "nothing in common microscopically" claim. If AGE is unavailable (branch not merged, seat busy on AETH-02), a torch 1-D CA with a memory tax is the fallback and must share no code with the other families.
2. Reach probes: run the reachability classifier at a fixed budget on the boundary nodes only. Question: does the evolutionary boundary sit where the economic boundary sits, or somewhere else? WSE's history predicts "somewhere else, and search-limited."
3. Anti-unification of the reference mechanisms that FIRE together across families, to name `X`.
4. NPE ingestion: 20,638 existing families with distance-1 edges, projected onto the shared coordinates. This is a free, already-run world graph for a different phenomenon set (replication, fidelity, coexistence).
5. Reality node: one behavioural dataset entered as a non-regenerable node.

---

## 7. Open questions for the operator

- Where should `wge/` live and under which seat? The pieces are Bellerophon's kernel, Archaeon's substrate and probes, Aphrodite's quotient and anti-unification, and Atlas's store. A new seat or an existing one is the operator's call.
- Is the economic definition of `SELECTIVE_PAYS` acceptable as the MVP phenomenon, given that it is a property of hand-written players and not of anything that emerged? The alternative, an emergent phenomenon, costs roughly two orders of magnitude more and starts behind a known wall.
- Is the RTX 5060 Ti on this machine available for post-MVP substrate work, given Aphrodite's standing "GPU not authorised" restriction was seat-specific?
