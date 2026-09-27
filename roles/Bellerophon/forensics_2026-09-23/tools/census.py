"""PHASE 1 census of the completed campaign, reconstructed from the raw files (never from the packet's prose).

Writes receipts/CENSUS.json. Read-only on the evidence.
    python roles/Bellerophon/forensics_2026-09-23/tools/census.py"""
from __future__ import annotations

import collections
import datetime
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import load as Ld  # noqa: E402

C = collections.Counter


def utc(ts: float) -> str:
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> None:
    R = Ld.runs(); F = Ld.families(); D = Ld.decisions(); FL = Ld.flags(); S = Ld.state_small()
    out = {"source": str(Ld.WD), "n_runs_jsonl": len(R), "n_families_jsonl": len(F), "n_decisions": len(D), "n_flags": len(FL)}

    # ---- identity / integrity -------------------------------------------------------------------------------------
    ids = [r["id"] for r in R]
    nos = sorted(r["_no"] for r in R)
    out["integrity"] = {
        "unique_run_ids": len(set(ids)), "duplicate_run_ids": [k for k, v in C(ids).items() if v > 1][:20],
        "run_no_min": nos[0], "run_no_max": nos[-1], "missing_run_nos": sorted(set(range(1, nos[-1] + 1)) - set(nos))[:50],
        "run_dirs_on_disk": len(os.listdir(Ld.WD / "runs")),
        "state_n_runs": S["n_runs"], "state_next_run_no": S["next_run_no"],
        "families_referenced_by_runs_not_in_families_jsonl": len({r["family"] for r in R} - set(F)),
        "families_with_zero_runs": sum(1 for f in F.values() if not f["runs"]),
        "family_run_lists_total": sum(len(f["runs"]) for f in F.values()),
        "family_allocated_total": sum(f["allocated"] for f in F.values()),
        "family_allocated_ne_runs": sum(1 for f in F.values() if f["allocated"] != len(f["runs"])),
    }
    # ingest order vs run number (imap_unordered): how far out of order
    disorder = [abs(r["_ingest"] + 1 - r["_no"]) for r in R]
    out["integrity"]["ingest_vs_runno_max_displacement"] = max(disorder)

    # ---- wall time from run-dir mtimes ------------------------------------------------------------------------------
    mt = {}
    for r in R:
        try:
            mt[r["id"]] = os.stat(Ld.WD / "runs" / r["id"] / "summary.json").st_mtime
        except OSError:
            mt[r["id"]] = None
    ok = [v for v in mt.values() if v]
    out["wall"] = {"start_utc": S["start_utc"], "stopped_utc": S["stopped"], "hours_declared": S["hours"],
                   "first_summary_mtime": utc(min(ok)), "last_summary_mtime": utc(max(ok)),
                   "missing_summary_json": sum(1 for v in mt.values() if v is None),
                   "run_wall_s": {"sum_hours": round(sum(r.get("wall_s") or 0 for r in R) / 3600, 1),
                                  "median": sorted(r.get("wall_s") or 0 for r in R)[len(R) // 2],
                                  "max": max(r.get("wall_s") or 0 for r in R)}}
    # completion-hour histogram (throughput; a worker stall shows as a hole)
    t0 = S["start_ts"]
    hours = C(int((v - t0) // 3600) for v in ok)
    out["wall"]["completions_per_hour"] = [hours.get(h, 0) for h in range(0, 73)]
    gaps = sorted(ok); big = [(utc(a), round(b - a, 1)) for a, b in zip(gaps, gaps[1:]) if b - a > 120]
    out["wall"]["completion_gaps_over_120s"] = big[:50]

    # ---- kinds / stages ---------------------------------------------------------------------------------------------
    out["runs_by_kind"] = dict(C(r["kind"] for r in R))
    out["runs_by_stage"] = dict(C(r["stage"] for r in R))
    out["runs_by_kind_stage"] = {"%s/%s" % k: v for k, v in C((r["kind"], r["stage"]) for r in R).items()}
    out["state_counters"] = S["counters"]
    out["stage_log"] = S["stage_log"]
    out["decisions_by_kind"] = dict(C(d["kind"] for d in D))
    out["restart_events"] = [d for d in D if d["kind"] in ("resume", "finalize", "halt")]

    # ---- families -----------------------------------------------------------------------------------------------------
    fam_kind = C(f["kind"] for f in F.values())
    runs_per_fam = C(len(f["runs"]) for f in F.values())
    out["families"] = {"n": len(F), "by_creating_kind": dict(fam_kind), "promoted": sum(f["promoted"] for f in F.values()),
                       "retired": sum(f["retired"] for f in F.values()),
                       "runs_per_family_hist": dict(sorted(runs_per_fam.items())),
                       "families_with_1_run": runs_per_fam.get(1, 0),
                       "unique_vectors": len({json.dumps(f["vec"], sort_keys=True) for f in F.values()})}
    prom_utc = {d["family"]: d["utc"] for d in D if d["kind"] == "promote"}
    # promotion by the kind of the run that promoted
    by_id = {r["id"]: r for r in R}
    pk = C()
    for d in D:
        if d["kind"] == "promote":
            rid = d["reason"].split()[1]
            pk[by_id[rid]["kind"] if rid in by_id else "?"] += 1
    out["families"]["promotions_by_promoting_run_kind"] = dict(pk)
    out["families"]["promotion_score_hist_all_runs"] = dict(sorted(C(r["score"] for r in R).items()))
    # promotion lineage: parents chains
    depth = {}
    def dep(fid, seen=()):
        if fid in depth:
            return depth[fid]
        ps = [p for p in (F.get(fid) or {}).get("parents", []) if p in F and p not in seen]
        depth[fid] = 0 if not ps else 1 + max(dep(p, seen + (fid,)) for p in ps)
        return depth[fid]
    for fid in F:
        dep(fid)
    out["families"]["parent_depth_hist"] = dict(sorted(C(depth.values()).items()))

    # ---- unique initial conditions / seeds / duplicates -----------------------------------------------------------
    ic = C()
    seeds = C(r["seed"] for r in R)
    for r in R:
        cfg_it = None
        ic[(json.dumps(r["vec"], sort_keys=True), r["seed"])] += 1
    out["seeds"] = {"unique_seeds": len(seeds), "runs": len(R), "seeds_used_more_than_once": sum(1 for v in seeds.values() if v > 1),
                    "max_reuse_of_one_seed": max(seeds.values()),
                    "exact_duplicate_vec_seed_pairs": sum(v - 1 for v in ic.values() if v > 1)}
    dup = [k for k, v in ic.items() if v > 1][:10]
    out["seeds"]["duplicate_examples"] = [{"vec_seed": k[1], "n": ic[k], "runs": [r["id"] for r in R if r["seed"] == k[1] and json.dumps(r["vec"], sort_keys=True) == k[0]]} for k in dup]
    out["seeds"]["dup_by_kind"] = dict(C(r["kind"] for r in R if ic[(json.dumps(r["vec"], sort_keys=True), r["seed"])] > 1))

    # ---- factor / task / topology / mutation coverage -------------------------------------------------------------
    cov = {a: dict(C(r["vec"][a] for r in R)) for a in Ld.AXES}
    out["coverage_runs_by_axis_level"] = cov
    out["coverage_families_by_axis_level"] = {a: dict(C(f["vec"][a] for f in F.values())) for a in Ld.AXES}
    out["topology_runs"] = dict(C(Ld.topology(r["vec"]) for r in R))
    out["mutation_regime_runs"] = dict(C("%s/%s" % (r["vec"]["mutation"], r["vec"]["mutation_rate"]) for r in R))
    out["task_x_kind_runs"] = {"%s/%s" % k: v for k, v in C((r["vec"]["task"], r["kind"]) for r in R).items()}
    out["reproduction_x_kind_runs"] = {"%s/%s" % k: v for k, v in C((r["vec"]["reproduction"], r["kind"]) for r in R).items()}
    out["init_x_kind_runs"] = {"%s/%s" % k: v for k, v in C((r["vec"]["init"], r["kind"]) for r in R).items()}

    # ---- run-level triggers -----------------------------------------------------------------------------------------
    trig_names = sorted({k for r in R for k in r["triggers"]})
    out["run_triggers"] = {}
    for k in trig_names:
        rs = [r for r in R if r["triggers"].get(k)]
        out["run_triggers"][k] = {"runs": len(rs), "families": len({r["family"] for r in rs}),
                                  "by_kind": dict(C(r["kind"] for r in rs)), "by_stage": dict(C(r["stage"] for r in rs)),
                                  "by_init": dict(C(r["vec"]["init"] for r in rs)), "by_reproduction": dict(C(r["vec"]["reproduction"] for r in rs))}

    # ---- high-value flags -------------------------------------------------------------------------------------------
    fc = {}
    for name in sorted({f["flag"] for f in FL}):
        fs = [f for f in FL if f["flag"] == name]
        fams = {f["family"] for f in fs}
        runs_ = {f.get("run") for f in fs if f.get("run")}
        fc[name] = {"events": len(fs), "unique_families": len(fams), "unique_runs": len(runs_) if runs_ else None,
                    "by_task": dict(C(F[f["family"]]["vec"]["task"] for f in fs)),
                    "by_reproduction": dict(C(F[f["family"]]["vec"]["reproduction"] for f in fs)),
                    "by_topology": dict(C(Ld.topology(F[f["family"]]["vec"]) for f in fs)),
                    "by_mutation": dict(C("%s/%s" % (F[f["family"]]["vec"]["mutation"], F[f["family"]]["vec"]["mutation_rate"]) for f in fs)),
                    "by_init": dict(C(F[f["family"]]["vec"]["init"] for f in fs)),
                    "by_scoring": dict(C(F[f["family"]]["vec"]["scoring"] for f in fs)),
                    "by_family_creating_kind": dict(C(F[f["family"]]["kind"] for f in fs))}
        if runs_:
            fc[name]["by_run_kind"] = dict(C(by_id[x]["kind"] for x in runs_))
            fc[name]["by_run_stage"] = dict(C(by_id[x]["stage"] for x in runs_))
            fc[name]["runs_per_family_hist"] = dict(sorted(C(C(f["family"] for f in fs).values()).items()))
            # temporal: completion-hour of the flagged run
            hh = C(int(((mt.get(x) or t0) - t0) // 6 // 3600) for x in runs_)
            fc[name]["flagged_runs_per_6h_window"] = [hh.get(h, 0) for h in range(12)]
    out["flags"] = fc
    # overlap matrix at FAMILY level
    fam_sets = {n: {f["family"] for f in FL if f["flag"] == n} for n in fc}
    out["flag_family_overlap"] = {"%s & %s" % (a, b): len(fam_sets[a] & fam_sets[b]) for a, b in itertools.combinations(sorted(fam_sets), 2)}
    out["flag_union_families"] = len(set().union(*fam_sets.values()))
    run_sets = {n: {f.get("run") for f in FL if f["flag"] == n and f.get("run")} for n in fc}
    out["flag_run_overlap"] = {"%s & %s" % (a, b): len(run_sets[a] & run_sets[b]) for a, b in itertools.combinations(sorted(run_sets), 2) if run_sets[a] and run_sets[b]}

    # exposure per 6h window (denominator for temporal rates)
    ex = C(int(((mt.get(r["id"]) or t0) - t0) // 6 // 3600) for r in R)
    out["runs_per_6h_window"] = [ex.get(h, 0) for h in range(12)]
    p = Ld.write("CENSUS.json", out)
    print("wrote", p)
    print(json.dumps({k: out[k] for k in ("n_runs_jsonl", "n_families_jsonl", "integrity", "runs_by_kind", "seeds")}, indent=1, default=str))


if __name__ == "__main__":
    main()
