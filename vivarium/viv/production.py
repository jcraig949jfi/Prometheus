"""The production descriptor: one machine-readable file consumers gate on
(point release; roles/Vivarium/point_release/PRODUCTION_DESCRIPTOR.md;
campaign-1 ledger L-002 / L-003 / L-005).

Resolution order for the file:
    VIV_PRODUCTION_DESCRIPTOR (env)  ->  <repo>/deploy/PRODUCTION.json (the shared,
    three-block file once Daedalus/Hermes/Vivarium land it)  ->
    <repo>/vivarium/deploy/PRODUCTION.draft.json (this seat's draft).

What a consumer does with it (operator s12: "if any production identity
differs from the descriptor: refuse work"):
    - HOLD live (non-expired)                        -> refuse to launch, print the hold
    - engine.engine_instance_id != /v2/version's     -> refuse (WRONG_ENGINE)
    - store identity != the live connection's        -> refuse (viv/db.py already does)
    - a credential key named for this role is absent -> refuse (by key NAME; no value is read)
Nothing here holds a secret.
"""
from __future__ import annotations

import datetime
import json
import os
import ssl
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO = Path(__file__).resolve().parent.parent.parent
SHARED = REPO / "deploy" / "PRODUCTION.json"
DRAFT = REPO / "vivarium" / "deploy" / "PRODUCTION.draft.json"
UNKNOWN = "UNKNOWN"


def path() -> Path:
    env = os.environ.get("VIV_PRODUCTION_DESCRIPTOR")
    if env:
        return Path(env)
    return SHARED if SHARED.exists() else DRAFT


def load(p: Optional[Path] = None) -> dict:
    p = p or path()
    d = json.loads(Path(p).read_text(encoding="utf-8"))
    d["_path"] = str(p)
    return d


def hold_live(d: dict, now: Optional[datetime.datetime] = None) -> Optional[dict]:
    h = d.get("hold")
    if not h:
        return None
    now = now or datetime.datetime.now(datetime.timezone.utc)
    exp = h.get("expires")
    if exp:
        try:
            when = datetime.datetime.fromisoformat(exp.replace("Z", "+00:00"))
            if when <= now:
                return None                       # expired hold is no hold
        except ValueError:
            return dict(h, note="unparseable expiry; treated as LIVE")
    return h


def probe_engine(d: dict, timeout_s: float = 10.0) -> dict:
    eng = d.get("engine") or {}
    url = str(eng.get("endpoint", "")).rstrip("/") + "/v2/version"
    cacert = eng.get("cacert")
    ctx = ssl.create_default_context()
    cpath = REPO / cacert if cacert and not os.path.isabs(str(cacert)) else Path(str(cacert)) if cacert else None
    if cpath and cpath.exists():
        ctx.load_verify_locations(str(cpath))
    else:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(url, timeout=timeout_s, context=ctx) as r:
            body = json.loads(r.read().decode("utf-8"))
    except Exception as exc:                                     # noqa: BLE001
        return {"ok": False, "reason": "UNREACHABLE", "url": url, "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    got = body.get("engine_instance_id")
    if got != eng.get("engine_instance_id"):
        return {"ok": False, "reason": "WRONG_ENGINE", "url": url, "expected": eng.get("engine_instance_id"), "observed": got}
    floor = eng.get("schema_floor")
    if floor is not None and (body.get("schema_version") or 0) < floor:
        return {"ok": False, "reason": "SCHEMA_BELOW_FLOOR", "url": url, "floor": floor, "observed": body.get("schema_version")}
    return {"ok": True, "reason": "ANSWERED", "url": url, "observed": got, "schema_version": body.get("schema_version"),
            "engine_source_hash": body.get("engine_source_hash"), "expected_source_hash": eng.get("engine_source_hash"),
            "source_hash_matches": body.get("engine_source_hash") == eng.get("engine_source_hash")}


def credential_presence(d: dict, role: str = "vivarium") -> dict:
    c = (d.get("consumers") or {}).get(role) or {}
    f = c.get("credential_file")
    keys = c.get("keys") or []
    # optional_keys: presence RECORDED, absence never a refusal -- the PEW
    # writer token gates the deliverer (the outbox holds without it), not the
    # consumer (operator repair order 2026-09-17: the restart must not wait on
    # a credential another seat issues out of band)
    optional = c.get("optional_keys") or []
    p = REPO / f if f and not os.path.isabs(f) else Path(f) if f else None
    present: Dict[str, bool] = {}
    have = set()
    if p and p.exists():
        try:
            have = set(json.loads(p.read_text(encoding="utf-8")).keys())
        except Exception:                                         # noqa: BLE001
            have = set()
    present = {k: (k in have) for k in keys}
    return {"role": role, "credential_file": str(p) if p else None, "present": present,
            "optional_present": {k: (k in have) for k in optional},
            "ok": bool(keys) and all(present.values())}


def store_check(d: dict) -> dict:
    """The live connection must be the descriptor's store (viv/db.py proves
    the cluster; this reports which environment that is)."""
    from . import db as _db
    want = (d.get("store") or {}).get("environment")
    try:
        env = _db.db_environment()
        conn = _db.connect()
        conn.close()
        return {"ok": env == want, "environment": env, "expected": want}
    except Exception as exc:                                      # noqa: BLE001
        return {"ok": False, "environment": None, "expected": want, "error": str(exc)[:300]}


def verify(d: Optional[dict] = None, *, role: str = "vivarium", probe: bool = True) -> dict:
    d = d or load()
    out: Dict[str, Any] = {"descriptor": d.get("_path"), "descriptor_version": d.get("descriptor_version"),
                           "ruled_by": d.get("ruled_by"), "ruled_at": d.get("ruled_at")}
    out["hold"] = hold_live(d)
    out["engine"] = probe_engine(d) if probe else {"ok": None, "reason": "NOT_PROBED"}
    out["store"] = store_check(d)
    out["credential"] = credential_presence(d, role)
    reasons: List[str] = []
    if out["hold"]:
        reasons.append("HOLD live: %s" % (out["hold"].get("reason") or ""))
    if probe and not out["engine"].get("ok"):
        reasons.append("engine %s" % out["engine"].get("reason"))
    if not out["store"].get("ok"):
        reasons.append("store is not %s" % out["store"].get("expected"))
    if not out["credential"].get("ok"):
        reasons.append("credential keys missing for role %s: %s"
                       % (role, [k for k, v in out["credential"]["present"].items() if not v]))
    out["refuse"] = reasons
    out["ok"] = not reasons
    return out
