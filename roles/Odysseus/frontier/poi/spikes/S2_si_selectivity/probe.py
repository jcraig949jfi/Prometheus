"""S2 spike: do the delegate's SI-selectivity readings (a)-(c) survive the 0.30 AC margin, arm-count balance,
and a permutation null?  Stdlib only.  Reads DEV rows only (seeds 9.33M / 9.41M / 9.5M; campaign seeds >= 1e9).

Inputs (read-only):
  ensorain/lm01/dev/selection_v2.json   (arm-selection v2, seeds 9_410_000-015, 26 arms per world)
  ensorain/lm01/FROZEN_SELECTION.json   (one frozen arm per class per stratum, chosen on selection_v2)
  ensorain/lm01/dev/margins/*.jsonl     (margins v1, seeds 9_500_000-015: frozen S/L/H arms, AC_a on full test set,
                                         and reservoir ladder random|B vs declared-policy|B at matched B)
  ensorain/lm01/dev/fixture_reservoir.json (eviction positive-control medians, seeds 9_330_000-003)
Run:  python3 probe.py   (from this directory or anywhere; paths are resolved from the repo root)
"""
import glob
import json
import math
import os
import random
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
DEV = os.path.join(ROOT, "ensorain", "lm01", "dev")
DELTA = 0.30          # PREREG_WTP_LM01.md s6.0 governing tolerance
SENS = (0.15, 0.60)   # prereg sensitivity deltas
NPERM = 2000
NBOOT = 1000
SEED = 20260927
CAMPAIGN_FLOOR = 10 ** 9
CLS = {"S": "SELECTIVE", "L": "LOSSLESS", "H": "HYBRID", "R": "RESERVOIR_EVICT"}

# one-sided 0.95 t quantiles (90% two-sided CI), df 1..40
T95 = [None, 6.314, 2.920, 2.353, 2.132, 2.015, 1.943, 1.895, 1.860, 1.833, 1.812, 1.796, 1.782, 1.771, 1.761,
       1.753, 1.746, 1.740, 1.734, 1.729, 1.725, 1.721, 1.717, 1.714, 1.711, 1.708, 1.706, 1.703, 1.701, 1.699, 1.697,
       1.696, 1.694, 1.692, 1.691, 1.690, 1.688, 1.687, 1.686, 1.685, 1.684]


def H(xs):
    n = len(xs)
    return -sum(c / n * math.log2(c / n) for c in Counter(xs).values()) if n else 0.0


def MI(w, x):
    return H(w) + H(x) - H(list(zip(w, x)))


def CMI(w, x, z):   # I(W;X|Z) = H(W,Z)+H(X,Z)-H(W,X,Z)-H(Z)
    return H(list(zip(w, z))) + H(list(zip(x, z))) - H(list(zip(w, x, z))) - H(z)


def verdict(diffs, delta=DELTA):
    """Program rule (s6.0): 90% two-sided t CI of the paired per-world difference."""
    n = len(diffs)
    if n < 2:
        return dict(n=n, verdict="NO_DATA")
    m = sum(diffs) / n
    sd = math.sqrt(sum((d - m) ** 2 for d in diffs) / (n - 1))
    t = T95[min(n - 1, 40)]
    lo, hi = m - t * sd / math.sqrt(n), m + t * sd / math.sqrt(n)
    v = "WIN+" if lo > delta else "WIN-" if hi < -delta else "EQUIV" if (lo > -delta and hi < delta) else "UNRESOLVED"
    return dict(n=n, mean=m, lo=lo, hi=hi, verdict=v)


def winner(acs, delta):
    """acs: {class: best AC in class}. Returns class if it beats every other class by > delta, else 'TIE'."""
    items = sorted(acs.items(), key=lambda kv: -kv[1])
    if len(items) < 2:
        return items[0][0]
    return items[0][0] if items[0][1] - items[1][1] > delta else "TIE"


def pct(null, obs):
    return sum(1 for v in null if v >= obs - 1e-12) / len(null)


def summ(null):
    s = sorted(null)
    return dict(mean=sum(s) / len(s), p50=s[len(s) // 2], p95=s[int(0.95 * len(s))], p99=s[int(0.99 * len(s))])


def info_block(worlds, labels, rng, tag):
    """worlds: list of dicts with family/gen/level; labels: winner labels.  Returns MI table + permutation nulls."""
    fam = [w["family"] for w in worlds]
    gen = [w["gen"] for w in worlds]
    lev = [w["level"] for w in worlds]
    obs = dict(n=len(labels), H_winner=H(labels), I_family=MI(labels, fam), I_generator=MI(labels, gen),
               I_level=MI(labels, lev), I_fam_given_gen=CMI(labels, fam, gen), I_gen_given_fam=CMI(labels, gen, fam))
    obs["I_fam_minus_I_gen"] = obs["I_family"] - obs["I_generator"]
    # null 1: winner labels shuffled across worlds (chance MI given finite n and category counts)
    n1 = defaultdict(list)
    lab = list(labels)
    for _ in range(NPERM):
        rng.shuffle(lab)
        n1["I_family"].append(MI(lab, fam))
        n1["I_generator"].append(MI(lab, gen))
        n1["I_fam_minus_I_gen"].append(n1["I_family"][-1] - n1["I_generator"][-1])
    # null 2: family shuffled within generator blocks -> I(W;F|G);  null 3: generator shuffled within family blocks
    def block_perm(vals, blocks):
        idx = defaultdict(list)
        for i, b in enumerate(blocks):
            idx[b].append(i)
        out = list(vals)
        for b, ii in idx.items():
            v = [vals[i] for i in ii]
            rng.shuffle(v)
            for i, x in zip(ii, v):
                out[i] = x
        return out
    n2, n3 = [], []
    for _ in range(NPERM):
        n2.append(CMI(labels, block_perm(fam, gen), gen))
        n3.append(CMI(labels, block_perm(gen, fam), fam))
    nulls = {k: summ(v) for k, v in n1.items()}
    nulls["I_fam_given_gen"] = summ(n2)
    nulls["I_gen_given_fam"] = summ(n3)
    pvals = {k: pct(v, obs[k]) for k, v in n1.items()}
    pvals["I_fam_given_gen"] = pct(n2, obs["I_fam_given_gen"])
    pvals["I_gen_given_fam"] = pct(n3, obs["I_gen_given_fam"])
    excess = {k: obs[k] - nulls[k]["mean"] for k in nulls}
    # world bootstrap of I(W;F) - I(W;G): is "family > generator" itself stable?  (NBOOT resamples)
    bs = []
    n = len(labels)
    for _ in range(NBOOT):
        ii = [rng.randrange(n) for _ in range(n)]
        lb, fb, gb = [labels[i] for i in ii], [fam[i] for i in ii], [gen[i] for i in ii]
        bs.append(MI(lb, fb) - MI(lb, gb))
    bs.sort()
    boot = dict(lo05=bs[int(0.05 * NBOOT)], hi95=bs[int(0.95 * NBOOT) - 1], frac_le0=sum(1 for v in bs if v <= 0) / NBOOT)
    return dict(tag=tag, observed=obs, null=nulls, p_perm=pvals, excess_over_null_mean=excess,
                boot_I_fam_minus_I_gen_90ci=boot, H_family=H(fam), H_generator=H(gen),
                label_counts=dict(Counter(labels)))


def gen_table(worlds, labels):
    t = defaultdict(Counter)
    for w, l in zip(worlds, labels):
        t[w["gen"]][l] += 1
    return {g: dict(c) for g, c in sorted(t.items())}


def pairwise_selective(worlds, per_class, delta, rng, tag):
    """(b) on pairwise-generator worlds: S wins beyond delta; null = per-world permutation of AC across arm labels."""
    idx = [i for i, w in enumerate(worlds) if w["gen"] == "pairwise"]
    arms_all = [per_class[i] for i in idx]   # list of {arm_label: AC}
    def s_wins(arm_maps, d):
        k = 0
        for am in arm_maps:
            best = defaultdict(lambda: -1e9)
            for a, v in am.items():
                best[a[0]] = max(best[a[0]], v)
            if winner(dict(best), d) == "S":
                k += 1
        return k
    obs = {str(d): s_wins(arms_all, d) for d in (0.0,) + (DELTA,) + SENS}
    null = []
    for _ in range(NPERM):
        perm = []
        for am in arms_all:
            labs, vals = list(am.keys()), list(am.values())
            rng.shuffle(vals)
            perm.append(dict(zip(labs, vals)))
        null.append(s_wins(perm, DELTA))
    s_frac = sum(sum(1 for a in am if a[0] == "S") / len(am) for am in arms_all) / max(1, len(arms_all))
    # program-rule per stratum: S minus best non-S, paired per world
    strata = defaultdict(list)
    for i in idx:
        am = per_class[i]
        s = max(v for a, v in am.items() if a[0] == "S")
        o = max(v for a, v in am.items() if a[0] != "S")
        w = worlds[i]
        strata[f'{w["family"]}|{w["level"]}'].append(s - o)
    sv = {k: verdict(v) for k, v in sorted(strata.items())}
    return dict(tag=tag, n_pairwise_worlds=len(idx), S_wins_by_delta=obs, null_S_wins_at_0p30=summ(null),
                p_perm_at_0p30=pct(null, obs[str(DELTA)]), chance_share_S_arms=s_frac,
                per_stratum_S_minus_bestother=sv,
                per_stratum_verdict_counts=dict(Counter(v["verdict"] for v in sv.values())))


def main():
    rng = random.Random(SEED)
    out = dict(delta=DELTA, sens=SENS, nperm=NPERM, rng_seed=SEED)

    # ---------------- selection_v2 (26 arms, raw) ----------------
    sel = json.load(open(os.path.join(DEV, "selection_v2.json")))
    rows = [r for r in sel["rows"] if r["status"] == "OK"]
    assert all(r["seed"] < CAMPAIGN_FLOOR for r in sel["rows"]), "non-dev seed found"
    out["seed_check"] = dict(selection_v2=[min(r["seed"] for r in sel["rows"]), max(r["seed"] for r in sel["rows"])])
    frozen = json.load(open(os.path.join(ROOT, "ensorain", "lm01", "FROZEN_SELECTION.json")))["choices"]
    sel_arms = []
    for r in rows:
        sel_arms.append({a: v for a, v in r["AC"].items() if v is not None})

    def classbest(am):
        b = defaultdict(lambda: -1e9)
        for a, v in am.items():
            b[a[0]] = max(b[a[0]], v)
        return dict(b)

    res = {}
    # A0: reproduce delegate (raw max, 26 arms)
    lab0 = [winner(classbest(am), 0.0) for am in sel_arms]
    res["sel_raw_d0"] = info_block(rows, lab0, rng, "selection_v2, 26 arms, raw max (delegate reproduction)")
    res["sel_raw_d0"]["gen_x_class"] = gen_table(rows, lab0)
    # A1: 26 arms, margin 0.30 (TIE label kept) and decisive-only
    for d in (DELTA,) + SENS:
        lab = [winner(classbest(am), d) for am in sel_arms]
        res[f"sel_raw_d{d}"] = info_block(rows, lab, rng, f"selection_v2, 26 arms, win only beyond {d} (TIE kept)")
        res[f"sel_raw_d{d}"]["gen_x_class"] = gen_table(rows, lab)
    lab = [winner(classbest(am), DELTA) for am in sel_arms]
    keep = [i for i, l in enumerate(lab) if l != "TIE"]
    res["sel_raw_d0.3_decisive"] = info_block([rows[i] for i in keep], [lab[i] for i in keep], rng,
                                              "selection_v2, 26 arms, decisive (>0.30) worlds only")
    # A2: balanced: one frozen arm per class (S,L,H,R) -- in-sample (frozen chosen on these rows)
    bal_arms = []
    for r in rows:
        ch = frozen[f'{r["family"]}|{r["level"]}|{r["gen"]}']
        bal_arms.append({ch[c]: r["AC"][ch[c]] for c in CLS.values() if r["AC"].get(ch[c]) is not None})
    for d in (0.0, DELTA):
        lab = [winner(classbest(am), d) for am in bal_arms]
        res[f"sel_bal_d{d}"] = info_block(rows, lab, rng, f"selection_v2, 1 frozen arm/class (IN-SAMPLE), delta {d}")
        res[f"sel_bal_d{d}"]["gen_x_class"] = gen_table(rows, lab)

    # ---------------- margins v1 (held-out seeds, 1 frozen arm per class) ----------------
    mrows, marms, evict = [], [], []
    for f in sorted(glob.glob(os.path.join(DEV, "margins", "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            assert r["seed"] < CAMPAIGN_FLOOR
            if r.get("status") != "OK":
                continue
            lad = r.get("ladder") or {}
            if r.get("arms"):
                am = {v["label"]: v["AC_a"] for v in r["arms"].values() if v.get("AC_a") is not None}
                pol = [k.split("|")[0] for k in lad if k.split("|")[0] in ("keep_worst", "residual_reservoir")]
                if pol and f"{pol[0]}|c/2" in lad:
                    am["R-" + pol[0]] = lad[f"{pol[0]}|c/2"]["AC"]
                mrows.append(r)
                marms.append(am)
            # eviction: matched-B pairs, only rungs where eviction actually happens (B < full store)
            nfull = lad.get("random|full", {}).get("B")
            for k, v in lad.items():
                p, rung = k.split("|")
                if p in ("keep_worst", "residual_reservoir") and rung != "full" and f"random|{rung}" in lad:
                    if nfull is not None and v["B"] >= nfull:
                        continue
                    evict.append(dict(family=r["family"], level=r["level"], gen=r["gen"], seed=r["seed"],
                                      policy=p, rung=rung, d=v["AC"] - lad[f"random|{rung}"]["AC"]))
    out["seed_check"]["margins_v1"] = [min(r["seed"] for r in mrows), max(r["seed"] for r in mrows)]
    for d in (0.0, DELTA):
        lab = [winner(classbest(am), d) for am in marms]
        res[f"mar_bal_d{d}"] = info_block(mrows, lab, rng, f"margins v1 held-out seeds, 1 frozen arm/class, delta {d}")
        res[f"mar_bal_d{d}"]["gen_x_class"] = gen_table(mrows, lab)
    out["a_information"] = res

    # ---------------- (b) pairwise: selective wins ----------------
    out["b_pairwise"] = dict(
        sel_26arms=pairwise_selective(rows, sel_arms, DELTA, rng, "selection_v2 26 arms (8 S of 26)"),
        sel_balanced=pairwise_selective(rows, bal_arms, DELTA, rng, "selection_v2 frozen 1/class (in-sample)"),
        margins_balanced=pairwise_selective(mrows, marms, DELTA, rng, "margins v1 frozen 1/class (held-out)"))

    # ---------------- (c) eviction: declared vs random at matched B, matched world ----------------
    ev = {}
    by_rung = defaultdict(list)
    for e in evict:
        by_rung[e["rung"]].append(e)
    for rung, es in sorted(by_rung.items()):
        ds = [e["d"] for e in es]
        obs_mean = sum(ds) / len(ds)
        lose = sum(1 for x in ds if x < -DELTA)
        win = sum(1 for x in ds if x > DELTA)
        nm, nl = [], []
        for _ in range(NPERM):   # sign-flip null (random/declared labels exchangeable within world)
            f = [x if rng.random() < 0.5 else -x for x in ds]
            nm.append(sum(f) / len(f))
            nl.append(sum(1 for x in f if x < -DELTA))
        strata = defaultdict(list)
        for e in es:
            strata[f'{e["family"]}|{e["level"]}|{e["gen"]}|{e["policy"]}'].append(e["d"])
        sv = {k: verdict(v) for k, v in strata.items()}
        ev[rung] = dict(n_worlds=len(ds), mean_declared_minus_random=obs_mean,
                        median=sorted(ds)[len(ds) // 2],
                        declared_loses_beyond_0p30=lose, declared_wins_beyond_0p30=win,
                        within_margin=len(ds) - lose - win,
                        null_mean_abs_p=sum(1 for v in nm if abs(v) >= abs(obs_mean)) / NPERM,
                        null_lose_count=summ(nl), p_lose_count=pct(nl, lose),
                        per_stratum_verdicts=dict(Counter(v["verdict"] for v in sv.values())),
                        by_policy={p: dict(n=len([e for e in es if e["policy"] == p]),
                                           mean=sum(e["d"] for e in es if e["policy"] == p) /
                                           max(1, len([e for e in es if e["policy"] == p])))
                                   for p in ("keep_worst", "residual_reservoir")})
    fx = json.load(open(os.path.join(DEV, "fixture_reservoir.json")))["positive_control"]["median_AC"]
    out["c_eviction"] = dict(matched_world_matched_B=ev, fixture_positive_control_medians=fx,
                             fixture_keep_worst_minus_random=fx["keep_worst"] - fx["random"],
                             fixture_residual_minus_random=fx["residual_reservoir"] - fx["random"])
    p = os.path.join(HERE, "probe_out.json")
    with open(p, "w") as f:
        json.dump(out, f, indent=1)
    print("wrote", p)


if __name__ == "__main__":
    main()
