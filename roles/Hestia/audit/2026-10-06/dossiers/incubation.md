# Dossier: incubation (v1 / v2 Operator Genesis / v3 Lens Genesis) + incubation_d (Agent D, D-VM)

VERDICT: SALVAGE_COMPONENT -- every "learning" result is exhaustive or frequency-count selection over a small experimenter-designed menu (n-grams of 4 primitives, 634 search programs, 11,050 action partitions) inside worlds engineered to contain the answer; the carry-forward items are the control/census protocol and the never-exercised homoiconic D-VM, not the learners.

Audit group G7(b). Auditor: Hestia audit worker, 2026-10-06. Read-only; nothing run
except side arithmetic in the scratchpad (inc_calc2.py, numbers quoted in 3a).

---

## 0. Identity

- Paths: incubation/ (66 tracked files: v1 root, v2/, v3/), incubation_d/ (19 files).
- Census rows (docs/fleet/fleet_state.json, key engines): `incubation` "Incubation /
  Lens Genesis", research-engine, primary_seat null, state DORMANT (last commit
  5531f053f 2026-08-27); `incubation_d` "Agent D homoiconic attack", research-engine,
  primary_seat null, DORMANT (last commit 62e5649d8 2026-08-27).
- Seat: none. There is no roles/Incubation or roles/AgentD directory; Artemis lists the
  owner as UNKNOWN (roles/Artemis/threads/sfe_retrospective/notes/C_engines.md:76,894)
  and classes it "SCIENTIFIC ENGINE (small, closed)". Entire program was built and
  closed in 2 days (commits 3b5e310f6 2026-08-26 .. 62e5649d8 2026-08-27, 13 commits).
- SHAs read: worktree HEAD 3fed30ac9 (origin/main merge); engine trees at 5531f053f and
  62e5649d8.
- Read in full: incubation/README.md, docs/LESSONS.md, primitives.py, solver/engine.py,
  solver/boundary.py, concepts/mine.py, concepts/guard.py, concepts/concept.py (Guard),
  worlds/families.py, v2/README.md, v2/dsl.py, v2/learner.py, v3/README.md,
  v3/representations/lens.py, incubation_d/README.md, design_manifest.md,
  meta_language/grammar_v2.py. Read in part: v2/runtime.py:148-210 (run_stage),
  v3/learner/lens_learner.py:136-175, incubation_d/vm/machine.py:1-160,
  experiments/incubation_v1.py (structure by grep, PREREG 57-100), DOCUMENTATION.md
  sections 0 and 5 (lines 1-40, 405-440). Result JSONs: all non-row keys of
  results/incubation_v1.json, v2/results/operator_genesis_v1.json,
  v3/results/lens_genesis_v1.json, incubation_d/results/census_gv2.json.
- NOT read: census_v0..v2.py and census_meta_v0..v4.py / census_lens_v0..v2.py bodies
  and their result JSONs (their numbers are taken from README/LESSONS prose = CLAIMED
  here); v2/domains.py beyond grep; v3/worlds/families_v3.py beyond grep;
  classify_v3.py, controls_v3.py; operator_genesis_v1.py and lens_genesis_v1.py
  harnesses; all tests/; ledger/*.json entries; incubation_d/census/census.py body,
  meta_census.json, review/hitl_census_dossier.html. Per-task rows (3,125 / 1,640 /
  2,030) were counted but medians were NOT recomputed from rows; I quote the committed
  aggregate keys.

## 1. Mechanism (code, cited)

### 1.1 v1 "executable symbolic learning"

- State: tuple in Z_m^k; four fixed primitives r00 rotate, r01 swap01, r02 s0+=s1,
  r03 s0=2*s0+1 (primitives.py:31-41). Same functions in every world.
- Worlds: wA (k=6,m=997), wB (k=7,m=673, string codec), wC (k=8,m=809, band trap
  slot1 < m//5 fails at runtime) (worlds/families.py:183-187, 67-73).
- Task generation PLANTS the composition: embed witness = X + M + Y with
  M=(r01,r02,r01), |X|,|Y| in {2,3} (families.py:135-149), then an omniscient filter
  keeps only tasks whose EVERY minimal solution contains M (families.py:124-133).
  Training cell A_train is 30 embed tasks per seed, all embed=True
  (experiments/incubation_v1.py:57, 248).
- Solver: plain IDDFS over the action alphabet, dmax 12, node budget 12M
  (solver/engine.py:106, 145-231); BFS-with-dedup control (engine.py:247-291). A
  "reified" action costs depth 1 (engine.py:119-121) -- that single line is the whole
  source of the "reification" advantage.
- Concept formation (concepts/mine.py:375-400): count contiguous 2..4-grams of the 30
  solutions, group by execution fingerprint on the episodes' start states, score
  support x (len-1), take the top. Hypothesis space: 4^2+4^3+4^4 = 336 words.
- Guard learning (concepts/guard.py:21-125): atoms are "slot j of probe(s) < c" or
  "== c", probes = prefixes of the concept word plus single primitives (guard.py:24-25);
  exact cover by <= 2 atoms, cheapest first. The trap is literally "slot1 < 161"
  (families.py:62,68), i.e. exactly one atom of the guard language.

### 1.2 v2 "Operator Genesis"

- DSL (v2/dsl.py:28-48): a STAGE is 1-2 processes from {A,Z}x{succ,pred}, a schedule
  from {ONLY0, ONLY1, ALT, IF obs op obs} (obs in {DEPTH,DUPS,FSIZE}), and a halt in
  {ANY,GOAL,MEET}. Count: 4 + 10 pairs x 21 schedules x 3 halts = 634; SEQ of two
  stages = 634^2 = 401,956. The runtime (v2/runtime.py:148-208) implements MEET
  natively: if the program contains an (A,S) and a (Z,P) process, newly expanded
  states are checked against the other process's visited set and the concatenated word
  verified (runtime.py:195-208). Meet-in-the-middle is therefore a built-in runtime
  behavior that 2.52% of the menu switches on, not something constructed from smaller
  parts.
- Construction (v2/learner.py:64-83): run ALL 634 programs on the learner's failed
  tasks, cheapest admissible wins. Trigger: >=30% budget failures over >=10 tasks
  (learner.py:29-31, 45-50).
- "Learning to learn" (learner.py:132-154): naive order = canonical list; experienced
  order = [library] + [SEQ(a,b) for a,b in library] + mutants... (learner.py:139-146).
  With a 1-item library, SEQ(o0001,o0001) is hard-coded to candidate #2.
- Revision (learner.py:159-190): choose the first of 4 hand-supplied features
  (AUDIT_T, AUDIT_S, NPRED_T, NPRED_S) that separates bad from good by a threshold.

### 1.3 v3 "Lens Genesis"

- A lens is a partition of a subset of the primitive alphabet into 1-3 groups
  (v3/representations/lens.py:53-77). Applying it: discover each group's slot support
  by execution, reject overlapping supports, solve one subtask per group with the
  unchanged v2 operator, concatenate, replay (lens.py:111-176).
- Construction: exhaustive over 11,050 lenses (8 primitives); 326 pass the support
  precheck; 1 is admissible in every seed (lens_genesis_v1.json per_seed.construction).
- Worlds (v3/worlds/families_v3.py:3-25, 43-140, grep only): registers with HIDDEN
  BLOCKS of slots plus cross-block decoys; i.e. the world is a direct product of
  independent sub-problems plus two coupling primitives, by construction.
- Recursion (lens_learner.py:136-157): extension_order keeps prior groups, keeps prior
  exclusions excluded, and enumerates only assignments of NEW primitives to
  {existing group, one new group, excluded}: (g+2)^n_new candidates.
- Revision (lens_learner.py:162-167): cap = 10 x clean median cost.

### 1.4 incubation_d (Agent D)

- D-VM (incubation_d/vm/machine.py): object tier o0..o4 = add/mul mod 97, dup, swap,
  skip-if-zero (machine.py:69-123); caps stack 16, block 64, 64 steps
  (machine.py:16-19). No loops, no calls, no recursion in the object tier (only o4
  skips one instruction, machine.py:111-119). Meta tier d00..d15 is a STRAIGHT-LINE
  Block editor (exec_meta, machine.py:148+, "for ip, op in enumerate(prog)" at 177):
  no meta conditional, no meta loop (also design_manifest.md section 3,
  grammar_v2.py GRAMMAR_SPEC meta_conditional False).
- Census: shortlex enumeration of all typed Block->Block meta programs to L=5 over
  21 tokens (grammar_v2.py TOKENS), structural and semantic fingerprints on 7 probe
  artifacts x 5 probe stacks, 7 kill gates CK1-CK7.
- Nothing else exists. Worlds A-F, M0/M1 learners, ledger, QD archive: "Not yet built"
  (incubation_d/README.md:37-43). Artemis confirms no later commits
  (roles/Artemis/backlog/harvest/D4_sfe_era.md:454-458).

### Documented claims vs code

| Claim (doc) | What the code does |
|---|---|
| "the miner produced M from the solver's own solutions" (README Results) | n-gram count over 30 tasks each FILTERED to contain M in every minimal solution; support 30/30 (per_seed[0].mine_report.top10[0]) |
| "learned guard recovered the dynamics boundary 161" | threshold-max over a guard language whose atom form equals the trap's form (guard.py:60-68 vs families.py:68) |
| "the learner reinvented meet-in-the-middle from cost pressure" (v2 README) | argmin-cost over 634 menu items; MEET semantics are implemented in runtime.py:195-208 |
| "experienced learner found SEQ(o0001,o0001) at candidate #2" | position 2 is fixed by learner.py:141 for a 1-element library |
| "constructed a new typed representation" (v3) | argmin over 11,050 partitions of an 8-letter alphabet; only 1 admissible |
| "homoiconic attack / reusable transformations of own machinery" (D) | a grammar census; no transformation has ever been learned or used |

The authors state most of this themselves (DOCUMENTATION.md:407-433: "Bounded
construction, not open-ended invention ... the menu of organizations is fixed";
v3/README.md "Honest notes" 3: "who wrote the ontology remains the open question").
The audit agrees with their scope section and disagrees with their headline verdict
names (RECURSIVE_LEARNING_EFFECT, RECURSIVE_REPRESENTATION_EFFECT), which oversell it.

## 2. Evidence (tiered)

OBSERVED (committed JSON on main, aggregates read; rows present):
- v1 results/incubation_v1.json: 5 seeds, 3,125 rows, 16/16 gates true. P0 median
  70,088 nodes, P3 11,762, P3R 230,626, P1 (BFS) 27,453 on wA held; P3/P0 = 0.169
  [0.164,0.171]; wB P3/P0 = 0.170; wC hostile P3/P0 = 2.85; wC blind failures
  2,102,725 / 6,978,052 attempts (0.30), 0 in wA/wB; guard OOS accuracy
  1.0/0.9975/1/1/1; guarded failures 0 vs 2,207,501. Miner top candidate support 30 of
  30 (seed 11), candidate identical in 5/5 seeds. K2 kill condition "SCOPED":
  bidirectional search solves these tasks in ~1e3 nodes.
- v2 v2/results/operator_genesis_v1.json: 1,640 rows, 20/20 gates, solve A0 0.30 vs
  A2 1.0 held (n=150), A2/A0 ops 0.0115; dC 0.0171; seed 11 construction 634
  candidates, 62,279,994 ops, 12 admissible (1.9%); o0001 differs across seeds
  (o0001_consistent false); dD blind A2 solve 0.914; naive E learner 1,200 candidates,
  72M ops, not found.
- v3 v3/results/lens_genesis_v1.json: 2,030 rows, 21/21 gates, 11,050 lenses, 326
  valid, 1 admissible per seed; R3 solve 1.0 vs R2 0.30; R3/R2 ops 0.0008; vD blind
  solve 0.533; E naive 1,500 candidates not found, experienced found at 68.
- D incubation_d/results/census_gv2.json: 4,288,305 sequences, 744,215 typed,
  28,891 valid, 1,584 structurally distinct, 1,296 semantically distinct, 238 mixed,
  verdict GRAMMAR_PASSED_CENSUS; gv0, gv1 rejected (rejected_grammars.jsonl, 2 lines).

CLAIMED (prose only, I did not open the backing JSON): census rejection numbers for
v1 census_v0/v1, v2 meta_v0..v4 (78 behavioral organizations, 2.52%, rank 49, growth
3.55^d), v3 lens_v0..v2 (28 classes, singleton rank 2,957, vE solver class min rank
523,378); the "first full run thrown out by anti-cheat" (commit message).

DESIGNED (never run): all of incubation_d beyond the grammar census (worlds A-F, M0 vs
M1, transform-of-transform, NULL world F, Holm-Bonferroni battery); v3's own "next
question" (failure routing plasticity across layers, v3/README.md last paragraph).

## 3. Matrix

### 3a. Combinatorial explosion and reachability

Search spaces (scratchpad inc_calc2.py):
- v1 states: 997^6 = 9.8e17 (wA), 673^7 = 6.3e19 (wB), 809^8 = 1.8e23 (wC). Task
  depth 7-9. Primitive IDDFS cumulative nodes: 29,116 (d=7) / 116,496 (d=8) /
  466,020 (d=9); with the macro (b=5, depth -2): 970 / 4,875 / 24,405. Observed
  P0 70,088 and P3 11,762 sit exactly where branching arithmetic puts them; the 0.169
  ratio is predictable before running anything (it is b^d accounting, Korf-style
  macro-operator math, not an emergent effect). The concept hypothesis space is 336
  words and the filter guarantees the answer has support 1.0.
- v2: 634 stage programs, 401,956 two-stage, 634^k for k stages. Measured cost
  ~98k ops per candidate (62.3M / 634). Exhaustive k=2 = ~3.9e10 ops; k=3 =
  2.5e8 programs, ~2.5e13 ops: the wall arrives at the third composition level.
- v2 recursion: canonical (naive) rank of SEQ(o0001,o0001) computed from dsl.py: 5,466
  for the ALT winner (634 + 4,832) and 284,652 for the FSIZE winner (634 + 284,018).
  The naive cap is 1,200, so the naive learner CANNOT reach the answer by design; the
  ">=600x separation" is cap / 2. True rank ratio 2,700x-142,000x, but it measures
  the hand-coded order at learner.py:139-141, not something learned.
- v3 lens count for an alphabet of n primitives = sum_j C(n,j)(S(j,1)+S(j,2)+S(j,3)),
  growth ~4^n/6: n=8 11,050; n=10 175,274; n=12 2,798,250; n=13 11,188,906. Allowing
  more than 3 groups makes it Bell-number-like (super-exponential). Hit rate 1/11,050
  = 0.009% (OBSERVED). Extension order with 4 new primitives and 2 prior groups =
  4^4 = 256 candidates vs 2,798,250, a 10,900x pruning that is entirely the
  hand-written assumption "prior groups stay valid" (lens_learner.py:136-157).
- D: 21^L meta programs: 4.29e6 to L=5, 8.6e7 at L=6, 3.8e10 at L=8, 1.7e13 at L=10.
  Typed-valid survivors 28,891 / 4.29e6 = 0.67%; distinct behaviors 1,584 = 0.037%.
  New behaviors per length 1, 22, 48, 292, 1,221 (x~4.2/length): the useful space is
  a thin, exponentially sparse shell. Any real transform (insert/mixed edit) starts at
  length 4; a transform-of-transform would need L >= 8-10, i.e. 1e10-1e13 raw
  sequences -- an unexplored desert with no learner yet built to cross it.

Reachability desert summary: every experiment is solvable only because the world was
iterated (2-5 census rejections each) until the planted answer was reachable, forced,
and inside a menu small enough to enumerate. Outside the designed family the hit rate
is undefined (never measured).

### 3b. Cosplay vs foundation

What does the work called "learning":
- v1: an n-gram frequency counter + one line making a macro cost depth 1. Fixed
  algorithm (macro-operator learning, Fikes/Korf 1972-85). Ceiling: macros of length
  <= 4 over a fixed alphabet; no macro-of-macro; mining is only correct when a filter
  has made the target ubiquitous.
- v1 guard: threshold fitting over a feature language shaped like the trap. Ceiling:
  disjunctions of 2 atoms of form slot<c or slot==c.
- v2: exhaustive argmin over 634 programs; the "algorithm" (meet-in-the-middle,
  Pohl 1971) lives in runtime.py:195-208 and is selected, not composed. Ceiling: the
  634 menu; o0001 even differs syntactically between seeds because many menu items tie.
- v3: exhaustive argmin over 11,050 partitions; the payoff (1,250x) is the textbook
  product-decomposition gain sum b^d_i vs b^(sum d_i) on a world BUILT as a product.
  Ceiling: <=3 groups, disjoint slot supports, worlds with hidden product structure.
- "Recursive" effects: hand-written candidate ordering (library-first). The learner
  did not learn the ordering; the experimenter wrote it.
- D-VM: no learner exists, so nothing to classify. The substrate is genuinely
  homoiconic (programs are Blocks, qlit reifies), which is the one property none of
  v1-v3 has, but the meta tier has no conditionals or loops and the object tier has no
  iteration, so its expressible transforms are bounded straight-line edits.

Verdict on 3b: a careful, honest selection loop over tiny designed operator sets. Not
cosplay in the sense of faked results -- the rows are real and the controls are
strong -- but cosplay in the sense that each "level" (concept, algorithm,
representation) is a different hand-built menu, and nothing composes ACROSS levels
or produces a new menu item. The program's own gen-30 "bounded-menu wall" note
(DOCUMENTATION.md:414-419) concedes this.

### 3c. Substrate bottlenecks

- Representation: three incompatible artifact types (primitive word, DSL tuple,
  partition) with three separate engines; a v1 concept cannot appear inside a v2
  program or a v3 lens. No common term language = no compositional reuse across
  levels. Only D-VM fixes this and it is unrun.
- State/memory: the "library" is a Python list of 1-2 items; ledgers are JSON audit
  records, never read back by the learner as data except via the hard-coded order.
- Addressing: guards and routers index raw slot positions (guard.py:60) and 4 named
  features (learner.py:159); no learned features.
- Credit assignment: whole-artifact accept/reject by paired cost ratio; no partial
  credit to sub-parts, so no gradient of improvement inside a menu item.
- Compositionality: v1 macro is length <= 4 and never re-mined over macros; v2 SEQ
  is 2-level max; v3 extension only adds primitives to fixed groups.
- I/O / oracle: exact equality oracle on a single target (boundary.py:325-326);
  worlds are deterministic, noiseless, tiny. Equality oracles make verification free,
  which is what makes exhaustive enumeration viable; any graded or noisy objective
  breaks the current construction loop.
- Throughput: v3 run 1,171 s, v2 459 s, v1 561 s (wall_sec); cheap, so the limit is
  design, not compute.

## 4. Deliverable sections

### Discovery Approach
Build exact-oracle toy reachability worlds, plant a structure (a composition, a
need for bidirectional search, a hidden product decomposition), census the world
until the structure is forced and the answer is not trivially "spelled" in the
menu, then let a learner pick the cheapest item from an enumerated menu after a
failure trigger, and measure the cost delta with very strong controls (flat, random
twin, ablation counter-identity, frozen-hash transfer, hostile world, revision).
incubation_d moves the same discipline onto a homoiconic stack machine so that
transforms of programs are themselves programs; only its grammar census was run.

### The Brick Walls
1. Menu-bounded construction: answer exists only as one of 336 / 634 / 11,050 designed
   candidates; lens space grows ~4^n/6 (2.8M at 12 primitives), SEQ space 634^k
   (2.5e8 at k=3). Exhaustive argmin is the learner, so the wall is the menu size.
2. Planted answers: v1 miner support 30/30 because the filter forced it; v3 has 1
   admissible lens of 11,050 because the world is a product by construction. Hit rate
   on worlds not designed around the answer: never measured (0 such worlds).
3. "Learning to learn" is a hand-written ordering: SEQ(lib,lib) is candidate #2 by
   code; naive rank is 5,466-284,652 against a cap of 1,200; extension order prunes
   2,798,250 to 256 by assumption. No learned prior exists anywhere.
4. Expressivity of D-VM: no meta conditional, no loops at either tier, 64-step object
   cap; behaviors 0.037% of sequences at L=5 and transform-of-transform needs L>=8
   (3.8e10 raw sequences) with no learner built.
5. Three separate type systems; zero cross-level composition.

### Seed Viability
The learners are a DEAD_END as mechanisms: they are known algorithms (macro mining,
bidirectional search, factored planning) re-derived by exhaustive selection, with a
ceiling equal to the experimenter's menu. Two components should be carried forward:
(a) the measurement protocol -- census-before-build with pre-stated pass bands,
flat-plus-random-twin controls, ablation counter-identity, strict meters, sha-pinned
enumeration order, and acquisition cost to first competence as the metric of
learning-to-learn (docs/LESSONS.md 1-15). This instrument WOULD detect a real
reusable circuit if one arose, and it would also expose a fake one; it is the best
abstraction-learning ruler in this group. (b) The D-VM homoiconic substrate
(vm/machine.py) plus its grammar census, as the only design here where a learned
transform could itself be data for the next transform. Hence SALVAGE_COMPONENT.

### Evolutionary Roadmap
1. One term language. Re-express v1 macros, v2 search programs and v3 lenses as
   Blocks in a single typed homoiconic calculus (extend D-VM, or adopt a typed lambda
   calculus with a small combinator basis). Success test: a v1-style macro appears as
   a subterm of a v2-style search program without new code.
2. Add the missing control: meta-tier `select` / block-equality and a bounded
   fixpoint/iteration combinator (structural recursion with fuel), so transforms can
   branch on artifact content. Re-census (CK1-CK7) after the change; this is the
   documented deferred item (design_manifest.md, "Deferred").
3. Replace hand-written orders with a learned generative prior: a probabilistic
   grammar over Blocks whose weights and new productions come from library learning by
   compression (anti-unification / e-graph refactoring as in DreamCoder/Stitch,
   scored by MDL: description length of corpus solutions given the library). The
   "experienced order" then becomes the posterior of that grammar, not learner.py:139.
4. Worlds the authors did not design around the answer: a separate world-generator
   agent (POET/PAIRED-style) proposes tasks, gated by the existing census for
   solvability and non-triviality, with held-out world families authored by a
   different procedure than training families. Measure open-endedness: library size,
   compression ratio, and depth of the deepest admitted term that references earlier
   admitted terms (transform-of-transform depth).
5. Credit assignment within artifacts: score subterms by ablation (the protocol
   already has counter-identity ablation) to allow partial reuse instead of
   whole-artifact accept/reject.

THE decisive next experiment (it is incubation_d's own Q12, sharpened): on the
frozen gv2 D-VM (plus step 2 only if CK5 demands it), build World A and a held-out
world family generated by an independently written procedure; run M0 (shortlex
canonical) vs M1 (ordering = MDL-learned grammar fitted ONLY from M1's own admitted
ledger Blocks, no hand-written neighborhood list) under identical meters, 5+ seeds.
Primary metric: acquisition cost (candidates + ops) to the first admitted transform
on the held-out family. Kill criterion: M1/M0 acquisition cost median with 95% CI
lower bound >= 0.5 on the held-out family, OR every admitted transform maps to a
single legacy edit shape (append/prepend/wrap/delete), OR no admitted transform's
construction history consumes an earlier admitted Block (transform-of-transform
depth 0). Any of the three = the homoiconic seed is dead too and the protocol is the
only salvage.

## 5. What would change this verdict

- Upgrade to VIABLE_SEED: the decisive experiment above passes, with M1's ordering
  learned (not written) and transform-of-transform depth >= 2 on a family the
  learner's authors did not design around a planted answer.
- Upgrade (partial): evidence that any v1-v3 learner finds the answer on a world where
  the answer was NOT planted and the menu was NOT iterated by census to contain it
  (e.g. random generator systems, measured hit rate). None exists in the repo.
- Downgrade to DEAD_END: if an independent reviewer shows the protocol's controls are
  not transferable (e.g. counter-identity ablation is unattainable for stochastic
  substrates, which all G1-G6 engines are) AND the D-VM census numbers fail to
  replicate from census.py; then nothing here carries forward.
- Correction risk: I quoted CLAIMED census numbers without opening their JSON, and did
  not recompute row-level medians; if those disagree with the aggregates, Section 2
  must be re-tiered. Same-model-family bias: the engine author and this auditor share
  a model lineage; the verdict should be attacked by a different reviewer.
