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

SCHEMA_VERSION = 7

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
    created_ts  REAL NOT NULL,
    -- session affinity (v5): the key is bearer-like, so only its SHA-256 is
    -- stored; engine_instance_id is the binding a router will later use to
    -- answer "which SFE instance owns this experiment?".
    key_hash            TEXT,
    engine_instance_id  TEXT,
    affinity_mode       TEXT NOT NULL DEFAULT 'STRICT'
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
    require_attestation INTEGER NOT NULL DEFAULT 0,
                                        -- 1 = observations in this world MUST
                                        -- carry a work_id (ENGINE_WORK_RESULT);
                                        -- set at creation, immutable after
    budget_root     TEXT,               -- world whose budget row is AUTHORITATIVE
                                        -- for this lineage (self for roots; a
                                        -- fork child inherits the parent's root
                                        -- so forking cannot mint fresh budget)
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
    claim_id      TEXT,                -- server-issued FENCING token for the
                                       -- current claim attempt; cleared on
                                       -- reclaim so a stale attempt can never
                                       -- complete the current one
    lease_expires REAL,
    heartbeat_ts  REAL,
    result        TEXT,
    result_hash   TEXT,
    -- v6 EXECUTED-side attestation. The engine holds the REQUESTED config
    -- (spec_hash, sealed at commit); these are what the executor says it
    -- ACTUALLY ran. Divergence is then a hash comparison, not a judgement.
    executed_config_hash      TEXT,
    entry_state_hash          TEXT,
    player_identity_hash      TEXT,
    measurement_identity_hash TEXT,
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
    committed_seq INTEGER,             -- event_seq of EXPERIMENT_COMMITTED: the
                                       -- irreversible boundary that freezes the
                                       -- prospective-prediction window, debits
                                       -- budget and authorizes execution.
                                       -- NULL = REGISTERED (non-executable).
    committed_ts  REAL,
    -- v6: for kind='analysis'. unit_of_analysis is DECLARED by the analyst and
    -- VERIFIED by the engine -- counting distinct units under a declared key is
    -- counting, not statistics, and it is what turns 128 observations over 8
    -- worlds from n=128 into n=8.
    unit_of_analysis TEXT,
    declared_n       INTEGER,
    source_set_hash  TEXT,
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
    pred_prospective INTEGER,          -- 1 iff the bound prediction preceded the
                                       -- experiment's COMMIT (mechanical; NULL
                                       -- when no prediction is bound)
    evidence_class TEXT NOT NULL DEFAULT 'CLIENT_ASSERTED'
                 CHECK (evidence_class IN ('ENGINE_WORK_RESULT',
                                           'CLIENT_ASSERTED')),
    evidence_role TEXT NOT NULL DEFAULT 'ORIGINAL'   -- F3: the FIRST observation
                 CHECK (evidence_role IN ('ORIGINAL', 'REPLICATION')),
                                       -- bound to a prediction is ORIGINAL and
                                       -- fixes its adjudication; a later binding
                                       -- must be an explicit REPLICATION and can
                                       -- never improve the original's status.
    work_id      TEXT REFERENCES work_items(work_id),
    created_ts   REAL NOT NULL,
    created_seq  INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_obs_world ON observations(world_id);
CREATE INDEX IF NOT EXISTS ix_obs_pred ON observations(world_id, pred_id);
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

-- Registered cross-client sharing groups (H5). A group id is a server-issued
-- UNGUESSABLE capability: two clients share it only by deliberate transfer, so
-- matching topology_group strings alone can never manufacture "bilateral
-- consent" -- the group must exist here for a cross-client crossing.
-- v6 SCIENTIFIC PROVENANCE.
--
-- families is the FIRST cross-world scientific container. Every other
-- scientific table carries world_id NOT NULL, which is correct for a ledger
-- but makes a campaign, an analysis family or a comparison family
-- inexpressible: they span worlds by definition. Without this, a selected
-- survivor cannot be attached to the alternatives it was selected from, which
-- is the provenance that makes best-of-N visible.
CREATE TABLE IF NOT EXISTS families (
    family_id     TEXT PRIMARY KEY,
    client_id     TEXT NOT NULL REFERENCES clients(client_id),
    kind          TEXT NOT NULL,          -- campaign | analysis | comparison
    manifest      TEXT NOT NULL,          -- DECLARED intended extent (freeform)
    manifest_hash TEXT NOT NULL,          -- sealed at creation, immutable
    state         TEXT NOT NULL DEFAULT 'OPEN'
                  CHECK (state IN ('OPEN','CLOSED')),
    created_ts    REAL NOT NULL
);

-- world_id is NULLABLE here ON PURPOSE: a member may be an analysis or a claim
-- that belongs to no single world. This is the whole point of the table.
CREATE TABLE IF NOT EXISTS family_members (
    family_id   TEXT NOT NULL REFERENCES families(family_id),
    member_kind TEXT NOT NULL,            -- experiment | analysis | world | claim
    member_id   TEXT NOT NULL,
    world_id    TEXT,
    role        TEXT,                     -- planned | executed | abandoned
    -- v7 ARM RULING. The arm is part of the sealed experimental DESIGN, not of
    -- the execution. It lives here rather than in experiments.spec precisely
    -- so that two members in different arms can carry an IDENTICAL execution
    -- spec_hash: what was RUN and what ROLE it played are different facts, and
    -- folding the label into the spec would make identical executions hash
    -- differently and destroy the comparison it exists to support.
    -- Append-only, like role: reassignment after commitment is a 409.
    arm         TEXT,
    created_ts  REAL NOT NULL,
    PRIMARY KEY (family_id, member_kind, member_id)
);
CREATE INDEX IF NOT EXISTS ix_family_members ON family_members(family_id, role);

-- A claim is the scientific assertion. It is deliberately NOT a world record:
-- it cites analyses, which cite observations, which live in worlds.
CREATE TABLE IF NOT EXISTS claims (
    claim_id        TEXT PRIMARY KEY,
    client_id       TEXT NOT NULL REFERENCES clients(client_id),
    family_id       TEXT REFERENCES families(family_id),
    analysis_exp_id TEXT,                 -- the kind='analysis' experiment
    analysis_world_id TEXT,
    estimand        TEXT NOT NULL,
    -- SUCCESSFUL_NEGATIVE exists because "the effect is bounded below a
    -- declared relevance floor" is a POSITIVE result, and collapsing it into
    -- INCONCLUSIVE destroys exactly the information that makes it valuable.
    -- The engine stores the conclusion; it does not judge the equivalence test.
    status          TEXT NOT NULL
                    CHECK (status IN ('SUPPORTED','SUCCESSFUL_NEGATIVE',
                                      'INCONCLUSIVE','RETRACTED')),
    relevance_floor TEXT,
    replication     TEXT,                 -- COMPOSITIONAL dict, never an ordinal
    transport_domain TEXT,
    content_hash    TEXT NOT NULL,
    created_ts      REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_claims_family ON claims(family_id);

CREATE TABLE IF NOT EXISTS topology_groups (
    group_id    TEXT PRIMARY KEY,
    created_by  TEXT NOT NULL REFERENCES clients(client_id),
    note        TEXT,
    created_ts  REAL NOT NULL
);

-- v7 CROSS-SEAT READ CONTRACT.
--
-- Every read route in this engine is owner-scoped, which is correct (I5) and
-- which made a whole class of consumer impossible: an ARCHAEOLOGIST that mines
-- another seat's executed record cannot see a single row, and its only recourse
-- was to open the SQLite file off disk -- a read with no tenancy filter, no
-- evidence-class filter, no schema guard and no contract at all.
--
-- A grant is scoped to a TOPOLOGY GROUP rather than to a client or a world.
-- The group id is already a server-issued unguessable capability (H5) that two
-- clients can only come to share by deliberate out-of-band transfer, so
-- string-guessing can never manufacture consent. Reusing it means the grant
-- names a set the granter has already had to curate deliberately.
--
-- READ ONLY, and only ever read: a grant confers no write, no claim, no work,
-- no budget. It is revocable, and revocation is recorded rather than deleted.
-- A READ SCOPE is a curated set of the owner's OWN worlds that exists only to
-- be granted for reading.
--
-- The first cut scoped grants to a topology_group, and that was wrong. A
-- topology group is a SHARING capability: _may_cross requires the destination
-- and source worlds to share one, so granting read over a group would make a
-- read grant confer artifact-IMPORT eligibility as a side effect. Worse, the
-- corpus that actually needs granting is 189 already-existing worlds -- 98 of
-- them in no group at all and the rest scattered over ~40 -- so using groups
-- would have meant MUTATING topology_group on live worlds, which is the one
-- field that changes what may cross between them.
--
-- A read scope touches none of that. It confers read and nothing else.
CREATE TABLE IF NOT EXISTS read_scopes (
    scope_id        TEXT PRIMARY KEY,
    owner_client_id TEXT NOT NULL REFERENCES clients(client_id),
    name            TEXT NOT NULL,
    note            TEXT,
    created_ts      REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_read_scopes_owner
    ON read_scopes(owner_client_id);

CREATE TABLE IF NOT EXISTS read_scope_worlds (
    scope_id   TEXT NOT NULL REFERENCES read_scopes(scope_id),
    world_id   TEXT NOT NULL REFERENCES worlds(world_id),
    added_ts   REAL NOT NULL,
    PRIMARY KEY (scope_id, world_id)
);

CREATE TABLE IF NOT EXISTS read_grants (
    grant_id          TEXT PRIMARY KEY,
    scope_id          TEXT NOT NULL REFERENCES read_scopes(scope_id),
    grantee_client_id TEXT NOT NULL REFERENCES clients(client_id),
    granted_by        TEXT NOT NULL REFERENCES clients(client_id),
    note              TEXT,
    created_ts        REAL NOT NULL,
    revoked_ts        REAL,
    UNIQUE (scope_id, grantee_client_id)
);
CREATE INDEX IF NOT EXISTS ix_read_grants_grantee
    ON read_grants(grantee_client_id, revoked_ts);

-- F5: request-identity idempotency for epistemic writes. A key is scoped to the
-- issuing client; request_hash binds the SEMANTIC request (route + world +
-- canonical body), so the same key with a materially different request is a
-- conflict, never a silent dedup. The response is stored so a transport retry
-- replays the SAME logical result. The row is written in the SAME transaction as
-- the epistemic object, so exactly-once holds across process restart: either the
-- object and its key committed together, or neither did.
CREATE TABLE IF NOT EXISTS idempotency_keys (
    client_id     TEXT NOT NULL REFERENCES clients(client_id),
    idem_key      TEXT NOT NULL,
    world_id      TEXT,
    route         TEXT NOT NULL,
    request_hash  TEXT NOT NULL,
    response      TEXT NOT NULL,      -- canonical JSON of the stored result
    created_ts    REAL NOT NULL,
    PRIMARY KEY (client_id, idem_key)
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
    -- v7: WHERE the value is, and WHAT IT MEANS.
    --
    -- observations.content is freeform by design, so nothing said which field
    -- of it was the outcome. That is the exact gap behind "computing a
    -- variance requires knowing which field is the outcome" -- the reason the
    -- engine declines to compute one. A DECLARED path does not make the engine
    -- a statistician: it makes locating the value a lookup instead of a guess,
    -- and it is the difference between an analyst reading the right column and
    -- reading a plausible one.
    value_path      TEXT,          -- dotted path into observations.content
    direction       TEXT           -- HIGHER_IS_BETTER | LOWER_IS_BETTER |
                    CHECK (direction IS NULL OR direction IN
                           ('HIGHER_IS_BETTER','LOWER_IS_BETTER','NEITHER')),
    unit            TEXT,
    range_min       REAL,
    range_max       REAL,
    identity_hash   TEXT,          -- canonical id of the DEFINITION (v7)
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
        # FAST PATH, and it is not an optimization -- it is an availability
        # fix (D-LOCK-1, 2026-09-06).
        #
        # api.get_foundry() builds a fresh Foundry PER REQUEST, and this method
        # used to open `with self.write()` unconditionally. write() issues
        # BEGIN IMMEDIATE, which takes SQLite's EXCLUSIVE WRITE LOCK. So every
        # request -- including unauthenticated read-only ones like
        # GET /v2/version -- queued behind every writer, purely to re-read one
        # row of `meta`. WAL gives concurrent readers, and the engine was
        # throwing that away on the first line of every request.
        #
        # Measured on the live M1 service before this fix, with one ordinary
        # consumer writing: GET /v2/version 22.8s and 17.6s against a 30s
        # busy_timeout, while GET /v2/openapi.json -- same process, same TLS,
        # no db dependency -- stayed at 18ms. Three consumers now share this
        # engine, so the tail was heading for the timeout, not merely for slow.
        #
        # The already-current case is every case except a genuine migration, so
        # settle it with a PLAIN READ and take no lock at all. Correctness is
        # unchanged: a schema at the current version has, by construction,
        # already run _SCHEMA and every migration, and the slow path below
        # still serializes real migrations behind BEGIN IMMEDIATE.
        try:
            row = self._conn.execute(
                "SELECT value FROM meta WHERE key='schema_version'").fetchone()
            if row is not None and int(row["value"]) == SCHEMA_VERSION:
                return
        except sqlite3.OperationalError:
            pass          # no meta table yet -- brand new db, full path below
        except (TypeError, ValueError):
            pass          # unparseable version -- let the slow path judge it

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
                return
            have = int(row["value"])
            if have == SCHEMA_VERSION:
                return
            if have > SCHEMA_VERSION:
                raise RuntimeError(
                    f"db schema version {have} is NEWER than this engine's "
                    f"{SCHEMA_VERSION}; refusing to run (would misread state)")
            if have <= 1:
                self._migrate_1_to_2(cx)
            if have <= 2:
                self._migrate_2_to_3(cx)
            if have <= 3:
                self._migrate_3_to_4(cx)
            if have <= 4:
                self._migrate_4_to_5(cx)
            if have <= 5:
                self._migrate_5_to_6(cx)
            if have <= 6:
                self._migrate_6_to_7(cx)
            cx.execute("UPDATE meta SET value=? WHERE key='schema_version'",
                       (str(SCHEMA_VERSION),))

    @staticmethod
    def _migrate_1_to_2(cx) -> None:
        """v1 -> v2: the requalification-hardening columns. Additive only; no
        rows are rewritten except the budget_root backfill. Pre-v2 worlds become
        their OWN budget root (their historical world-local semantics are
        preserved, never silently reinterpreted); lineage budget inheritance
        applies to forks created from v2 onward."""
        have = {r["name"] for r in cx.execute(
            "PRAGMA table_info(worlds)").fetchall()}
        if "budget_root" not in have:
            cx.execute("ALTER TABLE worlds ADD COLUMN budget_root TEXT")
        have = {r["name"] for r in cx.execute(
            "PRAGMA table_info(work_items)").fetchall()}
        if "claim_id" not in have:
            cx.execute("ALTER TABLE work_items ADD COLUMN claim_id TEXT")
        have = {r["name"] for r in cx.execute(
            "PRAGMA table_info(experiments)").fetchall()}
        if "committed_seq" not in have:
            cx.execute("ALTER TABLE experiments ADD COLUMN committed_seq INTEGER")
            cx.execute("ALTER TABLE experiments ADD COLUMN committed_ts REAL")
        have = {r["name"] for r in cx.execute(
            "PRAGMA table_info(observations)").fetchall()}
        if "evidence_class" not in have:
            cx.execute("ALTER TABLE observations ADD COLUMN "
                       "pred_prospective INTEGER")
            cx.execute("ALTER TABLE observations ADD COLUMN evidence_class "
                       "TEXT NOT NULL DEFAULT 'CLIENT_ASSERTED'")
            cx.execute("ALTER TABLE observations ADD COLUMN work_id TEXT")
        cx.execute("UPDATE worlds SET budget_root=world_id "
                   "WHERE budget_root IS NULL")

    @staticmethod
    def _migrate_2_to_3(cx) -> None:
        """v2 -> v3 (GEN-2.1). Additive: observations.evidence_role and the
        idempotency_keys table. Pre-v3 observations become ORIGINAL -- they were
        recorded under the old semantics; any historical DUPLICATE prospective
        bindings are honestly left as legacy (all ORIGINAL), NOT retroactively
        relabelled REPLICATION (invariant V: old events remain old events)."""
        have = {r["name"] for r in cx.execute(
            "PRAGMA table_info(observations)").fetchall()}
        if "evidence_role" not in have:
            cx.execute("ALTER TABLE observations ADD COLUMN evidence_role "
                       "TEXT NOT NULL DEFAULT 'ORIGINAL'")
        cx.execute(
            "CREATE TABLE IF NOT EXISTS idempotency_keys ("
            "client_id TEXT NOT NULL, idem_key TEXT NOT NULL, world_id TEXT, "
            "route TEXT NOT NULL, request_hash TEXT NOT NULL, "
            "response TEXT NOT NULL, created_ts REAL NOT NULL, "
            "PRIMARY KEY (client_id, idem_key))")

    @staticmethod
    def _migrate_3_to_4(cx) -> None:
        """v3 -> v4 (DAEDALUS 2026-09-04, orchestration-safety pass). Additive:
        worlds.require_attestation. Pre-v4 worlds default to 0 -- attestation
        stays OPTIONAL for every world that already exists, because retro-
        actively requiring it would reclassify historical CLIENT_ASSERTED
        observations that were legitimately recorded under the old contract
        (invariant V: old events remain old events). A world opts in at
        creation; the flag is immutable thereafter."""
        have = {r["name"] for r in cx.execute(
            "PRAGMA table_info(worlds)").fetchall()}
        if "require_attestation" not in have:
            cx.execute("ALTER TABLE worlds ADD COLUMN require_attestation "
                       "INTEGER NOT NULL DEFAULT 0")
        cx.execute("CREATE INDEX IF NOT EXISTS ix_obs_pred "
                   "ON observations(world_id, pred_id)")

    @staticmethod
    def _migrate_6_to_7(cx) -> None:
        """v6 -> v7 (2026-09-06): the cross-seat read contract and
        measurement meaning.

        Purely additive, and NOTHING is back-filled. read_grants starts empty
        because no grant has ever been made, and every pre-v7 measurement has a
        NULL value_path because nobody was ever asked for one -- inventing a
        path would assert where a value lives on evidence nobody supplied,
        which is the same reasoning that left v5 sessions LEGACY and v6
        attestations NULL."""
        have = {r["name"] for r in cx.execute(
            "PRAGMA table_info(family_members)").fetchall()}
        if "arm" not in have:
            cx.execute("ALTER TABLE family_members ADD COLUMN arm TEXT")
        have = {r["name"] for r in cx.execute(
            "PRAGMA table_info(measurements)").fetchall()}
        for col, typ in (("value_path", "TEXT"), ("direction", "TEXT"),
                         ("unit", "TEXT"), ("range_min", "REAL"),
                         ("range_max", "REAL"), ("identity_hash", "TEXT")):
            if col not in have:
                cx.execute("ALTER TABLE measurements ADD COLUMN %s %s"
                           % (col, typ))

    @staticmethod
    def _migrate_5_to_6(cx) -> None:
        """v5 -> v6 (DAEDALUS 2026-09-05, scientific-provenance point release).

        Purely additive. The new tables are created by the schema script; this
        adds columns to existing tables. NOTHING is back-filled: a pre-v6 work
        item has NULL attestation hashes because no executor ever attested
        anything, and inventing a value would manufacture a provenance claim
        that was never made -- the same reasoning as the v5 LEGACY sessions."""
        have = {r["name"] for r in cx.execute(
            "PRAGMA table_info(work_items)").fetchall()}
        for col in ("executed_config_hash", "entry_state_hash",
                    "player_identity_hash", "measurement_identity_hash"):
            if col not in have:
                cx.execute("ALTER TABLE work_items ADD COLUMN %s TEXT" % col)
        have = {r["name"] for r in cx.execute(
            "PRAGMA table_info(experiments)").fetchall()}
        if "unit_of_analysis" not in have:
            cx.execute("ALTER TABLE experiments ADD COLUMN unit_of_analysis TEXT")
            cx.execute("ALTER TABLE experiments ADD COLUMN declared_n INTEGER")
            cx.execute("ALTER TABLE experiments ADD COLUMN source_set_hash TEXT")

    @staticmethod
    def _migrate_4_to_5(cx) -> None:
        """v4 -> v5 (DAEDALUS 2026-09-05, session affinity). Additive:
        sessions.key_hash / .engine_instance_id / .affinity_mode.

        Sessions that already exist get affinity_mode='LEGACY' with a NULL
        key_hash and a NULL engine_instance_id. THIS IS DELIBERATE AND IT IS
        THE HONEST OPTION: those sessions were created before affinity existed,
        so no session key was ever issued for them and no engine binding was
        ever recorded. Back-filling this engine's instance id onto them would
        MANUFACTURE A PROVENANCE CLAIM THAT WAS NEVER MADE -- it would assert
        that this engine is where they were created, which happens to be true
        on M1 today and would become false the moment a database is restored
        elsewhere. A NULL says "unknown", which is what we actually know.

        LEGACY sessions keep working without a key (a mandatory key would
        strand 106 sessions and 346 worlds). They are visibly marked, counted
        at startup, and can never be silently mistaken for bound sessions:
        every response about them carries affinity_mode, and the strict-mode
        cutover is a single flag, not a rewrite."""
        have = {r["name"] for r in cx.execute(
            "PRAGMA table_info(sessions)").fetchall()}
        if "key_hash" not in have:
            cx.execute("ALTER TABLE sessions ADD COLUMN key_hash TEXT")
        if "engine_instance_id" not in have:
            cx.execute("ALTER TABLE sessions ADD COLUMN engine_instance_id TEXT")
        if "affinity_mode" not in have:
            # every pre-existing row becomes LEGACY; new rows are written STRICT
            cx.execute("ALTER TABLE sessions ADD COLUMN affinity_mode TEXT "
                       "NOT NULL DEFAULT 'LEGACY'")
        cx.execute("CREATE INDEX IF NOT EXISTS ix_sessions_keyhash "
                   "ON sessions(key_hash)")

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
