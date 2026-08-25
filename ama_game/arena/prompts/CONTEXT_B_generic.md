--- CONTEXT PACKAGE ---

Condition B. Generic falsification guidance. No arena history, no retrieved
cases, nothing specific to this claim.

Mathematical arguments commonly fail in the following ways. Consider each
against the claim in front of you:

- **Domain change** — the argument moves between domains without saying so:
  integers to rationals, closed interval to open, finite to infinite, a generic
  point to every point.
- **Quantifier error** — ∀∃ where ∃∀ was needed, or a uniform bound asserted
  from a pointwise one.
- **Invalid equivalence** — a step presented as reversible that is not: squaring
  both sides, multiplying by a quantity that may be zero, exponentiating,
  applying a non-injective map.
- **Hidden assumption** — an unstated coprimality, positivity, non-degeneracy,
  or general-position condition doing load-bearing work.
- **Boundary omission** — the claim fails at n = 0, n = 1, n = 2, the empty set,
  or a degenerate configuration.
- **Unjustified independence** — two quantities treated as independent that are
  coupled.
- **Incomplete exhaustive check** — "all cases" enumerates a proper subset; a
  recursion misses a branch.
- **Solver-encoding mismatch** — the verifier faithfully checks a proposition
  that is not the one claimed.
- **Numeric trap** — true in floating point and false exactly, or the
  counterexample sits below the precision floor.
- **Invalid inference** — a step that does not follow, dressed as routine.
- **State/invariant error** — an invariant asserted to be preserved that some
  operation breaks.

General technique:

- Test the smallest cases first, including the degenerate ones.
- Check the claim's stated domain against the domain its verifier iterates.
- Before searching, predict where it breaks; then test the prediction.
- Prefer one small witness to a large search.
- A bounded search that finds nothing bounds the failure; it does not prove the
  claim.
