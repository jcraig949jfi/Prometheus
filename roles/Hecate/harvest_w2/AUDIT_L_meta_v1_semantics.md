# AUDIT L -- meta-experiment v1: what the analysis code actually implements

Auditor: read-only subagent (Hecate harvest_w2), 2026-09-30.
Scope: roles/Hecate/prereg/2026-09-29_meta_experiment_v1/PREREG.md (frozen,
e0bd2e312); hecate/meta/{analyze,run_arms,units,scrub}.py;
hecate/gravity/run.py (detect/run_items); hecate/meta/RESULTS_v1.json;
hecate/meta/REPORT_v1.md; arms/arms_v1.jsonl, detector/detect_rows_v1.jsonl,
matcher/match_rows_v1.jsonl. No git writes, no network, no model calls.
Scratch: <scratchpad>/L/rerun.py (scratchpad = C:/Users/jcrai/AppData/
Local/Temp/claude/F--prometheus/dd0c3882-b7cd-448c-8a58-3c002b4bbbc8/scratchpad).

## 0. Baseline facts established first

- Reproducibility: analyze.m1/m2/m3 re-run on the current tree, serialised
  exactly as main() does, into scratch: byte-IDENTICAL to RESULTS_v1.json.
- analyze.py unchanged since its freeze commit 65e0fcf80. run_arms.py
  changed once since (684ffbbd1: gate path CALIBRATION_v1.json ->
  gate_v1.json, the K3 correction); no effect on any row or number.
- Arms: 40/40 status OK; one form-only regeneration (u4-G, 2 attempts).
  All 40 recorded prompt_sha256 equal sha256 of prompts rebuilt from
  units.arm_prompts(); all 40 concept lists equal units() order.
  units() implements the PREREG seeds exactly (SEED+100 unit shuffle of
  sorted ids, first 8; SEED+200+i concept order).
- Detector: 400 rows, 400 unique items, no duplicates for _latest() to
  overwrite. Row order == run_arms.detect_items() (SEED+400 shuffle;
  first 80 positions G22 O19 T17 S11 P11, interleaved). For all 400 rows
  blind_text == scrub(mechanism_text(m)); scrub_leaks empty for all 400;
  scrub.check() re-run on every blind_text finds 0 dictionary/field names.
- Matcher: 160 rows (80 T, 80 P), all ok. match_items() rebuilt locally:
  160/160 prompt_sha256 match, 160/160 answer letters match. check() on
  every matcher mechanism text: 0 leaks. Answer positions A41 B35 C43 D41.
  The 16 frozen triples share no concept (decoys never contain a true
  concept).

## 1. Findings

F1. A detector (scorer) refusal is silently dropped from the denominator;
    under the PREREG's own wording it flips the M1 vs-P verdict.
    Code: analyze.py:52-59 -- `if not r.get("ok"): failed += 1; continue`,
    then frac = sum(v)/len(v), i.e. FAMILIAR / SCORED items.
    PREREG (M1): "The fraction of a unit-arm's 10 mechanisms that the
    gravity detector classifies FAMILIAR." No rule for unscored items.
    The failed row is u4-P-m8: rc 0, call ok, raw = "Understood. I won't
    regenerate that analysis or a reworded version of it, so this task is
    left without a completed answer." -- a model refusal by the scorer,
    not a property of the arm. It was never retried (run_items retries
    non-ok rows only on a re-invocation, which did not happen).
    Unit 4: T = 2/10 FAMILIAR; P = 2 FAMILIAR of 9 scored.
      code (/9):               P = 0.2222  T 0.2 < 0.2222 -> T_lower TRUE
      PREREG literal (/10,
        unscored = not FAMILIAR): P = 0.2000  tie -> NOT lower
      unscored item FAMILIAR:  P = 0.3000  T_lower TRUE
    Recomputed vs P:
      reported: T lower 5/8, p = 0.363, INDETERMINATE
      literal:  T lower 4/8, p = 0.637, NO_ADDED_VALUE_vs_P
    So the vs-P verdict is not determined by the scored data: it is
    INDETERMINATE only if the refused item would have been FAMILIAR, and
    the /9 denominator is an imputation (it scores the missing item as
    2/9 FAMILIAR). Arm mean P: reported 0.140 (0.1403); /10 gives 0.1375
    (0.138); if FAMILIAR, 0.150. M4 P u4 = 9 is also this item.
    OVERALL is INDETERMINATE under every resolution (ADDS_VALUE vs P is
    unreachable; NO_ADDED_VALUE vs O does not hold), and the "not worth
    continuing" trigger is unaffected.
    REPORT_v1.md also states "T and P are indistinguishable on M1 (5/8)";
    under the literal rule the preregistered outcome is NO_ADDED_VALUE_vs_P,
    which is a stronger statement than "indistinguishable".
    Fix: re-score u4-P-m8 (one detector call, fresh context, same
    detector_sha256) or report vs-P as NO_ADDED_VALUE (literal) with the
    /9 alternative as sensitivity; record the refusal as scorer failure.
    Changes a reported number or decision: YES (vs-P verdict
    INDETERMINATE -> NO_ADDED_VALUE_vs_P under the literal PREREG
    denominator; 5/8 -> 4/8; p 0.363 -> 0.637; P mean 0.140 -> 0.138).

F2. The vs-P result is one item away from a different verdict in four
    units, not one. Per-unit T vs P FAMILIAR counts (of 10): u0 0/0 tie,
    u1 0/1, u2 0/1, u3 1/1 tie, u4 2/2(+1 unscored), u5 0/2, u6 1/2,
    u7 3/2. A single P mechanism reclassified FAMILIAR->COMPOSITE in u1,
    u2, u4 or u6 turns 5/8 into 4/8. Given the report's own finding that
    the FAMILIAR/COMPOSITE boundary is unstable, the vs-P INDETERMINATE is
    knife-edge. Descriptive; no rule is misapplied.
    Changes a reported number or decision: NO (fragility statement).

F3. M3 "state named" for T and P is a schema-type artifact, and the
    REPORT draws a conclusion from it.
    Code: analyze.py:129-130 -- counts only `isinstance(we, list) and
    len(we) >= 2`.
    PREREG (M3): "state named (what_exists lists >= 2 items)".
    Rows: every non-counted T and P mechanism comes from three whole
    unit-arms whose generator emitted what_exists as a STRING (T u3, T u6,
    P u3; 30 mechanisms). Every one of those strings names >= 2 items
    (comma/semicolon separated, e.g. "state grid s, time index t,
    cost-to-go tensor V[s,t], CP factor matrices ..."). The single S
    miss is a 1-element list naming three things ("sites with scalar
    state, threshold, and a refractory countdown timer").
    Recomputed (string split on , ;):
      T 0.750 -> 1.000; P 0.875 -> 1.000; S 0.9875 (1.000 if the list
      element is split); O 1.000; G 1.000.
    REPORT_v1.md item 5 "T ... has the fewest named state variables
    (0.75 vs 0.875-1.0)" is therefore false: no arm differs.
    Changes a reported number or decision: YES (secondary number; no
    decision rule attached; T 0.75 -> 1.00, P 0.875 -> 1.00).

F4. M3 comparator regex adds a term the PREREG does not list.
    Code: analyze.py:118 includes `vs\.?`.
    PREREG: "(baseline / null / control / versus / than / compared)".
    Recomputed without "vs": T 0.750 (same), P 0.600 -> 0.5625,
    O 0.5625 -> 0.550, S 0.4625 -> 0.400, G 0.4375 -> 0.425. REPORT range
    "0.44-0.60" becomes 0.40-0.56; T still highest. "vs" is arguably a
    spelling of "versus"; flagged as an unlisted extension.
    Changes a reported number or decision: YES (secondary numbers only;
    no decision).

F5. M2's 0.25 chance level is the wrong null for the claim, and the
    report's description of the decoys is inaccurate.
    Code: run_arms.py:108-140 (decoys = 3 random other frozen triples).
    PREREG (M2): "Chance = 0.25"; LABELS_SHAPE_OUTPUT at >= 36/80.
    A model-free lexical matcher (pick the option whose concept-name
    5-letter stems overlap most with the scrubbed text; ties split)
    scores T 0.742, P 0.729 on the same 160 items -- far above the 0.45
    threshold. The preregistered rule therefore certifies vocabulary
    carry-over, not label-shaped structure; the REPORT says this
    qualitatively (item 3), which is correct and should be kept.
    However REPORT item 3 says "the decoys come from distant triples":
    110/240 T decoy options and 57/240 P decoy options share a Nous field
    with the true set, so decoys are not systematically distant; matching
    succeeds on concept-specific vocabulary despite shared fields.
    Docstring mismatch: match_items() says P decoys use "the first two
    names of the decoy in the decoy's own seeded order"; the code takes
    the first two after rng.shuffle with the item rng (a random pair).
    Harmless to validity, but the docstring is false.
    Verdict per PREREG text is correctly computed (T 80/80, P 78/80,
    p = 6.8e-49 / 2.0e-44, both LABELS_SHAPE_OUTPUT).
    Changes a reported number or decision: NO (interpretive; one false
    descriptive sentence in REPORT item 3).

F6. PREREG's parenthetical p-value for the M1 rule is not attainable at
    its own threshold.
    PREREG: "T < X in >= 7 of 8 units (one-sided sign test p <= 0.035)".
    P(X >= 7 | n=8, 0.5) = 9/256 = 0.03516 > 0.035. The code (correctly)
    applies the count rule (analyze.py:72, wins >= 7), not the p-value.
    Observed counts are 8 and 5, so no outcome sits on the boundary.
    Changes a reported number or decision: NO.

F7. Ties are counted as losses inside a fixed n = 8, as preregistered,
    which makes the reported p-values conservative relative to a standard
    sign test. vs P (2 ties): reported p = 93/256 = 0.363 (5 of 8);
    tie-excluded sign test 5 of 6 -> 7/64 = 0.109. Under F1's literal
    reading: 4 of 8 -> 0.637; tie-excluded 4 of 5 -> 0.188. The
    preregistered verdict rule is count-based, so the rule is applied
    correctly; the printed p should be labelled "ties as not-lower".
    Changes a reported number or decision: NO.

F8. M4 counts distinct free-text strings, not families.
    Code: analyze.py:56-58 -- nearest_priors[0].name, lower(), [:60],
    added to a set. Two spellings of one family count as two. The
    reported saturation (10/10 almost everywhere; P u3 = 9, P u4 = 9,
    the latter only because of the F1 refusal) is partly a string-
    distinctness artifact, consistent with the REPORT calling M4
    uninformative. No decision rule.
    Changes a reported number or decision: NO.

F9. Stale provenance label in RESULTS_v1.json:
    "calibration": "hecate/gravity/CALIBRATION_v1.json (gate PASS)" --
    after K3 the gate lives in gate_v1.json. analyze.py:140 hard-codes
    the string; the REPORT carries the correction note, RESULTS does not.
    Changes a reported number or decision: NO.

F10. Eligibility guard does not fire on scorer failures. analyze.py:65-70
    marks a comparison NOT_ELIGIBLE only if a whole unit-arm has zero
    scored items. Any number of failed detector calls short of 10 per
    unit-arm passes silently into a shrunken denominator (the mechanism
    behind F1). run_arms.py's docstring rule (MISSING -> NOT_ELIGIBLE,
    never imputed) covers arm generation only; detector failures were
    left without a rule, and the code's choice is an imputation the
    docstring forbids in spirit.
    Changes a reported number or decision: covered by F1.

## 2. Checked and clean

- Float thresholds: all M1 fractions are k/10 (or k/9) floats compared
  with `<`; equal integer counts over equal denominators give identical
  floats, and k/9 vs k/10 comparisons are far from rounding. No epsilon
  issue. M2 thresholds use integer counts (k >= 36, k <= 25) with an
  n < 80 guard; n = 80 exactly for both arms. 36/80 = 0.45 and
  25/80 = 0.3125 <= 0.32 agree with the PREREG's accuracy thresholds;
  binom P(X >= 36 | 80, 0.25) = 7.9e-5 < 0.001 as stated.
- Sign-test p-values: binom_sf(8,8,.5) = 1/256 = 0.00390625 (reported
  0.0039) and binom_sf(5,8,.5) = 93/256 = 0.36328 (reported 0.363) are
  exact. Ties counted as NOT lower (analyze.py:67), as PREREG says.
- M1 decision mapping (>= 7 ADDS_VALUE, <= 4 NO_ADDED_VALUE, 5-6
  INDETERMINATE) matches PREREG for S, P, O; G computed by the same rule
  and flagged descriptive_only; OVERALL logic (all three ADDS_VALUE ->
  reduce; NO_ADDED_VALUE vs O -> do not; else INDETERMINATE) matches
  PREREG and excludes G.
- vs S and vs O: 8/8 in every unit with large margins (smallest margins
  u4 S 0.2 vs 0.3, u7 S 0.3 vs 0.6, u7 O 0.3 vs 0.5); not sensitive to
  F1. vs G 8/8, descriptive.
- Arm means T 0.0875 (0.088), S 0.775, O 0.8375 (0.838), G 0.850 match
  per-unit fractions. Classification table (T 7/73, P 11/68, S 62/18,
  O 67/11/2 INCOHERENT, G 68/12; 0 UNFAMILIAR; 399 scored) matches rows.
- INCOHERENT (2 in O) counted as not FAMILIAR, consistent with PREREG
  "classifies FAMILIAR".
- M2: no failed matcher calls (160 ok); n and k recomputed from rows;
  wrong answers are u1-P-m5 and u7-P-m1 only. True set for P = concepts
  [A, B], matching the P arm prompt. No concept is shared between the 16
  frozen triples, so no decoy option overlaps the true set.
- Blinding: arm/unit identity never enters detector or matcher text
  (mechanism_text excludes metadata and "form"); detector order
  interleaves arms. scrub() applied twice on the detector path is
  idempotent on these rows (0 "[[X]]").
- M3 change_rule (1.0 everywhere) and intervention_in_world recompute
  exactly as reported (T 0.6625, P 0.8125, S 0.4625, O 0.7375,
  G 0.8125).
- Bootstrap CIs: none in this analysis; no degenerate-CI class present.
