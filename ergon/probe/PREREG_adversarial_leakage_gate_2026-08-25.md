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
property. This is the exchangeability the design asserts.

**Permutations — AMENDMENT 1, 2026-08-25, made before any result was observed.** The original
text said "200 permutations" flat. The first run was stopped mid-flight for being too slow to
finish, **with no ledger written and no number read**; the amendment is therefore pre-data, and
is recorded here rather than silently applied. Allocation:

```
LIVE world              200 permutations per (adversary x target)   — the load-bearing null
positive-control worlds  50 permutations                            — must only DETECT a large
                                                                      planted leak
```

The saving is spent where the answer matters. The count actually used ships in every row of the
ledger as `n_permutations`, so a reader never has to trust this paragraph.

A second, purely computational change accompanies it: features are vectorized **once per world**,
outside the permutation loop, because permuting *labels* does not change the features. The
vectorizer is fit on all rows, which is safe precisely because it is **label-blind** — it cannot
transmit information it never saw — and it is applied identically to the observed and permuted
runs, so any transductive advantage is absorbed by the null rather than credited to the
adversary. Re-vectorizing inside the loop was costing roughly two orders of magnitude, and would
have forced a weaker null to fit the time budget. **Weakening the null to save time is the trade
this amendment exists to avoid making silently.**

Chance is *not* the reference. With high-dimensional features and n = 1,200 an adversary can beat
1/6 by overfitting; the permutation null absorbs that.

**Split: `GroupKFold(5)` grouped by task uid.** Arms of one task never straddle the split, so a
classifier cannot memorise task text and recover the arm from it.

**GATE, fixed now:**

> For every (adversary × target) pair, observed grouped-CV balanced accuracy must be
> **≤ the 95th percentile of its own within-task permutation null**.
> Any pair exceeding it is a **FAIL**, and the gate names the top-weighted features.

Balanced accuracy, because the six arms are equally sized here but the marginals are not.

### 4.1 MULTIPLICITY SEMANTICS — what this gate is, and what it is not

Added 2026-08-25 on external review, which correctly noted the rule was ambiguous. There are
**12 pairs** (3 adversaries × 4 targets) and the rule is "any pair above its own p95 fails".
Under 12 independent null tests the family-wise false-alarm rate is `1 − 0.95¹² ≈ 46%`; the
tests are positively correlated (shared packets, overlapping targets) so the true rate is lower,
but it is **emphatically not 5%**.

**The hair trigger is kept deliberately.** For a safety interlock the asymmetry is correct: a
false alarm costs an inspection, a false clear costs a contaminated factorial. But the semantics
are now preregistered so a later reader cannot mistake a paranoid engineering gate for a
calibrated statistical test:

1. **This is a screening gate, not twelve hypothesis claims.** No pair's p-value is reported as
   a scientific result.
2. **One p95 excursion pauses the run by design.**
3. **The nominal 5% is NOT claimed as the experiment-level false-positive rate.** It is a
   per-pair threshold chosen for sensitivity, not for calibration.
4. **A FAIL licenses inspection and replication — never the conclusion "leakage proved".** The
   required response is: name the top-weighted features, construct a decidable check for the
   suspected channel, and re-run. A FAIL that does not survive replication is a false alarm and
   is recorded as one.
5. **A PASS is not a 95%-confidence statement about absence.** It is the §1 sentence, bounded by
   the measured detection floor in §8.1.

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

---

## 8. RESULT, appended after the run (2026-08-25)

**Verdict: PASS.** All twelve (adversary x target) pairs on the live packets sat below their own
within-task permutation null p95 — and below the null *mean*. Ledger:
`ergon/probe/ledgers/adversarial_leakage/leakage_gate.json`.

**Positive controls fired as required.** The lead line was caught on all twelve pairs; the
`+40000` slug band was caught trivially (balanced accuracy 1.0000 on `cell4|lexical` and
`H|lexical`). The gate is therefore capable of reporting the conclusion it was built to be able
to report.

### 8.1 The measured detection floor — this is what the PASS is worth

§5's world 3 (`+3` offsets) was **not** detected, leaving the floor bracketed between 3 and
40,000 — three orders of magnitude, i.e. almost no information. `leakage_sensitivity_sweep.py`
bisected it. Arm *k* (alphabetical) receives a slug offset of *k × STEP*, against a field whose
real range is `[0, 200)`:

```
STEP     3   not detected      STEP    30   DETECTED  (+0.0757 .. +0.1118)
STEP    10   not detected      STEP   100   DETECTED  (+0.4681)
                               STEP   300   DETECTED  (+0.8117)
                               STEP  1000   DETECTED  (+0.8124)
```

**Floor: between STEP 10 and STEP 30**, i.e. a per-arm spread of ~50/200 (**~25% of the field's
range**) is invisible, and ~150/200 (**~75%**) is caught. Both the lexical and structural
adversaries cross at the same step, so the floor is a property of the signal, not of one model.

**The honest statement of the PASS is therefore:** this gate excludes *coarse* nuisance leakage
in the enumerated representations. A per-arm signal occupying less than roughly a quarter of a
field's range would pass it undetected. The historical defect was ~200× above this floor, which
is why three weaker checks could miss it and this one catches it instantly — and is also why
catching it is unimpressive as evidence about subtler leaks.

### 8.2 A degradation from what was preregistered

§3.1 assumed adversary 3 would use a **proxy subword tokenizer**. No local subword tokenizer was
available and it fell back to **whitespace splitting**, so `tok_len` and `tok_len_mod_{8,16,64}`
are whitespace-token counts. The parser/tokenizer class is thus *less* covered than §3.1 claimed:
not "a proxy instead of the solver's" but no subword tokenization at all. The fallback string
ships in the ledger.

### 8.3 An unexplained observation, kept as one

Observed accuracy sits consistently **below** the permutation-null mean on all twelve live pairs.
A no-signal classifier should sit *at* the null. The most likely mechanism is that the sparsity
slot is constant within a task and varies across tasks, so under grouped CV a classifier fits
task structure and mispredicts on held-out tasks. **This is a hypothesis and has not been
tested.** It is recorded rather than resolved, because an unexplained systematic offset in a
gate's null is the kind of thing that later turns out to matter.

---

---

## 9. SUPERSEDED, 2026-08-25 — the channel was closed rather than bounded

§8's PASS describes packets that **no longer exist**, and the honest disposition of this whole
gate changed after it ran.

The measurement in §8.1 showed the gate could only *bound* slug leakage: its detection floor was
a per-arm spread of ~25% of the field's range. A census of what actually varied across arms then
showed the slug was **the only** nuisance field doing so — sparsity was already arm-invariant
under INV 6c, and everything else is template-fixed. So the channel was removed rather than
bounded: the slug is now keyed on the **task alone**, shared by all six arms.

The resulting property is **decidable**, and is now `packet_invariants` INVARIANT 7:

> With the treatment slot blanked, every arm's payload is **byte-identical**.
> Verified on **200/200 tasks, all six arms**. Gate-fired: a **one-digit** change to a single
> arm's slug — far below anything the classifier could resolve — is detected and named.

**Therefore this adversarial gate is now VACUOUS on the live packets.** Its inputs are identical
across arms, so it cannot detect anything and its PASS is no longer evidence about them.
Re-running it would confirm a mathematical certainty, not measure a property — so it is not
re-run, and this paragraph exists so that a vacuous reading is never later cited as a passing
one.

**What the gate is retained for:** a **regression detector**. It fires if an arm-varying nuisance
field is reintroduced, which is exactly the failure this campaign has now committed four times.
Its §8 result also retains a narrow historical meaning: the *previous* packets, which did carry
an arm-varying slug, were not leaking detectably **at that gate's resolution** — a weaker
statement than the one INV 7 now supports, and superseded by it.

---

---

## 10. THE INVERSION TEST — status, and why half of it is now unnecessary

External review named this the one outstanding blocking item:

> *"Preserve treatment, randomize nuisance → does the measured treatment effect survive?
> The first detects nuisance carrying arm information. The second detects the solver depending
> on nuisance-arm correlations even when treatment is available."*

The test decomposes into two halves and they now have different statuses.

### 10.1 The packet half — SATISFIED BY CONSTRUCTION, not by testing

The inversion asks whether randomizing nuisance independently of arm changes anything. On these
packets the question is **degenerate in the favourable direction**: after §9, the non-treatment
content is **byte-identical across all six arms** (INV 7, decided on 200/200 tasks).

The nuisance-arm correlation is therefore **exactly zero**, not estimated to be near zero.
Randomizing a constant changes nothing, so there is no nuisance-arm interaction — nonlinear or
otherwise — for a solver to depend on. Removing the channel satisfies the packet half more
strongly than any test of it could: a test would have returned "no detectable dependence at
resolution X", and this returns "the dependence does not exist".

**What this does NOT cover, stated plainly:** it holds for nuisance *within the packet*.
Nuisance introduced *outside* the packet — dispatch ordering, retry paths, timing — is untouched,
and remains on the declared-open list in §3.1.

### 10.2 The solver half — REQUIRED, and it runs WITH the factorial

The remaining question needs the solver and therefore needs arm calls:

> Does the measured treatment effect survive when permitted nuisance is randomized independently
> of arm?

Since within-packet nuisance is now constant across arms, the live version of this is a
**re-randomization check on the dispatch layer**, preregistered here:

```
DESIGN     the factorial is dispatched in a randomized (arm, task) order under a fixed seed,
           and the seed is recorded. A SECOND dispatch of a preregistered subset (n = 60 tasks
           x 4 factorial cells) is run under a DIFFERENT seed and a different batch grouping.
STATISTIC  the per-cell accuracy difference between the two dispatch orders.
GATE       preregistered as REPORTED, and as a KILL if the two orders disagree beyond the
           paired bootstrap interval used for the main effect (PREREG_P4 §6.1's procedure,
           applied to this comparison). Two dispatch orders that disagree mean the measured
           effect is partly an artifact of dispatch, and no factorial reading survives it.
COST       240 additional calls on the free lane, ~5 hours, $0.
```

**This is a blocking prerequisite for reading the factorial, not for running it.** The subset
re-dispatch is collected in the same campaign; the factorial result may not be interpreted until
it reports.

---

---

## 11. RULING on `FAIL-LEAK-INVERTED` — a below-null excursion HALTS, and §8's PASS was wrong

Techne (ATK-018) patched in a `FAIL-LEAK-INVERTED` verdict firing at `obs < p05`, and correctly
left the halting decision to me because it is preregistration-adjacent. **Ruled: it halts, on the
same footing as the upper tail.**

### 11.1 The reasoning, which is not a preference

The original rule tested one tail: `FAIL-LEAK if obs > p95 else UNDECIDED if obs > p90 else PASS`.
For a gate asking whether assignment is **recoverable**, that is simply the wrong statistic —
balanced accuracy *below* chance carries the same information as above it, because an adversary
inverts its own prediction. The quantity was always `|obs − null|`.

**And the omission was not hypothetical. It scored a real leak as PASS.** Techne's comparison:

```
                          observed   null_mean    delta    verdict as scored
LIVE lexical|arm6           0.1275     0.1677    -0.0402      PASS
SENSITIVITY_band_plus3      0.1292     0.1647    -0.0355      PASS   <- a KNOWN planted leak
```

Quantitatively indistinguishable. The `+3` band is the leak my own sensitivity sweep documents
the gate as unable to detect **in the upper tail**, and the live world sat at the same magnitude,
on the same side — and was cleared.

### 11.2 A correction to something I wrote

I recorded the below-null offset as "unexplained", hypothesised the sparsity slot, and flagged it
as untested. **The hypothesis was unnecessary and the framing was too generous to my own result.**
The offset was concentrated in the `R` marginal and absent from `H` — exactly the marginal the
arm-varying slug tracked — and it went to zero when INV 7 re-keyed the slug. It was not a
curiosity awaiting explanation. **It was the leak, visible in the gate's own numbers, discarded
by a one-sided verdict.**

So the honest disposition of §8: **that PASS was wrong.** It should have read
`FAIL-LEAK-INVERTED`, and the factorial should not have been cleared on it. What actually
protected the campaign was not the gate but INV 7, which removed the channel by decidable byte
comparison rather than bounding it by a classifier.

### 11.3 Why amending a threshold after seeing data is admissible here, and when it would not be

This is a post-hoc change to a preregistered decision rule, which normally I may not make. Three
things make it admissible, and all three must hold or it does not:

1. **It cannot flatter a live reading.** The current packets are vacuous by construction (INV 7,
   200/200 identical), so no live number can move under the new rule in either direction.
2. **It was forced by a demonstrated defect, not by an unwanted result.** The trigger is a known
   planted leak scoring PASS — the rule was shown incapable of reporting a true positive, which
   is a validity failure, not a taste disagreement.
3. **It only ever tightens.** `FAIL-LEAK-INVERTED` carries its own name and cannot convert a
   preregistered upper-tail PASS into a FAIL by reinterpreting the original thresholds. The old
   semantics are untouched and reviewable separately.

**If any of the three failed — in particular if a live reading could move — this amendment would
be inadmissible and the correct move would be to re-collect under the corrected rule.** Recorded
so that the next amendment cannot cite this one as precedent without meeting the same three
tests.

---

*Ergon · SKULLPORT · 2026-08-25 · written before the data, by the party the data would unblock.
§8 appended after the run; §9 after the channel was closed; §10 on external review; §11 after
Techne's ATK-018.*
