"""PREFLIGHT for cw01-e06: provenance, environment and inherited-stack capability.

Records MEASURED facts, not recalled ones: interpreter and library versions read from
the running process, repository roots discovered by repopath from two different
directory depths, and the inherited-gate receipt read from disk rather than asserted.

CW01-D046: roots discovered by marker, never by counting parents. This file, like every
e06 module, is relocatable by construction.
"""
from __future__ import annotations

import json
import pathlib
import platform
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent


def _bootstrap_lib():
    for cand in [HERE] + list(HERE.parents):
        if (cand / "lib" / "repopath.py").exists():
            sys.path.insert(0, str(cand / "lib"))
            return cand / "lib"
    raise RuntimeError("cannot locate lib/repopath.py walking up from %s" % HERE)


LIB = _bootstrap_lib()
import repopath as RP          # noqa: E402
import recordsafety as RS      # noqa: E402

CAMPAIGN = RP.find_campaign_root(HERE)
REPO = RP.find_root(HERE)


def git(*a):
    r = subprocess.run(["git", "-C", str(REPO)] + list(a), capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def main():
    import numpy

    gate = {}
    gp = HERE / "INHERIT_GATE.json"
    if gp.exists():
        g = json.loads(gp.read_text(encoding="utf-8"))
        gate = {"all_proven": g["all_proven"], "n_passed": g["n_passed"],
                "n_total": g["n_total"],
                "gates": [c["id"] + ":" + c["gate"] for c in g["checks"] if c["passed"]]}
    else:
        gate = {"all_proven": None, "_note": "inherit_gate_e06.py has not been run"}

    # repopath discovery from TWO different depths, measured rather than claimed
    depths = {
        "from_lib": {"start": str(LIB), "depth": len(LIB.parts),
                     "repo": str(RP.find_root(LIB)), "campaign": str(RP.find_campaign_root(LIB))},
        "from_experiment": {"start": str(HERE), "depth": len(HERE.parts),
                            "repo": str(RP.find_root(HERE)),
                            "campaign": str(RP.find_campaign_root(HERE))},
    }
    depths["agree"] = (depths["from_lib"]["repo"] == depths["from_experiment"]["repo"]
                       and depths["from_lib"]["campaign"] == depths["from_experiment"]["campaign"])
    depths["depths_differ"] = depths["from_lib"]["depth"] != depths["from_experiment"]["depth"]

    out = {
        "campaign_id": "cw01-2026-09-17", "experiment_id": "cw01-e06",
        "attempt_id": "cw01-e06-a01", "phase": "PREFLIGHT",
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "environment": {
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "python_executable": sys.executable,
            "numpy": numpy.__version__,
        },
        "provenance": {
            "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "head": git("rev-parse", "--short", "HEAD"),
            "repo_root": str(REPO), "campaign_root": str(CAMPAIGN),
        },
        "path_policy": {
            "rule": "every e06 module resolves roots via lib/repopath; NO parents[N] assumptions",
            "discovery": depths,
            "_why": "CW01-D046 - e05 was reproducible IN PLACE but not relocatable, because REPO "
                    "was derived by counting directories. e06 is relocatable from inception.",
        },
        "seed_policy": {
            "rule": "all draws seeded from attempt_id via lib/seeds.py; latent facts drawn ONCE per "
                    "attempt, items drawn per episode (CW01-D029/D037)",
            "target": "attempt_target(cfg, seed)", "items": "make_items(cfg, rng, target)",
        },
        "inherited_stack": {
            "modules": ["contract", "guardproof", "repopath", "recordsafety", "writerlock",
                        "seeds", "localrun", "lineage", "infometrics", "learnability"],
            "engineering_target": gate,
            "_rule": "an inherited gate is not evidence until observed refusing in THIS experiment",
        },
        "durable_records": RS.check_records([CAMPAIGN / "CAMPAIGN_STATE.json",
                                             CAMPAIGN / "DEFECTS.jsonl"]),
        "tally_agreement": RS.check_tally(CAMPAIGN / "CAMPAIGN_STATE.json",
                                          CAMPAIGN / "DEFECTS.jsonl")["outcome"],
        "capability_match": {
            "needs_gpu": False, "needs_redis": False, "needs_network": False,
            "needs": "a git worktree and PM_TAG, nothing else",
            "_portability": "in-process via lib/localrun; requirement XI - Redis is never needed to "
                            "interpret a finished attempt",
        },
    }
    (HERE / "PREFLIGHT.json").write_text(json.dumps(out, indent=1, ensure_ascii=True),
                                         encoding="utf-8")
    print("PREFLIGHT written")
    print("  python %s | numpy %s" % (out["environment"]["python"], out["environment"]["numpy"]))
    print("  repo %s @ %s" % (pathlib.Path(out["provenance"]["repo_root"]).name,
                              out["provenance"]["head"]))
    print("  repopath depths %d vs %d, agree=%s, differ=%s"
          % (depths["from_lib"]["depth"], depths["from_experiment"]["depth"],
             depths["agree"], depths["depths_differ"]))
    print("  inherited gates: %s" % gate.get("all_proven"))
    print("  durable records: %s | tally %s" % (out["durable_records"]["verdict"],
                                                out["tally_agreement"]))
    return 0 if (depths["agree"] and depths["depths_differ"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
