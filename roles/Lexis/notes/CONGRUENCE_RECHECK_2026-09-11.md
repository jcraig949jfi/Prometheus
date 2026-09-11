# Congruence audit re-run at HEAD, 2026-09-11 (LEX-06)

Why: the exact ceiling (100/120) is conditional on the field projection D being
a congruence (ROLE.md s4a). apollo/ has 16 commits since the 08-25 measurement.
A precondition measured once is a label; this re-measures it.

Command (from the lexis-base-role worktree, HEAD 8600edd68 + this note):

    PYTHONHASHSEED=0 python roles/Lexis/instruments/congruence_audit.py \
        --out roles/Lexis/notes/congruence_audit_result_2026-09-11.json

Result: all five verdicts PASS (C no aliasing; A no cross-boundary aliasing;
D no reachable module state; F history-independent, 0 mismatches; G no
cross-task contamination). Rows: congruence_audit_result_2026-09-11.json.

Two facts beside the verdict:

1. The operator module did not change. apollo/src/ (blackboard_ops_v2.py and
   siblings) has 0 commits since 2026-08-25; last change a3e9bbee4, 2026-08-12.
   The 16 apollo/ commits are cycles/, pivot/, serendipity/ and scripts/ (the
   Gen-2 and S1 work). So the precondition holds by construction as well as by
   measurement. Both are recorded because "the file did not change" is a
   repository claim and the audit is a behavioural one.
2. Field-by-field diff against the committed 08-25 rows
   (congruence_audit_result.json): 25 keys, 1 differs: aliasing.records
   5026 -> 5029. Today's 5,029 matches the number quoted in ROLE.md s4a and
   STEP1_CEILING_CLOSED_2026-08-25.md ("5,029 states total"); the committed
   08-25 JSON is therefore from a draw three records smaller than the one the
   documents quote. The 08-25 run was not seed-pinned (handoff s8 item 3: the
   synth subset is redrawn per PYTHONHASHSEED); today's is. No verdict depends
   on the count. The 08-25 JSON is left as it is; this note is the annotation.

Not done: the fresh-process comparison (LEX-14). History independence is still
sampled (189 pairs), now on two dates.
