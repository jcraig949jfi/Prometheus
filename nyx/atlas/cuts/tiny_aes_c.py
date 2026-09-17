"""Cut: tiny-aes-c (ancestry-aware, Stage A DEEP-by-size; SOURCE_READ aes.c 45-146 (constants, tables), 146-235 (KeyExpansion, ctx), 237-410
(round functions and inverses, grepped), 413-466 (Cipher / InvCipher), 467-572 (modes)). 572 lines; organ names chosen to line up with
the des-reference cut where the mechanism is the same kind and to diverge where it is not."""
from nyx.atlas.author import Cut

S = "vault:tiny-aes-c/upstream/tree/aes.c"
c = Cut("tiny-aes-c", mode="ANCESTRY_AWARE", inspected=["aes.c (all 572 lines; round functions by structure)"], evidence=[("SOURCE_READ", S)],
        note="the DES successor in the same sample: same purpose, same three ingredient KINDS (substitution table, permutation, key schedule), but a substitution-permutation network needs explicit inverse round functions where DES's Feistel structure needed none -- a human-similar / mechanism-different pair for Stage E")

sb = c.organ("byte_substitution_from_one_256_entry_table", human_name="SubBytes / sbox (and InvSubBytes / rsbox)", status="ACCEPTED",
    mechanism="each of the 16 state bytes is replaced by sbox[byte]; the inverse uses a second table; the table is the standard's (multiplicative inverse in GF(2^8) followed by an affine map, but stored as data here)",
    input="16 bytes", output="16 bytes", state="none", update="none", assumptions=["the table is the standard's data"], fitness_value_in_ancestor="the only non-linearity (compare des-reference::six_to_four_bit_substitution_from_eight_tables: eight 6->4 tables vs one 8->8 bijection)",
    evidence_ref=S + ":79-97,251-264,371-381", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="SubBytes + sbox",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "representation_sensitivity": "SENSITIVE"})

sr = c.organ("row_rotation_of_the_4x4_state_by_row_index", human_name="ShiftRows / InvShiftRows", status="ACCEPTED",
    mechanism="row r of the 4x4 byte state is rotated left by r positions (0, 1, 2, 3); a byte permutation with no arithmetic; the inverse rotates right",
    input="16 bytes", output="16 bytes", state="none", update="none", fitness_value_in_ancestor="inter-column diffusion (compare des-reference::table_driven_bit_gather: bit-level table permutation vs byte-level rotation)",
    evidence_ref=S + ":266-292,383-410", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="ShiftRows",
    coverage={"input_topology": "MATRIX", "output_topology": "MATRIX", "state_amount": "NONE", "representation_sensitivity": "SENSITIVE"})

mc = c.organ("column_mixing_by_a_fixed_matrix_over_gf_2_8_using_shift_and_conditional_reduce", human_name="MixColumns / xtime (and InvMixColumns / Multiply)", status="ACCEPTED",
    mechanism="each column is multiplied by the circulant matrix (2 3 1 1) over GF(2^8) with the polynomial 0x11b; multiplication by 2 is xtime (shift left, XOR 0x1b if the top bit was set); by 3 is xtime XOR identity; the code computes it as Tmp (the XOR of the column) and four xtime terms; the inverse matrix (14 11 13 9) needs a general Multiply (a shift-and-add loop or macro)",
    input="16 bytes", output="16 bytes", state="none", update="none", assumptions=["GF(2^8) with the AES polynomial"], fitness_value_in_ancestor="intra-column diffusion; with ShiftRows, full diffusion in two rounds",
    evidence_ref=S + ":294-336,350-369", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="MixColumns + xtime + Multiply",
    coverage={"input_topology": "MATRIX", "output_topology": "MATRIX", "state_amount": "NONE", "representation_sensitivity": "SENSITIVE"})

ks = c.organ("round_key_expansion_by_rotate_substitute_and_round_constant_every_nk_words", human_name="KeyExpansion / Rcon", status="ACCEPTED",
    mechanism="the first Nk words are the key; each further word is the previous word, which every Nk words is rotated a byte, byte-substituted through the sbox, and XORed with Rcon[i/Nk] (powers of 2 in GF(2^8)) -- and for AES-256 substituted again at the half-way word -- XORed with the word Nk back; all Nr + 1 round keys are precomputed",
    input="16/24/32-byte key", output="4 * (Nr + 1) words", state="RoundKey (in the ctx)", update="once per key", fitness_value_in_ancestor="compare des-reference::subkey_schedule_by_rotating_two_halves: both rotate and select, AES adds the cipher's own non-linearity to the schedule",
    evidence_ref=S + ":120-135,146-217", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="KeyExpansion + Rcon",
    coverage={"input_topology": "VECTOR", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "update_topology": "SWEEP", "stochasticity": "DETERMINISTIC"})

rd = c.organ("substitution_permutation_rounds_with_key_xor_and_a_separately_coded_inverse", human_name="Cipher / InvCipher / AddRoundKey", status="ACCEPTED",
    mechanism="AddRoundKey(0); for rounds 1..Nr: SubBytes, ShiftRows, (MixColumns except in the last round), AddRoundKey(round); decryption is a DIFFERENT function applying the inverse steps in reverse order with the round keys backwards -- unlike a Feistel cipher, every step must be invertible and the inverse must be written",
    input="16-byte block, round keys", output="16-byte block", state="state_t (4x4) during the call", update="Nr rounds (10/12/14)", assumptions=["every round step is a bijection"],
    fitness_value_in_ancestor="compare des-reference::swap_halves_and_xor_keyed_function_into_one_half: DES gets decryption for free from structure; AES pays with InvCipher, InvSubBytes, InvShiftRows, InvMixColumns (about 120 lines of the 572)",
    evidence_ref=S + ":237-249,413-466", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="Cipher + InvCipher + AddRoundKey",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "CONSTANT", "update_topology": "SWEEP", "stochasticity": "DETERMINISTIC"})

md = c.organ("block_chaining_modes_ecb_cbc_and_a_counter_keystream", human_name="AES_ECB_* / AES_CBC_*_buffer / AES_CTR_xcrypt_buffer", status="ACCEPTED",
    mechanism="ECB: the block function per block; CBC: XOR each plaintext block with the previous ciphertext (the IV first) before encrypting, and after decrypting; CTR: encrypt the IV, XOR the result with the data byte by byte, increment the IV as a big-endian 128-bit counter with carry, regenerate every 16 bytes -- the block cipher becomes a stream cipher and the same function encrypts and decrypts (no InvCipher needed)",
    input="a buffer, an IV", output="the buffer transformed in place", state="ctx->Iv (advances)", update="per block / per byte", assumptions=["CBC: length is a multiple of 16; CTR: the IV never repeats under one key"],
    evidence_ref=S + ":467-572", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the mode functions",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "memory": "LAST_VALUE", "update_topology": "SWEEP"})

c.reject("'AES' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="five mechanisms each in its own function with none sharing state; the modes are a sixth layer over the block function")
c.reject("the compile-time selection of key size and modes (#if AES256 / CBC / CTR / ECB, MULTIPLY_AS_A_FUNCTION)", reason="GENERIC_LANGUAGE_MECHANICS", evidence=S + ":45-75,98,199,338,467,489,535")
c.reject("test.c (FIPS-197 known-answer vectors)", reason="EFFECT_FROM_ENVIRONMENT", evidence="the oracle Techne runs (record: 'make test')", note="unlike des-reference, this fossil's shipped test IS a known-answer test")

c.edge(ks, rd, "feeds", note="round keys"); c.edge(sb, rd, "feeds"); c.edge(sr, rd, "feeds"); c.edge(mc, rd, "feeds"); c.edge(sb, ks, "feeds", note="SubWord in the schedule"); c.edge(mc, ks, "feeds", note="Rcon = powers of 2 in the same field")
c.edge(rd, md, "feeds"); c.edge(md, rd, "gates", note="CTR never calls InvCipher"); c.edge("ENVIRONMENT", md, "feeds", note="IV")

c.pressure("a_block_cipher_must_be_invertible_fast_and_diffuse_fully_in_few_rounds_on_8_bit_and_32_bit_machines",
    condition="the same key must encrypt and decrypt; every output bit must depend on every input and key bit after few rounds; the implementation must be small enough for smart cards and fast on desktops", resource_or_constraint="code size; table size; rounds",
    failure_condition="slow diffusion or a structural weakness", world_punishes="bit-level permutations (slow in software); structures that need many rounds", world_rewards="byte-oriented operations (table, rotation, small-field arithmetic) that diffuse in two rounds",
    observable_consequence="avalanche vs round count (not measured); the FIPS vectors", vacuity_condition="no adversary", trivial_shortcuts="a fixed random permutation table (2^128 entries; impossible)",
    cheat_control="the round-count sweep proposed for des-reference applies unchanged: a cipher with rounds reduced to 1 must FAIL an avalanche measure; if the world does not detect that, it is not measuring diffusion", cost_class="CPU-scale", source_evidence="the round structure; record entry point", purpose="PURPOSE: confidentiality of 128-bit blocks (the DES replacement, 2001)")
c.pressure("the_same_block_function_must_serve_streams_of_any_length_without_repeating_structure",
    condition="messages are not 16 bytes; identical blocks must not encrypt identically; sometimes decryption code cannot be afforded", resource_or_constraint="code size on the decrypt side; an IV that must not repeat",
    failure_condition="ECB's block-pattern leakage; a repeated CTR nonce", world_punishes="ECB on structured data", world_rewards="chaining (CBC) or a counter keystream (CTR, which also deletes the inverse cipher)",
    observable_consequence="ciphertext of a repeated plaintext under each mode", vacuity_condition="single-block messages", trivial_shortcuts="none",
    cheat_control="N/A", cost_class="CPU-scale", source_evidence=S + ":467-572", purpose="PURPOSE: same")

c.ancestry("superseded", "des-reference", note="Techne records 'AES replaced DES as the US standard' on both records (direction fixed by the note)")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["avalanche and the DES structural comparison are unmeasured reading claims", "nothing ran here; Techne's FIPS vectors are on M1"],
          note="every function in aes.c is assigned to one of six mechanisms")
c.save(state="DEEP")
