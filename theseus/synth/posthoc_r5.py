"""POST-HOC (not preregistered as an H1 test): apply ruler R5 (response mid-band share,
validated in THESEUS-23a, AUC .751 planted vs random) to the committed arms of run v0_1.
Frozen consequence of roles/Theseus/prereg/2026-10-08_ruler_check/PREREG.md: R5 is applied
to the committed rows, labelled post hoc, before any new ecology run."""
import json

import numpy as np

from . import battery as bt

REF = "v0_1_2026-09-30"


def midband(fp):
    r = np.asarray(fp)[bt.N_DESC:]
    return float(((r > 0.05) & (r < 0.9)).mean())


def auc(pos, neg):
    allv = np.concatenate([pos, neg]); ranks = np.argsort(np.argsort(allv)) + 1.0
    for v in np.unique(allv):
        m = allv == v; ranks[m] = ranks[m].mean()
    return float((ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def main():
    vals = {}
    lane_arm = {"DEEP": "D", "VERY_DEEP": "D", "DEEP_LENS": "E", "SHALLOW": "S", "G0": "G"}
    for l in open(f"theseus/entities/{REF}.jsonl", encoding="utf-8"):
        e = json.loads(l)
        if e.get("kind") == "mechanism" and e.get("viable") and e.get("lane") in lane_arm:
            vals.setdefault(lane_arm[e["lane"]], []).append(midband(e.get("behavioralFingerprint") or []) if e.get("behavioralFingerprint") else None)
    fps = {json.loads(l)["id"]: json.loads(l)["fp"] for l in open(f"theseus/fingerprints/{REF}.jsonl", encoding="utf-8")}
    vals = {}
    for l in open(f"theseus/entities/{REF}.jsonl", encoding="utf-8"):
        e = json.loads(l)
        if e.get("kind") == "mechanism" and e.get("viable") and e.get("lane") in lane_arm and e["id"] in fps:
            vals.setdefault(lane_arm[e["lane"]], []).append(midband(fps[e["id"]]))
        if e.get("origin") == "human" and e.get("viable") and e["id"] in fps:
            vals.setdefault("G0seed", []).append(midband(fps[e["id"]]))
    for l in open(f"theseus/controls/arms_{REF}.jsonl", encoding="utf-8"):
        r = json.loads(l)
        if r["viable"] and r["arm"] in ("A", "B", "C", "P", "R", "W"):
            vals.setdefault(r["arm"], []).append(midband(r["fp"]))
    rng = np.random.default_rng(5)
    out = {"ref": REF, "label": "POST-HOC", "arms": {}}
    for a, v in sorted(vals.items()):
        v = np.array(v)
        out["arms"][a] = {"n": len(v), "median": float(np.median(v)), "mean": float(v.mean())}
    for a in ("D", "E", "A", "B", "C", "P", "G0seed"):
        if a in vals and "R" in vals:
            p, q = np.array(vals[a]), np.array(vals["R"])
            bs = [auc(p[rng.integers(len(p), size=len(p))], q[rng.integers(len(q), size=len(q))]) for _ in range(1000)]
            out["arms"][a]["auc_vs_R"] = auc(p, q)
            out["arms"][a]["auc_vs_R_ci95"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    if "D" in vals:
        p = np.array(vals["D"]); q = np.concatenate([vals[a] for a in ("B", "C", "P") if a in vals])
        bs = [auc(p[rng.integers(len(p), size=len(p))], q[rng.integers(len(q), size=len(q))]) for _ in range(1000)]
        out["D_vs_oneshot_auc"] = auc(p, q)
        out["D_vs_oneshot_ci95"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    json.dump(out, open("theseus/runs/posthoc_r5_2026-10-08/RESULT.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
