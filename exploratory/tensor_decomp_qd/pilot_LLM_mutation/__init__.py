"""LLM-driven mutation pilot for the polymul-n3 substrate.

Wraps Anthropic Claude (Haiku 4.5) as a mutation operator inside MAP-Elites,
applied to the polymul-n3 over F_2 tensor (rank 6 known via Karatsuba; naive
rank 9; 12 distinct sub-optimal orbits at rank 9 already found by local
mutation in the sibling pilot_polymul_n3).

The hypothesis: LLM-proposed whole-decomposition edits may bridge between
rank-r orbits that local bit-flip and column-level moves cannot.

Honest framing: AlphaEvolve already does LLM-driven matmul mutation without
QD. Our defensible contribution is the QD ARCHIVE on top, not the LLM-as-
mutation per se. We do NOT claim to find novel matmul algorithms.
"""
