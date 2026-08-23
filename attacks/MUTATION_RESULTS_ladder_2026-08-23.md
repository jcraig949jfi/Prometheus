# Mutation test of the reasoning-ladder circuits — 2026-08-23

**Question asked (James):** *"I don't trust the tests. Can we review those? Is there a way to
harden them? Test the tests?"*

**Instrument:** `attacks/mutation_harness.py`. Corrupt the module one AST node at a time, re-run
that module's own test file, count how many corruptions the suite fails to notice. **No judgment
in the verdict path** — the verdict is pytest's exit code on known-broken code.

**Host:** M3/GANDALF — *not* the machine the Techne loop runs on. 20 mutants per module.
Reproduce: `python attacks/mutation_harness.py <src.py> <test.py> 20`.

---

## Scores

| module | killed | survived | raw | **corrected** | note |
|---|---|---|---|---|---|
| `canon_r6_falsification.py` | 20 | 0 | 100% | **100%** | strongest suite measured |
| `canon_r5_invariant.py` | 19 | 1 | 95% | **100%** | lone survivor is `frozen=True` |
| `r4_strategy.py` | 16 | 4 | 80% | **80%** | |
| `r7_plan_revision.py` | 16 | 4 | 80% | **80%** | but see H1 — worst *kind* of hole |
| `r1_local_op.py` | 11 | 3 | 79% | **85%** | |
| `r2_pipeline.py` | 15 | 5 | 75% | **79%** | |
| `preprocessing_audit.py` | 15 | 5 | 75% | **79%** | |
| `canon_r10_analogy.py` | 14 | 6 | 70% | **78%** | |
| `canon_r12_conjecture.py` | 13 | 7 | 65% | **68%** | weakest measured |
| `aliasing.py` | — | — | — | **UNMEASURABLE** | baseline suite RED |
| `epistemic_value.py` | — | — | — | **UNMEASURABLE** | baseline suite RED |
| `fresh_generation.py` | — | — | — | **UNMEASURABLE** | test file exceeds 300 s/run |

**Corrected** excludes `@dataclass(frozen=True) → frozen=False` mutants (8 across the run).
Nothing tests immutability, which is true but near-equivalent — counting them would have
understated every suite. *This is why a mutation score must never be quoted without reading its
survivors.*

**Headline: median corrected score ≈ 80%.** For a research codebase that is respectable — better
than the prediction on record (that most rungs would fall). **The ladder's tests are not the weak
part of this work.** But the surviving holes are not randomly distributed, and where they cluster
matters more than the scores.

---

## The pattern: verdict-bearing and record-bearing code is the least tested

Every substantive survivor is in machinery that *decides or records whether something worked* —
never in the computation itself. The suites verify that the circuit computes; they do not verify
the apparatus that says whether the computing succeeded.

**H1 — `r7_plan_revision.py:50,72` — the learning record can be inverted undetected. (worst)**
`self.log.append(Attempt(plan, out is not None))` → `out is None` survives. Control flow is
separate (`if out is not None: return out`), so the circuit returns **the right answer with its
entire success/failure history inverted**, and no test fails. Three lines below the mutation site:
`# the failure TAUGHT something and it is retained`. In a program whose north star is *failure
from attempt N improving attempt N+1*, the residue is the log — and the log is unpinned.

**H2 — `preprocessing_audit.py:112,114` — the verdict property is never asserted.**
`as_expected` (`return want == got`) survives both `Eq→NotEq` and `return None`. No test asserts
it. This is the module behind the cycle-032 finding that R0/R1 may be measuring sympy's
normaliser rather than reasoning — which the loop itself called "the most consequential thread
open." Its verdict channel is untested.

**H3 — `canon_r12_conjecture.py:92` — the canon's own kill test is dead code to the suite.**
`closed_universe_alias_pair()` → `return None` survives, so no test calls the function encoding
R12's kill test. R12 is the top rung.

**H4 — `r2_pipeline.py:69` — `Div → Mult` survives.** The test corpus cannot distinguish
dividing by the leading coefficient from multiplying by it, which means it exercises only
`a = ±1`. Line 67's legality guard also survives `or → and`: its disjuncts are never
individually exercised.

**H5 — `r1_local_op.py:32` — the documented legality guard is untested.**
`sp.Wild("a", exclude=[0])` → `exclude=[1]` survives. The docstring makes this guard the
module's headline claim — *"Guard IS the operation's legality domain — 0*x + 7 matches the
template but has no root"* — and nothing tests it.

**H6 — `r4_strategy.py:43,45,47` — work accounting unpinned.** `max(len(trace), 1)` → `2`
survives three times. The `work` metric the loop proposed as a grading field (HITL #46) is not
tested.

---

## Hardening: targeted, not a rewrite

Roughly fifteen assertions close nearly everything above:
1. Assert the **contents of `log`**, not just the returned answer, in every R6/R7 test — the
   single highest-value fix in the list.
2. Assert `as_expected` directly, both polarities.
3. Call `closed_universe_alias_pair()` in an R12 test and assert the pair's defining property.
4. Add a linear case with `a ∉ {−1, 0, 1}` (e.g. `3x + 7 → −7/3`) so `*` and `/` separate.
5. Add `0·x + 7 → abstain` to the R1 suite.
6. Assert one exact `work` count.
7. Fix the two red suites and the 300 s test file. **Unmeasurable is not passing** — three of
   twelve modules could not be tested at all, and that is a bigger gap than any score here.

## What this does NOT license

Mutation testing measures the tests **against the implementation, never against the intent**. A
100% score says the suite notices when the code changes; it says nothing about whether the code
does anything worth doing. `canon_r6_falsification.py` scored 100% — that means its tests are
tight, not that its circuit reasons.

It also **would not have caught F9** (`return True` in the discovery pipeline's kill battery):
mutating it to `return False` is killed by a test asserting the tautology, and the suite looks
healthy. That failure mode needs the dual instrument — `prometheus_math.battery`'s
structural-constancy probe, which asks whether a member reads its arguments at all.

**Mutation testing catches tests that don't notice broken code. The constancy probe catches code
that cannot fail. Neither catches a circuit that is simply beaten by a trivial baseline** — for
that, run the baseline (as X-3 did, where raw term vectors scored 0.1250 against 0.1225 for four
campaigns of engineering).
