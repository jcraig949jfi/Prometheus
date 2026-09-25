"""Instrumented deterministic replay of preserved campaign runs (directive 2026-09-23, Phase 3 corroboration).

NOT a re-run of the campaign: each replay takes one preserved (SPEC.json, seed) exactly as it was run, executes it with the
repaired engine, and is admitted ONLY if every legacy signal equals the preserved RECEIPT.json byte for byte (the repair adds no
RNG draw, so any difference means the replay is not the historical world and its provenance must not be read). The admitted
replay contributes the provenance the campaign could not record: founder origin classes, clean/inserted birth counts, the
repaired spontaneous predicate, and the ancestry of the first task crossing. Historical files are read, never written.

    python -m archaeon.z80atlas.postcampaign.replay --set flagged|named|witness_sample --workers 24
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.z80atlas.postcampaign import adjudicate as A

HERE = Path(__file__).resolve().parent
OUT = HERE / "replays"


def replay_one(hist: str, run_dir: str) -> dict:
    from archaeon.z80atlas import engine as E
    d = Path(hist) / "runs" / run_dir
    spec = json.loads((d / "SPEC.json").read_text(encoding="utf-8")); rec = json.loads((d / "RECEIPT.json").read_text(encoding="utf-8"))
    t0 = time.time(); sig = E.run(spec, rec["seed"])["signals"]
    diffs = {}
    for k, v in rec["signals"].items():
        new = sig["spontaneous_replication_legacy_label"] if k == "spontaneous_replication" else sig.get(k)
        if new != v:
            diffs[k] = [v, new]
    return {"run_id": run_dir.split("/")[-1], "run_dir": run_dir, "seed": rec["seed"], "spec_id": spec["spec_id"], "scheduler_reason": spec["scheduler_reason"],
            "admitted": not diffs, "legacy_diffs": diffs, "wall_s": round(time.time() - t0, 1),
            "historical_spontaneous_label": rec["signals"].get("spontaneous_replication"),
            "repaired_spontaneous_replication": sig["spontaneous_replication"], "inserted_lineage_replication": sig["inserted_lineage_replication"],
            "moat_crossed": sig["moat_crossed"], "init": spec["init"], "init_hybrid": spec.get("init_hybrid"), "task": spec["task"]["name"],
            "reproduction": spec["reproduction"], "provenance": sig["provenance"]}


def select(which: str, hist: Path, runs: dict, fams: dict, n: int) -> list:
    done = [r for r in runs.values() if r["status"] == "DONE"]
    if which == "flagged":
        return sorted(r["run_dir"] for r in done if r["signals"].get("spontaneous_replication"))
    if which == "named":
        adj = json.loads((HERE / "Z80ATLAS_POSTCAMPAIGN_ADJUDICATION_2026-09-23.json").read_text(encoding="utf-8"))
        out = []
        for fam, row in adj["B_rescoring"]["named"].items():
            best = runs[row["corrected_best_run"]]; out.append(best["run_dir"])
            f = fams[fam]
            for r2 in f["specs"].values():                                    # the reproduction control the scorer compared it with
                if r2["scheduler_reason"].startswith("matched_control:reproduction") and r2["factor_vector"]["task"] == best["factor_vector"]["task"]:
                    out.append(r2["run_dir"])
        return sorted(set(out))
    if which == "denovo_candidates":                                           # every random-init endogenous run WITHOUT inserted material that did not go extinct
        endo = ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "OVERWRITE", "CONSTRUCTIVE", "PAIR_EXECUTION")
        return sorted(r["run_dir"] for r in done if r["factor_vector"]["init"] == "random" and r["factor_vector"]["reproduction"] in endo
                      and "-t_" not in r["run_id"] and r["signals"]["extinct_epoch"] is None)
    if which == "seeded_moat_advantage":                                       # FORENSIC-MOAT-01 (MOAT_LEDGER.json): the complete set, no sampling
        return sorted(r["run_dir"] for r in done if r["factor_vector"]["init"] == "seeded_replicator" and "moat_advantage" in (r.get("flags") or {}))
    if which == "witness_sample":                                              # fixed-seed random sample of moat_advantage runs, per init
        rng = random.Random(20260923); out = []
        for init in ("seeded_replicator", "random"):
            pool = sorted(r["run_dir"] for r in done if "moat_advantage" in (r.get("flags") or {}) and r["factor_vector"]["init"] == init)
            out += rng.sample(pool, min(n, len(pool)))
        return out
    raise SystemExit("unknown set " + which)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--set", required=True); ap.add_argument("--hist", default=A.DEFAULT_HIST); ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--n", type=int, default=20)
    a = ap.parse_args(argv); hist = Path(a.hist)
    runs, _, _ = A.load_runs(hist); fams = A.family_table(runs)
    todo = select(a.set, hist, runs, fams, a.n)
    OUT.mkdir(exist_ok=True); results = []
    with ProcessPoolExecutor(a.workers) as ex:
        futs = {ex.submit(replay_one, str(hist), rd): rd for rd in todo}
        for fu in as_completed(futs):
            r = fu.result()
            if a.set == "seeded_moat_advantage":                              # keep the crossing ledger, drop the bulky replication records
                pv = r["provenance"]
                r["provenance"] = {k: pv[k] for k in ("founders", "first_crossing", "first_clean_crossing", "births_endo_clean", "births_endo_inserted")}
            results.append(r)
            print(json.dumps({k: r[k] for k in ("run_id", "admitted", "wall_s", "repaired_spontaneous_replication", "moat_crossed")}), flush=True)
    results.sort(key=lambda r: r["run_dir"])
    (OUT / ("REPLAY_%s.json" % a.set)).write_text(json.dumps({"set": a.set, "n": len(results), "admitted": sum(r["admitted"] for r in results),
                                                              "historical_dir": str(hist), "results": results}, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    return 0 if all(r["admitted"] for r in results) else 4


if __name__ == "__main__":
    sys.exit(main())
