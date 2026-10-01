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
