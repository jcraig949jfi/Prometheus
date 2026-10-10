"""WTP-05 independent rung certifier (PREREG_WTP05 s6). Never used as fitness.

An organism is certified on HELD-OUT probe seeds, archive OFF. Plasticity runs exactly as in life, for a
normal lifetime; then PROBE blocks (K = 64 each, plasticity frozen at the learned parameters, no exploration
noise) record the working state.
  behavioural pass  final-gate accuracy with Wilson 95% lower bound >= .85 (n >= 256 gates)
  state retention   a latent is RETAINED if some single working-state channel, read at the decision step,
                    agrees in sign with it on >= 90% of probe episodes (either polarity)
  necessity         for R2+ the pass must collapse (accuracy <= .60) when the working state is reset every step
Rungs per family:
  A  R0 cA retained (A-R0/R2 worlds) | R1 cA and cB retained (A-R1/R3) | R2 pass A-R2 | R3 pass A-R3
  B  R0 one factor sign retained     | R1 both factor signs retained   | R2 pass B-R2 | R3 pass B-R3
  N  R0 mode retained (N-R3)         | R1 par0 and par1 retained (N-R3)| R2 pass N-R2 | R3 pass N-R3
  C  (not a ladder world) SWITCH_TRACKED: type-1 accuracy >= .75 (calibrated on the planted solver, .80) in the blocks from switch+3 to the end, and
     the never-switching type-2 law >= .90 over the whole life (unrelated competence preserved)
R4 / R5 need the nested family D (optional, directive s6); they are reported NOT_TESTED unless D is run.
"""
import copy

import numpy as np

from .tape import lifetime, run_block
from .worlds import make

RUNG_NUM = dict(R0=0, R1=1, R2=2, R3=3)


def wilson_lb(k, n, z=1.96):
    if n == 0:
        return 0.0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - r) / d


def _probe(g, world, rng, n_blocks=4, K=64, ws_reset=False):
    acc_k = acc_n = 0
    keep = {}
    for _ in range(n_blocks):
        ep = world.block(K, rng, world.L - 1)
        rec = {}
        acts = run_block(g, ep["obs"], record=rec, ws_reset=ws_reset)
        m = ep["role"] == 1
        acc_k += int((acts[m] == ep["tgt"][m]).sum())
        acc_n += int(m.sum())
        for name, (vals, tdec) in ep["lat"].items():
            zt = rec["z"][np.arange(K), tdec]                          # K x S x W
            keep.setdefault(name, []).append((zt.reshape(K, -1), vals))
    retained = {}
    for name, parts in keep.items():
        Z = np.vstack([p[0] for p in parts])
        v = np.concatenate([p[1] for p in parts])
        pos = (np.sign(Z) == v[:, None]).mean(0)
        neg = (np.sign(Z) == -v[:, None]).mean(0)
        retained[name] = float(np.max(np.maximum(pos, neg))) if Z.shape[1] else 0.0
    return acc_k, acc_n, retained


def certify(g, family, rung, seed, plasticity=True):
    """Certify organism g (trained on family-rung) on held-out seeds. Returns dict with 'rung' (highest
    certified, -1 if none) and the evidence."""
    rng = np.random.default_rng(seed)
    out = dict(family=family, trained_rung=rung)
    if family == "C":
        w = make(f"C-{rung}-desert")
        late, t2 = [], []
        for rep in range(4):
            w.new_life(rng)
            sw = w.sw
            life = lifetime(g, w, rng, plasticity=plasticity, K=64)
            late += [bl["acc"][1] for b, bl in enumerate(life["blocks"]) if b >= sw + 3 and 1 in bl["acc"]]
            t2 += [bl["acc"][5] for bl in life["blocks"] if 5 in bl["acc"]]
        out.update(c_late_type1=float(np.mean(late)), c_type2=float(np.mean(t2)))
        out["switch_tracked"] = bool(out["c_late_type1"] >= 0.75 and out["c_type2"] >= 0.90)
        out["rung"] = -1
        return out
    learned = lifetime(g, make(f"{family}-{rung}-desert"), rng, plasticity=plasticity)["learned"]
    learned = copy.deepcopy(learned)
    learned["eta"] = learned["sigma"] = 0.0
    res = {}
    probe_worlds = {"A": ("R0", "R1", "R2", "R3"), "B": ("R2", "R3"), "N": ("R2", "R3")}[family]
    for r in probe_worlds:
        w = make(f"{family}-{r}-desert")
        k, n, ret = _probe(learned, w, rng)
        res[r] = dict(acc=k / n, lb=wilson_lb(k, n), n=n, retained=ret)
    rung_ok = {}
    if family == "A":
        rung_ok["R0"] = res["R0"]["retained"].get("cA", 0) >= 0.9 or res["R2"]["retained"].get("cA", 0) >= 0.9
        rung_ok["R1"] = min(res["R1"]["retained"].get("cA", 0), res["R1"]["retained"].get("cB", 0)) >= 0.9 or \
            min(res["R3"]["retained"].get("cA", 0), res["R3"]["retained"].get("cB", 0)) >= 0.9
    elif family == "B":
        r2 = res["R2"]["retained"]
        rung_ok["R0"] = max(r2.get("ua", 0), r2.get("vb", 0)) >= 0.9
        rung_ok["R1"] = min(r2.get("ua", 0), r2.get("vb", 0)) >= 0.9
    elif family == "N":
        r3 = res["R3"]["retained"]
        rung_ok["R0"] = r3.get("mode", 0) >= 0.9
        rung_ok["R1"] = min(r3.get("par0", 0), r3.get("par1", 0)) >= 0.9
    for r in ("R2", "R3"):
        if r in res and res[r]["lb"] >= 0.85:
            k, n, _ = _probe(learned, make(f"{family}-{r}-desert"), rng, ws_reset=True)
            res[r]["acc_ws_reset"] = k / n
            rung_ok[r] = k / n <= 0.60
        else:
            rung_ok[r] = False
    out.update(probes=res, rung_ok=rung_ok)
    out["rung"] = max([RUNG_NUM[r] for r, ok in rung_ok.items() if ok], default=-1)
    out["R4"] = out["R5"] = "NOT_TESTED"
    return out
