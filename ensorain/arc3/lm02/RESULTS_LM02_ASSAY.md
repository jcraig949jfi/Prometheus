# RESULTS: LM02 bounded window-sufficiency assay + PKG-F-HIER

Run:
- prereg ensorain/arc3/lm02/PREREG_LM02_ASSAY.md, committed at 8b49a4456 BEFORE the run;
- 88 eval worlds (9_815_xxx), 8 workers, BELOW_NORMAL, M2;
- rows results/lm02_assay.json, verdicts results/lm02_verdict.json (score.py, unchanged since the precommit).

The first launch crashed at task 1 (a runpy/multiprocessing pickling error in the launcher; no rows existed). It was
relaunched unchanged through an importable wrapper.

## Verdicts (as computed by score.py)

| item | verdict |
|---|---|
| INSTRUMENT | OK: REF_HOLD preserved 83/88 (94%) |
| WINDOW | **WINDOW_NOT_SUPPORTED.** No window preserves >= 6/8 worlds in ANY regime. STOP; no tuning |
| POP | **POP_VALUE_REQUIRES_REPRESENTATIVENESS (falsified by HIDDEN)** |

Predictions:
- **L1 CONFIRMED** (not window-sufficient).
- **L2 CONFIRMED** (the POP verdict).
- **L3 CONFIRMED:** HIER_det false freshness <= .10 everywhere but HIDDEN. LOCAL_BOX .007 and MODE_SLAB .022 are the
  misaligned regimes.
- **L4 REFUTED:** see "Global pool vs strata" below.

## Preservation (worlds of 8)

| policy | STAT | ABRUPT | DIFFUSE | RAMP05 | RAMP20 | RAMP50 | MULTI | L_BLOCK | L_BOX | M_SLAB | HIDDEN |
|---|---|---|---|---|---|---|---|---|---|---|---|
| REF_HOLD | 8 | 8 | 8 | 7 | 7 | 6 | 8 | 8 | 8 | 7 | 8 |
| FULL | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 5 |
| ORACLE | 8 | 4 | 8 | 4 | 6 | 1 | 5 | 7 | 8 | 5 | 8 |
| WINDOW_12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| WINDOW_6 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 |
| WINDOW_3 | 0 | 3 | 0 | 5 | 4 | 0 | 1 | 1 | 0 | 0 | 0 |
| WINDOW_2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| STRICT_det | 0 | 2 | 0 | 4 | 5 | 0 | 3 | 0 | 0 | 1 | 0 |
| STRICT_orc | 8 | 2 | 0 | 4 | 1 | 0 | 5 | 1 | 0 | 0 | 0 |
| HIER_det | 6 | 2 | 0 | 4 | 5 | 0 | 3 | 3 | 0 | 1 | 0 |
| HIER_orc | 8 | 2 | 0 | 4 | 1 | 0 | 5 | 5 | 0 | 1 | 2 |
| POPG_det | 7 | 2 | 0 | 4 | 5 | 0 | 3 | 0 | 0 | 1 | 2 |

Component passes, 88 worlds (comp / ord / anom / contam):

| policy | comp | ord | anom | contam |
|---|---|---|---|---|
| WINDOW_12 | 0 | 47 | 61 | 88 |
| WINDOW_6 | 4 | 76 | 70 | 88 |
| WINDOW_3 | 23 | 82 | 83 | 69 |
| WINDOW_2 | 25 | 84 | 73 | 49 |
| STRICT_det | 20 | 78 | 82 | 83 |
| HIER_det | 33 | 80 | 80 | 83 |
| ORACLE | 72 | 81 | 84 | 88 |

## Readings

1. Why windows fail: a squeeze, not a tuning gap.
   - Short windows keep contamination at 0 but lose COMPETENCE. In STAT, WINDOW_2 reaches 1.76 AC vs 2.05 attainable;
     WINDOW_6 reaches 0.92.
   - Long windows keep competence only by admitting stale records. WINDOW_2's contamination is .26-.39 in
     ABRUPT/RAMP50/MULTI.
   - No window size sits inside both constraints in any regime.
   - Substrate ORDERING and the ANOMALY flag are far more robust than competence: WINDOW_3 keeps ordering in 82/88 and
     the flag in 83/88. The bounded-memory failure is a failure to reach the attainable competence level, not a
     failure to rank substrates.
2. Data availability dominates memory policy. After a change, even the best history subset (ATTAINABLE) sits
   .36-.95 AC below a full life of current-world data:
   - STAT -.003, ABRUPT .52, DIFFUSE .57, RAMP05/20/50 .65/.61/.75;
   - MULTI .95, LOCAL_BLOCK .45, LOCAL_BOX .46, MODE_SLAB .36, HIDDEN .61.
   This loss is not charged to any policy.
3. PKG-F-HIER, VALUE.
   - STAT: HIER_det recovers 76% of the STALE gap between STRICT and REF. Its best AC is 1.97 vs STRICT 1.08 vs 2.05
     attainable, and it retains 88% of valid records vs 36%.
   - LOCAL_BLOCK: recovery .25. Best AC 1.12 vs STRICT .80; retained 93% vs 48%.
   - ABRUPT / DIFFUSE / RAMP* / MULTI: the bound never passes (0 supported records). HIER equals STRICT: conservative,
     as designed.
4. PKG-F-HIER, SAFETY. Pooled stale fraction among POPULATION_SUPPORTED records:

   | regime | stale / supported | fraction |
   |---|---|---|
   | STAT | 0/26807 | 0 |
   | LOCAL_BLOCK | 0/21375 | 0 |
   | LOCAL_BOX | 2/281 | .007 |
   | MODE_SLAB | 91/4186 | .022 |
   | **HIDDEN** | **3372/27212** | **.124 > p_max .10** |

   HIER_orc in HIDDEN reaches .210. Sensitivity: p05 .126 and p20 .125 in HIDDEN.
   - The Markov bound is honest ONLY for the tested cells. In HIDDEN the tested sample is truthfully unchanged, so the
     bound is small and supports cells whose change is invisible to it.
   - No statistic computed on the observed cells can detect this. Safety requires an exchangeability assumption
     (tested ~ untested) that observation alone cannot certify.
5. Global pool vs strata (L4 REFUTED, in the safe direction).
   - POPG_det supported records ONLY in STAT and HIDDEN (HIDDEN .125).
   - In localized regimes, the localized change inflates the global bound, so the global pool supports nothing. It
     fails CONSERVATIVE, not unsafe.
   - The cost of global pooling is lost value, not leakage: LOCAL_BLOCK preservation POPG 0/8 vs HIER_det 3/8 vs
     HIER_orc 5/8.
   - Stratification is what lets unchanged regions be reused beside a changed one.
6. Gradual drift: detector placement vs memory policy.
   - RAMP05: det = orc (4/8, STRICT and HIER).
   - RAMP20: det 5/8 > orc 1/8. The ORACLE boundary (ramp end) keeps too little data. The mid-ramp detector placement
     trades a little contamination for competence and does BETTER on preserved conclusions.
   - RAMP50: 0/8 at both boundaries and for every window.
   - So the RAMP failures are memory-policy/data failures, not detector-placement failures. The detector was not
     repaired, and nothing here says it must be for interpretability.

## Disposition

- LM02 bounded assay CLOSED: WINDOW_NOT_SUPPORTED.
  - Under these dynamics, bounded temporal memory preserves the ORDERING and ANOMALY conclusions most of the time,
    but not attainable competence.
  - Every window size is squeezed between data loss and stale contamination.
- PKG-F-HIER: available as a LABELED experimental arm, never the gate of record.
  - It adds real value where the tested cells are representative (STAT 76% recovery, LOCAL_BLOCK).
  - It is conservative under diffuse and global change.
  - It is UNSAFE when drift hides in unrevisited cells (HIDDEN .124 > .10).
  - Answer to the ruling's question: temporal knowledge cannot safely generalize from observed to unobserved cells
    under these dynamics WITHOUT a structural assumption about which cells get revisited. Population evidence is safe
    only up to that assumption.
- The strict PKG-F gate (pkgf_obs.obs_keep) remains the conservative reference and the gate of record.
