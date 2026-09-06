"""The release-condition probe for M-ELIGIBLE.

The operator's release condition, in order:

    sealed arm binding -> granted readback -> one complete PEW round trip
      -> release the remaining M-ELIGIBLE requests

Each is a fact about a LIVE system, not about a commit. The v7 commit itself
says M1 was not restarted; a grant created against code that is not deployed
proves nothing. So this probe asks the running engine and the running PEW, with
Archaeon's own credentials, and reports what they actually return. It never
writes.

    python -m archaeon.producer.readback_probe

Read-only. No Vivarium. No model.
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LOCAL = REPO_ROOT / "archaeon" / "config.local.json"

#: The schema version at which the read-grant surface and family envelope exist.
V7 = 7


def _local() -> Dict[str, Any]:
    if LOCAL.exists():
        return json.loads(LOCAL.read_text(encoding="utf-8"))
    return {}


def _get(url: str, token: Optional[str], cacert: Optional[str],
         timeout: float = 8.0) -> Dict[str, Any]:
    ctx = ssl.create_default_context(cafile=cacert) if cacert else None
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return {"status": r.status, "body": json.loads(r.read() or b"{}")}
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read() or b"{}")
        except Exception:
            body = {}
        return {"status": e.code, "body": body}
    except Exception as exc:                       # noqa: BLE001
        return {"status": None, "error": "{}: {}".format(type(exc).__name__, exc)}


def probe(base_url: Optional[str] = None) -> Dict[str, Any]:
    cfg = _local()
    base = (base_url or cfg.get("sfe_base_url") or "https://192.168.1.202:8811").rstrip("/")
    cacert = cfg.get("sfe_cacert")
    if cacert and not os.path.isabs(cacert):
        cacert = str(REPO_ROOT / cacert)
    token = cfg.get("sfe_token")
    out: Dict[str, Any] = {"base_url": base, "conditions": {}}

    # ---- identity -------------------------------------------------------
    out["archaeon_client"] = {"registered": bool(cfg.get("sfe_client_id")),
                              "client_id": cfg.get("sfe_client_id"),
                              "name": cfg.get("sfe_client_name")}

    # ---- 1. live version: is v7 actually deployed? ----------------------
    v = _get(base + "/v2/version", None, cacert)
    body = v.get("body") or {}
    live_schema = body.get("schema_version")
    out["live"] = {"http": v.get("status"), "schema_version": live_schema,
                   "source_commit": body.get("source_commit"),
                   "engine_source_hash": body.get("engine_source_hash"),
                   "error": v.get("error")}
    out["conditions"]["v7_live"] = {
        "ok": live_schema is not None and int(live_schema) >= V7,
        "evidence": "GET /v2/version schema_version={}".format(live_schema),
        "owner": "daedalus",
        "note": ("the read-grant surface and the families envelope exist only "
                 "in v7; a grant created against undeployed code proves "
                 "nothing")}

    # ---- 2. granted readback with ARCHAEON's credentials ----------------
    rd = _get(base + "/v2/read/observations", token, cacert)
    rbody = rd.get("body") or {}
    rows = rbody.get("observations") or rbody.get("rows") or []
    census = rbody.get("census") or {}
    out["readback"] = {"http": rd.get("status"),
                       "rows_returned": len(rows) if isinstance(rows, list) else None,
                       "census": census if isinstance(census, dict) else None,
                       "has_family_metadata": any(
                           isinstance(r, dict) and ("family" in r or "families" in r)
                           for r in (rows if isinstance(rows, list) else [])[:50]),
                       "error": rd.get("error")}
    out["conditions"]["granted_readback"] = {
        "ok": (rd.get("status") == 200 and isinstance(rows, list)
               and len(rows) > 0 and bool(census)),
        "evidence": "GET /v2/read/observations -> HTTP {} rows={}".format(
            rd.get("status"), len(rows) if isinstance(rows, list) else None),
        "owner": "daedalus (deploy) + harmonia (grant) + archaeon (identity)",
        "note": ("must return the INTENDED observations WITH the census and the "
                 "comparison metadata the reader needs; an empty 200 is not "
                 "readback")}

    # ---- 3. one complete PEW round trip ---------------------------------
    rt = _pew_round_trip()
    out["round_trip"] = rt
    out["conditions"]["pew_round_trip"] = {
        "ok": bool(rt.get("repeat_round_trip")),
        "ok_arm_bound": bool(rt.get("arm_bound_round_trip")),
        "evidence": rt.get("evidence"),
        "owner": "vivarium (execute) + mnemosyne (readback)",
        "note": ("a repeat request has completed a round trip; an ARM-BOUND "
                 "request has not, and cannot until condition 1 lands")}

    out["release_ok"] = all(c["ok"] for c in out["conditions"].values()) \
        and out["conditions"]["pew_round_trip"]["ok_arm_bound"]
    out["release_condition"] = ("sealed arm binding -> granted readback -> one "
                                "complete PEW round trip -> release M-ELIGIBLE")
    return out


def _pew_round_trip() -> Dict[str, Any]:
    """Is there, in PEW prod, an encounter whose SFE experiment carries >1
    ordered attested observation? And one that also carries arm binding?"""
    try:
        from evidence_wiki.ew import db as ewdb
        import sqlite3
        conn = ewdb.connect()
        cur = conn.cursor()
        cur.execute("SELECT encounter_id, run_id, producer FROM ew.fossil_encounters "
                    " WHERE namespace='prod' AND run_id IS NOT NULL "
                    " ORDER BY revision DESC LIMIT 200")
        rows = cur.fetchall()
        conn.close()
    except Exception as exc:                       # noqa: BLE001
        return {"error": "pew unavailable: {}".format(exc)}
    sfe = os.environ.get("ARCHAEON_SFE_DB") or str(
        REPO_ROOT / "SerendipityFoundry" / "SerendipityFoundryEngine" / "var" / "engine.db")
    if not os.path.exists(sfe):
        return {"error": "sfe ledger not found at {}".format(sfe)}
    c = sqlite3.connect("file:{}?mode=ro".format(sfe), uri=True)
    best = None
    arm_bound = None
    for enc, run_id, producer in rows:
        exp_id = (run_id or "").split(":")[0]
        if not exp_id:
            continue
        obs = c.execute("SELECT count(*) FROM observations WHERE exp_id=? AND "
                        "evidence_class='ENGINE_WORK_RESULT'", (exp_id,)).fetchone()[0]
        if obs and obs > 1 and best is None:
            best = {"encounter_id": enc, "exp_id": exp_id, "observations": int(obs)}
        fam = (producer or {}).get("families") if isinstance(producer, dict) else None
        if fam and arm_bound is None:
            arm_bound = {"encounter_id": enc, "families": fam}
    c.close()
    return {"repeat_round_trip": best, "arm_bound_round_trip": arm_bound,
            "evidence": ("repeat: {} | arm-bound: {}".format(
                best["encounter_id"] if best else None,
                arm_bound["encounter_id"] if arm_bound else None))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="archaeon.producer.readback_probe")
    ap.add_argument("--base-url", default=None)
    a = ap.parse_args(argv)
    print(json.dumps(probe(a.base_url), indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
