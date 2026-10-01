# Evidence digest tan-a: Ensorain, Ananke, Theseus, Cosmos

- Reader: read-only evidence reader for EPIMETHEUS (OPUS-5.5), group tan-a.
- Tree: worktree C:/prometheus-worktrees/epimetheus-phase3 at 4c071e3c5 (merge of origin/main).
- Date: 2026-10-01.
- Starting point: docs/phase3/intake/tantalus/REPORT.md (skimmed) and seats/{Ensorain,Ananke,Theseus,Cosmos}.md
  (read in full). Load-bearing claims were then checked against code, ledgers and run JSONs. Each claim
  below says whether it was CONFIRMED at source by this reader or carried over from the dossier.
- Tags: IMPL (read in code or data), INTENT, HIST (historical claim), REPORTED (unverified result),
  CORR (later correction), INFER (code-inferred), UNK.
- Axes (Y/P/N/U): Q = the question could fail; S = substrate capacity (with a constructive proof?);
  W = world demand (with an ablated-capability baseline?); R = ruler validity; B = baseline discrimination;
  Rep = replication (not deterministic replay); M = mechanism (ablate removes, transplant restores).
- Nothing here evaluates reuse or salvage. Instruments are described only as evidence about what the record
  could detect.

## 0. Bottom line: what this apparatus could reveal

1. Across the four seats, only one world demands more than a one-bit latch, interpolation or lookup, and also
   comes with an exact ruler: Ensorain's ARC3 answer-keyed Even process. It needs a 1-bit causal state, has
   infinite Markov order, and is scored against exact Bayes with an analytic window floor. That instrument
   works. A learner with the right state count reaches Bayes. Window statistics provably cannot. The result
   was replicated by an independent reimplementation. But it is an estimation testbed: it has no organism,
   no development and no pressure. IMPL + REPORTED (ensorain/arc3/suff/worlds.py:126-131;
   RESULTS_S1_PILOT.md; replication/README.md).
2. Ananke's PTE substrate can express FLIP inference and XOR parity. In-genome hand plants at C1's exact
   physics prove this: FLIP .978 at the cell where search held .479; XOR .850 against a champion's .503.
   The GA (96 x 36) never found either. So most PTE NULLs are not evidence of absence. 30.6% are
   physics-capped by construction, about 14% are search-limited, and 55% are open. Its causal headline
   rested on a control (zero_comm) that cannot fail under the mirror-pair design. CONFIRMED at source
   (prometheus/ananke/envs.py docstring; roles/Ananke/pte/C1_ERRATA.md E-H2b, E-W20, E-W22, E-W23;
   harvest/H-PLANT/REPORT.md:36-50; harvest/wave2/W2-V/REPORT.md).
3. Theseus synth never instantiated its own hypothesis. In code, the "concept tensor" gain for slot j is a
   fixed random function of ONE parent's fingerprint, with no term coupling parents. There is no world, no
   task and no planted positive, and the rulers do not separate random programs from deep descendants. Its
   H1 null and its H1 FAIL are both uninformative about "higher-order concept interaction". CONFIRMED
   (theseus/synth/collide.py:82; theseus/runs/*/REPORT.json).
4. Both Cosmos campaigns re-derived the definition of their own label. C0 laws A and B tie a zero-parameter
   rule written from the certificate's economics on every sealed universe. The C3 law's coordinate was the
   P2 swap effect seen through the readout. The location and selection confounds are second-order defects
   of the same miner. The surviving value is the instrument record: the location attack, the definition
   rung, the family-leakage number, and lessons L1-L7. CONFIRMED (roles/Cosmos/research/RESULTS.md R-0001/2;
   GRAVEYARD.md G-0005, T-I1; reviews/AUTOPSY_C3_PUBLIC_2026-09-30.md).
5. In all four seats, no organism learns to act. Ensorain's policies are fixed heuristics, and WTP-03
   removes agency entirely. Ananke has one homogeneous evolved law and no learning within a lifetime that
   carries task information. Theseus and Cosmos C0 have no adaptive agent at all. Developmental emergence
   was not studied by any engine in this group. INFER from the code read.

## 1. What was actually built (engine cards)

### 1.1 Ensorain (M2, 09-23..09-30; numpy CPU only; no GPU code in tree; HIST/IMPL per dossier)
- E0/E1/E1.5/E2.
  - Organism: a bounded TT/CP/low-rank regressor over cell addresses, with at most about 200 params,
    updated by NLMS (E0) or ridge ALS on a 128-sample buffer (E1). It is attached to a fixed greedy
    move-to-best-predicted-exit policy.
  - World: a 4096-cell graph whose node values are a hidden rank-3 TT field.
  - Pressure: energy, a compute price, and memory caps from 96 to 4096 floats.
  - Ruler: R^2 on unvisited cells, EFF = (U - U_NOMEM)/params, transplant after relabeling.
  - Max demand: low-rank completion plus local greedy choice.
- WTP v1/v2 "World Genome foundry".
  - World: a scalar field over 64-4096 cells, made by one generator plus at most 3 transforms that run once
    at build time. The prose ("contraction as movement") has no code counterpart.
  - Organism: one online regressor substrate (16-1024 floats) plus one of 7 FIXED movement heuristics.
  - The base Memory class, also used for "none" and "marks", is a ONE-FLOAT RUNNING MEAN.
    CONFIRMED ensorain/wtp/organism.py:14-38.
- WTP v3 "substrate collider".
  - A fixed carrier (the marginal learner, itself a null-class substrate) generates one (cell, value)
    stream. That stream is replayed to every substrate and every null.
  - Ruler: XC = AC minus the max over the ladder N0 zero, N1 constant/recent constant, N2 marginal,
    N3 linear, N4 bounded lookup, N5 best simple substrate. Test sets: interp, novel, and recomb
    (pair-block holdout: every primitive seen, no pair of held values ever seen).
    CONFIRMED ensorain/wtp3/collider.py:1-15, 165-210.
  - The loop is open: the "organism" has no influence on its data (INFER).
- LM01 (frozen twice, never run).
  - Exact stores vs bounded substrates vs reservoirs on field completion. No campaign data. UNK as evidence.
- ARC3 suff/CSSR/PKG-F/LM02 (dev, answer-keyed).
  - Worlds: binary processes with exact Bayes (iid, order-k Markov, golden mean, Even, simple nonunifilar
    source), plus a key-value Zipf stream.
  - Learners: STAT(k), VERB_SUM, NEAREST, TABLE, WINDOW, HMM_EM(S), CSSR split/vote.
  - Ruler: excess log-loss vs exact Bayes, in bits/symbol. CONFIRMED worlds.py, hmm_learner.py.
  - These are estimators, not organisms.

### 1.2 Ananke PTE (M1, 09-24..10-01; torch CUDA-graph; HIST/IMPL per dossier; key parts CONFIRMED)
- Substrate: N sites, all running the SAME straight-line integer register program: 16 opcodes, L 8-16
  lines, G <= 4 rule variants, D <= 8 registers.
  - Packets are lossy, delayed and superposing. They arrive as per-channel sums and counts, with no sender
    identity.
  - "Tensor" means only the storage layout. There are no learned weights.
- Search: GA, pop 96 x 36 gens, 8 fresh worlds per generation, about 29k world-episodes per cell (INFER).
  - Fitness is acc + 0.10*max(twin contrast, 0) + 0.02*sens_any.
- Worlds: five 1-bit tasks (RELAY, XOR, MAJ, FLIP, HOLD), with 12-16 trials per episode, T about 84-360
  ticks, and N 64-144.
  - Targets are i.i.d. coins in MIRROR PAIRS: the twin world negates the targets and shares every
    exogenous draw. So any constant policy scores exactly .5 per pair. CONFIRMED prometheus/ananke/envs.py:1-16.
- Ruler: SIGNAL is lo99 > .55 on a 32-pair percentile bootstrap.
  - COMM_DEPENDENT also needs comm_delta lo99 > .03.
  - CAUSAL_SUPPORT needs zero_comm <= .55, packet_ablation <= normal - .10, and env_permutation in [.4, .6].
  - CONFIRMED prometheus/ananke/campaign.py:445-480.
- Instruments added later (exact, since the physics is deterministic):
  - mirror carrier swaps (lens_swap, swap_rel REL4);
  - per-carrier resets and flushes;
  - light-cone and epidemic ceilings;
  - plants inside the row's own genome;
  - per-trial accuracy profiles;
  - vertex-cut ablations against equal-size off-path cuts.
  - The Wave-2 certification stack (attainability, must-fail adversaries) was never promoted out of
    research/ or used on a fresh campaign (REPORTED).

### 1.3 Theseus (two tenants; seat built theseus/synth on 09-30)
- synth "organism" and world: a genome of at most 14 sequential numeric rules from 19 hand ops over
  X[4, 32] plus a memory field, run for 128 steps.
  - A "concept" is the set of ops whose keyword regex fired on a concept's prose, plus name-seeded
    parameters.
  - A "collision" splices contiguous rule runs, inserts one react rule, and applies 1-3 edit operators.
- The concept-tensor gain is gains = [2*tanh(latent(p) @ w[j % 16] * 2) for j, p in enumerate(parents)].
  - latent(p) = tanh(fp_p @ P), where P is a fixed random projection. Nothing is fitted.
  - TensorStore.edges is written, and read only to forbid exact repeats. CONFIRMED theseus/synth/collide.py:52-96.
- No environment, task, reward or agent. The ruler is grid occupancy and nearest-distance tests on a 34-d
  behavioural fingerprint: 12 trace summary statistics plus 22 intervention responses.
- The May 2026 Techne engine (theseus/ outside synth) is a different system: 658M self-verdicted
  arithmetic-relation records. The dossier records audits showing a field-name bug, a claim-shape category
  error, a shape-only promotion gate and inverted handoff labels. Its nulls are sound within 33 claim kinds
  (REPORTED/CORR; not re-read here).

### 1.4 Cosmos (M2, 09-23..10-01; numpy CPU)
- C0 world-graph engine.
  - Three hand-written families (regs, ring, ca) share one cue-distractor-ask task (V <= 16, K <= 7,
    H <= 40).
  - "Organisms" are three fixed hand-written retention programs per family: SEL / LOG / LAST.
    CONFIRMED prometheus/cosmos/substrates/regs.py:1-14.
  - Certificate SELECTIVE_PAYS.v1: PAYS iff mean fitness(SEL) - max(LOG, LAST) >= .10. It reads only native
    reward and cost arrays. CONFIRMED prometheus/cosmos/phenomenon.py.
  - The DECLARED coordinates are computed from the spec: C = cost/reward, N = expected corruption events
    (q*b*H in regs), K, G = 1 - 1/V, and Q. CONFIRMED regs.py:45-56.
  - INFER: these are close to sufficient statistics of the author's own cost/noise economics, so the guard
    against leakage through the certificate sits at the wrong level. Leakage enters through the
    coordinates, not the certificate.
  - Miner: exhaustive enumeration of expressions of size <= 6. The law is a threshold on one or two atoms,
    scored by leave-one-lineage-out balanced accuracy, with a whole-search permutation null, an adversary,
    a location attack and sealed holdouts.
- C3: a P1 decodability + P2 state-swap certificate on a one-cue delayed recall (V = 4, k = 6). The visible
  substrates, coordinates and law sit on withheld local M2 branches (UNK to this reader).
- C4: design only.

## 2. Results with evidence profiles and reclassification

Format per result: claim; reclassification; axes Q S W R B Rep M; source and check status.

### 2.1 Ensorain

ENS-E0. "Bounded TT memory discovers reusable latent structure" (15,760 lives).
- Recorded INDETERMINATE: the positive control failed. A planted TT with the true mode order and true ranks,
  learned online, reached R^2_unvisited .007 against a gate of .5 at C = 168.
- Reclass: organism_insufficiency. The representation exists but the online learner under the cap cannot
  reach it. The seat's F3: batch ALS needs about 1,600 floats, above every gated cap.
- Axes: Q Y | S P (representable: Y, a planted exact TT; learnable by the organism's rule: N) |
  W P (harvest won by coarse ranking; NOMEM harvest 3,759 beat LRU 3,030) | R P (cheat fixtures pass, PC
  fails) | B Y (NOMEM, RANDOM, LRU, LOWRANK ...) | Rep N | M N.
- Source: ensorain/E0_VERDICT.md:17-21, 91-96 (CONFIRMED by grep).

ENS-E1.5. "TT beats matrix; headroom transition."
- Reclass: world_insufficiency (the world is generated by the hypothesis class, so the contrast is a
  tautology; the seat said so in S3) plus search_insufficiency (the "transition" is where random
  order-search happened to succeed).
- Axes: Q P | S Y | W N (world = hypothesis class) | R P | B Y | Rep N | M N.
- Source: E1P5_VERDICT.md:65-70 (CONFIRMED by grep). The operator's INTRIGUING ruling coexists with the
  CLOSE verdict (HIST).

ENS-E2. "Organism discovers how its world factorises."
- Reclass: organism_insufficiency / search_insufficiency. The 512-sample buffer gave correct-model
  R^2 .44-.90, and the SD arm was worse than a no-fit MI heuristic. The INDETERMINATE control alarm was
  chance (blind_sim).
- Not a true_negative.
- Axes: Q Y | S P | W P | R P | B Y | Rep N | M N.
- REPORTED (dossier).

ENS-D. Dials: one replicated coupling (scratch x correct start, F 11.39, fresh seeds).
- Most other couplings were accounting or definitional artifacts.
- Reclass: survives_as_anomaly (weak). The EFF nulls are statistical_insufficiency (16 lives/cell).
- Axes: Q Y | S Y | W N | R P (synthetic additive/coupled grid controls) | B P | Rep P (fresh seeds, same
  code) | M N.
- REPORTED.

ENS-WTP01. Top "competence" anomalies (CG about 20).
- Reclass: ruler_insufficiency. NLMSE was normalised by the CURRENT field variance, which catastrophes drove
  to exactly 0. Memorisation and free economies also scored. The REDESIGN verdict stands.
- Axes: Q Y | S P | W N (many worlds demanded nothing; free economies) | R N | B N (CG vs the organism's own
  birth memory) | Rep P (anomalies replicated 3-4/5, but the artifact is deterministic in world
  structure) | M N.
- Source: ENSORAIN_WTP01_REPORT.md:84, 113-114 (CONFIRMED). The R1 redesign explicitly asked for "the mean
  predictor".

ENS-WTP02. Mechanical EXPAND.
- What happened: the sole surviving specimen family was 1-float running means. Specimen #10 (world
  0e3e9ca1cb88f30c, "marks", 1 float) had organism CGu .088, while its own frozen learned constant scored
  .166 (true-mean constant .000).
  - 8/8 Wave A positives were SCALAR-EXPLAINED. 6/8 are n_floats = 1 "marks" memories.
  - CONFIRMED from ensorain/runs/wtp02/kill_const.json (8 rows, all SCALAR-EXPLAINED; 6 marks/1-float).
- Ruler: CG = AC(organism) - AC(ZERO predictor). CONFIRMED ensorain/PREREG_WTP02.md:18.
- Gap: WTP-01's report asked for the MEAN predictor (ENSORAIN_WTP01_REPORT.md:113-114). Why the translation
  became "zero" is UNK; no record was found by the dossier.
- Mechanics (REPORTED, seat): organisms learned from TRANSFORMED observations (for example v_fft_abs ->
  v_tanh, a positive quantity) but were scored against the raw field.
- The detector chain amplified this. D3 divides by n_floats. Freeze, ablate-half and reskin are no-ops on a
  parameterless memory, so every gate read the same scalar.
- Reclass: false_positive, from ruler_insufficiency (zero reference; gates invariant for a constant) plus
  organism_insufficiency (684/1,500 admitted worlds had 1-float memories, REPORTED).
- Operator ruling: "FROZEN SCORER: EXPAND; OPERATOR SCIENTIFIC RULING: PARK/REDESIGN".
  CONFIRMED ensorain/WTP02_OPERATOR_RULING.md.
- Axes: Q Y | S P | W N (completion only) | R N (V1-V4 ALL_PASS with no constant in it) | B N (zero only;
  constant added post-data) | Rep P ("replicated 5/5" across seeds of a deterministic scalar
  phenomenon) | M N (ablations were no-ops).

ENS-WTP03. Mechanical "CANDIDATE PHYSICS FOUND -- DEEPEN"; seat adjudication: known completion.
- The post-data N6 check (low-rank ALS on every unfolding plus CP-ALS, ranks 1-4, tuned ridge) beat all 9
  promoted specimens by .224-2.284 AC. CONFIRMED ensorain/runs/wtp03/n6_check.json.
- Only 4 distinct N6 targets underlie the 9 rows, and different substrate classes (tt vs lowrank at q2/q3)
  reach identical AC (INFER from the JSON).
- Admission G5 required an unbounded same-class planted fit to beat the ladder. Result: 0 spectral, sparse
  or random generators among 181 admitted, and 174/181 are mutants of 13 founders.
  CONFIRMED ENSORAIN_WTP03_REPORT.md:87-92, 144-152.
- Reclass: instrument_positive (the collider correctly recovers completion as a positive control).
  For "beyond known physics": world_insufficiency (admission manufactures the class) plus
  ruler_insufficiency (no same-class batch rung).
- Axes: Q Y | S Y (completion substrates) | W P (completion demanded; nothing more) | R P (V3: the constant
  has XC <= 0 on the WTP-02 #10 world, REPORTED) | B P (N0-N5 Y, N6 missing) | Rep P (crossovers 0/12
  replicated) | M N.

ENS-ARC3-S1. Sufficiency ladder (16 seeds, T 4000).
- No window statistic reaches Bayes on the Even process: STAT excess by k = .252 .211 .131 .110 .075 .060
  .075, an interior optimum at k6.
- An EM-HMM with S = 2 reaches .000 on the 2nd half, using a 320-bit learned state against a 1,532-bit
  window statistic.
- Recency beats random eviction at matched capacity in Zipf key-value streams.
- An independent stdlib implementation, written from the spec only, confirmed C1-C4. The analytic
  representational floor H(X | last k) - 2/3 matches to 4 decimals. The precommitted prediction "optimum k
  grows with T" held (k6/k8/k8).
- CONFIRMED RESULTS_S1_PILOT.md, replication/README.md.
- Caveats: the HMM is GIVEN the state count S. The replica ran on the same M2 host and was written by the
  same model family. Execution was not independent (stated).
- Reclass: instrument_positive. The only world in the group with a provable demand and an exact ruler.
- Axes: Q Y | S Y (HMM S = 2 represents Even exactly; constructive) | W Y (an analytic floor proves window
  learners fail; golden mean is a matched control where windows suffice) | R Y (exact Bayes; h_mu = 2/3
  verified) | B Y (STAT(k), windows, NEAREST, TABLE) | Rep Y (independent reimplementation with different
  RNG ordering; same host) | M P (a model-class swap changes the outcome; no ablation inside a developing
  organism).

ENS-CSSR-T25. Precommitted P1-P6 all survived.
- Standard CSSR ("split") collapses to the window floor on Even: .0341, 7 states, 16/16 seeds.
- "Vote" recovers 3 states (.0005) but fails catastrophically on order-3 Markov (.394; 14/16 seeds > .05).
- The failure is localised in determinization (successor truncation), not in the statistics.
- The hybrid tau rule was never run.
- CONFIRMED CSSR_T25.md:1-80.
- Reclass: instrument_positive plus a failure-shape discovery. Learning without being told the state count
  is the hard part, and no rule tested here is safe across worlds.
- Axes: Q Y | S Y | W Y | R Y | B Y | Rep P (T = 16000 via Fabric: G1-G3 survive, G4 refuted, REPORTED) |
  M P (split vs vote swap localises the mechanism).

ENS-PKGF / LM02.
- Several interim readings were overturned by the seat's own controls:
  - v3 "regime discovery" was a recency artifact;
  - v6 "retention pays" came from stale-recall cells;
  - an N5 decaying-noise world made the detector fire 8/8 falsely.
- LM02: WINDOW_NOT_SUPPORTED.
- Reclass: mixed; mostly ruler_insufficiency repaired along the way. LM02 is a true_negative within toy drift
  regimes (REPORTED).
- Axes: Q Y | S P | W P | R P | B Y (CONST, TABLE, MARGINAL) | Rep N | M N.

ENS-LM01: never run. UNK. All axes U except Q Y (frozen kill rules) and B Y (N1 constant floor per world).

### 2.2 Ananke

ANA-C1-CAUSAL. "Communication-dependent machinery, causally verified" (RELAY .84-.89 vs zero_comm .500;
COMM_DEPENDENT 8/352; CAUSAL_SUPPORT 4/4).
- zero_comm is exactly .500 in 213/213 RELAY, 174/174 MAJ and 95/95 XOR rows. Mirror twins share every
  physics draw and the actuator is never the sensor, so with no packets the actuator trajectory is
  identical in both twins.
- COMM_DEPENDENT is an alias of SIGNAL; env_permutation cannot fail; max_loss repeats zero_comm.
- CONFIRMED C1_ERRATA.md:36-39 (E-H2b), 64-70 (E-W5); envs.py docstring; campaign.py:477-479.
- Reclass: ruler_insufficiency (control forced by construction). The causal reading rests on the
  packet_ablation clause alone, and that clause replicates for 613162a3 (E-W9 correction, REPORTED).
- Axes: Q P (zero_comm clause could not fail) | S Y | W P | R N for zero_comm, P for packet_ablation |
  B P (constant = .5 exact; no random-search or shaping-off arm) | Rep P | M P.

ANA-RELAY-TRANSPORT. Evolved one-hop transport exists.
- A1 rate 4/71. The 50 pooled SIGNAL rows are 17 conditions and 6 lineages, 32 rows from one.
- 150/196 RELAY tasks demanded only one hop.
- Reclass: survives_as_anomaly at modest scope (existence of evolved one-hop relay).
- Axes: Q Y | S Y (relay_flood plant .96-.98) | W P (mostly one hop) | R P (latch ceiling about .58;
  champions at .84-.89 are above it) | B P | Rep P (C1 reproduced 3/4; W-H: champions reproduce 0/4 from
  their own budget, i.e. tail draws, REPORTED) | M P (packet ablation, carrier swaps).
- Source: C1_ERRATA E-W4, E-W19 (CONFIRMED text).

ANA-MULTIHOP. The only two multi-hop RELAY SIGNALs (925caa3a ring d5; 882525a9 smallworld d3).
- Both are receipt-triggered one-shot flood latches.
- Accuracy by trial runs 1.00, .70, .59, ..., .50. A two-sign latch model predicts 99.0-99.6% of readouts.
- Vertex-cut -> .500, while equal-size off-path cuts change nothing.
- At 12 trials a latch clears SIGNAL (ceiling about .58-.59), and the trial-2 twin assay is a false
  negative for latches.
- CONFIRMED C1_ERRATA.md:188-201 (E-W22); W2-AI/REPORT.md lines 18, 57-77, 101-110.
- Reclass: false_positive for "multi-hop relay competence" (the gate was passable by a simpler mechanism),
  and instrument_positive for latch detection.
- Axes: Q Y | S Y | W P (per-trial forwarding is rewarded only about +.08 above the latch ceiling) |
  R N (SIGNAL) / Y (per-trial profile + cut) | B P | Rep N (2 cells) | M Y (cut ablation removes it;
  latch model).
- INFER: the root of most mechanism claims, A1 census cell 86fc0105, has held .598 and lo99 .576. That sits
  inside the one-shot latch band (H-SCI REPORT.md:50, CONFIRMED number). Whether that root is a latch was
  never checked; the W2-AL prevalence audit is INCOMPLETE.

ANA-M2. HOLD "delay-line memory" (4ab2ba01).
- Path: C1 post-hoc -> C1b in-flight carriage (flush -> .497; 3/3 fresh champions at the same physics) ->
  K1: the code is the sign of payload component 1 -> W-A: a zero-parameter two-hop echo model fits 46/46
  unseen curves (W-A/REPORT.md:53, CONFIRMED text). Chance at gap >= 12.
- Reclass: survives_as_anomaly, and it is the strongest mechanism description in PTE. But it schedules
  rather than stores, and it comes from one physics lineage (86fc0105). HOLD has sensor = actuator, so a
  4-9 line local latch also solves the task.
- Axes: Q Y | S Y | W N (a local latch suffices; i.i.d. targets never reward retention) | R Y (flush,
  swap, model prediction) | B P | Rep P (fresh champions, same physics point) | M Y (flush removes;
  component swap carries).

ANA-M3. "Self-modifying timing-locked MAJ".
- The C1 packet-ablation window excluded the readout tick. Corrected: .697 -> .501.
- K3/W-B: SETRULE is a one-time bootstrap to rule 0; a one-rule law is bit-identical.
- Reclass: false_positive, from implementation_defect (ablation window) plus ruler_insufficiency
  (frozen_routing vacuous under dest_mode all).
- Axes: Q Y | S Y | W P | R N (as run) | B P | Rep N | M Y (corrected ablation removes it).
- REPORTED (dossier; C1b CORRECTIONS file not opened).

ANA-M4. MAJ integration beyond one sensor (4781b0a1).
- Genuine at that one cell: a plant matches, and single-sensor transport cannot.
- At 13/19 MAJ SIGNAL physics INTEGRATION (lo99 > .70) is unattainable by ANY program (ceiling .701), and
  11/19 champions are matched by single-sensor transport.
- Reclass: survives_as_anomaly at one cell; ruler_insufficiency elsewhere.
- Axes: Q Y | S Y | W P | R P | B Y (single-sensor ceiling) | Rep N (replicates .636/.520) | M N.
- Source: C1_ERRATA E-W15 (CONFIRMED text).

ANA-XOR-NULL. 0/83 XOR SIGNAL.
- At least 36/83 rows are light-cone-capped below .60 for ANY program (62/83 under LC2).
- At 4222a5f7 (L12 D8 P1 C4) a 12-line parity plant fits inside the row's OWN sampled genome. It scores .850
  [lo99 .819] fresh and .832 on C1's own held-out worlds, against the champion's .503 (must-fail .500).
  Every line is essential, and the plant is evaluated with the C1 evaluator itself.
- At 3 L8/C1 rows parity is representation-limited (strongly argued, not proven).
- XOR SIGNAL is passable without parity: NOR .759.
- CONFIRMED C1_ERRATA.md:56-58, 71-74, 202-212; W2-V/REPORT.md s0-F1.
- Reclass: world_insufficiency (capped placements) + search_insufficiency (4222a5f7) +
  organism_insufficiency (L8 rows). NOT a true_negative.
- Axes: Q Y | S Y at L12, N at L8 (constructive plant) | W P (parity demanded, mostly unreachable) |
  R N (SIGNAL cheatable) | B Y | Rep N | M Y (plant line ablations).

ANA-FLIP-NULL. 0/82 FLIP SIGNAL.
- 24/82 rows are light-cone-capped.
- At the physics of C1 FLIP cell 6f82f9c7 (search held .479) a 16-line in-genome plant scores .978
  [.962, .990]. Teacher-zeroed must-fail .500; readout-ignores-m diagnostic .499.
- Copy policies attain balanced accuracy .75 exactly, and a block clock gets 1.000.
- CONFIRMED H-PLANT/REPORT.md:36-50; C1_ERRATA E-W6, E-W17.
- Note: ef77ef2e, cited alongside, was later shown to be a transfer row, not a search (Pattern 6, REPORTED).
- Reclass: search_insufficiency (n = 1 search at that cell) + ruler_insufficiency (FLIP SIGNAL is cheatable;
  certify only with balanced accuracy lo99 > .75).
- Axes: Q Y | S Y | W Y (FLIP demands inference of a hidden flipping bit, with copy = .75 as an
  ablated-capability baseline) | R P | B Y | Rep N | M Y (must-fail operand zeroing).

ANA-NULLS. Placement of the 454 C1 evolve NULLs.
- 139 (30.6%) physics-capped by a sound certificate (plus 17 probable caps).
- 62-65 eligible for a search-limitation reading.
- 250 open.
- 0/113 sampled were broken experiments.
- CONFIRMED C1_ERRATA.md:147-155 (E-W20).
- Reclass: a mix of world_insufficiency and search_insufficiency. The NULL count says nothing about
  emergence.

ANA-BOUNDARIES. 13 SUPPORTED phase boundaries.
- delta = transport-time identity; RELAY decay = plant design; HOLD decay = a non-refreshing latch
  artefact; emit-vs-rules = program space; economy x2 is OPEN.
- "No SUPPORTED boundary is established physics beyond the transport bound."
- CONFIRMED C1_ERRATA.md:176-187 (E-W21).
- Reclass: ruler_insufficiency (construction identities read as physics).

ANA-SIZE / TOPOLOGY.
- "Size-free to N = 2304" rests on ONE law, which failed fresh-seed reproduction (.572/.506):
  statistical_insufficiency.
- "Topology-bound" is hop count, since env d becomes BFS hops on random graphs: world_insufficiency.
  Corrected to REFINE for 4 laws.
- REPORTED/CORR (E-H5, E-W1).

ANA-H6. "Search reachability, not physics, bounds PTE".
- Rescoped: supportable for at most about 11-15% of NULLs, FALSE for about 24-31% (capped), undecided for
  the rest.
- The H6 text in CROSS_THREAD_COMPRESSION.md was not updated (REPORTED).
- Reclass: hypothesis_failure as a general law. Search-limitation is shown at specific cells.

ANA-SI01. No nontrivial cross-trial retention regime (W-E, W-G).
- Tasks have i.i.d. targets and never reward retention, while hand plants do retain.
- Reclass: world_insufficiency. The null was expected by construction.
- Axes: Q P | S Y | W N | R P | B P | Rep P (two namespaces, Holm) | M N.

### 2.3 Theseus (seat; theseus/synth)

THE-H1-v0. FAIL.
- Contaminated: 77 of 450 DEEP/VERY_DEEP children had a lens parent, and 19 had generation < 5.
- Coalition order depended on PYTHONHASHSEED.
- Reclass: implementation_defect.
- Axes: Q Y | S N | W N | R N | B Y | Rep N | M N.
- Source: dossier verified on committed entities. The REPORT.json verdict FAIL with grids 0 pass / 2 fail
  is CONFIRMED.

THE-H1-v0_1. INDETERMINATE.
- Grid EX(D) vs null median: desc 23 vs 21, pca 21 vs 21, resp 11 vs 7 (p .089). All metric CIs straddle 0.
- n_equal = 51, capped by the LLM arm's 51 viable genomes.
- In the desc grid the matched-random arm R occupies MORE exclusive cells (27) than D (23).
- R's median best distance to the known library (3.45 tau) EXCEEDS D's (2.15 tau). So the
  NOT_REPRODUCED_YET novelty ruler favours random programs.
- CONFIRMED theseus/runs/v0_1_2026-09-30/REPORT.json (hard_test, mechanistic, controls).
- Hidden-known control: 20/20 reproduced/partial, but the hidden genomes come from the same 12 family
  builders as the library (CONFIRMED run_v0.py:410-418). So it validates nearest-neighbour search, not
  mechanism discrimination.
- Reclass: the hypothesis was never instantiated. The concept tensor has no parent-coupling term
  (collide.py:82), there is no world, and no task. On top of that: ruler_insufficiency (no planted
  deep-ancestry positive, which the charter asked for as the FIRST positive control and v0 did not build)
  and statistical_insufficiency (n = 51; the verdict flipped between runs).
- Axes: Q P | S N (interaction not representable as built) | W N (no environment) | R N | B Y (P/B/C
  one-shot, R matched random, A LLM arm, X execution-neutral 0/40 viable, W weird) | Rep N (v0 -> v0_1 is
  a corrected rerun with a new stream; no bitwise rerun) | M N.

THE-CANDIDATES. M000617, M000946 "novel" (cells absent from controls, NOT_REPRODUCED_YET, "transfer" .90).
- "Transfer" is 1 minus the mean of six fingerprint entries. No second substrate exists.
- DEEP children sit 2-5 collisions from G0 and keep 24-35% verbatim human rules.
- Reclass: false_positive-shaped table with no discriminating ruler behind it. The seat states this.
- Axes: Q P | S N | W N | R N | B P | Rep N | M N (lens dependence not measured).

THE-MAY (Techne engine; context only).
- "Cross-catalog parity coupling": implementation_defect (field-name bug), then a claim-shape category
  error (provenance_defect).
- "2,351 discoveries": provenance_defect (0 promotable under the current formula).
- The nulls are true_negative only within 33 claim kinds; 99.98% of records were self-verdicted.
- REPORTED/CORR (dossier; underlying pivot files not opened).

### 2.4 Cosmos

COS-C0-LAW-A. Survived three sealed universes: D .983, E .972, F .930; G6b 12/12, G6E 10/12.
- The definition rung "G e^-N - C >= .10 AND (Q < 1 OR CK/2 >= .10)" scores D .973, E .971, F .887.
  McNemar law vs rung: p .688/.688/.125, so there is no significant margin anywhere.
- Status RESTRICTED: "planted-invariant recovery, not a discovered law".
- All six families were authored by Cosmos, and the sealed ones were written knowing the law's form.
- The seat had noted 97.5% agreement with a hand-derived law on 09-23 itself (HANDOFF s1 V2, CONFIRMED). The
  formal rung arrived on 09-29.
- CONFIRMED roles/Cosmos/research/RESULTS.md R-0001.
- Reclass: instrument_positive (the miner recovers a planted economic invariant) / false_positive as
  discovery. Causes: ruler_insufficiency (no definition rung) + world_insufficiency (one author; the
  coordinates encode the economics).
- Axes: Q Y (the adversary killed 7/9 laws) | S Y (trivially, by construction) | W N (fixed programs; the
  phenomenon is an authored formula) | R P (planted suite 7/7 REPORTED; rung missing) | B P (majority,
  5-NN; the rung ties) | Rep P (three sealed families by the same author; byte-identical reruns are replay
  only) | M N/A.

COS-C0-LAW-B. F .955, rung .943 (v4 coordinates); McNemar p .227.
- Law B exists because its predecessor c5cd50beb1 died by LOCATION alone at 1.01 SE over a 0.10 log2
  tolerance. Under 0.15 it would have lived.
- The rung itself moves .887 -> .943 between v3 and v4 coordinates: "the coordinate map matters more than
  the law".
- CONFIRMED RESULTS.md R-0002; GRAVEYARD.md G-0005.
- Reclass: false_positive as discovery. statistical_insufficiency (tolerance-decided succession) on top of
  the restatement.
- Axes: as law A; Rep N (one sealed universe).

COS-LOCATION. A location confound exposed by the attack.
- LOLO balanced accuracy and the confident-contradiction adversary cannot see a boundary shifted inside the
  law's own transition band.
- locate.py scans the cost knob from 0.6 to 1.4 x the predicted flip (33 points, 1,600 episodes, CRN), fits
  a logistic location, and computes delta = log2(f_obs / f_pred).
- Per-family offsets of opposite sign cancelled when pooled: regs -.147, ca -.105, ring +.142.
- Ring's offset tracked N (corr .99): a coordinate defect ("dead memory is free").
- CONFIRMED locate.py:1-81; HANDOFF s8; RESULTS R-0001 notes.
- Reclass: instrument_positive (the attack detected a real defect the pooled ruler hid).
- Axes: Q Y | S Y | W P | R Y (ladder resolution about .035 log2, below TOL) | B N/A | Rep P | M P.

COS-SELECTION. "Location-aware selection yields a surviving law."
- Selection and the location gate share one criterion: select.py calls locate on the candidates (CONFIRMED
  select.py:1-30).
- 2x2 attribution, one run per cell: 6/7 arms survive without selection. On seed 29 selection picked a WORSE
  initial law. "C1 -> C2 improvement was mostly seed."
- CONFIRMED HANDOFF s7, s10.
- Reclass: statistical_insufficiency (one run per cell; seed confound) + ruler_insufficiency (gate not
  independent of selection).
- Axes: Q Y | S Y | W N | R N | B P | Rep N | M N.

COS-G6. Intervention magnitude 10/12-12/12.
- A constant prescription also passes 10/12. Precision vs the best constant was added from G6E on.
- Reclass: ruler_insufficiency (no chance floor). REPORTED (HANDOFF s9 lists the defect; CONFIRMED text).

COS-ACTIVE. Active sampling ties random (.790 vs .788; .807 vs .831). Cost lines are worse than random
(.767 vs .946, budget-matched, 3 seeds).
- Reclass: true_negative for these samplers in this setting (post-holdout, descriptive).

COS-T-I1. On 720 spent sealed rows, 11 of 15 atoms of the C0-C2 laws re-express the definition rung beyond
a rung-excluded grammar null. The robustly killed atoms (G-0004) were the non-certificate ones.
- CONFIRMED GRAVEYARD.md:72-78.
- Reclass: instrument_positive. The graveyard's recurring fragment is the planted economics.

COS-C3-LAW. Passed its own gates L1-L5, then the coordinate audit returned REJECT.
- A zero-parameter P1/P2 rule reproduces 104/120 visible classes (40/40, 34/40, 30/40) and 12/12
  substitution worlds.
- Out-of-sample confident stratum: law and rule right on the same 42 of 44.
- Coordinate rank-correlation with the P2 effect: .875.
- Family recoverable at .77 against chance .33.
- The winning rule was preregistered as the expected outcome (credence .5).
- KILLED BEFORE HOLDOUT; D2 never spent.
- CONFIRMED AUTOPSY_C3_PUBLIC_2026-09-30.md s2; RESULTS R-0003.
- Reclass: false_positive caught before holdout (definition restatement plus family fingerprinting). The
  falsification is the result.
- Axes: Q Y | S U (substrates withheld) | W N (delayed recall of 1 of 4 symbols) | R N for the law; the
  audit is the R | B P (rung not preregistered) | Rep P (two audit replicas) | M N.

COS-C3-CERT. P1/P2 certificate.
- v1 and v2 FAILED. v3 PASSED on 6 planted systems x 5 fresh seeds (6-10); seeds 1-5 informed the amendment.
- At V = 2, k = 8 NZ is FUNCTIONAL only 3/5 (Artemis R-10, REPORTED). A fixed swap at t = k is insufficient
  for periodic-update engines.
- Reclass: instrument_positive with a recorded power limit.
- Axes: Q Y | S Y (planted) | W P | R Y on planted classes | B P | Rep P | M Y (state swap).

COS-C4: design only. Interim R-STAT: a family-constant predictor passes the S0-A gates in 200/200 sims
(REPORTED). Not evidence.

## 3. Failure shapes seen in this group (all distinct; none collapsed into FAIL)

| class | instance | direction | cite |
|---|---|---|---|
| ruler: reference choice | zero predictor instead of the mean; a 1-float running mean "competent" | false positive | ensorain/PREREG_WTP02.md:18; runs/wtp02/kill_const.json |
| ruler: denominator the world can zero | NLMSE / var(current field) after catastrophes | false positive | ENSORAIN_WTP01_REPORT.md; dossier s9 |
| ruler: missing same-class batch rung | N6 beats all 9 promoted specimens | false positive (discovery reading) | runs/wtp03/n6_check.json |
| ruler: correlated gate chain | five gates all invariant for a scalar | false positive | dossier s13 (seat journal) |
| world: admission manufactures class | G5 admits only completion-friendly worlds (0 spectral/sparse/random) | both | ENSORAIN_WTP03_REPORT.md:87-92,144-147 |
| organism: learner cannot reach representable solution | planted TT, online NLMS, R^2 .007 | false negative | E0_VERDICT.md:19-21 |
| organism: degenerate capacity in pool | 46% of WTP-02 admitted organisms are 1-float | false positive | dossier s6 (REPORTED) |
| world: lifetime < learning time | median WTP-02 life 25%; learning pays in 44/181 WTP-03 worlds | false negative | WTP03 report:95 |
| control forced by design symmetry | zero_comm = .500 exactly; env_permutation; max_loss | false positive (causal claim) | C1_ERRATA E-H2b, E-W5 |
| gate passable by simpler mechanism | one-shot latch .58 clears SIGNAL at 12 trials; NOR .759 on XOR; copy .75 / clock 1.0 on FLIP | false positive | C1_ERRATA E-W6, E-W17, E-W22 |
| world construction caps | light cone / placement: 139/454 NULLs capped | false negative | C1_ERRATA E-W20 |
| search budget vs needle | in-genome plants unreached: FLIP .978 vs .479; XOR .850 vs .503 | false negative | H-PLANT REPORT; W2-V REPORT |
| shaping pays non-task structure | w_any drives sensitivity in NULL runs; contrast bonus pays rectified codes at .75 | spurious mechanism | H-SCI F4; E-W10 |
| implementation defect in ablation | packet-ablation window excluded the readout tick (M3) | false positive | dossier C-05 |
| single physics lineage | most mechanisms descend from 86fc0105 (held .598 = latch band) | generality overclaim | H-SCI REPORT.md:45-50 |
| construction identity read as physics | delta boundaries = transport time; hop count read as topology | false positive | C1_ERRATA E-W1, E-W21 |
| hypothesis not instantiated | concept tensor has no parent coupling | uninformative null | theseus/synth/collide.py:82 |
| self-referential validation control | HK drawn from the library's own builders | ruler-validity illusion | theseus/synth/run_v0.py:410-418 |
| novelty ruler favours randomness | R farther from library (3.45 tau) than D (2.15) | false positive risk | theseus v0_1 REPORT.json |
| implementation defect flips verdict | lens-parent leak + set-order nondeterminism (FAIL -> INDETERMINATE) | both | dossier T5 |
| definition restatement | C0 law = certificate economics; C3 coordinate = P2 swap effect | false positive | Cosmos RESULTS R-0001..3; AUTOPSY |
| pooled metric masks structure | opposite-signed per-family location offsets | false positive | locate.py; HANDOFF s8 |
| tolerance-decided survival | law B succession at 1.01 SE | arbitrary | GRAVEYARD G-0005 |
| gate without chance floor | constant prescription passes G6 magnitude 10/12 | false positive | HANDOFF s9 |
| non-independent "independent" worlds | six families, one author, sealed ones written knowing the law form | false transfer evidence | RESULTS R-0001 domain |
| selection and gate share a criterion | location-aware selection vs location gate; seed confound | unresolved attribution | select.py; HANDOFF s7, s10 |

## 4. Most informative experimental geometries in this record

1. Answer-keyed process pairs with exact Bayes and analytic per-class floors (Ensorain suff).
   - The Even process (2 causal states, infinite Markov order) is paired with the golden mean (2 causal
     states, order 1).
   - The pair isolates hidden-state inference from window statistics. Excess log-loss gives a graded,
     exactly referenced score.
   - The analytic floor H(X | last k) - h_mu works as a proven ablated-capability baseline.
   - The key-value Zipf stream separates exact-history necessity from selection policy at matched capacity.
2. Excess over the best cheap null, with a ladder that includes the same-class tuned batch estimator
   (WTP-03 N0-N5 + post-data N6), plus a pair-block recombination holdout: every primitive seen, no pair
   ever seen. This is the only compositional-generalisation probe in the group.
3. A fixed carrier stream replayed to all substrates (WTP-03). It separates representation from exposure
   policy, at the cost of agency.
4. Mirror-pair worlds with shared exogenous randomness (Ananke).
   - They make constant policies exactly .5 and enable exact counterfactual swaps of a single state array at
     a named tick.
   - The same symmetry forces every control that removes the sensor-to-actuator path to .5, so such a control
     cannot fail. The geometry has to be paired with controls that are NOT invariant under the mirror.
5. Plants inside the row's own sampled genome at the exact physics where search failed, plus light-cone and
   epidemic ceilings (Ananke H-PLANT, W2-V, W2-W). This converts a NULL into one of: physics-capped,
   representation-limited, search-limited, or open.
6. A per-trial accuracy profile plus vertex-cut vs equal-size off-path cut ablation (Ananke W2-AI). It
   separates one-shot cascades from per-trial competence.
7. A boundary-location attack along an intervention knob, reported per family, with leave-one-lineage-out
   scoring (Cosmos locate.py). Location is measured, not just classification accuracy.
8. A zero-parameter definition rung as the first gate, plus a family-leakage number (Cosmos L2, L3). This
   tests whether a mined "law" exceeds the label's own semantics.
9. Matched-complexity random-program arm, execution-neutral arm and rule-destroyed twins (Theseus). Also
   rule-level provenance (raw-human rule fraction, min depth to G0) as a true depth-of-ancestry measure,
   rather than generation count.

## 5. Instruments whose detectability was actually demonstrated

| instrument | detects | evidence of detection | cite |
|---|---|---|---|
| Exact-Bayes excess on answer-keyed processes + analytic window floor | whether a learner tracks a hidden causal state vs a window statistic | HMM2 .000 vs STAT k6 .060; floor matched to 4 decimals by an independent implementation | ensorain/arc3/suff/RESULTS_S1_PILOT.md; replication/README.md |
| CSSR precommitted P1-P6 on Even/golden/order-3/SNS | determinization failure shape (successor truncation) | 6/6 precommitted predictions survived on eval seeds | ensorain/arc3/suff/CSSR_T25.md |
| Post-data constant kill (A8) | scalar-explained "competence" | 8/8 WTP-02 positives SCALAR-EXPLAINED | ensorain/runs/wtp02/kill_const.json |
| WTP-03 null ladder + XC | constant/marginal/lookup counterfeits | V3: constant XC <= 0 on the WTP-02 #10 world (REPORTED) | ensorain/wtp3/collider.py; WTP03 report |
| N6 same-class tuned batch fit | bounded online approximations of known estimators | beats all 9 promoted specimens by .22-2.28 AC | ensorain/runs/wtp03/n6_check.json |
| Mirror carrier swaps / flush (Ananke lens) | which state array carries a bit at a tick | M2 flush -> .497; component-1 sign identified (REPORTED) | dossier C-05; CORRECTIONS_2026-09-27 (not opened) |
| In-genome plants + light-cone ceilings | search-limited vs capped vs representation-limited NULLs | FLIP .978 / XOR .850 with must-fail .500; 139/454 capped | H-PLANT REPORT.md:36-50; W2-V REPORT.md; C1_ERRATA E-W20 |
| Per-trial profile + vertex-cut | one-shot latches vs per-trial relay | latch model predicts 99.0-99.6% of readouts; off-path cuts no effect | W2-AI REPORT.md |
| Cosmos location attack | per-family boundary offset invisible to BA | regs -.147, ca -.105, ring +.142; ring offset ~ N (corr .99) | prometheus/cosmos/locate.py; HANDOFF s8 |
| Zero-parameter definition rung | law = label restated | ties law A/B on D/E/F; 104/120 on C3 | RESULTS.md R-0001..3; AUTOPSY s2 |
| T-I1 fragment test | which mined atoms are the certificate | 11/15 atoms beyond a rung-excluded null | GRAVEYARD.md:72-78 |
| C3 P1/P2 certificate | decodable AND causally used history (planted) | v3 PASS 6 classes x 5 fresh seeds; weaker at V=2, k=8 (REPORTED) | dossier s9; c3/runs JSON (not opened) |
| Theseus execution-neutral arm | no-op programs passing viability | X 0/40 viable | theseus/runs/v0_1.../REPORT.json |
| Theseus HK control | nearest-neighbour library search only (NOT mechanism) | 20/20, but self-referential | run_v0.py:410-418 |

## 6. Design implications for Phase 3 (each tied to evidence)

1. A world earns a reasoning claim only with a demand proof shipped with it: an ablated-capability baseline
   that provably fails (analytic floor, light-cone ceiling, copy/latch ceiling) AND a constructive solver
   inside the organism's space that succeeds. Only ARC3 suff (Even vs golden mean) met both. Ananke FLIP met
   both only after the fact (copy .75 vs plant .978). WTP and Cosmos worlds demanded completion or a 1-symbol
   latch.
2. Organism capacity has two layers that must be shown separately: representable (a planted parameter
   setting exists) and reachable by the organism's own adaptation process. E0's planted TT was representable
   but not learnable online (R^2 .007). Ananke plants were representable but not found by the GA.
   Developmental claims need the second layer measured as a trajectory.
3. Every control must be shown to be able to fail under the experiment's own symmetry before data is taken.
   The mirror design forced zero_comm to exactly .500 in 482/482 comm rows. The preregistered WTP-02
   validation passed with no constant in it.
4. Cheap competitors must be inside the instrument before any detector fires: zero, optimal constant,
   marginal, linear, lookup, best simple substrate, same-class tuned batch estimator, the label's definition
   as a zero-parameter rule, one-shot latch, copy and clock policies. In this group each rung arrived
   post-data at least once: WTP-02 constant, WTP-03 N6, Cosmos rung (6 days late), Ananke latch.
5. Gates must be sized so that a one-shot event or a simpler mechanism cannot clear them. 12 trials let a
   latch reach .58 > .55. XOR and FLIP SIGNAL were passable without parity or inference. Per-trial profiles
   should be standard output.
6. Every NULL must be reported with its placement (capped / representation-limited / search-limited with an
   in-space plant / open) and a search-budget vs needle-size estimate. Ananke: 30.6% capped, about 14%
   search-eligible, 55% open; no needle size was ever measured.
7. Admission rules must not encode the phenomenon class. If they do, the discovered class equals the
   admission class: WTP-03 G5 admitted 0 spectral, sparse or random worlds.
8. Observables and coordinates must be computed by machinery disjoint from the label, with family leakage
   reported as a number, and worlds authored by independent hands. Cosmos C0 coordinates are the author's
   cost/noise formulas (regs.py:45-56). The C3 coordinate shared the P2 code path. L1-L7 already state this.
9. Claimed representational primitives must be checked in code for the interaction they name BEFORE running.
   Theseus's "concept tensor" had no coupling term, so a costly campaign tested nothing about concept
   interaction.
10. The unit of replication is the lineage, physics point or founder, and replication means independent
    reimplementation or new lineages, not replay.
    - ARC3 suff is the only independent reimplementation in the group.
    - Ananke mechanisms come mostly from one lineage (86fc0105).
    - WTP-03's 181 worlds come from 13 founders.
    - Cosmos "reproducibility" is byte-identical replay.
11. Exposure-controlled rulers and acting organisms are both needed. WTP-03 gained a clean ruler by deleting
    agency. No engine in this group has an organism whose policy is learned, so development of action
    selection was never observable.
12. Selection and shaping terms need a matched off arm. Ananke's w_any bonus drives sensitivity in flat NULL
    runs, and its contrast bonus pays rectified codes the full .10 at chance-level accuracy. The proposed
    shaping-off arm W0 was never run.
13. Pooled metrics must always come with per-family and per-location breakdowns. Cosmos's pooled offset hid
    opposite-signed family offsets.
14. Tolerance and threshold sensitivity must be reported for every survival decision (Cosmos law B at
    1.01 SE).
15. Learning time against lifetime must be measured per world before an inhabitability or competence claim:
    median WTP-02 life 25%; learning pays in 44/181 WTP-03 worlds.

## 7. Open questions an architect may want answered

- Why did WTP-02 implement the zero predictor when the WTP-01 redesign asked for the mean predictor? UNK; no
  record found.
- Is per-trial (resettable) multi-hop relay, FLIP inference or XOR parity search-reachable at larger
  budgets, without shaping, or with novelty search? What is the random-hit probability of the 16-line FLIP
  and 12-line XOR plants in the GA's genome distribution? Never measured.
- Is the 86fc0105 root (held .598, inside the latch band) itself a one-shot latch? W2-AL was INCOMPLETE.
- Would class-agnostic admission plus N6 plus cross-field transfer find any non-completion phenomenon in the
  WTP grammar? Never run.
- Can a learner DISCOVER the causal-state count (not be given S)? CSSR split and vote both fail across
  worlds, and the precommitted hybrid tau rule was never run.
- Would a planted deep-ancestry positive be detectable by any Theseus fingerprint? THESEUS-23 was never
  built.
- Does a foreign-authored world family break Cosmos's definition-rung tie? Not started as of 10-01.
- How independent is Ananke's CPU oracle? It shares a model family and spec, with a separate context.

## 8. Files actually opened by this reader

docs/phase3/intake/tantalus/REPORT.md; docs/phase3/intake/tantalus/seats/{Ensorain,Ananke,Theseus,Cosmos}.md;
ensorain/PREREG_WTP02.md; ensorain/ENSORAIN_WTP01_REPORT.md (excerpts); ensorain/wtp/organism.py (1-40);
ensorain/runs/wtp02/kill_const.json; ensorain/runs/wtp03/n6_check.json; ensorain/wtp3/collider.py
(excerpts); ensorain/WTP02_OPERATOR_RULING.md; ensorain/ENSORAIN_WTP03_REPORT.md (grep); ensorain/E0_VERDICT.md
(grep); ensorain/E1P5_VERDICT.md (grep); ensorain/arc3/suff/{worlds.py, RESULTS_S1_PILOT.md, CSSR_T25.md
(1-80), hmm_learner.py (1-25), replication/README.md (1-40)}; prometheus/ananke/envs.py (excerpts);
prometheus/ananke/campaign.py (440-485); prometheus/ananke/{assays.py, search.py} (grep);
roles/Ananke/pte/C1_ERRATA.md (most); roles/Ananke/research/harvest/H-PLANT/REPORT.md (excerpts);
roles/Ananke/research/harvest/H-SCI/REPORT.md (38-60); roles/Ananke/research/harvest/wave2/W2-V/REPORT.md (1-60);
roles/Ananke/research/harvest/wave2/W2-AI/REPORT.md (grep); roles/Ananke/research/workers/W-A/REPORT.md (grep);
theseus/synth/collide.py (40-100); theseus/synth/run_v0.py (400-425); theseus/runs/v0_2026-09-30/REPORT.json;
theseus/runs/v0_1_2026-09-30/REPORT.json; roles/Cosmos/research/{RESULTS.md, GRAVEYARD.md};
roles/Cosmos/research/reviews/AUTOPSY_C3_PUBLIC_2026-09-30.md; roles/Cosmos/campaigns/HANDOFF_2026-09-23.md
(s1, s7-s10); prometheus/cosmos/{phenomenon.py, locate.py, select.py (1-30), substrates/regs.py (1-60)}.
No holdout, secret or other-architect path was opened.
