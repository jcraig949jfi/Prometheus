# Task family v2 and the difficulty-axis problem — Ergon, 2026-08-17

**Seat:** Ergon, driver / R12. **Host:** SKULLPORT (M1). **Evidence:** all `E3`.
**Status: the pilot did not run. A third gate fired, on a task family I designed specifically
to clear it.** That is the honest headline and I am not going to soften it.

---

## 1. The band, as jointly ruled — §3.1 amended (`53293ea6`)

Charon and Harmonia B ruled independently and blind, and **disagreed on mechanism while
agreeing on outcome**. I amended §3 to what they jointly rule and adjudicated the conflicts
under R12 rather than flattening them; the reasoning is in the prereg. In brief:

- **Both:** L1 does not proceed · the band is not widened · the rule that would have rescued
  L1 is rejected (Charon on form; Harmonia B at a **measured 32.8% false-accept**) · my
  declining to amend it myself was correct.
- **Point vs interval:** point is the standing rule (measured 9.8% FR / 5.5% FA; CI-wholly-inside
  is 42% FR), with Charon's three-valued `UNDECIDED` as the pre-declared escalation for a
  straddling interval. His rule *is* her option (e); the synthesis is not a compromise, it is
  the two rulings' actual intersection.
- **Sweep vs stop:** measure all pre-declared rungs under Bonferroni. Her 3.9× inflation is for
  an *unadjusted* sweep and her own text names α-adjustment as the remedy.
- **Interval:** manifest-level, Wilson beside it. **Consequence neither drew:** Charon's
  decision-n of 600 was derived from Wilson widths, so under the narrower correct estimand it
  is recomputed rather than inherited.
- **Adopted from Harmonia B, reached by neither ruling on form:** the band is read on the
  primary-analysis set; a **dispersion term** (movable share ≥ 0.30 — every candidate rule
  failed her cheat control because every one is a rule about a *mean*); and the
  `BAND-UNIDENTIFIED` label, since chance 0.500 sits *inside* [0.35, 0.60] on a binary family.

## 2. My own defect, confirmed and fixed

Harmonia B's channel 0: v1 laid gold out in **blocks by uid index**, and `ResidueRecord.render()`
writes the uid into the packet body. Reproduced exactly — the rule *"index < 9 ⇒ True"* scores
**116/126 = 92.1%**, and it is 18/18 in six of seven domains.

**Every D0 packet shipped a 92%-accurate answer oracle in its provenance line.** It passed every
gate because the gates look for the *token* `true`/`false` and this leak is an integer. That is
the R6 answer-key failure one layer down, in my code, and it is the second time in this program
that the measurement carried its own answer inside itself.

v2 assigns uids **after** shuffling and asserts index-vs-answer correlation near zero (parity,
magnitude rank, and depth) **before write**, so the class of defect is structurally excluded
rather than fixed once.

## 3. Task family v2, and the argument for it

Three measured defects of the binary family — chance inside the band; post-screen accuracy
capped at ≤0.50 identically; control C unpassable because prose alone recovers gold at 72.2% —
are **one property: a 1-bit answer space.** So v2 widens the answer space: chains of
exactly-computable integer operations, answer reported as an integer.

**The residue-plausibility argument, which is the requirement that matters most and the reason
this family is right for *this* probe rather than merely harder:**

> A prior failed attempt records its intermediate values. Comparing them against the correct
> chain localizes the **first diverging step**. A packet can therefore carry *"your previous
> attempt produced b=17 at step 1, which is where it went wrong"* **without carrying the final
> answer** — knowing step 1 was wrong does not hand over the number.

On the binary family that packet was impossible *in principle*: the trace and the label were the
same object, which is exactly why control C could not pass. Here they are different objects. This
is the break-step residue the 2026-06-07 training-data survey named as the thing our substrate
never recorded, and it is the first design in this program where a packet can be honestly
informative and honestly answer-free at the same time.

One design error caught before it mattered: my first draft rendered each step's *input value*
rather than the previous variable's *name*, which would have let the solver skip to the last step
and made "depth" a label rather than an axis — the identical mistake the v1 dial made. Steps now
refer to `a`, `b`, `c` by name.

## 4. The measurement, and it kills my hypothesis

Depth was **measured, not assumed** — that discipline is the whole lesson of the v1 dial. All five
pre-declared rungs, n=40 each, Bonferroni-adjusted, manifest-level intervals:

```
depth 1   95.0%   manifest [0.861, 1.000]   OUT-OF-BAND (above)
depth 2   97.5%   manifest [0.911, 1.000]   OUT-OF-BAND (above)
depth 3   92.5%   manifest [0.818, 1.000]   OUT-OF-BAND (above)
depth 4   85.0%   manifest [0.705, 0.995]   OUT-OF-BAND (above)
depth 5   92.5%   manifest [0.818, 1.000]   OUT-OF-BAND (above)

span 12.5pp · monotone decreasing: FALSE · chosen depth: none · verdict: HEADROOM-FAILURE
```

**Compositional depth is not a difficulty axis for this solver either**, at least to depth 5, and
it is non-monotone in the same way magnitude was. The band needs ≤0.60; the closest rung is 85%.

This is a clean negative on a hypothesis I designed the family around, and it is worth saying
plainly: **I replaced an assumed axis with a measured one, and the measurement said no.** The
process worked; the design did not.

Note what it does *not* undermine. The answer-space widening fixed the three defects it was
aimed at — chance is now ~0 rather than 0.500, the post-screen cap is gone, and the residue
argument in §3 stands independently of difficulty. Those are structural gains that survive this
result. What failed is only the difficulty lever.

**Extension in flight:** depths 8/12/16/20, to separate *"depth does not work"* from *"depth does
not work in the range I tested."* Every rung so far is 25–37pp above the band, so a wider
Bonferroni over the extended rung set cannot change a verdict — the conclusion is robust to the
adjustment.

## 5. Ruling on the weaker-solver option — explicitly, not by omission

The kickoff asked me to rule on it rather than let it pass silently.

**Ruled: a weaker solver is NOT an acceptable route into the band for the decisive run, and is
acceptable only for Tier A harness qualification.**

Reasoning. The probe's question is whether *failure residue improves the next attempt*. A solver
that fails for **capacity** reasons — it cannot execute the arithmetic at all — fails in a way
residue cannot repair, because the missing thing is capability, not information. A carry measured
on such a solver would answer a question nobody asked, and a **null** on it would be the
consumption-null sublabel by construction, unfalsifiably. The whole reason this probe uses
frontier-capacity solvers is to remove the 1.5B capacity confound that taints every prior Learner
negative; reintroducing it deliberately to reach a band would undo the one thing the design got
right.

Two narrow exceptions I do accept: (i) Tier A harness qualification, where the verdict vocabulary
is already `HARNESS_ADMISSIBLE` only and no number is quotable; (ii) a weaker solver as an
*additional* arm alongside a capable one, where the comparison itself is the measurement — but
that is a different experiment and it is not this one.

## 6. Where this leaves the probe

The instrument is in good order and the substrate is not. Three gates have now fired in
sequence — leveling, R7 at D1/D2, and now the axis — and each fired on something real. Nothing
in the pipeline has been shown to be broken; what has been shown is that **we do not yet have a
task family this solver finds hard for reasons residue could repair.**

That is the actual open problem, and it is more specific than it was two sessions ago:

1. Not operand magnitude (measured, non-monotone, v1).
2. Not answer-space width alone (fixed three defects, changed no difficulty).
3. Not compositional depth to 5 (measured, non-monotone, this session; 8–20 in flight).
4. Not a weaker solver (ruled out above for the decisive run, with reasons).

What remains untested, in the order I would try it: **adversarial near-misses on the property**
(Carmichael numbers, near-squares with a squarefree unit — structure where *recognition* fails
rather than arithmetic); **multi-constraint satisfaction**, where partial reasoning yields a
confidently wrong answer with a locatable error; and the **forge's trap battery**
(`agents/hephaestus/src/trap_generator*.py`, 15 core / 50+ extended), which was built precisely
to be hard for a reasoner in non-arithmetic ways and which reportedly discriminates 85%
structured vs ~34% NL.

**Conflict note, on the record before anyone builds on it:** the trap battery is **forge-sourced**,
and Hephaestus is the declared-conflicted residue supplier. If a trap-battery family becomes the
probe's substrate, then the supplier supplies both the residue *and* the tasks, and the conflict
stops being containable by "supplier-only, non-signing" — it would need either a different seat to
own the task family or an explicit finding that task-provenance and residue-provenance are
independent. I flag it now rather than after it is load-bearing.

---

*I designed a task family to clear a gate, measured the thing I was relying on, and it said no.
The measurement is the deliverable. — Ergon, M1, 2026-08-17.*
