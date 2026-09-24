"""Campaign entry point. Freeze, verify, run, freeze again, emit.

ORDER OF OPERATIONS, AND WHY
 1. The grammar's hash must equal the hash recorded in PREREGISTRATION.md. If the two
    differ, the semantics changed after preregistration and the campaign REFUSES to run.
    That is the whole meaning of 'no new experiment semantics generated during execution'.
 2. The calibration gate must return PASS. A campaign whose VM, replicators, witnesses,
    exogenous control and invasion control have not been demonstrated cannot interpret a
    negative result, so it does not get to produce one.
 3. Only then does the scheduler start, on its own wall clock.
 4. At the deadline the scheduler stops cleanly, state is frozen, and the packet is
    emitted from the index rather than from anything held in memory - so the packet is
    reproducible from the artefacts alone.

Resume is supported: the same command with --resume picks up the producer's counts and
the campaign clock. A resume whose grammar hash differs is refused, not repaired.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import controls                      # noqa: E402
import grammar as G                  # noqa: E402
import packet as PK                  # noqa: E402
import scheduler as SC               # noqa: E402

PREREG = HERE / "PREREGISTRATION.md"


def prereg_hash():
    if not PREREG.exists():
        return None
    m = re.search(r"GRAMMAR_SHA256:\s*([0-9a-f]{64})", PREREG.read_text(encoding="ascii"))
    return m.group(1) if m else None


def gate(force_calibration=False):
    ph = prereg_hash()
    gh = G.grammar_hash()
    if ph is None:
        print("REFUSE: PREREGISTRATION.md has no GRAMMAR_SHA256 line", flush=True)
        return False
    if ph != gh:
        print("REFUSE: grammar hash %s does not match preregistered %s" % (gh[:16], ph[:16]), flush=True)
        return False
    cal_path = HERE / "CALIBRATION.json"
    cal = json.loads(cal_path.read_text(encoding="ascii")) if cal_path.exists() else None
    if force_calibration or cal is None or cal.get("gate") != "PASS" or cal.get("grammar_hash") != gh:
        print("running calibration...", flush=True)
        rc = controls.main()
        if rc != 0:
            print("REFUSE: calibration gate did not pass", flush=True)
            return False
    else:
        print("calibration already PASS for this grammar (%s)" % cal["written"], flush=True)
    return True


def heartbeat(sched):
    print("[%s] stage=%s elapsed=%.2fh submitted=%d completed=%d failed=%d specials=%d disk=%.2fGB"
          % (time.strftime("%H:%M:%S"), sched.stage(), (time.time() - sched.t_start) / 3600,
             sched.submitted, sched.completed, sched.failed, sched.specials,
             sched.obs.stats()["gb_written"]), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=72.0)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--root", default=str(HERE / "observatory"))
    ap.add_argument("--disk-gb", type=float, default=60.0)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--smoke", action="store_true", help="short end-to-end rehearsal")
    ap.add_argument("--skip-gate", action="store_true", help="smoke rehearsal only")
    a = ap.parse_args()

    if a.smoke:
        a.hours = min(a.hours, 0.05)
        a.root = str(HERE / "smoke")

    if not a.skip_gate and not gate():
        return 2

    root = pathlib.Path(a.root)
    sched = SC.Scheduler(root, hours=a.hours, workers=a.workers, seed=a.seed,
                         disk_budget_gb=a.disk_gb)
    if a.resume and sched.load_state():
        print("resumed: %.2f h already elapsed" % ((time.time() - sched.t_start) / 3600), flush=True)
    (root / "LAUNCH.json").write_text(json.dumps({
        "started": time.strftime("%Y-%m-%d %H:%M:%S"), "hours": a.hours, "workers": a.workers,
        "seed": a.seed, "grammar_hash": G.grammar_hash(), "resume": bool(a.resume),
        "smoke": bool(a.smoke), "python": sys.version.split()[0]}, indent=1), encoding="ascii")

    summary = sched.run(heartbeat=heartbeat)
    (root / "SCHEDULER_SUMMARY.json").write_text(
        json.dumps(summary, indent=1, ensure_ascii=True, default=str), encoding="ascii")
    p = PK.emit(root, summary)
    (root / "DONE").write_text(time.strftime("%Y-%m-%d %H:%M:%S"), encoding="ascii")
    print(json.dumps(p["totals"], indent=1), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
