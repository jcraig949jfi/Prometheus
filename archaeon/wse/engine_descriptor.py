"""ONE tracked engine descriptor for every consumer (campaign 2, group F; L-002 / L-003).

The production engine is described by the deploy pin Daedalus keeps under
SerendipityFoundry/SerendipityFoundryEngine/deploy/DEPLOYED_BUILD_M2.json (endpoint,
instance id, schema, source hash). This module reads THAT file and resolves the client
certificate beside the client package; no module keeps its own base URL or cert default.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

REPO = Path(__file__).resolve().parents[2]
DESCRIPTOR = REPO / "SerendipityFoundry" / "SerendipityFoundryEngine" / "deploy" / "DEPLOYED_BUILD_M2.json"
CACERT = REPO / "SerendipityFoundry" / "SerendipityFoundryClient" / "config" / "m2.crt"


def engine(descriptor: Path = DESCRIPTOR, cacert: Path = CACERT) -> Dict[str, object]:
    d = json.loads(Path(descriptor).read_text(encoding="utf-8"))
    return {
        "base_url": d["endpoint"],
        "engine_instance_id": d.get("engine_instance_id"),
        "schema_version": d.get("schema_version"),
        "engine_source_hash": d.get("engine_source_hash"),
        "cacert": str(cacert),
        "cacert_exists": Path(cacert).exists(),
        "descriptor": str(descriptor),
        "pinned_at": d.get("pinned_at"),
        "pinned_by": d.get("pinned_by"),
    }
