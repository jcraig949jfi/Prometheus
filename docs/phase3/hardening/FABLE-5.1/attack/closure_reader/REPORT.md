# Report of the closure reader, on the second version

Verbatim, as it was returned.

---

# Closure read: FABLE-5.1 hardening package, second version

Nothing under `F:\Prometheus-worktrees\` or `F:\prometheus` was created or changed. Scratch is in `...\scratchpad\verify3\`. All three receipts regenerate identically in a scratch mirror, timestamps apart.

Abbreviations as before: D1, D2, D3, RM (`00_README.md`), HR (`harness\README.md`), CH (`check_hardening.py`); A1/A2 (my-review responses), B (ASTRA report), C1/C5 (package), O1 (original design). `file:n` is a line number.

## 1. Closure table

| Finding | Status | Evidence where not CLOSED |
|---|---|---|
| B1 | CLOSED | |
| B2 | CLOSED | |
| B3 | CLOSED | |
| B4 | CLOSED | |
| B5 | CLOSED | |
| B6 | CLOSED | Over-corrected: see N15 |
| B7 | CLOSED | |
| B8 | CLOSED | |
| B9 | CLOSED | |
| B10 | CLOSED | |
| B11 | PARTLY | Placeholder gone (CH:181 checks it). RM:140, 145, 150 list three `MANIFEST.md`; none is on disk. Folder still ignored (`.gitignore:292`); the edit to the prompts `00_README.md` and `MANIFEST.md` is still uncommitted |
| M1 | CLOSED | |
| M2 | CLOSED | |
| M3 | CLOSED | |
| M4 | CLOSED | |
| M5 | CLOSED | |
| M6 | PARTLY | D1:228-229 "carry a quantity and a day": seven carry a quantity, two carry a day |
| M7 | CLOSED | |
| M8 | CLOSED | |
| M9 | PARTLY | D1:141-142 names 5, 6, 8 as untested rules. Point 12 is also design text only (D2:338-339). Point 11's kinds ORIGIN, TRANSFER, ECONOMY have no test (N5). Point 10: see M42 |
| M10 | CLOSED | |
| M11 | CLOSED | |
| M12 | CLOSED | |
| M13 | CLOSED | |
| M14 | CLOSED | |
| M15 | CLOSED | |
| M16 | CLOSED | Hedged at D1:42-44, 327 |
| M17 | CLOSED | |
| M18 | CLOSED | |
| M19 | PARTLY | D1:321-322 "not a defect"; D1:441 still lists "Organisms get 30%" under gaps |
| M20 | CLOSED | See N19 |
| M21 | CLOSED | |
| M22 | PARTLY | See N7 |
| M23 | CLOSED | Two cases kept as pinned escapes |
| M24 | CLOSED | |
| M25 | CLOSED | |
| M26 | CLOSED | Resolution pinned |
| M27 | PARTLY | See N8 |
| M28 | CLOSED | |
| M29 | PARTLY | See N4 |
| M30 | PARTLY | Arms nudged in three replicates pass (`audits.py:28`). Capped arms FAIL by stated design (D3:255-257) |
| M31 | PARTLY | D2:572 structure rule is not in code (`meta.py:561-562` is a TRANSFER claim with a typed facet). `render` checks the hash the claim itself carries (`claims.py:125-129`). Custodians compared as strings (`claims.py:72`) |
| M32 | OPEN | The 25 are now noticed; 34 of 44 new ones are not (N5) |
| M33 | CLOSED | |
| M34 | CLOSED | |
| M35 | CLOSED | |
| M36 | CLOSED | |
| M37 | CLOSED | |
| M38 | CLOSED | |
| M39 | CLOSED | |
| M40 | CLOSED | |
| M41 | CLOSED | |
| M42 | PARTLY | D2:475-476 (2x2 pilot "after GATE 30") and D2:381 (found organism by day 90) are in no line of D2:632-654 |
| M43 | CLOSED | |
| M44 | PARTLY | Digits closed; words open (N11) |
| M45 | CLOSED | |
| M46 | CLOSED | |

Minors: closed, except three.
- D1:494-497 still says "all 59" tests fit for CI beside "regression tests on four files".
- D3:334-338 "no cell that makes them false": one of run 3's six is false in 1 or 2 replicates.
- Six sound cases are still the same ruler evaluations (G3, G4 four times, G5).

## 2. Defects that are new or still open

### BLOCKER

- **N0 (B11 residue). RM:140, 145, 150.** Three manifests are listed and do not exist. Fix: generate them or drop the lines; commit the prompts `00_README.md` and `MANIFEST.md` edit in the same commit; `add -f` with files listed.

### MAJOR

- **N1 [fairness to B, new]. D1:81-83.** The "checked by" row for B now reads "its author's source anchors; a documentary consistency check". B's `VALIDATION.md:75-96` records an adversarial read-only reviewer with seven concerns, each adjudicated. The first draft had it; the rewrite dropped it. Fix: restore it.
- **N2 [fairness to B, new]. D1:283-292, D1:523-524, D2:247-256, RM:41-42.** B's repair is restated as "an exclusion against a registered class of fixed updaters", and "both end in one rule".
  - B:485 is one matched control "where feasible" among six repair items (B:473-494).
  - B:689-690 says "intervention-relative", not relative to a class.
  - D1 row 6 credits "name the class" to "B, A". RM:41-42 carries no ARGUED mark.
  - Fix: mark it as your reading in all four places.
- **N3 [accuracy toward O, new]. D2:288-289.** "O's eight coordinates, as the package orders them (..., exposure)". O1:26-36 has pressure, not exposure; C swapped them. `registration.py:14-16` follows C, so O's pressure coordinate is dropped without a word. Fix: "the package's eight; it replaces O's pressure with exposure", and say whether that is intended.
- **N4 [harness, M29]. `audits.py:212-216, 248`; D2:524.** The only PASS of G10.ruler depends on which organisms are registered.
  - The registry holds 4 of the 9 cells of `RECEIPT_keys.json` and reads the withdrawn label (`== "CONSTRUCTED"`).
  - With ACQUIRER(4) or ACQUIRER(8) registered as the positive it is, the verdict is FAIL.
  - D2:196-197 says those two were "certified at 1.44, 9.46 bits".
  - Fix: read certified bits (above 0, not a leak, ruler applicable) and register all nine cells. All nine are then answered correctly.
- **N5 [tests, M32]. D3:106-108, HR:52-53.** "55 changes, 54 noticed" is a fitted sample: 25 are mine from round one, with tests since written against them, and 30 are the author's. Of 44 new one-line changes, 34 pass all 59 tests. One of the 34 alters no verdict.
  - G6 observer, reset and restart each check only the first seed.
  - G7.report: unknown claim passes; a repair claim needs no repair start; the positive control need only reach 0.5; the bound uses the largest founder count.
  - G10.ruler: a ruler with no known positive is accepted.
  - G12: L1 without "resources"; L2 without "attack_round"; ORIGIN, TRANSFER and ECONOMY need nothing; a level may be skipped.
  - G8 alpha 1e-6 to 1e-3; G4 preflight removed (30 episodes then PASS where the original is BLOCKED).
  - Cause for G12: `test_harness.py:376-381` iterates `claims.L1` and `claims.L2` themselves. `meta.py:36-43` spells out required lists for three gates and not for facets.
  - Fix: report both figures; pin L1, L2 and KIND outside `claims.py`; add a mutant per kind.
- **N6 [new]. D3:104-105, D2:123-124, HR:66-67.** "What was found is now a registered mutant or a known escape" is not true of six round-one cases. They still pass and are in neither list.
  - Declared per-unit rates in G1; a declared rate at n = 20 in G2.
  - A registry that calls the builder a positive in G10.ruler (the strong claim then PASSES).
  - A variable nobody wrote down in G10.contrast.
  - Two prose labels in G7.report.
  - Of the ten gates with "esc 0" (D3:116-160), I found an unpinned passing fault in seven: G1.cell, G2, G7.report, G9.arms, G10.contrast, G10.ruler, G12.render.
  - D2:43-44 "Every gate lists the faults it is known not to catch" is therefore false for G10.contrast, whose blind spot `audits.py:161-162` documents.
  - Fix: pin them.
- **N7 [G8, M22]. `torture.py:10-11, 144-160`; D3:248-251; D2:455-460.** The fitted table memorises whole sequences.
  - The registered xor leak is caught at gap 6 to 12 and passes at gap 16 and 20 (table 1,042 and 1,031 of 2,048).
  - At gap 20 a reader of the last two distractors scores 64 of 64, and the ruler excludes the class.
  - "catches any leak that is a function of what the world shows after the cue" is false. The table also sees only the clock's parity (`retain1.py:378`).
  - Fix: fit on windows of recent observations; state the coverage limit; pin it.
- **N8 [G7.report, M27]. `search.py:145-152`; D3:241-242; D2:438-439.** "Registered seeds" are the seeds the report itself lists.
  - A null on the needle from 128 founders chosen because they missed PASSES; exact reach is 0.7298.
  - A discovery from 128 founders chosen because they hit PASSES.
  - A repair claim at distance 0 PASSES.
  - Fix: take seeds from the registered cell and compare a null with exact reach where it can be counted.
- **N9 [G6.observer, new escape]. `torture.py:84-92`.** An observer that flips one lattice cell between steps (72 flips over 12 seeds) PASSES. Majority repairs each flip before the next recorded state. An observer that writes a field `native()` does not report also passes. Neither is in D2:416-418. Fix: also record state straight after the observer call, or pin both.
- **N10 [G3, new]. `rulers.py:26-31, 89-108`; D2:367-373; D3:206-212.**
  - The panel does not pin alpha: 1e-9 to 1e-2 in the ruler all PASS. A weakest positive of 0.99 passes too.
  - The weak positive plays no part in the bracket. Without it the bracket is still 0.35 to 0.68; the upper end comes from the INVERTED rule on the lowest impostor block (25). At 0.69 and 0.70 the weak positive is still excluded.
  - "Four impostors on nine blocks" are 18 independent trials: three impostors score identically on every block.
  - Fix: say what sets each end; add fixtures near both thresholds.
- **N11 [checker, M44]. RM:86-94.** The description is partly untrue.
  - "Every table is parsed": eight are. D1 sections 1, 5, 7, 11, D2 sections 13, 14 and D3 sections 8, 11 are not.
  - Quotations: the registry maps quote to source, but who the sentence says spoke is not read.
  - Counts written as words are not pinned (CH:151-152).
  - Plants that pass include: B's sentence attributed to C; a registered quote swapped for another; "not built" to "built" and "not measured" to "measured" (D1 section 5); G10.ruler "FAIL at all three" to PASS; "NOT VERIFIED" to "VERIFIED"; "exploratory" to "registered" (D2:208, D2:722); "Ten such cases" to "Twenty"; "Eleven gates have a fault" to "No gates".
  - Fix: reword RM; pin normalised text of the unparsed tables and a word list (verdict words, "not", built, registered).
- **N12 [overclaim]. D2:28-29 "Attainability is computed, not declared".** Three inputs are declared numbers: the per-unit rates (`registration.py:44-59`), the positive's rate in plain preflight (`stats.py:86-105`) and the setting's power (`audits.py:147`). Rates 1.0 and 0.0 with nothing behind them PASS; power 0.99 with nothing computed PASSES. The mutant "power declared as a number, with no rate behind it" (`meta.py:295-296`) is rejected because its values are strings. Fix: "computed from declared rates; from design runs in G2 only".
- **N13 [unseen-pair world; the second reader's lane]. D2:258-276, D3:443-448, D2:695-699.**
  - A store of whole tables with 512 inherited composition schemas, reading no label, scores 13.46 of 16 on the unseen pair (CARRIED) and 3.50 after the control history.
  - So "no to a store of whole tables" holds only for one-table re-indexings.
  - Rule (i) of D2:225-228 fails here as it did in the draft world: 9 bits of selection suffice.
  - Falsifier 6 cannot fire: beating the bound needs information from three families whatever the organism.
  - Fix: name the excluded class; register this organism's answer; restate the falsifier.

### MINOR

- **N14.** D1:277-280 and D2:208-216 give 13.80, 3.42, 4.16, 15.07 as what "the reader" simulated or showed. Those are the author's re-run (`ladder.py`, 300 lives). Mine were 13.79, 3.39, 4.10, 15.06 at 3,000 lives, as RM:121 and `attack/README.md:37-40` say.
- **N15.** D1:402-403 and RM:109 "faults at every layer": five of ten (H3, H4, H5, H8, H9).
- **N16 [unfair to the first draft; my error].** "22 of 25" (RM:115, D2:118-119, D3:100, HR:64) includes one change that alters no verdict, as `mutation_probe.py:26` itself records. The fair figure is 21 of 24. My caveat "chosen after reading the code" was dropped. "65 of 71" counts about nine sweep points or arguable passes among my E labels.
- **N17.** RM:104-127 "in four groups" covers 10 of 11 blockers and 40 of 46 majors; B11, M39-M43 and M46 are in no group.
- **N18.** D2:179-180 "the adversarial reader showed": I argued it and said so.
- **N19.** D1:487-488 and D3:70 "six gates" return INDETERMINATE: five compute it; G12.promote carries a typed facet.
- **N20.** RM:43-44 "nine into what runs or into the registration": point 12 is in neither.
- **N21.** D1:352-354 "B (amortization horizon)": A has it too (A2:271-272, 417-418). D1:186-187 "at once": B puts one cell in days 31 to 55 (B:624).
- **N22.** RM:73-75 "the composition world ... specified and not built" beside RM:60-61 "Simulated here". D2:154-161 lists composition as claimable this round while G10.ruler returns UNQUALIFIED for it.
- **N23.** D1:272 and RM:47 "by anyone": supported for A, B, C and this package.
- **N24.** `test_harness.py:428-430` and CH:591-592 pin the 16-offset keeper as NOT_SHOWN. At 4,000 lives it is CARRIED (mean 4.06, threshold 4.05).
- **N25.** Document 3 section 5 against the code.
  - D3:188 "each used once": design seeds are not checked (`registration.py:75-80`).
  - D3:214-216 "on which G3 returns the truth": the entry gate uses the ruler on 64 seeds, not the G3 gate.
  - D3:233 "at every step": not the last (`torture.py:133`).
- **N26.** Sound cases refused: power given as integer 1 and horizon 3.0 are BLOCKED (`audits.py:147-150`); a cell that registers every episode seed FAILS (`registration.py:86-88`); `render` raises on an unregistered kind (`claims.py:80-81`).
- **N27.** A reset that fails on every third call passes G6.reset (same root as the pinned sleeper). An "impostor" that carries the cue one time in five passes G4.
- **N28.** `meta.py:309-310` registers "run at the clock tick" among the 148 broken cases; it is undecidable, not broken.

## 3. Counts

| Probe | Result |
|---|---|
| Round-one broken cases ported | 70 of 71 (one no longer expressible) |
| Still PASS | 14 (was 65): 8 are instances of a pinned escape, 6 are not pinned |
| Round-one sound cases | 12; 6 not PASS |
| New attacks this round | 14 distinct unpinned passing faults in 11 gates (N4, N6-N10, N12, N27) |
| My one-line logic changes | 44; 34 survive (33 excluding one equivalent) |
| Planted errors in the checker mirror | 69; 35 pass |

- **Pinned instances (8):** G12 typed facet, twice; G5 relabelled machines, twice; G6 unchecked seeds; G7 90% budget and 11 phantom hits; G9 rigged sham cell.
- **Not pinned (6):** as listed in N6.
- **Sound cases not PASS:**
  - Reworded setting, FAIL: not defensible as a shown defect.
  - Capped arms, FAIL: stated design.
  - Empty exposure, BLOCKED: defensible.
  - Same clock tick, INDETERMINATE: defensible.
  - 16 and 19 seeds, BLOCKED: correct, and what I asked for.
- **Checker plants:** all 22 digit plants are caught; 12 of 47 word plants are caught. Of the 33 plants adapted from round one, 29 are caught and 4 pass.
- **Author's probe, re-run:** 54 of 55 noticed, as stated.

## 4. Probes run

All on a scratch mirror with `python -B`, receipts found through `RSO_COUNTERFEIT`.

| Script | What it did |
|---|---|
| unit tests | 59 pass, 4.5 s |
| `run_harness.py`, `mutation_probe.py`, `replay_attack.py` | Each regenerated its receipt identically |
| `p20` | All 148 mutants with reasons |
| `p21` | The 71 + 12 round-one cases ported to the new API |
| `p22` | 44 logic changes of my own |
| `p23` | New attacks on G3, G6, G7, G8, G10, G11, G12 |
| `p24` | Fire test of the new checker, 69 plants |
| `p25` | Unseen-pair world with a label-blind schema cache; keeper at 300, 1,000 and 4,000 lives |
| `check_hardening.py`, in place | 50 of 50 |

## 5. Checked and found sound

- **Quotations.** All 49 are verbatim in the source they are registered to. I read each new B quote in context; only N2 stretches one.
- **Allocation table (D1 section 6).** Equals A, B and C; each sums to 100; the comments under it are right.
- **Mutants.** The registered reason matches the name for 146 of 148. The exceptions are the string-typed "power" mutant (N12) and the "structure" mutant (M31).
- **Attack folder.** Holds my brief and report as written. My eight scripts are byte-identical. `first_version` is the harness I attacked.
- **Exact null.** 3.38 = H_16; the numbers quoted for the two-boundary world match the receipts.
- **Two-boundary world.** The text now claims only retention across the epoch boundary, which is what the simulation supports. B9, B10 and M33-M38 are closed.
- **Worktree.** No file changed and no bytecode written by these runs.
