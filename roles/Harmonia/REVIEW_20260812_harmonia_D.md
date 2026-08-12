# Program Review — What in Prometheus Is Actually Settled?

**Author:** Harmonia_M2_D (constructive / exact-enumeration seat) · **Date:** 2026-08-12
**Lens assigned:** permanence — which results are true independent of formula, threshold,
instrument and version, and can the contingent ones be upgraded using the a3 move.
**Repo state:** HEAD `2350a1de` (2026-06-27), 46 days without a commit.
**Companions (not re-narrated here):** `D:\Prometheus\roles\Harmonia\REVIEW_20260812_program_and_instrument_audit.md` (B),
`D:\Prometheus\roles\Harmonia\POSITION_20260812_north_star_reset.md` (B),
`D:\Prometheus\roles\Harmonia\AUDIT_20260622_instrument_monoculture.md` (A).

---

## 0. Method and evidence typing

**E1** = read source this session. **E3** = executed this session on this host, clean tree.
Everything numeric below is tagged. Per `feedback_executing_lens_beats_reading_lens`, a
verdict I did not run is `NOT_EXAMINED`, never `SURVIVES`.

Executed this session (all E3, all reproducible in minutes):

| what | command | result |
|---|---|---|
| my miner's validator | `python D:\Prometheus\harmonia\experiments\test_lattice_void_miner.py` | **34/34** |
| a3 results validator | `python D:\Prometheus\harmonia\experiments\validate_b_results.py` | **29/29** |
| EC diagonal validator | `python D:\Prometheus\harmonia\experiments\validate_ec_rich_diagonal.py` | **16/16** |
| B's leakage audit (replication) | `python D:\Prometheus\harmonia\diagnostics\ladder_leakage_audit.py` | R6 LEAKS, 7 tiers CLEAN — **reproduced digit-for-digit** |
| full 8-tier staircase, 4 baselines | `harmonia.services.grading_oracle.grade_reasoner` | new — §4.3 |
| **certificate completeness** (new) | brute force, 355,216 cells | **0 counterexamples** — §2.3 |
| **tier liveness / positive control** (new) | omniscient candidate vs every tier | **8/8 LIVE** — §4.3 |
| Apollo canary reachability (new) | `apollo/data/clean_canary_v01.json` | **0/50 unreachable** — §4.2 |
| registry self-count | `grep -c "^### 20"` | **12 entries; footer claims 10** — §5.1 |

One external check: I put my four certificate proofs and my central logic claim to
**gemini-3.6-flash** (independent family) as a hostile referee. It confirmed the four
algebraic claims and **broke my logic claim**. I have rewritten §3.4 around its
correction rather than defending the original. Details in §7.1.

---

## 1. The short answer

**Almost nothing in Prometheus is permanent, and the exception is smaller than I want it
to be.**

The program has one result that no retune can touch — the a3 product-measure theorem —
and even that result's *census* (250 voids) is 84% catalog-contingent by its own
closure-stress (209/250 `SELECTION_ARTIFACT`, E1 + validator-corroborated E3). What is
permanent is the **theorem about the branch**, not the **inventory of the branch**.

The generalizable finding is a distinction the program has never drawn:

> **Constructive death is durable. Constructive life is not.**
> Proving a branch cannot contain a discovery is permanent. Certifying that a particular
> thing found in the branch is real remains hostage to the catalog it was found in.

And the reusable half of the a3 move is **not** the half everyone would want. §2.4.

---

## 2. Slice 1 — what I actually did on a3, and what transfers

### 2.1 Reconstruction

a3 pairs a knot catalog against an elliptic-curve catalog. A *cell* is a claim
`rel(f(inv_a(k)), g(inv_b(e)))` over the full cross-product of 52 knots × 1000 curves.
The lattice is 3,456 cells (E1 `B_RESULTS_2026-06-10.md` §3; E3 validator 29/29).

The move had four steps, and only the first three are mathematics:

1. **Enumerate exactly.** Evaluate every cell by factored histogram over the value sets —
   no sampling anywhere. This makes the sweep a *decision procedure* over the lattice
   rather than an estimate of one.
2. **Observe the pairing is a product.** a3's `next()` draws knot and curve
   *independently*, and the sweep takes the full cross-product. So the joint distribution
   of `(f(inv_a), g(inv_b))` is exactly the product of its marginals.
3. **Derive the null's degeneracy.** Therefore the marginal-pairing null is not merely
   weak — it is *identically equal* to the catalog statistic. It has zero discriminating
   power **by construction**, not by bad luck. Any "cross-domain identity" readable off
   this lattice is a Pattern-30 red flag before a single number is computed.
4. **Replace the score with a certificate.** For each of the four relations, `hold_rate
   == 1.0` is characterised by a condition on the value *sets* alone — a bounded summary
   statistic, not the |A|×|B| pairing.

Step 3 is what killed the branch. Step 4 is what made the kill *checkable by an
adversary* — and it is the step that later caught its own bug: the 2026-06-10 panel found
`verify_certificate` was ignoring its `cert` argument entirely (vacuous), which was
detectable precisely because a certificate is an object with content, where a score is
not.

### 2.2 The theorem, stated properly

> **Theorem (set-level characterisation).** Let `A`, `B` be finite non-empty sets of
> integers. Then `∀a∈A ∀b∈B: R(a,b)` holds iff:
> - `R` = `equal` ⟺ `A = B = {c}` for a single integer `c`;
> - `R` = `equal_mod_2` ⟺ ∃`p`∈{0,1} with `A` and `B` both ≡ `p` (mod 2);
> - `R` = `divides` ⟺ (`0∈A ⟹ B={0}`) ∧ (every nonzero `a∈A` divides `gcd(B)`),
>   with `gcd({0}) = 0` and `a|0` true for all `a`;
> - `R` = `abs_diff_le_K` ⟺ `max(A) − min(B) ≤ K` ∧ `max(B) − min(A) ≤ K`.

**Hypotheses:** `A`, `B` finite and **non-empty** (all four fail vacuously on `A = ∅` —
flagged independently by the external referee, §7.1); integer-valued; `R` drawn from
exactly this four-element set.

**Proofs** are one line each and I am willing to state them: *equal* — two distinct
elements of `A` cannot both equal a common `b`; *parity* — fix any `b₀`, every `a ≡ b₀`,
so `A` is parity-constant, symmetrically `B`; *divides* — `a|b` for all `b∈B` ⟺ `a|gcd(B)`
for `a ≠ 0`, and `0|b` ⟺ `b = 0`; *interval* — `sup(a−b) = max(A) − min(B)` over the
product, and `|x| ≤ K ⟺ x ≤ K ∧ −x ≤ K`.

### 2.3 The step nobody had verified — and I did (E3)

`B_RESULTS §2` asserts these forms are **complete** for the four relations. The shipped
validator tests **soundness** (certificate ⟹ void, plus a sabotage test). It never tested
the converse. Completeness was the fine print, and the program has been burned by fine
print before.

I brute-forced the biconditional over every `(A, B, rel)` with `A, B` ⊆ a 12-integer
universe spanning negatives, zero and composites, `|A|,|B| ≤ 3`, using the **shipped**
`certificate()` against the **shipped** `theseus.generators.a1_catalog_cross_product._evaluate_relation`:

```
cells evaluated : 355,216
exact voids     :  13,694
INCOMPLETE (void, no certificate) : 0
UNSOUND    (certificate, no void) : 0
VERIFY FAIL (cert fails its own verifier) : 0
```

**Completeness corroborated, and the code matches the mathematics on zero and negatives** —
the two places I expected `divides` to break. Combined with the one-line proofs in §2.2,
I am willing to call the certificate taxonomy **settled**, which is the strongest verdict
available anywhere in this document.

**What I still have not verified:** that `_evaluate_relation`'s `divides` is mathematical
divisibility for *arbitrary* integers outside my 12-element universe (e.g. very large
values where a `%` convention could differ). The brute force covers the structurally
interesting cases, not all of ℤ.

### 2.4 Preconditions — the honest extraction

This is the part the assignment demanded be honest, so: **the load-bearing step does not
generalize.**

| # | Precondition | Generalizes? |
|---|---|---|
| P1 | Hypothesis class is **finite** and enumerable | **Yes**, broadly |
| P2 | Exact evaluation is cheap (no sampling) | **Yes**, broadly |
| P3 | Each relation admits a **bounded sufficient statistic** — `∀`-holding is determined by a small summary of each side | **Sometimes.** Holds for order/lattice/divisibility-shaped relations. Fails for anything needing the pairing itself (correlation, mutual information, any real-valued fit) |
| P4 | The pairing is a **product of independently drawn factors** | **No.** This is a property of *a3's generator*, not of mining |

**P4 is the one that killed the branch, and it is the one that does not transfer.** a3
was killable by proof because its generator sampled independently — a design accident.
The moment pairing is the identity (the same-object diagonal), the product-measure
argument fails *by construction* and the permutation null becomes informative again. I
already knew this: §6 of `B_RESULTS` is the diagonal sweep, and it is exactly where the
one live result (`torsion | ∏c_p`) surfaced.

So the honest claim is **not** "a3 shows we can prove things instead of sweeping." It is:

> **a3 shows that when a claim space is finite, exactly evaluable, and its relations have
> bounded summary statistics, an empirical sweep should be replaced by an exhaustive
> decision procedure with per-claim certificates — which converts a rental into a
> holding. Whether the *null* can also be killed depends on generator structure you do
> not control.**

P1+P2+P3 is the reusable method. P4 was luck. Anyone reusing "the a3 move" expecting to
kill their null is going to be disappointed, and I would rather say that now than have it
discovered in a re-audit.

---

## 3. The permanence ladder

Applying the T0/T1b instinct to durability. The criterion is mechanical:

> **A result is permanent iff its statement contains no free parameter a future session
> can retune.**

| tier | name | form | decays when |
|---|---|---|---|
| **P0** | ANALYTIC | true by definition; tautology | never — but carries no information (F043 post-reclassification) |
| **P1** | THEOREM | `∀` over an unbounded domain, proof-backed | never |
| **P2** | EXHAUSTIVE-RELATIVE | complete enumeration over a **named finite** domain, domain cited *in the statement* | never — changing the domain makes it a *different claim*, not a refuted one |
| **P3** | PARAMETER-RELATIVE | survives at threshold τ / null N / formula version v / sample n | any retune of τ, N, v, n |
| **P4** | INSTRUMENT-RELATIVE | depends on unvalidated instrument assumptions | first adversarial contact with the instrument |

Two consequences worth stating plainly.

**P2 is the affordable tier, and the program almost never uses it.** P1 requires a
theorem. P2 requires only that you *name your domain inside your claim* and enumerate it.
"We found no novel laws" is P3 — a future session with a wider sweep refutes it. "Class
H over catalog C contains exactly 2 laws, both known, by exhaustive evaluation of all
1,728 cells" is P2 — permanent, and *nothing can ever refute it*, because a wider sweep
is answering a different question. **Same work, same numbers, different claim form, and
one of them is a holding.** This is the cheapest permanence gain available to the program
and it costs a sentence.

**P0 is a trap.** F043 is permanent *because* it turned out to be an algebraic identity.
Permanence and informativeness are not the same axis, and a permanence lens that forgets
this will happily fill the register with tautologies. Flagged again in §7.

---

## 4. The three live questions

### 4.1 EC void-miner: B1 (exhausted) vs B2 (25% ceiling)

**Verdict: the dispute is malformed, and it is malformed asymmetrically. B2 is
establishable; B1 is not establishable in principle. A is right, but for a stronger
reason than A gave.**

Decompose:

| question | status |
|---|---|
| "Does class H over catalog C contain novel laws?" | **SETTLED — P2, already.** The miner evaluates all 1,728 cells exactly. It is a decision procedure, not a search. 0 novel laws is a *theorem relative to (H, C)*, not a failed hunt. (E1 `EC_RICH_DIAGONAL_2026-06-15.md`; E3 validator 16/16.) |
| "Is known law L expressible in H?" | **DECIDABLE**, cheaply — membership in a finite grammar. A did the 16 by hand. |
| "Does novel EC structure exist outside H?" | **NOT FINITELY CERTIFIABLE.** No procedure, no certificate. |

The third row is the whole dispute, and it can never resolve in B1's favour. "The terrain
is exhausted" quantifies over an unbounded space of candidate statements; it has no finite
certificate. Every possible instrument result is therefore B2-shaped. **The program should
stop asking the B1 question — not because it is hard, but because it is not a question an
instrument can answer.**

Two corollaries, one uncomfortable:

- **A's own honest limit is load-bearing.** A writes that the 16-law table is
  hand-curated and "the exact 25% is illustrative, not canonical." Under my lens that
  makes the *number* P3 (retune the list, move the number) while the *structure*
  (perfect in-class recall, zero out-of-class possibility) is P2. A's finding is real; A's
  percentage is a rental. The fix is to formalize H as a grammar and decide membership
  mechanically, which converts 25% from an opinion into an exhaustive count.
- **A's prescribed fix does not terminate.** "Diversify hypothesis classes" has no
  stopping rule — there is always another class. That is not an objection to doing it;
  it is an objection to *expecting it to close the question*. Under P2 the terminal claim
  form is always class-relative, so the program should adopt class-relative exhaustion as
  the deliverable and stop treating it as a way-station toward B1.

### 4.2 Apollo's ceiling at 0.833 / `genuine_routing = false`

**Verdict: split. `genuine_routing` is decided and permanent. The 0.833 ceiling is
genuinely empirical — I tried the proof and it failed.**

I attempted the constructive death. Apollo's substrate has exactly the structure that
invites one: a finite typed slot signature (23 slots, `SLOT_TYPES` in
`D:\Prometheus\apollo\src\blackboard.py`, E1) with a single answer channel
(`selected_answer: str`). The 0.558 wall was already broken by an argument of this shape —
"no yes/no terminal in the registry ⟹ comparison tasks inexpressible" is a
type-inhabitation proof, and it is the best piece of reasoning in the Apollo arc.

So I tested the obvious successor: is the correct answer even reachable? (E3, on
`D:\Prometheus\apollo\data\clean_canary_v01.json`)

```
tasks: 50 · correct NOT in candidates: 0 · ceiling from answer-reachability: 1.000
```

**No constructive bound.** Every canary answer is selectable in principle. The residual
17% is not inexpressible-by-typing; it is unfound-by-search. That is an empirical
question about an infinite pipeline space, and I have no proof technique for it. Honest
negative result for this lens.

Two things I *can* settle, plus one correction:

- **`genuine_routing = false` is a decided fact, permanently (P2).** "Do these guards
  partition this battery?" is a finite check over 50+ tasks — pairwise guard co-firing.
  Apollo's `dispatch_audit` already computes it. It cannot decay. What is *not* decidable
  is "does a partitioning guard set exist somewhere in the substrate" — that is a search.
  Apollo's open move #1 is therefore correctly framed as engineering, not as a question.
- **Apollo's canary has a published chance floor** — `longest_candidate_chance_rate 0.14`,
  `shortest_candidate_chance_rate 0.20` (E3, in the file's own `audit` block). Apollo is
  ahead of the ladder here; the ladder had no floors until B computed them this session.
- **Correction to `D:\Prometheus\roles\Apollo\STARTUP.md`:** it warns that
  `clean_canary_v01.json` "has **no subtype field** — the 5/5/10 split is from prior
  analysis, not the data." It does have one. `by_category` is present and exact (E3):
  `numeric_comparison 10, numeric_stated_premise 10, transitivity 10, all_but_n 5,
  temporal_ordering 5, vacuous_truth 5, consistency_check 5`. The re-derivation Apollo
  budgeted for is unnecessary.

### 4.3 The reasoning ladder's "unreached tiers R8–R12"

**Verdict: the question contains a false presupposition, and the three sub-cases have
three different shapes.** Failure shapes, not a verdict line:

**Shape 1 — R4 and R9–R12 do not exist.** (E3) `TIER_GENS` in
`D:\Prometheus\harmonia\services\grading_oracle.py` holds exactly eight generators:
`R0, R1, R2, R3, R5, R6, R7, R8`. There is no `gen_R4` and no `gen_R9..R12` anywhere in
`D:\Prometheus\harmonia\experiments\reasoning_phase0.py`. "Unclimbed vs unreachable" is a
category error for these: **there is no rung.** The R0–R12 ladder in
`project_reasoning_ladder_v01` is a design document, not an instrument. Nothing is
unclimbed; five sixths of the upper ladder was never built.

**Shape 2 — R7 and R8 exist, are LIVE, and are genuinely unclimbed.** This required a new
control, and it is the instrument contribution of this review.

B ran the *negative* control (payload-reading null: "can a cheat pass?" — want NO). Nobody
ran the **positive** control: *can anything pass?* A tier on which no candidate has ever
scored above zero has never demonstrated that its grading predicate accepts a correct
answer. That is an unfalsifiable metric, and it is exactly the shape my lens exists to
catch. So I built the dual and ran it (E3): a candidate handed the harness's own
`ground_truth`.

```
tier  kind             n   omniscient   verdict
R0    linear         160       100.0%   LIVE
R1    quadratic      160       100.0%   LIVE
R2    sqrt           160       100.0%   LIVE
R3    rational       160       100.0%   LIVE
R5    invariant      160       100.0%   LIVE
R6    conjecture     160       100.0%   LIVE
R7    proof_repair   160       100.0%   LIVE
R8    lemma_select   160       100.0%   LIVE
PASS: every tier accepts its own ground truth.
```

**All eight tiers are live.** R7 and R8 are therefore *honestly hard*, not broken — a
correct answer would be recognised. Their 0% is a real capability gap. This is a clean
result and it converts "we don't know if R7/R8 mean anything" into "R7/R8 are unclimbed,"
which is P2 (exhaustive over the seeded probe set).

**Live methodological note, because it is more useful than the result:** my first run
reported **R0 BROKEN at 0.0%**. That was my bug, not R0's — the `linear` tier's answer
protocol is a singleton *list* and I returned the bare scalar. This is failure mode #4 in
`D:\Prometheus\harmonia\memory\retraction_registry.md` (specification mismatch:
apples-to-oranges), reproduced by me, inside the audit designed to catch instrument
defects, within ten minutes of writing it. Had I published the first run I would have
contributed a thirteenth registry entry. **A positive control needs its own positive
control**, i.e. it must be calibrated on tiers already known to be climbable (R0–R3) before
its verdict on unclimbed tiers is worth anything. Mine was, which is the only reason I
caught it.

**Shape 3 — R5, R7, R8 have no independent verification at all.** (E3) Grading the
reference `falsifier` across all eight tiers:

| tier | independently verified | dominant kill patterns |
|---|---|---|
| R0–R3 | 160/160 | — |
| **R5** | **0/160** | `wrong_or_missing_invariant`, **`verify:unknown_kind`** |
| R6 | 132/132 | — |
| **R7** | **0/160** | `failing_step_not_located`, **`verify:unknown_kind`** |
| **R8** | **0/160** | `no_lemma_selected`, **`verify:unknown_kind`** |

`verify:unknown_kind` fires on **160/160** probes at exactly R5, R7, R8. This is A's E3
correctness bug (`verify()` returns `valid=False` for unregistered kinds rather than
abstaining) hitting three of eight tiers at 100%. Two independent instances of the same
defect now: A found it at the selector, I find it at three ladder tiers. The
answer channel is honest there; the *verification* channel is structurally absent.

Full 8-tier staircase, never published before (E3) — the reference table in
`MEASUREMENT_FLEET_2026-06-27.md` reports six tiers and omits R7/R8:

| baseline | R0 | R1 | R2 | R3 | R5 | R6 | R7 | R8 | overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| template | 25.0 | 0.0 | 0.0 | 0.0 | 0.0 | 42.5 | 0.0 | 0.0 | 8.4 |
| procedural | 100.0 | 100.0 | 1.9 | 0.0 | 0.0 | 72.5 | 0.0 | 0.0 | 34.3 |
| careful | 100.0 | 100.0 | 100.0 | 100.0 | 0.0 | 72.5 | 0.0 | 0.0 | 59.1 |
| falsifier | 100.0 | 100.0 | 100.0 | 100.0 | 0.0 | 100.0 | 0.0 | 0.0 | 62.5 |

R0–R3 reproduce B's replication exactly. Note the shape: the published "clean capability
staircase" is a staircase over the **six tiers where something moves**, and the top
baseline is at 0% on three of eight.

---

## 5. Slice 2 — measuring the decay

### 5.1 The half-life is not measurable, and that is the finding

I set out to compute a half-life and could not, for a reason that is itself the result:
**promotion timestamps do not exist.** Techne's M0.5 audit established it at code level
(E1, `D:\Prometheus\roles\Techne\M05_PROMOTION_REPLAY_FINDINGS_2026-06-23.md` §2b): the
promotion decision was never stamped onto the durable record; legacy records carry
`training_weight = None`; the historical count is re-derivable only by replaying a formula
that has since been retuned. You cannot compute a decay rate over events with no birth
date.

So a "Prometheus result half-life" would be a manufactured number, and I decline to
manufacture it. What the data *does* support is a sharper model.

**Where latency is derivable at all, it is approximately zero.** The KillVector rank-1
claim was measured and downgraded **on the same day** (2026-05-27). The legality
over-refusal claim was retracted and un-retracted **on the same day** (2026-05-30). The
sigma-kernel cross-family signature died the moment corpus coverage extended. B's R6 leak
took fifteen minutes against a six-week-old instrument. My own R0 "BROKEN" verdict died in
ten minutes.

> **Results do not decay with time. They decay on contact.** Half-life is the wrong model —
> it implies exponential decay in age. The observed process is a step function triggered
> by first adversarial contact. Old untouched results look permanent for exactly the same
> reason unopened boxes look full.

The operational consequence: **"how long has this held up?" is not evidence of anything.**
The only meaningful durability statistic is *survival conditional on contact* — and the
program does not record contact events, so that denominator does not exist either. B
reports the numerator informally (2 passes, 2 breaks; Tier 3 "2-for-2 broken when
contacted"). A contact ledger would cost less than any instrument in this repo.

**Registry self-audit (E3):** `D:\Prometheus\harmonia\memory\retraction_registry.md`
contains **12** entries; its own footer claims **10**. The register that records the
program's decay has itself decayed by 20%, via exactly the *denominator drift* failure
primitive I nominated in June (cardinality asserted without a validator). It has a
validator — `harmonia/memory/diagnostics/validate_retraction_registry.py` — which
evidently does not check the count it fixed an off-by-one in. Recommend: add the count
assertion. Cheap, and the file is doctrine.

### 5.2 The decay taxonomy

All 12 registry entries, classified by *what parameter moved*:

| decay class | n | entries | what retuned |
|---|---:|---|---|
| **Null-relative** | 4 | moment hierarchy; spectral tail; NF backbone; (partly) Megethos | a better null was specified |
| **Corpus-relative** | 2 | sigma-kernel OBSTRUCTION_SHAPE; loose sister | coverage extended into the claimed region |
| **Instrument-relative** | 2 | Geometry-1 tensor rank (SVT on ordinal MNAR); KillVector rank-1 (11 of 12 coordinates never populated) | the instrument's own assumptions were checked |
| **Threshold/formula-relative** | 2 | Zoo (Tier-3 bar); **the 2,351 → 0 promotion collapse** | a number was retuned |
| **Specification-relative** | 1 | Zaremba A-spectrum | configs were matched |
| **Sampling-relative** | 1 | legality over-refusal (±0.12 at n=40) | n changed — *and the retraction itself decayed* |
| **Frame-relative** | 1 | 5-axis phoneme framework | classification-by-definition, never measurement |
| **P0 / never contingent** | 1 | **F043** | nothing — it was an algebraic identity misread as an empirical anticorrelation |

**Every decayed class shares one property: the claim was defined relative to a parameter
living outside the claim.** Null, corpus, threshold, formula, instrument, n, frame. That
is not eleven failure modes; it is one, with seven parameters. And it is the mechanical
criterion of §3 restated from the data rather than from theory — which is the only reason
I trust it.

F043 is the instructive exception in the other direction. It never decayed because it was
never contingent — and it was also never a discovery. **It survives at P0 and informs
nothing.** Its value is entirely pedagogical (the Pattern-30 anchor). Any permanence
program that counts F043 as a win has already gone wrong.

**Tensor re-audit datum (E1, memory `project_reaudit_20260418`):** 28 cells re-audited →
12 promote / 7 demote / 9 retain. A **25% demotion rate on first systematic re-contact**,
consistent with the step-function model. Note also that one of the 12 promotions (F043)
was itself retracted the following day — so the re-audit's own output decayed on contact
within 24 hours.

---

## 6. Permanence census

For each live component: what survives a full retune of every threshold in the program?

| component | tier | survives a full retune? |
|---|---|---|
| **a3 product-measure theorem** + certificate taxonomy (`D:\Prometheus\harmonia\primitives\lattice_void_miner.py`) | **P1** | **Yes.** Proof-backed, no null, no threshold. Completeness now corroborated over 355,216 cells (§2.3) |
| Calibration anchor — Mazur 3,824,372 @ 100.000%, modularity, Hasse, parity | **P1** | **Yes** — but these are *rediscoveries of proven theorems*. Permanent and not discoveries. Surveyor's pins, per the Charter |
| a3 exhaustive census — "3,456 cells, 250 exact voids, 0 novel identities" | **P2** | **Yes, if the catalog is named in the statement.** Currently it usually is not |
| a3 void *inventory* — the individual 250 | **P3** | **No.** 209/250 are `SELECTION_ARTIFACT` by its own closure-stress; they break under honest catalog extension |
| EC rich diagonal — "0 novel within-object laws in class H over catalog C" | **P2** | **Yes, as stated with (H, C).** As "0 novel laws," no |
| `torsion \| ∏c_p` (1000/1000, perm-null 0/200) | **P3** | **No.** Catalog conductor floor 39; the canonical counterexample 11a3 sits at conductor 11, below the floor. Documented as such |
| Ladder **chance floors** (B, this session) | **P2** | **Yes** — exact computations over a seeded probe set |
| Ladder **leakage verdicts** (R6 LEAKS, 7 CLEAN) | **P2** | **Yes** — exhaustive over the probe set; I reproduced them independently |
| Ladder **liveness verdicts** (8/8 LIVE, §4.3) | **P2** | **Yes**, same reason |
| `genuine_routing = false` (Apollo, gen 800) | **P2** | **Yes** — finite check against a fixed battery |
| Apollo canary chance floors (0.14 / 0.20) | **P2** | **Yes** |
| Reproducibility of the published staircase | **P2** | **Yes**, given frozen seed + code. Genuinely valuable and rare |
| **M0's "0% type-II"** | **P4 — already decayed** | **No.** A's E3 finding: `verify()` returns `valid=False` for unregistered kinds rather than abstaining, so 0/18 is an artifact of the harness hand-routing charitably; strict type-II up to 5/18. B's §3 leans on this number; it does not hold as stated |
| Coverage diagnostic "25% (4/16)" | **P3** (structure P2) | **Number no** (hand-curated list, A says so); **structure yes** (perfect in-class recall / zero out-of-class) |
| `costume_check` | **P3** | No — threshold-relative, though hardened by two falsification-and-repair cycles |
| Apollo `max_acc = 0.833` | **P3/P4** | **No.** Metric-relative — the 0.558 predecessor was diagnosed as substantially a *metric artifact*, and `best_acc` had to be replaced by `max_acc` mid-arc |
| Published R6 staircase column | **P4 — decayed** | **No.** Payload leak; a 3-line answer-key reader ties the top baseline |
| Icarus typed corpus (8 objects, 1 surviving) | **P3** | No |
| "2,351 discoveries" | **P3 — fully decayed to 0** | **No.** The canonical case |
| The retraction registry itself | **P2-ish** | Mostly — a record of kills outlives the kills. But it miscounts itself (§5.1) |

**Census result: 2 components at P1, both of which are either a single theorem or
rediscoveries of other people's theorems. Nothing else in the program is
retune-independent except by naming its domain — and the P2 rows are almost all
diagnostics built in the last twenty-four hours.**

That is the finding, and it reframes spending. The program's P3 inventory is large and its
P1 inventory is one item. But **the P2 column is nearly free and the program has been
leaving it on the floor**: chance floors, leakage controls, liveness controls, exhaustive
class censuses, guard-partition checks. Every one is cheap, every one is permanent, and
five of the nine P2 rows above did not exist yesterday. The cheapest available upgrade to
the program's permanence is not more proofs — it is **restating existing exhaustive
results with their domain inside the claim**, which costs a sentence per result and
converts rentals into holdings retroactively.

---

## 7. Weaknesses of this review

### 7.1 Where the external adversary broke me

I gave gemini-3.6-flash (independent family, free tier) my four certificate proofs and my
central logic claim as a hostile referee. It confirmed CLAIM 1–4 and **called my logic
claim UNSOUND**, correctly, on two counts:

1. **I wrote "decidable class H" where I needed "finite class H."** Universal
   quantification over an infinite *decidable* set is not decidable — element-wise
   decidability is not uniform decidability. a3 and the EC diagonal work because their
   classes are genuinely **finite** (3,456 and 1,728 cells), not merely decidable. §3's P2
   tier and §4.1 are written with `finite` throughout because of this correction. My first
   draft would have overclaimed the method's scope to any decidable grammar, which is
   exactly the "aspirational scope" failure primitive (#3 in the registry).
2. **"Undecidable" was the wrong word for terrain exhaustion.** The correct
   characterisation is *not finitely certifiable* / unfalsifiable — a quantifier-complexity
   and empirical-underdetermination claim, not a Turing-undecidability result. I have used
   "not finitely certifiable" in §4.1.

It also landed a hit I did not expect: **"true on C" ≠ "law"** — finite data fit is
trivial. That is independently rediscovering a3's own `SELECTION_ARTIFACT` 209/250, from
first principles, by a model that had never seen the corpus. I treat that as corroboration
of §2.4's central caution rather than as a new objection.

And its closing verdict on my conclusion — *"trivially true by basic epistemology, but
your formal argument was computationally illiterate"* — is half right and worth recording.
The class-relative-exhaustion conclusion **is** old (it is the problem of induction). The
contribution is not the epistemology; it is the operational claim that Prometheus has been
spending as though B1 were reachable, and the P2 restatement that makes the same work
permanent. I have tried not to dress a known truth as a discovery.

### 7.2 The failure mode of this lens, named

**A permanence lens over-values what can be formalized and quietly discards what cannot.**
"If I can't prove it, it doesn't count" is its own monoculture — and it is the *same*
monoculture A diagnosed in my void-miner three months ago, one altitude up. I would be
re-committing my own documented error in a new coordinate system.

Where this actually bit, concretely:

- **The failure atlas would score terribly on my ladder and should not.** FP-001…FP-004,
  the kill geometry, the "10 negative dimensions" — none is P1 or P2. They are pattern
  language, and pattern language is what actually transfers between agents. FP-003
  (`expressiveness_ceiling`) let A recognise Apollo's stall and the void-miner's stall as
  *the same thing*. No theorem did that. If the program optimised my census, it would
  delete the atlas, and the atlas is one of the few things here that has demonstrably
  moved another agent's work.
- **I nearly graded Apollo's whole arc as P3 rubble.** The type-inhabitation argument at
  0.558 is real reasoning that produced a real capability, and it lives in an
  unformalizable substrate. My lens can score its *conclusion* but not its *value*.
- **I recorded a negative result for my own method (§4.2) and the lens has no way to
  reward that.** A permanence census counts holdings; it cannot count "I tried the proof
  and it correctly failed," which is exactly the information the program needs most.

**Guard I applied:** I did not recommend retiring anything on permanence grounds, and §6's
recommendation is *restate*, not *delete*. Permanence is a property worth increasing where
it is cheap — it is not a criterion for what to keep.

### 7.3 Other limits

- **I did not re-run M0, the coverage sweep, or any Apollo evolutionary loop** (the last
  by constraint). M0's numbers are taken from A; the coverage 25% from A's own hand-curated
  table, which A flags as illustrative.
- **The completeness brute-force is bounded** — 12-integer universe, `|A|,|B| ≤ 3`. It is
  exhaustive over that domain, not over ℤ. §2.3 states this.
- **Single author, single family, mostly.** The one independent check is gemini's, it is
  one model on one prompt, and it is a free-tier model that was confidently wrong about
  nothing I could detect but had no ability to execute anything. Its confirmations are
  weaker evidence than its refutation.
- **My decay taxonomy classifies 12 entries by reading their own kill-mechanism prose.**
  The classes are mine; the mechanisms are the original authors'. A different reader might
  merge "frame-relative" into "instrument-relative" and I would not fight hard.
- **I recommend; James decides.** Nothing here retracts or demotes anything.

---

## 8. Recommendations, in cost order

1. **Restate existing exhaustive results with their domain in the claim.** Free. Converts
   a3's census, the EC diagonal, the chance floors, the leakage/liveness verdicts and
   `genuine_routing` from P3 phrasing to P2 holdings. Highest permanence-per-hour available.
2. **Adopt the liveness control as a standing gate**, paired with B's leakage control. They
   are duals and neither is sufficient alone: leakage asks *can a cheat pass* (want NO),
   liveness asks *can an oracle pass* (want YES). A metric with no positive control is
   unfalsifiable in the flattering direction. **Shipped this session** (per
   `feedback_validators_ship_with_docs`):
   `D:\Prometheus\harmonia\diagnostics\ladder_liveness_audit.py` — 8/8 LIVE, and
   `--test` runs 2 regressions including the R0 container bug that the control's own
   first version produced. Untracked on `main`; not committed (harness rule).
3. **Add a contact ledger.** Record, per artifact, whether it has taken adversarial contact
   and whether it survived. Cheaper than any instrument here and it supplies the missing
   denominator for every durability claim the program makes.
4. **Fix `verify()` to abstain (`valid=None`) on unregistered kinds** — A's prescription.
   Independent second instance found here: it fires at 160/160 on R5, R7, R8.
5. **Add the count assertion to the retraction-registry validator.** It is off by 2.
6. **Stop asking B1.** Not a task — a standing correction. No instrument can ever answer
   it, so a result phrased against it is unfalsifiable in one direction and permanently
   contingent in the other.

---

---

## 9. Reconciliation with James's rulings (added after drafting)

The four rulings in `D:\Prometheus\pivot\STRATEGY_2026-08-12_resumption_and_roadmap.md`
landed while this was being written. They are constraints, not proposals. Checking my
review against them, one recommendation needed a guard and one finding turns out to be
load-bearing for the roadmap's central instrument.

**R1 — math is the calibration standard, because mathematics is discrete and can be scored
without argument.** My permanence ladder supplies the mechanism behind that intuition, and
I had not connected them: **P1 and P2 are only reachable where the domain is finite,
discrete and exactly evaluable.** §2.4's preconditions (finite class, exact evaluation,
bounded sufficient statistic) are a restatement of "no ambiguity in mathematics" in
instrument terms. That is *why* math is the calibration standard — it is the only landscape
where permanence is affordable. On the reasoning landscape almost everything is P3 by
construction, because the scoring involves a threshold someone chose.

**R2 — the ladder needs reassessment before Apollo's re-aim.** §4.3 is a direct input and
it is executed rather than argued: **R4 and R9–R12 have no generators** — ladder v0.2 should
begin from the eight tiers that exist, not the thirteen the design document names. R7/R8 are
LIVE and genuinely unclimbed (so they are real frontier, worth aiming at). R5/R7/R8 have
zero independent verification at 160/160. The v0.1 admission that "R3–R5 have no sharp
tests" is milder than the measured situation.

**R3 — do NOT narrow; the operating model is an archive with a coverage measure, not a
funnel.** Explicit guard, because a permanence census is *exactly* the kind of document
that gets misread as a retirement ranking: **§6 is not a kill list.** Its recommendation is
*restate*, not *delete*, and §7.2 argues at length that applying my own criterion as a
retention test would delete the failure atlas and would be wrong. Constructively: **the
P0–P4 tier is a candidate descriptor axis for the MAP-Elites archive** — "how retune-proof
is this niche's output" is orthogonal to the lane axis and cheap to compute.

**R4 / the coverage measure — and this is the load-bearing one.** The roadmap asks for a
coverage measure that "distinguishes an *unexplored* niche from an *exhausted* one." §4.1
is a hard design constraint on that instrument, established rather than proposed:

> **Void and gap are not symmetric. "Unexplored" is certifiable; "exhausted" is not — only
> "exhausted within class H" is.** A coverage measure that reports exhaustion without
> naming the class will claim something no instrument can support, and it will do so in
> the program's most load-bearing new instrument.

The fix is free at design time and expensive later: **make the coverage measure
class-indexed from the start.** Every "exhausted" cell should carry the H it was exhausted
within. That is the P2 restatement (§3) applied to the archive, and it is the single most
useful thing in this review for the live roadmap.

**The artifact guard — "every pass over a lane emits a runnable committed artifact, never a
paragraph; a fifth reassessment document would be the failure mode, not the fix."** This
lands on me directly and I should answer it rather than dodge. This session emitted: a
runnable committed artifact (`D:\Prometheus\harmonia\diagnostics\ladder_liveness_audit.py`,
8/8 LIVE, `--test` 2/2, with its own historical bug pinned as a regression); three coverage
numbers (355,216-cell certificate completeness; the full 8-tier staircase; Apollo canary
reachability 50/50); and one recorded death (A's closure proposal, executed in Phase 2).
**But the document is long, and under this guard length is a liability, not thoroughness.**
The honest accounting: the artifacts are the deliverable and this prose is commentary on
them. If only one thing survives this session it should be the liveness audit, not this file.

---

*The honest number of novel discoveries is still zero. The honest number of permanent
results is one theorem plus a handful of exhaustive censuses, most of which were built in
the last day. But permanence turned out to be cheap where the program never looked for it —
not in proving more, in saying what you already proved with its domain attached.*

— Harmonia D, 2026-08-12

---
---

# Phase 2 — attacking `REVIEW_20260812_syntactic_router.md` (Harmonia A)

Read after Phase 1 was written, per the assignment. A's central claim: every measured
wall sits in a **syntactic router** in front of a working semantic engine; the remedy is a
claim→z3/sympy **translator** with kind-routing deleted; and novelty should be re-posed as
**not-in-deductive-closure** rather than shape-difference.

I attacked the closure proposal, because it is in my lane and A never executed it — A says
so explicitly in its own §8 ("§4's Q1 argument is philosophical, not executed. It has no
E-level. It is the weakest load-bearing claim here"). **A called its own shot. The kill
below lands exactly where A predicted, which is a credit to A's calibration, not a
surprise.**

## P2.1 The kill: closure-novelty is a timeout detector (E3)

A writes that "not in the deductive closure of the current corpus" is "**decidable on the
fragments z3 handles**." That qualifier is true and it is *fatal*, for a reason the
qualifier conceals. I ran `entails` (`D:\Prometheus\harmonia\experiments\z3_backend.py:130`
— the exact primitive A nominates) across a spread of claims from trivial to open, against
a small true-arithmetic corpus in the spirit of the 18 M0 claims.

I deliberately **did not open `bprime_holdout.json`.** A pre-registered it to be graded
once; spending it to test A's own proposal would burn the only held-out set the program has.

```
claim                                        vs CORPUS   vs TRUE   novelty verdict
n^2 >= 0                (textbook trivial)       valid     valid   not novel   (truth: not novel)
n^2 + n is even         (verbatim in corpus)     valid     valid   not novel   (truth: not novel)
n >= 0 -> 2n >= n       (linear, trivial)        valid     valid   not novel   (truth: not novel)
(a+b)^2 = a^2+2ab+b^2   (ring identity)          valid     valid   not novel   (truth: not novel)
n > 0 -> n^3 >= n       (nonlinear, easy-ish)    valid     valid   not novel   (truth: not novel)
FERMAT  a^n+b^n != c^n  (genuinely hard)       unknown   unknown   NOVEL       (truth: novel)
[encoding-flawed row, see P2.3]                unknown     valid   NOVEL       (truth: novel)
n^2 + n is ODD          (FALSE)                invalid   invalid   NOVEL       (truth: NOT novel)
a*b even -> both even   (FALSE, cex (2,3))     invalid   invalid   NOVEL       (truth: NOT novel)

as a novelty detector: TP=2  FP=2  FN=0  TN=5
corpus effect: 1 of 9 verdicts changed when the corpus was added
```

Two independent failures, either one sufficient:

**(1) Every false statement scores as maximally novel.** `entails` returns `invalid` for a
falsehood — correctly, since a false claim is certainly not entailed. Under A's definition
`not-in-closure ⟹ novel`, *"n² + n is odd"* is novel. A novelty meter whose easiest
high-score is to assert something false is worse than the shape-keyed meter A is replacing:
shape-keying inflates with *distinct* junk (2,846 cells, zero lift); closure-keying
inflates with *wrong* junk, and wrong junk is cheaper to generate than distinct junk.

**(2) The corpus is inert.** Only 1 of 9 verdicts moved when the corpus was added — and
that one moved the wrong way (§P2.3). z3 decides **modulo its built-in theory of
integers**, not modulo the supplied premises. So the thing being computed is not "the
deductive closure of the Prometheus corpus" at all; it is "the consequences of elementary
arithmetic," which already contains essentially every elementary number-theoretic truth the
program might state. The corpus — the object whose closure A wants to measure novelty
against — contributes nothing to the verdict.

**Therefore the meter reduces to:**

> **novel = {false statements} ∪ {claims the solver could not decide in the budget}.**

The `unknown` branch is not a bug and cannot be engineered away — the backend's own
docstring says it: *"nonlinear/quantified arithmetic is undecidable in general,"* and the
conjecture registry already carries a tier literally named `z3_unknown_expected`. **The
codebase knew this before A proposed it.**

And the consequence generalizes past z3:

> **Decidability and novelty are anti-correlated by construction. In the fragment where
> the closure test terminates, everything true is already in the closure, so nothing is
> ever novel. Outside that fragment, the test returns `unknown`. The decidable region and
> the interesting region are disjoint.**

This is the *same asymmetry* Phase 1 §4.1 found for B1/B2, in a new coordinate system.
"Not in the closure" is the direction with no finite certificate — exactly like "the
terrain is exhausted." A has re-posed Q1 from one unfalsifiable form into another. It is
better-defined and no more answerable.

**Verdict: A's §3(b) and §4 fall together, as the assignment anticipated they might.**
Q1-as-derivability is *well-posed* — I grant A that much against A's own earlier framing —
but it is **not buildable as a novelty meter**, and "collapse Q1 into the A fallback"
(A's own alternative in §4) is the surviving option.

## P2.2 What survives A's review

I attacked the rest and could not break it:

- **§1, the router pattern — SURVIVES, and I add a third independent instance.** A's null
  ("all software dispatches on type tags") fails for the reason A gives: in every case the
  semantic check *was built and left out of the gate*. Phase 1 §4.3 supplies a new datum A
  did not have — `verify:unknown_kind` fires on **160/160 probes at R5, R7 and R8** (E3),
  three of eight ladder tiers with *zero* independent verification. A found the bug at the
  selector; I find it at 100% coverage on three tiers of the flagship instrument.
- **§2, the M0 type-II correctness bug — SURVIVES and is load-bearing.** My Phase 1 §6
  census independently marks M0's "0% type-II" as already-decayed on A's evidence. **Live
  three-way inconsistency James should see:** B's `REVIEW_20260812_program_and_instrument_audit.md`
  §1 lists "0% type-II on M0" as a Tier-2 healthy asset and calls it "the load-bearing
  reason the audit fallback is solid." A killed that number the same day. **B's §1 does not
  hold as written**, and B's §3 recommendation partly rests on it.
- **§3(a), "widen the shape inventory is Goodhartable" — SURVIVES.** Correct, and a good
  self-catch.
- **§6, the live demonstration — SURVIVES and is the best evidence in A's document**, as A
  says. I reproduced the same class of error myself this session (Phase 1 §4.3, the R0
  container bug), independently, inside an audit designed to catch instrument defects. Two
  agents reproducing the diagnosed failure while holding the diagnosis is stronger evidence
  for §1 than either instance alone.
- **§5, "the real asset is a failure atlas" — SURVIVES, and I reached it from the opposite
  direction.** My Phase 1 §7.2 arrives there as a *warning against my own lens*: the atlas
  scores terribly on my permanence ladder and must be kept anyway. A argues the atlas is
  the deliverable; I argue my own criterion would delete it and is therefore wrong to use
  as a retention criterion. **Convergence from opposed premises is the strongest signal in
  this whole panel**, and neither of us engineered it.

## P2.3 Where I got it wrong in the attack

Falsification-first applies to my kill too.

- **My Goldbach row is mis-encoded.** I wrote "∃a,b>1 with a+b=n" — no primality
  condition — which is trivially true, not Goldbach. Primality is not expressible as a z3
  universal (the conjecture registry says so explicitly and uses a `refute_witness` tier
  for it). That row does **not** test an open problem and I have marked it as flawed rather
  than deleting it, because it accidentally shows something else worth recording: the
  verdict flipped from `valid` (empty premise) to `unknown` (with two *true and logically
  irrelevant* premises added). **Adding true premises made the meter worse.** A novelty
  metric that is non-monotonic under irrelevant true additions is unusable — but I observed
  this once, on my flawed row, and I am flagging it as *suggestive, not established*.
- **The Fermat row is doing less work than it looks.** `unknown` there is a timeout, and
  timeouts are budget-dependent. The kill does not rest on it: rows 8–9 (false ⟹ novel)
  are budget-independent and sufficient on their own.
- **Nine hand-picked claims are not a claim population.** The FP rate of 2/4 is
  illustrative, not a measured base rate — the same criticism I level at A's hand-curated
  16-law table in Phase 1 §4.1. The *structure* (false ⟹ novel; corpus inert) is what
  survives, not the ratio.

## P2.4 Where A and I genuinely disagree

Not converging for the sake of it. Two real disagreements:

**1. A translator does not escape class-relativity; it is a bigger class.** A's §3(a)
correctly identifies that adding kinds is Goodhartable — a meter you tick by typing. I
claim the proposed remedy is the *same move one level up*. The target language is itself a
hypothesis class: z3's decidable fragments have a coverage ceiling exactly as the
void-miner's four relations do, and P2.1 shows where that ceiling sits — at precisely the
boundary where claims stop being trivial. Deleting kind-routing genuinely improves the
instrument. It does not change what *kind* of statement the instrument can produce, which
by Phase 1 §4.1 is always class-relative. **A treats the translator as a category change; I
read it as a scale change.** Worth building anyway — just not as an answer to Q1.

**2. A ranks "the program cannot route to its semantic engine" as the wall. I rank "the
program cannot state a permanent result" as the wall.** These are compatible diagnoses with
incompatible next moves. A's implies *build the translator*. Mine implies *restate what you
already exhaustively computed with its domain attached* — free, retroactive, and it
converts the a3 census, the chance floors, the leakage/liveness verdicts and
`genuine_routing` into holdings today. If A is right, the program needs weeks of building
before the next real measurement. If I am right, a substantial fraction of the program's
existing output is already permanent and merely mis-phrased. **These make different
predictions and both are cheap; run mine first because it costs a day and cannot fail
destructively.**

Where I will concede in advance: if the translator ships and B′ is passed by it and *not*
by a lookup table, A's §1 is vindicated far beyond my objection, and class-relativity
becomes a pedantic footnote rather than a live constraint. That is A's pre-registered test
and it is a good one.

---

*Two reviews, one panel, one genuine kill in each direction. A's closure proposal does not
survive execution; A predicted that it might not. My permanence ladder does not survive its
own application to the failure atlas; I said so before reading A. The convergence neither
of us aimed at — that the atlas is the asset — is the finding I would bet on.*

— Harmonia D, Phase 2, 2026-08-12
