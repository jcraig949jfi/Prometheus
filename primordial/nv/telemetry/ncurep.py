"""Q2e: read an Nsight Compute .ncu-rep with NVIDIA's bundled ncu_report and judge whether counter metrics filled.

dump() needs the vendor pyd, so it runs in nv-venv-q as a script:
  nv-venv-q/python primordial/nv/telemetry/ncurep.py <report.ncu-rep> <out.json>
counter_filled()/judge() are pure and run anywhere (the verdict is code over the dump).
"""
from __future__ import annotations

import json
import re
import sys

NCU_PY = r"C:\Users\jcrai\lab\ncu-user\v2025.2\pkg\Library\nsight-compute\2025.2.1\extras\python"
COUNTER = re.compile(r"^(gpu__time_duration\.|[a-z0-9]+__cycles_elapsed\.|.*throughput)")


def dump(report: str, max_inst: int = 4) -> list[dict]:
    sys.path.insert(0, NCU_PY)
    import ncu_report as n
    c = n.load_report(report)
    out = []
    for ri in range(c.num_ranges()):
        r = c.range_by_idx(ri)
        for k in range(r.num_actions()):
            a = r.action_by_idx(k)
            metrics = {}
            for m in a.metric_names():
                if m.startswith("device__attribute"):
                    continue
                x = a.metric_by_name(m)
                vals = []
                for i in range(min(x.num_instances(), max_inst)):
                    try:
                        vals.append(x.as_double(i))
                    except Exception:
                        vals.append(None)
                metrics[m] = [x.num_instances(), vals]
            out.append({"range": ri, "kernel": a.name(a.NameBase_DEMANGLED)[:200], "metrics": metrics})
    return out


def counter_filled(kernels: list[dict]) -> list[tuple]:
    """(kernel, metric, first value) for every counter metric with >= 1 nonzero instance."""
    hits = []
    for kr in kernels:
        for m, (n, vals) in kr["metrics"].items():
            if COUNTER.match(m) and n > 0 and any(v for v in vals if v is not None):
                hits.append((kr["kernel"][:60], m, next(v for v in vals if v)))
    return hits


def judge(kernels: list[dict]) -> str:
    return "PASS" if counter_filled(kernels) else ("BOUND" if kernels else "NO_KERNELS")


if __name__ == "__main__":
    with open(sys.argv[2], "w", encoding="utf-8") as fh:
        json.dump(dump(sys.argv[1]), fh)
