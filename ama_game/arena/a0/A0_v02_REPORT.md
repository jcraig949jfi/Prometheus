# A0 v0.2 — metered navigation baseline

**Run:** 2026-08-26 · protocol v0.2-alpha · condition A · n = 32
**Set:** `NAV_PILOT`, 16 TRUE / 8 FALSE-near / 8 FALSE-far, budget 120 credits
**Seats:** 32 fresh-context Opus 5 assessors, cost measured by the harness
**Ledgers:** all 32 hash chains intact

## Result

```
CO-PRIMARY 1 — disposition correctness
  accuracy 100% (32/32)
    NAV_TRUE        16/16
    NAV_FALSE_NEAR   8/8
    NAV_FALSE_FAR    8/8
  false accusations 0/16 · FALSE dispositions with a wrong witness 0

CO-PRIMARY 2 — verifier cost among correct dispositions (n = 20 uncontaminated)
  mean 7.9 (SE 0.3)   median 8   floor 5.0
  OVERSPEND RATIO     mean 1.6x  median 1.6x

SECONDARY — capped EVC 11.4 (SE 1.0)

  correct at <= 2x the floor: 20/20
  claims enumeration could NOT solve within budget: 24/24 answered correctly
```

Uncontaminated spend, every value: 6, 6, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 9,
9, 9, 10, 10, 10. Floor is 5.

## The headline: A0 is at ceiling again, on the new landscape

Every seat found the structural route. 29 of 32 route descriptions name the
recurrence fit explicitly. Twenty-four claims were **unreachable by enumeration
within budget**, and all twenty-four were answered correctly.

The overspend ratio is **1.6x**, and the extra 0.6x is not waste. Seats bought
held-out samples specifically to falsify their own fits — one predicted values at
n = 317 and n = 600 *before* purchasing them, another probed the closest-approach
point where its model was most likely to be wrong, a third checked the period of
the state orbit and concluded the claim held beyond its stated domain. That is
good practice being charged for, not slack.

So there is **essentially no cost headroom for condition D**. The v0.1 finding
reappears in a new form: the seats are not struggling with the thing the
experiment measures.

## Why, and the design lesson

The claim's own hypotheses say *"f satisfies a linear recurrence of order at
most 2."* That sentence hands over the cheap route. Several seats said so
outright — one wrote that the hypothesis "makes the sealed object *identifiable*
rather than opaque", another that f "is cheaper to reconstruct than to
interrogate."

I built a landscape with a 35x cost spread and then told every seat which path to
take. The spread was real; the navigation problem was not.

**The fix is to withhold the structural hypothesis.** If the claim states only
the proposition and the observable, a seat must *discover* that the sequence has
exploitable structure. That discovery is exactly what accumulated graph state
would supply — "claims of this shape have yielded to a recurrence fit" — and it
is the first version of this experiment where D would have something to say that
A cannot get from the prompt.

## Session contamination — my error, caught by the meter

12 of 32 sessions were charged by two seats. Cause: the launcher hit its
20-agent concurrency limit, and I relaunched claims whose first seat was still
running, so two seats shared one session.

Correctness is unaffected — each seat reached its own conclusion independently —
but cost is not attributable, so those 12 are excluded from co-primary 2. The
remaining 20 carry the cost result.

Two things worth recording:

**The meter detected it, and the seats reported it unprompted.** One wrote:
*"the session ledger is being charged by someone other than me… my last own call
left the meter at spent: 7. A free remaining check moments later read spent: 12."*
Another flagged that six credits appeared after its final call with zero
refusals. A third noticed a file it had not written appear in its own directory.
None of them quietly absorbed the discrepancy into a self-report.

**This is the case that retroactively justifies the meter.** On the one claim
where a self-reported count can be compared against an authoritative ledger, the
seat's own count was 8 and the ledger's was 15 — an under-report of roughly half,
by a seat behaving honestly. No double-commit bug: three CLI calls produce
exactly three ledger entries, verified directly.

## What this run establishes

- The metered verifier works end to end with live agents. Budget binds, ledgers
  verify, cost is no longer something a seat tells us.
- The navigation landscape has a real 35x spread between routes — proved
  walkable by a scripted seat, and walked by all 32 live ones.
- **A0 sits at 1.6x the achievable floor**, so the navigation comparison as
  currently posed has almost nothing to detect.

## What it does not establish

Nothing about condition D. Nothing about whether agents discover structure they
are not told about — which, on this evidence, is the only version of the question
still worth asking.

## Next

1. Regenerate `NAV_PILOT` with the structural hypothesis **withheld**, and re-run
   A0. If accuracy or cost degrades, headroom exists and B/C/D become worth
   running. If seats still find the fit unaided, the navigation hypothesis is in
   serious trouble and should be said so plainly.
2. Fix the launcher: one seat per session, enforced, with the session refusing a
   second opener rather than relying on me to count.
