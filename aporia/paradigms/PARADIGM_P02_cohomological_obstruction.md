# PARADIGM P02 — Cohomological Obstruction (worked example + decision tree + code skeleton)

Aporia P80, 2026-08-21. Source: `aporia/docs/attack_angle_taxonomy.md` P02. DR grounding:
none exists in BACKCORPUS for P02 (checked; not re-fired — the substrate sufficed).
Consumer: Learner corpus type C + catalog assignment. Template: P01's shape.

**The move**: detect global impossibility via local-to-global failure classes. If the
obstruction vanishes a solution may exist; if it is nonzero, THAT is the proof of
impossibility — absence becomes an object you can compute with (the verb is OBSTRUCT;
the payoff verb is CERTIFY-IMPOSSIBILITY-FINITELY).

## 1. Worked example — EXECUTED, three legs (`paradigm_p02_worked_example.py`)

- **A. The obstruction made countable.** g2c_curves 2×2 census of
  (locally_solvable, globally_solvable): **1,051 curves are everywhere locally
  solvable yet PROVEN to have no rational point** — the cell that only an
  obstruction class can populate. The logically impossible cell (global point,
  local failure) is empty (asserted, 0 rows). 718 undecided (encoding −1) counted
  separately, per the cardinality rule.
- **B. The exemplar verified at scale.** Cassels' pairing forces |Sha| square for
  elliptic curves: all **3,824,372** non-null `ec_curvedata.sha` values (39 distinct)
  pass an integer-sqrt check. Zero non-squares.
- **C. The refinement witnessed.** Poonen–Stoll: genus-2 Jacobian Sha may be twice
  a square. **2,284** g2c curves carry `has_square_sha = false`; sampled witnesses
  all show `analytic_sha = 2` — literally twice a square. The obstruction theory
  refines with the category, which is P01's lesson seen from the obstruction side.

Instrument note (recorded because it is the paradigm's own moral): the first run
mis-tallied leg A as obstructed=0 because `globally_solvable` is an INTEGER
(−1/0/1), not a boolean — the raw census printed the truth while the derived
number lied. Typed-value assumptions get verified against the raw distribution,
never assumed from column names.

## 2. Decision tree — WHEN to reach for P02

- Q1: Is the question an EXISTENCE question (point, solution, object)? — NO →
  P02 is the wrong shape; obstructions certify non-existence.
- Q1 YES → Q2: Does the object have LOCAL avatars (reductions mod p, completions,
  restrictions) that are cheap to check? — NO → no local-global ladder exists;
  consider P01 (translate until one exists).
- Q2 YES → Q3: Do ALL local checks pass? — NO → done: local failure is already
  the certificate (the cheap exit; 3,371 of our census rows end here).
- Q3 YES → Q4: Is there a computable obstruction GROUP between local and global
  (Brauer-Manin, Sha, Cassels-Tate class)? — NO → the local-global gap is
  unexplained; record the gap itself as residue (it is a void with a boundary —
  navigable, per the failure-vector doctrine) and park.
- Q4 YES → EXECUTE: compute the class; nonzero = finite certificate of global
  impossibility; zero = existence NOT proven (the converse needs its own theorem
  — the paradigm's classic over-read, guarded here).

## 3. Code skeleton

```python
def obstruction_attack(obj, local_checks, obstruction_class, converse_theorem=None):
    """P02 template. 1. Run ALL local checks (cheap, ordered by cost).
    2. Any failure -> NONEXISTENT with the failing place as certificate.
    3. All pass -> compute the obstruction class.
    4. Nonzero -> NONEXISTENT with the class as finite certificate.
    5. Zero -> existence is OPEN unless a converse theorem applies —
       NEVER promote vanishing obstruction to existence without one."""
    for place, check in local_checks:
        if not check(obj):
            return ("NONEXISTENT", f"local failure at {place}")
    cls = obstruction_class(obj)
    if cls != 0:
        return ("NONEXISTENT", f"obstruction class {cls}")
    if converse_theorem and converse_theorem.applies(obj):
        return ("EXISTS", converse_theorem.name)
    return ("OPEN", "obstruction vanishes; vanishing is not existence")
```

## 4. Catalog assignment (type C refinement)

Primary: CAT-MATH-0063 (BSD — Sha IS the obstruction group), 0026/0193
(uniformity — obstruction strata bound rational points), 0070/0071 (standard/Tate
conjectures — cycle-class obstructions), 0145 (Brumer-Stark units via class
groups). Secondary: 0137 (Agoh-Giuga's full conjunction is a congruence
obstruction battery), 0482 tranche B (genus theory = the abelianized obstruction).
Anti-assignment: distributional problems (0057, 0058, 0062, 0165, 0175) — nothing
to obstruct; density questions have no existence dichotomy (Q1 = NO).

## Provenance and honesty

All three legs certify settled theory against stored data (Cassels at 3.8M-row
scale is a data-integrity statement about the mirror as much as a theorem check).
The paradigm's transferable content is the decision tree's Q5 guard (vanishing ≠
existence) and the skeleton's refusal to promote zero classes — the over-read this
paradigm invites is exactly the one the tree forbids. The 1,051-curve obstruction
cell and the 2,284 Poonen-Stoll witnesses are ready-made example pools for the
Learner corpus.
