# Report of the second reader's fork: gates G9 to G12, the kit and the checker

Verbatim, as it was returned.

Characters outside ASCII were replaced mechanically (12 x U+2013 as -, 9 x U+2192 as ->, 1 x U+2212 as -). Nothing else was changed.

---

Scope: harness v2 gates G9-G12 and GM, the kit registry, known_escapes, the attack and probe counts, and check_hardening.py. Everything below was run on scratch copies or read at the cited line. No BLOCKER in this scope; 13 MAJOR, 5 MINOR.

Paths: H = `F:\Prometheus-worktrees\dionysus-base-role\docs\phase3\hardening\FABLE-5.1\`; D1/D2/D3/RM = the three documents and `00_README.md`; HR = `harness\README.md`; AR = `attack\README.md`; CH = `check_hardening.py`; CF = `...\docs\phase3\review\FABLE-5.1\counterfeit\`; A1/A3 = `RESPONSE_1`/`RESPONSE_3` of the review.

## MAJOR

**1. Kit registry holds 13 of 26 receipt rows; "reuse, run 2" flips to FAIL when the omitted rows are registered.** (`audits.py:201-217`; D2:519-521; D1:473-476; D3:446-448)
- Not registered: run 1 STATIC; run 2 BADSHAM, HIDDEN, OFFHISTORY, STATIC, WASTEFUL; run 3 EAGER, STATIC; keys ACQUIRER(4), (8), (12), fire tests A and B.
- `CF\PREREG_gauntlet2.md:100-105` defines WASTEFUL, HIDDEN, BADSHAM and OFFHISTORY each as "BUILDER ...", which is the organism registered POSITIVE for reuse at this setting. The steps said FAIL on all four.
- D2:486-487 defines reuse as "parts built in a life lower the cost of a later family". Receipt medians: WASTEFUL dev_B 23.0 against naive 417.0; HIDDEN 20.5 against 301.5.
- Probe: `ruler_status("REUSE","S19@RUN2",CF, RUNS+[(cell,"S19@RUN2",(G2,"cell",cell),{"REUSE":"POSITIVE"})])` returns FAIL "registered POSITIVE, the ruler returned NEGATIVE" for each of the four. The four registered rows alone, unbuilt list emptied, return PASS.
- So "right on all four members they met" (the steps met nine cells) and "UNQUALIFIED at one setting and FAIL at two" depend on which rows were typed in.
- Fix: register every cell of each receipt with an answer per claim, or state in D2 s.12 and D1 s.10 item 6 that 5 of 9 cells are left out and why.

**2. The only PASS in the kit table (the author's own bits ruler) reads a label the review withdrew and omits the two organisms that label gets wrong.** (`audits.py:248`; D2:524; D2:196-197)
- `returned()` is `"POSITIVE" if data["verdicts"][key] == "CONSTRUCTED" else "NEGATIVE"`.
- `CF\README.md:445-457` ("A classification I withdrew") and A1:1013-1017 withdraw CONSTRUCTED / WITHIN_SELECTION_BOUND. `keys.py:33` defines the latter as "savings, but the certified bits carried do not exceed log2(G)".
- Probe: `returned()` gives NEGATIVE for ACQUIRER(4) and ACQUIRER(8), which D2:197 says were "certified at 1.44, 9.46" bits, and NEGATIVE for fire test A (receipt: RULER_NOT_APPLICABLE).
- Probe: BITS with ACQUIRER(8) or (4) registered POSITIVE returns FAIL.
- Probe: with the sandbagger's setting named for what it was (receipt key "fire test D: SANDBAGGER, harness reuses one key"), BITS returns UNQUALIFIED "not run at this setting".
- Fix: for BITS read `certified_bits_carried` (or the score against `threshold_correct`) with a third outcome; register all six organisms; give fire-test rows their own setting.

**3. The run-3 answer for the builder is new in this package, and its stated reason is one the review refuted.** (D2:505-507; `audits.py:196-198, 210`)
- A3:310-312 says only "a negative for "recursive" and a legitimate positive for reuse of built parts", with no setting.
- A1:1018-1021 withdrew "a pass in setting 2 with a fail in setting 3 meaning reuse of built parts ... it misfires". `CF\README.md:284`: "Both verdicts of run 3 follow the curriculum, not the disjoint parts".
- The registry scores the steps "right" on exactly that pattern. The run-3 verdict does not change (builder POSITIVE at run 3 still returns FAIL).
- Fix: say the per-setting answer is post hoc and give the curriculum as the reason.

**4. "55 changes, 54 noticed" does not hold for changes the test author did not choose.** (D3:106-108; HR "What the receipts say")
- Reproduced: 55/54, survivor R14, receipt identical apart from the timestamp. R01-R25 are the reader's, carried over; A26-A55 are the author's.
- My probe (`q06_my_mutations.py`): 36 one-line changes in `audits.py`, `claims.py`, `verdict.py`, `meta.py`. 10 noticed, 26 survive. Five of the 10 were controls I expected to be noticed.
- Survivors include:
  - a ruler with no known positive is accepted (`audits.py:272`);
  - L4 needs nothing; ORIGIN, ECONOMY, LAW and TRANSFER requirements deleted (`claims.py:20, 25-30`);
  - a sham neutral in 12 of 24 is enough (`audits.py:123`);
  - the arms threshold moved to 23; the contrast gate allows one extra difference;
  - the undecided band 13-21 counted as "can fail" or "can hold";
  - the custody selection check fires only on the literal word "confirmation";
  - WITHIN_SELECTION_BOUND read as POSITIVE.
- Caveat: mine were chosen after reading the code, the same caveat the first reader gave (`attack\REPORT_of_the_reader.md:148`). The documents do not carry it for the 55.
- Fix: say who chose the 55 and that the tests were written against them; add tests for the survivors.

**5. check_hardening.py: 12 of 13 freshly planted errors pass.** (RM:85-94; CH:71-120, 151-152, 215-224, 254-257, 585-592)
- In place: 50 checks, 0 failed, so "50 checks" is right.
- Fire test on a scratch copy (`q07_fire_checker.py`). These pass:
  - a sentence of B attributed to C in D1 s.3 (the checker reads its own QUOTES table, never the attribution in the sentence);
  - "Eleven gates" -> "Two gates" in the D3 headline; "Six gates return it" -> "Nine"; RM "twelve points" -> "two points" (the pin regex takes digits only);
  - two row labels swapped in the D2 s.5 composition table, so "carries nothing" scores 16.00 (the table is compared as a sorted bag);
  - "FAIL at all three" -> "PASS at all three" (D1 s.5); "yes to a selector" -> "no to a selector" (D2 s.12);
  - "it plants none" -> "it plants one"; "RUN (A); ARGUED (B)" -> "RUN (A); RUN (B)";
  - "Nobody has attacked version two" -> "Two readers have";
  - "An adversarial reader then wrote 71" -> "The package's authors then wrote 71";
  - a receipt body edited by hand (a G9.arms mutant set to PASS, status left alone).
- Caught: the digit control, and POSITIVE/NEGATIVE swapped in the G3 ranges.
- Fix: state these limits in RM, or parse attributions, pin number words, match D2 table rows by label, and re-run the harness in a temp copy.

**6. "65 of 71" and "12 of 12" are the author's tally of script lines, and half the sound cases are still refused.** (D3:13-17, 98-100; D2:116-119; RM:53-55, 114-116; D1:407-409)
- The reader's report never states 71, 65 or 12. The counts come from a regex on lines printed with E or S (`replay_attack.py:75`). Only AR says the labels are the reader's.
- Replay reproduced: 71/65/12/12/25/22.
- Of the 71 rows, 10 are two faults swept over a parameter (`reader\p06_escapes_c.py:93-95, 104-106`); 6 of the 65 passes are these.
- At least 3 rows are inputs identical to a clean case, labelled E to mark what a gate cannot see (`p07_audits.py:94` is the same call as line 93; `p06:129`; `p04:20`).
- On the current harness 6 of the reader's 12 sound cases are still not PASS (`q05_port_reader_cases.py`): exposure `{}` BLOCKED; same clock tick INDETERMINATE; same setting reworded FAIL; 16 seeds BLOCKED; 19 seeds BLOCKED; two capped arms FAIL.
- For 16 seeds the reader's own label is "FAIL instead of BLOCKED" (`p04:51`), a wrong kind of refusal, not a false accusation. AR says "a few"; D3 lists none.
- Fix: "by my replay, 71 lines the reader's scripts mark E, 65 PASS"; give the count of distinct faults; list the six in D3 s.11.

**7. "What was found is now a registered mutant or a known escape" is false, and "eleven" undercounts.** (D3:104-105, 500; HR "What happened to the first version")
- Of the reader's 18 portable broken rows for G9-G12, 8 still PASS on the current harness. Two are on the list of eleven (the G11 generator hash; the G9.sham rigged cell). Six are not:
  - a strong claim qualified by rows pointing at existing receipts;
  - "two things change, one not in the dictionary", which is the registered sound case of G10.contrast (`meta.py:499`);
  - a world filter chosen after design runs;
  - a structure claim with `exact_null` typed PASS at L2;
  - L3 with "reproduced" typed PASS;
  - render of an all-failed claim.
- Admitted in code and not listed: `audits.py:161-162`; D2:323-325 (selection, no gate); D3:180 (update law).
- The esc column of D3:118-158 shows 0 for G9.arms, G9.clauses, G10.contrast, G10.ruler and G12.render. I ran an escape for each (items 9, 10, 13).
- Outside my gates, one line each, all PASS on the ported run: declared rate 1.0 at n=20 in preflight; a 90% budget; 20 phantom hits of 256; 128 founders sharing one genome.
- Fix: "eleven pinned escapes; these others are admitted or shown and not pinned", and rename the column.

**8. G10.setting's sound case is run 2 plus two typed numbers; a declared power passes.** (`meta.py:221`; `audits.py:145-152`; D3:361-363; D3:410)
- `audit_setting(dict(RUN3, power=0.99, amortization_horizon=3))` returns PASS. Run 3's measured power was nine of ten blocks (`CF\README.md:333-335`).
- Also PASS: six choices given as `[]`, `{}`, `False`, `0`, `0.0`, `()`; as "pending", "-", "see above"; `effect_threshold=inf`.
- Sound case refused: `power=1` (an integer) returns BLOCKED.
- Fix: take power from the G1/G2 computation and require non-empty text.

**9. G10.ruler: a row's source is a declaration, and the run's third outcomes are lost.** (`audits.py:246-249, 263-271`)
- `ruler_status("STRONG","S19@NEW",CF,[("GENUINE_LEARNED_UPDATER","S19@NEW",(KEYS,"keys","ACQUIRER(16)"),{"STRONG":"POSITIVE"}),("PROCEDURE_SELECTOR","S19@NEW",(KEYS,"keys","ELIM"),{"STRONG":"NEGATIVE"})],{})` returns PASS.
- A cell verdict INDETERMINATE (`gauntlet2.py:556` can write it) returns BLOCKED "no readable verdict".
- Fix: bind rows to the organism and ruler ids recorded in the receipt; map third outcomes to INDETERMINATE.

**10. G12.render checks a claim against a hash carried by the claim itself.** (`claims.py:125-129`)
- `render(dict(claim(), setting={"note":"see the paper"}, setting_sha256=setting_hash({"note":"see the paper"})))` returns PASS "... setting: note = see the paper". A cell of one space also returns PASS.
- Fix: compare with the hash stored in the registration.

**11. G12.promote relays typed verdicts; four of seven kinds and L4 are untested; its sound cases are its own known escape.** (`claims.py:19-31`; D2:560-573; `meta.py:247, 553-554, 561-562`)
- PASS: `promote(claim("TRANSFER"),2)`; `promote(claim("NESTED"),2)`; L3 and L4 with typed facets; a source of one space.
- "A claim about structure ... stops at L1" (D2:572) is not in the gate. The mutant named for it is rejected only because the fixture types UNQUALIFIED.
- 5 of the 12 mutants exercise one path: a typed verdict relayed through `combine`.
- Every facet of every sound claim cites `RECEIPT_harness_v0.json`, including mediation, cargo_control, flattened_twin and second_implementation, which D3:178-182 says do not exist.
- An unknown or missing kind raises ValueError (`claims.py:80-81`). Levels 0 and -3 are treated as L1.
- Fix: a mutant per kind and per level; BLOCKED for an unknown kind; tie "structure" to kinds in code.

**12. G11.custody.** (`claims.py:59-72`)
- The generator check runs only when the claim field is literally "NEW_FAMILY". `check_custody(custody(claim="TRANSFER", confirmation=side(generator_sha256="1"*64)))` returns PASS, against D2:563 ("TRANSFER: a new family: another generator, not new seeds").
- Also PASS: confirmation seeds `["1","2","3"]` against `[1,2,3]`; custodians "tuner" and "Tuner "; generator hashes differing in letter case.
- `selection_data="Discovery"` returns FAIL with the reason "selected on confirmation data". `discovery="x"` raises AttributeError.
- Fix: check generators for every kind that needs a new family; normalise; BLOCKED on malformed sides.

**13. G9.** (`audits.py:17, 28, 92-96, 118-123`; D3:341)
- Arms: run-3 arms nudged in 3 replicates (21 of 24 equal) return PASS; the registered mutant nudges 1. The same three computations reported with constant offsets 1-3 return PASS.
- Arms against sham: a deterministic runtime with sham == intact and rescue == intact in 24 of 24 gets G9.sham PASS and G9.arms FAIL "dev_B = sham_B = rescue_B". The clean fixtures avoid this with a sham always one task slower (`meta.py:178, 483`).
- "G9.arms run 2 PASS" is the BUILDER cell. On the same receipt G9.arms returns FAIL for BADSHAM, MATURATION, MEMORISER, SELECTOR and STATIC (5 of 9 cells). In STATIC equal arms are the designed outcome.
- Clauses: thresholds are absolute counts and N is never used. With 240 replicates per isolating cell and the other clauses true in 22 of 240, the gate returns PASS. The registered clean toy cut to 12 replicates returns UNQUALIFIED.
- Empty replicate lists return FAIL, not BLOCKED.
- Fix: thresholds as fractions of a registered N; BLOCKED on empty input; name the cell in D3 s.7.

## MINOR

**14. "148 cases broken on purpose" (D3:13-14, RM:56) and GM status.**
- 15 of the 148 are the author's own runs or rows of the unbuilt list (`meta.py:470-519`). Two G10.ruler "mutants" say only "nothing registered has been built".
- GM is PASS for all 21 gates while 11 pass a registered broken case. The rule at D3:82 is avoided by filing those cases in `known_escapes()`, so D3:88 restricts nothing.
- `qualify()` raises on a thunk that raises (ZeroDivisionError, no row). Reasons are not compared: two mutants rejected by one unrelated precondition give PASS.
- "Six gates return INDETERMINATE" (D3:70, D1:487-488): G12.promote's is a typed facet relayed, which the test's own name excludes (`tests\test_harness.py:41-43`). Five gates compute it.

**15. Known-escape evidence.** `shown` exists for 3 of 11 (`meta.py:596-638`). The harness can produce it for G6.observer (unchecked seed returns FAIL, run) and G4 (unrelabelled returns FAIL, run).

**16. G10.contrast depends on the transcription.** Run 2 against run 3 written as one coarse field returns PASS; with the five other differing fields left out of both, PASS (`audits.py:164`). Sound cases refused: an unchanged cost reworded; `2` against `"2"`.

**17. Two scripts cannot run from a plain copy.** `mutation_probe.py:24` and `replay_attack.py:29` compute the receipts path from their own location, overriding `RSO_COUNTERFEIT`. I had to mirror `docs/phase3/{hardening,review}`.

**18. Smaller.**
- R14's name ("cells that do not differ ... pass") is false in the current code; they still FAIL (`audits.py:169`), so the 55 include one non-change.
- PROCEDURE_SELECTOR merges GEARBOX and run 2's SELECTOR, which `CF\README.md:175-176` calls different organisms.
- RM:140-150 lists three `MANIFEST.md` files that are not on disk.
- R17 and R07 are not the reader's original changes (`p09_mutate.py:44-46, 23-24`).

## Probes run

All in `C:\Users\jcrai\AppData\Local\Temp\claude\F--prometheus\3815a3b9-a31a-46a9-be9d-0e7abfa3cbf8\scratchpad\verify4\h2\`, with `python -B`. Three temp subfolders (`tmp`, `tmp2`, `tmp_cell`) may remain there.

| Script | What | Result |
|---|---|---|
| `q01_qualify.py` | `meta.qualify()` and every G9-G12 mutant reason | 21 gates, 44 sound, 148 mutants; 82/41/19/6; 11 escapes in 11 gates |
| mirrored tree | `mutation_probe.py`, `replay_attack.py` | 55/54 (R14); 71/65, 12/12, 25/22; both receipts equal the committed ones apart from the timestamp |
| `q02`, `q03` | dump of the four review receipts | as cited in items 1-3 |
| `q04_escapes.py` | constructed broken and sound cases, G9-G12 | as cited in items 8-13, 16 |
| `q05_port_reader_cases.py` | the reader's cases on the current harness | sound: 6 of 12 not PASS; broken G9-G12: 8 of 18 still PASS |
| `q06_my_mutations.py` | 36 one-line changes | 10 noticed, 26 survive |
| `q07_fire_checker.py` | 13 planted errors plus 2 controls | 1 caught, plus the digit control |
| `q08_misc.py` | arms and sham on every cell; registry counts; first version | 13 of 26 rows registered; 15 own-run "mutants"; 45 of 62 first-version names carried over |
| in place, read-only | `check_hardening.py` | 50 checks, 0 failed |

`check_hardening.py` reads the five ASTRA files by `git show` from their commit; I did not open that worktree. Afterwards nothing under `hardening\` or `review\` was newer than my start, and no `__pycache__` existed.

## Checked and found sound

- **Counts.** The gate table of D3 s.4 equals the receipt. More than half of the 148 postdate the attack (the first version had 62).
- **GM.** Its five self-tests exist (`tests\test_harness.py:46-70`).
- **Registry rows.** All 13 RUNS rows point at receipt keys that exist and hold what `returned()` reports.
- **Strong claim.** FAIL at runs 1, 2 and 3 exactly as the "why" column says, and it does not depend on the omitted rows. PASS went only to GEARBOX and BUILDER (run 1), BUILDER (run 2), STRATEGIST (run 3).
- **D3 s.7 numbers.**
  - Run 2: 4 of 13 clauses cannot fail; 2 fail by themselves (LIFECYCLE, NESTING.sham_harmless).
  - Run 3: 6 of 13; 1 fails by itself.
  - 8 arms give 3 series; BUILDER gives 8 series.
  - Sham within margin in 8 of 24, faster in 24.
  - 6 of 10 fields differ.
  - Both settings BLOCKED for power and horizon.
- **Mutant reasons.** G9-G12 mutants are rejected with reasons matching their names, apart from the typed-facet relays and own-run rows noted above.
- **R14.** It changes a reason text and no verdict.
