"""Sample the RSS of a process tree every 20 s until the root exits; append JSON lines to --out. Engineering only."""
import argparse, json, time, psutil
ap = argparse.ArgumentParser(); ap.add_argument("--pid", type=int, required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
root = psutil.Process(a.pid)
with open(a.out, "a", encoding="utf-8") as fh:
    while root.is_running() and root.status() != psutil.STATUS_ZOMBIE:
        try:
            procs = [root] + root.children(recursive=True)
            rss = [p.memory_info().rss for p in procs if p.is_running()]
            fh.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "n": len(rss), "sum_mb": round(sum(rss) / 2**20),
                                 "max_mb": round(max(rss) / 2**20), "free_gb": round(psutil.virtual_memory().available / 2**30, 1)}) + "\n"); fh.flush()
        except psutil.Error:
            pass
        time.sleep(20)
