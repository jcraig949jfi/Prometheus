# PTE-C3S result: selector resolution on graded FLIP stones

**Provenance**
- Freeze: 7f049f1ec (prereg PREREG_PTE_C3S.md).
- Run: 10:06:53Z to 14:41Z on 2026-10-07. 95 of 112 jobs ran. The 4h30 deadline censored the last seed rounds, and
  every arm equally (n = 24/24/23/24).
- Integrity: 0 flags. Every S8 replay gate passed: S8 reproduces C2C's OP0_STEP champions exactly.
- Verdicts come from the frozen reduce_c3s.py (REDUCE_C3S.json). Section 3 is descriptive.

## 1. Frozen verdict: SELECTOR_RESOLUTION_EFFECT (and no shaping interference)

| arm | M | shaping | A: lineage and function survive | B: function erodes | C: lineage dies | D: climbs to competence | retained (A + D) | median best-lineage held B (stone .61) |
|---|---|---|---|---|---|---|---|---|
| S8 | 8 | on | 8 | 10 | 6 | 0 | 8/24 | .520 |
| W8 | 8 | off | 7 | 11 | 4 | 2 | 9/24 | .523 |
| S32 | 32 | on | 18 | 1 | 0 | 5 | **23/24** | .638 |
| W32 | 32 | off | 18 | 1 | 2 | 2 | **20/23** | .633 |

**M effect (M32 − M8, paired by stone, pooled over shaping): +.55.**
- Sign test p = 1.1e-7; stone-bootstrap 95% interval .35-.74.
- Positive in all four cells: FLIP-0000 +.63, FLIP-0004 +.79, FLIP-0099 +.46, FLIP-0167 +.33.

**Shaping effect (off − on): −.02**, p 1.0, interval −.11 to +.07. There is no shaping interference.

**Competence climbs (class D):** 7 under M32 against 2 under M8, in 3 cells.

**Monitor trajectories** (median best-lineage B on monitor worlds, gens 0 → 35):
- M8 decays from .60 to about .51 by generation 18.
- M32 holds at .60, then rises to .615-.62.

**Decision rule applied:** C3R uses M32 in every arm.

## 2. Answer to the order's Q1

**Q1. Was graded FLIP function being lost because selection could not resolve it?** Largely yes.
- With 4 training pairs (M 8), a B ≈ .6 partial function cannot be told apart from noise-fit genomes, and the stone
  lineage drifts to chance even while it keeps winning (lineage retained, function eroded: C2C's observation,
  reproduced here as class B at M8).
- With 16 pairs (M32), the same stones keep their partial function in 43/47 searches and sometimes climb to full
  competence.
- The C2C "graded stones decay" finding is therefore mostly a selector-noise artefact. It is not evidence that the
  representation has no climbable path from a graded near-plant.

## 3. DESCRIPTIVE: the 9 competence climbs (assay_c3s_climbs.py)

- **Fresh worlds:** all 9 are competent on 256 fresh worlds (B .864-.958).
- **Controls:** all 9 lose competence when the teacher is removed after trial 0, and all 9 under zero
  communication. They use the teacher and the packets.
- **Carrier (swap_v2):** S0 (the readout/mapping register) reads FLIP in 5 of 9. Msum (in flight) reads PARTIAL. S1
  is PARTIAL or NO_EFFECT. One champion's targeted-trial subset failed the swap competence gate, so swaps are not
  informative for it.
- **Line distance:** every climb is 3-6 instruction lines from the plant of record. The stones are 1-2 edits away.
  So these are local near-plant repairs from a partially functional start, not new mechanisms.
- **Lineage:** all 9 champions descend fully from the stone (share 1.0).

## 4. What this changes

- The search does have a local gradient near a working FLIP mechanism, provided the selector can see it. C2A's
  "0/81 broken starts recovered" and C2C's graded-stone collapse were measured at M 8.
- Earlier M 8 FLIP results remain valid as measured, but they confound "no path" with "path invisible to the
  selector". C2A M32 from RANDOM starts found nothing (0/32), so selector resolution alone does not open FLIP from
  random initialisation. It preserves and climbs partial function once that function exists.
- C3R is therefore run at M32, so the representation arms are not judged with a selector known to erase partial
  function.

## 5. Files

- REDUCE_C3S.json; c3s_production/rows_C3S.jsonl.gz (95 rows, with per-generation monitor curves); c3s_production/pops_C3S.tar;
  c3s_production/assay_climbs.json.
- PREREG_PTE_C3S.md, FREEZE_C3S.json, PLAN_C3S.json, c3s_flight/.
