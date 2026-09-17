"""Cut: linpackd-netlib-1979 (the LINPACK benchmark program linpackd.f; ancestry-aware, Stage A DEEP; SOURCE_READ on M3; position 37
of the 2026-09-17 NOT_CUT order). Read: linpackd.f in full (802 lines): the driver 1-205 (timing cases, residual check, mflops),
dgefa 232-334, dgesl 335-451 (head), the BLAS-1 kernels daxpy/ddot/dscal/idamax 452-586, epslon 587-627, dmxpy 628-802 (head).
Nothing ran (Fortran 77; no compiler on M3). One file; nothing unread except dgesl/dmxpy bodies past their heads.
"""
from nyx.atlas.author import Cut

F = "vault:linpackd-netlib-1979/upstream/linpackd.f"
c = Cut("linpackd-netlib-1979", mode="ANCESTRY_AWARE", inspected=["linpackd.f 1-802"], evidence=[("SOURCE_READ", F + ":1-205"), ("SOURCE_READ", F + ":232-334"), ("SOURCE_READ", F + ":452-627")],
        note="LU factorisation with partial pivoting written as a loop over columns calling three BLAS-1 kernels (idamax, dscal, daxpy) so that the machine-specific work is in the kernels; wrapped in a benchmark driver that times the factor/solve, checks a normalised residual, and reports MFLOPS against a fixed operation count 2n^3/3 + 2n^2. The mechanism of interest is the second: a benchmark whose score is defined by a formula, not by the work actually done")

lu = c.organ("gaussian_elimination_with_partial_pivoting_by_columns_delegating_to_three_vector_kernels", human_name="dgefa (232-334): idamax for the pivot, dscal for the multipliers, daxpy for the rank-one update per column; ipvt; info = k on a zero pivot", status="ACCEPTED",
    mechanism="for each column k: find the largest magnitude below the diagonal (idamax), record it, swap if needed, scale the column below the diagonal by -1/pivot (dscal), then for each later column swap the pivot row element and add the multiplier column times that element (daxpy); a zero pivot sets info = k and skips the column ('not an error condition for this subroutine')",
    input="an n x n matrix", output="L and U in place, pivots", state="none", update="per column", assumptions=["partial pivoting suffices for stability in practice; the column orientation matches Fortran storage so the daxpy runs on contiguous memory"],
    fitness_value_in_ancestor="the inner loops are three tiny routines that vendors could hand-tune: the BLAS idea", failure_landscape="by reading: no growth-factor check (Wilkinson's worst case is not detected); the benchmark's residual check is the only guard",
    human_prior="Gaussian elimination as in Forsythe & Moler 1967; the BLAS-1 factoring is Lawson, Hanson, Kincaid, Krogh 1979", evidence_ref=F + ":232-334", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="dgefa + the three kernels",
    coverage={"input_topology": "MATRIX", "output_topology": "MATRIX", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP", "order_sensitivity": "SENSITIVE"})

bench = c.organ("benchmark_that_scores_a_machine_by_a_fixed_nominal_operation_count_over_measured_wall_time_and_validates_by_a_normalised_residual", human_name="the driver (20-205): ops = 2n^3/3 + 2n^2; time(i,4) = ops/(1e6 total); residn = resid/(n norma normx eps); the 'Please send the results of this run to Jack Dongarra' header; matgen with the 1992 RNG fix", status="ACCEPTED",
    mechanism="generate a random matrix (matgen; the 1992 note says the earlier generator's short period 'produced singular matrices occasionally'); time dgefa and dgesl separately with a wall-clock function; compute the residual b - A x with a fresh copy of A and normalise it by n, the matrix norm, the solution norm and machine epsilon; report MFLOPS as the NOMINAL operation count divided by time, the 'unit' as 2/MFLOPS, and the ratio to a Cray reference; repeat the timing three ways (single, ten averaged, with matgen time subtracted) and for two leading dimensions; the 2003 HP note says the loop was changed 'to prevent compilers from optimizing away dgesl code'",
    input="n (100 by convention), lda", output="a table of times and MFLOPS, and residn", state="none", update="per run", assumptions=["the operation count of the algorithm is a property of n, not of the compiled code; a machine that finishes faster did more useful arithmetic per second (which vendor tuning of the kernels, and later compiler elision, both attacked)"],
    fitness_value_in_ancestor="one number per machine, comparable across two decades; the TOP500's ancestor", failure_landscape="by reading: the two revision notes in the header ARE the failure landscape: a generator that produced singular matrices (1992) and compilers that removed the timed work (2003); the residual check exists because a fast wrong answer must not score",
    human_prior="Dongarra's 1979 LINPACK timing table; the score formula is the benchmark's definition", evidence_ref=F + ":1-205", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the driver",
    coverage={"input_topology": "SCALAR", "output_topology": "VECTOR", "state_amount": "NONE", "stochasticity": "SEEDED_RANDOM", "resource_dependence": "TIME", "uncertainty": "POINT"})

c.reject("daxpy / ddot / dscal / idamax with their 'clean-up loop' unrolling by 4 and 5, epslon, dmxpy (a 16-way unrolled matrix-vector product)", reason="BELOW_MEANINGFUL_GRAIN", evidence=F + ":452-802", note="the unrolling is the 1979 vector-machine idiom; a tuning, not a mechanism")
c.reject("dgesl (the triangular solves) past its head", reason="OTHER", evidence="NOT READ in full; the mirror of dgefa's structure")
c.reject("'LINPACK' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the factorisation and the benchmark protocol are separable; the second is what survived (HPL)")

c.edge(lu, bench, "feeds", note="the timed work")

c.pressure("a_single_number_must_rank_machines_on_a_fixed_computation_while_the_machines_and_their_compilers_adapt_to_the_number",
    condition="a benchmark defines its score by a nominal operation count over measured time; the parties being scored control the kernels and the compiler; a wrong answer must not score", resource_or_constraint="one fixed problem size and formula; a residual check",
    failure_condition="the score rising without the useful work rising (elided loops, tuned kernels that change the algorithm), or a singular test matrix scoring", world_punishes="timing code the compiler can prove dead; a generator with a short period", world_rewards="a residual check normalised to machine epsilon; work the optimiser cannot remove",
    observable_consequence="reported MFLOPS vs independently counted floating-point operations across compilers and optimisation levels, and the residn distribution over seeds", vacuity_condition="a single fixed machine and compiler", trivial_shortcuts="reporting the nominal count as the measured one (which is what the formula does: the pressure is that this is only honest while the work is really done)",
    cheat_control="an organism with a compiler that elides dgesl must show MFLOPS above the hardware's peak (a detectable lie); the 1992-fixed generator must show zero singular matrices over many seeds where the old one showed some: the world must show both",
    cost_class="CPU-scale", source_evidence="linpackd.f header notes (1992, 2003); the driver's residual and ops lines", purpose="PURPOSE: machine performance measurement (Dongarra 1979-)")

c.ancestry("historical_version_of", "LINPACK (Dongarra, Bunch, Moler, Stewart 1979); this driver's revisions 1992 (RNG) and 2003 (HP: anti-elision)", note="from the header comments")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["dgesl and dmxpy bodies past their heads", "nothing ran"], note="one 802-line file; both mechanisms read; the benchmark's two revision notes are the most informative lines in it")
c.save(state="DEEP")
