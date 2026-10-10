"""Read-only access to the FABLE-5.1 p1_slice prototype (docs/phase3/design/FABLE-5.1/prototype/p1_slice/).

C-013-T010 (Argus). The prototype is another lane's code and is used READ ONLY: this shim puts its directory on
sys.path and redirects numba's on-disk cache away from it (the prototype's kernels are @njit(cache=True), which would
otherwise write __pycache__ files into the prototype directory). Nothing here edits, copies or patches a prototype
file. PROTO_SHA256 pins the exact LF blobs the harness was built and frozen against; verify_prototype() refuses to
run against anything else.
"""
import hashlib
import os
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
PROTO_DIR = ROOT / "docs" / "phase3" / "design" / "FABLE-5.1" / "prototype" / "p1_slice"

os.environ.setdefault("NUMBA_CACHE_DIR", str(pathlib.Path(tempfile.gettempdir()) / "argus_rso_reach_numba_cache"))
if str(PROTO_DIR) not in sys.path:
    sys.path.insert(0, str(PROTO_DIR))

# sha256 of the LF-normalised blobs at base 9b1893d6f (the prototype files the harness executes).
PROTO_SHA256 = {
    "wm_mini.py": "12b342d0602bf311359c5dc266e2c4a112af1582b45e8d9a3da75c9893462d8c",
    "organisms.py": "305ba50a7826c8b72068d9e6583d194fec73e81187580539fe186d120d9b872e",
    "rulers.py": "d9876f05b1ea9142e3d43886fb9b86823b5078c012e90b60deb4397e5498f4b4",
    "reach.py": "3f0a99d5f4c26c35fecbf168ec2638346cda00d4831704a516b34909187b32cf",
    "oracle.py": "6e00e2d0033365f5990f928dcf56c33a91c4932d23711b5a0eebfc2fc904c240",
}

import wm_mini as wm          # noqa: E402
import organisms as org       # noqa: E402
import rulers as ru           # noqa: E402
import oracle                 # noqa: E402


def blob_sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def verify_prototype():
    bad = {name: blob_sha256(PROTO_DIR / name) for name in PROTO_SHA256
           if blob_sha256(PROTO_DIR / name) != PROTO_SHA256[name]}
    if bad:
        raise RuntimeError("prototype files differ from the frozen pins: %s" % sorted(bad))
    return True
