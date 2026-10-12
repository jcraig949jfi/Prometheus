"""ATLAS on FOUNDRY PILOT task JSON (calibration of the pipeline on generator-made tasks; NOT the E2 production run).

  python -m atlas.pilot TASK.json [TASK.json ...]      (from roles/Aphrodite/beta04)

Selection rule (fixed before any measurement, outcome-free): the first R2 and the first R3 admitted task, by file name,
of each pilot world W1, W2, W3 at origin/main 3491cfd49 (foundry/pilot/<W>/tasks/admitted/). Foundry CODE was not read;
only contract task JSON is consumed. Searches and archives receive the dev-only LearnerView; the witness and the
task's own tribunal reach only the Certifier and the atlas route measurements.
Writes atlas/calibration/PILOT_<family_id>.json.
"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
from tfs1.enum import Enumerator                 # noqa: E402

from . import common as K                        # noqa: E402
from . import descriptors as D                   # noqa: E402
from . import measure as M                       # noqa: E402
from .calibration import B, OUT, run_ladder      # noqa: E402

SEEDS = (0, 1, 2, 3)


def run(path):
    raw = Path(path).read_bytes()
    T = K.load_task(json.loads(raw))
    t0 = time.process_time()
    E = Enumerator(None)
    rec = {"source": str(Path(path).name), "task_sha256": hashlib.sha256(raw).hexdigest(),
           "source_commit": "origin/main 3491cfd49 roles/Aphrodite/beta04/foundry/pilot/",
           "label": "FOUNDRY PILOT task (world qualification NOT final: foundry v1 NOT_QUALIFIED per 7cd8fc3f4); "
                    "atlas pipeline calibration only"}
    a = M.atlas(T, None, seeds=SEEDS, enum_budget=16 * B, enum_max_size=7, density_max_n=6, robust_n=500,
                rank_max_class=600_000, E=E)
    rec["atlas"] = a
    rec["atlas_cpu_s"] = a["cpu_s"]
    t1 = time.process_time()
    rec["qualification"] = D.qualify(T, T["witness"], None, per_size=1000, walk_n=4000)
    rec["qual_cpu_s"] = round(time.process_time() - t1, 1)
    t2 = time.process_time()
    rec["ladder"] = run_ladder(T, None, SEEDS, B, E=E)
    rec["ladder_cpu_s"] = round(time.process_time() - t2, 1)
    rec["ladder"]["descriptor_arm_status"] = ("VALIDATED" if "D-BEH" in rec["qualification"]["qualified"]
                                              else "INSTRUMENT_UNVALIDATED")
    rec["classification_route"] = M.classify(a, B)
    rec["cpu_s"] = round(time.process_time() - t0, 1)
    (OUT / ("PILOT_%s.json" % T["family_id"])).write_text(json.dumps(rec, indent=1, sort_keys=True, default=str))
    print(T["family_id"], "cpu", rec["cpu_s"], rec["classification_route"].get("local_search"),
          rec["ladder"]["hits_by_arm"], rec["qualification"]["qualified"], flush=True)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        run(p)
