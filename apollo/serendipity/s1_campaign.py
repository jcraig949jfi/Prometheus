"""s1_campaign.py -- S1 Archive Value Test runner (executes the frozen PREREGISTRATION).

Phase 1 (search): for each (world, driver, seed) run one bounded burst, bracket it by
ledger seq, and reconstruct the FULL populations from the ledger (archive = ARCHIVE_INSERT
minus ARCHIVE_EVICT; random population = ARTIFACT_EXECUTED in bracket). Winners AND losers.
Phase 2 (transfer): evaluate each source population's DISTINCT members zero-shot on every
cross-family target world; record fitness/cases_passed/behavior/output_hash.

Resumable: every cell writes its own file and is skipped if present. Per-record flush,
never shell-redirected (charter hard rule). No repair, no rescue -- the analysis is a
SEPARATE frozen script (s1_analyze.py).

Usage:
  python apollo/serendipity/s1_campaign.py --phase search   [--pilot]
  python apollo/serendipity/s1_campaign.py --phase transfer [--pilot]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import foundry_creds as fc      # noqa: E402
import world_adapter as wa      # noqa: E402
import eval_adapter as ea       # noqa: E402
import s1_worlds as sw          # noqa: E402

PIN = "50b5c2327c64bf112c635ca1487f2b1a8fd64e1b7faade9476d5dfa7215fd492"
ROOT = HERE.parent / "cycles" / "S1_archive_value"
ENGINE = "stackvm-v1"

SCORED = {"seeds": [20260901, 4242, 7], "budget": 300, "engine": ENGINE}
PILOT = {"seeds": [999], "budget": 80, "engine": ENGINE}  # throwaway harness check

# Transfer is scored as a RATE, so a bounded deterministic sample of a population's
# distinct members estimates it without evaluating hundreds of members x targets. This
# caps campaign cost; it does not bias the rate (the sample is size-invariant).
MEMBER_CAP = 40


def _ledger_len(c):
    return c.get("/v0/health")["ledger_len"]


def _events(c, s0, s1):
    span = max(s1 - s0 + 5, 1)
    out, start = [], s0
    while start < s1 + 5:
        page = c.get(f"/v0/events?start_seq={start}&limit={min(span, 1000)}")
        evs = page.get("events", [])
        if not evs:
            break
        out.extend(evs)
        nxt = page.get("next_start_seq")
        if not nxt or nxt <= start:
            break
        start = nxt
        if len(out) >= span:
            break
    return out


def _extract(events):
    """Reconstruct populations + per-artifact metadata from a run's ledger bracket."""
    meta, archived, executed = {}, [], []
    for e in events:
        k, p = e.get("kind"), e.get("payload", {})
        aid = p.get("artifact_id")
        if k in ("ARTIFACT_CREATED", "ARTIFACT_MUTATED") and aid:
            meta[aid] = {"genotype_addr": p.get("genotype_addr"),
                         "parent_ids": p.get("parent_ids"), "op": p.get("op"),
                         "behavior": p.get("behavior")}
        elif k == "ARCHIVE_INSERT" and aid:
            archived.append(aid)
            meta.setdefault(aid, {})["cell"] = p.get("cell", p.get("behavior"))
        elif k == "ARCHIVE_EVICT" and aid and aid in archived:
            archived.remove(aid)
        elif k == "ARTIFACT_EXECUTED" and aid:
            executed.append(aid)
    return {"archive_members": list(dict.fromkeys(archived)),
            "random_population": list(dict.fromkeys(executed)),
            "meta": meta}


def phase_search(cfg):
    runs = ROOT / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    c = fc.make_client(expected_release_hash=PIN, timeout_s=400.0)
    worlds = sw.scored_worlds()
    for w in worlds:
        task = wa.ensure_task(c, w["train_cases"], test_cases=w["test_cases"],
                              campaign="S1", run_id=w["world_id"], rule=w["rule"])
        for driver in ("random", "map_elites"):
            for seed in cfg["seeds"]:
                tag = f"{w['world_id']}__{driver}__s{seed}"
                out = runs / f"{tag}.json"
                if out.exists():
                    print("skip (done):", tag)
                    continue
                s0 = _ledger_len(c)
                t0 = time.time()
                rep = ea.burst(c, driver, cfg["engine"], task, seed, cfg["budget"])["report"]
                s1 = _ledger_len(c)
                pop = _extract(_events(c, s0, s1))
                rec = {"world_id": w["world_id"], "family": w["family"], "task_id": task,
                       "driver": driver, "seed": seed, "budget": cfg["budget"],
                       "engine": cfg["engine"], "foundry_pin": PIN,
                       "seq_bracket": [s0, s1], "wall_s": round(time.time() - t0, 1),
                       "report": rep, **pop}
                out.write_text(json.dumps(rec) + "\n", encoding="utf-8")
                print(f"done {tag}: archive={len(pop['archive_members'])} "
                      f"randpop={len(pop['random_population'])} "
                      f"best={rep.get('best_fitness')} {rec['wall_s']}s", flush=True)


def phase_transfer(cfg):
    runs, tdir = ROOT / "runs", ROOT / "transfer"
    tdir.mkdir(parents=True, exist_ok=True)
    c = fc.make_client(expected_release_hash=PIN, timeout_s=200.0)
    worlds = {w["world_id"]: w for w in sw.scored_worlds()}
    task_of = {}
    for f in runs.glob("*.json"):
        r = json.loads(f.read_text(encoding="utf-8"))
        task_of[r["world_id"]] = r["task_id"]
    for f in sorted(runs.glob("*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        src_fam = r["family"]
        members = (r["archive_members"] if r["driver"] == "map_elites"
                   else r["random_population"])
        members = list(dict.fromkeys(members))
        targets = [w for wid, w in worlds.items()
                   if w["family"] not in (src_fam, "DEAD") and wid != r["world_id"]]
        for tw in targets:
            tag = f"{r['world_id']}__{r['driver']}__s{r['seed']}__to__{tw['world_id']}"
            out = tdir / f"{tag}.json"
            if out.exists():
                continue
            rows = []
            for aid in members:
                try:
                    ev = c.post("/v0/evaluate",
                                {"artifact_id": aid, "task_id": task_of[tw["world_id"]],
                                 "seed": r["seed"]}).get("result", {})
                    rows.append({"artifact_id": aid, "fitness": ev.get("fitness"),
                                 "cases_passed": ev.get("cases_passed"),
                                 "cases_total": ev.get("cases_total"),
                                 "exact_success": ev.get("exact_success"),
                                 "output_hash": ev.get("output_hash"),
                                 "behavior": ev.get("behavior")})
                except Exception as e:  # noqa: BLE001
                    rows.append({"artifact_id": aid, "_error": str(e)[:120]})
            rec = {"source_world": r["world_id"], "source_family": src_fam,
                   "driver": r["driver"], "seed": r["seed"],
                   "target_world": tw["world_id"], "target_family": tw["family"],
                   "n_members": len(members), "rows": rows}
            out.write_text(json.dumps(rec) + "\n", encoding="utf-8")
            print(f"transfer {tag}: n={len(members)}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["search", "transfer"], required=True)
    ap.add_argument("--pilot", action="store_true")
    args = ap.parse_args()
    cfg = PILOT if args.pilot else SCORED
    global ROOT
    if args.pilot:
        ROOT = ROOT.parent / "S1_archive_value_PILOT"
        # throwaway harness check: 2 families x 1 world + dead, seed 999 (never a scored
        # seed), separate PILOT dir -> cannot touch or contaminate scored cells.
        sw.SCORED_FAMILIES = ["F4_quadratic_reserve", "F1_affine"]
        for fam in sw.SCORED_FAMILIES:
            first = dict(list(sw.FAMILIES[fam].items())[:1])
            sw.FAMILIES[fam] = first
    (phase_search if args.phase == "search" else phase_transfer)(cfg)
    print("PHASE COMPLETE:", args.phase, "pilot" if args.pilot else "scored")


if __name__ == "__main__":
    raise SystemExit(main())
