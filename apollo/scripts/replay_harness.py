"""replay_harness.py — O6: re-run Apollo's load-bearing numbers and alarm on drift.

Motivation, measured 2026-08-19: a result validated in June still reproduced, but took
8.6x longer to find (mean 30 -> 255 generations). Nothing broke — the operator pool grew
14 -> 25 and a fitness term written for one mode became collateral damage in another. The
substrate grew around an archived number and NOBODY WOULD HAVE NOTICED. The June "4/5"
would still be cited today had the type-bridge cycle not re-run it.

Both external reviewers (2026-08-23) ranked this "do regardless of O1's outcome."

Each claim carries: what was measured, when, the recorded value, a tolerance, and an
executable check. FAST claims are seconds (scoring/pipeline layer — where silent rot
actually lives). SLOW claims require evolution runs and are opt-in.

Usage:
    python replay_harness.py                 # fast tier
    python replay_harness.py --slow          # include evolution-dependent claims
    python replay_harness.py --update        # re-baseline (records who/when; use sparingly)
Exit: 0 all within tolerance · 1 any drift
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "agents" / "hephaestus" / "src"))

CLAIMS = HERE.parent / "pivot" / "replay_claims.json"

import blackboard_evolve as be  # noqa: E402


_BATTERY = None


def battery():
    """Built EXACTLY ONCE per process. This is not an optimisation.

    `composition_gauntlet.build_synthetic_canary` draws from a module-level RNG that it
    never re-seeds, so a SECOND call in the same process returns DIFFERENT tasks (verified
    2026-08-23: synth content hash f34b7fa9 -> e56ae840). Every production caller happens
    to build once, which is why historical runs are internally consistent and why this
    never surfaced. The first version of this harness rebuilt per check and was therefore
    scoring four different batteries — see claim `synth_battery_idempotent`."""
    global _BATTERY
    if _BATTERY is None:
        canary = json.loads((SRC.parent / "data" / "clean_canary_v01.json")
                            .read_text(encoding="utf-8"))["tasks"]
        from composition_gauntlet import build_synthetic_canary
        from inference_canary import build_inference_canary
        from cross_tier_canary import build_cross_tier_canary
        _BATTERY = (canary, build_synthetic_canary(n_each=15),
                    build_inference_canary(n=20), build_cross_tier_canary(n=20))
    return _BATTERY


def acc(pipeline, tasks):
    return be._evaluate_acc([be.REGISTRY[n][0] for n in pipeline if n in be.REGISTRY], tasks)


KNOWN_0833 = ["parse_comparison", "parse_which_extreme", "parse_box_items",
              "op_aggregate_quantities", "parse_rules", "parse_ordinal", "forward_chain",
              "parse_names_and_relations", "relations_from_facts", "op_build_ordering",
              "score_by_extreme_number__g", "score_by_aggregate__g",
              "score_by_derivability__g", "score_by_comparison__g", "select_nth__g"]

CROSS_TIER_SOLVER = ["parse_rules", "parse_ordinal", "forward_chain",
                     "relations_from_facts", "op_build_ordering", "select_nth"]


# ── checks: each returns a float ──────────────────────────────────────

def c_known_organism_battery():
    can, syn, inf, xt = battery()
    return acc(KNOWN_0833, can + syn + inf + xt)


def c_known_organism_routable():
    can, syn, inf, xt = battery()
    return acc(KNOWN_0833, syn + inf + xt)


def c_cross_tier_solver():
    _, _, _, xt = battery()
    return acc(CROSS_TIER_SOLVER, xt)


def c_single_primitive_baseline():
    can, syn, inf, xt = battery()
    return be._single_primitive_baseline(can + syn + inf + xt)


def c_registry_size():
    return float(len(be.REGISTRY))


def c_transformer_count():
    return float(len(be.TRANSFORMERS))


def c_scorer_count():
    return float(len(be.SCORERS))


def c_battery_size():
    can, syn, inf, xt = battery()
    return float(len(can) + len(syn) + len(inf) + len(xt))


def c_terminal_only():
    can, syn, inf, xt = battery()
    return acc(["score_by_max_value"], can + syn + inf + xt)


def c_bridge_is_load_bearing():
    """The 2026-06-10 claim: removing the bridge collapses cross-tier accuracy."""
    _, _, _, xt = battery()
    with_bridge = acc(CROSS_TIER_SOLVER, xt)
    without = acc([n for n in CROSS_TIER_SOLVER if n != "relations_from_facts"], xt)
    return with_bridge - without


def c_synth_battery_idempotent():
    """1.0 if rebuilding the synth subset yields identical tasks, else 0.0.

    Currently 0.0. Recorded as a FAILING claim on purpose: a known defect that is visible
    every run is safer than one that is quietly waiting for the next analysis script to
    build the battery twice. Not fixed here — re-seeding would change the synth tasks and
    silently invalidate comparability with every historical Apollo number. That is James's
    call, not a harness decision."""
    import hashlib
    from composition_gauntlet import build_synthetic_canary
    def h(ts):
        return hashlib.md5(json.dumps([t["prompt"] for t in ts]).encode()).hexdigest()
    def full(ts):
        return hashlib.md5(json.dumps(
            [[t["prompt"], t["candidates"], t["correct"]] for t in ts]).encode()).hexdigest()
    a = build_synthetic_canary(n_each=15)
    b = build_synthetic_canary(n_each=15)
    return 1.0 if (h(a) == h(b) and full(a) == full(b)) else 0.0


def c_trivial_longest_candidate():
    can, syn, inf, xt = battery()
    ts = can + syn + inf + xt
    return sum(1 for t in ts if max(t["candidates"], key=len) == t["correct"]) / len(ts)


def c_ab_discovery_rate():
    """SLOW: the 2026-06-16 A/B treatment arm, replayed. 5 seeds x 400 gens, ~8 min."""
    sys.path.insert(0, str(HERE))
    import type_bridge_cycle as tbc
    hits = 0
    for seed in tbc.SEEDS:
        r = tbc.run_cell("A3", seed)
        hits += int(r["discovered"])
    return hits / len(tbc.SEEDS)


CHECKS = {
    "known_organism_battery_acc": (c_known_organism_battery, "fast"),
    "known_organism_routable_acc": (c_known_organism_routable, "fast"),
    "cross_tier_solver_acc": (c_cross_tier_solver, "fast"),
    "bridge_load_bearing_delta": (c_bridge_is_load_bearing, "fast"),
    "single_primitive_baseline": (c_single_primitive_baseline, "fast"),
    "registry_size": (c_registry_size, "fast"),
    "transformer_count": (c_transformer_count, "fast"),
    "scorer_count": (c_scorer_count, "fast"),
    "battery_size": (c_battery_size, "fast"),
    "terminal_only_acc": (c_terminal_only, "fast"),
    "trivial_longest_candidate": (c_trivial_longest_candidate, "fast"),
    "synth_battery_idempotent": (c_synth_battery_idempotent, "fast"),
    "ab_crossover_discovery_rate": (c_ab_discovery_rate, "slow"),
}


DEFAULT_CLAIMS = {
    "known_organism_battery_acc": {"value": 0.833, "tol": 0.001, "recorded": "2026-06-27",
        "why": "the headline max_acc. If this moves, every Apollo number moves."},
    "known_organism_routable_acc": {"value": 1.0, "tol": 0.001, "recorded": "2026-06-27",
        "why": "one organism fully solves synth+inference+cross_tier."},
    "cross_tier_solver_acc": {"value": 1.0, "tol": 0.001, "recorded": "2026-06-10",
        "why": "the cross-tier falsification. The multi-tier organism is the unique solver."},
    "bridge_load_bearing_delta": {"value": 0.6, "tol": 0.05, "recorded": "2026-08-23",
        "why": "removing relations_from_facts drops cross-tier accuracy by 0.6, from 1.0 "
               "to the 0.4 trivial-heuristic floor for that subset — NOT to zero. My first "
               "baseline here assumed 1.0 from the June write-up; measured, it is 0.6. The "
               "bridge is load-bearing for everything above the benchmark artifact floor, "
               "which is the honest form of the claim."},
    "single_primitive_baseline": {"value": 0.0, "tol": 0.001, "recorded": "2026-08-23",
        "why": "pinned at 0 by construction, which makes comp_lift identical to acc. "
               "If it ever moves, comp_lift starts meaning something and every historical "
               "ccs reading needs reinterpreting."},
    "registry_size": {"value": 27.0, "tol": 0.0, "recorded": "2026-08-23",
        "why": "the pool grew 14 -> 25 unnoticed and cost 8.6x search efficiency. "
               "Growth is allowed; growth WITHOUT NOTICE is what caused the rot."},
    "transformer_count": {"value": 15.0, "tol": 0.0, "recorded": "2026-08-23", "why": "as above."},
    "scorer_count": {"value": 10.0, "tol": 0.0, "recorded": "2026-08-23", "why": "as above."},
    "battery_size": {"value": 120.0, "tol": 0.0, "recorded": "2026-08-23",
        "why": "every accuracy in the corpus is denominated in this battery."},
    "terminal_only_acc": {"value": 0.292, "tol": 0.005, "recorded": "2026-08-23",
        "why": "the no-composition floor Apollo must beat to mean anything."},
    "trivial_longest_candidate": {"value": 0.338, "tol": 0.006, "recorded": "2026-08-23",
        "why": "benchmark-artifact floor; if it rises, the battery is leaking. Tolerance "
               "covers the observed 0.333-0.342 range, which is one task and is caused by "
               "the synth non-idempotency below. A residual cross-process difference was "
               "NOT fully reconciled; the tolerance is honest about that rather than "
               "pretending the quantity is exact."},
    "synth_battery_idempotent": {"value": 1.0, "tol": 0.0, "recorded": "2026-08-23",
        "why": "KNOWN FAILING. build_synthetic_canary draws from an unseeded module-level "
               "RNG, so rebuilding in one process yields different tasks (25% of the "
               "battery). Left failing deliberately so the defect stays visible."},
    "ab_crossover_discovery_rate": {"value": 0.6, "tol": 0.2, "recorded": "2026-08-19",
        "why": "the crossover result. Was 4/5 in June, replayed 3/5 in August. Wide "
               "tolerance because n=5 is coarse; the point is to catch a collapse to 0."},
}


def load_claims():
    if CLAIMS.exists():
        return json.loads(CLAIMS.read_text(encoding="utf-8"))
    return {"claims": DEFAULT_CLAIMS, "history": []}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slow", action="store_true")
    ap.add_argument("--update", action="store_true")
    args = ap.parse_args()

    db = load_claims()
    claims = db["claims"]
    tiers = ("fast", "slow") if args.slow else ("fast",)

    print(f"{'claim':32s} {'recorded':>9s} {'now':>9s} {'delta':>9s}  drift  "
          f"{'evidence':>9s}  standing")
    print("-" * 96)
    drift, results = [], {}
    for name, (fn, tier) in CHECKS.items():
        if tier not in tiers or name not in claims:
            continue
        exp = claims[name]["value"]
        tol = claims[name]["tol"]
        t0 = time.time()
        try:
            got = float(fn())
        except Exception as e:
            print(f"{name:32s} {exp:>9.3f} {'ERROR':>9s} {'':>9s}  {type(e).__name__}: {e}")
            drift.append((name, exp, None, f"check raised {type(e).__name__}"))
            continue
        d = got - exp
        ok = abs(d) <= tol
        results[name] = got
        cl = claims[name]
        nsurv = len(cl.get("survived_falsifications", []))
        need = cl.get("required_falsifications", 1)
        standing = cl.get("status", "?")
        print(f"{name:32s} {exp:>9.3f} {got:>9.3f} {d:>+9.3f}  "
              f"{'ok   ' if ok else 'DRIFT'}  {nsurv:>4d}/{need:<4d}  {standing}"
              f"{'' if standing == 'ESTABLISHED' else '  (' + cl.get('favours_lane','') + ')'}")
        if not ok:
            drift.append((name, exp, got, claims[name]["why"]))

    if args.update:
        for n, v in results.items():
            claims[n]["value"] = round(v, 4)
            claims[n]["recorded"] = "2026-08-23"
        db.setdefault("history", []).append(
            {"date": "2026-08-23", "by": "Apollo (M2)", "action": "re-baseline",
             "values": {k: round(v, 4) for k, v in results.items()}})
        CLAIMS.parent.mkdir(parents=True, exist_ok=True)
        with open(CLAIMS, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        print(f"\nre-baselined {len(results)} claims -> {CLAIMS}")
        return 0

    if not CLAIMS.exists():
        CLAIMS.parent.mkdir(parents=True, exist_ok=True)
        CLAIMS.write_text(json.dumps(db, indent=2), encoding="utf-8")
        print(f"\ninitialised claim registry -> {CLAIMS}")

    prov = [n for n in results if claims[n].get("status") == "PROVISIONAL"]
    fav_prov = [n for n in prov if claims[n].get("favours_lane") == "favours"]
    print(f"\nPROVISIONAL: {len(prov)} of {len(results)} claims have not yet survived the "
          f"required number of independent falsifications.")
    if fav_prov:
        print(f"  Of those, {len(fav_prov)} FAVOUR the lane and are therefore the ones most "
              f"likely to be wrong and least likely to be attacked:")
        for n in fav_prov:
            print(f"    {n} ({len(claims[n]['survived_falsifications'])}/"
                  f"{claims[n]['required_falsifications']})")
    print()
    if drift:
        print(f"DRIFT DETECTED in {len(drift)} claim(s):")
        for n, e, g, why in drift:
            print(f"  {n}: recorded {e}, now {g}")
            print(f"     why it matters: {why}")
        return 1
    print(f"all {len(results)} claims within tolerance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
