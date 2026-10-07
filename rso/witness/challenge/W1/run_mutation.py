"""C-010-T014 W1: run the six committed semantic edits with rso/slice001/mutation.py under ONE ledgered TOP_LEVEL
launch on the C-010 ledger (every child a MUTATION_CHILD row parented to it, charged its wall seconds).

DRIVER REPAIR after the set commit (931be915f): the headless rule caps every foreground command at 600 s, and
3 baselines + 6 children at ~70 s each exceed it, so the run is split by target module over three invocations that
share ONE launch (begun by the first, finished by the last; state in mutation_launch.json beside this file). The
edits run from the per-module files edits_<module>.json, byte-identical subsets of the frozen edits.json
(verified at load: every subset edit equals its edits.json entry), each committed before execution.

    python -B rso/witness/challenge/W1/run_mutation.py --ledger rso/witness/LEDGER.jsonl --contract rso/witness/contract.json \
        --edits rso/witness/challenge/W1/edits_evaluate.json --rows rso/witness/challenge/W1/mutation_rows_evaluate.jsonl
    ... --edits edits_ares_client.json --rows mutation_rows_ares_client.jsonl
    ... --edits edits_ruler.json --rows mutation_rows_ruler.jsonl --finish

Suite: the packet's acceptance suites (rso/witness/tests, rso/binding/tests) -- the frozen suite in full; a survivor
needs no second confirmation run.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.dont_write_bytecode = True

from rso.slice001 import ledger as L                       # noqa: E402
from rso.slice001 import mutation as M                     # noqa: E402

W = "rso.witness.tests."
SUITE = [W + n for n in ("test_ares_client", "test_evaluate", "test_launch_inventory", "test_make_configs", "test_ruler",
                         "test_run_witness")] + ["rso.binding.tests.test_binding"]
W1_BUDGET_S = 20 * 60              # this packet's allowance inside the C-010 60 CPU-minute cap (all invocations)
SUPPLIED_BY = "pallas C-010-T014 run_mutation.py"
STATE = os.path.join(HERE, "mutation_launch.json")
FROZEN = os.path.join(HERE, "edits.json")


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _subset_is_frozen(edits_path):
    """Every edit of the file equals, field for field, its entry in the frozen edits.json."""
    frozen = {e["edit_id"]: e for e in json.load(open(FROZEN, encoding="utf-8"))["edits"]}
    for e in json.load(open(edits_path, encoding="utf-8"))["edits"]:
        if frozen.get(e["edit_id"]) != e:
            raise SystemExit("edit %s differs from the frozen edits.json" % e["edit_id"])
    return sorted(frozen)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--contract", default=L.DEFAULT_CONTRACT)
    ap.add_argument("--edits", default=FROZEN)
    ap.add_argument("--rows", default=os.path.join(HERE, "mutation_rows.jsonl"))
    ap.add_argument("--finish", action="store_true", help="finish the shared TOP_LEVEL launch after this invocation")
    a = ap.parse_args(argv)
    frozen_ids = _subset_is_frozen(a.edits)
    led = L.Ledger.from_contract(a.ledger, a.contract)
    state = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else None
    if state is None:
        run_id = "W1-MUTATION-%s-%d" % (utc().replace(":", "").replace("-", ""), os.getpid())
        led.begin(run_id, "W1-MUTATION", L.TOP_LEVEL, supplied_by=SUPPLIED_BY)
        state = {"run_id": run_id, "next_child": 1, "cpu_s": 0.0, "charged_wall_s": 0.0, "invocations": [],
                 "frozen_edit_ids": frozen_ids, "status": "OPEN", "began_at_utc": utc()}
    run_id = state["run_id"]
    c0 = time.process_time()
    original = M._run_child

    def charged(job, timeout_s):
        n = state["next_child"]
        state["next_child"] = n + 1
        att = led.begin("%s/child-%03d" % (run_id, n), "W1-MUTATION-CHILD:" + os.path.basename(a.edits),
                        L.MUTATION_CHILD, supplied_by=SUPPLIED_BY, parent_run_id=run_id)
        try:
            res, wall = original(job, timeout_s)
        except BaseException:
            att.finish("FAILED", cpu_s=0.0)
            raise
        timed_out = res.get("phase") == "timeout"
        secs = float(timeout_s if timed_out else wall)
        state["charged_wall_s"] += secs
        att.finish("FAILED" if timed_out else "COMPLETED", cpu_s=secs)
        return res, wall

    M._run_child = charged
    report, ok = {"run_id": run_id, "edits_file": os.path.basename(a.edits), "rows": os.path.basename(a.rows)}, False
    try:
        remaining = max(0.0, W1_BUDGET_S - state["charged_wall_s"])
        out = M.run(a.edits, ROOT, SUITE, a.rows, timeout_s=900, require_committed=True, max_child_seconds=remaining)
        report.update({"suite": SUITE, "baseline": out["baseline"], "summary": out["summary"]})
        ok = True
    except L.CapExhausted as e:
        report["cap_exhausted"] = str(e)
    finally:
        M._run_child = original
        state["cpu_s"] += time.process_time() - c0
        state["invocations"].append({"edits_file": os.path.basename(a.edits), "rows": os.path.basename(a.rows),
                                     "ok": ok, "at_utc": utc()})
        if a.finish or not ok:
            status = "COMPLETED" if ok and all(i["ok"] for i in state["invocations"]) else "FAILED"
            L.Attempt(led, run_id).finish(status, cpu_s=state["cpu_s"])
            state["status"] = status
            state["finished_at_utc"] = utc()
        with open(STATE, "w", encoding="utf-8", newline="\n") as f:
            json.dump(state, f, indent=1, sort_keys=True)
    report["state"] = state
    report["ledger_usage"] = led.usage()
    print(json.dumps(report, sort_keys=True, indent=1, default=str))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
