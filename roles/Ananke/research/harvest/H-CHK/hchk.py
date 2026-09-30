"""H-CHK common code: loaders for the reused worker modules (imported by file path, never edited),
the C1 count-threshold plant, W-V/W-P summaries without file writes, C3 twin episodes and z CIs,
and the frozen readings (PLAN_ADDENDUM X1-X4).

All engine work: device="cpu" explicitly; the caller sets CUDA_VISIBLE_DEVICES=-1 and 1 thread.
"""
from __future__ import annotations

import dataclasses
import importlib.util
import json
import os
import pathlib
import sys

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[4]
WK = REPO / "roles/Ananke/research/workers"
OUT = HERE / "out"
DEV = "cpu"
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import numpy as np  # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


_MODS = {}


def mod(key):
    """Reused worker modules under distinct names (W-P and W-V both have ana.py)."""
    if key in _MODS:
        return _MODS[key]
    paths = {"wp_tt": WK / "W-P/tt.py", "wp_ana": WK / "W-P/ana.py", "wp_pj": WK / "W-P/plants_joint.py",
             "wv_wv": WK / "W-V/wv.py", "wv_ana": WK / "W-V/ana.py", "wv_plants": WK / "W-V/plants_wv.py",
             "wn_pr": WK / "W-N/plants_rel.py", "wn_sr": WK / "W-N/swap_rel.py"}
    if key == "wv_plants":
        sys.path.insert(0, str(WK / "W-V"))
    _MODS[key] = _load(key, paths[key])
    return _MODS[key]


def threads1():
    import torch
    torch.set_num_threads(1)


# ------------------------------------------------------------------ C1 plant (PLAN_ADDENDUM X2)
def champ():
    wv = mod("wv_wv")
    ph, env, g, meta = wv.load("4781b0a1")
    threads1()
    return ph, env, g


def c1_physics(ph_champ):
    php = mod("wv_plants").physics(ph_champ)
    return dataclasses.replace(php, dest_mode="sample", loss=ph_champ.loss, lat_jitter=ph_champ.lat_jitter)


def c2_physics(ph_champ):
    php = mod("wv_plants").physics(ph_champ)
    return dataclasses.replace(php, dest_mode="sample", loss=ph_champ.loss)


def theta_of(j: int) -> int:
    return 256 * j - 128


def c1_genome(ph, j: int):
    from prometheus.ananke import plants
    lines = [
        ("CONST", "T0", 0, 7, 1),            # 128
        ("GT", "T1", "SENSE", "T0", 0),      # 256 iff + cue
        ("SUB", "T2", "ZERO", "T0", 0),      # -128
        ("GT", "T2", "T2", "SENSE", 0),      # 256 iff - cue
        ("ADD", "T3", "T1", "T2", 0),        # 256 iff cue
        ("SUB", "T2", "T1", "S1", 0),
        ("MULQ", "T2", "T2", "T3", 0),
        ("ADD", "S1", "S1", "T2", 0),        # S1 := rectified cue (256 / 0) on cue ticks, held otherwise
        ("MOV", "EMIT", "S1", 0, 0),         # a + latched sensor re-emits every wake
        ("MOV", "PAY1", "S1", 0, 0),
        ("CONST", "T0", 0, 7, 2 * j - 1),    # theta = (2j-1)*128 = 256j - 128
        ("SUB", "S0", "IN0_1", "T0", 0),     # readout: sum of payload-1 arrivals in last wake window - theta
    ]
    return plants.assemble(ph, lines)[None]


# ------------------------------------------------------------------ W-V summary (no writes)
def wv_summary(raw, trials=None):
    ana = mod("wv_ana")
    Pd = int(raw["Pd"])
    trials = trials or [int(k) for k in raw["trials"]]
    out = {"strata": {}}
    for oi, o in enumerate(np.asarray(raw["offsets"]).tolist()):
        for lab, trs in (("pooled", trials), ("q0", [k for k in trials if (k * Pd + o) % 2 == 0]),
                         ("q1", [k for k in trials if (k * Pd + o) % 2 == 1])):
            t = ana.stratum(raw, oi, trs)
            cl = ana.classify(t)
            t["class"] = [cl[0], list(cl[1])]
            t["o"], t["lab"], t["trials"] = o, lab, trs
            out["strata"][f"o{o}{lab}"] = t
    return out


def wv_line(t):
    if t["n"] < 20:
        return f"o{t['o']:<2} {t['lab']:6} n {t['n']:4d} UNDEFINED"
    ef = lambda k: f"{t[k]['e']:.2f}[{t[k]['lo']:.2f},{t[k]['hi']:.2f}]"
    pv = t["piv"]
    return (f"o{t['o']:<2} {t['lab']:6} n {t['n']:4d} {t['class'][0]}{t['class'][1] or ''} | ALL5 {ef('ALL5')} "
            f"FLA {ef('FLA')} | " + " ".join(f"s{j} {ef(f's{j}')}" for j in range(5))
            + " | c " + " ".join(f"{t[f'c{j}']['e']:.2f}" for j in range(5))
            + f" | D_piv {pv['D']:.2f}[{pv['lo']:.2f},{pv['hi']:.2f}]")


def informative(out, offsets=None, labs=("q0", "q1")):
    return {k: t for k, t in out["strata"].items()
            if t["lab"] in labs and (offsets is None or t["o"] in offsets)
            and t["class"][0] not in ("UNDEFINED", "NOT-INFORMATIVE")}


# ------------------------------------------------------------------ W-P summary (no writes)
def wp_tables(res, ys, half, n, trials, offsets):
    """res[k][o] = s0 [K, M]; ys[k] = y[:, k]. -> {o: list of (a, yA, yB)} in trial order."""
    ana = mod("wp_ana")
    return {o: [(ana.full_a(res[k][o], half, n), ys[k][0::2], ys[k][1::2]) for k in trials] for o in offsets}


def wp_summary(tabs, names, site_mask, trials, Pd, P, n_boot=2000):
    ana = mod("wp_ana")
    out = {}
    for o, tb in tabs.items():
        recs = ana.analyse(tb, names, site_mask)
        s = {"pooled": ana.summarize(recs, names, P=P, n_boot=n_boot)}
        for par in (0, 1):
            rp = [r for r in recs if (trials[r["trial"]] * Pd + o) % 2 == par]
            s[f"parity{par}"] = ana.summarize(rp, names, P=P, n_boot=n_boot) if rp else {"eligible": 0,
                                                                                          "class": "UNDEFINED",
                                                                                          "base_N": 0}
        out[o] = s
    return out


def wp_line(o, lab, s):
    j2 = s.get("pt", {}).get("joint2")
    ci = (s.get("ci99") or {}).get("joint2")
    cls = {k: round(v, 2) for k, v in s.get("cls", {}).items()}
    f = lambda k: "-" if s.get(k) is None else f"{s[k]:.2f}"
    return (f"o{o:<2} {lab:8} el {s.get('eligible', 0):4d} fS {f('fS')} fC {f('fC')} fN {f('fN')} "
            f"baseN {s.get('base_N', 0):4d} {s.get('class')} {s.get('polarity', '')} "
            f"j2 {'-' if j2 is None else round(j2, 2)}{'' if not ci else tuple(round(x, 2) for x in ci)} "
            f"top2 {s.get('top2')} cls {cls}")


# ------------------------------------------------------------------ frozen readings
def reading_c1(wp, wvout):
    strata = [(o, lab, s) for o, d in wp.items() for lab, s in d.items() if lab.startswith("parity")]
    has_N = any(s.get("base_N", 0) >= 20 for _, _, s in strata)
    j2 = [(o, lab) for o, lab, s in strata if s.get("base_N", 0) >= 20 and str(s.get("class", "")).startswith("JOINT-2")]
    ana = mod("wv_ana")
    v, cls = ana.verdict(wvout, primary=("q0", "q1"))
    inf = informative(wvout)
    D = [t["piv"]["D"] for t in inf.values() if not np.isnan(t["piv"]["D"])]
    medD = float(np.median(D)) if D else float("nan")
    i_ok = bool(j2)
    ii_ok = v == "DISTRIBUTED-NONMAJ" and medD < 0.3
    if v == "MAJORITY" or (D and medD > 0.7) or not has_N:
        r = "DOES NOT REDUCE"
    elif i_ok and ii_ok:
        r = "REDUCES"
    else:
        r = "PARTIAL"
    return {"reading": r, "i_joint2_strata": j2, "has_N": has_N, "wv_verdict": v, "wv_strata": cls,
            "median_D_piv": medD, "D_piv": D, "i": i_ok, "ii": ii_ok}


def reading_c2(wvout, offsets=(2, 4, 6)):
    ana = mod("wv_ana")
    inf = informative(wvout, offsets)
    if not inf:
        return {"reading": "PARTIAL (no informative stratum)", "strata": {}}
    v, _ = ana.verdict(wvout, offsets=list(offsets))
    D = {k: t["piv"]["D"] for k, t in inf.items()}
    if v == "MAJORITY" and all(d > 0.7 for d in D.values()):
        r = "ROBUST"
    elif all(d < 0.3 for d in D.values()):
        r = "WEAKENED-CONFIRMED"
    else:
        r = "PARTIAL"
    return {"reading": r, "verdict": v, "D_piv": D, "classes": {k: t["class"] for k, t in inf.items()}}


def reading_c3(z):
    """z: {(spec, mode): zpoint}. modes 'a' (mirror), 'b' (twin)."""
    integ = ("n1_s0", "n2_s2")
    p1s_both = z[("P1S", "a")] <= -0.95 and z[("P1S", "b")] <= -0.95
    conf = p1s_both and all(z[(s, "a")] <= -0.95 and abs(z[(s, "b")]) <= 0.5 for s in integ)
    similar = all(abs(z[(s, "a")] - z[(s, "b")]) < 0.5 for s in integ)
    if conf:
        return "CONFUSION CONFIRMED"
    if similar:
        return "NOT CONFIRMED"
    return "PARTIAL"


# ------------------------------------------------------------------ C3 twins and z
def twin_episode(ph, env, seeds, k_scored: int, n: int, back_extra: int = 0):
    """Single-cue twins (lens_swap.twin_profile semantics): world 2i+1 = world 2i with ONLY the cue of trial
    k_scored - n - back_extra negated. Only trial k_scored is scored; y_B = -y_A iff back_extra == 0."""
    import torch
    from prometheus.ananke import envs
    from prometheus.ananke.engine import Schedule
    ep = envs.build(ph, env, seeds)
    M = len(seeds)
    Pd = env.period()
    kc = k_scored - n - back_extra
    assert kc >= 0
    sv = ep.schedule.sense_val.clone()
    sidx, ridx = ep.schedule.sense_idx.clone(), ep.schedule.read_idx.clone()
    t0 = kc * Pd
    y = ep.y.copy()
    for b in range(1, M, 2):
        sv[:, b] = sv[:, b - 1]
        sv[t0:t0 + env.cue_len, b] = -sv[t0:t0 + env.cue_len, b - 1]
        sidx[b], ridx[b] = sidx[b - 1], ridx[b - 1]
        y[b] = y[b - 1]
        if back_extra == 0:
            y[b, k_scored] = -y[b - 1, k_scored]
    scored = np.zeros_like(ep.scored)
    scored[:, k_scored] = ep.scored[:, k_scored]
    meta = dict(ep.meta)
    meta["twin"] = {"k_scored": k_scored, "cue": kc}
    return envs.Episode(Schedule(sidx, sv, ridx), ep.ro_tick.copy(), ep.ro_slot.copy(), y, scored, meta)


def z_ci(normal_pt, swap_pt, level=0.99, n_boot=2000, seed=0):
    """W-N pairing (same scored world-trials), z = (s-.5)/(a-.5) over pair means; percentile pair bootstrap
    of the ratio on W-N's resample indices."""
    sr = mod("wn_sr")
    n = np.asarray(normal_pt, float)
    sw = np.asarray(swap_pt, float)
    both = ~np.isnan(n) & ~np.isnan(sw)
    a = sr.pair_means(np.where(both, n, np.nan))
    s = sr.pair_means(np.where(both, sw, np.nan))
    g = ~np.isnan(a) & ~np.isnan(s)
    a, s = a[g], s[g]
    P = len(a)
    idx = sr._boot_idx(P, n_boot, seed)
    am, sm = a[idx].mean(1), s[idx].mean(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        zb = (sm - 0.5) / (am - 0.5)
    q = (1 - level) / 2
    zp = float((s.mean() - 0.5) / (a.mean() - 0.5)) if a.mean() != 0.5 else float("nan")
    zb = zb[np.isfinite(zb)]
    return {"z": zp, "lo": float(np.quantile(zb, q)), "hi": float(np.quantile(zb, 1 - q)), "P": int(P),
            "a": float(a.mean()), "s": float(s.mean()),
            "twins_differ_frac": None}


def dump(obj, name):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(json.dumps(obj, indent=1, default=lambda x: x.tolist() if hasattr(x, "tolist") else str(x)))
