"""Instrument VERSION CodeRefs for stage records and receipts (C-004-T023B; draft B B4.1).

A stage belongs to an instrument VERSION, and evidence.authority finds the record by
predicate_version(receipt.predicate.code) == predicate_version(record.version); the CodeRef `commit` is inside
that hash. One convention therefore serves stage records (T023A, T023B) and the receipts of the real G0 (T024):

    one CodeRef per instrument, over its own source file:
      {"role": "code:<repo path>", "sha256": sha256 of the LF-normalised bytes (= the git blob for text),
       "length": their length, "commit": the full SHA of the last commit at `rev` that touched <path>}

Editing the file changes its blob and its last-touching commit, hence its version, hence it needs a new stage
record (B4.1). Proposed to Cadmus and Palamedes in comms #1411/#1412 (roles/Argus/comms/
2026-10-04_C-004_stage_version_convention.md). Python >= 3.8, standard library only.
"""
import hashlib
import os
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Evidence-plane and ruler instruments (T023B) and their source files.
SOURCES = {"CALIBRATION": "rso/slice001/rulers.py", "RETENTION": "rso/slice001/rulers.py",
           "G-BIND": "rso/slice001/evidence.py", "G-INV": "rso/slice001/evidence.py",
           "G-RECOMP": "rso/slice001/checker.py"}


class VersionError(RuntimeError):
    pass


def lf_bytes(path, root=REPO_ROOT):
    with open(os.path.join(root, *path.split("/")), "rb") as f:
        return f.read().replace(b"\r\n", b"\n")


def last_commit(path, rev="HEAD", root=REPO_ROOT):
    r = subprocess.run(["git", "log", "-1", "--format=%H", rev, "--", path], cwd=root, capture_output=True,
                       text=True, timeout=60)
    sha = r.stdout.strip()
    if r.returncode != 0 or len(sha) != 40:
        raise VersionError("no commit touches %s at %s" % (path, rev))
    return sha


def committed_blob(path, commit, root=REPO_ROOT):
    """LF bytes of <path> at <commit> (git show), for checking a CodeRef against history."""
    r = subprocess.run(["git", "show", "%s:%s" % (commit, path)], cwd=root, capture_output=True, timeout=60)
    if r.returncode != 0:
        raise VersionError("%s not present at %s" % (path, commit))
    return r.stdout.replace(b"\r\n", b"\n")


def code_ref(path, rev="HEAD", root=REPO_ROOT):
    data = lf_bytes(path, root)
    commit = last_commit(path, rev, root)
    if committed_blob(path, commit, root) != data:
        raise VersionError("%s differs from its last commit %s (uncommitted edit)" % (path, commit[:12]))
    return {"role": "code:" + path, "sha256": hashlib.sha256(data).hexdigest(), "length": len(data),
            "commit": commit}


def instrument_version(instrument, rev="HEAD", root=REPO_ROOT, sources=SOURCES):
    return [code_ref(sources[instrument], rev, root)]
