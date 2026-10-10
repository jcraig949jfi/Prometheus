"""The Moonshot PostgreSQL publication layer (C-012-T002; contract INTERFACE_CONTRACT.md s4-s5).

Every guard lives in the database (schema.sql). This module connects through the program's credential resolver
and identity guard (as fabric.store does), creates the versioned schema and its NOLOGIN roles, and exposes a
`Moonshot` handle bound to ONE role: a publisher can only publish, a validator only validate, a resolver only
resolve. While program logins are superuser (INTERFACE_CONTRACT s5) that separation contains bugs; with per-role
logins it becomes a boundary without a code change.

Semantic verification (work_id / epoch_digest recomputed from canonical bytes, the derived spec) runs here before
`publish`; the database independently checks every byte hash, the manifest's position and the lineage guard."""
import hashlib
import json
import re
import sys
import time
from pathlib import Path

from moonshot.epoch import canonical as C
from moonshot.epoch import model

SCHEMA_VERSION = 1
ROLES = ("reader", "coordinator", "publisher", "validator", "resolver")
GRANTS = {
    "coordinator": ["create_chain(text, text, bytea, bytea, jsonb, text, integer, text)", "put_object(bytea)",
                    "record_receipt(text, bytea, text)", "record_materialization(jsonb, text)"],
    "publisher": ["publish(text, text, text, integer, text, bigint, bytea, bytea, bytea, bytea, jsonb, text)",
                  "record_attempt_outcome(text, text, text, integer, text, bigint, text, text, text, jsonb, text)",
                  "put_object(bytea)"],
    "validator": ["record_validation(text, integer, text, text, text[], text, text, text)"],
    "resolver": ["resolve_contest(bigint, text[], boolean, text)"],
}
REPO = Path(__file__).resolve().parents[2]
_NAME = re.compile(r"^[a-z][a-z0-9_]{0,40}$")
HOLD_LOCK_CLASS = 4242                       # advisory-lock key class used only by the crash tests' hold point


def _check(schema):
    if not _NAME.match(schema or ""):
        raise ValueError("unsafe schema name {!r}".format(schema))


def hold_key(schema):
    return int(hashlib.sha256(schema.encode()).hexdigest()[:7], 16)


def connect(pooled=False):
    """The canonical store through comms's resolver and identity guard: a wrong cluster fails closed.

    DEDICATED (non-pooled) by default. evidence_wiki's pool returns connections to the pool with their session
    state intact (found 2026-10-10: a handle's SET ROLE leaked into the next borrower), and a Moonshot handle
    always sets a role, so it must never share a pooled session."""
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from evidence_wiki.ew import db as ewdb
    from comms import identity
    if pooled:
        conn = ewdb.connect()
    else:
        import psycopg2
        conn = psycopg2.connect(**ewdb._conn_kwargs(ewdb.load_config()))
    try:
        identity.require(conn, identity.current_environment())
    except identity.WrongEnvironment:
        conn.close()
        raise
    return conn


def init_schema(conn, schema="moonshot"):
    """Create (idempotently) the roles, the schema owned by <schema>_owner, its tables and functions, and the
    grants: PUBLIC gets nothing; each functional role USAGE + SELECT + EXECUTE on exactly its functions."""
    _check(schema)
    cur = conn.cursor()
    for role in ("owner",) + ROLES:
        r = "{}_{}".format(schema, role)
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (r,))
        if cur.fetchone() is None:
            cur.execute("CREATE ROLE {} NOLOGIN".format(r))
    cur.execute("CREATE SCHEMA IF NOT EXISTS {s} AUTHORIZATION {s}_owner".format(s=schema))
    cur.execute("SET ROLE {}_owner".format(schema))
    cur.execute(Path(__file__).with_name("schema.sql").read_text(encoding="utf-8").replace("{schema}", schema))
    cur.execute("RESET ROLE")
    for kind in ("SCHEMA {s}", "ALL TABLES IN SCHEMA {s}", "ALL SEQUENCES IN SCHEMA {s}", "ALL FUNCTIONS IN SCHEMA {s}"):
        cur.execute(("REVOKE ALL ON " + kind + " FROM PUBLIC").format(s=schema))
    for role in ROLES:
        r = "{}_{}".format(schema, role)
        cur.execute("GRANT USAGE ON SCHEMA {} TO {}".format(schema, r))
        cur.execute("GRANT SELECT ON ALL TABLES IN SCHEMA {} TO {}".format(schema, r))
    for role, fns in GRANTS.items():
        for fn in fns:
            cur.execute("GRANT EXECUTE ON FUNCTION {}.{} TO {}_{}".format(schema, fn, schema, role))
    conn.commit()


def drop_schema(conn, schema, force=False):
    """Tests only: drop a throwaway schema and its roles. The production schema needs force=True."""
    _check(schema)
    if schema == "moonshot" and not force:
        raise ValueError("refusing to drop the production schema without force=True")
    conn.rollback()
    cur = conn.cursor()
    cur.execute("DROP SCHEMA IF EXISTS {} CASCADE".format(schema))
    for role in ROLES + ("owner",):
        r = "{}_{}".format(schema, role)
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (r,))
        if cur.fetchone():
            cur.execute("DROP OWNED BY {}".format(r))
            cur.execute("DROP ROLE {}".format(r))
    conn.commit()


class Moonshot:
    """A connection acting as exactly one Moonshot role."""

    def __init__(self, conn, schema="moonshot", role="reader", actor=""):
        _check(schema)
        if role not in ROLES:
            raise ValueError("role must be one of {}".format(ROLES))
        self.conn, self.schema, self.role, self.actor = conn, schema, role, actor or role
        self._set_role()

    def _set_role(self):
        cur = self.conn.cursor()
        cur.execute("SET ROLE {}_{}".format(self.schema, self.role))
        self.conn.commit()

    def _heal(self):
        """Replace a connection that has died (server restart, network fault, a terminated backend) with a fresh
        dedicated one acting as the same role. Nothing is lost: every call ends its own transaction."""
        if self.conn.closed:
            self.conn = connect()
            self._set_role()

    def _discard(self):
        try:
            self.conn.close()
        except Exception:
            pass

    def close(self):
        """Reset the role before closing, so even a pooled connection goes back clean."""
        try:
            self.conn.rollback()
            self.conn.cursor().execute("RESET ROLE")
            self.conn.commit()
        except Exception:
            pass
        try:
            self.conn.close()
        except Exception:
            pass

    def _q(self, sql, args=(), one=False, commit=False):
        self._heal()
        cur = self.conn.cursor()
        try:
            cur.execute(sql.format(s=self.schema), args)
            rows = cur.fetchall() if cur.description else []
            if commit:
                self.conn.commit()
            else:
                self.conn.rollback()             # reads end their transaction; nothing to keep
        except Exception:
            if not self.conn.closed:             # a dead connection has nothing to roll back
                self.conn.rollback()
            raise
        return (rows[0] if rows else None) if one else rows

    # ------------------------------------------------------------------------------------------- reads

    def schema_version(self):
        return int(self._q("SELECT value FROM {s}.meta WHERE key = 'schema_version'", one=True)[0])

    def head(self, chain_id):
        r = self._q("SELECT head_index, head_epoch_digest, head_checkpoint_sha256, generation, state, epochs_target, "
                    "approved_code_sha, namespace FROM {s}.chains WHERE chain_id = %s", (chain_id,), one=True)
        if r is None:
            raise KeyError("no chain " + chain_id)
        keys = ("head_index", "head_epoch_digest", "head_checkpoint_sha256", "generation", "state", "epochs_target",
                "approved_code_sha", "namespace")
        return dict(zip(keys, r))

    def genesis(self, chain_id):
        r = self._q("SELECT o.content FROM {s}.chains c JOIN {s}.objects o ON o.sha256 = c.genesis_sha256 "
                    "WHERE c.chain_id = %s", (chain_id,), one=True)
        if r is None:
            raise KeyError("no chain " + chain_id)
        return C.parse_canonical(bytes(r[0]))

    def object(self, sha256):
        r = self._q("SELECT content FROM {s}.objects WHERE sha256 = %s", (sha256,), one=True)
        return None if r is None else bytes(r[0])

    def lineage(self, chain_id):
        rows = self._q("SELECT epoch_index, epoch_digest, work_id, generation, publication_id, parent_epoch_digest, "
                       "attempt_id FROM {s}.publications WHERE chain_id = %s AND rejected_at IS NULL "
                       "ORDER BY epoch_index", (chain_id,))
        keys = ("epoch_index", "epoch_digest", "work_id", "generation", "publication_id", "parent_epoch_digest",
                "attempt_id")
        return [dict(zip(keys, r)) for r in rows]

    def epoch_files(self, chain_id, epoch_index):
        r = self._q("SELECT m.content, s.content, t.content, k.content FROM {s}.publications p "
                    "JOIN {s}.results r ON r.work_id = p.work_id AND r.epoch_digest = p.epoch_digest "
                    "JOIN {s}.objects m ON m.sha256 = r.manifest_sha256 JOIN {s}.objects s ON s.sha256 = r.spec_sha256 "
                    "JOIN {s}.objects t ON t.sha256 = r.trace_sha256 "
                    "JOIN {s}.objects k ON k.sha256 = r.output_checkpoint_sha256 "
                    "WHERE p.chain_id = %s AND p.epoch_index = %s AND p.rejected_at IS NULL",
                    (chain_id, epoch_index), one=True)
        if r is None:
            return None
        return {"manifest": bytes(r[0]), "spec": bytes(r[1]), "trace": bytes(r[2]), "checkpoint": bytes(r[3])}

    def checkpoint_at(self, chain_id, epoch_index):
        """The checkpoint bytes at a lineage position (0 = the genesis initial checkpoint)."""
        if epoch_index == 0:
            r = self._q("SELECT o.content FROM {s}.chains c JOIN {s}.objects o ON o.sha256 = c.initial_checkpoint_sha256 "
                        "WHERE c.chain_id = %s", (chain_id,), one=True)
            return bytes(r[0])
        return self.epoch_files(chain_id, epoch_index)["checkpoint"]

    def open_contest(self, chain_id):
        r = self._q("SELECT contest_id, epoch_index, work_id, published_epoch_digest, challenger_epoch_digest, reason, "
                    "state FROM {s}.contests WHERE chain_id = %s AND state IN ('CONTESTED', 'TAINTED', 'UNRESOLVED')",
                    (chain_id,), one=True)
        keys = ("contest_id", "epoch_index", "work_id", "published_epoch_digest", "challenger_epoch_digest", "reason",
                "state")
        return None if r is None else dict(zip(keys, r))

    def results_for_work(self, work_id):
        return [r[0] for r in self._q("SELECT epoch_digest FROM {s}.results WHERE work_id = %s", (work_id,))]

    def attempt_count(self, chain_id):
        return self._q("SELECT count(*) FROM {s}.attempts WHERE chain_id = %s", (chain_id,), one=True)[0]

    def attempt(self, attempt_id):
        r = self._q("SELECT outcome, publication_id, contest_id, detail FROM {s}.attempts WHERE attempt_id = %s",
                    (attempt_id,), one=True)
        return None if r is None else dict(zip(("outcome", "publication_id", "contest_id", "detail"), r))

    def object_count(self):
        return self._q("SELECT count(*) FROM {s}.objects", one=True)[0]

    def validation_state(self, chain_id, epoch_index):
        r = self._q("SELECT v.state FROM {s}.validations v JOIN {s}.publications p ON p.publication_id = v.publication_id "
                    "WHERE p.chain_id = %s AND p.epoch_index = %s AND p.rejected_at IS NULL "
                    "ORDER BY v.validation_id DESC LIMIT 1", (chain_id, epoch_index), one=True)
        return "UNVALIDATED" if r is None else r[0]

    def classified_attempt_ids(self):
        """Every attempt this schema has classified (the publisher's idempotency set)."""
        return {r[0] for r in self._q("SELECT attempt_id FROM {s}.attempts")}

    def attempt_outcomes(self, chain_id):
        return dict(self._q("SELECT outcome, count(*) FROM {s}.attempts WHERE chain_id = %s GROUP BY outcome",
                            (chain_id,)))

    def contests(self, chain_id):
        keys = ("contest_id", "epoch_index", "reason", "state", "published_epoch_digest", "challenger_epoch_digest")
        return [dict(zip(keys, r)) for r in self._q(
            "SELECT contest_id, epoch_index, reason, state, published_epoch_digest, challenger_epoch_digest "
            "FROM {s}.contests WHERE chain_id = %s ORDER BY contest_id", (chain_id,))]

    def select(self, sql, args=()):
        """A read-only query under this handle's role; `{s}` is this schema."""
        return self._q(sql, args)

    def materializations(self):
        """Every logged materializer report, oldest first."""
        return [r[0] for r in self._q("SELECT detail FROM {s}.events WHERE kind = 'materialization' ORDER BY event_id")]

    def receipts(self, chain_id):
        return [r[0] for r in self._q("SELECT detail->>'sha256' FROM {s}.events WHERE chain_id = %s AND kind = 'receipt' "
                                      "ORDER BY event_id", (chain_id,))]

    def rejected_epochs(self, chain_id):
        return [tuple(r) for r in self._q("SELECT epoch_index, epoch_digest FROM {s}.publications WHERE chain_id = %s "
                                          "AND rejected_at IS NOT NULL ORDER BY epoch_index", (chain_id,))]

    def publisher_waiting(self, schema):
        return bool(self._q("SELECT count(*) FROM pg_locks WHERE locktype = 'advisory' AND classid = %s "
                            "AND objid = %s AND granted", (HOLD_LOCK_CLASS, hold_key(schema)), one=True)[0])

    def public_privileges(self, schema):
        """Every privilege PUBLIC holds on the schema or anything in it (default ACLs included)."""
        rows = self._q(
            "SELECT 'schema' FROM pg_namespace n, aclexplode(coalesce(n.nspacl, acldefault('n', n.nspowner))) a "
            " WHERE n.nspname = %s AND a.grantee = 0 "
            "UNION ALL SELECT 'relation:' || c.relname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace, "
            " aclexplode(coalesce(c.relacl, acldefault((CASE WHEN c.relkind = 'S' THEN 's' ELSE 'r' END)::\"char\", "
            "c.relowner))) a "
            " WHERE n.nspname = %s AND a.grantee = 0 "
            "UNION ALL SELECT 'function:' || p.proname FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace, "
            " aclexplode(coalesce(p.proacl, acldefault('f', p.proowner))) a WHERE n.nspname = %s AND a.grantee = 0",
            (schema, schema, schema))
        return [r[0] for r in rows]

    def raw(self, sql, args=()):
        """Run arbitrary SQL under this handle's role (tests use it to probe privileges)."""
        return self._q(sql, args, commit=True)

    # ------------------------------------------------------------------------------------------- writes

    def create_chain(self, genesis, *, namespace, approved_code_sha):
        import psycopg2.extras
        return self._q("SELECT {s}.create_chain(%s, %s, %s, %s, %s, %s, %s, %s)",
                       (genesis.chain_id, namespace, genesis.bytes, genesis.initial_checkpoint,
                        psycopg2.extras.Json(genesis.obj["runtime"]), approved_code_sha, genesis.obj["epochs"],
                        self.actor), one=True, commit=True)[0]

    def record_receipt(self, chain_id, receipt_bytes):
        """Store a receipt's canonical bytes content-addressed and log it; returns its sha256."""
        return self._q("SELECT {s}.record_receipt(%s, %s, %s)", (chain_id, receipt_bytes, self.actor), one=True,
                       commit=True)[0]

    def record_materialization(self, report):
        """Log a materializer report (coordinator role); returns its event id."""
        import psycopg2.extras
        return self._q("SELECT {s}.record_materialization(%s, %s)", (psycopg2.extras.Json(report), self.actor),
                       one=True, commit=True)[0]

    def verify(self, chain_id, epoch_index, files):
        """The publisher's semantic checks; [] means the bytes are a well-formed epoch at this position."""
        errs = model.verify_epoch(files)
        if errs:
            return errs
        try:
            spec = model.derive_spec(self.genesis(chain_id), epoch_index)
        except (ValueError, KeyError) as e:
            return ["no derived spec at this position: {}".format(e)]
        if files["spec"] != C.canonical_bytes(spec):
            return ["SPEC is not the derived spec"]
        m = C.parse_canonical(files["manifest"])
        if (m["chain_id"], m["epoch_index"]) != (chain_id, epoch_index):
            return ["manifest position is not ({}, {})".format(chain_id, epoch_index)]
        return []

    def record_attempt_outcome(self, attempt_id, task_id, chain_id, epoch_index, expected_parent, expected_generation,
                               outcome, work_id=None, epoch_digest=None, detail=None):
        import psycopg2.extras
        r = self._q("SELECT * FROM {s}.record_attempt_outcome(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (attempt_id, task_id, chain_id, epoch_index, expected_parent, expected_generation, outcome, work_id,
                     epoch_digest, psycopg2.extras.Json(detail or {}), self.actor), one=True, commit=True)
        return {"outcome": r[0], "publication_id": None, "contest_id": None, "generation": None, "replayed": r[1]}

    def publish(self, attempt_id, task_id, chain_id, epoch_index, expected_parent, expected_generation, files, *,
                detail=None, verify=True, approved=True, _hold_before_commit_s=0.0, _raise_before_commit=False,
                _lose_acks=0, _retries=3):
        """One guarded publication, classified exactly once per attempt id.

        If the connection dies anywhere -- before the call, inside the transaction, or around COMMIT (a lost
        acknowledgement) -- the whole call is repeated on a fresh connection with the same attempt id. That is safe
        because every step is idempotent per attempt: the database answers a known attempt from its record.
        Test hooks (first try only): `_hold_before_commit_s` parks inside the transaction holding an advisory lock;
        `_raise_before_commit` fails there; `_lose_acks` = n drops the connection after the first n COMMITs succeed.
        """
        import psycopg2
        lost = [_lose_acks]
        for i in range(_retries + 1):
            try:
                return self._publish_once(attempt_id, task_id, chain_id, epoch_index, expected_parent,
                                          expected_generation, files, detail, verify, approved,
                                          _hold_before_commit_s if i == 0 else 0.0,
                                          _raise_before_commit and i == 0, lost)
            except (psycopg2.OperationalError, psycopg2.InterfaceError):
                # the connection died: the transaction may or may not have committed -> ask the record again
                if i == _retries:
                    raise
                self._discard()
                time.sleep(0.5 * (i + 1))

    def _publish_once(self, attempt_id, task_id, chain_id, epoch_index, expected_parent, expected_generation, files,
                      detail, verify, approved, hold_s, raise_before_commit, lost):
        import psycopg2
        import psycopg2.extras
        work = epoch = None
        try:
            m = C.parse_canonical(files["manifest"])
            work, epoch = m.get("work_id"), m.get("epoch_digest")
        except Exception:
            pass
        if not approved:
            return self.record_attempt_outcome(attempt_id, task_id, chain_id, epoch_index, expected_parent,
                                               expected_generation, "REFUSED_UNAPPROVED", work, epoch, detail)
        if verify:
            errs = self.verify(chain_id, epoch_index, files)
            if errs:
                return self.record_attempt_outcome(attempt_id, task_id, chain_id, epoch_index, expected_parent,
                                                   expected_generation, "INVALID", work, epoch,
                                                   dict(detail or {}, errors=errs))
        args = (attempt_id, task_id, chain_id, epoch_index, expected_parent, expected_generation,
                files["manifest"], files["spec"], files["trace"], files["checkpoint"],
                psycopg2.extras.Json(detail or {}), self.actor)
        self._heal()
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT * FROM {}.publish(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(self.schema),
                        args)
            row = cur.fetchone()
            if hold_s:
                cur.execute("SELECT pg_advisory_xact_lock(%s, %s)", (HOLD_LOCK_CLASS, hold_key(self.schema)))
                cur.execute("SELECT pg_sleep(%s)", (hold_s,))
            if raise_before_commit:
                raise RuntimeError("injected failure before commit")
            self.conn.commit()
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            raise
        except Exception:
            self.conn.rollback()
            raise
        if lost[0] > 0:                          # test hook: the server committed; the client never hears it
            lost[0] -= 1
            self.conn.close()
            raise psycopg2.OperationalError("injected: acknowledgement lost after COMMIT")
        return {"outcome": row[0], "publication_id": row[1], "contest_id": row[2], "generation": row[3],
                "replayed": row[4]}

    def record_validation(self, chain_id, epoch_index, epoch_digest, state, checks, replay_digest, replay_host):
        """Record one validation of the live epoch `epoch_digest`; refused if that digest is no longer live."""
        return self._q("SELECT {s}.record_validation(%s, %s, %s, %s, %s, %s, %s, %s)",
                       (chain_id, epoch_index, epoch_digest, state, list(checks), replay_digest, replay_host,
                        self.actor), one=True, commit=True)[0]

    def resolve_contest(self, contest_id, replay_digests, published_bytes_ok=True):
        return self._q("SELECT {s}.resolve_contest(%s, %s, %s, %s)",
                       (contest_id, list(replay_digests), published_bytes_ok, self.actor), one=True, commit=True)[0]
