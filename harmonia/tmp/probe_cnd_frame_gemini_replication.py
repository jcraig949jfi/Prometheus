"""Cross-family replication probe for CND_FRAME objection.

First probe (Claude Sonnet 4.6) returned: "PASS/CND_FRAME boundary is
underdetermined because 'shared observable Y' is itself lens-dependent;
lenses disputing Y-IDENTITY (not Y-value) may be PASS misclassified."

sessionB flagged MPA-variance caveat: single-run = one realization. This
probe asks GEMINI (different family) the structurally-same question with
NEUTRAL phrasing (doesn't lead with Y-IDENTITY framing). Tests replication.

Convergent on same objection = structural. Divergent = Claude-family artifact.
"""
import sys, io
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from keys import get_key
import google.generativeai as genai

PROMPT = """You are being asked for a fresh external perspective. You have no prior
context; evaluate based only on the text below.

A small research team is building a three-way classifier for catalogs of
"disciplinary lenses applied to an open math problem." Given a catalog (a
set of named lenses, each with a committed prediction), it returns:

  PASS      — at least one pair of lenses makes incompatible predictions
              on a shared downstream observable Y that is measurable at
              current scale AND not yet resolved.
  FAIL -> CND_FRAME — lenses disagree, but not on any shared Y at current
              scale. Sub-flavors: obstruction_class / truth_axis /
              framing_of_phenomenon / operator_identity.
  FAIL -> CONSENSUS_CATALOG — all lenses agree with community consensus
              and no adversarial frame is catalogued.

PASS catalogs drive measurement; CND_FRAME catalogs drive substrate-work;
CONSENSUS_CATALOG catalogs drive catalog-work.

Current anchors: Brauer-Siegel, knot_concordance, ulam_spiral, Hilbert-
Polya, and recently Irrationality Paradox — the last of which has each
lens (CF complexity / irrationality measure / transcendence class /
normality / OEIS position / motivic period form) committing to a
DIFFERENT measurable observable rather than disagreeing on the same one.

Give a direct, sharp structural critique. Specifically: is there a
hidden failure mode in how the classifier decides PASS vs FAIL? What
would cause it to systematically mislabel catalogs? Under 200 words.
NO preamble, NO hedging — identify ONE sharpest failure mode.
"""

def main():
    genai.configure(api_key=get_key('GEMINI'))
    model = genai.GenerativeModel('gemini-2.5-flash')
    resp = model.generate_content(PROMPT)
    out = resp.text
    print("=== GEMINI CROSS-FAMILY REPLICATION PROBE ===\n")
    print(out)
    print("\n=== META ===")
    try:
        um = resp.usage_metadata
        print(f"prompt_tokens={um.prompt_token_count} output_tokens={um.candidates_token_count}")
    except Exception as e:
        print(f"usage unavailable: {e}")
    return out

if __name__ == "__main__":
    main()
