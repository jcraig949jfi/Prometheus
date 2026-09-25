"""cw01-e03 — activation economics, and whether coalitions are CONDITIONAL.

Many affordances exist; using one costs something. Nothing rewards sparsity,
specialisation or teaming. The question is whether evolution discovers activation
that depends on WHAT ARRIVED, or merely activation that is cheap.

THE DISTINCTION THIS WORLD EXISTS TO MEASURE
  sparsity      = how few affordances fire
  conditionality = whether WHICH ones fire depends on the item
An organism that always fires the same 3 of 16 is sparse, cheap, and has learned
nothing. That outcome is deliberately REACHABLE (set all weights to 0) because it
is the honest null; engineering it away would rig the experiment.

TWO STRUCTURAL FIXES, applied at the right level this time
  1. Arms are GENOME TRANSFORMATIONS applied up front, not flags tested inside the
     loop. Every arm then runs identical code, so arms cannot diverge. e02 hit the
     same defect twice (CW01-D019, CW01-D021) because `flag and prng.random()`
     short-circuits; guarding that pattern failed. Removing the pattern does not.
  2. Activation is DETERMINISTIC given genome and observable features. There is no
     policy RNG at all, so there is no policy RNG to desynchronise.

Honest limitation: an 82-parameter linear activation policy, not a rich program.
"""
from __future__ import annotations

import math

import numpy as np

NEUTRAL_GENES = ("neutral_a", "neutral_b")


# ---------------------------------------------------------------------- genome

def seed_genome(cfg, rng):
    K = cfg["affordances"]["K"]
    F = cfg["items"]["observable_features"]
    gb = cfg["genome"]["bias_bounds"]
    wb = cfg["genome"]["weight_bounds"]
    return {
        "bias": rng.uniform(gb[0], gb[1], size=K),
        "w": rng.uniform(wb[0], wb[1], size=(K, F)),
        "neutral_a": float(rng.uniform(0, 1)),
        "neutral_b": float(rng.uniform(0, 1)),
    }


def mutate(genome, cfg, rng, sigma=0.10):
    gb = cfg["genome"]["bias_bounds"]
    wb = cfg["genome"]["weight_bounds"]
    return {
        "bias": np.clip(genome["bias"] + rng.normal(0, sigma * (gb[1] - gb[0]), genome["bias"].shape), *gb),
        "w": np.clip(genome["w"] + rng.normal(0, sigma * (wb[1] - wb[0]), genome["w"].shape), *wb),
        "neutral_a": float(np.clip(genome["neutral_a"] + rng.normal(0, sigma), 0, 1)),
        "neutral_b": float(np.clip(genome["neutral_b"] + rng.normal(0, sigma), 0, 1)),
    }


def apply_arm(genome, arm_cfg):
    """The arm is a genome transformation. After this, all arms run identical code."""
    g = {"bias": genome["bias"].copy(), "w": genome["w"].copy(),
         "neutral_a": genome["neutral_a"], "neutral_b": genome["neutral_b"]}
    if not arm_cfg.get("conditional_enabled", True):
        g["w"][:] = 0.0            # may be sparse; cannot be conditional
    return g


# ----------------------------------------------------------------- the world

def make_structure(cfg, rng):
    """Hidden structure: which affordances each latent class needs. Never readable."""
    K = cfg["affordances"]["K"]
    M = cfg["items"]["M_classes"]
    n = cfg["items"]["needs_per_class"]
    return [set(rng.choice(K, size=n, replace=False).tolist()) for _ in range(M)]


def make_items(cfg, rng, centres=None):
    """Items carry an observable feature vector correlated with a LATENT class.

    `centres` is the class -> feature-signature mapping. CW01-D029 (second half):
    drawing it from the episode rng moved class-0's centroid 1.955 apart between
    episodes, so the observable signature meant something different every time and
    routing was unlearnable even with a stable structure. Like the structure, it is
    a latent fact about the WORLD and must outlive the episode.
    """
    it = cfg["items"]
    M, F = it["M_classes"], it["observable_features"]
    n = it["items_per_episode"]
    d = it["size_distribution"]
    mu, sigma = math.log(d["median"]), d["sigma"]
    lo, hi = d["clip"]
    if centres is None:
        centres = rng.normal(0, 1, size=(M, F))
    ov = it["feature_overlap"]
    items = []
    for _ in range(n):
        m = int(rng.integers(0, M))
        x = centres[m] * (1.0 - ov) + rng.normal(0, 1, size=F) * ov
        items.append({"cls": m, "x": x,
                      "size": float(np.clip(rng.lognormal(mu, sigma), lo, hi))})
    return items


def activate(genome, x, force_all=False):
    """Deterministic. No RNG anywhere in the organism's decision."""
    if force_all:
        return np.ones(genome["bias"].shape[0], dtype=bool)
    z = genome["bias"] + genome["w"] @ x
    return z > 0.0


def run_episode(genome, cfg, arm, stream_seed, structure=None, centres=None, scramble=None,
                collect_patterns=False):
    """One organism, one episode.

    scramble: a permutation applied to the hidden structure (I1). The SHAM passes
    the identity permutation, so both arms pay identical cost and differ only in
    whether the structure still matches what evolved.
    """
    arm_cfg = cfg["arms"][arm]
    g = apply_arm(genome, arm_cfg)
    force_all = bool(arm_cfg.get("force_all", False))

    wrng = np.random.Generator(np.random.PCG64(stream_seed))
    if structure is None:
        structure = make_structure(cfg, wrng)
    items = make_items(cfg, wrng, centres=centres)

    if scramble is not None:
        structure = [structure[i] for i in scramble]

    af = cfg["affordances"]
    act_cost, base_cost = af["activation_cost"], af["base_process_cost"]
    K = af["K"]

    info = cost = 0.0
    n_act = 0
    hits = 0
    coverage_sum = 0.0
    used = np.zeros(K, dtype=int)
    classes, patterns = [], []

    for it in items:
        on = activate(g, it["x"], force_all)
        idx = set(np.flatnonzero(on).tolist())
        need = structure[it["cls"]]
        met = len(idx & need)
        cov = met / max(1, len(need))

        cost += base_cost + act_cost * len(idx)
        info += math.log2(1.0 + it["size"]) * cov

        n_act += len(idx)
        hits += met
        coverage_sum += cov
        used[list(idx)] += 1
        if collect_patterns:
            classes.append(it["cls"])
            patterns.append(int(sum(1 << i for i in idx)))

    n_items = len(items)
    m = {
        "activations_per_item": n_act / n_items,
        "sparsity": (n_act / n_items) / K,
        "distinct_affordances_used": int((used > 0).sum()),
        "routing_precision": (hits / n_act) if n_act else 0.0,
        "coverage_mean": coverage_sum / n_items,
        "info": info,
        "cost": cost,
        "score": info / cost if cost > 0 else 0.0,
    }
    if collect_patterns:
        m["_classes"], m["_patterns"] = classes, patterns
    return m


# ------------------------------------------------------------------ evolution

def attempt_structure(cfg, mkseed):
    """ONE hidden structure per attempt (CW01-D029).

    run_episode draws a structure from the stream seed when none is given, and the
    stream seed varies per organism and per generation -- so every episode faced a
    DIFFERENT world. Conditional routing would have been unlearnable in principle
    and e03 would have returned a confident NULL for an artefactual reason. The
    structure is a persistent latent fact about the world; it must outlive the
    episode, and it must be shared so organisms are actually comparable.
    """
    r = np.random.Generator(np.random.PCG64(mkseed(cfg["attempt_id"], "structure", 0)))
    return make_structure(cfg, r)


def attempt_centres(cfg, mkseed):
    """ONE class -> feature-signature mapping per attempt (CW01-D029, second half)."""
    r = np.random.Generator(np.random.PCG64(mkseed(cfg["attempt_id"], "centres", 0)))
    return r.normal(0, 1, size=(cfg["items"]["M_classes"], cfg["items"]["observable_features"]))


def evolve(cfg, arm, generations, n_org, mkseed, structure=None, centres=None):
    aid = cfg["attempt_id"]
    if structure is None:
        structure = attempt_structure(cfg, mkseed)
    if centres is None:
        centres = attempt_centres(cfg, mkseed)
    rng = np.random.Generator(np.random.PCG64(mkseed(aid, "evo|" + arm, 0)))
    pop = [seed_genome(cfg, rng) for _ in range(n_org)]
    ancestor = [dict(p) for p in pop]

    def ep(gm, tag, i):
        # stream_seed is arm-INDEPENDENT: matched worlds across arms (CW01-D010).
        # structure and centres are attempt-stable: the world's latent facts outlive
        # the episode and are shared across organisms (CW01-D029).
        return run_episode(gm, cfg, arm, mkseed(aid, "stream|" + tag, i),
                           structure=structure, centres=centres)

    anc_mean = float(np.mean([ep(p, "anc", i)["score"] for i, p in enumerate(ancestor)]))
    elite_n = max(2, int(n_org * cfg["population"]["elite_fraction"]))
    sigma = cfg["population"]["mutation_sigma"]
    hist = []

    for gen in range(generations):
        res = [ep(p, "g" + str(gen), i) for i, p in enumerate(pop)]
        sc = np.array([r["score"] for r in res])
        rec = {"gen": gen, "mean": float(sc.mean()), "best": float(sc.max()),
               "ancestor_relative": float(sc.mean() - anc_mean)}
        for k in ("sparsity", "routing_precision", "coverage_mean",
                  "activations_per_item", "distinct_affordances_used", "cost", "info"):
            rec["mean_" + k] = float(np.mean([r[k] for r in res]))
        rec["gene_neutral_a"] = float(np.mean([p["neutral_a"] for p in pop]))
        rec["gene_neutral_b"] = float(np.mean([p["neutral_b"] for p in pop]))
        rec["mean_abs_weight"] = float(np.mean([np.abs(p["w"]).mean() for p in pop]))
        hist.append(rec)

        elite = [pop[i] for i in np.argsort(-sc)[:elite_n]]
        pop = [mutate(elite[i % len(elite)], cfg, rng, sigma) for i in range(n_org)]

    return {"arm": arm, "ancestor_mean": anc_mean, "history": hist,
            "final_pop": pop, "ancestor_pop": ancestor}
