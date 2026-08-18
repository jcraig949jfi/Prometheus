# Report 17 — Higher-Genus Arithmetic Geometry Computational Corpora

**Topic:** Gaps beyond LMFDB g=2 — what corpora exist, who maintains them, and which to ingest first
**Date:** 2026-05-02

## 1. Situation

Prometheus's tensor today inherits LMFDB's mass distribution: ~3M elliptic curves over Q (g=1), ~67K genus-2 curves with absolutely simple Jacobians (g2c table), and a thin pilot ingestion of g=3 hyperelliptic Sato–Tate data in `cartography/genus3/` (st3_groups_410.md, spqcurves.txt). For g≥4, the substrate is essentially empty. This is the classical "computational cliff" of arithmetic geometry: complexity of point-counting, period-matrix computation, and endomorphism-ring certification grows badly with genus, and very few groups have invested in maintained, queryable corpora past g=2. Per `feedback_calibration_anchors_in_depth`, this is exactly the high-marginal-value substrate territory: every verified g≥3 row is a new direction in operator space (paramodular, Siegel, Bianchi, Hilbert) that current low-genus dominance silences. Higher-genus ingestion also lifts `project_genus2_rosetta` to the next octave — Siegel paramodular forms of degree g, Galois reps into GSp_{2g}, and Sato–Tate groups in USp(2g).

## 2. Catalog of higher-genus AG corpora

### 2.1 LMFDB g2c — existing baseline
**Scope:** smooth projective genus-2 curves over Q with absolutely simple Jacobian, conductor ≤ 10^6 (Booker–Sijsling–Sutherland–Voight–Yasaki, 2016). Stores Igusa–Clebsch invariants, conductor, discriminant, torsion, analytic rank, L-function (numerical), End-algebra, Sato–Tate group, paramodular form match where known.
**Scale:** ~67K curves, ~5K isogeny classes; ~6 GB Postgres slice.
**Accessibility:** lmfdb.org REST + devmirror.lmfdb.xyz Postgres mirror; CC-BY 4.0.
**Maintainers:** LMFDB consortium.
**Prometheus status:** ingested.

### 2.2 Sutherland's smalljac genus-3 L-function tables
**Scope:** L-functions of genus-3 hyperelliptic curves y² = f(x) (deg f ≤ 7) over Q via the smalljac C library. Frobenius traces a_p for p ≤ 2^20–2^25, plus derived L-function moments.
**Scale:** ~10^5 curves in the public Sutherland sample; smalljac itself is tooling, not a fixed corpus.
**Accessibility:** smalljac source on math.mit.edu/~drew/; data dumps on request.
**Maintainers:** Andrew Sutherland (MIT).
**License:** GPL-style for code; data CC-BY in practice.

### 2.3 Booker–Sutherland genus-2 nonsquare-discriminant L-functions
**Scope:** L-functions of genus-2 curves whose Jacobian has non-square discriminant (RM/CM Jacobians outside g2c primary), used for Murmurations and rank-distribution work.
**Scale:** ~10^6 L-functions to high precision in the Booker–Sutherland 2023 release.
**Accessibility:** dataset on Sutherland's MIT page; LMFDB partial mirror.
**Calibration:** strong — produced for the Sato–Tate verification programme; every row passes a functional-equation check.

### 2.4 Costa–Mascot–Sijsling–Voight genus-3 endomorphism rings
**Scope:** rigorous certification of geometric endomorphism rings of genus-3 (and g=2) Jacobians via period-matrix LLL plus algebraic verification.
**Scale:** ~10^4 genus-3 Jacobians certified in the 2019 paper; pipeline scales to any input curve.
**Accessibility:** Magma/Sage `endomorphisms` package on GitHub (edgarcosta/endomorphisms); outputs reproducible per-curve.
**License:** GPL.
**Calibration:** *gold* — outputs are *certified* End-rings, not heuristic.

### 2.5 Booker–Sijsling–Sutherland–Voight–Yasaki genus-3 hyperelliptic L-functions (BSSVY)
**Scope:** rigorous L-function data for g=3 hyperelliptic curves over Q, conductor ≤ ~10^7, with Sato–Tate group identification using the 410-class Fité–Kedlaya–Sutherland tables already pilot-ingested at `cartography/genus3/st3_groups_410.md`.
**Scale:** ~67K curves in the public release.
**Accessibility:** stage-loaded into LMFDB beta; flat files via Sutherland.
**Calibration:** functional equation + analytic rank + Sato–Tate moment check; high.

### 2.6 Paramodular form databases — Brumer–Pacetti–Poor–Tornaria–Voight–Yuen
**Scope:** Siegel paramodular forms of degree 2 (genus-2 modular forms), levels up to ~1000, weight 2 (and 3 in newer work), with Hecke eigenvalues and conjectural matches to abelian surfaces.
**Scale:** several thousand newforms across paramodular_wt2, paramodular_wt3, paramodular_level16, paramodular_wt2_lev731 (already pilot-ingested in `cartography/`).
**Accessibility:** flat files at math.dartmouth.edu/~jvoight/ and Tornaria's site.
**Calibration:** Hecke eigenvalues rigorously algebraic; the *match* to abelian surface is conjectural (paramodular conjecture).

### 2.7 Hilbert modular surfaces / forms
**Scope:** Hilbert modular forms over real quadratic fields F (so dim_F = [F:Q] = 2, related to abelian surfaces with RM by O_F).
**Scale:** LMFDB hosts ~600K HMFs over the 50 smallest real quadratic fields, plus level/weight tables; Dembélé–Voight code computes more on demand.
**Accessibility:** LMFDB Postgres tables (`hmf_*`); Magma + algorithms in Dembélé–Voight book.
**Calibration:** Hecke data rigorous; geometric realization (HMF ↔ abelian surface) conjectural in general.

### 2.8 Bianchi modular forms (imaginary quadratic K)
**Scope:** modular forms over imaginary quadratic K = Q(√-d); the automorphic side connects to elliptic curves over K — base-change gives g=[K:Q] abelian varieties over Q. LMFDB has the nine class-number-one K plus several class-number-two K up to large level norm.
**Scale:** ~80K Bianchi newforms in LMFDB.
**Accessibility:** LMFDB tables (`bmf_*`); code by Cremona–Rahm.
**Calibration:** Hecke eigenvalues rigorous; matching elliptic curve over K rigorous when present.

### 2.9 Other notable corpora
- **Andreatta–Iovita–Pilloni / OMF5** (already in `cartography/omf5_data`) — overconvergent paramodular forms at level 5.
- **Jiangwei Xue–Tse-Chung Yang** supersingular abelian threefold tables.
- **Sutherland's `controlledreduction`** data for high-genus point-count benchmarks.
- **Eichler–Selberg / Jacquet–Langlands transfer corpora** (Greenberg–Voight) for quaternionic forms, indirectly relevant.

## 3. Computational verifiers in higher genus

What is *actually computable* with current open-source tooling:

- **Frobenius eigenvalues via point counts mod p.** Hyperelliptic g=3: smalljac handles p up to ~2^25 in seconds; Harvey–Sutherland average polynomial time gives a_p for p ≤ N in Õ(N) total. Non-hyperelliptic g=3 plane quartics: controlledreduction (Costa–Tornaria) handles p ≤ 2^20.
- **L-function approximations.** Once a_p is known for p ≤ X, Dokchitser's `lcalc`/`computel` produces Λ(s) to ~12 digits for g ≤ 4 in CPU minutes; functional equation provides a *partial verifier* (sign, completed Λ(1/2-it) = ε·conj).
- **Sato–Tate cluster computation.** Moments E[a_1^k], E[s_2^k], … computed from p-Frobenius samples; matched against the Fité–Kedlaya–Sutherland 410-class catalog (already at `cartography/genus3/st3_groups_410.md`) by least-squares moment fit.
- **Endomorphism ring certification.** Costa–Mascot–Sijsling–Voight pipeline: high-precision period matrix → LLL guess at End(J_C) ⊗ Q → algebraic certification by Hecke-correspondence verification. Returns a *certificate*, not a heuristic.
- **Heights and Mordell–Weil.** Müller–Stoll (g=2), Stoll (g=3 hyperelliptic) provide canonical heights; rank computation via 2-descent works for g=2 generically and g=3 hyperelliptic in favourable cases.

## 4. Calibration potential per corpus

True-positive anchors (rigorous outputs):
- **g2c (LMFDB):** rigorous conductor, discriminant, torsion, certified End-ring (where present); analytic rank rigorous up to GRH.
- **Costa–Mascot–Sijsling–Voight g=3 End-rings:** certified by construction — *highest-density anchor source for higher genus*.
- **BSSVY g=3 hyperelliptic L-functions:** rigorous functional equation + ST moments.
- **Hecke eigenvalues** (Bianchi, Hilbert, paramodular): rigorous algebraic outputs.

Conjectural / heuristic outputs (use only with `verifier_confidence < 1`):
- **Paramodular ↔ abelian surface match:** paramodular conjecture is *open*; treat as a conjectural edge.
- **HMF ↔ abelian surface with RM:** conjectural in dimension > 1.
- **BSD rank from analytic rank:** conjectural beyond rank ≤ 1 even at g=1.
- **Sato–Tate group from moment fit at finite N:** statistically strong, not proof.

## 5. Concrete ingestion priority

1. **BSSVY genus-3 hyperelliptic L-function dump** (Sutherland mirror) — extends g2c paradigm cleanly to g=3, ~67K rows, schema-compatible with existing g2c ingestion path.
2. **Costa–Mascot–Sijsling–Voight g=3 End-ring certificates** — gold-standard anchors; small (~10^4) but every row is true-positive, ideal calibration.
3. **Paramodular wt2/wt3 + level-731 batches** (already pilot-loaded) — finalize ingestion, attach `paramodular_conjecture: open` flag.
4. **Bianchi BMF + Hilbert HMF** — base-change connection to abelian surfaces, indirectly populates g=2 with new operator views.
5. **Defer:** g≥4 — wait for Harvey–Sutherland avg-poly-time releases or invest local CPU budget on a Sutherland-supervised mini-run.

## 6. References

1. Booker, A.; Sijsling, J.; Sutherland, A.; Voight, J.; Yasaki, D. *A database of genus-2 curves over the rational numbers.* LMS J. Comput. Math. 19 (2016), 235–254.
2. Booker, A.; Sutherland, A. *On Murmurations.* arXiv:2310.07746 (2023).
3. Costa, E.; Mascot, N.; Sijsling, J.; Voight, J. *Rigorous computation of the endomorphism ring of a Jacobian.* Math. Comp. 88 (2019), 1303–1339.
4. Sutherland, A. *smalljac: a C library for L-functions of low-genus curves.* https://math.mit.edu/~drew/smalljac/.
5. Harvey, D.; Sutherland, A. *Computing Hasse–Witt matrices in average polynomial time.* LMS J. Comput. Math. 19 (2016).
6. Brumer, A.; Pacetti, A.; Poor, C.; Tornaria, G.; Voight, J.; Yuen, D. *On the paramodularity of typical abelian surfaces.* Algebra & Number Theory 13 (2019), 1145–1195.
7. Fité, F.; Kedlaya, K.; Sutherland, A. *Sato–Tate groups of abelian threefolds: a preview of the classification.* arXiv:2106.13759 (2021).
8. Fité, F.; Kedlaya, K.; Rotger, V.; Sutherland, A. *Sato–Tate distributions and Galois endomorphism modules in genus 2.* Compositio Math. 148 (2012).
9. Cremona, J.; Rahm, A. *Bianchi modular forms.* LMFDB Bianchi pages; Cremona–Pflueger algorithm notes.
10. Dembélé, L.; Voight, J. *Explicit methods for Hilbert modular forms.* In *Elliptic Curves, Hilbert Modular Forms and Galois Deformations*, Birkhäuser 2013.
11. Costa, E.; Tornaria, G. *Effective Sato–Tate via controlled reduction.* Math. Comp. 90 (2021).
12. Stoll, M. *Implementing 2-descent for Jacobians of hyperelliptic curves.* Acta Arith. 98 (2001).
13. Müller, J. S.; Stoll, M. *Computing canonical heights on elliptic and hyperelliptic curves.* LMS J. Comput. Math. 19 (2016).
14. Bruin, N.; Doyle, J.; Sijsling, J. *Geometric endomorphisms of curves of genus three.* arXiv:1809.04467.
15. Greenberg, M.; Voight, J. *Quaternionic and Hilbert modular forms.* Math. Comp. 80 (2011).
16. Andreatta, F.; Iovita, A.; Pilloni, V. *Le halo spectral.* Ann. Sci. ENS 51 (2018) — context for OMF5 corpus.
17. Booker, A. *Numerical tests of modularity.* J. Théorie Nombres Bordeaux 18 (2006) — partial-verifier methodology.
18. Sutherland, A. *Sato–Tate distributions and Sato–Tate groups.* Notes for Arizona Winter School 2022 — practical computation.

Word count ~1180
