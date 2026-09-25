"""Paired replicate block on the attributed core: all arms stepped in lockstep on one inflow stream, one base environment stream and one
schedule. Stream labels are parameters, so the same runner replays ENVGATE-01 worlds (labels 'envgate.*') and runs ENVGATE-02 ('envgate2.*')."""
from __future__ import annotations

import hashlib
import time
from collections import Counter

from proteus.foundry.prng import SplitMix64, seed_from
from archaeon.z80atlas.grammar import FROZEN as F
from archaeon.envgate import mechanism as M1
from archaeon.envgate.engine import EnvStream
from archaeon.envgate.ruler import measure, HIT
from archaeon.lineage.core import World, Memo, N, G, PERSIST, ORIGIN_INFLOW


def inflow(label: str, block: int):
    r = SplitMix64(seed_from(label + ".inflow", block))
    while True:
        yield bytes(r.randbelow(256) for _ in range(G))


class Env(EnvStream):
    def __init__(self, label: str, block: int):
        super().__init__(block); self.label = label

    def words(self, cell, epoch):
        if epoch != self.epoch: self.epoch = epoch; self.cache = {}
        w = self.cache.get(cell)
        if w is None:
            r = SplitMix64(seed_from(self.label + ".env", self.block, cell, epoch)); w = [(r.next_u32(), r.next_u32()) for _ in range(F["cases_per_opportunity"])]
            self.cache[cell] = w
        return w


def transform_inputs(env: Env, arm: dict):
    def f(world, cell, epoch):
        return [(M1.transform(arm, u, v),) for u, v in env.words(cell, epoch)]
    return f


def run_block(label: str, block: int, schedule: dict, arms: dict, until_epoch: int = None, keep_worlds: bool = False, tapes=None, origin=ORIGIN_INFLOW) -> dict:
    """arms: name -> arm dict ({'blocked', 'pool', '_bset'} as envgate.mechanism). Returns per-arm genetic + parent-chain results."""
    K = schedule["K_chambers"]; dwell = schedule["dwell"]; E_in = schedule["refills"] * dwell; E = E_in + PERSIST + 1
    if until_epoch is not None: E = min(E, until_epoch)
    memo = Memo(True); env = Env(label, block); stream = tapes if tapes is not None else inflow(label, block)
    worlds = {a: World(a, K, (label + ".world", block), (label + ".mutation", block), transform_inputs(env, arm)) for a, arm in arms.items()}
    pair = {a: hashlib.sha256() for a in arms}; hits = {}; ruler = Counter(); arrival = 0; t0 = time.time()
    for epoch in range(E):
        if epoch < E_in and epoch % dwell == 0:
            for c in range(K):
                t = next(stream); rv = measure(t, memo); ruler[rv["class"]] += 1
                if rv["class"] in HIT: hits[arrival] = dict(rv, tape=t.hex(), epoch_in=epoch)
                for a, w in worlds.items():
                    w.arrive(N + c, t, arrival, epoch, origin); pair[a].update(arrival.to_bytes(8, "big") + epoch.to_bytes(8, "big") + t)
                arrival += 1
        if epoch == E_in:
            for w in worlds.values(): w.clear_chambers(epoch)
        for w in worlds.values(): w.step(epoch, memo)
    out = {"label": label, "block": block, "schedule": schedule, "epochs": E, "arrivals": arrival, "ruler_counts": dict(ruler), "hits": hits,
           "pairing_sha256": {a: h.hexdigest() for a, h in pair.items()}, "wall_s": round(time.time() - t0, 1), "arms": {}}
    for a, w in worlds.items():
        est = set(w.genetic_establishments())
        out["arms"][a] = {"parent_chain_established_arrivals": w.parent_chain_establishments(), "genetic_established": sorted(est), "births": w.births,
                          "births_by_mechanism": dict(w.births_mech), "taint_calls": w.taint_calls, "fast_calls": w.fast_calls,
                          "final_ecology_pop": sum(1 for i in range(N) if w.genomes[i] is not None), "telemetry": w.telemetry,
                          "glins": {g: summarize(w, g, hits) for g, st in w.gl.items() if st["births"] >= 3 or g in est},
                          "events_sample": w.events[:400]}
        if keep_worlds: out["arms"][a]["_world"] = w
    return out


def summarize(w: World, g: int, hits: dict) -> dict:
    st = w.gl[g]; arr = st.get("arrival")
    d = {k: st[k] for k in ("root", "origin", "inserted", "epoch", "births", "births_hosted", "births_self", "exact", "peak", "max_ggen", "root_end",
                             "alive_at_check", "last_alive", "first_birth_epoch", "first_birth_input") if k in st}
    d.update({"first_birth_mech": st.get("first_birth_mech"), "arrival": arr, "ruler_class": (hits.get(arr) or {}).get("class", "NON_HIT") if arr is not None else None,
              "ruler_exact_inputs": (hits.get(arr) or {}).get("exact_inputs", []) if arr is not None else None, "tape": st.get("tape"),
              "parents": st.get("parents"), "executor_glin": st.get("executor_glin"), "hosts": dict(sorted(st["hosts"].items(), key=lambda kv: -kv[1])[:10]),
              "n_hosts": len(st["hosts"]), "traj": st["traj"][:80]})
    return d
