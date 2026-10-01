# REDTEAM Y -- adversarial review of CORRECTIONS_2026-10-01 (K1-K13) and RULING_REQUEST_C1_C8
Read-only; numbers recomputed from rows/code in scratch (exact fractions).
Key: CONFIRMED / DISPUTED (reading or fact wrong) / OVERREACH (numbers hold,
conclusion or procedure goes beyond them).

## Headline
1. Arithmetic is almost all right; defects are readings, causes, procedure.
2. Direction is NOT neutral. Outcome changes APPLIED or recommended APPLY
   mostly favour Hecate's programs or calibration (K1, K4, C1, C5); the
   unfavourable ones (C2, H4 in C7, C6 read strictly) are ANNOTATE-ONLY.
   C8 (unfavourable, APPLY) is the one exception.
3. K4 moved PARK -> SPECULATIVE without a ruling (same class as C1-C8).
4. Factual errors: K9 "Gemini verdict now reads NOT_ELIGIBLE" (not in the
   committed file); K4's cause (KC=1.6 repair made the clause unattainable).

## Per item
K1 55162 W6 ORIG "FIRED in substance" -- OVERREACH
- Rows (W6/pass4/rows.jsonl, ALT_TREATMENT, sigma 0.05): r=0.65 LLE -0.956..
  -0.853; r=0.8 LLE -0.057..-0.034; ARI 1.0 on 10/10 seeds at both; traj_std
  0.53-0.59. Numbers CONFIRMED.
- Caveat misstated: ORIG's frozen grid (pass4/NOTES.md) already had sigma
  0.05, and r0.2/sigma0.05 was readable and did NOT fire. The deviation is
  the CARRIER (frozen r=0.2), not sigma.
- The frozen firing rule needs a readable variant (PC groups, cheat groups,
  twin not). At r=0.65/0.8 no ORIG PC was run and the ALT cheat rows equal
  the twin rows, so readability is uncheckable. The evaluator recorded "ORIG
  as preregistered (r=0.2) did not fire".
- No verdict change; it rescues calibration ledger row 4 (self-serving).
  Fix: annotate "ALT rows show non-chaotic grouping"; keep row 4.
K2 affine 0.44 vs Claude 0.33 -- CONFIRMED (claim fails); framing OVERREACH
- Affine is fitted only if max(dims) <= 7 (baselines.py:168): 5 of 8
  adversarial systems. The original compared affine eval (n=5) with Claude
  T2 (n=8; 0.3255). Same 5 systems: T2 0.5125 vs 0.4875; eval 0.5132 vs
  0.4357. CONFIRMED.
- Claude eval is over 200 states, affine over 100 ([:100]); on the same 100
  Claude is 0.508. Affine wins T2 on 3/5 systems (37739, 42741, 46005); the
  lead is the two vm systems. Harmonia's "comparable on the affine-runnable
  subset" is the right restatement; "KILLED" plus Claude-ahead numbers tilts
  toward Claude.
K3 gravity controls overwritten -- CONFIRMED; cited evidence circular
- b15a475b8:hecate/gravity/calibration_v1.json holds {table, gate} (gate
  output). Gate re-derived in scratch: knowns 8/8, nonsense 0/4, composites
  2/2, PASS, identical to the committed gate.
- Circular: scrub changes none of the 14 texts (text == blind_text 14/14), so
  "restored texts scrub to recorded blind texts" proves only that they match
  the rows, not their source. accept lists are unrecoverable from the rows.
- Real provenance: transcript Write 2026-09-30T02:14:35Z is byte-identical
  to controls_v1.json; cite it. test_no_paths_differ_only_by_case cannot fire
  on the original failure (one name survives an overwrite).
K4 a9e2 W3 NULL -> SPEC_UNATTAINABLE -- DISPUTED (cause) + OVERREACH (procedure)
- W3/rows.jsonl: osc-comp ARI max 0.000 in PC and treatment (0/50 > 0); twin
  > 0.02 on 35/50 (median 0.072). Numbers CONFIRMED.
- Cause false: pilot_rows_attempt1.jsonl (KC=5.0, before the repair) already
  has PC osc-comp max -0.024, 0/50 > 0 (seed 0: 0.925 - 1.0). With PC comp
  ARI 1.0 and strong locking, osc = comp follows from the spec.
- The round-2 PREREG defines SPEC_UNATTAINABLE operationally as "pilot failed
  twice"; this pilot PASSED attempt 2. K4 swaps in the parenthetical
  definition after seeing a NULL. Counter-case: "osc > comp + 0.02" is the
  spec's own failure clause, and no oscillator gain may be the true answer.
- PARK -> SPECULATIVE (favourable) applied without a ruling; see S1. Revert
  to annotation and rule jointly with 79e9/W1, 47f4/W1, faa9/W1.
K5 autopsy Part A -- CONFIRMED (numbers); mild OVERREACH
- 243 mechanisms, 117 in a world, 126 never, 58/117 admitted; chi2 17.37,
  permutation p 0.181 (20k). Specification is a fixed budget (4-6 worlds x
  1-3 mechanisms; form skew there p 0.63): a count, not content filtering.
- Stale, unannotated: FLOW.json and the AUTOPSY table predate K4. A live
  flow gives read-validly 36 (file 38), NULL 18 (19), SPEC_UNATT 7 (6),
  PARK 14 (15).
K6 autopsy Part B -- partly CONFIRMED; one DISPUTED fact; OVERREACH
- Scrubber erased 8 ALIEN/4 KNOWN/2 DESTROY rule lists; R1 0/24 CONFIRMED.
- 23 items (not 22) have prior_fit <= 0.50; the 23rd (u3-O-m0, 0.35) is
  INCOHERENT. "All 22 COMPOSITE" selects by outcome; the 0.50 cut is post hoc.
- "No UNFAMILIAR at any prior_fit" restates the zero; with no positive prose
  control (ATTACK_D s2: "a sink, not a demonstrated failure"), calling it
  "better evidence" is absence-as-confirmation.
- The autopsy PREREG froze R1's consequence as "supports C4/C6"; K6 rewrites
  it as "C6, not C4" and applied it rather than escalating.
K7 sandbox rejections -- CONFIRMED with omission
- 5 programs on 4 systems (not 4 programs). SYS-59756, SYS-96628 -> eval
  exact 1.0; SYS-29593 stays 0/200.
- Omitted SYS-91678 (DSCRAMBLE): 61/200, 64/200 unsandboxed; still not
  learned, but the DSCRAMBLE code-exact mean moves (unreported).
K8 false-collapse story -- CONFIRMED (narrative); OVERREACH ("artefact")
- SYS-46959 code is a two-shear lookup step (no sine): story false. But the
  row meets the s4 T6 definition exactly (PARTIAL, eval exact 0.085,
  comp 0.18, confidence exactly 0.6 vs >= 0.6). "0/32 genuine" redefines the
  class; it is not a classifier bug.
- Unstated: 0/32 vs 0/20 -> CI [0,0] -> H5 NOT_SUPPORTED under s6 (not drawn).
K9 concurrency + Gemini verdict -- concurrency CONFIRMED; verdict DISPUTED
- Starts: gpt-oss 05:40:48Z, Claude 05:41:09Z, Gemini 05:42:50Z, against s10.
- runs/gemini/RESULTS.json:246 still reads NOVELTY_DETECTOR_NOT_VALIDATED,
  all inputs null. Only analyze.py:314 changed (684ffbbd1, a second
  post-freeze edit); no RESULTS regenerated. runs/gptoss/RESULTS.json:286 has
  the same defect. Fix the text or regenerate under an announced patch.
K10 scorer crash on vector claims -- CONFIRMED
- Std TRUE 26 -> 30; recall 17/32 -> 18/32; K TRUE 38 -> 42; code exact
  1591/2000 = 0.7955 (n=30) -> 0.8083 (n=32); AUC 187/192 = 0.9740 ->
  0.9760. Also moves, unreported: DESTROY TRUE 3 -> 4, FALSE 2 -> 3.
K11 taxonomy / SYS-60800 -- CONFIRMED with wording errors
- 5 RSWM: adversarial, 0 TRUE; but SYS-37739 is ABOVE its bar (0.300 > 0.283).
- SYS-60800 bar 241/300 + 1/5 = 301/300 > 1: USEFUL_PARTIAL is unattainable,
  but CORRECT_ANALOGY (>= 0.9) was reachable and missed at 0.81.
- AUDIT_A F07's "6 A systems with bar > 0.8" is a float artefact: SYS-39367's
  bar is exactly 4/5, so the true count is 5.
K12 meta v1 M3 -- CONFIRMED (numbers); ASYMMETRIC reading
- State T 0.75 -> 1.00, P 0.875 -> 1.00; comparator S 37/80 -> 32/80, P 0.600
  -> 0.5625. Unreported: O 0.5625 -> 0.550, G 0.4375 -> 0.425.
- Loose on state (a string accepted as a ">= 2 item list"), strict on the
  comparator ("vs" rejected); both favour T. S's one-element list naming
  three things is not split. A consistent stem reading: T 0.8125, S 0.4875,
  O 0.6375, P 0.575. No decision depends on M3.
K13 verdict re-derivation -- CONFIRMED, conditional on K4
- ROUND2 recounts as recorded, 6/7/8/5 after K4; inherits K4's defects.
C1 ae38 W5 INCONCLUSIVE band -- DISPUTED (asymmetric; favourable)
- W5/probe/OUTCOME.json: S1 = F1 = 0.3336, S2 0.2766, F2 -0.241, F3 0.420; no
  clause met. The band text is in spec alternative_explanation / DESIGN_NOTES
  item 6, not a numbered clause.
- pass3_v2 PREREG uses round-1 classes, and pre-run NOTES rule 4f chose NULL
  explicitly. NULL is the literal frozen outcome.
- Symmetry: 9744/W6 also met no failure clause (S1 0.4505, between F1 0.15
  and S1 0.60) and counted as a valid NULL for PARK; its spec merely lacks
  the word. Applied evenly, 9744 -> SPECULATIVE; 37e3/W5's reason changes.
C2 321a ALT fixed by counting -- CONFIRMED; ANNOTATE-ONLY right
- K_code = 3, K_majority = 0; pigeonhole 31 < 48; 18/31 single agents can
  manipulate. alt_pass = Kc > Km (evaluate.py:125), predicted pre-run.
- Same class as K4, opposite handling (K4 favourable applied; C2 escalated).
C3 79e9 W4 saturation -- CONFIRMED; "NULL likely" support DISPUTED
- 95%-of-max only at levels 4-7, T ~ 8-11; levels 0-2 never (max fraction
  0.03-0.28). PC max fraction 0.016, never in range.
- AUDIT_B's 0.476 pools 80 (level, seed) points. The frozen level-mean
  statistic (n=8): T 1-5 0.714 (between F < 0.5 and S >= 0.8), T 1-8
  0.524, T 1-10 0.452, T 1-30 0.167. NULL is less secure than stated.
C4 ae38 W4 SPEC_UNATTAINABLE kept -- CONFIRMED (no outcome effect)
- Attempt 1: PC passed; the cheat failed only because gamma_oracle is
  undefined at (4,2,0). Attempt 2: PC error 11.3% at (8,0) > 10%. No
  treatment was built.
- Principle inconsistent with K4: K4 overrides a PASSED pilot by substance;
  C4 keeps a procedurally failed pilot that passed in substance.
C5 alien H3 exact arithmetic -- arithmetic CONFIRMED; APPLY OVERREACH
- A passive 8/10, active 9/10; K 4/4 both. (1 - 4/5) - (1 - 9/10) = 1/10;
  PREREG s6 l.131 ">= 0.10"; float 0.0999... (analyze.py:276). All of it is
  SYS-19722.
- The PREREG never specifies exact arithmetic; s4 (l.83) and s10 (l.170-171)
  say score only with the frozen code. Choosing exact here is post hoc and
  yields SUPPORTED.
- s6 preamble (l.123): SUPPORTED also needs CI lower > 0. The preregistered
  bootstrap (2000, seed 20260930) gives CI [0, 0.30], 34% of draws <= 0.
  H3's own line may override the preamble, but Hecate applies the preamble
  to H4 and not H3; shadow_decisions.py:384 emits no CI reading for H3
  despite its docstring (38-39). PREREG labels H3 "descriptive primarily".
- Recommend ANNOTATE-ONLY.
C6 detector alien set -- OVERREACH ("report both" promotes the favourable reading)
- Pairs CONJ 7/7 + DSCRAMBLE 10/11 + SCRAMBLE 2/4 = 19/22 (0.864); SEDUCTIVE
  4/8; all 23/30 = 0.767.
- The PREREG is unambiguous: s1 (l.49-50) puts SEDUCTIVE in incompressible;
  s4 (l.108) says "incompressible pairs (30)". The code follows the text.
- All-aliens AUC 2257/2400 = 0.940 (CI low 0.878) PASSES; that reading fails
  on pairs, not on AUC as written.
- The VALIDATED reading drops exactly the 8 pairs at chance. On the remaining
  22, a trivial "fewer components change" cue scores 18/22 = 0.818 >= 0.80.
  NOT_VALIDATED stands.
C7 H2 / H4 -- PARTLY DISPUTED
- CP upper for 0/32: 0.10888 (95% two-sided), 0.0894 (one-sided); both
  > 0.075 (n >= 48 needed). But the PREREG specifies a bootstrap, not CP:
  substituting CP moves H2 away from NOT_SUPPORTED (favourable).
- H4: binary rule confirmed (analyze.py:293-294); s6 on CI [0,0] gives
  NOT_SUPPORTED. If "frozen text governs" justifies C5, it equally forces
  H4 -> NOT_SUPPORTED, which Hecate leaves ANNOTATE-ONLY.
C8 meta M1 vs P denominator -- numbers CONFIRMED; APPLY DISPUTED
- Unit 4: T 2/10, P 2/9; with /10 a tie, T lower in 4/8 units; sign test
  163/256 = 0.637 (5/8: 93/256 = 0.363). Exact.
- "FAMILIAR / items" is quoted from REPORT_v1.md (post hoc), not the PREREG.
  The PREREG reads "fraction of a unit-arm's 10 mechanisms ... FAMILIAR",
  which supports /10, but the source is misattributed.
- /10 imputes a refusal as not-FAMILIAR. The instrument excludes failed
  calls: run_arms MISSING -> NOT_ELIGIBLE "never imputed"; M2 n < 80 ->
  NOT_ELIGIBLE; the gate requires all_calls_ok. Consistently, P unit 4 is
  ineligible, 7 < 8 units, so vs-P reads NOT_ELIGIBLE (a third reading).
- u4-P-m8 is the only failed call (detector 399/400; matcher 160/160; reach
  62/62). Direction unfavourable (not self-serving); overall M1
  INDETERMINATE under all readings. Recommend ANNOTATE with all three.

## Symmetry: un-flipped decisions the same readings would flip
S1 K4 reading (clause unreachable by construction -> SPEC_UNATTAINABLE):
   79e9/W1 and 47f4/W1 would move toward SPECULATIVE; not flipped. faa9/W1
   has the same PC-only pilot; unchecked.
S2 C1 reading (no failure clause fired -> not a valid NULL): 9744/W6 ->
   9744 PARK -> SPECULATIVE; 37e3/W5 reason only. Not flipped.
S3 C5 reading (frozen TEXT over frozen CODE): H4 -> NOT_SUPPORTED (s6 rule
   on [0,0]); the s6 CI preamble keeps H3 INDETERMINATE; with K8's 0/32,
   H5 -> NOT_SUPPORTED. All unfavourable; none flipped.
S4 C8 reading (the instrument's own failed-call exclusion): vs-P ->
   NOT_ELIGIBLE, not NO_ADDED_VALUE.
S5 K1 reading (substance over frozen readout): 5516 R reproduction (ARI
   -0.111, below chance) would be re-read; not done. S6 C2 vs K4: see C2.
S7 Exact-arithmetic sweep (all float >=, <=, >, < on small-integer ratios
   in hecate/alien, meta/analyze.py:67, autopsy/reach.py:81-83,
   gravity/run.py:94, program OUTCOME/rows JSON):
   - The ONLY outcome flip is H3, toward SUPPORTED.
   - Masked sub-flip: SYS-39367 USEFUL (exact comp = bar + 1/5 -> True;
     float False); no effect, already CORRECT_ANALOGY at exact 1.0.
   - Exact ties holding under both readings: SYS-65579 / SYS-26937 T2 exact
     1/4; SYS-46959 confidence 0.6. Near misses SYS-91403 -1/240 and
     SYS-95220 +1/360 on T2 comp (not decisive). ae38 W4 ratio
     0.8000000000000002 is at a config where 0.8 is not the threshold.
   - No exact-arithmetic flip AGAINST any hypothesis exists. Exact reading is
     a one-sided rescue: adopt it globally and in advance, or not at all.
   - No epsilons in alien decision code; faa9 +/-1e-12 clamps are
     descriptive only.

## Harmonia #1037 items CORRECTIONS does not address
- A minors: the chance band and the r0.2/sigma0 "unreadable" exclusion are
  defined in NOTES, not the PREREG; control-first ordering is unprovable from
  git; pass4_report.py has no round-2 entry.
- B MAJOR: no UNFAMILIAR positive control in calibration is never accepted as
  such. "Composites 2/2 while both called FAMILIAR" stays 2/2 by construction.
- C minors: the post-freeze analyze.py edit (repeated at 684ffbbd1) and the
  self-recorded utc fields are unaddressed.
- Pattern-1 rule (an absence claim needs a positive control) is not adopted.
- Softening: K2 drops Harmonia's "comparable"; K9 "minor, accepted".
