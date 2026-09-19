"""Nestor evolver for the cw01-arch4 descendants (P-E03, P-E09): mutation-only births under the
frozen grammar, W2_K2 reward, individuals carry their ancestor (an init individual = a depth-16
walker of a viable parent). Arms: 'select' (tournament 3), 'drift' (uniform parent choice; the
same draws are made), 'weather' (each birth is evaluated on a COPY that lost 2 random
instructions with probability .5 - computational weather, the genome itself is inherited intact),
'sham' (the weather draws are made and nothing is applied). Every rng draw is unconditional so
arms share streams. Computational scope: integer programs on a bounded VM."""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common as CM            # noqa: E402
A = CM.A
sys.path.insert(0, str(HERE / "P-D01"))
from run_PD01 import damage, windows, reduced_class   # noqa: E402

ENV = "W2_K2"
N, G, K_T = 96, 60, 3
HELD = A.with_knobs(A.WorldSpec("W1_d1", delay=1, value_bits=4), name="W1_d1")


def init_population():
    """Two depth-16 walkers per viable parent (walkers 1 and 2), canonicalised; padded to N with walker 3."""
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    pop = []
    for w in (1, 2, 3):
        for p in parents:
            if len(pop) >= N:
                break
            wk = A.C5.walk(p["manifest"], p["organism_id"], w, A.episodes(p["env"]), 16, 32)
            pop.append({"m": A.canonical(wk["archived"].get(wk["depth"])), "anc": len(pop), "anc_parent": p["organism_id"], "anc_stratum": p["stratum"], "anc_walker": w})
        if len(pop) >= N:
            break
    parent_m = {p["organism_id"]: A.canonical(p["manifest"]) for p in parents}
    return pop[:N], parent_m


def gen_eps(g):
    return A.episodes_for(A.ENVS[ENV], A.CAMPAIGN_SEED, "train", 1000 + g, A.C1.E)


def blind_delete(m, rng, k=2):
    c = json.loads(json.dumps(m))
    n = len(c["genome"]) // A.IW
    if n <= k:
        return c
    idx = set()
    while len(idx) < k:
        idx.add(int(rng.next_u32() % n))
    c["genome"] = [x for i, x in enumerate(c["genome"]) if (i // A.IW) not in idx]
    return c


def fitness(ind, eps, arm, rng):
    m = ind["m"]
    u = rng.unit()                                  # weather coin: drawn in EVERY arm
    d = blind_delete(m, rng)                        # deletion positions: drawn in EVERY arm
    target = d if (arm == "weather" and u < 0.5) else m
    ev = A.evaluate(target, eps, rng_seed=0, reward_mode="per_ask")
    return ev


def run(arm, seed, init, G_=G, N_=N, env=ENV, ep_transform=None, price=0.0, archive_gens=(), label="nestor.evolver"):
    """arm: select | drift (uniform parent) | ndrift (uniform parent, child kept only inside the band of its
    parent's reward - competence retained without a fitness ordering) | weather | sham.
    env: selection world; ep_transform(eps, g) may rewrite the generation's episodes (idle ticks);
    price: fitness = reward - price * n_instr for the tournament; archive_gens: snapshot generations."""
    rng = A.SplitMix64(A.seed_from(label, A.LOOP_SEED, seed))      # arm-independent: arms share every draw (CW01-D083)
    pop = [dict(x) for x in init]
    hist, archive = [], {}
    for g in range(G_):
        eps = A.episodes_for(A.ENVS[env], A.CAMPAIGN_SEED, "train", 1000 + g, A.C1.E)
        if ep_transform is not None:
            eps = ep_transform(eps, g)
        evs = [fitness(ind, eps, arm, rng) for ind in pop]
        pr = price(g) if callable(price) else price                 # a price may be a schedule over generations
        fit = np.array([e["reward_per_ask"] - pr * CM.n_instr(ind["m"]) for e, ind in zip(evs, pop)])
        if g in archive_gens:
            archive[g] = [dict(x, reward=float(e["reward_per_ask"])) for x, e in zip(pop, evs)]
        hist.append({"gen": g, "reward_mean": float(fit.mean()), "reward_max": float(fit.max()),
                     "len_mean": float(np.mean([CM.n_instr(x["m"]) for x in pop])),
                     "persist": {k: sum(1 for x in pop if x["m"]["persist"] == k) / len(pop) for k in ("none", "regs", "tape", "all")},
                     "tape_writes": float(np.mean([e["tape_writes_per_episode"] for e in evs])),
                     "persistent_words": float(np.mean([e["meter"].get("persistent_state_words", 0) for e in evs])),
                     "occupancy": float(np.mean([e["tape_occupancy_max"] for e in evs])),
                     "answered": float(np.mean([e["answered_share"] for e in evs])),
                     "n_ancestors": len({x["anc"] for x in pop})})
        kids = []
        for i in range(N_):
            cand = [int(rng.next_u32() % N_) for _ in range(K_T)]        # drawn in every arm
            if arm in ("drift", "ndrift"):
                pi = cand[0]
            else:
                pi = max(cand, key=lambda c: fit[c])
            parent = pop[pi]
            child = None
            for _try in range(8):
                try:
                    child, rec = A.GR.mutate(parent["m"], rng, mate=None, name=None)
                    break
                except A.ManifestError:
                    continue
            if child is None:
                child = json.loads(json.dumps(parent["m"]))
            if arm == "ndrift":                                            # neutral-band acceptance relative to the PARENT
                rc = A.evaluate(child, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
                if abs(rc - evs[pi]["reward_per_ask"]) > A.C1.BAND:
                    child = json.loads(json.dumps(parent["m"]))
            kids.append({"m": child, "anc": parent["anc"], "anc_parent": parent.get("anc_parent"), "anc_stratum": parent.get("anc_stratum"), "anc_walker": parent.get("anc_walker")})
        pop = kids
    fixed = A.episodes(env)
    final = [dict(x, reward=A.evaluate(x["m"], fixed, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]) for x in pop]
    return {"arm": arm, "seed": seed, "env": env, "price": (price if not callable(price) else "schedule"), "history": hist, "final": final, "archive": archive}


ASSAY_CELLS = [("delete", 2, 1), ("delete", 4, 1), ("delete", 4, 4), ("operand", 4, 1), ("opcode", 4, 1)]


def mean_or_none(xs):
    xs = [x for x in xs if x is not None and np.isfinite(x)]
    return float(np.mean(xs)) if xs else None


def assay(m, tag, draws=4):
    """P-D01 damage cells on W2_K2 (loss, displacement) and W1_d1 (reward change); modulo decode."""
    eps = {ENV: A.episodes(ENV), "HELD": A.episodes_for(HELD, A.CAMPAIGN_SEED, "train", 1, A.C1.E)}
    pm = A.canonical(m)
    pev = A.eval_all(pm, eps)
    n = CM.n_instr(pm)
    rows = []
    for kind, k, s in ASSAY_CELLS:
        if k >= n:
            continue
        for d in range(1, draws + 1):
            rng = A.SplitMix64(A.seed_from("nestor.evolver.assay", A.LOOP_SEED, tag, kind, k, s, d))
            wins = windows(n, k, s, "even", rng)
            child = damage(pm, kind, wins, rng, "modulo")
            cev = A.eval_all(child, eps)
            disp = A.C1.displacement(cev[ENV]["_answers"], pev[ENV]["_answers"])
            D = reduced_class(cev, pev, disp, ENV)
            rows.append({"kind": kind, "k": k, "s": s, "draw": d, "D": D, "loss": int(D in ("D2", "D3")), "disp": disp, "held_delta": cev["HELD"]["reward_per_ask"] - pev["HELD"]["reward_per_ask"]})
    return {"degenerate": bool(pev[ENV]["answered_share"] == 0.0), "r0": pev[ENV]["reward_per_ask"], "n_instr": n, "persist": pm["persist"],
            "persistent_words": pev[ENV]["meter"].get("persistent_state_words", 0), "tape_writes": pev[ENV]["tape_writes_per_episode"],
            "loss": float(np.mean([r["loss"] for r in rows])) if rows else None, "disp": float(np.mean([r["disp"] for r in rows])) if rows else None,
            "held_delta": float(np.mean([r["held_delta"] for r in rows])) if rows else None, "n_rows": len(rows), "rows": rows}
