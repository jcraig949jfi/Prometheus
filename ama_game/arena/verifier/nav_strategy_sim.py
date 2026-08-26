#!/usr/bin/env python3
"""Run real strategies against the navigation claims, through the real meter.

`navgen.py` writes an `achievable_floor` into every sealed record. That is an
assertion until something actually reaches it. This runs a scripted seat that
does the mathematics — sample four residues, solve the two-by-two system for the
recurrence coefficients modulo M, reconstruct the sequence locally, and confirm
with one evaluate — and checks the meter's ledger against the claimed floor.

If the fit route cannot be walked, the route menu is fiction and the headroom
number is worthless.

  python nav_strategy_sim.py
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARENA = HERE.parent
sys.path.insert(0, str(HERE))

from meter import BudgetExhausted, Meter  # noqa: E402


def enumerate_left(sess, N):
    for n in range(1, N + 1):
        try:
            if not sess.evaluate(n):
                return "FALSE", n
        except BudgetExhausted:
            return "UNRESOLVED", None
    return "TRUE", None


def boundary_first(sess, N):
    order = list(range(N, N - 40, -1)) + list(range(1, 41))
    for n in order:
        if not (1 <= n <= N):
            continue
        try:
            if not sess.evaluate(n):
                return "FALSE", n
        except BudgetExhausted:
            return "UNRESOLVED", None
    return enumerate_left(sess, N)


def fit_recurrence(sess, N, R, M):
    """Recover the sealed recurrence from four samples, then compute for free.

    f(k) = p*f(k-1) + q*f(k-2) modulo M. Sampling f at 1..4 gives two equations
    in (p, q); M is prime so the system is solvable whenever its determinant is
    non-zero. After that the whole sequence is reconstructible locally at no
    cost to the meter, and a single evaluate confirms the witness.
    """
    try:
        f = {k: sess.sample(k) for k in (1, 2, 3, 4)}
    except BudgetExhausted:
        return "UNRESOLVED", None

    det = (f[2] * f[2] - f[1] * f[3]) % M
    if det == 0:
        return enumerate_left(sess, N)           # degenerate: fall back
    inv = pow(det, M - 2, M)
    p = ((f[3] * f[2] - f[1] * f[4]) * inv) % M
    q = ((f[2] * f[4] - f[3] * f[3]) * inv) % M

    prev, cur = f[1], f[2]
    if prev == R:
        witness = 1
    elif cur == R:
        witness = 2
    else:
        witness = None
        for n in range(3, N + 1):
            prev, cur = cur, (p * cur + q * prev) % M
            if cur == R:
                witness = n
                break
    if witness is None:
        return "TRUE", None
    try:
        holds = sess.evaluate(witness)           # one confirming call
    except BudgetExhausted:
        return "UNRESOLVED", None
    return ("FALSE", witness) if not holds else ("UNRESOLVED", None)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default=str(ARENA / "heldout" / "NAV_PILOT"))
    ap.add_argument("--budget", type=int, default=650)
    args = ap.parse_args()

    root = Path(args.set)
    sealed_dir = root / "sealed"
    ids = sorted(p.stem for p in sealed_dir.glob("*.json"))
    seals = {i: json.loads((sealed_dir / f"{i}.json").read_text(encoding="utf-8"))
             for i in ids}

    rows = {k: [] for k in ("enumerate", "boundary", "fit")}
    correct = {k: [] for k in rows}
    floor_hits, floor_misses = 0, []

    for cid in ids:
        s = seals[cid]
        N, R, M = s["params"]["N"], s["params"]["R"], s["params"]["M"]
        oracle = s["oracle_disposition"]

        for name, fn in (("enumerate", lambda se: enumerate_left(se, N)),
                         ("boundary", lambda se: boundary_first(se, N)),
                         ("fit", lambda se: fit_recurrence(se, N, R, M))):
            m = Meter(sealed_dir, budget=args.budget)
            sess = m.open(cid, name)
            disp, w = fn(sess)
            ok = disp == oracle
            correct[name].append(ok)
            rows[name].append(sess.ledger.spent if ok else args.budget)
            if name == "fit":
                if ok and sess.ledger.spent <= s["achievable_floor"]:
                    floor_hits += 1
                elif ok:
                    floor_misses.append((cid, sess.ledger.spent,
                                         s["achievable_floor"]))

    L = []
    L.append("NAVIGATION CLAIMS — REAL STRATEGIES THROUGH THE REAL METER")
    L.append("=" * 66)
    L.append(f"claims {len(ids)} · budget {args.budget}")
    L.append("")
    L.append(f"  {'route':<12s} {'accuracy':>9s} {'mean cost':>10s} {'median':>8s}")
    for name in rows:
        acc = sum(correct[name]) / len(ids)
        L.append(f"  {name:<12s} {acc:>8.0%} {statistics.mean(rows[name]):>10.1f} "
                 f"{statistics.median(rows[name]):>8.0f}")
    L.append("")

    inter = [i for i in range(len(ids))
             if all(correct[k][i] for k in rows)]
    L.append("INTERSECTION CONTRAST (PREREG Amendment 1)")
    L.append(f"  claims every route dispositioned correctly: {len(inter)}/{len(ids)}")
    if len(inter) < 20:
        L.append("  UNPOWERED: fewer than 20 shared items; no cost claim made.")
    else:
        for name in rows:
            c = [rows[name][i] for i in inter]
            L.append(f"    {name:<12s} mean {statistics.mean(c):>8.1f}  "
                     f"median {statistics.median(c):>7.0f}")
        en = [rows["enumerate"][i] for i in inter]
        ft = [rows["fit"][i] for i in inter]
        L.append(f"  enumerate / fit on the intersection: "
                 f"{statistics.mean(en) / max(1e-9, statistics.mean(ft)):.1f}x")
    L.append("")

    L.append("IS THE CLAIMED FLOOR REACHABLE?")
    L.append(f"  fit reached the sealed achievable_floor on {floor_hits}/"
             f"{sum(correct['fit'])} claims it solved")
    for cid, spent, floor in floor_misses[:5]:
        L.append(f"    {cid}: spent {spent}, floor {floor}")
    L.append("")
    ok_floor = floor_hits == sum(correct["fit"]) and sum(correct["fit"]) > 0
    if ok_floor:
        L.append("VERDICT: the route menu is real. The cheap route is walkable")
        L.append("and costs what the sealed record says it costs, so the")
        L.append("headroom figure is a measurement rather than an assertion.")
    else:
        L.append("VERDICT: the claimed floor is not reachable as written. The")
        L.append("route menu is fiction until this is fixed.")

    text = "\n".join(L)
    print(text)
    (HERE / "NAV_STRATEGY.txt").write_text(text + "\n", encoding="utf-8",
                                           newline="\n")
    return 0 if ok_floor else 1


if __name__ == "__main__":
    raise SystemExit(main())
