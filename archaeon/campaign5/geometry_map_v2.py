"""DAMAGE GEOMETRY MAP V2 (campaign 5): built from the attempts of record of C5-03..C5-08 and
C4's DAMAGE_GEOMETRY_MAP.json (unchanged, cited). Writes DAMAGE_GEOMETRY_MAP_V2.{md,json}.

    python -m archaeon.campaign5.geometry_map_v2
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from archaeon.campaign5.c5base import C5                                     # noqa: E402

C4 = REPO / "archaeon" / "campaign4"


def latest(slot: str, marker: str) -> Path:
    ds = sorted(d for d in (C5 / slot / "attempts").iterdir() if (d / marker).exists())
    return ds[-1]


def load(slot: str, marker: str) -> tuple:
    d = latest(slot, marker)
    return d.name, json.loads((d / marker).read_text(encoding="utf-8"))


def main() -> int:
    a03, q = load("C5-03", "QUALIFICATION.json")
    a04, g4 = load("C5-04", "GENREP.json")
    a05, g5 = load("C5-05", "GEOMETRY_B.json")
    a06, r6 = load("C5-06", "RECOVERY.json")
    a07, c7 = load("C5-07", "COST.json")
    a08, m8 = load("C5-08", "MECHANISM.json")
    v1 = json.loads((C4 / "DAMAGE_GEOMETRY_MAP.json").read_text(encoding="utf-8")) if (C4 / "DAMAGE_GEOMETRY_MAP.json").exists() else {}
    bins = ("D2", "D3", "D4", "D5", "D6", "D7", "DT", "DF")
    table = {k: {b: v[b]["rate"] for b in bins} for k, v in g5["by_grammar_interp"].items()}
    by_op = {}
    for k, v in g5["by_grammar_interp_operator"].items():
        gname, interp, op = k.split(" x ")
        by_op.setdefault(op, {})[gname + " x " + interp] = {kk: vv for kk, vv in v.items() if kk not in ("DF_sub",)}
    out = {
        "schema": "archaeon.c5.damage_geometry_map.v2",
        "representation": {"old": "proteus.foundry.vm total interpreter (opcode mod 25, register mod n_regs)",
                           "new": q["representation"], "boundary": "encoding only; addresses/offsets modulo tape; FAIL = whole evaluation; FIZZLE = skip + count"},
        "qualification": {"attempt": a03, "disposition": q["disposition"], "fixtures": q["fixtures_pass"], "F3_tvd_count": q["F3"]["tvd"], "F3_tvd_sites": q["F3"]["tvd_sites"],
                          "F7_raw_answer_old_trap_new": q["F7"]["raw_answer_old_but_trap_new"], "F8_crossing_by_operator": {k: v["rate"] for k, v in q["F8"]["by_operator"].items()}},
        "generator_x_representation": {"attempt": a04, "table": g4["table"], "predictions": g4["predictions"]},
        "single_edit_geometry": {"attempt": a05, "replication_of_C4_01": g5["replication"], "crossing_share": g5["crossing_share"], "bins": table,
                                 "DF_sub": {k: v["DF_sub"] for k, v in g5["by_grammar_interp"].items()}, "thresholds": g5["thresholds"], "by_operator": by_op},
        "local_recovery": {"attempt": a06, "input_n": r6["input_n"], "by_grammar": r6["by_grammar"], "by_operator": r6["by_operator"], "fault_kinds": r6["fault_kinds"],
                           "replication": r6["replication"], "gate": r6["gate_c5_07"], "old_labels_of_recovery": r6["old_labels_of_recovery"], "disposition": r6["disposition"]},
        "cost_of_insulation": {"attempt": a07, "K1": c7["K1"], "K2": c7["K2"], "K3": c7["K3"], "reading": c7["reading"]},
        "robustness_mechanism": {"attempt": a08, "full": m8["full"], "ablated": m8["ablated"], "by_length_bin": m8["by_length_bin"], "tests": m8["tests"], "reading": m8["reading"],
                                 "dead_share_mean": m8["dead_share_mean"]},
        "v1_reference": {"path": "archaeon/campaign4/DAMAGE_GEOMETRY_MAP.json", "present": bool(v1)},
    }
    (C5 / "DAMAGE_GEOMETRY_MAP_V2.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    L = []
    L.append("+=====================================================================+")
    L.append("|  DAMAGE GEOMETRY MAP V2 -- representation B beside the total one     |")
    L.append("|  Archaeon[m2-49ee5a4d]   Campaign 5   built by geometry_map_v2.py    |")
    L.append("+=====================================================================+")
    L.append("")
    L.append("Attempts of record: C5-03 %s, C5-04 %s, C5-05 %s, C5-06 %s, C5-07 %s, C5-08 %s." % (a03, a04, a05, a06, a07, a08))
    L.append("V1 (Campaign 4, total interpreter) is unchanged at archaeon/campaign4/DAMAGE_GEOMETRY_MAP.md.")
    L.append("")
    L.append("1. SINGLE-EDIT BINS (share of applied children; 57 parents x 12 operators x 8 draws)")
    L.append("   grammar   interp      D2     D3     D4     D5     D6     D7     DT     DF")
    for k in ("v04 x OLD", "v04 x B_FAIL", "v04 x B_FIZZLE", "B x OLD", "B x B_FAIL", "B x B_FIZZLE"):
        gname, interp = k.split(" x ")
        L.append("   %-8s  %-9s " % ("v0.4" if gname == "v04" else gname, interp) + " ".join("%6.3f" % table[k][b] for b in bins))
    L.append("   crossing share: v0.4 %.3f, B %.3f.  DF sub-bins v0.4 %s; B %s" % (g5["crossing_share"]["v04"]["share"], g5["crossing_share"]["B"]["share"],
                                                                                    out["single_edit_geometry"]["DF_sub"]["v04 x B_FIZZLE"], out["single_edit_geometry"]["DF_sub"]["B x B_FIZZLE"]))
    L.append("   C4-01 replicated %d/%d (digest and label)." % (g5["replication"]["digest_equal"], g5["replication"]["rows_matched"]))
    L.append("")
    L.append("2. THE BOUNDARY (per grammar): executed-crossing (T1) %s / %s; D5 of non-crossing children under FAIL vs OLD %s / %s" % (
        g5["thresholds"]["v04"]["T1"]["share"], g5["thresholds"]["B"]["T1"]["share"],
        "%.3f vs %.3f" % (g5["thresholds"]["v04"]["T2"]["D5_B_FAIL"], g5["thresholds"]["v04"]["T2"]["D5_OLD"]),
        "%.3f vs %.3f" % (g5["thresholds"]["B"]["T2"]["D5_B_FAIL"], g5["thresholds"]["B"]["T2"]["D5_OLD"])))
    L.append("   D6 (exaptation) v0.4 OLD/FAIL/FIZZLE %s; B %s; D7 = 0 everywhere." % (
        {m: g5["thresholds"]["v04"]["T3"]["D6"][m]["rate"] for m in ("OLD", "B_FAIL", "B_FIZZLE")}, {m: g5["thresholds"]["B"]["T3"]["D6"][m]["rate"] for m in ("OLD", "B_FAIL", "B_FIZZLE")}))
    L.append("")
    L.append("3. MATCHED RECOVERY (C5-06; executed-crossing children of non-degenerate parents, n=%d)" % r6["input_n"])
    for gname in ("v04", "B"):
        L.append("   %-5s %s" % (gname, r6["by_grammar"][gname]))
    L.append("   fault kinds %s; replicated RECOVERY %d, INSULATION_LOSS %d; disposition %s" % (r6["fault_kinds"], r6["replication"]["recovery"]["replicated"],
                                                                                              r6["replication"]["insulation_loss"]["replicated"], r6["disposition"]))
    L.append("")
    L.append("4. COST OF INSULATION (C5-07): K1 median ops ratio %s (> 1.10x: %s); K2 second-edit neutral children %s vs parents %s (diff %s); K3 lost elsewhere %s; %s" % (
        c7["K1"]["median_ratio"], c7["K1"]["share_gt_1_10"], c7["K2"]["children_neutral"], c7["K2"]["parents_neutral_weighted"], c7["K2"]["diff"], c7["K3"]["share"], c7["reading"]))
    L.append("")
    L.append("5. ROBUSTNESS MECHANISM (C5-08): R_old full %.3f -> ablated %.3f (dead share %.3f); GAP %.3f / %.3f; tests %s; %s" % (
        m8["full"]["R_old"], m8["ablated"]["R_old"], m8["dead_share_mean"], m8["full"]["GAP"], m8["ablated"]["GAP"], m8["tests"], m8["reading"]))
    L.append("   by length bin (R_old full/ablated): " + "; ".join("%s %.3f/%.3f" % (lb, m8["by_length_bin"]["full/" + lb]["R_old"], m8["by_length_bin"]["ablated/" + lb]["R_old"])
                                                              for lb in ("1-8", "9-16", "17-32", "33+") if "full/" + lb in m8["by_length_bin"]))
    L.append("")
    L.append("6. GENERATOR x REPRESENTATION (C5-04, viable share): " + "; ".join("%s %.3f" % (k, v["viable"]) for k, v in g4["table"].items()) + "; predictions %s" % g4["predictions"])
    L.append("")
    L.append("7. QUALIFICATION (C5-03 %s): %s; fixtures %s; count-TVD %s; site-TVD %s; grammar-B crossing by operator %s" % (
        a03, q["disposition"], q["fixtures_pass"], q["F3"]["tvd"], q["F3"]["tvd_sites"], {k: v["rate"] for k, v in q["F8"]["by_operator"].items() if v["crossed"]}))
    L.append("")
    L.append("8. PER-OPERATOR BINS (counts; grammar x interpreter)")
    for op, d in by_op.items():
        L.append("   " + op)
        for k, v in d.items():
            L.append("      %-16s n %4d crossing %4d  %s" % (k, v["n"], v["crossing"], {b: v[b] for b in bins if b in v}))
    (C5 / "DAMAGE_GEOMETRY_MAP_V2.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(L[:40]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
