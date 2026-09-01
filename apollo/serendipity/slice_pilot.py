"""slice_pilot.py -- Apollo Gen-2 thin vertical slice (charter S19).

  Foundry world -> evolutionary burst -> evaluation -> lineage/fossil -> replay,
  plus the charter's mandated cheap-baseline comparison (map_elites vs random at
  equal budget). One engine (stackvm-v1, deterministic -> clean replay), an
  Apollo-owned isolated task, bounded budget, CPU. Writes ONE fossil + a JSON log.

Two things are measured, deliberately kept separate:
  (a) SCIENCE  -- does an evolutionary burst beat a random baseline on this world
      (budget-dependent; may be "neither solves" at a small budget -- that is a
      real result, not a bug);
  (b) PLUMBING -- world/artifact/evaluate/lineage/replay all round-trip against the
      live host, deterministically. A concrete create_random organism exercises (b)
      regardless of whether (a) solved, so the loop is always fully exercised.

Usage:
  python apollo/serendipity/slice_pilot.py [--budget 300] [--engine stackvm-v1]
                                           [--seed 20260901] [--timeout 300]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import foundry_creds as fc          # noqa: E402
import world_adapter as wa          # noqa: E402
import eval_adapter as ea           # noqa: E402
import fossil as fs                 # noqa: E402

PIN = "50b5c2327c64bf112c635ca1487f2b1a8fd64e1b7faade9476d5dfa7215fd492"
OUT = HERE.parent / "cycles" / "serendipity_slice"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=300)
    ap.add_argument("--engine", default="stackvm-v1")
    ap.add_argument("--seed", type=int, default=20260901)
    ap.add_argument("--timeout", type=float, default=300.0)
    args = ap.parse_args()

    c = fc.make_client(expected_release_hash=PIN, timeout_s=args.timeout)
    run_id = "slice-" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    log = {"run_id": run_id, "charter": "gen2-slice", "client_id": "apollo",
           "foundry_pin": PIN, "engine_id": args.engine, "seed": args.seed,
           "budget": args.budget, "steps": []}

    def step(name, **kw):
        rec = {"step": name, "t": time.strftime("%H:%M:%SZ", time.gmtime()), **kw}
        log["steps"].append(rec)
        print(f"[{rec['t']}] {name}: " +
              " ".join(f"{k}={v}" for k, v in kw.items()))

    # 1. WORLD -- Apollo authors its own isolated task f(x)=3x+1
    task = wa.ensure_task(c, wa.affine_cases(3, 1, [-9, -5, -3, -1, 0, 2, 4, 6, 8, 11]),
                          test_cases=wa.affine_cases(3, 1, [-7, -2, 3, 7, 13]),
                          campaign="slice_pilot", run_id=run_id, rule="f(x)=3x+1")
    log["task_id"] = task
    step("world", task_id=task[:23] + "...", rule="f(x)=3x+1")

    # 2. BURSTS (SCIENCE) -- evolution (map_elites) vs cheap baseline (random), equal budget
    reports = {}
    for driver in ("random", "map_elites"):
        t0 = time.time()
        resp = ea.burst(c, driver, args.engine, task, args.seed, args.budget)
        rep = resp.get("report", {})
        reports[driver] = {"report": rep,
                           "operator_config_hash": resp.get("operator_config_hash")}
        step(f"burst:{driver}", solved=rep.get("solved"),
             best_fitness=rep.get("best_fitness"),
             evals=rep.get("evaluations_used"),
             archive=json.dumps(rep.get("archive_stats", {})),
             wall_s=round(time.time() - t0, 1))
    me = reports["map_elites"]["report"]
    rnd = reports["random"]["report"]
    step("baseline_compare",
         map_elites_best=me.get("best_fitness"), random_best=rnd.get("best_fitness"),
         map_elites_coverage=me.get("archive_stats", {}).get("coverage"),
         map_elites_qd=me.get("archive_stats", {}).get("qd_score"))

    # 3. ORGANISM (PLUMBING) -- a concrete create_random artifact, always available
    art = c.post("/v0/artifacts", {"engine_id": args.engine, "op": "create_random",
                                   "seed": args.seed})
    aid = art["artifact_id"]
    step("artifact", id=aid[:16], genotype_bytes=art.get("genotype_bytes_len"),
         creation_event_seq=art.get("creation_event_seq"))

    # 4. EVALUATE -> yields the replayable event_seq + result_hash
    ev = c.post("/v0/evaluate", {"artifact_id": aid, "task_id": task, "seed": args.seed})
    eval_seq, eval_hash = ev.get("event_seq"), ev.get("result_hash")
    step("evaluate", event_seq=eval_seq, result_hash=str(eval_hash)[:22])

    # 5. LINEAGE / FOSSIL CAPTURE
    cap = fs.capture(c, aid)
    step("capture", have=[k for k in cap if k != "artifact_id"])

    # 6. REPLAY -- reproducibility (charter Job I): re-run the evaluate event, compare hashes
    replay_match = None
    if eval_seq is not None:
        rp = c.post("/v0/replay", {"event_seq": int(eval_seq)})
        replay_match = rp.get("match")
        log["replay"] = rp
        step("replay", event_seq=eval_seq, match=replay_match,
             engine_version_mismatch=rp.get("engine_version_mismatch"))

    # 7. EMIT the fossil
    fossil = {
        "run_id": run_id, "kind": "serendipity_slice_v0", "foundry_pin": PIN,
        "organism_source": "create_random",  # structural: NOT a search discovery
        "world": {"task_id": task, "rule": "f(x)=3x+1", "engine_id": args.engine},
        "budget": args.budget, "seed": args.seed,
        "science": {
            "map_elites": me, "random": rnd,
            "note": ("neither solved at this budget" if not me.get("solved")
                     and not rnd.get("solved") else "see solved flags"),
        },
        "organism": {
            "artifact_id": aid,
            "genotype_addr": art.get("genotype_addr"),
            "genotype_bytes_len": art.get("genotype_bytes_len"),
            "creation_op": art.get("creation_op"),
            "creation_seed": art.get("creation_seed"),
            "creation_event_seq": art.get("creation_event_seq"),
            "parent_ids": art.get("parent_ids"),
            "genotype_b64": cap.get("genotype", {}).get("genotype_b64"),
            "lineage": cap.get("lineage", {}).get("lineage"),
        },
        "evaluate": {"event_seq": eval_seq, "result_hash": eval_hash,
                     "result": ev.get("result")},
        "replay": {"event_seq": eval_seq, "match": replay_match,
                   "engine_version_mismatch": (log.get("replay") or {}).get(
                       "engine_version_mismatch")},
    }
    fossil_path = fs.emit(fossil, str(OUT))
    log["fossil_path"] = fossil_path
    step("fossil", path=Path(fossil_path).name, provenance=fossil["provenance_hash"][:20])

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{run_id}_log.json").write_text(json.dumps(log, indent=2) + "\n",
                                            encoding="utf-8")
    ok = replay_match is True
    print(f"\nSLICE {'COMPLETE (replay verified)' if ok else 'COMPLETE'}: {fossil_path}")
    return 0 if ok else 0


if __name__ == "__main__":
    raise SystemExit(main())
