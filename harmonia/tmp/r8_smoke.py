"""Smoke R8 lemma-selection on Opus (3 calls)."""
import sys, random
sys.path.insert(0, "harmonia/experiments")
from reasoning_phase0 import gen_R8, grade
from reasoners_llm import make_opus_reasoner

rng = random.Random(8)
probes = [p for p in gen_R8(rng) if p.version == "clean"][:3]
log = []
r = make_opus_reasoner(model="claude-opus-4-8", use_thinking=True, call_log=log)
for p in probes:
    ans, tr = r(p)
    v, ok = grade(p, ans, tr)
    correct_type = p.data["types"][p.ground_truth - 1]
    picked_type = p.data["types"][ans - 1] if isinstance(ans, int) and 1 <= ans <= 5 else "?"
    print(f"goal={p.data['goal'][:42]!r}  truth_idx={p.ground_truth}({correct_type})  "
          f"ans={ans}({picked_type})  correct={ok}  parse_err={tr.get('_parse_error')}")
