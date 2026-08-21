# Rung R0 — Pattern Response · Circuit Study (Loop pass 1, cycle 001)

**Canon:** `aporia/doctrine/reasoning_ladder.md` v2.0, Band E. R0 = surface-form response;
kill test = paraphrase/isomorphism (accuracy collapse >50% under rename ⇒ R0).
**Existing instrument:** `harmonia/experiments/reasoning_phase0.gen_R0` (clean/iso/adversarial/
transfer versions) — the probe side exists; this note is about the CIRCUIT side.

## 1. What reasoning circuits could be built for R0?

R0 is the one rung where the circuit is fully understood: it is **retrieval keyed on surface
form**. Candidate circuit families, cheapest first:

- **C-R0a: Literal-string memo.** dict[problem_text] → answer. The degenerate case; exists to
  be the floor every other circuit must beat.
- **C-R0b: AST-hash retrieval (built this cycle).** Parse the expression to an AST, hash the
  tree WITH literal identities preserved (variable names, constant values), retrieve. This is
  "pattern response" made mechanically precise: two problems hit the same memo iff their
  surface structure is identical.
- **C-R0c: Canonicalized-AST retrieval.** Same, but hash the tree after alpha-renaming
  variables to de Bruijn-style indices. This is *deliberately one notch above R0* — it
  survives the rename kill test while still being pure retrieval. Its existence is the
  interesting point: **the R0→R1 boundary is exactly the choice of AST canonicalization.**
  Which invariances the hash quotient out = which perturbations the circuit survives. The
  ladder's lower rungs are, mechanically, a lattice of AST quotient maps.

## 2. AST options for this tier

The AST is the natural substrate for Band E because every kill test in reasoning_phase0 is an
AST transformation: iso = rename leaves; adversarial = distractor subtree; transfer = same
tree, new operator leaf. So an R0 circuit's capability is *fully characterized* by the
equivalence relation its key induces on ASTs. That gives a clean research handle:

> **Claim (testable): for Band E, "rung" = coarseness of the AST congruence the circuit's
> lookup key respects.** R0 = identity congruence. R1 ⊇ alpha-equivalence + one rewrite rule.
> R2 ⊇ closure under rule composition along a supplied order.

## 3. TDD tests for an R0 circuit

Built in `techne/ladder_circuits/tests/test_r0_pattern.py`:
- **Recall**: trained pair answers correctly (the only thing R0 promises).
- **Kill test as a test**: iso-variant of a trained problem MUST miss (return `None`), not
  answer. An R0 circuit that answers a paraphrase is mislabeled — the suite enforces the
  *failure*, per falsification-first doctrine.
- **Abstention honesty**: unseen problem → `None`, never a guess.
- **Determinism**: same store, same query, same answer.
- **Canonicalizer contrast**: C-R0c answers the renamed variant (and is therefore NOT R0) —
  the boundary is tested, not asserted.

## 4. Traps for a system gaming the tests

- **Trap 1 — memorized paraphrase table.** A gamed R0+ system passes iso probes by having
  SEEN the iso variants. Trap: generate iso variants at test time with a fresh RNG seed;
  passing rate on unseen renames is the statistic. (reasoning_phase0 already seeds per-run;
  keep it that way — frozen probe files would be gameable.)
- **Trap 2 — answer-distribution priors.** On True/False or small-integer answers, a circuit
  can beat chance with no pattern response at all (the greedy-LoRA lesson,
  `feedback_greedy_lora_surface_not_reasoning`). Trap: score against a shuffled-answer-key
  null; require lift over the label prior, not over 0.
- **Trap 3 — hash-collision freeloading.** A weak hash lets structurally different problems
  collide and "generalize" by accident. Trap: adversarial pairs crafted to collide under
  cheap hashes (same multiset of tokens, different tree) must NOT share answers.
  Test included: token-multiset-equal / tree-different pair.
- **Trap 4 — probe leakage via ordering.** If probes are generated in a fixed order, index
  memorization suffices. Trap: shuffle probe order; accuracy must be order-invariant.

## 5. Straw man built (this cycle)

`techne/ladder_circuits/r0_pattern.py`: `R0PatternCircuit` (exact-AST retrieval) +
`CanonicalizingCircuit` (alpha-renamed retrieval) over sympy ASTs, ~90 lines, no
architecture. Purpose is diagnostic, not capability: it is the **null model** every claimed
R1+ circuit must beat *and* the reference implementation of the rung's failure signature
(answers clean, abstains on iso). 12 tests green.

## 6. Open questions (HITL log carries them)

- Should the R0 null circuit be wired into the grading oracle as a permanent baseline lane,
  so every future reasoner's staircase is reported as lift-over-R0-retrieval? (I think yes;
  it operationalizes the counter-baseline discriminator for Band E.)
- The AST-congruence claim in §2 predicts R1/R2 circuits are enumerable as rewrite-system
  quotients. Next pass should try to falsify it at R2 (does "multi-step execution" really
  reduce to congruence coarseness, or does state tracking break the frame?).

*— Techne loop, cycle 001.*
