"""Toy demonstrations of the SELECTION BOUNDARY (mission section 14, 19A-D, 19F).

Canonical educational test for future Prometheus seats.

The naive historical test is: take an interesting artifact C, compare it with
fresh random draws, reject if C looks unusual. This module shows exactly when
that is meaningless and exactly what repairs it.

Demonstrations:
  A  max-of-N selection makes a naive base-measure null "discover" constantly
  B  reproducing max-of-N under the null removes the false discovery
  C  two-stage selection (best-of-run, then best-of-runs)
  D  specification selection (pick the observable after seeing the candidate)
  F  INCOMPLETE replay leaves a false-positive channel open -- the most
     important negative result, because a partially-matched null looks correct

Exact computation is used where available; simulation is seeded and reported
with its uncertainty otherwise.
"""
from __future__ import annotations

import hashlib
import math
import statistics


def rng_stream(*tag):
    """Deterministic seeded stream; no wall clock, no OS entropy."""
    seed = int.from_bytes(hashlib.sha256(
        "|".join(str(t) for t in tag).encode()).digest()[:8], "big")
    state = seed | 1

    def nxt():
        nonlocal state
        state = (state * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        return (state >> 11) / float(1 << 53)
    return nxt


def phi(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def normal(u1, u2):
    return math.sqrt(-2.0 * math.log(max(u1, 1e-12))) * math.cos(2 * math.pi * u2)


# ----------------------------------------------------------------- A and B
def demo_A_B(N=100, trials=4000, alpha=0.05):
    """Generator emits pure noise. Selection returns the MAXIMUM of N draws.

    A: naive null compares the winner to ONE fresh draw  -> false discovery
       at a rate governed by max-of-N, not by alpha.
    B: correct null regenerates N draws, takes ITS maximum, and compares
       winner-against-winner -> level restored.

    EXACT reference: under the naive test the rejection probability is
    P(max of N > z_alpha) = 1 - Phi(z_alpha)^N.
    """
    r = rng_stream("AB")
    z_alpha = 1.6448536269514722                      # one-sided 0.05
    naive_rej = 0
    correct_rej = 0
    for t in range(trials):
        winner = max(normal(r(), r()) for _ in range(N))
        # A: naive -- compare winner against the BASE measure
        if winner > z_alpha:
            naive_rej += 1
        # B: correct -- compare winner against the law of the WINNER
        ref = max(normal(r(), r()) for _ in range(N))
        if winner > ref:
            # rank-based: p = P(ref >= winner); reject at alpha only if the
            # winner beats a 1-alpha quantile of the winner distribution
            pass
        refs = [max(normal(r(), r()) for _ in range(N)) for _ in range(19)]
        # exact rank test at level 1/20 = 0.05: reject iff winner is strict max
        if all(winner > x for x in refs):
            correct_rej += 1
    exact_naive = 1.0 - phi(z_alpha) ** N
    return {
        "N": N, "trials": trials, "alpha": alpha,
        "A_naive_rejection_rate": naive_rej / trials,
        "A_exact_prediction": exact_naive,
        "A_inflation_factor": round((naive_rej / trials) / alpha, 1),
        "B_selection_replicating_rate": correct_rej / trials,
        "B_target": 0.05,
    }


# ----------------------------------------------------------------------- C
def demo_C_two_stage(runs=20, per_run=50, trials=2000):
    """Two-stage selection: each run keeps its best of `per_run`; then the
    analyst keeps the best of `runs` runs. Total search = runs*per_run.

    A null that replicates ONLY the inner stage (best-of-per_run) is still
    wrong by the outer factor. This is the 'partially process-matched' trap
    in its simplest form.
    """
    r = rng_stream("C")
    partial_rej = 0
    full_rej = 0
    for t in range(trials):
        champion = max(max(normal(r(), r()) for _ in range(per_run))
                       for _ in range(runs))
        # partial replay: inner stage only
        prefs = [max(normal(r(), r()) for _ in range(per_run))
                 for _ in range(19)]
        if all(champion > x for x in prefs):
            partial_rej += 1
        # full replay: both stages
        frefs = [max(max(normal(r(), r()) for _ in range(per_run))
                     for _ in range(runs)) for _ in range(19)]
        if all(champion > x for x in frefs):
            full_rej += 1
    return {"runs": runs, "per_run": per_run, "trials": trials,
            "C_partial_replay_rate": partial_rej / trials,
            "C_full_replay_rate": full_rej / trials, "target": 0.05}


# ----------------------------------------------------------------------- D
def demo_D_spec_selection(n_specs=20, trials=4000):
    """Specification selection. The candidate is ONE fixed object. The analyst
    computes n_specs independent observables on it and reports the most
    extreme. Each individual observable has an exactly valid rank test.

    This is the menu-selection channel: every menu member is individually
    valid; the CHOICE among them is not."""
    r = rng_stream("D")
    naive_rej = 0
    bonf_rej = 0
    beacon_rej = 0
    for t in range(trials):
        # under H0 each spec's rank p-value is uniform on {1/20,...,20/20}
        ps = [int(r() * 20) + 1 for _ in range(n_specs)]
        pmin = min(ps) / 20.0
        if pmin <= 0.05:                       # analyst reports the best spec
            naive_rej += 1
        if pmin <= 0.05 / n_specs:             # Bonferroni over the menu
            bonf_rej += 1
        j = int(r() * n_specs)                 # BEACON picks the spec
        if ps[j] / 20.0 <= 0.05:
            beacon_rej += 1
    return {"n_specs": n_specs, "trials": trials,
            "D_report_best_spec_rate": naive_rej / trials,
            "D_bonferroni_rate": bonf_rej / trials,
            "D_beacon_selected_rate": beacon_rej / trials,
            "target": 0.05}


# ----------------------------------------------------------------------- F
def demo_F_incomplete_replay(N=100, censor_frac=0.5, trials=3000):
    """THE MOST IMPORTANT NEGATIVE RESULT.

    The historical pipeline (i) draws N candidates, (ii) CENSORS the failures
    -- only runs that cleared a threshold were preserved -- and (iii) returns
    the best survivor.

    A replay that reproduces the max-of-N but NOT the censoring produces a
    null that is systematically too easy, so a false-positive channel stays
    open even though the replay 'matched the process'.
    """
    r = rng_stream("F")
    thresh = 0.0                     # only non-negative draws were preserved
    naive_rej = 0
    uncensored_replay_rej = 0
    full_replay_rej = 0

    def hist_pipeline():
        draws = [normal(r(), r()) for _ in range(N)]
        kept = [d for d in draws if d > thresh]      # censoring
        return max(kept) if kept else None

    def replay_no_censor():
        return max(normal(r(), r()) for _ in range(N))

    def replay_full():
        draws = [normal(r(), r()) for _ in range(N)]
        kept = [d for d in draws if d > thresh]
        return max(kept) if kept else None

    for t in range(trials):
        champ = hist_pipeline()
        if champ is None:
            continue
        if champ > 1.6448536269514722:
            naive_rej += 1
        r1 = [replay_no_censor() for _ in range(19)]
        if all(champ > x for x in r1):
            uncensored_replay_rej += 1
        r2 = [x for x in (replay_full() for _ in range(19)) if x is not None]
        if r2 and all(champ > x for x in r2):
            full_replay_rej += 1
    return {"N": N, "trials": trials,
            "F_naive_rate": naive_rej / trials,
            "F_replay_without_censoring_rate": uncensored_replay_rej / trials,
            "F_full_replay_rate": full_replay_rej / trials,
            "target": 0.05,
            "note": ("censoring here happens to make the UNCENSORED replay "
                     "CONSERVATIVE rather than anti-conservative, because the "
                     "omitted step removed only LOW draws. The direction of "
                     "the error depends on which tail the omitted stage cut. "
                     "See demo_F2 for the anti-conservative direction.")}


def demo_F2_anticonservative(N=100, trials=3000):
    """The dangerous direction: the omitted stage was ADVERSARIAL SELECTION
    that the replay leaves out. Historical pipeline takes the best of N;
    replay takes the best of only n < N because the analyst did not know how
    many candidates were really examined (logs were incomplete)."""
    r = rng_stream("F2")
    rej = {}
    for n_replay in (100, 50, 20, 10, 1):
        cnt = 0
        for t in range(trials):
            champ = max(normal(r(), r()) for _ in range(N))
            refs = [max(normal(r(), r()) for _ in range(n_replay))
                    for _ in range(19)]
            if all(champ > x for x in refs):
                cnt += 1
        rej[n_replay] = cnt / trials
    return {"true_N": N, "trials": trials,
            "F2_rate_by_assumed_replay_N": rej, "target": 0.05}


def main():
    print("=" * 78)
    print("TOY SELECTION-BIAS DEMONSTRATIONS")
    print("=" * 78)

    print("\n[A/B] MAX-OF-N SELECTION vs SELECTION-REPLICATING NULL")
    ab = demo_A_B()
    print("  A naive base-measure test on the winner of N=%d:" % ab["N"])
    print("      rejection rate %.4f   (exact prediction %.4f)"
          % (ab["A_naive_rejection_rate"], ab["A_exact_prediction"]))
    print("      INFLATION vs nominal 0.05: %.1fx" % ab["A_inflation_factor"])
    print("  B selection-replicating null (winner vs winners):")
    print("      rejection rate %.4f   (target %.2f)"
          % (ab["B_selection_replicating_rate"], ab["B_target"]))

    print("\n[C] TWO-STAGE SELECTION -- partial replay is not enough")
    c = demo_C_two_stage()
    print("  historical search = %d runs x %d draws" % (c["runs"], c["per_run"]))
    print("  replay INNER stage only : %.4f" % c["C_partial_replay_rate"])
    print("  replay BOTH stages      : %.4f  (target %.2f)"
          % (c["C_full_replay_rate"], c["target"]))

    print("\n[D] SPECIFICATION SELECTION -- the menu is a selection channel")
    d = demo_D_spec_selection()
    print("  analyst reports best of %d specs : %.4f" %
          (d["n_specs"], d["D_report_best_spec_rate"]))
    print("  Bonferroni over the menu         : %.4f" % d["D_bonferroni_rate"])
    print("  BEACON selects the spec          : %.4f  (target %.2f)"
          % (d["D_beacon_selected_rate"], d["target"]))

    print("\n[F] INCOMPLETE REPLAY -- omitting a stage")
    f = demo_F_incomplete_replay()
    print("  naive                       : %.4f" % f["F_naive_rate"])
    print("  replay WITHOUT censoring    : %.4f" %
          f["F_replay_without_censoring_rate"])
    print("  replay WITH censoring       : %.4f  (target %.2f)"
          % (f["F_full_replay_rate"], f["target"]))
    print("  " + f["note"].replace(". ", ".\n  "))

    print("\n[F2] THE ANTI-CONSERVATIVE DIRECTION -- undercounting the search")
    f2 = demo_F2_anticonservative()
    print("  true search depth N = %d; replay assumes n:" % f2["true_N"])
    for n, rate in sorted(f2["F2_rate_by_assumed_replay_N"].items(),
                          reverse=True):
        flag = "  <-- correct" if n == f2["true_N"] else ""
        print("      n = %-4d -> rejection %.4f%s" % (n, rate, flag))
    print("  UNDERCOUNTING THE HISTORICAL SEARCH IS DIRECTLY")
    print("  ANTI-CONSERVATIVE. If the logs do not say how many artifacts")
    print("  were really examined, the replay CANNOT be trusted.")
    print("=" * 78)
    return {"A_B": ab, "C": c, "D": d, "F": f, "F2": f2}


if __name__ == "__main__":
    main()
