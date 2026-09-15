"""Q1: capture smoke test for N2 -- can the installed Nsight tools profile on this Blackwell host?

Probes (each a subprocess under a timeout; stdout/stderr/exit are kept verbatim in the row):
  control_torch       torch CUDA matmul, no profiler                -> the target itself works
  nsys_trivial        nsys profile -t none -s none on `cmd /c echo` -> is nsys usable at all (GPU-free)
  nsys_cuda_torch     nsys profile -t cuda,nvtx on the torch target -> CUDA trace on cc 12.0
  ncu_torch           ncu on the torch target                        -> Nsight Compute on cc 12.0
  cupti_torch         torch.profiler CUDA activity (bundled CUPTI)   -> the no-Nsight fallback
The B6 fused rollout is a numba CPU kernel with no CUDA context: ncu has nothing to attach to,
and nsys's CPU-side tracing is admin-gated on Windows (see nsys_trivial), so it is not probed here.

classify() turns a probe result into a verdict by code, from exit code and tool output only.

usage: python -m primordial.nv.telemetry.smoke --out primordial/ledger/rows/Q/Q1-capture-smoke.jsonl
"""
from __future__ import annotations

import argparse
import os
import pathlib
import platform
import shutil
import subprocess
import sys
import tempfile

NV = pathlib.Path(r"C:\Program Files\NVIDIA Corporation")
NSYS = NV / "Nsight Systems 2024.4.2" / "target-windows-x64" / "nsys.exe"
NCU = NV / "Nsight Compute 2024.3.0" / "target" / "windows-desktop-win7-x64" / "ncu.exe"
REPORTS = pathlib.Path(r"C:\Users\jcrai\lab\pm-data\nv-telemetry")

TORCH_TARGET = ("import torch; torch.set_num_threads(1); x = torch.randn(512, 512, device='cuda'); "
                "print('cc', torch.cuda.get_device_capability(), float((x @ x).sum()))")
CUPTI_TARGET = ("import torch\nfrom torch.profiler import profile, ProfilerActivity\ntorch.set_num_threads(1)\n"
                "w = torch.randn(256, 64)\n"
                "with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]) as p:\n"
                "    y = (w.cuda() @ w.cuda().T).relu().sum(1).cpu(); torch.cuda.synchronize()\n"
                "n = sum(1 for e in p.events() if e.device_type.name == 'CUDA')\n"
                "print('cuda_events', n)\n")

# first tool versions that name Blackwell support in NVIDIA's release notes (checked 2026-09-14)
FIRST_BLACKWELL = {"ncu": "2024.4 ('Added support for the Blackwell architecture.')",
                   "nsys": "not named in release notes; the 2024.4.2 failure here is admin-scoped, not GPU-scoped"}

VERDICTS = ("ok", "refused_admin", "perm_gpu_counters", "driver_incompatible", "cuda_modules_failed", "cupti_invalid_device", "target_crashed",
            "timeout", "tool_missing", "failed")


def classify(probe: str, rc: int | None, out: str, err: str) -> str:
    """Verdict from exit code and tool text only."""
    text = f"{out}\n{err}"
    if rc is None:
        return "timeout"
    if rc == 127 or "tool_missing" in text:
        return "tool_missing"
    if "requires administrator privileges" in text and rc != 0:
        return "refused_admin"
    if "ERR_NVGPUCTRPERM" in text:
        return "perm_gpu_counters"
    if "Cuda driver is not compatible with Nsight Compute" in text:
        return "driver_incompatible"
    if "Failed to load Nsight Compute CUDA modules" in text:
        return "cuda_modules_failed"
    if "CUPTI_ERROR_INVALID_DEVICE" in text:
        return "cupti_invalid_device"
    if rc in (3221225477, -1073741819, 139) or "error code (3221225477)" in text:
        return "target_crashed"
    if probe == "cupti_torch":
        for line in out.splitlines():
            if line.startswith("cuda_events"):
                return "ok" if int(line.split()[1]) > 0 else "failed"
        return "failed"
    return "ok" if rc == 0 else "failed"


REPORT_EXTS = (".ncu", ".ncu-rep")                             # ncu 2024.x writes .ncu, 2025.x writes .ncu-rep (Q2d)


def report_ok(files) -> bool:
    """An ncu capture counts only if a report file exists (rc 0 alone is not a capture)."""
    return any(str(f).endswith(REPORT_EXTS) for f in files)


def judge_capture(rows: list[dict]) -> str:
    """Q2c/Q2d predicate by code: PASS iff control_torch ok AND ncu_torch rc 0 with no refusal text AND a report."""
    by = {r.get("probe"): r for r in rows}
    c, n = by.get("control_torch"), by.get("ncu_torch")
    if not c or not n or classify("control_torch", c["rc"], c["stdout"], c["stderr"]) != "ok":
        return "INVALID"
    v = classify("ncu_torch", n["rc"], n["stdout"], n["stderr"])
    if v == "ok" and report_ok(n["report_files"]):
        return "PASS"
    return "REFUSAL:" + v


def _run(cmd, cwd, timeout, env=None):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        return None, e.stdout or "", e.stderr or ""
    except FileNotFoundError as e:
        return 127, "", f"tool_missing: {e}"


def probes(py: str, work: pathlib.Path, ncu: pathlib.Path = NCU, ncu_set: str = ""):
    return {
        "control_torch": [py, "-c", TORCH_TARGET],
        "nsys_trivial": [str(NSYS), "profile", "-t", "none", "-s", "none", "--cpuctxsw=none",
                         "-o", str(work / "nsys_trivial"), "-f", "true", "cmd.exe", "/c", "echo", "hi"],
        "nsys_cuda_torch": [str(NSYS), "profile", "-t", "cuda,nvtx", "-s", "none", "--cpuctxsw=none",
                            "-o", str(work / "nsys_cuda"), "-f", "true", py, "-c", TORCH_TARGET],
        "ncu_torch": [str(ncu), *(["--set", ncu_set] if ncu_set else []), "-o", str(work / "ncu_torch"), "-f", py, "-c",
                      TORCH_TARGET],
        "cupti_torch": [py, "-c", CUPTI_TARGET],
    }


def tool_version(exe: pathlib.Path) -> str:
    rc, out, err = _run([str(exe), "--version"], None, 60)
    lines = [x for x in (out + err).splitlines() if "ersion" in x]
    return lines[0].strip() if lines else f"rc={rc}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--py", default=sys.executable)
    ap.add_argument("--timeout", type=float, default=150)
    ap.add_argument("--only", default="")
    ap.add_argument("--ncu", default=str(NCU))
    ap.add_argument("--exp", default="Q1-capture-smoke")
    ap.add_argument("--set", default="", help="ncu section set (Q2e: detailed)")
    a = ap.parse_args(argv)
    from primordial.fabric.rows import RowWriter
    env = dict(os.environ, OMP_NUM_THREADS="1", NUMBA_NUM_THREADS="1")
    work = pathlib.Path(tempfile.mkdtemp(prefix="q1_"))
    host = {"os": platform.platform(), "nsys": tool_version(NSYS), "ncu": tool_version(pathlib.Path(a.ncu)), "ncu_path": a.ncu,
            "gpu": _run(["nvidia-smi", "--query-gpu=name,compute_cap,driver_version", "--format=csv,noheader"],
                        None, 60)[1].strip(),
            "first_blackwell": FIRST_BLACKWELL}
    only = set(a.only.split(",")) - {""}
    with RowWriter(a.out, a.exp, commit_every_s=3600) as w:
        for name, cmd in probes(a.py, work, pathlib.Path(a.ncu), a.set).items():
            if only and name not in only:
                continue
            rc, out, err = _run(cmd, work, a.timeout, env)
            v = classify(name, rc, out, err)
            files = sorted(p.name for p in work.iterdir() if p.name.startswith(name.split("_")[0]))
            if name == "ncu_torch" and v == "ok" and not report_ok(files):
                v = "failed"                                   # PASS needs the report file, not just rc 0
            if files:
                keep = REPORTS                                 # binary reports stay out of git
                keep.mkdir(parents=True, exist_ok=True)
                for f in files:
                    shutil.copy2(work / f, keep / f"{a.exp}-{f}")
            status = "control" if name == "control_torch" else "record"
            w.write({"status": status, "probe": name, "verdict": v, "rc": rc, "cmd": cmd,
                     "stdout": out[-2000:], "stderr": err[-2000:], "report_files": files, "host": host})
            print(f"{name:<16} rc={rc} verdict={v} files={files}", flush=True)
    shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
