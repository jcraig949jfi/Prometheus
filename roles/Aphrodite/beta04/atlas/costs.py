"""COST PER TASK PER ARM at 1x (B = 5,000 charges), full budget (stop_on_hit=False), seeds 0 and 1, one process.
Writes atlas/calibration/COSTS.json. CPU seconds are process_time on M4/HARRY1 (Python 3.12, 1 thread), measured while
one other process of this lead was running (2-worker cap): treat as conservative.

  python -m atlas.costs          (from roles/Aphrodite/beta04)
"""
import json
import os
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
from tfs1.enum import Enumerator                 # noqa: E402

from . import arms as A                          # noqa: E402
from . import toys                               # noqa: E402
from .calibration import B, DESC, OUT, _load     # noqa: E402


def main():
    out = {"budget": B, "seeds": [0, 1], "toys": {}}
    for toy, (T, lib) in toys.all_toys().items():
        E = Enumerator(lib)
        ar = _load("%s_arms.json" % toy) or {}
        cal = ar.get("random_control_calibration", {})
        K3 = cal.get("C3", {}).get("K", 500)
        K2 = cal.get("C2", {}).get("K", 100)
        rows = {}
        for arm, desc in (("A-FRESH", None), ("A-CHAIN", None), ("B1-RETAIN", None), ("B2-DESCSEL", DESC),
                          ("B3-CELLADMIT", DESC), ("C3-RAND", "RAND:%d" % K3), ("C2-RAND", "RAND:%d" % K2)):
            cpu, units, probes, ver = [], [], [], []
            for sd in (0, 1):
                r = A.run_arm(T, lib, arm, sd, B, descriptor=desc, stop_on_hit=False, E=E, final_eval=False)
                cpu.append(r["cpu_s"])
                units.append(r["ledger"]["search"]["units_dev_expanded"])
                probes.append(r["ledger"]["search"]["probe_runs"])
                ver.append(r["ledger"]["certifier"]["verify_evals"])
            rows[arm] = {"cpu_s_per_run": round(sum(cpu) / 2, 3), "charges": B,
                         "charges_per_cpu_s": round(B / (sum(cpu) / 2)),
                         "units_dev_expanded_per_run": sum(units) // 2, "probe_runs_per_run": sum(probes) // 2,
                         "verify_evals_per_run": sum(ver) / 2}
        a = _load("%s_atlas.json" % toy) or {}
        q = _load("%s_qual.json" % toy) or {}
        out["toys"][toy] = {"arms": rows, "atlas_measurement_cpu_s": a.get("cpu_s_total"),
                            "descriptor_qualification_cpu_s": q.get("cpu_s"),
                            "arms_part_cpu_s(8 arms x 8 seeds + K calibration)": ar.get("cpu_s")}
        print(toy, {k: v["cpu_s_per_run"] for k, v in rows.items()}, flush=True)
    (OUT / "COSTS.json").write_text(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    t0 = time.process_time()
    main()
    print("cpu", round(time.process_time() - t0, 1))
