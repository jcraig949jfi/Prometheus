# Ananke Wave-2 inference ledger (operator directive sha256 3c68feac...; window to 08:30Z close / 09:00Z stop)

Each entry is one investigation. Fields: question | evidence | result | confidence | strongest objection |
unresolved | next. Workers' ledger blocks are folded in when their reports are deposited.

## Active queue (kept at 8 or more investigations)
| id | owner | question (short) |
|---|---|---|
| W2-A1 | Opus worker | Executable semantics of the world: init, genome, registers, packets, routing, latency, loss, superposition, receiver execution, writes. Causal graph vs DESIGN/PREREG |
| W2-A2 | Opus worker | Executable semantics of the experiment: envs, feedback, search/fitness, promotion, assays, labels, report generation vs PREREG/C1_REPORT |
| W2-B | Opus worker | Ruler reachability proofs for every C1/C1b/ARC3/harvest gate; attainability certifier design |
| W2-C | Opus worker | Mutation/metamorphic test library for experimental semantics (draft implementation and tests) |
| W2-D | Opus worker | Search vs physics decomposition: chain instrumentation; existing-data discriminators; bounded stability-under-selection test |
| W2-E | Opus worker | Strange PTE phenomena mining and classification |
| W2-F | Opus worker | Below-engine shared experiment library (reachability, control competence, write authority, provenance, attainable range) |
| W2-G | Opus worker | Claim re-derivation: every number and verdict in C1_REPORT/C1b reports re-derived from rows |
| W2-H | Opus worker | Statistical-method review: independence units, CIs, multiplicity, seed reuse, swap_rel floor units (H16) |
| P-1 | principal | Recursive adversarial loop on H6 ("search, not physics") using H-PLANT, C1 curves and W-L |

## Entries
### P-1a (principal): is H-PLANT's light-cone bound sound, and what does it say about P3 ("zero XOR SIGNAL")?
- Question: can any information path reach the XOR actuator that lightcone.py does not model? Is P3's
  confirmation forced by construction?
- Evidence: harvest/H-PLANT/lightcone.py and out/lc_census.json; engine.py step order (deliver at slot t,
  then sense, then wake, then run, then emit with delay; draws depend only on (ws, stream, t, site), never
  on state); envs.build XOR branch (envs.py:191-207); DESIGN.md:265-267; PREREG_PTE_C1.md P3.
- Result:
  - The bound is SOUND. All inter-site influence goes through Msum/Mcnt delivered at t+delay with
    delay >= max(1, lat_base + lat_hop*dist). The model's arrival-processing rule matches the step order.
    No state-dependent RNG or global coupling exists. Async is modelled optimistically, so it is
    conservative as an upper bound. XOR coins are i.i.d. with no block structure, so an out-of-reach
    trial is exactly .5 in expectation.
  - P3 is construction-forced only on part of the census. XOR light-cone bound < .65 holds in 18.3% of
    218 non-A0 XOR rows: ring 19/19, random 7/13, smallworld 9/18, torus 5/87, global 0/81.
  - Mismatch [V]: the code places the XOR actuator at distance >= max(1, d//2) from both sensors.
    DESIGN.md says >= d. The code is MORE reachable than the design, so this does not explain the NULLs.
    The design itself places no upper bound on the actuator distance, which is why rings are dead.
- Confidence: high on soundness (code-traced); medium on census fractions (64 worlds per row; the
  census includes all non-A0 kinds).
- Strongest objection: the bound is an expectation. Finite-sample held accuracy can exceed it slightly,
  but not to lo99 > .55 at bound .52-.55.
- Unresolved: whether XOR NULLs on global/torus (bound 1.0, 168 rows) are search, representation, or
  the mirror/one-flag ruler issue. W2-D owns the search side.
- Next: (1) a P3 erratum: "zero XOR SIGNAL" is uninformative on ring rows; (2) the attainable XOR SIGNAL
  rate per topology should be reported beside P3; (3) a light-cone check should precede every future
  env freeze (route to W2-B / W2-F as a reachability primitive).
- CORRECTION to P-1a (from W2-G F3, verified by the principal by joining lc_census rows to row kind):
  lc_census counts every non-A0 kind. The kind=evolve figures are: XOR 36/83 capped below .60 (43%),
  FLIP 24/82 (29%), RELAY 16/196. My P-1a per-topology split was over all kinds. The direction of the
  conclusion is unchanged, but the magnitude is larger: nearly half of C1's XOR searches could not pass
  whatever program they found. Read P3 accordingly.

### W2-G (deposited wave2/W2-G/REPORT.md): claim re-derivation, 179 claims
- Result: 124 MATCH, 30 PARTIAL, 17 MISMATCH, 6 REPORT_ONLY, 2 UNDERIVABLE.
- Top items:
  - F1: topology->random transplant (campaign.py:317) keeps env d, so a 1-hop ring task becomes a 3-hop
    random task. At d=1 all 4 laws keep SIGNAL. "Topology-bound" is a KILL candidate. Principal
    verified the code basis.
  - F2: size-free = one unreproduced law, one-hop at every N.
  - F4: transfers ef77ef2e and 1b26026f were also cited as search outcomes in H-PLANT (in addition to
    fac4aaa2). The principal review missed ef77ef2e.
  - F5: one-hop = 17 distinct conditions; A1 one-hop 3/18 vs multi-hop 1/26 (p = .29).
  - F6: COMM_DEPENDENT == SIGNAL in comm families; CAUSAL_SUPPORT rests on packet_ablation alone.
  - F7: pooled L3 ratios; A1 rates RELAY 4/71, MAJ 3/70.
  - F10: provenance holes.
- Confidence: high (helpers' headline mismatches spot-checked by W2-G; F1 basis and F3 verified by the
  principal).
- Strongest objection: F1's d=1 check is post hoc, one physics, 32 pairs.
- Next: hop-matched transplants on all D cells; per-kind lc_census reissue; automated kind-audit of
  every cited cell id.

### W2-A2 (deposited wave2/W2-A2/REPORT.md): executable semantics of the experiment layer
- F1 [V]: the GA shaping terms (sens_act, sens_any) are what the twin ruler measures. On NULL cells,
  champion persist/beyond_hop sit about 80x above random genomes. MEMORY_WITHOUT_USE (46 rows) and
  REACH_BEYOND_HOP on NULLs are selection products. Bonus vs variance-seeking is undecided (needs the
  w=0 A/B, a search).
- F3 [V]: MAJ placement does not honour d (ring d=1 == d=2; 3 of 5 sensors off d). All 19 MAJ SIGNALs
  are one-hop; multi-hop MAJ placements score 0/55.
- F4 [V]: classify stamps transfer rows with REACH_BEYOND_HOP=False although no twin ran, and the prereg
  NULL-with-eligibility label is implemented nowhere. This is the root cause of transfers cited as NULLs.
- F6: summary.json gives TRANSFER_SUPPORT 23; the effective count is 1.
- F7: the wave hour cap resets per attempt (latent).
- F8: the c1b_run fresh-eligibility key bug (summary corrected post hoc).
- F10: SIGNAL CI undercovers (1.2% vs 0.5% at .55 with 12 trials).
- Held seeds are independent of selection, and the winner's curse is about -.005.
- APPLIED by the principal (NEUTRAL; tests fail 3/5 before and pass 5/5 after; related suites 34 passed):
  - c1b_run_fresh_eligibility.diff, with prometheus/ananke/tests/test_c1b_run_fresh_eligibility.py;
  - report_transfer_effective_p1_track.diff, with tests/test_report_transfer_effective_p1.py. The legacy
    summary.json values are asserted unchanged.
- DEFERRED until the workers that import campaign.py finish: classify_transfer_reach_none,
  run_wave_budget_and_exact_resume.

### P-2 (principal): is C1's plant-viability "physics map" plant-specific?
- Evidence: A0 RELAY rows' result.plant.acc tabulated by dial.
- Result:
  - In A0's independent draws, relay_flood viability (acc > .6) is 17/18/15% at noise 0/16/64 (no
    effect), but 17% at decay 0 vs 0-5% at decay 1/3/6.
  - The earlier "noise kills" reading came from pooling targeted non-A0 waves (my own error, caught
    before recording; an instance of W2-G F7).
  - Hypothesis: decay kills relay_flood by design, because it writes S0 only on change, so S0 decays
    toward 0 before readout. A refresh plant (S0 := sign(S0)*256 every awake tick, then relay_flood) is
    under test (wave2/P-1/decay_plant.py, running).
- Next: if refresh revives the decay rows, then C1's "decay kills RELAY" and P2-style physics-map
  statements are plant artifacts, and DESIGN's plant_viability "physics-dead vs search-failed" needs a
  plant-family qualifier.

### W2-H (deposited wave2/W2-H/REPORT.md): statistical-method review
- The pair is the right unit. pair_ci (percentile) undercovers at P=32: lower-tail miss .7-1.2% at
  p <= .8, and 3-9% at high heterogeneous p (nominal .5%). BOOTT is near nominal.
- 2 SIGNAL calls flip under BOOTT (884a64df, 8ccf6c72) and 3 under t. No prediction flips.
- BH q=.01 keeps 210/216 SIGNAL calls; Holm .01 keeps 185.
- H16: the swap_rel floor is on the SE scale and never binds (>= 2.4x margin), which is why H2 == REL3.
  The INTENDED floor would break FC (1.9% at P32). DO NOT rescale it.
- The FC model (K iid trials) is misspecified (real K_eff 3.8-56), but REL3/H2 FC stays <= .87% on the
  real mirror structure.
- AUDIT3 excess: 12.3 expected vs 22, cluster z ~1.7; 0/227 disagreements at >= 3 SE.
- The search seed is the true unit for physics-level claims: D replicates drop .857 -> .706.
- 613162a3 CAUSAL_SUPPORT is fragile (keep .88).
- C4 S2: a universal law false-fails 21-31% (my interim said ~40%). Carry this into the C4 FINAL as a
  calibration of finding A4; W2-H read no C4 reviews or data.
- Process: W2-H exceeded its compute cap (1.0-1.5 core-h vs 0.5) under machine contention. One
  self-kill of its own shell via a cmdline-matched kill, its own processes only. Recorded.
- APPLIED (NEUTRAL, a new module that nothing frozen imports): prometheus/ananke/inference.py, with
  tests/test_inference_w2h.py (6 fail before, 7 pass after).
- Not applied: b2_seed_key (SEMANTIC, gated default-off). Deferred.
- Queue replenished: W2-K (C1b and high-p fragility under BOOTT/t; census class keep probabilities).

### P-1b (principal): does multi-hop scarcity reflect search, or plant viability?
- Evidence: RELAY kind=evolve rows with light-cone bound >= .95; recorded result.plant (relay_flood,
  campaign.plant_viability). My eager re-evaluation of 16 rows reproduced the recorded plant acc to
  4 decimals, so the recorded field is used and the census was stopped as redundant.
- Result [V], SIGNAL rate by hop demand and plant viability:
  | hop demand | plant | rows | distinct conditions | SIGNAL |
  |---|---|---|---|---|
  | one-hop | ok | 99 | 23 | 40 (40%) |
  | multi-hop | ok | 9 | 5 | 2 (22%) |
  | one-hop | fail | 40 | 33 | 2 |
  | multi-hop | fail | 21 | 21 | 0 |
  Of 30 reachable multi-hop rows, 21 are relay_flood-dead (mostly decay_shift > 0, cap/aloha, async).
  "Multi-hop is rare" is therefore mostly a plant-viability/physics fact. Conditional on a working
  plant, the one-hop vs multi-hop search gap is small and not significant (n = 9, 5 conditions).
- Also: relay_flood's own A-wave viability is only 8/27 one-hop and 3/23 multi-hop. A-wave physics are
  mostly hostile to C1's only RELAY plant.
- Confidence: high on the counts; low on any multi-hop search inference (n = 9).
- Objection: relay_flood failure is a lower bound (P-2 is testing decay-refresh). If a refresh plant
  revives the decay rows, the 21 "plant-dead" multi-hop rows move to "plant-ok, search-missed".
- Next: the P-2 matched decay counterfactual (running).

### W2-D (deposited wave2/W2-D/REPORT.md): search vs physics chain
- R/S/U/P/V instruments are defined exactly. Known-answer gate: C1 champion reproduced bit-for-bit.
- FLIP @ d9cc 6f82f9c7:
  - R excluded, P excluded;
  - V excluded for full competence (the plant gets SIGNAL/COMM_DEP);
  - U excluded over the tested horizon (seeded plant rank 0 in 2/2 runs, 4 and 2 generations;
    extrapolated loss <= ~1% over 36 generations);
  - objective ranks the plant first (1.05 vs .50; the bonus can never reorder a gap > .12).
  - => link S. The plant is an isolated peak (6% of mutate() offspring keep function).
  - A relay_flood basin at .602 [.549, .650] also exists and was not reached.
  - n = 1 search seed.
- The selector cannot see competence below ~.57 (M = 8 winner's curse). Weak partial solutions are not
  retained; strong ones are.
- No "found then lost" signature in any comm family (0 rows); 2 in HOLD.
- Falsifiers F-R/P, F-U, F-V and F-S are stated. A family-level H6 needs >= 3 cells per family meeting
  all of them; none does yet.
- Ruler: FLIP SIGNAL needs a relay-only control (relay scores .602 and misses SIGNAL by .001).
- Queue replenished: W2-L (FLIP uncapped placement + relay-only control) and W2-M (MAJ integration
  plant, INTEGRATION attainability).

### X-1 (from Nestor #1207): W-U build_table.py PASS-by-default
- Confirmed [V]: pass and robust start True, so a missing FC job reads PASS. The recorded inputs had
  54/54 jobs with the full grid, so REL3/REL4/swap_rel are unaffected. A latent defect in a frozen
  worker script; not edited. Replied to Nestor #1207.
- Lesson routed to W2-F: missing input must read NOT_VERIFIED (memory: check_needs_a_third_outcome).

### P-3 (principal): fitness bonus or variance-seeking? (the open item in W2-A2 F1; partly ANANKE-14)
- Evidence: C1 evolve curves (per generation: best_fit, best_acc, max_acc, mean_acc, mean_sens_any,
  max_contrast) for 454 NULL comm-family cells (RELAY/XOR/MAJ/FLIP, held lo99 <= .55);
  search.py:332 f = acc + .10*max(sens_act, 0) + .02*sens_any; truncation on f.
- Result [V]:
  - In the median NULL run, EVERY genome scores acc exactly .5 (max_acc - mean_acc = 0) until
    generation 5 (IQR 2-12). In 40 runs it stays 0 for all 36 generations.
  - Population sens_any nevertheless rises: gen0 .0004 -> .0076 by the generation before any accuracy
    variance appears (rose in 313/364 runs).
  - In the 40 runs with zero accuracy variance throughout, it rises .0002 -> .008-.058 (RELAY .008,
    XOR .009, MAJ .058), with max_contrast 0.
  - With accuracy tied and contrast 0, f differs only by .02*sens_any, so truncation selects on the
    bonus, deterministically.
  - In typical NULL runs, sens_any reaches .10-.19 by gen 35, after accuracy variance appears. That
    later phase is consistent with both bonus and noise-seeking (bonus .02 vs accuracy spread .03 at
    gen 35).
- Inference: the w_any bonus INITIATES the sensitivity climb in NULL runs, and is its sole driver while
  accuracy is flat. Variance-seeking can only take over once accuracy noise exists. W2-A2's objection
  ("noise-chasing alone would do the same") fails for the flat phase.
  So MEMORY_WITHOUT_USE / REACH_BEYOND_HOP / persist on NULL champions are, at least in their onset,
  products of the w_any term specifically.
- Confidence: high for the flat phase (arithmetic on f with tied accuracy); medium for the late phase.
- Strongest objection: mean_sens_any can also move under mutation drift with deterministic tie-breaking.
  But tie-breaking happens on f, which includes the bonus. With nonzero bonus differences there are no
  ties among sensitive genomes, so drift alone is excluded only where bonus differences exist (they do
  whenever sens_any differs).
- Unresolved: the relative share in the late phase; only the w = 0 A/B separates it.
- Next: route to the handoff as "partially answers ANANKE-14 from existing data". The w = 0 A/B remains
  the decisive (search) test for the late phase.

### P-4 (principal): were C1's HELD predictions losable as built? (prediction-risk audit)
- Evidence: PREREG s12 P1-P8; c1_report/summary.json predictions and C_transfer; boundaries_verdicts;
  findings W2-G, W2-A2, P-1a, P-1b, P-2.
- Result, per HELD prediction:
  - P1 (RELAY plant boundary on lat/loss/delta/d) HELD on DELTA: plant .585 -> .983 and .486 -> .641 as
    delta rises. A relay plant gaining accuracy when the readout comes later is close to a light-cone
    tautology, so its risk was LOW. The other two SUPPORTED RELAY plant boundaries (decay 1.0 -> .547;
    economy 1.0 -> .547) are relay_flood-design candidates: flood-on-change vs decay, and flooding
    costs energy. P-2 tests decay.
  - P3 (zero XOR SIGNAL) HELD: 43% of XOR searches were light-cone-capped, and no XOR plant existed in
    C1. Risk was PARTLY REMOVED by construction. Note the one-flag cheat (.763 at X0) cut the other
    way: P3 was losable by a cheat, and search did not find even that.
  - P4 (<= 5% A1 COMM_DEPENDENT) HELD: COMM_DEPENDENT == SIGNAL in comm families (zero_comm forced). P4
    actually measures the A1 SEARCH SUCCESS RATE, not comm dependence. Losable, but MISLABELLED.
  - P5 (zero cross-family TRANSFER_SUPPORT for comm-family champions) HELD on n = ONE comm-family source
    (bbef66a1 -> XOR .505, MAJ .549 [lo .512], FLIP .507, HOLD .500). All other cross-family transfers
    came from HOLD sources, which P5 excludes. MAJ came within .04 of SIGNAL. WEAKLY TESTED.
  - P7 (HOLD champions size-free) HELD: HOLD's sensor is the actuator, so a local latch is size-free by
    construction (the prediction's own rationale). Risk was LOW.
  - The three LOST predictions (P2, P6, P8) were the informative ones.
- Inference: of 5 HELD predictions, 2 were low-risk by construction (P1, P7), 1 partly forced (P3),
  1 mislabelled (P4), and 1 tested on n = 1 (P5). C1's "5/8 held" therefore carries much less evidential
  weight than the count suggests. A prereg should carry a per-prediction RISK statement: an attainable
  outcome under the alternative, checked before freezing (cf. memory
  preregistered_rules_need_an_eligibility_count).
- Confidence: medium-high (P1 and P7 by argument; P3, P4, P5 by counts).
- Strongest objection: "low risk" predictions are legitimate calibration checks, and the prereg did
  label them losable. Agreed, but the report counts them as substantive evidence.
- Next: a "prediction risk" column for future preregs (route to W2-F as a primitive: attainable outcome
  under the null and the alternative for each prediction); erratum wording for C1_REPORT s1.

### W2-B (deposited wave2/W2-B/REPORT.md): ruler reachability proofs (13 proofs, certifier attain.py)
Rulers that cannot fail or cannot be reached:
- zero_comm DEGENERATE (proof P1); COMM_DEPENDENT an alias of SIGNAL; LOCAL_ONLY UNREACHABLE.
- CAUSAL_SUPPORT reduces to packet_ablation alone; env_permutation DEGENERATE (P5).
- 8/104 transects have 2 levels and are UNREACHABLE.
- The size-free test is forced for the tested laws.
- C1b M/CARRYOVER are exactly .5 for twin-symmetric predictors.
- The AUDIT3 bar fails a perfect instrument with P >= .14.
- 24/98 W-Z NO_EFFECT_REL arms are score-identical no-ops.

Rulers that are cheatable:
- XOR SIGNAL as a parity ruler: every non-parity readout scores <= .75 (P2). The "one-flag" result is
  NOR over both sensors; XOR_PIVOT (min_j p_j > .5) is SOUND.
- FLIP SIGNAL: FLIP_CLOCK (teacher once + block clock, 28 lines) scores 1.000 ignoring later teachers;
  FLIP_FEEDBACK is SOUND. Fitting the cheat in 16 lines is not shown.
- Legacy REACH_BEYOND_HOP: one-hop emitters fire it even when d <= hop.
- reach_certificate draft: window aliasing and 1-world value nudges.
  APPLIED: patch to harvest/H-INST/pte_trace.py (unfrozen harvest draft). Regression test 2/2 pass on
  the patched module; the H-INST suite 23/23 still passes.

Other:
- relay_flood never crosses .75 on XOR/MAJ/FLIP in A0 (0/1000 each). maj_sum shows MAJ itself is
  attainable at X0 (lo99 .771).
- Disagreement D1 corrects H-PLANT and the principal: "one-flag" = NOR (two-sensor), the general .75
  ceiling.
- Follow-ups routed by message: XOR_PIVOT at C1 points -> W2-J; FLIP_FEEDBACK and a <= 16-line clock
  cheat -> W2-L.

### W2-A1 (deposited wave2/W2-A1/REPORT.md): world executable semantics; causal graph from code
- F1 [V]: MAJ sensors are placed by out-distance from the actuator (envs.py:212). Packets travel sensor ->
  actuator, so on directed graphs only 18% of sensors sit at transport distance d, and 2.5% of random
  worlds are impossible. 2 of the 3 MAJ topology CANDIDATEs are artefacts (random dip .50 -> ~.62 under
  forward placement); the 3rd is the dest_mode confound.
- F2: the dest_mode alias changed no B dial selection. Consequences: one transect confound and wrong
  summary.json descriptions (5/12 D cells).
- F3: max_loss == zero_comm (12/12 pair vectors). shuffle_dest on global is a routing re-draw, so
  613162a3's "shuffle .72 > normal .688" is routing variance (the Wave-1 strange observation explained).
- F4: the twins share NOISE, so the contrast bonus pays linear sub-noise codes the full +.10 at chance.
- F5: the economy boundary is a budget identity (relay_flood is mute by tick 11).
- F6: the FLIP state transplant always raises; latent crash.
- F7: SENSE is not latched while asleep, giving unstated ceilings (MAJ single-sensor .65 at async .5).
- F8: saturate and routing-write sign asymmetries.
- F9: cap is inert under collision=none (1761 rows).
- 78 invariant tests pass, and a mutation check shows they can fail.
- Patches: P1 (record effective dest_mode) and P2 (FLIP transplant -> NOT_APPLICABLE) are NEUTRAL and
  touch campaign.py. DEFERRED to one campaign.py batch with W2-A2's two diffs, once the workers that
  import campaign finish. P3 (MAJ forward placement) is SEMANTIC, for C2 only.

### W2-F (deposited wave2/W2-F/REPORT.md): explib shared below-engine library
- 9 primitives (outcomes, trace, lockstep, reach, authority, controls, metamorphic, attainable,
  provenance, stats); 40 tests pass, 35 with prometheus and torch import-blocked.
- PTE adapter reproduces H-INST reach verdicts 4/4. It fits Bellerophon's toolbox (the Worlds Kernel)
  as the missing audit layer. The promotion path is in API.md s5.
- NEW F4 [V]: s(site_all) + s(channel_all) = max at every pair/trial at offset >= 1 (93/93 RELAY/MAJ
  groups). The two arms are ONE measurement, and AUDIT3 rows double-count mirrored arms.
- NEW F5: H-INST B4's half-width replication guard cannot fire on certificates (0/20 caught). The
  predictive rule catches 14-20/20.
- F6: between-namespace flips run 2.4x the pair-independent expectation (20 vs 8.3).
  CONTRADICTION with W2-H: W2-H finds the pair is the right unit and BOOTT calibrated within run, and
  attributes the AUDIT3 excess to a first-draw estimator plus clustering (z ~1.7).
  Both can hold if between-namespace variance includes a term absent within run (e.g. topo/physics
  draws shared within a namespace). -> W2-N replicate-seed estimate.
- D5: Harmonia freeze_precedes does not check the plan blob is unchanged; Ananke freeze_check does.
  Unify them.
- Hygiene: W2-F/explib/__pycache__ and W2-F/tests/__pycache__ are left (gitignored).

### W2-C (deposited wave2/W2-C/REPORT.md): mutation/metamorphic testing, 14 operators x 6 stages
- 191 cells: 68 self-alarm (KILLED-A), 37 caught only differentially (no clean run in production),
  47 SURVIVED, 36 EQUIVALENT, 3 UNRESOLVED.
- F1: silent_sensors/disable_channel turn SIGNAL -> NULL with NO alarm. A broken experiment reads as a
  NULL, so every NULL interpretation (H6) needs a broken-experiment guard first.
- F2: causal_label has no competence precondition (normal acc 0.0 -> NOT_SUPPORTED). A SEMANTIC patch
  for C2; no C1 D label is affected (all normal >= .60).
- F3: held/selection seed disjointness is not enforced anywhere (C1 seeds are in fact disjoint per W2-A2).
- F4: freeze_state half-way (-.25 acc) leaves labels unchanged.
- F5: irrelevant_channel is exempt from the no-op guard by a code-only assumption.
- F6: COMM_DEPENDENT comes from search.evolve's UNGUARDED zero_comm arm.
- F7: forced zero_comm also makes the CRN/mirror design untestable.
- guards.py (G0-G12): 13/14 operators self-alarm; randomize_source is not caught.
- Proposed standing mutation gate before prereg freeze (s4).
- Compute 0.54 core-h (slightly over 0.5).
- Queue replenished: W2-O (run the guards over recorded C1 NULL cells).

### W2-I (deposited wave2/W2-I/REPORT.md): hop-matched transplants + kind auditor
- F1 [V]: every transplanted law scores exactly .500 at 2 hops on its OWN ring (RELAY 4/4, MAJ 3/3 at d6).
  Evolved transport crosses exactly one hop.
- F2: at matched hops on the same C1 random graph, 6/7 D laws keep SIGNAL (MAJ needs inward placement).
  Panel: RELAY 15/18 hop-bound, MAJ 4/6.
- F3: port order never removes SIGNAL, and Kp is not a routing index (no lattice-offset arithmetic).
  CLUSTER-BOUND: 4781b0a1, bf82cb29, cd5b6fd6, 8743da7f (fail on tree-like graphs, recover on a K4-clique
  graph). LATENCY-LABEL-BOUND: HOLD M2 4ab2ba01 (needs the ring's per-port delays).
- F4: MAJ placement uses M[a] (out-distance), confirming W2-A1 F1. 79% of random-graph MAJ sensors sit
  beyond nominal d; 0/35 MAJ graph evolve rows are SIGNAL.
- F5: kind audit, 1411 citations: 5 true misattributions (4 in H-PLANT, plus the principal's own
  PRINCIPAL_REVIEW L19, now corrected) and 17 NAMING (W-E keys its retention table by adjudicate ids).
- Wording proposals for C1_REPORT F2, s1 and the engine card. Covered by E-W1 / E-W2; to be refined
  with F3 at close.

### W2-E (deposited wave2/W2-E/REPORT.md): strange phenomena
- S1/S2 613162a3: the shuffle excess does NOT reproduce (fresh -.015). The "chaos" is linear one-hop
  broadcast integration on global topology plus the decay floor (positive values < 8 never decay), and
  div_frac reads unused divergence. Agrees with W2-A1 F3.
- S3: W-L's builder == envs HOLD exactly; echo vs integrator is search contingency (p ~.2).
- S4: a 4-line latch scores 1.000 at M2 physics. The latch is a needle (43% of 1-mutants -> chance) vs
  flat echo/integrator basins: an accessibility explanation [I].
- S5 + N2 [V]: 5/86 HOLD champions depend on distractors (2c300c47 1.0 -> .508, 0c18ce5e .958 -> .5).
  The FIRST awake distractor acts as a store strobe; 311c465f is a distractor-entrained parity clock.
  "Memory despite distractors" is sometimes "memory triggered by distractors".
- S6: 4781b0a1's low pivotality is plausibly its one-copy threshold (k=1 vs the plant's k=3) [I].
- N1 [V]: rule-mosaic lottery (setrule=0, rules=2): the actuator's random initial rule decides; held >
  train by up to +.22.
- N3 [V]: relay_flood scores .633 on FLIP at 926328ee by cue-repeat gating (agrees with W2-D F6).
- N4 [V]: the transplant table had no matched normal. 62a7fff9 is one tick out of tune (+.055 at
  latency+1). Additive patch proposed (C2 driver).
- Compute 0.75-1.05 core-h (over the 0.5 cap); disclosed.

### W2-K (deposited wave2/W2-K/REPORT.md): C1b and high-p fragility
- 22 C1b readings re-evaluated exactly: 0 flips under t/BOOTT. 7/22 are within 2.33 SE; expected flips
  on a fresh re-run: 1.6.
- M2 label kept 62.5% (B false at 0.89 SE is INDETERMINATE). M3 label kept 99% / 89.5%. C1b-P1 joint
  keep ~.77, from the absolute .62 bar, while the window effect is ~0.
- Kill line without a competence gate: f6b6 k0 C1_CONTROL_NOT_REPRODUCED is an artefact.
- INTEGRATION 4781b0a1: replicated (pooled 3.4 SE). TRANSFER_SUPPORT >= 10.7 SE. 613162a3 packet clause:
  pooled 2.96 SE, which supersedes W2-H F10.
- Census: 14/284 S/C/N records are within 1 SE of a boundary; NEITHER is the most fragile class.
- APPLIED (NEUTRAL, additive): inference.reading3 / kill_eligible, with tests/test_reading3_w2k.py.

### Fix batch: campaign.py (applied ~01:35Z, NEUTRAL; frozen C1 rows/labels untouched)
- W2-A1 P1: physics_from_levels records the effective dest_mode (cell ids unchanged).
- W2-A1 P2: the FLIP state transplant returns NOT_APPLICABLE instead of crashing.
- W2-A2: classify gives REACH_BEYOND_HOP=None (not False) when no twin ran.
- W2-A2: run_wave persists the wave clock and PARKs on a non-exact resume.
- Tests: 4 new files, 13 tests (6 failed before, all pass after). Related existing suites: 61 passed.
  Shared fixtures in prometheus/ananke/tests/conftest.py.

### P-2 RESULT (principal): C1's decay "physics-dead" map is a relay_flood design artefact (decay 3)
- Design (wave2/P-1/decay_plant.py): matched counterfactual on 3 random A0 RELAY rows where relay_flood
  is viable at decay 0. decay_shift set to 3; relay_flood vs relay_refresh (3 lines renormalising S0 to
  sign(S0)*256 each awake tick, then relay_flood unchanged); identical worlds (campaign.plant_viability
  seeds, 16 worlds); eager CPU.
- Result [V]: at decay 3, relay_flood falls in all 3 cells while refresh is EXACTLY its no-decay value.
  | cell | decay 0 | relay_flood @ decay 3 | refresh @ decay 3 |
  |---|---|---|---|
  | dd265721 (random, async) | .797 | .625 | .797 |
  | 7f193b43 (random, sync) | .724 | .604 | .724 |
  | 5d87ec87 (ring, sync) | 1.000 | .677 | 1.000 |
- Inference:
  - decay_shift 3 does not physically prevent RELAY. C1's RELAY plant-viability collapse at decay > 0
    (17% -> 0-5% viable in A0) and the SUPPORTED phase boundary on decay_shift (plant 1.0 -> .547) measure
    relay_flood's write-on-change design.
  - The same holds for the multi-hop "plant-dead" rows in P-1b, where most failures involve decay.
  - The economy boundary is a budget identity (W2-A1 F5). So of C1's three SUPPORTED RELAY plant
    boundaries (delta, decay, economy): delta is a light-cone near-tautology, decay is a plant artefact,
    and economy is arithmetic.
- Confidence: high for decay 3 on these 3 cells (exact equality); decay 1 is running.
- Objection: 16 worlds per cell, 3 cells; refresh needs prog_len >= 15 (it ran at 16, as C1's plant
  ran at max(L, 12)).
- Next: append to C1_ERRATA as E-W13 once decay 1 is in.

### Process incident (principal, ~01:30Z)
- I committed and pushed 96b47d73e with test_reading3_w2k.py failing (3/12). The test read its data
  relative to its own folder, and the .npz arrays are gitignored.
- The commit command did not gate on pytest's RC: the same defect as memory
  feedback_gate_commits_on_tool_exit_not_pipe.
- Fixed in the next commit: path corrected, skip if the data is absent, the 40 KB arrays force-added,
  12/12 pass, commit gated on RC.
- Module code was unaffected.
- P-2 UPDATE: decay_shift 1 gives refresh .792/.724/1.000 (no-decay .797/.724/1.000) vs flood .617/.604/.677.
  The artefact holds at the harshest decay level as well. Recorded as C1_ERRATA E-W13.

### W2-L (deposited wave2/W2-L/REPORT.md): FLIP NULL placement + relay-only control
- F5 PROOF: copy-class policies (readout = x_k or y_{k-1}, no sign inversion) attain exactly <= .75 on
  FLIP. Exceeding .75 requires computing m. Changed-cue trials give exactly 1/2 for every copy policy.
- F4 [V]: RELAY_LATCH (14 lines, inside d9cc's genome space, no mapping inference) scores .688 and passes
  SIGNAL, COMM_DEPENDENT and FLIP_FEEDBACK. FLIP_FEEDBACK is cheatable in-space (refines W2-B "SOUND"),
  and it is blind to weak true inference (.63-.66 fail).
- F3: relay_flood's FLIP edge is a change-gated teacher hold, and the echo HURTS (corrects W2-D F6).
- FLIP placement (82 evolve rows):
  - 24 P (light cone);
  - 3 PLANT-SOLVED in exact genome space (6f82f9c7, 996716ac, 64d33b89), so S or U;
  - 14 R-CANDIDATE (all decay > 0; only 22-28-line plants found);
  - 41 UNDECIDED.
  - "FLIP NULLs search-limited" is supported 3/82, open 55/82, false 24/82.
- P-FLIP is decay-fragile (0/49 decay > 0 rows), the same pattern as relay_flood (E-W13).
- Proposed ruler FLIP_CHANGE (changed-cue accuracy lo99 > .55): relays .46/.47, P-FLIP .958.
- Clock cheat in <= 16 lines at d9cc: NOT SHOWN (~21 lines needed).
- Queue: W2-S (FLIP_CHANGE on recorded champions; physics removal on the 41 UNDECIDED).

### W2-O (deposited wave2/W2-O/REPORT.md): are C1 NULLs broken experiments?
- 16/16 sampled NULLs reproduce bit-for-bit (held, final ranking, telemetry). BROKEN 0/16 (95% UB 17%).
- Actuator reachability: 0 impossible worlds in XOR/FLIP/RELAY; MAJ 0.17%. Immaterial (W2-A1's 2.5% was
  on A0 plant worlds).
- Admissibility classes:
  - CAPPED 4 (light cone);
  - INERT 4 (readout never written in >= 50/64 worlds; 3 also FLAT, i.e. max_acc never > .5);
  - ADMISSIBLE for an S/U reading 8 (strict 7).
  - 49/454 C1 NULLs are FLAT searches.
- So H6's exposure is attribution (capped/inert/flat mixed into the NULL population), not breakage.
  Corrects my P-1 v3 emphasis on "possibly broken".
- G12 false-alarms on zero_comm control arms (2/4 SIGNAL cells). NEUTRAL patch to the proposed guards.
- Wake loss (SENSE not latched) caps 54 async NULL cells at <= .875: the light cone is optimistic on async.
- NULL admissibility checklist (A integrity, B feasibility, C interpretation) delivered.
- Queue: W2-T (checklist over all 454 NULL cells -> population rates).

### W2-P (deposited wave2/W2-P/REPORT.md): MAJ placement counterfactual + timing ceilings
- 35 MAJ graph champions under inward placement: 0/35 become SIGNAL (mean change -.003). Known-answer
  35/35 exact. The relay_flood plant is also 0/35.
- Joint light-cone + async cue-loss + wake ceiling for all 358 RELAY/MAJ evolve rows. It reproduces
  H-PLANT 18/18, and 0/69 SIGNAL rows exceed their ceiling.
- CONSTRUCTION-CAPPED NULLs (ceiling < .614, the 50%-power SIGNAL-attainable accuracy):
  RELAY 17/146, MAJ 34/143 (6 placement-only), XOR 36/83, FLIP 24/82 (light cone only).
  TOTAL 111/454 = 24% of C1's evolve NULLs were unwinnable by any program.
- MAJ graph rows: 24 capped as placed, 18 capped even under correct placement, 11 open under both
  (search failures).
- F4: held acc up to .518 where no current-trial information can reach the actuator (stale cues from
  earlier trials add zero-mean noise). W2-B P1's "exactly .5 per pair" holds only with no information
  at all.
- Inward placement is not uniformly easier (12 rows get lower ceilings).

### Batch ~02:25Z: W2-N, M, R, Q, J, S, T, U (all deposited)

W2-N (swap interval inflation; resolves the W2-F vs W2-H contradiction)
- Namespaces differ only in world seeds. Direct f(DF) = 1.00 [.91, 1.11] (M=512, 124 groups); fresh
  namespaces give 1.00 [.78, 1.39]. f = 2 is rejected.
- The AUDIT3 "excess" is fully explained: 22 rows = 10 measurements = 8 specimens, plus plug-in vs
  two-draw noise, plus first-draw selection (excluded AMBIGUOUS rows hid cert->INDET flips). The
  estimator explains 0/22, which refutes W2-H's attribution.
- Gate: keep = Phi(d/(sqrt2 f)) with f = 1 (1.12 robust); 2.33-2.6 SE for 95% keep.
- The normal run is shared per specimen (r = .993), so the specimen is the cluster unit.

W2-M (MAJ integration plants)
- Plant family hits Bayes .837 at known answers.
- One-hop MAJ placed: 18/19 SIGNAL cells and 8/15 sampled one-hop NULLs have a SIGNAL-level plant. The
  plant beats the champion at 8 SIGNAL cells (S-partial).
- 11/19 SIGNAL champions are matched by a single-sensor transport, so they do not demonstrate
  integration.
- INTEGRATION is UNATTAINABLE (ceiling .701) at the physics of 13/19 SIGNAL rows. It is genuine at
  4781b0a1, where the plant matches and single-sensor transport cannot.
- Multi-hop MAJ: 25/56 physics-capped; 0/15 placed.
- The energy economy binds MAJ programs (c_op per line).

W2-R (bonus-linear codes + timing)
- W2-A1 F4's noise-cancelling bonus leaves NO footprint on C1 champions (OR 1.54, p = .17). Scope it as
  a potential bias.
- The bonus excess actually paid comes from one-sided codes (noise-0 RELAY SIGNAL). SIGNAL champions
  are linear, not thresholded (the scorer applies sign).
- Timing: 4/16 comm champions are credibly mis-tuned (+.06-.09), all in the sync-2 delta-8 RELAY
  family. Paired M=8 selection could see such gains, so the cause is reachability or the stop, not
  selector blindness.

W2-Q (distractor strobe + lottery prevalence)
- Distractor-schedule HOLD memory is 5/86 (5.8%; 0 new); 94% is schedule-robust under fair edits.
  Broad-magnitude collapses come from distractors near cue amplitude (an ill-posed test).
- Same physics + env gives strobe vs robust champions, so mechanism is decided by search seed (H5
  fails).
- Rule-mosaic lottery: 5/8 setrule=0 rules>1 SIGNAL cells and 6/7 near-SIGNAL. Only the actuator's
  initial rule matters (R^2 .69-.96); best pin is +.09-.21 above normal.
- W2-E's a1 r0 split used unmirrored seeds (16-38% wrong); corrected .98/.49.
- Lottery cells are over-represented among census corrections (OR 6.5, p = .019).

W2-J (XOR across all 83 rows)
- New reach bound LC2 (fanout, loss, async incl. sensor wake, dup, jitter) reduces to lightcone exactly
  in the deterministic limit.
- XOR classes: CAPPED-LC1 36 + CAPPED-LC2 26 = 62/83 (75%) physics-capped. H6 is FALSE there.
- PLANT-SOLVED 6 (4 with a 16-line C1-space plant, 0 within the row's own sampled genome), so these
  are search OR representation limited. UNDECIDED 15 (8 async, 7 economy).
- The NOR cheat passes SIGNAL at 5/6 XOR-feasible rows.
- XOR_PIVOT has false negatives at partial reach. A conditional-symmetry ruler XOR_SYM separated 9/9.

W2-S (FLIP_CHANGE + physics removal)
- No recorded FLIP reading rests on copy accuracy (only 996716ac > .5, and symmetric).
- W2-L's FLIP_CHANGE is UNSOUND: 4 anti-copy champions pass it with zero inference. W2-L F5 has a
  proof error (teacher copy is always wrong on changed cues).
- The sound certificate is B = mean(same, changed) lo99 > .75; enumeration proves non-inferring
  policies stay <= .75.
- 5/14 R-candidates are copy-range.
- An epidemic bound proves P at 7 global FLIP rows.
- Revised FLIP placement: P 31 / PLANT-SOLVED 3 / R-cand 9 / PLANT-DESIGN (economy) 9 /
  P-candidate 11 / UNDECIDED 19.

W2-T (population NULL admissibility, 454 + 58 HOLD)
- BROKEN 0/113 under full guarded replay (95% UB 3.2%); 0/454 on partial checks.
- Admissible for any search-limitation reading: 48.2% strict / 57.7% lenient [.53, .62].
- Plant-backed (checklist item 12): only 51/454 = 11.2%, ALL RELAY.
- The "TRUNCATED" class (12) is early-latch champions (partial competence), renamed LATCHED-PARTIAL.
- lcwake exact-wake bound validated (60/60 match, 0/166 SIGNAL violations).

W2-U (XOR/FLIP ceilings + A0 normalisation)
- Construction-capped NULLs: 111/454 (24.4%; 109-113 robust). Async adds XOR +3, FLIP 0, MAJ +1.
- 30 FLIP rows are copy-capped.
- A0 RELAY dial ranking, ceiling-normalised: the top 3 becomes decay / economy / topology. delta falls
  from rank 2 to 12, d from 6 to 13.
  - "Enough time budget" is mostly the light-cone identity (79%/75%/64% of the raw spread).
  - decay, economy and loss survive.
  - Topology strengthens (global worst once normalised).
  - So C1's B-wave delta transect was selected by a timing identity.
- Combined with E-W13 (decay artefact for relay_flood), "decay" survives normalisation as an effect on
  the RELAY PLANT, but P-2 shows it is plant-design, not physics.
- X-2 (Nestor #1214): Nestor's W2-21 force-killed PID 18960 at ~01:55Z. This most likely ended W2-R's
  tune.py part 1 early (exit 1, no traceback). Coverage reduced, no result wrong; replied #1215-ish.

### W2-AB (deposited): PTE-C2 prereg DRAFT (not frozen, not authorized)
- Question: H6 at admitted cells (P/R/V excluded by admission) with arms BASE (12 seeds), W0, M32, B4X,
  PSEED, KSEED, STEP. B certificate for FLIP; XOR only with an XOR_SYM power certificate; replacement
  packet ablation for zero_comm.
- Gates: keep = Phi(d/(sqrt2 f)) at f = 1.12 (2.605 SE); BH; specimen clustering.
- Decisive tier 9-15 GPU-h; needs s7/operator authorization.
- F2: "multi-hop-only distribution" is not a new test, since each C1 GA trains on one env (P-1 v3 (iii)
  corrected).
- APPLIED (NEUTRAL): inference keep_prob/margin_for_keep/replication_gate gain f (default 1 = current).
  tests/test_keep_prob_f.py: 3 fail before; 17 pass with the inference suites.

### W2-AC (deposited): headline counts at correct units
- -> C1_ERRATA E-W19. A1 is the right unit (352 distinct physics/seeds).
- The namespace/family effect cannot touch C1 counts (789/789 unique seeds).
- W-Z Pb "HELD" holds only at the point estimate (CI [.19, .41]).

### W2-W (deposited): consolidated placement of 454 NULLs + 58 HOLD
- Final classes:
  - P_PROVEN 134, CONSTRUCTION_PLACEMENT 5 (capped 139 = 30.6%);
  - P_CANDIDATE 17;
  - PLANT_SOLVED_IN_SPACE 65, OVERRIDE 7;
  - R_CANDIDATE 9, PLANT_DESIGN 7;
  - INERT 56, FLAT 6, LATCHED_PARTIAL 12;
  - UNDECIDED 136.
- H6-eligible: 62 strict / 65 lenient (13.7-14.3%), mostly RELAY.
- 13 contradictions resolved; they are definitional (thresholds .60 vs .614; certificate model terms).
  Glossary of 9 term clashes.
- F1 corrects the principal: P-2's decay artefact does not transfer to C1 RELAY NULLs (6/41 rescued).
  -> E-W13 scoped, E-W20 added.
- 69 MAJ NULLs were never plant-scored: the largest open block.
