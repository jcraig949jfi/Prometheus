"""PKG-F cheap prerequisite probe (ensorain/arc3/packages/PKG_F_CAUSAL_SELECTIVITY.md s9). DEV seeds 9_800_000+.

For F2 (noise), F3 (obsolete episodes), F5 (spurious nuisance) at L2, 4 worlds each:
  S          the frozen SELECTIVE substrate for the stratum at cap cells/4, trained online on the stream
  D_S        the residual channel r_i = y_i - S(c_i) (exact records); (theta_S, D_S) is lossless for H by construction
  g(q)       residual smoother: mean r over the stored records at minimum Hamming distance to q (unlearned kernel)
  S+D/learned  S(q) + a * g(q), with a in {0, .25, .5, 1} chosen on a held-out 20% of the TRAINING records (in-sample
             distribution). a = 0 means "ignore D".
  S+D/forced S(q) + g(q)
  SHAM       the same readouts over the residual channel of an INDEPENDENT stream of the same world (the same size)
Reports AC on:
  (1) exact-hit recall (seen cells; PC-help: restoring must help);
  (2) the headline test (never-seen / fresh / OOD).
Also checks losslessness (max |S(c) + r - y|) and wall. Single process, BELOW_NORMAL."""
import json
import os
import sys
import time

import numpy as np

from ensorain.wtp3.world3 import AC
from ensorain.lm01.families import make_world
from ensorain.lm01.select_arms import HEADLINE_SEL, SELECTIVE_GRID
from ensorain.lm01.arms import Selective

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "results", "pkgf_probe.json")


def _feed(arm, segs):
    for A, y, _ in segs:
        for i in range(0, len(y), 50):
            arm.observe(A[i:i + 50], y[i:i + 50])
    return arm


def g_smooth(SA, Sr, Q):
    out = np.zeros(len(Q))
    for i in range(0, len(Q), 128):
        D = (Q[i:i + 128, None, :] != SA[None]).sum(2)
        W = D == D.min(1, keepdims=True)
        out[i:i + 128] = (W * Sr[None]).sum(1) / W.sum(1)
    return out


def one(family, gen, seed):
    fz = json.load(open(os.path.join(HERE, "..", "lm01", "FROZEN_SELECTION.json")))["choices"]
    lab = fz[f"{family}|L2|{gen}"]["SELECTIVE"]
    kind, recipe = dict(SELECTIVE_GRID)[lab]
    w = make_world(family, "L2", seed, gen=gen)
    T, truth = w["tests"][HEADLINE_SEL[family]]
    A = np.concatenate([s[0] for s in w["train"]])
    y = np.concatenate([s[1] for s in w["train"]])
    sg = np.concatenate([s[2] for s in w["train"]])
    cells = int(np.prod(w["dims"]))
    S = _feed(Selective(kind, w["dims"], cap=max(160, cells // 4), recipe=recipe), w["train"])
    r = y - S.predict(A)
    lossless = float(np.max(np.abs(S.predict(A) + r - y)))
    # sham: residuals from an independent stream of the same world family, generator and level
    w2 = make_world(family, "L2", seed + 50_000, gen=gen)
    S2 = _feed(Selective(kind, w2["dims"], cap=max(160, cells // 4), recipe=recipe), w2["train"])
    A2 = np.concatenate([s[0] for s in w2["train"]])
    r2 = np.concatenate([s[1] for s in w2["train"]]) - S2.predict(A2)
    m = min(len(r), len(r2))
    A2, r2 = A2[:m], r2[:m]
    # choose a on a held-out 20% of training records (in-distribution)
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(y))
    ho, tr = idx[: len(y) // 5], idx[len(y) // 5:]
    base_ho = S.predict(A[ho])
    gho = g_smooth(A[tr], r[tr], A[ho])
    alphas = (0.0, 0.25, 0.5, 1.0)
    a_best = min(alphas, key=lambda a: np.mean((base_ho + a * gho - y[ho]) ** 2))
    gho2 = g_smooth(A2, r2, A[ho])
    a_sham = min(alphas, key=lambda a: np.mean((base_ho + a * gho2 - y[ho]) ** 2))
    res = {}
    seen = np.unique(A, axis=0)[:512]
    x_seen = np.array([sg[(A == c).all(1)].mean() for c in seen])          # the noise-free truth at seen cells
    for name, Q, tt in (("exact_hit", seen, x_seen), ("headline", T, truth)):
        s0 = S.predict(Q)
        gD, gS = g_smooth(A, r, Q), g_smooth(A2, r2, Q)
        res[name] = dict(S=AC(s0, tt, 1.0), SD_learned=AC(s0 + a_best * gD, tt, 1.0), SD_forced=AC(s0 + gD, tt, 1.0),
                         SHAM_learned=AC(s0 + a_sham * gS, tt, 1.0), SHAM_forced=AC(s0 + gS, tt, 1.0))
    return dict(family=family, gen=gen, seed=seed, selective=lab, lossless_maxerr=lossless, a_learned=a_best,
                a_sham=a_sham, AC=res)


def main():
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass
    t0 = time.time()
    rows = []
    for fam, gens in (("F2_latent", ("lowrank", "spectral")), ("F3_switch", ("cp", "tt")), ("F5_nuisance", ("cp", "spectral"))):
        for g in gens:
            for sd in range(9_800_000, 9_800_004):
                rows.append(one(fam, g, sd))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(dict(wall_s=round(time.time() - t0, 1), rows=rows), open(OUT, "w"), indent=1)
    print("wall", round(time.time() - t0, 1))


if __name__ == "__main__":
    sys.exit(main())
