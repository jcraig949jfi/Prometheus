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

## v6: PARTIAL switches (reviewer Q1 of PKGF_CRYPT_REVIEW; pkgf_partial.py)

- Worlds are built from the frozen LM01 helpers: the F3-like episode structure (3 equal episodes, so the final regime
  starts at 2/3). At each switch only a fraction rho of cells is redrawn.
- rho in {1, .5, .1, 0}; rho = 0 is stationary. Generators cp and tt; FRESH seeds 9_800_050-053 (8 worlds per rho).
- Design note: built without waiting for review, under MWO-0004 R1 (a small reversible dev probe).

### Precommitment (written BEFORE running pkgf_partial.py)

- W1: rho = .5: v5 detects the final switch (cp_frac in [.60, .75]) in >= 7/8.
- W2: rho = .1: detection in <= 4/8. The straddling-pair statistic is diluted by the ~90% unchanged cells.
- W3: rho = .1: the undetected harm is smaller than at rho = 1: mean dAC(SD_all) at rho = .1 > mean at rho = 1 AND
  > -0.5.
- W4: rho = 0: false detections <= 1/8.

### v6 result (precommit commit a434fb870; results/pkgf_partial.json; 63 s)

| rho | final switch detected (cp_frac .60-.75) | mean dAC(SD_all) | mean dAC(SD_cp3) |
|---|---|---|---|
| 1.0 | 8/8 | -1.10 | 0.00 |
| 0.5 | 8/8 | +0.05 | +0.12 |
| 0.1 | 5/8 | +0.30 | +0.29 |
| 0.0 | 0/8 false | +0.44 | +0.44 |

- W1 SURVIVES (8/8).
- W2 REFUTED: 5/8 detected at rho = .1, more sensitive than predicted. The detector is not as easily diluted as
  claimed.
- W3 SURVIVES: +0.30 > -1.10, and > -0.5.
- W4 SURVIVES: 0/8 false.

Answer to reviewer Q1: v5 is NOT an oracle-in-disguise that needs every cell to change. It finds switches that change
half the cells in 8/8 worlds and a tenth of them in 5/8, with 0/8 false alarms.

Exploratory (NOT precommitted), the more important shape:
- The SIGN of restoring the stored residual channel depends on how much of the world changed:
  - full switch: -1.10 (it hurts unless the regime is found);
  - half: about +0.05 .. +0.12;
  - a tenth: +0.30;
  - stationary: +0.44.
  With this substrate (the F3-selected SELECTIVE arm at cap cells/4, a bounded learner), stored exact records carry
  information the substrate cannot retain. Retention PAYS, except for the fraction of it that is obsolete.
- At rho = .1, restricting the holdout to the detected regime is slightly WORSE than using all history in 3/8 worlds
  (e.g. +0.156 -> +0.125). Most old records are still valid, so the conservative rule discounts good records.
- This is the first dev evidence in PKG-F that "keep and ignore" beats "discard" by a margin that shrinks smoothly with
  the obsolete fraction.
- It needs the obvious control before any claim: the SAME rho sweep with the F2-selected substrate, where the stationary
  gain was ~0 in v2 to v5. Does the gain come from a mismatched (weak) substrate?

## v6 control: substrate mismatch? (pkgf_partial_ctrl.py; pkgf_partial.one gained a sub_family argument, default unchanged)

- The same partial-switch worlds and seeds as v6, but the substrate is the F2_latent-selected SELECTIVE arm.
- Question: does v6's stationary retention gain (+0.44) come from a mismatched, weak F3-selected substrate?

### Precommitment (written BEFORE running pkgf_partial_ctrl.py)

- M1: rho = 0, mean dAC(SD_all) < +0.10. The gain vanishes with a matched substrate, i.e. v6's gain was mismatch.
- M2: rho = 1, mean dAC(SD_all) < -0.5. The obsolete-history harm persists with either substrate.
- If M1 fails, v6's "retention pays" survives a matched substrate and becomes a candidate PKG-F reading.

### v6 control result (precommit commit e7958ce18; results/pkgf_partial_ctrl.json; 60 s)

- Substrate labels: cp: F2-selected = F3-selected = S-cp, so the cp half of the control is IDENTICAL to v6 and tests
  nothing. tt: F2-selected S-lowrank vs F3-selected S-tt, a genuine control.
- **M1 REFUTED:** rho = 0 mean dAC(SD_all) = +0.48 (tt with the matched substrate: +0.17 .. +0.92). The stationary gain
  is not a substrate mismatch.
- **M2 SURVIVES:** rho = 1 mean dAC(SD_all) = -0.63 < -0.5.

The actual mechanism (found while diagnosing M1; a world property, checked directly):
- The F3-style headline test ("never_seen") is never-seen in the FINAL episode only.
- 87-89% of those test cells WERE recorded in earlier episodes. Measured on v6 worlds 9_800_050/051 and the frozen F3
  worlds with the same seeds.
- In a stationary world those earlier records are exact and current, so the gain is EXACT RECALL. Under a full switch
  they are stale at the very cells being tested, so the harm is STALE RECALL.
- The v2-v5 F2 twins used F2's test, which is unseen over the WHOLE stream. That is why their gain was ~0.

Consequences:
- v6's exploratory "keep-and-ignore beats discard, shrinking with the obsolete fraction" is WITHDRAWN as a
  generalization reading. It is a statement about reuse of exact old records at the tested cells.
- All PKG-F F3 readings (v2-v6) concern re-querying cells seen only in earlier regimes. That is a legitimate and
  intended LM01 F3 question (can stale exact records be ignored?), but it is not generalization to unseen cells.
- The PKG-F design must report two headline splits separately:
  - (a) cells seen only in earlier regimes: the stale-recall test;
  - (b) cells unseen in the whole stream: the generalization test.
  Every claim must name its split. Added as the next precommitted run.
- Note for LM01 (read-only; no frozen change): its F3 headline test has the same composition, and its interpretation
  should say so.

## v7: the two-split rerun of v6 (pkgf_split.py)

- STALE split: cells unseen in the final episode but recorded earlier.
- GEN split: cells unseen in the whole stream.
- Same worlds, seeds and substrate as v6. Test cells are drawn with a new seed (seed + 99); each split is capped at
  512 cells.

### Precommitment (written BEFORE running pkgf_split.py)

- T1: GEN, rho = 0: mean dAC(SD_all) in [-0.10, +0.10], i.e. no generalization gain from stored residuals in a
  stationary world.
- T2: GEN, rho = 1: mean dAC(SD_all) > -0.30. The obsolete-history harm is mostly a STALE-recall phenomenon.
- T3: STALE, rho = 1 mean dAC(SD_all) < -0.80 AND STALE, rho = 0 mean dAC(SD_all) > +0.30. The STALE split carries
  both v6 effects.

### v7 result (precommit commit 437251e55; results/pkgf_split.json; 64 s)

Mean dAC vs S (8 worlds per cell):

| rho | STALE SD_all | STALE SD_cp3 | GEN SD_all | GEN SD_cp3 |
|---|---|---|---|---|
| 1.0 | -1.153 | 0.000 | -0.137 | 0.000 |
| 0.5 | +0.065 | +0.132 | -0.018 | -0.004 |
| 0.1 | +0.389 | +0.371 | -0.007 | -0.008 |
| 0.0 | +0.856 | +0.856 | -0.005 | -0.005 |

- T1 SURVIVES: GEN, rho = 0, -0.005.
- T2 SURVIVES: GEN, rho = 1, -0.137 > -0.30.
- T3 SURVIVES: STALE, rho = 1, -1.153 and STALE, rho = 0, +0.856.
- Caveat: the GEN split is small, 64-87 cells per world. Few cells are never visited at L2.

Reading (supersedes the v6 exploratory reading):
- Restoring stored exact records does NOTHING for generalization to never-seen cells, at any rho (|dAC| <= .02 for
  rho < 1).
- Under a full switch they cost -0.14 there, through nearest-neighbour smoothing over stale neighbours, and the
  detected-regime holdout removes that cost.
- Everything v2-v6 measured as "harm" or "gain" is STALE RECALL:
  - the value of exact old records at re-queried cells runs smoothly from -1.15 (all obsolete) to +0.86 (all
    current);
  - the regime detector turns the negative end to 0 without losing the positive end (rho = .5: +0.13; rho = 0:
    +0.86).
- PKG-F therefore has one clean dev result: keeping exact records and gating their use by a discovered regime is never
  worse than discarding them on re-queried cells (0 at a full switch, positive otherwise), and neutral for novel cells.
  That is a statement about RECALL, not generalization. It is what the ARC3 question "can irrelevant distinctions
  remain stored but simply be ignored?" asks, answered for recall.

## N5: decaying reliability (pkgf_n5.py; design s9e)

- The field is FIXED. Observation noise SD grows linearly from 1x to 3x NOISE over the stream, so old records are
  more reliable than recent ones.
- 3 episodes; STALE and GEN splits. Holdouts: ALL, REC20, CP3.
- F3-selected substrate. FRESH seeds 9_800_060-063, cp and tt (8 worlds).

### Precommitment (written BEFORE running pkgf_n5.py; the thresholds from design s9e, unchanged)

- N1: the v5 detector FALSELY detects a regime in >= 4/8. Its squared-disagreement statistic is variance-sensitive;
  if it does not fire, that limitation is refuted.
- N2: STALE split, mean dAC(REC20) < mean dAC(ALL). Handed-in recency picks its weight on the noisiest records and
  loses.

### N5 result (precommit commit 1f607d35f; results/pkgf_n5.json; 15 s)

- **N1 SURVIVES:** the v5 detector fires in 8/8 worlds with NO regime change. The detected start is at .88-.95 of the
  stream, i.e. the noisiest tail.
- **N2 SURVIVES:** STALE mean dAC: ALL +0.664 > REC20 +0.645 > CP3 +0.611. GEN: all within +-0.01.

Shape:
- The v5 statistic (squared disagreement across a split) cannot tell GROWING NOISE from a REGIME CHANGE. It reads rising
  variance as a switch.
- Both recency-based holdouts then choose the readout weight on the least reliable records. The weight falls from
  1.0 to 0.5 or 0.25 in 3/8 worlds, so good old records are discounted.
- The cost is small here (-0.05 mean on STALE, up to -0.20 in one world), only because the weight grid is coarse and
  the fitted weights mostly stayed put. It is a failure mode, not a catastrophe.
- Consistent with the PKG-F thread so far: a selection signal keyed to TIME (recency or regime) is right when newer
  means more relevant, and wrong when newer means noisier.

Design consequence (PKG-F s9e, to be precommitted before building):
- A variance-robust detector must separate mean change from spread change.
- Candidate: compare straddling-pair disagreement against a same-time noise reference, e.g. the within-cell spread of
  records close in time on each side. Accept a regime only if straddling disagreement exceeds the LOCAL noise on both
  sides.
- An N5 world is then the required negative control for every PKG-F regime detector, alongside the stationary twins.

## v8: variance-robust detector (pkgf_cp4.py). Detection only; FRESH seeds 9_800_070-073, cp and tt

- Statistic: straddling-pair disagreement minus the mean of the left and right local disagreement, within a window of
  +-20% of the stream.
- Same permutation null, threshold and recursion as v5.

### Precommitment (written BEFORE running pkgf_cp4.py)

- V1: N5 (noise growth, no change): false detections <= 1/8.
- V2: F3 L2: detection with cp_frac in [.60, .75] in >= 7/8.
- V3: F2 L2 twins: false detections <= 1/8.
- V4: partial switch at rho = .5: detection with cp_frac in [.60, .75] in >= 6/8.

### v8 result (precommit commit e8549ccbd; results/pkgf_cp4.json; 30 s)

| world | detected | final switch in [.60, .75] | v5 on the same world type |
|---|---|---|---|
| N5 (noise growth) | 0/8 | - | 8/8 FALSE |
| F3 (full switch) | 8/8 | 8/8 | 16/16 |
| F2 twins | 0/8 | - | 0/16 |
| partial rho = .5 | 4/8 | 1/8 | 8/8 |

- V1 SURVIVES: 0/8 false on N5. The variance confound is fixed.
- V2 SURVIVES: 8/8.
- V3 SURVIVES: 0/8.
- V4 REFUTED: 1/8 at the final switch.
  - Three worlds stop at the FIRST switch (.327). The recursion on the later part then fails to find the second
    switch.
  - Four find nothing.

Shape: a trade-off between robustness and power.
- Referencing each split to its LOCAL left and right noise (a +-20% window) removes the noise-growth false alarms, but
  it uses fewer pairs per test.
- On partial switches (half the cells unchanged, which dilutes the mean shift) it loses the power v5 had. After a
  first split the remaining segment is shorter, which cuts power further.
- No single detector in this series passes all four controls:
  - v5 fails N5;
  - v8 fails partial switches.

Next candidates (design, not run):
- (a) combine both: accept a split only if v5 fires AND the v8 local-noise statistic is positive at that tau (with no
  separate significance test). This keeps v5's power and uses v8 as a veto against pure variance growth.
- (b) per-cell normalization: divide each pair's disagreement by that cell's own pooled within-side spread.
- Either must pass all four world types, precommitted.

## v9: v5 proposes, v8 vetoes at the proposed tau only (pkgf_cp5.py). Detection only; FRESH seeds 9_800_080-083

### Precommitment (written BEFORE running pkgf_cp5.py; the same thresholds as v8)

- Z1: N5: false detections <= 1/8.
- Z2: F3 L2: final switch (cp_frac in [.60, .75]) in >= 7/8.
- Z3: F2 twins: false detections <= 1/8.
- Z4: partial rho = .5: final switch in >= 6/8.

### v9 result (precommit commit 22c472887; results/pkgf_cp5.json; 44 s)

| world | detected | final switch in [.60, .75] | v5 | v8 |
|---|---|---|---|---|
| N5 (noise growth) | 2/8 false | - | 8/8 false | 0/8 |
| F3 | 8/8 | 8/8 | 16/16 | 8/8 |
| F2 twins | 0/8 | - | 0/16 | 0/8 |
| partial rho = .5 | 8/8 | 8/8 | 8/8 | 1/8 |

- **Z1 REFUTED (narrowly):** 2/8 > 1/8. Both false detections are seed 9_800_082, in its cp and tt variants. These
  share the walk and noise draws (the N5 world's walk RNG is keyed on the seed only), so they are not independent:
  effectively 1 of 4 seeds.
- **Z2, Z3, Z4 SURVIVE.**

Reading:
- v9 recovers v5's power on partial switches (8/8, where v8 had 1/8) and keeps v8's robustness, up to the refuted
  margin (2/8 correlated N5 false alarms).
- It is the first detector in this series that is close on all four controls.
- The obvious fix, a stricter veto level (p < .01 instead of .05), is a POST-HOC change. It must be precommitted and
  run on fresh seeds, with independent generator variants (distinct walk seeds) so that the N5 count is not inflated by
  correlated pairs.
- Design note for every future PKG-F world builder: cp and tt variants of the same seed share the walk. Count per seed,
  or de-correlate the walk.
