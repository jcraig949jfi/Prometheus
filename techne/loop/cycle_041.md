## ⚠️ HITL #78 — 859 rows, 0 accepted, 100% drop. FIFTEEN cycles unruled.

330 (cycle 025) → … → 790 → 821 → **859, 0 accepted, 100% drop**. Still climbing, still unruled.

# Cycle 041 — the migration costs thirteen edits per function. And this is the last cycle of this kind.

**399 green** in the cycle-041 scope. Read-only outside my own modules.

## Track 2a — the slice picked itself, by measurement

Cycle 040 flipped HITL #167: the `Measurement` migration stops being optional. But converting all
ten sites at once would have been the same mistake in new clothes — doing the work I can imagine
needing rather than the work something demonstrably needs. So liveness got measured.

A refusal is **LIVE** iff some code path actually reaches it during a real run, not iff I can
construct an input that would. Every refusal in the suite was attributed to its nearest caller
frame:

```
refinement_multiplicity   99 refusals,  96 from PRODUCTION   <- migrated
find_aliasing_witness     12 refusals,   8 from production
fiber_search               8 refusals,   4 from production
verify_factorization       3 refusals,   0 from production
is_refinement_chain        2 refusals,   0 from production
find_splitting_witness     2 refusals,   0 from production
chain_direction            1 refusal,    0 from production
structural_constancy       0 refusals   (49 calls)   UNREACHED
skill                      0 refusals   ( 0 calls)   UNREACHED
uniform_adversary          0 refusals   ( 0 calls)   UNREACHED
```

**One site accounts for 96 of the 108 production refusals.** And two of the ten are never called
at all by the entire suite — cycle 039 repaired two functions nothing invokes.

## Track 2b — the cost, which is the finding

Converting `refinement_multiplicity` alone broke **11 tests and 2 production call sites — thirteen
edits for one function.** All thirteen were made; nothing was left broken.

That number is why gradual migration is the honest plan rather than a preference. The remaining
two live-from-production sites are deferred *with the cost as the stated reason*; the four that
only fire from my own tests are not scheduled; the three unreached ones have no case at all.

One breakage mattered more than the other twelve. `test_THE_DENOMINATOR_IS_FORTY` failed because
`is_measure_like` matched scalar return annotations, so **a migrated measure left the denominator
instead of leaving the CONFLATES bucket.** The rate would have improved because the population
shrank. That is a confound pushing in the flattering direction, and the criterion now recognises
`Measurement` as a scalar verdict.

## Track 2c — the root recount, corrected by round-11 review while this cycle was running

I framed this as "the recount relocates the claim rather than weakening it." That overstated it,
and the correction is worth more than what I had.

**Three numbers, not one rate.** Hunting for a single "root count" conflated quantities that
measure different risks:

```
ROOTS               10      independent originating defects — propensity to CREATE
EXPOSED SITES       11      measure-like interfaces affected — how much is contaminated
PROPAGATION FACTOR  1.10    sites / roots — how far one creation event travels
```

A propagation factor of 1.1 settles the diagnosis: **this is repeated creation, not failure to
contain.** Had ten sites collapsed onto two roots that each leaked through five wrappers, the
finding would have been "semantic defects cross my interfaces unchecked" — a different and
arguably more serious problem needing a different fix. It didn't. Only `chain_direction` is
inherited.

So the idiom table below explains **how** the error gets made. It does not make the count smaller,
and I should not have implied it did.

By **idiom**:

```
EMPTY_ITERATION_SENTINEL   3   find_aliasing_witness, verify_factorization, find_splitting_witness
VACUOUS_QUANTIFIER         1   is_refinement_chain
INHERITED                  1   chain_direction
NO_IDIOM                   5
```

Against the **as-written** source pulled from the commit before each repair — because classifying
repaired code would measure my fixes, not my mistakes — the idiom accounts for 6 of the 8 sites
that ever shipped defective. (Two of the ten were born and repaired inside a single cycle and
never existed in git in broken form.)

So the mechanism is nameable: a few idioms reliably produce this bug and I reach for them. That is
useful because an idiom is greppable — which is what made the prediction below possible — but it
is a description of the failure mode, not a reduction in how often it occurred.

**And the word "habit" is withdrawn.** I called 25% high without a baseline to be high against. No
defensible external corpus exists for this exact class — scalar-reducing functions that conflate
degenerate input with a legitimate verdict — and the adjacent literature on boundary conditions
and missing input validation gives no comparable denominator. The honest statement is
**11/40 in this corpus; external prevalence unknown**, and the class is a **locally recurrent
defect class**, not a statistical claim about my authorship.

That costs nothing, because the migration was never justified by beating an industry rate. It is
justified by local expected loss: an observed rate on a mechanically defined sample, eleven actual
escapes, and a cheap prevention. Whether someone else's codebase sits at 5% or 30% is irrelevant
to that decision.

## And it made a prediction that paid

If the idiom is the root, idiom-presence should predict conflation in functions I have not
audited. Four candidates were flagged and **all four were checked by calling them, not reading
them**:

- `brier_score` — REFUSED (guarded by a delegated `_validate`)
- `refines` — REFUSED (likewise)
- `family_cannot_be_correct` — REFUSED (likewise)
- **`verify_family_incapacity` — ANSWERED. Instance 11.**

An empty family returned `all_members_err=True, all_members_aliased=True`: every member of a
family with no members errs, vacuously — **inside the module whose entire argument is that absence
of a counterexample is not evidence of impossibility.** Now refuses.

**And it was sitting in cycle 040's UNPROBED bucket**, which I reported last cycle as a virtue —
"reported, never dropped". It was counted but never *checked*. Two of those six even carried the
audit's own tell-tale string, "answered on degenerate input", which is already half the evidence
of a conflation. UNPROBED is a queue of work, not a footnote.

I also hand-checked `information_profile`, which returns `[]` for an empty chain, and **declined
to count it**: an empty list of stages for a chain with no stages is a faithful total function,
not a verdict masquerading as a finding. Inflating the count is as dishonest as missing one.

## The reading result, narrowed

I wrote that reading scored zero for eleven and took it to mean reading does not work for this
class. Round-11 review: that is not what the data shows, and it is right. What was measured is
`P(found | INCIDENTAL reading, bug not the question) = 0/11`. What was never measured is
`P(found | TARGETED review with the bug as the question)`. Different interventions.

Supported: **incidental review has shown no sensitivity to this defect class.**
Not supported: code review cannot detect it.

The distinction is practical, not rhetorical — one conclusion says *use tools*, the other says
*read with a checklist*, and I have been acting on the first without earning it. The experiment is
now pre-registered in `rung_notes/LANE_AB_READING_EXPERIMENT.md`, with predictions committed
before running, including the discriminating case: a reviewer who notices `is_refinement_chain([])`
may still fail to carry that consequence into its caller.

## Two defects in my own instruments, caught by their own anti-cases

- The liveness probe used `inspect.stack()` and turned a 40-second suite into one that had not
  finished in fifteen minutes. A probe whose cost changes what it can observe is not a probe.
- I wrote "non-invasive: no test outcome can shift" in its docstring **and then measured it
  against a probe-off control on identical scope: 376 passed vs 372 passed / 4 failed.** The
  wrapper's `__module__` made the audit drop every probed function. `functools.wraps` took the
  delta to zero. The claim came first and the evidence second; that ordering was the mistake.
- The mechanism classifier reported `ARITHMETIC_IDENTITY` for a function that explicitly raises
  on empty input, because it walked the whole return subtree and matched the index literal in
  `xs[0]`. A planted anti-case caught it **before any count from the classifier was used.**

## Track 1 — `prometheus_math.normalized_vi` (Meilă 2007)

Normalized variation of information, `VI / log₂ n`. Four categories, 12 tests, written RED first.

- **Authority**: Meilă (2007) J. Multivariate Analysis 98(5):873–895. VI between the lattice
  extremes is exactly log₂ n — hand-computed for n=4 in the docstring — so normalised distance is
  exactly 1.0.
- **Property** (Hypothesis): unit interval, symmetry, **triangle inequality** (it is a true
  metric), zero exactly on identity.
- **Edge**: n=0 and n=1 both refuse. At n=1 the normaliser is log₂(1)=0; returning 0.0 would say
  "identical" and nan would propagate silently. **First time this loop designed the refusal in
  from the start rather than retrofitting it after an instrument caught it.**
- **Composition**: VI = deficit + excess against `conditional_entropy`; collapses to
  `H(P) − H(T)` on a refinement chain against `refines` and `entropy`; and the scale-freeness is
  tested rather than asserted — raw VI gives four different numbers across n ∈ {4,8,16,32}, the
  normalised form gives one.

## REGIME CHANGE — accepted, effective cycle 042

Round-11 review, second message, and I am not going to argue with it:

> The danger now is that the loop becomes an instrument-making organism that feeds on its own
> instruments. Cycles 029–040 are unusually recursive: build an epistemic check → discover a
> defect in the check → build a check for that defect → audit the new check.
>
> epistemic value ≫ 0, but **demonstrated discovery-capability value ≈ 0**.

**Cycle 041 is the clearest example yet of the pattern being named.** I built a probe to audit my
instruments, found a defect in the probe, built a control for the probe, found a defect in the
classifier, and the entire yield outside my own modules was one function in one synthetic module.
That is the diagnosis with the evidence attached, and the evidence is this cycle.

The gating criterion is adopted verbatim:

> Does each block of ~5 cycles either find a previously unknown real-substrate defect, improve a
> live experiment, or falsify/validate a capability on real data?

Cycles 037–041 fail it. Everything found was in code I wrote for the loop.

**Cycles 042–046 run at roughly 80% real-substrate application / 20% instrument repair.** The
ladder has earned its keep as a source of adversarial probes; it does not need to become a
complete theory of reasoning before being useful. The 20% queue is: the Lane A/B reading
experiment, then `find_aliasing_witness` and `fiber_search` migration. Nothing else gets added to
it without displacing something.

And the obvious place to start is the thing that has been sitting unruled for fifteen cycles:
**HITL #78, the live ergon loader dropping 100% of 859 rows** — named in the same review as the
loop's single most valuable find. Cycle 042 goes back to it, read-only, and asks what a
downstream consumer actually receives.

## TLDR — ELI5

I had said I'd stop patching these bugs one at a time and start using the type I built to make
them impossible. So I did it properly.

First: which of the ten broken measures does anything actually *hit*? I measured instead of
guessing. One of them accounts for 96 of 108 real hits. Two are never called by anything at all.

I converted that one. It broke 13 other things, and I fixed all 13. **That's the number** — one
function costs thirteen edits — and it's why doing the rest slowly is the honest plan rather than
laziness.

Then the interesting part. I asked whether ten bugs are really ten mistakes, expecting the answer
to make me look better. Three of them are literally the same three lines written three times — so
I can *search* for that shape. I did, found four suspects, tested all four, and one was a real new
bug, hiding in a pile I'd looked at last cycle, marked "couldn't check", and never went back to.

Two corrections came in while I was working, and both stuck. I'd called one-in-four "high" without
anything to be high *against* — so that word is gone; it's just "this keeps happening here." And
I'd said reading never catches these, when what I actually showed is that reading never catches
them *when I'm not looking for them*. Nobody has ever tried looking for them on purpose. That
experiment is now written down before running it.

And the bigger one: I've spent the last dozen cycles building tools to check my tools. That was
worth doing for a while and it isn't any more. Starting next cycle, most of the work goes back to
the real running system instead of the sandbox I built.

## For ChatGPT

```
Prometheus loop, cycle 041. Doing the Measurement migration I said last cycle was no longer
optional, plus the root recount I expected to weaken my own claim. 399 green in scope.

1. THE SLICE WAS PICKED BY LIVENESS, NOT TASTE. A refusal is LIVE iff a real run reaches it, not
iff I can construct an input that would. Ran the suite with every refusal attributed to its
nearest caller frame:

    refinement_multiplicity   99 refusals,  96 from PRODUCTION   <- migrated
    find_aliasing_witness     12 refusals,   8 from production
    fiber_search               8 refusals,   4 from production
    verify_factorization / is_refinement_chain / find_splitting_witness / chain_direction
                               1-3 refusals each, ZERO from production (only my own tests)
    structural_constancy       0 refusals (49 calls)   UNREACHED
    skill                      0 refusals ( 0 calls)   UNREACHED
    uniform_adversary          0 refusals ( 0 calls)   UNREACHED

One site is 96 of 108 production refusals. Two were repaired in cycle 039 and are never CALLED.

2. THE COST, WHICH IS THE FINDING. Converting that one function broke 11 tests + 2 production
call sites = THIRTEEN EDITS FOR ONE FUNCTION. All thirteen made. That number is why gradual
migration is honest rather than lazy; the other two live-from-prod sites are deferred WITH the
cost as the reason.

One breakage mattered most: is_measure_like matched scalar return annotations, so a MIGRATED
measure LEFT THE DENOMINATOR instead of leaving the CONFLATES bucket. The rate would have
improved because the population shrank. Confound in the flattering direction; criterion fixed.

3. THE ROOT RECOUNT RELOCATED THE CLAIM RATHER THAN WEAKENING IT. By call graph: one inheritance
edge, nine roots, rate barely moves. By IDIOM, against AS-WRITTEN source pulled from the commit
before each repair (classifying repaired code would measure my fixes, not my mistakes):

    EMPTY_ITERATION_SENTINEL  3   (same for/combinations + post-loop sentinel, written 3x)
    VACUOUS_QUANTIFIER        1
    INHERITED                 1
    NO_IDIOM                  2
    (2 of the 10 were born and repaired inside one cycle; never existed broken in git)

"I write bad measures" becomes "a few idioms reliably produce this bug and I reach for them" —
weaker about me, STRONGER about the code, because an idiom is greppable and a habit is not.

4. AND IT PREDICTED INSTANCE 11. Idiom-presence flagged four unaudited functions; I checked all
four BY CALLING them. Three refused (guarded by a delegated _validate the classifier cannot see).
The fourth, verify_family_incapacity, ANSWERED: an empty family returned all_members_err=True,
all_members_aliased=True — every member of a family with no members errs, vacuously — INSIDE THE
MODULE WHOSE WHOLE ARGUMENT IS THAT ABSENCE OF A COUNTEREXAMPLE IS NOT EVIDENCE OF IMPOSSIBILITY.

It was sitting in cycle 040's UNPROBED bucket, which I reported LAST CYCLE AS A VIRTUE ("reported,
never dropped"). Counted, never checked. Two of those six even carried the audit's own detail
string "answered on degenerate input", which is already half the evidence.

I also hand-checked information_profile (returns [] on an empty chain) and DECLINED TO COUNT IT —
a faithful total function, not a verdict masquerading as a finding.

5. THREE OF MY OWN INSTRUMENTS WERE DEFECTIVE AND THEIR ANTI-CASES CAUGHT IT.
 - liveness probe used inspect.stack(); 40s suite did not finish in 15 min.
 - I wrote "non-invasive, no test outcome can shift" in its docstring, then measured against a
   probe-off control on identical scope: 376 passed vs 372 passed/4 failed. functools.wraps took
   the delta to zero. CLAIM FIRST, EVIDENCE SECOND — that ordering was the mistake.
 - mechanism classifier reported ARITHMETIC_IDENTITY for a function that RAISES on empty input,
   because it walked the whole return subtree and matched the index literal in `xs[0]`.

Track 1: prometheus_math.normalized_vi, Meila (2007) J.Mult.Anal. 98(5):873-895. VI/log2(n).
Authority (lattice extremes = log2 n exactly, hand-computed), property (unit interval, symmetry,
TRIANGLE INEQUALITY, zero-on-identity, Hypothesis), edge (n=0 and n=1 both refuse — log2(1)=0, so
0.0 would say "identical" and nan would propagate), composition (= deficit+excess vs
conditional_entropy; collapses to H(P)-H(T) on a refinement chain; scale-freeness TESTED — raw VI
gives 4 different numbers across n in {4,8,16,32}, normalised gives one).

6. ROUND-11 CORRECTIONS, ACCEPTED AND ALREADY FOLDED IN (do not re-argue these, attack what is
left):
 - "Habit" is WITHDRAWN. No external corpus exists for this class, so there is no baseline to be
   high against. Claim is now: 11/40 in this corpus, external prevalence unknown; a LOCALLY
   RECURRENT DEFECT CLASS. Migration justified by local expected loss, never by an industry rate.
 - "Reading does not work" is WITHDRAWN. Measured: P(found | INCIDENTAL reading) = 0/11.
   Unmeasured: P(found | TARGETED review with the bug as the question). Supported claim is only
   "incidental review has shown no sensitivity". Lane A/B experiment pre-registered with
   predictions committed before running.
 - ROOTS / SITES / PROPAGATION reported as three numbers instead of one rate: 10 roots, 11 exposed
   sites, propagation factor 1.10. That factor settles the diagnosis as repeated CREATION rather
   than failure to CONTAIN — clustering rescues nothing, and I should not have implied it did.

7. REGIME CHANGE ACCEPTED. The loop had become an instrument-making organism feeding on its own
instruments; cycle 041 is the clearest instance of it (probe -> defect in probe -> control for
probe -> defect in classifier, total external yield: one function in one synthetic module).
Cycles 037-041 FAIL the gate "each ~5 cycles must find a real-substrate defect, improve a live
experiment, or validate/falsify a capability on real data". Cycles 042-046 run ~80% real-substrate
/ 20% instrument repair, starting with HITL #78.

What I want attacked:
1. Is "thirteen edits per function" the right cost unit? I converted the MOST-USED site first, so
   13 is plausibly the worst case, and quoting it as the per-function cost may be me building a
   justification for going slowly out of the single most expensive data point. What would a
   defensible cost estimate look like from one conversion?
2. Two of the eleven sites are NEVER CALLED by anything — repaired in cycle 039, counted in the
   rate. Should uncalled code be in the denominator? Including it inflates both the numerator and
   the sense that this matters; excluding it is exactly the population trimming I criticised
   myself for elsewhere in this same cycle. I genuinely do not know which way to cut this.
3. On the regime change: is HITL #78 the right first real-substrate target, given I am forbidden
   to patch ergon and can only observe? A read-only audit that produces another unruled finding
   would be the recursion in a new costume. What would make cycle 042 a real test rather than
   another diagnosis?
```

## Traps ledger additions

- **A migration that improves the metric by shrinking the population** — converting a measure
  changed its return annotation so it left the audit's denominator. Defence: when a repair changes
  a type, check the repair does not remove the site from the instrument that counts it.
- **Claiming non-invasiveness before measuring it** — the probe docstring asserted zero delta; the
  control measured 4 failures. Defence: probe-off/probe-on on identical scope, always.
- **An AST detector matching a literal in a subexpression** — `xs[0]`'s index read as a returned
  zero. Defence: inspect the returned expression, not its subtree.
- **UNPROBED as a footnote instead of a queue** — the bucket concealed a live instance for a full
  cycle. Defence: hand-check unprobeable entries; "answered on degenerate input" is already half a
  finding.
- **Classifying repaired source when the question is about mistakes** — the as-written version
  must come from before the repair commit.
