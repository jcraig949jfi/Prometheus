"""Prove a database connection reached the environment it was meant to reach.

comms.identity -- built by Hermes 2026-09-11, moved here under Archaeon's
ruling on Hermes #68 (D-24 amendment 1, comms message 73): comms owns the
notion of which store is the program's; the Evidence Wiki may import it.
The fail-closed invariant:

    A Prometheus client MUST NOT execute a statement against a resolved
    target until the target has PROVED it is the expected environment.

Motivation, measured (roles/Hermes/journal/2026-09-11b.md; the incident
file is roles/Hermes/incidents/c84e26826cc12217.md):
  * evidence_wiki/config.json is git-tracked and ships db_host="localhost",
    db_name="prometheus_fire" to every machine. On M1 that is the canonical
    store. On M2 it is a local fork of it, made 2026-09-04, carrying an `ew`
    schema with 34 of the canonical 41 tables and diverging in BOTH
    directions since.
  * Five seats reached the wrong one on 2026-09-11. comms failed loudly
    (UndefinedTable). The Evidence Wiki did NOT: `ew.claims` exists in both.
  * The discriminator was already being COMPUTED and stored --
    evidence_wiki/ew/closure.py service_attestation() reads
    pg_control_system().system_identifier and calls it, correctly,
    "non-spoofable proof of WHICH database persisted a row". It is recorded
    on the row and never compared to anything. A record is not a gate.

So this module adds exactly one thing: the EXPECTED value, and the refusal.

Identity evidence and what each element can and cannot distinguish:

  db_system_id   pg_control_system().system_identifier, assigned at initdb.
                 Distinguishes: a dump/restore fork (new cluster -> new id;
                 this is how M2's fork was made, measured), an unrelated
                 cluster, the same schema stood up on another machine.
                 Does NOT distinguish: a pg_basebackup/streaming clone,
                 which inherits the id. See RESIDUAL below.
  db_name        distinguishes two databases inside one cluster. Alone it
                 is worthless here: both stores are named prometheus_fire.
  schema presence  NOT identity. Measured: `ew` exists in both stores.
                 This is why the invariant does not test for tables.

RESIDUAL, stated rather than solved (no evidence justifies the cost today):
  A promoted physical clone keeps the system_identifier and is writable, so
  it would pass. Catching it needs a logical identity minted AFTER the
  split -- a one-row table holding a UUID. No such clone exists in this
  fleet: M2's fork has a DIFFERENT system_identifier (7681719240261676752
  vs the canonical 7628127204585430828), which proves it came from a dump,
  not a basebackup. Build the UUID table when the first basebackup clone
  exists, not before; `expected_uuid` is already accepted below so the
  upgrade is additive.

No credential is read, logged or returned by anything here.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

REGISTRY_ENV = "PROMETHEUS_ENVIRONMENTS"
DEFAULT_REGISTRY = Path(__file__).resolve().parent / "environments.json"
#: The environment a client requires when it does not say. Overridable per
#: process with PROMETHEUS_ENV so that deliberate work on a fork is a VISIBLE
#: act rather than a default (Archaeon's constraint: the registry carries no
#: credentials, only non-secret identity facts).
DEFAULT_ENVIRONMENT = "prometheus-canonical"


#: Where the one-file-per-failure-signature records live. A refusal must point
#: at a REAL path, so this names where they are TODAY (Hermes's lane), not
#: where they may end up; the permanent home is an open question the failure
#: convergence probe answers. Overridable with PROMETHEUS_INCIDENTS.
INCIDENT_DIR = os.environ.get("PROMETHEUS_INCIDENTS", "roles/Hermes/incidents")


def current_environment() -> str:
    return os.environ.get("PROMETHEUS_ENV") or DEFAULT_ENVIRONMENT


class WrongEnvironment(RuntimeError):
    """Raised instead of proceeding. Carries the signature so identical
    failures across seats collapse into one incident (see signature())."""

    def __init__(self, message: str, *, signature: str, observed: Dict[str, Any],
                 expected: Dict[str, Any], environment: str):
        super().__init__(message)
        self.signature = signature
        self.observed = observed
        self.expected = expected
        self.environment = environment


def registry_path() -> Path:
    return Path(os.environ.get(REGISTRY_ENV) or DEFAULT_REGISTRY)


def load_registry(path: Optional[Path] = None) -> Dict[str, Any]:
    p = path or registry_path()
    return json.loads(p.read_text(encoding="utf-8"))["environments"]


def observe(conn) -> Dict[str, Any]:
    """Read identity from the LIVE connection. Never cached: the attestation
    in closure.py caches per process, which is right for a service pinned to
    one store and wrong for a guard that must answer for THIS connection."""
    out: Dict[str, Any] = {"db_system_id": None, "db_name": None, "read_error": None}
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT system_identifier::text, current_database() "
                        "FROM pg_control_system()")
            row = cur.fetchone()
        out["db_system_id"], out["db_name"] = row[0], row[1]
    except Exception as e:                       # noqa: BLE001 - any failure is a refusal
        out["read_error"] = "{}: {}".format(type(e).__name__, str(e)[:200])
        try:
            conn.rollback()
        except Exception:
            pass
    return out


def signature(environment: str, observed: Dict[str, Any], expected: Dict[str, Any]) -> str:
    """A stable id for THIS failure class, not this occurrence. Two seats that
    reach the same wrong store from the same expectation produce the same
    signature, which is what lets five backlog items become one incident."""
    basis = "|".join([
        "db_identity_v1", environment,
        str(expected.get("db_system_id")), str(expected.get("db_name")),
        str(observed.get("db_system_id")), str(observed.get("db_name")),
        "read_error" if observed.get("read_error") else "mismatch",
    ])
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]


def check(conn, environment: str, *, registry: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return a verdict dict. Never raises on a wrong target; require() does."""
    envs = registry if registry is not None else load_registry()
    expected = envs.get(environment)
    observed = observe(conn)
    if expected is None:
        # Fail CLOSED on an unknown environment: an expectation that does not
        # exist is not an expectation that is satisfied.
        sig = signature(environment, observed, {})
        return {"ok": False, "reason": "NO_EXPECTATION", "environment": environment,
                "observed": observed, "expected": {}, "signature": sig}
    if observed["read_error"] is not None:
        sig = signature(environment, observed, expected)
        return {"ok": False, "reason": "IDENTITY_UNREADABLE", "environment": environment,
                "observed": observed, "expected": expected, "signature": sig}
    fields = ["db_system_id", "db_name"]
    if expected.get("expected_uuid"):            # additive upgrade path, unused today
        fields.append("instance_uuid")
    bad = [f for f in fields if expected.get(f) is not None and observed.get(f) != expected.get(f)]
    if bad:
        sig = signature(environment, observed, expected)
        return {"ok": False, "reason": "WRONG_ENVIRONMENT", "mismatched": bad,
                "environment": environment, "observed": observed,
                "expected": expected, "signature": sig}
    return {"ok": True, "reason": "MATCH", "environment": environment,
            "observed": observed, "expected": expected, "signature": None}


def require(conn, environment: str, *, registry: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The call site. Returns the verdict on success; raises WrongEnvironment
    otherwise. Put this after connect() and before the first statement."""
    v = check(conn, environment, registry=registry)
    if v["ok"]:
        return v
    o, e = v["observed"], v["expected"]
    msg = (
        "REFUSED: connection is not environment {env!r} ({reason}).\n"
        "  expected  db_system_id={ed} db_name={en}  ({desc})\n"
        "  observed  db_system_id={od} db_name={on}{err}\n"
        "  incident signature {sig} -- if {inc}/{sig}.md exists, add a\n"
        "  line to it; do NOT open a new backlog item for a known class.\n"
        "  Identity, not the host name, is the check: db_host is configuration\n"
        "  and two machines ship the same value."
    ).format(env=environment, reason=v["reason"],
             ed=e.get("db_system_id"), en=e.get("db_name"),
             desc=e.get("description", "no expectation registered"),
             od=o.get("db_system_id"), on=o.get("db_name"),
             err="  read_error=" + str(o["read_error"]) if o.get("read_error") else "",
             sig=v["signature"], inc=INCIDENT_DIR)
    raise WrongEnvironment(msg, signature=v["signature"], observed=o,
                           expected=e, environment=environment)
