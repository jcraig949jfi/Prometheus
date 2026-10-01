"""W2-K: re-evaluate the C1b readings that lie near a cut, on CPU (eager), and save the PAIR arrays.

C1b rows store only (mean, lo99, hi99) per arm (c1b_run.summarise), never pair arrays, so every paired-
difference reading (B, Z, I, K_x, R) is unrecoverable from the rows. This script reruns, on the recorded C1b
held seeds (HELD_NS 0xC1B0, 64 worlds), only the arms whose readings are within ~2 SE of a cut, checks that the
pct CI reproduces the recorded triple, and writes out/pairs_<tag>.npz.

usage: python reeval_c1b.py <tag>     tag in {m2spec, m3_0a23, m3_f6b6, m2fresh}
"""
import json
import os
import pathlib
import sys
import time

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ.setdefault("OMP_NUM_THREADS", "2")
import numpy as np  # noqa: E402
import torch  # noqa: E402

torch.set_num_threads(2)
assert not torch.cuda.is_available()

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[5]
sys.path.insert(0, str(REPO))
os.chdir(REPO)
from prometheus.ananke import c1b, c1b_run  # noqa: E402

OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
SUMM = json.loads((REPO / "roles/Ananke/pte/c1b/C1B_SUMMARY.json").read_text())
SEEDS = c1b.assays.world_seeds(c1b.HELD_NS, c1b.H_WORLDS)


def go(tag):
    t0 = time.time()
    arrays, status, rec, extra = {}, {}, {}, {}
    if tag == "m2spec":
        cid = "4ab2ba014aac967e"
        ph, env, g, _ = c1b_run.load(cid)
        bat = c1b.m2_battery(ph, env)
        keep = ("normal", "normal_from1", "reset_all_nonpacket", "reset_w", "flush_inflight_iti",
                "flush_inflight", "reset_inbox")
        res = c1b.run_battery({k: bat[k] for k in keep}, g, env, SEEDS, "cpu")
        rec = SUMM["specimens"][cid]["arms"]
        n = res["normal"]["run"]
        cen = c1b.census_predicts(n, "c_inflight_sum", c1b.ticks(env)["mid"])
        extra["census_C"] = {k: cen[k] for k in ("acc", "lo99", "hi99", "perm_p", "pass")}
        # per-world census correctness, so C can be re-scored under t/BOOTT
        pred = np.stack([n.tel["c_inflight_sum"][t] for t in c1b.ticks(env)["mid"]], 1)
        c = np.where(pred == 0, 0.5, (np.sign(pred) == n.ep.y).astype(float))
        c = np.where(n.ep.scored, c, np.nan)
        arrays["census_C"] = np.nanmean(c, 1).reshape(-1, 2).mean(-1)
    elif tag in ("m3_0a23", "m3_f6b6"):
        cid = {"m3_0a23": "0a23398f20cc41a2", "m3_f6b6": "f6b623cdb23afd2c"}[tag]
        ph, env, g, _ = c1b_run.load(cid)
        bat = c1b.m3_battery(ph, env)
        keep = ("normal", "drop_window_c1", "freeze_rule")
        res = c1b.run_battery({k: bat[k] for k in keep}, g, env, SEEDS, "cpu")
        rec = SUMM["specimens"][cid]["arms"]
    elif tag == "m2fresh":
        ph, env, _, _ = c1b_run.load("4ab2ba014aac967e")
        champs = json.loads((REPO / "roles/Ananke/research/spikes/out/champions_m2.json").read_text())
        res = {}
        for k in (1, 2, 3):
            gk = np.asarray(champs[f"fresh{k}"], dtype=np.int64)
            r = c1b.run_battery({"normal": c1b.m2_battery(ph, env)["normal"]}, gk, env, SEEDS, "cpu")
            res[f"fresh{k}_normal"] = r["normal"]
            n = r["normal"]["run"]
            cen = c1b.census_predicts(n, "c_inflight_sum", c1b.ticks(env)["mid"])
            extra[f"fresh{k}_census_C"] = {kk: cen[kk] for kk in ("acc", "lo99", "hi99", "perm_p", "pass")}
            pred = np.stack([n.tel["c_inflight_sum"][t] for t in c1b.ticks(env)["mid"]], 1)
            c = np.where(pred == 0, 0.5, (np.sign(pred) == n.ep.y).astype(float))
            c = np.where(n.ep.scored, c, np.nan)
            arrays[f"fresh{k}_census_C"] = np.nanmean(c, 1).reshape(-1, 2).mean(-1)
            fr = [f for f in SUMM["fresh"] if f["replicates"].startswith("4ab2") and f["k"] == k][0]
            rec[f"fresh{k}_normal"] = fr["arms"]["normal"]
    elif tag == "m2fresh_b":
        # fresh M2 champions: the Z / B / K_w difference readings (approx rows otherwise)
        ph, env, _, _ = c1b_run.load("4ab2ba014aac967e")
        champs = json.loads((REPO / "roles/Ananke/research/spikes/out/champions_m2.json").read_text())
        res = {}
        bat = c1b.m2_battery(ph, env)
        for k in (1, 2, 3):
            gk = np.asarray(champs[f"fresh{k}"], dtype=np.int64)
            r = c1b.run_battery({a: bat[a] for a in ("normal", "normal_from1", "flush_inflight_iti",
                                                     "reset_all_nonpacket", "reset_w")}, gk, env, SEEDS, "cpu")
            fr = [f for f in SUMM["fresh"] if f["replicates"].startswith("4ab2") and f["k"] == k][0]
            for a, v in r.items():
                res[f"fresh{k}_{a}"] = v
                rec[f"fresh{k}_{a}"] = fr["arms"][a]
    elif tag == "s3_6131":
        # S3 CORRECTED_WINDOW_RECHECK of D cell 613162a3 (C1's fragile CAUSAL_SUPPORT, W2-H F10)
        import gzip
        from prometheus.ananke import envs
        from prometheus.ananke.physics import Physics
        r = [x for x in c1b_run.d_wave_cells() if x["extra"]["source_cell"].startswith("613162a3")][0]
        ph, env = Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"])
        g = np.asarray(r["extra"]["genome"], dtype=np.int64)
        bat = c1b.m3_battery(ph, env)
        res = c1b.run_battery({k: bat[k] for k in ("normal", "drop_window_c1", "drop_window_corrected")},
                              g, env, SEEDS, "cpu")
        rec = [x for x in SUMM["recheck"] if x["cell"].startswith("613162a3")][0]["arms"]
        extra["c1_controls_packet_ablation"] = r["result"]["controls"].get("packet_ablation")
    else:
        raise SystemExit(tag)
    for name, v in res.items():
        arrays[name] = v["run"].pairs
        status[name] = v["status"]
    repro = {}
    for name, v in res.items():
        m, lo, hi = c1b.ci(v["run"].pairs)
        r = rec.get(name)
        repro[name] = {"cpu": [round(m, 4), round(lo, 4), round(hi, 4)], "recorded": r,
                       "match": r is not None and [round(m, 4), round(lo, 4), round(hi, 4)] == r}
    np.savez(OUT / f"pairs_{tag}.npz", **arrays)
    meta = {"tag": tag, "status": status, "repro": repro, "extra": extra, "wall_s": time.time() - t0,
            "seeds_ns": hex(c1b.HELD_NS), "device": "cpu", "graph": False}
    (OUT / f"pairs_{tag}.json").write_text(json.dumps(meta, indent=1, default=float))
    print(json.dumps(meta, default=float))


if __name__ == "__main__":
    go(sys.argv[1])
