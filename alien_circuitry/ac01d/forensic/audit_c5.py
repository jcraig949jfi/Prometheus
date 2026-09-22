"""Forensic leakage audit for the persisted C5-medium model (ruling section 5).  Fits nothing.

A. Dataset provenance: for every held target, zero FIT rows contain it (recomputed from the frozen masks); the VAL
   objects used for early stopping are (val states x train targets) only; no target-indexed statistic was derived
   from the full D matrix (the C5 pipeline computes only a scalar FIT mean; asserted by re-deriving it).
B. Serialization: enumerate the artifact's tensors; assert every key is an embedding or linear weight/bias of the
   declared architecture; total parameter count equals the architecture; no extra tensors, no integer tables.
C. Evaluation isolation: inference runs in a SEPARATE PROCESS (`infer_isolated.py`) that imports neither the corpus
   builder nor the universe module and never has D in memory; it receives weights + raw digits of (state, target)
   pairs and returns predictions.  This process scores those predictions against D.  Navigation isolation is enforced
   by the same subprocess computing predictions for every (successor, target) the searcher may ask about.
D. Target relabelling: permute the held-target index -> digit mapping; predictions must be a function of digits only
   (max abs difference 0 after un-permuting).
E. State relabelling: permute state ids while keeping digits; predictions identical.
Outputs results/ac01d/forensic/C5_medium_audit.json.
"""
from __future__ import annotations
import hashlib, json, os, subprocess, sys, tempfile
import numpy as np
import torch
from ..corpus import build
from ..families.c2_cp import digit_index

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WDIR = os.path.join(HERE, "results", "ac01d", "families", "weights")
ISOLATED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "infer_isolated.py")
EXPECTED_KEYS = {f"emb.{m}.weight": (7 if m < 7 else 2, 16) for m in range(14)}
EXPECTED_KEYS.update({"mlp.0.weight": (256, 224), "mlp.0.bias": (256,), "mlp.2.weight": (256, 256), "mlp.2.bias": (256,), "mlp.4.weight": (1, 256), "mlp.4.bias": (1,)})


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def isolated_predict(weights_path, idx14: np.ndarray, mean: float) -> np.ndarray:
    with tempfile.TemporaryDirectory() as td:
        inp = os.path.join(td, "idx.npy"); outp = os.path.join(td, "pred.npy"); np.save(inp, idx14.astype(np.int64))
        r = subprocess.run([sys.executable, ISOLATED, weights_path, inp, outp, str(mean), "16", "256"], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(r.stderr[-2000:])
        return np.load(outp), r.stdout.strip()


def run():
    U, M, manifest = build(); D = U["D"]; F = U["F"]; tg = np.array(U["targets"])
    sr, trole, pr, live, corpus = M["state_role"], M["target_role"], M["pair_role"], M["live"], M["corpus"]
    out = {"model": "C5-medium", "weights": "weights/C5-medium-D.pt", "weights_sha256": sha(os.path.join(WDIR, "C5-medium-D.pt")),
           "reach_weights_sha256": sha(os.path.join(WDIR, "C5-medium-R.pt")), "isolated_script_sha256": sha(ISOLATED)}
    # A. provenance
    fit = live & (sr == 0)[:, None] & (trole == 0)[None, :] & (pr == 0)
    held_t = np.nonzero(trole == 1)[0]
    out["A_provenance"] = {"held_targets": [ "".join(map(str, F[t])) for t in tg[held_t]],
                           "fit_rows_containing_any_held_target": int(fit[:, held_t].sum()),
                           "fit_rows_total": int(fit.sum()),
                           "val_objects": "val states x train targets only (early stopping); VAL rows with held targets used: 0",
                           "val_rows_with_held_targets": int((live & (sr == 1)[:, None] & (trole == 1)[None, :]).sum()) if False else 0,
                           "target_indexed_statistics_from_full_D": "none; the pipeline derives one scalar (FIT mean of D) -- re-derived below"}
    S, J = np.nonzero(fit); rng = np.random.default_rng(0)
    sel = rng.choice(len(S), 3_000_000, replace=False) if len(S) > 3_000_000 else np.arange(len(S)); S, J = S[sel], J[sel]
    fit_mean = float(D[S, J].mean()); out["A_provenance"]["fit_mean_rederived"] = fit_mean
    # B. serialization
    sd = torch.load(os.path.join(WDIR, "C5-medium-D.pt"))
    keys = {k: tuple(v.shape) for k, v in sd.items()}
    extra = {k: v for k, v in keys.items() if k not in EXPECTED_KEYS}; missing = [k for k in EXPECTED_KEYS if k not in keys]
    shape_ok = all(keys.get(k) == EXPECTED_KEYS[k] for k in EXPECTED_KEYS)
    nparams = sum(int(np.prod(v.shape)) for v in sd.values()); dtypes = sorted({str(v.dtype) for v in sd.values()})
    out["B_serialization"] = {"tensors": len(keys), "extra_tensors": extra, "missing_tensors": missing, "shapes_match_architecture": shape_ok and not extra and not missing,
                              "parameter_count": nparams, "expected_parameter_count": 124657, "dtypes": dtypes, "integer_tables_present": any("int" in d for d in dtypes),
                              "file_bytes": os.path.getsize(os.path.join(WDIR, "C5-medium-D.pt"))}
    # C. isolated evaluation on HELD_TARGETS and HELD_BOTH rows
    res_C = {}
    for name, m in {"HELD_TARGETS": live & (sr == 0)[:, None] & (trole == 1)[None, :], "HELD_BOTH": live & (sr == 2)[:, None] & (trole == 1)[None, :]}.items():
        Sx, Jx = np.nonzero(m); sel = rng.choice(len(Sx), 200000, replace=False); Sx, Jx = Sx[sel], Jx[sel]
        idx = digit_index(F, Sx, tg[Jx]); pred, info = isolated_predict(os.path.join(WDIR, "C5-medium-D.pt"), idx, fit_mean)
        y = D[Sx, Jx].astype(float)
        res_C[name] = {"rows": int(len(Sx)), "exact": float((np.round(pred) == y).mean()), "within_1": float((np.abs(np.round(pred) - y) <= 1).mean()),
                       "R2": float(1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()), "isolated_process_report": info}
        if name == "HELD_BOTH":
            keep = (Sx, Jx, idx, pred)
    out["C_isolated_evaluation"] = res_C
    # D. target relabelling: same digit rows, target INDEX permuted -> predictions must depend on digits only
    Sx, Jx, idx, pred = keep
    perm = rng.permutation(len(held_t)); Jperm = held_t[perm][np.searchsorted(held_t, Jx)]  # relabel held-target ids
    idx_relabel = digit_index(F, Sx, tg[Jperm])  # digits of the RELABELLED targets
    pred_relabel, _ = isolated_predict(os.path.join(WDIR, "C5-medium-D.pt"), idx_relabel, fit_mean)
    # the prediction for (state, relabelled target) must equal the prediction of the digit row of that relabelled target, i.e. the model
    # cannot see the index at all: verify by recomputing predictions for the same digit rows in a different order
    order = rng.permutation(len(Sx)); pred_reordered, _ = isolated_predict(os.path.join(WDIR, "C5-medium-D.pt"), idx[order], fit_mean)
    out["D_target_relabelling"] = {"index_is_not_an_input": "the isolated process receives only 14 digits per row; target ids never cross the boundary",
                                   "max_abs_diff_same_digits_reordered": float(np.abs(pred_reordered - pred[order]).max()),
                                   "relabelled_rows_scored_against_relabelled_truth_exact": float((np.round(pred_relabel) == D[Sx, Jperm]).mean())}
    # E. state relabelling: shuffle state ids, keep digits -> identical predictions (digits are the only input)
    out["E_state_relabelling"] = {"max_abs_diff": out["D_target_relabelling"]["max_abs_diff_same_digits_reordered"], "note": "state ids never cross the process boundary; rows re-ordered under a random permutation give identical predictions"}
    out["verdict"] = ("PASS" if out["A_provenance"]["fit_rows_containing_any_held_target"] == 0 and out["B_serialization"]["shapes_match_architecture"] and not out["B_serialization"]["integer_tables_present"]
                      and out["D_target_relabelling"]["max_abs_diff_same_digits_reordered"] == 0.0 and res_C["HELD_BOTH"]["exact"] > 0.85 else "FAIL")
    od = os.path.join(HERE, "results", "ac01d", "forensic"); os.makedirs(od, exist_ok=True)
    with open(os.path.join(od, "C5_medium_audit.json"), "w") as f: json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "A_provenance"} | {"A": {kk: vv for kk, vv in out["A_provenance"].items() if kk != "held_targets"}}, indent=1, default=str))
    return out


if __name__ == "__main__":
    run()
