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
