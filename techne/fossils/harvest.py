"""Fossil harvest CLI: acquire a body into the vault, run its recipe, write the receipt.

    python -m techne.fossils.harvest acquire <specimen_id>        fetch per record.source_origin, hash, extract
    python -m techne.fossils.harvest run <specimen_id>            execute recipe.json (build, run, tests) -> receipt
    python -m techne.fossils.harvest verify <specimen_id>         re-hash the body against UPSTREAM_HASHES.txt
    python -m techne.fossils.harvest verify --all [--out F]       every body; the census as JSON rows
    python -m techne.fossils.harvest restore <specimen_id>        put a drifted body back to its pin (rows in a receipt)
    python -m techne.fossils.harvest mirror --dest D [--dry-run]  copy verified bodies to D/<tree_sha256>/ (TECHNE-65: D is the operator's call)
    python -m techne.fossils.harvest mirror-verify --dest D      re-hash every mirrored body against the records (a corrupted mirror file MUST fail this)
    python -m techne.fossils.harvest status                       one line per specimen
    python -m techne.fossils.harvest summary                      the directive's success measures, computed
    python -m techne.fossils.harvest rematerialize <id> | --all [--out F]  second host: fetch from origin, verify by hash, never write tracked files
    python -m techne.fossils.harvest repin <id> --reason R     repair a CRLF/residue-defective record from upstream.drifted/ (old list kept as superseded)
    python -m techne.fossils.harvest receipt-check [--out F]      RQ-4 census: receipts carrying / predating the environment block

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

ENVIRONMENT (2026-09-16, Rhadamanthus #245 RQ-4). Receipt schema /2 carries an "environment"
block: interpreter implementation + version, sha256 over the sorted `name==version` list of every
installed distribution, and the NAMES of the environment variables the vault code read (through
vault.getenv; never a value) plus the names it exports into recipe commands. run() validates its
own receipt (validate_run_receipt) before writing it; `receipt-check` censuses the tracked ones.
"""
from __future__ import annotations

import argparse
import json
import os
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

# archive kinds restore() can re-extract a dirtied file from (module-level: the batch-10
# de-duplication briefly deleted this along with the stale acquire() it happened to sit after,
# which test_fossil_isolation caught immediately).
ARCHIVE_SUFFIXES = (".tar.gz", ".tgz", ".tar.bz2", ".tar.xz", ".tar", ".zip")

MAX_CAPTURE = 4000


# --------------------------------------------------------------------------- runners


# --------------------------------------------------------------------------- acquire


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
    """Destroy a directory tree that Linux builds may have filled with names Windows cannot address
    by ordinary path (a trailing dot: the Ada sorter's "WORK."). First the extended-length prefix,
    then, if residue remains, `wsl rm -rf` on the same directory (the runners that created the
    names can delete them). Never returns with the directory still present."""
    p = pathlib.Path(p)
    target = ("\\\\?\\" + str(p.resolve())) if os.name == "nt" else str(p)
    try:
        if sys.version_info >= (3, 12):
            shutil.rmtree(target, onexc=_rm_readonly)
        else:
            shutil.rmtree(target, onerror=_rm_readonly)
    except OSError:
        pass
    if p.exists() and os.name == "nt" and shutil.which("wsl.exe"):
        subprocess.run(["wsl.exe", "-e", "rm", "-rf", vault.to_wsl(p)], timeout=600)
    if p.exists():
        raise OSError("could not remove %s (residue: %s)" % (p, [x.name for x in p.rglob("*")][:5]))


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


# --------------------------------------------------------------------------- environment (RQ-4)
RUN_RECEIPT_SCHEMA = "techne.fossil.run_receipt/2"
# names the runner EXPORTS into every recipe command (see _shell); values are paths, so names only
ENV_EXPORTED_TO_RECIPE = ("BODY", "HARNESS")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def pip_freeze_lines() -> list[str]:
    """`name==version` for every installed distribution visible to THIS interpreter, sorted and
    de-duplicated, from importlib.metadata rather than a pip subprocess (same answer, no shell)."""
    from importlib import metadata
    seen = set()
    for d in metadata.distributions():
        name = (d.metadata["Name"] or "").strip()
        if name:
            seen.add("%s==%s" % (name.lower(), (d.version or "").strip()))
    return sorted(seen)


def environment_fingerprint(env_reads=None) -> dict:
    """What the harvest driver ran under (Rhadamanthus #245 RQ-4): interpreter version, a hash of
    the package state, and the NAMES of the environment variables read -- never a value. The
    recipe's own world (image, toolchain) is a separate fact and stays in the receipt's probe."""
    import hashlib
    lines = pip_freeze_lines()
    reads = sorted(set(vault.ENV_READS if env_reads is None else env_reads))
    return {"interpreter": {"implementation": platform.python_implementation(),
                            "version": platform.python_version(),
                            "executable_basename": pathlib.Path(sys.executable).name},
            "pip_freeze_sha256": hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest(),
            "pip_freeze_n": len(lines),
            "env_vars_read": reads,
            "env_vars_exported_to_recipe": list(ENV_EXPORTED_TO_RECIPE)}


def validate_run_receipt(receipt: dict) -> list[str]:
    """Defects in a run receipt's environment block, as strings; [] means it carries RQ-4.
    Schema /1 receipts predate the field and are reported as such rather than failed."""
    why = []
    schema = receipt.get("schema")
    if schema == "techne.fossil.run_receipt/1":
        return ["schema/1 receipt: predates the environment block (not a defect of the receipt)"]
    if schema != RUN_RECEIPT_SCHEMA:
        return ["unknown receipt schema %r" % (schema,)]
    env = receipt.get("environment")
    if not isinstance(env, dict):
        return ["environment block missing"]
    it = env.get("interpreter")
    if not isinstance(it, dict) or not it.get("version") or not it.get("implementation"):
        why.append("interpreter version/implementation missing")
    if not _HEX64.match(str(env.get("pip_freeze_sha256", ""))):
        why.append("pip_freeze_sha256 is not a sha256 hex digest")
    reads = env.get("env_vars_read")
    if not isinstance(reads, list) or not all(isinstance(n, str) for n in reads):
        why.append("env_vars_read is not a list of names")
    else:
        for n in reads:
            if "=" in n or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", n):
                why.append("env_vars_read carries something that is not a bare name: %r" % n[:40])
    for key in ("host", "tree_sha256_before", "recipe_sha256"):
        if key not in receipt:
            why.append("%s missing" % key)
    return why


# --------------------------------------------------------------------------- native shell (TECHNE-101)
# The native runner used to launch ["bash", ...] by NAME. On Windows, CreateProcess searches
# System32 before PATH, so the process that ran was C:\Windows\System32\bash.exe -- the WSL
# launcher -- while the tests' guard, shutil.which("bash"), answered from PATH (Git's bash).
# On a host without a WSL distro every native recipe therefore reported exit 1 (found on M3,
# 2026-09-17); on M1/M2 the two resolutions agreed only because there the launcher IS a distro.
# Now the shell is resolved once per process BY CAPABILITY -- it must run and print its own
# BASH_VERSION -- to an absolute path that the receipt records. Candidates are tried in the
# order CreateProcess would have used (System32 first, then PATH), so a host where the old
# resolution worked keeps the same bash and its receipts do not change.
NATIVE_SHELL_PROBE = "echo BASH_VERSION=$BASH_VERSION; uname -s"


class NativeShellUnavailable(RuntimeError):
    """No candidate bash passed the capability probe on this host."""


def native_shell_candidates() -> list[str]:
    """Every file a bare "bash" could resolve to, System32 first (what CreateProcess did), then
    PATH order; absolute, existing, de-duplicated. No drive letter is assumed anywhere."""
    cands: list[str] = []
    names = ("bash.exe", "bash") if os.name == "nt" else ("bash",)
    if os.name == "nt":
        sysroot = vault.getenv("SystemRoot") or vault.getenv("WINDIR")   # recorded reads (RQ-4)
        if sysroot:
            cands.append(str(pathlib.Path(sysroot) / "System32" / "bash.exe"))
    for d in (vault.getenv("PATH", "") or "").split(os.pathsep):
        if not d:
            continue
        for n in names:
            cands.append(str(pathlib.Path(d) / n))
    out, seen = [], set()
    for c in cands:
        try:
            if not os.path.isfile(c):
                continue
        except OSError:
            continue
        k = os.path.normcase(os.path.abspath(c))
        if k in seen:
            continue
        seen.add(k)
        out.append(os.path.abspath(c))
    return out


def probe_native_shell(path: str, timeout: int = 20) -> dict:
    """Run the candidate. It is a usable bash only if the probe exits 0 AND prints a BASH_VERSION;
    an exit code alone is a label (the cheat control in test_fossil_native_shell proves it)."""
    pr = {"path": path, "exit": None, "bash_version": None, "uname": None, "capable": False, "error": None}
    try:
        p = subprocess.run([path, "-c", NATIVE_SHELL_PROBE], capture_output=True, text=True,
                           timeout=timeout, errors="replace")
        out = (p.stdout or "").replace("\x00", "")
        m = re.search(r"BASH_VERSION=(\S+)", out)
        pr["exit"] = p.returncode
        pr["bash_version"] = m.group(1) if m else None
        lines = [ln.strip() for ln in out.splitlines() if ln.strip() and not ln.startswith("BASH_VERSION=")]
        pr["uname"] = lines[0][:60] if lines else None
        pr["capable"] = p.returncode == 0 and pr["bash_version"] is not None
    except (OSError, subprocess.TimeoutExpired) as e:
        pr["error"] = "%s: %s" % (type(e).__name__, str(e)[:120])
    return pr


_NATIVE_SHELL: dict | None = None
_NATIVE_SHELL_RESOLVED = False
_NATIVE_SHELL_PROBES: list[dict] = []


def native_shell(candidates: list[str] | None = None, refresh: bool = False) -> dict | None:
    """The first candidate that PROVES it is a bash, with every probe made on the way in
    ["probes"]; None when none does. Resolved once per process (explicit candidates are never
    cached: they are the tests' instrument)."""
    global _NATIVE_SHELL, _NATIVE_SHELL_RESOLVED, _NATIVE_SHELL_PROBES
    if candidates is None and _NATIVE_SHELL_RESOLVED and not refresh:
        return _NATIVE_SHELL
    probes: list[dict] = []
    chosen = None
    for c in (candidates if candidates is not None else native_shell_candidates()):
        pr = probe_native_shell(c)
        probes.append(pr)
        if pr["capable"]:
            chosen = dict(pr)
            chosen["probes"] = probes
            break
    if candidates is None:
        _NATIVE_SHELL, _NATIVE_SHELL_RESOLVED, _NATIVE_SHELL_PROBES = chosen, True, probes
    return chosen


def native_shell_probes() -> list[dict]:
    """The probes of the last process-level resolution (what was tried and refused)."""
    return list(_NATIVE_SHELL_PROBES)


# --------------------------------------------------------------------------- runners
def _shell(runner: str, cmd: str, body: pathlib.Path, rel: str, image: str | None, timeout: int,
           readonly: bool = False) -> dict:
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
                "docker run --rm -v %s:/w%s -w /w %s bash -lc %s" % (
                    shlex.quote(vault.to_wsl(body)), ":ro" if readonly else "", shlex.quote(image or "prometheus-fossil-c:bookworm"), shlex.quote(pre + cmd))]
    elif runner == "native":
        sh = native_shell()
        if sh is None:
            raise NativeShellUnavailable("no candidate bash passed the capability probe on %s: %s" % (
                platform.node(), "; ".join("%s -> exit %s" % (p["path"], p["exit"]) for p in native_shell_probes()) or "no candidates"))
        b = str(body).replace("\\", "/")
        pre = "export BODY=%s HARNESS=%s; cd %s && " % (shlex.quote(b), shlex.quote(b + "/harness"), shlex.quote(b + "/" + rel))
        full = [sh["path"], "-lc", pre + cmd]
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
def _fetch_artifacts(artifacts: list, up: pathlib.Path, body: pathlib.Path) -> list:
    """Fetch every artifact of a source_origin into <up>/ exactly as acquire() always has.
    MUTATES the artifact dicts it is given (sha256 / bytes / extracted_to / commit_resolved):
    acquire() passes the record's own list so the pins are written back; rematerialize()
    passes a deep copy so the record is never touched."""
    fetched = []
    for art in artifacts:
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
            fetched.append(f)
        elif kind == "file":
            # A file already on THIS host (a delivery from another seat, a run output): copied into the body,
            # never moved, and REFUSED if its sha256 differs from the record's pin. Directive 2026-09-19 s6:
            # preserving a rollout as a first-class fossil starts from a local, hashed file.
            src = pathlib.Path(art["source_path"])
            if not src.is_file():
                raise FileNotFoundError("file artifact source missing on this host: %s" % src)
            dest = up / art["filename"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            h = vault.sha256_file(src)
            if art.get("sha256") and h != art["sha256"]:
                raise RuntimeError("sha256 mismatch for file artifact %s: got %s expected %s" % (src, h, art["sha256"]))
            shutil.copyfile(src, dest)
            if vault.sha256_file(dest) != h:
                raise RuntimeError("copy of %s does not hash as its source" % src)
            art["sha256"] = h
            art["bytes"] = dest.stat().st_size
            fetched.append({"source_path": str(src), "path": str(dest), "sha256": h})
        elif kind == "git":
            dest = up / "tree"
            # Submodules are fetched only when the record DECLARES them ("submodules": "required"),
            # and then only at the commits the superproject pins -- never implicitly, never at HEAD.
            want_subs = str(art.get("submodules", "")).lower() in ("required", "true", "yes", "1")
            g = vault.git_pin(art["url"], art["commit"], dest, init_submodules=want_subs)
            art.update({"commit_resolved": g["commit"], "commit_date": g["commit_date"]})
            if art["commit"] == "HEAD":
                art["commit"] = g["commit"]          # the pin is exact from now on
            if g.get("submodules") is not None:
                art["submodules_pinned"] = [{"path": x["path"], "url": x["url"],
                                             "commit": x["pinned_commit"]} for x in g["submodules"]]
            fetched.append(g)
        else:
            raise ValueError("unknown artifact kind " + kind)
    return fetched


def acquire(specimen_id: str) -> dict:
    rec = record.load(specimen_id)
    origin = rec["source_origin"]
    body = vault.body_dir(specimen_id)
    up = body / "upstream"
    up.mkdir(parents=True, exist_ok=True)
    out = {"specimen_id": specimen_id, "fetched": [], "body": str(body)}
    out["fetched"] = _fetch_artifacts(origin.get("artifacts", []), up, body)
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
    rec["preservation"] = preservation_of(specimen_id, rec)
    out["preservation"] = rec["preservation"]["status"]
    record.save(rec)
    out["tree_sha256"] = rec["hashes"]["tree_sha256"]
    out["n_files"] = len(rows)
    print(json.dumps({k: v for k, v in out.items() if k != "fetched"}, indent=1))
    return out


# --------------------------------------------------------------------------- rematerialize (second host)
REMAT_SCHEMA = "techne.fossil.rematerialize/1"


def rematerialize(specimen_id: str, timeout: int = 900) -> dict:
    """Bring a preserved body onto THIS host from its recorded origin and prove it is the same
    body -- without touching anything tracked. The test of PRESERVATION.md's guarantee
    ("reconstructible from the recorded origin + verifiable by hash"), one specimen at a time.

        ALREADY_PRESENT_VERIFIED  a body is here and matches the record; nothing fetched
        ALREADY_PRESENT_DRIFTED   a body is here and does NOT match; left alone (see restore)
        MATCH                     fetched to a staging dir, tree hash == record; installed as upstream/
        DRIFT                     fetched, tree hash != record; kept at upstream.drifted/, NOT installed
        ORIGIN_UNREACHABLE        a fetch failed (network, 404, gone, sha256 mismatch on an archive);
                                  staging removed, nothing installed
        NO_ORIGIN                 the record names no artifacts

    record.json and UPSTREAM_HASHES.txt are never written. A DRIFT or ORIGIN_UNREACHABLE row is
    the finding: that body exists only where it was first acquired and must be copied by hash."""
    import copy
    t0 = time.time()
    rec = record.load(specimen_id)
    body = vault.body_dir(specimen_id)
    row = {"specimen_id": specimen_id, "tree_sha256_recorded": rec["hashes"].get("tree_sha256"),
           "n_files_recorded": rec["hashes"].get("n_files"), "status": None, "tree_sha256_fetched": None,
           "n_files_fetched": None, "bytes_fetched": None, "added": [], "removed": [], "modified": [],
           "error": None, "seconds": None}
    try:
        if (body / "upstream").exists():
            d = drift(specimen_id)
            row["status"] = "ALREADY_PRESENT_VERIFIED" if d["matches"] else "ALREADY_PRESENT_DRIFTED"
            row["tree_sha256_fetched"] = d["tree_sha256_now"]
            row["n_files_fetched"] = d["n_now"]
            row.update({k: d[k] for k in ("added", "removed", "modified")})
            return row
        arts = copy.deepcopy(rec["source_origin"].get("artifacts", []))
        if not arts:
            row["status"] = "NO_ORIGIN"
            return row
        stage = body / "rematerialize.tmp"
        if stage.exists():
            _rmtree(stage)
        up = stage / "upstream"
        up.mkdir(parents=True)
        try:
            _fetch_artifacts(arts, up, stage)
        except Exception as e:  # noqa: BLE001 -- the origin's failure IS the row
            row["status"] = "ORIGIN_UNREACHABLE"
            row["error"] = "%s: %s" % (type(e).__name__, str(e)[:300])
            _rmtree(stage)
            return row
        rows = vault.hash_tree(up)
        got = {rel: (h, n) for rel, h, n in rows}
        want = _want_rows(specimen_id)
        row["tree_sha256_fetched"] = vault.tree_hash_of(rows)
        row["n_files_fetched"] = len(rows)
        row["bytes_fetched"] = sum(r[2] for r in rows)
        row["added"] = sorted(set(got) - set(want))
        row["removed"] = sorted(set(want) - set(got))
        row["modified"] = sorted(r for r in want if r in got and got[r][0] != want[r][0])
        if row["tree_sha256_fetched"] == row["tree_sha256_recorded"]:
            body.mkdir(parents=True, exist_ok=True)
            shutil.move(str(up), str(body / "upstream"))
            _rmtree(stage)
            row["status"] = "MATCH"
        else:
            drifted = body / "upstream.drifted"
            if drifted.exists():
                _rmtree(drifted)
            body.mkdir(parents=True, exist_ok=True)
            shutil.move(str(up), str(drifted))
            _rmtree(stage)
            row["status"] = "DRIFT"
        return row
    finally:
        row["seconds"] = round(time.time() - t0, 1)
        print("%-32s %-26s %s" % (specimen_id, row["status"], row["error"] or (
            "+%d -%d ~%d" % (len(row["added"]), len(row["removed"]), len(row["modified"])) if row["status"] == "DRIFT" else "")), flush=True)


def rematerialize_all(out=None, specimen_ids=None, timeout: int = 900) -> dict:
    """Every specimen through rematerialize(); the census is written after EVERY row so a killed
    run leaves a readable partial file."""
    ids = sorted(specimen_ids or (p.parent.name for p in vault.SPECIMENS.glob("*/record.json")))
    census = {"schema": REMAT_SCHEMA, "written_utc": None, "host": platform.node(),
              "vault_root": str(vault.vault_root()), "specimens": len(ids), "complete": False,
              "counts": {}, "rows": []}

    def flush():
        census["written_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        c = {}
        for r in census["rows"]:
            c[r["status"]] = c.get(r["status"], 0) + 1
        census["counts"] = c
        if out:
            pathlib.Path(out).write_text(json.dumps(census, indent=1) + "\n", encoding="utf-8", newline="\n")

    for sid in ids:
        census["rows"].append(rematerialize(sid, timeout=timeout))
        flush()
    census["complete"] = True
    flush()
    print("REMATERIALIZE", census["specimens"], "specimens", json.dumps(census["counts"], sort_keys=True))
    return census



# --------------------------------------------------------------------------- repin (record repair)
REPIN_SCHEMA = "techne.fossil.repin_receipt/1"


def classify_drift(specimen_id: str, fetched_root: pathlib.Path) -> dict:
    """Explain a DRIFT file by file against a hash-verified fetch. Classes:
    SAME; RECORD_IS_CRLF (recorded hash == sha256 of the fetched bytes with LF->CRLF, i.e. the
    record was taken over a Windows-converted checkout); NOT_IN_ORIGIN (recorded, absent from
    the pinned fetch -- by construction not upstream content: a build product or interpreter
    residue hashed into the record); FETCH_IS_CRLF (the reverse smudge, a fetch-side defect);
    OTHER (real content difference); plus ADDED (in the fetch, not in the record)."""
    import hashlib
    want = _want_rows(specimen_id)
    got = {rel: (h, n) for rel, h, n in vault.hash_tree(fetched_root)}
    classes = {"SAME": [], "RECORD_IS_CRLF": [], "NOT_IN_ORIGIN": [], "FETCH_IS_CRLF": [], "OTHER": [],
               "ADDED": sorted(set(got) - set(want))}
    for rel, (h, n) in want.items():
        p = fetched_root / rel
        if rel not in got:
            classes["NOT_IN_ORIGIN"].append(rel)
            continue
        if got[rel][0] == h:
            classes["SAME"].append(rel)
            continue
        b = p.read_bytes()
        lf = b.replace(b"\r\n", b"\n")
        if hashlib.sha256(lf.replace(b"\n", b"\r\n")).hexdigest() == h:
            classes["RECORD_IS_CRLF"].append(rel)
        elif hashlib.sha256(lf).hexdigest() == h:
            classes["FETCH_IS_CRLF"].append(rel)
        else:
            classes["OTHER"].append(rel)
    return classes


def repin(specimen_id: str, reason: str) -> dict:
    """Repair a record whose hash list was taken over a Windows-converted and/or build-dirtied
    body, using the byte-exact fetch that `rematerialize` kept at upstream.drifted/.

    REFUSES unless the drift is FULLY explained by RECORD_IS_CRLF and NOT_IN_ORIGIN: any
    ADDED, FETCH_IS_CRLF or OTHER file means this is not a record defect and nothing is
    touched. On success: UPSTREAM_HASHES.txt is renamed UPSTREAM_HASHES.superseded-<date>.txt
    (kept, tracked), a new list is written from the fetch, record.hashes is replaced and the
    old block appended to record.hashes_superseded with the reason and the receipt path, the
    fetch becomes upstream/, and a tracked repin receipt carries every classified path.
    Any host still holding the old body will now fail `verify` for it -- that is correct and
    the receipt says so."""
    rec = record.load(specimen_id)
    sd = vault.specimen_dir(specimen_id)
    body = vault.body_dir(specimen_id)
    drifted = body / "upstream.drifted"
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out = {"schema": REPIN_SCHEMA, "specimen_id": specimen_id, "receipt_id": "repin-%s-%s" % (specimen_id, ts),
           "written_utc": ts, "host": platform.node(), "reason": reason, "status": None,
           "tree_sha256_old": rec["hashes"].get("tree_sha256"), "tree_sha256_new": None,
           "classes": None, "refused_because": []}
    if (body / "upstream").exists():
        out["refused_because"].append("upstream/ already present on this host; nothing to repin from")
    if not drifted.exists():
        out["refused_because"].append("no upstream.drifted/ (run rematerialize first; it keeps the fetch there on DRIFT)")
    if out["refused_because"]:
        out["status"] = "REFUSED"
        print("REPIN", specimen_id, "REFUSED:", "; ".join(out["refused_because"]))
        return out
    classes = classify_drift(specimen_id, drifted)
    out["classes"] = {k: sorted(v) for k, v in classes.items()}
    out["class_counts"] = {k: len(v) for k, v in classes.items()}
    for k in ("ADDED", "FETCH_IS_CRLF", "OTHER"):
        if classes[k]:
            out["refused_because"].append("%d file(s) %s -- not a record defect: %s" % (len(classes[k]), k, classes[k][:5]))
    if not (classes["RECORD_IS_CRLF"] or classes["NOT_IN_ORIGIN"]):
        out["refused_because"].append("nothing to repair (no RECORD_IS_CRLF or NOT_IN_ORIGIN files)")
    if out["refused_because"]:
        out["status"] = "REFUSED"
        print("REPIN", specimen_id, "REFUSED:", "; ".join(out["refused_because"]))
        return out
    # --- repair, in the order that leaves a recoverable state at every step
    rows = vault.hash_tree(drifted)
    old_list = sd / "UPSTREAM_HASHES.txt"
    superseded = sd / ("UPSTREAM_HASHES.superseded-%s.txt" % ts[:8])
    if superseded.exists():
        superseded = sd / ("UPSTREAM_HASHES.superseded-%s.txt" % ts)
    old_text = old_list.read_text(encoding="utf-8")
    superseded.write_text("# SUPERSEDED %s by %s -- %s\n" % (ts, out["receipt_id"], reason) + old_text,
                          encoding="utf-8", newline="\n")
    vault.write_hashes(specimen_id, rows)
    new_hashes = {"tree_sha256": vault.tree_hash_of(rows), "n_files": len(rows), "bytes": sum(r[2] for r in rows),
                  "artifacts": rec["hashes"].get("artifacts"), "body_location": str(body),
                  "hash_list": "techne/fossils/specimens/%s/UPSTREAM_HASHES.txt" % specimen_id}
    rp = sd / "receipts" / (out["receipt_id"] + ".json")
    rp_rel = "techne/fossils/specimens/%s/receipts/%s.json" % (specimen_id, out["receipt_id"])
    old_block = dict(rec["hashes"])
    old_block.update({"superseded_utc": ts, "reason": reason, "receipt": rp_rel,
                      "superseded_hash_list": "techne/fossils/specimens/%s/%s" % (specimen_id, superseded.name),
                      "class_counts": out["class_counts"]})
    rec.setdefault("hashes_superseded", []).append(old_block)
    rec["hashes"] = new_hashes
    record.save(rec)
    shutil.move(str(drifted), str(body / "upstream"))
    out["tree_sha256_new"] = new_hashes["tree_sha256"]
    out["n_files_old"] = old_block.get("n_files")
    out["n_files_new"] = len(rows)
    out["superseded_hash_list"] = old_block["superseded_hash_list"]
    out["consequence"] = ("any host whose body was hashed into the old list now fails verify for this specimen; "
                          "receipts before %s were run on that body (tree %s)" % (ts, out["tree_sha256_old"]))
    out["status"] = "REPINNED"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("REPIN", specimen_id, "REPINNED", out["tree_sha256_old"][:12], "->", out["tree_sha256_new"][:12],
          json.dumps(out["class_counts"], sort_keys=True))
    return out

# --------------------------------------------------------------------------- mirror
def mirror(dest: str, specimen_ids=None, dry_run: bool = False, allow_same_volume: bool = False) -> dict:
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
    # A mirror on the same volume as the vault is not redundancy (operator, TECHNE-65 ruling): the
    # destination must be a different storage device. On Windows the drive letter of the resolved
    # path is the cheap test; a UNC path has no drive letter and passes. Tests pass
    # allow_same_volume=True for their disposable controls and say so in the receipt.
    src_anchor = pathlib.Path(vault.vault_root()).resolve().anchor.upper()
    dst_anchor = d.anchor.upper()
    same_volume = bool(dst_anchor) and not dst_anchor.startswith("\\\\") and dst_anchor == src_anchor
    if same_volume and not allow_same_volume:
        raise ValueError("mirror destination %s is on the same volume as the vault (%s): not redundancy; "
                         "pass allow_same_volume only for a disposable control" % (d, vault.vault_root()))
    ids = specimen_ids or sorted(p.parent.name for p in vault.SPECIMENS.glob("*/record.json"))
    rep = {"schema": "techne.fossil.mirror_receipt/1", "receipt_id": "mirror-%s" % ts, "written_utc": ts,
           "destination": str(d), "dry_run": dry_run, "same_volume_as_vault": same_volume,
           "allow_same_volume": allow_same_volume, "rows": []}
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
    if not dry_run and d.exists():
        # the specimen -> tree-hash mapping lives beside the bodies so the mirror is self-describing
        idx_path = d / "MIRROR_INDEX.json"
        idx = json.loads(idx_path.read_text(encoding="utf-8")) if idx_path.exists() else {"schema": "techne.fossil.mirror_index/1", "specimens": {}}
        for r in rep["rows"]:
            if r["status"] in ("COPIED_VERIFIED", "ALREADY_PRESENT_VERIFIED"):
                idx["specimens"][r["specimen_id"]] = {"tree_sha256": r["source_tree_sha256"], "bytes": r.get("bytes"), "mirrored_utc": ts}
        idx["updated_utc"] = ts
        idx_path.write_text(json.dumps(idx, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        rep["index"] = str(idx_path)
    out = vault.REPO / "techne" / "fossils" / "mirror" / (rep["receipt_id"] + (".dryrun" if dry_run else "") + ".json")
    out.parent.mkdir(parents=True, exist_ok=True)
    k = 1
    while out.exists():                       # two invocations inside one second never share a receipt
        k += 1
        out = out.with_name("%s-%d%s.json" % (rep["receipt_id"], k, ".dryrun" if dry_run else ""))
    out.write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("mirror ->", d, rep["summary"], "receipt", out)
    return rep


def mirror_verify(dest: str, specimen_ids=None) -> dict:
    """Re-hash every mirrored body at <dest>/<tree_sha256>/upstream and compare with BOTH the
    directory name and the specimen's record. A corrupted, truncated or missing file in the
    mirror shows up as MIRROR_DIFFERS; a body the record expects that the mirror lacks shows up
    as MIRROR_MISSING. Writes a tracked receipt. Never touches the source bodies."""
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    d = pathlib.Path(dest).resolve()
    ids = specimen_ids or sorted(p.parent.name for p in vault.SPECIMENS.glob("*/record.json"))
    idx_path = d / "MIRROR_INDEX.json"
    idx = json.loads(idx_path.read_text(encoding="utf-8"))["specimens"] if idx_path.exists() else {}
    rep = {"schema": "techne.fossil.mirror_verify_receipt/1", "receipt_id": "mirror-verify-%s" % ts, "written_utc": ts,
           "destination": str(d), "index_present": idx_path.exists(), "rows": []}
    for sid in ids:
        want = record.load(sid)["hashes"].get("tree_sha256")
        row = {"specimen_id": sid, "recorded_tree_sha256": want}
        target = d / (want or "-") / "upstream"
        if not want or not target.exists():
            row["status"] = "MIRROR_MISSING"; rep["rows"].append(row); continue
        got = vault.tree_hash_of(vault.hash_tree(target))
        row["mirror_tree_sha256"] = got
        row["index_agrees"] = (idx.get(sid, {}).get("tree_sha256") == want) if idx else None
        row["status"] = "MIRROR_VERIFIED" if got == want else "MIRROR_DIFFERS"
        rep["rows"].append(row)
    rep["summary"] = {k: sum(1 for r in rep["rows"] if r["status"] == k) for k in sorted({r["status"] for r in rep["rows"]})}
    out = vault.REPO / "techne" / "fossils" / "mirror" / (rep["receipt_id"] + ".json")
    out.parent.mkdir(parents=True, exist_ok=True)
    k = 1
    while out.exists():
        k += 1; out = out.with_name("%s-%d.json" % (rep["receipt_id"], k))
    out.write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("mirror-verify", d, rep["summary"], "receipt", out)
    return rep


# --------------------------------------------------------------------------- run
def run(specimen_id: str, timeout: int = 1800, image=None, persist=None) -> dict:
    """image= runs the SAME preserved body and the SAME recipe in a DIFFERENT world (batch 10 P5:
    "test them using preserved bodies and explicit world changes"). A world-override never
    persists by default, so probing a fossil in a foreign world cannot overwrite its real
    classification or append a misleading receipt."""
    if persist is None:
        persist = image is None
    rec = record.load(specimen_id)
    sd = vault.specimen_dir(specimen_id)
    recipe = json.loads((sd / "recipe.json").read_text(encoding="utf-8"))
    if image:
        recipe["image"] = image
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
    receipt = {"schema": RUN_RECEIPT_SCHEMA, "specimen_id": specimen_id, "receipt_id": "run-%s-%s" % (specimen_id, ts),
               "written_utc": ts, "runner": runner, "image": image, "workdir": rel,
               "isolation": "in_place" if in_place else "disposable_copy",
               "exec_root": str(exec_body.relative_to(body)).replace("\\", "/") if exec_body != body else ".",
               "harness_sha256": {str(p.relative_to(sd / "harness")).replace("\\", "/"): vault.sha256_file(p) for p in sorted((sd / "harness").rglob("*")) if p.is_file()} if (sd / "harness").exists() else {},
               "host": {"platform": platform.platform(), "python": sys.version.split()[0]},
               # schema/2 (2026-09-16, RQ-4): interpreter, package-state hash, env-var NAMES read;
               # filled in AFTER the run so every read the run made is in the list
               "environment": None,
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

    # TECHNE-101: a native run names the shell that will execute it, resolved by capability.
    # No capable shell is a fact about THIS HOST, so the run is refused with a typed reason,
    # nothing is attempted, and nothing is persisted to the specimen's record.
    blocked = None
    if runner == "native":
        sh = native_shell()
        receipt["native_shell"] = sh if sh else {"path": None, "capable": False, "probes": native_shell_probes()}
        if sh is None:
            blocked = "NATIVE_SHELL_UNAVAILABLE"
            receipt["blocked_reason"] = blocked
            print("BLOCKED", specimen_id, blocked, "on host", platform.node(),
                  "-- candidates refused:", ", ".join(p["path"] for p in native_shell_probes()) or "none", flush=True)
    track = recipe.get("track_products", True) and not blocked
    before = {r[0]: r[1] for r in vault.hash_tree(workdir)} if track else {}
    if blocked:
        built, ran, tested = False, False, None
    else:
        do("probe", recipe.get("probe", []))
        built = do("build", recipe.get("build", []))
        ran = do("runs", recipe.get("runs", [])) if built else False
        tested = do("tests", recipe.get("tests", [])) if built and recipe.get("tests") else None
    if track:
        after = vault.hash_tree(workdir)
        receipt["produced"] = [{"path": rel, "sha256": h, "bytes": n} for rel, h, n in after
                               if before.get(rel) != h][:200]
    if blocked:
        receipt["classification"] = "BLOCKED_PLATFORM"
    elif built and ran:
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
    receipt["environment"] = environment_fingerprint()
    defects = validate_run_receipt(receipt)
    if defects:
        raise RuntimeError("run receipt fails its own environment check: " + "; ".join(defects))
    if blocked:
        receipt["persisted"] = False
        print("BLOCKED", specimen_id, blocked, receipt["classification"], "(not persisted: a host fact is not a specimen fact)")
        return receipt
    if not persist:
        receipt["persisted"] = False
        receipt["world_override_image"] = recipe.get("image")
        print("WORLD-PROBE", specimen_id, "image=%s" % recipe.get("image"),
              receipt["classification"], "ok=%s" % receipt["ok"], "(not persisted)")
        return receipt
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


# --------------------------------------------------------------- preservation completeness
# Charter 2026-09-13 (batch 09, P1/P8): a matching top-level tree hash does NOT mean the body is
# complete. avida hashed fine while libs/apto (required to build) was an empty directory. These
# functions classify what a body actually contains and FAIL when a declared external is missing.

_NETWORK_PAT = re.compile(
    r"(apt-get\s+(?:-\S+\s+)*install|apt-get\s+update|pip3?\s+install|npm\s+install|"
    r"go\s+get|cargo\s+(?:fetch|install)|gem\s+install|wget\s|curl\s|git\s+clone|conda\s+install)")

PRESERVATION_STATES = ("SELF_CONTAINED", "FULLY_PINNED_EXTERNALS", "UNPINNED_EXTERNAL_DEPENDENCY",
                       "KNOWN_INCOMPLETE", "UNKNOWN")
_RANK = {s: i for i, s in enumerate(PRESERVATION_STATES)}


def _recipe_network_deps(specimen_id):
    """Distinct network-fetch invocations appearing in the recipe (build/run time)."""
    rp = vault.specimen_dir(specimen_id) / "recipe.json"
    if not rp.exists():
        return []
    txt = rp.read_text(encoding="utf-8", errors="ignore")
    return sorted({m.group(1).strip() for m in _NETWORK_PAT.finditer(txt)})


def preservation_of(specimen_id, rec=None):
    """Classify how complete this body actually is. The body axis and the recipe axis are kept
    separate; `status` is the worse of the two, so nothing reads as preserved on a tree hash alone."""
    rec = rec or record.load(specimen_id)
    up = vault.body_dir(specimen_id) / "upstream"
    tree = up / "tree"
    arts = list(rec.get("source_origin", {}).get("artifacts", []))
    subs = vault.submodules_of(tree) if tree.exists() else []
    has_gitmodules = (tree / ".gitmodules").exists()
    missing = [x["path"] for x in subs if not x["present"]]
    drifted = [x["path"] for x in subs
               if x["present"] and x["pinned_commit"] and x["checked_out_commit"]
               and not x["checked_out_commit"].startswith(x["pinned_commit"][:12])]
    # The authoritative acquisition pin lives in hashes.artifacts (acquire() writes it there);
    # source_origin.artifacts is re-written by the batch scripts and loses sha256/commit_resolved,
    # so it must NOT be read as evidence of missing pinning.
    hart = {}
    for h in (rec.get("hashes", {}) or {}).get("artifacts", []) or []:
        hart[str(h.get("filename") or "")] = h
    unpinned = []
    for a in arts:
        if a.get("kind") == "url":
            h = hart.get(str(a.get("filename") or "")) or {}
            if not (a.get("sha256") or h.get("sha256")):
                unpinned.append("url:" + str(a.get("url", ""))[:70])
        if a.get("kind") == "git":
            h = hart.get(str(a.get("url") or "")) or {}
            if not (a.get("commit_resolved") or h.get("commit") or
                    (a.get("commit") and a.get("commit") != "HEAD")):
                unpinned.append("git:" + str(a.get("url", ""))[:70])
    lfs = False
    ga = tree / ".gitattributes"
    if ga.exists():
        lfs = "filter=lfs" in ga.read_text(encoding="utf-8", errors="ignore")

    if missing or drifted:
        body = "KNOWN_INCOMPLETE"
    elif has_gitmodules and not subs:
        body = "UNKNOWN"
    elif unpinned:
        body = "UNPINNED_EXTERNAL_DEPENDENCY"
    elif subs or lfs:
        body = "FULLY_PINNED_EXTERNALS"
    else:
        body = "SELF_CONTAINED"

    net = _recipe_network_deps(specimen_id)
    recipe = "NETWORK_DEPENDENT" if net else "NO_NETWORK_FETCH_DETECTED"
    status = body
    if net and _RANK[body] < _RANK["UNPINNED_EXTERNAL_DEPENDENCY"]:
        status = "UNPINNED_EXTERNAL_DEPENDENCY"
    return {"status": status, "body_status": body, "recipe_status": recipe,
            "submodules": subs, "submodules_missing": missing, "submodules_drifted": drifted,
            "unpinned_artifacts": unpinned, "git_lfs": lfs, "network_fetch_in_recipe": net,
            "checked_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "note": "status is the worse of body_status and the recipe axis; a matching tree hash "
                    "alone never implies completeness."}


def preservation_check(specimen_id):
    """INVARIANT. Returns (ok, problems). Fails when a submodule the superproject pins is absent
    from the body or checked out at a different commit -- the avida defect, and the negative
    control for this instrument."""
    p = preservation_of(specimen_id)
    problems = []
    for path in p["submodules_missing"]:
        problems.append("required submodule MISSING from body: %s" % path)
    for path in p["submodules_drifted"]:
        problems.append("submodule NOT at the pinned commit: %s" % path)
    if p["body_status"] == "UNKNOWN":
        problems.append(".gitmodules present but submodules could not be enumerated (no .git)")
    return (not problems), problems


def preservation_census(out=None):
    specimens = vault.specimen_dir("_").parent
    rows = []
    for sid in sorted(x.name for x in specimens.iterdir() if x.is_dir() and (x / "record.json").exists()):
        try:
            p = preservation_of(sid)
        except Exception as e:
            rows.append({"specimen_id": sid, "status": "UNKNOWN", "error": str(e)[:120]})
            continue
        rows.append({"specimen_id": sid, "status": p["status"], "body_status": p["body_status"],
                     "recipe_status": p["recipe_status"], "submodules": len(p["submodules"]),
                     "submodules_missing": p["submodules_missing"],
                     "unpinned_artifacts": p["unpinned_artifacts"],
                     "network_fetch_in_recipe": p["network_fetch_in_recipe"]})
    tally = {}
    for r in rows:
        tally[r["status"]] = tally.get(r["status"], 0) + 1
    doc = {"schema": "techne.fossil.preservation_census/1",
           "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "n": len(rows), "by_status": tally,
           "network_dependent": sum(1 for r in rows if r.get("recipe_status") == "NETWORK_DEPENDENT"),
           "rule": "body_status from submodules/lfs/artifact pinning; recipe_status from network "
                   "fetches in recipe.json; status = worse of the two. Mechanical, no judgement.",
           "rows": rows}
    if out:
        pathlib.Path(out).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
        print("preservation census", out, len(rows), "fossils", tally)
    return doc


def receipt_census(out=None) -> dict:
    """Every tracked run receipt, validated; the RQ-4 coverage count is derived, not asserted."""
    rows = []
    for rp in sorted(vault.SPECIMENS.glob("*/receipts/run-*.json")):
        try:
            rcpt = json.loads(rp.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            rows.append({"receipt": rp.name, "specimen_id": rp.parent.parent.name, "schema": None,
                         "status": "UNREADABLE", "defects": [str(e)[:120]]})
            continue
        why = validate_run_receipt(rcpt)
        legacy = rcpt.get("schema") == "techne.fossil.run_receipt/1"
        rows.append({"receipt": rp.name, "specimen_id": rp.parent.parent.name, "schema": rcpt.get("schema"),
                     "status": "PREDATES_RQ4" if legacy else ("CARRIES_RQ4" if not why else "DEFECTIVE"),
                     "defects": [] if legacy else why})
    c = {"n": len(rows), "carries_rq4": sum(r["status"] == "CARRIES_RQ4" for r in rows),
         "predates_rq4": sum(r["status"] == "PREDATES_RQ4" for r in rows),
         "defective": sum(r["status"] in ("DEFECTIVE", "UNREADABLE") for r in rows)}
    print("RECEIPT-CHECK n=%(n)d carries_rq4=%(carries_rq4)d predates_rq4=%(predates_rq4)d defective=%(defective)d" % c)
    for r in rows:
        if r["status"] in ("DEFECTIVE", "UNREADABLE"):
            print("  ", r["specimen_id"], r["receipt"], r["status"], "; ".join(r["defects"]))
    if out:
        pathlib.Path(out).write_text(json.dumps({"schema": "techne.fossil.receipt_census/1",
                                                 "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                                 "counts": c, "rows": rows}, indent=1) + "\n", encoding="utf-8", newline="\n")
    return c


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("acquire"); a.add_argument("specimen_id")
    r = sub.add_parser("run"); r.add_argument("specimen_id"); r.add_argument("--timeout", type=int, default=1800); r.add_argument("--image", help="run the same preserved body in a different world; never persists")
    v = sub.add_parser("verify"); v.add_argument("specimen_id", nargs="?"); v.add_argument("--all", action="store_true"); v.add_argument("--out")
    rs = sub.add_parser("restore"); rs.add_argument("specimen_id")
    mi = sub.add_parser("mirror"); mi.add_argument("--dest", required=True); mi.add_argument("--specimen", action="append"); mi.add_argument("--dry-run", action="store_true"); mi.add_argument("--allow-same-volume", action="store_true", help="disposable controls only")
    mv = sub.add_parser("mirror-verify"); mv.add_argument("--dest", required=True); mv.add_argument("--specimen", action="append")
    sub.add_parser("status"); sub.add_parser("summary")
    rm = sub.add_parser("rematerialize", help="bring bodies onto THIS host from their recorded origins and verify by hash; tracked files untouched"); rm.add_argument("specimen_id", nargs="?"); rm.add_argument("--all", action="store_true"); rm.add_argument("--out"); rm.add_argument("--timeout", type=int, default=900)
    rpn = sub.add_parser("repin", help="repair a record whose hash list was CRLF-converted / build-dirtied, from the byte-exact fetch at upstream.drifted/; refuses any real content difference"); rpn.add_argument("specimen_id"); rpn.add_argument("--reason", required=True)
    rc_ = sub.add_parser("receipt-check", help="RQ-4 census: every tracked run receipt by schema, defects listed"); rc_.add_argument("--out")
    pr = sub.add_parser("preservation"); pr.add_argument("specimen_id", nargs="?"); pr.add_argument("--all", action="store_true"); pr.add_argument("--out")
    args = ap.parse_args(argv)
    if args.cmd == "acquire":
        acquire(args.specimen_id)
    elif args.cmd == "run":
        rc = run(args.specimen_id, args.timeout, image=getattr(args, "image", None))
        return 0 if rc["ok"] else 1
    elif args.cmd == "verify":
        if args.all or not args.specimen_id:
            c = verify_all(args.out)
            return 0 if c["differs"] == 0 and c["body_missing"] == 0 else 1
        return 0 if verify(args.specimen_id) else 1
    elif args.cmd == "restore":
        return 0 if restore(args.specimen_id)["verified"] else 1
    elif args.cmd == "mirror-verify":
        r = mirror_verify(args.dest, args.specimen)
        return 0 if all(x["status"] == "MIRROR_VERIFIED" for x in r["rows"]) else 1
    elif args.cmd == "mirror":
        r = mirror(args.dest, args.specimen, args.dry_run, args.allow_same_volume)
        bad = [x for x in r["rows"] if x["status"] in ("REFUSED_SOURCE_DRIFTED", "COPY_DIFFERS_LEFT_AS_PARTIAL", "ALREADY_PRESENT_DIFFERS")]
        return 1 if bad else 0
    elif args.cmd == "preservation":
        if args.all or not args.specimen_id:
            preservation_census(args.out)
        else:
            ok, probs = preservation_check(args.specimen_id)
            print(json.dumps(preservation_of(args.specimen_id), indent=1))
            print("PRESERVATION", args.specimen_id, "OK" if ok else "FAIL", *probs)
            return 0 if ok else 1
    elif args.cmd == "rematerialize":
        if args.all or not args.specimen_id:
            c = rematerialize_all(args.out, timeout=args.timeout)
            bad = sum(v for k, v in c["counts"].items() if k not in ("MATCH", "ALREADY_PRESENT_VERIFIED"))
            return 0 if bad == 0 else 1
        r = rematerialize(args.specimen_id, timeout=args.timeout)
        return 0 if r["status"] in ("MATCH", "ALREADY_PRESENT_VERIFIED") else 1
    elif args.cmd == "repin":
        return 0 if repin(args.specimen_id, args.reason)["status"] == "REPINNED" else 1
    elif args.cmd == "receipt-check":
        c = receipt_census(args.out)
        return 0 if c["defective"] == 0 else 1
    elif args.cmd == "status":
        status()
    elif args.cmd == "summary":
        summary()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
