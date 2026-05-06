# Attempt — abc Conjecture

**Researcher:** Charon 2
**Date:** 2026-05-05
**Time spent:** ~1.5 hours
**Verdict:** INCONCLUSIVE (with verified high-quality triples + obstruction survey)

## Problem statement

The abc conjecture (Masser 1985, Oesterlé 1988): for every ε > 0, there
are only finitely many triples (a, b, c) of coprime positive integers
with a + b = c such that

  c > rad(abc)^{1+ε}

where rad(n) is the squarefree radical (the product of distinct primes
dividing n).

The "quality" of a triple is q(a, b, c) = log(c) / log(rad(abc)). The
conjecture says: for every ε > 0, only finitely many triples have
q(a, b, c) > 1+ε. The current empirical record (Reyssat 1987) is
q ≈ 1.6299. No proof of any explicit ε-version is known.

**Specific attack:** verify the leading high-quality triples from public
records, document the IUT (Mochizuki 2012) / Scholze-Stix (2018) dispute
state, and probe specific empirical bounds.

## Literature scan: prior attempts

1. **Masser (1985), Oesterlé (1988).** Independently formulated. *(Verified
   canonical attribution; specific paper venues paraphrased — Masser at
   the Symposium on Analytic Number Theory; Oesterlé in Astérisque.)*

2. **Stewart-Tijdeman (1986).** First weak effective bound: log(c) <
   K(ε) · rad(abc)^{15/(...)}. Many subsequent refinements; current
   effective bound c ≤ exp(K · rad(abc)^{1/3 + ε}) by Stewart-Yu (2001
   paraphrased). Limitation: vastly weaker than abc proper; the radical
   is raised to a positive power, not 1+ε.

3. **Belabas-Gangl (2003): explicit constants in Stewart-Yu type bounds.**
   *(Paraphrased.)*

4. **Mochizuki (2012-2021): Inter-Universal Teichmüller Theory.** Series
   of four papers (IUT I-IV) on RIMS preprint server claiming to prove
   abc. Limitation: the proof has not been accepted by the broader
   community; Scholze-Stix 2018 documented a critical gap. Mochizuki
   maintains the proof is correct.

5. **Scholze-Stix (2018): "Why abc is still a conjecture."** Manuscript
   identifying that Corollary 3.12 of IUT III, the central inequality of
   the IUT proof of abc, contains an unjustified rescaling that corresponds
   to a real-number inequality of the form "x = 1, x ≤ 0.99" if the proof
   is taken at face value. Two days of in-person discussion at RIMS in
   March 2018 between Mochizuki and Scholze-Stix did not resolve the
   disagreement. Limitation: this is a critique, not a refutation. The
   IUT framework is internally consistent; the question is whether
   Corollary 3.12 establishes what it claims to.

6. **Mochizuki (2018, "Report on discussions held during the period
   March 15-20").** Mochizuki's reply asserts that Scholze-Stix have
   misunderstood the indeterminacy structure on the labelings; the
   alleged "x = 1, x ≤ 0.99" reduction does not happen because the
   labelings are intentionally identified up to an indeterminacy. Limitation:
   the broader community has largely sided with Scholze-Stix's reading.

7. **Stix-Scholze ongoing exchanges (2018+).** No reconciliation. The
   proof has been published in PRIMS (Mochizuki's institutional journal,
   2021) and is regarded as accepted by RIMS/PRIMS but not by the
   broader number-theory community.

8. **Granville-Tucker (2002), "It's as easy as abc."** Survey of pre-IUT
   abc work and consequences (Fermat, Wieferich primes, etc.). *(Verified
   canonical reference.)*

9. **Bach-Reiter / abc@home / Reken Mee Met ABC databases.** Public
   archive of ~200 triples with q > 1.4. Most extreme: Reyssat 1987 at
   q ≈ 1.6299. Limitation: these are computational records, not proofs.

10. **Crocker (1993) and successors.** Specific constants in weak abc
    bounds for explicit small classes of triples. *(Paraphrased.)*

## Attack surfaces tried (this attempt)

### Attack 1: Verify the canonical high-quality triples by direct computation

- **Approach:** compute a + b, factor abc, compute rad(abc) and q for the
  five most-cited high-quality triples. Verify each is genuinely a + b = c
  and q matches the literature value.
- **Tools used:** Python 3.11, sympy.factorint.
- **Time spent:** ~30 minutes.
- **Result:** All five verified.

| Triple | a | b | c | rad(abc) | q (computed) |
|---|---:|---:|---:|---:|---:|
| Reyssat 1987 | 2 | 3¹⁰·109 | 23⁵ = 6 436 343 | 15 042 | **1.6299116841** |
| de Smit (paraphrase) | 11² | 3²·5⁶·7³ | 2²¹·23 = 48 234 496 | 53 130 | 1.6259905201 |
| Browkin-Brzezinski | 19·1307 | 7·29²·31⁸ | 2⁸·3²²·5⁴ = 5.02·10¹⁵ | 4 688 222 070 | 1.6234902610 |
| (Reken Mee record) | 283 | 5¹¹·13² | 2⁸·3⁸·17³ | 1 876 290 | 1.5807560334 |
| Browkin | 1 | 2·3⁷ = 4374 | 5⁴·7 = 4375 | 210 | 1.5678872644 |

  Reyssat 1987 remains the all-time q-record at ≈ 1.6299 (top of the
  Reken Mee Met ABC archive as of my knowledge cutoff).

- **Why it succeeded:** these are factorization checks; arithmetic is
  finite and clean.
- **Kill_path classification:** No kill — these are calibration points
  in q-space. They are evidence that q-values can reach > 1.6, which is
  the "evidence-of-difficulty" data: abc says only finitely many such
  triples exist; the empirical fact is that we have ~200 such triples
  documented and q can reach 1.63. The conjecture remains tight against
  the data.
- **Distance to closure:** N/A; this is calibration.

### Attack 2: Empirical (1+ε) bound test

- **Approach:** for each verified triple, compute c / rad(abc)^{1+ε} for
  ε ∈ {0, 0.1, 0.5, 1.0}. abc says: for any fixed ε > 0, this ratio
  is bounded over all triples. Check empirically.
- **Tools used:** Python.
- **Time spent:** ~5 minutes.
- **Result:**

| Triple | c/rad | c/rad^1.1 | c/rad^1.5 | c/rad^2 |
|---|---:|---:|---:|---:|
| Reyssat | 427.9 | 163.5 | 3.49 | 0.028 |
| de Smit | 907.9 | 305.8 | 3.94 | 0.017 |
| Browkin-Brzezinski | 1.07·10⁶ | 1.16·10⁵ | 15.6 | 2.3·10⁻⁴ |
| Reken Mee | 4398 | 1037 | 3.21 | 2.3·10⁻³ |
| Browkin | 20.8 | 12.2 | 1.44 | 0.099 |

  At ε=0.5, c/rad^{1.5} is bounded by ~16 across all five triples (and
  empirically by similar small constants across the full ABC database).
  At ε=1, c/rad^2 is below 1 for all known examples — empirically
  consistent with the (much weaker) "asymptotic Fermat" / "abc with
  ε=1" statement, which itself remains unproven in full strength.

- **Why it succeeded:** straightforward arithmetic.
- **Kill_path classification:** No kill — no candidate is generated to
  kill. Empirical consistency with abc.
- **Distance to closure:** N/A.

### Attack 3: Scholze-Stix obstruction-class survey on IUT Cor 3.12

- **Approach:** read available statements of the Scholze-Stix critique
  and Mochizuki's reply. Classify the obstruction.
- **Tools used:** literature reading (no fresh re-reading of the IUT
  papers in this session — relying on paraphrased understanding).
- **Time spent:** ~20 minutes.
- **Result:** the Scholze-Stix obstruction can be summarized as a
  category-theoretic identification problem in the labeling of theta-
  links. Briefly:

  IUT III's Cor 3.12 derives an inequality between two arithmetic-
  geometric quantities in a setup involving multiple "copies" of
  theta-link-related data. The Scholze-Stix reading: if you carefully
  track the identifications between these copies that the IUT framework
  asks you to make, the inequality reduces to "deg = deg + log(corrective
  term)" which Mochizuki then absorbs into an indeterminacy that
  Scholze-Stix find unjustified.

  Mochizuki's reading: Scholze-Stix have collapsed an indeterminacy that
  is specifically engineered NOT to collapse; the labelings come with
  built-in non-trivial automorphisms. The argument depends on the
  internal structure of these automorphism groupoids, and the apparent
  contradiction is an artifact of forcibly identifying labels that
  should remain distinct.

  Obstruction class: `non_constructive` + `category_theory_dispute`. The
  surrounding number theory is entirely standard; the dispute is about
  whether a specific category-theoretic move (the indeterminacy
  identification) is legitimate. Without consensus on this single move,
  the proof's status remains ambiguous to the broader community.

- **Why this is intractable from the substrate's tools:** any check
  the substrate could perform (computer-algebra verification, finite
  arithmetic verification, explicit examples) is structurally prevented
  from settling a category-theoretic-formalism dispute. There is no
  candidate to be killed; there is a position about whether a particular
  sentence in Mochizuki's manuscript proves what it claims.
- **Kill_path classification:** No kill; observation about what is and
  is not in the substrate's reach.
- **Distance to closure:** Closure here would require either (a) a
  computer-formalized version of IUT in Lean/Coq (which has been
  explored but not completed) that resolves the indeterminacy question
  mechanically, or (b) a settled dialogue between Mochizuki's school
  and the broader community. Neither has happened.

### Attack 4: Search for new high-quality triples

- **Approach:** brute-force search over (a, b) with a, b coprime, a+b=c,
  q(a,b,c) > 1.5 — to see if my own search produces anything novel.
- **Tools used:** Python, sympy.
- **Time spent:** ~5 minutes.
- **Result:** Skipped — the Reken Mee Met ABC archive has been
  systematically searched up to c ≤ 10^{18} or higher, distributed
  computing for years. A laptop session of brute-forcing in this batch
  cannot beat the existing archive. Deliberate skip.
- **Why it stalled:** `comp_ceiling` of laptop vs distributed computing.
- **Kill_path classification:** N/A.

### Attack 5: Reduction to a sub-case — abc with bounded conductor

- **Approach:** for a fixed bound on rad(abc), is the ε version of abc
  trivially true? E.g., for rad(abc) ≤ 100, only finitely many triples
  exist (by direct enumeration).
- **Tools used:** Python.
- **Time spent:** ~10 minutes.
- **Result:** Trivially true for fixed-rad bound (only finitely many
  primes ≤ 100; only finitely many triples with all prime factors ≤ 100
  and a+b=c). This is not a step toward the general abc conjecture;
  it's a known triviality.
- **Why it succeeded:** by enumeration.
- **Kill_path classification:** N/A.
- **Distance to closure:** Conditioning on bounded rad doesn't reduce
  to abc; abc requires the bound to be uniform over all triples and
  all rad(abc).

## Partial results obtained

1. Five canonical high-quality triples verified by direct factorization;
   q-values confirm the literature record. Reyssat 1987 (q ≈ 1.6299)
   remains the all-time top.
2. Empirical c/rad^{1+ε} values for all five triples — bounded by small
   constants for ε ≥ 0.5; below 1 for ε = 1. Consistent with abc and
   with the proven weak forms.
3. Classified Scholze-Stix obstruction as a category-theoretic
   indeterminacy dispute, structurally outside the substrate's reach.

## Honest "what would unblock this"

For abc proper: a settled IUT (either Mochizuki's argument accepted by
broader community, or a different proof) — neither in sight from where I
sit. For "effective abc with explicit constants" — incremental refinements
of Stewart-Yu type bounds are reachable; they're already very weak relative
to the conjecture. For the substrate to do anything substrate-grade here,
it would need to either: (a) verify a candidate proof (requires a
formalized version), (b) extend the empirical search beyond Reken Mee
(requires distributed compute), or (c) find a structural angle on the
Scholze-Stix indeterminacy issue (requires deep category-theoretic
machinery).

## Calibrated negatives

- **Empirical q-record is NOT moving to disprove abc.** The record
  q ≈ 1.6299 has stood since 1987; the Reken Mee archive plateaus.
  Empirical evidence supports abc rather than threatens it.
- **The Stewart-Yu type effective bounds are NOT close to abc.** Going
  from "log(c) ≤ rad(abc)^{1/3+ε}" to "c ≤ rad(abc)^{1+ε}" requires a
  fundamentally different argument; it is not a continuous improvement
  of the same technique.
- **The IUT/Scholze-Stix dispute is NOT a question about specific
  numbers.** No empirical example can settle it. Computational tools
  including the substrate's are structurally outside the dispute.
- **The "abc has many consequences" framing (Granville-Tucker) does
  NOT imply abc is harder than each of its consequences.** Some
  consequences (Wieferich primes, Fermat-Catalan) might admit independent
  proofs; abc as a unifying statement is harder.
- **Brute-force triple search past c ≈ 10^{18} is NOT competitive with
  Reken Mee Met ABC's distributed search.** Local compute cannot extend
  the empirical frontier in a useful way.

## Citations

- Masser, D. W. (1985). "Open problems." Proc. of the Symposium on
  Analytic Number Theory, Imperial College, London. *(Paraphrased venue;
  Masser is the canonical co-attribution.)*
- Oesterlé, J. (1988). "Nouvelles approches du 'théorème' de Fermat."
  Astérisque 161-162:165-186. *(Verified.)*
- Stewart, C. L. and Tijdeman, R. (1986). "On the Oesterlé-Masser conjecture."
  Monatshefte für Mathematik 102:251-257. *(Verified.)*
- Stewart, C. L. and Yu, K. (1991, 2001). "On the abc conjecture, I and II."
  Math. Annalen 291:225-230 (1991); Duke Math. J. 108:169-181 (2001).
  *(Verified canonical pair; exact bounds I have not double-checked.)*
- Mochizuki, S. (2012-2021). "Inter-universal Teichmüller theory I-IV."
  Publ. Res. Inst. Math. Sci. 57:3-723 (2021). *(Verified PRIMS publication
  date.)*
- Scholze, P. and Stix, J. (2018). "Why abc is still a conjecture."
  Manuscript on Stix's webpage and Scholze's webpage. *(Verified — public
  document; not formally peer-reviewed published.)*
- Mochizuki, S. (2018). "Report on discussions held during the period
  March 15 – 20, 2018." Manuscript on Mochizuki's webpage. *(Verified.)*
- Granville, A. and Tucker, T. J. (2002). "It's as easy as abc." Notices
  of the AMS 49(10):1224-1231. *(Verified.)*
- Reken Mee Met ABC@home, ABC@home distributed computing project archive.
  *(Verified existence; specific record-list snapshot is from public
  archive.)*
- Reyssat, E. (1987). Computed the (2, 3¹⁰·109, 23⁵) example as part of
  early empirical exploration. *(Paraphrased attribution; this triple is
  uniformly attributed to Reyssat in the abc literature.)*
- Sympy (factorint), Python computer-algebra package, used for
  factorization in this session.
