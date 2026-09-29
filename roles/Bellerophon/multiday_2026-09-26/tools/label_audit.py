"""POST-HOC label audit of E-BEL-MD (labelled; never an endpoint change). Written after the frozen analysis ran.

The frozen endpoint `acquired` reads final_competent_sr, i.e. the lineage label sr_depth > 0 (a birth event), which can
include tapes that do not copy themselves (Odysseus #748/#804; DEF-BEL-003). For every acquired run, this reads the
frozen per-run arch descriptor of the dominant competent SR tape (adjudication.arch_descriptor: self_copy alone, task
accuracy on the configured task) already stored in results.jsonl, and whether that tape equals a founder/fixture tape.
    python label_audit.py <workdir>/results.jsonl <out.json>
"""
import collections
import json
import sys

R = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
acq = [r for r in R if not r.get("void") and ((r.get("competence") or {}).get("final_competent_sr") or 0) > 0]
cells = collections.defaultdict(lambda: {"acquired": 0, "self_copy": 0, "task_exact": 0, "equals_fixture": 0})
for r in acq:
    a = r.get("dominant_competent_arch") or {}
    c = cells["%s|%s" % (r["lane"], r["arm"])]
    c["acquired"] += 1; c["self_copy"] += bool(a.get("self_copy")); c["task_exact"] += a.get("task_accuracy") == 1.0
    c["equals_fixture"] += (r.get("competence") or {}).get("dominant_competent_sr_tape") in (r.get("fixture_tapes") or [])
out = {"about": "post-hoc label audit; not an endpoint", "acquired_runs": len(acq), "by_lane_arm": dict(sorted(cells.items()))}
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
