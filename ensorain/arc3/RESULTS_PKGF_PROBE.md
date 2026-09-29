# PKG-F prerequisite probe (DEV, 2026-09-28): restoring the discarded distinctions

Status: prerequisite probe allowed by directive Block F. Not preregistered; not a result about the law.
- Data: results/pkgf_probe.json. Code: pkgf_probe.py.
- 3 families (F2 noise, F3 obsolete, F5 spurious) x 2 generators x 4 dev worlds (seeds 9_800_000-003; shams
  9_850_000-003), L2, frozen LM01 SELECTIVE substrate at cap cells/4.
- 53 s, single process, BELOW_NORMAL.

## Instrument checks (all pass)

- LOSSLESS: (theta_S, D_S) reconstructs the admitted history to max error 8.9e-16.
- PC-help (restoration restores information): on exact-hit recall, S+D beats S in every stratum. Mean delta AC
  +0.45 .. +2.32.
- SHAM behaves as designed:
  - the learned readout IGNORES the size-matched sham (a = 0 in 23 of 24 worlds; delta 0.00);
  - the forced sham HURTS by -0.23 .. -1.32.
  - So "any extra records" burden is visible and a learned readout can opt out.

## Readings on the headline (never-seen / OOD) test. Mean delta AC vs S (4 worlds)

| stratum | S+D learned | S+D forced | SHAM learned | SHAM forced | learned a |
|---|---|---|---|---|---|
| F2 lowrank (noise) | +0.01 | +0.02 | 0.00 | -0.25 | 1, 1, .5, .5 |
| F2 spectral | +0.09 | +0.17 | 0.00 | -0.33 | .5 x4 |
| F5 cp (spurious) | 0.00 | +0.03 | 0.00 | -0.33 | 1, 1, .5, 1 |
| F5 spectral | +0.04 | +0.03 | 0.00 | -0.23 | .5, 1, .5, .5 |
| F3 cp (obsolete) | -0.90 | -1.13 | 0.00 | -0.91 | 1, 1, .5, .5 |
| F3 tt | -1.32 | -1.59 | 0.00 | -1.32 | 1, 1, .5, .5 |

## Reading (dev probe; provisional)

1. NOISE (F2) and SPURIOUS NUISANCE (F5): the restored discarded channel is nearly INERT for generalization, even when
   the readout is forced to use it. Discarding these distinctions was not causally necessary here. The prior from
   Kirichenko et al. (harm under forced use for spurious features) is NOT reproduced in this form.
2. OBSOLETE STRUCTURE (F3): restoring the discarded channel HURTS sharply, even under the readout that may ignore it,
   while the size-matched sham is ignored.
   - This is the SELECTIVITY_CAUSAL pattern of PKG-F s6. But the learned readout picks its weight on a holdout drawn
     from the WHOLE history, which is dominated by the old episodes.
   - The harm may therefore be a RETRIEVAL/SELECTION failure: the readout cannot identify which history is relevant
     (directive H). It may not be a property of the information itself.
   - Discriminator (added to PKG-F as a required arm): S+D/learned-recent, with the weight chosen on a holdout of the
     MOST RECENT records only (legitimate learner behaviour, no test leak). If the harm vanishes, obsolete history hurts
     only through readout selection. If it persists, the evidence for causal selectivity is stronger.
3. The F5 null and the F3 harm must both be tested against the NO-CHANGE control (PKG-F s7: stationary twins) before any
   causal reading.

## Consequence for the design

PKG-F moves from "design" to "instrument validated on dev". The next step is the recency-holdout arm and stationary
twins (cheap), then the preregistration after LM01 integration.

## v2: recency-holdout discriminator + stationary twins (results/pkgf_probe_v2.json; 32 dev worlds, 72 s)

Mean delta AC vs S on the headline test:

| stratum | S+D learned (holdout = all history) | S+D learned-recent (holdout = last 20%) | learned-recent weights |
|---|---|---|---|
| F3 cp (obsolete) | -0.90 | -0.01 | 0, .25, 0, 0 |
| F3 tt (obsolete) | -1.32 | 0.00 | 0, 0, 0, 0 |
| F2 cp (stationary twin) | +0.03 | +0.03 | .5, .5, 1, .5 |
| F2 tt (stationary twin) | 0.00 | 0.00 | 1, 1, .25, .25 |
| F2 lowrank / spectral | +0.01 / +0.09 | +0.01 / +0.09 | - |
| F5 cp / spectral | 0.00 / +0.04 | +0.03 / +0.04 | - |

DEV FINDING (provisional; 4 worlds per stratum; one readout family):
- The F3 harm from restoring obsolete distinctions VANISHES when the readout chooses its use of the channel on recent
  records. The obsolete information can stay stored and be IGNORED; it hurt only because the readout's selection
  signal was dominated by the old regime.
- In these worlds, discarding was NOT causally necessary. What mattered was the SELECTION SIGNAL (which records the
  readout trusts), not the storage.
- This bears directly on the ARC3 central question ("can irrelevant distinctions remain stored but simply be ignored?"):
  here, YES, given a regime-appropriate selection signal.
- Scope: an additive residual readout with a 4-value weight grid. The PKG-F campaign must add richer readouts, more
  worlds, the decaying-reliability nuisance (N5), and a regime-change detector that must DISCOVER recency rather than
  being handed "last 20%".

## v3: DISCOVERED recency (pkgf_cp.py), BIC binary segmentation on the residual sequence

- The holdout is the final detected regime. If nothing is detected, the random 20% holdout is used.
- The v2 worlds (seeds 9_800_000-003) are reported for comparability.
- The FRESH seeds 9_800_020-023 are the precommitted subjects. The detector was designed after seeing v2's aggregate
  table only, with no per-world tuning.

### Precommitment (written BEFORE running pkgf_cp.py)

- P1: F3 (cp, tt; 8 fresh worlds), mean dAC(SD_cp vs S) >= -0.10. The harm mostly vanishes; v2's all-history holdout
  gave -0.90 / -1.32.
- P2: F2 stationary twins (cp, tt; 8 fresh worlds): the detector finds NO change (cp_start = 0) in >= 6/8.
- P3: F2 twins (8 fresh worlds), |mean dAC(SD_cp) - mean dAC(SD_all)| <= .05. Discovery costs nothing without a regime
  change.

### v3 result (precommit commit 4ef32124c; results/pkgf_cp.json; 36 s on M2)

Fresh worlds (9_800_020-023), dAC vs S:

| stratum | SD_all (all-history holdout) | SD_cp (discovered) | detected regime start (fraction of stream) |
|---|---|---|---|
| F3 cp | -1.30 -1.63 -0.74 -1.70 | 0 0 0 -0.45 | .69 .67 .99 .999 |
| F3 tt | -1.39 -1.77 -0.99 -2.21 | 0 0 0 0 | .67 .98 .98 .67 |
| F2 cp twin | -.03 -.03 -.09 +.10 | identical | 0 .80 .81 0 |
| F2 tt twin | -.02 -.00 -.01 +.11 | -.01 0 0 0 | .92 .94 .996 .985 |

- **P1 SURVIVES:** F3 mean dAC(SD_cp) = -0.056 >= -0.10. The harm vanishes in 7/8 fresh worlds, with no handed-in
  recency. v2 worlds: 8/8 at 0.
- **P2 REFUTED:** the detector finds no change in only 2/8 stationary twins (needed >= 6).
  - Shape: the residual series comes from an ONLINE-trained substrate whose error shrinks over the stream. The learning
    curve itself is a variance change point, so BIC segmentation "discovers" a regime in stationary worlds.
  - Most false detections sit at .8-.996 of the stream: a small trailing segment.
- **P3 SURVIVES:** twins |mean dAC(SD_cp) - mean dAC(SD_all)| = .011 <= .05. The false detections were nearly
  harmless: they pull the weight toward 0, which forgoes small gains such as F2 tt 023 (+.11 -> 0).

Reading:
- A discovered recency signal suffices to neutralize obsolete history. Discarding was not necessary, and the
  selection signal can be found rather than handed in.
- But this detector is not a REGIME detector. It conflates the substrate's learning curve with world change. Its
  harmlessness on stationary twins comes from the asymmetric cost of the weight grid, not from correct detection.
- NEXT (design): detect on residuals of a FIXED end-of-stream model, i.e. refit S once, then segment its residuals
  over time. That removes the learning-curve artefact. Precommit that twins then show no change in >= 6/8.

Side finding: the frozen LM01 CP selective arm emits transient float-overflow warnings in training on F3 cp L2 dev seed
9_800_001 (ensorain/wtp/organism.py grad_and_pred np.prod). Its final predictions are finite (max |p| 4.3). Recorded as
LM01 ERRATA E-3.

### v3 CORRECTION (2026-09-29T15:12Z, before any new run): the stated P2 mechanism was wrong

- v3 attributed the false detections to the substrate's LEARNING CURVE. But v3's residuals are r = y - S_final(A),
  computed with the FINAL model, not with online predictions, so there is no learning curve in them.
- Revised hypothesis: RETENTION RECENCY. The bounded SELECTIVE substrate (cap cells/4, with eviction) retains mostly
  recent records, so S_final fits recent records better than old ones. That is a variance change in time order even in
  a stationary world.
- This is a hypothesis, tested below (v4). The v3 'NEXT' line (refit a fixed end-of-stream model) is withdrawn: v3
  already used one.

## v4: order-agnostic residuals (pkgf_cp2.py)

- The change point is detected on r_shuf = y - S_shuf(A), where S_shuf is the same substrate trained on a RANDOM
  PERMUTATION of the stream: same records, no temporal order, so no retention recency.
- The weight choice is unchanged: holdout = the detected final regime; g is fitted on the earlier records, as in v3.
- Same fresh worlds (9_800_020-023).

### Precommitment (written BEFORE running pkgf_cp2.py)

- Q1: F2 stationary twins (8 fresh): no change detected in >= 6/8. If this fails, retention recency is NOT the (only)
  mechanism.
- Q2: F3 (8 fresh): a change detected in >= 7/8 AND mean dAC(SD_cp2 vs S) >= -0.10.

### v4 result (precommit commit f11553f85; results/pkgf_cp2.json; 16 s)

- **Q1 SURVIVES:** stationary twins show no change in 7/8 (v3: 2/8). The retention-recency hypothesis for v3's false
  detections is supported.
- **Q2 REFUTED:** a change is detected in only 4/8 F3 worlds (cp 020, 021, 023; tt 023), and the mean
  dAC(SD_cp2) = -0.61. In undetected worlds the full harm returns (-0.74 to -1.77).
  - Shape: the order-agnostic model averages both regimes, so the regime structure largely disappears from its
    residual mean and variance.

Reading (revises v3):
- v3's success on F3 and its false detections on stationary twins had ONE cause: the substrate's retention recency.
  v3 "discovered" recency in every stream. That happened to be right in switch worlds and nearly free in stationary
  ones.
- So what neutralized obsolete history in v2 and v3 was a RECENCY PRIOR, not regime DISCOVERY.
- A residual-segmentation detector without that prior (v4) has little power on these F3 worlds at L2.
- For PKG-F:
  - The claim "the selection signal can be discovered" is NOT supported by v3 + v4.
  - The supported claim is narrower: a recency-weighted selection signal is sufficient to neutralize obsolete stored
    history, and costs little when there is no change.
  - A powered regime detector remains unbuilt. Candidates: a detector on per-cell residual SIGN agreement across
    time; or BOCPD on the prediction of a model refit per window.
  - Do not describe v3 as "discovered recency" anywhere downstream.

## v5: MODEL-FREE regime detector, no recency prior (pkgf_cp3.py)

- Statistic: disagreement of successive same-cell records STRADDLING a candidate split, minus the non-straddling
  disagreement.
- Null: within-cell time permutation (200); a split is accepted iff p < .01; it recurses on the later part.
- Worlds: seeds 9_800_020-023 plus FRESH 9_800_030-033 (16 F3 worlds + 16 F2 stationary twins).

### Precommitment (written BEFORE running pkgf_cp3.py)

- R1: F3: a change is detected in >= 14/16.
- R2: F2 twins: no change detected in >= 13/16.
- R3: F3 mean dAC(SD_cp3 vs S) >= -0.10.
- If same-cell pairs are too sparse in a world, the detector cannot fire. That is reported per world (the 'pairs'
  column) and counted as a miss, not excluded.

### v5 result (precommit commit 370922f19; results/pkgf_cp3.json; 58 s)

- **R1 SURVIVES:** a change is detected in 16/16 F3 worlds, the regime start at .667-.673 of the stream in every
  world.
- **R2 SURVIVES:** no change is detected in 16/16 stationary twins.
- **R3 SURVIVES:** F3 mean dAC(SD_cp3 vs S) = 0.000. The all-history holdout gives -1.26 (range -0.74 to -2.21).
  Twins: dAC(SD_cp3) = dAC(SD_all) = +.004, so discovery costs nothing without a change.

Reading:
- With a MODEL-FREE statistic (same-cell disagreement across a split, with a within-cell time-permutation null), the
  selection signal IS discovered. The harm of stored obsolete history vanishes, with no recency prior and no
  handed-in window.
- This restores, on firmer ground, the claim v3 wrongly appeared to support:
  - obsolete distinctions can stay stored and be ignored, IF the system can locate the regime boundary;
  - here it can, from the stored records themselves.

Scope (a reason for caution, not a footnote):
- Every F3 L2 world switches once, sharply, at ~2/3 of the stream. The regime start is constant across seeds.
- Every world has ~4,700 same-cell successive pairs, dense repeats.
- This is the easy case for the detector. Untested:
  - multiple or gradual switches;
  - sparse repeats (L3, larger cell spaces);
  - F5-style nuisance drifts;
  - decaying-reliability worlds (N5).
- Whether PKG-F would pass on those is open. A precommitted sparse-repeat test (L3) is the natural next check.

## v5b: detector power vs repeat density (pkgf_cp3_sparse.py)

- L3 is NOT sparser: a world property checked on spare seed 9_800_090 before this precommitment, with no detector run.
  L3 has ~7,450 same-cell pairs vs ~4,700 at L2. So sparseness is induced instead: L2 streams thinned in time order to
  a fraction f of records, f in {.25, .10, .05}.
- Worlds: F3 and F2 twins (cp, tt), FRESH seeds 9_800_040-043. That is 8 F3 + 8 twin worlds per f.

### Precommitment (written BEFORE running pkgf_cp3_sparse.py)

- S1: f = .25: F3 detected in >= 7/8.
- S2: f = .10: F3 detected in <= 6/8 (power loss begins).
- S3: f = .05: F3 detected in <= 2/8 (pairs fall near the 30-pair minimum).
- S4: at every f, twins falsely detected in <= 1/8 (the permutation null holds its size under thinning).

### v5b result (precommit commit d17be0163; results/pkgf_cp3_sparse.json; 10 s)

| f | same-cell pairs | F3 detected | twins false | F3 dAC(SD_all), i.e. the harm undetected | F3 dAC(SD_cp3) |
|---|---|---|---|---|---|
| .25 | ~570 | 8/8 | 0/8 | -0.02 .. -0.54 | 0.00 (one -0.04) |
| .10 | ~110 | 0/8 | 0/8 | 0.00 .. -0.05 | same as SD_all |
| .05 | ~30 | 0/8 | 2/8 | 0.00 .. -0.07 | same as SD_all |

- S1 SURVIVES.
- S2 SURVIVES. Power collapses sharply between ~570 and ~110 pairs.
- S3 SURVIVES.
- S4 REFUTED at f = .05 only: 2/8 false detections, cp and tt of the SAME seed 9_800_042.
  - These two share the thinned record sequence and are not independent.
  - At ~31 pairs, right at the 30-pair minimum, the grid-max statistic is coarse. The p < .01 threshold is not
    reliable at this density.
  - Size holds (0/8) at f = .25 and .10.

Exploratory (NOT precommitted), the more important pattern:
- The HARM of stored obsolete history shrinks with repeat density in lockstep with detector power. At f <= .10 the
  undetected all-history holdout costs ~0.
- Both are driven by same-cell repeats. The obsolete residuals hurt the readout only where the smoother finds exact
  or near cells from the old regime, and those same repeats are what make the regime detectable.
- If this holds generally, then in these worlds "the regime is detectable" and "stored obsolete history is harmful"
  co-occur, and the detector fails mainly where it is not needed.
- It must be tested against a world design where harm and repeats are decoupled (e.g. a smoother over neighbours
  rather than exact cells) before it is claimed.
