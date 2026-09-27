"""WTP-LM01 freeze record (G1, directive s13 "machine-readable frozen config/manifest").

record(freeze_commit) writes ensorain/lm01/FREEZE.json from the COMMITTED blobs of the freeze commit:
  freeze_commit (full SHA), and the sha256 (LF-normalised, i.e. the git blob bytes) of the prereg, its tables,
  FROZEN_SELECTION.json, margins_reduced_v2.json, every ensorain/lm01/*.py, and the governing constants.
verify() re-hashes the working tree and is called by the launcher before any campaign seed is derived. Any mismatch
means the frozen study is not the one being launched, and the launcher refuses."""
import hashlib
import json
import os
import subprocess

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(os.path.dirname(__file__), "FREEZE.json")
FILES = ["ensorain/PREREG_WTP_LM01.md", "ensorain/PREREG_WTP_LM01_TABLES.md", "ensorain/lm01/FROZEN_SELECTION.json",
         "ensorain/lm01/dev/margins_reduced_v2.json"]


def _code():
    out = subprocess.run(["git", "-C", REPO, "ls-files", "ensorain/lm01/*.py", "ensorain/wtp/*.py", "ensorain/wtp3/*.py"],
                         capture_output=True, text=True).stdout.split()
    return sorted(p for p in out if "/tests/" not in p)


def _blob(commit, path):
    return subprocess.run(["git", "-C", REPO, "show", f"{commit}:{path}"], capture_output=True).stdout


def _norm(b):
    return b.replace(b"\r\n", b"\n")


def record(freeze_commit):
    full = subprocess.run(["git", "-C", REPO, "rev-parse", freeze_commit], capture_output=True, text=True).stdout.strip()
    hashes = {p: hashlib.sha256(_norm(_blob(full, p))).hexdigest() for p in FILES + _code()}
    from .margins_reduce_v2 import DELTA, SENS
    from .campaign import RUNG_SCALE
    rec = dict(freeze_commit=full, files=hashes, DELTA=DELTA, SENSITIVITY=list(SENS), RUNG_SCALE=RUNG_SCALE,
               N_PER_STRATUM=48, launch_authority="OPERATOR ONLY (direct chat; ruling 2026-09-26 item 6)",
               launch_phrase="LAUNCH WTP-LM01 using frozen prereg <prefix of freeze_commit, 7-40 hex>")
    with open(OUT, "w") as f:
        json.dump(rec, f, indent=1)
    return rec


def verify():
    rec = json.load(open(OUT))
    bad = []
    for p, h in rec["files"].items():
        fp = os.path.join(REPO, p)
        if not os.path.exists(fp) or hashlib.sha256(_norm(open(fp, "rb").read())).hexdigest() != h:
            bad.append(p)
    return rec["freeze_commit"], bad
