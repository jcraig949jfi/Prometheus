import sys, json, time, statistics
sys.path.insert(0, r"F:\Prometheus")
from pathlib import Path
from comp_sprint8_science.s8_runner import _build_artifact_from_proposal
from comp_sprint8_science.s8_benchmarks import build_s8_benchmarks
from comp_sprint8_science.s8_core import run_s8_artifact, fast_todd_2022_optimize, extract_phase_poly, odd_t_parities
D = Path(__file__).parent
mods = []
for nm, ex in [("mod_g0_rng_utils", None), ("mod_g0_todd_core", None), ("mod_g0_search", None)]:
    mods.append({"name": nm, "source": (D / f"{nm}.py").read_text(), "rationale": ""})
prop = {"new_modules": mods, "orchestrator_source": (D / "orchestrator.py").read_text(), "rationale": "g0"}
art = _build_artifact_from_proposal(prop, 0, None, "G0")
suites = build_s8_benchmarks()
split = sys.argv[1] if len(sys.argv) > 1 else "dev_diag"
lim = int(sys.argv[2]) if len(sys.argv) > 2 else 99
tot_a = tot_f = tot_0 = 0
for t in suites[split][:lim]:
    t0 = time.perf_counter()
    c, tel = run_s8_artifact(art, t.circuit, seed=0)
    w = time.perf_counter() - t0
    ft = fast_todd_2022_optimize(t.circuit).t_count()
    p0 = len(odd_t_parities(extract_phase_poly(t.circuit)[0]))
    tot_a += c.t_count(); tot_f += ft; tot_0 += p0
    print(t.task_id, t.circuit.n_qubits, "init", p0, "G0", c.t_count(), "FT", ft, "ops%", round(tel.get("ops_spent",0)/2400000*100,1), tel.get("status"), str(tel.get("error",""))[:120], tel.get("fn_errors"), "fb", tel.get("verifier_fallback"), f"{w:.1f}s", flush=True)
print("TOTAL init", tot_0, "G0", tot_a, "FT", tot_f)
