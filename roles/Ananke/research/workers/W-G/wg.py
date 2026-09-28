"""W-G retention confirmation (PLAN.md in this directory).

Usage: python wg.py --ns 0x5EB [--only NAME ...] [--controls] [--nperm N]
Writes out/<nsname>/<name>.json. Between-tick hooks only; engine untouched.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

import numpy as np
import torch

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO))
from prometheus.ananke import assays, c1b_run, envs, plants  # noqa: E402
from prometheus.ananke.engine import Schedule, World  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402

torch.set_num_threads(2)
M = 64
NP = 32
K = 3
J = [2, 3, 4, 5, 6]
J3 = [1, 2, 3, 4, 5, 6]
import os
DEV = os.environ.get("WG_DEV", "cpu")
GROUPS = {"S": ["S"], "Kp": ["Kp"], "w": ["w"], "E": ["E"], "r": ["r"],
          "inbox": ["Acc_sum", "Acc_cnt"], "flight": ["Msum", "Mcnt"]}
FLIGHT = ("Msum", "Mcnt")


# ------------------------------------------------------------------ specimens
def specimens():
    out = []
    for r in c1b_run.d_wave_cells():
        out.append({"name": "D_" + r["cell_id"][:8], "cell": r["cell_id"], "family": r["env"]["family"],
                    "ph": Physics.from_dict(r["physics"]), "env": envs.EnvSpec(**r["env"]),
                    "g": np.asarray(r["extra"]["genome"], dtype=np.int64)})
    ph, env, _, _ = c1b_run.load("4ab2ba014aac967e")
    m2 = json.loads((REPO / "roles/Ananke/research/spikes/out/champions_m2.json").read_text())
    for k, g in m2.items():
        out.append({"name": "M2_" + k, "cell": "4ab2ba014aac967e/" + k, "family": env.family, "ph": ph,
                    "env": env, "g": np.asarray(g, dtype=np.int64)})
    return out


def _latch(dst):
    return [("CONST", "T0", 0, 7, 1), ("GT", "T2", "SENSE", "T0", 0), ("SUB", "T1", "ZERO", "T0", 0),
            ("GT", "T3", "T1", "SENSE", 0), ("SUB", "T1", "T2", "T3", 0), ("MULQ", "T2", "T1", "T1", 0),
            ("SUB", "T3", "T1", dst, 0), ("MULQ", "T3", "T3", "T2", 0), ("ADD", dst, dst, "T3", 0)]


def control_specs():
    ph0, env, _, _ = c1b_run.load("4ab2ba014aac967e")
    ph = ph0.replace(state_dim=4, prog_len=24)
    progs = {
        "C-NEG": _latch("S0"),
        "C-INT": _latch("S0") + [("ADD", "S1", "S1", "SENSE", 0)],
        "C-EFF": [("ADD", "S0", "S0", "SENSE", 0)],
        "C-AVL": _latch("S0") + [("ADDI", "T0", "ZERO", 0, 0), ("ADD", "T0", "T0", "SENSE", 0),
                                 ("CONST", "T1", 0, 0, 9), ("WIMM", "T3", "T1", "T0", 0),
                                 ("MULQ", "T2", "S0", "S0", 0), ("SEL", "T2", "S0", "T0", 0),
                                 ("MOV", "S0", "T2", 0, 0)],
        "C-CHAOS": _latch("S2") + [("ADD", "S1", "S1", "SENSE", 0), ("MULQ", "T0", "S1", "S1", 0),
                                   ("XOR", "S1", "S1", "T0", 0), ("ADDI", "S1", "S1", 0, 77),
                                   ("CONST", "T1", 0, 0, 1023), ("MOD", "T0", "S1", "T1", 0),
                                   ("ADDI", "T0", "T0", 0, -512), ("ADD", "S0", "S2", "T0", 0)],
    }
    assert len(progs["C-AVL"]) == 16  # WIMM index 9 = the ADDI reader line
    out = []
    for n, lines in progs.items():
        body = plants.assemble(ph, lines)
        g = np.broadcast_to(body, (ph.rules, *body.shape)).copy()
        out.append({"name": n, "cell": "plant", "family": env.family, "ph": ph, "env": env, "g": g})
    return out


# ------------------------------------------------------------------ twins + probes
def twin_setup(ph, env, seeds, probe=None):
    ep = envs.build(ph, env, seeds)
    sv = ep.schedule.sense_val.clone()
    sidx, ridx = ep.schedule.sense_idx.clone(), ep.schedule.read_idx.clone()
    Pd = env.period()
    tk0 = K * Pd
    for b in range(1, M, 2):
        sv[:, b] = sv[:, b - 1]
        sidx[b], ridx[b] = sidx[b - 1], ridx[b - 1]
    t2 = (K + 2) * Pd
    if probe in ("BLANK", "PING", "CLEAR_S0", "CLEAR_FAST"):
        orig = sv[t2:t2 + env.cue_len].clone()
        sv[t2:] = 0
        if probe == "PING":
            sv[t2:t2 + env.cue_len] = torch.div(orig, 4, rounding_mode="floor")
    for b in range(1, M, 2):
        sv[tk0:tk0 + env.cue_len, b] = -sv[tk0:tk0 + env.cue_len, b - 1]
    d = (sv[:, 0::2] != sv[:, 1::2]).any(-1).any(-1).numpy()
    bad = [t for t in np.flatnonzero(d) if not (tk0 <= t < tk0 + env.cue_len)]
    g3 = (len(bad) == 0) and bool(d[tk0:tk0 + env.cue_len].all())
    ws = [seeds[m - (m % 2)] for m in range(M)]
    lead = np.arange(0, M, 2)
    ro = ep.ro_tick[lead]
    assert (ro == ro[0]).all()
    return {"ep": ep, "sch": Schedule(sidx, sv, ridx), "ws": ws, "Pd": Pd, "tk0": tk0,
            "ro": ro[0], "ylead": ep.y[lead], "G3": g3}


def all_equal(w):
    eq = torch.ones(NP, dtype=torch.bool, device=w.dev)
    for n, a in w.state_arrays().items():
        if n in FLIGHT:
            x, y = a[:, 0::2], a[:, 1::2]
            eq &= (x == y).permute(1, 0, *range(2, x.dim())).reshape(NP, -1).all(1)
        else:
            eq &= (a[0::2] == a[1::2]).reshape(NP, -1).all(1)
    return eq.cpu().numpy()


def diff_vec(w):
    """per pair: concatenated (lead - twin) over all carriers, int64 [32, X]."""
    parts = []
    for n, a in sorted(w.state_arrays().items()):
        a = a.to(torch.int64)
        if n in FLIGHT:
            d = (a[:, 0::2] - a[:, 1::2]).permute(1, 0, *range(2, a.dim())).reshape(NP, -1)
        else:
            d = (a[0::2] - a[1::2]).reshape(NP, -1)
        parts.append(d)
    return torch.cat(parts, 1).cpu().numpy()


def carrier_diff_pairs(w):
    res = {}
    for g, names in GROUPS.items():
        tot = np.zeros(NP, dtype=np.int64)
        for n in names:
            if n == "w" and not w.R:
                continue
            a = getattr(w, n)
            if n in FLIGHT:
                x = (a[:, 0::2] != a[:, 1::2]).permute(1, 0, *range(2, a.dim())).reshape(NP, -1)
            else:
                x = (a[0::2] != a[1::2]).reshape(NP, -1)
            tot += x.sum(1).cpu().numpy()
        res[g] = tot
    return res


def features(w):
    names, vals = [], []
    D = w.ph.state_dim
    bi = torch.arange(w.B, device=w.dev)
    a = w.read_idx[:, 0]
    s0 = w.sch_idx[:, 0]
    S = w.S.to(torch.int64)
    for d in range(D):
        names.append(f"S{d}_sum"); vals.append(S[..., d].sum(1))
    for d in range(D):
        names.append(f"S{d}_act"); vals.append(S[bi, a, d])
    for d in range(D):
        names.append(f"S{d}_sen"); vals.append(S[bi, s0, d])
    E, Kp = w.E.to(torch.int64), w.Kp.to(torch.int64)
    names += ["E_sum", "r_sum", "Kp_sum", "E_sen", "E_act", "Kp_sen", "Kp_act"]
    vals += [E.sum(1), w.r.to(torch.int64).sum(1), Kp.sum((1, 2)), E[bi, s0], E[bi, a],
             Kp[bi, s0].sum(-1), Kp[bi, a].sum(-1)]
    if w.R:
        W = w.w.to(torch.int64)
        names += ["w_sum", "w_sen", "w_act"]
        vals += [W.sum((1, 2)), W[bi, s0].sum(-1), W[bi, a].sum(-1)]
    names += ["inbox_sum", "inbox_cnt"]
    vals += [w.Acc_sum.to(torch.int64).sum((1, 2, 3)), w.Acc_cnt.to(torch.int64).sum((1, 2))]
    Ms = w.Msum.to(torch.int64)
    for p in range(w.ph.payload_width):
        names.append(f"fl_pay{p}"); vals.append(Ms[..., p].sum((0, 2, 3)))
        names.append(f"fl_pay{p}_act"); vals.append(Ms[:, bi, a, :, p].sum((0, 2)))
    names.append("fl_cnt"); vals.append(w.Mcnt.to(torch.int64).sum((0, 2, 3)))
    return names, torch.stack(vals).cpu().numpy().astype(np.float64)


def run(sp, tw, hooks=None, record=False):
    ph, env = sp["ph"], sp["env"]
    w = World(ph, np.repeat(sp["g"][None], M, 0), tw["ws"], device=DEV, schedule=tw["sch"])
    T, Pd = env.T(), tw["Pd"]
    ends = {(m + 1) * Pd - 1: m for m in range(env.trials)}
    ro_set = {int(t): i for i, t in enumerate(tw["ro"])}
    rec = {"eq": [], "feat": {}, "cdiff": {}, "dvec": {}, "reloc": {}}
    hooks = hooks or {}
    bi = torch.arange(M, device=w.dev)
    for t in range(T):
        w.step()
        if record:
            rec["eq"].append(all_equal(w))
            if t in ends:
                m = ends[t]
                rec["feat"][m] = features(w)
                rec["cdiff"][m] = carrier_diff_pairs(w)
                if m in (K + 2, K + 6):
                    rec["dvec"][m] = diff_vec(w)
            if t in ro_set:
                S = w.S
                rec["reloc"][ro_set[t]] = {"act": S[bi, w.read_idx[:, 0]].cpu().numpy(),
                                            "sen": S[bi, w.sch_idx[:, 0]].cpu().numpy()}
        if t in hooks:
            hooks[t](w)
    rec["trace"] = w.trace.cpu().numpy()[..., 0].copy()
    rec["final_eq"] = all_equal(w)
    return rec


# ------------------------------------------------------------------ statistics
def perm_signs(nperm, seed):
    g = np.random.default_rng(seed)
    P = np.where(g.random((nperm, NP)) < 0.5, -1, 1)
    return np.concatenate([np.ones((1, NP), dtype=np.int64), P])


def pval(T):
    return float((1 + (T[1:] >= T[0] - 1e-12).sum()) / len(T))


def g_of(ans, c):
    """ans [64] answers (sign) -> g [32]."""
    return c * (ans[0::2] - ans[1::2]) / 2.0


def signed_test(G, signs, Y=None):
    """G [L, 32] g per lag; Y [L, 32] optional conditioning signs.
    T = max_l |sum s g| (+ |sum s y g|); sign flips per pair across lags."""
    T = np.abs(signs @ G.T)                    # [P, L]
    if Y is not None:
        T = T + np.abs(signs @ (G * Y).T)
    T = T.max(1)
    return float(T[0]), pval(T)


def _score(pred, y):
    return np.where(pred == 0, 0.5, (pred == y).astype(np.float64))


def single_decoder(X, Ywp, train, test):
    Xt, Yt = X[:, train], Ywp[:, train]
    pos = (Yt == 1).astype(np.float64)
    neg = 1 - pos
    mp = (Xt @ pos.T) / pos.sum(1).clip(min=1)
    mn = (Xt @ neg.T) / neg.sum(1).clip(min=1)
    th = (mp + mn) / 2
    s = np.sign(mp - mn)
    tr = _score(np.sign(s[..., None] * (Xt[:, None, :] - th[..., None])), Yt[None]).mean(-1)
    sel = tr.argmax(0)
    ar = np.arange(len(sel))
    pr = np.sign(s[sel, ar][:, None] * (X[sel][:, test] - th[sel, ar][:, None]))
    return _score(pr, Ywp[:, test]).mean(-1), sel


def hist_decoder(X, H, Yk, train, test):
    P = Yk.shape[0]
    F = X.shape[0]
    tr = np.zeros((F, P))
    te = np.zeros((F, P))
    Htr = H[train]
    W = len(train)
    for P0 in range(0, P, 4000):
        Y = Yk[P0:P0 + 4000]
        p = len(Y)
        D = np.concatenate([np.ones((p, W, 1)), Y[:, train, None], np.broadcast_to(Htr, (p, *Htr.shape))], 2)
        A = np.einsum("pwi,pwj->pij", D, D) + 1e-6 * np.eye(D.shape[2])
        for f in range(F):
            b = np.linalg.solve(A, np.einsum("pwi,w->pi", D, X[f, train])[..., None])[..., 0]

            def pred(idx):
                r = X[f, idx][None] - b[:, :1] - (H[idx] @ b[:, 2:].T).T
                return np.sign(b[:, 1:2] * r)
            tr[f, P0:P0 + p] = _score(pred(train), Y[:, train]).mean(-1)
            te[f, P0:P0 + p] = _score(pred(test), Y[:, test]).mean(-1)
    sel = tr.argmax(0)
    return te[sel, np.arange(P)], sel


def paired_decoder(Dp, Cp, trp, tep):
    s = np.sign(Dp[:, trp] @ Cp[:, trp].T)
    tr = _score(np.sign(s[..., None] * Dp[:, None, trp]), Cp[None, :, trp]).mean(-1)
    sel = tr.argmax(0)
    pr = np.sign(s[sel, np.arange(len(sel))][:, None] * Dp[sel][:, tep])
    return _score(pr, Cp[:, tep]).mean(-1), sel


def folds(ns):
    fp = np.random.default_rng(ns).permutation(NP)
    return [(np.sort(fp[:16]), np.sort(fp[16:])), (np.sort(fp[16:]), np.sort(fp[:16]))]


def w_of(pairs):
    return np.sort(np.concatenate([2 * pairs, 2 * pairs + 1]))


def decode_all(rec, tw, c, signs, ns):
    FO = folds(ns)
    Yw = np.stack([signs * c, -signs * c], 2).reshape(len(signs), -1).astype(float)
    per = {"D1": {}, "D2": {}, "PAIR": {}}
    acc = {"D1": [], "D2": [], "PAIR": []}
    for j in J:
        names, X = rec["feat"][K + j]
        a1 = np.zeros(len(signs)); a2 = np.zeros(len(signs)); a3 = np.zeros(len(signs))
        others = [m for m in range(K + j + 1) if m != K]
        H = np.repeat(tw["ylead"][:, others].astype(float), 2, axis=0)
        Dp = X[:, 0::2] - X[:, 1::2]
        Cp = signs * c[None]
        s1 = s2 = s3 = None
        for trp, tep in FO:
            x, s = single_decoder(X, Yw, w_of(trp), w_of(tep)); a1 += x / 2; s1 = s1 if s1 is not None else int(s[0])
            x, s = hist_decoder(X, H, Yw, w_of(trp), w_of(tep)); a2 += x / 2; s2 = s2 if s2 is not None else int(s[0])
            x, s = paired_decoder(Dp, Cp, trp, tep); a3 += x / 2; s3 = s3 if s3 is not None else int(s[0])
        for key, a, s in (("D1", a1, s1), ("D2", a2, s2), ("PAIR", a3, s3)):
            per[key][j] = {"acc": float(a[0]), "feature": names[s]}
            acc[key].append(a)
    out = {}
    for key in acc:
        A = np.stack(acc[key], 1).max(1)
        out[key] = {"maxacc": float(A[0]), "p": pval(A), "per_lag": per[key]}
    return out


def hist_ratio(rec, tw, c, j=6):
    """Full-data history regression of every feature at end of trial k+j;
    feature with best in-sample D2 accuracy; ratio median_{m!=k}|b_m| / |b_k|."""
    names, X = rec["feat"][K + j]
    Y = np.repeat(tw["ylead"][:, :K + j + 1].astype(float), 2, axis=0)
    ck = np.stack([c, -c], 1).reshape(-1).astype(float)
    Y[:, K] = ck
    D = np.concatenate([np.ones((M, 1)), Y], 1)
    best = None
    for f in range(X.shape[0]):
        if np.ptp(X[f]) == 0:
            continue
        b, *_ = np.linalg.lstsq(D, X[f], rcond=None)
        others = np.delete(b[1:], K)
        r = X[f] - D @ b + b[1 + K] * Y[:, K]
        acc = float(_score(np.sign(b[1 + K] * r), ck).mean())
        if best is None or acc > best[0]:
            ratio = float(np.median(np.abs(others)) / max(abs(b[1 + K]), 1e-9))
            same = float(np.mean(np.sign(others) == np.sign(b[1 + K])))
            best = (acc, names[f], ratio, same, float(b[1 + K]))
    return None if best is None else {"acc_in_sample": best[0], "feature": best[1], "ratio": best[2],
                                      "frac_same_sign": best[3], "b_k": best[4]}


# ------------------------------------------------------------------ one specimen
def analyse(sp, ns, nperm):
    t0 = time.time()
    ph, env = sp["ph"], sp["env"]
    seeds = assays.world_seeds(ns, M)
    tw = run_tw = twin_setup(ph, env, seeds)
    Pd, ro, T = tw["Pd"], tw["ro"], env.T()
    c = tw["ylead"][:, K].astype(np.int64)
    signs = perm_signs(nperm, ns + 1)
    rec = run(sp, tw, record=True)
    eq = np.stack(rec["eq"])                      # [T, 32]
    g1 = bool(eq[:tw["tk0"]].all())
    redivg = False
    for p in range(NP):
        idx = np.flatnonzero(eq[int(ro[K]):, p])
        if idx.size and not eq[int(ro[K]) + idx[0]:, p].all():
            redivg = True
    ndiff = {j: int((~eq[(K + j + 1) * Pd - 1]).sum()) for j in range(0, 7)}
    L1 = ndiff[2] >= 4
    L1p = L1 and ndiff[6] >= 4
    carriers = {j: {g: int((v > 0).sum()) for g, v in rec["cdiff"][K + j].items()} for j in range(0, 7)}
    # form
    dv2, dv6 = rec["dvec"][K + 2], rec["dvec"][K + 6]
    both = (np.abs(dv2).sum(1) > 0) & (np.abs(dv6).sum(1) > 0)
    frozen = float(np.mean([(dv2[p] == dv6[p]).all() for p in np.flatnonzero(both)])) if both.any() else None
    nel = {"k+2_median_elems": float(np.median((dv2 != 0).sum(1))), "k+6_median_elems": float(np.median((dv6 != 0).sum(1)))}
    # scar sign consistency: sign of summed difference * c
    sgn = np.sign(dv6.sum(1)) * c
    scar_sign = {"pos": int((sgn > 0).sum()), "neg": int((sgn < 0).sum()), "zero_or_same": int((sgn == 0).sum())}
    # answers, L3
    ans = np.sign(rec["trace"][ro])               # [trials, 64]
    G3 = np.stack([g_of(ans[K + j], c) for j in J3])
    Y3 = np.stack([tw["ylead"][:, K + j] for j in J3]).astype(float)
    T3, p3 = signed_test(G3, signs, Y3)
    unsigned = {j: float((ans[K + j, 0::2] != ans[K + j, 1::2]).mean()) for j in J3}
    L3_desc = {j: {"sum_g": float(G3[i].sum()), "sum_yg": float((G3[i] * Y3[i]).sum())} for i, j in enumerate(J3)}
    # decoders (L2, L1.5)
    dec = decode_all(rec, tw, c, signs, ns)
    # probes (L4)
    probes = {}
    hook_t = (K + 2) * Pd - 1

    def clear_s0(w):
        w.S[..., 0] = 0

    def clear_fast(w):
        for n in ("S", "Acc_sum", "Acc_cnt", "Msum", "Mcnt"):
            getattr(w, n).zero_()
    for pr, hook in (("BLANK", None), ("PING", None), ("CLEAR_S0", clear_s0), ("CLEAR_FAST", clear_fast)):
        tp = twin_setup(ph, env, seeds, probe=pr)
        rp = run(sp, tp, hooks={hook_t: hook} if hook else None)
        a = np.sign(rp["trace"][ro])
        G = np.stack([g_of(a[K + j], c) for j in J])
        Y = np.stack([np.sign(tp["sch"].sense_val[(K + 2) * Pd, 0::2].sum(-1).numpy())] * len(J)).astype(float) \
            if pr == "PING" else None
        Tp, pp = signed_test(G, signs, Y)
        probes[pr] = {"T": Tp, "p": pp, "G3": tp["G3"],
                      "per_lag": {j: {"sum_g": float(G[i].sum()), "n_diff": int((G[i] != 0).sum())} for i, j in enumerate(J)}}
    # P5 RELOC
    Gs, keys = [], []
    for j in J:
        R = rec["reloc"][K + j]
        for role in ("act", "sen"):
            for d in range(ph.state_dim):
                Gs.append(g_of(np.sign(R[role][:, d]), c)); keys.append((j, role, d))
    Gs = np.stack(Gs)
    Tp, pp = signed_test(Gs, signs)
    best = int(np.abs(Gs.sum(1)).argmax())
    probes["RELOC"] = {"T": Tp, "p": pp, "best": {"j": keys[best][0], "role": keys[best][1], "d": keys[best][2],
                                                  "sum_g": float(Gs[best].sum()), "n_diff": int((Gs[best] != 0).sum())}}
    # heal tests (locus)
    heal = {}
    if L1:
        before = ~eq[(K + 3) * Pd - 1]
        for gname, names in GROUPS.items():
            if gname == "w" and not ph.plastic_route:
                pass

            def hk(w, names=names):
                for n in names:
                    if n == "w" and not w.R:
                        continue
                    a = getattr(w, n)
                    if n in FLIGHT:
                        a[:, 1::2] = a[:, 0::2]
                    else:
                        a[1::2] = a[0::2]
            nb = int(before.sum())
            if rec["cdiff"][K + 2][gname].sum() == 0:
                fe = rec["final_eq"]            # X identical in every pair: heal is a no-op
            else:
                fe = run(sp, tw, hooks={(K + 3) * Pd - 1: hk})["final_eq"]
            heal[gname] = {"n_before": nb, "merged_at_end": int((fe & before).sum()),
                           "frac": float((fe & before).sum() / max(nb, 1))}
    suff = [g for g, v in heal.items() if v["n_before"] and v["frac"] >= 0.9]
    hr = hist_ratio(rec, tw, c)
    # G4
    from prometheus.ananke import lens
    base = lens.run(ph, sp["g"], env, seeds, device=DEV)
    normal = lens.ci(lens.trial_acc(base, range(env.trials)))
    return {"name": sp["name"], "cell": sp["cell"], "family": sp["family"], "ns": hex(ns), "nperm": nperm,
            "guards": {"G1": g1, "G2_no_rediverge": not redivg, "G3": tw["G3"],
                       "G3_probes": all(v.get("G3", True) for v in probes.values())},
            "normal_acc_ci": normal, "ndiff_pairs_end_trial_k+j": ndiff, "L1": L1, "L1_persistent": L1p,
            "carrier_pairs_differing": carriers, "frozen_frac_k2_vs_k6": frozen, "elems": nel,
            "scar_sign_vs_cue_k+6": scar_sign,
            "L3": {"T": T3, "p": p3, "per_lag": L3_desc, "unsigned_answer_diff": unsigned},
            "decoders": dec, "probes": probes, "heal": heal, "sufficient_stores": suff, "hist_ratio": hr,
            "secs": time.time() - t0}


def _js(o):
    if isinstance(o, dict):
        return {str(k): _js(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_js(v) for v in o]
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ns", required=True)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--controls", action="store_true")
    ap.add_argument("--nperm", type=int, default=20000)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    ns = int(a.ns, 16)
    od = HERE / "out" / (hex(ns) + a.tag)
    od.mkdir(parents=True, exist_ok=True)
    sps = control_specs() if a.controls else specimens()
    for sp in sps:
        if a.only and sp["name"] not in a.only:
            continue
        r = analyse(sp, ns, a.nperm)
        (od / f"{sp['name']}.json").write_text(json.dumps(_js(r), indent=1))
        d = r["decoders"]
        print(sp["name"], "G", r["guards"], "acc", [round(x, 3) for x in r["normal_acc_ci"]],
              "ndiff", r["ndiff_pairs_end_trial_k+j"], "frozen", r["frozen_frac_k2_vs_k6"],
              "L3", (round(r["L3"]["T"], 1), r["L3"]["p"]),
              "D1", (round(d["D1"]["maxacc"], 3), d["D1"]["p"]), "D2", (round(d["D2"]["maxacc"], 3), d["D2"]["p"]),
              "PAIR", (round(d["PAIR"]["maxacc"], 3), d["PAIR"]["p"]),
              "probes", {k: (round(v["T"], 1), v["p"]) for k, v in r["probes"].items()},
              "suff", r["sufficient_stores"], "hr", r["hist_ratio"], "secs", round(r["secs"]), flush=True)


if __name__ == "__main__":
    main()
