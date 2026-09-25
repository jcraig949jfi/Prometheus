"""WTP-01 campaign (PREREG_WTP01): Waves A-E and the verdict.
python -m ensorain.wtp.campaign <A|B|C|D|E|verdict|all>

Anomaly selection for Wave B (fixed in code before Wave A runs): up to
40, stratified over detectors A1..A6 in order, up to 7 per detector by
most extreme statistic, no genome twice, then round-robin fill."""
import collections
import copy
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from .genome import random_genome, mutate, recombine, descriptor, ghash, SPECIAL
from .detect import class_refs, population_refs, flags, niche
from .ledger import fingerprint, record, write

OUT = "ensorain/runs/wtp01"
DET = ("A1", "A2", "A3", "A4", "A5", "A6")
COMPETENCE_DETS = ("A1", "A2", "A3", "A5")


def _run(job):
    import warnings
    warnings.filterwarnings("ignore")
    from .world import run_world
    g, seed, kw = job["g"], job["seed"], job.get("kw", {})
    try:
        r = run_world(g, seed, **kw)
    except Exception as ex:
        r = dict(status="CRASH", reason=f"{type(ex).__name__}: {ex}")
    r.pop("_memory", None)
    r.pop("events", None)
    return job.get("tag", {}), g, seed, r


def pool(jobs, workers=None):
    workers = workers or int(os.environ.get("ENSORAIN_WORKERS", "20"))
    with ProcessPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(_run, jobs, chunksize=2))


def load(path):
    return [json.loads(l) for l in open(path)] if os.path.exists(path) else []


# ------------------------------------------------------------------ Wave A

def wave_a(n_gen=6, per_gen=500):
    os.makedirs(OUT, exist_ok=True)
    fp = fingerprint()
    rng = np.random.default_rng(24_091_101)
    archive, elites = [], []
    path = f"{OUT}/waveA.jsonl"
    idx = 0
    for gen in range(n_gen):
        genomes = []
        for i in range(per_gen):
            u = rng.random()
            if gen == 0 or u < 0.30 or not elites:
                g = random_genome(rng)
            elif u < 0.50:
                g = random_genome(rng, bias=str(rng.choice(SPECIAL)))
            elif u < 0.70:
                cands = [random_genome(rng) for _ in range(5)]
                A = np.array([descriptor(a) for a in archive], float)
                sd = A.std(0) + 1e-6
                dist = [np.min(np.abs((A - np.array(descriptor(c), float)) / sd).sum(1)) for c in cands]
                g = cands[int(np.argmax(dist))]
                g["meta"]["strategy"] = "novelty"
            elif u < 0.90:
                g = mutate(elites[int(rng.integers(len(elites)))], rng, "large" if rng.random() < 0.3 else "local")
            else:
                a, b = rng.choice(len(elites), 2)
                g = recombine(elites[a], elites[b], rng)
            genomes.append(g)
        jobs = []
        for g in genomes:
            s = 100_000 + idx
            idx += 1
            jobs.append(dict(g=g, seed=s, tag=dict(ctrl=0)))
            jobs.append(dict(g=g, seed=s, kw=dict(shuffle_latents=True), tag=dict(ctrl=1)))
        res = pool(jobs)
        rows = []
        for k in range(0, len(res), 2):
            (_, g, s, r), (_, _, _, rc) = res[k], res[k + 1]
            rows.append(record(g, s, r, "A", fp=fp, extra=dict(gen=gen, CG_shuf=rc.get("CG") if rc.get("status") == "OK" else None)))
            archive.append(g)
        write(rows, path)
        ok = [r for r in load(path) if r["status"] == "OK"]
        cref, pref = class_refs(ok), population_refs(ok)
        fl = [(r, flags(r, cref, pref)) for r in ok]
        elites = [r["genome"] for r, f in fl if f]
        by = collections.defaultdict(list)
        for r in ok:
            by[r["genome"]["memory"]["substrate"]].append(r)
        for k, v in by.items():
            elites += [r["genome"] for r in sorted(v, key=lambda r: -r["CG"])[:5]]
        print(f"gen {gen}: rows {len(rows)} ok {sum(r['status'] == 'OK' for r in rows)} flagged-so-far {sum(1 for _, f in fl if f)}", flush=True)


# ------------------------------------------------------------------ Wave B

def select_anomalies(ok, cref, pref, k=40, per=7):
    flagged = [(r, flags(r, cref, pref)) for r in ok]
    chosen, seen = [], set()
    for d in DET:
        cand = [(r, next(v for n, v in f if n == d)) for r, f in flagged if any(n == d for n, _ in f)]
        rev = d != "A4"
        cand.sort(key=lambda x: -x[1] if rev else x[1])
        n = 0
        for r, v in cand:
            if r["genome_hash"] in seen or n >= per:
                continue
            chosen.append((r, d))
            seen.add(r["genome_hash"])
            n += 1
    return chosen[:k]


def wave_b():
    from .ledger import replay_check
    A = [r for r in load(f"{OUT}/waveA.jsonl") if r["status"] == "OK"]
    cref, pref = class_refs(A), population_refs(A)
    chosen = select_anomalies(A, cref, pref)
    os.makedirs(f"{OUT}/fossils", exist_ok=True)
    jobs = []
    for i, (r, d) in enumerate(chosen):
        for k in range(5):
            s = 200_000 + i * 10 + k
            jobs.append(dict(g=r["genome"], seed=s, tag=dict(i=i, det=d, ctrl=0)))
            jobs.append(dict(g=r["genome"], seed=s, kw=dict(shuffle_latents=True), tag=dict(i=i, det=d, ctrl=1)))
    res = pool(jobs)
    out = []
    for i, (r, d) in enumerate(chosen):
        ok_replay, rr = replay_check(r["genome"], r["seed"], r)
        json.dump(dict(genome=r["genome"], seed=r["seed"], detector=d, events=rr.get("events", [])[:5000],
                       digests={k: rr.get(k) for k in ("init_digest", "event_digest", "final_digest")}),
                  open(f"{OUT}/fossils/{r['genome_hash']}_{r['seed']}.json", "w"), default=str)
        reps = [x for x in res if x[0].get("i") == i and x[0]["ctrl"] == 0 and x[3].get("status") == "OK"]
        ctrls = [x for x in res if x[0].get("i") == i and x[0]["ctrl"] == 1 and x[3].get("status") == "OK"]
        hits = sum(any(n == d for n, _ in flags(dict(x[3], genome=x[1]), cref, pref)) for x in reps)
        chits = sum(any(n == d for n, _ in flags(dict(x[3], genome=x[1]), cref, pref)) for x in ctrls)
        state = "REPLICATED" if hits >= 3 else ("WEAK SIGNAL" if hits == 2 else "FALSIFIED")
        if state == "REPLICATED" and d in COMPETENCE_DETS and chits >= 3:
            state = "ARTIFACT"
        out.append(dict(genome_hash=r["genome_hash"], seed=r["seed"], detector=d, waveA_flags=flags(r, cref, pref),
                        replay_ok=ok_replay, hits=hits, n_reps=len(reps), ctrl_hits=chits, n_ctrl=len(ctrls), state=state,
                        CG_reps=[x[3]["CG"] for x in reps], CG_ctrl=[x[3]["CG"] for x in ctrls],
                        klass=[r["genome"]["memory"]["substrate"], r["genome"]["geometry"]["kind"], r["genome"]["learning"]["rule"]],
                        genome=r["genome"]))
        print(i, d, state, f"hits {hits}/{len(reps)} ctrl {chits}/{len(ctrls)} replay_ok {ok_replay}", flush=True)
    json.dump(out, open(f"{OUT}/waveB.json", "w"), indent=1, default=str)


# ------------------------------------------------------------------ Wave C

VARIANTS = ("mem_half", "mem_double", "no_delay", "shuffled_topology", "shuffled_latents", "reversible", "noisier",
            "no_marks", "no_rollouts", "frozen_world")


def variant(g, v):
    g = copy.deepcopy(g)
    kw = {}
    if v == "mem_half":
        g["memory"]["cap"] = max(8, g["memory"]["cap"] // 2)
    elif v == "mem_double":
        g["memory"]["cap"] = g["memory"]["cap"] * 2
    elif v == "no_delay":
        g["credit"]["delay"] = 0
    elif v == "shuffled_topology":
        g["geometry"]["kind"] = "erdos"
    elif v == "shuffled_latents":
        kw["shuffle_latents"] = True
    elif v == "reversible":
        g["irreversibility"].update(door_close=0.0, hazard_frac=0.0, oneway=0.0)
    elif v == "noisier":
        g["observation"]["noise_sd"] += 0.3
    elif v == "no_marks":
        kw["no_marks"] = True
    elif v == "no_rollouts":
        kw["no_rollouts"] = True
    elif v == "frozen_world":
        g["transition"].update(drift=0.0, basis_change_period=0, rewire_period=0, catastrophe_rate=0.0)
    return g, kw


def prop_value(r, d):
    return {"A1": r["CG"], "A2": max([0.0] + list(np.diff([t["nlmse"] for t in r["trace"]]))), "A3": r["CG"],
            "A4": r["CG"], "A5": r["reach"], "A6": r["U"]}[d]


def wave_c(max_anom=8, max_sweeps=3):
    A = [r for r in load(f"{OUT}/waveA.jsonl") if r["status"] == "OK"]
    cref, pref = class_refs(A), population_refs(A)
    B = json.load(open(f"{OUT}/waveB.json"))
    rep = [b for b in B if b["state"] == "REPLICATED"]
    rep.sort(key=lambda b: (b["detector"] not in COMPETENCE_DETS, -np.median(b["CG_reps"])))
    rep = rep[:max_anom]
    jobs = []
    for i, b in enumerate(rep):
        for v in VARIANTS:
            gv, kw = variant(b["genome"], v)
            for k in range(3):
                jobs.append(dict(g=gv, seed=300_000 + i * 100 + k, kw=kw, tag=dict(i=i, v=v)))
    res = pool(jobs)
    fam = []
    for i, b in enumerate(rep):
        d = b["detector"]
        vv = {}
        for v in VARIANTS:
            rs = [x for x in res if x[0]["i"] == i and x[0]["v"] == v and x[3].get("status") == "OK"]
            h = sum(any(n == d for n, _ in flags(dict(x[3], genome=x[1]), cref, pref)) for x in rs)
            vv[v] = dict(hits=h, n=len(rs), present=h >= 2, median_prop=float(np.median([prop_value(x[3], d) for x in rs])) if rs else None)
        removes = [v for v in VARIANTS if vv[v]["n"] and not vv[v]["present"]]
        keeps = [v for v in VARIANTS if vv[v]["present"]]
        fam.append(dict(genome_hash=b["genome_hash"], detector=d, variants=vv, removes=removes, keeps=keeps,
                        causal_support=bool(removes and keeps), genome=b["genome"]))
        print(i, d, "removes", removes, "keeps", keeps, flush=True)
    # sweeps
    sweeps = []
    for i, f in enumerate(fam[:max_sweeps]):
        g0, d = f["genome"], f["detector"]
        if "mem_half" in f["removes"] or "mem_double" in f["removes"] or not f["removes"]:
            dial, levels = "cap", [max(8, int(g0["memory"]["cap"] * m)) for m in (1 / 8, 1 / 4, 1 / 2, 1, 2, 4, 8)]
        elif "no_delay" in f["removes"]:
            dial, levels = "delay", [0, 1, 2, 4, 8, 16, 32]
        elif "noisier" in f["removes"]:
            dial, levels = "noise", [0, .05, .1, .2, .3, .5, .8]
        elif "frozen_world" in f["removes"]:
            dial, levels = "drift", [0, .05, .1, .2, .3, .5, .8]
        else:
            dial, levels = "cap", [max(8, int(g0["memory"]["cap"] * m)) for m in (1 / 8, 1 / 4, 1 / 2, 1, 2, 4, 8)]
        jobs = []
        for li, lv in enumerate(levels):
            g = copy.deepcopy(g0)
            if dial == "cap":
                g["memory"]["cap"] = lv
            elif dial == "delay":
                g["credit"]["delay"] = lv
            elif dial == "noise":
                g["observation"]["noise_sd"] = lv
            else:
                g["transition"]["drift"] = lv
            for k in range(4):
                jobs.append(dict(g=g, seed=350_000 + i * 1000 + li * 10 + k, tag=dict(li=li, k=k)))
        res = pool(jobs)
        M = np.full((len(levels), 4), np.nan)
        for tag, g, s, r in res:
            if r.get("status") == "OK":
                M[tag["li"], tag["k"]] = prop_value(r, d)
        sd = float(np.sqrt(np.nanmean(np.nanvar(M, axis=1)))) + 1e-9
        bnd = []
        for li in range(len(levels) - 1):
            j_all = np.nanmean(M[li + 1]) - np.nanmean(M[li])
            j1 = np.nanmean(M[li + 1, :2]) - np.nanmean(M[li, :2])
            j2 = np.nanmean(M[li + 1, 2:]) - np.nanmean(M[li, 2:])
            if abs(j_all) > 3 * sd and np.sign(j1) == np.sign(j2) and abs(j1) > 3 * sd and abs(j2) > 3 * sd:
                bnd.append(dict(between=(levels[li], levels[li + 1]), jump=float(j_all)))
        sweeps.append(dict(genome_hash=f["genome_hash"], detector=d, dial=dial, levels=levels, values=M.tolist(),
                           pooled_sd=sd, boundaries=bnd))
        print("sweep", i, dial, "boundaries", bnd, flush=True)
    json.dump(dict(families=fam, sweeps=sweeps), open(f"{OUT}/waveC.json", "w"), indent=1, default=str)


# ------------------------------------------------------------------ Wave D

def wave_d(max_n=5):
    from .world import run_world
    B = json.load(open(f"{OUT}/waveB.json"))
    rep = [b for b in B if b["state"] == "REPLICATED" and b["detector"] in ("A1", "A2", "A3")]
    rep.sort(key=lambda b: -np.median(b["CG_reps"]))
    out = []
    for i, b in enumerate(rep[:max_n]):
        g, s = b["genome"], 400_000 + i
        base = run_world(g, s, return_memory=True)
        if base.get("status") != "OK":
            continue
        mem = base["_memory"]
        a = {}
        for name, kw in (("reskin", dict(reskin=True)), ("new_seed", dict()), ("same", dict())):
            seed = s + 1 if name == "new_seed" else s
            tr = run_world(g, seed, transplant=mem, freeze=True, **kw)
            fr = run_world(g, seed, freeze=True, **kw)
            a[name] = dict(transplant_nlmse=tr.get("nlmse_birth"), fresh_nlmse=fr.get("nlmse_birth"),
                           gain=(tr.get("nlmse_birth", 0) - fr.get("nlmse_birth", 0)))
        scr = copy.deepcopy(mem)
        scr.hazard("scramble", np.random.default_rng(1))
        sc = run_world(g, s, transplant=scr, freeze=True)
        fr = run_world(g, s, freeze=True)
        a["scramble"] = dict(gain=sc.get("nlmse_birth", 0) - fr.get("nlmse_birth", 0))
        nm = run_world(g, s, no_marks=True)
        a["no_marks_CG"] = nm.get("CG")
        a["transferred"] = bool(a["reskin"]["gain"] >= 0.5 * base["CG"]) if base["CG"] > 0 else False
        out.append(dict(genome_hash=b["genome_hash"], detector=b["detector"], CG=base["CG"], CG_marks=base["CG_marks"],
                        final_kind=base["final_kind"], n_floats=base["n_floats"], autopsy=a, genome=g))
        print(i, b["detector"], "CG", round(base["CG"], 3), {k: (round(v["gain"], 3) if isinstance(v, dict) else v) for k, v in a.items()}, flush=True)
    json.dump(out, open(f"{OUT}/waveD.json", "w"), indent=1, default=str)


# ------------------------------------------------------------------ Wave E

def wave_e(n=200):
    A = [r for r in load(f"{OUT}/waveA.jsonl") if r["status"] == "OK"]
    cref, pref = class_refs(A), population_refs(A)
    B = json.load(open(f"{OUT}/waveB.json"))
    surv = [b["genome"] for b in B if b["state"] == "REPLICATED"]
    if not surv:
        json.dump(dict(note="no survivors"), open(f"{OUT}/waveE.json", "w"))
        return
    rng = np.random.default_rng(24_091_105)
    elite = [r["genome"] for r in sorted(A, key=lambda r: -r["CG"])[:200]]
    jobs = [dict(g=recombine(surv[int(rng.integers(len(surv)))], elite[int(rng.integers(len(elite)))], rng), seed=500_000 + i)
            for i in range(n)]
    res = pool(jobs)
    ok = [(g, r) for _, g, _, r in res if r.get("status") == "OK"]
    fl = collections.Counter(n for g, r in ok for n, _ in flags(dict(r, genome=g), cref, pref))
    json.dump(dict(n=n, ok=len(ok), flag_counts=dict(fl), CG_q=np.quantile([r["CG"] for _, r in ok], [.5, .9, .99]).tolist()),
              open(f"{OUT}/waveE.json", "w"), indent=1)
    print("wave E", len(ok), dict(fl))


# ------------------------------------------------------------------ verdict

def verdict():
    A_all = load(f"{OUT}/waveA.jsonl")
    A = [r for r in A_all if r["status"] == "OK"]
    B = json.load(open(f"{OUT}/waveB.json"))
    C = json.load(open(f"{OUT}/waveC.json")) if os.path.exists(f"{OUT}/waveC.json") else dict(families=[], sweeps=[])
    rep = [b for b in B if b["state"] == "REPLICATED"]
    classes = {tuple(b["klass"]) for b in rep}
    a_ok = len(rep) >= 3 and len(classes) >= 2
    b_ok = any(s["boundaries"] for s in C["sweeps"])
    shuf = np.array([r["CG_shuf"] for r in A if r.get("CG_shuf") is not None])
    thr = float(np.quantile(shuf, .95)) if len(shuf) else 0.0
    comp = [r for r in A if r["CG"] > thr]
    qU = np.quantile([r["U"] for r in A], [.25, .5, .75])
    niches = {niche(r, qU) for r in comp}
    c_ok = len(comp) / max(len(A), 1) >= 0.05 and len(niches) >= 20
    if not rep:
        v = "NO USEFUL SIGNAL -- PARK"
    elif a_ok and b_ok and c_ok:
        v = "FOUND RICH SEARCH PHYSICS -- CONTINUE"
    else:
        v = "SEARCH SPACE MOSTLY DEGENERATE -- REDESIGN"
    summ = dict(
        attempted=len(A_all), valid=len(A), illegal=sum(r["status"] == "ILLEGAL" for r in A_all),
        crashed=sum(r["status"] == "CRASH" for r in A_all), strategies=dict(collections.Counter(r["strategy"].split(":")[0] for r in A_all)),
        control_CG95=thr, competent=len(comp), competent_frac=len(comp) / max(len(A), 1), niches=len(niches),
        anomalies_selected=len(B), states=dict(collections.Counter(b["state"] for b in B)),
        replicated_classes=sorted(map(list, classes)), causal_support=sum(f["causal_support"] for f in C["families"]),
        phase_boundaries=[(s["dial"], s["boundaries"]) for s in C["sweeps"] if s["boundaries"]],
        criteria=dict(a=a_ok, b=b_ok, c=c_ok), VERDICT=v)
    json.dump(summ, open(f"{OUT}/summary.json", "w"), indent=1, default=str)
    print(json.dumps(summ, indent=1, default=str))


if __name__ == "__main__":
    w = sys.argv[1]
    steps = {"A": wave_a, "B": wave_b, "C": wave_c, "D": wave_d, "E": wave_e, "verdict": verdict}
    if w == "all":
        for k in ("A", "B", "C", "D", "E", "verdict"):
            steps[k]()
    else:
        steps[w]()
