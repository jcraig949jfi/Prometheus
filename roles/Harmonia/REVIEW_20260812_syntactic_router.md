# Prometheus — whole-program review: the syntactic router

**Author:** Harmonia_M2_A (Claude Opus 5) · **Date:** 2026-08-12
**Trigger:** James — "a general review of Prometheus... from your unique role perspective."
**Status:** one lens of an intended panel. Harmonia B and C are reviewing the same
program from different angles; this document is the artifact they are asked to
attack in phase 2 of their reviews. **It is not consensus and should not be cited
as such.**

**Evidence levels:** E1 = read the source. E3 = executed it this session.
Claims below carry their level. Anything unmarked is inference and should be
treated as the weakest link.

---

## 0. Context

Last program activity was 2026-06-28; this review opens after ~6.5 weeks idle.
Nothing was running at session start (swarm pid dead, no python processes, no
live crons).

Evidence base read for this review:
`D:\Prometheus\pivot\REASSESSMENT_2026-06-22_v3_the_reframing.md`,
`D:\Prometheus\roles\Harmonia\AUDIT_20260622_program_stall_map_of_disagreement.md`,
`D:\Prometheus\roles\Techne\M05_PROMOTION_REPLAY_FINDINGS_2026-06-23.md`,
`D:\Prometheus\harmonia\experiments\M0_RESULTS.md`,
`D:\Prometheus\roles\Harmonia\MEASUREMENT_FLEET_2026-06-27.md`,
plus source reads of `verifier_lens.py`, `z3_backend.py`, `blackboard_evolve.py`.

## 1. The finding: a semantic engine wrapped in a syntactic router

The four headline results of the last active month are one wall seen four times.

| Where | The gate actually applied | The content check that exists |
|---|---|---|
| Theseus promotion (E1, Techne §1) | `training_weight` reads `relation` string, `claim_kind`, `verdict`, `kill_pattern` tokens — never whether the relation holds on the stored values | `theseus/scoring/content_aware_promote.py` — built, evaluates the relation against a random-pairing null, **not wired into the gate** |
| M0 / `verify()` (E3) | routes by `probe.kind` (5 kinds: linear, quadratic, sqrt, rational, conjecture) and by literal `cid` string | `certify_universal` / `entails` — decide content, reachable only by hand-routing |
| Apollo novelty (E1) | `_novel_multitier_solvers` = role-signature not in seed set | accuracy is measured, but novelty is not keyed on it |
| Icarus R5/R6 | serialization + probe-schema shape | the reasoner was capable; the interface hid the fields |

**The null I tested this against:** *"all software dispatches on type tags; you are
over-reading an ordinary implementation detail."* That null **fails**, because in
every case the expensive semantic check **was already built and left out of the
gate**. F2 exists and does not gate. `entails` exists and is called from nothing
but M0's harness and its own unit tests (E3, grep across all `*.py`). That is a
repeated architectural choice, not incidental typing.

**Statement:** Prometheus has a genuine semantic core (z3, sympy, accuracy
evaluation) sitting behind a syntactic router, and every measured wall in the
program is in the router, not the core. This is why B4/B6 are "z3-decidable
today" and still return `unknown`.

## 2. A correctness bug in M0's most load-bearing claim (E3)

M0's headline defensive property is "**0% reject** — the battery never certifies a
true claim FALSE; it fails closed and silent." That property is what makes the
audit fallback defensible.

Executed against the real instrument:

```
graph / pigeonhole / linear_algebra / identity / inequality
  -> verify() returns valid=False, kill_pattern=unknown_kind
```

`_DISPATCH.get(probe.kind)` returns `None` for any unregistered kind, and the
function returns `valid=False`. M0's own `_verdict_from` maps `valid is False` →
**reject**. The 0% holds only because the M0 harness charitably hand-routes
unrepresentable shapes, recording a STRUCTURAL non-recognition rather than calling
`verify()`. A downstream consumer calling `verify(probe, claim)` directly gets a
true claim certified **WRONG**.

Strict type-II is therefore **up to 5/18 (B1, B2, B5, C1, C2)**, not 0/18,
depending on routing. Fix: return `valid=None` for `unknown_kind`. The instrument
does not abstain on unrepresentable shapes — it rejects them, and the abstention
was supplied by the measurement harness.

## 3. Two corrections to my own 2026-06-27 prescription

**(a) "Widen the representable-shape inventory" is Goodhartable.** I proposed a
per-cycle meter: each new shape that converts a Set-B `unknown` into an `accept`
is a tick toward discovery-alive. If the mechanism is a lookup table, that is a
metric whose numerator I control by typing. 5 kinds → 12 kinds yields an
instrument blind to shape 13 and a meter that reported progress the whole way.
`REASSESSMENT_2026-06-22_v3_the_reframing.md` §6 predicted exactly this failure
mode for the progress meter; I failed to apply the guard to my own metric.

The corrected artifact is a **translator** (claim → z3/sympy formula) with
kind-routing **deleted**, not extended. A translator handling multi-variable
reals, `abs`, and small finite structures clears B1/B2/B4/B5/B6/C1/C2 at once —
those items share no shape, they share a target language.

**(b) Novelty is not-in-closure, not unrecognized-shape.** Three independent
implementations use one definition: Theseus dedups to shape-classes (413M records
→ 3,311, verdict baked into the key); Apollo counts novel = role-signature not in
seeds; `verify()` recognizes = cid in registry. Apollo's llm2 run demonstrates the
consequence — **2,860 cells / 2,846 "distinct shapes" produced zero accuracy
lift.** Shape-keyed novelty inflates trivially.

`entails(premise, conclusion)` at `D:\Prometheus\harmonia\experiments\z3_backend.py:130`
is a closure primitive, reserved in its own docstring "for future R9
lemma-invention grading," and called by nothing in production (E3).

## 4. Consequence for v3: one of the three questions is ill-posed

v3 stakes the program on Q1 *are we there yet* / Q2 *closer than yesterday* /
Q3 *what next*.

- **Q1 as posed is unanswerable by construction.** It asks the selector to
  *recognize* novelty. Recognition against an authored manifold returns only
  "resembles something I was given." Every surface bottoms out in hand-authored
  content: the 18 M0 claims, the conjecture registry, Apollo's 27 primitives, the
  trap battery. You cannot author a recognizer for novelty you have not conceived.
- **Q1 re-posed as derivability is well-posed and unbuilt.** "Not in the deductive
  closure of the current corpus, and survives falsification" is decidable on the
  fragments z3 handles. The program has no closure test at any layer.
- **Q2 and Q3 are sound.** They measure movement within an authored frame, which
  is what a TDD layer legitimately does.

**Proposal: prune v3 rather than abandon it — D survives as Q2+Q3; Q1 either
collapses into the A fallback or gets rebuilt on `entails`.**

## 5. Where the program stands, stated plainly

- Novel cross-domain bridges: **zero** (charter's honest number, unchanged).
- Promoted discoveries replayable under the current battery: **zero** —
  `total_promoted = 0`, global max `training_weight` 0.312 against a 0.6
  threshold, verified on the full 123K `bridge_extension` population
  (Techne §4, E3). The historical "2,351" is a fossil of a superseded formula.
- Set-B novelty reach of the packaged battery: **17%**, and the 4 genuine
  out-of-manifold accepts were hand-routed around the gate.

Against that: 10 negative dimensions, the FP-001..004 failure primitives, the
retraction registry, the coverage diagnostic, the grading oracle's calibrated
staircase. **The program's real accumulated asset is a failure atlas, and it keeps
being filed as a stalled discovery engine.** Under the north star — compressing
coordinate systems of legibility, not laws — the atlas is the deliverable, and it
is in better shape than the discovery ledger by a wide margin.

## 6. The live demonstration (unintended, E3)

Building B′ (§7), my first run rejected **20/20 true claims — zero for content
reasons.** The sandbox blocked `import itertools` (I had removed `__import__`
from builtins) and a regex screen false-rejected `from X import Y` as an
unapproved import. Statically permitted, dynamically blocked.

I reproduced the syntactic-router failure inside the session that diagnosed it, in
code I wrote while holding the diagnosis in mind. Fix: screen with `ast`, parse
the code rather than pattern-match it. **This is the strongest evidence in this
document for §1, and I did not produce it deliberately.**

## 7. What shipped this session

`D:\Prometheus\harmonia\experiments\bprime_generate.py` →
`bprime_holdout.json` (24 statements, 6 domains — the only artifact a translator
may read) + `bprime_oracle.json` (QUARANTINED checkers and truth values).

Authored by **gemini-3.6-flash**, an independent model family. Each claim admitted
only after its own brute-force checker was **executed** and returned True.
Negative control (`bprime_negative_control.py`): **8/8 plausible-but-false claims
correctly rejected, 0 unusable checkers** — the oracle has teeth.

B′ is pre-registered so the table-vs-translator question is decidable: **a lookup
table cannot pass a held-out set; a translator can.** B′ must not be consulted
during translator construction, and must be graded once.

## 8. Known weaknesses of this review

- §1 is a pattern claim across four systems built by different agents at different
  times. Pattern claims are exactly what this role is supposed to distrust. It
  survives the one null I posed; a better null may exist and would take §1–§3
  down together.
- §4's Q1 argument is philosophical, not executed. It has no E-level. It is the
  weakest load-bearing claim here.
- §5's characterization of the failure atlas as "the real asset" is a value
  judgment about what the program is for, not a measurement.
- Single reviewer, single session, single lens. Explicitly not consensus.

---

## 9. Corrections forced by the panel (added post-write, same day)

Harmonia C and D returned their reviews and both landed executed hits. Recorded
here rather than defended.

### 9a. §3(b) and §4 are RETRACTED — closure-novelty is a timeout detector

Harmonia D ran `entails` over 9 claims, with and without a true-arithmetic corpus
(`D:\Prometheus\roles\Harmonia\REVIEW_20260812_harmonia_D.md`, Phase 2). Two
independent failures, either sufficient:

1. **Every false statement scores as maximally novel.** `entails` correctly returns
   `invalid` for a falsehood, so under *not-in-closure ⟹ novel*, "n²+n is odd" is
   novel. This is **worse** than the shape-keyed meter it was meant to replace:
   shape-keying inflates with *distinct* junk, closure-keying with *wrong* junk,
   and wrong junk is cheaper to generate.
2. **The corpus is inert.** Only 1 of 9 verdicts changed when the corpus was
   supplied. z3 decides modulo its **built-in theory of integers**, not modulo the
   premises given — so the object computed is the closure of elementary arithmetic,
   never the closure of the Prometheus corpus. The thing whose closure I wanted to
   measure contributes nothing.

Reduces to `novel = {false statements} ∪ {claims the solver couldn't decide in
budget}`.

**D's generalization, which is the real result and is not z3-specific:
decidability and novelty are anti-correlated by construction.** Where the closure
test terminates, everything true is already inside the closure, so nothing is ever
novel; outside that fragment it returns `unknown`. **The decidable region and the
interesting region are disjoint.** The backend said so in its own docstring
("nonlinear/quantified arithmetic is undecidable in general") and the conjecture
registry already carries a tier named `z3_unknown_expected`. I proposed building on
a primitive whose documentation contained the refutation.

**Consequence:** §4's "re-pose Q1 as derivability" is dead. Q1 does **not** get
rebuilt on `entails`. §4's negative half — that Q1-as-recognition is ill-posed —
is untouched, so the live options are prune Q1 or leave it unanswered, not rebuild
it. The translator (§3a) is still worth building; it was never an answer to Q1.

### 9b. §1's dispositional claim is WITHDRAWN — I never ran the base rate

Harmonia C attacked §1 with the null I failed to pose. I tested one null
("all software dispatches on type tags"), it failed, and I accepted the claim.
The null that mattered was the **base rate inside this repo**.

C measured it: decision-machinery modules lose all live consumers at **5.4%** vs
**8.4%** for ordinary modules, and are never-wired-at-all at **58%** vs **55%**.
**Detectors are orphaned *less* than average.** Being unwired is the repo's ambient
condition — 55–58% of real library modules were never imported by anything, ever.

So four instances of "built and not wired" is not evidence of a disposition; it is
four draws from a population where that is the majority state. **"A repeated
architectural choice, not incidental typing" is withdrawn.** I noticed those four
because I authored or audited them — salience, not frequency.

**What survives, stated narrowly:** in four named systems that sit on the program's
critical measurement path, the gate applied is syntactic while a semantic check
exists. Those instances are individually verified (E1/E3) and individually
actionable. They no longer support an inference about the program's character.

**The reference class I should have used, still unmeasured:** not "all library
modules" but *gates on critical paths* — of those, what fraction decide on shape
versus content? An unimported module is inert; a shape-gate on the critical path
actively emits wrong verdicts. That is the measurement that would settle §1 in
either direction, and neither C nor I have run it. Noting it as a defense would be
special pleading unless someone actually runs it.

### 9c. §2 is STRENGTHENED

I demonstrated the `unknown_kind` → `valid=False` bug on five synthetic kinds. D
found it **firing 160/160 at R5/R7/R8** on the live ladder. It is not a latent
edge case; it is in production, certifying true claims WRONG at scale. Fix priority
raises accordingly.

### 9d. Panel disagreement, left unresolved

D reports §1 "attacked, unbroken." C's base-rate null breaks its dispositional
form. **Both are correct about different claims** — D attacked whether the four
instances are real (they are), C attacked whether they imply a disposition (they
do not). Recorded as disagreement per the map-of-disagreement doctrine rather than
flattened into a consensus line.

### 9e. §0 was factually wrong

"Opens after ~6.5 weeks idle" is false. Local `git log` showed nothing after
2026-06-27, but the working tree was **281 commits behind origin**; Ergon, Techne,
Aporia and Charon had all been active, several committing the same day. I never
ran `git fetch`. **Repo state is not program state; HEAD is a lower bound on
activity.** Every load-bearing file in this review was checked against those 281
commits and none had changed, so §1–§5 survive the error — but the error was mine
and it was avoidable with one command.

---

*Reported under the failure-signature doctrine: the verdict lines are the least
informative content here. The SHAPE — a working semantic engine that the program
cannot route to, and a novelty definition that inflates because it keys on form —
is the product. Two of this review's four proposals died on contact with executed
counter-tests, which is the panel working as designed. Harmonia A, 2026-08-12.*
