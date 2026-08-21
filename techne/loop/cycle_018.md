# Cycle 018 — 2026-08-21 — external review fold-in (round 6)

**Not the scheduled R11 cycle.** James relayed round-6 review of cycle 017 mid-loop, and it
materially corrects the rung I had just built. Folding it in outranks moving on; R11 slides to
cycle 019. Three of the four items were accepted as-is, and the fourth (Lean tracing) was built
further than the reviewer's sketch because the toolchain permitted it.

208 green.

## 1. Claim v11 restated as evaluator aliasing — and turned into an instrument

The reviewer's formulation is strictly better than mine and, crucially, **provable rather than
measured**:

> Let an evaluator family `E_θ` observe only a projection `π(x)`. Then `π(x₁) = π(x₂)` implies
> `E_θ(x₁) = E_θ(x₂)` for all θ. If `Y(x₁) ≠ Y(x₂)`, no θ is correct on both.

Cycle 017 swept a dial and observed that no setting worked. That is an experiment about one
family on one battery. The aliasing form is an impossibility proof against the whole family,
and it yields an executable design rule: **find two probes in the same equivalence class under
everything the evaluator can see, with different correct verdicts.**

So it became `techne/ladder_circuits/aliasing.py` — `find_aliasing_witness`,
`family_cannot_be_correct` (the theorem), `verify_family_incapacity` (the measurement that must
agree with it). Then I retrofitted it to the earlier sightings, which is the real test of
whether the generalisation covers them or merely sounds like it does:

- **R6, search horizon.** Witness: a conjecture first failing at H+2 versus a true one — equal
  on n ≤ H, different truths. Every horizon in the family errs. This is *why* Euler's n²+n+41
  defeats a pre-fixed horizon.
- **R9, the deletion test.** Witness: the honest lemma versus the circular one, equal on
  (lemma_true, goal_proved, load_bearing). Cycle 016's finding re-derived from the general
  instrument instead of by hand.
- **R10, world features.** Cycle 017's sweep restated as an impossibility.

**One refinement the formulation needs.** Where family members differ in how much they observe
(a horizon-h searcher sees more as h grows), π must be the **finest** projection any member can
see; a witness under the finest kills every member, since each sees a coarsening. Recorded in
the module.

**And a correction to my own framing:** aliasing is not a fact about dials. R9's deletion-only
checker has no parameter at all and dies to the same argument. Calling it "instance-blind
parameter" pointed at the wrong feature of the situation. Ledger claim v11 rewritten as
**evaluator aliasing / observational non-identifiability**.

R3's capacity width is listed in the ledger as a fourth instance and is **not** retrofitted. It
is marked unverified rather than counted.

## 2. R10 gets a third verdict — (assumption status, conclusion status)

Accepted in full. A broken assumption does not entail a false conclusion; the F_3 Frobenius case
proved that last cycle. So the verdict splits, and `derive_verdict` is the only sanctioned
collapse: `(·, UNKNOWN) → UNVERIFIED`, never `BREAKS`.

Two techniques now carry conclusions that are genuinely **open over ℤ** — Artin's primitive-root
conjecture and the twin-prime conjecture — while their function-field proofs lean on the
constant field being *finite*, which ℤ does not supply. Both land in `(BROKEN, UNKNOWN)`:
a witnessed assumption violation with no verdict available.

`UnknownCollapser` is the new trap, and it is the one most likely to be committed in good faith:
identical to the honest circuit except that it reads a witnessed assumption violation as
evidence against the conclusion. It thereby manufactures a refutation of the twin-prime
conjecture — **and it passed cycle 017's artifact check**, because that check asked only whether the
`witness` field was populated — and the collapser populates it with a restatement of the
assumption violation, which witnesses nothing and cannot, since the conclusion is open.

**Repair, implemented this cycle:** `is_supported_strict` requires a BREAKS claim to carry
`conclusion_status == "REFUTED"`. A witness must witness the *conclusion*. It kills every
collapser claim and costs the honest circuit nothing (`unsupported_strict` = 0 on the decidable
battery).

Third rung to demand an abstention channel, after R3 and R6.

## 3. A sharper near-analogy — the break hidden in a residue class

The reviewer designed this one and it is better than my unit-count probe. Technique: *x² − a is
irreducible over the constant field*, assumption: *a is a nonsquare there*. At **fixed q = 7**,
varying only `a` flips the verdict — 3² = 2 mod 7, so `a = 2` breaks while `a = 3, 5` transfer.

Everything visible is held constant: same domain kind, same characteristic, same field size,
same unit group, same polynomial machinery. So the aliasing witness here is **strictly stronger
than cycle 017's**: the projection is the *entire* (source, target) pair — complete world
knowledge, not a feature subset — and it still fails. Nothing about the worlds can supply the
answer; the circuit is forced through technique → its own assumption → a target-world test.

The assumption is checked by a residue computation and the conclusion by sympy factorisation —
independent code paths, agreeing by mathematics rather than by construction.

## 4. Track 1 — mechanical assumption extraction from Lean (HITL #38, closed)

The reviewer's three layers, built. `#print axioms` really is too coarse: **measured**, a
theorem whose proof runs through a custom typeclass reports `[propext, Quot.sound]` and nothing
else.

- **Layer 1, kernel closure.** A Lean metaprogram walks the elaborated proof term's transitive
  constant closure. (`NameSet` is a `Std.TreeSet` in 4.30 with no `.fold` — took three attempts.)
- **Layer 2, structural assumptions.** Each dependency is classified CLASS / INSTANCE:c / CTOR /
  CONST. `tgt` reports `MyChar` + `instCharNat`; a theorem not using the class reports neither,
  so the tracer discriminates rather than always-firing. Constructors are filtered out of the
  instance list — `MyChar.mk` has the class as its type head and is not an instance.
- **Layer 3, necessity against a FROZEN term.** `check_frozen_term` re-elaborates *this exact
  proof term* against a modified context and never asks Lean to search again. The reviewer's
  warning is demonstrated in a test: `pm_double` is load-bearing for `by rw [pm_double]`, and
  a re-search with `omega` proves the same goal without it — same goal, opposite conclusions
  about necessity. Canon R9's non-unique-proof problem wearing R10 clothes.

`traced_classes()` gives an R10 circuit's declared assumption set something to be **audited
against**, which is what HITL #38 asked for.

**A gap I found in my own checker while building this:** `sorry` produces a Lean *warning*, not
an error, so `check_lean_source` classifies a sorry-contaminated proof as **PROVED**. Measured
and now under test. The axiom lane catches it (`sorryAx` in the dependency report), which is
precisely the job `#print axioms` is good for even though it is useless as an assumption tracer.

## TLDR — ELI5

Suppose you're grading translations between two languages, and your grading sheet only records
facts about the two *languages* — never about the sentence being translated. Now hand yourself
two sentences from the same language pair where one translates fine and one doesn't. Your sheet
says the same thing for both, so whatever rule you write on it, you get one wrong. Not because
the rule is badly tuned — because the sheet doesn't have a column for the thing that matters.
That's provable, and finding two such sentences is now a five-line function.

Second: if a translation method relies on something the new language lacks, that doesn't mean
the translated sentence is *false*. It means you don't know. Saying "false" there is manufacturing
a result — and my scoring from last cycle would have applauded it, because it filled in the
"evidence" box with a note about the missing thing rather than actual evidence.

Third: we can now ask Lean itself what a proof leaned on, instead of taking the circuit's word
for it. Along the way I found that my own checker calls a proof "proved" when it contains the
word `sorry` — a placeholder meaning "I gave up here". The axiom audit catches it; the verdict
alone doesn't.

## For ChatGPT

```
Prometheus loop, cycle 018 — fold-in of your round-6 review. All four items accepted; three
built as specified, the Lean one built past the sketch. 208 tests green.

1. ALIASING. Your formulation replaced mine in the ledger, because it converts a measurement
into an impossibility proof. Built as a general instrument (find_aliasing_witness /
family_cannot_be_correct / verify_family_incapacity) and RETROFITTED to R6 (horizon), R9
(deletion test) and R10 (world features). All three produce witnesses; every family member errs
on each. One refinement I had to add: where members differ in how much they observe, pi must be
the FINEST projection any member can see, since each member's view is then a coarsening.
Also a correction to my own framing: aliasing is not about dials. R9's deletion-only checker
has NO parameter and dies to the same argument, so "instance-blind parameter" named the wrong
feature. R3 capacity width is listed but NOT retrofitted; marked unverified rather than counted.

2. THIRD VERDICT. Built as (assumption_status, conclusion_status) with derive_verdict as the
only sanctioned collapse; (BROKEN, UNKNOWN) -> UNVERIFIED, never BREAKS. Two techniques now
carry conclusions open over Z (Artin primitive root, twin primes) whose function-field proofs
need the constant field FINITE. The UnknownCollapser trap manufactures a refutation of the twin
prime conjecture — and it PASSES my cycle-017 artifact check, because it fills the witness field
with a restatement of the assumption violation. So the artifact check needed strengthening too, and
I built the repair: is_supported_strict requires conclusion_status == REFUTED. A witness must
witness the CONCLUSION, not the assumption.

3. YOUR NEAR-ANALOGY. Built at fixed q=7, varying a: 3^2 = 2 mod 7, so a=2 breaks and a=3,5
transfer. It gives a strictly stronger aliasing witness than cycle 017's — the projection is the
ENTIRE (source, target) pair, complete world knowledge, and it still fails.

4. LEAN TRACING. Your #print axioms critique is confirmed by measurement: a theorem proving
through a custom typeclass reports [propext, Quot.sound] and nothing else. Built all three
layers: constant-closure traversal via a Lean metaprogram, CLASS/INSTANCE/CTOR classification
(constructors filtered — MyChar.mk has the class as its type head and is not an instance), and
check_frozen_term for necessity. Your freeze warning is now a test: pm_double is load-bearing
for `by rw [pm_double]`, and re-searching with omega proves the same goal without it.

Found in passing: `sorry` is a Lean WARNING not an error, so my checker classified a
sorry-contaminated proof as PROVED. The axiom lane catches it (sorryAx). Under test now.

What I want attacked next:
1. My witness-must-witness-the-conclusion repair. Is "the witness must be a counterexample to
   the conclusion, not evidence about the assumption" the right general form of the artifact
   requirement, or is there a case where assumption-side evidence legitimately IS the artifact?
   Canon R10's own wording ("the broken assumption named") is silent on what the naming must be
   backed by, which is how the collapser got through.
2. The aliasing instrument currently searches pairs from a battery I supply. That makes it a
   diagnostic, not a generator. Is there a principled way to SYNTHESISE an aliasing witness
   given only pi and a truth oracle — i.e. to attack an evaluator family without already having
   a battery that happens to contain the pair? That would turn it from an audit into a weapon.
3. Layer 3 necessity is per-proof-term by construction. That means an assumption can be
   load-bearing for the proof I have and dispensable for the theorem. Is per-proof necessity the
   right notion for R10 at all, or does transfer entitlement need per-THEOREM necessity — which
   is undecidable in general and would push R10 back toward "unverified" much more often?
4. Anything I have mis-stated about your position in items 1-4 above.
```

## Traps ledger additions

- **UNKNOWN collapsed into REFUTED** — a witnessed assumption violation read as evidence against
  the conclusion. Passed the artifact check that only asked whether a witness field is populated.
  Defence, BUILT: `is_supported_strict` requires the conclusion to have been refuted.
- **Declared-assumption gaming** (now defensible, was flagged in cycle 017): a circuit that
  declares its own assumptions can declare the convenient ones. `traced_classes()` audits the
  declaration against the proof term's dependency closure.
- **`sorry` contamination invisible to the verdict lane** — Lean warns rather than errors, so a
  compile-based checker reports PROVED. Defence: the axiom lane (`sorryAx`).
- **Necessity by re-search** — ablating an assumption and re-proving finds a different proof and
  wrongly reports the assumption unused. Defence: freeze the proof term.
