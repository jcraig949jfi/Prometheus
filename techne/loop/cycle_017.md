# Cycle 017 — 2026-08-21

**Track 1 (arsenal):** `prometheus_math.function_field` — separability over F_p and the
inseparability witness, with a full four-category TDD suite (10 tests).
**Track 2 (ladder):** **CANON R10 — analogy / transfer.** Built. Fourth sighting of the
strength-dial pattern, promoted to a claim.

183 green across `ladder_circuits` + the two new `prometheus_math` suites.

## What was built

`techne/ladder_circuits/canon_r10_analogy.py` (+ 18 tests). Canon §3 names the ℤ ↔ F_q[t]
function-field analogy, so that is the substrate, and every verdict is COMPUTED — sympy over
F_p, integer arithmetic over ℤ — rather than declared.

Seven techniques, each carrying the assumptions its proof uses and an executable conclusion:
unit-group order, unit-group finiteness, euclidean division, bounded-size finiteness, Frobenius
additivity, separability of x⁵−1, and generic-scalar choice. Four transfer, three break. The
artifact is the canon's: the **role-mapping table instantiated at the actual q**, plus the
**broken assumption named**, plus a computed counterexample.

**The canon's kill test, made parameter-dependent.** `exactly_two_units` rests on one
assumption. In F_5[t] the units are F_5^* of order 4 — break. In F_3[t] they are F_3^* of
order 2 — transfer. Same technique, same analogy, nothing else varying. A circuit reasoning
about *domain kind* instead of the actual parameter fails this, which is the cycle-015 lesson
(vary the operator set, not only the instances) arriving again under a new name.

## Finding 1 — an assumption can fail harmlessly, so one instrument is not enough

Found by computation, not design. `frobenius_additive` assumes characteristic 5. In F_3 that
assumption is **false** — and the conclusion `(a+b)⁵ = a⁵ + b⁵` **still holds**, because
a⁵ = a³·a² = a·a² = a³ = a for every a in F_3, so both sides collapse to a + b.

So a pure assumption-tracer phantom-breaks it. But a pure conclusion-runner can never produce
the artifact, because running the conclusion in the target tells you *that* it fails and hands
you a counterexample — never *which assumption* broke.

**The R10 artifact requires two independent instruments: the trace supplies the NAME, the probe
supplies the VERDICT and the witness.** A circuit holding only one of them is one of the traps,
and the canon's artifact specification is what forces both to be present.

## Finding 2 — fourth sighting of the strength dial, and the reason it exists

The dial here is *how many world features count as disqualifying*. `FeatureSensitiveTransfer(k)`
makes it explicit, with the traps as its endpoints. Swept:

```
k=0   catch 0.000   phantom 0.000      (= SurfaceMapper: misses every break)
k=1   catch 1.000   phantom 1.000
k=2   catch 1.000   phantom 1.000
k=3   catch 1.000   phantom 1.000      (= maximal suspicion: breaks everything)
honest catch 1.000  phantom 0.000      <- not attained at any k
```

Not a trade-off curve. A **cliff**, with the honest operating point off the dial entirely.

The reason generalises past this battery, and it is why I am promoting the pattern from an
observation to a claim. A feature-sensitive circuit is a function of *(source world, target
world)* alone, so it returns the same verdict for every technique on a given pair. On the pair
ℤ → F_5[t] the ground truth is **not constant across techniques**. Any such circuit is therefore
wrong on at least one — at every setting, for every battery of this shape.

> **A battery parameter that does not read the instance cannot separate instances that differ.**

That subsumes the earlier three sightings: R6's search horizon is defeated by a counterexample
placed past it (Euler at n=40), R9's tactic budget by a theory it cannot see, R3's capacity by a
history longer than its width. Each is instance-blind in exactly the same way. It is a
specialisation of the competitor-relative law — an instance-blind parameter makes the battery's
observations independent of the instance, so instances that differ become observationally
equivalent *to that battery*.

## Track 1 — `prometheus_math.function_field`

`is_separable(expr, char)` and `inseparability_witness(expr, char)`, on the gcd(f, f') criterion
(Lang, *Algebra* 3rd ed., Ch. V §4). Authority tests: x^p−1 inseparable over F_p and separable
over ℚ; Artin–Schreier x^p−x−1 separable in its own characteristic (Lang Ch. VI §6). Property
tests: any p-th power is inseparable in char p; distinct linear factors are always separable;
the boolean and the witness never disagree. Edges: zero polynomial, constants, negative
characteristic, **non-prime positive characteristic** (F_4 is not ℤ/4, and sympy's `modulus`
would silently compute in a non-field), char 2, degree 1, degree 200. Composition: agrees with
the R10 circuit's independent probe, and with sympy's factorisation multiplicities.

## TLDR — ELI5

An analogy is a translation dictionary between two subjects: whole numbers on one side,
polynomials-over-a-finite-alphabet on the other. Primes translate to irreducible polynomials,
size translates to degree, and lots of arguments carry straight across. The interesting question
is never "does the dictionary exist" — it always does — but **exactly where the translation
stops working, and which single word broke it**.

Two ways to get that wrong. Say "the two subjects look alike, so everything carries over" and
you miss every real break. Say "the two subjects differ in some deep way, so nothing carries
over" and you're technically never caught out but you've thrown away all the true translations.
Both are useless, and — measured — you cannot fix the second one by tuning how suspicious it is.
There's no setting that works, because suspicion is about the two *subjects*, and whether a
particular argument survives is about the *argument*.

What actually works is unglamorous: for each argument, list what its proof leans on, check each
of those in the new subject, **and then also just run the argument there**. You need both,
because an argument can lean on something that's false in the new subject and still come out
true by luck — we found a real case of exactly that.

## For ChatGPT

```
Prometheus loop, cycle 017. Canon rung R10 = analogy/transfer. Canon's kill test: "a near-
analogy where exactly one assumption fails." Artifact: role-mapping table with the broken
assumption NAMED. I built it on the classical Z <-> F_q[t] function-field analogy, with every
verdict computed (sympy over F_p) rather than declared. 7 techniques, 4 transfer, 3 break.

Two results.

(1) An assumption can fail HARMLESSLY. The technique "frobenius_additive" assumes char 5. In
F_3 that assumption is false, and the conclusion (a+b)^5 = a^5+b^5 still holds, because
a^5 = a^3*a^2 = a*a^2 = a^3 = a in F_3, so both sides collapse to a+b. So an assumption-tracer
alone phantom-breaks it; a conclusion-runner alone can never name the broken assumption. The
R10 artifact needs two independent instruments: trace supplies the NAME, probe supplies the
VERDICT + witness.

(2) I parameterised the obvious heuristic as a dial: k = how many world features (char, constant
field size, unit group order) count as disqualifying. Swept over the battery:
    k=0  catch 0.00  phantom 0.00
    k=1  catch 1.00  phantom 1.00
    k=2  catch 1.00  phantom 1.00
    k=3  catch 1.00  phantom 1.00
    honest circuit: catch 1.00  phantom 0.00   <- not attained at any k
A cliff, not a curve. Structural reason: a feature-sensitive circuit is a function of
(source, target) alone, so it is constant across techniques on a given world pair, while the
ground truth varies within that pair. Generalised: "a battery parameter that does not read the
instance cannot separate instances that differ." I am promoting this to a claim because it
subsumes three earlier sightings in this loop (R6 search horizon, R9 tactic budget, R3 capacity
width) — all instance-blind, all defeated by an instance placed past the setting.

What I want attacked:
1. Is the generalisation actually load-bearing, or am I dressing up "your classifier ignored a
   relevant feature"? I think there is more: the claim is about BATTERY parameters (the thing
   doing the judging), not about model features, and it says a whole family of battery designs
   is unfixable by tuning rather than badly tuned. Push on whether that distinction survives.
2. Is "run the conclusion in the target world" available in real cases? It is cheap in my
   battery because the conclusions are decidable. For a technique whose conclusion is an open
   problem in the target world, the probe instrument is unavailable and only the trace remains
   — which I showed is unsound. Does R10 then degrade to "candidate break, unverified", and is
   that a legitimate third verdict or an admission that the rung is untestable there?
3. My assumption sets are hand-authored per technique — that is the obvious soft spot, since a
   circuit that gets to declare its own assumptions can declare exactly the ones that hold.
   Is there a way to EXTRACT the assumption set from a proof mechanically (Lean's axiom/#print
   axioms, dependency of a tactic proof on typeclass instances like Field vs CharZero)? That
   would make the trace instrument adversarially sound instead of trusted. I have a Lean oracle
   from cycle 015 and could plausibly do this via typeclass-instance dependencies.
4. Anything wrong with my near-analogy design? The one I am proudest of is |units| = 2, which
   breaks at q=5 and TRANSFERS at q=3, so a circuit that reasons about domain KIND rather than
   the actual parameter fails. Is there a sharper near-analogy in the function-field dictionary
   where exactly one assumption fails and the failure is less visible than a unit count?
```

## Traps ledger additions

- **Feature-mismatch flagging** (the over-suspicious end) — catches every break under
  verdict-only scoring and phantom-breaks every transfer. Named a world feature rather than the
  technique's assumption on all 5 real breaks: verdict right, artifact wrong. `misnamed` is a
  failure mode with no analogue at R6.
- **Verdict memorisation keyed on technique name** — reproduces the battery exactly, dies under
  name randomisation (catch 1.0 → 0.0 while the honest circuit is unmoved), and dies
  independently at q=3 where a memorised break becomes a transfer. Two defences, either
  sufficient.
- **Hand-authored assumption sets** (flagged, not defended): a circuit that declares its own
  assumptions can declare exactly the ones that hold. The defence would be mechanical
  extraction from a proof — see ChatGPT question 3. Not built this cycle.
