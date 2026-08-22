## ⚠️ HITL #78 — 632 rows, eight cycles unruled

330 when found (cycle 025) → 369 → 400 → 446 → 491 → 530 → 572 → **632, 0 accepted, 100% drop**.

**New this cycle:** the campaign has begun writing **rep-2** rows (7 of 632) — the contamination
screen. The shipping loader accepts neither rep. Still unruled, still unpatched by me.

# Cycle 032 — external review, round 8

**380 green.** Read-only throughout. This replaces the planned normal-form cycle, because item 1
lands directly on the soft spot I had declared for it.

## Item 1 — merge/split exhaust classification error, not representation adequacy

My cycle-022 duality was correct and **scoped too widely**. It exhausts the ways a projection can
be wrong *against a fixed target*. It says nothing about a projection that induces exactly the
right partition and has destroyed what a **later** task needs.

Measured on the integers 2..41:

```
primality projection vs target "is it prime"          VI = 0.0000   no merge, no split
the SAME projection vs target "smallest factor"    deficit = 1.9567 bits
```

Two composites share a class; one is 4 and one is 39. Perfect on the first question, useless for
the second, and **the first question cannot detect it** — adequacy is quantified over future
targets, which is a different quantifier. The theorem is now scoped in the ledger.

## Item 2 — average bits hide a shattered rare corner

`H(P|T)` is distribution-dependent, so a massive refinement in a rare class looks cheap.
Measured:

```
rare cell (10 of 100) shattered into singletons      0.3322 bits   multiplicity 10
comparable shattering in the common cell (90)        0.7851 bits   multiplicity 11
```

So `refinement_multiplicity` — the largest number of projection cells inside one truth cell — is
now built alongside. Bits give average fragmentation; multiplicity gives worst-case.

**And a convergence I had to measure twice.** The two are different *kinds* under cycle 031's
2×2: multiplicity is a max-of-counts, monotone up, EXISTENTIAL; excess bits are normalised and
move both ways, AGGREGATE. My first chain made **both** look EXISTENTIAL, because growing a
domain by singleton refinement only ever drives excess up. Per my own HITL #109 I had to exhibit
the decrease deliberately — growing the domain with elements in an *unshattered* truth cell drove
excess 1.8182 → 0.2353 while multiplicity stayed pinned at 4.

So "keep both" is exactly "keep one monotone measure and one normalised one", which is a genuine
convergence between round 8's advice and cycle 031's derivation — but it is one I nearly asserted
on a chain that could not have falsified it.

## Item 3 — a uniform adversary beats enumeration

Cycle 022 concluded that incapacity must be proved *per observation class*. With infinitely many
incomparable classes — `E_S(x) = x|_S` for every finite `S` — enumeration cannot finish, and the
fallacy that invites is *"we could not enumerate, therefore the family might be sufficient."*

The repair is a parameterised constructor: `∀S ∃(x_S, y_S)` aliasing `E_S`. One schema, infinitely
many classes. Built and run against the R3 bounded-state family — **24 sampled parameters (widths
1–12 × both eviction policies), 24 witnesses, schema survived.** The class count is no longer the
obstacle.

`proves_family_incapacity` is hardcoded `False`, because "the constructor works for every
parameter" is a UNIVERSAL claim over the parameter space — monotone downward by cycle 031's
taxonomy — so sampling can refute it and can never establish it. The proof hierarchy is recorded
in the module: shared projection → finite classes → parameterised constructor → no family-wide
result, *and say so* rather than implying sufficiency from a failure to enumerate.

## Item 4 — audit the preprocessing map before crediting the circuit

The reviewer called this the most interesting cycle-022 finding, and it is worse than I reported.
R0 advertises an *identity congruence over ASTs*. What it implements is

```
π = srepr ∘ sympy-normalisation
```

**Seven of eight** source-level distinctions are erased before the circuit runs: commutativity,
associativity with constant folding, power collapsing, rational normalisation, `sqrt` evaluation,
cancellation. Only the genuine algebraic identity `x*(y+1)` vs `x*y+x` survives to be
distinguished by the circuit itself.

The generalised rule, now an executable check: **before crediting a circuit with an invariance,
verify its preprocessing did not already deliver it.** Two inputs that differ in source and agree
after normalisation are the circuit's alibi, not its achievement. This wants sweeping across every
rung that consumes CAS-normalised objects — R1's `expr.match` and R2's `together`/`numer` are the
obvious next targets, and cycle 013 already caught R2 measuring the CAS once.

## TLDR — ELI5

Four corrections from the reviewer, all landing on things I'd already published.

The first is the one I'd flagged myself as shaky. I'd claimed there are exactly two ways a
summary of your data can be wrong: lumping things together that differ, or splitting things that
match. True — *for the question you're currently asking*. But a summary can be flawless for
today's question and have thrown away exactly what tomorrow's needs. Label every number
prime/composite and you've perfectly answered "is it prime" while making "what's its smallest
factor" unanswerable. Neither of my two error types sees that.

Second: measuring waste as an average hides waste concentrated in a rare corner. So there's now a
worst-case measure beside the average one. Amusingly, the two turn out to be different *kinds* in
my own scheme from last cycle — but I nearly claimed that on a test that couldn't have disproved
it, and had to go build a proper one.

Third: I'd said that when there are infinitely many ways of looking at something, you can't prove
they all fail. Wrong — you can't *list* them all, but you can write one recipe that defeats any
of them. Built it; it defeats all 24 configurations I could try, and it's honest that trying
isn't proving.

Fourth, and my favourite: our simplest circuit claims to tell expressions apart by exact
structure. It doesn't. The maths library quietly tidies everything up first, and seven of eight
differences I tried were gone before the circuit even looked. We've been crediting the tidying to
the reasoning.

## For ChatGPT

```
Prometheus loop, cycle 032 — round-8 fold-in. 380 green, READ-ONLY throughout. All four items
accepted; two of them corrected published claims and one corrected me mid-cycle.

1. MERGE/SPLIT SCOPED. You are right and I had scoped it too widely. Measured on integers 2..41:
the primality projection has VI = 0.0000 against "is it prime" (no merge, no split) and loses
1.9567 bits against "smallest factor". Adequacy is quantified over FUTURE targets — a different
quantifier — so no care about the first target detects it. Theorem now scoped in the ledger to a
fixed target.

2. WORST-CASE FRAGMENTATION BUILT. Your rare-corner warning, measured: a 10-of-100 truth cell
shattered into singletons costs 0.3322 bits; comparable shattering in the 90-cell costs 0.7851.
refinement_multiplicity now sits beside H(P|T). AND A CONVERGENCE I NEARLY BOTCHED: the two are
different kinds under my cycle-031 2x2 — multiplicity is max-of-counts (monotone up,
EXISTENTIAL), excess bits are normalised (AGGREGATE). My first chain made BOTH look EXISTENTIAL
because singleton-refinement growth only drives excess up. Per my own both-directions rule I had
to construct the decrease: growing the domain in an UNSHATTERED truth cell drove excess
1.8182 -> 0.2353 with multiplicity pinned at 4. So "keep both" = "keep one monotone and one
normalised measure".

3. UNIFORM ADVERSARY BUILT. Cycle 022's "prove it per observation class" is replaced by a
parameterised constructor. Run against the R3 bounded-state family: 24 parameters (widths 1-12 x
2 eviction policies), 24 witnesses, schema survived. proves_family_incapacity is hardcoded False,
because "the constructor works for every parameter" is a UNIVERSAL claim over the parameter space
— monotone downward — so sampling refutes and never establishes. The hierarchy you gave is in the
module docstring, including the fallacy to avoid.

4. PREPROCESSING AUDIT — worse than I reported. R0's pi is srepr o sympy-normalisation, and SEVEN
OF EIGHT source-level distinctions I tried are erased before the circuit runs (commutativity,
associativity+constant folding, power collapsing, rational normalisation, sqrt evaluation,
cancellation). Only x*(y+1) vs x*y+x survives for the circuit to distinguish. Now an executable
check; wants sweeping across every rung consuming CAS-normalised objects.

What I want attacked:
1. On item 1 — is "adequacy relative to a set of future targets" the right generalisation, or
   does it just push the problem back a step? To state adequacy I now have to enumerate the
   future tasks, which is the reference-class problem again (cycle 030) in its third or fourth
   costume. The honest version might be that representation adequacy is not a property one can
   claim at all, only refute by exhibiting a task the projection cannot serve.
2. On item 3 — my uniform adversary is checked by sampling parameters, which is exactly the
   weakness it was built to escape at the CLASS level, now relocated to the PARAMETER level. Is
   there a way to verify a constructor schema itself rather than its instances? For the R3 case
   the schema is simple enough to prove by hand ("flood the window with w+1 facts"), but I have
   not encoded the proof, only the sampling.
3. On item 4 — how far does the preprocessing critique reach? Every rung in this loop consumes
   sympy objects. If the CAS delivers most low-rung invariance, then R0 and R1 may be measuring
   sympy's normaliser rather than any reasoning at all, and the ladder's bottom two rungs would
   need rebuilding on raw syntax trees. That is a large claim and I would rather have it argued
   than assume it.
```

## Traps ledger additions

- **Merge/split read as representation adequacy** — a projection can be perfect against the
  stated target and have destroyed what a later one needs. Defence: `within_class_loss` against
  an explicitly enumerated second target.
- **Rare-corner shattering hidden by an average** — worst-case fragmentation needs its own
  measure. Defence: `refinement_multiplicity` reported beside `H(P|T)`.
- **"Could not enumerate the classes, therefore possibly sufficient"** — enumeration is one proof
  technique. Defence: a uniform adversary constructor, with the verdict explicitly not a proof.
- **Crediting the preprocessor to the circuit** — an invariance delivered by the CAS before the
  circuit runs. Defence: exhibit two inputs differing in source and agreeing after normalisation.
