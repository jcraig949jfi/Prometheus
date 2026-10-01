# W2-S plan (frozen before any scoring run; 2026-10-01 ~01:55Z)

Pipeline: W2-L w2l_common (hp_common.evaluate semantics, eager CPU, 2 threads), re-implemented in
w2s_common.py so the per-trial matrix is returned. Pairs = mirror pairs; CI = assays.pair_ci (99%).

## Task 1: FLIP_CHANGE on the record
- Population: all 82 C1 FLIP evolve champions (row genome, row physics/env, held seeds
  H_int(search_seed, HELD_NS), M=64 = 32 pairs) and all 12 C1 FLIP transfer rows (extra.genome, seeds
  H_int(search_seed, 0x7F7F), M=64). C1b rows and c1_posthoc contain no FLIP cells (checked: C1b = HOLD/MAJ/
  RELAY cells; posthoc = 2 HOLD) -> none to score.
- Pipeline check: my overall accuracy must equal the recorded held acc for every row (bit-for-bit target).
- FLIP_CHANGE = accuracy on scored trials with x_k != x_{k-1} (pooled within a mirror pair), pair CI;
  FLIP_CHANGE PASS iff lo99 > .55. Also same-cue accuracy and the (m, same/changed) decomposition.
- COPY-CLASS flag for a row: overall acc > .5 by more than noise (overall lo99 > .50) AND changed-cue CI
  contains .5 (or changed <= .55). Weak flag ("copy-leaning"): overall > .52 and same - changed > .05.
- Controls at their rows (32 pairs): P-FLIP at 6f82f9c7, 996716ac, 64d33b89 (positives; must PASS);
  RELAY_LATCH and relay_flood at 6f82f9c7 (negatives; must FAIL with changed ~.5). Also RELAY_LATCH at
  996716ac and 64d33b89 if cheap.

## Task 2: physics removal on the 41 UNDECIDED rows (W2-L refresh plant; state_dim>=2, prog_len>=22 OVR)
Dials (neutralised value): D = decay_shift->0; L = loss->0; C = cap->0 and collision->none;
U = update_mode->sync, update_period->1; J = lat_jitter->0. A dial already at its neutral value is a no-op
and is not run.
- Seeds: the row's held seeds; screen = first 32 worlds (16 pairs); confirm = 64 worlds (32 pairs).
- Competent = 32-pair lo99 > .55 (C1 SIGNAL bar). Screen pass (triggers confirmation) = 16-pair lo99 > .52.
- Order (compute economy, declared): (1) ALL active dials removed together (screen). (2) Single-dial
  removals for every row whose ALL screen passes. (3) Monotonicity spot check: single removals on 4 rows
  whose ALL screen fails (if any single rescues there, the shortcut is invalid and I run singles on all).
  (4) Rows with ALL pass but no single pass: all pairs of active dials (screen), then confirm.
  (5) Rows whose ALL fails: also try ALL + noise->0 + dup->0 + economy off (extended lossless, beyond brief)
  to see if anything in the physics at all lets the plant work.
- Classification:
  * binding dial X: single removal of X is competent (several -> list all).
  * D (decay) as the only binding dial -> PLANT-DESIGN (E-W13: decay kills write-on-change plants by design).
  * non-D binding dial (L, C, U, J) -> P-candidate attributable to that dial (physics), labelled
    "P-dial(X)" -- it is P only relative to THIS plant; P proper needs a plant-independent argument.
  * combination only -> "joint(X+Y)" / "joint(all)"; with D in the combination -> PLANT-DESIGN-or-P.
  * ALL fails -> PLANT-INADEQUATE (neither P nor R established).
- Revised FLIP placement: counts of P / R-candidate / PLANT-DESIGN / UNDECIDED over 82 rows, keeping W2-L's
  24 P, 3 PLANT-SOLVED, 14 R-CAND and re-placing the 41.
Compute cap 0.6 core-hours (2160 CPU-s process time); ledger in out/compute_ledger.json.

## Addendum A1 (after Task-1 record run and the Task-2 ALL screen; before any further Task-2 run)
- Task-2 ALL (5 brief dials removed) screen: 12/41 pass (16-pair lo99 > .52); 29 fail. All 12 rows with
  c_op = 1 (economy e_income 4 / c_op 1 / c_mem 1 / c_emit 4) are among the 29 fails; no pass has c_op = 1.
  Engine step 5: emission needs E >= c_emit*copies and every awake tick spends c_op * (#non-NOP lines), so a
  22-line plant spends ~22/tick against income 4. Economy is therefore a candidate binding dial outside the
  brief's five. Extra dials (labelled EXTENDED, beyond brief): E = economy off (e_income=c_emit=c_op=c_mem=0);
  N = noise->0 and dup->0. 'C' is active only when cap > 0 (collision is inert at cap 0; ALL runs that set an
  inert collision are unaffected).
- Step A: ALLX = ALL + E + N screen on the 29 ALL-fails.
- Step B: single-dial screens (active dials among D,L,C,U,J,E,N) on every row whose ALL or ALLX screen passed.
- Step C: confirm every single-dial screen pass at 32 pairs (competent = lo99 > .55); if a row has no single
  pass, screen pairs of active dials and confirm.
- Step D (monotonicity spot check): singles on 4 ALLX-fail rows.
- Classification adds: binding E only -> "P-econ" (any plant with more than ~3 non-NOP lines cannot sustain
  emission; argued analytically, see report), N only -> P-noise.
- Task 1 addendum: 4 recorded champions pass FLIP_CHANGE (lo99 > .55) at overall ~.5 with same-cue accuracy
  far below .5 (anti-copy). A balanced-accuracy statistic B = (same + changed)/2 with pair CI and the answer-
  source decomposition (ans = x_k, y_{k-1}, -y_{k-1}) are computed for the controls, those 4 rows, 2 teacher-
  copy transfer rows and 996716ac.

## Addendum A2 (after ALLX + singles screens; before confirmations, LOO, R-CAND check)
- Observation: single D, C, E removals reproduce W2-L's refresh M32 baseline bit-for-bit at many rows (inert
  dials for this plant); D is inert for the refresh plant by construction (sign renormalised each awake tick).
- Observation: several partial repairs give overall > .6 with changed-cue accuracy ~.3-.45 (plant degrades to
  teacher-hold/copy behaviour). Competence is therefore tightened, before any confirmation run, to:
  32-pair overall lo99 > .55 AND FLIP_CHANGE lo99 > .55 (a P-FLIP-type plant answers y_{k-1} on same-cue
  trials, so the anti-copy cheat cannot inflate its FLIP_CHANGE). Overall-only passes are "COPY-ONLY".
  Screen pass = 16-pair overall lo99 > .52 AND changed point estimate > .55.
- Step C': single E on the 9 ALLX-rescued rows that contain E; confirm passes at 32 pairs.
- Step C'': rows whose ALL screen passed but with no competent single: leave-one-out from ALL (ALL minus X for
  each active X), screen; the necessary set = dials whose omission breaks it; confirm the necessary set at 32.
- Step E: FLIP_CHANGE (16 pairs) for W2-L's 14 R-CAND readings (refresh plant; thin at bfa85a55).
- Monotonicity spot check (Step D) dropped for compute; stated as unresolved.
