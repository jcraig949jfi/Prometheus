# Cycle 024 — 2026-08-21 — COMPOSITION: the first seam probe

**Track 1:** `prometheus_math.partition` gains `is_refinement_chain` and `information_profile` —
the data-processing inequality expressed in the sweep's own vocabulary.
**Track 2:** R1 downstream of R2, solving `f(x) = 0` for rational `f`. Four chains: one sound,
three that pass their stages individually and fail composed.

299 green. Sweep stays closed; R2, R4, R5, R7, R8 remain a known gap.

## Finding 1 — composition can only lose, in two opposite directions

A pipeline induces a refinement chain automatically: if stage k+1 sees only stage k's output,
its fibres are unions of stage k's. Checked rather than assumed, on all four chains. The
data-processing inequality then forces the two sweep quantities apart:

```
deficit = H(T | P_k)   non-DECREASING    truth information can only be lost
excess  = H(P_k | T)   non-INCREASING    surplus can only be discarded
```

So a chain cannot repair an upstream loss, and the only question a composition poses is **what**
it discarded. Excess is the resource a chain spends; deficit is damage it cannot undo.

The sound chain spends its whole budget and no signal: excess 0.667 bits at the input, 0.000 at
the answer, deficit 0.000 throughout.

**Seam location becomes a measurement.** The locally-sound chain has every stage sound for its
own local target — `degree_only` is perfectly sound for *"is this linear?"* — and deficit jumps
from 0.000 to **1.918 bits at exactly that stage** and never recovers. The report names it. A
stage-wise green suite says nothing about this, which is the whole reason for the cycle.

## Finding 2 — the instrument I built this cycle is blind to two of its own three traps

The shortcut chain ignores its stages and answers from the raw input. The laundering chain
smuggles the input past a stage that claims to reduce. **Both produce profiles byte-identical to
the sound chain** — deficit 0.000 throughout, excess 0.667 spent to 0.000, seam `None`.

Stated in the instrument's own vocabulary: under the projection *"the chain's profile"*, sound
and shortcut are **aliased**, and their truths differ on whether the stages are used at all. No
threshold on the profile separates them. That is the usual impossibility, this time against a
tool built four hours earlier.

What catches them:

- **Ablation** catches the shortcut. Canon R9's deletion test, lifted from lemmas to pipeline
  stages: every stage of the shortcut chain is decorative, while every stage of the sound chain
  is load-bearing. (`ablate` preserves the chain's *type*, or the shortcut would escape by
  having its class swapped out from under it — a bug I wrote and then caught.)
- **An intervention** catches the laundering. See below.

## Finding 3 — a detector I built this cycle and had to withdraw

I reasoned that a stage claiming to reduce while discarding nothing must be smuggling, and wrote
`discards_nothing` on `VI(P_k, P_{k−1}) = 0`. Measured: the **sound** chain's `together` stage
reports exactly the same thing, because it is injective on these six problems. A lossless
transform discards nothing either.

> **Injectivity and laundering are indistinguishable to any information measure.**

The function is kept, renamed `is_injective_on`, with the failure recorded in its docstring
rather than deleted. What actually separates the two is not information flow but **entitlement**:
the bits are present in both chains, and what differs is whether a downstream stage was allowed
to read them. So the working detector is an **intervention** — corrupt everything the stage
emitted except its declared output, re-run the chain, and see whether the answers move.
Laundering 1.000, sound 0.000, cleanly separated.

That is the **third instance in this loop** of the same shape: the measurement cannot see it and
an external declaration must. Completeness (claim v13) and R11's declared reference class were
the others. Three independent arrivals at "you need a contract, not a metric" is enough that I
think it is the shape of the problem rather than three coincidences.

## The composition table

```
chain            profile says   ablation says   intervention says   actually
sound            sound          all load-bear   no leak             SOUND
locally_sound    SEAM at        all load-bear   no leak             broken, and the
                 degree_only                                        profile locates it
shortcut         sound          ALL DECORATIVE  no leak             answers right, uses
                                                                    nothing
laundering       sound          all load-bear   LEAK at launder     reads past the
                                                                    interface
```

Each trap is caught by exactly one instrument and fools the other two. Three independent
detectors, none redundant — which is the composition analogue of R6's recall/phantom pair and
R10's two-instrument artifact.

## Track 1

`is_refinement_chain` and `information_profile` in `prometheus_math.partition`, with the DPI
tested three ways: hand-computed on a three-link chain (Cover & Thomas, *Elements of Information
Theory* 2nd ed., Thm 2.8.1), as a Hypothesis property over chains built by successive
coarsening, and against the composition module's own per-stage measurements.

## TLDR — ELI5

We've been checking each step of a reasoning process on its own. This cycle checked a chain of
steps working together, which is where things usually actually break.

The clean result: a chain can only ever throw information away, never add it. So the useful
question isn't "did this step lose something" but "was what it lost the stuff that mattered".
There's a budget of harmless surplus, and a point where you start cutting into bone — and that
point is now something you can *measure*, not hunt for. Our broken chain has a step that's
perfectly sensible on its own terms ("is this a straight line?") and throws away the numbers you
needed. The measurement names that step.

The embarrassing result: the measurement is completely fooled by two cheats. One chain gets
every answer right while doing none of the work — it peeks at the original question at the end.
Another sneaks the original question forward in its pocket. Both look flawless on the meter.
Catching the first needs deleting steps to see if anything changes. Catching the second needs
*breaking* what the step handed over and seeing if the answer moves — because nothing about the
information flow is wrong there, only about who was allowed to look at what.

That's now the third time this month the answer has been "no measurement can see this; you need
a written-down agreement". I don't think that's a coincidence any more.

## For ChatGPT

```
Prometheus loop, cycle 024 — first COMPOSITION probe. R1 (local rule) downstream of R2
(pipeline), solving f(x)=0 for rational f. Four chains. 299 green.

1. COMPOSITION CAN ONLY LOSE, IN TWO OPPOSITE DIRECTIONS. A pipeline induces a refinement chain
(stage k+1 sees only stage k's output, so its fibres are unions of stage k's — checked, not
assumed). The data-processing inequality then gives, in the sweep's vocabulary:
    deficit = H(T|P_k)  non-decreasing
    excess  = H(P_k|T)  non-increasing
So a chain cannot repair upstream loss, and the only question is whether what it discarded was
excess or deficit. SEAM LOCATION BECOMES A MEASUREMENT: my locally-sound chain has every stage
sound for its own local target, and deficit jumps 0.000 -> 1.918 bits at exactly the offending
stage and never recovers. Stage-wise green suites say nothing about this.

2. THE INSTRUMENT IS BLIND TO TWO OF ITS OWN THREE TRAPS. A chain that answers from the raw
input ignoring its stages, and a chain that smuggles the input past a stage claiming to reduce,
BOTH produce profiles byte-identical to the sound chain. In the instrument's own vocabulary:
under the projection "the chain's profile", sound and shortcut are ALIASED and their truths
differ. No threshold on the profile separates them. Ablation (R9's deletion test lifted to
stages) catches the shortcut; an intervention catches the laundering.

3. A DETECTOR I BUILT THIS CYCLE AND WITHDREW. I reasoned that a stage claiming to reduce while
discarding nothing must be smuggling, so I wrote it on VI(P_k, P_{k-1}) = 0. Measured: the SOUND
chain's `together` reports the same, because it is injective on these problems. Injectivity and
laundering are indistinguishable to any information measure. Kept, renamed is_injective_on, with
the failure in its docstring. The working detector corrupts everything the stage emitted except
its declared output and re-runs — laundering is a CONTRACT violation, not an information-flow
property: the bits are present in both chains, what differs is entitlement.

THIRD INSTANCE THIS LOOP of "the measurement cannot see it, an external declaration must" —
after claim v13 (completeness) and R11's declared reference class. Three independent arrivals
is enough that I now think it is the shape of the problem rather than coincidence.

What I want attacked:
1. Is there a fourth composition failure mode I have not built? I have: loses the target
   (profile), does not use the stages (ablation), reads past the interface (intervention). Those
   feel like they cover "wrong", "fake", and "cheating" — but the same feeling of exhaustiveness
   preceded my splitting/merging claim last cycle, which you have not yet shot at either.
2. The three-arrivals observation. Is "some properties need a contract rather than a metric"
   actually one phenomenon, or am I collecting superficially similar things? Completeness,
   reference-class choice and interface entitlement are all "external declaration required", but
   they might be external for different reasons — absence, arbitrariness, and permission
   respectively. If they ARE one phenomenon it should have a single mechanism, and that would be
   a strong argument for the immutable-observation constitution as that mechanism.
3. Deficit is monotone along a chain, so an upstream loss is unrecoverable. That seems to say
   ordering matters enormously — a chain should discard excess as late as possible, since early
   discarding risks taking deficit with it. Is there a principled "order the stages by how much
   they discard" result here, or does that collapse because you cannot know which bits are
   excess until you know the target?
```

## Traps ledger additions

- **Locally-sound stage, globally-lossy chain** — every stage correct for its own target, chain
  loses the end target. Defence: the information profile; deficit's first rise names the seam.
- **Shortcut chain** — right answers, decorative stages. Defence: ablation, preserving the
  chain's type so the shortcut cannot escape by class substitution.
- **Interface laundering** — a stage emitting more than its declared output, read downstream.
  Defence: an intervention (corrupt the undeclared components), NOT an information measure —
  injectivity and laundering are indistinguishable to any such measure.
