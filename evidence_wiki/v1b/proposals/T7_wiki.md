# PROPOSAL T7 (wiki)

Designer: V1B-T7-wiki (M1) · 2026-09-02 · Specification only — no collection authorized by this document.
Substrate: local LMFDB mirror (`ec_curvedata` 3,824,372 rows; `lfunc_lfunctions` ~24M rows; `bsd_joined` materialized view, 2,481,157 rows), accessed via `thesauros.prometheus_data.get_lmfdb()`.
Target stratum (verified live 2026-09-02): rank >= 2 in `bsd_joined` = 282,373 curves (275,644 rank 2; 6,728 rank 3; 1 rank 4) in 182,937 isogeny classes, conductor 389–399,993. Coverage of `leading_term`, `regulator`, `sha`, `z1` on this stratum: 100%.

## Hypothesis

H1 (BSD square-consistency at rank >= 2, non-circular): For rank >= 2 elliptic curves over Q in the mirror, the analytic Sha order assembled WITHOUT using the stored `sha` column,

    Sha_an = leading_term · torsion² / (regulator · Ω · ∏cp)

— where `leading_term` (L-side, lfunc pipeline), `regulator` and `torsion` (Mordell–Weil side, ec pipeline) come from the mirror, and the real period Ω and Tamagawa product ∏cp are RECOMPUTED locally from `ainvs` by our own instrument — lies within numerical tolerance of a perfect square integer (Cassels pairing: |Sha| is a perfect square when finite), for at least 99.9% of isogeny classes.

What this is and is not. The mirror's `sha` at rank >= 2 is DEFINED as round(Sha_an) assuming BSD (C-e0352ce96e11), so "recomputed Sha matches stored sha" is a tautology and is excluded from every verdict statistic. The genuine falsifiable content that survives the circularity is the square-integrality of the assembled quantity: BSD + Cassels jointly predict Sha_an ≈ m² for integer m; nothing in the construction of leading_term, regulator, Ω, or cp forces that. A failure list is a list of BSD-inconsistency candidates (or instrument defects — Phase 0 separates these); a clean pass is a consistency verification at a stated tolerance, NOT a proof of BSD.

Claim ceiling (declared up front): (a) verification-at-tolerance on the joined stratum only, not "all LMFDB curves"; (b) the analytic rank underlying `leading_term`'s derivative order is a numerical-vanishing judgment (one cannot prove L''(1) ≠ 0 numerically) — this caveat is inherited, documented, and not resolvable by this design; (c) a pass constrains BSD only up to factors that map squares near squares (e.g., an omega wrong by ~4x can survive S1 — the perturbation null C2 measures the actual false-pass rate and bounds this).

H2 (secondary, descriptive, not gated): the residual distribution |Sha_an − nearest square| is statistically indistinguishable across rank ∈ {2, 3} after conductor-decile matching. Reported, never pooled into H1.

## Design

Phase 0 — Instrument (no rank >= 2 row read).
1. Implement in `prometheus_math` (via math-tdd, test-first):
   - `real_period(ainvs)` — Ω via AGM on the period lattice, with an independent second method (direct numerical integration of the invariant differential) as a composition test; the two must agree to 1e-9 relative on every test curve.
   - `tamagawa_product(ainvs, bad_primes)` — Tate's algorithm in exact integer arithmetic; bad primes parsed from the mirror's `bad_primes` column (no factoring needed). Internal cross-check: for `semistable = true` curves, multiplicative reduction gives cp ∈ {ord_p(Δ), 1, 2} with the split case decidable exactly — a property test over the semistable stratum.
2. Calibration (authority anchor, explicitly instrument-only): draw a STRATIFIED sample of 10,000 rank-0 and 10,000 rank-1 curves (stratified by conductor decile and torsion order — never files[:N] / lowest-conductor-first). On rank <= 1 the mirror's identity sha = round(Sha_an) is definitional, so requiring our reassembled Sha_an to reproduce `sha` there tests OUR Ω·∏cp against LMFDB's, not BSD. Record the empirical residual distribution r = |Sha_an − sha| / sha.
3. Freeze: tol := max(1e-4, p99.99 of the Phase 0 residual distribution). Freeze tol, the analysis script, and its sha256 hash in the preregistration commit BEFORE any rank >= 2 row is read. Also compute and record the ATTAINABLE residual range under double-precision `leading_term`/`regulator` so the gate is shown reachable and exceeds measurement error (SE/precision computed before the line is drawn, not after).

Phase 1 — Main run (full enumeration, no sampling).
4. For all 282,373 rank >= 2 curves: assemble Sha_an as above; compute m* = nearest integer whose square is closest to Sha_an; residual d = |Sha_an − m*²| / max(Sha_an, 1). Per-curve pass iff d < tol AND m* >= 1.
5. Aggregate at the isogeny-class level (a class fails if any member curve fails); report per-rank and per-conductor-decile pass rates with binomial CIs on n = 182,937 classes.
6. Tautology audit (gate, mechanical): emit the provenance DAG of every ingredient (leading_term ← lfunc pipeline; regulator, torsion ← ec/MW pipeline; Ω, ∏cp ← local recomputation from ainvs; `sha` ← EXCLUDED) and verify no edge of the DAG is the BSD identity itself. Run before the verdict is written; the audit artifact ships with the verdict.
7. Ship every failing row (ec_label, all ingredients, d, m*) in the SAME commit as the verdict. Exhibit rows regardless of verdict: the single rank-4 curve; the 10 largest-d passes; the 10 smallest-d failures.

Phase 2 — Only if Phase 1 produces failures above threshold: re-verify each failing curve with a high-precision recomputation of Ω (mpmath, 50 digits) before any BSD-inconsistency language is used; a failure that dissolves under precision is reclassified INSTRUMENT, not BSD.

Compute budget: pure Python/mpmath, ~300K curves × (AGM + Tate) ≈ well under one M1 CPU-day; $0 API.

## Controls

C1 (conductor conditioning): every comparative statement (rank 2 vs rank 3, pass-rate trends) is computed within conductor deciles; nothing rank-related is claimed unless it survives conductor matching. (Two prior rank-adjacent claims died exactly here: C-9334502f16d1, C-d151768c6740.)

C2 (perturbation null / power control): rerun the S1 statistic with Ω swapped for the Ω of a random other curve in the same conductor decile (1,000 draws, seeded). This breaks the arithmetic linkage while preserving marginal scale. The pass rate under the null is the false-pass floor of the instrument and is REPORTED NEXT TO the true pass rate.

C3 (pre-committed vacuous reading): if the C2 null pass rate >= 50%, the instrument has no discriminative power at the chosen tolerance and the whole Phase 1 result is read VACUOUS — no BSD-consistency claim in either direction. This reading is committed here, before data.

C4 (join-selection audit): `bsd_joined` covers 2.48M of 3.82M curves. Before Phase 1, compute join-coverage rates by rank × conductor decile on `ec_curvedata`. The population claim is scoped to the joined stratum; if rank >= 2 coverage differs from rank <= 1 coverage by > 5pp within any decile, a selection-bias flag ships with the verdict and all language of the form "curves of rank >= 2" is replaced by "joined curves of rank >= 2".

C5 (unit / clustering): curves within an isogeny class share an L-function and correlated inputs; all CIs and rates use n = isogeny classes (182,937), never n = curves (282,373). Per-curve numbers appear only as exhibits.

C6 (cross-pipeline provenance check, descriptive): `analytic_rank` (ec pipeline) vs `lfunc_analytic_rank` (lfunc pipeline) currently agree on 282,373/282,373 joined rank >= 2 rows (verified live during design). Re-emitted as a mechanical precondition check, not a finding — agreement on joined rows may be induced by the join itself.

## Preregistered falsifiers (each with an explicit numeric threshold)

F1 (instrument gate): Phase 0 calibration must reproduce stored `sha` on rank <= 1 within tol for >= 99.9% of the 20,000 calibration curves, ELSE the instrument is defective: fix, re-freeze, and do not open Phase 1. (Threshold: 99.9%; failing = < 19,980/20,000.)

F2 (power gate): the C2 perturbation null must pass at < 50%. Null pass rate >= 50.0% → VACUOUS verdict, no BSD claim either way.

F3 (primary, BSD-consistency): if > 0.1% of isogeny classes (i.e., > 183 of 182,937) fail S1 after Phase 2 precision re-verification, the verdict is BSD-SQUARE-INCONSISTENCY-CANDIDATES and every failing row ships in the verdict commit. If <= 0.1% fail, the verdict is CONSISTENT-AT-TOLERANCE with the exact tol and CI stated beside it.

F4 (residual-shape falsifier for H2): rank-2 vs rank-3 residual distributions compared by KS test within each conductor decile; H2 is refuted if KS p < 0.001 (Holm-corrected across deciles) in >= 2 deciles. Refutation of H2 does not touch H1.

F5 (selection falsifier): join coverage difference (rank >= 2 vs rank <= 1) > 5.0pp in any conductor decile → scope restriction fires automatically (C4 language substitution). This falsifies the "representative stratum" framing, not H1.

## Stopping rule

Fixed-scope, single-pass, full enumeration — no sampling at Phase 1, hence no optional stopping on the primary statistic. Hard sequence: Phase 0 → freeze (tol + hashed script committed) → Phase 1 (one pass) → Phase 2 only for failing rows → verdict. No threshold, tolerance, or stratification may change after the first rank >= 2 row is read; a discovered code bug forces: stop, fix, re-freeze with a new preregistration commit, restart Phase 1 from zero, and both preregistrations remain in history. The experiment ends at the first written verdict; there is no "run it again until it passes" branch. Total wall-clock cap: 3 M1 CPU-days; exceeding the cap → publish partial coverage with the coverage fraction in the verdict line.

## Unit of inference

Isogeny class (n = 182,937 on the rank >= 2 joined stratum). Curves within a class share the L-function and correlated BSD ingredients, so per-curve counting would inflate precision (per the SE-on-the-wrong-unit failure: n is the number of independent decisions, not the number of rows). Population: elliptic curves over Q present in BOTH mirror pipelines (the `bsd_joined` stratum), conductor <= 399,993 — never quoted as a property of "all elliptic curves" or even "all LMFDB curves" unless F5 stays silent.

## Prior work bearing on this design

- C-954b8ae3b448 (ESTABLISHED, Aporia, X-ae9d96172e49): BSD rank agreement perfect, 3,824,372/3,824,372. Ceiling: "Sha values at rank >= 2 are computed assuming BSD (circularity documented separately)." Rank agreement is therefore DONE and not re-run here; its ceiling is precisely the hole this proposal targets.
- C-e0352ce96e11 (OBSERVED, Mnemosyne, X-2997d9f4883a): "F005 cannot be used to verify BSD at rank >= 2 because Sha values on that stratum are themselves computed assuming BSD." QUALIFIES-relation R-5bf3380aedc9 onto C-954b8ae3b448. Source quote: "circular at rank ≥ 2 — computed assuming BSD."
- C-450a0c8756cf (RETRACTED, Harmonia, X-ffe21a879e15): F043 BSD–Sha anticorrelation was an algebraic-identity rearrangement (Pattern 30 Level 4 IDENTITY); evidence E-2d7e7912e4f8 cites the PATTERN_BSD_TAUTOLOGY precondition surface.
- C-96779c5836df (REFUTED, Mnemosyne): F028 Szpiro × Faltings ρ=0.97 killed as tautology — both sides encoded log|Disc|.
- C-9334502f16d1 (REFUTED, Harmonia, X-c93d51f26127): moment-hierarchy discrimination killed — "did not stratify families beyond what the underlying conductor / rank already explained"; gate was a marginal-preserving (conductor/rank) null.
- C-d151768c6740 (REFUTED, Harmonia, X-dc1c945891a3): OQ1 spectral-tail rank–spacing correlation killed by conductor conditioning.
- H-bac36ae694a2 (HYPOTHESIZED gap, Mnemosyne): mechanism=projection_equivalence × substrate_class=lmfdb_arithmetic is an untested cell (noted; this design does not claim to fill it).
- Repo doctrine applied: gate-exceeds-measurement-error and gate-shown-reachable (tolerance frozen from measured residuals, attainable range computed first); verdict-ships-rows; stratified sampling only; pre-committed vacuous reading; SE on the correct unit.

## Evidence Wiki consultation log (queries run + object ids retrieved)

Client: `EvidenceWiki(machine='M1', agent='V1B-T7-wiki')`, canonical_revision 521 (embedding index behind 0).

1. search_evidence("BSD Birch Swinnerton-Dyer rank agreement analytic rank elliptic curves") → C-954b8ae3b448, C-9334502f16d1, C-e0352ce96e11, C-894ed91b9ca5, C-e0b3b4966385, C-a3744a88ea5e, C-948eae5cb70c, C-d151768c6740, C-96a0e90f4eeb, C-450a0c8756cf.
2. search_evidence("Sha Tate-Shafarevich order verification LMFDB") → C-0c169dd6e0d9 (top hit) et al.
3. get_claim("C-e0352ce96e11") → claim + evidence E-f4eff097cabd (STRUCTURAL_ANALYSIS, negative=true, substrate "high-Sha (sha >= 9) elliptic curve stratum, LMFDB", quote above) + relation R-5bf3380aedc9 (QUALIFIES → C-954b8ae3b448). get_counterevidence("C-e0352ce96e11") → no counter-relations; negative evidence E-f4eff097cabd.
4. get_claim("C-954b8ae3b448") → evidence E-1fbd254ab7c8 (DETERMINISTIC_TEST, metric "3,824,372/3,824,372 rank agreement", gate "full-table check, no sampling"). get_counterevidence("C-954b8ae3b448") → counter-relation R-5bf3380aedc9 from C-e0352ce96e11.
5. related_findings("C-954b8ae3b448") → graph: C-e0352ce96e11 (1 hop); semantic: C-a3744a88ea5e, C-894ed91b9ca5, C-0c169dd6e0d9, C-9334502f16d1, C-450a0c8756cf, C-948eae5cb70c, C-e0b3b4966385, C-4f607db9b4a7, C-d0f2742bd8ed.
6. Negative-evidence/circularity query: search_evidence("circularity negative evidence rank 2 Sha computed assuming BSD calibration anchor") → C-e0352ce96e11, C-954b8ae3b448, C-450a0c8756cf, C-d0f2742bd8ed, C-0c169dd6e0d9, C-b3b4b28a3a62, C-96779c5836df, C-9334502f16d1, C-b037a49b641c, C-894ed91b9ca5.
7. contradictions() → one open pair: R-e68c9331eca2 (C-3a1c49fa5a78 vs C-3d12c440f087, D-5/D-8 executable-history effect, APPARENT_UNDER_DIFFERING_CONDITIONS) — not BSD-relevant; logged, no design impact.
8. find_gaps() → H-a86125892a3e, H-41f9f15ce208, H-bac36ae694a2 (lmfdb_arithmetic cell), H-c9832bd95134, H-7c607f34d50e, H-9b0a7922015e.
9. Follow-up detail reads: get_claim on C-450a0c8756cf (E-2d7e7912e4f8), C-9334502f16d1 (E-e2c3d903daeb), C-d151768c6740 (E-cdb670a5d454) for verbatim mechanism quotes.

## Evidence that changed this design (specific ids + the concrete design decision each changed)

- C-e0352ce96e11 (+ E-f4eff097cabd, R-5bf3380aedc9): forced the central design decision — the stored `sha` column is EXCLUDED from every verdict statistic at rank >= 2; the primary endpoint became square-integrality of an independently assembled Sha_an (with Ω and ∏cp recomputed locally from `ainvs`), because "recompute sha and compare" is circular by this claim. It also dictated the Phase 0 calibration placement: rank <= 1 only, and labeled instrument-calibration, never BSD evidence.
- C-954b8ae3b448 (+ ceiling text + E-1fbd254ab7c8): removed rank agreement as an endpoint (already ESTABLISHED at 100%, full-table, no sampling — re-running it would add nothing); demoted the rank-column comparison to precondition check C6; and its explicit ceiling ("Sha at rank >= 2 computed assuming BSD") selected the target of this experiment.
- C-450a0c8756cf and C-96779c5836df (E-2d7e7912e4f8; Pattern 30 IDENTITY kills): added the mandatory mechanical tautology audit (Design step 6 — provenance DAG with the BSD identity forbidden as an edge) and are the reason Ω and ∏cp must be recomputed from `ainvs` rather than rearranged out of stored BSD ingredients, which would have rebuilt exactly the F043/F028 failure.
- C-9334502f16d1 and C-d151768c6740 (E-e2c3d903daeb, E-cdb670a5d454): two rank-adjacent claims died under conductor conditioning — this added C1 (all comparative statements within conductor deciles), shaped F4 (H2 is tested decile-wise with Holm correction), and caused the deliberate REMOVAL of a planned zero-statistics (z1) secondary endpoint from this proposal.
- contradictions() R-e68c9331eca2 and gaps H-a86125892a3e/H-41f9f15ce208/H-c9832bd95134/H-7c607f34d50e/H-9b0a7922015e: consulted, not BSD-relevant, no design change (logged per protocol; cited here only as consulted-and-rejected).
