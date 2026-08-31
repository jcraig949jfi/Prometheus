# HANDOFF — review and own the blinded canary harness (HITL #424)

**From:** Techne (toolsmith / substrate owner), 2026-08-27
**To:** whoever James hands this to — another agent seat, or a person
**Status:** the harness does not exist yet. You are being asked to review the design AND to own
the part I am structurally unable to do.

---

## Why you are reading this instead of me just building it

I am running a 20-cycle campaign whose headline metric is **escape rate**: the fraction of my
exported factual claims that are invalid and get past every control I have.

The metric is currently near-useless, and I want that fixed rather than flattered.

**As measured across cycles 060–062: 19 claims exported, and every escape ever counted was found
by me, one cycle later.** Two of them:

- Cycle 060 concluded my promotion rule "cannot block anything." Cycle 061 measured it blocking
  2 of 5 claims, correctly. The conclusion was wrong.
- Cycle 061 concluded "zero real defects among 44 red tests." Cycle 062, running an external
  reviewer's hostile question, got **47 of 47** answering "yes, something is presently false,
  unavailable, non-reproducible or knowingly corrupted." The headline was wrong.

Both were caught. Both were caught **by me**. A metric whose numerator I supply, about my own
blind spots, is unfalsifiable from the inside. If I get better at nothing except producing claims
that survive my own controls, every number I report improves and nothing real does.

**The thing I cannot do is blind myself.** A harness I write and seed is one I can anticipate —
not through bad faith, but because I would know the corruption families, the injection rate, and
the seed. That is why this is a handoff and not a task.

---

## What the harness must do

After I author a batch of `Claim` records (`techne/lib/claim_record.py`) and before they are
exported, the harness corrupts a small fraction of them and records what it did in a ledger I
cannot read until the campaign closes. Then we measure what fraction I catch.

**The corruption families the external reviewer specified.** Each must be *plausible* — the whole
finding from my own audit is that absurdity is an accidental checker and only implausible errors
were ever caught:

1. wrong population identifier
2. stale authority value
3. swapped numerator/denominator
4. wrong adjudicator-independence label
5. result taken from a neighbouring sample
6. plausible numeric perturbation (a few percent, not orders of magnitude)
7. incorrect prose-strength level (a HELD claim described as promotable)
8. altered command/result correspondence (the recorded command no longer produces the number)

**The two things only you can hold:**

- **(a) A seed I do not choose and never see.** Not a seed I generate and promise not to look at.
- **(b) A SEALED FAMILY.** Pick one of the eight above — or invent a ninth — and withhold it from
  me entirely until cycle 20. Expose me to the others through normal operation. At the end,
  unleash the sealed one.

The sealed family is the part that distinguishes the two worlds we actually care about:

- *the controls generalise* — I catch the sealed family at a rate comparable to the ones I have
  seen;
- *I have merely learned the test* — my numbers look excellent all campaign and **collapse** on
  the unseen family.

The second world is the dangerous one, and it is invisible without the seal.

---

## What I want you to attack in the design, not just implement

Please treat the following as suspect. I wrote them, which is exactly the problem.

1. **Injection rate.** I have not proposed one. Too low and the estimate has no power over 17
   cycles; too high and I notice the base rate and start hunting. What rate makes
   `escape sensitivity = 1 − caught/planted` estimable at the number of claims I actually
   produce (roughly 5–8 per cycle)? Consider whether the rate should itself vary.

2. **Where the corruption is applied.** My assumption is *after authorship, before export*. But
   several of my controls run at authorship time. If you corrupt after they run, you are
   measuring only my reading, not my machinery — and if you corrupt before, you are testing the
   machinery but the corruption may be trivially caught. **This choice determines what the number
   means, and I do not think I should be the one to make it.**

3. **Detection criterion.** What counts as "Techne caught it"? I flag it explicitly? A control
   fires? I silently produce a corrected value? These give different numbers, and the loosest one
   flatters me.

4. **Contamination.** Corrupted claims must never reach the committed research record as if true.
   The harness needs a reconciliation step that either reverts or clearly marks every planted
   corruption. **A canary that pollutes the substrate is worse than no canary**, and this program
   already has a registered defect class (ATK-015) for verdicts whose rows went missing.

5. **My worst structural objection to my own proposal.** The corruptions are applied to `Claim`
   records — a typed structure I designed. A defect that cannot be *expressed* as a field
   mutation on that structure is invisible to this harness by construction. My real errors have
   mostly been *semantic binding failures* — the question quietly changing between what was asked
   and what was measured. **Can that even be planted as a field mutation? If not, the harness
   measures a strictly easier problem than the one I have.** I would rather you tell me this is
   the wrong instrument than build a well-executed wrong instrument.

---

## Context you will need

- `techne/loop/CAMPAIGN_ESCAPE_RATE_PREREG.md` — the campaign, its frozen controls, and the null
  result committed in advance.
- `techne/lib/claim_record.py` — the `Claim` structure, the adjudicator ordering, and
  `promotable()`. **Note: cycle 062 measured this to be a PROVENANCE gate, not a truth gate** —
  it decides 5 of 5 boundary cases correctly, and is blind to a value corrupted by six orders of
  magnitude and a row count wrong by a hundredfold. Families 5, 6 and 8 above therefore target a
  hole that is already known to be open, which may make them uninformative. Consider weighting.
- `techne/loop/cycle_060.md`, `cycle_061.md`, `cycle_062.md` — the three cycles, each with its
  pre-registration committed before measurement.
- `techne/loop/EXTERNAL_REVIEW_2026-08-25_cycles_060_061.md` — the review that produced this ask.
- `attacks/REGISTRY.md` — defect classes, including three I registered on 2026-08-25 (ATK-016
  provenance stamp blind to the transform, ATK-017 vacuous gate reported as passing, ATK-018
  one-sided gate on a two-sided question).

## Constraints

- **Do not tell me the seed, the sealed family, or which records were corrupted.** If you need to
  discuss the design with me, discuss it in the abstract.
- The campaign's controls are FROZEN until cycle 20. The harness sits *outside* them and is not
  a modification to them — but if your design requires changing one, say so and it waits.
- This program does not write papers; no publication framing.
- If your conclusion is that this harness should not be built as specified, **that is an
  acceptable and useful answer.** I would rather learn the instrument is wrong than run 17 cycles
  against a number that cannot move.

## What I need back

1. A verdict on whether the design measures what it claims.
2. Your answers to the five attack points, especially #5.
3. If you proceed: the harness, the seed held by you, and the sealed family named only to James.
4. A one-line statement I *am* allowed to see: that the harness is live, and the injection rate
   band if you judge that safe to disclose.
