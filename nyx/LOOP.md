# The Chop Shop loop (opened 2026-09-11 under the production trial, Phase VII)

Authority: roles/Nyx/prompts/2026-09-11_production_trial/PROMPT_verbatim.md.
Procedure per specimen: nyx/KNIFE.md ("How the knife is applied").
Bookkeeping per specimen: nyx/specimens/<name>/cuts.json + cutledger.
Program-level counters: the ANTI-COLLECTION table below, refreshed at each
journal close.

## Work-in-progress cap (from observed consumer throughput, not ambition)

Observed 2026-09-11: 10 deliveries (6 pressures to Vivarium, 4 reports to
Archaeon) over ~7 hours; 0 substantive returns. CORRECTION 21:10Z: Vivarium
IS active in comms since 17:05 local (python -m comms who; m1-416d588d);
the earlier claim that it had never booted was stale by four hours.
Throughput observed is still 0 per hour, but the consumer exists.

    CAP = 1 specimen in flight until the first substantive return exists.
    In flight now: lean_simp (CUT-3 done; awaiting #175 / #176).

When the first return arrives the cap is recomputed as
    ceil(returns per day / 1) bounded to [1, 3]
and written here with the date.

## STOP / escalation status (checked at every journal close)

    consumer backlog makes inventory useless   WATCH (downgraded 21:10Z from TRIGGERED-CANDIDATE):
                                               6 pressures + 4 organ reports, 0 consumed,
                                               BUT Vivarium booted at 17:05 and #175 is
                                               4h younger than that. Reported to the operator;
                                               loop OPEN at cap 1; HELD until a return or a
                                               ruling, because the cap rule needs a throughput.
    inherited rate high after knife refinement  NOT YET TESTABLE (K1 has not been applied
                                               to a new specimen)
    organs repeatedly fail independent test     NOT YET TESTED (0 independent tests attempted)
    pressures leak their solution               NO RETURNS
    convergence only by adding human judgment   watch: CUT-2 was all judgment
    same cut pattern regardless of specimen     watch: 3 specimens, all cut to
                                               store + traversal + guard shapes
    rediscovering taxonomy not mechanisms       watch: 8 dispositions in use
    provenance cannot be preserved              NO (all pins cited; one management gap)
    Nyx designing descendants                   NO (AMBIGUITY.md combinations recorded, not built)

## Specimen selection (criteria from the prompt; choose from evidence)

Prefer: demonstrated capability; strange mechanism; strong empirical
performance; architectural difference from current inventory; useful
failure landscape; suspected hidden human prior; mechanisms that appear
transferable; pressure likely separable from mechanism. Vary lineages.
Periodically: something hard to decompose; Prometheus machinery; a
specimen expected to yield NOTHING.

Lineages cut so far: quality diversity (MAP-Elites), program synthesis /
compression (DreamCoder), theorem proving / symbolic (Lean simp). The
next specimens must NOT be in those three.

## Next specimens, preregistered here and NOT started (cap = 1)

N1  hypothesis (Python property-based testing) -- the SHRINKER only.
    Why: Techne holds receipts (techne/acquisition/checks/hypothesis_*,
    fixtures/hypothesis_*), so the pin is managed and the Techne gap of
    lean_simp does not recur; lineage is testing/search, absent from the
    inventory; the mechanism (shrink toward a minimal failing example by a
    fixed order over a choice sequence) is strange, has a suspected human
    prior (the shrink order), and the pressure ("a world that rewards the
    smallest witness, not the first") looks separable. Expected yield:
    1 organ, 1 pressure, 1 hidden prior.
N2  diomedes_k0_coordinate_census (endogenous; seat PARKED 2026-09-02).
    Nominated as the specimen expected to yield NOTHING (a census script
    is DATA tooling by construction). Negative chops matter; a DEAD_CUT
    with a receipt is the deliverable.
N3  go_explore (NYX-07 as queued) -- RL/search; Archaeon H3 consumer;
    the "deterministic reset" prior. Third because two RL-adjacent
    archive specimens (MAP-Elites, then this) in four would be the
    "same conceptual family" the prompt warns against.

Rejected for now: z3 / cvc5 / lean-as-checker (same lineage as the
proving specimen: hold until the theorem-proving cut has a return);
field_simp (DEAD_CUT already; nothing to cut); POET (H4 has no live
consumer this week).

## ANTI-COLLECTION table (program level; refreshed at journal close)

    organs delivered                 12  (MAP-Elites 3, DreamCoder 3, lean_simp 8 at CUT-1 -> 4 at CUT-3; counted as delivered 8)
    organs actually consumed          0
    pressures delivered               6  (+1 held, +1 candidate not written)
    pressures operationalized         0
    cuts falsified                    1  (c23 negative control; plus P5 as a prediction)
    cuts materially revised          16  (lean_simp 15 + 1; MAP-Elites/DreamCoder had no second cut)
    independent behaviours reproduced 0  (every run was inside the ancestor)
    downstream experiments enabled    0  (none run by a consumer)
    downstream failures made cheaper  0  (no consumer has failed on a Nyx artefact yet)
    inherited boundaries discovered  22  (lean_simp 20 + 2; stamped, not estimated)
    cheat paths closed                1  (D3 planted loop fires the budget)

Reading: the warehouse has grown; nothing has been consumed. This table
is why the loop is held at cap 1 and the STOP condition is reported
rather than argued away.
