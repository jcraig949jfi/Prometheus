"""W-E T-RET-1 retention census (PLAN.md in this directory).

Usage: python ret_census.py [--only NAME ...] [--controls] [--calib] [--nperm N]
Writes out/<name>.json per specimen and out/controls.json / out/calib.json.
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
from prometheus.ananke import assays, c1b_run, envs, lens, plants  # noqa: E402
from prometheus.ananke.engine import Schedule, World  # noqa: E402

torch.set_num_threads(2)
NS = 0x5E9
M = 64
SEEDS = assays.world_seeds(NS, M)
K = 3
LAGS = list(range(7))
DEV = "cpu"
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
FULL = list(lens.SITE_ARRAYS) + list(lens.FLIGHT_ARRAYS)


# ------------------------------------------------------------------ specimens
def specimens():
    sct = json.loads((REPO / "roles/Ananke/research/spikes/out/s_ct.json").read_text())
    out = []
    for r in c1b_run.d_wave_cells():
        par = r["parent"][:8]
        v = sct.get(par, {})
        if v.get("sitestate", {}).get("verdict") == "FLIP":
            cls = "site-state"
        elif v.get("inflight", {}).get("verdict") == "FLIP":
            cls = "in-flight"
        else:
            cls = "joint"
        from prometheus.ananke.physics import Physics
        out.append({"name": "D_" + r["cell_id"][:8], "parent": par, "class": cls,
                    "family": r["env"]["family"], "normal_rec": v.get("normal"),
                    "ph": Physics.from_dict(r["physics"]), "env": envs.EnvSpec(**r["env"]),
                    "g": np.asarray(r["extra"]["genome"], dtype=np.int64)})
    ph, env, _, _ = c1b_run.load("4ab2ba014aac967e")
    m2 = json.loads((REPO / "roles/Ananke/research/spikes/out/champions_m2.json").read_text())
    for k, g in m2.items():
        out.append({"name": "M2_" + k, "parent": "4ab2ba01", "class": "in-flight(M2 pay1)",
                    "family": env.family, "normal_rec": None, "ph": ph, "env": env,
                    "g": np.asarray(g, dtype=np.int64)})
    return out


def control_specs():
    ph, env, _, _ = c1b_run.load("4ab2ba014aac967e")
    neg = plants.plant("hold_latch", ph)
    body = plants.fix_const_shift(plants.hold_latch(ph), 0, 7)
    body = np.concatenate([body[:9], plants.assemble(ph, [("ADD", "S1", "S1", "SENSE", 0)], L=1),
                           np.zeros((ph.prog_len - 10, 5), dtype=np.int64)])
    pos = np.broadcast_to(body, (ph.rules, *body.shape)).copy()
    return [{"name": "C-NEG_hold_latch", "class": "control", "family": env.family, "parent": None,
             "normal_rec": None, "ph": ph, "env": env, "g": neg},
            {"name": "C-POS_integrator", "class": "control", "family": env.family, "parent": None,
             "normal_rec": None, "ph": ph, "env": env, "g": pos}]


# ------------------------------------------------------------------ twins
def twin_setup(ph, env):
    ep = envs.build(ph, env, SEEDS)
    sv = ep.schedule.sense_val.clone()
    sidx, ridx = ep.schedule.sense_idx.clone(), ep.schedule.read_idx.clone()
    Pd = env.period()
    tk0 = K * Pd
    for b in range(1, M, 2):
        sv[:, b] = sv[:, b - 1]
        sv[tk0:tk0 + env.cue_len, b] = -sv[tk0:tk0 + env.cue_len, b - 1]
        sidx[b], ridx[b] = sidx[b - 1], ridx[b - 1]
    # G3: twin schedules differ only at trial K cue ticks
    d = (sv[:, 0::2] != sv[:, 1::2]).any(-1).any(-1).numpy()
    bad = [t for t in np.flatnonzero(d) if not (tk0 <= t < tk0 + env.cue_len)]
    g3 = (len(bad) == 0) and bool(d[tk0:tk0 + env.cue_len].all())
    ws = [SEEDS[m - (m % 2)] for m in range(M)]
    lead = np.arange(0, M, 2)
    ro = ep.ro_tick[lead]                    # [32, trials]
    assert (ro == ro[0]).all()
    ro = ro[0]
    ylead = ep.y[lead]                       # [32, trials]  (lead's schedule for both twins)
    return {"ep": ep, "sch": Schedule(sidx, sv, ridx), "ws": ws, "Pd": Pd, "tk0": tk0,
            "ro": ro, "ylead": ylead, "G3": g3}


def pair_diff(w):
    """per carrier: (#differing elements per pair [32])."""
    res = {}
    for n, a in w.state_arrays().items():
        if n in ("Msum", "Mcnt"):
            x, y = a[:, 0::2], a[:, 1::2]
            dd = (x != y).reshape(x.shape[0], x.shape[1], -1).sum((0, 2))
        else:
            x, y = a[0::2], a[1::2]
            dd = (x != y).reshape(x.shape[0], -1).sum(1)
        res[n] = dd.numpy().astype(np.int64)
    return res


def features(w):
    names, vals = [], []
    D = w.ph.state_dim
    a = w.read_idx[:, 0]
    bi = torch.arange(w.B)
    S = w.S.to(torch.int64)
    for d in range(D):
        names.append(f"S{d}_sum"); vals.append(S[..., d].sum(1))
    for d in range(D):
        names.append(f"S{d}_act"); vals.append(S[bi, a, d])
    names += ["E_sum", "r_sum", "Kp_sum"]
    vals += [w.E.to(torch.int64).sum(1), w.r.to(torch.int64).sum(1), w.Kp.to(torch.int64).sum((1, 2))]
    if w.R:
        names.append("w_sum"); vals.append(w.w.to(torch.int64).sum((1, 2)))
    names += ["inbox_sum", "inbox_cnt"]
    vals += [w.Acc_sum.to(torch.int64).sum((1, 2, 3)), w.Acc_cnt.to(torch.int64).sum((1, 2))]
    Ms = w.Msum.to(torch.int64)
    for p in range(w.ph.payload_width):
        names.append(f"fl_pay{p}"); vals.append(Ms[..., p].sum((0, 2, 3)))
    for p in range(w.ph.payload_width):
        names.append(f"fl_pay{p}_act"); vals.append(Ms[:, bi, a, :, p].sum((0, 2)))
    names.append("fl_cnt"); vals.append(w.Mcnt.to(torch.int64).sum((0, 2, 3)))
    return names, torch.stack(vals).numpy().astype(np.float64)


def run_twins(sp, tw, hooks=None, record=True):
    ph, env = sp["ph"], sp["env"]
    w = World(ph, np.repeat(sp["g"][None], M, 0), tw["ws"], device=DEV, schedule=tw["sch"])
    T = env.T()
    Pd = tw["Pd"]
    ends = {(m + 1) * Pd - 1: m for m in range(env.trials)}
    rec = {"diff": [], "feat": {}}
    hooks = hooks or {}
    for t in range(T):
        w.step()
        if record:
            rec["diff"].append(pair_diff(w))
            if t in ends:
                rec["feat"][ends[t]] = features(w)
        if t in hooks:
            hooks[t](w)
    rec["trace"] = w.trace.numpy()[..., 0]          # [T, B]
    return rec


# ------------------------------------------------------------------ decoders
def _score(pred, y):
    return np.where(pred == 0, 0.5, (pred == y).astype(np.float64))


def single_decoder(X, Ywp, train, test):
    """X [F, W]; Ywp [P, W] world labels +-1 (row 0 = observed); train/test world idx.
    Returns held-out acc [P] of the train-selected feature, and the selected idx [P]."""
    Xt, Yt = X[:, train], Ywp[:, train]
    pos = (Yt == 1).astype(np.float64)
    neg = 1 - pos
    npos = pos.sum(1).clip(min=1)
    nneg = neg.sum(1).clip(min=1)
    mp = (Xt @ pos.T) / npos            # [F, P]
    mn = (Xt @ neg.T) / nneg
    th = (mp + mn) / 2
    s = np.sign(mp - mn)
    tr = _score(np.sign(s[..., None] * (Xt[:, None, :] - th[..., None])), Yt[None]).mean(-1)  # [F,P]
    sel = tr.argmax(0)                  # first max
    Xs = X[:, test]
    pr = np.sign(s[sel, np.arange(len(sel))][:, None] * (Xs[sel] - th[sel, np.arange(len(sel))][:, None]))
    return _score(pr, Ywp[:, test]).mean(-1), sel


def paired_decoder(Dp, Cp, trp, tep):
    """Dp [F, 32] twin differences; Cp [P, 32] pair labels."""
    s = np.sign(Dp[:, trp] @ Cp[:, trp].T)     # [F, P]
    tr = _score(np.sign(s[..., None] * Dp[:, None, trp]), Cp[None, :, trp]).mean(-1)
    sel = tr.argmax(0)
    pr = np.sign(s[sel, np.arange(len(sel))][:, None] * Dp[sel][:, tep])
    return _score(pr, Cp[:, tep]).mean(-1), sel


FOLD_PERM = np.random.default_rng(NS).permutation(32)
FOLDS = [(np.sort(FOLD_PERM[:16]), np.sort(FOLD_PERM[16:])), (np.sort(FOLD_PERM[16:]), np.sort(FOLD_PERM[:16]))]


def w_of(pairs):
    return np.sort(np.concatenate([2 * pairs, 2 * pairs + 1]))


def perm_signs(nperm, seed):
    g = np.random.default_rng(seed)
    P = np.where(g.random((nperm, 32)) < 0.5, -1, 1)
    return np.concatenate([np.ones((1, 32), dtype=np.int64), P])


def test_single(X, c_world_fn, signs, chunk=2000):
    """c_world_fn(signs [P,32]) -> world labels [P,64]. Returns A_obs, p, feature."""
    accs, sel0 = [], None
    for i in range(0, len(signs), chunk):
        S = signs[i:i + chunk]
        Y = c_world_fn(S)
        a = np.zeros(len(S))
        for trp, tep in FOLDS:
            acc, sel = single_decoder(X, Y, w_of(trp), w_of(tep))
            a += acc / 2
            if i == 0 and sel0 is None:
                sel0 = int(sel[0])
        accs.append(a)
    A = np.concatenate(accs)
    return float(A[0]), float((1 + (A[1:] >= A[0]).sum()) / len(A)), sel0


def test_paired(Dp, c, signs, chunk=2000):
    accs, sel0 = [], None
    for i in range(0, len(signs), chunk):
        Cp = signs[i:i + chunk] * c[None]
        a = np.zeros(len(Cp))
        for trp, tep in FOLDS:
            acc, sel = paired_decoder(Dp, Cp, trp, tep)
            a += acc / 2
            if i == 0 and sel0 is None:
                sel0 = int(sel[0])
        accs.append(a)
    A = np.concatenate(accs)
    return float(A[0]), float((1 + (A[1:] >= A[0]).sum()) / len(A)), sel0


# ------------------------------------------------------------------ one specimen
def analyse(sp, nperm, do_swaps=True):
    t0 = time.time()
    ph, env = sp["ph"], sp["env"]
    tw = twin_setup(ph, env)
    rec = run_twins(sp, tw)
    T, Pd, ro = env.T(), tw["Pd"], tw["ro"]
    rk = int(ro[K])
    diffs = rec["diff"]
    carriers = list(diffs[0].keys())
    tot = np.stack([sum(d[n] for n in carriers) for d in diffs])      # [T, 32]
    equal = tot == 0
    # G1: equal before cue onset
    g1 = bool(equal[:tw["tk0"]].all())
    # merge time
    merge, redivg = [], False
    for p in range(32):
        idx = [t for t in range(rk, T) if equal[t, p]]
        if idx:
            t = idx[0]
            if not equal[t:, p].all():
                redivg = True
            merge.append(t - rk)
        else:
            merge.append(None)
    merged_before_ro = int(sum(1 for p in range(32) if equal[tw["tk0"]:rk, p].any()))
    ends = {j: (K + j + 1) * Pd - 1 - rk for j in LAGS}
    frac_merged_by = {j: float(np.mean([m is not None and m <= ends[j] for m in merge])) for j in LAGS}
    frac_ever = float(np.mean([m is not None for m in merge]))
    # per-carrier presence at trial ends
    carrier_pairs = {n: {j: int((diffs[(K + j + 1) * Pd - 1][n] > 0).sum()) for j in LAGS} for n in carriers}
    carrier_elems = {n: {j: float(diffs[(K + j + 1) * Pd - 1][n].mean()) for j in LAGS} for n in carriers}
    # answers
    tr = rec["trace"]
    ans = np.sign(tr[ro])                                   # [trials, 64]
    c = tw["ylead"][:, K].astype(np.int64)                  # [32]
    yk = np.stack([c, -c], 1).reshape(-1)                   # world labels
    # baseline accuracy of the twin run at trial K (sanity)
    acc_k = float(_score(ans[K], yk).mean())
    diff_ans = {j: (ans[K + j, 0::2] != ans[K + j, 1::2]).astype(float) for j in LAGS}
    signed = {j: float(np.mean(c * (ans[K + j, 0::2] - ans[K + j, 1::2]) / 2)) for j in LAGS}
    # decoders
    signs = perm_signs(nperm, NS + 1)
    dec, decp = {}, {}
    for j in LAGS:
        names, X = rec["feat"][K + j]
        A, p, s0 = test_single(X, lambda S: np.stack([S * c, -S * c], 2).reshape(len(S), -1), signs)
        dec[j] = {"acc": A, "p": p, "feature": names[s0]}
        Dp = X[:, 0::2] - X[:, 1::2]
        A2, p2, s2 = test_paired(Dp, c, signs)
        decp[j] = {"acc": A2, "p": p2, "feature": names[s2]}
    # C-POS2: own-trial cue of trial K+1 (shared by twins), end of trial K+1
    names, X = rec["feat"][K + 1]
    c1 = tw["ylead"][:, K + 1].astype(np.int64)
    A, p, s0 = test_single(X, lambda S: np.repeat(S * c1, 2, axis=1), signs[:2001])
    own = {"acc": A, "p": p, "feature": names[s0]}
    # swaps (EFFECTIVE) + G5
    eff, g5 = {}, True
    if do_swaps:
        for j in LAGS:
            tick = (K + j) * Pd - 1
            sw = run_twins(sp, tw, hooks={tick: lambda w: lens.swap(w, FULL)}, record=False)
            a2 = np.sign(sw["trace"][ro[K + j]])
            ch = (a2[0::2] != ans[K + j, 0::2]).astype(float)
            ch2 = (a2[1::2] != ans[K + j, 1::2]).astype(float)
            if j == 0:
                ok = np.array_equal(sw["trace"], tr)
            else:
                ok = (np.array_equal(a2[0::2], ans[K + j, 1::2]) and np.array_equal(a2[1::2], ans[K + j, 0::2]))
            g5 &= bool(ok)
            pairs = np.maximum(ch, ch2)
            eff[j] = {"frac": float(pairs.mean()), "ci": lens.ci(pairs) if pairs.any() else [0.0, 0.0, 0.0]}
    else:
        for j in LAGS:
            pairs = diff_ans[j] if j else np.zeros(32)
            eff[j] = {"frac": float(pairs.mean()), "ci": lens.ci(pairs) if pairs.any() else [0.0, 0.0, 0.0],
                      "from_baseline_identity": True}
    # G4 normal mirrored accuracy
    base = lens.run(ph, sp["g"], env, SEEDS, device=DEV)
    normal = lens.ci(lens.trial_acc(base, range(env.trials)))
    return {"name": sp["name"], "class": sp["class"], "family": sp["family"], "parent": sp["parent"],
            "normal_rec": sp["normal_rec"], "normal_here": normal, "acc_trialK_twinrun": acc_k,
            "Pd": Pd, "ro_k": rk, "T": T, "ends_rel_ro": ends,
            "guards": {"G1": g1, "G2_no_rediverge": not redivg, "G3": tw["G3"], "G5": g5},
            "merged_before_ro": merged_before_ro, "merge_rel_ro": merge,
            "frac_merged_by_end_of_trial_k_plus": frac_merged_by, "frac_ever_merged": frac_ever,
            "carrier_pairs_differing": carrier_pairs, "carrier_mean_elems_differing": carrier_elems,
            "decoder_single": dec, "decoder_paired": decp, "own_trial_control": own,
            "effective": eff, "signed_interference": signed,
            "answer_differs_baseline": {j: float(diff_ans[j].mean()) for j in LAGS},
            "nperm": nperm, "secs": time.time() - t0}


def calib(nrep=200, nperm=2000):
    g = np.random.default_rng(NS + 7)
    ps, pps = [], []
    for r in range(nrep):
        X = g.standard_normal((20, 64))
        c = np.where(g.random(32) < 0.5, -1, 1)
        signs = perm_signs(nperm, NS + 100 + r)
        ps.append(test_single(X, lambda S: np.stack([S * c, -S * c], 2).reshape(len(S), -1), signs)[1])
        pps.append(test_paired(X[:, 0::2] - X[:, 1::2], c, signs)[1])
    ps, pps = np.array(ps), np.array(pps)
    return {"single_frac_p_lt_05": float((ps < 0.05).mean()), "paired_frac_p_lt_05": float((pps < 0.05).mean()),
            "single_frac_p_lt_01": float((ps < 0.01).mean()), "paired_frac_p_lt_01": float((pps < 0.01).mean()),
            "nrep": nrep, "nperm": nperm}


def _js(o):
    if isinstance(o, dict):
        return {str(k): _js(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_js(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--controls", action="store_true")
    ap.add_argument("--calib", action="store_true")
    ap.add_argument("--nperm", type=int, default=20000)
    ap.add_argument("--no-swaps", action="store_true")
    a = ap.parse_args()
    if a.calib:
        r = calib()
        (OUT / "calib.json").write_text(json.dumps(r, indent=1))
        print(r)
        return
    sps = control_specs() if a.controls else specimens()
    for sp in sps:
        if a.only and sp["name"] not in a.only:
            continue
        r = analyse(sp, a.nperm, do_swaps=not a.no_swaps)
        (OUT / f"{sp['name']}.json").write_text(json.dumps(_js(r), indent=1))
        print(sp["name"], sp["class"], "G", r["guards"], "normal", [round(x, 3) for x in r["normal_here"]],
              "merged_by", {j: round(v, 2) for j, v in r["frac_merged_by_end_of_trial_k_plus"].items()},
              "ever", r["frac_ever_merged"],
              "single", {j: (round(v["acc"], 3), round(v["p"], 5)) for j, v in r["decoder_single"].items()},
              "paired", {j: (round(v["acc"], 3), round(v["p"], 5)) for j, v in r["decoder_paired"].items()},
              "eff", {j: round(v["frac"], 3) for j, v in r["effective"].items()},
              "own", r["own_trial_control"], "secs", round(r["secs"], 1), flush=True)


if __name__ == "__main__":
    main()
