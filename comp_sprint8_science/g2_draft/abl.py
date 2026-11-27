import sys, time
sys.path.insert(0, r"F:\Prometheus")
from pathlib import Path
from comp_sprint8_science.s8_runner import _build_artifact_from_proposal
from comp_sprint8_science.s8_benchmarks import build_s8_benchmarks
from comp_sprint8_science.s8_core import run_s8_artifact, fast_todd_2022_optimize
D = Path(__file__).parent
src = (D / "mod_g2_escape.py").read_text()
variants = {"full": src, "no_flat": src.replace("    m = len(P)\n    if m < 6:\n        return None, -99", "    m = len(P)\n    if m < 10**9:\n        return None, -99")}
split = sys.argv[1]
tasks = build_s8_benchmarks()[split]
ft = sum(fast_todd_2022_optimize(t.circuit).t_count() for t in tasks)
print(split, "FastTODD", ft)
for name, s in variants.items():
    prop = {"new_modules": [{"name": "mod_g2_escape", "source": s}], "orchestrator_source": (D / "orchestrator.py").read_text()}
    art = _build_artifact_from_proposal(prop, 2, None, "G2")
    tot = 0; errs = 0
    for t in tasks:
        c, tel = run_s8_artifact(art, t.circuit, seed=0)
        tot += c.t_count(); errs += sum(tel["fn_errors"].values()) + (tel["status"] != "ok")
    print(split, name, tot, "errs", errs, flush=True)
