"""Cut: eispack-netlib-1976 (ancestry-aware; SOURCE_READ of tql2.f, tred2.f, pythag.f, epslon.f, rs.f in full; tql1/tred1/tqlrat
not read -- they are the eigenvalues-only twins per rs.f's dispatch)."""
from nyx.atlas.author import Cut

B = "F:/Prometheus/vault/fossils/eispack-netlib-1976/upstream/"
c = Cut("eispack-netlib-1976", mode="ANCESTRY_AWARE", inspected=["tql2.f", "tred2.f", "pythag.f", "epslon.f", "rs.f", "harness/driver.f (listed, not read)"],
        evidence=[("SOURCE_READ", B + "tql2.f"), ("SOURCE_READ", B + "tred2.f"), ("SOURCE_READ", B + "pythag.f")],
        note="SUPERSEDED (by LAPACK) per Techne; 1976 code in a world with no floating-point standard: three of its mechanisms exist because the arithmetic was unknown")

hh = c.organ("householder_reduction_to_tridiagonal_with_accumulated_transforms", human_name="tred2", status="ACCEPTED",
    human_interpretation="reduce a full symmetric matrix to tridiagonal form by orthogonal similarity, keeping the transforms",
    mechanism="for each row from the last upward: form a reflection vector from the row's leading part, apply it as a symmetric rank-2 update to the remaining leading block (z := z - f e^T - g d^T computed column by column), storing the reflection vector in the eliminated row/column of z; a second pass from the top accumulates the stored reflections into an explicit orthogonal matrix by applying each to the columns already formed",
    input="n x n symmetric a", output="diagonal d, subdiagonal e, orthogonal z", state="a/z overwritten in place; d, e as work", update="n-1 reflections then n-1 accumulations", assumptions=["symmetry (only one triangle is referenced)"],
    fitness_value_in_ancestor="turns an O(n^3) dense eigenproblem into an O(n^2)-per-sweep tridiagonal one", evidence_ref=B + "tred2.f", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN",
    source_boundary="tred2 loops 300 and 500", coverage={"input_topology": "MATRIX", "output_topology": "MATRIX", "state_amount": "SUPERLINEAR", "update_topology": "SWEEP", "stochasticity": "DETERMINISTIC"})

c.organ("scale_row_before_norm", parent=hh, human_name="the `scale` guard", status="ACCEPTED",
    mechanism="before squaring the entries of a row to get its norm, divide them all by the sum of their absolute values; a zero sum short-circuits the reflection entirely (the row is already reduced)",
    input="a row of length l", output="scaled row + scale factor", state="none", update="none", assumptions=["|sum| is representable when the squares might not be"],
    fitness_value_in_ancestor="prevents overflow/underflow in the norm on 1976 arithmetic with narrow exponent ranges", evidence_ref=B + "tred2.f loops 120-150", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN",
    source_boundary="tred2 lines scale=..., d(k)=d(k)/scale", coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "NONE", "failure_mode": "CORRUPTS"})

ql = c.organ("implicit_ql_iteration_with_shift", human_name="tql2", status="ACCEPTED",
    human_interpretation="find all eigenvalues of a symmetric tridiagonal matrix by repeated shifted orthogonal transforms",
    mechanism="for each leading index l: find the first negligible subdiagonal below it (deflation point m); if m > l compute a shift from the leading 2x2 block (a root of its characteristic quadratic via pythag), subtract it from the trailing diagonal (accumulating the total shift in f), then run a sweep of plane rotations from m-1 down to l that chases the bulge and updates d, e and the columns of z; repeat until e(l) is negligible; at most 30 iterations per eigenvalue else exit with ierr = l",
    input="d, e (tridiagonal), z", output="eigenvalues in d (sorted), eigenvectors in z, ierr", state="d, e, z in place; accumulated shift f; iteration counter j", update="one QL sweep per iteration",
    assumptions=["e(n) = 0 sentinel", "convergence within 30 iterations"], fitness_value_in_ancestor="cubic convergence with the shift; the whole spectrum from one loop",
    failure_landscape="ierr = l after 30 iterations -- eigenvalues 1..l-1 are correct but unsorted (documented)", evidence_ref=B + "tql2.f", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN",
    source_boundary="tql2 loop 240", coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "SUPERLINEAR", "update_topology": "SWEEP", "failure_mode": "STALLS", "recovery": "DEGRADES_GRACEFULLY", "temporal_horizon": "EPISODE"})

c.organ("deflate_where_addition_leaves_the_sum_unchanged", parent=ql, human_name="tst2 .eq. tst1 convergence test", status="ACCEPTED",
    human_interpretation="a subdiagonal is negligible when adding it to the local scale does not change the scale",
    mechanism="tst1 = running max of |d(l)|+|e(l)|; the test is literally whether tst1 + |e(m)| == tst1 in floating point -- the machine's own rounding IS the tolerance; no epsilon parameter exists",
    input="e(m), tst1", output="deflate or continue", state="tst1", update="max", assumptions=["rounding is monotone and the sum rounds to the larger operand when the smaller is below half an ulp"],
    fitness_value_in_ancestor="portable across 1976 arithmetics without knowing their epsilon; on extended-precision registers (later x87) this test behaves differently -- a known fossil pathology, NOT measured here",
    failure_landscape="a compiler that keeps tst2 in a wider register never sees equality -> more iterations or the 30-cap",
    evidence_ref=B + "tql2.f lines 'look for small sub-diagonal element'", confidence="HIGH on mechanism", portability="YES", compatibility="YES", utility="UNKNOWN",
    source_boundary="do 110 loop", coverage={"input_topology": "SCALAR", "output_topology": "DECISION", "state_amount": "CONSTANT", "representation_sensitivity": "SENSITIVE"})

c.organ("plane_rotation_sweep_with_vector_accumulation", parent=ql, human_name="Givens sweep + 'form vector'", status="ACCEPTED",
    mechanism="from the bottom of the unreduced block upward, each step computes a rotation (c, s) from the current bulge via pythag, applies it to two adjacent diagonal/subdiagonal entries, and applies the same rotation to two adjacent columns of z (the inner loop over k = 1..n)",
    input="d, e segment, z columns", output="rotated d, e, z", state="c, s, c2, c3, s2 carried between steps", update="m-l rotations per sweep", assumptions=[],
    fitness_value_in_ancestor="the eigenvector accumulation is the whole cost difference between tql2 and tql1", evidence_ref=B + "tql2.f loop 200/180", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN",
    source_boundary="do 200 ... do 180", coverage={"input_topology": "VECTOR", "output_topology": "MATRIX", "update_topology": "SWEEP"})

py = c.organ("hypotenuse_by_convergent_rescaling", human_name="pythag", status="ACCEPTED",
    human_interpretation="sqrt(a^2 + b^2) without overflow or underflow",
    mechanism="p = max(|a|,|b|), r = (min/max)^2; iterate t = 4 + r; if t == 4 stop; s = r/t; u = 1 + 2s; p *= u; r *= (s/u)^2 -- p converges to the hypotenuse using only ratios <= 1 and multiplications by u in [1, 1.5]; the stopping test is again floating-point equality (4 + r == 4)",
    input="a, b", output="hypot", state="p, r", update="iterative, ~3-4 rounds in double", assumptions=["squaring the ratio cannot overflow"], fitness_value_in_ancestor="called at every rotation and shift; no sqrt of a sum of squares anywhere in the package",
    failure_landscape="none for finite inputs", evidence_ref=B + "pythag.f", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="function pythag",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "update_topology": "RECURSIVE", "failure_mode": "NONE_KNOWN"})

ep = c.organ("probe_machine_epsilon_by_arithmetic", human_name="epslon", status="ACCEPTED",
    mechanism="a = 4/3; b = a - 1; c = b + b + b; eps = |c - 1|; repeat while eps == 0 -- the rounding error of representing 4/3 in the machine's base, tripled, exposes one unit in the last place; returns eps * |x|",
    input="x", output="a relative tolerance at x", state="none", update="loop until nonzero (guards against arithmetics where 4/3 happens to be exact -- none, but 1976 could not be sure)",
    assumptions=["radix 2 or a radix where 4/3 is inexact"], fitness_value_in_ancestor="a portable tolerance where no standard defined one", evidence_ref=B + "epslon.f", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN",
    source_boundary="function epslon", coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "NONE", "representation_sensitivity": "SENSITIVE"})

c.organ("selection_sort_of_eigenpairs", parent=ql, human_name="order eigenvalues and eigenvectors", status="CANDIDATE",
    mechanism="for each position find the smallest remaining eigenvalue and swap it (and its eigenvector column) into place",
    input="d, z", output="ascending d, matching z", state="none", update="n passes", fitness_value_in_ancestor="a documented output contract (ascending order); quadratic but n is small next to the QL cost",
    evidence_ref=B + "tql2.f loop 300", confidence="HIGH (trivial); flagged CANDIDATE because it sits at the grain boundary with generic sorting", portability="YES", compatibility="YES", utility="N/A",
    source_boundary="do 300", coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "update_topology": "SWEEP"})

c.organ("dispatch_on_whether_vectors_are_wanted", human_name="rs", status="CANDIDATE",
    mechanism="if eigenvectors are not wanted call the cheaper twins (tred1 + tql1) that skip the accumulation; else tred2 + tql2; an n > nm dimension check returns ierr = 10n",
    input="matz flag", output="a choice of path", state="none", update="none", fitness_value_in_ancestor="halves the work when vectors are unneeded", evidence_ref=B + "rs.f", confidence="HIGH", portability="YES", compatibility="YES", utility="N/A",
    source_boundary="subroutine rs", coverage={"input_topology": "SCALAR", "output_topology": "DECISION", "state_amount": "NONE"})

c.reject("tqlrat (rational QL variant)", reason="EFFECT_FROM_ENVIRONMENT",
         evidence=B + "rs.f: '*  tqlrat encounters catastrophic underflow on the Vax' -- the call is commented out and tql1 substituted; the file tqlrat.f is still in the body, unreachable",
         note="a mechanism disabled by its environment and left in place: fossil evidence of a 1983 repair. Not read.")
c.reject("epsilon / tolerance parameter", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY",
         evidence="no tolerance is passed anywhere; every convergence decision in tql2 and pythag is a floating-point equality test. A reader expecting a 'tol' input would be inventing it")
c.reject("the 30-iteration cap as a mechanism", reason="BELOW_MEANINGFUL_GRAIN", evidence="a constant compared to a counter; recorded in the QL organ's failure landscape instead")
c.reject("Fortran storage conventions (column-major, nm leading dimension)", reason="GENERIC_LANGUAGE_MECHANICS", evidence="nm/n distinction and z(k,i) indexing")

c.edge(hh, ql, "feeds", note="d, e, z from tred2 into tql2"); c.edge(py, ql, "feeds", note="every rotation and the shift")
c.edge(ql, "selection_sort_of_eigenpairs", "feeds"); c.edge("dispatch_on_whether_vectors_are_wanted", hh, "selects"); c.edge("dispatch_on_whether_vectors_are_wanted", ql, "selects")
c.edge("deflate_where_addition_leaves_the_sum_unchanged", ql, "gates", note="decides when a subproblem splits off")
c.edge(ep, "WHOLE_SYSTEM", "feeds", note="epslon is in the body but NOT called by rs/tred2/tql2 -- it serves other EISPACK paths; here it is present, unused")

c.pressure("arithmetic_of_unknown_precision_and_range",
    condition="the code must run on many machines whose floating-point base, precision and exponent range differ and are not queryable", resource_or_constraint="no standard, no parameters",
    failure_condition="a tolerance right for one machine is wrong for another: false convergence or non-termination", world_punishes="hard-coded epsilons; norms that overflow", world_rewards="letting the arithmetic itself decide (equality tests, probing 4/3, ratio-only hypotenuse)",
    observable_consequence="three organs (deflate test, pythag, epslon) exist only because of this", vacuity_condition="a single known arithmetic (post-1985 IEEE 754)", trivial_shortcuts="double everything",
    cheat_control="run under x87 extended precision vs SSE and count iterations (not run)", cost_class="a few extra operations per test", source_evidence="record.human_environmental_pressure 'heterogeneous floating point' + source", purpose="PURPOSE: eigenvalues of symmetric matrices")
c.pressure("clustered_or_repeated_eigenvalues",
    condition="eigenvalues close together slow the shifted iteration and make deflation ambiguous", resource_or_constraint="iterations per eigenvalue", failure_condition="30 iterations exceeded (ierr)",
    world_punishes="unshifted iteration", world_rewards="a good shift and a deflation test that recognises decoupling", observable_consequence="ierr path with partial results", vacuity_condition="well-separated spectrum",
    trivial_shortcuts="none", cheat_control="Techne's entry point: 'feed matrices with clustered or degenerate eigenvalues' (not run)", cost_class="iterations", source_evidence="tql2 header + ierr contract", purpose="PURPOSE: same")

c.residue("PARTIALLY_EXPLAINED", ["tred1/tql1/tqlrat (the no-vectors path) not read; assumed twins of tred2/tql2 per rs.f", "harness/driver.f not read: the oracle matrix is Techne's"],
          note="the vectors path (rs with matz != 0) is fully accounted for by 7 organs")
c.save(state="DEEP")
