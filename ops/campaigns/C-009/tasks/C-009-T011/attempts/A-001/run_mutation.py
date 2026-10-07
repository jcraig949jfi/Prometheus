import json, os, sys, time
sys.path.insert(0, os.getcwd())
sys.dont_write_bytecode = True
from rso.slice001 import mutation as M
A = "ops/campaigns/C-009/tasks/C-009-T011/attempts/A-001/"
T = "rso.slice001.tests."
SUITE = [T + "test_evidence", T + "test_checker_render", T + "test_stages_evidence", T + "test_ledger"]
c0, t0 = time.process_time(), time.time()
out = M.run(A + "edits_x3_y1.json", os.getcwd(), SUITE, A + "mutation_rows.jsonl", timeout_s=600,
            require_committed=True, max_child_seconds=1800)
print(json.dumps({"baseline": out["baseline"], "summary": out["summary"], "wall_s": round(time.time() - t0, 1)},
                 sort_keys=True, indent=1))
