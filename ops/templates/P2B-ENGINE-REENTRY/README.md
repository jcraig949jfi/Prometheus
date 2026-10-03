# Template P2B-ENGINE-REENTRY -- an engine's first Phase 2-B campaign

Instantiate with:

    python -m workgraph new-campaign P2B-ENGINE-REENTRY --owner <Seat> --subject "<engine>" --by <Seat[tag]>

It creates ops/campaigns/<next C-id>/ (thread TH-P2B-ENGINE-HARDENING, epic EP-PHASE2B) with the owner as
coordinator and two PROPOSED tasks, A and B. The owner tailors them with its real sources, makes them READY,
and commits/pushes the directory. Everything after triage is created by the owner from what triage found:
this template deliberately knows nothing about any engine's failure history.

Stages (directive s8):
- A. Feedback ingestion -- read the forensic findings and failure records that apply to this engine; decide
  which actually fit the implementation; do not accept accusations that do not.
- B. Defect triage -- classify each finding: CONFIRMED_DEFECT, ALREADY_REPAIRED, NOT_APPLICABLE,
  NEEDS_DISCRIMINATOR, SCIENTIFIC_LIMITATION, OPEN.
- C. Repair -- fix implementation/instrumentation defects that materially affected interpretation; add
  regression fixtures (one packet per repair, RED = the fixture that fails before the fix).
- D. Replay -- re-run the most important historical experiments those defects affected; preserve the original
  receipts and compare old and new outcomes.
- E. Residual science -- experiments from the backlog with real information value left; cheap discriminating
  probes before large campaigns.
- F. Continued exploration -- if the engine is still useful after hardening, propose new bounded campaigns.
A campaign may close with NO_JUSTIFIED_FURTHER_WORK.
