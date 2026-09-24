"""WTP-02 campaign (PREREG_WTP02 + addendum s9).
python -m ensorain.wtp2.campaign2 <validate|A|B|C|D|E|F|fossil|verdict|all>

Wave-B selection (fixed before Wave A): up to 40 anomalies, per detector
D1..D9 up to 5, each new pick must differ from earlier picks of that
detector in (memory substrate, geometry, band); ranked by statistic
within the diversity constraint; then round-robin fill."""
import collections
import copy
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from ensorain.wtp.genome import ghash, recombine
from .genome2 import candidate, normalize, mutate
from .detect2 import DETS, NULL, fires, null_fires, refs_from, status

OUT = "ensorain/runs/wtp02"
TWINS = (None, "shuffled", "frozen", "random")


def W():
    return int(os.environ.get("ENSORAIN_WORKERS", "20"))


def _life(job):
    import warnings
    warnings.filterwarnings("ignore")
    from .world2 import run_life
    try:
        r = run_life(job["g"], job["seed"], **job.get("kw", {}))
    except Exception as ex:
        r = dict(status="CRASH", reason=f"{type(ex).__name__}: {ex}")
    r.pop("_memory", None)
    r.pop("events", None)
    return job.get("tag"), r


def lives(jobs):
    with ProcessPoolExecutor(W()) as ex:
        return list(ex.map(_life, jobs, chunksize=2))


def unit_jobs(g, seed, tag, kw=None):
    out = []
    for tw in TWINS:
        k = dict(kw or {})
        if tw:
            k["twin"] = tw
        out.append(dict(g=g, seed=seed, kw=k, tag=dict(tag, twin=tw or "real")))
    return out


def gather(res, key):
    units = collections.defaultdict(dict)
    for tag, r in res:
        units[tuple(tag[k] for k in key)][tag["twin"]] = r
    return units


def _pf(job):
    import warnings
    warnings.filterwarnings("ignore")
    from .preflight import preflight
    try:
        ok, rec = preflight(job["g"], job["seed"])
    except Exception as ex:
        ok, rec = False, dict(gate="CRASH", reason=f"{type(ex).__name__}: {ex}")
    return ok, rec, job["g"], job["seed"]


def dump(obj, name):
    os.makedirs(OUT, exist_ok=True)
    json.dump(obj, open(f"{OUT}/{name}", "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))


def load(name):
    return json.load(open(f"{OUT}/{name}"))


# ---------------------------------------------------------------- validation V1-V4

def validate():
    from .world2 import run_life
    from .preflight import preflight
    rng = np.random.default_rng(424_242)
    out = {}
    g = None
    for i in range(20000):
        c = candidate(rng, [], [])
        ok, rec = preflight(c, 8_000_000 + i)
        if ok:
            g = c
            break
    out["found_admitted_after"] = i + 1
    # V1 forced collapse -> DEGENERATE, never scored
    gc = copy.deepcopy(g)
    gc["transition"]["catastrophe_rate"] = 1.0
    r = run_life(gc, 5)
    out["V1_collapse_status"] = r["status"]
    out["V1_pass"] = r["status"] == "DEGENERATE"
    # V2 a table memory cannot reach unseen cells
    gt = copy.deepcopy(g)
    gt["memory"]["substrate"] = "table"
    r = run_life(gt, 5)
    out["V2_table_CGu"] = r.get("CGu")
    out["V2_pass"] = r.get("status") != "OK" or not (r.get("CGu") is not None and np.isfinite(r["CGu"]) and r["CGu"] >= 0.05)
    # V3 identical environment under a transplant: the pre-drawn environment is seed-determined
    a = run_life(g, 7, return_memory=True)
    b = run_life(g, 7, transplant=a["_memory"], freeze=True)
    c2 = run_life(g, 7, transplant=a["_memory"], freeze=True)
    out["V3_same_seed_same_battery_graph"] = a["init_digest"] == b["init_digest"]
    out["V3_transplant_deterministic"] = b["event_digest"] == c2["event_digest"]
    out["V3_pass"] = out["V3_same_seed_same_battery_graph"] and out["V3_transplant_deterministic"]
    # V4 the shuffled twin removes planted competence: an ORACLE-predictor memory transplanted into
    # the real world vs the shuffled world (the same frozen predictions scored against permuted values)
    from ensorain.wtp.organism import make_memory

    class Truth:
        kind = "truth"

        def __init__(self, x):
            self.x = x

        def predict(self, cells):
            return self.x[tuple(cells.T)]

        def n_floats(self):
            return 1

        def params(self):
            return []

        def learn(self, *a):
            return 0

        def quantize(self, b):
            pass

        def forget(self, *a):
            pass

        def hazard(self, *a):
            pass

        def eff_rank(self):
            return None
    from .world2 import streams, build
    gf = copy.deepcopy(g)
    gf["transition"].update(drift=0.0, basis_change_period=0, rewire_period=0, catastrophe_rate=0.0)
    S, _ = streams(11)
    x, *_ = build(gf, S)
    real = run_life(gf, 11, transplant=Truth(x), freeze=True, excursions=False)
    shuf = run_life(gf, 11, twin="shuffled", transplant=Truth(x), freeze=True, excursions=False)
    out["V4_truth_CG_real"], out["V4_truth_CG_shuffled"] = real.get("CG"), shuf.get("CG")
    out["V4_pass"] = (real.get("CG") or 0) >= 1.0 and (shuf.get("CG") or 0) < 0.10
    out["ALL_PASS"] = all(out[k] for k in ("V1_pass", "V2_pass", "V3_pass", "V4_pass"))
    dump(out, "validation.json")
    print(json.dumps(out, indent=1, default=str))


# ---------------------------------------------------------------- Wave A

def wave_a(target=1500, max_cand=150_000, batch=4000):
    rng = np.random.default_rng(24_092_401)
    archive, admitted, gates = [], [], collections.Counter()
    n = 0
    while len(admitted) < target and n < max_cand:
        cands = []
        for _ in range(batch):
            g = candidate(rng, archive, [a["g"] for a in admitted])
            cands.append(dict(g=g, seed=1_000_000 + n))
            archive.append(g)
            n += 1
        with ProcessPoolExecutor(W()) as ex:
            res = list(ex.map(_pf, cands, chunksize=8))
        for ok, rec, g, s in res:
            gates[rec["gate"]] += 1
            if ok and len(admitted) < target:
                admitted.append(dict(g=g, seed=s, pre=rec))
        print(f"candidates {n} admitted {len(admitted)} gates {dict(gates)}", flush=True)
        dump(dict(candidates=n, gates=dict(gates), admitted=admitted, partial=True), "waveA_admission.json")
    dump(dict(candidates=n, gates=dict(gates), admitted=admitted), "waveA_admission.json")
    jobs = []
    for i, a in enumerate(admitted):
        jobs += unit_jobs(a["g"], 3_000_000 + i, dict(i=i))
    res = lives(jobs)
    units = gather(res, ("i",))
    rows = []
    for i, a in enumerate(admitted):
        u = units[(i,)]
        rows.append(dict(i=i, genome_hash=ghash(a["g"]), seed=3_000_000 + i, genome=a["g"], pre=a["pre"],
                         unit={k: _slim(v) for k, v in u.items()}))
    dump(rows, "waveA.json")
    print("wave A lives", len(res))


def _slim(r):
    return {k: v for k, v in r.items() if k not in ("stream_seeds",)}


def waveA_units():
    rows = load("waveA.json")
    return rows, [r["unit"] for r in rows]


# ---------------------------------------------------------------- Wave B

def wave_b(k=40, per=5):
    rows, units = waveA_units()
    refs = refs_from(units)
    fl = []
    for r, u in zip(rows, units):
        for d in DETS:
            s, f = fires(d, u, refs)
            if f:
                fl.append((d, s, r))
    chosen, used = [], collections.defaultdict(set)
    for d in DETS:
        cand = sorted([x for x in fl if x[0] == d], key=lambda x: -abs(x[1]) if np.isfinite(x[1]) else 0)
        n = 0
        for _, s, r in cand:
            key = (r["genome"]["memory"]["substrate"], r["genome"]["geometry"]["kind"], r["genome"]["memory"]["band"])
            if key in used[d] or n >= per:
                continue
            used[d].add(key)
            chosen.append((d, r))
            n += 1
    chosen = chosen[:k]
    jobs = []
    for j, (d, r) in enumerate(chosen):
        for s in range(5):
            jobs += unit_jobs(r["genome"], 4_000_000 + j * 10 + s, dict(j=j, s=s))
    res = lives(jobs)
    units_b = gather(res, ("j", "s"))
    out = []
    for j, (d, r) in enumerate(chosen):
        us = [units_b[(j, s)] for s in range(5)]
        st, info = status(d, us, refs)
        out.append(dict(j=j, detector=d, genome_hash=r["genome_hash"], waveA_i=r["i"], status=st, info=info,
                        klass=[r["genome"]["memory"]["substrate"], r["genome"]["geometry"]["kind"],
                               r["genome"]["learning"]["rule"], r["genome"]["memory"]["band"]],
                        genome=r["genome"]))
        print(j, d, st, {k2: info.get(k2) for k2 in ("hits", "null_hits", "median_SD", "median_stat")}, flush=True)
    dump(dict(flag_counts=dict(collections.Counter(x[0] for x in fl)), refs=refs, anomalies=out), "waveB.json")


# ---------------------------------------------------------------- Wave C

INTERVENTIONS = ("band_third", "band_triple", "delay_0", "delay_16", "drift_0", "drift_up", "door_0", "door_03",
                 "rewire_off", "rewire_on", "obs_swap", "policy_random", "rule_none", "marks_off")
SWEEPS = {"band": [0.005, 0.01, 0.02, 0.03, 0.06, 0.1, 0.25], "delay": [0, 1, 2, 4, 8, 16, 32],
          "drift": [0, .05, .1, .2, .3, .5, .8], "door": [0, .05, .1, .2, .3, .45, .6],
          "rewire": [0, 300, 150, 80, 40, 20, 10]}
CAUSAL_TO_SWEEP = {"band_third": "band", "band_triple": "band", "delay_0": "delay", "delay_16": "delay",
                   "drift_0": "drift", "drift_up": "drift", "door_0": "door", "door_03": "door",
                   "rewire_off": "rewire", "rewire_on": "rewire"}


def intervene(g, v):
    g = copy.deepcopy(g)
    kw = {}
    if v == "band_third":
        g["memory"]["band"] = g["memory"]["band"] / 3
    elif v == "band_triple":
        g["memory"]["band"] = min(0.25, g["memory"]["band"] * 3)
    elif v == "delay_0":
        g["credit"]["delay"] = 0
    elif v == "delay_16":
        g["credit"]["delay"] = g["credit"]["delay"] + 16
    elif v == "drift_0":
        g["transition"]["drift"] = 0.0
    elif v == "drift_up":
        g["transition"]["drift"] = min(0.9, g["transition"]["drift"] + 0.3)
    elif v == "door_0":
        g["irreversibility"].update(door_close=0.0, hazard_frac=0.0, oneway=0.0)
    elif v == "door_03":
        g["irreversibility"]["door_close"] = 0.3
    elif v == "rewire_off":
        g["transition"]["rewire_period"] = 0
    elif v == "rewire_on":
        g["transition"].update(rewire_period=40, rewire_frac=0.3)
    elif v == "obs_swap":
        g["observation"]["kind"] = "fiber" if g["observation"]["kind"] == "cell" else "cell"
    elif v == "policy_random":
        g["search"]["policy"] = "random"
    elif v == "rule_none":
        g["learning"]["rule"] = "none"
    elif v == "marks_off":
        kw["no_marks"] = True
    return g, kw


def set_dial(g, dial, val):
    g = copy.deepcopy(g)
    if dial == "band":
        g["memory"]["band"] = val
    elif dial == "delay":
        g["credit"]["delay"] = int(val)
    elif dial == "drift":
        g["transition"]["drift"] = float(val)
        g["transition"]["drift_period"] = g["transition"]["drift_period"] or 100
    elif dial == "door":
        g["irreversibility"]["door_close"] = float(val)
    elif dial == "rewire":
        g["transition"]["rewire_period"] = int(val)
        g["transition"]["rewire_frac"] = g["transition"]["rewire_frac"] or 0.3
    return g


def wave_c(max_spec=6, max_sweeps=2):
    B = load("waveB.json")
    _, unitsA = waveA_units()
    refs = refs_from(unitsA)
    spec = [a for a in B["anomalies"] if a["status"] == "STRUCTURE-DEPENDENT"][:max_spec]
    fam = []
    for sp in spec:
        d, g0 = sp["detector"], sp["genome"]
        jobs = []
        for v in INTERVENTIONS:
            gv, kw = intervene(g0, v)
            for s in range(3):
                jobs += unit_jobs(gv, 5_000_000 + sp["j"] * 1000 + INTERVENTIONS.index(v) * 10 + s, dict(v=v, s=s), kw)
        units = gather(lives(jobs), ("v", "s"))
        res = {}
        for v in INTERVENTIONS:
            fl = [fires(d, units[(v, s)], refs)[1] for s in range(3)]
            res[v] = dict(fires=sum(fl), removed=sum(fl) <= 1)
        causal = [v for v in INTERVENTIONS if res[v]["removed"]]
        noncausal = [v for v in INTERVENTIONS if not res[v]["removed"]]
        sweeps = []
        dials = []
        for v in causal:
            dl = CAUSAL_TO_SWEEP.get(v)
            if dl and dl not in dials:
                dials.append(dl)
        for dl in dials[:max_sweeps]:
            sweeps.append(sweep(sp, d, g0, dl, refs))
        fam.append(dict(j=sp["j"], detector=d, genome_hash=sp["genome_hash"], interventions=res, causal=causal,
                        causal_support=bool(causal and noncausal), sweeps=sweeps, genome=g0))
        print("C", sp["j"], d, "causal", causal, "boundaries", [s["boundaries"] for s in sweeps], flush=True)
    dump(dict(families=fam), "waveC.json")


def sweep(sp, d, g0, dial, refs):
    levels = list(SWEEPS[dial])
    vals = {}

    def run_levels(lv_list, base_seed):
        jobs = []
        for li, lv in enumerate(lv_list):
            for s in range(4):
                jobs += unit_jobs(set_dial(g0, dial, lv), base_seed + li * 10 + s, dict(lv=lv, s=s))
        units = gather(lives(jobs), ("lv", "s"))
        for lv in lv_list:
            st = [fires(d, units[(lv, s)], refs) for s in range(4)]
            vals[lv] = dict(stat=[a for a, _ in st], fire=[f for _, f in st])
    run_levels(levels, 6_000_000 + sp["j"] * 10_000)
    for rnd in range(2):  # refine between the first present/absent adjacent pair
        ks = sorted(vals)
        pres = [sum(vals[k]["fire"]) >= 2 for k in ks]
        mids = [(ks[i] + ks[i + 1]) / 2 for i in range(len(ks) - 1) if pres[i] != pres[i + 1]][:2]
        if not mids:
            break
        if dial in ("delay", "rewire"):
            mids = sorted({int(round(m)) for m in mids} - set(ks))
        if mids:
            run_levels(mids, 6_500_000 + sp["j"] * 10_000 + rnd * 1000)
    ks = sorted(vals)
    M = np.array([[x if np.isfinite(x) else np.nan for x in vals[k]["stat"]] for k in ks], float)
    sd = float(np.sqrt(np.nanmean(np.nanvar(M, axis=1)))) + 1e-9
    bnd = []
    for i in range(len(ks) - 1):
        a, b = M[i], M[i + 1]
        j_all = np.nanmean(b) - np.nanmean(a)
        j1, j2 = np.nanmean(b[:2]) - np.nanmean(a[:2]), np.nanmean(b[2:]) - np.nanmean(a[2:])
        pa, pb = sum(vals[ks[i]]["fire"]) >= 2, sum(vals[ks[i + 1]]["fire"]) >= 2
        if abs(j_all) > 3 * sd and np.sign(j1) == np.sign(j2) and pa != pb:
            bnd.append(dict(between=(ks[i], ks[i + 1]), jump=float(j_all)))
    return dict(dial=dial, levels=ks, values={str(k): vals[k] for k in ks}, pooled_sd=sd, boundaries=bnd)


# ---------------------------------------------------------------- Wave D

def wave_d(max_n=5):
    from .world2 import run_life
    C = load("waveC.json")
    out = []
    for f in [f for f in C["families"] if f["causal_support"]][:max_n]:
        g, s = f["genome"], 7_000_000 + f["j"]
        base = run_life(g, s, return_memory=True)
        if base.get("status") != "OK" or base.get("CGu") is None or not np.isfinite(base["CGu"]):
            out.append(dict(j=f["j"], note="base life not scorable", base_status=base.get("status")))
            continue
        mem = base["_memory"]
        a = {}
        a["transplant_same"] = run_life(g, s, transplant=mem, freeze=True).get("CGu")
        a["reset_memory_frozen"] = run_life(g, s, freeze=True, intervene={"reset_memory": True}).get("CGu")
        a["reset_then_learn"] = run_life(g, s, intervene={"reset_memory": True}).get("CGu")
        a["ablate_half"] = run_life(g, s, transplant=mem, freeze=True, intervene={"ablate_half": True}).get("CGu")
        a["no_marks"] = run_life(g, s, transplant=mem, freeze=True, no_marks=True).get("CGu")
        a["reskin"] = run_life(g, s, transplant=mem, freeze=True, reskin=True).get("CGu")
        for v in ("drift_0", "door_0", "delay_0"):
            gv, kw = intervene(g, v)
            a[v] = run_life(gv, s, **kw).get("CGu")
        b = base["CGu"]
        carrier = (a["transplant_same"] or -9) >= 0.5 * b and (a["reset_memory_frozen"] or 0) <= 0.2 * b
        out.append(dict(j=f["j"], detector=f["detector"], base_CGu=b, autopsy=a, artifact_carrier=bool(carrier),
                        memory_kind=base["final_kind"], n_floats=base["n_floats"], genome=g))
        print("D", f["j"], "base CGu", round(b, 3), {k: (None if v is None else round(v, 3)) for k, v in a.items()},
              "carrier", carrier, flush=True)
    dump(out, "waveD.json")


# ---------------------------------------------------------------- Wave E

def wave_e():
    from .world2 import run_life
    D = load("waveD.json")
    rng = np.random.default_rng(24_092_405)
    out = []
    for d in [d for d in D if d.get("artifact_carrier")]:
        g, s = d["genome"], 7_000_000 + d["j"]
        mem = run_life(g, s, return_memory=True)["_memory"]
        targets = {}
        for name, gg, kw, seed in (
                ("new_seed_1", g, {}, s + 101), ("new_seed_2", g, {}, s + 102), ("reskinned", g, {"reskin": True}, s),
                ("related", normalize(mutate(g, rng, "local"), rng), {}, s + 103),
                ("topology", _geo(g, "erdos"), {}, s + 104), ("basis", g, {"reskin": True}, s + 105)):
            t = run_life(gg, seed, transplant=mem, freeze=True, **kw).get("CGu")
            f = run_life(gg, seed, freeze=True, **kw).get("CGu")
            targets[name] = dict(transplant=t, fresh=f, gain=(t - f) if t is not None and f is not None else None)
        kept = [v["gain"] for v in targets.values() if v["gain"] is not None and v["gain"] >= 0.5 * d["base_CGu"]]
        out.append(dict(j=d["j"], base_CGu=d["base_CGu"], targets=targets, transferred=len(kept) >= 2))
        print("E", d["j"], {k: (None if v["gain"] is None else round(v["gain"], 3)) for k, v in targets.items()}, flush=True)
    dump(out, "waveE.json")


def _geo(g, kind):
    g = copy.deepcopy(g)
    g["geometry"]["kind"] = kind
    return g


# ---------------------------------------------------------------- Wave F

def wave_f(n=100):
    from .preflight import preflight
    C = load("waveC.json")
    surv = [f["genome"] for f in C["families"] if f["causal_support"]]
    if not surv:
        dump(dict(note="no CAUSAL SUPPORT: Wave F not run (PREREG s5)"), "waveF.json")
        print("F skipped")
        return
    rows, unitsA = waveA_units()
    refs = refs_from(unitsA)
    rng = np.random.default_rng(24_092_406)
    elites = [r["genome"] for r in rows]
    cands = [dict(g=normalize(recombine(surv[int(rng.integers(len(surv)))], elites[int(rng.integers(len(elites)))], rng), rng),
                  seed=8_000_000 + i) for i in range(n)]
    with ProcessPoolExecutor(W()) as ex:
        pf = list(ex.map(_pf, cands))
    adm = [(g, s) for ok, rec, g, s in pf if ok]
    jobs = []
    for i, (g, s) in enumerate(adm):
        jobs += unit_jobs(g, 8_500_000 + i, dict(i=i))
    units = gather(lives(jobs), ("i",))
    flagged = [(i, d) for i in range(len(adm)) for d in DETS if fires(d, units[(i,)], refs)[1]][:10]
    reps = []
    for q, (i, d) in enumerate(flagged):
        jb = []
        for s in range(5):
            jb += unit_jobs(adm[i][0], 8_700_000 + q * 10 + s, dict(s=s))
        us = gather(lives(jb), ("s",))
        st, info = status(d, [us[(s,)] for s in range(5)], refs)
        reps.append(dict(i=i, detector=d, status=st, info=info))
    dump(dict(recombinants=n, admitted=len(adm), flagged=len(flagged), replicated=reps,
              recombined_support=any(r["status"] == "STRUCTURE-DEPENDENT" for r in reps)), "waveF.json")
    print("F admitted", len(adm), "flagged", len(flagged), [r["status"] for r in reps])


# ---------------------------------------------------------------- failure-fossil lane (WTP-01 engine)

def fossil():
    from ensorain.wtp.world import run_world
    B1 = json.load(open("ensorain/runs/wtp01/waveB.json"))
    fos = next(b for b in B1 if b["genome_hash"] == "b235013022100e1f")
    g0 = fos["genome"]
    out = []
    for hebb in (1, 0):
        for delay in (1, 0):
            for irr in (1, 0):
                for drift in (1, 0):
                    g = copy.deepcopy(g0)
                    if not hebb:
                        g["learning"]["rule"] = "sgd"
                    if not delay:
                        g["credit"]["delay"] = 0
                    if not irr:
                        g["irreversibility"].update(door_close=0.0, hazard_frac=0.0, oneway=0.0)
                    if not drift:
                        g["transition"].update(drift=0.0, basis_change_period=0, rewire_period=0, catastrophe_rate=0.0)
                    for s in range(3):
                        r = run_world(g, 9_000_000 + s, return_memory=True)
                        if r.get("status") != "OK":
                            out.append(dict(hebb=hebb, delay=delay, irr=irr, drift=drift, seed=s, status=r.get("status")))
                            continue
                        nl = [t["nlmse"] for t in r["trace"]]
                        inc = np.diff(nl)
                        pn = float(np.sqrt(sum(float((np.asarray(a) ** 2).sum()) for a in r["_memory"].params())))
                        out.append(dict(hebb=hebb, delay=delay, irr=irr, drift=drift, seed=s, CG=r["CG"],
                                        max_jump=float(inc.max()) if len(inc) else 0.0,
                                        jump=bool(len(inc) >= 3 and inc.max() > 5 * (np.median(np.abs(inc)) + 1e-9) and inc.max() > 0.3),
                                        ranks=[t["rank"] for t in r["trace"]], param_norm=pn))
    dump(out, "fossil_factorial.json")
    cells = collections.defaultdict(list)
    for o in out:
        if "CG" in o:
            cells[(o["hebb"], o["delay"], o["irr"], o["drift"])].append(o)
    for k in sorted(cells):
        v = cells[k]
        print("fossil hebb,delay,irr,drift", k, "jump", sum(x["jump"] for x in v), "/", len(v),
              "CG", round(float(np.median([x["CG"] for x in v])), 2), "norm", round(float(np.median([x["param_norm"] for x in v])), 1))


# ---------------------------------------------------------------- verdict

def verdict():
    V = load("validation.json")
    adm = load("waveA_admission.json")
    rows, unitsA = waveA_units()
    refs = refs_from(unitsA)
    B = load("waveB.json")
    C = load("waveC.json") if os.path.exists(f"{OUT}/waveC.json") else dict(families=[])
    D = load("waveD.json") if os.path.exists(f"{OUT}/waveD.json") else []
    E = load("waveE.json") if os.path.exists(f"{OUT}/waveE.json") else []
    reals = [u["real"] for u in unitsA]
    ok = [r for r in reals if r.get("status") == "OK"]
    cgu_sd = 0
    for u in unitsA:
        r, sh = u["real"], u.get("shuffled")
        if r.get("status") == "OK" and sh and sh.get("status") == "OK" and r.get("CGu") is not None and sh.get("CGu") is not None:
            if np.isfinite(r["CGu"]) and np.isfinite(sh["CGu"]) and r["CGu"] >= 0.10 and r["CGu"] - sh["CGu"] >= 0.10:
                cgu_sd += 1
    sd_specs = [a for a in B["anomalies"] if a["status"] == "STRUCTURE-DEPENDENT"]
    fam = {f["j"]: f for f in C["families"]}
    dmap = {d["j"]: d for d in D if "j" in d}
    emap = {e["j"]: e for e in E}
    chain = []
    for a in sd_specs:
        f = fam.get(a["j"])
        if not f or not f["causal_support"]:
            continue
        d = dmap.get(a["j"])
        if not d or not d.get("artifact_carrier"):
            continue
        extra = []
        if any(s["boundaries"] for s in f["sweeps"]):
            extra.append("PHASE BOUNDARY")
        if emap.get(a["j"], {}).get("transferred"):
            extra.append("TRANSFERRED")
        if a["detector"] in ("D7", "D8", "D9"):
            extra.append({"D7": "reorganization", "D8": "reachability", "D9": "amortization"}[a["detector"]])
        if extra:
            chain.append(dict(j=a["j"], detector=a["detector"], extra=extra))
    if chain:
        v = "FOUND CANDIDATE INTELLIGENCE PHYSICS -- EXPAND"
    elif V.get("ALL_PASS") and sd_specs:
        v = "FOUNDRY WORKS, SIGNAL STILL SPARSE -- CONTINUE SEARCH"
    else:
        v = "SEARCH SPACE REMAINS DEGENERATE -- PARK/REDESIGN"
    summ = dict(validation=V, candidates=adm["candidates"], gates=adm["gates"], admitted=len(adm["admitted"]),
                life_status=dict(collections.Counter(r.get("status") for r in reals)),
                frac_CGu_and_SD=cgu_sd / max(len(reals), 1), n_CGu_and_SD=cgu_sd,
                flags=B["flag_counts"], anomalies=len(B["anomalies"]),
                statuses=dict(collections.Counter(a["status"] for a in B["anomalies"])),
                structure_dependent=[dict(j=a["j"], detector=a["detector"], klass=a["klass"]) for a in sd_specs],
                causal_support=[f["j"] for f in C["families"] if f["causal_support"]],
                phase_boundaries=[(f["j"], s["dial"], s["boundaries"]) for f in C["families"] for s in f["sweeps"] if s["boundaries"]],
                carriers=[d["j"] for d in D if d.get("artifact_carrier")], transferred=[e["j"] for e in E if e.get("transferred")],
                full_chain=chain, VERDICT=v)
    dump(summ, "summary.json")
    print(json.dumps(summ, indent=1, default=str))


if __name__ == "__main__":
    steps = dict(validate=validate, A=wave_a, B=wave_b, C=wave_c, D=wave_d, E=wave_e, F=wave_f, fossil=fossil, verdict=verdict)
    w = sys.argv[1]
    if w == "all":
        for k in ("validate", "A", "B", "C", "D", "E", "F", "fossil", "verdict"):
            print("=====", k, flush=True)
            steps[k]()
    else:
        steps[w]()
