"""WTP-03 planted controls (dev + validation only; never campaign seeds).

planted(gen, dims, rank, band): a clean, inhabitable world: the field comes from generator `gen`;
cell observations with small Gaussian noise; tensor-index geometry; static physics; no
irreversibility; an economy that cannot starve. Used to (a) choose each substrate's fixed training
recipe on dev seeds and (b) validate that the collider has teeth (V1) and does not
hallucinate (V2, V3)."""
import copy

import numpy as np

from ensorain.wtp.world import _std


def planted(gen="lowrank", dims=(10, 10, 10), rank=2, band=0.25, lifetime=2000, noise=0.05, geo="tensor_index", k=4):
    return {
        "substrate": {"dims": list(dims), "gen": gen, "rank": rank, "chain": [], "reward_chain": []},
        "geometry": {"kind": geo, "n_nodes": int(np.prod(dims)), "k": k, "p": 0.05, "directed": 0.0, "map": "random"},
        "observation": {"kind": "cell", "mode": 0, "k": 1, "chain": [], "noise_sd": noise, "noise_dist": "normal"},
        "transition": {"drift": 0.0, "drift_period": 10 ** 6, "basis_change_period": 0, "rewire_period": 0,
                       "rewire_frac": 0.0, "catastrophe_rate": 0.0},
        "irreversibility": {"oneway": 0.0, "door_close": 0.0, "hazard_frac": 0.0, "hazard": "scramble"},
        "resource": {"energy0": 1e9, "metabolism": 0.0, "gain": 1.0, "theta": 0.0, "regrow": 50, "query_every": 0,
                     "query_reward": 0.0, "tol": 0.1, "p_compute": 0.0, "p_read": 0.0, "p_write": 0.0, "p_move": 0.0,
                     "p_probe": 0.0, "p_rollout": 0.0},
        "memory": {"substrate": "additive", "cap": 0, "bits": 64, "forget": "none", "forget_rate": 0.0, "fluid": 0, "band": band},
        "learning": {"rule": "nlms", "lr": 0.5, "batch": 32, "sweeps": 1},
        "credit": {"delay": 0, "radius": 0, "noise": 0.0, "sign_flip": 0.0},
        "search": {"policy": "novelty", "eps": 0.1, "depth": 2, "temp": 1.0},
        "boundary": {"n_org": 1, "marks": "none", "mark_decay": 0.0},
        "time": {"lifetime": lifetime, "checkpoints": 10, "lifetime2": lifetime},
        "meta": {"strategy": "planted", "parents": [], "mutations": []},
    }


def additive_hook(seed):
    """Replace the field by a purely additive (main-effects) field: the planted NEGATIVE."""
    def hook(x, rew):
        rng = np.random.default_rng(seed)
        out = np.zeros(x.shape)
        for m, d in enumerate(x.shape):
            sh = [1] * x.ndim
            sh[m] = d
            out = out + rng.normal(size=d).reshape(sh)
        return _std(out), rew
    return hook


def variant(g, **kw):
    g = copy.deepcopy(g)
    for path, v in kw.items():
        a, b = path.split("__")
        g[a][b] = v
    return g
