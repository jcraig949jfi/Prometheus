# EXTERNAL REVIEW RULING — Gen-1 Precondition A

**Received:** 2026-09-02, external reviewer, on `REVIEW_PACKET_GEN1_PRECONDITION_A_2026-09-01.txt`
**Recorded by:** Ergon (second instance, M2)
**Ruling:** PRECONDITION A — **PASS**. Gen-1 authorized to proceed, with one interpretation
correction and one preregistration correction.

This file records the ruling, what this seat did in response, and what it verified rather
than assumed. Two of the reviewer's requirements turned out to be **already discharged
upstream**; that is reported as found, not claimed as work.

---

## 1. ACCEPTED — Finding 1 stands, my inference from it does not

The reviewer accepts the measured 16-task window and **rejects Q8/Q11**, which drifted into:

> "the consumer structurally cannot hold more than ~16 tasks"

That does not follow, and the correction is right. The cap binds on **artifact count (64)**,
not on age. The ~16-task horizon is an arithmetic consequence of the *baseline policy*
admitting ~4.03 artifacts per task and evicting blindly by recency. A selective policy can
preserve an artifact from task 3 to task 58 while killing newer low-value ones. That is not
a workaround — it is the experiment.

**I did not merely concede this; I measured it.** The baseline memory-age survival curve
(§4 below) shows a **max survivor age of 28 tasks** under blind recency on the 42-task
corpus. The substrate already permits nearly double the mean horizon with no selection
pressure at all. There is no 16-task structural ceiling, and my own instrument's data
falsifies my own claim.

**The error was an internal contradiction in my own packet, which is the instructive part.**
Section 7 reframed the contrast as RECENCY-forgetting vs SELECTIVE-forgetting — correct, and
the reviewer adopts it as canonical. Q8/Q11 then treated the window as a property of the
*substrate*. Those two cannot both be true: if the window were substrate-imposed, selective
forgetting would have nothing to select over. I wrote both, four sections apart, and did not
notice.

**ADOPTED AS CANONICAL:**
- The control has a **measured ~16-task effective horizon**. That is a property of I0.
- Whether the treatment **extends useful persistence beyond that horizon** is one of the
  most interesting available outcomes, not a design flaw.
- **Do NOT raise the cap** to make the library span more history. Raising it reduces
  eviction pressure and weakens the phenomenon being measured. Nothing here has changed
  the cap, and nothing should.

Q8 and Q11 are **WITHDRAWN** from the packet.

## 2. VERIFIED ALREADY DISCHARGED — the estimand correction

The reviewer requires the live experiment not be described as holding the candidate stream
constant, and that it be registered as the **total causal effect** including downstream
search divergence.

**This is already frozen, and correctly.** `ergon/gen1b/PREREG_GEN1_2026-09-01.txt` §1:

```
The causal effect of a RETENTION (eviction) POLICY on future capability,
INCLUDING the downstream search trajectory that the policy induces.

NOT the effect of library composition holding candidate generation fixed.
Exact stream freezing is architecturally impossible under the frozen D-5
consumer; this is an accepted limitation, established in Gen-1 and ruled
on in Gen-1A.
```

No amendment is required, and none should be made — amending a frozen preregistration to
insert text it already contains would be a worse outcome than leaving it alone. The
mechanistic secondary the reviewer asks for also exists: Gen-1A's replay of one admission
stream through five eviction rules (terminal Jaccard 0.000 for EFFUSE and LRU_DRAW, 0.461
RANDOM, 0.113 RETIRE_N).

The reviewer's framing is nonetheless worth adopting in the *analysis write-up*, because it
pre-answers the predictable objection — "maybe the library merely changed what search
happened to discover" — with: **yes, and that mediated change is inside the registered
estimand.**

## 3. NEW FINDING — the frozen MDE and the frozen decision rule use different alphas

Raised by the reviewer's requirement to fix the multiplicity treatment. Checking it against
the frozen prereg surfaced an inconsistency neither line had recorded.

`PREREG_GEN1_2026-09-01.txt` §5 freezes both:

```
Preregistered MDE    1.9 pp at n=30 (Gen-1A power analysis, sigma 0.0412)
Multiplicity         5 contrasts; Holm-Bonferroni across the five.
                     A contrast is called ONLY if it survives Holm.
Test                 two-sided paired sign-flip permutation
```

Re-simulating the frozen test directly (`mde_under_multiplicity.py`, 3000 experiments x
2000 sign-flips per effect size, no normal approximation):

| condition | MDE at 80% power |
|---|---|
| one-sided, alpha = 0.05 | **1.95 pp** — reproduces the prereg's 1.9 |
| two-sided, alpha = 0.05 | 2.18 pp |
| two-sided, Holm best-of-5 (alpha = 0.01) | **2.72 pp** |

So the preregistered MDE was derived **one-sided at uncorrected alpha**, while the frozen
decision rule is **two-sided under Holm across five**. Under the rule actually frozen, the
smallest *callable* effect at n=30 is **~2.7 pp — 1.4x the number the preregistration
commits to.** An effect of 1.9 pp is detectable in the sense the power analysis meant and
**not callable** under the rule that will decide it.

This is `feedback_gate_must_exceed_measurement_error` — the gate sitting below the
measurement error it must clear. It is free to know now and expensive to discover after
results.

**Three admissible resolutions. Choosing is the primary line's call, not mine.**

1. **Record 2.7 pp as the real callable MDE** and leave everything frozen. Cheapest;
   honest; the true effect may well exceed it.
2. **Raise n to 60**, which restores 80% power at 1.9 pp under Holm (measured: power 0.43
   at n=30, 0.82 at n=60). At 27 s per lineage this is ~1.8 h for 60 lineages x 4 arms.
3. **Reduce to a single primary contrast** — the reviewer's H1 preference. This resolves
   the inconsistency at **zero compute cost**: alpha stays 0.05, two-sided MDE is 2.18 pp,
   and the remaining arms become mechanism/ablation arms.

Worth noting that the reviewer's stylistic preference for one primary contrast and this
quantified inconsistency have **the same fix**. Option 3 turns a presentational
recommendation into a power argument.

I am a conflicted party on option 2 — it makes the run bigger and more interesting — and
say so.

## 4. BUILT — memory-age survival curve, with the baseline frozen before results

The reviewer mandated this diagnostic. `memory_age_survival.py` is committed **before any
treatment arm has run**, so the baseline reference is fixed ahead of the comparison.
It reports exactly what was asked: P(resident older than 16 / 32 tasks), max survivor age,
median post-saturation age, and **draw mass attributable to old residents** — the line that
separates "old artifacts survive" from "old artifacts are used."

**BASELINE REFERENCE CURVE — I0_D5_BASELINE_MRU, 5 lineages, 42-task corpus:**

```
lin  tasks  sat  maxAge  medAge  P(>16)  P(>32)  draws>16  draws>32
  0     42   16      22       7   0.004   0.000    0.0019    0.0000
  1     42   14      17       7   0.001   0.000    0.0000    0.0000
  2     42   15      28       8   0.011   0.000    0.0086    0.0000
  3     42   15      21       8   0.003   0.000    0.0022    0.0000
  4     42   14      21       7   0.003   0.000    0.0016    0.0000

mean P(resident older than 16 tasks) ... 0.0042
mean P(resident older than 32 tasks) ... 0.0000
max survivor age, any lineage ......... 28
mean draw mass to residents >16 tasks .. 0.0029
```

**Reading.** Under blind recency the median resident is 7-8 tasks old, only 0.4% of
residencies exceed 16 tasks, **none ever exceeds 32**, and old residents receive 0.3% of
all library draws. That is a demanding floor to beat and an easy one to beat *visibly*:
any policy that genuinely extends useful memory should move `P(>16)`, `P(>32)` and the
draw mass by large multiples, not by percentage points.

**The three-world test the reviewer specified is now executable:**

| observed | mechanism verdict |
|---|---|
| CFR up, age distribution unmoved | long-term retention is NOT the mechanism |
| old survivors accumulate, draw mass flat | persistence alone is NOT the mechanism |
| old survivors accumulate AND draw mass rises with CFR | selective memory is doing work |

**Scope note, stated because the numbers differ from my packet's.** My 16.6-task depth was
measured on the **58-task** full dev battery; this curve is on the **42-task** non-control
corpus the preregistration actually uses. The two are not directly comparable, and the
42-task figures are the relevant baseline for Gen-1.

## 5. AGREED WITHOUT QUALIFICATION

- **n=30.** Treatment is assigned at the lineage; treating 290 task rows as independent
  would be pseudoreplication. Preserved.
- **D-5 split verdict.** Scientific result survives; freeze protocol fails modern standards.
  Do not conflate. This matches this seat's own MEDIUM grading and its exculpatory reading.
- **Systemic fix:** normalized-content hashes plus an executable freeze verifier in every
  future campaign. `verify_d5_freeze.py` is the working reference implementation. A freeze
  manifest nobody reads is documentation, not a gate.

## 6. HANDOFF

Items 3 and 4 are for the **primary Gen-1A/1B line**, which owns the preregistration and
the run. This instance holds neither and is not amending either. Filed, not enacted:

1. The MDE/Holm inconsistency (§3) with three resolutions — **decide before the run**.
2. `memory_age_survival.py` and the frozen baseline curve (§4), ready to run against each
   treatment arm's corpus as `--corpus <dir> --policy <name>`.

*Declared conflict: §1 concedes an error of mine, which is the cheap direction. §3 raises a
problem in the other line's frozen document, which is the direction where I should be
distrusted most — so it is stated as a measurement anyone can rerun in about four minutes,
with the script committed beside it, and the resolution left to them.*

— Ergon (second instance), 2026-09-02, M2
