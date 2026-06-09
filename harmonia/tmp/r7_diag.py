"""Diagnose the R7 ValidationError on Opus: thinking on vs off + raw response."""
import sys, random, traceback
sys.path.insert(0, "harmonia/experiments")
from reasoning_phase0 import gen_R7
from reasoners_llm import _prompt_for, _SYSTEM
import anthropic
from keys import get_key
from pydantic import BaseModel

class Proof(BaseModel):
    failing_step_index: int = 0
    reasoning: str = ""

p = [x for x in gen_R7(random.Random(7)) if x.version == "clean"][0]
prompt = _prompt_for(p)
client = anthropic.Anthropic(api_key=get_key("claude"))

for think in (True, False):
    try:
        kw = dict(model="claude-opus-4-8", max_tokens=6000,
                  system=[{"type": "text", "text": _SYSTEM}],
                  messages=[{"role": "user", "content": prompt}],
                  output_format=Proof)
        if think:
            kw["thinking"] = {"type": "adaptive"}
        resp = client.messages.parse(**kw)
        print(f"think={think}: OK parsed={resp.parsed_output} stop={resp.stop_reason} "
              f"out_tokens={resp.usage.output_tokens}")
    except Exception as e:
        print(f"think={think}: ERR {type(e).__name__}: {str(e)[:400]}")
