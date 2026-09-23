"""Run the frozen ARCH4 tranche sequentially; each driver is independent; failures are recorded."""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ORDER = ["P-C13", "P-C15", "P-C04", "P-C03", "P-C16"]     # P-C14 ran synchronously first (shim validation)


def main():
    status = {}
    for pid in ORDER:
        d = HERE / pid
        script = next(d.glob("run_*.py"))
        t0 = time.time()
        with (d / "run.log").open("w", encoding="utf-8") as fh:
            rc = subprocess.call([sys.executable, str(script)], stdout=fh, stderr=subprocess.STDOUT, cwd=str(d))
        status[pid] = {"rc": rc, "wall_s": round(time.time() - t0, 1), "result_written": (d / "RESULT.json").exists()}
        print("%s rc=%d %.0f s result=%s" % (pid, rc, status[pid]["wall_s"], status[pid]["result_written"]), flush=True)
        (HERE / "RUN_STATUS.json").write_text(json.dumps(status, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
