## ⚠️ HITL #78 — 530 rows, six cycles unruled

330 when found (cycle 025) → 369 → 400 → 446 → 491 → **530, 0 accepted, 100% drop**. Still
unruled, still unpatched by me.

# Cycle 030 — the reference-class problem: one core, two kinds

**363 green.** Read-only throughout.

## The question

Three independent arrivals of what looked like the same complaint:

- **R11 (cycle 020)** — a forecaster that picks its own reference class can pick a flattering one.
- **Battery strength (cycle 028)** — F6 measured 0.9082 bits on a narrow band, 0.2285 on a wide one.
- **Constancy (cycle 029)** — F11 is constant on well-formed input, VARIES under hostile input.

The instruction was to decide: one phenomenon or three? **The answer is neither, and the split is
the finding.**

## The shared core is real

Each is a property `Φ(O, D)` of an object **and a domain**, stated as though it were a property
of the object alone, with the speaker choosing `D`. That much genuinely unifies, and the fix is
the same in all three: make `D` part of the claim, and refuse a claim that lacks one.

## But they do not behave the same way when `D` grows — and that is testable

**EXISTENTIAL claims are monotone.** A witness stays a witness, so a positive existential holds
on every superset of the domain it was found in. Measured on F11:

```
well-formed only       UNSETTLED
+ hostile              VARIES
+ hostile (superset)   VARIES
```

Only the *negative* — "no witness found in D" — is domain-relative. That asymmetry is exactly why
UNSETTLED is a real verdict rather than a weak yes.

**AGGREGATE claims are non-monotone, and not merely decreasing.** This is where I had to correct
myself mid-cycle: my first attempt only exhibited decreases, which would have left open the
reading that aggregates are monotone-downward and therefore still well-behaved. Constructed the
increase properly, on F6 over real candidates:

```
subset excluding every firing case  (n=40)   0.0000 bits
+ the three firing cases            (n=43)   0.3651 bits    +0.3651   INCREASE
full wide set                       (n=81)   0.2285 bits    −0.1365   DECREASE
```

Widening the domain moved it **up and then down**. So an aggregate value on a superset cannot be
inferred at all, in either direction — only re-measured.

> **A witnessed existential may eventually be stated absolutely. An aggregate never may.**

## The mechanism — `prometheus_math.relative_claim`

The smallest thing that carries a domain and encodes the difference. `Domain` is named and
content-addressed (a digest, so two parties quoting "0.23 on the wide band" can confirm they mean
the same band). `RelativeClaim` carries the property, the value, the domain and the kind.

Rules, each of which is a test:

- **A claim without a domain is refused.** Not defaulted to "all inputs", not defaulted to the
  sample in hand. Every one of the three arrivals above was an undeclared default being read as
  universal, so defaulting is the defect rather than a convenience.
- **A positive existential without a witness is refused** — it cannot travel to a superset, so it
  is an aggregate wearing existential clothes.
- `entails_on(other)` is True only for a witnessed positive existential on a superset. Negative
  existential: never. Aggregate: never, **not even on its own domain**, because re-measurement is
  the only honest route.
- `state_absolutely()` raises for everything except a witnessed existential, and the error names
  the domain, its size and its digest.

Composition tests chain it into both live results — F11's constancy and F6's resolution — so the
rules are pinned against real measurements rather than illustrations.

## Bearing on the constitution

**Partial.** The declared-domain mechanism is the same *shape* the immutable-observation
constitution needs — an external, checkable statement of what was measured over, fixed before the
measurement is quoted — so it is a fifth argument in the sense that it is a fifth place the same
need appears. But it is **not the same mechanism**: the constitution's job is that the historical
record of predictions and outcomes cannot be rewritten, and a domain digest does not do that. It
constrains what a claim *means*, not what the record *says*.

The honest statement: four arguments for the constitution, plus one adjacent requirement that
shares its shape and would sit naturally alongside it. Not ratifying anything — that is James's
call — and not inflating the count.

## TLDR — ELI5

Three times now, a measurement has changed its answer depending on which examples I happened to
feed it, and each time nobody had written down which examples counted. The question was whether
that's one problem or three.

It's one problem with two halves, and the halves behave differently.

If your claim is "there EXISTS something that breaks this" — once you've found one, you've found
it. Adding more examples can never un-find it. Those claims get stronger as you look harder, and
once witnessed you can state them flatly.

If your claim is an AVERAGE over the examples — "this check catches 23% of things" — then adding
examples moves the number, and I showed it moves *both ways*: the same check read 0%, then 37%,
then 23%, purely from widening the pool. So that kind of number is never a fact about the check.
It's a fact about the check *and* the pool, permanently, and quoting it without the pool is how
you accidentally make a universal claim.

So the tool refuses to let you state an average without saying what you averaged over — and
refuses to let you claim you found something without producing the thing you found.

## For ChatGPT

```
Prometheus loop, cycle 030. The reference-class problem, which had arrived three independent
times. Instruction: decide whether it is one phenomenon or three. 363 green. READ-ONLY.

ANSWER: NEITHER — one shared core, two kinds, and the split is the finding.

SHARED CORE (real): each is a property Phi(O, D) of an object AND a domain, stated as though it
were a property of the object alone, with the speaker choosing D. Same fix in all three: make D
part of the claim and refuse a claim without one.

THE SPLIT (measured):
* EXISTENTIAL claims are MONOTONE. A witness stays a witness. F11: UNSETTLED on well-formed
  input, VARIES once hostile input is added, VARIES on every superset after. Only the NEGATIVE
  ("no witness in D") is domain-relative.
* AGGREGATE claims are NON-MONOTONE, and I had to correct myself here. My first attempt only
  exhibited DECREASES, which leaves open "monotone downward, therefore still well-behaved". So I
  constructed the increase properly, on F6 over real candidates:
      subset excluding every firing case (n=40)  0.0000 bits
      + the three firing cases           (n=43)  0.3651 bits   +0.3651 INCREASE
      full wide set                      (n=81)  0.2285 bits   -0.1365 DECREASE
  Widening moved it UP then DOWN. A superset value cannot be inferred in either direction, only
  re-measured.

So: a witnessed existential may eventually be stated absolutely; an aggregate never may.

MECHANISM: prometheus_math.relative_claim. Domain is named and content-addressed (digest, so two
parties quoting "0.23 on the wide band" can confirm they mean the same band). RelativeClaim
carries property, value, domain, kind. Rules, each a test: a claim without a domain is REFUSED
(not defaulted to "all inputs", not to the sample in hand — every one of the three arrivals was
an undeclared default read as universal); a positive existential without a witness is refused
(it cannot travel, so it is an aggregate in disguise); entails_on is true only for a witnessed
positive existential on a superset; aggregates never entail, NOT EVEN ON THEIR OWN DOMAIN, since
re-measurement is the only honest route; state_absolutely raises for everything else and names
the domain, size and digest.

ON THE CONSTITUTION: partial, and I am not inflating the count. The declared-domain mechanism has
the same SHAPE the immutable-observation constitution needs — an external checkable statement
fixed before the claim is quoted — but it is not the same mechanism. The constitution's job is
that the record of predictions and outcomes cannot be rewritten; a domain digest constrains what
a claim MEANS, not what the record SAYS. So: four arguments for the constitution, plus one
adjacent requirement sharing its shape.

What I want attacked:
1. Is the existential/aggregate split exhaustive? Those are the two I met. A universal claim
   ("for all x in D, P(x)") is the obvious third: monotone DOWNWARD — it can only be broken by
   widening, never established. If that is right the taxonomy is three-with-a-symmetry
   (existential monotone up, universal monotone down, aggregate neither) and I should build the
   third rather than wait to trip over it. But I have said "that feels exhaustive" twice this
   month and been wrong once.
2. Aggregates never entailing even on their own domain is deliberately strict — re-measurement
   on the identical domain is deterministic and would give the identical number. I made it
   refuse anyway so that no code path can quote a cached aggregate as though it were a fact. Is
   that over-strict to the point of being ignored in practice, which would be worse than a
   permissive rule people actually follow?
3. The domain digest is over repr(members). That makes it stable and checkable but ties it to
   Python representation, so the same mathematical domain built differently digests differently.
   Is a semantic digest worth it, or is repr-stability the right trade for a bookkeeping tool?
```

## Traps ledger additions

- **Undeclared domain read as universal** — a measurement quoted without the input space it was
  taken over. Defence, BUILT: `RelativeClaim` refuses construction without a `Domain`.
- **Positive existential without a witness** — cannot travel to a superset, so it is an aggregate
  in disguise. Defence: refused at construction.
- **Cached aggregate quoted as a fact** — an aggregate value from one domain read as a property
  of the object. Defence: `entails_on` returns False for every aggregate, on every domain.
- **Monotone-downward mistaken for well-behaved** — my own near-error this cycle: exhibiting only
  decreases would have left aggregates looking safely bounded. Defence: to claim non-monotonicity,
  exhibit a move in *both* directions.
