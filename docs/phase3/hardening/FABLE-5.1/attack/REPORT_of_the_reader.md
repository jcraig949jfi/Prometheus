# Defect list: FABLE-5.1 hardening package (adversarial review, read-only)

Nothing under `F:\Prometheus-worktrees\` was created or changed. Everything in this list was checked against the source files or run in scratch.

**Abbreviations**
- D1, D2, D3: the three documents. RM: `00_README.md`. HR: `harness\README.md`. CH: `check_hardening.py`. All under `F:\Prometheus-worktrees\dionysus-base-role\docs\phase3\hardening\FABLE-5.1\`.
- A1, A2, A3, A-RM: `RESPONSE_1`, `RESPONSE_2`, `RESPONSE_3`, `00_README.md` under `...\docs\phase3\review\FABLE-5.1\`.
- B: `reports\Wind tunnel charter review.md` in the Enceladus worktree.
- C1, C2, C3, C5: `chatgpt56_01`, `_02`, `_03`, `_05` under `...\roles\Dionysus\prompts\2026-10-02_hardening_v0.2\`.
- O1, O2: `03_RSO_WIND_TUNNEL_DESIGN_v0.1_as_pasted.md`, `04_RACE_CAR_PORTFOLIO_R0-R9_as_pasted.md`.
- `[n]` is the attack number from the brief. `file:n` is a line number.

## BLOCKERS

- **B1 [1] D1:280-283.** Says C dropped "native against host cost". C1:120 has "native resource unit plus host-cost accounting", and D2 section 7 builds on it. Fix: delete; C lacks only an explicit "no universal scalar" rule.
- **B2 [1] D1:284-286.** Says C dropped "conditions travel with a verdict". C1:61-63 makes every claim conditional on the cell, and C1:254-256 carries "setting S" in the report form, which D2:132-134 adopts. Fix: "C carries the setting; it has no gate refusing an unconditioned quote".
- **B3 [1] D1:266 and D1:435-437.** Calls "second candidate by evidence" new and credits C. It is O2:231, quoted by the author at A1:459-460, and B:626, 649-651. Fix: attribute to the original portfolio and B; C adds only the R5 branch.
- **B4 [1] D1:165-169.** "For R3, R4 and R6 that means no claim, ever". B:99-101, 132, 458, 490 cap only the intervention and nested claims and keep behavioural comparison open. D1:139-141 says the same of B. Fix: "caps mechanism and nested claims in those physics".
- **B5 [1] D1:180-183 "I did the mirror image"; D2:456-457 "Each of us ranked our own candidate second".** False for B.
  - B names no second deep build (B:626, 649-651: at most one R3 extension or full R4, by a named question).
  - Its R4 is the 8% tiny specimen that D1:440 accepts on merit.
  - R3 is partly Astra's (O2:16), so folding it cuts against B's own stake.
  - Fix: delete both sentences; only A ranked its own candidate second.
- **B6 [1] D1:296-307, RM:45-47.** Three of the four BLOCKERS charged to C say C lacks what its text partly contains.
  - B2 (gates not qualified): C2:26-35, 41-46, 50-57, 81, 85 list injected faults per layer, and C1:281 requires that fixtures fire. Most of D3's mutants come from these lists. Missing is only the meta-rule and clean cases.
  - B3 (attainability not a gate): C1:282 "verdict attainability/power is checked pre-run"; C5:30 "power/attainability preflight"; C5:15 refusal gates in days 1-15. The gap is its day (16-30).
  - B4 (nine negatives, no positive): C3:41-43 "counterfeit/admission kit ... expected verdict is claim-specific"; C2:77, C1:258 and C5:54 require a genuine positive. The gap is the missing answer table.
  - Fix: restate each as the narrower gap and reword RM:45-47 and D2:26.
- **B7 [2] RM:43-44 "outside both on one row"; D1:236-238 "the one row".** D1:225 puts C at 55 against 45 and 50. That is two rows. Fix: correct or drop.
- **B8 [1,6] D1:186-189, RM:40-41 "the same object".** Contradicted inside the package.
  - D1:211-212 says neither has "a built nested compiler"; so do D1:371-373 and D3:316-317.
  - D2:375 and 380 give the library learner (reuse POSITIVE, built) and nested compiler cargo (reuse negative, not built) different registered answers.
  - D1's table omits B's write-provenance row (B:436), the feature B's first flaw is named for. Run 2 measured no write ancestry.
  - Fix: "run 2 is one member of the family B describes; four of B's six evidence rows are reproduced".
- **B9 [4] D2:156 "in none of the three sources".** The ladder is in A2:347-359 (orders 1 to 4; bits "at each order, against the exact score of the class that carries nothing across that boundary"), A2:443-444, A1:673-676 and C1:40-53. Only the order-4 world of D3 section 9 is new. Fix: say so, and narrow D2:29-30.
- **B10 [4] D2:173-175 "Content below the claimed order is redrawn, so cargo about content cannot help".** Refuted by simulation of D3 section 9 as written.
  - An organism that caches one solved family table and applies a fixed 256-way re-indexer scores 13.79 of 16 on the order-4 certificate, against the 3.38 bound.
  - It has no notion of epochs and learns nothing after its first family.
  - Only s and o are redrawn; a cached family table is L up to that gauge.
  - Fix: "per-level parameters are redrawn; what is certified is carried content; the ladder cannot separate cargo from a changed rule of acquisition". Remove the bullet from "WHY IT ANSWERS BOTH REVIEWS".
- **B11 [5] RM:83 is `REVIEW_SECTION_PLACEHOLDER`.** D1:460-461 cites it as written. RM:92 and 96 list two `MANIFEST.md` files that do not exist. Fix before commit. Two commit hazards:
  - The folder is ignored (`.gitignore:292` `docs/*`), so it needs `add -f` with files listed.
  - CH's "inputs README records the hashes" check depends on the uncommitted edit to `...\2026-10-02_hardening_v0.2\00_README.md` and `MANIFEST.md`.

## MAJOR

**Fairness toward B and C [1]**

- **M1 D1:58-60, RM:34-36.** "Exact bounds and known answers (mine), interventions and custody (ASTRA's)". B has exact W0 truth and cheap-policy bounds (B:321-325), exactly solvable W1 cases (B:360), exact micro-landscapes (B:293, 551) and an exact-W0 checker (B:705). Fix: "B has exact bounds in W0; A adds planted keys beyond W0".
- **M2 D1:161-163.** The quoted sentence is from B's W2 paragraph (B:387-391). The same paragraph gives the remedy ("state which baseline classes are bounded", "narrowing its claims"), which is A's own "cap the claim". Fix: drop "without a remedy".
- **M3 D1:170-172.** "B has no entry rule and no way in for a physics nobody can hand-program". B conditions the reading of a search null (B:287-314) and never shuts a physics out (B:99-101), so it needs no second door. The door repaired A's own draft (A1:246-249). Fix: say that.
- **M4 D1:173-174.** "B keeps them as observational coordinates". B flags the state split (B:94-97, 247-248: "Define intervention scope, not mandatory buffers"). Fix: credit it.
- **M5 D1:175-177.** B asks for "an executable registration" with sample size and power (B:518-521) and a stop rule (B:624). Fix: quote it.
- **M6 D1:178-179 and D1:75.** A's reversals 6 and 9 carry no number (A1:1317-1324, 1335-1337). B has a reversal condition per candidate (B:194-205) and an exit decision per interval (B:620-626), not "five, in words". Fix: "seven of nine".
- **M7 D1:73.** "Gates at days 30, 60, 90, decided by code". Only GATE 30 is (A1:1179). GATE 90 is three operator decisions (A1:1200-1202, 1220).
- **M8 D1:113-116, 424-426; RM:37-39 "the largest".** A already wrote "a legitimate positive for reuse of built parts. Register which claim an organism is a control for" (A3:310-312), and D1:67-68 says so. What B adds is a genuine learned-updater positive and measured false rejection. D2's kit has neither. Fix: state the concession as that.
- **M9 D1:106 "I take each into my version".** Not true of four points.
  - Point 6 (reconstruction) appears nowhere in D2 or D3, and D2:413-414 rewards reproduction "in another physics".
  - Point 11: D2:409-416 are A's own ladder requirements (A2:455-467). B's causal, origin, transfer and resource facets are absent (`claims.py:12-16`).
  - Point 10: the 2x2 has no slot in D2:475-495 and is second to slip (D2:497).
  - Point 3: G11 has no field for when the acceptance rule was fixed.
- **M10 D1:142-143.** "AT SMALL COST ... is cheap" is not B's claim. B's Experiment 4 needs priced worksites, independently prepared worlds and four interventions with physical-damage shams (B:578-593).
- **M11 D1:249.** "Search inside the cell: A". O1:26, 34 already has S, and A1:289-290 says so.
- **M12 D1:263-269, RM:45.** Five rows are marked new; the text says three. UNQUALIFIED descends from O1:326-335 and B:122, 313-314. "Qualification fixture" is B's phrase (B:201).
- **M13 D1:278, 334-336.** More "C lacks" claims that C contains.
  - "What slips" dropped: C5:48, 52, 54 have "only if earlier gates were on schedule".
  - "Second-author isomers have no date": C5:30 puts them in days 16-30.
  - "Quantities on reversals" dropped: C5:38 keeps A's reversal 1 with its day and "one repair round".
- **M14 D1:313-324.**
  - M2: "a sham that cannot fail" is C2:94 ("impossible/non-failing control"), which D3:304 maps to G9.sham.
  - M4: C1:161 and C2:39 include the ascent fixture, which is this harness's own positive control (`meta.py:88`).
  - M5: the exact class bound is in C2:20 and C1:178; the inheritance dial is in C1:117.
  - M6: C has INTERVENTION_INVALID (C2:61) and "typed inconclusive" (C5:61).
- **M15 D1:292-295, 342-343.** A delivery gap is charged as a design defect. The archive holds `harness/__pycache__/` and `tests/__pycache__/` (prompts `00_README.md:76-80`), which is evidence a harness ran. Fix: status NOT_VERIFIED; ask the operator for the files.
- **M16 D1:268 "a fair merge".** The table credits A in 14 of 16 rows and omits the original design as a source. The author is the main beneficiary. Fix: state the count.

**The common-bucket table [2]**

- **M17 D1:217-218.** B's sentence is cut before "and qualification fixtures" (B:41-43; B:632 includes the message ring). B's 30 holds known-answer fixtures that D1 counts under organisms for A. Fix: quote in full.
- **M18 D1:225.** A's 45 is "tunnel core (runner, worlds, rulers)" (A1:1212). A's X1 and X3 sit in standards, X4 in R0 and the kernel, X5 in the census. So most of A's experiment running is outside row 1, while all of B's 20 is inside it.
- **M19 D1:215, 236.** "Five points on every row" is an artefact of the bucket choice.
  - The differences must sum to zero.
  - On unmerged lines: core 45 against 30; runtimes 25 against 26; standards 20 against 14 plus fixtures; experiments unstated against 20.
  - "Nearly one plan" cannot stand beside D1:328 (C's 30 as a MAJOR defect).
  - C never calls its allocation a compromise.
  - B's R8 and R4 as organisms is consistent with A's "standards"; the inconsistency is M17.

**The harness [3]**

- **M20 `rulers.py:22`, `stats.py:89-93`.** No gate can return INDETERMINATE.
  - `three_way` is called only by its test. The one INDETERMINATE mutant is a hand-set facet (`meta.py:306`).
  - NOT_EXCLUDED is mapped to NEGATIVE, so `entry_gate` with 16 or 19 seeds returns FAIL "the designed positive does not beat the exact bound" on a sound positive.
  - That is the misreading D3:47-49 says the fifth verdict prevents; D1:390-392 says "tested".
  - Fix: three-outcome ruler; call preflight inside G3 and G4.
- **M21 D3:60, 66 against HR:32 "21 gates, each qualified".** The registry leaves out the mutant G3 is known to pass. By the meta-gate's own rule G3.exclusion is FAIL and may not feed G4 or G5.
  - Any bound from 0.22 to 0.805 passes.
  - Changing BOUND from 0.5 to 0.7 passes all 31 tests.
  - D3:410 "cannot tell" is wrong: an impostor at one half reaches the 0.25 critical count (35) with probability 0.27. The escape is seed luck; three impostors are the same function (26, 26, 26, 31).
  - Fix: report 20 qualified plus one with a known escape.
- **M22 G8, `torture.py:71-81`.** Three broken worlds pass.
  - The probe carries the complement of the answer: the reader scores 0 of 64 and the test is one-sided.
  - The cue is the xor of the last two distractors.
  - The probe leaks in 40% of episodes: the reader scores 44, and P(flag at 0.70) is 0.056.
  - In the first two, a policy that carries nothing scores 64 of 64 and the exclusion ruler certifies it POSITIVE.
  - The gate checks five hand-written policies, three of them identical on the clean world. That is not D2:341-344.
  - Fix: two-sided test with a margin; rename it "baseline list".
- **M23 G4, G3, G5.** Each has an escape or a rejected sound case.
  - G4 PASSes when the "impostor" holds the bit perfectly and answers its complement.
  - G4 PASSes when CHEMISTRY is admitted on register organisms.
  - G3 PASSes an always-POSITIVE ruler on a panel with no impostors (`meta.py:57`).
  - G5 PASSes REGISTER_SWAP declared SHARED on three look-alike physics (`rulers.py:107` counts dictionary keys).
  - Sound case rejected: a fifth physics with no organism makes every shared claim UNQUALIFIED, against D2:279-280.
- **M24 G6.reset, `torture.py:48`.** State that survives reset and shows only in cued episodes passes.
  - The world clears its mark every episode (`retain1.py:47`). Removing that line passes all tests.
  - So cross-episode external carryover (C2:33; D3:315) is not covered.
  - D1:359-362 "five" incomplete-reset cases are two reset faults, two restart faults and one within-episode write.
- **M25 G6.restart.** The mutant named "a restore that leaves stale state" is a no-op restore into a fresh runtime (`retain1.py:306-310`, `torture.py:57-61`). Restores that really keep stale state (append; fill-if-empty) pass. Capture is checked at step 3 only.
- **M26 G7.calibration.**
  - Repair counted as cold passes on 3 of 6 landscape and rule pairs.
  - A 70%-budget estimator and one with 6 phantom hits of 48 pass.
  - A sound estimator FAILs on 19 of 400 founder sets (4.8%), below the 0.99 that D2:224-226 demands.
  - Four of five clean cases are degenerate (exact 0 or 1).
- **M27 G7.report, `search.py:119-140`.**
  - Escapes: cold discovery with zero hits; a needle null from two strict policies (against D2:325-326 and D3:309); the label "the substrate cannot do it".
  - Sound cases rejected: the label "not a claim that the target is impossible"; a bound rounded to 0.0605.
  - The positive control is not tied to the policy that produced the null.
- **M28 D3:267-293.** The G10.setting and G10.contrast rows read dictionaries typed after the fact (`audits.py:131-146`), not receipts.
  - G10.setting passes power 0.2, power 0 and "tbd" (`audits.py:114`).
  - "Would not have started" rests on two empty fields.
  - None of the faults found can be checked before a run starts (`audits.py:3`).
  - "Five other things changed" is relative to a ten-key dictionary; the reader found two.
  - Fix: "two fields were never registered; the other faults are found after the run".
- **M29 G10.ruler, `audits.py:185-188`.** Only file existence is checked.
  - `README.md` and `MANIFEST.md` as "receipts" give PASS.
  - STRONG_RECURSION passes once members are flagged built.
  - Registered answers are never compared with receipt contents. `RECEIPT_keys.json` certifies 38.99 bits for the sandbagger; only the irrelevant-history arm refuses it.
  - D3:20, 434 "four receipts": two are parsed.
- **M30 G9.**
  - Arms: one nudged replicate of 24 passes; two arms at a cap are accused.
  - Sham: an idle sham plus one rigged cell passes; a neutral sham at 3 against 4 tasks fails.
  - Clauses: the "cannot hold" half has no mutant.
- **M31 G11, G12, G1.**
  - G11: no field for acceptance-rule timing or custodian, so the D1:122-125 fault passes; a renamed generator passes.
  - G12: an absent facet plus a FAIL gives BLOCKED (`claims.py:56-58`), against D2:115-117.
  - G12: `render` prints L0 for all four non-pass verdicts, against D2:117-118, and accepts any non-empty conditions.
  - G12: the "structure" mutant is the generic unqualified-facet path.
  - G1: power for one answer only, NaN and 99 pass; `design_seeds=[]` is BLOCKED.
- **M32 Tests.** 22 of 25 targeted one-line changes to gate logic pass all 31 tests. The changes were chosen after reading the code, so this is not a mutation score. Survivors include:
  - power floor 0.99 to 0.50;
  - BOUND 0.5 to 0.7;
  - trajectory comparison removed from reset and restart;
  - calibration interval made one-sided;
  - mark not cleared;
  - required-field lists cut.

  By D3:59 those checks are UNQUALIFIED.

**The order ladder [4]**

- **M33 D2:29-30, 172-182, 528-531; D3:366-368; RM:51.** "A ruler for nested improvement" and "answers both reviews" overclaim.
  - The ladder certifies retention of random content (D2:191-195).
  - A's own text on run 4: "It shows nothing about depth" (A1:1053-1054).
  - Under B's criterion (savings follow cargo) every pass is cargo.
  - The key-world positive is a memoriser, a registered negative in the kit (D2:378), so "the package's rule is met" (D2:181) is not.
  - Fix: call it a retention ladder throughout.
- **M34 D3:358.** ACQ3's "no" at order 4 comes from an instruction to forget at the epoch signal.
  - The same organism without the forgetting scores 4.10 against 3.38.
  - With a second offset as the epoch object it scores 15.06.
  - So falsifier D2:528 cannot fail.
- **M35 Order labels.** By D2:53-55 and A's glossary (A1:94-96), a 16-trial family on one hidden function is a task. Run 4 is then order 2 and the proposed world order 3. A's accuracy reviewer made the same charge against run 1 (A1:784-786). This is argued, not run.
- **M36 D3:337 "can be preregistered as it stands".** No E, F, lives, alpha, threshold, unit, power or irrelevant-history arm is given. The author's own G1.cell and G10.setting would BLOCK it.
- **M37 D2:184-189, D1:383-385.** The operational form decides by pedigree (found against designed).
  - That contradicts D2:176-178 and D1:108-116.
  - It is circular: a found positive must be certified by the ruler it qualifies.
  - A never-forgetting organism with a broad re-indexer meets it.
- **M38 D2:160-164.** Omits the first-family check and the irrelevant-history arm that run 4 needed.

**Consistency and the checker [5]**

- **M39 D2:98-100.** "Its runs were sound" contradicts D3:274-290. "Most of them in controls ... and sentences" contradicts A-RM:118-120 ("Most of the rest ... blamed the package for lacking a safeguard it has").
- **M40 D3:267, RM:54-55, D1:315, HR:36-38, `meta.py:7-8`, test:145.** The faults in runs 2 and 3 were found by one reader, the third (A-RM:103-108). The harness returns about a third of them. It does not return: C read the easy way, world selection, the acceptance rule changed after design runs, factor and curriculum dependence, the measured power of 0.9.
- **M41 D2:223 "FOUR RULES, each a gate".** SELECTION has no gate (D3:331 "specified"). ATTAINABILITY's G2 is connected to no runner or cell.
- **M42 D2:475 "decided by code".** D3 has no gate for GATE 15 to 60, and the second-build rule has no thresholds. The 2x2 pilot (D2:359), second-author isomers and found organisms (D2:273-275) are in no gate line.
- **M43 D1:440 "in the first panel".** D2:477-481 puts the lattice at GATE 30, later than B's days 10-15 and C's days 1-15, yet it is labelled "B over A".
- **M44 CH fire test.** 22 of 33 planted errors pass. RM:75-79 is therefore untrue on "every quotation against its source" and "every number quoted". Examples that pass:
  - a package sentence attributed to B;
  - "85" changed to "95" in D1;
  - "three of four physics" changed to "two";
  - D3 section 7 FAIL changed to PASS, 8 to 18, 6 to 9;
  - "0.24" changed to "0.42";
  - any number in RM or HR.
- **M45 CH:232-238.** The bucket check compares D1 with constants typed in CH. `45 == 45 + 0` and its neighbours cannot fail. Nothing is read from A, B or C.
- **M46 D2:538.** Falsifier 6 targets "scaffold distance as a planning tool", which D2 does not contain. Falsifiers 3 and 7 carry no number, against D2:39.

## MINOR

**Fairness and attribution [1]**

- D1:326 "my lighter draft": the draft had twenty packages (A1:1159-1161).
- D1:61 "worst flaw" imposes a ranking B does not make.
- D2:455-456 lists five stakes for A (D1:180 says six; the R4 lattice arm is missing) and omits B's share of R3.
- D2:31 presents "nine registered choices" as a change from the package; it is C1:240-250 verbatim.
- D2:209 "first six" open against A's "five".

**Consistency [5]**

- D1:34-36 "each line below is marked": only 12 lines are, and NONE is never used.
- D1:394 and D3:406 "two known escapes": the second is not an escape of the harness, since G6.observer rejects it.
- D1:317-318 "a test caught it": no receipt or history exists (the folder is untracked).
- D1:191-207 quotes run-2 medians without factor, acceptance rule or world selection, against D2:230.
- D1:399 "fit for CI: all 31" against D1:400-403.
- D1:438-439 "reactivation test": D2:444-446 gives none.
- D2:371 "reuse at order 3" is undefined and not among D2:123-128.
- `audits.py:165` marks WORLD_PARKING not built while `retain1.WorldParker` runs in G8.
- D3:277: one of the "6" is false in 1 or 2 of 24 replicates; it never FAILs.
- D3:313 and 318: fixtures 13 and 17 are loosely mapped.
- D3:384 "margins ... specified": only a rule is given.
- CH:261-264 "as my review states them": the review never states 72 (72 is correct).
- Six of the 34 clean cases are the same eight ruler evaluations (G3, G4 four times, G5).
- `meta.py:89-91, 232`: the clean REPAIR_REACH case carries cold-start hits.
- `test_harness.py:92-93` cannot fail given lines 90-91. Line 102 restates the formula. Lines 104-105 pass for any interval containing 0.5.
- `test_counts` and CH pin 21, 34 and 62, so adding a mutant breaks them.

**Readability [7]**

- D1 never says what the two reviews review. "Section 19" (D1:61), R0 to R9, W1, V/U/S, "task cargo", "write ancestry" and "positive" are undefined in its first 60 lines.
- D2:6 "RSO" is never expanded. D2:20-21 uses "two axes, two doors, isomer panel, facets" before any definition. "Observatory", W0 to W2 and Track-A are undefined.
- D3 has no terms section: gate, ruler, physics, kit and "v1 and v2" (D3:453) are undefined.
- Unparseable: D2:485-487 (missing "if"); D3:366-368; the split labels at D1:27-28 ("What I did / not get.") and D1:284-285 ("From / both:").

## Probes run

Scratch: `C:\Users\jcrai\AppData\Local\Temp\claude\F--prometheus\3815a3b9-a31a-46a9-be9d-0e7abfa3cbf8\scratchpad\verify2\`. All runs used `python -B` on copies. Afterwards there was no `__pycache__` and no changed file in either worktree.

| Probe | What it did | Result |
|---|---|---|
| `p01`, `p08` | Reran the harness and `run_harness.py` in a patched copy | 31 tests OK in 1.4 s; every receipt section identical except timestamp and my path patch |
| `p03` | Binomial arithmetic, Clopper-Pearson, zero-hit bound, panel scores | Critical count 51 (P(X>=51) = 9.40e-7; P(X>=50) = 3.5e-6); power at 0.75 is 0.239; interval matches scipy to 2e-16; zero-hit 0.1173 and 0.0605; panel 64 against 26, 26, 26, 31 |
| `p04` to `p07` | Constructed escapes and sound cases per gate; audits against receipts | As listed in M20 to M31 |
| `p06` | `exact_reach` against an independent chain and 20,000-run Monte Carlo | All 12 cells agree |
| `p09` | 25 targeted one-line logic changes | 22 survive all tests |
| `p10` | Fire test of CH on a scratch mirror (`git show` pointed at the real repository) | 11 of 33 planted errors caught |
| `p11` | Simulation of the order-4 key world, 3,000 lives | See below |
| In place, read-only | `check_hardening.py` and `check_review.py` | 29 of 29 pass; 72 of 72 pass |

Order-4 simulation, mean correct of 16 (bound 3.38):

| Organism | Order-3 certificate | Order-4 certificate |
|---|---|---|
| ELIM | 3.38 | 3.39 |
| ACQ3 with the forgetting instruction | 15.06 | 3.39 |
| ACQ3 without it | 15.06 | 4.10 (15.06 if the epoch object is a second offset) |
| Cached table plus fixed re-indexer | 15.06 | 13.79 |

## Checked and found sound

- **Quotations.** All 33 are verbatim in a source, and the attributions I checked by hand are right, apart from the truncation in M17.
- **Bucket source numbers.** A 45/20/10/15/5/5; B 30/12/14/6/8/20/10; C 35/30/20/10/5. All sums are 100.
- **Record numbers.** 85 (38 + 21 + 26); 72 checks; the run-2 medians (313.5, 20.5, 316.0, 12.0, 16.0, 22.0, 323.5); 660; the run-4 bits; 3.38 = H_16; 0.865 (A2:498-501).
- **Receipt.** Reproducible. The gate table, kit table and reach table equal it.
- **Arithmetic.** `stats.py` is correct. NEEDLE under the strict rule has cold reach exactly 0, and the other reach values are exact.
- **Audits.** The 13 clauses in `audits.py` equal the `relations` functions in `gauntlet2.py` and `gauntlet3.py`, and reproduce the receipts' own conjunct counts. Results: 4 of 13 and 6 of 13; 8 arms as 3 computations; sham 8 of 24 near and 24 faster.
- **Run-2 sham FAIL** is stable for margins 0.25 to 0.50.
- **Content resets** are empty for BUILDER (0 of 24 replicates change), as D1:119-121 says. Neither preregistration states power.
- **Exact-null argument** for the order-4 world is correct as a retention certificate: 3.38 is the bound in the first family of an epoch for any policy carrying nothing across that boundary.
- **Mutants.** The registered reasons match the names except the three noted: stale restore, structure claim, the label-only "repair as cold".
- **Form.** Table columns line up. "Five of the seven files" is right. Commits `ff1d7f0f4` and `f4d9e72d9` exist.
