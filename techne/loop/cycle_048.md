## 🟢 HITL #78 — REACTIVATION CONDITION FIRED, AND THE DEFECT NEVER BIT

`p1_bandread.json` appeared — a pre-declared trigger. I reopened and checked immediately.

**The campaign ENDED at P1.** `campaign_end`, verdict `UNDECIDED-UNDERPOWERED`, coverage
1240/1240, `n_required_for_decidability: 2969`. **P3 constructs `Arms`; P3 never ran.** The
`F-prom-retrieved` arm was never built, so the 100%-drop loader **never touched a result**.

**Realised blast radius of HITL #78: ZERO.** The loader is still broken (1248 rows, 0 accepted),
and it remains latent for any future campaign reaching P3. But the twenty-cycle worry is now
settled for this run, not by argument but by the campaign's own append-only log.

*One honest note on my own detector:* I wrote the trigger as "a P3/P4 record appears **or**
`p1_bandread.json` appears". `p1_bandread.json` is P1's own output — it fires at the *end of P1*,
not at the start of P3. So the trigger was **over-broad**, and fired in the safe direction. I would
rather have that than the reverse, but it was imprecise and is now recorded as such.

Arsenal red: **29** (26 dependency artifacts; #242 unruled, nothing installed).

# Cycle 048 — the precision worry does not bite, and I overstated it last cycle

## Pre-registered, then measured

`rung_notes/MAHLER_PRECISION_BITES_PREREG.md`, committed `e6da78d9` before reading a single band
constant. Three "bites" criteria fixed in advance.

**Prediction 1 — the band is not near Lehmer's constant: FALSIFIED.** `BAND_HIGH = 1.18`, and
Lehmer's number is 1.17628…. The band's *entire content* is Lehmer.

**Prediction 2 — the sort has near-ties within 5.1e-6: HELD, 20 of 20.**

**Prediction 3 — overall it does not bite: HELD**, but for a reason I had not anticipated.

## The three criteria, measured

```
CRITERION 2  threshold        closest live value to BAND_HIGH = 3.719e-03   NOT MET
CRITERION 3  Lehmer compare   |BAND_HIGH - Lehmer|          = 3.719e-03   NOT MET
CRITERION 1  ranking ties     20 of 20 adjacent gaps <= 5.1e-6            MET
```

Criterion 1 is met and still does not bite, because **the values are stored literals**.
`CORPUS_SOURCE = prometheus_math.databases.mahler.MAHLER_TABLE`, and my function appears there only
in a *verification* path — recompute and compare — never as the source of the stored number. The
sort order is therefore deterministic across runs and my precision never enters it.

## Where the precision does land — and the number that closes it

`lookup_by_M(M, tol=1e-6)` is the one place a consumer's correctness depends on my function's
accuracy: compute `M`, look it up, and a too-large error returns `[]` — *an absence read as "not in
the catalog"*, which is this loop's oldest shape.

So I recomputed **all 8,625 catalog entries** and compared against their stored values:

```
max absolute |recomputed - stored| = 4.481e-10
entries exceeding lookup_by_M's default tol=1e-6 = 0 of 8625
```

**Four orders of magnitude of headroom.** VERDICT: **DOES NOT BITE.** HITL #266 is answered —
documenting the limit is enough.

## The correction I owe cycle 047

Cycle 047 wrote: *"a 5e-6 error is larger than the gaps such a search resolves, so a candidate
could be mis-ranked."*

**That was speculation stated with too much force.** The 5.1e-6 figure came from a *synthetic*
product of two Hypothesis-drawn polynomials — a deliberately awkward object. On the actual
published catalog the error is **4.481e-10**. I generalised from one synthetic worst case to real
usage without checking, which is cycle 045's "inflated cost presented as prudence" error running
in the opposite direction: an **inflated risk presented as diligence**.

The 5.1e-6 measurement stands. The *inference* from it did not, and one cycle of measurement was
the whole cost of finding that out.

## A finding I did not go looking for

The band `1.001 < M < 1.18` selects **21 entries, and every one has Lehmer's measure.**

They are genuinely 21 *distinct* polynomials, degrees 10 through 28 — Lehmer's polynomial times
Φ₁, Φ₂, Φ₃, … plus "Lehmer-extension" variants. But **M is multiplicative and cyclotomics have
M = 1**, so multiplying by them changes the polynomial and not its measure. Their stored measures
span **2.1e-14** — floating-point noise.

`stage0b/corpus.py` sorts them by `(mahler_measure, coeffs)` with the comment *"so the slice is
reproducible across runs"*. It **is** reproducible, since the values are frozen literals. But the
ordering is decided by rounding in the 14th–16th decimal, and `coeffs` — the intended
tiebreaker — is only consulted on *exact* ties, so it almost never runs. **Anything sorting this
slice by measure is sorting by noise, not mathematics.**

That is aporia's experiment, not mine to patch, so it is HITL #274 rather than a diff.

## What I changed in my own tree

`prometheus_math/tests/test_mahler_catalog_precision.py` — 5 tests pinning the **real-data** budget
so `lookup_by_M`'s tolerance stays defensible: if a future change degrades accuracy toward 1e-6,
lookups start silently returning `[]`.

**My own assertion failed first**, and the failure was mine: I wrote `BUDGET < default/100` with
`BUDGET = 1e-8` and `default/100 = 1e-8` — strict inequality on equal numbers. **I fixed the
assertion, not the budget.** Loosening `BUDGET` to satisfy a mis-stated inequality would have been
moving a goalpost that was set from a measurement.

## Postcondition, by name-diff

```
047   29 failed / 3518 passed
048   30 failed / 3546 passed
NEW   test_extract_anti_anchor_claims_v0_1::...test_couplet_claim_does_not_dispatch_primary_verifier
GONE  none
```

**The new failure is not mine, and I checked rather than assumed.** It passes in isolation, its
whole file passes (12/12), and running it in one process directly after both of my new files gives
**40 passed**. It is unrelated by subject — text extraction, not number theory. Second
order-dependent flake surfaced in four cycles (cycle 045's was `test_sigma_env_learning`).
**I cannot prove it predates this cycle without a bisect, and I do not claim that.**

Also worth stating: I nearly diffed against an **incomplete** background run whose file still held
partial output, which would have reported "29 → 0 failures". Caught it because the numbers were
absurd, not because I had a guard. The name-diff discipline saved a false report only by luck.

## Track 1 — `prometheus_math.house` (Everest & Ward 1999)

23 tests, RED first, four categories. The third and cheapest height, with the sharpest domain.

- **Authority**: **Lehmer's polynomial is Salem** — one root outside the unit circle — so
  `house = M` exactly, which makes one test an authority check on *both* quantities at 1.176280818…
  Plus golden ratio, linear cases, four cyclotomics.
- **Property**: positive except on monomials; **the monic bound `house ≤ M ≤ house^deg`**, guarded
  on the *actual* precondition `|a_n| = 1` rather than a proxy — the lower bound genuinely fails
  for non-monic `f`, which is why `2x − 1` has house 0.5 and measure 2; scale-invariance, the
  property that distinguishes it from M.
- **Edge**: the zero polynomial refuses; **a non-zero CONSTANT refuses** — it has no roots, so its
  house is a max over the empty set, while `M` and `L` are both defined there and equal `|c|`; and
  a **monomial correctly returns 0.0**, which is exactly why the constant case must refuse rather
  than return zero, or the two would be indistinguishable.
- **Composition**: Kronecker's `house = 1 ⟺ M = 1`; the Salem identity; and `house ≤ M ≤ L`
  chaining all three heights built across 047–048.

## TLDR — ELI5

Two worries closed this cycle, both by measuring instead of arguing.

**The loader bug never hurt anything.** For twenty cycles I've been flagging that a data loader
throws away every row, and warning that an experiment would eventually be poisoned by it. This
cycle the trigger I'd set fired — and when I looked, the experiment had *stopped early* for a
completely unrelated statistical reason, before it ever reached the stage that uses the broken
loader. The bug is still there. It just never got the chance.

**And last cycle I cried wolf.** I'd found the Mahler-measure function could be off by 5 parts in a
million on an awkward test case, and said that could mis-rank real candidates. So I checked all
8,625 real entries: the actual error is 4 parts in ten billion — ten thousand times better than the
number I'd worried about, and four orders of magnitude inside the tolerance that matters. My
warning was built from one artificial example I'd made up myself and never checked against real
data.

The interesting accident: the "interesting band" of that database contains 21 polynomials that all
have *exactly the same* measure — they're Lehmer's famous polynomial multiplied by things that
don't change the answer. Code elsewhere sorts them by that measure to get a stable order, which
means it's really sorting by rounding errors in the 14th decimal place.

## For ChatGPT

```
Prometheus loop, cycle 048. TWO WORRIES CLOSED BY MEASUREMENT, one of them my own overstatement.

*** HITL #78: REACTIVATION CONDITION FIRED, AND THE DEFECT NEVER BIT ***
p1_bandread.json appeared (a pre-declared trigger). Checked immediately: THE CAMPAIGN ENDED AT P1.
campaign_end logged, verdict UNDECIDED-UNDERPOWERED, coverage 1240/1240,
n_required_for_decidability 2969. P3 constructs Arms; P3 NEVER RAN. The F-prom-retrieved arm was
never built. REALISED BLAST RADIUS: ZERO. Loader still broken (1248 rows, 0 accepted) and still
latent for any future campaign reaching P3, but the twenty-cycle worry is settled for this run by
the campaign's own append-only log.
MY DETECTOR WAS OVER-BROAD: I wrote the trigger as "P3/P4 record OR p1_bandread.json appears", but
bandread is P1's OWN OUTPUT — it fires at the END of P1, not the start of P3. It fired in the safe
direction, but it was imprecise and is recorded as such.

*** THE PRECISION WORRY DOES NOT BITE, AND I OVERSTATED IT IN 047 ***
Pre-registered (e6da78d9) before reading any band constant, three "bites" criteria fixed.
  PREDICTION 1 (band not near Lehmer): FALSIFIED. BAND_HIGH = 1.18; Lehmer is 1.17628. The band's
    ENTIRE CONTENT is Lehmer.
  PREDICTION 2 (near-ties within 5.1e-6): HELD, 20 of 20 adjacent gaps.
  PREDICTION 3 (does not bite): HELD, for a reason I had not anticipated.
    criterion 2 threshold      closest live value to BAND_HIGH = 3.719e-03   NOT MET
    criterion 3 Lehmer compare |BAND_HIGH - Lehmer|            = 3.719e-03   NOT MET
    criterion 1 ranking ties   20/20 gaps <= 5.1e-6                          MET
Criterion 1 is MET and still does not bite, because THE VALUES ARE STORED LITERALS. My function
appears in that module only in a VERIFICATION path, never as the source of the stored number, so
the sort is deterministic and my precision never enters it.

WHERE THE PRECISION ACTUALLY LANDS: lookup_by_M(M, tol=1e-6). A consumer computes M, looks it up,
and a too-large error returns [] — an absence read as "not in the catalog". So I recomputed ALL
8,625 CATALOG ENTRIES: max absolute |recomputed - stored| = 4.481e-10; entries exceeding tol=1e-6 =
ZERO. Four orders of headroom. VERDICT: DOES NOT BITE. HITL #266 answered — documenting is enough.

THE CORRECTION I OWE CYCLE 047: I wrote "a 5e-6 error is larger than the gaps such a search
resolves, so a candidate could be mis-ranked." THAT WAS SPECULATION STATED WITH TOO MUCH FORCE. The
5.1e-6 came from a SYNTHETIC product of two Hypothesis-drawn polynomials. On the real catalog the
error is 4.481e-10. I generalised from one synthetic worst case to real usage without checking —
cycle 045's "inflated cost presented as prudence" running backwards: AN INFLATED RISK PRESENTED AS
DILIGENCE. The measurement stands; the inference did not.

A FINDING I DID NOT GO LOOKING FOR: the band 1.001 < M < 1.18 selects 21 entries and EVERY ONE HAS
LEHMER'S MEASURE. They are 21 genuinely distinct polynomials, degrees 10-28 — Lehmer x Phi_1,
Lehmer x Phi_2, Lehmer-extensions — but M is multiplicative and cyclotomics have M=1, so they
change the polynomial and not its measure. Stored measures span 2.1e-14. stage0b sorts them by
(mahler_measure, coeffs) "so the slice is reproducible": it IS reproducible (frozen literals) but
the order is decided by rounding in the 14th-16th decimal, and the `coeffs` tiebreaker only fires
on EXACT ties so it almost never runs. ANYTHING SORTING THAT SLICE BY MEASURE IS SORTING BY NOISE.
Aporia's experiment, not mine to patch -> HITL #274.

IN MY OWN TREE: test_mahler_catalog_precision.py, 5 tests pinning the REAL-DATA budget so
lookup_by_M's tolerance stays defensible. MY OWN ASSERTION FAILED FIRST and the failure was mine —
I wrote BUDGET < default/100 with both equal to 1e-8. I FIXED THE ASSERTION, NOT THE BUDGET;
loosening a measured budget to satisfy a mis-stated inequality is moving a goalpost.

Track 1: prometheus_math.house (Everest & Ward 1999 ch.1). 23 tests, RED first, four categories.
Authority: LEHMER'S POLYNOMIAL IS SALEM so house = M exactly — one test is an authority check on
BOTH quantities. Property: monic bound house <= M <= house^deg, guarded on the ACTUAL precondition
|a_n|=1 (the lower bound genuinely fails for non-monic: 2x-1 has house 0.5 and measure 2);
scale-invariance, which M does not have. Edge: zero polynomial refuses; A NON-ZERO CONSTANT REFUSES
(no roots at all, while M and L are defined and equal |c|); A MONOMIAL CORRECTLY RETURNS 0.0 —
which is exactly why the constant must refuse rather than return zero. Composition: Kronecker
house=1 iff M=1; the Salem identity; house <= M <= L across all three heights.

What I want attacked:
1. I closed the precision worry on the CURRENT catalog. But mahler_measure is also called on
   polynomials NOT in the catalog (charon's generators construct new ones). My 8,625-entry
   measurement says nothing about those. Is "does not bite" too strong a verdict for a check whose
   population was the stored table?
2. Cycle 047 overstated a risk; cycle 045 overstated a cost. Both were single unrepresentative
   measurements generalised to real usage. That is now twice. Is there a rule that would have
   caught both, beyond "measure before inferring"?
3. The 21-states-one-measure finding is in another role's live experiment and I cannot fix it. Does
   flagging it as HITL discharge my obligation, or should the loop be doing something more with
   findings it is structurally barred from acting on?
```

## Traps ledger additions

- **Generalising from one synthetic worst case to real usage** — cycle 047's 5.1e-6 came from a
  Hypothesis-built product; the real catalog runs at 4.481e-10. Defence: before inferring an
  operational risk from a measured extreme, measure the same quantity on the population that
  actually occurs.
- **A trigger condition that names an event later than the one it means** — `p1_bandread.json`
  marks the END of P1, not the start of P3. Fired safe, but imprecise. Defence: a reactivation
  condition should name the earliest event that implies the harm, and no earlier.
- **A sort key whose ties are resolved by rounding** — 21 equal measures ordered by 1e-16 noise,
  with the intended `coeffs` tiebreaker only firing on exact equality. Defence: when a float sort
  key can be mathematically equal across entries, compare it at a stated tolerance or sort on the
  exact key alone.
- **Fixing a measured budget to satisfy a mis-stated assertion** — nearly did; the assertion was
  wrong, and budgets set from measurements are not the adjustable end.
