"""Clymene vault audit, part C: model provenance, integrity and reproducibility.

Preregistered in roles/Clymene/PREREGISTRATION_2026-09-11_vault_audit.md s1.

The Hugging Face snapshot sidecar .cache/huggingface/download/<file>.metadata
carries three lines: the REPOSITORY COMMIT HASH the file was fetched at, the
file's ETAG, and a timestamp. The registry has no revision column, so this
sidecar -- written by huggingface_hub, not by Clymene -- is the only recorded
provenance these artifacts have.

Etag semantics: a 40-hex etag is the git blob sha1 of a small (non-LFS) file;
a 64-hex etag is the sha256 of an LFS file's content. Both are checked against
the bytes on disk. This is local and needs no network, and is the strongest
available evidence that a payload is intact rather than truncated.

Everything here is READ-ONLY against the vault.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request

SCRATCH = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SCRATCH, "model_audit.jsonl")
VAULT_MODELS = "D:/Prometheus/vault/models"
REGISTRY = os.path.join(SCRATCH, "registry.json")
HF_CACHE = os.path.expanduser("~/.cache/huggingface/hub")

WEIGHT_EXT = (".safetensors", ".bin", ".gguf", ".pt", ".pth", ".msgpack", ".h5")
UA = {"User-Agent": "prometheus-clymene-audit/1.0 (read-only provenance check)"}


def blob_sha1(path):
    h = hashlib.sha1()
    size = os.path.getsize(path)
    h.update(b"blob %d\0" % size)
    with open(path, "rb") as fh:
        while True:
            b = fh.read(1 << 22)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(1 << 22)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def head(url, timeout=45):
    req = urllib.request.Request(url, method="HEAD", headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {})
    except Exception as e:
        return -1, {"error": type(e).__name__ + ": " + str(e)[:160]}


def emit(fh, rec):
    fh.write(json.dumps(rec) + "\n")
    fh.flush()
    os.fsync(fh.fileno())


def read_sidecars(d):
    """rel file path -> (commit, etag, ts) from .cache/huggingface/download."""
    base = os.path.join(d, ".cache", "huggingface", "download")
    out = {}
    if not os.path.isdir(base):
        return out
    for dirpath, _dirnames, filenames in os.walk(base):
        for fn in filenames:
            if not fn.endswith(".metadata"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, base).replace(os.sep, "/")
            target = rel[: -len(".metadata")]
            try:
                lines = open(full, encoding="utf-8", errors="replace").read().splitlines()
            except OSError:
                continue
            commit = lines[0].strip() if len(lines) > 0 else ""
            etag = lines[1].strip().strip('"') if len(lines) > 1 else ""
            ts = lines[2].strip() if len(lines) > 2 else ""
            out[target] = (commit, etag, ts)
    return out


def main():
    reg = json.load(open(REGISTRY, encoding="utf-8"))
    by_dir = {m["hf_id"].replace("/", "--"): m for m in reg["models"]}
    dirs = sorted(x for x in os.listdir(VAULT_MODELS)
                  if os.path.isdir(os.path.join(VAULT_MODELS, x)))

    with open(OUT, "w", encoding="utf-8") as fh:
        emit(fh, {"kind": "header",
                  "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                  "vault_models": VAULT_MODELS, "dirs_on_disk": len(dirs),
                  "registry_model_rows": len(reg["models"]),
                  "hf_cache_path": HF_CACHE,
                  "hf_cache_entries": sorted(os.listdir(HF_CACHE)) if os.path.isdir(HF_CACHE) else None})

        # control: the integrity channel must detect a deliberate corruption.
        # A byte is appended to a COPY in scratch, never to the vault file.
        ctl = {"kind": "control", "control": "INTEGRITY_CHANNEL_CHEAT",
               "expect": "clean copy verifies, corrupted copy fails"}
        try:
            src = None
            for d in dirs:
                p = os.path.join(VAULT_MODELS, d, "config.json")
                if os.path.exists(p):
                    src = p
                    break
            data = open(src, "rb").read()
            good = os.path.join(SCRATCH, "ctl_good.bin")
            bad = os.path.join(SCRATCH, "ctl_bad.bin")
            open(good, "wb").write(data)
            open(bad, "wb").write(data + b"x")
            g, b = blob_sha1(good), blob_sha1(bad)
            ctl.update({"source": src, "clean_sha": g, "corrupt_sha": b,
                        "PASS": g != b and len(g) == 40})
        except Exception as exc:
            ctl.update({"PASS": None, "error": type(exc).__name__ + ": " + str(exc)[:160]})
        emit(fh, ctl)

        for dname in dirs:
            d = os.path.join(VAULT_MODELS, dname)
            row = by_dir.get(dname)
            rec = {"kind": "model", "dir": dname,
                   "hf_id": (row or {}).get("hf_id") or dname.replace("--", "/", 1),
                   "registry_row_present": bool(row),
                   "registry_status": (row or {}).get("status"),
                   "registry_size_bytes": (row or {}).get("size_bytes"),
                   "registry_local_path": (row or {}).get("local_path"),
                   "registry_records_revision": False}

            files = []
            total = 0
            for dirpath, dirnames, filenames in os.walk(d):
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
            weights = [(r, s) for r, s in files if r.lower().endswith(WEIGHT_EXT)]
            rec["weight_files"] = len(weights)
            rec["weight_bytes"] = sum(s for _r, s in weights)
            rec["PAYLOAD_PRESENT"] = rec["weight_files"] > 0 and rec["weight_bytes"] > 0
            rec["largest_files"] = sorted(files, key=lambda t: -t[1])[:4]

            side = read_sidecars(d)
            rec["sidecar_count"] = len(side)
            commits = sorted({c for c, _e, _t in side.values() if c})
            rec["sidecar_commits"] = commits
            rec["PROVENANCE_COMPLETE"] = bool(side) and len(commits) == 1 and all(
                any(r == t for t, _ in [(w[0], 0) for w in weights]) or True for r in [])
            rec["recorded_revision"] = commits[0] if len(commits) == 1 else None
            # every payload file must have a sidecar for provenance to be complete
            missing_side = [r for r, _s in weights if r not in side]
            rec["payload_files_without_sidecar"] = missing_side
            rec["PROVENANCE_COMPLETE"] = bool(commits) and len(commits) == 1 and not missing_side

            # integrity: verify every sidecar-covered file present on disk
            checked = ok = failed = skipped = 0
            failures = []
            t0 = time.time()
            for rel, (commit, etag, _ts) in sorted(side.items()):
                p = os.path.join(d, rel.replace("/", os.sep))
                if not os.path.exists(p):
                    skipped += 1
                    continue
                checked += 1
                try:
                    if len(etag) == 40 and all(c in "0123456789abcdef" for c in etag.lower()):
                        got = blob_sha1(p)
                    elif len(etag) == 64 and all(c in "0123456789abcdef" for c in etag.lower()):
                        got = sha256(p)
                    else:
                        skipped += 1
                        checked -= 1
                        continue
                except OSError as exc:
                    failed += 1
                    failures.append({"file": rel, "error": type(exc).__name__})
                    continue
                if got == etag.lower():
                    ok += 1
                else:
                    failed += 1
                    failures.append({"file": rel, "expected": etag, "got": got})
            rec["integrity_checked"] = checked
            rec["integrity_ok"] = ok
            rec["integrity_failed"] = failed
            rec["integrity_skipped_no_file_or_etag"] = skipped
            rec["integrity_failures"] = failures[:5]
            rec["integrity_seconds"] = round(time.time() - t0, 1)
            rec["INTEGRITY_VERIFIED"] = checked > 0 and failed == 0

            # reproducibility: does the recorded revision still resolve today?
            rev = rec["recorded_revision"]
            if rev:
                probe_file = None
                for cand in ("config.json", "README.md", "tokenizer_config.json"):
                    if cand in side:
                        probe_file = cand
                        break
                if probe_file is None and side:
                    probe_file = sorted(side)[0]
                url = "https://huggingface.co/{}/resolve/{}/{}".format(
                    rec["hf_id"], rev, probe_file)
                status, hdrs = head(url)
                rec["repro_probe_url"] = url
                rec["repro_http_status"] = status
                rec["repro_server_etag"] = (hdrs.get("ETag") or hdrs.get("X-Linked-ETag") or "").strip('"')
                rec["repro_error"] = hdrs.get("error")
                if status in (200, 302):
                    rec["REPRODUCIBLE"] = True
                    rec["repro_note"] = "recorded revision resolves today"
                elif status in (401, 403):
                    rec["REPRODUCIBLE"] = False
                    rec["repro_note"] = "GATED: needs a credential"
                elif status == 404:
                    rec["REPRODUCIBLE"] = False
                    rec["repro_note"] = "revision or file gone"
                else:
                    rec["REPRODUCIBLE"] = None
                    rec["repro_note"] = "INDETERMINATE (transport)"
            else:
                rec["REPRODUCIBLE"] = False
                rec["repro_note"] = "no recorded revision on the artifact and none in the registry"

            # duplication against this host's HF cache
            cache_name = "models--" + dname
            rec["ALSO_IN_HF_CACHE"] = os.path.isdir(os.path.join(HF_CACHE, cache_name)) \
                if os.path.isdir(HF_CACHE) else None
            emit(fh, rec)

        # registry rows with no directory on M2
        emit(fh, {"kind": "reconciliation",
                  "registry_rows_without_dir_on_m2":
                      sorted(set(by_dir) - set(dirs)),
                  "dirs_without_registry_row": sorted(set(dirs) - set(by_dir))})
        emit(fh, {"kind": "footer",
                  "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})


if __name__ == "__main__":
    main()
    print("wrote", OUT)
