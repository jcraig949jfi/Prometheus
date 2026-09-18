"""Campaign 1 economics and substrate selection from committed benchmark receipts (PREREGISTERED).

Operator directives of 2026-09-18 (benchmark execution; freeze-layer
amendment). Written and hashed into BENCHMARK_MANIFEST before any receipt
exists. Rules:
- VALIDITY: bundle_manifest_sha256 equals the frozen canonical hash and
  bundle_verified is true; harness sha256 equals the frozen harness hash;
  failure_rate <= 0.05; a measurement is present.
- IDENTITY: a candidate is a SERVED VARIANT = (requested model,
  checkpoint, quantisation, runtime family, extra_body). Eligibility,
  accuracy and throughput belong to (variant, host). Nothing is averaged
  across hosts.
- ELIGIBILITY: aggregate starting accuracy (point estimate) in
  [0.15, 0.70]. Per-family accuracies are reported as diagnostics only.
- CROSS-HOST CONSISTENCY: the same variant on two hosts with aggregate
  accuracies differing by >= 0.05 (10 of 200 tasks) is an ANOMALY: the
  hosts are characterised separately and NOT combined until investigated.
- THROUGHPUT, three reported bounds per receipt: (A) mean of per-
  generation throughputs; (B) slowest observed generation; (C) variance-
  aware: seconds per evaluation per generation s_g, upper one-sided 95%
  bound on their mean, mean + t(0.95, n-1) sd / sqrt(n), inverted. The
  DECISION throughput for the 14/30-day rule is the smaller of (C) and the
  harness's frozen conservative value (max(min, mean - 1.2816 sd) for 3+
  generations), i.e. the larger projection. (B) is reported, not used for
  the decision; raw per-generation times are never discarded.
- TWO HOSTS: combined only for an identical variant, eligible on both, no
  anomaly; integer sharding of independent lineages over measured
  DECISION capacities minimising makespan; never averaged, never "2x".
  Otherwise each host is characterised alone and labelled so.
- SELECTION: the fastest (shortest decision-throughput 64-lineage time at
  the measured evolution effort) variant that is eligible on every host it
  was measured on; else NO_ELIGIBLE_SUBSTRATE. A variant eligible on one
  host and not on the other is not selectable (investigate).
- BUDGET: target <= 14 days, hard ceiling 30 days.

python economics.py BENCHMARK_MANIFEST.json receipt1.json [receipt2.json ...]
"""
from __future__ import annotations

import json
import math
import statistics
import sys

WINDOW = (0.15, 0.70)
TARGET_DAYS, CEILING_DAYS = 14.0, 30.0
GENERATIONS, ASSAY, SECONDARY = 8, 1760, 320
ANOMALY_ACC = 0.05
T95 = {1: 6.314, 2: 2.920, 3: 2.353, 4: 2.132, 5: 2.015, 6: 1.943, 7: 1.895, 8: 1.860, 9: 1.833, 10: 1.812}


def variant_key(r):
    m = r["model"]
    return json.dumps([m.get("requested"), m.get("checkpoint"), m.get("quant"),
                       (m.get("runtime") or "").split(" ")[0].lower(), m.get("extra_body")], sort_keys=True)


def valid(r, manifest):
    probs = []
    if r.get("bundle_manifest_sha256") != manifest["canonical_sha256"] or not r.get("bundle_verified"):
        probs.append("bundle manifest hash missing or different (not run through run_frozen.py on the frozen bundle)")
    if r.get("harness_sha256") != manifest["files"]["bench.py"]:
        probs.append("harness sha256 differs from the frozen harness")
    m = r.get("measured") or {}
    if not m or m.get("model_calls", 0) == 0:
        probs.append("no measurement")
    elif m.get("failure_rate", 1) > 0.05:
        probs.append(f"failure rate {m.get('failure_rate')} > 0.05")
    return probs


def bounds(r):
    gens = r["measured"]["per_generation"]
    thr = [g["evals_per_s"] for g in gens]
    spe = [g["wall_s"] / g["evaluations"] for g in gens]
    n = len(spe)
    mean_thr = statistics.mean(thr)
    slowest = min(thr)
    if n >= 2:
        up = statistics.mean(spe) + T95.get(n - 1, 1.645) * statistics.stdev(spe) / math.sqrt(n)
        va = 1.0 / up
    else:
        va = slowest
    harness_cons = r["measured"]["eval_throughput_per_s"]["conservative"]
    return {"A_mean": mean_thr, "B_slowest_generation": slowest, "C_variance_aware_upper95": va,
            "harness_conservative": harness_cons, "DECISION": min(va, harness_cons), "n_generations": n}


def capacity(thr, evo):
    return 86400 * thr / (GENERATIONS * evo + ASSAY + SECONDARY)   # lineages per day


def shard(L, caps):
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
    manifest = json.load(open(sys.argv[1], encoding="utf-8"))
    paths = sys.argv[2:]
    out = {"frozen_bundle": manifest["canonical_sha256"], "receipts": [], "variants": {}, "selection": None}
    good = {}
    for p in paths:
        r = json.load(open(p, encoding="utf-8"))
        probs = valid(r, manifest)
        acc = r.get("starting_accuracy", {})
        out["receipts"].append({"path": p, "host": r.get("host_label"), "variant": variant_key(r),
                                "valid": not probs, "problems": probs, "accuracy": acc.get("accuracy"),
                                "accuracy_wilson95": acc.get("wilson95"), "by_family_DIAGNOSTIC": acc.get("by_family")})
        if not probs:
            good.setdefault(variant_key(r), {})[r["host_label"]] = r
    for key, hosts in good.items():
        v = {"hosts": {}, "combined": None, "notes": []}
        for h, r in hosts.items():
            acc = r["starting_accuracy"]["accuracy"]
            b = bounds(r)
            evo = r["measured"]["evaluations_per_generation"]
            v["hosts"][h] = {"accuracy": acc, "eligible": WINDOW[0] <= acc <= WINDOW[1],
                             "accuracy_wilson95": r["starting_accuracy"]["wilson95"],
                             "by_family_DIAGNOSTIC": r["starting_accuracy"]["by_family"],
                             "throughput_bounds": {k: round(x, 4) if isinstance(x, float) else x for k, x in b.items()},
                             "gpu_identity": r["gpu_identity"], "tokens_in_out": [r["measured"]["tokens_in_per_task"],
                                                                                   r["measured"]["tokens_out_per_task"]],
                             "single_host_days": {f"L{L}|evo{e}|{w}": round(L / capacity(b[w], evo if e == "measured" else e), 2)
                                                  for L in (32, 64) for e in ("measured", 200, 1000)
                                                  for w in ("A_mean", "B_slowest_generation", "C_variance_aware_upper95", "DECISION")}}
        elig = [h for h in v["hosts"] if v["hosts"][h]["eligible"]]
        accs = [v["hosts"][h]["accuracy"] for h in v["hosts"]]
        anomaly = len(accs) == 2 and abs(accs[0] - accs[1]) >= ANOMALY_ACC
        if anomaly:
            v["notes"].append(f"ANOMALY: same served variant, starting accuracies {accs} differ by >= {ANOMALY_ACC}; "
                              "hosts characterised separately; combination withheld pending investigation")
        if len(v["hosts"]) == 2 and len(elig) == 1:
            v["notes"].append("eligible on one host only: NOT selectable as a homogeneous substrate")
        v["selectable"] = len(elig) == len(v["hosts"]) and not anomaly
        if len(v["hosts"]) == 2 and v["selectable"]:
            res = {}
            for e in ("measured", 200, 1000):
                caps = {h: capacity(bounds(hosts[h])["DECISION"], hosts[h]["measured"]["evaluations_per_generation"]
                                    if e == "measured" else e) for h in hosts}
                for L in (32, 64):
                    alloc, days = shard(L, caps)
                    res[f"L{L}|evo{e}"] = {"allocation": alloc, "days": round(days, 2), "within_14": days <= TARGET_DAYS,
                                           "within_30": days <= CEILING_DAYS,
                                           "caps_lineages_per_day": {h: round(c, 3) for h, c in caps.items()}}
            v["combined"] = res
        out["variants"][key] = v
    cands = {}
    for key, v in out["variants"].items():
        if not v["selectable"]:
            continue
        days = (v["combined"]["L64|evomeasured"]["days"] if v["combined"]
                else min(v["hosts"][h]["single_host_days"]["L64|evomeasured|DECISION"] for h in v["hosts"]))
        cands[key] = days
    out["selection"] = ("NO_ELIGIBLE_SUBSTRATE" if not cands else
                        {"variant": min(cands, key=cands.get), "L64_decision_days": cands[min(cands, key=cands.get)],
                         "basis": "shortest decision-throughput L64 time at measured evolution effort among "
                                  "variants eligible on every host measured"})
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
