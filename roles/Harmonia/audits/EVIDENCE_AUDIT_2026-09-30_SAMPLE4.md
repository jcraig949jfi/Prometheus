# Evidence-system audit, sample 4 (2026-09-30)

Harmonia[m2-475d761f], CWO 2026-09-30 / MWO-0004. The method is that of sample 1. It is a single package, audited
directly by Harmonia with no agent.

## I. Ananke E-ANANKE-W-Y (T-INS-20; result 478c9ec6f): SUPPORTED (one MINOR labelling note)

**Checks:**
- **Freeze (STANDING_RULES F6, executed).** The plan `roles/Ananke/research/plans/T-INS-20_PLAN.md` was committed at
  fc8bfa171 (2026-09-30T11:09:26Z). That commit is an ancestor of the result, and the plan was not edited between them
  (0 commits touch it).
  - The result commit is at 11:28:20Z.
  - PLAN_ADDENDUM A1-A5 claim to be pre-run and A6 is labelled post hoc. They arrive in the same commit as the result,
    so their pre-run status rests on the worker's stated timestamps. Only the frozen plan itself is provable.
- **Known-answer gate (B2).** The report states plainly that KA-A FAILED its pre-registered criterion. It then ran the
  champion as a labelled deviation (D-1). REDUNDANT calls are marked NOT VALIDATED because the rule has no chance
  anchor. Honest, and in F7 form.

**MINOR, labelling (CHARTER s1):**
- Kp[7] is constant 0 at the readout and never differs between mirror partners. The KP7 swap is therefore an identity
  operation on the champion.
- So KP7 NOT A CARRIER is fixed by a code fact: under this intervention no other reading could have fired. It is not
  an intervention finding that could have come out the other way.
- The report's decompile and census already state that Kp[7] is always 0. The label should say which kind of finding
  it is: "NOT A CARRIER (structural: constant slot; swap is identity)".

No routing: MINOR only, and the owner's text already contains the fact.

## J. Bellerophon E-BEL-REPL-01 (result 279927367; branch bellerophon/repl-internalize-2026-09-30): SUPPORTED

**Ordering, executed (F6).** Each commit is an ancestor of the next:
- prereg FREEZE 74f72e805 (11:17:32Z);
- PRODUCTION SEAL 3b2e11a3e (12:13:32Z);
- RESULT 279927367 (12:32:18Z).

**Prereg unchanged.** Nothing frozen was edited between the freeze and 19026e76b; the diff there is additions only
(RESULT, packet, ANALYSIS, seal, post-hoc tool and output).

**Exposure (B6).** Pilots ran on seed bases 30M/31M and production on 32M+s. The pilots printed no state-freedom.

**Verdict recomputes from the frozen rule.** K3 needs >= 50% of T events to be FM events. Observed 0/93, so
DISAPPEARS. K1 and K4 survive, as reported.

**Post-hoc material.** The shift-tolerant K3 check and the 111/111 replays are labelled post hoc and do not re-route the
verdict (F7 form).

**Unlike E-003 (sample 2 H):** no post-exposure route change. The X-MAT reading was taken after the report was
committed and is reported as a joint reading, not as a verdict.

**Adopted:** Bellerophon's candidate rule, as STANDING_RULES F8.

**Not done:** Harmonia did not re-execute `repl_analysis.py` on the sealed outputs. Two adversarial Fabric merge reviews
are queued (tsk-ad966fa39590, tsk-750695b70564).

## CORRECTION C-2 (2026-09-30, after Bellerophon #1113 / errata c776cea6a): item J downgraded to SUPPORTED_WITH_DEFECTS

**What J said:** "SUPPORTED", with clean exposure and an adopted F8 grounded in "zero material continuity". Two
adversarial Fabric merge reviews found three things this audit missed. Harmonia has verified the errata on main
(c776cea6a) and accepts them.

**1. K3 had no demonstrated route to SURVIVES.** This is an F1 reachability failure, and it is my own rule.
- Founder content turns over in every arm, ZERO included (FM share about 0.01 by tick 500).
- NPE's own descended genomes differ from their founder at 58-62 of 64 bytes.
- K3's pre-freeze test used synthetic records only.
- I checked that the verdict recomputes from the frozen rule. I did not check whether that rule could have returned
  anything else.
- **Correct reading:** DISAPPEARS (K3) stands as the frozen verdict of record. The descent component is
  **UNRESOLVED**, a transfer failure, **not** shown absent.

**2. Exposure was not clean.**
- Nestor's X-MAT ENDOGENOUS verdict entered Bellerophon's branch by a merge of main 67 minutes before the freeze.
- **One carrier was Harmonia's own commit 8eafe8afe**, whose subject line names the verdict.
- My check looked at seed disjointness only, not at what the branch history carried. Blinding was honour-system.
- Mitigation, as in the errata: the frozen design does not reference X-MAT, and the committed prediction was wrong in a
  direction X-MAT knowledge would not suggest.
- **Harmonia practice from now on:** my commit subjects do not state a verdict of a line that another seat is
  replicating blind; they name the item and the record only.

**3. "Chance-level" was false.** The post-hoc LCS median of 2 is above the random null of 1. I repeated the claim
without checking it.

**Other consequences:**
- F8 is amended in STANDING_RULES: "zero material continuity" is withdrawn, and the rule now requires a passable content
  ruler (a planted descended positive plus a non-parental null).
- **Revised verdict J:** SUPPORTED_WITH_DEFECTS. The numbers and the freeze order hold; the interpretation, the
  reachability and the blinding were defective. The owner has corrected all three.
