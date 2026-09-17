"""Controls and audits for the C5 result (run AFTER the family, on the same frozen corpus and harness).

NC-PERM  label permutation: the medium architecture trained on FIT rows whose D values are randomly permuted among
         rows.  It must collapse (VAL RMSE ~ std of D, HC_D <= 0); otherwise the harness or the input leaks.
AUDIT    input audit: every feature the model receives is enumerated (digit_index columns) and checked to be a raw
         digit of the state or target; the held-target and held-state masks are re-derived and asserted disjoint
         from the FIT rows used.
COST     decision-time cost: wall-clock per predict_D call (batch of 3 successors) vs the harness's transition
         expansion, for the saved C5 medium / small models.
"""
from __future__ import annotations
import json, os, time
import numpy as np
import torch
from ..evaluate import Context, write_result
from .c2_cp import digit_index
from .c5_learned import DigitNet, LearnedRep, train, serialized_bytes, DEV


def run(epochs=12, per_set=300, max_obs=3_000_000):
    t0 = time.perf_counter(); ctx = Context(per_set=per_set); U, M = ctx.U, ctx.M; D = U["D"]; F = U["F"]; tg = np.array(U["targets"])
    sr, trole, pr, live = M["state_role"], M["target_role"], M["pair_role"], M["live"]; rng = np.random.default_rng(0)
    fit = live & (sr == 0)[:, None] & (trole == 0)[None, :] & (pr == 0); S, J = np.nonzero(fit)
    if len(S) > max_obs: sel = rng.choice(len(S), max_obs, replace=False); S, J = S[sel], J[sel]
    mean = float(D[S, J].mean()); idx = digit_index(F, S, tg[J]).astype(np.int64); y = D[S, J].astype(np.float32) - mean
    val = live & (sr == 1)[:, None] & (trole == 0)[None, :]; Sv, Jv = np.nonzero(val); sel = rng.choice(len(Sv), 200000, replace=False); Sv, Jv = Sv[sel], Jv[sel]
    idxv = digit_index(F, Sv, tg[Jv]).astype(np.int64); yv = D[Sv, Jv].astype(np.float32) - mean
    out = {}
    # AUDIT
    assert set(trole[J].tolist()) == {0} and set(sr[S].tolist()) == {0} and set(pr[S, J].tolist()) == {0}, "FIT rows touch a held role"
    cols = digit_index(F, S[:1000], tg[J[:1000]])
    assert cols.shape[1] == 14 and (cols[:, :7] == F[S[:1000]]).all() and (cols[:, 7:] == F[tg[J[:1000]]]).all(), "input is not the raw digits"
    out["audit"] = {"fit_rows": int(len(S)), "fit_roles": "train states x train targets x pair-fit only (asserted)", "inputs": "14 raw digits (asserted equal to F[state], F[target])",
                    "held_targets": int((trole == 1).sum()), "prohibited_features_present": False}
    # NC-PERM
    yp = y[rng.permutation(len(y))]
    m, info = train(DigitNet(16, 256), idx, yp, idxv, yv, "mse", epochs)
    rep = LearnedRep("C5-medium-LABEL-PERMUTED", m, None, mean, F, serialized_bytes(m)); rep.eligible_sets = ["HELD_TARGETS", "HELD_BOTH"]
    ev = ctx.evaluate(rep); ev["fit"] = info; ev["std_D"] = float(y.std()); out["NC_PERM"] = ev
    print(json.dumps({"NC_PERM_val_rmse": round(info["best_val"], 3), "std_D": round(float(y.std()), 3),
                      "sets": {k: {kk: (vv.get("HC_D_transitions"), vv.get("failures")) for kk, vv in v.items() if kk in ("GBFS", "DFS")} for k, v in ev["sets"].items()}}), flush=True)
    # COST
    wdir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "results", "ac01d", "families", "weights")
    cost = {}
    for name, emb, hidden in (("small", 8, 128), ("medium", 16, 256)):
        net = DigitNet(emb, hidden); sd = torch.load(os.path.join(wdir, f"C5-{name}-D.pt")); net.load_state_dict({k: v.float() for k, v in sd.items()}); net = net.to(DEV).eval()
        r = LearnedRep(f"C5-{name}", net, None, mean, F, 0)
        states = rng.choice(U["NS"], 3000); targets = tg[rng.integers(0, 63, 3000)]
        t1 = time.perf_counter()
        for i in range(0, 3000, 3): r.predict_D(states[i:i + 3], targets[i:i + 3])
        per_call = (time.perf_counter() - t1) / 1000
        # cpu variant
        net_cpu = DigitNet(emb, hidden); net_cpu.load_state_dict({k: v.float() for k, v in sd.items()}); net_cpu.eval()
        idx3 = torch.as_tensor(digit_index(F, states[:3], targets[:3]))
        t1 = time.perf_counter()
        with torch.no_grad():
            for _ in range(1000): net_cpu(idx3)
        per_call_cpu = (time.perf_counter() - t1) / 1000
        cost[name] = {"seconds_per_decision_gpu_batch3": per_call, "seconds_per_decision_cpu_batch3": per_call_cpu}
    # transition expansion cost in the harness (python)
    fi, fx = ctx.obs.fi, ctx.obs.fx; t1 = time.perf_counter(); n = 0
    for s in rng.choice(U["NS"], 20000).tolist():
        n += len(fx[fi[s]:fi[s + 1]])
    cost["seconds_per_transition_expansion_python"] = (time.perf_counter() - t1) / 20000
    out["cost"] = cost; out["seconds"] = round(time.perf_counter() - t0, 1)
    print(json.dumps(cost, indent=1)); print(write_result(out, "C5_controls")); return out


if __name__ == "__main__":
    run()
