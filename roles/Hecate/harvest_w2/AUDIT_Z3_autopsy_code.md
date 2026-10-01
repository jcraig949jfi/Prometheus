# AUDIT Z3 -- executable semantics of the novelty autopsy code (flow.py, reach.py)

Auditor: Hecate W2 sub-auditor Z3, 2026-09-30 (read-only; local Python; no
model/API calls; no git writes). Worktree hecate-base-role @ 7ab70b843.
Targets: hecate/autopsy/flow.py, FLOW.json, reach.py, REACH.json,
reach_rows.jsonl, AUTOPSY.md; PREREG roles/Hecate/prereg/2026-09-30_novelty_autopsy/.
Not repeated: K5, K6 (CORRECTIONS_2026-10-01.md), ATTACK_D, INV_H.
Scratch re-runs: .../scratchpad/Z3/FLOW_rerun.json, .../scratchpad/Z3/REACH.json
(flow.flow() called directly; reach.HERE redirected so committed files untouched).

## Summary

    id   finding                                              changes a reported number
    Z3-1 FLOW.json / AUTOPSY Part A are stale vs K4               YES (5 numbers)
    Z3-2 "admitted" counts 3 NOT_BUILT worlds as probed            YES under the docstring's own definition
    Z3-3 "untestable as specified" lumps build/instrument failures NO (number) / YES (attribution text)
    Z3-4 join mechanics (ids, rounds, multi-world mechanisms)     NO -- correct
    Z3-5 SIGNAL / Pass 4 / survived_pass4 semantics               NO -- correct, one cosmetic gap
    Z3-6 PREREG Part A selector-vs-chance item not computed        NO (disclosed as provenance gap)
    Z3-7 8 pilot-built, unprobed round-2 worlds: invisible stage   NO (descriptive omission)
    Z3-8 reach.py: rows, joins, Wilson, medians, decision          NO -- all reproduce exactly
    Z3-9 FLOW.json not byte-reproducible (set-order dict keys)     NO

## Re-run diff

REACH.json: re-run is byte-identical to the committed file.
FLOW.json: differs (all differences are K4, plus dict key order in forms_admitted):

    field                                          committed  re-run (post-K4 program.json)
    survived_probe.worlds_with_valid_reading_or_signal   25      24
    survived_probe.worlds_untestable_as_specified         12      13
    survived_probe.mechanisms_read_validly                38      36
    world_outcomes.NULL                                   19      18
    world_outcomes.SPEC_UNATTAINABLE                       6       7
    parked                                   PARK 15, PROBING 1   PARK 14, PROBING 1, SPECULATIVE 1
    forms_admitted                             same values, different key order

FLOW.json was committed in e4a05ba3b (09-30 04:25 -0400); K4 was applied to
HT-a9e2ba7618/program.json in 684ffbbd1 (09-30 20:38 -0400). flow.py was not
re-run and AUTOPSY.md's CORRECTIONS banner cites K5/K6 only.

## Z3-1 FLOW / AUTOPSY stale vs K4 -- changes a reported number: YES

a9e2 W3 (mechanism_ids M3, M12) is now SPEC_UNATTAINABLE. Neither mechanism
appears in another probed world of a9e2 (W4 is M5), so both leave
"read validly". Before -> after in AUTOPSY.md Part A:

    read validly (valid reading or SIGNAL)   38 (0.16)  ->  36 (0.15)
    worlds untestable as specified           12         ->  13
    NULL                                     19         ->  18
    "(2) specification -- 12/37 probed worlds could not be read" -> 13/37
    programs PARK 15, PROBING 1             -> PARK 14, PROBING 1, SPECULATIVE 1
Unchanged by K4: generated 243, admitted 58, behind SIGNAL 6, Pass 4 0,
worlds 80/37, SIGNAL 5, CONFOUNDED 1, forms_admitted, K5's 58/117.
K13 already records the post-K4 verdict tally (PARK 14 / PROBING 1 /
SPECULATIVE 1) and annotates PROBE_ROUND2_REPORT, but nothing annotates
FLOW.json or the AUTOPSY Part A table. No conclusion in Part C changes.
Fix: re-run `python -m hecate.autopsy.flow` and add K4 to the AUTOPSY banner.

## Z3-2 "admitted" includes NOT_BUILT worlds -- changes a reported number: YES (definition-dependent)

flow.py: a mechanism is admitted if it is named by ANY world with a non-empty
outcome (`if not out: continue`). The flow.py docstring and the AUTOPSY table
both define admitted as "a probed world was BUILT on it". Three worlds have
outcome NOT_BUILT (8a87 W1, e106 W2, faa9 W2; the latter two raw_outcome
INSTRUMENT_FAIL re-labelled NOT_BUILT). Five mechanisms are admitted only
through them: 8a87 M8, e106 M1, e106 M6, faa9 M3, faa9 M15.

    measure                              as coded   built-world definition
    worlds probed                           37            34
    mechanisms admitted                     58            53
    fraction ever tested                  0.239         0.218
    never tested ("76%", "185")         185 / 76%     190 / 78%
    K5 admission among specified        58/117        53/117
The PREREG's own wording ("mechanisms behind a probed world") is ambiguous
on whether a selected-but-unbuilt world was probed; the code's choice is
defensible but contradicts its docstring and the AUTOPSY row label. Either
relabel the row "admitted (selected for a probe)" or exclude NOT_BUILT.
Read-validly / SIGNAL counts are unaffected (NOT_BUILT is not in VALID).

## Z3-3 "untestable as specified" bucket -- number NO, attribution text YES

NO_WORLD = INSTRUMENT_FAIL (3) + NOT_BUILT (3) + SPEC_UNATTAINABLE (6; 7
post-K4). AUTOPSY writes "(2) specification -- 12/37 probed worlds could not
be read". Only the SPEC_UNATTAINABLE worlds failed for specification
reasons; 6 are build / instrument failures (round 1 harness). Corrected
reading: 13/37 unreadable post-K4, of which 7 by specification and 6 by
build/instrument failure. The count is right; its attribution to
"specification" is not.

## Z3-4 Join mechanics -- NO

- Join is per program: mechanisms keyed (programId, hypothesis id); worlds
  join on w["mechanism_ids"] exact string match, filtered `m in mechs`
  (kind == "mechanism"). No string/prose matching anywhere.
- Checked all 16 programs: 0 duplicate hypothesis ids, 0 duplicate world
  ids, 0 triplicateId mismatches, 0 mechanism_ids not resolving to a
  mechanism (so the `if m in mechs` filter drops nothing), 0 repeated ids
  within one world, 0 worlds missing the key.
- Rounds: round-1 (passId P3, 64 worlds) and round-2 (P3v2, 16) worlds share
  the program's single mechanism namespace; no id is re-used for a different
  mechanism, so cross-round joins are sound.
- Multi-world mechanisms are de-duplicated by set union (e.g. 056d M1 in W1
  INSTRUMENT_FAIL and W4 NULL counts once, as read validly; 8a87 M1 in W1
  NOT_BUILT and W5 SIGNAL counts once, as SIGNAL). Correct.
- forms_admitted: the comprehension filters the cumulative set by tid, so
  no cross-program leakage; sums to 58. Correct.
- Totals independently recomputed: 243 mechanisms, 111 interpretations,
  80 worlds, 43 worlds with no outcome, 117 mechanisms in any world.

## Z3-5 SIGNAL / Pass 4 semantics -- NO

- "behind a SIGNAL" = mechanisms of outcome == SIGNAL worlds: 321a M3,
  5516 M12, 5b0b M11+M13, 71b6 M2, 8a87 M1 = 6. Matches PREREG.
- pass4 predicate in program.json equals PASS4_OUTCOME.json for all 5
  SIGNAL worlds (ORIG_FOSSIL_ALT_PASS 1, PARK 4); no pass4 on a non-SIGNAL
  world; no SIGNAL world without pass4.
- survived_pass4 = count of predicate "SURVIVES" (the pass4 vocabulary:
  SURVIVES -> PROMISING, ORIG_FOSSIL_ALT_PASS -> PROBING, PARK). 0 is
  correct. Cosmetic: the table's "survived Pass 4 0" hides that 321a W1 had
  ALT PASS with ORIG fired (FOSSIL); that row is the contested C2 item and
  is visible in FLOW.json attacked.pass4.

## Z3-6 PREREG Part A item not computed -- NO

PREREG Part A also asks for each generator's "most likely familiar in
disguise" mechanism and whether the lowest-cost selector chose it more or
less often than chance. flow.py computes neither. AUTOPSY discloses that the
self-assessment never reached committed records (provenance gap), so this is
a disclosed deviation, not a hidden one; it should be listed as "PREREG item
not executed" rather than only as a provenance remark.

## Z3-7 Invisible stage: pilot-built, unprobed round-2 worlds -- NO

8 worlds have a frozen ATTAINABILITY.json + control rows but no outcome
(056d W6, 37e3 W6, 5516 W5, 8a87 W6, 9744 W5, ae38 W6, e106 W6, faa9 W5):
round-2 candidates built and controlled, then not selected. flow.py treats
them exactly like never-built specs. They carry 9 mechanisms, 7 of which are
never admitted elsewhere. No number is wrong, but "loss at specification"
(K5) and "loss at admission" both absorb a third stage -- built and passed
pilot, not selected -- that the flow does not show.

## Z3-8 reach.py -- NO

- 62 rows, 62 items (KNOWN 20, ALIEN 32, DESTROY 10, as PREREG); 0 duplicate
  item ids (the dict-by-item would silently keep the last), 0 rows without
  item, 0 items without row, 0 ok=false; one detector sha (91fbe8f2...).
- Row order equals the seed-20260930 shuffle; blind_text equals
  scrub(describe(params)) for 62/62 (inputs unchanged since the run; the
  scrubbing itself is K6).
- Wilson: formula correct. Independent recompute (z = 1.95996):
  0/32 upper 0.10718 (reported 0.107), 0/20 0.16113 (0.161), 0/10 0.27753
  (0.278). Clopper-Pearson upper for 0/32 would be 0.109; irrelevant to
  the decision, R1 uses the point rate (0.0 <= 0.10). ATTACK_D's 0/24 -> 0.138
  and 0/21 -> 0.155 also verified. Lower bounds print "-0.0" (float
  cancellation, cosmetic).
- median_prior_fit takes sorted(...)[n // 2], the UPPER median for even n,
  and indexes the numeric-filtered list with the unfiltered n (would shift
  or IndexError if any prior_fit were non-numeric). Neither bites here:
  all 62 numeric; statistics.median gives 0.93 / 0.85 / 0.90, identical.
- Decision branch order (R1 checked before R2) matches PREREG; with all
  three rates 0.0, R1 fires. counts / FAMILIAR-COMPOSITE split
  (ALIEN 28/4) reproduce the AUTOPSY Part B table.

## Z3-9 Reproducibility -- NO

forms_admitted is built by iterating a Python set of strings, so its key
order depends on PYTHONHASHSEED; FLOW.json is not byte-reproducible even
when values are. Values agree. Sort keys on write.

## Dropped rows

None. Every program.json world with an outcome (37) enters world_outcomes;
every mechanism id resolves; every Part B item has exactly one ok row. The
only exclusions are by definition (no-outcome worlds; adversarial aliens and
non-DESTROY nulls in Part B, as PREREG).

## Recommended record actions (not applied; this audit edits nothing)

1. Re-run flow.py; annotate AUTOPSY banner with K4 (Z3-1).
2. Relabel or redefine "admitted" re NOT_BUILT (Z3-2); split the
   "untestable" bucket into specification vs build/instrument (Z3-3).
3. Sort FLOW.json keys; use statistics.median in reach.py (Z3-8/9).
