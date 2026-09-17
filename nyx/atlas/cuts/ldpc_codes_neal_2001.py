"""Cut: ldpc-codes-neal-2001 (Radford Neal's LDPC software; ancestry-aware, Stage A COARSE; SOURCE_READ on M3; twentieth of the
2026-09-17 NOT_CUT order). Read in full: dec.c (385 lines: enum_decode, prprp_decode, initprp, iterprp). NOT read: make-ldpc.c
(parity-check construction), the encoders, mod2sparse/mod2dense (the matrix library), rand.c, the channel and transmit programs.
Nothing ran (C; not on M3).
"""
from nyx.atlas.author import Cut

D = "vault:ldpc-codes-neal-2001/upstream/tree/dec.c"
c = Cut("ldpc-codes-neal-2001", mode="ANCESTRY_AWARE", inspected=["dec.c (all)"], evidence=[("SOURCE_READ", D)],
        note="two decoders for the same code: exhaustive enumeration (the oracle, feasible to 31 message bits) and probability propagation over the sparse parity-check graph; the propagation is written as two sweeps per iteration with a product-of-likelihood-ratios trick that avoids a division")

enum = c.organ("exhaustive_maximum_likelihood_decoding_as_the_oracle_for_small_codes", human_name="enum_decode (dec.c)", status="ACCEPTED",
    mechanism="for every one of 2^(N-M) messages, encode it, multiply the per-bit likelihoods of the resulting codeword, keep the best (block MAP) and accumulate per-bit marginals (bit MAP); refuses more than 31 message bits ('absurd')",
    input="likelihood ratios per received bit", output="the most likely codeword, or per-bit most likely values, and marginals", state="none", update="per block", assumptions=["exact but exponential; exists to calibrate the iterative decoder"],
    fitness_value_in_ancestor="a ground truth inside the body: the instrument ships its own oracle", failure_landscape="none (exact)", evidence_ref=D + ":enum_decode_setup, enum_decode", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the two enum_ functions",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP", "uncertainty": "DISTRIBUTION"})

bp = c.organ("probability_propagation_as_check_node_and_bit_node_sweeps_over_a_sparse_graph_with_early_stop_on_a_valid_codeword", human_name="prprp_decode / initprp / iterprp", status="ACCEPTED",
    mechanism="each nonzero of the parity-check matrix H carries two messages (pr: bit-to-check probability ratio; lr: check-to-bit likelihood ratio); initprp sets pr from the channel; each iteration: for every check row, a forward pass accumulates the product of (2/(1+pr) - 1) = (1-p)/(1+p) terms and a backward pass forms each edge's outgoing lr = (1-t)/(1+t) from the product of all OTHER edges (forward x backward partial products, no division); "
              "for every bit column the same forward/backward trick multiplies the incoming lr into the channel ratio to produce each edge's outgoing pr and the posterior; the tentative decoding is the sign of the posterior; the loop stops when the tentative word satisfies all checks (or after max_iter; a negative max_iter forces the count)",
    input="H (sparse), channel likelihood ratios", output="a decoded word, its parity checks, bit posteriors, the iteration count", state="two doubles per nonzero of H", update="per iteration (two sweeps)",
    assumptions=["the graph is sparse and nearly cycle-free so the product rule is nearly exact (the whole point of LOW density)", "a NaN posterior is treated as 1 (a numerical guard, not a theorem)"],
    fitness_value_in_ancestor="near-Shannon-limit decoding in linear time per iteration; the forward/backward partial products make each sweep linear in the nonzeros", failure_landscape="by reading: short cycles in H make the messages overconfident; the decoder can converge to a wrong codeword (early stop accepts any valid codeword) or oscillate",
    human_prior="Gallager 1962 rediscovered by MacKay & Neal 1996; the ratio parametrisation and the two-sweep product trick are Neal's implementation choices", evidence_ref=D + ":prprp_decode, initprp, iterprp", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the three prprp functions",
    coverage={"input_topology": "GRAPH", "output_topology": "VECTOR", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_CALL", "feedback": "CLOSED_LOOP", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP", "failure_mode": "OSCILLATES", "uncertainty": "DISTRIBUTION", "hidden_state": "ESTIMATES"})

trace = c.organ("per_iteration_diagnostics_changed_bits_parity_errors_loglikelihood_expected_errors_entropy", human_name="the table==2 printout in prprp_decode", status="ACCEPTED",
    mechanism="at every iteration the decoder can print: bits changed from the channel decision, current parity errors, log-likelihood of the tentative word, expected parity errors and expected log-likelihood under the posteriors, and the posterior entropy -- i.e. it exposes its own convergence as measurables",
    input="the decoder's state", output="one row per iteration", state="none", update="per iteration", assumptions=["convergence is a trajectory, not a bit"], fitness_value_in_ancestor="the body's own instrument; the natural Stage C observable",
    failure_landscape="none", evidence_ref=D + ":prprp_decode table==2", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the printf under table==2",
    coverage={"input_topology": "VECTOR", "output_topology": "SEQUENCE", "state_amount": "NONE", "stochasticity": "DETERMINISTIC"})

c.reject("make-ldpc.c (parity-check matrix construction: the code design), the encoders (sparse/dense/mixed), mod2sparse/mod2dense, rand.c, channel/transmit", reason="OTHER", evidence="NOT READ; residue", note="the matrix constructor is where the 'low density' and cycle avoidance are decided -- the second most important mechanism in the body, unread")
c.reject("'LDPC' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the code (H) and the decoder are separate; the decoder is the sum-product algorithm the vault's libdai-mooij (NOT_CUT) holds for general factor graphs", note="recurrence candidate: libdai's belief propagation")

c.edge(bp, trace, "feeds"); c.edge(enum, bp, "verifies", note="the oracle for small codes")

c.pressure("beliefs_about_many_coupled_binary_unknowns_must_be_refined_by_passing_only_local_messages_on_a_sparse_constraint_graph",
    condition="N bits, M sparse parity constraints, a noisy observation per bit; the organism may only pass messages along the constraint graph's edges, linearly many per round; it must output a word satisfying every constraint",
    resource_or_constraint="two numbers per edge; rounds", failure_condition="no valid word found within the round budget, or a valid but wrong word", world_punishes="dense constraints (cycles) and decisions made per bit from the channel alone", world_rewards="extrinsic messages (exclude the receiving edge's own contribution)",
    observable_consequence="block error rate vs noise against the exhaustive oracle on codes with <= 31 message bits; iterations to convergence", vacuity_condition="no noise, or constraints so few that per-bit decisions suffice", trivial_shortcuts="the oracle (exponential); a world that reveals the word",
    cheat_control="the enumerative decoder in the body is the ceiling; a decoder that uses each edge's own message back (no extrinsic exclusion) must be visibly worse: the world must show both",
    cost_class="CPU-scale", source_evidence="dec.c iterprp; the enum_decode oracle", purpose="PURPOSE: iterative decoding of low-density parity-check codes (Gallager 1962; MacKay & Neal 1996)")

c.ancestry("algorithm_from", "Gallager 1962 (LDPC codes and probabilistic decoding); MacKay & Neal 1996-97 (rediscovery, near-Shannon performance)", note="from the record and the code's author; not verified against the papers this pass")
c.residue("PARTIALLY_EXPLAINED", ["the code construction (make-ldpc.c) and the matrix library not read", "the tail of iterprp (the backward column pass) read to its first lines only", "nothing ran; the body ships an exact oracle for a Stage C world on any host with a C compiler"], note="the decoder is accounted for; the code design is the residue")
c.save(state="COARSE")
