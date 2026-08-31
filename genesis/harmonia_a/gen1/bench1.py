#!/usr/bin/env python
"""
HARMONIA A GEN-1 -- causal density and consequence geometry.

Substrate, generator, edit family, and ruler are IDENTICAL to Gen-0
(genesis/harmonia_a/gen0/bench.py, sha a28386bc...): Boolean functions
f: {0,1}^10 -> {0,1} as random 24-gate straight-line circuits over
{AND,OR,XOR,NAND}; the 1056-member single-gate edit family; exact
full-domain Hamming displacement. The relevant Gen-0 functions are
copied here verbatim (self-contained, hash-journaled) with provenance.

New in Gen-1:
  - structural liveness s_live (graph-only)
  - exact per-gate behavioral influence inf(g) (wire-negation
    intervention, full-domain), b_live, inf_density
  - the FORCED layer: d <= inf(target gate) for every single-gate
    edit; forced_neutral_floor and forced_local_bound computed per
    object and treated as confounds, never as findings
  - a controlled liveness ladder built by REJECTION SAMPLING from the
    unchanged Gen-0 generator, bins chosen by frozen rule from a
    graph-only census (span [P1,P99], 5 equal-width bins, each with
    natural mass >= 0.5%; one shrink retry to [P2.5,P97.5]; else
    AXIS_NOT_IDENTIFIABLE_UNDER_CURRENT_GENERATOR)

Phases: census -> objects -> assay. All randomness from named
SeedSequence spawns. No LLM anywhere. StackVM is held out and never
touched by this code.
"""

import json
import sys
import time

import numpy as np

N = 10
DOM = 1 << N
G = 24
MASTER_SEEDS = (11, 22, 33, 44, 55)
OBJECTS_PER_CELL = 12          # per (seed, level)
N_LEVELS = 5
K_EDITS = 128
LOCAL_BAND = 0.25
BALANCE_BAND = (0.05, 0.95)
CENSUS_PER_SEED = 60_000       # graph-only draws per seed
BIN_MIN_MASS = 0.005
SPAN_PRIMARY = (1.0, 99.0)     # percentiles
SPAN_RETRY = (2.5, 97.5)
REJECT_CAP = 400_000           # draws per (seed, level)
SHAM_LEVELS = (0, N_LEVELS - 1)
ASSAY_VERSION = "harmonia_a_gen1_v1.0"

INPUT_COLS = ((np.arange(DOM)[:, None] >> np.arange(N)) & 1).astype(bool)


# ------------------------------------------------ Gen-0 verbatim layer

def gate_eval(op, a, b):
    if op == 0:
        return a & b
    if op == 1:
        return a | b
    if op == 2:
        return a ^ b
    return ~(a & b)


def eval_wires(gates, perm=None):
    """All wires (inputs + gates); wire i<N is input bit i (or bit
    perm[i] for the SHAM decode)."""
    wires = [INPUT_COLS[:, perm[i] if perm is not None else i]
             for i in range(N)]
    for op, a, b in gates:
        wires.append(gate_eval(op, wires[a], wires[b]))
    return wires


def random_circuit(rng):
    gates = []
    for g in range(G):
        nw = N + g
        a = int(rng.integers(nw))
        b = int(rng.integers(nw))
        op = int(rng.integers(4))
        gates.append((op, a, b))
    return gates


def circuit_edit_space(gates):
    edits = []
    for gi, (op, a, b) in enumerate(gates):
        for new_op in range(4):
            if new_op != op:
                edits.append(("op", gi, new_op))
        nw = N + gi
        for slot in (0, 1):
            cur = (a, b)[slot]
            for w in range(nw):
                if w != cur:
                    edits.append(("wire", gi, (slot, w)))
    return edits


def apply_edit(gates, edit):
    kind, gi, payload = edit
    out = list(gates)
    op, a, b = out[gi]
    if kind == "op":
        out[gi] = (payload, a, b)
    else:
        slot, w = payload
        out[gi] = (op, w, b) if slot == 0 else (op, a, w)
    return out


def moebius(v):
    v = v.copy()
    step = 1
    while step < DOM:
        for start in range(0, DOM, 2 * step):
            v[start + step:start + 2 * step] ^= v[start:start + step]
        step *= 2
    return v


def rng_for(*key):
    return np.random.default_rng(np.random.SeedSequence(list(key)))


def displacement(f, g):
    return float(np.count_nonzero(f != g)) / DOM


# ------------------------------------------------ Gen-1 coordinates

def live_gate_set(gates):
    """Gates structurally on a dependency path to the output."""
    live = set()
    stack = [G - 1]
    while stack:
        g = stack.pop()
        if g in live:
            continue
        live.add(g)
        for w in gates[g][1:]:
            if w >= N:
                stack.append(w - N)
    return live


def influences(gates, wires):
    """Exact per-gate influence: negate gate g's wire, propagate
    downstream, count output flips over the full domain."""
    base = wires[-1]
    infs = []
    for g in range(G):
        w2 = list(wires[:N + g + 1])
        w2[N + g] = ~wires[N + g]
        for h in range(g + 1, G):
            op, a, b = gates[h]
            w2.append(gate_eval(op, w2[a], w2[b]))
        infs.append(float(np.count_nonzero(w2[-1] != base)) / DOM)
    return infs


def edit_gate_weights():
    """Edit-family weight landing on each gate (fixed for all objects:
    3 op edits + 2*(N-1+g) rewires per gate; total 1056)."""
    w = np.array([3.0 + 2.0 * (N - 1 + g) for g in range(G)])
    return w / w.sum()


def cone_depth(gates):
    d = [0] * N
    for op, a, b in gates:
        d.append(max(d[a], d[b]) + 1)
    return d[-1]


def n_live_vars(f):
    x = np.arange(DOM)
    return int(sum(1 for i in range(N)
                   if not np.array_equal(f[x], f[x ^ (1 << i)])))


def covariates(gates):
    wires = eval_wires(gates)
    f = wires[-1].copy()
    infs = influences(gates, wires)
    ew = edit_gate_weights()
    infs_a = np.array(infs)
    live = live_gate_set(gates)
    return f, dict(
        s_live=len(live) / G,
        b_live=float(np.mean(infs_a > 0)),
        inf_density=float(infs_a.mean()),
        inf_profile=[round(v, 6) for v in infs],
        forced_neutral_floor=float(ew[infs_a == 0].sum()),
        forced_local_bound=float(
            ew[(infs_a > 0) & (infs_a <= LOCAL_BAND)].sum()),
        balance=float(f.mean()),
        live_vars=n_live_vars(f),
        anf_support=int(moebius(f.astype(np.uint8)).sum()),
        depth=cone_depth(gates))


# ------------------------------------------------ census (frozen rule)

def graph_census():
    """Pooled graph-only s_live distribution; no evaluation."""
    vals = []
    for seed in MASTER_SEEDS:
        rng = rng_for(seed, 100)
        for _ in range(CENSUS_PER_SEED):
            vals.append(len(live_gate_set(random_circuit(rng))) / G)
    return np.array(vals)


def choose_bins(vals):
    for span, label in ((SPAN_PRIMARY, "primary"), (SPAN_RETRY, "retry")):
        lo, hi = np.percentile(vals, span)
        edges = np.linspace(lo, hi, N_LEVELS + 1)
        masses = []
        for i in range(N_LEVELS):
            top_ok = vals <= edges[i + 1] if i == N_LEVELS - 1 \
                else vals < edges[i + 1]
            masses.append(float(np.mean((vals >= edges[i]) & top_ok)))
        if min(masses) >= BIN_MIN_MASS:
            return edges, masses, label
    return None, masses, "FAILED"


def in_bin(s, edges, level):
    top_ok = s <= edges[level + 1] if level == N_LEVELS - 1 \
        else s < edges[level + 1]
    return edges[level] <= s and top_ok


def build_objects(edges):
    objects, report = [], []
    for seed in MASTER_SEEDS:
        for level in range(N_LEVELS):
            rng = rng_for(seed, 101, level)
            draws = live_hits = 0
            cell = []
            while len(cell) < OBJECTS_PER_CELL:
                draws += 1
                if draws > REJECT_CAP:
                    return None, report + [dict(
                        seed=seed, level=level, draws=draws,
                        status="REJECT_CAP_EXCEEDED")]
                gates = random_circuit(rng)
                s = len(live_gate_set(gates)) / G
                if not in_bin(s, edges, level):
                    continue
                live_hits += 1
                f, cov = covariates(gates)
                if not (BALANCE_BAND[0] <= cov["balance"]
                        <= BALANCE_BAND[1]):
                    continue
                cell.append(dict(seed=seed, level=level,
                                 obj=len(cell), gates=gates,
                                 f=f, cov=cov))
            objects.extend(cell)
            report.append(dict(
                seed=seed, level=level, draws=draws,
                liveness_acceptance=live_hits / draws,
                balance_acceptance=OBJECTS_PER_CELL / max(live_hits, 1),
                status="OK"))
    return objects, report


# ------------------------------------------------ assay

def run_assay(objects):
    rows = []
    for o in objects:
        edits = circuit_edit_space(o["gates"])
        rng = rng_for(o["seed"], 102, o["level"], o["obj"])
        for k in range(K_EDITS):
            e = edits[int(rng.integers(len(edits)))]
            f2 = eval_wires(apply_edit(o["gates"], e))[-1]
            rows.append(dict(arm="NAT", seed=o["seed"], level=o["level"],
                             obj=o["obj"], edit=k, gate=e[1], kind=e[0],
                             d=displacement(o["f"], f2)))
        # SHAM at the extreme levels only (harness positive control)
        if o["level"] in SHAM_LEVELS:
            perm = rng_for(o["seed"], 103, o["level"],
                           o["obj"]).permutation(N)
            gates_s = [(op,
                        int(perm[a]) if a < N else a,
                        int(perm[b]) if b < N else b)
                       for op, a, b in o["gates"]]
            inv = np.argsort(perm)
            f0 = eval_wires(gates_s, perm=inv)[-1]
            assert np.array_equal(f0, o["f"]), "SHAM same-object violation"
            edits_s = circuit_edit_space(gates_s)
            rng = rng_for(o["seed"], 104, o["level"], o["obj"])
            for k in range(K_EDITS):
                e = edits_s[int(rng.integers(len(edits_s)))]
                f2 = eval_wires(apply_edit(gates_s, e), perm=inv)[-1]
                rows.append(dict(arm="SHAM", seed=o["seed"],
                                 level=o["level"], obj=o["obj"], edit=k,
                                 gate=e[1], kind=e[0],
                                 d=displacement(o["f"], f2)))
    return rows


# ------------------------------------------------ main

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    t0 = time.time()
    vals = graph_census()
    edges, masses, label = choose_bins(vals)
    hist, hedges = np.histogram(vals, bins=25)
    census = dict(
        n=len(vals), span_rule=label,
        natural_hist=dict(counts=hist.tolist(), edges=hedges.tolist()),
        s_live_min=float(vals.min()), s_live_max=float(vals.max()),
        s_live_median=float(np.median(vals)),
        bin_edges=None if edges is None else [float(e) for e in edges],
        bin_masses=[float(m) for m in masses],
        wall_s=round(time.time() - t0, 1))
    if edges is None:
        census["verdict"] = "AXIS_NOT_IDENTIFIABLE_UNDER_CURRENT_GENERATOR"
        json.dump(census, open("results/census_gen1.json", "w"), indent=1)
        print("CENSUS:", census["verdict"])
        return
    census["verdict"] = "BINS_OK"

    t0 = time.time()
    objects, rep = build_objects(edges)
    census["rejection_report"] = rep
    census["objects_wall_s"] = round(time.time() - t0, 1)
    if objects is None:
        census["verdict"] = "AXIS_NOT_IDENTIFIABLE_UNDER_CURRENT_GENERATOR"
        json.dump(census, open("results/census_gen1.json", "w"), indent=1)
        print("CENSUS:", census["verdict"])
        return

    # per-level covariate summary (residual imbalance, disclosed)
    summ = {}
    for level in range(N_LEVELS):
        sub = [o["cov"] for o in objects if o["level"] == level]
        summ[str(level)] = {
            k: dict(mean=float(np.mean([c[k] for c in sub])),
                    sd=float(np.std([c[k] for c in sub])))
            for k in ("s_live", "b_live", "inf_density", "balance",
                      "live_vars", "anf_support", "depth",
                      "forced_neutral_floor", "forced_local_bound")}
    census["per_level_covariates"] = summ
    json.dump(census, open("results/census_gen1.json", "w"), indent=1)
    print(f"CENSUS: {census['verdict']} span={label} "
          f"edges={[round(e,3) for e in census['bin_edges']]} "
          f"masses={[round(m,4) for m in census['bin_masses']]}")
    for level in range(N_LEVELS):
        s = summ[str(level)]
        print(f"  L{level}: s_live={s['s_live']['mean']:.3f} "
              f"b_live={s['b_live']['mean']:.3f} "
              f"inf_den={s['inf_density']['mean']:.3f} "
              f"anf={s['anf_support']['mean']:.1f} "
              f"lvars={s['live_vars']['mean']:.1f}")

    with open("results/objects.jsonl", "w") as fh:
        for o in objects:
            rec = dict(assay_version=ASSAY_VERSION, seed=o["seed"],
                       level=o["level"], obj=o["obj"],
                       gates=[list(g) for g in o["gates"]],
                       edit_family="gen0_op_plus_rewire_1056",
                       **o["cov"])
            fh.write(json.dumps(rec) + "\n")
    if mode == "census":
        return

    t0 = time.time()
    rows = run_assay(objects)
    with open("results/rows.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print(f"ASSAY: {len(rows)} rows in {round(time.time()-t0,1)}s")


if __name__ == "__main__":
    main()
