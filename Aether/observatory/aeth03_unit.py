"""One portable Aether work unit: law + seed + origin slice + arm -> result.

Research block, Blocks F and G. A unit is the smallest schedulable piece of
the propagation assay: one law, one seed, a slice of that seed's origin
list, one perturbation arm. It is written to be run on any host with Python
and NumPy, from a checkout pinned to a commit, with no host paths.

The result file carries everything C-001's portable-Task record asks for:

  inputs        the canonical parameters, and their sha256 (the unit id is
                derived from them, so the same inputs always name the same
                unit, whoever runs it);
  code          sha256 of every Aether module the unit actually imported,
                computed over LF-normalised content (a Windows checkout has
                CRLF line endings and a Linux one LF, so raw-byte hashes of
                the SAME commit differ between hosts; the normalised hash
                does not);
  result        the per-origin summaries and horizon rows, and
                result_sha256 over their canonical JSON (host, wall time and
                resource figures are excluded, so equal science gives an
                equal hash on any host);
  legacy_sha256 the same hash with the post-ladder-2 "content" block
                removed, comparable with results recorded before that metric
                existed (the known-answer lane uses it);
  resources     wall seconds and peak resident memory where the OS reports it;
  host          platform, Python and NumPy versions, hostname.

It writes only its output file; cleanup of the working copy is the
executor's job and is recorded in the Attempt row.
"""

import argparse
import hashlib
import json
import os
import platform
import socket
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_AETHER = os.path.dirname(_HERE)
for _p in (_AETHER, os.path.join(_AETHER, "test", "reference")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from observatory import aeth03_longhorizon as LH         # noqa: E402
from observatory import aeth03_propagation as P          # noqa: E402

ARMS = {"off": "perturbation_off", "on": "perturbation_on"}


def canon(obj):
    """Canonical JSON bytes: normalised key types, sorted, no whitespace."""
    return json.dumps(json.loads(json.dumps(obj)), sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def lf_sha256(path):
    with open(path, "rb") as fh:
        data = fh.read().replace(b"\r\n", b"\n")
    return sha(data)


def unit_inputs(law, seed_index, arm, start, stop, n=128, warmup=1500, ticks=400,
                origins=32):
    return {"law": law, "seed_index": int(seed_index), "arm": arm,
            "slice": [int(start), int(stop)], "n": int(n), "warmup": int(warmup),
            "ticks": int(ticks), "origins_total": int(origins),
            "instrument": "aeth03_propagation.assay"}


def unit_id(inputs):
    return "%s-s%d-%s-%d_%d-%s" % (inputs["law"], inputs["seed_index"], inputs["arm"],
                                   inputs["slice"][0], inputs["slice"][1],
                                   sha(canon(inputs))[:10])


def science_block(inputs, runs, legacy=False):
    out = []
    for r in runs:
        summ = dict(r["summary"])
        if legacy:
            summ.pop("content", None)
        out.append({"summary": summ, "horizons": r["horizons"]})
    return {"inputs": inputs, "runs": out}


def peak_rss_mb():
    try:
        import resource                                  # POSIX
        kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return kb / 1024.0 if sys.platform != "darwin" else kb / (1024.0 * 1024.0)
    except ImportError:
        pass
    try:
        import ctypes
        import ctypes.wintypes as wt

        class PMC(ctypes.Structure):
            _fields_ = [("cb", wt.DWORD), ("PageFaultCount", wt.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t),
                        ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t),
                        ("PeakPagefileUsage", ctypes.c_size_t)]
        pmc = PMC()
        pmc.cb = ctypes.sizeof(PMC)
        # 64-bit handles: declare the types, or the pseudo-handle (-1) is
        # truncated and the call silently fills nothing (read 0.0 MB).
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        k32.GetCurrentProcess.restype = wt.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [wt.HANDLE, ctypes.POINTER(PMC), wt.DWORD]
        psapi.GetProcessMemoryInfo.restype = wt.BOOL
        if not psapi.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(pmc),
                                          pmc.cb):
            return None
        return pmc.PeakWorkingSetSize / (1024.0 * 1024.0)
    except Exception:                                    # noqa: BLE001
        return None


def code_hashes():
    out = {}
    for name, mod in sorted(sys.modules.items()):
        f = getattr(mod, "__file__", None) or ""
        if f and os.path.abspath(f).startswith(_AETHER) and f.endswith(".py"):
            out[os.path.relpath(f, _AETHER).replace(os.sep, "/")] = lf_sha256(f)
    return out


def longhorizon_inputs(law, seed_index, arm, n=256, warmup=1500, ticks=10000):
    return {"law": law, "seed_index": int(seed_index), "arm": arm, "n": int(n),
            "warmup": int(warmup), "ticks": int(ticks),
            "instrument": "aeth03_longhorizon.run"}


def run_unit(inputs):
    if inputs["instrument"] == "aeth03_longhorizon.run":
        return run_longhorizon_unit(inputs)
    t0 = time.time()
    res = P.assay(inputs["law"], inputs["n"], inputs["warmup"], inputs["ticks"],
                  inputs["origins_total"], inputs["seed_index"],
                  origin_slice=tuple(inputs["slice"]), arms=(ARMS[inputs["arm"]],))
    runs = res["arms"][ARMS[inputs["arm"]]]
    wall = time.time() - t0
    sci = science_block(inputs, runs)
    legacy = science_block(inputs, runs, legacy=True)
    return {
        "unit_id": unit_id(inputs),
        "inputs": inputs,
        "inputs_sha256": sha(canon(inputs)),
        "semantics_id": res["semantics_id"],
        "result_sha256": sha(canon(sci)),
        "legacy_sha256": sha(canon(legacy)),
        "runs": runs,
        "code_sha256_lf": code_hashes(),
        "resources": {"wall_seconds": wall, "peak_rss_mb": peak_rss_mb()},
        "host": {"platform": platform.platform(), "python": platform.python_version(),
                 "numpy": np.__version__, "hostname": socket.gethostname()},
        "locality_violations": sum(r["summary"]["locality_violations"] for r in runs),
    }


def run_longhorizon_unit(inputs):
    from observatory import aeth03_scouts as S
    t0 = time.time()
    res = LH.run(inputs["law"], inputs["n"], inputs["warmup"], inputs["ticks"],
                 inputs["seed_index"], S.MUT_ON if inputs["arm"] == "on" else 0,
                 progress_every=1000)
    wall = time.time() - t0
    sci = {"inputs": inputs, "origins": res["origins"]}
    uid = "LH-%s-s%d-%s-%d-%s" % (inputs["law"], inputs["seed_index"], inputs["arm"],
                                  inputs["ticks"], sha(canon(inputs))[:10])
    return {
        "unit_id": uid, "inputs": inputs, "inputs_sha256": sha(canon(inputs)),
        "result_sha256": sha(canon(sci)), "legacy_sha256": None,
        "origins": res["origins"],
        "code_sha256_lf": code_hashes(),
        "resources": {"wall_seconds": wall, "peak_rss_mb": peak_rss_mb()},
        "host": {"platform": platform.platform(), "python": platform.python_version(),
                 "numpy": np.__version__, "hostname": socket.gethostname()},
        "locality_violations": res["locality_violations"],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--instrument", choices=("assay", "longhorizon"), default="assay")
    ap.add_argument("--law", required=True)
    ap.add_argument("--seed-index", type=int, required=True)
    ap.add_argument("--arm", choices=("off", "on"), required=True)
    ap.add_argument("--slice", default="0:32", help="start:stop into the 32-origin list")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--warmup", type=int, default=1500)
    ap.add_argument("--ticks", type=int, default=None)
    ap.add_argument("--origins", type=int, default=32)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.instrument == "longhorizon":
        inputs = longhorizon_inputs(a.law, a.seed_index, a.arm, a.n or 256, a.warmup,
                                    a.ticks or 10000)
    else:
        start, stop = (int(x) for x in a.slice.split(":"))
        inputs = unit_inputs(a.law, a.seed_index, a.arm, start, stop, a.n or 128,
                             a.warmup, a.ticks or 400, a.origins)
    res = run_unit(inputs)
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({k: res[k] for k in ("unit_id", "result_sha256", "legacy_sha256",
                                          "resources", "locality_violations")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
