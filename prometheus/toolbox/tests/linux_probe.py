"""Second-platform probe WITHOUT pytest (overnight C144): on a host that has only a bare interpreter (WSL Linux
python3, no pytest, no numpy) execute random IRs on both paths and replay every committed receipts file.
Prints one JSON line. Run:  python3 -m prometheus.toolbox.tests.linux_probe [n_seeds]"""
from __future__ import annotations

import collections
import json
import pathlib
import platform
import sys
import tempfile


def main(n_seeds: int = 120) -> dict:
    # the fuzz generator imports pytest at module level; provide a stub when pytest is absent
    if "pytest" not in sys.modules:
        try:
            import pytest  # noqa: F401
        except ImportError:
            import types
            stub = types.ModuleType("pytest")
            stub.mark = types.SimpleNamespace(parametrize=lambda *a, **k: (lambda f: f), skipif=lambda *a, **k: (lambda f: f))
            stub.raises = None; stub.skip = lambda *a, **k: None; stub.approx = lambda x: x
            sys.modules["pytest"] = stub
    from prometheus.toolbox.tests.test_fuzz import random_experiment, REG
    from prometheus.toolbox.ir import Experiment
    from prometheus.toolbox.backends.local import execute, replay_file
    from prometheus.toolbox.receipt import read_all
    c = collections.Counter(); bad = 0
    with tempfile.TemporaryDirectory() as td:
        for seed in range(n_seeds):
            e = random_experiment(seed)
            if e.validate():
                c["invalid"] += 1; continue
            low = e.compile("local", REG)
            if not low.ok:
                c[low.status] += 1; continue
            eb = Experiment.from_dict(e.to_dict()); eb.budget = dict(eb.budget, batch=3)
            execute(low.job, pathlib.Path(td) / ("s%d.jsonl" % seed), REG); execute(eb.compile("local", REG).job, pathlib.Path(td) / ("b%d.jsonl" % seed), REG)
            key = lambda r: (r["arm"], json.dumps(r["sweep_point"], sort_keys=True), r["seed"])
            S = {key(r): r for r in read_all(pathlib.Path(td) / ("s%d.jsonl" % seed)) if r["arm"] != "SUMMARY"}
            B = {key(r): r for r in read_all(pathlib.Path(td) / ("b%d.jsonl" % seed)) if r["arm"] != "SUMMARY"}
            for k, r in S.items():
                c["runs"] += 1; c[B[k]["execution"]["reason"]] += 1
                if r["trace_hashes"] != B[k]["trace_hashes"] or r["science"] != B[k]["science"]:
                    bad += 1
        root = pathlib.Path(__file__).resolve().parents[1]
        div = 0; files = 0; compared = 0
        for f in sorted(list((root / "examples" / "receipts").rglob("*.jsonl")) + list((root / "playtests" / "receipts").rglob("*.jsonl"))):
            if f.name in ("archive.jsonl", "replay.jsonl") or "soak" in f.parts:
                continue
            if not any(r["arm"] == "SUMMARY" and r.get("experiment") for r in read_all(f)):
                continue
            out = replay_file(f, pathlib.Path(td) / ("rp%d.jsonl" % files)); files += 1; div += len(out["divergent"]); compared += out["runs_compared"]
    res = {"platform": platform.platform(), "python": sys.version.split()[0], "numpy": "numpy" in sys.modules or _has("numpy"),
           "fuzz": dict(c), "path_divergences": bad, "committed_files_replayed": files, "runs_compared": compared, "divergent_runs": div}
    print(json.dumps(res))
    return res


def _has(mod: str) -> bool:
    try:
        __import__(mod); return True
    except Exception:  # noqa: BLE001
        return False


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 120)
