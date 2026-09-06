"""The substrate census: the signal campaign's instrument.

One row per tick in ``archaeon.substrate_census`` recording what the fossil
substrate could support that cycle. Counts and hashes only. The slope of
``detectors_eligible`` and ``s17_eligible_units`` over time is the campaign's
progress measure -- "is the substrate becoming interrogable?" -- and it needs no
signal to be useful. It is also what turns every delegation to another lane
into a measurable before/after.

The WISHLIST is the other half: per detector that is not eligible, the specific
structure that would flip it, measured against the corpus in hand. It is
generated from the eligibility census's own blocked reasons, so it cannot
drift from what the detectors actually require.

Nothing here is a scientific claim.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from .. import cadence as cad

#: What each detector needs, in the vocabulary the eligibility census uses for
#: its blocked_reason `cause`. Kept small and literal; a wishlist entry is a
#: pointer to a lane, not an argument.
WISHLIST_BY_CAUSE = {
    "NO_PLAYER_FIELD": {
        "need": "observation-level player attribution in the chart",
        "lane": "archaeon",
        "how": "use a chart whose player_field resolves per observation "
               "(sfe.spec_players.v0 reads spec.pew.players)"},
    "EMPTY_CORPUS": {
        "need": "any engine-attested observation under the declared tenancy",
        "lane": "vivarium",
        "how": "the loop must run; nothing to detect until it does"},
    "PLAYER_UNBOUND": {
        "need": "experiments that DECLARE pew.players (non-empty)",
        "lane": "archaeon+vivarium",
        "how": "Archaeon's spec builder must name the player; Vivarium passes "
               "spec.pew.players through unchanged"},
}

S17_WISHLIST = {
    "need": ">=2 comparison groups x 2 arms x >=2 worlds x >=4 ordered "
            "observations, with arm identity preserved in the fossil",
    "lane": "vivarium+daedalus",
    "how": "Vivarium implements repeated execution using SFE's existing "
           "record_observation(replication=True); Daedalus verifies the "
           "semantics and the families(kind=comparison) contract",
}


def build(corpus, results: Dict[str, Any], census: Dict[str, Any], *,
          lane: str, s17: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Assemble one census row from what tick() already computed."""
    detectors: Dict[str, Any] = {}
    wishlist: List[Dict[str, Any]] = []
    for name, r in results.items():
        e = r.eligibility
        cause = (e.detail or {}).get("cause")
        detectors[name] = {"eligible": e.eligible_units, "total": e.total_units,
                           "fired": len(r.signals),
                           "cause": cause if not e.is_eligible else None}
        if not e.is_eligible:
            item = dict(WISHLIST_BY_CAUSE.get(cause, {
                "need": e.blocked_reason, "lane": "archaeon",
                "how": "see detector blocked_reason"}))
            item["detector"] = name
            wishlist.append(item)
    if s17 is not None and not s17.get("eligible_units"):
        wishlist.append(dict(S17_WISHLIST, detector="S17_FRAGILITY"))

    return {
        "lane": lane,
        "chart": corpus.chart.name,
        "corpus_hash": corpus.corpus_hash(),
        "rows": len(corpus.rows),
        "regions": len({r.region for r in corpus.rows}),
        "players": len({r.player for r in corpus.rows if r.player}),
        "tenancy": (corpus.window or {}).get("tenancy") or {},
        "detectors": detectors,
        "detectors_eligible": census["detectors_eligible"],
        "detectors_fired": census["detectors_fired"],
        "s17_eligible_units": (s17 or {}).get("eligible_units"),
        "s17_verdict": (s17 or {}).get("verdict"),
        "wishlist": wishlist,
        "instance": cad.instance_id(),
    }


def persist(conn, row: Dict[str, Any]) -> Optional[int]:
    """Write one census row. Failure is logged by the caller, never raised into
    the tick: a census that cannot be written must not stop a proposal."""
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO archaeon.substrate_census
            (lane, chart, corpus_hash, rows, regions, players, tenancy,
             detectors, detectors_eligible, detectors_fired,
             s17_eligible_units, s17_verdict, wishlist, instance)
        VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s,%s,%s,%s,%s::jsonb,%s)
        RETURNING census_id
        """,
        (row["lane"], row["chart"], row["corpus_hash"], row["rows"],
         row["regions"], row["players"], json.dumps(row["tenancy"], default=str),
         json.dumps(row["detectors"], default=str), row["detectors_eligible"],
         row["detectors_fired"], row["s17_eligible_units"], row["s17_verdict"],
         json.dumps(row["wishlist"], default=str), row["instance"]))
    cid = cur.fetchone()[0]
    conn.commit()
    return int(cid)


def series(conn, lane: str, limit: int = 200) -> List[Dict[str, Any]]:
    """The time series, newest first. This is the campaign's chart."""
    cur = conn.cursor()
    cur.execute(
        "SELECT taken_at, rows, regions, players, detectors_eligible, "
        "       detectors_fired, s17_eligible_units, s17_verdict, corpus_hash "
        "  FROM archaeon.substrate_census WHERE lane = %s "
        " ORDER BY taken_at DESC LIMIT %s", (lane, int(limit)))
    names = [d[0] for d in cur.description]
    return [dict(zip(names, r)) for r in cur.fetchall()]


def main(argv=None) -> int:
    """python -m archaeon.producer.census --lane prod [--limit 50]"""
    import argparse
    ap = argparse.ArgumentParser(prog="archaeon.producer.census")
    ap.add_argument("--lane", default="prod")
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--wishlist", action="store_true",
                    help="print the latest wishlist instead of the series")
    a = ap.parse_args(argv)
    from evidence_wiki.ew import db as ewdb
    conn = ewdb.connect()
    try:
        if a.wishlist:
            cur = conn.cursor()
            cur.execute("SELECT taken_at, wishlist FROM archaeon.substrate_census "
                        " WHERE lane = %s ORDER BY taken_at DESC LIMIT 1", (a.lane,))
            row = cur.fetchone()
            print(json.dumps({"taken_at": str(row[0]) if row else None,
                              "wishlist": row[1] if row else []},
                             indent=2, default=str))
        else:
            print(json.dumps(series(conn, a.lane, a.limit), indent=2, default=str))
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
