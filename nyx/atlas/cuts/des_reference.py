"""Cut: des-reference (ancestry-aware; SOURCE_READ des.c in full structure: tables 7-100, generate_sub_keys 148-245, process_message 246-420).
Techne's recipe was read: it is a ROUND TRIP test, not the known-answer test the record calls the oracle."""
from nyx.atlas.author import Cut

S = "F:/Prometheus/vault/fossils/des-reference/upstream/tree/des.c"
c = Cut("des-reference", mode="ANCESTRY_AWARE", inspected=["des.c (tables, generate_sub_keys, process_message)", "recipe.json runs"],
        evidence=[("SOURCE_READ", S)], note="an OBSOLETED_BY_ENVIRONMENT fossil: the machinery still runs exactly; the world's compute grew past its key length")

perm = c.organ("table_driven_bit_gather", human_name="permutation / expansion / compression tables (IP, FP, E, P, PC-1, PC-2)", status="ACCEPTED",
    human_interpretation="rearrange the bits of a block according to a fixed table",
    mechanism="for output bit i, read the table entry t[i], fetch input bit t[i]-1 by masking its byte, and OR it into output byte i/8 at position i%8; the same loop shape serves six tables; a table with repeated entries duplicates bits (expansion 32->48), a table shorter than its input drops bits (56->48, 64->56)",
    input="a bit vector + a table", output="a bit vector", state="none (tables are constants)", update="none", assumptions=["tables are the standard's data"],
    fitness_value_in_ancestor="all diffusion across S-box boundaries comes from P and E; IP/FP are historically hardware-convenience with no cryptographic role", failure_landscape="none structural; bit-serial loop is slow (software, not the standard's fault)",
    decomposability="one mechanism, six data tables", composability="any fixed bit rewiring", evidence_ref=S + ":7-100,255-262,278-285,360-368", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN",
    source_boundary="the six identical for-loops over a table", coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "representation_sensitivity": "SENSITIVE"})

fe = c.organ("swap_halves_and_xor_keyed_function_into_one_half", human_name="Feistel round", status="ACCEPTED",
    human_interpretation="the structure that makes the cipher invertible regardless of the round function",
    mechanism="split the block into L and R; new L = old R; new R = old L XOR f(old R, subkey_k); after 16 rounds swap once more; because f is only XORed in, running the same rounds with subkeys in reverse order inverts the whole thing without inverting f",
    input="64-bit block, 16 subkeys, mode", output="64-bit block", state="l[4], r[4] per round", update="16 iterations", assumptions=["XOR is its own inverse"],
    fitness_value_in_ancestor="decryption is the same code with key_index = 17-k (line 288-292)", evidence_ref=S + ":265-275,286-292,370-385", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN",
    source_boundary="process_message round loop", coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "CONSTANT", "update_topology": "SWEEP", "stochasticity": "DETERMINISTIC"})

sb = c.organ("six_to_four_bit_substitution_from_eight_tables", parent=fe, human_name="S-boxes", status="ACCEPTED",
    mechanism="the 48 expanded-and-keyed bits are cut into eight 6-bit groups; each group's outer two bits pick a row and inner four bits a column in that group's 64-entry table; the 4-bit outputs are concatenated; the only non-linear step in the cipher",
    input="48 bits", output="32 bits", state="none", update="none", assumptions=["the tables are the standard's (their design criteria were secret in 1977)"],
    fitness_value_in_ancestor="all non-linearity; without it the cipher is affine and breaks with 64 plaintexts", evidence_ref=S + ":45-84,296-358", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN",
    source_boundary="the eight row/column blocks", coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "NONE", "representation_sensitivity": "SENSITIVE"})

ks = c.organ("subkey_schedule_by_rotating_two_halves", human_name="key schedule (PC-1, rotations, PC-2)", status="ACCEPTED",
    mechanism="the 56 key bits (after a table gather that drops 8 parity bits) are split into two 28-bit halves; for each of 16 rounds both halves are rotated left by 1 or 2 positions per a fixed schedule table, and 48 of the 56 bits are gathered by a second table to form that round's subkey; all 16 subkeys are precomputed before any block is processed",
    input="64-bit key", output="16 x 48-bit subkeys", state="c[4], d[4] rotating halves; key_sets[17]", update="16 rotations", assumptions=["rotation amounts sum to 28 so the halves return to start"],
    fitness_value_in_ancestor="each round sees a different 48-bit selection of the same 56 bits", failure_landscape="weak keys (all-zero halves) make every subkey identical -- present in the standard, not tested here",
    evidence_ref=S + ":148-245", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="generate_sub_keys",
    coverage={"input_topology": "VECTOR", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "update_topology": "SWEEP", "stochasticity": "DETERMINISTIC"})

c.reject("'DES' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="four mechanisms with distinct data/state (above); the Feistel structure and the S-boxes are independently replaceable (later ciphers kept one and changed the other)")
c.reject("initial/final permutation as cryptographic machinery", reason="STATE_OBSERVATIONALLY_IRRELEVANT",
         evidence="IP and FP are fixed, key-independent, mutually inverse bit rewirings applied outside the rounds; they change no security property (a known fact, not measured here) -- kept as INSTANCES of table_driven_bit_gather, rejected as a separate organ",
         note="the human standard lists them as steps; the anatomy does not need them")
c.reject("byte-by-byte bit extraction (0x80 >> ...) idiom", reason="GENERIC_LANGUAGE_MECHANICS", evidence="the same three-line idiom appears 8 times; it is how C addresses a bit, not machinery")
c.reject("Techne's oracle claim 'known-answer test'", reason="OTHER",
         evidence="recipe.json runs: generate a random key, encrypt, decrypt, compare (roundtrip_identical=yes; ciphertext_differs=yes). A round trip passes for ANY invertible transform, e.g. XOR with the key; no published FIPS vector is checked",
         note="TECHNE FEEDBACK: record.example says 'the ORACLE: a known-answer test'; the executed test is weaker than the record claims")

c.edge(ks, fe, "feeds", note="subkeys consumed one per round"); c.edge(perm, fe, "transforms", note="E before the XOR, P after the S-boxes, IP/FP outside")
c.edge(fe, sb, "feeds"); c.edge(sb, perm, "feeds"); c.edge(perm, ks, "transforms", note="PC-1 and PC-2 are table gathers inside the schedule")
c.edge("ENVIRONMENT", fe, "gates", note="mode flips the subkey order")

c.pressure("adversary_with_growing_compute_against_a_fixed_secret_size",
    condition="the secret is a fixed number of bits; the cost of trying them all falls every year; the transform itself has no known shortcut", resource_or_constraint="key length fixed by the standard; adversary compute",
    failure_condition="exhaustive search becomes affordable (1998: days)", world_punishes="a parameter frozen in a document", world_rewards="nothing inside the machinery -- the fix was a new standard",
    observable_consequence="withdrawal of the standard; the fossil still round-trips", vacuity_condition="adversary compute stops growing", trivial_shortcuts="none",
    cheat_control="N/A", cost_class="2^56 operations", source_evidence="record.human_failure_condition", purpose="PURPOSE: confidentiality of 64-bit blocks under a shared key")
c.pressure("confusion_and_diffusion_in_few_operations",
    condition="every output bit must depend non-linearly on every input and key bit, on 1977 hardware", resource_or_constraint="gate count / cycle count",
    failure_condition="a linear or local dependency exposes the key from few plaintexts", world_punishes="affine structure; slow diffusion", world_rewards="a non-linear step and a rewiring step per round, repeated",
    observable_consequence="avalanche after few rounds (NOT measured here; record names it as the behavioural entry point)", vacuity_condition="no adversary", trivial_shortcuts="a random-looking but linear map",
    cheat_control="a round-count sweep measuring output-bit flip fraction per input-bit flip (planned, not run)", cost_class="16 rounds x (8 table lookups + 3 rewirings)", source_evidence="source structure", purpose="PURPOSE: same")

c.residue("EXPLAINED_BY_CURRENT_CUT", ["run_des.c (file I/O driver) not read; it is the harness, not the cipher", "the 8 S-box tables are data whose design criteria are not in the fossil (published later by IBM); the atlas cannot say why these tables"],
          note="4 mechanisms account for every operation in process_message and generate_sub_keys")
c.save(state="DEEP")
