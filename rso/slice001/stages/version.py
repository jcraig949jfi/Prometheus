"""Instrument VERSION CodeRefs for the T023B stage records (C-004-T023B; draft B B4.1).

A stage belongs to an instrument VERSION, and evidence.authority finds the record by
predicate_version(receipt.predicate.code) == predicate_version(record.version); the CodeRef `commit` is inside
that hash. This follows the convention Cadmus fixed in T023A (rso/slice001/stages/fire_world.py): a version is
one CodeRef (adapter.file_code_ref: LF blob sha256 and length) per slice file the instrument imports and
executes, all at ONE commit on main that holds those sources. An edit to any of those files is a new version
and needs a new stage record. Receipts of the real G0 (T024) copy `version` from the record files, so the two
cannot drift. (Supersedes Argus's single-file proposal of comms #1411/#1412.)

Python >= 3.8, standard library only.
"""
import os
import re
import subprocess

from rso.slice001 import adapter as AD

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# The main commit the T023B versions are pinned to: the same one T023A pinned (Cadmus, 6f57aa7c6); every
# source below is byte-identical there and at the T023B base.
PINNED = "6f57aa7c62f22edc66ea6b35c8c4cbda0b6324ff"

_RULERS = ["rso/slice001/rulers.py", "rso/slice001/world.py"]
# C-009-T011: evidence.py executes rso/binding/binding.py (G-INV, custody), so it is part of every version that
# includes evidence.py; an edit to the binding is a new version of the gates that run it.
_EVIDENCE = ["rso/binding/binding.py", "rso/slice001/evidence.py", "rso/slice001/receipt.py"]
SOURCES = {"CALIBRATION": _RULERS, "RETENTION": _RULERS, "G-BIND": _EVIDENCE, "G-INV": _EVIDENCE,
           "G-RECOMP": ["rso/slice001/checker.py"] + _EVIDENCE}
ENTRY = {"CALIBRATION": "rso/slice001/rulers.py", "RETENTION": "rso/slice001/rulers.py",
         "G-BIND": "rso/slice001/evidence.py", "G-INV": "rso/slice001/evidence.py",
         "G-RECOMP": "rso/slice001/checker.py"}


class VersionError(RuntimeError):
    pass


def lf_bytes(path, root=REPO_ROOT):
    with open(os.path.join(root, *path.split("/")), "rb") as f:
        return f.read().replace(b"\r\n", b"\n")


def committed_blob(path, commit, root=REPO_ROOT):
    """LF bytes of <path> at <commit> (git show)."""
    r = subprocess.run(["git", "show", "%s:%s" % (commit, path)], cwd=root, capture_output=True, timeout=60)
    if r.returncode != 0:
        raise VersionError("%s not present at %s" % (path, commit))
    return r.stdout.replace(b"\r\n", b"\n")


def instrument_version(instrument, commit=PINNED, root=REPO_ROOT):
    """[CodeRef] of the instrument at `commit`; refuses if a working file differs from its blob there."""
    out = []
    for path in SOURCES[instrument]:
        if committed_blob(path, commit, root) != lf_bytes(path, root):
            raise VersionError("%s differs from its blob at %s: a new version needs a new record" % (path, commit[:12]))
        out.append(AD.file_code_ref(path, commit, root))
    return out


_IMPORT = re.compile(r"^\s*from rso\.(slice001|binding)(?:\.(\w+))? import (\w+)", re.M)


def slice_imports(path, root=REPO_ROOT, seen=None):
    """Every rso/slice001 and rso/binding module file `path` imports, transitively (top-level and function-level
    imports)."""
    seen = set() if seen is None else seen
    for top, pkg, name in _IMPORT.findall(lf_bytes(path, root).decode("utf-8")):
        dep = "rso/%s/%s%s.py" % (top, pkg + "/" if pkg else "", name)
        if dep not in seen and os.path.isfile(os.path.join(root, *dep.split("/"))):
            seen.add(dep)
            slice_imports(dep, root, seen)
    return seen
