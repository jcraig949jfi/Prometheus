# PTE-C2A result packet: search-limit localization

Date: 2026-10-05. Prepared by Ananke, instance m1-46797183, on M1 with the RTX 5060 Ti.

**Provenance**
- Authority: operator order of 2026-10-05, roles/Ananke/prompts/2026-10-05_pte_c2a_directive/ (34bcebe4b).
- Frozen design: PREREG_PTE_C2A.md, freeze commit a5049119e, code 4cdc2e15b (addendum 99c07c209).
- Run: 362/362 jobs, 11:50:47Z to about 18:35Z (6.75 h; the projection was 6.6 to 8.4 h).
  - The 3 workers all exited with code 0.
  - There was no censoring, so every comparison uses complete, balanced seed groups.
- Stop flags: none. Every one of the 362 held evaluations read the plant TRUE. No held/train overlap. No
  ceiling violation.
- Verdicts come from the frozen reduce.py (REDUCE_C2A.json).
- Section 4 is POST-HOC and DESCRIPTIVE. It is labelled as such and does not change any frozen verdict.

## 1. Headline

**Positive control: CONTROL_ALIVE.** The RELAY-1h control (C1 d9cc d3 delta8) succeeded in 8/8 BASE searches
and kept its plant in 2/2 PSEED searches. The search harness is working.

| family | cells | verdicts | BASE success (pooled) | PSEED retention | frozen family verdict |
|---|---|---|---|---|---|
| RELAY-mh | 0010, 0019, 0027, 0032 | 4/4 S-LOCATED | 1/48 (95% CI 0.001-0.111) | 16/16 | **SEARCH_LIMIT_SUPPORTED** |
| FLIP | 0000, 0004, 0099, 0167 | 4/4 S-LOCATED | 0/48 (95% CI 0-0.074) | 16/16 | **SEARCH_LIMIT_SUPPORTED** |

Every cell met the conditions that rule out the other explanations before search ran:
- P: the physics ceiling is at least .846 at every cell;
- R: the plant passes the competence ruler on fresh worlds, and on every one of the cell's 46 held sets;
- V: every in-scope adversary reads FALSE.

Under those conditions the C1-protocol search essentially never finds the competence class: 1 success in 96
searches. When the solution is handed to it, selection keeps it in 32 of 32 seeds.

**Maximum claim (order s11).** Within the 8 admitted RELAY-mh and FLIP cells tested, C1-style competence failure
localizes to the search (construction), not to physics, representability, ruler failure, or selection.

The verdict at each cell assumes a true BASE rate. If that rate is .05, the cell is called S-LOCATED with
probability .88 (n = 12). All 8 cells, at k = 0 or 1, are consistent with true rates of about .1 or below.

## 2. Per cell

Every plant was re-encoded into the GA's sampling support (repair R1). The held-plant figure is the plant's median
accuracy over the cell's held sets.

| cell | physics | hops | ceiling | plant (admission acc / held median) | BASE | W0 | M32 | PSEED | KSEED k=1/2/4 | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| RELAY-0010 | random N100 | 3 | .98 | relay_refresh .727 / .736 | 0/12 | 0/8 | 0/8 | 4/4 | 2/1/0 of 4 | S-LOCATED |
| RELAY-0019 | torus N100 | 2 | .98 | relay_refresh .837 / .846 | 1/12 | 0/8 | 1/8 | 4/4 | 3/1/0 | S-LOCATED |
| RELAY-0027 | random N144 | 4-5 | .98 | relay_refresh .968 / .973 | 0/12 | 0/8 | 0/8 | 4/4 | 2/0/0 | S-LOCATED |
| RELAY-0032 | ring N100 | 3 | .846 | relay_refresh .720 / .747 | 0/12 | 0/8 | 0/8 | 4/4 | 0/0/0 | S-LOCATED |
| FLIP-0000 | random N64 | 2 | 1.0 | P_FLIP B .933 / acc .900 | 0/12 | 0/8 | 0/8 | 4/4 | 1/0/0 | S-LOCATED |
| FLIP-0004 | smallworld N64 | 3 | .977 | P_FLIP B .925 / .897 | 0/12 | 0/8 | 0/8 | 4/4 | 2/0/0 | S-LOCATED |
| FLIP-0099 | smallworld N144 | 2 | 1.0 | P_FLIP B 1.0 / 1.0 | 0/12 | 0/8 | 0/8 | 4/4 | 1/1/0 | S-LOCATED |
| FLIP-0167 | ring N100 | 2 | .966 | P_FLIP B .926 / .938 | 0/12 | 0/8 | 0/8 | 4/4 | 1/0/0 | S-LOCATED |

**The non-seeded successes (all at RELAY-0019):**
- BASE seed 4: a genuinely new relay. Every one of its 16 lines differs from the plant. Held accuracy .839,
  against the plant's .833, and the late half is live at .82.
- M32 seed 1: a marginal pass at accuracy .59, late half .585.

**Failed searches.** There were 222 failed BASE/W0/M32 searches across the 8 cells.
- Champions sit at chance:
  - RELAY-mh: median .538, maximum .586;
  - FLIP: median .500, maximum .545.
- None of these runs ever had a population member within 2 instructions of the plant.
- FLIP BASE selector maxima (median .62-.66 on 4 training pairs) do not carry over to held accuracy (.50). They
  are selector noise, not partial solutions.

**Strongest alternative explanation, per cell.** In each case the plant is a designer-tuned program, so "S"
means the GA did not find the designed mechanism or any other member of its competence class. It does not mean
the class is unreachable by every search. The genome space (16 lines, rules 1) and the budget (96 x 36) are the
C1 ones. A larger budget (B4X) was excluded by design and was not tested.

## 3. Response arms and the frozen landscape form

| family | W0 vs BASE (balanced n = 32) | M32 vs BASE | upper 95% bound on gain | KSEED recovery, k = 1 / 2 / 4 | frozen form |
|---|---|---|---|---|---|
| RELAY-mh | 0 vs 1 | 1 vs 1 | .079 / .129 | 7/16, 2/16, 0/16 | RESPONSIVE |
| FLIP | 0 vs 0 | 0 vs 0 | .107 / .107 | 5/16, 1/16, 0/16 | RESPONSIVE |

**Arms.** Neither shaping-off (W0) nor four times the selector worlds (M32) rescues search. Both differences
are bounded below .25. That is a measured "no response", not an assumed one.

**Frozen form.** The label RESPONSIVE comes only from the prereg clause "KSEED recovery > 0 at k >= 2". It rests
on 2/16 (RELAY) and 1/16 (FLIP) at k = 2. No response arm contributed. Section 4 shows that this clause measured
the wrong thing.

## 4. POST-HOC, DESCRIPTIVE: KSEED measured edit neutrality, not recoverability

This is analysis/kseed_break_check.py, run on the frozen code. For every KSEED search, the perturbed starting
genome was regenerated (the edit record matches the run row in all 96 cases) and scored with the frozen ruler on
that search's held worlds.

| family | k | start competent: the edit was neutral | start broken | broken starts that recovered |
|---|---|---|---|---|
| RELAY-mh | 1 | 7 | 9 | **0/9** |
| RELAY-mh | 2 | 2 | 14 | **0/14** |
| RELAY-mh | 4 | 0 | 16 | **0/16** |
| FLIP | 1 | 5 | 11 | **0/11** |
| FLIP | 2 | 1 | 15 | **0/15** |
| FLIP | 4 | 0 | 16 | **0/16** |

- **All 15 KSEED "recoveries" were neutral edits.** The starting genome was already competent and was simply
  kept. That is the same retention seen in PSEED.
- **0 of 81 genuinely broken starts recovered, including 0/20 at k = 1.**
- A broken start usually falls straight to chance: median accuracy .500, maximum .582. One field edit typically
  destroys the mechanism outright, with no partial-credit gradient back.

Read descriptively, the landscape around each plant is a competent point with some neutral directions. Off those,
competence falls to chance and is not recovered within 36 generations. Under the measured mutation/operator
neighbourhood, the known solution lies in a locally unrecoverable region: the order's LOCALLY_FLAT /
LANDSCAPE-FACT reading.

This reading is post-hoc. The frozen label stays RESPONSIVE. The fix belongs to the next design: KSEED should
condition on, or redraw until, a start that is actually broken. It is recorded as a prereg defect in s7.

## 5. Program questions (order s26)

1. **How often does ordinary search succeed once impossible and unmeasurable cells are removed?**
   - At the admitted multi-hop RELAY and FLIP cells: 1/96 (about 1%).
   - At the one-hop RELAY control: 8/8.
   - Removing those cells is itself most of the story. Of 200 candidates, only 17 RELAY and 4 FLIP were
     admissible. The rest were out of stratum, physics-capped, or had no working plant.
2. **Where search fails, can selection retain a known solution?** Yes: 32/32 PSEED retained competence. In 26 of
   those the exact plant was still the champion. The others drifted to a competent descendant. U is not the
   bottleneck at any cell.
3. **Does reduced selector noise help?** No. M32 gave 1/32 against BASE's 1/32 (upper bound on the gain .13) for
   RELAY, and 0/32 against 0/32 for FLIP.
4. **Does removing shaping help or hurt?** It does not help: 0/32 in both families.
   - Descriptively, for RELAY-mh it removes the sub-threshold climb. W0 champions sit at exactly .500 (median
     selector maximum .500), against .538 for BASE.
   - So shaping buys partial, non-competent signal and nothing more.
5. **How local is the basin?**
   - Edits that keep competence: k = 1, 12/32 (38%); k = 2, 3/32; k = 4, 0/32.
   - Recovery from a broken start: 0/81 (s4).
6. **Is RELAY-mh predominantly search-limited?** Yes: 4/4 cells S-LOCATED. SEARCH_LIMIT_SUPPORTED.
7. **Is FLIP predominantly search-limited?** Yes: 4/4 S-LOCATED, with BASE at 0/48.
8. **Are the two families governed by the same failure mode?** Yes, on every measured axis:
   - no search success;
   - full retention;
   - no response to W0 or M32;
   - the same neutral-or-dead edit structure.
9. **Which C1 interpretations must be revised?**
   - (a) **C1 NULLs at multi-hop RELAY and at FLIP are search NULLs** where the cell is admissible. They are not
     evidence about physics. The C1 phase-map readings for those families are maps of search.
   - (b) **"Evolved PTE transport is one hop"** is a statement about search reachability. Multi-hop forwarding is
     representable, retainable, and found 1/48 by search.
   - (c) **FLIP@d9cc as a "search gap"** generalizes: 0/48 at four fresh, fully admitted cells.
   - (d) **Most of C1's candidate space is not admissible at all.** Any population-level C1 rate mixes impossible
     cells with search failures.
10. **The single highest-information next PTE experiment.** A search-construction intervention at these same 8
    admitted cells, with the plants, rulers and held design already frozen and validated. Two options:
    - KSEED-broken: starts forced to be broken, at k = 1 and 2, to measure true recoverability;
    - B4X or STEP, to test whether budget or a stepping stone opens a gradient.

    Arms W0 and M32 are now known not to help, so the remaining open question is whether any operator-side change
    creates a path. Without one, H6 for these families reduces to the landscape fact in s4.

## 6. Admission funnel (P/R/V)

| family | candidates | out of stratum | P-CAPPED | R-NOT-ESTABLISHED | V-FAILED | admitted |
|---|---|---|---|---|---|---|
| RELAY-mh | 200 | 106 | 52 | 25 | 0 | 17 |
| FLIP | 200 | 0 | 147 | 48 | 1 (FLIP-0184: copy policy B .76, INDETERMINATE) | 4 |

## 7. Defects and threats to carry forward

- **KSEED design defect.** KSEED did not condition on a broken start, so 15/96 starts were already competent.
  The frozen RESPONSIVE label is an artifact of those starts (s4).
- **Same author.** One seat wrote the plants, rulers, adversaries and verdict code, and no external adversarial
  review came before the run.
- **Late-half guard.** Two-valued. The marginal M32 success at RELAY-0019 (.59 / .585) is the kind of champion it
  flips on.
- **Plant scope.** The plants are designer-tuned. "S" is relative to the C1 operator, budget and genome spec.
- **No in-situ randomize_source guard.** Mitigated: all 362 final populations and champions were saved
  (production/run/pops) and can be re-evaluated.

## 8. Files

- `REDUCE_C2A.json`: the frozen reducer's output.
- `production/rows_C2A.jsonl.gz`: all 362 rows, with curves, champions, namespaces and basins.
- `production/pops_C2A.tar`: the final populations.
- `analysis/kseed_break_check.py` and `analysis/kseed_break_check.json` (post-hoc).
- `PREREG_PTE_C2A.md`, `FREEZE_C2A.json`, `FREEZE_C2A_ADDENDUM.md`, `PLAN_C2A.json`.
- `admission/`, `flight1/` and `flight2/`.
