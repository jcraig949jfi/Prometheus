"""Verify the NPE 1% production agreement sample BEFORE any read of its content (GO_FINAL v2 + addendum 2).

The manifest is SAMPLE_MANIFEST_CONTENT.json from the owner's commit 81895e729 (sha256 LF e1584484...), read from git, not from
the transfer. Every expected file must be present, and its gz sha256 AND its uncompressed sha256 must match. The script prints
hashes and counts only, never content.
    python -m archaeon.attribution.probes.npe_sample_verify DIR
"""
import gzip
import hashlib
import json
import os
import subprocess
import sys

REF = "81895e729:roles/Nestor/campaigns/ancestry-replay-2026-09-28/exports/SAMPLE_MANIFEST_CONTENT.json"
PIN = "e1584484bb77045eccf9091373b4f056240299c7e23d767391e9219310dc8c93"


def main(d):
    raw = subprocess.check_output(["git", "show", REF])
    assert hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest() == PIN, "manifest does not match the pinned hash"
    files = json.loads(raw)["files"]
    ok = True; n = 0
    for name, e in sorted(files.items()):
        p = os.path.join(d, name)
        if not os.path.exists(p):
            print("MISSING", name); ok = False; continue
        b = open(p, "rb").read()
        g = hashlib.sha256(b).hexdigest() == e["gz_sha256"]
        u = gzip.decompress(b)
        c = hashlib.sha256(u).hexdigest() == e["uncompressed_sha256"]
        r = u.count(b"\n") == e["records"]
        n += e["records"]
        print("%-4s gz=%s content=%s records=%s %s" % ("OK" if g and c and r else "BAD", g, c, r, name))
        ok &= g and c and r
    extra = sorted(set(os.listdir(d)) - set(files))
    if extra: print("EXTRA (ignored, not read):", extra)
    print("SAMPLE VERIFIED: %s (%d files, %d records)" % (ok, len(files), n))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
