<!-- DEPOSITED VERBATIM by Ananke for worker W-O; sha256(report)=4d11edc1ca762cdc; delimited; see REPORT.provenance.json -->
W-O REPORT — E-ANANKE-W-O, T-SWAP-AUDIT (successor of T-SWAP-LOWACC thr-5df816e9b844), MWO-0001

WHAT I TESTED
- Scope: every recorded carrier-swap CHANCE verdict (lens.swap_verdict output) in the named Ananke records.
- Re-run design (frozen in PLAN.md before any re-run):
  - M=512 worlds (256 mirror pairs), seeds assays.world_seeds(0x600, 512).
  - Trials: the recorded design's set, scored trials only (W-F and s_ct: all trials; W-I: trials 1 onward).
  - Swap at the recorded offset, specimen loaded the same way the record loaded it.
- PRIMARY verdict: SINGLE-trial swaps (Arm trial=k, pooled over k), scored with lens.swap_verdict (unchanged rule) on paired pair means.
  - Run by my own fork runner (runner.fork_single). It is bit-identical to lens_swap.run_arms SINGLE (selfcheck.json).
  - I did not reuse W-N's run_fork; I wrote the same idea myself and selfchecked it.
- Every group also ran site_all and channel_all SINGLE, for the lens_swap census, classify and census_follow.
- SECONDARY: EVERY-trial swaps with the absolute rule, at M=512.
- TERTIARY, context only: W-N's relative rule (swap_rel), ungated, and gated with W-N's attain_table p_min (P256: .58-.59).
- Compute: 8 processes x 1 torch thread, CPU only, about 2 h 15 min of compute inside the 3 h budget.
- Deviation (LOG A8, order only, no rule or threshold changed): the preregistered EVERY subset was the lowest-hash groups, and shards ran in hash order, so the expensive EVERY groups ran first.
  - I stopped the shards and re-ran every group SINGLE first.
  - EVERY exists only for the 12 subset groups finished before the stop (29 verdicts). The other 55 subset groups have EVERY = NOT_RUN.
- Freeze: I cannot git commit, so inventory.csv was frozen by sha256 73eecd8a77a0c4e5… (LOG A1) before any re-run.

INVENTORY (out/inventory.csv, out/inventory_counts.json)
- 733 swap CHANCE verdicts on 249 groups (source x specimen x offset):
  - W-F census_s{0,1}.jsonl: 281 verdicts on 71 specimens (170 of them unreadable, recorded normal lo99 < .60).
  - W-I traj_<cell>.json, from which table_<cell>.csv is derived: 448 verdicts on 30 specimens (68 unreadable).
  - spikes/out/s_ct.json, the source of W-E's class labels: 4 verdicts on 2 specimens.
- Sources with 0 swap verdicts and 0 CHANCE: W-E out/, W-G out/, pte/c1b LABEL_TABLES.json, C1B_SUMMARY.json and c1b_rows.
- s_ct delay+1 CHANCE excluded: it is a perturbation, not a swap, and can never FLIP.
- Arms: site_all 172, channel_all 169, S 92, channel_content 92, joint 75, inbox 41, channel_count 40, pay* 28, r 15, Kp 5, sitestate/inflight/payload 4.
- Families: RELAY 536, MAJ 117, HOLD 80.
- Not audited (outside the brief's scope, but they contain CHANCE strings): W-B deepdive*, W-C x1b_x5/x4, W-H cf, W-J e2/e3/e6, spikes s_joint_4781 and s_m2, W-L carriers_champs (already re-run by W-N).

RESULTS (transition matrix; all rows recorded CHANCE; 99% intervals = Wilson / specimen-cluster bootstrap)

SINGLE, absolute rule, M=512 (733 of 733 run):

| Set | n | -> FLIP | -> NO-EFFECT | stays CHANCE |
|---|---|---|---|---|
| All | 733 | 90 (.123) W[.095,.157] C[.076,.188] | 28 (.038) W[.024,.061] C[.012,.068] | 615 (.839) W[.801,.871] C[.771,.896] |
| Readable | 495 | 39 (.079) C[.037,.125] | 17 (.034) | 439 (.887) |
| Unreadable | 238 | 51 (.214) C[.098,.429] | 11 (.046) | 176 (.739) |
| W-F | 281 | 64 (.228) C[.126,.349] | 11 | 206 |
| W-I | 448 | 26 (.058) C[.018,.095] | 17 | 405 |
| s_ct | 4 | 0 | 0 | 4 |
| HOLD | 80 | 35 (.44) | 1 | 44 |
| MAJ | 117 | 22 (.19) | 4 | 91 |
| RELAY | 536 | 33 (.06) | 23 | 480 |
| site_all arm | 172 | 40 (.23) | 7 | 125 |
| joint arm | 75 | 18 (.24) | 0 | 57 |

- Sub-carriers mostly stay CHANCE: S 8/92 FLIP, channel_content 7/92, inbox 0/41, channel_count 0/40, r 0/15.
- W-F by timing: mid 45/198 FLIP, late 19/78 FLIP, pre 5/5 NO-EFFECT.
- 117 of the 238 "unreadable" verdicts sit on specimens whose normal lo99 is >= .60 at M=512. Most of the unreadable FLIPs come from these (HOLD unreadable: 25/32 FLIP).
- D1 (frozen rule): readable CHANCE->FLIP is 39/495, cluster 99% [.037, .125]. The call is PARTIAL (the lower bound is not > .20; the upper bound is not < .10).
- EVERY vs SINGLE, absolute rule, 29 verdicts: agree on 28/29. The one split is FLIP (SINGLE) vs CHANCE (EVERY). EVERY alone: 3 FLIP, 26 CHANCE.
- W-N relative rule on all 733 (context only):
  - Ungated: FLIP_REL 170 (.23), NO_EFFECT_REL 81, CHANCE_REL 376, INDETERMINATE 106.
  - Gated: FLIP_REL 117, NO_EFFECT_REL 80, CHANCE_REL 354, INDETERMINATE 101, NOT_ELIGIBLE 81.
  - Of the 615 that stay CHANCE (absolute), gated REL gives CHANCE_REL 344, INDETERMINATE 96, NOT_ELIGIBLE 79, NO_EFFECT_REL 54 and FLIP_REL 42.
  - Those 42 are complete transfers at normal about .57-.62 (swap about 1 - normal). The absolute rule can never call these FLIP, however many worlds are used.
- Census of the 249 groups (site_all/channel_all SINGLE):

| Class | Groups |
|---|---|
| UNRESOLVED | 69 |
| UNDEFINED | 62 |
| SITE | 45 |
| IDENTITY-BROKEN | 34 |
| MIXTURE | 17 |
| NEITHER | 12 |
| CHANNEL | 10 |

- Predictions vs outcome (PLAN): FLIP 30±10% -> 12.3%, NO-EFFECT 15±10% -> 3.8%, CHANCE 55±15% -> 83.9%. All three missed. Readable FLIP predicted ~40%, observed 7.9%; unreadable FLIP predicted <= 10%, observed 21.4%.

KNOWN-ANSWER CHECKS (+ must-fail inputs); all PASS
- KA1 W-L champion n1_s3 (M=512, ns 0x601, offset -1): normal .716; S and site_all FLIP (.270 [.253, .284]); channel_all NO-EFFECT.
  - Must-fail: the FLIP check fed channel_all gives NO-EFFECT, so it fails as required.
- KA2 pure latch plants.plant("hold_latch") on the 4ab2ba01 physics/env, mid offset: site_all FLIP (swap .000); channel_all NO-EFFECT.
  - Caveat: this NO-EFFECT is trivial, because the plant sends no packets.
  - Must-fail: the NO-EFFECT check fed site_all gives FLIP.
- KA3 latch site_all swap in a fixed random half of the pairs gives CHANCE (.4375 [.359, .520]).
  - Must-fail: swapping all pairs gives FLIP, not CHANCE.
- KA4 fork runner vs lens_swap.run_arms SINGLE: normal, site_all, channel_all, S and pay0 bit-identical; lens_swap.selfcheck all True.
  - Must-fail: forking at offset+1 is not identical.
- KA5 all 733 recorded CIs re-derive CHANCE under the rule.
  - Must-fail: a synthetic swap hi of .39 does not read CHANCE.
- KA6 re-running at the original design (64 worlds, original namespace, EVERY) reproduces the recorded swap accuracy exactly for W-F mid, W-F pre, W-I S and s_ct sitestate.
  - Must-fail offset+1: not reproduced for 3 of 4. For W-F c939c3c7 (offset 9 -> 10) it did reproduce, because that swap is time-invariant, so that one must-fail does not discriminate.
- The re-derivation code reproduces the recorded W-F class 166/166 and the W-I reader/sub_chance/sub_flip 135/135 from the recorded verdicts.

PROPOSED RECORD CORRECTIONS (not applied; full lists in out/corrections_WF.csv and out/corrections_WI.csv)

Rule D3: re-run verdicts replace only the CHANCE arms; the record's own rule re-derives the reading; readability uses the recorded normal.

W-F census_table.csv class / class_late (row = csv line):

| Cell | Row | Change |
|---|---|---|
| 0187372b | 3 | ELSEWHERE -> SITE |
| 11f3ac85 | 4 | ELSEWHERE -> SITE |
| 83d9d7b5 | 5 | ELSEWHERE -> SITE; late ELSEWHERE -> SITE |
| 42716814 | 124 | ELSEWHERE -> JOINT; late -> SITE |
| d3c0d182 | 125 | ELSEWHERE -> JOINT |
| 2dccdaa5 | 127 | JOINT -> SITE |
| 8c37f32e | 132 | JOINT -> SITE |
| c16d5231 | 135 | JOINT -> SITE |
| 8743da7f | 106 | JOINT -> CHANNEL |
| 4781b0a1 | 105 | late ELSEWHERE -> SITE |
| cc18858f | 70 | late ELSEWHERE -> SITE |
| cdf60380 | 71 | late ELSEWHERE -> SITE |
| bf82cb29 | 121 | late ELSEWHERE -> SITE |

- The source lines are in census_s0/s1.jsonl (listed in the CSV).
- Where the record ran no joint arm for a changed cell, the CSV notes it.
- If readability is also re-evaluated at M=512, 12 more UNREADABLE cells get a class:
  - SITE: c868a87b, ed884172, e2fa0531, 9dd25cb2, 0017d8cc, 7ca102eb, b4e404f6.
  - CHANNEL: 88f94654, 57650798, 4ba2a869, 8a8e65ad.
  - JOINT: a395784b.

W-I table_<cell>.csv reader letter (line = offset + 3):

| Cell | Offsets | Change |
|---|---|---|
| 369f5a5b | o2, o14, o15 | J -> S |
| 4781b0a1 | o5, o15 | J -> S |
| 4781b0a1 | o11 | M -> C |
| 4781b0a1 | o14 | J -> C |
| 613162a3 | o9 | M -> S |
| c16d5231 | o5 | M -> S |
| cd5b6fd6 | o6 | M -> C |
| 8c37f32e | o5 | J -> S |

- 20 W-I rows change sub_chance/sub_flip; see the CSV.
- On 42716814 (unreadable '?' at 64 worlds, normal .63 at 512), S becomes FLIP at o14 and o15.
- Motif strings in W-I motifs.json and REPORT built from these letters should be re-derived.

W-E class (from s_ct): no change. c16d5231 sitestate and 4781b0a1 inflight/sitestate/payload all stay CHANCE at M=512.

DISAGREEMENTS
1. With W-N's generalisation, as read from its RESULTS section: its CHANCE->FLIP pattern does not extend to the records at large.
   - It holds for HOLD (44%) and for W-F site_all/joint (about 23%), which is where W-N looked.
   - Across all 733 recorded CHANCE verdicts, 84% remain CHANCE at M=512 under the same rule, and only 8% of readable ones flip.
   - Most recorded CHANCE verdicts are real partial or mixed effects: census UNRESOLVED/IDENTITY-BROKEN/MIXTURE, and relative CHANCE_REL or INDETERMINATE.
2. With my own PLAN: all three predicted proportions missed. The "unreadable -> CHANCE" prediction was wrong because 64-world normal lo99 understates accuracy; half of those specimens are readable at 512.
3. With the recorded "UNREADABLE" labels in W-F: 12 of these cells get SITE/CHANNEL/JOINT at M=512. The .60 gate at 64 worlds removed real carriers from the census.
4. The absolute rule remains blind at low accuracy. 42 absolute-CHANCE verdicts are gated FLIP_REL (complete transfer, normal about .57-.62). Sample size alone cannot fix these; W-N's relative rule is needed.

LEASES
- Fabric skullport:cpu8 --as Ananke, lease lse-9ef8ebed677c (token d53cf0dbcfa75e96).
  - Acquired 06:59:39Z, renewed 07:18Z (ttl 7200 s), RELEASED 09:14Z.
  - `python -m fabric lease status` afterwards shows no lse-9ef8 entry.
- No GPU used. All audit processes were stopped; running-process count is 0.

FILES (roles/Ananke/research/workers/W-O/)
- PLAN.md, LOG.md
- Scripts: inventory.py, runner.py, selfcheck.py, audit.py, coverage.py, ka_repro.py, ka_plants.py, summarize.py
- Inventory: out/inventory.csv, out/inventory_counts.json
- Checks: out/selfcheck.json, out/ka_repro.json, out/ka_plants.json (+ .log)
- Re-run records: out/rerun_s*.jsonl (per group; `*r` files are the tail helpers)
- Tables and summary: out/rerun_table.csv (per verdict), out/summary.json, out/summary.txt
- Proposed corrections: out/corrections_WF.csv, out/corrections_WI.csv
- Shard logs: out/audit_*.log
