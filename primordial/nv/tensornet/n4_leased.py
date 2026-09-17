"""Run one n4_timing side under the O5 GPU lease (Windows driver; the cutn side runs through wsl.exe).

The lease lives in Redis on the Windows host, so this process holds it (renewed) while the measured process
runs, then appends a {"kind": "lease"} row with the holder, token prefix and `lost` flag to the rows file.
A lost lease makes that side's speed INDETERMINATE.

usage: python -m primordial.nv.tensornet.n4_leased --side cutn|torch --out C:/Users/jcrai/lab/pm-data/T/x.jsonl
                                                   --git SHA [--wait 900] [--timeout 540] [--quick]
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[3]


def wsl_path(p) -> str:
    """Windows path -> /mnt/<drive>/...; parsed as a Windows path on any OS (tests run in WSL too)."""
    w = pathlib.PureWindowsPath(str(p))
    if not w.drive:
        return pathlib.PurePath(p).as_posix()
    return f"/mnt/{w.drive[0].lower()}{w.as_posix()[2:]}"


def command(side: str, out: pathlib.Path, git: str, lease: str, timeout: int, quick: bool,
            extra: list[str] | None = None) -> list[str]:
    args = ["--side", side, "--git", git, "--lease", lease] + (["--quick"] if quick else []) + (extra or [])
    if side == "torch":
        return [sys.executable, "-m", "primordial.nv.tensornet.n4_timing", *args, "--out", str(out)]
    tag = os.environ.get("PM_TAG", "")
    return ["wsl.exe", "-e", "bash", "-lc",
            f"cd {wsl_path(REPO)} && OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PM_TAG={tag} timeout {timeout} "
            f"~/lab/nv-venv-t/bin/python -m primordial.nv.tensornet.n4_timing {' '.join(args)} --out {wsl_path(out)}"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--side", required=True, choices=["cutn", "torch"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--git", required=True)
    ap.add_argument("--wait", type=float, default=900)
    ap.add_argument("--timeout", type=int, default=540)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--configs", default="")
    ap.add_argument("--min-b", type=int, default=0)
    a = ap.parse_args(argv)
    extra = (["--configs", a.configs] if a.configs else []) + (["--min-b", str(a.min_b)] if a.min_b else [])
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    from primordial.bus import bus      # Windows-side only (redis); WSL imports this module for tests
    t0 = time.time()
    with bus.gpu_lease(f"T N4-timing side={a.side}", ttl_s=600, wait_s=a.wait) as rec:
        waited = time.time() - t0
        lease = f"{rec['holder']}:{rec['token'][:8]}"
        rc = subprocess.run(command(a.side, out, a.git, lease, a.timeout, a.quick, extra), timeout=a.timeout + 60).returncode
        row = {"exp_id": "N4-cutensornet-vs-torch-bucket-timing", "status": "record", "kind": "lease",
               "side": a.side, "holder": rec["holder"], "token8": rec["token"][:8], "since": rec["since"],
               "released": round(time.time(), 3), "waited_s": round(waited, 1), "lost": bool(rec["lost"]), "rc": rc}
    with open(out, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(row) + "\n")
    print(json.dumps(row))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
