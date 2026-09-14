"""Stage C ablation: spin-pathfinder-priority-inversion-1997 -- which of the two candidate mechanisms is the deadlock made of?

Pre-registered before running (this docstring is the prereg):
  BASELINE  the model as preserved                       -> expect errors: 1 (invalid end state), as Techne's receipt shows
  A1  REMOVE the priority rule (drop `provided (h_state == idle)`)   -> if the deadlock is the rule's, errors: 0
  A2  REMOVE the mutex guard (mutex never busy: `mutex == free` always true, never set busy) -> errors: 0 predicted; mutual exclusion is lost (not measured here)
  A3  REVERSE the rule (low runs only when high is NOT idle)          -> unknown; recorded either way
  A4  WEAKEN the rule so a high task WAITING counts as yielding (`provided (h_state != running)`) -> the human story says a blocked high
      task would let low run; if errors: 0 the model's deadlock lives in the rule's over-approximation, not in the mutex
  CONTROL  a syntactically altered but semantically identical model (rename mtype constants) -> errors: 1
Outcome measure: pan's 'errors: N' line. Exhaustive search on a 12-state model; no statistics needed.
LEDGERED REPAIR after run 1 (receipt kept as *_run1_vacuous_indicator.json): the secondary indicator 'invalid end state' in stdout was
vacuous -- pan prints 'invalid end states +' in its summary on every run; the indicator now matches the error line 'pan:N: invalid end state'.
The primary measure (errors count) and all six results are unchanged between run 1 and run 2.
"""
import re
from nyx.atlas.tunnel import Experiment

F = "spin-pathfinder-priority-inversion-1997"
SPIN = "upstream/tree/Spin-version-6.5.2"
e = Experiment(F, "ablate_rule_vs_mutex", image="prometheus-fossil-c:bookworm", note=__doc__)
e.copy_from_body(SPIN + "/Src", "Src")
base = e.copy_from_body(SPIN + "/Examples/pathfinder.pml", "models/baseline.pml")
orig = base.read_text(encoding="utf-8")

variants = {
    "baseline": orig,
    "A1_remove_priority_rule": orig.replace("active proctype low() provided (h_state == idle) /* scheduling rule */", "active proctype low()"),
    "A2_remove_mutex_guard": orig.replace("atomic { mutex == free -> mutex = busy };", "skip;").replace("atomic { mutex == free -> mutex = busy};", "skip;"),
    "A3_reverse_priority_rule": orig.replace("provided (h_state == idle)", "provided (h_state != idle)"),
    "A4_waiting_high_yields": orig.replace("provided (h_state == idle)", "provided (h_state != running)"),
    "CONTROL_rename_constants": orig.replace("free", "libre").replace("busy", "ocupado"),
}
for name, text in variants.items():
    assert text != orig or name == "baseline", name
    e.write(f"models/{name}.pml", text, intervention=name)

r = e.run("build spin", "cd Src && make -s 2>&1 | grep -iE '\\berror' | head -3; test -x ./spin && echo built", timeout=900)
results = {}
for name in variants:
    out = e.run(f"verify {name}", f"cd models && ../Src/spin -a {name}.pml 2>&1 | tail -1; gcc -O2 -w -o pan_{name} pan.c && ./pan_{name} 2>&1 | grep -E 'invalid end state|errors:|assertion|pan:' | head -6; rm -f pan.* *.trail")
    m = re.search(r"errors:\s*(\d+)", out["stdout"])
    results[name] = {"errors": int(m.group(1)) if m else None, "invalid_end_state": bool(re.search(r"pan:\d+: invalid end state", out["stdout"])), "raw": out["stdout"].strip()[:400]}
    print("   ", name, results[name]["errors"], results[name]["invalid_end_state"])

fp = {"organ_candidates": [F + "::fixed_priority_run_rule", F + "::binary_mutex_test_and_set"],
      "intervention": "remove / reverse / weaken one mechanism at a time; exhaustive verification",
      "measure": "pan errors count (invalid end state = deadlock)", "results": results,
      "reading": {
          "rule_removed_kills_deadlock": results["A1_remove_priority_rule"]["errors"] == 0,
          "mutex_removed_kills_deadlock": results["A2_remove_mutex_guard"]["errors"] == 0,
          "waiting_counts_as_yield_kills_deadlock": results["A4_waiting_high_yields"]["errors"] == 0,
          "control_preserved": results["CONTROL_rename_constants"]["errors"] == results["baseline"]["errors"] == 1}}
e.save(fingerprint=fp, controls=[{"name": "CONTROL_rename_constants", "expect": "errors: 1", "got": results["CONTROL_rename_constants"]["errors"]}])
