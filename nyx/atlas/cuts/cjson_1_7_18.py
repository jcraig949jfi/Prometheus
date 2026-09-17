"""Cut: cjson-1.7.18 (cJSON; ancestry-aware, Stage A DEEP; SOURCE_READ on M3; position 42 of the 2026-09-17 NOT_CUT order). Read:
cJSON.c parse_number 307-383, parse_string 781-910, parse_value 1325-1380, parse_object 1614-1731, the parse_buffer struct and
CJSON_NESTING_LIMIT sites. NOT read: the printer (print_* / ensure), cJSON_Utils.c (JSON pointer / patch / merge), the item API,
the unity tests. Nothing ran (C; the record pairs it with radamsa under ASan on M2).
"""
from nyx.atlas.author import Cut

J = "vault:cjson-1.7.18/upstream/tree/cJSON-1.7.18/cJSON.c"
c = Cut("cjson-1.7.18", mode="ANCESTRY_AWARE", inspected=["cJSON.c 307-383, 781-910, 1325-1380, 1614-1731, 294, 1459-1463"], evidence=[("SOURCE_READ", J + ":307-383"), ("SOURCE_READ", J + ":781-910"), ("SOURCE_READ", J + ":1325-1380"), ("SOURCE_READ", J + ":1614-1731")],
        note="a recursive-descent JSON reader whose defensive form is the mechanism: every byte access goes through a bounds predicate on a (content, length, offset, depth) buffer, nesting is capped by a constant, strings are measured before allocation, numbers are copied into a bounded local buffer before strtod; a parse failure frees the partial tree and returns NULL; the fuzzing history (CVE-2019-11834 and others) is why each check exists")

bounds = c.organ("recursive_descent_over_a_bounded_buffer_with_a_bounds_predicate_on_every_access_and_a_constant_nesting_limit", human_name="parse_buffer {content, length, offset, depth}; can_access_at_index / cannot_access_at_index / can_read; parse_value (1325-1380); parse_array / parse_object depth check (1459, 1619) against CJSON_NESTING_LIMIT", status="ACCEPTED",
    mechanism="parse_value dispatches on the first byte (null/false/true by strncmp after a can_read check; string on a quote; number on '-' or a digit; array on '['; object on '{'); arrays and objects increment a depth counter and refuse beyond the limit (default 1000) before recursing; every read of buffer_at_offset is guarded by an offset-vs-length predicate; the top-level parser optionally requires the buffer to end after the value",
    input="bytes and a length", output="a tree or NULL with an error position", state="the buffer cursor and depth", update="per byte", assumptions=["input is hostile; the cost of a predicate per byte is acceptable"],
    fitness_value_in_ancestor="a parser that can be fuzzed to completion without crashing, in one C file", failure_landscape="by reading: the depth limit turns a stack overflow into a parse error; the history (the record names CVE-2019-11834) is the list of places a check was missing", human_prior="recursive descent (any JSON reader); the bounded-buffer discipline is the 1.7 rewrite's",
    evidence_ref=J + ":1325-1380; 1614-1731; 294", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the parse_* family and the buffer predicates",
    coverage={"input_topology": "SEQUENCE", "output_topology": "TREE", "state_amount": "LOG", "stochasticity": "DETERMINISTIC", "update_topology": "RECURSIVE", "failure_mode": "NONE_KNOWN", "recovery": "ROLLS_BACK"})

strp = c.organ("string_parsed_in_two_passes_measuring_escapes_before_one_exact_allocation_then_decoding_with_utf16_surrogate_handling", human_name="parse_string (781-910): the measuring loop (skipped_bytes), allocation_length, the decode loop, utf16_literal_to_utf8 (660)", status="ACCEPTED",
    mechanism="first pass walks to the closing quote counting backslash escapes (and failing if a backslash is the last byte); the output is allocated once at the measured upper bound; second pass copies bytes and decodes escapes, with \\u sequences converted from UTF-16 (surrogate pairs) to UTF-8 by a helper that returns 0 on a malformed pair; on failure the partial output is freed and the error position recorded",
    input="a quoted literal in the buffer", output="a NUL-terminated UTF-8 string", state="none", update="per string", assumptions=["measuring first is cheaper than growing; an over-estimate by the escape count is acceptable"],
    fitness_value_in_ancestor="no realloc, no overflow: the length is known before writing", failure_landscape="UNKNOWN by run", evidence_ref=J + ":781-910", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="parse_string + utf16_literal_to_utf8",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP"})

num = c.organ("number_copied_into_a_bounded_local_buffer_with_locale_decimal_point_substitution_then_strtod_with_integer_saturation", human_name="parse_number (307-383): number_c_string[64], get_decimal_point, strtod, INT_MAX/INT_MIN saturation", status="ACCEPTED",
    mechanism="up to 63 bytes of the number's character class (digits, sign, e/E, '.') are copied into a stack buffer, '.' replaced by the C locale's decimal point (so strtod works under any locale), NUL-terminated (the input need not be NUL-terminated), converted by strtod; no progress means a parse error; the integer field saturates at INT_MAX/INT_MIN rather than overflowing",
    input="the buffer at a number", output="valuedouble and valueint", state="none", update="per number", assumptions=["63 characters suffice for any number worth parsing (longer numbers are silently truncated: a known limitation)"],
    fitness_value_in_ancestor="locale-proof and length-proof numeric parsing with the C library's converter", failure_landscape="by reading: a 64+ character number parses as its prefix without error", evidence_ref=J + ":307-383", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="parse_number",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SCALAR", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC"})

c.reject("the printer (print_value / print_object / ensure with its doubling buffer), cJSON_Utils.c (JSON Pointer, Patch, Merge Patch, sorting), the item construction and lookup API, hooks, the unity test framework", reason="OTHER", evidence="NOT READ; residue")
c.reject("the doubly linked child list with head->prev = tail (1697)", reason="BELOW_MEANINGFUL_GRAIN", evidence=J + ":1693-1699", note="a representation choice")
c.reject("'JSON parser' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the bounded-buffer discipline, the two-pass string and the bounded number are separable defences; a grammar-only parser has none of them")

c.edge(bounds, strp, "feeds"); c.edge(bounds, num, "feeds"); c.edge(strp, bounds, "feeds", note="object keys")

c.pressure("a_reader_of_a_recursive_text_format_must_accept_every_byte_sequence_without_memory_error_while_parsing_valid_input_at_linear_cost",
    condition="an organism reads untrusted bytes into a tree; inputs include truncated, over-nested, escape-broken and locale-varying forms; a crash or out-of-bounds read is the failure; valid inputs must parse in linear time and bounded stack", resource_or_constraint="stack depth; one allocation per node",
    failure_condition="any out-of-bounds access, unbounded recursion or leak on failure", world_punishes="reading past the length; recursing without a cap; allocating before measuring", world_rewards="per-access bounds predicates; a depth constant; measure-then-allocate",
    observable_consequence="crashes and sanitizer reports per million mutated inputs (the radamsa pair), and parse time vs input size on valid documents", vacuity_condition="trusted, well-formed input only", trivial_shortcuts="rejecting everything (which the valid-input score punishes)",
    cheat_control="an organism given a validity oracle must accept exactly the valid inputs at zero crashes; the 1.7 parser with the depth check removed must crash on a 100,000-deep array: the world must show both",
    cost_class="CPU-scale", source_evidence="cJSON.c parse_* family; the record's fuzzing pair with radamsa-0.6", purpose="PURPOSE: defensive JSON parsing (Gamble 2009-)")

c.ancestry("historical_version_of", "cJSON (Gamble 2009) as rewritten for 1.7 (2017) around parse_buffer after fuzzing findings", note="from the source and the record")
c.residue("PARTIALLY_EXPLAINED", ["printer and utils unread", "nothing ran; the fuzzing pair is an M2 world"], note="the defensive discipline is the mechanism and it is located line by line")
c.save(state="DEEP")
