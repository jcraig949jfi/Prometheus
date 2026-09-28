# PREREG -- regate_v01: A8-repaired accumulation battery, known-answer re-gate

Currency: 2026-09-28. Fresh research worker (did not write the battery or
the cold-start). Written BEFORE any world in this directory was simulated.
Never edited after the first run; amendments go to AMENDMENTS_v01.md.
Pure ASCII. Campaign: expedition/CAMPAIGN_EXP1.md Phase 0.
Measurement: expedition/accumulation/ACCUMULATION_v0.md with v0.1 A1-A8.

Frozen and inherited unchanged from ../PREREG.md + ../AMENDMENTS.md:
world parameters, 300-generation planted burn-in, world seeds 1000..1019
(n = 20 per arm), per-world salted probe seeds (A1/A6: world_salt), every
original statistic (D0, D1, D2, Dp, Dr, Di, D_episode, I, Dx, J, window,
D_AA, D_fw), delta = 0.05, PASS/EQUIV, bootstrap 2000 resamples seed 12345.
Code: battery_v01.py / world_v01.py are COPIES of ../battery.py /
../world.py with additions only; the originals are not edited.

## 1. The repair (A8), new statistics

H_hist (DIFFERENT-HISTORY twin; ACCUMULATION s1 (h)). From the snapshot
  30 generations before S*, rerun to S* (i) under a DIFFERENT physics
  stream (different environment + noise event history; rng_phys reseeded
  salt+70000+k) and (ii) under the SAME physics stream with different
  organism coins (rng_bio reseeded salt+80000+k), k = 0..3. Statistic:
  mismatch rate vs the actual S* record over cells written in the last 20
  generations, (i) minus (ii). Same producers, same genomes, same world;
  only the earlier event stream differs. NOT a no-write twin. (This is the
  cold-start's history_twin(), unchanged.) If no cell was written in the
  last 20 generations, H_hist = None for that world (counts as not PASS
  for that world only via its absence; if all worlds None -> not PASS).
D_episode (consumer; unchanged original statistic): S1(own, intact) -
  S1(own, own nest record from 50 generations earlier).
E0 (episode test at R0's own readout, the declared decoder): the D0
  decoder protocol (20 snapshots, producers removed, T = 5 physics-only
  generations, LOO majority map record-tuple -> producing s) applied to
  pairs (record from snapshot t-50 after the same 5-gen persistence, s
  producing at t). E0 = acc(intact) - acc(episode pairs). Rationale: R0
  is decoder-defined (A3); a consumer statistic is meaningless for arms
  with no reader (N_a), so "D_episode" at R0 is taken at the R0 readout.
  SENSITIVITY (reported, not decisional): R0 with the literal consumer
  D_episode clause.
Per-cell H_hist (cell 0, cell 1) is reported as a diagnostic.

## 2. Repaired decision rules (primary; cumulative ladder as ../PREREG s4)

  R0 := PASS(D0) AND PASS(H_hist) AND PASS(E0)
  R1 := R0 AND PASS(D1)
  R2 := R1 AND PASS(D2) AND no receiver wrote the record (assertion)
  R3 := R2 AND [original: PASS(Dp), PASS(Dr), Dp >= .5 D1, Dr >= .5 D1,
        EQUIV(Di) or n/a] AND PASS(H_hist) AND PASS(D_episode) AND
        mean D_episode >= 0.5 mean D1
  R4, R5 unchanged. Convention qualifier unchanged (2-way, for gate
  comparability) plus the A2 3-way label reported.
  Also reported: every test individually and the A3 reading (each rung's
  own tests, no lower-rung prerequisite).

## 3. Known-answer set (n = 20 worlds per arm, seeds 1000..1019)

Original arms (unchanged construction): P, P4, N_a, N_b, C, P_sigma.
Cold-start arms: T (nest tag; colony-biased physics: redraw -> site g with
  prob .7), P_cb (P in the same physics, positive control).
NEW cheat 1, CAL ("calendar tag"; aimed to defeat D_episode, not H_hist):
  physics 'calendar': epoch(t) = floor((t + 25) / 50); on a redraw colony
  g's patch goes to site (g + epoch) mod 4 with prob .7, else uniformly to
  one of the other 3 (same three physics draws per colony per generation).
  Plant: a clonal genome SCHEDULE: in epoch e colony g's writers write the
  constant symbol (g + e) mod 4 into cell 0 regardless of site/outcome;
  readers decode cell 0 as P; explore .2. The record content is a function
  of the clock only: every history drives it to the same value (s1 (h)
  fails by construction). The phase offset 25 puts S* (gen 300) mid-epoch
  and the 50-gen episode record in the previous epoch, so the old record
  names the WRONG favoured site: consumer D_episode should PASS (defeated).
  Note: the task's example ("period equal to the episode lag") would make
  the old record identical to the current one and be CAUGHT by D_episode;
  a tag that DIFFERS at lag 50 is what defeats it.
P_cal: P plant in the calendar physics (positive control).
NEW cheat 2, DECOY ("decoy cell"; aimed at H_hist): colony-biased physics
  (as T). Half the colony (caste A) writes the constant nest tag g into
  cell 0 every generation; the other half (caste B) writes the site it
  found into cell 1 (fail -> noop), a genuine history-specific record.
  Readers decode cell 0 only (as P). The benefit comes from the static tag;
  the history-specific content sits in a cell nobody reads. H_hist is
  computed over all recently written cells, so it should PASS (defeated);
  the consumer D_episode should catch it (old cell 0 = same tag).

## 4. Gate (THE decision; every criterion must hold)

  G0 identity: battery_v01/world_v01 reproduce every per-world value of the
     6 original arms in ../known_answer.json (tolerance 1e-12, keys
     present in the fixture), and the ORIGINAL decide() on them gives the
     fixture's highest rung and tests dict for every arm.
  G1 P: R3 awarded under the repaired rules; R4, R5 not; qualifier INSTALLED.
  G2 N_a: nothing above R0.     G3 N_b: nothing above R0.
  G4 C: R3 not awarded, R2 awarded, R3_perm or R3_rand fails (content).
  G5 A/A CI contains 0 in every arm (all 11 arms).
  G6 P_cb: R3.   G7 P_cal: R3.
  G8 T: R0 not awarded AND R3 not awarded AND PASS(H_hist) false.
  G9 CAL: R3 not awarded AND PASS(H_hist) false.
  G10 DECOY: R2 awarded AND R3 not awarded (the cheat is tested AT R3,
     not stopped by a lower rung).
  Secondary (reported, not blocking): P4 R4.
  "Original verdicts preserved" := every original arm's highest rung under
  the repaired rules equals its fixture highest rung (predicted YES).

## 5. Predictions (stated now; reported, not gate)

  P, P_cb, P_cal: H_hist > .3, D_episode > .3, E0 > .3 (all PASS).
  N_a: H_hist, E0 PASS -> R0 (preserved). N_b: H_hist ~ 0 (fails).
  C: H_hist PASS, D_episode ~ 0; R2 (preserved). P_sigma: R0 (preserved).
  P4: R3 (preserved), R4 undetermined (secondary).
  T: H_hist ~ .003, D_episode ~ 0, E0 ~ 0 -> highest None; A3 reading: R1,
     R2 pass, R3 fails.
  CAL: D1, D2, Dp, Dr PASS; D_episode PASS (~D1: defeated); H_hist < .05
     (catches); E0 ~ 0 (the LOO decoder learns old-tag -> current site, so
     the decoder-level episode test also catches it; the consumer-level
     test does not). Highest None; A3 reading R3 fails ONLY on H_hist.
  DECOY: H_hist PASS (~.2-.4, carried by cell 1; defeated), D0 and E0
     PASS, D1, D2, Dp, Dr PASS, D_episode ~ 0 (catches). Highest R2.
  Literal-consumer sensitivity: N_a and P_sigma would lose R0 (a defect
     of the literal reading, not of the arms).

## 6. Unplanted (EXPLORATORY; only if the gate PASSES)

Configuration of ../unplanted.json (3000 generations, seeds 1000..1019,
arms as ../run_battery.py). Order (budget): U_sigma seed 1016 first, then
the rest of U_sigma, then U_id, then U_frozen. Identity check: original
per-world values vs ../unplanted.json. Reported: the repaired rungs per
arm, H_hist, E0, D_episode, and seed 1016's per-world values. R5 uses the
arm's own no-record ceiling (U_norec not re-run). Hard stop: 40 minutes of
cumulative run wall from the gate start; unfinished parts are reported as
NOT RUN. Words "language", "culture", "knowledge" are not used.

## 7. Budget

1 process, stdlib, <= 45 min wall total. No reduction of n or generations
in the gate is permitted.
