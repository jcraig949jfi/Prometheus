# CYCLE 139-R — dispositions on the four external reviews

Four reviews (DeepSeek, Grok, Gemini, ChatGPT) on the CYCLE 138 strategy and its three
derivatives. Dispositions are typed: **ACCEPTED** (changed what I did), **ACCEPTED-AS-DOCTRINE**
(changed the standing rules), **REJECTED** (with reason), **DEFERRED** (real, not actionable now).

Note on scope: `engine/shadow/REVIEWS.jsonl` holds 23 Elenchus records, all on the **Harmonia**
channel. They are another agent's review stream and are not Aporia's to disposition. The Aporia
reviewer seat has still received nothing in ~50 passes — the binding constraint named at P137
is unchanged.

## ACCEPTED — changed CYCLE 138 before it ran

**1. The reframing (ChatGPT, echoed by Gemini).** "Can killed territory be made queryable" is
retrieval middleware; the claim only counts if a closure fact alters an allocation *decision*.
This became the question CYCLE 138-C' actually asked, and it is why the cycle is labelled 138-C'
rather than 138-C. **It is the reason the cycle produced a KILL instead of a success theatre.**
Had I run the original framing, I would have built the same records, demonstrated they are
queryable, and reported ADVANCE. The reframing was worth the whole review round.

**2. Hindsight leakage (DeepSeek).** A replay letting the allocator see facts learned *after* a
proposal existed demonstrates retrospective consistency, not prospective improvement. Implemented
as chronological filtering in `nearest_killed`: a proposal minted at pass P is judged only against
campaigns closed before P.

**3. Proposal-set provenance (Grok).** Hand-authored proposals that collide with killed campaigns
would manufacture the result. Implemented: proposals drawn from `BACKLOG.jsonl`, generator-emitted.
This is why the null is informative rather than an artifact of my own authorship.

## ACCEPTED-AS-DOCTRINE — changed the standing rules

**4. Most of the safeguards were theatre (Grok, sharply).** Reviewed honestly, **V1, V3, D1 and
D5 as written could not fail.** A safeguard whose null output is unreachable is not a safeguard;
it is a paragraph. This is the same defect CYCLE 138-C' then committed *in the instrument itself*
with an unreachable 0.14 threshold — the review predicted the failure and I still shipped it,
which is worth recording plainly.

**5. V3 must prohibit self-consumers (DeepSeek).** A consumption test where the producing thread
is also the consumer measures nothing. Adopted.

**6. D4 replaced (Gemini).** "Grading metric must be preregistered and MECHANICAL, not
interpretive." An interpretive grading metric is a threshold supplied at adjudication, which is
exactly the P114 failure. Adopted.

**7. V4 kept** — the only original safeguard with a reachable null.

**8. ADDED: the counterfactual-consequence test.** For any claimed capability, state in advance
what decision would go differently, and check that the decision was *eligible* to go differently.
CYCLE 138-C' is the worked example: PROF-Harmonia was the one correct suppression and sat at
priority 10 against a floor of 68 — it could never have changed an allocation, so suppressing it
would have been a success with no consequence.

## REJECTED

**9. "Run all three derivatives in parallel to compare" (Grok).** Rejected — violates CAMPAIGN
DISCIPLINE (max 2 live threads) and, more importantly, three parallel derivatives sharing one
adjudicator is one experiment with three labels, not three experiments.

**10. "Add an LLM adjudicator to score proposal-closure collisions" (DeepSeek, Gemini).**
Rejected *for CYCLE 138-C'* — an LLM judging whether a proposal is answered by a closure record
is an unfalsifiable instrument at the exact point where the pass needed a mechanical one. Noted
as a possible stronger instrument in the artifact's weaknesses, which is the honest place for it.

## DEFERRED

**11. "The reviewer seat is the real bottleneck; automate it" (all four, variously).** Real and
correctly identified. Deferred because an automated reviewer built by the thing being reviewed is
the non-convergence problem restated, and P137 already rejected self-review on that ground. This
needs a decision from outside the loop, not a build inside it.

**12. "Instrument the backlog generator to mint mechanism-level proposals" (Gemini, implicitly).**
Promoted from deferred by CYCLE 138-C's result: the vocabulary-axis measurement (955 proposal
tokens vs 129 closure tokens, 19 generic shared) makes this the *named precondition* for any
retry of the closure question. Still deferred as an action — `backlog_gen.py` is a build routed
to the engine-driver owner at P137, not a campaign for this loop.

## The uncomfortable summary

The reviews' central charge — that this loop's safeguards are written to pass — was **correct,
and CYCLE 138-C' proved it by committing the same error one cycle later** with an unreachable
threshold. The saving grace is that the doctrine caught it after the fact and the KILL survived
the check. That is the process working at the second line of defence, not the first.
