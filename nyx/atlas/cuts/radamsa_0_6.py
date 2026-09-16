"""Cut: radamsa-0.6 (ancestry-aware, Stage A COARSE; SOURCE_READ rad/mutations.scm 25-50, 960-1181 (menu, scheduler) and the function
index 1-960; patterns.scm function index + 23-65 skimmed; file sizes for the rest; generators.scm / output.scm / fuse.scm / xp.scm /
digest.scm NOT read). Owl Lisp; 3,926 lines; the general-purpose black-box fuzzer."""
from nyx.atlas.author import Cut

S = "vault:radamsa-0.6/upstream/tree/radamsa-v0.6/rad/"
c = Cut("radamsa-0.6", mode="ANCESTRY_AWARE", inspected=["mutations.scm (scheduler, menu, function index)", "patterns.scm (index, mutate-once)", "file list"],
        evidence=[("SOURCE_READ", S + "mutations.scm"), ("SOURCE_READ", S + "patterns.scm")],
        note="a menu of 32 mutators at five representation levels (byte, byte-sequence, line, delimiter-tree, lexed string) under a scheduler whose only feedback is whether the mutation changed the bytes -- there is no signal from the target")

sch = c.organ("mutator_scheduler_by_score_times_priority_with_self_reported_delta_and_retry_on_no_change", human_name="mux-fuzzers / weighted-permutation / adjust-priority", status="ACCEPTED",
    human_interpretation="mutators compete for use; ones that keep producing changes get used more",
    mechanism="each mutator carries (score in [2, 10], randomised from the seed at start; a user priority from the -m string); to pick one, draw rand(score * priority) per mutator and sort descending; try them in that order until one CHANGES the current chunk; every tried mutator returns a delta (+1 / -1 drawn with a 11/20 upward bias on success, -1 when it could not apply) which is added to its score and clamped; the new closure carries the updated scores ('always remember whatever was learned')",
    input="the mutator list, a random state, the data stream", output="a mutated stream and a re-scored mutator list", state="per-mutator score (2..10)", update="per mutation attempt",
    assumptions=["'the bytes changed' is the only success signal available; the delta is a biased random walk, not a reward from the target"],
    fitness_value_in_ancestor="prevents a stuck mutator (one that never applies to this input) from being drawn forever; the record's 'mutations too shallow' failure is what the menu, not the scheduler, addresses", failure_landscape="UNKNOWN by run",
    evidence_ref=S + "mutations.scm:25-50,1095-1181", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="mux-fuzzers + weighted-permutation + adjust-priority + mutators->mutator",
    coverage={"input_topology": "STREAM", "output_topology": "STREAM", "state_amount": "CONSTANT", "stochasticity": "SEEDED_RANDOM", "adaptation": "PARAMETER", "competition": "CONTENDS", "feedback": "CLOSED_LOOP", "memory": "SUMMARY_STATISTIC"})

pat = c.organ("mutation_count_and_placement_pattern_once_many_burst_with_inverse_probability_walk", human_name="patterns.scm (od / nd / bu)", status="ACCEPTED",
    mechanism="a pattern decides how many mutations one output gets and where: mutate-once walks the lazy byte stream decrementing an 'inverse probability' counter drawn at start so the position is geometric-like and the last chunk is always eligible; pat-many applies once then possibly again; pat-burst applies several in a row at one place; patterns are themselves chosen by priority (mux-patterns)",
    input="stream, mutator, random state", output="a stream with mutations applied", state="none beyond the random state", update="per output", evidence_ref=S + "patterns.scm:23-111", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="patterns.scm",
    coverage={"input_topology": "STREAM", "output_topology": "STREAM", "state_amount": "NONE", "stochasticity": "SEEDED_RANDOM"})

by = c.organ("byte_level_edits_at_a_random_position", human_name="bd bf bi br bp bei bed ber (sed-byte-*)", status="ACCEPTED",
    mechanism="edit-byte-vector at a random index: drop, flip one bit, insert random, repeat (with a heavy-tailed repeat count, repeat-len), permute a few, +1, -1, replace random; each returns the delta for the scheduler",
    input="a byte chunk", output="a byte chunk", state="none", update="none", evidence_ref=S + "mutations.scm:64-85,162-260", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="sed-byte-* functions",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "NONE", "stochasticity": "SEEDED_RANDOM"})

sq = c.organ("sequence_repeat_and_delete_of_a_random_range", human_name="sr sd", status="ACCEPTED", mechanism="pick a range and repeat it (repeat-len times) or delete it", input="a byte chunk", output="a byte chunk", state="none", update="none",
    evidence_ref=S + "mutations.scm:324-362", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="sed-seq-repeat / sed-seq-del",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "NONE"})

ln = c.organ("line_level_list_operations_by_lifting_through_a_newline_split", human_name="ld lds lr2 li lr ls lp lis lrs (line-op / stateful-line-op)", status="ACCEPTED",
    mechanism="line-op wraps a generic list operation (delete, delete-sequence, duplicate, clone nearby, repeat, swap, permute) as: split the chunk on newlines -> apply -> join; stateful-line-op carries state across calls for insert/replace 'from elsewhere' (a line seen earlier)",
    input="a byte chunk", output="a byte chunk", state="none (stateful ops: a remembered line)", update="none", assumptions=["the input is line-structured"], evidence_ref=S + "mutations.scm:364-425", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="lines / unlines / line-op / stateful-line-op and the nine definitions",
    fitness_value_in_ancestor="the same list ops serve lines and (below) tree nodes: representation lifting is the design",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "NONE", "representation_sensitivity": "SENSITIVE"})

tr = c.organ("tree_level_operations_over_a_partial_parse_by_balanced_delimiters", human_name="td tr2 ts1 ts2 tr (sed-tree-*)", status="ACCEPTED",
    mechanism="partial-parse builds a tree from balanced delimiter pairs (usual-delims: brackets, braces, quotes...; grow / count-nodes / sublists); a random subtree is deleted, duplicated, swapped with another, or a parent->child path is repeated ('stutter'); flatten writes the tree back",
    input="a byte chunk", output="a byte chunk", state="none", update="none", assumptions=["the input has nested delimiters (JSON, XML, source code)"], evidence_ref=S + "mutations.scm:507-720", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="usual-delims through sed-tree-stutter",
    fitness_value_in_ancestor="the answer to 'mutations too shallow': structure-preserving edits pass the first byte checks", coverage={"input_topology": "TREE", "output_topology": "TREE", "state_amount": "NONE", "representation_sensitivity": "SENSITIVE"})

st = c.organ("lexed_string_regions_replaced_by_classic_badness", human_name="ab (ascii-bad): string-lex / silly-strings / random-badness", status="ACCEPTED",
    mechanism="string-lex splits a chunk into text / byte / delimited(quote) regions when it is 'texty enough' (6+ printable bytes); a region is mutated by inserting or overwriting known-bad strings (format specifiers, huge lengths, 'A' runs -- silly-strings) or a random lex string; string-unlex rebuilds",
    input="a byte chunk", output="a byte chunk", state="none", update="none", evidence_ref=S + "mutations.scm:720-960", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="texty? through ascii-bad",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "NONE"})

nu = c.organ("textual_number_rewriting_with_interesting_deltas", human_name="num (sed-num / mutate-a-num)", status="CANDIDATE",
    mechanism="find digit runs, parse, replace with a boundary-ish value (the delta generators rand-delta / rand-delta-up and xp.scm's number tables -- xp.scm NOT read)", input="a chunk", output="a chunk", state="none",
    evidence_ref=S + "mutations.scm:86-160", confidence="LOW", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="sed-num + xp.scm",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE"})

fu = c.organ("splice_between_shared_suffixes_within_or_across_samples", human_name="ft fo fn (sed-fuse-this / fuse-old / fuse-next), fuse.scm", status="CANDIDATE",
    mechanism="jump from one position to another that shares a suffix (a suffix-array style join) inside the block, with an earlier sample, or with the next -- a crossover operator between inputs (fuse.scm not read)", input="chunks", output="a chunk", state="earlier samples (fuse-old)",
    evidence_ref=S + "mutations.scm:262-322; fuse.scm (unread)", confidence="LOW", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="sed-fuse-* + fuse.scm",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "memory": "WINDOW"})

ut = c.organ("utf8_overwide_encoding_and_funny_codepoint_insertion", human_name="uw ui", status="ACCEPTED", mechanism="re-encode a code point with too many continuation bytes; insert from a table of troublesome code points (funny-unicode)", input="a chunk", output="a chunk", state="none", update="none",
    evidence_ref=S + "mutations.scm:427-505", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="funny-unicode / sed-utf8-*",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "NONE"})

c.reject("'radamsa' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="a scheduler over a menu of independent mutators, each separately selectable from the command line (-m)")
c.reject("generators.scm / output.scm (stdin, file, random, pcapng sources; stdout, file, tcp sinks)", reason="EFFECT_FROM_ENVIRONMENT", evidence="by name and the record; the I/O ends", note="unread")
c.reject("the lazy list (ll) streaming representation and the threaded random state (rs)", reason="GENERIC_LANGUAGE_MECHANICS", evidence="every function takes and returns rs; ll forces chunks on demand -- Owl Lisp purity discipline, not fuzzing machinery", note="it IS what makes the seed reproducible (record failure condition 'non-reproducible'); recorded as the mechanism of pressure 2, rejected as an organ")
c.reject("binarish? probe", reason="BELOW_MEANINGFUL_GRAIN", evidence=S + "mutations.scm:52-62 -- checks for a zero byte in the first few; gates ascii-bad")
c.reject("digest.scm (output de-duplication by hash), xp.scm", reason="OTHER", evidence="NOT READ", note="UNKNOWN")

for o in (by, sq, ln, tr, st, nu, fu, ut):
    c.edge(sch, o, "selects")
    c.edge(o, sch, "updates", note="delta")
c.edge(pat, sch, "schedules", note="how many / where"); c.edge(tr, ln, "competes", note="same list ops lifted to a different representation")

c.pressure("one_parser_faces_unbounded_malformed_input_with_no_signal_back_from_it",
    condition="a target rejects most random bytes at the first check; the fuzzer sees nothing from the target (no crash feedback, no coverage) and must still produce inputs that reach deep code", resource_or_constraint="no target feedback; a fixed menu of edits",
    failure_condition="all cases rejected at the first byte (record)", world_punishes="byte-only mutation of structured input", world_rewards="edits at the representation level the target parses (lines, trees, strings, numbers) and a menu wide enough that some edit applies",
    observable_consequence="how far into cjson's parser the cases get (record entry point: pipe into cjson under ASan)", vacuity_condition="a target that accepts anything", trivial_shortcuts="replay a corpus of known crashes (the world must present a new target)",
    cheat_control="a mutator given the target's grammar must reach deeper than every menu item; if the world scores it equal to byte flips, depth is not being measured", cost_class="CPU-scale", source_evidence="record pressure / failure; the mutation menu", purpose="PURPOSE: find parser bugs")
c.pressure("a_stochastic_process_must_be_exactly_replayable_from_a_seed",
    condition="a found bug is worthless unless the input can be regenerated; every random choice must derive from one seed and nothing else (no time, no I/O order)", resource_or_constraint="purity discipline",
    failure_condition="non-reproducible cases (record)", world_punishes="hidden entropy", world_rewards="threading one random state through every decision",
    observable_consequence="byte-identical output for the same seed and input", vacuity_condition="single-shot use", trivial_shortcuts="log every output (space; the world must charge for it)",
    cheat_control="N/A", cost_class="CPU-scale", source_evidence="the rs threading in every function", purpose="PURPOSE: same")
c.pressure("a_menu_of_operators_of_unknown_usefulness_must_be_scheduled_without_a_reward",
    condition="some operators never apply to this input and some always change it; the only observable is whether the output differs; the choice must not starve rare operators nor waste draws on inapplicable ones", resource_or_constraint="no external reward",
    failure_condition="repeatedly drawing an operator that cannot apply", world_punishes="uniform draws", world_rewards="a self-scoring scheduler with a floor (min-score 2) so nothing starves",
    observable_consequence="the 'used <name>' trace distribution on stderr", vacuity_condition="all operators always apply", trivial_shortcuts="round robin",
    cheat_control="a scheduler told which operators apply must waste zero draws; if the world scores it equal to uniform, applicability is not being charged", cost_class="CPU-scale", source_evidence="mux-fuzzers", purpose="PURPOSE: same")

c.residue("PARTIALLY_EXPLAINED", ["generators / output / fuse / xp / digest unread", "the lazy-stream position walk in mutate-once is read once, not understood to the constant (initial-ip 'magic value')", "the scheduler's delta is a biased random walk: whether scores ever separate mutators in practice is UNKNOWN by run"],
          note="the menu and the scheduler are fully read; the per-mutator implementations are read by index and signature")
c.save(state="COARSE")
