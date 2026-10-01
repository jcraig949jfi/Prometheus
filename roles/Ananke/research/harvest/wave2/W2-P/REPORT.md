<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-P; sha256(report)=407119a029567256; delimited; see REPORT.provenance.json -->
# W2-P: placement and timing ceilings on the C1 RELAY/MAJ NULLs (worker W2-P, Ananke Wave 2)

**Setup.** Worktree F:/Prometheus-worktrees/ananke-base-role at b513c99cc. I wrote only to roles/Ananke/research/harvest/wave2/W2-P/ and changed no repo file. Everything ran on CPU (CUDA_VISIBLE_DEVICES=-1, `torch.cuda.is_available()` asserted False, 2 threads). Every engine evaluation used the eager `hp_common.evaluate` with 64 worlds (32 pairs) or fewer. Inward placement is a context manager (`w2p_common.inward`) that hands `envs.build` the transposed distance matrix. The MAJ branch reads M only at `_pick_at(g, M[a], ...)`, so this gives exactly `M[:, a]`; the other families never build in this mode.

**Files (all under W2-P/):**
- `w2p_common.py`
- `task1_maj_inward.py` -> out/task1_maj_inward.json, out/task1.log
- `task1b_plant_inward.py` -> out/task1b_plant_inward.json, out/task1b.log
- `task2_timing.py` -> out/task2_timing.json, out/task2.log
- `analyze2.py` -> out/task2_summary.json
- `analyze_join.py` -> out/construction_capped.json
- `check_lightcone_exact.py` -> out/check_lightcone_exact.json

## 1. Findings

**F1 [V] Re-evaluating the 35 recorded MAJ champions (random or smallworld topology) under inward placement turns 0 of 35 into SIGNAL. The mean accuracy change is -0.003.** Confidence: high.
- **Known-answer gate:** original placement on each row's recorded held seeds reproduces the recorded held acc and lo99 exactly in 35 of 35 rows. 23 of those rows have a held acc other than .5, so the match is not trivial.
- **Fresh seeds (64 worlds, W2PP namespace):**

| Group | Rows | Mean acc, original | Mean acc, inward | Mean change | lo99 > .55 (original / inward) |
|---|---|---|---|---|---|
| All | 35 | .5027 | .5000 | -.0027 | 0 / 0 |
| random | 15 | | | -.0015 | 0 / 0 |
| smallworld | 20 | | | -.0036 | 0 / 0 |

- On the recorded held seeds the mean change is -.0012, and 0 rows reach SIGNAL.
- Best inward result: acf58f34 at .533 (lo99 .519).
- **Placement check:** the fraction of sensors at transport distance exactly d rises from .00-.86 to .06-1.00 under inward placement. The patch therefore does what it claims.
- **Positive control (task1b):** the hand-written relay_flood plant, run with plant_viability semantics on the same 35 cells, also reproduces its recorded acc exactly in 35 of 35 (known-answer).
  - Fresh-seed mean: .5036 original, .5090 inward (random cells +.015).
  - 0 of 35 reach lo99 > .55 under either placement.
- **Caveat (required):** the champions were selected under the wrong placement. This is a lower bound on what search would find under the correct placement, not an estimate of it.
- **Strongest objection:** a chance-level champion cannot gain from any placement, so F1 alone does not separate "placement artefact" from "search failure". F3 separates them analytically.
- **Unresolved:** a bounded re-search under inward placement on the 17 graph cells that are open under both placements (next question 2).

**F2 [V] Timing and light-cone ceilings for all 358 RELAY and MAJ evolve rows.** Confidence: high for the bound. The 50%-power threshold is a convention.
- **The model is an upper bound for any program.** It rests on these engine facts:
  - SENSE enters only through an awake site's registers and is not latched (engine.py:303-316).
  - Packets wait in Acc until the receiver is awake.
  - S changes only on awake ticks (engine.py:369), and the readout is the actuator's S0.
  - Delay is at least max(1, lat_base + lat_hop*dist) (engine.py:512).
  - Sync wake is t % period == 0. Async wake is independent per site and tick with p16(update_p).
- **Per trial:**
  - Sync: the earliest processing tick of each sensor's cue at the actuator, using the same logic as H-PLANT `lightcone.earliest` with the topology cached.
  - Async: the sensor's first awake tick j in the cue window has probability p(1-p)^j. The actuator must then be awake at some tick in [arrival+j, ro]. I condition on the actuator's last awake tick, and sensors are independent given that tick.
  - MAJ: Bayes accuracy given k arrived votes (majority, ties .5, reliability .7).
  - Optimistic: no loss, cap, collision or jitter; intermediate relays fire on arrival.
- **Known-answer checks:**
  - My transport (lc) component reproduces H-PLANT's lc_census bound exactly in 18 of 18 RELAY rows, including 6 with bound < .60.
  - The closed forms reproduce W2-A1 F7: .7877 (MAJ, async .5, cue loss only), .8369 (MAJ sync), .875 and .98 (RELAY single sensor).
- **Falsification attempt:** 0 of 69 SIGNAL rows exceed their joint ceiling. The minimum margin is +.038 (MAJ async 18c218f5: held .699, ceiling .737).
- **SIGNAL-attainable threshold:** every RELAY and MAJ evolve row has P=32 and K=12, so W2-B `min_true_to_cross(.55, 32, 12, power .5)` = .614 applies to all of them.

**F3 [V] Construction-capped NULL counts per family.** A row counts when its NULL could not have been won by any program, for light-cone, timing or placement reasons.

| Family | NULL evolve rows | Capped (ceiling < .614) | Ceiling <= .55 | Cause |
|---|---|---|---|---|
| RELAY | 146 | 17 | 16 | transport/light-cone alone in all 17; async cue loss alone caps 0 |
| MAJ | 143 | 34 | 25 | light-cone alone in 33; 1 only jointly with async cue loss (0677e0ae) |
| XOR | 83 | 36 | n/a | H-PLANT light-cone only; timing not analysed |
| FLIP | 82 | 24 | n/a | H-PLANT light-cone only; timing not analysed |
| **Total** | **454** | **111 (24%)** | | |

- **RELAY:** my 17 are a superset of H-PLANT's 16. The extra row is de5ad87b, ceiling .605.
- **MAJ:** 6 of the 34 are capped by placement only; their inward ceiling is at least .614. They are e41b7b13, 5edb4474, 09c6dc85 (the d=1 random rows: .55-.58 rising to .81-.82), 699c8b2a (.577 to .732), 0677e0ae (.605 to .619) and 0327a9ab (.607 to .670). 10 of the 34 are on torus, ring or global topology. H-PLANT's census excluded MAJ entirely.
- **The 35 MAJ graph evolve rows split three ways:**
  - 24 are capped under the recorded placement;
  - 18 stay capped under inward placement (6 placement-only);
  - 11 are open under both.
- **Answer to TASK 1:** the C1 MAJ graph NULLs were partly construction artefacts. Placement alone accounts for 6 of 35 analytically, and delta-versus-latency timing for 18 more. The rest are search or representation failures. No recorded champion benefits from correcting the placement.
- **Dominant mechanism:** delta=4 combined with lat_base 2-4. One hop already takes 4-5 ticks against a 4-tick window, and sync period 2 removes odd processing ticks on top of that.

TASK 1 table (fresh seeds; "rec" = recorded held acc; KA = known-answer exact; ceilings = joint):

| cell | topo | mode | d | delta | rec | KA | champion orig / inward (lo99 inward) | plant orig / inward | ceiling orig / inward |
|---|---|---|---|---|---|---|---|---|---|
| 4a06cfed | random | async | 3 | 8 | .500 | 1 | .500 / .500 (.500) | .516 / .514 | .659 / .739 |
| 3a2f0152 | smallworld | sync | 1 | 16 | .510 | 1 | .497 / .505 (.488) | .510 / .522 | .837 / .837 |
| 0677e0ae | smallworld | async | 2 | 4 | .505 | 1 | .508 / .496 (.482) | .493 / .501 | .605 / .619 |
| 67e459d7 | smallworld | sync | 3 | 4 | .493 | 1 | .499 / .508 (.499) | .512 / .487 | .528 / .500 |
| 699c8b2a | random | async | 2 | 4 | .503 | 1 | .508 / .507 (.496) | .501 / .531 | .577 / .732 |
| c9d2ff6e | random | async | 5 | 4 | .500 | 1 | .500 / .500 (.500) | .473 / .521 | .545 / .500 |
| 3fd0dbcd | random | async | 2 | 16 | .496 | 1 | .502 / .480 (.455) | .505 / .546 | .788 / .788 |
| 0327a9ab | smallworld | sync | 2 | 4 | .500 | 1 | .500 / .500 (.500) | .500 / .527 | .607 / .670 |
| afc07cc5 | smallworld | sync | 3 | 4 | .500 | 1 | .500 / .500 (.500) | .495 / .505 | .509 / .500 |
| 911e7048 | smallworld | async | 2 | 4 | .493 | 1 | .498 / .475 (.449) | .497 / .452 | .500 / .500 |
| 773e7fa3 | smallworld | async | 2 | 4 | .500 | 1 | .497 / .498 (.492) | .492 / .485 | .500 / .500 |
| 8bf069cf | smallworld | async | 3 | 16 | .501 | 1 | .503 / .493 (.480) | .526 / .499 | .690 / .703 |
| 14e62ff5 | random | async | 1 | 16 | .498 | 1 | .501 / .505 (.489) | .508 / .585 | .796 / .812 |
| bf1f3a10 | smallworld | async | 3 | 4 | .486 | 1 | .490 / .492 (.461) | .503 / .495 | .683 / .703 |
| 6dd65b5a | smallworld | sync | 3 | 16 | .497 | 1 | .496 / .497 (.474) | .524 / .520 | .837 / .837 |
| ab5c2944 | random | sync | 3 | 4 | .504 | 1 | .499 / .497 (.484) | .500 / .500 | .523 / .500 |
| 44a3159d | smallworld | sync | 2 | 4 | .500 | 1 | .500 / .500 (.500) | .484 / .487 | .500 / .500 |
| de60a65c | random | sync | 5 | 4 | .494 | 1 | .490 / .513 (.478) | .505 / .478 | .500 / .500 |
| 19df30b9 | smallworld | async | 3 | 4 | .493 | 1 | .510 / .500 (.475) | .512 / .504 | .522 / .500 |
| c7ec8097 | smallworld | sync | 2 | 16 | .500 | 1 | .500 / .500 (.500) | .471 / .477 | .837 / .837 |
| a4685b67 | random | async | 3 | 4 | .500 | 1 | .500 / .503 (.500) | .503 / .487 | .502 / .502 |
| b75a4981 | random | async | 3 | 4 | .500 | 1 | .500 / .500 (.500) | .496 / .470 | .500 / .500 |
| cf195eaf | smallworld | sync | 3 | 8 | .507 | 1 | .518 / .489 (.458) | .492 / .492 | .516 / .500 |
| 7977cef5 | random | async | 3 | 4 | .503 | 1 | .501 / .509 (.493) | .512 / .509 | .528 / .500 |
| 4704ff70 | random | async | 3 | 4 | .510 | 1 | .510 / .503 (.489) | .496 / .512 | .522 / .504 |
| f88e5299 | random | async | 3 | 4 | .505 | 1 | .501 / .493 (.474) | .508 / .500 | .514 / .500 |
| 92796727 | smallworld | async | 3 | 4 | .503 | 1 | .491 / .510 (.492) | .516 / .508 | .524 / .500 |
| 16e48268 | smallworld | async | 3 | 4 | .497 | 1 | .520 / .493 (.466) | .492 / .505 | .512 / .500 |
| 6f9bd088 | smallworld | async | 3 | 4 | .492 | 1 | .492 / .498 (.483) | .479 / .501 | .518 / .500 |
| e41b7b13 | random | sync | 1 | 8 | .500 | 1 | .500 / .500 (.500) | .513 / .525 | .553 / .811 |
| 09c6dc85 | random | sync | 1 | 8 | .513 | 1 | .500 / .495 (.475) | .518 / .546 | .584 / .814 |
| 5edb4474 | random | sync | 1 | 8 | .500 | 1 | .499 / .483 (.465) | .497 / .554 | .569 / .819 |
| acf58f34 | smallworld | sync | 1 | 8 | .536 | 1 | .536 / .533 (.519) | .537 / .524 | .774 / .788 |
| 81c30134 | smallworld | sync | 1 | 8 | .500 | 1 | .500 / .500 (.500) | .494 / .501 | .781 / .794 |
| f29ca123 | smallworld | sync | 1 | 8 | .513 | 1 | .526 / .520 (.498) | .546 / .544 | .781 / .793 |

Group means:
- 17 rows open under inward placement: champion .504 -> .5005; plant .510 -> .524.
- 18 rows capped under inward placement: champion .5015 -> .4995; plant .498 -> .495.

TASK 2 table: construction-capped NULL rows. Columns: lc = transport/parity ceiling, cue = async cue-loss ceiling, joint = both, inward = joint ceiling under inward placement; attainable = .614 for every row.

RELAY (17 rows; all wave A; inward does not apply):

| cell | topo | mode | period or p | d | delta | lat base/hop | held | lc | cue | joint |
|---|---|---|---|---|---|---|---|---|---|---|
| eb081d9b | smallworld | async | .8 | 5 | 16 | 4/1 | .500 | .500 | .98 | .500 |
| 9d374e18 | torus | async | .8 | 2 | 4 | 4/1 | .495 | .500 | .98 | .500 |
| 526da0c0 | random | async | .5 | 5 | 8 | 1/1 | .500 | .500 | .875 | .500 |
| 055286f8 | random | sync | 2 | 1 | 4 | 4/1 | .491 | .500 | 1 | .500 |
| e23633ea | torus | async | .5 | 2 | 8 | 4/1 | .503 | .500 | .875 | .500 |
| 6d0eab4b | smallworld | sync | 2 | 3 | 4 | 2/1 | .499 | .500 | 1 | .500 |
| 58f97ecf | random | sync | 1 | 5 | 4 | 4/1 | .500 | .500 | 1 | .500 |
| db8782d5 | smallworld | async | .5 | 3 | 4 | 1/1 | .503 | .500 | .875 | .500 |
| 3ee1df85 | smallworld | sync | 2 | 3 | 8 | 2/1 | .493 | .500 | 1 | .500 |
| 8a47a64b | torus | sync | 2 | 3 | 16 | 4/1 | .518 | .500 | 1 | .500 |
| 900ec359 | ring | sync | 1 | 1 | 4 | 4/1 | .500 | .500 | 1 | .500 |
| ea5fca03 | smallworld | sync | 1 | 2 | 4 | 4/1 | .499 | .500 | 1 | .500 |
| 3c372b39 | smallworld | sync | 1 | 3 | 4 | 2/1 | .500 | .500 | 1 | .500 |
| c90a8d57 | random | sync | 2 | 5 | 4 | 1/1 | .508 | .500 | 1 | .500 |
| 9e5842f9 | ring | sync | 2 | 5 | 8 | 4/1 | .500 | .500 | 1 | .500 |
| ffbd28b0 | smallworld | sync | 1 | 5 | 8 | 1/1 | .500 | .508 | 1 | .508 |
| de5ad87b | random | sync | 2 | 5 | 16 | 4/0 | .500 | .605 | 1 | .605 |

MAJ (34 rows; the cue ceiling is .837 for sync, .788 for async .5 and .827 for async .8; "n/a" = not a graph topology):

| cell | wave | topo | mode | period or p | d | delta | lat base/hop | held | lc | joint | inward |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bc5e4f11 | A | global | async | .8 | 2 | 4 | 4/1 | .492 | .500 | .500 | n/a |
| 15d2a3e9 | A | global | async | .8 | 1 | 4 | 4/1 | .500 | .500 | .500 | n/a |
| b8057a11 | A | torus | async | .5 | 5 | 8 | 4/0 | .501 | .500 | .500 | n/a |
| 3ee88ab6 | A | torus | sync | 1 | 5 | 4 | 2/0 | .503 | .500 | .500 | n/a |
| adbca007 | A | torus | async | .5 | 3 | 8 | 2/1 | .499 | .500 | .500 | n/a |
| 911e7048 | A | smallworld | async | .5 | 2 | 4 | 4/1 | .493 | .500 | .500 | .500 |
| 773e7fa3 | A | smallworld | async | .5 | 2 | 4 | 4/1 | .500 | .500 | .500 | .500 |
| 44a3159d | A | smallworld | sync | 1 | 2 | 4 | 4/1 | .500 | .500 | .500 | .500 |
| f80a21d3 | A | torus | sync | 2 | 3 | 4 | 4/0 | .488 | .500 | .500 | n/a |
| de60a65c | A | random | sync | 2 | 5 | 4 | 4/1 | .494 | .500 | .500 | .500 |
| b75a4981 | A | random | async | .5 | 3 | 4 | 4/1 | .500 | .500 | .500 | .500 |
| c6a06b87 | A | ring | async | .5 | 5 | 4 | 2/1 | .517 | .500 | .500 | n/a |
| a4685b67 | A | random | async | .5 | 3 | 4 | 4/0 | .500 | .509 | .502 | .502 |
| afc07cc5 | A | smallworld | sync | 1 | 3 | 4 | 2/1 | .500 | .509 | .509 | .500 |
| 16e48268 | B | smallworld | async | .8 | 3 | 4 | 4/0 | .497 | .519 | .512 | .500 |
| f88e5299 | B | random | async | .8 | 3 | 4 | 4/0 | .505 | .522 | .514 | .500 |
| cf195eaf | A | smallworld | sync | 2 | 3 | 8 | 4/1 | .507 | .516 | .516 | .500 |
| 6f9bd088 | B | smallworld | async | .8 | 3 | 4 | 4/0 | .492 | .528 | .518 | .500 |
| 19df30b9 | A | smallworld | async | .5 | 3 | 4 | 2/1 | .493 | .544 | .522 | .500 |
| 4704ff70 | B | random | async | .8 | 3 | 4 | 4/0 | .510 | .534 | .522 | .504 |
| ab5c2944 | A | random | sync | 2 | 3 | 4 | 4/0 | .504 | .523 | .523 | .500 |
| 92796727 | B | smallworld | async | .8 | 3 | 4 | 4/0 | .503 | .538 | .524 | .500 |
| 7977cef5 | B | random | async | .8 | 3 | 4 | 4/0 | .503 | .544 | .528 | .500 |
| 67e459d7 | A | smallworld | sync | 1 | 3 | 4 | 1/1 | .493 | .528 | .528 | .500 |
| c9d2ff6e | A | random | async | .8 | 5 | 4 | 2/1 | .500 | .550 | .545 | .500 |
| e41b7b13 | B | random | sync | 2 | 1 | 8 | 4/1 | .500 | .553 | .553 | .811 |
| 5edb4474 | B | random | sync | 2 | 1 | 8 | 4/1 | .500 | .569 | .569 | .819 |
| 699c8b2a | A | random | async | .8 | 2 | 4 | 2/0 | .503 | .596 | .577 | .732 |
| 09c6dc85 | B | random | sync | 2 | 1 | 8 | 4/1 | .513 | .584 | .584 | .814 |
| 937703a8 | B | ring | sync | 2 | 5 | 8 | 4/1 | .531 | .600 | .600 | n/a |
| 45d695e0 | B | ring | sync | 2 | 5 | 8 | 4/1 | .528 | .600 | .600 | n/a |
| 8c802392 | B | ring | sync | 2 | 5 | 8 | 4/1 | .500 | .600 | .600 | n/a |
| 0677e0ae | A | smallworld | async | .5 | 2 | 4 | 1/1 | .505 | .791 | .605 | .619 |
| 0327a9ab | A | smallworld | sync | 2 | 2 | 4 | 1/1 | .500 | .607 | .607 | .670 |

**F4 [V] Recorded held acc can sit above .5 (up to .518) when no information about the current trial can reach the actuator.** Confidence: high.
- **Rows:** 4 sync rows have held acc above their exact held-set ceiling: 8a47a64b .518, c90a8d57 .508 (lo99 .503), 3ee88ab6 .503 and cf195eaf .507.
- **Deterministic engine check (`check_lightcone_exact.py`):** RNG draws do not depend on state. Negating trial k's cue alone changes S0 at trial k's readout in 0 worlds, for all 12 trials in all 4 rows.
- **Fresh seeds (4 x 64 worlds):** means .487, .501, .502 and .506.
- **Mechanism:** late-arriving cues from earlier trials are independent of y_k. They add zero-mean, non-zero-variance noise around .5 per pair.
- **Consequence:** a held acc a little above .5 is not evidence of transport, and the "no-transport gives exactly .5 per pair" property (W2-B P1) holds only when no information from any trial reaches the actuator.
- **Unresolved:** how much this inflates the false-positive rate of lo99 > .55 (next question 5).

**F5 [V] Inward placement is not uniformly easier.** Confidence: high.
- In 12 MAJ graph rows the inward ceiling is lower than the original one; for example 67e459d7 goes .528 -> .500 and c9d2ff6e .545 -> .500.
- **Reason:** inward placement puts every sensor exactly at transport distance d, which is outside the light cone when delta=4. The reversed placement had put some sensors closer by accident.

## 2. Proposed fixes
None from me. The placement fix is W2-I patches/envs_maj_inward_placement.diff and W2-A1 SEMANTIC_envs_maj_forward_placement.diff; I endorse it, SEMANTIC, for C2 only.

Recommendation, SEMANTIC (C2 design): before spending compute on a cell, compute its joint ceiling with `task2_timing.ceilings()`. Admit the cell only if the ceiling is at least the gate's attainable accuracy (.614 for SIGNAL at P32 K12, .70+ for INTEGRATION). This is new tooling, not a fix, so it comes with no diff or test.

## 3. Disagreements
- **H-PLANT lc_census** omits MAJ, yet MAJ has the most construction-capped evolve NULLs (34 of 143). The census is also optimistic under async: it ignores cue loss and actuator wake. That changes 1 MAJ row and no RELAY row.
- **W2-A1 F1 "random level about .62 with forward placement"** describes the transect census cells. It does not carry over to the MAJ evolve cells: 18 of 35 stay capped below .614 under correct placement, and the relay_flood plant averages only .509.
- **W2-I F4 objection** ("may be NULL for other reasons too"): confirmed. Correct placement alone uncaps only 6 of 35. Timing caps 18 regardless of placement. 11 are open under both, and those are search failures.
- **W2-B "no-transport readouts give exactly .5 per pair"**: true only without stale information from earlier trials (F4).

## 4. Next questions (ranked)
1. Should C2 gate cells on the joint ceiling? 111 of 454 evolve NULL rows (24%) across RELAY, MAJ, XOR and FLIP were unwinnable by construction.
2. A bounded inward-placement re-search (needs authorisation) on the 17 MAJ graph cells open under inward placement, especially the 6 placement-only cells. Does search reach SIGNAL there?
3. Extend the async cue-loss and actuator-wake terms to XOR (both inputs needed) and FLIP. The H-PLANT counts of 36 and 24 are light-cone only.
4. Re-express the A0 dial_effects and interaction tables as ceiling-normalised accuracy, (acc-.5)/(ceiling-.5). How much of the "delta" and "latency" effects is the light-cone identity?
5. False-positive rate of lo99 > .55 under stale-information noise alone (F4): does pair_ci still give its nominal 1%?
6. MAJ async .5 SIGNAL rows sit at .68-.70 against a joint ceiling of .737, so INTEGRATION (> .70) is nearly unattainable there. Should the C2 INTEGRATION bar be ceiling-relative?

## 5. Inference ledger
question | evidence | result | confidence | strongest objection | unresolved | next
- Are the MAJ graph NULLs placement artefacts? | task1 (35 champions), task1b (plant), task2 inward ceilings | 0/35 SIGNAL, mean change -.003; 6/35 capped by placement only, 18 by timing | high | champions were selected under the wrong placement (lower bound) | re-search under inward placement | Q2
- Known-answer reproduction | held acc/lo99 exact 35/35 (23 non-trivial); plant acc 35/35 | pass | high | none | none | none
- Timing/light-cone ceilings | task2_timing.py; 18/18 match to H-PLANT; A1 F7 closed forms; 0/69 SIGNAL rows above ceiling | RELAY 17/146, MAJ 34/143 capped | high | the .614 threshold is 50% power, not impossibility (strict <= .55: 16 and 25) | XOR/FLIP timing | Q3
- Held acc above the ceiling in 4 sync rows | check_lightcone_exact.py (0 S0 changes over 48 trial-flips); fresh means about .5 | stale-information noise, not a model failure | high | only 4 rows checked | FP rate | Q5
- Is inward placement monotone easier? | task2 inward vs original ceilings | no; 12 rows get lower ceilings | high | none | none | C2 placement design
- Per-family construction-capped count | analyze_join.py | RELAY 17, MAJ 34 (6 placement-only), XOR 36, FLIP 24 (light-cone only); total 111/454 | high (RELAY/MAJ), medium (XOR/FLIP: optimistic under async) | XOR/FLIP undercounted | timing extension | Q1, Q3

## 6. Compute used
About 1540 CPU-seconds, or 0.43 core-hours, against a 0.6 cap:

| Run | CPU-s |
|---|---|
| task1 | 571 |
| task1b | 481 |
| task2 | 164 |
| lightcone exact check | 318 |
| smoke | about 5 |

All runs were CPU-only, 2 threads, eager, with 64 worlds (32 pairs) or fewer per evaluation. No search was run.
