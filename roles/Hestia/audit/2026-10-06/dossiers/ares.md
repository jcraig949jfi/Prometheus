# Hestia audit 1 -- dossier: ares (pressure-engineering sandbox, graph organism)

VERDICT: SALVAGE_COMPONENT -- the organism is a 17-slot recurrent arithmetic
graph whose entire evolved "mechanism" is a one-bit latch (in 2/10 fresh W4
champions literally one output self-loop and zero hidden nodes), but the
carrier-attribution instruments, the present/absent/shuffled control
discipline and the measured "viable-region width decides what evolution
uses" observation are worth carrying into a substrate that can compose.

Auditor: Hestia worker (G5b), 2026-10-06. Read-only. Rubric: AUDIT_PLAN s2-4.

## 0. Identity

- Paths: ares/ (1055 tracked files: 23 top-level files, 2 tests, 1 fossil
  dir, 1027 run receipts under ares/runs/sweep_c0|c1|c2), roles/Ares/
  (30 files).
- Seat: Ares (M2). State per roles/Ares/STATUS.md: PARKED after cycle 2,
  CONTINUE_RECOMMENDED by the operator's gate rule, awaiting decision.
  Last commit touching ares/ or roles/Ares/: 3f68be2b9 (2026-09-25).
- Worktree read: C:/Prometheus-worktrees/hestia-boot-2026-10-06 at
  3fed30ac9.
- Read in full: ares/substrate.py, ares/worlds.py, ares/search.py,
  ares/carriers.py lines 1-220, ares/tests/test_ares.py lines 90-110,
  ares/develop.py header (1-40), ARES_FIRST_REPORT.md,
  ARES_CYCLE1_REPORT.md, ARES_CYCLE2_REPORT.md, roles/Ares/calibration/
  LEDGER.md, STATUS.md, RESUME.md (s1-9), charter verbatim, cycle-1 and
  cycle-2 operator directives verbatim.
- Rows inspected directly: ares/runs/sweep_c2/gates.txt, basin.json,
  recheck.json, c1_all_s201..s210_dissect.json (carrier inventories);
  ares/runs/sweep_c1/disposition.json (head); fossil REPLAY.txt; run-JSON
  headers of all c0/c1/c2 GA runs (P, G, eps) for evaluation counts.
- NOT read: ares/cycle2.py and ares/validate.py bodies (only function
  outlines), develop.py body (W10 expression), baselines.py,
  calibrate_w12.py, supp_*.py, verdict.py body, carriers.py 221-343
  (transplant/swap), ARES_PRESSURE_NOTES.md, PRESSURE_CATALOG.json,
  DESIGN_C0/C1/C2.md, journals, review packets, TODO/BACKLOG, the W8/W9/
  W10/W6 run JSONs individually, any sweep_c0/c1 dissect rows. Claims that
  rest only on those are tiered CLAIMED below.

## 1. Mechanism (what the code does)

Organism (ares/substrate.py):
- Fixed slot layout: 6 input + n_hidden (default 8) + 3 output = 17 nodes
  (substrate.py:18-19, 61-63). Action = argmax over 3 output values
  (substrate.py:419-420). Each node: one of 9 arithmetic ops (ADD MUL MAX
  MIN THRESH GATE TANH DIFF CONST, substrate.py:20, semantics 423-435), a
  bias, a "keep" leak coefficient, two dense weighted input ports W1, W2
  (17x17 each) and a Hebbian rate matrix R on W1 (substrate.py:87-92).
- Execution: per world step, `ticks` (default 2) synchronous updates;
  inputs clamped each tick; new = keep*v + (1-keep)*f(op, W1 v, W2 v, b),
  clipped to +-8 (substrate.py:402-420). Node values persist across world
  steps unless reset_each_step (substrate.py:405-406). Plastic update
  dW1 = R * v_i v_j each tick, clipped (substrate.py:416-418).
- So there are exactly three cross-step channels, all hand-provided:
  (a) recurrent activation through any directed cycle, (b) the keep leak,
  (c) Hebbian W1. carriers.py:1-15 enumerates them as RECUR/KEEP/PLAST.
  A fourth, unacknowledged channel exists in code: a feed-forward chain
  deeper than `ticks` acts as a pipeline delay line (a depth-3 node reads
  depth-2 values from the previous tick), giving a few steps of fixed
  delay without any cycle. With 8 hidden slots it cannot span W4's 37-step
  hold, so it is harmless here, but it is a carrier the "no recurrence"
  arm does not remove (only reset_each_step does, substrate.py:405).
- Keep is clipped to [0, 0.98] at mutation (substrate.py:300) -- an
  experimenter-chosen ceiling that later becomes the "knife edge".

Search (ares/search.py):
- Plain GA: P=128, elitism 12.5%, size-3 tournament from the top half,
  1+Poisson(1) mutations from a 10-operator menu with fixed weights
  (search.py:276-289; substrate.py:200-238). No crossover in the main
  loop (splice_subgraph exists, substrate.py:336-378, used only for
  transplant protocols, search.py:179-194). Fitness = mean episode reward
  over 4 common-random-number episodes per generation (search.py:236-237).
- Defect D1 (seat-found): the reported final champion is argmax over the
  final population ON the held-out seeds (search.py:292-294), a
  max-of-128 statistic; still unfixed in code (RESUME s5 D1).

Worlds (ares/worlds.py): 16 tiny batched worlds, each with
present/absent/shuffled modes. The one that carries every result is W4
(worlds.py:170-197): regime bit r in {0,1} shown on ch1 for 3 steps,
then 37 steps of noise; reward +1 for action r+1 every step, T=40, so
cap 40.0. W13-W16 are W4 variants (longer delay, state noise injected
by the runtime at search.py:84-85, reset events at search.py:86-87,
variable cue time).

Instruments: carriers.py:93-134 cuts self-loops / all recurrent edges /
keep / plasticity / everything, per SCC and per recurrent edge, and
classifies by which cut collapses fitness to <= 25% of gain
(carriers.py:126-153). carriers.py:156-187 measures P(one mutation
creates a carrier). This is the most careful piece of code in the engine.

DOCUMENTED vs CODE:
- "Nothing here is named after a cognitive function; the ops are
  arithmetic" (substrate.py:1-7): true of names, but the three memory
  channels ARE designed in; the organism cannot invent a fourth kind of
  state, only choose among provided ones. The seat's "NEW_CARRIER: 0
  occurrences" (CYCLE2 s2) is therefore guaranteed by construction, not a
  finding about evolution.
- "The optimizer ... carries none of the capability" (search.py:1-4):
  true; the capability is carried by the arithmetic of a single saturating
  node with a self-edge (see 3b).
- test_ares.py:100-102 already states, in cycle 0, that a TANH self-loop
  with weight 3 is "bistable at +-1" while a keep-0.9 leak "decays to
  noise by step ~15". The cycle-2 "why recurrence wins" answer was latent
  in the seat's own cheat control.

## 2. Evidence (tiered)

GA volume, OBSERVED from run JSON headers (P*G*eps summed):
cycle 0 171 runs / 9.2M organism-episodes; cycle 1 120 runs / 7.4M;
cycle 2 180 runs parsed (report says 190) / 11.1M. Total ~27.6M
organism-episodes of 30-80 steps.

OBSERVED (rows on main that I read):
- E1 W4 needs a cross-step carrier: c1_none 0/10 above threshold 8.0,
  clean median 2.30 of cap 40 (recheck.json clean_heldout.c1_none).
- E2 Each carrier alone suffices: only_recur 10/10 (ttt 10 gens),
  only_plast 10/10 (17.5), only_keep 10/10 reported / 9/10 clean (ttt 30;
  clean scores include 2.94 and 21.6) (gates.txt rows 2-4; recheck.json).
- E3 Substitution: c2_no_recur 10/10 at cap, classes PLAST 6 KEEP 2
  REDUNDANT 1 MIXED 1, ttt 20 vs 10 (gates.txt).
- E4 Carrier preference persists under keep subsidy (RECUR 5 REDUNDANT 4
  PLAST 1) and under recurrent-edge jitter (RECUR 7, ttt 5) (gates.txt).
- E5 Basin sweep on HAND-WIRED organisms: keep fitness rises from 4.75 at
  0.5 to 33.75 at 0.98 (the clip); recurrence weight 0.5..6.0 gives
  2.5 -> 40.0 and is flat at 40.0 from 4.0 up (basin.json). Post-hoc.
- E6 Per-pair carrier swap: 59 informative pairs, median recovery 0.019,
  >= 0.5 in 16/59 (recheck.json swap_recheck). gates.txt still prints
  GATE C OPEN with "median_recovery=1.0" -- the uncorrected best-of-9
  figure; the correction lives only in the report and recheck.json.
- E7 D1 bias is real: shuffled W4 clean median 0.0 vs reported 4.22;
  W14 shuffled clean -2.38 vs reported 13.47 (recheck.json
  empirical_floor_from_shuffled). gates.txt row "W14_shuffled above
  10/10" is that artifact.
- E8 Champion anatomy, c1_all seeds 201-210 (dissect rows): s203 has 0
  hidden nodes, 4 edges, one self-loop on an output node; s207 has 0
  hidden nodes and its only load-bearing edge is output self-loop
  15->15; s209's only load-bearing edge is output self-loop 16->16;
  s202 reaches only 20.0 via self-loop 14->14. Four of ten champions
  are carried by a single self-edge.
- E9 Fossil replays bit-exactly (REPLAY.txt: 40.0000 == stored).
- E10 Cycle-1 disposition rows: W4 10/10 at cap, load-bearing-node
  signatures 7 distinct including "(none)" x4 (disposition.json).

CLAIMED (report prose; rows exist but I did not open them):
- W5 26-step delayed token at cap 9/10 needing plasticity AND activation
  in 8/10; W12 state-dependent risk 9/10; W13 carrier stress 9/10
  (CYCLE1 s2). Usable-carrier creation p=0.0173 (recurrent) vs 0.0000
  (keep) is OBSERVED (recheck.json useful_opportunity); the c3 arm result
  "keep load-bearing 2/10" is CLAIMED (c3_summary not opened).
- Nulls: W3 (no reliable within-lifetime adaptation, post-flip accuracy
  0.00 in 2/3), W7 (reflex, no specialisation), W11 (blind commitment on
  step 1), W8 transplant = random subgraph, W9 Red Queen cycling, W10
  developmental encoding not faster (CYCLE0 s2). 3 seeds each.

DESIGNED (not run): RESUME s6.1 decoupled-leak arm and re-parameterised
keep; s6.2 basin width across all primitives; s6.3 redundancy under W15.

The seat's own ledger (roles/Ares/calibration/LEDGER.md, 13 rows) records
six instrument or prediction failures it caught itself, including a
cycle-1 headline ("plasticity 0/10") that did not replicate (4/10,
LEDGER row 2026-09-23). This is unusually honest and is the main reason
the evidence above can be trusted at the tier given.

## 3. Matrix

### 3a Combinatorial explosion and reachability

Genotype space (scratch calc ares_calc.py): edge slots = 2 ports x 11
non-input targets x 17 sources = 374, so 2^374 ~ 10^112.6 topologies;
times 9^11 ~ 3.1e10 op assignments, times 2^8 alive masks: a discrete
skeleton of ~10^125.5 before any continuous weight, bias, keep or R.
Explored: ~2.8e7 organism-episodes total, a fraction ~10^-118 of the
skeleton.

That fraction is irrelevant, and that is the point: the solution set for
every world that succeeded is DENSE. A W4 solution is any genome
containing one saturating node with self-weight above ~1.5 (bistable
tanh: fixed point 0.86 at w=1.5, 0.96 at w=2, 0.999 at w=4; scratch
calc) wired with the right sign from ch1 to the output argmax. The GA
hits the cap in a median of 10 generations x 128 = ~1,300 genomes. There
is no desert here because there is no depth: the worlds demand at most
1 latched bit (W4, W5, W13-W16) or a threshold on an OBSERVED scalar (W12,
W1, W2).

Where it explodes: the moment a world needs more than one bit or a
composition of conditionals, the record shows failure, not slow success.
W3 (detect a rule reversal from reward feedback and invert) failed in
2/3 seeds; W7 (two regimes, arbitration) produced reflexes; W11 (gather
evidence, then commit) produced commit-at-step-1 (CLAIMED, CYCLE0 s2).
Each of these needs at least two interacting state variables (evidence
accumulator + decision latch, or regime estimate + per-regime policy).
With mutation as the only variation operator and no reuse, the expected
waiting time for k coordinated components that are individually neutral
scales roughly as (1/p)^k for per-mutation probability p; with the
measured usable-carrier creation rate p ~ 0.017 (recheck.json), k=1 is
~60 mutations, k=2 ~3,400, k=3 ~200,000 -- consistent with the 1-bit
worlds solving in ~10 generations and the 2-variable worlds not solving
in 120. The seat's own single-mutation gradient measurement (CYCLE2
s4.2: p(immediate improvement) 0.00 in 4/5 lineages) says the
intermediate steps are neutral, which is exactly the regime where this
power law bites.

Capacity ceiling: 8 hidden slots, 3 actions, 6 inputs (two of them
clock and constant). Even perfectly used, the organism holds at most ~8
latched bits with no addressing; the worlds never asked for more than 1.

### 3b Cosplay vs foundation

What does the work called "memory machinery" / "carrier": a single
nonlinear node with a positive self-weight -- a bistable attractor, i.e.
a 1-bit flip-flop. Evidence E8: four of ten fresh W4 champions are
carried by one self-edge, two of them with zero hidden nodes. The
"structurally diverse, functionally identical" finding (CYCLE1 s0) is
diversity of neutral wiring around that latch, not diversity of
mechanism.

Why recurrence beats keep (the cycle-2 headline): this is the textbook
difference between an attractor and a linear leak, not a new design
rule. My scratch calc for a single keep node fed the raw cue (6 loading
ticks, 74 holding ticks, cue noise sd 0.3): end-of-episode SNR is 0.06
at keep 0.94, 0.85 at 0.98 (the code's clip), and peaks at only ~1.36
near 0.99-0.995 before falling again. A linear leaky integrator cannot
hold one bit cleanly over 37 steps at ANY keep; the evolved keep-only
solutions therefore need an upstream nonlinear filter (GATE/THRESH) to
stop noise loading -- two coordinated parts, hence the slower, long-
tailed ttt (30, tail to 90). A tanh self-loop is bistable for w > 1 and
saturates, so "larger is never worse" (basin.json flat at 40 from w=4).
The seat measured this honestly and labelled it post-hoc; it did not
name it as bistability vs leak, and its proposed decisive arm (RESUME
s6.1, v = keep*v + f) leaves the node linear: rescaling the input term
does not change a linear integrator's SNR, so my prediction is that arm
will NOT make keep competitive unless evolution again adds a nonlinear
filter. The "basin width" rule is real but is the bifurcation structure
of the primitives, which can be computed before running any GA.

Classification: a selection loop over a fixed 10-operator mutation menu
on a 9-op arithmetic graph, choosing among three hand-provided memory
channels. The pressure worlds are genuine and well-controlled; the
"machinery" they elicit is the smallest dynamical-systems object that
solves them. This is not reasoning and the seat never claimed it was
(LEDGER row 2026-09-23 retracts the one overreach). Ceiling, concretely:
reactive policies plus up to a few independent latches; no evidence of
composition, addressing, or reuse of a learned part.

Reuse/compositionality, measured: carrier swap per-pair median recovery
0.019 (E6); cycle-0 W8 transplant equals random subgraph; cycle-1 causal
transplant above random in 1/10 W4, 0/10 elsewhere (CLAIMED, CYCLE1
s3.4). Evolved parts do not travel. That is the single most important
negative for the charter: nothing here behaves like a reusable organ.

### 3c Substrate bottlenecks

- Representation: dense 17x17 weight matrices with absolute slot indices
  (substrate.py:90-92). A subgraph's meaning depends on which absolute
  input/output slots it touches; splice_subgraph re-attaches external
  edges to RANDOM host nodes (substrate.py:365, 377). That alone
  predicts the transplant failures -- there is no interface type.
- State: <= 8 hidden scalars, clipped to +-8 (substrate.py:22, 414).
  No external tape, stack or addressable memory; no way to grow.
- Addressing: none. A node cannot select which other node to read at run
  time except by GATE on a fixed wire.
- Credit assignment: none below the episode. Fitness is total reward
  over 4 episodes; the single-mutation gradient is ~0 at carrier birth
  (CYCLE2 s4.2), so multi-part mechanisms must drift neutrally.
- Compositionality: no module boundary, no duplication-with-divergence
  in practice (duplicate_node exists, substrate.py:322-332, weight 0.5 of
  12.3, but no result attributes anything to it), no crossover in the
  main loop.
- I/O bandwidth: 4 world channels + clock + constant in, argmax over 3
  out. Every world is designed to fit this; harder worlds cannot.
- Time: ticks=2 per step bounds within-step computation depth to 2
  synchronous layers; any deeper DAG silently becomes a delay line (s1).

## 4. Deliverable sections

Discovery Approach. Ares does pressure engineering: it writes tiny
worlds that make some unnamed mechanism advantageous (hidden regime,
delayed revelation, catastrophic tail, dying lineage, ...), evolves
generic arithmetic graphs in them with a deliberately dumb GA, and asks
which pressures changed the KIND of machinery that arose, with
present/absent/shuffled controls, carrier-level ablation and
preregistered predictions. It is a well-run experimental method sitting
on a deliberately minimal substrate.

The Brick Walls.
1. Task depth ceiling: every positive result needs at most 1 latched bit
   or a threshold on an observed scalar; the one-self-edge solution
   (E8, 4/10 champions) shows the "mechanism" has description length of
   a few parameters. Every world needing two interacting state variables
   (W3, W7, W11) failed or reflexed.
2. Neutral-network waiting time: with usable-carrier creation p ~ 0.017
   per mutation and ~0 single-step gradient, coordinated k-part
   mechanisms cost ~(1/p)^k ~ 60^k mutations; k=3 is ~2e5, beyond a 120-
   generation x 128 budget (15,360 genomes per run).
3. No reuse: per-pair carrier transplant median recovery 0.019; random
   re-attachment of external edges (substrate.py:365, 377) guarantees
   context dependence. Without reuse, the cost of the next mechanism
   never falls -- the opposite of what a reasoning substrate needs.
Also: the three memory channels are hand-provided, so "no new carrier
class appeared" (0 occurrences) is structurally guaranteed.

Seed Viability. As a cognitive substrate: no seed; it is a bistable-
latch generator with a ceiling at a handful of independent bits. As a
method and instrument: yes. Salvage (a) carriers.py edge/SCC-aware
carrier ablation and mutational-opportunity measurement (would detect a
real circuit's load-bearing cycle; node-only ablation would not, as the
seat showed); (b) the world harness discipline -- present/absent/
shuffled modes, per-world balance_key seeding (search.py:33-56), the D1/
D2 warnings; (c) the empirical rule "evolution uses the primitive with
the widest viable region, not the best optimum or the most reachable
one", restated as: prefer primitives whose useful behaviour lies in a
bifurcation regime that is open-ended (attractors), and compute that
regime analytically before designing a substrate.

Evolutionary Roadmap (for the salvaged components, not this organism).
1. Re-host the instruments on a substrate that can compose: typed graph
   rewriting or a typed lambda / combinator genome where a subgraph has
   an explicit interface (typed input/output ports), so transplant is
   well-defined and reuse is measurable (fixes 3c representation).
2. Make duplication-with-divergence and module libraries first-class:
   an evolving library of named-by-hash subroutines (DreamCoder-style
   compression / MDL over the population's genomes), with credit
   assigned to library entries by the fitness of their callers.
3. Replace the 1-bit worlds with a graded compositional family: k
   independent hidden cues and a reward that depends on a function of
   them (parity/XOR, ordered recall, "if cue A then use cue B"), with k
   as the dial. This turns "does it compose?" into a curve, not an
   anecdote.
4. Predict primitive usage analytically: for each op, compute its
   fixed-point / bifurcation structure under self-coupling and the
   width of its viable region; test the seat's basin rule as a
   quantitative predictor (RESUME s6.2) on the new substrate.
5. Multi-agent only after reuse exists: coevolution in W9 produced Red
   Queen cycling and no extra machinery (CLAIMED); coupling should be
   reintroduced as library sharing between populations (horizontal
   transfer of typed modules), not as matching pennies.

THE decisive next experiment (cheap, runs on the existing code with one
new world, no substrate change -- that is the point):
  Compositional depth curve. World W4k: k in {1, 2, 3} independent
  regime bits cued at separate early windows; reward in the last 10
  steps for action = parity of the k bits (k=1 is W4). Same GA, same
  substrate (n_hidden 8, ticks 2), 10 fresh seeds per k, budget G=480
  (4x cycle budget), training-selected champions only (D1 fixed),
  shuffled control per k. Measure success rate and time-to-threshold vs
  k, plus carrier-attributed anatomy of any success. Add one arm per k
  that seeds the population with an evolved W4 latch as a pre-wired
  module to test whether reuse cuts the cost.
  Kill criterion: if k=2 reaches threshold in < 5/10 lineages at 4x
  budget, or if median time-to-threshold grows by more than 30x from
  k=1 to k=2 and k=3 is 0/10, the organism is a latch generator with no
  compositional path -- close Ares as a substrate and export only the
  instruments. If k=3 is reached in >= 5/10 with ttt growing at most
  polynomially in k, and the seeded-latch arm is faster, upgrade the
  substrate verdict to VIABLE_SEED and proceed with roadmap items 1-3.

## 5. What would change this verdict

- Upward to VIABLE_SEED: the W4k curve above shows sub-exponential cost
  in k on this substrate, or any carrier-attributed champion whose
  load-bearing structure is two or more interacting SCCs computing a
  function of stored bits (not parallel independent latches), and that
  structure transplants per-pair with median recovery >= 0.5.
- Downward to DEAD_END: if carriers.py-style attribution, ported to
  another engine's organism, fails to localise a known hand-built
  circuit there (positive control), the instrument salvage claim falls
  and nothing here survives.
- Evidence I would need to correct: if the unread W3/W7/W11 rows (sweep_
  c0) show the nulls were budget- or control-artifacts rather than
  failures (the seat found three control defects in cycle 0), brick wall
  1's "two-variable worlds fail" weakens from OBSERVED-by-report to
  untested, and the decisive experiment becomes even more necessary.
- My scratch SNR argument against the RESUME s6.1 arm is analytic on a
  single raw-fed keep node; if that arm makes keep load-bearing in
  >= 5/10 WITHOUT an upstream nonlinear filter in the champions, my
  bistability-vs-leak reading of the basin result is wrong.
