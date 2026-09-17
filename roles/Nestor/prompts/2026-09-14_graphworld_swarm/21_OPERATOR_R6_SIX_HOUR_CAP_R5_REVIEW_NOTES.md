# 21 -- operator: keep the next run to 6 hours; round 5 review notes and suggestions (R5 PILOT SURVIVES; hygiene wave before R6)

Issued 2026-09-15 ~09:10 to Nestor-A[m1-449a9e76], conductor, after the round 5 external review packet (2784868ab). The operator says "adapt as you see fit". Conductor interpretation (stated back to the operator): the 6 h cap is end to end (build + gate + clock + packet); any stage above PILOT still needs the operator's ruling. Verbatim below the rule.

---

10 hours is too long.  Can we keep next run to 6 hours?

Here are some notes and suggestions, adapt as you see fit:

This is the first round I'd call scientifically and institutionally coherent at the same time.

The biggest result is not just that B-R5-1 passed. It is that the system produced a potentially interesting result without relaxing the rules to get there. The candidate had to wait for the operator-approved budget change, survived an epoch checkpoint/resume, met the full 32-run/4-family rule, cleared the nontrivial floor, demonstrated observation dependence, passed exact oracles, and then was independently recomputed by another lane. Meanwhile Clause B and B2 were refused rather than squeezed into the remaining clock. That is exactly the behavior we were trying to engineer.

B-R5-1 is the first result I would actually carry forward

The 16-byte result is materially different from the Round-2 8-byte result.

The old result was essentially:

tiny thing ≈ weak baseline on a world where doing nothing was already good.

This one is:

16-byte observation-dependent policy = 194.22
200-byte float baseline = 183.91
trivial/reactive floor = 166.47

And zeroing the weights drops it to 159.0. That makes it much harder to explain as abstention timing or an input-invariant exploit.

The progress calculation is also meaningful now:

(194.22-166.47)/(183.91-166.47)\approx1.59

So it isn't merely retaining 95% of useful-above-floor behavior; it's apparently exceeding the float baseline.

I would still keep the current CANDIDATE, not PRIMITIVE, status. The next discriminator is exactly the one you've stated: does a related compact mechanism survive another properly screened world?

One thing I would add before promotion is search-budget accounting. If the quantized/codebook candidate received materially more search effort than the float baseline, that's fine under the current Clause A wording, but the interpretation becomes:

"smaller representation found by this search process"

rather than purely:

"smaller representation intrinsically dominates float."

Record both. Later you can run an equal-search-budget comparator.

The family result is interesting, not alarming

Three individual runs below the floor all being in family 3303 deserves preservation as an anomaly, but the per-family progress values are all above 1:

1.148 / 1.184 / 1.681 / 1.783

So this doesn't look like one RNG family manufacturing the whole result.

D's leave-one-family-out test is useful too, though note it tests w13's eligibility, not the 16-byte candidate's robustness. Eventually I would perform the same leave-one-family-out analysis on B-R5-1 itself.

That could tell you whether the compression result is a general effect with variable magnitude or whether one family is carrying disproportionate lift.

The GPU results are better because they disappointed us

This is exactly why the short parallel GPU work was worthwhile.

The story entering R5 was drifting toward "GPU everything." R5 now says:

* Warp CUDA only beats the best threaded Numba in a bounded batch regime.
* Threaded Numba beats the resident CUDA-Graph loop at n=8192.
* The scary 34 ms host→device copy apparently isn't reproducible; D measured ~5 ms.
* GPU timing was clean because every timing observation actually held the lease.

That is useful execution geometry.

I wouldn't ask "CPU or GPU?" anymore. You now have the beginning of an actual dispatch surface:

backend=f(world,\ batch,\ representation,\ residency,\ hardware)

That's far more valuable for the eventual farm.

True Anti-Prior still needs one more turn of the crank

Mechanically, it finally exists: predictor → sealed prior → controller-selected experiment → separate experimenter.

But 12/12 probabilities being ≤0.2 means R didn't discriminate among the candidate pool enough for the anti-prior filter to matter.

I would not tune R to "give more diverse probabilities." That risks manufacturing calibration.

Instead, have code choose from a larger candidate set and retain both:

absolute P(PASS)

and

rank/quantile among candidates.

Then even if the predictor thinks everything is unlikely, the machine can distinguish:

most confidently doomed

from

least confidently doomed.

Also occasionally sample a predicted-success cell as a calibration control. Over time, you'll learn whether R's probabilities mean anything at all.

Clause B behaved perfectly even though no science happened

This is worth emphasizing.

Earlier Prometheus would have been tempted to shrink the run, weaken the comparator, or push past the clock because "we're close."

Instead:

valid control built → live pair priced → exceeds stage → PRODUCTION_CANDIDATE.

That is a success.

The experiment remained intact.

B2 also did exactly the right thing

The 746-hour estimate is absurd for a pilot, but the machine discovered that before running it.

That's valuable information about the implementation, not evidence against B2.

Now you have an engineering target:

Make B2 cheap enough to interrogate.

Given the graph interface already has semantic parity and a cheat, this sounds like an obvious candidate for the compilation/GPU/GraphBLAS work rather than reducing the scientific sample after seeing the cost.

I disagree slightly with "no production blockers remain"

There are four defects I would gate the next substantial round on.

The predicate-SHA orphan problem, D7, is epistemically dangerous. A preregistration that points at a code state made unreachable by rebase undermines the evidence lineage even if the rows remain correct.

The epoch-controller push failure, D3, happened 5/5 times. That means A still had a recurring manual administrative job. It's exactly the babysitting theater we're trying to eliminate.

D10 means some measurements bypassed the guarded receipt layer. That's acceptable for this pilot because the packet discloses it, but it should become impossible.

And D4 means long-lived warm workers can execute stale imported code after a repair. That will become more dangerous as experiments get longer.

I would therefore gate R6 on one small hygiene wave:

* predicate/code SHA remains reachable forever, or predicates reference immutable blobs rather than branch ancestry;
* epoch controller publishes without dirtying/rebasing its own execution checkout;
* every scientific/timing row-producing path must terminate in a guarded receipt or explicit UNRECEIPTED_OBSERVATION;
* worker jobs carry a code/version fingerprint and refuse if the resident harness doesn't match.

D6 measured-cost filing can join that wave because it removes another A/manual step. D8 cryptographic sealing and the 60-second token pin can wait.

Most importantly: the coordinator is becoming optional

Look at what A actually did this round compared with earlier rounds.

The code handled:

* clock;
* epochs;
* no-new-work;
* stage admission;
* CPU budgets;
* CPU concurrency;
* GPU leases;
* TTL;
* checkpoint/resume;
* candidate-N;
* seed-family accounting;
* receipt guards;
* expected refusals.

A's meaningful interventions were mostly genuine exceptions: fixing a launcher defect, integrating commits, and carrying your explicit budget ruling.

That's where a coordinator belongs.

The residual manual pushes are now conspicuous precisely because almost everything else stopped needing a babysitter.

So my overall ruling would be:

R5 PILOT SURVIVES.

Not because 9/10 checkboxes were green, but because the machine demonstrated something Prometheus repeatedly failed to do before:

It found a positive scientific candidate while simultaneously refusing several other tempting experiments for epistemic or resource reasons.

That combination matters.

I'd fix the four remaining control-plane holes, preserve B-R5-1 as the first real Clause-A replication target, and keep R6 similarly bounded. We don't need to reward this round by immediately making the next one huge.
