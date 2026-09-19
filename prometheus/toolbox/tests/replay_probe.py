"""Cross-process / cross-platform replay probe (overnight C46/C47). Prints the primary trace hashes of the
committed EXP-001 and EXP-002 fixtures recomputed in THIS interpreter, as JSON, so another process (or another
platform's Python) can compare. No pytest needed: python -m prometheus.toolbox.tests.replay_probe"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile


def main() -> dict:
    from prometheus.toolbox.examples.exp_001_delay_sweep import build as b1
    from prometheus.toolbox.examples.exp_002_substrate_sweep import build as b2
    from prometheus.toolbox.backends.local import execute
    from prometheus.toolbox.receipt import read_all
    from prometheus.toolbox.registry import default_registry
    out = {"python": sys.version.split()[0], "platform": sys.platform, "fixtures": {}}
    with tempfile.TemporaryDirectory() as d:
        for name, build in (("exp_001", b1), ("exp_002", b2)):
            e = build(); e.controls = []
            execute(e.compile("local", default_registry()).job, pathlib.Path(d) / (name + ".jsonl"), default_registry())
            rs = read_all(pathlib.Path(d) / (name + ".jsonl"))
            out["fixtures"][name] = {json.dumps(r["sweep_point"], sort_keys=True) + "|" + str(r["seed"]): r["trace_hashes"] for r in rs if r["arm"] == "primary"}
        try:
            from prometheus.toolbox.registry import default_registry as DR
            from prometheus.toolbox.ir import Experiment, ref
            from prometheus.toolbox.ref.players import random_statemachine
            reg = DR()
            if reg.has("world.c6.composed.v1") and reg.get("world.c6.composed.v1").state != "UNAVAILABLE":
                e = Experiment(family="c6probe", world=ref("world.c6.composed.v1", seed=3, bin=6), substrate=ref("substrate.flat.v1"), players=[random_statemachine(1).manifest()],
                               seed_policy={"base": 1, "n_seeds": 3}, budget={"episodes": 2, "horizon": 24})
                execute(e.compile("local", reg).job, pathlib.Path(d) / "c6.jsonl", reg)
                out["fixtures"]["c6"] = {str(r["seed"]): r["trace_hashes"] for r in read_all(pathlib.Path(d) / "c6.jsonl") if r["arm"] == "primary"}
        except Exception as exc:                                    # noqa: BLE001
            out["fixtures"]["c6"] = {"error": str(exc)[:200]}
    print(json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    main()
