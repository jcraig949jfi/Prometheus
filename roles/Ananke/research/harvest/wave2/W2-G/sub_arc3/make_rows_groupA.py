"""Write rows_groupA.csv (group A claims) from groupA_values.json + audit judgements.

Run from the worktree root AFTER rederive_groupA.py:
    python roles/Ananke/research/harvest/wave2/W2-G/sub_arc3/make_rows_groupA.py
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
V = json.load(open(os.path.join(HERE, "groupA_values.json")))
WK = "roles/Ananke/research/workers/"
COLS = ["claim_id", "doc", "location", "claim_text", "source_report", "report_value", "raw_path",
        "rederived_value", "status", "denominator", "denominator_ok", "wording_exceeds", "notes"]
S27, A2, A3, PR, EC, BL = ("SYNTHESIS_2026-09-27.md", "SYNTHESIS_2026-09-28_ARC2.md", "SYNTHESIS_2026-09-28_ARC3.md",
                          "ARC3_PRIORITIES.md", "PTE_ENGINE_CARD.md", "BACKLOG_V2.md")


def v(k):
    return json.dumps(V.get(k), default=str)


rows = [
    # ---------------- W-A
    ["7a", f"{A2};{BL}", "ARC2 s1/s5; BACKLOG_V2 T-DE-1 row",
     "zero-parameter model predicts 46/46 unseen accuracy-vs-gap curves (median MAE .02)",
     WK + "W-A/REPORT.md s2", "46/46 FIT+INTERVAL-HOLDS; median MAE ~0.02, max 0.058",
     WK + "W-A/out/engine.json; predictions.json",
     f"sat {v('WA_sat_pass')} MAE(med,max) {v('WA_sat_MAE_median_max')}; nosat {v('WA_nosat_pass')}; "
     f"bit-identical to a base (trained-condition) curve: {v('WA_tests_identical_to_a_base_curve')}; "
     "canon:uniform == pr0:4ab2ba01 == pr0:fresh3 (bit-identical)",
     "MATCH", "46 curves = 50 engine curves - 4 base", "PARTIAL",
     "YES (minor)",
     "Rule reproduced exactly. But 2 of the 46 'unseen' curves are bit-identical to base curves (canon:specimen; "
     "pr0:fresh1) and 3 more are one curve counted 3 times: 42 distinct curves not equal to a base curve. "
     "All 46 are TRANSFER re-evaluations of 4 frozen champions (one genome family), not independent mechanisms. "
     "Suggested: '46/46 curves (42 distinct, 4 champions of one lineage under 13 conditions)'."],
    ["7b", A2, "s1", "the base-curve null passes 12/44", WK + "W-A/REPORT.md s2 (post hoc)", "12/44",
     WK + "W-A/out/engine.json", v("WA_null_pass"), "MATCH", "44 = 46 minus 2 canonical-genome curves", "YES", "NO",
     "Labelled post hoc by W-A; ARC2 omits the post-hoc label. Null includes the pr0:fresh1 curve, which trivially passes (identical)."],
    ["7c", A2, "s2", "gap 7 beats gap 8 in 4/4 champions (readout-parity sawtooth)", WK + "W-A/REPORT.md s3(a)",
     "4/4 (0.97 vs 0.87 specimen)", WK + "W-A/out/engine.json base:*", v("WA_gap7_vs_gap8"), "MATCH",
     "4 champions (1 specimen + 3 regenerated fresh searches, same physics)", "YES",
     "NO", "Point estimates only; 7-vs-8 differences .04-.11, well outside pair CIs for 3/4 (not a formal test)."],
    ["7d", S27, "s2", "[M2] tuned to the trained gap: at chance at gap >= 12",
     "SPIKES_2026-09-27_LOG.md S-M2b (Ananke spike, not a W- worker)", "gap >= 12 at chance in 4/4",
     "roles/Ananke/research/spikes/out/s_m2b.json; W-A/out/engine.json",
     f"gap12 lo99>0.5 in {v('S_M2b_gap12_lo99_above_0.5')}/4 (acc .53-.58); gap16 lo99>0.5 in {v('S_M2b_gap16_lo99_above_0.5')}/4; "
     f"W-A base gap12 lo99 {v('WA_base_gap12_lo99')}",
     "MISMATCH", "4 champions", "YES", "YES",
     "At gap 12 three of four champions are above chance by their own 99% CI (spike AND W-A independent runs agree). "
     "Chance holds from gap 13/16. Correct: 'near chance by gap 12 (acc .53-.58), at chance by gap >= 16'. "
     "The frozen TUNED decision rule (gap 16 lo99 < .60) is unaffected."],
    # ---------------- W-B
    ["8a", f"{A2};{EC}", "ARC2 s2/s5; engine card MEMORY",
     "SETRULE is a per-tick conditional branch in 29% of 42 qualifying cells; bootstrap in 64%",
     WK + "W-B/REPORT.md s2", "bootstrap sufficient 27/42 (64%); ONGOING 12/42 (29%)", WK + "W-B/out/census.json",
     f"{v('WB_boot_share')}; {v('WB_ongoing_share')}; classes {v('WB_classes')}", "MATCH", "42 C1 cells", "PARTIAL",
     "YES",
     "Numbers match. Denominator caveat stated by W-B but dropped downstream: 5 of the 12 ONGOING are one lineage "
     "(c939c3c7 + 4 children). ARC2 s5 calls the 64% a 'bootstrap ARTIFACT'; the engine card says 'bootstrap into the "
     "ZERO-DEFAULT rule variant in ~64%' but only 24/42 (57%) are UNIFORM_BOOT/ZERO (1 settles on rule 1; 2 are "
     "PATTERN_BOOT). ARC2 calls ONGOING 'a per-tick branch' for all 29%, but the branch was shown in 6 RELAY + 2 HOLD "
     "deep-dived cells, not all 12."],
    ["8b", "SPIKES_LOG via S27 (s9 BACKLOG ref)", "", "(ARC2 s2 '~64%' bootstrap figure) see 8a", "", "", "", "", "MATCH",
     "", "", "", "merged into 8a"],
    ["8c", f"{A2};{EC}", "ARC2 s1 '0 FLIPs in 18 swaps'; engine card 'r never the memory carrier in 18/18 swap tests'",
     "r is never the bit carrier: 0 FLIPs in 18 swaps", WK + "W-B/REPORT.md s3 (and LOG A11)",
     "NO-EFFECT 17/18, CHANCE 1, FLIP 0", WK + "W-B/out/deepdive_all.json (merge of deepdive_part1 6 + part2 11)",
     f"n={v('WB_r_swap_n_cells')}; {v('WB_r_swap_verdicts')}", "MISMATCH", "17 cells (not 18)", "NO",
     "NO (direction), denominator wrong",
     "Raw has 17 cells (6 part 1 + 11 part 2; LOG A10 lists exactly 6+11). Report/LOG say 18 and '17/18 NO-EFFECT'. "
     f"Also 'pin all other sites exactly 0.000 in 13/18': raw exact-zero {v('WB_pin_others_exact0_near0')}; "
     f"pin readout HURTS {v('WB_pin_readout_HURTS')} (report 12/18). The 1 CHANCE (b059e735) is 'needed but not "
     "carrying' only under the absolute rule; W-O shows CHANCE is often a partial effect. Correct: 'r-swap FLIP 0/17 (16 NO-EFFECT, 1 CHANCE)'."],
    ["8d", A2, "s1", "M3: a one-rule law is bit-identical to the champion", WK + "W-B/REPORT.md s1",
     "rules=1 law bit-identical to rules=4 with r:=0 frozen; that arm EQUIV to normal (+0.014/+0.007)",
     WK + "W-B/out/m3.json X7", f"bit-identical vs r0-frozen {v('WB_rules1_vs_r0frozen_bit_identical')}; vs normal {v('WB_rules1_vs_normal')}",
     "MISMATCH", "2 M3 specimens", "YES", "YES",
     "The one-rule law is bit-identical to the champion WITH r:=0 FROZEN, not to the champion; vs the champion it is "
     "EQUIV with a +.014/+.007 gain concentrated in trial 0 (0.53 -> 0.67). Correct: 'a one-rule law is bit-identical "
     "to the champion with r reset to 0, and behaviourally EQUIV to the champion (2 M3 specimens)'."],
    # ---------------- W-F
    ["9a", f"{A2};{EC}", "ARC2 s5", "carriers: HOLD = site (81/85)", WK + "W-F/REPORT.md", "81/85 readable",
     WK + "W-F/out/census_table.csv", f"{v('WF_HOLD_site_over_readable')}; after W-O 512-world audit HOLD SITE {v('WF_HOLD_site_after_WO')}/85",
     "MATCH", "85 readable of 97 HOLD", "YES", "NO",
     "12 HOLD UNREADABLE excluded (stated). W-O audit moves 3 HOLD ELSEWHERE->SITE (84/85). Census is a RE-EVALUATION of stored champions at one tick (mid)."],
    ["9b", f"{A2};{PR}", "ARC2 s3; ARC3_PRIORITIES DEMOTED T-DM-2 ('14/14 were phase mixtures')",
     "all 14 JOINT cells are per-trial PHASE MIXTURES (site_acc + chan_acc = 1.00)", WK + "W-F/REPORT.md surprise 2",
     "14/14, mean .999", WK + "W-F/out/census_table.csv",
     f"(n,min,max,mean) {v('WF_JOINT_n_sum_min_max_mean')}; JOINT count after W-O audit {v('WF_JOINT_count_after_WO')}",
     "PARTIAL", "14 JOINT of 124 readable", "PARTIAL", "YES",
     "Numbers match raw (sum .978-1.011). The inference 'sum = 1 => phase mixture' is RETRACTED in ARC3 s2 (sum is a "
     "mirror-pair identity; by phi only 3/7 mixtures, W-I). ARC3_PRIORITIES still demotes T-DM-2 on '14/14 were phase "
     "mixtures' with no correction note, and W-O's 512-world audit leaves 12 JOINT (3 -> SITE, 1 -> CHANNEL, 2 ELSEWHERE -> JOINT). "
     "Correct: '14 census-JOINT cells (12 after audit) have site+chan accuracy summing to ~1, which is forced by the mirror-pair identity and does not by itself show a mixture'."],
    ["9c", A2, "s5 W-F line", "RELAY/MAJ = program- and phase-dependent; family 'selects' only via HOLD",
     WK + "W-F/REPORT.md decision + surprise 1", "tree CV .730 vs family .797; non-HOLD no model > ~.40",
     WK + "W-F/out/model.json", "not recomputed (classifier CV; needs refit)", "REPORT_ONLY", "39 non-HOLD readable, 11 physics points",
     "YES", "NO", "'Family selects' is a classifier-accuracy statement over a re-evaluated census, not a selection/search outcome."],
    # ---------------- W-C
    ["10a", f"{A2};{EC}", "ARC2 s6; engine card MEMORY CORRECTION", "7/13 PTE specimens carry the cue as WHO FIRES",
     WK + "W-C/REPORT.md bottom line", "7/13", WK + "W-C/out/x12.json", f"fire_share>0.5: {v('WC_fire_share_gt_0.5')}",
     "MATCH", "13 specimens (12 D-wave + M2)", "YES", "PARTIAL",
     "7 by fire_share > .5. W-C's own class list names 8 presence cells (incl. HOLD 7b7b025e, fire .49/presence .50). "
     "13 specimens from one campaign; 'PTE specimens carry...' should read '7 of 13 C1 D-wave/M2 specimens'."],
    ["10b", EC, "MEMORY CORRECTION", "'never counts' is NOT_VERIFIED where the counts swap was near-identity (5/13)",
     WK + "W-C/REPORT.md X2", "5/13", WK + "W-C/out/x12.json x2.pairs_mcnt_differ",
     v("WC_counts_swap_near_identity(<5% pairs differ)"), "MATCH", "13", "YES", "NO",
     "4 have exactly 0 count-differing pairs; 85ca202e has 1.8% (near-identity threshold not stated in report; <5% reproduces)."],
    ["10c", A2, "s6", "the cost made champions communicate more (3/3 vs 1/3), not change code class (n = 3 per arm)",
     WK + "W-C/X4_RESULT.md", "A1 3/3 vs A0 1/3 communicate", WK + "W-C/out/x4_A{0,1}_{0,1,2}.json",
     f"comm_delta>0: A1 {v('WC_X4_A1_comm_delta_gt0')}, A0 {v('WC_X4_A0_comm_delta_gt0')}; fire_share defined A1 3/3, A0 1/3; per-run {v('WC_X4(held,lo99,comm_delta,fire_share,site,inflight,counts)')}",
     "MISMATCH", "3 searches per arm", "YES (n=3 stated)", "YES",
     "A1_2 has comm_delta = 0.000 (zero-comm accuracy = held .760; site FLIP): it FIRES (fire share 1.0) but communication "
     "is not used. By the behavioural measure the cost arm communicates in 2/3, not 3/3. 3/3 counts 'fires', not "
     "'communicates'. Correct: 'cost champions fired in 3/3 (vs 1/3) but used communication in 2/3 (vs 1/3); n = 3 per arm, "
     "different economy (W-C pre-run deviation 2/1/64)'. This IS a search outcome (6 real searches)."],
    ["10d", EC, "MEMORY CORRECTION", "an emission-cost pilot evolved a counts code that FLIPs under a counts swap (n = 1)",
     WK + "W-C/REPORT.md X4 pilot", "A1 seed 0 counts FLIP", WK + "W-C/out/x4_A1_0.json",
     "A1_0 counts FLIP, inflight FLIP, site CHANCE", "MATCH", "1 search", "YES", "NO", "n=1 stated."],
    # ---------------- W-E
    ["11a", A2, "s5 W-E line; s9", "W-E: no recoverable retention past the query (preregistered NO)",
     WK + "W-E/REPORT.md verdict", "NO; min Holm p .149 (f7e62fe3); 'mostly a POWER limit'",
     WK + "W-E/out/D_*.json, M2_*.json decoder_single",
     f"family {v('WE_family_size')} (16x7); min Holm j>=2 {v('WE_min_holm_single_j>=2')}; labels {v('WE_labels')}; "
     f"j0 decodes after Holm {v('WE_j0_decodes')}/16",
     "PARTIAL", "16 champions (12 D-wave + 4 M2), 1 namespace", "YES", "YES",
     "Preregistered verdict reproduced exactly (0.149). But W-E itself says the NO is mostly a POWER limit, and its post-hoc "
     "history-aware decoder RECOVERS cue k from f7e62fe3 w_sum at .89-.97 for j=1..6; W-G later CONFIRMED this as "
     "preregistered L2 in two namespaces. So 'no recoverable retention' is contradicted for f7e62fe3; what failed is "
     "EFFECTIVE (answer-changing) retention. Minor report mismatch: 'all 16 decode at j=0 (p at the floor)': D_544f3d24 "
     "raw p 2e-4 (not floor) -> Holm 15/16. Correct: 'no champion's cue k is recoverable by the preregistered single-world "
     "decoder (power-limited); one accumulation trace (f7e62fe3 w) is recoverable post hoc and never changes an answer'."],
    # ---------------- SYNTHESIS 09-27
    ["13a", S27, "s6", "C1 window covered 0% of the cue-bearing arrivals in both M3 cells and 69-100% elsewhere",
     "TEMPORAL_INTERVENTION_COVERAGE.md / SPIKES S-F (Ananke spike)", "0 / 0; RELAY .69-1.00, MAJ .93, M2 .80",
     "roles/Ananke/research/spikes/out/s_f.json", f"{v('S_F_c1_window_coverage')}", "MATCH",
     "9 cells (2 M3, 4 RELAY, 2 MAJ, M2); 28-30 of 32 pairs with any cue arrival in M3", "YES", "PARTIAL",
     "'elsewhere' = the 7 other spike cells, not all C1 cells."],
    ["13b", S27, "s11", "Predictions held: 15. Lost: 5", "SPIKES_2026-09-27_LOG.md", "itemised per line",
     "roles/Ananke/research/SPIKES_2026-09-27_LOG.md (pred column)",
     f"lines marked HELD {v('SPIKES_pred_lines_HELD')} (2 of them partial 3/4), LOST {v('SPIKES_pred_lines_LOST')}",
     "PARTIAL", "unclear grouping", "NO", "NO",
     "The tally depends on grouping: synthesis counts the 3 S-CT cell losses (bbef66a1, 613162a3, 4781b0a1) as ONE loss and "
     "one HELD (likely the joint-swap addendum or a partial) is not counted. Line count: 16 HELD (2 partial 3/4) vs 7 LOST. "
     "No raw ledger of predictions to recount."],
    ["13c", S27, "s2", "M2 carrier: sign of the in-flight sum of one component (decoder 1.00)", "SPIKES_2026-09-27_LOG.md S-M2",
     "1.00 [1.00] in 4/4", "roles/Ananke/research/spikes/out/s_m2.json", v("S_M2_code_component_decoder"), "MATCH",
     "4 champions, held-out half of pairs", "YES", "NO", "pay1 for specimen/fresh2/fresh3, pay0 for fresh1."],
    ["13d", S27, "s4", "EXTERNAL RESEARCH (~45 sources, graded)", "PRIOR_ART_temporal_distributed_computation.md",
     "~45", "roles/Ananke/research/PRIOR_ART_temporal_distributed_computation.md",
     f"Source: blocks {v('PRIOR_ART_Source_blocks')}; unique URLs/DOIs {v('PRIOR_ART_unique_urls_dois')}", "MATCH",
     "44 source entries", "YES", "NO", "Not worker-sourced. Count depends on unit (entries vs references)."],
    ["13e", S27, "s2", "The same code in 3/3 fresh champions (one on the other component)", "SPIKES_2026-09-27_LOG.md D5/D6",
     "pay1 x3 (incl. specimen), pay0 fresh1", "roles/Ananke/research/spikes/out/s_m2.json", v("S_M2_code_component_decoder"),
     "MATCH", "3 fresh re-searches, same physics and seed recipe", "YES", "NO",
     "fresh1-3 are deterministic regenerations of stored search seeds (bit-identical held), i.e. replay, not new searches."],
    # ---------------- ARC2 instruments
    ["14a", A2, "s1", "carrier swap and temporal reach instruments: 10 known-answer tests with negative controls",
     "instruments/INSTRUMENT_CARRIER_SWAP.md; commit a4e414392", "10",
     "prometheus/ananke/tests/test_lens_instruments.py @a4e414392 (git show)",
     f"def test_ count = {v('lens_tests_at_a4e414392(before ARC2 8eabc990b)')}", "MATCH", "test functions", "YES", "NO",
     "9 at bb61f8483 + 1 arm_identical test at a4e414392 = 10 before the ARC2 commit 8eabc990b. Not run here (read-only)."],
    ["14b", A2, "s1", "used across 166 cells with 0 errors", WK + "W-F/REPORT.md", "166 cells, 0 errors",
     WK + "W-F/out/census_s{0,1}.jsonl", f"166 rows, error fields {v('WF_jsonl_rows_with_error_field')}", "PARTIAL",
     "166 C1 cells", "YES", "YES",
     "'0 errors' = 0 runtime/software errors. It is not verdict validity: W-O's 512-world audit changed 9 W-F mid classes "
     "(21 under re-run normal) and found the absolute rule blind to complete transfers at normal ~.57-.62. Correct: '166 cells, "
     "0 runtime errors; verdicts later partly revised (W-O)'."],
    # ---------------- other W-A..W-F numbers
    ["15a", A2, "s4", "W-D mined 8 'could not fire' cases in 5 seats; three checks plus an identical-arms alarm cover all 8",
     WK + "W-D/REPORT.md", "8 cases; cover 8/8", "none (W-D has REPORT.md only)", "none", "REPORT_ONLY", "8 cases", "n/a", "NO",
     "Provenance hole: W-D has no PLAN/LOG/out/ in the worker dir."],
    ["15b", A2, "s1/s5", "M2 in-flight carrier is CONTENT, not presence (W-C twin census: no firing difference)",
     WK + "W-C/REPORT.md X1", "presence/fire share 0/0", WK + "W-C/out/x12.json M2:4ab2ba01",
     "presence_share 0.0, fire_share 0.0", "MATCH", "1 specimen (M2)", "YES", "NO", ""],
]

with open(os.path.join(HERE, "rows_groupA.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(COLS)
    for r in rows:
        if r[0] == "8b":
            continue
        assert len(r) == len(COLS), r[0]
        w.writerow(r)
print("wrote rows_groupA.csv", len(rows) - 1, "rows")
