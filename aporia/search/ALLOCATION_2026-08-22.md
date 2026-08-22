# Allocation pass — SB is blocked on missing data; **Campaign W opens**; my own X-5 recommendation was weaker than I stated

Zero campaigns live, no reserve splits. This pass makes an allocation decision and opens one
campaign. No experiment was run.

## 1. Decision yield across the campaign era (P106–P122), unflattered

    campaign-era passes                       17
    terminal states emitted                    6   ADVANCE 1 · REDESIGN 2 · PARK 3
    last three campaigns                           REDESIGN, PARK, PARK
    claims logged                             69   (51 certain, 14 supported, 4 ambiguous)
    frozen splits burned                       5   2,275 held-out pairs
    frozen-validated effects                   4   1 positive, 3 nulls — all on ONE question
    doctrine rules produced                    3   gate design · branches partition · verdict rules
    reviews with a disposition                 0   nothing here has been externally checked

**Process improving, science flat, and the two separate precisely.** Defect detection moved earlier
every campaign: X caught its problem at terminal, X-2 at terminal, X-3 at terminal, X-4 at pass 2,
X-5 at pass 1. That is a real trend. But five campaigns produced one positive and three nulls about
the same question, and three of six terminal states are PARK — a blocked state, not a decided one.

**The flatness has a specific cause worth naming.** X-3 established that raw term vectors retrieve at
156x chance. That was the gating question — is a search method good enough to point at the target? —
and the answer was yes. The loop then spent four more campaigns trying to *improve* the method rather
than *apply* it. The P106 critique said the loop had a strong adjudicator and no search policy
learning from it; the update is that when the adjudicator says "good enough", the loop keeps
adjudicating.

## 2. The candidate I preferred, and why it failed its own check

The obvious application is the **Sleeping Beauty sweep** — 11 parked `SB-SWEEP` rows over 68,770
zero-connectivity sequences, the target the whole X-line was built to serve. It scores best on
resolvability by a wide margin: the outcome is a count of relations verified **exactly** (operator
holds over at least 20 terms), so existence needs no statistical inference at all — one verified
relation is a discovery, zero is a real null.

**It cannot be opened. The data is not there.** `prometheus_math/databases/oeis_sleeping.json.gz`
holds **212 curated anchors** — A000045 Fibonacci, A000108 Catalan, A000079, A000142, A000040 primes —
the most-referenced sequences in OEIS, the opposite of unreferenced. The 68,770 set requires
*connectivity* data, and the only OEIS files on disk are `stripped.gz` (terms) and `names.gz`
(names). Cross-references are in neither. **Parked with a gate below, rather than redefining the
target to fit the data I happen to have.**

## 3. My X-5 recommendation was weaker than I stated

X-5 recommended one overlap-fix campaign predicting "the elaborate arms' advantage over raw terms
increases." Examining it: `RAW_K = 20` currently equals the benchmark's **minimum** `exact_terms`, so
the raw arm already reads entirely inside the guaranteed window. Correcting to the **per-pair** window
gives raw *more* terms too, up to 45 where `exact_terms` allows. **The correction helps both arms, so
the directional prediction is not clean** — and I did not notice that when I wrote it.

The fix is to change the question, not the prediction. The sharp version is **within-arm**: does
computing features over the guaranteed overlap change L2 *for the same arm*? That is a paired
comparison on the same pairs with no cross-arm confound, and it has a property the X-line never had —
**index reliability affects both windows equally, so no G-null-style gate is needed at all.** The
direction-conditional machinery that cost X-4 and X-5 their terminal states is unnecessary here by
construction.

## 4. Both sides, in numbers

**For Campaign W (window):** it determines whether five campaigns' negative results are trustworthy
or artifactual. X-5 pass 2 showed the V2 image-to-target gap collapses by roughly 100% under length
matching for binomial and moebius and 85% for diff, so the window plausibly distorts everything
measured. If windowing matters, the line's negative reopens with a corrected representation; if it
does not, the negative is **robust and the line closes cleanly**. Either outcome is a decision. Cost
about 4 passes including a fresh build, since no reserve remains.

**Against, and it is not weak:** this is a sixth instrument campaign on a line that has produced its
transferable result. 2,275 held-out pairs are already spent. No reviewer has seen any of it, so the
entire edifice rests on adversarial checks I chose to run against myself. A reader who concluded the
X-line should close now and the four passes go to an entirely different question would be making a
defensible call, and I am not going to pretend otherwise. The tie-breaker is that W can *close* the
line honestly, which nothing else available can.

## 5. CAMPAIGN W — pass-1 preregistration

**Measurable:** `W = L2(features over the guaranteed per-pair overlap) − L2(features over the fixed
45-term window)`, **same arm, same pairs**, top-10, any-valid, `shift` separated and never folded in.
Run for V2 and for raw independently. Fresh benchmark, split development / frozen / **reserve** — the
multi-split design stays, having paid for itself twice.

**Power, from the X-5 discordance range:** paired SE = sqrt(pi/n) at n = 640 four-real-operator
frozen pairs gives 0.0125 at pi = 0.10, **0.0153 at pi = 0.15**, and 0.0177 at pi = 0.20.
**MDE = 0.0306** at the central assumption, to be restated in pass 2 from the observed discordance
rather than inherited.

**Branches on the paired McNemar 95% CI [lo, hi] of W:**

    W5 REDESIGN   hi < 0                              windowing HURTS
    W1 ADVANCE    hi >= 0, lo >  0.0306               windowing materially helps; the line's
                                                      negatives were measured through a bad window
    W2 REDESIGN   hi >= 0, 0 < lo <= 0.0306           real but below the powered effect
    W3 KILL       lo <= 0 <= hi, hi <  0.0306         windowing does not matter; the negative is
                                                      ROBUST and the X-line CLOSES
    W4 PARK       lo <= 0 <= hi, hi >= 0.0306         underpowered

**No G-null.** The comparison is within-arm, so index reliability cancels and the gate that parked two
campaigns is structurally unnecessary. **G-pos still applies** — a permutation null on the windowed
arm, mean over 20 derangements at 3x answer-set-adjusted chance computed on the frozen split.

**Verdict-rule check, per the P121 doctrine:** under the null (windowing does nothing) the CI centres
on zero with half-width about 0.031, so `hi < 0.0306` fires **W3 KILL** — the null output is the
line-closing branch, which is correct behaviour and distinct from every finding branch. Partition to
be verified by enumeration in pass 1, not by eye.

## GATE_ELI5 — the Sleeping Beauty sweep, parked

**What is stuck:** the sweep needs the list of 68,770 OEIS sequences that nothing else references,
and we only have two OEIS files locally — one with the numbers in each sequence and one with their
titles. Neither says which sequences cite which, so the list cannot be rebuilt from what is on disk.

**What would unstick it:** obtain OEIS cross-reference data — the per-sequence links, or the xref and
comment fields — and derive zero-connectivity from it. The sweep itself is then cheap and exact,
because a relation either holds over 20-plus terms or it does not, so the result is a count of
confirmed discoveries rather than a statistical estimate.

## Allocation pass; CAMPAIGN W opens at pass 1/3; SB-SWEEP parked on missing connectivity data
