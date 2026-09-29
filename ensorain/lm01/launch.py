"""WTP-LM01 LAUNCHER. It refuses unless ALL hold, in this order:
  1. freeze.verify(): every frozen file hashes to FREEZE.json (the study being launched is the frozen one);
  2. launch_gate.campaign_seeds(directive_path, freeze_commit, ...): a committed, MANIFEST-verified operator directive
     "LAUNCH WTP-LM01 using frozen prereg <prefix of the freeze commit>" (operator ruling 2026-09-26 item 6);
  3. an M2 process census: no other python process above 50% CPU (a measurement, not an assumption).
Then it runs campaign.job over (TESTABLE strata x 48 seeds) with 8 workers, BELOW_NORMAL, and the RAM gate, writing
rows per stratum to ensorain/lm01/campaign/<freeze_commit[:9]>/ and start/end to CAMPAIGN_LOG.jsonl.
Usage: python -m ensorain.lm01.launch <path to committed operator launch directive>"""
import json
import os
import sys
import time
from multiprocessing import Pool

HERE = os.path.dirname(__file__)


def census():
    import psutil
    ps = [p for p in psutil.process_iter(["pid", "name", "cmdline"]) if p.info["name"] and "python" in p.info["name"].lower()]
    for p in ps:
        try:
            p.cpu_percent(None)
        except Exception:
            pass
    time.sleep(2)
    me = os.getpid()
    busy = []
    for p in ps:
        try:
            if p.pid != me and p.cpu_percent(None) > 50:
                busy.append((p.pid, " ".join(p.info["cmdline"] or [])[:120]))
        except Exception:
            pass
    return busy


def main(directive_path, workers=8):
    from .freeze import verify
    from .launch_gate import campaign_seeds
    from .campaign import job, jobs
    fc, bad = verify()
    if bad:
        raise SystemExit(f"LM01 REFUSED: frozen files changed since the freeze: {bad}")
    dev = json.load(open(os.path.join(HERE, "dev", "margins_reduced_v2.json")))
    strata = sorted(k for k, v in dev.items() if v.get("frame") == "TESTABLE")
    seeds = campaign_seeds(directive_path, fc, strata, 48)
    busy = census()
    if busy:
        raise SystemExit(f"LM01 REFUSED: other heavy processes on M2: {busy}")
    out = os.path.join(HERE, "campaign", fc[:9])
    os.makedirs(out, exist_ok=True)
    J = jobs({tuple(k.split("|")): v for k, v in seeds.items()})
    J.sort(key=lambda j: {"L3": 0, "L2": 1, "L1": 2}[j["level"]])
    log = os.path.join(HERE, "CAMPAIGN_LOG.jsonl")
    t = lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(log, "a") as fh:
        fh.write(json.dumps(dict(event="launch", freeze_commit=fc, directive=directive_path, n_jobs=len(J),
                                 strata=len(strata), workers=workers, t=t())) + "\n")
    from .learn_probe import _init
    t0, n_stop = time.time(), 0
    with Pool(workers, initializer=_init) as p:
        for r in p.imap_unordered(job, J, chunksize=1):
            n_stop += r["status"] == "STOP_RAM"
            with open(os.path.join(out, f"{r['family']}__{r['level']}__{r['gen']}.jsonl"), "a") as fh:
                fh.write(json.dumps(r) + "\n")
    with open(log, "a") as fh:
        fh.write(json.dumps(dict(event="end", freeze_commit=fc, n_jobs=len(J), n_stop_ram=n_stop,
                                 wall_s=round(time.time() - t0, 1), t=t())) + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
