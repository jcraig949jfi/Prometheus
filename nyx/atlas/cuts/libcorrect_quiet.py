"""Cut: libcorrect-quiet (Quiet Modem Project's libcorrect; ancestry-aware, Stage A COARSE; SOURCE_READ on M3; position 21 of the
2026-09-17 NOT_CUT order). Read in full: src/convolutional/decode.c (warmup, inner, tail, init), history_buffer.c, metric.c.
Read by structure: reed-solomon/decode.c (function list). NOT read: encode.c, lookup.c, bit.c, error_buffer.c, the SSE variant,
reed-solomon/*.c bodies, the polynomial-search tools. Nothing ran (C; not on M3).
"""
from nyx.atlas.author import Cut

D = "vault:libcorrect-quiet/upstream/tree/src/convolutional/decode.c"; H = "vault:libcorrect-quiet/upstream/tree/src/convolutional/history_buffer.c"
M = "vault:libcorrect-quiet/upstream/tree/src/convolutional/metric.c"; RS = "vault:libcorrect-quiet/upstream/tree/src/reed-solomon/decode.c"
c = Cut("libcorrect-quiet", mode="ANCESTRY_AWARE", inspected=["convolutional/decode.c, history_buffer.c, metric.c (all)", "reed-solomon/decode.c (function list)"],
        evidence=[("SOURCE_READ", D), ("SOURCE_READ", H), ("SOURCE_READ", M), ("SOURCE_READ", RS)],
        note="a production Viterbi decoder: the same add-compare-select as the toy viterbi-hmm-xukmin body, but with soft-decision metrics, a butterfly pairing of states, a bounded traceback window, and periodic renormalisation of the path metrics -- four engineering organs the toy lacks; plus a Reed-Solomon decoder read only by name")

acs = c.organ("butterfly_add_compare_select_over_paired_states_with_precomputed_distance_pairs", human_name="convolutional_decode_inner (decode.c)", status="ACCEPTED",
    mechanism="per symbol the distances from the received symbol to every possible output are tabulated once (2^rate entries), then combined pairwise (pair_lookup) so that two successor states' branch distances come from one lookup; states are processed in butterflies (low, high = low + 2^(order-1)) and the survivor's predecessor is recorded as one bit of history; ties go to the low branch",
    input="received symbols (hard bits or soft bytes); the previous error vector", output="the new error vector and one history column", state="two error buffers (swapped), the history buffer", update="per symbol",
    assumptions=["the trellis has the shift-register structure (each state has exactly two predecessors differing in the high bit)"], fitness_value_in_ancestor="the inner loop touches memory in a pattern the SSE variant can vectorise; the pair lookup halves distance work",
    failure_landscape="UNKNOWN by run", evidence_ref=D + ":convolutional_decode_inner", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the inner function and pair_lookup use",
    coverage={"input_topology": "SEQUENCE", "output_topology": "VECTOR", "state_amount": "LINEAR_IN_INPUT", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP"})

soft = c.organ("soft_decision_metrics_linear_or_quadratic_over_byte_confidences", human_name="metric_soft_distance_linear / _quadratic; soft_measurement (metric.c; decode.c)", status="ACCEPTED",
    mechanism="a received bit is a byte 0..255 (0 = confident 0, 255 = confident 1); the branch metric is the sum over the symbol's bits of |soft - hard*255| (linear) or its square >> 3 (quadratic); hard decoding uses the Hamming distance; the choice is a runtime setting",
    input="soft bytes or hard bits", output="a distance per candidate output", state="none", update="per symbol", assumptions=["byte confidences are monotone in log-likelihood; quadratic is closer to Gaussian-channel ML, linear is cheaper"],
    fitness_value_in_ancestor="~2 dB of coding gain over hard decisions on an AWGN channel (the textbook figure; not measured here)", failure_landscape="UNKNOWN by run", evidence_ref=M + "; " + D + ":soft branches", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="metric.c and the soft_measurement switch",
    coverage={"input_topology": "VECTOR", "output_topology": "SCALAR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "uncertainty": "SAMPLE"})

tb = c.organ("bounded_sliding_traceback_from_the_current_best_state_with_periodic_renormalisation", human_name="history_buffer_process / _traceback / _search / _renormalize (history_buffer.c)", status="ACCEPTED",
    mechanism="history columns live in a ring of cap = min_traceback + group_length entries; when the ring is full, the best current state is found, the path is traced back min_traceback symbols without emitting (the unreliable recent part), and the remaining group is emitted in reverse; every renormalize_interval symbols the minimum path metric is subtracted from all states so the 16-bit metrics never overflow (the interval is computed from the maximum metric per symbol)",
    input="the history ring, the error vector", output="decoded bits in blocks", state="the ring index/len, renormalize counter", update="per symbol; emission per group",
    assumptions=["survivor paths merge within min_traceback symbols (about 5x the constraint length is the rule of thumb), so decoding from the best state is as good as from the true end state"],
    fitness_value_in_ancestor="constant memory for unbounded streams and bounded latency, unlike the toy decoder's full trellis", failure_landscape="by reading: a min_traceback shorter than the merge depth emits wrong bits silently; the renormalisation interval is derived so overflow cannot happen, but it is computed from soft_max, so a wrong soft scale breaks it",
    human_prior="the sliding-window Viterbi of every hardware decoder; the renormalisation-by-minimum trick", evidence_ref=H, confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="history_buffer.c",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "state_persistence": "PER_EPISODE", "memory": "WINDOW", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP", "resource_dependence": "MEMORY"})

tail = c.organ("warmup_and_tail_phases_that_exploit_the_known_zero_start_and_flush", human_name="convolutional_decode_warmup / _tail (decode.c)", status="ACCEPTED",
    mechanism="for the first order-1 symbols only 2^(i+1) states are reachable from state 0, so only those are updated; for the last order-1 symbols the encoder is known to be flushing zeros, so successor states are visited with a stride (skip) that excludes impossible paths and the history is processed with the same stride",
    input="the symbol index relative to the ends", output="restricted state updates", state="none", update="at the two ends", assumptions=["the encoder starts at 0 and flushes to 0 (the same convention the toy body uses)"],
    fitness_value_in_ancestor="fewer operations and no spurious survivors at the ends", failure_landscape="UNKNOWN by run", evidence_ref=D + ":convolutional_decode_warmup, convolutional_decode_tail", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the two end-phase functions",
    coverage={"input_topology": "SEQUENCE", "output_topology": "VECTOR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC"})

rs = c.organ("reed_solomon_decoder_syndromes_error_locator_evaluator_and_erasures", human_name="reed-solomon/decode.c: factorize_error_locator, find_error_evaluator, find_error_values, find_error_locations, decode, decode_with_erasures", status="CANDIDATE",
    mechanism="by function names only: compute syndromes, find the error locator polynomial, factor it (Chien-style root search), compute the error evaluator and error values (Forney), optionally with known erasure positions -- the standard algebraic decoder; the Berlekamp-Massey or Euclid choice is not established by this reading",
    input="a received codeword; optional erasure positions", output="the corrected message or failure", state="none", update="per block", assumptions=["Galois field arithmetic from field.c (not read)"],
    fitness_value_in_ancestor="burst-error correction paired with the convolutional inner code (the classic concatenated scheme)", failure_landscape="UNKNOWN", evidence_ref=RS + ":function list", confidence="LOW", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="reed-solomon/decode.c; CANDIDATE: names only",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC"})

c.reject("encode.c, lookup.c (pair table construction), bit.c (bit reader/writer), error_buffer.c, the SSE decode variant, the polynomial-search tools, the RS encoder and field arithmetic", reason="OTHER", evidence="NOT READ; residue", note="lookup.c builds the pair_lookup the ACS organ depends on")
c.reject("'libcorrect' / 'FEC' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="two codes, two decoders; the convolutional decoder alone is four separable mechanisms")

c.edge(soft, acs, "feeds"); c.edge(acs, tb, "feeds"); c.edge(tail, acs, "gates", note="which states at the ends"); c.edge(tb, acs, "updates", note="renormalised metrics"); c.edge(acs, rs, "feeds", note="concatenation: inner code feeds outer, by design")

c.pressure("a_maximum_likelihood_sequence_decoder_must_run_on_an_unbounded_stream_with_bounded_memory_and_bounded_latency",
    condition="symbols arrive forever; the organism must emit decisions with a fixed delay and fixed memory, though the optimal decision depends on the whole future", resource_or_constraint="a window of W symbols of history; fixed-width metrics",
    failure_condition="wrong bits from deciding too early, or overflow/unbounded memory from deciding too late", world_punishes="both", world_rewards="a window longer than the survivor merge depth and metrics kept bounded",
    observable_consequence="bit error rate vs window length W on a noisy channel: a knee at the merge depth; overflow events vs renormalisation interval", vacuity_condition="finite short messages (full traceback is affordable)", trivial_shortcuts="unbounded memory",
    cheat_control="a decoder with a full-length trellis (the toy body) is the ceiling; a window of 1 symbol must show the error floor of per-symbol decisions: the world must show the knee between them",
    cost_class="CPU-scale", source_evidence="history_buffer.c; the toy viterbi-hmm-xukmin body as the full-traceback reference", purpose="PURPOSE: streaming Viterbi decoding (libcorrect)")

c.ancestry("reimplementation_of", "the Viterbi decoder lineage (Viterbi 1967; Forney 1973 sliding traceback); libfec-karn (in the vault, cut 09-16) is the direct ancestor by API and design (the record's lineage)", note="from the record and the vault; RECURRENCE R1 by reading: libfec-karn's viterbi27 and this decoder share the butterfly ACS + renormalisation shape")
c.residue("PARTIALLY_EXPLAINED", ["the RS decoder is a CANDIDATE by names only", "lookup.c (the pair table) not read", "nothing ran; the vault holds libfec-karn (same lineage) and viterbi-hmm-xukmin (the toy) -- a three-body recurrence test on one code is the natural Stage E item"],
          note="the convolutional decoder's four mechanisms are accounted for")
c.save(state="COARSE")
