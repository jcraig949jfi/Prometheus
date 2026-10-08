"""Run declared experiments sequentially in a detached process.  python -B runqueue.py [--after=PID] EXP1 EXP2 ...
Each experiment's pool output goes to runs/<EXP>.log; queue state lines go to runs/QUEUE.log."""
import contextlib, pathlib, sys, time
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
if __name__ == "__main__":
    import exp, fh
    q = HERE / "runs" / "QUEUE.log"
    names = sys.argv[1:]
    if names and names[0].startswith("--after="):
        import psutil
        pid = int(names.pop(0).split("=")[1])
        with open(q, "a") as f:
            f.write("%s WAIT for pid %d before %s" %  (time.strftime("%Y-%m-%dT%H:%M:%S"), pid, names) + chr(10))
        while psutil.pid_exists(pid):
            time.sleep(30)
    for name in names:
        with open(q, "a") as f:
            f.write("%s START %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%S"), name))
        with open(HERE / "runs" / (name + ".log"), "a") as lf, contextlib.redirect_stdout(lf):
            try:
                fh.pool_run(name, exp.EXPS[name]["jobs"], HERE / "runs" / name, 4)
                st = "DONE"
            except Exception as e:
                st = "FAIL %r" % (e,)
        with open(q, "a") as f:
            f.write("%s %s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%S"), st, name))
