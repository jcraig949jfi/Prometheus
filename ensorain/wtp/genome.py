"""World Genome (directive s2, s26, s27): a JSON-serialisable, hashable,
mutable description of a world AND its organisms. Generators: random,
grammar (toward s57 targets), local/large mutation, recombination.
Novelty descriptors for the archive."""
import copy
import hashlib
import json

import numpy as np

from .registry import REG, FIELD_OPS, VECTOR_OPS, HAZARDS, sample_params

GENERATORS = ("tt", "cp", "lowrank", "pairwise", "sparse", "spectral", "random", "sum")
GEOMETRIES = ("tensor_index", "ring", "torus", "small_world", "scale_free", "random_geometric", "erdos",
              "modular", "tree", "dag", "wormholes", "spectral_roads")
OBS = ("cell", "fiber", "marginal", "masked", "probe_only")
MEMORIES = ("none", "table", "sketch", "additive", "lowrank", "tt", "cp", "dct", "marks", "mixture")
RULES = ("sgd", "nlms", "batch_replay", "hebbian", "anti_hebbian", "evolve", "none")
POLICIES = ("random", "greedy", "eps_greedy", "novelty", "rollout", "probe_greedy", "softmax")
FORGET = ("none", "oldest", "random", "spectral_trunc", "lowest_value", "decay")
BITS = (64, 16, 8, 4, 2)


def canonical(g):
    return json.dumps(g, sort_keys=True, separators=(",", ":"), default=str)


def ghash(g):
    return hashlib.sha256(canonical({k: v for k, v in g.items() if k != "meta"}).encode()).hexdigest()[:16]


def _dims(rng):
    style = rng.choice(["few_big", "many_small", "mixed", "binary"])
    if style == "binary":
        d = int(rng.integers(6, 12))
        dims = [2] * d
    elif style == "many_small":
        d = int(rng.integers(5, 10))
        dims = [int(rng.integers(2, 5)) for _ in range(d)]
    elif style == "few_big":
        d = int(rng.integers(2, 4))
        dims = [int(rng.integers(6, 30)) for _ in range(d)]
    else:
        d = int(rng.integers(3, 7))
        dims = [int(rng.choice([2, 3, 5, 7, 11, 17, 29])) for _ in range(d)]
    while np.prod(dims) > 4096:
        i = int(np.argmax(dims))
        dims[i] = max(2, dims[i] // 2)
    while np.prod(dims) < 64:
        dims[int(rng.integers(len(dims)))] += 1
    return [int(x) for x in dims]


def _chain(rng, ops, kmax):
    k = int(rng.integers(0, kmax + 1))
    out = []
    for _ in range(k):
        oid = str(rng.choice(ops))
        out.append({"op": oid, "p": sample_params(REG[oid], rng)})
    return out


def random_genome(rng, bias=None):
    """Pure random composition across every law. `bias` (grammar mode) pushes one
    s57 special target toward an extreme; everything else stays random."""
    dims = _dims(rng)
    g = {
        "substrate": {"dims": dims, "gen": str(rng.choice(GENERATORS)), "rank": int(rng.integers(1, 6)),
                      "chain": _chain(rng, FIELD_OPS, 3), "reward_chain": _chain(rng, FIELD_OPS, 1) if rng.random() < 0.3 else []},
        "geometry": {"kind": str(rng.choice(GEOMETRIES)), "n_nodes": int(rng.integers(64, 1025)), "k": int(rng.integers(2, 7)),
                     "p": float(rng.uniform(0.01, 0.3)), "directed": float(rng.uniform(0, 0.6)),
                     "map": str(rng.choice(["random", "sorted", "blocked"]))},
        "observation": {"kind": str(rng.choice(OBS)), "mode": int(rng.integers(0, 16)), "k": int(rng.integers(1, 9)),
                        "chain": _chain(rng, VECTOR_OPS, 2), "noise_sd": float(rng.uniform(0, 0.5)),
                        "noise_dist": str(rng.choice(["normal", "laplace", "cauchy_clip"]))},
        "transition": {"drift": float(rng.choice([0, 0, rng.uniform(0, 0.5)])), "drift_period": int(rng.integers(20, 400)),
                       "basis_change_period": int(rng.choice([0, 0, rng.integers(30, 400)])),
                       "rewire_period": int(rng.choice([0, 0, rng.integers(20, 300)])), "rewire_frac": float(rng.uniform(0, 0.5)),
                       "catastrophe_rate": float(rng.choice([0, 0, rng.uniform(0, 0.02)]))},
        "irreversibility": {"oneway": float(rng.uniform(0, 0.5)), "door_close": float(rng.choice([0, 0, rng.uniform(0, 0.3)])),
                            "hazard_frac": float(rng.choice([0, 0, rng.uniform(0, 0.2)])), "hazard": str(rng.choice(HAZARDS))},
        "resource": {"energy0": float(rng.uniform(50, 400)), "metabolism": float(rng.uniform(0.1, 1.5)),
                     "gain": float(rng.uniform(0.5, 5)), "theta": float(rng.uniform(-0.5, 1.0)), "regrow": int(rng.integers(10, 800)),
                     "query_every": int(rng.choice([0, rng.integers(3, 40)])), "query_reward": float(rng.uniform(0, 10)),
                     "tol": float(rng.uniform(0.05, 0.5)),
                     "p_compute": float(np.exp(rng.uniform(np.log(1e-6), np.log(1e-2)))),
                     "p_read": float(np.exp(rng.uniform(np.log(1e-5), np.log(1e-1)))),
                     "p_write": float(np.exp(rng.uniform(np.log(1e-5), np.log(1e-1)))),
                     "p_move": float(rng.uniform(0, 1)), "p_probe": float(rng.uniform(0, 3)), "p_rollout": float(rng.uniform(0, 1))},
        "memory": {"substrate": str(rng.choice(MEMORIES)), "cap": int(np.exp(rng.uniform(np.log(16), np.log(1024)))),
                   "bits": int(rng.choice(BITS)), "forget": str(rng.choice(FORGET)), "forget_rate": float(rng.uniform(0, 0.2)),
                   "fluid": int(rng.random() < 0.15)},
        "learning": {"rule": str(rng.choice(RULES)), "lr": float(np.exp(rng.uniform(np.log(0.005), np.log(1.0)))),
                     "batch": int(rng.integers(8, 129)), "sweeps": int(rng.integers(1, 8))},
        "credit": {"delay": int(rng.choice([0, 0, rng.integers(1, 65)])), "radius": int(rng.choice([0, 0, 1, 2])),
                   "noise": float(rng.choice([0, 0, rng.uniform(0, 1)])), "sign_flip": float(rng.choice([0, 0, rng.uniform(0, 0.3)]))},
        "search": {"policy": str(rng.choice(POLICIES)), "eps": float(rng.uniform(0, 0.5)), "depth": int(rng.choice([1, 2, 3, 4])),
                   "temp": float(np.exp(rng.uniform(np.log(0.05), np.log(3))))},
        "boundary": {"n_org": int(rng.choice([1, 1, 2, 4])), "marks": str(rng.choice(["none", "private", "shared"])),
                     "mark_decay": float(rng.uniform(0, 0.05))},
        "time": {"lifetime": int(rng.integers(200, 601)), "checkpoints": 10},
        "meta": {"strategy": "random", "parents": [], "mutations": []},
    }
    if bias:
        g = apply_bias(g, bias, rng)
        g["meta"]["strategy"] = f"grammar:{bias}"
    return g


SPECIAL = ("forced_forgetting", "representation_fluidity", "credit_delay", "counterfactual_depth", "memory_compute_exchange",
           "graph_rewiring", "irreversibility", "communication_bandwidth", "world_change", "search_granularity")


def apply_bias(g, target, rng):
    g = copy.deepcopy(g)
    if target == "forced_forgetting":
        g["memory"]["forget"] = str(rng.choice(["spectral_trunc", "lowest_value", "random", "oldest"]))
        g["memory"]["forget_rate"] = float(rng.uniform(0.05, 0.4))
    elif target == "representation_fluidity":
        g["memory"]["fluid"] = 1
    elif target == "credit_delay":
        g["credit"]["delay"] = int(rng.choice([8, 16, 32, 64]))
    elif target == "counterfactual_depth":
        g["search"]["policy"] = "rollout"
        g["search"]["depth"] = int(rng.choice([1, 2, 3, 4]))
    elif target == "memory_compute_exchange":
        if rng.random() < 0.5:
            g["resource"]["p_write"], g["resource"]["p_read"], g["resource"]["p_compute"] = 0.05, 0.05, 1e-6
        else:
            g["resource"]["p_write"], g["resource"]["p_read"], g["resource"]["p_compute"] = 1e-5, 1e-5, 5e-3
    elif target == "graph_rewiring":
        g["transition"]["rewire_period"] = int(rng.integers(10, 80))
        g["transition"]["rewire_frac"] = float(rng.uniform(0.1, 0.8))
    elif target == "irreversibility":
        g["irreversibility"]["door_close"] = float(rng.uniform(0.1, 0.6))
        g["irreversibility"]["hazard_frac"] = float(rng.uniform(0.05, 0.3))
    elif target == "communication_bandwidth":
        g["boundary"]["n_org"] = int(rng.choice([2, 4]))
        g["boundary"]["marks"] = "shared"
    elif target == "world_change":
        g["transition"]["drift"] = float(rng.uniform(0.2, 0.8))
        g["transition"]["drift_period"] = int(rng.integers(20, 150))
    elif target == "search_granularity":
        g["learning"]["rule"] = "evolve"
        g["learning"]["batch"] = int(rng.choice([8, 32, 128]))
    return g


LAWS = ("substrate", "geometry", "observation", "transition", "irreversibility", "resource", "memory", "learning",
        "credit", "search", "boundary", "time")


def mutate(g, rng, scale="local"):
    """Local: re-draw 1-2 parameters inside 1-2 laws. Large: re-draw 1-3 whole laws."""
    child = copy.deepcopy(g)
    fresh = random_genome(rng)
    muts = []
    if scale == "large":
        for law in rng.choice(LAWS, size=int(rng.integers(1, 4)), replace=False):
            child[law] = fresh[law]
            muts.append(f"law:{law}")
    else:
        for law in rng.choice(LAWS, size=int(rng.integers(1, 3)), replace=False):
            keys = list(child[law].keys())
            for k in rng.choice(keys, size=min(len(keys), int(rng.integers(1, 3))), replace=False):
                child[law][k] = fresh[law][k]
                muts.append(f"{law}.{k}")
    child["meta"] = {"strategy": f"mutate:{scale}", "parents": [ghash(g)], "mutations": muts}
    return child


def recombine(g1, g2, rng):
    child = {law: copy.deepcopy((g1 if rng.random() < 0.5 else g2)[law]) for law in LAWS}
    child["meta"] = {"strategy": "recombine", "parents": [ghash(g1), ghash(g2)], "mutations": []}
    return child


def descriptor(g):
    """Coarse descriptor for novelty search (categorical + a few scalars)."""
    return [MEMORIES.index(g["memory"]["substrate"]), GEOMETRIES.index(g["geometry"]["kind"]), RULES.index(g["learning"]["rule"]),
            POLICIES.index(g["search"]["policy"]), GENERATORS.index(g["substrate"]["gen"]), len(g["substrate"]["dims"]),
            np.log10(g["memory"]["cap"]), g["transition"]["drift"] > 0, g["boundary"]["marks"] != "none",
            g["credit"]["delay"] > 0, g["irreversibility"]["door_close"] > 0, len(g["substrate"]["chain"])]
