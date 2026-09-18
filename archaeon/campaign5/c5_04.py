"""C5-04 -- GENERATOR x REPRESENTATION CONTROL (campaign 5, Phase B). Preregistration: C5-04/DESIGN.md.

    python -m archaeon.campaign5.c5_04 [--dry-run] [--self-test] [--n 200]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from archaeon.wse.evolve import evaluate, FOUNDRY                            # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign5.c5base import C5                                     # noqa: E402
from archaeon.campaign5.repb import gen_b                                    # noqa: E402
from archaeon.campaign5.repb.evaluate_b import evaluate_b                    # noqa: E402

ID = "C5-04"
GENERATORS = ("raw", "valid", "injected2")
INTERPRETERS = ("OLD", "B_FAIL", "B_FIZZLE")
SEEDS = (1, 2, 3)


def _strip(r: dict) -> dict:
    r = dict(r); r["meter"] = {k: v for k, v in r["meter"].items() if k not in ("wall_s", "cpu_s")}; return r


def run_one(m: dict, interp: str, eps: list) -> dict:
    if interp == "OLD":
        return _strip(evaluate(m, eps, rng_seed=0, reward_mode="per_ask"))
    return _strip(evaluate_b(m, eps, rng_seed=0, reward_mode="per_ask", mode="FAIL" if interp == "B_FAIL" else "FIZZLE"))


def cell(job: dict) -> dict:
    gen, interp, seed, n = job["generator"], job["interpreter"], job["seed"], job["n"]
    eps = C1.episodes("W0", 16)
    kind, k = ("injected", 2) if gen == "injected2" else (gen, 0)
    pop = gen_b.population(kind, FOUNDRY, seed, n, k=k)
    rows = [run_one(m, interp, eps) for m in pop]
    viable = sum(1 for r in rows if r["answered_share"] > 0) / n
    floor = sum(1 for r in rows if r["reward_per_ask"] >= C1.FLOOR) / n
    out = {"generator": gen, "interpreter": interp, "seed": seed, "n": n, "viable": round(viable, 4), "floor": round(floor, 4),
           "mean_reward": round(sum(r["reward_per_ask"] for r in rows) / n, 4),
           "trapped": round(sum(1 for r in rows if r.get("trapped")) / n, 4), "faulted": round(sum(1 for r in rows if r.get("faults", 0) > 0) / n, 4),
           "rewards": [round(r["reward_per_ask"], 4) for r in rows], "writable": [m["code_writable"] for m in pop]}
    return out


def analyse(cells: list) -> dict:
    T = {}
    for c in cells:
        T.setdefault((c["generator"], c["interpreter"]), []).append(c)
    pooled = {"%s x %s" % k: {"viable": round(sum(c["viable"] for c in v) / len(v), 4), "floor": round(sum(c["floor"] for c in v) / len(v), 4),
                              "mean_reward": round(sum(c["mean_reward"] for c in v) / len(v), 4), "trapped": round(sum(c["trapped"] for c in v) / len(v), 4),
                              "faulted": round(sum(c["faulted"] for c in v) / len(v), 4)} for k, v in T.items()}
    g = lambda gen, it, key: pooled["%s x %s" % (gen, it)][key]                      # noqa: E731
    B = C1.BAND
    P1 = abs(g("raw", "OLD", "viable") - g("valid", "OLD", "viable")) <= B and abs(g("raw", "OLD", "floor") - g("valid", "OLD", "floor")) <= B
    P2 = (abs(g("valid", "OLD", "viable") - g("valid", "B_FAIL", "viable")) <= B and abs(g("valid", "OLD", "viable") - g("valid", "B_FIZZLE", "viable")) <= B
          and abs(g("valid", "OLD", "floor") - g("valid", "B_FAIL", "floor")) <= B and abs(g("valid", "OLD", "floor") - g("valid", "B_FIZZLE", "floor")) <= B)
    P3 = g("raw", "B_FAIL", "viable") <= 0.01 and (g("raw", "OLD", "viable") - g("raw", "B_FIZZLE", "viable")) > B
    P4 = (g("injected2", "B_FIZZLE", "viable") - g("injected2", "B_FAIL", "viable")) > B and g("injected2", "B_FIZZLE", "viable") < g("valid", "B_FIZZLE", "viable")
    # identity control: valid x OLD vs valid x B_FAIL program for program on non-writable programs
    ident = {"n": 0, "equal": 0}
    for s in SEEDS:
        a = next(c for c in cells if c["generator"] == "valid" and c["interpreter"] == "OLD" and c["seed"] == s)
        b = next(c for c in cells if c["generator"] == "valid" and c["interpreter"] == "B_FAIL" and c["seed"] == s)
        for ra, rb, w in zip(a["rewards"], b["rewards"], a["writable"]):
            if not w:
                ident["n"] += 1; ident["equal"] += (ra == rb)
    ident["share"] = round(ident["equal"] / max(1, ident["n"]), 4)
    ctrl = {"positive_injected2_fail_trapped": g("injected2", "B_FAIL", "trapped"), "identity": ident,
            "pass": g("injected2", "B_FAIL", "trapped") >= 0.5 and ident["share"] == 1.0}
    return {"table": pooled, "predictions": {"P1": P1, "P2": P2, "P3": P3, "P4": P4}, "controls": ctrl,
            "representation_effect_viable": {it: round(g("valid", it, "viable") - g("raw", it, "viable"), 4) for it in INTERPRETERS},
            "generator_effect_under_OLD_viable": round(g("valid", "OLD", "viable") - g("raw", "OLD", "viable"), 4)}


def self_test() -> int:
    cells = [cell({"generator": gname, "interpreter": it, "seed": 1, "n": 20}) for gname in GENERATORS for it in INTERPRETERS]
    cells += [cell({"generator": gname, "interpreter": it, "seed": s, "n": 20}) for gname in GENERATORS for it in INTERPRETERS for s in (2, 3)]
    a = analyse(cells)
    again = cell({"generator": "raw", "interpreter": "B_FIZZLE", "seed": 1, "n": 20})
    det = again == next(c for c in cells if c["generator"] == "raw" and c["interpreter"] == "B_FIZZLE" and c["seed"] == 1)
    print(json.dumps({"table": a["table"], "predictions": a["predictions"], "controls": a["controls"], "deterministic": det}, indent=1))
    return 0 if (a["controls"]["pass"] and det) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--procs", type=int, default=9)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C5-04")
    if a.self_test:
        return self_test()
    from archaeon.campaign5.c5base import harness                            # noqa: PLC0415

    class GenRep(harness()):
        ID = "C5-04"
        TITLE = "generator x representation control (no selection)"
        PARENTS = ["C5-03", "C4-01"]
        ARM_FIELD = "arm"
        METRICS = ("viable", "floor", "trapped", "faulted")

    X = GenRep(dry_run=a.dry_run, procs=a.procs)
    design = (C5 / "C5-04" / "DESIGN.md").read_text(encoding="utf-8")
    X.seal({
        "question": "Generator or representation: which one decides whether a sampled program lives or dies, measured without selection?",
        "parent_evidence": "C5-03 fixtures (static and dynamic separation); C4-01 total interpreter.",
        "why_this_slot": "The directive's control before any damage geometry is read on representation B.",
        "assay_capability_requirement": "positive control injected(2) x B_FAIL trapped >= .50; identity control valid x OLD == valid x B_FAIL program for program (non-writable)",
        "positive_control": "controls arm: pass >= 1.0",
        "reachability_estimate": {"note": "not a reach experiment"},
        "arms": ["%s x %s" % (g, i) for g in GENERATORS for i in INTERPRETERS] + ["controls"],
        "crn_policy": "population seed s gives the same programs to every interpreter; W0 train index 1, rng 0",
        "budget": {"n": a.n, "seeds": list(SEEDS), "cells": 27},
        "primary_observable": "viable and floor shares per cell; predictions P1-P4 (DESIGN.md)",
        "claim_ceiling": "a 3 x 3 table under no selection; no mechanism",
        "falsification_condition": "P1 failing means the old generator was not neutral under OLD (affects every C4 census)",
        "kill_condition": "control failure -> INSTRUMENT_INVALID",
        "typed_failure_conditions": ["INSTRUMENT_INVALID"],
        "expected_machine_telemetry": ["per-cell shares", "per-program rewards"],
        "machine_changes_exercised": ["gen_b.population", "evaluate_b"],
        "replacement_condition": "none",
        "ancestry": "original (Phase B, slot 2)",
        "design_digest": "sha256:" + hashlib.sha256(design.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "decl": {"n_min": 3, "positive_control": {"arm": "controls", "metric": "pass", "min": 1.0, "min_rows": 1},
                 "primary": {"treatment": "raw x B_FIZZLE", "control": "raw x OLD", "metric": "viable", "min_effect": -0.0625}},
    })
    X.open("cmp5-c5-04")
    wid = X.world("generator-x-representation", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    jobs = [{"generator": gname, "interpreter": it, "seed": s, "n": a.n} for gname in GENERATORS for it in INTERPRETERS for s in SEEDS]
    cells = X.pool_map(cell, jobs, "cells_s")
    res = analyse(cells)
    grouped = [{"arm": "controls", "pass": float(res["controls"]["pass"]), "n": 1}]
    for c in cells:
        row = {"arm": "%s x %s" % (c["generator"], c["interpreter"]), "seed": c["seed"], "viable": c["viable"], "floor": c["floor"], "trapped": c["trapped"], "faulted": c["faulted"]}
        grouped.append(row)
        X.record(wid, row, {"arm": row["arm"], "seed": c["seed"]}, {k: v for k, v in c.items() if k not in ("rewards", "writable")}, "SURVIVED", key_parts=(row["arm"], c["seed"]))
    res["wall_s"] = round(time.time() - t0, 1)
    X.att.write("GENREP.json", res)
    X.att.write("cells.json", cells)
    X.publish(wid, "genrep", "cmp5.c504_genrep.v1", res, {"info_kind": "artifact", "label": "C5-04 generator x representation table"})
    out = X.close(grouped, addendum={"predictions": json.dumps(res["predictions"]), "table": json.dumps(res["table"])})
    print(json.dumps({"table": res["table"], "predictions": res["predictions"], "controls": res["controls"], "effects": {"representation": res["representation_effect_viable"], "generator_under_OLD": res["generator_effect_under_OLD_viable"]}, "close": out["disposition"]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
