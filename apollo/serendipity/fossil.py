"""fossil.py -- Apollo's FossilEmitter + ProvenanceAdapter boundary (charter S2/S4).

A fossil is the unit of Apollo output: enough that another system can reconstruct the
structure, see where it worked/failed, inspect its lineage, and reproduce its evaluation.
Storage is not a landfill (S7) -- emit informative cases, not millions of duplicates.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path


def capture(client, artifact_id: str) -> dict:
    """Pull the durable, host-authoritative facts about one organism."""
    out = {"artifact_id": artifact_id}
    for suffix, key in (("", "artifact"), ("/genotype", "genotype"),
                        ("/lineage", "lineage")):
        try:
            out[key] = client.get(f"/v0/artifacts/{artifact_id}{suffix}")
        except Exception as e:  # noqa: BLE001
            out[key] = {"_error": f"{type(e).__name__}: {e}"}
    return out


def provenance_hash(fossil: dict) -> str:
    """Content hash over everything except volatile/self fields."""
    volatile = {"emitted_utc", "provenance_hash", "fossil_path"}
    core = {k: v for k, v in fossil.items() if k not in volatile}
    blob = json.dumps(core, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(blob).hexdigest()


def emit(fossil: dict, out_dir: str) -> str:
    """Write one fossil JSON, stamped with an emit time and a provenance hash."""
    d = Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    fossil["emitted_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    fossil["provenance_hash"] = provenance_hash(fossil)
    fid = fossil.get("run_id", "fossil") + "_" + fossil["provenance_hash"][7:19]
    path = d / f"{fid}.json"
    path.write_text(json.dumps(fossil, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return str(path)
