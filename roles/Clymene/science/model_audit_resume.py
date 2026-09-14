"""Resume the model audit for ONE directory and APPEND its row.

The first run was killed by the harness at 9 of 11 for host memory pressure
while hashing multi-GB weight files. This resumes per-directory so each
invocation is bounded, and reads in 1 MiB chunks instead of 4 MiB. It APPENDS
to model_audit.jsonl; rows already written are not recomputed and not altered.

Usage: python model_audit_resume.py <dir-name> [<dir-name> ...]
       python model_audit_resume.py --footer
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model_audit as M  # noqa: E402

CHUNK = 1 << 20


def _blob_sha1(path):
    import hashlib
    h = hashlib.sha1()
    h.update(b"blob %d\0" % os.path.getsize(path))
    with open(path, "rb") as fh:
        while True:
            b = fh.read(CHUNK)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(CHUNK)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


M.blob_sha1 = _blob_sha1
M.sha256 = _sha256


def existing(path):
    if not os.path.exists(path):
        return set()
    out = set()
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        if r.get("kind") == "model":
            out.add(r["dir"])
    return out


def audit_one(dname, reg_by_dir):
    """Identical logic to model_audit.main()'s per-directory body."""
    import time
    d = os.path.join(M.VAULT_MODELS, dname)
    row = reg_by_dir.get(dname)
    rec = {"kind": "model", "dir": dname,
           "hf_id": (row or {}).get("hf_id") or dname.replace("--", "/", 1),
           "registry_row_present": bool(row),
           "registry_status": (row or {}).get("status"),
           "registry_size_bytes": (row or {}).get("size_bytes"),
           "registry_local_path": (row or {}).get("local_path"),
           "registry_records_revision": False,
           "resumed": True}

    files, total = [], 0
    for dirpath, _dn, filenames in os.walk(d):
        if ".cache" in dirpath.replace("\\", "/").split("/"):
            continue
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, d).replace(os.sep, "/")
            try:
                sz = os.path.getsize(p)
            except OSError:
                sz = -1
            files.append((rel, sz))
            total += max(sz, 0)
    rec["file_count"] = len(files)
    rec["bytes_on_disk"] = total
    weights = [(r, s) for r, s in files if r.lower().endswith(M.WEIGHT_EXT)]
    rec["weight_files"] = len(weights)
    rec["weight_bytes"] = sum(s for _r, s in weights)
    rec["PAYLOAD_PRESENT"] = rec["weight_files"] > 0 and rec["weight_bytes"] > 0
    rec["largest_files"] = sorted(files, key=lambda t: -t[1])[:4]

    side = M.read_sidecars(d)
    rec["sidecar_count"] = len(side)
    commits = sorted({c for c, _e, _t in side.values() if c})
    rec["sidecar_commits"] = commits
    rec["recorded_revision"] = commits[0] if len(commits) == 1 else None
    missing_side = [r for r, _s in weights if r not in side]
    rec["payload_files_without_sidecar"] = missing_side
    rec["PROVENANCE_COMPLETE"] = bool(commits) and len(commits) == 1 and not missing_side

    checked = ok = failed = skipped = 0
    failures = []
    t0 = time.time()
    for rel, (commit, etag, _ts) in sorted(side.items()):
        p = os.path.join(d, rel.replace("/", os.sep))
        if not os.path.exists(p):
            skipped += 1
            continue
        hexy = etag.lower()
        if len(etag) == 40 and all(c in "0123456789abcdef" for c in hexy):
            got = _blob_sha1(p)
        elif len(etag) == 64 and all(c in "0123456789abcdef" for c in hexy):
            got = _sha256(p)
        else:
            skipped += 1
            continue
        checked += 1
        if got == hexy:
            ok += 1
        else:
            failed += 1
            failures.append({"file": rel, "expected": etag, "got": got})
        print("   %s %s" % ("ok " if got == hexy else "FAIL", rel), flush=True)
    rec["integrity_checked"] = checked
    rec["integrity_ok"] = ok
    rec["integrity_failed"] = failed
    rec["integrity_skipped_no_file_or_etag"] = skipped
    rec["integrity_failures"] = failures[:5]
    rec["integrity_seconds"] = round(time.time() - t0, 1)
    rec["INTEGRITY_VERIFIED"] = checked > 0 and failed == 0

    rev = rec["recorded_revision"]
    if rev:
        probe = None
        for cand in ("config.json", "README.md", "tokenizer_config.json"):
            if cand in side:
                probe = cand
                break
        if probe is None and side:
            probe = sorted(side)[0]
        url = "https://huggingface.co/{}/resolve/{}/{}".format(rec["hf_id"], rev, probe)
        status, hdrs = M.head(url)
        rec["repro_probe_url"] = url
        rec["repro_http_status"] = status
        rec["repro_server_etag"] = (hdrs.get("ETag") or hdrs.get("X-Linked-ETag") or "").strip('"')
        rec["repro_error"] = hdrs.get("error")
        if status in (200, 302):
            rec["REPRODUCIBLE"], rec["repro_note"] = True, "recorded revision resolves today"
        elif status in (401, 403):
            rec["REPRODUCIBLE"], rec["repro_note"] = False, "GATED: needs a credential"
        elif status == 404:
            rec["REPRODUCIBLE"], rec["repro_note"] = False, "revision or file gone"
        else:
            rec["REPRODUCIBLE"], rec["repro_note"] = None, "INDETERMINATE (transport)"
    else:
        rec["REPRODUCIBLE"] = False
        rec["repro_note"] = "no recorded revision on the artifact and none in the registry"

    rec["ALSO_IN_HF_CACHE"] = (os.path.isdir(os.path.join(M.HF_CACHE, "models--" + dname))
                               if os.path.isdir(M.HF_CACHE) else None)
    return rec


def main():
    reg = json.load(open(M.REGISTRY, encoding="utf-8"))
    by_dir = {m["hf_id"].replace("/", "--"): m for m in reg["models"]}
    done = existing(M.OUT)

    if sys.argv[1:] == ["--footer"]:
        import time
        dirs = sorted(x for x in os.listdir(M.VAULT_MODELS)
                      if os.path.isdir(os.path.join(M.VAULT_MODELS, x)))
        with open(M.OUT, "a", encoding="utf-8") as fh:
            M.emit(fh, {"kind": "reconciliation",
                        "registry_rows_without_dir_on_m2": sorted(set(by_dir) - set(dirs)),
                        "dirs_without_registry_row": sorted(set(dirs) - set(by_dir))})
            M.emit(fh, {"kind": "footer", "resumed_after_oom_kill": True,
                        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        print("footer written")
        return

    for dname in sys.argv[1:]:
        if dname in done:
            print("already done, skipping:", dname)
            continue
        print("auditing", dname, flush=True)
        rec = audit_one(dname, by_dir)
        with open(M.OUT, "a", encoding="utf-8") as fh:
            M.emit(fh, rec)
        print("  -> integrity %s/%s failed=%s repro=%s" % (
            rec["integrity_ok"], rec["integrity_checked"], rec["integrity_failed"],
            rec["REPRODUCIBLE"]), flush=True)


if __name__ == "__main__":
    main()
