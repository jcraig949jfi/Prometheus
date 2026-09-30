# HT-ae38c641b1 / W5 probe (round 3, prompt probe_impl_v3.md sha256 a34a8c61...1685)

Written BEFORE any treatment code was run. Implementer: fresh instance for Hecate.
Frozen inputs read: spec.json, controls.py, ATTAINABILITY.json, DESIGN_NOTES.md (and,
incidentally, revisions.json / a directory listing of _rev0/ in the same world; nothing
from them is used). None of the frozen files is modified; control_rows.jsonl and
ATTAINABILITY.json are not rewritten (controls.main() is NOT called, because it
overwrites them; world.py calls the same controls.run / world / fitness / cheat /
summary functions instead, i.e. the same code path, and writes to probe/rows.jsonl).

## Arms (20 seeds each, seeds 0..19 as in spec)
Controls (re-run through controls.py functions, unchanged):
- POSITIVE_CONTROL      = controls.run(seed, "PC", 0.0)
- POSITIVE_CONTROL_ROT  = controls.run(seed, "PC", 22.5 deg)
- NULL_TWIN             = controls.run(seed, "NULL", 0.0, ref_accept=PC acceptance)
- CHEAT                 = controls.cheat(NULL_TWIN final maps, dom), dom = 0 and 22.5
Treatment:
- V      box-verifier gate, dom = 0
- V_rot  box-verifier gate, dom = 22.5 deg
Treatment-matched null twins (spec: "V for S1, V_rot for S2"):
- NULL_TWIN_V     = controls.run(seed, "NULL", 0.0, ref_accept=V acceptance per generation)
- NULL_TWIN_VROT  = controls.run(seed, "NULL", 0.0, ref_accept=V_rot acceptance)

Treatment GA = a copy of controls.run with the gate replaced: same world(seed) initial
population (concrete-safe, shared with all arms), same mutation stream [seed,11], same
null-coin stream [seed,13] drawn every generation (unused by V, drawn to keep streams
parallel with the control code), fitness = lam_hat - shape_pen (controls.fitness with an
arm name that adds no bonus), acceptance = PROVEN(dom), (mu+lambda) stable-sort
truncation exactly as controls.run. No concrete gate in V/V_rot (spec). Parents are
never re-gated; the initial population is not required to be PROVEN (spec: it is the
shared concrete-safe population).

Verifier(dom), per spec: Q = rot(dom), B_j = Q^T A_j Q, h0 = (0.5, 0.5),
h_{n+1} = max(h0, |B_1| h_n, |B_2| h_n) for n = 0..29 (h_30 after 30 steps),
h* = 1.05 h_30, PROVEN iff |B_j| h* <= h* componentwise for j = 1,2 AND
h*_1^2 + h*_2^2 <= 1. Non-finite values -> not PROVEN (comparisons with NaN are False;
inf fails the disc test).

## Readings chosen (none changes a threshold)
1. Statistics: S1/F1 = mean over seeds of A4(0) in V; S2 = mean A4(22.5) in V_rot;
   F2 = mean A4(0) in V_rot; F3 = mean over seeds of the per-seed mean over generations
   of V's accepted fraction (equal generations per seed, so = mean over seeds x gens).
2. Reproducibility check (first step of evaluate.py): recompute S1/S2 positive and twin
   values and cheat values from the rerun control rows; compare attainable and
   discriminating status per clause, and cheat_detected, with ATTAINABILITY.json. Any
   status difference -> INSTRUMENT_FAIL (reproducibility), stop. Numeric deltas recorded.
3. positive_control_detected = PC meets S1 AND PC_ROT meets S2 (rerun).
   cheat_detected = CHEAT A4 >= 0.40 at both doms (rerun).
   null_twin_meets_success = NULL_TWIN_V meets S1 (A4(0) >= 0.40) OR NULL_TWIN_VROT
   meets S2 (A4(22.5) >= 0.40).
4. Outcome precedence (decided in code):
   a. control status mismatch -> INSTRUMENT_FAIL (reproducibility)
   b. positive or cheat not detected -> INSTRUMENT_FAIL
   c. F3 met -> INSTRUMENT_FAIL (spec: "reading invalid, not a falsification"; NULL
      would be a falsification, so the round-1 class that makes no treatment reading
      is used; sub-reason recorded)
   d. null twin meets success -> CONFOUNDED
   e. S1 and S2 met and neither F1 nor F2 met -> SIGNAL
   f. otherwise -> NULL. If no failure clause fires and a success statistic lies in
      [0.15, 0.40), the spec calls it INCONCLUSIVE; the round-1 class is still NULL
      (treatment fails the success criterion) and the sub-reading
      "INCONCLUSIVE band per spec, not a falsification of M2" is recorded in
      statistics.spec_reading.
5. Diagnostics (not clauses): A8(0), median rho(|A|)/rho(A), median lam_hat, mean w,
   accepted fractions, per arm; also acceptance-match gap of the twins.

## Seeds / budget
Seeds 0..19 (spec). Single-threaded BLAS (OMP/OPENBLAS/MKL_NUM_THREADS=1), CPU time by
time.process_time(). Budget <= 10 core-min. One attempt; a rerun only for a crash/bug,
which would be described in OUTCOME.json "attempts".
