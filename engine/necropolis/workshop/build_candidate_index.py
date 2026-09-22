"""CANDIDATE_INDEX.jsonl: every forensic-instrument candidate the seven scouts returned
(harvest charter XIII item 1 "candidates discovered" vs item 2 "inspected"), joined to
what was measured about it and to the registry row it became, if any.

LAYER: NECROPOLIS VALIDATION.  Inputs are the scout table, the import-verify and
file-exists measurements (harvest scratch, copied into candidates/ as read-only
evidence), and TOOLS.jsonl.  Nothing here executes a candidate.

    python engine/necropolis/workshop/build_candidate_index.py <candidates_index.json> <import_verify.json> <file_exists.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def registry_by_path() -> dict[str, str]:
    p = HERE / "TOOLS.jsonl"
    out = {}
    if p.exists():
        for l in p.read_text(encoding="utf-8").splitlines():
            if l.strip():
                r = json.loads(l)
                for k in ("current_path", "historical_path"):
                    if r.get(k):
                        out[r[k]] = r["tool_id"]
    return out


def main(argv) -> int:
    cands = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    imp = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    exists = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    reg = registry_by_path()
    rows, counts = [], {}
    for i, c in enumerate(cands, 1):
        files = c.get("_files") or [c["path"].split("::")[0]]
        files = [f.split("::")[0] for f in files]
        fe = {f: exists.get(f) for f in files}
        iv = {f: (imp.get(f) or {}).get("import") for f in files}
        tool = next((reg[f] for f in files if f in reg), None)
        if tool:
            disp = "REGISTERED"
        elif not any(fe.values()):
            disp = "ABSENT_AT_HEAD" if all(v is False for v in fe.values()) else "UNVERIFIED_PATH"
        elif any(v == "IMPORT_OK" for v in iv.values()):
            disp = "IMPORTS_UNREGISTERED"
        elif any(v and v.startswith("IMPORT_FAIL") for v in iv.values()):
            disp = "IMPORT_FAILS_UNREGISTERED"
        else:
            disp = "PRESENT_UNREGISTERED"
        counts[disp] = counts.get(disp, 0) + 1
        rows.append({"cand_id": f"CAND-{i:03d}", "scout": c["scout"], "name": c["name"], "path": c["path"], "kind": c.get("kind"),
                     "computes": (c.get("computes") or "")[:400], "deps": c.get("deps"), "files": files, "file_exists": fe,
                     "import_verify": iv, "registered_as": tool, "disposition": disp,
                     "scout_control_note": (c.get("control") or "")[:300], "scout_caveat": (c.get("caveat") or "")[:300],
                     "forbidden_inference": "a scout row is a LEAD (charter IX); only a registry row with a Keeper control is an instrument"})
    out = HERE / "CANDIDATE_INDEX.jsonl"
    out.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8", newline="\n")
    print(len(rows), "candidates ->", out)
    print(json.dumps(counts, indent=0))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
