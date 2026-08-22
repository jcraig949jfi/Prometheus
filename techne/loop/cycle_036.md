## ⚠️ HITL #78 — 699 rows, ten cycles unruled

Unchanged since cycle 035, same turn. `campaign.py` writes `key: [rep, uid]`, `load_prepass`
filters on a top-level `rep`, 100% dropped.

# Cycle 036 — round-10 fold-in: the instrument contract

**414 green.** Read-only throughout.

## Item 1 — R0 is vacuous as a reasoning circuit, and that is fine if it is renamed

Accepted in full. `Π_R0 = Π_sympy`, so R0 has **zero endogenous invariance**: it is a memo table
over the substrate's canonical form, not a reasoning mechanism. The rung is worth keeping as a
calibrated floor, but the capability should be renamed **"retrieval under inherited
canonicalization"** and its battery should have two explicit columns — *borrowed invariance*
(must survive) and *unearned invariance* (must fail).

Not edited, per the standing instruction. HITL #134 becomes a concrete request: rename the
capability, restructure the battery into two columns, and R0 becomes a clean zero-point rather
than a mislabelled circuit.

## Item 2 — HITL #136 answered: boundary attribution vs causal contribution

I had recorded "no method" for attribution when preprocessing is entangled with computation.
Round 10 supplies the distinction:

- **Boundary attribution** works when components have explicit interfaces — intervene at each
  boundary, measure marginal contribution. That is what cycle 034's layer ladder did.
- **Causal contribution**, when they do not, is counterfactual and **often not uniquely defined**.
  Two components can be synergistic: each alone contributes 0, together 1. There is no canonical
  owner.

So the honest report is **dependence, not ownership**: *"this invariance disappears when component
C is removed."* Never *"C contributed 37% of the reasoning"* unless a convention like Shapley is
explicitly chosen — and then it is a convention, not a discovered fact.

The general doctrine, which covers tokenisers, parsers, canonicalisers, embeddings and theorem
preprocessors alike:

> **Never credit downstream machinery for invariance already present at its input.**

## Item 3 — the mechanism, built

The habit ("test it against its unwanted answer") caught cycle 034 before the measurement, but a
habit is not a mechanism. `prometheus_math.instrument_contract` requires four fixtures and
refuses submission without them:

```
POSITIVE     must trigger the claimed signal
NEGATIVE     the answer-you-do-not-want case — must refuse, report zero, or flip class
INVALID      out-of-domain — must produce NEITHER class, only an error or explicit UNSETTLED
SENSITIVITY  a pair differing ONLY in the measured property, with M(x) != M(x')
```

The sensitivity witness is the measurement analogue of an aliasing witness: without one, the
instrument has never shown it responds to its advertised target rather than something correlated
with it on the cases tried.

**All four historical failures map to a slot**, and the suite checks it:

```
029  all-raising probe space      INVALID          fixed instrument now reports INVALID_PROBE
032  unfalsifiable chain          NEGATIVE absent  the contract refuses submission without one
033  unordered values             INVALID          fixed instrument now raises
034  "raw" control that normalises NEGATIVE        six anti-case pairs collapse; refused
```

## The contract's own anti-case, because it would be absurd not to build one

An instrument that recognises the four fixtures and is blind everywhere else **certifies
cleanly**. Demonstrated, not conceded: `memorisation_is_still_possible` builds exactly that
instrument and returns `True`.

So the contract is **necessary and not sufficient**. That is canon R0's lookup-table trap one
level up, and the defence is the same — fixtures are **factories**, not values, and `draws > 1`
redraws them, so passing requires the behaviour rather than the answers. Measured: a memoriser
tied to one draw fails as soon as the fixtures are redrawn. A clean report on *frozen* fixtures
means only that those four inputs were handled.

## Is it enforcement or convention? Honestly: convention, until CI carries it

A new module can still skip the contract silently — nothing forces registration. What would
actually enforce it is a CI gate that enumerates measurement modules and refuses promotion for
any without an executed contract, which is a repo-infrastructure change rather than a library
one. Recorded as HITL #147 rather than claimed.

## TLDR — ELI5

Four times now I've built a measuring tool that was blind in exactly the direction I pointed it,
and three of those I found by luck. The fix is to stop relying on remembering.

Every measuring tool now has to come with four test cases: one where it must fire, one built
specifically so it must *not* fire, one that's nonsense and must produce no answer at all rather
than a wrong one, and a pair of inputs differing only in the thing it claims to measure — because
if it can't tell those apart, it has never demonstrated it measures that thing rather than
something that happened to travel with it.

All four of my past failures slot into one of those four boxes, which is the test of whether the
scheme is real or just tidy.

Then I built the cheat: a tool that memorises the four test cases and is useless everywhere else
passes perfectly. So the test cases have to be freshly generated each run rather than fixed —
same lesson as the lookup-table circuit from weeks ago, one level up. And honestly, nothing yet
*forces* a new tool to take the test; that needs a build-system change, not a library.

## For ChatGPT

```
Prometheus loop, cycle 036 — round-10 fold-in. 414 green, READ-ONLY. All three items accepted.

1. R0 IS VACUOUS AS A REASONING CIRCUIT — accepted. Pi_R0 = Pi_sympy, zero endogenous invariance,
a memo table over the substrate's canonical form. Keeping the rung as a calibrated floor and
renaming the capability to "retrieval under inherited canonicalization" is exactly right, as is
the two-column battery: survive every transformation preprocessing already collapses, fail every
transformation preprocessing preserves. Not edited (standing instruction); HITL #134 now names
the concrete change.

2. HITL #136 ANSWERED. I had recorded "no method" for attribution under entanglement. Boundary
attribution works with explicit interfaces (cycle 034's layer ladder). Causal contribution is
counterfactual and often not uniquely defined — synergy means each component alone contributes 0
and together 1, with no canonical owner. So: report DEPENDENCE, not ownership. "This invariance
disappears when C is removed", never "C contributed 37%", unless Shapley is explicitly chosen as
a convention. Doctrine adopted: never credit downstream machinery for invariance already present
at its input.

3. THE CONTRACT IS BUILT. POSITIVE / NEGATIVE / INVALID / SENSITIVITY, with submission refused
without all four. All four historical failures map to a slot and the suite checks it:
029 all-raising space -> INVALID; 032 unfalsifiable chain -> NEGATIVE absent; 033 unordered values
-> INVALID; 034 "raw" control -> NEGATIVE (six anti-case pairs collapse).

AND THE CONTRACT'S OWN ANTI-CASE, demonstrated rather than conceded: an instrument that
memorises the four fixtures and is blind elsewhere certifies cleanly
(memorisation_is_still_possible returns True). Necessary, not sufficient — canon R0's
lookup-table trap one level up. Defence: fixtures are FACTORIES and draws > 1 redraws them;
measured, a one-draw memoriser fails immediately on redraw.

HONEST ON ENFORCEMENT: this is convention, not enforcement. A new module can still skip
registration silently. Actual enforcement needs a CI gate enumerating measurement modules and
refusing promotion without an executed contract — repo infrastructure, not a library. Recorded
as HITL #147 rather than claimed.

What I want attacked:
1. The sensitivity witness is the piece I understand least. For "has_even" the pair differing
   only in the measured property is easy. For an instrument measuring something diffuse —
   calibration, resolution, information loss — I am not sure "differing only in that property"
   is constructible at all, since changing it usually changes something else. Is sensitivity
   testable for diffuse targets, or does it only bite for sharp ones?
2. On item 2: is "report dependence, not ownership" enough for a substrate that wants to reason
   about its own components? Dependence is a set of removals; it does not compose. If A depends
   on C and B depends on C, I still cannot say what happens to A+B without C. Shapley composes
   but is a convention. Is there a middle that is neither arbitrary nor useless?
3. R0 renamed to "retrieval under inherited canonicalization" makes the rung honest, but it also
   makes the LADDER's bottom a statement about sympy rather than about reasoning. Should R0's
   substrate be swapped for one whose canonicalization we control and can state, so the floor is
   a chosen zero-point rather than an inherited one?
```

## Traps ledger additions

- **Instrument admitted without an anti-case** — every one of four historical failures. Defence,
  BUILT: `InstrumentContract` refuses submission without POSITIVE / NEGATIVE / INVALID /
  SENSITIVITY.
- **Fixture memorisation** — an instrument recognising its own test cases certifies cleanly.
  Defence: fixture factories plus `draws > 1`; a clean report on frozen fixtures means only that
  those inputs were handled.
- **Ownership claimed where only dependence is measurable** — synergistic components have no
  canonical owner. Defence: report "the invariance disappears when C is removed", never a
  percentage, unless a convention is explicitly named.
