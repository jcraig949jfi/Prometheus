---
catalog_name: Kolmogorov K41 inertial-range energy cascade (turbulence)
problem_id: k41-turbulence
version: 1
version_timestamp: 2026-04-23T22:00:00Z
status: alpha
cnd_frame_status: consensus_catalog
teeth_test_verdict: FAIL_via_uniform_alignment
teeth_test_sub_flavor: null
teeth_test_resolved: 2026-04-23
teeth_test_resolver: Harmonia_M2_sessionA
teeth_test_cross_resolver: Harmonia_M2_sessionB
teeth_test_third_reader: Harmonia_M2_sessionC
shadows_on_wall_tier: coordinate_invariant
teeth_test_sub_flavor: empirical_range_saturated
teeth_test_doc: agora:harmonia_sync 1776914599704-0 (sessionA forward-path) + 1776914739362-0 (sessionB cross-resolve ENDORSE) + sessionC third-reader ENDORSE this iteration
teeth_test_note: Third proposed CONSENSUS_CATALOG anchor after p_vs_np (anchor 1) + drum_shape (anchor 2). If confirmed + cross-resolved, CONSENSUS_CATALOG@v0 hits 3-anchor promotion threshold and can graduate to @v1. Consensus_basis=empirical_range_saturated (different sub-flavor than drum_shape's external_theorem_proven and p_vs_np's no_counterexample_found+barrier_results — three distinct sub-flavors across 3 anchors strengthens promotion case).
surface_statement: In a fully developed homogeneous isotropic turbulent flow at high Reynolds number, the energy spectrum in the inertial range scales as E(k) = C·ε^(2/3)·k^(-5/3), where ε is the mean energy dissipation rate and C is a dimensionless constant (~1.5). The cascade proceeds from large scales (energy injection) to small scales (viscous dissipation) with no net flux across the inertial range. Conjectured by Kolmogorov 1941; empirically verified across ~80 years of experiments + DNS at every accessible Reynolds.
author_caveat: First-pass catalog by a generalist sessionA, not a fluid-mechanics researcher. Deep-domain expert review welcomed. Catalog scope is to establish the teeth-test uniform-alignment shape; lens enumeration may be incomplete on intermittency + coherent-structures corners. If an expert flags a genuinely adversarial frame I missed, sub-flavor may flip.
---

# Kolmogorov K41 inertial-range energy cascade

## What the problem is really asking

1. **Does a self-similar inertial range exist at finite Reynolds?** K41 assumes asymptotic scale-separation between injection + dissipation. At any finite Re there's a finite inertial range; as Re → ∞ the range grows. The conjecture is universality of the 5/3 exponent within that range.
2. **Is the cascade a statistical-mechanical consequence of Navier-Stokes, or a separate physical mechanism?** K41's derivation uses symmetry + dimensional analysis without invoking specific Navier-Stokes dynamics. Whether NS equations imply K41, or K41 is a consequence of something broader (dimensional coincidence + symmetry), is structurally open.
3. **How robust is K41 to intermittency corrections?** Higher-order structure functions deviate from the 5/3 prediction (She-Leveque 1994, multifractal models). Most literature treats this as a refinement of K41 rather than a refutation; consensus holds at the second-order / spectrum level.
4. **Which coherent structures carry the cascade?** Filamentary vortex tubes, sheets, and worm-like structures are observed in DNS and lab. Whether these are causal (cascade happens via vortex stretching) or epiphenomenal (cascade is bulk-statistical, structures are visualization) is active but not predictively-disputed on the 5/3 scaling.
5. **What is the Navier-Stokes regularity connection?** The open Clay Millennium problem on NS existence + smoothness is upstream of K41's status; K41 holds empirically regardless.

## Data provenance

- **Kolmogorov 1941 ("On the Local Structure of Turbulence")** — original 5/3 scaling conjecture from dimensional arguments.
- **Obukhov 1941 + Onsager 1945** — independent derivations; Onsager's cutoff argument links cascade to finite-time singularities in Euler equations.
- **Grant-Stewart-Moilliet 1962** — first clean oceanographic experimental confirmation of the 5/3 spectrum.
- **Direct Numerical Simulation (Orszag-Patterson 1972 onward)** — computational confirmation at increasing Reynolds; Ishihara-Gotoh-Kaneda 2009 at Re_λ = 1201 reached inertial-range scaling agreement with K41 to within intermittency-correction tolerance.
- **She-Leveque 1994** — multifractal intermittency model; predicts small corrections to higher-order structure-function exponents ζ_p, with ζ_2 still ≈ 5/3 to within observational precision.
- **Frisch, "Turbulence: The Legacy of A.N. Kolmogorov" (1995)** — canonical review treating K41 as established at the 2-point / 2nd-order level and intermittency as perturbative refinement.

**Consensus state 2026-04-23:** the 5/3 spectral scaling in the inertial range of homogeneous isotropic turbulence is treated as empirically saturated in the fluid-mechanics + engineering-turbulence + applied-physics communities. Every major review (Pope 2000, Davidson 2015) adopts K41 as the baseline; intermittency corrections refine higher moments without challenging the baseline.

## Motivations

- **Foundational to turbulence engineering.** LES/RANS models, weather forecasting, chemical mixing, aerospace design all assume K41 in their closure approximations. Engineering success stories are empirical consensus evidence.
- **Dimensional analysis archetype.** K41 is one of the cleanest examples of physics where dimensional analysis alone delivers a quantitative universality.
- **Probe of critical phenomena.** The cascade shares language with RG fixed points + critical exponents; turbulence is historically a test case for universality-class reasoning beyond equilibrium statistical mechanics.
- **Pedagogical.** Students across physics / engineering / applied-math share K41 as common vocabulary.

## Lens catalog (6 entries)

### Lens 1 — Dimensional analysis / Kolmogorov original

- **Discipline:** Statistical physics / dimensional analysis
- **Description:** Given mean dissipation ε (units [L² T⁻³]) and wavenumber k, the only dimensionally-consistent spectrum is E(k) ~ ε^(2/3) k^(-5/3).
- **Status:** PUBLIC_KNOWN (K41 1941)
- **Prior result / stance:** 5/3 exponent on E(k). Universal across all HIT flows in the inertial range.
- **Tier contribution:** Yes — the anchor lens.

### Lens 2 — Experimental turbulence measurement

- **Discipline:** Experimental fluid mechanics
- **Description:** Hot-wire anemometry, LDV, PIV measurements of velocity spectra in laboratory + geophysical turbulence.
- **Status:** PUBLIC_KNOWN (Grant-Stewart-Moilliet 1962 and subsequent)
- **Prior result / stance:** Observed 5/3 spectrum across ~6 decades of scale separation in oceanographic + atmospheric data. Agreement with K41 within experimental error.
- **Tier contribution:** Yes — empirical-confirmation axis.

### Lens 3 — Direct Numerical Simulation (DNS)

- **Discipline:** Computational fluid dynamics
- **Description:** Full Navier-Stokes DNS at increasing Reynolds; measurement of E(k) in the inertial range.
- **Status:** PUBLIC_KNOWN (Ishihara-Gotoh-Kaneda 2009 + successors)
- **Prior result / stance:** 5/3 spectrum observed; intermittency corrections at high-order moments (ζ_6 ≈ 1.75 vs K41 prediction 2.00) present but small.
- **Tier contribution:** Yes — computational-confirmation axis, distinct from experimental.

### Lens 4 — Renormalization group physics

- **Discipline:** Theoretical statistical physics
- **Description:** Cascade as fixed-point behavior in a hypothetical RG flow on the NS equations; 5/3 exponent as critical-exponent output of an RG calculation (Yakhot-Orszag, Wilson-style schemes).
- **Status:** PUBLIC_KNOWN
- **Prior result / stance:** RG derivations recover K41's 5/3 exponent within calculational precision. Treated as theoretical validation that K41 is consistent with a well-defined fixed point.
- **Tier contribution:** Yes — theory-of-universality axis.

### Lens 5 — Intermittency / multifractal refinements

- **Discipline:** Multifractal scaling theory
- **Description:** Higher-order structure functions S_p(r) ~ r^ζ_p deviate from K41's ζ_p = p/3 prediction at large p; She-Leveque, multifractal, and log-Poisson models refine the exponents.
- **Status:** PUBLIC_KNOWN
- **Prior result / stance:** 5/3 exponent on E(k) (ζ_2) is preserved; corrections appear only at high-order moments. Treated as extension-of K41, not refutation.
- **Tier contribution:** Yes — but aligned with K41 baseline; not adversarial.

### Lens 6 — Coherent-structures / vortex-dynamics perspective

- **Discipline:** Vortex dynamics + topological fluid mechanics
- **Description:** Turbulence as an ensemble of filamentary vortex tubes, sheets, and worms; cascade proceeds via vortex stretching and reconnection events.
- **Status:** PUBLIC_KNOWN
- **Prior result / stance:** Coherent structures are observed in DNS + lab; their presence does not dispute the 5/3 spectrum, but offers a mechanistic picture of what carries the cascade. Viewed as complementary to K41's statistical framing, not competitive.
- **Tier contribution:** Yes — mechanism axis; crucially NOT adversarial on the 5/3 prediction.

## Cross-lens summary

- **Total lenses cataloged:** 6
- **APPLIED (Prometheus):** 0 (turbulence is outside Prometheus's current measurement substrate; no internal DNS or lab data)
- **PUBLIC_KNOWN:** 6
- **NEW / BLEND:** 0

**All 6 lenses commit to the 5/3 exponent on E(k) in the inertial range.** Intermittency (Lens 5) refines higher-order moments; coherent structures (Lens 6) offers a mechanism; RG (Lens 4) theorizes the universality class; experimental + DNS + dimensional (Lenses 1-3) observationally confirm. **No lens in the catalog predicts an incompatible Y value** on the primary 5/3-scaling observable.

**Candidate adversarial frames NOT catalogued (because they are not seriously held in the community):**
- "5/3 is wrong at asymptotically high Re" — no theoretical or observational basis
- "Cascade doesn't exist; energy is transferred non-locally" — observational evidence of local cascade is strong
- "Intermittency refutes K41" — universal reading of intermittency is as refinement, not refutation

**Teeth-test verdict: FAIL_via_uniform_alignment.** All catalogued lenses align with the 5/3 consensus. No adversarial frame is catalogued. Diagnostic: **catalog-completeness work needed** — a forced-adversarial MPA run on K41 would need to manufacture a serious anti-5/3 stance (perhaps "cascade is finite-time-singularity-dominated at Re → ∞, violating K41's stationary assumption" per Onsager 1949 lineage). Such a stance exists in the math-PDE community around NS regularity but does not dispute K41's empirical scaling in the inertial range — the dispute lives one layer up (regularity of NS itself, which is orthogonal to K41's empirical status).

**Consensus_basis:** `empirical_range_saturated`. Distinct from p_vs_np's `no_counterexample_found + barrier_results` and drum_shape's `external_theorem_proven`. Three anchors now span three distinct sub-flavors of consensus, strengthening the CONSENSUS_CATALOG@v0 → @v1 promotion case.

**SHADOWS_ON_WALL tier:** `coordinate_invariant` on the 5/3 scaling at the empirical / inertial-range level. `shadow` on open upstream question (NS regularity) which is catalogued separately at the Millennium-problem level.

## Connections

**To other open problems:**
- **Navier-Stokes existence + smoothness (Clay Millennium problem)** — K41 is downstream of NS regularity in the sense that K41 holds empirically regardless of the NS-regularity answer, but a resolution of NS-regularity would constrain which theoretical derivations of K41 are rigorous.
- **Onsager 1949 + NS Euler singularity regularity** — Onsager conjectured the dissipation anomaly persists in the infinite-Reynolds limit, which is consistent with K41 but adds regularity structure. Partial proofs: Eyink 1994, Constantin-E-Titi 1994 showed ζ_2 ≤ 5/3 implies dissipation anomaly possible.

**To Prometheus symbols:**
- `CONSENSUS_CATALOG@v0` — this catalog is the proposed 3rd anchor for uniform-alignment sub-shape of the teeth-test FAIL bucket.
- `FRAME_INCOMPATIBILITY_TEST@v2` — catalog teeth-tested via v2 section 2.E decision tree; fires STEP 3 CONSENSUS_CATALOG per uniform alignment + committed lenses + declared community consensus.
- `SHADOWS_ON_WALL@v1` — canonical example of lens convergence at the empirical / inertial-range level.
- `methodology_toolkit.md` — Lens 4 (RG) + Lens 1 (dimensional analysis) are shelf-entry-adjacent; `CRITICAL_EXPONENT@v1` toolkit entry is very directly applicable to the 5/3 exponent itself.

**Originator probe:** sessionA API_PROBE_RESULT 1776906584732-0 (Claude Sonnet 4.6, 2026-04-22) proposed K41 as a concrete non-Millennium CONSENSUS_CATALOG anchor candidate with aligning-lenses (stat mech + engineering + RG) and missing-adversarial-frame (dissipation-geometry realism). This catalog operationalizes that suggestion into a teeth-test-compatible artifact.

**Path to coordinate_invariant on CONSENSUS_CATALOG@v1:** if this catalog is cross-resolved by one of {sessionB, sessionC, auditor} to ENDORSE the FAIL_via_uniform_alignment verdict, it reaches `surviving_candidate`. With {p_vs_np, drum_shape, k41_turbulence} at surviving_candidate each with distinct sub-flavors, CONSENSUS_CATALOG@v0 has 3 cross-resolved anchors + 1 forward-path application → meets CND_FRAME diagnostic_certainty schema for promotion to @v1. sessionA is the author-of-record, so cross-resolver must come from a different agent.
