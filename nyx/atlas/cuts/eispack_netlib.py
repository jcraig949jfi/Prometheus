"""Cut: eispack-netlib (EISPACK as served by netlib, 71 Fortran routines; ancestry-aware, Stage A COARSE; SOURCE_READ on M3; position 66 of
the 2026-09-17 NOT_CUT order). Read: the file list; the header comments of balanc.f, tred2.f, tql2.f, hqr.f (each 'a translation of the
algol procedure ... Handbook for Automatic Computation vol. II'). NOT read: any routine body; the drivers (rs, rg, ch, cg, rsg, svd); the
generalised (qz*) and banded routines. Nothing ran (Fortran; no compiler on M3). An inventory cut of a library whose organisation is
itself the mechanism of note.
"""
from nyx.atlas.author import Cut

B = "vault:eispack-netlib/upstream/balanc.f"; T2 = "vault:eispack-netlib/upstream/tred2.f"; TQ = "vault:eispack-netlib/upstream/tql2.f"; HQ = "vault:eispack-netlib/upstream/hqr.f"
c = Cut("eispack-netlib", mode="ANCESTRY_AWARE", inspected=["file list (71 routines)", "balanc.f, tred2.f, tql2.f, hqr.f header comments"], evidence=[("SOURCE_READ", B + ":1-30"), ("SOURCE_READ", T2 + ":1-30"), ("SOURCE_READ", TQ + ":1-30"), ("SOURCE_READ", HQ + ":1-40")],
        note="eigenvalue computation as a pipeline of separately published, separately callable stages, each a Fortran translation of a Wilkinson-Reinsch Handbook Algol procedure with its Numerische Mathematik citation in the header: balance (scale and permute), reduce (to tridiagonal for symmetric matrices, to Hessenberg for general ones), iterate (implicit QL with shifts on the tridiagonal, Francis QR on the Hessenberg), back-transform; the drivers (rs, rg, ...) are a few calls each; the organisation, not any single routine, is what the library contributed")

pipe = c.organ("eigenproblem_as_a_pipeline_of_separately_callable_stages_balance_reduce_iterate_back_transform_each_a_literal_translation_of_a_published_algol_procedure", human_name="balanc (Parlett & Reinsch 1969) / balbak; tred1 / tred2 (Martin, Reinsch, Wilkinson 1968) / trbak1; elmhes / orthes / ortran; tql1 / tql2 (Bowdler et al. 1968); hqr / hqr2 (Martin, Peters, Wilkinson 1970); imtql*, tqlrat, bisect, tinvit, tsturm; drivers rs, rg, rsg, ch, cg, svd", status="ACCEPTED",
    mechanism="a general real matrix is balanced (diagonal scaling by powers of two and permutation to isolate eigenvalues), reduced to upper Hessenberg form by elimination or orthogonal transformations, its eigenvalues found by the shifted QR iteration, and eigenvectors recovered by back-substitution and back-transformation; a symmetric matrix is reduced to tridiagonal by Householder transformations and iterated by implicit QL; each stage is a routine whose header names its Algol source and page, and the drivers call them in the canonical order",
    input="a matrix", output="eigenvalues (and vectors)", state="none", update="per call", assumptions=["the Handbook's procedures are correct and numerically analysed (Wilkinson 1965); translation preserves the analysis; users compose stages for special structure"],
    fitness_value_in_ancestor="the first portable, tested, reference eigen-library (Argonne 1972-76); every stage's provenance is in its header", failure_landscape="by reading: no blocking, no BLAS, column-by-column loops (the reason LAPACK replaced it; the record's lineage)", human_prior="Wilkinson & Reinsch 1971 Handbook vol. II", evidence_ref="the four headers read; the file list", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the library's organisation; MEDIUM because no body was read",
    coverage={"input_topology": "MATRIX", "output_topology": "VECTOR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP"})

bal = c.organ("balancing_by_powers_of_two_scaling_and_permutation_to_isolate_eigenvalues_before_reduction", human_name="balanc.f ('balances a real matrix and isolates eigenvalues whenever possible'); balbak restores the vectors", status="CANDIDATE",
    mechanism="rows and columns whose off-diagonal parts are zero are permuted to the ends (their diagonal entries are eigenvalues with no iteration); the remaining block is scaled by a diagonal similarity with powers of the machine radix so row and column norms are comparable, which does not change eigenvalues and improves the conditioning of the later stages; the permutation and scaling are recorded for the back-transformation",
    input="a real matrix", output="a balanced matrix and low/igh indices", state="none", update="per call", assumptions=["scaling by exact powers of two introduces no rounding error"],
    fitness_value_in_ancestor="eigenvalue accuracy on badly scaled matrices at negligible cost", failure_landscape="UNKNOWN by run", human_prior="Parlett & Reinsch 1969", evidence_ref=B + ":1-30 (header only)", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="balanc / balbak; CANDIDATE because the body was not read",
    coverage={"input_topology": "MATRIX", "output_topology": "MATRIX", "state_amount": "NONE", "stochasticity": "DETERMINISTIC"})

c.reject("every routine body; the generalised eigenproblem (qzhes, qzit, qzval, qzvec), the banded and packed variants, the complex routines (comqr, cinvit, ...), svd / minfit, the bisection and inverse-iteration paths", reason="OTHER", evidence="NOT READ; residue", note="hqr's Francis double-shift and tql2's implicit shift are each a mechanism worth a DEEP read (both are still the algorithms in LAPACK's kernels)")
c.reject("'eigensolver' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the library IS a decomposition of the solver into stages; the atlas records that decomposition")

c.edge(bal, pipe, "feeds")

c.pressure("eigenvalues_of_general_and_symmetric_matrices_must_be_computed_reliably_across_machines_and_matrix_structures_from_a_set_of_stages_that_can_be_composed_and_replaced_one_at_a_time",
    condition="an organism computes eigen-decompositions of matrices with varied structure (symmetric, general, banded, generalised) on machines with different arithmetic; the score is accuracy against a reference and portability; users need to substitute or skip stages", resource_or_constraint="Fortran 66/77; no vendor code",
    failure_condition="wrong eigenvalues on badly scaled or ill-conditioned inputs, or a monolith that cannot be adapted to structure", world_punishes="a single black-box routine; unbalanced iteration", world_rewards="published, analysed stages with recorded provenance and drivers that compose them",
    observable_consequence="eigenvalue error vs a reference on the Handbook's test matrices with balancing on and off, and with each stage replaced by its alternative (elmhes vs orthes; tql vs imtql)", vacuity_condition="small well-conditioned matrices", trivial_shortcuts="a modern LAPACK call (which the world withholds)",
    cheat_control="an organism given the reference eigenvalues must reproduce them to working precision; the pipeline with balancing removed must lose accuracy on the scaled test matrix; the two Hessenberg reductions must agree to round-off on well-conditioned inputs: the world must show all three",
    cost_class="CPU-scale", source_evidence="the routine headers; the drivers' call order", purpose="PURPOSE: reference eigenvalue software (Argonne 1972-76; Wilkinson & Reinsch 1971)")

c.ancestry("port_of", "the Algol procedures of the Wilkinson-Reinsch Handbook (1971), translated at Argonne (Smith, Boyle, Dongarra, Garbow, Ikebe, Klema, Moler)", note="from the headers")
c.residue("LARGE_RESIDUE", ["no routine body read", "nothing ran"], note="an inventory cut; the library's organisation is recorded as the mechanism, with balancing as one CANDIDATE stage")
c.save(state="COARSE")
