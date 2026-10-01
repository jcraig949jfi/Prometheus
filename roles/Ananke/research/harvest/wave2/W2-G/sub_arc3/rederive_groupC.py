"""W2-G sub_arc3 group C: independent re-derivation of W-L, W-K, designed_echoes and
joint_carrier claims from raw saved JSON outputs. Parses JSON only; imports no worker code.
Run from the worktree root:  python roles/Ananke/research/harvest/wave2/W2-G/sub_arc3/rederive_groupC.py
CPU only, no simulation; reads files and counts.
"""
import os, json, itertools, glob
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
os.environ.setdefault("OMP_NUM_THREADS", "2")

R = "roles/Ananke/research"
WL = f"{R}/workers/W-L/out"
WK = f"{R}/workers/W-K/out"
DE = f"{R}/designed_echoes"
JC = f"{R}/joint_carrier"


def J(p):
    with open(p) as f:
        return json.load(f)


def hr(t):
    print("\n==== " + t)


# ---------------------------------------------------------------- W-L
hr("W-L searches (held-out 0x5F3), criterion recomputed: lo99 > .60 AND diff_lo99 > 0")
runs = {}
for p in sorted(glob.glob(f"{WL}/search_n*_s*.json")):
    s = J(p)
    h = s["held_5F3"]
    a = h["lo99"] > 0.60
    b = (h.get("diff_lo99") is not None) and h["diff_lo99"] > 0
    runs[s["tag"]] = dict(n=s["n"], seed=s["seed"], pop=s["spec"]["pop"], gens=s["spec"]["gens"],
                          acc=h["acc"], lo99=h["lo99"], base=h.get("baseline"), dlo=h.get("diff_lo99"),
                          zc=h["zero_comm"], crit_a=a, crit_ab=a and b, flag=h["SUCCESS"])
for t, r in runs.items():
    print(t, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
rewarded = [t for t, r in runs.items() if r["n"] in (1, 2)]
succ = [t for t in rewarded if runs[t]["crit_ab"]]
print("rewarded searches:", len(rewarded), "pass (a)&(b):", len(succ), succ)
print("flag agreement with recomputed criterion:", all(runs[t]["flag"] == runs[t]["crit_ab"] for t in runs))
for n in (1, 2):
    tt = [t for t in rewarded if runs[t]["n"] == n]
    print(f"n={n}: {sum(runs[t]['crit_ab'] for t in tt)}/{len(tt)}")
ctrl = [t for t in runs if runs[t]["n"] == 0]
print("n=0 control: crit (a) only:", {t: runs[t]["crit_a"] for t in ctrl})
print("local (|zero_comm-acc|) in successes:", {t: round(abs(runs[t]["zc"] - runs[t]["acc"]), 4) for t in succ})

hr("W-L lag profile (post hoc, 256 worlds, no CI)")
lp = J(f"{WL}/lagprofile.json")
sel = {}
for t, v in lp.items():
    lags = v["lags"] if "lags" in v else v
    lags = {int(k): x for k, x in lags.items()}
    rng = max(lags.values()) - min(lags.values())
    n = runs[t]["n"] if t in runs else None
    s_n = None
    if n in (1, 2):
        s_n = lags[n] - max(x for k, x in lags.items() if k != n)
    sel[t] = (round(rng, 3), None if s_n is None else round(s_n, 3))
    print(t, lags, "range", round(rng, 3), "selectivity(lag n - max other)", sel[t][1])
n2_selective = [t for t in runs if runs[t]["n"] == 2 and sel[t][1] is not None and sel[t][1] > 0]
print("n=2 runs with positive lag-2 selectivity:", len(n2_selective), "/", sum(runs[t]["n"] == 2 for t in runs))
n1_selective = [t for t in runs if runs[t]["n"] == 1 and sel[t][1] is not None and sel[t][1] > 0.05]
print("n=1 runs with lag-1 selectivity > .05:", n1_selective)
flat = [t for t in ctrl if sel[t][0] < 0.04 and min(lp[t]["lags"].values()) > 0.6]
print("n=0 control runs with flat above-chance (integrator) profile:", flat, "of", ctrl)

hr("W-L plants (checks.json) and carrier swaps (carriers_champs.json, 64-world design)")
ck = J(f"{WL}/checks.json")
for p in ck["plants"]:
    if p["plant"] in ("P1S", "P1K", "P2S"):
        print(p["plant"], "n", p["n"], "lines", p["lines"], "acc", p["acc"], "lo99", p["lo99"], p["ns"])
print("physics prog_len:", ck["physics"].get("prog_len"))
cc = J(f"{WL}/carriers_champs.json")
for t, v in cc.items():
    b = v["back0"]
    nrm = b["normal"][0]
    print(t, "normal", round(nrm, 3), "S", round(b["S"]["acc"][0], 3), b["S"]["verdict"],
          "S<=1-normal", b["S"]["acc"][0] <= 1 - nrm,
          "others NO-EFFECT", all(b[a]["verdict"] == "NO-EFFECT" for a in ("Kp", "w", "inbox", "channel_all", "pay0", "pay1")))

# ---------------------------------------------------------------- W-K
hr("W-K fixture x check matrix")
m = J(f"{WK}/matrix.json")
fixtures = list(m)
checks = sorted({c for f in m.values() for c in f["checks"]})
broken = [f for f in fixtures if m[f]["truth"] == "BROKEN"]
valid = [f for f in fixtures if m[f]["truth"] == "VALID"]
print("fixtures", len(fixtures), "broken", len(broken), "valid", len(valid), "checks", len(checks), checks)
twins = [f for f in valid if m[f].get("twin")]
print("valid with twin field:", len(twins), "valid w/o twin:", [f for f in valid if not m[f].get("twin")])
score = {}
for c in checks:
    caught = [f for f in broken if m[f]["checks"][c]["status"] == "FLAG"]
    fa = [f for f in valid if m[f]["checks"][c]["status"] == "FLAG"]
    err = [f for f in fixtures if m[f]["checks"][c]["status"] == "ERROR"]
    jj = len(caught) / len(broken) - len(fa) / len(valid)
    score[c] = (len(caught), len(fa), round(jj, 2), err)
for c, v in sorted(score.items(), key=lambda kv: -kv[1][2]):
    print(c, f"caught {v[0]}/{len(broken)} FA {v[1]}/{len(valid)} J {v[2]} errors {v[3]}")
zfa = [c for c in checks if score[c][1] == 0]
covers = []
for k in range(1, 5):
    for S in itertools.combinations(zfa, k):
        if all(any(m[f]["checks"][c]["status"] == "FLAG" for c in S) for f in broken):
            covers.append(S)
    if covers:
        break
print("min zero-FA covers (size", len(covers[0]) if covers else None, "):", covers)
sc = J(f"{WK}/scores.json")
print("scores.json K2 J:", sc["scores"]["K2"]["J"], "n_broken", sc["n_broken"], "n_valid", sc["n_valid"])
print("readings:", {f: m[f]["reading"]["reading"] for f in fixtures})
print("normal >= .99 all:", all(m[f]["reading"]["normal"][0] >= 0.99 for f in fixtures))

# ---------------------------------------------------------------- designed echoes
hr("designed_echoes: MAE(model, engine) per design; >=.65 interval; E4 gap-8 hi99")
pr = J(f"{DE}/predictions.json")
en = J(f"{DE}/engine.json")


def interval(d):
    g = sorted(int(k) for k in d if not k.startswith("_"))
    ok = [x for x in g if d[str(x)] >= 0.65]
    return (min(ok), max(ok)) if ok else None


fits = 0
maes = {}
for name in pr:
    p = pr[name]
    e = {k: v[0] for k, v in en[name].items()}
    gaps = sorted(int(k) for k in p if not k.startswith("_") and k in e)
    mae = sum(abs(p[str(g)] - e[str(g)]) for g in gaps) / len(gaps)
    ip, ie = interval(p), interval(e)
    holds = ip is not None and ie is not None and abs(ip[0] - ie[0]) <= 1 and abs(ip[1] - ie[1]) <= 1
    fit = mae <= 0.07
    fits += fit and holds
    maes[name] = mae
    print(f"{name:22s} gaps {gaps[0]}-{gaps[-1]} n={len(gaps)} MAE {mae:.4f} FIT {fit} interval pred {ip} engine {ie} HOLDS {holds}")
print("designs FIT&INTERVAL-HOLDS:", fits, "/", len(pr), "MAE range", round(min(maes.values()), 3), "-", round(max(maes.values()), 3))
e4 = [k for k in en if k.startswith("E4")][0]
print("E4 gap 8:", en[e4]["8"], "hi99<=.60:", en[e4]["8"][2] <= 0.60)

hr("designed_echoes instruments: three committed predictions (PLAN.md lines 29-39)")
ins = J(f"{DE}/instruments.json")
e1 = ins["E1_canon"]["swaps_by_lag_before_readout"]
e2 = ins["E2_pipe2"]["swaps_by_lag_before_readout"]
p_e1 = any(e1.get(l, {}).get("channel_all") == "FLIP" for l in ("-6", "-4")) and e1["-6"]["site_all"] != "FLIP"
p_e2a = any(e2.get(l, {}).get("site_all") == "FLIP" and e2[l]["channel_all"] == "NO-EFFECT" for l in ("-1", "-2"))
p_e2b = any(e2.get(l, {}).get("channel_all") == "FLIP" or e2.get(l, {}).get("pay1") == "FLIP" for l in ("-6", "-4"))


def meanlag(d):
    tot = sum(d.values())
    return sum(int(k) * v for k, v in d.items()) / tot


m1 = meanlag(ins["E1_canon"]["cue_arrival_lags"])
m2 = meanlag(ins["E2_pipe2"]["cue_arrival_lags"])
p_arr = m2 < m1
print("E1 held:", p_e1, "| E2 site-part held:", p_e2a, "transit-part held:", p_e2b, "-> E2 held:", p_e2a and p_e2b)
print(f"arrival mean lag E1 {m1:.2f} E2 {m2:.2f} shift {m1 - m2:.2f} -> earlier held: {p_arr}")
print("instrument predictions held:", int(p_e1) + int(p_e2a and p_e2b) + int(p_arr), "/ 3")

# ---------------------------------------------------------------- joint carrier
hr("joint_carrier 4781b0a1")
jp = J(f"{JC}/out_j_probe.json")
j5 = J(f"{JC}/out_j5.json")
print("normal j_probe", jp["normal"], "normal j5", j5["normal"])
print("J5a erase S at actuator/sensors/others:", {k: v[0] for k, v in j5["J5a"].items()})
print("J3 pay0 decoder:", jp["J3 decoders t0+8"]["pay0"], "| swap pay0 t0+8:", jp["swap t0+8 pay0"][1],
      "| swap pay1 t0+8:", round(jp["swap t0+8 pay1"][0][0], 3), jp["swap t0+8 pay1"][1])
print("mid (t0+8) single swaps:", {a: (round(jp[f"swap t0+8 {a}"][0][0], 3), jp[f"swap t0+8 {a}"][1]) for a in ("S", "site", "channel", "pay1", "joint")})
print("flush at t0+8:", jp["erase t0+8 flush"][0], "J4 joint swap t0-1:", jp["J4 joint swap t0-1"])
eS = {int(k): v["erase_S"][0] for k, v in j5["J5b"].items()}
fl = {int(k): v["flush"][0] for k, v in j5["J5b"].items()}
print("erase_S by tick:", {k: round(v, 3) for k, v in sorted(eS.items())})
print("flush by tick  :", {k: round(v, 3) for k, v in sorted(fl.items())})
kill_S = [k for k, v in sorted(eS.items()) if v <= 0.5 + 1e-9]
print("erase_S exactly kills (0.50) at ticks:", kill_S, "(report says 'kills through t0+9'; t0+9 =", round(eS[9], 3), ")")
