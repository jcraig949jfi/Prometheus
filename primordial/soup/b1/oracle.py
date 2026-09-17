"""Oracle: a form is the SAME world iff every sampled episode's trace hash (and obs
hash) equals the wforge Encounter's. Zero tolerance.

usage: python -m primordial.soup.b1.oracle --form np --worlds 40 --envs 12 [--cheat skip_lin]
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np

from .common import action_tensor, episode_seeds, hash_obs, make_world, reference

FORMS = {}


def form_np(mech, wid, seeds, acts, cheat):
    from .np_world import NpEncounter
    n = len(seeds)
    w = NpEncounter(mech, wid, record=np.arange(n), cheat=cheat)
    T = mech.horizon
    obs_log = np.zeros((T, n, mech.n_slots, len(mech.obs_perm)), dtype=np.int64)
    obs_log[0] = w.reset(seeds)
    for t in range(T):
        o, _, done = w.step(acts[t])
        if t + 1 < T:
            obs_log[t + 1] = o
        if done.all():
            break
    th = [h.decode() for h in w.trace_hashes()]
    oh = [hash_obs(obs_log[:, e], int(w.done_tick[e])) for e in range(n)]
    return th, oh


FORMS["np"] = form_np


def form_nb(mech, wid, seeds, acts, cheat):
    from .nb_world import NbEncounter
    w = NbEncounter(mech, wid, cheat=cheat)
    w.prepare(seeds, log=True)
    w.run(acts)
    return [h.decode() for h in w.trace_hashes()], None


FORMS["nb"] = form_nb


def _lua_form(k_per_call):
    def form_lua(mech, wid, seeds, acts, cheat):
        from .lua_world import LuaEncounter
        w = LuaEncounter(mech, wid, cheat=cheat)
        w.prepare(seeds)
        log = w.run(acts, k=k_per_call or mech.horizon, record=True)
        return [h.decode() for h in w.trace_hashes(log)], None
    return form_lua


FORMS["lua1"] = _lua_form(1)
FORMS["luak"] = _lua_form(0)


def form_fk(mech, wid, seeds, acts, cheat):
    from .falkor_world import FalkorEncounter
    w = FalkorEncounter(mech, wid, cheat=cheat)
    w.prepare(seeds)
    return [h.decode() for h in w.trace_hashes(w.run(acts, record=True))], None


FORMS["fk"] = form_fk


def run(form: str, worlds: int, envs: int, cheat: str = "", world_base: int = 0) -> dict:
    rows = []
    for g in range(world_base, world_base + worlds):
        mech, wid = make_world(g)
        seeds = episode_seeds(envs, base=7000 + g)
        acts = action_tensor(mech, envs, seed=g)
        th, oh = FORMS[form](mech, wid, seeds, acts, cheat)
        for e in range(envs):
            rt, ro = reference(mech, wid, int(seeds[e]), acts[:, e], with_obs=oh is not None)
            rows.append({"world_seed": g, "world_id": wid, "episode_seed": int(seeds[e]),
                         "trace_eq": th[e] == rt, "obs_eq": None if oh is None else oh[e] == ro,
                         "n_slots": mech.n_slots, "delay": mech.delay, "stoch": mech.stoch_rate,
                         "regime": mech.regime_period, "corrupt": mech.corrupt_rate,
                         "obs_delay": mech.obs_delay})
    n = len(rows)
    return {"form": form, "cheat": cheat or None, "episodes": n,
            "trace_eq": sum(r["trace_eq"] for r in rows),
            "obs_eq": None if rows and rows[0]["obs_eq"] is None else sum(r["obs_eq"] for r in rows),
            "rows": rows}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--form", default="np")
    ap.add_argument("--worlds", type=int, default=40)
    ap.add_argument("--envs", type=int, default=12)
    ap.add_argument("--cheat", default="")
    ap.add_argument("--out", default="")
    a = ap.parse_args(argv)
    res = run(a.form, a.worlds, a.envs, a.cheat)
    fails = [r for r in res["rows"] if not (r["trace_eq"] and r["obs_eq"] is not False)]
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}))
    for r in fails[:8]:
        print("FAIL", r)
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
            for r in res["rows"]:
                fh.write(json.dumps({"form": a.form, "cheat": a.cheat or None, **r}, sort_keys=True) + "\n")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
