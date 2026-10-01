import glob, subprocess, sys, pathlib, json, time
WT = r"D:\Prometheus-worktrees\bellerophon-mwo-0001"; OUT = pathlib.Path(r"C:\Users\James\repl_2026-09-30\posthoc"); OUT.mkdir(exist_ok=True)
runs = sorted(glob.glob(r"C:\Users\James\repl_2026-09-30\production\runs_*.jsonl"))
T = WT + r"\roles\Bellerophon\repl_2026-09-30\tools\posthoc_k3_shift.py"
ps = [subprocess.Popen([sys.executable, "-I", T] + runs + ["--out", str(OUT / ("k3_%d.jsonl" % k)), "--part", str(k), "--parts", "12"],
                       cwd=WT, stdout=subprocess.DEVNULL, stderr=open(OUT / ("err_%d.log" % k), "w")) for k in range(12)]
rc = [p.wait() for p in ps]
(OUT / "DONE.json").write_text(json.dumps({"finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "rc": rc}))
