"""Independent bounded replication of AA-018's computational basis.

AA-018 (COLLATZ_2025_26_PROOF_CLAIMS, grade A3) asserts: Collatz remains OPEN,
"verified to 2.36e21 with no general proof".

I cannot reach 2.36e21. What IS replicable is the *structure* of the computational
basis: an independent implementation, written from the stated recurrence rather
than copied from any existing code in this repo, should find no counterexample in
whatever range it can cover, and should reproduce published stopping times on
calibration points.

Honest scope: a clean run over ~1e7 is ~14 orders of magnitude short of the cited
bound. It is therefore NOT evidence for the cited number. It is evidence that (i)
this implementation is sound and (ii) the anchor's claim-shape is replicable in
kind. Calibration-before-discovery: known stopping times are checked FIRST; if
those miss, the run is VACUOUS and nothing else it reports counts.
"""
import sys, time

def total_stopping_time(n):
    """Steps for n to reach 1 under 3x+1. Written from the recurrence."""
    steps = 0
    while n != 1:
        n = (3 * n + 1) if (n & 1) else (n >> 1)
        steps += 1
    return steps

# ---- CALIBRATION FIRST (published total stopping times) -------------------
CALIB = {6: 8, 7: 16, 27: 111, 97: 118, 871: 178, 6171: 261, 77031: 350}
cal_fail = [(n, total_stopping_time(n), e) for n, e in CALIB.items()
            if total_stopping_time(n) != e]
print("CALIBRATION:", "PASS" if not cal_fail else f"FAIL {cal_fail}")
if cal_fail:
    print("VACUOUS: instrument failed calibration; downstream numbers void.")
    sys.exit(1)

# ---- BOUNDED SWEEP -------------------------------------------------------
LIMIT = 10_000_000
t0 = time.time()
counterexamples, max_steps, argmax = [], 0, None
seen_below = [0] * (LIMIT + 1)   # memo: 1 once n proven to reach 1
seen_below[1] = 1
for n in range(2, LIMIT + 1):
    m, steps = n, 0
    while m != 1:
        if m <= LIMIT and seen_below[m]:
            steps += 0  # already known to converge; stop walking
            break
        m = (3 * m + 1) if (m & 1) else (m >> 1)
        steps += 1
        if steps > 5000:
            counterexamples.append(n)
            break
    seen_below[n] = 1
    if steps > max_steps:
        max_steps, argmax = steps, n

el = time.time() - t0
print(f"SWEEP: n in [2, {LIMIT:,}]  elapsed {el:.1f}s")
print(f"  counterexamples (no convergence within 5000 steps): {len(counterexamples)}")
print(f"  max residual steps-to-known: {max_steps} at n={argmax}")
print(f"  orders of magnitude below the cited 2.36e21 bound: "
      f"{21 - len(str(LIMIT)) + 1}")
