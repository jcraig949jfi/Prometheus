"""The Gen-2 authoritative substrate: one SQLite database (WAL, foreign keys ON)
holding the entire durable state -- identity hierarchy, per-world hash-chained
event ledger, transactional work queue, research objects, lineage DAG, budgets,
artifacts, measurements, checkpoints.

WHY SQLITE (grounded in the forensic baseline, not preference):
  * cross-store atomic commit was ABSENT in the existing Foundry; here an event
    append, a state change and a work claim commit as ONE transaction;
  * atomic work claiming (ABSENT) is a single guarded UPDATE under BEGIN
    IMMEDIATE;
  * per-world partitioning (ABSENT) is a world_id column + index;
  * referential integrity and queryability (needed for lineage/failure queries)
    are native;
  * it is boring, single-machine, recoverable, concurrent-reader friendly --
    exactly the section-23 constraints.

Blobs (artifact bytes) stay content-addressed on disk under blobs/, referenced
by hash from rows -- the one existing pattern worth keeping verbatim.

Connections are per-thread (SQLite objects are not shareable across threads);
open a Store per thread/worker. WAL lets many readers run while one writer holds
the write lock; BEGIN IMMEDIATE serializes writers so a claim's read-then-update
is atomic against other claimers.
"""

from __future__ import annotations

import contextlib
import sqlite3
import time
from pathlib import Path
from typing import Any, Iterator, Optional

SCHEMA_VERSION = 1

# The schema is intentionally explicit and constrained: NOT NULLs, CHECK
# enumerations on lifecycle columns, and foreign keys, so a bad transition or a
# dangling reference is a database error, not a silent corruption.
_SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY, value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS clients (
    client_id   TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    token_hash  TEXT,
    created_ts  REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id  TEXT PRIMARY KEY,
    client_id   TEXT NOT NULL REFERENCES clients(client_id),
    name        TEXT NOT NULL,
    state       TEXT NOT NULL DEFAULT 'OPEN'
                CHECK (state IN ('OPEN','CLOSED')),
    created_ts  REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_sessions_client ON sessions(client_id);

CREATE TABLE IF NOT EXISTS worlds (
    world_id        TEXT PRIMARY KEY,
    session_id      TEXT NOT NULL REFERENCES sessions(session_id),
    client_id       TEXT NOT NULL REFERENCES clients(client_id),
    name            TEXT NOT NULL,
    state           TEXT NOT NULL DEFAULT 'CREATED'
                    CHECK (state IN ('CREATED','RUNNING','PAUSED',
                                     'TERMINATED')),
    parent_world_id TEXT REFERENCES worlds(world_id),
    fork_point      INTEGER,            -- parent world_index at the fork
    sharing_policy  TEXT NOT NULL DEFAULT 'ISOLATED',
    topology_group  TEXT,
    seed_root       INTEGER NOT NULL,
    next_index      INTEGER NOT NULL DEFAULT 0,   -- next world event index
    head_hash       TEXT NOT NULL DEFAULT '',     -- entry_hash of last event
    created_ts      REAL NOT NULL,
    terminated_ts   REAL
);
CREATE INDEX IF NOT EXISTS ix_worlds_session ON worlds(session_id);
CREATE INDEX IF NOT EXISTS ix_worlds_client ON worlds(client_id);
CREATE INDEX IF NOT EXISTS ix_worlds_parent ON worlds(parent_world_id);

-- Per-world hash-chained, append-only event ledger. (world_id, world_index) is
-- the position in that world's chain; prev_hash/entry_hash chain it. A fork
-- child continues the chain from the parent's fork_point entry (recorded in the
-- child's first event's prev_hash), so the shared prefix is the PARENT's rows,
-- immutable and never copied -- parent and child cannot mutate one another.
CREATE TABLE IF NOT EXISTS events (
    event_seq    INTEGER PRIMARY KEY AUTOINCREMENT,   -- global order
    event_id     TEXT NOT NULL UNIQUE,
    world_id     TEXT NOT NULL REFERENCES worlds(world_id),
    world_index  INTEGER NOT NULL,
    event_type   TEXT NOT NULL,
    ts           REAL NOT NULL,
    actor        TEXT NOT NULL,
    payload      TEXT NOT NULL,        -- canonical JSON
    refs         TEXT NOT NULL,        -- canonical JSON
    causal       TEXT NOT NULL,        -- canonical JSON list of parent event_ids
    artifacts    TEXT NOT NULL,        -- canonical JSON list of blob hashes
    prev_hash    TEXT NOT NULL,
    entry_hash   TEXT NOT NULL,
    schema_ver   INTEGER NOT NULL,
    UNIQUE (world_id, world_index)
);
CREATE INDEX IF NOT EXISTS ix_events_world ON events(world_id, world_index);
CREATE INDEX IF NOT EXISTS ix_events_type ON events(world_id, event_type);

-- Foundry/client/session lifecycle events (a separate global audit chain).
CREATE TABLE IF NOT EXISTS foundry_events (
    seq         INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id    TEXT NOT NULL UNIQUE,
    event_type  TEXT NOT NULL,
    ts          REAL NOT NULL,
    actor       TEXT NOT NULL,
    scope_kind  TEXT NOT NULL,
    scope_id    TEXT NOT NULL,
    payload     TEXT NOT NULL,
    prev_hash   TEXT NOT NULL,
    entry_hash  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS work_items (
    work_id       TEXT PRIMARY KEY,
    world_id      TEXT NOT NULL REFERENCES worlds(world_id),
    kind          TEXT NOT NULL,
    payload       TEXT NOT NULL,
    status        TEXT NOT NULL DEFAULT 'QUEUED'
                  CHECK (status IN ('QUEUED','CLAIMED','RUNNING','COMPLETED',
                                    'FAILED','EXPIRED','RETRYABLE','CANCELLED')),
    priority      INTEGER NOT NULL DEFAULT 100,
    attempts      INTEGER NOT NULL DEFAULT 0,
    max_attempts  INTEGER NOT NULL DEFAULT 3,
    dedup_key     TEXT,
    claimed_by    TEXT,
    lease_expires REAL,
    heartbeat_ts  REAL,
    result        TEXT,
    result_hash   TEXT,
    error         TEXT,
    created_ts    REAL NOT NULL,
    updated_ts    REAL NOT NULL,
    completed_ts  REAL,
    UNIQUE (world_id, dedup_key)
);
CREATE INDEX IF NOT EXISTS ix_work_claimable
    ON work_items(world_id, status, priority, created_ts);
CREATE INDEX IF NOT EXISTS ix_work_lease ON work_items(status, lease_expires);

CREATE TABLE IF NOT EXISTS hypotheses (
    hyp_id      TEXT PRIMARY KEY,
    world_id    TEXT NOT NULL REFERENCES worlds(world_id),
    statement   TEXT NOT NULL,
    state       TEXT NOT NULL DEFAULT 'PROPOSED'
                CHECK (state IN ('PROPOSED','PREDICTED','TESTED','FALSIFIED',
                                 'SURVIVED','UPDATED')),
    content_hash TEXT NOT NULL,
    created_ts  REAL NOT NULL,
    created_seq INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_hyp_world ON hypotheses(world_id);

CREATE TABLE IF NOT EXISTS predictions (
    pred_id      TEXT PRIMARY KEY,
    world_id     TEXT NOT NULL REFERENCES worlds(world_id),
    hyp_id       TEXT NOT NULL REFERENCES hypotheses(hyp_id),
    content      TEXT NOT NULL,
    content_hash TEXT NOT NULL,       -- SEALED at registration; immutable
    created_ts   REAL NOT NULL,
    created_seq  INTEGER NOT NULL,    -- the event_seq at registration (ordering)
    state        TEXT NOT NULL DEFAULT 'REGISTERED'
                 CHECK (state IN ('REGISTERED','OBSERVED'))
);
CREATE INDEX IF NOT EXISTS ix_pred_world ON predictions(world_id);
CREATE INDEX IF NOT EXISTS ix_pred_hyp ON predictions(hyp_id);

CREATE TABLE IF NOT EXISTS experiments (
    exp_id      TEXT PRIMARY KEY,
    world_id    TEXT NOT NULL REFERENCES worlds(world_id),
    hyp_id      TEXT REFERENCES hypotheses(hyp_id),
    pred_id     TEXT REFERENCES predictions(pred_id),
    spec        TEXT NOT NULL,
    spec_hash   TEXT NOT NULL,
    work_id     TEXT REFERENCES work_items(work_id),
    state       TEXT NOT NULL DEFAULT 'CREATED'
                CHECK (state IN ('CREATED','RUNNING','OBSERVED','ABANDONED')),
    created_ts  REAL NOT NULL,
    created_seq INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_exp_world ON experiments(world_id);

CREATE TABLE IF NOT EXISTS observations (
    obs_id       TEXT PRIMARY KEY,
    world_id     TEXT NOT NULL REFERENCES worlds(world_id),
    exp_id       TEXT NOT NULL REFERENCES experiments(exp_id),
    pred_id      TEXT REFERENCES predictions(pred_id),
    content      TEXT NOT NULL,
    outcome      TEXT NOT NULL
                 CHECK (outcome IN ('FALSIFIED','SURVIVED','INCONCLUSIVE')),
    created_ts   REAL NOT NULL,
    created_seq  INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_obs_world ON observations(world_id);
CREATE INDEX IF NOT EXISTS ix_obs_exp ON observations(exp_id);

CREATE TABLE IF NOT EXISTS failures (
    failure_id       TEXT PRIMARY KEY,
    world_id         TEXT NOT NULL REFERENCES worlds(world_id),
    experiment_id    TEXT REFERENCES experiments(exp_id),
    hypothesis_id    TEXT REFERENCES hypotheses(hyp_id),
    prediction_id    TEXT REFERENCES predictions(pred_id),
    failure_type     TEXT NOT NULL,
    reference        TEXT NOT NULL,
    expected         TEXT NOT NULL,
    observed         TEXT NOT NULL,
    falsifier        TEXT NOT NULL,
    violated         TEXT NOT NULL,
    measurement_id   TEXT REFERENCES measurements(measurement_id),
    artifact_refs    TEXT NOT NULL,
    reproducibility  TEXT NOT NULL DEFAULT 'UNKNOWN'
                     CHECK (reproducibility IN ('BIT_DETERMINISTIC',
                        'SEMANTIC','PARTIAL','NONDETERMINISTIC','UNKNOWN')),
    extensions       TEXT NOT NULL,
    created_ts       REAL NOT NULL,
    created_seq      INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_fail_world ON failures(world_id);
CREATE INDEX IF NOT EXISTS ix_fail_type ON failures(world_id, failure_type);

-- The recorded reference DAG. Edges are the ONLY source of lineage -- never
-- reconstructed after the fact.
CREATE TABLE IF NOT EXISTS lineage_edges (
    edge_id     TEXT PRIMARY KEY,
    world_id    TEXT NOT NULL REFERENCES worlds(world_id),
    src_kind    TEXT NOT NULL,
    src_id      TEXT NOT NULL,
    dst_kind    TEXT NOT NULL,
    dst_id      TEXT NOT NULL,
    relation    TEXT NOT NULL,
    claimed     INTEGER NOT NULL DEFAULT 1,   -- 1 = agent-claimed reference
    created_ts  REAL NOT NULL,
    created_seq INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_edge_src ON lineage_edges(world_id, src_kind, src_id);
CREATE INDEX IF NOT EXISTS ix_edge_dst ON lineage_edges(world_id, dst_kind, dst_id);

CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id    TEXT PRIMARY KEY,      -- content address
    world_id       TEXT NOT NULL REFERENCES worlds(world_id),
    kind           TEXT NOT NULL,
    blob_hash      TEXT NOT NULL,
    meta           TEXT NOT NULL,
    origin         TEXT NOT NULL DEFAULT 'NATIVE'
                   CHECK (origin IN ('NATIVE','IMPORTED')),
    source_world   TEXT,
    source_artifact TEXT,
    import_seq     INTEGER,
    created_ts     REAL NOT NULL,
    created_seq    INTEGER NOT NULL,
    UNIQUE (world_id, artifact_id)
);
CREATE INDEX IF NOT EXISTS ix_art_world ON artifacts(world_id);

CREATE TABLE IF NOT EXISTS budgets (
    world_id    TEXT PRIMARY KEY REFERENCES worlds(world_id),
    limits      TEXT NOT NULL,        -- {resource: {limit, enforcement}}
    consumed    TEXT NOT NULL,        -- {resource: amount}
    exhausted   INTEGER NOT NULL DEFAULT 0,
    updated_ts  REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    world_id      TEXT NOT NULL REFERENCES worlds(world_id),
    world_index   INTEGER NOT NULL,    -- chain position captured
    head_hash     TEXT NOT NULL,
    state_hash    TEXT NOT NULL,       -- content hash of captured world state
    meta          TEXT NOT NULL,
    created_ts    REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_ckp_world ON checkpoints(world_id);

CREATE TABLE IF NOT EXISTS measurements (
    measurement_id  TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    version         TEXT NOT NULL,
    implementation_hash TEXT NOT NULL,
    params          TEXT NOT NULL,
    domain          TEXT NOT NULL,
    inputs          TEXT NOT NULL,
    outputs         TEXT NOT NULL,
    provenance      TEXT NOT NULL,
    validation_status TEXT NOT NULL DEFAULT 'UNVALIDATED'
                    CHECK (validation_status IN ('UNVALIDATED','VALIDATED',
                                                 'DEPRECATED')),
    created_ts      REAL NOT NULL,
    UNIQUE (name, version)
);
"""


class Store:
    """A per-thread connection to the Gen-2 database. Open one per worker."""

    def __init__(self, db_path: str, *, timeout: float = 30.0):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.blobs_dir = Path(self.db_path).parent / "blobs"
        self.blobs_dir.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, timeout=timeout,
                                     isolation_level=None,  # explicit txns
                                     check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._conn.execute(f"PRAGMA busy_timeout={int(timeout * 1000)}")

    # -- schema ------------------------------------------------------------
    def initialize(self) -> None:
        # executescript() COMMITs any pending transaction, so the DDL runs in
        # autocommit (outside our write() wrapper). CREATE TABLE IF NOT EXISTS
        # makes this idempotent and safe for many processes opening the same db.
        self._conn.executescript(_SCHEMA)
        with self.write() as cx:
            row = cx.execute(
                "SELECT value FROM meta WHERE key='schema_version'").fetchone()
            if row is None:
                cx.execute("INSERT INTO meta(key,value) VALUES(?,?)",
                           ("schema_version", str(SCHEMA_VERSION)))
            elif int(row["value"]) != SCHEMA_VERSION:
                raise RuntimeError(
                    f"db schema version {row['value']} != {SCHEMA_VERSION}; "
                    f"refusing to run against a mismatched database")

    # -- transactions ------------------------------------------------------
    @contextlib.contextmanager
    def write(self) -> Iterator[sqlite3.Connection]:
        """A write transaction. BEGIN IMMEDIATE takes the write lock up front,
        so a read-then-write (e.g. claim a work item) is atomic against other
        writers -- the single most important property for the work queue."""
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            yield self._conn
            self._conn.execute("COMMIT")
        except Exception:
            self._conn.execute("ROLLBACK")
            raise

    def read(self) -> sqlite3.Connection:
        return self._conn

    # -- blobs -------------------------------------------------------------
    def put_blob(self, data: bytes) -> str:
        from sfe.ids import blob_hash
        h = blob_hash(data)
        path = self.blobs_dir / h.replace(":", "_")
        if not path.exists():
            tmp = path.with_suffix(f".tmp.{time.time_ns()}")
            tmp.write_bytes(data)
            import os
            os.replace(tmp, path)         # atomic publish
        return h

    def get_blob(self, h: str) -> bytes:
        from sfe.ids import blob_hash
        path = self.blobs_dir / h.replace(":", "_")
        data = path.read_bytes()
        if blob_hash(data) != h:          # verify on read
            raise RuntimeError(f"blob {h} failed content verification")
        return data

    def close(self) -> None:
        with contextlib.suppress(Exception):
            self._conn.close()


def now() -> float:
    return time.time()
