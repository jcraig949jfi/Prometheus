"""Family C5: learned compact embedding over raw digits (torch, GPU if available).

Input: the 14 digits (7 state digits in 0..6, 7 target digits in 0..1), each embedded; MLP head.  Two separately
trained models with the same architecture:
  C5-D  regresses D - mean on FIT entries (train states x train targets, pair role fit); VAL RMSE for early stopping.
  C5-R  classifies reachability on AC-01R FIT rows (all corpus pairs of train states x train targets, pair role fit);
        VAL PR-AUC for early stopping; provides reach_score for the AC-01R sensitivity test.
Eligible for all four held sets (digit encoding).  Input policy: raw digits only.  Storage: float16 state_dict, lzma.
Two sizes: small (emb 8, hidden 128) and medium (emb 16, hidden 256, ~125k params, under the 265 KB landmark).
"""
from __future__ import annotations
import io, json, lzma, os, time
import numpy as np
import torch, torch.nn as nn
from ..corpus import build
from ..evaluate import Context, DENOM_LZMA, write_result
from ..families.c2_cp import digit_index
from ...gate2 import analysis2 as A

DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SIZES = [7] * 7 + [2] * 7


class DigitNet(nn.Module):
    def __init__(self, emb, hidden):
        super().__init__()
        self.emb = nn.ModuleList([nn.Embedding(sz, emb) for sz in SIZES])
        self.mlp = nn.Sequential(nn.Linear(14 * emb, hidden), nn.ReLU(), nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, 1))

    def forward(self, idx):
        h = torch.cat([e(idx[:, m]) for m, e in enumerate(self.emb)], dim=1)
        return self.mlp(h).squeeze(1)


def serialized_bytes(model):
    buf = io.BytesIO(); torch.save({k: v.detach().cpu().half() for k, v in model.state_dict().items()}, buf)
    return len(lzma.compress(buf.getvalue(), preset=6))


class LearnedRep:
    def __init__(self, name, dmodel, rmodel, mean, F, nbytes):
        self.name = name; self.dm = dmodel.eval(); self.rm = rmodel.eval() if rmodel is not None else None; self.mean = mean; self.F = F
        self.serialized_bytes = nbytes; self.eligible_sets = ["HELD_PAIRS", "HELD_STATES", "HELD_TARGETS", "HELD_BOTH"]
        self.reach_score = self._reach if rmodel is not None else None

    @torch.no_grad()
    def _fwd(self, model, states, targets):
        idx = torch.as_tensor(digit_index(self.F, np.asarray(states), np.asarray(targets)), device=DEV)
        out = []
        for i in range(0, len(idx), 65536): out.append(model(idx[i:i + 65536]).float().cpu().numpy())
        return np.concatenate(out) if out else np.zeros(0)

    def predict_D(self, states, targets): return self._fwd(self.dm, states, targets) + self.mean
    def _reach(self, states, targets): return self._fwd(self.rm, states, targets)


def train(model, idx, y, idxv, yv, loss_kind, epochs, lr=2e-3, batch=8192, seed=0):
    torch.manual_seed(seed); model = model.to(DEV); opt = torch.optim.Adam(model.parameters(), lr=lr)
    X = torch.as_tensor(idx, device=DEV); Y = torch.as_tensor(y, device=DEV); Xv = torch.as_tensor(idxv, device=DEV); Yv = torch.as_tensor(yv, device=DEV)
    lossf = nn.MSELoss() if loss_kind == "mse" else nn.BCEWithLogitsLoss()
    best = (1e9, None, -1); hist = []
    n = len(X)
    for ep in range(epochs):
        model.train(); perm = torch.randperm(n, device=DEV)
        for i in range(0, n, batch):
            b = perm[i:i + batch]; opt.zero_grad(); loss = lossf(model(X[b]), Y[b]); loss.backward(); opt.step()
        model.eval()
        with torch.no_grad():
            pv = torch.cat([model(Xv[i:i + 65536]) for i in range(0, len(Xv), 65536)])
            if loss_kind == "mse": score = float(torch.sqrt(((pv - Yv) ** 2).mean()))
            else: score = -A._pr_auc(pv.cpu().numpy(), Yv.cpu().numpy())
        hist.append((ep, score))
        if score < best[0]: best = (score, {k: v.clone() for k, v in model.state_dict().items()}, ep)
        elif ep - best[2] >= 3: break
    model.load_state_dict(best[1]); return model, {"best_epoch": best[2], "best_val": best[0], "history": hist}


def run(configs=(("small", 8, 128), ("medium", 16, 256)), epochs=12, per_set=300, max_obs=3_000_000):
    t0 = time.perf_counter(); ctx = Context(per_set=per_set); U, M = ctx.U, ctx.M; D = U["D"]; F = U["F"]; tg = np.array(U["targets"])
    sr, trole, pr, live, corpus = M["state_role"], M["target_role"], M["pair_role"], M["live"], M["corpus"]
    rng = np.random.default_rng(0)
    # AC-01D fit / val rows
    fit = live & (sr == 0)[:, None] & (trole == 0)[None, :] & (pr == 0); S, J = np.nonzero(fit)
    if len(S) > max_obs: sel = rng.choice(len(S), max_obs, replace=False); S, J = S[sel], J[sel]
    mean = float(D[S, J].mean()); idx = digit_index(F, S, tg[J]).astype(np.int64); y = (D[S, J].astype(np.float32) - mean)
    val = live & (sr == 1)[:, None] & (trole == 0)[None, :]; Sv, Jv = np.nonzero(val)
    if len(Sv) > 200000: sel = rng.choice(len(Sv), 200000, replace=False); Sv, Jv = Sv[sel], Jv[sel]
    idxv = digit_index(F, Sv, tg[Jv]).astype(np.int64); yv = D[Sv, Jv].astype(np.float32) - mean
    # AC-01R fit / val rows (all corpus pairs, label = reachable)
    fitR = corpus[:, None] & (sr == 0)[:, None] & (trole == 0)[None, :] & (pr == 0); SR, JR = np.nonzero(fitR)
    if len(SR) > max_obs: sel = rng.choice(len(SR), max_obs, replace=False); SR, JR = SR[sel], JR[sel]
    idxR = digit_index(F, SR, tg[JR]).astype(np.int64); yR = (D[SR, JR] >= 0).astype(np.float32)
    valR = corpus[:, None] & (sr == 1)[:, None] & (trole == 0)[None, :]; SRv, JRv = np.nonzero(valR)
    sel = rng.choice(len(SRv), 200000, replace=False); SRv, JRv = SRv[sel], JRv[sel]
    idxRv = digit_index(F, SRv, tg[JRv]).astype(np.int64); yRv = (D[SRv, JRv] >= 0).astype(np.float32)
    out = {"family": "C5 learned digit embedding (torch)", "device": str(DEV), "configs": {}}
    for name, emb, hidden in configs:
        dm, dinfo = train(DigitNet(emb, hidden), idx, y, idxv, yv, "mse", epochs)
        rm, rinfo = train(DigitNet(emb, hidden), idxR, yR, idxRv, yRv, "bce", epochs)
        nbytes = serialized_bytes(dm); nbytes_r = serialized_bytes(rm)
        rep = LearnedRep(f"C5-{name}", dm, rm, mean, F, nbytes)
        wdir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "results", "ac01d", "families", "weights"); os.makedirs(wdir, exist_ok=True)
        torch.save({k: v.detach().cpu().half() for k, v in dm.state_dict().items()}, os.path.join(wdir, f"C5-{name}-D.pt"))
        torch.save({k: v.detach().cpu().half() for k, v in rm.state_dict().items()}, os.path.join(wdir, f"C5-{name}-R.pt"))
        ev = ctx.evaluate(rep); ev["fit"] = {"emb": emb, "hidden": hidden, "params": sum(p.numel() for p in dm.parameters()), "D_model": dinfo, "R_model": rinfo,
                                            "bytes_D_lzma": nbytes, "bytes_R_lzma": nbytes_r, "observed_D_rows": int(len(S)), "observed_R_rows": int(len(SR))}
        out["configs"][name] = ev
        summary = {k: {kk: (round(vv.get("HC_D_transitions"), 3) if vv.get("HC_D_transitions") is not None else None, vv.get("mean_excess"), vv.get("failures"), vv.get("dominance")) for kk, vv in v.items() if kk in ("GBFS", "DFS")} for k, v in ev["sets"].items()}
        print(json.dumps({"config": name, "params": ev["fit"]["params"], "CR": round(ev["CR"], 1), "val_rmse": round(dinfo["best_val"], 3), "AC01R": ev.get("AC01R"), "sets": summary,
                          "distance": {k: (round(v["distance"]["R2"], 3), round(v["distance"]["exact"], 3), round(v["distance"]["within_1"], 3)) for k, v in ev["sets"].items() if "distance" in v}}), flush=True)
        write_result(out, "C5_learned")
    out["seconds"] = round(time.perf_counter() - t0, 1); print(write_result(out, "C5_learned")); return out


if __name__ == "__main__":
    run()
