"""INV_Z8 -- affine / structured linear-coordinate baselines on the 8 adversarial
ALIEN systems of the alien pilot. Read-only over hecate/alien/data; no model
calls, no network, writes only to the scratch dir given as argv[1] (optional).

Every learner sees exactly baselines._transitions(p, pub) (the 80 observed
transitions the subject saw) and is scored with hecate.alien.score.acc on the
12 T2 queries and on all 200 T5 eval states (Claude's T5 also used 200).

    python roles/Hecate/harvest_w2/INV_Z8_affine_on_maps.py [scratch_dir]
"""

from __future__ import annotations

import itertools
import json
import os
import sys
import time
from math import factorial

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)

from hecate.alien import baselines as B          # noqa: E402
from hecate.alien.dataset import OUT              # noqa: E402
from hecate.alien.score import acc                # noqa: E402
from hecate.alien.systems import all_states, dims_of, step  # noqa: E402


# ---- GF(p) linear algebra ---------------------------------------------------

def gf_solve(A, b, p):
    """Solve A x = b mod p. Returns (consistent, nullity, particular x or None)."""
    A = np.array(A, dtype=np.int64) % p
    b = np.array(b, dtype=np.int64).reshape(-1, 1) % p
    M = np.concatenate([A, b], axis=1)
    rows, cols = A.shape
    piv_cols, r = [], 0
    for c in range(cols):
        nz = np.nonzero(M[r:, c])[0]
        if len(nz) == 0:
            continue
        k = r + nz[0]
        M[[r, k]] = M[[k, r]]
        M[r] = (M[r] * pow(int(M[r, c]), -1, p)) % p
        others = np.nonzero(M[:, c])[0]
        for o in others:
            if o != r:
                M[o] = (M[o] - M[o, c] * M[r]) % p
        piv_cols.append(c)
        r += 1
        if r == rows:
            break
    if np.any(M[r:, cols] % p):
        return False, cols - r, None
    x = np.zeros(cols, dtype=np.int64)
    for i, c in enumerate(piv_cols):
        x[c] = M[i, cols]
    return True, cols - r, x


def monos(d):
    return [(i, j) for i in range(d + 1) for j in range(d + 1 - i)]


def design(S, ms, p):
    S = np.asarray(S, dtype=np.int64)
    return np.stack([(pow_mod(S[:, 0], i, p) * pow_mod(S[:, 1], j, p)) % p for i, j in ms], axis=1)


def pow_mod(v, e, p):
    out = np.ones_like(v)
    for _ in range(e):
        out = (out * v) % p
    return out


# ---- learners: maps (Z_31^2) --------------------------------------------------

P31 = 31


def map_affine_exhaustive(ts):
    """Best-agreement affine per component, ALL (a1, a2, b) in Z_31^3."""
    X = np.array([t[0] for t in ts])
    models = []
    for i in range(2):
        y = np.array([t[1][i] for t in ts])
        best, bc = None, -1
        for a1, a2 in itertools.product(range(P31), repeat=2):
            base = (X @ np.array([a1, a2])) % P31
            cnt = np.bincount((y - base) % P31, minlength=P31)
            b = int(np.argmax(cnt))
            if cnt[b] > bc:
                best, bc = ((a1, a2), b), int(cnt[b])
        models.append((best, bc))
    return models


def map_poly_degree_scan(ts, dmax=12):
    X = np.array([t[0] for t in ts])
    Y = np.array([t[1] for t in ts])
    out = []
    for d in range(1, dmax + 1):
        ms = monos(d)
        D = design(X, ms, P31)
        per = [gf_solve(D, Y[:, i], P31) for i in range(2)]
        out.append({"d": d, "k": len(ms), "consistent": all(c for c, _, _ in per),
                    "nullity": [n for _, n, _ in per], "coef": [x for _, _, x in per], "ms": ms})
    return out


def poly_predict(coef, ms, q):
    D = design(np.array([q]), ms, P31)
    return tuple(int((D @ c)[0] % P31) for c in coef)


def involutions_31():
    """All S in GL(2,31) with S^2 = I, trace 0, det -1 (conjugates of the swap)."""
    out = []
    for a in range(P31):
        for b in range(P31):
            for c in range(P31):
                if (a * a + b * c) % P31 == 1:
                    out.append(np.array([[a, b], [c, (-a) % P31]]))
    return out


def eig_basis(S):
    """Columns e+ (eigval 1), e- (eigval -1) of S over GF(31)."""
    vecs = []
    for lam in (1, P31 - 1):
        K = (S - lam * np.eye(2, dtype=np.int64)) % P31
        for v in ([1, 0], [0, 1]) + tuple([1, t] for t in range(P31)):
            v = np.array(v)
            if not np.any((K @ v) % P31):
                vecs.append(v)
                break
    return np.stack(vecs, axis=1)


def inv2(A):
    det = int((A[0, 0] * A[1, 1] - A[0, 1] * A[1, 0]) % P31)
    di = pow(det, -1, P31)
    return (np.array([[A[1, 1], -A[0, 1]], [-A[1, 0], A[0, 0]]]) * di) % P31


def map_structured(ts, d=3):
    """Linear-coordinate search composed with the family class: for every
    involution S (one coordinate frame A per S, A S A^-1 = swap, up to the
    centraliser which preserves the class), fit z' = (g(x,y), g(y,x)) with g a
    degree-<=d polynomial in z = A s (10 unknowns, 160 equations)."""
    X = np.array([t[0] for t in ts])
    Y = np.array([t[1] for t in ts])
    ms = monos(d)
    H = np.array([[1, 1], [1, P31 - 1]])
    hits = []
    for S in involutions_31():
        E = eig_basis(S)
        A = (H @ inv2(E)) % P31
        Z, Z2 = (X @ A.T) % P31, (Y @ A.T) % P31
        D1 = design(Z, ms, P31)
        D2 = design(Z[:, ::-1], ms, P31)
        ok, nul, g = gf_solve(np.concatenate([D1, D2]), np.concatenate([Z2[:, 0], Z2[:, 1]]), P31)
        if ok:
            hits.append((A, g, nul))
    return hits, len(involutions_31())


def struct_predict(A, g, ms, q):
    Ai = inv2(A)
    z = (A @ np.array(q)) % P31
    gz = (int((design(np.array([z]), ms, P31) @ g)[0] % P31),
          int((design(np.array([z[::-1]]), ms, P31) @ g)[0] % P31))
    return tuple(int(v) for v in (Ai @ np.array(gz)) % P31)


# ---- learners: tab linmix (Z_5^5) ----------------------------------------------

P5 = 5


def proj_functionals(n=5, p=P5):
    out = []
    for v in itertools.product(range(p), repeat=n):
        nz = [x for x in v if x]
        if nz and nz[0] == 1:
            out.append(v)
    return np.array(out, dtype=np.int64)


def normalize(v, p=P5):
    v = np.array(v) % p
    f = next(x for x in v if x)
    return tuple(int(x) for x in (v * pow(int(f), -1, p)) % p)


def tab_structured(ts):
    """Search functionals u (projective) and partners v such that u.(s'-s) is
    a function of (u.s, v.s) on all observed transitions (the latent
    'local table' class seen through an unknown invertible linear map), plus
    conserved functionals (the compensated coordinate)."""
    F = proj_functionals()
    X = np.array([t[0] for t in ts])
    Y = np.array([t[1] for t in ts])
    U = (X @ F.T) % P5                  # (80, 781)
    DU = ((Y - X) @ F.T) % P5
    conserved = [tuple(F[k]) for k in range(len(F)) if not DU[:, k].any()]
    nF = len(F)
    pairs = {}
    for ku in range(nF):
        if not DU[:, ku].any():
            continue
        key = (U[:, ku][None, :] * 5 + U.T) * 5 + DU[:, ku][None, :]   # (781, 80)
        idx = (np.arange(nF)[:, None] * 125 + key).ravel()
        cnt = np.bincount(idx, minlength=nF * 125).reshape(nF, 25, 5)
        okv = np.nonzero(((cnt > 0).sum(axis=2) <= 1).all(axis=1))[0]
        if len(okv):
            pairs[tuple(F[ku])] = [tuple(F[k]) for k in okv]
    return pairs, conserved


def tab_table(ts, u, v):
    tab = {}
    for s, s2 in ts:
        a, b = int(np.dot(u, s) % P5), int(np.dot(v, s) % P5)
        tab[(a, b)] = int(np.dot(u, np.subtract(s2, s)) % P5)
    return tab


def gf_inv(A, p):
    n = len(A)
    ok, _, _ = gf_solve(A, np.zeros(n), p)
    M = np.concatenate([np.array(A) % p, np.eye(n, dtype=np.int64)], axis=1)
    for c in range(n):
        nz = np.nonzero(M[c:, c])[0]
        if len(nz) == 0:
            return None
        k = c + nz[0]
        M[[c, k]] = M[[k, c]]
        M[c] = (M[c] * pow(int(M[c, c]), -1, p)) % p
        for o in range(n):
            if o != c and M[o, c]:
                M[o] = (M[o] - M[o, c] * M[c]) % p
    return M[:, n:]


# ---- learners: vm_long (pc in 0..5, r in Z_7^3) --------------------------------

def vm_hypotheses():
    H = []
    for a, t in itertools.product(range(3), range(6)):
        H.append(("jz", a, t))
        H.append(("jnz", a, t))
    for a, b, z in itertools.product(range(3), repeat=3):
        for k1, k2, e in itertools.product(range(1, 7), range(7), range(7)):
            H.append(("aff", a, b, z, k1, k2, e))
    for a, b in itertools.product(range(3), repeat=2):
        H.append(("tab", a, b))
    return H


def vm_apply(h, s, T=None):
    c, r = s[0], list(s[1:])
    nxt = (c + 1) % 6
    if h[0] == "aff":
        _, a, b, z, k1, k2, e = h
        r[a] = (k1 * r[b] + k2 * r[z] + e) % 7
    elif h[0] == "tab":
        _, a, b = h
        r[a] = T.get(r[b], r[a]) if T is not None else r[a]
    elif h[0] == "jz":
        nxt = h[2] if r[h[1]] == 0 else nxt
    elif h[0] == "jnz":
        nxt = h[2] if r[h[1]] != 0 else nxt
    return tuple([nxt] + r)


def vm_structured(ts):
    H = vm_hypotheses()
    per_pc = {}
    for c in range(6):
        obs = [(s, s2) for s, s2 in ts if s[0] == c]
        cons = []
        for h in H:
            if h[0] == "tab":
                _, a, b = h
                T, ok = {}, True
                for s, s2 in obs:
                    r, r2 = s[1:], s2[1:]
                    if s2[0] != (c + 1) % 6 or any(r2[j] != r[j] for j in range(3) if j != a):
                        ok = False
                        break
                    if T.setdefault(r[b], r2[a]) != r2[a]:
                        ok = False
                        break
                if ok and len(set(T.values())) == len(T):
                    cons.append((h, T, factorial(7 - len(T))))
            elif all(vm_apply(h, s) == tuple(s2) for s, s2 in obs):
                cons.append((h, None, 1))
        per_pc[c] = (len(obs), cons)
    return per_pc


def vm_order(h):
    rank = {"jz": 0, "jnz": 0, "aff": 1, "tab": 2}[h[0][0]]
    simp = 0
    if h[0][0] == "aff":
        _, a, b, z, k1, k2, e = h[0]
        simp = (k2 != 0) + (e != 0) + (k1 != 1)
    return (rank, simp)


# ---- driver ---------------------------------------------------------------------

def score(f, k):
    a = k["answers"]
    q2 = [tuple(s) for s in a["q2_states"]]
    ev = [tuple(s) for s in a["eval_states"]]
    t2 = acc([f(q) for q in q2], [tuple(s) for s in a["t2"]])
    t5 = acc([f(q) for q in ev], [tuple(s) for s in a["eval_next"]])
    return {"t2_exact": t2[0], "t2_comp": t2[1], "eval_exact": t5[0], "eval_comp": t5[1]}


def main():
    scratch = sys.argv[1] if len(sys.argv) > 1 else None
    with open(os.path.join(OUT, "public.json"), encoding="utf-8") as fh:
        public = {e["id"]: e for e in json.load(fh)}
    with open(os.path.join(OUT, "answer_key.json"), encoding="utf-8") as fh:
        key = json.load(fh)
    with open(os.path.join(ROOT, "hecate", "alien", "runs", "claude", "RESULTS.json"), encoding="utf-8") as fh:
        cl = json.load(fh)["rows"]
    res = {}
    adv = sorted(s for s, e in key.items() if e["class"] == "ALIEN_LAWFUL" and e.get("adversarial"))
    for sid in adv:
        k = key[sid]
        p = k["params"]
        dims = dims_of(p)
        ts = B._transitions(p, public[sid])
        r = {"family": p["family"], "kind": (p.get("base") or p).get("kind"), "wrap": p.get("wrap"),
             "n_trans": len(ts), "n_distinct_src": len({t[0] for t in ts}),
             "claude": {"t2_comp": cl[sid]["t2_comp"], "eval_comp": cl[sid]["t5"].get("eval_comp"),
                        "t2_exact": cl[sid]["t2_exact"], "eval_exact": cl[sid]["t5"].get("eval_exact")},
             "learners": {}}
        r["learners"]["identity"] = score(lambda q: tuple(q), k)
        # (1) the pilot's own fit_affine with the max(dims)<=7 gate lifted
        t0 = time.time()
        aff = B.fit_affine(ts, dims)
        r["learners"]["fit_affine_gate_lifted"] = {**score(lambda q: B.pred_affine(aff, q, dims), k),
                                                    "sec": round(time.time() - t0, 2)}
        if p["family"] == "map":
            t0 = time.time()
            am = map_affine_exhaustive(ts)
            models = [m for m, _ in am]
            r["learners"]["affine_full_Z31"] = {
                **score(lambda q: tuple(int((np.dot(c, q) + b) % P31) for (c, b) in models), k),
                "train_agree": [c for _, c in am], "sec": round(time.time() - t0, 2), "evals": 2 * 31 ** 2}
            t0 = time.time()
            scan = map_poly_degree_scan(ts)
            r["poly_scan"] = [{"d": s["d"], "k": s["k"], "consistent": s["consistent"], "nullity": s["nullity"]}
                              for s in scan]
            for d in (3,):
                s = scan[d - 1]
                if s["consistent"]:
                    r["learners"][f"poly_deg{d}_GF31"] = {
                        **score(lambda q: poly_predict(s["coef"], s["ms"], q), k),
                        "nullity": s["nullity"], "sec": round(time.time() - t0, 2)}
            dmin = next((s for s in scan if s["consistent"]), None)
            if dmin:
                r["learners"]["poly_min_degree"] = {
                    **score(lambda q: poly_predict(dmin["coef"], dmin["ms"], q), k),
                    "d": dmin["d"], "nullity": dmin["nullity"]}
            # exhaustive check: deg-3 fit == true step on all 961 states?
            s3 = scan[2]
            if s3["consistent"]:
                r["deg3_fit_equals_truth_on_all_961"] = all(
                    poly_predict(s3["coef"], s3["ms"], q) == step(p, q) for q in all_states(dims))
            t0 = time.time()
            hits, nS = map_structured(ts)
            r["struct"] = {"involutions_searched": nS, "consistent_frames": len(hits),
                           "nullities": [h[2] for h in hits], "sec": round(time.time() - t0, 2)}
            if hits:
                A, g, _ = hits[0]
                ms = monos(3)
                r["learners"]["struct_linframe_symdeg3"] = {
                    **score(lambda q: struct_predict(A, g, ms, q), k), "sec": r["struct"]["sec"]}
                Mi = np.array(p["Minv"])
                r["struct"]["true_frame_found"] = any(
                    np.array_equal((inv2(A) @ np.array([[0, 1], [1, 0]]) @ A) % P31,
                                   (np.array(p["M"]) @ np.array([[0, 1], [1, 0]]) @ Mi) % P31) for A, _, _ in hits)
        elif p["family"] == "tab":
            t0 = time.time()
            pairs, conserved = tab_structured(ts)
            Mi = np.array(p["Minv"])
            base = p["base"]
            c = base["comp"]
            true_rows = [normalize(Mi[i]) for i in range(5) if i != c]
            true_nb = {normalize(Mi[i]): normalize(Mi[base["nb"][i]]) for i in range(5) if i != c}
            omega = normalize((np.array(base["w"]) @ Mi) % P5)
            st = {"u_with_partner": len(pairs), "pairs": sum(len(v) for v in pairs.values()),
                  "conserved_functionals": len(conserved), "true_omega_found": omega in conserved,
                  "true_rows_found": sum(u in pairs for u in true_rows),
                  "true_rows_with_true_partner": sum(u in pairs and true_nb[u] in pairs[u] for u in true_rows),
                  "partners_per_true_row": [len(pairs.get(u, [])) for u in true_rows]}
            # assemble every invertible choice of 4 u's (+ the conserved omega) and score it
            us = sorted(pairs)
            preds = []
            if len(conserved) == 1:
                om = conserved[0]
                n_inv = 0
                for combo in itertools.combinations(us, 4):
                    A = np.array(list(combo) + [om]) % P5
                    if gf_inv(A, P5) is None:
                        continue
                    n_inv += 1
                    if n_inv > 20000:
                        break
                    preds.append(combo)
                st["invertible_assemblies"] = n_inv
            st["sec_search"] = round(time.time() - t0, 2)
            # score: the true-row assembly with its first-listed consistent partner (oracle pick)
            # and every assembly (distribution), partner = first consistent v per u
            def mk(combo, partner_pick):
                tabs = []
                for u in combo:
                    v = partner_pick(u)
                    tabs.append((u, (v, tab_table(ts, u, v))))
                rows = [u for u, _ in tabs]
                vv = [t for _, t in tabs]

                def f(q):
                    A = np.array(list(rows) + [conserved[0]]) % P5
                    Ai = gf_inv(A, P5)
                    z = (A @ np.array(q)) % P5
                    z2 = z.copy()
                    for kk, (v, tab) in enumerate(vv):
                        z2[kk] = (z[kk] + tab.get((int(z[kk]), int(np.dot(v, q) % P5)), 0)) % P5
                    return tuple(int(x) for x in (Ai @ z2) % P5)
                return f
            if preds:
                scores = [score(mk(cb, lambda u: pairs[u][0]), k) for cb in preds[:2000]]
                ec = [s["eval_comp"] for s in scores]
                st["assemblies_scored"] = len(scores)
                st["assembly_eval_comp_min_med_max"] = [min(ec), float(np.median(ec)), max(ec)]
                st["assembly_t2_comp_med"] = float(np.median([s["t2_comp"] for s in scores]))
                r["learners"]["struct_assembly_median"] = {"eval_comp": float(np.median(ec)),
                                                           "t2_comp": st["assembly_t2_comp_med"]}
            if st["true_rows_found"] == 4 and len(conserved) >= 1:
                f = mk(true_rows, lambda u: true_nb[u] if true_nb[u] in pairs[u] else pairs[u][0])
                r["learners"]["struct_true_frame_ORACLE_PICK"] = score(f, k)
            st["sec_total"] = round(time.time() - t0, 2)
            r["struct"] = st
        else:
            t0 = time.time()
            per = vm_structured(ts)
            pick = {}
            st = {"per_pc": {}}
            for c_, (nobs, cons) in per.items():
                n_h = sum(m for _, _, m in cons)
                st["per_pc"][c_] = {"obs": nobs, "consistent": n_h,
                                    "true": json.dumps(p["program"][c_])[:40]}
                pick[c_] = min(cons, key=vm_order) if cons else None
            prog = p["program"]

            def true_match(c_):
                h, T, _ = pick[c_]
                ins = prog[c_]
                return list(h) == ins[:len(h)] if h[0] != "tab" else (ins[0] == "tab" and list(h[1:]) == ins[1:3])
            st["picked_equals_true"] = sum(true_match(c_) for c_ in range(6) if pick[c_])

            def f(q):
                h, T, _ = pick[q[0]]
                return vm_apply(h, q, T)
            r["learners"]["struct_vm_grammar"] = {**score(f, k), "sec": round(time.time() - t0, 2)}
            r["struct"] = st
        res[sid] = r
        print(sid, json.dumps({kk: v for kk, v in r.items() if kk not in ("poly_scan",)}, default=str)[:1500])
        sys.stdout.flush()
    if scratch:
        os.makedirs(scratch, exist_ok=True)
        with open(os.path.join(scratch, "INV_Z8_results.json"), "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, default=str)
    return res


if __name__ == "__main__":
    main()
