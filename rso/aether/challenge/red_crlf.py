"""C-018-T040 S2 follow-up: the builder's red harness (rso/aether/red/run_red.py) matches four of its 21 edits with an
embedded '\n'; on a CRLF checkout (this worktree: core.autocrlf) they never match and are reported EDIT_NOT_UNIQUE.
Re-apply exactly those edits with the file's own line ending, run the frozen suite, restore byte for byte.

    python -B -m rso.aether.challenge.red_crlf <scratch>
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

from rso.aether.red.run_red import EDITS, purge
from rso.registry.registry import ROOT

SUITE = [sys.executable, "-B", "-m", "unittest", "rso.aether.tests.test_adapter"]


def main(scratch):
    rows = []
    for i, (f, old, new) in enumerate(EDITS):
        if "\n" not in old:
            continue
        path = os.path.join(ROOT, "rso", "aether", f)
        raw = open(path, "rb").read()
        sha = hashlib.sha256(raw).hexdigest()
        src = raw.decode("utf-8")
        crlf = "\r\n" in src
        o, nw = (old.replace("\n", "\r\n"), new.replace("\n", "\r\n")) if crlf else (old, new)
        if src.count(o) != 1:
            rows.append({"edit": i, "file": f, "result": "EDIT_NOT_UNIQUE_EVEN_WITH_CRLF", "count": src.count(o)})
            continue
        try:
            open(path, "wb").write(src.replace(o, nw).encode("utf-8"))
            purge()
            p = subprocess.run(SUITE, cwd=ROOT, capture_output=True, text=True, timeout=500)
            tail = (p.stderr or p.stdout).strip().splitlines()
        finally:
            open(path, "wb").write(raw)
        assert hashlib.sha256(open(path, "rb").read()).hexdigest() == sha
        rows.append({"edit": i, "file": f, "old": old.strip(), "crlf_file": crlf, "returncode": p.returncode,
                     "result": "KILLED" if p.returncode != 0 else "SURVIVED", "tail": tail[-1] if tail else ""})
        print(i, f, rows[-1]["result"], file=sys.stderr, flush=True)
    purge()
    with open(os.path.join(scratch, "red_crlf.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(rows, indent=1) + "\n")
    print(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
