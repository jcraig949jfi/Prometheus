# Mutation grammar (V0) — `proteus/foundry/grammar.py`, hash recorded in `v0/NEUTRALITY_PREREG.json`

Thirteen operators, all syntactic or genotypic (amendment A3). One operator per descent by
default. Weights are frozen and part of `GRAMMAR_HASH`; changing any weight is a new grammar and
requires a new neutrality preregistration and run.

| operator | weight | what it does (the hashed description) | length |
|---|---|---|---|
| insertion | 0.08 | insert k in [1,4] uniformly random instructions at an aligned position | + |
| deletion | 0.11 | delete k in [1,4] contiguous instructions at an aligned position | − |
| duplication | 0.04 | copy k in [1,4] contiguous instructions and insert the copy at an aligned position | + |
| movement | 0.08 | cut k in [1,4] contiguous instructions and paste them at another aligned position | 0 |
| replacement | 0.12 | overwrite one instruction with four uniformly random words | 0 |
| operand_perturbation | 0.19 | pick one word; add a signed delta in [−8,8] or flip one bit | 0 |
| reference_redirection | 0.08 | pick one instruction; keep its opcode word; overwrite one operand word uniformly | 0 |
| region_swap | 0.06 | swap two non-overlapping regions of k in [1,4] instructions | 0 |
| splice | 0.05 | replace a region of k instructions with a region of k′ instructions copied from a mate (self if none) | ± |
| zeroing | 0.04 | set a region of k in [1,4] instructions to all-zero words (NOP 0 0 0) | 0 |
| randomization | 0.04 | set a region of k in [1,4] instructions to uniformly random words | 0 |
| unreachable_removal | 0.03 | delete one instruction not statically reachable from ip=0 (no offset fixup; approximate when code_writable) | − |
| config_perturbation | 0.08 | step one manifest limit (n_regs, tape_words, code_writable, persist, tick_budget, out_cap) within published bounds | 0 |

**Version v0.1.** Grammar v0 (deletion 0.10, operand_perturbation 0.20, tape halving clamped to
the genome) FAILED the neutrality gate with a growth ratchet: operator mass favoured subtraction
(0.13 vs 0.12) but expected *instructions* did not (0.25 removed vs 0.30 added), because
unreachable_removal removes one instruction while the others move about 2.5. That mistake is
recorded in `v0/NEUTRALITY_PREREG.md`. v0.1 balances expected instructions (≈0.275 + 0.01–0.03
removed vs 0.30 added) and stops the tape-halving clamp that pinned genomes at their cap.
Whether v0.1 is free of a ratchet at a 300-generation horizon is a measured property under the
same preregistered tolerances, not a design claim.

**Operators considered and NOT built, with the reason (A3 flag rule):**

- *"promote a subroutine"*, *"add a loop"*, *"wire an input to an output"* — each is describable
  only as adding a presumed capability; flagged, not built.
- *"semantic-preserving refactor"* — requires an oracle for semantics; not syntactic.
- *"crossover at matching opcode"* — "matching" is a cognition stem and the operator privileges
  structure the grammar would then be authoring. Splice at arbitrary aligned positions was built instead.

**Lens tags dropped.** The pre-execution packet's C5 promised per-operator `(M, T, C, Π)` tags.
Under A3 the operators are purely syntactic and no such tag is meaningful: an insertion is not
"about" memory or control; it is four words. C5's check is therefore withdrawn as written, and
replaced by the knockout vector, which reports post hoc which primitive classes an organism's
transcript actually depends on. Recorded here so the packet's promise is seen to have been changed, not forgotten.

**Config perturbation** is the only operator that touches the manifest outside the genome. It is
how the population moves along the bounded-storage and persistence axes. It never changes
`schema_version`, never exceeds the published bounds, and never shrinks the tape below the genome.
