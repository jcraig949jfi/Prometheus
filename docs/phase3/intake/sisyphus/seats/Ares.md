# Ares -- forensic dossier (Sisyphus crawl)

Seat: Ares
Crawl date: 2026-10-01
Worktree base SHA: 19299e06b (origin/main at crawl time)
Crawler: Sisyphus worker (Opus 5.5), read-only

Coverage statement.
READ: roles/Ares/ in full (RESPONSIBILITIES, superseded/RESPONSIBILITIES_precharter_2026-09-19, STATUS, RESUME, TODO,
BACKLOG_H0H5, calibration/LEDGER.md, charter verbatim (first ~150 lines), the three review packets by header);
ares/ code: substrate.py (whole), worlds.py (W1, W4, W9, W13-W16 in full; the rest by class header), search.py
(run(), selection, final-champion code), develop.py header, verdict.py / validate.py / cycle2.py / recheck_c2.py
(grep for the held-out statistic); reports ARES_FIRST_REPORT.md, ARES_CYCLE1_REPORT.md, ARES_CYCLE2_REPORT.md (whole);
DESIGN_C2.md (the 33.75/24.56 line); runs/sweep_c2/gates.txt, recheck.json, basin.json (parsed); git log of ares/ and
roles/Ares/ (13 commits, 2026-09-19..25). Cross-seat: comms #518-#540 (Ares outbound), #574 (Nyx reading, body read
to ~9k chars), #875/#1004 (Artemis findings), #1121 (Artemis residuals); roles/Artemis/backlog/FRONTIER.md FR-001/
FR-118, INDEX.md FR-002/FR-083/FR-118, dispatch/D001/DIGEST.md D001-08, dispatch/D002/RESULT.md D002-08A/B/C,
selftest/runs/R-17 (W16) and R-29 (accessibility predictors) reports (partial); Atlas inference harvest grep.
NOT READ: ARES_PRESSURE_NOTES.md and PRESSURE_CATALOG.json beyond their role as listed deliverables (citations are
self-labelled FROM MEMORY); DESIGN_C0/C1 bodies (only via the reports' quotations); carriers.py, sweep.py, baselines.py
bodies; individual run JSONs other than the three c2 summary files; journals 09-19..09-25 (used STATUS/RESUME instead);
roles/Nyx/reports/ARES_W4_READING_2026-09-25_run.txt (used the comms body). No code was executed except parsing two
committed JSON files.

---

## 1. Identity and purpose

Canonical name: Ares. Aliases/instances: Ares[m2-640acfe6] (the only instance id in commit subjects). [HIST]

Host: M2 (SPECTREX5); worktree D:\Prometheus-worktrees\ares-base-role, branch ares/base-role-adopt-2026-09-19,
fully merged into origin/main (RESUME.md s1). [HIST] All 13 commits on ares/ and roles/Ares/ are 2026-09-19 to
2026-09-25 (git log). [IMPL]

Creation and charter.
- 2026-09-19 d1f22735a: created on M2 with only "inherit base role, then discuss the charter"; pre-charter file kept at
  roles/Ares/superseded/RESPONSIBILITIES_precharter_2026-09-19.md (no lane, no science). [HIST]
- 2026-09-19 2a7ada279: charter adopted, verbatim at roles/Ares/prompts/2026-09-19_charter/CHARTER_verbatim.md
  ("ARES -- PRESSURE ENGINEERING / PRIMORDIAL SOUP SANDBOX"). Mission: abstract the selective pressures behind
  biological reasoning (catastrophic asymmetry, rare opportunity, nonstationarity, hidden state, delayed consequence,
  scarcity, developmental construction, plasticity, ecological coupling, transplantation, irreversibility, ...) and use
  them as "light steering" for the emergence of alien machinery. "Create the necessity. Do not prescribe the
  mechanism." Forbidden: rewarding memory, planning, modularity, etc. [INTENT]
- Same day the operator corrected a generalisation (calibration row 1: the M2 non-interference rule binds Atlas
  collectors, not every M2 seat). [CORRECTION]
- Later directives: 2026-09-21 cycle-1 directive ("validate, compress, exit"), 2026-09-23 cycle-2 directive ("attack
  the mechanism", with a mechanical A/B/C gate rule), 2026-09-23 export note (roles/Ares/prompts/*). [HIST]

Terminal role: PARKED since 2026-09-25 pending an operator continue/close decision that, as far as the record shows,
never arrived (STATUS.md; Artemis D001-08 verified "no Ares commit after 3f68be2b9"). [HIST] The seat is
recommendation-only for cycle 3 (gates A and B OPEN, C SHUT -> CONTINUE_RECOMMENDED). [HIST]

Relationships. Ares positions itself against Apollo/Ludus (organism/world evolution inside the ecosystem), Crius
(fitness over a fixed workshop), Aphrodite, Theophrastus, Bellerophon (Worlds Kernel, adoption deferred: ARES-24
never started), and hands mechanisms to Nyx/Harmonia for naming (RESPONSIBILITIES s1). [INTENT] Isolation: no
integration with SFE/NPE/Archaeon/Vivarium/prometheus/toolbox. [IMPL: ares/ imports only numpy and itself]

Consumers in practice: Ares sent 7 comms messages (#518, #519, #535, #536, #538, #539, #540) and its RESUME (commit
3f68be2b9, 2026-09-25 06:55 -0400) records zero replies. [HIST] That claim was overtaken 85 minutes later: Nyx replied
at #574 (2026-09-25 08:21 -0400, commit bf5073a91 08:20) with a full reading of the W4 fossils (nyx/readings/ares_w4_reading.py, commit bf5073a91). Artemis
later sent unverified worker findings (#875 09-28, #1004 09-29) and residual reruns (#1121 09-30). Theophrastus (a
named export recipient, #539) had been dormant since 09-14 and never replied. Harmonia never replied. [HIST,
CORRECTION of RESUME Q2]

## 2. Engine / system inventory

One engine: the Ares pressure-engineering sandbox, ares/ at repo root (1055 tracked files; ~20 code/doc files, the rest
run receipts). [IMPL]

| component | path | role |
|---|---|---|
| substrate | ares/substrate.py (560 lines) | batched generic graph organism, mutation, runtime, structural measures, ablation, splice |
| worlds | ares/worlds.py (483) | W1-W5, W7, W9 (two-sided), W11-W16; modes present/absent/shuffled |
| search | ares/search.py (439) | GA run(), run_coevo() for W9, rollout, dissect, transfer, receipts |
| developmental encoding | ares/develop.py (172) | W10: 4 graph-rewrite rules x 11 fields grown for 4 steps |
| carrier instruments | ares/carriers.py (343) | edge- and SCC-aware carrier attribution/classification, opportunity, basin, edge-aware transplant/swap (cycle 2) |
| sweep drivers | ares/sweep.py (c0), validate.py (c1), cycle2.py (c2), verdict.py (c0 verdict) | |
| repairs/probes | supp_nomem.py, supp_selfloop.py, recheck_c2.py, calibrate_w12.py, baselines.py | post-hoc ablations and D1/D2 re-derivation |
| tests | ares/tests/test_ares.py, test_carriers.py | determinism, cheat controls, floors |
| docs | ARES_PRESSURE_NOTES.md (P01-P18), PRESSURE_CATALOG.json (12 built + 6 candidate), DESIGN_C0/C1/C2.md, three reports | |
| data | ares/runs/sweep_c0 (297 files), sweep_c1 (334), sweep_c2 (396), runs/baselines.json, fossils/W4_activation_memory_s3 (FOSSIL.json, REPLAY.txt) | |

Execution model: pure Python + numpy; a population of P organisms is stored as stacked arrays and run in lockstep
against one batched world episode (common random numbers). Reported speed "~13 ms per 128-organism episode"
(cycle-1 report s6). [HIST] Finite command-line sweeps, no daemon, no monitor ever registered. [IMPL/HIST]

Persistence: one JSON per run with log (every 5 generations), final genome, best_ever, champion ancestry chain and a
receipt (code_commit, config, seeds). Per-run dissection JSONs in c1/c2. [IMPL: search.receipt, search.run return]
Artemis Fabric Q10 (#1004) notes that full population ancestry is built in memory but only the champion chain and
pooled mutation_survival are persisted, so "does ancestry predict breakage" is untestable from the record.
[HIST, consistent with search.run code]

Scale: cycle 0 ~ 12 worlds x 3 modes x 3 seeds plus arms; cycle 1 130 GA runs at 10 seeds; cycle 2 190 GA runs
(180 preregistered + 10 post-hoc). P=128, G=120, 4 training episodes per generation, 32 held-out episodes.
[IMPL defaults in search.run; HIST counts from reports]

## 3. Architecture

World. A World object holds a hidden per-episode schedule drawn at reset (e.g. W4: regime bit r, cue array, noise
array) and returns, per step, a (P, 6) observation: channels 0-3 world-specific, ch4 = t/T clock, ch5 = constant 1.0;
reward (P,), alive (P,) (only W12 kills), and an info dict never shown to the organism. Episodes are 40-80 steps.
Actions are 3 discrete choices (argmax over 3 output nodes). [IMPL worlds.py, substrate.py]

Organism / genotype. A directed graph of n = OBS_DIM(6) + n_hidden(default 8) + N_OUT(3) = 17 node slots. Each node
has one of 9 arithmetic ops (ADD, MUL, MAX, MIN, THRESH, GATE, TANH, DIFF, CONST), a bias, a keep (leak) coefficient,
and two weighted input ports (W1, W2 matrices); W1 edges may carry a plasticity rate R (Hebbian-like
dw = R * v_i * v_j). Weights clipped to +-4, activations to +-8. [IMPL substrate.py]

Phenotype / execution. Per world step the runtime does `ticks` (default 2) synchronous updates:
v_new = keep*v_old + (1-keep)*op(W1 v, W2 v, bias), clipped and masked; plastic W1 updated after each tick. Node values
persist across steps unless reset_each_step. Memory model: three cross-step channels -- activation persistence via
keep, activation persistence via directed cycles (recurrence/self-loops), and plastic weights. [IMPL Runtime.step]

Mutation operators: add_node, remove_node, add_edge, remove_edge, alter_op, alter_bias, alter_keep (N(0, sigma=0.3),
clipped to [0, 0.98]), perturb_weight, alter_plasticity (N(0,0.05), clip +-0.2, 30% chance zeroing), duplicate_node;
1 + Poisson(1) mutations per child, fixed operator weights. Optional constraints: forbid_self_loops,
forbid_recurrence (snapshot/rollback of any structural mutation that creates a cycle), keep_mut_weight (subsidy),
recur_mut_noise (jitter attack), keep_mut_sigma. [IMPL]

Selection: truncation + tournament + elitism. Elite fraction 0.125 copied unchanged; each other child picks the best of
3 random draws from the top half and mutates. Fitness = summed world reward over 4 freshly drawn episodes per
generation (optionally minus a recurrent-edge tax). No crossover in the main GA (splice_subgraph exists only for the
W8 transplant protocol). [IMPL search.run]

Reproduction / lineage: asexual copy + mutation; ancestry dict id -> (parent, gen, mutations); only the final
champion's chain is written out. [IMPL]

Learning: within-lifetime plasticity only (R rates); no gradient learning. Communication: none, except W9 coupling
(two populations see each other's last two choices). Cross-world transfer: evaluated by running a genome on other
worlds (search.transfer) and by subgraph transplant; nothing is trained across worlds. [IMPL]

Provenance/control structure: preregistration files committed before each sweep (DESIGN_C0 eed9c7121 before
bb133d083; DESIGN_C1 de8fd3abf before 8ba05b2c8; DESIGN_C2 ab137f52b before 1dde117f7); balanced held-out seed sets
per world (balanced_seeds_for + balance_key) from cycle 1 on. [IMPL + git order verified]

Implementation vs design disagreements (load-bearing):
- D1 (held-out selection) is STILL IN THE CODE at HEAD: search.run ends with
  `fit = rollout(pop, world, eval_seeds); champ = int(np.argmax(fit)); final = dict(heldout=float(fit[champ]), ...)`,
  i.e. the reported champion is chosen on the held-out set. TODO ARES-C2-1 to fix it at source was never done;
  Artemis R-21 (#875) independently reports the same lines. [IMPL, verified at ares/search.py ~lines 291-294]
- verdict.py (cycle 0) and validate.py (cycle 1) both score criterion (i) and the shuffled controls from
  res["final"]["heldout"] (grep-verified). Only cycle 2 was re-derived from the clean number (recheck_c2.py uses
  log[-1]["champ_heldout"]). Cycle-0 and cycle-1 control readings were never re-derived. [IMPL]
- The charter says "nodes contain tiny state/registers" and "edges transmit symbols"; the substrate is purely scalar
  float arithmetic. [IMPL vs INTENT; not a defect, a choice]

## 4. World capability audit

All worlds are tiny, non-spatial, single-agent (except W9), fixed-length episodic tasks with 6 observation channels
(two of them a clock and a constant) and 3 discrete actions. [IMPL]

| world | pressure | hidden state | horizon | notes |
|---|---|---|---|---|
| W1 | catastrophic tail | Markov danger bit seen through noisy cue | T=60 | acting in danger wipes 90% of accumulated reward |
| W2 | rare override | Markov window | 60 | risky +60 in rare cued windows; reward channel leaks window one step late (LEDGER) |
| W3 | changing rules | mapping flips mid-episode | -- | |
| W4 | hidden regime | 1 bit, shown as cue for 3 steps only | 40 | +1/-1/0; no reward channel |
| W5 | delayed revelation | token x pay (two bits) | -- | 26-step delay through distractors |
| W6 | scarcity | = W3 under n_hidden=2, ticks=1 | | a substrate config, not a world |
| W7 | incompatible regimes | -- | -- | |
| W8 | transplant | a protocol | | |
| W9 | matching pennies | coevolving opponent population | 40 | sees last two choices of each side |
| W10 | development | a genome encoding | | |
| W11 | irreversible commitment | -- | -- | |
| W12 | dying lineage | energy store, death | -- | only world with death |
| W13 | carrier stress | W4 cue + 57-step sd-1 distractor, pay steps 60-79 | 80 | |
| W14 | state noise | W4 + activation noise sd 0.5 | 40 | |
| W15 | interrupt | W4 + 4 random activation resets | 40 | |
| W16 | variable delay | cue window start in [0,20], pay last 10 | 40 | |

State size: the world-side latent is 1-2 bits plus a noise schedule; observation is 4 informative floats. The memory
demand in the best-studied world (W4) is ONE BIT held for ~37 steps. Partial observability: yes (by construction).
Stochasticity: yes (noise, Markov schedules). Delayed consequences: yes (W5, W13, W16). Adversaries/multi-agent:
only W9 (two-population matching pennies). Resources: only W12's energy. Ecology, environmental change across
generations, world generation, open-endedness, task diversity within a lifetime: NONE. Transfer between worlds:
measured only as a probe; failed. [IMPL]

Toy assessment (precise, not rhetorical): every world is a hand-written episodic decision problem whose solution is a
reflex, a state-keyed switch, or a one-bit latch. Nyx (#574) showed the W4 task is solved at cap by a zero-hidden-node
organism with two edges (an output self-loop plus the cue edge) for any self-weight in [1.5, 6.0]; lineage 9 evolved
exactly that. [HIST from Nyx, consistent with Ares cycle-1 s3.1 "seed 9 has zero hidden nodes"] This is effectively a
memorisable task: the attainable behaviour space at the cap is a small set of latch topologies.

## 5. Organism capability audit

- Instruction set: 9 scalar ops, two input ports per node, 2 ticks per world step by default. [IMPL]
- Memory: 8 hidden slots max (default), activations clipped at +-8. The clip is what makes positive-feedback loops
  bistable (Nyx #574: loop gain 3.92 per tick on seed 3 saturates to the clip). [IMPL + HIST]
- Writable memory: only activations and plastic W1 weights; no addressable memory, no registers, no tape.
- Control flow: none beyond dataflow through a fixed graph; GATE/THRESH provide data-dependent selection. Many ops
  degenerate to signed identities when port 2 is unwired (Nyx #574: GATE with unwired condition is "identity x
  weight"; MAX with unwired port is a rectifier). [HIST, CODE-INFERRED from _apply_ops]
- Sensors: 6 floats; actuators: argmax over 3 outputs. Learning: Hebbian plasticity on W1 only, rate in +-0.2.
- Planning, internal simulation, tool use, communication, self-modification, recombination: absent.
- Reproduction: imposed by the GA; organisms do not reproduce themselves.
- Development: only in the W10 arm (4 rewrite rules, 4 growth steps); reported no speed-up (cycle-0 Q7). [HIST]

Fighting chance for a nontrivial reasoning primitive: in this architecture, the richest structure realistically
reachable is a small recurrent analog circuit of <= 8 hidden nodes with 2 ticks of settling per observation. It can
latch bits, threshold, and condition an action on a held bit. It cannot compose, iterate an algorithm over
variable-size data, or build representations beyond a handful of scalars. Combined with worlds whose demand is one
bit, the system could only ever exhibit memory carriers, reflexes and switches -- which is exactly what the record
shows, and what Ares itself wrote in cycle 0 Q8 ("nothing yet defies a threshold/gate/carrier vocabulary") and cycle 1
s5. [CODE-INFERRED + HIST]

## 6. Search and pressure mechanism

Novelty source: random mutation + truncation/tournament selection with elitism; no novelty search, no QD, no
crossover (ARES-19 novelty arm never built). Pressure = the world's reward structure and episode schedule; extra
pressure knobs are substrate constraints (scarcity config, carrier exclusion, recurrent-edge tax, mutational subsidy,
jitter attack) and world variants (W13-W16). [IMPL]

Bottlenecks and collapse modes:
- Training fitness saturates fast: Artemis R-29 reports the champion training fitness reaches 90% of the cap within
  2.5-6 generations in every cycle-2 arm, so the evolutionary path is too short to read gradedness from. [HIST,
  unverified here]
- Training uses only 4 episodes per generation and selection takes the max of 128, so training fitness of the champion
  is a noisy max statistic; held-out is logged every 5 generations only. [IMPL]
- No parsimony pressure: neutral baggage accretes (duplicate_node copies never acquiring a function; Nyx #574). [HIST]
- Keep mutation is clipped at 0.98 and steps N(0, 0.3) from 0; the hand-wired keep sweep is monotone increasing right
  up to 0.98 (basin.json keep fit 27.8 at 0.96, 33.75 at 0.98). The "narrow basin pressed against the ceiling" is
  therefore partly a property of an implementation constant (the clip), not only of the update rule. [IMPL +
  CODE-INFERRED; not stated this way in the Ares record]

## 7. Measurement / ruler stack

- Fitness: world reward only; everything else recorded, not optimised. [IMPL]
- Cycle-0 verdict criteria (verdict.py): (i) present champion held-out >= threshold; (ii) conditional behaviour
  present AND absent from shuffled; (iii) >= 1 load-bearing hidden node (ablation delta <= -25% of range).
  Dispositions MATERIAL / REFLEX / FITNESS WITHOUT THE BEHAVIOUR / DID NOTHING / MERELY HARDER. [IMPL/HIST]
- Cycle-1 dispositions (validate.py): MECHANISM_DIVERSE / PRESERVE / NEW_CARRIER, three-way memory ablation
  (no_activation_mem, no_plasticity, no_memory), memory class ACT/PLAST/BOTH/NONE, node-level signatures. [HIST]
- Cycle-2 (carriers.py): edge- and SCC-aware cuts of recurrence / keep / plasticity, classes RECUR, KEEP, PLAST,
  MIXED:<list> (each listed cut alone collapses), REDUNDANT (only the cut-all collapses); mechanical gates A
  (substitution), B (causal explanation), C (transplantable). [IMPL per Artemis D001-08 C1 verification of
  carriers.py:135-149; HIST]
- Controls: absent mode, shuffled mode (balanced on every hidden binary only from cycle 1/2), abundant config, cheat
  controls (hand-wired W2/W4 mechanisms), no-memory arm, random organisms. Positive-control clause added after the
  cycle-2 smoke test produced a false OPEN (LEDGER 2026-09-23). [HIST]
- Transfer: transfer() across worlds; W8 subgraph transplant vs random subgraph; cycle-2 edge-aware transplant and
  per-pair carrier swap. [IMPL]

Known blind spots (recorded by the seat or later):
- D1 held-out selection (max-of-128) -- inflates every non-cap number and every shuffled control; fixed only in
  reporting for cycle 2. [CORRECTION]
- D2 best-of-N transfer statistic. [CORRECTION]
- D3 node-only ablation blind to output-node self-loops (cycle-1 criterion iii under-counted 6/10 vs 10/10). [CORRECTION]
- D4 shuffled controls balanced only on the first hidden binary (W5 cycle 0; W4/W13 cycle 1). [CORRECTION]
- "no_state" ablation left plasticity intact (cycle 0). [CORRECTION]
- Attainable/threshold borrowed from the absent mode (W12 cycle 0). [CORRECTION]
- Float32 exact-tie readout: W16 seed 208 holds its bit as a ~1e-22 residue read through an argmax tie (Artemis
  R-17, #875); "the KEEP carrier census should be treated as contaminated until tie-breaking/noise floor is fixed".
  [HIST, unverified here]
- carriers' class labels: W15 "redundancy" in the report is, by the instrument's own definitions, MIXED
  (co-dependent) 6/10 and REDUNDANT 1/10 (Artemis D001-08, D002-08C). [CORRECTION]

## 8. Experiment inventory (campaigns)

### Campaign A -- Cycle 0 sweep (2026-09-19)
- Question: which of 12 abstract pressures change the KIND of evolved machinery vs absent/shuffled controls?
- Organism/world/pressure: default substrate; W1-W5, W7, W11, W12 plus W6 (scarcity config), W8 (transplant protocol),
  W9 (coevolution), W10 (developmental encoding); 3 modes; 3 seeds/cell; P=128, G=120.
- Measurement: verdict.py criteria i-iii, nomem ablation (post-hoc supp_nomem.py), transfer, W8 transplant.
- Reported result: W4 MATERIAL (ablation 40 -> 2.6, activation memory, "GATE+MAX" pair in seed 3, fossil frozen);
  W1 MATERIAL (modest); W2/W7 REFLEX; W3 fitness without adaptation; W11 did nothing; W5 and W12 mis-scored by bad
  controls/threshold; no transfer; development not faster. Commit bb133d083; ares/ARES_FIRST_REPORT.md;
  ares/runs/sweep_c0/; ares/fossils/W4_activation_memory_s3/.
- Later reinterpretation: "accreted over ~13 generations" retracted (cycle 1 s3.3); "GATE+MAX pair" description
  wrong twice (cycle 1: GATE<->MAX 2-cycle; Nyx #574: a 3-node ring 13 -> 7 -> 15 -> 13 through output node 15, GATE
  and MAX ops functionally inert/dispensable); D1 means all cycle-0 shuffled-control numbers (e.g. W2 shuffled 60-80,
  W5 shuffled "high floor") were max-of-128 statistics, never re-derived.
- Label: MIXED.

### Campaign B -- Cycle 1 validate/compress/exit (2026-09-21)
- Question: does the W4 carrier replicate at 10 seeds with repaired controls; do W5/W12 hold; does a combined stress
  world (W13) produce a NEW_CARRIER?
- Arms: W4, W5, W12, W13 present/shuffled at 10 seeds; arm_nomem_W4; dissection, ancestry snapshots, causal
  transplant into 64 random organisms. 130 GA runs; prereg de8fd3abf; close 8ba05b2c8.
- Reported result: W4/W5/W12 MECHANISM_DIVERSE; W13 PRESERVE; NEW_CARRIER 0; W4 carrier "recurrent activation 10/10,
  keep 0/10, plasticity 0/10"; transplant fails; independence caveat: seeds 1-3 reproduce cycle-0 lineages byte for
  byte, so 7 new lineages.
- Later reinterpretation: "plasticity 0/10" does not replicate (cycle 2: 4/10 on fresh lineages with edge-aware
  attribution); scores still D1-biased (validate.py uses final.heldout), though W4 sits at the cap.
- Label: MIXED (replication of function REPORTED POSITIVE; carrier-mix headline LATER OVERTURNED).

### Campaign C -- Cycle 2 attack the mechanism (2026-09-23)
- Question: why does recurrence win over the designated keep carrier? Is substitution possible? Is the carrier
  transplantable?
- Arms (gates.txt): c1_all, c1_only_recur/keep/plast, c1_none, c2_no_selfloop, c2_no_recur, c2_tax_low/high,
  c2_keep_subsidy, c2_recur_unstable, W14/W15/W16 present and shuffled, c1_shuffled_ref; plus post-hoc
  c3_keep_reachable. 10 fresh seeds (201-210), held-out from 40000. 190 runs. Prereg ab137f52b; close 1dde117f7.
- Reported result: all three carriers individually sufficient (only_recur 10/10 ttt 10; only_plast 10/10 ttt 17.5;
  only_keep 9/10 clean, ttt 30); c1_none 0/10; substitution under exclusion/tax; W15 "redundancy"; no transfer
  (per-pair recovery median 0.02, >= 0.5 in 16/59); reachability-subsidy arms did not flip the carrier; c3 prediction
  (keep load-bearing >= 3/10) LOST at 2/10; post-hoc basin width explanation. Gates A OPEN, B OPEN, C SHUT
  (corrected from OPEN).
- Later reinterpretation: (1) the "intrinsic superiority killed" step rests on comparing hand-built keep 33.75 with
  recurrence at weight 3.0 (24.56); basin.json itself shows recurrence 40.0 for weight >= 4.0, so recurrence has the
  higher peak AND the wider basin -- the headline confounds basin with payoff (Artemis FR-001, R-29; verified here in
  basin.json). (2) W15 "redundancy" is MIXED co-dependence by the instrument's own classes (D001-08), confirmed not an
  artifact of the cut (D002-08C, 6/6 MIXED collapse with R kept), origin INDETERMINATE (D002-08B). (3) Ares itself
  demoted its proposed falsifier (re-parameterise keep) on 09-25 in favour of "decouple load/hold"; never run.
- Label: MIXED.

### Campaign D -- Nyx reading of the W4 fossils (2026-09-25, cross-seat)
- Question: what does the evolved W4 structure compute; minimal circuit; atlas novelty.
- Result: a saturating positive-feedback latch set by the cue and read at the output; minimal circuit = output
  self-loop + cue edge; GATE/MAX ops inert; set window determined by the zero initial condition. Prediction that the
  latch fails when the cue moves (W16). [HIST]
- Label: REPORTED POSITIVE (descriptive), not re-verified here.

### Campaign E -- Artemis residual reruns on Ares data (2026-09-28..30, cross-seat)
- R-17 (W16 champions: one-sided threshold detectors, mixed storage, float32 tie artefact in s208), R-29 (no first-step
  property predicts carrier choice; premise correction), D002-08A/B/C (W15 plasticity-alone solves W15; MIXED real;
  origin indeterminate). Worker claims; Artemis marks them unverified (#875) or frozen-rule reruns (#1121). [HIST]
- Label: MIXED.

## 9. False-positive / false-negative archaeology

Timeline 1 -- the W4 "GATE+MAX memory mechanism".
claim (09-19, cycle 0: two load-bearing nodes, a GATE and a MAX, accreted over ~13 generations) -> evidence (ablation
40 -> 2.6; fossil replays to 40.0000) -> challenge (cycle 1: GATE+MAX signature 1/10, only the same lineage; carrier
is recurrence; accretion is lineage age) -> correction (Nyx #574: the cycle is 3 nodes through output node 15; GATE and
MAX are inert; minimal circuit has zero hidden nodes) -> current historical status: the function (one-bit latch) is
robust; every structural description issued by Ares about it was wrong in some detail.

Timeline 2 -- "plasticity is never the W4 carrier".
claim (cycle 1: ACT 10/10, plasticity 0/10) -> evidence (config-level three-way ablation) -> challenge (cycle 2
c1_all, edge/SCC-aware: recurrence 7/10, plasticity 4/10, keep 1/10) -> correction (cycle-2 report s5; LEDGER) ->
status: overturned; carrier mix is lineage-dependent. Note the instruments differ, so the two samples are not a clean
replication either way.

Timeline 3 -- "the designated carrier has the better optimum; recurrence wins on basin width".
claim (DESIGN_C2: hand-built keep 33.75 > recurrence 24.56; cycle-2 s0 "evolution took the wide basin, not the higher
peak") -> evidence (basin.json) -> challenge (Artemis FR-001 and R-29: basin.json recurrence reaches 40.0 at weight >=
4) -> correction (not applied in Ares files; Ares itself flagged the basin explanation as post-hoc and hand-wired) ->
status: the "higher peak loses to wider basin" framing is unsupported by Ares's own data; "recurrence wins on speed"
(median ttt 10 vs 30) stands as reported; the cause is open. Additionally the keep sweep is truncated by the 0.98 clip.

Timeline 4 -- shuffled-control floors and D1.
claim (cycle 0: W5 shuffled control "contaminated by imbalance"; W2 shuffled reaches 60-80 by reward reflex) ->
evidence (balance repair improved W5) -> challenge (cycle 2 found D1: reported champions selected on held-out;
shuffled controls 4.22/13.47/1.41/1.50 reported vs 0.00/-2.38/-0.14/0.00 clean) -> correction (cycle 2 only, via
recheck_c2.py) -> status: cycle-0/1 control readings were never re-derived; how much of the cycle-0 "control
contamination" was imbalance and how much was D1 is UNKNOWN.

Timeline 5 -- gate C transplantability.
claim (gates.txt: "GATE C OPEN median_recovery=1.0") -> challenge (own audit: best-of-9 donor) -> correction
(per-pair median 0.02; SHUT) -> status: corrected before publication. A true pre-publication catch.

Timeline 6 -- W15 "redundancy under attack".
claim (cycle-2: lineages build redundancy across recurrence and plasticity) -> challenge (Artemis D001-08: report's
own classifier says MIXED 6/10 = each carrier alone collapses, i.e. co-dependence, REDUNDANT only 1/10) -> correction
(D002-08C: not a cut artifact) -> status: "co-dependence, origin indeterminate"; plasticity alone can solve W15
(D002-08A: 33 W4-evolved PLAST champions median 40 on W15). The only "unpredicted" result is relabelled.

Timeline 7 -- "a small, clean instance of mechanisms no human conceived".
claim (cycle-1 close) -> correction (operator in chat 09-23; LEDGER) -> status: narrowed to "the substrate routed
around the experimenter's design intent". Recurrent state as memory is textbook.

False-negative regimes:
- "No mechanism transfers / no organs" (cycle 0 W8, cycle 1 causal transplant, cycle 2 gate C). The organisms are
  2-17-node analog circuits whose function depends on exact gains and on output-node membership; a hidden-node splice
  cannot move an output self-loop (acknowledged), and even edge-aware swaps re-attach external edges randomly. The
  null is about this substrate's lack of modular interfaces at least as much as about pressures. [CODE-INFERRED]
- "No NEW_CARRIER / nothing outside the enumerated channels" (cycle 1 W13, cycle 2): by construction the substrate has
  exactly three cross-step channels (keep, cycles, plastic W1); a fourth cannot exist except via float artefacts
  (which R-17 then found). This is a closure property of the substrate, not a result about pressures. [CODE-INFERRED]
- "Pressure did nothing" for W11, W3 adaptation, W7 arbitration, W9 Red-Queen machinery: 3 seeds, G=120, <= 8 hidden
  nodes, 2 ticks. With training fitness saturating in a few generations in easy worlds, and no budget sweeps,
  "did nothing" cannot be separated from "too little capacity/time". [CODE-INFERRED]
- Development (W10) "not faster": 4 rules x 4 growth steps at one budget; a single design point. [HIST]

## 10. Research outputs

- ares/ARES_PRESSURE_NOTES.md -- P01-P18 pressure notes (phenomenon, abstraction, toy, confound, falsifier);
  citations explicitly FROM MEMORY (RESUME s9). [INTENT/HIST]
- ares/PRESSURE_CATALOG.json -- 12 built + 6 candidate pressures with falsifiers. [INTENT]
- ares/DESIGN_C0.md, DESIGN_C1.md, DESIGN_C2.md -- three preregistrations with predictions. [INTENT]
- ares/ARES_FIRST_REPORT.md (cycle 0), ARES_CYCLE1_REPORT.md, ARES_CYCLE2_REPORT.md (+ 09-25 annotation). [HIST]
- roles/Ares/REVIEW_PACKET_C0_2026-09-19.txt, _C1_2026-09-21.txt, _C2_2026-09-23.txt -- external packets. [HIST]
- roles/Ares/calibration/LEDGER.md -- 14 self-corrections with changed practice (unusually informative). [CORRECTION]
- roles/Ares/RESUME.md -- state of the science, defects D1-D4, fully specified cycle-3 test. [HIST/INTENT]
- Cross-seat readings: Nyx #574 + roles/Nyx/reports/ARES_W4_READING_2026-09-25_run.txt + nyx/readings/ares_w4_reading.py;
  Artemis selftest R-17, R-21, R-29; dispatch D001-08, D002-08A/B/C; FRONTIER FR-001/FR-002/FR-083/FR-118. [HIST]

## 11. Journals, TODOs, pivots, abandoned branches

- Journals: roles/Ares/journal/2026-09-19, -21, -23, -25 (not read in full; STATUS/RESUME summarise).
- Pivot 1 (09-19): seat with no lane -> chartered sandbox same day.
- Pivot 2 (09-21): operator "validate, compress, exit" -> seat PARKED after cycle 1.
- Pivot 3 (09-23): operator reopened for one focused "attack the mechanism" round with a mechanical stopping rule.
- Pivot 4 (09-25): park across an operator reboot; RESUME/TODO written; s7.1 test sharpened from "re-parameterise
  keep" to "decouple load/hold (v = keep*v + f)".
- Never done: ARES-15/16 pressure combinations (partially touched by W13), ARES-17 new primitives (6 candidates
  never built), ARES-18 POET-like world-setter for W9, ARES-19 novelty-search arm, ARES-24 Worlds Kernel assessment,
  ARES-25 evidence-wiki submission, ARES-26 standing sweep decision, ARES-C2-1 D1 fix at source, ARES-C2-2 retire
  node-only dissect. (TODO.md, BACKLOG_H0H5.md)
- No abandoned branches: single seat branch, merged. [HIST]

## 12. Lens inventory

Lens: "pressure-to-carrier microscope" (Ares sandbox).
- Substrate observed: tiny batched analog dataflow graphs (<= 17 nodes) under a mutation-only GA.
- Organisms: scalar-op graphs with keep, recurrence and Hebbian plasticity as the three possible cross-step carriers.
- Worlds: 16 hand-written episodic toy tasks with present/absent/shuffled modes.
- Pressures: reward-structure pressures plus substrate constraints (exclusion, tax, subsidy, jitter).
- Phenomenon family: which cross-step state carrier evolution recruits under which pressure; substitution when a
  carrier is blocked; accessibility (speed) of supplied primitives.
- Resolving mechanism: edge/SCC-aware carrier cuts (carriers.py), single-carrier arms, exclusion arms, time to
  threshold at 10 seeds.
- Current resolution ceiling: one-bit memory tasks; 10 seeds; time-to-threshold on a 5-generation grid; training
  fitness saturating within ~2.5-6 generations (R-29) so path gradedness is invisible; held-out logged every 5 gens.
- Noise sources: D1 selection bias (still in code), 4-episode training noise, float32 argmax ties, lineage sampling.
- Architectural limitation: the substrate has exactly three cross-step channels and no addressable memory, no
  modularity interface, no composition; worlds demand one bit.
- Reusable: carriers.py (edge/SCC-aware attribution, classify, opportunity/basin measurement); the present/absent/
  shuffled world-mode discipline with per-world balanced seeding; the calibration-ledger record of seven instrument
  defect classes (held-out selection, best-of-N, node-only ablation, first-draw balancing, borrowed thresholds,
  partial "no memory" ablation, rules reading negatives without a positive-control clause).
- Fundamentally toy-grade: the worlds (one-bit latch suffices) and organism size.
- Unknown: whether the "speed not capability" carrier preference survives a decoupled keep (test never run); whether
  basin width or peak or path payoff drives selection (confounded, R-29); whether anything beyond latches/switches
  could appear with larger graphs, more ticks and richer worlds.

## Open questions / unknowns

1. Were any cycle-0/cycle-1 shuffled-control or non-cap numbers materially inflated by D1? Never re-derived.
2. Does keep win when load and hold are decoupled (RESUME s6.1 arm A) -- the only proposed test that separates basin
   from parameterisation? Never run.
3. How much of keep's narrow viable region is due to the 0.98 clip in alter_keep and the sweep's upper bound?
4. Origin of W15 co-dependence (by-product / selected / drift): INDETERMINATE at n=6.
5. Is the s208-type float32 tie artefact present in other carrier-class counts (KEEP in particular)?
6. Did the operator ever decide continue/close? No record found after 09-25.
