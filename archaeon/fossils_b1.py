"""The B1 evidence reader: fossils through the engine's cross-tenant read
grant (/v2/read/worlds, /v2/read/observations), never the ledger file.

Operator order 2026-09-12 (fossil metabolism S2, phase 0): after parity, B1
is Archaeon's operational evidence source and the raw SQLite read is
retired from active operation. This module produces the SAME Corpus shape
as fossils.read_sfe so every detector, census and template sees no
difference -- except where the read route carries less than the ledger,
which is recorded in the window block rather than papered over:

    spec.candidate coords   NOT available (the route returns observations,
                            not experiment specs)          -> coords {}
    anchors.spec_hash,      NOT available on the route      -> None
    anchors.committed_seq
    family (topology_group) available from /v2/read/worlds  -> filled

Those absences are Daedalus's to close on the route (exact requirement
sent 2026-09-12); until then a detector that needs spec coords (D6) is
INELIGIBLE on B1 evidence and its census says so. NO FALLBACK: if the grant,
the scope or the route fails, the Corpus carries the error and zero rows.
A raw read is never substituted silently.

Configuration (archaeon/config.local.json, per host, gitignored):
    evidence_source   "b1"  (anything else -> the legacy raw reader, which
                            logs that it is the legacy path)
    sfe_base_url, sfe_token, sfe_cacert, sfe_client_id
    b1_scope          the scope id granted to this client
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import config as cfg
from .fossils import Corpus, FossilRow, _metric

REPO = Path(__file__).resolve().parent.parent
LOCAL = Path(__file__).resolve().parent / "config.local.json"


def local_config() -> Dict[str, Any]:
    try:
        return json.loads(LOCAL.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def evidence_source() -> str:
    return os.environ.get("ARCHAEON_EVIDENCE_SOURCE") or local_config().get("evidence_source") or "raw"


def _client(lc: Dict[str, Any]):
    p = str(REPO / "SerendipityFoundry" / "SerendipityFoundryClient")
    if p not in sys.path:
        sys.path.insert(0, p)
    from sfclient.client import EngineClient
    cafile = lc.get("sfe_cacert")
    if cafile and not os.path.isabs(cafile):
        cafile = str(REPO / cafile)
    return EngineClient(lc["sfe_base_url"], lc["sfe_token"], cafile=cafile, client_id=lc.get("sfe_client_id"))


def read_b1(chart: Optional[cfg.CoordinateChart] = None,
            lookback_rows: int = cfg.DEFAULT.lookback_rows,
            scope: Optional[str] = None) -> Corpus:
    chart = chart or cfg.CHARTS[cfg.DEFAULT_CHART]
    lc = local_config()
    scope = scope or lc.get("b1_scope")
    ten = cfg.DEFAULT.tenancy
    declared = {"admitted_client_names": list(ten.include_client_names),
                "evidence_classes": list(ten.evidence_classes),
                "expected_schema_version": ten.expected_schema_version}
    ref = "b1:{}@{}".format(scope, lc.get("sfe_base_url"))
    missing = [k for k in ("sfe_base_url", "sfe_token") if not lc.get(k)]
    if missing or not scope:
        return Corpus([], chart, ref, {"source": "b1", "error": "b1 not configured: missing {}".format(missing + ([] if scope else ["b1_scope"])), "tenancy": declared})
    try:
        c = _client(lc)
        ws = c.read_worlds(scope=scope, limit=5000)
        worlds = {w["world_id"]: w for w in ws.get("worlds", [])}
        rows_raw: List[Dict[str, Any]] = []
        truncated_worlds = 0
        # one page per world: the route caps a page at `limit`; per-world pages
        # cannot be truncated for our world sizes and the flag is checked anyway
        for wid in sorted(worlds):
            r = c.read_observations(scope=scope, world_id=wid, limit=1000)
            if (r.get("corpus") or {}).get("truncated"):
                truncated_worlds += 1
            rows_raw.extend(r.get("observations") or [])
    except Exception as exc:                                     # noqa: BLE001
        return Corpus([], chart, ref, {"source": "b1", "error": "b1 read failed: {}: {}".format(type(exc).__name__, str(exc)[:200]), "tenancy": declared})
    # the declared tenancy still applies: client NAMES are resolved from the worlds the grant exposes
    rows: List[FossilRow] = []
    excluded_class = 0
    rows_raw.sort(key=lambda o: -int(o.get("created_seq") or 0))
    for o in rows_raw[: int(lookback_rows)]:
        if o.get("evidence_class") not in ten.evidence_classes:
            excluded_class += 1
            continue
        content = o.get("content") if isinstance(o.get("content"), dict) else None
        if content is None:
            continue
        metric = _metric(content, chart)
        if metric is None:
            continue
        w = worlds.get(o["world_id"], {})
        rows.append(FossilRow(
            row_id=o["obs_id"], source="sfe", seq=int(o["created_seq"]), region=o["world_id"],
            family=w.get("topology_group"), player=None, metric=metric, coords={},
            anchors={"obs_id": o["obs_id"], "exp_id": o.get("exp_id"), "work_id": o.get("work_id"), "world_id": o["world_id"],
                     "spec_hash": None, "committed_seq": None, "observation_created_seq": int(o["created_seq"]),
                     "evidence_class": o.get("evidence_class"), "outcome": o.get("outcome"),
                     "seed_root": w.get("seed_root"), "world_name": w.get("name"),
                     # the observation content the route DOES carry, kept for the S2 census (bits/score are the fossil)
                     "result": (content.get("result") if isinstance(content.get("result"), dict) else None)}))
    rows.sort(key=lambda x: (x.seq, x.row_id))
    return Corpus(rows, chart, ref, {
        "source": "b1", "scope": scope, "grantee": lc.get("sfe_client_id"),
        "lookback_rows": int(lookback_rows), "order": "observations.created_seq DESC (client-side over the scope's pages)",
        "join": "/v2/read/observations per world x /v2/read/worlds", "returned": len(rows),
        "worlds_in_scope": len(worlds), "observations_in_scope": len(rows_raw), "truncated_world_pages": truncated_worlds,
        "excluded_by_evidence_class": excluded_class,
        "tenancy": {"admitted_client_names": list(ten.include_client_names), "basis": "the read grant's scope (owner-enumerated worlds); declared names are not consulted on this path", "evidence_classes": list(ten.evidence_classes), "snapshot": "per-world pages, not one transaction"},
        "not_available_on_route": ["spec.candidate coords", "anchors.spec_hash", "anchors.committed_seq"],
        "unattributed_multi_player_experiments": 0})
