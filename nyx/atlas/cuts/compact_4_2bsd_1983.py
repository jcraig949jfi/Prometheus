"""Cut: compact-4.2bsd-1983 (ancestry-aware, Stage A DEEP-by-size: the whole body is 666 lines; SOURCE_READ on M3; fourth of the
2026-09-17 NOT_CUT order). Read in full: compact.h (67), compact.c (273), tree.c (153). Skimmed: uncompact.c (173; the decoder
mirrors encode/uptree). Nothing ran. The record marks this a LOSER (superseded by compress-4.2.4 / LZW); the anatomy says why:
every symbol costs a walk to the root plus an O(depth) exchange-and-rebalance, and the tree never forgets.
"""
from nyx.atlas.author import Cut

C = "vault:compact-4.2bsd-1983/upstream/compact.c"
T = "vault:compact-4.2bsd-1983/upstream/tree.c"
H = "vault:compact-4.2bsd-1983/upstream/compact.h"
c = Cut("compact-4.2bsd-1983", mode="ANCESTRY_AWARE", inspected=["compact.h, compact.c, tree.c (all)", "uncompact.c (skimmed)"],
        evidence=[("SOURCE_READ", C), ("SOURCE_READ", T), ("SOURCE_READ", H)],
        note="an adaptive (one-pass, no header) Huffman coder from 1979: the model and the code are the same tree, updated after every symbol by a "
             "sibling-property repair; two reserved leaves (NC = not-yet-seen escape, EF = end) make the code self-describing")

tree = c.organ("code_tree_as_a_flat_array_of_nodes_with_parent_pointers_and_two_counts", human_name="struct node dict[258]; in[258] leaf index (compact.h)", status="ACCEPTED",
    mechanism="258 node slots hold a binary tree bottom-up: each node has a parent pointer with side flags (LLEAF/RLEAF say which children are leaves, FBIT which side this node is on), two child slots that are either node pointers or character codes, "
              "and TWO counts (one per child side); the leaf table in[] maps a byte to the node and side that holds it; 'bottom' is the newest node",
    input="symbols", output="a path from any leaf to the root (the code word, read parent by parent)", state="dict[258], in[258], bottom", update="per symbol (uptree) and per new symbol (insert)",
    assumptions=["at most 256 symbols plus NC and EF, so the array bound is static", "the count belongs to the EDGE (parent, side), which is what lets a whole subtree be swapped by exchanging two child slots"],
    fitness_value_in_ancestor="the model and the code are one structure; encoding is a leaf-to-root walk, no code table is ever built",
    failure_landscape="UNKNOWN by run; by reading: counts are longint and never rescaled, so after 2^31 symbols the ordering invariant breaks", evidence_ref=H + ":32-57", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="the four structs and the three tables in compact.h",
    coverage={"input_topology": "SEQUENCE", "output_topology": "TREE", "state_amount": "CONSTANT", "state_persistence": "PER_EPISODE", "memory": "FULL_HISTORY", "stochasticity": "DETERMINISTIC", "representation_sensitivity": "SENSITIVE"})

enc = c.organ("encode_by_walking_leaf_to_root_and_emitting_the_reversed_path", human_name="encode() (compact.c 180-224)", status="ACCEPTED",
    mechanism="starting at the symbol's leaf, push the side bit of each parent edge onto a 16-bit-word stack until the root; then pop the stack emitting bits msb-first into a 16-bit output accumulator that is flushed two bytes at a time",
    input="a symbol id (byte, NC or EF)", output="its current code word, bit-serial", state="d (16-bit accumulator), bits (fill count), the stack", update="per symbol",
    assumptions=["code length <= 17*16 bits (stack[17]); the tree depth is bounded by the number of symbols"], fitness_value_in_ancestor="no code table; the current tree IS the code",
    failure_landscape="UNKNOWN by run", evidence_ref=C + ":180-224", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="encode()",
    coverage={"input_topology": "SCALAR", "output_topology": "SEQUENCE", "state_amount": "LOG", "stochasticity": "DETERMINISTIC", "update_topology": "RECURSIVE"})

up = c.organ("sibling_property_repair_by_count_increment_and_block_leader_exchange", human_name="uptree() (tree.c 37-127) with the index list dir[514]", status="ACCEPTED",
    mechanism="after a symbol, increment the count on its leaf edge and walk toward the root; at each level, if the incremented count now exceeds the count of the next edge in the (implicit) ordered sibling list, exchange this edge's subtree with the LEADER of its count block (found through the index list dir/top, "
              "which chains one index record per distinct count value), fix the leaf/side flags, and continue from the leader's position; the index list is maintained so that equal-count edges form contiguous blocks (create an index when rc == sc+1, dispose one when rc > sc+1)",
    input="the symbol's leaf", output="a tree that again satisfies the sibling property (counts non-decreasing along the sibling order, parents above children)", state="dir[514] index records, head/flist free list, per-edge top[] pointers", update="per symbol, O(depth) exchanges",
    assumptions=["a Huffman tree is optimal iff it has the sibling property (Gallager 1978); maintaining it incrementally keeps the code optimal for the counts so far"],
    fitness_value_in_ancestor="one pass over the input; the decoder replays the same updates so no tree is transmitted", failure_landscape="by reading: the exchange logic is written against a compiler quirk ('change code when Cory gets v. 7'); the pointer juggling through union treep is the fragile part",
    human_prior="Faller (1973) / Gallager (1978) sibling-property algorithm, implemented before Knuth's (1985) and Vitter's (1987) forms; the 'index list of count blocks' is McMaster's own device",
    evidence_ref=T + ":37-127", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="uptree() + exch() + the dir/top bookkeeping",
    coverage={"input_topology": "EVENT", "output_topology": "TREE", "state_amount": "CONSTANT", "state_persistence": "PER_EPISODE", "memory": "FULL_HISTORY", "stochasticity": "DETERMINISTIC",
              "update_topology": "RECURSIVE", "order_sensitivity": "SENSITIVE", "adaptation": "STRUCTURE"})

esc = c.organ("escape_leaf_for_unseen_symbols_followed_by_the_raw_byte_and_a_split_insert", human_name="NC / insert() (compact.c 118-131; tree.c 8-34)", status="ACCEPTED",
    mechanism="a reserved leaf NC (code 0401) is always present; an unseen byte is sent as code(NC) then 8 raw bits; both sides then split the NC leaf: the old NC node becomes an internal node whose children are the new symbol (count 0) and a fresh NC; then uptree(NC) and uptree(symbol) run",
    input="a byte with SEEN clear", output="escape + literal; a grown tree", state="in[c].flags SEEN/FBIT", update="once per distinct byte",
    assumptions=["the alphabet is bytes, so 8 literal bits suffice; the new symbol enters with count 0 so its first code is long"], fitness_value_in_ancestor="no header, no static model; the file starts compressing from byte two",
    failure_landscape="UNKNOWN by run; by reading: the first occurrence of each of 256 bytes costs code(NC)+8 bits, so short or high-entropy files expand (the 'Does not save bytes' branch at compact.c 224-236 refuses to keep them)",
    evidence_ref=C + ":118-131, 224-236; " + T + ":8-34", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the else branch of the main loop and insert()",
    coverage={"input_topology": "SCALAR", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC", "update_topology": "EVENT_DRIVEN", "adaptation": "STRUCTURE"})

eof = c.organ("in_band_end_symbol_instead_of_a_length_field", human_name="EF (0400) leaf; encode(EF) at end; bit flush", status="ACCEPTED",
    mechanism="a second reserved leaf EF is present from the start with count 1; the encoder ends the stream with code(EF) and pads the last 16-bit word; the decoder stops on EF, so no length is stored and the stream is self-terminating",
    input="end of input", output="the terminator code and a flushed word", state="none", update="once", assumptions=["EF's count stays 1 forever (it is never uptree'd until the end), so its code lengthens as the file grows -- the cost is paid once"],
    fitness_value_in_ancestor="streams can be piped; no seek-back to write a length", failure_landscape="UNKNOWN by run", evidence_ref=C + ":146-160", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="encode(EF) and the flush",
    coverage={"input_topology": "EVENT", "output_topology": "SEQUENCE", "state_amount": "NONE", "stochasticity": "DETERMINISTIC"})

gate = c.organ("keep_only_if_smaller_gate_with_a_two_byte_magic_and_a_percent_report", human_name="COMPACTED magic 017777; oc >= ic refusal (compact.c 60-70, 224-236)", status="ACCEPTED",
    mechanism="the output starts with a two-byte magic (017777; 017437 is 'pack' and refused); at the end, if the output is not shorter the file is deleted and the input kept ('Does not save bytes'); otherwise the input is unlinked and a compression percentage is printed with an integer-scaling trick to avoid overflow",
    input="ic, oc byte counts", output="keep/discard; a report", state="ic, oc", update="per file", assumptions=["disk space is the fitness; a file that grew is a failure"],
    fitness_value_in_ancestor="the tool never makes a file bigger", failure_landscape="UNKNOWN by run", evidence_ref=C + ":60-70, 224-250", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the magic check and the oc>=ic branch",
    coverage={"input_topology": "SCALAR", "output_topology": "DECISION", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC"})

c.reject("argv/fopen/fstat/chmod/unlink plumbing and the error-exit ladder (goto closein/closeboth/fail)", reason="GENERIC_LANGUAGE_MECHANICS", evidence=C + ":25-60, 236-270")
c.reject("byte-order union cio and the VAX/sun/pdp11 ifdefs", reason="INHERITED_FROM_RUNTIME_OR_LIBRARY", evidence=H + ":1-30", note="1983 portability; no behaviour")
c.reject("'adaptive Huffman coding' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the tree, the walk, the repair, the escape and the terminator are each separately replaceable (the LZW successor keeps none of them)")

c.edge(tree, enc, "feeds"); c.edge(enc, up, "triggers", note="every encoded symbol is then uptree'd"); c.edge(up, tree, "updates"); c.edge(esc, tree, "updates"); c.edge(esc, up, "triggers"); c.edge(tree, esc, "gates", note="SEEN flag")
c.edge(eof, enc, "feeds"); c.edge(gate, eof, "verifies", note="oc vs ic after the flush")

c.pressure("a_stream_must_be_encoded_in_one_pass_with_no_side_channel_and_the_decoder_must_reconstruct_the_model_from_the_stream_alone",
    condition="symbols arrive one at a time and each must be emitted before the next is seen; the receiver has no header, no table and no second pass; the score is output length",
    resource_or_constraint="one pass; bounded memory (a fixed node table); the receiver's model may use only what has already been transmitted", failure_condition="output longer than input, or a receiver that desynchronises",
    world_punishes="expansion on short or high-entropy inputs (the escape cost); model updates the receiver cannot replay", world_rewards="an organism whose model after k symbols is a deterministic function of those k symbols",
    observable_consequence="compressed/uncompressed ratio as a function of input length on stationary and on drifting sources; desynchronisation count under injected errors", vacuity_condition="a source with a known fixed distribution (a static code wins) or a two-pass budget",
    trivial_shortcuts="transmitting the model as a header (forbidden by the condition); a fixed code tuned to the test corpus", cheat_control="an organism handed the true source distribution must beat the ancestor on a stationary source and lose to it on a source that drifts after 10^4 symbols: if the world cannot show both, it is not exerting the one-pass/adaptivity pressure",
    cost_class="CPU-scale", source_evidence="compact.c main loop 96-150; tree.c uptree; record domain 'superseded-design'", purpose="PURPOSE: adaptive Huffman file compression (McMaster 1979)")

c.pressure("an_incrementally_maintained_ordering_must_stay_valid_after_every_single_count_increment",
    condition="a structure orders items by counts that increase one at a time; after each increment the ordering invariant must hold before the next item is processed; repairs cost time per level",
    resource_or_constraint="O(depth) per update; no batch rebuild allowed", failure_condition="an invariant violation that goes unrepaired (a non-optimal code, or worse a decoder mismatch)",
    world_punishes="rebuilding from scratch per symbol (time) and lazy repair (mismatch)", world_rewards="a repair that touches only the path from the changed item to the root", observable_consequence="repair operations per update vs invariant-check failures per update",
    vacuity_condition="counts arrive in sorted order", trivial_shortcuts="periodic full rebuild with the invariant checked only at rebuild time", cheat_control="an organism that rebuilds fully after every increment must show zero violations at maximal cost; an organism that never repairs must show violations after the first out-of-order increment: the world must see both",
    cost_class="CPU-scale", source_evidence="tree.c 37-127", purpose="PURPOSE: dynamic Huffman tree maintenance (Faller/Gallager)")

c.ancestry("algorithm_from", "Faller 1973 / Gallager 1978 sibling-property adaptive Huffman", note="from the source header ('Adaptive Huffman code ... On-line algorithm ... Colin L. McMaster 1979'); the record's lineage not re-read this pass")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["uncompact.c not read line by line (skimmed: the same tree code driven by input bits)", "no claim about optimality or about the LZW comparison was run"], note="every line of compact.c and tree.c is accounted for")
c.save(state="DEEP")
