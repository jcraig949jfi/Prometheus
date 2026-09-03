# Verdict-Entropy Theory

**What must remain unknowable before purchase for the 1/K guarantee to retain
its intended meaning?**

Mission section 5 instructed me to treat "H(verdict) >= 0.5 bits" as a
hypothesis to qualify, not a constitutional constant, and to replace it if
entropy alone proves insufficient. It did prove insufficient. The replacement
is not a bigger entropy threshold. **The whole entropy framing is the wrong
shape, and the harness data shows why.**

---

## 1. The proposed standard, and its empirical death

The archaeology mission proposed a two-part gate:

```
p0 <= 1/K                 (empirical level)
H(verdict) >= 0.5 bits    (verdict entropy)
```

The mandatory negative control is the **offline-oracle attack**: a
specification whose inputs are beacon-fresh but whose verdict the attacker
computes in advance. On stackvm-v1 the cheapest instance is a *saturating
program* — `JMP 0`, two bytes, a legal program by spec (every byte sequence
is) that burns the entire step budget on every input, so its `steps`
observable is pinned at the maximum on every context the beacon can produce.

Measured over 300 decoy beacons (`VERDICT_ENTROPY_RESULTS.txt`):

| quantity | attack spec |
|---|---|
| Shannon entropy H | **0.869 bits** |
| min-entropy H_inf | 0.494 bits |
| attacker best-prediction accuracy | **0.710** |
| empirical level p0 | **0.160** (target 1/K = 0.001) |

**The 0.5-bit Shannon gate PASSES the attack.** H = 0.869 is comfortably above
0.5, while the attacker can predict the verdict 71% of the time. The gate that
was supposed to be the defence waves the attack through.

The reason is standard but worth stating precisely: **Shannon entropy is the
wrong functional for a guessing game.** It is an average code length, not a
bound on prediction. A distribution with p = 0.71 on its modal class has
H = 0.869 bits and min-entropy H_inf = -log2(0.71) = 0.494 bits. The attacker's
optimal strategy is to guess the mode, and the quantity that governs that is
min-entropy, not Shannon entropy. Any threshold on H can be satisfied by a
distribution whose mode is highly predictable.

---

## 2. But min-entropy is also the wrong gate

The obvious repair — raise to `H_inf >= 1.0 bits` — does reject the attack
(0.494 < 1.0). It also **rejects every honest test.** From the same run:

| spec | p1 (admit rate) | attacker accuracy | Shannon H |
|---|---|---|---|
| honest: random 40B, steps | 0.000 | **1.000** | 0.000 |
| honest: random 40B, n_opcodes | 0.033 | 0.967 | 0.211 |
| honest: random 64B vs uniform | 0.000 | **1.000** | 0.000 |

An honest, well-calibrated test **is supposed to be predictable.** Under a true
null at threshold K, the admission probability is 1/K by design — for K = 1000
that is 0.001, so the verdict is "REFUSE" with probability 0.999 and the
attacker predicts it perfectly. *Predictability of the verdict is the signature
of a correctly calibrated test, not of a broken one.*

So a gate of the form "the verdict must be uncertain" is self-defeating: it
refuses exactly the tests whose level is right, and it is satisfiable by an
attacker who manufactures entropy. Both directions fail.

---

## 3. What actually matters

The confusion is between two different unknowables:

* **Is the verdict unknown?** — irrelevant. An honest test's verdict is
  overwhelmingly knowable ("it will refuse"), and that is fine. Knowing you
  will lose is not an exploit.
* **Can the registrant choose a (candidate, specification) pair whose
  admission probability UNDER A TRUE NULL exceeds 1/K?** — this is the entire
  question. It is the only thing the conserved-risk guarantee depends on.

Formally, the ledger's bound is

```
E[# false admissions] = SUM_c P(ADMIT_c | H0_c) <= SUM_c 1/K_c <= ALPHA_LIFE
```

and it needs exactly one property per candidate: `P(ADMIT | H0) <= 1/K`.
Nothing in that expression mentions the entropy, predictability, or surprise
of the verdict. An attacker who predicts a refusal costs the program nothing.
An attacker who obtains admission at rate 0.16 while paying 0.001 has broken
the arithmetic — and that is measurable directly.

**THE CORRECT OPERATIONAL CONDITION.** Replace the entropy gate with:

> **The harness — never the registrant — measures the empirical level
> `p0 = P(ADMIT | subject drawn from the canonical reference law)` over
> independent decoy beacons, and refuses the specification unless
> `p0 <= 1/K` with a one-sided upper confidence bound at a stated
> confidence.**

`p0` is the admission rate when the *candidate is replaced by a reference
draw*: a subject that is null-true by construction. It is precisely
`P(ADMIT | H0)`. Measuring it requires no assumption about the attacker's
knowledge, because it does not model the attacker at all — it measures the
test.

On the attack spec, `p0 = 0.160` against a target of `0.001`: **refused by a
factor of 160.** The gate that works is the one that was already there.

---

## 4. Two auxiliary conditions the level check does not cover

The level check is necessary and nearly sufficient. Two gaps remain, both
cheap to close:

**(a) BEACON SENSITIVITY (anti-constant-fibre).** A specification whose
evidence does not actually depend on the beacon has a level that is either 0
or 1, and a `p0 = 0` passes the level check while sealing nothing. Require
that at least two decoy beacons produce **different evidence hashes**. This
catches predictions entailed by substrate invariants that are statically
readable from the bytecode — e.g. a program with no input-dependent branch,
whose `steps` are constant in the inputs, making the beacon fibre a set on
which the verdict is constant.

**(b) MEASUREMENT ADEQUACY.** `p0` must be measured with enough decoys to
resolve `1/K`. This is a hard, honest limit: with N decoys and zero observed
admissions, the one-sided 95% upper bound on `p0` is about `3/N`. To certify
`p0 <= 10^-3` therefore needs `N >~ 3000` decoys; to certify it comfortably,
`N ~ 10^4`. **My sweep used N = 200, which can only bound `p0 <= 0.015.`**
That is enough to rule out gross miscalibration (and it did: it exposed a
160x error in my own default configuration) but it is *not* a certification
of the 1/K level, and this document does not claim one.

---

## 5. What the level check exposed about my own configuration

Running the level check over configurations produced the most useful single
table in this mission (`VERDICT_ENTROPY_RESULTS.txt`, calibration sweep):

| n_refs | n_blocks | K | p0 (attack subject) | p0 (honest subject) | level OK |
|---|---|---|---|---|---|
| 3 | 24 | 1000 | 0.160 | 0.000 | no |
| 3 | 12 | 1000 | 0.070 | 0.000 | no |
| 3 | 8 | 1000 | 0.010 | 0.000 | no |
| 7 | 8 | 1000 | 0.020 | 0.000 | no |
| 7 | 6 | 1000 | 0.010 | 0.000 | no |
| 15 | 5 | 1000 | 0.000 | 0.000 | yes* |
| 15 | 4 | 1000 | 0.000 | 0.000 | yes* |

\* "yes" here means "no admissions in 200 decoys", i.e. `p0 <= 0.015` at 95%
— see the measurement-adequacy caveat above.

The mechanism is transparent. Under a true null the subject ranks top with
probability `1/(1+n_refs)`. With `n_refs = 3` that is 1/4, and a run of about
five consecutive tops inside 24 blocks reaches K — an event with probability
far above 1/1000. Raising the reference count to 15 drops the per-block
success probability to 1/16 and shortening the block budget removes the
lucky-run opportunities.

**The configuration I would have shipped by default was miscalibrated by two
orders of magnitude.** No amount of entropy measurement would have revealed
that; the level check revealed it immediately.

---

## 6. Answer to the mission's question

> *What exactly must remain unknowable before purchase for the 1/K guarantee
> to retain its intended meaning?*

**Nothing about the verdict needs to be unknowable.**

What must hold is a property of the *test*, not of the *attacker's knowledge*:

1. **LEVEL.** `P(ADMIT | subject is null-true under the canonical reference
   law) <= 1/K`, measured by the harness over enough independent decoy beacons
   to resolve `1/K`, with the candidate replaced by a reference draw.
2. **BEACON DEPENDENCE.** The evidence must actually be a function of the
   beacon — verified by distinct evidence hashes across decoys — so that the
   admission event is not constant on the beacon fibre.
3. **NULL PROVENANCE.** Every element of the null path is
   `SPEC_DERIVED | PROTOCOL_CONSTANT | EXTERNAL_RANDOMNESS`, never
   `CORPUS_DERIVED` (see `NULL_PATH_TYPE_SYSTEM.md`). Conditions 1 and 2 are
   about the test; this one is about who chose it. Without it, `p0` is
   measured under a null the registrant fitted, and a measured level is only
   as meaningful as the law it was measured against.

Conditions 1-3 are jointly what the guarantee needs. Entropy appears nowhere
in the final standard.

---

## 7. Residual risks, stated plainly

* **R1 Measurement cost.** Certifying `p0 <= 10^-3` needs ~10^4 decoy
  evaluations per specification, each of which executes a VM program on
  multiple contexts across multiple blocks. This is the dominant cost of
  qualification, and it is *per specification*, not per campaign.
* **R2 The level check is empirical.** It bounds `p0` at whatever resolution
  the decoy count buys. A specification whose true level sits just under the
  threshold is indistinguishable from one just over it at any finite N.
* **R3 The level check assumes the canonical reference law is the right null.**
  If the reference law is wrong (not corpus-fitted, merely inappropriate),
  `p0` is measured against the wrong hypothesis and can pass while the
  scientific claim is meaningless. This is not a statistical failure; it is a
  modelling one, and no harness detects it.
* **R4 Adaptive registration across candidates.** The bound is additive by
  linearity over candidates, so no independence is required — but an attacker
  who can propose many specifications and keep only the ones whose measured
  `p0` came out low is selecting on measurement noise. **The measured `p0`
  must be the one from a pre-committed decoy stream, and re-measurement after
  a failed qualification must be treated as a new specification.**
