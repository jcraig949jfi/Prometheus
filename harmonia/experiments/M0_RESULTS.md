# M0 — Can the selector recognize novelty outside its calibration manifold?

**Experiment:** the keystone fork of the Prometheus v2 reassessment.
**Doctrine anchor:** `D:\prometheus\pivot\REASSESSMENT_2026-06-22_v2_enforcement.md` §M0;
`D:\prometheus\pivot\prometheus_thesis_v2.md` "Battery Limitations".
**Date:** 2026-06-27 · **Author:** Harmonia (Claude Opus 4.8, Anthropic)
**Evidence level: E3** — every number below was produced by EXECUTING the real
instrument this session, not asserted. Reproduce:

```
cd D:\prometheus
PYTHONPATH=. PYTHONIOENCODING=utf-8 python harmonia/experiments/m0_anticalibration_sets.py   # build + oracle self-check
PYTHONPATH=. PYTHONIOENCODING=utf-8 python harmonia/experiments/m0_anticalibration.py          # run M0
```

Artifacts:
- `D:\prometheus\harmonia\experiments\m0_anticalibration_sets.py` — the 18 hand-curated TRUE claims (A/B/C), each independently oracle-confirmed true.
- `D:\prometheus\harmonia\experiments\m0_anticalibration.py` — the executing harness.
- `D:\prometheus\harmonia\experiments\m0_results.json` — machine-readable results.

The instrument under test: `D:\prometheus\harmonia\experiments\verifier_lens.py`
(`verify`, `certify_universal`, `entails`, `decide_conjecture`) and its z3 backend
`D:\prometheus\harmonia\experiments\z3_backend.py`. **No LLM in the loop** —
selection side is pure sympy + z3, by doctrine.

---

## 1. The three anti-calibration sets (all claims TRUE)

| Set | Definition | n | Items |
|---|---|---|---|
| **A** | TRUE facts of the calibration core in an UNFAMILIAR SURFACE FORM (re-encodings) | 5 | A1–A5 |
| **B** | TRUE claims from ADJACENT, UNDER-REPRESENTED domains (graph theory, combinatorics, real analysis, linear algebra) | 6 | B1–B6 |
| **C** | SYNTHETIC TRUE claims, externally checkable, zero calibration leakage (sympy identities, z3 universals/entailments) | 7 | C1–C7 |

Every item carries `id, set, statement, truth (True), truth_source,
why_outside_manifold`, plus an independent `oracle_true` check. **All 18 items
were independently oracle-confirmed TRUE; 0 excluded.** We never trust our own
"truth" label — sympy/z3/arithmetic re-derives it.

---

## 2. Results (executed)

```
id  set verdict  recognition  valid  which_check
A1  A   accept   RECOGNIZED   True   verify_quadratic          (factored quadratic)
A2  A   accept   RECOGNIZED   True   verify_quadratic          (difference of squares)
A3  A   accept   RECOGNIZED   True   verify_rational           (fresh-constant identity)
A4  A   unknown  SUPERFICIAL  None   unverifiable_universal    (n(n+1) even, unregistered cid)
A5  A   accept   RECOGNIZED   True   verify_sqrt               (sqrt(x+2)=x, b=0 parametrization)
B1  B   unknown  STRUCTURAL   None   no_representable_kind     (handshake lemma / graphs)
B2  B   unknown  STRUCTURAL   None   no_representable_kind     (pigeonhole)
B3  B   accept   RECOGNIZED   True   z3_proved                 (n(n+1) even, via raw primitive)
B4  B   unknown  STRUCTURAL   None   single_int_var            (Cauchy-Schwarz, 4 reals)
B5  B   unknown  STRUCTURAL   None   no_representable_kind     (2x2 invertibility)
B6  B   unknown  STRUCTURAL   None   single_int_var            (triangle inequality, abs)
C1  C   unknown  STRUCTURAL   None   no_identity_kind          ((x+1)^3 expansion)
C2  C   unknown  STRUCTURAL   None   no_identity_kind          (x^2-1 factoring)
C3  C   accept   RECOGNIZED   True   z3_proved                 (2n even)
C4  C   accept   RECOGNIZED   True   z3_proved                 (n^2 >= 0)
C5  C   accept   RECOGNIZED   True   entails_valid             (n>5 => n>3)
C6  C   accept   RECOGNIZED   True   verify_quadratic          (irrational roots ±sqrt2)
C7  C   accept   RECOGNIZED   True   verify_rational           (fresh-constant identity)
```

### Per-set rates

| Set | n | accept | reject | unknown | accept_rate | reject_rate | unknown_rate |
|---|---|---|---|---|---|---|---|
| **A** (re-encodings) | 5 | 4 | 0 | 1 | **80%** | 0% | 20% |
| **B** (adjacent domains) | 6 | 1 | 0 | 5 | **17%** | 0% | 83% |
| **C** (synthetic checkable) | 7 | 5 | 0 | 2 | **71%** | 0% | 29% |
| **OVERALL** | 18 | 10 | 0 | 8 | **56%** | **0%** | **44%** |

Recognition-cause split: **RECOGNIZED 10 · STRUCTURAL 7 · SUPERFICIAL 1.**

---

## 3. The type-II reading

The headline, stated plainly:

- **reject_rate = 0% across all sets.** The instrument NEVER actively denied a
  true claim. This is the single most important defensive result: the battery
  does **not** produce false negatives by mis-certifying a true claim as WRONG.
  When it cannot certify, it returns honest `None` ("unknown"), not `False`.
  *The instrument fails CLOSED and SILENT, not LOUD-and-WRONG.* By the standard
  decision-theoretic definition (type-II = true claim certified false), the
  measured type-II rate is **0/18**.

- **But "no false rejection" is bought with a 44% unknown rate.** The instrument
  declines to certify nearly half of all out-of-manifold truths. That is the
  weaker, more honest face of the same coin: it is not *wrong* about novelty,
  it is *blind* to it. Re-stated in the thesis's own language: a recognizer that
  returns `None` on 44% of true claims is "structurally unable to certify a true
  claim that is unlike its calibration set" for that 44%.

### The brutal honesty the harness is built to surface

The 56% accept rate is **not** evidence the *battery* sees novelty. Decompose the
10 accepts:

- **4 are Set-A re-encodings** (A1, A2, A3, A5) — these are the calibration core's
  OWN facts (polynomial roots, rational identity, sqrt extraneous-root) wearing
  light disguises. The verifier expands/substitutes internally, so factoring or
  shifting a constant survives. This shows the kinds **generalize within their
  kind** — good, but it is *not* novelty reach.
- **2 are within-kind controls** (C6 irrational roots, C7 fresh constants) —
  deliberately included to measure kind-generalization, explicitly excluded from
  the novelty reading.
- **4 are raw z3 primitives** (B3, C3, C4, C5) — and these are the ONLY genuine
  out-of-manifold accepts. **Every one of them is z3 deciding a small
  arithmetic universal/entailment, reached through `certify_universal` /
  `entails` DIRECTLY — not through the packaged `verify()` battery.** The
  `verify()` conjecture path can only route a claim if its `cid` is already in a
  hand-written registry (`CONJECTURE_REGISTRY`). A4 proves this: `n(n+1) is even`
  is *logically identical* to the registered `n2_plus_n_even`, but because its
  `cid` is unregistered, `verify()` returns `unverifiable_universal`. **The
  packaged battery is keyed by surface identity, not meaning** — that is the lone
  SUPERFICIAL wall, and it is load-bearing: it means the battery's "novelty
  reach" is exactly the set of cids a human pre-registered.

So the honest decomposition of out-of-manifold reach (excluding the 2 within-kind
controls): **8/16 accepted = 50%, and of those 8, four are Set-A re-encodings of
core facts and four are raw-z3 decisions a human had to pose by hand.** The
*battery as a packaged selector* certifies **zero** genuinely novel-shaped truths
on its own; everything novel that passed did so through a raw SMT primitive
invoked outside the `verify()` dispatch.

### Where the wall is STRUCTURAL (7 items)

These are the heart of the M0 signal. The instrument has **no representation at
all** for:
- graphs / degree sums (B1), functions between finite sets (B2), matrices (B5)
  — no kind, no primitive: `no_representable_kind`;
- inequalities over multiple reals (B4 Cauchy-Schwarz, B6 triangle inequality)
  — z3 *can* decide them (we confirmed `unsat` on the negation directly), but the
  instrument's exposed `certify_universal` takes **one integer variable**, so the
  claim cannot be handed to it: `single_int_var`;
- plain algebraic identities `LHS == RHS for all x` (C1, C2) — the instrument
  verifies polynomial *roots* and rational identities *with a singular excluded
  point*, but has **no identity kind**: `no_identity_kind`.

In each case the harness did NOT invent a check. It recorded a structural
non-recognition and (for B4/B6) separately confirmed the underlying claim is
decidable, to prove the wall is the *instrument's surface*, not the claim's
hardness.

---

## 4. Pre-registered verdict

The pre-registration (REASSESSMENT §M0):
- **Reading A (thesis alive):** certifies *enough* out-of-manifold truths to justify continuing success-state B (discovery engine).
- **Reading B (thesis demoted):** rejects them at a rate that demotes Prometheus to an audit/recognition substrate (success-state A/C).

The harness's mechanical rule (accept ≥ 50% of out-of-manifold truths → A) prints
**Reading A** at exactly 8/16 = 50%. **I override that mechanical verdict as
misleading and report the honest reading below.** The 50% is an artifact of (a)
counting Set-A re-encodings of core facts as "out-of-manifold" and (b) counting
raw-z3-primitive accesses that bypass the packaged battery. Both inflate apparent
reach.

### Honest verdict: **B-leaning, with a critical nuance.**

1. **As a packaged discovery selector, the battery is NEARER to Reading B.** On
   the genuinely novel arm (Set B, adjacent domains) it certifies **1/6 = 17%**,
   and that single success (B3) is again a raw-z3 universal posed by hand, not the
   battery recognizing a graph/analysis/linear-algebra claim. Confronted with the
   *shapes* of mathematics outside school algebra + a tiny z3-decidable arithmetic
   fragment, the instrument is **blind, not discerning.** The thesis's own
   self-flag — "a recognizer of things-that-look-like-existing-truths" — is
   **empirically confirmed for the packaged battery.**

2. **But the failure mode is the GOOD one, and it is fixable.** The 0% reject rate
   means the instrument is not *deceiving* itself about novelty — it is *declining*
   to rule on it. Unknown is honest. And the dominant blocker is **representational
   (interface), not epistemic**: Lens 7 of the very same reassessment ("suspect the
   interface before the reasoning"). B4/B6 are z3-decidable *today* and fail only
   because `certify_universal` is wired to a single integer variable; A4 fails only
   because the conjecture registry is keyed by literal `cid` string. These are
   **surface walls** — exactly the class the reassessment predicted would
   masquerade as capability ceilings. Widen the primitive's signature (multi-var,
   reals, abs), let `verify()` synthesize a predicate instead of looking up a cid,
   and add an identity kind, and a large fraction of the current `unknown`s convert
   to `accept` *without any new discovery capability* — because the truth was
   externally checkable all along.

### What this means for the 20-year bet

The discovery thesis is **not killed, but it is demoted from where the README
advertised it.** The instrument as currently packaged is an **audit / recognition
substrate** (success-state A/C): it reliably certifies things that look like its
calibration core and honestly abstains on the rest, with **zero false denials.**
That is a genuinely valuable and trustworthy property — but it is *recognition*,
not *discovery*.

The path back toward Reading A is **not** "find universal math" or "more search";
it is **representational engineering**: every `STRUCTURAL`/`SUPERFICIAL` row above
is a missing or mis-keyed *coordinate system* (in the north-star framing,
Prometheus compresses coordinate systems of legibility — and right now it has
coordinates for ~5 shapes of claim). Until the instrument can *represent* a graph
theorem, an inequality, an identity, or an unregistered universal, it cannot
discover one, and a discovery claim outside those shapes is structurally
unreachable. **M0's verdict: stop advertising discovery (B) until the
representable-shape inventory is widened; the instrument's current, honest job is
audit (A/C). The bet survives, but it is gated on representation, not on more
crawlers, terrain, or agents** — consistent with the reassessment's Gate ("no new
crawler/agent/terrain may claim discovery progress until M0 reports").

---

## 5. Caveats / limits of this M0 (falsification-first self-attack)

- **n is small (18, hand-curated).** Rates are illustrative of *structure*
  (perfect-in-shape recognition, blindness-out-of-shape), not precise
  percentages. The *shape* — A high, B low, C bimodal (z3-reachable high,
  identity/graph nil) — is the robust finding; the exact 56%/17% are not.
- **"Out-of-manifold" is a judgment call.** I excluded C6/C7 as within-kind
  controls and flagged the Set-A items as re-encodings of the core. A harsher
  reading that counts ONLY Set B as truly novel gives **17% reach** and an
  unambiguous Reading B; a looser reading that counts all non-A items gives a
  rosier picture. I report all three so the reader can re-arbitrate.
- **Single instrument, single session, single family.** Per the reassessment's
  own §0/C8, this is one realization. The z3 backend's reach is a property of how
  the primitive is *wired*, which a different engineer would wire differently —
  itself evidence the wall is interface, not capability.
- **The 0% reject rate could be over-comfortable.** It partly reflects that the
  instrument *abstains* rather than commits on hard claims. A battery that
  certified more would also risk certifying wrong; the current design buys safety
  with blindness. Whether that trade is right depends on whether downstream
  consumers can metabolize `unknown` (M1 territory).

---

*M0 reporting follows the failure-signature doctrine: the verdict line ("56%
accept") is the least informative number here. The SHAPE — recognizes its own core
in disguise, abstains honestly on everything else, and the everything-else is a
representational wall the reassessment already named (Lens 7) — is the product.*
