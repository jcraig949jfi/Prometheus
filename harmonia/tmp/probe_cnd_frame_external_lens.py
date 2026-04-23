"""External-lens probe for CND_FRAME@v1 three-way classifier.

Calls Claude Sonnet 4.6 via Anthropic API with a minimal fresh-context prompt
asking for structural critique + one candidate anchor. Purpose: get input
from an LLM that has not been shaped by team priors.

Usage: python harmonia/tmp/probe_cnd_frame_external_lens.py
Run-time: ~5-15s.
"""
import sys, io
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from keys import get_key
import anthropic

PROMPT = """You are being asked for a fresh external perspective. You have no prior
context on the project this is from; please evaluate based only on the text below.

A small research team is building a three-way classifier for catalogs of
"disciplinary lenses applied to an open math problem." The classifier takes
a catalog (a set of named lenses, each with a committed prediction on some
observable) and returns one of three verdicts:

  PASS      — at least one pair of lenses makes incompatible predictions
              on a shared downstream observable Y that is measurable at
              current scale AND not yet resolved. ("Substrate-divergent.")
  FAIL -> CND_FRAME — lenses disagree, but not on any shared Y at current
              scale. Sub-flavors: obstruction_class / truth_axis /
              framing_of_phenomenon / operator_identity.
  FAIL -> CONSENSUS_CATALOG — all lenses agree with community consensus
              and no adversarial frame is catalogued.

PASS catalogs drive future measurement. CND_FRAME catalogs drive
substrate-work (build tools to make the disagreement measurable).
CONSENSUS_CATALOG catalogs drive catalog-work (generate adversarial
frames).

Five CND_FRAME anchors so far: Brauer-Siegel (obstruction_class),
knot_concordance (truth_axis), ulam_spiral (framing_of_phenomenon),
Hilbert-Polya (operator_identity), Irrationality Paradox (currently
tagged framing_of_phenomenon but reviewers are debating a new
"partition_axis_disagreement" sub-flavor — each lens measures a
different thing rather than disagreeing on a shared thing).

Two questions, be direct, NO preamble, NO apologies:

1. What is the strongest conceptual objection to this three-way classifier?
   Not "interesting but vague" — a sharp objection. If the classifier has
   a hidden failure mode where it would mislabel or miss a real phenomenon,
   name it. Under 150 words.

2. Identify ONE candidate CONSENSUS_CATALOG anchor that is NOT a famous
   Millennium/Clay problem (those are obvious and already flagged as
   candidates). Something from applied math, engineering, or physics where
   community consensus is strong and adversarial frames are rarely
   catalogued. Name the problem, name 2-3 lenses that would align, and
   name what the missing adversarial frame class would be. Under 200 words.
"""

def main():
    client = anthropic.Anthropic(api_key=get_key('CLAUDE'))
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": PROMPT}],
    )
    out = resp.content[0].text
    print("=== EXTERNAL-LENS PROBE RESPONSE ===\n")
    print(out)
    print("\n=== META ===")
    print(f"model={resp.model}")
    print(f"usage={resp.usage}")
    return out

if __name__ == "__main__":
    main()
