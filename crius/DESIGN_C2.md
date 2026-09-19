# Crius Campaign 2 -- preregistration: the ACCESSIBILITY FRONTIER (D2)

Currency: 2026-09-19. Written BEFORE any C2 code; committed first. Ruling:
roles/Crius/prompts/2026-09-19_c2_ruling/ (MANIFEST). The frozen C1/C1b
family is CLOSED; its principal result is preserved verbatim in section 0.

## 0. Preserved result (C1/C1b) and the question C2 asks

RELAY establishes that independently useful procedural reuse exists in the
frozen world (gate F/G/H: ARTIFACT_TRANSPLANT 18/18 vs CODE_ONLY 1-5/18,
ablation returns it to CODE_ONLY), but no measurable evolutionary gradient
from ordinary programs to that mechanism was found under the tested VM,
variation operators, search budget, seeds, streams and two budget regimes.
This is not generalised to universal inaccessibility. The critical
observation (C1b Q-c): keeping state is not selected against (41/65
census rows above contemporaries); what is missing is the assembly of a
load-bearing causal chain from ACQUISITION through REPRESENTATION,
RETENTION, ADDRESSING and INVOCATION (and, for chains, COMPOSITION).

C2 question: at what representational and variation granularity does
reusable computation become incrementally selectable? The result sought
is a boundary on a ladder, located by the first rung at which a
reproducible ancestral gradient toward useful persistent computation
appears -- or the finding that none of the rungs produces one.

## 1. What is frozen across the ladder

World RELAY, generator, sealed namespaces (search / qual / gate), C1b chain
budgets {1: 2000, 2: 50, 3: 50, 4: 50}, C1_FITNESS (competence first;
unsolved pays full budget; secondary cost term <= 0.5), FAIL sentinel and
strict ACT, telemetry, the s10 control battery, gates A-H, qualification
protocol (final-population ranking; top-3 + 3 contemporaries + 3
ancestors + best-ever; 3 sealed streams). Block ids remain values
(CRIUS-28 untouched). Only the SUBSTRATE (VM instruction set + artifact
representation) and the VARIATION protocol move, rung by rung.

Stated consequence carried from C1b: under 50-interaction chain budgets a
Player solves chains only by planning in the head (or a partial-progress
signal it discovers), never by physical trial of stored procedures. The
competence gradient (+1 per chain task) is therefore reachable only by
rungs that make mental simulation local; the earlier rungs can earn only
the cost term on single tasks (<= 0.5 fitness over a lifetime). This is
named "fitness granularity" and is a fourth interpretation category
alongside the ruling's three (section 5).

## 2. Resource invariant (ruling: fix the invariant, not the behaviour)

Every store object charges a METADATA size on creation: records, blocks
and typed procedures cost 2 bytes each plus their payload, counted against
the 4096-byte capacity; a block's instructions cost 4 bytes each as
before. Zero-payload objects are therefore bounded (2048 per lifetime at
most, fewer with payload). Ids stay monotonic values: clocks, counters and
id arithmetic remain legal. CRIUS-28 (block-id clock, C0) and CRIUS-31
(record-id clock, C1b) are added to crius/fixtures/ with signature tests
that must still reproduce under the new accounting (the record clock
needs ~150 ids per lifetime; capacity allows it).

## 3. Streams and takeover (ruling: no single-stream lottery)

Every comparison uses TWO paired common-random streams per iteration
(seeds S(i, 1), S(i, 2) in the search namespace; the whole population,
parents included, on both); fitness is the mean. TAKEOVER CHECK: after
truncation on the paired mean, any child that would displace a member of
the current elite is evaluated together with the member it displaces on
an independent CHECK stream S(i, 3); the child enters only if its check
fitness >= the displaced member's. Every displacement decision is
recorded (child, displaced, paired fitnesses, check fitnesses, outcome)
in takeovers.jsonl. Prediction: drift below the seed (C1b S3, 2 of 9
runs) disappears (<= 1 of 9 runs per rung ends below the seed).

## 4. The substrate ladder (rung = which links of the chain are single instructions)

Links: L1 acquisition (action id -> primitive), L2 representation (a
procedure relative to an argument), L3 retention, L4 addressing (which
procedure and argument for this task), L5 invocation with an argument,
L6 composition (chains: planning in the head).

  C2-A  C1b as is. No link is local. Re-run under the section-3 protocol
        so its dynamics are comparable (3 arms x 3 seeds).
  C2-B  L1 + L2 + L3 + L5 local; L4 and L6 remain the program's job.
        New typed artifact PROCEDURE = list of (kind, offset) steps. New
        instructions: PREC_BEGIN; PREC_END r (the actions emitted between
        the two are stored as primitives relative to the FIRST step's
        position, as one procedure object in the artifact store; r = its
        handle); PINVOKE h, a (executes procedure h with argument a:
        each step (kind, off) -> primitive (kind, (a+off) mod 4) -> the
        action id that performs it, via the CALIBRATION TABLE). The
        calibration table is an artifact object maintained BY THE
        SUBSTRATE: every executed action's revealed primitive (INPUT
        last_primitive is a new observation field: the world reports what
        an executed action did, as (kind, pos)) is written into it. It
        lives in the artifact store like any block, so FRESH / RESET /
        SCRAMBLE / ABLATION / TRANSPLANT act on it; PINVOKE of a step
        whose primitive has no known id sets status 1 and emits nothing.
        Invocation stays "coordinated": a program must still decide WHICH
        procedure and argument (L4) and, for chains, in what order (L6).
  C2-C  C2-B + L6 made local: PSIM r_out, h, a, r_in applies procedure h
        with argument a to the object in r_in IN THE HEAD (no
        interaction; compute cost = steps of h) and returns the result.
        PMATCH r, h, a = 1 iff PSIM(h, a, current) == target. With PSIM a
        chain plan is a nested loop over (h, a) pairs with EQ against the
        target: every piece is one instruction, and no complete reuse
        program is provided.
  C2-D  C2-C substrate + a variation change: the recombination arm's
        donor pool is the union of the population and the frozen PARTS
        of section 5 (recorder-only, invoker-only, planner-only), so
        splice can bring a part into a lineage. The PARTS never enter the
        population as candidates; they are donors only. This is the
        ruling's "independently evolvable parts plus generic
        recombination" as a diagnostic treatment.
  Each rung's instruction set is a superset of the previous; the ENUMERATE
  seed is unchanged and uses none of the new instructions. Mutation draws
  opcodes uniformly from the rung's set (so a PREC/PINVOKE/PSIM appears by
  one edit).

## 5. PARTS diagnostic (central; controls, never population members)

Frozen hand-written partial mechanisms, each in bytecode, each the
ENUMERATE seed plus one link:
  P-CAL   rung A: calibrator only -- probes 12 actions once, stores the
          id -> primitive map in cells; never uses it.
  P-REC   rung B: recorder only -- after each enumeration success, re-
          executes the solving sequence inside PREC_BEGIN/END (pays the
          re-execution; never invokes).
  P-INV   rung B: invoker only -- before enumerating, tries every stored
          procedure with every argument (physical trial, <= 12 x 4
          invocations on single tasks); records nothing. Measured from
          scratch (empty store: equals the seed plus overhead) and WITH
          the positive control's transplanted procedures.
  P-REC-INV rung B: recorder + invoker (physical trial only).
  P-PLAN  rung C: planner only -- given procedures exist (transplant),
          loops PSIM over (h, a) and (h, a, h', a') and executes the first
          match; records nothing.
  P-REC-INV-PLAN rung C: the complete mechanism (positive control at rungs
          C and D; NEVER seeded into search).
For each partial and its immediate ancestor (the seed, or the partial one
link shorter) we measure on the gate streams 301-310 (controls only):
  selective value  = mean paired-stream fitness(partial) - fitness(ancestor)
                     with its sign's reproducibility (streams where the
                     sign holds / 10), delta solved, delta charged cost
  structural distance = instruction-level edit distance from the seed
                     (and from the ancestor) to the partial
  transplant value = selective value when the store is pre-loaded with the
                     positive control's artifacts (isolates L4/L5 from L2/L3)
Interpretation (ruling's target, plus one):
  parts individually non-beneficial            -> coordination / valley
  parts beneficial but do not compose          -> variation / linkage
  gradient develops then stalls                -> localise the transition
  parts save cost but move fitness < the stream noise -> fitness granularity

## 6. Search protocol per rung

Arms random / seeded / recombination (splice from population) at A, B, C;
at D the recombination donor pool adds the PARTS. 3 seeds x 300
iterations x (8 + 24), paired streams + takeover check (section 3).
Qualification and battery as C1b. Tracing adds PREC_BEGIN/END, PINVOKE,
PSIM, PMATCH counts; the invocation log records (handle, argument,
emitted actions) for PINVOKE.

## 7. Gates per rung

Gate A-H is run at every rung with that rung's positive control (rung A:
PROCEDURE_REUSE_C1; rungs B-D: P-REC-INV-PLAN, whose artifacts are typed
procedures + the calibration object). F and G are required at every rung
whose semantics changed (B, C): ARTIFACT_TRANSPLANT > CODE_ONLY and
ABLATION_ALL == CODE_ONLY. A rung whose gate fails is not searched.

## 8. Primary readout per rung (the ruling's list)

  structural distance to useful reuse (edits from the seed to P-REC-INV,
    and to P-REC-INV-PLAN); selective value of each partial; frequency of
    persistent-state creation (candidates creating >= 1 procedure/block
    per lifetime); frequency of useful invocation (invocations that
    emitted >= 1 valid action); ancestral trend toward load-bearing
    state (LINEAGE.md gradients); ACCUMULATED vs FRESH (reuse_gain, sign
    reproducibility over 3 sealed streams); transplant and ablation;
    sealed-stream competence; recombination contribution (fraction of the
    top lineage's edits that are splices, and splices from PARTS at D).

## 9. Predictions (written before any rung is built; each can be lost)

  R1 Rung A under paired streams + takeover: no gradient (replicates
     C1b); <= 1 of 9 runs ends below the seed on sealed streams.
  R2 PARTS at rung B: P-REC has negative selective value (re-execution
     cost, no benefit); P-INV from scratch ~ 0, positive with transplant
     on single tasks only; P-REC-INV positive on single tasks only
     (delta solved 0, delta fitness between +0.05 and +0.3), sign
     reproducible on >= 8/10 streams. Category: fitness granularity for
     the cost term, coordination for the competence term.
  R3 Rung B search: persistent-state creation frequency rises (PREC is
     one edit) to > 20 percent of candidates; useful invocations appear
     (> 0 in > 5 percent of candidates); still no reproducible
     ACCUMULATED > FRESH with competence kept, because L4 (addressing)
     and physical trial cannot solve chains within 50.
  R4 Rung C: P-PLAN with transplant and P-REC-INV-PLAN have large
     positive value (+20 tasks); seeded and recombination searches do
     NOT assemble PSIM planning within 300 iterations in 3/3 seeds each
     (the pair loop is ~10 coordinated edits with no reward until
     complete).
  R5 Rung D: splice from PARTS donors produces at least one lineage with
     reproducible ACCUMULATED > FRESH and competence kept in >= 1 of 3
     seeds. This is the frontier prediction: the boundary lies between
     "each link is one instruction" (C) and "parts exist as donors" (D).
     Losing R5 means even donor-level parts do not compose under splice
     -- a linkage result, and the most informative failure available.
  R6 Structural distance from the seed to P-REC-INV falls from >= 40
     edits (rung A, the full mechanism in raw bytecode) to <= 12 (rung
     B) and to P-REC-INV-PLAN <= 25 (rung C).

## 10. What is frozen at each rung's freeze commit

configs/c2a.json .. c2d.json (hash in every receipt), the substrate
version string per rung (in the world/VM fingerprint), the PARTS programs
and their hashes, the paired-stream/takeover protocol, this file's
predictions. Nothing in section 1 changes at any rung.
