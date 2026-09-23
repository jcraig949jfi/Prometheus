"""Render a campaign REPORT.json as a pure-ASCII summary (80 columns).

  python -m prometheus.cosmos.report <campaign_out_dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def _f(x, nd=3):
    return ("%." + str(nd) + "f") % x if isinstance(x, (int, float)) else str(x)


def render(out: Path) -> str:
    r = json.loads((out / "REPORT.json").read_text(encoding="utf-8"))
    L = []
    L.append("CWE CAMPAIGN 0 REPORT  %s" % out.name)
    L.append("=" * 78)
    ident = r["identity"]
    L.append("code   head %s  src %s  dirty %s" % (str(ident.get("git_head"))[:10], ident["cosmos_src_sha"][:12], ident.get("cosmos_dirty")))
    L.append("graph  nodes %s edges %s runs %s laws %s  edge kinds %s" % (
        r["graph"]["nodes"], r["graph"]["edges"], r["graph"]["runs"], r["graph"]["laws"], r["graph"]["edge_kinds"]))
    L.append("queries (chamber, excl. oracle) %s   wall %ss" % (r.get("n_queries"), r.get("t_total_s")))
    L.append("-" * 78)
    L.append("GATES")
    for g in ("G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7"):
        v = r["gates"].get(g, {"verdict": "NOT REACHED (not run by campaign0; see G3 receipt)" if g == "G3" else "NOT REACHED"})
        L.append("  %-3s %s" % (g, v["verdict"]))
    L.append("-" * 78)
    L.append("INITIAL MINING (main dataset)")
    for k, v in r["mine_initial"].items():
        L.append("  %-4s %-26s p=%s score=%s" % (k, v["verdict"], _f(v["p"]), _f(v["score"])))
        L.append("       %s" % (v["law"] or "-"))
    L.append("ADVERSARY")
    for a in r.get("adversary", []):
        L.append("  round %d  %s  confirmed %d / confident %d" % (a["round"], a["verdict"], a["confirmed"], a["confident"]))
        L.append("    law  %s" % a["law"])
        if a.get("revision"):
            rv = a["revision"]
            L.append("    revision picked %s ; %s" % (rv["picked"], " ; ".join("%s %s" % (k, v["verdict"]) for k, v in rv.items() if k != "picked")))
    L.append("LAW LEDGER")
    for l in r.get("laws", []):
        L.append("  %s v%d parent=%s cmap=%s  %s" % (l["law_id"][:10], l["version"], (l["parent"] or "-")[:10], l["cmap"], "/".join(l["events"])))
        L.append("    %s" % l["law"])
    if "final_law" in r:
        L.append("FROZEN  %s  freeze %s" % (r["final_law"]["law"], r["final_law"]["freeze_hash"][:16]))
    if "G5" in r["gates"] and "law_ba" in r["gates"]["G5"]:
        g5 = r["gates"]["G5"]
        L.append("HOLDOUT D  BA %s acc %s base_rate %s  knn5 BA %s  majority BA %s  brier %s (clim %s)" % (
            _f(g5["law_ba"]), _f(g5["law_acc"]), _f(g5["base_rate_D"]), _f(g5["baselines"]["knn5_visible"]["ba"]),
            _f(g5["baselines"]["majority_visible"]["ba"]), _f(g5["brier"]), _f(g5["brier_climatology"])))
    if "G6" in r["gates"] and "n_scored" in r["gates"]["G6"]:
        g6 = r["gates"]["G6"]
        L.append("INTERVENTION  scored %s  direction ok %s  magnitude ok %s  in band %s" % (
            g6["n_scored"], g6["direction_ok"], g6["magnitude_ok"], g6["in_band"]))
    q = r.get("quotient")
    if q:
        L.append("QUOTIENT  %d nodes -> %d classes (%.3f); boundary edge fraction %s" % (
            q["n_nodes"], q["n_classes"], q["compression"], q["boundary_edge_fraction"]))
    if r.get("null_pool_failures"):
        L.append("ENGINEERING  null-pool failures: %s" % r["null_pool_failures"])
    L.append("=" * 78)
    return "\n".join(L)


if __name__ == "__main__":
    print(render(Path(sys.argv[1])))
