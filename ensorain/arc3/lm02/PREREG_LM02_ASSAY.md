# PREREG: LM02 bounded window-sufficiency assay + PKG-F-HIER (dev, CPU, no campaign)

Authority:
- operator direction 2026-09-30 (roles/Ensorain/prompts/2026-09-30_operator_direction/);
- operator ruling 2026-09-30 (roles/Ensorain/prompts/2026-09-30_pkgf_pop_lm02_ruling/).

This replaces the broad PKG-LM02 v0.2 research design (ensorain/arc3/packages/PKG_LM02_DESIGN.md, now PARKED) with a
bounded instrument test.

Code:
- ensorain/arc3/lm02/assay.py (worlds, policies, substrates);
- ensorain/arc3/lm02/score.py (the verdict rules below, verbatim in code).

Both are committed with this file BEFORE the evaluation run.

## 1. Question

Under what environmental regimes can bounded temporal memory preserve the downstream conclusions we care about, and at
what stale contamination? The conclusions are competence, substrate ordering and the anomaly flag.

## 2. Worlds (11 regimes x 8 = 88 worlds; eval seeds 9_815_000 + 100 j + i)

Common set-up:
- L2 geometry 12x12x12, N = 6400 records, one L2 walk (families.walk), noise .1 on standardised fields.
- Generator alternates cp/tt by seed.
- Single-switch regimes switch at 2N/3.

| regime | change |
|---|---|
| STAT | none |
| ABRUPT | all cells, step |
| DIFFUSE | 30% random cells, step |
| RAMP05 / RAMP20 / RAMP50 | all cells, linear ramp of width .05 / .2 / .5 of the life, centred at 2/3 (three drift rates) |
| MULTI | 6 episodes, 5 switches, each rho from {1, .5, .1, 0} |
| LOCAL_BLOCK | one octant (ALIGNED with the HIER strata), step |
| LOCAL_BOX | a 7x7x7 box at a random offset (MISALIGNED; crosses strata), step |
| MODE_SLAB | 3 random index values of one mode (a slab through every stratum), step |
| HIDDEN | ADVERSARIAL: cells NOT visited after the switch, each with p = .5. Changed cells are systematically absent from the tested sample. This is the main falsifier |

Ground truth:
- A record is STALE iff |s_i - x_final| > DELTA = .25 (the PKG-F DELTA).
- Test splits against x_final: RECENT (seen in the last N/6), STALE (seen, not recently), GEN (never seen). Up to 512
  cells each.

## 3. Policies (a kept record set, with a provenance label per record)

| policy | kept | label |
|---|---|---|
| FULL | all | UNVERIFIED (diagnostic) |
| ORACLE | truly non-stale | ORACLE (diagnostic) |
| WINDOW_12 / 6 / 3 / 2 | last N/12, N/6, N/3, N/2 | UNVERIFIED |
| STRICT_det | repaired strict gate (pkgf_obs.obs_keep, UNCHANGED), boundary = detector v9b, fallback 5N/6 | POST, CERTIFIED_FRESH |
| STRICT_orc | the same gate at the ORACLE regime boundary | POST, CERTIFIED_FRESH |
| HIER_det / HIER_orc | STRICT + POPULATION_SUPPORTED (below) | POST, CERTIFIED_FRESH, POPULATION_SUPPORTED |
| POPG_det | HIER with one global stratum (the intentionally weak baseline) | as HIER |
| HIER_det_p05 / p20 | declared p_max sensitivity | as HIER |

The oracle boundary is:
- the switch time for single switches;
- the ramp END for ramps;
- the start of the last episode after a switch with rho > 0 for MULTI;
- 0 for STAT.

Not kept: QUARANTINED (UNKNOWN, unsupported) and CHANGED. The code asserts that HIER's POST+CERTIFIED_FRESH set equals
the strict gate's keep set, so the strict gate is untouched.

PKG-F-HIER (assay.hier_keep):
- States: CERTIFIED_FRESH (strict equivalence), CHANGED (|d| > 1.645 se), POPULATION_SUPPORTED, QUARANTINED.
  POPULATION_SUPPORTED is never merged with CERTIFIED_FRESH; labels are scored separately.
- Strata: the 8 octants of the index grid (each mode split at 6), declared before any data.
- Tested cell = >= 1 pre and >= 1 post record; q_i = d_i^2 - se_i^2 (unbiased for Delta_i^2).
- Stale-risk bound (distribution-free, Markov): the fraction of cells with |Delta| > DELTA is <= E[Delta^2] / DELTA^2.
  - pi_ucb = max(0, mean(q) + 1.645 sd(q) / sqrt(m)) / DELTA^2.
  - It is a one-sided 95% bound on the tested cells of the stratum.
- Governing p_max = .10. Sensitivity values .05 and .20 are reported, not governing.
- Coverage: >= 30 tested cells AND tested / (stratum cells with pre records) >= .20. Otherwise the stratum's UNKNOWN
  cells stay QUARANTINED.
- A supported stratum's UNKNOWN cells (untested or inconclusive) become POPULATION_SUPPORTED. CHANGED cells are never
  supported.
- The claim is "some reuse is justified", NOT "fresh".
- Graded reuse is not built (optional per the ruling).

## 4. Substrates and conclusions

Every substrate is fitted on the kept records only, in stream order:
- cheap competitors: CONST, TABLE (per-cell mean), MARGINAL (additive backfit);
- S-lowrank, S-cp, S-tt, S-dct, S-additive (WTP Selective, default recipes).

References: REF1-3 and REF_HOLD are the same walk re-observed from the FINAL field (independent noise draws). REF1-3
form the consensus; REF_HOLD is the noise control.

Per world and policy, with pooled AC = the mean over the available splits:
- competence: best pooled AC >= ATTAINABLE - .10, where ATTAINABLE = max(FULL, ORACLE) best pooled AC. The gap
  ATTAINABLE -> REF consensus is data-availability loss: reported per regime, never charged to a memory policy.
- ordering: Kendall tau(pooled AC over the 8 substrates, consensus) >= .60.
- anomaly: the world-level flag (best non-cheap - best cheap > .10) equals the consensus flag. It counts as agreement
  when the consensus margin is within +-.05 of .10 (ambiguous).
- contamination: stale fraction of the kept records <= .10.
- PRESERVED = all four.

Also reported: retained valid records, unnecessary quarantine, and false freshness per label (the stale fraction among
CERTIFIED_FRESH / POPULATION_SUPPORTED / POST records).

Dev calibration, disclosed. Non-eval seeds 9_814_1xx-3xx. The criteria changed three times before this commit:
1. A single REF became the REF1-3 consensus + REF_HOLD. One substrate's AC moves ~.2 between noise draws; FULL failed vs
   one REF in STAT.
2. Per-substrate anomaly flags became the world-level flag, for the same reason.
3. Competence moved from "vs REF" to "vs ATTAINABLE". Every policy, ORACLE included, failed vs REF in every changed
   world: data availability, not memory policy.

On the last dev pass REF_HOLD passed 11/11 and ORACLE 9/11.

## 5. Verdict rules (score.py)

- INSTRUMENT: REF_HOLD preserved in >= 90% of the 88 worlds. Otherwise INSTRUMENT_NOISY is reported beside every
  verdict.
- WINDOW_SUFFICIENT: two ADJACENT windows each preserve >= 6/8 worlds in EVERY regime.
- WINDOW_REGIME_DEPENDENT: not sufficient; some window reaches >= 6/8 in >= 9 of 11 regimes; and the best window differs
  across regimes. The dependency is reported against the declared variables: change type, ramp width, changed fraction.
- WINDOW_NOT_SUPPORTED: otherwise. STOP; no tuning.
- POPULATION_EVIDENCE_ADDS_VALUE requires both:
  - (i) VALUE: in STAT, HIER_det recovers >= 50% of the STALE-split gap between STRICT_det and the REF consensus
    (per-world (HIER - STRICT)/(REF - STRICT), averaged over the worlds with a gap > .05);
  - (ii) SAFETY: the realized stale fraction among POPULATION_SUPPORTED records <= p_max = .10, pooled per regime, in
    EVERY regime INCLUDING HIDDEN.
  - Value with safety everywhere except HIDDEN: "POP_VALUE_REQUIRES_REPRESENTATIVENESS (falsified by HIDDEN)".
  - Value while unsafe elsewhere too: POP_UNSAFE.
  - No value: POP_NO_VALUE.
- Gradual drift is reported at BOTH boundaries: STRICT/HIER _det vs _orc per RAMP regime. The det-orc difference is
  error from detector placement; the orc-attainable difference is error from memory policy. The detector is not
  repaired in LM02.

## 6. Predictions (writable-to-lose; from dev seeds only)

- L1: the window verdict is NOT WINDOW_SUFFICIENT. On dev, no window preserved competence in STAT: half the data costs
  ~.3 AC.
- L2: POP verdict = POP_VALUE_REQUIRES_REPRESENTATIVENESS. On dev seed 9_814_101, HIDDEN population-supported records
  were 14.5% stale.
- L3: HIER_det stale-risk safety holds (<= .10) in every non-HIDDEN regime, including the misaligned LOCAL_BOX and
  MODE_SLAB.
- L4: POPG_det (global pool) is less safe than HIER_det: a higher pooled false freshness in at least one of LOCAL_BLOCK,
  LOCAL_BOX, MODE_SLAB.

## 7. Resources

- 88 worlds x (14 policies + 4 references) x 8 substrates.
- 8 workers, OPENBLAS 1 thread, estimated ~15 min on M2 CPU.
- No GPU, no spend.
- Output: ensorain/arc3/lm02/results/lm02_assay.json and lm02_verdict.json.
