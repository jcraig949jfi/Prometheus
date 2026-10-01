# Hecate ruling request -- contested items C1-C8 (Wave 2, 2026-10-01)

Each item would change the OUTCOME of a frozen decision rule if applied,
so under CWO-C s4 it is escalation class: Hecate has NOT applied any of
them. Full evidence: roles/Hecate/harvest_w2/CORRECTIONS_2026-10-01.md.
Owner: Aporia (scheduler) to route; operator to rule. Default if no
ruling: everything stays as recorded, with the annotation visible.

Format: item -- recorded -> proposed -- basis -- consequence if applied.

C1 ae38 W5 -- NULL (program PARK) -> INCONCLUSIVE, not a valid NULL
   (program SPECULATIVE). Basis: the frozen spec's own INCONCLUSIVE band
   (0.15-0.40) "is not a falsification"; the round PREREG had no such
   class. Consequence: ae38 eligible for another world (none may start
   under CWO-C).
C2 321a Pass-4 r1 -- PROBING -> PARK, or PROBING annotated "degenerate
   ALT". Basis: the ALT is fixed by counting (alt_pass = Kc > Km), correct
   under round-1 rules, NOT_ELIGIBLE under round-2 rules. Consequence:
   last PROBING program goes to PARK (16/16 PARK or SPECULATIVE).
C3 79e9 W4 -- NULL stays; flagged INSTRUMENT-WEAK (no ruling needed
   unless the operator wants it reclassified).
C4 ae38 W4 -- SPEC_UNATTAINABLE stays; flagged (aggregation reading).
C5 Alien H3 -- INDETERMINATE -> SUPPORTED. Basis: float compare
   0.2-0.1 = 0.0999... < 0.10; the PREREG text in exact arithmetic is
   1/10 >= 1/10. Fragile: one alien (SYS-19722). Consequence: "active
   experimentation closes the gap" becomes a supported (n=1) result.
C6 Alien detector -- NOT_VALIDATED -> report under both consistent
   alien sets (standard: VALIDATED, pairs 19/22; all: NOT_VALIDATED, AUC
   0.940). Basis: the code mixes alien sets across its two legs, as the
   PREREG text literally does. Consequence: the "novelty detector not
   validated" headline becomes reading-dependent.
C7 Alien H2 / H4 -- H2 NOT_SUPPORTED rests on a zero-variance bootstrap
   (exact bound says INDETERMINATE); H4 used a binary rule not the s6
   rule (s6 gives NOT_SUPPORTED on a degenerate CI). Proposed: report
   both, change neither without ruling.
C8 Meta v1 M1 vs P -- INDETERMINATE (5/8) -> NO_ADDED_VALUE_vs_P (4/8)
   if the refused detector call u4-P-m8 stays in the denominator (literal
   "FAMILIAR / items"). Overall M1 unchanged (INDETERMINATE).

Ask: one line per item -- APPLY / ANNOTATE-ONLY / OTHER. Hecate's
recommendation: APPLY C5 (the frozen text governs; report as n=1),
ANNOTATE-ONLY for C2, C3, C4, C6, C7 (report both readings), APPLY C1
and C8 (frozen spec text / literal denominator govern). These
recommendations come from the instance that wrote the original rules,
so they need independent review.
