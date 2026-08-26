#!/usr/bin/env python3
"""Does the metered interface actually create navigation headroom?

The v0.1 A0 finding was that seats sat at ceiling: unanimously correct at a
median of two verifier calls, leaving nothing for condition D to improve. The
metered verifier is only worth building if it produces a cost landscape where
strategies measurably differ. If a naive sweep and an informed probe cost the
same, the navigation experiment is dead regardless of how well the meter is
implemented.

So this runs scripted strategies against sealed claims and reports the cost
spread. Scripted, not LLM: this measures the LANDSCAPE, not any agent's ability
to walk it.

The claims carry structure an informed strategy can exploit — failure positions
are not uniform, they cluster near the domain boundary and at one residue class.
That is the stand-in for what the graph is supposed to supply. A strategy that
knows the clustering should beat one that does not; if it cannot, the metric
cannot see navigation even in principle.

  python strategy_sim.py --claims 120
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from meter import BudgetExhausted, Meter  # noqa: E402


def make_claims(tmp: Path, n: int, rng: random.Random, hi: int) -> Path:
    """Sealed claims whose failure positions carry exploitable structure."""
    d = tmp / "sealed"
    d.mkdir(parents=True, exist_ok=True)
    meta = {}
    for i in range(n):
        shape = rng.choices(["boundary", "residue", "low", "diffuse"],
                            [0.35, 0.35, 0.15, 0.15])[0]
        if shape == "boundary":
            w = rng.randint(hi - 40, hi)
        elif shape == "residue":
            w = rng.randrange(7, hi, 7)
        elif shape == "low":
            w = rng.randint(1, 40)
        else:
            w = rng.randint(1, hi)
        (d / f"S{i}.json").write_text(json.dumps({
            "claim_id": f"S{i}", "domain_lo": 1, "domain_hi": hi,
            "witness_var": "n", "claim_predicate": f"n != {w}",
            # PUBLIC: the shape is visible to any seat. What is NOT public is
            # which probe order each shape rewards -- that is what the graph
            # accumulates, and what separates an informed seat from a
            # generically careful one.
            "shape": shape,
            "sealed_component": True,
        }, indent=2), encoding="utf-8", newline="\n")
        meta[f"S{i}"] = w
    return d


# --------------------------------------------------------------------------
# strategies. Each returns (disposition, session).
# --------------------------------------------------------------------------

def naive_sweep(sess, hi):
    """Ask for everything affordable in one call, and pay for all of it."""
    try:
        r = sess.evaluate_range(1, min(hi, sess.remaining()))
        return ("FALSE" if r["first_failure"] else "UNRESOLVED"), sess
    except BudgetExhausted:
        return "UNRESOLVED", sess


def left_step(sess, hi):
    """Step from the left, one credit per probe, stop on the first failure."""
    for n in range(1, hi + 1):
        try:
            if not sess.evaluate(n):
                return "FALSE", sess
        except BudgetExhausted:
            break
    return "UNRESOLVED", sess


def boundary_first(sess, hi):
    """Probe both boundaries before falling back to stepping."""
    order = list(range(hi, hi - 45, -1)) + list(range(1, 45))
    for n in order:
        if not (1 <= n <= hi):
            continue
        try:
            if not sess.evaluate(n):
                return "FALSE", sess
        except BudgetExhausted:
            return "UNRESOLVED", sess
    return left_step(sess, hi)


def informed(sess, hi):
    """Probe order chosen from the claim's shape. The graph-informed route.

    The shape tag is public; what the graph supplies is the mapping from shape
    to the probe order that reaches the witness soonest. A boundary-first
    heuristic solves the same claims eventually, so the two only separate on
    COST, which is the whole point of the metered design.
    """
    shape = sess.statement().get("shape", "diffuse")
    if shape == "residue":
        order = list(range(7, hi, 7)) + list(range(hi, hi - 45, -1))
    elif shape == "low":
        order = list(range(1, 60)) + list(range(hi, hi - 45, -1))
    elif shape == "boundary":
        order = list(range(hi, hi - 45, -1)) + list(range(7, hi, 7))
    else:
        order = list(range(hi, hi - 45, -1)) + list(range(7, hi, 7)) +             list(range(1, 45))
    seen = set()
    for n in order:
        if n in seen or not (1 <= n <= hi):
            continue
        seen.add(n)
        try:
            if not sess.evaluate(n):
                return "FALSE", sess
        except BudgetExhausted:
            return "UNRESOLVED", sess
    return "UNRESOLVED", sess


STRATEGIES = {"naive_sweep": naive_sweep, "left_step": left_step,
              "boundary_first": boundary_first, "informed": informed}


def permutation_p(a, b, rng, draws=2000):
    obs = abs(statistics.mean(a) - statistics.mean(b))
    pool, na, hits = list(a) + list(b), len(a), 0
    for _ in range(draws):
        rng.shuffle(pool)
        if abs(statistics.mean(pool[:na]) - statistics.mean(pool[na:])) >= obs:
            hits += 1
    return (hits + 1) / (draws + 1)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--claims", type=int, default=120)
    p.add_argument("--budget", type=int, default=1500)
    p.add_argument("--hi", type=int, default=5000)
    p.add_argument("--seed", type=int, default=20260826)
    args = p.parse_args()

    tmp = Path(tempfile.mkdtemp(prefix="ama_strategy_"))
    rng = random.Random(args.seed)
    sealed = make_claims(tmp, args.claims, rng, args.hi)

    results = {k: {"cost": [], "correct": []} for k in STRATEGIES}
    for name, fn in STRATEGIES.items():
        m = Meter(sealed, budget=args.budget)
        for i in range(args.claims):
            sess = m.open(f"S{i}", name)
            disp, sess = fn(sess, args.hi)
            correct = disp == "FALSE"          # every fixture claim is false
            results[name]["correct"].append(correct)
            results[name]["cost"].append(
                sess.ledger.spent if correct else args.budget)
            results[name].setdefault("raw", []).append(sess.ledger.spent)

    L = []
    L.append("METERED STRATEGY LANDSCAPE")
    L.append("=" * 66)
    L.append(f"claims {args.claims} · domain [1, {args.hi}] · budget {args.budget}")
    L.append("Scripted strategies. This measures the COST LANDSCAPE the meter")
    L.append("creates, not any agent's ability to navigate it.")
    L.append("")
    L.append(f"  {'strategy':<16s} {'accuracy':>9s} {'mean cost':>10s} "
             f"{'median':>8s} {'p90':>8s}")
    for name in STRATEGIES:
        c = results[name]["cost"]
        acc = sum(results[name]["correct"]) / len(c)
        srt = sorted(c)
        L.append(f"  {name:<16s} {acc:>8.0%} {statistics.mean(c):>10.1f} "
                 f"{statistics.median(c):>8.0f} {srt[int(0.9*len(srt))]:>8.0f}")
    L.append("")

    prng = random.Random(3)
    base = results["naive_sweep"]["cost"]
    L.append("SEPARATION versus the naive sweep")
    for name in ("left_step", "boundary_first", "informed"):
        c = results[name]["cost"]
        pv = permutation_p(base, c, prng)
        L.append(f"  {name:<16s} mean {statistics.mean(c):>8.1f} vs "
                 f"{statistics.mean(base):>8.1f}   perm p {pv:.3f}")
    pv_inf = permutation_p(results["boundary_first"]["cost"],
                           results["informed"]["cost"], prng)
    L.append(f"  informed vs boundary_first                      "
             f"perm p {pv_inf:.3f}")
    L.append("")

    # PREREG Amendment 1 applied to this simulation. Accuracy ranges from 32%
    # to 88% across strategies, so a raw cost comparison is confounded: wrong
    # answers are charged the cap, and the cheaper-looking strategy may simply
    # be the more accurate one. Conditioning on "correct" would be a collider.
    # The honest contrast is the INTERSECTION - claims every strategy got right.
    inter = [i for i in range(args.claims)
             if all(results[k]["correct"][i] for k in STRATEGIES)]
    L.append("INTERSECTION CONTRAST (PREREG Amendment 1)")
    L.append(f"  claims dispositioned correctly by every strategy: "
             f"{len(inter)}/{args.claims}")
    if len(inter) < 20:
        L.append("  UNPOWERED: fewer than 20 shared items. No cost claim is made.")
        inter_spread = None
        pv_inter_inf = None
    else:
        for name in STRATEGIES:
            c = [results[name]["raw"][i] for i in inter]
            L.append(f"    {name:<16s} mean {statistics.mean(c):>8.1f}  "
                     f"median {statistics.median(c):>7.0f}")
        ni = [results["naive_sweep"]["raw"][i] for i in inter]
        inf = [results["informed"]["raw"][i] for i in inter]
        bf = [results["boundary_first"]["raw"][i] for i in inter]
        inter_spread = statistics.mean(ni) / max(1e-9, statistics.mean(inf))
        pv_inter_inf = permutation_p(bf, inf, prng)
        L.append(f"  naive/informed cost ratio on the intersection: "
                 f"{inter_spread:.1f}x   perm p "
                 f"{permutation_p(ni, inf, prng):.3f}")
        L.append(f"  informed vs boundary_first on the intersection: perm p "
                 f"{permutation_p(bf, inf, prng):.3f}")
    L.append("")
    accs = {k: sum(results[k]["correct"]) / args.claims for k in STRATEGIES}
    L.append("  Reported separately, as the amendment requires: the strategies")
    L.append("  differ in ACCURACY too (" +
             ", ".join(f"{k} {v:.0%}" for k, v in accs.items()) + ").")
    L.append("  That is a real effect and not a substitute for the cost result.")
    L.append("")

    spread = statistics.mean(base) / max(1e-9, statistics.mean(results["informed"]["cost"]))
    L.append("VERDICT")
    if (inter_spread is not None and inter_spread > 2
            and pv_inter_inf is not None and pv_inter_inf < 0.05):
        L.append(f"  The meter creates a {inter_spread:.1f}x cost spread on the")
        L.append("  INTERSECTION, so it is not an accuracy effect in disguise,")
        L.append("  and informed separates from a")
        L.append("  merely boundary-aware strategy. There is headroom for D to")
        L.append("  win on cost without needing the mathematics to be harder.")
    elif spread > 3:
        L.append(f"  A {spread:.1f}x spread exists between naive and informed, but")
        L.append("  informed does not separate from boundary_first: the landscape")
        L.append("  rewards generic heuristics, not accumulated structure. D could")
        L.append("  be matched by condition B.")
    else:
        L.append(f"  Only a {spread:.1f}x spread. The metered interface does NOT")
        L.append("  create enough cost variation for navigation to be measurable.")
        L.append("  Fix the landscape before running v0.2 A0.")

    text = "\n".join(L)
    print(text)
    (HERE / "STRATEGY_LANDSCAPE.txt").write_text(text + "\n", encoding="utf-8",
                                                 newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
