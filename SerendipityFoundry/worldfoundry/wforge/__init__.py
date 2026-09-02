"""wforge -- World Foundry v0 prototype.

Deterministic, integer-only, seeded generative system for world mechanics.
A world is the pure-function expansion of a genome by a versioned grammar.
No floats anywhere in world physics (cross-host determinism by construction).
No wall-clock, no OS entropy, no dict-order dependence in any trace.

This is an OFFLINE DESIGN PROTOTYPE for the v0 external review packet:
no service, no port, no evolution loop, no campaign.
"""

GRAMMAR_VERSION = "wforge-grammar-0.1"
