"""Family C2 (tensor), decompositions 2 and 3 of 3: Tensor Train and Tucker over the 14 digit modes, fitted on the
observed FIT entries by gradient descent (torch autograd, Adam), VAL RMSE for early stopping.

TT: cores G_m of shape (r_{m-1}, n_m, r_m) with r_0 = r_14 = 1; entry = product of the selected slices.
Tucker: mode factors U_m (n_m x k) and a dense core of shape k^14 (k = 2 keeps the core at 16,384 entries).
Both eligible for all four held sets (digit encoding); raw digits only; storage = float16 parameters after lzma.
Tensor Train has no privileged status here: it is scored exactly like CP and Tucker.
"""
from __future__ import annotations
import io, json, lzma, os, time
import numpy as np
import torch, torch.nn as nn
from ..evaluate import Context, DENOM_LZMA, write_result
from .c2_cp import digit_index
from .c5_learned import DEV, SIZES, train, serialized_bytes


class TTNet(nn.Module):
    def __init__(self, rank):
        super().__init__()
        ranks = [1] + [rank] * 13 + [1]
        self.cores = nn.ParameterList([nn.Parameter(torch.randn(ranks[m], SIZES[m], ranks[m + 1]) * (1.0 / np.sqrt(max(1, ranks[m])))) for m in range(14)])

    def forward(self, idx):
        v = self.cores[0][:, idx[:, 0], :].permute(1, 0, 2)  # (n, 1, r)
        for m in range(1, 14):
            v = torch.bmm(v, self.cores[m][:, idx[:, m], :].permute(1, 0, 2))
        return v.reshape(len(idx), -1).sum(dim=1)


class TuckerNet(nn.Module):
    def __init__(self, k):
        super().__init__()
        self.U = nn.ParameterList([nn.Parameter(torch.randn(SIZES[m], k) * 0.5) for m in range(14)])
        self.core = nn.Parameter(torch.randn(*([k] * 14)) * 0.05); self.k = k

    def forward(self, idx):
        # contract the core with the selected factor rows one mode at a time
        core = self.core.unsqueeze(0).expand(len(idx), *([self.k] * 14))
        for m in range(14):
            u = self.U[m][idx[:, m]]  # (n, k)
            core = torch.einsum("n...k,nk->n...", core.reshape(len(idx), -1, self.k), u).reshape(len(idx), *([self.k] * (13 - m)))
        return core.reshape(len(idx))


class TorchRep:
    def __init__(self, name, model, mean, F, nbytes):
        self.name = name; self.model = model.eval(); self.mean = mean; self.F = F; self.serialized_bytes = nbytes
        self.eligible_sets = ["HELD_PAIRS", "HELD_STATES", "HELD_TARGETS", "HELD_BOTH"]; self.reach_score = None

    @torch.no_grad()
    def predict_D(self, states, targets):
        idx = torch.as_tensor(digit_index(self.F, np.asarray(states), np.asarray(targets)), device=DEV)
        out = [self.model(idx[i:i + 32768]).float().cpu().numpy() for i in range(0, len(idx), 32768)]
        return (np.concatenate(out) if out else np.zeros(0)) + self.mean


def run(tt_ranks=(4, 8, 16), tucker_k=(2,), epochs=12, per_set=300, max_obs=3_000_000):
    t0 = time.perf_counter(); ctx = Context(per_set=per_set); U, M = ctx.U, ctx.M; D = U["D"]; F = U["F"]; tg = np.array(U["targets"])
    sr, trole, pr, live = M["state_role"], M["target_role"], M["pair_role"], M["live"]; rng = np.random.default_rng(0)
    fit = live & (sr == 0)[:, None] & (trole == 0)[None, :] & (pr == 0); S, J = np.nonzero(fit)
    if len(S) > max_obs: sel = rng.choice(len(S), max_obs, replace=False); S, J = S[sel], J[sel]
    mean = float(D[S, J].mean()); idx = digit_index(F, S, tg[J]).astype(np.int64); y = D[S, J].astype(np.float32) - mean
    val = live & (sr == 1)[:, None] & (trole == 0)[None, :]; Sv, Jv = np.nonzero(val)
    sel = rng.choice(len(Sv), 200000, replace=False); Sv, Jv = Sv[sel], Jv[sel]
    idxv = digit_index(F, Sv, tg[Jv]).astype(np.int64); yv = D[Sv, Jv].astype(np.float32) - mean
    out = {"family": "C2 tensor train / Tucker over digit modes (torch, observed-entry fit)", "device": str(DEV), "models": {}}
    models = [(f"C2-TT-r{r}", TTNet(r)) for r in tt_ranks] + [(f"C2-Tucker-k{k}", TuckerNet(k)) for k in tucker_k]
    for name, model in models:
        m, info = train(model, idx, y, idxv, yv, "mse", epochs, lr=1e-2 if "TT" in name else 5e-3, batch=4096)
        nbytes = serialized_bytes(m); rep = TorchRep(name, m, mean, F, nbytes); ev = ctx.evaluate(rep)
        ev["fit"] = {"params": sum(p.numel() for p in m.parameters()), **info, "bytes_lzma": nbytes, "observed_rows": int(len(S))}
        out["models"][name] = ev
        summary = {k: {kk: (round(vv.get("HC_D_transitions"), 3) if vv.get("HC_D_transitions") is not None else None, vv.get("mean_excess"), vv.get("failures"), vv.get("dominance")) for kk, vv in v.items() if kk in ("GBFS", "DFS")} for k, v in ev["sets"].items()}
        print(json.dumps({"model": name, "params": ev["fit"]["params"], "CR": round(ev["CR"], 1), "val_rmse": round(info["best_val"], 3), "sets": summary,
                          "distance": {k: (round(v["distance"]["R2"], 3), round(v["distance"]["exact"], 3), round(v["distance"]["within_1"], 3)) for k, v in ev["sets"].items() if "distance" in v}}), flush=True)
        write_result(out, "C2_tt_tucker")
    out["seconds"] = round(time.perf_counter() - t0, 1); print(write_result(out, "C2_tt_tucker")); return out


if __name__ == "__main__":
    run()
