import sys, time
sys.path.insert(0, r"F:\Prometheus")
from pathlib import Path
from comp_sprint8_science.s8_runner import _build_artifact_from_proposal
from comp_sprint8_science.s8_benchmarks import build_s8_benchmarks
from comp_sprint8_science.s8_core import run_s8_artifact

D = Path(__file__).parent
split = sys.argv[1] if len(sys.argv) > 1 else "dev_diag"
which = sys.argv[2] if len(sys.argv) > 2 else "g3"
if which == "g3":
    mods = [{"name": "mod_g3_rmflat", "source": (D / "mod_g3_rmflat.py").read_text(), "rationale": ""}]
    orch = (D / "orchestrator.py").read_text()
else:
    G2 = D.parent / "g2_draft"
    mods = [{"name": "mod_g2_escape", "source": (G2 / "mod_g2_escape.py").read_text(), "rationale": ""}]
    orch = (G2 / "orchestrator.py").read_text()
art = _build_artifact_from_proposal({"new_modules": mods, "orchestrator_source": orch}, 3, None, which)
suites = build_s8_benchmarks()
seeds = [0, 1, 2]
tot = 0
t0 = time.perf_counter()
for t in suites[split]:
    cs = []
    for sd in seeds:
        c, tel = run_s8_artifact(art, t.circuit, seed=sd)
        cs.append(c.t_count())
        if tel.get("fn_errors") or tel.get("verifier_fallback") or tel.get("status") != "ok":
            print("PROBLEM", t.task_id, tel.get("status"), str(tel.get("error", ""))[:200], tel.get("fn_errors"), tel.get("fn_error_msgs"), tel.get("verifier_fallback"))
    tot += sum(cs)
    print(t.task_id, cs, "ops%", round(tel.get("ops_spent", 0) / 2400000 * 100, 1), flush=True)
print(which, split, "TOTAL(3 seeds)", tot, "avg/seed", round(tot / 3, 2), "wall", round(time.perf_counter() - t0, 1))
