# Loop Cycle 015 — 2026-08-21 (first cycle under CORRECTED canon numbering)

## Track 1 — Lean 4 proof-checker oracle: SPIKE PASSED, tool forged

The last unstarted item from the 2026-08-21 arsenal scan, and it turned out to be nearly free:
**Lean 4.30.0 is already installed on M1 via elan.** No procurement, no model — a wrap
(Standing Order #1) of the checker as a VERDICT LANE, which is what canon §7 says R9 (lemma
invention) requires.

`prometheus_math/lean_oracle.py` + 7 tests, all green against real Lean:
- `2 + 2 = 4` -> PROVED; `∀ a b : Nat, a + b = b + a` (by omega) -> PROVED.
- `2 + 2 = 5` -> **REFUTED**, with Lean's own words ("proved that the proposition ... is false").
  That trustworthy NO is what makes this a verdict lane rather than a linter.
- **Three-valued by design:** a syntax error and a tactic that cannot discharge a TRUE
  statement both return ERROR, never REFUTED. Conflating "I could not tell" with "false" is
  exactly the phantom-failure pathology canon R6 scores — a verdict lane that committed it
  would poison every claim it touched.
- Verdicts carry toolchain + source hash (provenance doctrine).

Install friction worth recording: the elan shim defaults to a 2023 nightly that rejects modern
syntax, so the wrapper writes a `lean-toolchain` file beside every claim. Found by the spike
failing, not by reading docs.

## Track 2 — CANON R5 (invariant detection) built

`canon_r5_invariant.py` + 8 tests. The artifact requirement is the rung: not "impossible" but
**the conserved quantity, NAMED**, with BOTH properties checked — conserved under the actual
move set, and decisive between start and goal.

- Canon probe reproduced: mutilated board -> impossible, quantity `colour_difference`,
  start -2, goal 0. (My draft had the sign backwards; the board is the authority.)
- **Canon kill executed:** the near-identical board with two OPPOSITE-colour cells removed.
  Parity is balanced, the classic argument is silent, and the honest circuit ABSTAINS rather
  than converting "my invariant is quiet" into a verdict.
- **Trap 2 (conserved but not decisive)** caught by the artifact check: a genuinely conserved
  quantity taking the same value on start and goal proves nothing, while passing any test that
  only asks "is it conserved?".

## 7th instance of the competitor-relative law — and a sharper repair than expected

On a battery of ONLY classic mutilated boards, the parity pattern-matcher and the real
reasoner agree on every verdict AND on the named quantity. Observationally identical.

The repair is narrower than I assumed. Varying the removed-cell colours does **not** separate
them — with parity balanced the matcher also abstains, looking exactly as careful as the real
reasoner. **Only varying the MOVE SET separates them**: under diagonal moves (which do not
conserve colour) the matcher keeps asserting an invariant those moves do not preserve, while
the reasoner abstains.

> A battery that varies only the problem instance, never the OPERATOR SET, cannot tell a
> conservation-checker from a shape-matcher.

That is a battery-design rule with teeth beyond this rung, and it generalises the trap ledger
from "vary the probes" to "vary the rules of the game".
