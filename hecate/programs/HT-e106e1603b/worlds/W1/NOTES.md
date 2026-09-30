# HT-e106e1603b / W1 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v2.md (sha256 2021ed66...185e).
Bound by roles/Hecate/prereg/2026-09-30_probe_round2/PREREG.md and round 1.
Spec: program.json experiments[W1] (mechanism M9, lenses L1, L5, L6).

## Spec field -> code

| spec field | code |
|---|---|
| LxL planar lattice, errors on edges, vertex parity checks | core.py `build_lattice`: L*L vertices (checks), edges right/down between neighbours plus one boundary edge per border side (corner = 2), 2L^2+2L edges. `err[e]` edge error bits, `dfx[v]` defect bits |
| drive: flip one uniformly random edge | core.py `run_decoder`: uniform over all 2L^2+2L edges (boundary edges included); drive flip is NOT counted in the avalanche |
| active: 3x3 neighbourhood holds >= theta defects | `cnt[v]` = defects in clipped 3x3 window, maintained incrementally; active iff cnt >= theta |
| annihilate adjacent pair / move a defect toward nearest boundary, random tie-breaks | `relax`: pick a uniformly random active vertex; if any nearest-neighbour defect pair lies inside its 3x3 window, flip the connecting edge of a uniformly random such pair; otherwise pick a uniformly random defect in the window and flip its edge in the direction of that defect's nearest boundary (ties random). A border defect stepping outward flips a boundary edge and is removed |
| relax until no active vertex | loop until active set empty |
| avalanche size (edge flips) | number of relaxation edge flips after one drive flip |
| s95 | 95th percentile of NON-EMPTY avalanche sizes (size >= 1) per (arm, L, seed) |
| theta=3 conserving rule (TREATMENT) | `run_decoder(theta=3, eps=0)` -- phase 2 only |
| eager control theta=1 | `run_decoder(theta=1, eps=0)` -- phase 2 only |
| null twin: + bulk deletion with prob eps per active step | `run_decoder(theta=3, eps>0)`: after the normal action of an active step, with prob eps delete one uniformly random defect remaining in that vertex's window (no edge flip, not counted as avalanche size; counted as a parity violation) |
| eps calibration by bisection, mean avalanche size within 5% | `calibrate_eps` per L (see A2) |
| positive control: BTW at L=16,32,64 through the same analysis | core.py `run_btw`: z>=4 topples, open boundary, random single-grain drive; size = topplings; analysed by the same `analysis.py` |
| CHEAT | null-twin avalanche size stream with success injected: s -> s*(L/16)^2 before analysis |
| bulk parity-violation count (L5) | deletions counted in-kernel AND audited at run end as #vertices where dfx != syndrome(err) |
| logical failure count (boundary-to-boundary chain) per 1000 injections | every 100 measured injections, union-find over error edges + 4 virtual side nodes; failure iff left-right or top-bottom connected; reported as positive checkpoints per 1000 injections (= count*100/1000 scaled, see A6) |
| size L in {16,32,64}, 2000 burn-in + 20000 measured | as spec |
| seeds | 5 seeds per arm (prompt minimum overrides spec's 4): seed = 1000*arm_code + 10*s + Lindex, s in 0..4 |
| success: cons ratio >= 4 AND twin ratio <= 2, bootstrap 90% intervals not overlapping | analysis.py `ratio_stats`; evaluate.py |
| failure: cons < 2 OR twin ratio inside cons 90% CI OR PC fails (void) | evaluate.py |

## Ambiguities and chosen readings

A1. "either annihilates ... or moves": annihilation has priority when an
    adjacent defect pair exists in the active vertex's window; otherwise a
    move. "Its defects" = defects in the active vertex's 3x3 window (a
    vertex holds at most one defect).
A2. eps calibration: eps = 0 matches trivially (twin == conserving rule),
    which would make the twin degenerate. Reading: the twin uses the
    LARGEST eps in (0,1] whose mean non-empty avalanche size is within 5%
    of the conserving rule's (bisection in log10 eps on [-6, 0], 14 steps,
    edge of the 5% band on whichever side the mean moves), i.e. the
    strongest parity breaking the spec's match permits. Calibration runs:
    2 seeds (distinct from measurement seeds), 2000 burn-in + 10000
    measured, per L. This requires the eps=0 (conserving) mean as the
    calibration TARGET; it is the only treatment quantity computed in the
    pilot, it is a spec-mandated calibration target (not a tuning), and
    no treatment s95 or ratio is computed before the pilot passes. The
    match is re-checked on the full measurement runs and reported.
A3. Ratio statistic: R = mean_seeds s95(64) / mean_seeds s95(16);
    90% interval = percentile bootstrap over seeds (5 seeds, resampled
    jointly across L since each seed index is a paired run set), 4000
    resamples, fixed rng seed 12345.
A4. Arm-level "meets success" (pilot and CONFOUNDED test): point R >= 4.
    Positive control meets success iff R_btw >= 4 (spec: "must give
    >= 4"). Null twin meets success iff R_twin >= 4. Cheat detected iff
    R_cheat >= 4.
A5. Full success (SIGNAL): R_cons >= 4 AND R_twin <= 2 AND
    cons CI and twin CI disjoint AND PC and cheat detected AND twin does
    not meet success. Failure criterion clauses are also evaluated and
    reported. Class precedence: INSTRUMENT_FAIL > CONFOUNDED > SIGNAL >
    NULL.
A6. Logical failure: checked every 100 measured injections (200
    checkpoints per run); reported as positive checkpoints per 1000
    injections = count / 20000 * 1000.
A7. L6 (residue-cluster geometry): the largest error-cluster fraction is
    recorded at the final checkpoint only; no criterion uses it.
A8. BTW avalanche size = number of topplings (the spec's "edge flips" has
    no sandpile analogue); same s95 / ratio code path.

## Parameters (from the spec only)

theta = 3 (conserving, twin), 1 (eager). L in {16,32,64}. burn-in 2000,
measured 20000 injections. Thresholds 4 and 2, 90% intervals, 5% match.
No parameter will change after a treatment statistic exists.

## Budget

<= 10 CPU core-minutes total, single process, measured by
time.process_time() and recorded per script in *_cpu.json.

## Pilot log

(attempts appended below)

### Attempt 1 (2026-09-29)
pilot.py 1 -> PILOT.json: positive R_btw = 14.20 (CI 14.03-14.41) >= 4;
cheat R = 16.0 detected; null twin R = 1.0 (s95 = 1 at every L), not
meeting success -> pilot_pass = true. No repair used. CPU 1.33 s.
Calibrated eps (largest in band): L16 0.339, L32 0.318, L64 0.309.
Disclosure: the calibration target (conserving-rule mean non-empty
avalanche size, eps=0, calibration seeds) was ~1.16 at all three L; it
was visible before phase 2. No parameter or threshold was changed
because of it (none are free: all come from the spec / A1-A8).
Phase 2 reuses calibration.json eps values unchanged (no recalibration).

## Phase 2 (run once, no changes after)
world.py -> rows.jsonl; evaluate.py -> OUTCOME.json: NULL.
R_cons = 1.00 [1.00,1.00] (s95 = 2 at every L, max ~10), R_twin = 1.00,
R_eager = 2.45 [2.40,2.55], R_btw = 14.20, R_cheat = 16.0.
Conserving rule: 0 parity violations, 0 audit mismatches (L5 holds).
Post-run observations (not used by the evaluator): logical-failure
checkpoints saturate at ~10/1000 (= every checkpoint spanning) in all
decoder arms, so that observable is uninformative at this drive; the
twin's mean on measurement seeds sits at 0.948-0.950 of the conserving
mean (edge of the 5% band, as A2 intends; L16 marginally outside);
the eager control's growth (max = L) is the boundary-walk effect.
Total CPU ~0.04 core-minutes.
