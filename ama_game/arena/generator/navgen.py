#!/usr/bin/env python3
"""Navigation-shaped claims: crisp truth, wildly unequal routes to it.

The v0.1 A0 finding was that seats sat at ceiling — unanimously correct at a
median of two verifier calls. External review diagnosed it: the experiment was
measuring truth-determination, and the agents are not struggling with that. What
we want to know is whether accumulated structure helps a seat choose which
falsification operation to spend next.

So harden the search geometry, not the mathematics. Each claim here is about a
sequence the seat can only observe through the metered API:

    Let f be the sequence held by the arena. For every n with 1 <= n <= N,
    f(n) mod M is not R.

f is a second-order linear recurrence with SEALED coefficients. The seat cannot
reimplement it, which is what makes the meter bind. Three routes exist and cost
very different amounts:

  enumerate   test the proposition at 1, 2, 3, ... until it fails.
              Cost = the witness position, which can be in the hundreds.
  boundary    probe near the ends first. Cheap when the witness is there,
              useless otherwise.
  fit         sample f at a handful of points, recognise that it satisfies a
              two-term linear recurrence, solve for the coefficients, then
              compute the whole sequence locally for nothing. Cost ~6.

`fit` is real mathematics — recovering a recurrence from samples — and it is
dramatically cheaper. That is the cost geometry the navigation experiment needs,
and it exists without making the truth harder to certify.

Every item records its full route menu with per-route cost in the sealed record,
so the achievable floor is known and the gap between what a seat spent and what
was available becomes the measurement.

  python navgen.py --count 40 --out ../heldout/NAV_PILOT
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARENA = HERE.parent


def sequence(a0: int, a1: int, p: int, q: int, n_max: int) -> list[int]:
    f = [a0, a1]
    while len(f) <= n_max:
        f.append(p * f[-1] + q * f[-2])
    return f


def build(rng: random.Random, n_max: int, cls: str, budget: int,
          blind: bool = False):
    """One claim of the requested class. Returns (public, sealed) or None.

    Three classes, and deliberately no UNRESOLVED. A genuine order-2 sequence is
    always resolvable from four samples, so an unresolvable-within-budget
    navigation claim cannot be built without lying about the hypotheses. That
    class stays with the opaque-iteration items, where it belongs; here the
    measurement is cost and correctness, which is what Amendment 1 asks for.

      NAV_TRUE        the residue never occurs. Only the structural route can
                      establish it; enumeration runs out of budget.
      NAV_FALSE_NEAR  witness inside the budget. Both routes work, at very
                      different prices.
      NAV_FALSE_FAR   witness beyond the budget. Only the structural route.
    """
    r, s = sorted(rng.sample([2, 3, 4, 5, 6, 7], 2))
    C, D = rng.randint(1, 5), rng.randint(1, 5)
    p, q = r + s, -r * s
    a0, a1 = C + D, C * r + D * s
    # A LARGE prime modulus. The first version used M in [11, 31] and produced
    # no headroom at all: residues of a linear recurrence modulo a small number
    # cycle fast, so any residue that occurs occurs almost immediately, the
    # witness was always tiny, and enumeration beat the structural route. With
    # M >> N the period is long, a chosen residue is essentially unique in
    # range, and the witness lands where it is placed.
    M = rng.choice([1009, 1409, 2003, 2711, 3301, 4001, 5003])

    f = sequence(a0, a1, p, q, n_max)
    residues = [f[n] % M for n in range(n_max + 1)]

    present = set(residues[1:n_max + 1])
    if cls == "NAV_TRUE":
        absent = [x for x in range(M) if x not in present]
        if not absent:
            return None
        R = rng.choice(absent)
        first = None
    else:
        if cls == "NAV_FALSE_NEAR":
            window = [n for n in range(2, max(3, budget // 2))
                      if residues[n] not in residues[1:n]]
        else:
            window = [n for n in range(budget + 30, n_max)
                      if residues[n] not in residues[1:n]]
        if not window:
            return None
        w = rng.choice(window)
        R = residues[w]
        first = next((n for n in range(1, n_max + 1) if residues[n] == R), None)
        if first is None:
            return None
        if cls == "NAV_FALSE_NEAR" and first > budget:
            return None
        if cls == "NAV_FALSE_FAR" and first <= budget:
            return None

    # route costs, computed rather than asserted
    cost_enumerate = first if first is not None else n_max
    boundary_probes = list(range(n_max, n_max - 40, -1)) + list(range(1, 41))
    cost_boundary = next((i + 1 for i, n in enumerate(boundary_probes)
                          if 1 <= n <= n_max and residues[n] == R), None)
    enumerate_within_budget = cost_enumerate <= budget
    # fit: sample four values, solve the 2x2 system for (p, q), one confirming
    # evaluate at the position the local computation predicts
    cost_fit = 5

    public = {
        "claim_id": None,
        "kind": "navigation",
        "proposition": (f"Let f be the sequence held by the arena. For every "
                        f"integer n with 1 <= n <= {n_max}, f(n) mod {M} is "
                        f"not {R}."),
        "domain": f"integers n with 1 <= n <= {n_max}",
        "quantifiers": f"for all n in [1, {n_max}]",
        # The third hypothesis is the route hint. Disclosing it hands the seat
        # the cheap strategy: v0.2 A0 came in at 1.6x the achievable floor with
        # 29 of 32 seats naming the recurrence fit, and several said outright
        # that the hypothesis made the sealed object "identifiable rather than
        # opaque". Withholding it is the whole experiment - a seat must now
        # DISCOVER that the sequence has exploitable structure.
        "hypotheses": [
            "f is an integer sequence; its defining coefficients are sealed",
            "f may be observed only through the metered interface",
        ] + ([] if blind else
             ["f satisfies a linear recurrence of order at most 2"]),
        "disclosure": "blind" if blind else "structure_disclosed",
        "observable": (f"sample(n) returns f(n) mod {M}; evaluate(n) tests the "
                       "proposition at n"),
    }
    sealed = {
        "claim_id": None,
        "sealed_class": cls,
        "truth_status": "TRUE" if first is None else "FALSE",
        "oracle_disposition": "TRUE" if first is None else "FALSE",
        "witness": None if first is None else {"n": first},
        "sealed_component": True,
        "witness_var": "n",
        "domain_lo": 1, "domain_hi": n_max,
        "claim_predicate": f"lin_rec(n, {a0}, {a1}, {p}, {q}) % {M} != {R}",
        # observations are RESIDUES, not the raw terms. f(600) with roots up to
        # 7 is a 500-digit integer; nobody needs that, and the recurrence is
        # recoverable modulo M just as well, which is all the proposition needs.
        "sealed_value_expr": f"lin_rec(n, {a0}, {a1}, {p}, {q}) % {M}",
        "params": {"r": r, "s": s, "C": C, "D": D, "p": p, "q": q,
                   "a0": a0, "a1": a1, "M": M, "R": R, "N": n_max},
        "route_menu": {
            "enumerate": cost_enumerate,
            "boundary": cost_boundary,
            "fit_recurrence": cost_fit,
        },
        "cheapest_route": "fit_recurrence",
        "achievable_floor": cost_fit,
        "enumerate_within_budget": enumerate_within_budget,
        "budget_assumed": budget,
    }
    return public, sealed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--count", type=int, default=40)
    ap.add_argument("--seed", type=int, default=20260826)
    ap.add_argument("--n-max", type=int, default=600)
    ap.add_argument("--budget", type=int, default=120)
    ap.add_argument("--out", default=str(ARENA / "heldout" / "NAV_PILOT"))
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--blind", action="store_true",
                    help="withhold the structural hypothesis from the public "
                         "package; the sealed record is unchanged")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    out = Path(args.out)
    # Clear before writing. generate.py already refuses to merge two runs; this
    # module did not, and a 32-claim run silently inherited 28 files from a
    # previous 60-claim run whose records lacked a field added since. Same
    # defect class, second location - worth a guard rather than a habit.
    existing = list((out / "sealed").glob("*.json")) if out.exists() else []
    if existing and not args.overwrite:
        raise SystemExit(
            f"{out} already holds {len(existing)} items. Pass --overwrite to "
            "rebuild from scratch, or choose a different --out.")
    for sub in ("public", "sealed"):
        if (out / sub).exists():
            shutil.rmtree(out / sub)
        (out / sub).mkdir(parents=True, exist_ok=True)

    # Half TRUE, half FALSE. An equal three-way split would make 2/3 of the set
    # false, and a seat that answered FALSE to everything would score 67%
    # without resolving anything.
    classes = ["NAV_TRUE", "NAV_FALSE_NEAR", "NAV_TRUE", "NAV_FALSE_FAR"]
    made, tries = [], 0
    while len(made) < args.count and tries < args.count * 60:
        tries += 1
        cls = classes[len(made) % len(classes)]
        got = build(rng, args.n_max, cls, args.budget, args.blind)
        if not got:
            continue
        pub, sea = got
        cid = f"NAV-{len(made):04d}"
        pub["claim_id"] = sea["claim_id"] = cid
        (out / "public" / f"{cid}.json").write_text(
            json.dumps(pub, indent=2) + "\n", encoding="utf-8", newline="\n")
        (out / "sealed" / f"{cid}.json").write_text(
            json.dumps(sea, indent=2) + "\n", encoding="utf-8", newline="\n")
        made.append(sea)

    enum = [m["route_menu"]["enumerate"] for m in made]
    bnd = [m["route_menu"]["boundary"] for m in made
           if m["route_menu"]["boundary"] is not None]
    by_class = {}
    for m in made:
        by_class[m["sealed_class"]] = by_class.get(m["sealed_class"], 0) + 1
    manifest = {
        "set_name": out.name, "emitted": len(made), "seed": args.seed,
        "n_max": args.n_max, "budget": args.budget,
        "disclosure": "blind" if args.blind else "structure_disclosed",
        "counts_by_class": by_class,
        "enumerate_within_budget":
            f"{sum(1 for m in made if m['enumerate_within_budget'])}/{len(made)}",
        "route_cost_summary": {
            "enumerate": {"min": min(enum), "median": sorted(enum)[len(enum)//2],
                          "max": max(enum)},
            "boundary_solvable": f"{len(bnd)}/{len(made)}",
            "fit_recurrence": 5,
        },
        "headroom_ratio_median_enumerate_over_fit":
            round(sorted(enum)[len(enum)//2] / 5, 1),
    }
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                       encoding="utf-8", newline="\n")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
