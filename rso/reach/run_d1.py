"""D1 confirmatory runner: the archive-arm ladder on the p1_slice reach world (C-013-T010 builds it; C-013-T012 runs it).

    python -m rso.reach.run_d1 --out-dir rso/reach/runs/D1 [--workers 2]          (C-013-T012 only, after FREEZE_D1)
    python -m rso.reach.run_d1 --out-dir rso/reach/runs/D1 --resume [--max-rounds-this-call K]
    python -m rso.reach.run_d1 --toy --out-dir <scratch>                          (development: toy lineages only)

Frozen design: PREREGISTRATION.md (this file implements its s4-s6). Order of work:
  1. refuse unless every frozen file matches FROZEN_D1.json and the prototype matches its pins (--toy skips the
     freeze check, never the prototype check);
  2. CONTROLS (CONTROLS.json, never pooled with discoveries): every arm started AT the target (d = 0) must report a
     seeded hit at evaluation 0 that certifies; the impostors (holder, constant, lookup, empty) must NOT certify. Any
     control failure stops the run with status VOID_CONTROLS;
  3. ROUNDS j = 0 .. N_MAX-1: lineage j of every (d, arm) cell, d in DISTANCES, arm in ARMS -- 18 lineages per round,
     at most `workers` processes. Every training-perfect hit is certified (certify.py) before the row is written.
     One JSON row per lineage is appended to LEDGER.jsonl. After each round, if the summed worker CPU time has
     reached CPU_CAP_S the run stops (a round is never left incomplete); the analysis uses completed rounds only.
  4. any VOID certificate (oracle disagreement) stops the run with status VOID_INSTRUMENT.
RESUME. Rounds are written atomically (a whole round or nothing), lineages are deterministic, and the CPU total is
recomputed from the ledger, so --resume continues at the first missing round with identical results; a seat whose
tool calls are time-limited runs the design in slices with --max-rounds-this-call. The controls are re-run (and must
pass) on every call.
"""
import argparse
import hashlib
import json
import os
import pathlib
import platform
import sys
import time
from datetime import datetime, timezone

os.environ.setdefault("NUMBA_NUM_THREADS", "1")

HERE = pathlib.Path(__file__).resolve().parent
DISTANCES = (1, 3, 8)
N_MAX = 24
BUDGET = 200_000
CPU_CAP_S = 3.2 * 3600
TOY_LINEAGE0 = -500          # --toy uses lineages -500, -499, ... (development only)
TOY_BUDGET = 3000
TOY_ROUNDS = 2


def _sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def check_frozen():
    spec = json.loads((HERE / "FROZEN_D1.json").read_text(encoding="utf-8"))
    root = HERE.parents[1]
    bad = [p for p, h in spec["files"].items() if _sha(root / p) != h]
    if bad:
        raise SystemExit("REFUSED: frozen files changed since FREEZE_D1: %s" % bad)
    return spec


def _worker(task):
    from rso.reach import arms, certify
    arm, d, lineage, budget, geno_b, confirmatory = task
    c0 = time.process_time()
    r = arms.run_reach_lineage(arm, d, lineage, budget=budget, impl="nb", geno_buckets=geno_b,
                               confirmatory=confirmatory)
    row = {k: r[k] for k in ("evals", "cells", "accepted", "new_cells_admitted", "distinct_genomes", "final_fit",
                             "seeded_hit", "stones_evaluated", "max_stone_restored", "stones_retained_end")}
    row.update(arm=arm, d=d, lineage=lineage, knockout_index=arms.LINEAGE0 + lineage, budget=budget,
               geno_buckets=geno_b, start=r["start"].tolist(), final_prog=r["final_prog"].tolist())
    row["hit"] = r["evals"] >= 0
    row["certificate"] = None
    if row["hit"]:
        row["hit_prog"] = r["hit_prog"].tolist()
        row["certificate"] = certify.certify(r["hit_prog"], claimed_training_fit=r["final_fit"])
    row["discovery"] = bool(row["hit"] and not r["seeded_hit"] and row["certificate"]["certified"])
    row["cpu_s"] = time.process_time() - c0
    return row


def controls(geno_b_any):
    from rso.reach import arms, certify
    from rso.reach._proto import org
    out, ok = {"seeded": {}, "impostors": {}}, True
    for arm in arms.ARMS:
        r = _worker((arm, 0, 0, 100, geno_b_any if arm == "X3G" else None, True))
        good = r["evals"] == 0 and r["seeded_hit"] and r["certificate"]["certified"] and not r["discovery"]
        out["seeded"][arm] = dict(evals=r["evals"], seeded_hit=r["seeded_hit"], status=r["certificate"]["status"],
                                  counted_as_discovery=r["discovery"], ok=good)
        ok &= good
    P = certify.P
    imps = {"holder": org.holder(P.K), "constant": org.constant(), "lookup": org.lookup(),
            "empty": __import__("numpy").zeros((8, 4), dtype="int64")}
    for name, prog in imps.items():
        c = certify.certify(prog)
        out["impostors"][name] = dict(status=c["status"], ok=not c["certified"])
        ok &= not c["certified"]
    out["ok"] = bool(ok)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--toy", action="store_true")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--max-rounds-this-call", type=int, default=None)
    a = ap.parse_args(argv)
    from rso.reach import _proto, arms
    _proto.verify_prototype()
    spec = None if a.toy else check_frozen()
    cal = json.loads((HERE / "CALIBRATION_B.json").read_text(encoding="utf-8"))["by_d"]
    geno_b = {d: int(cal[str(d)]["B"]) for d in DISTANCES}
    out = pathlib.Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ledger = out / "LEDGER.jsonl"
    prior = []
    if ledger.exists():
        if not a.resume:
            raise SystemExit("REFUSED: %s exists; use --resume to continue it" % ledger)
        prior = [json.loads(x) for x in ledger.read_text(encoding="utf-8").splitlines() if x.strip()]
        if prior and len(prior) % (len(DISTANCES) * len(arms.ARMS)) != 0:
            raise SystemExit("REFUSED: ledger holds a partial round; inspect it, never repair it by hand")
        if (out / "RUN.json").exists() and json.loads((out / "RUN.json").read_text())["status"] not in (
                "IN_PROGRESS", "PAUSED"):
            raise SystemExit("REFUSED: the run already ended (RUN.json status is final)")
    budget = TOY_BUDGET if a.toy else BUDGET
    rounds = TOY_ROUNDS if a.toy else N_MAX
    lin0 = TOY_LINEAGE0 if a.toy else 0
    meta = dict(what="D1 archive-arm ladder" + (" (TOY development run)" if a.toy else ""),
                started_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), host=platform.node(),
                python=platform.python_version(), workers=a.workers, budget=budget, rounds_max=rounds,
                distances=DISTANCES, arms=arms.ARMS, geno_buckets=geno_b, seed=arms.SEED, lineage0=arms.LINEAGE0,
                cpu_cap_s=CPU_CAP_S, frozen=spec and spec.get("freeze_commit"))
    ctl = controls(geno_b[1])
    (out / "CONTROLS.json").write_text(json.dumps(ctl, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if not ctl["ok"]:
        meta.update(status="VOID_CONTROLS")
        (out / "RUN.json").write_text(json.dumps(meta, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return 2
    import multiprocessing as mp
    done = len(prior) // (len(DISTANCES) * len(arms.ARMS))
    cpu, status = sum(r["cpu_s"] for r in prior), "COMPLETE"
    if done and cpu >= CPU_CAP_S:
        status = "STOPPED_AT_CPU_CAP"
    stop_at = rounds if a.max_rounds_this_call is None else min(rounds, done + a.max_rounds_this_call)
    with mp.get_context("spawn").Pool(a.workers) as pool, open(ledger, "a", encoding="utf-8", newline="\n") as fh:
        for j in range(done, stop_at if status == "COMPLETE" else done):
            tasks = [(arm, d, lin0 + j, budget, geno_b[d] if arm == "X3G" else None, not a.toy)
                     for d in DISTANCES for arm in arms.ARMS]
            rows = pool.map(_worker, tasks)
            for row in rows:
                row["round"] = j
                fh.write(json.dumps(row, sort_keys=True) + "\n")
                cpu += row["cpu_s"]
            fh.flush()
            done = j + 1
            if any(r["certificate"] and r["certificate"]["status"] == "VOID" for r in rows):
                status = "VOID_INSTRUMENT"
                break
            print("round %d/%d done; cpu %.0f s" % (done, rounds, cpu), flush=True)
            if cpu >= CPU_CAP_S and done < rounds:
                status = "STOPPED_AT_CPU_CAP"
                break
    if status == "COMPLETE" and done < rounds:
        status = "PAUSED"
    meta.update(status=status, rounds_completed=done, cpu_s=round(cpu, 1),
                finished_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    (out / "RUN.json").write_text(json.dumps(meta, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if status in ("COMPLETE", "STOPPED_AT_CPU_CAP", "PAUSED") else 2


if __name__ == "__main__":
    sys.exit(main())
