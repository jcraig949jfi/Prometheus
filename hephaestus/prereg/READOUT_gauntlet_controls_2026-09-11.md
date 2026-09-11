# READOUT -- closure gauntlet controls on the boolean specs (HEPH-09 / HEPH-10), 2026-09-11

**Script:** `hephaestus/src/gauntlet_controls.py` (expectations fixed in the file before the run).
**Rows:** `hephaestus/closure_results/controls_vacuous_truth.json`, `controls_consistency_check.json`
(every witness and alias listed; workspace receipt inside). Console: `controls_console_2026-09-11.txt`.
**Protocol:** depth 3, budget 300,000 per arm, frozen basis A2-GENERIC-v1 (7f2ef69196e7f128), seed 20260911.
**Author:** Hephaestus (conflicted: author of the gauntlet and of these controls). All numbers E3.

## Result: ALL_PASS on both specs

| spec | control | expectation (pre-stated) | observed | PASS |
|---|---|---|---|---|
| vacuous_truth | NEGATIVE (seeded random column) | n_mechanism == 0 in A1, A2, B | A1 0 mech / 0 alias (300,000 evaluated); A2 0 / 0 (300,000); B 0 / 0 (107,629, exhausted) | yes |
| vacuous_truth | POSITIVE-A1 `pigeonhole_check(d, s)` | witness at depth 1, named expression present | 5 witnesses, min depth 1, named present | yes |
| vacuous_truth | POSITIVE-B `eq(d, s)` | witness at depth 1, named present | 5 witnesses, min depth 1, named present | yes |
| vacuous_truth | CHEAT: real kernel injected as `decoy_kernel` | depth-1 decoy witness on every route in A1+decoy; decoy present in A2-only | universal: baseline A1 3 witnesses at min depth 2 -> 5 at depth 1; negative_universal 5@1 -> 5@1; existential 5@1 -> 5@1; A2-only decoy present on all three | yes |
| consistency_check | NEGATIVE | n_mechanism == 0 in A1, A2, B | A1 0/0 (55 evaluated, exhausted); A2 0/0 (908); B 0/0 (20) | yes |
| consistency_check | POSITIVE-A2 `is_none(topological_sort(rels))` | witness at depth 2, named present | 5 witnesses, min depth 2, named present | yes |
| consistency_check | POSITIVE-B `has_cycle_dfs(rels)` | witness at depth 1, named present | 2 witnesses, min depth 1, named present | yes |
| consistency_check | CHEAT | as above | **baseline A1: 0 witnesses -> A1+decoy: 1 witness at depth 1**; A2-only decoy present | yes |

## What this establishes, and only this

- On the two boolean specimens the gauntlet does not hallucinate a mechanism on a random target
  (negative), finds a named reachable expression at its true depth (positive), and reports injected
  success through the channel it claims to measure (cheat) -- including on `consistency_check`,
  where the frozen arm is empty and the decoy is the ONLY witness. The cheat control is the one the
  operator made constitutional on 2026-09-11 and it is now executed for every specimen the seat
  has run: Q045 (arm C), vacuous_truth, consistency_check.
- Together with Q045 this is: one constructed OPERATOR positive in the vector regime, and
  negative/positive/cheat controls in the boolean regime. It is NOT "the gauntlet is validated"
  (operator ruling 2/3: experimental until controls establish broader discrimination). It is not a
  statement about the boolean specimens' CLASSIFICATIONS, which stand as recorded on 2026-09-01.
- A limitation of the negative control as built: the random column produced zero coerced aliases
  on the search points (21 points for vacuous_truth), so the alias column was not exercised by it;
  the positive evidence that the alias column works remains Q045's CONTROL set (5 aliases) and
  vacuous_truth's existential route (8,239 aliases on the real target). A negative control with a
  planted search-point coincidence is a reasonable next control (not built today).

## Reproduce

    python -m hephaestus.src.gauntlet_controls          # both specs, ~2.6 min, deterministic
    python -m hephaestus.src.gauntlet_controls vacuous_truth
