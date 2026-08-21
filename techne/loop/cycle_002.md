# Loop Cycle 002 — 2026-08-21

**HITL check:** no replies yet (charter: continue).

**Track 1 (arsenal):** `prometheus_math.tensor_train` FORGED — quimb installed and wrapped.
`tt_ranks` / `tt_reconstruct` / `tt_rank_null_test` / `signature_occupancy_tensor`.
11 tests, four categories: authority incl. the TT-SVD unfolding-rank theorem checked against
numpy as an independent second tool; property incl. **the degenerate-null proof** (slice
permutation along any axis is rank-invariant — the F011 lesson encoded as a theorem-test);
composition incl. planted-structure detection with null calibration AND the real
signature_index ledger loading end-to-end (3,311 rows → generator × claim_kind × verdict
occupancy tensor). The API ships ONLY the correct fiber-shuffle null — the wrong null is not
reachable through this module. Registered in facade; TDD_LOG row added.
This is Priority-#1 material: the proto-tensor now has a rank instrument with the null
discipline built in, not bolted on.

**Track 2 (ladder, rung R1):** notes + straw man (`r1_local_op.py`, guarded template-rule
circuit) + 8 tests. R1 must PASS R0's kill test (renames, fresh coefficients — capability)
and ABSTAIN upward: no rule, guard-illegal (0·x+7), symbolic coefficient needing a case
split, AC near-misses. New traps: answer-function overfit (probe far outside any training
hull — 10⁹ coefficients, exact rationals), guard-as-class-prior, template overreach.

**The claim took its first hit, as hoped:** cycle-001's "rung = AST congruence coarseness"
does NOT survive R1 unamended — R1 answers VARY within a template class, so the object is a
congruence + witness fibration + legality guard. Amended claim (v2): Band E rung =
(congruence coarseness, witness arity, guard complexity). Next cycle tries to break v2 at R2:
does "multi-step along a supplied order" reduce to witness-passing between fibrations, or
does growing state escape the frame?

**Next cycle (003):** Track 1 → PySR spike (venv install, smoke on a known law). Track 2 →
rung R2 (multi-step execution); consider `egglog` for rule composition.

---

## TLDR ELI5

Two builds. First, a *structure detector* for our big data cube. Imagine a huge box of
numbers; if the rows and columns secretly move together, the box can be compressed a lot —
and the amount it compresses is a measurement of hidden structure. The trap is that a lazy
shuffle test can look rigorous while proving nothing (shuffling whole rows changes nothing
about compressibility — we *proved* that and built the test so only the honest shuffle is
even possible to run).

Second, one rung up the ladder: last time we built the student who only answers questions
seen letter-for-letter. This time, the student who has been *taught exactly one trick* (solve
a·x+b) and applies it perfectly to any numbers — but refuses to answer when the trick doesn't
apply, when it would divide by zero, or when the question needs two tricks in a row. The
refusal is the point: it draws the line between "knows one move" and "can chain moves," which
is the next rung. And our neat theory from last cycle already needed a patch to survive this
rung — which is what a good theory-under-test looks like.

---

## ChatGPT paste block (cycle 002)

```
Follow-up to the AST-congruence claim about a Reasoning Ladder (R0 pattern response, R1 local
operation, R2 multi-step execution, R3 constraint maintenance; each rung has kill tests).
Status update: the v1 claim ("rung = coarseness of the AST congruence the circuit's key
respects") FAILED at R1 as predicted-fragile, and was amended:

CLAIM v2: For Band E (R0-R3, symbolic math), a circuit's rung is characterized by the triple
(congruence coarseness, witness arity, guard complexity):
- R0 = (identity congruence, no witnesses, no guard) — exact retrieval
- R1 = (template classes via alpha-renaming + literal slots, finite literal witnesses,
  quantifier-free guard on witnesses) — one guarded rule application; answer is a function of
  the witnesses, so the object is a FIBRATION over the congruence, not a congruence
- R2 (prediction, untested) = a pipeline of R1 fibrations where witnesses FLOW between
  stages along a supplied order; guard = conjunction of stage guards
- R3 (prediction) = R2 plus witnesses that accumulate as CONSTRAINT SETS checked globally

Questions:
1. Break v2 at R2: give the smallest concrete multi-step symbolic-math behavior (order
   SUPPLIED, so no planning) that cannot be written as witness-passing between guarded
   template rules. Candidates I suspect: intermediate expression GROWTH (witness arity not
   fixed), and rewriting under a binder. Are those genuine breaks or accommodations?
2. If witness-flow suffices for R2, the R2->R3 boundary becomes "witnesses become a
   monotonically growing constraint store consulted by later guards." Is that equivalent to
   saying R3 = R2 + a blackboard? What is the smallest R3 behavior that a blackboard-free
   pipeline provably cannot do?
3. For e-graph fans: at which rung does equality saturation become the NATURAL substrate
   rather than overkill? My guess is R2 (composition) — argue for or against in <=5 lines.
4. Name a trap for benchmark-gaming at R2 beyond: distractor-step insertion, step-order
   permutation with supplied order, and coefficient-hull escape. Something structural.
Terse; counterexamples over prose.
```
