"""Writes RED_EDITS.json (run from the repo root: python rso/z80/red/make_edits.py); asserts every find string is unique.
v1.1.0: 27 + 5 repair pins (R1-R5) + 4 challenge edits (E1 E2 E3 E5, verbatim from rso/z80/challenge/edits.json) = 36."""
import json
O, A, N = "rso/z80/observe.py", "rso/z80/assay.py", "rso/z80/analysis.py"
E = [
 ("O1", O, 'and all(a["nbr_mask"][k] and a["nbr_window"][k] == win[k] for a in alts) else "K"', 'else "K"', "P ignores the counterfactual", "test_a_copy_made_by_the_neighbours_code_is_environmental"),
 ("O2", O, '"P" if res0["nbr_mask"][k] and all(', '"P" if all(', "unwritten (kept) bytes count as parent-written", "test_counterfactual_tags_per_byte"),
 ("O3", O, '"M" if child[k] != win[k] else', '"M" if False else', "copy noise not tagged", "test_counterfactual_tags_per_byte"),
 ("O4", O, 'p, "R" * G)', 'p, "P" * G)', "runner births tagged parent-written", "test_external_child_is_runner_written"),
 ("O5", O, 'src = "S" if supplied else "R"', 'src = "S"', "random founders recorded as supplied", "test_origin_reads_founder_bytes"),
 ("O6", O, 'bytes(alt(b) for b in nbr)', 'bytes(nbr)', "counterfactual does not alter the pre-window", "test_a_copy_made_by_the_neighbours_code_is_environmental"),
 ("O7", O, 'tags[i] = "".join("M" if a != b else t for a, b, t in zip(new, genomes[i], tags[i])); situ[i] = None', 'situ[i] = None', "background mutation not tagged", "test_background_mutation_is_tagged_where_it_changed_bytes"),
 ("O8", O, 'situ[i] = touched and all(T.score_case(tname, vm.execute(genomes[i], nbr, c', 'situ[i] = touched and all(T.score_case(tname, vm.execute(genomes[i], bytes(G), c', "situ probed with a zeroed, not the live, neighbour", "test_situ_is_neighbour_dependence_not_luck"),
 ("O9", O, 'situ[i] = touched and all(', 'situ[i] = touched and any(', "situ needs one probe case, not all", "test_situ_is_neighbour_dependence_not_luck"),
 ("S1", A, 'z = bytes(len(tape))', 'z = S.HOST()', "F0 probe with a live (host) neighbour", "test_function_only_with_the_neighbour_is_environmental"),
 ("S2", A, 'return all(T.score_case(S.TASK', 'return any(T.score_case(S.TASK', "F0 needs one case, not all", "test_nonfunctional_is_unlabelled"),
 ("S3", A, 'if f0(restrict(tape, tags, letter), cases):', 'if letter in tags:', "writer by presence, not sufficiency", "test_sufficiency_order"),
 ("S4", A, '"PRIM"', '"PRIMK"', "environment bytes never needed", "test_sufficiency_order"),
 ("S5", A, 'return "ENV" if situ else None', 'return "ENV"', "every non-F0 organism is ENV", "test_nonfunctional_is_unlabelled"),
 ("S6", A, '2 * labels.count(top) > len(labels)', '2 * labels.count(top) >= len(labels)', "plurality, not strict majority", "test_run_class_is_a_strict_majority"),
 ("S7", A, 'if claimed != [(o["cell"], o["tape"].hex(), o["gen"]) for o in obs["final"]]:', 'if False:', "no replay equality check", "test_byte_and_physics_forgeries_are_refused"),
 ("S8", A, 'src == "S" and f0(t, cases)', 'f0(t, cases)', "a lucky random founder counts as insertion", "test_origin_reads_founder_bytes"),
 ("S9", A, 'cls=run_class(labels), n_func', 'cls=run_class(labels) if rec["spec"].get("init") != "random" else "ENDO", n_func', "the class reads the spec's init label", "test_label_forgeries_change_nothing"),
 ("N1", N, 'if n <= 0 or tail_le(n, 0, bound) > alpha:', 'if n <= 0:', "no power floor", "test_w_max_is_the_exact_binomial_threshold"),
 ("N2", N, 'and r[key] != "NONE"]', ']', "non-functional runs stay in the denominator", "test_nonfunctional_runs_leave_the_denominator"),
 ("N3", N, 'sum(r[key] != c for r in R)', 'sum(r[key] not in (c, "MIXED") for r in R)', "MIXED not counted as wrong", "test_mixed_counts_as_wrong"),
 ("N4", N, ' or r["origin"] != r["source_origin"]', '', "label forgeries may move the origin", "test_one_label_forgery_that_moves_the_origin_fails"),
 ("N5", N, 'r["cls"] != "REFUSED" or r["refused"] != "REPLAY_MISMATCH"', 'r["refused"] == "UNSUPPORTED"', "an unrefused byte forgery passes", "test_one_unrefused_forgery_fails"),
 ("N6", N, 'if not R or bad:', 'if bad:', "a missing forgery kind passes", "test_a_missing_forgery_kind_fails"),
 ("N7", N, 'baseline_passes = [b for b, q in Q4.items() if all(t["pass"] for t in q.values())]', 'baseline_passes = []', "baselines never checked", "test_a_baseline_that_passes_q1_makes_the_set_uninformative"),
 ("N8", N, 'if failed:', 'if failed and not unpowered:', "underpowered hides a failure", "test_failure_outranks_underpowered"),
 ("N9", N, 'sum(r["origin"] != r["origin_gt"] for r in R2)', '0', "origin never scored", "test_origin_errors_fail"),
]
# v1.1.0 (C-017-T041): the repair's own pins, and Pallas's semantic edits applied VERBATIM from challenge/edits.json (find/replace
# not retyped) with the test that now pins each. E4 is already S6.
SUB = "rso/z80/subjects.py"
E += [
 ("R1", O, 'else "K" if reads else', 'else', "a parent that read the window may still write P bytes (the v1.0.0 tag)", "test_a_parent_that_reads_the_window_writes_no_parent_byte"),
 ("R2", O, 'reads = res0["reads_nbr"] > 0', 'reads = res0["reads_nbr"] > 0 or res0["exec_foreign"] > 0', "foreign execution (a parent running its own fresh copy) forces K", "test_running_into_its_own_fresh_copy_stays_parent_written"),
 ("R3", A, '"ENDO" if f0(written, cases) else "ENV"', '"ENDO"', "the recipe reader has no ENV output", "test_recipe_reader_reads_the_construction"),
 ("R4", N, 'BASELINES = ("b1", "b2", "b4")', 'BASELINES = ("b1", "b2")', "the recipe reader is not a Q4 baseline", "test_the_recipe_reader_is_a_registered_baseline"),
 ("R5", SUB, 'if i < 10 else BASE2[part]', 'if True else BASE2[part]', "arm 10 seeds overlap the next partition", "test_partitions_are_disjoint_from_every_registered_namespace"),
]
PINS = {"E1_ONE_COUNTERFACTUAL": "test_both_counterfactual_samples_are_load_bearing", "E2_NOP_FILLER_0x1E": "test_the_sufficiency_filler_is_zero",
        "E3_REFUSED_LEAVES_DENOMINATOR": "test_an_unforged_refusal_counts_as_wrong", "E5_COUNTERFACTUAL_EMPTY_INPUT": "test_the_counterfactual_keeps_the_parents_input"}
for c in json.load(open("rso/z80/challenge/edits.json", encoding="utf-8"))["edits"]:
    if c["id"] in PINS:
        E.append((c["id"], c["file"], c["find"], c["replace"], c["what"] + " (challenge/edits.json, verbatim)", PINS[c["id"]]))
# O1 / O6: the copy-onto-itself parent READS the window, so since v1.1.0 it is K whatever the counterfactual says; the two
# counterfactual mutants are pinned by the exec-only parent instead
RE = {"O1": "test_both_counterfactual_samples_are_load_bearing", "O6": "test_both_counterfactual_samples_are_load_bearing"}
E = [(i, f, a, b, w, RE.get(i, t)) for i, f, a, b, w, t in E]
out = [dict(id=i, file=f, find=a, replace=b, what=w, expect=t) for i, f, a, b, w, t in E]
for e in out:
    src = open(e["file"], encoding="utf-8").read()
    assert src.count(e["find"]) == 1, (e["id"], src.count(e["find"]))
json.dump(out, open("rso/z80/red/RED_EDITS.json", "w", encoding="utf-8", newline="\n"), indent=1)
print(len(out), "edits, every find unique")
