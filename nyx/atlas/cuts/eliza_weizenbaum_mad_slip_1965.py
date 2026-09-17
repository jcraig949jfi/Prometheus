"""Cut: eliza-weizenbaum-mad-slip-1965 (the 1965 MAD-SLIP source of ELIZA as transcribed from Weizenbaum's listing, plus a modernised
translation and the 1966 CACM DOCTOR script; ancestry-aware, Stage A COARSE; SOURCE_READ on M3; sixteenth of the 2026-09-17 NOT_CUT
order). Read: MAD-SLIP_translation.txt in full (the CHANGE editor 1-100, TPRINT, the script reader and MAIN LOOP 236-445); the
annotated transcription's header. Not read: the CACM script text itself (data), the SLIP library (YMATCH/ASSMBL are external
functions whose code is NOT in the body -- the translation points at the SLIP manual). Nothing ran (SOURCE_ONLY; MAD on a 7094).
The body is a transcription of a listing (LATER_TRANSCRIPTION class); the vault also holds eliza-anthay-1966 (C++, cut 09-16) and
cosell-eliza-bbn-lisp-1969 (NOT_CUT) -- recurrence candidates.
"""
from nyx.atlas.author import Cut

T = "vault:eliza-weizenbaum-mad-slip-1965/upstream/MAD-SLIP_translation.txt"
c = Cut("eliza-weizenbaum-mad-slip-1965", mode="ANCESTRY_AWARE", inspected=["MAD-SLIP_translation.txt (all); ELIZA_transcription_annotated.txt (header)"],
        evidence=[("SOURCE_READ", T + ":236-445"), ("SOURCE_READ", T + ":1-100"), ("SOURCE_READ", "vault:eliza-weizenbaum-mad-slip-1965/upstream/ELIZA_transcription_annotated.txt:1-60")],
        note="the 1965 program is a script interpreter: keywords hashed into 32 buckets with a precedence number; a scan that keeps the highest-precedence keyword found before a clause break; decomposition/reassembly rules applied by two SLIP library functions; a four-slot MEMORY that queues a transformed earlier sentence for use when nothing matches; and a live script editor")

kw = c.organ("keyword_dictionary_hashed_into_32_buckets_with_per_keyword_precedence_and_substitution", human_name="KEY(HASH.(word,5)); the script reader BEGIN; the scan NOTYET-KEYFND (236-330)", status="ACCEPTED",
    mechanism="each script entry is a list headed by a keyword, hashed on 5 bits into KEY(0..31); KEY(32) holds the NONE rules; the scan walks the input words, hashes each, searches its bucket for the keyword, and TESTS the entry: a substitution word (DL) may replace the input word in place (NEWTOP), and an optional precedence number ranks the keyword; the highest precedence seen so far becomes IT/KEYWRD",
    input="the input word list; the script lists", output="the selected keyword's rule list and the substituted input", state="KEY(0..32) (the script); IT, KEYWRD, PREDNC per sentence", update="per word",
    assumptions=["a 5-bit hash and linear bucket search suffice for a script of a few hundred keywords; precedence is a small integer set by the script author"], fitness_value_in_ancestor="the program is data-driven: the DOCTOR persona is entirely in the script", failure_landscape="UNKNOWN by run",
    human_prior="keyword precedence (the 'rank' in the 1966 paper) is Weizenbaum's mechanism for deciding which of several keywords wins", evidence_ref=T + ":236-330", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="BEGIN through PLCKEY",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SCALAR", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP", "order_sensitivity": "SENSITIVE"})

clause = c.organ("clause_break_at_punctuation_or_BUT_keeping_the_side_that_holds_the_keyword", human_name="the '.' ',' 'BUT' test in the scan (NULSTL / NULSTR)", status="ACCEPTED",
    mechanism="when a period, comma or BUT is met: if no keyword has been found yet, the words before it are discarded (NULSTL) and scanning continues; if one has, the words after it are discarded (NULSTR) and the scan ends -- so the sentence is truncated to the clause containing the winning keyword",
    input="the word stream and the keyword-found flag", output="a truncated input list", state="IT", update="per punctuation", assumptions=["one clause holds the topic; the rest is noise for pattern matching"], fitness_value_in_ancestor="decomposition patterns need only match a clause, not a whole sentence",
    failure_landscape="by reading: a keyword after the first comma in a keyword-less first clause is kept, one before a comma after a found keyword is lost -- the rule is asymmetric by design", evidence_ref=T + ":the WORD = '.' block", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the punctuation test inside NOTYET",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC"})

decomp = c.organ("decomposition_and_reassembly_by_library_pattern_match_with_a_rotating_choice_among_reassemblies", human_name="MATCH / TRY / HIT with YMATCH and ASSMBL (SLIP); the POINT counter", status="ACCEPTED",
    mechanism="for the selected keyword's rule list, each decomposition pattern is tried by YMATCH (a SLIP function: match the input against a template with wildcards, binding pieces into TEST); on success the rule's reassembly list is chosen by a counter POINT stored in the rule (incremented and wrapped so successive uses cycle through the reassemblies), and ASSMBL builds the output from the template and the bound pieces; a rule of the form '= WORD' redirects to another keyword's rules",
    input="the truncated input; the rule list", output="a reply sentence", state="POINT per rule (persistent across sentences)", update="per reply",
    assumptions=["YMATCH/ASSMBL are library code outside this body (the SLIP manual is cited); their semantics are inferred from the calls", "cycling through reassemblies is what prevents identical replies to identical inputs"],
    fitness_value_in_ancestor="the illusion of understanding: a reply built from the user's own words in a new frame", failure_landscape="by reading: a decomposition that matches nothing falls through to the next; a keyword with no matching rule falls to NOMATCH", human_prior="Weizenbaum's decomposition/reassembly rules (CACM 1966)",
    evidence_ref=T + ":MATCH through HIT", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="MATCH/TRY/FNDHIT/HIT; the library calls are outside the body",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "memory": "LAST_VALUE", "stochasticity": "DETERMINISTIC", "representation_sensitivity": "SENSITIVE"})

mem = c.organ("four_slot_memory_that_stores_a_transformed_earlier_sentence_and_replays_it_when_nothing_matches", human_name="MEMORY / MYTRAN(1..4) / MYLIST; ENDTXT (the LIMIT = 4 branch)", status="ACCEPTED",
    mechanism="the script names one keyword as MEMORY with four transformation rules; whenever that keyword wins, the input is ALSO transformed by one of the four rules (chosen by a 2-bit hash of the last word) and appended to MYLIST; later, when a sentence has no keyword and the sentence counter LIMIT (cycling 1..4) equals 4 and MYLIST is not empty, the oldest stored transformation is printed instead of a NONE reply",
    input="sentences containing the MEMORY keyword; keyword-less sentences", output="a delayed reply about an earlier topic", state="MYLIST (a queue), LIMIT (1..4 counter)", update="per sentence",
    assumptions=["returning to an earlier topic reads as attentiveness; the 1-in-4 cadence is a constant"], fitness_value_in_ancestor="the only cross-sentence state in the program; the 1966 paper's 'memory' feature", failure_landscape="UNKNOWN by run",
    human_prior="the MEMORY keyword is usually MY in the DOCTOR script ('earlier you said your ...')", evidence_ref=T + ":BEGIN (MEMORY branch); ENDTXT", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the MEMORY reader, the KEYWRD = MEMORY branch, the LIMIT = 4 branch",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "state_persistence": "PER_EPISODE", "memory": "WINDOW", "stochasticity": "DETERMINISTIC", "temporal_horizon": "WINDOW"})

none = c.organ("fallbacks_for_no_keyword_and_no_match_with_a_four_way_rotating_stock_phrase", human_name="KEY(32) NONE rules; NOMATCH(1..4) indexed by LIMIT", status="ACCEPTED",
    mechanism="a sentence with no keyword goes to the NONE rule list (KEY(32), 'ES = BOT.(TOP.(KEY(32)))'); a keyword whose decompositions all fail goes to one of four fixed replies chosen by the sentence counter ('PLEASE CONTINUE', 'HMMM', 'GO ON, PLEASE', 'I SEE')",
    input="the failure branch", output="a content-free reply", state="LIMIT", update="per failure", assumptions=["silence would break the illusion; a rotating stock reply is cheaper than a rule"], fitness_value_in_ancestor="the conversation never stops", failure_landscape="none",
    evidence_ref=T + ":ENDTXT (IT = 0), NOMATCH(1..4)", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the two fallback paths",
    coverage={"input_topology": "EVENT", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC"})

edit = c.organ("live_script_editor_reached_by_a_leading_plus_sign", human_name="CHANGE (1-100): TYPE, SUBST, APPEND, ADD, START, RANK, DISPLA", status="ACCEPTED",
    mechanism="an input beginning with '+' enters CHANGE, which reads commands to print a keyword's rules, substitute or append to a rule, add a rule, set a keyword's rank, or display everything including the memory list; '*' adds a new keyword list; at end of input the revised script is dumped as a new numbered script",
    input="editor commands", output="a modified script in memory; a dumped script file", state="the script lists", update="per command", assumptions=["the script is edited in the same session it runs in; the persona is grown by conversation"],
    fitness_value_in_ancestor="Weizenbaum's stated purpose: a tool for building scripts, not a fixed DOCTOR", failure_landscape="UNKNOWN by run", evidence_ref=T + ":1-100; NEWLST; ENDPLA", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="the CHANGE function and the '+' / '*' branches",
    coverage={"input_topology": "SEQUENCE", "output_topology": "TREE", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "DURABLE", "stochasticity": "DETERMINISTIC"})

c.reject("TPRINT, TREAD, TXTPRT, LISTRD and the SLIP list primitives (SEQRDR, SEQLR, NEWTOP, POPTOP, ...)", reason="INHERITED_FROM_RUNTIME_OR_LIBRARY", evidence="SLIP is Weizenbaum's list-processing library, not in the body; YMATCH/ASSMBL are its pattern functions", note="the two pattern functions ARE load-bearing and are outside the body: a provenance gap to report")
c.reject("the DOCTOR script (CACM_1966_eliza_script.txt)", reason="OTHER", evidence="data, not mechanism; the persona", note="the script is the world's content; a different script is a different conversation with the same organs")
c.reject("'ELIZA' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the 1966 C++ re-implementation in the vault (eliza-anthay-1966, cut 09-16) has the same five mechanisms in a different language; recurrence R1 by reading")

c.edge(kw, clause, "feeds"); c.edge(clause, decomp, "feeds"); c.edge(kw, decomp, "selects"); c.edge(kw, mem, "triggers", note="the MEMORY keyword"); c.edge(mem, none, "competes", note="a stored line beats a NONE reply at LIMIT = 4"); c.edge(decomp, none, "triggers", note="no decomposition matched"); c.edge(edit, kw, "updates")

c.pressure("a_reply_must_be_produced_to_any_sentence_within_one_scan_from_a_small_editable_rule_set_and_must_not_repeat_itself",
    condition="an interlocutor types free text; the organism must answer every line with something that reads as responsive, using rules a non-programmer can edit; it has one pass over the words and a few hundred rules; identical inputs must not draw identical replies",
    resource_or_constraint="one scan; a hash table of rules; a handful of words of state across turns", failure_condition="silence, an off-topic reply where a keyword was present, or a repeated reply", world_punishes="parsing (too slow, too brittle) and canned replies (repetition)",
    world_rewards="keyword precedence, clause truncation, template reassembly from the user's words, a rotating choice, a small memory", observable_consequence="fraction of test sentences answered with a reply containing a fragment of the input; repeat rate over a scripted dialogue; human judgement of responsiveness (the record's 1966 outcome)",
    vacuity_condition="a fixed set of inputs (a lookup table suffices)", trivial_shortcuts="echoing the input verbatim", cheat_control="an organism given the human's expected reply must score 100% responsive; the echo organism must score high on 'contains a fragment' and zero on judged responsiveness: the world must separate those two measures or it is measuring echo",
    cost_class="CPU-scale", source_evidence="MAD-SLIP_translation.txt main loop; record human_capability_summary", purpose="PURPOSE: natural-language conversation by script (Weizenbaum 1966)")

c.ancestry("historical_version_of", "the 1966 CACM description; eliza-anthay-1966 (C++ recreation, in the vault) and cosell-eliza-bbn-lisp-1969 (BBN Lisp port, in the vault) descend from this listing", note="from the record and the vault; the recurrence across the three is the natural Stage E test")
c.residue("PARTIALLY_EXPLAINED", ["YMATCH and ASSMBL (the pattern matcher and rebuilder) are SLIP library functions outside the body; their semantics are inferred from the call sites and the annotation's pointer to the SLIP manual -- a provenance gap for Techne", "the CACM script not read; the annotated transcription read only at its head", "nothing ran (MAD on IBM 7094; the vault's lisp-1-5 record names simh i7094 as a reachable world for the same era)"],
          note="the interpreter's control flow is accounted for line by line; the matcher is the residue")
c.save(state="COARSE")
