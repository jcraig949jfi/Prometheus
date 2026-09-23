"""Run the frozen ten sequentially, cheapest first; each driver is independent and writes its
own PREREG/RESULT; a failure in one does not stop the others (recorded as FAILED)."""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ORDER = ["P-B05", "P-A11", "P-B03", "P-B09", "P-A10", "P-A07", "P-A08", "P-A01", "P-A04"]   # P-B04 ran synchronously first


def main():
    status = {}
    for pid in ORDER:
        d = HERE / pid
        script = next(d.glob("run_*.py"))
        t0 = time.time()
        log = d / "run.log"
        with log.open("w", encoding="utf-8") as fh:
            rc = subprocess.call([sys.executable, str(script)], stdout=fh, stderr=subprocess.STDOUT, cwd=str(d))
        status[pid] = {"rc": rc, "wall_s": round(time.time() - t0, 1), "result_written": (d / "RESULT.json").exists()}
        print("%s rc=%d %.0f s result=%s" % (pid, rc, status[pid]["wall_s"], status[pid]["result_written"]), flush=True)
        (HERE / "RUN_STATUS.json").write_text(json.dumps(status, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
