"""Cycle-2 reruns after the main batch: P-D01 (bounded sampler, CW01-D075), P-D11 and P-D13 (growth
formula without world_e06's latent crash, CW01-D074). Sequential; failures recorded."""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ARCH = HERE.parent / "cw01-arch4"
ORDER = [(HERE, "P-D11"), (HERE, "P-D13"), (ARCH, "P-D01")]


def main():
    status = json.loads((HERE / "RUN_STATUS.json").read_text(encoding="utf-8")) if (HERE / "RUN_STATUS.json").exists() else {}
    for base, pid in ORDER:
        d = base / pid
        script = next(d.glob("run_*.py"))
        if (d / "run.log").exists():
            (d / "run.log").rename(d / ("run_crash_%s.log" % time.strftime("%H%M%S")))
        t0 = time.time()
        with (d / "run.log").open("w", encoding="utf-8") as fh:
            rc = subprocess.call([sys.executable, str(script)], stdout=fh, stderr=subprocess.STDOUT, cwd=str(d))
        status[pid] = {"rc": rc, "wall_s": round(time.time() - t0, 1), "result_written": (d / "RESULT.json").exists(), "rerun": True}
        print("%s rc=%d %.0f s result=%s" % (pid, rc, status[pid]["wall_s"], status[pid]["result_written"]), flush=True)
        (HERE / "RUN_STATUS.json").write_text(json.dumps(status, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
