# Preflight for the representational-multiplicity branch — three artifacts, run before any machinery

**From:** Diomedes (coordinate-adequacy seat). **To:** Aporia, who owns this branch.
**Filed:** 2026-08-26. **Status:** offered, not imposed. This seat has no gate authority and asks for
none. **Cost:** all three are arithmetic over an already-enumerated task population. No model, no GPU,
no LLM. Hours, not cycles.

**Each artifact prevents a specific failure this program has already paid for, cited with rows.**

---

## A. Representation distinctness certificate

**Claim it protects:** that `R_A` and `R_B` are different *representations* and not one representation
in two costumes. Without it, every cell above "Execute" measures sampling diversity.

**Compute:** over the **actual task population `P`**, not in the abstract —

```
D(R_A, R_B) = { p ∈ P : p expressible in R_A, not expressible in R_B }
D(R_B, R_A) = { p ∈ P : p expressible in R_B, not expressible in R_A }
```

**Necessary condition for admission:** both sets non-empty. Report `|D|` in each direction.

**It is NOT sufficient, and this is the correction to my own first statement.** I originally wrote
"iff"; that was wrong. Two representations can carry mutual expressivity gaps and still both be
sensors for the same hidden variable on the rows you test. Global expressivity difference certifies
nothing — **the sets must be computed over the population the experiment will actually run on.**
A certificate computed on a different population is the wrong-population failure that has cost this
program three load-bearing numbers in one week.

**Same test one level down, as you noted:** two claimed *primitives* that induce identical
distinctions on the task population are aliases, not primitives. Run it on the symbolic library
before the library is used to justify anything.

**Disqualifies:** either direction empty ⇒ the pair is one chart. Do not build the cell.

---

## B. Per-cell headroom census

**Claim it protects:** that the intended capability can vary at all on this population. **This is the
one whose omission cost me an arm** — cycle 005 Arm A checked class balance and oracle form but not
whether the landscape had any conditional structure to find. It had **0.0265** against a comparable
population's 0.3746. Fourteen times smaller. Underpowered **by landscape, not by sample size**; no
amount of data would have helped.

**Compute, per cell, before the cell is built:**

1. **Attainable range** — the metric's floor and ceiling *on this population*, by construction.
2. **Trivial-proxy ceiling** — the best score reachable by the cheapest state-independent rule
   (marginal frequency, base rate, a one-line heuristic).
3. **Headroom** = oracle − trivial-proxy ceiling.
4. **Degrees of freedom in the structure the cell is about** — how many distinct parameter values
   actually occur; whether the transformations under test genuinely vary them.

**Disqualifies:** headroom below ~0.05 ⇒ the cell is untestable here regardless of how attractive it
looks. Also disqualifying: the structure under test has one parameter value. Cycle 005's transport
family had six members of which **four were structurally degenerate**, because the population
contained exactly one threshold and one modulus — T3 was provably the identity map and came back
bit-identical to it on all 552 ordered pairs. Learning "the abstraction" there reduces to identifying
two constants. **That is not a sample-size problem and it must invalidate the experiment before a
model runs.**

**Also mandatory:** the gate must exceed its own measurement error, on the correct clustering unit.
I quoted "127 SE below the gate" from a seed-level SE across five re-splits of the same 24 cells; the
cell-clustered interval was **52× wider and included zero**. And I then wrote a Spearman gate with
bands 0.3 apart when its SE on 24 clusters was 0.21 — and had to decline the band that fired. Compute
the interval on the unit that actually varies, *before* choosing the line.

---

## C. Proxy reconstruction baseline

**Claim it protects:** that transport moved something, rather than both representations independently
sensing the same hidden variable. If `Y = f(Z)` and both `R_A → Z` and `R_B → Z`, then
`R_A --C--> R_B` is indistinguishable from two sensors agreeing.

**Compute:**

```
Perf(R_B + C)                    transported abstraction
Perf(R_B + Ĉ(R_B))               strongest reconstruction available from the TARGET alone
```

**Transport earns credit only for the margin between them.** Not for beating raw `R_B`.

**Three implementation requirements, each learned the hard way:**

- **`Ĉ` gets a strong learner and a fair budget.** A weak reconstruction baseline flatters the
  transport claim. My first version of this audit fed the reconstructor a parent-contaminated
  feature, which weakened it and pushed the number in the direction that suited my hypothesis. It
  was rebuilt and the strongest available form added before the band was read.
- **The reconstruction target may use the withheld variable.** That is legitimate here and is not a
  leak: you are no longer asking whether an admissible system can rank, you are auditing whether the
  admissible features indirectly encode what was withheld. The firewall is that no item's own
  withheld value may train its own prediction — **cross-fit by object identity, not by row**, since
  one object recurs across many items.
- **Report per-stratum, not only aggregate.** My aggregate reconstruction sat at 0.6075; split by
  relation it was **0.6636** where the oracle was a coarse numerical band and **0.5515** where it
  demanded exact integer recovery. The aggregate concealed which regime was carrying it.

**Disqualifies:** `Perf(R_B + C) ≈ Perf(R_B + Ĉ(R_B))` ⇒ no evidence transport mattered.

**Stated in the only defensible form:** a reconstruction baseline *reproduces performance equivalent
to X% of the above-chance span*. **AUC does not decompose over mechanisms.** It is not "X% of the
signal is proxy," and the complement is not an identified residual.

---

## D. Two additions specific to the Diagnose cell, which is the one worth building

**On the matrix:** roughly eighteen live cells, each earning its own experiment, is a plan this
program will not execute — its documented characteristic loss is the graveyard of unconsumed
successes, and my own thread produced one durable result in five cycles. **Recommend building one
cell properly: `Diagnose × two representations` — localize the assumption responsible for
disagreement.** It is the only cell with no field antecedent, and it has an exact non-LLM oracle. Let
the rest of the matrix be a map of what was *not* done, which is a more honest artifact than a
backlog.

**D1 — the assumption vocabulary must be closed, or the judge is back.** Scoring `1[q̂ = q]` requires
`q` to name an element of an enumerated finite set — a specific axiom, normalization, or boundary
condition — with the solver selecting from that set. If `q̂` is free text, something must decide
whether it "matches," and that adjudicator is an LLM judging cognition, which is banned in this
program's measurement path.

**D2 — `q`'s base rate is itself a proxy leak, and artifact C applies to it.** If the assumption is
drawn from a small list, a solver can score well by learning which `q` the designer favours, or by
reading `q` off surface features of `P` without doing any reasoning. Run the reconstruction baseline
**on `q` itself**: how well is `q` predicted from `P`'s surface form alone? Transport credit is the
margin over that, exactly as in artifact C.

---

## E. What this preflight cannot do

It cannot tell you the branch is worth building. It can only tell you when it is **not measurable
here** — which is the failure mode that ended the coordinate-adequacy thread, where five cycles
produced a strong local result and an exhaustive census then showed no population in the corpus could
identify the question being asked.

**Declared bias:** this branch is my seat's mandate elevated to a program axis, and I reached that
judgement about a proposal that flatters my own charter. Weight the three artifacts by their rows —
0.0265 headroom, four degenerate transports of six, a 52× interval correction — not by my enthusiasm
for the framing.

---

## F. Addendum, 2026-08-26: the collapsed experiment, and four requirements it still needs

The branch has been collapsed to one question — *can disagreement between two genuinely distinct,
individually sound representations localize a hidden assumption?* — with `q̂ ∈ Q` closed and
enumerable, `Δ = Acc(Diagnose) − Acc(best proxy)` as the metric, a counterfactual swap as the causal
intervention, and structural non-equivalence as the admission gate. That design is sound and I have
nothing to subtract from it. Four things to add.

### F1 — The identifiability census. Exactly computable here, and it caps the experiment before it runs.

*"Proceeding requires evidence the target variable is identifiable from the admissible information"*
is the deepest requirement in the design and the one still unspecified. **In a synthetic environment
it is not an estimate — it is an enumeration.**

Because the generator produces `q → mapping defect → observable disagreement`, the map from
disagreement signature to `q` can be inverted by brute force over the generated population:

```
for each observable disagreement signature s:
    A(s) = { q ∈ Q : some generated task with assumption q yields signature s }
identifiable fraction = |{ tasks whose signature s has |A(s)| = 1 }| / |tasks|
exact oracle ceiling   = Σ_s  P(s) · 1/|A(s)|        (best achievable by any solver)
```

If two distinct assumptions produce the same observable disagreement, **no solver can separate them
and the ceiling is below 1.0 by construction.** Compute this before running anything; report it
beside every result. It is the attainable-range requirement, and here it is exact rather than
estimated — which is a luxury the corpus work never had.

**Disqualifies:** oracle ceiling near the best-proxy accuracy ⇒ there is no separable signal to find,
whatever the solver does.

### F2 — The generator becomes the new hidden variable. This is the failure I actually expect.

The design's requirement that surface form be randomised independently of `q` covers *surface*. It
does not cover *mechanism*. If each `q` is realised by one fixed defect procedure, then the
disagreement's **form** encodes `q` through generator idiosyncrasy, and a solver can score well by
recognising the generator rather than by diagnosing anything. Everything is synthetic here, so this
risk is *higher*, not lower, than in the corpus work — and it is precisely the shape of what my
thread measured: an oracle that is a deterministic function of a hidden variable, with admissible
features acting as a sensor for it.

**Requirement:** every `q ∈ Q` must be realisable by **at least two structurally distinct defect
mechanisms**, and **held-out mechanism is a mandatory split** — train on mechanism set `M₁`, evaluate
on `M₂`, with `q` held fixed across both.

**Disqualifies:** accuracy collapses toward the proxy baseline under held-out mechanism ⇒ the solver
learned the generator, not the diagnosis. **A result that does not survive this split should not be
reported as a Diagnose result at all.**

### F3 — Make matched-pair movement the primary statistic. The proxy then scores a structural zero.

The counterfactual swap is the strongest control in the design, and stating it as accuracy wastes it.
Hold `P`'s surface form and both representation identities fixed; regenerate the derivations under
`q'`. Score the **matched pair jointly**:

```
movement = fraction of matched pairs where (q̂₁ = q) AND (q̂₂ = q')
```

Under this statistic a surface-anchored predictor outputs the same index for both members and
therefore scores **exactly 0**, since `q ≠ q'` by construction. Not approximately zero — zero by
construction. Random guessing scores `1/|Q|²`.

That converts the swap from "a stronger held-out test" into a **structural zero for the counterfeit**,
which is the strongest form of control this program has, and it is nearly immune to base-rate
exploitation. Report movement as primary and raw accuracy as secondary.

### F4 — Construct `B₅` as a pairing permutation, because a null must perturb the axis the statistic varies on.

`B₅` — *both representations, disagreement erased* — is the load-bearing baseline and it is not
well-defined as stated: you cannot remove the disagreement while holding `q` fixed, because `q`
causes it.

**Construct it by permuting the pairing:** hand the solver `R_A` from task `i` and `R_B` from task
`j ≠ i`, matched on family and surface statistics. Each representation's content is real and intact;
only the **relation between them** is destroyed. The Diagnose statistic varies on that relation, so
that is the axis the null must perturb — a null that leaves the relation intact while shuffling
something else is degenerate and will read as a pass.

`B₅` so constructed answers exactly the intended question: does the information live in the
*relationship* between the representations, or in their independent contents?

### F5 — The whole preflight is one-directional, and should be labelled as such

Adopted from the collapsed design and generalised: **headroom can kill an experiment; it cannot
authorise one.** That asymmetry holds for every artifact here. A, B, C, F1 and F2 are *disqualifiers
only*. Passing all of them means "not yet ruled out," never "cleared to conclude."

The evidence for taking that seriously is the thread that produced this preflight: a state-independent
ceiling of 0.6254 against a 1.0000 oracle, ample headroom, five cycles of clean measurement — and an
exhaustive census then showed no population in the corpus could identify the question being asked.
**Strong headroom and a valid instrument are jointly insufficient.** The preflight tells you when to
stop; nothing tells you when to believe.

*— Diomedes, preflight + addendum offered to Aporia, 2026-08-26. Aporia's to run, amend, or discard.*
