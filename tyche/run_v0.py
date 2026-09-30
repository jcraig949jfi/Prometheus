"""Tyche v0 campaign driver: Pass A (baseline) -> B (residuals) -> C (lens
evolution with residual epochs) -> D (falsification). Preregistration:
roles/Tyche/prereg/2026-09-30_v0/PREREG.md (frozen before this ran).

Usage: python -m tyche.run_v0 --out tyche/runs/v0_<tag> [--workers N]
Every record is written by the program with per-record flush.
"""

from __future__ import annotations

import os

# One BLAS thread per process. Without this, 16 workers x OpenBLAS threads
# oversubscribed 28 CPUs and generations went from 13 s to 330 s once the
# ecology reached 32 lenses (aborted attempt, PREREG_AMENDMENT_1.md).
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import argparse
import gzip
import json
import platform
import subprocess
import time
from multiprocessing import Pool

import numpy as np

from . import audits as A
from . import ecology as E
from . import lens as Lm
from . import worlds as Wm
from .organisms import ORGANISMS, RULERS

CFG = {
    "master_seed": 20260930,
    "select_seed": 1,          # input-noise seed used for selection/admission
    "rep_seeds": [101, 102],   # replication seeds (Pass D only)
    "N": 96,
    "epochs": 4,
    "gens_per_epoch": 10,
    "dark_frac": 0.15,
    "dark_age_protect": 3,
    "elite_cap": 24,
    "graft_p": 0.25,
    "admit_min_val_gain": 0.02,
    "admit_top_per_world": 5,
    "admit_z": 4.0,
    "admit_min_conf_gain": 0.01,
    "admit_per_world_epoch": 1,
    "admit_cap_total": 48,
    "sig_z": 4.0,              # Pass D significance on a test split
    "rep_z": 3.0,              # Pass D replication on each fresh seed
    "null_n": 64,              # matched random lenses per admitted lens (home case)
    "null_n_transfer": 32,
    "evolution_core_hour_cap": 2.5,  # upper bound: wall x workers (MWO-0004 R2)     # matched random lenses per transfer candidate
}


class Log:
    def __init__(self, path, gz=False):
        self.f = gzip.open(path, "at", encoding="ascii") if gz else open(path, "a", encoding="ascii")

    def w(self, rec):
        self.f.write(json.dumps(rec, sort_keys=True) + "\n")
        self.f.flush()


def case_keys(train_ids):
    return [(w, r, o, sc) for w in train_ids for r in RULERS for o in ORGANISMS for sc in E.SCOPES]


def git_receipt():
    def g(*a):
        try:
            return subprocess.run(["git", *a], capture_output=True, text=True, timeout=30).stdout.strip()
        except Exception:
            return None
    return {"head": g("rev-parse", "HEAD"), "branch": g("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": bool(g("status", "--porcelain", "--untracked-files=no")),
            "host": platform.node()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=min(24, os.cpu_count() or 4))
    ap.add_argument("--smoke", action="store_true", help="tiny run for tests; not a result")
    ap.add_argument("--pilot-epochs", type=int, default=None, help="timing pilot; not a result")
    ap.add_argument("--pilot-gens", type=int, default=None, help="timing pilot; not a result")
    a = ap.parse_args()
    cfg = dict(CFG)
    if a.smoke:
        cfg.update(N=16, epochs=2, gens_per_epoch=2, null_n=4, null_n_transfer=4)
    if a.pilot_epochs is not None:
        cfg.update(epochs=a.pilot_epochs, gens_per_epoch=a.pilot_gens, pilot=True)
    os.makedirs(a.out, exist_ok=True)
    t_start = time.time()
    specs = Wm.build_worlds(cfg["master_seed"])
    train = [s["id"] for s in specs if s["role"] == "train"]
    held = [s["id"] for s in specs if s["role"] == "heldout"]
    by = {s["id"]: s for s in specs}
    json.dump({"config": cfg, "worlds_hash": Wm.worlds_hash(specs), "receipt": git_receipt(),
               "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "workers": a.workers}, open(os.path.join(a.out, "CONFIG.json"), "w"), indent=1)
    json.dump(specs, open(os.path.join(a.out, "WORLDS.json"), "w"), indent=1)

    L_gen = Log(os.path.join(a.out, "GENEALOGY.jsonl"))
    L_ev = Log(os.path.join(a.out, "EVALS.jsonl.gz"), gz=True)
    L_g = Log(os.path.join(a.out, "GENERATIONS.jsonl"))
    L_adm = Log(os.path.join(a.out, "ADMISSIONS.jsonl"))
    L_res = Log(os.path.join(a.out, "RESIDUALS.jsonl"))
    L_fos = Log(os.path.join(a.out, "FOSSILS.jsonl"))

    rng = np.random.default_rng(cfg["master_seed"])
    pool = Pool(a.workers, initializer=E._worker_init, initargs=(specs,))

    meta = {}      # lens id -> genealogy record (in memory mirror)
    eco = []       # admitted genomes, oldest first
    eco_ids = []

    def birth(g, parents, ops, gen, epoch):
        lid = Lm.lens_id(g)
        if lid not in meta:
            rec = {"id": lid, "birth_gen": gen, "epoch": epoch, "parents": parents, "ops": ops,
                   "genome": g, "len": len(g["ins"]), "eff_len": Lm.effective_length(g),
                   "inputs": Lm.input_channels(g), "dark_gens": 0, "root": None}
            rec["root"] = meta[parents[0]]["root"] if parents else lid
            meta[lid] = rec
            L_gen.w({"event": "birth", **rec})
        return lid

    def baseline(tag, ids, splits):
        out = dict(pool.map(E._base_task, [(w, cfg["select_seed"], eco, splits) for w in ids]))
        for w in ids:
            L_res.w({"tag": tag, "world": w, "eco": list(eco_ids), **out[w]})
        return out

    # ---------------------------------------------------------------- PASS A
    print("PASS A", flush=True)
    base0 = baseline("passA_eco0", train + held, ("val", "test"))
    pop = []
    for _ in range(cfg["N"]):
        g = Lm.random_genome(rng)
        pop.append(birth(g, [], ["init"], 0, 0))
    gid = {}  # id -> genome
    for lid in pop:
        gid[lid] = meta[lid]["genome"]

    cache = {}  # (epoch, id) -> case dict

    def evaluate(ids, epoch):
        todo = [i for i in dict.fromkeys(ids) if (epoch, i) not in cache]
        if todo:
            gl = [gid[i] for i in todo]
            chunks = [(w, gl, eco) for w in train]
            res = dict(pool.map(E._eval_task, chunks))
            for j, i in enumerate(todo):
                cache[(epoch, i)] = {w: res[w][j] for w in train}
                L_ev.w({"epoch": epoch, "id": i, "cases": cache[(epoch, i)]})
        return [cache[(epoch, i)] for i in ids]

    keys = case_keys(train)

    def matrix(ids, epoch):
        cs = evaluate(ids, epoch)
        return np.array([[c[w][f"{r}|{o}|{sc}"] for (w, r, o, sc) in keys] for c in cs])

    M0 = matrix(pop, 0)
    init_best = {}
    for wi, w in enumerate(train):
        cols = [k for k, kk in enumerate(keys) if kk[0] == w and kk[3] == "all"]
        sub = M0[:, cols]
        j, c = np.unravel_index(np.argmax(sub), sub.shape)
        _, r, o, _ = keys[cols[c]]
        init_best[w] = {"id": pop[j], "ruler": r, "org": o, "val_gain": float(sub[j, c])}
    # test-split value of each world's best initial lens (baseline, frozen)
    tasks = [(w, cfg["select_seed"], gid[init_best[w]["id"]], [], ("test",), ("all",),
              (init_best[w]["org"],), (init_best[w]["ruler"],), None) for w in train]
    for w, gd in zip(train, pool.map(E._gains_task, tasks)):
        k = f"{init_best[w]['ruler']}|{init_best[w]['org']}|test|all"
        init_best[w]["test_gain"], init_best[w]["test_z"] = gd[k][0], gd[k][1]
    json.dump({"baseline_eco0": base0, "initial_population_best": init_best},
              open(os.path.join(a.out, "PASS_A_BASELINE.json"), "w"), indent=1, sort_keys=True)

    # ---------------------------------------------------------------- PASS C
    dark = {}  # id -> age in reserve
    n_dark = int(round(cfg["dark_frac"] * cfg["N"]))
    n_adm_tests = 0
    gen = 0
    truncated = None
    for epoch in range(cfg["epochs"]):
        if truncated:
            break
        print(f"EPOCH {epoch} eco={eco_ids}", flush=True)
        # PASS B: residuals frozen at epoch start (err/dis masks live in workers)
        baseline(f"epoch{epoch}_start", train, ("val",))
        for gi in range(cfg["gens_per_epoch"]):
            t0 = time.time()
            ids = list(dict.fromkeys(pop + list(dark)))
            M = matrix(ids, epoch)
            allc = [k for k, kk in enumerate(keys) if kk[3] == "all"]
            # elites: best lens per (world, ruler) on the 'all' scope
            elite = []
            for w in train:
                for r in RULERS:
                    cols = [k for k in allc if keys[k][0] == w and keys[k][1] == r]
                    sub = M[:, cols].max(1)
                    j = int(np.argmax(sub))
                    if sub[j] > 0.01:
                        elite.append((float(sub[j]), ids[j]))
            elite = [i for _, i in sorted(elite, reverse=True)]
            elite = list(dict.fromkeys(elite))[: cfg["elite_cap"]]
            # dark reserve: age-protected members, then novelty, then random
            for i in list(dark):
                dark[i] += 1
            keep = [i for i in dark if dark[i] < cfg["dark_age_protect"] and i not in elite]
            sigs = {i: Lm.signature(gid[i]) for i in ids}
            rest = [i for i in ids if i not in elite and i not in keep]
            nov = E.novelty([sigs[i] for i in rest], [sigs[i] for i in ids])
            slots = max(0, n_dark - len(keep))
            by_nov = [rest[k] for k in np.argsort(-nov)]
            n_nov = int(round(slots * 2 / 3))
            chosen = by_nov[:n_nov]
            remaining = [i for i in rest if i not in chosen]
            if remaining and slots - n_nov > 0:
                chosen += [str(x) for x in rng.choice(remaining, size=min(len(remaining), slots - n_nov), replace=False)]
            new_dark = {i: dark.get(i, 0) for i in keep + chosen}
            for i in new_dark:
                meta[i]["dark_gens"] += 1
            # offspring by epsilon-lexicase parent choice
            n_off = cfg["N"] - len(elite) - len(new_dark)
            parents = E.eps_lexicase(M, rng, 2 * max(n_off, 0))
            off = []
            for k in range(max(n_off, 0)):
                p1 = ids[parents[2 * k]]
                if rng.random() < cfg["graft_p"]:
                    p2 = ids[parents[2 * k + 1]]
                    g = Lm.graft(gid[p1], gid[p2], rng)
                    ops, par = ["graft"], [p1, p2]
                    if not Lm.validate(g):
                        g, ops, par = gid[p1], ["graft_invalid_copy"], [p1]
                else:
                    g, ops = Lm.mutate(gid[p1], rng)
                    par = [p1]
                lid = birth(g, par, ops, gen + 1, epoch)
                gid[lid] = g
                off.append(lid)
            survivors = set(elite) | set(new_dark) | set(off)
            for j, i in enumerate(ids):
                if i not in survivors:
                    row = M[j]
                    kb = int(np.argmax(row))
                    L_fos.w({"id": i, "gen": gen, "epoch": epoch, "reason": "not_selected",
                             "best_case": "|".join(keys[kb]), "best_val_gain": float(row[kb]),
                             "root": meta[i]["root"], "dark_gens": meta[i]["dark_gens"]})
            best_w = {}
            for w in train:
                cols = [k for k in allc if keys[k][0] == w]
                best_w[w] = float(M[:, cols].max())
            L_g.w({"gen": gen, "epoch": epoch, "n_eval": len(ids), "elite": len(elite),
                   "dark": len(new_dark), "offspring": len(off),
                   "mean_eff_len": float(np.mean([meta[i]["eff_len"] for i in ids])),
                   "roots_alive": len({meta[i]["root"] for i in survivors}),
                   "best_val_gain_by_world": best_w, "secs": round(time.time() - t0, 2)})
            print(f"  gen {gen} {time.time() - t0:.1f}s elite={len(elite)} dark={len(new_dark)}", flush=True)
            pop = list(dict.fromkeys(elite + off))
            dark = new_dark
            gen += 1
            used = (time.time() - t_start) * a.workers / 3600
            if used > cfg["evolution_core_hour_cap"]:
                truncated = {"gen": gen, "epoch": epoch, "core_hours_upper_bound": round(used, 3)}
                L_g.w({"TRUNCATED_BY_COMPUTE_CAP": truncated})
                print(f"  TRUNCATED {truncated}", flush=True)
                break

        # ------------------------------------------------ admission (conf split)
        ids = list(dict.fromkeys(pop + list(dark)))
        M = matrix(ids, epoch)
        admitted_now = 0
        for w in train:
            if len(eco) >= cfg["admit_cap_total"]:
                break
            cols = [k for k, kk in enumerate(keys) if kk[0] == w and kk[3] == "all"]
            sub = M[:, cols]
            best = sub.max(1)
            order = [j for j in np.argsort(-best) if best[j] >= cfg["admit_min_val_gain"]]
            order = [j for j in order if ids[j] not in eco_ids][: cfg["admit_top_per_world"]]
            n_w = 0
            for j in order:
                if n_w >= cfg["admit_per_world_epoch"] or len(eco) >= cfg["admit_cap_total"]:
                    break
                c = int(np.argmax(sub[j]))
                _, r, o, _ = keys[cols[c]]
                gd = pool.apply(E._gains_task, ((w, cfg["select_seed"], gid[ids[j]], eco, ("conf",),
                                                 ("all",), (o,), (r,), None),))
                mu, z, n = gd[f"{r}|{o}|conf|all"]
                n_adm_tests += 1
                ok = z >= cfg["admit_z"] and mu >= cfg["admit_min_conf_gain"]
                L_adm.w({"epoch": epoch, "world": w, "id": ids[j], "ruler": r, "org": o,
                         "val_gain": float(sub[j, c]), "conf_gain": mu, "conf_z": z, "n": n,
                         "admitted": bool(ok), "test_index": n_adm_tests, "eco_before": list(eco_ids)})
                if ok:
                    meta[ids[j]]["admission"] = {"epoch": epoch, "world": w, "ruler": r, "org": o,
                                                 "eco_before": list(eco_ids), "conf_gain": mu, "conf_z": z}
                    eco.append(gid[ids[j]])
                    eco_ids.append(ids[j])
                    n_w += 1
                    admitted_now += 1
        print(f"  admitted {admitted_now} (tests so far {n_adm_tests})", flush=True)
    baseline("final", train + held, ("val", "test"))

    # ---------------------------------------------------------------- PASS D
    print("PASS D", flush=True)
    cheat = A.cheat_control()
    audit_rows = []
    all_ids = train + held
    for lid in eco_ids:
        g = gid[lid]
        ad = meta[lid]["admission"]
        w, r, o, eb = ad["world"], ad["ruler"], ad["org"], [gid[i] for i in ad["eco_before"]]
        row = {"id": lid, "home": w, "ruler": r, "org": o, "genome": g, "len": len(g["ins"]),
               "eff_len": meta[lid]["eff_len"], "root": meta[lid]["root"],
               "admission": ad}
        we_x = Wm.generate(by[w], cfg["select_seed"])[0]
        row["causality"] = A.causality_audit(g, we_x)
        # home: test split + replication seeds
        tasks = [(w, s, g, eb, ("test",), ("all",), (o,), (r,), None)
                 for s in [cfg["select_seed"]] + cfg["rep_seeds"]]
        res = pool.map(E._gains_task, tasks)
        k = f"{r}|{o}|test|all"
        row["home_test"] = res[0][k]
        row["home_reps"] = [x[k] for x in res[1:]]
        replicated = (row["home_test"][1] >= cfg["sig_z"]
                      and all(x[1] >= cfg["rep_z"] for x in row["home_reps"]))
        row["replicated"] = bool(replicated)
        # transfer / twins / false gradients: every other world, every case
        tasks = [(w2, cfg["select_seed"], g, eb, ("test",), ("all",), ORGANISMS, tuple(RULERS), None)
                 for w2 in all_ids if w2 != w]
        tr = {}
        for w2, gd in zip([x for x in all_ids if x != w], pool.map(E._gains_task, tasks)):
            bestk = max(gd, key=lambda kk: gd[kk][1])
            tr[w2] = {"best_case": bestk, "gain": gd[bestk][0], "z": gd[bestk][1]}
        row["transfer"] = tr
        # matched random null (same instruction count and output width)
        nrng = np.random.default_rng([cfg["master_seed"], len(audit_rows)])
        nulls = [Lm.random_genome(nrng, n_ins=len(g["ins"]), k=len(g["out"])) for _ in range(cfg["null_n"])]
        res = pool.map(E._gains_task, [(w, cfg["select_seed"], ng, eb, ("test",), ("all",), (o,), (r,), None)
                                       for ng in nulls])
        ng = np.array([x[k][0] for x in res])
        row["null"] = {"n": len(ng), "max": float(ng.max()), "p95": float(np.percentile(ng, 95)),
                       "frac_ge_lens": float((ng >= row["home_test"][0]).mean())}
        row["beats_null"] = bool(row["home_test"][0] > row["null"]["p95"])
        # a transfer counts only if it holds on a fresh seed AND beats the
        # matched random null on that world and case (capacity patches that
        # any random nonlinear feature supplies are not transfer)
        cand = [w2 for w2 in tr if tr[w2]["z"] >= cfg["sig_z"]]
        sig = []
        for w2 in cand:
            rr, oo = tr[w2]["best_case"].split("|")[:2]
            k2 = f"{rr}|{oo}|test|all"
            x = pool.apply(E._gains_task, ((w2, cfg["rep_seeds"][0], g, eb, ("test",), ("all",),
                                             (oo,), (rr,), None),))
            tr[w2]["rep"] = x[k2]
            nres = pool.map(E._gains_task, [(w2, cfg["select_seed"], ngm, eb, ("test",), ("all",), (oo,), (rr,), None)
                                            for ngm in nulls[: cfg["null_n_transfer"]]])
            nv = np.array([y[k2][0] for y in nres])
            tr[w2]["null_p95"] = float(np.percentile(nv, 95))
            tr[w2]["null_max"] = float(nv.max())
            if x[k2][1] >= cfg["rep_z"] and tr[w2]["gain"] > tr[w2]["null_p95"]:
                sig.append(w2)
        row["sig_transfer_worlds"] = sorted(sig)
        row["sensor_class"], row["false_gradient_worlds"] = A.sensor_class(
            w, sig + ([w] if (replicated and row["beats_null"]) else []), specs)
        # causal contribution: ablate each input channel the lens reads
        abl = {}
        chans = Lm.input_channels(g)
        res = pool.map(E._gains_task, [(w, cfg["select_seed"], g, eb, ("test",), ("all",), (o,), (r,), c)
                                       for c in chans])
        d = by[w]["d"]
        for c, x in zip(chans, res):
            abl[str(c)] = {"world_channel": c % d, "gain_ablated": x[k][0]}
        row["ablation"] = abl
        base_gain = row["home_test"][0]
        needed = sorted({v["world_channel"] for v in abl.values()
                         if base_gain > 0 and (base_gain - v["gain_ablated"]) >= 0.5 * base_gain})
        row["needed_world_channels"] = needed
        if by[w]["kind"] == "planted":
            row["interpretation"] = ("PLANTED_INPUTS_RECOVERED" if needed == A.planted_channels(by[w])
                                     else "UNKNOWN")
        else:
            row["interpretation"] = "UNKNOWN"
        # lineage: dark ancestry
        anc, stack = set(), list(meta[lid]["parents"])
        while stack:
            p = stack.pop()
            if p in anc:
                continue
            anc.add(p)
            stack.extend(meta[p]["parents"])
        row["n_ancestors"] = len(anc)
        row["dark_ancestors"] = sorted(p for p in anc if meta[p]["dark_gens"] > 0)
        row["admitted_ancestors"] = sorted(p for p in anc if p in eco_ids)
        audit_rows.append(row)
        print(f"  {lid} home={w} {r}/{o} test={row['home_test'][0]:+.3f} z={row['home_test'][1]:.1f} "
              f"rep={[round(x[0], 3) for x in row['home_reps']]} {row['sensor_class']} "
              f"caus={row['causality']['pass']} {row['interpretation']}", flush=True)
        json.dump({"cheat_control": cheat, "admitted": audit_rows, "n_admission_tests": n_adm_tests},
                  open(os.path.join(a.out, "PASS_D_AUDITS.json"), "w"), indent=1, sort_keys=True)
    json.dump({"cheat_control": cheat, "admitted": audit_rows, "n_admission_tests": n_adm_tests},
              open(os.path.join(a.out, "PASS_D_AUDITS.json"), "w"), indent=1, sort_keys=True)
    pool.close()
    pool.join()
    json.dump({"finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "wall_secs": round(time.time() - t_start, 1), "generations": gen,
               "lenses_born": len(meta), "admitted": eco_ids, "truncated": truncated},
              open(os.path.join(a.out, "DONE.json"), "w"), indent=1)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
