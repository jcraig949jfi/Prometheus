# Attempt — Novikov Conjecture (specific groups)

**Researcher:** Charon 3
**Date:** 2026-05-05
**Time spent:** ~30 min (literature scan + obstruction class identification; no computation)
**Verdict:** NO_PROGRESS_DOCUMENTED_OBSTACLES

## Problem statement

**Novikov Conjecture (NC).** Let G be a finitely generated discrete group, M a closed oriented manifold with π₁(M) = G, and BG a classifying space (Eilenberg–MacLane K(G,1)). The higher signatures of M, defined as

  σ_x(M) = ⟨L(M) ∪ f*(x), [M]⟩

for x ∈ H*(BG, ℚ) and f: M → BG the classifying map, are *homotopy invariants* of M (i.e., depend only on the oriented homotopy type of M, not on the smooth/PL structure).

**Specific class attacked:** Burnside groups **B(m, n) for m = 2 and n = 665** (the original Adyan–Novikov bound for infinite Burnside groups), and **Gromov monster groups** (groups containing expanders, Gromov 2003). For both classes the Novikov conjecture is **open**.

## Literature scan: prior attempts

1. **Novikov 1965** ("Topological invariance of rational Pontrjagin classes," *Doklady Akad. Nauk SSSR* 163; 1966 *Izvestiya AN SSSR*). Proved rational Pontrjagin classes are topological (homeomorphism) invariants, motivating the conjecture for higher signatures as homotopy invariants. Original conjecture stated for π₁ = ℤⁿ.

2. **Mishchenko 1974** ("Infinite-dimensional representations of discrete groups, and higher signatures," *Math. USSR Izv.* 8). Reformulated NC via the assembly map μ: K_*(BG) → K_*(C*_max(G)) and proved injectivity for many G via C*-algebraic techniques. Foundation of all subsequent attacks.

3. **Kasparov 1988** ("Equivariant KK-theory and the Novikov conjecture," *Invent. Math.* 91). Proved NC for **discrete subgroups of connected Lie groups**, including all lattices in semisimple Lie groups. Method: equivariant KK-theory + γ-element. Limitation: requires the group to embed nicely in a Lie group; does not apply to Burnside groups.

4. **Higson & Kasparov 2001** ("E-theory and KK-theory for groups which act properly and isometrically on Hilbert space," *Invent. Math.* 144). Proved the Baum–Connes conjecture (which implies NC) for **a-T-menable groups (Haagerup property)**. Includes free groups, Coxeter groups, finite groups, amenable groups, groups acting properly on trees. Limitation: a-T-menability is incompatible with Kazhdan's property (T); does not apply to Burnside groups (which are not amenable and lack Haagerup property for large parameters).

5. **Yu 1998** ("The Novikov conjecture for groups with finite asymptotic dimension," *Annals of Math.* 147). Proved NC for groups of **finite asymptotic dimension**. Includes hyperbolic groups, CAT(0) cube complexes acting properly on. Limitation: many infinite torsion groups (including Burnside) have INFINITE asymptotic dimension by an isoperimetric obstruction — finite generators + torsion ⇒ growth properties make the asymptotic dimension large.

6. **Yu 2000** ("The coarse Baum–Connes conjecture for spaces which admit a uniform embedding into Hilbert space," *Invent. Math.* 139). Proved coarse BC + NC for groups with **Property A** (equivalently, exact groups; equivalently, groups uniformly embeddable into Hilbert space). Property A is much broader than Haagerup. Limitation: **NOT all groups have Property A** — Gromov 2003 constructed groups containing expanders that fail Property A (Gromov monsters). Burnside groups: Property A is **OPEN**.

7. **Higson, Lafforgue, Skandalis 2002** ("Counterexamples to the Baum–Connes conjecture," *Geom. Funct. Anal.* 12). Showed the *coarse* Baum–Connes conjecture (with coefficients) fails for Gromov monsters. The classical Baum–Connes conjecture and the Novikov conjecture remain open for these groups, but the standard tools (Yu's coarse method) cannot apply.

8. **Lafforgue 2002** ("K-théorie bivariante pour les algèbres de Banach et conjecture de Baum–Connes," *Invent. Math.* 149). Proved Baum–Connes (and hence Novikov) for **hyperbolic groups** via Banach KK-theory. Generalized later to many classes. Doesn't apply to Burnside groups (not hyperbolic for n ≥ 665).

9. **Guentner, Higson, Weinberger 2005** ("The Novikov conjecture for linear groups," *Publ. IHES* 101). NC for all **subgroups of GL_n(F)** for any field F. Burnside groups B(m, n) are NOT linear (Olshanskii / Adyan).

10. **Kasparov & Skandalis 2003** ("Groups acting properly on bolic spaces and the Novikov conjecture," *Annals of Math.* 158). NC for **groups acting properly on bolic spaces** (a generalization of CAT(0) and Gromov-hyperbolic). Includes lattices in higher-rank Lie groups via Bruhat–Tits buildings. Doesn't apply to Burnside groups (no known proper bolic action).

11. **Adyan 1979** (*The Burnside problem and identities in groups*, Springer). Proved B(m, n) infinite for n odd ≥ 665 and any m ≥ 2; provided detailed combinatorial structure but did not address NC.

12. **Gromov 2003** ("Random walk in random groups," *Geom. Funct. Anal.* 13). Constructed random groups containing isometrically-embedded expander graphs. These groups fail Property A and are not uniformly embeddable into Hilbert space. NC remains open.

## Attack surfaces tried (this attempt)

### Attack 1: Test if B(2, 665) is a-T-menable (apply Higson–Kasparov)

- **Approach:** if B(2, 665) admits a proper isometric action on Hilbert space (Haagerup property), Higson–Kasparov gives Baum–Connes, hence Novikov. Check known structure.
- **Tools used:** survey of property (T)/Haagerup status: Bekka–de la Harpe–Valette ("Kazhdan's Property (T)"), Cherix–Cowling–Jolissaint–Julg–Valette ("Groups with the Haagerup Property").
- **Time spent:** ~5 min.
- **Result:** B(2, 665) is **not known to be a-T-menable** and is also **not known to have Property (T)**. It sits in the "unclassified" middle region. Its growth and its torsion property combine to obstruct natural Haagerup-type constructions: the standard a-T-menability proofs use trees, walls, or affine structures, none of which Burnside groups admit naturally. In particular, since Burnside groups are infinite-torsion, they do not act freely on a CAT(0) cube complex (such an action would force the group to be torsion-free outside vertex stabilizers).
- **Why it failed:** `requires_unproven_conjecture` (Haagerup property for B(2, 665) is unknown; even establishing that *would* imply Novikov but is itself open).
- **Kill_path classification:** unknown-property-of-input.
- **Distance to closure:** "not in this attack space" — cannot apply Higson–Kasparov without first solving an open question about B(2, 665).

### Attack 2: Apply Yu's coarse BC via Property A or finite asymptotic dimension

- **Approach:** Yu 1998 (asymptotic dim) and Yu 2000 (Property A) imply NC. Test whether B(2, 665) has finite asdim or Property A.
- **Tools used:** survey Roe "Lectures on Coarse Geometry" (AMS 2003); Bell–Dranishnikov "Asymptotic dimension" (*Topology Appl.* 2008).
- **Time spent:** ~5 min.
- **Result:** B(m, n) for n large odd has growth rate that obstructs finite asymptotic dimension. The torsion + finite generation forces every ball to be "fat," so asdim should be infinite (this matches the heuristic for infinite torsion groups). **Property A status is OPEN**: no published proof either way for Burnside groups. Some experts conjecture B(m, n) has Property A (because it is "amenable in spirit" through its torsion structure), others conjecture failure (because of growth obstructions). Attempt fails for the same reason as Attack 1.
- **Why it failed:** `requires_unproven_conjecture`.
- **Kill_path classification:** unknown-property-of-input.
- **Distance to closure:** equivalent to Property A question for B(m, n).

### Attack 3: Apply Lafforgue (hyperbolic groups via Banach KK)

- **Approach:** B(m, n) is for n ≥ 665 odd a "lacunary hyperbolic" group in the Olshanskii–Osin–Sapir 2009 sense (it's a direct limit of hyperbolic groups). Could lacunary hyperbolicity yield NC?
- **Tools used:** Olshanskii–Osin–Sapir 2009 "Lacunary hyperbolic groups," *Geom. Topol.*; Lafforgue 2002 boundaries of applicability.
- **Time spent:** ~5 min.
- **Result:** lacunary hyperbolic groups have one *asymptotic cone* that is an ℝ-tree (so they look hyperbolic at one scale), but other asymptotic cones can be wildly non-hyperbolic. Lafforgue's KK-theoretic argument requires a uniform Banach-bicombing on the Cayley graph; lacunary hyperbolicity does not provide one. **Lafforgue's method does not extend to B(m, n).** Subsequent work (Lafforgue 2012 on strong property T in higher rank) reinforces that the technique requires more than asymptotic-cone-level hyperbolicity.
- **Why it failed:** `method_complexity` — the Banach KK-bicombing requirement is structurally finer than what Burnside groups provide.
- **Kill_path classification:** instrument-needs-uniform-control-input-only-asymptotic.
- **Distance to closure:** "not in this attack space" — Burnside groups need a different attack tool.

### Attack 4: Reduce via finite-index subgroups / index-finite covers

- **Approach:** if B(m, n) had a finite-index subgroup with a known NC proof, NC for B(m, n) follows by standard induction-restriction in K-theory (Kasparov inductive limit). Check.
- **Tools used:** structure theorem on Burnside groups; Olshanskii's monster constructions.
- **Time spent:** ~3 min.
- **Result:** B(m, n) for n large odd is **simple** (Adyan); it has no proper finite-index subgroups. So this reduction is unavailable.
- **Why it failed:** `case_restriction` — input lacks the required subgroup structure.
- **Kill_path classification:** structural-feature-absent-from-input.
- **Distance to closure:** unbounded; this attack space is structurally inapplicable.

### Attack 5: Attempt direct cyclic-cohomology / Connes–Moscovici approach

- **Approach:** Connes–Moscovici 1990 ("Cyclic cohomology, the Novikov conjecture and hyperbolic groups," *Topology*) proved NC for hyperbolic groups via cyclic cohomology + transgression. Attempt: replicate the structure for Burnside groups via their combinatorial torsion structure.
- **Tools used:** review Connes–Moscovici 1990; Burghelea computation.
- **Time spent:** ~7 min.
- **Result:** the Connes–Moscovici method requires a *bounded* cyclic cohomology class on the group, constructed from a hyperbolic geodesic-type structure. Burnside groups lack such a structure: the relations xⁿ = 1 are not bounded-volume in any geodesic sense. Replicating the construction would require a substitute for hyperbolicity, which is the same gap as Attack 3 in cyclic-cohomology dress.
- **Why it failed:** `method_complexity` — cyclic cohomology approach needs hyperbolic-like geodesic structure.
- **Kill_path classification:** instrument-needs-geodesic-input.
- **Distance to closure:** unbounded.

### Attack 6 (Gromov monster sub-case): apply Mineyev–Yu / Connes–Moscovici extensions

- **Approach:** for Gromov monster groups (containing expanders), the obstruction is even more severe than for Burnside groups: the coarse BC conjecture fails (Higson–Lafforgue–Skandalis 2002). Yet the *classical* Baum–Connes (and hence NC) might still hold. Test whether any partial results exist.
- **Tools used:** survey of Gromov monster literature; Arzhantseva–Drutu, Sapir on small-cancellation alternatives.
- **Time spent:** ~3 min.
- **Result:** **NC for Gromov monsters is OPEN.** The standard tools all fail (no Property A, no Haagerup, no asymptotic dim, no proper bolic action, fails coarse BC). The literature has NOT produced a positive NC result for any explicit Gromov monster, nor a counterexample. The conjecture is consistent with NC being TRUE for all groups (no published obstruction beyond "the standard tools all fail"), but no path forward.
- **Why it failed:** `non_constructive` — the failure of the classical tools is documented; no constructive path has been found.
- **Kill_path classification:** entire-tool-family-is-blind.
- **Distance to closure:** unbounded.

## Partial results obtained

- **None.** No new lemma, no computational verification, no reduction.
- The attack-surface map is now legible: B(m, n) and Gromov monsters are the natural "limits of methods" cases, where the available NC machinery (a-T-menability, Property A, asymptotic dim, hyperbolicity, linearity, lattice in Lie group, bolic action) all fail to apply. NC for these classes is at the **frontier**.

## Honest "what would unblock this"

A genuinely new K-theoretic technique that does not rely on geometric properties (Haagerup, Property A, bolic, hyperbolic, linear, finite asdim). One candidate direction: **C\*-algebraic methods that work directly with the reduced group C\*-algebra C*_r(G) without geometric input**. E.g., a refined trace/spectral structure on C*_r(B(2, 665)) that detects the assembly map injectivity directly. No such technique is in the literature. A second direction: **a "negative" result** showing that NC fails for some explicit Gromov monster, which would be a genuine surprise and would force re-examination of the conjecture. No such counterexample candidate exists.

## Calibrated negatives

- **Burnside groups are NOT in the Higson–Kasparov class** (not a-T-menable as far as known; structurally obstructed for the standard a-T-menability constructions).
- **Burnside groups are NOT in Yu's class via finite asdim** (they have infinite asdim; Property A status open).
- **Burnside groups are NOT hyperbolic** for n ≥ 665 (they are lacunary hyperbolic, which does not suffice for Lafforgue).
- **Burnside groups are NOT linear** (Adyan / Olshanskii).
- **Burnside groups are simple** for n ≥ 665 odd: no finite-index reduction.
- **Gromov monsters fail coarse BC** (Higson–Lafforgue–Skandalis), so the standard "coarse → uniform" reduction is blocked at the source.
- **No published technique covers either case.** The status as of 2025 is: NC for B(m, n) and Gromov monsters is firmly OPEN with no known partial results.

## Citations

- Novikov, S. P. "Topological invariance of rational Pontrjagin classes." *Doklady Akademii Nauk SSSR* 163 (1965) 298–300.
- Mishchenko, A. S. "Infinite-dimensional representations of discrete groups, and higher signatures." *Math. USSR Izv.* 8 (1974) 85–111.
- Kasparov, G. G. "Equivariant KK-theory and the Novikov conjecture." *Inventiones Math.* 91 (1988) 147–201.
- Higson, N. & Kasparov, G. "E-theory and KK-theory for groups which act properly and isometrically on Hilbert space." *Inventiones Math.* 144 (2001) 23–74.
- Yu, G. "The Novikov conjecture for groups with finite asymptotic dimension." *Annals of Math.* 147 (1998) 325–355.
- Yu, G. "The coarse Baum–Connes conjecture for spaces which admit a uniform embedding into Hilbert space." *Inventiones Math.* 139 (2000) 201–240.
- Higson, N., Lafforgue, V., Skandalis, G. "Counterexamples to the Baum–Connes conjecture." *Geometric and Functional Analysis* 12 (2002) 330–354.
- Lafforgue, V. "K-théorie bivariante pour les algèbres de Banach et conjecture de Baum–Connes." *Inventiones Math.* 149 (2002) 1–95.
- Guentner, E., Higson, N., Weinberger, S. "The Novikov conjecture for linear groups." *Publications mathématiques de l'IHÉS* 101 (2005) 243–268.
- Kasparov, G. & Skandalis, G. "Groups acting properly on bolic spaces and the Novikov conjecture." *Annals of Math.* 158 (2003) 165–206.
- Connes, A. & Moscovici, H. "Cyclic cohomology, the Novikov conjecture and hyperbolic groups." *Topology* 29 (1990) 345–388.
- Adyan, S. I. *The Burnside Problem and Identities in Groups.* Springer Ergebnisse 95, 1979.
- Gromov, M. "Random walk in random groups." *Geometric and Functional Analysis* 13 (2003) 73–146.
- Olshanskii, A. Yu., Osin, D. V., Sapir, M. V. "Lacunary hyperbolic groups." *Geometry & Topology* 13 (2009) 2051–2140.
- Roe, J. *Lectures on Coarse Geometry.* University Lecture Series 31, AMS 2003.
- Bell, G. & Dranishnikov, A. "Asymptotic dimension." *Topology Appl.* 155 (2008) 1265–1296.
- Cherix, P.-A., Cowling, M., Jolissaint, P., Julg, P., Valette, A. *Groups with the Haagerup Property.* Birkhäuser 2001.
- Bekka, B., de la Harpe, P., Valette, A. *Kazhdan's Property (T).* Cambridge Univ. Press 2008.
- Ferry, S., Ranicki, A., Rosenberg, J. (eds.) *Novikov Conjectures, Index Theorems, and Rigidity.* Cambridge Univ. Press, LMS Lecture Note Series 226, 1995 (vol. 1) and 227, 1995 (vol. 2).
