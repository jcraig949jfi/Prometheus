"""The consumer-facing enumeration of the fossil vault (batch 05 charter: ARCHAEON VISIBILITY).

    python -m techne.fossils.catalog                 one line per fossil
    python -m techne.fossils.catalog --json [--out F]  machine-readable rows
    from techne.fossils.catalog import enumerate_fossils   (Python API)

Records are the TRACKED half of the vault (techne/fossils/specimens/<id>/record.json), so any
checkout or worktree at or after the commit that added a record can enumerate it -- with or
without the host-local bodies. Each row says whether a body is present ON THIS HOST; absence of
a body is never absence of the record. This module reads only; it is the same interface for
Archaeon, Nyx, or anyone else, and it names no organ and scores nothing.

Note the homonym: archaeon/fossils.py reads SFE/PEW EXPERIMENT fossils from the engine ledger;
this module enumerates Techne's preserved COMPUTATIONAL fossils. The 2026-09-11 "ZERO fossils"
tick records were the former (a pinned worktree without archaeon/config.local.json; see
archaeon/docs/OPERATIONS.md), not this vault.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

from . import vault

FIELDS = ("fossil_id", "canonical_name", "lineage", "human_purpose", "version", "era", "language",
          "domain", "run_status", "test_status", "source_type", "license_spdx", "acquisition_tags",
          "tree_sha256", "record_path", "recipe_path", "receipts", "body_present_on_this_host", "body_path")


def enumerate_fossils(check_bodies: bool = True) -> list[dict]:
    rows = []
    for rec_path in sorted(vault.SPECIMENS.glob("*/record.json")):
        r = json.loads(rec_path.read_text(encoding="utf-8"))
        sid = r["specimen_id"]
        sd = rec_path.parent
        body = vault.body_dir(sid)
        def rel(p):
            try:
                return str(p.relative_to(vault.REPO)).replace("\\", "/")
            except ValueError:
                return str(p).replace("\\", "/")
        hs = r.get("human_capability_summary") or {}
        obs = r.get("observability") or {}
        tags = r.get("acquisition_tags", [])
        # known historical disposition: the human record's verdict, drawn only from explicit tags
        disp = [t for t in tags if t in ("loser", "known_bad", "known_bad_lineage", "failed_branch",
                                         "superseded_design", "contested_design", "historical_redesign",
                                         "successor", "predecessor", "pathology", "documented_pathology")]
        mirror = _mirror_status(tree_sha256=(r.get("hashes") or {}).get("tree_sha256", ""))
        rows.append({
            "fossil_id": sid,
            "canonical_name": r.get("canonical_name", ""),
            "lineage": r.get("lineage", ""),
            "ancestry": r.get("lineage_relations", []),
            "human_purpose": hs.get("built_to") or r.get("known_human_problem_solved", ""),
            "human_environmental_pressure": r.get("human_environmental_pressure", "") or hs.get("pressure", ""),
            "version": r.get("version", ""),
            "era": r.get("era", ""),
            "language": r.get("language", []),
            "domain": r.get("domain", []),
            "run_status": r.get("run_classification", ""),
            "test_status": r.get("test_classification", ""),
            "observability": obs,
            "oracle_backed": obs.get("ORACLE_BACKED", "unknown"),
            "intervention_ready": obs.get("INTERVENTION_READY", "unknown"),
            "known_historical_disposition": disp,
            "source_type": r.get("source_type", ""),
            "license_spdx": (r.get("license") or {}).get("spdx", ""),
            "acquisition_tags": tags,
            "tree_sha256": (r.get("hashes") or {}).get("tree_sha256", ""),
            "record_path": rel(rec_path),
            "recipe_path": rel(sd / "recipe.json") if (sd / "recipe.json").exists() else None,
            "receipts": [x.get("receipt") for x in r.get("receipts", [])],
            "body_present_on_this_host": (body / "upstream").exists() if check_bodies else None,
            "body_path": str(body),
            "mirror_available": mirror,
        })
    return rows


_MIRROR_INDEX = {"loaded": False, "specimens": {}}


def _mirror_status(tree_sha256=""):
    """Whether an off-host mirror holds this body, read from the mirror's MIRROR_INDEX.json if a
    mirror destination is configured (techne/config.local.json 'fossil_mirror'). Absent config or
    index -> 'no_mirror_configured'. Records availability without needing the body."""
    if not _MIRROR_INDEX["loaded"]:
        _MIRROR_INDEX["loaded"] = True
        cfg = vault.REPO / "techne" / "config.local.json"
        try:
            dest = json.loads(cfg.read_text(encoding="utf-8")).get("fossil_mirror")
            if dest:
                idx = pathlib.Path(dest) / "MIRROR_INDEX.json"
                if idx.exists():
                    _MIRROR_INDEX["specimens"] = json.loads(idx.read_text(encoding="utf-8")).get("specimens", {})
                    _MIRROR_INDEX["configured"] = True
        except (OSError, ValueError):
            pass
    if not _MIRROR_INDEX.get("configured"):
        return "no_mirror_configured"
    hits = [sid for sid, v in _MIRROR_INDEX["specimens"].items() if v.get("tree_sha256") == tree_sha256]
    return "mirrored" if hits else "not_mirrored"


def catalog(check_bodies: bool = True) -> dict:
    rows = enumerate_fossils(check_bodies)
    return {"schema": "techne.fossil.catalog/1",
            "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "records_root": str(vault.SPECIMENS).replace("\\", "/"),
            "vault_root_on_this_host": str(vault.vault_root()),
            "fossils": len(rows),
            "runnable": sum(1 for r in rows if str(r["run_status"]).startswith("RUNNABLE")),
            "bodies_present_on_this_host": sum(1 for r in rows if r["body_present_on_this_host"]),
            "fields": list(FIELDS),
            "rows": rows}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--no-body-check", action="store_true", help="do not touch the host-local vault at all")
    a = ap.parse_args(argv)
    c = catalog(check_bodies=not a.no_body_check)
    if a.json or a.out:
        text = json.dumps(c, indent=1)
        if a.out:
            pathlib.Path(a.out).write_text(text + "\n", encoding="utf-8", newline="\n")
            print("catalog", a.out, c["fossils"], "fossils")
        else:
            print(text)
    else:
        for r in c["rows"]:
            print("%-38s %-28s %-24s body=%s  %s" % (r["fossil_id"], r["run_status"], r["test_status"],
                  {True: "yes", False: "no", None: "?"}[r["body_present_on_this_host"]], r["record_path"]))
        print("fossils %d  runnable %d  bodies_present_on_this_host %d" % (c["fossils"], c["runnable"], c["bodies_present_on_this_host"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
