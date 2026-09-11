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

    CAP = 1 (operator ruling 2026-09-11 evening: exactly 1; not recomputed).
    In flight now: N1 hypothesis shrinker (opened after #182 was processed).
    WAITING-ON-CONSUMER (not WIP): lean_simp (#176 open at Archaeon; #175
    RETURNED by Vivarium #182 at 21:23Z, 0.5 h after posting), map_elites
    (#44 returned: world sketch, blocked on the objective family), dreamcoder
    (#52 returned: vacuous on the live corpus; executor half exists).
    N2, N3: CLOSED by ruling. METABOLIC GATE after N1: one substantive return
    exists (#182), so N2 is to be ASSESSED, not assumed.

When the first return arrives the cap is recomputed as
    ceil(returns per day / 1) bounded to [1, 3]
and written here with the date.

## STOP / escalation status (checked at every journal close)

    consumer backlog makes inventory useless   CLEARED 21:23Z for Vivarium (#182 returned on all six
                                               pressures); OPEN for Archaeon (#45 #53 #176 unanswered).
                                               Previously WATCH (downgraded 21:10Z from TRIGGERED-CANDIDATE):
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
    pressures operationalized         0  (6 returned: 1 world sketch blocked on semantics, 1 vacuous, 4 unhostable -- no rewriting substrate)
    cuts falsified                    1  (c23 negative control; plus P5 as a prediction)
    cuts materially revised          17  (lean_simp 15 + 1 + orientation cheat read-out on #182; MAP-Elites/DreamCoder annotated, not recut)
    independent behaviours reproduced 0  (every run was inside the ancestor)
    downstream experiments enabled    0  (none run by a consumer)
    downstream failures made cheaper  1  (#44: eligibility count moved into Vivarium PREFLIGHT -- a 0 rejects the spec at admission instead of after a run)
    inherited boundaries discovered  22  (lean_simp 20 + 2; stamped, not estimated)
    cheat paths closed                1  (D3 planted loop fires the budget)

Reading (21:23Z): the warehouse has grown; six pressures have been READ and returned, none operationalized; nothing has been consumed. This table
is why the loop is held at cap 1 and the STOP condition is reported
rather than argued away.
