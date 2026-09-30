"""Tyche v1 driver: can a lens lineage acquire a useful sense whose
necessary precursors have no individually measurable utility?

Arms (same worlds, same initial population per evolutionary seed, same
per-world evaluation budget in UNITS = new lens evaluations + pair
evaluations; an arm runs until its budget is spent):
  V0    v0 selection: eps-lexicase on individual marginal gain, elites,
        v0 dark reserve (14 slots, novelty/random/age), single-lens
        admission only
  DE    dark ecology: v0 selection PLUS a utility-free reserve (48 slots:
        age protection, output-signature novelty with a lineage-novelty
        bonus, random persistence, neutral drift) PLUS pair evaluation
        O(L_a(X), L_b(X)) mostly among reserve lenses PLUS fused-sensor
        admission PLUS delayed credit (precursors of an admitted fused
        sensor are vindicated: protected in the reserve, favoured by drift)
  DENR  preservation ablation: pair evaluation among the utility-selected
        population only; no reserve of any kind

Usage: python -m tyche.v1.run_v1 --arm DE --seed 1 --out DIR [--workers N]
       python -m tyche.v1.run_v1 --pass-a-only --seed 1 --out DIR
"""

from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import argparse
import itertools
import json
import platform
import subprocess
import time
from multiprocessing import Pool

import numpy as np

from .. import audits as A
from .. import ecology as E0
from .. import lens as Lm
from ..organisms import ORGANISMS
from . import eco_v1 as E1
from .eco_v1 import RULERS
from . import worlds_v1 as W1

CFG = {
    "world_seed": 20261001, "select_seed": 1, "rep_seeds": [101, 102],
    "N": 96, "gens_per_epoch": 10, "budget_units": 6000,
    "graft_p": 0.25, "v0_dark": 14, "v0_dark_age": 3, "elite_cap": 24,
    "reserve_size": 48, "reserve_age": 5, "reserve_random_frac": 1 / 3,
    "lineage_bonus": 0.1, "drift_per_gen": 12, "credit_weight": 3.0, "credit_protect_gens": 10,
    "pairs_per_world": 60, "pair_mix": {"rr": 0.5, "rp": 0.3, "pp": 0.2},
    "admit_min_val_gain": 0.02, "admit_top": 5, "admit_z": 4.0, "admit_min_conf_gain": 0.01,
    "sig_z": 4.0, "rep_z": 3.0, "null_n": 64, "null_n_transfer": 32,
    "precursor_max_gain": 0.01, "gate_min_test_gain": 0.10,
}


class Log:
    def __init__(self, path):
        self.f = open(path, "a", encoding="ascii")

    def w(self, rec):
        self.f.write(json.dumps(rec, sort_keys=True) + "\n")
        self.f.flush()


def receipt():
    def g(*a):
        try:
            return subprocess.run(["git", *a], capture_output=True, text=True, timeout=30).stdout.strip()
        except Exception:
            return None
    return {"head": g("rev-parse", "HEAD"), "branch": g("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": bool(g("status", "--porcelain", "--untracked-files=no")), "host": platform.node()}


class Run:
    def __init__(self, arm, seed, out, workers, cfg):
        self.arm, self.seed, self.out, self.cfg = arm, seed, out, cfg
        os.makedirs(out, exist_ok=True)
        self.specs = W1.build_worlds_v1(cfg["world_seed"])
        self.by = {s["id"]: s for s in self.specs}
        self.train = [s["id"] for s in self.specs if s["role"] == "train"]
        self.held = [s["id"] for s in self.specs if s["role"] == "heldout"]
        self.pool = Pool(workers, initializer=E1._init, initargs=(self.specs,))
        self.rng = np.random.default_rng([cfg["world_seed"], seed])
        self.gid, self.meta = {}, {}
        self.eco = {w: [] for w in self.train}        # per-world admitted genomes
        self.eco_ids = {w: [] for w in self.train}
        self.cache = {}                                # (epoch, id) -> {world: {case: gain}}
        self.best_ind = {}                             # id -> {world: max individual val gain ever}
        self.units = 0
        self.credit = {}                               # id -> gen vindicated
        self.L = {k: Log(os.path.join(out, f"{k}.jsonl")) for k in
                  ("GENEALOGY", "EVALS", "GENERATIONS", "ADMISSIONS", "DEFICITS", "PAIRS", "CREDIT", "RESERVE")}
        json.dump({"arm": arm, "seed": seed, "config": cfg, "worlds_hash": W1.worlds_hash(self.specs),
                   "receipt": receipt(), "workers": workers,
                   "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
                  open(os.path.join(out, "CONFIG.json"), "w"), indent=1)
        json.dump(self.specs, open(os.path.join(out, "WORLDS.json"), "w"), indent=1)

    # ------------------------------------------------------------ registry
    def birth(self, g, parents, ops, gen, kmax=Lm.KMAX):
        lid = Lm.lens_id(g)
        if lid not in self.meta:
            root = self.meta[parents[0]]["root"] if parents else lid
            self.meta[lid] = {"id": lid, "birth_gen": gen, "parents": parents, "ops": ops, "root": root,
                              "len": len(g["ins"]), "eff_len": Lm.effective_length(g),
                              "inputs": Lm.input_channels(g), "kout": len(g["out"])}
            self.gid[lid] = g
            self.L["GENEALOGY"].w({"event": "birth", **self.meta[lid], "genome": g})
        return lid

    # ------------------------------------------------------------ evaluation
    def evaluate(self, ids, epoch):
        todo = [i for i in dict.fromkeys(ids) if (epoch, i) not in self.cache]
        if todo:
            gl = [self.gid[i] for i in todo]
            res = dict(self.pool.map(E1.task_lenses, [(w, gl, self.eco[w]) for w in self.train]))
            for j, i in enumerate(todo):
                c = {w: res[w][j] for w in self.train}
                self.cache[(epoch, i)] = c
                b = self.best_ind.setdefault(i, {})
                for w in self.train:
                    b[w] = max(b.get(w, -1.0), max(c[w].values()))
                self.L["EVALS"].w({"epoch": epoch, "id": i, "cases": c})
            self.units += len(todo)
        return [self.cache[(epoch, i)] for i in ids]

    def keys(self):
        return [(w, r, o) for w in self.train for r in RULERS for o in ORGANISMS]

    def matrix(self, ids, epoch):
        cs = self.evaluate(ids, epoch)
        return np.array([[c[w][f"{r}|{o}"] for (w, r, o) in self.keys()] for c in cs])

    def deficits(self, tag, worlds, split):
        tasks = []
        for w in worlds:
            s = self.by[w]
            orc = W1.oracle(self.by[s["twin_of"]]) if s.get("twin_of") else W1.oracle(s)
            tasks.append((w, self.cfg["select_seed"], self.eco.get(w, []), orc, split))
        for w, d in self.pool.map(E1.task_deficit, tasks):
            self.L["DEFICITS"].w({"tag": tag, "world": w, "split": split, "eco": self.eco_ids.get(w, []), **d})

    # ------------------------------------------------------------ pass A
    def pass_a(self, pair_floor=False):
        cfg = self.cfg
        self.deficits("eco0", self.train + self.held, "val")
        self.deficits("eco0", self.train + self.held, "test")
        pop = [self.birth(Lm.random_genome(self.rng), [], ["init"], 0) for _ in range(cfg["N"])]
        M = self.matrix(pop, 0)
        ks = self.keys()
        out = {"initial_ids": pop, "single_best": {}, "pair_floor": {}}
        for w in self.train:
            cols = [k for k, kk in enumerate(ks) if kk[0] == w]
            j, c = np.unravel_index(np.argmax(M[:, cols]), (len(pop), len(cols)))
            _, r, o = ks[cols[c]]
            gd = self.pool.apply(E1.task_gains, ((w, cfg["select_seed"], self.gid[pop[j]], [], ("test",), (o,), (r,), None),))
            out["single_best"][w] = {"id": pop[j], "case": f"{r}|{o}", "val": float(M[j, cols[c]]),
                                     "test": gd[f"{r}|{o}|test"][0], "test_z": gd[f"{r}|{o}|test"][1]}
        # brute-force floor: EVERY pair of initial lenses on every Z world
        pairs = list(itertools.combinations(pop, 2))
        for w in ([x for x in self.train if self.by[x]["cls"] == "Z"] if pair_floor else []):
            chunks = [pairs[i:i + 200] for i in range(0, len(pairs), 200)]
            res = self.pool.map(E1.task_pairs, [(w, [(self.gid[a], self.gid[b]) for a, b in ch], []) for ch in chunks])
            best, arg = -1.0, None
            for ch, (_, rr) in zip(chunks, res):
                for (a, b), cs in zip(ch, rr):
                    v = max(cs.values())
                    if v > best:
                        best, arg = v, (a, b, max(cs, key=cs.get))
            out["pair_floor"][w] = {"n_pairs": len(pairs), "best_val_joint": best, "pair": arg[:2], "case": arg[2]}
        json.dump(out, open(os.path.join(self.out, "PASS_A.json"), "w"), indent=1, sort_keys=True)
        return pop

    # ------------------------------------------------------------ reserve
    def reserve_v0(self, dark, ids, elite):
        for i in list(dark):
            dark[i] += 1
        keep = [i for i in dark if dark[i] < self.cfg["v0_dark_age"] and i not in elite]
        sig = {i: Lm.signature(self.gid[i]) for i in ids}
        rest = [i for i in ids if i not in elite and i not in keep]
        nov = E0.novelty([sig[i] for i in rest], [sig[i] for i in ids])
        slots = max(0, self.cfg["v0_dark"] - len(keep))
        n_nov = int(round(slots * 2 / 3))
        chosen = [rest[k] for k in np.argsort(-nov)][:n_nov]
        remaining = [i for i in rest if i not in chosen]
        if remaining and slots - n_nov > 0:
            chosen += [str(x) for x in self.rng.choice(remaining, size=min(len(remaining), slots - n_nov), replace=False)]
        return {i: dark.get(i, 0) for i in keep + chosen}

    def reserve_de(self, res, ids, elite, gen):
        cfg = self.cfg
        for i in list(res):
            res[i] += 1
        protected = [i for i in res if res[i] < cfg["reserve_age"]]
        protected += [i for i, g0 in self.credit.items() if gen - g0 < cfg["credit_protect_gens"] and i in self.gid]
        protected = list(dict.fromkeys(protected))[: cfg["reserve_size"]]
        cand = [i for i in dict.fromkeys(ids + list(res)) if i not in protected and i not in elite]
        slots = cfg["reserve_size"] - len(protected)
        chosen = []
        if cand and slots > 0:
            pool_sig = [Lm.signature(self.gid[i]) for i in dict.fromkeys(ids + list(res))]
            nov = E0.novelty([Lm.signature(self.gid[i]) for i in cand], pool_sig)
            roots = {self.meta[i]["root"] for i in protected}
            score = nov + cfg["lineage_bonus"] * np.array([self.meta[i]["root"] not in roots for i in cand])
            n_rand = int(round(slots * cfg["reserve_random_frac"]))
            chosen = [cand[k] for k in np.argsort(-score)][: slots - n_rand]
            left = [i for i in cand if i not in chosen]
            if left and n_rand:
                chosen += [str(x) for x in self.rng.choice(left, size=min(len(left), n_rand), replace=False)]
        return {i: res.get(i, 0) for i in protected + chosen}

    def drift(self, res, gen):
        """Neutral drift: reserve members replaced by their own mutants with
        no utility check; vindicated lineages are favoured."""
        ids = list(res)
        if not ids:
            return res
        w = np.array([self.cfg["credit_weight"] if i in self.credit else 1.0 for i in ids])
        pick = self.rng.choice(len(ids), size=min(self.cfg["drift_per_gen"], len(ids)), replace=False, p=w / w.sum())
        for k in pick:
            p = ids[k]
            g, ops = Lm.mutate(self.gid[p], self.rng)
            c = self.birth(g, [p], ["drift"] + ops, gen)
            if c != p and p not in self.credit:
                res.pop(p, None)
            res[c] = 0
            if p in self.credit:
                self.credit.setdefault(c, self.credit[p])
        return res

    # ------------------------------------------------------------ pairs
    def pair_step(self, pop, res, epoch, gen):
        cfg = self.cfg
        n = cfg["pairs_per_world"]
        R, P = list(res), list(dict.fromkeys(pop))
        cands = []
        for w in self.train:
            pairs = set()
            if self.arm == "DE" and R:
                mix = cfg["pair_mix"]
                spec = [("rr", R, R), ("rp", R, P), ("pp", P, P)]
                for tag, A_, B_ in spec:
                    k = int(round(n * mix[tag]))
                    for _ in range(4 * k):
                        if len([p for p in pairs if p[2] == tag]) >= k:
                            break
                        a, b = str(self.rng.choice(A_)), str(self.rng.choice(B_))
                        if a != b:
                            pairs.add((min(a, b), max(a, b), tag))
            else:
                for _ in range(4 * n):
                    if len(pairs) >= n:
                        break
                    a, b = str(self.rng.choice(P)), str(self.rng.choice(P))
                    if a != b:
                        pairs.add((min(a, b), max(a, b), "pp"))
            pairs = sorted(pairs)
            _, rr = self.pool.apply(E1.task_pairs, ((w, [(self.gid[a], self.gid[b]) for a, b, _ in pairs], self.eco[w]),))
            self.units += len(pairs) / len(self.train)  # units are per world; pairs are per world
            for (a, b, tag), cs in zip(pairs, rr):
                best = max(cs, key=cs.get)
                ga = self.cache[(epoch, a)][w][best] if (epoch, a) in self.cache else None
                gb = self.cache[(epoch, b)][w][best] if (epoch, b) in self.cache else None
                if cs[best] >= cfg["admit_min_val_gain"]:
                    rec = {"gen": gen, "epoch": epoch, "world": w, "a": a, "b": b, "mix": tag, "case": best,
                           "joint_val": cs[best], "a_val": ga, "b_val": gb,
                           "synergy": cs[best] - max(ga or 0.0, gb or 0.0)}
                    self.L["PAIRS"].w(rec)
                    cands.append(rec)
        return cands

    # ------------------------------------------------------------ admission
    def admit(self, epoch, ids, M, pair_cands):
        cfg = self.cfg
        ks = self.keys()
        n_adm = 0
        for w in self.train:
            cols = [k for k, kk in enumerate(ks) if kk[0] == w]
            best = M[:, cols].max(1)
            opts = []
            for j in np.argsort(-best)[: cfg["admit_top"]]:
                if best[j] >= cfg["admit_min_val_gain"] and ids[j] not in self.eco_ids[w]:
                    _, r, o = ks[cols[int(np.argmax(M[j, cols]))]]
                    opts.append((float(best[j]), "single", ids[j], None, r, o))
            pc = sorted([p for p in pair_cands if p["world"] == w], key=lambda p: -p["joint_val"])
            seen = set()
            for p in pc:
                if (p["a"], p["b"]) in seen:
                    continue
                seen.add((p["a"], p["b"]))
                r, o = p["case"].split("|")
                opts.append((p["joint_val"], "pair", p["a"], p["b"], r, o))
                if len(seen) >= cfg["admit_top"]:
                    break
            for val, kind, a, b, r, o in sorted(opts, key=lambda x: -x[0]):
                g = self.gid[a] if kind == "single" else Lm.fuse(self.gid[a], self.gid[b])
                mu, z, n = self.pool.apply(E1.task_gains, ((w, cfg["select_seed"], g, self.eco[w], ("conf",),
                                                            (o,), (r,), None),))[f"{r}|{o}|conf"]
                ok = z >= cfg["admit_z"] and mu >= cfg["admit_min_conf_gain"]
                lid = a if kind == "single" else self.birth(g, [a, b], ["fuse"], -1)
                self.L["ADMISSIONS"].w({"epoch": epoch, "world": w, "kind": kind, "id": lid, "a": a, "b": b,
                                        "ruler": r, "org": o, "val": val, "conf_gain": mu, "conf_z": z, "n": n,
                                        "admitted": bool(ok), "eco_before": list(self.eco_ids[w])})
                if ok:
                    self.meta[lid]["admission"] = {"epoch": epoch, "world": w, "kind": kind, "a": a, "b": b,
                                                   "ruler": r, "org": o, "eco_before": list(self.eco_ids[w]),
                                                   "conf_gain": mu, "conf_z": z}
                    self.eco[w].append(g)
                    self.eco_ids[w].append(lid)
                    n_adm += 1
                    if kind == "pair" and self.arm == "DE":
                        for p in (a, b):
                            self.credit[p] = epoch
                            self.L["CREDIT"].w({"epoch": epoch, "vindicated": p, "by": lid, "world": w})
                    break
        return n_adm

    # ------------------------------------------------------------ main loop
    def evolve(self, pop):
        cfg = self.cfg
        dark, res = {}, {}
        gen, epoch = 0, 0
        while self.units < cfg["budget_units"]:
            for _ in range(cfg["gens_per_epoch"]):
                if self.units >= cfg["budget_units"]:
                    break
                t0 = time.time()
                ids = list(dict.fromkeys(pop + list(dark) + list(res)))
                M = self.matrix(ids, epoch)
                ks = self.keys()
                elite = []
                for w in self.train:
                    for r in RULERS:
                        cols = [k for k, kk in enumerate(ks) if kk[0] == w and kk[1] == r]
                        sub = M[:, cols].max(1)
                        j = int(np.argmax(sub))
                        if sub[j] > 0.01:
                            elite.append((float(sub[j]), ids[j]))
                elite = list(dict.fromkeys(i for _, i in sorted(elite, reverse=True)))[: cfg["elite_cap"]]
                if self.arm == "V0":
                    dark = self.reserve_v0(dark, ids, elite)
                elif self.arm == "DE":
                    res = self.reserve_de(res, ids, elite, gen)
                    self.L["RESERVE"].w({"gen": gen, "members": sorted(res)})
                n_off = cfg["N"] - len(elite) - len(dark)
                parents = E0.eps_lexicase(M, self.rng, 2 * max(n_off, 0))
                off = []
                for k in range(max(n_off, 0)):
                    p1 = ids[parents[2 * k]]
                    if self.rng.random() < cfg["graft_p"]:
                        p2 = ids[parents[2 * k + 1]]
                        g = Lm.graft(self.gid[p1], self.gid[p2], self.rng)
                        ops, par = ["graft"], [p1, p2]
                        if not Lm.validate(g):
                            g, ops, par = self.gid[p1], ["graft_invalid_copy"], [p1]
                    else:
                        g, ops = Lm.mutate(self.gid[p1], self.rng)
                        par = [p1]
                    off.append(self.birth(g, par, ops, gen + 1))
                pop = list(dict.fromkeys(elite + off))
                pair_c = []
                if self.arm in ("DE", "DENR"):
                    self.evaluate(list(dict.fromkeys(pop + list(res))), epoch)
                    pair_c = self.pair_step(pop, res, epoch, gen)
                    self.epoch_pairs.extend(pair_c)
                if self.arm == "DE":
                    res = self.drift(res, gen + 1)
                self.L["GENERATIONS"].w({"gen": gen, "epoch": epoch, "units": round(self.units, 1),
                                         "elite": len(elite), "dark": len(dark), "reserve": len(res),
                                         "offspring": len(off), "pair_cands": len(pair_c),
                                         "secs": round(time.time() - t0, 2)})
                print(f"  {self.arm} s{self.seed} gen {gen} units {self.units:.0f} pc={len(pair_c)} "
                      f"{time.time() - t0:.1f}s", flush=True)
                gen += 1
            ids = list(dict.fromkeys(pop + list(dark) + list(res)))
            M = self.matrix(ids, epoch)
            n = self.admit(epoch, ids, M, self.epoch_pairs)
            print(f"EPOCH {epoch} admitted {n}", flush=True)
            self.epoch_pairs = []
            self.deficits(f"epoch{epoch}_end", self.train, "val")
            epoch += 1
        self.gens, self.epochs = gen, epoch

    # ------------------------------------------------------------ pass D
    def audit(self):
        cfg = self.cfg
        rows = []
        twin = {s["twin_of"]: s["id"] for s in self.specs if s.get("twin_of")}
        for w in self.train:
            for idx, lid in enumerate(self.eco_ids[w]):
                ad = self.meta[lid]["admission"]
                r, o = ad["ruler"], ad["org"]
                eb = [self.gid[i] for i in ad["eco_before"]]
                g = self.gid[lid]
                k = f"{r}|{o}|test"
                row = {"id": lid, "home": w, "kind": ad["kind"], "ruler": r, "org": o, "genome": g,
                       "admission": ad, "eff_len": self.meta[lid]["eff_len"]}
                row["causality"] = A.causality_audit(g, W1.generate(self.by[w], cfg["select_seed"])[0])
                res_ = self.pool.map(E1.task_gains, [(w, s, g, eb, ("test",), (o,), (r,), None)
                                                     for s in [cfg["select_seed"]] + cfg["rep_seeds"]])
                row["home_test"], row["home_reps"] = res_[0][k], [x[k] for x in res_[1:]]
                row["replicated"] = bool(row["home_test"][1] >= cfg["sig_z"] and
                                         all(x[1] >= cfg["rep_z"] for x in row["home_reps"]))
                nrng = np.random.default_rng([cfg["world_seed"], self.seed, len(rows)])
                if ad["kind"] == "pair":
                    ga, gb = self.gid[ad["a"]], self.gid[ad["b"]]
                    nulls = [Lm.fuse(Lm.random_genome(nrng, n_ins=len(ga["ins"]), k=len(ga["out"])),
                                     Lm.random_genome(nrng, n_ins=len(gb["ins"]), k=len(gb["out"])))
                             for _ in range(cfg["null_n"])]
                else:
                    nulls = [Lm.random_genome(nrng, n_ins=len(g["ins"]), k=len(g["out"])) for _ in range(cfg["null_n"])]
                nv = np.array([x[k][0] for x in self.pool.map(
                    E1.task_gains, [(w, cfg["select_seed"], ng, eb, ("test",), (o,), (r,), None) for ng in nulls])])
                row["null"] = {"n": len(nv), "p95": float(np.percentile(nv, 95)), "max": float(nv.max())}
                row["beats_null"] = bool(row["home_test"][0] > row["null"]["p95"])
                if w in twin:
                    t = self.pool.apply(E1.task_gains, ((twin[w], cfg["select_seed"], g, [], ("test",), (o,), (r,), None),))
                    row["twin"] = {"world": twin[w], "gain": t[k][0], "z": t[k][1]}
                ho = {}
                others = self.held + [x for x in self.train if x != w]
                for w2, gd in zip(others, self.pool.map(E1.task_gains, [
                        (w2, cfg["select_seed"], g, [], ("test",), ORGANISMS, tuple(RULERS), None) for w2 in others])):
                    bk = max(gd, key=lambda kk: gd[kk][1])
                    ho[w2] = {"case": bk, "gain": gd[bk][0], "z": gd[bk][1]}
                row["transfer_raw"] = ho
                chans = Lm.input_channels(g)
                ab = self.pool.map(E1.task_gains, [(w, cfg["select_seed"], g, eb, ("test",), (o,), (r,), c) for c in chans])
                d = self.by[w]["d"]
                row["ablation"] = {str(c): {"world_channel": c % d, "gain_ablated": x[k][0]} for c, x in zip(chans, ab)}
                if ad["kind"] == "pair":
                    comp = {}
                    for nm in ("a", "b"):
                        cid = ad[nm]
                        x = self.pool.apply(E1.task_gains, ((w, cfg["select_seed"], self.gid[cid], eb, ("test",), (o,), (r,), None),))
                        comp[nm] = {"id": cid, "max_individual_val_gain_home": self.best_ind.get(cid, {}).get(w),
                                    "max_individual_val_gain_any": max(self.best_ind.get(cid, {}).values(), default=None),
                                    "test_alone": x[k][0], "test_alone_z": x[k][1],
                                    "genome": self.gid[cid], "root": self.meta[cid]["root"],
                                    "ops": self.meta[cid]["ops"], "birth_gen": self.meta[cid]["birth_gen"]}
                    row["components"] = comp
                rows.append(row)
                print(f"  audit {lid} {w} {ad['kind']} test={row['home_test'][0]:+.3f} rep="
                      f"{[round(x[0], 3) for x in row['home_reps']]} null95={row['null']['p95']:+.3f}", flush=True)
                json.dump(rows, open(os.path.join(self.out, "PASS_D.json"), "w"), indent=1, sort_keys=True)
        json.dump(rows, open(os.path.join(self.out, "PASS_D.json"), "w"), indent=1, sort_keys=True)
        return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["V0", "DE", "DENR"], default="DE")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=13)
    ap.add_argument("--pass-a-only", action="store_true")
    ap.add_argument("--smoke", action="store_true", help="tiny budget; not a result")
    a = ap.parse_args()
    cfg = dict(CFG)
    if a.smoke:
        cfg.update(N=24, budget_units=120, gens_per_epoch=2, reserve_size=12, drift_per_gen=4,
                   pairs_per_world=10, null_n=4, v0_dark=4)
    t0 = time.time()
    run = Run(a.arm, a.seed, a.out, a.workers, cfg)
    run.epoch_pairs = []
    pop = run.pass_a(pair_floor=a.pass_a_only)
    if a.pass_a_only:
        run.pool.close()
        print("PASS A only", flush=True)
        return
    run.evolve(pop)
    run.deficits("final", run.train + run.held, "test")
    run.audit()
    run.pool.close()
    run.pool.join()
    json.dump({"finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "wall_secs": round(time.time() - t0, 1),
               "units": run.units, "generations": run.gens, "epochs": run.epochs,
               "admitted": run.eco_ids, "lenses_born": len(run.meta)},
              open(os.path.join(a.out, "DONE.json"), "w"), indent=1)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
