"""WTP-03 campaign: validation, Waves A-G, verdict (PREREG_WTP03). Rows -> ensorain/runs/wtp03/.

    python -m ensorain.wtp3.campaign3 validate|A|B|C|D|E|F|G|verdict|all
"""
import collections
import copy
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from ensorain.wtp.genome import ghash
from .autopsy import autopsy
from .collider import experience, collide, test_sets, holdout, STRUCT, PANEL, SIMPLE, _addr, train, score, make
from .detect3 import completion, crossovers, superadditive, status_units, TH, MIN_FLOATS
from .genome3 import candidate, normalize, mutate, market
from .preflight3 import preflight
from .world3 import mem_cap, BANDS, AC

OUT = os.path.join(os.path.dirname(__file__), "..", "runs", "wtp03")
os.makedirs(OUT, exist_ok=True)


def W():
    return int(os.environ.get("ENSORAIN_WORKERS", 20))


def dump(obj, name):
    json.dump(obj, open(os.path.join(OUT, name), "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))


def load(name):
    return json.load(open(os.path.join(OUT, name)))


# ------------------------------------------------------------------ strata (s9)

STRATA = (("wild", 0.45), ("clean_channel", 0.25), ("mutant", 0.30))


def clean_channel(g, rng):
    """Learnable-channel stratum: clean sensing + clean credit; every other law stays wild."""
    g["observation"]["chain"] = []
    g["observation"]["noise_sd"] = float(rng.uniform(0, 0.2))
    if g["observation"]["kind"] in ("probe_only", "marginal"):
        g["observation"]["kind"] = str(rng.choice(["cell", "fiber", "masked"]))
    g["credit"].update(delay=0, radius=0, sign_flip=0.0, noise=float(rng.uniform(0, 0.05)))
    g["meta"]["stratum"] = "clean_channel"
    return g


def propose(rng, archive, parents):
    u = rng.random()
    if u < STRATA[0][1] or not parents:
        g = candidate(rng, archive, [])
        g["meta"]["stratum"] = "wild"
        if u >= STRATA[0][1] and rng.random() < STRATA[1][1] / (STRATA[1][1] + STRATA[2][1]):
            g = clean_channel(g, rng)
        return g
    if u < STRATA[0][1] + STRATA[1][1]:
        return clean_channel(candidate(rng, archive, []), rng)
    p = parents[int(rng.integers(len(parents)))]
    g = market(normalize(mutate(p["g"], rng, "local" if rng.random() < 0.7 else "large"), rng), rng)
    g["meta"]["stratum"] = "mutant"
    g["meta"]["root"] = p["root"]
    return g


def _pf(job):
    t0 = time.time()
    try:
        ok, rec = preflight(job["g"], job["seed"])
    except Exception as ex:
        ok, rec = False, dict(gate="CRASH", reason=f"{type(ex).__name__}: {ex}"[:300])
    rec["secs"] = round(time.time() - t0, 2)
    return ok, rec, job["g"], job["seed"]


def near_miss(rec):
    """Learnability margin for rejected-at-economy worlds: learner gain as a fraction of information value."""
    ks = [k for k in (rec.get("kappa_search") or []) if k.get("lrn")]
    best = None
    for k in ks:
        t, o, l = max(k["triv"]), min(k["orc"]), min(k["lrn"])
        if o - t > 0:
            v = (l - t) / (o - t)
            best = v if best is None else max(best, v)
    return best


def wave_a(target=1000, max_cand=200_000, batch=2000, hours=10.0, lineage_cap=None):
    lineage_cap = lineage_cap or max(1, int(0.015 * target))
    rng = np.random.default_rng(24_092_501)
    admitted, gates, archive, near = [], collections.Counter(), [], []
    per_root = collections.Counter()
    n, t0, seed0 = 0, time.time(), 5_000_000
    while len(admitted) < target and n < max_cand and time.time() - t0 < hours * 3600:
        # parents: admitted worlds under the lineage cap, plus the best near-misses (declared s9)
        parents = [dict(g=a["g"], root=a["root"]) for a in admitted if per_root[a["root"]] < lineage_cap]
        parents += [dict(g=m["g"], root=m["root"]) for m in sorted(near, key=lambda m: -m["score"])[:50]
                    if per_root[m["root"]] < lineage_cap]
        jobs = []
        for _ in range(batch):
            g = propose(rng, archive, parents)
            jobs.append(dict(g=g, seed=seed0 + n))
            n += 1
        with ProcessPoolExecutor(W()) as ex:
            res = list(ex.map(_pf, jobs, chunksize=4))
        for ok, rec, g, s in res:
            gates[rec.get("gate")] += 1
            archive.append(g)
            root = g["meta"].get("root") or ghash(g)
            if ok:
                if per_root[root] >= lineage_cap:
                    gates["LINEAGE_CAP"] += 1
                    continue
                per_root[root] += 1
                admitted.append(dict(g=g, seed=s, root=root, stratum=g["meta"].get("stratum"), pre=rec, h=ghash(g)))
            elif rec.get("gate") in ("G3_ECONOMY", "G4_EXPOSURE", "G5_DEMAND", "G6_SURROGATE"):
                sc = near_miss(rec) if rec.get("gate") == "G3_ECONOMY" else 0.5 + (rec.get("demand") or 0)
                if sc is not None and sc > 0:
                    near.append(dict(g=g, root=root, score=float(sc), gate=rec.get("gate")))
                    near = sorted(near, key=lambda m: -m["score"])[:500]
        archive = archive[-4000:]
        strat = collections.Counter(a["stratum"] for a in admitted)
        print(f"candidates {n} admitted {len(admitted)} lineages {len(set(a['root'] for a in admitted))} strata {dict(strat)} "
              f"gates {dict(gates)} {round((time.time() - t0) / 60, 1)} min", flush=True)
        dump(dict(candidates=n, gates=dict(gates), admitted=admitted, partial=True, lineage_cap=lineage_cap,
                  near_miss_top=[dict(root=m["root"], score=m["score"], gate=m["gate"]) for m in near[:50]]), "waveA.json")
    dump(dict(candidates=n, gates=dict(gates), admitted=admitted, partial=False, lineage_cap=lineage_cap,
              minutes=round((time.time() - t0) / 60, 1),
              near_miss_top=[dict(root=m["root"], score=m["score"], gate=m["gate"]) for m in near[:50]]), "waveA.json")
    print("wave A done", len(admitted), "admitted from", n, flush=True)


# ------------------------------------------------------------------ Wave B (collision)


def compact(c):
    return dict(cap=c["cap"], best_null=c["best_null"], n_test=c["n_test"], seen_frac=c["seen_frac"], holdout=c["holdout"],
                n_samples=c["n_samples"], ladder=c["ladder"],
                subs={k: {kk: vv for kk, vv in v.items()} for k, v in c["subs"].items()})


def ratios(g, st, cap, life):
    """Latent control ratios (s14) recorded per world."""
    x = st["x"]
    cells = x.size
    E = np.abs(np.fft.fftn(x)) ** 2
    e = np.sort(E.reshape(-1))[::-1]
    k90 = int(np.searchsorted(np.cumsum(e) / e.sum(), 0.9) + 1)
    dims = st["dims"]
    lr90 = []
    for s in range(1, len(dims)):
        M = x.reshape(int(np.prod(dims[:s])), -1)
        sv = np.linalg.svd(M, compute_uv=False) ** 2
        r = int(np.searchsorted(np.cumsum(sv) / sv.sum(), 0.9) + 1)
        lr90.append(r * (M.shape[0] + M.shape[1]))
    DL = min(k90, min(lr90) if lr90 else k90)
    tr = g["transition"]
    return dict(mem_over_cells=cap / cells, mem_over_DL=cap / max(1, DL), DL=DL, DL_fourier90=k90, DL_lowrank90=min(lr90) if lr90 else None,
                learn_over_change=(life.get("updates", 0) / tr["drift_period"]) if tr["drift"] > 0 else 0.0,
                coverage=float(len(np.unique(st["c"])) / cells),
                forget_rate=g["memory"]["forget_rate"], n_org=g["boundary"]["n_org"],
                door_close=g["irreversibility"]["door_close"], kappa=g["resource"].get("kappa"))


def unit(g, seed, *, bands=True, exposure=True, fields=("real", "marg", "shuf")):
    """One world x seed: streams for each field; the panel at the native budget on every field; the
    budget ladder and the exposure ladder on the real stream."""
    out = dict(seed=seed)
    streams = {}
    for f in fields:
        st, life = experience(g, seed, field=f)
        out[f"life_{f}"] = dict(status=life.get("status"), life_frac=life.get("life_frac"), updates=life.get("updates"),
                                consolidations=life.get("consolidations"), steps=life.get("steps"), U=life.get("U"))
        if st is None or life.get("status") != "OK" or len(st["y"]) < 50:
            out[f] = None
            continue
        streams[f] = st
    if "real" not in streams:
        out["status"] = "NO_STREAM"
        return out
    st = streams["real"]
    cells = st["x"].size
    cap = mem_cap(g, cells)
    for f, s in streams.items():
        out[f] = compact(collide(s, cap, seed))
    out["ratios"] = ratios(g, st, cap, out["life_real"])
    if bands:
        lad = []
        for b in BANDS:
            c = max(1, int(b * cells))
            if c < sum(st["dims"]) + 1:
                continue
            lad.append((b, out["real"] if c == cap else compact(collide(st, c, seed))))
        out["band_ladder"] = lad
    if exposure:
        n = len(st["y"])
        out["exposure_ladder"] = [(q, compact(collide(st, cap, seed, upto=max(50, int(q * n))))) for q in (0.25, 0.5)] + [(1.0, out["real"])]
    out["status"] = "OK"
    return out


def _unit_job(a):
    g, seed, kw = a
    t0 = time.time()
    try:
        u = unit(g, seed, **kw)
    except Exception as ex:
        u = dict(status="CRASH", reason=f"{type(ex).__name__}: {ex}"[:300])
    u["secs"] = round(time.time() - t0, 1)
    return u


def flags(u):
    if u.get("status") != "OK":
        return []
    fl = []
    for s, det in (("interp", "X1"), ("recomb", "X6")):
        for k, a, sd in completion(u["real"], u.get("marg"), s):
            fl.append(dict(det=det, substrate=k, set=s, XC=a, SD=sd))
    for lad_name in ("band_ladder", "exposure_ladder"):
        for c in crossovers(u.get(lad_name) or []):
            fl.append(dict(det="X3", ladder=lad_name, **c))
    for c in superadditive(u["real"], u.get("marg")):
        fl.append(dict(det="X4", **c))
    return fl


def wave_b():
    A = load("waveA.json")
    jobs = [(a["g"], a["seed"], {}) for a in A["admitted"]]
    t0 = time.time()
    with ProcessPoolExecutor(W()) as ex:
        units = list(ex.map(_unit_job, jobs))
    rows = []
    for a, u in zip(A["admitted"], units):
        rows.append(dict(h=a["h"], root=a["root"], stratum=a["stratum"], seed=a["seed"], carrier=a["g"]["memory"].get("carrier"),
                         gen=a["g"]["substrate"]["gen"], unit=u, flags=flags(u)))
    dump(rows, "waveB.json")
    fc = collections.Counter(f["det"] for r in rows for f in r["flags"])
    lin = {d: len({r["root"] for r in rows if any(f["det"] == d for f in r["flags"])}) for d in fc}
    print("wave B", len(rows), "worlds", round((time.time() - t0) / 60, 1), "min; flags", dict(fc), "lineages", lin, flush=True)


# ------------------------------------------------------------------ Wave C (replication)


def _key(r, f):
    if f["det"] in ("X1", "X6"):
        return (r["h"], f["det"], f["substrate"], f["set"])
    if f["det"] == "X3":
        return (r["h"], "X3", f["ladder"], tuple(f["pair"]), f["set"], tuple(f["levels"]))
    return (r["h"], "X4", f["set"])


def select_flags(rows, k=48, per_det=12, per_lineage=2):
    """Diverse selection: strongest first within detector, <= per_lineage units per lineage."""
    chosen, used, per_d = [], collections.Counter(), collections.Counter()
    cand = []
    for r in rows:
        for f in r["flags"]:
            if f["det"] == "X3":
                strength = min(abs(f["d"][0]), abs(f["d"][1]))
            else:
                strength = f.get("XC") if f.get("XC") is not None else f.get("excess", 0.0)
            cand.append((f["det"], float(strength), r, f))
    seen = set()
    for det in ("X6", "X1", "X4", "X3"):
        for d, s, r, f in sorted([c for c in cand if c[0] == det], key=lambda c: -c[1]):
            kk = _key(r, f)
            if kk in seen or used[(r["root"], det)] >= per_lineage or per_d[det] >= per_det or len(chosen) >= k:
                continue
            seen.add(kk)
            used[(r["root"], det)] += 1
            per_d[det] += 1
            chosen.append((r, f))
    return chosen


def replicate_status(f, units):
    """Hits/null hits for flag f over replicate units."""
    hits = nh = deg = 0
    sds = []
    for u in units:
        if u.get("status") != "OK":
            deg += 1
            continue
        if f["det"] in ("X1", "X6"):
            real = [x for x in completion(u["real"], None, f["set"]) if x[0] == f["substrate"]]
            marg = [x for x in completion(u["marg"], None, f["set"]) if x[0] == f["substrate"]] if u.get("marg") else []
            xr = u["real"]["subs"].get(f["substrate"], {}).get("XC", {}).get(f["set"])
            xm = (u["marg"] or {}).get("subs", {}).get(f["substrate"], {}).get("XC", {}).get(f["set"]) if u.get("marg") else None
            hits += bool(real)
            nh += bool(marg)
            if xr is not None:
                sds.append(xr - (xm if xm is not None else 0.0))
        elif f["det"] == "X3":
            lad = u.get(f["ladder"]) or []
            rev = [c for c in crossovers(lad, (f["set"],)) if tuple(c["pair"]) == tuple(f["pair"])]
            hits += bool(rev)
            sds.append(1.0 if rev else 0.0)
        elif f["det"] == "X4":
            sa = [c for c in superadditive(u["real"], u.get("marg")) if c["set"] == f["set"]]
            hits += bool(sa)
            sds.append(sa[0]["SD"] if sa else 0.0)
    return hits, nh, deg, sds


def wave_c(n_rep=5):
    rows = load("waveB.json")
    chosen = select_flags(rows)
    jobs, idx = [], []
    for q, (r, f) in enumerate(chosen):
        A = next(a for a in load("waveA.json")["admitted"] if a["h"] == r["h"])
        for s in range(n_rep):
            kw = dict(bands=f["det"] == "X3" and f.get("ladder") == "band_ladder",
                      exposure=f["det"] == "X3" and f.get("ladder") == "exposure_ladder",
                      fields=("real", "marg") if f["det"] != "X3" else ("real", "marg"))
            jobs.append((A["g"], 6_000_000 + q * 10 + s, kw))
            idx.append(q)
    with ProcessPoolExecutor(W()) as ex:
        units = list(ex.map(_unit_job, jobs))
    by = collections.defaultdict(list)
    for q, u in zip(idx, units):
        by[q].append(u)
    out = []
    for q, (r, f) in enumerate(chosen):
        hits, nh, deg, sds = replicate_status(f, by[q])
        st = status_units(hits, nh, n_rep, sds, deg)
        if f["det"] == "X3":  # crossover: seed-split replication (both halves) instead of a surrogate null
            first, second = [u for u in by[q][:2]], [u for u in by[q][2:]]
            h1 = replicate_status(f, first)[0]
            h2 = replicate_status(f, second)[0]
            st = "REPLICATED" if hits >= 3 and h1 >= 1 and h2 >= 1 else ("UNRESOLVED" if hits == 2 else "FALSIFIED")
            # structure dependence of the crossover: does the same reversal appear on the surrogate budget ladder?
        out.append(dict(q=q, h=r["h"], root=r["root"], flag=f, status=st, hits=hits, null_hits=nh, degenerate=deg,
                        median_SD=float(np.median(sds)) if sds else None, units=by[q]))
        print("C", q, f["det"], f.get("substrate") or f.get("pair"), f.get("set"), st, hits, nh, flush=True)
    dump(out, "waveC.json")


# ------------------------------------------------------------------ Waves D-G (survivors only)


def survivors(kind=("X1", "X6", "X4")):
    C = load("waveC.json")
    return [c for c in C if c["flag"]["det"] in kind and c["status"] == "STRUCTURE-DEPENDENT"]


def crossings():
    C = load("waveC.json")
    return [c for c in C if c["flag"]["det"] == "X3" and c["status"] == "REPLICATED"]


def _genome(h):
    return next(a for a in load("waveA.json")["admitted"] if a["h"] == h)


def wave_d(levels=7, seeds=4):
    """Local physics: sweep the budget (always) and the exposure for every survivor / crossover;
    bracket boundaries (adjacent levels differ by > 3 x pooled sd, same sign in both seed halves,
    phenomenon present on one side and absent on the other)."""
    targets = [("specimen", c) for c in survivors()] + [("crossover", c) for c in crossings()]
    out = []
    for kind, c in targets[:12]:
        A = _genome(c["h"])
        g = A["g"]
        jobs = []
        for s in range(seeds):
            jobs.append((g, 6_500_000 + c["q"] * 10 + s, dict(bands=False, exposure=False, fields=("real",))))
        with ProcessPoolExecutor(W()) as ex:
            base = list(ex.map(_unit_job, jobs))
        res = dict(kind=kind, q=c["q"], h=c["h"], flag=c["flag"], sweeps={})
        # budget sweep on each seed's own real stream (offline: same stream, different caps)
        from .collider import experience as exp
        rows = []
        for s in range(seeds):
            st, life = exp(g, 6_500_000 + c["q"] * 10 + s)
            if st is None or life.get("status") != "OK":
                continue
            cells = st["x"].size
            lo = sum(st["dims"]) + 1
            caps = sorted(set(int(v) for v in np.geomspace(lo, 0.25 * cells, levels)))
            for cp_ in caps:
                cc = collide(st, cp_, 6_500_000 + c["q"] * 10 + s)
                rows.append(dict(seed=s, cap=cp_, cap_over_cells=cp_ / cells, res=compact(cc)))
        res["sweeps"]["budget"] = rows
        res["boundary"] = bracket(rows, c["flag"])
        out.append(res)
        print("D", kind, c["q"], c["flag"]["det"], "boundary", res["boundary"], flush=True)
    dump(out, "waveD.json")


def _stat(res, flag):
    if flag["det"] in ("X1", "X6"):
        v = res["subs"].get(flag["substrate"], {})
        return v.get("XC", {}).get(flag["set"]) if v.get("status") == "OK" else None
    if flag["det"] == "X3":
        a, b = flag["pair"]
        va, vb = res["subs"].get(a, {}), res["subs"].get(b, {})
        if va.get("status") != "OK" or vb.get("status") != "OK":
            return None
        x, y = va["AC"].get(flag["set"]), vb["AC"].get(flag["set"])
        return None if x is None or y is None else x - y
    if flag["det"] == "X4":
        h, a, l = (res["subs"].get(k, {}) for k in ("hybrid_al", "additive", "lowrank"))
        if any(v.get("status") != "OK" for v in (h, a, l)):
            return None
        return h["AC"][flag["set"]] - max(a["AC"][flag["set"]], l["AC"][flag["set"]])


def bracket(rows, flag):
    """Levels = rank of cap within each seed (budgets differ per seed only if cells differ)."""
    by = collections.defaultdict(dict)
    for r in rows:
        v = _stat(r["res"], flag)
        if v is not None:
            by[round(r["cap_over_cells"], 4)][r["seed"]] = v
    lv = sorted(by)
    found = []
    for a, b in zip(lv, lv[1:]):
        A, B = by[a], by[b]
        common = sorted(set(A) & set(B))
        if len(common) < 4:
            continue
        va, vb = np.array([A[s] for s in common]), np.array([B[s] for s in common])
        pooled = np.sqrt((va.var(ddof=1) + vb.var(ddof=1)) / 2) + 1e-9
        d = vb.mean() - va.mean()
        h1 = np.sign(vb[:2].mean() - va[:2].mean())
        h2 = np.sign(vb[2:].mean() - va[2:].mean())
        present = lambda v: v >= TH if flag["det"] != "X3" else abs(v) >= TH
        crosses = (present(va.mean()) != present(vb.mean())) if flag["det"] != "X3" else (np.sign(va.mean()) != np.sign(vb.mean()) and present(va.mean()) and present(vb.mean()))
        if abs(d) > 3 * pooled and h1 == h2 == np.sign(d) and crosses:
            found.append(dict(between=(a, b), means=(float(va.mean()), float(vb.mean())), pooled_sd=float(pooled)))
    return found


def wave_e():
    out = []
    for c in survivors()[:12]:
        A = _genome(c["h"])
        g, f = A["g"], c["flag"]
        res = dict(q=c["q"], h=c["h"], flag=f, seeds=[])
        for s in range(3):
            seed = 6_800_000 + c["q"] * 10 + s
            st, life = experience(g, seed)
            if st is None or life.get("status") != "OK":
                continue
            cap = mem_cap(g, st["x"].size)
            if f["set"] == "recomb":
                stR, blk, _ = holdout(st, np.random.default_rng(seed + 29))
                if stR is None:
                    continue
                stream, T = stR, blk
            else:
                stream, T = st, test_sets(st, np.random.default_rng(seed + 17))["interp"]
            cc = collide(st, cap, seed)
            res["seeds"].append(dict(seed=seed, autopsy=autopsy(f["substrate"], stream, T, cap, seed, None, cc["best_null"][f["set"]])))
            # reskin: a genuine field model must LOSE on the reskinned (axis-permuted) field (negative control)
            mem, _ = train(f["substrate"], stream, cap, seed + 101)
            xr = st["x"].copy()
            rr = np.random.default_rng(seed + 55)
            for m in range(xr.ndim):
                xr = np.take(xr, rr.permutation(xr.shape[m]), axis=m)
            p = mem.predict(_addr(st["dims"], T))
            res["seeds"][-1]["reskin_AC"] = AC(p, xr.reshape(-1)[T], st["V0"])
            res["seeds"][-1]["native_AC"] = AC(p, st["x"].reshape(-1)[T], st["V0"])
        car = [s["autopsy"].get("carrier") for s in res["seeds"]]
        res["carrier"] = sum(bool(x) for x in car) >= 2
        res["reskin_loses"] = sum(s["reskin_AC"] < s["native_AC"] - TH for s in res["seeds"]) >= 2
        out.append(res)
        print("E", c["q"], f["det"], f["substrate"], "carrier", res["carrier"], "reskin_loses", res["reskin_loses"], flush=True)
    dump(out, "waveE.json")


def wave_f():
    """Transfer / recombination: (a) three fresh recombination blocks per seed; (b) artifact transfer to
    a related world with the same field (observation noise x2, policy changed) without retraining."""
    out = []
    for c in survivors()[:12]:
        A = _genome(c["h"])
        g, f = A["g"], c["flag"]
        res = dict(q=c["q"], h=c["h"], flag=f, blocks=[], related=[])
        for s in range(3):
            seed = 6_900_000 + c["q"] * 10 + s
            st, life = experience(g, seed)
            if st is None or life.get("status") != "OK":
                continue
            cap = mem_cap(g, st["x"].size)
            for b in range(3):
                stR, blk, hi = holdout(st, np.random.default_rng(seed * 7 + b))
                if stR is None:
                    continue
                tt = dict(interp=np.zeros(0, int), novel=np.zeros(0, int), recomb=blk)
                from .collider import null_ladder
                lad = null_ladder(stR, cap, tt)
                bn = max(v["recomb"] for v in lad.values() if v["recomb"] is not None)
                simple = []
                for k in SIMPLE:
                    m, _ = train(k, stR, cap, seed + 101)
                    if m is not None:
                        simple.append(score(m, stR, tt)["recomb"])
                bn = max([bn] + [v for v in simple if v is not None])
                mem, _ = train(f["substrate"], stR, cap, seed + 101)
                if mem is None:
                    continue
                res["blocks"].append(dict(seed=s, block=b, XC=score(mem, stR, tt)["recomb"] - bn, removed=hi["removed"]))
            # related world: same field (same seed -> same world_gen), altered sensing noise and policy
            g2 = copy.deepcopy(g)
            g2["observation"]["noise_sd"] = min(1.0, 2 * g2["observation"]["noise_sd"] + 0.05)
            g2["search"]["policy"] = "novelty" if g2["search"]["policy"] != "novelty" else "eps_greedy"
            st2, life2 = experience(g2, seed)
            if st2 is None:
                continue
            mem, _ = train(f["substrate"], st, cap, seed + 101)
            T2 = test_sets(st2, np.random.default_rng(seed + 18))["interp"]
            if mem is None or len(T2) < 32:
                continue
            cc2 = collide(st2, cap, seed)
            p = mem.predict(_addr(st2["dims"], T2))
            fresh, _ = train(f["substrate"], st2, cap, seed + 101)
            res["related"].append(dict(seed=s, transplant_AC=AC(p, st2["x"].reshape(-1)[T2], st2["V0"]),
                                       fresh_AC=AC(fresh.predict(_addr(st2["dims"], T2)), st2["x"].reshape(-1)[T2], st2["V0"]),
                                       best_null=cc2["best_null"]["interp"]))
        xb = [b["XC"] for b in res["blocks"]]
        res["recombines"] = bool(xb) and float(np.median(xb)) >= TH
        tr = [r["transplant_AC"] - r["best_null"] for r in res["related"] if r["best_null"] is not None]
        res["transfers"] = len(tr) >= 2 and sum(v >= TH for v in tr) >= 2
        out.append(res)
        print("F", c["q"], f["det"], f["substrate"], "recombines", res["recombines"], "transfers", res["transfers"], flush=True)
    dump(out, "waveF.json")


def wave_g():
    """Hybridisation / conversion for survivors: distil the trained specimen into each other structured
    kind (cost = distillation flops + workspace); compare with training that kind directly (the
    conversion must be necessary)."""
    from ensorain.wtp.organism import convert
    out = []
    for c in survivors()[:12]:
        A = _genome(c["h"])
        g, f = A["g"], c["flag"]
        seed = 7_100_000 + c["q"]
        st, life = experience(g, seed)
        if st is None or life.get("status") != "OK":
            continue
        cap = mem_cap(g, st["x"].size)
        T = test_sets(st, np.random.default_rng(seed + 17))["interp"]
        if len(T) < 32:
            continue
        cc = collide(st, cap, seed)
        bn = cc["best_null"]["interp"]
        src, _ = train(f["substrate"], st, cap, seed + 101)
        xs = AC(src.predict(_addr(st["dims"], T)), st["x"].reshape(-1)[T], st["V0"]) - bn
        rows = []
        for tgt in STRUCT:
            if tgt == f["substrate"] or tgt == "hybrid_al":
                continue
            try:
                sample = np.random.default_rng(seed).choice(st["x"].size, size=min(256, st["x"].size), replace=False)
                new, fl = convert(src, tgt, st["dims"], cap, np.random.default_rng(seed), _addr(st["dims"], sample), None)
            except (ValueError, KeyError) as ex:
                rows.append(dict(target=tgt, status=f"INCOMPATIBLE: {ex}"))
                continue
            direct, _ = train(tgt, st, cap, seed + 101)
            xc_conv = AC(new.predict(_addr(st["dims"], T)), st["x"].reshape(-1)[T], st["V0"]) - bn
            xc_dir = AC(direct.predict(_addr(st["dims"], T)), st["x"].reshape(-1)[T], st["V0"]) - bn if direct is not None else None
            rows.append(dict(target=tgt, XC_before=xs, XC_after=xc_conv, XC_direct=xc_dir, conv_flops=fl,
                             size_before=src.n_floats(), size_after=new.n_floats(),
                             X7=bool(xc_conv >= xs + TH and (xc_dir is None or xc_conv >= xc_dir + TH))))
        out.append(dict(q=c["q"], h=c["h"], flag=f, conversions=rows))
        print("G", c["q"], f["substrate"], [(r["target"], r.get("X7")) for r in rows], flush=True)
    dump(out, "waveG.json")


# ------------------------------------------------------------------ verdict (s12)


def verdict():
    A = load("waveA.json")
    V = load("validation.json") if os.path.exists(os.path.join(OUT, "validation.json")) else {}
    B = load("waveB.json") if os.path.exists(os.path.join(OUT, "waveB.json")) else []
    C = load("waveC.json") if os.path.exists(os.path.join(OUT, "waveC.json")) else []
    D = load("waveD.json") if os.path.exists(os.path.join(OUT, "waveD.json")) else []
    E = load("waveE.json") if os.path.exists(os.path.join(OUT, "waveE.json")) else []
    F = load("waveF.json") if os.path.exists(os.path.join(OUT, "waveF.json")) else []
    G = load("waveG.json") if os.path.exists(os.path.join(OUT, "waveG.json")) else []
    specimens = []
    for c in [c for c in C if c["flag"]["det"] in ("X1", "X6", "X4") and c["status"] == "STRUCTURE-DEPENDENT"]:
        e = next((e for e in E if e["q"] == c["q"]), None)
        f = next((f for f in F if f["q"] == c["q"]), None)
        d = next((d for d in D if d["q"] == c["q"] and d["kind"] == "specimen"), None)
        gg = next((x for x in G if x["q"] == c["q"]), None)
        extra = []
        if f and f.get("recombines"):
            extra.append("RECOMBINES")
        if f and f.get("transfers"):
            extra.append("TRANSFERS")
        if d and d.get("boundary"):
            extra.append("PHASE_BOUNDARY")
        if gg and any(r.get("X7") for r in gg["conversions"]):
            extra.append("CONVERSION")
        full = bool(e and e.get("carrier") and e.get("reskin_loses") and extra)
        specimens.append(dict(q=c["q"], h=c["h"], root=c["root"], flag=c["flag"], carrier=bool(e and e.get("carrier")),
                              reskin_loses=bool(e and e.get("reskin_loses")), extra=extra, full_chain=full))
    xover = [d for d in D if d["kind"] == "crossover" and d.get("boundary")]
    rep_x = [c for c in C if c["flag"]["det"] == "X3" and c["status"] == "REPLICATED"]
    valid = bool(V.get("ALL_PASS"))
    if not valid:
        v = "STILL EASY TO FOOL -- REDESIGN"
    elif any(s["full_chain"] for s in specimens):
        v = "CANDIDATE PHYSICS FOUND -- DEEPEN"
    elif rep_x and xover:
        v = "SUBSTRATE PHASE STRUCTURE FOUND -- MAP"
    else:
        v = "INSTRUMENT CLEAN, NO SIGNAL -- BROADEN"
    lin = len({a["root"] for a in A["admitted"]})
    summ = dict(validation=V, candidates=A["candidates"], gates=A["gates"], admitted=len(A["admitted"]), lineages=lin,
                flags=dict(collections.Counter(f["det"] for r in B for f in r["flags"])),
                flag_lineages={d: len({r["root"] for r in B if any(f["det"] == d for f in r["flags"])}) for d in ("X1", "X6", "X3", "X4")},
                wave_c={f"{d}:{s}": n for (d, s), n in collections.Counter((c["flag"]["det"], c["status"]) for c in C).items()} if C else {},
                specimens=specimens, replicated_crossovers=len(rep_x), bracketed_crossovers=len(xover),
                sd_lineages=len({s["root"] for s in specimens}), VERDICT=v)
    dump(summ, "summary.json")
    print(json.dumps({k: v for k, v in summ.items() if k != "validation"}, indent=1, default=str), flush=True)


STEPS = dict(A=wave_a, B=wave_b, C=wave_c, D=wave_d, E=wave_e, F=wave_f, G=wave_g, verdict=verdict)

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which == "validate":
        from .validate3 import validate
        validate()
    elif which == "all":
        from .validate3 import validate
        print("===== validate", flush=True)
        validate()
        for k in ("A", "B", "C", "D", "E", "F", "G", "verdict"):
            print("=====", k, flush=True)
            STEPS[k]()
        print("ALLDONE", flush=True)
    else:
        STEPS[which]()
