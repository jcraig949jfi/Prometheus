"""Assemble APHRODITE_AMENDMENT16_CAMPAIGN_REPORT_2026-09-24.md from the
stage artifacts that exist. Never combines effects across experiments."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "pivot" / "APHRODITE_AMENDMENT16_CAMPAIGN_REPORT_2026-09-24.md"


def rd(n):
    p = HERE / n
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def exp_block(tag, r):
    if r is None:
        return ["  %s: NOT RUN (time envelope or precondition)" % tag, ""]
    L = ["  %s_BOUNDED_RSI = %s" % (tag, r.get("BOUNDED_RSI"))]
    if "reason" in r:
        L.append("    reason: %s" % r["reason"])
    if "R1" in r:
        R = r["R1"]
        L += ["    R1: altered-experience replicates %s; G1 NEW replicates %s; P NEW replicates %s"
              % (R["altered_replicates"], R["G1_new_replicates"], R["P_new_replicates"]),
              "        discordant G1-only %d / P-only %d; sign-test p = %.4f; R1 PASS = %s"
              % (R["discordant_G1_only"], R["discordant_P_only"], R["sign_test_p"], R["PASS"])]
    if "failure_link" in r:
        L.append("    failed link: %s" % r["failure_link"])
    if "conditions" in r:
        L.append("    conditions: %s" % r["conditions"])
        p = r["pooled_L2_vs_L1"]
        L.append("    L2 vs L1 pooled paired saving %.0f (lower95 %.0f, n=%d cells); L2 FP fraction %s"
                 % (p["mean_paired_saving"], p["lower95_one_sided"], p["n_cells"], r["L2_fp_fraction"]))
        L.append("    L2 schemas %s sha %s" % (r["L2"]["schemas"], r["L2"]["sha256"][:12]))
        for f, v in r["per_family_criterion"].items():
            L.append("      %-22s L2 %2d/16  L1 %2d/16  saving %9.0f lb %9.0f  attributed %d/%d  beats-all-shams %s"
                     % (f, v["L2_q"], v["L1_q"], v["paired_L2_vs_L1"]["mean_paired_saving"],
                        v["paired_L2_vs_L1"]["lower95_one_sided"], v["attributed"], v["qualified"],
                        v["beats_every_sham"]))
    if "shams" in r:
        L.append("    shams: %s" % [s["schema"] for s in r["shams"]])
    L.append("")
    return L


def donor_lines(cat):
    d = rd("A16_%s_DONORS_2026-09-24.json" % cat)
    if not d:
        return []
    L = ["    donor traces (observed classes -> candidate schemas [NEW?] -> selected):"]
    for x in sorted(d, key=lambda x: (x["replicate"], x["donor"])):
        t = x["trace"]
        L.append("      r%d %-2s classes=%d  cands=%s  sel=%s  NEW=%s  meta=%d"
                 % (x["replicate"], x["donor"], len(t["classes"]),
                    [("%s%s" % (c["schema"], "*" if c["SEMANTICALLY_NEW"] else "")) for c in t["candidate_schemas"]],
                    t["selected"], x["SELECTED_SEMANTICALLY_NEW"], x["meta_charges"]))
    L.append("      (* = SEMANTICALLY_NEW)")
    return L


def main(elapsed, extra):
    cats = rd("A16_CATALOGS_2026-09-24.json")
    e1, e2, e4 = rd("A16_E1_RESULT_2026-09-24.json"), rd("A16_E2_RESULT_2026-09-24.json"), rd("A16_E4_RESULT_2026-09-24.json")
    L = ["+" + "=" * 78 + "+",
         "|  APHRODITE -- AMENDMENT 16 CAMPAIGN REPORT (four-hour recursion campaign)" + " " * 4 + "|",
         "|  Author: Aphrodite (RSI seat), host harry1 / M4.  Date: 2026-09-24" + " " * 11 + "|",
         "|  For: James (HITL) and external reviewers. Self-contained." + " " * 19 + "|",
         "+" + "=" * 78 + "+", "",
         "Prereg: AMENDMENT_16_2026-09-24.md @ 46e477d81 (T0 18:35:51Z). Code a16.py @ 5c74e4c58.",
         "AMENDMENT 15 stands: BRSI = NO, INTERPRETATION = UNTESTABLE_CATALOG (not redrawn).",
         "GLOBAL_BEHAVIOR_IDENTITY = FAIL (permanent). Campaign 1 frozen and unrun. No G3.", "",
         "-" * 78, "0. DISPOSITIONS", "-" * 78]
    for c in ("A", "B"):
        if cats and c in cats:
            L.append("  CATALOG_%s = %s  roles %s  pool sha %s" % (
                c, cats[c]["DISPOSITION"], {k: len(v) for k, v in cats[c]["roles"].items()},
                cats[c]["accepted_pool_sha256"][:12]))
            L.append("    per stratum accepted/evaluated: %s" % {op: "%d/%d" % (v["accepted"], v["evaluated"])
                                                                  for op, v in cats[c]["per_stratum"].items()})
        else:
            L.append("  CATALOG_%s = NOT PRODUCED" % c)
    L.append("  CATALOG_C = generated and hashed only (E3 conditional)")
    L.append("")
    L += ["  E1 (catalog A):"] + exp_block("E1", e1) + donor_lines("A")
    L += ["", "  E2 (catalog B):"] + exp_block("E2", e2) + donor_lines("B")
    y1, y2 = (e1 or {}).get("BOUNDED_RSI"), (e2 or {}).get("BOUNDED_RSI")
    rep = "YES" if (y1 == "YES" and y2 == "YES") else "NO"
    L += ["", "  REPLICATED_BOUNDED_RSI = %s" % rep]
    if (y1 == "YES") != (y2 == "YES"):
        L.append("  REPLICATION = NO (positive fossil preserved)")
    L += ["  G4_REPRESENTATIONAL_CEILING = %s" % extra.get("ceiling", "UNTESTABLE"),
          "    %s" % extra.get("ceiling_reason", ""), ""]
    if e4:
        L += ["  S1_NECESSITY = %s  (WHOLE recovered %d/3, BODY_ONLY %d/3)" % (
            e4["S1_NECESSITY"], e4["whole_recovered"], e4["body_only_recovered"])]
        for k, v in sorted(e4["results"].items()):
            L.append("    %-12s derived %s selected %s RECOVERED %s" % (k, v["derived"], v["selected"], v["RECOVERED"]))
        L.append("    note: %s" % extra.get("e4_note", ""))
    L += ["", "-" * 78, "1. CLOUD, TIME, SPEND", "-" * 78,
          "  CLOUD_UNAVAILABLE at T0 (no RunPod key, no Azure CLI/credential); not polled.",
          "  Total cloud spend: $0.00. No remote resource created.",
          "  Total elapsed: %s" % elapsed,
          "  Wall-clock under concurrent stages is CONTAMINATED; all endpoints are charges.", "",
          "-" * 78, "2. APPARATUS DEFECTS AND DEVIATIONS", "-" * 78]
    L += ["  - " + x for x in extra.get("defects", [])]
    L += ["", "-" * 78, "3. WHAT THIS DOES AND DOES NOT ESTABLISH", "-" * 78]
    L += ["  " + x for x in extra.get("ceiling_text", [])]
    L += ["", "-" * 78, "4. ARTIFACTS", "-" * 78,
          "  A16_DRAWS / A16_CATALOGS / A16_{A,B}_DONORS / A16_E{1,2,4}_RESULT (roles/Aphrodite/engine/)",
          "  branch aphrodite/engine-2026-09-21", "",
          "+" + "=" * 78 + "+", "|  END. 'Not worth continuing' remains a first-class answer." + " " * 20 + "|",
          "+" + "=" * 78 + "+"]
    OUT.write_text("\n".join(L) + "\n", encoding="ascii", errors="replace")
    print(OUT)


if __name__ == "__main__":
    main(sys.argv[1], json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 else {})
