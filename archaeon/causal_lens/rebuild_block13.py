"""Rebuild the A4 block-13 canonical graph from the PRESERVED birth events (no replay), with the D1-fixed adapter.
The glin registry fields the adapter needs (root, origin) are recovered from the HU nodes of the first graph."""
from __future__ import annotations

import json
from pathlib import Path

from archaeon.causal_lens.adapters import archaeon as AD
from archaeon.causal_lens.schema import Graph, dump, spontaneous
from archaeon.causal_lens.fossils_archaeon import EVID, OUT, summarize

ev = json.loads((EVID / "A4_block13_events.json").read_text(encoding="utf-8"))
old = json.loads((EVID / "A4_block13.graph.json").read_text(encoding="utf-8"))
reg = {}
for nid, a in old["nodes"].items():
    if a["kind"] == "HU" and nid.startswith("glin:"): reg[int(nid[5:])] = {"root": a.get("native_root"), "origin": a.get("native_origin")}
g = Graph("archaeon.lineage", "segment", {"world": "BLOCK_128", "fossil": "A4_block13_host_rescue", "rebuilt": "D1 fix"})
AD.add_events(g, ev["watched"], reg); AD.add_establishments(g, reg, ev["native"]["genetic_established_at_epoch"])
dump(g, str(EVID / "A4_block13.graph.v2.json"))
s = summarize(g); dom = "glin:%d" % ev["native"]["dominant_glin"]
host_hu = ["glin:%d" % h for h in ev["native"]["host_arrival_glins"]]
hosted = [t for t in g.of_kind("TRANSFORMATION") if g.nodes[t]["fields"].get("resulting_hu", {}).get("value") == dom and "HOSTING" in g.nodes[t]["types"]]
by_host = {h: sum(1 for t in hosted if any(g.hu_of(m) == h for m in g.out(g.nodes[t]["fields"]["host"]["value"], "owns"))) for h in host_hu}
s["block13"] = {"dominant": dom, "dominant_spontaneous": spontaneous(g, dom), "dominant_origin": sorted(g.hu_origins(dom)),
                "hosted_births_into_dominant": len(hosted), "hosted_by_host_arrival_glin": by_host,
                "host_arrival_glin_is_contributor_to_dominant": any(h in g.contributors_hu(t) for t in hosted for h in host_hu),
                "native": ev["native"]}
rr = json.loads((OUT / "REFERENCE_RESULTS.json").read_text(encoding="utf-8")); rr["A4_A5_block13"] = {"native": ev["native"], "lens": s, "defect_D1": "fixed, rebuilt from preserved events"}
(OUT / "REFERENCE_RESULTS.json").write_text(json.dumps(rr, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({"n_violations": s["n_violations"], "violations": s["violations"][:3], "block13": {k: v for k, v in s["block13"].items() if k != "native"}, "events_by_type": s["events_by_type"]}, indent=1))
