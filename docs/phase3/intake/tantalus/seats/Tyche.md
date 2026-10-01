# Tyche -- seat dossier

- Seat: Tyche
- Crawler: Tantalus (worker)
- Tree SHA: 21a47402a (origin/main)
- Date: 2026-10-01

Summary. Tyche was created on 2026-09-29 on M2 (SPECTREX5) and chartered on
2026-09-30 as "DARK RESIDUAL / DARK ECOLOGY", extending Hecate. In about 28
hours it built tyche/ (lens chemistry, worlds, weak-learner organisms,
ecology, audits, three campaign generations v0/v1/v2, and a provenance-checked
residual catalogue) and ran four preregistered campaigns: v0 (H5 and H2 PASS,
H1/H6 later labelled UNREACHABLE_BY_DESIGN by Harmonia, H3 and H4 FAIL), v1
(GATE 6 FAIL), and v2 Block R (RH1-RH4 FALSE, 2 of 72 cells adapt). In code a
LENS is a small causal feed-forward register program (up to 48 instructions,
27 ops including delay, window sums, mod-accumulators, xor and a 2-4 state
FSM) over a 6-channel binary or Gaussian time series; a lens's VALUE is the
paired accuracy gain it gives a weak classifier (ridge, depth-4 tree, or
median-split lookup table) predicting a hidden integer label Y; a RESIDUAL is,
successively, (v0) the set of time points all organisms get wrong or disagree
on, (v1/v2) the accuracy gap between the ecology and an answer-key "oracle"
lens on calibration worlds, and (catalogue) a quote-verified text record of an
unexplained finding elsewhere in Prometheus. Lenses evolve by mutation,
cross-lineage graft, fusion and (in code, unrun) composition under
epsilon-lexicase over a per-(world, ruler, organism, scope) case vector. The
worlds are toy boolean functions of delayed inputs (xor, parity, count mod 3,
window majority) plus four Hecate alien-lawful finite-state systems, and the
lens chemistry contains the very primitives the planted laws are built from.
The seat's own reading: the leakage guard works and no false gradients appeared;
gradient-following search reaches structure with partial footholds; true
zero-marginal needles (3-way parity, deep-precursor xor) were never reached;
two of its first instruments manufactured residuals.

---------------------------------------------------------------------------

## 1. Identity, charter and pivots

- Creation: operator chat, verbatim at
  roles/Tyche/prompts/2026-09-29_creation/01_OPERATOR_CREATION_verbatim.md;
  creation commit 0b8832dc6 (2026-09-29 22:04 -0400). Instance m2-ebcbbd6b on
  M2 SPECTREX5 (28 logical CPUs, 32 GB, python 3.14.4, numpy 2.4.4, sklearn
  1.8.0, per journal). Name archaeology: no prior seat; only an unused
  alternate name in Artemis's creation. [IMPL/CLAIM]
- Charter: roles/Tyche/prompts/2026-09-30_charter/01_OPERATOR_CHARTER_verbatim.md
  ("You are Tyche, extending Hecate's work ... PROJECT: DARK RESIDUAL / DARK
  ECOLOGY"), committed 01c53f64e before any design. Asks: never call
  residual "noise"; WORLD / LENS / ORGANISM / RULER / INTERPRETER separation;
  MarginalLensValue(L) = performance(ecology + L) - performance(ecology);
  lens genomes from about 40 named primitives; dark ecology reserve;
  experiment organisms; five world classes; positive and impossible
  controls; passes A-J; v0 scale 32 worlds, 64-128 lenses, 3 organism
  types, 20-50 generations. [INTENT]
- Pivots (operator-directed):
  1. v1 directive (roles/Tyche/prompts/2026-09-30_v1_directive/, e6884298c):
     make delayed XOR the canonical dark-ecology positive control; residual
     = capability deficit vs an oracle; two lanes (calibration vs natural
     residuals); do not touch the 122 natural residuals yet. [INTENT]
  2. v2 directive (prompts/2026-09-30_v2_pressure_map/, db985709e):
     "information-maximizing pressure map": vary selection harshness, world
     diversity, coalition depth, needle order, mutation chemistry; regime
     shifts; "latent option value"; causal natural history of each sense.
     [INTENT]
  3. CWO 2026-09-30 (Aporia #1032): residual catalogue as CURRENT item.
     [CLAIM]
- Relationship to Hecate (charter "extend"): Tyche uses
  hecate/alien/systems.py and hecate/alien/data/answer_key.json read-only to
  build HA_* (ALIEN_LAWFUL) and HN_* (MATCHED_NOISE) worlds; it does not run
  Hecate's triplicate programs (Hecate triplicate worlds are backlog
  TYCHE-09). Hecate systems: deterministic maps on <= ~4k enumerable states
  (families tab 5xZ5, graph 6x4, rewrite 6x4, vm, map Z31^2). [IMPL
  tyche/worlds.py:142-176,183-187; hecate/alien/systems.py:1-30]
- Relationship to Theseus: Theseus imports tyche.lens (execute, mutate,
  random_genome) as a dependency and asked Tyche an interface question
  (#1124); no Tyche reply found at this SHA. [IMPL; UNKNOWN reply]
- Oversight: Harmonia ruler audit e72508448
  (roles/Harmonia/audits/RULER_QUALITY_2026-09-30.md) relabelled v0 H1/H6;
  Cyclops #1061 observability audit; Aporia #1096/#1144 VISIBILITY_STALE.
  [CLAIM]
- Current state (STATUS_REPORT_2026-10-01.md, 97e57aada): IN_FLIGHT on v2;
  Block R done, Block M not started, nothing running. Last Tyche commit
  59f68caf4 (2026-10-01 05:06 -0400, committing tyche/scripts/ launchers).
  [IMPL]

## 2. Engine/system inventory

### E1. Tyche lens ecology v0 (tyche/*.py)

- Paths: tyche/lens.py (544 lines), worlds.py (324), organisms.py (82),
  ecology.py (223), audits.py (90), run_v0.py (430), passd_resume.py (110),
  report.py (204); tests tyche/tests/. [IMPL]
- Entrypoint: `python -m tyche.run_v0 --out tyche/runs/v0_2026-09-30
  --workers 16`; Pass D resume via tyche/passd_resume.py. [IMPL]
- Versions: prereg + code 075e5fc21; amendment 1 32fa63544 (BLAS pin);
  amendment 2 e8f9ff4c3 (Pass D resume). [IMPL]
- Data flow: build_worlds (32 specs) -> generate(spec, seed) -> X[T=12100,
  d] and Y[T] -> lens.execute(g, X) -> Z[T, K<=3] -> features [Z,
  ecology lens outputs, raw X] -> organism fit on train split -> per-point
  correctness on val -> paired gain vs base -> case vector -> eps-lexicase
  -> mutation/graft -> admission on conf split -> Pass D on test and fresh
  seeds. [IMPL]
- Persistence: tyche/runs/v0_2026-09-30/{GENEALOGY, FOSSILS, EVALS.gz,
  ADMISSIONS, RESIDUALS, GENERATIONS, PASS_A_BASELINE, PASS_D_AUDITS,
  WORLDS, CONFIG, DONE, REPORT.json, REPORT.md} (5.6 MB);
  v0_2026-09-30_ABORTED/ (unscored, 4.4 MB). [IMPL]
- Scale: 32 worlds (24 selection, 8 held out), N = 96 lenses, 4 epochs x 10
  generations, 2,368 lenses born, 432 cases per lens, 44 admitted, 210
  admission tests; evolution 418 s wall at 16 workers; item <= 15.4
  core-hours (13.0 of it the stopped attempt). [RESULT-UNVERIFIED]

### E2. Tyche v1 (tyche/v1/)

- Paths: worlds_v1.py (153), eco_v1.py (138), run_v1.py (489),
  report_v1.py (143), trace_precursors.py (93); launcher
  tyche/scripts/run_v1_all.sh. Prereg 282f01c45 (roles/Tyche/prereg/
  2026-09-30_v1/). Rows tyche/runs/v1_2026-09-30/ (48 MB). [IMPL]
- Changes vs v0: per-world ecology; tab sees [candidate, raw] only;
  residual = oracle capability deficit; pair evaluation O(L_a(X), L_b(X));
  lens.fuse; R0 only (R2 excluded after a design-time leak); arms V0 / DE
  (48-slot utility-free reserve, 60 pair evaluations per world per
  generation, fused admission, delayed credit) / DENR (pairs among
  utility-selected lenses, no reserve); equal 6,000 evaluation units per
  world; seeds 1, 2. [IMPL eco_v1.py docstring; CLAIM for arm details]
- Scale: 6 runs, 36-83 generations, about 2 core-hours. [RESULT-UNVERIFIED]

### E3. Tyche v2 pressure map (tyche/v2/)

- Paths: worlds_v2.py (349), certify.py (122), eco_v2.py (186), run_v2.py
  (489), history_v2.py (187), report_v2.py (129); design
  roles/Tyche/design/V2_PRESSURE_MAP_DESIGN.md (ad5e912e6); prereg Block R
  e9fd76349 + amendment 1 7fc0cf97a; launcher tyche/scripts/run_blockR.sh;
  rows tyche/runs/v2_blockR/ (36 run directories, about 205 MB uncompressed,
  committed against CWO-C s10.4 per seat). [IMPL]
- New: world classes D1-D7 with hidden precursor variables and exact
  subset-MI certificates; STRICT / LEX / RES selection; organism-free
  coalition screen by train-split joint MI and synergy; functional
  precursor carriers via MI(lens outputs; hidden precursor) (tracer only);
  regime worlds that switch law at an unannounced generation; option-value
  clock; natural-history tracer; chemistry flag MUT | GRAFT | LOL (LOL adds
  lens.compose = b(a(X))). Block M (the static multi-axis map that would
  exercise coalition depth and LOL chemistry) is NOT run at this SHA.
  [IMPL run_v2.py:12,46,383-384; STATUS_REPORT]

### E4. Residual catalogue (tyche/residuals/)

- Paths: catalogue.py (121; schema + validate), build.py, import_artemis.py,
  enrich.py, cluster.py; data artemis_import.jsonl, drafted_survey.jsonl
  (from tyche/scripts/gen_survey.py, written by a drafting agent),
  v0_1/{CATALOGUE_v0.jsonl, CLUSTERS_v0_1.json, REJECTED_v0.jsonl,
  SUMMARY_v0.json}. Commits 3c7b9783e (v0: 122 admitted from 30 seats, 10
  rejected), 8cb8d804a (v0.1: 67/122 with raw rows, 31 framing notes, 17
  behaviour niches). [IMPL]
- Mechanism: an entry is admitted only if every source quote is an exact
  substring of `git show sha:path` and raw_rows exist at the ref.
  behaviour_tags are "provisional, model-assigned ... NOT evidence".
  [IMPL catalogue.py:1-35]
- Status: "natural residuals untouched" -- no lens has been evolved against
  any catalogue entry. [CLAIM STATUS.md]

## 3. Code architecture and dataflow (as read)

LENS (tyche/lens.py). Genome {"ins": [[op, [arg regs], param], ...], "out":
[reg, ...]}. Registers 0..7 are virtual input channels (channel c reads
world column c % d, so every lens runs on every world); instruction i
writes register 8 + i; arguments may only reference earlier registers, so a
genome is a DAG (feed-forward), with recurrence only inside the ops fsm
(2-4 state table over x > 0.5), accmod (cumsum mod m), ewma, wsum.
Outputs 1..KMAX=3 registers (KFUSED 6 for fused sensors). MAXLEN 48. 27 ops:
delay, diff, wsum, wmax, wmin, rank, accmod, fold, thresh, ewma, norm,
sample, fsm, sign, abs, neg, add, sub, mul, max2, min2, gt, eq, xor, hash,
wcorr, where. Mutations: point, replace, insert, delete, rewire, out,
temporal (wrap with delay/diff/wsum/sample), recur (wrap with
fsm/accmod/ewma), dup; graft appends a donor output's cone and optionally
binds it with a random binary op; fuse concatenates two lenses' outputs;
compose rewires b's inputs to a's outputs. Introns are kept. Behaviour
signature = rank-normalised outputs on a fixed probe input at 64 times
(diversity only). [IMPL lens.py:38-544]

WORLD (tyche/worlds.py). A spec plus generate(spec, seed) -> X (T x d),
Y (T,) int. T = 12100; splits train 100-3100, val 3100-6100, conf
6100-9100, test 9100-12100. Planted laws use only delayed inputs (xor2,
par3, cmod, wmaj, gate, psign, fsm); tsd twins draw Y from an independent
hidden copy of the inputs; prf = keyed SHA-256 bit of a 24-step window;
known = Y a function of current X; hec_alien / hec_null = Hecate
deterministic systems with restart every 25 steps, one component hidden, Y
= next value of the highest-entropy observed component; adv = decoy (an
observed channel agrees with the xor target 65%), noisymaj, alias
(period-11 phase), sparse. RNG seeded by (seed, spec uid). [IMPL
worlds.py:1-324]

ORGANISM and RULER (tyche/organisms.py). lin = one-vs-rest ridge on
standardised features; tree = sklearn depth-4, min 20 per leaf; tab =
lookup table on median-binarised features (<= 60 columns; majority per
cell). Rulers: R0 predicts Y[t] from Z[t]; R2 predicts Y[t+2]. Value =
accuracy. [IMPL]

ECOLOGY (tyche/ecology.py). Gain = paired mean of per-point correctness
difference (with vs without the candidate), z = mean / SE; scopes all /
err (every organism wrong under current ecology) / dis (organisms
disagree); eps-lexicase with MAD epsilon; novelty = mean L1 distance to k=5
nearest signatures. v0 tab feature budget 10 columns taken newest-lens
first (the defect behind F2). [IMPL ecology.py:24-223]

AUDITS (tyche/audits.py). causality_audit replaces the future at 5 cuts and
requires bit-identical outputs up to each cut; cheat_control builds a
world where Y[t] = X[t+1] and a lens using the forbidden LEAD op, which
must show z >= 4 and fail causality; sensor_class LOCAL / FAMILY /
TRANSFER / GENERAL from significant test gains, with significance on
tsd/prf counted as FALSE_GRADIENT. [IMPL]

Code vs docs: the charter's list of 40 primitives maps to 27 ops; "permute,
mask, unfold, partition, bind/unbind, lift, contract/expand, rotate,
rewrite, couple/decouple, encode/decode, interleave, scatter/gather,
convolve" are absent or approximated (lens.py docstring lists the mapping;
"the rest are backlog"). Representational diversity (graphs, event streams)
is backlog TYCHE-10; all outputs are T x K float arrays. Experiment
organisms (TYCHE-06), intervention rulers (TYCHE-07), lens-of-lens (Pass G)
in a run, world mutation (Pass E), cross-observer organisms (TYCHE-13), LLM
as organism (TYCHE-14), Visual Cortex (TYCHE-16) are not built. [IMPL
lens.py:17-22; BACKLOG]

## 4. Claimed computational primitive vs actual mechanism

- Label: "evolution of new perceptual lenses / senses against dark
  residuals"; "sagacity"; "a sensory organ can evolve from components for
  which no contemporaneous ruler could individually detect value".
- Smallest actual mechanism: a causal feature-construction program (DAG of
  windowed/delayed/modular/boolean ops over a few input channels) whose
  output columns are appended to the input of a weak classifier; selection
  keeps programs whose columns raise held-out label accuracy over the
  current feature set. This is evolutionary feature construction for
  sequence classification with a held-out, null-matched admission test.
  [IMPL]
- What it could express in principle: any causal function computable by
  <= 48 such ops, including exactly the planted laws: xor(delay(a,4),
  delay(b,11)) is a 3-instruction lens; parity of 3 delays is 5
  instructions; count mod 3 is accmod; window majority is wsum + thresh; a
  2-4 state FSM is one op. [CODE-INFERRED]
- Phenomenon the ruler tried to observe: acquisition of a "sense" for
  structure that the current ecology cannot exploit, in particular senses
  whose precursors carry zero marginal information (v1 gate 6) and retention
  of "latent option value" across a regime shift (v2 Block R).
- Could the organism perform it: the classifier organisms are fixed weak
  learners; the "organism" that adapts is the lens population. The lens
  grammar can represent every planted needle in a handful of instructions,
  so the question reduces to whether mutation + selection finds a specific
  short program (search reachability), not whether a new representation
  can be formed. [CODE-INFERRED] The seat and Atlas both frame the results
  this way ("search reachability, not physics"; Atlas R3).
- Could the ruler tell it from a cheap shortcut: partly. The ruler resolves
  leakage (cheat caught), future-reading (causality audit), structure
  destruction (tsd twins and PRF stay flat), and seed-specific gains
  (replication on 2 fresh seeds; F4 caught). It did NOT resolve
  organism-capacity patching or manufactured residuals in v0 (F1, F2), and
  it cannot distinguish "a new sense" from "the search hit a short program
  the grammar already contains". In v1 "would have died under strict
  selection" was an assumption that proved false (lexicase and an unlogged
  14-slot reserve kept useless lineages alive). [RESULT-UNVERIFIED;
  CORRECTION]

## 5. Representation/state architecture

Lens state = list of registers (T-length float arrays); internal recurrent
state only in fsm/accmod/ewma/wsum; no learned weights inside a lens.
Ecology state = admitted genomes (v0 global; v1/v2 per world), population
(96) with genealogy (parents, operators), reserve slots, fossils (genome,
best case, reason). World state = generator spec (law parameters fixed;
seed draws input noise). Residual state: v0 masks per (ruler, split); v1/v2
deficit numbers per (world, ruler, organism); catalogue entries as JSON.
[IMPL]

## 6. Organism/player architecture

Three fixed weak learners (lin, tree, tab), fitted on 3,000 training
points, deliberately weak per charter ("use weak organisms deliberately").
No recurrent organism, no policy, no actions on the world: A in the charter's
W -> X -> L -> Z -> O -> A -> W loop is a prediction, and the world does not
respond. tab was the main source of v0 artefacts: 28 of 44 admissions; its
feature budget displaced raw channels as the ecology grew (K1_ident
baseline 1.000, 0.995, 0.547, 0.998, 0.518 by epoch). [IMPL;
RESULT-UNVERIFIED]

## 7. World/environment architecture

TOY SCALE, flagged precisely: every v0-v2 world is a 6-channel (Hecate
worlds: component count minus one, e.g. 4 or 5; H_ADV_sparse 8)
observation stream of length 12,100, i.i.d. Bernoulli(0.5) or Gaussian
inputs (one Markov sibling), and an integer label that is a fixed boolean
or modular function of up to 4 delayed inputs (delays <= 16) or the next
value of a <= 4,096-state deterministic Hecate system with restarts every
25 steps. No spatial structure, no agents, no resources, no actions,
fixed laws within a phase (v2 regime worlds switch once at generation 20).
Partial observability only in Hecate worlds (one component hidden) and by
delay. Task diversity: v0 24 selection + 8 held-out worlds of about 12 law
types; v1 Z1-Z5, C1-C2, G, N twins, held-out siblings; v2 D1-D7 classes +
R1-R4 regime worlds + up to 10 broad worlds. All laws are authored by the
same seat that authored the lens chemistry. [IMPL worlds.py,
worlds_v2.py:1-25; PREREG_BLOCK_R]

## 8. Search/training/adaptation mechanism

- Variation: 9 mutation operators, 25% cross-lineage graft, fuse (v1+),
  compose (v2 LOL flag, unrun). [IMPL]
- Selection: eps-lexicase over 432 (v0) or fewer (v1/v2 R0 only) cases;
  elites best per (world, ruler); reserve with age protection, novelty of
  signature, random quota (v0 14 slots; v1 DE 48 slots plus neutral drift);
  v2 STRICT arm requires val z >= 2 on some case. [IMPL; CLAIM]
- Admission: per epoch, conf split, paired z >= 4 and gain >= 0.01, one per
  world per epoch (cap 48) in v0. [CLAIM PREREG]
- Bottlenecks/collapse modes recorded by the seat: (1) needle blindness --
  zero-marginal structure gives no gradient (P1 xor, P7 parity, ADV_decoy
  unsolved in v0; Z3 parity-3 and Z5 deep-precursor xor unsolved by every
  arm in v1; R2 parity-3 adapted 0/18 in Block R); (2) "soft precursors" --
  windows and smoothers give 2-way xor graded footholds (+0.076 at gen 15),
  so xor is not a true needle in this chemistry; (3) budget parity in
  evaluation units penalises pair-evaluating arms (DE ran 36 generations vs
  V0's 80); (4) noisy lexicase acts as an implicit reserve; (5) complete
  precursor sets are never co-stored (max 0.007 of living lenses in any
  Block R run). [RESULT-UNVERIFIED]

## 9. Measurement/ruler stack

- Gains: paired accuracy differences per (world, ruler R0/R2, organism,
  scope); never collapsed (lexicase). [IMPL]
- Admission: conf split z >= 4 and gain >= 0.01. Pass D: test split,
  replication on seeds 101/102, 64 matched random lenses (same size) as
  null, causality audit, channel ablation (circular shift by 997 of one
  channel in the lens input), transfer to all 31 other worlds (counted only
  with fresh-seed replication AND beating 32 matched random lenses).
  Sensor classes. [CLAIM review packet; IMPL audits.py, ecology.py
  _gains_task]
- v0 verdict rules: H1 planted positives PASS if >= 4 valid worlds and >= 4
  SOLVED (a world is VOID if the best random initial lens already gains >=
  0.03); H2 false gradients; H3 residual shift; H4 redundancy; H5 instrument
  (cheat control); H6 end-to-end (PASS iff H1, H2, H5 PASS and a later
  generation lens ...). [IMPL PREREG v0 lines 105-130]
- v1: gate-6 predicate on a fused sensor: both components' max individual
  home val gain < 0.01 at every logged evaluation, fused test gain >= 0.10,
  replication, pair-null p95, twin clean. Valid Z worlds: best initial
  single <= 0.018, best of 4,560 initial pairs <= 0.061, void threshold 0.10.
  [CLAIM REVIEW_PACKET_v1]
- v2: world certificates (bias-corrected plug-in MI of Y with every subset
  of hidden precursors, 20 permutations, 0.005-bit threshold; a raw feature
  bank foothold check; oracle deficit); OV = generations after the switch
  until the slot's best replicated L2 gain (censored at 31); SO = fraction
  of living lenses carrying any / all L2 precursors by MI. [IMPL certify.py
  docstring; PREREG_BLOCK_R]
- Known blind spots (seat-found): v0 err/dis residuals had no negative
  control and moved mechanically with ecology size (F1); tab budget
  manufactured residual (F2); three of six "inaccessible" positive controls
  were accessible to random lenses (VOID); H1 PASS unattainable by
  construction with 3 valid worlds (Harmonia); OV clock blind to admitted
  coalitions (Block R); reserve membership unlogged in v1 V0; "revived
  lineages" 37/44 with no base rate (F5). [CORRECTION]
- Additional blind spot (this crawl): the "oracle" for the v1/v2 deficit
  is an answer-key lens written in the same chemistry; the deficit
  therefore measures distance to a known program, which is right for
  calibration but means no v0-v2 measurement addresses structure outside
  the grammar. The PRF worlds are the only "outside the grammar" control
  and they are designed to be unreachable. [CODE-INFERRED]

## 10. Baselines and controls

TSD twins (same inputs, Y from an independent hidden copy) per planted law;
keyed PRF worlds; known worlds (K1-K4) as redundancy checks; Hecate
MATCHED_NOISE worlds; LEAD cheat control; matched random-lens nulls at
admission (v0 Pass D 64, transfer 32; v1 pair nulls); best-of-initial-
population access check (v1: all 4,560 initial pairs); answer-key oracle
deficit; v2 STRICT arm as a by-construction "would have died" baseline.
Missing: stronger organism baseline (no neural or program-search learner;
TYCHE-13); a raw-feature-bank learner as a non-evolutionary baseline (the
v2 certificate bank exists but is a foothold check, not a competing arm);
longer-search or larger-population arm for the needles (Atlas notes "Tyche
2/72 has no plant or longer-search contrast"). [IMPL; CLAIM Atlas]

## 11. Historical experiment campaigns

C1. v0 attempt 1 (stopped)
- 2026-09-30, from 075e5fc21; stopped by the seat at gen 34/40 after 13.0
  core-hours (BLAS oversubscription, 13 s -> 330 s per generation). Rows
  tyche/runs/v0_2026-09-30_ABORTED/, unscored. Label: INSTRUMENT FAILURE
  (infrastructure).

C2. v0 dark-ecology lens evolution
- Dates 2026-09-30; prereg 075e5fc21, amendments 32fa63544, e8f9ff4c3;
  rows d5b25e4e0; report 8d6e4c805; Harmonia labels bdeba9865.
- Question: does lens mutation -> differential capability -> reproduction
  -> residual shift -> new generation work end to end without leakage?
  Organism lin/tree/tab; worlds 32 (s7); pressure eps-lexicase + reserve +
  graft; measurement s9; arms none (single ecology); scale s2.
- Reported: H5 PASS (cheat z 54.9 rejected by causality), H2 PASS (0 of 8
  negative worlds, 0 of 210 admission tests admit on them), H1
  INDETERMINATE (P2 count mod 3 and P5 sign of product SOLVED from chance;
  P1 xor NOT SOLVED; P3, P4, P6 VOID), H3 FAIL, H4 FAIL, H6 INDETERMINATE;
  44 admitted, sensor classes LOCAL 12, FAMILY 7, TRANSFER 10, GENERAL 11,
  NOT_REP 4; "opaque successful" 28. Verified in this crawl: REPORT.json
  verdicts match.
- Later reinterpretation: Harmonia e72508448 labelled H1/H6
  UNREACHABLE_BY_DESIGN and H3's negative arm NON_DISCRIMINATING; the seat's
  packet says "the v0 positives are instrument positives" and "the 28
  opaque successful lenses are opaque only because nobody looked; several
  are likely capacity patches or F2 artifacts". F4: three P5/R2/tree
  lenses +0.236/+0.159/+0.134 on the selection seed, 0.033/-0.006/0.000 on
  fresh seeds (open, TYCHE-26; Atlas buried-signal F6).
- Label: MIXED (instrument validity PASS; science hypotheses FAIL or
  unreachable).

C3. Residual catalogue v0 / v0.1
- 3c7b9783e, 8cb8d804a, 2026-09-30. 93 entries imported from Artemis's
  harvest, 39 drafted by an agent (15 skipped as duplicates, 9 framings
  corrected), 122 admitted / 10 rejected by quote verification; v0.1 67/122
  with raw rows, 17 cross-engine niches (model-assigned tags). Not an
  experiment. Label: UNKNOWN (inventory; no measurement of the residuals).

C4. v1 zero-marginal precursors (gate 6)
- Directive e6884298c; prereg 282f01c45; result d32dbfb49; correction
  6a28fc49e.
- Question: can a lens lineage acquire a useful sense whose necessary
  precursors have no individually measurable utility? Arms V0 / DE / DENR x
  seeds 1, 2; R0 only; worlds Z1-Z5, C1-C2, G, N twins + PRF, held-out
  siblings.
- Reported: GATE 6 FAIL. Z cells solved (test >= 0.10, replicated): V0 3,
  DENR 2, DE 1 of 10. One both-useless fused sensor (DE s1, Z2: components
  0.004 / 0.006; fused +0.075, z 5.6; fresh seeds +0.101 / +0.109) fails only
  the 0.10 bar. Z3 parity-3 and Z5 unreached. Negatives clean (1 conf
  admission on a twin killed by Pass D).
- Later reinterpretation: the V0 arm included v0's unlogged 14-slot reserve,
  so "survived on noise-level lexicase wins" is inference, not observation
  (CORRECTION annotated in the packet, 6a28fc49e).
- Label: REPORTED NEGATIVE/NULL (gate), with an informative MIXED trace.

C5. v2 Block R attempt 1
- Harness memory stop (~15 GB, host at 4.6 GB free); survivor processes
  killed by the seat; cache fix + amendment 1 (7fc0cf97a). Label:
  INSTRUMENT FAILURE (infrastructure).

C6. v2 Block R, latent option value under unannounced regime change
- Prereg e9fd76349 + 7fc0cf97a; result 4dbbc07d0
  (tyche/runs/v2_blockR/REPORT_BLOCK_R.md).
- Design: H {STRICT, LEX, RES} x V {solo x 4 regime worlds, related,
  broad} x seeds {1, 2} = 36 runs; 50 generations, switch at 20. Regime
  worlds R1 smooth majority -> xor of 2 delays; R2 smooth -> parity of 3;
  R3 xor(A,B) -> xor(A,C); R4 xor(A,B) -> xor(C,D).
- Reported: RH1-RH4 FALSE, RH5 (0/18 R2 adaptations) held. 2 of 72 cells
  adapt, both related condition seed 2 (RES R1 fused +0.496 OV 10; STRICT
  R3 fused +0.337, missed by the OV clock). Stored optionality any
  precursor LEX 0.115 > RES 0.075 > STRICT 0.055; broad 0.120 > related
  0.079 > solo 0.045; all precursors about 0. 92 natural histories: 62
  coalitions, 63 with exaptation; persistence events noise-level parent
  choice 395, significant-elsewhere 280, drift-born 120, reserve age 94,
  elite 53, reserve novelty 36, random 2; mean strict-survivable fraction
  of path ancestors 0.929. One "preserved-useless-until-needed" assembly
  (RES related s2 R1).
- Later reinterpretation: none yet beyond the seat's note that 30
  post-switch generations may be a clock artefact.
- Label: REPORTED NEGATIVE/NULL (with one anecdotal positive instance).

C7. v2 Block M (static pressure map, coalition depth, LOL chemistry,
D1-D7 classes): NOT RUN at this SHA. Label: UNKNOWN.

## 12. Reported results and later corrections (timelines)

T1 v0 H1: prereg expects PASS with P1, P3, P4, P5 solved -> run: P3, P4, P6
VOID, P1 unsolved -> INDETERMINATE -> Harmonia: PASS was unreachable by
design (3 valid worlds vs rule >= 4) -> label UNREACHABLE_BY_DESIGN ->
status: design defect, not a lens-evolution result. [CORRECTION]

T2 v0 residual shift (H3): claim residual shrinks as lenses evolve ->
evidence err residual 0.261 -> 0.140 on PRF1 with flat accuracy -> seat:
organism decorrelation, not information -> v1 retires err/dis for oracle
deficit -> status: v0 residual instrument invalid. [CORRECTION]

T3 v0 redundancy (H4): lenses admitted for re-supplying raw channels ->
tab budget manufactured residual -> v1 tab sees [candidate, raw] only ->
status: fixed; H4 FAIL stands for v0. Seat's Harmonia reply #1047 offers an
"evolving baseline" counterpoint (not read). [CORRECTION]

T4 v0 seed fragility (F4): P5/R2/tree gains vanish on fresh seeds -> open
(TYCHE-26) -> Atlas lists it as buried signal F6. Status: unexplained.
[RESULT-UNVERIFIED]

T5 v1 "noise persistence is an implicit dark ecology" (F1) -> correction
6a28fc49e: V0 carried an unlogged reserve -> mechanism unresolved -> v2
separates LEX and RES with logged membership -> Block R: LEX stores more
fragments than RES; persistence events dominated by noise-level parent
choice and significance elsewhere -> status: in Block R, noisy lexicase
plus exaptation, not an explicit reserve, carried most persistence (one
RES exception). [CORRECTION then RESULT-UNVERIFIED]

T6 v0 "xor is a zero-marginal needle" -> v1 F2 soft precursors: windows
and smoothers give graded footholds -> seat: STOP using 2-way xor as the
canonical control in this chemistry -> v2 adds parity-3/4 and secret
sharing with exact certificates. [CORRECTION]

T7 Atlas: Atlas cites Tyche v0 H1 "3 valid worlds < 4 required"
(VERIFY_SYNTHESIS_2.md, CONFIRMED against PREREG line 109), Block R "2/72"
and "fragments stored, never sets", "62/92 senses by coalition, 63/92
with exaptation", catalogue "122 entries", "model-assigned" niche tags.
All agree with the seat files read here. Atlas ATLAS_ONTOLOGY_GAPS_VNEXT.md
groups Tyche H1 under "ruler_can_return_opposite" failures, and
ARTIFACT_MAP.md R3 notes the claim "search reachability, not physics,
bounds what we see" is "close to unfalsifiable as framed" and proposes a
needle-size measurement (fraction of random programs at plant length that
solve) not yet done. Atlas also notes Tyche spoke once in comms (1 message
vs Nestor's 91), so its digests may underweight Tyche. No disagreement
found. [CLAIM; verified where stated]

## 13. False-positive archaeology

- F1 residual shift (v0): a residual that tracks organism disagreement
  falls as more features decorrelate learners; looked like "residual
  converted to structure". Killed by the seat's negative-world comparison.
- F2 manufactured residual (v0): an attention budget pushed raw inputs out;
  lenses that restored them earned +0.49 and were admitted as "senses".
- "Opaque successful lenses: 28" (v0): opacity was not tested
  (interpretation never attempted), so the count is of unlooked-at lenses.
- "Revived lineages 37/44" (v0): no base rate.
- Transfer significance from capacity patching (smoke): any random
  nonlinear feature helps lin/tab on many worlds; caught before freeze by a
  matched random-lens null.
- R2 ruler leak (v1 design): shifting every delay by 2 made Z4 solvable by
  one initial lens (+0.497); caught at design time; v1 R0 only.
- D6 world (v2 design): certificate showed a 0.92-bit window foothold;
  redesigned before the freeze.
- v1 both-useless fused sensor (+0.075): genuine-looking instance of the
  directive's mechanism, below the preregistered bar, and V0 solved the
  same world in the same seed. Not a false positive yet, not a positive.

## 14. Likely false-negative regimes

- Search budget: 40 (v0), 36-83 (v1), 30 post-switch (v2) generations of 96
  lenses; Atlas notes no longer-search arm. A parity-3 lens is 5
  instructions in a 27-op chemistry; the probability that mutation hits it
  without gradient in this budget was never measured (needle-size
  measurement absent), so "unreached" may be budget, not mechanism.
  [CODE-INFERRED]
- Organisms: lin cannot represent xor of two binary features at all; tree
  depth 4 can represent 2- and 3-way parity of given features only if the
  features are supplied; tab of median-binarised features can, if the
  needed columns are within its window. So a pair (fused) of two delay
  lenses is solvable by tree/tab, not lin; the gain the ruler sees depends
  on organism capacity, not only on lens information. [CODE-INFERRED]
- Budget accounting: equal evaluation units penalise pair search (v1 F3);
  a coalition-screen fix exists in v2 but Block M is unrun.
- Ruler resolution: admission z >= 4 with 210 tests (v0) may suppress weak
  real effects (seat Q3).
- Single-channel information: the observation is only 6 i.i.d. channels;
  structure in Hecate worlds is confounded by tab artefacts in v0 (15
  admissions there, mostly tab) and not revisited.
- Natural residuals: the 122 catalogue entries were never run, so nothing
  about real Prometheus anomalies is known.

## 15. Phase 3 audit

### E1-E3 Tyche lens ecology (v0-v2, one engine family)

a. Representation richness (lens + organism):
- hierarchy: PARTIAL (register DAG; graft/fuse; compose b(a(X)) exists in
  code, unrun in any campaign).
- compositional structure: YES (programs compose ops; grafts and fusion
  combine lineages).
- variable binding: NO (register indices are positional; no symbols).
- memory: PARTIAL (delays up to 16, windows up to 24, ewma, cumulative
  accmod).
- recurrence: PARTIAL (only inside fsm/accmod/ewma; the DAG itself cannot
  loop).
- counterfactual state: NO (no intervention rulers; TYCHE-07 backlog).
- latent variables: PARTIAL (fsm hidden state; Hecate worlds have one hidden
  component that a lens could in principle track).
- temporal abstraction: PARTIAL (sample-and-hold, windows; no learned event
  segmentation).
- spatial abstraction: NO (no spatial worlds).
- reusable substructure: PARTIAL (graft copies donor cones; admitted lenses
  become features; no named library calls).
- dynamic routing: PARTIAL (where op; gate-like conditionals).
- self-reference: NO.
b. Reasoning opportunity: the environments demand finding a small fixed
   boolean/modular function of delayed inputs and handing it to a
   classifier. That is feature search for a lookup/parity target; no
   planning, no control, no sequential decision, no transfer of an
   abstract rule beyond law siblings. The interesting part is the search
   problem (crossing zero-gradient regions), not the cognition demanded
   of any organism.
c. Shortcut surface: capacity patching (random nonlinear features help weak
   learners); manufactured residual via feature budgets (fixed in v1);
   seed-specific fits (caught by fresh seeds); soft footholds from windows
   (make xor gradual); the lens chemistry contains the generators'
   primitives (xor, delay, accmod, wsum, thresh, fsm), so success measures
   reachability of the author's own construction; coalitions where a
   zero-value partner completes a useful lens (F4 in v1) blur "both
   useless". World identity is not visible to lenses (seed derives from
   uid but X is the only input), and the causality audit forbids
   future-reading.
d. Ruler resolving power: good for leakage, causality, structure-destroyed
   twins and seed replication (negatives stayed flat through v0-v2); weak
   for "new sense vs short program the grammar contains"; v0 residual
   rulers invalid; v2 OV clock censored nearly everything at 31 and missed
   one coalition adaptation.
e. Scale: inputs d = 6 (4-8), T = 12,100 (3,000 per split), labels binary or
   3-class; lens <= 48 instructions, <= 3 outputs, 27 ops; population 96;
   generations 40 / 36-83 / 50; worlds 32 (v0), about 15 (v1), up to 14 per
   run (v2 broad); 3 organisms; compute v0 <= 15.4 core-h, v1 about 2 core-h,
   Block R about 12 core-h upper bound; 28-CPU host, 32 GB, memory-bounded
   (two harness stops).

### E4 Residual catalogue

a. Representation: JSON records with quote-verified sources, kind enum,
   free-text phenomenon, model-assigned tags. Richness criteria do not apply
   (not an executable system).
b. Reasoning opportunity: none executed.
c. Shortcut surface: tags and niche clusters are model-assigned (Atlas
   notes "validate() proves a quote exists, not that the phenomenon is
   real").
d. Ruler resolving power: the validator resolves provenance (exact quote at
   sha), not truth.
e. Scale: 122 entries from 30 seats; 67 with raw rows; 17 niches.

## 16. Research reports and substantial documents

- roles/Tyche/prompts/2026-09-30_charter/01_OPERATOR_CHARTER_verbatim.md --
  the DARK RESIDUAL / DARK ECOLOGY charter.
- roles/Tyche/prompts/2026-09-30_v1_directive/..., 2026-09-30_v2_pressure_map/...
  -- operator directives (v1 zero-marginal control; v2 pressure map).
- roles/Tyche/prereg/2026-09-30_v0/PREREG.md (+ AMENDMENT_1, _2),
  2026-09-30_v1/PREREG.md, 2026-09-30_v2/PREREG_BLOCK_R.md (+ AMENDMENT_1),
  with CODE_SHA256 files -- frozen designs.
- roles/Tyche/design/V2_PRESSURE_MAP_DESIGN.md -- v2 axes and difficulty
  classes.
- roles/Tyche/REVIEW_PACKET_v0_2026-09-30.txt, REVIEW_PACKET_v1_2026-09-30.txt
  -- self-contained packets with failure shapes F1-F5.
- roles/Tyche/STATUS_REPORT_2026-10-01.md -- heartbeat and results summary.
- roles/Tyche/calibration/LEDGER.md -- 15 wrong-call rows.
- tyche/runs/v0_2026-09-30/REPORT.md, v1_2026-09-30/REPORT_v1.md,
  v2_blockR/REPORT_BLOCK_R.md -- campaign reports.
- tyche/residuals/README.md, v0_1/SUMMARY_v0.json -- catalogue.
- roles/Tyche/prompts/2026-09-30_reply_harmonia/01_REPLY.md -- reply to the
  ruler audit (not read).
- roles/Harmonia/audits/RULER_QUALITY_2026-09-30.md -- external ruler audit
  (not read beyond commit message).

## 17. Journals/TODOs/backlogs/pivots/abandoned branches

- roles/Tyche/journal/2026-09-29.md, 2026-09-30.md -- creation, build
  findings (headroom fixes, tab 0/1 fix, MemoryError cache cap, smoke
  capacity-patching finding, consequence-in-observation test rewrite),
  stopped attempts, Pass D resume, catalogue build, v1, v2.
- roles/Tyche/TODO.md (stale currency 08:10Z: TYCHE-22..26) and
  BACKLOG_H0H5.md (27 rows: experiment organisms, intervention rulers,
  lens-of-lens, Hecate triplicate worlds, representational diversity, world
  mutation, recombination pass, cross-observer, LLM as organism, legibility
  surface, Visual Cortex, human-machine coevolution, ruler population,
  second-order sagacity, external world adapters, Fabric, independent
  review, base-rate null for revivals). Most charter passes E-J are backlog.
- roles/Tyche/superseded/ -- pre-charter scaffold.
- Branch tyche/dark-ecology-v0-2026-09-30, fast-forwarded to main.
  Abandoned: v0 attempt 1 and Block R attempt 1 (infrastructure); Block M
  pending.

## 18. Dependencies on other engines and seats

- hecate/alien/systems.py and hecate/alien/data/answer_key.json (world
  families; read-only import). [IMPL]
- Artemis harvest D1-D5 (catalogue import). [CLAIM]
- sklearn DecisionTreeClassifier, scipy lfilter, numpy. [IMPL]
- Consumers: Theseus imports tyche.lens (lensmap op; dark-object lens
  evolution) -- a change to tyche/lens.py changes Theseus (blob changed
  2f309eeb8 -> 5f3df8cc2 between Theseus runs; compose() added). [IMPL]
- Governance: Harmonia, Cyclops, Aporia (CWO), MWO-0004 envelope. [CLAIM]

## 19. Scaling limitations

Per-generation cost grew with a global ecology (2 s -> 18 s per generation
in v0), fixed by per-world ecology; memory per worker (lens-output caches;
two harness stops) bounds concurrency; evaluation is O(worlds x organisms x
rulers x candidates) organism fits per generation (sklearn tree fits
dominate); pair screening is O(L^2) (v2 MI pre-screen); logs at 205 MB for
36 runs. Search is a 96-lens population for tens of generations; needle
problems likely need orders of magnitude more evaluations or a different
operator. [IMPL; CLAIM]

## 20. Lens potential for Phase 3 (descriptive, no ranking)

As a lens on "evolution of perceptual feature constructors across
zero-gradient regions":
- substrate: causal register programs over multichannel time series;
- organisms: fixed weak classifiers; the evolving entity is the lens
  population;
- worlds: authored boolean/modular functions of delayed inputs, Hecate
  finite deterministic systems, structure-destroyed twins, keyed PRFs,
  regime-switching worlds;
- pressures: lexicase, strict significance gating, explicit reserves,
  world diversity, regime change;
- phenomenon family: synergistic (zero-marginal) feature discovery,
  exaptation, coalition assembly, latent option value;
- current resolving mechanism: held-out accuracy gains with matched random
  nulls, fresh-seed replication, causality audit, exact subset-MI
  certificates, natural-history tracer;
- likely resolution ceiling: can tell found vs not-found for a known
  answer-key program and can trace how it was found; cannot tell a "new
  sense" from search reaching an author-known short program; nothing yet
  on structure outside the chemistry;
- noise sources: lexicase noise-level cases, seed-specific fits, organism
  capacity, tab binarisation, budget accounting;
- architectural limit: DAG lenses with a fixed 27-op chemistry, fixed weak
  organisms, prediction-only rulers, toy worlds with i.i.d. inputs;
- reusable parts: causality audit and LEAD cheat control; TSD twin
  construction; keyed-PRF negatives; certify.py subset-MI certificates;
  oracle-deficit residual for calibration lanes; natural-history tracer
  with per-event persistence reasons; fuse/compose/graft genome algebra;
  quote-verified residual catalogue validator;
- toy-grade parts: the world set, the organisms, the 30-generation regime
  horizon;
- unknowns: needle-size (random-program hit rate at plant length); Block
  M; any natural residual; organism-x-lens interactions with a stronger
  learner.

## 21. Open questions / coverage gaps

Not read: tyche/run_v0.py, report.py, passd_resume.py bodies; v1
run_v1.py, worlds_v1.py, report_v1.py, trace_precursors.py bodies;
v2 run_v2.py beyond the header/flags, history_v2.py, report_v2.py,
worlds_v2.py past the primitives, certify.py past its docstring and mi();
tyche/tests/; any run row files beyond REPORT.json verdict keys and
directory listings; PREREG v1 text; PREREG_BLOCK_R past the hypotheses;
V2 design past section 2; the Harmonia ruler audit body and Tyche's reply;
catalogue entries themselves; roles/Hecate beyond hecate/alien/systems.py
docstring. Not resolved: TYCHE-26 seed fragility; whether Tyche answered
Theseus #1124; the content of Harmonia's "evolving baseline" exchange.
Zero-cost inspections run by this crawl: Python reads of the v0 and v1
REPORT JSON verdict keys and directory sizes. No code executed.
