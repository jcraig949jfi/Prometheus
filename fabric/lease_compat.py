"""fabric.lease_compat -- the one lease authority, behind the legacy helpers' command lines.

Operator ruling 2026-09-28: the fabric lease (Postgres, one unreleased row per resource) is the only authority.
The ARC3 helpers (roles/Ananke/research/lease.py, roles/Nestor/tools/nestor_lease.py) keep their CLIs so running
experiments do not break. Underneath, every acquire, renew and release is this module on the SAME atomic
resource row that fabric Attempts take:

    old experiment -> legacy lease CLI -> fabric/Postgres lease -> same resource row

Legacy resource names are host-scoped: `cpu8` on SKULLPORT is the fabric resource `skullport:cpu8`. No host file
is written and no comms LEASE record is posted. `python -m fabric lease status` is the record.

Fail closed: if the store is unreachable, nothing is granted (StoreUnavailable). A caller that waits must wait on
this, never assume "probably free".
"""
from __future__ import annotations

import socket
from typing import Any, Dict, List, Optional

from . import store as S


class StoreUnavailable(Exception):
    """The canonical lease store cannot be reached or verified: nothing is granted."""


def host() -> str:
    return socket.gethostname().lower()


def resource(res: str, on_host: Optional[str] = None) -> str:
    return "{}:{}".format((on_host or host()).lower(), res)


def _conn():
    try:
        return S.connect()
    except Exception as e:                                            # noqa: BLE001 -- any failure means no lease
        raise StoreUnavailable("{}: {}".format(type(e).__name__, str(e)[:300]))


def acquire(res: str, holder: str, *, purpose: str = "", ttl_s: int = 3600) -> Dict[str, Any]:
    """{"result": "ACQUIRED", lease_id, token, resource, expires_at} or {"result": "BUSY", held_by, resource}."""
    c = _conn()
    try:
        r = S.lease_acquire(c, resource(res), holder, host(), purpose=purpose, ttl_s=int(ttl_s))
    except Exception as e:                                            # noqa: BLE001
        raise StoreUnavailable("{}: {}".format(type(e).__name__, str(e)[:300]))
    finally:
        c.close()
    return r


def _find(c, res: str, token: str) -> Optional[Dict[str, Any]]:
    cur = c.cursor()
    cur.execute("SELECT lease_id, holder, expires_at FROM {}.leases WHERE resource = %s AND token = %s AND released_at IS NULL"
                .format(S.schema()), (resource(res), token))
    row = cur.fetchone(); c.commit()
    return {"lease_id": row[0], "holder": row[1], "expires_at": row[2]} if row else None


def release(res: str, token: str, actor: str) -> str:
    c = _conn()
    try:
        f = _find(c, res, token)
        if not f:
            return "NOT HELD"
        return "RELEASED" if S.lease_release(c, f["lease_id"], token, actor) else "NOT HELD"
    finally:
        c.close()


def renew(res: str, token: str, ttl_s: int) -> str:
    c = _conn()
    try:
        f = _find(c, res, token)
        if not f:
            return "NOT HELD"
        return "EXTENDED" if S.lease_renew(c, f["lease_id"], token, int(ttl_s)) else "NOT HELD"
    finally:
        c.close()


def status(on_host: Optional[str] = None) -> List[Dict[str, Any]]:
    c = _conn()
    try:
        pre = (on_host or host()).lower() + ":"
        return [l for l in S.leases(c) if l["resource"].startswith(pre)]
    finally:
        c.close()
