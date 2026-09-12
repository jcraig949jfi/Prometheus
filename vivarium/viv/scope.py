"""B1 recurrence: keep the enumerated read scope current, owner-side.

THE GAP THIS CLOSES (operator, 2026-09-12). The B1 scope was filled once with
592 viv-* worlds at 12:52; S1 then created 24 more at 12:56. A scope filled
once is a snapshot: every world this consumer creates afterwards is invisible
to Archaeon's granted read until an owner adds it. Nothing did.

THE RULE (smallest, on existing machinery):

    An explicit owner-side extension of each DECLARED scope, run
      (a) once at consumer start, and
      (b) once at every BATCH BOUNDARY -- the first IDLE tick after a run of
          productive ticks (a drained queue is the end of a batch),
      (c) by hand: `python -m viv.cli scope-reconcile [--dry-run]`.

    It is deploy/read_scope_grant.py's `ensure_grant` -- the tool that filled
    the scope -- called with the consumer's own owner identity. Add-only
    (INSERT OR IGNORE on the engine), owner-only (the engine refuses foreign
    worlds: `not_yours`), filtered owner-side by the declared name prefix,
    idempotent, and it never removes anything. SFE's read-scope semantics
    are untouched: the scope stays an explicit enumeration; the filter lives
    here, in the owner's process, where the agreed policy is.

    Declared in config.json under `read_scopes`:
        [{"scope_name": "archaeon-campaigns",
          "grantee": "cli_...", "name_prefix": "viv-", "note": "..."}]
    No declaration -> explicit no-op ("no scopes declared").

BOUNDED, VISIBLE. One call per boundary, never a loop. Every call writes a
receipt to <var_dir>/scope_reconcile-<utc>.json and logs its productivity:
"added N" or "no-op: scope complete (M worlds)". A failure is logged and
receipted and NEVER touches a row: the reconcile runs between ticks, after
the queue is already empty.

NOT SCIENCE. Worlds becoming readable is infrastructure. This module counts
nothing toward any experiment.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

CONFIG_KEY = "read_scopes"

_REPO = Path(__file__).resolve().parents[2]
_DEPLOY = _REPO / "SerendipityFoundry" / "SerendipityFoundryEngine" / "deploy"


def _ensure_grant():
    """Daedalus's tool, imported from where it lives; one definition."""
    if str(_DEPLOY) not in sys.path:
        sys.path.insert(0, str(_DEPLOY))
    from read_scope_grant import ensure_grant                      # noqa: PLC0415
    return ensure_grant


def declared(cfg: dict) -> List[Dict[str, Any]]:
    out = []
    for s in cfg.get(CONFIG_KEY) or ():
        if not s.get("scope_name") or not s.get("grantee"):
            raise ValueError("read_scopes entries need scope_name and grantee: %r" % (s,))
        out.append(dict(s))
    return out


def reconcile(client, scopes: List[Dict[str, Any]], *, dry_run: bool = False,
              log: Callable = lambda *_a: None, trigger: str = "manual",
              ensure=None) -> Dict[str, Any]:
    """Extend every declared scope with the owner's newly eligible worlds.

    Returns one record: per-scope receipts from ensure_grant plus the
    productivity line. Never raises for a scope failure -- the failure is
    the receipt for that scope."""
    ensure = ensure or _ensure_grant()
    rec = {"schema": "viv.scope_reconcile.v1",
           "at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
           "trigger": trigger, "dry_run": dry_run, "pid": os.getpid(),
           "owner_client_id": getattr(client, "client_id", None),
           "scopes": [], "added_total": 0, "productive": False}
    if not scopes:
        rec["no_op"] = "no scopes declared in config"
        log("[viv] scope reconcile (%s): no-op, no scopes declared" % trigger)
        return rec
    for s in scopes:
        prefix = s.get("name_prefix")
        flt = (lambda w, p=prefix: str(w.get("name", "")).startswith(p)) if prefix else None
        try:
            r = ensure(client, scope_name=s["scope_name"],
                       grantee_client_id=s["grantee"], world_filter=flt,
                       note=s.get("note"), dry_run=dry_run)
            r["name_prefix"] = prefix
            added = int(r.get("worlds_added_this_run", r.get("would_add", 0)) or 0)
            rec["added_total"] += added
            if added > 0:
                log("[viv] scope reconcile (%s): %s added %d -> %s in scope (grantee %s)"
                    % (trigger, s["scope_name"], added,
                       r.get("worlds_in_scope_after", "?"), s["grantee"]))
            else:
                log("[viv] scope reconcile (%s): %s no-op, scope complete (%s in scope)"
                    % (trigger, s["scope_name"], r.get("worlds_in_scope_after", r.get("would_add", "?"))))
            if r.get("not_yours"):
                log("[viv] scope reconcile: engine refused %d foreign world(s) (not_yours)"
                    % len(r["not_yours"]))
        except Exception as exc:                                  # noqa: BLE001
            r = {"scope_name": s["scope_name"], "grantee_client_id": s["grantee"],
                 "error": str(exc)[:600], "name_prefix": prefix}
            log("[viv] scope reconcile (%s): %s FAILED %s" % (trigger, s["scope_name"], str(exc)[:200]))
        rec["scopes"].append(r)
    rec["productive"] = rec["added_total"] > 0
    return rec


def write_receipt(rec: Dict[str, Any], var: Path) -> Optional[Path]:
    try:
        var.mkdir(parents=True, exist_ok=True)
        p = var / ("scope_reconcile-%s.json"
                   % rec["at"].replace(":", "").replace("+00:00", "Z")[:20])
        p.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
        return p
    except OSError:                                                # pragma: no cover
        return None
