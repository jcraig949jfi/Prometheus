"""AR-1 KP timing: CPU-s per search by stage (r1 / chain / scratch) from the cached pilot searches, and the production
projection for the 15 admitted R3/R4 families (7 worlds; ~17 units with <= 2 R1 families each -- the E3-KP projection
counts, no production data read).  python -m alien.ar1_timing [--root foundry/pilot_v2]"""
import argparse
import json
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
N_FAM, N_UNITS, R1_PER_UNIT = 15, 17, 2


def stats(root, out_dir):
    rows = {}
    for p in sorted(Path(out_dir).glob("AR1_W*.json")):
        d = json.loads(p.read_text())
        w = d["world"]
        sealed = json.loads((Path(root) / w / "WORLD_SEALED.json").read_text())
        rung = {f["family_id"]: f["rung"] for f in sealed["families"]}
        for k, r in d["searches"].items():
            fid, _seed, lib = k.split("|")[:3]
            stage = "r1" if rung[fid] == "R1" else ("chain" if lib != "lib=-" else "scratch")
            rows.setdefault(stage, []).append(r)
    out = {}
    for s, v in sorted(rows.items()):
        c = [r["cpu_s"] for r in v]
        cen = [r for r in v if not r["hit"]]
        out[s] = {"n": len(v), "hits": len(v) - len(cen), "mean_cpu_s": round(st.mean(c), 1), "max_cpu_s": max(c),
                  "censored_mean_cpu_s": round(st.mean(r["cpu_s"] for r in cen), 1) if cen else None,
                  "cpu_s_per_1e6_charges": round(st.mean(r["cpu_s"] / r["charges"] * 1e6 for r in v), 1)}
    return out


def projection(s):
    r1, ch, sc = s["r1"], s.get("chain", s["scratch"]), s["scratch"]
    n_r1 = N_UNITS * R1_PER_UNIT
    exp = n_r1 * 0.85 * r1["mean_cpu_s"] + N_FAM * ch["mean_cpu_s"] + N_FAM * sc["mean_cpu_s"]
    hi = n_r1 * r1["max_cpu_s"] + N_FAM * max(ch["max_cpu_s"], sc["max_cpu_s"]) * 2
    ms_exp = 3 * n_r1 * 0.85 * r1["mean_cpu_s"] + N_FAM * ch["mean_cpu_s"]
    ms_hi = 3 * n_r1 * r1["max_cpu_s"] + N_FAM * ch["max_cpu_s"]
    return {"assumptions": "15 families, 17 units x <= 2 R1 families (E3-KP projection counts); expected = 85% of the "
                           "R1 attempts run (some units acquired at the first family) x pilot mean, every chain and "
                           "scratch run at the pilot mean; bound = every search at the pilot max",
            "primary_core_h_expected": round(exp / 3600, 2), "primary_core_h_bound": round(hi / 3600, 2),
            "r1_multiseed4_extra_core_h_expected": round(ms_exp / 3600, 2),
            "r1_multiseed4_extra_core_h_bound": round(ms_hi / 3600, 2),
            "full_seed_row_core_h_expected": round(exp / 3600, 2),
            "wall_h_one_worker_primary_expected": round(exp / 3600, 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="foundry/pilot_v2")
    a = ap.parse_args()
    out_dir = HERE / "runs" / Path(a.root).name
    s = stats(a.root, out_dir)
    res = {"label": "EXPOSED DEV DATA (pilot)" if "pilot" in a.root else "PRODUCTION", "per_search": s,
           "total_search_cpu_s": round(sum(v["mean_cpu_s"] * v["n"] for v in s.values()), 1),
           "production_projection": projection(s)}
    (out_dir / "AR1_TIMING.json").write_text(json.dumps(res, indent=1, sort_keys=True))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
