"""W2-G sub_arc3 group A: independent re-derivation of W-A, W-B, W-C, W-E, W-F,
SYNTHESIS_2026-09-27 and ARC2 numeric claims from raw saved outputs.

Run from the worktree root:
    python roles/Ananke/research/harvest/wave2/W2-G/sub_arc3/rederive_groupA.py

Read-only. Parses worker JSON/CSV directly; imports no worker code; runs no
simulation. Writes groupA_values.json and (via make_rows_groupA.py) rows_groupA.csv here.
"""
import csv
import glob
import json
import os
import re
import statistics
import subprocess

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
os.environ.setdefault("OMP_NUM_THREADS", "2")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../../../../../.."))
RES = os.path.join(ROOT, "roles/Ananke/research")
W = os.path.join(RES, "workers")
OUT = {}


def J(*p):
    with open(os.path.join(*p)) as f:
        return json.load(f)


def say(k, v):
    OUT[k] = v
    print(f"{k}: {v}")


# ---------------------------------------------------------------- W-A
GAPS = list(range(2, 17))
THR = 0.65


def interval(c):
    ok = [g for g in GAPS if c[g] >= THR]
    return (min(ok), max(ok)) if ok else None


def iv_ok(a, b):
    if a is None or b is None:
        return a is None and b is None
    return abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1


eng = J(W, "W-A/out/engine.json")
pred = J(W, "W-A/out/predictions.json")
eng = {k: v for k, v in eng.items() if not k.startswith("_")}
meas = {k: {g: v[str(g)][0] for g in GAPS} for k, v in eng.items()}
tests = [k for k in meas if not k.startswith("base:")]
fit = {}
for mode in ("sat", "nosat"):
    res = []
    for k in tests:
        p = {g: pred[k][mode][str(g)] for g in GAPS}
        mae = statistics.mean(abs(meas[k][g] - p[g]) for g in GAPS)
        res.append((k, mae, mae <= 0.07 and iv_ok(interval(meas[k]), interval(p))))
    fit[mode] = res
    say(f"WA_{mode}_pass", f"{sum(r[2] for r in res)}/{len(res)}")
    say(f"WA_{mode}_MAE_median_max", (round(statistics.median(r[1] for r in res), 4), round(max(r[1] for r in res), 4)))
# curves among the 46 that are bit-identical to a base (seen) curve
ident = [k for k in tests for b in ("4ab2ba01", "fresh1", "fresh2", "fresh3")
         if all(eng[k][str(g)] == eng[f"base:{b}"][str(g)] for g in GAPS)]
say("WA_tests_identical_to_a_base_curve", ident)
canon = [k for k in tests if k.startswith("canon")]
say("WA_canonical_genome_curves_in_46", canon)
# base-curve null (non-canon tests)
ntests = [k for k in tests if not k.startswith("canon")]
good = 0
for k in ntests:
    b = meas["base:" + k.split(":")[1]]
    mae = statistics.mean(abs(b[g] - meas[k][g]) for g in GAPS)
    good += mae <= 0.07 and iv_ok(interval(meas[k]), interval(b))
say("WA_null_pass", f"{good}/{len(ntests)}")
g78 = {c: (round(meas[f"base:{c}"][7], 3), round(meas[f"base:{c}"][8], 3))
       for c in ("4ab2ba01", "fresh1", "fresh2", "fresh3")}
say("WA_gap7_vs_gap8", g78)
say("WA_gap7_gt_gap8_count", sum(a > b for a, b in g78.values()))
# "at chance at gap >= 12" (spikes S-M2b raw + W-A base curves)
m2b = J(RES, "spikes/out/s_m2b.json")
at12 = {c: [round(x, 3) for x in m2b[c]["12"]] for c in m2b if not c.startswith("_")}
say("S_M2b_gap12_acc_lo99_hi99", at12)
say("S_M2b_gap12_lo99_above_0.5", sum(v[1] > 0.5 for v in at12.values()))
say("S_M2b_gap16_lo99_above_0.5", sum(m2b[c]["16"][1] > 0.5 for c in m2b if not c.startswith("_")))
lo12 = {c: round(eng[f"base:{c}"]["12"][1], 3) for c in ("4ab2ba01", "fresh1", "fresh2", "fresh3")}
say("WA_base_gap12_lo99", lo12)

# ---------------------------------------------------------------- W-B
cen = J(W, "W-B/out/census.json")
cls = {}
for v in cen.values():
    cls[v["class"]] = cls.get(v["class"], 0) + 1
say("WB_census_n", len(cen))
say("WB_classes", cls)
boot = sum(n for c, n in cls.items() if c.startswith(("UNIFORM_BOOT", "PATTERN_BOOT")))
ong = sum(n for c, n in cls.items() if c.startswith("ONGOING"))
say("WB_boot_share", f"{boot}/{len(cen)} = {boot/len(cen):.3f}")
say("WB_ongoing_share", f"{ong}/{len(cen)} = {ong/len(cen):.3f}")
dd = J(W, "W-B/out/deepdive_all.json")
rv = {}
for v in dd.values():
    rv[v["Y1_r"]["verdict"]] = rv.get(v["Y1_r"]["verdict"], 0) + 1
say("WB_r_swap_n_cells", len(dd))
say("WB_r_swap_verdicts", rv)
say("WB_pin_readout_HURTS", f"{sum(v['Y4a_pin_readout_after_settle'].get('v') == 'HURTS' for v in dd.values())}/{len(dd)}")
exact0 = sum(v["Y4b_pin_others_after_settle"]["d"][0] == 0.0 for v in dd.values())
near0 = sum(abs(v["Y4b_pin_others_after_settle"]["d"][0]) < 0.005 for v in dd.values())
say("WB_pin_others_exact0_near0", f"exact {exact0}/{len(dd)}, |d|<.005 {near0}/{len(dd)}")
m3 = J(W, "W-B/out/m3.json")
say("WB_rules1_vs_r0frozen_bit_identical", {k: v["X7_rules1_vs_r0frozen_bit_identical"] for k, v in m3.items()})
say("WB_rules1_vs_normal", {k: (v["X7_rules1_vs_normal"]["v"], round(v["X7_rules1_vs_normal"]["d"][0], 4)) for k, v in m3.items()})

# ---------------------------------------------------------------- W-C
x12 = J(W, "W-C/out/x12.json")
fire = {k: v["x1"]["fire_share"] for k, v in x12.items()}
say("WC_n_specimens", len(x12))
say("WC_fire_share_gt_0.5", sorted(k for k, s in fire.items() if s > 0.5))
say("WC_fire_share_ge_0.49", sorted(k for k, s in fire.items() if s >= 0.49))
cnt_ident = sorted(k for k, v in x12.items() if v["x2"]["pairs_mcnt_differ"] < 0.05)
say("WC_counts_swap_near_identity(<5% pairs differ)", cnt_ident)
x4 = {}
for f in sorted(glob.glob(os.path.join(W, "W-C/out/x4_A?_?.json"))):
    d = J(f)
    x4[os.path.basename(f)[3:-5]] = (round(d["held"]["acc"], 3), round(d["held"]["lo99"], 3),
                                     round(d["held"]["comm_delta"], 3), d["x1"]["fire_share"],
                                     d["sitestate"]["verdict"], d["inflight"]["verdict"], d["counts"]["verdict"])
say("WC_X4(held,lo99,comm_delta,fire_share,site,inflight,counts)", x4)
for arm in ("A0", "A1"):
    say(f"WC_X4_{arm}_comm_delta_gt0", f"{sum(v[2] > 0 for k, v in x4.items() if k.startswith(arm))}/3")
    say(f"WC_X4_{arm}_fire_share_defined", f"{sum(v[3] is not None for k, v in x4.items() if k.startswith(arm))}/3")

# ---------------------------------------------------------------- W-E
champs = sorted(glob.glob(os.path.join(W, "W-E/out/D_*.json")) + glob.glob(os.path.join(W, "W-E/out/M2_*.json")))
champs = [c for c in champs if "fresh" not in os.path.basename(c) or True]
ps = {}
for f in champs:
    d = J(f)
    for j in range(7):
        ps[(d["name"], j)] = d["decoder_single"][str(j)]["p"]


def holm(pv):
    items = sorted(pv.items(), key=lambda kv: kv[1])
    m, run, adj = len(items), 0.0, {}
    for i, (k, p) in enumerate(items):
        run = max(run, min(1.0, (m - i) * p))
        adj[k] = run
    return adj


say("WE_n_champions", len({k[0] for k in ps}))
say("WE_family_size", len(ps))
ha = holm(ps)
mn = min(((v, k) for k, v in ha.items() if k[1] >= 2))
say("WE_min_holm_single_j>=2", (round(mn[0], 4), mn[1]))
say("WE_j0_decodes", sum(ha[(n, 0)] < 0.01 for n in {k[0] for k in ps}))
wsum = J(W, "W-E/out/summary.json")
lab = {}
for r in wsum["rows"]:
    if r["name"].startswith(("D_", "M2_")):
        lab[r["label"]] = lab.get(r["label"], 0) + 1
say("WE_labels", lab)
hh = J(W, "W-E/out/explore_hist_holm.json") if os.path.exists(os.path.join(W, "W-E/out/explore_hist_holm.json")) else None
if hh is not None:
    say("WE_explore_hist_holm_keys", list(hh)[:5] if isinstance(hh, dict) else type(hh).__name__)

# ---------------------------------------------------------------- W-F
R = list(csv.DictReader(open(os.path.join(W, "W-F/out/census_table.csv"))))
tab = {}
for r in R:
    tab[(r["family"], r["class"])] = tab.get((r["family"], r["class"]), 0) + 1
say("WF_n_cells", len(R))
hold_read = sum(n for (f, c), n in tab.items() if f == "HOLD" and c != "UNREADABLE")
say("WF_HOLD_site_over_readable", f"{tab.get(('HOLD','SITE'),0)}/{hold_read}")
JT = [r for r in R if r["class"] == "JOINT"]
s = [float(r["site_acc"]) + float(r["chan_acc"]) for r in JT]
say("WF_JOINT_n_sum_min_max_mean", (len(JT), min(s), round(max(s), 3), round(statistics.mean(s), 4)))
rows_s = [json.loads(l) for sh in ("s0", "s1") for l in open(os.path.join(W, f"W-F/out/census_{sh}.jsonl"))]
say("WF_jsonl_rows_with_error_field", sum(1 for r in rows_s if any("err" in k.lower() for k in r)))
corr = list(csv.DictReader(open(os.path.join(W, "W-O/out/corrections_WF.csv"))))
F = {r["cell"]: r for r in R}
ch = [c for c in corr if c["basis"] == "rec_normal" and c["class_rec"] != c["class_new"]]
moves = {}
for c in ch:
    k = (F[c["cell"]]["family"], c["class_rec"], c["class_new"])
    moves[k] = moves.get(k, 0) + 1
say("WO_corrections_WF_rec_normal_mid_moves", {"/".join(k): v for k, v in moves.items()})
j_after = len(JT) - sum(v for (f, a, b), v in moves.items() if a == "JOINT") + sum(v for (f, a, b), v in moves.items() if b == "JOINT")
say("WF_JOINT_count_after_WO", j_after)
say("WF_HOLD_site_after_WO", tab.get(("HOLD", "SITE"), 0) + sum(v for (f, a, b), v in moves.items() if f == "HOLD" and b == "SITE" and a != "UNREADABLE"))

# ---------------------------------------------------------------- SYNTHESIS_2026-09-27
sf = J(RES, "spikes/out/s_f.json")
cov = {k: round(v["c1_window_share"], 3) for k, v in sf.items() if not k.startswith("_")}
say("S_F_c1_window_coverage", cov)
oth = [v for k, v in cov.items() if not k.startswith("M3")]
say("S_F_coverage_M3_and_others_range", ([cov[k] for k in cov if k.startswith("M3")], min(oth), max(oth)))
sm2 = J(RES, "spikes/out/s_m2.json")
dec = {k: max(v["decoders"]["pay0"]["acc"], v["decoders"]["pay1"]["acc"]) for k, v in sm2.items() if not k.startswith("_")}
say("S_M2_code_component_decoder", dec)
log = open(os.path.join(RES, "SPIKES_2026-09-27_LOG.md")).read().splitlines()
held = [l.strip()[:50] for l in log if re.search(r"\bHELD\b", l) and re.search(r"pred", l)]
lost = [l.strip()[:50] for l in log if re.search(r"\bLOST\b", l) and re.search(r"pred", l)]
say("SPIKES_pred_lines_HELD", len(held))
say("SPIKES_pred_lines_LOST", len(lost))
pa = open(os.path.join(RES, "PRIOR_ART_temporal_distributed_computation.md")).read()
say("PRIOR_ART_Source_blocks", len(re.findall(r"(?im)^sources?:", pa)))
say("PRIOR_ART_unique_urls_dois", len(set(re.findall(r"https?://[^\s)>,;]+|doi:[^\s,;)]+", pa))))

# ---------------------------------------------------------------- ARC2 s1 instruments
try:
    t = subprocess.run(["git", "-C", ROOT, "show", "a4e414392:prometheus/ananke/tests/test_lens_instruments.py"],
                       capture_output=True, text=True, check=True).stdout
    say("lens_tests_at_a4e414392(before ARC2 8eabc990b)", t.count("def test_"))
except Exception as e:  # noqa: BLE001
    say("lens_tests_at_a4e414392", f"NOT_VERIFIED ({e})")

with open(os.path.join(HERE, "groupA_values.json"), "w") as f:
    json.dump({k: (v if isinstance(v, (int, float, str, list, dict, bool)) or v is None else str(v)) for k, v in OUT.items()},
              f, indent=1, default=str)
print("wrote groupA_values.json")

# emit the CSV rows (judgement text lives in make_rows_groupA.py; values come from groupA_values.json)
import runpy  # noqa: E402
runpy.run_path(os.path.join(HERE, "make_rows_groupA.py"), run_name="__main__")
