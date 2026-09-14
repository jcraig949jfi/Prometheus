"""B1t: WHERE do the fix_unaffordable blind spots come from? Measure landing ticks directly.

For every episode, step the honest numpy form (== wforge, B1) and, before each tick t,
flag each live in-episode slot whose nonzero action costs more than its charge (an
"unpaid" action). Its writes land at tick t + delay, and they are inside the recorded
trace iff t + delay < episode end tick. The cheat form drops exactly those writes and
never touches charge, so:

  detected  = honest trace hash != fix_unaffordable trace hash
  classes for exercised episodes (>= 1 unpaid action while live):
    detected                         expected when >= 1 write lands in-episode
    missed_all_after_end             every unpaid write lands at/after the end tick
    missed_in_episode_absorbed       >= 1 lands in-episode yet the trace is unchanged
    anomaly_detected_no_landing      detected with NO in-episode landing (must be 0)

Sources: (a) E4b's saved fix_unaffordable elites (pm-data/E, read-only), seeds 9100..9107,
elite-level detection = any of its 8 episodes detected (E's oracle rule); (b) the B1s
configuration (60 worlds x 16 seeds, same actions as sensitivity.py).

usage: python -m primordial.soup.b1.landing --out rows.jsonl
"""
from __future__ import annotations

import argparse
import json
import pathlib
from collections import Counter

import numpy as np

from .common import action_tensor, episode_seeds, make_world
from .np_world import NpEncounter

E4B = pathlib.Path("C:/Users/jcrai/lab/pm-data/E/E4b-qd-encounter-archive-positive")
E_SEEDS = np.arange(9100, 9108, dtype=np.int64)


def analyse(mech, wid, seeds, acts_env_first):
    """acts_env_first: int32 [n, T, S, W]. Returns per-episode dicts."""
    n = len(seeds)
    acts = np.ascontiguousarray(acts_env_first.transpose(1, 0, 2, 3)).astype(np.int32)   # [T, n, S, W]
    hon = NpEncounter(mech, wid, record=np.arange(n), with_obs=False)
    che = NpEncounter(mech, wid, record=np.arange(n), with_obs=False, cheat="fix_unaffordable")
    hon.reset(seeds)
    che.reset(seeds)
    unpaid_ticks = [[] for _ in range(n)]
    for t in range(mech.horizon):
        cost = (acts[t].astype(np.int64) % 8).sum(-1) * mech.act_cost          # [n, S]
        flag = (hon.alive & (cost > hon.charge) & (cost > 0)).any(1) & ~hon.done
        for e in np.nonzero(flag)[0]:
            unpaid_ticks[e].append(t)
        hon.step(acts[t])
        che.step(acts[t])
        if hon.done.all() and che.done.all():
            break
    hh = hon.trace_hashes()
    ch = che.trace_hashes()
    out = []
    for e in range(n):
        end = int(hon.done_tick[e])
        lands = [t + mech.delay for t in unpaid_ticks[e]]
        in_ep = sum(L < end for L in lands)
        det = hh[e] != ch[e]
        if not lands:
            cls = "not_exercised" if not det else "anomaly_detected_not_exercised"
        elif det:
            cls = "detected" if in_ep else "anomaly_detected_no_landing"
        else:
            cls = "missed_all_after_end" if in_ep == 0 else "missed_in_episode_absorbed"
        out.append({"episode": e, "seed": int(seeds[e]), "end_tick": end, "unpaid_ticks": len(lands),
                    "landings_in_episode": int(in_ep), "landings_after_end": len(lands) - int(in_ep),
                    "last_unpaid_tick": (unpaid_ticks[e][-1] if lands else None), "detected": bool(det),
                    "class": cls})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--b1s-worlds", type=int, default=60)
    a = ap.parse_args(argv)
    rows = []
    # (a) E4b fix_unaffordable elites
    for gs in range(1, 6):
        f = E4B / f"full_w{gs}_elites.npz"
        if not f.exists():
            continue
        fel = np.load(f)["fix_unaffordable"]                                   # [P, T, S, W]
        mech, wid = make_world(gs)
        P, k = len(fel), len(E_SEEDS)
        eps = analyse(mech, wid, np.tile(E_SEEDS, P), np.repeat(fel, k, axis=0))
        for r in eps:
            rows.append({"source": "E4b", "world_seed": gs, "delay": mech.delay, "horizon": mech.horizon,
                         "elite": r["episode"] // k, **r})
    # (b) B1s configuration
    for g in range(a.b1s_worlds):
        mech, wid = make_world(g)
        seeds = episode_seeds(16, base=31_000 + g)
        acts = action_tensor(mech, 16, seed=5000 + g, abstain_p=0.3)            # [T, n, S, W]
        eps = analyse(mech, wid, seeds, np.ascontiguousarray(acts.transpose(1, 0, 2, 3)))
        for r in eps:
            rows.append({"source": "B1s", "world_seed": g, "delay": mech.delay, "horizon": mech.horizon, **r})
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")

    def summ(sel):
        c = Counter(r["class"] for r in sel)
        missed = c["missed_all_after_end"] + c["missed_in_episode_absorbed"]
        return {"episodes": len(sel), "classes": dict(c),
                "missed_exercised": missed,
                "share_missed_all_after_end": (round(c["missed_all_after_end"] / missed, 4) if missed else None)}

    report = {"E4b_all": summ([r for r in rows if r["source"] == "E4b"]),
              "B1s_all": summ([r for r in rows if r["source"] == "B1s"]),
              "B1s_delay0": summ([r for r in rows if r["source"] == "B1s" and r["delay"] == 0]),
              "B1s_delay_gt0": summ([r for r in rows if r["source"] == "B1s" and r["delay"] > 0])}
    for gs in range(1, 6):
        sel = [r for r in rows if r["source"] == "E4b" and r["world_seed"] == gs]
        if not sel:
            continue
        elites = sorted({r["elite"] for r in sel})
        ex = [el for el in elites if any(r["unpaid_ticks"] > 0 for r in sel if r["elite"] == el)]
        caught = [el for el in ex if any(r["detected"] for r in sel if r["elite"] == el)]
        report[f"E4b_w{gs}"] = {**summ(sel), "delay": sel[0]["delay"], "horizon": sel[0]["horizon"],
                                "elites_exercised": len(ex), "elites_caught": len(caught)}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
