"""Cycle-9 report: ADJUDICATION_C9.json -> REPORT_C9.md. No number is typed by hand.

The report opens with a MACHINE block (JSON between markers) holding every load-bearing
number and verdict; every sentence below it is rendered from that same block. The audit
(report_audit_c9.py) recomputes the block from the raw bundle files independently and
fails the report on any disagreement.

    python report_c9.py [observatory]
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
BEGIN, END = "<!-- MACHINE-BEGIN", "MACHINE-END -->"


def machine(adj):
    h = adj["hypotheses"]
    m = {"constants_sha256": adj["constants_sha256"]}
    if "H1" in h:
        x = h["H1"]
        m["H1"] = {"verdict": x["verdict"], "n_complete": x.get("n_complete"),
                   "M": x.get("M"), "I": x.get("I"), "threshold": adj["rules"]["H1_THRESHOLD"],
                   "means_held_final": x.get("means_held_final")}
    if "H2" in h:
        p = h["H2"]["primary"]
        m["H2"] = {"verdict": h["H2"]["verdict"], "supporting": p["supporting"],
                   "distinct_supporting_strata": p["distinct_supporting_strata"],
                   "per_specimen": {k: {"verdict": v["verdict"], "B_reaching": v["B_reaching"],
                                        "C_reaching": v["C_reaching"]}
                                    for k, v in sorted(p["specimens"].items())},
                   "sensitivity_literal_verdict": h["H2"]["sensitivity_literal_authorship"]["verdict"]}
    if "H3" in h:
        x = h["H3"]
        m["H3"] = {"verdict": x["verdict"], "n_complete": x.get("n_complete"),
                   "certificates": x.get("certificates"),
                   "separation_vs_B": x.get("separation_vs_B"),
                   "separation_vs_C": x.get("separation_vs_C")}
    return m


def render(adj, prov):
    m = machine(adj)
    L = ["# Cycle 9 -- verification report", "",
         "Generated from `ADJUDICATION_C9.json`; every number below is rendered from the "
         "machine block and recomputed from the raw bundle files by `report_audit_c9.py`.",
         "Provenance: protocol `%s`, manifest `%s`." % (prov.get("protocol_hash", "?"),
                                                       prov.get("manifest_hash", "?")), "",
         BEGIN, json.dumps(m, indent=1, sort_keys=True), END, ""]
    if "H1" in m:
        x = m["H1"]
        L += ["## H1 -- cue gating", "",
              "Verdict **%s** over %s complete bundles: gate main effect M = %s, "
              "cost interaction I = %s (threshold %s on final held-out competence)."
              % (x["verdict"], x["n_complete"], x["M"], x["I"], x["threshold"]), ""]
    if "H2" in m:
        x = m["H2"]
        L += ["## H2 -- propagation of P-11 replicators", "",
              "Verdict **%s**: %d supporting specimen(s) across %d distinct stratum/strata. "
              "Literal-authorship sensitivity verdict: **%s**."
              % (x["verdict"], len(x["supporting"]), x["distinct_supporting_strata"],
                 x["sensitivity_literal_verdict"]), "",
              "| specimen | verdict | B reaching depth 5 | C reaching depth 5 |", "|---|---|---|---|"]
        for k, v in x["per_specimen"].items():
            L.append("| %s | %s | %s | %s |" % (k, v["verdict"], v["B_reaching"], v["C_reaching"]))
        L.append("")
    if "H3" in m:
        x = m["H3"]
        L += ["## H3 -- easy-niche reservoir (material ruler R3)", "",
              "Verdict **%s** over %s complete bundles. Certificates A/B/C = %s; separation "
              "A-B = %s, A-C = %s." % (x["verdict"], x["n_complete"], x["certificates"],
                                        x["separation_vs_B"], x["separation_vs_C"]), ""]
    return "\n".join(L) + "\n"


def main(argv):
    obs = HERE / (argv[1] if len(argv) > 1 else "observatory")
    adj = json.loads((obs / "ADJUDICATION_C9.json").read_text())
    prov = json.loads((obs / "LAUNCH.json").read_text()) if (obs / "LAUNCH.json").exists() else {}
    (obs / "REPORT_C9.md").write_text(render(adj, prov), encoding="utf-8")
    print("wrote", obs / "REPORT_C9.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
