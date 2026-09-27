# SNAPSHOT_SOURCES -- pre-final numbers quoted for the BELLEROPHON Z80 x Atlas campaign

Compiled 2026-09-23 (read-only research; nothing in the repo, worktrees or campaign workdir was modified).
Authoritative final: C:\Users\James\z80atlas_campaign_2026-09-19\CAMPAIGN_PACKET.md
(start 2026-09-19T14:39:46Z, stop 2026-09-22T14:38:42Z; 63,247 runs / 49,412 families / 31,196 promoted /
18 retired / 15,614 specimen archive / 1,629 high-value flags).

## 1. Headline finding

The "44.6-hour snapshot" and the "276 replication flags" figure are NOT in git on any ref searched.
They exist only in the Claude Code transcript of the Bellerophon seat session:

    C:\Users\James\.claude\projects\D--Prometheus\c95cc146-61b5-4b8e-bbff-902630a045cc.jsonl
      line 7285  2026-09-21T11:17:20Z  tool result: `campaign --status` JSON
      line 7288  2026-09-21T11:17:33Z  tool result: flag/trigger breakdown ("elapsed: 44.6h ... spontaneous_replication fires: 276")
      line 7290  2026-09-21T11:17:43Z  assistant summary table ("44.6h in, 27.4h remaining")

"276" is the count of runs whose mechanical TRIGGER `spontaneous_replication` fired (runs.jsonl lines at read time).
It is NOT a high-value flag class (the five flag classes are REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL,
REPRODUCTIVE_MACHINERY_RAISED_BENEFICIAL_DENSITY, REPRODUCTIVE_ARCHITECTURE_RESPONDED_TO_TASK,
REACHED_INCREMENTAL_NOT_ATOMIC, RESERVOIR_CROSSED_MOAT). The operator directive's phrase "276 replication flags"
(roles/Bellerophon/prompts/2026-09-23_post_campaign_forensics/00_OPERATOR_DIRECTIVE_verbatim.md:119 on
origin/bellerophon/post-campaign-forensics-2026-09-23, commit f17292833) is therefore a RELABEL of a trigger count.
It is also distinct from the broader `replication` trigger (6,510 runs at 44.6h; 18,647 final).
Final value of the same quantity: 544 runs / 471 families (CENSUS.json run_triggers.spontaneous_replication).
Reconstruction from final runs.jsonl (ingest order): 275 at line 37,732 -- matches 276 within the +/-1 expected
because runs.jsonl is written before state.json and the breakdown was read 13 s after the status call.

## 2. Every pre-final Bellerophon number found (chronological)

Elapsed hours computed from start 2026-09-19T14:39:46Z. All from transcript c95cc146 (Bellerophon[m2-c95cc146])
unless stated. "Snapshot" = mid-campaign; nothing below is a final value except row F.

| id | source (line) | UTC | elapsed | quoted values | campaign | snapshot/final |
|---|---|---|---|---|---|---|
| S0 | c95cc146 L7074, L7098 | 2026-09-19T14:43:38Z | 0.06h | runs 36, fam 35, promoted 13, flags 0; test --finalize packet: runs 59 fam 58 promoted 13 specimens 9 (packet written to a TEMP dir, not the workdir) | Bellerophon | snapshot (launch smoke) |
| S1 | c95cc146 L7154 | 2026-09-19T15:57:45Z | 1.30h | runs 1,060 (1,089 in runs.jsonl), fam 1,059, promoted 546, flags 15, extinct 320, spont-repl 7, exploits 76, disk 180 MB | Bellerophon | snapshot |
| S2 | c95cc146 L7168 (tool), L7173 (summary) | 2026-09-20T02:45:48Z | 12.10h | runs 10,084, fam 10,078, promoted 4,792, flags 108 (76 RUE / 19 RMBD / 11 RART / 2 RINA), spont-repl 59 (37 COPY/12 PARTIAL/7 PAIR/3 OVERWRITE), extinct 3,067/10,110, exploits 733, disk 1.6 GB | Bellerophon | snapshot |
| S2b | same S2 numbers repeated in compaction summary c95cc146 L7199 | 2026-09-20T09:18Z | (refers to 12.10h) | "10,084 runs, 108 flags ... 59 spontaneous replication runs" | Bellerophon | snapshot (restated) |
| S3 | c95cc146 L7231, L7255, L7264, L7267 | 2026-09-20T09:18:23Z | 18.64h ("18.7h") | runs 15,556, fam 15,536, promoted 7,294 (state says 0 -- see A3), flags 169 (124 RUE / 25 RMBD / 18 RART / 2 RINA); RUE by task INC29 CONST25 COND_ONE20 ECHO19 COND_MULTI16 SUM2 15; triggers cross_niche 8,688, moat 5,590, escape 2,732, task_score 1,854, novelty 1,740, novel_arch 1,578, replication 1,431, coexistence 1,369, persistent 1,229, exploit 1,124, repro_compression 664, env_lineage 239, task_repro_coupling 169, spontaneous_replication 84, persistence_above_control 1; "SPONTANEOUS REPLICATION total 5,854" (see A2); extinct 4,737; gains min .125 med .475 max .975 | Bellerophon | snapshot |
| S4 = "44.6h snapshot" | c95cc146 L7285, L7288, L7290 | 2026-09-21T11:17:20Z | 44.63h | runs 37,732, fam 33,333, promoted 18,309, retired 0, counters control 10,301 / exploration 15,144 / promoted 12,283 / verification 0 / intervention 0, flags 446 (185 RUE / 119 RMBD / 104 RART / 33 RINA / 5 RCM); RUE by task CONST39 INC39 ECHO36 COND_ONE26 COND_MULTI25 SUM2 20; triggers cross_niche 23,476, moat 15,497, escape 7,262, novel_arch 6,996, novelty 6,751, replication 6,510, task_score 5,098, persistent 4,625, coexistence 3,999, exploit 3,199; **spontaneous_replication fires 276**; run_wall_ema 69.5 s; stage MIDDLE (LATE not yet reached) | Bellerophon | snapshot (pre-LATE: 0 verification, 0 intervention runs) |
| F | c95cc146 L7307, L7310, L7312 | 2026-09-22T19:56:18Z | 71.98h (stop) | runs 63,247, fam 49,412, promoted 31,196, retired 18, flags 1,629 (600 RART / 493 RMBD / 393 RUE / 136 RINA / 7 RCM), verification 10,667, intervention 3,808; RUE by task ECHO108 INC72 CONST68 COND_ONE68 COND_MULTI47 SUM2 30; gains max 1.000 | Bellerophon | FINAL (matches packet) |
| X1 | c95cc146 L7525 (operator paste of an external reviewer's text) | 2026-09-23T01:39:30Z | refers to 44.6h | "I'm not going to pretend the 44.6-hour checkpoint is the final campaign ... latest BEE-specific campaign state we had before LATE verification ... excluding the Nestor replication campaign entirely." | Bellerophon (explicitly) | snapshot-based external analysis (no numbers in the paste; the reviewer's full analysis is not in any local file found) |
| D1 | origin/bellerophon/post-campaign-forensics-2026-09-23 (f17292833): roles/Bellerophon/prompts/2026-09-23_post_campaign_forensics/00_OPERATOR_DIRECTIVE_verbatim.md:30, :119, :617 | 2026-09-23 | refers to 44.6h | "previously discussed 44.6-hour snapshot"; "not merely '276 replication flags'" | Bellerophon | snapshot reference (value 276 = S4 trigger count, relabelled "flags") |
| D2 | same ref: roles/Bellerophon/STATUS.md:10-15 | 2026-09-23 | final | "63,247 runs / 49,412 families / 1,629 high-value flags ... DO NOT mistake earlier 44.6h snapshot numbers" | Bellerophon | final (correct) |

Abbrev: RUE=REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL, RMBD=REPRODUCTIVE_MACHINERY_RAISED_BENEFICIAL_DENSITY,
RART=REPRODUCTIVE_ARCHITECTURE_RESPONDED_TO_TASK, RINA=REACHED_INCREMENTAL_NOT_ATOMIC, RCM=RESERVOIR_CROSSED_MOAT.

Final equivalents for S4 quantities (CENSUS.json in D:\Prometheus-worktrees\bellerophon-post-campaign-forensics\roles\Bellerophon\forensics_2026-09-23\receipts\):
spontaneous_replication 544 runs/471 fam; replication 18,647; cross_niche 42,995; moat 30,470; escape 12,872;
novel_arch 19,253; novelty 15,614; task_score 11,686; persistent 9,675; coexistence 7,177; exploit 6,437.

## 3. Git-committed Bellerophon numbers (all refs searched)

- 2df98af3e roles/Bellerophon/STATUS.md (2026-09-19T14:45Z): launch config only (16 workers, 500 ticks x 256 cells,
  seed 20260919, positive controls 5/5). No run/flag counts. No mid-campaign STATUS commit exists
  (next STATUS commit is f17292833, post-campaign).
- 98b2149a7 / 16fc6c2a2: harness + patch; no campaign numbers.
- f17292833 (origin/bellerophon/post-campaign-forensics-2026-09-23): D1, D2 above.
- Untracked in worktree bellerophon-post-campaign-forensics: forensics_2026-09-23/EVIDENCE_MANIFEST.md and
  receipts/CENSUS.json -- final-only numbers, consistent with packet.
- No Bellerophon snapshot file in C:\Users\James\z80atlas_campaign_2026-09-19\ (only final artifacts; stdout log
  holds the stop record: runs 63247, families 49412).

## 4. Other campaigns' numbers that could be confused (NOT Bellerophon)

| campaign | source | numbers |
|---|---|---|
| Archaeon | archaeon/z80atlas/campaign/CAMPAIGN_DONE.json, CAMPAIGN_PACKET.md, pivot/Z80ATLAS_REVIEW_2026-09-22.md (d50f5710a, merged bcb9f22ad) | done_at 2026-09-22T13:55:58Z, runs 101,003; 26 spontaneous_replication verification runs (all transplant-derived per roles/Archaeon/prompts/2026-09-23_z80atlas_postcampaign/00_OPERATOR_DIRECTIVE.md:39-51); score-17 families 2ace470e5c47/5b237a475b69/e8394eee206d |
| Nestor | roles/Nestor/campaigns/z80atlas-2026-09-19/observatory/PACKET.md (3b407946e) | runs 23,471, families 20,638, crossed 7,092, replicated 5,309, spontaneous replication runs 1,031, specials 1,221, specimens 41,402 |
| Archaeon (unrelated) | archaeon/frontier/digests/EPOCH_2026-09-21T2054Z.json:4374,4769,6264 | "COMPLETE": 276 / "FULL": 276 -- a coincidental 276 in Archaeon's WSE frontier epoch digest (bcb9f22ad); not Z80 x Atlas, not Bellerophon |

Neither Archaeon nor Nestor contains a 44.6h figure or a 276 replication count.

## 5. Attribution / consistency anomalies to flag

- A1 (attribution error, in git): 2df98af3e roles/Bellerophon/STATUS.md says "archaeon/z80atlas/ (Nestor's own build)
  landed on main the same hour". archaeon/z80atlas/ is ARCHAEON's build (c7610ea19, DF-016); Nestor's is
  roles/Nestor/campaigns/z80atlas-2026-09-19/ (aa5833488). Any reader following this line would cross-wire the campaigns.
- A2 (two predicates called "spontaneous replication"): at 18.7h the transcript printed both
  "SPONTANEOUS REPLICATION total 5,854" (= runs whose first_replication.seeded is False) and trigger
  `spontaneous_replication` = 84. Reconstruction from final runs.jsonl confirms: at 15,585 lines, unseeded
  first_replication = 5,854 and trigger = 84; at 37,732 lines 15,638 vs 275; final 24,458 vs 544. The 276 / 544
  series is the TRIGGER; do not mix with the unseeded-first-replication series.
- A3 ("promoted" means two things): status JSON "promoted" = families promoted (7,294 at 18.7h; 18,309 at 44.6h;
  31,196 final) while counters.promoted = runs of kind promoted (0; 12,283; 19,095). The 18.7h tool output also
  printed "promoted: 0" from state (the counter), contradicting 7,294 from --status.
- A4 (mislabelled comparison columns): the 18.7h summary (L7267) labels the 12.1h values "+7h" (actually 6.5h earlier)
  and attributes "promoted 4,792" to that column; the 44.6h summary (L7290) labels 12.1h values "+7h" (actually
  32.5h earlier) and 18.7h values "+26h"; the final summary (L7312) labels 44.6h values "at 44h".
- A5 (stage-boundary predictions inconsistent): 1.3h message says LATE at 80% ~57.6h; 44.6h message says LATE at
  "72x70% = ~50.4h -> ~17:05Z". Actual LATE start 2026-09-22T00:18:00Z = 57.64h (stage_log). The 44.6h prediction
  was wrong; S4 is firmly pre-LATE (0 verification runs), so every S4 flag count is pre-verification.
- A6 (flag-class counts at 44.6h not reconstructable by prefix): flags.json order is not append order -- its first
  446 entries give 199/102/112/29/4, not the 185/119/104/33/5 printed live. The S4 flag-class split is therefore only
  attested by the transcript tool output, not by a prefix of final evidence. (The trigger count 276 IS reconstructable.)
- A7 (flag growth is dominated by LATE verification): RART 104 -> 600 and RMBD 119 -> 493 between 44.6h and final;
  per-6h flagged-run windows (CENSUS) jump to 109/226/130 and 68/175/93 in the last three windows, i.e. LATE-stage
  exposure, not a rising discovery rate at fixed exposure.

## 6. Places searched with no Bellerophon snapshot numbers

git refs main, origin/main, origin/bellerophon/post-campaign-forensics-2026-09-23, origin/archaeon/wse-2026-09-16,
archaeon/z80atlas-postcampaign-2026-09-23 (paths roles/, archaeon/, docs/, prometheus/z80atlas/); commits 2df98af3e,
d50f5710a, bcb9f22ad, 3b407946e, 16fc6c2a2, 98b2149a7; roles/Archaeon journal/TODO/prompts; roles/Nestor
STATUS/FINDINGS/campaign; roles/Atlas journal/proposals (mention Bellerophon only as a candidate engine);
D:\Prometheus-worktrees\* (only bellerophon-post-campaign-forensics has untracked z80/Bellerophon files);
C:\Users\James\z80atlas_campaign_2026-09-19\ (final artifacts only).
Other Claude transcripts containing "44.6"/"z80atlas_campaign_2026-09-19" (0ee6272b, 14baf7d5, 49ee5a4d, 57e24282,
640acfe6, 6ed01908, 8d43bbf9, db608f52, ef3f0f62) were scanned for the S1-S4 values; see section 7.

## 7. Transcript scan of other sessions

The nine other D--Prometheus transcripts listed in section 6 contain 0 hits for the distinctive S4 strings
(37,732 / 33,333 / 18,309 / "spontaneous_replication fires" / "elapsed: 44.6" / "44.6h" / "44.6-hour" /
"276 replication"); their earlier match was only the workdir path. Project dirs C--Prometheus, D--,
D--Prometheus-worktrees-hephaestus-boot-2026-09-19 and C--Users-James: 0 files match.
Conclusion: transcript c95cc146 is the SOLE origin of every pre-final Bellerophon number. The only downstream
re-quotes are the operator directive (D1: "44.6-hour snapshot", "276 replication flags") and the external
reviewer paste (X1, no numbers). The external reviewer's own snapshot-based analysis is not stored anywhere local.

Reconstruction scripts (read-only against the workdir): scratchpad/snapshots/recon.py, ext.py, dump.py;
transcript extracts c95_status.txt, c95_7195.txt, c95_7291.txt, c95_7505.txt in the same folder.
