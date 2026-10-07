# Dossier: agent_d2_blind .. agent_d5_blind (August blind D-series)

Audit: Hestia audit 1 (2026-10-06), group G7(d). Rubric: AUDIT_PLAN.md s2-s4.

VERDICT: SALVAGE_COMPONENT -- none of the four is a reasoning substrate or meant to be one; what survives is the measurement discipline (separating expressible / reachable / findable, counting distinct reachable artifacts not programs, controls with known pathology, shuffled-history and random-library ablations), and D-5's own ablation shows its single positive is a seeded-start cache, not developmental learning.

## 0. Identity

- Paths: agent_d2_blind/ (28 tracked files), agent_d3_blind/ (33), agent_d4_blind/ (60),
  agent_d5_blind/ (53). Worktree C:/Prometheus-worktrees/hestia-boot-2026-10-06 at 3fed30ac9.
- Seat: none named. Four "blind" independent agents built on ONE day, 2026-08-27
  (D-2 7e466657a -> 4f17f6a0c; D-3 38a5304d1 -> 6bbec4383, 9aee3c163; D-4 927f17f84 ->
  20adccd37, 8380785ff; D-5 66c6a8e9f -> 976d4a0df). Later consumer: Ergon (memory-metabolism
  seat) took D-5 as its donor/baseline (Ergon correction 8e7a6f505, 2026-09-01).
- Census state: not checked against docs/fleet/fleet_state.json row-by-row.
- READ: all four VERDICT files; MANIFEST heads; D-2 d2/core.py, d2/g1.py (full),
  d2/classify.py (full), ledgers/phase1_summary.json, census_G1_diagnostic.json; D-3
  mutation/mutators.py:1-90, substrates/s4_rev.py (full), ledgers/basis_S*.json (m0, targets,
  probe stability), census_rows_S*.jsonl (recomputed validity); D-4 substrates/vm_substrates.py
  header, mutate (102-140), d1 (176-187), S4Mem (479-530), d4core/navigators.py (signatures),
  results/*_nav_rows.jsonl (recomputed hit tables); D-5 substrate/rm_vm.py, learner/m1.py,
  mutation/physics.py (all full), navigators/m0.py:74-128 (grep), ledgers/m0_rows, m1_rows,
  ablation_rows (recomputed solve counts), results/gates_verdict.json, ledgers/BUILD_LOG.md,
  final_libraries/lineage_0.json (shape only); roles/Ergon/STATUS.md:1-75.
- NOT READ: D-2 g2.py, g3.py, g3b.py, census.py, st_tests.py, PREREG-CENSUS.md; D-3
  s1_tpc/s2_flat/s3_trs, census/phase1_basis.py, anti_cheat, PREREG; D-4 S1/S2/S3 run code,
  d4core/metrics.py and gates.py bodies, PREREG-INSTRUMENT, synthetic controls code,
  REVIEW-PACKET-PHASE1.txt, redteam_findings.json; D-5 task_generators (families, hidden
  library), compute_gates.py, preflight, PREREG-*; Ergon gen1a/gen1b/gen3 code.

## 1. Mechanism (code, not prose)

What the series IS: an escalating ladder of adversarial preconditions for one question --
"can accumulated executable history create reusable transformations of executable
structure without a human taxonomy of change?" (agent_d2_blind/MANIFEST.md s0). Each
agent froze a prereg, built substrates, and stopped at the first failed gate. None
contains a reasoning mechanism; three of four contain no learner at all.

D-2 (SUBSTRATE_INVALID). Homoiconic Lisp-like language: Val ::= Sym | List
(d2/core.py:1-14). G1 grammar: 20 V-terminals (x, nil, 18 quoted symbols) and 5 V-forms
head/tail/self/cons/if, 4 B-forms (d2/g1.py:14-24). Evaluator is a fuel-bounded interpreter
(limit 4000 steps, recursion depth 24, g1.py:86-202); `self` recurses on the whole program
(g1.py:152-159). Transforms are programs applied to programs' serialisations
(apply_transform, g1.py:210-220), output kept only if valid_V. The "experiment" is
exhaustive size-major enumeration (Enum, g1.py:225-300) plus a human-side classifier of
(input, output) pairs into WRAP/APPEND/PRE/ROUTE/DELETE/RELABEL/DUP (classify.py:14-32).
No search, no learner.

D-3 (NO_BASIS_PASSED). Four substrates sharing V = int tuples; S4 is a reversible affine
register machine over (Z_251)^6, every tuple a valid program (s4_rev.py:1-94). Mutation is
6 syntactic sequence edits for S2-S4 (SUBST/INSERT/DELETE/TRANSPOSE/DUPBLOCK/SPLICE,
mutators.py:17-68) and 5 type-directed tree edits for S1 (mutators.py:18). M0 baselines
(walk, QD, cost-biased, recombination) at 200,000 metered units. No learner.

D-4 (ACCESSIBILITY_GEOMETRY_ESTABLISHED on S2_STACK, S4_MEM). Four byte-genome VMs with
total decode (vm_substrates.py:1-23). S4_MEM is an 8-opcode tape machine (inc/dec/ptr+/ptr-
/read/write/skip/back-jump-6), 72 cells, 16-cell tape, 128 steps (vm_substrates.py:479-530)
-- essentially a Brainfuck variant. Phenotype = outputs on 8 frozen probes of 8 nibbles;
d1 = mean positional nibble mismatch (vm_substrates.py:176-187). Mutation: 5 content-blind
byte operators (bitflip burst, cell subst, block copy, block swap, rotation;
vm_substrates.py:102-138). Navigators N1-N4 are target-directed: restart walk, greedy
d1-to-target hill-climb, novelty, population recombination (d4core/navigators.py:76-323);
hit = d1 <= 0.10 to a target phenotype at 1,200 evals. No learner.

D-5 (HISTORY_FINDABILITY_ADVANTAGE). RM-D5: 8 registers, 16-bit words, 14 ops including
SKZ/SKG skips and JNZ back-jump, max length 24, 512-step budget (substrate/rm_vm.py:4-61).
Mutation: 6 classes OP_REPLACE/ARG_TWEAK/INSERT/DELETE/SWAP/DUP_BLOCK plus one-point
crossover (mutation/physics.py:7-74); 16-program seed repertoire (physics.py:78-87).
Tasks: exact 64-entry input->output tables from 7 hand-written families compiled from a
37-primitive "hidden library" (BUILD_LOG.md, entry "PHASE 1 apparatus"; files not read).
Search objective: bitwise Hamming over the whole table, correctness by exact oracle
(BUILD_LOG "pre-freeze meter change"). M0c-RX is a GA, psize 32, tournament 3, 50%
crossover, 10% immigrants (navigators/m0.py:74-128). M1 (learner/m1.py:44-97) is that SAME
GA, character-identical, with exactly one change: `fresh()` draws 50% of the time from a
library instead of the seed repertoire (m1.py:51-54). `fresh()` is used for the initial 32
and for immigrants (10% of children, m1.py:71-72). Library = solver plus up to 4
behaviour-distinct best of the last generation per task, cap 64, most-recent eviction
(m1.py:100-128). That is the whole "accumulated history" mechanism.

Documented vs code. The documents are unusually honest: each verdict states its own
limits, and the code matches the prose wherever checked. The one inflation is lexical:
"history-conditioned learner" (m1.py:1) for what is a 64-slot warm-start pool feeding
~5% of offspring plus the initial population.

## 2. Evidence (tiered)

OBSERVED (committed rows, recomputed here):
- D-2: G1 904,880 programs to size 6; 138 struct classes; 91 nontrivial semantic classes;
  live 4.61%; 154 distinct valid artifacts ever produced (phase1_summary.json;
  census_G1_diagnostic.json). G2/G3/G3B 230/273/310 classes, all fail CG-B (>=500).
  My recount of the G1 grammar reproduces 904,880 exactly (scratch dser.py).
- D-3: validity from census_rows: S1 1.000/1.000, S3 0.434/0.122, S4 1.000/1.000 at
  r=1/r=3 (1,440 rows each). M0a on S4: 14,193 semantic classes, coverage 1/60 targets,
  0 mid/far hits (basis_S4.json m0). Total meter runs 1.18M-1.45M per basis.
- D-4 (recomputed from results/*_nav_rows.jsonl): far-stratum hits N2/N4:
  S1 0/60, 1/60; S2 3/60, 9/60; S3 0/60, 0/60; S4 32/60, 25/60. Near S3 52/60 (N2):
  S3 is locally trivial-easy and remotely dead.
- D-5 (recomputed from ledgers): solves out of 290 runs each: M1 80, M0c-RX 51,
  M0b-POP 53, M0a-HC 34; ablations random-library 62, shuffled-history 77, frozen-half 73.
  gates_verdict.json: G4 +10.95pp p 0.0007 n 42; G5 HACR 2.13 CI90 [0.93, 3.70];
  G6 -0.001; G7 alien +0.05 p 0.26; G9 retention shuffled 1.00, random 0.39.
  Final libraries persisted: final_libraries/lineage_0..4.json, 64 genotypes each
  (lineage_0 sample: 7-24 instruction RM programs).
- Ergon follow-ups on D-5's library question: Gen-1B headline +2.78pp "falls by
  annotation"; Project 3 retention policy RANDOM vs MRU +0.55pp CI [-0.24, +1.33], verdict
  RETENTION_POLICY_DOES_NOT_MEASURABLY_MATTER (roles/Ergon/STATUS.md:12-27, 69-70).

CLAIMED (prose only on main):
- D-3 cites results/*.json (phase1_verdict, threshold_sensitivity, mutation_bias_r1,
  m0_comparison ...) for its gate table and its operator-confusion finding. agent_d3_blind/
  results/ is NOT tracked: the blanket `**/results/` rule (.gitignore:27) excluded it, the
  same defect Ergon fixed for D-5 only (.gitignore:29-34). D-3's G6 confusion-table claim
  (VERDICT s3.2) and the E-SWAP 100%-dead claim are therefore CLAIMED, not OBSERVED.
- D-2 ST3 witness sizes (substitution 24, scaffold 27) and "~10^25" programs at size 27.
- D-4 privilege ablation z-scores and oracle far reach (0.73 S4, 0.50 S2): in
  results/phase1_verdict.json (tracked) but not opened by me.
- D-5 "R == E theorem" (every expressible task reachable via INSERT paths <= 26 steps);
  reachability_rows.jsonl present, theorem text in PREREG-TASKS (not read).

DESIGNED: D-2/D-3 Phases 2-3 (worlds, M1); D-4 Phase 2; D-5 P5-P7. None run.

Correction to a CLAIMED number: D-2 says size 27 is "on the order of 10^25 programs"
(VERDICT s4). Recounting the frozen G1 grammar: V_27 = 1.29e30, cumulative to 27 =
1.38e30, growth ~14.9x per level (scratch dser.py). The claim UNDERSTATES the wall by
five orders of magnitude; the verdict's conclusion only gets stronger.

## 3. Matrix

### 3a Combinatorial explosion and reachability

| engine | syntactic space | explored | behavioural yield |
|---|---|---|---|
| D-2 G1 | cum(size<=n) ~ 14.9^n; 9.05e5 at n=6; 1.38e30 at n=27 | 9.05e5 = 6.6e-25 of size<=27 | 154 valid artifacts; 91 nontrivial behaviours |
| D-3 S4 | 360 token values, len<=32: 10^81.8 | ~1.45e6 runs | 14,193 classes, 1/60 targets hit |
| D-4 S4_MEM | 8^72 = 10^65.0 genomes; 16^64 = 10^77 fingerprints | 1,200 evals per episode | far hit 32/60 at d1<=0.10 |
| D-5 RM-D5 | 856 instructions, len<=24: 10^70.4 | 290 x 30,000 = 8.7e6 evals per arm | 80/290 exact solves (M1) |

Where it explodes: D-2 is the textbook case. The useful transform (structural map:
substitution + recursion scaffold) lives at size 24-27; exhaustive enumeration stops at
size 6-7 under a 1e6 cap. Gap 3.9e26 / 9.05e5 ~ 4e20. No history-free search closes it,
and the agent correctly refused to add a `map` primitive that would hand the answer over.

Where it is a desert: D-2's validity filter (4.6% live G1, 0.16% G2); D-3's S3 viability
decays 0.440 -> 0.022 from r=1 to r=8; D-3 S4 and D-4 S3 are the opposite desert --
total validity, huge phenotype count, no connectivity (D-3 S4 giant component 0.24; D-4 S3
zero far paths in ~1.5M evals). D-5's build log names the third desert: exact-match tasks
are needles -- 0/48 solved at 10k evals; a 1-mutation neighbour of a witness is 21% neutral
and otherwise jumps ~91 of 1024 bits (BUILD_LOG "MEASUREMENT: hardness probe"). The
2^1024 table space against a few thousand reachable behaviour classes is the real wall.

What the hit rates imply: the "navigable" passes (D-4) are measured against targets the
same physics emitted under an independent seed, with a loose ball (d1<=0.10 permits ~6 of
64 nibbles wrong). D-5 shows the gap directly: emitted targets 57% reachable,
externally-defined tasks 0/48 under the pointwise objective. Accessibility of
self-emitted phenotypes does not predict findability of anything a user would ask for.

### 3b Cosplay vs foundation

There is no cosplay here in the usual sense: no component is labelled "reasoning" and
the verdicts forbid the word. Component by component:
- D-2/D-3/D-4: enumerators, syntactic mutation operators and hill-climbers on output
  Hamming distance. Fixed algorithms; no adaptive component exists.
- D-5 M1: the only component credited with an effect is a 64-slot warm-start cache inside
  a fixed GA (m1.py:51-54). Its own ablation: shuffled order keeps 100% of the gain and a
  size-matched random-walk library keeps 39%. So ~39% is generic diversity injection and
  ~61% is "having some programs that were previously selected on sibling families" --
  library content, not order, not composition. G6 (no trend over development) and G7 (no
  alien transfer, +5pp p 0.26) close the remaining readings. Per family, F2 stays at 0
  (gate per_family F2 0.0): the cache does not move the frontier.
- Ceiling, concretely: a cache of whole genotypes reused as mutation starting points
  helps only when a new task's solution is within a few edits of a cached solution of the
  same hand-written family. It cannot compose two cached programs into a third (crossover
  is one-point splice, physics.py:70-74), cannot abstract (no parameterised entries), and
  Ergon's follow-up shows even the retention policy does not matter. That is
  memoisation, the floor of "learning".

### 3c Substrate bottlenecks

- Representation: all four use flat syntax (token strings, byte genomes, s-expressions)
  with syntactic mutation. No typed holes, no abstraction/application node that a learner
  could grow. D-2 G1 was the only fully homoiconic basis and was also the poorest (91
  behaviours).
- Credit assignment: none in D-2..D-4; in D-5 a scalar Hamming distance on 1024 output
  bits per genotype. No credit to sub-programs, so nothing below the whole-genotype level
  can be reused.
- Compositionality: library entries are opaque genotypes; one-point crossover is the only
  combinator. A two-stage solution cannot be assembled from two learned stages.
- Memory/addressing: RM-D5 8 regs x 16 bits, 24 instructions; S4_MEM 16 cells. Enough
  for toy tables, far below anything needing intermediate data structures.
- Probe-relative semantics: every equivalence class is relative to 8-24 probes; D-3
  measured S1/S3 class counts still moving 4.3% / 6.1% between 12 and 16 probes.

## 4. Deliverable sections

### Discovery Approach

Not discovery of intelligence; discovery of whether a FAIR test bed for history-conditioned
self-modification can exist. Freeze a prereg, census the substrate's reachable behaviour,
validate instruments on synthetic pathologies (D-4 C1-C8), build strong history-free
baselines, and only then (D-5) add the minimal history mechanism and decompose its effect
with ablations.

### The Brick Walls

1. Size gap between useful transforms and enumerable region: D-2 useful map at size 24-27,
   enumeration at 6-7; recounted 1.38e30 vs 9.05e5 programs (gap ~1e24).
2. Validity/navigability trade-off: across D-2 and D-3, bases that are valid by
   construction are disconnected or taxonomy-shaped; S3 viability 0.440 -> 0.022 (r=1..8);
   S4 14,193 classes but 1/60 targets. No basis tested in the series is both.
3. Needle landscape of external tasks: D-5 0/48 at 10k evals before partial credit; even
   after it, strongest M0 solves 22.4%, F2 0%. The space of 64-entry tables is 2^1024.
4. Memoisation ceiling: D-5's gain is 100% retained under shuffled history and 39% under a
   random library; follow-up retention-policy effect +0.55pp, CI includes 0 (Ergon P3).
5. Instrument circularity: D-3 found its taxonomy-neutrality gate measured its own six
   operators (claimed; rows untracked); D-4 navigates to self-emitted targets.

### Seed Viability

SALVAGE_COMPONENT. Carry forward, as instruments for any future substrate:
(a) the E/R/F three-way split with CFR = solved / oracle-reachable (D-5 MANIFEST);
(b) "count distinct reachable artifacts, not programs" (D-2 s8; 904,880 -> 154);
(c) D-4's synthetic pathology controls (fragmented, corridor, trapped, chaos, sparse)
as a pre-freeze instrument check; (d) D-5's causal ablation pair (shuffled-history,
random-library), which is exactly the test that separates developmental learning from a
cache and should be mandatory for every "library/learning" claim in the fleet.
Not carried forward: any of the eight substrates as a reasoning substrate; the M1 cache.
Would these instruments detect a real reasoning circuit if one arose? Partly: the G9
ablation would detect order-dependent, compositional reuse (it would show shuffled
retention well below 1.0). None of them measures composition of learned parts directly.

### Evolutionary Roadmap

The series' own successor lessons converge: (i) task ecologies where late tasks are
buildable ONLY from earlier solutions, (ii) physics without INSERT-completeness so
reachability bites, (iii) diversity injection metered as its own arm. Concretely:
1. Replace flat genotypes with a typed combinator / lambda-calculus library
   (DreamCoder-style): library entries become parameterised functions with types; new
   programs are applications over them; MDL (description length of the corpus under the
   library) is the admission criterion instead of "solver + 4 best".
2. Curriculum with forced dependency: generate family k+1 tasks as compositions
   f_k o g_j of earlier families' hidden primitives, so a cache of whole programs is
   useless and only reusable PARTS help.
3. Credit assignment to sub-terms: admit fragments (subtrees occurring in >= 2 solvers),
   not whole genotypes; compression-based abstraction (anti-unification / e-graph
   extraction).
4. Keep D-5's harness, comparator freeze and G9 ablations unchanged.
The ONE decisive experiment: on a composition-forced curriculum (family B tasks = composition
of two family-A primitives, A solved first), compare M1-fragment-library vs
M1-whole-genotype-cache vs M1-shuffled vs M1-random at equal metered budget, paired
lineages n >= 40 tasks. Kill criterion: if M1-fragment's CFR advantage over
M1-whole-genotype-cache is < 5pp, OR shuffled-history retains >= 80% of the fragment
advantage, then abstraction adds nothing beyond memoisation on this substrate and the
line stops.

## 5. What would change this verdict

- Upward to VIABLE_SEED: the decisive experiment above passes (fragment library beats
  whole-genotype cache by >= 5pp and shuffled history loses >= 20% of the gain), i.e. an
  order-dependent, compositional reuse effect appears.
- Downward to DEAD_END for the instruments: Ergon-20 (D-5 reproducibility on the merged
  tree, open per roles/Ergon/STATUS.md:50-51) fails to reproduce +10.95pp, or D-3's
  untracked results cannot be regenerated from ledgers, which would mean the series'
  measurement discipline did not survive its own storage.
- Reading the unread files (D-5 task_generators/hidden_library.py, families.py): if the
  F3/F4 families share literal sub-programs, the library gain is family leakage, which
  would further lower D-5's single positive.
