"""Connection + schema handling for the Vivarium queue (schema `viv` in
prometheus_fire, the shared PostgreSQL instance hosted on M1).

CREDENTIALS ARE NEVER COMMITTED HERE. Precedence, highest first:

    1. environment      VIV_DB_HOST / VIV_DB_NAME / VIV_DB_USER /
                        VIV_DB_PASSWORD / VIV_SCHEMA / VIV_SFE_TOKEN /
                        VIV_PEW_TOKEN / VIV_PEW_NAMESPACE
    2. vivarium/config.local.json          (gitignored -- see repo .gitignore)
    3. evidence_wiki's existing loader     (the established shared-Postgres
                                            credential mechanism; reused rather
                                            than duplicated, so there is one
                                            place to rotate)
    4. vivarium/config.json                (non-secret defaults only)

The schema name is likewise overridable (VIV_SCHEMA) so tests run the identical
DDL against a throwaway schema on the same server -- SKIP LOCKED, partial
unique indexes and plpgsql triggers cannot be honestly tested against a mock.

THE CONNECTION MUST PROVE WHICH CLUSTER IT REACHED (2026-09-16). db_host is
configuration: the tracked default is "localhost", and on M2 that is the
QUARANTINED fork (db_system_id 7681719240261676752), which ships the same
db_name as the canonical store on M1. Measured on the 09-16 boot: `viv.cli
status` on M2 with no VIV_DB_HOST reached the fork and failed only because the
fork has no viv schema; `viv.cli run` applies migrations at start and would
have created it and ticked an empty queue, green, forever. Incident class
c84e26826cc12217 (roles/Hermes/incidents/). connect() therefore calls
comms.identity.require() before returning, exactly as comms does:

    production schema `viv`   ALWAYS environment "prometheus-canonical";
                              no variable or config key can re-aim it
    any other schema          VIV_DB_ENVIRONMENT / config "db_environment",
                              default "prometheus-canonical"; naming the
                              fork is a visible act, never a default

A guard that cannot be imported or cannot read the registry refuses: an
expectation that does not exist is not an expectation that is satisfied.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import psycopg2
import psycopg2.extras

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"
LOCAL_PATH = ROOT / "config.local.json"
MIGRATIONS = ROOT / "migrations"

_SCHEMA_RE = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")


def _evidence_wiki_credentials() -> dict:
    """The shared-Postgres credential mechanism already in the repo.

    Imported lazily and defensively: Vivarium must still start on a host where
    evidence_wiki is absent (it lives on origin/mnemosyne/evidence-wiki-v0), it
    just needs its own env/local config there."""
    import sys
    repo = ROOT.parent
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    try:
        from evidence_wiki.ew import db as ew_db  # type: ignore
        cfg = ew_db.load_config()
    except Exception:
        return {}
    return {k: cfg[k] for k in ("db_host", "db_name", "db_user", "db_password")
            if cfg.get(k) is not None}


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_config() -> dict:
    cfg: dict[str, Any] = {
        "db_host": "localhost",
        "db_name": "prometheus_fire",
        "db_user": "postgres",
        "db_password": None,
        "schema": "viv",
        "identity_role": "production",
    }
    cfg.update(_read_json(CONFIG_PATH))
    cfg.update(_evidence_wiki_credentials())
    cfg.update(_read_json(LOCAL_PATH))
    for key, env in (("db_host", "VIV_DB_HOST"), ("db_name", "VIV_DB_NAME"),
                     ("db_user", "VIV_DB_USER"),
                     ("db_password", "VIV_DB_PASSWORD"),
                     ("schema", "VIV_SCHEMA"),
                     ("sfe_token", "VIV_SFE_TOKEN"),
                     ("pew_token", "VIV_PEW_TOKEN"),
                     # VIV_PEW_NAMESPACE exists so a test run can force `test`
                     # even when the committed default is `prod`. See
                     # tests/conftest.py, which sets it unconditionally.
                     ("pew_namespace", "VIV_PEW_NAMESPACE"),
                     ("identity_role", "VIV_IDENTITY_ROLE"),
                     # A DEVELOPMENT engine. The committed default is the
                     # production URL, so a dev run must say so out loud in the
                     # environment rather than by editing a tracked file --
                     # which is also what stops a dev config from being
                     # committed by accident.
                     ("sfe_base_url", "VIV_SFE_BASE_URL"),
                     ("sfe_cacert", "VIV_SFE_CACERT"),
                     ("sfe_insecure", "VIV_SFE_INSECURE")):
        if os.environ.get(env):
            cfg[key] = os.environ[env]
    return cfg


def schema() -> str:
    s = load_config()["schema"]
    if not _SCHEMA_RE.match(s):
        raise ValueError(f"unsafe schema name {s!r}")
    return s


PRODUCTION_SCHEMA = "viv"
CANONICAL_ENVIRONMENT = "prometheus-canonical"


class WrongStore(RuntimeError):
    """connect() reached a cluster that is not the one this schema is bound
    to, or could not prove which one it reached. Carries comms.identity's
    verdict (`verdict`) so a caller can log the incident signature."""

    def __init__(self, msg: str, verdict: dict | None = None):
        super().__init__(msg)
        self.verdict = verdict or {}


def db_environment(cfg: dict | None = None) -> str:
    """The environment name a connection for this configuration must prove.

    The production schema is PINNED to the canonical store: the pin is decided
    by the schema, not by any variable, so an exported VIV_DB_ENVIRONMENT (or a
    config.local.json key) cannot aim the consumer at the fork. A throwaway
    schema may name another registered environment explicitly."""
    cfg = cfg if cfg is not None else load_config()
    if cfg.get("schema", PRODUCTION_SCHEMA) == PRODUCTION_SCHEMA:
        return CANONICAL_ENVIRONMENT
    return (os.environ.get("VIV_DB_ENVIRONMENT")
            or cfg.get("db_environment")
            or CANONICAL_ENVIRONMENT)


def _identity_module():
    """comms.identity, from the repository this package lives in. Fails
    CLOSED: without the guard there is no proof, and no proof is a refusal."""
    import sys
    repo = ROOT.parent
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    try:
        from comms import identity  # type: ignore
    except Exception as e:                                   # noqa: BLE001
        raise WrongStore("REFUSED: the database identity guard (comms.identity) "
                         "cannot be imported, so the connection cannot prove "
                         "which cluster it reached: %s: %s"
                         % (type(e).__name__, e)) from e
    return identity


def require_environment(conn, environment: str) -> dict:
    """Prove `conn` reached `environment` or close it and raise WrongStore.
    Returns comms.identity's verdict on success."""
    identity = _identity_module()
    try:
        return identity.require(conn, environment)
    except identity.WrongEnvironment as e:
        try:
            conn.close()
        except Exception:                                    # noqa: BLE001
            pass
        raise WrongStore(str(e), getattr(e, "__dict__", {})) from e


def connect(*, autocommit: bool = False):
    cfg = load_config()
    conn = psycopg2.connect(host=cfg["db_host"], dbname=cfg["db_name"],
                            user=cfg["db_user"], password=cfg["db_password"])
    conn.autocommit = autocommit
    try:
        require_environment(conn, db_environment(cfg))
        if not autocommit:
            conn.rollback()          # the identity read opened a transaction
    except BaseException:
        try:
            conn.close()
        except Exception:                                    # noqa: BLE001
            pass
        raise
    return conn


def dict_cur(conn):
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def apply_migrations(conn, *, target_schema: str | None = None) -> list[str]:
    """Apply every migration, substituting the schema placeholder. Migrations
    are idempotent, so this is safe to run on every start."""
    s = target_schema or schema()
    if not _SCHEMA_RE.match(s):
        raise ValueError(f"unsafe schema name {s!r}")
    applied = []
    with conn.cursor() as cur:
        for path in sorted(MIGRATIONS.glob("*.sql")):
            cur.execute(path.read_text(encoding="utf-8").replace("{schema}", s))
            applied.append(path.name)
    conn.commit()
    return applied


def drop_schema(conn, target_schema: str) -> None:
    """Test teardown only. Refuses to touch the production schema name."""
    if target_schema in ("viv", "public", "ew"):
        raise ValueError(f"refusing to drop {target_schema!r}")
    if not _SCHEMA_RE.match(target_schema):
        raise ValueError(f"unsafe schema name {target_schema!r}")
    with conn.cursor() as cur:
        cur.execute(f"DROP SCHEMA IF EXISTS {target_schema} CASCADE")
    conn.commit()
