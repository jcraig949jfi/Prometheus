"""Decision-n derivation against the MANIFEST-LEVEL estimand (prereg §3.1 ruling #3).

Charon's ruling set decision-n = 600/rung, derived from WILSON widths. My §3.1 ruling #3 adopted
manifest-level intervals as the correct estimand — the manifest is frozen and the arms run on
exactly these items, so the only live noise is solver stochasticity — with the explicit
consequence that his n does NOT carry over and must be recomputed. This is that computation.

IN-BAND requires the whole interval inside [0.35, 0.60]:

    z * sqrt(p(1-p)/n)  <=  d(p),      d(p) = min(p - 0.35, 0.60 - p)
    =>  n  >=  z^2 * p(1-p) / d(p)^2

z is Bonferroni-adjusted over the k rungs actually re-measured: z = Phi^-1(1 - 0.05/(2k)).

The DISPERSION term (Harmonia B ruling 2) has to be decidable too — a rung that passes on the
mean and fails on movable share is not leveled — so the same requirement is applied to
movable >= 0.30:

    n  >=  z^2 * m(1-m) / (m - 0.30)^2

and the binding requirement is the max of the two. Cost is 2n calls, because the dispersion term
needs both cold reps.
"""
from statistics import NormalDist
import sys

BAND = (0.35, 0.60)
MOVABLE_FLOOR = 0.30


def z_for(k: int, alpha: float = 0.05) -> float:
    return NormalDist().inv_cdf(1 - alpha / (2 * k))


def n_for_band(p: float, k: int) -> float:
    d = min(p - BAND[0], BAND[1] - p)
    if d <= 0:
        return float("inf")
    return z_for(k) ** 2 * p * (1 - p) / d ** 2


def n_for_dispersion(m: float, k: int) -> float:
    d = m - MOVABLE_FLOOR
    if d <= 0:
        return float("inf")
    return z_for(k) ** 2 * m * (1 - m) / d ** 2


if __name__ == "__main__":
    ks = (1, 4)
    print("DECISION-N, manifest-level estimand\n")
    print("band term:  n >= z^2 p(1-p) / min(p-0.35, 0.60-p)^2")
    print(f"{'true p':>8} | " + " | ".join(f"k={k} (z={z_for(k):.3f})" for k in ks))
    for p in (0.40, 0.45, 0.475, 0.50, 0.52, 0.55, 0.57, 0.58):
        cells = " | ".join(f"{n_for_band(p,k):12.0f}" for k in ks)
        print(f"{p:8.3f} | {cells}")
    print("\ndispersion term:  n >= z^2 m(1-m) / (m-0.30)^2")
    print(f"{'movable':>8} | " + " | ".join(f"k={k}" for k in ks))
    for m in (0.35, 0.40, 0.45, 0.50, 0.60):
        cells = " | ".join(f"{n_for_dispersion(m,k):12.0f}" for k in ks)
        print(f"{m:8.3f} | {cells}")
    if len(sys.argv) > 2:
        p, m = float(sys.argv[1]), float(sys.argv[2])
        k = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        nb, nd = n_for_band(p, k), n_for_dispersion(m, k)
        print(f"\nAPPLIED  p={p} movable={m} k={k}: band {nb:.0f} · dispersion {nd:.0f} "
              f"-> decision-n = {max(nb, nd):.0f}  ({2*max(nb,nd):.0f} calls with 2 reps)")
