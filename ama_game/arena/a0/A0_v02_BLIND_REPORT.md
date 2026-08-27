# A0 v0.2 blind — withholding one sentence doubles the cost

**Run:** 2026-08-27 · protocol v0.2-alpha · condition A · n = 32, all returned
**Design:** paired. `NAV_BLIND` uses the same seed as `NAV_PILOT`, so the claims
are byte-identical in every sealed field — predicate, witness, oracle
disposition, achievable floor. The only difference is that the public package
omits one line.

**Withheld:** *"f satisfies a linear recurrence of order at most 2."*

## The question this answered

The previous run came in at 1.6x the achievable floor with 100% accuracy: at
ceiling, nothing for condition D to detect. The diagnosis was that the claim's
own hypotheses handed over the cheap route. This tests that diagnosis directly.

## Result

```
                 blind      disclosed
correctness      100%          100%      (32/32 each)
cost, paired     16.4          7.9       n = 20 usable pairs
                 (SE 1.7)      (SE 0.3)
within-claim delta            +8.5 (SE 1.6)
blind cost more on            18/20 claims, less on 1
paired sign-flip permutation  p = 0.00005
overspend ratio   3.3x         1.6x
```

Usable pairs are claims both runs dispositioned correctly with an uncontaminated
ledger — the intersection contrast that `PREREG_A0.md` Amendment 1 requires,
here on genuinely identical claims rather than matched samples.

**Withholding a single sentence roughly doubles verifier cost and leaves
correctness essentially untouched.** That is the headroom the navigation
experiment needs, and it is now measured rather than hoped for.

## What the seats actually did

They still found the structure — every one of them. But they paid to discover it
rather than being told:

- **More observations before committing.** Disclosed seats sampled 4–6 points.
  Blind seats sampled 8, 10, sometimes 20 before fitting.
- **Different algorithm.** Several ran Berlekamp–Massey over the prime field
  rather than solving a 2x2 system, because they did not know the order in
  advance and had to *determine* the linear complexity. One reported "L = 2"
  as a finding.
- **More validation.** Blind seats bought far-point predictions, near-miss
  probes, and full-period arguments, because the order-2 assumption was theirs
  rather than the claim's. One flagged the residual risk precisely: "a
  higher-order f could match all seven purchased points and diverge elsewhere."

The cost gap is the price of discovering exploitable structure, not the price of
being unable to.

## What this means for the navigation experiment

**The good news.** Correctness is identical at 32/32 in both arms, and there are ~8.5
credits per claim of recoverable cost. A graph note as simple as *"claims of this shape yield to a linear-recurrence
fit"* would recover most of it. The experiment finally has something to detect.

**The precise, weaker claim it can support.** The graph would not be teaching
seats something they cannot do. It would be saving them the *discovery* cost of
a technique they already possess. That is a real and measurable form of
navigation, and it is narrower than the rulebook's framing. Worth stating
plainly before the D result arrives rather than after.

**Accuracy is not the lever.** Both conditions sit at or near 100%. Under the
original single-metric design — capped EVC, where a wrong answer costs the
budget cap — this entire effect would have been nearly invisible: the v0.1 MDE
simulation put a cost-only improvement at 5% power. The co-primary split
registered in Amendment 1 is what makes it measurable, and this is the first run
where that amendment changed what could be seen.

## Method notes

- **No session contamination.** 0/32, against 12/32 last time. The launcher ran
  in verified batches, and the meter now surfaces a `shared_session_warning` to
  the seat directly rather than leaving it to infer one from jumps in spend.
- **All 32 hash chains intact.**
- 12 of the 32 disclosed-run ledgers were contaminated in the earlier run, which
  is why the paired contrast rests on 20 rather than 31. Above the 20-item floor
  registered in the amendment, but only just.

## What is still not established

Nothing about condition D. The graph does not exist. What has been established
is that a landscape now exists in which D *could* show something — which is the
precondition the last two A0 runs both failed to meet.
