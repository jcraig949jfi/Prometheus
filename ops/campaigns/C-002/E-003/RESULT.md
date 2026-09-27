# E-003 result -- propagation assay audit (Block A). CLOSED 2026-09-27.

Full account: Aether/AETH-03/PROPAGATION_ASSAY_AUDIT.md. Evidence: Aether/AETH-03/evidence/2026-09-27_assay_audit/.
Instrument: Aether/observatory/aeth03_assay_audit.py (39b7f7e85). Fixtures: Aether/test/test_aeth03_assay_audit.py (15 passed).

Conclusion (one of the three the directive offered): **exact after repair, prior results unchanged** -- with one claim withdrawn
and restated.

- Locality holds: 27,000 light-cone flips, no law beyond its declared radius (mov reaches 2, as declared). Every hash key is a
  function of (seed, tick, coordinates, field) only; contest membership is observer-only.
- The hidden path is real and was guarded: rcv twins identical in all five bytes but differing in the received flag produce
  visible differences in 20/20 trials; a bytes-only predicate records 32 locality violations, the assay's full predicate 0.
- WITHDRAWN as stated: "generation = the exact shortest causal chain". A differing neighbour need not be a cause. Counterfactual
  single-parent sufficiency over 2,793 events: the assay's adjacency generation equals the causal generation in 100% (v1), 99%
  (add), 96.5% (mov, rcv OFF), 84% (rcv ON) of events; it is a LOWER BOUND, so every prior secondary/sustained claim was
  conservative and no verdict changes. Joint causation: 2 of 2,793.
- Repairs: carried state compared generically (World.extra); adversarial fixtures; exact causal generation available on demand.

Tasks: none were split into portable units (runs tied to the instrument build that launched them; see CAMPAIGN.md finding 3).
