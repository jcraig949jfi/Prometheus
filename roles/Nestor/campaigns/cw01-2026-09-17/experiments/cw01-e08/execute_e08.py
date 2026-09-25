"""EXECUTE cw01-e08 under the frozen contract: 4 arms x 8 lineages, durable rows, blinded assay.

Refuses to run unless the driver's view of the contract equals the committed VERDICT_CONTRACT.json
and WORLD.json carries the frozen values. Production seeds use component 'evo' (disjoint from
qualification by construction and by check). Every row carries the contract hash.

Rows (primordial.fabric row vocabulary; 'record' for TAX arms, 'control' otherwise):
  kind=lineage     one per lineage: arm, lineage, final fitness summary, generations, wall
  kind=generation  every rows.generation_every generations: fitness, sel, burden means, amputations
  kind=assay       one per representative: held64, live ticks, work, burden vector + scalar, retention,
                   genome sha256 (the assay itself received genomes only; the arm is joined here from the
                   lineage id, in the ledger, not inside the assay)
Representatives' packed genomes are preserved as a fossil (fossils/representatives.npz).
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent


def _bootstrap_lib():
    for cand in [HERE] + list(HERE.parents):
        if (cand / "lib" / "repopath.py").exists():
            sys.path.insert(0, str(cand / "lib"))
            return cand / "lib"
    raise RuntimeError("cannot locate lib/repopath.py walking up from %s" % HERE)


_bootstrap_lib()
sys.path.insert(0, str(HERE))
import contract as CT          # noqa: E402
import localrun as LR          # noqa: E402
import world_e08 as W          # noqa: E402

CFG = json.loads((HERE / "WORLD.json").read_text(encoding="utf-8"))
AID = CFG["attempt_id"]
EXP_ID = "CW01-E08-A01"


def preconditions():
    c = CT.VerdictContract.load(HERE / "VERDICT_CONTRACT.json").freeze()
    q = json.loads((HERE / "QUALIFY.json").read_text(encoding="utf-8"))
    if q["verdict"] != "QUALIFIED":
        raise CT.ContractViolation("QUALIFY.json is not QUALIFIED")
    ev, tx = CFG["evolution"], CFG["tax"]
    want = {"generations": c.get("evolution")["generations"], "g_amp": c.get("evolution")["g_amp"],
            "lambda": c.get("tax")["lambda"], "weights": c.get("tax")["weights"]}
    have = {"generations": ev["generations"], "g_amp": ev["g_amp"], "lambda": tx["lambda"], "weights": tx["weights"]}
    if want != have:
        raise CT.ContractViolation("WORLD.json %s != contract %s" % (have, want))
    if c.get("production_seed_component") in c.get("qualification_seed_components"):
        raise CT.ContractViolation("production seed component overlaps qualification")
    return c


def genome_sha(pop, cfg, spec):
    rec = W.pack(pop, cfg, spec)
    return [hashlib.sha256(rec[i].tobytes()).hexdigest()[:16] for i in range(rec.shape[0])]


def job(ctx, **kw):
    t_all = time.time()
    c = preconditions()
    spec = W.world_spec(CFG)
    ev, tx, ac = CFG["evolution"], CFG["tax"], CFG["assay"]
    every = CFG["rows"]["generation_every"]
    fossil = {"records": [], "meta": []}
    for arm in CFG["arms"]:
        status = "record" if W.is_tax(arm) else "control"
        for lineage in range(CFG["lineages_per_arm"]):
            t0 = time.time()
            gen_rows = []

            def on_gen(rec, arm=arm, lineage=lineage, status=status):
                if rec["gen"] % every == 0 or rec["gen"] == ev["generations"] - 1:
                    row = {"status": status, "kind": "generation", "arm": arm, "lineage": lineage}
                    row.update(rec)
                    gen_rows.append(row)

            res = W.evolve(CFG, spec, AID, arm, lineage, ev["generations"], lam=tx["lambda"], g_amp=ev["g_amp"],
                           seed_component=c.get("production_seed_component"), history_every=1, on_generation=on_gen)
            for row in gen_rows:
                ctx.emit(c.stamp(row))
            reps, idx = W.representatives(res["pop"], res["fit"], ac["top_k"])
            asy = W.assay(CFG, spec, reps, AID, tag="assay")          # genomes only; no arm label
            shas = genome_sha(reps, CFG, spec)
            for i in range(ac["top_k"]):
                row = {"status": status, "kind": "assay", "arm": arm, "lineage": lineage, "rep": i,
                       "genome_sha": shas[i], "train_fit": float(res["fit"][idx[i]]),
                       "held64": float(asy["held64"][i]), "held64_after_amp": float(asy["held64_after_amp"][i]),
                       "live_ticks": float(asy["live_ticks"][i]), "work": float(asy["work"][i]),
                       "scalar": float(asy["scalar"][i])}
                for cname in W.COORDS:
                    row["b_" + cname] = float(asy["burden"][cname][i])
                    row["b_amp_" + cname] = float(asy["burden_after_amp"][cname][i])
                row["rk"] = [int(x) for x in reps["rk"][i]]
                row["mk_bits"] = int(reps["mk"][i].sum())
                ctx.emit(c.stamp(row))
            fossil["records"].append(W.pack(reps, CFG, spec))
            fossil["meta"] += [{"arm": arm, "lineage": lineage, "rep": i, "sha": shas[i]} for i in range(ac["top_k"])]
            ctx.emit(c.stamp({"status": status, "kind": "lineage", "arm": arm, "lineage": lineage,
                              "generations": ev["generations"], "wall_s": round(time.time() - t0, 1),
                              "fit_max": float(res["fit"].max()), "fit_mean": float(res["fit"].mean()),
                              "scalar_mean": float(W.scalar_burden(res["burden"], CFG, spec).mean()),
                              "held64_reps_mean": float(asy["held64"].mean()),
                              "n_competent_reps": int((asy["held64"] > ac["competence_floor_held64"]).sum())}))
            print("   %-8s lineage %d  %.0f s  fit max %d  held64 reps mean %.1f  competent %d/%d  scalar %.2f"
                  % (arm, lineage, time.time() - t0, res["fit"].max(), asy["held64"].mean(),
                     (asy["held64"] > ac["competence_floor_held64"]).sum(), ac["top_k"],
                     W.scalar_burden(res["burden"], CFG, spec).mean()), flush=True)
    fdir = HERE / "fossils"
    fdir.mkdir(exist_ok=True)
    np.savez_compressed(fdir / "representatives.npz", records=np.concatenate(fossil["records"], 0),
                        meta=json.dumps(fossil["meta"]), contract=c.hash, record_nbytes=W.record_nbytes(CFG, spec))
    print("EXECUTE done in %.0f s; %d rows" % (time.time() - t_all, ctx.n))


if __name__ == "__main__":
    os.environ.setdefault("PM_LANE", "A")
    from primordial.fabric import envelope as EV
    env = EV.example(predicate_id="cw01-e08-rank-tax", experiment_class="PROBE", cohort="A")
    rows = HERE / "rows" / "cw01-e08-a01.jsonl"
    out = LR.run_job_locally(job, rows, EXP_ID, env)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    raise SystemExit(0 if out["ok"] else 1)
