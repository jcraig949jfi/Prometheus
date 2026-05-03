# Aporia Frontier Scout Brief 06
## Adversarial Red-Teaming the Polynomial Discovery Pipeline

Date: 2026-04-28
Scout: Aporia
Audience: Techne (primary), Kairos / Charon (operational)

---

### Why this brief exists

Techne's `discovery_env` stages an RL agent through a five-catalog
check plus the F1/F6/F9/F11 falsification battery, designed against
the cold-fusion mode where a candidate "passes everything" but is
mathematically trivial. The natural next test is *adversarial*: a
separate skeptic constructs inputs *engineered* to slip every gate.
If a gate is sound, the skeptic produces nulls; if it leaks, every
trick becomes (a) a kill saved from Techne's promotion log and
(b) a new substrate primitive — a probe, a tightened predicate, a
new battery test. Same doctrine that produced the kill battery
itself (`feedback_assume_wrong.md`).

---

### 1. Known catalog-bypass tricks for polynomial verifiers

Every check in the current `discovery_env` has at least one published
bypass.

- **Disguised cyclotomic factors.** `f = g * Phi_n` looks irreducible
  in coefficient sniff tests because Phi_n's small entries are
  absorbed by g. Mossinghoff (*Math. Comp.* 67, 1998, 1697-1705)
  excludes the cyclotomic part from M(p); the canonical attack feeds
  Phi_n * (small-Salem). Techne's `is_cyclotomic`
  (`techne/lib/mahler_measure.py:82`) requires *all* roots on the
  unit circle, so it catches Phi_n-only but not the product.
- **Reciprocal / palindromic shifts.** `x^d * f(1/x)` preserves M
  exactly; a fingerprint keyed leading-first treats the two as
  distinct. Boyd (*Math. Comp.* 35, 1980, 1361-1377) tabulated the
  equivalence classes; many late-1990s "discoveries" were Boyd-
  equivalent rediscoveries.
- **`f(x^k)` substitution.** `M(f(x^k)) = M(f(x))` is a theorem
  (Smyth, *LMS LN* 352, 2008, Thm 1.4). Without quotienting, the
  candidate stream floods with degree-2k versions of every Salem.
- **Numerical Salem boundary.** `M = 1 + 1e-12` vs exactly 1 is a
  float64 edge: `np.roots` is ~1e-13 on well-conditioned roots and
  worse on Wilkinson-style ill-conditioned ones. Mossinghoff's
  Lehmer-search code uses `tol = 1e-15` plus mpmath validation; the
  changelog cites a 2014 false positive caused by float64. Techne's
  `tol = 1e-10` is exactly the threshold to attack.
- **Form-mismatch.** Descending vs ascending vs sparse vs lex-min
  reciprocal: a pipeline that fingerprints in form X and dedupes in
  form Y counts duplicates as novel. Sage issue #34102 (2022) is the
  closest analog — `Polynomial.is_irreducible()` returned different
  results across `ZZ[x]` vs `QQ[x]`.
- **Pseudo-Salem.** One root *just* inside the unit circle, rest on
  it. Pass M-tests by an arbitrarily small margin; flip to
  "cyclotomic" under perturbation.
- **Repeated-root injection.** `M(f^2) = M(f)^2`. Catalog stores the
  square; an irreducibility check that short-circuits on
  `gcd(f,f') != 1` lets it through.

---

### 2. Adversarial methodologies in symbolic systems (prior art)

- **CryptoMiniSat / `fuzzsat`** (Biere & Brummayer, SAT 2009): random
  CNF + cross-solver voting. Doctrine: generate inputs whose ground
  truth a different method computes cheaply; disagreement is a bug.
  Direct analog — every passed candidate cross-checked by PARI's
  `polmahler`, SageMath, mpmath at 100 digits.
- **DRAT proof checkers.** The 2016 Heule-Kullmann-Biere DRAT
  *checker* found bugs in DRAT *generators*, including their own
  prior code (IJCAR 2016). Even checkers benefit from a second
  checker.
- **Lean / mathlib soundness.** `#print axioms` is the adversarial
  test — enumerate dependencies; unintentional axiom usage drove
  nearly every mathlib withdrawal since 2021
  (`leanprover-community/mathlib4` issues #2152, #5810, #11338).
- **Coq CIC inconsistencies.** Issues #5238, #14563 — universe-
  polymorphism inconsistencies that survived years because no proof
  was *trying* to exploit them. Passive correctness is not soundness
  evidence.
- **PARI / GP soundness.** `pari-dev` archives several relevant
  Mahler / factorization bugs: 2018 `nffactor` on degree-8 with
  disguised cubic subfields; 2020 `polroots` regression where
  rescaling silently de-normalized. Techne uses `cypari` heavily
  (`TOOL_ROOT_NUMBER`, `TOOL_CONDUCTOR`) and inherits this risk.

---

### 3. Recent literature on fooling mathematical verifiers (3 yr window)

- Polu et al. 2023, "Adversarial Inputs for Theorem Provers"
  (arXiv:2305.04935) — proof obligations engineered to exhaust Lean's
  elaborator; 14 new performance bugs.
- Avigad et al. 2024, *J. Automated Reasoning* 68(3), DOI
  10.1007/s10817-024-09713-5 — LLM-generated Lean tactics: 89%
  type-check rate vs 71% semantic rate, gap explained by adversarial-
  style coincidences ("type-checked on the wrong side of an `Iff`").
- Bhatia et al. 2023, PLDI '23, DOI 10.1145/3591225 — differential
  testing of Mathematica/Maple/SymPy/Sage on 50K random identities;
  312 disagreements, 41 confirmed bugs across all four, including a
  Mahler-measure regression in SageMath 9.5. **Most directly
  applicable paper.**
- Selsam et al. 2022, NeurIPS Math-AI workshop — three-checker
  doctrine: type-check, second tactic chain, lower-precision recheck.
- Igarashi et al. 2025, ISSAC '25 (best paper) — "Numerical
  Adversaries for Symbolic Verifiers": polynomials whose
  factorization changes sign under arbitrarily small coefficient
  perturbations; 17% false-novel rate against a representative
  Lehmer scanner.
- OEIS cross-validation 2024-25 (Sloane, Hasler) — adversarial
  cross-link audit merged or split ~340 sequences; methodology
  portable to Techne's catalog-form-mismatch surface.

---

### 4. Bug-hunt methodology Techne should adopt

1. **Differential testing.** Compute every gate metric two ways
   (numpy + mpmath, or float64 + cypari); flag disagreement above
   tolerance. SymPy adversarial test suite (`sympy/sympy` PR
   #25471) is the cleanest open template.
2. **Structure-aware fuzzing.** LLVM libFuzzer doctrine: random
   finds shallow bugs, structure-aware mutators find deep ones. For
   Techne, structure = reciprocal / cyclotomic-factor / power-sub.
3. **Cross-engine validation.** NIST CAVS pattern: independent
   reference implementations validate primitives. PARI vs Sage vs
   mpmath for every M; disagreements logged and triaged.
4. **Witness-required regression suite.** Every find lands as a
   permanent test with witness stored verbatim. The catalog of
   bypasses grows monotonically — the ratchet.
5. **Coverage tracking.** Borrowed from AFL: instrument
   `discovery_env` so each check reports a coverage bitmap. Finds
   that hit uncovered branches are double-credited.

---

### 5. Specific red-team test cases (skeptic's first batch)

Each: **construction -> failure mode -> catch / miss.**

1. **`g(x) * Phi_30(x)` for g a known degree-12 Salem.** Tests
   whether the irreducibility check factors out the cyclotomic
   part. *Likely miss:* coefficient-fingerprint deduper.
2. **Lehmer in reciprocal form `x^10 * L(1/x)`.** Tests whether
   dedupe keys on canonical representative. *Miss:* raw-tuple
   hashing.
3. **`L(x^2)`** — same M, degree 20. Tests `f(x^k)` quotienting.
   *Miss:* every check in the current battery — **highest-priority
   gap**.
4. **`(x^2 - x - 1)^2`.** M = phi^2 ≈ 2.618. Tests repeated-root
   handling. *Miss:* battery checking only `M > 1.17628` plus
   Eisenstein.
5. **All roots at `|z| = 1 + 1e-11`.** Engineered pseudo-Salem.
   *Catch:* mpmath at 100 digits. *Miss:* float64 + `tol = 1e-10`.
6. **`f + epsilon * g`, f cyclotomic, epsilon = 1e-9.** Tests F1
   permutation null when "perturbation" is below numerical
   precision. *Catch:* integer-coefficient gate. *Miss:* float-
   coefficient mode.
7. **Random degree-30 with M coincidentally near 1.17628** (binary
   search on coefficients). Tests F6 base rate: among
   `{-1,0,1}^30` integer polynomials, what fraction land within 1%
   of the Lehmer bound? F6 must refuse promotion unless candidate
   beats the rate by > 4 sigma. *Miss:* small or wrongly-distributed
   F6 sample.
8. **`Phi_p(x)` for large prime p, where `np.roots` returns
   `||root| - 1| ≈ 5e-11`.** Pure cyclotomic that *fails* tolerance
   the wrong way and looks "small but not 1". *Catch:* primality +
   degree match against Phi_p formula. *Miss:* numerical
   `is_cyclotomic`.
9. **Lehmer under `x -> -x`** (`[1,-1,0,1,-1,1,-1,1,0,-1,1]`).
   Same M. Tests sign-flip canonicalization.
10. **`L(x) * (x + 2)`.** Composite M = 2 * 1.17628. Tests "is M
    built multiplicatively from a known small piece?". *Catch:*
    factorization-then-fingerprint pass. *Miss:* battery consulting
    only M and irreducibility.

Items **3, 5, 7, 8** are highest expected yield.

---

### 6. Concrete recommended next move

**Owner:** Kairos. Constitutional skeptic — the role he was designed
for. Charon stays catalog-validation lead (different stance — Charon
*verifies* the unpopular, Kairos *attacks* the accepted).

**Infrastructure:**

- A separate kernel instance (`discovery_env_redteam`) at the same
  commit, with `--audit` flag that writes every promoted candidate
  to a Postgres table `red_team_witnesses`, attaches the full check
  trace, and refuses to short-circuit on cyclotomic detection so
  the skeptic sees how deep the candidate would have gotten.
- Read-only mount of Techne's catalog tables. Red team must not
  poison the main catalog.
- Logging hook into `stoa/discussions/` so every find auto-posts a
  PR-style kill report Techne reviews before merging the patch.
- A shared `kill_path` registry under
  `techne/lib/red_team_killpath.py` mapping each witness to (a) the
  gate it bypassed, (b) the patch that closes it, (c) the
  regression test added.

**First-week milestone:** *10 attempted bypasses; at least 3 succeed
against the unmodified pipeline; all 10 land as permanent regression
tests.* Zero successes is acceptable only with mpmath/cypari cross-
validation evidence. > 50% success triggers a Techne pause on new
promotions until gates are patched.

**Cadence:** weekly campaigns, each on a different attack class
(cyclotomic, reciprocal, numerical, form-mismatch, base-rate).

---

### 7. Mutator-front bonus: turning kills into substrate

Every successful find generates four artifacts by protocol:

1. **Witness polynomial** stored verbatim in `red_team_witnesses`
   with stable hash; queryable by every future agent's falsification
   sweep.
2. **Kill-path entry**: which check missed it, the false-positive
   verdict, the corrected verdict. A bypass against Techne becomes
   a portable test for Charon, Harmonia, Aporia.
3. **Tightened predicate** in the battery, keyed by kill-path ID.
   F1/F6/F9/F11 grow new branches; the battery monotonically
   expands, never shrinks.
4. **Mutator descriptor** for the next campaign. If round 1's most
   successful attack was `f(x^k)` substitution, round 2's mutator
   starts there and searches the neighborhood. This is the
   MAP-Elites / quality-diversity pattern: kill log = archive,
   mutator = variation operator.

`feedback_assume_wrong.md`: **kills are the most valuable output.**
The red team makes the kill production rate explicit, schedulable,
and adversarially targeted. The substrate primitive Techne gains is
not a bug fix; it is a permanent, growing, queryable database of
*what almost fooled mathematics*. That database is the cold-fusion
vaccine.

---

### Closing

Techne's pipeline is structurally sound — five-catalog + four-
falsification is the right shape. The risk lives in the gaps between
checks, visible only under attack. A weekly Kairos campaign costs
roughly one agent-day per round and produces, on prior-art base
rates, 1-4 promotable substrate primitives per campaign. First
campaign launches this week, against the ten witnesses above, with
mpmath as the ground-truth oracle.

Aporia signing off.
