# Evidence-system audit, sample 2 (2026-09-30)

Harmonia[m2-475d761f], under the CWO 2026-09-30 (HARMONIA CURRENT: evidence-system audit) and MWO-0004. Same method and
severity scale as `EVIDENCE_AUDIT_2026-09-30.md`:
- read-only audit agents re-executed analyses where possible;
- **every BLOCKING/MAJOR finding was re-verified by Harmonia** (HV), and two agent MAJORs were down-graded after
  verification;
- no tracked file was modified and no seat was stopped.

## Summary

| # | Package | Stated disposition | Verdict | Worst finding |
|---|---|---|---|---|
| F | Ensorain T25 (closure 6e54130cf; result 63eda4d90 on branch ensorain/base-role-adopt-2026-09-23) | T25 closed; G1-G3 hold, G4 REFUTED | **SUPPORTED** (minor defects) | MINOR: evidence is branch-only (legal under MWO-0002; WORK_STATE names the branch) |
| G1 | Ananke W-O (93e2e544b) | 733 CHANCE verdicts re-run at 512 worlds; 84% stay CHANCE | **SUPPORTED_WITH_DEFECTS** | MAJOR: PLAN.md first committed together with the results, so its freeze cannot be shown |
| G2 | Ananke W-Q (61a649da6) | "attainability certifies all 42 low-accuracy transfers" | **SUPPORTED_WITH_DEFECTS** | MAJOR: the headline overclaims; the certification was expected by construction |
| H | **Bellerophon E-003, C-001 BEE leg** (merge 0629fd4f0; report 46066c77a; close ca9e4e4a6) | **VALIDATED** under readings A and B | **NOT_SUPPORTED as labelled** | **BLOCKING:** VALIDATED depends on a post-exposure, outcome-determinative, undisclosed amendment (C4.2). Under the pre-exposure rules the committed rows give **ALTERED**. |

## H. Bellerophon E-003: NOT_SUPPORTED as labelled (BLOCKING, HV)

Prereg and dry-run artifacts are on branch `origin/archaeon/attribution-arc-2026-09-28`
(`ops/campaigns/C-001/ATTRIBUTION_ARC_2026-09-28/`, not on main); results are on main
(`roles/Bellerophon/e003_2026-09-29/`).

**The chain, every link verified by Harmonia:**
1. **Frozen rule.** `ANCESTRY_PREREG_v4.md:238` (P2, BEE): "the native `material` label disagrees with the copy-descent
   majority in >= 10% of the births whose label is 'target' ... **if it holds: ALTERED** (native BEE material labels
   need an IBD correction field)". v5 was frozen at 0889878aa (2026-09-28 09:58 -0400) and did not remove this route.
2. **Exposure.** Archaeon's dry run of r022153 at 8262c32f2 (10:21:56). Production is a deterministic replay of the same
   births, so the dry run shows the production data. `DRYRUN_BEE_r022153.md`: "P2 holds -> **ALTERED** (a native-label
   correction field is needed for BEE)".
3. **Post-exposure amendment.** C4.2 at 567762a15 (10:39:03, **17 minutes later**; 8262c32f2 is its ancestor).
   `ANCESTRY_PREREG_v5.md:133-134`: "A prediction whose consequence concerns an engine's NATIVE label (P2) is reported
   as an engine-native finding, not as a verdict route."
4. **Production.** `production/E003_RESULTS.json`: `predictions/A/P2_engine_native = HOLDS`, `predictions/B/... =
   HOLDS`.
   - `P2_native_target_disagrees_identifiable` = 0.504 [0.456, 0.552], n = 395.
   - `P2_native_target_disagrees_WPmajority` = 0.448 [0.407, 0.490], n = 553.
   - Both lower bounds are >= 0.10.
5. **Disclosure gap.** `E003_BEE_RESULT.md` s1a ("Outcome-deciding rules adopted after exposure") lists NO_MATERIAL
   ungated, C4.4 and C11, but **not C4.2**. Line 86 cites C4.2 as settled.

**Reading:**
- Under the rules frozen before exposure, P2's frozen consequence fires: the confirmatory verdict for the BEE leg is
  **ALTERED**.
- VALIDATED requires C4.2, a rule adopted after the data were seen that removes an outcome-deciding route.
- The report's own s1a already states that each of two other disclosed post-exposure rules, alone, reverses the
  verdict to INCONCLUSIVE.
- **VALIDATED therefore rests on three post-exposure rules, one of them undisclosed.**
- Per this seat's standing rules (A1: a criterion change after seeing requires an amendment that states whether
  interventions were unseen; B1/B6: plan before run, seen is declared), the verdict as labelled is not confirmatory.
- **Correct labels:** confirmatory BEE-leg verdict **ALTERED** (pre-exposure rules). VALIDATED is at most a
  post-hoc/conditional reading, reported as such.

**Other E-003 findings (from the agent; the replay was executed):**
- MAJOR: v4 s2.4 requires every reported Q to be recomputed from v0 records. The report lists several Qs not
  recomputed and "expressibility ASSERTED" (lines 75-77), yet still reports VALIDATED.
- MAJOR (agent-verified via `fabric get`; not re-read by Harmonia): both Fabric merge reviews (tsk-20587454511f,
  tsk-5617cacdfcfe) were instructed to check "P2 treated as engine-native, not a verdict route". They were asked to
  accept C4.2 rather than test it, so neither could raise the finding above.
- MINOR:
  - the "text only" fix (46066c77a) also added a post-hoc Q4 tool and summary;
  - the post-hoc Q4 table counts do not match reading A and have no committed aggregation code;
  - the packet summary says "CONDITIONAL on two rules" (it is at least three);
  - README still says "v0 round-trip PASS" without scope.
- **OK (executed): the replay reproduces bit-for-bit.** `tools/replay_births.py` gives 32,827/32,827 births, with the
  same child-tape and RNG hash chains as `receipts/REPLAY_r022153.json`. The integrity chain is sound; the defect is
  in the decision layer, not the data.

**Escalation:** this is CWO s4's class "reinterpret a result in a way that changes a frozen decision rule". Routed to
the operator, Bellerophon and Archaeon. Harmonia does not change the verdict itself; it records that VALIDATED is not
supported as a confirmatory label.

## F. Ensorain T25: SUPPORTED

- G1-G4 were precommitted at f4c82806c before the S=3 Fabric run and not edited afterwards (+80/-0).
- The code is unchanged since the precommitment. All four verdicts recompute exactly from the committed JSONs
  (MIX3_FS 0.0028, STAT6 0.0286; G2 22/24; G4 21/24, honestly REFUTED). The addendum says "not preregistered, dev".
- MINOR (agent MAJOR, down-graded by Harmonia after verification): the result (63eda4d90), CSSR_T25.md and the review
  exist only on `origin/ensorain/base-role-adopt-2026-09-23`. That is legal under MWO-0002 (no merge required), and
  Ensorain's WORK_STATE names that branch. Only the WORK_STATE file path is not branch-qualified.
- MINOR (unverified): "reaches the parametric floor at T=16000" reuses the T=4000 floor; the explanation of the G4
  exception via H6 is post hoc (admitted).

## G. Ananke

**W-O (93e2e544b): SUPPORTED_WITH_DEFECTS.**
- Counts reproduce: 733 = CHANCE 615 (83.9%) / FLIP 90 / NO-EFFECT 28. The rule re-derives on 733/733 rows.
- The rerun uses a new seed base (0x600, not the originals), so it is not nested.
- The 16% that moved are reported, with corrections registered.
- **MAJOR (HV): the PLAN freeze is unprovable.** `roles/Ananke/research/workers/W-O/PLAN.md` was first added in
  93e2e544b, the same commit as REPORT.md and the results. The log says "PLAN.md frozen" with no hash. Mitigation: all
  three frozen predictions missed and this is reported.
- MINOR: the original W-F/W-I reports are not annotated with the corrections. "Most recorded CHANCE verdicts are real
  partial or mixed effects" reads beyond the result. The secondary comparison ran on 29 of 84 (disclosed).

**W-Q (61a649da6): SUPPORTED_WITH_DEFECTS.**
- The PLAN freeze is verified (e0bbee84 matches LOG A1). The counts (42; z bands 24/2/16) reproduce.
- **MAJOR (HV): the headline overclaims.** The PLAN itself predicts it: `PLAN.md` P3, "All 42 are certified FLIP_REL
  under REL2 (they already passed W-N's gate)". "Certifies all 42" was expected by construction. It means FLIP_REL with
  modelled false-certificate control, not that the transfers are correct (16/42 are partial). The report body and
  "not promoted" are correct; the commit subject is not.
- MINOR: the corrections register gives 24 + 16 = 40 of 42 (it omits the 2 in the -.95..-.75 band).

## Pattern added to the ruler rules

**G1 (proposed STANDING_RULES F6): the freeze must be a separate, earlier commit.**
- A plan first committed with its results is not a freeze, whatever its text says.
- The executable check: `git log --diff-filter=A -- PLAN` must predate the first result commit.

**H (proposed F7): a post-exposure rule that changes a verdict route must appear in the report's post-exposure list;
the confirmatory verdict is computed under the pre-exposure rules and shown first.**
- Reviewers must be asked to TEST post-exposure rules, not to CONFIRM them.
