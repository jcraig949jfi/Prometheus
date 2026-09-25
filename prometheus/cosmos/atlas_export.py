"""Export a CWE store as Atlas-shaped JSONL (atlas/sql/002_model_v2.sql: atlas.edge, atlas.fact).

CWE never needs Atlas online; this writes rows an Atlas harvest adapter can upsert. Edge
convention follows Atlas (src = the later/derived world, dst = the parent). CWE edge kinds
with no Atlas vocabulary entry keep their CWE name and say so in `detail`; the Atlas seat
owns the vocabulary and decides.

  python -m prometheus.cosmos.atlas_export <store_dir> <out_dir>
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ATLAS_RELATION = {"DEFORMATION_OF": "DEFORMATION_OF", "TRANSPLANT_OF": "TRANSPLANT_OF"}
METHOD = "cosmos.cwe/0.1 atlas_export"


def export(store_dir: Path, out_dir: Path) -> dict:
    db = sqlite3.connect(str(Path(store_dir) / "cwe.sqlite"))
    out_dir.mkdir(parents=True, exist_ok=True)
    n_e = n_f = 0
    with open(out_dir / "atlas_edge.jsonl", "w", encoding="utf-8", newline="\n") as fe:
        for src, dst, kind, delta in db.execute("SELECT src, dst, kind, delta FROM edges"):
            rel = ATLAS_RELATION.get(kind, kind)
            fe.write(json.dumps({"src_type": "cosmos_world", "src_key": dst, "dst_type": "cosmos_world", "dst_key": src,
                                 "relation": rel, "lineage_kind": "SCIENTIFIC", "reason": "UNKNOWN", "basis": "DECLARED",
                                 "confidence": "HIGH", "method": METHOD,
                                 "detail": (delta if kind in ATLAS_RELATION else "CWE kind %s (not in atlas vocabulary); %s" % (kind, delta))},
                                sort_keys=True) + "\n")
            n_e += 1
    with open(out_dir / "atlas_fact.jsonl", "w", encoding="utf-8", newline="\n") as ff:
        for wid, rep, eps, verdict, margin, se, purpose in db.execute(
                "SELECT world_id, replicate, episodes, verdict, margin, margin_se, purpose FROM runs"):
            ff.write(json.dumps({"fact_key": "cosmos_world|%s|SELECTIVE_PAYS.v1|r%d_e%d" % (wid, rep, eps), "layer": "OBSERVED",
                                 "kind": "phenomenon_verdict", "subject_type": "cosmos_world", "subject_key": wid,
                                 "name": "SELECTIVE_PAYS.v1.margin", "value_text": verdict, "value_num": margin,
                                 "band_low": margin - 2 * se, "band_high": margin + 2 * se, "status": "REPORTED",
                                 "author": "Cosmos", "method": METHOD + " purpose=" + purpose}, sort_keys=True) + "\n")
            n_f += 1
        for law_id, version, parent, body, fh in db.execute("SELECT law_id, version, parent, body, freeze_hash FROM laws"):
            ev = [s for (s,) in db.execute("SELECT status FROM law_events WHERE law_id=? ORDER BY t", (law_id,))]
            ff.write(json.dumps({"fact_key": "cosmos_law|%s" % law_id, "layer": "CONCLUDED", "kind": "candidate_law",
                                 "subject_type": "cosmos_law", "subject_key": law_id, "name": "law.v%d" % version,
                                 "value_text": json.loads(body)["law"]["law"], "value_json": {"events": ev, "parent": parent,
                                                                                               "freeze_hash": fh},
                                 "status": "REPORTED", "author": "Cosmos", "method": METHOD}, sort_keys=True) + "\n")
            n_f += 1
    return {"edges": n_e, "facts": n_f}


if __name__ == "__main__":
    print(export(Path(sys.argv[1]), Path(sys.argv[2])))
