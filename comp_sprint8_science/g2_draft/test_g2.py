import sys, time
sys.path.insert(0, r"F:\Prometheus")
from pathlib import Path
from comp_sprint8_science.s8_runner import _build_artifact_from_proposal
from comp_sprint8_science.s8_benchmarks import build_s8_benchmarks
from comp_sprint8_science.s8_core import run_s8_artifact

D = Path(__file__).parent
mods = [{"name": "mod_g2_escape", "source": (D / "mod_g2_escape.py").read_text(), "rationale": ""}]
prop = {"new_modules": mods, "orchestrator_source": (D / "orchestrator.py").read_text(), "rationale": "g2"}
art = _build_artifact_from_proposal(prop, 2, None, "G2")
suites = build_s8_benchmarks()
split = sys.argv[1] if len(sys.argv) > 1 else "dev_diag"
tot = 0
for t in suites[split]:
    t0 = time.perf_counter()
    c, tel = run_s8_artifact(art, t.circuit, seed=0)
    tot += c.t_count()
    print(t.task_id, t.circuit.n_qubits, "G2", c.t_count(), "ops%", round(tel.get("ops_spent", 0) / 2400000 * 100, 1),
          tel.get("status"), str(tel.get("error", ""))[:150], tel.get("fn_errors"), tel.get("fn_error_msgs"),
          "fb", tel.get("verifier_fallback"), "%.1fs" % (time.perf_counter() - t0), flush=True)
print("TOTAL G2", tot)
