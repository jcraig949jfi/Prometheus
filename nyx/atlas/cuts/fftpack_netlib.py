"""Cut: fftpack-netlib (ancestry-aware, Stage A COARSE; SOURCE_READ cffti1.f, cfftf1.f, passf2.f, ezfftf.f, cost.f in full; rfftf1.f call
structure; doc lines 60-363 (grepped); passf.f / radfg.f (general-radix passes, 116 / 166 lines) NOT read; the sine/quarter-wave
files skimmed by name). Swarztrauber's 1985 FFT package, 51 Fortran-77 files."""
from nyx.atlas.author import Cut

T = "vault:fftpack-netlib/upstream/"
c = Cut("fftpack-netlib", mode="ANCESTRY_AWARE", inspected=["cffti1.f", "cfftf1.f", "passf2.f", "rfftf1.f (calls)", "ezfftf.f", "cost.f", "doc (grepped)"],
        evidence=[("SOURCE_READ", T + "cffti1.f"), ("SOURCE_READ", T + "cfftf1.f"), ("SOURCE_READ", T + "passf2.f"), ("SOURCE_READ", T + "cost.f")],
        note="one mechanism family (mixed-radix passes) driven by a factorisation, wrapped by real / cosine / sine / quarter-wave pre- and post-processing; a Fortran-77 body whose control flow is arithmetic IFs and GO TOs")

fac = c.organ("factor_n_into_small_primes_preferring_4_then_2_then_3_then_5_with_2_moved_first", human_name="the IFAC factorisation (cffti1 / rffti1)", status="ACCEPTED",
    mechanism="try divisors from NTRYH = (3, 4, 2, 5) then 7, 9, 11, ... (odd numbers after 5); each hit appends the factor and divides; if a 2 appears after other factors it is moved to the front (lines 105-107); the result IFAC = (N, NF, f1..fNF) drives every pass below; the doc says the transform 'is most efficient when n is a product of small primes'",
    input="N", output="IFAC", state="none", update="once per N", assumptions=["trial division; N with a large prime factor falls through to the general pass"], evidence_ref=T + "cffti1.f:1-27; doc:60,89,363", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the factorisation loop 101-107 in cffti1 / rffti1",
    coverage={"input_topology": "SCALAR", "output_topology": "SEQUENCE", "state_amount": "NONE", "stochasticity": "DETERMINISTIC"})

tw = c.organ("twiddle_table_per_factor_stage_from_cos_sin_of_multiples_of_two_pi_over_n", human_name="WA (the wsave array)", status="ACCEPTED",
    mechanism="for each factor stage with stride L1 and IP-1 sub-blocks, tabulate (cos, sin)(FI * LD * 2pi/N) for the stage's IDO points; stored consecutively so each pass gets a pointer WA(IW) advanced by (IP-1)*IDOT per stage; computed once, reused for every transform of the same N",
    input="N, IFAC", output="WA", state="none (a table)", update="once per N", assumptions=["single precision (TPI = 6.28318530717959 as a REAL)"], evidence_ref=T + "cffti1.f:28-58", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="cffti1 lines 28-58",
    coverage={"input_topology": "SEQUENCE", "output_topology": "VECTOR", "state_amount": "LINEAR_IN_INPUT", "stochasticity": "DETERMINISTIC"})

drv = c.organ("stage_driver_alternating_two_buffers_over_the_factor_list", human_name="cfftf1 / cfftb1 / rfftf1 / rfftb1", status="ACCEPTED",
    mechanism="for each factor IP in IFAC: choose the specialised pass (4, 2, 3, 5) or the general one; call it with (source, destination) = (C, CH) or (CH, C) according to a toggle NA that flips after each pass (the general pass reports via NAC whether it flipped); advance L1 *= IP and the twiddle pointer; copy CH back to C at the end if the toggle ended on CH",
    input="C (data), CH (scratch), WA, IFAC", output="C transformed in place", state="NA toggle, L1, IW", update="one loop per transform", assumptions=["scratch of size 2N is available"],
    fitness_value_in_ancestor="no in-place bit-reversal: the alternating-buffer scheme is how FFTPACK avoids the permutation step", evidence_ref=T + "cfftf1.f:1-60; rfftf1.f (same shape)", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the four *1 drivers",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "LINEAR_IN_INPUT", "update_topology": "SWEEP", "order_sensitivity": "SENSITIVE"})

p2 = c.organ("radix_r_butterfly_pass_with_twiddle_multiply_on_all_but_the_first_output", parent=drv, human_name="PASSF2 / PASSF3 / PASSF4 / PASSF5 / PASSF (general), and RADF*/RADB* for real data", status="ACCEPTED",
    mechanism="radix-2 as read: CH(i,k,1) = CC(i,1,k) + CC(i,2,k); the difference is multiplied by the twiddle (wa1) into CH(i,k,2); the array is reshaped between (IDO, IP, L1) and (IDO, L1, IP) by the argument declarations alone (the same memory, two DIMENSION statements); for IDO = 2 no twiddle multiply is needed (lines 4-10); radices 3, 4, 5 are the same shape with fixed rotation constants; the general PASSF handles any prime with an inner loop (NOT read)",
    input="CC as (IDO, IP, L1)", output="CH as (IDO, L1, IP)", state="none", update="none", assumptions=["Fortran column-major aliasing of one array under two shapes"],
    fitness_value_in_ancestor="the butterfly is the whole arithmetic; the reshaping-by-declaration is the transposition step other FFTs do explicitly", evidence_ref=T + "passf2.f:1-24; passf3/4/5.f by name; radf2.f by name", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="each pass* / rad* file",
    coverage={"input_topology": "MATRIX", "output_topology": "MATRIX", "state_amount": "NONE", "update_topology": "PARALLEL_ROUNDS", "representation_sensitivity": "SENSITIVE"})

rw = c.organ("real_sequence_transforms_by_pre_and_post_processing_around_a_half_length_or_real_fft", human_name="EZFFTF/B, COST, SINT, COSQF/B, SINQF/B", status="ACCEPTED",
    mechanism="ezfftf: copy R to scratch, RFFTF, then scale and split the packed result into azero, a[], b[] (2/N, sign flip on b); cost: fold the sequence with its reverse using the cos table (K, N+1-K pairs), RFFTF of length N-1, then an unfolding recurrence (X(I) = X(I-2) - X(I-1), lines 33-40); sint / cosq / sinq are analogous folds (skimmed by name only)",
    input="a real sequence", output="Fourier / cosine / sine coefficients", state="none beyond wsave", update="none", assumptions=["the symmetry of the wanted transform lets a shorter real FFT do the work"],
    evidence_ref=T + "ezfftf.f:1-27; cost.f:1-42", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the wrapper files ezfft*, cost*, sint*, cosq*, sinq*",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "NONE", "update_topology": "SWEEP"})

c.reject("'FFT' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="factorisation, twiddle table, driver and passes have separate files and separate lifetimes (init once, transform many)")
c.reject("forward vs backward (cfftf vs cfftb, passf vs passb) as separate anatomy", reason="OTHER", evidence="passb2.f differs from passf2.f in the sign of the twiddle products only (by name and shape; passb2 not diffed line by line)", note="a sign parameter, recorded as one organ")
c.reject("test.f", reason="EFFECT_FROM_ENVIRONMENT", evidence=T + "test.f -- the shipped driver Techne ran (UPSTREAM_DRIVERS_RUN_NO_ORACLE per the record family)")
c.reject("arithmetic IF / GO TO control flow", reason="GENERIC_LANGUAGE_MECHANICS", evidence="every file; Fortran 66/77 idiom, not machinery")

c.edge(fac, tw, "feeds"); c.edge(fac, drv, "feeds"); c.edge(tw, p2, "feeds"); c.edge(drv, p2, "schedules"); c.edge(rw, drv, "feeds", note="wrappers call RFFTF/RFFTB"); c.edge(drv, rw, "feeds")

c.pressure("a_dense_n_squared_transform_must_be_computed_in_near_n_log_n_on_1980s_memory",
    condition="the discrete Fourier transform is an N x N matrix product; N in the thousands must run on machines where N^2 flops and an N x N table are unaffordable", resource_or_constraint="flops and memory of the era; single precision",
    failure_condition="N^2 cost; or an N restricted to powers of two", world_punishes="direct evaluation; a transform that only accepts 2^k", world_rewards="factoring the index set and reusing sub-transforms (the same structure whatever the factors)",
    observable_consequence="runtime vs N and vs the factorisation of N (the doc's 'most efficient when n is a product of small primes')", vacuity_condition="small N", trivial_shortcuts="restrict N to 2^k (the world must include awkward N)",
    cheat_control="a transform given a precomputed N x N matrix must match to single precision and cost N^2; if the world scores it equal, cost is not being charged", cost_class="CPU-scale", source_evidence="doc; cffti1 factorisation", purpose="PURPOSE: spectral analysis / PDE solvers (Swarztrauber's use)")
c.pressure("the_same_arithmetic_must_serve_real_cosine_and_sine_transforms_without_new_kernels",
    condition="applications need several related transforms; each written from scratch multiplies the code and the error surface", resource_or_constraint="code size; verification effort",
    failure_condition="divergent implementations of the same butterflies", world_punishes="duplication", world_rewards="symmetry-exploiting pre/post processing around one kernel",
    observable_consequence="the wrapper files call RFFTF/RFFTB and never a pass directly", vacuity_condition="one transform needed", trivial_shortcuts="none",
    cheat_control="N/A", cost_class="CPU-scale", source_evidence="cost.f, ezfftf.f", purpose="PURPOSE: same")

c.residue("PARTIALLY_EXPLAINED", ["the general-radix passes passf.f / radfg.f (any prime) are unread; their inner structure may be a distinct mechanism (a DFT of prime length by direct sums)", "sint / cosq / sinq folds are assumed analogous to cost from names and sizes only", "single-precision accuracy vs N is not measured (Techne's run had no oracle)"],
          note="the small-radix path (factor, twiddle, driver, butterfly, real wrapper) is fully read")
c.save(state="COARSE")
