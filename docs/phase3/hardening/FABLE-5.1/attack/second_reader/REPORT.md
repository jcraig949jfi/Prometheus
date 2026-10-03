# Report of the second reader, on the second version

Verbatim, as it was returned. It worked with three forks of itself; their reports are beside this one.

Characters outside ASCII were replaced mechanically (1 x U+00B9 as 1, 1 x U+207B as ^-, 2 x U+2218 as o). Nothing else was changed.
1 HTML entities put in by the notification wrapper were turned back into their characters.

---

# Defect list: FABLE-5.1 hardening package, second adversarial read

The package is not ready to commit: 8 blockers. The composition proposal's headline payoff is contradicted by the package's own gate, and its falsifier cannot fire. Three gates pass faults the documents say they catch, and "54 of 55" does not hold for changes the test author did not choose.

Nothing under `F:\Prometheus-worktrees\` or `F:\prometheus` was written; no `__pycache__` was created. Scratch is `C:\Users\jcrai\AppData\Local\Temp\claude\F--prometheus\3815a3b9-a31a-46a9-be9d-0e7abfa3cbf8\scratchpad\verify4\` (`comp\`, `h1\`, `h2\`). Three forks of me covered fairness, gates G1 to G8 and gates G9 to G12. I re-ran every fork finding promoted to blocker, opened the fairness sources at the cited lines for item 8 and the items marked "checked" below, and re-ran a sample of the other harness findings; the rest are as the forks reported them.

Abbreviations: D1, D2, D3 = the three documents; RM = `00_README.md`; HR = `harness\README.md`; AR = `attack\README.md`. A1, A3 = `RESPONSE_1`, `RESPONSE_3`; A-CF = `counterfeit\README.md`. B = ASTRA's report; B-val = its `VALIDATION.md`. C01 to C06 = the package files; O03 = the original design. Harness paths are under `harness\rso_harness\`.

## BLOCKER

1. **D3:446-448, D2:272-274, D3:443-445. "Would give reuse of built parts its first qualified ruler"; "no to a store of whole tables".**
   - The package's own gate disagrees. `ruler_status("REUSE","BITS@PAIRS")` is UNQUALIFIED and stays so with the three composition organisms built and answered correctly. They are registered under COMPOSITION; four REUSE members are unbuilt and five were never run there.
   - A store of whole tables gets a yes. A table cache with 392 inherited recombinations (aob^-1oc over stored tables), chosen by feedback and reading no label, scores 13.81 of 16 (3,000 lives). After three controls it scores 3.41, 3.37 and 3.40.
   - That organism does compose, by blind enumeration. It is also a selector over inherited procedures on memorised tables, and the kit registers both as negatives for REUSE (`audits.py:203-209`).
   - So a yes does not tell choosing from building, which D2:182-184 and A1:1025-1026 call open.
   - Fix: delete the sentence. Say a yes means that information from at least three separately shown families was combined, under claim COMPOSITION, and nothing about how.

2. **D2:695-699. Falsifier 6 cannot fire.**
   - The ninth map is exactly uniform given any set of seen tables that does not connect table 2 to move 2. Proof by re-gauging the component of move 2; confirmed by exhaustive enumeration at 3 symbols (46,656 keys).
   - So "above the bound without combining tables" is impossible in a correct harness, and "without combining" cannot be read from behaviour.
   - It can fire only through a key leak, which the proposed control misses (item 12).
   - This is the fault the first reader named at M34.
   - Fix: falsify on something that can happen, for example a named class of re-indexers fixed before the life scoring above the bound, or a hider passing both arms.

3. **D3:106-108, HR:52-53. "55 changes, 54 noticed".**
   - 25 of the 55 are the first reader's changes, which the tests were then written against (`mutation_probe.py:6-9`); 30 are the author's. The documents do not say so.
   - Two fresh sets: mine, 32 changes, 20 unnoticed (one of the 20 changes no verdict); the fork's, 36 changes, 26 unnoticed. The sets overlap in part.
   - Survivors include:
     - G10.ruler accepts a ruler with no known positive (`audits.py:272`);
     - ORIGIN needs no class bound, and ECONOMY, LAW and L4 need nothing;
     - a receipt on a subset of the registered seeds;
     - attainability floor 0.97;
     - G8 at alpha 1e-3;
     - HOLDS at 20 and FAILS at 16 of 24;
     - a null with one hit;
     - a repair claim from a cold start.
   - Fix: "54 of the 55 changes the tests were written against", and carry the reader's caveat (`REPORT_of_the_reader.md:148`).

4. **D2:519-524, D1:473-476, `audits.py:201-217, 247-248`. Two kit verdicts depend on which receipt rows were typed in.**
   - The only PASS (bits, run 4) reads the label CONSTRUCTED, which A1:1051-1053 withdrew ("read the numbers, not the labels").
   - ACQUIRER(4) and ACQUIRER(8), "certified at 1.44, 9.46" bits by D2:196-197, are read as NEGATIVE. Registering either as POSITIVE turns PASS into FAIL.
   - The registry holds 13 of 26 receipt rows. At run 2 the steps met nine cells, not four.
   - WASTEFUL, HIDDEN, BADSHAM and OFFHISTORY are "BUILDER ..." (`PREREG_gauntlet2.md:100-105`). They reuse built parts by D2:486-487 (medians 23.0 against 417.0, and so on) and got FAIL. Registering any one as POSITIVE turns "UNQUALIFIED" into FAIL.
   - Fix: read certified bits; register every cell with an answer per claim, or state the omissions and why.

5. **`torture.py:10-11`, D3:249-251, D2:457-458. "A fitted table catches any leak that is a function of what the world shows after the cue".** False two ways.
   - The registered xor leak passes at longer gaps: FAIL at gaps 6 and 12, INDETERMINATE at 14, PASS at 16 and 20 (table 1042 of 2048). A policy that xors the two distractors scores 64 of 64 at every gap.
   - `Recorder` keeps only `obs.clock & 1` (`retain1.py:378`). Keeping two bits, the table scores 2048 of 2048 on the "known escape" of D3:516-518. That escape is the recorder's choice, not "a list, not the class".
   - Fix: fit low-order tables; BLOCKED when test contexts were unseen in training; record the whole observation.

6. **`search.py:146-149`, D2:438-439, D3:241-242. "Replays the registered search on the registered seeds".**
   - The seeds are the report's own.
   - A null on NEEDLE from 128 founders kept because the search missed returns PASS; exact reach is 0.7298.
   - Fix: bind the report's seeds to the registered cell.

7. **`torture.py:86-88`, D2:416-418, D3:225-227. Observer equivalence "on a run's own seeds".**
   - Each seed is one episode in a fresh world.
   - An observer that draws from the world's stream in every episode after a world's first returns PASS. As one 12-episode run on the same seeds, 11 episodes differ.
   - Fix: compare a multi-episode run in one world.

8. **D1:389-392. "FROM BOTH".**
   - C is charged with leaving out a gate for a verdict quoted without its setting and a rule that a world filter is registered.
   - Neither review has either. A1:991-993 is a reporting rule, which C carries. A1:843-846 is a finding about A's own run. B:72-76 prescribes custody, which C carries.
   - D2:323-325 itself says "No gate yet".
   - Fix: retitle "NEW IN MY VERSION".

## MAJOR

**Composition certificate and section 5**

9. **D3:429-432.** The bound is exact only for organisms whose carried state is independent of the ninth map. After eight pairs the map is determined by the seen tables, so TABLE_CACHE is outside that class. Its 3.32 is one organism with one 256-member re-indexer, not a bound. No class is named for world two, against D2:229-231.
10. **D2:269-271, "no inherited re-indexing leads to it".** True for re-indexings fixed before the life: rotation and offset 3.39, xor 3.35, affine with 16,384 per table 3.46, two-table products 3.40. False for one that reads the cache: 13.81.
11. **D2:225-231, the corrected rule.**
    - (i) rests on "the counting bound of my review's fourth run", which A1:1013-1017 and A-CF:445-457 withdrew ("a selector with many indices is an acquirer").
    - (ii)'s class as worded contains the cache of item 1, which world two does not exclude.
    - "8 bits" is right, and (i) does disqualify the draft world.
12. **D3:431-432, `ladder.py:164`. The control.**
    - It has six families against eight and a label never met. That is two differences, against D2:318-320, and the organism can tell.
    - With one key reused by the harness (run 4's fire tests B and D), on the author's own code: a hider that uses its inherited answer only after eight families scores 16.00 and 3.36, the composer's exact signature. A plain hider is caught (16.00, 16.00).
    - A history of other keys under the same labels catches the sandbagger (16.00, in my implementation).
    - D2:198-201 names the two controls the bits certificate needs; world two has neither.
13. **D3:437-441, control column.**
    - COMPOSER equals ELIM in 300 of 300 lives. The author's G9.arms returns FAIL "3 arms give 2 distinct series".
    - TABLE_CACHE's equal 3.47 is a chance tie (other seeds: 1044 against 1038).
    - NOT_SHOWN is not "at the bound" (against D2:146-149, 403-405). At 300 lives a composer keeping 2 entries (5.25) is NOT_SHOWN in 40 of 40 runs.
14. **D2:272-274, "by a fixed builder".** True of the designed organism only. A yes cannot say whether the composing step was inherited or acquired in the first eight families.
15. **D3:451-457.** The list omits:
    - the nine choices of D2:297-311 (stored tables are content by A-CF:511-512; with them cleared the positive cannot pass);
    - the REUSE kit at this setting;
    - a control the organism cannot tell apart.

    `audits.py:230-232` registers only the three organisms already simulated; COMPOSITION would PASS on them alone.
16. **D2:235-256, the general point.**
    - "Enough carried content" assumes no bound, while D2:333 and D2:464 mandate an inheritance budget. What the paragraph supports is that a behavioural claim is relative to a class.
    - D2:242-243 ("cannot be defined") contradicts D1:481-484 ("Relative to a registered class it can").
    - D2:160-161 lets the class-relative claim be made this round with no ruler for it.
17. **D2:250-256, D1:283-292, RM:41-42. B's cargo control.**
    - B's question 1 (B:686-690) says intervention-relative, not class-relative. The quoted sentence is one of four in item 4 of six (B:473-494), hedged "where feasible".
    - The supporting line is uncited: B:610 "qualifies only the tested attack classes".
    - "One rule seen from two sides" is the author's reading, not B's.
18. **D2:17, 166-167.** "EVERY CLAIM NAMES THE CLASS IT EXCLUDES" has no field in `claims.render`, no gate, and is not in D3's not-built list. Deleting ORIGIN's class bound goes unnoticed.
19. **D2:505-507, `audits.py:196-198`.** The run-3 answer is new in this package. Its stated reason (no part recurs) is the one A-CF:284-289 and A1:1018-1021 refuted and withdrew.

**Harness**

20. **D3:104-105, 500; RM:56-57. "Eleven".**
    - Every one of the 21 gates has an escape not on the list, including the ten shown with esc 0.
    - Ten of the reader's cases still PASS and are not listed.
    - Examples: `render` checks a hash carried by the claim; a contrast with only the named field written; arms with constant offsets; declared rate 1.0 at 20 episodes; SneakyRegister passes restart.
    - Fix: "eleven pinned escapes".
21. **G6.restart, G6.reset.** Restart cuts at steps 0 to 6 of 8, not "every step" (`torture.py:133`). A carry set by a no-cue episode passes reset.
22. **Empty input.** With no seeds, the observer, reset, restart and calibration checks all return PASS.
23. **G7.calibration.** An estimator that never searches passes the registered sound cells where exact reach is 0.
24. **G2, G1.**
    - PASS does not make the negative's answer attainable: n=18, bound 1/50 gives PASS while P(NEGATIVE) is 0.695.
    - Declared rates are believed.
    - The mutant "power declared as a number" tests strings.
    - D2:28 "computed, not declared" overstates.
25. **G1.receipt.** String clocks "100" and "99" pass. Outcome fields are not read.
26. **G3.** The bracket is 0.35 to 0.68 with or without the weak positive. Three of the four impostors are one series. Duplicate blocks pass a bound of 0.25.
27. **G5.** Interchange has no earned negative. It calls the weak positive NEGATIVE, so D3:219-221 holds only because that organism is left off the G5 panel.
28. **G7.report.** True reports at small budgets get UNQUALIFIED. A repair claim from distance 0 passes with 128 of 128.
29. **G9 to G12.**
    - G10.ruler: rows pointing at another organism's receipt key qualify STRONG.
    - G12.promote: TRANSFER at L2, L3 and L4 pass on typed facets.
    - G11: the generator check runs only for the literal "NEW_FAMILY".
    - G10.setting: `power=0.99` typed onto run 3 passes.
    - G9: arms nudged in 3 of 24 replicates pass.
30. **D3:98-100, D2:116-119, RM:53-55. "65 of 71", "12 of 12".**
    - These are the author's tally of lines the reader's scripts mark E and S. The reader's report states neither number.
    - 10 of the 71 are two faults swept over a parameter.
    - 6 of the 12 sound cases are still not PASS; AR says "a few".
31. **`check_hardening.py`.** It makes 50 checks and all pass. 12 of 13 freshly planted errors also pass, for example "Eleven gates" changed to "Two gates", row labels swapped in a table, and a B sentence attributed to C.

**Fairness to B, C and O (document lines and source lines from the fairness fork; "checked" = I opened the source too)**

32. **D1:81-83.** B's "checked by" omits its read-only adversarial pass with seven concerns adjudicated (B-val:75-94; checked).
33. **D3:461-465.** "Both plans hold" experiment 5. C's plan holds only the cargo and flattening attacks (C05, days 46-60; checked).
34. **D1:204-208.** B has exactly solvable cases in W1 (B:359-361; checked). The quoted sentence is from its W2 paragraph.
35. **D1:214-216.** B also requires witnesses beyond W0 (B:287-289, 387-388).
36. **D1:228-229.** Seven reversals carry a quantity; two carry a day (A1:1294-1337; checked).
37. **D1:141-142, RM:43-44.** Point 12 has no code, so four rules are untested, not three.
38. **D2:110-113.** C injects faults at most layers and asks for mutants (C06:16; checked).
39. **D2:288-289.** O's eight coordinates include selection pressure, not exposure (O03:25-36; checked).
40. **D1:338.** The neutrality question is O's (O03:158; checked).
41. **D1:92-95.** A's repair is narrowed to bits; A's own list has six items (A1:981-1011).
42. **D1:374-375.** C's charter asks reviewers to try the masquerade (C06:17; checked).

**Overclaims**

43. **D1:15-17, 274, 291; RM:41-42.** A's repair was shown incomplete by a run. B's is untested, and B says itself it "does not promise a universal depth detector" (B:65-66). "Both end in one rule" is the author's synthesis.
44. **RM:104-127.** The "four groups" leave out the first reader's blocker 11 and majors 39 to 43 and 46. RM:140-150 lists three `MANIFEST.md` files that do not exist. The folder is ignored by `.gitignore:292` and needs `add -f`.
45. **D2:116, D1:407-408, HR:57-58.** "Passed all 62 mutants" means rejected; in the next sentence "passed" means escaped.
46. **D2:687-690, falsifier 4.** "65 in 71" counts targeted attempts, not a rate that "1 in 10" can be read against.

## MINOR

- `tests\test_harness.py:443-446`: `test_the_composition_is_of_three_seen_tables` asserts list lengths only.
- D1:277-281 gives 13.80 as the reader's number; the reader's is 13.79.
- D2:178-180 "showed"; the reader wrote "argued, not run".
- With a fixed held-out pair, one hard-wired formula scores 16.00 (4.83 when the pair is drawn per life). D3 lists this as still needed.
- "Six gates return INDETERMINATE": G12.promote relays a typed facet.
- `mutation_probe.py:24` and `replay_attack.py:29` override `RSO_COUNTERFEIT`.
- D2:583: statuses "are the package's", but R7 and R3 differ from C's.
- D1:538-540: the "from" cell sits on the third line.
- **Readability, undefined terms.**
  - D1 cites gates G5, G6, G8 and G11 with no gate table. "Cargo", "write ancestry", "clamp and swap", "R8-U", "FLAW 1" and "isomer" are undefined.
  - D2:21-22 uses "two axes, two doors, isomer panel, facets" before any definition. "Receipt", "certificate" and "class exclusion" are never defined.
  - D3 uses H0 to H9, E1 to E3, W1 and "door two" undefined, and "the cue" at 206-217 before section 6 defines it.
- **Readability, parsing.** D3:206 "A score of 64"; D2:203 "A proposed".
- **Readability, layout.** Three-column 80-character tables will wrap on a phone. RM:12 is 217 characters.
- **Length.** About 14,700 words. Cut D1 sections 10 and 11; cut D2 sections 7, 9, 10, 11, 14, 16 and 18 to a diff against the package; move D3 section 8 to an appendix; keep one TERMS block.

## Probes run

All with `python -B` on copies.

| Probe | Result |
|---|---|
| `comp\comp.py`, my own world from D3 section 9 | ELIM 3.38 (4,000 lives); TABLE_CACHE 3.39; COMPOSER 16.00; controls 3.38 |
| Author's `ladder.py` in a copy | 3.3667, 3.3167, 16.0, 3.4733, as documented |
| Organisms not using three families | same-table 3.40; same-move 3.36; others in item 10; all at the bound |
| Organisms using three families | 392-recombination cache 13.81; one cached table plus one acquired relabelling 16.00; composer keeping 3 entries 6.22 |
| `comp\exact3.py` | ninth map uniform unless the shown pairs connect table 2 to move 2 |
| Key reuse planted in the author's code | HIDER 16.00, 16.00; SANDBAGGER 16.00, 3.36 |
| G10.ruler | REUSE at BITS@PAIRS UNQUALIFIED; BITS with ACQUIRER(8) FAIL; REUSE at run 2 with WASTEFUL FAIL |
| `comp\fresh_probe.py` | 32 changes, 12 noticed, 20 survive |
| Fork blockers re-run | G8 xor at gap 16 PASS; false null PASS; observer PASS |
| Unit tests on a copy | 59 OK in 4.4 s |
| Fork scripts `h1\p01-p09`, `h2\q01-q08` | replay 71/65/12/12/25/22 and probe 55/54 reproduce |

## Checked and found sound

- H16 = 3.3807; threshold 5.8086 (Hoeffding, unit is the life); 44.25 bits; world-one numbers equal the receipt.
- The null is exact after the control history, with the move or the table withheld.
- No organism that avoids combining three families beat the bound.
- Binomial numbers: critical count 51; bands 0-13, 14-47, 48-50; calibration 164 to 208; bracket 0.35 to 0.68; the reach table.
- Gate table sums 44, 148 and 11; verdict split 82, 41, 19, 6.
- Strong-claim FAIL at runs 1 to 3 does not depend on the omitted rows.
- D3 section 7 numbers match the receipts.
- Every quotation attributed to B, C or O is verbatim; each allocation column sums to 100.
- E and S are the reader's own labels.
