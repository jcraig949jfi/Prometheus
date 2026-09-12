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
    N3 Go-Explore: DONE 2026-09-12 05:0xZ at its evidence boundary (one cut; 1 organ NO CURRENT CONSUMER,
    1 pressure delivered #202 hostable UNKNOWN, 1 recurrence of an inventory organ, 1 coupled cluster).
    In flight now: NOTHING. RULING 2026-09-12 (roles/Nyx/prompts/2026-09-12_ruling_n3_accepted_n4_closed/): N3 ACCEPTED; N4 CLOSED;
    production loop CLOSED. ATTACK EXISTING CLAIMS; DO NOT GROW THE WAREHOUSE. NYX-44 pre-authorized
    on a managed pin (#201); controls FROZEN before any result (ablations/n3_c04_controls.py).
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

    organs delivered                 18  (unchanged: go_explore c04 marked NO CURRENT CONSUMER and NOT delivered)
    organs actually consumed          0
    pressures delivered               8  (#202 resume_from_remembered_places, hostable UNKNOWN, owner candidate named; +3 held)
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

## Recurrence of inventory organs (first instance 2026-09-12)

    go_explore c01 archive admission -> RECURRENCE of organ.map_elites cell replacement (and of h3_replay's admission rule)
    The Chop Shop did not manufacture apparent diversity here; the anti-collection law worked once.

## Three transfer failures, recorded SEPARATELY (ruling 2026-09-12; provisional classes, not ontology)

    TYPE A  interface mismatch at an existing site     c07 (#200): consumer exists; its value geometry does not fit the organ's contract
    TYPE B  no current consumer state                  c04: no site holds the state/value/interface the organ needs
    TYPE C  capability belongs to the environment      c03: reset/resume is the world's; policy + assumption ride on it
    Not collapsed into one bit. nyx.chop/0 unchanged.

## Standing diagnostic: CROSS-LINEAGE ORGAN RECURRENCE (ruling 2026-09-12)

    2026-09-12  go_explore c01 (RL/search) -> organ.map_elites cell replacement by fitness in a behaviour-keyed archive (quality diversity)
                Both ancestries preserved (nyx/specimens/map_elites/, nyx/specimens/go_explore/cuts.json c01).
    Counts as: two independent cuts reaching materially equivalent machinery.
    Does NOT count as: new organ / validation of the existing organ / proof of universality.

## N4 gate (ruling 2026-09-12): CLOSED. Reconsider after ANY of
    A  NYX-44 executable evidence about c04      B  #202 substantive pressure return
    C  another substantive consumer attempt on an existing ORGAN
    D  cross-lineage recurrence gives a concrete reason to test another lineage
    E  the Keeper supplies a more informative experiment
    Availability of another interesting tool is not sufficient.

## The questions that now matter (ruling)
    Can c04 survive executable attack?  (NYX-44; the unique-key-family cheat control especially)
    Can #202 become an operational world pressure?  (decisive: does an EXISTING world supply opaque
      state capture, exact restoration, world-owned novelty accounting, explicit cost -- without
      anyone manufacturing Go-Explore around the pressure)
    Can any ORGAN become genuinely CONSUMED?

## Ruling 2026-09-12 (roles/Nyx/prompts/2026-09-12_ruling_c07_c03_c01_hold/): shrinker organ dispositions and held routes

    c07  INTERFACE_INSUFFICIENT stands. No tree<->sequence encoder. No new Hypothesis organs.
         REOPEN ONLY IF an EXISTING consumer already has: (1) a sequence-valued object; (2) a Boolean
         preservation predicate; (3) a natural existing order / one-line reversible representation;
         (4) a real minimisation objective not already solved as well by its baseline. Never manufactured.
    c03  HOLD -- unless an existing adaptive delete/repeat consumer appears naturally.
    c01  HOLD, untested -- unless a live consumer specifically asks for it.
    Held routes: Proteus halves of #189/#190; Diomedes half of #192 (never booted). Not delivered.
    No more anatomy until a consumer creates demand.

## RE-PREMISE 2026-09-12 ~05:10Z -- Keeper directive (roles/Nyx/prompts/2026-09-12_directive_catalogue_loop/)

The Keeper: "loop until the end of time building out this database, graph or tensor.
Pull from existing databases, lists, wikis first then, chop chop chop. The smallest
components computable. Human descriptions are OK but the Classification for
searchability is the real gem ... Imagine a tool seeing a weird solution produced by
an organism to survive. We want to match that against a similar set of known
algorithmic bits."

How this sits against the standing rulings, stated plainly:
  - N4 gate condition E (the Keeper supplies a different experiment) is met by this
    directive. The production loop reopens FOR THE CATALOGUE.
  - The product changes: from ORGANs delivered to consumers (fitness = consumption)
    to a CATALOGUE of algorithmic bits with behavioural classification (fitness =
    a held-out description of a known mechanism retrieves it; a recurrence is
    detected by classification, not by name). The anti-collection law is kept in
    its adapted form: a bit that cannot be retrieved by a behavioural query is
    inventory failure; the count of bits is not a score.
  - Delivery of ORGANs to consumers stays ON DEMAND ONLY (ruling 04:50Z); the
    catalogue does not deliver, it answers queries.
  - Provenance grades travel: list/wiki-seeded bits are T2 (human description of a
    known mechanism) until a chop or a run makes them T1; the grade is a field.
  - Recurrence (N2/N3 rulings) becomes the catalogue's core operation: two bits with
    the same behavioural signature are one bit with two ancestries.
Layout: nyx/catalog/ (schema, search, seed, loop); records under nyx/catalog/bits/.

## Catalogue loop state (refreshed at each checkpoint)

    2026-09-12 ~05:45Z  bits 140 (T1 16 / T2 124); sources: wikipedia_list_of_algorithms 917
    (601 pending), wikipedia_list_of_data_structures 220 (pending); vocabulary v0.4; planted
    controls 10/10; residual recurrence pairs 6 (named in schema changelog / LOOP_LOG).
    Fitness (adapted anti-collection law): every planted behavioural query retrieves its bit
    without the name -- YES at this checkpoint. Bits with no behavioural query yet: most;
    the planted set grows only from real query needs, not per bit.
    checkpoint after batch 6: bits 190; pending in list_of_algorithms shrinking; loop self-paced (ScheduleWakeup), one batch per wake.
    2026-09-12 13:21Z after batch 8 (numerical: DE solving / elementary functions / geometric, 51 decisions: 26 BIT, 12 INSTANCE_OF, 11 NOT_A_BIT, 2 DEFER): bits 231 (T1 16 / T2 215); list_of_algorithms pending 403; controls 10/10; recurrence groups 9 -- new group = the two IMPLICIT one-step advances (slope at the new point vs mean of old and new slopes): same signature, differ in order of accuracy and damping, which the vocabulary does not carry; accepted, not a vocabulary change (no control failed). Also this tick: Techne #203 processed, NYX-44 run as frozen -> CANNOT_INSTANTIATE (loky), c04 unchanged.
    2026-09-12 13:50Z CHECKPOINT after batch 9 (interpolation / linear algebra / Monte Carlo / root finding, 62 decisions): bits 268 (T1 16 / T2 252); list_of_algorithms 341 pending; controls 10/10; recurrence groups 14 (five new this batch, all accepted, none a vocabulary change); cross-lineage recurrences recorded via related RECURRENCE_OF: fewest-options-first (Warnsdorff = DLX = minimum degree), bracket halving (binary search = bisection = unimodal bracket), Gauss-Seidel = min-conflicts (= Gibbs, stochastic), Metropolis = annealing acceptance, power iteration = score propagation. Next: batch 10, remaining Computational mathematics.
    2026-09-12 14:14Z after batch 10 (abstract/computer algebra + geometry, 46 decisions: 29 BIT, 3 INSTANCE_OF, 12 NOT_A_BIT, 2 DEFER): bits 297; list_of_algorithms pending 295; controls 10/10; groups 15 (new: back-projection vs separable distance transform -- both axis-wise passes over a grid). Recurrences recorded: completion (Buchberger = Knuth-Bendix = lazy constraint addition), leading-term cancellation (polynomial division = integer long division), guess-and-square (Chan = iterative deepening), farthest-point split (Quickhull = pivot partition), advance-the-smaller (rotating calipers = merge-join), sweep with active order (Bentley-Ottmann = Fortune), neighbour-mean smoothing = Gauss-Seidel sweep. Keeper re-issued the c07/c03/c01 hold ruling verbatim; recorded in its MANIFEST; nothing changed.
    2026-09-12 14:45Z after batch 11 (cryptography, 53 decisions: 24 BIT, 17 INSTANCE_OF, 11 NOT_A_BIT, 1 DEFER): bits 321; list_of_algorithms pending 242; controls 10/10; groups 19 (four new, incl. the four block-cipher round structures sharing one signature -- accepted, not a vocabulary change). LOOP STOPPED by the Keeper at this break; external status report roles/Nyx/reports/STATUS_REPORT_2026-09-12_external.md.
