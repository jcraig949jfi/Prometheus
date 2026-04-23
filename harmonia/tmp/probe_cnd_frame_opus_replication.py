"""Third-seed cross-instance variance check: Opus 4.7 internal probe.

Uses sessionA's neutral prompt verbatim (probe_cnd_frame_neutral_claude.py)
but with claude-opus-4-7 model. Different model family within Anthropic
(opus vs sonnet) — provides cross-model variance per MPA discipline.

Per sessionB ops_note (1776906965662-0): 2 sonnet seeds converge on
structural objection. 3rd seed needed before cementing v1.1 amendment.
This probe is that 3rd seed.
"""
import sys, io
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from keys import get_key
import anthropic

# Verbatim from sessionA's neutral probe
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
        model="claude-opus-4-7",
        max_tokens=600,
        messages=[{"role": "user", "content": PROMPT}],
    )
    out = resp.content[0].text
    print("=== OPUS 4.7 PROBE (3rd seed, cross-model within Anthropic) ===\n")
    print(out)
    print("\n=== META ===")
    print(f"model={resp.model}  usage={resp.usage}")
    return out

if __name__ == "__main__":
    main()
