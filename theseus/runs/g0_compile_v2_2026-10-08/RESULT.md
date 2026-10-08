# THESEUS-32: G0 compiler collapse -- measurement and a flag-gated v2 compile (2026-10-08)

Finding (Hestia #1897 s4.19; seat recount): v1 compiles 95 concepts into 67 distinct op
sequences; the largest identical-sequence class is 22 concepts (diffuse + saturate, differing
only in seeded parameters); 24 concepts compile to 2-rule programs.

Change: compile_g0.compile_corpus(v2=True). When fewer than 3 non-bounding rules fire, add the
fixed rules of the concept's declared Nous "mechanism" field (dynamics: advect + react;
structure: coarse + mirror; constraint: conserve + threshold; measure: rank + select).
Deterministic, keyword/field-driven, no interpretation. v1 (default) is byte-identical to the
committed v0_1 corpus; no run has used v2 yet.

v2: 73 distinct op sequences; largest identical class 9; no 2-rule programs (min 3 rules).
Command: python -c "from theseus.synth import compile_g0 as cg; cg.compile_corpus(v2=True)".
Limit: the mechanism field has four values, so v2 removes the 2-rule collapse but still maps
many description-only concepts to a few templates; the text-length confound of v1 remains.
