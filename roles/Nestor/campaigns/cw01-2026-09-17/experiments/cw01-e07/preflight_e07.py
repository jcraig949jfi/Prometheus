"""PREFLIGHT for cw01-e07: provenance, environment, path policy, records, capability.

Records MEASURED facts: interpreter and library versions from the running process, roots
discovered by repopath from two different depths, durable-record portability and tally
agreement read from disk. The five inherited engineering gates were demonstrated by
observed refusal in e06 and are inherited FROZEN; they are not re-proven here (maximum
recursive validation depth ONE). Their self-tests are run once as a smoke check only.
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
import writerlock as WL        # noqa: E402

CAMPAIGN = RP.find_campaign_root(HERE)
REPO = RP.find_root(HERE)


def git(*a):
    r = subprocess.run(["git", "-C", str(REPO)] + list(a), capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def main():
    import numpy
    cfg = json.loads((HERE / "WORLD.json").read_text(encoding="utf-8"))

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

    smoke = {}
    for mod in ("repopath", "recordsafety", "writerlock"):
        r = subprocess.run([sys.executable, str(LIB / (mod + ".py"))], capture_output=True,
                           text=True, cwd=str(REPO))
        smoke[mod] = {"rc": r.returncode, "last": (r.stdout.strip().splitlines() or [""])[-1][:80]}

    wl = WL.check(REPO)
    records = RS.check_records([CAMPAIGN / "CAMPAIGN_STATE.json", CAMPAIGN / "DEFECTS.jsonl",
                                HERE / "WORLD.json"])
    tally = RS.check_tally(CAMPAIGN / "CAMPAIGN_STATE.json", CAMPAIGN / "DEFECTS.jsonl")

    out = {
        "campaign_id": cfg["campaign_id"], "experiment_id": cfg["experiment_id"],
        "attempt_id": cfg["attempt_id"], "phase": "PREFLIGHT",
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "environment": {"platform": platform.platform(), "python": sys.version.split()[0],
                        "python_executable": sys.executable, "numpy": numpy.__version__},
        "provenance": {"branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                       "head": git("rev-parse", "--short", "HEAD"),
                       "repo_root": str(REPO), "campaign_root": str(CAMPAIGN)},
        "path_policy": {"rule": "every e07 module resolves roots via lib/repopath; NO parents[N]",
                        "discovery": depths},
        "seed_policy": {"rule": "three independent components via lib/seeds: task stream "
                                "(attempt, r, kind, index), weather stream (attempt, r, kind, "
                                "generation), evolution stream (attempt, r, arm, lineage); "
                                "Q_r drawn ONCE per replicate world"},
        "inherited_stack": {
            "modules": ["contract", "guardproof", "repopath", "recordsafety", "writerlock",
                        "seeds", "localrun", "lineage", "infometrics", "learnability"],
            "frozen": True,
            "engineering_targets": "demonstrated by observed refusal in cw01-e06 (INHERIT_GATE.json); "
                                   "not re-proven here",
            "smoke": smoke},
        "writerlock_now": {"outcome": wl["outcome"], "reason": wl["reason"]},
        "durable_records": records,
        "tally_agreement": tally["outcome"],
        "capability_match": {"needs_gpu": False, "needs_redis": False, "needs_network": False,
                             "needs": "a git worktree and PM_TAG, nothing else",
                             "expected_compute": "minutes; 96 lineages x 120 generations, vectorised"},
        "world_params_hash_source": "WORLD.json",
    }
    (HERE / "PREFLIGHT.json").write_text(json.dumps(out, indent=1, ensure_ascii=True),
                                         encoding="utf-8")
    ok = (depths["agree"] and depths["depths_differ"] and records["safe"]
          and tally["outcome"] == "PASS" and all(v["rc"] == 0 for v in smoke.values()))
    print("PREFLIGHT written | python %s numpy %s | head %s" % (
        out["environment"]["python"], out["environment"]["numpy"], out["provenance"]["head"]))
    print("  repopath depths %d vs %d agree=%s | records %s | tally %s | writerlock %s"
          % (depths["from_lib"]["depth"], depths["from_experiment"]["depth"], depths["agree"],
             records["verdict"], tally["outcome"], wl["outcome"]))
    for k, v in smoke.items():
        print("  smoke %-12s rc=%d %s" % (k, v["rc"], v["last"]))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
