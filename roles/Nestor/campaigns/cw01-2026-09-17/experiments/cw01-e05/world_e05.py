"""cw01-e05 — composition economics, and whether a mixture EXCEEDS its parts.

Components are individually weak. Conjunctive items yield value only when ALL
required capabilities are present, so a lone component is worth little and a
complementary set is worth a great deal. Nothing rewards carrying more, being
diverse, or being complementary: the world prices inclusion and defines when value
accrues.

THE DISTINCTION THIS WORLD EXISTS TO MEASURE
  mixture value       what the evolved set actually scores
  additive prediction the sum of what its members are worth ALONE
  superadditivity     the difference
A set of weak specialists that each handle their own share independently is a
PARTITION, and its value is the sum of its members. That outcome is deliberately
REACHABLE - carrying one component, none, or all are all inside the search space -
because it is the honest null.

CRITICAL: the additive prediction is MEASURED by running each component alone in
the same world. Computing it from a formula would make superadditivity a definition
rather than a measurement.

CW01-D037: the first version drew items ONCE per attempt, so every organism scored
a single exact number with zero variance. That had two consequences - the sham-vs-
sham noise floor (D035) could not be built at all, silently disabling a gate; and
evolution optimised against one frozen 120-item list. Now the demand STRUCTURE is
attempt-stable (capability assignment and a pool of demand templates) while the
items themselves are drawn PER EPISODE from that pool. Structure stays learnable
(D029); variation returns.

Structural fixes carried forward: arms are transformations applied up front so all
arms run identical code (D019/D021); the organism's decision is deterministic given
its genome; latent facts are attempt-stable.

Honest limitation: an 8-gene inclusion vector, not a rich program.
"""
from __future__ import annotations

import math

import numpy as np

NEUTRAL_GENES = ("neutral_a", "neutral_b")


# ---------------------------------------------------------------- latent facts

def attempt_capabilities(cfg, mkseed):
    """component -> capability. ONE assignment per attempt (CW01-D029)."""
    K = cfg["components"]["K"]
    r = np.random.Generator(np.random.PCG64(mkseed(cfg["attempt_id"], "capmap", 0)))
    return list(int(x) for x in r.permutation(K))


def attempt_item_pool(cfg, mkseed, conj_fraction=None, n_templates=48):
    """The DEMAND STRUCTURE: a pool of templates, attempt-stable.

    Which items arrive varies per episode; what kinds of demand exist does not.
    """
    it = cfg["items"]
    K = cfg["components"]["K"]
    cf = it["conjunctive_fraction"] if conj_fraction is None else conj_fraction
    r = np.random.Generator(np.random.PCG64(mkseed(cfg["attempt_id"], "itempool", 0)))
    pool = []
    for _ in range(n_templates):
        conj = bool(r.random() < cf)
        n_lo, n_hi = it["required_capabilities"]["conjunctive" if conj else "disjunctive"]
        n = int(r.integers(n_lo, n_hi + 1))
        pool.append({"conj": conj, "need": set(int(c) for c in r.choice(K, size=n, replace=False))})
    return pool


def make_items(cfg, rng, pool):
    """PER EPISODE: sample which templates arrive and their values (CW01-D037)."""
    it = cfg["items"]
    lo, hi = it["value_range"]
    idx = rng.integers(0, len(pool), size=it["items_per_episode"])
    return [{"conj": pool[i]["conj"], "need": pool[i]["need"], "value": float(rng.uniform(lo, hi))}
            for i in idx]


# ---------------------------------------------------------------------- genome

def seed_genome(cfg, rng):
    K = cfg["components"]["K"]
    lo, hi = cfg["genome"]["inclusion_bounds"]
    return {"incl": rng.uniform(lo, hi, size=K),
            "neutral_a": float(rng.uniform(0, 1)), "neutral_b": float(rng.uniform(0, 1))}


def mutate(genome, cfg, rng, sigma=0.12):
    lo, hi = cfg["genome"]["inclusion_bounds"]
    return {"incl": np.clip(genome["incl"] + rng.normal(0, sigma * (hi - lo), genome["incl"].shape), lo, hi),
            "neutral_a": float(np.clip(genome["neutral_a"] + rng.normal(0, sigma), 0, 1)),
            "neutral_b": float(np.clip(genome["neutral_b"] + rng.normal(0, sigma), 0, 1))}


def carried(genome, arm_cfg):
    """Which components are carried, after the arm transformation. No RNG."""
    on = [i for i, v in enumerate(genome["incl"]) if v > 0.0]
    cap = arm_cfg.get("max_components")
    if cap is not None and len(on) > cap:
        on = sorted(on, key=lambda i: -genome["incl"][i])[:cap]
    return sorted(on)


def genome_with(cfg, components):
    """A hand-built genome carrying exactly `components`."""
    K = cfg["components"]["K"]
    v = np.full(K, -0.5)
    for c in components:
        v[c] = 0.9
    return {"incl": v, "neutral_a": 0.5, "neutral_b": 0.5}


# ----------------------------------------------------------------------- world

def run_episode(genome, cfg, arm, stream_seed, pool, capmap,
                force_disjunctive=False, drop=None, scramble=None):
    """One organism, one episode. Items drawn from the attempt-stable pool.

    drop              remove a component after the arm transformation (M1)
    force_disjunctive every item needs ANY rather than ALL (M3)
    scramble          permute component -> capability (M2); None or identity is the sham
    """
    arm_cfg = cfg["arms"][arm]
    on = carried(genome, arm_cfg)
    if drop is not None and drop in on:
        on = [c for c in on if c != drop]
    cm = capmap if scramble is None else [capmap[i] for i in scramble]
    caps = set(cm[c] for c in on)

    conj_on = arm_cfg.get("conjunctive_enabled", True) and not force_disjunctive
    cc = cfg["components"]["cost_carry_per_episode"]
    ca = cfg["items"]["cost_attempt"]

    rng = np.random.Generator(np.random.PCG64(stream_seed))
    items = make_items(cfg, rng, pool)

    cost = cc * len(on)
    info = 0.0
    m = dict(components_carried=len(on), carry_cost=cc * len(on),
             conjunctive_satisfied=0, disjunctive_satisfied=0,
             conjunctive_seen=0, disjunctive_seen=0, items_attempted=0)

    for it in items:
        m["items_attempted"] += 1
        cost += ca
        need = it["need"]
        if it["conj"] and conj_on:
            m["conjunctive_seen"] += 1
            ok = need.issubset(caps)
            if ok:
                m["conjunctive_satisfied"] += 1
        else:
            m["disjunctive_seen"] += 1
            ok = bool(need & caps)
            if ok:
                m["disjunctive_satisfied"] += 1
        if ok:
            info += math.log2(1.0 + it["value"])

    m["info"], m["cost"] = info, cost
    m["score"] = info / cost if cost > 0 else 0.0
    return m


def mean_metric(genome, cfg, arm, pool, capmap, mkseed, aid, tag, n=16, key="score", **kw):
    """Average one metric over n independent episodes.

    The spread across blocks is the noise floor (CW01-D035/D037).
    """
    return float(np.mean([run_episode(genome, cfg, arm, mkseed(aid, "stream|" + tag, i),
                                      pool, capmap, **kw)[key] for i in range(n)]))


def mean_score(genome, cfg, arm, pool, capmap, mkseed, aid, tag, n=16, **kw):
    return mean_metric(genome, cfg, arm, pool, capmap, mkseed, aid, tag, n, key="score", **kw)


def mean_info(genome, cfg, arm, pool, capmap, mkseed, aid, tag, n=16, **kw):
    """CW01-D038(b): superadditivity is defined on INFORMATION, not on info/cost.

    Every organism pays the same item-attempt floor (0.5 x 120 = 60.0) regardless of
    what it carries. Summing solo SURPLUSES of a ratio therefore double-counts that
    floor's dilution and inflates the additive prediction, making any real mixture
    look sub-additive. Information composes linearly; cost is reported separately.
    """
    return mean_metric(genome, cfg, arm, pool, capmap, mkseed, aid, tag, n, key="info", **kw)


# --------------------------------------------------- superadditivity machinery

def solo_values(cfg, arm, pool, capmap, components, mkseed, aid, tag="solo", n=16, **kw):
    """MEASURED solo information of each component: run it ALONE. Never inferred.

    CW01-D038(a): **kw MUST reach here. The first version applied an intervention
    (force_disjunctive) to the mixture but NOT to its own baseline, so the mixture was
    measured under one composition law and the solo values under another. The M3
    verdict that produced (+1.8330 vs -0.2184) compared two different worlds.
    """
    empty = mean_info(genome_with(cfg, []), cfg, arm, pool, capmap, mkseed, aid, tag, n, **kw)
    out = {}
    for c in components:
        out[c] = mean_info(genome_with(cfg, [c]), cfg, arm, pool, capmap,
                           mkseed, aid, tag, n, **kw) - empty
    return out, empty


def superadditivity(cfg, arm, pool, capmap, genome, mkseed, aid, tag="sa", n=16, **kw):
    """Mixture INFORMATION minus the MEASURED additive prediction.

    Both the mixture and every solo baseline are measured under the SAME conditions,
    including any intervention in **kw (CW01-D038a). Defined on information, which
    composes linearly, rather than on info/cost (CW01-D038b). Cost is reported
    alongside so the trade stays visible without contaminating the arithmetic.
    """
    on = carried(genome, cfg["arms"][arm])
    mix = mean_info(genome, cfg, arm, pool, capmap, mkseed, aid, tag, n, **kw)
    solos, empty = solo_values(cfg, arm, pool, capmap, on, mkseed, aid, tag, n, **kw)
    additive = empty + sum(solos.values())
    return {"mixture_info": mix, "additive_prediction": additive,
            "superadditivity": mix - additive, "empty_baseline": empty,
            "solo_values": solos, "carried": on,
            "mixture_score": mean_score(genome, cfg, arm, pool, capmap, mkseed, aid, tag, n, **kw),
            "carry_cost": cfg["components"]["cost_carry_per_episode"] * len(on)}


def ablation_profile(cfg, arm, pool, capmap, genome, mkseed, aid, tag="abl", n=16, **kw):
    """Per component: what removing it costs, versus what it is worth alone.

    On INFORMATION, and with **kw reaching the baselines, for the same two reasons
    as superadditivity (CW01-D038). Removing a component also removes its carry cost,
    so a ratio would reward ablation for free.
    """
    on = carried(genome, cfg["arms"][arm])
    mix = mean_info(genome, cfg, arm, pool, capmap, mkseed, aid, tag, n, **kw)
    solos, _ = solo_values(cfg, arm, pool, capmap, on, mkseed, aid, tag, n, **kw)
    prof = {}
    for c in on:
        without = mean_info(genome, cfg, arm, pool, capmap, mkseed, aid, tag, n, drop=c, **kw)
        prof[c] = {"ablation_cost": mix - without, "solo_value": solos[c],
                   "load_bearing": (mix - without) > solos[c]}
    return {"mixture_info": mix, "profile": prof,
            "n_load_bearing": sum(1 for v in prof.values() if v["load_bearing"]),
            "n_carried": len(on)}


def score_blocks(genome, cfg, arm, pool, capmap, mkseed, aid, n_blocks=10, per=16, **kw):
    """Independent estimates of the SAME quantity: the sham-vs-sham noise floor (D035)."""
    return [mean_score(genome, cfg, arm, pool, capmap, mkseed, aid, "nf%d" % b, per, **kw)
            for b in range(n_blocks)]


# ------------------------------------------------------------------- evolution

def evolve(cfg, arm, generations, n_org, mkseed, pool=None, capmap=None, n_eval=4):
    aid = cfg["attempt_id"]
    if capmap is None:
        capmap = attempt_capabilities(cfg, mkseed)
    if pool is None:
        pool = attempt_item_pool(cfg, mkseed)
    rng = np.random.Generator(np.random.PCG64(mkseed(aid, "evo|" + arm, 0)))
    pop = [seed_genome(cfg, rng) for _ in range(n_org)]
    ancestor = [dict(p) for p in pop]

    def ev(g, tag, i):
        return [run_episode(g, cfg, arm, mkseed(aid, "stream|%s|%d" % (tag, i), j), pool, capmap)
                for j in range(n_eval)]

    anc_mean = float(np.mean([np.mean([r["score"] for r in ev(p, "anc", i)])
                              for i, p in enumerate(ancestor)]))
    elite_n = max(2, int(n_org * cfg["population"]["elite_fraction"]))
    sigma = cfg["population"]["mutation_sigma"]
    hist = []

    for gen in range(generations):
        res = [ev(p, "g%d" % gen, i) for i, p in enumerate(pop)]
        sc = np.array([np.mean([r["score"] for r in rr]) for rr in res])
        flat = [r for rr in res for r in rr]
        rec = {"gen": gen, "mean": float(sc.mean()), "best": float(sc.max()),
               "ancestor_relative": float(sc.mean() - anc_mean)}
        for k in ("components_carried", "carry_cost", "conjunctive_satisfied",
                  "disjunctive_satisfied", "cost", "info"):
            rec["mean_" + k] = float(np.mean([r[k] for r in flat]))
        for k in NEUTRAL_GENES:
            rec["gene_" + k] = float(np.mean([p[k] for p in pop]))
        hist.append(rec)

        elite = [pop[i] for i in np.argsort(-sc)[:elite_n]]
        pop = [mutate(elite[i % len(elite)], cfg, rng, sigma) for i in range(n_org)]

    return {"arm": arm, "ancestor_mean": anc_mean, "history": hist,
            "final_pop": pop, "ancestor_pop": ancestor, "pool": pool, "capmap": capmap}
