"""Cut: md5-rfc1321 (the RFC text itself, 1,178 lines, with Rivest's reference C in its appendix; ancestry-aware, Stage A COARSE;
SOURCE_READ on M3; seventeenth of the 2026-09-17 NOT_CUT order). Read: section 3 (steps 1-5) in full; the appendix code skimmed.
The body is a SPECIFICATION with reference code, so every organ is a mechanism the text defines; the record marks it a LOSER
(broken as a collision-resistant hash since 2004), which the cut treats as the failure landscape of the design, not of the text.
"""
from nyx.atlas.author import Cut

R = "vault:md5-rfc1321/upstream/rfc1321.txt"
c = Cut("md5-rfc1321", mode="ANCESTRY_AWARE", inspected=["rfc1321.txt section 3 (lines 119-295) in full; appendix code skimmed"], evidence=[("SOURCE_READ", R + ":119-295")],
        note="a Merkle-Damgard construction with a four-round compression function; the organs are the padding rule, the chaining, the nonlinear round functions, the message-word schedule with rotation constants, and the sine-derived additive constants")

pad = c.organ("length_padding_to_a_block_boundary_with_the_message_length_appended", human_name="Steps 1-2 (3.1, 3.2)", status="ACCEPTED",
    mechanism="append a single 1 bit, then 0 bits until the length is 448 mod 512, then the 64-bit original length (low word first); padding is applied even when the length is already 448 mod 512, so every message has a distinct padded form",
    input="a message of b bits", output="a multiple of 512 bits", state="none", update="once", assumptions=["the length suffix is what prevents trivial extension of the padded message into another valid padded message (but not the length-extension attack on the digest itself)"],
    fitness_value_in_ancestor="unambiguous parsing of the last block", failure_landscape="by reading: the Merkle-Damgard length-extension property: knowing H(m) and |m| one can compute H(m || pad || m') without m", evidence_ref=R + ":132-159", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="sections 3.1-3.2",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "NONE", "stochasticity": "DETERMINISTIC"})

chain = c.organ("chained_compression_over_512_bit_blocks_with_feed_forward_addition", human_name="Steps 3-5: the (A,B,C,D) buffer, the per-block save/add-back, the output", status="ACCEPTED",
    mechanism="four 32-bit registers start at fixed constants; for each block the registers are saved, 64 operations mix the block in, then the saved values are ADDED back (feed-forward) so the compression function is not invertible from its output; the final registers are the digest",
    input="the padded message blocks", output="a 128-bit digest", state="A,B,C,D (128 bits)", update="per block", assumptions=["collision resistance of the whole follows from that of the compression function (Merkle 1989, Damgard 1989) -- the assumption that failed in practice"],
    fitness_value_in_ancestor="streaming: a message of any length is hashed with 128 bits of state", failure_landscape="the record's own: differential collisions in the compression function (Wang & Yu 2004) break the construction; the feed-forward does not help",
    human_prior="Merkle-Damgard; the four-register width chosen for 32-bit machines of 1991", evidence_ref=R + ":160-183, 270-295", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="sections 3.3-3.5",
    coverage={"input_topology": "SEQUENCE", "output_topology": "VECTOR", "state_amount": "CONSTANT", "state_persistence": "PER_CALL", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP", "failure_mode": "CORRUPTS"})

rounds = c.organ("four_rounds_of_a_bitwise_nonlinear_function_plus_message_word_plus_constant_then_rotate_and_add", human_name="Step 4: F, G, H, I; [abcd k s i] = a = b + ((a + f(b,c,d) + X[k] + T[i]) <<< s)", status="ACCEPTED",
    mechanism="each of 64 operations updates one register from the other three: add a bitwise selector/majority/parity/xor-or function of (b,c,d), a message word X[k], and a table constant T[i]; rotate left by s; add b; the registers rotate roles (ABCD, DABC, CDAB, BCDA); rounds use F (if-then-else), G (a different selector), H (parity), I (y xor (x or not z))",
    input="the block X[0..15], the four registers", output="updated registers", state="the registers", update="64 times per block",
    assumptions=["the text's own claim: if the inputs' bits are independent and unbiased, each function's output bits are too", "the mix of boolean functions, modular addition and rotation is 'ARX plus boolean' -- fast on 32-bit hardware"],
    fitness_value_in_ancestor="speed on 1991 hardware with 'strong' mixing by the standards of the time", failure_landscape="the differential path that breaks MD5 goes through these round functions' weak diffusion in rounds 1-2", human_prior="Rivest's design; the round functions are chosen for bitwise-parallel nonlinearity",
    evidence_ref=R + ":184-269", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the four function definitions and the 64 operations",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP", "representation_sensitivity": "SENSITIVE"})

sched = c.organ("message_word_schedule_and_rotation_constants_per_round", human_name="the k and s columns of the 64 operations (rounds: k = i, 5i+1, 3i+5, 7i mod 16; s = 7/12/17/22, 5/9/14/20, 4/11/16/23, 6/10/15/21)", status="ACCEPTED",
    mechanism="each round visits all 16 message words once in a fixed permutation (identity, then strides 5, 3, 7 with offsets) and uses four rotation amounts cycling per operation; the schedule is a constant table, not derived from the message",
    input="the round and operation index", output="which word and which rotation", state="none", update="per operation", assumptions=["the four strides are coprime to 16 so every word is used exactly once per round"],
    fitness_value_in_ancestor="every message bit influences every round", failure_landscape="by reading: a fixed schedule lets an attacker choose message differences that cancel across rounds", evidence_ref=R + ":234-269", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the k, s columns",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC"})

sine = c.organ("nothing_up_my_sleeve_constants_from_the_integer_part_of_2_32_abs_sin_i", human_name="the table T[1..64]", status="ACCEPTED",
    mechanism="T[i] = floor(2^32 x |sin(i)|), i in radians, i = 1..64; the constants are published as derived from a transcendental function so that no hidden structure can be suspected in their choice",
    input="i", output="a 32-bit constant", state="none", update="n/a", assumptions=["a publicly derivable constant is trusted more than an arbitrary one (a social mechanism encoded in arithmetic)"],
    fitness_value_in_ancestor="trust in the design; breaks the symmetry between operations", failure_landscape="none by reading", human_prior="the 'nothing up my sleeve' convention", evidence_ref=R + ":210-215 and the appendix table", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the T table definition",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC"})

c.reject("the reference C implementation in the appendix (MD5Init/Update/Final, byte-order handling), the test suite (mddriver), the executive summary and terminology sections", reason="OTHER", evidence="skimmed only; the appendix code implements the five steps above and is the natural Stage C body (it compiles anywhere with a C compiler -- not on M3)", note="not rejected on the merits; unread this pass")
c.reject("'MD5' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="padding, chaining, rounds, schedule and constants are separately replaceable; SHA-1 keeps the first two and changes the rest")

c.edge(pad, chain, "feeds"); c.edge(chain, rounds, "feeds"); c.edge(sched, rounds, "feeds"); c.edge(sine, rounds, "feeds"); c.edge(rounds, chain, "updates")

c.pressure("a_fixed_size_fingerprint_of_arbitrary_input_must_make_two_inputs_with_one_fingerprint_infeasible_to_construct_against_an_adversary_who_reads_the_design",
    condition="the organism maps any input to n bits; an adversary who knows the map fully tries to produce two inputs with the same output (collision) or an input for a given output (preimage); the organism's cost per input bit is bounded",
    resource_or_constraint="n bits of state; a few operations per input word; the design is public", failure_condition="a collision found in far fewer than 2^(n/2) trials", world_punishes="linear diffusion, weak nonlinearity, message-independent schedules",
    world_rewards="mixing that resists differential cancellation", observable_consequence="trials to first collision under a differential search vs the birthday bound; MD5's own history (2^64 -> 2^24) is the measured failure",
    vacuity_condition="no adversary (a checksum suffices)", trivial_shortcuts="a world where the adversary cannot read the design", cheat_control="an organism that is a random oracle (a world-supplied lookup) must show the birthday bound; MD5 must show the known 2^24 differential shortcut: if the world cannot distinguish them, it is not exerting the adversarial pressure",
    cost_class="CPU-scale", source_evidence="record disposition LOSER; RFC 1321 section 3", purpose="PURPOSE: cryptographic message digest (Rivest 1992; broken Wang & Yu 2004)")

c.ancestry("historical_version_of", "MD4 (Rivest 1990) -> MD5 (1991-92); SHA-1 (1995) is the same construction with a different compression function", note="from the RFC's own introduction and general knowledge; the record's lineage not re-read")
c.residue("PARTIALLY_EXPLAINED", ["the appendix reference code and its byte-order/endianness handling not read line by line", "the specific differential path that breaks MD5 is not in the body; the failure landscape cites the record's disposition"], note="the specification's five steps are fully accounted for")
c.save(state="COARSE")
