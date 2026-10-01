"""E-BEL-REPL-02 launcher (freeze 4d1a7c885; under held lease lse-4e19412ded95, same seat, disclosed)."""
import json, pathlib, subprocess, sys, time
WT = r"D:\Prometheus-worktrees\bellerophon-mwo-0001"
OUT = pathlib.Path(r"C:\Users\James\repl_2026-09-30\production_02"); OUT.mkdir(parents=True, exist_ok=True)
RUN = WT + r"\roles\Bellerophon\repl_2026-09-30\tools\falsify_run.py"
chunks = [("BASE:P90", 0, 25), ("BASE:P90", 25, 25), ("BASE:ZERO", 0, 25), ("BASE:ZERO", 25, 25), ("BASE:RANDOM", 0, 25), ("BASE:RANDOM", 25, 25),
          ("COPY:P90", 0, 50), ("COPY:ZERO", 0, 50), ("MUTLO:P90", 0, 50), ("MUTLO:ZERO", 0, 50), ("NOFND:P90", 0, 200), ("NOFND:ZERO", 0, 200)]
head = subprocess.check_output(["git", "-C", WT, "rev-parse", "HEAD"], text=True).strip()
ps = []
for i, (a, s0, n) in enumerate(chunks):
    ps.append(subprocess.Popen([sys.executable, "-I", RUN, "--arm", a, "--s0", str(s0), "--n", str(n), "--out", str(OUT / ("runs_%02d.jsonl" % i))],
                               cwd=WT, stdout=subprocess.DEVNULL, stderr=open(OUT / ("err_%02d.log" % i), "w")))
(OUT / "LAUNCH.json").write_text(json.dumps({"head": head, "chunks": chunks, "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1))
rc = [p.wait() for p in ps]
(OUT / "DONE.json").write_text(json.dumps({"finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "rc": rc}))
