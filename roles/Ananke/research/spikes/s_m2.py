"""S-M2: carrier swaps + descriptive decoders on M2 (plan 8e081dcb1)."""
import dataclasses
import json
import pathlib
import sys
import time

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
from prometheus.ananke import assays, c1b, envs, lens, search  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402

OUT = pathlib.Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)
DEV = "cuda"
SEEDS = assays.world_seeds(0x5E1, 64)
t_start = time.time()


def specimens():
    ph, env, g, row = c1b_run_load("4ab2ba014aac967e")
    out = {"4ab2ba01": (ph, env, g, None)}
    sp = search.SearchSpec(**{k: v for k, v in row["search"].items()
                              if k in {f.name for f in dataclasses.fields(search.SearchSpec)}})
    summ = json.loads((REPO / "roles/Ananke/pte/c1b/C1B_SUMMARY.json").read_text())
    for f in summ["fresh"]:
        if f["replicates"].startswith("4ab2") and f["signal"]:
            k = f["k"]
            sseed = H_int(c1b.SEARCH_NS, 0, 0, k)
            ev = search.evolve(ph, env, sseed, sp, device=DEV)
            same = abs(ev["held"]["acc"] - f["held"]["acc"]) < 1e-12
            out[f"fresh{k}"] = (ph, env, np.asarray(ev["champion"], dtype=np.int64),
                                {"regenerated_held": ev["held"]["acc"], "stored_held": f["held"]["acc"],
                                 "bit_identical_regeneration": same})
    return out


def c1b_run_load(cid):
    from prometheus.ananke import c1b_run
    return c1b_run.load(cid)


def features(w, env, t):
    """Descriptive decoders at the end of tick t (in-flight state)."""
    a = w.read_idx[:, 0]
    bi = np.arange(w.B)
    ms = w.Msum.cpu().numpy()               # [LM,B,N,C,P]
    mc = w.Mcnt.cpu().numpy()               # [LM,B,N,C]
    LM = w.LM
    lag = np.array([((s - (t + 1)) % LM) for s in range(LM)])
    an = a.cpu().numpy()
    f = {"pay0": ms[..., 0].sum((0, 2, 3)), "cnt": mc.sum((0, 2, 3)).astype(float)}
    if ms.shape[-1] > 1:
        f["pay1"] = ms[..., 1].sum((0, 2, 3))
    f["pay0_a"] = ms[..., 0][:, bi, an, :].sum((0, 2))
    if ms.shape[-1] > 1:
        f["pay1_a"] = ms[..., 1][:, bi, an, :].sum((0, 2))
    ca = mc[:, bi, an, :].sum(-1)           # [LM, B]
    f["cnt_a"] = ca.sum(0).astype(float)
    f["lag_a"] = (lag[:, None] * ca).sum(0) / np.maximum(ca.sum(0), 1)
    return f


def decode(feats_by_trial, y):
    """feats: list over trials of {name: [B]}; y [B, trials]. Fit a sign map
    on the first half of the pairs, score on the second half."""
    B, K = y.shape
    half = (B // 2) // 2 * 2
    res = {}
    for name in feats_by_trial[0]:
        X = np.stack([feats_by_trial[k][name] for k in range(K)], 1)      # [B, K]
        thr = np.median(X[:half])
        s = np.sign(X - thr)
        pol = 1 if (s[:half] * y[:half]).mean() >= 0 else -1
        c = np.where(s == 0, 0.5, (pol * s == y).astype(float))[half:]
        pairs = c.mean(1).reshape(-1, 2).mean(-1)
        m, lo, hi = lens.ci(pairs)
        g = np.random.default_rng(0)
        obs = c.mean()
        null = []
        for _ in range(2000):
            perm = g.permutation((B - half) // 2)
            idx = np.stack([2 * perm, 2 * perm + 1], 1).reshape(-1)
            yy = y[half:][idx]
            cc = np.where(s[half:] == 0, 0.5, (pol * s[half:] == yy).astype(float))
            null.append(cc.mean())
        p = (np.sum(np.array(null) >= obs) + 1) / 2001
        res[name] = {"acc": m, "lo99": lo, "hi99": hi, "perm_p": float(p)}
    return res


def spike(name, ph, env, g):
    mid = c1b.ticks(env)["mid"]
    trials = range(env.trials)
    out = {}
    feats = []

    def rec(w, t):
        if t in mid:
            feats.append(features(w, env, t))
        return None
    base = lens.run(ph, g, env, SEEDS, recorders={"f": rec}, device=DEV)
    nrm = lens.trial_acc(base, trials)
    out["normal"] = lens.ci(nrm)
    out["decoders"] = decode(feats, base.ep.y)
    arms = {
        "D1_swap_inflight": lambda w: lens.swap(w, lens.FLIGHT_ARRAYS),
        "D2_swap_sitestate": lambda w: lens.swap(w, lens.SITE_ARRAYS),
        "D3_swap_payload_only": lambda w: lens.swap(w, ["Msum"]),
        "D4_swap_counts_only": lambda w: lens.swap(w, ["Mcnt"]),
        "D5_swap_pay0": lambda w: lens.swap(w, ["Msum"], sub=0),
        "D6_swap_pay1": lambda w: lens.swap(w, ["Msum"], sub=1),
        "D7a_delay_plus1": lambda w: lens.roll_slots(w, 1),
        "D7b_delay_plus2": lambda w: lens.roll_slots(w, 2),
        "D8_recipient_roll": lambda w: lens.roll_recipients(w, 1),
        "D9_swap_w_only": lambda w: lens.swap(w, ["w"]),
    }
    for an, fn in arms.items():
        if an in ("D6_swap_pay1",) and ph.payload_width < 2:
            out[an] = "NOT_APPLICABLE (P=1)"
            continue
        r = lens.run(ph, g, env, SEEDS, hooks={t: fn for t in mid}, device=DEV)
        pr = lens.trial_acc(r, trials)
        out[an] = {"acc": lens.ci(pr), "verdict": lens.swap_verdict(nrm, pr)}
    return out


if __name__ == "__main__":
    res = {}
    for name, (ph, env, g, meta) in specimens().items():
        res[name] = {"meta": meta, **spike(name, ph, env, g)}
        print(name, json.dumps({k: (v["verdict"] if isinstance(v, dict) and "verdict" in v else v)
                                for k, v in res[name].items() if k.startswith("D")}), flush=True)
    res["_wall_s"] = time.time() - t_start
    (OUT / "s_m2.json").write_text(json.dumps(res, indent=1, default=float))
    print("wall", res["_wall_s"])
