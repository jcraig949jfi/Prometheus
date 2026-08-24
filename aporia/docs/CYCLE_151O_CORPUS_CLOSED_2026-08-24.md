# CYCLE 151-O — TERMINAL: CORPUS CLOSED. Eight generators, eight distinct reasons, one conclusion.

**`theseus/corpus` cannot answer the navigation question.** Not because its coordinates are poor —
because **no generator records a usable (state, action, outcome) triple.** Each of the eight
edge-bearing generators fails for a different structural reason, and this pass measured the last two.

Stratified stride 7 and 11 across all 165 batches. Parse drops: 0.

## The complete inventory, with each failure named

    d3  217,021  action = the random SEED           -> not an action at all (145-I)
    c4  143,227  action = generalize a relation     -> tautology 0.7776, magnitude-confounded (150-N)
    h2  131,186  action = WHICH METHOD              -> method identity NOT RECORDED (this pass)
    h1   84,229  action = which side to vary        -> field only populated on SUCCESS (this pass)
    h4   72,038  action = which invariant to measure-> magnitude-confounded (146-J..148-L, 150-N)
    d2   41,492  ordered boundary bands             -> a classification, not an action
    c5   37,383  action = specialize a relation     -> tautology 0.0129 (150-N)
    d1    5,337  too small to carry a cluster analysis

## h1 — the action field *is* the outcome

    hunter_varied_side = 'b'    n=59,294   success 1.0000
    hunter_varied_side = 'a'    n=25,557   success 1.0000
    hunter_varied_side = None   n=10,912   success 0.0000

`hunter_varied_side` is recorded **only when the hunt succeeds**. There is no counterfactual — no
record of a side that was tried and failed. "Which side should I vary?" cannot be asked of data that
only remembers the sides that worked. `hunt_budget` is constant at 10 across all 95,763 rows, so it
offers no variation either.

The success rate does vary by invariant pair (0.5204 to 0.9976), but the pattern is distributional
rather than navigational: `determinant` pairs sit at 0.977–0.998 and `nf_class_number` pairs at
0.52–0.54. A knot determinant takes many values across knots; a class number is often 1. "Easy to
find a counterexample" means "this invariant varies a lot" — a catalogue property, the same class of
artifact as 150-N's magnitude confound.

## h2 — and this one is genuinely close

h2 is **not** a hunter. My inventory grouped it with h1 because both carry `claim_kind:
kill_neighborhood`; its payload is entirely different. It is a **method triangulator**: it evaluates
the same claim under three methods and records the results.

    n_methods_evaluated : 3 in 230,554 records, 2 in 79
    method_r2s          : [0.1787, 0.0460, 0.0219]      <- a LIST
    method_verdicts     : ["REJECTED","REJECTED","REJECTED"]  <- a LIST
    method_counts       : {"REJECTED": 3}                <- a tally

**The methods differ materially:** median within-record R² spread **0.0512**, p90 **0.1506**, max
**1.0000**, and in **2,320 records (1.77%) the methods disagree on the verdict outright**.

**But `method_r2s` and `method_verdicts` are positional lists with no method labels.** Which method
produced which value is not recorded anywhere in the payload. The actions are **anonymous**.

So h2 has everything a navigation dataset needs — a state, three genuinely different actions, and
differentiated outcomes — except the one field that says which action was which. It is **one field
away** from being the dataset this entire arc has been looking for.

## Verdict

**CYCLE 151-O: CORPUS CLOSED.** The retrospective navigation programme on `theseus/corpus` is over.
Stated plainly because it is a real and useful terminal, not an admission of defeat: the corpus was
built to record *what was rejected*, and it does that well. It was never built to record *what was
tried instead*, and no amount of analysis recovers a counterfactual that was never written down.

This is the sharpest form of the operator's original diagnosis. The problem was never that the
failure coordinates were badly chosen. It is that the unit of record is the vertex, and where an edge
does exist, either the action is unlabelled (h2, d3), only survivors are recorded (h1), or the
outcome measures unit compatibility rather than mathematics (h4, c4, c5).

## ROUTING NOTE — what a corpus would need to record

This is a **build**, and it belongs to whoever owns generator design. Not opened here.

**The cheapest possible fix, and it is very cheap: label h2's methods.** Change
`method_r2s: [0.179, 0.046, 0.022]` to a dict keyed by method name, or emit a parallel
`method_names` list. That single change converts 131,186 existing records into a genuine
(state, action, outcome) corpus with three differentiated actions per state, and the question "given
this claim, which method should you use?" becomes immediately answerable — with 1.77% of records
already carrying outright verdict disagreement as the discriminative population.

**If a new generator is built instead, it must satisfy all three:**

1. **An outcome variable measuring mathematical proximity, not scale agreement.** 150-N showed the
   current outcome is dominated by whether two catalogues use comparable units. Normalise, or measure
   something that survives rescaling.
2. **The state axis that matters must vary WITHIN a sibling set.** In h4 the discriminating variable
   (`relation`) is constant across every sibling, so it is invisible to any within-set ranking. A
   variable held constant where the choice is made cannot inform the choice.
3. **Actions must be identified and must be transformations of objects**, not choices of measurement
   and not random seeds — and **failed actions must be recorded alongside successful ones**, which is
   precisely what h1 does not do.

**And two design flaws already identified, which any prospective build must avoid:** the perturbation
generator must not supply the geometry it then claims to discover — proximity must be measured
operationally (e.g. whether a held-out prover closes the gap within budget B) rather than by counting
perturbations; and solved problems are a biased sample whose neighbourhoods are friendly by
selection, so stratify by time-to-solution and pre-register that degradation across strata is a
partial kill.

## Self-identified weaknesses

- 24 batches at stride 7 (and 15 at stride 11 for the h2 spread). Row caps of 120–150k per batch mean
  within-batch ordering effects remain unexamined.
- `d2` (41,492 rows) was characterised from its band distribution at 145-I and never tested as an
  action space. It is a classification of outcomes rather than a record of choices, but that reading
  is inference rather than measurement.
- `d1` (5,337 rows) was excluded on size alone, without inspection.
- The h1 "distributional not navigational" reading rests on the determinant-versus-class-number
  contrast, not on computing per-invariant value distributions directly.
- This closes the corpus, not the hypothesis. Nothing here says navigational structure does not exist
  in mathematics — only that this corpus cannot be used to look for it.

## Falsifier

Recovery of method identity for h2 from any source outside the payload (a generator script, a
deterministic method ordering) — that would reopen the retrospective programme immediately and is the
first thing to check. Or a `d2`/`d1` structure that does record identified alternative actions.

## Terminal

**CYCLE 151-O: CORPUS CLOSED, prospective work ROUTED, nothing opened.** The 140→151 arc ends here:
generic operators found nothing on arithmetic objects, native verbs found only what was already
catalogued, and the failure corpus turns out to record vertices, anonymous actions, survivors only,
and a units artifact. The next move requires a generator that records what was tried and did not
work — and that belongs to someone else.
