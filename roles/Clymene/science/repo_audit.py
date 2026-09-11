"""Clymene vault audit, part A+B: repository reproducibility and completeness.

Preregistered in roles/Clymene/PREREGISTRATION_2026-09-11_vault_audit.md.
Nothing is written under the vault; every fetch lands in the scratch area.
Results are written by this program with a flush per record (never by shell
redirection of a background job).
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import time

SCRATCH = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(SCRATCH, "probe_work")
OUT = os.path.join(SCRATCH, "repo_audit.jsonl")
VAULT_REPOS = "D:/Prometheus/vault/repos"
REGISTRY = os.path.join(SCRATCH, "registry.json")

FAKE_SHA = "0123456789abcdef0123456789abcdef01234567"
DEAD_URL = "https://github.com/prometheus-clymene-audit/this-repo-does-not-exist"


def run(args, timeout=600, cwd=None):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except OSError as exc:
        return -2, "", "OSERROR:" + str(exc)


def blob_sha(data: bytes) -> str:
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def local_index(root: str):
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            try:
                with open(full, "rb") as fh:
                    data = fh.read()
            except OSError as exc:
                out[rel] = ("UNREADABLE:" + type(exc).__name__, "", -1)
                continue
            raw = blob_sha(data)
            lf = blob_sha(data.replace(b"\r\n", b"\n")) if b"\r\n" in data else raw
            out[rel] = (raw, lf, len(data))
    return out


def parse_ls_tree(text: str):
    out = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        meta, path = line.split("\t", 1)
        mode, typ, sha = meta.split()
        out[path.strip()] = (mode, typ, sha)
    return out


def compare(root: str, up: dict):
    loc = local_index(root)
    submodules = {p for p, v in up.items() if v[1] == "commit"}
    symlinks = {p for p, v in up.items() if v[0] == "120000"}
    comparable = {p: v for p, v in up.items() if p not in submodules}
    m_raw = m_lf = mism = 0
    missing, mismatched = [], []
    for p, (mode, typ, sha) in comparable.items():
        if p not in loc:
            missing.append(p)
            continue
        raw, lf, _ = loc[p]
        if raw == sha:
            m_raw += 1
        elif lf == sha:
            m_lf += 1
        else:
            mism += 1
            mismatched.append(p)
    extra = sorted(set(loc) - set(up))
    n = len(comparable)
    return {
        "upstream_entries": len(up),
        "submodule_entries": len(submodules),
        "symlink_entries": len(symlinks),
        "comparable_entries": n,
        "local_files": len(loc),
        "matched_exact": m_raw,
        "matched_after_crlf": m_lf,
        "content_mismatch": mism,
        "missing_from_disk": len(missing),
        "extra_on_disk": len(extra),
        "match_fraction": round((m_raw + m_lf) / n, 6) if n else None,
        "sample_missing": sorted(missing)[:4],
        "sample_mismatch": sorted(mismatched)[:4],
        "sample_extra": extra[:4],
    }


def fetch_tree(url: str, sha: str, tag: str):
    """Blob-less partial fetch of one commit. Returns (ok, ls_tree_text, note)."""
    d = os.path.join(WORK, tag)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d, exist_ok=True)
    rc, _, err = run(["git", "init", "-q", d], timeout=120)
    if rc != 0:
        return False, "", "init failed: " + err.strip()[:200]
    rc, _, err = run(["git", "-C", d, "remote", "add", "origin", url], timeout=120)
    if rc != 0:
        return False, "", "remote add failed: " + err.strip()[:200]
    rc, _, err = run(["git", "-C", d, "fetch", "--depth", "1", "--filter=blob:none",
                      "origin", sha], timeout=900)
    if rc != 0:
        return False, "", err.strip().replace("\n", " ")[:300]
    rc, out, err = run(["git", "-C", d, "ls-tree", "-r", "FETCH_HEAD"], timeout=600)
    if rc != 0:
        return False, "", "ls-tree failed: " + err.strip()[:200]
    return True, out, ""


def emit(fh, rec):
    fh.write(json.dumps(rec) + "\n")
    fh.flush()
    os.fsync(fh.fileno())


def main():
    os.makedirs(WORK, exist_ok=True)
    reg = json.load(open(REGISTRY, encoding="utf-8"))
    repos = reg["repos"]
    on_disk = sorted(d for d in os.listdir(VAULT_REPOS)
                     if os.path.isdir(os.path.join(VAULT_REPOS, d)))

    with open(OUT, "w", encoding="utf-8") as fh:
        emit(fh, {"kind": "header",
                  "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                  "registry_rows": len(repos), "dirs_on_disk": len(on_disk),
                  "vault_repos": VAULT_REPOS})

        ok, text, note = fetch_tree("https://github.com/tensorly/tensorly",
                                    "acc439e9f9662c2b10ccdb53e5e88a0a40090525", "ctl_pos")
        emit(fh, {"kind": "control", "control": "POSITIVE", "expect": "fetch ok",
                  "fetch_ok": ok, "entries": len(parse_ls_tree(text)) if ok else 0,
                  "note": note, "PASS": bool(ok and len(parse_ls_tree(text)) > 0)})

        ok, text, note = fetch_tree("https://github.com/tensorly/tensorly", FAKE_SHA, "ctl_neg_sha")
        emit(fh, {"kind": "control", "control": "NEGATIVE_FABRICATED_SHA",
                  "expect": "fetch fails", "fetch_ok": ok, "note": note, "PASS": (not ok)})

        ok, text, note = fetch_tree(DEAD_URL, FAKE_SHA, "ctl_neg_url")
        emit(fh, {"kind": "control", "control": "NEGATIVE_DEAD_URL",
                  "expect": "fetch fails", "fetch_ok": ok, "note": note, "PASS": (not ok)})

        cheat_row = next((r for r in repos if r["name"] == "baukit"), None)
        cheat = {"kind": "control", "control": "CHEAT_KNOWN_GOOD_TREE",
                 "expect": "match_fraction == 1.0, 0 missing, 0 extra"}
        if cheat_row and cheat_row.get("commit_hash"):
            d = os.path.join(WORK, "cheat_checkout")
            shutil.rmtree(d, ignore_errors=True)
            os.makedirs(d, exist_ok=True)
            rc1, _, e1 = run(["git", "init", "-q", d], timeout=120)
            rc2, _, e2 = run(["git", "-C", d, "remote", "add", "origin", cheat_row["url"]], timeout=120)
            rc3, _, e3 = run(["git", "-C", d, "fetch", "--depth", "1", "origin",
                              cheat_row["commit_hash"]], timeout=900)
            rc4, _, e4 = run(["git", "-C", d, "checkout", "-q", "FETCH_HEAD"], timeout=900)
            okc, text, note = fetch_tree(cheat_row["url"], cheat_row["commit_hash"], "cheat_tree")
            if rc3 == 0 and rc4 == 0 and okc:
                res = compare(d, parse_ls_tree(text))
                cheat.update(res)
                cheat["PASS"] = (res["match_fraction"] == 1.0 and res["missing_from_disk"] == 0
                                 and res["extra_on_disk"] == 0 and res["content_mismatch"] == 0)
                cheat["repo"] = cheat_row["name"]
            else:
                cheat["PASS"] = None
                cheat["note"] = "setup failed rc={} {} / {} / {}".format(
                    [rc1, rc2, rc3, rc4], e3.strip()[:120], e4.strip()[:120], note)
        else:
            cheat["PASS"] = None
            cheat["note"] = "no cheat row available"
        emit(fh, cheat)

        for i, r in enumerate(repos, 1):
            name = r["name"]
            rec = {"kind": "repo", "i": i, "name": name, "url": r.get("url"),
                   "registry_commit": r.get("commit_hash"),
                   "registry_status": r.get("status"),
                   "registry_size_bytes": r.get("size_bytes"),
                   "registry_local_path": r.get("local_path"),
                   "registry_last_updated": r.get("last_updated")}
            sha = (r.get("commit_hash") or "").strip()
            url = (r.get("url") or "").strip()
            rec["R1_identity_complete"] = bool(url) and len(sha) == 40 and all(
                ch in "0123456789abcdef" for ch in sha.lower())
            disk = os.path.join(VAULT_REPOS, name)
            rec["on_disk"] = os.path.isdir(disk)

            if not rec["R1_identity_complete"]:
                rec["R2_upstream_fetchable"] = None
                rec["R3_tree_resolves"] = None
                rec["reproducible"] = False
                rec["fail_stage"] = "R1"
                emit(fh, rec)
                continue

            t0 = time.time()
            ok, text, note = fetch_tree(url, sha, "r%02d" % i)
            rec["fetch_seconds"] = round(time.time() - t0, 1)
            rec["R2_upstream_fetchable"] = ok
            rec["fetch_note"] = note
            if not ok:
                rec["R3_tree_resolves"] = None
                rec["reproducible"] = False
                rec["fail_stage"] = "R2"
                low = note.lower()
                rec["indeterminate"] = any(k in low for k in
                                           ("timeout", "could not resolve host", "connection",
                                            "tls", "ssl", "proxy", "early eof", "rpc failed"))
                emit(fh, rec)
                continue

            up = parse_ls_tree(text)
            rec["R3_tree_resolves"] = len(up) > 0
            rec["upstream_tree_entries"] = len(up)
            rec["reproducible"] = bool(rec["R1_identity_complete"] and ok and len(up) > 0)
            rec["completeness"] = compare(disk, up) if rec["on_disk"] else None
            emit(fh, rec)
            shutil.rmtree(os.path.join(WORK, "r%02d" % i), ignore_errors=True)

        names = {r["name"] for r in repos}
        emit(fh, {"kind": "reconciliation",
                  "dirs_without_registry_row": sorted(set(on_disk) - names),
                  "registry_rows_without_dir": sorted(names - set(on_disk))})
        emit(fh, {"kind": "footer",
                  "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})


if __name__ == "__main__":
    main()
    print("wrote", OUT)
