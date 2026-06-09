"""Does messages.parse accept output_config.effort + structured output? (1 call)"""
import sys, random
sys.path.insert(0, "harmonia/experiments")
from reasoning_phase0 import gen_R2, grade
from reasoners_llm import make_opus_reasoner

p = [x for x in gen_R2(random.Random(2)) if x.version == "clean"][0]
for eff in ("max", "low"):
    log = []
    r = make_opus_reasoner(model="claude-opus-4-8", use_thinking=True, effort=eff, call_log=log)
    ans, tr = r(p)
    v, ok = grade(p, ans, tr)
    print(f"effort={eff}: ans={ans} correct={ok} parse_err={tr.get('_parse_error')} "
          f"out_tokens={log[0].get('out') if log and 'out' in log[0] else '?'} err={tr.get('_raw_excerpt') if tr.get('_parse_error') else ''}")
