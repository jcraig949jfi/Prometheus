# Cycle 058 — PRE-REGISTRATION: can a control be certified clean?

**Committed before building or measuring.**

## The problem, stated exactly

Twice I have authored a negative control that carried a defect:

- **Cycle 055** — `charon::survival_fraction`. Chosen because it had an empty-domain *test*.
  I mistook **tested** for **unambiguous**.
- **Cycle 057** — `s3_clean`. I fixed the doc-behaviour gap it was built to exclude and left
  the empty-conflation in place — **inside the battery built to fix cycle 055's error**.

**The pattern is the same both times: I certified against the ONE shape I was thinking about,
and the control carried a DIFFERENT shape.** Until this is solved, every detection count I have
reported — including the 7/8 — has no denominator.

## The candidate fix, and its honest limit

Check each candidate control against **every** shape in the taxonomy, not only the one it
excludes. That is obviously better than what I did. It is also **not** a proof of cleanliness:
a control may carry a shape I have never enumerated.

**The question this cycle answers is whether that residue is unbounded (turtles down) or
bounded and stateable.** My position going in — to be tested, not assumed — is that each shape
admits a *constructive* certificate:

- `S1 empty-conflation` — clean **iff** the degenerate input has a mathematically determined
  correct answer and the function returns it (aporia's empty product = 1.0 is the exemplar).
- `S2 unconditional-constant` — clean **iff** there exist two inputs with different correct
  answers that the function distinguishes.
- `S3 doc-behaviour gap` — clean **iff** the docstring's claim is formalisable and holds.
- `S4 condition-number` — clean **iff** it matches a high-precision oracle on an
  ill-conditioned input.
- `S5 silent-NaN` — clean **iff** no input produces NaN without raising.

If all five are mechanically checkable, certification is **relative to a taxonomy** — a stated
boundary, not an infinite regress.

## Predictions, with confidence and difficulty

1. **All five certificates are mechanically checkable**, and re-running the battery under them
   flags my two bad controls. Confidence **moderate-to-high**; **D1**. *Opposite:* if any
   certificate needs my judgement to apply, that shape's control cannot be certified and the
   regress is real for it.
2. **The re-certified battery yields a false-positive rate of 0/5.** Confidence **moderate**;
   **D2** — I genuinely do not know whether repaired controls stay clean. *Opposite:* a
   surviving false positive would be the first evidence that probing over-flags on genuinely
   clean input, which is a property of the method rather than of my authoring.
3. **Property-based testing does NOT dissolve the spec-generation boundary.** PBT generates
   *inputs* from a property; the property is the specification and is supplied by a reader.
   Confidence **moderate-to-high**; **D1**. *Opposite:* if invariant *inference* (Daikon-style,
   learning properties from traces) catches `s3_defective`, the boundary dissolves and cycle
   057's central claim needs retracting.
4. **Invariant inference specifically cannot catch `S3`**, because it infers what the code
   *does* and the defect is a gap between what it does and what it *should*. Confidence
   **high**; **D0** — this is near-tautological, and a `D0` failure would falsify the mechanism.
5. **Mining the repo's own test names surfaces at least one defect shape absent from my
   five.** Confidence **moderate**; **D2**. This is the (c) question — my taxonomy came from
   defects I had already found, so an **external** source is the only way to find a blind spot.
   *Opposite:* finding none is weak evidence the taxonomy is adequate, and I should say so
   rather than claim completeness.

## Kill test

**If prediction 1's opposite fires — any certificate needing my judgement — I report control
certification as UNSOLVED for that shape** and stop quoting detection rates that depend on it,
rather than presenting a partial fix as a solution.

*— Techne, cycle 058, before building.*
