"""Cut: libfec-karn (ancestry-aware, Stage A COARSE; SOURCE_READ viterbi27_port.c in full, decode_rs.h in full, encode_rs.h, init_rs.h 1-106,
fano.c 21-140, metrics.c 24-80, dotprod_port.c; the mmx/sse/sse2/altivec variants, viterbi29/615/224 (same shape, longer
constraint), rstest/vtest harnesses and sim.c skimmed). Phil Karn's forward-error-correction library, 2004-2006."""
from nyx.atlas.author import Cut

T = "vault:libfec-karn/upstream/tree/"
c = Cut("libfec-karn", mode="ANCESTRY_AWARE",
        inspected=["viterbi27_port.c", "decode_rs.h", "encode_rs.h", "init_rs.h", "fano.c 21-140", "metrics.c 24-80", "dotprod_port.c", "file list (74 .c, 17 .s)"],
        evidence=[("SOURCE_READ", T + "viterbi27_port.c"), ("SOURCE_READ", T + "decode_rs.h"), ("SOURCE_READ", T + "fano.c"), ("SOURCE_READ", T + "init_rs.h"), ("SOURCE_READ", T + "encode_rs.h")],
        note="three decoders for two code families plus DSP helpers; the SIMD files are the same machinery re-expressed for four instruction sets (a preservation of the 2004 hardware pressure, not new anatomy)")

# ------------------------------------------------------------------------------------------ convolutional / Viterbi
vit = c.organ("viterbi", human_name="K=7 rate-1/2 Viterbi decoder (viterbi27)", status="CANDIDATE",
    human_interpretation="maximum-likelihood decoding of a convolutional code by dynamic programming over the encoder's 64 states",
    mechanism="create (branch tables) -> init (metrics = 63, start state 0) -> update_blk (one butterfly sweep per data bit, decisions stored) -> chainback (walk the decisions from the end state) ; the same four calls exist for K=9 (viterbi29), K=15 (viterbi615) and K=24 (viterbi224)",
    input="soft symbols 0..255, two per bit", output="decoded bits", state="two 64-entry metric buffers + one decision word per bit", update="per bit", interface="create/init/update_blk/chainback/delete (fec.h)",
    evidence_ref=T + "viterbi27_port.c:1-174", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="viterbi27_port.c",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "update_topology": "SWEEP", "stochasticity": "DETERMINISTIC"})

bt = c.organ("viterbi.expected_symbol_table_per_state_from_the_generator_polynomials", parent=vit, human_name="branch table", status="ACCEPTED",
    mechanism="for each of 32 butterfly indices, Branchtab[k][state] = 255 if parity(2*state & POLY_k) else 0: the symbol the encoder WOULD emit leaving that state; at decode time (table XOR received soft symbol) is the branch distance, so the two branches of a butterfly have complementary costs metric and 510-metric",
    input="V27POLYA, V27POLYB (constants)", output="two 32-byte tables", state="computed once (static Init)", update="none", assumptions=["both polynomials odd (fano.c 88-90 states the same assumption) so the pair of branches is complementary"],
    evidence_ref=T + "viterbi27_port.c:12,42-51,92-94", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="create_viterbi27_port's init block",
    coverage={"input_topology": "SCALAR", "output_topology": "VECTOR", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC"})

acs = c.organ("viterbi.add_compare_select_butterfly_over_ping_pong_metric_buffers", parent=vit, human_name="ACS butterfly", status="ACCEPTED",
    mechanism="for butterfly i (states i and i+32 -> states 2i and 2i+1): m0 = old[i] + metric, m1 = old[i+32] + (510 - metric); keep the smaller into new[2i] and record the choice as one decision bit; repeat with the metrics swapped for new[2i+1]; after 32 butterflies swap the old/new buffer pointers; metrics are never renormalised (unsigned wrap is tolerated by the signed comparison)",
    input="old metrics[64], sym0, sym1", output="new metrics[64], 64 decision bits", state="metrics1, metrics2, old/new pointers, dp", update="per bit", assumptions=["64 states fit; the best path's metric difference stays below 2^31"],
    fitness_value_in_ancestor="the whole decoding cost is here; every SIMD file re-expresses this macro", evidence_ref=T + "viterbi27_port.c:91-106,112-165", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="BFLY + update_viterbi27_blk_port",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "CONSTANT", "update_topology": "PARALLEL_ROUNDS", "order_sensitivity": "INVARIANT", "memory": "LAST_VALUE"})

cb = c.organ("viterbi.traceback_by_stored_decision_bits_from_a_known_end_state", parent=vit, human_name="chainback", status="ACCEPTED",
    mechanism="starting from endstate (<<2 to align with the decision bit layout) and past the 6 tail bits, for each bit from the last: read the decision bit of the current state, shift it in as the new high bit of the state and of the output byte; the register value IS the decoded byte every 8 steps",
    input="decision words, nbits, endstate", output="data bytes", state="none beyond the register", update="per bit backwards", assumptions=["the encoder was flushed to a known end state (tail)"],
    evidence_ref=T + "viterbi27_port.c:57-82", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="chainback_viterbi27_port",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "memory": "FULL_HISTORY", "update_topology": "SWEEP"})

# ------------------------------------------------------------------------------------------------ Reed-Solomon
rs = c.organ("rs", human_name="Reed-Solomon codec (parametrised: symsize, gfpoly, fcr, prim, nroots, pad)", status="CANDIDATE",
    mechanism="init builds the field and generator; encode divides by the generator; decode = syndromes -> (erasure seed) -> Berlekamp-Massey -> Chien -> Forney; the same header is #included three times for char / int / CCSDS symbol types",
    input="symbol blocks", output="parity symbols (encode) / corrected block + count (decode)", state="the field tables and generator (per code)", update="per block",
    evidence_ref=T + "init_rs.h, encode_rs.h, decode_rs.h", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the three *_rs.h templates and their instantiations",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC"})

gf = c.organ("rs.galois_field_log_antilog_tables_from_a_primitive_polynomial", parent=rs, human_name="GF(2^m) tables", status="ACCEPTED",
    mechanism="run a shift register from 1: alpha_to[i] = sr, index_of[sr] = i, sr <<= 1, reduce by gfpoly on overflow; after nn steps sr must return to 1 or the polynomial is not primitive (refused); then build genpoly = prod (x - alpha^(fcr + i*prim)) by repeated multiplication in index form",
    input="symsize, gfpoly, fcr, prim, nroots", output="alpha_to[], index_of[], genpoly[]", state="none after construction", update="once", assumptions=["gfpoly primitive"],
    fitness_value_in_ancestor="all field multiplication in the codec is a table add mod nn", evidence_ref=T + "init_rs.h:1-106", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="init_rs.h",
    coverage={"input_topology": "SCALAR", "output_topology": "VECTOR", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC"})

enc = c.organ("rs.systematic_encoding_by_lfsr_division_by_the_generator", parent=rs, human_name="RS encoder", status="ACCEPTED",
    mechanism="for each data symbol: feedback = log(data ^ parity[0]); shift the parity register by one; parity[j] ^= alpha^(feedback + genpoly[nroots-j]); the remainder after all data symbols is the parity",
    input="nn - nroots - pad data symbols", output="nroots parity symbols", state="the parity register", update="per symbol", assumptions=["genpoly monic (comment 35-37)"],
    evidence_ref=T + "encode_rs.h:28-58", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="encode_rs.h",
    coverage={"input_topology": "SEQUENCE", "output_topology": "VECTOR", "state_amount": "CONSTANT", "update_topology": "SWEEP"})

syn = c.organ("rs.syndrome_evaluation_by_horner_at_consecutive_roots", parent=rs, human_name="syndromes", status="ACCEPTED",
    mechanism="s[i] = received(alpha^(fcr+i)) for i < nroots by Horner's rule over the block; if all zero the block is a codeword and decoding stops (count 0)",
    input="the received block", output="nroots syndromes (index form) + syn_error flag", state="none", update="none",
    evidence_ref=T + "decode_rs.h:67-91", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="decode_rs.h syndrome loop",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "NONE", "output_topology": "DECISION"})

bm = c.organ("rs.iterative_locator_polynomial_from_syndromes_with_erasure_seed", parent=rs, human_name="Berlekamp-Massey (errors + erasures)", status="ACCEPTED",
    mechanism="lambda starts as the erasure locator (product over known erasure positions, 92-100); then for r from no_eras+1 to nroots: discrepancy = sum lambda[i] * s[r-i-1]; if zero shift b; else lambda = lambda - discr*x*b with b updated from the old lambda when 2*el <= r+no_eras-1 (the length test); deg(lambda) is the number of errors+erasures found",
    input="syndromes, erasure positions", output="lambda (locator polynomial), deg_lambda", state="lambda, b, el", update="nroots - no_eras iterations", assumptions=["errors + 2*erasures <= nroots"],
    failure_landscape="UNKNOWN by run; by reading: a locator of degree != number of roots later found is reported as uncorrectable (count = -1, line 239-244)", evidence_ref=T + "decode_rs.h:92-100,164-214", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="decode_rs.h 164-214",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "CONSTANT", "update_topology": "SWEEP", "memory": "LAST_VALUE"})

ch = c.organ("rs.exhaustive_root_search_over_the_field", parent=rs, human_name="Chien search", status="ACCEPTED",
    mechanism="evaluate lambda at every field element by keeping one running register per coefficient (reg[j] += j each step) and XORing; each zero gives a root and its location number; refuse if the root count != deg_lambda",
    input="lambda", output="roots[], loc[], count", state="reg[]", update="nn steps", evidence_ref=T + "decode_rs.h:215-247", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="decode_rs.h 215-247",
    coverage={"input_topology": "VECTOR", "output_topology": "SET", "state_amount": "CONSTANT", "update_topology": "SWEEP"})

fo = c.organ("rs.error_magnitudes_from_evaluator_over_locator_derivative", parent=rs, human_name="Forney algorithm", status="ACCEPTED",
    mechanism="omega = s * lambda mod x^nroots; for each root X: num1 = omega(1/X), num2 = X^(fcr-1) factor, den = lambda'(1/X) (the odd-power terms); error = num1*num2/den XORed into data at loc",
    input="syndromes, lambda, roots", output="corrected data, count, eras_pos", state="omega", update="per root", evidence_ref=T + "decode_rs.h:249-298", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="decode_rs.h 249-298",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "CONSTANT"})

# --------------------------------------------------------------------------------------------------- Fano / metrics
fa = c.organ("fano.depth_first_tree_search_with_a_running_threshold_and_backtracking", human_name="Fano sequential decoder", status="ACCEPTED",
    human_interpretation="decode the same convolutional code as Viterbi but by exploring one path at a time, going deeper while the accumulated metric stays above a threshold and backing up when it drops",
    mechanism="precompute per-node branch metrics from a metric table; at each node try the better branch first (sorted tm[0], tm[1]); move forward if gamma + branch >= t, tightening t by multiples of delta on first visits; otherwise back up and try the other branch, loosening t by delta when both are exhausted; stop at the last node or after maxcycles*nbits cycles (a decoding FAILURE with the cycle count returned)",
    input="soft symbols, mettab[2][256], delta, maxcycles", output="decoded bits, final metric, cycles used", state="an array of nodes (metrics[4], tm[2], gamma, encstate, i), threshold t", update="one node per cycle",
    assumptions=["a good frame needs few cycles; effort grows with noise (the sequential-decoding computation distribution)", "tail is zero so the last K-1 nodes have one branch"],
    fitness_value_in_ancestor="long constraint lengths (K=32 here) where Viterbi's 2^(K-1) states are impossible; pays with variable and unbounded effort", failure_landscape="UNKNOWN by run; by reading: timeout (returns 0 with cycles = maxcycles) is the designed failure",
    evidence_ref=T + "fano.c:38-200", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="fano()",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "update_topology": "RECURSIVE", "resource_dependence": "COMPUTE", "failure_mode": "STALLS", "recovery": "NONE", "memory": "FULL_HISTORY"})

me = c.organ("metrics.log_likelihood_ratio_table_from_a_gaussian_channel_model", human_name="gen_met", status="ACCEPTED",
    mechanism="for each of 256 received bins compute P(bin | 0 sent) and P(bin | 1 sent) as differences of the normal CDF at bin edges shifted by +/- signal and scaled by 1/noise; metric = log2(p/(p0+p1)/2) - bias, scaled and rounded; bias = 0 for Viterbi, the code rate for sequential decoding (the Fano metric)",
    input="signal, noise, bias, scale", output="mettab[2][256]", state="none", update="once per channel estimate", assumptions=["AWGN; 8-bit quantised soft decisions with bins centred on integers"],
    fitness_value_in_ancestor="makes the decoders soft-decision; the bias term is what makes Fano's threshold test meaningful", evidence_ref=T + "metrics.c:19-80", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="gen_met + normal()",
    coverage={"input_topology": "SCALAR", "output_topology": "MATRIX", "state_amount": "NONE", "uncertainty": "DISTRIBUTION", "hidden_state": "ASSUMES"})

dp = c.organ("dsp.fixed_point_dot_product_against_stored_coefficients", human_name="dotprod (FIR core)", status="CANDIDATE",
    mechanism="sum a[i] * coeffs[i] over len in 16-bit fixed point; the SIMD variants keep several shifted copies of the coefficients to align loads (the portable one keeps one)",
    input="a[len]", output="a long", state="coeffs", update="none", evidence_ref=T + "dotprod_port.c:1-58", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="dotprod_port.c",
    coverage={"input_topology": "VECTOR", "output_topology": "SCALAR", "state_amount": "CONSTANT"})

c.reject("MMX / SSE / SSE2 / AltiVec variants of every organ (viterbi*_mmx/sse/sse2/av, *bfly*.s, dotprod_*, peakval_*, sumsq_*)", reason="OTHER",
         evidence="file list: 4 instruction-set variants per mechanism plus cpu_mode_x86.c / cpu_mode_ppc.c dispatch; the portable file is the reference (comment in viterbi27_port.c header)", note="the same anatomy under a 2004 hardware pressure (SIMD width); a Stage D fingerprint could test behavioural identity across variants -- it is claimed by intent, not verified")
c.reject("sim.c addnoise / normal_rand and the *test.c drivers", reason="EFFECT_FROM_ENVIRONMENT", evidence=T + "sim.c:8-60; vtest27.c, rstest.c -- the simulated channel and the harnesses; Techne's receipt runs vtest27")
c.reject("peakval / sumsq", reason="BELOW_MEANINGFUL_GRAIN", evidence=T + "peakval_port.c, sumsq_port.c: 16 lines each; max-abs and sum-of-squares over an array")
c.reject("viterbi29 / viterbi615 / viterbi224 as separate organs", reason="OTHER", evidence="same create/init/update/chainback shape with 256 / 16384 / 2^23 states and 2 / 4 / 3 polynomials; viterbi224 reads its decisions differently (viterbi224.h) -- NOT read in full", note="recorded as instances of viterbi.*; the K=24 one is not confirmed to be the same shape")
c.reject("'FEC library' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="three decoders share no state; fec.h only declares them side by side")
c.reject("CCSDS concatenation (gen_ccsds.c, decode_rs_ccsds.c)", reason="OTHER", evidence="instantiations of rs.* with fixed parameters (255,223, dual-basis conversion tables) -- skimmed, not read", note="the interleaver/concatenation that CCSDS specifies is NOT in the body: only the RS half")

c.edge(bt, acs, "feeds"); c.edge(acs, cb, "stores", note="decision bits"); c.edge(me, fa, "feeds", note="mettab"); c.edge("ENVIRONMENT", acs, "feeds", note="soft symbols"); c.edge("ENVIRONMENT", fa, "feeds")
c.edge(gf, enc, "feeds"); c.edge(gf, syn, "feeds"); c.edge(syn, bm, "feeds"); c.edge(syn, bm, "gates", note="zero syndromes skip everything"); c.edge(bm, ch, "feeds"); c.edge(ch, fo, "feeds"); c.edge(ch, fo, "gates", note="root count mismatch aborts")
c.edge(fa, vit, "competes", note="two decoders for the same code family; the hybrid test (hybridtest.c) runs Fano first and falls back to Viterbi -- read from the file name and header only")

c.pressure("independent_symbol_corruption_with_a_fixed_redundancy_budget",
    condition="a channel flips or perturbs each transmitted symbol independently with some probability; the receiver sees only the corrupted sequence and knows the code; redundancy costs bandwidth so it is fixed in advance", resource_or_constraint="parity fraction (rate); decoder compute",
    failure_condition="bit/frame error rate above what the application tolerates at the operating SNR", world_punishes="decoding that ignores soft information or the code's structure", world_rewards="exploiting structure (trellis or algebra) to reach the code's correction capacity",
    observable_consequence="BER vs Eb/No curves (vtest27's output)", vacuity_condition="a noiseless channel", trivial_shortcuts="majority vote on repetition (works, far from capacity); a world must charge for redundancy",
    cheat_control="a decoder given the transmitted bits must show BER 0; a world that scores it equal to a real decoder at high noise is not measuring correction", cost_class="CPU-scale", source_evidence="the whole library; metrics.c models the channel", purpose="PURPOSE: deliver bits over a noisy link (satellite, amateur radio)")
c.pressure("decoding_effort_must_scale_with_noise_under_a_compute_ceiling",
    condition="frames are usually clean and occasionally very noisy; a decoder with fixed cost pays the worst case always, one with variable cost pays for the noise it meets but may not finish", resource_or_constraint="cycles per bit (maxcycles)",
    failure_condition="timeout on a noisy frame (Fano) versus a state count that cannot be afforded at all (Viterbi at K=32)", world_punishes="fixed cost when noise is rare; unbounded cost when noise is common", world_rewards="an early-exit search whose failure is detectable and cheap to fall back from",
    observable_consequence="the distribution of cycles per frame; timeout rate vs SNR", vacuity_condition="unlimited compute", trivial_shortcuts="always run the exhaustive decoder (only possible for short constraint lengths)",
    cheat_control="a search told the true path must use ~1 cycle per bit; if the world does not reward that, effort is not being measured", cost_class="CPU-scale", source_evidence="fano.c maxcycles; hybridtest.c by name", purpose="PURPOSE: same, at long constraint length")
c.pressure("errors_arrive_in_bursts_of_adjacent_symbols",
    condition="corruption hits runs of bits (fading, a scratched medium), so a bit-level code sees many errors in one place while a symbol-level code sees few corrupted symbols", resource_or_constraint="symbol size vs burst length",
    failure_condition="bit-level decoders fail on bursts they could survive if spread", world_punishes="treating burst errors as independent bit errors", world_rewards="grouping bits into symbols (RS) or spreading errors (an interleaver -- NOT in this body)",
    observable_consequence="frame error rate under burst vs random noise at equal bit-error rate", vacuity_condition="memoryless channel", trivial_shortcuts="none obvious",
    cheat_control="a decoder told the burst boundaries must correct up to nroots/2 symbol errors regardless of bit count", cost_class="CPU-scale", source_evidence="record: RS decoder present beside Viterbi; CCSDS concatenation files", purpose="PURPOSE: same")

c.ancestry("algorithm_from", "Viterbi 1967; Fano 1963; Berlekamp 1968 / Massey 1969; Reed-Solomon 1960", note="named by the functions themselves; not re-checked against the record")
c.residue("PARTIALLY_EXPLAINED", ["viterbi224 (K=24) and the CCSDS dual-basis conversion were not read; their shapes are assumed from names", "the SIMD variants are claimed equivalent to the portable ones by the author, not measured", "nothing ran here; Techne's receipt (vtest27) is the executed evidence, on M1", "the interleaver the CCSDS standard needs is absent: the body is half of a concatenated system"],
          note="the portable decoders are fully accounted for")
c.save(state="COARSE")
