#!/usr/bin/env python3
"""
build_organs.py — regenerate ORGANS.jsonl from the residue sections of validating dossiers.

F5 (ROLES.md): Doctor Frankenstein harvests only certified organs, and an organ is certified only
by appearing in a Necromancer dossier's `residue`. This script is the ONLY writer of ORGANS.jsonl.

Each residue string becomes one organ row. The organ_type is inferred from the residue bucket and
then refined by keyword (a detector is not a verifier; a corpus is not a schema). Rows carry a
stable organ_id = <agent_lower>.<bucket>.<index> so monsters can reference them across rebuilds
as long as dossier residue order is stable (residue is append-only by convention).

Organ rows can be ANNOTATED by the Keeper in ORGAN_NOTES.json (keyed by organ_id) — status,
constraints, known failures recorded against the organ (F6). Notes survive regeneration.

Run:  python engine/necropolis/build_organs.py
"""
import json, os, glob, re

HERE = os.path.dirname(os.path.abspath(__file__))
def here(*a): return os.path.join(HERE, *a)

BUCKET_TYPE = {
    "salvageable_code": "transform",
    "salvageable_data": "failure_corpus",
    "salvageable_schemas": "interface_contract",
    "salvageable_operators": "routing_mechanism",
    "salvageable_tests": "measurement_instrument",
    "representation_hints": "informative_failure_mode",
}
ORGAN_TYPES = ["producer", "representation", "detector", "selector", "verifier", "consumer",
               "transform", "measurement_instrument", "routing_mechanism", "search_procedure",
               "interface_contract", "failure_corpus", "informative_failure_mode"]

REFINE_BUCKETS = {"salvageable_code", "salvageable_operators"}  # hints/schemas/data/tests keep their bucket type
REFINE = [  # (regex over residue text, organ_type) — first match wins, applied only to REFINE_BUCKETS
    (r"detector", "detector"),
    (r"harness|null|floor|decoy|check:|gate replica|base-rate", "measurement_instrument"),
    (r"generator|traps? ", "measurement_instrument"),
    (r"engines?\b|primitives", "producer"),
    (r"parser|_parse_|encode_dataset|load_", "transform"),
    (r"prompt|stance|scaffold", "representation"),
    (r"selector|picker|priority seam|_forge_priority", "selector"),
    (r"request path|DR path|-> Pythia", "consumer"),
    (r"retry|backoff", "routing_mechanism"),
    (r"knockout|ablation", "measurement_instrument"),
    (r"ledger|reports|results\.jsonl|dataset|corpus|base-rate series|histogram", "failure_corpus"),
    (r"shape|contract|schema", "interface_contract"),
]

def refine(text, default):
    for rx, t in REFINE:
        if re.search(rx, text, re.I):
            return t
    return default

def first_path(text):
    m = re.search(r"([A-Za-z0-9_./\-]+\.(?:py|jsonl|json|md)(?:::[A-Za-z0-9_+, ]+)?|(?=[^/\s]*[A-Za-z])[A-Za-z0-9_./\-]+/)", text)
    return m.group(1) if m else ""

def main():
    notes = {}
    if os.path.exists(here("ORGAN_NOTES.json")):
        notes = json.load(open(here("ORGAN_NOTES.json"), encoding="utf-8"))
    rows = []
    for f in sorted(glob.glob(here("dossiers", "*.dossier.json"))):
        d = json.load(open(f, encoding="utf-8"))
        aid = d["identity"]["agent_id"]
        if aid.startswith("PLACEHOLDER"): continue
        res = d.get("residue", {})
        cls = d.get("disposition", {}).get("classification")
        axis = d.get("autopsy", {}).get("death_axis", "undetermined")
        for bucket, default_type in BUCKET_TYPE.items():
            for i, text in enumerate(res.get(bucket, [])):
                oid = f"{aid.lower()}.{bucket.replace('salvageable_','')}.{i}"
                row = {
                    "organ_id": oid,
                    "source_agent": aid,
                    "source_dossier": os.path.relpath(f, HERE).replace("\\", "/"),
                    "source_classification": cls,
                    "source_death_axis": axis,
                    "residue_bucket": bucket,
                    "organ_type": refine(text, default_type) if bucket in REFINE_BUCKETS else default_type,
                    "location": first_path(text),
                    "function": text,
                    "status": "certified_by_dossier",
                    "failures_recorded_against": [],
                }
                row.update(notes.get(oid, {}))
                rows.append(row)
    with open(here("ORGANS.jsonl"), "w", encoding="utf-8") as fh:
        for r in rows: fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    by_type = {}
    for r in rows: by_type[r["organ_type"]] = by_type.get(r["organ_type"], 0) + 1
    print(f"ORGANS.jsonl: {len(rows)} organs from {len({r['source_agent'] for r in rows})} dossiers")
    for t in ORGAN_TYPES:
        if by_type.get(t): print(f"  {t:26s} {by_type[t]}")

if __name__ == "__main__":
    main()
