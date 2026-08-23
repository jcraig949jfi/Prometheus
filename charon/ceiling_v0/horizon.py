"""Is the arena the confound?

Iteration 15 established that substrate accuracy is entirely coverage, and that
coverage is set by how far rewriting drives a query down the length scale
(r = -0.944 across seven arms). The memo only ever holds SHORT canonical forms,
because it is harvested from prefixes of probes capped at length 6. So the whole
result may be an artifact of one arena parameter: the gap between what an arm may
RUN (<=6) and what it is ASKED (8-12).

That is testable. Raise the probe cap and the memo fills with longer forms, so
less shortening is needed to reach it. Prediction if the mechanism is purely
compression-to-horizon:

  * coverage rises for every arm as the cap rises
  * the P3c/P3d gap SHRINKS, because there is less shortening left to do
  * at a cap close to the query length the arms converge

If instead P3d keeps its lead at every cap, it is doing something beyond
compression and the iteration-15 story is incomplete.

Query lengths track the cap (cap+2 .. cap+6) so the task stays "predict sequences
longer than you may run" at every setting, and the held-out set is never runnable.

  python horizon.py
"""
from __future__ import annotations

from typing import Dict, List

from baselines import substrate_arm
from config import ArmConfig
from mechanism import profile
from universe import EvalSet, Universe, UniverseSpec

SEEDS = list(range(1, 13))
ROUNDS = 6
CAPS = [4, 6, 8, 10]
MODES = ["datadriven", "relevance"]


def run() -> None:
    print("=" * 78)
    print("HORIZON — does the substrate result survive a bigger probe cap?")
    print("Query length is always cap+2 .. cap+6, so the task shape is constant.")
    print("=" * 78)
    print(f"\n  {'cap':>4}{'queries':>10}{'arm':>14}{'acc':>8}{'cov':>8}"
          f"{'canon len':>11}{'rules':>8}{'memo':>8}")
    table: Dict[int, Dict[str, Dict]] = {}
    for cap in CAPS:
        lo, hi = cap + 2, cap + 6
        table[cap] = {}
        for mode in MODES:
            rows = []
            for seed in SEEDS:
                spec = UniverseSpec(seed=seed, max_word_len=cap)
                uni = Universe(spec)
                ev = EvalSet(uni, n_queries=40, len_lo=lo, len_hi=hi)
                _, store = substrate_arm(uni, ev, seed, ArmConfig(), ROUNDS, mode)
                rows.append(profile(store, uni, ev))
            mean = lambda f: sum(r[f] for r in rows) / len(rows)
            table[cap][mode] = {f: mean(f) for f in
                                ("acc", "coverage", "mean_canon_len",
                                 "n_rules", "n_memo")}
            m = table[cap][mode]
            print(f"  {cap:>4}{f'{lo}-{hi}':>10}{mode:>14}{m['acc']:>8.3f}"
                  f"{m['coverage']:>8.3f}{m['mean_canon_len']:>11.2f}"
                  f"{m['n_rules']:>8.1f}{m['n_memo']:>8.0f}")

    print(f"\n  P3d advantage over P3c at each cap:")
    print(f"    {'cap':>4}{'acc gap':>10}{'cov gap':>10}{'len gap':>10}")
    for cap in CAPS:
        a = table[cap]["relevance"]
        b = table[cap]["datadriven"]
        print(f"    {cap:>4}{a['acc']-b['acc']:>10.3f}"
              f"{a['coverage']-b['coverage']:>10.3f}"
              f"{b['mean_canon_len']-a['mean_canon_len']:>10.2f}")

    gaps = [table[c]["relevance"]["acc"] - table[c]["datadriven"]["acc"]
            for c in CAPS]
    trend = gaps[-1] - gaps[0]
    print(f"\n  gap at cap {CAPS[0]}: {gaps[0]:+.3f}   "
          f"gap at cap {CAPS[-1]}: {gaps[-1]:+.3f}   change {trend:+.3f}")
    if trend < -0.05:
        print("  -> the advantage SHRINKS as the horizon rises: the result is")
        print("     substantially an artifact of the run/ask length gap.")
    elif trend > 0.05:
        print("  -> the advantage GROWS: compression-to-horizon is not the whole")
        print("     story and iteration 15's explanation is incomplete.")
    else:
        print("  -> the advantage is stable across horizons: it is not simply an")
        print("     artifact of the cap, though the mechanism is still shortening.")


if __name__ == "__main__":
    run()
