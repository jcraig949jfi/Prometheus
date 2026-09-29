"""Target B: frozen BEE lens over every preserved traced-birth log, then the native-vs-lens differential.
    python -m archaeon.causal_lens.fossils_bee [--workers 12] [--graphs 12]
Order of operations (blind differential, s9): the lens pass (adapters/bee.py, frozen at 0d598efd2) runs first on each run; the native
verdict columns and the run's summary.json are read only afterwards, in `compare`.
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "archaeon/causal_lens/out/bee"
EVID = Path(r"C:\Prometheus-data\evidence\portability01_2026-09-26\bee")


def one(args):
    rid, want_graph = args
    from archaeon.causal_lens.adapters import bee as B
    t0 = time.time()
    try:
        r = B.run(rid, want_graph=want_graph, graph_limit=4000)
    except FileNotFoundError as e:
        return rid, {"error": "missing: %s" % e}
    wall = time.time() - t0
    g = r.pop("graph")
    if g is not None:
        v = g.check(); r["graph_violations"] = len(v); r["graph_violation_sample"] = v[:5]; r["graph_nodes"] = len(g.nodes)
        EVID.mkdir(parents=True, exist_ok=True)
        from archaeon.causal_lens.schema import dump
        dump(g, str(EVID / (rid + ".graph.json")))
    r["lens_wall_s"] = round(wall, 2)
    # ---- native reading, read AFTER the lens pass
    s = json.loads((B.RUNS / rid / "summary.json").read_text(encoding="utf-8"))
    r["native_summary"] = {k: s.get(k) for k in ("first_self_replication", "first_replication", "seed_lineage_share", "genetic_lineages_final",
                                                   "captures", "sr_max_depth", "sr_alive_end") if k in s}
    return rid, r


def compare(res: dict) -> dict:
    """Per-birth and per-run differential tables."""
    joint = Counter(); runs = Counter(); first = Counter(); rows = []
    for rid, r in res.items():
        if "error" in r: runs["missing"] += 1; continue
        for k, v in r["joint_lens_native"].items(): joint[k] += v
        fsr = (r["native_summary"] or {}).get("first_self_replication") or None
        nat_seeded = fsr.get("seeded") if isinstance(fsr, dict) else None
        fa = r["first_autonomous"]; lens_sp = fa["lens_spontaneous"] if fa else None
        # run-level: does the lens's first AUTONOMOUS reproduction carry inserted ancestry, vs the native `seeded` flag
        cell = ("native_sr" if fsr else "native_no_sr", "lens_auto" if fa else "lens_no_auto",
                "nat_seeded=%s" % nat_seeded, "lens_spont=%s" % lens_sp)
        first[cell] += 1
        same_birth = None
        if fa and r["first_native_sr"]:
            same_birth = fa["child"] == r["first_native_sr"]["child"]
        rows.append({"rid": rid, "init": r["init"], "init_tapes": r["init_tapes"], "births": r["births"], "lens_counts": r["lens_counts"],
                     "native_first_sr_seeded": nat_seeded, "lens_first_auto_spontaneous": lens_sp, "same_first_birth": same_birth,
                     "lens_first_auto_tick": fa["tick"] if fa else None, "native_first_sr_tick": r["first_native_sr"]["tick"] if r["first_native_sr"] else None,
                     "lens_wall_s": r["lens_wall_s"]})
        runs["ok"] += 1
    return {"runs": dict(runs), "per_birth_joint": dict(sorted(joint.items(), key=lambda kv: -kv[1])), "run_level": {" | ".join(k): v for k, v in first.items()},
            "rows": rows}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    from archaeon.causal_lens.adapters import bee as B
    wk = int(argv[argv.index("--workers") + 1]) if "--workers" in argv else 12
    ng = int(argv[argv.index("--graphs") + 1]) if "--graphs" in argv else 12
    rids = sorted(p.name[:-9] for p in B.BIRTHS.glob("*.jsonl.gz"))
    jobs = [(rid, i < ng) for i, rid in enumerate(rids)]
    res = {}; t0 = time.time()
    with ProcessPoolExecutor(wk) as ex:
        for rid, r in ex.map(one, jobs, chunksize=4): res[rid] = r
    OUT.mkdir(parents=True, exist_ok=True); EVID.mkdir(parents=True, exist_ok=True)
    (EVID / "BEE_LENS_PER_RUN.json").write_text(json.dumps(res, default=str), encoding="utf-8")
    d = compare(res); d["wall_s"] = round(time.time() - t0, 1)
    d["graph_checks"] = {rid: {k: r.get(k) for k in ("graph_violations", "graph_nodes", "graph_violation_sample")} for rid, r in res.items() if "graph_violations" in r}
    tot_rows = sum(r.get("births", 0) for r in res.values()); tot_wall = sum(r.get("lens_wall_s", 0) for r in res.values())
    d["light_mode_cost"] = {"birth_rows": tot_rows, "cpu_s": round(tot_wall, 1), "us_per_birth": round(1e6 * tot_wall / max(1, tot_rows), 2)}
    (OUT / "BEE_DIFFERENTIAL.json").write_text(json.dumps(d, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: d[k] for k in ("runs", "run_level", "light_mode_cost", "wall_s")}, indent=1))


if __name__ == "__main__":
    main()
