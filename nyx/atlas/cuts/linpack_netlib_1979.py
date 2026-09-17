"""Cut: linpack-netlib-1979 (the record says 'LINPACK the library'; the body is the benchmark driver linpackd.f plus six separately-filed
kernels; Stage A COARSE; SOURCE_READ on M3; position 56 of the 2026-09-17 NOT_CUT order). Read: the file list; linpackd.f is BYTE-IDENTICAL
(md5 e43e84f43cb4997c0c3996c7d673cb3c) to linpackd-netlib-1979's body, cut DEEP in this atlas; daxpy.f / ddot.f / dscal.f / idamax.f /
dgefa.f / dgesl.f are the same routines split out (headers read). NOT in the body: dgeco, dgedi, dpofa, dqrdc, dsvdc, the banded and
symmetric drivers -- the library the record's lineage describes. Nothing ran.
"""
from nyx.atlas.author import Cut

D = "vault:linpack-netlib-1979/upstream/daxpy.f"; G = "vault:linpack-netlib-1979/upstream/dgefa.f"
c = Cut("linpack-netlib-1979", mode="ANCESTRY_AWARE", inspected=["file list (7 files)", "daxpy.f 1-60", "dgefa.f 1-40", "linpackd.f identity check against linpackd-netlib-1979"], evidence=[("SOURCE_READ", D + ":1-60"), ("SOURCE_READ", G + ":1-40")],
        note="the body duplicates the linpackd-netlib-1979 body (same linpackd.f, byte for byte) and adds the six kernels as separate files; it does NOT contain the LINPACK library (dgeco, dpofa, dqrdc, dsvdc, ...) that its record's lineage describes. The one thing this body shows that the benchmark cut rejected as below grain is the kernel INTERFACE as a separately compiled, stride-parameterised unit: that is recorded here as the single organ; everything else is the other cut's")

blas = c.organ("vector_kernels_as_separately_compiled_routines_with_a_count_and_two_strides_so_the_factorisation_never_touches_a_matrix_element_directly", human_name="daxpy(n, da, dx, incx, dy, incy), ddot, dscal(n, da, dx, incx), idamax(n, dx, incx) as their own files; dgefa's inner loop written entirely as calls to them", status="ACCEPTED",
    mechanism="each kernel takes a length, pointers to the first elements and a stride per vector; the unit-stride case is unrolled by four (daxpy) or five (ddot) with a clean-up loop, the general case loops with the strides; the factorisation (dgefa) expresses the pivot search, the scaling of the multipliers and the rank-one update per column as one call each, so a vendor can replace the six files with hand-tuned versions and the factorisation is unchanged",
    input="n, scalars, arrays, strides", output="updated vectors", state="none", update="per call", assumptions=["the performance-critical work is in a handful of vector operations; an interface with explicit strides is enough for column and row access in Fortran storage"],
    fitness_value_in_ancestor="the BLAS-1 idea: a hardware/software contract that let LINPACK run near peak on the vector machines of 1979 without changing the numerical code", failure_landscape="by reading: level-1 kernels are memory-bound on cache machines (the reason LAPACK moved to level-3 BLAS; the record says so)", human_prior="Lawson, Hanson, Kincaid & Krogh 1979 (BLAS); Dongarra et al. 1979", evidence_ref=D + ":1-60; " + G + ":1-40", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the six kernel files and their call sites in dgefa/dgesl",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP", "representation_sensitivity": "SENSITIVE"})

c.reject("linpackd.f (the benchmark driver, dgefa, dgesl, matgen, epslon, dmxpy)", reason="OTHER", evidence="byte-identical to linpackd-netlib-1979's body (md5 e43e84f43cb4997c0c3996c7d673cb3c); cut there (DEEP, two organs)", note="DUPLICATE BODY: record defect for Techne -- two specimens carry the same file; the record's lineage describes the library (dgeco, dpofa, dqrdc, dsvdc) which is absent from the body")
c.reject("'LINPACK the library' as described by the record", reason="OTHER", evidence="not in the body: only dgefa/dgesl of the ~40 LINPACK routines are present", note="the cut records the body, not the record")

c.pressure("dense_linear_algebra_must_run_near_peak_on_machines_whose_fast_paths_differ_while_the_numerical_code_stays_portable_and_verifiable",
    condition="an organism factorises matrices on several machine families with different vector hardware; the numerical algorithm must be identical across them (verifiable by residual); each machine's peak is reachable only through its own idioms", resource_or_constraint="a fixed, small interface between the algorithm and the machine",
    failure_condition="portable code that runs far below peak, or fast code that differs numerically per machine", world_punishes="inlining the loops into the factorisation; interfaces without strides", world_rewards="a small set of stride-parameterised kernels with reference implementations",
    observable_consequence="fraction of peak achieved with reference kernels vs tuned kernels, with the residual identical", vacuity_condition="one machine", trivial_shortcuts="a machine-specific rewrite of the whole factorisation (which the verifiability score punishes)",
    cheat_control="an organism with tuned kernels must show the same residual as the reference within round-off and a higher fraction of peak; the inlined factorisation must be no faster than the reference kernels and unverifiable across machines: the world must show both",
    cost_class="CPU-scale", source_evidence="the six kernel files; dgefa's call structure", purpose="PURPOSE: portable performance for dense linear algebra (Dongarra et al. 1979)")

c.ancestry("historical_version_of", "linpackd-netlib-1979 (in this atlas): the same driver file; the six kernels are the BLAS-1 of Lawson et al. 1979", note="by md5 comparison of linpackd.f and the file headers")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["nothing further to read: the body is the other cut's file plus six kernel files", "record defect: duplicate body and a lineage describing an absent library", "nothing ran"], note="one organ (the interface) that the benchmark cut had folded into its rejects; recorded here so the census counts the specimen without double-counting the factorisation")
c.save(state="COARSE")
