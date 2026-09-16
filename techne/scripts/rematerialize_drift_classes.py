"""Usage: python techne/scripts/rematerialize_drift_classes.py [census.json]  (run from the repo root)

Classify every DRIFT row of the M2 rematerialize census by defect class, from the bytes
kept at upstream.drifted/ against the tracked hash list. Diagnostic; writes a JSON beside
the census. Classes per file: SAME, RECORD_IS_CRLF (fetched->CRLF reproduces the recorded
hash), RECORD_IS_LF_FETCHED_CRLF (the reverse), MISSING_IN_FETCH, OTHER."""
import hashlib, json, pathlib, sys, collections
from techne.fossils import vault, harvest

CENSUS = sys.argv[1] if len(sys.argv) > 1 else "techne/fossils/REMATERIALIZE_M2_2026-09-16_run2.json"
OUT = CENSUS.replace(".json", "_drift_classes.json")
census = json.load(open(CENSUS, encoding="utf-8"))
out = {"schema": "techne.fossil.rematerialize_drift_classes/1", "census": "REMATERIALIZE_M2_2026-09-16_run2.json", "rows": []}
for r in census["rows"]:
    if r["status"] != "DRIFT":
        continue
    sid = r["specimen_id"]
    want = harvest._want_rows(sid)
    root = vault.body_dir(sid) / "upstream.drifted"
    c = collections.Counter(); missing = []; other = []
    for rel, (h, n) in want.items():
        p = root / rel
        if not p.exists():
            c["MISSING_IN_FETCH"] += 1; missing.append(rel); continue
        b = p.read_bytes()
        if hashlib.sha256(b).hexdigest() == h: c["SAME"] += 1
        elif hashlib.sha256(b.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")).hexdigest() == h: c["RECORD_IS_CRLF"] += 1
        elif hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest() == h: c["RECORD_IS_LF_FETCHED_CRLF"] += 1
        else: c["OTHER"] += 1; other.append(rel)
    kinds = [a["kind"] for a in __import__("techne.fossils.record", fromlist=["load"]).load(sid)["source_origin"]["artifacts"]]
    residue = [m for m in missing if "__pycache__" in m or m.endswith((".pyc", ".o", ".a", ".so", ".eo", ".exe")) or (root / m).suffix == "" and "/bin/" in m or m.rsplit("/", 1)[-1] in ("flisp", "pforth", "pforth_standalone", "espresso", "pfdicdat.h", "pforth.dic")]
    row = {"specimen_id": sid, "artifact_kinds": kinds, "n_recorded": len(want), "classes": dict(c),
           "missing_in_fetch": missing[:20], "missing_is_execution_residue": len(residue), "other": other[:10]}
    if c["OTHER"] == 0 and c["RECORD_IS_LF_FETCHED_CRLF"] == 0 and c["MISSING_IN_FETCH"] == len(residue):
        row["verdict"] = "RECORD_DEFECT_ONLY (CRLF-converted hashes and/or execution residue in the hash list)"
    else:
        row["verdict"] = "NEEDS_LOOK"
    out["rows"].append(row)
    print(sid, kinds, dict(c), "residue", len(residue), "|", row["verdict"])
pathlib.Path(OUT).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
