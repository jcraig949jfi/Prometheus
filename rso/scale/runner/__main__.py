"""python -m rso.scale.runner <command> (C-013-T022)

    create <run_dir> --spec <spec.json>     freeze a run (spec: name, runtime, params, partitions, epochs[, ...])
    launch <run_dir>                        start a detached supervisor (survives the caller) and return
    supervise <run_dir>                     run the supervisor in the foreground
    work <run_dir> <chain_id>               one worker for one partition chain
    status <run_dir>                        heads, leases, supervisor, latest progress (JSON)
    verify <run_dir> <chain_id>             the s3.8 resume checks, replay forced (records a RESUME_CHECK row)
    account <run_dir> [--write]             the final account (JSON); --write stores FINAL_ACCOUNT.json once
    control <run_dir>                       the uninterrupted control digest (JSON)
    relaunch <run_dir>                      idempotent host-relaunch entry for a scheduler timer (relaunch.py)
    prune <run_dir> [--dry-run]             apply the manifest's checkpoint_retention policy (retention.py)
"""
import argparse
import json
import os
import sys

from rso.scale.runner import account as A
from rso.scale.runner import control as CTL
from rso.scale.runner import engine as E
from rso.scale.runner import lease as L
from rso.scale.runner import resume as RS
from rso.scale.runner import relaunch as RL
from rso.scale.runner import retention as RET
from rso.scale.runner import run as RUN
from rso.scale.runner import store as S
from rso.scale.runner import supervisor as SUP
from rso.scale.runner import worker as W


def status(run_dir):
    m, mid = RUN.load_manifest(run_dir)
    out = {"manifest_id": mid, "chains": {}}
    for c in RUN.chain_ids(m):
        out["chains"][c] = {"head": RUN.head(run_dir, c), "lease": L.live_holder(run_dir, c),
                            "latest_progress": RUN.latest_progress(run_dir, c)}
    p = os.path.join(SUP.sdir(run_dir), "SUPERVISOR.json")
    cur = S.read_json(p) if os.path.exists(p) else None
    out["supervisor"] = dict(cur, live=SUP._live(cur)) if cur else None
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m rso.scale.runner")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("create")
    c.add_argument("run_dir")
    c.add_argument("--spec", required=True)
    for name in ("launch", "supervise", "status", "control", "_spawn", "relaunch"):
        sub.add_parser(name).add_argument("run_dir")
    for name in ("work", "verify"):
        s = sub.add_parser(name)
        s.add_argument("run_dir")
        s.add_argument("chain_id")
    pr = sub.add_parser("prune")
    pr.add_argument("run_dir")
    pr.add_argument("--dry-run", action="store_true")
    a = sub.add_parser("account")
    a.add_argument("run_dir")
    a.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    rd = os.path.abspath(args.run_dir)
    if args.cmd == "create":
        with open(args.spec, encoding="utf-8") as f:
            spec = json.load(f)
        print(json.dumps(RUN.create_run(rd, **spec), indent=1))
        return 0
    if args.cmd == "launch":
        print(json.dumps(SUP.launch_detached(rd)))
        return 0
    if args.cmd == "relaunch":
        out = RL.relaunch(rd)
        print(json.dumps(out), flush=True)
        return RL.EXIT[out["action"]]
    if args.cmd == "_spawn":
        SUP.spawn_supervisor(rd)
        return 0
    if args.cmd == "supervise":
        SUP.guard_code_root(E.REPO)
        st = SUP.supervise(rd)
        print(json.dumps(st), flush=True)
        return 0 if st["state"] == "COMPLETE" else 2
    if args.cmd == "work":
        return W.main(rd, args.chain_id)
    if args.cmd == "verify":
        eng = E.get_engine(RUN.load_manifest(rd)[0]["engine"]["runtime"])
        print(json.dumps(RS.verify_resume(rd, args.chain_id, eng, force_replay=True), indent=1))
        return 0
    if args.cmd == "status":
        print(json.dumps(status(rd), indent=1, default=str))
        return 0
    if args.cmd == "prune":
        print(json.dumps(RET.prune(rd, dry_run=args.dry_run), indent=1))
        return 0
    if args.cmd == "account":
        print(json.dumps(A.final_account(rd, write=args.write), indent=1))
        return 0
    if args.cmd == "control":
        print(json.dumps(CTL.control(rd), indent=1))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
