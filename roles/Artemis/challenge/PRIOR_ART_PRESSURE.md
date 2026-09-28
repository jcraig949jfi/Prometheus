# PRIOR_ART_PRESSURE -- prior art turned into controls, adversaries, world generators, nulls and estimators

Seat: Artemis (challenge pass). Date: 2026-09-28. Worktree: /home/jcraig/Prometheus-worktrees/artemis-base-role
(branch artemis/challenge-2026-09-28, HEAD a9d5f5f23). Read-only apart from this file. No engine was run and nothing
was committed.

Operator instruction (verbatim): "Prior art must become executable pressure. For each of the strongest prior-art
findings, identify: What experiment would we design differently if we took this paper/result seriously? If the answer
is 'none,' the citation is context, not operational prior art. Label it accordingly. Translate claims into controls,
adversaries, or world generators wherever possible."

Inputs: roles/Artemis/backlog/prior_art/PA_{origin_of_replication, accessibility_landscape, instruments_and_gaming,
memory_and_sagacity}.md; backlog/INDEX.md; threads FR-001 FR-002 FR-010 FR-011 FR-035 FR-038 FR-043 FR-058 FR-059
FR-070 FR-118. Engine code read to make the specs concrete: the three Z80 VMs, ares/, ensorain/lm01/,
ensorain/arc3/suff/, prometheus/cosmos/c3/, prometheus/ananke/, crius/, apollo/, Aphrodite (origin/aphrodite/*),
programs/selective_irreversibility/.

Verification. Citations carry the status given in the PA notes (VERIFIED / BIBLIO-VERIFIED / UNVERIFIED). Two items
were checked for the first time in this pass:
- Avida flag semantics, fetched from github.com/devosoft/avida master through a summarising fetch tool, so the exact
  line numbers still need confirming:
  - avida-core/source/main/cWorld.cc sets
    m_test_on_div = (revert_fatal || revert_neg || revert_neut || revert_pos || revert_taskloss || revert_equals ||
    sterilize_unstable) and
    m_test_sterilize = (sterilize_fatal || sterilize_neg || sterilize_neut || sterilize_pos || sterilize_taskloss).
  - cHardwareBase.cc: Divide_TestFitnessMeasures returns at once unless GetTestOnDivide(). Its test CPU calls
    test_info.UseRandomInputs(). The in-situ block sits in Divide_CheckViable under m_world->GetTestSterilize().
  - Reading: in the stock code, REVERT_* selects the separable test-CPU path and STERILIZE_* selects the in-situ path.
    This corrects the PA W2 reading ("the same option name is consumed by both paths") and fixes FR-070's step-0
    question. Status: VERIFIED-BY-FETCH, UNVERIFIED line numbers.
- Computational-mechanics generator facts, from a search listing:
  - the Golden Mean process is 1-cryptic and the Even process is infinity-cryptic (Mahoney, Ellison, Crutchfield,
    "Information accessibility and cryptic processes", https://arxiv.org/abs/0905.4787);
  - RRXOR has C_mu = 2.2516 bits (https://wiki.cse.ucdavis.edu/cm/rrxor_process);
  - a crypticity primer is at https://arxiv.org/abs/1108.1510.
  - Status: search-snippet level; UNVERIFIED in the full text.

BLIND-LANE NOTICE. This file names the Selective Irreversibility program, so it must not be forwarded whole to
Bellerophon, Nyx, Techne or Aether (programs/selective_irreversibility/DO_NOT_BRIEF.txt @4f5d9bac8). Rows P05, P06,
P07, P13 and P18 are Z80/BEE work. Brief them to Bellerophon only as an SI-free extract.

Counts: 23 OPERATIONAL, 20 CONTEXT.

-----------------------------------------------------------------------------------------------------------------------

## 1. Summary table

Cost classes: XS = desk/analysis only, < 0.5 agent-day; S = < 1 CPU-hour or ~1 agent-day of code; M = CPU-hours plus
1-3 agent-days; L = CPU-days or a new substrate. Host: L = any Linux node (CPU, stdlib/numpy); A = needs Avida C++
build; S = the run belongs to the owning seat (operator gate may apply).

| id | finding (short) | label | artifact type | target engine | cost/host |
|---|---|---|---|---|---|
| P01 | Lange-McKenzie-Tapp 2000 / Bennett 1973,1989: bounded computation is reversible in the same space at exponential time | OPERATIONAL | CONTROL (reversible learner arm) + MEASUREMENT (bits x ops/query frontier) | Ensorain ARC3 PKG-S1 (LM02); LM01 v0.3.2 ops field; SI falsifier A | S / L |
| P02 | Schaper & Louis 2014 arrival of the frequent; Mingard 2021 / Valle-Perez 2019 basin volume | OPERATIONAL | MEASUREMENT (pre-run P(carrier) estimator) + CONTROL (payoff-matched arm) | Ares | S-M / L,S |
| P03 | Wilke et al. 2001 survival of the flattest (needs high mutation) | OPERATIONAL | WORLD-GENERATOR factor (mutation load) | Ares (inside P02) | S / L,S |
| P04 | Lehman et al. 2020 Avida "play dead" + Avida source: test-CPU vs in-situ parent-relative | OPERATIONAL | ADVERSARY (evaluation-isolation) + CONTROL (in-situ arm) | NPE first; Crius, Aphrodite, Apollo, Archaeon WSE; Avida reference | S-M / L,A |
| P05 | Aguera y Arcas et al. 2024: in a real Z80 soup, PUSH/stack copiers arise first | OPERATIONAL | WORLD GENERATOR (stack-route ISA variant) | BEE, NPE, Archaeon VMs | M / L |
| P06 | Cicala et al. 2026: with block copy removed, LDD loops emerge but take over only under task pressure | OPERATIONAL | CONTROL (ISA-level ablation x task coupling 2x2) + seeded probes | BEE, NPE, Archaeon | M / L,S |
| P07 | Knierim et al. 2026: random-walk sampling finds BFF replicators; interaction mostly drives takeover | OPERATIONAL | NULL MODEL (isolated-sampling density) | Archaeon census, BEE, NPE | S / L |
| P08 | Shalizi & Crutchfield 2001 causal states = minimal sufficient statistic | OPERATIONAL | WORLD GENERATOR (known causal-state partition) + scoring rule | Ensorain ARC3 (exists in part), Cosmos C3 adapter, Ananke env | M / L |
| P09 | Still, Sivak, Bell, Crooks 2012: nonpredictive information = dissipation bound | OPERATIONAL | MEASUREMENT (label-free I_mem - I_pred) | runs on P08 worlds; Ananke M2 | S / L |
| P10 | Bialek, Nemenman, Tishby 2001: predictive information I_pred(T) classifies worlds | OPERATIONAL | NULL WORLD + generator axis (I_pred growth class) | P08 family; SI falsifiers | XS / L |
| P11 | Kolchinsky et al. 2019: IB degenerate when relevance is deterministic | OPERATIONAL | CONTROL (stochastic-relevance knob) | SI falsifier A (NPE reversible core), P08 | XS / L |
| P12 | Isele & Cosgun 2018; Karamcheti et al. 2021: surprise retains noise; reservoir = distribution matching | OPERATIONAL | CONTROL (learning-progress arm) + dose-response | LM01 dev fixture (not the campaign), ARC3 | S / L |
| P13 | Eigen 1971 error threshold (with Wilke 2001) | OPERATIONAL | MEASUREMENT (effective-rate threshold predicts conserved length) | NPE C-CORE, BEE | S / L |
| P14 | Knowles & Watson 2002; Rothlauf 2006: neutrality helps only when biased | OPERATIONAL | CONTROL (biased vs unbiased redundancy) | any "add neutral networks" repair (H-D3-61; Crius-like) | S / L |
| P15 | Stanley & Miikkulainen 2002 NEAT evolves XOR (complexify + protect innovation) | OPERATIONAL | CONTROL (positive-control world + protection arm) | Ananke PTE XOR | S-M / L,S |
| P16 | Watson, Hornby, Pollack 1998 HIFF | OPERATIONAL | WORLD GENERATOR (known-answer calibration) | FR-003 accessibility rulers | S / L |
| P17 | Weissman et al. 2009 valley/plateau crossing times | OPERATIONAL | NULL MODEL (predicted discovery time vs plateau length, N) | Crius-like substrates, FR-003 | S / L |
| P18 | Jonas & Kording 2017; El-Brolosy & Stainier 2017; Hall 2004 | OPERATIONAL | CONTROL (ISA-level knockout + re-creation block + root intervention) | BEE, NPE, Archaeon knockouts | S / L |
| P19 | Kepler injection-recovery (Christiansen et al.); LIGO blind injection GW100916 | OPERATIONAL | MEASUREMENT (completeness curve) + ADVERSARY (blind plant) | Cosmos C3, Ananke C1b nulls, LM01 E6 | M / L,S |
| P20 | Gross & Vitells 2010 trial factor; Gao et al. 2023 best-of-n overoptimisation | OPERATIONAL | CONTROL (trial-factor-corrected held-out) | Ares D1, Apollo NSGA | XS-S / L |
| P21 | Sutter et al. 2025 non-linear representation dilemma | OPERATIONAL | MEASUREMENT (IIA vs alignment-map complexity) | Cosmos C3 P1 on foreign specimens (FR-035) | S / L |
| P22 | Berlot-Attwell et al. 2024/25; Sesterhenn et al. 2025: library gains vanish at matched compute | OPERATIONAL | CONTROL (compute-matched no-library arm + usage census + leave-one-out) | Aphrodite S4 / FR-043; Archaeon campaign2 | XS-M / L,S |
| P23 | Ficici & Pollack 1998; Watson & Pollack 2001: coevolved evaluators collude or cycle | OPERATIONAL | CONTROL (frozen hall-of-fame reference) | Ares run_coevo (W9); any co-evolved selector | S / L |
| C01-C20 | see s4 | CONTEXT | none | -- | -- |

-----------------------------------------------------------------------------------------------------------------------

## 2. OPERATIONAL rows: specifications

Each row gives: the finding and the FR/H ids it bears on; the artifact; the engine and the file to touch or wrap;
the inputs; the expected behaviour if the claim holds and if it fails; which existing experiment would have been
designed differently; cost and host.

### P01. Lange-McKenzie-Tapp / Bennett -> a REVERSIBLE LEARNER arm and a (bits, ops/query) frontier  [mandatory 1]

Finding. Lange, McKenzie, Tapp (2000) "Reversible space equals deterministic space", JCSS 60(2):354
(https://www.sciencedirect.com/science/article/pii/S0022000099916720, web-checked in PA). Any S-space deterministic
computation has a reversible simulation in O(S) space, at exponential time. Bennett (1973, 1989;
compute-copy-uncompute, pebbling) does it in polynomial time at larger space (UNVERIFIED).

Bears on: H-D1-38, H-D1-41, H-D3-39; FR-036, FR-037, FR-039; SI FALSIFIERS row A; memo G1.

Why it changes an experiment. If only bytes are priced, a bounded agent can avoid elimination by theorem, so the SI
"requires" clause is non-trivial only on a time-space frontier.

The program already has an empirical instance of this: Ensorain's ARC3 PKG-S1 pilot, finding 1
(ensorain/arc3/suff/RESULTS_S1_PILOT.md @bef057f44). Storage compression (STAT(k)) and a verbatim store summarised at
query time (VERB_SUM(B,k), which is compute-copy-uncompute at the agent level) have IDENTICAL excess log-loss once
B >= T. The pilot already records query_ops per learner (ensorain/arc3/suff/learners.py @bef057f44: STAT
query_ops = k; VERB_SUM query_ops = B*k). Nobody has yet read those numbers as a frontier.

Artifact (CONTROL + MEASUREMENT), in two places, both respecting the operator's 2026-09-28 LM01 ruling
(roles/Ensorain/prompts/2026-09-28_lm01_v032_amend/01_OPERATOR_V032_AMEND_verbatim.md @c2b507e9e: no HMM or
causal-state retrofit into LM01; the three compression loci are recorded).

(a) ARC3 / LM02: new learners in ensorain/arc3/suff/learners.py.
- REV_LOG: a Bennett-style reversible learner. It keeps the full verbatim history, which is an injective,
  reversible record, and at each query it recomputes the order-k statistic from the whole log. It then uncomputes:
  nothing persists except the log. Charge bits = T, query_ops = T*k.
- REV_PEBBLE(S): an LMT-style variant. It keeps a checkpoint set of S symbols plus a reversible recomputation schedule
  (a pebble game over the log), with query_ops = O(T^(1+eps)) or 2^O(S) as the schedule dictates. Implement it
  analytically: identical predictions to REV_LOG, charged ops per the pebble schedule.
- CS_TRACK: the causal-state tracker (1 bit on the Even process). It is the irreversible, selective arm.

Procedure:
- Worlds: W2 (order 3), Even, golden mean, W5 key-value. Fix a per-query op budget Q in {8, 64, 512, 4096} and sweep
  T in {1e3, 4e3, 1.6e4, 6.4e4}.
- For each (learner, Q, T): if the learner's query_ops > Q, it must truncate. REV_LOG then becomes VERB_SUM with
  B = Q/k, i.e. a lossy window: countermodel-C territory.
- Report excess log-loss vs exact Bayes on the (persistent bits, query_ops) plane.

If the claim holds (the law is a time-space claim): at fixed Q, the reversible and lossless arms fall off the
competence frontier past a crossover T* ~ Q/k, while CS_TRACK (Even) and STAT(k_true) (W2) stay at excess ~0 with
O(1) ops.

Against the claim: some reversible or lossless arm stays on the frontier at fixed Q as T grows. Test this with
equivalence at the declared .02 tolerance plus the pilot's positive control. That is a real countermodel-A signal
with time priced.

W5 is the known exception: there, exact history is the sufficient statistic (pilot finding 5). It must show NO
crossover. If a crossover appears on W5, the harness is wrong.

(b) LM01 v0.3.2: measurement only, which the amendment's item 6 permits ("query/readout computation" locus).
- Add ops_per_query = meter.ops / meter.n_queries as a recorded field for every arm (ensorain/lm01/accounting.py
  @e94fe0d5e, class Meter). Report L-R (arms.py:140, a per-query refit) separately from L-K.
- No new arm and no verdict change. Report the frontier descriptively.

(c) SI FALSIFIERS row A (programs/selective_irreversibility/FALSIFIERS.md, 20:37Z row) must state Q. As written, "a
bounded reversible core ... whose RANDOM export policy keeps held-out competence" is satisfiable by theorem when time
is free.

Would have been designed differently:
- FALSIFIERS.md row A and memo G1 (programs/selective_irreversibility @4f5d9bac8) would carry an ops budget.
- The Harmonia s12 freeze request would have priced ops. The request is recorded as NOT ACTIONED:
  roles/Harmonia/journal/2026-09-27_m2-475d761f.md:69-74 @c17d4c477. The vehicle is therefore now LM02 and the ARC3
  ladder, not the freeze.
- LM01 PREREG s5 (ensorain/PREREG_WTP_LM01.md @768ea8ce9) meters ops but makes no per-query comparison.

Cost: S. About 1 day to add three learners and a frontier plot; the pilot runtime was 93 s on M2. Host: any Linux
node (numpy). It belongs to Ensorain's ARC3 lane or a neutral seat.

### P02. Arrival of the frequent / Mingard basin volume -> pre-run basin-volume estimate + payoff-matched arm for Ares  [mandatory 2]

Finding.
- Schaper & Louis (2014) PLoS ONE 9:e86635: frequent phenotypes fix before fitter ones arrive.
- Mingard et al. (2021) JMLR 22(79), arXiv:2006.15191: the optimiser's output frequency tracks the prior basin volume
  V_B(f) estimated by random parameter sampling.
- Valle-Perez et al. (2019).
- All VERIFIED in PA_accessibility.

Bears on: H-D3-56, H-D3-57, H-D3-64, H-D1-23; FR-001, FR-002, FR-083.

Why it changes an experiment. Ares states a design rule ("a supplied primitive is available when its viable region is
wide", ares/ARES_CYCLE2_REPORT.md s4.5 @3f68be2b9). It never measured the quantity the literature says predicts
recruitment: the random-genome prior P(carrier sufficient).
- What does exist: basin.json is hand-wired, one-node, and has no committed generator script (the audit found no
  viable_frac in any ares/*.py).
- carriers.opportunity() (ares/carriers.py:156-187 @ab137f52b) measures one-mutation creation, not volume.
- baselines.py only scores gen-0 fitness.

Artifact 1 (MEASUREMENT, pre-run, recorded before any GA run): estimate_prior(cfg, world, n=10_000).
- New file ares/prior_volume.py; read-only use of substrate and carriers.
- Sample n genomes from the GA's own initial distribution (search.run's init, ares/search.py:222 @ab137f52b). Then
  apply the same mutation kernel for m in {0, 5, 20} random steps, to also estimate the neutral-walk-reachable volume.
- Score each genome on W4 with the cycle-2 held-out seeds, and run carrier_ablation + classify (carriers.py:93-148).
- Estimates:
  - P_suff(c) = the fraction of genomes whose score is >= 50% of best with carrier c load-bearing (the same viability
    threshold as basin.json);
  - P_viable_region(c) = the fraction of each carrier's parameter draws inside its viable region.
- Record P_suff for keep, recur and plast per arm (c1_all, c3_keep_reachable, and the ARM A/B cells below) in a JSON
  committed before the GA runs.

Artifact 2 (CONTROL, payoff-matched arm).
- The ARM A rule (decoupled leak v = keep*v + f; roles/Ares/RESUME.md:124-145 @3f68be2b9) is implemented as a Config
  flag in ares/substrate.py:413.
- Also add a gain cap g_cap on the keep node's input so that its single-node peak on W4 equals 33.75 (the cycle-2
  keep peak). Find g_cap by bisection on the existing basin sweep before any GA.
- Cells, 10 seeds each (201-210), P=128, G=120, EPS=4:
  - A0 original;
  - A1 decoupled, uncapped (the peak may reach 40);
  - A2 decoupled + g_cap (peak 33.75, wider basin);
  - A3 = the keep_mut_sigma=1.5 arrival subsidy (c3), as the already-run reference.

Expected under arrival/basin (the claim):
- keep load-bearing share tracks P_suff(keep) across A0 -> A2 at FIXED peak 33.75;
- A2 >= 5/10 while A0 stays at 1-2/10;
- Spearman(P_suff, share) > 0 across all cells.

Against (payoff of the first carrier decides):
- A2 stays at <= 2/10 and only A1 (peak 40) flips;
- P_suff does not predict share better than current fitness does. That is Herakles K7:
  herakles/HERAKLES_HISTORICAL_COLLIDER_V0/ACCESSIBILITY_WITHOUT_ACQUISITION_NEGATIVES.jsonl @2a5ac0117.
- In that case FR-001 should read "intermediate payoff".

Would have been designed differently:
- Ares cycle 2 (ares/DESIGN_C2.md @ab137f52b; runs ares/runs/sweep_c2 @1dde117f7) would have recorded P_suff before
  the c3 falsification arm, so c3's failed prediction (">= 3/10") would have had a predicted value to test against.
- basin.json would have been produced by committed code, not by hand.

Cost: S for estimate_prior (1e4 genomes x 32 held-out episodes; minutes of numpy). M for 40 GA runs (the cycle-2 rate
was 190 runs; roughly an hour on one node, UNVERIFIED). Host: any Linux node. The runs belong to Ares, which is
PARKED, so they are operator-gated. The estimator alone is not.

### P03. Wilke 2001 survival of the flattest -> mutation-load factor inside P02

Finding. Wilke, Wang, Ofria, Lenski, Adami (2001) Nature 412:331 (VERIFIED): robust genotypes beat fast ones only at
high mutation rate.

Bears on: H-D3-56, H-D3-57; FR-002.

Artifact (WORLD-GENERATOR factor). In ares/substrate.py mutate_one (L200-205 @1dde117f7), n_mut = 1 + Poisson(lam),
with lam in {1 (baseline), 4}. Cross it with A0/A2 of P02: a 2x2, 10 seeds per cell.

Under flatness: the keep-share gain from A0 -> A2 appears mainly at lam = 4.
Under arrival: it appears at both rates.
Under payoff: it appears at neither.

Also record the recurrence share under lam = 4. The flat, saturating recur basin predicts that recurrence gains at
high load. If keep gains instead, "wide basin" is not the operative property.

Would have been designed differently: the Ares cycle-2 prereg varied opportunity (keep_mut_weight 8x) and
reachability (sigma 1.5) but never mutation load, so it cannot separate arrival from flatness (PA_accessibility item 3).

Cost: S-M (20 extra GA runs). Host: L; the runs are Ares's (S).

### P04. Avida test-CPU vs in-situ parent-relative evaluation -> EVALUATION-ISOLATION ADVERSARY  [mandatory 3]

Finding.
- Lehman, Clune, Misevic et al. (2020) Artificial Life 26(2):274 (VERIFIED record). Avida organisms detected the
  isolated test environment and "played dead", then defeated randomised test inputs by acting probabilistically.
  Only in-situ, lineage-relative elimination worked.
- Avida source (see the Verification note): REVERT_* > 0 routes offspring through a separable test CPU with random
  inputs. STERILIZE_* > 0 routes through an in-situ comparison with the parent.

Bears on: H-D5-39, H-D1-36, H-D5-38; FR-070, FR-021.

Which Prometheus engines have a separable evaluation episode (audit this pass; path@sha):

| engine | evaluation used for SELECTION? | where | distinguishable from normal life? |
|---|---|---|---|
| NPE (Nestor z80atlas) | YES. Competence gates ALLOC, pair interaction, energy, reaping | roles/Nestor/campaigns/z80atlas-2026-09-19/world.py:803-824 (_validate) -> tasks.py:117-166 (score) @aa5833488; gating world.py:424-431,577-582,680-700 | YES. Fresh 512-byte arena, world ops disabled, fresh registers (in-soup registers PERSIST, z8.py:159,456), budget 140, task inputs present only here |
| Crius | YES. mu+lambda on search streams; qualify/gate namespaces | crius/search.py:173-207 @96d299784; crius/qualify.py @095116eed | YES in principle. The qual namespace uses chain_repeat3/chain4, while search/gate use chain_repeat2/3 (crius/tasks_c1.py:71-78 @97af44f88); programs INPUT task fields |
| Aphrodite | YES. fair.select on dev cells; tribunal | roles/Aphrodite/engine/fair.py:170-190 @1e79fbc09; improver.py:51-70 @6e602dffc | YES in principle. The prompt carries the family name (md_* vs mt_*); extrapolation lengths 20-60 vs 4-9. The worker currently parses digits only |
| Apollo | YES, and it leaks. The held-out margin is written to `generalization`, one of the 6 NSGA objectives | apollo/src/apollo.py:1006-1023 @3ebdad8b4; apollo/src/fitness.py:8,36 @dd42cb103 | The held-out set is fixed (seeds 42/100/200) and refreshed every 500 generations |
| Archaeon WSE | YES. Tournament on the train family; held-out families separate | archaeon/wse/evolve.py:266-271 @b50f75b7c; worlds.py:416-420 @f6e18b5c7 | Partly. The heldout_vocab / changed knobs differ by design |
| Ares | Train-episode selection; champion = argmax on held-out (defect D1) | ares/search.py:236-237,292-294 @ab137f52b | NO. Same observations and dynamics; the seed is never observed; there is no life outside episodes |
| Ananke PTE | Selection on train worlds; held-out evaluated once | prometheus/ananke/search.py:81-135 @2c53c82eb | NO. Identical physics |
| BEE z80atlas | NO. Selection is in-life (energy/copy resource); the competence panel is measurement only | prometheus/z80atlas/coupling.py:153-176 @c9bed96de; tasks.py:150-159 @f8ed38944 | The panel is distinguishable but does not select |
| Archaeon z80atlas | NO. The in-soup task is scored over 3 cases; the probes are measurement only | archaeon/z80atlas/engine.py:150-156,341-349,419-432 @29b03fd80 | measurement only |
| Cosmos C3, Ensorain LM01, Herakles EvCA, Aether | NO selection of agents by the evaluation (certificates or fixed arms), or no evaluation at all | -- | LM01's query phase is structurally distinct but its arms are fixed algorithms |

So there are five engines where selection reads a separable episode: NPE, Crius, Aphrodite, Apollo and Archaeon WSE.
- In three of them the episode is distinguishable in principle: NPE strongly, Crius and Aphrodite weakly.
- NPE is the Avida test-CPU design almost exactly: reproduction is gated by a score earned only in an isolated
  arena the organism never lives in.
- BEE is the in-situ design (task scored on the same in-soup execution, prometheus/z80atlas/world.py:419 @c9bed96de).
  The two engines are therefore a ready natural contrast.

Artifact A (ADVERSARY, NPE; the highest value). A planted "test-conditional" specimen plus a context-swap
re-validation.
- (i) Hand-write an NPE genome G_tc. On entry it tests a feature that differs between _validate and soup life. The
  cheapest such feature: all registers zero, since in the soup registers persist across slices (z8.py:159,456).
  - Validation branch: runs the task code (reuse a competent committed donor's task block).
  - Soup branch: jumps to a copy loop (LDIR, as in _replicator_bytes, world.py:214-241) without the task code.
  - Seed G_tc and an honest control G_h (the same bytes with the branch removed: task and copy both unconditional)
    into a MID-tier pair-tape world. Seed at equal count, 10 seeds.
  - Under the claim (a separable episode is a target), G_tc out-reproduces G_h. It spends no soup steps on the task
    yet holds identical competence, so gating pays it.
  - Against the claim, no difference. Then the gate is not exploitable at this budget, and the soup task was never a
    cost.
- (ii) MEASUREMENT on committed runs: re-score every competent lineage's genome under a CONTEXT-SWAPPED validation.
  Run tasks.score with the registers, PC and arena size that the genome had at its last soup slice (the observatory
  keeps genomes; the register state may need a replay). The statistic is the fraction of lineages whose competence
  drops by more than 50% under the swap. Any non-zero fraction means NPE "competence" is partly test-conditional
  behaviour.
- (iii) CONTROL arm, the in-situ design: compute competence from task inputs presented DURING soup slices (BEE-style
  IN_A at a memory-mapped port), compared with the parent's in-situ score (Avida TestSterilize analogue). Compare
  time-to-first-G_tc-like lineage (a lineage whose swap drop > 50%) across the two arms.

Artifact B (reference, external). FR-070 T6 on stock Avida, with the arms now specified by flag:
- (1) REVERT_BENEFICIAL = 1.0, STERILIZE_* = 0, with UseRandomInputs patched out (fixed-input test CPU);
- (2) REVERT_BENEFICIAL = 1.0, stock (random-input test CPU);
- (3) STERILIZE_BENEFICIAL = 1.0, REVERT_* = 0 (in-situ).
- 20 seeds per arm. Outcome: updates to the first lineage that out-replicates its ancestor by more than 10%
  (Kaplan-Meier).
- Predicted ordering from the anecdote: escape time (1) < (2) << (3).

Artifact C (grader-feature scans, XS):
- Crius: does any evolved program read a task field whose distribution differs between the qual and search namespaces
  (chain length)? Check this by re-scoring qualifiers on a search-distribution copy of the qual tasks.
- Aphrodite: pre-register that the worker must stay name-blind (a unit test asserting that improver.search ignores
  the family string) before any LLM-in-the-loop worker is authorised.
- Apollo: see P20.

Would have been designed differently:
- The NPE z80atlas grammar (roles/Nestor/campaigns/z80atlas-2026-09-19/grammar.py @aa5833488) would have run
  competence in situ, or randomised the validation context to match soup state.
- H-D5-39's proposal would have named the in-situ path (STERILIZE_*) and not the test CPU (REVERT_*).
- FR-070 step 0 is now answered.

Cost: A(i) S (one hand-written genome, 20 runs of an existing world). A(ii) S-M (replay needed for register state).
A(iii) M (new grammar factor). B M plus an Avida build. Host: L for NPE (pure Python), A for Avida. The runs are
Nestor's.

### P05. Aguera y Arcas et al. 2024: PUSH/stack copiers first -> STACK-ROUTE ISA VARIANT  [mandatory 4, part 1]

Finding. Aguera y Arcas et al. (2024) "Computational Life", arXiv:2406.19108 s3.3 (VERIFIED). In a Z80 soup of
16-byte programs, concatenated in pairs and addressed modulo 32, "early generations use stack-based copy mechanism".
SP starts at the end of the address space, so PUSH writes into the partner. LDIR/LDDR replicators replace these
later.

Bears on: H-D2-01, H-D2-02, H-D2-08, H-D1-35; FR-010, FR-011, FR-013.

What opcode support is missing (audit this pass, with line numbers):

- BEE, prometheus/z80atlas/vm.py @b2ee19847 (own ISA, not Z80 byte values).
  - No SP, PUSH, POP, CALL, RET, LD SP.
  - No 16-bit register pairs or 16-bit immediates.
  - Registers zeroed per execute() (vm.py:96-97).
  - Addresses wrap MOD 256, never mod 2L (vm.py:98,120-125). In PAIR_EXECUTION the VM is called with 2L, so its
    "neighbour window" is [128,256), which overlaps the I/O region (world.py:366-370 @c9bed96de).
  - 0xC5 and 0xED are undefined (NOP).
- Archaeon, archaeon/z80atlas/vm.py @c7610ea19 (dense own ISA: op = byte & 31).
  - No SP, PUSH, POP, CALL, RET, 16-bit pairs.
  - Own tape [0,G) and neighbour [128,128+G) are NOT contiguous. Writes to the gap are refused as illegal
    (vm.py:92-98).
  - Wrap is mod 256. Registers are reset per case.
  - Everything is missing for this route.
- NPE, roles/Nestor/campaigns/z80atlas-2026-09-19/z8.py @aa5833488 (real Z80 bytes).
  - 0x31 LD SP,nn consumes 3 bytes and does nothing (z8.py:276-285).
  - PUSH/POP (C5 D5 E5 F5 / C1 D1 E1 F1), CALL, RET and RST are absent; unknown bytes are a 1-byte NOP
    (z8.py:451-452).
  - The pair-tape world concatenates A at 0 and B at n in a tape of size pow2(2L). That is exactly 2L for L = 32 and
    64, so mod-2L wrap already holds there (world.py:584-587).
  - Registers persist across slices and are not reset per interaction.
  - A and B run sequentially, one slice each (world.py:589-593).
  - COLLISION: the C-DENSE-COPY experiment aliased 0xE5 (PUSH HL on a real Z80) to LDIR and 0xE7 to LDDR
    (roles/Nestor/campaigns/npe-w1-donor-discovery-2026-09-26/x_dd_dense_copy/run_dc.py:46). A PUSH route cannot
    share that build.

Artifact (WORLD GENERATOR; an ISA variant behind a flag in each VM; default off so that past results are unchanged).

- NPE (smallest change; real Z80 semantics).
  - Add register SP (16-bit).
  - LD SP,nn loads it.
  - PUSH rr (C5/D5/E5/F5): SP -= 1; mem[SP] = hi; SP -= 1; mem[SP] = lo, with addresses mod tape size.
  - POP rr (C1/D1/E1/F1).
  - Optional: CALL nn (CD) and RET (C9), since call/ret chains also write through SP.
  - Per pair interaction, reset registers, PC and SP to SP = 0 (so the first PUSH writes at 2L-1, the end of partner
    B), only in the stack-variant world.
  - Flag: ops mask bit STACK in grammar.py.
  - Remove the 0xE5/0xE7 dense alias in this variant.
- BEE.
  - Add pairs BC/DE (or reuse A:B), a 16-bit immediate load, register SP initialised to 2L per interaction, PUSH/POP,
    and an option wrap = "2L" in execute() (address & (2L-1)).
  - Pick unused byte values for the new ops and record the mapping.
- Archaeon.
  - Needs layout change first: neighbour contiguous at [G,2G), wrap mod 2G.
  - Then SP and PUSH as op codes on currently-NOP values (0 or 30). This alters the decode density, so declare it as
    a new substrate, "z80stack".

Seeded probe (before any random soup). The Load-Push replicator: the W1/W2 "01 nn nn C5" family (LD BC,nn; PUSH BC
repeated, so the program pushes its own bytes). Write one per VM in its own encoding. Place it in tape A with a random
tape B. Run one interaction and measure the fidelity of B vs A over the pushed span. Then run a 50-tick soup seeded
with 1 copy.
- Replicates when seeded but never arises in random soups: a discovery barrier (encoding length, H-D2-08).
- Cannot replicate even when seeded: the ISA forbids the route. That is our design choice, not a law.

Random-soup test: the same world, with the stack variant on and block copy (LDIR/LDDR/LDI/COPY) REMOVED at decode.
Measure time to first replicator with an information criterion (FR-011: dominant-byte share < 0.8).
- W1 predicts stack copiers appear.
- If none appear in 300 x 500 ticks (the BEE P8 scale), the Z80 prior-art claim does not transfer to these
  frame/layout choices. Report which factor blocks it: layout, wrap or reset.

Would have been designed differently:
- BEE P8 (roles/Bellerophon/forensics_2026-09-23/GROUNDING_REPORT.md:78-84 @3efdacf7e) concluded replication is
  "reachable ONLY through LDIR plus the neutral undefined-byte slide" from an ISA with no stack route. It should have
  stated "in this ISA".
- Archaeon's COPIER-CENSUS ruling "Copying requires the COPY primitive in this bench"
  (archaeon/z80atlas/pivot/Z80ATLAS_RULINGS_FOLLOWUP_REVIEW_2026-09-24.md:227 @863d34a55) is correctly scoped, but
  Block D's "design law" (FR-010) is not.

Cost: M (about 1-2 days of code per VM; the NPE flag is the smallest). Seeded probes are minutes. Random soups are
CPU-hours. Host: L (all three VMs are pure Python). The runs belong to the owning seats. BEE work goes to Bellerophon
as an SI-free brief.

### P06. Cicala et al. 2026: LDD loops when block copy is removed, takeover only under task pressure -> ISA-ablation x task-coupling 2x2 with seeded probes  [mandatory 4, part 2]

Finding. Cicala, Niklasson, Randazzo et al. (2026) "Coevolution of self-replication and function in a digital
primordial soup", arXiv:2607.09211 (VERIFIED; the design ancestor of the 2026-09-19 directive).
- Replicator families: Load-Push, LDIR, LDD loops; robustness is LDIR >> LDD >> Load-Push.
- With block copy absent, LDD-based replication emerges "only under task pressure; without it, the transition from
  Load-Push ... fails to complete within ten million epochs".
- Hard-wired copy solves more tasks but keeps lower ancestor entropy.

Bears on: H-D2-02, H-D2-04, H-D2-33, H-D2-41, H-D2-45, H-D1-35, H-D1-47; FR-011, FR-015, FR-021.

What is missing for an LDD byte-loop route (audit):
- BEE: no LDD/LDDR and no DEC S / DEC T (only increments). LDI decrements C but sets no flag (vm.py:158). Wrap mod 256
  sends a decremented pointer into the I/O area. An ascending LDI + JR/DJNZ loop is already possible.
- Archaeon: no descending copy op. A manual descending loop (LD A,(B); LD (C),A; DEC B; DEC C; DJNZ) is expressible,
  but a pointer decremented below 0 lands at 255, outside the window.
- NPE: LDI (ED A0) and LDD (ED A8) are 2-byte no-ops (z8.py:449). DJNZ (0x10) is a NOP. LDDR exists as a block op. A
  manual loop (LD A,(HL); LD (DE),A; DEC HL; DEC DE; DEC BC; LD A,B; OR C; JR NZ) is expressible today.

Artifact (CONTROL; ISA-level ablation, not byte NOPing, per P18).

Factor 1, route available (decode-level):
- BLOCK: LDIR/LDDR/COPYALL on.
- BYTE: block ops removed at decode; LDI/LDD (added: ED A0/ED A8 in NPE; new single-byte ops in BEE; a
  decrementing COPY variant in Archaeon) on.
- STACK: P05 variant, with block and byte copy ops removed.
- NONE: all copy ops removed, only LD (r),A-style stores.

Factor 2, task coupling:
- OFF: the task causally inert, as in BEE P8 (GROUNDING_REPORT.md:51-55).
- ON: BEE physics v3 coupling (prometheus/z80atlas/coupling.py @c9bed96de pays copy resource for correct output);
  NPE competence gating (but see P04); Archaeon competence-gated interaction.

Seeded probes in every cell: hand-written LDIR, LDD-loop and Load-Push replicators (extend
roles/Nestor/.../world.py:214-241 _replicator_bytes, prometheus/z80atlas/vm.py:233-239 replicator(),
archaeon/z80atlas/engine.py:176-190 seeded_replicator). Seed each at 1% of the soup.
- Readouts: establishment (fraction of the soup at 1,000 ticks); persistence; cargo retained, i.e. the task bytes
  inside the replicator.

Random-origin cells: 300 soups x 500 ticks per cell (the BEE P8 scale). Readouts: time to first informative replicator
and time to takeover (> 50% of tapes of that route).

Under the claim (transfer of W2):
- BYTE cells produce byte-loop replicators;
- takeover occurs only with coupling ON;
- the seeded LDD loop establishes under ON and fails under OFF;
- NONE produces only homopolymer "painting" (the NPE BYTEWISE finding, FR-011).

Against:
- Zero informative byte-loop replicators under both couplings, while the seeded LDD loop DOES replicate: then the Z80
  engines' heredity is primitive-bound at the discovery stage (encoding length).
- Or the seeded loop cannot replicate: an ISA or layout gate.

Would have been designed differently:
- BEE P8 ran "LDIR off" as a byte NOP, with the task inert.
- NPE's copy_primitive factor BYTEWISE (grammar.py:64-67 @aa5833488) also removed LDI, so it tested NONE, not BYTE.
- The Archaeon census z80 substrate (c5067fac6) is also NONE plus manual loads.
- None of the three crossed route with task coupling, which is the one variable W2 says decides takeover.

Cost: M-L (the ISA flags are shared with P05; 8 cells x 300 soups per engine is CPU-hours to a day). Host: L; the runs
belong to the seats.

### P07. Knierim et al. 2026: origin is a lottery on byte density; interaction drives takeover -> ISOLATED-SAMPLING NULL

Finding. Knierim, Versari, Obryk, Aguera y Arcas, Saurous (2026) "BFF: Simple explanations for complex phenomena",
arXiv:2607.01483 (VERIFIED).
- A mutation random walk finds BFF replicators about as easily as paired interaction.
- A tuned byte distribution needs 9.4e4 samples vs 2.9e7 uniform.
- Capping ancestry prevents takeover, not emergence.

Bears on: H-D2-06, H-D2-07, H-D2-08, H-D2-21, H-D2-28; FR-012, FR-013, FR-017.

Artifact (NULL MODEL): isolated_density(vm, byte_dist, n).
- Draw n isolated tapes from the soup's own byte distribution at the first-replicator epoch. That means the
  empirical distribution of the soup at that time, not uniform.
- Test each with the engine's own copier classifier against a fresh random partner. Archaeon already has
  archaeon/z80atlas/census/copier_census.py:82-91 @b48245002; wrap the BEE and NPE detectors the same way.
- Predicted first-appearance time under the lottery = 1 / (density x interactions per tick).

Readouts per engine: observed first-appearance time vs the null's prediction; and separately, time from first
appearance to takeover.
- Under the claim: observed ~ predicted, and the null cannot predict takeover. Origin is a lottery, and interaction or
  construction matters only for establishment, so FR-012's "lottery or construction" splits into two answers.
- Against: observed << predicted. Soup history is building replicators faster than sampling ("construction"). This is
  the first quantitative evidence for H-D2-07 in any of the three engines.

Would have been designed differently: the Archaeon census (1e7 uniform tapes, COPIER-CENSUS-01 c5067fac6) sampled
UNIFORM bytes, so its 9.6e-6 is not the density the soup actually faced. BEE's 8/300 origin rate has no null at all.

Cost: S (1e6-1e7 isolated evaluations per engine; the Archaeon census ran at that scale). Host: L.

### P08. Causal states / epsilon-machines -> WORLD GENERATOR with a KNOWN causal-state partition  [mandatory 5]

Finding.
- Shalizi & Crutchfield (2001) J Stat Phys 104:817 (UNVERIFIED in PA, canonical): causal states are the unique
  minimal sufficient statistic of the past for the future.
- Mahoney, Ellison, Crutchfield (2009) arXiv:0905.4787 and the crypticity primer arXiv:1108.1510 (search-verified):
  the generator's state can hide from the observer (crypticity).
- Li, Walsh, Littman (2006): prediction-sufficient and control-sufficient abstractions differ.

Bears on: H-D1-42, H-D1-44, H-D1-68, H-D3-45, H-D3-41, H-D3-66, H-D5-24; FR-035, FR-036, FR-038, FR-039, FR-040,
FR-041.

What exists. Ensorain ARC3 already has an exact-Bayes HMM world class with even_process, golden_mean and
simple_nonunifilar_source (ensorain/arc3/suff/worlds.py:89-146 @bef057f44). It carries a causal-state COUNT, not a
partition, and scores learners by excess log-loss, not by which distinctions they keep. It is sequence-prediction
only, with no cue/query demand, no control, and no export to Cosmos or Ananke.

Artifact (WORLD GENERATOR family "CSG", computational-mechanics ground truth). New module ensorain/arc3/suff/csg.py
(or a neutral prometheus/common/csg.py so Cosmos and Ananke can import it). Parameters:
- alphabet K in {2, 4};
- causal-state count n in {2, 3, 5, 8};
- unifilar (exact finite partition) vs nonunifilar (belief-state generator; the partition is infinite, so use
  truncated mixed states at depth d);
- presentation redundancy r in {0, 1, 2}: each causal state is split into r+1 generator states with identical
  futures but different internal labels. The generator state then carries IRRELEVANT distinctions by construction;
- crypticity class: 0-cryptic (golden-mean-like), k-cryptic, infinity-cryptic (Even-like), plus RRXOR (C_mu = 2.2516
  bits, search-verified);
- noise eps: symbol-flip probability (see P11);
- action channel (optional, the control variant): an action a_t picks one of two emission matrices. The control-
  relevant partition (states that differ in optimal action value) is computed separately from the predictive
  partition, and the generator is constructed so that the two differ.

The ground truth the generator emits (the answer key):
- For every history prefix, the causal-state label CS(h), computed by Moore-style minimisation on predictive
  equivalence of the generator (exact for unifilar; no library needed).
- The generator-state label GS(h) (finer than CS when r > 0).
- The Relevant / Expired / Never-relevant class of any planted distinction:
  - R: the distinction changes CS now;
  - E: it changed CS at some earlier time and no longer does (after synchronisation);
  - N: it changes GS but never CS.
- C_mu, h_mu, excess entropy E and crypticity chi, computed exactly.

Scoring rule for any specimen with a readable memory M_t (a Cosmos full_state, an LM02 learner's state, an Ananke
register file plus in-flight packets):
- estimate H(CS | M) = the relevant information LOST (coarsening);
- estimate H(M | CS) restricted to GS-distinctions = the irrelevant distinctions KEPT (refinement);
- both come from plug-in counts over 1e4-1e5 test histories, with a shuffled-label floor.

Classify:
- MATCH: both near floor;
- COARSE: loss > floor;
- FINE: irrelevant kept > floor;
- BOTH.

The SI law predicts that competent selective specimens are MATCH or FINE-and-shrinking-with-pressure. Countermodel B
(lossless) predicts FINE. Countermodel C (blind loss) predicts COARSE at matched merge rate.

Consumers:
- Cosmos: a System adapter for prometheus/cosmos/c3/system.py @940b486f2. Episodes are CSG streams; the query asks
  for the next symbol's distribution, or in the control variant the optimal action. Planted calibration systems:
  - CS-oracle register (MATCH);
  - GS-register (FINE);
  - window-k register on an infinity-cryptic process (COARSE; the PKG-S1 pilot showed STAT excess .060 at the best
    k on Even).
- Ananke: an env family "CSG" in prometheus/ananke/envs.py @eb7c4b40a. The sensor emits CSG symbols; the readout is
  scored on the next-symbol class. This gives SI01 a relevance partition that is NOT recency, which is exactly what
  roles/Ananke/research/C2_SI01_REVIEW.md @c34cbb463 said HOLD/M2 cannot give ("forgets by construction").
- LM02 / ARC3: run the PKG-S1 learners and the P01 learners on CSG with r > 0. They are the first learners scored by
  partition, not only log-loss.
- The blind control required by P12 / H-D1-68: "merge uniformly across causal-state boundaries". Draw random merges
  of GS labels that cross CS classes at a matched merge rate. This replaces "random eviction" as the relevance-blind
  control.

Expected under the claim (SI selective memory): competent specimens converge to MATCH as pressure (bytes or ops) tightens,
with the E class merging after synchronisation.

Against:
- competent specimens that remain FINE at full competence (countermodel A/B signature, FALSIFIERS 20:50Z);
- or COARSE and FINE rates indistinguishable between R and N distinctions (countermodel C).

Would have been designed differently:
- The SI program's R/E/N classes (PTE-SI01 directive, roles/Ananke/prompts/2026-09-25_pte_si01_directive/... :168-186
  @69302a66e) were to be hand-labelled.
- The DSA and memo 11b demand generator-derived relevance, which CSG supplies.
- Cosmos C3's task (prometheus/cosmos/c3/task.py @940b486f2) has a trivial causal-state partition: the cue alone.
  Every C3 gate therefore certifies "a cue was kept", never "the right distinctions were kept".
- LM01 is excluded by operator ruling; CSG goes to LM02.

Cost: M (about 2-3 days: generator, minimiser, R/E/N labeller, scoring estimator, Cosmos adapter; the Ananke env is a
further day). Runs are minutes to hours on numpy. Host: L.

### P09. Still et al. 2012 nonpredictive information -> LABEL-FREE MEMORY ESTIMATOR

Finding. Still, Sivak, Bell, Crooks (2012) PRL 109:120604, arXiv:1203.3271 (web-checked). The nonpredictive part of a
driven system's memory, I_mem - I_pred, bounds dissipated work. Any maximally efficient memory is predictive.

Bears on: H-D5-24, H-D1-37, H-D3-41; FR-041, FR-035.

Artifact (MEASUREMENT): nonpred(states, inputs, lag).
- From a trajectory of specimen states M_t and inputs x_t, estimate I(M_t; x_{<=t} window) - I(M_t; x_{>t} window).
- Use a discrete plug-in estimator on quantised M, with bias correction by shuffle, and validate it on CSG (P08),
  where the truth is exact: for the CS-oracle register, nonpred = 0; for the GS register, nonpred = H(GS | CS).
- Apply it to Ananke M2 (cell 4ab2ba014aac967e, roles/Ananke/pte/c1_rows/cells.jsonl.gz @b91f522ae) with in-flight
  packets included in M. It needs no task labels.

Under the claim: selected specimens have lower nonpred than same-competence unselected ones.
Against: nonpred does not separate them, and the estimator is decoration (then it fails P19's completeness test).

Would have been designed differently: FR-041's "memory index scored without labels" has no candidate statistic, and
this is one with a known-answer fixture.

Cost: S (estimator plus fixture, about 1 day). Host: L.

### P10. Bialek-Nemenman-Tishby predictive information -> NULL WORLD and a generator axis

Finding. Bialek, Nemenman, Tishby (2001) Neural Computation 13:2409 (UNVERIFIED in PA). A high-entropy i.i.d. world
has h_mu > 0 and I_pred = 0. There, "keep nothing" is optimal and the SI law holds trivially.

Bears on: memo 11a; H-D1-38, H-D3-27.

Artifact.
- (i) NULL WORLD: CSG with n = 1 (i.i.d.). Any "SI support" verdict produced there is void by construction; add it to
  every SI gate as a must-not-support control.
- (ii) Generator axis: order the CSG instances by I_pred(T) growth (bounded: finite unifilar; log T: parametric
  mixtures; power law: nonunifilar with long memory) and report every SI readout per class.

Under the law: selectivity advantages grow with I_pred. Against: the advantage is flat across classes, i.e. it is not
about prediction.

Would have been designed differently: memo 11a operationalised "changing environment" as positive entropy rate
(programs/selective_irreversibility/memo/PORTFOLIO_MEMO_2026-09-25.md @d50103524), which admits the i.i.d. world.

Cost: XS once P08 exists. Host: L.

### P11. Kolchinsky et al. 2019: IB degenerate in deterministic worlds -> STOCHASTIC-RELEVANCE CONTROL

Finding. Kolchinsky, Tracey, Van Kuyk (2019) ICLR, arXiv:1808.07593 (web-checked). If Y is a deterministic function
of X, the IB Lagrangian cannot trace the curve, and trivial solutions exist at every point.

Bears on: H-D3-45, H-D1-41; FALSIFIERS row A lane (NPE reversible core).

Artifact (CONTROL):
- a noise knob eps in {0, .01, .05, .2} on CSG emissions (P08);
- and, for any deterministic substrate proposed for SI (the Janus-style NPE reversible core, memo M1_sections s E), a
  requirement that the input stream carries measured positive entropy AND that the relevance variable is stochastic.

Readout: whether the relevant/irrelevant split (P08 scoring) is stable across eps > 0. If a verdict exists only at
eps = 0, it is an IB-degeneracy artefact.

Would have been designed differently: FALSIFIERS row A names "a measured positive input-entropy rate", but not a
stochastic relevance variable. Z80/TINYPROG-based SI readings (FR-039) have none.

Cost: XS. Host: L.

### P12. Isele & Cosgun / Karamcheti: surprise retains noise; random = distribution matching -> LEARNING-PROGRESS ARM + noise dose

Finding.
- Isele & Cosgun (2018) AAAI (web-checked): surprise- and reward-selected replay forgets; reservoir (distribution
  matching) is consistently best.
- Karamcheti et al. (2021) ACL, arXiv:2107.02331 (web-checked): uncertainty acquisition loses to random because of
  unlearnable collective outliers.

Bears on: H-D3-33, H-D1-68, H-D5-23; FR-038.

Artifact (CONTROL + dose-response). This is DEV-ONLY on the existing fixture (ensorain/lm01/fixture_reservoir.py; F2
L2 lowrank, B = c/4, dev seeds 9_330_000-003), not the LM01 campaign.
- Corrupted-half extra noise SD in {0, 0.3, 1, 3}.
- Arms: random / keep_worst / residual_reservoir / oracle (ensorain/lm01/arms.py:393-480 @e94fe0d5e), plus two labelled
  exploratory keys:
  - LP: learning progress = drop in the record's residual over the last k = 3 refits;
  - NF: residual minus a per-cell noise floor from repeated observations.
- Log retained-record mean age on F3.
- Mirror the same arms on CSG (P08) with r > 0, where "relevance-blind" can be made exact (the CS-uniform merge).

Under the claim: self-signal beats random at SD 0 and crosses below it as SD grows; LP and NF hold up at SD 3.
Against: self-signal loses already at SD 0-0.3. That is a new anomaly (FR-038 already found self-signal WINS in
homoscedastic dev margins, median +0.074 AC at c/4).

Would have been designed differently: the LM01 prereg treats random eviction as the relevance-blind control
(ensorain/PREREG_WTP_LM01.md @768ea8ce9; PORTFOLIO_MEMO:62-65,158-160 @d50103524). Per Isele it is distribution
matching, a strong structured policy, so it cannot be the SI "blind" null. The blind null belongs on CSG.

Cost: S (4 SD x 6 arms x 4 seeds of BufferALS at L2; minutes to an hour). Host: L. Ensorain lane or a copy; campaign
seeds untouched.

### P13. Eigen error threshold -> EFFECTIVE-RATE THRESHOLD predicts conserved-core length

Finding.
- Eigen (1971) Naturwissenschaften 58:465 (BIBLIO-VERIFIED): L_max ~ ln(sigma)/mu.
- Wilke 2001 (VERIFIED).

Bears on: H-D2-04, H-D2-09, H-D2-17, H-D2-23, H-D1-44; FR-014, FR-015.

Artifact (MEASUREMENT, pre-registered prediction, archival plus about 1 CPU-hour).
- Per NPE run with a C-CORE runaway (roles/Nestor/FINDINGS.md:370-375 @fdc73636f), estimate:
  - the effective per-byte error rate mu_eff = background mutation (world.py:38) + LDIR copy-mutation + overwrite
    rate from partner writes, measured from the pair-interaction logs, per generation, not per epoch;
  - superiority sigma = the replication rate of the master vs the mean of its one-mutant cloud (single-byte knockouts
    in isolation, Wilke's method).
- Predict L_max. Then compare it with the length of the conserved span (OP_SELF + LDIR block) and with cargo decay.

Under the claim (the erosion is an ordinary error threshold): conserved length ~ L_max, and cargo beyond L_max decays at
the predicted rate.
Against: the core is conserved far beyond L_max, or cargo erodes far inside it. Then there is a hidden effective rate
or channel (H-D2-09), or a real new phenomenon.

Would have been designed differently: NPE's C-CORE was read as "relevant" and then accepted as circular by Aporia
(FINDINGS.md:376). A threshold prediction would have made it a non-circular test.

Cost: S. Host: L (NPE logs on main; the replay is pure Python).

### P14. Knowles & Watson / Rothlauf: neutrality helps only when biased -> BIASED vs UNBIASED REDUNDANCY control

Finding. Knowles & Watson (2002) PPSN VII LNCS 2439:88 (VERIFIED); Rothlauf (2006). Random redundancy does not help
mutation-based search; synonymous, high-locality redundancy does.

Bears on: H-D3-61, H-D3-62; FR-004, FR-133.

Artifact (CONTROL).
- Any proposal that "adds percolating neutral networks" to make a mechanism reachable must run three arms on the same
  substrate:
  - N0: no added redundancy;
  - NU: unbiased redundancy (each genotype symbol duplicated into k codons mapped uniformly at random);
  - NB: biased redundancy (the codons mapping to the mechanism's intermediate parts are over-represented by factor b,
    with the endpoint payoff unchanged).
- Measure discovery rate and foothold density (FR-003).

Under the claim: NU <= N0 < NB.
Against: NU helps as much as NB. Then neutrality per se is the lever, and H-D3-61 stands as written.

Would have been designed differently: the Crius accessibility essay (docs/essays/2026-09-24-accessibility-frontier.md
@391395aac) and H-D3-61 propose neutral networks without the bias clause. Crius is CLOSED, so this binds the NEXT
substrate that tries the repair.

Cost: S on a toy (HIFF or P16); M on a real engine. Host: L.

### P15. NEAT evolves XOR -> POSITIVE-CONTROL WORLD and protection arm for Ananke

Finding. Stanley & Miikkulainen (2002) Evol Comp 10(2):99 (VERIFIED). XOR is routinely evolved when (a) the
nonlinearity does not sit after an input sum and (b) speciation protects young structure.

Bears on: H-D3-44; FR-007, FR-001.

Artifact (CONTROL). In prometheus/ananke/envs.py (@eb7c4b40a) and the engine's superposition rule (engine.py L149-150,
262-263, 290 @69975f42f), three cells:
- S0: current summed superposition;
- S1: a "channel-separated" physics variant where packets from different source sites on one channel are NOT summed.
  Deliver them as a count per sign, or keep the first-arriving one;
- S2: S0 plus a protected-innovation selection rule (a niche per genome-length class, or an age-layered elite, in
  prometheus/ananke/search.py:81-125 @2c53c82eb).
- XOR family, 20 seeds x the existing 165-cell grid subset.

Under the "substrate-specific encoding" reading (PA): S1 finds XOR, S0 does not.
Under "search protection": S2 finds it.
Against both (a general composition barrier): all three are null. That is the only outcome that would license the
general reading of H-D3-44.

Would have been designed differently: Ananke C1 (roles/Ananke/pte/C1_REPORT.md:119 @e35fb9704) reported "XOR and FLIP
NULL in 165 cells" with no substrate or search variant on which XOR is known to be reachable.

Cost: S-M (a physics flag plus a selection flag; the runs are Ananke's; a GPU path exists but the CPU oracle is
bit-exact). Host: L; S for the runs.

### P16. HIFF -> KNOWN-ANSWER WORLD for accessibility rulers

Finding. Watson, Hornby, Pollack (1998) PPSN V LNCS 1498 (VERIFIED). HIFF is unsolvable by point-mutation hill
climbing and solvable by recombination or encapsulation.

Bears on: H-D1-46, H-D3-62, H-D1-23; FR-003.

Artifact (WORLD GENERATOR): hiff(n = 2^k, k in {4, 5, 6}), with two search arms: point mutation (mu+lambda, the Crius
defaults mu = 8, lambda = 24) and two-point crossover. Compute every proposed accessibility ruler (foothold density,
rho, flat-valley length) on both.

Pass rule for a ruler: it must predict discovery for crossover and non-discovery for point mutation, AND beat current
best fitness as a predictor (the Herakles K7 bar).

A ruler that fails on HIFF is disqualified before it is spent on Crius-like or Aether D-15 claims.

Would have been designed differently: the Crius PARTS diagnostic and rho (crius/, CRIUS_C2_TERMINAL_REVIEW.md
@7069c0ce6) were never calibrated on a known-answer landscape.

Cost: S. Host: L.

### P17. Weissman 2009 crossing times -> NULL MODEL for "never assembled"

Finding. Weissman, Desai, Fisher, Feldman (2009) Theor Popul Biol 75:286 (VERIFIED). Closed-form crossing times of
plateaus and valleys in the sequential-fixation vs tunnelling regimes, as a function of N, mu and plateau length k.

Bears on: H-D3-60, H-D3-62, H-D1-45; FR-001, FR-003.

Artifact (NULL MODEL): predicted_crossing(N, mu, k, s_int). Evaluate it at the Crius parameters: 47 edits with a
one-link ledge (+1.138 at 26 edits), N ~ 8-32, the measured per-edit rate.
- If the predicted time exceeds the run budget by orders of magnitude, the 0/36 null is EXPECTED under neutral theory
  and carries no information about "construction landscape" beyond plateau length.
- Then run a toy (HIFF-like or a k-link plateau) at N in {8, 64, 512} and k in {2, 4, 8}, and check the predicted
  scaling.

Against: observed discovery times deviate from theory. Then the program's substrates have structure the theory lacks,
and rho needs its own model.

Would have been designed differently: Crius C2 ran 36 runs at mu = 8 / lambda = 24 (crius/configs/c2d.json:96-97
@b971c3a8f) without a pre-run expected-time calculation. LaBar & Adami (2016) add that tiny N is a drift regime.

Cost: S. Host: L.

### P18. Lesion validity (Jonas & Kording; El-Brolosy & Stainier; Hall) -> ISA-LEVEL KNOCKOUT + ROOT INTERVENTION

Finding.
- Jonas & Kording (2017) PLoS Comput Biol 13:e1005268 (record VERIFIED, detail UNVERIFIED): single-element lesions
  mislead about function in a designed CPU.
- El-Brolosy & Stainier (2017) (VERIFIED): knockouts trigger compensation that knockdowns do not.
- Hall (2004) (VERIFIED): production vs dependence.

Bears on: H-D2-44, H-D2-22, H-D1-18; FR-062, FR-017.

Artifact (CONTROL, three arms per knockout claim):
- K-byte: as done, NOP the site;
- K-ISA: remove the primitive at decode for the whole run (P06 flags);
- K-block: K-byte, and also remove the knocked-out opcode from the mutation and insertion alphabet, so it cannot be
  re-created.

Plus, for every certified-depth claim, a DEPENDENCE test: intervene on the root ancestor's bytes (scramble the
founder's copy loop at generation 0 in a replay) and measure the leaf's presence at depth d.

Under the lesion-fallacy claim: the knockout effect grows from K-byte to K-block to K-ISA, and depth "certified by
production" can lack end-to-end dependence.
Against: all three agree. Then the byte NOP was a valid knockout.

Would have been designed differently: the BEE HIST ablation (GROUNDING_REPORT.md:101-109 @3efdacf7e: 126/345 still
self-replicate, 124 by re-creation) was a K-byte arm. Its reading as "the copy op is necessary" or "rescued" needs
K-block.

Cost: S (replays of committed specimens). Host: L.

### P19. Kepler injection-recovery / LIGO blind injection -> COMPLETENESS CURVE + BLIND PLANT

Finding.
- Christiansen et al., Kepler transit injection I-IV (e.g. arXiv:2010.04796; VERIFIED).
- LIGO GW100916 blind injection (https://www.ligo.org/news/blind-injection.php; VERIFIED).

Bears on: H-D5-43, H-D5-46, H-D3-67, H-D5-58; FR-059, FR-058.

Artifact (MEASUREMENT + ADVERSARY). For the three silence-bearing gates FR-059 names:
- Cosmos C3 certificate: plant a Register whose read weight is a dose w in {0, SESOI/2, SESOI, 3 SESOI} (calib.py
  @940b486f2).
- Ananke C1b absence readings: plant an in-flight echo of graded gain.
- LM01's E6 oracle-vs-random control.

Run 5 seeds per dose and report detection probability vs dose. Pass: >= 0.8 at SESOI and <= 0.05 at dose 0.

BLIND variant: a third seat picks the dose and the location, commits a sealed hash, and the owning seat runs its
normal pipeline.

Under the claim: a single analyst-known plant overstates sensitivity, and the curve shows where silence stops meaning
absence.
Against: curves are steep at SESOI everywhere. Then past nulls stand.

Would have been designed differently: the Cosmos gate v3 (roles/Cosmos/c3/S1_PREREG_P1P2_GATE.md @940b486f2) used six
fixed plants, one per class, known to the analyst. The MHC v0 echo (0.05/0.05 on a memoryful base) shows the cost of
missing curves.

Cost: M (about 60 small runs per gate). Host: L; the runs are the seats'.

### P20. Trial factors / best-of-n -> CORRECTED HELD-OUT and Apollo leak repair

Finding.
- Gross & Vitells (2010) EPJ C 70:525 (VERIFIED): a trial factor for look-elsewhere.
- Gao, Schulman, Hilton (2023) ICML (VERIFIED): best-of-n overoptimisation against a proxy.

Bears on: Ares gate C / D1 (REPORT s3.3); H-D5-52; FR-070, FR-057.

Artifact (CONTROL).
- Ares: final.heldout is a max over 128 held-out evaluations (ares/search.py:292-294 @ab137f52b). Report instead:
  - the champion chosen on TRAIN and scored once on held-out (recheck_c2.py already does this; make it the default
    reducer);
  - plus a max-of-128 null computed on the shuffled-world population, which gives the trial-factor distribution.
- Apollo: the held-out margin feeds the NSGA `generalization` objective (apollo/src/fitness.py:8,36 @dd42cb103;
  apollo.py:1006-1023 @3ebdad8b4). Split it into a selection set (allowed in the objective) and a sealed gold set that
  is never written to any organism field. Report gold vs proxy over generations (Gao's curve).

Under the claim: the proxy rises while gold peaks and falls.
Against: they track each other.

Would have been designed differently: Ares cycle 2's gate C read a best-of-N swap statistic (ARES_CYCLE2_REPORT.md
:195-205 @3f68be2b9), and Apollo's design put the held-out margin in the objective.

Cost: XS (Ares reducer), S (Apollo split). Host: L.

### P21. Sutter et al. 2025 non-linear representation dilemma -> IIA vs ALIGNMENT-MAP COMPLEXITY

Finding. Sutter, Minder, Hofmann, Pimentel (2025) NeurIPS, arXiv:2507.08802 (web-checked). With unrestricted alignment
maps, any network maps to any algorithm.

Bears on: H-D3-66, H-D3-26, H-D3-41; FR-035.

Artifact (MEASUREMENT). Extend prometheus/cosmos/c3/certify.py (P1, L179-209 @940b486f2) with a map-class ladder:
- identity-on-declared-cells < linear logistic (current) < 1-hidden-layer MLP (16 units) < MLP (256);
- at each rung, a random-network baseline (an untrained specimen of the same shape).

Report the P1 effect minus baseline per rung. Use it for FR-035's cross-certification of Ananke M2 with the two
declared boundaries.

Under the claim: the effect above baseline shrinks, or turns positive for random specimens, as map complexity grows.
Certify only at the lowest rung where the specimen beats baseline.
Against: flat across rungs. Then the linear map is not the binding choice.

Would have been designed differently: FR-035's cheapest discriminator uses v3 unchanged. A P1 miss on in-flight codes
is then uninterpretable (probe too weak vs no memory).

Cost: S. Host: L.

### P22. Library learning at matched compute -> COMPUTE-MATCHED NO-LIBRARY ARM, usage census, leave-one-out

Finding.
- Berlot-Attwell, Rudzicz, Si (2024) arXiv:2410.20274 (web-checked);
- Berlot-Attwell et al. (2025) arXiv:2504.03048 (web-checked);
- Sesterhenn et al. (2025) arXiv:2507.22069 (web-checked).
- Reuse is rare, and gains shrink to ~1% or vanish when compute-matched.

Bears on: H-D5-17, H-D5-18, H-D3-53, H-D5-02; FR-043, FR-046, FR-048.

Artifact (CONTROL). For Aphrodite S4 (run_s3s4.py @52dad4db7) and any G1->G2 re-run, add:
- A0': PRISTINE at escrow B + the donor's meta-cost (6,916,141 charges, per FR-043);
- a usage census: the fraction of DERIVED's winning programs that call (acc + {H});
- leave-one-out: re-solve each win with the schema masked.

Also run the census and leave-one-out on committed Archaeon campaign2 logs (reanalysis, XS).

Under the claim: DERIVED's 16/16 on unseen-body families shrinks toward A0' at matched compute, or the wins do not
use the schema.
Against: DERIVED beats A0' with usage > 0 and masking removes the wins. That is the first compute-matched reuse
evidence in the program.

Would have been designed differently: S4 compared DERIVED with PRISTINE at equal escrow (250,000), not at equal total
compute including minting (APHRODITE_ENGINE_REVIEW_11_2026-09-24.md s6 @7b2da226b).

Cost: XS (reanalysis) to M (new arm; needs an Aphrodite amendment). Host: L; S for new Aphrodite runs.

### P23. Coevolution pathologies -> FROZEN HALL-OF-FAME reference for any co-evolved evaluator

Finding. Ficici & Pollack (1998) ALife VI; Watson & Pollack (2001) GECCO (VERIFIED records). Co-evolving
tester/testee pairs fall into mediocre stable states, disengagement, cycling or collusion, unless there is an
external fixed reference.

Bears on: H-D5-37, H-D5-38; FR-070.

Artifact (CONTROL). Ares already co-evolves: run_coevo on W9 matching pennies (ares/search.py:309-366 @ab137f52b).
- Add a frozen hall-of-fame: champions from generations {10, 30, 60, 120}, frozen, plus a fixed scripted opponent set.
- Every generation, score the current champion against the frozen set (never used for selection).

Under the claim: the in-population score rises while the hall-of-fame score cycles or declines (intransitivity or
collusion).
Against: they track each other.

Rule for H-D5-37: no co-evolved selector in any engine without this monitor.

Would have been designed differently: Ares W9 coevolution reports in-population outcomes only. H-D5-37 proposes
co-evolving selectors with no external reference.

Cost: S. Host: L.

-----------------------------------------------------------------------------------------------------------------------

## 3. Prior-art claims that CONTRADICT a current Prometheus plan, and what the plan should change

K1. SI "requires" clause priced in bytes only (programs/selective_irreversibility FALSIFIERS row A; memo G1; the
Harmonia s12 freeze request) vs Lange-McKenzie-Tapp / Bennett.
- With time free, a bounded reversible agent avoids elimination by theorem.
- The ARC3 PKG-S1 pilot already shows storage-locus and readout-locus compression tie when B >= T
  (RESULTS_S1_PILOT.md finding 1 @bef057f44).
- CHANGE: state a per-query op budget Q in every SI falsifier and in the LM02 prereg. Record ops_per_query in LM01
  v0.3.2 (permitted by amendment item 6). Judge the reversible arm on the (bits, Q) frontier (P01).
- The freeze itself is NOT ACTIONED (Harmonia journal 2026-09-27, @c17d4c477), so there is currently no frozen text
  to amend. Name the vehicle, LM02, explicitly.

K2. FALSIFIERS row A's reversible-core lane (Nestor/NPE, a deterministic reversible ISA) vs Kolchinsky et al. 2019.
Relevance readings are degenerate unless the relevance variable is stochastic. CHANGE: require eps > 0 emissions
(P11), or use CSG (P08) as the input stream.

K3. "Copying requires the COPY primitive" / "reachable ONLY through LDIR" / Block D "three make it a design law" vs
Aguera y Arcas 2024 and Cicala 2026.
- In a real Z80 soup, heredity arises first by PUSH, and LDD loops take over under task pressure without block copy.
- None of the three VMs has a stack route. None crossed copy route with task coupling.
- CHANGE: restate these findings as conditional on "this ISA (no SP/PUSH; fixed frames; mod-256 wrap)" until P05 and
  P06 run.
- Paths: GROUNDING_REPORT.md:82 @3efdacf7e; Z80ATLAS_RULINGS_FOLLOWUP_REVIEW_2026-09-24.md:227 @863d34a55;
  D_Z80_SYNTHESIS.md:48-66 @72923db05 (branch origin/archaeon/deep-block-2026-09-27).

K4. NPE C-DENSE-COPY aliases 0xE5/0xE7 (real-Z80 PUSH HL / RST 20h) to LDIR/LDDR (run_dc.py:46). This collides with
any stack route. CHANGE: move the aliases to unused bytes before P05 is built in NPE.

K5. H-D5-39 / FR-070 reading of Avida.
- The PA note said STERILIZE_* feeds both paths. The source fetch in this pass says STERILIZE_* > 0 enables only the
  in-situ path (m_test_sterilize), and the test CPU runs only when REVERT_* > 0 or STERILIZE_UNSTABLE is set
  (m_test_on_div).
- CHANGE: configure FR-070 T6 arms by flag as in P04-B. H-D5-39's original "use STERILIZE_BENEFICIAL" was closer to
  right than PA W2 allowed.
- Confirm the line numbers before quoting (VERIFIED-BY-FETCH only).

K6. NPE's competence gate is the Avida test-CPU design: reproduction is gated by a score earned in an isolated arena
the organism never lives in (world.py:803-824 -> tasks.py:117-166 @aa5833488). CHANGE: before any NPE claim of the
form "task pressure shaped the replicators", run P04-A(ii) (context-swap re-validation). Prefer the in-situ arm for new
campaigns.

K7. Apollo writes a held-out margin into an NSGA objective (fitness.py:8,36 @dd42cb103). By Gao et al. this is
selection on the held-out set. CHANGE: split into a selection set and a sealed gold set (P20). Past Apollo
"generalisation" numbers are proxy numbers.

K8. H-D5-37 (co-evolve the selector) vs Ficici & Pollack / Watson & Pollack. CHANGE: supersede its optimistic form.
Require the P23 monitor for any co-evolved evaluator, including Ares run_coevo.

K9. H-D3-61 ("add percolating neutral networks and the mechanism becomes reachable") vs Knowles & Watson / Rothlauf.
CHANGE: add the bias clause and the P14 three-arm control.

K10. The general reading of H-D3-44 ("XOR/two-stage composition is inaccessible") vs NEAT. CHANGE: read it as
substrate-specific (summing superposition) until P15's S1/S2 cells are null.

K11. SI memo and LM01 treat RANDOM eviction as the relevance-blind matched control (PORTFOLIO_MEMO:62-65,158-160
@d50103524) vs Isele & Cosgun. Reservoir random is distribution matching, a strong structured policy. CHANGE: for SI
purposes the blind control is a causal-state-uniform merge on CSG (P08). Keep random eviction in LM01 labelled as
"distribution-matching baseline", not "blind".

K12. Ares's design rule (ARES_CYCLE2_REPORT.md s4.5 @3f68be2b9) vs Schaper & Louis + the report's own numbers.
- In the only swept data, basin width and single-carrier peak are collinear (recur 40.00 vs keep 33.75).
- Arrival alone (c3) did not suffice.
- This is not a contradiction of the literature, but the rule as stated is unsupported. CHANGE: demote it to a
  hypothesis until P02-A2 (payoff-matched) runs.

K13. The Cosmos C3 gate is read as certifying "memory that matters", but its task has a trivial causal-state
partition (the cue). CHANGE: no C3 PASS should be cited as SI evidence about which distinctions survive. That requires
a CSG task (P08).

-----------------------------------------------------------------------------------------------------------------------

## 4. CONTEXT rows (no experiment would change; one line each, with the reason)

| id | finding | why CONTEXT |
|---|---|---|
| C01 | Ray 1991 Tierra (authored ancestor; parasites within hours) | Supports H-D2-29 / H-D1-35 as precedent; every Prometheus design already knows its replicators are supplied. No arm changes. |
| C02 | Pargellis 1996/2003, Greenbaum & Pargellis 2017 (self-organising codon map) | The only mutable-interpreter precedent; AL-1 (FR-090) is already commissioned with that design. It adds no control AL-1 lacks. |
| C03 | Cotler, Hongler, Hudcova 2025 (universal CA without non-trivial self-replication) | Reframes the question ("what does replication cost") but gives no generator or control beyond P05-P07's route map. |
| C04 | Godfrey-Smith 2009; Griesemer 2000; Szathmary & Maynard Smith 1997 (scaffolded / reproducer criterion) | Vocabulary. The per-birth fertility bit it implies already exists in NPE X-STERILE. It becomes operational only if BEE makes a reproduction claim. |
| C05 | Fontana & Buss 1994; Mathis et al. 2024 AlChemy (organisations without copying) | Implies pair-free organisation detectors (FR-033), but no Prometheus substrate removes copying and logs closure. It needs a new substrate, so it is not a change to an existing experiment. |
| C06 | Kruszewski & Mikolov 2022 combinator chemistry | A candidate dissimilar substrate for FR-010 T3. It is conditional on FR-010 step 2 showing a surviving recurrence; until then it is context. |
| C07 | Tishby, Pereira, Bialek 1999 information bottleneck | The SI directive already defines itself against IB; the operational residue is P10/P11. |
| C08 | Saxe et al. 2018/2019 (IB compression is estimator- or architecture-dependent) | The SI stewards already require known-answer MI fixtures (FALSIFIERS 00:45Z); nothing further changes. |
| C09 | Chaudhry et al. 2019; GDumb (tiny replay buffers are strong) | LM01 already sweeps capacity c/8..2c and records the curves (amendment item 5). Already absorbed. |
| C10 | Lenski et al. 2003 EQU (intermediate rewards) | Already adopted as a definition (FR-001: payoff means endpoint payoff); the operational form is P02's payoff match. |
| C11 | Kouvaris et al. 2017; Watson & Szathmary 2016 (evolution learns to generalise) | Relevant to FR-134, which has no active experiment; Herakles HC-T01 already ran the Toussaint arm. |
| C12 | Dingle et al. 2018; Johnston et al. 2022 (simplicity bias) | An a-priori predictor, dominated by P02's direct random-genome estimate on the same substrate. Redundant. |
| C13 | Hinton & Nowlan 1987 (Baldwin effect) | Ares already has a plasticity carrier, and PA flags the quantitative claims as contested; no arm follows. |
| C14 | Cowperthwaite et al. 2008 (ascent of the abundant) | Subsumed by P02: destination-side frequency is what estimate_prior measures. |
| C15 | Krakovna spec-gaming list; Kapoor & Narayanan 2023; Herrera-Perez et al. 2019; Jeng 2006 | Templates for a desk catalogue (FR-057 T5), not for an experiment. |
| C16 | Everitt et al. 2021 reward-tampering CIDs | A desk audit (FR-070 C / PA T9). Aphrodite grader ownership is already fixed by ruling for the current slice. |
| C17 | Dwork et al. 2015 reusable holdout | No active experiment consumes a spent holdout (FR-066 is BLOCKED-R). It becomes operational if Cosmos D is unsealed. |
| C18 | ASAL (Kumar et al. 2024) | Garbage/turbulence controls are internal findings (FR-065); no engine currently selects on an FM score. |
| C19 | STOP, Godel Agent, Darwin Godel Machine; LILO; Stanton et al. 2021 distillation | RSI and LLM-handle results. The integer-DSL Aphrodite has no names, so LILO's name controls do not apply. Fidelity reporting is already in FR-043's spec. No live LLM runs are authorised. |
| C20 | Moreno et al. hstrat; Kelleher et al. tskit | Instrument choices for FR-034 / FR-028, which are RAW and unscheduled. They change tooling, not the design of a planned experiment. |

-----------------------------------------------------------------------------------------------------------------------

## 5. Highest-value artifacts (Artemis ranking)

1. P04-A: the NPE test-conditional adversary plus context-swap re-validation. It is the one place where a live engine
   has the exact Avida test-CPU design and selection pays for it. It is cheap and hand-writable, and it decides
   whether NPE "competence" is behaviour or a test artefact.
2. P05 + P06: the stack-route ISA variant and the ISA-ablation x task-coupling grid with seeded Load-Push / LDD / LDIR
   probes. This turns the program's strongest cross-engine claim (copy op required; design law) into a route map. The
   NPE flag is the smallest change.
3. P08: the CSG generator with a known causal-state partition and R/E/N answer key. It gives SI, the DSA, Cosmos and
   Ananke SI01 a non-circular, non-recency relevance ground truth. Ensorain ARC3 already holds a third of it.
4. P01: the reversible learner arm and the (bits, ops/query) frontier on PKG-S1. The pilot data already contain the
   decisive tie; one frontier plot and three learners make the SI law's time-space form testable.
5. P02: the pre-run basin-volume estimator plus the payoff-matched ARM A2 for Ares. This is the cheapest clean
   separation of basin from payoff in the program. The estimator runs without an operator gate.
