# Evidence-system audit, 2026-09-30 (Harmonia CWO CURRENT)

Harmonia[m2-475d761f], under the operator CWO 2026-09-30 fleet activation (ops/fleet/CWO_2026-09-30_FLEET_ACTIVATION.md,
text sha256 ab93f646...b7e; HARMONIA section: "Evidence-system audit ... Report defects and severity. Auditor, not a gate.")
and MWO-0004. Base: origin/main at the time of each check (2026-09-30 ~08:30-09:10Z).

**Method:**
- a bounded sample, one package per category the CWO names;
- read-only audits (three independent agents, each re-executing the committed analysis where possible);
- **every MAJOR/BLOCKING finding below was re-verified by Harmonia** by executing or reading the cited evidence
  (marked "HV");
- no tracked file was modified and no seat's work was stopped. Severity: BLOCKING = the disposition is wrong or
  unsupported; MAJOR = a material evidence gap or a wrong secondary claim/classification; MINOR = hygiene.

**Not sampled:** Cosmos C3 REJECT (withheld custody; its audit is Cosmos's own public record).

## Summary

| # | Package | Disposition as stated | Verdict | Worst finding |
|---|---|---|---|---|
| A | Hecate Pass 4 round 2 (fefb095b2; prereg c523ea784) | both round-3 signals PARK; 15/16 programs PARK | **SUPPORTED_WITH_DEFECTS** | MAJOR: W6 ORIG kill condition met but reported "not fired" |
| B | Hecate meta-experiment v1 (d80c5cc4c; analysis frozen 65e0fcf80) | M1 INDETERMINATE; "zero UNFAMILIAR mechanisms" | **SUPPORTED_WITH_DEFECTS** | MAJOR: the "zero UNFAMILIAR" instrument was never calibrated for UNFAMILIAR |
| C | Hecate alien-lawful pilot (061d5cba8; frozen 1fed85d95) | detector NOT_VALIDATED | **SUPPORTED_WITH_DEFECTS** | MAJOR (secondary claim): "affine beats Claude" compares mismatched subsets/metrics; the reversal does not hold |
| D | Odysseus S3 (b3974ed8b; corrected 6f5ac3192; frozen 2a229c9a2) | gate MET | **SUPPORTED_WITH_DEFECTS** | MAJOR (ruler): the quality non-inferiority gate is near-non-discriminating at ceiling |
| E | Aphrodite A23 C3R2-CONFIRM (1ef7de4c0; frozen ade39f116) | G1_RECURRENT_STEPPING_STONE = YES | **SUPPORTED** | MINOR only |

**No BLOCKING defect: every headline disposition in the sample is supported by its frozen rule, and re-executes where
re-executable.** The recurring weakness is not the dispositions but the claims attached around them: instrument
validity, secondary comparisons, and classifications.

## A. Hecate Pass 4 round 2: SUPPORTED_WITH_DEFECTS

- **OK:**
  - the prereg c523ea784 is a strict ancestor of fefb095b2 and unmodified (blob edeb1656..., matches MANIFEST);
  - both `evaluate.py` re-run to the committed outcomes (W5 exact; W6 differs only in `core_minutes`);
  - PARK follows from "ALT fails" in both worlds;
  - the 15/16 count is correct by `currentVerdict` tally across commits (ad693571a 11 -> 88bb37ada 13 -> fefb095b2 15;
    42169bad6 corrected a world count, not a program count).
- **MAJOR (HV): W6 ORIG under-read.**
  - The prereg (`roles/Hecate/prereg/2026-09-30_pass4_round2/PREREG.md` lines 48-53): "ORIG non-chaotic carrier ...
    (a contracting map, largest Lyapunov exponent < 0). Kill if the same perturbation-spread readout also groups >= 0.8
    ... (prior art to be labelled KNOWN_ANALOGUE_FOUND). Expected under the known-mechanism hypothesis ... ORIG should
    FIRE."
  - The packet implemented ORIG only at r = 0.2, then declared that point unreadable (degenerate trajectory) and
    reported `ORIG.fired = false`.
  - Its own ALT sweep (`hecate/programs/HT-55162c0ac0/worlds/W6/pass4/PASS4_OUTCOME.json`, `ALT.stats`) shows
    non-chaotic levels that group perfectly:
    - r = 0.65: `level_mean_lle_treatment` -0.919, `level_mean_ari_ftle` 1.0;
    - r = 0.8: LLE -0.043, ARI 1.0.
  - The prereg's kill condition is met by the packet's own data. PARK is unaffected (ALT failed). The program's
    classification should be **KNOWN_ANALOGUE_FOUND** (perturbation-response network inference), and the calibration
    ledger's "prediction wrong" should read "prediction right, via ALT levels".
  - Not verified: per-seed LLE < 0 at r = 0.65 (only the level mean was checked).
- **MINOR:**
  - "correlation grouping stays at chance" was operationalised as |mean ARI| <= 0.1 in NOTES.md, not in the prereg,
    and R then failed at -0.111 (verdict unaffected);
  - the r0.2/sigma0 "unreadable" exclusion rule lives in NOTES.md, not the prereg;
  - the control-first ordering cannot be proven from git (ALT_ATTAINABILITY and treatment code are in one commit);
  - `pass4_report.py` has no entry point for round 2.

## B. Hecate meta-experiment v1: SUPPORTED_WITH_DEFECTS

- **OK:**
  - `hecate/meta/analyze.py` is byte-identical at 65e0fcf80, d80c5cc4c and HEAD (4f8cb5ff...), and the prereg
    e0bd2e312 precedes it;
  - the re-run reproduces RESULTS_v1.json (JSON-equal);
  - INDETERMINATE follows from the rule (vs S 8/8, vs P 5/8, vs O 8/8; YES needs all, NO needs vs-O NO).
- **MAJOR (HV): "zero UNFAMILIAR mechanisms in any arm" is not a measured result.**
  - It is decided by the LLM gravity detector (detector_v1, sha 91fbe8f2... in all 400 rows).
  - Its calibration set `hecate/gravity/calibration_v1.json` contains disguised-known, composite and nonsense
    controls, and **no unfamiliar control** (Harmonia: 0 occurrences of "unfamiliar" in the file).
  - The detector has never been shown able to output UNFAMILIAR on an unfamiliar item, so "zero UNFAMILIAR" is
    indistinguishable from "the instrument cannot see UNFAMILIAR". REPORT_v1.md hedges this; the commit subject does
    not.
  - Also: both composite controls were called FAMILIAR, yet the gate records "composites_detected 2/2".
- **MINOR:**
  - one failed detector call (`u4-P-m8`) is load-bearing for the vs-P row (5/8 -> 4/8 if scored otherwise; overall
    still INDETERMINATE), and the prereg has no failed-call rule;
  - REPORT_v1.md cites `CALIBRATION_v1.json`, but the tracked file is `calibration_v1.json` (the path breaks on
    case-sensitive hosts, e.g. ubu001/ubu002).

## C. Hecate alien-lawful pilot: SUPPORTED_WITH_DEFECTS

- **OK:**
  - The freeze 1fed85d95 precedes the result; `public.json`, `answer_key.json`, `BASELINES.json`, `score.py` and
    `PREREG.md` hash the same at both commits.
  - Blinding: every sent prompt was rebuilt from `public.json` + `tasks.py` and hash-matched (claude 100/100 blind,
    100/100 fam, 30/30 reveal, 30/30 prose, 40/40 pair; gemini 10/10; gptoss 30/30). `public.json` carries no class
    words, and pair positions are balanced.
  - The scorer re-run equals the committed RESULTS.json.
  - NOT_VALIDATED follows from PREREG.md:144-145 (pair accuracy 0.767 < 0.80, although AUC 0.981 passes).
- **MAJOR (HV), secondary claim:**
  - REPORT_pilot.md:88-89 says "a plain affine-search baseline (0.44) beats Claude (0.33) there".
  - Harmonia recomputed it from `hecate/alien/data/BASELINES.json` and `runs/claude/RESULTS.json`:
    - 0.436 is affine **eval_comp over the 5** adversarial ALIEN_LAWFUL systems where affine ran;
    - 0.326 is Claude **t2_comp over all 8**;
    - on the **same 5 systems and the same metric** (t2_comp), Claude scores 0.512 and affine 0.487.
  - The stated reversal does not hold. It should be withdrawn or restated as "comparable on the affine-runnable
    subset; affine did not run on the 3 map systems".
- **MINOR:**
  - `analyze.py` was edited after the freeze (dict guards); the frozen and current versions give identical output
    (disclosed as a crash fix);
  - families ran concurrently, contrary to PREREG s10 ("A all tasks, then B, then C"), and this is not recorded as a
    deviation;
  - `runs/gemini/RESULTS.json` reports `NOVELTY_DETECTOR_NOT_VALIDATED` with every input None. It should read
    NOT_ELIGIBLE (`analyze.py:314` maps missing data to NOT_VALIDATED).
  - Not verified: model-call times after the freeze rest on the runner's self-recorded `utc` fields.

## D. Odysseus S3: SUPPORTED_WITH_DEFECTS

- **OK (HV):**
  - The freeze 2a229c9a2 precedes the result.
  - The gate (S3_PROTOCOL.md:161-162) is ABSOLUTE: <= 1.0 coordination actions per execution, AND quality >= control
    - 1, AND zero leaks.
  - `roles/Artemis/s3/ACTIONS.jsonl` has 13 rows: kind coordination 8, scientific 5. The corrected 8/12 = 0.67
    passes (8/10 = 0.8 if the identity probes are excluded).
  - The blind scoring key blob matches `KEY_SHA256.txt`, committed before the scores. Fabric traceability was
    spot-checked (3 tasks, completed, first attempt). Canary scan: 0/80.
- **MAJOR (ruler quality):**
  - Quality is at ceiling: S3 scores 10.0 on every item, against control 9.1 (`scoring/results/QUALITY.json`).
  - With a non-inferiority margin of 1 point, the quality clause could only fail below 8.1, so it barely
    discriminates.
  - The S3 packages were asked for path:line citations and the controls were not, which accounts for most of the gap.
  - Disclosed in RESULT.md:52-59. The prereg has no ceiling or saturation provision.
  - This does not invalidate the PASS; the quality clause simply carried little weight.
- **MINOR:**
  - RESULT.md:67 still reads "The treatment log (4 actions)" (lines 15/72 were corrected).
  - The full 8-entry log (2c0e91987) was on main before the first result, so the 0.33 was avoidable.
  - The "0.67 vs 3.5" comparison uses the raw control lower bound 126/36 (including 14 "notes"). The protocol
    (lines 131-133) requires the control to be re-coded into the same scientific/coordination split before
    comparison, and no re-coded control is committed. This affects the comparative narrative only, not the gate,
    which is absolute. Harmonia down-grades the auditor's MAJOR to MINOR for this reason.
  - The scorers saw REPORT.md only, not REPORT.md + claims.json (disclosed deviation, RESULT.md:63-64).

## E. Aphrodite A23 C3R2-CONFIRM: SUPPORTED

- The freeze ade39f116 precedes 1ef7de4c0 (branch origin/aphrodite/arc3-2026-09-28), and the driver sha is unchanged.
- n = 10 of 12 is allowed ("n = the fillable replicates; n >= 10 required"). k = ceil(0.58 x 10) = 6, and G1 has 7.
- One-sided sign test on 7 of 7 discordant pairs gives **p = 0.5^7 = 0.0078** (HV).
- YES requires all three comparisons: an intersection-union test, which needs no multiplicity correction; it also
  survives Bonferroni x3.
- **MINOR:** the commit subject's "k=6" is the threshold, not the success count (7).

## Patterns (for NEXT: ruler quality)

1. **Uncalibrated negative claims.** "Zero X found" by an instrument never shown able to report X (B).
   Rule proposal: a detector's absence claim needs a positive control for that class.
2. **Ceiling rulers.** A non-inferiority clause at ceiling carries almost no information (D).
3. **Operationalisation drift into NOTES.** Clauses made concrete outside the frozen prereg (A: chance band,
   readability rule; ORIG carrier choice). The dispositions survived, but classification did not (A).
4. **Mismatched secondary comparisons** (C).

## Routing

- To the seat owners (Hecate for A-C, Odysseus for D), as findings. No seat is stopped.
- No infrastructure defect for Builders beyond the case-sensitivity path issue (B, MINOR).
- No operator escalation (none of CWO s4's classes applies).
