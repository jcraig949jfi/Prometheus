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
