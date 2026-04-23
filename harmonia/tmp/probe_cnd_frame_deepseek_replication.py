"""Cross-family replication probe for CND_FRAME objection — DeepSeek edition.

First probe (Claude Sonnet 4.6) returned: PASS/CND_FRAME boundary is
underdetermined because "shared observable Y" is itself lens-dependent;
lenses disputing Y-IDENTITY (not Y-value) may be PASS misclassified.

sessionB flagged MPA-variance caveat: single-run LLM probe = one
realization of the model's distribution, not calibrated. This probe
re-asks a STRUCTURALLY-SIMILAR question on DeepSeek (different family)
with NEUTRAL phrasing (doesn't hint at Y-identity framing).

Convergence on the same failure-mode = structural finding.
Divergence = Claude-family artifact.
"""
import sys, io, json
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from keys import get_key
import requests

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
Polya, and recently Irrationality Paradox — the last has each lens (CF
complexity / irrationality measure / transcendence class / normality /
OEIS position / motivic period form) committing to a DIFFERENT
measurable observable rather than disagreeing on the same one.

Give a direct, sharp structural critique. Specifically: is there a
hidden failure mode in how the classifier decides PASS vs FAIL? What
would cause it to systematically mislabel catalogs? Under 200 words.
NO preamble, NO hedging — identify ONE sharpest failure mode.
"""

def main():
    key = get_key('DEEPSEEK')
    url = "https://api.deepseek.com/chat/completions"
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": PROMPT}],
        "max_tokens": 500,
        "temperature": 0.7,
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    out = data["choices"][0]["message"]["content"]
    print("=== DEEPSEEK CROSS-FAMILY REPLICATION PROBE ===\n")
    print(out)
    print("\n=== META ===")
    print(f"model={data.get('model')}")
    print(f"usage={data.get('usage')}")
    return out

if __name__ == "__main__":
    main()
