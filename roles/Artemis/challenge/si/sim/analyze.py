"""Mechanical readings for SI Phase 2: fixtures (S0), S1-S5, as amended (AMENDMENTS_P2.md).
usage: python3 analyze.py OUTDIR  -> OUTDIR/readings.json + printed summary
"""
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np

import sources as src

REV = ("RG", "RU", "RULMT", "RQ", "RMIN", "RH", "RX")


def fib(n):
    a, b = 1, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return a


def med(xs):
    return float(np.median(xs))


def machine_for(row):
    if row["fam"] == "F1":
        return src.rp(row["q"])
    if row["fam"] == "F2":
        return src.golden_mean() if row["source"] == "GM" else src.even()
    return src.random_machine(row["k"], row["X"], src.seed_for("F3gen", "k%dX%d" % (row["k"], row["X"]), row["j"]))


def rprime(m, W, cache):
    key = (m.name, W)
    if key in cache:
        return cache[key]
    if W is None:
        cache[key] = (0.0, "exact")
        return cache[key]
    v, how = src.r_prime_exact(m, W)
    if v is None:
        xs, S = m.sample(20000, src.seed_for("MC", m.name, W))
        Dend = m.sync_depth_end(xs)
        ev = 0
        for t in range(2, len(xs)):
            if m.merges(int(S[t]), int(xs[t])) and int(Dend[t - 1]) > W - 1:
                ev += 1
        v, how = ev / (len(xs) - 2), "mc"
    cache[key] = (v, how)
    return cache[key]


def main():
    out = sys.argv[1]
    rows = json.load(open(os.path.join(out, "rows.json")))
    f4 = json.load(open(os.path.join(out, "f4.json")))
    budget = json.load(open(os.path.join(out, "budget.json")))
    for r in rows:
        r["Wn"] = None if r["W"] == "inf" else int(r["W"])
        r["capn"] = None if r["cap"] == "inf" else int(r["cap"])
    machines = {}
    for r in rows:
        if r["source"] not in machines:
            machines[r["source"]] = machine_for(r)
    q = {n: m.quantities() for n, m in machines.items()}
    merging = {n: (not m.co_unifilar()) for n, m in machines.items()}
    R = {}
    cpath = os.path.join(out, "rprime_cache.json")
    cache = {}
    if os.path.exists(cpath):
        for k, v in json.load(open(cpath)).items():
            n, W = k.rsplit("|", 1)
            cache[(n, None if W == "None" else int(W))] = tuple(v)

    def sel(**kw):
        out_ = []
        for r in rows:
            ok = True
            for k, v in kw.items():
                if r.get(k) != v:
                    ok = False
                    break
            if ok:
                out_.append(r)
        return out_

    # ---------------- S0 fixtures ----------------
    fx = {}
    bad = [(r["source"], r["kind"], r["W"], r["cap"]) for r in rows if r["kind"] in REV and not (r["cert"] and r["erase_total"] == 0)]
    badI = [(r["source"], r["W"]) for r in rows if r["kind"] == "I" and (r["Wn"] == 0 or merging[r["source"]])
            and not (r["erase_total"] > 0 and not r["cert"])]
    I_cou = [r["erase_total"] for r in rows if r["kind"] == "I" and r["Wn"] != 0 and not merging[r["source"]]]
    fx["FX1"] = dict(pass_=(not bad and not badI), reversible_runs=sum(1 for r in rows if r["kind"] in REV),
                     reversible_fail=bad[:10], I_runs_checked=sum(1 for r in rows if r["kind"] == "I" and (r["Wn"] == 0 or merging[r["source"]])),
                     I_fail=badI[:10], I_counifilar_W_ge1_erase_max=(max(I_cou) if I_cou else None))
    Ibad = [(r["source"], r["W"]) for r in rows if r["kind"] == "I" and not (r["exact"] and r["D"] == 0.0)]
    se_fail = []
    fx2 = {}
    by_src = defaultdict(dict)
    for r in rows:
        by_src[r["source"]][(r["fam"], r["seed_i"])] = r["oracle_batches"]
    for s, d in by_src.items():
        b = np.concatenate([np.array(v) for v in d.values()])
        mean = float(b.mean())
        se = float(b.std(ddof=1) / math.sqrt(len(b)))
        h = q[s]["h"]
        ok = abs(mean - h) <= 3 * se
        fx2[s] = dict(mean=mean, h=h, se=se, z=(mean - h) / se if se > 0 else None, ok=ok)
        if not ok:
            se_fail.append(s)
    fx["FX2"] = dict(pass_=(not Ibad and not se_fail), I_not_exact=Ibad[:10], loss_vs_h_fail=se_fail,
                     n_sources=len(fx2), max_abs_z=max(abs(v["z"]) for v in fx2.values() if v["z"] is not None))
    f3 = sel(fam="F1", kind="RG", W=1, cap=8)
    f3 = [r for r in f3 if abs(r["q"] - 0.1) < 1e-12]
    ov = [r["overflow_t"] for r in f3 if r["overflow_t"] is not None]
    da = [r["D_after_overflow"] for r in f3 if r["D_after_overflow"] is not None]
    fx["FX3"] = dict(pass_=(len(ov) == len(f3) and 40 <= med(ov) <= 160 and med(da) > 0.05),
                     overflow_t_median=(med(ov) if ov else None), overflow_t_all=ov,
                     D_after_overflow_median=(med(da) if da else None), band=[40, 160])
    f4r = [r for r in rows if r["kind"] == "RMIN" and r["Wn"] == 1 and (r["source"].startswith("RP(q=0,") or r["source"] == "EVEN")]
    # A11: "constant M_agent" = persistent end-of-step width constant (= the state register) and the
    # within-step peak = state + the transient input register (v1 wrongly required peak == end).
    fx["FX4"] = dict(pass_=(len(f4r) > 0 and all(r["erase_total"] == 0 and r["exact"] and abs(r["slope"]) < 1e-9
                                                 and r["M_end"] == machines[r["source"]].w
                                                 and r["M_peak"] == machines[r["source"]].w + machines[r["source"]].wx for r in f4r)),
                     n=len(f4r), sources=sorted(set(r["source"] for r in f4r)))
    ih = [r for r in rows if r["kind"] == "IH"]
    ihs = defaultdict(list)
    for r in ih:
        ihs[r["source"]].append(r["D"])
    fx5_fail = [s for s, v in ihs.items() if q[s]["C"] > 0.1 and not (min(v) > 0)]
    fx["FX5"] = dict(pass_=(len(ihs) > 0 and not fx5_fail), n_sources=len(ihs), fail=fx5_fail,
                     D_min=min(min(v) for v in ihs.values()), D_median=med([med(v) for v in ihs.values()]))
    S0 = all(v["pass_"] for v in fx.values())
    R["S0"] = dict(pass_=S0, fixtures=fx, fx2_detail=fx2)

    # ---------------- helpers ----------------
    def cell_rows(source, kind, Wn, capn=None):
        return [r for r in rows if r["source"] == source and r["kind"] == kind and r["Wn"] == Wn and r["capn"] == capn and r["fam"] != "LMT"]

    def succeed_unbounded(rs):
        return len(rs) > 0 and all(r["exact"] for r in rs) and med([r["slope"] for r in rs]) <= 1e-3 and all(r["stack_end"] == 0 for r in rs)

    def succeed_cap(rs, cap):
        return len(rs) > 0 and all(r["exact"] for r in rs) and all(r["stack_end"] <= cap for r in rs)

    sources_main = sorted(set(r["source"] for r in rows if r["fam"] in ("F1", "F2", "F3")))

    # ---------------- S1 ----------------
    s1i = []
    for s in sources_main:
        I = cell_rows(s, "I", None)
        if not I:
            continue
        kindL = "RMIN" if not merging[s] and cell_rows(s, "RMIN", None) else "RU"
        L = cell_rows(s, kindL, None)
        cI, lI = med([r["C_mean"] for r in I]), med([r["LAT_mean"] for r in I])
        cL, lL = med([r["C_mean"] for r in L]), med([r["LAT_mean"] for r in L])
        ok = succeed_unbounded(L) and cL <= 4 * cI and lL <= lI + 2
        RG = cell_rows(s, "RG", None)
        RQ = cell_rows(s, "RQ", None)
        s1i.append(dict(source=s, learner=kindL, match=succeed_unbounded(L), C_ratio=cL / cI, LAT_I=lI, LAT_L=lL,
                        M_peak_L=med([r["M_peak"] for r in L]), M_peak_I=med([r["M_peak"] for r in I]),
                        replay_reads_step=med([r["reads_step"] for r in L]), erase_I=med([r["erase_step"] for r in I]),
                        pass_=ok, RG_match=succeed_unbounded(RG), RG_C_ratio=med([r["C_mean"] for r in RG]) / cI if RG else None,
                        RQ_match=succeed_unbounded(RQ), RQ_LAT_mean=med([r["LAT_mean"] for r in RQ]) if RQ else None,
                        RQ_LAT_max=max(r["LAT_max"] for r in RQ) if RQ else None))
    s1ii = []
    for s in sources_main:
        if merging[s]:
            continue
        for Wn in sorted(set(r["Wn"] for r in rows if r["source"] == s and r["kind"] == "RMIN"), key=lambda w: 10 ** 9 if w is None else w):
            L = cell_rows(s, "RMIN", Wn)
            I = cell_rows(s, "I", Wn)
            ok = (succeed_unbounded(L) and all(r["erase_total"] == 0 for r in L)
                  and med([r["M_peak"] for r in L]) <= med([r["M_peak"] for r in I])
                  and med([r["C_mean"] for r in L]) <= med([r["C_mean"] for r in I])
                  and med([r["LAT_mean"] for r in L]) <= med([r["LAT_mean"] for r in I]))
            s1ii.append(dict(source=s, W=("inf" if Wn is None else Wn), pass_=ok,
                             C_L=med([r["C_mean"] for r in L]), C_I=med([r["C_mean"] for r in I]),
                             M_L=med([r["M_peak"] for r in L]), M_I=med([r["M_peak"] for r in I]),
                             erase_I=med([r["erase_step"] for r in I])))
    s1iii = []
    for Wn in (1, 2, None):
        found = []
        for kind in ("RG", "RU", "RQ"):
            L = cell_rows("GM", kind, Wn)
            if succeed_unbounded(L):
                found.append(kind)
        s1iii.append(dict(source="GM", W=("inf" if Wn is None else Wn), pass_=bool(found), matching=found))
    s1_fail_i = [c["source"] for c in s1i if not c["pass_"]]
    s1_pass = (not s1_fail_i) and all(c["pass_"] for c in s1ii) and all(c["pass_"] for c in s1iii)
    R["S1"] = dict(i=s1i, ii=s1ii, iii=s1iii, fail_i=s1_fail_i, pass_=s1_pass,
                   ii_pass=all(c["pass_"] for c in s1ii), iii_pass=all(c["pass_"] for c in s1iii))

    # ---------------- S2 ----------------
    s2i = []
    for s in sources_main:
        if not s.startswith("RP(") or s.startswith("RP(q=0,"):
            continue
        m = machines[s]
        rp1, _ = rprime(m, 1, cache)
        I = cell_rows(s, "I", 1)
        T = I[0]["T"]
        for cap in (8, 64):
            elig = rp1 * T >= 1.5 * cap / m.w
            succ = []
            for kind, capk in (("RG", cap), ("RU", None), ("RQ", None)):
                L = cell_rows(s, kind, 1, capk)
                if succeed_cap(L, cap):
                    succ.append(kind)
            gap = (not succ) and all(r["exact"] for r in I)
            s2i.append(dict(source=s, cap=cap, eligible=elig, expected_events=rp1 * T, rev_gap=gap, reversible_succeeding=succ,
                            reading=("REV_GAP" if gap else ("FINITE_LIFETIME_ESCAPE" if not elig else "NO_GAP"))))
    s2i_pass = all(c["rev_gap"] for c in s2i if c["eligible"])
    slope_cells = []
    for s in sources_main:
        if not merging[s]:
            continue
        m = machines[s]
        Ws = sorted(set(r["Wn"] for r in rows if r["source"] == s and r["kind"] == "RG" and r["capn"] is None and r["Wn"] not in (None, 0)))
        for Wn in Ws:
            L = cell_rows(s, "RG", Wn, None)
            rpw, how = rprime(m, Wn, cache)
            T = L[0]["T"]
            pred = rpw * m.w
            obs = med([r["slope"] for r in L])
            elig = rpw * T / 2 >= 10
            ratio = obs / pred if pred > 0 else (None if obs == 0 else float("inf"))
            passed = (ratio is not None and 0.5 <= ratio <= 1.5) if pred > 0 else (abs(obs) < 1e-6)
            slope_cells.append(dict(source=s, W=Wn, rprime=rpw, how=how, pred_slope=pred, obs_slope=obs, ratio=ratio,
                                    eligible=elig, pass_=passed))
    el = [c for c in slope_cells if c["eligible"]]
    frac_el = sum(c["pass_"] for c in el) / len(el) if el else None
    frac_all = sum(c["pass_"] for c in slope_cells) / len(slope_cells) if slope_cells else None
    s2ii_pass = frac_el is not None and frac_el >= 0.8
    # F4
    f4r = {}
    for c in f4:
        f4r[(c["W"], c["d"])] = c
    w1 = []
    for (W, d), c in sorted(f4r.items()):
        if W != 1:
            continue
        fb = fib(d)
        if c["status"] == "FOUND":
            st = "CONTRADICTED" if c["n_min"] < fb else "VERIFIED"
        elif c["status"] == "NOT_FOUND":
            st = "VERIFIED" if c["last_excluded_n"] >= fb - 1 else "CONSISTENT"
        else:
            st = "VERIFIED" if c.get("last_excluded_n", 0) >= fb - 1 else "CONSISTENT"
        w1.append(dict(d=d, fib=fb, status=c["status"], last_excluded=c.get("last_excluded_n"), n_min=c.get("n_min"), reading=st, cpu_s=c["cpu_s"]))
    c1 = {}
    for W in (2, 3):
        cs = [f4r[(W, d)] for d in (8, 10) if (W, d) in f4r]
        if any(c["status"] == "CAPPED" for c in cs):
            c1[W] = "U_CAPPED"
        elif all(c["status"] == "FOUND" for c in cs) and len(set(c["n_min"] for c in cs)) == 1:
            c1[W] = "C1_FALSIFIED"
        elif all(c["status"] == "FOUND" for c in cs):
            ns = [c["n_min"] for c in cs]
            c1[W] = "C1_HOLDS_GROWING" if ns[-1] > ns[0] else "C1_FALSIFIED"
        else:
            c1[W] = "C1_HOLDS_NOT_FOUND"
    R["S2"] = dict(i=s2i, i_pass=s2i_pass, slope_cells=slope_cells, slope_frac_eligible=frac_el,
                   slope_frac_all_original_rule=frac_all, n_eligible=len(el), ii_pass=s2ii_pass,
                   f4_W1=w1, f4_C1=c1, f4_raw=f4)
    contradicted = any(x["reading"] == "CONTRADICTED" for x in w1)
    # ---------------- verdicts ----------------
    if not S0:
        broad = narrow = "INSTRUMENT_FAILURE"
    else:
        broad = "K" if s1_pass else ("N_for:" + ",".join(s1_fail_i) if s1_fail_i and R["S1"]["ii_pass"] and R["S1"]["iii_pass"] else "NOT_K")
        if contradicted:
            narrow = "STOP_CONTRADICTED"
        elif any(v == "U_CAPPED" for v in c1.values()) or not s2ii_pass:
            narrow = "U"
        elif any(v == "C1_FALSIFIED" for v in c1.values()):
            fals = sorted(W for W, v in c1.items() if v == "C1_FALSIFIED")
            narrow = "N*-narrowed(C1 falsified at W=%s)" % fals if s2i_pass else "NOT_ESTABLISHED"
        elif s2i_pass and s2ii_pass:
            narrow = "N*"
        else:
            narrow = "NOT_ESTABLISHED"
    R["verdict"] = dict(claim_broad=broad, claim_narrow=narrow)
    # ---------------- S4 (B3) ----------------
    flips = []
    for c in s1i:
        if c["match"]:
            flips.append(dict(source=c["source"], W="inf", B1B2="REV_MATCH", B3="REV_GAP (retained past grows t*log2|X|)"))
    for c in s1ii:
        if c["W"] == "inf" and c["pass_"]:
            flips.append(dict(source=c["source"], W="inf", B1B2="REV_MATCH", B3="REV_GAP"))
    R["S4"] = dict(flips=flips, n_flips=len(flips),
                   note="finite-W cells: M_env = W*log2|X| is constant, so no finite-W reading flips")
    # ---------------- extra numbers ----------------
    lmt = [r for r in rows if r["kind"] == "RULMT" and r.get("lmt_n")]
    bylmt = defaultdict(list)
    for r in lmt:
        bylmt[r["k"]].append((r["lmt_ops_mean"], r["lmt_ratio_mean"], r["lmt_D_mean"]))
    R["LMT"] = {k: dict(ops_per_recompute=med([a for a, _, _ in v]), ratio_to_D_S2=med([b for _, b, _ in v]),
                        D_mean=med([c for _, _, c in v]), n=len(v)) for k, v in sorted(bylmt.items())}
    luc = [r for r in rows if r["fam"] == "LMT" and r["kind"] in ("RULMT", "RU", "I")]
    R["LMT_cert"] = all(r["cert"] for r in luc if r["kind"] != "I")
    R["LMT_exact"] = all(r["exact"] for r in luc if r["kind"] in ("RULMT", "RU") and r["stack_end"] == 0)
    R["W0"] = {}
    for s in sources_main:
        if not s.startswith("RP("):
            continue
        d = {}
        for kind, k in (("I", None), ("RH", None), ("RX", None), ("RQ", None), ("IH", None), ("IW", 2), ("IW", 8), ("IW", 32)):
            rs = [r for r in rows if r["source"] == s and r["kind"] == kind and r["Wn"] == 0 and r["k"] == k]
            if rs:
                d[kind + ("" if k is None else str(k))] = dict(D=med([r["D"] for r in rs]), M_end=med([r["M_end"] for r in rs]),
                                                             M_export=med([r["M_export"] for r in rs]), erase_step=med([r["erase_step"] for r in rs]),
                                                             C=med([r["C_mean"] for r in rs]), LAT=med([r["LAT_mean"] for r in rs]))
        R["W0"][s] = d
    json.dump({"%s|%s" % k: v for k, v in cache.items()}, open(cpath, "w"))
    R["quantities"] = q
    R["budget"] = budget
    with open(os.path.join(out, "readings.json"), "w") as f:
        json.dump(R, f, indent=1, default=str)
    print(json.dumps(dict(verdict=R["verdict"], S0={k: v["pass_"] for k, v in fx.items()},
                          S1_fail_i=s1_fail_i, S1_ii=R["S1"]["ii_pass"], S1_iii=R["S1"]["iii_pass"],
                          S2_i=s2i_pass, slope_el=frac_el, slope_all=frac_all, n_el=len(el), C1=c1, W1=w1,
                          flips=len(flips)), indent=1, default=str))


if __name__ == "__main__":
    main()
