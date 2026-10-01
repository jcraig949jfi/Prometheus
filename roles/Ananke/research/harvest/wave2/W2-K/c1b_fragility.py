"""W2-K Q1/Q2: C1b verdict and battery-reading fragility under pct (recorded), t and BOOTT, from the pair arrays
saved by reeval_c1b.py / c1_integration.py (every array reproduced the recorded pct triple exactly), plus
APPROXIMATE rows for readings whose arrays cannot be regenerated cheaply (fresh-search M3 champions were never
saved; regenerating one costs a full 96x36 search on CPU, ~20 min).

SE = sd(pair values, ddof 1) / sqrt(P) (exact rows) or (hi99 - lo99) / (2 * 2.5758) from the recorded pct CI
(approx rows; SE of a paired difference approximated as r * sqrt(se_a^2 + se_b^2) with r measured on the
specimens' exact arrays). Distance d = how far the deciding statistic sits beyond the cut ON THE RECORDED SIDE,
in SE units (negative = the reading would be on the other side). keep = Phi(d / sqrt 2) (predictive replication
probability, inference.keep_prob).
Output: out/c1b_fragility.json and a printed table.
"""
import json
import math
import os
import pathlib
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[5]
sys.path.insert(0, str(REPO))
import numpy as np  # noqa: E402

from prometheus.ananke import assays, inference  # noqa: E402
from prometheus.ananke import c1b  # noqa: E402

Q = 2.5758
TQ = 2.7440  # t_{.995, 31}
OUT = HERE / "out"
SUMM = json.loads((REPO / "roles/Ananke/pte/c1b/C1B_SUMMARY.json").read_text())
L = lambda tag: np.load(OUT / f"pairs_{tag}.npz")


def three(x):
    x = np.asarray(x, float)
    m, lo, hi = assays.pair_ci(x)
    _, tlo, thi = inference.pair_ci_t(x)
    _, blo, bhi = inference.pair_ci_student(x)
    se = x.std(ddof=1) / math.sqrt(len(x))
    return {"m": float(m), "pct": [float(lo), float(hi)], "t": [float(tlo), float(thi)],
            "boott": [float(blo), float(bhi)], "se": float(se)}


ROWS = []


def row(cell, reading, stat, side, cut, s, recorded, note="", exact=True, consequence=""):
    """side: which bound decides ('lo','hi','m'); op: reading TRUE iff bound >= cut ('ge') / <= / > / <.
    `recorded` = the reading's recorded truth value; d is measured toward keeping it."""
    op = stat
    b = {"pct": s["pct"], "t": s["t"], "boott": s["boott"]}
    idx = {"lo": 0, "hi": 1}

    def val(meth):
        if side == "m":
            return s["m"]
        return b[meth][idx[side]]

    def truth(v):
        return {"ge": v >= cut, "le": v <= cut, "gt": v > cut, "lt": v < cut}[op]
    vals = {k: val(k) for k in ("pct", "t", "boott")}
    tv = {k: bool(truth(v)) for k, v in vals.items()}
    se = s["se"]
    raw = (vals["pct"] - cut) if op in ("ge", "gt") else (cut - vals["pct"])   # >0 iff TRUE
    d = (raw / se if se > 0 else (math.inf if raw > 0 else (-math.inf if raw < 0 else 0.0)))
    if not recorded:
        d = -d
    keep = float(inference.keep_prob(d)) if math.isfinite(d) else (1.0 if d > 0 else 0.0)
    r = {"cell": cell, "reading": reading, "rule": f"{side} {op} {cut}", "m": round(s["m"], 4),
         "pct": round(vals["pct"], 4), "t": round(vals["t"], 4), "boott": round(vals["boott"], 4),
         "se": round(se, 4), "recorded": recorded, "pct_truth": tv["pct"], "t_truth": tv["t"],
         "boott_truth": tv["boott"], "flips_t": tv["t"] != recorded,
         "flips_boott": None if math.isnan(vals["boott"]) else tv["boott"] != recorded,
         "d_se": round(d, 2) if math.isfinite(d) else d, "keep": round(keep, 3), "exact": exact,
         "note": note, "consequence": consequence}
    assert tv["pct"] == recorded or not exact, r
    ROWS.append(r)
    return r


def approx(m, lo, hi):
    se = (hi - lo) / (2 * Q)
    return {"m": m, "pct": [lo, hi], "t": [m - TQ * se, m + TQ * se], "boott": [float("nan")] * 2, "se": se}


# ---------------------------------------------------------------- M2 specimen (exact)
a = L("m2spec")
n, n1 = a["normal"], a["normal_from1"]
C = "M2 4ab2ba01"
row(C, "A flush_inflight kills", "le", "hi", c1b.KILL_HI, three(a["flush_inflight"]), True)
row(C, "Z iti-flush intact (NE)", "ge", "lo", c1b.INTACT_LO, three(a["flush_inflight_iti"] - n1), True,
    note="Z is NOT_ELIGIBLE (A1/A3) -> _UNRESOLVED regardless")
row(C, "B reset_all_nonpacket intact", "ge", "lo", c1b.INTACT_LO, three(a["reset_all_nonpacket"] - n), False,
    consequence="B true -> IN_FLIGHT_UNDECODED_UNRESOLVED instead of IN_FLIGHT_PLUS_JOINT_UNRESOLVED")
row(C, "K_w reset_w drops (point)", "le", "m", -c1b.DROP_PT, three(a["reset_w"] - n), False,
    consequence="K_w true -> MIXED:in_flight,w")
row(C, "K_w reset_w drops (lo clause)", "lt", "lo", c1b.DROP_LO, three(a["reset_w"] - n), True,
    note="second clause of drops(); already true")
row(C, "I reset_inbox drops (point)", "le", "m", -c1b.DROP_PT, three(a["reset_inbox"] - n), False)
row(C, "C census sign predicts (lo>.60)", "gt", "lo", c1b.PRED_LO, three(a["census_C"]), False,
    note="component 0 only (CORRECTIONS K1: wrong component)")
# ---------------------------------------------------------------- M3 specimens (exact for 3 arms)
diff_ratio = []
for tag, cell in (("m3_0a23", "0a23398f20cc41a2"), ("m3_f6b6", "f6b623cdb23afd2c")):
    a = L(tag)
    n = a["normal"]
    C = "M3 " + cell[:8]
    row(C, "T: c1 window intact (lo>=.62)", "ge", "lo", c1b.C1_INTACT_LO, three(a["drop_window_c1"]), True,
        note="T_c1_window NOT_ELIGIBLE -> label carries _UNRESOLVED",
        consequence="T false -> RULE_SWITCH_ONLY (no suffix); C1b-P1 lost for this cell")
    row(C, "X: c1 window kills", "le", "hi", c1b.KILL_HI, three(a["drop_window_c1"]), False)
    row(C, "R: freeze_rule drops (point)", "le", "m", -c1b.DROP_PT, three(a["freeze_rule"] - n), True,
        consequence="R false -> TRANSPORT_ONLY_UNRESOLVED; C1b-P2 lost for this cell")
    row(C, "R: freeze_rule drops (lo<-.05)", "lt", "lo", c1b.DROP_LO, three(a["freeze_rule"] - n), True)
    se_n = n.std(ddof=1) / math.sqrt(len(n))
    se_f = a["freeze_rule"].std(ddof=1) / math.sqrt(len(n))
    se_d = (a["freeze_rule"] - n).std(ddof=1) / math.sqrt(len(n))
    diff_ratio.append(se_d / math.hypot(se_n, se_f))
    # readout-tick / corrected-window kills: marginal, from the recorded CI (far from the cut)
    arms = SUMM["specimens"][cell]["arms"]
    for k in ("drop_readout_tick_only", "drop_window_corrected"):
        m_, lo_, hi_ = arms[k]
        row(C, f"T: {k} kills", "le", "hi", c1b.KILL_HI, approx(m_, lo_, hi_), True, exact=False)
R_DIFF = float(np.mean(diff_ratio))
# ---------------------------------------------------------------- A3 eligibility readings at M2 physics (exact)
a = L("elig_m2")
row("M2 elig F_sham_positive", "A3 fired: hi99(iti - normal_from1) < -.10", "lt", "hi", c1b.FIRED_HI,
    three(a["sham_iti"] - a["sham_n1"]), False,
    consequence="fired -> Z eligible -> M2 label loses _UNRESOLVED (IN_FLIGHT_PLUS_JOINT); fresh k1 -> DELAY_LINE_SPECIMEN")
row("M2 elig F_sham_positive", "A3 competent: lo99(normal) > .55", "gt", "lo", c1b.COMPETENT_LO,
    three(a["sham_n1"]), True)
row("M2 elig F_echo (gates nothing)", "A3 fired: hi99(flush - normal) < -.10", "lt", "hi", c1b.FIRED_HI,
    three(a["echo_flush"] - a["echo_n"]), False)
# ---------------------------------------------------------------- S3 recheck 613162a3 (exact)
a = L("s3_6131")
n = a["normal"]
row("D 613162a3 (S3 recheck)", "C1 window packet drop >= .10 (C1 CAUSAL rule, point)", "le", "m", -0.10,
    three(a["drop_window_c1"] - n), True,
    note="independent worlds (0xC1B0) vs C1 adjudication; C1 reading was .143 at 1.65 SE (W2-H F10)")
row("D 613162a3 (S3 recheck)", "corrected window drop >= .10 (point)", "le", "m", -0.10,
    three(a["drop_window_corrected"] - n), True)
# ---------------------------------------------------------------- C1 INTEGRATION (exact)
a = L("c1_4781")
row("C1 4781b0a1 (MAJ, wave C)", "INTEGRATION held lo99 > .70", "gt", "lo", 0.70, three(a["held"]), True,
    consequence="the only INTEGRATION_BEYOND_ONE_SENSOR call in C1 (1/174 MAJ rows)")
row("C1 4781b0a1 on C1b worlds", "same statistic, independent worlds, lo99 > .70", "gt", "lo", 0.70,
    three(a["c1b_normal"]), True, note="replicate draw (S3 recheck normal arm)")
# ---------------------------------------------------------------- fresh searches (APPROX: arrays not saved)
for f in SUMM["fresh"]:
    h = f["held"]
    cell = f"fresh {f['replicates'][:8]} k{f['k']}"
    row(cell, "S2 SIGNAL gate held lo99 > .55", "gt", "lo", 0.55, approx(h["acc"], h["lo99"], h["hi99"]),
        bool(f["signal"]), exact=False,
        note="search held pairs not saved; champion not saved (M3) -> t approx, BOOTT not computable")
    if f["mechanism"] == "M3" and f.get("arms"):
        A = f["arms"]
        row(cell, "T: c1 window intact (lo>=.62)", "ge", "lo", c1b.C1_INTACT_LO, approx(*A["drop_window_c1"]),
            f["booleans"]["T"], exact=False,
            consequence="T true would give TRANSPORT+... (k1: the specimen's own label -> M3_REPRODUCED)")
        row(cell, "X: c1 window kills", "le", "hi", c1b.KILL_HI, approx(*A["drop_window_c1"]),
            f["booleans"]["X"], exact=False)
        mn, ln, hn = A["normal"]
        mf, lf, hf = A["freeze_rule"]
        sen, sef = (hn - ln) / (2 * Q), (hf - lf) / (2 * Q)
        sed = R_DIFF * math.hypot(sen, sef)
        dm = mf - mn
        s = {"m": dm, "pct": [dm - Q * sed, dm + Q * sed], "t": [dm - TQ * sed, dm + TQ * sed],
             "boott": [float("nan")] * 2, "se": sed}
        rec_R = bool(dm <= -0.10 and dm - Q * sed < -0.05)
        row(cell, "R: freeze_rule drops (point)", "le", "m", -c1b.DROP_PT, s, f["booleans"]["R"] or dm <= -0.10,
            exact=False, note=f"diff SE approx (r={R_DIFF:.2f} from specimens)")
# fresh M2 battery difference readings (EXACT: champions regenerated bit-identically by spikes/s_m2.py)
a = L("m2fresh_b")
for k in (1, 2, 3):
    cell = f"fresh 4ab2ba01 k{k}"
    f = [x for x in SUMM["fresh"] if x["replicates"].startswith("4ab2") and x["k"] == k][0]
    n, n1 = a[f"fresh{k}_normal"], a[f"fresh{k}_normal_from1"]
    row(cell, "Z iti intact", "ge", "lo", c1b.INTACT_LO, three(a[f"fresh{k}_flush_inflight_iti"] - n1), f["booleans"]["Z"])
    row(cell, "B nonpacket intact", "ge", "lo", c1b.INTACT_LO, three(a[f"fresh{k}_reset_all_nonpacket"] - n),
        f["booleans"]["B"], consequence="B false -> k1 IN_FLIGHT_PLUS_JOINT; k2/k3 IN_FLIGHT_PLUS_JOINT")
    row(cell, "K_w drops (point)", "le", "m", -c1b.DROP_PT, three(a[f"fresh{k}_reset_w"] - n), f["booleans"]["K_w"])
    row(cell, "C census (lo>.60)", "gt", "lo", c1b.PRED_LO, three(L("m2fresh")[f"fresh{k}_census_C"]), f["booleans"]["C"])
json.dump({"rows": ROWS, "r_diff": R_DIFF}, open(OUT / "c1b_fragility.json", "w"), indent=1, default=str)
hdr = f"{'cell':28s} {'reading':48s} {'rule':14s} {'m':>7s} {'pct':>7s} {'t':>7s} {'boott':>7s} {'se':>6s} rec  d_se  keep flipT flipB"
print(hdr)
for r in ROWS:
    print(f"{r['cell'][:28]:28s} {r['reading'][:48]:48s} {r['rule']:14s} {r['m']:7.4f} {r['pct']:7.4f} {r['t']:7.4f} "
          f"{r['boott']:7.4f} {r['se']:6.4f} {str(r['recorded'])[0]} {r['d_se']:6} {r['keep']:5.3f} "
          f"{str(r['flips_t'])[0]} {'-' if r['flips_boott'] is None else str(r['flips_boott'])[0]} {'' if r['exact'] else 'APPROX'}")
print("r_diff", R_DIFF)
