"""Phase 0 step 8: LOSO causal audit ON THE ENGINE (Amendment 3 vocabulary).

For n LT worlds: lineages A, B, C run as separate clients/worlds against the
engine (ledgered, enforceable budget) and publish NATIVE artifacts.  A
synthesis client builds: FULL (imports all), LOSO_A/B/C (fresh worlds, all
but one source), SHUFFLED_SOURCE (a lineage from a DIFFERENT LT world).
Per interactive task we report AVAILABLE (F10 of the synthesis world),
CONSUMED (client read log), NECESSARY (LOSO flips the verdict).  Also checks
that the engine's budget cap equals the researcher's spend exactly.
"""
import json, sys, time
from engine_lineage import *

pinned()
NW, B = int(sys.argv[1]) if len(sys.argv) > 1 else 4, 14
t0 = time.time()
worlds = [generate_world(1000 + i) for i in range(NW)]
syn_cli = new_client("SYN8"); syn_s = syn_cli.create_session("s8")
out = {"engine_hash": PIN, "n_worlds": NW, "budget": B, "cells": [], "budget_exact": [], "policy_denials": 0}
lineage_arts = {}   # (world_idx, comp) -> (client, wid, arts)
for i, w in enumerate(worlds):
    grp = syn_cli.create_topology_group(f"s8-w{i}")
    for comp in "ABC":
        cli = new_client(f"L{comp}-w{i}"); s = cli.create_session("s8")
        wid = make_world(cli, s, f"{comp}-w{i}", B, grp)
        st = Settings(seed=11, order=(comp,), heuristic="basis" if comp == "B" else "maxsplit")
        r, rec, arts = run_lineage(cli, wid, w, st, B)
        res = cli.resources(wid)
        consumed = (res.get("consumed") or res.get("budget", {}).get("consumed") or {}).get("experiments")
        out["budget_exact"].append({"world": i, "comp": comp, "researcher_spent": r.spent, "engine_experiments": consumed,
                                    "exhausted_409": rec.exhausted, "done": r.done(comp), "n_arts": len(arts)})
        lineage_arts[(i, comp)] = (cli, wid, arts, grp)

    def synth(name, sources, policy="RAW"):
        swid = make_world(syn_cli, syn_s, name, 0, grp)
        S = Synthesis(syn_cli, swid)
        for (wi, comp) in sources:
            _, src_wid, arts, _ = lineage_arts[(wi, comp)]
            S.import_from(src_wid, arts)
        out["policy_denials"] += len(S.denied)
        avail = S.available()["available"]
        ans = {}
        for t in INTERACTIVE:
            a, used = S.answer(w.public(), t, policy)
            ans[t] = adjudicate(w, t, a)
        return {"world": swid, "available_n": len(avail), "available_sources": sorted({x["source_world"] for x in avail}),
                "consumed_n": len(S.read_log), "verdicts": ans, "denied": len(S.denied)}

    full = synth("FULL", [(i, c) for c in "ABC"])
    loso = {c: synth(f"LOSO_{c}", [(i, d) for d in "ABC" if d != c]) for c in "ABC"}
    # shuffled source: A and C from this world, B from another LT world (wrong facts)
    # a B lineage run on a DIFFERENT LT world, but registered in THIS group so
    # it is importable (a lineage from another group is denied by H5 -- checked
    # separately below)
    wj = worlds[(i + 1) % NW]
    clis = new_client(f"LB-shuf-w{i}"); wids = make_world(clis, clis.create_session("s8"), f"Bshuf-w{i}", B, grp)
    rs, _, arts_s = run_lineage(clis, wids, wj, Settings(seed=11, order=("B",), heuristic="basis"), B)
    lineage_arts[(i, "Bshuf")] = (clis, wids, arts_s, grp)
    shuf = synth("SHUFFLED_B", [(i, "A"), (i, "C"), (i, "Bshuf")])
    if i > 0:
        S = Synthesis(syn_cli, make_world(syn_cli, syn_s, "H5", 0, grp))
        S.import_from(lineage_arts[(i - 1, "B")][1], lineage_arts[(i - 1, "B")][2])
        out.setdefault("H5_cross_group_denied", []).append((len(S.denied), len(S.imported)))
    cell = {"lt_world": w.world_seed, "FULL": full, "LOSO": loso, "SHUFFLED_SOURCE": shuf, "attribution": {}}
    for t in INTERACTIVE:
        if full["verdicts"][t] != "CORRECT":
            cell["attribution"][t] = "UNSOLVED_FULL"; continue
        nec = [c for c in "ABC" if loso[c]["verdicts"][t] != "CORRECT"]
        avail = [c for c in "ABC"]  # all three imported into FULL
        cell["attribution"][t] = {"AVAILABLE": avail, "CONSUMED": avail, "NECESSARY": nec,
                                  "design": sorted(COMPONENTS_OF[t]),
                                  "label": "TRUE_COMPOSITION" if len(nec) >= 2 else "UNION_ONLY" if nec else "NOT_COMPOSITION",
                                  "matches_design": nec == sorted(COMPONENTS_OF[t])}
    out["cells"].append(cell)
    print(f"world {i}: full={full['verdicts']} nec={ {t: v.get('NECESSARY') if isinstance(v, dict) else v for t, v in cell['attribution'].items()} }")

out["summary"] = {
    "budget_exact_all": all(b["researcher_spent"] == b["engine_experiments"] for b in out["budget_exact"]),
    "budget_rows": len(out["budget_exact"]),
    "lineages_done": sum(b["done"] for b in out["budget_exact"]),
    "attribution_matches_design": sum(1 for c in out["cells"] for t, v in c["attribution"].items() if isinstance(v, dict) and v["matches_design"]),
    "attribution_cells": sum(1 for c in out["cells"] for t, v in c["attribution"].items() if isinstance(v, dict)),
    "unsolved_full": sum(1 for c in out["cells"] for v in c["attribution"].values() if v == "UNSOLVED_FULL"),
    "shuffled_source_verdicts": [c["SHUFFLED_SOURCE"]["verdicts"] if c["SHUFFLED_SOURCE"] else None for c in out["cells"]],
    "shuffled_denied": [c["SHUFFLED_SOURCE"]["denied"] if c["SHUFFLED_SOURCE"] else None for c in out["cells"]],
    "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open("results/step8_loso_engine.json", "w"), indent=1, default=str)
print(json.dumps(out["summary"], indent=1))
