"""Reduce Aether unit Attempts into Task states, for both lanes (Blocks F, G).

  expected   Build a known-answer task list: each task names a slice of a
             ladder-2 run whose result is already committed
             (AETH-03/evidence/2026-09-26_propagation/prop_<law>_n128_s<k>.json);
             its expected legacy_sha256 is computed FROM THAT FILE with the
             same canonicalisation the unit runner uses. The expected answer
             is the historical record, not a fresh run.

  reduce     Read a task list and a directory of Attempt files named
             <task_id>__A-<k>__<host>.json. Per task:
               MISSING            no Attempt produced a result
               DETERMINISM_ALARM  two Attempts disagree on result_sha256
               INSTRUMENT_VOID    an Attempt reports locality violations
               MATCH / MISMATCH   known-answer lane: legacy hash vs expected
               DONE               open-science lane: at least one result
             The battery is COMPLETE only if every task is MATCH (known) or
             DONE (open) with no alarm. An INCOMPLETE battery gets no
             aggregate: the reducer lists what is missing and stops.
"""

import argparse
import glob
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_AETHER = os.path.dirname(_HERE)
if _AETHER not in sys.path:
    sys.path.insert(0, _AETHER)

from observatory import aeth03_unit as U                 # noqa: E402

ARMS = {"off": "perturbation_off", "on": "perturbation_on"}


def expected_from_record(evidence_dir, law, seed_index, arm, start, stop):
    path = os.path.join(evidence_dir, "prop_%s_n128_s%d.json" % (law, seed_index))
    with open(path, encoding="utf-8") as fh:
        rec = json.load(fh)
    runs = rec["arms"][ARMS[arm]][start:stop]
    inputs = U.unit_inputs(law, seed_index, arm, start, stop, rec["n"], rec["warmup"],
                           rec["ticks"], 32)
    return inputs, U.sha(U.canon(U.science_block(inputs, runs, legacy=True)))


def cmd_expected(a):
    tasks = []
    for i, spec in enumerate(a.spec):
        law, seed, arm, sl = spec.split(",")
        start, stop = (int(x) for x in sl.split(":"))
        inputs, exp = expected_from_record(a.evidence, law, int(seed), arm, start, stop)
        tasks.append({"task_id": "%s%03d" % (a.prefix, a.first + i), "lane": "known",
                      "unit_id": U.unit_id(inputs), "inputs": inputs,
                      "expected_legacy_sha256": exp,
                      "expected_from": os.path.relpath(
                          os.path.join(a.evidence, "prop_%s_n128_s%s.json" % (law, seed)),
                          _AETHER).replace(os.sep, "/")})
    print(json.dumps(tasks, indent=1))


def cmd_reduce(a):
    with open(a.tasks, encoding="utf-8") as fh:
        tasks = json.load(fh)
    out, complete = [], True
    for t in tasks:
        atts = []
        for p in sorted(glob.glob(os.path.join(a.results, "%s__A-*.json" % t["task_id"]))):
            with open(p, encoding="utf-8") as fh:
                r = json.load(fh)
            atts.append({"file": os.path.basename(p), "result_sha256": r["result_sha256"],
                         "legacy_sha256": r.get("legacy_sha256"),
                         "unit_id": r["unit_id"], "host": r["host"]["hostname"],
                         "platform": r["host"]["platform"],
                         "numpy": r["host"]["numpy"],
                         "wall_seconds": round(r["resources"]["wall_seconds"], 1),
                         "peak_rss_mb": r["resources"]["peak_rss_mb"],
                         "violations": r["locality_violations"]})
        row = {"task_id": t["task_id"], "lane": t["lane"], "attempts": atts}
        if not atts:
            row["state"] = "MISSING"
        elif len({x["result_sha256"] for x in atts}) > 1:
            row["state"] = "DETERMINISM_ALARM"
        elif any(x["violations"] for x in atts):
            row["state"] = "INSTRUMENT_VOID"
        elif any(x["unit_id"] != t["unit_id"] for x in atts):
            row["state"] = "WRONG_UNIT"
        elif t["lane"] == "known":
            row["state"] = ("MATCH" if atts[0]["legacy_sha256"] == t["expected_legacy_sha256"]
                            else "MISMATCH")
        else:
            row["state"] = "DONE"
        if row["state"] not in ("MATCH", "DONE"):
            complete = False
        out.append(row)
    verdict = "COMPLETE" if complete else "INCOMPLETE"
    report = {"battery": verdict, "tasks": out}
    if not complete:
        report["blocking"] = [r["task_id"] + ":" + r["state"] for r in out
                              if r["state"] not in ("MATCH", "DONE")]
    print(json.dumps(report, indent=1))
    return 0 if complete else 3


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("expected")
    e.add_argument("--evidence", required=True)
    e.add_argument("--prefix", default="T-")
    e.add_argument("--first", type=int, default=1)
    e.add_argument("spec", nargs="+", help="law,seed,arm,start:stop")
    r = sub.add_parser("reduce")
    r.add_argument("--tasks", required=True)
    r.add_argument("--results", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "expected":
        cmd_expected(a)
        return 0
    return cmd_reduce(a)


if __name__ == "__main__":
    raise SystemExit(main())
