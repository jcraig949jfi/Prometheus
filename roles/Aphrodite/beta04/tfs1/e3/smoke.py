"""E3 DEVELOPMENT SMOKE on EXPOSED pilot_v2 worlds (labelled; not a screen, no statistics claimed).
One (world, arm, seed) per process:  python -m tfs1.e3.smoke --world W --arm ARM --seed 0 --B 20000
Writes runs/SMOKE_<world>_<arm>_s<seed>_B<B>.json = lifetime record + final evaluation + dependency tests."""
import argparse
import json
import os
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
from tfs1.e3 import organism as O        # noqa: E402
from tfs1.e3 import final_eval as FE     # noqa: E402
from tfs1.e3 import dependency as DP     # noqa: E402

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="foundry/pilot_v2")
    ap.add_argument("--world", required=True)
    ap.add_argument("--arm", required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--B", type=int, default=20000)
    ap.add_argument("--R", type=int, default=100)
    ap.add_argument("--K", type=int, default=8)
    ap.add_argument("--no-dep", action="store_true")
    a = ap.parse_args()
    t0 = time.process_time()
    rec = O.run_lifetime(a.root, a.world, a.arm, a.seed, B=a.B, R=a.R, K=a.K)
    t1 = time.process_time()
    fe = FE.evaluate_lifetime(rec, a.root, a.world)
    dep = [] if a.no_dep else DP.dependency_tests(rec, fe, a.root, a.world)
    t2 = time.process_time()
    out = {"label": "DEVELOPMENT SMOKE on EXPOSED pilot_v2 data; not a screen", "lifetime": rec, "final": fe,
           "dependency": dep, "cpu_s": {"lifetime": round(t1 - t0, 1), "final_and_dependency": round(t2 - t1, 1)}}
    p = HERE / "runs" / ("SMOKE_%s_%s_s%d_B%d.json" % (a.world, a.arm, a.seed, a.B))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=1, sort_keys=True, default=str))
    e = fe["endpoint"]
    print(a.world, a.arm, "solved", rec["solved"], "qualified", e["total_qualified"], "R3R4", e["R3R4_admitted_qualified"],
          "R2", e["R2_admitted_qualified"], "lib", len(rec["final_library"]["entries"]), "dep", len(dep),
          "cpu", out["cpu_s"], flush=True)


if __name__ == "__main__":
    main()
