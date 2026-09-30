# W6 design notes (HT-55162c0ac0, P3v2)

Layer: implemented candidate (controls only). No treatment reading exists.

## What it tests

M12 via lens L4's comparison-against-a-simpler-baseline logic: can
finite-time co-divergence of perturbations recover which elements
interact when the interaction is XOR-like (partners pairwise
uncorrelated), with an unstructured global leak present? Baseline =
correlation grouping (M12's stated simpler alternative).

It can fail cleanly in two distinct ways: F1 (the leak spreads
perturbations as fast as the structured coupling, so co-divergence no
longer isolates groups) or F2 (correlation grouping does as well, so the
XOR construction did not hide the structure and FTLE adds nothing). The
modulator's allocation step in M12 is not tested; only the measurement
primitive (the Chaos x Cognitive-Load part) is.

Honest limit, stated in the spec's alternative_explanation: a pass would
show that intervention (perturbation) beats observation (correlation) in
this carrier, not that chaos is necessary to measure interactivity. A
contracting-carrier knockout would be the next world if this passes.

## Why it avoids the earlier failures of this program

- The positive control is a construction (leak removed) under which
  success follows from the topology, not from the hypothesis; it reaches
  S1 = 1.0 and S2 = 0.979 on all 10 seeds' mean (FTLE ARI = 1.0 on every
  seed).
- Clauses are seed means, not per-seed maxima; the twins sit near chance
  (S1 0.019 / -0.033, S2 0.024 / -0.059), so a single lucky seed cannot
  break a bound.
- Control (correlation grouping) and null twin (random partners) are
  different constructions.
- The substrate is not one in which the claimed resource is trivially
  sufficient: the leak is a real competitor to the structured coupling.
- Revision 1 removed a leak strength (0.10) at which the twin synchronised,
  which would have made a failure uninformative.

## Ambiguities resolved

1. "Positive control (effect present by construction)": the same world and
   readouts with the one nuisance (leak) removed, so the partition is
   recoverable by topology.
2. "CHEAT detected": evaluator registers success when the nominal
   partition is injected as the FTLE result.
3. Number of clusters is given to the clustering (4): the claim is about
   which elements group, not about estimating the count.
4. Between F and S thresholds (FTLE ARI 0.3 to 0.8, or gap 0.2 to 0.5)
   the reading is INCONCLUSIVE.
5. The nominal partition is the scoring target in every arm including the
   twins, so the twins measure chance agreement with it.
6. Lens: L4 is listed because it targets M12; its specific context-table
   machinery is not used (the observable is a grouping ARI).
