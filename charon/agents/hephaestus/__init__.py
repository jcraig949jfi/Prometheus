"""Hephaestus -- forger / composer agent (Charon swarm v0.7, 8th member).

Named for the smith god (forger of new things from raw materials).

Per 4/4 frontier-model convergence (2026-05-25): the conspicuously
missing layer in the Charon swarm is GENERATIVE/CONSTRUCTIVE, not
another passive scanner. Every prior agent (Stygian, Lethe, Acheron,
Moros, Hecate, Nephele, Pollux) measures, audits, critiques, or
fetches; none synthesize new candidate claims.

Hephaestus closes the loop: it reads Stygian PROMOTED rows + Pollux
PROMOTED rows + Hecate cross-generator canonical patterns; composes
intersection-claims ('Stygian claim X holds when restricted to
Pollux survivor subset Y'); emits the composed claim as a kill_ledger
row AND enqueues it to stygian_priority for v10 battery validation.
"""
