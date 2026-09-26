"""AETH-02 closure: H2's lifetime gap and H3's cycle deficit, properly powered.

Operator directive 2026-09-26 (roles/Aether/prompts/2026-09-26_resume_science).
Two questions the closing report (AETH-02_CLOSE_2026-09-24.md) left open:

  H2  Independence predicted the edge fraction to 0.2% but over-predicted
      the >=64-tick cohort 3.1x. Does that gap persist under a null conditioned
      on the cohort that can actually carry an edge?
  H3  The realized functional graph has ~2.75x FEWER cycle nodes than a
      rewired graph. Is that real at 512^2, and if so which field carries
      it and what in the transition law produces it?

`aeth01.v1` is not modified. Every null below is a counterfactual state
fed to the unmodified kernel, or a counterfactual graph built from the
observer; nothing edits the law.

PREREGISTERED, written before the first 512^2 run of this module
------------------------------------------------------------------
H2-P1  The old null (`aeth02_falsifiers.h2_independence`) estimated edge
       persistence from change rates averaged over ALL sites and ignored
       energy. An edge's source is an active writer, which pays
       write_cost + maintenance every tick against an expected
       replenishment of 8 * 0.125 = 1, so it drains. PREDICTION: the
       measured per-tick edge hazard exceeds the old null's (1 - s), and
       starvation of the source is a named, non-negligible share of it.
H2-P2  A conditioned null -- cause-specific template/arbitration hazards
       measured on the edge cohort, treated as memoryless, times an
       energy persistence curve from an i.i.d. bootstrap of active-writer
       energy increments -- predicts the stationary P(run >= 64) within
       a factor of 1.5.
       CLOSE H2 AS A NULL-MODEL DEFECT IF: P2 holds.
       H2 PERSISTS IF: the conditioned null is still off by > 1.5x. Then
       the lifetime distribution is the most interesting open property
       of aeth01.v1, and nothing here is licensed to call it functional.
H3-P1  The cycle deficit against a matched null persists at 512^2 with
       thousands of on-cycle edges pooled (not 205).
       RECORD AS SAMPLING NOISE IF: real/null cycle-node ratio is within
       [0.8, 1.25] at 512^2 against both nulls.
H3-P2  A cycle node is, by construction, the target of a write every
       tick. A write into opcode (payload != WRITE) deactivates it; a
       write into arg0 re-aims it unless payload % 4 matches. Writes into
       arg1, payload and energy leave the topology alone. PREDICTION: the
       deficit is concentrated in opcode- and arg0-field cycle edges
       (real/null well below 1) and near 1 for arg1/payload/energy.
       Not privileged: if the deficit is spread evenly across fields, the
       mechanism is not the write semantics and this is recorded.
H3-P3  If the mechanism is the write semantics, a writer's one-tick
       out-edge persistence depends on the FIELD it was written in, and NOT
       on whether it is on a cycle. PREDICTION: per-field persistence for
       cycle members matches that for off-cycle written writers within
       noise. FALSIFIED IF cycle membership changes persistence materially
       at fixed field.
H3-P4  Relaxation: a direction-shuffled state starts near the null's
       cycle count and decays to the realized count within tens of
       ticks, the opcode/arg0 cycle edges going first.
"""

import argparse
import json
import os
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_AETHER = os.path.dirname(_HERE)
for _p in (_AETHER, os.path.join(_AETHER, "test", "reference")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gpu_aeth01 as K                                   # noqa: E402
from observatory import aeth01_graph as G                # noqa: E402
from observatory import aeth02_falsifiers as F           # noqa: E402

FIELDS = F.FIELDS
OFFS = np.array(G.SLOT_OFFSETS, dtype=np.int64)
CAUSES = ("source_opcode_overwritten", "source_starved", "source_redirected",
          "source_refielded", "lost_arbitration")
AGE_EDGES = (1, 2, 3, 4, 5, 9, 17, 33, 65, 129, 10 ** 9)   # bin lower bounds


def age_bin(run):
    return np.searchsorted(np.array(AGE_EDGES[1:]), run, side="right")


def active_mask(fields, write_cost):
    return (fields[0] == K.WRITE_OPCODE) & (
        fields[4].astype(np.int64) >= write_cost)


def source_coords(n, targets, slots):
    return (targets + OFFS[slots]) % n


def field_of_source(observer, n):
    """Flat array: the field each realized source wrote this tick, or -1."""
    out = np.full(n * n, -1, dtype=np.int64)
    rows = np.arange(n, dtype=np.int64).reshape(n, 1)
    cols = np.arange(n, dtype=np.int64).reshape(1, n)
    for f, entry in enumerate(observer):
        w = G.unpack(entry)[0]
        for slot, (dr, dc) in enumerate(G.SLOT_OFFSETS):
            m = w == slot
            if m.any():
                src = ((rows + dr) % n) * n + ((cols + dc) % n)
                out[np.broadcast_to(src, (n, n))[m]] = f
    return out


def cycle_stats(nxt, fsrc):
    """Cycle-node count and the field of every on-cycle edge."""
    mask, count, _ = G.cycle_node_mask(np, nxt)
    on = mask.astype(bool)
    per_field = np.bincount(fsrc[on], minlength=5)[:5] if count else np.zeros(5, int)
    return on, int(count), [int(v) for v in per_field]


def cycle_lengths(nxt, on, cap=64):
    """Histogram of cycle lengths, counted once per cycle."""
    idx = np.flatnonzero(on)
    if not len(idx):
        return {}
    cur = nxt[idx].copy()
    length = np.zeros(len(idx), dtype=np.int64)
    for step_no in range(1, cap + 1):
        done = (length == 0) & (cur == idx)
        length[done] = step_no
        cur = nxt[cur]
    hist = {}
    for L in np.unique(length):
        k = int((length == L).sum())
        hist[int(L)] = k // int(L) if L else k        # L == 0 means > cap
    return hist


def rewire_null(nxt, fsrc, n, rng):
    """Null A: each realized source aims a uniformly random neighbour."""
    live = np.flatnonzero(nxt >= 0)
    r, c = live // n, live % n
    slots = rng.integers(0, 4, size=len(live))
    tr, tc = (r + OFFS[slots, 0]) % n, (c + OFFS[slots, 1]) % n
    null = np.full(n * n, -1, dtype=np.int64)
    null[live] = tr * n + tc
    return cycle_stats(null, fsrc)[1:]


def shuffle_null(fields, tick, par, rng):
    """Null B: permute arg0 among active writers, then run the real kernel.

    Same writers, same fields, same payloads, same direction histogram,
    same arbitration law; only the spatial assignment of directions is
    destroyed. Returns (count, per_field, shuffled_fields).
    """
    n = fields[0].shape[0]
    shuffled = [f.copy() for f in fields]
    act = active_mask(fields, par["write_cost"])
    vals = shuffled[1][act]
    shuffled[1][act] = vals[rng.permutation(len(vals))]
    _out, obs = F.step([f.copy() for f in shuffled], tick, par)
    nxt = G.realized_map(np, obs, n, n)
    _on, count, per_field = cycle_stats(nxt, field_of_source(obs, n))
    return count, per_field, shuffled


def relaxation(fields, tick, par, rng, ticks):
    """H3-P4: run a direction-shuffled state forward and watch cycles."""
    n = fields[0].shape[0]
    _c, _pf, cur = shuffle_null(fields, tick, par, rng)
    series = []
    for k in range(ticks):
        cur, obs = F.step(cur, tick + k, par)
        nxt = G.realized_map(np, obs, n, n)
        _on, count, per_field = cycle_stats(nxt, field_of_source(obs, n))
        series.append({"t": k + 1, "cycle_nodes": count, "per_field": per_field})
    return series


def one_tick_persistence(nxt0, nxt1, fsrc0, on0, observer0, n):
    """H3-P3: does a written writer keep its out-edge, by field and cycle?

    For every realized edge s -> t at tick k whose TARGET t is itself a
    realized source at k, ask whether t's out-edge is identical at k+1.
    Split by the field of the edge INTO t and by whether t is on a cycle.
    Also report written-nowhere writers as the unwritten baseline.
    """
    written_field = np.full(n * n, -1, dtype=np.int64)
    rows = np.arange(n, dtype=np.int64).reshape(n, 1)
    cols = np.arange(n, dtype=np.int64).reshape(1, n)
    tgt = (rows * n + cols).ravel()
    # A site can be written in several fields at once; record the most
    # topology-relevant one (opcode, then arg0, arg1, payload, energy).
    for f in (4, 3, 2, 1, 0):
        w = G.unpack(observer0[f])[0].ravel()
        written_field[tgt[w != G.NO_WINNER]] = f
    src = nxt0 >= 0
    keeps = src & (nxt1 == nxt0)
    out = {}
    for label, sel in (("on_cycle", on0), ("off_cycle", ~on0)):
        row = {}
        for f in range(5):
            m = src & sel & (written_field == f)
            row[FIELDS[f]] = [int(keeps[m].sum()), int(m.sum())]
        m = src & sel & (written_field < 0)
        row["unwritten"] = [int(keeps[m].sum()), int(m.sum())]
        out[label] = row
    return out


def h2_tick(prev_state, state, obs_prev, obs_now, ages_prev, n, write_cost,
            acc):
    """Accumulate edge deaths by cause and age, one tick."""
    for f in range(5):
        w0 = G.unpack(obs_prev[f])[0]
        w1 = G.unpack(obs_now[f])[0]
        present = w0 != G.NO_WINNER
        if not present.any():
            continue
        targets = np.argwhere(present)
        slots = w0[present].astype(np.int64)
        ages = ages_prev[f][present].astype(np.int64)
        bins = age_bin(ages)
        died = w1[present] != w0[present]
        src = source_coords(n, targets, slots)
        sr, sc = src[:, 0], src[:, 1]
        op1 = state[0][sr, sc]
        en1 = state[4][sr, sc].astype(np.int64)
        dir0 = prev_state[1][sr, sc] % 4
        dir1 = state[1][sr, sc] % 4
        fld0 = prev_state[2][sr, sc] % 5
        fld1 = state[2][sr, sc] % 5
        cause = np.full(len(targets), -1, dtype=np.int64)
        rem = died.copy()
        for code, cond in enumerate((
                op1 != K.WRITE_OPCODE, en1 < write_cost, dir1 != dir0,
                fld1 != fld0, np.ones(len(targets), dtype=bool))):
            hit = rem & cond
            cause[hit] = code
            rem &= ~hit
        a = acc[f]
        a["at_risk"] += np.bincount(bins, minlength=len(AGE_EDGES) - 1)
        for code in range(len(CAUSES)):
            m = cause == code
            if m.any():
                a["deaths"][code] += np.bincount(bins[m],
                                                 minlength=len(AGE_EDGES) - 1)
        # Energy bookkeeping for the conditioned null: the source energy
        # at birth, and the per-tick increment of every source.
        born = ages == 1
        if born.any():
            e0 = prev_state[4][sr[born], sc[born]].astype(np.int64)
            a["birth_energy"] += np.bincount(e0, minlength=256)
        inc = en1 - prev_state[4][sr, sc].astype(np.int64)
        a["energy_increment"] += np.bincount(np.clip(inc + 255, 0, 510),
                                             minlength=511)
        a["ge64_num"] += int((ages >= 64).sum())
        a["ge64_den"] += int(len(ages))


def new_acc():
    nb = len(AGE_EDGES) - 1
    return [{"at_risk": np.zeros(nb, np.int64),
             "deaths": [np.zeros(nb, np.int64) for _ in CAUSES],
             "birth_energy": np.zeros(256, np.int64),
             "energy_increment": np.zeros(511, np.int64),
             "ge64_num": 0, "ge64_den": 0} for _ in range(5)]


def energy_persistence(birth_hist, inc_hist, write_cost, horizon, rng,
                    walkers=20000):
    """S_E(k): P(source still >= write_cost after k-1 ticks), i.i.d. walk.

    The source energy at birth is drawn from the measured birth
    histogram; each tick adds an increment drawn from the measured
    increment histogram of edge sources, clipped to [0, 255]. Starved
    means below write_cost at the start of a tick, which is what makes
    a writer inactive under aeth01.v1.
    """
    if birth_hist.sum() == 0:
        return np.ones(horizon)
    e = rng.choice(256, size=walkers, p=birth_hist / birth_hist.sum())
    incs = np.arange(511) - 255
    p_inc = inc_hist / inc_hist.sum()
    alive = np.ones(walkers, dtype=bool)
    surv = np.empty(horizon)
    surv[0] = 1.0
    for k in range(1, horizon):
        e = np.clip(e + rng.choice(incs, size=walkers, p=p_inc), 0, 255)
        alive &= e >= write_cost
        surv[k] = alive.mean()
    return surv


def h2_models(acc, naive_s, write_cost, rng, horizon=2000):
    """Old null, conditioned memoryless null, conditioned + energy null."""
    out = {}
    for f in range(5):
        a = acc[f]
        risk = a["at_risk"].sum()
        if not risk:
            continue
        deaths = [d.sum() for d in a["deaths"]]
        h_total = sum(deaths) / risk
        h_cause = {CAUSES[c]: deaths[c] / risk for c in range(len(CAUSES))}
        observed = a["ge64_num"] / a["ge64_den"]
        s1 = 1.0 - h_total
        n1 = s1 ** 63
        # Conditioned null with energy aging: memoryless non-energy
        # causes times an i.i.d. energy walk. Starvation is taken OUT of
        # the memoryless part so it is not counted twice.
        h_nonE = h_total - h_cause["source_starved"]
        k = np.arange(horizon)
        s_template = (1.0 - h_nonE) ** k
        s_energy = energy_persistence(a["birth_energy"], a["energy_increment"],
                                   write_cost, horizon, rng)
        surv = s_template * s_energy
        n2 = surv[63:].sum() / surv.sum()
        # Life table from the measured age-specific hazard: an instrument
        # self-check (should reproduce `observed` if the edge cohort is
        # stationary and the bins are fine enough), NOT a model.
        haz = np.array([sum(a["deaths"][c][b] for c in range(len(CAUSES)))
                        / a["at_risk"][b] if a["at_risk"][b] else 0.0
                        for b in range(len(AGE_EDGES) - 1)])
        lt = np.ones(horizon)
        for kk in range(1, horizon):
            lt[kk] = lt[kk - 1] * (1.0 - haz[age_bin(np.array([kk]))[0]])
        n_lt = lt[63:].sum() / lt.sum()
        age_hazard = {}
        for b in range(len(AGE_EDGES) - 1):
            r = int(a["at_risk"][b])
            age_hazard["%d-%s" % (AGE_EDGES[b], AGE_EDGES[b + 1] - 1
                                  if AGE_EDGES[b + 1] < 10 ** 9 else "inf")] = {
                "at_risk": r,
                **{CAUSES[c]: (int(a["deaths"][c][b]) / r if r else None)
                   for c in range(len(CAUSES))}}
        out[FIELDS[f]] = {
            "edges_at_risk": int(risk),
            "observed_ge64": observed,
            "hazard_total": h_total,
            "hazard_by_cause": h_cause,
            "naive_s": naive_s,
            "naive_pred_ge64": naive_s ** 63,
            "naive_ratio": (naive_s ** 63) / observed if observed else None,
            "conditioned_memoryless_pred_ge64": n1,
            "conditioned_memoryless_ratio": n1 / observed if observed else None,
            "conditioned_energy_pred_ge64": n2,
            "conditioned_energy_ratio": n2 / observed if observed else None,
            "life_table_selfcheck_ge64": n_lt,
            "energy_persistence_at": {str(t): float(s_energy[t])
                                   for t in (1, 8, 16, 32, 63, 128, 256)},
            "age_hazard": age_hazard,
        }
    return out


def naive_s_from_rates(per_field_rates, activity_density):
    """The old null's per-tick edge persistence, recomputed from per-tick rates."""
    p = activity_density / 20.0
    at_least_one = 1.0 - (1.0 - p) ** 4
    exactly_one = 4.0 * p * (1.0 - p) ** 3
    keep_op = 1.0 - per_field_rates["opcode"]
    keep_a0 = 1.0 - per_field_rates["arg0"]
    keep_a1 = 1.0 - per_field_rates["arg1"]
    keep_dir = keep_a0 + (1.0 - keep_a0) / 4.0
    keep_field = keep_a1 + (1.0 - keep_a1) / 5.0
    return keep_op * keep_dir * keep_field * (1.0 - (at_least_one - exactly_one))


def closure(n, warmup, follow, seed_index, h3_every, relax_every, relax_ticks,
            rewirings, out_dir):
    seed = F.B_SEED0 + seed_index
    rng_seed = F.B_RNG0 + seed_index
    par = F.params(seed)
    wc = par["write_cost"]
    t0 = time.time()
    print("[n=%d seed=%d] warmup %d" % (n, seed_index, warmup), file=sys.stderr)
    base = F.run(n, warmup, seed=seed, rng_seed=rng_seed, progress=500)
    fields, runs, obs_prev = base["fields"], base["runs"], base["observer"]
    tick = base["tick"]
    prev_state = None
    rng = np.random.default_rng(0xC105E + seed_index)
    acc = new_acc()
    rate_sum = {f: 0.0 for f in FIELDS}
    act_sum = 0.0
    h3_samples, surv_acc, relax = [], None, []
    nxt_prev = fsrc_prev = on_prev = None
    for k in range(follow):
        tick += 1
        state = [f.copy() for f in fields]          # S_k: input to this tick
        fields, obs = F.step(fields, tick, par)
        _r, per_field = F.OBS.change_rate(np, state, fields)
        for f in FIELDS:
            rate_sum[f] += per_field[f]
        act_sum += float(active_mask(state, wc).mean())
        # H2: edges present in obs_prev (tick-1) persist into obs (tick)?
        # runs["run"] holds the ages of the edges in obs_prev here: it has
        # been updated through tick-1 and not yet with this tick.
        if prev_state is not None:
            h2_tick(prev_state, state, obs_prev, obs, runs["run"], n, wc, acc)
        G.update_runlengths(np, runs, obs)
        # H3
        nxt = G.realized_map(np, obs, n, n)
        fsrc = field_of_source(obs, n)
        on, count, per_field_cyc = cycle_stats(nxt, fsrc)
        if nxt_prev is not None:
            s = one_tick_persistence(nxt_prev, nxt, fsrc_prev, on_prev,
                                  obs_prev, n)
            if surv_acc is None:
                surv_acc = s
            else:
                for lab in s:
                    for key in s[lab]:
                        surv_acc[lab][key] = [a + b for a, b in
                                              zip(surv_acc[lab][key], s[lab][key])]
        if (k + 1) % h3_every == 0:
            classes = G.edge_classes(np, obs, state, fields, restrict=None)
            classes_cyc = G.edge_classes(np, obs, state, fields,
                                         restrict=on.reshape(n, n))
            nullA = [rewire_null(nxt, fsrc, n, rng) for _ in range(rewirings)]
            nullB = shuffle_null(state, tick, par, rng)
            h3_samples.append({
                "tick": tick, "cycle_nodes": count,
                "cycle_edges_by_field": per_field_cyc,
                "mapped_nodes": int((nxt >= 0).sum()),
                "sources_by_field": [int(v) for v in
                                     np.bincount(fsrc[fsrc >= 0], minlength=5)],
                "cycle_lengths": cycle_lengths(nxt, on),
                "nullA_cycle_nodes": [c for c, _ in nullA],
                "nullA_by_field": [pf for _, pf in nullA],
                "nullB_cycle_nodes": nullB[0], "nullB_by_field": nullB[1],
                "state_changing_all": {f: [classes[f]["STATE_CHANGING"],
                                           classes[f]["edges"]] for f in FIELDS},
                "state_changing_cycle": {f: [classes_cyc[f]["STATE_CHANGING"],
                                             classes_cyc[f]["edges"]]
                                         for f in FIELDS},
            })
        if relax_every and (k + 1) % relax_every == 0:
            relax.append({"tick": tick, "realized_cycle_nodes": count,
                          "series": relaxation(state, tick, par, rng,
                                               relax_ticks)})
        prev_state, obs_prev = state, obs
        nxt_prev, fsrc_prev, on_prev = nxt, fsrc, on
        if (k + 1) % 100 == 0:
            print("  follow %d/%d  %.0fs" % (k + 1, follow, time.time() - t0),
                  file=sys.stderr)
    rates = {f: rate_sum[f] / follow for f in FIELDS}
    naive_s = naive_s_from_rates(rates, act_sum / follow)
    models = h2_models(acc, naive_s, wc, np.random.default_rng(0xE2 + seed_index))
    result = {
        "n": n, "warmup": warmup, "follow": follow, "seed_index": seed_index,
        "seed": seed, "rng_seed": rng_seed, "semantics": "aeth01.v1",
        "per_tick_change_rate_by_field": rates,
        "activity_density": act_sum / follow,
        "h2": models, "h3_samples": h3_samples,
        "h3_one_tick_persistence": surv_acc, "h3_relaxation": relax,
        "wall_seconds": time.time() - t0,
    }
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "closure_n%d_s%d.json" % (n, seed_index))
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, indent=1, sort_keys=True, default=float)
        fh.write("\n")
    print("wrote %s (%.0fs)" % (path, time.time() - t0), file=sys.stderr)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--n", type=int, default=512)
    ap.add_argument("--warmup", type=int, default=2500)
    ap.add_argument("--follow", type=int, default=600)
    ap.add_argument("--seed-index", type=int, default=0)
    ap.add_argument("--h3-every", type=int, default=25)
    ap.add_argument("--relax-every", type=int, default=200)
    ap.add_argument("--relax-ticks", type=int, default=60)
    ap.add_argument("--rewirings", type=int, default=8)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    closure(a.n, a.warmup, a.follow, a.seed_index, a.h3_every, a.relax_every,
            a.relax_ticks, a.rewirings, a.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
