"""C-012-T006: how much work is a native epoch? Times the in-process reference replay of run N20261010A's three worlds
(4 epochs x 8 ticks each) -- the same model.replay_chain the run compared its lineages against -- for the review
packet's cost argument. Read-only: no database, no Fabric, no node. Run from the repository root:

    python ops/campaigns/C-012/evidence/T006/time_native_reference.py --reps 5 --out ops/campaigns/C-012/evidence/T006/NATIVE_REFERENCE_TIMING.json
"""
import argparse
import json
import os
import platform
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO))
from moonshot.epoch import canonical as C  # noqa: E402
from moonshot.epoch import model  # noqa: E402
from moonshot.epoch import native_wforge as NW  # noqa: E402

RUN = REPO / "ops/campaigns/C-012/evidence/NATIVE/N20261010A/RUN.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    NW._wforge()                           # puts wforge on the path exactly as the runtime does
    from wforge import GRAMMAR_VERSION
    from wforge.genome import de_novo
    run = json.loads(RUN.read_text(encoding="utf-8"))
    rows = []
    for c in run["chains"]:
        seed = int(c["chain_id"][2:].split("-")[0])
        p = NW.genesis_params(de_novo(GRAMMAR_VERSION, seed), episode_seed=0, ticks_per_epoch=c["ticks_per_epoch"],
                              policy_seed=seed)
        g = model.make_genesis(c["chain_id"], epochs=c["epochs"], params=p, approved_code_sha=run["approved_code_sha"],
                               initial_checkpoint=NW.initial_checkpoint(p), runtime=NW.NATIVE_WFORGE_V1)
        assert C.sha256_hex(g.bytes) == c["genesis_sha256"], "not the run's genesis: " + c["chain_id"]
        times = []
        for _ in range(a.reps):
            t0 = time.perf_counter()
            model.replay_chain(g, c["epochs"])
            times.append(time.perf_counter() - t0)
        ticks = c["epochs"] * c["ticks_per_epoch"]
        rows.append({"chain_id": c["chain_id"], "world_id": c["world_id"], "horizon": c["horizon"], "ticks": ticks,
                     "replay_s": [round(t, 6) for t in times], "min_s": round(min(times), 6),
                     "us_per_tick_min": round(1e6 * min(times) / ticks, 1),
                     "fabric_run_s": [x["run_s"] for s in c["steps"] for x in s["attempts"]]})
    out = {"what": "in-process reference replay of N20261010A's chains (model.replay_chain), the work a native epoch "
                   "carries, vs the Fabric attempt run time the run recorded",
           "host": platform.node(), "python": platform.python_version(), "cpu_count": os.cpu_count(),
           "measured_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "reps": a.reps,
           "note": "M2 was carrying the operator's experiments; the times are upper bounds for this host",
           "chains": rows}
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
    for r in rows:
        print(r["chain_id"], "min {:.4f} s for {} ticks = {} us/tick; fabric run_s {}".format(
            r["min_s"], r["ticks"], r["us_per_tick_min"], r["fabric_run_s"]))


if __name__ == "__main__":
    main()
