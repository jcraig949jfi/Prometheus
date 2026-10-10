"""Summarise the E3 development smoke (EXPOSED pilot_v2) and derive the per-family cost model.
python -m tfs1.e3.summarize_smoke  ->  runs/SMOKE_SUMMARY.json"""
import json
import statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    rows, per_family = [], []
    for p in sorted((HERE / "runs").glob("SMOKE_*_s*_B*.json")):
        d = json.loads(p.read_text())
        L, F = d["lifetime"], d["final"]
        rate = L["ledger"]["charges"] / max(1e-9, sum(f["cpu_s"] for f in L["families"]))
        fe = {r["opaque"]: r for r in F["families"]}
        for f in L["families"]:
            r = fe[f["opaque"]]
            per_family.append({"world": L["world_id"], "arm": L["arm"], "rung": r["rung"], "status": r["status"],
                               "charges": f["charges"], "cpu_s": f["cpu_s"], "solved": f["solved"],
                               "qualified": r.get("qualified", False)})
        dep = d["dependency"]
        rows.append({"world": L["world_id"], "arm": L["arm"], "seed": L["seed"], "B": L["config"]["B"],
                     "R": L["config"]["R"], "K": L["config"]["K"], "order": L["order_name"],
                     "families": len(L["families"]), "solved_in_lifetime": L["solved"],
                     "endpoint": F["endpoint"], "final_library": [(e["body"], e["depth"])
                                                                  for e in L["final_library"]["entries"]],
                     "archive_size": len(L["archive_final"]), "ledger": L["ledger"],
                     "lifetime_cpu_s": d["cpu_s"]["lifetime"], "final_and_dependency_cpu_s":
                         d["cpu_s"]["final_and_dependency"], "charges_per_cpu_s": round(rate),
                     "families_using_library": sum(f["uses_library"] for f in L["families"]),
                     "hits_from_archive_origin": sum(1 for f in L["families"] if f["origin"] == "archive"),
                     "dependency_tests": [{"family": x["family_id"], "replay_reproduces": x["replay_reproduces"],
                                           "supported_depth": x["supported_depth"],
                                           "entries": [(e["entry"], e["depth"], e["DEPENDENCY_SUPPORTED"])
                                                       for e in x["entries"]]} for x in dep],
                     "decision_sha256": L["decision_sha256"]})
    # cost model
    rates = [r["charges_per_cpu_s"] for r in rows]
    cpu_per_charge = 1.0 / statistics.median(rates) if rates else None
    by_rung = defaultdict(list)
    for x in per_family:
        by_rung[x["rung"]].append(x)
    rung_tab = {k: {"n": len(v), "solved_frac": round(sum(x["solved"] for x in v) / len(v), 3),
                    "mean_charges": round(statistics.mean(x["charges"] for x in v)),
                    "mean_cpu_s": round(statistics.mean(x["cpu_s"] for x in v), 2)} for k, v in sorted(by_rung.items())}
    nfam = statistics.mean(r["families"] for r in rows) if rows else 0
    model = {"median_charges_per_cpu_s": statistics.median(rates) if rates else None,
             "cpu_s_per_charge": cpu_per_charge,
             "families_per_world_mean": nfam,
             "upper_bound_core_h_per_lifetime": {str(B): round(nfam * B * cpu_per_charge / 3600, 3)
                                                 for B in (20_000, 50_000, 100_000, 200_000)} if rows else None,
             "screen_upper_bound_core_h": {str(B): round(8 * 7 * nfam * B * cpu_per_charge / 3600, 1)
                                           for B in (20_000, 50_000, 100_000, 200_000)} if rows else None,
             "note": "upper bound = every family spends the full B (unsolved families do); solved families stop "
                     "earlier. 8 worlds x 7 arms (4 cells + 3 controls) x 1 seed. Final evaluation is negligible; "
                     "dependency re-runs cost 3 x B per (solution, entry)."}
    out = {"label": "DEVELOPMENT SMOKE on EXPOSED pilot_v2 data; not a screen; no statistics claimed",
           "runs": rows, "per_rung": rung_tab, "cost_model": model}
    (HERE / "runs" / "SMOKE_SUMMARY.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    for r in rows:
        e = r["endpoint"]
        print("%-10s %-17s solved %2d qual %2d R3R4 %d/%d R2 %d/%d lib %d arch %3d useLib %d fromArch %d cps %d cpu %.0f dep %s"
              % (r["world"], r["arm"], r["solved_in_lifetime"], e["total_qualified"], e["R3R4_admitted_qualified"],
                 e["admitted_R3R4"], e["R2_admitted_qualified"], e["admitted_R2"], len(r["final_library"]),
                 r["archive_size"], r["families_using_library"], r["hits_from_archive_origin"],
                 r["charges_per_cpu_s"], r["lifetime_cpu_s"], r["dependency_tests"]))
    print(json.dumps(rung_tab))
    print(json.dumps(model))


if __name__ == "__main__":
    main()
