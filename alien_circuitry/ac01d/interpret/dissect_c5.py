"""Interpretation of the FROZEN C5-medium model (ruling sections 7-11).  The model is never modified or retrained.

Sections
  P  representation dissection: ridge probes (closed-form, no gradient) from frozen hidden layers to known quantities on
     HELD data -- rank, image multiplicities (count vector), block-size multiset, kernel partition (21 pairwise bits),
     minimal collapses (rank f - rank t), exact D, successor D differences, shortest-action identity.  Reported as R^2 /
     accuracy of the PROBE, separately from the model.  Layer 0 = concatenated embeddings (224); layer 1 = first ReLU
     (256); layer 2 = second ReLU (256).
  A  causal ablations without retraining: zero each embedding position (state digit m, target digit m) and each hidden
     unit group (16 groups of 16) and measure D-prediction R^2, shortest-action top-1 and AC-01R PR-AUC on HELD_BOTH.
  S  symmetry: T_7 relabelling.  For a permutation pi of values: f -> pi o f o pi^-1 is an automorphism of the left action
     (it commutes with the generators only if pi fixes the generator set; for general pi it maps the universe to an
     isomorphic one with relabelled generators).  The action metric is invariant under simultaneous relabelling of
     values in f and t.  Measured: |Dhat(pi f pi^-1, pi t pi^-1) - Dhat(f, t)| for random pi, and for pi in the subgroup
     that fixes {0,1} setwise (which fixes the generator set exactly).
  R  C5 vs CP rank 16 per problem: HC_D contribution partition and residual characterisation.
Outputs results/ac01d/interpret/C5_dissection.json.
"""
from __future__ import annotations
import itertools, json, os
import numpy as np
import torch
from ..corpus import build
from ..families.c2_cp import digit_index
from ..families.c5_learned import DigitNet, DEV
from ...gate2 import analysis2 as A

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WDIR = os.path.join(HERE, "results", "ac01d", "families", "weights")
FIT_MEAN = 16.7334  # re-derived in the forensic audit from FIT rows; the model predicts D - FIT_MEAN


def load_c5(name="medium"):
    emb, hidden = (16, 256) if name == "medium" else (8, 128)
    sd = torch.load(os.path.join(WDIR, f"C5-{name}-D.pt")); net = DigitNet(emb, hidden); net.load_state_dict({k: v.float() for k, v in sd.items()}); net = net.to(DEV).eval()
    sdr = torch.load(os.path.join(WDIR, f"C5-{name}-R.pt")); netr = DigitNet(emb, hidden); netr.load_state_dict({k: v.float() for k, v in sdr.items()}); netr = netr.to(DEV).eval()
    return net, netr


@torch.no_grad()
def hidden(net, idx, abl=None):
    """Returns (emb_concat, h1, h2, out) for int64 idx (n,14). abl: dict of ablations {"emb_pos": [m...], "h1_units": [...], "h2_units": [...]}"""
    X = torch.as_tensor(idx, device=DEV); outs = [[], [], [], []]
    for i in range(0, len(X), 65536):
        b = X[i:i + 65536]
        e = [net.emb[m](b[:, m]) for m in range(14)]
        if abl and "emb_pos" in abl:
            for m in abl["emb_pos"]: e[m] = torch.zeros_like(e[m])
        h0 = torch.cat(e, dim=1); h1 = torch.relu(net.mlp[0](h0))
        if abl and "h1_units" in abl: h1[:, abl["h1_units"]] = 0
        h2 = torch.relu(net.mlp[2](h1))
        if abl and "h2_units" in abl: h2[:, abl["h2_units"]] = 0
        o = net.mlp[4](h2).squeeze(1)
        for k, v in enumerate((h0, h1, h2, o)): outs[k].append(v.float().cpu().numpy())
    return [np.concatenate(o) for o in outs]


def ridge_probe(Xtr, ytr, Xte, yte, lam=1.0):
    Xtr = np.concatenate([Xtr, np.ones((len(Xtr), 1))], 1); Xte = np.concatenate([Xte, np.ones((len(Xte), 1))], 1)
    W = np.linalg.solve(Xtr.T @ Xtr + lam * np.eye(Xtr.shape[1]), Xtr.T @ ytr); p = Xte @ W
    if yte.ndim == 1:
        return {"R2": float(1 - ((yte - p) ** 2).sum() / max(1e-9, ((yte - yte.mean()) ** 2).sum()))}
    r2 = 1 - ((yte - p) ** 2).sum(0) / np.maximum(1e-9, ((yte - yte.mean(0)) ** 2).sum(0))
    acc = ((p > 0.5) == (yte > 0.5)).mean(0) if set(np.unique(yte)) <= {0, 1} else None
    return {"mean_R2": float(r2.mean()), "min_R2": float(r2.min()), "mean_bit_accuracy": None if acc is None else float(acc.mean())}


def run(n_probe=60000, seed=0):
    U, M, _ = build(); D = U["D"]; F = U["F"]; tg = np.array(U["targets"]); C = U["C"].astype(np.int64); rank = U["rank"].astype(np.int64); kmask = U["kmask"]; succ = M["succ"]
    sr, trole, live, corpus = M["state_role"], M["target_role"], M["live"], M["corpus"]; rng = np.random.default_rng(seed)
    net, netr = load_c5("medium")
    held = live & (sr == 2)[:, None] & (trole == 1)[None, :]; Sx, Jx = np.nonzero(held)
    sel = rng.choice(len(Sx), 2 * n_probe, replace=False); Sx, Jx = Sx[sel], Jx[sel]; Tx = tg[Jx]
    idx = digit_index(F, Sx, Tx); h0, h1, h2, out = hidden(net, idx)
    tr = np.arange(n_probe); te = np.arange(n_probe, 2 * n_probe)
    res = {"model": "C5-medium (frozen)", "probe_rows_train_test": [n_probe, n_probe], "data": "HELD_BOTH (test states x held targets)"}
    # ---- P: targets for probes
    pairs = list(itertools.combinations(range(7), 2))
    kbits = np.stack([(kmask[Sx] >> p) & 1 for p in range(21)], 1).astype(float)
    kbits_t = np.stack([(kmask[Tx] >> p) & 1 for p in range(21)], 1).astype(float)
    bs = -np.sort(-C[Sx], axis=1).astype(float)
    y = D[Sx, Jx].astype(float)
    sd = np.stack([D[succ[Sx, r], Jx] for r in range(3)], 1).astype(float); sd_valid = (sd >= 0).all(1)
    best_action = np.argmin(np.where(sd >= 0, sd, 99), 1)
    onehot = np.eye(3)[best_action]
    quantities = {"rank_f": rank[Sx].astype(float), "count_vector_f": C[Sx].astype(float), "block_sizes_f": bs, "kernel_bits_f": kbits, "kernel_bits_t": kbits_t,
                  "min_collapses_rank_diff": (rank[Sx] - rank[Tx]).astype(float), "exact_D": y, "successor_D_minus_D": (sd - y[:, None]),
                  "shortest_action_onehot": onehot, "kernel_compatible_flag": ((kmask[Sx] & ~kmask[Tx]) == 0).astype(float)}
    probes = {}
    for lname, H in (("L0_embeddings", h0), ("L1_relu", h1), ("L2_relu", h2)):
        probes[lname] = {}
        for q, Y in quantities.items():
            probes[lname][q] = ridge_probe(H[tr], Y[tr], H[te], Y[te])
    # direct baselines: probes from the RAW digits (one-hot) for the same quantities, so "represented" means beyond input
    raw = np.concatenate([np.eye(7)[idx[:, m]] for m in range(7)] + [np.eye(2)[idx[:, 7 + m]] for m in range(7)], 1)
    probes["RAW_digits_onehot"] = {q: ridge_probe(raw[tr], Y[tr], raw[te], Y[te]) for q, Y in quantities.items()}
    res["P_probes"] = probes
    res["P_model_own_R2_on_exact_D"] = float(1 - ((y[te] - (out[te] + FIT_MEAN)) ** 2).sum() / ((y[te] - y[te].mean()) ** 2).sum())
    # ---- A: ablations
    def score(abl):
        _, _, _, o = hidden(net, idx[te], abl); p = o + FIT_MEAN
        r2 = float(1 - ((y[te] - p) ** 2).sum() / ((y[te] - y[te].mean()) ** 2).sum())
        # shortest-action top-1: predict D for the three successors and pick the min
        S3 = succ[Sx[te]]; ok = sd_valid[te]
        idx3 = np.stack([digit_index(F, S3[:, r], Tx[te]) for r in range(3)], 1).reshape(-1, 14)
        _, _, _, o3 = hidden(net, idx3, abl); p3 = o3.reshape(-1, 3)
        top1 = float((np.argmin(p3, 1)[ok] == best_action[te][ok]).mean())
        return {"D_R2": r2, "shortest_action_top1": top1}
    abl = {"none": score(None)}
    for m in range(14):
        abl[f"zero_emb_{'s' if m < 7 else 't'}{m % 7}"] = score({"emb_pos": [m]})
    for g in range(16):
        abl[f"zero_h1_units_{g*16}-{g*16+15}"] = score({"h1_units": list(range(g * 16, g * 16 + 16))})
    for g in range(16):
        abl[f"zero_h2_units_{g*16}-{g*16+15}"] = score({"h2_units": list(range(g * 16, g * 16 + 16))})
    # AC-01R under the same embedding ablations (reachability head)
    corpus_held = corpus[:, None] & (sr == 2)[:, None] & (trole == 1)[None, :]; Sr, Jr = np.nonzero(corpus_held)
    selr = rng.choice(len(Sr), 100000, replace=False); Sr, Jr = Sr[selr], Jr[selr]; idxr = digit_index(F, Sr, tg[Jr]); yr = (D[Sr, Jr] >= 0).astype(float)
    def score_r(a):
        _, _, _, o = hidden(netr, idxr, a); return A._pr_auc(o, yr)
    ablr = {"none": score_r(None)}
    for m in range(14): ablr[f"zero_emb_{'s' if m < 7 else 't'}{m % 7}"] = score_r({"emb_pos": [m]})
    res["A_ablations_D_model"] = abl; res["A_ablations_R_model_prauc"] = ablr
    # ---- S: symmetry under simultaneous value relabelling
    def relabel(states_digits, pi):
        # f -> pi o f o pi^-1 : new_f(i) = pi[f[pi_inv[i]]]
        pinv = np.argsort(pi); return pi[states_digits[:, pinv]]
    sym = {}
    for kind in ("random", "fix01_setwise"):
        diffs = []; rank_changes = []
        for _ in range(20):
            pi = rng.permutation(7)
            if kind == "fix01_setwise":
                pi = np.concatenate([rng.permutation(2), 2 + rng.permutation(5)])
            fs = relabel(idx[te][:, :7], pi); ts = relabel(idx[te][:, 7:], pi)
            # target digits after relabelling may leave the rank-2 restricted-growth form; that is fine for the model input (values 0..6) but
            # the target embedding only knows values 0/1 -> restrict to pi that keeps target values in {0,1}: pi fixes {0,1} setwise
            if ts.max() > 1: continue
            _, _, _, o2 = hidden(net, np.concatenate([fs, ts], 1)); diffs.append(np.abs(o2 - out[te]))
        if diffs:
            d = np.concatenate(diffs); sym[kind] = {"n_perms_applicable": len(diffs), "mean_abs_pred_change": float(d.mean()), "p95_abs_pred_change": float(np.percentile(d, 95)), "frac_change_gt_0.5": float((d > 0.5).mean())}
        else:
            sym[kind] = {"n_perms_applicable": 0, "note": "random value permutations move target digits outside {0,1}; the target embedding is undefined there"}
    res["S_symmetry"] = sym
    # ---- R: C5 vs CP r16 residuals on the same held rows
    cp = np.load(os.path.join(WDIR, "C2-CP-r16.npz")); A_ = [cp[f"arr_{m}"].astype(np.float64) for m in range(14)]; cpmean = float(cp["mean"])
    G = np.ones((len(te), A_[0].shape[1]))
    for m in range(14): G *= A_[m][idx[te][:, m]]
    p_cp = G.sum(1) + cpmean; p_c5 = out[te] + FIT_MEAN
    e_cp = np.abs(np.round(p_cp) - y[te]); e_c5 = np.abs(np.round(p_c5) - y[te])
    both_ok = (e_cp == 0) & (e_c5 == 0); cp_only = (e_cp == 0) & (e_c5 > 0); c5_only = (e_cp > 0) & (e_c5 == 0); neither = (e_cp > 0) & (e_c5 > 0)
    def charac(mask):
        if not mask.any(): return {"n": 0}
        return {"n": int(mask.sum()), "mean_D": float(y[te][mask].mean()), "mean_rank_f": float(rank[Sx[te]][mask].mean()), "mean_rank_diff": float((rank[Sx[te]] - rank[Tx[te]])[mask].mean()),
                "mean_cp_abs_err": float(e_cp[mask].mean()), "mean_c5_abs_err": float(e_c5[mask].mean())}
    res["R_c5_vs_cp"] = {"both_exact": charac(both_ok), "cp_only_exact": charac(cp_only), "c5_only_exact": charac(c5_only), "neither_exact": charac(neither),
                         "corr_of_errors": float(np.corrcoef(e_cp, e_c5)[0, 1]), "cp_R2": float(1 - ((y[te] - p_cp) ** 2).sum() / ((y[te] - y[te].mean()) ** 2).sum()),
                         "c5_R2_on_cp_residual": float(1 - ((y[te] - p_cp - (p_c5 - p_cp)) ** 2).sum() / max(1e-9, ((y[te] - p_cp) ** 2).sum()))}
    od = os.path.join(HERE, "results", "ac01d", "interpret"); os.makedirs(od, exist_ok=True)
    with open(os.path.join(od, "C5_dissection.json"), "w") as f: json.dump(res, f, indent=1)
    return res


if __name__ == "__main__":
    r = run()
    print(json.dumps({"model_R2": r["P_model_own_R2_on_exact_D"], "probes": {L: {q: (v.get("R2") or v.get("mean_R2"), v.get("mean_bit_accuracy")) for q, v in P.items()} for L, P in r["P_probes"].items()},
                      "ablations_top": sorted(((k, round(v["D_R2"], 3), round(v["shortest_action_top1"], 3)) for k, v in r["A_ablations_D_model"].items()), key=lambda x: x[1])[:12],
                      "ablations_R": sorted(((k, round(v, 4)) for k, v in r["A_ablations_R_model_prauc"].items()), key=lambda x: x[1])[:8],
                      "symmetry": r["S_symmetry"], "c5_vs_cp": r["R_c5_vs_cp"]}, indent=1, default=str))
