"""B1u: how does an unpaid write that lands INSIDE an episode leave the trace unchanged?

An instrumented scalar replica of wforge Encounter.step (semantics copied, wforge read-only)
with a probe after every sub-phase. Two replicas run in lock-step on the same episode:
honest, and fix_unaffordable (unpaid writes dropped). After each probe point the register
difference set D = {i : regs_h[i] != regs_c[i]} is recorded; charge and alive never differ
(the cheat only drops writes).

Probe order inside tick t (wforge order):
  land      after pending writes landing at t are applied
  lin[j]    after lin_op j (dst, a, s1, b, s2, c) is applied
  stoch     after the stochastic kick (if any)
  trace     the trace line is hashed from this state

Per episode whose writes differ at some `land` probe, the first tick's story is classified:
  erased_by_lin_op        D becomes empty right after a lin_op whose dst was the last member of D
  erased_by_stoch         D becomes empty right after the stoch kick
  cancelled_on_landing    the landing itself leaves D empty (writes sum to 0 mod M)
  survives_to_trace       D is non-empty at the trace line (the hash must then differ)
A `read_before_erase` flag records whether some lin_op read a member of D (as s1 with a != 0
or as s2 with b != 0) before the erasure; reading propagates the difference.

Replica validity: every replayed honest episode must equal the wforge trace hash.
usage: python -m primordial.soup.b1.absorb --out rows.jsonl
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from collections import Counter

import numpy as np

from .common import M, Encounter, action_tensor, episode_seeds, make_world, stream

ROWS = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "B"
E4B = pathlib.Path("C:/Users/jcrai/lab/pm-data/E/E4b-qd-encounter-archive-positive")
E_SEEDS = np.arange(9100, 9108, dtype=np.int64)


class Replica:
    """wforge Encounter.step semantics, no observation, with probes. cheat='fix_unaffordable'."""

    def __init__(self, m, wid, seed, cheat=""):
        self.m, self.cheat = m, cheat
        self.regs = [stream("init", wid, seed, i).below(M) for i in range(m.n_regs)]
        self.charge = [m.start_charge] * m.n_slots
        self.alive = [True] * m.n_slots
        self.tick = 0
        self.pending = []
        self.trace = hashlib.sha256()
        self.st = stream("stoch", wid, seed)

    def step(self, actions, probe):
        m = self.m
        for s in range(m.n_slots):
            if not self.alive[s]:
                continue
            a = actions[s]
            mag = sum(x % 8 for x in a)
            cost = mag * m.act_cost
            afford = cost <= self.charge[s]
            if not afford:
                cost = 0
            self.charge[s] -= cost
            if self.cheat == "fix_unaffordable" and not afford:
                continue
            for i, x in enumerate(a[:m.act_width]):
                if x % 8:
                    self.pending.append((self.tick + m.delay, s, m.act_targets[i], (x % 8) * 251))
        landing = [p for p in self.pending if p[0] == self.tick]
        self.pending = [p for p in self.pending if p[0] > self.tick]
        for _, s, tgt, amt in sorted(landing, key=lambda p: (p[1], p[2])):
            self.regs[tgt] = (self.regs[tgt] + amt) % M
        probe("land", None)
        flip = (m.regime_period and (self.tick // m.regime_period) % 2 == 1)
        for j, (dst, a, s1, b, s2, c) in enumerate(m.lin_ops):
            aa = (M - a) % M if flip else a
            self.regs[dst] = (aa * self.regs[s1] + b * self.regs[s2] + c) % M
            probe("lin", (j, dst, s1 if aa else None, s2 if b else None))
        if m.stoch_rate and self.st.below(m.stoch_rate) == 0:
            v = self.st.below(M)                       # RHS first, as wforge evaluates it
            self.regs[self.st.below(m.n_regs)] = v
        probe("stoch", None)
        v = self.regs[m.yield_reg]
        in_win = (m.yield_lo <= v < m.yield_hi) if m.yield_lo < m.yield_hi else (v >= m.yield_lo or v < m.yield_hi)
        winners = [s for s in range(m.n_slots) if self.alive[s]] if in_win else []
        for s in range(m.n_slots):
            if not self.alive[s]:
                continue
            self.charge[s] -= m.step_cost
            if s in winners:
                self.charge[s] += m.yield_amt // len(winners)
            if self.charge[s] <= 0:
                self.alive[s] = False
        self.trace.update(bytes(str((self.tick, self.regs, self.charge, self.alive)), "ascii"))
        probe("trace", None)
        self.tick += 1
        return self.tick >= m.horizon or not any(self.alive)


def episode(m, wid, seed, acts_env):
    """acts_env [T, S, W]. Returns (row dict, replica_equals_wforge)."""
    h, c = Replica(m, wid, seed), Replica(m, wid, seed, cheat="fix_unaffordable")
    done, t = False, 0
    stories = []                 # one story per tick where a NEW difference appears at landing
    detected = False
    prev_trace_diff = False
    while not done:
        acts = [[int(x) for x in acts_env[t, s]] for s in range(m.n_slots)]
        # step the cheat replica first, snapshotting its registers at every probe point;
        # then step honest and compare at the same probe points (both emit identical probe sequences)
        snaps_c = []
        c.step(acts, lambda st, inf: snaps_c.append(list(c.regs)))
        idx = [0]
        tick_log = []

        def probe_h(stage, info):
            D = {i for i, (x, y) in enumerate(zip(h.regs, snaps_c[idx[0]])) if x != y}
            tick_log.append((stage, info, D))
            idx[0] += 1

        done = h.step(acts, probe_h)
        if not prev_trace_diff:
            if tick_log[0][2]:
                stories.append(classify(t, tick_log))
            elif any(D for _, _, D in tick_log):
                stories.append({"tick": t, "class": "diff_appears_after_landing", "read_before_erase": None,
                                "erasing_lin_op": None})
        prev_trace_diff = bool(tick_log[-1][2])
        detected |= prev_trace_diff
        t += 1
    ref = Encounter(m, wid, int(seed))
    for tt in range(t):
        ref.step([[int(x) for x in acts_env[tt, s]] for s in range(m.n_slots)])
    return stories, detected, h.trace.hexdigest() == ref.outcome()["trace_hash"], t


def classify(t, tick_log):
    stage0, _, D0 = tick_log[0]
    D_prev, read = set(D0), False
    for stage, info, D in tick_log[1:]:
        if stage == "lin" and D_prev:
            j, dst, r1, r2 = info
            if (r1 is not None and r1 in D_prev) or (r2 is not None and r2 in D_prev):
                read = True
        if D_prev and not D:
            return {"tick": t, "class": "erased_by_lin_op" if stage == "lin" else "erased_by_stoch"
                    if stage == "stoch" else f"erased_at_{stage}", "read_before_erase": read,
                    "erasing_lin_op": info[0] if stage == "lin" else None}
        D_prev = set(D)
    return {"tick": t, "class": "survives_to_trace", "read_before_erase": read, "erasing_lin_op": None}


def sources(landing_rows):
    """Yield (source, world_seed, seed, acts_env, b1t_class) for B1t episodes."""
    by = {}
    for r in landing_rows:
        by.setdefault((r["source"], r["world_seed"]), []).append(r)
    for (src, g), rs in sorted(by.items()):
        mech, wid = make_world(g)
        if src == "E4b":
            fel = np.load(E4B / f"full_w{g}_elites.npz")["fix_unaffordable"]
            A = np.repeat(fel, len(E_SEEDS), axis=0)                              # [P*8, T, S, W]
        else:
            A = np.ascontiguousarray(action_tensor(mech, 16, seed=5000 + g, abstain_p=0.3).transpose(1, 0, 2, 3))
        for r in rs:
            yield src, g, mech, wid, r["seed"], A[r["episode"]], r["class"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--detected-sample", type=int, default=150, help="detected episodes checked as control")
    a = ap.parse_args(argv)
    land = [json.loads(x) for x in open(ROWS / "B1t-landing.jsonl", encoding="utf-8")]
    absorbed = [r for r in land if r["class"] == "missed_in_episode_absorbed"]
    rng = np.random.default_rng(0)
    det = [r for r in land if r["class"] == "detected"]
    det = [det[i] for i in rng.choice(len(det), size=min(a.detected_sample, len(det)), replace=False)]
    rows = []
    for src, g, mech, wid, seed, acts_env, b1t_cls in sources(absorbed + det):
        stories, detected, valid, T = episode(mech, wid, seed, acts_env)
        classes = Counter(s["class"] for s in stories)
        rows.append({"source": src, "world_seed": g, "seed": int(seed), "b1t_class": b1t_cls,
                     "replica_eq_wforge": valid, "replica_detected": detected, "ticks": T,
                     "delay": mech.delay, "lin_ops": len(mech.lin_ops),
                     "n_stories": len(stories), "story_classes": dict(classes),
                     "all_erased_by_lin_op": bool(stories) and set(classes) == {"erased_by_lin_op"},
                     "any_survives_to_trace": classes["survives_to_trace"] > 0,
                     "any_read_before_erase": any(bool(s.get("read_before_erase")) for s in stories),
                     "first_story": stories[0] if stories else None})
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    ab = [r for r in rows if r["b1t_class"] == "missed_in_episode_absorbed"]
    dt = [r for r in rows if r["b1t_class"] == "detected"]
    agg = Counter()
    for r in ab:
        agg.update(r["story_classes"])
    print(json.dumps({
        "replica_eq_wforge": f"{sum(r['replica_eq_wforge'] for r in rows)}/{len(rows)}",
        "absorbed": {"n": len(ab), "episodes_all_erased_by_lin_op": sum(r["all_erased_by_lin_op"] for r in ab),
                     "story_classes_over_all_ticks": dict(agg),
                     "episodes_any_read_before_erase": sum(r["any_read_before_erase"] for r in ab),
                     "episodes_with_no_story": sum(r["n_stories"] == 0 for r in ab),
                     "replica_detected (must be 0)": sum(r["replica_detected"] for r in ab)},
        "detected_control": {"n": len(dt),
                             "replica_detected (must be all)": sum(r["replica_detected"] for r in dt),
                             "any_survives_to_trace": sum(r["any_survives_to_trace"] for r in dt)},
    }, indent=1))


if __name__ == "__main__":
    main()
