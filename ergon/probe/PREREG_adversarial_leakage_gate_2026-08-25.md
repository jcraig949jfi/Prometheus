# Preregistration — the adversarial assignment-leakage gate

**Ergon · SKULLPORT (M1) · 2026-08-25 · written BEFORE the adversary is run.**
**No number in this file exists yet.** Thresholds and nulls are fixed here, not after seeing a
result. Prompted by an external review that identified the previous claim as malformed.

---

## 1. The claim being retired, and why it was wrong

**RETIRED:** *"arm identity is computationally unavailable."*

It is not achievable and it is not what the experiment needs. **The treatment identifies the
arm.** If residue is present, or a method hint is present, a capable solver is entitled to notice
— that is the manipulation. A packet-shape check can pass in full while the wrong property is
being tested.

A second defect in the wording, found while formalising it: the reviewer's conditional form
`I(A; N | R, H) ≈ 0` is **degenerate for this design**. The arm label `A` is a *deterministic
function* of `(R, H)` — six arms, six `(R,H)` combinations — so conditioning on `(R,H)` fixes `A`
and the mutual information is zero by construction, whatever the packets look like. The
conditional wording is right in spirit and unmeasurable as written here.

**What is measurable is the destructive form**: remove the treatment content, and ask whether
assignment survives in what remains.

**ADOPTED CLAIM — the only sentence the artifacts may assert:**

> No tested adversary recovered assignment above its preregistered permutation null, from the
> non-treatment content of held-out packets, at any of three representations.

That sentence has an attack surface: it names the adversaries, the null, the representation, and
the split. "Computationally unavailable" has none.

---

## 2. The design, stated so `T` and `N` are unambiguous

The factorial is **3 × 2**, not 2 × 2:

```
R (residue)  ∈ { generic , null , prom }      H (method hint) ∈ { absent , present }
  generic  = generic advice, no task provenance
  null     = a real prior-attempt record drawn from a DIFFERENT task
  prom     = the record from THIS task
A = (R, H)  — six arms
```

**Treatment content `T`** is exactly the `items` slot of the packet template: the method census
(for `null`/`prom`), the generic advice list (for `generic`), and the hint tokens (for `H+`).

**Nuisance `N`** is *everything else in the delivered prompt*: the frame, the synthetic record
id (slug) including its digits, the sparsity block, whitespace, punctuation, ordering, lengths,
and the shared task text.

**The destructive test:** replace the `items` slot with a single constant token, then attempt to
recover `A` from what remains. Any recovery above null is nuisance leakage, and no guess about
its feature class is required to detect it.

---

## 3. Adversaries — fixed now

All operate on the **constantized** payload. Numbers, whitespace, punctuation, Unicode and
ordering are **not** normalised first; normalising is how the previous checks erased the evidence.

1. **Lexical.** Character n-grams (1–5), TF-IDF, logistic regression. Sees literals and digits.
2. **Structural.** An explicit vector: byte length, line count, token count, digit count and
   digit-run count, the slug's integer value, counts per Unicode general category, whitespace-run
   histogram, delimiter counts, terminal-newline flag, treatment-slot start/end offsets, and the
   length of every field. Gradient-boosted trees, so **interactions** are available — the
   previous failure was invisible to univariate censuses.
3. **Distributional.** Compression ratio (zlib), Shannon entropy, vocabulary size, digit
   frequency, punctuation frequency, char histogram, proxy-tokenizer length and that length
   modulo 8/16/64. Logistic regression.

**Targets, all four scored separately:** the 6-way arm label; the 4-way factorial cell; and the
two marginals `R` (3-way) and `H` (2-way). A leak may exist in a marginal and cancel in the
joint.

### 3.1 Declared gaps, so they are not later discovered as surprises

- **Tokenizer is a proxy.** The solver is `nvidia:deepseek-v4-flash` and its tokenizer is not
  available locally. Adversary 3 uses a local tokenizer as a stand-in. **This gate therefore
  does not close the parser/tokenizer attack class** — two strings isomorphic to my checker may
  tokenize differently for the real solver. Recorded as an open hole, not as covered.
- **Cross-instance and generation-path attacks are only partially covered.** The slug is
  deterministic in `(arm, uid)` and enters adversary 2 as an integer, so an id-increment or
  seed-stream leak within a task would be caught. Ordering effects *across* packets in a
  dispatch batch are **not** tested here.
- **Failure-path attacks are not covered.** Malformed values, truncation and retry defaults are
  not exercised, because every packet in this population renders cleanly. Open.

---

## 4. The null, and the gate — fixed before measurement

**Null: permutation of arm labels WITHIN task.** Each task contributes exactly one packet per
arm, so permuting the six labels within a task destroys arm identity while preserving every task
property. This is the exchangeability the design asserts. **200 permutations.**

Chance is *not* the reference. With high-dimensional features and n = 1,200 an adversary can beat
1/6 by overfitting; the permutation null absorbs that.

**Split: `GroupKFold(5)` grouped by task uid.** Arms of one task never straddle the split, so a
classifier cannot memorise task text and recover the arm from it.

**GATE, fixed now:**

> For every (adversary × target) pair, observed grouped-CV balanced accuracy must be
> **≤ the 95th percentile of its own within-task permutation null**.
> Any pair exceeding it is a **FAIL**, and the gate names the top-weighted features.

Balanced accuracy, because the six arms are equally sized here but the marginals are not.

**If the gate FAILS, P2 does not run.** The finding is that nuisance leakage exists, and the
named features are the next repair. This is the outcome I least want and the reason the threshold
is written down first.

**A near-miss is not a pass.** If any observed value lands within the null's p90–p95 band, the
result is **UNDECIDED** and re-run with 1,000 permutations before being read either way.

---

## 5. Positive control — required, and it runs FIRST

An adversary that cannot detect a *known* leak proves nothing when it reports a null. Before the
real read, the same pipeline is run against three constructed worlds:

1. **The lead line**, re-injected on 2 of 6 arms (the killed 400/400 defect).
2. **The slug band**, re-injected as `+40000`-style per-arm offsets (the killed 200/200 defect).
3. **A subtle band**: a per-arm offset of **+3** on the slug index — deliberately far smaller than
   the historical defect, to measure sensitivity rather than merely confirm the obvious.

**Adversaries 1 and 2 must exceed their nulls on worlds 1 and 2.** If they do not, the adversary
is too weak and **no null reading from it is interpretable** — that is itself a terminal finding
about the gate, reported as such.

World 3's result is **reported, not gated**: it estimates the smallest leak this gate can see,
which is the honest statement of what a PASS means.

**Negative control:** the same pipeline on the current live packets with treatment constantized
*and* arm labels randomised — must sit at null. Without it, a FAIL could be an artifact of the
harness.

---

## 6. What a PASS does and does not license

**Does:** it licenses the §1 sentence, scoped to the three adversaries, three representations,
four targets, and the enumerated gaps in §3.1.

**Does not:** it does not establish that no arm label exists. Nothing finite can. The three
attack classes named in §3.1 as uncovered remain uncovered, and the honest summary of 2026-08-25
is that three previous checks felt equally complete on the morning they were passing over a
400/400 label.

---

## 7. Standing constraints

- No LLM is called. Everything here is deterministic and local; total spend $0.
- The pinned manifests are read-only. Output goes only to
  `ergon/probe/ledgers/adversarial_leakage/`.
- **Conflict of interest:** a PASS unblocks my own run, and I wrote both the adversaries and the
  packets they attack. The positive controls in §5 are the structural answer available to me;
  they are necessary and not sufficient, because — per the same review — **mutation competence
  and omission competence are different capabilities**, and gate-firing does nothing to
  decorrelate the author's conceptual partition from the checker's.

---

*Ergon · SKULLPORT · 2026-08-25 · written before the data, by the party the data would unblock.*
