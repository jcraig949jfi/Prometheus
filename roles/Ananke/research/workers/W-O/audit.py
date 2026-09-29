"""W-O step 3: re-run the inventory (PLAN.md frozen). Usage:
    python audit.py <shard i> <n shards> [threads=1]
Groups (source, loader, specimen, offset) processed in preregistered sha256 order,
interleaved over shards. Appends one JSON line per group to out/rerun_s<i>.jsonl;
skips groups already present (resume)."""
import csv, collections, hashlib, json, math, sys, time
import numpy as np, torch
import runner as R
from prometheus.ananke import lens_swap

OUT = R.HERE / "out"


def gkey(src, sp, off):
    return hashlib.sha256(f"{src}|{sp}|{off}".encode()).hexdigest()


def groups():
    rows = list(csv.DictReader(open(OUT / "inventory.csv")))
    g = collections.OrderedDict()
    for r in rows:
        k = (r["source"], r["loader"], r["specimen"], r["offset"], r["trial_set"], r["family"])
        g.setdefault(k, []).append(r)
    keys = sorted(g, key=lambda k: gkey(k[0], k[2], k[3]))
    return keys, g


def every_subset(keys):
    strata = collections.defaultdict(list)
    for k in keys:
        strata[(k[0], k[5])].append(k)
    sel = set()
    for s, ks in strata.items():
        if s[0] == "SCT":
            sel.update(ks)
            continue
        ks = sorted(ks, key=lambda k: gkey(k[0], k[2], k[3]))
        sel.update(ks[:math.ceil(0.25 * len(ks))])
    return sel


def arm_names(label):
    if label.startswith("pay") and label[3:].isdigit():
        return ("pay", int(label[3:]))
    return R.ARMS[label]


def run_group(k, rows, do_every):
    src, loader, sp, off, tset, fam = k
    ph, env, g = R.load(loader, sp)
    o = R.sct_offset(env) if off == "" else int(off)
    sd = R.seeds()
    trials = list(range(env.trials)) if tset == "all" else list(range(1, env.trials))
    labels = sorted({r["arm"] for r in rows})
    arms = {lab: arm_names(lab) for lab in labels}
    site_lab = next((l for l in labels if arms[l] == R.SITE), None)
    chan_lab = next((l for l in labels if arms[l] == R.FLIGHT), None)
    if site_lab is None:
        arms["site_all"] = R.SITE
        site_lab = "site_all"
    if chan_lab is None:
        arms["channel_all"] = R.FLIGHT
        chan_lab = "channel_all"
    t0 = time.time()
    ep, npt, apt, n0, s0 = R.fork_single(ph, g, env, sd, arms, o, trials)
    scored_tr = [t for t in trials if ep.scored[:, t].any()]
    res = {"group": list(k), "offset_used": o, "trials": trials, "M": len(sd), "ns": hex(R.NS),
           "arms": {}, "t_single": None}
    for lab in arms:
        v = R.verdicts(npt, apt[lab], trials)
        v["recorded"] = lab in labels
        res["arms"][lab] = v
    c = lens_swap.census(npt, apt[site_lab], apt[chan_lab], s0[site_lab], s0[chan_lab], scored_tr)
    c["class"] = lens_swap.classify(c)
    f = lens_swap.census_follow(n0, s0[site_lab], s0[chan_lab], ep.scored, scored_tr)
    f["class"] = lens_swap.classify(f)
    res["census"] = {kk: c[kk] for kk in ("eligible", "fS", "fC", "fN", "fX", "ftie", "identity", "class", "ci99",
                                          "site_acc", "chan_acc")}
    res["census_follow"] = {kk: f.get(kk) for kk in ("eligible", "fS", "fC", "fN", "fX", "identity", "class")}
    res["t_single"] = round(time.time() - t0, 1)
    if do_every:
        t1 = time.time()
        ev = {}
        normal_arms = {l: arms[l] for l in labels if arms[l][0] != "pay"}
        if normal_arms:
            r = R.every_arms(ph, g, env, sd, normal_arms, o)
            nrm = r.per_trial["normal"]
            for l in normal_arms:
                ev[l] = R.verdicts(nrm, r.per_trial[l], trials)
        pays = [l for l in labels if arms[l][0] == "pay"]
        if pays:
            base = R.lens.run(ph, g, env, sd)
            nb = R.envs.per_trial(base.ep, base.trace).astype(float)
            nb[~base.ep.scored] = np.nan
            for l in pays:
                tr = R.every_pay(ph, g, env, sd, arms[l][1], o)
                p = R.envs.per_trial(tr.ep, tr.trace).astype(float)
                p[~tr.ep.scored] = np.nan
                ev[l] = R.verdicts(nb, p, trials)
        res["every"] = ev
        res["t_every"] = round(time.time() - t1, 1)
    return res


def run_every_only(k, rows):
    """EVERY arms only, for a subset group whose SINGLE record exists (deviation A8)."""
    src, loader, sp, off, tset, fam = k
    ph, env, g = R.load(loader, sp)
    o = R.sct_offset(env) if off == "" else int(off)
    sd = R.seeds()
    trials = list(range(env.trials)) if tset == "all" else list(range(1, env.trials))
    labels = sorted({r["arm"] for r in rows})
    arms = {lab: arm_names(lab) for lab in labels}
    t1 = time.time()
    ev = {}
    normal_arms = {l: arms[l] for l in labels if arms[l][0] != "pay"}
    if normal_arms:
        r = R.every_arms(ph, g, env, sd, normal_arms, o)
        nrm = r.per_trial["normal"]
        for l in normal_arms:
            ev[l] = R.verdicts(nrm, r.per_trial[l], trials)
    pays = [l for l in labels if arms[l][0] == "pay"]
    if pays:
        base = R.lens.run(ph, g, env, sd)
        nb = R.envs.per_trial(base.ep, base.trace).astype(float)
        nb[~base.ep.scored] = np.nan
        for l in pays:
            tr = R.every_pay(ph, g, env, sd, arms[l][1], o)
            p = R.envs.per_trial(tr.ep, tr.trace).astype(float)
            p[~tr.ep.scored] = np.nan
            ev[l] = R.verdicts(nb, p, trials)
    return {"group": list(k), "every": ev, "t_every": round(time.time() - t1, 1), "every_only": True}


if __name__ == "__main__":
    i, n = int(sys.argv[1]), int(sys.argv[2])
    th = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    torch.set_num_threads(th)
    keys, g = groups()
    sub = every_subset(keys)
    mine = [k for j, k in enumerate(keys) if j % n == i]
    import os as _os
    if _os.environ.get("WO_REVERSE"):              # helper for a slow shard (A11): same list, reversed
        mine = mine[::-1]
    import glob, os
    mode = os.environ.get("WO_MODE", "both")        # both | single | every (deviation A8)
    out = OUT / (f"rerun_every_s{i}.jsonl" if mode == "every" else
                 (f"rerun_s{i}r.jsonl" if os.environ.get("WO_REVERSE") else f"rerun_s{i}.jsonl"))
    done, has_every = set(), set()
    for fn in glob.glob(str(OUT / "rerun_s*.jsonl")) + glob.glob(str(OUT / "rerun_every_s*.jsonl")):
        for l in open(fn):
            if l.strip():
                x = json.loads(l)
                if "error" in x:
                    continue
                done.add(tuple(x["group"]))
                if "every" in x:
                    has_every.add(tuple(x["group"]))
    if mode == "every":
        mine = [k for k in mine if k in sub and tuple(k) not in has_every]
        done = set()
    print(f"shard {i}/{n}: {len(mine)} groups, done {len(done)}, every-subset total {len(sub)}", flush=True)
    for j, k in enumerate(mine):
        if tuple(k) in done:
            continue
        t0 = time.time()
        try:
            if mode == "every":
                res = run_every_only(k, g[k])
            else:
                res = run_group(k, g[k], (k in sub) and mode == "both")
        except Exception as e:
            import traceback
            res = {"group": list(k), "error": repr(e), "tb": traceback.format_exc()}
        res["wall"] = round(time.time() - t0, 1)
        with out.open("a") as f:
            f.write(json.dumps(res, default=float) + "\n")
        print(f"[{j+1}/{len(mine)}] {k[0]} {k[2][:8]} o={k[3]} arms={len(g[k])} "
              f"{ {a: v['abs'] for a, v in (res.get('arms') or res.get('every') or {}).items()} } every={'every' in res} {res['wall']}s", flush=True)
