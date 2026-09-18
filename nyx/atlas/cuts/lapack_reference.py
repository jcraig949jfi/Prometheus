"""Cut: lapack-reference (LAPACK, Anderson et al.; Stage A COARSE, narrow per the 2026-09-18 directive; SOURCE_READ on M3; position 84 of
the 2026-09-17 NOT_CUT order). Read: SRC/dgetrf.f header and structure (the blocked right-looking LU: NB from ILAENV, DGETRF2 on the
panel, DLASWP row swaps, DTRSM, DGEMM), SRC/dgetrf2.f header (the recursive panel). NOT read: any routine body; the 6,700 other files;
the BLAS. Nothing ran (Fortran; no compiler on M3). The atlas's linpackd-netlib-1979 cut holds the LINPACK ancestor this supersedes.
"""
from nyx.atlas.author import Cut

G = "vault:lapack-reference/upstream/tree/lapack-reference/SRC/dgetrf.f"; G2 = "vault:lapack-reference/upstream/tree/lapack-reference/SRC/dgetrf2.f"
c = Cut("lapack-reference", mode="ANCESTRY_AWARE", inspected=["SRC/dgetrf.f header + call structure", "SRC/dgetrf2.f header"], evidence=[("SOURCE_READ", G + ":1-215"), ("SOURCE_READ", G2 + ":1-80")],
        note="the successor in the dense-linear-algebra pair (LINPACK is the predecessor): the LU factorisation is BLOCKED so that a panel of NB columns is factored, its pivots applied across the matrix, the panel's triangular part solved against the trailing block (DTRSM), and the trailing block updated by a matrix-matrix product (DGEMM); the block size NB is chosen per machine by ILAENV, and the panel itself is factored recursively (DGETRF2 splits M-by-N into two halves). The point is that the heavy work is Level-3 BLAS, so data loaded into cache is reused O(NB) times")

blk = c.organ("blocked_right_looking_lu_that_factors_a_panel_applies_its_pivots_across_the_matrix_solves_the_triangular_panel_and_updates_the_trailing_block_by_a_matrix_matrix_product", human_name="DGETRF (dgetrf.f): NB = ILAENV(1, 'DGETRF', ...); loop over panels of JB columns: DGETRF2 on the panel, DLASWP to apply pivots left and right, DTRSM to solve the L11 U12 block, DGEMM to update A22 = A22 - L21 U12", status="ACCEPTED",
    mechanism="the matrix is processed in column panels of width NB; each panel is factored (with partial pivoting) by DGETRF2, the row interchanges it chose are applied to the columns on both sides of the panel by DLASWP, the upper block of the current column band is solved against the panel's unit-lower-triangular part by DTRSM, and the trailing submatrix is updated by a single DGEMM; because the update is a matrix-matrix product, each element brought into cache is used NB times, unlike LINPACK's rank-1 DAXPY updates that touch each element once",
    input="an M-by-N matrix", output="L, U in place, pivots", state="none", update="per panel", assumptions=["the machine has a memory hierarchy where reuse dominates flop count, so casting the work as Level-3 BLAS is the win (the LAPACK thesis); ILAENV knows a good NB per architecture"],
    fitness_value_in_ancestor="near-peak dense factorisation on cache machines; the reason LAPACK replaced LINPACK/EISPACK (the record names this the winner of the pair)", failure_landscape="by reading: performance depends entirely on the tuned BLAS behind DGEMM; a reference BLAS gives correct but slow results (the point of the pressure)", human_prior="Anderson et al. 1992 (LAPACK); Dongarra, Du Croz, Hammarling, Duff 1990 (Level-3 BLAS)",
    evidence_ref=G + ":160-215", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="DGETRF; MEDIUM because only the header and call structure were read",
    coverage={"input_topology": "MATRIX", "output_topology": "MATRIX", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP", "resource_dependence": "MEMORY"})

rec = c.organ("recursive_panel_factorisation_that_splits_the_panel_into_two_column_halves_so_the_update_within_the_panel_is_also_a_matrix_matrix_product", human_name="DGETRF2 (RECURSIVE SUBROUTINE): divide N into N1, N2; factor the left half, apply its pivots and DTRSM to the right half, DGEMM-update the right half, recurse on it", status="CANDIDATE",
    mechanism="the panel that DGETRF factors is itself factored by halving its columns and recursing, so even the panel's internal update is a DGEMM rather than a sequence of rank-1 updates; the recursion bottoms out at a single column (IDAMAX pivot, DSCAL)", input="an M-by-N panel", output="its LU", state="none", update="per recursion",
    assumptions=["recursion turns the panel factorisation into cache-efficient Level-3 work too (Toledo 1997)"], fitness_value_in_ancestor="the panel is no longer a Level-2 bottleneck", failure_landscape="UNKNOWN by run", human_prior="Toledo 1997 (recursive LU); Gustavson 1997", evidence_ref=G2 + ":1-80 (header only)", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="DGETRF2; CANDIDATE because the body was not read",
    coverage={"input_topology": "MATRIX", "output_topology": "MATRIX", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "update_topology": "RECURSIVE"})

c.reject("every routine body; the eigenvalue and SVD drivers (the EISPACK successors), the QR/Cholesky/least-squares paths, the banded and packed forms, ILAENV's tuning tables, the BLAS, LAPACKE and the tests (6,700+ files)", reason="OTHER", evidence="NOT READ; residue", note="per the 2026-09-18 directive s1: no deepening of large COARSE bodies without a downstream question")
c.reject("'linear algebra library' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="LAPACK is hundreds of routines over the same blocked-BLAS idea; the atlas records the idea via one factorisation")

c.edge(rec, blk, "feeds", note="DGETRF2 is DGETRF's panel")

c.pressure("a_dense_matrix_factorisation_must_run_near_the_machine_peak_across_architectures_with_different_cache_hierarchies_while_the_numerical_algorithm_stays_identical_and_portable",
    condition="an organism factorises dense matrices on machines whose speed is bounded by memory bandwidth, not flop rate; the numerical result must be identical everywhere; the tuned kernel differs per machine", resource_or_constraint="cache; a tuned Level-3 BLAS per target",
    failure_condition="a portable code that runs at a fraction of peak because it reuses cached data O(1) times (LINPACK's Level-1 form)", world_punishes="rank-1 updates; unblocked factorisation", world_rewards="blocking so the update is a matrix-matrix product with O(NB) reuse",
    observable_consequence="fraction of peak on the LINPACK benchmark for the Level-1 (linpackd) vs Level-3 (dgetrf) formulations on the same host with a tuned BLAS, at identical residual", vacuity_condition="matrices smaller than the cache", trivial_shortcuts="a vendor library (which the world may allow as the tuned-BLAS control)",
    cheat_control="an organism with a perfectly tuned BLAS must approach peak; the unblocked LINPACK form must show the memory-bound ceiling; both must give the same residual: the world must show both", cost_class="CPU-scale",
    source_evidence="dgetrf.f blocking; dgetrf2.f recursion; the record's LINPACK-vs-LAPACK framing", purpose="PURPOSE: portable near-peak dense linear algebra (Anderson et al. 1992-)")

c.ancestry("historical_version_of", "linpackd-netlib-1979 / linpack-netlib-1979 (in this atlas): the same LU functionality recast in Level-3 BLAS; EISPACK's eigen routines likewise", note="from the record")
c.residue("LARGE_RESIDUE", ["only DGETRF's header and structure read; one CANDIDATE organ", "the eigen/SVD/QR drivers and the BLAS unread", "nothing ran"], note="inventory by the directive; the blocked-BLAS mechanism is located and tied to the LINPACK ancestor")
c.save(state="COARSE")
