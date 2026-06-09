"""2-call smoke: validate the Opus-4.8 structured-output reasoner call shape."""
import sys, random
sys.path.insert(0, "harmonia/experiments")
from reasoning_phase0 import gen_R0, gen_R6, grade
from reasoners_llm import make_opus_reasoner

rng = random.Random(1)
probes = [gen_R0(rng)[0], gen_R6(rng)[0]]  # one linear, one conjecture
log = []
r = make_opus_reasoner(call_log=log)
for p in probes:
    ans, tr = r(p)
    v, ok = grade(p, ans, tr)
    print(f"{p.tier}/{p.version}/{p.kind}: ans={ans} correct={ok} "
          f"parse_err={tr.get('_parse_error')} provider={tr.get('_provider')}")
print("call_log:", log)
