"""cw01-e01 — necessity economics world.  (v2, after INSTANTIATE smoke)

Neutral affordances, each priced. There is NO workspace architecture here: A1 is
an addressable region that costs something to occupy. Whether a lineage uses it to
carry unfinished work across a gap is the thing being measured, not built.

v1 -> v2 fixes, all found by smoking the instrument before spending budget:
  E01-I1  region jammed: cells_frac up to 0.476 meant ~2 items filled 64 cells and
          nothing ever evicted, so re_entries was 0 and the mechanism under test
          could never fire. Fixed: per-item footprint is small and bounded, and
          `persist_steps` now drives eviction.
  E01-I2  arms were seeded differently, so item streams differed and the apparent
          treatment advantage was a seed artifact. Fixed: the item stream is drawn
          from a stream_seed INDEPENDENT of the arm; arms differ only in
          affordances. Arms are now genuinely matched.
  E01-I3  `persist_steps` was a gene under selection that nothing read. Now live.
  E01-I4  A4/Store was instantiated and never called; retrievals_* were emitted as
          permanent zeros. A4 is OUT of the minimal form and no longer reported.
  E01-I5  `held_keys` was never assigned. Removed.

Honest limitation: the minimal form evolves a small real-valued policy vector, not
a rich program. That is enough to ask whether the ECONOMICS select for retention,
and not enough to claim what machinery a richer organism would invent.

Backends: 'mem' and 'redis' implement identical organism-visible physics (IX).
"""
from __future__ import annotations

import math

import numpy as np


class Refused(Exception):
    """Hard refusal. Q6: a disabled affordance must REFUSE, not silently no-op."""


class Region:
    """A1: addressable region. Occupancy is priced whether or not it is read."""

    def __init__(self, cells, w_cost, r_cost, h_cost, enabled, backend="mem", rconn=None, ns=""):
        self.cells, self.w, self.r, self.h = cells, w_cost, r_cost, h_cost
        self.enabled, self.backend, self._r, self.ns = enabled, backend, rconn, ns
        self._mem = {}                       # key -> [cells, remaining, written_at]
        self.refusals = 0
        self.cell_steps_held = 0.0
        self.evicted = 0
        self.jammed = 0                      # writes refused for lack of room
        self._free = False                   # I1 sham: occupancy stops being charged

    # --- backend-neutral accessors ---------------------------------------
    def _all(self):
        if self.backend == "redis":
            return {k: [float(x) for x in v.split("|")]
                    for k, v in (self._r.hgetall(self.ns + ":region") or {}).items()}
        return self._mem

    def _put(self, key, rec):
        if self.backend == "redis":
            self._r.hset(self.ns + ":region", str(key), "|".join(str(x) for x in rec))
        else:
            self._mem[str(key)] = rec

    def _occupied(self):
        return sum(v[0] for v in self._all().values())

    def write(self, key, payload_cells, remaining, now):
        if not self.enabled:
            self.refusals += 1
            raise Refused("A1_DISABLED")
        cur = self._all()
        if str(key) in cur:                                   # refresh in place
            self._put(key, [payload_cells, remaining, now])
            return self.w * payload_cells, True
        if self._occupied() + payload_cells > self.cells:
            self.jammed += 1
            return 0.0, False
        self._put(key, [payload_cells, remaining, now])
        return self.w * payload_cells, True

    def read(self, key):
        if not self.enabled:
            self.refusals += 1
            raise Refused("A1_DISABLED")
        v = self._all().get(str(key))
        return self.r, (v is not None), (v[1] if v else None)

    def drop(self, key):
        if self.backend == "redis":
            self._r.hdel(self.ns + ":region", str(key))
        else:
            self._mem.pop(str(key), None)

    def expire(self, now, persist_steps):
        """E01-I3: the organism's own persistence gene decides how long it pays."""
        for k, v in list(self._all().items()):
            if now - v[2] >= persist_steps:
                self.drop(k)
                self.evicted += 1

    def hold_tick(self):
        occ = self._occupied()
        self.cell_steps_held += occ
        # Under the I1 sham occupancy is NOT charged, exactly as erase relieves it.
        return 0.0 if self._free else self.h * occ

    # --- I1 and its cost-matched sham -------------------------------------
    def erase(self):
        """I1: content destroyed. Charged nothing; the loss IS the intervention."""
        if self.backend == "redis":
            self._r.delete(self.ns + ":region")
        else:
            self._mem.clear()

    def sham_release(self):
        """I1 sham, corrected (CW01-D014).

        v2's sham re-charged a WRITE price every step (+39% cost) while erase
        *reduced* cost by 3%, because erasing also stops paying occupancy. Two
        arms that differ in cost by 42 points cannot isolate information loss.

        I1_erase does two things: destroys information AND relieves occupancy.
        The sham must reproduce the second WITHOUT the first -- contents stay
        readable, occupancy stops being charged -- so the only remaining
        difference between erase and sham is whether the information survives.
        """
        self._free = True
        return 0.0


# ---------------------------------------------------------------------- genome

GENE_NAMES = ("p_write", "cells_frac", "p_retrieve", "p_reenter", "persist_steps")
GENE_BOUNDS = {
    "p_write": (0.0, 1.0),
    # E01-I1: bounded so a single partial cannot monopolise the region.
    "cells_frac": (0.015, 0.125),
    "p_retrieve": (0.0, 1.0),
    "p_reenter": (0.0, 1.0),
    "persist_steps": (1.0, 60.0),
}


def seed_genome(rng):
    return {g: float(rng.uniform(*GENE_BOUNDS[g])) for g in GENE_NAMES}


def mutate(genome, rng, sigma=0.12):
    out = {}
    for g, v in genome.items():
        lo, hi = GENE_BOUNDS[g]
        out[g] = float(np.clip(v + rng.normal(0.0, sigma * (hi - lo)), lo, hi))
    return out


# ------------------------------------------------------------------ task stream

def make_items(cfg, recurrence_rate, rng, n_steps):
    """Items whose demand often exceeds one step's budget; some recur after a gap.

    E01-I2: depends ONLY on (cfg, recurrence_rate, rng). The arm never touches it,
    so matched arms see an identical stream.
    """
    p = cfg["pressure"]
    d = p["item_demand_distribution"]
    mu, sigma = math.log(d["median"]), d["sigma"]
    lo, hi = d["clip"]
    gapd = p["recurrence_gap_distribution"]
    items, schedule = [], {}
    for t in range(n_steps):
        demand = float(np.clip(rng.lognormal(mu, sigma), lo, hi))
        items.append({"id": t, "demand": demand, "arrive": t, "origin": t})
        if rng.random() < recurrence_rate:
            gap = int(np.clip(rng.geometric(1.0 / gapd["mean_steps"]), *gapd["clip"]))
            if t + gap < n_steps:
                schedule.setdefault(t + gap, []).append(t)
    return items, schedule


# -------------------------------------------------------------------- episode

N_STEPS = 120


def run_episode(genome, cfg, arm, stream_seed, policy_seed=None, intervention=None,
                backend="mem", rconn=None, ns=""):
    """One organism, one episode.

    stream_seed drives the WORLD (items, gaps). policy_seed drives the organism's
    own coin flips. Keeping them separate is what makes arms comparable: the same
    stream_seed gives every arm an identical world (E01-I2).
    """
    A = cfg["affordances"]
    a1 = A["A1_addressable_region"]
    arms = cfg["arms"][arm]

    wrng = np.random.Generator(np.random.PCG64(stream_seed))
    prng = np.random.Generator(np.random.PCG64(stream_seed if policy_seed is None else policy_seed))

    items, schedule = make_items(cfg, arms["recurrence_rate"], wrng, N_STEPS)

    region = Region(a1["cells"], a1["cost_write_per_cell"], a1["cost_read_per_cell"],
                    a1["cost_hold_per_cell_per_step"], arms["A1_enabled"], backend, rconn, ns)

    budget = cfg["pressure"]["step_compute_budget"]
    cells = max(1, int(round(genome["cells_frac"] * a1["cells"])))
    persist = genome["persist_steps"]

    cost = info = 0.0
    m = dict(compute_used=0.0, writes=0, reads=0, re_entries=0, recompute_events=0,
             partial_emissions=0, completed=0, refusals=0, evicted=0, jammed=0,
             work_saved=0.0)

    for t in range(N_STEPS):
        todo = [items[t]] + [dict(items[o], arrive=t, recurred=True)
                             for o in schedule.get(t, [])]

        for it in todo:
            remaining = it["demand"]
            key = it["origin"]

            if it.get("recurred"):
                recovered = False
                # The organism's propensity to look is a gene; the affordance may refuse.
                if prng.random() < genome["p_retrieve"]:
                    try:
                        c, hit, rem = region.read(key)
                        cost += c
                        m["reads"] += 1
                        if hit and prng.random() < genome["p_reenter"]:
                            m["work_saved"] += (remaining - rem)
                            remaining = rem
                            cost += A["A3_re_entry"]["cost"]
                            m["re_entries"] += 1
                            region.drop(key)
                            recovered = True
                    except Refused:
                        m["refusals"] += 1
                if not recovered:
                    m["recompute_events"] += 1

            spend = min(budget, remaining)
            cost += spend
            m["compute_used"] += spend
            remaining -= spend

            if remaining <= 1e-9:
                info += math.log2(1.0 + it["demand"])
                m["completed"] += 1
            else:
                m["partial_emissions"] += 1
                if prng.random() < genome["p_write"]:
                    try:
                        c, stored = region.write(key, cells, remaining, t)
                        if stored:
                            cost += c
                            m["writes"] += 1
                    except Refused:
                        m["refusals"] += 1

        region.expire(t, persist)          # E01-I3
        cost += region.hold_tick()         # occupancy charged every step

        if intervention == "I1_erase":
            region.erase()
        elif intervention == "I1_sham":
            cost += region.sham_release()

    m["cell_steps_held"] = region.cell_steps_held
    m["evicted"], m["jammed"] = region.evicted, region.jammed
    m["refusals"] += region.refusals
    m["info"], m["cost"] = info, cost
    # PRIMARY MEASURE (II): useful information transformed per unit resource.
    m["score"] = info / cost if cost > 0 else 0.0
    return m


# ------------------------------------------------------------------- evolution

def evolve(cfg, arm, generations, n_org, backend="mem", rconn=None, ns="", mkseed=None):
    """Selection on ancestor-relative score. mkseed is injected (no sys.path games)."""
    aid = cfg["attempt_id"]
    rng = np.random.Generator(np.random.PCG64(mkseed(aid, f"eo|{arm}", 0)))
    pop = [seed_genome(rng) for _ in range(n_org)]
    ancestor = [dict(g) for g in pop]

    def ep(g, tag, i):
        # stream_seed is arm-INDEPENDENT: matched worlds across arms (E01-I2).
        return run_episode(g, cfg, arm, mkseed(aid, f"stream|{tag}", i),
                           policy_seed=mkseed(aid, f"policy|{tag}", i),
                           backend=backend, rconn=rconn, ns=ns)

    anc = [ep(g, "anc", i) for i, g in enumerate(ancestor)]
    anc_mean = float(np.mean([r["score"] for r in anc]))

    hist = []
    for gen in range(generations):
        res = [ep(g, f"g{gen}", i) for i, g in enumerate(pop)]
        sc = np.array([r["score"] for r in res])
        order = np.argsort(-sc)
        elite = [pop[i] for i in order[: max(2, n_org // 4)]]
        hist.append({
            "gen": gen, "mean": float(sc.mean()), "best": float(sc.max()),
            "ancestor_relative": float(sc.mean() - anc_mean),
            "mean_writes": float(np.mean([r["writes"] for r in res])),
            "mean_reentries": float(np.mean([r["re_entries"] for r in res])),
            "mean_recompute": float(np.mean([r["recompute_events"] for r in res])),
            "mean_work_saved": float(np.mean([r["work_saved"] for r in res])),
            "mean_jammed": float(np.mean([r["jammed"] for r in res])),
            "mean_p_write": float(np.mean([g["p_write"] for g in pop])),
            "mean_p_reenter": float(np.mean([g["p_reenter"] for g in pop])),
            "mean_persist": float(np.mean([g["persist_steps"] for g in pop])),
        })
        pop = [mutate(elite[i % len(elite)], rng) for i in range(n_org)]

    return {"arm": arm, "ancestor_mean": anc_mean, "history": hist,
            "final_pop": pop, "ancestor_pop": ancestor}
