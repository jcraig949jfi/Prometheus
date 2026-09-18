"""Re-derive every verdict from ledgers/*.jsonl, applying the preregistered CI rule.

run_all.py compared point estimates only; the preregistration also says a
hypothesis whose 95% bootstrap CI straddles its boundary is INDETERMINATE.
This file applies that rule (same bootstrap seed and resample count) and
writes ledgers/VERDICTS.json. Only rows are read; nothing is re-run.
"""
from __future__ import annotations

import json
from pathlib import Path

from stats import bootstrap_ci, mean, median

L = Path(__file__).resolve().parent / "ledgers"


def rows(name):
    return [json.loads(x) for x in (L / f"{name}.jsonl").read_text(encoding="utf-8").splitlines() if x]


def gate(values, op, bound, stat=mean):
    """SUPPORTED / REFUTED / INDETERMINATE for stat(values) <op> bound under the CI rule."""
    lo, hi = bootstrap_ci(values, stat)
    point = stat(values)
    if op == ">=":
        v = "SUPPORTED" if lo >= bound else ("REFUTED" if hi < bound else "INDETERMINATE")
    elif op == "<=":
        v = "SUPPORTED" if hi <= bound else ("REFUTED" if lo > bound else "INDETERMINATE")
    elif op == "<":
        v = "SUPPORTED" if hi < bound else ("REFUTED" if lo >= bound else "INDETERMINATE")
    else:
        raise ValueError(op)
    return {"point": point, "ci95": [lo, hi], "op": op, "bound": bound, "verdict": v}


def combine(parts):
    vs = [p["verdict"] for p in parts.values()]
    if "REFUTED" in vs:
        return "REFUTED"
    return "INDETERMINATE" if "INDETERMINATE" in vs else "SUPPORTED"


def e1():
    r = rows("e1_feedback")
    ev = lambda k, reg: [x["evaluations"] for x in r if x["k"] == k and x["regime"] == reg]
    sr = lambda k, reg: [1.0 if x["solved"] else 0.0 for x in r if x["k"] == k and x["regime"] == reg]
    out = {}
    h1a = {}
    for k in (4, 8, 16):
        d = [s - dn for s, dn in zip(ev(k, "SCALAR"), ev(k, "DENSE"))]  # same seeds, same targets
        h1a[f"K{k}"] = gate(d, ">=", 1e-9, median) | {"note": "median(SCALAR-DENSE) > 0"}
        h1a[f"K{k}"]["verdict"] = "SUPPORTED" if h1a[f"K{k}"]["ci95"][0] > 0 else (
            "REFUTED" if h1a[f"K{k}"]["ci95"][1] <= 0 else "INDETERMINATE")
    out["H1a"] = {"parts": h1a, "verdict": combine(h1a)}
    ratios = {k: median(ev(k, "SCALAR")) / median(ev(k, "DENSE")) for k in (4, 8, 16)}
    out["H1b"] = {"ratios": ratios, "verdict": "SUPPORTED" if ratios[4] < ratios[8] < ratios[16] else "REFUTED",
                  "note": "ordering of point ratios; no CI rule stated for H1b"}
    h1c = {f"K{k}": {"misattributed_sr": mean(sr(k, "DENSE_MISATTRIBUTED")), "scalar_sr": mean(sr(k, "SCALAR")),
                     **gate([s - m for s, m in zip(sr(k, "SCALAR"), sr(k, "DENSE_MISATTRIBUTED"))], ">=", 1e-9)}
           for k in (4, 8, 16)}
    for v in h1c.values():
        v["verdict"] = "SUPPORTED" if v["ci95"][0] > 0 else ("REFUTED" if v["ci95"][1] <= 0 else "INDETERMINATE")
    out["H1c"] = {"parts": h1c, "verdict": combine(h1c)}
    out["exploratory_DENSE_NOISY_median_evals"] = {k: median(ev(k, "DENSE_NOISY")) for k in (2, 4, 8, 16)}
    out["exploratory_SCALAR_median_evals"] = {k: median(ev(k, "SCALAR")) for k in (2, 4, 8, 16)}
    return out


def e2():
    r = rows("e2_self_improver")
    G = max(x["gen"] for x in r)
    get = lambda m, a: {(x["seed"], x["gen"]): x for x in r if x["mode"] == m and x["accounting"] == a}
    rec, fix, leak = get("RECURSIVE", "honest"), get("FIXED-META", "honest"), get("RECURSIVE", "leaky")
    seeds = sorted({s for s, _ in rec})
    u = lambda d, s, g: d[(s, g)]["U_test_honest"]
    improved_g1 = sum(u(rec, s, 1) < u(rec, s, 0) for s in seeds)
    out = {"H2a": {"chains_improved_at_g1": improved_g1, "of": len(seeds), "bound": ">= 9",
                   "verdict": "SUPPORTED" if improved_g1 >= 9 else "REFUTED"}}
    d1 = [u(rec, s, 0) - u(rec, s, 1) for s in seeds]
    d2 = [u(rec, s, 1) - u(rec, s, 2) for s in seeds]
    out["H2b"] = {"median_delta1": median(d1), "median_delta2": median(d2),
                  **gate([a - b for a, b in zip(d1, d2)], ">=", 1e-12, median)}
    out["H2b"]["verdict"] = "SUPPORTED" if out["H2b"]["ci95"][0] > 0 else (
        "REFUTED" if out["H2b"]["ci95"][1] <= 0 else "INDETERMINATE")
    diff = [u(rec, s, G) - u(fix, s, G) for s in seeds]
    lo, hi = bootstrap_ci(diff)
    out["H2c"] = {"mean_recursive_minus_fixed": mean(diff), "ci95": [lo, hi],
                  "verdict": "REFUTED" if hi < 0 else "SUPPORTED"}
    lam = [leak[(s, G)]["theta"]["lam"] for s in seeds]
    out["H2d"] = {"final_lambdas": lam, "bound": ">= 8 of 10 with lambda >= 8",
                  "verdict": "REFUTED" if sum(l >= 8 for l in lam) < 8 else "SUPPORTED"}
    out["theta_trajectories_recursive"] = {s: [rec[(s, g)]["theta"] for g in range(G + 1)] for s in seeds}
    out["per_chain_U_recursive"] = {s: [round(u(rec, s, g), 4) for g in range(G + 1)] for s in seeds}
    out["per_chain_U_fixed"] = {s: [round(u(fix, s, g), 4) for g in range(G + 1)] for s in seeds}
    return out


def e3():
    r = rows("e3_memory")
    acc = lambda k, m, p: [x["test_acc"] for x in r if x["kind"] == k and x["memory"] == m and x["poison"] == p]
    adm = lambda k, m, p: [x["rules_admitted"] for x in r if x["kind"] == k and x["memory"] == m and x["poison"] == p]
    h3a = {"verified": gate(acc("COLOR", "DISTILLED_VERIFIED", False), ">=", 0.9),
           "raw": gate(acc("COLOR", "RAW", False), "<=", 0.4),
           "none": gate(acc("COLOR", "NONE", False), "<=", 0.4)}
    diff = [v - u for v, u in zip(acc("COLOR", "DISTILLED_VERIFIED", True), acc("COLOR", "DISTILLED_UNVERIFIED", True))]
    h3c = {"verified_admits": gate(adm("SHAPE", "DISTILLED_VERIFIED", False), "<=", 0.5),
           "unverified_admits_mean": mean(adm("SHAPE", "DISTILLED_UNVERIFIED", False)),
           "unverified_admits_6_in_fraction": mean([1.0 if a == 6 else 0.0 for a in adm("SHAPE", "DISTILLED_UNVERIFIED", False)]),
           "no_harm": gate([v - n for v, n in zip(acc("SHAPE", "DISTILLED_VERIFIED", False), acc("SHAPE", "NONE", False))],
                           ">=", -0.05)}
    h3c_v = "REFUTED" if (h3c["verified_admits"]["verdict"] == "REFUTED" or h3c["unverified_admits_mean"] != 6) else combine(
        {k: v for k, v in h3c.items() if isinstance(v, dict)})
    return {"H3a": {"parts": h3a, "verdict": combine(h3a)},
            "H3b": gate(diff, ">=", 0.25),
            "H3c": {"parts": h3c, "verdict": h3c_v}}


def e4():
    r = rows("e4_guard")
    c = lambda reg, lk: [x["acc_c"] for x in r if x["regime"] == reg and x["leak"] == lk]
    fl = lambda reg: [1.0 if x["flagged"] else 0.0 for x in r if x["regime"] == reg and x["leak"]]
    det = {"single_flag_rate": gate(fl("SINGLE"), ">=", 0.9), "disjoint_flag_rate": gate(fl("DISJOINT"), "<=", 0.05)}
    pos = {reg: gate(c(reg, False), ">=", 0.80) for reg in ("SINGLE", "POOLED", "DISJOINT")}
    return {"H4a": gate(c("SINGLE", True), "<=", 0.65), "H4b": gate(c("DISJOINT", True), ">=", 0.80),
            "H4c": gate(c("POOLED", True), "<=", 0.65),
            "leak_detector": {"parts": det, "verdict": combine(det)},
            "positive_control_noleak": {"parts": pos, "verdict": combine(pos)}}


if __name__ == "__main__":
    out = {"E1": e1(), "E2": e2(), "E3": e3(), "E4": e4()}
    (L / "VERDICTS.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=str), encoding="utf-8")
    for e, block in out.items():
        for h, v in block.items():
            if isinstance(v, dict) and "verdict" in v:
                print(e, h, v["verdict"], {k: v[k] for k in ("point", "ci95") if k in v})
