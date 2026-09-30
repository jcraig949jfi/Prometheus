"""Resume Pass D of a v0 run from its committed rows (operator go-ahead
2026-09-30 after the harness stopped the run for host memory pressure).

Uses run_v0.audit_lens -- the same procedure the driver runs. Before
auditing any new lens it re-audits the last already-audited lens and
requires the stored and recomputed rows to match on every measured field
(determinism control); a mismatch aborts without writing.

Lineage caveat: dark-reserve membership is reconstructed from FOSSILS
(dark_gens at death). An ancestor still alive at the end of evolution has
unknown reserve history, so dark_ancestors on resumed rows is a lower
bound; each resumed row says so.

Usage: python -m tyche.passd_resume <run_dir> [--workers 8] [--cache 12]
"""

from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import argparse
import json
import time
from multiprocessing import Pool

from . import ecology as E
from .run_v0 import audit_lens

MEASURED = ("home_test", "home_reps", "replicated", "transfer", "null", "beats_null",
            "sig_transfer_worlds", "sensor_class", "false_gradient_worlds", "ablation",
            "needed_world_channels", "interpretation", "causality", "genome")


def jl(p):
    return [json.loads(x) for x in open(p, encoding="ascii") if x.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--cache", type=int, default=12)
    a = ap.parse_args()
    t0 = time.time()
    C = json.load(open(os.path.join(a.run, "CONFIG.json")))
    cfg = C["config"]
    specs = json.load(open(os.path.join(a.run, "WORLDS.json")))
    by = {s["id"]: s for s in specs}
    all_ids = [s["id"] for s in specs if s["role"] == "train"] + [s["id"] for s in specs if s["role"] == "heldout"]
    meta, gid = {}, {}
    for r in jl(os.path.join(a.run, "GENEALOGY.jsonl")):
        if r.get("event") == "birth" and r["id"] not in meta:
            meta[r["id"]] = dict(r, dark_gens=0)
            gid[r["id"]] = r["genome"]
    for f in jl(os.path.join(a.run, "FOSSILS.jsonl")):
        meta[f["id"]]["dark_gens"] = max(meta[f["id"]]["dark_gens"], f.get("dark_gens", 0))
    eco_ids = []
    for x in jl(os.path.join(a.run, "ADMISSIONS.jsonl")):
        if x["admitted"]:
            meta[x["id"]]["admission"] = {k: x[k] for k in ("epoch", "world", "ruler", "org", "eco_before")}
            meta[x["id"]]["admission"].update(conf_gain=x["conf_gain"], conf_z=x["conf_z"])
            eco_ids.append(x["id"])
    dpath = os.path.join(a.run, "PASS_D_AUDITS.json")
    D = json.load(open(dpath))
    done = D["admitted"]
    assert [r["id"] for r in done] == eco_ids[: len(done)], "stored audit order differs from admissions"
    todo = eco_ids[len(done):]
    print(f"audited {len(done)} / {len(eco_ids)}; resuming {len(todo)}", flush=True)
    pool = Pool(a.workers, initializer=E._worker_init, initargs=(specs, a.cache))

    # determinism control on the last stored row
    k = len(done) - 1
    ref = done[k]
    re = json.loads(json.dumps(audit_lens(pool, cfg, specs, by, gid, meta, eco_ids, all_ids, ref["id"], k)))
    diff = [f for f in MEASURED if re.get(f) != ref.get(f)]
    ctl = {"lens": ref["id"], "index": k, "fields_compared": list(MEASURED), "mismatched": diff}
    print("determinism control:", ctl, flush=True)
    if diff:
        pool.terminate()
        json.dump(ctl, open(os.path.join(a.run, "PASS_D_RESUME_CONTROL_FAILED.json"), "w"), indent=1)
        raise SystemExit("determinism control failed; nothing resumed")

    for lid in todo:
        idx = eco_ids.index(lid)
        row = audit_lens(pool, cfg, specs, by, gid, meta, eco_ids, all_ids, lid, idx)
        row["resumed"] = True
        row["dark_ancestry_source"] = "fossils_only_lower_bound"
        done.append(row)
        print(f"  {lid} home={row['home']} {row['ruler']}/{row['org']} test={row['home_test'][0]:+.3f} "
              f"z={row['home_test'][1]:.1f} rep={[round(x[0], 3) for x in row['home_reps']]} "
              f"{row['sensor_class']} caus={row['causality']['pass']} {row['interpretation']}", flush=True)
        D["admitted"] = done
        D["resume"] = {"control": ctl, "workers": a.workers, "cache": a.cache,
                       "resumed_ids": todo, "note": "harness memory stop; operator go-ahead 2026-09-30"}
        json.dump(D, open(dpath, "w"), indent=1, sort_keys=True)
    pool.close()
    pool.join()
    gens = [g for g in jl(os.path.join(a.run, "GENERATIONS.jsonl")) if "gen" in g]
    json.dump({"finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "generations": len(gens), "lenses_born": len(meta), "admitted": eco_ids,
               "truncated": None, "pass_d_resumed": todo, "resume_wall_secs": round(time.time() - t0, 1)},
              open(os.path.join(a.run, "DONE.json"), "w"), indent=1)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
