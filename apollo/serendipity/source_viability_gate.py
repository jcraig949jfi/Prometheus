"""source_viability_gate.py -- the Source Viability Gate (HITL ruling 2026-09-01).

The lesson of S1: a RELATIVE bar (tau from random) cannot detect the pathology where
random itself defines a meaningless floor. So ABSOLUTE CALIBRATION comes BEFORE any
relative comparison. No archive-value campaign may run against an engine/release until
that engine PASSES this gate. Machine-enforced, not a checklist (s1_campaign refuses to
run the scored phase without a PASS artifact for the target engine+release).

Four gates, all must PASS:
  G1 FRONTIER DEPTH   >= G1_MIN_NONTRIVIAL distinct NONTRIVIAL operation types reach an
                      absolute functional-fitness threshold (not identity/increment,
                      not parameterizations of one trivial op).
  G2 POPULATION MASS  a passing task has >= G2_MIN_MASS distinct organisms at/above the
                      threshold (not one lucky champion).
  G3 HEADROOM         best-fitness across the ladder spans >= G3_MIN_RANGE and is neither
                      all-floor nor all-ceiling (so a downstream enrichment statistic is
                      not saturated).
  G4 NEGATIVE DISCRIM the dead/random control stays BELOW the threshold on both depth and
                      mass (structureless worlds must not clear the bar).

Usage:
  python apollo/serendipity/source_viability_gate.py --engine stackvm-v1 [--budget 600]
  python apollo/serendipity/source_viability_gate.py --from-ladder <ladder.json>
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import foundry_creds as fc      # noqa: E402
import world_adapter as wa      # noqa: E402
import eval_adapter as ea       # noqa: E402
import s1_worlds as sw          # noqa: E402

PIN = "50b5c2327c64bf112c635ca1487f2b1a8fd64e1b7faade9476d5dfa7215fd492"
OUT = HERE.parent / "cycles" / "S1_archive_value" / "gate"

# --- FROZEN thresholds (absolute; do not tune to make an engine pass) ---
THETA_FUNCTIONAL = 0.5     # fitness >= 0.5 = passes at least half the cases = "functional"
G1_MIN_NONTRIVIAL = 3      # >= 3 distinct nontrivial operation types reach THETA
G2_MIN_MASS = 3            # >= 3 distinct organisms at/above THETA on a passing task
G3_MIN_RANGE = 0.5         # ladder best-fitness spread; and not all-floor/all-ceiling

# Distinct NONTRIVIAL operation types (not identity/increment; not one op reparameterized)
NONTRIVIAL = {
    "add_const": lambda x: x + 5,
    "multiply":  lambda x: 2 * x,
    "affine":    lambda x: 3 * x + 1,
    "abs":       lambda x: abs(x),
    "modular":   lambda x: ((x % 3) + 3) % 3,
    "square":    lambda x: x * x,
    "threshold": lambda x: max(x, 0),
}


def _pop_mass(c, s0, s1, theta):
    """# distinct organisms with fitness >= theta, from the run's ledger bracket."""
    span = max(s1 - s0 + 5, 1)
    page = c.get(f"/v0/events?start_seq={s0}&limit={min(span, 1000)}")
    seen = {}
    for e in page.get("events", []):
        if e.get("kind") == "ARTIFACT_EXECUTED":
            p = e.get("payload", {})
            aid = p.get("artifact_id")
            fit = (p.get("result") or {}).get("fitness")
            if aid is not None and fit is not None:
                seen[aid] = max(seen.get(aid, 0.0), fit)
    return sum(1 for f in seen.values() if f >= theta)


def run_gate(engine, budget=600, seed=20260901):
    c = fc.make_client(expected_release_hash=PIN, timeout_s=500.0)
    ladder = {}
    for name, fn in NONTRIVIAL.items():
        task = wa.ensure_task(c, sw._cases(fn, sw.X_TRAIN), campaign="gate",
                              run_id=f"{engine}-{name}", rule=name)
        s0 = c.get("/v0/health")["ledger_len"]
        rep = ea.burst(c, "map_elites", engine, task, seed, budget)["report"]
        s1 = c.get("/v0/health")["ledger_len"]
        ladder[name] = {"best_fitness": rep.get("best_fitness"),
                        "solved": rep.get("solved"),
                        "pop_mass": _pop_mass(c, s0, s1, THETA_FUNCTIONAL)}
        print(f"  {name:10s} best={ladder[name]['best_fitness']:.3f} "
              f"mass={ladder[name]['pop_mass']}", flush=True)
    # dead-world control
    dw = sw.dead_random_world()
    task = wa.ensure_task(c, dw["train_cases"], campaign="gate",
                          run_id=f"{engine}-DEAD", rule="dead")
    s0 = c.get("/v0/health")["ledger_len"]
    rep = ea.burst(c, "map_elites", engine, task, seed, budget)["report"]
    s1 = c.get("/v0/health")["ledger_len"]
    dead = {"best_fitness": rep.get("best_fitness"),
            "pop_mass": _pop_mass(c, s0, s1, THETA_FUNCTIONAL)}
    print(f"  DEAD       best={dead['best_fitness']:.3f} mass={dead['pop_mass']}", flush=True)
    return {"engine": engine, "release_pin": PIN, "budget": budget, "seed": seed,
            "ladder": ladder, "dead": dead}


def verdict(result):
    ladder, dead = result["ladder"], result.get("dead", {})
    passing = [n for n, v in ladder.items()
               if (v.get("best_fitness") or 0) >= THETA_FUNCTIONAL]
    g1 = len(passing) >= G1_MIN_NONTRIVIAL
    g2 = (all((ladder[n].get("pop_mass") or 0) >= G2_MIN_MASS for n in passing)
          if passing else False)
    bests = [v.get("best_fitness") or 0 for v in ladder.values()]
    spread = (max(bests) - min(bests)) if bests else 0
    g3 = spread >= G3_MIN_RANGE and max(bests) > 0.05 and min(bests) < 0.95
    g4 = ((dead.get("best_fitness") or 0) < THETA_FUNCTIONAL
          and (dead.get("pop_mass") or 0) < G2_MIN_MASS)
    result["gates"] = {"G1_frontier_depth": g1, "G1_passing_ops": passing,
                       "G2_population_mass": g2, "G3_headroom": g3,
                       "G3_spread": round(spread, 3), "G4_negative_discrim": g4}
    result["verdict"] = "PASS" if (g1 and g2 and g3 and g4) else "FAIL"
    result["thresholds"] = {"THETA_FUNCTIONAL": THETA_FUNCTIONAL,
                            "G1_MIN_NONTRIVIAL": G1_MIN_NONTRIVIAL,
                            "G2_MIN_MASS": G2_MIN_MASS, "G3_MIN_RANGE": G3_MIN_RANGE}
    return result


def gate_artifact_path(engine, pin=PIN):
    return OUT / f"gate_{engine}_{pin[:12]}.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine")
    ap.add_argument("--budget", type=int, default=600)
    ap.add_argument("--from-ladder", help="compute verdict from an existing ladder JSON "
                    "(best_fitness/pop_mass per op + dead) without new bursts")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.from_ladder:
        result = json.loads(Path(args.from_ladder).read_text(encoding="utf-8"))
    else:
        if not args.engine:
            ap.error("--engine required unless --from-ladder")
        print(f"SOURCE VIABILITY GATE: {args.engine} @ {PIN[:12]} budget {args.budget}")
        result = run_gate(args.engine, args.budget)
    result = verdict(result)
    result["computed_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out = gate_artifact_path(result["engine"], result.get("release_pin", PIN))
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"\nGATES: {result['gates']}")
    print(f"VERDICT: {result['verdict']}  -> {out}")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
