# Dossier: tyche (Dark Residual / Dark Ecology; evolved perceptual lenses)

Auditor: Hestia audit worker (G8b), 2026-10-06. Read-only. Rubric:
roles/Hestia/audit/2026-10-06/AUDIT_PLAN.md s2-s4.

VERDICT: SALVAGE_COMPONENT -- the lens-evolution loop is a GP-over-a-27-op-DSL feature search whose "senses" are completed by a depth-4 decision tree and which empirically stalls at interaction order 3 (0 order-3 solves across v0, v1, v2), but its measurement stack (paired marginal-gain ruler with TSD/PRF twins, causality audit with a LEAD cheat control, subset-MI interaction-order certificates, natural-history tracer) is the best-built reasoning-circuit detector in this group and should be carried forward.

## 0. Identity

- Paths: tyche/ (755 tracked files; 47 are code/tests/scripts, the rest
  are committed run rows: runs/v2_blockR 506, runs/v1_2026-09-30 108,
  runs/v2_blockR_ABORTED_memory 66, runs/v0 13 + 9 aborted, residual
  catalogue 7). Seat roles/Tyche/ (42 files).
- Seat: Tyche (instance m2-ebcbbd6b, host M2). Last seat state in
  roles/Tyche/STATUS_REPORT_2026-10-01.md: IN_FLIGHT, v2 Block R DONE,
  Block M NOT STARTED, nothing running. No Block M rows exist on main
  (git ls-files | grep -i blockM: empty).
- Tree read: worktree C:/Prometheus-worktrees/hestia-boot-2026-10-06 at
  3fed30ac9. Last Tyche commits on main: 59f68caf4, 97e57aada,
  4dbbc07d0 (Block R complete).
- READ IN FULL: tyche/lens.py, tyche/organisms.py, tyche/ecology.py,
  tyche/worlds.py; tyche/run_v0.py lines 30-60 and 270-410 (config,
  evolution loop, admission); tyche/audits.py 1-40; tyche/v2/eco_v2.py
  97-140 (synergy screen, coalitions); tyche/v2/run_v2.py config 40-56
  plus grep of selection arms; tyche/v2/worlds_v2.py 1-60; reports
  tyche/runs/v0_2026-09-30/REPORT.md, tyche/runs/v1_2026-09-30/REPORT_v1.md,
  tyche/runs/v2_blockR/REPORT_BLOCK_R.md; roles/Tyche/calibration/LEDGER.md,
  STATUS.md, STATUS_REPORT_2026-10-01.md, WORK_STATE.json; head of the
  charter roles/Tyche/prompts/2026-09-30_charter/; tyche/residuals/README.md;
  head of tyche/runs/v2_certs/CERTIFICATES.json.
- ROWS CHECKED (not just prose): v0 DONE.json (2368 born, 44 admitted),
  GENEALOGY.jsonl 2368 lines, ADMISSIONS.jsonl 210 tests / 44 admitted
  (tab 28, tree 10, lin 6); v1 GENEALOGY line counts per arm (sum 25077);
  v2 Block R GENEALOGY across 36 runs (162973 births); PHASE_DIAGRAM.json
  block_r (adapted counts, hypotheses booleans).
- NOT READ: tyche/v1/eco_v1.py, run_v1.py, trace_precursors.py,
  worlds_v1.py; tyche/v2/history_v2.py, certify.py, report_v2.py;
  report.py; passd_resume.py; tests/*; residuals/*.py; most of run_v2.py
  (coalition_step, reserve internals); prereg documents and amendments;
  review packets; journals; the 122-entry residual catalogue contents;
  per-lens PASS_D audit rows. I did not independently recompute any
  verdict from EVALS rows. Census row in docs/fleet/fleet_state.json not
  opened.

## 1. Mechanism (code, cited)

1.1 Genome. A lens is a straight-line register program
{"ins": [[op, args, param]...], "out": [...]} (lens.py:1-15). 8 virtual
input registers, channel c reads world column c % d (lens.py:38,200).
Each instruction appends one register (lens.py:201-205); outputs are 1..3
registers (KMAX=3, lens.py:39; fused sensors 6, lens.py:217). Max 48
instructions (lens.py:40). 27 ops (lens.py:120-148): 16 unary with small
integer/choice parameters (delay 1-16, wsum 2-24, thresh from a 10-value
list, ewma from 4 values, a 2-4 state binary FSM with a random table,
etc.), 10 binary (add/sub/mul/max/min/gt/eq/xor/hash/wcorr), 1 ternary
(where). Every op is causal by construction; non-finite values are
clamped (lens.py:204-205). No loops, no memory beyond the fixed-window
ops, accmod/ewma accumulators and the tiny FSM; no learned weights inside
a lens.

1.2 Variation. Nine mutations (point, replace, insert, delete, rewire,
out, temporal-wrap, recur-wrap, cone duplication; lens.py:296-425,
493-497), 1-2 per child (lens.py:501-510), plus graft = append a donor's
output cone and optionally bind it with a random binary op
(lens.py:428-455). fuse (lens.py:458-472) concatenates two lenses'
outputs; compose (lens.py:475-490) pipes one lens into another. Random
initial genomes have 1-4 instructions (lens.py:260) with a 0.6 bias to
read recent registers (lens.py:279).

1.3 Who acts on the lens output. A lens never predicts. Three fixed
"organisms" fit on the train split (organisms.py:38-74): ridge
one-vs-rest linear; sklearn DecisionTreeClassifier(max_depth=4,
min_samples_leaf=20) (organisms.py:49); and a lookup table over
median-binarised features truncated to the first 10 features in ecology
order (organisms.py:52-73, ecology.py:107,145-146). Rulers: predict Y[t]
(R0) or Y[t+2] (R2) (organisms.py:28).

1.4 Value. MarginalLensValue = per-point accuracy of organism on
[lens Z | admitted ecology | raw X] minus accuracy without Z, paired on
the same val points, reported as (mean, z, n) (ecology.py:142-198).
Cases are (world x ruler x organism x scope); scopes all/err/dis
(ecology.py:165-169). Selection: elites (best per world x ruler,
run_v0.py:290-300), a 14-slot "dark reserve" (age-protected, then 2/3
behaviour-signature novelty, 1/3 random; run_v0.py:305-321), offspring by
epsilon-lexicase over the case matrix (ecology.py:277-292,
run_v0.py:323-336). Admission to the ecology: best val gain >= 0.02, then
a conf-split test with z >= 4 and gain >= 0.01, at most 1 per world per
epoch, cap 48 (run_v0.py:35-51,369-400). v0 budget: N=96, 4 epochs x 10
generations (run_v0.py:39-41).

1.5 v2 additions (eco_v2.py, run_v2.py config). Three harshness arms
(STRICT: parents must hold a case with gain > 0 and z >= 2; LEX: lexicase
only; RES: lexicase + 48-slot utility-free reserve, run_v2.py:4-8,47).
Coalitions: an organism-free mutual-information synergy screen of 300
pairs and 300 triples of lenses per step (eco_v2.py:104-121,
run_v2.py:49), then organism evaluation of the best 20 pairs / 10 triples
where the organism sees the concatenated member outputs
(eco_v2.py:124-134). Worlds are built as hidden precursors P_i = f_i(X)
from the same primitive vocabulary (delay, window majority, accumulator
mod m, window parity) plus a combiner (worlds_v2.py:1-23,46-60).

1.6 Instruments. causality_audit replaces future inputs at 5 cut points
and demands bit-identical past outputs (audits.py:25-39); a LEAD op that
reads the future exists only for the cheat control (lens.py:152-153,
187-192). TSD twins draw Y from an independent hidden copy of X with
identical marginals (worlds.py:136-139); PRF worlds use a keyed SHA-256
bit of a 24-step window (worlds.py:95-102). v2 certificates
(runs/v2_certs/CERTIFICATES.json) give subset mutual information of the
hidden precursors, i.e. an empirical interaction order per world (e.g.
D3 order-2: each single precursor 0.0003 bits, the pair 0.99999 bits).

DOCUMENTED vs CODE. README (tyche/README.md) says lenses are "kept for
measured marginal consequence"; the code agrees for admission
(run_v0.py:390) but NOT for survival: v1 F1 and v2 histories show
survival is dominated by noise-level lexicase wins (see s2), so
"consequence" gates the ecology, not the population. The charter speaks
of evolving "reasoning organs"; no code path builds anything beyond a
feature extractor feeding a fixed sklearn-grade classifier.

## 2. Evidence (tiered)

OBSERVED (rows on main, counts checked by me):
- v0 (runs/v0_2026-09-30): 2368 lenses born over 40 generations
  (DONE.json, GENEALOGY.jsonl), 210 admission tests, 44 admitted, tab
  organism 28 of 44 (ADMISSIONS.jsonl). Report verdicts: H5 instrument
  PASS (LEAD cheat z=54.9 caught; 44/44 causal), H2 false gradients PASS
  (0 replicated null-beating gains on 8 negative worlds), H1/H6
  UNREACHABLE_BY_DESIGN (3 of 6 planted controls void: random 1-4 op
  lenses already had test gain >= 0.03), H3 FAIL and H4 FAIL as
  instrument defects.
- v1 (runs/v1_2026-09-30): 6 runs, 25077 births in total (GENEALOGY line
  sums). GATE 6 FAIL. Z-world cells solved at equal budget: V0 3, DENR 2,
  DE 1 of 10 each (REPORT_v1.md table). Z3 (3-way parity) and Z5 (xor of
  windowed majorities) solved by no arm in either seed. One fused pair of
  individually useless lenses replicated at +0.075 (below the 0.10 bar).
- v2 Block R (runs/v2_blockR): 36 runs, 162973 births, 50 generations
  each, unannounced switch to a zero-marginal law at generation 20.
  PHASE_DIAGRAM.json: RH1-RH4 all false, RH5 (0 order-3 adaptations)
  held; adapted cells counted by the clock: 1 of 72 (report says 2 of 72
  counting one coalition the clock missed). Stored "ALL precursors"
  fraction at the switch: <= 0.0006 by arm, max 0.007 in any run.
- Certificates (runs/v2_certs/CERTIFICATES.json): per-world subset MI.

CLAIMED (prose in reports, consistent with the rows I sampled but not
recomputed by me): 92 natural histories with 62 coalitions and 63
exaptations; persistence causes (noise-level parent choice 395,
significant-elsewhere 280, drift 120, reserve 132 events); the one clean
"preserved-useless-then-fused" RES assembly (+0.496); 28 opaque
successful lenses in v0 nobody has interpreted.

DESIGNED (not run): v2 Block M (static pressure map, ~58 runs); the
residual-catalogue attack (122 residuals from 30 seats, 67 with raw rows;
explicitly "untouched until the calibration lane proves the machinery",
STATUS.md). The charter's actual target -- dark residuals of real
Prometheus experiments -- has had ZERO lens runs.

The seat's own calibration ledger (roles/Tyche/calibration/LEDGER.md) has
14 rows of wrong calls, including every substantive prediction of v0, v1
and v2 Block R. This is honest bookkeeping and makes the evidence base
unusually trustworthy as a negative record.

## 3. Matrix

### 3a Combinatorial explosion and reachability

Program space (scratchpad tyche_space.py; per instruction at register
count n: 66433*n unary-with-params + 36*n^2 binary + n^3 ternary; the
FSM tables are 65 536 of the 66 433 unary instances):

    instructions L     log10 #programs     (excluding FSM tables)
    1                   5.7                  3.6
    3                  17.3                 11.1
    5                  29.1                 18.9
    7                  41.0                 27.0
    16                 96.0                 66.1
    48 (MAXLEN)       301.6                228.3

Explored: v0 2.4e3, v1 2.5e4, v2 Block R 1.6e5 lens births (all
campaigns ~1.9e5 ~ 10^5.3). Even at L=3 that is 10^-6 to 10^-12 of
the space; the raw space is not the issue -- reachability of the
right FEATURE TUPLE is.

The decisive quantity is interaction order k. The planted laws present
k hidden delayed bits whose subsets of size < k carry zero information
(certificate D3: single precursor 0.0003 bits, pair 1.0 bit). The
selection signal is therefore flat until all k precursors are presented
jointly. With 8 virtual channels x 16 delays = 128 one-op delay features,
the density of a specific k-tuple among random k-output lenses is about
128^-k:

    k=2  6.1e-5   x 2.5e4 births (v1)  ~ 1.5 expected blind hits
    k=3  4.8e-7   x 2.5e4              ~ 0.012
    k=4  3.7e-9   x 2.5e4              ~ 9e-5

This arithmetic matches every observed outcome: xor2 solved in 3-6 of 10
cells, parity-3 never (v0 P7, v1 Z3, v2 RH5: 0 of 18), parity-4 never
attempted to success. The exact 3-instruction xor2 program under the
random-genome sampler has probability ~7e-11 (1 in 1.4e10); xor2 was
reached anyway only because (a) a depth-4 tree can do the xor if the two
delays are merely PRESENTED as separate outputs, and (b) "soft
precursors" (window sums overlapping a delay, v1 F2) give graded
footholds. Both reduce the needle; neither scales with k.

Coalition search does not rescue order 3: v2 screens 300 triples per
step from a living pool of ~96 + 48 reserve lenses, C(144,3) = 487 344
triples, so ~6e-4 of triples per step; and the stored fraction of
lenses carrying ALL precursors of the next law is <= 0.0006
(REPORT_BLOCK_R.md). The reachability desert begins at k=3 and is
exponential in k with base ~128 (channels x lags).

Measured hit rates: v0 planted controls 2 of 3 valid solved; v1 Z cells
6 of 30 (V0+DE+DENR, both seeds); v2 regime adaptations 1-2 of 72;
order-3 targets 0 of all attempts across v0/v1/v2.

### 3b Cosplay vs foundation

What gets called a "sense" or "reasoning organ" is: (lens) a short
fixed-vocabulary feature transform -- typically 1-16 effective
instructions (v0 report: effective lengths 1-16) -- that presents a few
delayed/windowed channels; plus (organism) a depth-4 sklearn decision
tree or a 10-feature lookup table that performs the actual combination.
In the xor/parity worlds the logical work (xor) is done by the tree or
the table, not by the lens; coalitions (fuse) are literally column
concatenation (lens.py:458-472, eco_v2.py:131).

The search is genetic programming over a hand-picked 27-op DSL whose ops
are the same primitives the worlds are built from (worlds.py:57-113,
worlds_v2.py:46-60: delay, window majority, cumulative mod, gates).
Success on planted worlds is grammar-world alignment, not discovery. The
"dark reserve" and novelty are standard GP diversity maintenance; the
seat's own trace shows noise-level epsilon-lexicase does most of the
preservation (v1 F1, v2 histories: 395 noise-level vs 132 reserve
events).

Ceiling, stated concretely: (1) interaction order k <= 2 is the reachable
class (above); (2) a lens cannot hold state beyond its fixed windows,
accumulators and a <= 4-state FSM, so any law needing unbounded or
learned memory is outside the grammar; (3) the tree organism represents
parity of at most 4 presented bits (depth 4), lin represents no parity;
(4) KMAX = 3 outputs (6 fused) caps how many precursors one sense can
present. No mechanism abstracts a discovered sense into a new primitive
op (no library learning), so nothing compounds across campaigns.

Verdict on this axis: COSPLAY as a reasoning substrate; FOUNDATION-grade
as an instrument. The rulers did their job: they caught the cheat, held
0 false gradients on 8+ negative worlds, and exposed two of the seat's
own instrument defects (H3 organism decorrelation, H4 attention-budget
manufactured residuals: "the observer's architecture created a dark
residual and evolution solved the residual it created", v0 REPORT.md F2).

### 3c Substrate bottlenecks

- Representation: fixed-width straight-line DAG, no loops, no function
  definition, no learned parameters, 3 outputs. Compositionality exists
  syntactically (graft/compose) but credit does not flow through it.
- State/memory: at most a 4-state FSM per instruction; worlds T=12100
  steps but lenses see a few-step window.
- Credit assignment: one scalar paired accuracy difference per case;
  zero gradient for any proper subset of a k>=2 interaction. No
  intermediate credit (no MI-of-subset reward, no curriculum) in v0/v1;
  v2's MI screen is the first step and is applied only at coalition
  level and sparsely.
- Evaluation cost: every lens costs 3 organisms x 2 rulers x worlds
  model fits; v0 per-generation cost rose 2 s -> 18 s with ecology
  growth (REPORT.md S6); the v0 compute estimate was off by >13x
  (LEDGER row 1); Block R hit a harness memory stop (~15 GB). Throughput
  is ~10^4-10^5 births per campaign -- three orders below what k=3 needs
  blind.
- Observer coupling: organism input order depended on ecology order and
  manufactured residuals (v0 F2) -- fixed in v1, but it shows the
  instrument, not the lens, can be the thing that is "learning".
- I/O: worlds are synthetic binary/Gaussian streams with d=6; the real
  residual catalogue (heterogeneous seat rows) has no adapter.

## 4. Deliverable sections

Discovery Approach. Tyche treats "noise" as structure no current observer
can exploit, and evolves executable causal lenses (register programs
over time series) that are admitted to a shared ecology only if a weak
organism predicts consequences measurably better with them than
without, against matched random nulls, independent-copy twins and keyed
PRF worlds. It studies whether ecologies preserve useless precursors
(dark reserves) that later fuse into new senses.

The Brick Walls.
1. Interaction-order wall: zero-marginal structure of order k is a
   needle of density ~128^-k; k=3 needs ~2e6 blind presentations vs
   ~1e4-1e5 births per campaign; order-3 hit rate is 0 across v0, v1
   and 18 Block R cells.
2. Regime-change wall: unannounced switch to a new zero-marginal law was
   adapted in 1-2 of 72 cells within 30 generations; complete precursor
   sets stored at the switch <= 0.0006 of living lenses. "Latent option
   value" is empirically ~0.
3. The organism does the reasoning: the combiner (xor, parity) is
   computed by a depth-4 tree / 10-feature table; lenses are feature
   selectors over a DSL that mirrors the world generator. Nothing in the
   loop invents an operator outside the 27 or reuses a found sense as a
   new primitive.
4. Compute wall at modest scale: >13x compute misestimate, 2 s -> 18 s
   per generation from ecology growth, memory stop at ~15 GB for 36
   small runs.
5. Charter target untouched: 0 runs on the 122 catalogued real
   residuals.

Seed Viability. As a cognitive substrate: DEAD_END as built -- it is
classic GP feature construction with a lexicase/novelty population and
the known GP failure on parity-type deceptive problems (the field's
standard benchmark for exactly this wall). The SALVAGE components are
the instruments: (a) the paired marginal-gain ruler with TSD twins and
PRF negatives (0 false gradients); (b) the causality audit plus LEAD
cheat control; (c) the subset-MI interaction-order certificate per world;
(d) the natural-history tracer that attributes persistence to
noise/significance/drift/reserve. Together these are a ready-made
"would we detect a real reasoning circuit" harness for other engines
(Aether, primordial, Ananke): a claimed circuit must beat its TSD twin,
pass causality, and its interaction order must be certified.

Evolutionary Roadmap.
1. Port the instrument stack out of tyche into a shared ruler package
   (marginal-gain vs ecology, twin/PRF negatives, causality audit,
   subset-MI certificate, persistence tracer) and run it on another
   engine's claimed circuits first; that is the highest-value use.
2. Replace flat accuracy credit with interaction-aware credit: reward
   lenses by conditional / synergistic mutual information
   I(Z; Y | ecology) and partial-information-decomposition synergy over
   candidate pairs and triples, so precursors of an order-k law receive
   credit only jointly but are searched as tuples (beam over tuples with
   MI screens), not as individuals waiting for chance co-occurrence.
3. Library learning: after admission, compress the sense into a new
   named op (DreamCoder-style abstraction with an MDL prior), so order-k
   structure found once becomes an order-1 primitive next time; measure
   compounding as description length of later solutions.
4. Move the combiner into the lens: drop the depth-4 tree as the
   reasoning site; organisms become fixed linear readouts, so any
   nonlinear combination must be constructed in the lens graph. Only then
   is a found "sense" a circuit rather than a feature for sklearn.
5. Typed program representation (typed lambda calculus or a typed
   dataflow graph with loops/recursion) to break the 3-output,
   48-instruction straight-line cap and allow learned state.
6. Multi-agent: the RES/LEX/STRICT ecology is already a population of
   observers; add explicit trade of output registers between lineages
   (market for features priced by synergy) rather than random fuse.

THE ONE decisive experiment. Parity-k ladder with interaction-aware
credit vs current credit, equal births. Worlds: v2 D3 (k=2), D4a (k=3),
D4c (k=4), plus their TSD twins and PRF. Arms: current LEX; LEX +
tuple-MI beam (pairs/triples scored by synergy, no organism); LEX +
tuple-MI beam + library learning. 10 seeds each, 2e5 births per arm per
world, organism restricted to linear readout so the lens must build the
xor. Kill criterion: if no arm solves k=3 (replicated test gain >= 0.10,
beats twin and 32-lens null) in >= 5/10 seeds at 2e5 births, and solve
rate does not improve by >= 10x births-to-solve over LEX at k=2, retire
lens evolution as a discovery mechanism and keep only the instrument
stack. Pass criterion: k=4 solved in >= 3/10 seeds with births-to-solve
growing sub-exponentially in k (fit log births vs k; slope well below
log10(128) = 2.1 per order).

## 5. What would change this verdict

- Upward to VIABLE_SEED: a committed run showing an order-3 or order-4
  zero-marginal law solved with a linear-readout organism (so the lens,
  not the tree, computes the combination), replicated on fresh seeds and
  beating its TSD twin; or a lens admitted on a real catalogued residual
  that replicates and is later confirmed by the owning seat.
- Downward to DEAD_END (instruments included): evidence that the
  marginal-gain ruler admits false positives on another engine's null
  data, or that the subset-MI certificate misorders interaction level on
  worlds with continuous / non-binary precursors.
- Audit-side falsifier: if the v1/v2 run code (not read here) shows
  that coalitions or organisms receive information beyond the lens
  outputs and ecology (a leak), the "lens did not do the work" reading
  must be re-examined in both directions; and if Block M rows on another
  branch show order-3 solves, s3a's reachability numbers are wrong.
