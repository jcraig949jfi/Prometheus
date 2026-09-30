"""BEHAVIOURAL FINGERPRINT: a standardised perturbation battery.

B(M) = [d_1..d_12 baseline descriptors, r_1..r_22 intervention responses]

Descriptors are computed mechanically from the trace after a burn-in (the
first quarter is discarded). Each intervention reruns the genome with one
thing changed; its response r_i = mean_j tanh(|d_ij - d_0j| / s_j), a number
in [0, 1), where s_j is a per-descriptor scale FROZEN from the G0 population
before any arm is evaluated (calibrate_scales). Nothing is interpreted.

VIABILITY (charter "IMPORTANT FAILURE MODE"), all mechanical, all recorded:
  deterministic   same (genome, seed) run twice -> bitwise identical trace
  stable          no blow-up (non-finite or |x| > 1e6) in the baseline run
  nontrivial      final half is not uniform-and-static (temporal OR spatial
                  variation above 1e-6)
  lifetime        activity (step-to-step change) persists past T/4, OR a
                  non-uniform spatial pattern persists (a structured fixed
                  state is allowed; a dead one is not)
  transforms      the dynamics move the state away from the initial
                  condition: max |x_T - x_0| > 1e-3 (a program that leaves
                  its IC untouched is execution-neutral, not a structure)
  responsive      intervention responses neither all < 0.02 (inert) nor
                  more than 90% of them > 0.9 (saturated: everything changes
                  everything -- the "weird-because-broken" signature)
  replicable      fingerprint distance between IC seeds 0 and 1 below
                  TAU_REP (frozen from the G0 population's replicate
                  distances before any arm runs)
"""

from __future__ import annotations

import copy

import numpy as np

from . import substrate as sb

T = sb.T_DEFAULT
N = sb.N_DEFAULT
BURN = T // 4
N_DESC = 12

DESC_NAMES = ["log_level", "log_temporal_std", "log_spatial_std", "ac1_mean", "spectral_entropy",
              "dominant_period", "frac_active_cells", "frac_moving_steps", "spatial_ac1",
              "cross_channel_corr", "memory_of_ic", "value_entropy"]

INTERVENTIONS = [
    "ic_perturb", "ic_seed", "remove_rule", "duplicate_rule", "reverse_relation",
    "randomize_param", "scale_up", "scale_down", "transplant", "delay_info",
    "remove_memory", "bc_change", "add_noise", "substrate_quantize", "invert_order",
    "freeze_component", "mutate_rule", "synchronous_update", "long_horizon",
    "channel_rotate", "topology_rewire", "ic_sign_flip",
]
N_INT = len(INTERVENTIONS)
FP_DIM = N_DESC + N_INT


def _safe_corr(a, b):
    sa, sb_ = a.std(), b.std()
    if sa < 1e-12 or sb_ < 1e-12:
        return 0.0
    return float(np.clip(np.corrcoef(a, b)[0, 1], -1, 1))


def descriptors(trace):
    tr = trace[BURN:]
    Tn, C, Nn = tr.shape
    S = tr.mean(2)  # [T, C] spatial means
    level = np.log1p(np.abs(tr).mean())
    tstd = np.log1p(S.std(0).mean())
    sstd = np.log1p(tr.std(2).mean())
    ac = np.mean([_safe_corr(S[1:, c], S[:-1, c]) for c in range(C)])
    x = S[:, 0] - S[:, 0].mean()
    ps = np.abs(np.fft.rfft(x)) ** 2
    ps = ps[1:]
    if ps.sum() > 1e-18:
        p = ps / ps.sum()
        sent = float(-(p * np.log(p + 1e-18)).sum() / np.log(len(p)))
        dom = float((np.argmax(ps) + 1) / len(x))
    else:
        sent, dom = 0.0, 0.0
    act = float((tr.std(0) > 1e-3).mean())
    steps = np.abs(np.diff(trace, axis=0)).reshape(trace.shape[0] - 1, -1).max(1)
    scale = 1e-4 * (1.0 + np.abs(trace).max())
    moving = float((steps[BURN:] > scale).mean())
    fin = tr[-1]
    sac = np.mean([_safe_corr(fin[c, 1:], fin[c, :-1]) for c in range(C)])
    xc = _safe_corr(S[:, 0], S[:, 1]) if C > 1 else 0.0
    mem = _safe_corr(trace[0, 0], trace[-1, 0])
    v = fin.ravel()
    if v.max() - v.min() > 1e-9:
        h, _ = np.histogram(v, bins=16)
        q = h / h.sum()
        vent = float(-(q[q > 0] * np.log(q[q > 0])).sum() / np.log(16))
    else:
        vent = 0.0
    d = np.array([level, tstd, sstd, ac, sent, dom, act, moving, sac, xc, mem, vent], dtype=float)
    return np.nan_to_num(d)


TRANSPLANT_RULE = {"op": "diffuse", "src": [0], "dst": 0, "p": [0.1], "prov": "battery:transplant"}


def intervene(g, name, rng):
    """Return (genome', run kwargs) for one intervention. Deterministic given rng."""
    g2 = copy.deepcopy(g)
    kw = {"seed": 0, "T": T, "N": N, "opts": {}}
    rules = g2["rules"]
    mid = len(rules) // 2
    if name == "ic_perturb":
        kw["opts"]["ic_eps"] = 1e-3
    elif name == "ic_seed":
        kw["seed"] = 7
    elif name == "remove_rule":
        if len(rules) > 1:
            rules.pop(mid)
        else:
            rules[0] = dict(rules[0], op="decay", src=[], p=[0.0])
    elif name == "duplicate_rule":
        if len(rules) < sb.MAXRULES + 4:
            rules.insert(mid, copy.deepcopy(rules[mid]))
    elif name == "reverse_relation":
        for r in rules:
            if r["src"] and r["op"] not in ("remember", "lensmap") and r["src"][0] != r["dst"]:
                r["src"][0], r["dst"] = r["dst"], r["src"][0]
                break
        else:
            kw["opts"]["chan_rot"] = True
            g2["rules"] = rules[::-1]
    elif name == "randomize_param":
        r = rules[mid]
        r["p"] = sb.rand_params(r["op"], rng, len(r["src"])) if r["op"] != "lensmap" else [float(rng.uniform(-1, 1))]
    elif name == "scale_up":
        kw["N"] = 2 * N
    elif name == "scale_down":
        kw["N"] = N // 2
    elif name == "transplant":
        rules[mid] = copy.deepcopy(TRANSPLANT_RULE)
    elif name == "delay_info":
        kw["opts"]["lag"] = 2
    elif name == "remove_memory":
        kw["opts"]["no_memory"] = True
    elif name == "bc_change":
        kw["opts"]["bc"] = "fixed0" if g["bc"] == "periodic" else "periodic"
        kw["opts"]["topo"] = {"kind": "line" if g["topo"]["kind"] != "line" else "ring", "seed": 0}
    elif name == "add_noise":
        kw["opts"]["noise"] = 1e-2
    elif name == "substrate_quantize":
        kw["opts"]["quant"] = 1e-2
    elif name == "invert_order":
        g2["rules"] = rules[::-1]
    elif name == "freeze_component":
        kw["opts"]["freeze"] = N // 4
    elif name == "mutate_rule":
        r = rules[mid]
        same = [o for o in sb.BASIC_OPS if sb.OPS[o][0] == sb.OPS.get(r["op"], (None,))[0] and o != r["op"] and o != "react"]
        if same and r["op"] not in ("react", "lensmap"):
            r["op"] = same[int(rng.integers(len(same)))]
            r["p"] = sb.rand_params(r["op"], rng, len(r["src"]))
        else:
            r["p"] = [-v if isinstance(v, float) else v for v in r["p"]]
    elif name == "synchronous_update":
        kw["opts"]["sync"] = True
    elif name == "long_horizon":
        kw["T"] = 2 * T
    elif name == "channel_rotate":
        if g["C"] > 1:
            kw["opts"]["chan_rot"] = True
        else:
            kw["opts"]["ic_flip"] = True
            kw["seed"] = 3
    elif name == "topology_rewire":
        kw["opts"]["topo"] = {"kind": "rrg" if g["topo"]["kind"] != "rrg" else "ring", "seed": 99}
    elif name == "ic_sign_flip":
        kw["opts"]["ic_flip"] = True
    else:  # pragma: no cover
        raise ValueError(name)
    return g2, kw


def _run_desc(g, **kw):
    T_ = kw.get("T", T)
    tr, info = sb.run(g, seed=kw.get("seed", 0), T=T_, N=kw.get("N", N), opts=kw.get("opts"))
    if T_ != T:  # long horizon: describe the last T steps so descriptors are comparable
        tr = tr[-T:]
    return descriptors(tr), info, tr


def fingerprint(g, scales, seed=0, want_trace=False):
    """Full battery at IC seed `seed`. Returns dict."""
    base_tr, info = sb.run(g, seed=seed)
    d0 = descriptors(base_tr)
    rng = np.random.default_rng(12345)
    resp = np.zeros(N_INT)
    for i, name in enumerate(INTERVENTIONS):
        g2, kw = intervene(g, name, rng)
        if name != "ic_seed":
            kw["seed"] = seed if kw["seed"] == 0 else kw["seed"] + seed
        else:
            kw["seed"] = 7 + seed
        errs = sb.validate(g2) if len(g2["rules"]) <= sb.MAXRULES else []
        if errs:
            resp[i] = 1.0
            continue
        di, info_i, _ = _run_desc(g2, **kw)
        if info_i["blowup"]:
            resp[i] = 1.0
            continue
        resp[i] = float(np.mean(np.tanh(np.abs(di - d0) / scales)))
    out = {"desc": d0, "resp": resp, "fp": np.concatenate([d0, resp]), "blowup": info["blowup"]}
    if want_trace:
        out["trace"] = base_tr
    return out


def evaluate(g, scales, tau_rep, fp_scale=None):
    """Fingerprint + viability. Returns a JSON-able dict (fp as list)."""
    tr_a, info_a = sb.run(g, seed=0)
    tr_b, _ = sb.run(g, seed=0)
    deterministic = bool(np.array_equal(tr_a, tr_b))
    f0 = fingerprint(g, scales, seed=0)
    f1 = fingerprint(g, scales, seed=1)
    fin = tr_a[T // 2:]
    temporal = float(fin.std(0).max())
    spatial = float(fin[-1].std(1).max())
    nontrivial = (temporal > 1e-6) or (spatial > 1e-6)
    steps = np.abs(np.diff(tr_a, axis=0)).reshape(T - 1, -1).max(1)
    active_late = bool((steps[T // 4:] > 1e-6).any())
    lifetime = active_late or spatial > 1e-3
    transforms = bool(np.abs(tr_a[-1] - sb._init(g, g["C"], N, 0)).max() > 1e-3)
    r = f0["resp"]
    inert = bool((r < 0.02).all())
    saturated = bool((r > 0.9).mean() > 0.9)
    fs = FP_SCALE_UNIT if fp_scale is None else np.asarray(fp_scale)
    rep_dist = float(np.linalg.norm((f0["fp"] - f1["fp"]) / fs))
    replicable = rep_dist < tau_rep if tau_rep is not None else None
    viability = {
        "deterministic": deterministic,
        "stable": not info_a["blowup"],
        "nontrivial": bool(nontrivial),
        "lifetime": bool(lifetime),
        "transforms": transforms,
        "responsive": (not inert) and (not saturated),
        "inert": inert,
        "saturated": saturated,
        "replicable": replicable,
        "rep_dist": rep_dist,
    }
    viable = all(viability[k] for k in ("deterministic", "stable", "nontrivial", "lifetime", "transforms", "responsive")) and \
        (replicable is not False)
    fp = (f0["fp"] + f1["fp"]) / 2.0
    return {"fp": fp.tolist(), "fp_seed0": f0["fp"].tolist(), "fp_seed1": f1["fp"].tolist(),
            "viability": viability, "viable": bool(viable)}


# unit scale for fingerprint distances: descriptors are O(1), responses in [0,1)
FP_SCALE_UNIT = np.ones(FP_DIM)


def calibrate_scales(genomes):
    """Per-descriptor scales from a calibration population (G0), frozen."""
    D = []
    for g in genomes:
        tr, info = sb.run(g, seed=0)
        if not info["blowup"]:
            D.append(descriptors(tr))
    D = np.array(D)
    s = D.std(0)
    return np.where(s > 1e-3, s, 1e-3) * 0.5
