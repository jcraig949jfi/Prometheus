"""Digest every run directory of the campaign (read-only): per-run sha256 over its files, one digest-of-digests.

Writes LOCAL/RUNDIR_DIGEST.jsonl (per-run file list + bytes + sha256; ~16 MB, not committed) and the committed
receipts/RUNDIR_DIGEST_ROOT.json (root digest + integrity summary). Slow (~10 GB); run in the background.
    python roles/Bellerophon/forensics_2026-09-23/tools/rundir_digest.py"""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import load as Ld  # noqa: E402


def main() -> None:
    root = Ld.WD / "runs"
    names = sorted(os.listdir(root))
    lines = []; missing = []
    top = hashlib.sha256()
    for i, rid in enumerate(names):
        d = root / rid
        files = sorted(os.listdir(d))
        h = hashlib.sha256(); total = 0
        for fn in files:
            b = (d / fn).read_bytes(); total += len(b)
            h.update(fn.encode() + b"\0" + hashlib.sha256(b).digest())
        for need in ("config.json", "summary.json"):
            if need not in files:
                missing.append((rid, need))
        dg = h.hexdigest()
        top.update(rid.encode() + b"\0" + bytes.fromhex(dg))
        lines.append({"run": rid, "files": files, "bytes": total, "sha256": dg})
        if i % 5000 == 0:
            print(i, rid, flush=True)
    Ld.OUT.mkdir(parents=True, exist_ok=True); Ld.LOCAL.mkdir(parents=True, exist_ok=True)
    (Ld.LOCAL / "RUNDIR_DIGEST.jsonl").write_text("".join(json.dumps(x, sort_keys=True) + "\n" for x in lines), encoding="utf-8", newline="\n")
    summary = {"run_dirs": len(names), "root_sha256": top.hexdigest(), "total_bytes": sum(x["bytes"] for x in lines),
               "missing_required_files": missing, "file_sets": {}}
    fs = {}
    for x in lines:
        k = ",".join(x["files"]); fs[k] = fs.get(k, 0) + 1
    summary["file_sets"] = fs
    (Ld.OUT / "RUNDIR_DIGEST_ROOT.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
