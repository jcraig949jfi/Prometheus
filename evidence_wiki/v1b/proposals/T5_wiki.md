# PROPOSAL T5 (wiki)

Designer: V1B-T5-wiki (M1) — 2026-09-02
Substrate: `topology.knots` (prometheus_sci, 12,965 rows: name, crossing_number, determinant, signature, alexander_coeffs, jones_coeffs, conway_coeffs) joined to spine arithmetic/spectral tables (`nf_fields`, `zeros.dirichlet_zeros` [184,830 rows, keyed by conductor], `lfunc_lfunctions`).
Status of the field going in: the Evidence Wiki records knot silence as GENUINE with the feature-mismatch rescue already REFUTED (C-1938a4759fd8, ceiling: "knot silence is genuine (H3 leading hypothesis)"). This proposal is written expecting a null; the null is the product. The design's value is severity: it tests the one *categorical* bridge computable from existing columns, with quantified sensitivity, so a null upgrades "silence" from "no signal under lenses tried" to "no signal under the canonical covering-space join at MDE rho <= 0.2."

## Hypothesis

H-T5: The arithmetic of the double branched cover couples to knot topology beyond magnitude. Concretely: each knot K determines, canonically (not by feature re-encoding), a quadratic number field via its double branched cover Sigma_2(K), whose H_1 has order det(K) (odd). Define the join key d*(K) = fundamental discriminant of -det(K). H-T5 claims that arithmetic properties of d*(K) — primality of det, class number h(d*), and the normalized lowest zero of the conductor-|d*| Dirichlet L-function — are statistically coupled to topology-side invariants (signature, Jones span) after controlling for magnitude (log det), crossing number, and the algebraically forced genus-theory component (2-rank of Cl(d*) = omega(det) - 1, which is NOT evidence of coupling and is subtracted by design).

Null H0-T5 (expected, per claim ceiling of C-1938a4759fd8): conditional on (crossing_number stratum, log-det stratum), topology-side invariants are exchangeable with respect to arithmetic class of d*; knot silence extends to the categorical join.

This is deliberately NOT a rerun of the killed channel: the prior kill (X-f6743537ade6 / E-86e2edb52047) tested numerical feature re-encodings (univariate Mahler, root-of-unity evaluations) against EC L-values with no structural join, on 2,977 knots (<=12 crossings). The lens-mismatch catalog (harmonia/memory/catalogs/knot_nf_lens_mismatch.md) diagnoses the bridge as categorical; its preferred lens (A-polynomial Mahler) requires SnapPy data that does not exist in the spine, so the double-branched-cover discriminant is the only categorical bridge computable from existing columns.

## Design

Phase 0 — Inventory and preflight (no hypothesis testing; all gates computed BEFORE any test statistic is read):
1. Enumerate the FULL 12,965-row inventory (no prefix sampling). Compute per knot: det, d*(K), omega(det), log det, jones span (deg max - deg min), signature.
2. Join coverage census: fraction of knots whose |d*| matches a conductor in `zeros.dirichlet_zeros` (degree-1 rows) and a field in `nf_fields`; count of DISTINCT d* values in the joined set. Coverage numbers are reported per population (discovery vs confirmation) — never quoted across populations.
3. Projection-inequivalence check: regress the new features {d*, omega(det), primality} on the previously killed feature set (Alexander Mahler proxy: log max|alexander_coeffs|, root-of-unity evaluations of Alexander/Jones). If R^2 > 0.9 for a new feature, that feature is declared projection-equivalent to the killed lens and is DROPPED (it cannot claim independence from the prior kill).
4. Attainable-range check: for every preregistered statistic, compute the attainable min/max on the actual joined data and verify each threshold in the falsifier section lies strictly inside the attainable range. Any unreachable gate voids the corresponding test (declared VACUOUS, not null).
5. Positive control / MDE: inject synthetic coupling into a label-permuted copy at effect sizes rho in {0.10, 0.15, 0.20} (partial Spearman at the cluster level) and measure recovery power of the full pipeline at alpha = 0.005. The minimum detectable effect (MDE) is the smallest rho recovered with >= 90% power. Committed before Phase 1 output is read.

Phase 1 — Discovery set: the 2,977 knots with crossing_number <= 12 (the same population as the prior kill, deliberately, so the two results are comparable). Preregistered family of five tests (m = 5), all object-level, no tensor scorers:
- T1: signature vs primality of det. Statistic: difference in mean |signature| between prime-det and composite-det knots within (crossing_number, log-det-quintile) cells, aggregated by inverse-variance weighting. Null: cluster permutation (see Controls) of the arithmetic label, 10,000 permutations.
- T2: Jones span vs primality of det. Same machinery as T1.
- T3: signature vs h(d*), residualized on log det, omega(det), crossing_number (partial Spearman at the determinant-cluster level). The genus-theory forced component enters through omega(det) and is thereby removed from the claim.
- T4: normalized lowest zero z1~ = z1 * (log(|d*|/2pi e)/2pi)^{-1}... operationally: z1 rescaled by the local mean spacing at conductor |d*| (mean-spacing normalization FIRST), tested against knot multiplicity-weighted topology summaries within log-conductor deciles (partial Spearman, cluster level).
- T5: determinant-multiset arithmetic test: chi-square of the omega(det) distribution of distinct knot determinants against a magnitude- and parity-matched random odd-integer null (1,000 resamples). Tests whether knot determinants are arithmetically special at all.

Phase 2 — Confirmation set: the ~9,988 knots with crossing_number = 13, held out completely (never touched in Phase 0 statistics beyond coverage counts, never read during Phase 1). Any Phase 1 positive must replicate here: same sign, p <= 0.05 (one-sided, direction fixed by Phase 1). No positive in Phase 1 => Phase 2 is not run and the verdict is the Phase 1 null with its MDE.

All analysis code hashed (sha256) and committed before any Phase 1 statistic is computed. Verdict ledger and program-disposition ledger kept separate. Raw per-knot rows ship in the same commit as the verdict.

## Controls

1. Cluster permutation at the determinant level (primary null). Every arithmetic quantity is a deterministic function of det, so knots sharing a det are one exchangeable block. Permutations reassign arithmetic labels across DISTINCT det values within (crossing_number, log-det-quintile) strata; knots inherit their block's label. This (a) puts the null on the axis the statistic varies on, and (b) breaks the knot->field assignment while preserving magnitude structure and the det multiplicity profile.
2. Magnitude stratification everywhere: no statistic is ever computed across unmatched magnitude strata; no outcome of the form |a - b| <= N between quantities of different scales is permitted anywhere in the pipeline.
3. Conductor conditioning for T4: all zero-statistics comparisons are within log-conductor deciles, after mean-spacing normalization; nothing is claimed from raw z1.
4. Tautology (Pattern 30) audit on any positive: both sides are checked for a shared algebraic ancestor. The known forced components are declared in advance: (i) genus theory: 2-rank of Cl(d*) = omega(det) - 1; (ii) h(d*) grows like sqrt(|d*|) log — i.e., h carries log det; (iii) z1 scale carries log conductor = f(log det). Every claim is therefore about the residual after log det and omega(det) are partialled out. A positive whose partial effect is < 50% of its raw effect with a partial-CI covering 0 is verdicted TAUTOLOGY-DRIVEN, not coupling.
5. Positive control (Phase 0.5) doubles as the instrument-validity control: a pipeline that cannot recover injected rho = 0.20 at 90% power is INVALID and produces no verdict about knots.
6. Negative control: the whole T1-T4 battery is additionally run once with d* replaced by the fundamental discriminant of a random odd integer matched to det in magnitude and parity (one fixed seed, preregistered). Any "coupling" that also appears under the matched-random join indicates a pipeline artifact, and the corresponding real-join positive is voided.

## Preregistered falsifiers (each with an explicit numeric threshold)

- FALS-1 (instrument): if injected coupling at rho = 0.20 is recovered with power < 0.90 at alpha = 0.005 (>= 500 injection replicates), the instrument is INVALID; experiment halts with verdict INSTRUMENT_FAIL. No knot claim of any kind is made.
- FALS-2 (vacuity, pre-committed VACUOUS reading): if joined coverage in the discovery set is < 30% of knots (< 894 of 2,977) OR distinct-d* cluster count < 500, verdict is VACUOUS_COVERAGE — a statement about the join, not about knots. (Rationale: at 500 clusters the MDE for a partial Spearman at alpha = 0.005 is approx rho = 0.19; below that the null is uninformative.)
- FALS-3 (the coupling claim, i.e., what kills H-T5): H-T5 is REFUTED if, across the m = 5 family, no test achieves Holm-corrected p <= 0.005 with |effect| >= MDE (from Phase 0.5) at the cluster level. Effect floor is explicit: partial Spearman |rho| >= 0.15 for T3/T4; |standardized mean difference| >= 0.15 for T1/T2; chi-square p <= 0.001 for T5.
- FALS-4 (transfer): any Phase 1 positive that fails Phase 2 confirmation (same sign, one-sided p <= 0.05 on 13-crossing knots) is verdicted NON-TRANSFERRING (memorisation-class, per the 147-K/148-L precedent) and does NOT support H-T5.
- FALS-5 (tautology): a positive whose effect, after partialling log det + omega(det) + crossing_number, retains < 50% of the raw effect AND whose partial 99% CI (cluster bootstrap, n = distinct d*) covers 0, is verdicted TAUTOLOGY-DRIVEN and does NOT support H-T5.
- FALS-6 (artifact): a positive that reproduces (same test, |effect| >= 50% of real-join effect, p <= 0.01) under the matched-random-discriminant negative control is verdicted PIPELINE_ARTIFACT and voided.
- Gate hygiene: every threshold above must be shown to (a) lie inside the attainable range computed in Phase 0.4 and (b) exceed the measurement SE of its statistic by at least 2x (SE computed at cluster n BEFORE the statistic is read). A gate failing either check is re-derived only by amending this document BEFORE Phase 1, never after.

## Stopping rule

One pass. Phase 0 gates -> Phase 1 (fixed battery of 5 tests, 10,000 permutations each, fixed seeds committed with the code hash) -> Phase 2 only if Phase 1 produced a survivor. No test may be added, dropped, or re-parameterized after any Phase 1 statistic is read. No optional stopping, no second look with new invariants on a null: a null here is final for this join and is submitted to the Evidence Wiki as a NEGATIVE_RESULT with its MDE attached. Any follow-up (e.g., the A-polynomial lens once SnapPy data exists) requires a new preregistration; it may not amend this one. Hard resource cap: if the full pipeline exceeds 12 hours on M1, halt and record INCOMPLETE with the phase reached.

## Unit of inference

The distinct determinant value (equivalently, distinct d*), NOT the knot. Every arithmetic quantity is constant within a det block, so the effective sample is the number of distinct determinants in the joined set (expected O(10^2)-O(10^3) in discovery), not 2,977 knots — an SE computed at knot n would inflate precision exactly as in the 57x per-row error previously recorded. All permutations, bootstraps, SEs, and power calculations are at the cluster (det-block) level; topology-side variation within a block is summarized (median signature, median Jones span) before testing. Reported n is always cluster n, per population.

## Prior work bearing on this design

- X-f6743537ade6 / E-86e2edb52047 / C-1938a4759fd8 (Ergon P1.3, 2026-04-15, REFUTED): Mahler + root-of-unity re-encodings vs EC L-values, NO SIGNAL on 2,977 knots (<=12 crossings). Claim ceiling: "knot silence is genuine (H3 leading hypothesis)." The most direct predecessor; this proposal is its severity-quantified extension to the categorical join.
- F027 / F032 (harmonia/memory/algebraic_coupling_audit.md): Alexander-Mahler x EC L-value KILLED ("cyclotomic gap, no Lehmer probing"); knot silence recorded as persistent null across every projection; both audited CLEAN (no tautology).
- harmonia/memory/catalogs/knot_nf_lens_mismatch.md: LENS_MISMATCH@v1 diagnosis — the knot<->NF bridge is real under the A-polynomial lens (26 Chinburg verifications) but that lens is categorical and its data (A-polynomials, hyperbolic volumes) is absent from the spine; SnapPy pending. Also: prometheus_math/databases/knots.json.gz is a 52-entry corpus shipping hyperbolic_volume = 0.0 for all entries (KNOT_VOLUME_CONFLATION_PREREG.md) — unusable for volume-dependent work, so no volume-based test appears in this design.
- C-4f607db9b4a7 (cycle 150-N KILL): magnitude-compatibility outcome variables (single-digit invariant vs 4-digit conductor) are degenerate.
- C-d151768c6740, C-9334502f16d1 (Harmonia): conductor conditioning kills naive spectral correlations; moments add nothing beyond conductor + rank.
- C-96779c5836df (F028), C-450a0c8756cf (F043): tautologies from shared algebraic ancestors (log|Disc| on both sides; BSD identity rearrangement).
- C-8f20c74fa0cf: the tensor measures feature geometry, not object-level coupling — object-level statistics only.
- C-1f1a743fce1b: permutation null (z = 0.0) exposed a distributional-not-object-level "structure"; nulls must attack the assignment axis.
- C-e5e726a050c1 (148-L retraction of 147-K): a positive that is memorisation of constants fails held-out transfer; rankings can reverse across relations.
- C-96a0e90f4eeb / C-a3744a88ea5e: native verbs found relations where generic operators found zero — motivating the canonical (native) covering-space construction over generic feature pairing.

## Evidence Wiki consultation log (queries run + object ids retrieved)

Client: `EvidenceWiki(machine='M1', agent='V1B-T5-wiki')`, canonical_revision 521 (embedding index current; cp derived view 118 behind — noted, not load-bearing).

1. search_evidence("knot invariants coupling spectral arithmetic", hybrid, k=10) -> C-1938a4759fd8, C-d151768c6740, C-4f607db9b4a7, C-a3744a88ea5e, C-8f20c74fa0cf, C-96779c5836df, C-e5e726a050c1, C-a36c7e9fe323, C-96a0e90f4eeb, C-450a0c8756cf.
2. search_evidence("knots Jones polynomial silence null", hybrid, k=10) -> C-1938a4759fd8, C-948eae5cb70c, C-94fc12c3e6af, C-1f1a743fce1b, C-a36c7e9fe323, C-777c096815e3, C-e5e726a050c1, C-3a1c49fa5a78, C-d151768c6740, C-9334502f16d1.
3. get_claim("C-1938a4759fd8") -> claim v1 (REFUTED; ceiling "knot silence is genuine (H3 leading hypothesis)"), evidence E-86e2edb52047 (NEGATIVE_RESULT, substrate "2,977 knots with computed Mahler measures (range 0.89-30.4) vs EC L-values"), experiment X-f6743537ade6, packet SP-2256eb272cce, source roles/Aporia/SESSION_JOURNAL_20260415.md L98-L99 (verified verbatim in repo).
4. get_counterevidence("C-1938a4759fd8") -> counter_relations: none; negative_evidence: E-86e2edb52047. No recorded rescue of the feature-mismatch thesis.
5. related_findings("C-1938a4759fd8") -> semantic: C-754b9b65fb6c, C-4f607db9b4a7, C-96779c5836df, C-45bd5ff28211, C-450a0c8756cf, C-8f20c74fa0cf, C-a36c7e9fe323, C-efb1cf440e10, C-b287aa6823b0, C-ec2958821325; graph edges: none. Follow-up get_claim on C-754b9b65fb6c (leak-gate denylist kill) and C-45bd5ff28211 (S3 accessibility-geometry kill).
6. Negative-evidence/kill query: search_evidence("kill negative result cross-domain topology knot coupling", hybrid, k=10) -> C-1938a4759fd8, C-4f607db9b4a7, C-96779c5836df, C-01f913ae81af, C-450a0c8756cf, C-8f20c74fa0cf, C-ec2958821325, C-aba202675bd8, C-d0f2742bd8ed, C-ff8811fa0ac7.
7. contradictions() -> R-e68c9331eca2 (C-3a1c49fa5a78 vs C-3d12c440f087, D-5 vs D-8 executable-history dispute, APPARENT_UNDER_DIFFERING_CONDITIONS). Not knot-related.
8. find_gaps() -> H-a86125892a3e, H-41f9f15ce208, H-bac36ae694a2 (projection_equivalence x lmfdb_arithmetic MISSING_CELL), H-c9832bd95134, H-7c607f34d50e, H-9b0a7922015e. All flagged HYPOTHESIZED, not evidence.

## Evidence that changed this design (specific ids + the concrete design decision each changed)

- C-1938a4759fd8 + E-86e2edb52047 (+ its claim ceiling): removed any univariate-Mahler or root-of-unity-vs-EC-L-value channel from the battery; forced the hypothesis to be stated null-first with the null as the deliverable; fixed the discovery population to the same 2,977-knot (<=12 crossing) set so the new result is directly comparable to the kill; motivated the MDE-attached-to-null requirement (a null without sensitivity would add nothing over the existing kill).
- harmonia/memory/catalogs/knot_nf_lens_mismatch.md (surfaced via C-1938a4759fd8's related_hints and repo follow-up): excluded the A-polynomial/volume lens as infeasible (data absent, SnapPy uninstalled, knots.json.gz volumes are a documented conflation) and selected the double-branched-cover discriminant as the only categorical bridge computable from existing columns — the central design choice of T5.
- C-4f607db9b4a7: banned magnitude-difference outcome variables outright and imposed log-det stratification on every statistic (Controls 2).
- C-d151768c6740: made conductor conditioning + mean-spacing normalization mandatory and prior to any zero-statistic comparison (T4, Control 3).
- C-96779c5836df and C-450a0c8756cf: created FALS-5 and Control 4 — the pre-declared forced components (genus theory 2-rank, h ~ sqrt(|d*|), z1 ~ 1/log conductor) are partialled out BEFORE any coupling claim, and the 50%-retention tautology gate is preregistered.
- C-8f20c74fa0cf: dropped tensor scorers entirely; all five tests are direct object-level statistics.
- C-1f1a743fce1b: shaped the primary null as a cluster permutation on the knot->arithmetic assignment axis within strata (Control 1), rather than a row-shuffle that would leave the tested axis unperturbed.
- C-e5e726a050c1: added the held-out 13-crossing confirmation set and FALS-4 (transfer requirement); a discovery-set positive alone is verdicted memorisation-class.
- H-bac36ae694a2 (projection_equivalence x lmfdb_arithmetic gap; HYPOTHESIZED, used only as a prompt): added Phase 0.3, the explicit projection-inequivalence check that the new join features are not R^2 > 0.9 re-encodings of the killed feature set — without which T5 could not claim independence from the prior kill.
- C-754b9b65fb6c and C-45bd5ff28211 (related-findings follow-ups), C-948eae5cb70c, C-94fc12c3e6af, C-01f913ae81af, C-aba202675bd8, C-d0f2742bd8ed, C-ff8811fa0ac7, C-ec2958821325, C-3a1c49fa5a78, C-777c096815e3, C-a36c7e9fe323, C-9334502f16d1 (beyond the conductor rule above), C-96a0e90f4eeb / C-a3744a88ea5e (beyond the native-construction preference noted in prior work), R-e68c9331eca2, and the remaining find_gaps ids: retrieved and read, no design change — listed here only so the consultation is auditable, not cited as design drivers.
