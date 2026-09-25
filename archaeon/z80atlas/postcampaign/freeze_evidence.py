"""Freeze the 72-hour Z80 x Atlas campaign records into a read-only evidence bundle OUTSIDE the worktree/repository
(operator ruling 3, 2026-09-23). The source directory is read, never modified.

    python -m archaeon.z80atlas.postcampaign.freeze_evidence --out C:\\Prometheus-data\\evidence\\z80atlas_campaign_2026-09-19
    python -m archaeon.z80atlas.postcampaign.freeze_evidence --verify C:\\Prometheus-data\\evidence\\z80atlas_campaign_2026-09-19

Bundle layout:
    campaign.tar             every file under the campaign dir (RUNS.jsonl, ATLAS_INDEX.jsonl, PACKET, STATE, GRAMMAR, logs,
                             runs/<family>/<run_id>/*) plus code/ = the campaign code at its commit, byte for byte from git
    MANIFEST.jsonl.gz        one row per member: path, size, sha256
    BUNDLE.json              totals, per-kind counts/sizes, campaign code commit + per-file sha256, grammar digest,
                             sha256 of campaign.tar and MANIFEST.jsonl.gz, key artifact hashes
The repo keeps only BUNDLE.json (archaeon/z80atlas/postcampaign/EVIDENCE_BUNDLE_<date>.json) so the bundle can be verified from git.
Files are set read-only after writing and verification.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import stat
import subprocess
import sys
import tarfile
import time
from collections import Counter
from pathlib import Path

from archaeon.z80atlas.postcampaign.adjudicate import DEFAULT_HIST, CAMPAIGN_COMMIT, REPO, sha

CODE = ["archaeon/z80atlas/engine.py", "archaeon/z80atlas/scheduler.py", "archaeon/z80atlas/grammar.py", "archaeon/z80atlas/vm.py",
        "archaeon/z80atlas/tasks.py", "archaeon/z80atlas/packet.py", "archaeon/z80atlas/CAMPAIGN_CONTRACT.md", "archaeon/z80atlas/run_campaign.bat"]
KEY = ["RUNS.jsonl", "ATLAS_INDEX.jsonl", "PACKET.json", "CAMPAIGN_PACKET.md", "CAMPAIGN_STATE.json", "CAMPAIGN_DONE.json", "GRAMMAR_FROZEN.json", "STATUS.json", "scheduler.log"]


def kind_of(rel: str) -> str:
    if rel.startswith("code/"): return "code"
    if rel.startswith("runs/"): return "run:" + rel.rsplit("/", 1)[-1]
    return "top:" + rel


def freeze(src: Path, out: Path) -> int:
    if out.exists() and any(out.iterdir()):
        print("REFUSED: %s is not empty (bundles are write-once)" % out); return 2
    out.mkdir(parents=True, exist_ok=True)
    full = subprocess.run(["git", "rev-parse", CAMPAIGN_COMMIT], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
    rows, kinds = [], Counter(); ksize = Counter(); t0 = time.time()
    tar_path = out / "campaign.tar"
    with tarfile.open(tar_path, "w", format=tarfile.PAX_FORMAT) as tf:
        def add(rel: str, data: bytes, mtime: float):
            ti = tarfile.TarInfo(rel); ti.size = len(data); ti.mtime = int(mtime); ti.mode = 0o444
            tf.addfile(ti, io.BytesIO(data))
            h = hashlib.sha256(data).hexdigest(); rows.append({"path": rel, "size": len(data), "sha256": h})
            k = kind_of(rel); kinds[k] += 1; ksize[k] += len(data)
        for c in CODE:
            data = subprocess.run(["git", "show", "%s:%s" % (full, c)], cwd=REPO, capture_output=True, check=True).stdout
            add("code/" + c, data, 0)
        n = 0
        for root, dirs, files in os.walk(src):
            dirs.sort(); files.sort()
            for f in files:
                p = Path(root) / f; rel = p.relative_to(src).as_posix()
                add(rel, p.read_bytes(), p.stat().st_mtime); n += 1
                if n % 20000 == 0: print(json.dumps({"files": n, "elapsed_s": round(time.time() - t0)}), flush=True)
    man = out / "MANIFEST.jsonl.gz"
    with gzip.open(man, "wt", encoding="utf-8", newline="\n") as g:
        for r in rows: g.write(json.dumps(r, sort_keys=True) + "\n")
    by = {r["path"]: r for r in rows}
    run_dirs = {r["path"].rsplit("/", 1)[0] for r in rows if r["path"].startswith("runs/")}
    bundle = {"schema": "archaeon.z80atlas.evidence_bundle.v1", "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "source_dir": str(src),
              "source_modified": False, "campaign_code_commit": full, "grammar_digest": json.loads((src / "GRAMMAR_FROZEN.json").read_text(encoding="utf-8")).get("digest"),
              "code_sha256": {c: by["code/" + c]["sha256"] for c in CODE}, "files": len(rows), "bytes": sum(r["size"] for r in rows),
              "run_dirs": len(run_dirs), "families": len({d.split("/")[1] for d in run_dirs}),
              "by_kind": {k: {"files": kinds[k], "bytes": ksize[k]} for k in sorted(kinds)},
              "key_artifacts_sha256": {k: by[k]["sha256"] for k in KEY if k in by},
              "campaign_tar_sha256": sha(tar_path), "manifest_sha256": sha(man), "freeze_wall_s": round(time.time() - t0)}
    (out / "BUNDLE.json").write_text(json.dumps(bundle, indent=1) + "\n", encoding="utf-8", newline="\n")
    rc = verify(out)
    for p in (tar_path, man, out / "BUNDLE.json"):
        os.chmod(p, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
    print(json.dumps({k: bundle[k] for k in ("files", "bytes", "run_dirs", "families", "campaign_tar_sha256", "manifest_sha256")}))
    return rc


def verify(out: Path) -> int:
    b = json.loads((out / "BUNDLE.json").read_text(encoding="utf-8"))
    if sha(out / "campaign.tar") != b["campaign_tar_sha256"] or sha(out / "MANIFEST.jsonl.gz") != b["manifest_sha256"]:
        print("VERIFY FAIL: container hash"); return 5
    with gzip.open(out / "MANIFEST.jsonl.gz", "rt", encoding="utf-8") as g:
        man = {r["path"]: r for r in map(json.loads, g)}
    seen = 0
    with tarfile.open(out / "campaign.tar", "r") as tf:
        for m in tf:
            data = tf.extractfile(m).read(); r = man.get(m.name)
            if r is None or r["size"] != len(data) or r["sha256"] != hashlib.sha256(data).hexdigest():
                print("VERIFY FAIL: %s" % m.name); return 5
            seen += 1
    if seen != len(man) or seen != b["files"]:
        print("VERIFY FAIL: member count %d vs manifest %d vs bundle %d" % (seen, len(man), b["files"])); return 5
    print(json.dumps({"verified": True, "members": seen})); return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--src", default=DEFAULT_HIST); ap.add_argument("--out"); ap.add_argument("--verify")
    a = ap.parse_args(argv)
    if a.verify: return verify(Path(a.verify))
    if a.out: return freeze(Path(a.src), Path(a.out))
    ap.print_help(); return 1


if __name__ == "__main__":
    sys.exit(main())
