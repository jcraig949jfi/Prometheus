"""Fly ANOTHER seat's GPU conformance suite, unmodified: Ananke's PTE engine.

Iteration 5 of the RunPod ladder asks whether the platform carries work
that is not Aether's. This module is a wrapper and nothing else:

  1. download Ananke's engine and tests from a PINNED commit of the public
     repository, and verify every file's sha256 against a manifest built
     locally with `git show <commit>:<path>` before anything runs;
  2. run the owner's own conformance tests with pytest, unchanged -- the
     GPU engine against the independent CPU oracle, bit-identical, plus the
     CUDA-graph and checkpoint/resume tests that SKIP on a machine without
     CUDA (Ananke's DESIGN.md claims exact replay "on RunPod hardware too";
     these tests have only ever run on the owner's Windows GPU host);
  3. time the owner's own randomly generated physics at larger batch sizes,
     eager vs CUDA-graph, as a WRAPPER-SIDE measurement relevant to the
     owner's open item ANANKE-09 (throughput is launch-bound on Windows).
     It is labelled as such and is not Ananke's benchmark.

Imports nothing from Aether or from the platform. Engineering only: no
Ananke science is run and no scientific claim can come from this flight.
"""

import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request

FORBIDDEN = ("RUNPOD_API_KEY", "RUNPOD_API_TOKEN", "RUNPOD_TOKEN")
ORIGIN = time.monotonic()
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = "https://raw.githubusercontent.com/jcraig949jfi/Prometheus/%s/%s"


def emit(path, kind, **fields):
    rec = {"kind": kind,
           "t_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "t_elapsed_s": round(time.monotonic() - ORIGIN, 3)}
    rec.update(fields)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
        fh.flush()


def fetch_pinned(manifest, dest, tel):
    """Download every file at the pinned commit; refuse on any mismatch."""
    commit = manifest["commit"]
    for rel, want in sorted(manifest["files"].items()):
        req = urllib.request.Request(RAW % (commit, rel),
                                     headers={"User-Agent": "prometheus-gpu-module/1"})
        with urllib.request.urlopen(req, timeout=60) as r:
            blob = r.read()
        got = hashlib.sha256(blob).hexdigest()
        if got != want:
            raise SystemExit("PINNED FILE MISMATCH %s: %s != %s" % (rel, got, want))
        path = os.path.join(dest, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(blob)
    emit(tel, "progress", stage="fetched", files=len(manifest["files"]),
         commit=commit)


def time_engine(src, tel):
    """Wrapper-side timing of the owner's engine on the owner's own configs."""
    sys.path.insert(0, src)
    import numpy as np
    import torch
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ananke_tc", os.path.join(src, "prometheus", "ananke", "tests",
                                  "test_conformance.py"))
    tc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tc)
    from prometheus.ananke.engine import World
    rows = []
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    for seed in (0, 1, 2, 3):
        ph = tc.random_physics(seed)
        for B in (256, 2048):
            T = 200
            gen, ws, sense = tc.random_inputs(ph, B, T, seed)
            for graph in (False, True):
                if graph and dev != "cuda":
                    continue
                w = World(ph, gen, ws, device=dev,
                          schedule=tc.dense_schedule(sense, B, ph.n_sites))
                w.run(5, graph=graph)                 # warm up / capture
                if dev == "cuda":
                    torch.cuda.synchronize()
                t0 = time.perf_counter()
                w.run(T - 5, graph=graph)
                if dev == "cuda":
                    torch.cuda.synchronize()
                dt = time.perf_counter() - t0
                su = B * ph.n_sites * (T - 5)
                rows.append({"seed": seed, "topology": ph.topology,
                             "n_sites": ph.n_sites, "B": B, "ticks": T - 5,
                             "graph": graph, "seconds": round(dt, 4),
                             "site_updates_per_s": round(su / dt, 1)})
                emit(tel, "progress", stage="timing", **rows[-1])
    return {"device": dev, "rows": rows,
            "label": "WRAPPER-SIDE timing of Ananke's World on Ananke's own "
                     "random_physics configs (test_conformance.py); not "
                     "Ananke's benchmark, not the C1 configuration"}


def main():
    for name in FORBIDDEN:
        if os.environ.get(name):
            raise SystemExit("a provider credential is readable; refusing")
    art = os.environ.get("PROMETHEUS_ARTIFACT_DIR", os.path.join(HERE, "out"))
    os.makedirs(art, exist_ok=True)
    tel = os.environ.get("PROMETHEUS_TELEMETRY_PATH",
                         os.path.join(art, "telemetry.jsonl"))
    with open(os.path.join(HERE, "ananke_files.json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    import platform
    versions = {"python": platform.python_version()}
    for mod in ("torch", "numpy", "pytest"):
        try:
            versions[mod] = __import__(mod).__version__
        except Exception as exc:
            versions[mod] = "unavailable: %s" % exc
    try:
        import torch
        versions["cuda_available"] = torch.cuda.is_available()
        versions["gpu"] = (torch.cuda.get_device_name(0)
                           if torch.cuda.is_available() else None)
        versions["torch_cuda"] = torch.version.cuda
    except Exception:
        pass
    emit(tel, "start", run_id=os.environ.get("PROMETHEUS_RUN_ID"),
         owner_seat="Ananke", commit=manifest["commit"], versions=versions)

    src = os.path.join(HERE, "src")
    fetch_pinned(manifest, src, tel)

    junit = os.path.join(art, "pytest_junit.xml")
    log_path = os.path.join(art, "pytest.log")
    t0 = time.monotonic()
    tests = [os.path.join(src, *p.split("/")) for p in manifest["run_tests"]]
    with open(log_path, "w", encoding="utf-8") as log:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-rs", "-p", "no:cacheprovider",
             "--junitxml", junit] + tests,
            cwd=src, stdout=log, stderr=subprocess.STDOUT,
            env=dict(os.environ, PYTHONPATH=src))
    pytest_s = time.monotonic() - t0
    with open(log_path, encoding="utf-8") as fh:
        tail = fh.read().strip().splitlines()[-1:] or [""]
    emit(tel, "progress", stage="pytest", exit_code=proc.returncode,
         summary=tail[0], seconds=round(pytest_s, 1))

    timing = time_engine(src, tel)
    result = {"owner_seat": "Ananke", "commit": manifest["commit"],
              "files_verified": len(manifest["files"]),
              "tests": manifest["run_tests"],
              "pytest_exit_code": proc.returncode, "pytest_summary": tail[0],
              "pytest_seconds": round(pytest_s, 1), "versions": versions,
              "timing": timing,
              "scope": "engineering conformance only; no Ananke science"}
    with open(os.path.join(art, "result.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
    emit(tel, "end", status="ok" if proc.returncode == 0 else "tests_failed",
         elapsed_s=round(time.monotonic() - ORIGIN, 3))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
