"""Read-only access to the owner's frozen C4 artifacts (C-019-T040). Nothing is copied into roles/Ananke/.

Every artifact is read with `git show <OWNER_SHA>:<path>` and refused unless its git blob id equals the pinned one, so
a moved branch or an edited file cannot change what this evaluator was qualified against. Populations
(pops_C4T.tar, pops_C4D.tar, pops_C4L.tar) and any C5T output are NOT on the allow-list: owner consent is pending
(comms #2249); `load` refuses them by construction.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess

OWNER_BRANCH = "origin/ananke/p2b-2026-10-05"
OWNER_SHA = "f58362c5e3f3ca111c96217568f01fdc8babb398"
C4 = "roles/Ananke/pte/c4/"
PINNED = {                                    # path -> git blob id at OWNER_SHA
    C4 + "admission_R4.json": "2e4a893af8194eaacb3753aca3ebf1107d59aea7",
    C4 + "PLAN_C4_T.json": "c4c53b91fc17e188f3ce261a50e7f51b36ee357e",
    C4 + "LIBRARY_C4.json": "1f983e3606bbc2d58f1432b3ea66b3bb4c4305c3",
    C4 + "DLIB_C4.json": "31732c35b164a3d0a1a3aa5fdafba33d211f1769",
    C4 + "ASSAY_C4D.json": "522ac744d5ea5ccb056aa6de4e9db8b2b1b6c756",
    C4 + "REDUCE_C4D.json": "32d1cc3c899e247cd59ab58d02e16ef38db954ed",
}
FORBIDDEN_MARKERS = ("pops_", "c5t_production", "C5T_production", "rows_C5T")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


class OwnerArtifactError(RuntimeError):
    pass


def _git(*args) -> bytes:
    return subprocess.run(["git", "-C", ROOT, *args], check=True, capture_output=True).stdout


def load(path: str):
    if any(m in path for m in FORBIDDEN_MARKERS):
        raise OwnerArtifactError(f"REFUSED: {path} is a population / C5T artifact (owner consent pending)")
    if path not in PINNED:
        raise OwnerArtifactError(f"REFUSED: {path} is not a pinned artifact")
    data = _git("show", f"{OWNER_SHA}:{path}")
    blob = hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()       # git's blob id of the bytes received
    if blob != PINNED[path]:
        raise OwnerArtifactError(f"REFUSED: {path} content hashes to blob {blob} != pinned {PINNED[path]}")
    return json.loads(data.decode())


def cells() -> list:
    """The four C4 FLIP cells (physics at the cell's base representation, env, cell_key)."""
    return load(C4 + "PLAN_C4_T.json")["cells"]


def admission() -> dict:
    return load(C4 + "admission_R4.json")


def library() -> list:
    return load(C4 + "LIBRARY_C4.json")["modules"]


def dlib() -> dict:
    return load(C4 + "DLIB_C4.json")
