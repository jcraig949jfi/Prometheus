"""Cut: kissfft-131.1.0 (KISS FFT, Borgerding; ancestry-aware, Stage A DEEP; SOURCE_READ on M3; position 47 of the 2026-09-17 NOT_CUT
order). Read: kiss_fft.c kf_bfly2 15-37, kf_work 236-306, kf_factor 307-336, kiss_fft_alloc 337-370. NOT read: kf_bfly3/4/5 and
kf_bfly_generic bodies (86-235), kiss_fftr.c (real input), kiss_fftnd.c, the fixed-point macros, the tools. Nothing ran (C; no
compiler on M3).
"""
from nyx.atlas.author import Cut

F = "vault:kissfft-131.1.0/upstream/tree/kissfft-131.1.0/kiss_fft.c"
c = Cut("kissfft-131.1.0", mode="ANCESTRY_AWARE", inspected=["kiss_fft.c 15-37, 236-370"], evidence=[("SOURCE_READ", F + ":15-37"), ("SOURCE_READ", F + ":236-370")],
        note="a mixed-radix decimation-in-time FFT in three parts: a factorisation of n that prefers 4, then 2, then odd primes; a recursion that computes p sub-transforms of size m on strided input and recombines them with a butterfly for the radix; and a single precomputed twiddle table indexed by stride; the whole transform is 420 lines and its stated purpose is to be readable")

fac = c.organ("length_factorised_greedily_into_radix_4_then_2_then_odd_primes_with_the_remaining_cofactor_used_whole_past_the_square_root", human_name="kf_factor (307-336): p = 4 -> 2 -> 3, 5, 7, ...; if p > floor(sqrt(n)) then p = n; facbuf = p1, m1, p2, m2, ...", status="ACCEPTED",
    mechanism="starting with 4, divide out that radix while it divides n, then fall to 2, then step through odd numbers; whenever the candidate exceeds the square root of the remainder, the remainder itself becomes the last radix (a prime, handled by the generic butterfly); the factor list is stored as (radix, sub-length) pairs consumed by the recursion",
    input="n", output="the factor list", state="none", update="at plan time", assumptions=["radix-4 stages are the cheapest per point among the hard-coded butterflies, so they are taken first; any n is allowed, with primes paying O(p^2) in the generic stage"],
    fitness_value_in_ancestor="arbitrary lengths with the best hard-coded stages used first", failure_landscape="by reading: a large prime length costs O(n^2) (kiss_fft_next_fast_size exists so callers can pad to 2^a 3^b 5^c)", evidence_ref=F + ":307-336", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="kf_factor",
    coverage={"input_topology": "SCALAR", "output_topology": "SEQUENCE", "state_amount": "NONE", "stochasticity": "DETERMINISTIC"})

rec = c.organ("recursive_decimation_in_time_computing_p_strided_sub_transforms_then_recombining_with_a_radix_specific_butterfly", human_name="kf_work (236-306): p, m from the factor list; the m == 1 base case copies strided input; the recursive call with fstride * p; the switch to kf_bfly2/3/4/5/generic", status="ACCEPTED",
    mechanism="for a stage with radix p and sub-length m: if m is 1 copy the p strided input points; else call itself p times on input offset by k * stride to fill p contiguous blocks of m outputs (the sub-transforms), then apply the radix-p butterfly across the blocks; the stride multiplies by p at each level so the decimation is expressed by pointer arithmetic, not by a bit-reversal permutation",
    input="strided input, the factor list, the twiddles", output="the transform in place in Fout", state="the recursion", update="per call", assumptions=["Cooley-Tukey: a length p*m DFT is p DFTs of length m on decimated input followed by m radix-p DFTs with twiddles; recursion on the factor list makes mixed radix natural"],
    fitness_value_in_ancestor="no bit reversal, no scratch beyond the output, one code path for every radix", failure_landscape="by reading: recursion depth equals the number of factors (small); the OpenMP branch parallelises only the top level", human_prior="Cooley & Tukey 1965; the recursive strided form is common in small FFTs (also FFTW's codelets)", evidence_ref=F + ":236-306", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="kf_work",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "LOG", "stochasticity": "DETERMINISTIC", "update_topology": "RECURSIVE", "order_sensitivity": "SENSITIVE"})

bfly = c.organ("radix_specific_butterflies_reading_twiddles_from_one_table_at_the_stage_stride_with_a_generic_o_p_squared_fallback", human_name="kf_bfly2 (15-37): t = Fout2 * tw; Fout2 = Fout - t; Fout += t; tw advances by fstride; kiss_fft_alloc (337-370): twiddles[i] = exp(-2 pi i k / n) for the whole n; kf_bfly_generic (192, not read)", status="ACCEPTED",
    mechanism="one table of n twiddles for the full length is computed at plan time; a stage with stride s reads every s-th entry, which is exactly the twiddle set for that stage's sub-length; the radix-2 butterfly multiplies the second half by the twiddle and forms sum and difference in place; radices 3, 4 and 5 have hand-written equivalents; other primes use a generic loop that multiplies every input by every twiddle power (O(p^2)); the fixed-point build divides by the radix at each stage to prevent overflow (C_FIXDIV)",
    input="p blocks of m points", output="m radix-p transforms in place", state="none", update="per stage", assumptions=["the twiddles of every stage are a stride-subset of the length-n table (true because every sub-length divides n)"],
    fitness_value_in_ancestor="one table, no per-stage tables, and the hot loops are a page of arithmetic", failure_landscape="UNKNOWN by run", evidence_ref=F + ":15-37, 337-370", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the bfly functions and the table setup (3/4/5/generic bodies not read)",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP"})

c.reject("kiss_fftr.c (real-input transform by a half-length complex FFT and a post-twiddle), kiss_fftnd.c (multi-dimensional by row-column), the fixed-point and SIMD macros, the tools (fastfir, psdpng)", reason="OTHER", evidence="NOT READ; residue", note="the real-input trick is a small mechanism of its own")
c.reject("'FFT' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="factorisation, recursion and butterflies are separately replaceable (FFTW replaces all three with generated codelets and a planner)")

c.edge(fac, rec, "feeds"); c.edge(rec, bfly, "feeds"); c.edge(bfly, rec, "feeds", note="in place")

c.pressure("a_discrete_fourier_transform_of_arbitrary_length_must_be_computed_in_near_n_log_n_time_by_code_small_enough_to_be_read_and_verified_by_hand",
    condition="an organism must transform vectors of lengths chosen by the world (including odd and composite ones); the score is time per transform and the size of the organism (lines, tables) it needs; an O(n^2) DFT is the baseline", resource_or_constraint="one twiddle table; no code generation",
    failure_condition="O(n^2) on composite lengths, or a wrong result on a length with an odd factor", world_punishes="power-of-two-only transforms; per-stage tables; bit-reversal bookkeeping", world_rewards="mixed-radix recursion with strided twiddle reuse",
    observable_consequence="time vs n for n in {2^k, 2^a 3^b 5^c, primes} against the direct DFT and against a generated-codelet FFT (FFTW) on the same host; max error vs the direct DFT", vacuity_condition="n a power of two only", trivial_shortcuts="padding to a power of two (which changes the transform)",
    cheat_control="an organism given the direct DFT must match it to round-off; the organism on a prime length must show the O(p^2) fallback; a power-of-two length must show the radix-4 stages dominating: the world must show all three",
    cost_class="CPU-scale", source_evidence="kiss_fft.c kf_factor, kf_work, kf_bfly2, kiss_fft_alloc", purpose="PURPOSE: a readable FFT (Borgerding 2003-)")

c.ancestry("algorithm_from", "Cooley & Tukey 1965 (mixed radix); the strided recursive form", note="from the README and the source")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["the radix 3/4/5/generic butterfly bodies and the real/ND wrappers unread", "nothing ran"], note="the three mechanisms of the complex transform are located")
c.save(state="DEEP")
