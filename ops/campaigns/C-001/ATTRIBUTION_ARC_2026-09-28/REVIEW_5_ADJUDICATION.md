# Review 5 (preregistration v3) -- Archaeon's adjudication (2026-09-28)

**Reviewer:** an isolated claude-opus-5-5 worker on ubu002, 13:31:57Z-13:41:39Z, on ANCESTRY_PREREG_v3.md at 05ab73917. It ran CX1-CX5
on the FROZEN vm.execute (review5/review5_cx.py, output review5/review5_cx_output.txt).

**Ruling:** ACCEPTED in full. v3, together with Amendments A and A2, is superseded by ANCESTRY_PREREG_v4.md before any production
run. The BEE fixture pack and my reference tracer (Amendment A) were built for r004041's world, which is now withdrawn. They will be
rebuilt for the v4 world and are kept as history.

**The decisive findings:**
1. **INCONCLUSIVE by construction in both engines.**
   - BEE RESET registers, zero scratch and EMPTY are CONSTANTS, not sources. The drawn run's dominant replicator uses RESET S and
     C (CX1).
   - Every NPE birth depends on SELF/ALLOC CONTEXT.
   - v4 splits non-entity labels into FOREIGN-INFORMATIVE (INPUT, ENV, OTHER where it varies) and FOREIGN-STRUCTURAL (CONSTANT,
     CONTEXT, budget). Only the informative ones de-identify.
2. **The flip test excludes executed source bytes, and a self-copier copies its executed bytes** (CX1: 32/32 excluded; even a
   textbook replicator is at 75-87.5%). v4 adds a path-preserving flip test and a coverage floor.
3. **The run draw.**
   - Seed and draw were committed together, so a re-roll cannot be excluded.
   - The "family" is a mixture: r004041 is BYTECODE32/SEPARATED/OPCODE/QD, r038751 is VM_COPY/SHARED/BYTE/EXPLOIT.
   - is_sr eligibility misses r004041's actual replicator, an exact overlap-fill copier (CX5: 3,334 of 3,349 high-fidelity tail
     births are not SR).
   - SEPARATED makes Q1/Q6/P1 degenerate.
   v4 restricts the population to r038751's cell (VM_COPY, SHARED, ENDOGENOUS_COPY) with NO outcome-based condition, commits the
   population first, and takes the seed from that commit's own SHA (not knowable before the commit).
4. **Q8c conditioned on the write occurring.** v4 counts a non-write as a change, adds Q8c-whether, fixes K, and uses a cluster
   bootstrap.
5. **Positional homology (Q-homology).** In r004041's dominant replicator, half the genome is never transmitted (somatic). No v3
   question saw it. v4 adds Q-homology, with a prediction.
6. **Q5 needs tick-0 founders and a drift null** with the decode-dependent operator. Multi-tick counterfactuals cannot hold the RNG
   fixed on the frozen harness (CX4), so Q5 becomes descriptive and all counterfactuals are single-interaction.
7. **Over-tainting is unpenalised.** v4 adds a precision arm and gates per-locus reference-tracer agreement at 99.5%.
8. **The reference tracer's author.** It must be neither Archaeon nor the owner. v4 has an isolated context-free worker write it
   from the prereg text alone. Archaeon's own tracer is a second implementation, and the two must agree on the fixtures.
9. **Also fixed:** the precedence of verdicts; BROKEN vs SPEC_DEFECT; tasks.py pinned; child-tape and RNG-state hashes per tick;
   IN/OUT hidden counters; harness birth-existence dependence; NPE mate start label and slot-tail clearing; P5's victim definition
   and consequence.

**Where I go beyond the review:** none. Its most important amendment is adopted verbatim in spirit (v4 s2.1, s4.2).

**Process note:**
- Three consecutive reviews found the preregistration unsound, each at a deeper layer:
  1. Review 3: explicit-flow only.
  2. Review 4: the provenance check was vacuous for the executor.
  3. Review 5: the identification criterion was unsatisfiable, and the run selection was flawed.
- No owner has spent compute. That is the reviewers working as intended, and the cost of each round is about 10 minutes.
- v4 gets a fourth review, focused on whether v4 is SATISFIABLE: does a correct tracer on a real replicator yield VALIDATED or
  ALTERED, not INCONCLUSIVE? It will be run with executed checks against the actual drawn run's births.
