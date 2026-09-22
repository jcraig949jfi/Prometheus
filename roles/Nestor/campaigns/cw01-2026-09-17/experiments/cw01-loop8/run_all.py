"""Run cycle 8's frozen ten plus P-J01's mandated companions (P-J04 forensics, P-J05 genealogy) in dependency
order; P-J01 first (P-J02 / P-J03 / P-J04 / P-J05 / P-J06 / P-J07 / P-J09 read from it or from P-J02)."""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ARCH = HERE.parent / "cw01-arch4"
ORDER = [(ARCH, "P-J01"), (ARCH, "P-J05"), (ARCH, "P-J02"), (ARCH, "P-J08"), (ARCH, "P-J07"), (ARCH, "P-J04"), (ARCH, "P-J09"), (ARCH, "P-J03"), (ARCH, "P-J06"),
         (HERE, "P-D08"), (HERE, "P-A02"), (HERE, "P-C05")]


def main(only=None):
    status = json.loads((HERE / "RUN_STATUS.json").read_text(encoding="utf-8")) if (HERE / "RUN_STATUS.json").exists() else {}
    for base, pid in ORDER:
        if only and pid not in only:
            continue
        d = base / pid
        script = next(d.glob("run_*.py"))
        if (d / "run.log").exists():
            (d / "run.log").rename(d / ("run_prev_%s.log" % time.strftime("%H%M%S")))
        t0 = time.time()
        with (d / "run.log").open("w", encoding="utf-8") as fh:
            rc = subprocess.call([sys.executable, str(script)], stdout=fh, stderr=subprocess.STDOUT, cwd=str(d))
        status[pid] = {"rc": rc, "wall_s": round(time.time() - t0, 1), "result_written": (d / "RESULT.json").exists()}
        print("%s rc=%d %.0f s result=%s" % (pid, rc, status[pid]["wall_s"], status[pid]["result_written"]), flush=True)
        (HERE / "RUN_STATUS.json").write_text(json.dumps(status, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main(set(sys.argv[1:]) or None)
