#!/usr/bin/env python
"""
HARMONIA A GEN-0 -- representational reachability bench.

Substrate: Boolean functions f: {0,1}^10 -> {0,1}.
Native representation: random 24-gate straight-line circuits.
Consequence ruler: exact Hamming displacement over the full 1024-point
domain (no sampling, no faults possible, single battery -- the same
ruler serves census, channels, and claims; D-13 F1 cannot arise).

Arms:
  NAT      circuit; edit = 1-gate op-swap or 1-input rewire
  SHAM     input-relabeled circuit, same edit class (harness positive
           control; distribution provably == NAT)
  ANF      F2 polynomial (Moebius); edit = toggle 1 monomial
           (LOCAL_MASS analytically forced; declared, not discovered)
  ANF_SCR  ANF composed with a random input-space bijection
           (provably == ANF; second harness control)
  VT       truth table; edit = flip 1 row (triviality ceiling)
  TT       exact TT-SVD cores of (-1)^f; edit = +-eps*rms(core) on one
           core entry, sign-round decode. eps grid {0.125, 0.5, 2.0},
           primary eps = 0.5 (named before any run). EMPIRICAL.
  TT_SCR   TT after a random permutation of the 1024 entries
           (destroys variable-order structure; same mechanics). EMPIRICAL.

All randomness flows from the 5 master seeds via named SeedSequence
spawn keys. No LLM anywhere. Everything deterministic.
"""

import json
import sys
import time

import numpy as np

N = 10                     # input bits
DOM = 1 << N               # 1024
G = 24                     # gates per circuit
OPS = ("AND", "OR", "XOR", "NAND")
MASTER_SEEDS = (11, 22, 33, 44, 55)
OBJECTS_PER_SEED = 12
K_EDITS = 128              # perturbations sampled per object per arm
EPS_GRID = (0.125, 0.5, 2.0)
EPS_PRIMARY = 0.5
LOCAL_BAND = 0.25          # K_positive@0.25, aligned with D-13 channel def
BALANCE_BAND = (0.05, 0.95)
RESAMPLE_CAP = 50
SVD_CUTOFF = 1e-12

INPUT_COLS = ((np.arange(DOM)[:, None] >> np.arange(N)) & 1).astype(bool)


# ---------------------------------------------------------------- circuits

def gate_eval(op, a, b):
    if op == 0:
        return a & b
    if op == 1:
        return a | b
    if op == 2:
        return a ^ b
    return ~(a & b)


def eval_circuit(gates, perm=None):
    """gates: list of (op, a, b) wire refs; wire i<N is input bit i
    (or bit perm[i] when perm is given -- the SHAM decode)."""
    wires = [INPUT_COLS[:, perm[i] if perm is not None else i]
             for i in range(N)]
    for op, a, b in gates:
        wires.append(gate_eval(op, wires[a], wires[b]))
    return wires[-1].copy()


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
    """Frozen mechanical edit space: (kind, gate, payload)."""
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


# ---------------------------------------------------------------- ANF

def moebius(v):
    """Self-inverse Moebius/ANF transform over F2. v: uint8 (DOM,)."""
    v = v.copy()
    step = 1
    while step < DOM:
        for start in range(0, DOM, 2 * step):
            v[start + step:start + 2 * step] ^= v[start:start + step]
        step *= 2
    return v


# ---------------------------------------------------------------- TT

def tt_decompose(F):
    """Exact TT-SVD (cutoff SVD_CUTOFF) of F: float64 (2,)*N tensor."""
    cores = []
    M = F.reshape(1, -1)
    r = 1
    for _ in range(N - 1):
        M = M.reshape(r * 2, -1)
        U, S, Vt = np.linalg.svd(M, full_matrices=False)
        keep = S > SVD_CUTOFF
        U, S, Vt = U[:, keep], S[keep], Vt[keep]
        cores.append(U.reshape(r, 2, -1))
        M = S[:, None] * Vt
        r = U.shape[1]
    cores.append(M.reshape(r, 2, 1))
    return cores


def tt_contract(cores):
    M = np.ones((1, 1))
    for c in cores:
        M = M @ c.reshape(c.shape[0], -1)
        M = M.reshape(-1, c.shape[2])
    return M.reshape(-1)


def tt_size(cores):
    return int(sum(c.size for c in cores))


# ---------------------------------------------------------------- helpers

def displacement(f, g):
    return float(np.count_nonzero(f != g)) / DOM


def rng_for(*key):
    """Deterministic named stream."""
    return np.random.default_rng(np.random.SeedSequence(list(key)))


# ---------------------------------------------------------------- objects

def build_objects():
    """Census C1: balance band, resample cap. Returns objects + census log."""
    objects = []
    census = []
    for seed in MASTER_SEEDS:
        for oi in range(OBJECTS_PER_SEED):
            attempts = 0
            while True:
                attempts += 1
                if attempts > RESAMPLE_CAP:
                    raise SystemExit(
                        f"CENSUS C1 FAIL seed={seed} obj={oi}: "
                        f"balance band unreachable in {RESAMPLE_CAP}")
                rng = rng_for(seed, 0, oi, attempts)
                gates = random_circuit(rng)
                f = eval_circuit(gates)
                bal = float(f.mean())
                if BALANCE_BAND[0] <= bal <= BALANCE_BAND[1]:
                    break
            objects.append(dict(seed=seed, obj=oi, gates=gates, f=f))
            census.append(dict(seed=seed, obj=oi, attempts=attempts,
                               balance=bal))
    return objects, census


# ---------------------------------------------------------------- census

def run_census(objects, census_rows):
    out = {"C1_balance": {"rows": census_rows,
                          "band": list(BALANCE_BAND),
                          "verdict": "PASS"}}

    # C2: native edit space size
    sizes = [len(circuit_edit_space(o["gates"])) for o in objects]
    out["C2_edit_space"] = {"min": min(sizes), "band_min": 500,
                            "verdict": "PASS" if min(sizes) >= 500
                            else "FAIL"}

    # C3: TT exact roundtrip on every object
    bad = 0
    ranks = []
    for o in objects:
        F = (1.0 - 2.0 * o["f"].astype(np.float64)).reshape((2,) * N)
        cores = tt_decompose(F)
        dec = tt_contract(cores)
        f_back = dec < 0
        if not np.array_equal(f_back, o["f"]):
            bad += 1
        ranks.append(max(c.shape[2] for c in cores))
    out["C3_tt_roundtrip"] = {"failures": bad, "n": len(objects),
                              "max_ranks": ranks,
                              "verdict": "PASS" if bad == 0 else "FAIL"}

    # C5: ANF analytic displacement check, 100 sampled toggles
    rng = rng_for(999, 5)
    mism = 0
    for _ in range(100):
        o = objects[int(rng.integers(len(objects)))]
        u = int(rng.integers(DOM))
        a = moebius(o["f"].astype(np.uint8))
        a[u] ^= 1
        f2 = moebius(a).astype(bool)
        d = displacement(o["f"], f2)
        deg = bin(u).count("1")
        if abs(d - 2.0 ** (-deg)) > 1e-12:
            mism += 1
    out["C5_anf_analytic"] = {"mismatches": mism, "n": 100,
                              "verdict": "PASS" if mism == 0 else "FAIL"}

    out["verdict"] = ("PASS" if all(
        v.get("verdict") == "PASS" for k, v in out.items()
        if isinstance(v, dict) and "verdict" in v) else "FAIL")
    return out


# ---------------------------------------------------------------- assay

def assay_native(o, sham=False):
    rows = []
    seed, oi = o["seed"], o["obj"]
    if sham:
        perm = rng_for(seed, 2, oi).permutation(N)
        gates = [(op,
                  int(perm[a]) if a < N else a,
                  int(perm[b]) if b < N else b)
                 for op, a, b in o["gates"]]
        inv = np.argsort(perm)
        f0 = eval_circuit(gates, perm=inv)
        assert np.array_equal(f0, o["f"]), "SHAM same-object violation"
    else:
        gates, inv = o["gates"], None
        f0 = o["f"]
    edits = circuit_edit_space(gates)
    rng = rng_for(seed, 3 if sham else 1, oi)
    for k in range(K_EDITS):
        e = edits[int(rng.integers(len(edits)))]
        f2 = eval_circuit(apply_edit(gates, e), perm=inv)
        rows.append(dict(arm="SHAM" if sham else "NAT", seed=seed, obj=oi,
                         edit=k, d=displacement(f0, f2)))
    return rows, dict(rep_size=G * 3)


def assay_anf(o, scrambled=False):
    rows = []
    seed, oi = o["seed"], o["obj"]
    f = o["f"]
    if scrambled:
        sig = rng_for(seed, 4, oi).permutation(DOM)
        g = f[sig]                     # g = f o sigma
        siginv = np.argsort(sig)
    else:
        g = f
    a0 = moebius(g.astype(np.uint8))
    rng = rng_for(seed, 5 if scrambled else 6, oi)
    for k in range(K_EDITS):
        u = int(rng.integers(DOM))
        a = a0.copy()
        a[u] ^= 1
        g2 = moebius(a).astype(bool)
        f2 = g2[siginv] if scrambled else g2
        rows.append(dict(arm="ANF_SCR" if scrambled else "ANF",
                         seed=seed, obj=oi, edit=k,
                         d=displacement(f, f2)))
    return rows, dict(rep_size=int(a0.sum()))


def assay_vt(o):
    rows = []
    seed, oi = o["seed"], o["obj"]
    rng = rng_for(seed, 7, oi)
    for k in range(K_EDITS):
        x = int(rng.integers(DOM))
        f2 = o["f"].copy()
        f2[x] = ~f2[x]
        rows.append(dict(arm="VT", seed=seed, obj=oi, edit=k,
                         d=displacement(o["f"], f2)))
    return rows, dict(rep_size=DOM)


def assay_tt(o, scrambled=False):
    rows = []
    seed, oi = o["seed"], o["obj"]
    f = o["f"]
    if scrambled:
        rho = rng_for(seed, 8, oi).permutation(DOM)
        vec = (1.0 - 2.0 * f.astype(np.float64))[rho]
        rhoinv = np.argsort(rho)
    else:
        vec = 1.0 - 2.0 * f.astype(np.float64)
    F = vec.reshape((2,) * N)
    cores = tt_decompose(F)
    base = tt_contract(cores)
    f_check = (base[rhoinv] if scrambled else base) < 0
    assert np.array_equal(f_check, f), "TT reconstruction violation"
    rng = rng_for(seed, 9 if scrambled else 10, oi)
    arm = "TT_SCR" if scrambled else "TT"
    for k in range(K_EDITS):
        c = int(rng.integers(len(cores)))
        idx = int(rng.integers(cores[c].size))
        sign = 1.0 if rng.integers(2) else -1.0
        rms = float(np.sqrt(np.mean(cores[c] ** 2)))
        for eps in EPS_GRID:
            pert = [x.copy() for x in cores]
            flat = pert[c].reshape(-1)
            flat[idx] += sign * eps * rms
            dec = tt_contract(pert)
            if scrambled:
                dec = dec[rhoinv]
            f2 = dec < 0
            pre = float(np.linalg.norm(dec - (base[rhoinv] if scrambled
                                              else base)) /
                        np.linalg.norm(base))
            rows.append(dict(arm=arm, seed=seed, obj=oi, edit=k, eps=eps,
                             d=displacement(f, f2), preround_l2=pre,
                             fhash=hash(f2.tobytes())))
    return rows, dict(rep_size=tt_size(cores))


def run_assay(objects):
    all_rows = []
    meta = {}
    for name, fn in (
            ("NAT", lambda o: assay_native(o, sham=False)),
            ("SHAM", lambda o: assay_native(o, sham=True)),
            ("ANF", lambda o: assay_anf(o, scrambled=False)),
            ("ANF_SCR", lambda o: assay_anf(o, scrambled=True)),
            ("VT", assay_vt),
            ("TT", lambda o: assay_tt(o, scrambled=False)),
            ("TT_SCR", lambda o: assay_tt(o, scrambled=True))):
        t0 = time.time()
        sizes = []
        for o in objects:
            rows, m = fn(o)
            all_rows.extend(rows)
            sizes.append(m["rep_size"])
        meta[name] = dict(wall_s=round(time.time() - t0, 2),
                          rep_size_min=min(sizes),
                          rep_size_med=float(np.median(sizes)),
                          rep_size_max=max(sizes))
        print(f"  arm {name:8s} done {meta[name]}", flush=True)
    return all_rows, meta


# ---------------------------------------------------------------- main

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    objects, census_rows = build_objects()
    census = run_census(objects, census_rows)
    with open("results/census.json", "w") as fh:
        json.dump(census, fh, indent=1)
    print("CENSUS:", census["verdict"])
    for k, v in census.items():
        if isinstance(v, dict) and "verdict" in v:
            print(f"  {k}: {v['verdict']}")
    if census["verdict"] != "PASS":
        raise SystemExit("census failed; assay not run")
    if mode == "census":
        return
    rows, meta = run_assay(objects)
    with open("results/rows.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    with open("results/arm_meta.json", "w") as fh:
        json.dump(meta, fh, indent=1)
    print(f"ASSAY: {len(rows)} rows written")


if __name__ == "__main__":
    main()
