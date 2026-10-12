"""Beta-04 close tools: COMPUTE_REPORT.json and ARTIFACT_MANIFEST.json (re-runnable; reads only committed records).

Compute: MEASURED rows sum per-search / per-shard cpu_s from result files, counting each unique search once;
REPORTED rows are the figures the leads / reviewers stated in their design docs or reports (not re-measured).
Manifest: every git-tracked file under roles/Aphrodite/beta04 with its git blob id, size and category.
Usage (from roles/Aphrodite/beta04): python close_tools.py
"""
import glob
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def _sum_searches(pattern, keys=("searches",)):
    tot, files = 0.0, 0
    for p in glob.glob(os.path.join(HERE, pattern)):
        d = json.load(open(p, encoding="utf-8"))
        files += 1
        for k in keys:
            s = d.get(k)
            if isinstance(s, dict):
                tot += sum(v.get("cpu_s", 0) or 0 for v in s.values() if isinstance(v, dict))
    return tot / 3600.0, files


def _sum_shards(pattern):
    tot, files = 0.0, 0
    for p in glob.glob(os.path.join(HERE, pattern), recursive=True):
        if os.path.basename(p) in ("E2_ANALYSIS.json", "PLAN.json", "PROJECTION.json"):
            continue
        d = json.load(open(p, encoding="utf-8"))
        if isinstance(d, dict) and isinstance(d.get("cpu_s"), (int, float)):
            tot += d["cpu_s"]
            files += 1
    return tot / 3600.0, files


def _e3r():
    p = os.path.join(HERE, "runs", "e3r_production", "E3R_STATE.json")
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding="utf-8"))
    led = d.get("ledger_s") or {}
    return sum(v for v in led.values() if isinstance(v, (int, float))) / 3600.0 if led else None


def compute_report():
    measured = {}
    measured["E2 shards (qual/kcal/atlas/run)"] = _sum_shards("runs/e2/*/**/*.json")
    measured["E2 prelaunch"] = _sum_shards("runs/E2_PRELAUNCH.json")
    measured["E3-KP production, all rows (unique searches)"] = _sum_searches("runs/kp_production/KPA1_W*.json")
    measured["E3-ID production (unique searches + enumerations)"] = _sum_searches(
        "runs/id_production/ID_W*.json", ("searches", "enumerations"))
    measured["AR-1 production (unique searches)"] = _sum_searches("alien/runs/production/AR1_W*.json")
    e3r = _e3r()
    if e3r is not None:
        measured["E3-R production (driver CPU ledger)"] = (e3r, 1)
    reported = {
        "FOUNDRY v1 pilot + build (FOUNDRY_DESIGN s pilot total)": 1.4,
        "FOUNDRY v2 repair round (FOUNDRY_DESIGN s round total)": 1.3,
        "FOUNDRY production, 12 secret worlds (FOUNDRY_DESIGN s production)": 4.4,
        "SUBSTRATE core build (W01)": 0.7,
        "SUBSTRATE E3 runner + smoke (estimate from SMOKE cost model)": 1.0,
        "SUBSTRATE E3-KP alignment + pilot timing": 1.7,
        "SUBSTRATE E3-ID build + pilot": 0.35,
        "SUBSTRATE E3-R build + pilot": 0.65,
        "SUBSTRATE E3-R A1 code + pilot": 0.75,
        "ATLAS build + calibration": 2.5,
        "ATLAS E2 driver + timing": 1.0,
        "ALIEN AR-1 build + pilot": 1.43,
        "K-AB conformance (estimate)": 0.2,
        "Red teams + independent reviews (foundry red team ~0.47; others < 0.1 each)": 0.6,
    }
    rows = [{"item": k, "core_h": round(v[0], 3), "files": v[1], "kind": "MEASURED"} for k, v in measured.items()]
    rows += [{"item": k, "core_h": v, "kind": "REPORTED"} for k, v in reported.items()]
    tot_m = sum(r["core_h"] for r in rows if r["kind"] == "MEASURED")
    tot_r = sum(r["core_h"] for r in rows if r["kind"] == "REPORTED")
    return {
        "schema": "beta04.compute.v1", "campaign": "C-015",
        "cap": "48 core-h per rolling 24 h; <= 4 workers; $0 cloud",
        "rows": rows,
        "total_measured_core_h": round(tot_m, 2),
        "total_reported_core_h": round(tot_r, 2),
        "total_core_h": round(tot_m + tot_r, 2),
        "notes": [
            "MEASURED = sum of recorded per-search/per-shard CPU seconds, each unique search counted once; process "
            "start-up and orchestration overhead not included.",
            "REPORTED = figures stated by the leads/reviewers in their docs; not independently re-measured.",
            "Everything before E3-R ran between 2026-10-10 09:27Z and 2026-10-11 01:30Z, i.e. inside one rolling 24 h "
            "window; its total is below the 48 core-h cap. E3-R starts at/after 2026-10-11 11:30Z.",
            "Cloud spend: $0. No live models.",
        ],
    }


def _category(path):
    rel = path.split("roles/Aphrodite/beta04/", 1)[-1]
    if rel.startswith("windows/") and "PREREG" in rel or rel.startswith("FREEZE_") or "RULES" in rel:
        return "prereg/freeze"
    if rel.startswith("reviews/"):
        return "review"
    if rel.startswith("windows/"):
        return "window-report"
    if "/runs/" in "/" + rel or rel.startswith("runs/") or "/production/" in rel:
        return "result/data"
    if rel.endswith(".py"):
        return "code"
    return "doc/state"


def manifest():
    root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=HERE).decode().strip()
    out = subprocess.check_output(["git", "ls-files", "-s", "--", "roles/Aphrodite/beta04"], cwd=root).decode()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root).decode().strip()
    items, counts = [], {}
    for line in out.splitlines():
        meta, path = line.split("\t", 1)
        _mode, blob, _stage = meta.split()
        cat = _category(path)
        counts[cat] = counts.get(cat, 0) + 1
        items.append({"path": path, "git_blob": blob, "category": cat})
    return {"schema": "beta04.manifest.v1", "campaign": "C-015", "head_at_generation": head,
            "n_files": len(items), "by_category": counts, "files": items}


if __name__ == "__main__":
    c = compute_report()
    json.dump(c, open(os.path.join(HERE, "COMPUTE_REPORT.json"), "w"), indent=1)
    m = manifest()
    json.dump(m, open(os.path.join(HERE, "ARTIFACT_MANIFEST.json"), "w"), indent=1)
    print(json.dumps({"total_measured": c["total_measured_core_h"], "total_reported": c["total_reported_core_h"],
                      "total": c["total_core_h"], "manifest_files": m["n_files"], "by_category": m["by_category"]}))
