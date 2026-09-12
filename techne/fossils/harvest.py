"""Fossil harvest CLI: acquire a body into the vault, run its recipe, write the receipt.

    python -m techne.fossils.harvest acquire <specimen_id>        fetch per record.source_origin, hash, extract
    python -m techne.fossils.harvest run <specimen_id>            execute recipe.json (build, run, tests) -> receipt
    python -m techne.fossils.harvest verify <specimen_id>         re-hash the body against UPSTREAM_HASHES.txt
    python -m techne.fossils.harvest verify --all [--out F]       every body; the census as JSON rows
    python -m techne.fossils.harvest restore <specimen_id>        put a drifted body back to its pin (rows in a receipt)
    python -m techne.fossils.harvest mirror --dest D [--dry-run]  copy verified bodies to D/<tree_sha256>/ (TECHNE-65: D is the operator's call)
    python -m techne.fossils.harvest status                       one line per specimen
    python -m techne.fossils.harvest summary                      the directive's success measures, computed

A RECIPE (techne/fossils/specimens/<id>/recipe.json) is the executable statement of "how to
run it": {"runner": "wsl"|"native"|"docker", "image": ..., "workdir": <relative to the body>,
"probe": [cmds that print toolchain versions], "build": [cmds], "runs": [{"name", "cmd",
"expect": {"exit": 0, "stdout_contains": [...], "stdout_regex": ...}}], "tests": [same shape],
"classification_if_ok": "RUNNABLE_NATIVE", "test_classification_if_ok": ...}. Commands run
in the body's workdir; a receipt records every command, exit status, timing, stdout/stderr
(head and tail; full text under <vault>/<id>/run/), the toolchain probe, and the sha256 of
every file the build produced. Nothing here alters upstream source: a recipe that needs a
patch names it under patches/ and the receipt lists the patch's own hash.

ISOLATION (2026-09-12). `run` never executes inside the preserved body. It stages a disposable
copy at <vault>/<id>/work/ (upstream/ + harness/ + an empty build/), runs the recipe there,
and afterwards re-hashes the PRESERVED upstream/ and writes tree_sha256_after and
body_preserved into the receipt -- the property, not a promise. Before this rule 23 of 57
bodies had been dirtied by in-place builds (techne/fossils/VAULT_INTEGRITY_2026-09-12.json).
A recipe may set "in_place": true to opt out (archaeology of the old behaviour, and the
positive control for the detector); the receipt then says isolation "in_place".
"""
from __future__ import annotations

import argparse
import json
import pathlib
import platform
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import time

from . import record, vault

MAX_CAPTURE = 4000


# --------------------------------------------------------------------------- runners
def _shell(runner: str, cmd: str, body: pathlib.Path, rel: str, image: str | None, timeout: int) -> dict:
    """Run `cmd` in <body>/<rel>. $HARNESS is the body's harness/ copy (Techne's smoke inputs),
    $BODY the body root, whatever the runner; the command text in the receipt is what ran."""
    t0 = time.time()
    if runner == "wsl":
        b = vault.to_wsl(body)
        pre = "export BODY=%s HARNESS=%s; cd %s && " % (shlex.quote(b), shlex.quote(b + "/harness"), shlex.quote(b + "/" + rel))
        full = ["wsl.exe", "-e", "bash", "-lc", pre + cmd]
    elif runner == "docker":
        pre = "export BODY=/w HARNESS=/w/harness; cd %s && " % shlex.quote("/w/" + rel)
        full = ["wsl.exe", "-e", "bash", "-lc",
                "docker run --rm -v %s:/w -w /w %s bash -lc %s" % (
                    shlex.quote(vault.to_wsl(body)), shlex.quote(image or "prometheus-fossil-c:bookworm"), shlex.quote(pre + cmd))]
    elif runner == "native":
        b = str(body).replace("\\", "/")
        pre = "export BODY=%s HARNESS=%s; cd %s && " % (shlex.quote(b), shlex.quote(b + "/harness"), shlex.quote(b + "/" + rel))
        full = ["bash", "-lc", pre + cmd]
    else:
        raise ValueError("unknown runner " + runner)
    try:
        p = subprocess.run(full, capture_output=True, text=True, timeout=timeout, errors="replace")
        rc, out, err = p.returncode, p.stdout or "", p.stderr or ""
    except subprocess.TimeoutExpired as e:
        so = e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        rc, out, err = -1, so, "TIMEOUT after %ss" % timeout
    return {"cmd": cmd, "runner": runner, "exit": rc, "seconds": round(time.time() - t0, 2),
            "stdout": out, "stderr": err}


def _clip(s: str) -> dict:
    if len(s) <= MAX_CAPTURE:
        return {"text": s}
    return {"head": s[:MAX_CAPTURE // 2], "tail": s[-MAX_CAPTURE // 2:], "bytes": len(s), "truncated": True}


def _expect_ok(res: dict, expect: dict | None) -> tuple[bool, list[str]]:
    expect = expect or {"exit": 0}
    why = []
    if "exit" in expect and res["exit"] != expect["exit"]:
        why.append("exit %s != expected %s" % (res["exit"], expect["exit"]))
    for s in expect.get("stdout_contains", []):
        if s not in res["stdout"]:
            why.append("stdout lacks %r" % s)
    for s in expect.get("stderr_contains", []):
        if s not in res["stderr"]:
            why.append("stderr lacks %r" % s)
    if expect.get("stdout_regex") and not re.search(expect["stdout_regex"], res["stdout"], re.S):
        why.append("stdout does not match /%s/" % expect["stdout_regex"])
    if expect.get("stdout_not_contains"):
        for s in expect["stdout_not_contains"]:
            if s in res["stdout"]:
                why.append("stdout unexpectedly contains %r" % s)
    return (not why), why


# --------------------------------------------------------------------------- acquire
def acquire(specimen_id: str) -> dict:
    rec = record.load(specimen_id)
    origin = rec["source_origin"]
    body = vault.body_dir(specimen_id)
    up = body / "upstream"
    up.mkdir(parents=True, exist_ok=True)
    out = {"specimen_id": specimen_id, "fetched": [], "body": str(body)}
    for art in origin.get("artifacts", []):
        kind = art["kind"]
        if kind == "url":
            dest = up / art["filename"]
            if dest.exists() and art.get("sha256") and vault.sha256_file(dest) == art["sha256"]:
                f = {"url": art["url"], "path": str(dest), "sha256": art["sha256"], "cached": True}
            else:
                f = vault.fetch_url(art["url"], dest)
                if art.get("sha256") and f["sha256"] != art["sha256"]:
                    raise RuntimeError("sha256 mismatch for %s: got %s expected %s" % (art["url"], f["sha256"], art["sha256"]))
            art["sha256"] = f["sha256"]
            art["bytes"] = dest.stat().st_size
            if art.get("extract", True) and dest.name.lower().endswith((".gz", ".tgz", ".zip", ".bz2", ".xz", ".tar")):
                root = vault.extract(dest, up / "tree")
                art["extracted_to"] = str(root.relative_to(body)).replace("\\", "/")
            out["fetched"].append(f)
        elif kind == "git":
            dest = up / "tree"
            g = vault.git_pin(art["url"], art["commit"], dest)
            art.update({"commit_resolved": g["commit"], "commit_date": g["commit_date"]})
            if art["commit"] == "HEAD":
                art["commit"] = g["commit"]          # the pin is exact from now on
            out["fetched"].append(g)
        else:
            raise ValueError("unknown artifact kind " + kind)
    # hash EVERYTHING under upstream/: the immutable archive(s) as fetched plus the extracted
    # tree plus any loose files, so one tree hash covers the whole body
    rows = vault.hash_tree(up)
    vault.write_hashes(specimen_id, rows)
    rec["hashes"] = {"tree_sha256": vault.tree_hash_of(rows), "n_files": len(rows),
                     "bytes": sum(r[2] for r in rows),
                     "artifacts": [{"filename": a.get("filename") or a.get("url"), "sha256": a.get("sha256"),
                                    "commit": a.get("commit_resolved")} for a in origin.get("artifacts", [])],
                     "body_location": str(body), "hash_list": "techne/fossils/specimens/%s/UPSTREAM_HASHES.txt" % specimen_id}
    rec["acquisition_date"] = time.strftime("%Y-%m-%d", time.gmtime())
    record.save(rec)
    out["tree_sha256"] = rec["hashes"]["tree_sha256"]
    out["n_files"] = len(rows)
    print(json.dumps({k: v for k, v in out.items() if k != "fetched"}, indent=1))
    return out


ARCHIVE_SUFFIXES = (".tar.gz", ".tgz", ".tar.bz2", ".tar.xz", ".tar", ".zip")


def _want_rows(specimen_id: str) -> dict:
    """UPSTREAM_HASHES.txt -> {relpath: (sha256, bytes)}; the tracked half is the authority."""
    want = {}
    hl = vault.specimen_dir(specimen_id) / "UPSTREAM_HASHES.txt"
    for line in hl.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        h, n, rel = line.split("  ", 2)
        want[rel] = (h, int(n))
    return want


def drift(specimen_id: str) -> dict:
    """What differs between the preserved upstream/ and its recorded hash list, as rows."""
    body = vault.body_dir(specimen_id)
    rows = vault.hash_tree(body / "upstream")
    got = {rel: (h, n) for rel, h, n in rows}
    want = _want_rows(specimen_id)
    rec_hash = record.load(specimen_id)["hashes"].get("tree_sha256")
    now = vault.tree_hash_of(rows)
    return {"specimen_id": specimen_id, "tree_sha256_recorded": rec_hash, "tree_sha256_now": now,
            "matches": now == rec_hash, "n_recorded": len(want), "n_now": len(got),
            "added": sorted(set(got) - set(want)), "removed": sorted(set(want) - set(got)),
            "modified": sorted(r for r in want if r in got and got[r][0] != want[r][0]),
            "body_present": (body / "upstream").exists()}


def verify(specimen_id: str) -> bool:
    d = drift(specimen_id)
    print(specimen_id, "tree", d["tree_sha256_now"], "matches" if d["matches"] else
          "DIFFERS FROM RECORD %s (+%d added, -%d removed, %d modified)" % (
              d["tree_sha256_recorded"], len(d["added"]), len(d["removed"]), len(d["modified"])))
    return d["matches"]


def verify_all(out: str | None = None) -> dict:
    """The vault integrity census: every specimen's drift rows, and the counts beside them."""
    ids = sorted(p.parent.name for p in vault.SPECIMENS.glob("*/record.json"))
    rows = []
    for sid in ids:
        if not (vault.body_dir(sid) / "upstream").exists():
            rows.append({"specimen_id": sid, "matches": None, "body_present": False})
            print("%-30s BODY MISSING on this host" % sid)
            continue
        d = drift(sid)
        rows.append(d)
        print("%-30s %s" % (sid, "matches" if d["matches"] else "DIFFERS +%d -%d ~%d" % (len(d["added"]), len(d["removed"]), len(d["modified"]))))
    census = {"schema": "techne.fossil.vault_integrity/1",
              "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "vault_root": str(vault.vault_root()), "specimens": len(ids),
              "matches": sum(1 for r in rows if r.get("matches") is True),
              "differs": sum(1 for r in rows if r.get("matches") is False),
              "body_missing": sum(1 for r in rows if r.get("body_present") is False),
              "rows": rows}
    print("specimens %d  matches %d  differs %d  body_missing %d" % (census["specimens"], census["matches"], census["differs"], census["body_missing"]))
    if out:
        pathlib.Path(out).write_text(json.dumps(census, indent=1) + "\n", encoding="utf-8", newline="\n")
        print("census", out)
    return census


def _rm_readonly(func, path, _exc):
    # git object files are read-only on Windows; rmtree needs them writable first
    try:
        pathlib.Path(path).chmod(stat.S_IWRITE)
        func(path)
    except OSError:
        pass


def _rmtree(p: pathlib.Path):
    if sys.version_info >= (3, 12):
        shutil.rmtree(p, onexc=_rm_readonly)
    else:
        shutil.rmtree(p, onerror=_rm_readonly)


def _prune_empty_dirs(root: pathlib.Path):
    for d in sorted((x for x in root.rglob("*") if x.is_dir() and ".git" not in x.relative_to(root).parts),
                    key=lambda x: -len(x.parts)):
        try:
            d.rmdir()          # only succeeds when empty
        except OSError:
            pass


def restore(specimen_id: str) -> dict:
    """Put a drifted preserved body back to its pin, and prove it with the rows.

    added files (build products) are deleted; modified or missing files are recovered from the
    body's own immutable sources -- `git checkout` at the pin for a git body, else by CONTENT
    from the archive(s) kept beside the tree (re-extracted to a temp dir and indexed by sha256,
    so no path mapping is assumed). Anything neither source holds is reported UNRECOVERABLE and
    the body stays unverified; nothing is ever fabricated. Rows land in a tracked receipt."""
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    before = drift(specimen_id)
    body = vault.body_dir(specimen_id)
    up = body / "upstream"
    rep = {"schema": "techne.fossil.restore_receipt/1", "specimen_id": specimen_id,
           "receipt_id": "restore-%s-%s" % (specimen_id, ts), "written_utc": ts,
           "before": {k: before[k] for k in ("tree_sha256_recorded", "tree_sha256_now", "matches")},
           "deleted": [], "restored_from_git": [], "restored_from_archive": [], "unrecoverable": [],
           "after": None, "verified": None}
    if before["matches"]:
        rep["after"] = rep["before"]
        rep["verified"] = True
        print(specimen_id, "already matches; nothing to restore")
        return rep
    want = _want_rows(specimen_id)
    for rel in before["added"]:
        (up / rel).unlink()
        rep["deleted"].append(rel)
    _prune_empty_dirs(up)
    need = before["modified"] + before["removed"]
    remaining = []
    tree_git = up / "tree" / ".git"
    for rel in need:
        if rel.startswith("tree/") and tree_git.exists():
            r = subprocess.run(["git", "-c", "core.autocrlf=false", "-c", "core.eol=lf", "-C", str(up / "tree"),
                                "checkout", "--", rel[len("tree/"):]], capture_output=True, text=True, timeout=300)
            if r.returncode == 0 and (up / rel).exists() and vault.sha256_file(up / rel) == want[rel][0]:
                rep["restored_from_git"].append(rel)
                continue
        remaining.append(rel)
    if remaining:
        archives = [a for a in up.iterdir() if a.is_file() and a.name.lower().endswith(ARCHIVE_SUFFIXES)]
        with tempfile.TemporaryDirectory(prefix="fossil-restore-") as tmp:
            idx = {}
            for a in archives:
                try:
                    vault.extract(a, pathlib.Path(tmp) / re.sub(r"[^A-Za-z0-9_.-]+", "_", a.name))
                except (OSError, ValueError) as e:
                    print("  archive", a.name, "did not extract:", e)
            for f in pathlib.Path(tmp).rglob("*"):
                if f.is_file():
                    idx.setdefault(vault.sha256_file(f), f)
            for rel in remaining:
                src = idx.get(want[rel][0])
                if src is None:
                    rep["unrecoverable"].append(rel)
                    continue
                (up / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, up / rel)
                rep["restored_from_archive"].append(rel)
    after = drift(specimen_id)
    rep["after"] = {k: after[k] for k in ("tree_sha256_recorded", "tree_sha256_now", "matches")}
    rep["after"].update({"added": after["added"], "removed": after["removed"], "modified": after["modified"]})
    rep["verified"] = after["matches"]
    rp = vault.specimen_dir(specimen_id) / "receipts" / (rep["receipt_id"] + ".json")
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(rep, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("%s restore: deleted %d, git %d, archive %d, UNRECOVERABLE %d -> %s  (%s)" % (
        specimen_id, len(rep["deleted"]), len(rep["restored_from_git"]), len(rep["restored_from_archive"]),
        len(rep["unrecoverable"]), "VERIFIED" if rep["verified"] else "STILL DIFFERS", rp))
    return rep


# --------------------------------------------------------------------------- runners
def _shell(runner: str, cmd: str, body: pathlib.Path, rel: str, image: str | None, timeout: int) -> dict:
    """Run `cmd` in <body>/<rel>. $HARNESS is the body's harness/ copy (Techne's smoke inputs),
    $BODY the body root, whatever the runner; the command text in the receipt is what ran."""
    t0 = time.time()
    if runner == "wsl":
        b = vault.to_wsl(body)
        pre = "export BODY=%s HARNESS=%s; cd %s && " % (shlex.quote(b), shlex.quote(b + "/harness"), shlex.quote(b + "/" + rel))
        full = ["wsl.exe", "-e", "bash", "-lc", pre + cmd]
    elif runner == "docker":
        pre = "export BODY=/w HARNESS=/w/harness; cd %s && " % shlex.quote("/w/" + rel)
        full = ["wsl.exe", "-e", "bash", "-lc",
                "docker run --rm -v %s:/w -w /w %s bash -lc %s" % (
                    shlex.quote(vault.to_wsl(body)), shlex.quote(image or "prometheus-fossil-c:bookworm"), shlex.quote(pre + cmd))]
    elif runner == "native":
        b = str(body).replace("\\", "/")
        pre = "export BODY=%s HARNESS=%s; cd %s && " % (shlex.quote(b), shlex.quote(b + "/harness"), shlex.quote(b + "/" + rel))
        full = ["bash", "-lc", pre + cmd]
    else:
        raise ValueError("unknown runner " + runner)
    try:
        p = subprocess.run(full, capture_output=True, text=True, timeout=timeout, errors="replace")
        rc, out, err = p.returncode, p.stdout or "", p.stderr or ""
    except subprocess.TimeoutExpired as e:
        so = e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        rc, out, err = -1, so, "TIMEOUT after %ss" % timeout
    return {"cmd": cmd, "runner": runner, "exit": rc, "seconds": round(time.time() - t0, 2),
            "stdout": out, "stderr": err}


def _clip(s: str) -> dict:
    if len(s) <= MAX_CAPTURE:
        return {"text": s}
    return {"head": s[:MAX_CAPTURE // 2], "tail": s[-MAX_CAPTURE // 2:], "bytes": len(s), "truncated": True}


def _expect_ok(res: dict, expect: dict | None) -> tuple[bool, list[str]]:
    expect = expect or {"exit": 0}
    why = []
    if "exit" in expect and res["exit"] != expect["exit"]:
        why.append("exit %s != expected %s" % (res["exit"], expect["exit"]))
    for s in expect.get("stdout_contains", []):
        if s not in res["stdout"]:
            why.append("stdout lacks %r" % s)
    for s in expect.get("stderr_contains", []):
        if s not in res["stderr"]:
            why.append("stderr lacks %r" % s)
    if expect.get("stdout_regex") and not re.search(expect["stdout_regex"], res["stdout"], re.S):
        why.append("stdout does not match /%s/" % expect["stdout_regex"])
    if expect.get("stdout_not_contains"):
        for s in expect["stdout_not_contains"]:
            if s in res["stdout"]:
                why.append("stdout unexpectedly contains %r" % s)
    return (not why), why


# --------------------------------------------------------------------------- acquire
def acquire(specimen_id: str) -> dict:
    rec = record.load(specimen_id)
    origin = rec["source_origin"]
    body = vault.body_dir(specimen_id)
    up = body / "upstream"
    up.mkdir(parents=True, exist_ok=True)
    out = {"specimen_id": specimen_id, "fetched": [], "body": str(body)}
    for art in origin.get("artifacts", []):
        kind = art["kind"]
        if kind == "url":
            dest = up / art["filename"]
            if dest.exists() and art.get("sha256") and vault.sha256_file(dest) == art["sha256"]:
                f = {"url": art["url"], "path": str(dest), "sha256": art["sha256"], "cached": True}
            else:
                f = vault.fetch_url(art["url"], dest)
                if art.get("sha256") and f["sha256"] != art["sha256"]:
                    raise RuntimeError("sha256 mismatch for %s: got %s expected %s" % (art["url"], f["sha256"], art["sha256"]))
            art["sha256"] = f["sha256"]
            art["bytes"] = dest.stat().st_size
            if art.get("extract", True) and dest.name.lower().endswith((".gz", ".tgz", ".zip", ".bz2", ".xz", ".tar")):
                root = vault.extract(dest, up / "tree")
                art["extracted_to"] = str(root.relative_to(body)).replace("\\", "/")
            out["fetched"].append(f)
        elif kind == "git":
            dest = up / "tree"
            g = vault.git_pin(art["url"], art["commit"], dest)
            art.update({"commit_resolved": g["commit"], "commit_date": g["commit_date"]})
            if art["commit"] == "HEAD":
                art["commit"] = g["commit"]          # the pin is exact from now on
            out["fetched"].append(g)
        else:
            raise ValueError("unknown artifact kind " + kind)
    # hash EVERYTHING under upstream/: the immutable archive(s) as fetched plus the extracted
    # tree plus any loose files, so one tree hash covers the whole body
    rows = vault.hash_tree(up)
    vault.write_hashes(specimen_id, rows)
    rec["hashes"] = {"tree_sha256": vault.tree_hash_of(rows), "n_files": len(rows),
                     "bytes": sum(r[2] for r in rows),
                     "artifacts": [{"filename": a.get("filename") or a.get("url"), "sha256": a.get("sha256"),
                                    "commit": a.get("commit_resolved")} for a in origin.get("artifacts", [])],
                     "body_location": str(body), "hash_list": "techne/fossils/specimens/%s/UPSTREAM_HASHES.txt" % specimen_id}
    rec["acquisition_date"] = time.strftime("%Y-%m-%d", time.gmtime())
    record.save(rec)
    out["tree_sha256"] = rec["hashes"]["tree_sha256"]
    out["n_files"] = len(rows)
    print(json.dumps({k: v for k, v in out.items() if k != "fetched"}, indent=1))
    return out


def verify(specimen_id: str) -> bool:
    body = vault.body_dir(specimen_id)
    rows = vault.hash_tree(body / "upstream")
    want = record.load(specimen_id)["hashes"].get("tree_sha256")
    got = vault.tree_hash_of(rows)
    print(specimen_id, "tree", got, "matches" if got == want else "DIFFERS FROM RECORD %s" % want)
    return got == want


# --------------------------------------------------------------------------- mirror
def mirror(dest: str, specimen_ids=None, dry_run: bool = False) -> dict:
    """Copy preserved bodies to an off-host store keyed by their immutable tree hash.

    TECHNE-65: the DESTINATION is the operator's decision; this function only makes the copy
    executable once it is named. For each specimen whose body is present and VERIFIED against
    its record, upstream/ is copied to <dest>/<tree_sha256>/upstream/ (content-addressed: the
    same body from any host lands in the same place; a drifted body is refused, never mirrored),
    the copy is re-hashed, and a receipt row carries source hash, destination hash, bytes and
    the verdict. The receipt is tracked under techne/fossils/mirror/; the bodies never enter git,
    and a destination inside the repository is refused."""
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    d = pathlib.Path(dest).resolve()
    try:
        d.relative_to(vault.REPO.resolve())
        raise ValueError("mirror destination %s is inside the repository; bodies never enter git" % d)
    except ValueError as e:
        if "inside the repository" in str(e):
            raise
    ids = specimen_ids or sorted(p.parent.name for p in vault.SPECIMENS.glob("*/record.json"))
    rep = {"schema": "techne.fossil.mirror_receipt/1", "receipt_id": "mirror-%s" % ts, "written_utc": ts,
           "destination": str(d), "dry_run": dry_run, "rows": []}
    for sid in ids:
        body = vault.body_dir(sid) / "upstream"
        row = {"specimen_id": sid, "source": str(body)}
        if not body.exists():
            row["status"] = "BODY_MISSING_ON_THIS_HOST"; rep["rows"].append(row); continue
        dr = drift(sid)
        row["source_tree_sha256"] = dr["tree_sha256_now"]
        if not dr["matches"]:
            row["status"] = "REFUSED_SOURCE_DRIFTED"; rep["rows"].append(row); continue
        target = d / dr["tree_sha256_now"] / "upstream"
        row["destination"] = str(target)
        row["bytes"] = sum(n for _, _, n in vault.hash_tree(body))
        if dry_run:
            row["status"] = "WOULD_COPY" if not target.exists() else "ALREADY_PRESENT"; rep["rows"].append(row); continue
        if target.exists():
            got = vault.tree_hash_of(vault.hash_tree(target))
            row["destination_tree_sha256"] = got
            row["status"] = "ALREADY_PRESENT_VERIFIED" if got == dr["tree_sha256_now"] else "ALREADY_PRESENT_DIFFERS"
            rep["rows"].append(row); continue
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name("upstream.partial")
        if tmp.exists():
            _rmtree(tmp)
        shutil.copytree(body, tmp, symlinks=True)
        got = vault.tree_hash_of(vault.hash_tree(tmp))
        row["destination_tree_sha256"] = got
        if got == dr["tree_sha256_now"]:
            tmp.rename(target); row["status"] = "COPIED_VERIFIED"
        else:
            row["status"] = "COPY_DIFFERS_LEFT_AS_PARTIAL"
        rep["rows"].append(row)
    rep["summary"] = {k: sum(1 for r in rep["rows"] if r["status"] == k) for k in sorted({r["status"] for r in rep["rows"]})}
    out = vault.REPO / "techne" / "fossils" / "mirror" / (rep["receipt_id"] + (".dryrun" if dry_run else "") + ".json")
    out.parent.mkdir(parents=True, exist_ok=True)
    k = 1
    while out.exists():                       # two invocations inside one second never share a receipt
        k += 1
        out = out.with_name("%s-%d%s.json" % (rep["receipt_id"], k, ".dryrun" if dry_run else ""))
    out.write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("mirror ->", d, rep["summary"], "receipt", out)
    return rep


# --------------------------------------------------------------------------- run
def run(specimen_id: str, timeout: int = 1800) -> dict:
    rec = record.load(specimen_id)
    sd = vault.specimen_dir(specimen_id)
    recipe = json.loads((sd / "recipe.json").read_text(encoding="utf-8"))
    body = vault.body_dir(specimen_id)
    rel = recipe.get("workdir", "upstream/tree")
    runner = recipe["runner"]
    in_place = bool(recipe.get("in_place", False))
    # ISOLATION: the recipe executes in a disposable copy of the body (work/), never in the
    # preserved upstream/. The copy carries upstream/ + Techne's harness/ + an empty build/, so
    # every $BODY-relative path in a recipe resolves unchanged. in_place=true is the opt-out.
    exec_body = body if in_place else _stage_work(body, sd)
    if in_place and (sd / "harness").exists():
        if (body / "harness").exists():
            _rmtree(body / "harness")
        shutil.copytree(sd / "harness", body / "harness")
    workdir = exec_body / rel
    image = recipe.get("image")
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    rundir = body / "run" / ts
    rundir.mkdir(parents=True, exist_ok=True)
    receipt = {"schema": "techne.fossil.run_receipt/1", "specimen_id": specimen_id, "receipt_id": "run-%s-%s" % (specimen_id, ts),
               "written_utc": ts, "runner": runner, "image": image, "workdir": rel,
               "isolation": "in_place" if in_place else "disposable_copy",
               "exec_root": str(exec_body.relative_to(body)).replace("\\", "/") if exec_body != body else ".",
               "harness_sha256": {str(p.relative_to(sd / "harness")).replace("\\", "/"): vault.sha256_file(p) for p in sorted((sd / "harness").rglob("*")) if p.is_file()} if (sd / "harness").exists() else {},
               "host": {"platform": platform.platform(), "python": sys.version.split()[0]},
               "tree_sha256_before": rec["hashes"].get("tree_sha256"),
               "recipe_sha256": vault.sha256_file(sd / "recipe.json"),
               "patches": [], "probe": [], "build": [], "runs": [], "tests": [],
               "produced": [], "classification": None, "test_classification": None, "ok": None}
    for pth in sorted((sd / "patches").glob("*")) if (sd / "patches").exists() else []:
        if pth.is_file():
            receipt["patches"].append({"file": pth.name, "sha256": vault.sha256_file(pth)})

    def do(section, items):
        all_ok = True
        for it in items:
            cmd = it["cmd"] if isinstance(it, dict) else it
            res = _shell(runner, cmd, exec_body, rel, image, it.get("timeout", timeout) if isinstance(it, dict) else timeout)
            ok, why = _expect_ok(res, it.get("expect") if isinstance(it, dict) else None)
            name = it.get("name", cmd[:40]) if isinstance(it, dict) else cmd[:40]
            (rundir / ("%s-%s.stdout.txt" % (section, re.sub(r"[^A-Za-z0-9_.-]+", "_", name)[:60]))).write_text(res["stdout"], encoding="utf-8", errors="replace")
            (rundir / ("%s-%s.stderr.txt" % (section, re.sub(r"[^A-Za-z0-9_.-]+", "_", name)[:60]))).write_text(res["stderr"], encoding="utf-8", errors="replace")
            receipt[section].append({"name": name, "cmd": cmd, "exit": res["exit"], "seconds": res["seconds"],
                                     "ok": ok, "why_not": why, "stdout": _clip(res["stdout"]), "stderr": _clip(res["stderr"])})
            print("%-6s %-40s exit=%-3s %6.1fs %s %s" % (section, name[:40], res["exit"], res["seconds"], "OK " if ok else "FAIL", "; ".join(why)), flush=True)
            all_ok = all_ok and ok
            if section == "build" and not ok and it.get("stop_on_fail", True) if isinstance(it, dict) else (section == "build" and not ok):
                return False
        return all_ok

    before = {r[0]: r[1] for r in vault.hash_tree(workdir)} if recipe.get("track_products", True) else {}
    do("probe", recipe.get("probe", []))
    built = do("build", recipe.get("build", []))
    ran = do("runs", recipe.get("runs", [])) if built else False
    tested = do("tests", recipe.get("tests", [])) if built and recipe.get("tests") else None
    if recipe.get("track_products", True):
        after = vault.hash_tree(workdir)
        receipt["produced"] = [{"path": rel, "sha256": h, "bytes": n} for rel, h, n in after
                               if before.get(rel) != h][:200]
    if built and ran:
        receipt["classification"] = recipe.get("classification_if_ok", "RUNNABLE_NATIVE")
    elif built:
        receipt["classification"] = recipe.get("classification_if_built_only", "BUILDS_BUT_NOT_RUN")
    else:
        receipt["classification"] = recipe.get("classification_if_build_fails", "BROKEN_UPSTREAM")
    if tested is None:
        receipt["test_classification"] = recipe.get("test_classification_if_none", "NO_TESTS")
    elif tested and recipe.get("test_classification_override"):
        receipt["test_classification"] = recipe["test_classification_override"]
    else:
        kind = recipe.get("test_kind", "UPSTREAM")
        receipt["test_classification"] = ("%s_PASS" if tested else "%s_FAIL") % ("UPSTREAM_TESTS" if kind == "UPSTREAM" else "TECHNE_SMOKE_HARNESS")
    receipt["ok"] = bool(built and ran and (tested is None or tested))
    # the preservation property, measured after the run on the PRESERVED body, whatever ran
    after_rows = vault.hash_tree(body / "upstream")
    receipt["tree_sha256_after"] = vault.tree_hash_of(after_rows)
    receipt["body_preserved"] = receipt["tree_sha256_after"] == receipt["tree_sha256_before"]
    rp = sd / "receipts" / (receipt["receipt_id"] + ".json")
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    rec["run_classification"] = receipt["classification"]
    rec["test_classification"] = receipt["test_classification"]
    try:
        rp_rel = str(rp.relative_to(vault.REPO)).replace("\\", "/")
    except ValueError:
        rp_rel = str(rp).replace("\\", "/")
    rec["receipts"].append({"receipt": rp_rel, "ok": receipt["ok"],
                            "classification": receipt["classification"], "test_classification": receipt["test_classification"]})
    record.save(rec)
    print("RECEIPT", rp, receipt["classification"], receipt["test_classification"], "ok=%s" % receipt["ok"])
    print("BODY", "PRESERVED" if receipt["body_preserved"] else "DIRTIED: tree %s != recorded %s" % (
        receipt["tree_sha256_after"], receipt["tree_sha256_before"]), "(isolation=%s)" % receipt["isolation"])
    return receipt


def _stage_work(body: pathlib.Path, sd: pathlib.Path) -> pathlib.Path:
    """A fresh disposable copy of the body for one run: work/{upstream,harness,build}."""
    work = body / "work"
    if work.exists():
        _rmtree(work)
    work.mkdir(parents=True)
    shutil.copytree(body / "upstream", work / "upstream", symlinks=True)
    if (sd / "harness").exists():
        shutil.copytree(sd / "harness", work / "harness")
    (work / "build").mkdir()
    return work


# --------------------------------------------------------------------------- status / summary
def _all_records():
    for p in sorted(vault.SPECIMENS.glob("*/record.json")):
        yield json.loads(p.read_text(encoding="utf-8"))


def status():
    for r in _all_records():
        print("%-28s %-6s %-22s %-24s %-26s %s" % (r["specimen_id"], r["era"][:6], r["run_classification"],
                                                   r["test_classification"], (r.get("language") or [""])[0][:26] if isinstance(r.get("language"), list) else r["language"], r["canonical_name"]))


def summary() -> dict:
    recs = list(_all_records())
    n = len(recs)
    def frac(pred):
        k = sum(1 for r in recs if pred(r))
        return "%d/%d" % (k, n)
    langs, eras, domains, lineages = set(), set(), set(), set()
    for r in recs:
        langs.update(r.get("language") or [])
        eras.add((r.get("era") or "")[:4])
        domains.update(r.get("domain") or [])
        lineages.add(r.get("lineage"))
    out = {
        "specimens": n,
        "unique_lineages": len(lineages),
        "era_coverage_decades": sorted({e[:3] + "0s" for e in eras if e}),
        "language_coverage": sorted(langs),
        "problem_pressure_domains": sorted(domains),
        "runnable": frac(lambda r: r["run_classification"].startswith("RUNNABLE")),
        "testable": frac(lambda r: r["test_classification"] in ("UPSTREAM_TESTS_PASS", "TECHNE_SMOKE_HARNESS_PASS")),
        "source_available": frac(lambda r: r["source_type"] in record.SOURCE_TYPES[:5]),
        "exact_version_pinned": frac(lambda r: bool(r.get("hashes", {}).get("tree_sha256"))),
        "historical_versions_preserved": sum(len(r.get("versions_preserved") or []) for r in recs),
        "executable_receipts": sum(1 for r in recs for x in r.get("receipts", []) if x.get("ok")),
        "provenance_complete": frac(lambda r: not record.validate(r)),
        "nyx_ready": frac(lambda r: r["run_classification"].startswith("RUNNABLE") and not record.validate(r)
                          and any(x.get("ok") for x in r.get("receipts", []))),
    }
    print(json.dumps(out, indent=2))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("acquire"); a.add_argument("specimen_id")
    r = sub.add_parser("run"); r.add_argument("specimen_id"); r.add_argument("--timeout", type=int, default=1800)
    v = sub.add_parser("verify"); v.add_argument("specimen_id", nargs="?"); v.add_argument("--all", action="store_true"); v.add_argument("--out")
    rs = sub.add_parser("restore"); rs.add_argument("specimen_id")
    mi = sub.add_parser("mirror"); mi.add_argument("--dest", required=True); mi.add_argument("--specimen", action="append"); mi.add_argument("--dry-run", action="store_true")
    sub.add_parser("status"); sub.add_parser("summary")
    args = ap.parse_args(argv)
    if args.cmd == "acquire":
        acquire(args.specimen_id)
    elif args.cmd == "run":
        rc = run(args.specimen_id, args.timeout)
        return 0 if rc["ok"] else 1
    elif args.cmd == "verify":
        if args.all or not args.specimen_id:
            c = verify_all(args.out)
            return 0 if c["differs"] == 0 and c["body_missing"] == 0 else 1
        return 0 if verify(args.specimen_id) else 1
    elif args.cmd == "restore":
        return 0 if restore(args.specimen_id)["verified"] else 1
    elif args.cmd == "mirror":
        r = mirror(args.dest, args.specimen, args.dry_run)
        bad = [x for x in r["rows"] if x["status"] in ("REFUSED_SOURCE_DRIFTED", "COPY_DIFFERS_LEFT_AS_PARTIAL", "ALREADY_PRESENT_DIFFERS")]
        return 1 if bad else 0
    elif args.cmd == "status":
        status()
    elif args.cmd == "summary":
        summary()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
