"""Derive Campaign 1 economics and substrate selection from committed benchmark receipts.

Operator rules (2026-09-18): hosts are measurements, not replicas; two-host
throughput comes from sharding independent lineages across MEASURED
capacities (never "2x"); a single valid host is reported alone; the
selection rule is the fastest model whose frozen starting accuracy lies in
[0.15, 0.70], else NO_ELIGIBLE_SUBSTRATE; design target <= 14 days, hard
ceiling 30 days; near the ceiling use the conservative throughput.

python economics.py FROZEN_SHA256 receipt1.json [receipt2.json ...] > economics.json
"""
from __future__ import annotations

import json
import math
import sys

WINDOW = (0.15, 0.70)
TARGET_DAYS, CEILING_DAYS = 14.0, 30.0
GENERATIONS, ASSAY, SECONDARY = 8, 1760, 320


def valid(r, frozen_sha):
    probs = []
    if r.get("harness_sha256") != frozen_sha:
        probs.append("harness sha256 differs from the frozen harness")
    m = r.get("measured") or {}
    if not m or m.get("model_calls", 0) == 0:
        probs.append("no measurement")
    if m.get("failure_rate", 1) > 0.05:
        probs.append(f"failure rate {m.get('failure_rate')} > 0.05")
    return probs


def capacity(r, evo, which):
    """Lineages per day on this host for a campaign with evo task evaluations per generation."""
    t = r["measured"]["eval_throughput_per_s"][which]
    per_lineage = GENERATIONS * evo + ASSAY + SECONDARY
    return 86400 * t / per_lineage


def shard(L, caps):
    """Integer allocation of L independent lineages minimising makespan; caps in lineages/day."""
    hosts = list(caps)
    if len(hosts) == 1:
        return {hosts[0]: L}, L / caps[hosts[0]]
    best = None
    for n1 in range(L + 1):
        n2 = L - n1
        span = max(n1 / caps[hosts[0]] if n1 else 0.0, n2 / caps[hosts[1]] if n2 else 0.0)
        if best is None or span < best[1]:
            best = ({hosts[0]: n1, hosts[1]: n2}, span)
    return best


def main():
    frozen, paths = sys.argv[1], sys.argv[2:]
    rs = [json.load(open(p, encoding="utf-8")) for p in paths]
    out = {"receipts": [], "by_model": {}, "selection": None}
    by_model = {}
    for p, r in zip(paths, rs):
        probs = valid(r, frozen)
        out["receipts"].append({"path": p, "host": r.get("host_label"), "model": r["model"].get("requested"),
                                "valid": not probs, "problems": probs,
                                "starting_accuracy": r.get("starting_accuracy", {}).get("accuracy")})
        if not probs:
            by_model.setdefault(r["model"]["requested"], []).append(r)
    for model, recs in by_model.items():
        acc = [x["starting_accuracy"]["accuracy"] for x in recs]
        eligible = all(WINDOW[0] <= a <= WINDOW[1] for a in acc)
        m = {"hosts": [x["host_label"] for x in recs], "starting_accuracy_by_host": dict(zip([x["host_label"] for x in recs], acc)),
             "eligible": eligible, "configs": {}}
        for evo in ("measured", 200, 1000):
            for which in ("mean", "conservative"):
                caps = {x["host_label"]: capacity(x, x["measured"]["evaluations_per_generation"] if evo == "measured"
                                                  else evo, which) for x in recs}
                for L in (32, 64):
                    alloc, days = shard(L, caps)
                    m["configs"][f"L{L}|evo{evo}|{which}"] = {
                        "allocation": alloc, "days": round(days, 2),
                        "within_target_14": days <= TARGET_DAYS, "within_ceiling_30": days <= CEILING_DAYS,
                        "hosts_used": len(caps), "caps_lineages_per_day": {h: round(c, 3) for h, c in caps.items()}}
        m["two_host"] = len(recs) == 2
        by_model[model] = m
        out["by_model"][model] = m
    elig = {k: v for k, v in out["by_model"].items() if v["eligible"]}
    if not elig:
        out["selection"] = "NO_ELIGIBLE_SUBSTRATE"
    else:
        # fastest = shortest conservative 64-lineage time at the measured evolution effort
        key = lambda k: elig[k]["configs"]["L64|evomeasured|conservative"]["days"]
        out["selection"] = {"model": min(elig, key=key), "basis": "shortest conservative L64 campaign time "
                            "among models with starting accuracy in [0.15, 0.70] on every measured host"}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
