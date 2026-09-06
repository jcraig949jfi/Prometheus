"""ONE durable SFE identity per role, persisted.

SFE uses the client id as part of its tenancy and family structure, so a
process that registers a fresh client on every start does not look like one
long-lived Vivarium with many runs underneath it -- it looks like N different
Vivariums with one run each. Cross-run families and longitudinal analysis over
this seat's work become impossible, not difficult.

Measured on 2026-09-06 before this existed: **44 client rows** whose name
contains "viv", 35 of them holding exactly ONE world. Every live-SFE test run
minted another `vivarium-selftest`, and every daemon start minted another
`vivarium@<worker>`. That is the whole history of this seat, shredded.

    SFE saw                         it should have seen
      vivarium-selftest  (x24)        vivarium            run 1
      vivarium@skullport (x2)                             run 2
      vivarium@e2e-viv                                    run 3
      vivarium@m1                                         ...
      ...

TWO durable identities, not one. Production work and test work both create real
SFE worlds -- the engine has no namespace to separate them, unlike the queue
and PEW -- so the honest split is two STABLE identities rather than one stable
and a shredded tail:

    sfe_token         ROLE_PRODUCTION   the autonomous consumer
    sfe_test_token    ROLE_TEST         live tests

Both live in the gitignored vivarium/config.local.json. Registration happens
once, ever; after that the token is read. Nothing here is committed.

The 44 pre-existing identities are NOT merged or renamed. SFE's client rows are
its own record and not mine to rewrite, and the worlds under them really were
produced by separate registrations -- rewriting that would be inventing a
history that did not happen. This is a going-forward fix, and the discontinuity
is dated here.
"""
from __future__ import annotations

import json
import threading
from typing import Optional

from . import db as _db

ROLE_PRODUCTION = "production"
ROLE_TEST = "test"

#: role -> (config key for the token, config key for the client id, SFE name)
_ROLES = {
    ROLE_PRODUCTION: ("sfe_token", "sfe_client_id", "vivarium"),
    ROLE_TEST: ("sfe_test_token", "sfe_test_client_id", "vivarium-test"),
}

_LOCK = threading.Lock()


class IdentityError(RuntimeError):
    pass


def _write_local(updates: dict) -> None:
    """Merge into the gitignored local config. Never touches config.json."""
    path = _db.LOCAL_PATH
    current = {}
    if path.exists():
        current = json.loads(path.read_text(encoding="utf-8"))
    current.update(updates)
    path.write_text(json.dumps(current, indent=2) + chr(10), encoding="utf-8")


def token_for(role: str, *, register_if_missing: bool = False,
              client_factory=None, log=lambda *_a: None) -> str:
    """The durable token for `role`, registering ONCE if allowed.

    `register_if_missing=False` by default so an accidental new identity is a
    loud error naming the fix, not a silent 45th client row.
    """
    if role not in _ROLES:
        raise IdentityError("unknown identity role %r" % role)
    tok_key, cid_key, name = _ROLES[role]
    cfg = _db.load_config()
    tok = cfg.get(tok_key)
    if tok:
        return tok
    if not register_if_missing:
        raise IdentityError(
            "no durable SFE identity for role %r. Vivarium will not mint one "
            "implicitly: a fresh client id per run is what turned this seat's "
            "history into 44 single-world tenants. Run:  python -m viv.cli "
            "sfe-identity --ensure --role %s" % (role, role))
    with _LOCK:
        cfg = _db.load_config()                # re-read under the lock
        tok = cfg.get(tok_key)
        if tok:
            return tok
        if client_factory is None:
            raise IdentityError("no client_factory supplied to register")
        client = client_factory()
        tok = client.register(name)
        cid = getattr(client, "client_id", None)
        _write_local({tok_key: tok, **({cid_key: cid} if cid else {})})
        log("[viv] registered the DURABLE %s SFE identity as %r and persisted "
            "it to %s. This happens once." % (role, name, _db.LOCAL_PATH.name))
        return tok


def configured(role: str = ROLE_PRODUCTION) -> bool:
    tok_key, _, _ = _ROLES[role]
    return bool(_db.load_config().get(tok_key))


def describe() -> dict:
    cfg = _db.load_config()
    out = {}
    for role, (tok_key, cid_key, name) in _ROLES.items():
        tok = cfg.get(tok_key)
        out[role] = {"sfe_name": name, "configured": bool(tok),
                     "client_id": cfg.get(cid_key),
                     "token_prefix": (tok[:10] + "...") if tok else None}
    return out
