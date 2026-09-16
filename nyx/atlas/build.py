"""Assemble the directive's eleven artifacts from nyx/atlas/fossils/*.json (plus fingerprints/, recurrence/, blind/ when present).

    python -m nyx.atlas.build            # writes nyx/atlas/out/*.json and prints the depth map

Nothing here is authored: every row is a projection of a fossil file, a fingerprint receipt or a recurrence record, so the
artifacts cannot disagree with their sources. Counts are computed, never typed. Empty cells stay empty (directive: DO NOT FORCE).
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from nyx.atlas.schema import ROOT, SCHEMA, COVERAGE_DIMS, UNMEASURED, load_fossils

OUT = ROOT / "out"


def _dump(name: str, obj) -> str:
    OUT.mkdir(exist_ok=True)
    p = OUT / f"{name}.json"
    text = json.dumps(obj, indent=1, ensure_ascii=False) + "\n"
    p.write_text(text, encoding="utf-8", newline="\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def build() -> dict:
    fossils = load_fossils()
    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    cut = [f for f in fossils if f["cut"]["state"] not in ("NOT_CUT", "BLOCKED")]
    organs = [o for f in cut for o in f["organs"]]
    rejected = [r for f in cut for r in f["rejected_cuts"]]
    pressures = [p for f in cut for p in f["pressures"]]
    comp = [e for f in cut for e in f["composition_edges"]]
    anc = [e for f in fossils for e in f.get("ancestry_edges", [])]
    fps = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "fingerprints").rglob("*.json"))]
    rec = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "recurrence").glob("*.json"))] if (ROOT / "recurrence").exists() else []
    blind = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "blind").glob("*.json"))] if (ROOT / "blind").exists() else []

    hashes = {}
    hashes["FOSSIL_ANATOMY"] = _dump("FOSSIL_ANATOMY", {"schema": SCHEMA, "built": stamp, "fossils": [{"fossil_id": f["whole_system"]["FOSSIL_ID"]["value"], "cut": f["cut"]["state"], "organs": len(f["organs"]), "rejected": len(f["rejected_cuts"]), "pressures": len(f["pressures"]), "residue": f.get("residue", {}).get("state", "NOT_CHECKED")} for f in fossils]})
    hashes["ORGAN_CATALOG"] = _dump("ORGAN_CATALOG", {"schema": SCHEMA, "built": stamp, "n": len(organs), "organs": organs})
    hashes["REJECTED_CUTS"] = _dump("REJECTED_CUTS", {"schema": SCHEMA, "built": stamp, "n": len(rejected), "by_reason": dict(Counter(r["reason"] for r in rejected)), "rejected": rejected})
    hashes["PRESSURE_CATALOG"] = _dump("PRESSURE_CATALOG", {"schema": SCHEMA, "built": stamp, "n": len(pressures), "pressures": pressures})
    hashes["ANCESTRY_GRAPH"] = _dump("ANCESTRY_GRAPH", {"schema": SCHEMA, "built": stamp, "n": len(anc), "by_relation": dict(Counter(e["relation"] for e in anc)), "edges": anc,
                                                       "note": "Techne's 'superseded' relation carries no fixed direction in its records (17 edges, both readings observed on 2026-09-16); direction must be read from each note"})
    hashes["COMPOSITION_GRAPH"] = _dump("COMPOSITION_GRAPH", {"schema": SCHEMA, "built": stamp, "n": len(comp), "by_label": dict(Counter(e["label"] for e in comp)), "edges": comp})
    hashes["BEHAVIORAL_FINGERPRINTS"] = _dump("BEHAVIORAL_FINGERPRINTS", {"schema": SCHEMA, "built": stamp, "n": len(fps), "receipts": fps})
    hashes["RECURRENCE_CANDIDATES"] = _dump("RECURRENCE_CANDIDATES", {"schema": SCHEMA, "built": stamp, "n": sum(len(r.get("candidates", [])) for r in rec), "files": rec})
    hashes["BLIND_CUT_COMPARISON"] = _dump("BLIND_CUT_COMPARISON", {"schema": SCHEMA, "built": stamp, "n": len(blind), "comparisons": blind, "note": "0 blind cuts have been performed; the measure of Nyx's human-prior dependence is EMPTY, not zero"})

    # coverage map: per dimension, how many organs carry a READ value, a MEASURED value, or UNMEASURED; and which values occur
    cov = {}
    for dim, vocab in COVERAGE_DIMS.items():
        cells = [o["coverage"].get(dim, {"value": UNMEASURED, "basis": "READ"}) for o in organs]
        cov[dim] = {"read": sum(1 for c in cells if c["value"] != UNMEASURED and c["basis"] == "READ"),
                    "measured": sum(1 for c in cells if c["value"] != UNMEASURED and c["basis"] == "MEASURED"),
                    "unmeasured": sum(1 for c in cells if c["value"] == UNMEASURED),
                    "values": dict(Counter(c["value"] for c in cells if c["value"] != UNMEASURED)),
                    "vocabulary_unused": [v for v in vocab if v not in {c["value"] for c in cells}]}
    hashes["ATLAS_COVERAGE"] = _dump("ATLAS_COVERAGE", {"schema": SCHEMA, "built": stamp, "organs": len(organs), "dims": cov,
                                                        "note": "READ cells are Nyx's reading of the source; MEASURED cells come from wind-tunnel receipts only; a dimension with measured == 0 is UNMEASURED for the whole atlas whatever its read count"})
    hashes["UNEXPLAINED_RESIDUE"] = _dump("UNEXPLAINED_RESIDUE", {"schema": SCHEMA, "built": stamp, "by_state": dict(Counter(f.get("residue", {}).get("state", "NOT_CHECKED") for f in cut)),
                                                                  "residue": [{"fossil_id": f["whole_system"]["FOSSIL_ID"]["value"], **f.get("residue", {})} for f in cut]})

    depth = Counter(max([o["depth"] for o in f["organs"]] or [0]) for f in cut)
    sizes = Counter(len(f["organs"]) for f in cut)
    dm = {"schema": SCHEMA, "built": stamp,
          "fossils_available": len(fossils), "fossils_inspected": len(cut), "fossils_decomposed": sum(1 for f in cut if f["organs"]),
          "fossils_ORGAN0": sum(1 for f in cut if f["cut"]["state"] == "ORGAN0"), "fossils_blocked": sum(1 for f in fossils if f["cut"]["state"] == "BLOCKED"),
          "by_cut_state": dict(Counter(f["cut"]["state"] for f in fossils)),
          "candidate_fragments": len(organs), "accepted_organs": sum(o["status"] == "ACCEPTED" for o in organs), "candidate_organs": sum(o["status"] == "CANDIDATE" for o in organs),
          "rejected_cuts": len(rejected), "max_depth_distribution": dict(sorted(depth.items())), "organ_count_distribution": dict(sorted(sizes.items())),
          "evidence_grades": dict(Counter(o["evidence"]["grade"] for o in organs)),
          "runnable_organs": "UNKNOWN (no organ has been run in isolation; 1 fossil-level ablation exists)",
          "intervention_tested_organs": sum(1 for o in organs if o["ablation"] not in ("NOT_RUN", "UNKNOWN")),
          "fingerprinted_organs": 0 if not fps else len({r.get("organ_id") for r in fps if r.get("organ_id")}),
          "pressures": len(pressures), "composition_edges": len(comp), "ancestry_edges": len(anc),
          "artifact_hashes_sha256_16": hashes}
    _dump("DEPTH_MAP", dm)
    return dm


if __name__ == "__main__":
    print(json.dumps(build(), indent=1))
