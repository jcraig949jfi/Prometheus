"""pte_mut: mutation / metamorphic testing of PTE experimental semantics (Ananke Wave-2, worker W2-C).

Draft package. Imports prometheus.ananke read-only; corrupts experiments only by monkeypatching attributes
inside context managers (operators.py) and restores them on exit. See score.py for the classification rules.
"""
