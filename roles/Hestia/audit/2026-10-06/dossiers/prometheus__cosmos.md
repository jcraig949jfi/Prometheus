# Dossier: prometheus/cosmos (Cosmos World-Graph Engine, CWE)

Audit: Hestia audit 1, group G4 (world engines). Auditor: Hestia audit worker (claude-opus-5-5).
Rubric: roles/Hestia/audit/2026-10-06/AUDIT_PLAN.md s2-s4 (binding).

VERDICT: SALVAGE_COMPONENT -- Cosmos is a law-mining chamber over hand-written memory toys, not a cognitive substrate; carry forward the C3 P1/P2 functional-memory certificate (decodability + interchange) and the definition-rung/adversary discipline, and stop treating the world graph as a place reasoning could arise.

## 0. Identity

- Code: prometheus/cosmos/ (106 tracked files, 12,639 Python lines). Seat: roles/Cosmos/ (210 files).
- Worktree read: C:/Prometheus-worktrees/hestia-boot-2026-10-06 at 3fed30ac9 (origin/main merge).
  Last commits touching the engine: 79dc4c4b8 (Theseus foreign C4 family), 5f5051e66 (C4 DESIGN v0.2).
- Seat state (roles/Cosmos/STATUS.md:3-6, journal/2026-10-06.md): ACTIVE. C0/C1/C2 closed with two
  RESTRICTED laws; C3 KILLED BEFORE HOLDOUT; C4 DESIGNED v0.2, build NOT authorized; D2 sealed, unspent.
- Census kind: research-engine (fleet_state.json per AUDIT_PLAN s1; not re-read here).
- READ in full or in the cited ranges: __init__.py; contract.py; phenomenon.py; world.py:15-45;
  substrates/regs.py (all), ring.py:1-48, ca.py:1-48; miner.py:1-200, 339-430 and the def index;
  pipeline.py (all); quotient.py:1-40; c3/system.py (all); c3/certify.py (all); c3/task.py:1-40;
  c3/calib.py:1-60; c3_holdout_D/medium.py:1-40; c4/families/theseus_sediment/world.py:1-60;
  holdout/{well,swarm,clone}.py space() only.
  Seat docs: STATUS.md, research/RESULTS.md, research/GRAVEYARD.md, calibration/LEDGER.md,
  design/02_cwe_as_built_2026-09-23.md, research/reviews/AUTOPSY_C3_PUBLIC_2026-09-30.md,
  c4/DESIGN_C4.md s1-s4, journal/2026-10-06.md, campaigns/c0/run2_f31339054/REPORT.txt,
  c3/runs/GATE_v2_FAIL.json and GATE_v3_PASS_seeds6to10.json (summary keys),
  campaigns/c0/run1_1d4465df9/sampler_eta.json (first 800 chars).
- NOT READ: adversary.py, select.py, locate.py, sampler.py, broker.py, store.py bodies (only def
  indices); the entire c3_holdout_D2/ custody stack (6.5k lines incl. runner.py 1344, protocol.py 795,
  selftest_protocol.py 1623) beyond line counts; holdout physics bodies; c3/probe.py beyond the Logit
  class header; all atlas_export jsonl; C1/C2/c2abl/c2x REPORT files (I rely on RESULTS/GRAVEYARD, which
  cite them); the withheld C3 branches (not on origin, by design). No engine was run.

## 1. Mechanism (what the code does)

1.1 The world. Every Cosmos world implements ONE functional demand, fixed in the contract
(contract.py:22-25): a cue (one of V symbols) appears, K distractors arrive over a horizon, and at the
ask the system is rewarded iff it emits the cue. V is at most 16 in visible families (regs.py:33,
ring.py:34, ca.py:34), so the task carries at most log2(16) = 4 bits of relevant history. That is a
delayed match-to-sample task, the simplest memory task there is.

1.2 The "agents". There are none that adapt in C0-C2. Each family ships three HAND-WRITTEN reference
mechanisms (contract.py:17-20, MECHANISMS at :34): SEL (keep only the cue), LOG (keep everything), LAST
(keep nothing). In regs these are literal register programs (regs.py:7-10, 74-99). world.evaluate runs
all three on common random numbers (world.py:19-31) and the certificate asks one question:
does SEL beat max(LOG, LAST) by 0.10 in reward-minus-maintenance-cost (phenomenon.py:32-43). The only
"behavior" anywhere in C0-C2 is a comparison of three fixed programs under a price list.

1.3 The physics. Three visible families (regs: metered bit registers with flips; ring: delay-line
packets with loss and eviction; ca: block tape with optional majority repair) and three sealed
families (well, swarm, clone). Each is ~100-130 lines of numpy implementing noise + cost on a stored
symbol (regs.py:86-98 is the whole of regs' dynamics). They differ in HOW a symbol decays and what it
costs, never in what has to be computed.

1.4 The "discovery" engine. miner.py enumerates expressions over declared coordinates C, N, K, G (+Q in
v3/v4) with unary log, exp(-x) and binary + - * /, size <= 6 (miner.py:3-7, 33, 81-100), fits a
threshold per expression by sorted cumulative balanced accuracy (miner.py:111-139), and searches
single atoms plus greedy two-atom conjunctions (P1 = 60 first atoms, P2 = 4 seconds, NPAIR = 60 scored
pairs; miner.py:37-39, 383-426). Scoring is leave-one-lineage-out over 3 lineages (miner.py:339-381;
pipeline.py:18, 86-88), with a whole-search permutation null (miner.py:461-474). The coordinates are
DECLARED by the family author from the spec (contract.py:8-9, e.g. regs.py:45-56), never measured.

1.5 C3 (killed) and C4 (designed). C3 changed the object: a generic System interface
(c3/system.py:3-12) with a full causal state, a trained multinomial-logistic readout as the "policy"
(c3/system.py:70-75), and a two-part certificate: P1 = held-out cross-entropy gain of decoding the cue
from the state over the current observation, with a within-stratum permutation null
(c3/certify.py:24-56); P2 = paired episodes sharing all noise, swap the two rows' full states at t = k,
measure the drop in correct answers, 3-SE test (c3/certify.py:59-73); class FUNCTIONAL / PASSIVE /
INCOHERENT / NONE (c3/certify.py:76-90). Planted calibration systems N0, PV, FX, FD, MC, NZ
(c3/calib.py:1-60). C4 (roles/Cosmos/c4/DESIGN_C4.md s3-s4) adds task-independent SYSID probes under
six import/mutation/invariance guards, and gates any law on uplift over the zero-parameter shortcut.

1.6 Where the code mass is. Physics (all 8 families incl. D medium and Theseus sediment): 1,181 lines.
Mining/adversary/selection/location/quotient/sampler: 1,122 lines. Sealing, custody, firewall,
broker and holdout selftests: 6,471 lines. Governance outweighs physics 5.5 : 1.

Documented vs code. The package docstring calls it "an adversarial chamber over executable
counterfactual worlds" (__init__.py:3-8) and explicitly says nothing here runs an LLM or adjudicates
reality. That is accurate. The seat never claims Cosmos grows reasoning; its own question is whether a
substrate-independent LAW of when memory pays exists. The charter-level framing "world physics engine
in which reasoning could arise" is NOT supported by any code path: no component searches over
mechanisms, policies or programs in C0-C2 (as-built D-list: "evolution (C0 is search-free by
charter)", design/02:73).

## 2. Evidence (tiered)

OBSERVED (committed rows/results on main, looked at):
- C0 run2 (campaigns/c0/run2_f31339054/REPORT.txt): 721 world nodes, 243 edges, 799 runs, 867 chamber
  queries; 3 laws proposed, all 3 killed by the adversary (17/108, 11/108, 25/108 confirmed
  counterexamples); G1 FAIL, G4 FAIL. World quotient: 721 nodes -> 8 behavioral classes (0.011).
- Sealed adjudications (RESULTS.md R-0001/R-0002, recomputed by the seat 2026-09-29 from
  G5_holdout.json, C0E.json, F_adjudication.json): law A BA .983/.972/.930 on D/E/F; law B .955 on F.
  The zero-parameter DEFINITION RUNG written from the certificate's own economics scores
  .973/.971/.887 (v3) and .943 (v4, F). McNemar law vs rung: p .688, .688, .125, .227. No significant
  margin anywhere. Status RESTRICTED: "a planted-invariant recovery, not a discovered law".
- T-I1 fragment test v3 (GRAVEYARD.md tail; research/analysis/t_i1_fragments_v3.json): 11 of 15 law
  atoms re-express the definition rung beyond a rate-matched null; the atoms that died robustly
  (G-0004) are the non-certificate ones.
- Sampler: P4 "active beats random by >= .03" lost (active .790 vs random .788 at B=30; .807 vs .831 at
  B=60); eta2 cost lines .767 vs random .946 BA (calibration/LEDGER.md rows 2, 11). At budget 30 each
  seed/strategy returns a DIFFERENT law (sampler_eta.json: e.g. "(K/(log(C)/K)) <= -1.597 AND ..." vs
  "(K/(N - log(C))) >= .5523"): the law language is non-identifiable at the data scale used.
- C3 certificate calibration: GATE_v2 FAIL (NZ one INCOHERENT in 5 seeds) then GATE_v3 PASS on seeds
  6-10, all six planted systems classified as expected 5/5 (c3/runs/*.json summary).
- C3 autopsy (AUTOPSY_C3_PUBLIC_2026-09-30.md s2): zero-parameter P1/P2 precondition rule reproduces
  104/120 visible classes and 12/12 substitutions; law vs rule 6:1 discordant in-sample (p .125, all
  noise-floor), 42 = 42 on the confident out-of-sample stratum; coordinate rank-correlates .875 with the
  P2 effect; coordinate set identifies family at .77 vs chance .33.

CLAIMED (prose only, not checked against rows by me): Artemis R-14 analytic formula 0.960 BA on the c2
pool (cited secondhand in GRAVEYARD); C2 rerun byte-identical (STATUS 2026-09-25 block); "cosmos suite
93 passed" (journal 2026-10-06).

DESIGNED (not run): all of C4 (DESIGN_C4.md, "build NOT authorized"); D2 holdout (sealed, unspent);
Theseus sediment family exists as code + SELFTEST.json but no C4 campaign rows.

The seat's own record is unusually honest: every positive in C0-C3 has been downgraded by the seat
itself (RESTRICTED x2, KILLED x1) with the definition rung as the reason. This audit agrees with
those downgrades and adds no rescue.

## 3. Matrix

### 3a Combinatorial explosion and reachability

World lattice (computed, scratchpad cosmos_sizes.py, from the space() dicts):
  regs 4*3*5*2*10*6 = 7,200; ring 28,800; ca 28,800  -> visible 64,800 worlds.
  sealed: well 25,920; swarm 48,600; clone 64,800.
  C0 run2 observed 721 nodes = 1.1% of the visible lattice. That is NOT a reachability problem: the
  quotient says those 721 collapse to 8 behavioral classes (REPORT.txt last block). The battery
  (quotient.py:18-27) has 4 binary probes, so at most 2^4 = 16 classes exist; 8 are realized. The world
  space is not a desert, it is a near-flat plain with one boundary: the phase line where memory stops
  paying. There is nothing deeper to reach.

Law language (reimplemented enumerate_exprs, miner.py:81-100, in scratchpad):
  4 terminals, size <= 6: 13,272 expressions (sizes 1..6: 4, 8, 44, 280, 1,624, 11,312) -- matches the
  seat's "13,272 -> ~4,400 rank classes" (design/02:41). 5 terminals (v3/v4): 25,695.
  Two-atom conjunctions with direction: ~(2*13,272)^2/2 = 3.5e8 (4 terms), 1.3e9 (5 terms).
  The miner evaluates 120 first atoms x 4 seconds = 480 candidate pairs and LOLO-scores 60
  (miner.py:390-411): 60 / 3.5e8 = 1.7e-7 of the conjunction space, chosen greedily.
  Growth: expressions of size s grow roughly x6.5-7 per node (1,624 -> 11,312), so size 8 would be
  ~5e5 and size 10 ~2.5e7 before conjunction. The grammar explodes exactly where a non-trivial law would
  live, while the data (hundreds of rows, 3 folds) cannot identify even the size-6 laws (different seeds
  -> different laws, sampler_eta.json).

Measured hit rates: 9 laws proposed across C0-C2, 7 killed, 2 survived to RESTRICTED (GRAVEYARD
G-0001..G-0005, RESULTS R-0001/2); 1 of 1 C3 laws killed. Laws that beat the definition rung: 0 of 10.

### 3b Cosplay vs foundation

- Work called "law discovery": a fixed enumerative symbolic-regression grammar with threshold fitting
  (miner.py). Not compositional in any learned sense; it is exhaustive enumeration to size 6 plus a
  greedy conjunction. Its ceiling is reached and documented: it rediscovers the certificate's own cost
  economics (C - G e^-N atom, GRAVEYARD cross-entry note; T-I1 v3), i.e. a measurement artifact
  re-derived through the coordinates the author declared.
- Work called "memory" or "selectivity": three hand-coded programs (contract.py:17-20). Nothing in the
  world selects, learns or composes. SEL is correct by construction; the only question is its price.
- C3's "policy": a logistic regression on a readout vector (c3/system.py:70-75) - a linear probe, not
  an agent. The C3 substrates are dynamical media (D: advection-diffusion-reaction channel,
  medium.py:1-35; Theseus: sediment bed, world.py:1-30) whose "memory" is passive physical trace.
- Would reasoning be SELECTED FOR in these worlds? No. The demand is "hold <= 4 bits for <= 40 steps
  against noise and a price". The optimal policy is a single latch; any reasoning beyond a latch has
  zero fitness value in every Cosmos world (no composition of cues, no conditional rule, no multi-step
  dependency, no second query). The world is structurally incapable of rewarding anything above
  reflex + one register.
- Verdict for 3b: as a reasoning substrate, cosplay-by-category (it never claimed to be one). As a
  meta-science instrument, foundation-grade discipline: definition rung, LOLO, adversary with
  coordinate-preserving attacks, sealed holdouts, graveyard.

### 3c Substrate bottlenecks

- Representation: coordinates are declared by the family author from the spec (contract.py:8-9). Every
  law is therefore bounded by what the author already believed (C0 coordinate map went v1 -> v4 in one
  day by hand, design/02 D11/D16). This is the root cause of both failures (L1, L6 of the autopsy).
- State: C0 has no system state at all beyond the fixed carrier; C3 state is (E, D) numpy arrays read
  linearly.
- Addressing / I/O: one input channel, one output symbol, one ask per episode (c3/task.py:1-12).
- Credit assignment: none (no learner). The readout is trained once per world by convex fit.
- Compositionality: zero in the world (single demand), bounded in the miner (size 6, 2 atoms).
- Statistical: 3 lineages -> 3 LOLO folds; one author lineage for 6 of 6 sealed+visible C0 families
  (RESULTS R-0001 domain). The universality gate MIN_LINEAGES = 3 (pipeline.py:18) is met nominally
  but not in authorship.
- Engineering: custody/sealing code 6,471 lines vs physics 1,181 lines. The bottleneck is not compute;
  it is that each new world costs an authored family plus a sealing ceremony.

## 4. Deliverable sections

### Discovery Approach
Cosmos builds several independently coded "physics" in which holding a cue costs something and decays,
runs three fixed memory programs in each, labels each world by whether selective memory pays, and then
searches a small symbolic grammar over author-declared dimensionless coordinates for a threshold law
that predicts that label across substrates, attacked by an adversary and adjudicated by sealed holdout
families. C3/C4 generalize the label to "does the system's state causally carry the cue to behavior"
(P1/P2). It maps the economics of memory, not the physics of intelligence.

### The Brick Walls
1. Definition-rung wall: 0 of 10 mined laws beat the zero-parameter rule written from the certificate
   (best margin: McNemar p .125 on F; C3 42 = 42 out of sample). The miner recovers its own label.
2. Task-poverty wall: one demand, <= 4 bits, one ask; 721 observed worlds collapse to 8 of at most 16
   behavioral classes. No world rewards anything above a latch, so no search inside Cosmos could select
   reasoning even if a searcher were added.
3. Grammar/identifiability wall: 13,272 atoms and ~3.5e8 conjunctions over ~hundreds of rows and 3
   folds; 60 conjunctions (1.7e-7) are scored; different seeds return different laws at B = 30.
   Going to size 8 (~5e5 atoms) makes identifiability worse, not better.
4. Authorship/cost wall: one author lineage for all C0 families; 5.5 lines of custody per line of
   physics; each sealed universe is spent once. Throughput of independent worlds is a few per month.

### Seed Viability
No reasoning seed exists in Cosmos, and none was attempted. Two components are worth carrying forward:
(a) the C3 P1/P2 certificate (c3/certify.py + c3/calib.py): a substrate-agnostic test that a state
causally carries history into behavior (decodability AND interchange intervention), with planted
NONE/PASSIVE/FUNCTIONAL/noisy controls that pass 5/5 seeds at v3. This is exactly the instrument other
engines (Aether, Primordial, Ares, Ensorain organisms) lack: it would detect a real memory circuit if
one arose and reject passive traces. Its recorded weakness is power for weak history (S1 PREREG:70).
(b) The methodological stack: definition-rung-first gating, LOFO, coordinate-preserving adversary,
graveyard with killed_by, family-leakage-as-a-number (autopsy L1-L7). These should be imported as fleet
standards. The world graph, miner and sealing apparatus should not be scaled.

### Evolutionary Roadmap
Not a roadmap for Cosmos-as-substrate (there is none); a roadmap for the salvaged parts.
1. Extract the certificate into a standalone instrument package (System adapter + P1/P2 + calib) with
   no Cosmos imports; add an interchange-intervention generalization (causal abstraction / distributed
   alignment search style: swap a SUBSPACE, not the full state) so it localizes WHERE a variable lives,
   not only THAT it lives. Formalism: causal abstraction (interchange interventions over a high-level
   causal model), with P1 as conditional mutual information I(cue; S | O).
2. Extend the certificate from 1 variable to a 2-variable composition test: a task with two cues and a
   query that asks for f(cue1, cue2) (e.g. XOR or "cue1 if cue2 is red"). FUNCTIONAL for each cue plus
   an interchange test that the output depends on the PAIR (swap cue1 alone flips output only when the
   high-level model says it should). This is the minimal "reasoning circuit" certificate.
3. If Cosmos continues as a world engine, the world must change before the miner: add a demand
   lattice (number of cues, query rule depth, number of asks) so that a family of worlds exists where
   a latch is NOT optimal; then measure the phase boundary in demand depth, not maintenance price.
   Replace author-declared coordinates with MDL-measured coordinates (description length of the minimal
   predictor of the label from native observations) so the law cannot be written in the author's terms.
4. Multi-agent: none warranted until the world rewards composition.

THE ONE DECISIVE EXPERIMENT: apply the extracted P1/P2 certificate, unchanged, to the "memory" or
"circuit" claims of at least three OTHER fleet engines (an Aether native circuit, a Primordial/tensor
organism, an Ensorain bounded organism) on the C3 delayed-match task with k in {2, 6, 12}.
Kill criterion for the salvage claim: if the certificate either (i) fails its own planted v3 gate again
on a fresh seed block (any planted system misclassified in >= 1 of 5 seeds), or (ii) cannot separate a
planted PASSIVE trace from a FUNCTIONAL register at the power available in those engines (n episodes
they can afford), then it is not a usable fleet instrument and Cosmos is DEAD_END in full.

## 5. What would change this verdict

- Upward (to VIABLE_SEED): a C4 campaign (or any Cosmos run) in which a candidate law over measured
  (not declared) coordinates beats the shortcut on S0-A by >= 0.10 BA with every family condition met,
  on a foreign-authored family (Theseus sediment) and then on D2. That would make Cosmos a working
  instrument for laws of physical memory, still not a reasoning substrate.
- Downward (to DEAD_END): the decisive experiment's kill criterion; or evidence that the P1/P2
  certificate's PASS depends on the specific planted systems (e.g. fails on a re-encoded readout basis,
  autopsy L7).
- Audit falsifier: if a Cosmos world exists where a non-latch policy (anything requiring more than one
  register or a conditional rule) strictly outperforms SEL, my "task-poverty wall" is wrong. I did not
  read the holdout physics bodies or C4 sediment dynamics beyond headers; the claim rests on the
  contract (contract.py:22-25) and c3/task.py:1-12, which bind all families.
- Independence caveat: auditor and engine author are the same model family; the seat's own downgrades
  were used heavily here and an independent reviewer should check them against the raw stores.
