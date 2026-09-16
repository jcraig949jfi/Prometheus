"""CUT format v1 provenance (Amendment 3, R34 / N4; Nyx, 2026-09-16): every cut records the provenance-grade object actually
inspected and the payload hash of every file its evidence refs name.

Adds to each cut fossil's `cut` block (v0 fields untouched; the v0 records stay in git history at ef05d395f):

    cut.provenance = {
      "schema": "nyx.atlas/1-provenance",
      "migrated_at", "migrated_from",
      "provenance_grade_read":  ORIGINAL_ARTIFACT | ... | UNKNOWN   (from Techne's record: ORIGINAL_AUTHORITATIVE_RELEASE
                                 -> ORIGINAL_ARTIFACT; RECONSTRUCTION -> RECONSTRUCTION; TRANSCRIPTION -> LATER_TRANSCRIPTION;
                                 else UNKNOWN; per R34 the grade POPULATES from Techne's provenance and Harmonia may re-grade)
      "source_object_id":       Techne's source_origin artifact (url+sha256, or repo@commit)
      "payload_manifest_id":    Techne's recorded tree_sha256 (+ n_files)
      "host_tree_matches_record": True/False/None  (from the bodies receipt on this host)
      "files_read": [ {path, payload_hash_read (bytes on THIS host), techne_recorded_hash, match, refs} ]
      "unresolved_refs": [...]   refs that name no file under the vault (directories, receipts, prose)
    }

populate() is called by author.Cut.save() for every new cut; migrate() back-fills the existing ones.
Refs recognised: vault:<id>/<path>[:lines]  and the 09-13 form F:/Prometheus/vault/fossils/<id>/<path>[:lines].
Run from the worktree with TECHNE_FOSSIL_VAULT set:  python -m nyx.atlas.migrate_v1
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
from pathlib import Path

from nyx.atlas.schema import ROOT, load_fossils, validate_fossil
from techne.fossils import vault

REPO = ROOT.parent.parent
SPEC = REPO / "techne" / "fossils" / "specimens"
GRADES = {"ORIGINAL_AUTHORITATIVE_RELEASE": "ORIGINAL_ARTIFACT", "RECONSTRUCTION": "RECONSTRUCTION", "TRANSCRIPTION": "LATER_TRANSCRIPTION"}


def techne_hashes(fid: str) -> dict:
    out = {}
    p = SPEC / fid / "UPSTREAM_HASHES.txt"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            parts = line.split(None, 2)
            if len(parts) == 3 and len(parts[0]) == 64:
                out[parts[2].strip().replace("\\", "/")] = parts[0]
    return out


def grade_from_record(rec: dict) -> str:
    s = (rec.get("nyx_handoff") or {}).get("where_it_came_from", "")
    for k, v in GRADES.items():
        if k in s:
            return v
    return "UNKNOWN"


def split_ref(ref: str, fid: str):
    """-> relative path under the body (or None)."""
    m = re.match(r"vault:([^/]+)/(.+)", ref)
    if m and m.group(1) == fid:
        rel = m.group(2)
    else:
        m = re.match(r"[A-Z]:/Prometheus/vault/fossils/([^/]+)/(.+)", ref)
        if not (m and m.group(1) == fid):
            return None
        rel = m.group(2)
    rel = re.sub(r"\s*\(.*$", "", rel)                  # strip a trailing parenthetical note
    rel = rel.split(",")[0].split(";")[0]
    rel = re.sub(r":[0-9][0-9,\-]*.*$", "", rel)         # strip :lines and anything after
    return rel.rstrip("/").strip()


def populate(f: dict, fid: str, host_matches=None, migrated_from: str = "nyx.atlas/0 (record at origin/main ef05d395f)") -> dict:
    """Fill f['cut']['provenance'] from Techne's record and the bytes on this host."""
    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    rec = json.loads((SPEC / fid / "record.json").read_text(encoding="utf-8"))
    th = techne_hashes(fid)
    body = vault.body_dir(fid)
    refs = [e["ref"] for e in f["cut"]["evidence"]] + [o["evidence"]["ref"] for o in f["organs"]]
    files, unresolved, seen = [], [], {}
    for ref in refs:
        rel = split_ref(ref, fid)
        p = (body / rel) if rel else None
        if (p is None or not p.is_file()) and rel and " " in rel and (body / rel.split(" ")[0]).is_file():
            rel = rel.split(" ")[0]; p = body / rel          # a path followed by prose
        if p is None or not p.is_file():
            hit = False
            for piece in ref.split(";"):                     # refs naming several files
                r2 = split_ref(piece.strip(), fid)
                if r2 and (body / r2).is_file():
                    rel, p, hit = r2, body / r2, True
                    break
            if not hit:
                unresolved.append(ref[:160])
                continue
        if rel in seen:
            seen[rel]["refs"] += 1
            continue
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        trec = th.get(rel) or th.get("tree/" + rel) or th.get(rel.replace("upstream/", "", 1))
        row = {"path": rel, "payload_hash_read": h, "techne_recorded_hash": trec, "match": (h == trec) if trec else None, "refs": 1}
        seen[rel] = row
        files.append(row)
    arts = (rec.get("source_origin") or {}).get("artifacts", [])
    src = "; ".join((a.get("url", "") + ("@" + a["commit"] if a.get("commit") else "") + (" sha256:" + a["sha256"] if a.get("sha256") else "")) for a in arts) or "UNKNOWN"
    f["cut"]["provenance"] = {
        "schema": "nyx.atlas/1-provenance", "migrated_at": stamp, "migrated_from": migrated_from,
        "provenance_grade_read": grade_from_record(rec), "grade_basis": "Techne record nyx_handoff.where_it_came_from (populated per R34; Harmonia may re-grade)",
        "source_object_id": src,
        "payload_manifest_id": f"techne tree_sha256 {rec.get('hashes', {}).get('tree_sha256', 'UNKNOWN')} ({rec.get('hashes', {}).get('n_files', '?')} files)",
        "host_tree_matches_record": host_matches, "host": "M2 (SPECTREX5), bodies receipt nyx/atlas/samples/stageA_bodies_m2_2026-09-16.json",
        "files_read": files, "unresolved_refs": unresolved,
    }
    return f["cut"]["provenance"]


def migrate(bodies_receipt: Path) -> None:
    receipt = {r["fossil_id"]: r for r in json.loads(bodies_receipt.read_text(encoding="utf-8"))["rows"]}
    n_files = n_match = n_mismatch = n_unres = 0
    for f in load_fossils():
        if f["cut"]["state"] in ("NOT_CUT", "BLOCKED"):
            continue
        fid = f["whole_system"]["FOSSIL_ID"]["value"]
        pv = populate(f, fid, receipt.get(fid, {}).get("verify_matches"))
        files, unresolved = pv["files_read"], pv["unresolved_refs"]
        n_files += len(files); n_match += sum(1 for r in files if r["match"]); n_mismatch += sum(1 for r in files if r["match"] is False); n_unres += len(unresolved)
        probs = [x for x in validate_fossil(f) if "outside the provisional list" not in x]
        assert not probs, (fid, probs)
        (ROOT / "fossils" / f"{fid}.json").write_text(json.dumps(f, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(f"{fid:40s} grade {pv['provenance_grade_read']:18s} files {len(files):2d} match {sum(1 for r in files if r['match'])} mismatch {sum(1 for r in files if r['match'] is False)} unresolved {len(unresolved)}")
    print(f"TOTAL files_read {n_files} match {n_match} mismatch {n_mismatch} unresolved refs {n_unres}")


if __name__ == "__main__":
    migrate(ROOT / "samples" / "stageA_bodies_m2_2026-09-16.json")
