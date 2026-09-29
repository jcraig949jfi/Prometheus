"""v2 of the pre-read sample verification, implementing GO_FINAL addendum 5 EXACTLY. Addendum 5 was written BEFORE any candidate
copy was reported. Committed after Nestor #952 reported run-1 candidates whose gz bytes differ only in the gzip header mtime;
no sample content has been read.

PASS iff, for all 11 files named in the pinned manifest (81895e729, e1584484...), the UNCOMPRESSED sha256 and the record count
match. The gz sha256 is REPORTED, not required (addendum 2: the mtime header is not tracer output).
Also refused:
- a file without the gzip magic/deflate header (1f 8b 08);
- any extra file with the sample suffix.
v1 (npe_sample_verify.py) is unchanged and stays the strict check.
    python -m archaeon.attribution.probes.npe_sample_verify_v2 DIR
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
        hdr = b[:3] == b"\x1f\x8b\x08" and len(b) > 10
        n += e["records"]
        good = c and r and hdr
        print("%-4s content=%s records=%s gz_equal=%s(reported) header_ok=%s %s" % ("OK" if good else "BAD", c, r, g, hdr, name))
        ok &= good
    extra = sorted(f for f in os.listdir(d) if f.endswith(".sample1pct.jsonl.gz") and f not in files)
    if extra: print("EXTRA sample files present:", extra); ok = False
    print("SAMPLE VERIFIED (addendum 5 content identity): %s (%d files, %d records)" % (ok, len(files), n))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
