# REACH01 R3 / FRONTIER01 preregistration: crossing the reachability desert

Physics: aeth01.op_xor (R2: PLANTED_COMPOSITION_SUPPORTED) as primary; aeth01.op_rotx as the alien-reserve arm
(~20% of runs). Execution-only energy regime, P0. Task tile, rungs, arms and descriptor: see r3_frontier.py.

## Design decisions made during qualification (disclosed)
1. With patch energies 0..3, all 1024 random patches were rung 0, with no transmission. With 0..7 they were still
   rung 0, and input-dependent state reached at most ~3-7 of 16 columns.
2. A planted relay COMBINE needs cells firing >= 24 times (one firing per energy unit in execution-only). Energy
   0..7 therefore could not express the planted solution at all, so the energy range was widened to 0..31 and the
   WRITE probability to 0.5.
3. An output-only descriptor gives search no gradient in the desert. Arm C uses a CAUSAL-INTERVENTIONAL descriptor:
   reach of a-dependent, b-dependent and jointly dependent patch state, measured by controlled input variation
   across the 16 passes, plus the output rung. No entropy, turnover or novelty descriptor.
4. Contest-arbitration finding: the planted COMBINE patch certifies COMPOSE (13 a-only, 10 b-only necessary cells,
   0 shared) at its evaluation position, but COMBINEs at only 26% of tile positions and under neither alternative
   physics seed. No energy tuning of its two final writers exceeds 51% (64-point grid). The reason: two
   continuously firing streams merging into one target are resolved by coordinate- and seed-keyed arbitration.
   The AUTONOMY check therefore has a validated NEGATIVE (the planted patch is flagged non-autonomous) but no
   validated positive in this tile geometry. (R2's one-shot gadgets are translation- and surroundings-invariant.)

## Arms and budget (equal evaluations)
- A ordinary (fresh random patches), B random-checkpoint, C certificate-guided.
- Both B and C restore with P_RESTORE = 0.9; mutation re-draws 3 cells.
- 30 batches x 1024 = 30,720 evaluations per seed and arm.
- XOR: 8 screening seeds per arm. ROTX: 2 seeds per arm.
- Expansion to 32 seeds is permitted only for a comparison that is promising AND resolves uncertainty (scaling
  rule), and would be a new, separately frozen plan.

## Certification (r3_certify.py; outside the search loop)
Up to 20 COMBINE candidates per unit, in discovery order:
- two-batch per-position ablation gives Na and Nb, and COMPOSE;
- autonomy = COMBINE at >= 0.9 of 256 tile positions AND under 2 other physics seeds.

## Decision (RULES.json)
Per seed, paired across arms:
- REACHABILITY_EXPANDED: C's max_progress AND bins_reached exceed both A's and B's in >= 6/8 seeds.
- ARCHIVE_ASSISTED_COMPOSITION: COMPOSE-certified mechanisms in >= 3/8 C seeds, AND in <= 1/8 seeds of each of A
  and B.
- AUTONOMOUS_COMPOSITION: the above, plus >= 1 C mechanism AUTONOMOUS.
- FRONTIER_NO_GAIN: none of the above.
Each outcome is reported per op. ROTX (2 seeds) is descriptive only.

## Seen before freezing
Qualification only: rung counts and reach of random patches, and the planted certificate and positional fractions
above. No search-arm data.

Hashes:
  157cf784bd6e0c8b6b6c6552ce9fc37b4a9561aadb50ffba26d4d51aac5a0b3f RULES.json
  1e8c4a0031b910d1486ddcb783f821017ce810f46d1547b421acb87e2ea00896 plan_search.json
  bd772e78c3874b8ea32e1102b6dbb86ead4fc75737e75280f08f64e8bc1bf61d plan_certify.json
  d43e9987a10a1600dbded6c8c236aeb96390f26a6c69be25be68b69f8f953c1b r3_frontier.py
  851208e771ba2fc9e90dae7ded5bc2aeb77abf3a40a56525a5984e06f3ed86f7 r3_certify.py
  e9b530759dedd05882c8ee63cb4de7f7c93ec16b66164f106fede51e8a4f02a5 r3_certify_run.py
  d0203f041378bfe302f13bddc3917bca7c4f91fa318e740a5b4f6305dd61b7b9 r3_planted.py
  b6c5a38a9bcdbaef87bb1d357cd3683713cc9b58050e78f4491447ca7f65dbb7 ../R2/express01.py
  2b594c81418d1fa1f845dd09216dc12c805c209b834b711edbd46c82919e8b54 ../reach_flight.py

## ATTEMPT 2 (the campaign's one bounded technical repair for R3), frozen before any attempt-2 data
Instrument defect in attempt 1:
- frontier_descriptor v1 bucketed reach into 4-column bins.
- In 6 completed units (XOR A/B/C, seeds 0-1; 30,720 evaluations each) every archive's best elite had progress 4
  (reach bucket 2). Arm C's parent weights (progress^2) were therefore uniform, so C reduced to B by construction.
- The experiment could not discriminate the arms. That is a ruler failure, not a scientific result.
- Attempt-1 evidence is preserved in C:/Prometheus-data/aether_reach01/R3/attempt1/: 6 unit JSONs, ledger,
  stderr.

Repair (one): per-column reach (0..16) for a, b and joint cells in the descriptor (runner r3_frontier.v2).
Everything else is identical: search operators, budgets, arms, seeds, rules, certifier. All arms are rerun, so every
unit comes from the same code version. A second technical failure marks R3 UNRESOLVED (campaign rule).

Attempt-2 hashes:
  157cf784bd6e0c8b6b6c6552ce9fc37b4a9561aadb50ffba26d4d51aac5a0b3f RULES.json
  1e8c4a0031b910d1486ddcb783f821017ce810f46d1547b421acb87e2ea00896 plan_search.json
  bd772e78c3874b8ea32e1102b6dbb86ead4fc75737e75280f08f64e8bc1bf61d plan_certify.json
  72cd5c3f2e7e74af71546403aeb8da02d6c5783167a91ffcaf9bf5783154a3d6 r3_frontier.py
  851208e771ba2fc9e90dae7ded5bc2aeb77abf3a40a56525a5984e06f3ed86f7 r3_certify.py
  e9b530759dedd05882c8ee63cb4de7f7c93ec16b66164f106fede51e8a4f02a5 r3_certify_run.py
