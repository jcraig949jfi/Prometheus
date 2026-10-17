"""Run one frozen REACH01 script under aeth01.op_xor_fold, then stamp its JSON output with the semantics.

    python r01_run.py STAMP_JSON REACH01_SCRIPT [script args...]

REACH01_SCRIPT is relative to Aether/V2B/REACH01 (e.g. R3/r3_frontier.py). The script runs as __main__ in this
process after fold_physics.install(), so its op "XOR" is the fold law and any other op raises. STAMP_JSON is the
script's own output file; if the script wrote it, a "robust01" block is added (atomic replace), including the number
of fold ticks this process executed. A missing output is left missing, so a failed unit stays visibly failed to the
resume-safe flight driver. express01.py itself is refused: run as a script it calls its own module-level step, which
the patch does not reach.
"""

import hashlib
import json
import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fold_physics as FP  # noqa: E402

RUNNER = "r01_run.v1"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def stamp(path):
    if not os.path.exists(path):
        return
    d = json.load(open(path))
    d["robust01"] = {"semantics_id": FP.SEMANTICS_ID, "op_string_means": "XOR -> " + FP.SEMANTICS_ID,
                     "control_semantics_id": FP.CONTROL_SEMANTICS_ID, "runner": RUNNER,
                     "fold_physics_sha256": sha(os.path.join(HERE, "fold_physics.py")),
                     "fold_ticks_executed": FP.STEP_CALLS}
    tmp = path + ".stamp"
    json.dump(d, open(tmp, "w"), separators=(",", ":"))
    os.replace(tmp, path)


def main():
    out, script, args = sys.argv[1], sys.argv[2], sys.argv[3:]
    if os.path.basename(script) == "express01.py":
        print("robust01: express01.py as a script uses its own step and would bypass the fold law", file=sys.stderr)
        return 2
    FP.install()
    path = os.path.join(FP.REACH01, script)
    print("robust01: %s under %s" % (script, FP.SEMANTICS_ID), file=sys.stderr)
    sys.argv = [path] + args
    rc = 0
    try:
        runpy.run_path(path, run_name="__main__")
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    if rc == 0:
        stamp(out)
    return rc


if __name__ == "__main__":
    sys.exit(main())
