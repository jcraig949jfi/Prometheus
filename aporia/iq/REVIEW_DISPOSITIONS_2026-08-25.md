# External review — dispositions

Review received 2026-08-25. Disposition vocabulary: **fixed** / **acknowledged** / **rebutted**.
Reviewer's stated disposition adopted as the arc's own: **ADVANCE the assay as a microscope ·
PARK any compass claim · REDESIGN the selector test before running it.**

---

## R1 — Claim-object provenance is the critical epistemic hole. **ACKNOWLEDGED, blocking.**

Correct, and it is the weakness I named first myself. The chain is
`RESULT artifact → my interpretation → claim object → gate → verdict`, and the gate is
deterministic only *after* the lossy step. It cannot catch a mistranscribed numerator, a wrong
denominator, a wrong population, an omitted qualifier, or a swapped experiment identity.

Adopted verbatim: **hashes and filenames are insufficient; the gate must consume the underlying
observations.** Until BATTERY recomputes every field it uses directly from the RESULT artifact,
its 6/6 retro-validation is **suggestive bookkeeping, not detector validity**, and it is recorded
that way from here on.

Adopted: **no further experimental run before this is fixed.** That supersedes my own plan to
run ABLATION next.

## R2 — "Ceiling unchanged" was an unmeasured extrapolation. **FIXED — the proof exists and I should have made it.**

The reviewer is right that two witnesses do not establish `E(C_abstain, T) = E(C, T)`, and right
that the monotonic argument closes it. Making it formally:

**Lemma (last writer wins).** Scorers write only `selected_answer` and `candidate_scores`. No
operator in the registry *declares a read* of either, and no guard's predicate references either
— **verified by execution over all 27 registry entries: both lists are empty.** So abstaining
cannot enable or disable any downstream operator; it can only remove an emission.

**Therefore for every program g and every task t:** under abstention the final writer either
emits what it emitted before, or emits nothing. Removing an emission can turn a correct answer
into no answer, or a wrong answer into no answer. Neither creates a correct answer. Hence
`acc_abstain(g) ≤ acc_C(g)` pointwise, so

    E(C_abstain, T) ≤ E(C, T) = 0.8333          (monotonicity)
    E(C_abstain, T) ≥ 0.8333                    (the witness, measured)
    ⟹ E(C_abstain, T) = 0.8333 EXACTLY

**The abstain-regime ceiling is now closed**, not extrapolated — which is the reviewer's action
item 2, delivered by argument plus one executed check rather than by re-running the BFS. The
headline is corrected from *"ceiling unchanged"* (an inference) to *"ceiling equal, by
monotonicity plus witness"* (a proof with a stated and verified precondition).

## R3 — "Inert for capability" overreaches. **FIXED.**

Accepted without reservation. The experiment supports **"inert for the observed ceiling
solutions"** and no more. The scorers may matter in non-ceiling programs, in mutation
trajectories, and in categories outside the current winners. Every future use of that claim
carries the narrower wording.

The mutation-corruption half stands, and the reviewer's framing is sharper than mine: a default
first-candidate response gives semantically failed programs a nonzero score, so **mutation
ranking can reward noise — a substrate defect capable of manufacturing fake evolutionary
gradients.** That is now the headline of that finding rather than a corollary.

## R4 — The rotation probe is not a semantic oracle. **ACKNOWLEDGED; the prescription is better than mine.**

I had planned to "enumerate whether an order-dependent scorer exists." The reviewer is right that
this tests an undocumented convention. Adopted: **declare a permutation-invariance contract per
scorer, and apply rotation only to scorers whose semantics are declared invariant.** Intentional
priority semantics, stable tie-breaking over ordered candidates, and first-valid/leftmost
specifications are all legitimate and would be misread as guessing.

## R5 — TRANSFER-1 falsifies the compass story more than ΔE_port supports it. **ACKNOWLEDGED as the conceptual centre.**

This is the sharpest point in the review and I did not state it this way. The port gains +5/120
under the route it was designed around and fires **0/200** under held-out construction, so ΔE has
shown *"this primitive expands reachable outputs under this representation"* and not *"this
primitive captures a reusable capability."*

Adopted: **ΔE currently measures extension of the ISA, not acquisition of an abstraction.**

Adopted as standing taxonomy for every future ΔE win:

    adapter gain          exposes information already latent elsewhere
    route-specific gain   solves one construction/encoding only
    abstraction gain      transfers across independently generated realizations

**Only the third earns capability-acquisition language.** By this taxonomy `op_all_but_n` is an
**adapter gain** — which the injection result already implied and I under-read.

## R6 — Do not let a corrected result inherit its original preregistration status. **FIXED.**

Accepted; this is the right epistemic hygiene and my version blurred it. TRANSFER-1 is recorded
from here as:

    PREREGISTERED GATE:      FAIL        (mutant bar 0.10 sat below the 1/k floor of 0.25)
    GATE ASSUMPTION:         FALSIFIED
    CORRECTED INTERPRETATION: mutants at 0.1366 are the substrate's 1/k floor, not capability

The experiment exposing a defect in its own gate is the event worth preserving. Reclassifying the
gate as passed would erase it.

## R7 — BATTERY is a codified checklist until proven otherwise; split it. **FIXED in design, ACKNOWLEDGED in status.**

Accepted: 6/6 on the defects that generated the six rules is near-tautological, and the 5/7
prospective coverage is *revealing* rather than incidental. **A gate that needs post-hoc fields is
not a preregistration gate.**

Adopted: split into **design admissibility** (evaluable on a preregistration) and **result
interpretation** (G-VACUOUS, G-INERT, and anything else keyed on realised outcomes). Calling the
whole thing a preregistration battery muddied the contract, and that was my error in naming.

## R8 — Single-seed criticism should be selective, not uniform. **FIXED — and this corrects me in the generous direction.**

Accepted. I had been applying a blanket "single seed, no intervals" caveat that is wrong for
exhaustive facts. Corrected classification:

    EXHAUSTIVE / DETERMINISTIC — no interval appropriate
      provenance: 0 of 464,652 non-port pipelines reach 5/5
      ΔE on the frozen 120-task battery
      the abstain-ceiling equality above
    SAMPLED FROM A DISTRIBUTION — interval required, currently absent
      TRANSFER-1's 400/200/200 draws from the generator
      the X-heldout 0/200

**TRANSFER-1 needs intervals and does not have them.** That is now a specific debt rather than a
blanket disclaimer.

## R9 — The selector question is circular as posed. **ACCEPTED; SELECTOR is withdrawn and redesigned.**

The decisive objection: if "correct capability" is defined by the same frozen battery, ΔE wins by
construction; if by held-out transfer, the port already looks bad. My PF3 pre-flight caught that
the DV could not *vary*; it did not catch that the DV was the *wrong target*. The reviewer's
point is upstream of mine.

Adopted design:

> Does ΔE_C(p) predict U(p), where U(p) is independently measured downstream utility —
> transfer across held-out constructions, task families, or representations — rather than
> another statistic computed from T?

with the requirement I would have got wrong: **the candidate set must contain failures as well as
successes.** One positive port and null controls cannot establish ranking ability. The assay is a
**rank correlation between ΔE and held-out utility**, not a five-selector horse race.

The preregistered SELECTOR at `01bfbfa6` is **withdrawn as mis-specified.** Its VACUOUS
pre-flight result stands as a measurement of pool headroom and nothing more.

## R10 — ΔE may diagnose interface impoverishment rather than capability absence. **ACCEPTED, and it reframes the arc's best finding.**

If C's existing tail already solved the category once supplied the count, then `op_all_but_n` may
expose a **missing intermediate representation** rather than a missing verb. Then
`E(C,T)` tells you *where the instruction set cannot express a needed intermediate* — not *which
abstraction to learn*. That is a more useful and more modest reading of the instrument than the
one I was carrying, and it is consistent with every measurement in the arc.

## Adopted next actions, in the reviewer's order

1. **Machine-bind BATTERY claim objects to raw RESULT artifacts** — gate recomputes every field it
   uses. **Blocking: no experimental run before this.**
2. **Close the abstain ceiling** — **DONE ABOVE** by monotonicity plus witness, with the
   precondition verified by execution.
3. **Replace SELECTOR with a ΔE → held-out-utility rank-correlation test**, over a candidate set
   containing failures.

## What I am not conceding

Nothing in this review is rebutted. The two places I would add rather than argue: the abstain
ceiling is closed by proof and no longer needs re-maximization (R2 delivered), and the
monotonicity precondition is executed rather than assumed, which is the standard the review is
holding the rest of the arc to.
