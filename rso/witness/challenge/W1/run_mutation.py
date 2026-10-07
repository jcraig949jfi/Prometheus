"""C-010-T014 W1: run the six committed semantic edits with rso/slice001/mutation.py (ONE ledgered TOP_LEVEL launch
on the C-010 ledger; every child a MUTATION_CHILD row parented to it, charged its wall seconds).

    python -B rso/witness/challenge/W1/run_mutation.py --ledger rso/witness/LEDGER.jsonl --contract rso/witness/contract.json

Suite: the packet's acceptance suites (rso/witness/tests, rso/binding/tests) -- the frozen suite in full; a survivor
needs no second confirmation run. Rows: mutation_rows.jsonl beside this file.
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
W1_BUDGET_S = 20 * 60              # this packet's allowance inside the C-010 60 CPU-minute cap
SUPPLIED_BY = "pallas C-010-T014 run_mutation.py"


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--contract", default=L.DEFAULT_CONTRACT)
    a = ap.parse_args(argv)
    led = L.Ledger.from_contract(a.ledger, a.contract)
    run_id = "W1-MUTATION-%s-%d" % (utc().replace(":", "").replace("-", ""), os.getpid())
    top = led.begin(run_id, "W1-MUTATION", L.TOP_LEVEL, supplied_by=SUPPLIED_BY)
    c0 = time.process_time()
    state = {"n": 0}
    original = M._run_child

    def charged(job, timeout_s):
        state["n"] += 1
        att = led.begin("%s/child-%03d" % (run_id, state["n"]), "W1-MUTATION-CHILD", L.MUTATION_CHILD,
                        supplied_by=SUPPLIED_BY, parent_run_id=run_id)
        try:
            res, wall = original(job, timeout_s)
        except BaseException:
            att.finish("FAILED", cpu_s=0.0)
            raise
        timed_out = res.get("phase") == "timeout"
        att.finish("FAILED" if timed_out else "COMPLETED", cpu_s=float(timeout_s if timed_out else wall))
        return res, wall

    M._run_child = charged
    report, ok = {"run_id": run_id}, False
    try:
        out = M.run(os.path.join(HERE, "edits.json"), ROOT, SUITE, os.path.join(HERE, "mutation_rows.jsonl"),
                    timeout_s=900, require_committed=True, max_child_seconds=W1_BUDGET_S)
        report.update({"suite": SUITE, "baseline": out["baseline"], "summary": out["summary"]})
        ok = True
    except L.CapExhausted as e:
        report["cap_exhausted"] = str(e)
    finally:
        M._run_child = original
        top.finish("COMPLETED" if ok else "FAILED", cpu_s=time.process_time() - c0)
    report["ledger_usage"] = led.usage()
    print(json.dumps(report, sort_keys=True, indent=1, default=str))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
