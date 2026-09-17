"""Cut: compress-4.2.4-lzw (ncompress 4.2.4.6, compress42.c 1,928 lines; ancestry-aware, Stage A COARSE; SOURCE_READ on M3; twelfth of
the 2026-09-17 NOT_CUT order). Read: compress() 1341-1530 (the encoder core: hash table, code-width growth, block-mode ratio check and
CLEAR), the #defines 238-382. NOT read: decompress() 1594-1820 (the mirror), the file/directory drivers 707-1340, the FAST hash variant
beyond its first lines. Nothing ran (needs a C compiler; not on M3).
"""
from nyx.atlas.author import Cut

C = "vault:compress-4.2.4-lzw/upstream/tree/ncompress-4.2.4.6/compress42.c"
c = Cut("compress-4.2.4-lzw", mode="ANCESTRY_AWARE", inspected=["compress42.c 238-382 (defines), 1341-1530 (compress())"], evidence=[("SOURCE_READ", C + ":1341-1530"), ("SOURCE_READ", C + ":238-382")],
        note="LZW as shipped in Unix compress: a dictionary that is never stored, only re-derived; codes that widen as the dictionary fills; and a block-mode heuristic that throws the dictionary away when the compression ratio starts falling")

dict_ = c.organ("implicit_dictionary_as_prefix_code_plus_byte_keyed_by_hashing_never_transmitted", human_name="fcode = (byte << BITS-8) ^ ent; htab / codetab; free_ent from FIRST=257 (compress() 1440-1530)", status="ACCEPTED",
    mechanism="the current string is represented by its dictionary code ent; each new byte c forms the key (c, ent); if the pair is in the hash table its code becomes the new ent (the string grows), else the code for ent is emitted, the pair is entered at the next free code, and ent restarts at c; "
              "the decoder rebuilds the same table from the code stream, so the dictionary is never sent; the table is open-addressed with a secondary hash (disp = HSIZE - hp - 1, after G. Knott)",
    input="bytes", output="codes of n_bits each", state="htab (hash of pair -> code), free_ent", update="per byte", assumptions=["the decoder will see codes in the same order and can reconstruct each entry one step behind the encoder (the KwKwK case is the decoder's to handle)"],
    fitness_value_in_ancestor="one pass, no model transmitted, adaptive to any byte statistics", failure_landscape="UNKNOWN by run", human_prior="Welch 1984 (LZW); the hash-with-secondary-probe is the 4.x BSD implementers'",
    evidence_ref=C + ":1440-1530", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the hfound/next/next2 loop and the hash probe",
    coverage={"input_topology": "STREAM", "output_topology": "STREAM", "state_amount": "SUPERLINEAR", "state_persistence": "PER_EPISODE", "memory": "ARCHIVE", "stochasticity": "DETERMINISTIC", "update_topology": "SINGLE_STEP"})

width = c.organ("code_width_grows_from_9_bits_as_the_dictionary_fills_up_to_maxbits_then_freezes", human_name="n_bits / extcode / MAXCODE / INIT_BITS (1362-1379, 1394-1410)", status="ACCEPTED",
    mechanism="codes start 9 bits wide (INIT_BITS); when free_ent reaches 2^n_bits the width increments (the output bit position is realigned to a code boundary, boff) up to maxbits (default 16); at maxbits the table is frozen (stcode = 0) and no new entries are added until a CLEAR",
    input="free_ent", output="n_bits; a realignment", state="n_bits, extcode, boff", update="on each table-size threshold", assumptions=["the decoder increments its width at the same free_ent counts (the alignment is part of the format, including the padding to a code boundary at each width change)"],
    fitness_value_in_ancestor="short codes early, wide codes only when the dictionary is large", failure_landscape="by reading: the boff realignment is the source of the classic 'compress' format incompatibilities between versions", evidence_ref=C + ":1362-1379, 1394-1410", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the if (free_ent >= extcode ...) block",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC", "adaptation": "PARAMETER"})

clear = c.organ("block_mode_dictionary_reset_when_the_compression_ratio_stops_improving", human_name="CHECK_GAP / ratio / checkpoint / CLEAR (1411-1440)", status="ACCEPTED",
    mechanism="once the table is full (stcode = 0), every CHECK_GAP = 10000 input bytes the running ratio bytes_in/bytes_out (8 fractional bits) is compared with the best seen; if it improved the best is updated; if it FELL, the table is cleared, a CLEAR code (256) is emitted, the width returns to 9 bits and the dictionary starts over; the check itself is only made at string boundaries (ent < FIRST)",
    input="bytes_in, bytes_out", output="a CLEAR code and a fresh table, or nothing", state="ratio (best), checkpoint", update="per CHECK_GAP bytes once full",
    assumptions=["a falling ratio means the frozen dictionary no longer fits the data (the input statistics drifted); restarting costs a few thousand bytes of poor compression and pays back if the drift is real"],
    fitness_value_in_ancestor="adaptivity restored after the dictionary freezes; the only feedback loop in the coder", failure_landscape="by reading: a ratio that oscillates around the best value triggers resets on every dip (no hysteresis beyond 'best so far'); the reset costs the whole dictionary, never part of it",
    human_prior="block mode (the 0x80 flag in the header byte) was added to compress 4.0 by the Unix community; the 10000-byte gap is tuning", evidence_ref=C + ":365, 1411-1440", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the if (!stcode && bytes_in >= checkpoint ...) block",
    coverage={"input_topology": "SCALAR", "output_topology": "DECISION", "state_amount": "CONSTANT", "state_persistence": "PER_EPISODE", "feedback": "CLOSED_LOOP", "memory": "LAST_VALUE", "stochasticity": "DETERMINISTIC", "adaptation": "STRUCTURE", "recovery": "SELF_RESETS", "failure_mode": "OSCILLATES"})

c.reject("decompress() and the KwKwK special case", reason="OTHER", evidence="NOT READ (1594-1820); the decoder's table rebuild is the mirror of the encoder organ; residue", note="a second pass reads it for the one asymmetric case")
c.reject("main(), comprexx(), compdir() (file handling, recursion into directories, the magic bytes, signal handling), the FAST hash variant", reason="GENERIC_LANGUAGE_MECHANICS", evidence=C + ":707-1340; the #ifdef FAST branch", note="drivers and a performance variant of the same probe")
c.reject("'LZW' / 'compress' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the implicit dictionary, the code widening and the ratio reset are separately replaceable; gzip (in the vault) keeps none of them and beats it -- the record's superseded-design tag")

c.edge(dict_, width, "triggers", note="free_ent"); c.edge(width, dict_, "gates", note="freeze at maxbits"); c.edge(clear, dict_, "restores", note="clear_htab"); c.edge(clear, width, "restores", note="back to 9 bits"); c.edge(dict_, clear, "feeds", note="bytes_in/bytes_out")

c.pressure("a_model_that_can_only_grow_must_be_discarded_wholesale_when_the_source_drifts_and_the_only_signal_is_its_own_recent_performance",
    condition="an organism builds a dictionary from what it has seen; once full it cannot change; the source's statistics may drift; the organism sees only its own compression ratio, in chunks", resource_or_constraint="a full dictionary is frozen; a reset costs the dictionary and a restart",
    failure_condition="keeping a stale dictionary (ratio decays) or resetting on noise (ratio never recovers)", world_punishes="both", world_rewards="a reset rule that fires on real drift and not on noise", observable_consequence="compressed size on a source that changes statistics at a known point vs a stationary source, with the reset enabled and disabled",
    vacuity_condition="a stationary source or an unbounded dictionary", trivial_shortcuts="a world that announces the drift", cheat_control="an organism told the drift point must reset exactly there and beat the ancestor; the ancestor with block mode off must show the decay after the drift: the world must show both",
    cost_class="CPU-scale", source_evidence="compress42.c 1411-1440; record tags dictionary-coding / lzw", purpose="PURPOSE: adaptive dictionary compression with reset (Unix compress 4.x)")

c.ancestry("algorithm_from", "Welch 1984 (LZW) on Lempel-Ziv 1978; Unix compress by Spencer Thomas, Jim McKie, Steve Davies, Ken Turkowski, James Woods, Joe Orost (the file's header)", note="from the source header; record lineage not re-read")
c.residue("PARTIALLY_EXPLAINED", ["decompress() not read", "the FAST hash variant read only to its first probe", "nothing ran"], note="the encoder's three mechanisms are accounted for; the vault's ncompress-5.0 and gzip fossils are recurrence/supersession neighbours")
c.save(state="COARSE")
