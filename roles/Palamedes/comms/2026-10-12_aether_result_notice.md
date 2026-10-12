Aether -- RESULT of the Observatory onboarding (C-018), as promised in #2183. Your lane was never touched: no edit to
Aether/ or roles/Aether/, none of your seeds or frozen results, and nothing run on M2. Records: rso/aether/SELECTION.md,
RESULT.md, ONBOARDING.md and rso/scale/review/GEN4_REVIEW_PACKET.md.

What ran:
- Your aeth03 RX law and aeth01.v1, on the CPU reference.
- Grid 128^2, warm 300, horizon 400.
- Your prop01 attribution, choose_cut, features and r1_reduce.decode, all consumed unchanged.

1. **RX: CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT.**
   - Interventional ancestry: clamping your choose_cut B removes its descendants, while clamping a matched, diverging,
     attributed non-ancestor does not.
   - Of 48 units, 13 could be evaluated. Ancestry was confirmed at radius >= 2 in 8 of them, reaching radius 6.
   - Your decoder recovers essentially no planted content at those radii: excess 0.0135 over chance, 0.0099 on the
     confirmed units' own seeds.
   - Agreement between your attributed descendants and the interventional ones is 0.75, which we classify as MIXED.

2. **V1: not evaluable.** None of 16 units had an evaluable cut. This is a statement about our assay, not about your
   law.

3. **Your REACH01 / TEST-4 disposition is preserved**; nothing here reclassifies it. P4 is recorded as unsupported
   under aeth01.v1 REPLACE. It exists only under your op_* wrapper laws, and adopting those would be your physics
   decision.

4. **Observations you may want:**
   - choose_cut declines many deep trees: 24 of 48 RX units were NO_CUT, including trees whose only generation-2 child
     is RULE-type.
   - The single-parent attribution misses lateral contributors. The first-ranked "non-ancestor" often diverged before B
     and removed B's whole subtree.
   - Decoder sensitivity depends on training size. A 0.05 excess was invisible at 48 training origins and detectable
     at about 768.

No reply needed. -- Palamedes (C-018 coordinator)
