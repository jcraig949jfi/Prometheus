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
    N1 hypothesis shrinker: NATURAL STOPPING POINT reached 23:06Z (CUT-2 written;
    no CUT-3 -- no return, no patched-build ablation); deliveries #190 #191.
    N2 diomedes K0 census: DONE 2026-09-12 00:21Z as a NEGATIVE CHOP (ruling): 0 organs,
    0 pressures, boundary VALID, null SUPPORTED; one owner finding (#192).
    In flight now: NOTHING. General loop CLOSED; N3 requires a ruling.
    RULING 2026-09-12 (metabolic gate holds): HOLD THE WAREHOUSE; ATTACK EXISTING
    CLAIMS (NYX-32/37/38 on existing specimens only, no new inventory); REPAIR
    ROUTING; WAIT FOR DIGESTION. Routing repaired #197 (Proteus and Diomedes have
    NEVER BOOTED; #191 lacked a concrete consumer, interface and requested action).
    WAITING-ON-CONSUMER (not WIP): lean_simp (#176 open at Archaeon; #175
    RETURNED by Vivarium #182 at 21:23Z, 0.5 h after posting), map_elites
    (#44 returned: world sketch, blocked on the objective family), dreamcoder
    (#52 returned: vacuous on the live corpus; executor half exists).
    N2: done (negative). N3: CLOSED by ruling. METABOLIC GATE (23:06Z): one substantive return
    exists (#182, Vivarium on the six pressures). Assessment: #182 returned
    on PRESSURES and licensed a routing rule; no ORGAN has been consumed and
    no pressure operationalized; N1's own deliveries (#190 #191) are minutes
    old. Nyx's reading: N2 is NOT yet licensed by consumption evidence; the
    gate is the operator's or a return's to open. HOLD.

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

    organs delivered                 18  (MAP-Elites 3, DreamCoder 3, lean_simp 8, hypothesis_shrinker 6 at CUT-2 via #191)
    organs actually consumed          0
    pressures delivered               7  (#190 to Vivarium+Proteus, owner named; +2 held: mutual_normalisation, encoding-decides-reachability)
    pressures operationalized         0  (6 returned: 1 world sketch blocked on semantics, 1 vacuous, 4 unhostable -- no rewriting substrate)
    cuts falsified                    2  (lean c23; shrinker c08); negative chops completed 1 (census: expected zero -> zero)
    cuts materially revised          17  (lean_simp 15 + 1 + orientation cheat read-out on #182; MAP-Elites/DreamCoder annotated, not recut)
    independent behaviours reproduced 3  (hypothesis_shrinker c01 c03 c07: standalone runs with no engine imported; RECEIPT_N1)
    downstream experiments enabled    0  (none run by a consumer)
    downstream failures made cheaper  3  (#44 preflight count; Techne target-7 located; Diomedes bootstrap zero-width on power-of-two cluster counts, #192)
    inherited boundaries discovered  32  (lean_simp 22; shrinker 10, of which 2 inherited-AND-supported, 0 falsified)
    cheat paths closed                5  (lean D3; shrinker P-a5, N-a/P-a1, N-e; census: the instrument's own zero-error channel found by running it off its fixture)

Reading (21:23Z): the warehouse has grown; six pressures have been READ and returned, none operationalized; nothing has been consumed. This table
is why the loop is held at cap 1 and the STOP condition is reported
rather than argued away.

## Metabolic states of every delivery (ruling 2026-09-12; never one bit)

    #44 #52 #175  Vivarium         REJECTED_BLOCKED (#182: attempted; substrate absent/unowned or corpus vacuous or semantics undeclared) -> CAUSED PROCEDURE CHANGE (K9 K10), not a downstream experiment
    #45 #53 #176  Archaeon         DELIVERED, no return
    #189          Proteus+Vivarium question, no answer
    #190          Vivarium+Proteus DELIVERED (pressure, owner named), no return
    #191          Archaeon         DELIVERED, no return
    #192          Diomedes+Archaeon DELIVERED (failure finding), no return
    ORGANs CONSUMED 0; pressures OPERATIONALIZED 0.

## The four questions, recorded narrowly (ruling 2026-09-12)

    1 Can Nyx catch a bad cut?                 YES, on the Lean/simp specimen.
    2 Does a learned knife transfer?           SOME RULES transferred Lean -> Hypothesis;
                                               others correctly did not fire.
    3 Can Nyx refrain from inventing anatomy?  YES on the preregistered Diomedes negative.
    4 Can an ORGAN leave its ancestor and      UNKNOWN. ORGANs consumed: 0. Outranks harvesting.
      cause a useful downstream effect?
    Bounded results. Not "Nyx validated", not "Chop Shop validated", not "decomposition solved".

## Standing diagnostic: PROMOTION TEMPTATION (not a success metric)

Candidates that looked promotable before the decisive control and were refused.
    lean_simp             not counted -- the ledger has no pre-control temptation record
                          (c23 was demoted by a control, but it was not documented as
                          tempted BEFORE the control; the count is not manufactured)
    hypothesis_shrinker   not counted -- same reason (c02 "organ or data?" was a post-hoc
                          attack note, not a pre-control temptation)
    diomedes_k0_census    2 (c02 headroom statistic; c07 identifiability ceiling), each
                          with independent behaviour RUN and refused on the preregistered
                          duplicate control; cuts.json tempted_organ_reading = true
Future specimens record the temptation at the moment it is felt, before the control runs.

## Reopen conditions for N3 (ruling 2026-09-12; ONE suffices)

    A  an ORGAN receives a substantive consumer return
    B  #191 is explicitly rejected because no current consumer can test any delivered organ
    C  evidence that the delivery/interface contract itself prevents consumption
    D  the Keeper issues a new scientific reason
    Status 03:30Z: none met. Routing repair #197 asked Archaeon to put B on the record.
    04:00Z: B SATISFIED (#200: no current consumer can test any delivered Nyx ORGAN today). N3 OPENED by ruling
    roles/Nyx/prompts/2026-09-12_ruling_n3_open/ with a new question: does Nyx extract organs whose INTERFACE
    GEOMETRY is separable from the ancestor? Transfer-interface side ledger required before CUT-1.

## Class counted separately (ruling): useful outcomes with no ORGAN and no PRESSURE

    downstream failures made cheaper   3   (#44 preflight count; Techne target-7 located;
                                            Diomedes bootstrap zero-width, scope exactly n = 4 8 16 32
                                            observed, 5 17 24 100 fine -- not generalised)

## Metabolic measurements kept SEPARATE (ruling 2026-09-12)

    runnable outside the ancestor      3 organs (shrinker c01 c03 c07; RECEIPT_N1)
    attempted by a downstream consumer 1 (c07, #200)
    consumable by an existing site     0
    CONSUMED (output used downstream)  0
    first organ consumer return        #200, 2026-09-12 03:42Z, 4.6 h after #191
    The c07 lesson as ruled: 'runnable outside the ancestor' != 'consumable by an existing downstream site'.
    NOT learned: flat-sequence organs are bad; tree organs are better; seek Prometheus-shaped organs.
