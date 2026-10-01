"""W2-B rows audit: which C1 rulers are forced, degenerate or unreachable, read from the recorded rows.

Pure numpy + stdlib (no torch, no engine). Reads roles/Ananke/pte/c1_rows/cells.jsonl.gz (read-only) and
writes out/rows_audit.json. Run:  python rows_audit.py
Each check is aimed at a claim in the W2-B table (REPORT, ruler table).
"""
from __future__ import annotations

import collections
import gzip
import json
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
ROWS = ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)

DIALS_LEVELS = {  # campaign.DIALS / ENV_DIALS level counts (copied, read-only)
    "topology": 5, "n_sites": 3, "radius": 3, "k_random": 2, "rewire": 2, "state_dim": 4, "payload_width": 3,
    "channels": 3, "fanout": 4, "dest_mode": 2, "loss": 4, "loss_per_hop": 2, "lat_base": 3, "lat_hop": 2,
    "lat_jitter": 3, "dup": 2, "noise": 3, "cap": 4, "collision": 3, "decay_shift": 4, "update_mode": 2,
    "update_period": 2, "update_p": 2, "rules": 3, "prog_len": 3, "plastic_route": 2, "adapt_shift": 2,
    "wimm": 2, "setrule": 2, "mut_site": 3, "economy": 3, "d": 4, "delta": 3, "gap": 3, "block": 2}


def rows():
    return [json.loads(l) for l in gzip.open(ROWS, "rt")]


def hop(ph):
    return ph["radius"] if ph["topology"] in ("ring", "torus") else 1


def main():
    R = rows()
    out = {}
    held_rows = [r for r in R if r["kind"] in ("evolve", "transfer") and "held" in r["result"]]
    # ---- 1. zero_comm forced and COMM_DEPENDENT == SIGNAL (comm families)
    t = collections.defaultdict(lambda: collections.Counter())
    max_dev = 0.0
    for r in held_rows:
        f = r["env"]["family"]
        h = r["result"]["held"]
        zc_exact = h["zero_comm"] == 0.5
        sig = h["lo99"] > 0.55
        cd = sig and h["comm_delta_lo99"] > 0.03
        t[f]["n"] += 1
        t[f]["zc_exact_half"] += zc_exact
        t[f]["SIGNAL"] += sig
        t[f]["COMM_DEPENDENT"] += cd
        t[f]["LOCAL_ONLY"] += sig and not cd
        if zc_exact:
            dev = abs((h["lo99"] - 0.5) - h["comm_delta_lo99"])
            max_dev = max(max_dev, dev)
            t[f]["cdlo_eq_lo_minus_half(1e-9)"] += dev < 1e-9
    out["zero_comm_forced"] = {f: dict(c) for f, c in t.items()}
    out["max_abs(comm_delta_lo99-(lo99-.5))_where_zc_exact"] = max_dev
    # FLIP zero_comm: not exactly .5, but E=.5 for every program (proof in REPORT)
    fz = [r["result"]["held"]["zero_comm"] for r in held_rows if r["env"]["family"] == "FLIP"]
    out["FLIP_zero_comm"] = {"n": len(fz), "mean": float(np.mean(fz)), "min": float(np.min(fz)),
                             "max": float(np.max(fz)), "exact_half": int(sum(x == 0.5 for x in fz))}
    # ---- 2. REACH_BEYOND_HOP structure: d vs hop, global
    bh = collections.defaultdict(lambda: collections.Counter())
    for r in R:
        if r["kind"] != "evolve" or "twin" not in r["result"]:
            continue
        f = r["env"]["family"]
        ph = r["physics"]
        tw = r["result"]["twin"]
        lab = tw.get("beyond_hop", 0) >= 0.5
        key = "global" if ph["topology"] == "global" else ("d>hop" if r["env"]["d"] > hop(ph) else "d<=hop")
        bh[f][key + ":n"] += 1
        bh[f][key + ":REACH_BEYOND_HOP"] += lab
        if r["result"]["held"]["comm_delta"] < 0.02:
            bh[f][key + ":RBH_with_comm_delta<.02"] += lab
    out["reach_beyond_hop"] = {f: dict(c) for f, c in bh.items()}
    # ---- 3. CAUSAL_SUPPORT clauses on D adjudications (which clause is live)
    adj = []
    for r in R:
        if r["kind"] != "adjudicate":
            continue
        c = r["result"]["controls"]
        fam = r["env"]["family"]
        n = c["normal"]["acc"]
        perm = c["env_permutation"]["acc"]
        e = {"cell": r["cell_id"][:8], "family": fam, "normal": n, "env_perm": perm,
             "env_perm_range": [c["env_permutation"]["min"], c["env_permutation"]["max"]],
             "ok_perm": 0.40 <= perm <= 0.60}
        if fam == "HOLD":
            ma = c.get("memory_ablation", {})
            e["memory_ablation"] = ma.get("acc", ma.get("status"))
            e["live_clause_mem"] = (ma.get("status") == "RAN") and ma["acc"] <= n - 0.10
            e["zero_comm"] = c["zero_comm"].get("acc")
        else:
            e["zero_comm"] = c["zero_comm"].get("acc", c["zero_comm"].get("status"))
            e["zc_clause"] = c["zero_comm"].get("status") == "RAN" and c["zero_comm"]["acc"] <= 0.55
            e["packet_ablation"] = c["packet_ablation"].get("acc", c["packet_ablation"].get("status"))
            e["pa_clause"] = c["packet_ablation"].get("status") == "RAN" and c["packet_ablation"]["acc"] <= n - 0.10
            e["CAUSAL_SUPPORT"] = e["zc_clause"] and e["pa_clause"] and e["ok_perm"]
            e["CAUSAL_iff_pa_clause"] = e["CAUSAL_SUPPORT"] == e["pa_clause"]
        adj.append(e)
    out["adjudications"] = adj
    # ---- 4. transects: levels per transect, binary-dial transects cannot produce a candidate
    tr = collections.defaultdict(set)
    for r in R:
        e = r.get("extra") or {}
        if r["wave"] in ("B", "B2") and "transect" in e:
            tr[(r["env"]["family"], e["transect"], e["base"], e.get("track"), r["wave"])].add(e["level_index"])
    lv = collections.Counter()
    two = []
    for k, s in tr.items():
        lv[len(s)] += 1
        if len(s) < 3:
            two.append({"family": k[0], "dial": k[1], "base": k[2], "track": k[3], "wave": k[4], "levels": len(s)})
    out["transects"] = {"n": len(tr), "levels_hist": dict(lv), "lt3_levels_unreachable": two}
    bdir = ROOT / "roles/Ananke/pte/c1_rows"
    try:
        bv = json.load(open(bdir / "boundaries_verdicts.json"))
        bl = bv if isinstance(bv, list) else bv.get("verdicts", bv)
        out["boundary_dials"] = sorted({(x["family"], x["dial"], x["metric"], x["label"]) for x in bl})
    except Exception as ex:  # report, do not hide
        out["boundary_dials"] = f"unreadable: {ex!r}"
    # ---- 5. plant viability attainability per family (A0 'living' plant clause)
    pv = {}
    for f in ("RELAY", "XOR", "MAJ", "FLIP", "HOLD"):
        a = np.array([r["result"]["plant"]["acc"] for r in R if r["result"].get("plant") and r["env"]["family"] == f])
        pv[f] = {"n": int(a.size), "max": float(a.max()), "ge.75": int((a >= 0.75).sum()), "gt.55": int((a > 0.55).sum())}
    out["plant_viability"] = pv
    # ---- 6. MAJ INTEGRATION and XOR rows near gates
    maj = [r["result"]["held"] for r in held_rows if r["env"]["family"] == "MAJ"]
    out["MAJ_integration_lo99>.70"] = int(sum(h["lo99"] > 0.70 for h in maj))
    out["MAJ_acc>.70"] = int(sum(h["acc"] > 0.70 for h in maj))
    xor = [r["result"]["held"] for r in held_rows if r["env"]["family"] == "XOR"]
    out["XOR_held_max_acc"] = float(max(h["acc"] for h in xor))
    out["XOR_held_max_lo99"] = float(max(h["lo99"] for h in xor))
    # ---- 7. size-free (wave E) physics: is the law lattice-local?
    E = [r for r in R if r["wave"] == "E" and r["kind"] == "transfer"]
    out["waveE"] = [{"cell": r["cell_id"][:8], "src": (r["extra"] or {}).get("source_cell", "")[:8],
                     "topology": r["physics"]["topology"], "n_sites": r["physics"]["n_sites"],
                     "radius": r["physics"]["radius"], "d": r["env"]["d"], "family": r["env"]["family"],
                     "acc": r["result"]["held"]["acc"], "lo99": r["result"]["held"]["lo99"]} for r in E]
    # ---- 8. cross-family transfers (wave C): RELAY -> MAJ is embedded
    C = [r for r in R if r["wave"] == "C" and r["kind"] == "transfer"]
    out["waveC_transfer_signal"] = [{"src_family": (r["extra"] or {}).get("source_family"), "family": r["env"]["family"],
                                     "variant": bool((r["extra"] or {}).get("variant")),
                                     "acc": r["result"]["held"]["acc"], "lo99": r["result"]["held"]["lo99"]}
                                    for r in C if r["result"]["held"]["lo99"] > 0.55]
    (OUT / "rows_audit.json").write_text(json.dumps(out, indent=1, default=str))
    return out


if __name__ == "__main__":
    o = main()
    print(json.dumps({k: v for k, v in o.items() if k not in ("adjudications", "waveE", "transects")}, indent=1, default=str)[:6000])
    print("ADJ")
    for e in o["adjudications"]:
        print(e)
    print("TRANSECTS", o["transects"]["n"], o["transects"]["levels_hist"])
    for x in o["transects"]["lt3_levels_unreachable"]:
        print("  ", x)
    print("WAVE E")
    for x in o["waveE"]:
        print("  ", x)
