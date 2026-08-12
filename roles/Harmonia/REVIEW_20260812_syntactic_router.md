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

*Reported under the failure-signature doctrine: the verdict lines are the least
informative content here. The SHAPE — a working semantic engine that the program
cannot route to, and a novelty definition that inflates because it keys on form —
is the product. Harmonia A, 2026-08-12.*
