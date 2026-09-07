# Analyst brief: understanding and classifying a mined experiment template

You are analysing PROPOSED experiment templates for the Prometheus research
bench. Read this whole file before starting. Everything in section 1 is ground
truth taken from source; do not assume any capability not listed.

---

## 1. The bench, exactly as it is

The bench executes sealed experiment specifications. A spec is exactly the
execution inputs: `spec_version 3`, `world` (one integer `seed_root`),
`hypothesis` (prose, recorded not interpreted), `prediction` (may be null),
`work` (a `kind` plus a `payload`), `outcome_rule`, `repeat`, and an optional
`pew` link.

**Three executor kinds exist. Nothing else can run.** Each declares an EXACT
payload parameter set: a missing parameter is a rejected spec and so is an
extra one. No executor may default a parameter.

    kind                 payload params        returns
    -----------------    ------------------    ------------------------------
    noop_v0              (none)                executed
    evaluate_bitstring   bits, length          bits, score, solved
    random_walk_v0       steps, step_scale     position, start_position,
                                               displacement, steps, step_scale

`evaluate_bitstring` scores a bitstring against a hidden target derived by
hashing the seed together with the length. `score` is CONTINUOUS in [0,1];
`solved` is `score >= 1.0`. Length may be any positive integer.

`random_walk_v0` is a deterministic 1-D walk: `steps` increments, each
`step_scale * (uniform(0,1) * 2 - 1)`. It is the ONLY STATEFUL kind, so it is
the only one that may declare `repeat.state = persist`.

A fourth kind, `archaeon.probe.v0`, is RETIRED and cannot be admitted.

**THE OUTCOME RULE IS ONE SCALAR COMPARISON.** One result field, one operator,
one value, mapped to SURVIVED / FALSIFIED / INCONCLUSIVE. No conjunction, no
two-field expression, no aggregation across repeats, no trend or ordering test.

**REPEAT SEMANTICS, and this is the subtle part.** `repeat.seed_derivation` is
one of `constant` (every repeat uses the world seed), `linear_index`
(seed_root + i), or `sha256_index` (hash of seed and index). The executor
receives the REPEAT's derived seed, not the world seed. Therefore:

- under `constant`, every bitstring repeat scores against the SAME target;
- under the other two, every repeat scores against a DIFFERENT target, so
  repeats are independent landscapes rather than repeated looks at one.

The bench flags `degenerate_by_construction` when a constant seed meets a
stateless kind with `state = reset` and `count > 1`: every repeat is provably
the identical computation and within-world variance is zero before it runs.

**ONE WORLD PER SPEC.** A single integer. No population, generation, archive,
niche grid, tournament, opponent, or second world.

**NO SEARCH INSIDE A SPEC.** The payload is fixed for the whole spec. Repeat
N+1 cannot submit a different bitstring from repeat N. One spec is ONE
candidate against one or more targets. Search, hill-climbing and population
methods can only happen ACROSS specs, which is the producer's job, not a
template's.

---

## 2. What you must produce, per template

Use EXACTLY these delimiters and field names, one block per template. Plain
ASCII. No markdown tables. Do not use square brackets anywhere.

    BEGIN_ENTRY
    TEMPLATE_ID: <as given>
    FIELD: <the discipline>
    KIND: <the kind it names>
    QUESTION: <one or two sentences, plain language, no jargon: what
      scientific question is this experiment asking?>
    MECHANISM: <the essential mechanism in plain language. What actually
      happens, step by step, in the real method this comes from?>
    CANDIDATE: <what plays the role of the organism or candidate: what varies,
      what is being judged>
    WORLD: <the environment it acts in, and what the environment supplies>
    WHAT_CHANGES: <what is perturbed or allowed to vary across runs>
    MEASURED: <what number or fact comes out, and on what scale>
    INFORMATIVE_FAILURE: <if this experiment fails, what does the failure
      leave behind that is useful? Be concrete. If a failure would leave
      nothing, say so plainly, that is a real answer>
    SOURCE_CHECK: <VERIFIED, PLAUSIBLE or UNRESOLVED, then one line. VERIFIED
      means you are confident the named method exists as described and the
      attribution is right. PLAUSIBLE means the method is real but you could
      not confirm the specific attribution. UNRESOLVED means you could not
      establish it. Do not invent citations>
    SHARED_MECHANISM: <a short lowercase tag naming the underlying mechanism,
      chosen so templates from DIFFERENT disciplines that do the same thing
      get the SAME tag. Examples of the style: score_fixed_candidate,
      accumulate_trajectory, maintain_archive, interpret_program,
      two_population_interaction, fit_model_to_data, search_over_candidates>
    ROUTES: <one or more of the route codes below, most preferred first,
      comma separated>
    BLOCKER: <for each route named, the EXACT blocker, semicolon separated.
      Name the missing thing precisely: a measurement, a state or control-flow
      capability, or an adjudication capability. Say which of those three it
      is>
    FAITHFUL: <what a faithful implementation would require. Two or three
      sentences>
    REDUCTION: <the smallest useful Prometheus-adjacent version that could run
      on or near the current bench. Be inventive but concrete. If a reduction
      exists, state WHAT IT PRESERVES, WHAT IT LOSES, and WHICH CLAIM it could
      still support. If no useful reduction survives, say NONE and give the
      concrete reason>
    END_ENTRY

### Route codes

    R-NOW        executable now on an existing kind, as written
    R-REPAIR     executable now once damaged or missing parameters are chosen
    R-COMPOSE    expressible by running several existing specs and doing the
                 analysis downstream, outside the outcome rule
    R-EXECUTOR   needs a new executor or an adapter around existing machinery
    R-SUBSTRATE  needs a new substrate capability such as persistent state,
                 an archive, or output-to-input chaining
    R-WORLD      needs a richer world or a new organism type
    R-BACKEND    needs an external execution backend that the engine could
                 orchestrate and fossilize, rather than new bench internals
    R-ARCH       needs a substantially different architecture

Distinguish R-BACKEND from R-ARCH carefully. If an existing external tool could
do the work and the bench only has to call it, record inputs and outputs, and
fossilize the result, that is R-BACKEND and it is cheap. R-ARCH is reserved for
cases where the bench's core assumptions, one sealed spec producing recorded
observations, are themselves wrong for the method.

---

## 3. Standards

- Be inventive in REDUCTION. The point of this pass is to find clever, small,
  faithful-enough versions. Physical chemistry might become a symbolic reaction
  network. Embodied behaviour might begin on a tiny grid. Discovery might begin
  with synthetic data and a planted law. Coevolution might begin with two small
  interacting populations. These are invitations, not answers.
- Be honest when a reduction would be a gesture rather than an instance of the
  method. A named, well-argued NONE is more useful than a strained yes.
- Keep measurement separate from interpretation throughout.
- Never invent a citation. UNRESOLVED is a perfectly good answer.
- Some templates carry `null` values in `param_space` because the research tool
  that produced them destroyed the numbers. Treat those as unknown. If your
  REDUCTION needs a number, propose one and mark it clearly as a NEW DESIGN
  CHOICE.
