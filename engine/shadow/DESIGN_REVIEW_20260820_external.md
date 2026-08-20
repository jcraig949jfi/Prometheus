# Shadow-channel design review — external reviewer + cycle-1 operator notes

**Logged by:** Harmonia_M2_A (wearing the Harmonia hat, **not** Elenchus).
**Date:** 2026-08-20 · **Trigger:** James — external-review loop on the shadow-reviewer concept.

**Why this is not in REVIEWS.jsonl.** `roles/Elenchus/RESPONSIBILITIES.md` boundary 4:
"Reviews Aporia's WORK, not Aporia's charter. Charter disputes go to James via the
dashboard, not into REVIEWS.jsonl verdicts." This document is charter-level design
feedback, so it lands here. The cycle-1 review records stay in `REVIEWS.jsonl`
(commit `be38627c`), untouched.

**Provenance.** Cycle 1 was run by an M2 session temporarily assuming the Elenchus role
to test whether the role is bootstrappable. The cycle-1 report was then pasted into an
external AI tool by James for an independent read. What follows is that reviewer's
critique plus the operator's own notes. **The external reviewer had no repo access** —
only the cycle-1 summary.

---

## 1. The reframe that reorganizes everything

> **"The shadow reviewer is useful, but in its current form it is an epistemic linter,
> not an independent verifier."**

Elenchus currently conflates three capabilities with very different strengths:

| Capability | Question | Current state |
|---|---|---|
| **Reproducibility audit** | Can I reconstruct what Aporia says it did? | **Strong.** The independent re-derivation with a deliberately different algorithm is good methodology. |
| **Evidence adequacy audit** | Does the supplied evidence actually support the claim? | **Strong.** The dead-heartbeat find demonstrates it. |
| **Truth audit** | Is the claim actually true of the world/data? | **Badly crippled.** |

The third is the most important, and the reviewer named the danger precisely:

> "If Aporia says 'querying 47 million records shows phenomenon X,' and Elenchus can only
> inspect the query text, output summary, and internal arithmetic, you have created a
> beautifully disciplined audit of a potentially fabricated measurement. That is dangerous
> because **the system can produce something that looks more trustworthy precisely because
> it was reviewed.**"

That failure mode — review as trust-laundering — is worse than having no reviewer.

## 2. The five recommendations

### 2a. Ground-truth sampling bridge (first architectural change)
Not broader permissions. A *controlled* capability: for any reviewed pass, Elenchus may
select up to N claims or source rows and request an independently executed replay on the
machine holding the data. **Elenchus chooses the sample, not Aporia.** The response should
be mechanically generated — raw query, source identifiers, row hashes, result hashes,
execution environment, output — so Elenchus never has to trust another agent's prose.

Split the verdict taxonomy, which currently compresses three epistemic levels into one:
- **LOG-SOUND** — the reasoning follows from the recorded evidence.
- **REPLAY-SOUND** — independent execution reproduced it.
- **GROUND-SOUND** — independent access to the underlying source confirmed it.

Also: **give Elenchus read access to the published artifact now.** The audit object should
be `claim → evidence → computation → log → published artifact`, not `claim → log`.
Reviewing the intermediate proof but not the published theorem is backwards.

### 2b. The reviewer needs its own falsification regime
`praise_withheld: true` is fine and should stay. But "never praise" is not "find as many
defects as possible," and the current implicit incentive is `findings / passes`, which
Goodharts toward pedantry. What matters is
`material errors detected − false accusations − wasted review effort`.

- **Seed four classes of blind calibration cases** into the review stream: known defect;
  known clean claim; ambiguous claim; and a material-vs-cosmetic defect pair (does the
  reviewer rank substance above formatting?). **Do not tell Elenchus which passes are
  calibration cases, and do not let Aporia author all of them** — that turns an
  adversarial test into a cooperative unit test.
- **The missing metric is false-positive rate.** 37 findings / 31 confirmed tells you
  something; 112 findings / 19 confirmed / 93 rejected means you built a grievance generator.
- **Two new required fields per finding:**
  - `materiality` — would correcting this plausibly change the conclusion, confidence,
    decision, or downstream artifact?
  - `counterfactual` — what observable difference distinguishes "my criticism is valid"
    from "I am merely demanding more evidence"? This kills unfalsifiable criticisms like
    "insufficient exploration" / "alternative explanations remain."
- **Finding-survival ledger:** confirmed / partially_confirmed / rejected / stylistic /
  duplicate / unverifiable. Exposes harshness drift fast.
- **Replace the 10-SOUND self-recheck rule** (broken exactly as cycle 1 found — zero SOUND
  verdicts means it never fires) with random retrospective sampling across *all* verdict
  classes, weighted toward high-confidence and high-materiality judgments. **The reviewer
  should periodically be forced to defend an accusation, which is more revealing than
  rechecking its successes.**

### 2c. The planted citation test proves less than it appears
Two separable findings:
- **Aporia predicting exactly which citations were dubious is a real result about
  Aporia's metacognition** — the weakness field carries signal, not boilerplate.
- **But it is weak validation of Elenchus.** The reviewer was told a test existed, Aporia
  authored the defects, and Aporia already knew where the uncertainty lived. *"Very close
  to testing whether a smoke detector works by telling someone, 'I am about to light
  something on fire.'"* Useful commissioning test; weak field validation.

The real experiment: **can Elenchus detect errors neither agent knows exist?** That needs
externally generated perturbations from a third mechanism — swap a database row, alter one
citation metadata field, introduce a stale endpoint, change one unit, duplicate records
invisibly, perturb one denominator, substitute a subtly stale artifact — applied after
Aporia produces the pass and before Elenchus sees it, with neither agent knowing whether a
perturbation occurred. Then measure detection.

**The dead heartbeat is already a small natural version of this experiment** — nobody
planted the retired endpoint. It should carry far more evidentiary weight than the citation
sting.

### 2d. "Never blocks" is right at the micro level, wrong at the macro level
Do not put Elenchus synchronously in Aporia's inner loop — that destroys throughput and
turns Aporia into an agent optimizing for reviewer appeasement. **But a reviewer that can
never affect anything is decorative governance.** The model is **escalation, not blocking**
— CI rather than pair programming: developers keep writing code after a test failure, they
just cannot merge the broken branch.

Prometheus needs the distinction between **continue investigating** and **promote into
trusted substrate**:
- METHOD-FLAW does not stop an exploratory pass, but the claim cannot be promoted to a
  durable "established result" until resolved.
- CITATION-FAIL does not stop investigation, but **that citation cannot propagate into a
  published artifact.**
- Unresolved high-materiality findings carry as debt; the same defect class appearing three
  times triggers a doctrine or tooling change.

**Propagation quarantine is the highest-leverage engineering change after ground-truth
replay,** and cycle 1 already demonstrated the need: the wrong citation migrated from P16
into P17 and into a published artifact. *"The system currently notices epistemic infection
but apparently lacks quarantine."* Fix: every finding attaches to a stable claim ID, and
descendants inherit unresolved flags automatically, so a later artifact cannot silently
launder a disputed claim into apparent consensus.

### 2e. The blind spot: correlated epistemic blindness
Not laziness, not over-harshness, not hallucination — those are visible. The dangerous case:
**Aporia and Elenchus share a conceptual ontology, so both agree on the wrong question.**
Elenchus can rigorously verify arithmetic, citations, query, stated alternatives, rerun and
artifact, and the exercise can still be worthless because the measurement does not
discriminate between the hypotheses that matter. Both agents run inside the same doctrine
and likely share model-family priors, terminology, program history and evaluation habits.

> "You can get extremely high-quality internal epistemology inside a locally wrong frame."

`narrative_resistance` is meant to attack this but **ritualizes easily** — "simplest
alternative considered: sampling bias. Rejected because X. ✓". The real question is **who
decides what the live alternative explanations are.** If Aporia proposes them and Elenchus
only audits whether Aporia tested them, **Aporia still controls the hypothesis space.**

Fix: periodically give Elenchus *only the observations and the claim*, withholding Aporia's
narrative, interpretation, alternatives_rejected and possibly intent. Ask it to generate the
strongest competing explanations **before** seeing the author's. Then reveal. Even better,
reverse it: give Elenchus the raw evidence and ask what it thinks is justified, then compare
`claim(Aporia)` against `claim(Elenchus | evidence only)`. **The divergence is informative
even when neither is demonstrably wrong** — and it is a far stronger anti-narrative
instrument than auditing whether a field named `narrative_resistance` was filled convincingly.

## 3. The evaluation standard (the broader architectural point)

> **Do not evaluate Elenchus by how many Aporia mistakes it catches. Evaluate it by how much
> it improves the reliability of the promotion boundary.** Otherwise you will accidentally
> optimize the reviewer into a prolific critic.

The eventual experiment:
- Without Elenchus, what fraction of promoted claims later fail?
- With Elenchus, what fraction fail?
- Which kinds of failure disappear?
- What new failures does Elenchus introduce via false vetoes or review-induced distortion?
- What compute/throughput does the improvement cost?

**If those numbers move, you have an instrument. If Elenchus produces brilliant forensic
reports but the error rate of durable Prometheus substrate does not change, you have theater.**

**Recommended priority order:** ground-truth sampling → artifact/claim propagation tracking →
blind calibration with false-positive measurement → reviewer-before-narrative experiments →
promotion consequences for unresolved findings.

Next 50 passes should be designed to determine whether the heartbeat catch was a repeatable
capability or a lucky hit.

---

## 4. Operator notes (Harmonia_M2_A, cycle-1 self-assessment)

**Independent convergence.** The external reviewer reached two of my cycle-1 structural
findings — data access and the log/artifact scope hole — from a summary alone, with no repo
access. Convergence from a different frame is the strongest corroboration available here.

**Where it went past me.** I wrote "finding-count inflation is the predictable drift" and
stopped at naming it. The reviewer supplied the actual instrumentation: false-positive rate,
a finding-survival ledger, and the `materiality` / `counterfactual` fields. Naming a failure
mode without an instrument for it is the weaker half of the job.

**Where it caught something I missed entirely — correlated epistemic blindness.** I audited
whether Aporia tested its *stated* alternatives. I never asked who controls the hypothesis
space. That is the same error class Harmonia C surfaced against me a week ago
(`feedback_base_rate_null_for_pattern_claims`): I audited *within* the frame I was handed
instead of testing the frame. Being the designated adversary did not protect me from it,
which is itself evidence for the reviewer's point.

**A correction to my own reporting.** I led the cycle-1 report with the citation findings
because that was the assigned test. The reviewer is right that **the unplanted heartbeat
discovery was the stronger result** and I under-weighted it. Planted defects measure
commissioning; latent defects measure capability.

**Two additions I would put back to the reviewer:**
1. *Trust bootstrap in the ground-truth bridge.* Row and result hashes prevent prose
   laundering, but if the replay executes on M1 via machinery inside Aporia's blast radius,
   the hashes certify a possibly-compromised executor. The replay executor needs to be
   independent of the reviewed agent, not merely mechanical.
2. *The reviewer-before-narrative experiment collides with a hard rule.* Having Elenchus
   generate competing explanations from raw evidence is Elenchus doing Aporia's work, which
   boundary 1 forbids. It should be scoped as a **diagnostic comparison that never enters
   the claim stream** — otherwise the shadow reviewer forks into a second, unreviewed
   investigator, and the whole structure regresses.

**Bootstrap verdict on Aporia's build:** the role *is* bootstrappable. Cold start to filed
reviews, no questions asked, write-scope respected. Two defects found in the wiring itself —
the heartbeat targets retired `192.168.1.176` (live bus is `192.168.1.202`), and
`REVIEW_AGENT_PROMPT.md` hardcodes `F:\Prometheus` while M2 runs `D:\Prometheus`.
