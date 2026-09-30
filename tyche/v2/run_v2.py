"""Tyche v2 driver: one run = one point of the pressure map.

Axes (roles/Tyche/design/V2_PRESSURE_MAP_DESIGN.md):
  --harsh STRICT | LEX | RES
        STRICT  parents and elites must hold a SIGNIFICANT case (val gain
                > 0 with z >= 2); no reserve; empty slots -> random immigrants
        LEX     eps-lexicase over all cases; elites; NO reserve
        RES     LEX + 48-slot utility-free reserve (age 5, novelty +
                lineage bonus, 1/3 random, neutral drift 12/gen, credit)
  --worlds broad | related:<CLASS> | solo:<WORLD> | rbroad | rrelated | rsolo:<Rk>
  --coal   SINGLE | PAIRS | TRIPLES   (organism-free MI screen, then fit)
  --chem   MUT | GRAFT | LOL          (LOL adds compose(a, b) = b(a(X)))
  budget: --gens N (fixed generations; regime runs) or --units U
  regime worlds switch law at --switch G (unannounced to the ecology)

Every parent choice is logged with the deciding case, its gain and z, so a
survival can later be attributed to a significant win, a noise-level win,
elitism or reserve membership.
"""

from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import argparse
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
from . import eco_v2 as E2
from . import worlds_v2 as W2

SEED_WORLDS = 20261002
CFG = {
    "N": 96, "gens_per_epoch": 10, "elite_cap": 24, "graft_p": 0.25, "compose_p": 0.15,
    "reserve_size": 48, "reserve_age": 5, "reserve_random_frac": 1 / 3, "lineage_bonus": 0.1,
    "drift_per_gen": 12, "credit_weight": 3.0, "credit_protect_gens": 10,
    "screen_pairs": 300, "fit_pairs": 20, "screen_triples": 300, "fit_triples": 10,
    "screen_unit": 0.05, "strict_z": 2.0,
    "admit_min_val_gain": 0.02, "admit_top": 5, "admit_z": 4.0, "admit_min_conf_gain": 0.01,
    "rep_seeds": [101, 102], "sig_z": 4.0, "rep_z": 3.0, "null_n": 32,
}


def world_set(name):
    """(selection specs, all specs the workers must know)."""
    static = {v: W2.build_static(SEED_WORLDS, v) for v in range(4)}
    regime = W2.build_regime(SEED_WORLDS, 0)
    allspecs = [s for v in static.values() for s in v] + regime
    if name == "broad":
        sel = static[0]
    elif name.startswith("related:"):
        cls = name.split(":")[1]
        sel = [s for v in range(4) for s in static[v] if s["cls"] == cls]
    elif name.startswith("solo:"):
        sel = [s for s in allspecs if s["id"] == name.split(":")[1]]
    elif name == "rbroad":
        # regime worlds + 6 UNRELATED static niches (smooth, deceptive,
        # order-2, donor, representation-change, generated); trimmed from
        # the full static set for compute (design s5)
        keep = {"D1_v0", "D2_v0", "D3_v0", "D5d_v0", "D6_v0", "D7a_v0"}
        sel = regime + [s for s in static[0] if s["id"] in keep]
    elif name == "rrelated":
        sel = regime
    elif name.startswith("rsolo:"):
        sel = [s for s in regime if s["id"].startswith(name.split(":")[1] + "_")]
    else:
        raise ValueError(name)
    # workers see phase-expanded specs of everything
    known = []
    for s in allspecs:
        known += [W2.phase_spec(s, 1), W2.phase_spec(s, 2)] if "law2" in s else [s]
    return sel, known


class Log:
    def __init__(self, path):
        self.f = open(path, "a", encoding="ascii")

    def w(self, rec):
        self.f.write(json.dumps(rec, sort_keys=True) + "\n")
        self.f.flush()


def lexicase_trace(M, Zs, rng, n_select, eligible=None):
    """eps-lexicase on gains M; returns [(row, deciding case)]."""
    n, c = M.shape
    rows = np.arange(n) if eligible is None else np.asarray(eligible)
    if len(rows) == 0:
        return []
    med = np.median(M[rows], 0)
    eps = np.median(np.abs(M[rows] - med), 0)
    out = []
    for _ in range(n_select):
        cand = rows
        last = None
        for j in rng.permutation(c):
            v = M[cand, j]
            cand = cand[v >= v.max() - eps[j]]
            last = j
            if len(cand) == 1:
                break
        out.append((int(rng.choice(cand)), int(last)))
    return out


class RunV2:
    def __init__(self, a, cfg):
        self.a, self.cfg = a, cfg
        os.makedirs(a.out, exist_ok=True)
        sel, known = world_set(a.worlds)
        self.sel = sel
        self.slots = [s["id"] for s in sel]
        self.by = {s["id"]: s for s in known}
        self.base = {s["id"]: s for s in sel}
        self.phase = 1
        self.pool = Pool(a.workers, initializer=E2._init, initargs=(known,))
        self.rng = np.random.default_rng([SEED_WORLDS, a.seed])
        self.gid, self.meta, self.cache, self.credit = {}, {}, {}, {}
        self.eco = {w: [] for w in self.slots}
        self.eco_ids = {w: [] for w in self.slots}
        self.units = 0.0
        self.L = {k: Log(os.path.join(a.out, f"{k}.jsonl")) for k in
                  ("GENEALOGY", "EVALS", "GENERATIONS", "SELECTION", "ADMISSIONS", "DEFICITS",
                   "COALITIONS", "OPTIONALITY", "POP")}
        def g(*x):
            try:
                return subprocess.run(["git", *x], capture_output=True, text=True, timeout=30).stdout.strip()
            except Exception:
                return None
        json.dump({"args": vars(a), "config": cfg, "slots": self.slots,
                   "worlds_hash": W2.worlds_hash(sel), "receipt": {
                       "head": g("rev-parse", "HEAD"), "dirty": bool(g("status", "--porcelain", "--untracked-files=no")),
                       "host": platform.node()},
                   "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
                  open(os.path.join(a.out, "CONFIG.json"), "w"), indent=1)
        json.dump(sel, open(os.path.join(a.out, "WORLDS.json"), "w"), indent=1)

    # ------------------------------------------------------------------
    def spec_id(self, slot):
        s = self.base[slot]
        return W2.phase_spec(s, self.phase)["id"] if "law2" in s else slot

    def law(self, slot):
        return self.by[self.spec_id(slot)]["law"]

    def birth(self, g, parents, ops, gen):
        lid = Lm.lens_id(g)
        if lid not in self.meta:
            root = self.meta[parents[0]]["root"] if parents and parents[0] in self.meta else lid
            self.meta[lid] = {"id": lid, "birth_gen": gen, "parents": parents, "ops": ops, "root": root,
                              "len": len(g["ins"])}
            self.gid[lid] = g
            self.L["GENEALOGY"].w({**self.meta[lid], "genome": g})
        return lid

    def evaluate(self, ids, epoch):
        key = (epoch, self.phase)
        todo = [i for i in dict.fromkeys(ids) if (key, i) not in self.cache]
        if todo:
            gl = [self.gid[i] for i in todo]
            res = dict(self.pool.map(E2.task_lenses, [(self.spec_id(w), gl, self.eco[w]) for w in self.slots]))
            for j, i in enumerate(todo):
                c = {w: res[self.spec_id(w)][j] for w in self.slots}
                self.cache[(key, i)] = c
                self.L["EVALS"].w({"epoch": epoch, "phase": self.phase, "id": i, "cases": c})
            self.units += len(todo)
        return [self.cache[(key, i)] for i in ids]

    def cases(self):
        return [(w, o) for w in self.slots for o in ORGANISMS]

    def matrices(self, ids, epoch):
        cs = self.evaluate(ids, epoch)
        G = np.array([[c[w][f"R0|{o}"][0] for (w, o) in self.cases()] for c in cs])
        Zs = np.array([[c[w][f"R0|{o}"][1] for (w, o) in self.cases()] for c in cs])
        return G, Zs

    def deficits(self, tag, split="val"):
        tasks = [(self.spec_id(w), 1, self.eco[w], W2.oracle(self.law(w)), split) for w in self.slots]
        for (wid, d), w in zip(self.pool.map(E2.task_deficit, tasks), self.slots):
            self.L["DEFICITS"].w({"tag": tag, "slot": w, "spec": wid, "phase": self.phase, "split": split,
                                  "eco": list(self.eco_ids[w]), **d})

    # ------------------------------------------------------------------ reserve (RES)
    def reserve(self, res, ids, elite, gen):
        cfg = self.cfg
        for i in list(res):
            res[i] += 1
        prot = [i for i in res if res[i] < cfg["reserve_age"]]
        prot += [i for i, g0 in self.credit.items() if gen - g0 < cfg["credit_protect_gens"] and i in self.gid]
        prot = list(dict.fromkeys(prot))[: cfg["reserve_size"]]
        cand = [i for i in dict.fromkeys(ids + list(res)) if i not in prot and i not in elite]
        slots = cfg["reserve_size"] - len(prot)
        chosen, why = [], {i: "age_or_credit" for i in prot}
        if cand and slots > 0:
            pool_sig = [Lm.signature(self.gid[i]) for i in dict.fromkeys(ids + list(res))]
            nov = E0.novelty([Lm.signature(self.gid[i]) for i in cand], pool_sig)
            roots = {self.meta[i]["root"] for i in prot}
            score = nov + cfg["lineage_bonus"] * np.array([self.meta[i]["root"] not in roots for i in cand])
            n_rand = int(round(slots * cfg["reserve_random_frac"]))
            chosen = [cand[k] for k in np.argsort(-score)][: slots - n_rand]
            for i in chosen:
                why[i] = "novelty"
            left = [i for i in cand if i not in chosen]
            if left and n_rand:
                r = [str(x) for x in self.rng.choice(left, size=min(len(left), n_rand), replace=False)]
                for i in r:
                    why[i] = "random"
                chosen += r
        new = {i: res.get(i, 0) for i in prot + chosen}
        return new, why

    def drift(self, res, gen):
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
        return res

    # ------------------------------------------------------------------ coalitions
    def coalition_step(self, pool_ids, epoch, gen):
        cfg, a = self.cfg, self.a
        if a.coal == "SINGLE" or len(pool_ids) < 3:
            return []
        plan = [(2, cfg["screen_pairs"], cfg["fit_pairs"])]
        if a.coal == "TRIPLES":
            plan.append((3, cfg["screen_triples"], cfg["fit_triples"]))
        cands = []
        for w in self.slots:
            for k, n_screen, n_fit in plan:
                seen = set()
                for _ in range(4 * n_screen):
                    if len(seen) >= n_screen:
                        break
                    t = tuple(sorted(str(x) for x in self.rng.choice(pool_ids, size=k, replace=False)))
                    seen.add(t)
                seen = sorted(seen)
                _, sc = self.pool.apply(E2.task_screen, ((self.spec_id(w), [[self.gid[i] for i in t] for t in seen]),))
                self.units += len(seen) * cfg["screen_unit"] / len(self.slots)
                order = sorted(range(len(seen)), key=lambda j: (-sc[j][1], -sc[j][0]))[:n_fit]
                fit = [seen[j] for j in order]
                _, cs = self.pool.apply(E2.task_coalitions, ((self.spec_id(w), [[self.gid[i] for i in t] for t in fit],
                                                              self.eco[w]),))
                self.units += len(fit) / len(self.slots)
                for t, c, j in zip(fit, cs, order):
                    best = max(c, key=lambda kk: c[kk][0])
                    if c[best][0] >= cfg["admit_min_val_gain"]:
                        ind = [self.cache.get(((epoch, self.phase), i), {}).get(w, {}).get(best, (None, None)) for i in t]
                        rec = {"gen": gen, "epoch": epoch, "slot": w, "members": list(t), "case": best,
                               "joint_val": c[best][0], "joint_z": c[best][1], "screen": sc[j],
                               "members_val": ind}
                        self.L["COALITIONS"].w(rec)
                        cands.append(rec)
        return cands

    # ------------------------------------------------------------------ admission
    def admit(self, epoch, ids, G, cands):
        cfg = self.cfg
        cs = self.cases()
        n = 0
        for w in self.slots:
            cols = [k for k, (ww, o) in enumerate(cs) if ww == w]
            best = G[:, cols].max(1)
            opts = []
            for j in np.argsort(-best)[: cfg["admit_top"]]:
                if best[j] >= cfg["admit_min_val_gain"] and ids[j] not in self.eco_ids[w]:
                    o = cs[cols[int(np.argmax(G[j, cols]))]][1]
                    opts.append((float(best[j]), "single", [ids[j]], o))
            for c in sorted([c for c in cands if c["slot"] == w], key=lambda c: -c["joint_val"])[: cfg["admit_top"]]:
                opts.append((c["joint_val"], "coalition", c["members"], c["case"].split("|")[1]))
            for val, kind, mem, o in sorted(opts, key=lambda x: -x[0]):
                g = self.gid[mem[0]]
                for m in mem[1:]:
                    g = Lm.fuse(g, self.gid[m])
                mu, z, nn = self.pool.apply(E2.task_gains, ((self.spec_id(w), 1, [g], self.eco[w], ("conf",), (o,), None),))[f"R0|{o}|conf"]
                ok = z >= cfg["admit_z"] and mu >= cfg["admit_min_conf_gain"]
                lid = mem[0] if kind == "single" else self.birth(g, mem, ["fuse"], -1)
                self.L["ADMISSIONS"].w({"epoch": epoch, "phase": self.phase, "slot": w, "spec": self.spec_id(w),
                                        "kind": kind, "id": lid, "members": mem, "org": o, "val": val,
                                        "conf_gain": mu, "conf_z": z, "admitted": bool(ok),
                                        "eco_before": list(self.eco_ids[w])})
                if ok:
                    self.meta[lid]["admission"] = {"epoch": epoch, "phase": self.phase, "slot": w,
                                                   "spec": self.spec_id(w), "kind": kind, "members": mem, "org": o,
                                                   "eco_before": list(self.eco_ids[w]), "conf_gain": mu, "conf_z": z}
                    self.eco[w].append(g)
                    self.eco_ids[w].append(lid)
                    n += 1
                    if kind == "coalition" and self.a.harsh == "RES":
                        for m in mem:
                            self.credit[m] = epoch
                    break
        return n

    # ------------------------------------------------------------------ optionality at a regime switch
    def optionality(self, living, gen):
        for w in self.slots:
            s = self.base[w]
            if "law2" not in s:
                continue
            spec2 = W2.phase_spec(s, 2)
            _, rows = self.pool.apply(E2.task_carriers, ((spec2["id"], spec2["law"], [self.gid[i] for i in living]),))
            carry = [[v > 0.005 for v in r] for r in rows]
            self.L["OPTIONALITY"].w({"gen": gen, "slot": w, "n_living": len(living),
                                     "per_precursor_frac": [float(np.mean([c[j] for c in carry])) for j in range(len(rows[0]))] if rows else [],
                                     "frac_any": float(np.mean([any(c) for c in carry])) if carry else 0.0,
                                     "frac_all": float(np.mean([all(c) for c in carry])) if carry else 0.0,
                                     "carriers": {i: r for i, r in zip(living, rows) if max(r) > 0.005}})

    # ------------------------------------------------------------------ loop
    def run(self):
        a, cfg = self.a, self.cfg
        self.deficits("eco0")
        pop = [self.birth(Lm.random_genome(self.rng), [], ["init"], 0) for _ in range(cfg["N"])]
        res = {}
        gen, epoch = 0, 0

        def done():
            return gen >= a.gens if a.gens else self.units >= a.units

        while not done():
            for _ in range(cfg["gens_per_epoch"]):
                if done():
                    break
                if a.switch and gen == a.switch and self.phase == 1:
                    self.optionality(list(dict.fromkeys(pop + list(res))), gen)
                    self.phase = 2
                    self.deficits(f"switch_gen{gen}")
                t0 = time.time()
                ids = list(dict.fromkeys(pop + list(res)))
                G, Zs = self.matrices(ids, epoch)
                cs = self.cases()
                sig = (G > 0) & (Zs >= cfg["strict_z"])
                elite = []
                for w in self.slots:
                    cols = [k for k, (ww, o) in enumerate(cs) if ww == w]
                    sub = G[:, cols].max(1)
                    if a.harsh == "STRICT":
                        sub = np.where(sig[:, cols].any(1), sub, -np.inf)
                    j = int(np.argmax(sub))
                    if sub[j] > (0.0 if a.harsh == "STRICT" else 0.01):
                        elite.append((float(sub[j]), ids[j], w))
                elite_ids = list(dict.fromkeys(i for _, i, _ in sorted(elite, reverse=True)))[: cfg["elite_cap"]]
                why = {}
                if a.harsh == "RES":
                    res, why = self.reserve(res, ids, elite_ids, gen)
                n_off = cfg["N"] - len(elite_ids)
                eligible = [k for k in range(len(ids)) if sig[k].any()] if a.harsh == "STRICT" else None
                picks = lexicase_trace(G, Zs, self.rng, 2 * max(n_off, 0), eligible)
                off, sel_log = [], []
                for k in range(max(n_off, 0)):
                    if not picks:
                        g = Lm.random_genome(self.rng)
                        off.append(self.birth(g, [], ["immigrant"], gen + 1))
                        continue
                    (r1, c1), (r2, c2) = picks[2 * k], picks[2 * k + 1]
                    p1, p2 = ids[r1], ids[r2]
                    sel_log.append({"p": p1, "case": list(cs[c1]), "gain": float(G[r1, c1]), "z": float(Zs[r1, c1])})
                    u = self.rng.random()
                    if a.chem in ("GRAFT", "LOL") and u < cfg["graft_p"]:
                        g, ops, par = Lm.graft(self.gid[p1], self.gid[p2], self.rng), ["graft"], [p1, p2]
                        sel_log.append({"p": p2, "case": list(cs[c2]), "gain": float(G[r2, c2]), "z": float(Zs[r2, c2])})
                    elif a.chem == "LOL" and u < cfg["graft_p"] + cfg["compose_p"]:
                        g, ops, par = Lm.compose(self.gid[p1], self.gid[p2]), ["compose"], [p1, p2]
                        sel_log.append({"p": p2, "case": list(cs[c2]), "gain": float(G[r2, c2]), "z": float(Zs[r2, c2])})
                    else:
                        g, ops = Lm.mutate(self.gid[p1], self.rng)
                        par = [p1]
                    if not Lm.validate(g, 9) or len(g["ins"]) > 2 * Lm.MAXLEN:
                        g, ops, par = self.gid[p1], ["invalid_copy"], [p1]
                    off.append(self.birth(g, par, ops, gen + 1))
                self.L["SELECTION"].w({"gen": gen, "phase": self.phase, "parents": sel_log,
                                       "elites": [[i, w, round(v, 4)] for v, i, w in elite],
                                       "reserve": {i: why.get(i, "kept") for i in res},
                                       "n_eligible": None if eligible is None else len(eligible),
                                       "immigrants": sum(1 for i in off if self.meta[i]["ops"] == ["immigrant"])})
                pop = list(dict.fromkeys(elite_ids + off))
                cands = []
                if a.coal != "SINGLE":
                    pool_ids = list(dict.fromkeys(pop + list(res)))
                    self.evaluate(pool_ids, epoch)
                    cands = self.coalition_step(pool_ids, epoch, gen)
                    self.epoch_cands.extend(cands)
                if a.harsh == "RES":
                    res = self.drift(res, gen + 1)
                best = {w: round(float(G[:, [k for k, (ww, o) in enumerate(cs) if ww == w]].max()), 4) for w in self.slots}
                self.L["POP"].w({"gen": gen, "pop": pop, "reserve": sorted(res)})
                self.L["GENERATIONS"].w({"gen": gen, "epoch": epoch, "phase": self.phase, "units": round(self.units, 1),
                                         "best_val_by_slot": best, "elite": len(elite_ids), "reserve": len(res),
                                         "coalition_cands": len(cands), "secs": round(time.time() - t0, 2)})
                print(f"  {a.tag} gen {gen} ph{self.phase} units {self.units:.0f} {time.time() - t0:.1f}s", flush=True)
                gen += 1
            ids = list(dict.fromkeys(pop + list(res)))
            G, _ = self.matrices(ids, epoch)
            n = self.admit(epoch, ids, G, self.epoch_cands)
            self.epoch_cands = []
            self.deficits(f"epoch{epoch}_end")
            print(f"EPOCH {epoch} admitted {n}", flush=True)
            epoch += 1
        self.gens, self.epochs = gen, epoch
        self.deficits("final", "test")

    # ------------------------------------------------------------------ pass D (slim)
    def audit(self):
        cfg = self.cfg
        rows = []
        twins = {s.get("twin_of"): s["id"] for s in self.by.values() if s.get("twin_of")}
        for w in self.slots:
            for lid in self.eco_ids[w]:
                ad = self.meta[lid]["admission"]
                o, spec = ad["org"], ad["spec"]
                eb = [self.gid[i] for i in ad["eco_before"]]
                g = self.gid[lid]
                k = f"R0|{o}|test"
                r = self.pool.map(E2.task_gains, [(spec, s, [g], eb, ("test",), (o,), None) for s in [1] + cfg["rep_seeds"]])
                row = {"id": lid, "slot": w, "spec": spec, "kind": ad["kind"], "members": ad["members"], "org": o,
                       "admission": ad, "home_test": r[0][k], "home_reps": [x[k] for x in r[1:]]}
                row["replicated"] = bool(row["home_test"][1] >= cfg["sig_z"] and all(x[1] >= cfg["rep_z"] for x in row["home_reps"]))
                nrng = np.random.default_rng([SEED_WORLDS, self.a.seed, len(rows)])
                nulls = []
                for _ in range(cfg["null_n"]):
                    ng = None
                    for m in ad["members"]:
                        rg = Lm.random_genome(nrng, n_ins=len(self.gid[m]["ins"]), k=min(3, len(self.gid[m]["out"])))
                        ng = rg if ng is None else Lm.fuse(ng, rg)
                    nulls.append(ng)
                nv = np.array([x[k][0] for x in self.pool.map(E2.task_gains, [(spec, 1, [ng], eb, ("test",), (o,), None) for ng in nulls])])
                row["null"] = {"p95": float(np.percentile(nv, 95)), "max": float(nv.max())}
                row["beats_null"] = bool(row["home_test"][0] > row["null"]["p95"])
                row["causality"] = A.causality_audit(g, W2.generate(self.by[spec], 1)[0])
                base_id = spec.split("@")[0]
                if base_id in twins:
                    t = self.pool.apply(E2.task_gains, ((twins[base_id], 1, [g], [], ("test",), (o,), None),))
                    row["twin"] = {"world": twins[base_id], "gain": t[k][0], "z": t[k][1]}
                rows.append(row)
        json.dump(rows, open(os.path.join(self.a.out, "PASS_D.json"), "w"), indent=1, sort_keys=True)
        return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harsh", choices=["STRICT", "LEX", "RES"], required=True)
    ap.add_argument("--worlds", required=True)
    ap.add_argument("--coal", choices=["SINGLE", "PAIRS", "TRIPLES"], default="PAIRS")
    ap.add_argument("--chem", choices=["MUT", "GRAFT", "LOL"], default="GRAFT")
    ap.add_argument("--gens", type=int, default=0)
    ap.add_argument("--units", type=float, default=0)
    ap.add_argument("--switch", type=int, default=0)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    assert a.gens or a.units
    t0 = time.time()
    r = RunV2(a, dict(CFG))
    r.epoch_cands = []
    r.run()
    r.audit()
    r.pool.close()
    r.pool.join()
    json.dump({"finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "wall_secs": round(time.time() - t0, 1),
               "gens": r.gens, "units": r.units, "admitted": r.eco_ids, "lenses_born": len(r.meta)},
              open(os.path.join(a.out, "DONE.json"), "w"), indent=1)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
