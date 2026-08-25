"""Read-only. Rung R4 for the FORGE population.

G0 (2026-08-25) established that `forge/tester.py:run_ablation` already ran during the
2026-04 rebuild and wrote its results into `forge/verdicts/*_verdict.json`. This mines
that existing ledger. It measures nothing new; it reads what was measured in April.

Population: every `forge/verdicts/*_verdict.json` carrying an `ablation` block.
Ablation protocol (theirs, not ours): each called primitive is stubbed to `return None`,
the battery is re-run at seed=42, n_per_category=2, and `delta = baseline - ablated`.
`load_bearing` is their own flag, |delta| >= min_ablation_impact (0.20, pre-committed).

Repo-relative by design (feedback_paths). Run from the Prometheus root.
"""
import json
import glob
import os
import collections
import statistics

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
VERDICTS = os.path.join(ROOT, "forge", "verdicts", "*_verdict.json")

rows = []                                  # (tool_id, primitive, delta, load_bearing)
per_tool = {}                              # tool_id -> dict
errors = []

for path in sorted(glob.glob(VERDICTS)):
    d = json.load(open(path, encoding="utf-8"))
    abl = d.get("ablation")
    if abl is None:
        continue
    tid = d.get("tool_id", os.path.basename(path))
    per_tool[tid] = {
        "verdict": d.get("verdict"),
        "score": d.get("overall_score"),
        "n_prims": len(abl),
        "deltas": [],
    }
    for prim, rec in abl.items():
        if rec.get("delta") is None:
            errors.append((tid, prim, rec.get("error", "")[:60]))
            continue
        rows.append((tid, prim, float(rec["delta"]), bool(rec.get("load_bearing"))))
        per_tool[tid]["deltas"].append(float(rec["delta"]))

print("POPULATION: %d verdict files with an ablation block, %d tools, %d primitive "
      "ablations, %d errors" % (len(per_tool), len(per_tool), len(rows), len(errors)))
print()

# ---- 1. The headline: is any primitive load-bearing? ------------------------
lb = [r for r in rows if r[3]]
nonzero = [r for r in rows if abs(r[2]) > 1e-12]
positive = [r for r in rows if r[2] > 1e-12]     # removing it HURT  -> it helped
negative = [r for r in rows if r[2] < -1e-12]    # removing it HELPED -> it hurt

print("--- R4: load-bearingness across ALL ablations ---")
print("  flagged load_bearing (|delta| >= 0.20) : %d / %d  (%.2f%%)"
      % (len(lb), len(rows), 100.0 * len(lb) / max(1, len(rows))))
print("  delta exactly 0.000 (no effect at all) : %d / %d  (%.2f%%)"
      % (len(rows) - len(nonzero), len(rows),
         100.0 * (len(rows) - len(nonzero)) / max(1, len(rows))))
print("  delta > 0 (primitive HELPED the tool)  : %d  (%.2f%%)"
      % (len(positive), 100.0 * len(positive) / max(1, len(rows))))
print("  delta < 0 (primitive HURT the tool)    : %d  (%.2f%%)"
      % (len(negative), 100.0 * len(negative) / max(1, len(rows))))
if nonzero:
    mags = sorted(abs(r[2]) for r in nonzero)
    print("  |delta| among nonzero: median %.4f  p90 %.4f  max %.4f"
          % (statistics.median(mags), mags[int(0.9 * (len(mags) - 1))], mags[-1]))
print()

# ---- 2. Same, restricted to tools that actually cleared the battery --------
passing = {t for t, v in per_tool.items() if v["verdict"] == "PASS"}
prows = [r for r in rows if r[0] in passing]
print("--- R4 restricted to tools with verdict PASS (%d tools) ---" % len(passing))
if prows:
    plb = [r for r in prows if r[3]]
    pz = [r for r in prows if abs(r[2]) <= 1e-12]
    print("  %d ablations; load_bearing %d (%.1f%%); zero-delta %d (%.1f%%)"
          % (len(prows), len(plb), 100.0 * len(plb) / len(prows),
             len(pz), 100.0 * len(pz) / len(prows)))
    for tid in sorted(passing):
        v = per_tool[tid]
        ds = v["deltas"]
        print("   %-38s score=%s  prims=%d  max|d|=%.4f  nonzero=%d"
              % (tid, v["score"], v["n_prims"],
                 max([abs(x) for x in ds], default=0.0),
                 sum(1 for x in ds if abs(x) > 1e-12)))
else:
    print("  none")
print()

# ---- 3. Per-primitive aggregation: which primitives ever matter? -----------
by_prim = collections.defaultdict(list)
for _tid, prim, delta, _lb in rows:
    by_prim[prim].append(delta)

never = [p for p, ds in by_prim.items() if all(abs(d) <= 1e-12 for d in ds)]
ever = [p for p, ds in by_prim.items() if any(abs(d) > 1e-12 for d in ds)]
print("--- per-primitive: %d distinct primitives ablated ---" % len(by_prim))
print("  primitives whose removal NEVER changed any score : %d (%.1f%%)"
      % (len(never), 100.0 * len(never) / max(1, len(by_prim))))
print("  primitives that mattered at least once           : %d" % len(ever))
print()
print("  top 15 primitives by max |delta|:")
ranked = sorted(by_prim.items(), key=lambda kv: -max(abs(d) for d in kv[1]))
for prim, ds in ranked[:15]:
    print("    %-34s n=%-4d max|d|=%.4f  mean d=%+.4f"
          % (prim[:34], len(ds), max(abs(d) for d in ds),
             sum(ds) / len(ds)))
print()

# ---- 4. Why FAIL_ABLATION never fired -------------------------------------
vc = collections.Counter(v["verdict"] for v in per_tool.values())
print("--- verdict distribution over the ablated population ---")
for k, n in vc.most_common():
    print("    %-16s %d" % (k, n))
print()
print("  NOTE: tester.py only reaches the ablation branch when battery AND seed")
print("  gates already passed. Tools failing the battery are never ablation-judged,")
print("  so FAIL_ABLATION can only fire on the handful that got that far.")
