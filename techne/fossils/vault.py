"""The fossil vault: where preserved machinery lives, and the helpers that put it there.

Layout (operator directive 2026-09-12, roles/Techne/prompts/2026-09-12_fossil_harvest/):

    TRACKED in git, under techne/fossils/specimens/<specimen_id>/
        record.json        the machine-readable package record (schema in record.py)
        UPSTREAM_HASHES.txt sha256 of every upstream file, so the host-local copy is checkable
        recipe.json        how to build / run / test it (the commands the receipts executed)
        receipts/          run receipts, one file per attempt, append-only
        harness/           Techne's MINIMAL behavioural smoke harness, if upstream has no test
        patches/           compatibility patches, each with ancestry (never applied in place)
        environment/       Dockerfile / toolchain record / emulator config
        NOTES.md           anything a human must know that the record cannot hold

    HOST-LOCAL, gitignored, under <vault>/<specimen_id>/
        upstream/          the immutable upstream artefact(s) exactly as fetched + extracted tree
        build/             build products (disposable)
        recovered/         disassembly / decompilation, labelled RECOVERED REPRESENTATION
        run/               inputs and outputs of receipted runs

The vault root resolves, first hit wins: $TECHNE_FOSSIL_VAULT; techne/config.local.json
"fossil_vault"; <canonical checkout>/vault/fossils (parent of git-common-dir, so it is the
same directory from every worktree and no drive letter is assumed).

The tracked half is the durable, cross-machine half: hashes, records, recipes, receipts,
patches. The host-local half is the bodies. A second copy of the host-local half is a
storage decision for the operator (the Z: share has been the convention for large data); this
module records where the bodies are, it does not replicate them.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import tarfile
import time
import urllib.error
import urllib.request
import zipfile

REPO = pathlib.Path(__file__).resolve().parents[2]
SPECIMENS = REPO / "techne" / "fossils" / "specimens"

# Every environment variable the vault code READS goes through getenv() so a run receipt can
# name them (Rhadamanthus #245 RQ-4: names, never values). A direct os.environ.get() here is
# an unreceipted read; test_fossil_environment.py greps for it.
ENV_READS: set[str] = set()


def getenv(name: str, default=None):
    ENV_READS.add(name)
    return os.environ.get(name, default)


def canonical_root() -> pathlib.Path:
    try:
        out = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                             cwd=str(REPO), capture_output=True, text=True, timeout=30)
        if out.returncode == 0 and out.stdout.strip():
            return pathlib.Path(out.stdout.strip()).parent
    except (OSError, subprocess.TimeoutExpired):
        pass
    return REPO


def vault_root() -> pathlib.Path:
    env = getenv("TECHNE_FOSSIL_VAULT")
    if env:
        return pathlib.Path(env)
    local = REPO / "techne" / "config.local.json"
    try:
        cfg = json.loads(local.read_text(encoding="utf-8"))
        if cfg.get("fossil_vault"):
            return pathlib.Path(cfg["fossil_vault"])
    except (OSError, ValueError):
        pass
    return canonical_root() / "vault" / "fossils"


def specimen_dir(specimen_id: str) -> pathlib.Path:
    return SPECIMENS / specimen_id


def body_dir(specimen_id: str) -> pathlib.Path:
    return vault_root() / specimen_id


def to_wsl(p: pathlib.Path) -> str:
    """F:\\x\\y -> /mnt/f/x/y (WSL2 default drive mounts)."""
    p = pathlib.Path(p).resolve()
    drive = p.drive.rstrip(":").lower()
    rest = "/".join(p.parts[1:])
    return "/mnt/%s/%s" % (drive, rest)


# --------------------------------------------------------------------------- hashing
def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_tree(root: pathlib.Path, skip_dirs=(".git",)) -> list[tuple[str, str, int]]:
    """(relative path, sha256, bytes) for every file, sorted; .git excluded so a pinned clone
    hashes to its working tree, which is what anyone re-fetching will compare."""
    rows = []
    for p in sorted(root.rglob("*")):
        if any(part in skip_dirs for part in p.relative_to(root).parts):
            continue
        try:
            # a dangling or Linux-only symlink (autotools' build-aux/compile -> /usr/share/...) cannot
            # be stat'ed from Windows (WinError 1920); symlinks are not file content and are skipped
            if p.is_symlink() or not p.is_file():
                continue
            rows.append((str(p.relative_to(root)).replace("\\", "/"), sha256_file(p), p.stat().st_size))
        except OSError:
            continue
    return rows


def write_hashes(specimen_id: str, rows) -> pathlib.Path:
    d = specimen_dir(specimen_id)
    d.mkdir(parents=True, exist_ok=True)
    out = d / "UPSTREAM_HASHES.txt"
    total = sum(r[2] for r in rows)
    lines = ["# sha256  bytes  path   (%d files, %d bytes; tree hash below is sha256 over these lines)" % (len(rows), total)]
    lines += ["%s  %d  %s" % (h, n, rel) for rel, h, n in rows]
    body = "\n".join(lines[1:]) + "\n"
    tree_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
    lines.append("# TREE_SHA256 " + tree_hash)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return out


def tree_hash_of(rows) -> str:
    body = "\n".join("%s  %d  %s" % (h, n, rel) for rel, h, n in rows) + "\n"
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- fetching
def fetch_url(url: str, dest: pathlib.Path, timeout: int = 600) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "Prometheus-Techne-fossil-harvest/1"})
    final_url = url
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r, open(dest, "wb") as f:
            shutil.copyfileobj(r, f)
            final_url = r.geturl()
    except urllib.error.HTTPError as e:
        # sourceforge's download redirector answers 403 to urllib and 200 to curl; the
        # fetched bytes are what is hashed either way, so the transport is recorded, not trusted
        # (sourceforge also 403s any non-browser-looking User-Agent, so curl's default is kept)
        subprocess.run(["curl", "-sSL", "--fail", "-m", str(timeout), "-o", str(dest), url],
                       check=True, timeout=timeout + 30)
        final_url = url + "  (via curl after urllib HTTP %s)" % e.code
    return {"url": url, "final_url": final_url, "path": str(dest), "bytes": dest.stat().st_size,
            "sha256": sha256_file(dest), "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "seconds": round(time.time() - t0, 1)}


def extract(archive: pathlib.Path, into: pathlib.Path) -> pathlib.Path:
    into.mkdir(parents=True, exist_ok=True)
    name = archive.name.lower()
    if name.endswith((".tar.gz", ".tgz", ".tar.bz2", ".tar.xz", ".tar")):
        with tarfile.open(archive) as t:
            t.extractall(into, filter="data")
    elif name.endswith(".zip"):
        with zipfile.ZipFile(archive) as z:
            z.extractall(into)
    else:
        raise ValueError("unknown archive type: " + archive.name)
    kids = [p for p in into.iterdir()]
    return kids[0] if len(kids) == 1 and kids[0].is_dir() else into


def git_pin(url: str, commit: str, dest: pathlib.Path, timeout: int = 900,
            init_submodules: bool = False) -> dict:
    """Clone and check out EXACTLY `commit`; refuse to proceed if HEAD disagrees.

    When init_submodules, also fetch the submodules AT THE COMMITS THE SUPERPROJECT PINS
    (git submodule update --init --recursive uses the recorded gitlink SHAs, never HEAD) so
    the body is preservation-complete. The avida failure came from fetching a submodule at
    HEAD instead; this is the fix. Submodule metadata (path/url/pinned commit) is returned."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    GITENV = ["-c", "core.autocrlf=false", "-c", "core.eol=lf"]
    if not (dest / ".git").exists():
        # Force LF and no autocrlf so the working tree is BYTE-EXACT upstream, not Windows-
        # converted -- otherwise text files get CRLF on a Windows checkout and (a) the tree hash
        # would not match a Linux re-fetch and (b) shell scripts like tinycc's configure break.
        subprocess.run(["git", *GITENV, "clone", "--quiet", url, str(dest)], check=True, timeout=timeout)
    if commit == "HEAD":
        # "whatever the default branch is right now" -- resolved ONCE here and written back to
        # the record as commit_resolved, so the pin becomes exact from this moment on.
        commit = subprocess.run(["git", "-C", str(dest), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    else:
        subprocess.run(["git", "-C", str(dest), "fetch", "--quiet", "origin", commit], timeout=timeout)
    subprocess.run(["git", "-C", str(dest), "checkout", "--quiet", "--detach", commit], check=True, timeout=timeout)
    head = subprocess.run(["git", "-C", str(dest), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    if not head.startswith(commit):
        raise RuntimeError("HEAD %s != requested %s" % (head, commit))
    date = subprocess.run(["git", "-C", str(dest), "show", "-s", "--format=%cI", "HEAD"], capture_output=True, text=True).stdout.strip()
    out = {"url": url, "commit": head, "commit_date": date, "path": str(dest),
           "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if (dest / ".gitmodules").exists():
        if init_submodules:
            # update --init --recursive checks out the PINNED gitlink commits (not HEAD).
            subprocess.run(["git", "-C", str(dest), *GITENV, "submodule", "update", "--init",
                            "--recursive"], check=True, timeout=timeout)
        out["submodules"] = submodules_of(dest)
        out["submodules_fetched"] = bool(init_submodules)
    return out


def submodules_of(tree_dir: pathlib.Path) -> list:
    """Read-only census of a checked-out git tree's submodules (needs the tree's .git).
    Returns [{path, url, pinned_commit, present, checked_out_commit, n_files}]. present means
    the submodule working tree is populated (a real file besides its own .git)."""
    tree_dir = pathlib.Path(tree_dir)
    if not (tree_dir / ".gitmodules").exists() or not (tree_dir / ".git").exists():
        return []
    cfg = subprocess.run(["git", "-C", str(tree_dir), "config", "-f", ".gitmodules",
                          "--get-regexp", r"submodule\..*\.(path|url)"], capture_output=True, text=True).stdout
    paths, urls = {}, {}
    for line in cfg.splitlines():
        try:
            key, val = line.split(None, 1)
        except ValueError:
            continue
        name = key[len("submodule."):].rsplit(".", 1)[0]
        if key.endswith(".path"):
            paths[name] = val.strip()
        elif key.endswith(".url"):
            urls[name] = val.strip()
    ls = subprocess.run(["git", "-C", str(tree_dir), "ls-tree", "-r", "HEAD"], capture_output=True, text=True).stdout
    pinned = {}
    for line in ls.splitlines():
        # <mode> <type> <sha>\t<path>   -- mode 160000 marks a gitlink (submodule)
        meta, _, path = line.partition("\t")
        parts = meta.split()
        if len(parts) >= 3 and parts[0] == "160000":
            pinned[path] = parts[2]
    subs = []
    for name in sorted(set(paths) | set(urls)):
        rel = paths.get(name, name)
        sub_dir = tree_dir / rel
        present = sub_dir.exists() and any(p.name != ".git" for p in sub_dir.iterdir()) if sub_dir.exists() else False
        co = ""
        if present and (sub_dir / ".git").exists():
            co = subprocess.run(["git", "-C", str(sub_dir), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        n_files = sum(1 for p in sub_dir.rglob("*") if p.is_file() and ".git" not in p.relative_to(sub_dir).parts) if present else 0
        subs.append({"path": rel, "url": urls.get(name, ""), "pinned_commit": pinned.get(rel, ""),
                     "present": bool(present), "checked_out_commit": co, "n_files": n_files})
    return subs
