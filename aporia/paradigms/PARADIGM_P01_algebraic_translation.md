# PARADIGM P01 — Algebraic Translation (worked example + decision tree + code skeleton)

Aporia P79, 2026-08-21. Source: `aporia/docs/attack_angle_taxonomy.md` P01; grounding:
`aporia/docs/deep_research_reports/2026-05-19/00048_para_p01_modularity_lifting_2025.md`
(read, not re-fired). Consumer: Learner corpus type C + catalog assignment.

**The move**: reframe the problem in a richer algebraic category where tools are
sharper. The translation itself often CREATES computable objects from non-computable
ones — that creation is the paradigm's operational signature (verbs over nouns: the
verb is TRANSLATE, the payoff verb is COMPUTE-WHERE-YOU-COULD-NOT).

## 1. Worked example — EXECUTED, not narrated

Modularity as translation, run against our own mirror
(`paradigm_p01_worked_example.py`, results committed alongside):

- **Diophantine side** (poor category): #E(F_p) counted by brute enumeration of
  (x,y) pairs — no theory, O(p²) per prime, unscalable, but unimpeachable.
- **Automorphic side** (rich category): a_p = trace(T_p) fetched from
  `mf_newforms.traces` — a dataset built by an entirely independent pipeline
  (modular symbols, not point counting).
- **Result**: a_p = p + 1 − #E(F_p) matches `traces[p−1]` for ALL 94 good primes
  p ≤ 500 on BOTH 11.a2 (rank 0) and 37.a1 (rank 1). 188/188 exact.
  Verdict per pre-stated reading: **TRANSLATION-EXACT**.

What the example teaches (the type-C substrate lesson): after translation, the
hard question (rational points, BSD data) sits in a category where the objects
carry MORE structure (Hecke operators, L-functions, Galois representations) and
the previously-expensive quantity becomes a table lookup. The 2024-26 frontier
(report 00048) is exactly this move scaled up: Calegari-Geraghty lifts the
translation to positive-defect settings (abelian surfaces / GSp4, K3 via
Kuga-Satake) — same verb, richer categories.

## 2. Decision tree — WHEN to reach for P01

- Q1: Is the direct category computation-poor (enumeration explodes, no
  invariants to grip)? — NO → P01 is overhead; use direct methods.
- Q1 YES → Q2: Does a functor to a richer category EXIST with established
  transport (curve→newform, variety→Galois rep, knot→polynomial, sequence→
  generating function, problem→tensor embedding)?
  - NO → P01 is BLOCKED; the paradigm's failure mode is inventing an embedding
    with no inverse discipline (translation without faithfulness = wishful
    renaming). Consider P03 (symmetry) or P02 (obstruction) instead.
- Q2 YES → Q3: Is the functor FAITHFUL for your question (does the rich-side
  answer pull back)? Verify on known instances FIRST — the worked example's
  188-point check is the template; a translation unverified on knowns is a
  conjecture, not a tool.
- Q3 YES → Q4: Is the rich side COMPUTABLE (tables exist / algorithms
  polynomial)? — NO → you have translated one wall into another; record the
  translation anyway (it may compose with a future one), park the attack.
- Q4 YES → EXECUTE: compute rich-side, pull back, and ALWAYS spot-check the
  pullback against direct computation on small instances (the two-sided gate).

## 3. Code skeleton — the reusable translation-attack template

```python
def translation_attack(problem, functor, rich_compute, pullback,
                       known_instances, direct_compute):
    """P01 template. Every stage gates on the previous; no stage trusts memory.
    1. FAITHFULNESS GATE: for each known instance, rich-side answer must pull
       back to the direct answer EXACTLY (or within stated tolerance).
    2. TRANSLATE the live problem; 3. COMPUTE in the rich category;
    4. PULL BACK; 5. SPOT-CHECK pullback wherever direct computation is
       affordable. Emit a typed record either way."""
    for inst in known_instances:                      # stage 1 — the 188-point gate
        assert pullback(rich_compute(functor(inst))) == direct_compute(inst), \
            f"faithfulness FAILS at {inst} — translation unusable, record and halt"
    rich = rich_compute(functor(problem))             # stages 2-3
    answer = pullback(rich)                           # stage 4
    return answer                                     # stage 5 at call site
```

## 4. Catalog assignment (type C refinement)

P01 is the primary paradigm for: CAT-MATH-0063 (BSD — curve↔L-function is the
translation), 0130 (Langlands reciprocity — the paradigm's namesake territory),
0036 (Arthur — automorphic side), 0026/0193 (uniformity via Jacobians/modularity),
0334-class (volume conjecture: knot→quantum invariant). Secondary for: 0057/0058
(circle method IS a translation to exponential sums), 0332 (Jones→unknot).
Anti-assignment: pure-density problems (0479, 0483, 0484) — the direct category
is already computable; P01 adds nothing (decision tree Q1=NO).

## Provenance and honesty

The worked example demonstrates the paradigm on SETTLED mathematics (modularity
of 11a/37a is a theorem) — it certifies the INSTRUMENT and the two-sided gate
discipline, not new knowledge (feedback_instrument_vs_architectural_pass). Its
value to the Learner corpus is the executable template + the derived decision
tree, both of which now carry a 188/188 verification trace.
