"""What tick() is allowed to look at.

ARCHAEON IS FIRE-AND-FORGET ACROSS EXECUTION. Once an experiment is written to
the canonical queue, Vivarium owns its LIFECYCLE: Archaeon does not track its
completion, poll its status, wait, retry, or keep per-experiment state. In the
tick path nothing ever asks what became of a proposal.

**Archaeon's only persistent feedback channel is PEW.** New fossils are simply
new evidence on the next tick, regardless of who or what produced them.

This is a statement about OPERATION, not about EVALUATION. The queue row
carries `policy_version` and `template_id` in `source_evidence`, and Vivarium
is asked to carry them into the PEW producer block, precisely so that outcomes
can later be measured BY POLICY and BY TEMPLATE against a frozen random
baseline. That comparison is Harmonia's to adjudicate and is never performed
here; the record is what makes it possible.

That leaves exactly two reads, and the boundary between them is the point:

``recent_fossils``    the PEW/SFE record of what has been OBSERVED. The
                      scientific input. Read-only, and it never sees the
                      queue: a proposal that has not executed is not a fossil,
                      and letting the detector see pending work would let
                      Archaeon respond to its own intentions.

``publication_record``  this seat's own PUBLICATION history -- when it last
                      published and what spec hashes it has already emitted.
                      This is a producer's outbox, not a tracker: it carries
                      no status, no sfe_experiment_id, no pew_reference and no
                      error, because those describe an experiment's fate and
                      Archaeon does not follow it.

Cadence necessarily reads the queue too (how many published today, how long
since the last). That is the producer's own rate limit, not lifecycle
tracking, and it reads timestamps and ordinals -- never execution status.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .. import fossils
from .. import vivqueue as vq

#: Columns Archaeon may read from its own rows. Deliberately closed, and
#: deliberately excluding status / sfe_experiment_id / pew_reference / error:
#: those are the experiment's fate, which belongs to Vivarium.
PUBLICATION_COLUMNS = ("experiment_id", "created_at", "spec_hash",
                       "source_reason", "candidate_set_id",
                       "cadence_day_ordinal")

#: The columns Archaeon must never read live in contract.LIFECYCLE_COLUMNS,
#: declared there so a test can scan THIS module for those names without
#: matching the constant's own definition.


# --------------------------------------------------------------------------
def recent_fossils(chart: Optional[str] = None, lookback_rows: int = 2000):
    """The fossil corpus, through the normal chart machinery.

    Returns a ``fossils.Corpus``. Errors are not swallowed: a reader that
    returned an empty corpus on failure would be indistinguishable from a
    quiet substrate, and tick() must be able to tell those apart.
    """
    from .. import config as cfg
    return fossils.read(chart or cfg.DEFAULT.chart,
                        lookback_rows=lookback_rows)


def fossil_summary(corpus) -> Dict[str, Any]:
    """Small, loggable description of what was read."""
    return {"chart": corpus.chart.name,
            "rows": len(corpus.rows),
            "corpus_hash": corpus.corpus_hash(),
            "regions": len({r.region for r in corpus.rows}),
            "window": dict(corpus.window)}


# --------------------------------------------------------------------------
def publication_record(conn, lane: str, limit: int = 50) -> List[Dict[str, Any]]:
    """What this seat has PUBLISHED recently. Not what became of it.

    Reads through ``vivqueue`` so it resolves the same schema the writer uses.
    A reader pinned to production while the writer targeted a test schema
    would report an empty history and let tick() re-propose forever.
    """
    cols = ", ".join(PUBLICATION_COLUMNS)
    cur = conn.cursor()
    cur.execute(
        "SELECT {cols} FROM {q} WHERE cadence_lane = %s "
        "ORDER BY created_at DESC LIMIT %s".format(cols=cols, q=str(vq.QUEUE)),
        (lane, int(limit)))
    names = [d[0] for d in cur.description]
    return [dict(zip(names, r)) for r in cur.fetchall()]


def published_spec_hashes(conn, lane: str, limit: int = 200) -> set:
    """Spec hashes this lane has already published.

    Publication-side only: it prevents emitting a byte-identical spec twice by
    accident. A deliberate repeat is legitimate and declares ``replication_of``.
    Nothing here asks whether any of them ran.
    """
    cur = conn.cursor()
    cur.execute("SELECT spec_hash FROM {q} WHERE cadence_lane = %s "
                "ORDER BY created_at DESC LIMIT %s".format(q=str(vq.QUEUE)),
                (lane, int(limit)))
    return {r[0] for r in cur.fetchall()}


def health(conn, lane: str) -> Dict[str, Any]:
    """Producer health: publication rate and cadence position.

    Reports what ARCHAEON does -- how often it publishes and where it sits in
    its own quota. `last_published_at` and `seconds_since_last` count only rows
    that CONSUMED QUOTA, exactly as the cadence evaluator does: counting all
    rows here made health say "24 minutes ago" while cadence said "never",
    which is the kind of contradiction that teaches an operator to distrust
    both numbers. It deliberately does not count claimed/running/completed/
    failed: those describe experiments Archaeon has already handed off, and
    reporting them here would reintroduce the tracking this seat does not do.
    Queue execution state is Vivarium's to report.
    """
    cur = conn.cursor()
    cur.execute(
        """
        SELECT count(*)                                          AS published,
               count(*) FILTER (WHERE cadence_day_ordinal IS NOT NULL
                                 AND cadence_utc_day
                                     = (now() AT TIME ZONE 'UTC')::date)
                                                                  AS published_today,
               max(created_at) FILTER (WHERE cadence_day_ordinal IS NOT NULL)
                                                                  AS last_published_at,
               EXTRACT(EPOCH FROM (now() - max(created_at)
                       FILTER (WHERE cadence_day_ordinal IS NOT NULL)))
                                                                  AS seconds_since_last
          FROM {q}
         WHERE cadence_lane = %s
        """.format(q=str(vq.QUEUE)), (lane,))
    names = [d[0] for d in cur.description]
    row = dict(zip(names, cur.fetchone()))
    row["published_today"] = int(row["published_today"] or 0)
    row["published"] = int(row["published"] or 0)
    row["last_published_at"] = (str(row["last_published_at"])
                                if row["last_published_at"] else None)
    row["seconds_since_last"] = (float(row["seconds_since_last"])
                                 if row["seconds_since_last"] is not None
                                 else None)
    row["lane"] = lane
    row["queue"] = str(vq.QUEUE)
    row["note"] = ("producer health only. Execution state (claimed / running / "
                   "completed / failed) is Vivarium's to report; Archaeon is "
                   "fire-and-forget after publication.")
    return row
