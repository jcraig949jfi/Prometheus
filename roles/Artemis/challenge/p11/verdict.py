"""Apply PREREG_P11.md s5 (D1, A0, D2, D3) mechanically to the result files -> results/VERDICT.json."""
from __future__ import annotations

import json
import math

from common import OUT


def load(name):
    return {json.loads(l)["id"]: json.loads(l) for l in open(OUT / name)}


def main():
    P = load("PANEL.jsonl")
    G = json.load(open(OUT / "GATES_PANEL.json"))
    NAT = [json.loads(l) for l in open(OUT / "NATURAL_REAPPLY.jsonl")]
    NS = json.load(open(OUT / "NATURAL_SUMMARY.json"))
    v = {"gates": {"E0_pass": G["E0_pass"], "E1_pass": G["E1_pass"],
                   "G_all_pass": all(g["pass"] for g in G["G"].values()),
                   "excluded": [i for i, g in G["G"].items() if not g["pass"]]}}
    ok = v["gates"]["E0_pass"] and v["gates"]["E1_pass"]
    cert = lambda i: bool(P[i]["P11"]["certify"])

    # ---- D1
    NEG = ["Z1", "Z2", "TV-1", "TV-2"]
    POS_P11 = ["Z3", "Z3b", "TV-3", "TV-6", "TV-6k", "Z6h"]
    negc = [i for i in NEG if cert(i)]
    posc = [i for i in POS_P11 if cert(i)]
    if not ok:
        d1 = "STOP (E0/E1 failed)"
    elif negc and posc:
        d1 = "UNSOUND FOR HEREDITY"
    elif not negc and len(posc) == len(POS_P11):
        d1 = "SOUND FOR HEREDITY (on this panel)"
    else:
        d1 = "MIXED"
    over = [i for i in ("TV-4", "Z5a", "TV-5b", "Z3u96") if not cert(i)]
    v["D1"] = {"verdict": d1, "NEG_certified": negc, "POS_P11_certified": posc,
               "OVER_STRICT": bool(over), "over_strict_rejections": over}

    # ---- A0
    z1c2 = P["Z1"]["P11"]["events"][0]["C2_rate"]
    z3uc2 = P["Z3u96"]["P11"]["events"][0]["C2_rate"]
    v["A0"] = {"Z1_C2_rate": z1c2, "Z3u96_C2_rate": z3uc2,
               "same_cell_and_tier": (P["Z1"]["n"], P["Z1"]["budget"]) == (P["Z3u96"]["n"], P["Z3u96"]["budget"]),
               "Z3u96_copied_prefix": G["G"]["Z3u96"]["checks"].get("_copied_prefix"),
               "verdict": "SUPPORTED" if (z1c2 >= 0.5 and z3uc2 < 0.5) else "NOT SUPPORTED"}

    # ---- D2
    REQ_POS = ["Z3", "Z3b", "Z3u96", "Z3n", "TV-3", "TV-4", "Z5a", "TV-5b", "TV-6", "TV-6k", "Z6h"]
    REQ_NEG = NEG
    acc = {"FERT": lambda r: r["FERT"]["accept"], "LOCAL": lambda r: r["LOCAL"]["accept"],
           "CVT1": lambda r: r["CVT1"]["accept"], "CVT2": lambda r: r["CVT2"]["accept"],
           "CVTR": lambda r: r["CVTR"]["accept"]}
    nat_rec = [r for r in NAT if r["recertified"]]

    def nat_acc(c, r):
        s = [x for x in r["sides"].values() if x["recertified"]]
        if c in ("FERT", "LOCAL"):
            return any(x[c]["accept"] for x in s)
        return any(x[c]["accept"] for x in s)
    d2 = {}
    for c, f in acc.items():
        miss_pos = [i for i in REQ_POS if not f(P[i])]
        miss_neg = [i for i in REQ_NEG if f(P[i])]
        calib = None
        if c.startswith("CVT"):
            TB = lambda i: P[i][c]["TB"]
            calib = {"TV-6": TB("TV-6"), "TV-6k": TB("TV-6k"), "TV-1": TB("TV-1"), "TV-2": TB("TV-2")}
            cal_ok = TB("TV-6") == 1 and TB("TV-6k") == 4 and TB("TV-1") == 0 and TB("TV-2") == 0
        else:
            cal_ok = True
        accepted = [i for i in P if f(P[i])] + [r["run_id"] for r in nat_rec if nat_acc(c, r)]
        d2[c] = {"adequate": not miss_pos and not miss_neg and cal_ok, "rejects_required_pos": miss_pos,
                 "accepts_required_neg": miss_neg, "calibration": calib, "calibration_ok": cal_ok,
                 "acceptance_set_size": len(accepted), "accepts_TV7": f(P["TV-7"]), "accepts_TV8": f(P["TV-8"])}
    gens = {"FERT": 2, "LOCAL": 1, "CVT1": 1, "CVT2": 2, "CVTR": 4}
    adequate = [c for c in d2 if d2[c]["adequate"]]
    if adequate:
        sel = sorted(adequate, key=lambda c: (-d2[c]["acceptance_set_size"], gens[c]))[0]
        note = None
        if d2[sel]["accepts_TV7"] and "CVTR" in adequate and not d2["CVTR"]["accepts_TV7"]:
            if d2["CVTR"]["accepts_TV8"]:
                note = ("%s is the weakest adequate certificate for the required panel; CVT-R is required if "
                        "information-preserving but non-resembling reproduction (TV-7) must count as non-hereditary."
                        % sel)
            else:
                note = "CVT-R rejects TV-8: OVER-STRICT on counters, not recommended."
        v["D2"] = {"selected_weakest_adequate": sel, "adequate": adequate, "stress_note": note, "per_certificate": d2}
    else:
        v["D2"] = {"selected_weakest_adequate": None, "verdict": "NO ADEQUATE CANDIDATE", "per_certificate": d2}

    # ---- D2 sensitivity: pre-repair shared toy ISA, with the AMENDMENT b B1 analytic truth
    try:
        PR = load("PANEL_prerepair.jsonl")
        truth = {"TV-1": 1.0, "TV-2": 0.0, "TV-6": math.log2(3), "TV-6k": math.log2(17)}
        sens = {}
        for c in ("CVT1", "CVT2", "CVTR"):
            got = {i: PR[i][c]["TB"] for i in truth}
            sens[c] = {"TB": got, "matches_corrected_truth": all(abs(got[i] - truth[i]) < 1e-3 for i in truth)}
        v["D2_sensitivity_prerepair_shared_ISA"] = {"corrected_truth_bits": {k: round(x, 4) for k, x in truth.items()},
                                                   "per_certificate": sens}
    except FileNotFoundError:
        pass

    # ---- D3 (selected certificate)
    sel = v["D2"].get("selected_weakest_adequate") or "CVT2"
    key = sel + "_TB"
    byte_ = [r for r in nat_rec if r["copy_primitive"] == "BYTEWISE"]
    block = [r for r in nat_rec if r["copy_primitive"] == "BLOCK"]
    n1 = ("INCONCLUSIVE (%d BYTEWISE recertified < 5)" % len(byte_) if len(byte_) < 5 else
          ("HOLDS" if all(r[key] < 1 for r in byte_) else "DOES NOT HOLD"))
    n2 = "HOLDS" if any(r[key] >= 1 for r in block) else "DOES NOT HOLD"
    hom = [r for r in nat_rec if r["DOM_diag"]["dominant_share"] >= 0.9]
    blk_lo = [r for r in block if r["has_ED_B0_B8"] and r["DOM_diag"]["dominant_share"] < 0.9]
    v["D3"] = {"certificate": sel, "recertified": len(nat_rec), "of": len(NAT),
               "N1_BYTEWISE_construction_without_heredity": n1,
               "N2_BLOCK_heredity_exists": n2,
               "N2_BLOCK_with_TB_ge_1": [r["run_id"] for r in block if r[key] >= 1],
               "N3": NS.get("N3_zero_bit_share_" + ("CVTR" if sel == "CVTR" else "CVT2")),
               "prediction_homopolymers_TB2_zero": {"n": len(hom), "zero": sum(r["CVT2_TB"] < 1 for r in hom)},
               "prediction_BLOCK_EDB0_lowdom_majority_TB2_ge_1": {"n": len(blk_lo),
                                                                 "ge1": sum(r["CVT2_TB"] >= 1 for r in blk_lo)}}
    (OUT / "VERDICT.json").write_text(json.dumps(v, indent=1, sort_keys=True))
    print(json.dumps(v, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
