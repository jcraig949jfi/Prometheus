"""THE OPPOSITE CASE (mission section 15, 19E).

Prometheus must not overcorrect from

    "base-measure rarity tests after selection are often vacuous"

to

    "retrospective candidates can never be scientifically tested."

Those are different statements. This module demonstrates the difference.

SELECTION-FREEDOM THEOREM (informal). Let D be the sigma-field of ALL
historical data, including human choices and adaptive mining. Let the
candidate C be D-measurable -- chosen by ANY rule, however hindsight-laden.
Let U be fresh randomness independent of D (the post-commit beacon). Let the
test reject iff phi(C,U)=1 and suppose the level bound holds POINTWISE IN c:

    for EVERY fixed c,   P_U(phi(c,U)=1) <= alpha.

Then P(reject) = E_D[ P_U(phi(C,U)=1 | C) ] <= alpha, for ANY selection rule.

The crux is POINTWISE. A bound that holds only ON AVERAGE over c ~ nu (a base
measure) does not survive selection that targets c. Base-measure rarity tests
have exactly that weaker form -- their null is a statement about C's
PROVENANCE ("C is a draw from nu"), which selection falsifies for every
selected C. Randomized intervention tests have the stronger form, because
their null is a statement about the RESPONSE TO EXPERIMENTER RANDOMNESS.

Demonstrated here:
  E1  a candidate selected by ABSURDLY extreme historical selection
      (max of 200,000 draws on the very statistic later reported) still
      yields an exactly-level randomized causal test
  E2  level is flat across selection intensity: 1, 10^2, 10^3, 10^5 -- the
      randomized test does not care how the specimen was found
  E3  THE BOUNDARY WITHIN CLASS E: if the INTERVENTION or the OBSERVABLE is
      chosen after seeing the candidate's response, level breaks again. Class
      E is free with respect to SPECIMEN selection, not with respect to
      TEST selection.
"""
from __future__ import annotations

import hashlib
import math


def rng_stream(*tag):
    seed = int.from_bytes(hashlib.sha256(
        "|".join(str(t) for t in tag).encode()).digest()[:8], "big")
    state = seed | 1

    def nxt():
        nonlocal state
        state = (state * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        return (state >> 11) / float(1 << 53)
    return nxt


def normal(r):
    return math.sqrt(-2.0 * math.log(max(r(), 1e-12))) * \
        math.cos(2 * math.pi * r())


def randomization_test(r, specimen_bias, n_clones=16, n_perm=200,
                       effect=0.0):
    """A fresh randomized intervention on independent CLONES of the specimen.

    * `specimen_bias` is an arbitrary specimen-specific constant -- it may be
      enormous, and it is EXACTLY what extreme historical selection produces.
      It is a MAIN EFFECT: it shifts treated and control clones equally.
    * treatment assignment is drawn AFTER the specimen is fixed (the beacon).
    * the null is "the intervention has no effect ON THIS SPECIMEN".
    * inference is by permuting the assignment labels -- the same randomness
      the experiment used.

    Returns True if the test rejects at level 1/(n_perm+1)*ceil -- here we use
    the exact 5% rank cut of the permutation distribution.
    """
    assign = [1 if r() < 0.5 else 0 for _ in range(n_clones)]
    if all(a == 0 for a in assign) or all(a == 1 for a in assign):
        return False
    y = [specimen_bias + effect * assign[i] + normal(r)
         for i in range(n_clones)]

    def stat(a):
        t = [y[i] for i in range(n_clones) if a[i] == 1]
        c = [y[i] for i in range(n_clones) if a[i] == 0]
        if not t or not c:
            return -1e18
        return sum(t) / len(t) - sum(c) / len(c)

    obs = stat(assign)
    ge = 1
    for _ in range(n_perm):
        perm = [1 if r() < 0.5 else 0 for _ in range(n_clones)]
        if stat(perm) >= obs:
            ge += 1
    return (ge / (n_perm + 1)) <= 0.05


def E1_E2_selection_intensity(trials=1500):
    """Level of the randomized causal test as a function of how extreme the
    historical selection of the specimen was."""
    out = {}
    for n_select in (1, 100, 1000, 200000):
        r = rng_stream("E", n_select)
        rej = 0
        for t in range(trials):
            # HISTORICAL SELECTION: keep the max of n_select draws, on the
            # very statistic the analyst finds interesting. This is the most
            # hindsight-laden selection imaginable.
            specimen_bias = max(normal(r) for _ in range(min(n_select, 2000)))
            if n_select > 2000:                       # emulate deeper search
                specimen_bias += math.log(n_select / 2000.0)
            # FRESH randomized experiment on clones, null true (effect = 0)
            if randomization_test(r, specimen_bias, effect=0.0):
                rej += 1
        out[n_select] = rej / trials
    return out


def E3_test_selection_breaks_it(n_obs=20, trials=2000):
    """THE BOUNDARY WITHIN CLASS E. Same randomized experiment, but the
    analyst measures n_obs observables and reports the most significant.
    Specimen selection was free; TEST selection is not."""
    r = rng_stream("E3")
    best_rej = 0
    beacon_rej = 0
    for t in range(trials):
        specimen_bias = max(normal(r) for _ in range(500))
        ps = []
        for j in range(n_obs):
            ps.append(0 if randomization_test(r, specimen_bias, effect=0.0)
                      else 1)
        if any(p == 0 for p in ps):        # report the observable that "worked"
            best_rej += 1
        j = int(r() * n_obs)               # beacon picks the observable
        if ps[j] == 0:
            beacon_rej += 1
    return {"n_observables": n_obs,
            "E3_report_best_observable": best_rej / trials,
            "E3_beacon_selected_observable": beacon_rej / trials,
            "target": 0.05}


def E4_power_check(trials=800):
    """The test is not vacuous: with a real effect it rejects."""
    out = {}
    for effect in (0.0, 0.5, 1.0, 2.0):
        r = rng_stream("E4", effect)
        rej = sum(randomization_test(r, max(normal(r) for _ in range(500)),
                                     effect=effect) for _ in range(trials))
        out[effect] = rej / trials
    return out


def main():
    print("=" * 78)
    print("CANDIDATE-CONDITIONAL RANDOMIZATION -- THE OPPOSITE CASE")
    print("=" * 78)

    print("\n[E1/E2] LEVEL vs HISTORICAL SELECTION INTENSITY (null is true)")
    print("  The specimen is chosen as the MAXIMUM of n draws, on the very")
    print("  statistic the analyst cares about. Then a FRESH randomized")
    print("  intervention is run on clones, with assignment drawn after the")
    print("  specimen is fixed.")
    lv = E1_E2_selection_intensity()
    for n, rate in sorted(lv.items()):
        print("      selection depth n = %-8d -> rejection %.4f" % (n, rate))
    print("  LEVEL IS FLAT IN SELECTION INTENSITY. Arbitrarily extreme")
    print("  historical selection does NOT inflate the randomized causal")
    print("  test, because the null concerns the response to experimenter")
    print("  randomness, not the specimen's provenance.")

    print("\n[E4] AND THE TEST IS NOT VACUOUS (power against real effects)")
    pw = E4_power_check()
    for e, rate in sorted(pw.items()):
        print("      true effect %.1f -> rejection %.4f" % (e, rate))

    print("\n[E3] THE BOUNDARY WITHIN CLASS E -- TEST selection is NOT free")
    e3 = E3_test_selection_breaks_it()
    print("  analyst reports best of %d observables : %.4f"
          % (e3["n_observables"], e3["E3_report_best_observable"]))
    print("  beacon selects the observable         : %.4f  (target %.2f)"
          % (e3["E3_beacon_selected_observable"], e3["target"]))
    print("  CLASS E IS FREE WITH RESPECT TO SPECIMEN SELECTION,")
    print("  NOT WITH RESPECT TO TEST SELECTION. The specimen may be chosen")
    print("  by unlimited hindsight; the intervention, the observable, the")
    print("  tail and the stopping rule may not.")
    print("=" * 78)
    return {"level_vs_selection": lv, "power": pw, "test_selection": e3}


if __name__ == "__main__":
    main()
