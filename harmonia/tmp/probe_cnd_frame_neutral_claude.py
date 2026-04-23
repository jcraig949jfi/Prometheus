"""Within-family variance check: second Claude call with neutral phrasing.

First probe (same model, Claude Sonnet 4.6) led with an explicit three-way
classifier description and asked for "strongest conceptual objection" —
response: PASS/CND_FRAME boundary is underdetermined; Y-IDENTITY dispute
mode. That response may be prompt-steered.

This probe:
- Same model (claude-sonnet-4-6)
- NEUTRAL phrasing: no "strongest objection" framing, no leading question
- Asks ONLY: "is this classifier well-specified?"
- Discards the Irrationality Paradox anchor detail that hinted at Y-identity dispute

Convergence on same objection = within-model robust (prompt-invariant).
Divergence = prior response was prompt-steered.

Still within-family (Claude x Claude); cross-family (Gemini/DeepSeek/OpenAI)
is infrastructure-blocked this tick (DeepSeek 402, Gemini package missing).
"""
import sys, io
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from keys import get_key
import anthropic

PROMPT = """A team is designing a classifier for sets of "disciplinary lenses
applied to an open problem." Each lens commits to a prediction on some
observable. The classifier returns one of:

  A) at least one pair of lenses gives incompatible predictions on a
     shared observable Y, measurable now
  B) lenses disagree but on no shared-and-measurable Y
  C) lenses all agree with a community consensus

Is this classifier well-specified? Evaluate under 200 words. Direct, no
preamble, no hedging.
"""

def main():
    client = anthropic.Anthropic(api_key=get_key('CLAUDE'))
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": PROMPT}],
    )
    out = resp.content[0].text
    print("=== NEUTRAL CLAUDE PROBE (within-family variance) ===\n")
    print(out)
    print("\n=== META ===")
    print(f"model={resp.model}  usage={resp.usage}")
    return out

if __name__ == "__main__":
    main()
