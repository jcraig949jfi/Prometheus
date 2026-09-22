"""Cut: eliza-anthay-1966 (ancestry-aware, Stage A COARSE; SOURCE_READ src/eliza.cpp 3369-3490 (eliza::response in full), 2403-2440 (the
reconstructed SLIP mid-square hash), 2798-2900 (rule_memory, grepped), class index; the matcher (1081-1340), reassembly (2120-2200),
the script reader (3930+) and the 1966 DOCTOR script (embedded) read by index only). Anthony Hay's C++ reconstruction of Weizenbaum's
1966 ELIZA from the recovered MAD-SLIP source; 12,324 lines including tests and the CACM conversation."""
from nyx.atlas.author import Cut

S = "vault:eliza-anthay-1966/upstream/tree/src/eliza.cpp"
c = Cut("eliza-anthay-1966", mode="ANCESTRY_AWARE", inspected=["src/eliza.cpp response() 3369-3490", "hash() 2403-2440", "rule_memory 2798-2900", "class index"],
        evidence=[("SOURCE_READ", S)],
        note="a reconstruction faithful enough to reproduce the CACM 1966 dialogue including the memory-recall quirk (LIMIT == 4) and the 7094 sign-magnitude hash; the anatomy below is Weizenbaum's, with the reconstructor's page references preserved in the code")

ks = c.organ("keyword_scan_with_precedence_ordered_keystack_and_subclause_cut_at_delimiters", human_name="eliza::response first loop [CACM page 39]", status="ACCEPTED",
    mechanism="uppercase and split the input; walk the words: at a delimiter (comma/period), discard the text so far if no keyword was found yet, else cut the text there; for each word that is a script keyword, push it to the FRONT of the keystack if its precedence exceeds the best so far, else to the back; apply the keyword's word substitution in place (I -> YOU, MY -> YOUR); LIMIT cycles 1..4 per turn",
    input="a line of text", output="a trimmed word list and an ordered keystack", state="limit_ (1..4 counter)", update="per turn", assumptions=["the script's precedences encode which keyword should be answered first"],
    evidence_ref=S + ":3369-3410", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the first loop of response()",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "memory": "NONE", "order_sensitivity": "SENSITIVE", "update_topology": "SWEEP"})

dr = c.organ("decomposition_pattern_match_with_wildcards_and_tag_classes_then_reassembly_by_index", human_name="rule_keyword::apply_transformation -> match() / reassemble() [pages 39-40]", status="ACCEPTED",
    mechanism="a keyword's rule holds decomposition patterns (a sequence of literal words, integers meaning 'any n words' (0 = any number), and (/TAG) class references resolved through the DLIST tags); match() binds the pattern to the words into components; the rule's reassembly rules (cycled in turn per decomposition) name components by index to build the reply; a rule may instead say NEWKEY (drop this keyword) or link to another keyword (= OTHERKEY)",
    input="words, a keyword rule, the tag map", output="a reply, or an action (linkkey / newkey / inapplicable)", state="per-rule cursor over reassembly rules (round robin)", update="per application",
    fitness_value_in_ancestor="the entire 'understanding'; the record's failure condition is a pattern that does not cover the turn", evidence_ref=S + ":1081-1340 (match family, index), 2120-2200 (reassemble), 2900-3050 (rule_keyword)", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="match / xmatch / reassemble / rule_keyword",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "memory": "LAST_VALUE", "representation_sensitivity": "SENSITIVE"})

mem = c.organ("memory_queue_filled_on_a_keyword_and_recalled_only_when_a_counter_reads_four", human_name="rule_memory [page 41 (f)]; the LIMIT quirk", status="ACCEPTED",
    mechanism="whenever the MEMORY keyword (MY) is applied, a transformed version of the sentence is pushed on a FIFO, the transformation chosen by the mid-square hash of the last word's BCD encoding (4 alternatives); when a later input has NO keyword and LIMIT == 4 and the queue is non-empty, the oldest memory is popped and returned ('Does that have anything to do with the fact that your ...')",
    input="keyworded sentences; keyword-free turns", output="a delayed reply", state="memories_ (FIFO), limit_", update="per turn", assumptions=["the 1966 code's 'certain counting mechanism' is exactly LIMIT == 4 -- the reconstructor's finding from the recovered source"],
    fitness_value_in_ancestor="the only cross-turn state; what made ELIZA seem to remember", evidence_ref=S + ":2798-2900,3411-3420", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="rule_memory + the keystack.empty() branch",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "memory": "WINDOW", "temporal_horizon": "EPISODE", "stochasticity": "DETERMINISTIC"})

hs = c.organ("mid_square_hash_of_a_35_bit_sign_magnitude_word", human_name="SLIP HASH (FAP) reconstruction", status="ACCEPTED",
    mechanism="mask to 35 bits, square, take the middle n bits of the 70-bit product (n = 2 for the memory choice); the 7094's sign-magnitude representation is reproduced so the same word hashes to the same 1966 bucket",
    input="a 6-character BCD word", output="n bits", state="none", update="none", assumptions=["the reconstruction of the FAP code is right (tests compare against known 1966 outputs)"],
    fitness_value_in_ancestor="decides which of 4 memory transformations fires; part of why the CACM dialogue is reproduced exactly", evidence_ref=S + ":2403-2440", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="hash()",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "NONE", "representation_sensitivity": "SENSITIVE"})

nm = c.organ("no_match_fallbacks_cycled_by_the_same_counter", human_name="nomatch_msgs_[limit_ - 1] / NONE rule", status="ACCEPTED",
    mechanism="when no keyword applies and no memory is due, one of four canned deflections indexed by LIMIT is returned (or the script's NONE rule); the same counter thus governs both deflection variety and memory timing",
    input="a keyword-free turn", output="a deflection", state="limit_", update="per turn", evidence_ref=S + ":3372-3374,3434-3470", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the nomatch branches",
    coverage={"input_topology": "EVENT", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "memory": "LAST_VALUE"})

sc = c.organ("script_as_data_with_keywords_precedences_substitutions_tags_and_rules", human_name="elizascript reader / the DOCTOR script (embedded)", status="CANDIDATE",
    mechanism="an S-expression script defines every keyword, its precedence, substitution, decomposition/reassembly rules, DLIST tag classes and the MEMORY rule; the engine has no English in it (the record: swap the script, change the personality) -- reader read by index", input="script text", output="rulemap, tagmap", state="none",
    evidence_ref=S + ":3778-4860 (tokenizer, eliza_script_reader; index)", confidence="LOW", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="elizascript namespace",
    coverage={"input_topology": "TREE", "output_topology": "SET", "state_amount": "NONE"})

c.reject("the micro test library, tracers, Hollerith/BCD conversion tables, serial I/O for a period terminal", reason="GENERIC_LANGUAGE_MECHANICS", evidence=S + ":108-160 (tests), 3148-3320 (tracers), 305-330 (hollerith); posix/win_serial_io.cpp", note="the tracers are the reconstructor's instrument; BCD encoding is needed by the hash organ and recorded there")
c.reject("'ELIZA' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the engine is five mechanisms and the script is data; the record's entry point relies on that split")
c.reject("the DOCTOR script's content as machinery", reason="EFFECT_FROM_ENVIRONMENT", evidence="the script is the WORLD the engine runs in; its rules are data", note="a second script would be a second world for the same organs")

c.edge(sc, ks, "feeds"); c.edge(sc, dr, "feeds"); c.edge(ks, dr, "feeds", note="keystack order"); c.edge(dr, mem, "stores", note="MY -> create_memory"); c.edge(hs, mem, "selects", note="which transformation"); c.edge(ks, mem, "gates", note="empty keystack + LIMIT == 4")
c.edge(ks, nm, "gates"); c.edge(dr, ks, "updates", note="linkkey pushes a new keyword"); c.edge(mem, nm, "competes", note="both answer a keyword-free turn")

c.pressure("a_believable_reply_must_come_from_surface_transformation_alone_with_no_model_of_meaning",
    condition="the machine has a word list and patterns; the human supplies all meaning; the reply must reflect the input back in a form that invites the next turn", resource_or_constraint="1966 memory (a few hundred rules); no parsing beyond keywords",
    failure_condition="a turn no rule covers -> canned deflection; the illusion breaks (record)", world_punishes="rules that do not cover the input distribution", world_rewards="reflection (pronoun swap + echo), a precedence that answers the most specific keyword, and a delayed memory that simulates continuity",
    observable_consequence="the CACM 1966 conversation reproduced exactly (the record's oracle); the rate of fallback replies on new inputs", vacuity_condition="a cooperative human who only uses scripted keywords", trivial_shortcuts="a fixed list of open questions (no reflection; a world that measures only turn-taking rewards it)",
    cheat_control="an engine that echoes the input verbatim with pronouns swapped must score below the scripted one on any measure of believability; if the world cannot tell them apart, it measures echo, not the script", cost_class="CPU-scale", source_evidence="record pressure / failure; response()", purpose="PURPOSE: demonstrate (and, per Weizenbaum, debunk) natural-language understanding")

c.ancestry("reimplementation_of", "Weizenbaum's MAD-SLIP ELIZA (1966), from the source recovered in 2021 (the reconstructor's README, not read here)", note="human prior")
c.residue("PARTIALLY_EXPLAINED", ["the matcher and the script reader read by index only", "the embedded DOCTOR script not read", "nothing ran here; Techne's CACM-line oracle is on M1"],
          note="the response algorithm is read line by line; five mechanisms account for it")
c.save(state="COARSE")
