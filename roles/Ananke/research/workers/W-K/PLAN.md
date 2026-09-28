# W-K PLAN: minimum evidence that an intervention reached its mechanism

Worker W-K. Namespace 0x5F0 (specimen worlds = assays.world_seeds(0x5F0, 64),
32 mirror pairs; 99% pair bootstrap via c1b.ci / assays.pair_ci). CPU only,
torch.set_num_threads(2). No lease needed (single 2-thread process).
Frozen: 2026-09-28, before any check is scored. Context read before PLAN:
COMMON_RULES*, the W-K brief, W-D REPORT.md (allowed hypothesis source),
engine/lens/plants/physics/rng/envs/assays/c1b source,
tests/test_lens_instruments.py, pte/C1_ERRATA.md, research/instruments/*.md.
NOT read: SYNTHESIS*, C1B_REVIEW*, PTE_ENGINE_CARD.md, ARC3_PRIORITIES.md,
other workers' reports (except W-D).

## Question
What is the minimum evidence sufficient to claim an intervention actually
reached the candidate mechanism? Build adversarial fixtures (broken arms)
each with a VALID twin, run a set of candidate checks over all of them,
and measure which check catches which fixture, at what cost.

## Objects
A FIXTURE = (physics, env, specimen genome, harness = "the arm's own code",
arm spec, declared pathway, declared factor, declared state variable,
footprint (ticks x sites), ground truth BROKEN/VALID).
The harness is my code in this directory (a correct reference harness plus
bugged variants). The engine is never edited; bugs live in harness or spec.

Reading on the specimen (c1b rules): EFFECT = c1b.drops (point drop >= .10
and lo99 of diff < -.05); NULL = c1b.intact (lo99 of diff >= -.10);
otherwise AMBIG.

Ground truth BROKEN := the arm as implemented could not have affected the
declared pathway in this physics, OR the declared factor was not applied,
OR the outcome is determined by something other than the declared factor
(wrong targets, seeds, probe side-effect, forced by the readout).
VALID := declared factor applied as declared, only it differs from
control, the physics reads the targeted variable, and the reading is
specific (a true positive or a true, non-vacuous null).

## Fixtures (B = broken, V = valid)  [W-D case in brackets]
WIN-B   [1a] relay_flood, c1b_da physics (delay==delta==4), RELAY d1 delta4
        iti50; drop_packets over [t0, ro).            pathway transport
WIN-V        same, window [t0, ro].
INERT-B [1b] c1b_da physics + plastic_route=1 (dest_mode all: w never read);
        specimen flood_rwrite = relay_flood + cue-signed routing writes;
        freeze_routing.                                pathway routing
INERT-V      c1b_route physics, route_relay, RELAY d2 delta8 cue4;
        freeze_routing.
UNWIRED-B [2a] rule_switch_hold, c1b_rule physics, HOLD; harness builds
        Controls from an old field whitelist that lacks freeze_rule.
UNWIRED-V    same, correct harness.                    pathway rule
TARGET-B [2b] echo_hold, c1b_echo physics, HOLD; reset_S at mid-gap; the
        harness scores non-normal arms against keyed targets (y * key).
TARGET-V     same, correct harness (TRUE NULL: the bit is in flight).
DEAD-B  [3b] echo_hold HOLD; conditional flush hook "flush in-flight in
        worlds where |sensor S0| > 256" (never true); CRN.  pathway transport
COND-V       same hook, condition "sensor emitted this tick" (fires).
SEED-B  [3a] as DEAD-B but the harness seeds each arm's worlds from the arm
        label (no common random numbers).
PROBE-B [3a/Hauser] as DEAD-B but the condition probe mutates state
        (in-place abs_ on S) -> declared hits 0, outcome changed.
MASK-B  [mis-target] hold_latch, HOLD; reset_S at mid restricted to the
        sensor site, mask built from world 0's sensor for every world.
MASK-V       per-world mask.                           pathway S memory
FORCED-B [4] echo_hold, HOLD; reset_S at the READOUT tick; claim "S
        carries the bit" (the readout reads S0: forced for any genome).
FORCED-V     hold_latch, reset_S at mid-gap.
SAT-B   [5] relay_flood + economy (c_op, c_emit) with e_income cut to a
        value that drains E but never below the emission cost within T;
        claim "energy gates relaying".                 pathway energy
SAT-V        e_income cut to 0 (binding).
V0-WIN   latch_listen (sensor latches SENSE, relays echo the cue back,
        sensor ignores arrivals), HOLD; drop corrected window. TRUE NULL,
        arrivals present at the actuator.
V0-ROUTE flood_rwrite-style decorative cue-independent w writes on
        c1b_route physics (w IS read); freeze_routing.  TRUE NULL expected.
V0-RULE  rule_decor: two identical latch rule programs + a SETRULE toggle;
        freeze_rule. TRUE NULL (r changes, is read, specimen indifferent).
Twins: WIN, INERT, UNWIRED, TARGET, MASK, FORCED, SAT pair 1:1; DEAD, SEED,
PROBE share COND-V. V0-* are extra valid fixtures (true nulls) so that a
check that flags every null is penalised.

Fixture acceptance (construction, BEFORE any check is scored; fixtures may
be repaired and the repair logged, thresholds below fixed):
 - specimen normal competent: mean >= 0.90 (all fixtures);
 - V twins with a real mechanism give EFFECT; V0-* and TARGET-V give NULL;
 - broken fixtures: the bug is present (inspected by construction).
 A fixture that cannot be made to meet these is dropped and reported.
 SEED-B: no outcome is required (its reading is whatever the seeds give);
 I will NOT search labels for a spurious effect (declared now).

## Candidate checks (each returns PASS / FLAG / NA)
K0  NULL strawman: FLAG iff the specimen reading is NULL.
K1  temporal reach (lens.cue_arrival_profile + lens.reach, trial 5):
    windowed packet-drop arms only (else NA). FLAG if reach < 0.5 or None.
K1g generic twin reach: single-cue twins (trial 5 cue negated), normal
    physics; fraction of pairs whose DECLARED variable differs between twins
    inside the arm's FOOTPRINT (ticks x sites; conditional arms: ticks where
    the condition holds on the normal run). NA if the variable never
    differs anywhere; FLAG if fraction < 0.5.
K2  positive control through the ARM'S OWN harness+spec: must-flip plant
    for the declared pathway, at the fixture physics (plant genome-space
    fields, c1b.at_specimen) and env. FLAG unless competent (normal lo99 >
    .55) AND fired (hi99 of diff < -.10) [c1b A3.1]. Plant map:
    transport HOLD echo_hold / RELAY relay_flood; S hold_latch;
    rule rule_switch_hold; routing route_relay; energy relay_flood (RELAY)
    / echo_hold (HOLD).
K2iso same plant through the REFERENCE harness (mechanism in isolation).
K3  arm identical (trace, every world, CRN): FLAG if identical.
K3b arm identical (per-world state digest + trace; c1b no-op guard).
K3c pair coverage: FLAG if < 50% of pairs differ from normal (trace).
K4d self-reported applied count (what the harness says it did): FLAG if 0.
K4c counterfactual applied count: each tick, a shadow world restored from
    the arm world with default Controls/base physics/no hook; FLAG if the
    arm's post-tick(+hook) state never differs from the shadow.
K5  state-change of the declared variable, arm vs normal, over the run:
    FLAG if it never differs.
K6a arm-diff of actual inputs: physics, genome, world seeds, schedule,
    targets y, scored mask, readout ticks, actual Controls; FLAG if
    anything other than the declared factor differs.
K6b declared factor present in the engine's actual configuration
    (World.ctrl / World.ph / hook installed): FLAG if absent.
K7  could-fail counter-plant (must-not-flip): a competent plant that does
    NOT use the declared pathway, through the arm's harness+spec; FLAG if
    not intact (lo99 of diff < -.10). NA if no such plant for the env
    (RELAY has no non-transport solver) or it is not competent.
    Map: transport HOLD hold_latch; S echo_hold; rule hold_latch;
    routing relay_flood; energy HOLD hold_latch / RELAY NA.
K8s specimen scramble of the declared variable at the footprint (uniform
    random values): FLAG if the trace is unchanged in every world.
K9  sham identity: the arm's own code with the declared factor neutral
    (Controls field default / physics override removed / condition forced
    False, probe kept); FLAG if trace OR scored per-world accuracy differs
    from the normal run in any world.
Cost per check: engine runs (World episodes) and wall seconds, recorded.

## Scoring rule (frozen)
For each check: catch = #BROKEN with FLAG / #BROKEN (10);
false alarm = #VALID with FLAG / #VALID (11). NA is reported separately and
scored two ways: lenient (NA = not flagged) and strict (NA = FLAG).
Primary metric: Youden J = catch - false alarm (lenient). A check is
SUFFICIENT for a fixture class when it FLAGs the broken fixture and does
not FLAG its twin. Minimum evidence set = smallest (by total wall cost)
set of checks whose OR catches every BROKEN fixture while FLAGging no VALID
fixture; computed by exhaustive search over subsets of checks with 0
false alarms individually (checks with any false alarm may enter only if
no zero-FA cover exists, and that is reported). Class -> required-check
mapping reported from the matrix. Hypothesis from W-D to test: "plant
through own code + reach counter; arm-diff; could-fail counter-plant;
identical-arms alarm cover all shapes; no single check is universal".
Prediction (mine, before running): K0 J ~ 0 (penalised by V0 and positive
broken fixtures); K3 catches UNWIRED/DEAD/INERT but false-alarms on V0-WIN
and V0-RULE; K2 is the best single check but misses TARGET, SEED, PROBE,
FORCED; K7 is the only catch for FORCED; K6/K9 are the only catches for
TARGET/SEED; no single check exceeds J = 0.7.
