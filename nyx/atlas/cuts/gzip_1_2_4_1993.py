"""CORRECTION 2 2026-09-16 (Harmonia #317): the switch named below as deflate.c:667 is at deflate.c:672; 667 is match_length.
CORRECTION 2026-09-16 (annotation; nothing below is edited): the cut note 'a four-column table that changes NO mechanism' is WRONG
in one respect -- the level is ALSO consumed at deflate.c:667 (compr_level <= 3 selects deflate_fast) and trees.c:987 (block-flush
heuristic gated on level > 2). Recorded in nyx/atlas/predictions/MECH-GZIP-LEVELTABLE-001.json; the organ record carries the marker.
DO NOT RE-RUN THIS SCRIPT: it would reproduce the uncorrected text and drop the marker. A new cut, if needed, is a new script.

Cut: gzip-1.2.4-1993 (ancestry-aware, Stage A COARSE; SOURCE_READ deflate.c 154-290 (state, config table, hash macros), 357-420
(longest_match head), 516-560 (fill_window), 661-763 (deflate) in full; trees.c 94-274 (state) and function index; inflate.c 132-280
(index, huft_build signature); unlzw.c / bits.c / gzip.c by name). The 1993 DEFLATE implementation."""
from nyx.atlas.author import Cut

S = "vault:gzip-1.2.4-1993/upstream/tree/gzip-1.2.4/"
c = Cut("gzip-1.2.4-1993", mode="ANCESTRY_AWARE", inspected=["deflate.c (state, config, longest_match, fill_window, deflate)", "trees.c (state + index)", "inflate.c (index)", "file list"],
        evidence=[("SOURCE_READ", S + "deflate.c"), ("SOURCE_READ", S + "trees.c"), ("SOURCE_READ", S + "inflate.c")],
        note="LZ77 with hash chains + lazy matching + dynamic Huffman; the record's knob (-1..-9) is a four-column table that changes NO mechanism, only four thresholds -- a clean Stage C ablation target")

hc = c.organ("rolling_three_byte_hash_into_chains_of_prior_positions", human_name="UPDATE_HASH / INSERT_STRING / head[] / prev[]", status="ACCEPTED",
    mechanism="h = ((h << H_SHIFT) ^ c) & HASH_MASK over the next three bytes; INSERT_STRING stores the current position at head[h] and links the previous occupant into prev[pos & WMASK], so each hash bucket is a chain of earlier positions with the same 3-byte prefix, newest first; the chain is bounded by the window (positions older than MAX_DIST are ignored by the matcher)",
    input="window bytes at strstart", output="hash_head (the most recent candidate)", state="ins_h, head[HASH_SIZE], prev[WSIZE]", update="per input byte", assumptions=["3-byte minimum match; the hash need not be good, only fast"],
    fitness_value_in_ancestor="turns the O(n^2) search for repeats into a walk of a short chain", evidence_ref=S + "deflate.c:164-180,266-284", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the hash macros and the two arrays",
    coverage={"input_topology": "STREAM", "output_topology": "SCALAR", "state_amount": "CONSTANT", "memory": "WINDOW", "update_topology": "SINGLE_STEP"})

lm = c.organ("longest_match_walk_of_the_chain_with_a_length_bounded_early_exit", human_name="longest_match", status="ACCEPTED",
    mechanism="walk the chain from hash_head back toward the window limit; for each candidate first compare the byte at the current best length (a cheap reject), then the full string up to MAX_MATCH (258); keep the longest; stop after chain_length candidates (quartered when the previous match was already 'good') or when a match reaches nice_match; the comparison loop is unrolled 8x with an UNALIGNED_OK variant",
    input="hash_head, prev_length, window", output="match length and match_start", state="none", update="per position tried", assumptions=["strings up to 258 bytes; lookahead available"],
    fitness_value_in_ancestor="the cost of compression lives here; the chain and nice thresholds are the -1..-9 knob", evidence_ref=S + "deflate.c:357-486", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="longest_match",
    coverage={"input_topology": "SEQUENCE", "output_topology": "VECTOR", "state_amount": "NONE", "resource_dependence": "COMPUTE", "update_topology": "SWEEP"})

lz = c.organ("lazy_evaluation_deferring_a_match_by_one_byte_to_see_if_a_longer_one_starts_there", human_name="deflate() (levels 4-9) vs deflate_fast() (levels 1-3)", status="ACCEPTED",
    mechanism="at each position find the best match but do not emit it; advance one byte and search again; if the new match is not longer, emit the PREVIOUS match (prev_length, prev_match) and skip over it inserting hash entries; else emit the byte before as a literal and keep looking; a 3-byte match too far back (TOO_FAR) is demoted to a literal; deflate_fast emits greedily without the deferral",
    input="positions, matches", output="a sequence of (length, distance) pairs and literals via ct_tally", state="prev_length, prev_match, match_available", update="per byte", assumptions=["max_lazy_match bounds when lazy search is skipped (a long enough match is taken at once)"],
    fitness_value_in_ancestor="a few percent of ratio for a roughly doubled search cost (by the table, not measured)", evidence_ref=S + "deflate.c:661-763,580-660", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="deflate() / deflate_fast()",
    coverage={"input_topology": "STREAM", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "memory": "LAST_VALUE", "temporal_horizon": "STEP"})

cf = c.organ("four_threshold_table_indexed_by_level", parent=lz, human_name="configuration_table[10]: good, lazy, nice, chain", status="ACCEPTED",
    mechanism="level 0 stores; 1-3 use deflate_fast with (lazy reinterpreted); 4-9 set good_match (when to quarter the chain), max_lazy_match, nice_match (stop searching), max_chain_length; no other code changes with the level",
    input="pack_level", output="four thresholds", state="none", update="once", evidence_ref=S + "deflate.c:199-245,286-356", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="configuration_table + lm_init",
    coverage={"input_topology": "SCALAR", "output_topology": "VECTOR", "state_amount": "NONE", "adaptation": "PARAMETER"})

sw = c.organ("sliding_window_by_halving_copy_with_hash_chain_rebasing", human_name="fill_window", status="ACCEPTED",
    mechanism="the window is 2 * WSIZE; when strstart passes WSIZE + MAX_DIST the upper half is copied down, every position variable is decremented by WSIZE, and both hash arrays are rebased (entries below WSIZE become NIL); then more input is read into the free space; MIN_LOOKAHEAD is kept ahead of strstart",
    input="the input stream", output="a refilled window", state="window[2*WSIZE], lookahead, eofile", update="when lookahead runs low", evidence_ref=S + "deflate.c:516-579", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="fill_window",
    coverage={"input_topology": "STREAM", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "memory": "WINDOW", "resource_dependence": "MEMORY"})

hf = c.organ("per_block_huffman_trees_from_tallied_frequencies_with_a_static_fallback_and_a_length_limit", human_name="trees.c: ct_tally / build_tree / gen_bitlen / gen_codes / flush_block", status="ACCEPTED",
    mechanism="ct_tally records each literal or (length, distance) into buffers and frequency counts (dyn_ltree, dyn_dtree); at block end build_tree makes a Huffman tree with a heap, gen_bitlen limits code lengths to MAX_BITS by overflow correction, gen_codes assigns canonical codes; a third tree (bl_tree) encodes the code lengths themselves; the block is emitted with whichever is shorter: dynamic trees, the fixed static trees, or stored; lengths and distances are split into a code plus extra bits (extra_lbits / extra_dbits)",
    input="ct_tally events", output="a compressed block", state="the trees, the literal/distance buffers, flag bits", update="per block (flush when the buffer fills, ct_tally's return)", assumptions=["code lengths <= 15 (the DEFLATE format)"],
    evidence_ref=S + "trees.c:94-274 (state) and function index; deflate.c ct_tally / FLUSH_BLOCK call sites", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="trees.c",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "memory": "SUMMARY_STATISTIC", "update_topology": "SWEEP"})

inf = c.organ("table_driven_decoding_with_two_level_huffman_lookup", human_name="inflate.c: huft_build / inflate_codes / inflate_dynamic / inflate_fixed / inflate_stored", status="CANDIDATE",
    mechanism="huft_build turns code lengths into lookup tables of lbits/dbits (9/6) bits with sub-tables for longer codes; inflate_codes reads symbols through them and copies from the sliding output window for matches (by index and signatures only)", input="a compressed stream", output="bytes", state="the tables, the output window",
    evidence_ref=S + "inflate.c:132-280", confidence="LOW", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="inflate.c",
    coverage={"input_topology": "STREAM", "output_topology": "STREAM", "state_amount": "CONSTANT", "memory": "WINDOW"})

c.reject("'gzip' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the matcher, the lazy policy, the window and the entropy coder are separate files with separate state; zlib later kept them separable")
c.reject("unlzw.c / unpack.c / unlzh.c (decoders for compress, pack, lzh formats)", reason="OTHER", evidence="by name: compatibility decoders for rival formats, not gzip's own machinery", note="the ancestry (compress LZW) is preserved as a DECODER inside its successor -- an archaeological observation")
c.reject("gzip.c (driver, file handling, options), bits.c (bit output), util.c, crypt/zip headers", reason="GENERIC_LANGUAGE_MECHANICS", evidence="by name and size; bits.c is a bit buffer")
c.reject("the -1..-9 levels as nine organs", reason="OTHER", evidence=S + "deflate.c:225-245 -- a table of four numbers; no mechanism differs except fast vs lazy at level 3/4")

c.edge(sw, hc, "feeds", note="bytes; rebasing"); c.edge(hc, lm, "feeds", note="hash_head"); c.edge(lm, lz, "feeds"); c.edge(cf, lm, "updates", note="chain, nice, good"); c.edge(cf, lz, "updates", note="lazy"); c.edge(lz, hf, "feeds", note="ct_tally"); c.edge(hf, lz, "triggers", note="flush when the buffer fills")
c.edge(hf, inf, "feeds", note="the format; inverse"); c.edge(lz, hc, "updates", note="inserts skipped positions")

c.pressure("repeated_substrings_in_a_stream_must_be_found_in_bounded_memory_and_time_per_byte",
    condition="redundancy is mostly local repeats of short strings; the encoder may look back a bounded distance and spend bounded work per byte; ratio and speed trade against each other", resource_or_constraint="32 KB window; a chain-length budget; 1993 memory",
    failure_condition="too slow to be usable, or a ratio no better than compress", world_punishes="exhaustive search; unbounded memory", world_rewards="hashing to candidates, bounded chain walks, and a one-byte deferral that recovers most of the greedy loss",
    observable_consequence="ratio vs time across the level table (the record's entry point)", vacuity_condition="incompressible input", trivial_shortcuts="store only (level 0)",
    cheat_control="an encoder given the optimal parse must beat level 9's ratio; if the world scores it equal, ratio resolution is too coarse", cost_class="CPU-scale", source_evidence="the configuration table; record pressure", purpose="PURPOSE: a compressor free of the LZW patent")
c.pressure("a_file_format_once_published_can_never_change",
    condition="every archive ever written must decode forever; the encoder may improve, the bitstream may not", resource_or_constraint="backward compatibility",
    failure_condition="orphaned archives (record)", world_punishes="format changes", world_rewards="a format whose flexibility (dynamic trees, stored blocks) lets encoders improve without touching the decoder",
    observable_consequence="1993 archives decoded by 2025 decoders", vacuity_condition="short-lived data", trivial_shortcuts="none",
    cheat_control="N/A", cost_class="CPU-scale", source_evidence="record failure condition; the three block types", purpose="PURPOSE: same")
c.pressure("a_patent_on_the_rival_algorithm_forbids_the_obvious_design",
    condition="LZW (compress) is encumbered; the design must avoid its mechanism while beating it", resource_or_constraint="legal",
    failure_condition="distribution stopped (record)", world_punishes="dictionary-based LZW", world_rewards="LZ77 pointer-based matching plus Huffman coding",
    observable_consequence="the existence of unlzw.c beside deflate.c: decode the rival, never encode it", vacuity_condition="no patent", trivial_shortcuts="none",
    cheat_control="N/A", cost_class="CPU-scale", source_evidence="record pressure; file list", purpose="PURPOSE: same")

c.ancestry("superseded", "ncompress-5.0-lzw-1985", note="Techne records this edge with direction 'gzip displaced compress'; the atlas keeps it as recorded")
c.residue("PARTIALLY_EXPLAINED", ["trees.c read as state and index, not line by line", "inflate.c CANDIDATE from signatures", "the -1..-9 ablation is a ready Stage C experiment on Techne's container: ratio/time per level with the table as the only variable"],
          note="deflate.c is fully read")
c.save(state="COARSE")
