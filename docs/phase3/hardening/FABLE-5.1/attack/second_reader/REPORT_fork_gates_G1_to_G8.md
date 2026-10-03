# Report of the second reader's fork: gates G1 to G8

Verbatim, as it was returned.
3 HTML entities put in by the notification wrapper were turned back into their characters.

---

Scope: harness v2 gates G1.cell to G8.demand and stats.py, attacked on a scratch copy; nothing under F:\Prometheus-worktrees was written.

Every one of the twelve gates has at least one escape that is not in `known_escapes()`, including the five the document 3 table lists with esc 0 (G1.cell, G1.receipt, G2.preflight, G6.restart, G7.report). No documented number in this scope is wrong. Paths below are relative to `...\hardening\FABLE-5.1\harness\rso_harness\`; D2 and D3 are documents 2 and 3.

## Defects

**BLOCKER**

1. **G8.demand: the registered xor leak passes at gap 15 and above.** torture.py:10-11 says "a fitted table catches any leak that is a function of what the world shows after the cue"; D3:250 says the same.
   - Probe: `demand_closure(DEMAND, TRAIN, gap=g, cue_from_distractors=True)` gives FAIL at gaps 6 to 13 (TABLE 2048, 2048, 1917, 1448, 1270), INDETERMINATE at 14 (1124), PASS at 15, 16, 18, 20 (1099, 1042, 1033, 1031 of 2048).
   - A policy that xors the last two distractors scores 64 of 64 at every gap. `gap` is the one World keyword that is not a fault (retain1.py:25).
   - Cause: the table is a lookup over the joint context with a default guess of 0 for unseen contexts (torture.py:158); 2,048 fits cover about 6% of 2^15.
   - Fix: fit low-order tables (each bit and each pair), or return BLOCKED when too few test contexts were seen in training; register gap 16 as a mutant.

2. **G7.report: the "registered seeds" are the report's own.** search.py:146-149 reads `p["seeds"]` from the report and takes no registration; D2:438-439 and the FAIL text say "the registered search on the registered seeds".
   - Probe: a null on NEEDLE with STRICT and NEUTRAL, on 128 founders kept because NEUTRAL missed (195 misses in 700 tried; exact reach 0.7298), right scope, bound 0.0231, gives PASS. The same false null on the registered founders FAILs (meta.py:438).
   - Also PASS: a discovery of 128 hits in 128 founders kept because they hit.
   - Fix: `check_report` takes the cell and requires the report's seeds to equal the registered seeds, else BLOCKED.

3. **G6.observer: equivalence is not shown "on a run's own seeds" (D2:417-418).** torture.py:86-88 runs each seed as one episode in a fresh `World()`, and `final` (retain1.py:88-89) leaves out the world's configuration.
   - An observer that draws from the world's stream in every episode but a world's first passes; on the same 12 seeds as one 12-episode run, 11 of 12 episodes differ.
   - An observer that sets `world.leak_key="plain"` after the probe passes; a probe reader then scores 63 of 64, which class exclusion calls EXCLUDES.
   - Fix: compare a multi-episode run in one world, and put the world's configuration in the final state.

**MAJOR**

4. **G6.restart (listed esc 0).** The harness's own `SneakyRegister` passes: the uncut hidden carry is 1, the restored one is 0, and reported state is equal. Also PASS:
   - a restore that a never-used runtime ignores (word (1,) restored gives (None,));
   - a restore that corrupts when the target already holds the same word (the check always supplies the opposite cue);
   - a capture that is wrong at the last step only: torture.py:133 cuts at steps 0 to 6 of 8, while D3:233, D2:413 and torture.py:119 say "at every step".

5. **G6.reset.** A carry set by a no-cue episode and used in the very next one passes (blank episode, then cue 1, answers 0). The earlier episode is always cued (torture.py:110-112). This is one episode ahead, not the listed two-episode sleeper. A reset that works twice and not a third time also passes.

6. **Vacuous PASS on empty or tiny input.** With `seeds=[]`, `observer_equivalence` (with the greedy observer), `reset_closure` (leaky reset), `restart_equivalence` (no-op restore) and `calibration` all return PASS. With 1 to 5 founders every count passes calibration. `combine([])` is BLOCKED by the harness's own rule. Fix: BLOCKED on empty; INDETERMINATE when no count could fail.

7. **G7.calibration on degenerate cells.** An estimator that never searches passes VALLEY/STRICT/COLD (a registered sound cell, meta.py:411), NEEDLE/STRICT/COLD and VALLEY/NEUTRAL/COLD. One that reports every founder a hit passes ASCENT/STRICT/COLD (registered sound cell, meta.py:410) and VALLEY/STRICT/REPAIR. Nulls are claimed exactly where exact reach is 0. A half-budget estimator also passes on 256 founders picked after the fact (187 hits; its true rate is 0.497). Fix: UNQUALIFIED where exact reach is within resolution of 0 or 1; bind founders to a registration.

8. **G8: the table fitted on nothing.** The xor leak at gap 6 with `train_seeds=[]` or 8 seeds gives PASS (16 seeds: FAIL, 1262). torture.py:175 checks only that the sets are disjoint. Fix: BLOCKED below a registered training size.

9. **G8: baselines are required by name** (torture.py:172). `writable_mark=True` with a constant under the name WORLD_PARKER gives PASS; with the real list it FAILs.

10. **G8's listed escape is an artefact.** `Recorder` keeps `obs.clock & 1` (retain1.py:378). With `& 3` (patched in memory) the bit-1 leak FAILs (TABLE 2048) and the sound world still passes. D3:250 "everything the world shows" is false, and D3 section 11 blames the list.

11. **G8 margin.** A class at true rate 0.54 is called WITHIN with probability 0.73 at 2,048 episodes. At that rate P(51 or more of 64) is 1.7e-5 against 9.4e-7 at one half, so the ruler's false-yes rate is 18 times higher. Not stated anywhere.

12. **G2.preflight: PASS does not make the negative's answer attainable.** stats.py:103-104 checks `1 - alpha >= floor`; `classify` gives NEGATIVE only at or below `lower_critical(n, p_positive)`.
    - Probe: n=18, bound 1/50, weakest positive 0.6, alpha 1e-6 gives PASS with power 0.994, while P(class member is answered NEGATIVE) is 0.695.
    - 56 such settings in my grid at the smallest admitted n (bounds 1/50 to 1/10 among the worst). At the registered setting it is 0.99996.
    - Declared inputs are also believed: `preflight_from_design(64, .5, 1e-6, 10**6, 10**6)` and a rate of `True` both PASS.
    - Fix: compute P(AT_BOUND | p0) through `classify`.

13. **G1.cell: attainability is computed from a declared rate.** `known_answers={"HOLDS": 1.0, "FAILS": 0.0}` with `design_seeds=[]` gives PASS. The registered mutant "power declared as a number, with no rate behind it" (meta.py:295-296) passes strings and is BLOCKED for being strings ("known answer FAILS needs ... a rate in [0, 1]"), so the named fault is untested. D2:28 "Attainability is computed, not declared" overstates.

14. **G1.cell: other escapes, all PASS.**
    - A two-outcome table with no undecided band.
    - Known answers HOLDS and INDETERMINATE with no "no": P(FAILS | rate 0.2) is 0.11, though registration.py:48 says "a yes and a no".
    - Every descriptive field "tbd", blank or 0 (G10.setting blocks these).
    - `registered_seeds=()` or `range(0)`: registration.py:65 tests membership in `(None, "", [], {})` and :86 skips when empty.
    - A design seed "5000" beside a registered 5000.
    - Design seeds repeated (D3:188 says "each used once").
    - A sound `design_seeds=(1,2,3)` is BLOCKED.

15. **G1.receipt (listed esc 0).**
    - `registered_at="100"`, `ran_at="99"` gives PASS (string comparison, registration.py:118).
    - A receipt reporting HOLDS for a count of 13, or 30 passes of 40 units, gives PASS: outcome fields are not read.
    - A receipt checked against a cell G1.cell would block gives PASS.
    - A sound receipt whose hash was registered as the plain sha256 of a CRLF checkout FAILs (registration.py:96 normalises line endings).

16. **G3.exclusion.**
    - Bound 0.25 with the eight "further blocks" equal to the first gives PASS (rulers.py:99-105 has no distinctness check); the registered blocks FAIL it.
    - A two-answer ruler (yes at 51 or more, otherwise no) passes; it calls an inverter and a 49-of-64 scorer NEGATIVE. The panel has no known INVERTED or UNDECIDED case.
    - A ruler that looks up class names and runs no episode passes G3 and G5 as SHARED.

17. **G3: the weak positive does not bracket the bound.** D2:369-372 and rulers.py:92-94 credit it.
    - The bracket is 0.35 to 0.68 with it and 0.35 to 0.68 without it. With block 0 only it is 0.22 to 0.70; with the INVERTED rule off, 0.35 to 0.71.
    - The upper end is one Attractor-impostor block scoring 25 (INVERTED at 25 or fewer from bound 0.69). The mutant "a bound of 0.70" is rejected by that block alone; the weak positive (61, needs 61) still passes at 0.70.
    - The REGISTER, PACKET and LATTICE impostors are one series: same answer in 64 of 64 episodes, same scores on all nine blocks. "Four impostors on nine blocks" is two series.

18. **G4.entry.**
    - A positive right only in its first 64 episodes passes (64, then 0 of the next 64).
    - A constant answerer as the "matched" impostor passes.
    - A sound pair supplied as lambdas or `functools.partial` gets FAIL "not declared to be of this physics" (rulers.py:125-127); a missing declaration is BLOCKED at most.

19. **G5.neutrality: interchange has no earned negative.** rulers.py:56 returns NEGATIVE as "otherwise".
    - The weak positive follows the donor in 44 of 48 trials and is called NEGATIVE; class exclusion calls it POSITIVE (61 of 64). G5 with it on the panel FAILs.
    - So D3:219-221 ("return the truth in all four physics") holds only because the weak positive is left off the G5 panel.
    - A positive whose restore does nothing is called NEGATIVE and accepted as an impostor: SHARED, PASS.

20. **G7.report: sound reports rejected, degenerate ones passed.**
    - A true cold discovery at 12 proposals (46 of 128, counts replay) and a true repair report at 5 proposals (55 of 128) both get UNQUALIFIED: search.py:153-156 applies the cold-ASCENT control to every claim.
    - A repair claim from distance 0 passes with 128 of 128 (distance defaults to 0, search.py:144).
    - A null with bound `True` or 1.0 passes.

21. **G6.observer, further escapes, all PASS.**
    - An observer that sets `world.skip_reset=True`.
    - One that disturbs only impostors, the weak positive and the baselines; `all_positives` (meta.py:114-120) checks four classes, and the same observer FAILs when run on an impostor.
    - One that changes `Lattice.N` for every later run.
    - `compare="score"` (torture.py:84, 89) with the greedy observer returns an ordinary gate PASS.

**MINOR**

22. In the sound world four of the five required non-table baselines are one series: CONSTANT, KEY_READER and WORLD_PARKER all score 1036 (same answer in 256 of 256 episodes) and CLOCK is the complement (1012).
23. `classify`: from n=81 a score can be both at or above the yes threshold and at or below the weak positive's lower critical (n=128: 92 to 103); the code returns EXCLUDES (stats.py:128). "Five places to stand" omits this.
24. D2:314 says "every registered answer" is attainable at 0.99. The sound cell registers INDETERMINATE with no known case, and its best attainable probability is 0.962.
25. Malformed input raises instead of BLOCKED: a 2-tuple rule (ValueError), mixed clock types (TypeError), a float budget (TypeError). A non-dict verdict table is BLOCKED as "empty cell".
26. Uppercase hex in a receipt FAILs as "other code". A null bound rounded to 0.023 FAILs while 0.024 passes (by design, but a FAIL for a rounding).

## Probes run

All in `...\scratchpad\verify4\h1\` with `python -B` and RSO_COUNTERFEIT set: drv.py, exactbin.py, p01_totals.py, p02_stats.py, p03_g1.py, p04_g2.py, p05_g345.py, p06_g6.py, p07_g7.py, p08_g8.py, p09_followups.py.

- Unit tests in the copy: 59 tests, OK, 4.5 s (11.6 s wall with import).
- `qualify()`: 21 gates, 44 sound cases, 148 mutants; 82 FAIL, 41 BLOCKED, 19 UNQUALIFIED, 6 INDETERMINATE; every gate PASS. `known_escapes()`: 11, one per listed gate.
- Per-gate rows for my twelve gates match the D3 section 4 table. Gates returning INDETERMINATE: G1.receipt, G3, G4, G8, G9.clauses, G12.promote.
- A first version of p02 using Fractions at n=2048 ran past the 10-minute limit and was stopped; the rewrite with integer weights finished.

## Checked and found sound

- stats.py against an independent exact binomial in integer arithmetic:
  - critical count 51 (tails 9.4e-7 at 51, 3.5e-6 at 50), lower critical 13, weak-positive critical 47, power 0.99997 at 15/16;
  - classify bands 0-13, 14-47, 48-50, 51-64;
  - equivalence bands at 2,048: OUTSIDE at 912 or fewer and 1136 or more, WITHIN 929 to 1119;
  - calibration counts 164 to 208;
  - `lower_bound` direction and values (0.7943, 0.9822);
  - `zero_hit_upper` 0.1173 and 0.0231.
- D3 section 6 reach table (1.0000, 0.0000, 0.7298, 0.7757, 0.1797) and 0.7113 at 380 proposals, by an independent chain on bit count.
- Bracket 0.35 to 0.68 is contiguous; impostor scores range 25 to 41; weak positive 61; positives 64 of 64 on all nine blocks.
- The two one-mutant-for-many helpers have the right logic (BLOCKED only if every omission is BLOCKED; `design_seeds=None` is tested).
- All other registered mutants in these twelve gates are rejected for the reason their name gives.
- No false alarm of the sound G3 panel with any of the eight other blocks as the main block; G4 passes on all 4 physics across 9 blocks.
- A null bound rounded to four decimals is accepted for every founder count from 1 to 2,999.
- Train and test seeds are disjoint and the world is re-created between fit and score.
- No `__pycache__` written in the package or the copy.
