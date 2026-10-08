"""THESEUS v0 driver. Preregistered in roles/Theseus/prereg/2026-09-30_v0/PREREG.md.

  python -m theseus.synth.run_v0 --tag <tag> [--workers 4] [--gens 30] [--smoke]

Phases (every phase logs wall and CPU seconds):
  0  G0: compile the corpus, evaluate, build and FREEZE the calibration
  1  known-mechanism library
  2  recursive ecology (the giant ball): lanes G0 / SHALLOW / DEEP /
     VERY_DEEP / DEEP_LENS x arities 2, 3, 6; dark objects -> lens evolution
     -> admitted lenses become collision matter
  3  one-shot arms (pairs, triplets, sextuplets of G0), LLM semantic
     synthesis arm, complexity-matched random arm, controls
  4  mechanistic reproduction, replication, transfer, lens marginal value,
     rule-destroyed twins
  5  analysis (theseus.synth.analysis) -> reports
Outputs: theseus/{corpus,entities,lineages,fingerprints,collisions,tensor,
archive,dark_objects,controls,runs,reports}/ -- per-run files named by tag.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import time
from multiprocessing import Pool

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

from . import battery as bt  # noqa: E402
from . import collide as co  # noqa: E402
from . import compile_g0 as cg  # noqa: E402
from . import dark as dk  # noqa: E402
from . import ecology as ec  # noqa: E402
from . import entities as en  # noqa: E402
from . import known as kn  # noqa: E402
from . import rulers as ru  # noqa: E402
from . import substrate as sb  # noqa: E402

CONFIG = {
    "master_seed": 20260930,
    "gens": 30,
    "per_cell": 3,
    "arities": [2, 3, 6],
    "lanes": ["G0", "SHALLOW", "DEEP", "VERY_DEEP", "DEEP_LENS"],
    "deep_min_gen": en.DEEP_MIN_GEN,
    "pop_cap": ec.POP_CAP,
    "field": {"P_NEAR": ec.P_NEAR, "P_FAR": ec.P_FAR, "P_UNDER": ec.P_UNDER, "P_RAND": ec.P_RAND},
    "lens_evolutions_per_gen": 2,
    "n_oneshot_per_arity": 300,
    "n_random": 300,
    "n_weird": 60,
    "n_neutral": 40,
    "n_hidden_known": 20,
    "reproduce_top": {"D": 20, "E": 10, "R": 10, "B": 10, "C": 10, "P": 10, "A": 10},
    "lens_marginal_sample": 60,
    "battery": {"T": bt.T, "N": bt.N, "n_interventions": bt.N_INT, "fp_dim": bt.FP_DIM},
    "known_library_per_family": kn.LIB_PER_FAMILY,
    "compute_guard_wall_s_ecology": 4 * 3600,
    "law": True,
    "quality": "rep",            # QD elite quality: "rep" (-replicate distance, v0) or "r5" (response mid-band)
    "elite_grids": ["pca", "desc", "resp"],
    "dark_protect_gens": None,   # None = untried dark objects protected forever (v0)
    "elite_protect_k": None,     # None = every elite protected (v0); int = only the top-k by quality
    "seed_select": 0.0,          # 0 = v0; > 0 = coalition seed weight x exp(s * z(quality))
}

_CAL = None


def _init_worker(cald):
    global _CAL
    _CAL = ru.Cal(cald) if cald else None


def _eval_job(args):
    g, scales, tau, fp_scale, do_dark = args
    t0 = time.process_time()
    r = bt.evaluate(g, np.asarray(scales), tau, fp_scale)
    if do_dark:
        r["dark"] = dk.assess(g, r["viable"])
    r["cpu_s"] = time.process_time() - t0
    return r


def _lens_job(args):
    g, seed = args
    t0 = time.process_time()
    r = dk.evolve_lens(g, seed=seed, lens_space_seed=seed)
    r["cpu_s"] = time.process_time() - t0
    return r


def _repro_job(args):
    fp, seed = args
    return kn.reproduce(fp, _LIB, _CAL, seed=seed)


def _fp_seed_job(args):
    g, scales, seed = args
    return bt.fingerprint(g, np.asarray(scales), seed=seed)["fp"].tolist()


def _marg_job(args):
    g, lenses = args
    return dk.lens_marginal(g, lenses)


_LIB = None


def _init_repro(cald, lib):
    global _CAL, _LIB
    _CAL = ru.Cal(cald)
    _LIB = {"fam": lib["fam"], "theta": lib["theta"], "fp": np.asarray(lib["fp"])}


class Tee:
    """The program writes its own log (base role s6: never shell-redirect a background job)."""

    def __init__(self, path, stream):
        self.f = open(path, "a", encoding="utf-8")
        self.s = stream

    def write(self, x):
        self.s.write(x)
        self.f.write(x)
        self.f.flush()

    def flush(self):
        self.s.flush()
        self.f.flush()


class Clock:
    def __init__(self):
        self.rows = []
        self.t = time.time()

    def mark(self, phase, cpu_s):
        now = time.time()
        self.rows.append({"phase": phase, "wall_s": round(now - self.t, 1), "worker_cpu_s": round(cpu_s, 1)})
        self.t = now
        print(f"[{time.strftime('%H:%M:%S')}] {phase}: wall {self.rows[-1]['wall_s']}s cpu {cpu_s:.0f}s", flush=True)


def jdump(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, sort_keys=True, default=_np)


def jl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, default=_np, separators=(",", ":")) + "\n")


def _np(o):
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, tuple):
        return list(o)
    raise TypeError(type(o))


def state_of(ev, assess):
    if not ev["viable"]:
        return "PARK"
    if ev.get("dark", {}).get("dark"):
        return "DARK"
    if assess and assess["n_rulers_novel"] >= 2:
        return "NOVEL_NICHE"
    return "ALIVE"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--gens", type=int, default=CONFIG["gens"])
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--no-law", action="store_true", help="THESEUS-28: collisions without the generated k-ary law")
    ap.add_argument("--ecology-only", action="store_true", help="stop after phase 2; export ecology rows only")
    ap.add_argument("--quality", choices=["rep", "r5"], default="rep")
    ap.add_argument("--elite-grids", default="pca,desc,resp")
    ap.add_argument("--pop-cap", type=int, default=None)
    ap.add_argument("--dark-protect-gens", type=int, default=None)
    ap.add_argument("--elite-protect-k", type=int, default=None)
    ap.add_argument("--seed-select", type=float, default=0.0)
    a = ap.parse_args(argv)
    cfg = copy.deepcopy(CONFIG)
    cfg["gens"] = a.gens
    if a.no_law:
        cfg["law"] = False
    cfg["ecology_only"] = bool(a.ecology_only)
    cfg["quality"] = a.quality
    cfg["elite_grids"] = a.elite_grids.split(",")
    if a.pop_cap is not None:
        cfg["pop_cap"] = a.pop_cap
    cfg["dark_protect_gens"] = a.dark_protect_gens
    cfg["elite_protect_k"] = a.elite_protect_k
    cfg["seed_select"] = a.seed_select
    if a.smoke:
        cfg.update(gens=min(a.gens, 7), per_cell=1, n_oneshot_per_arity=12, n_random=12, n_weird=6, n_neutral=6,
                   n_hidden_known=4, reproduce_top={k: 2 for k in cfg["reproduce_top"]}, lens_marginal_sample=6)
        kn.LIB_PER_FAMILY = 3
        kn.REFINE_STEPS = 2
        cfg["known_library_per_family"] = 3
    tag = a.tag
    root = "theseus"
    rdir = f"{root}/runs/{tag}"
    for d in ("corpus", "entities", "lineages", "fingerprints", "collisions", "tensor", "archive",
              "dark_objects", "controls", "runs", "reports"):
        os.makedirs(f"{root}/{d}", exist_ok=True)
    os.makedirs(rdir, exist_ok=True)
    sys.stdout = Tee(f"{rdir}/STDOUT.txt", sys.__stdout__)
    jdump(f"{rdir}/CONFIG.json", cfg)
    rng = np.random.default_rng(cfg["master_seed"])
    clock = Clock()
    compute = {}

    # ------------------------------------------------------------------ 0
    corpus = cg.compile_corpus()
    os.makedirs(f"{root}/corpus/g0", exist_ok=True)
    jl(f"{root}/corpus/g0/{tag}.jsonl", corpus)
    g0_genomes = [c["genome"] for c in corpus]
    scales = bt.calibrate_scales(g0_genomes)
    with Pool(a.workers, initializer=_init_worker, initargs=(None,)) as pool:
        g0_ev = pool.map(_eval_job, [(g, scales.tolist(), None, None, True) for g in g0_genomes])
    pre_viable = [i for i, r in enumerate(g0_ev) if r["viable"]]
    cal = ru.build_cal([g0_ev[i]["fp"] for i in pre_viable],
                       [(g0_ev[i]["fp_seed0"], g0_ev[i]["fp_seed1"]) for i in pre_viable], scales)
    ru.save_cal(cal, f"{rdir}/CAL.json")
    for r in g0_ev:  # apply the frozen replicability gate
        rd = float(np.linalg.norm((np.asarray(r["fp_seed0"]) - np.asarray(r["fp_seed1"])) / cal.sd))
        r["viability"]["rep_dist"] = rd
        r["viability"]["replicable"] = rd < cal.tau_rep
        r["viable"] = r["viable"] and r["viability"]["replicable"]
    compute["g0"] = sum(r["cpu_s"] for r in g0_ev)
    clock.mark("0_g0_and_calibration", compute["g0"])
    cald = cal.to_json()
    fp_sd = cal.sd.tolist()

    reg = en.Registry()
    tensor = co.TensorStore(cfg["master_seed"])
    tensor.set_projection(bt.FP_DIM, cfg["master_seed"] + 3)
    archive = ru.Archive(cal)
    field = ec.Field(cal, cfg["master_seed"] + 5)
    evals = {}
    assessments = {}
    active, vitality, born_gen = set(), {}, {}
    qual = {}
    for c, r in zip(corpus, g0_ev):
        e = {"id": c["id"], "origin": "human", "kind": "concept", "executableRepresentation": c["genome"],
             "parentIds": [], "metadata": c["metadata"], "lane": "G0_SEED", "born_step": 0}
        reg.add(e)
        e["behavioralFingerprint"] = r["fp"]
        evals[e["id"]] = r
        if r["viable"]:
            assessments[e["id"]] = archive.insert(e["id"], r["fp"], quality_of(r, cfg))
            qual[e["id"]] = quality_of(r, cfg)
            active.add(e["id"])
            field.place(e["id"], r["fp"])
            born_gen[e["id"]] = 0
        e["state"] = state_of(r, assessments.get(e["id"]))
    n_g0 = sum(1 for e in reg.values() if e["origin"] == "human")

    # ------------------------------------------------------------------ 1
    with Pool(a.workers) as pool:
        lib = kn.build_library(cal, seed=cfg["master_seed"] + 11, per_family=kn.LIB_PER_FAMILY, mapper=pool.map)
    clock.mark("1_known_library", 0.0)
    jdump(f"{root}/archive/known_library_{tag}.json",
          {"fam": lib["fam"], "theta": lib["theta"], "fp": lib["fp"].tolist(), "per_family": kn.LIB_PER_FAMILY})

    # ------------------------------------------------------------------ 2
    collisions, pop_hist, lens_rows = [], [], []
    lenses = []  # (id, genome)
    dark_queue = []
    cidn = 0
    eco_cpu = 0.0
    with Pool(a.workers, initializer=_init_worker, initargs=(cald,)) as pool:
        t_eco = time.time()
        for gen in range(1, cfg["gens"] + 1):
            if time.time() - t_eco > cfg["compute_guard_wall_s_ecology"]:
                print(f"  COMPUTE GUARD: ecology stopped before gen {gen}", flush=True)
                cfg["compute_guard_tripped_at_gen"] = gen
                break
            jobs = []
            for lane in cfg["lanes"]:
                base_lane = "DEEP" if lane == "DEEP_LENS" else lane
                for k in cfg["arities"]:
                    for _ in range(cfg["per_cell"]):
                        pids, modes = ec.choose_coalition(reg, tensor, field, active, base_lane, k, rng,
                                                          lenses=[l for l, _ in lenses], need_lens=(lane == "DEEP_LENS"),
                                                          seed_quality=qual, seed_strength=cfg["seed_select"])
                        if pids is None:
                            continue
                        cidn += 1
                        cid = f"c{cidn:06d}"
                        g, rec = co.collide([reg[p] for p in pids], tensor, cid, law=cfg["law"])
                        rec.update({"lane": lane, "gen": gen, "modes": modes})
                        jobs.append((cid, pids, g, rec))
            res = pool.map(_eval_job, [(g, cal.desc_scales.tolist(), cal.tau_rep, fp_sd, True) for (_, _, g, _) in jobs])
            born = {"total": 0}
            for (cid, pids, g, rec), r in zip(jobs, res):
                eco_cpu += r["cpu_s"]
                eid = f"M{cid[1:]}"
                e = {"id": eid, "origin": "synthetic", "kind": "mechanism", "executableRepresentation": g,
                     "parentIds": pids, "metadata": {"collision": cid, "arity": len(pids)},
                     "lane": rec["lane"], "born_step": gen}
                reg.add(e)
                e["behavioralFingerprint"] = r["fp"]
                # amendment 1: lensDependencies = lenses the genome EXECUTES (lensmap rules); ancestry kept apart
                e["lensDependencies"] = sorted({r_["prov"].split("|")[-1][2:] for r_ in g["rules"]
                                                if r_["op"] == "lensmap" and "L:" in r_.get("prov", "")})
                e["metadata"]["lens_ancestry"] = sorted({p for p in pids if reg[p].get("kind") == "lens"} |
                                                        {l for p in pids for l in reg[p]["metadata"].get("lens_ancestry", [])})
                evals[eid] = r
                asmt = None
                if r["viable"]:
                    asmt = archive.insert(eid, r["fp"], quality_of(r, cfg))
                    qual[eid] = quality_of(r, cfg)
                    assessments[eid] = asmt
                    active.add(eid)
                    field.place(eid, r["fp"])
                    born_gen[eid] = gen
                    for p in pids:
                        vitality[p] = vitality.get(p, 0) + 1 + (2 if asmt["n_rulers_novel"] >= 2 else 0)
                    if r.get("dark", {}).get("dark"):
                        dark_queue.append(eid)
                e["state"] = state_of(r, asmt)
                rec.update({"child": eid, "viable": r["viable"], "state": e["state"],
                            "n_rulers_novel": asmt["n_rulers_novel"] if asmt else None})
                tensor.record(pids, eid, rec["law"], {"viable": r["viable"], "state": e["state"]})
                collisions.append(rec)
                field.after_collision(pids)
                born["total"] += 1
                born[rec["lane"]] = born.get(rec["lane"], 0) + 1
            # dark objects -> lens evolution
            todo = [d for d in dark_queue if not reg[d]["metadata"].get("lens_tried")][: cfg["lens_evolutions_per_gen"]]
            if todo:
                lres = pool.map(_lens_job, [(reg[d]["executableRepresentation"], cfg["master_seed"] + int(d[1:]) % 1000)
                                            for d in todo])
                for d, lr in zip(todo, lres):
                    reg[d]["metadata"]["lens_tried"] = True
                    eco_cpu += lr["cpu_s"]
                    row = {"dark_object": d, "gen": gen, **{k: lr.get(k) for k in
                           ("admitted", "lens_id", "resid_L0", "resid_with_lens", "drop", "null_p95_drop")}}
                    lens_rows.append(row)
                    if lr.get("admitted"):
                        lid = lr["lens_id"]
                        if lid not in reg:
                            reg.add({"id": lid, "origin": "synthetic", "kind": "lens",
                                     "executableRepresentation": lr["lens"], "parentIds": [],
                                     "metadata": {"evolved_against": d, "drop": lr["drop"],
                                                  "null_p95_drop": lr["null_p95_drop"], "format": "tyche.lens v0 genome"},
                                     "lane": "LENS", "born_step": gen, "state": "ALIVE"})
                            lenses.append((lid, lr["lens"]))
                            active.add(lid)
                            field.place(lid)
                            born_gen[lid] = gen
                        reg[d]["metadata"]["resolved_by_lens"] = lid  # measured: held-out drop > null p95
            dpg = cfg["dark_protect_gens"]
            elites = (archive.elite_ids(cfg["elite_grids"]) if cfg["elite_protect_k"] is None
                      else archive.top_elites(cfg["elite_grids"], cfg["elite_protect_k"]))
            protected = elites | {d for d in dark_queue if not reg[d]["metadata"].get("lens_tried")
                                                                 and (dpg is None or gen - born_gen.get(d, 0) < dpg)} | \
                {l for l, _ in lenses}
            fos = ec.fossilize(reg, active, vitality, protected, gen, born_gen, cap=cfg["pop_cap"])
            for i in list(vitality):
                vitality[i] *= 0.9
            field.tick(active)
            syn = [reg[i] for i in active if reg[i]["origin"] == "synthetic" and reg[i].get("kind") == "mechanism"]
            gens_ = [x["generation"] for x in syn]
            pop_hist.append({
                "gen": gen, "active": len(active), "active_human": sum(reg[i]["origin"] == "human" for i in active),
                "active_synthetic": len(syn), "lenses": len(lenses), "born": born,
                "viable_born": sum(1 for (_, _, _, rec) in jobs if rec.get("viable")), "fossilized": len(fos),
                "archive_occupancy": archive.occupancy(), "dark_queue": len(dark_queue),
                "active_generation_max": max(gens_) if gens_ else 0,
                "active_generation_mean": float(np.mean(gens_)) if gens_ else 0.0,
                "eligible": {ln: sum(en.eligible(reg, i, ln) for i in active) for ln in en.LANES},
            })
            print(f"  gen {gen}: born {born} viable {pop_hist[-1]['viable_born']} active {len(active)} "
                  f"lenses {len(lenses)} occ {archive.occupancy()} maxgen {pop_hist[-1]['active_generation_max']}",
                  flush=True)
    compute["ecology"] = eco_cpu
    clock.mark("2_ecology", eco_cpu)
    if cfg["ecology_only"]:
        export_ecology_only(root, rdir, tag, reg, evals, collisions, pop_hist, n_g0, cfg, clock, compute)
        return

    # ------------------------------------------------------------------ 3
    g0_viable = [e["id"] for e in reg.values() if e["origin"] == "human" and evals[e["id"]]["viable"]]
    arms = {}  # arm -> list of (id, genome, meta)
    for arm, k in (("P", 2), ("B", 3), ("C", 6)):
        rows = []
        seen = set()
        while len(rows) < cfg["n_oneshot_per_arity"]:
            pids = [g0_viable[i] for i in rng.choice(len(g0_viable), size=k, replace=False)]
            if tuple(pids) in seen:
                continue
            seen.add(tuple(pids))
            cidn += 1
            cid = f"o{cidn:06d}"
            g, rec = co.collide([reg[p] for p in pids], tensor, cid, law=cfg["law"])
            rows.append((f"{arm}{cid[1:]}", g, {"parents": pids, "collision": rec}))
        arms[arm] = rows
    llm_path = f"{root}/controls/llm_arm_v0/GENOMES.jsonl"
    arms["A"] = []
    llm_rejected = []
    if os.path.exists(llm_path):
        for line in open(llm_path, encoding="utf-8"):
            d = json.loads(line)
            g = d["genome"]
            for r_ in g.get("rules", []):
                r_["prov"] = "llm"
            errs = sb.validate(g)
            if errs:
                llm_rejected.append({"tid": d["tid"], "errors": errs})
                continue
            arms["A"].append((f"A-{d['tid']}", g, {"tid": d["tid"], "idea": d.get("idea")}))
    deep_ids = [c["child"] for c in collisions if c["lane"] in ("DEEP", "VERY_DEEP")]
    if not deep_ids:
        deep_ids = [c["child"] for c in collisions]
    arms["R"] = []
    for i in range(cfg["n_random"]):
        ref = reg[deep_ids[int(rng.integers(len(deep_ids)))]]["executableRepresentation"]
        cx = sb.complexity(ref)
        g = co.random_genome(rng, cx["n_rules"], cx["C"], max(1, cx["max_src"]))
        arms["R"].append((f"R-{i:04d}", g, {"matched_to_complexity": cx}))
    arms["W"] = [(f"W-{i:03d}", weird_genome(rng), {"control": "weird_random"}) for i in range(cfg["n_weird"])]
    arms["X"] = [(f"X-{i:03d}", neutral_genome(rng), {"control": "execution_neutral"}) for i in range(cfg["n_neutral"])]
    hk_rng = np.random.default_rng(cfg["master_seed"] + 99)
    arms["HK"] = []
    for i in range(cfg["n_hidden_known"]):
        fam = kn.FAMILY_NAMES[i % len(kn.FAMILY_NAMES)]
        th = kn.sample_theta(fam, hk_rng)
        g = kn.build(fam, th)
        for r_ in g["rules"]:
            r_["prov"] = "SYN"  # hidden behind synthetic naming
        arms["HK"].append((f"SYN-HK-{i:03d}", g, {"hidden_family": fam, "theta": th}))
    arm_ev = {}
    arm_cpu = 0.0
    with Pool(a.workers, initializer=_init_worker, initargs=(cald,)) as pool:
        for arm, rows in arms.items():
            res = pool.map(_eval_job, [(g, cal.desc_scales.tolist(), cal.tau_rep, fp_sd, True) for (_, g, _) in rows])
            arm_ev[arm] = res
            arm_cpu += sum(r["cpu_s"] for r in res)
    compute["arms"] = arm_cpu
    clock.mark("3_arms_and_controls", arm_cpu)

    # ------------------------------------------------------------------ 4
    eco_children = [c["child"] for c in collisions]
    armsets = {"D": [i for i in eco_children if reg[i]["lane"] in ("DEEP", "VERY_DEEP")],
               "E": [i for i in eco_children if reg[i]["lane"] == "DEEP_LENS"],
               "S": [i for i in eco_children if reg[i]["lane"] == "SHALLOW"],
               "G": [i for i in eco_children if reg[i]["lane"] == "G0"]}
    table = {}  # arm -> list of dict(id, fp, viable, genome, dark...)
    for arm, ids in armsets.items():
        table[arm] = [{"id": i, "fp": evals[i]["fp"], "viable": evals[i]["viable"], "genome": reg[i]["executableRepresentation"],
                       "viability": evals[i]["viability"], "dark": evals[i].get("dark")} for i in ids]
    for arm, rows in arms.items():
        table[arm] = [{"id": rid, "fp": r["fp"], "viable": r["viable"], "genome": g, "viability": r["viability"],
                       "dark": r.get("dark"), "meta": meta} for (rid, g, meta), r in zip(rows, arm_ev[arm])]
    table["G0"] = [{"id": i, "fp": evals[i]["fp"], "viable": evals[i]["viable"], "genome": reg[i]["executableRepresentation"],
                    "viability": evals[i]["viability"], "dark": evals[i].get("dark")}
                   for i in reg.E if reg[i]["origin"] == "human"]
    pooled = np.array([r["fp"] for arm in ("A", "B", "C", "P", "R") for r in table[arm] if r["viable"]] or
                      [np.zeros(bt.FP_DIM)])

    def top(arm, n):
        rows = [r for r in table[arm] if r["viable"]]
        if not rows:
            return []
        own = {r["id"] for r in rows}
        F = np.array([r["fp"] for r in rows])
        ref = np.vstack([pooled, np.array([r["fp"] for arm2 in ("D", "E") for r in table[arm2]
                                           if r["viable"] and r["id"] not in own] or np.zeros((0, bt.FP_DIM)))])
        s = ru.sparseness(F, ref, "euclid_z", cal)
        order = np.argsort(-s)
        return [rows[i] for i in order[:n]]

    repro_targets = []
    for arm, n in cfg["reproduce_top"].items():
        for r in top(arm, n):
            repro_targets.append((arm, r))
    for r in table["HK"]:
        repro_targets.append(("HK", r))
    libd = {"fam": lib["fam"], "theta": lib["theta"], "fp": lib["fp"].tolist()}
    t_rep = time.time()
    with Pool(a.workers, initializer=_init_repro, initargs=(cald, libd)) as pool:
        rep = pool.map(_repro_job, [(r["fp"], 7) for (_, r) in repro_targets])
    repro_rows = [{"arm": arm, "id": r["id"], **rr} for (arm, r), rr in zip(repro_targets, rep)]
    clock.mark("4a_mechanistic_reproduction", (time.time() - t_rep) * a.workers)

    # replication + transfer on reproduction targets (non-HK)
    cand = [(arm, r) for (arm, r) in repro_targets if arm != "HK"]
    with Pool(a.workers) as pool:
        fps2 = pool.map(_fp_seed_job, [(r["genome"], cal.desc_scales.tolist(), 2) for (_, r) in cand])
        fps3 = pool.map(_fp_seed_job, [(r["genome"], cal.desc_scales.tolist(), 3) for (_, r) in cand])
        twins = pool.map(_eval_job, [(rule_destroyed_twin(r["genome"]), cal.desc_scales.tolist(), cal.tau_rep, fp_sd, False)
                                     for (_, r) in cand])
        lens_list = [(l, g) for l, g in lenses]
        marg_sample = []
        for arm in ("D", "E", "R", "B"):
            vs = [r for r in table[arm] if r["viable"]]
            idx = rng.choice(len(vs), size=min(cfg["lens_marginal_sample"], len(vs)), replace=False) if vs else []
            marg_sample += [(arm, vs[i]) for i in idx]
        margs = pool.map(_marg_job, [(r["genome"], lens_list) for (_, r) in marg_sample]) if lens_list else []
    SUBSTRATE_INT = [bt.INTERVENTIONS.index(n) for n in ("scale_up", "scale_down", "substrate_quantize",
                                                           "synchronous_update", "topology_rewire", "bc_change")]
    cand_rows = []
    for (arm, r), f2, f3, tw in zip(cand, fps2, fps3, twins):
        fp = np.asarray(r["fp"])
        d2 = float(ru.dist_matrix(fp[None], np.asarray(f2)[None], "euclid_z", cal)[0, 0])
        d3 = float(ru.dist_matrix(fp[None], np.asarray(f3)[None], "euclid_z", cal)[0, 0])
        resp = fp[bt.N_DESC:]
        transfer = float(1.0 - resp[SUBSTRATE_INT].mean())
        dtw = float(ru.dist_matrix(fp[None], np.asarray(tw["fp"])[None], "euclid_z", cal)[0, 0])
        cand_rows.append({"arm": arm, "id": r["id"], "replicate_d_seed2": d2, "replicate_d_seed3": d3,
                          "replicates": bool(d2 < cal.tau_rep and d3 < cal.tau_rep), "transfer_score": transfer,
                          "twin_viable": tw["viable"], "twin_dist": dtw,
                          "complexity": sb.complexity(r["genome"]),
                          "stability": float(1.0 - (resp >= 0.999).mean())})
    marg_rows = [{"arm": arm, "id": r["id"], **m} for (arm, r), m in zip(marg_sample, margs)]
    clock.mark("4b_replication_transfer_twins_lens_marginal", 0.0)

    # promote states
    rep_by = {x["id"]: x for x in repro_rows}
    for x in cand_rows:
        if x["id"] in reg and x["replicates"]:
            e = reg[x["id"]]
            e["state"] = "REPLICATING"
            if x["transfer_score"] >= 0.7:
                e["state"] = "TRANSFER"
                if rep_by.get(x["id"], {}).get("verdict") == "NOT_REPRODUCED_YET" and e["generation"] >= en.DEEP_MIN_GEN:
                    e["state"] = "INTERPRET"

    # ------------------------------------------------------------------ 5
    from . import analysis as an
    out = an.analyse(reg=reg, evals=evals, table=table, collisions=collisions, pop_hist=pop_hist, cal=cal,
                     repro_rows=repro_rows, cand_rows=cand_rows, marg_rows=marg_rows, lens_rows=lens_rows,
                     llm_rejected=llm_rejected, n_g0=n_g0, rng=np.random.default_rng(cfg["master_seed"] + 7),
                     archive=archive)
    compute["total_worker_cpu_s_measured"] = sum(v for v in compute.values())
    out["compute"] = {"phases": clock.rows, "worker_cpu_s": compute, "workers": a.workers,
                      "note": "phase 1 and 4 worker CPU not instrumented; wall x workers is the upper bound"}
    out["config"] = cfg

    # ------------------------------------------------------------------ exports
    ents = []
    for e in reg.values():
        x = {k: e.get(k) for k in ("id", "generation", "ancestry", "origin", "kind", "parentIds", "lensDependencies",
                                    "state", "lane", "born_step", "metadata")}
        x["executableRepresentation"] = e["executableRepresentation"]
        x["genealogy"] = reg.genealogy(e["id"], n_g0)
        x["viable"] = evals.get(e["id"], {}).get("viable")
        x["dark"] = evals.get(e["id"], {}).get("dark")
        x["viability"] = evals.get(e["id"], {}).get("viability")
        ents.append(x)
    jl(f"{root}/entities/{tag}.jsonl", ents)
    jl(f"{root}/fingerprints/{tag}.jsonl",
       [{"id": i, "fp": evals[i]["fp"], "fp_seed0": evals[i]["fp_seed0"], "fp_seed1": evals[i]["fp_seed1"]} for i in evals] +
       [{"id": r["id"], "arm": arm, "fp": r["fp"]} for arm in arms for r in table[arm]])
    jl(f"{root}/lineages/{tag}.jsonl",
       [{"child": e["id"], "parent": p, "position": j, "collision": e["metadata"].get("collision")}
        for e in reg.values() for j, p in enumerate(e.get("parentIds", []))])
    jl(f"{root}/collisions/{tag}.jsonl", collisions)
    jl(f"{root}/tensor/{tag}.jsonl", [{"key": list(k), **v} for k, v in tensor.edges.items()])
    jdump(f"{root}/archive/{tag}.json", {"occupancy": archive.occupancy(),
                                         "elites": {g: {",".join(map(str, c)): v for c, v in archive.elites[g].items()}
                                                    for g in ru.GRIDS},
                                         "first": {g: {",".join(map(str, c)): v for c, v in archive.first[g].items()}
                                                   for g in ru.GRIDS}})
    dark_rows = []
    for e in reg.values():
        dv = evals.get(e["id"], {}).get("dark")
        if dv and dv.get("dark"):
            dark_rows.append({"id": e["id"], "generation": e["generation"], "lane": e.get("lane"), "state": e["state"],
                              "resid_L0": dv["resid_L0"], "resid_full": dv["resid_full"],
                              "structure_ac1": dv["structure_ac1"], "lens_tried": e["metadata"].get("lens_tried", False),
                              "resolved_by_lens": e["metadata"].get("resolved_by_lens"),
                              "genealogy": reg.genealogy(e["id"], n_g0),
                              "tyche_world_spec": {"id": f"theseus:{e['id']}", "role": "heldout", "kind": "theseus_substrate",
                                                   "family": "theseus_dark_object", "law_group": e["id"],
                                                   "d": 2 * e["executableRepresentation"]["C"] + 3,
                                                   "observe": "theseus.synth.dark.observe(theseus.synth.substrate.run(genome, seed)[0])"},
                              "genome": e["executableRepresentation"]})
    jl(f"{root}/dark_objects/{tag}.jsonl", dark_rows)
    jl(f"{root}/dark_objects/lenses_{tag}.jsonl", lens_rows)
    jl(f"{root}/controls/{tag}.jsonl", [{"arm": arm, "id": r["id"], "viable": r["viable"], "viability": r["viability"],
                                         "meta": r.get("meta")} for arm in ("R", "W", "X", "HK", "A") for r in table[arm]])
    jl(f"{rdir}/POPULATION_HISTORY.jsonl", pop_hist)
    jl(f"{rdir}/REPRODUCTION.jsonl", repro_rows)
    jl(f"{rdir}/CANDIDATES.jsonl", cand_rows)
    jl(f"{rdir}/LENS_MARGINAL.jsonl", marg_rows)
    # visual export for the strongest candidates (traces only here, to keep the tree small)
    vis = []
    for x in [x for x in cand_rows if x["id"] in reg][:20]:  # amendment 1: ecology candidates only
        if True:
            g = reg[x["id"]]["executableRepresentation"]
            tr, _ = sb.run(g, seed=0)
            np.savez_compressed(f"{rdir}/trace_{x['id']}.npz", trace=tr.astype(np.float32))
            vis.append({"id": x["id"], "trace": f"trace_{x['id']}.npz",
                        "lineage": reg[x["id"]]["ancestry"], "fp": evals[x["id"]]["fp"],
                        "residual": evals[x["id"]].get("dark"), "lens_dependencies": reg[x["id"]]["lensDependencies"],
                        "collision_ancestry": [reg[a]["metadata"].get("collision") for a in reg[x["id"]]["ancestry"]
                                               if reg[a]["origin"] == "synthetic"]})
    assert vis or not any(x["id"] in reg for x in cand_rows), "VISUAL_EXPORT empty with candidates present"
    jl(f"{rdir}/VISUAL_EXPORT.jsonl", vis)
    # amendment 1: every arm row with genome and viability, so H1 is reconstructable from committed rows
    jl(f"{root}/controls/arms_{tag}.jsonl", [{"arm": arm, "id": r["id"], "viable": r["viable"], "viability": r["viability"],
                                              "fp": r["fp"], "dark": r.get("dark"), "genome": r["genome"], "meta": r.get("meta")}
                                             for arm in sorted(table) for r in table[arm]])
    jdump(f"{rdir}/REPORT.json", out)
    with open(f"{root}/reports/{tag}.md", "w", encoding="utf-8") as f:
        f.write(an.render(out, tag))
    clock.mark("5_analysis_and_export", 0.0)
    print(json.dumps(out.get("verdicts", {}), indent=1))


def quality_of(r, cfg):
    """QD elite quality (never novelty): v0 = reproducibility; THESEUS-27 = R5."""
    if cfg.get("quality") == "r5":
        return r5_midband(r["fp"])
    return -r["viability"]["rep_dist"]


def r5_midband(fp):
    r = np.asarray(fp)[bt.N_DESC:]
    return float(((r > 0.05) & (r < 0.9)).mean())


def export_ecology_only(root, rdir, tag, reg, evals, collisions, pop_hist, n_g0, cfg, clock, compute):
    """Ecology-only export (THESEUS-28/27): entities, fingerprints, collisions, population
    history, and the R5-by-generation table the ablation preregistrations read."""
    ents = []
    for e in reg.values():
        x = {k: e.get(k) for k in ("id", "generation", "origin", "kind", "parentIds", "state", "lane", "born_step")}
        x["executableRepresentation"] = e["executableRepresentation"]
        x["genealogy"] = reg.genealogy(e["id"], n_g0)
        x["viable"] = evals.get(e["id"], {}).get("viable")
        ents.append(x)
    jl(f"{root}/entities/{tag}.jsonl", ents)
    jl(f"{root}/fingerprints/{tag}.jsonl", [{"id": i, "fp": evals[i]["fp"]} for i in evals])
    jl(f"{root}/collisions/{tag}.jsonl", collisions)
    jl(f"{rdir}/POPULATION_HISTORY.jsonl", pop_hist)
    rows = [{"id": c["child"], "lane": c["lane"], "arity": c["arity"], "gen_step": c["gen"],
             "generation": reg[c["child"]]["generation"], "r5": r5_midband(evals[c["child"]]["fp"])}
            for c in collisions if evals[c["child"]]["viable"]]
    jl(f"{rdir}/R5_ROWS.jsonl", rows)
    jdump(f"{rdir}/SUMMARY.json", {"config": cfg, "n_viable_children": len(rows), "compute": clock.rows,
                                   "worker_cpu_s": compute})


def weird_genome(rng):
    """Deliberately trivial 'novel-looking' program: high-gain coupling + wrapping."""
    C = int(rng.integers(1, 5))
    rules = []
    for _ in range(int(rng.integers(10, 15))):
        op = rng.choice(["react", "wrap", "delay", "advect", "gate"])
        r = sb.rand_rule(rng, C, op=str(op), prov="weird", arity=int(rng.integers(1, 4)))
        if r["op"] == "react":
            r["p"][0] = float(rng.choice([-1.0, 1.0]))
            r["p"][2:] = [float(rng.choice([-2.0, 2.0])) for _ in r["p"][2:]]
        if r["op"] == "wrap":
            r["p"][0] = float(rng.uniform(0.5, 0.8))
        rules.append(r)
    return {"C": C, "topo": {"kind": "rrg", "seed": int(rng.integers(1 << 16))}, "bc": "periodic",
            "init": {"kind": "random", "amp": 1.0}, "rules": rules}


def neutral_genome(rng):
    """Syntax-valid, execution-neutral: every rule is an exact no-op on this IC."""
    C = int(rng.integers(1, 4))
    menu = [
        lambda: {"op": "wrap", "src": [], "dst": int(rng.integers(C)), "p": [4.0]},
        lambda: {"op": "recall", "src": [], "dst": int(rng.integers(C)), "p": [0.0]},
        lambda: {"op": "threshold", "src": [int(rng.integers(C))], "dst": int(rng.integers(C)), "p": [0.0, 0.0]},
        lambda: {"op": "react", "src": [int(rng.integers(C))], "dst": int(rng.integers(C)), "p": [0.0, 0.5, 1.0]},
        lambda: {"op": "delay", "src": [int(rng.integers(C))], "dst": int(rng.integers(C)), "p": [2, 0.0]},
        lambda: {"op": "gate", "src": [int(rng.integers(C)), int(rng.integers(C))], "dst": int(rng.integers(C)), "p": [0.0, 0.0]},
    ]
    rules = [dict(menu[int(rng.integers(len(menu)))](), prov="neutral") for _ in range(int(rng.integers(3, 10)))]
    return {"C": C, "topo": {"kind": "ring", "seed": 0}, "bc": "periodic",
            "init": {"kind": str(rng.choice(["random", "gradient", "blocks"])), "amp": 1.0}, "rules": rules}


def rule_destroyed_twin(g):
    """Same structure, every rule's effect removed (rate/gain/coef -> 0 where the op has one)."""
    t = copy.deepcopy(g)
    for r in t["rules"]:
        op = r["op"]
        if op in ("diffuse", "remember", "replicate"):
            r["p"][0] = 0.0
        elif op in ("advect", "coarse", "delay", "gate", "threshold", "select"):
            r["p"][-1] = 0.0 if op != "select" else 0.0
        elif op in ("react", "recall", "lensmap", "drive", "conserve", "mirror", "rank"):
            r["p"][0] = 0.0
        elif op == "decay":
            r["p"][0] = 0.0
        elif op == "saturate":
            r["op"], r["src"], r["p"] = "recall", [], [0.0]
        elif op == "wrap":
            r["p"][0] = 1e6
        r["prov"] = "twin"
    return t


if __name__ == "__main__":
    main(sys.argv[1:])
