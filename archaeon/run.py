"""One Archaeon cycle.

    read fossils -> run detectors -> census -> rank
      -> if signals: propose a probe
         else:       propose an exploration run
      -> cadence-checked enqueue

Exactly one proposal per cycle at most. The cycle is a pure function of
(corpus, config, UTC day) up to the cadence decision, which is the database's
call and not this module's.

CLI:
    python -m archaeon.run --dry-run              # decide, print, write nothing
    python -m archaeon.run --enqueue              # decide and write
    python -m archaeon.run --census-only          # eligibility census only
    python -m archaeon.run --migrate              # apply migrations
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, Optional

from . import config as cfg
from . import detectors, explore, fossils, propose, provenance, queue, rank
from .cadence import CadenceRefused
from .clock import iso, utc_day_str


def plan(corpus, config: Optional[cfg.ArchaeonConfig] = None,
         day: Optional[str] = None) -> Dict[str, Any]:
    """Decide what this cycle would propose. Writes nothing.

    Always returns a proposal. There is no "nothing to do" outcome: an absence
    of signals routes to exploration, which is the charter's only reading of
    that absence.
    """
    config = config or cfg.DEFAULT
    day = day or utc_day_str()

    results = detectors.run_all(corpus, config.detectors)
    census = detectors.eligibility_census(results)
    signals = detectors.all_signals(results)
    candidates = rank.rank(signals, config.rank_weights)

    if candidates:
        chosen = candidates[0]
        spec = propose.build_spec(chosen, corpus)
        ev = provenance.signal_provenance(
            corpus=corpus, config=config, chosen=chosen,
            all_candidates=candidates, census=census)
        return {"mode": "weak_signal", "source_reason": "weak_signal",
                "spec": spec, "source_evidence": ev,
                "n_signals": len(signals), "n_candidates": len(candidates),
                "census": census, "day": day, "planned_at": iso()}

    selection = explore.choose(corpus, config.exploration, day=day)
    if not selection.get("ok"):
        return {"mode": "exploration", "source_reason": "exploration",
                "spec": None, "source_evidence": None, "blocked": selection,
                "n_signals": 0, "n_candidates": 0,
                "census": census, "day": day, "planned_at": iso()}

    spec = explore.build_spec(selection, corpus)
    ev = provenance.exploration_provenance(
        corpus=corpus, config=config, selection=selection, census=census)
    return {"mode": "exploration", "source_reason": "exploration",
            "spec": spec, "source_evidence": ev,
            "n_signals": 0, "n_candidates": 0,
            "census": census, "day": day, "planned_at": iso()}


def cycle(conn, corpus=None, config: Optional[cfg.ArchaeonConfig] = None
          ) -> Dict[str, Any]:
    """Plan and enqueue. Returns the outcome record."""
    config = config or cfg.DEFAULT
    corpus = corpus if corpus is not None else fossils.read(
        config.chart, lookback_rows=config.lookback_rows)

    p = plan(corpus, config)
    if p.get("spec") is None:
        return {"enqueued": False, "reason": "no legal experiment constructible",
                "plan": p}

    try:
        pid, decision = queue.enqueue(
            conn, spec=p["spec"], source_reason=p["source_reason"],
            source_evidence=p["source_evidence"], config=config)
    except CadenceRefused as exc:
        return {"enqueued": False, "reason": "cadence",
                "decision": exc.decision.to_json(), "plan": p}

    return {"enqueued": True, "proposal_id": pid,
            "decision": decision.to_json(), "plan": p}


def _connect():
    from evidence_wiki.ew import db as ewdb
    return ewdb.connect()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="archaeon.run")
    ap.add_argument("--dry-run", action="store_true",
                    help="plan and print; write nothing")
    ap.add_argument("--enqueue", action="store_true",
                    help="plan and write to the queue")
    ap.add_argument("--census-only", action="store_true",
                    help="print the eligibility census and exit")
    ap.add_argument("--migrate", action="store_true",
                    help="apply archaeon/migrations/*.sql")
    ap.add_argument("--chart", default=cfg.DEFAULT.chart)
    ap.add_argument("--lookback", type=int, default=cfg.DEFAULT.lookback_rows)
    args = ap.parse_args(argv)

    if args.migrate:
        conn = _connect()
        try:
            print(json.dumps({"applied": queue.apply_migrations(conn)}, indent=2))
        finally:
            conn.close()
        return 0

    config = cfg.ArchaeonConfig(chart=args.chart, lookback_rows=args.lookback)
    corpus = fossils.read(config.chart, lookback_rows=config.lookback_rows)

    if args.census_only:
        results = detectors.run_all(corpus, config.detectors)
        print(json.dumps({"corpus": {"hash": corpus.corpus_hash(),
                                     "rows": len(corpus),
                                     "chart": corpus.chart.name},
                          "census": detectors.eligibility_census(results)},
                         indent=2, default=str))
        return 0

    if args.enqueue:
        conn = _connect()
        try:
            print(json.dumps(cycle(conn, corpus, config), indent=2, default=str))
        finally:
            conn.close()
        return 0

    # default: dry run
    print(json.dumps(plan(corpus, config), indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
