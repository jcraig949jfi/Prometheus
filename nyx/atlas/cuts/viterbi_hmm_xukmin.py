"""Cut: viterbi-hmm-xukmin (a small C++ convolutional encoder + Viterbi decoder; ancestry-aware, Stage A DEEP-by-size: 192 + 95 lines;
SOURCE_READ on M3; eleventh of the 2026-09-17 NOT_CUT order). Read in full: viterbi.h, viterbi.cpp. Skimmed: viterbi_main.cpp,
viterbi_test.cpp (drivers). Nothing ran. NOTE on the record: the record's domain tags say 'hidden-markov-model / viterbi / dynamic
programming'; the body is a CONVOLUTIONAL CODE decoder (shift-register encoder, Hamming branch metric), i.e. Viterbi's algorithm
in its coding-theory form, not an HMM library. Recorded as a census defect for Techne (9-class), not repaired by Nyx.
"""
from nyx.atlas.author import Cut

V = "vault:viterbi-hmm-xukmin/upstream/tree/viterbi.cpp"
c = Cut("viterbi-hmm-xukmin", mode="ANCESTRY_AWARE", inspected=["viterbi.h, viterbi.cpp (all)", "viterbi_main.cpp, viterbi_test.cpp (skimmed)"],
        evidence=[("SOURCE_READ", V), ("SOURCE_READ", "vault:viterbi-hmm-xukmin/upstream/tree/viterbi.h")],
        note="two organs and a table: a shift-register encoder whose outputs are precomputed per (state, input), and a decoder that keeps one survivor per state by add-compare-select and walks back the survivor pointers")

enc = c.organ("shift_register_encoder_with_outputs_precomputed_per_state_and_input", human_name="NextState / Output / InitializeOutputs / Encode (viterbi.cpp)", status="ACCEPTED",
    mechanism="state = the last constraint-1 input bits; NextState shifts the new bit in; each parity bit is the XOR of the state-plus-input bits selected by a generator polynomial (ReverseBits handles the bit order); the 2^constraint outputs are tabulated once; Encode walks the bits and appends constraint-1 zero bits to flush the register to state 0",
    input="a bit string; constraint length; polynomials", output="a parity bit string (rate 1/k)", state="the register (an int)", update="per input bit",
    assumptions=["the decoder knows the same polynomials; the tail flush returns to state 0 so the decoder can end anywhere but the encoder ends known"], fitness_value_in_ancestor="the table makes both encoding and branch metrics a lookup", failure_landscape="UNKNOWN by run",
    evidence_ref=V + ":NextState, Output, InitializeOutputs, Encode", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the four functions",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC", "update_topology": "SINGLE_STEP"})

acs = c.organ("survivor_per_state_by_add_compare_select_with_hamming_branch_metric_and_traceback", human_name="BranchMetric / PathMetric / UpdatePathMetrics / Decode", status="ACCEPTED",
    mechanism="per received symbol, for each of 2^(constraint-1) states take the two predecessor states, add the Hamming distance between the received bits and the tabulated output of that transition to each predecessor's path metric, keep the smaller (ties to the 0-branch) and record the chosen predecessor in a trellis column; unreachable states carry INT_MAX and are never extended; "
              "at the end start from the minimum-metric state and walk the trellis backward, emitting the input bit implied by each state, then reverse and drop the constraint-1 tail bits",
    input="the received bit string (padded with zeros to a symbol multiple)", output="the most likely input bits", state="2^(constraint-1) path metrics; a trellis of predecessor indices, one column per symbol", update="per symbol",
    assumptions=["hard decisions (Hamming distance), so soft channel information is discarded; memory grows linearly with the message (no sliding-window traceback)", "the encoder started in state 0 (path_metrics.front() = 0)"],
    fitness_value_in_ancestor="maximum-likelihood decoding of a convolutional code in O(states x length) instead of O(2^length)", failure_landscape="by reading: a burst longer than the constraint length defeats it (no interleaver here); the min_element tie-break at the end favours the lowest state",
    human_prior="Viterbi 1967; the add-compare-select formulation and the tie-to-zero convention are the implementer's", evidence_ref=V + ":BranchMetric, PathMetric, UpdatePathMetrics, Decode", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the four functions and the Trellis typedef",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_CALL", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP", "uncertainty": "POINT", "hidden_state": "ESTIMATES"})

c.reject("operator<< and the drivers (viterbi_main.cpp, viterbi_test.cpp)", reason="OTHER", evidence="instruments and I/O", note="the test file is a ready oracle for a Stage C run (known codes with known decodings)")
c.reject("'Viterbi algorithm' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the same add-compare-select over any trellis (HMM, PoS tagging) is the recurrence the vault's umdhmm and other bodies hold; the branch metric (Hamming vs log-emission) is what differs", note="recurrence candidate: umdhmm-kanungo-1.02 (NOT_CUT) will hold the HMM form")

c.edge(enc, acs, "feeds", note="the output table is the branch metric's reference")

c.pressure("a_sequence_must_be_recovered_after_a_channel_flips_symbols_and_the_receiver_knows_only_the_generating_machine",
    condition="a finite-state machine emits redundant symbols from an input sequence; some symbols are flipped; the receiver holds the machine's description and must return the input", resource_or_constraint="memory per state and per symbol; a decision per symbol",
    failure_condition="wrong input bits after decoding", world_punishes="decoders that decide per symbol (no memory) and decoders that enumerate paths (no budget)", world_rewards="keeping one survivor per state",
    observable_consequence="bit error rate vs flip probability, against the per-symbol decision baseline", vacuity_condition="no flips, or a code with one state", trivial_shortcuts="a world that reveals the input",
    cheat_control="a decoder handed the true input must show zero errors; the per-symbol (memoryless) baseline must show errors at any positive flip rate: the world must separate them or the redundancy pressure is absent",
    cost_class="CPU-scale", source_evidence="viterbi.cpp Decode; record domain error-correction", purpose="PURPOSE: convolutional code decoding (Viterbi 1967)")

c.ancestry("algorithm_from", "Viterbi 1967; the encoder is the standard rate-1/k feed-forward convolutional coder", note="from the code; record lineage not re-read")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["record/body mismatch: the record calls it an HMM; the body is a convolutional decoder (reported to Techne as a census defect, not repaired)", "nothing ran"], note="every function in viterbi.cpp is in one of the two organs or rejected")
c.save(state="DEEP")
