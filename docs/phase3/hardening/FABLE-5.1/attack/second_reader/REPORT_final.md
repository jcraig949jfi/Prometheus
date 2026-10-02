# Report of the second reader on version three

Verbatim, as it was returned.

21 HTML entities put in by the notification wrapper were turned back into their characters. Nothing else was changed.

---

FINAL CLOSURE READ OF VERSION THREE (second reader, alone, read-only)

All 8 blockers are closed. Of the 38 majors, 33 are closed, 5 partly, none open. New: 1 blocker, 5 majors, 9 minors. At first sight the tests missed 20 of 54 changes; 2 of those alter no verdict.

Nothing under F:\Prometheus-worktrees\ or F:\prometheus was written, and no __pycache__ was left. Scratch is ...\scratchpad\verify6\. In place I ran only check_hardening.py with the three flags: 49 checks, 1 failed (the placeholder check).

Abbreviations: D1, D2, D3 = the three documents; RM = 00_README.md; HR = harness/README.md. Code paths are under harness/rso_harness/.

## 1. FIRST-SIGHT SCORE OF THE TESTS

Order kept. Before writing the list I read only harness/rso_harness/*.py of version three, plus my own two earlier sets from my scratch so as not to copy them.
- The list of 54 changes over all eleven modules was hashed at 10:23:04 UTC (sha256 b0dad416...), before tests/test_harness.py or mutation_probe.py of version three were opened.
- The test file has still not been opened. mutation_probe.py was opened after the run, to look for overlap.
- Three search.py patterns did not match on the first run (my indentation). I corrected the whitespace, not the change, and ran them before opening the probe.

    changes 54 | noticed 34 | unnoticed 20 | of the unnoticed, alter no verdict: 2

So 18 of 52 changes that alter a verdict went unnoticed.

After the run, 5 of my 54 proved identical to closure-reader changes already in the probe (C03, C11, C18, C43, C44). Without them: 49 changes, 30 noticed, 19 unnoticed, 1 with no verdict change, so 18 of 48.

Per module (changes/unnoticed): stats 7/1, registration 6/1, verdict 3/0, rulers 4/1, torture 4/4, search 6/3, audits 10/3, claims 4/3, ladder 3/0, retain1 3/1, meta 4/3.

Unnoticed changes. Each witness is one input, original verdict -> changed verdict.

| id | file | change | witness |
|---|---|---|---|
| S03 | stats.py | G2 negative's probability taken without min(no, k-1) | NO VERDICT CHANGE (proof; 2,730 inputs identical) |
| G04 | registration.py | an empty list or dict counts as a registered field | registered_seeds=[]: BLOCKED -> PASS |
| U03 | rulers.py | interchange calls an undecided count NEGATIVE | scripted(143) as impostor, 32 seeds: INDETERMINATE -> PASS |
| T01 | torture.py | reset does not compare the final mark | NO VERDICT CHANGE (same as C18; a write at the last step is the answer) |
| T02 | torture.py | restart skips the step right after the cut | a two-slot echo that capture omits: FAIL -> PASS |
| T03 | torture.py | restart makes no cut after the first step | capture wrong right after the cue step: FAIL -> PASS |
| T04 | torture.py | observer runs the first six seeds only | an observer that disturbs from the seventh episode: FAIL -> PASS |
| R01 | search.py | founders compared as a set | registered founders reversed, one repeated: FAIL -> PASS |
| R02 | search.py | fewer hits reported than the replay finds | FAIL -> PASS |
| R06 | search.py | a null from one neutral policy | BLOCKED -> PASS |
| A01 | audits.py | under 22 replicates no arms merge | 12 identical replicates: FAIL -> PASS |
| A02 | audits.py | a pair of identical arms is tolerated | FAIL -> PASS |
| A10 | audits.py | a member run here and elsewhere is "not run here" | PASS -> UNQUALIFIED |
| C01 | claims.py | the opening clock is not type-checked | 20.5: BLOCKED -> PASS |
| C03 | claims.py | the setting hash depends on key order | PASS -> FAIL |
| C04 | claims.py | an empty string counts as a custody field | BLOCKED -> PASS |
| W02 | retain1.py | the final state holds no mark | observer marking after the last step: FAIL -> PASS |
| M02 | meta.py | a sound case refused as BLOCKED is no false accusation | GM FAIL -> PASS |
| M03 | meta.py | the missing-field mutant tries eight fields only | on a gate that drops "adapter": PASS(open) -> BLOCKED |
| M04 | meta.py | the kind-facet mutant tries three kinds only | on a gate that drops ORIGIN's class bound: the same |

## 2. CLOSURE

Blockers.

| # | status | where | note |
|---|---|---|---|
| B1 | CLOSED | D2:327-336, D3:461-467, D2:191-192 | The author's table reproduces and equals the receipt. My 392-recombination cache scores 13.78 / 3.44 and is called COMBINED, as the text now says. |
| B2 | CLOSED | D2:758-764 | It can fire, and its first clause does fire in one variant (new blocker N1). |
| B3 | CLOSED | D3:104-110, HR:53-56 | |
| B4 | CLOSED | audits.py:199-249, 294-296; D2:574-580 | 26 rows = 26 receipt cells; bits and guards are read, not the label; no reuse verdict. |
| B5 | CLOSED | torture.py:10-15, 183-216; retain1.py:439-441; D3:280-288 | |
| B6 | CLOSED | search.py:142-176; meta.py:593-600 | Residual in N4. |
| B7 | CLOSED | torture.py:112-126; meta.py:519-522 | Residual in N6. |
| B8 | CLOSED | D1:435-438 | |

Majors.

| # | status | where | note |
|---|---|---|---|
| 9 | CLOSED | D3:432-435, D2:307-310 | |
| 10 | CLOSED | D2:307-310, 329-333 | Sentence removed. |
| 11 | CLOSED | D2:261-270, 272-278 | Rule removed. |
| 12 | PARTLY | D2:312-315; ladder.py:294-323 | The control catches the author's sandbagger and a plain hider. A hider that watches for repetition passes (N1). |
| 13 | CLOSED | D2:269-270, D3:469-470 | |
| 14 | CLOSED | D2:333-335 | |
| 15 | PARTLY | D3:468-479; audits.py:261-264 | The list now names the setting, content reset, kit and drawn pair. ELIM, TWO_TABLES and SANDBAGGER are not registered. |
| 16 | CLOSED | D2:272-278, D1:556-562, D2:195-197 | |
| 17 | CLOSED | D2:285-293, D1:309-324 | |
| 18 | CLOSED | D2:17-18, 206-207; claims.py:133-136; D3:184-186 | |
| 19 | CLOSED | audits.py:213-215; D2:574-580 | |
| 20 | PARTLY | D3:14-19, 522-525 | Counts fixed. D3:114-115 is still false (N2). |
| 21 | CLOSED | torture.py:147, 172; meta.py:531, 549-550 | |
| 22 | CLOSED | torture.py:114-115, 137-138, 161-162; search.py:117-118 | |
| 23 | CLOSED | search.py:128-139 | |
| 24 | CLOSED | stats.py:125-130; registration.py:46-67; D2:377-383 | |
| 25 | CLOSED | registration.py:121-122; meta.py:814-817 | |
| 26 | CLOSED | rulers.py:26, 116-129; D2:424-433 | Bracket 0.342 to 0.686 and thresholds within 0.001 verified. |
| 27 | CLOSED | rulers.py:40-72; meta.py:485 | |
| 28 | CLOSED | search.py:178-179, 195-199; meta.py:573 | |
| 29 | PARTLY | claims.py:59-61; meta.py:883-903 | Still passing and unlisted: ruler rows pointing at another cell; arms with constant offsets. |
| 30 | CLOSED | D3:92-97; D2:138-141; attack/README.md | |
| 31 | PARTLY | check_hardening.py; RM:103-113 | With pins off, 13 of my 18 fresh plants pass: swapped row labels in the D2 section 5 table, FAILS -> PASSES, yes -> no, an attribution, "no ruler has been checked" -> "a ruler has". All digit plants are caught. |
| 32 | CLOSED | D1:93-96, 132-134 | |
| 33 | CLOSED | D3:483-487, D1:594-597 | |
| 34 | CLOSED | D1:230-236 | |
| 35 | CLOSED | D1:242-245 | |
| 36 | CLOSED | D1:127-128, 257-258 | |
| 37 | CLOSED | D1:165-166, 218-220; RM:49-50 | |
| 38 | CLOSED | D2:127-130; D1:408-413 | |
| 39 | CLOSED | D2:348-351; D1:489-490 | |
| 40 | CLOSED | D1:376, 404-406 | |
| 41 | CLOSED | D1:106-113 | |
| 42 | CLOSED | D1:419-422 | |
| 43 | CLOSED | D1:16-20, 299-324; RM:45-48 | |
| 44 | CLOSED | RM:121-157 | |
| 45 | CLOSED | D1:453-456; D2:138-141 | |
| 46 | CLOSED | D2:748-753 | |

Re-runs for B1, B2 and majors 9 to 15.
- **My comp.py organisms under the new control (300 lives).** Same-table 3.47/3.48, same-move 3.51/3.49, two-table products 3.49/3.43, xor cache 3.52/3.50, affine cache 3.39/3.51: all NOT_SHOWN. The 392 cache 13.78/3.44, one table plus one acquired relabelling 16.00/3.49, and the hard-wired formula 16.00/3.49: all COMBINED. A composer keeping 2 entries scores 5.27 and is NOT_SHOWN.
- **Excluded class.** Correct as stated for guesses that depend on a non-linking set (proof). The cache over all eight tables is measured at 3.382 +/- 0.009 over 24,000 lives, not derived (N15).
- **My version-two sandbagger.** It can no longer tell the arms apart, so the control catches it.

## 3. DEFECTS STILL OPEN OR NEW

**BLOCKER**

N1. D2:312-315, D3:478-479, ladder.py:306-312. Falsifier 6 fires in one variant of the planted fault.
- REPEAT_WATCHER keeps last life's nine tables and uses the kept ninth only if this life's eight repeat them. It combines nothing.
- With only the life's own key reused and the control's key drawn per life, it scores 15.96 on the ninth pair and 3.46 in the control: COMBINED.
- With both keys reused, as the author's fire test plants it, it is caught (15.96 / 15.96). With no fault it is NOT_SHOWN.
- So "cannot tell the two arms apart" holds within a life, not across lives.
- Fix: plant both variants; say the control guards only against a leak that reaches both arms alike; add a custody check that each life's key is fresh (hash every key, none repeated); state in D2 section 19 that the first clause of falsifier 6 was met once, in an exploratory run.

**MAJOR**

N2. D3:114-115, D2:151-153. "What was found is a registered mutant or a known escape" is still false. At least 12 faults my forks reported on version two still PASS and are neither registered nor among the 24 (marked "v2" in section 4). Fix: register or list them, or write "most".

N3. audits.py:36-47, 111-126; D3:290-300. A sham that changes nothing (sham == intact in 24 of 24) gets G9.sham PASS and G9.arms FAIL. The sound fixtures avoid it (meta.py:252, 659). Fix: exempt the registered sham/intact pair from G9.arms, or state the requirement.

N4. search.py:142-176; D3:270-272; D2:494-496. "Replays the registered search": only the founders are registered. Budget, policies, start law, distance and landscape are the report's own; a discovery at a budget chosen afterwards (2,000) passes. Fix: pass the registered cell and compare, else BLOCKED.

N5. registration.py:73, 84-95; D3:201-205. `registered_seeds=()` PASSES, so "one registered seed per unit" is false for it. A design seed "5000" beside 5000 passes. Every descriptive field "tbd" passes. Fix: require a non-empty list of integers, compare n with len(seeds) unconditionally, refuse the placeholder words.

N6. meta.py:155-161, 504-522; D3:251-254. Observer equivalence is run on the four positives only. An observer that disturbs only impostors and the weak positive passes, and FAILs when run on an impostor. Fix: run it on every organism the observer will watch, or state the scope and list the escape.

**MINOR**

N7. audits.py:17, 92-96; D3:294-297. Clause thresholds are absolute counts. With 240 replicates, clauses "holding" in 22 of 240 PASS; the sound toy at 12 replicates is UNQUALIFIED. Fix: BLOCKED unless every cell has 24 replicates.

N8. audits.py:311-319. STRONG passes from two rows that point at run 4's key cells. Fix: list beside meta.py:889-891.

N9. torture.py:228. Baselines are required by name. A constant entered as WORLD_PARKER passes a world that keeps what is written. Fix: list.

N10. search.py:210. A null with bound 1.0 or True passes. Fix: refuse booleans and a bound of 1.

N11. registration.py:108-135. A receipt passes against a cell that G1.cell blocks. Fix: call check_cell first.

N12. claims.py:63. Text seeds "1","2","3" against integer 1, 2, 3 pass.

N13. claims.py:134. An excluded class or a cell of one space renders. Fix: strip, as claims.py:99 does for sources.

N14. registration.py:74; rulers.py:148-150. Design seeds as a tuple are BLOCKED. A sound pair given through functools.partial gets FAIL, not BLOCKED.

N15. D2:307-310. Say "measured" for the row of the cache over all eight tables.

To fill FINAL_READ_PLACEHOLDER at D3:604, HR:69, RM:159 and D1:616: version three, at first sight, 20 of 54 unnoticed, 2 of them without a verdict change.

## 4. NEW PASSING FAULTS BY GATE

None is in meta.known_escapes(). Each is a broken case that PASSES on the unchanged copy. "v2" = already reported on version two.

| gate | case | |
|---|---|---|
| G1.cell | registered_seeds=() | v2 |
| G1.cell | design seed "5000" beside registered 5000 | v2 |
| G1.cell | every descriptive field a placeholder | v2 |
| G1.receipt | a receipt checked against a blocked cell | v2 |
| G4.entry | a "positive" right in its first 64 episodes and wrong after | v2 |
| G6.observer | disturbs only impostors and the weak positive | v2 |
| G7.calibration | right on the five cells at budget 400, reports 0 elsewhere (0 of 256 where exact reach is 1.0) | new |
| G7.report | a budget of the report's own choosing | new |
| G7.report | bound 1.0 or True | v2 |
| G8.demand | a constant under the name WORLD_PARKER | v2 |
| G9.arms | three computations as eight arms with constant offsets | v2 |
| G9.clauses | 240 replicates, "holds" at 22 of 240 | v2 |
| G10.ruler | STRONG from rows pointing at run 4's key cells | v2 |
| G11.custody | text seeds against integer seeds | v2 |
| G12.render | excluded class of one space; a cell of one space | v2 (cell) |
| world two (not a gate) | REPEAT_WATCHER called COMBINED (N1) | new |

Sound cases refused: an exactly neutral sham (G9.arms FAIL, N3); the sound toy at 12 replicates (G9.clauses UNQUALIFIED); design seeds as a tuple (G1.cell BLOCKED); a functools.partial pair (G4.entry FAIL).

Statements in D2 or D3 about what a gate catches that are false: D3:204-205 (N5), D3:270-272 and D2:494-496 (N4), D3:114-115 (N2), D2:313-314 (N1). The rest are narrower than the reader might assume, not false.

Checked and true: attainability 0.9985, 0.9897, 0.8715; positive control 0.0107, 0.8126, 0.9896, 0.9909; 21 gates, 48 sound, 215 mutants split 108/78/22/7; five gates compute INDETERMINATE; KEEPER is CARRIED at 4,000 lives (4.058 against 4.046); the six survivors of the author's probe alter no verdict.

## 5. WHAT I DID NOT CHECK

- tests/test_harness.py was not read; I saw only the test names that failed.
- run_harness.py and fire_test.py were not run. I read fire_test.py's plant list only.
- The closure reader's report and scripts, and attack/second_version, were not re-run.
- The new statements about B, C and O were not re-checked line by line against the sources. I compared them with my notes from the first read, and the checker found all 58 quotations verbatim. The Enceladus worktree was not opened this time.
- D1 sections 6, 9 to 12 and D2 sections 6 to 16 were read once, for closure only.
- Readability on a phone, the pins, the placeholders and the MANIFEST files were left out, as instructed.
- Whether the bound is exact for a cache that selects among fixed re-indexings of all eight tables: measured, not proved.
- No gate was attacked beyond the cases in section 4.
