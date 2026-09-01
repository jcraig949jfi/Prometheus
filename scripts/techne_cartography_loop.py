"""techne_cartography_loop.py -- one tick of the Techne 48-hour research cartography campaign.

Follows the repository's established seat-loop convention (scripts/charon_loop.py,
scripts/harmonia_loop.py): ONE cycle per invocation, state in a JSON file so the campaign
survives process restarts, driven by Claude Code's /loop:

    /loop 30m python scripts/techne_cartography_loop.py

    python scripts/techne_cartography_loop.py --init      # cycle 000, freeze the manifest
    python scripts/techne_cartography_loop.py             # run the next cycle
    python scripts/techne_cartography_loop.py --status    # print state, run nothing
    python scripts/techne_cartography_loop.py --report    # force a Charon report now

WHY ONE TICK PER INVOCATION rather than a long-lived process with sleeps: a 48-hour resident
process is the most fragile way to run a 48-hour campaign. Everything durable lives in
append-only JSONL under techne/cartography/store/, so a crash, a reboot or a closed terminal
costs the cycle in flight and nothing else.

STOPPING IS AUTOMATIC AND HARD. The campaign refuses to run past its planned cycle count or
past its 48-hour deadline, whichever comes first, and says so. "Do not silently extend the
campaign" is enforced here rather than left to discipline.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
for _p in (str(_REPO_ROOT), str(_SCRIPT_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from techne.cartography import cycle as cyc              # noqa: E402
from techne.cartography import report as rep             # noqa: E402
from techne.cartography import seeds, store, taxonomy    # noqa: E402
from techne.cartography.schema import digest, now_iso    # noqa: E402

CARTO = _REPO_ROOT / "techne" / "cartography"
STATE_PATH = CARTO / "campaign_state.json"
MANIFEST_PATH = CARTO / "CAMPAIGN_MANIFEST.json"

PLANNED_CYCLES = 96
DURATION_HOURS = 48
REPORT_EVERY_HOURS = 4


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        # A torn state file must not end the campaign; the cycle fossils are the real record
        # and state is a convenience index that can be rebuilt from them.
        cycles = store.read_cycles()
        return {"last_cycle": max([c["cycle"] for c in cycles], default=-1),
                "recovered_from_torn_state": True}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")
    tmp.replace(STATE_PATH)          # atomic on the same volume


def init_campaign() -> dict:
    """CYCLE 000. Freeze the manifest and record the start timestamp.

    The manifest is hashed and never rewritten. That hash is what makes the historical
    backtest meaningful: a prediction made under a frozen protocol can be checked, and a
    protocol edited after the reveal cannot.
    """
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    start = time.time()
    man = {
        "campaign_id": "techne-cartography-" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(start)),
        "mission": ("build and adversarially test a machine-readable cartography of search "
                    "physics across evolutionary computation, program synthesis, "
                    "quality-diversity, mechanistic interpretability and neurosymbolic "
                    "reasoning; find what researchers may have missed WITHOUT treating "
                    "retrieval absence as discovery"),
        "start_iso": now_iso(),
        "start_epoch": start,
        "duration_hours": DURATION_HOURS,
        "planned_cycles": PLANNED_CYCLES,
        "cycle_interval_minutes": 30,
        "report_every_hours": REPORT_EVERY_HOURS,
        "deadline_epoch": start + DURATION_HOURS * 3600,
        "schema_version": "cartography-0.1",
        "taxonomy_gen0": {
            "bottlenecks": list(taxonomy.BOTTLENECKS.keys()),
            "qd_axes": taxonomy.QD_AXES,
            "total_cells": taxonomy.total_cells(),
            "n_mechanisms": len(taxonomy.MECHANISMS),
            "mutation_tests": list(taxonomy.TAXONOMY_MUTATION_TESTS),
        },
        "seed_corpus": {
            "core": list(seeds.CORE_SURFACE),
            "collision": list(seeds.COLLISION_QUERIES),
            "awkward": list(seeds.AWKWARD_QUERIES),
            "historical": list(seeds.HISTORICAL_QUERIES),
            "total_seed_queries": len(seeds.all_seeds()),
        },
        "sources": {
            "primary": ["openalex", "crossref", "arxiv", "dblp"],
            "blocked": {"semanticscholar": "HTTP 429 without an API key (measured 2026-08-31); "
                                           "never counted as an independent formulation"},
            "politeness": "mailto identification, per-host minimum interval, 429 backoff, "
                          "no scraping, no paywall circumvention, no auth defeat",
        },
        "adjudication_rule": ("an LLM or heuristic may PROPOSE; only a deterministic predicate "
                             "over stored evidence may write CONFIRMED. Predicates P1-P6 are "
                             "frozen in techne/cartography/predicates.py at this digest."),
        "hole_promotion_rule": ("PERSISTENT_COVERAGE_HOLE requires >= 4 distinct formulations "
                               "across >= 3 independent indexes with 0 relevant results. It "
                               "means 'no matching experiment found under this protocol', "
                               "never 'nobody has tried this'."),
        "anti_goals": [
            "no citation-count leaderboard",
            "no generic literature summaries",
            "absence is never reported as novelty",
            "no imputed budgets or metrics",
            "no algorithm names used as scientific coordinates",
            "failed searches are recorded, never hidden",
        ],
        "charon_report_path": "charon/reports/techne_cartography_hourNN_<UTC>.txt",
        "code_digests": {},
    }
    # Hash the frozen code so a later reader can tell whether the protocol moved mid-campaign.
    for name in ("schema.py", "store.py", "sources.py", "taxonomy.py", "predicates.py",
                 "seeds.py", "cycle.py", "report.py"):
        p = CARTO / name
        if p.exists():
            man["code_digests"][name] = digest(p.read_text(encoding="utf-8"))
    man["manifest_digest"] = digest({k: v for k, v in man.items() if k != "manifest_digest"})

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(man, indent=2), encoding="utf-8")
    return man


def should_stop(man: dict, state: dict) -> tuple:
    nxt = int(state.get("last_cycle", -1)) + 1
    if nxt >= man.get("planned_cycles", PLANNED_CYCLES):
        return True, ("cycle budget exhausted: " + str(nxt) + " >= "
                      + str(man.get("planned_cycles")))
    if time.time() > man.get("deadline_epoch", 0):
        return True, "48-hour deadline passed"
    return False, ""


def maybe_report(man: dict, state: dict, force: bool = False):
    last = state.get("last_report_epoch")
    due = force or last is None or (time.time() - float(last)) >= REPORT_EVERY_HOURS * 3600
    if not due:
        return None
    p = rep.write_report(man)
    # charon/reports/ is covered by .gitignore's `**/reports/` rule, so a report written there
    # is invisible to everyone but this machine. Six reports were produced and none shipped
    # before this was caught (LIM-005). Force-staging here makes delivery part of writing
    # rather than a separate step someone has to remember.
    try:
        import subprocess
        subprocess.run(["git", "add", "-f", str(p)], cwd=str(_REPO_ROOT),
                       capture_output=True, timeout=30)
    except Exception:                                                 # noqa: BLE001
        pass
    state["last_report_epoch"] = time.time()
    state.setdefault("reports", []).append(str(p.relative_to(_REPO_ROOT)))
    return p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true", help="cycle 000: freeze manifest, no crawl")
    ap.add_argument("--status", action="store_true", help="print state and exit")
    ap.add_argument("--report", action="store_true", help="force a Charon report now")
    ap.add_argument("--max-new", type=int, default=12,
                    help="max new sources compiled per cycle (politeness bound)")
    a = ap.parse_args()

    man = init_campaign()
    state = load_state()

    if a.status:
        s = store.summary()
        print("campaign : " + man["campaign_id"])
        print("started  : " + man["start_iso"])
        print("elapsed  : {:.2f} h of {}".format(
            (time.time() - man["start_epoch"]) / 3600.0, man["duration_hours"]))
        print("cycles   : {} of {}".format(int(state.get("last_cycle", -1)) + 1,
                                           man["planned_cycles"]))
        print("lanes    : " + json.dumps(state.get("lane_counts", {})))
        for k, v in s.items():
            print("  {:34s} {}".format(k, v))
        return 0

    if a.report:
        p = maybe_report(man, state, force=True)
        save_state(state)
        print("report written: " + str(p))
        return 0

    if a.init:
        state.setdefault("last_cycle", -1)
        state["initialized_at"] = now_iso()
        save_state(state)
        print("CYCLE 000 COMPLETE -- campaign manifest frozen")
        print("  campaign_id     : " + man["campaign_id"])
        print("  manifest_digest : " + man["manifest_digest"])
        print("  start           : " + man["start_iso"])
        print("  planned cycles  : " + str(man["planned_cycles"]))
        print("  seed queries    : " + str(man["seed_corpus"]["total_seed_queries"]))
        print("  QD cells        : " + str(man["taxonomy_gen0"]["total_cells"]))
        print("  report path     : " + man["charon_report_path"])
        return 0

    stop, why = should_stop(man, state)
    if stop:
        print("CAMPAIGN STOPPED: " + why)
        maybe_report(man, state, force=True)
        save_state(state)
        return 0

    # LIM-011 REPAIR: the number is RESERVED by exclusive file creation, not derived from
    # local state. Two concurrent workers cannot receive the same number even with no shared
    # memory, no lock file and no agreed clock.
    n, _reserved_path = store.allocate_cycle(int(state.get("last_cycle", -1)) + 1)
    rec, state = cyc.run_cycle(n, state, max_new=a.max_new)
    p = maybe_report(man, state)
    save_state(state)

    print("cycle {:03d} [{}] lane={} target={}".format(
        rec.cycle, rec.status, rec.frontier_kind, str(rec.frontier_target)[:52]))
    print("  genomes+{}  claims+{}  holes+{}  killed={}  confounds+{}  rejected={}".format(
        rec.genomes_created, rec.claims_created, rec.holes_proposed,
        rec.holes_killed, rec.confounds_found, rec.sources_rejected))
    if rec.blockers:
        print("  blockers: " + "; ".join(str(b)[:70] for b in rec.blockers[:3]))
    if p:
        print("  charon report: " + str(p.relative_to(_REPO_ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
