"""Run cycle 2's frozen ten sequentially (ARCH4 grids live under cw01-arch4, the rest here)."""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ARCH = HERE.parent / "cw01-arch4"
ORDER = [(HERE, "P-D05"), (HERE, "P-D11"), (HERE, "P-B10"), (HERE, "P-B07"), (HERE, "P-D13"), (ARCH, "P-D01"), (ARCH, "P-D03"), (HERE, "P-D07"), (HERE, "P-D12")]   # P-D02 ran synchronously (validation)


def main():
    status = {}
    for base, pid in ORDER:
        d = base / pid
        script = next(d.glob("run_*.py"))
        t0 = time.time()
        with (d / "run.log").open("w", encoding="utf-8") as fh:
            rc = subprocess.call([sys.executable, str(script)], stdout=fh, stderr=subprocess.STDOUT, cwd=str(d))
        status[pid] = {"rc": rc, "wall_s": round(time.time() - t0, 1), "result_written": (d / "RESULT.json").exists()}
        print("%s rc=%d %.0f s result=%s" % (pid, rc, status[pid]["wall_s"], status[pid]["result_written"]), flush=True)
        (HERE / "RUN_STATUS.json").write_text(json.dumps(status, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
