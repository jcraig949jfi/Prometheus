"""Cut: whitakers-words-ada (Whitaker's Words, Latin morphological analyser; ancestry-aware, Stage A COARSE; SOURCE_READ on M3;
position 34 of the 2026-09-17 NOT_CUT order). Read: src/words_engine/words_engine-word_package.adb Run_Inflections 205-305, Word
603-690 (Order_Stems), Reduce_Stem_List 736-870, Prune_Stems 1298-1378; words_engine-parse.adb Pass 642-695; words_engine-tricks.adb
Syncope 56-250 (structure). NOT read: the dictionary loading and the PDL construction (Dictionary_Search 320-505), Apply_Prefix /
Apply_Suffix bodies, Try_Tackons / Process_Packons / enclitics, the English side, the data files (DICTLINE.GEN 39,335 lines,
INFLECTS.LAT 3,228). Nothing ran (Ada; no compiler on M3).
"""
from nyx.atlas.author import Cut

W = "vault:whitakers-words-ada/upstream/tree/src/words_engine/words_engine-word_package.adb"; P = "vault:whitakers-words-ada/upstream/tree/src/words_engine/words_engine-parse.adb"; T = "vault:whitakers-words-ada/upstream/tree/src/words_engine/words_engine-tricks.adb"
c = Cut("whitakers-words-ada", mode="ANCESTRY_AWARE", inspected=["word_package.adb 205-305, 603-690, 736-870, 1298-1378", "parse.adb 642-695", "tricks.adb 56-250"],
        evidence=[("SOURCE_READ", W + ":205-305"), ("SOURCE_READ", W + ":603-690"), ("SOURCE_READ", W + ":736-870"), ("SOURCE_READ", W + ":1298-1378"), ("SOURCE_READ", P + ":642-695"), ("SOURCE_READ", T + ":56-250")],
        note="analysis by generate-and-test over the word's suffixes: every ending of length Z that matches the word's tail proposes a (stem, inflection) pair; the stems are looked up in a dictionary indexed by first letters; a surviving pair must agree between the inflection's part/declension/key and the dictionary entry's; failures fall through a fixed ladder of repairs (syncope, enclitics, prefixes, suffixes, orthographic 'tricks') each of which re-runs the same core")

infl = c.organ("all_suffix_splits_of_the_word_tried_against_an_inflection_table_partitioned_by_ending_length_and_last_letter", human_name="Run_Inflections (205-305): Lelf/Lell index by (Z, last letter); the blank-ending pass; Sa(stem_length)", status="ACCEPTED",
    mechanism="the inflection table is read in one of four sections chosen by the word's last letter; for each ending length Z from the maximum down to 1, the endings indexed by (Z, last letter) are compared with the word's last Z characters; each match yields a parse record (stem = word minus Z, the inflection record) and marks stem length Z as possible; the blank ending is always added first for words within the stem-size limit",
    input="a lower-cased word", output="a list of (stem, inflection) candidates and the set of possible stem lengths", state="none beyond the loaded table", update="per word", assumptions=["Latin inflection is suffixal (prefixes are handled separately as 'fixes'); the table indexed by (length, last letter) makes the trial cheap"],
    fitness_value_in_ancestor="every morphologically possible split is enumerated without a grammar", failure_landscape="by reading: no ranking here; the ambiguity is resolved later by dictionary agreement and a sort", human_prior="finite-state morphology (Koskenniemi 1983) is the contemporaneous alternative; Whitaker's is table-driven generate-and-test",
    evidence_ref=W + ":205-305", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="Run_Inflections",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SET", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP"})

agree = c.organ("candidate_survives_only_if_the_inflection_and_the_dictionary_entry_agree_in_part_of_speech_declension_and_stem_key_with_prefix_suffix_transformation_of_the_entry", human_name="Reduce_Stem_List (736-870): the three '<=' agreement operators; the suffix/prefix root and target checks", status="ACCEPTED",
    mechanism="for each reduced-dictionary entry (PDL) and each candidate: if a suffix is in play the entry's part must be compatible with the suffix's root part and key, and the entry is transformed to the suffix's target part; a prefix must match the (possibly transformed) part or be universal; then the candidate's inflection must agree with the entry under partial-order operators: part (Pack <= Pron; X matches all), gender (C matches non-neuter; X all), stem key (0 matches all); survivors carry the dictionary entry's MNPC id",
    input="candidates; the reduced dictionary list", output="agreed parse records", state="none", update="per word", assumptions=["morphological agreement is a lattice with wildcards (X, C, key 0), not equality; affixes change the entry's category before agreement"],
    fitness_value_in_ancestor="one agreement pass filters the generate-and-test explosion; wildcards let the dictionary be underspecified", failure_landscape="by reading: the operators are hand-written per field; a new category means a new operator",
    evidence_ref=W + ":736-870", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="Reduce_Stem_List",
    coverage={"input_topology": "SET", "output_topology": "SET", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "representation_sensitivity": "SENSITIVE"})

ladder = c.organ("fixed_ladder_of_repairs_each_re_running_the_core_analysis_and_stopping_at_the_first_that_yields_a_parse", human_name="Pass (parse.adb 642-695): Roman numerals -> Word -> Try_Slury -> Perform_Syncope -> Enclitic -> (fixes on) Word -> Syncope -> Enclitic; Prune_Stems (1298-1378): Search_Dictionaries -> Apply_Prefix -> Apply_Suffix -> Apply_Prefix; Syncope (tricks.adb): -avi- -> -a-, -ivi- -> -i-, -sis/-xis-, each 'Exit loop here if SYNCOPE found hit'",
    status="ACCEPTED",
    mechanism="the plain analysis runs first with prefix/suffix fixes disabled; if it yields nothing, a sequence of rewrites of the input word (syncopated perfects, enclitic stripping -que/-ne/-ve, orthographic flips) each re-run the same Word core and stop at the first hit, restoring Pa_Last on failure; only then are prefixes and suffixes enabled and the core re-run; the order encodes the author's judgment of prior probability ('There may be a valid simple parse, if so it is most probable')",
    input="a word", output="the first non-empty parse set along the ladder", state="Pa_Last (the parse array's high-water mark) as the success signal", update="per word", assumptions=["earlier rungs are more probable readings than later ones; a hit at any rung ends the search (no scoring across rungs)"],
    fitness_value_in_ancestor="rare phenomena are handled without contaminating the common case; the core is reused rather than generalised", failure_landscape="by reading: a word with a rare true reading and a spurious common one returns the spurious one; the author's comments say as much ('This sort is very sloppy', 'the following condition is absurd')",
    human_prior="backoff by ordered rewrites (as in early spell correction)", evidence_ref=P + ":642-695; " + W + ":1298-1378; " + T + ":56-250", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="Pass, Prune_Stems, Syncope",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SET", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC", "update_topology": "PRIORITY", "order_sensitivity": "SENSITIVE"})

c.reject("Order_Stems (610-687): a bubble sort of 1-5 records by MNPC, ending size, quality, dictionary kind", reason="BELOW_MEANINGFUL_GRAIN", evidence=W + ":610-687", note="a preference order, not a mechanism; the author calls it 'very sloppy'")
c.reject("Dictionary_Search / Load_Pdl (320-505): the first-two-letters index into DICTLINE", reason="OTHER", evidence="NOT READ in full; residue", note="the index is the run-time cost centre")
c.reject("Apply_Prefix / Apply_Suffix bodies, Try_Tackons, Process_Packons, Process_Qu_Pronouns, the enclitic tables, the English-to-Latin side, list_package (output), the data files", reason="OTHER", evidence="NOT READ; residue")
c.reject("'Latin parser' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="enumeration, agreement and the repair ladder are three separable steps; the data files are a fourth thing")

c.edge(infl, agree, "feeds"); c.edge(ladder, infl, "feeds", note="each rung re-runs the core"); c.edge(agree, ladder, "gates", note="Pa_Last > 0 stops the ladder")

c.pressure("a_string_from_an_inflecting_language_must_be_mapped_to_lexicon_entries_plus_grammatical_features_when_most_splits_are_spurious_and_rare_phenomena_must_not_swamp_common_ones",
    condition="an organism receives a word form; a lexicon of stems and a table of endings exist; the true analysis is one of many string-compatible splits; a small fraction of words need rewrites (syncope, enclitics, affixes)", resource_or_constraint="lexicon lookups per word; a fixed table",
    failure_condition="the true analysis missing from the output, or the output dominated by spurious splits", world_punishes="accepting every split; running every repair on every word (spurious hits)", world_rewards="agreement filtering with wildcards; ordered backoff",
    observable_consequence="precision and recall of analyses against a hand-tagged corpus (the body ships expected outputs for the Aeneid: test/10_aeneid/expected.txt) with the repair ladder enabled, disabled and reordered", vacuity_condition="an uninflected language", trivial_shortcuts="a full-form lexicon",
    cheat_control="an organism given the gold split must reach 100 percent; the ladder reordered (fixes first) must lower precision on the corpus; the ladder disabled must lower recall: the world must show the two failures in opposite directions",
    cost_class="CPU-scale", source_evidence="Run_Inflections; Reduce_Stem_List; Pass; test/10_aeneid/expected.txt", purpose="PURPOSE: Latin morphological analysis (Whitaker 1993-2010)")

c.ancestry("algorithm_from", "Whitaker's own design (1993-); the Ada 2012 port and test corpus by the mk270 maintainers", note="from the README and the record")
c.residue("LARGE_RESIDUE", ["dictionary indexing, affix application, tackons/packons, enclitics and the English side unread", "the data files (the lexicon) are half the program and unread", "nothing ran"], note="the three control mechanisms of the analyser are located; the test corpus is an oracle a Stage C run could use once an Ada compiler exists")
c.save(state="COARSE")
