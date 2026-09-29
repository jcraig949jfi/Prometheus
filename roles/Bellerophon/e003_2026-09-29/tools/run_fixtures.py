"""Run Archaeon's BEE fixture pack (archaeon/attribution/bee_fixtures.py, Amendment A; images + expectations as data)
against Bellerophon's tracer on the PINNED frozen VM.

The pack module imports `archaeon.attribution.bee_ref_tracer as T` and calls T.vm16(), T.trace() and T.identified().
Here a STUB module supplies those three names from this seat's tracer, so Archaeon's tracer is never loaded or read.
The pack source is read byte-exact from the arc branch at the pinned SHA (git show) and executed with the stub in
place. check() -- the pack's own comparison -- is unchanged.
    python run_fixtures.py --arc-sha 028f2eff8 --out <receipt.json>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import types

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bee_tracer as BT  # noqa: E402

HARNESS = "C:/Users/James/e003_harness_16fc6c2a"


def load_vm():
    if HARNESS not in sys.path:
        sys.path.insert(0, HARNESS)
    from prometheus.z80atlas import vm
    return vm


def stub(vm):
    m = types.ModuleType("archaeon.attribution.bee_ref_tracer")
    m.vm16 = lambda: vm

    def trace(mem, L, budget, inputs, bug=None):
        if bug is not None:
            raise NotImplementedError("mutant tracers are Archaeon's; not part of the owner's run")
        after, recs, info = BT.trace(vm, bytearray(mem), L, budget, list(inputs), allow_copyall=True)
        return after, recs, info
    m.trace = trace
    m.identified = BT.identified_rule
    m.MUTANTS = {}
    pkg = types.ModuleType("archaeon"); sub = types.ModuleType("archaeon.attribution"); pkg.attribution = sub
    sub.bee_ref_tracer = m
    sys.modules["archaeon"] = pkg; sys.modules["archaeon.attribution"] = sub; sys.modules["archaeon.attribution.bee_ref_tracer"] = m


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arc-sha", default="028f2eff8"); ap.add_argument("--repo", default="D:/Prometheus"); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    src = subprocess.run(["git", "-C", a.repo, "show", "%s:archaeon/attribution/bee_fixtures.py" % a.arc_sha], capture_output=True, check=True).stdout
    vm = load_vm(); stub(vm)
    mod = types.ModuleType("bee_fixtures_pack"); mod.__file__ = "bee_fixtures.py@%s" % a.arc_sha
    exec(compile(src.decode("utf-8"), mod.__file__, "exec"), mod.__dict__)
    F = mod.fixtures()
    res = {}; all_fails = []
    for name, (m, x, exp) in F.items():
        try:
            fails, _, _ = mod.check(name, m, x, exp)
        except Exception as e:                                   # a tracer crash or a divergence from the frozen VM is a FAIL
            fails = ["%s EXCEPTION %r" % (name, e)]
        res[name] = {"pass": not fails, "fails": fails}
        all_fails += fails
    out = {"pack_source": "archaeon/attribution/bee_fixtures.py@%s" % a.arc_sha, "pack_sha256": hashlib.sha256(src.replace(b"\r\n", b"\n")).hexdigest(),
           "tracer_sha256": hashlib.sha256((HERE / "bee_tracer.py").read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
           "fixtures": len(F), "passed": sum(r["pass"] for r in res.values()), "results": res}
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("fixtures", "passed")}), "\n".join(all_fails[:60]))
    return 0 if not all_fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
