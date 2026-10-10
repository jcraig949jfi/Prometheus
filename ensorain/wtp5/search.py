"""WTP-05 evolutionary / developmental search (SLOW timescale; PREREG_WTP05 s3.4, s7).

Arms (directive s13): base, R (archive), P (promotion / module duplication), L (lifetime plasticity) and the
combinations R+P, P+L, R+P+L, plus Rr (random-checkpoint archive control, with P+L as in R+P+L).

  base  (mu + lambda) with tournament selection, mu = lambda = 32; survivors re-evaluated every generation
        (fitness = running mean over evaluations), so lucky draws do not persist.
  R     Go-Explore-style archive keyed by certified stepping-stone DESCRIPTORS (never the construction):
        per-role accuracy bins, latents retained in working state, slots in use, module count, plastic flag.
        Half of the parents come from the archive, weighted 1/sqrt(1 + times selected).
  Rr    the same archive machinery keyed by a random hash of the genome (random checkpoints).
  P     promotion operators (mutate.py) available.
  L     plasticity genes and operators available (otherwise eta = sigma = 0 always).

Fitness = lifetime reward share - complexity cost (score in PREREG s3.5). The ladder rung is NEVER fitness.
The certifier runs on candidates only (elite at log points), on held-out seeds.
This module must not import planted.py (constructed solutions are never supplied to the search).
"""
import copy
import os
import pickle
import time

import numpy as np

from .certify import certify
from .mutate import mutate, random_genome
from .tape import lifetime, n_nodes, ghash
from .worlds import make

LAM_NODE = 0.001          # per main-graph node, and per executed module node
LAM_MODULE = 0.01         # fixed cost per library module (promotion is never free)
FROZEN_DISCOUNT = 0.5     # frozen module nodes cost half


def complexity(g):
    c = LAM_NODE * len(g["nodes"])
    for m in g["modules"]:
        c += LAM_MODULE + LAM_NODE * len(m["nodes"]) * (FROZEN_DISCOUNT if m.get("frozen") else 1.0)
    calls = sum(1 for nd in g["nodes"] if nd["op"] == "CALL")
    c += LAM_NODE * calls * np.mean([len(m["nodes"]) for m in g["modules"]]) if g["modules"] and calls else 0.0
    return c


def slots_used(g):
    w = {nd["s"] for nd in g["nodes"] if nd["op"] == "WRITE"}
    r = {nd["s"] for nd in g["nodes"] if nd["op"] == "READ"}
    return len(w & r)


def _bin(a):
    return 0 if a < 0.6 else (1 if a < 0.8 else (2 if a < 0.95 else 3))


def descriptor(g, life):
    roles = tuple(sorted((k, _bin(v)) for k, v in life["roles"].items()))
    ret = ()
    rec = life.get("record")
    if rec is not None:
        K = rec["z"].shape[0]
        bits = []
        for name, (vals, tdec) in sorted(rec["ep"]["lat"].items()):
            zt = rec["z"][np.arange(K), tdec].reshape(K, -1)
            pos = (np.sign(zt) == vals[:, None]).mean(0) if zt.shape[1] else np.zeros(1)
            neg = (np.sign(zt) == -vals[:, None]).mean(0) if zt.shape[1] else np.zeros(1)
            bits.append(int(np.max(np.maximum(pos, neg)) >= 0.9))
        ret = tuple(bits)
    return (roles, ret, min(slots_used(g), 4), min(len(g["modules"]), 3), int(g.get("eta", 0) > 0))


class Run:
    def __init__(self, world_spec, arm, seed, budget_evals, out_dir, log_every=2000, cert_seed=None, seed_genomes=None):
        self.spec, self.arm, self.seed = world_spec, arm, seed
        self.world = make(world_spec)
        self.fam, self.rung, self.cond = world_spec.split("-")
        self.archive_on = arm in ("R", "RP", "RPL", "Rr")
        self.random_archive = arm == "Rr"
        self.promotion = arm in ("P", "RP", "PL", "RPL", "Rr")
        self.plasticity = arm in ("L", "PL", "RPL", "Rr")
        self.budget = budget_evals
        self.log_every = log_every
        self.cert_seed = cert_seed if cert_seed is not None else 7_000_000 + seed
        self.rng = np.random.default_rng(seed)
        self.path = os.path.join(out_dir, f"{world_spec}__{arm}__{seed}.pkl")
        self.pop, self.archive, self.telemetry = [], {}, []
        self.evals, self.gen, self.cpu, self.wall = 0, 0, 0.0, 0.0
        self.best_rung = -1
        self.first_rung_at = {}
        self.done = False
        self.seed_genomes = seed_genomes          # DIAGNOSTIC arms only (assays.py); never set by campaign5

    # ------------------------------------------------------------ evaluation
    def evaluate(self, g, record=False):
        self.world.new_life(self.rng)
        life = lifetime(g, self.world, self.rng, plasticity=self.plasticity, record_last=record)
        self.evals += 1
        return life["R"] - complexity(g), life

    def _archive_add(self, g, fit, life):
        if not self.archive_on:
            return
        key = (int(ghash(g), 16) % 64,) if self.random_archive else descriptor(g, life)
        cur = self.archive.get(key)
        if cur is None or fit > cur["fit"]:
            self.archive[key] = dict(g=g, fit=fit, sel=(cur or {}).get("sel", 0), born=self.evals)

    def _parent(self):
        if self.archive_on and self.archive and self.rng.random() < 0.5:
            keys = list(self.archive)
            w = np.array([1 / np.sqrt(1 + self.archive[k]["sel"]) for k in keys])
            k = keys[int(self.rng.choice(len(keys), p=w / w.sum()))]
            self.archive[k]["sel"] += 1
            return self.archive[k]["g"], "archive"
        idx = self.rng.choice(len(self.pop), 3, replace=False)
        return max((self.pop[i] for i in idx), key=lambda x: x["fit"])["g"], "pop"

    # ------------------------------------------------------------ loop
    def init(self):
        for k in range(32):
            if self.seed_genomes:
                g = copy.deepcopy(self.seed_genomes[k % len(self.seed_genomes)])
            else:
                g = random_genome(self.rng)
            if self.plasticity and self.rng.random() < 0.5:
                g["eta"], g["sigma"] = 0.3, 0.3
            fit, life = self.evaluate(g, record=self.archive_on)
            self.pop.append(dict(g=g, fit=fit, n=1))
            self._archive_add(g, fit, life)

    def step(self):
        t0, c0 = time.time(), time.process_time()
        children = []
        for _ in range(32):
            par, src = self._parent()
            child, _ = mutate(par, self.rng, promotion=self.promotion, plasticity=self.plasticity)
            lineage = dict(par.get("lineage", {}))
            lineage[src] = lineage.get(src, 0) + 1
            child["lineage"] = lineage
            fit, life = self.evaluate(child, record=self.archive_on)
            children.append(dict(g=child, fit=fit, n=1))
            self._archive_add(child, fit, life)
        for p in sorted(self.pop, key=lambda x: -x["fit"])[:8]:          # re-evaluate the leading survivors
            fit, _ = self.evaluate(p["g"])
            p["fit"] = (p["fit"] * p["n"] + fit) / (p["n"] + 1)
            p["n"] += 1
        self.pop = sorted(self.pop + children, key=lambda x: -x["fit"])[:32]
        self.gen += 1
        self.cpu += time.process_time() - c0
        self.wall += time.time() - t0

    def log(self):
        elite = self.pop[0]["g"]
        c = certify(elite, self.fam, self.rung, self.cert_seed + self.gen, plasticity=self.plasticity)
        rung = c["rung"] if self.fam != "C" else (1 if c.get("switch_tracked") else -1)
        if rung > self.best_rung:
            self.best_rung = rung
        for r in range(rung + 1):
            self.first_rung_at.setdefault(r, self.evals)
        arch_rungs = None
        self.telemetry.append(dict(evals=self.evals, gen=self.gen, wall=round(self.wall, 1), cpu=round(self.cpu, 1),
                                   best_fit=round(self.pop[0]["fit"], 4), elite_rung=rung, best_rung=self.best_rung,
                                   archive=len(self.archive), nodes=n_nodes(elite), modules=len(elite["modules"]),
                                   calls=sum(1 for nd in elite["nodes"] if nd["op"] == "CALL"),
                                   slots=slots_used(elite), plastic=int(elite.get("eta", 0) > 0),
                                   c_late=c.get("c_late_type1"), cert=c.get("rung_ok")))

    def save(self):
        tmp = self.path + ".tmp"
        with open(tmp, "wb") as fh:
            pickle.dump(self.__dict__, fh)
        os.replace(tmp, self.path)

    @classmethod
    def load(cls, path):
        r = cls.__new__(cls)
        with open(path, "rb") as fh:
            r.__dict__.update(pickle.load(fh))
        return r

    def run(self, max_wall=None):
        t_start = time.time()
        if not self.pop:
            self.init()
            self.log()
            self.save()
        next_log = (self.evals // self.log_every + 1) * self.log_every
        while self.evals < self.budget:
            self.step()
            if self.evals >= next_log:
                self.log()
                self.save()
                next_log += self.log_every
                if getattr(self, "flat_stop", False) and self.frontier_flat():
                    self.stopped_flat = True
                    break
            if max_wall and time.time() - t_start > max_wall:
                break
        if self.evals >= self.budget:
            self.log()
            self.done = True
        if getattr(self, "stopped_flat", False):
            self.done = True
        self.save()
        return self

    def frontier_flat(self):
        """PREREG_WTP05 s7.3 FLAT STOP: over the last max(50,000, 40% of evals) evaluations, no new best rung,
        archive growth < 5% and best-fitness gain < .01. Never fires before that window has fully elapsed."""
        win = max(50_000, 0.4 * self.evals)
        if self.evals < win or not self.telemetry:
            return False
        cut = self.evals - win
        before = [t for t in self.telemetry if t["evals"] <= cut]
        after = [t for t in self.telemetry if t["evals"] > cut]
        if not before or not after:
            return False
        b, a = before[-1], after[-1]
        new_rung = a["best_rung"] > b["best_rung"]
        arch_growth = (a["archive"] - b["archive"]) / max(1, b["archive"])
        fit_gain = max(t["best_fit"] for t in after) - max(t["best_fit"] for t in before)
        return (not new_rung) and arch_growth < 0.05 and fit_gain < 0.01


def summary(r):
    t = r.telemetry
    return dict(spec=r.spec, arm=r.arm, seed=r.seed, evals=r.evals, gens=r.gen, wall=round(r.wall, 1), cpu=round(r.cpu, 1),
                best_rung=r.best_rung, final_rung=t[-1]["elite_rung"] if t else None, first_rung_at=r.first_rung_at,
                best_fit=t[-1]["best_fit"] if t else None, archive=len(r.archive), done=r.done,
                stopped_flat=bool(getattr(r, "stopped_flat", False)), telemetry=t,
                elite=copy.deepcopy(r.pop[0]["g"]) if r.pop else None)
