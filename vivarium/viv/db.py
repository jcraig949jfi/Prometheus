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
                     ("identity_role", "VIV_IDENTITY_ROLE")):
        if os.environ.get(env):
            cfg[key] = os.environ[env]
    return cfg


def schema() -> str:
    s = load_config()["schema"]
    if not _SCHEMA_RE.match(s):
        raise ValueError(f"unsafe schema name {s!r}")
    return s


def connect(*, autocommit: bool = False):
    cfg = load_config()
    conn = psycopg2.connect(host=cfg["db_host"], dbname=cfg["db_name"],
                            user=cfg["db_user"], password=cfg["db_password"])
    conn.autocommit = autocommit
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
