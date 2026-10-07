# PTE-C3S preregistration: selector-resolution test on graded FLIP stones

Status: FROZEN at the commit that adds this file, PLAN_C3S.json and FREEZE_C3S.json. That commit comes before any C3S
production row.

**Authority:** the 72h order (roles/Ananke/prompts/2026-10-07_72h_c3_c4_c5/, 8c48ebfdf), s3.

## 1. Question

Do graded FLIP stepping stones lose function because the selector cannot resolve partial function? The
alternative is that the representation offers no climbable path.

Evidence to beat (C2C): stone lineages usually win selection (22/28 champions under OP0), yet the champions sit at
chance (accuracy .505, B .51) against the stones' own .612 / .615.

## 2. Design (2x2 factorial, paired by stone)

**Stones.** The 28 C2C graded stones exactly as frozen in PLAN_C2C.json:
- FLIP-0004, FLIP-0099 and FLIP-0167 have 8 each;
- FLIP-0000 has 4 (idx 2/4/5/7 unavailable).

No new stones are generated.

**Seeds.** search_seed = the C2C seed for (cell, idx). The arms share the gen-0 population and the training-world
stream (world_seeds is prefix-consistent in M).

**Fixed settings:** operator OP0 (the frozen C2 mutation), pop 96, 36 generations, elite 4, trunc .25, M_final 16.
The stone sits at gen-0 index 0.

**Arms:**

| arm | selector worlds M | shaping (w_contrast, w_any) |
|---|---|---|
| S8 | 8 | (.10, .02) |
| S32 | 32 | (.10, .02) |
| W8 | 8 | off |
| W32 | 32 | off |

S8 is C2C's OP0_STEP arm exactly. Its replay gate requires the champion and the champion's held status to equal the
C2C row.

**Jobs:** 112. The order is rounds by idx, FLIP cells interleaved, arms in the order S8, S32, W8, W32.

## 3. Measurements

**Every 3rd generation plus the last, on MONITOR worlds** (64, H(C3_NS = 0xC3001007, 0x404E, cell_key); disjoint from every train,
final, held and qualification world, asserted). Two genomes are scored with the frozen FLIP ruler:
- LB: the best lineage member by fitness, with lineage share ≥ .5 (C2B's line-tag definition);
- GB: the generation best.

Also recorded EVERY generation: the lineage count, the lineage's best rank, and its training accuracy. The monitor
never feeds selection.

**Final, on HELD worlds** (C2C's: 128, H(search_seed, HELD_NS)):
- the champion (C2A rule);
- the injected stone;
- BL: the final lineage member with the highest monitor-world B. It is selected on monitor worlds only.

## 4. Frozen classification and labels (reduce_c3s.py, verbatim)

**Per search** (stone B and BL B are the held B values):

| class | meaning | rule |
|---|---|---|
| D | climb to competence | BL TRUE, or the champion TRUE with lineage share ≥ .5 |
| A | lineage and function survive | lineage alive, not D, BL B ≥ stone B − .05 |
| B | lineage survives, function erodes | lineage alive, not D, BL B < stone B − .05 |
| C | lineage dies | no final member with share ≥ .5 |

- retained = A or D.
- climb (secondary) = lineage alive and BL B ≥ stone B + .05.

**Effects.** Both are paired by stone and pooled over the other factor, giving 56 pairs each.
- M effect = retained(M32) − retained(M8). Tested with a one-sided sign test.
- Shaping effect = retained(off) − retained(on). Tested with a two-sided sign test.

Each is reported with per-cell means and a stone-bootstrap 95% interval.

**Labels** (more than one may be issued):

| label | rule |
|---|---|
| SELECTOR_RESOLUTION_EFFECT | M effect ≥ +.20, p < .05, positive in ≥ 3 of 4 cells; or D under M32 ≥ 4 in ≥ 2 cells and ≥ 4 above D under M8 |
| NO_SELECTOR_RESOLUTION_EFFECT | not the above, the M-effect bootstrap upper bound < .20, and P(retained \| M32) ≤ .50 |
| SHAPING_INTERFERENCE | \|shaping effect\| ≥ .20, p < .05, same sign in ≥ 3 of 4 cells (direction reported) |
| MIXED_OR_INCONCLUSIVE | none of the above |

**Exclusions** (flagged, never counted): OVERLAP (held/train or held/monitor), and REPLAY_FAIL on an S8 row.

**Decision rule for C3R** (order s3): if SELECTOR_RESOLUTION_EFFECT, every C3R arm uses M32. Otherwise C3R uses the C2
selector (M 8). C3R follows regardless of the result.

## 5. What each outcome would exclude

- **SELECTOR_RESOLUTION_EFFECT:** the C2C stone decay was partly a selector-noise artefact. Representation arms must
  then not be judged with M 8.
- **NO_SELECTOR_RESOLUTION_EFFECT:** the decay is not explained by four times the selector worlds. This weakens the
  selector-noise account and leaves representation/composition as the leading hypothesis.
- **SHAPING_INTERFERENCE:** the shaping bonus itself drives the loss or keeping of partial function.

## 6. Envelope

- Hardware: M1 RTX 5060 Ti, 3 workers, lease lse-7d61e3584398.
- Projection: about 2.5-3.5 h. In the flight, per-generation monitoring made a job about 4x slower (S8 ~400 s against
  ~95 s in C2C), so the monitor cadence was set to every 3rd generation plus the last (13 points) before production.
- Deadline: launch + 4 h 30 m. No job starts after it. Arm-balanced censoring applies: the rounds by idx contain
  every arm.

## 7. Threats

- Graded stones are 1-2-edit degradations of P_FLIP (a C2C threat, carried over).
- The δ = .05 retention band is about 2 SE of held B at 64 pairs.
- FLIP-0004's plant is near the ruler margin, so "competence" (D) there is conservative.
- Same author. Review is requested and is not a gate.
