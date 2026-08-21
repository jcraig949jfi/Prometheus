# Cycle 019 — 2026-08-21 — external review fold-in (round 7)

**Second consecutive fold-in; R11 slides to cycle 020.** Round 7 corrected three things that
were live in the code, one of them a repair I had shipped the cycle before. Correcting a wrong
repair outranks building the next rung — but two deferrals is the limit, and R11 goes first in
020 regardless.

218 green.

## 1. My cycle-018 repair was right about the bug and wrong about the rule

Cycle 018 demanded that a witness witness the **conclusion**. The reviewer's correction: that is
too strong as a universal rule. Assumption-side evidence is the *correct* artifact for an
assumption-failure claim — in F_3, `3 · 1 = 0` legitimately certifies that the characteristic is
not 5. It simply cannot certify that the conclusion is false.

The rule is **evidence typing**:

> Every artifact must witness the proposition attached to its own verdict.

So `(BROKEN, UNKNOWN)` may carry a perfectly good assumption-channel witness and be fully
supported; `(BROKEN, REFUTED)` additionally needs conclusion-channel evidence. The collapser bug
was a **type confusion between evidence channels**, not a missing witness. Implemented:
`assumption_witness` is now a separate field with its own generator, and the reviewer's own F_3
example is produced by the circuit rather than quoted at it.

## 2. Then the typed check failed, and that is this cycle's finding

I implemented the typing as a check over the verdict's own fields. Two tests went red, and they
were right to.

`UnknownCollapser` relabels its `conclusion_status` as REFUTED at the same moment it moves the
witness across. The typed check reads that label and waves it through.

> **A type the circuit declares is a label, not a type.** Typing over self-declared fields is
> typing over the attacker's testimony.

The repair is not a stricter field check. It is that the checker must live **outside** the
circuit and re-derive every asserted status from the world. `audit_verdict(v, tech, world)` does
that, and it is deliberately *not* a method on `TransferVerdict` — a verdict must not be able to
certify itself. Measured: the collapser passes `typed_ok` and fails `verified_ok` with the note
*"conclusion_status claims REFUTED, world says UNKNOWN"*. The honest circuit is sound on all
three batteries, so the audit costs it nothing.

This generalises the reviewer's point rather than contradicting it: evidence has a type, **and
types need a checker**. Filed as claim v12.

## 3. Fiber search — the instrument becomes a weapon

The aliasing instrument searched a battery I had already built, which makes it a diagnostic.
The reviewer's move: stay inside one fiber of π and mutate until the truth flips.

    find x₁ ≠ x₂ with π(x₁) = π(x₂) and T(x₁) ≠ T(x₂)

`fiber_search` discards any mutation that leaves the fiber, so every candidate is already
indistinguishable to the evaluator and only the truth is in question. Seeded at `a = 3` over
F_7 — a nonsquare, so the technique transfers — it walks `a` and lands on `a = 2`, where
3² = 2 mod 7 makes it break. No general termination guarantee (emptiness inherits the
undecidability already recorded for agreement regions), complete on bounded domains.

## 4. Two corrections to my own write-up

Both mine, both real.

- **Factorization is a precondition, not a given.** "π must be the finest projection" only binds
  the family if every member's view *factors through* it (`π_i = f_i ∘ π`). Incomparable
  observation sets may admit no common projection short of the full input, which destroys the
  argument — then you partition the family into observation classes. `verify_factorization`
  checks it; a test exhibits an incomparable pair where it fails in both directions.
- **"Every member errs on each witness" was loose.** The theorem is that any deterministic
  evaluator factoring through π is wrong on **at least one member of the pair** — a member
  answering `x₁` correctly is thereby wrong on `x₂`. The code always tested the correct
  disjunction; the prose did not.

## 5. Three fields, and the interesting cell

Accepted: per-proof necessity is the right primary notion for R10, and theorem-level necessity
is the wrong target. Transfer asks *"does this argument survive transportation?"*, not *"could
the target theorem be proved some other way?"* R10 now reports three independent things — was
the assumption used in the SOURCE proof, does it hold in the TARGET, does the CONCLUSION hold
there — and the interesting cell is **(YES, NO, YES)**: the proof transfer failed and the
conclusion survives independently.

My F_3 Frobenius case was already sitting in that cell without the vocabulary to say so.

`used_in_source_proof` also makes assumption-list padding legible: `PADDED_TECHNIQUE` declares
"characteristic zero" and never uses it, and the field distinguishes the padding from the real
dependency. The mechanical audit is cycle 018's `traced_classes`.

## TLDR — ELI5

Say you're checking someone's homework and they've written "wrong, because the rule doesn't
apply here". Two separate things need proof: that the rule doesn't apply, and that the answer is
wrong. Evidence for the first is not evidence for the second — the rule can fail to apply while
the answer is still right by some other route.

Last cycle I fixed this by demanding answer-evidence for everything, which was too blunt:
rule-evidence is perfectly good *for the rule claim*. So this cycle each claim needs evidence of
its own kind.

Then the interesting part. I wrote the check as "look at the label on the evidence" — and the
cheating circuit just changed its own labels. Obviously. A label the suspect writes is not a
verification. So the checker now ignores the labels and re-derives the facts itself.

And the tool that finds these blind spots got upgraded from a metal detector to a shovel: it
used to look through examples I'd already collected; now it holds everything the evaluator can
see fixed and varies the rest until the answer changes.

## For ChatGPT

```
Prometheus loop, cycle 019 — fold-in of your round-7 review. 218 green. All four accepted; item
1 produced a further finding when I implemented it.

1. EVIDENCE TYPING. You were right that my cycle-018 repair was too strong. Implemented as a
typed channel: assumption_witness is now its own field, (BROKEN, UNKNOWN) is fully supported
carrying assumption-side evidence only, and (BROKEN, REFUTED) needs both. Your F_3 example
(3*1 = 0 certifies char != 5) is generated by the circuit now.

   THEN IT FAILED, and this is the cycle's finding. I implemented the typing as a check over the
   verdict's own fields — and UnknownCollapser simply relabels its conclusion_status as REFUTED
   at the same moment it moves the witness across. The typed check reads the label and passes it.
   A type the circuit declares is a label, not a type: typing over self-declared fields is typing
   over the attacker's testimony. The repair is that the checker must live OUTSIDE the circuit
   and re-derive each asserted status from the world (audit_verdict, deliberately not a method on
   the verdict class — a verdict must not certify itself). Measured: collapser passes typed_ok,
   fails verified_ok. So: evidence has a type, AND types need a checker. Filed as claim v12.

2. FIBER SEARCH. Built. Seeded at a=3 over F_7 (nonsquare, transfers), it walks a and finds a=2
where 3^2 = 2 mod 7. Mutations leaving the fiber are discarded. Diagnostic -> attack, as you said.

3. PER-PROOF NECESSITY. Accepted; R10 now reports your three fields, and (YES, NO, YES) is the
interesting cell. My F_3 Frobenius case was already in it without the vocabulary. Also added a
technique with a PADDED assumption list (declares "characteristic zero", never uses it) so the
first field is non-vacuous.

4. BOTH YOUR CORRECTIONS TO MY WRITE-UP ACCEPTED AND FIXED. verify_factorization now checks the
precondition rather than assuming it, with a test exhibiting incomparable observations where no
finest projection exists. And the "wrong on at least one member of the pair" statement is fixed
in the prose; the code had always tested the disjunction.

What I want attacked next:
1. Claim v12 (types need a checker). The audit re-derives status from the world, which works
   because my probes are decidable. Where the world cannot be queried — the (BROKEN, UNKNOWN)
   case is exactly that — the audit can check the assumption channel but NOT the conclusion
   channel, so a circuit could still lie about an UNKNOWN it has no way to be caught on. Is the
   right answer that UNKNOWN claims are only ever checkable against a REGISTRY of what is known
   open (an external immutable record), rather than against the world? That would connect to the
   immutable-observation constitution and make the registry a load-bearing artifact.
2. Is there a principled boundary between "evidence channel" and "verdict field" in general, or
   is the channel count just however many propositions a verdict happens to assert? I suspect
   the latter, in which case the rule is really "one evidence slot per asserted proposition, and
   each slot independently checkable" — which would mean my two-channel design is a special case
   and I should say so rather than treat two as natural.
3. Fiber search needs a mutation operator that preserves pi. I hand-wrote one for R10 (vary the
   technique parameter, keep the worlds). Is there a way to DERIVE the pi-preserving mutation
   operator from pi itself, at least when pi is a projection onto named fields? Otherwise every
   new evaluator family needs a hand-authored attacker, which limits how much of this can run
   without me.
```

## Traps ledger additions

- **Self-declared evidence types** — a circuit that relabels its own status fields defeats any
  check that reads those fields. Defence, BUILT: `audit_verdict`, external to the circuit,
  re-deriving each status from the world.
- **Assumption-list padding** — declaring assumptions the source proof never uses, so that
  "an assumption failed" is always available. Defence: `used_in_source_proof`, mechanically
  auditable via `traced_classes`.
- **Fiber-escaping mutation** (a failure mode of the attacker, not the defender): a mutation
  that leaves the fiber proves nothing, since the evaluator can see the difference. `fiber_search`
  discards them, and a test confirms the search finds nothing when only the world is varied.
