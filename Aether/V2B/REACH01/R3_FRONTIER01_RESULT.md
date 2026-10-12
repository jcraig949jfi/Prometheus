# REACH01 R3 / FRONTIER01 RESULT: crossing the reachability desert

Attempt 2 (the one permitted technical repair): freeze e5bbeedcd, production 11:47Z-15:1xZ on 2026-10-10, search 30/30
and certify 30/30 rc=0. Attempt 1 (99d6e38bd) was stopped for an instrument defect: 4-column descriptor buckets left
every elite at progress 4, so arm C was identical to arm B by construction. Its 6 completed units are preserved, and
summarized in R3/evidence/search_summary_attempt1.json.
Evidence: R3/evidence/ (per-unit summaries, ledgers). Physics: aeth01.op_xor (primary) and op_rotx (alien reserve),
execution-only regime, 20 x 20 task tile.

## Frozen disposition: FRONTIER_NO_GAIN (XOR)
- REACHABILITY_EXPANDED needs C to exceed both A and B on max progress AND bins reached, in >= 6/8 paired seeds.
- Observed: 5/8 (s0, s1, s4, s6, s7). s2 lost to B; s3 and s5 tied B on progress.
- No arm discovered a COMBINE: 0 candidates certified, so no COMPOSE and no autonomy test.

| XOR, 8 seeds, 30,720 evaluations each | A ordinary | B random-checkpoint | C certificate-guided |
|---|---|---|---|
| max progress (median) | 8 | 9 | 10.5 |
| max progress (range) | 7-9 | 7-11 | 9-16 |
| descriptor bins reached (median) | 25 | 24 | 42.5 |
| bins reached (range) | 22-26 | 20-41 | 28-67 |
| cells jointly dependent on both inputs (any unit) | 0 | 0 | 0 |
| output rung reached | 0 | 0 | 0 |
| COMBINE / COMPOSE certified | 0 / 0 | 0 / 0 | 0 / 0 |

ROTX alien arm (2 seeds; descriptive): the same pattern. C 11-13 progress / 41-53 bins vs A 8-9 / 26 and B 10-11 /
31-38. No joint cells, no combination.

## Reading
- Certificate-guided restoration DOES help a little. Arm C reaches more distinct causal frontier states (median ~1.7x
  the controls) and pushes input-dependent state further into the patch.
  - The best C run reached reach_a 7-11 columns, against at most ~5-7 for A and B.
  - It is not enough to clear the preregistered 6/8 bar for REACHABILITY_EXPANDED.
- The decisive negative: in ~737k XOR evaluations (plus ~184k ROTX) no patch ever contained a single cell whose state
  depended jointly on both inputs. The two input streams never met.
- The reachability desert here is not a long walk across a landscape with a gradient. The first combination event
  is itself unreachable at this budget: both inputs must travel ~7 rows toward each other through cells that must
  fire at the right times.
- Compare the planted COMBINE (R3 qualification). A hand-designed 38-cell relay pair with energies >= 24
  certifies COMPOSE at its evaluation position. But it COMBINEs at only 26% of tile positions and under no other
  physics seed, because Aether's contest arbitration resolves merging continuous streams by coordinate- and
  seed-keyed hashes. Even the designed solution is not autonomous in this geometry.

## Separate reports (as required)
- ARCHIVE-ASSISTED DISCOVERY: none (no mechanism found with frontier assistance).
- AUTONOMOUS COMPETENCE: not applicable for discovered mechanisms (none). For the planted combiner: NOT autonomous
  (26% of positions, 0/2 seeds).

## Cognitive accounting
- Substrate: XOR combination plus relay transport (planted), and contest arbitration.
- Search infrastructure: arm C's causal-interventional archive. It expanded the explored frontier modestly and found
  no function.
- Certifier: per-pass dependency maps, ablation, autonomy.
- Experimenter: tile geometry, search space (energies widened during qualification so the planted solution was
  expressible), planted control.

## Limitations
- One tile geometry and one task.
- Mutation re-draws 3 cells; budget 30,720 per seed and arm.
- The descriptor (per-column reach) was the repaired v2. A finer gradient, e.g. timing or vertical reach, was not
  tried. A third design would be a new experiment, not a rerun.
