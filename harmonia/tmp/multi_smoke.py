"""Smoke: validate R7 (Opus) + Sonnet & Haiku call shapes (3 calls)."""
import sys, random
sys.path.insert(0, "harmonia/experiments")
from reasoning_phase0 import gen_R7, gen_R0, grade
from reasoners_llm import make_opus_reasoner

rng = random.Random(7)
r7 = [p for p in gen_R7(rng) if p.version == "clean"][0]   # a proof-repair probe
r0 = [p for p in gen_R0(rng) if p.version == "clean"][0]

print(f"R7 probe proof={r7.data['proof']} ground_truth(first-bad-step)={r7.ground_truth}")
for model, think, probe, label in [
    ("claude-opus-4-8", True, r7, "R7 proof-repair"),
    ("claude-sonnet-4-6", True, r0, "R0 linear"),
    ("claude-haiku-4-5", False, r0, "R0 linear"),
]:
    log = []
    rr = make_opus_reasoner(model=model, use_thinking=think, call_log=log)
    ans, tr = rr(probe)
    v, ok = grade(probe, ans, tr)
    print(f"{model:22s} [{label}] ans={ans} correct={ok} "
          f"parse_err={tr.get('_parse_error')} tokens={log[0].get('in')}/{log[0].get('out') if log and 'out' in log[0] else '?'}")
