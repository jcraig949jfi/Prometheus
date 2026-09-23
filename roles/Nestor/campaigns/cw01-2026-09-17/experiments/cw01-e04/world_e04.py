"""cw01-e04 — channel economics, and whether handling is TRIAGE or merely uniform.

Items arrive in pairs separated by a gap, so useful output requires carrying
information across time. The channel that spans the gap is bounded, expiring,
delayed and lossy. Nothing here is named queue, cache, scheduler or retry: the
organism never observes TTL, occupancy, or whether a specific value still exists.
The object vanishes. It pays the consequence.

THE DISTINCTION THIS WORLD EXISTS TO MEASURE
  selectivity = how few pairs get channel treatment
  triage      = whether WHICH ones depends on the item's properties
An organism that places a fixed fraction blindly is selective, cheap, and has
learned nothing. That outcome is deliberately REACHABLE (all weights zero) because
it is the honest null.

STRUCTURAL FIXES CARRIED FORWARD, applied at construction rather than guarded:
  * Arms are genome/world transformations applied UP FRONT, so every arm runs
    identical code (CW01-D019, CW01-D021).
  * Decisions are DETERMINISTIC given genome and observable features - no policy RNG.
  * p_drop is world-side stochasticity, and an organism that places fewer items
    would otherwise consume fewer drop draws and desynchronise the arms. Drop
    outcomes are PRE-DRAWN per item, so RNG consumption is decision-independent.
  * The property->worth map is attempt-stable, never episode-stable (CW01-D029).

Honest limitation: two 5-parameter linear policies, not a rich program.
"""
from __future__ import annotations

import math

import numpy as np

NEUTRAL_GENES = ("neutral_a", "neutral_b")


# ---------------------------------------------------------------- latent facts

def attempt_worth_map(cfg, mkseed):
    """Hidden features -> worth map. ONE per attempt (CW01-D029)."""
    r = np.random.Generator(np.random.PCG64(mkseed(cfg["attempt_id"], "worthmap", 0)))
    return r.normal(0, 1, size=cfg["items"]["observable_features"])


def worth_of(x, wmap, cfg, scramble=None):
    """Latent worth. The organism never sees this - only x."""
    w = wmap if scramble is None else wmap[list(scramble)]
    lo, hi = cfg["items"]["worth_range"]
    z = float(np.dot(x, w)) / max(1e-9, np.linalg.norm(w))
    return lo + (hi - lo) / (1.0 + math.exp(-z))


# ---------------------------------------------------------------------- genome

def seed_genome(cfg, rng):
    F = cfg["items"]["observable_features"]
    gb, wb = cfg["genome"]["bias_bounds"], cfg["genome"]["weight_bounds"]
    return {"b_place": float(rng.uniform(*gb)), "w_place": rng.uniform(wb[0], wb[1], size=F),
            "b_rec": float(rng.uniform(*gb)), "w_rec": rng.uniform(wb[0], wb[1], size=F),
            "neutral_a": float(rng.uniform(0, 1)), "neutral_b": float(rng.uniform(0, 1))}


def mutate(genome, cfg, rng, sigma=0.10):
    gb, wb = cfg["genome"]["bias_bounds"], cfg["genome"]["weight_bounds"]
    out = {}
    for k in ("b_place", "b_rec"):
        out[k] = float(np.clip(genome[k] + rng.normal(0, sigma * (gb[1] - gb[0])), *gb))
    for k in ("w_place", "w_rec"):
        out[k] = np.clip(genome[k] + rng.normal(0, sigma * (wb[1] - wb[0]), genome[k].shape), *wb)
    for k in NEUTRAL_GENES:
        out[k] = float(np.clip(genome[k] + rng.normal(0, sigma), 0, 1))
    return out


def apply_arm(genome, arm_cfg):
    """The arm is a transformation. After this, all arms run identical code."""
    g = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in genome.items()}
    if not arm_cfg.get("triage_enabled", True):
        g["w_place"][:] = 0.0
        g["w_rec"][:] = 0.0
    return g


def _fires(bias, w, x):
    return (bias + float(np.dot(w, x))) > 0.0


# ----------------------------------------------------------------------- world

def make_items(cfg, rng, wmap, scramble=None):
    """Items in pairs. Drop outcomes are PRE-DRAWN so RNG use is decision-independent."""
    it = cfg["items"]
    F, n = it["observable_features"], it["items_per_episode"]
    gapd = it["pair_gap_distribution"]
    p_drop = cfg["channel"]["p_drop"]
    items = []
    for t in range(n):
        x = rng.normal(0, 1, size=F)
        gap = int(np.clip(rng.geometric(1.0 / gapd["mean_steps"]), *gapd["clip"]))
        items.append({"t": t, "x": x, "gap": gap, "partner_t": t + gap,
                      "worth": worth_of(x, wmap, cfg, scramble),
                      "drop": bool(rng.random() < p_drop)})
    return items


class Channel:
    """Bounded, ordered, forgetful, delayed. Nothing about it is observable."""

    def __init__(self, cfg):
        c = cfg["channel"]
        self.cap, self.ttl, self.delay = c["capacity"], c["ttl_steps"], c["delay_steps"]
        self.slots = {}
        self.full_failures = 0
        self.expiries = 0
        self.occ_sum = 0.0
        self.ticks = 0

    def place(self, key, step, dropped):
        if dropped:
            return False
        if len(self.slots) >= self.cap:
            self.full_failures += 1
            return False
        self.slots[key] = step
        return True

    def get(self, key, step):
        put = self.slots.get(key)
        if put is None:
            return False
        if step - put < self.delay:
            return False
        del self.slots[key]
        return True

    def tick(self, step):
        gone = [k for k, t in self.slots.items() if step - t >= self.ttl]
        for k in gone:
            del self.slots[k]
        self.expiries += len(gone)
        self.occ_sum += len(self.slots)
        self.ticks += 1


def run_episode(genome, cfg, arm, stream_seed, wmap=None, scramble=None, collect_patterns=False):
    arm_cfg = cfg["arms"][arm]
    g = apply_arm(genome, arm_cfg)
    channel_on = bool(arm_cfg.get("channel_enabled", True))

    wrng = np.random.Generator(np.random.PCG64(stream_seed))
    if wmap is None:
        wmap = wrng.normal(0, 1, size=cfg["items"]["observable_features"])
    items = make_items(cfg, wrng, wmap, scramble)

    ch = Channel(cfg)
    c = cfg["channel"]
    c_put, c_get, c_rec = c["cost_put"], c["cost_get"], cfg["actions"]["cost_recompute"]

    by_partner = {}
    for it in items:
        by_partner.setdefault(it["partner_t"], []).append(it)

    info = cost = 0.0
    m = dict(pairs_seen=0, placements=0, placement_failures_full=0, retrievals=0, retrieval_hits=0,
             expiries_suffered=0, drops_suffered=0, recomputes=0, skips=0)
    feats, acts, worths = [], [], []

    n_steps = cfg["items"]["items_per_episode"]
    for step in range(n_steps):
        it = items[step]
        m["pairs_seen"] += 1

        place = channel_on and _fires(g["b_place"], g["w_place"], it["x"])
        if place:
            cost += c_put
            m["placements"] += 1
            before = ch.full_failures
            ok = ch.place(it["t"], step, it["drop"])
            if it["drop"]:
                m["drops_suffered"] += 1
            if ch.full_failures > before:
                m["placement_failures_full"] += 1
        if collect_patterns:
            # Triage means handling tracks what MATTERS, and worth depends on all four
            # features through the hidden map. Conditioning on x[0] alone would
            # systematically understate triage and could manufacture an artefactual
            # NULL (the CW01-D029 shape). Worth is latent to the ORGANISM; measuring
            # against it here is legitimate and is the sharper question.
            lo, hi = cfg["items"]["worth_range"]
            edges = [lo + (hi - lo) * q for q in (0.25, 0.5, 0.75)]
            worths.append(int(np.digitize(float(it["worth"]), edges)))
            feats.append(int(np.digitize(float(it["x"][0]), [-0.6, 0.0, 0.6])))
            acts.append(1 if place else 0)

        for partner in by_partner.get(step, []):
            got = False
            if channel_on:
                cost += c_get
                m["retrievals"] += 1
                got = ch.get(partner["t"], step)
                if got:
                    m["retrieval_hits"] += 1
            if got:
                info += math.log2(1.0 + partner["worth"])
            elif _fires(g["b_rec"], g["w_rec"], partner["x"]):
                cost += c_rec
                m["recomputes"] += 1
                info += math.log2(1.0 + partner["worth"])
            else:
                m["skips"] += 1

        ch.tick(step)

    m["expiries_suffered"] = ch.expiries
    m["channel_occupancy_mean"] = ch.occ_sum / max(1, ch.ticks)
    m["selectivity"] = m["placements"] / max(1, m["pairs_seen"])
    m["info"], m["cost"] = info, cost
    m["score"] = info / cost if cost > 0 else 0.0
    if collect_patterns:
        m["_features"], m["_actions"], m["_worths"] = feats, acts, worths
    return m


# ------------------------------------------------------------------- evolution

def evolve(cfg, arm, generations, n_org, mkseed, wmap=None):
    aid = cfg["attempt_id"]
    if wmap is None:
        wmap = attempt_worth_map(cfg, mkseed)
    rng = np.random.Generator(np.random.PCG64(mkseed(aid, "evo|" + arm, 0)))
    pop = [seed_genome(cfg, rng) for _ in range(n_org)]
    ancestor = [dict(p) for p in pop]

    def ep(gm, tag, i):
        return run_episode(gm, cfg, arm, mkseed(aid, "stream|" + tag, i), wmap=wmap)

    anc_mean = float(np.mean([ep(p, "anc", i)["score"] for i, p in enumerate(ancestor)]))
    elite_n = max(2, int(n_org * cfg["population"]["elite_fraction"]))
    sigma = cfg["population"]["mutation_sigma"]
    hist = []

    for gen in range(generations):
        res = [ep(p, "g" + str(gen), i) for i, p in enumerate(pop)]
        sc = np.array([r["score"] for r in res])
        rec = {"gen": gen, "mean": float(sc.mean()), "best": float(sc.max()),
               "ancestor_relative": float(sc.mean() - anc_mean)}
        for k in ("selectivity", "placements", "retrieval_hits", "recomputes", "skips",
                  "expiries_suffered", "placement_failures_full", "channel_occupancy_mean",
                  "cost", "info"):
            rec["mean_" + k] = float(np.mean([r[k] for r in res]))
        for k in NEUTRAL_GENES:
            rec["gene_" + k] = float(np.mean([p[k] for p in pop]))
        hist.append(rec)

        elite = [pop[i] for i in np.argsort(-sc)[:elite_n]]
        pop = [mutate(elite[i % len(elite)], cfg, rng, sigma) for i in range(n_org)]

    return {"arm": arm, "ancestor_mean": anc_mean, "history": hist,
            "final_pop": pop, "ancestor_pop": ancestor}
