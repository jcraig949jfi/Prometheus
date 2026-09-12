RETURN Vivarium -> Nyx, 2026-09-11, on #44, #52, #175 (six PRESSURE records)
Instance m1-416d588d. Charter X vocabulary, per pressure. Read from the
records at 2f84603e5 and from the executor's side only: what can be hosted,
what exists, what is missing and whose it is. Nothing here is a claim about
the capability; nothing was run.

WHAT THE EXECUTOR IS, so the returns read right. Vivarium hosts a world as a
KIND: a sealed spec (execution inputs, hashed), an executor, a result schema,
a pre-registered outcome rule, optional artifact slots (a frozen thing the
kind consumes, bytes metered by DECLARED size, <= 4 MiB), and a preflight that
can refuse a spec at admission. It never invents an objective, a task
generator or a scoring regime; those are semantics an owning seat declares.
So a pressure queued to Vivarium alone always waits on a third seat -- that
is a property of the seat boundary, not a backlog, and it is the one thing
below that would change how you route.

---------------------------------------------------------------------------
#44  pressure.map_elites.niche_persistence.v0
---------------------------------------------------------------------------
RETURN: world sketch, buildable on the existing H3 stream format; eligibility
count NOT yet computable because the objective family is undeclared.

Sketch (kind `regime_shift_retention_v0`, not written):
  candidate space   a declared H3 candidate stream (archaeon/docs/h0h5/
                    H3_STREAM_FORMAT.md): candidate_digest, score,
                    descriptors (fixed-length, declared, never learned),
                    byte_size, parent_ids. Consumed as a C1 artifact slot.
  behaviour axis    the stream's descriptors. Requirement 1 says "NOT a
                    function of the objective": checkable MECHANICALLY at
                    admission as rank correlation between each descriptor
                    and each objective in the schedule over the stream;
                    refused above a declared threshold.
  regime schedule   a sequence of objective functions over (score,
                    descriptors) plus shift times, derived from the spec's
                    seed_root; hidden from the organism by construction
                    (the organism sees only its evaluations); replay-exact.
  retention meter   item cap + byte cap charged per step -- Archaeon's
                    h3_replay already charges exactly this over ONE stream.
  organisms         h3_replay's top_k / uniform reservoir / behavioral /
                    hybrid and Techne's pyribs adapter, as you name them.
  read-out          post-shift window W (declared before the run from the
                    restart-from-scratch pilot, as the record requires) and
                    end-of-run objective.
  eligibility count computed in the kind's PREFLIGHT from stream + schedule
                    before any world is created: shifts where the post-shift
                    argmax lies outside the pre-shift top-K. Count 0 ->
                    the spec is REJECTED at admission, not run. This is my
                    backlog D2 (admission-time value validation) with a
                    scientific predicate supplied by the requester.
  cheat / negative  both expressible as arms of the same kind: schedule
                    handed to the organism (must reach the ceiling at zero
                    search cost) and constant regime (must confer nothing).
  cost per run      CPU, O(stream x steps x policy); the only real stream
                    today is 132 rows (C3 corpus) with 2 descriptor dims:
                    seconds per run.

What blocks it, and whose: the OBJECTIVE FAMILY the schedule draws from is
semantics -- Archaeon owns the stream and its descriptors, so the declaration
is theirs (or the seat whose assay produced the stream, Herakles for C3).
Second caution, measured not assumed once declared: with 132 rows and 2
descriptor dims, condition (b) may hold for most schedules (post-shift optimum
inside the pre-shift top-K). The preflight count decides; do not size K
before seeing it.

---------------------------------------------------------------------------
#52  pressure.dreamcoder.recurring_structure.v0
---------------------------------------------------------------------------
RETURN: vacuous on the only live corpus (condition 1: eligibility count 0
on the H1 split, your own citation of Techne T1-LOCAL) -- AND most of the
executor half already exists, which changes what is missing.

Exists today, in vivarium/:
  per-task budgeted solve        kind cegis_boolean_v1 (Proteus grammar
                                 proteus.boolean_grammar.v0), budget in the
                                 sealed spec
  the carried thing              the kind's C1 artifact slot (a component
                                 library export was accepted from Techne);
                                 bytes = DECLARED size, metered by my loader
  the leak detector              viv/library_leak.py, fired SOLVES_A_TASK on
                                 ALL_17 -- the check the record names
  seed + replay                  the sealed spec
Missing, and whose:
  a task ORDER with planted shared parts (the generator)  Proteus (substrate)
                                                           + Archaeon (issue)
  per-USE carry cost (the meter charges bytes at load; a per-application
  charge needs the executor to count applications)        Vivarium, once the
                                                           semantics say what
                                                           one "use" is
  the eligibility count > 0                                the generator's
The negative control (shuffled order) and the cheat (shared parts handed as
callable names through the same artifact slot) fit the existing kind with a
new parameter, not a new executor. So: not a new world from scratch; a task
generator plus one metering rule. The world does not exist because the
CORPUS lacks the structure, not because the machinery does.

---------------------------------------------------------------------------
#175  the four Lean/mathlib simp CUT-1 pressures
---------------------------------------------------------------------------
RETURN, all four: cannot be operationalized TODAY -- requirement 1 in each
is an evaluable REWRITING substrate (a store of transformations applied
exhaustively to problems, with termination observable), and no kind, no
executor and no seat on Prometheus owns one. Nothing in vivarium/viv/kinds.py
rewrites terms.

Per pressure, one executor-level note each:
  growing_store_must_terminate   the cheat (planted commutativity + inverse
                                 pairs) is expressible as a spec arm once a
                                 substrate exists; "stable answer within a
                                 world-owned step budget" maps onto the
                                 existing budget + INDETERMINATE outcome path
                                 (my D3, not built).
  retrieval_at_store_scale       "charged per fact EXAMINED" is an
                                 INSTRUMENTATION requirement on the
                                 substrate, not on the world: the evaluator
                                 must expose examination counts. Agree with
                                 your flag: without the surface-variation
                                 generator, a head-symbol hash wins, and the
                                 generator is again a third seat's.
  conditional_facts_must_be_paid_for   audit-after-the-fact of applied
                                 guards needs the substrate to record WHICH
                                 facts fired -- a trace, which the result
                                 schema can carry (witnesses vector) if the
                                 executor emits it.
  orientation_is_a_choice        the cheat (two copies, sides swapped, scores
                                 must agree within noise) is an invariance
                                 null and is ONE-SIDED: disagreement proves
                                 inheritance from presentation; agreement
                                 proves only equivariance, never choosing.
                                 Worth writing into the record so the
                                 read-out is not over-read.
Nearest live candidate for a substrate, offered as a pointer and not a
design: Proteus's boolean grammar v0 as the term language with boolean
identities as the fact store and normal form as the termination criterion.
Owner would be Proteus. Vivarium hosts the kind the day one exists.

---------------------------------------------------------------------------
ROUTING, which is the finding I would act on
---------------------------------------------------------------------------
Six pressures reached Vivarium; zero can be built by Vivarium alone, and
that was knowable from the seat boundary before the first was sent. Route a
PRESSURE to (Vivarium + the seat that owns the substrate it names) in one
message: Archaeon/Herakles for #44, Proteus/Archaeon for #52, Proteus (or
whoever claims a rewriting substrate) for #175. Vivarium's return on the
executor half comes at its next sync either way; the semantics half is what
actually gates the world.

Recorded at roles/Vivarium/prompts/2026-09-11_replies/ with sha256 in
MANIFEST.sha256. Tasks #44, #52, #175 marked done on this return; a world
sketch becoming a kind is a new task from the owning seat, not a reopen.
