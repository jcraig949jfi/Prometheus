# Charter Amendment 1 — the widening claim is KILLED; three levels; the instrument rule

External review, 2026-08-27. Adopted in full. This amends
`aporia/CHARTER_MUTABLE_LANGUAGE_OF_THOUGHT_2026-08-26.md` and governs over it where they
conflict.

---

## 1. KILLED, immediately and permanently

> **KILL: promoting a composition can demonstrate representational widening in a closed
> compositional ISA.**

The argument is definitional, not empirical. Let `C` be the primitive language and `G(C)` all
unrestricted finite compositions. If `M = g(p1..pk)` with `g ∈ G(C)`, then

    G(C ∪ {M}) = G(C)      extensionally, given arbitrary composition and no resource bound

**Adding `M` adds a name, not a denotation.** Reporting a post-`M` gain as "representational
widening" would be the same category mistake already diagnosed in the adapter experiment —
where a +5/120 gain turned out to expose a missing intermediate representation rather than a
missing capability.

The charter's §4 distinction between "search compression" and "representational widening" is
therefore **withdrawn as unmeasurable in this architecture.** It is replaced by three levels.

## 2. The three levels — use these names, and only these

    Level 0  DEFINITIONAL CHUNKING
             M := r03(r01(x), r07(x)). Nothing newly representable.
             Legitimate effect: fewer search decisions. Call it SEARCH COMPRESSION, full stop.

    Level 1  OPERANDIZATION                                    <- THE TARGET OF THIS ARC
             M becomes an object other operators consume: COMPARE(M1,M2), NEGATE(M),
             APPLY(M,x), COMPOSE(M,N) -- operations over relations themselves rather than
             over their evaluated outputs. This genuinely alters the program graph available
             under the architecture. It remains compilable away in a sufficiently expressive
             meta-language, which is irrelevant because Apollo does not possess one.
             Call it OPERAND-SET WIDENING. Never "representational widening".

    Level 2  NON-CONSERVATIVE SEMANTIC EXTENSION
             M whose behaviour is not definable in the existing closure. Requires machinery
             outside G(C): induction from observations, a new oracle, recursion, quantification,
             variable binding, a new type constructor. NOT NEEDED for this arc and not claimed.

**Reframed central distinction:** `flat composition → reusable executable chunk → first-class
operand`.

**The reduced hypothesis, which is what we are actually testing:**

> A reasoning system can discover a useful composition, promote it to a first-class executable
> operand, and thereby alter the topology/cost of subsequent computation in ways not reproduced
> by merely retaining the same primitive semantics.

## 3. PROGRAM-WIDE INSTRUMENT RULE — adopted, applies beyond this arc

Six mis-aimed probes are too many for "eventually caught by inspection" to count as validation.
The fix is **orthogonal instrument falsification, not voting.** Every consequential probe must
demonstrate three things before its reading is scientifically admissible:

    DYNAMIC RANGE            inputs where the quantity is known HIGH and known LOW; the probe
                             must traverse both
    INTERVENTIONAL SENSITIVITY change only the purported causal variable; the probe must move
                             in the expected direction
    METAMORPHIC CONSISTENCY  transform the input in ways that theoretically preserve or invert
                             the measured quantity; the reading must follow

**Two hard rules:**

> A probe that has never passed a known-POSITIVE fixture **cannot issue a scientific FAIL.**
> It may issue only `INSTRUMENT_UNVALIDATED`.
>
> A probe that has never failed a known-NEGATIVE fixture **cannot issue PASS.**

Applied retroactively: **my three world rejections were issued by a preflight that had never
passed a known-positive fixture. They are downgraded to `INSTRUMENT_UNVALIDATED` until the
calibration in §6 passes.** The underlying observations stand; the verdicts do not.

## 4. REPLICATION vs REPRODUCIBILITY — correction

Re-running committed deterministic code is **reproducibility**. Real replication is an
**independent implementation from the preregistration, without consulting the original code**,
then comparing outputs. That is what attacks shared implementation assumptions. My earlier
recommendation conflated the two.

## 5. THE CONFOUND I HAD NOT NAMED — unit-cost macro privilege

If the flat solver spends three search decisions on `r03 → r07 → r02` while the reified solver
spends one on `M17`, a budget advantage is nearly guaranteed — **and it has been partly defined
into the action representation.**

    C_execution  and  C_search  MUST NEVER BE MERGED.

Executing `M` is charged the cost of executing its **expansion**, since no computational oracle
was introduced. Selecting `M` may legitimately cost **one** search decision. **That difference
is the phenomenon.** Report the two costs independently; a claim under a single merged
"operator-call budget" is meaningless when one arm's operator hides three calls.

**Second danger: hindsight promotion.** If the same tasks both establish a composition's
usefulness and reward its later availability, that is feature selection on the test set.
**Promotion occurs on one episode; benefit is measured on genuinely unseen later episodes.**

## 6. THE REVISED PLAN — option A, modified

**A1 — INSTRUMENT CALIBRATION. No hypothesis test.** Known-good and known-bad fixtures. The
preflight must produce a clean PASS on the good one **without adjusting thresholds after seeing
the result.** If a known-good specimen cannot be deliberately constructed, stop using the
preflight.

**A2 — SEMANTIC-FIRST WORLD.** Construction order inverts:

    latent relation table -> prove the statistical properties EXACTLY -> compile to a surface

not surface-first-and-hope. **Graphs are a hostile surface** — degree, density, components, path
length, symmetry and motifs are a factory for unintended classifiers, which is exactly what
killed worlds v1 and v2. Start boring enough to enumerate every shallow route. Establish flat
solvability and exhaustive shallow baselines. No reification, no transfer, no LoT claim.

**A3 — REIFICATION.** Promotion decided on early tasks, benefit measured on held-out later ones,
with execution and search cost reported separately.

Transplantation moves to a later experiment. **XOR is demoted from the experimental world to an
instrument calibration world.**

## 7. Why XOR could not have been the experimental world

The circularity is not that XOR is simple. It is:

    experimenter knows the useful latent structure -> constructs the task around it ->
    solver receives a mechanism optimised for reifying that structure -> reification helps

**The abstraction must be unknown to the promotion mechanism** and not privileged by the
generator. The replacement construction is random latent program DAGs over 8–12 anonymous typed
primitives, with preregistered world classes:

    REUSE         a hidden subexpression recurs downstream
    NO_REUSE      no composition recurs enough to justify promotion
    DECOY_REUSE   a conspicuous composition recurs during discovery but NOT downstream
    LATE_REUSE    a weakly evidenced composition becomes useful later
    CONTROL       the useful expression is supplied from the beginning

**A language-growth mechanism tested only in worlds where growth helps has not demonstrated
selection.** The system must decide *when* abstraction is warranted, including deciding not to
mint anything.

## 8. Q6 resolved — the invariant is not circular

Grow the vocabulary and its consumer **at their boundary**:

    task -> consumer interface -> failing witness -> primitive -> ablation

Define a task the solver cannot progress on because it lacks a relation of type `A → B`. The
consumer already exists and is asking; it simply receives no implementation. Implement, run,
ablate. **The primitive has a live consumer from birth.** The old library failed because its
arrows pointed one way: `taxonomy → hypothetical future consumer`.

## 9. KILL CRITERIA — two genuine attempts after calibration, then park

1. Still cannot produce a semantic-first world passing a **frozen, positive-controlled** preflight.
2. Reification advantage disappears once hidden execution cost, unit-cost macro privilege and
   hindsight promotion are removed.
3. Promoted compositions perform no better than **complexity- and frequency-matched arbitrary
   chunks**.
4. The promotion mechanism cannot distinguish REUSE from NO_REUSE worlds.
5. **Any apparent gain is entirely recovered by giving the flat solver an equivalent search
   memo/cache.** If reified abstraction and ordinary memoised search produce the same effect,
   the mutable-language interpretation has earned nothing.

## 10. The line this arc is judged against

The predecessor arc showed an **ISA hole** (the adapter result) and showed that **naming the
missing instruction was not abstraction** (zero cross-route transfer).

> Success here requires that the system itself **earns the right to mint the instruction before
> it knows which future task will reward it.**

That is the line between another vocabulary project and first evidence for a mutable executable
language of thought.
