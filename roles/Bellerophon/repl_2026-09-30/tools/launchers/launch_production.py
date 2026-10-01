"""E-BEL-REPL-01 production launcher (freeze 74f72e805; lease lse-4e19412ded95). 12 processes; each writes its own JSONL.
Chunks: arm x pair-range; 3 arms x 4 ranges of 25 pairs = 12 chunks. Resumable (the runner skips pairs already written)."""
import json, pathlib, subprocess, sys, time

WT = pathlib.Path(r"D:\Prometheus-worktrees\bellerophon-mwo-0001")
OUT = pathlib.Path(r"C:\Users\James\repl_2026-09-30\production"); OUT.mkdir(parents=True, exist_ok=True)
RUN = WT / "roles/Bellerophon/repl_2026-09-30/tools/repl_run.py"
head = subprocess.check_output(["git", "-C", str(WT), "rev-parse", "HEAD"], text=True).strip()
procs = []
for arm in ("ZERO", "P90", "P75"):
    for k in range(4):
        out = OUT / ("runs_%s_%d.jsonl" % (arm, k))
        p = subprocess.Popen([sys.executable, "-I", str(RUN), "--arm", arm, "--s0", str(25 * k), "--n", "25", "--out", str(out)],
                             cwd=str(WT), stdout=subprocess.DEVNULL, stderr=open(OUT / ("err_%s_%d.log" % (arm, k)), "w"))
        procs.append((arm, k, p))
(OUT / "LAUNCH.json").write_text(json.dumps({"head": head, "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                             "pids": [p.pid for _, _, p in procs]}, indent=1))
rc = [p.wait() for _, _, p in procs]
(OUT / "DONE.json").write_text(json.dumps({"finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "returncodes": rc}, indent=1))
