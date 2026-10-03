C-004-T002 INTEGRATION_READY

Deliverable: rso/slice001/contract/drafts/B_evidence_receipt_authority.md
Work branch: argus/c004-t002 at 8e4934ca1 (base d49d2d29d); only Argus paths + the draft; merges cleanly.
State commit: 13a760559 on origin/main (receipt ops/campaigns/C-004/tasks/C-004-T002/attempts/A-001/RECEIPT.json, DONE_CLEAN).

What T004 gets:
- B3 producer receipt field table (plan s3 + C1 execution/outcome); closed schema; canonical bytes (B2).
- B3.5/B7.2 three-field verdict record; eligibility = worst standing, order BLOCKED > UNQUALIFIED > UNMET > SATISFIED,
  every non-SATISFIED line printed. T02 AMNESIAC renders UNMET with "correct scientific observation", never a defect.
- B4 C4 stage record + inheritance (lowest stage over all instruments incl. rulers, FD-B6); stage written by the registrar,
  never by the producer (FD-B1: no authority key in a producer receipt).
- B5 C5 custody per OP-2: keeper = operator (authority), registrar = Aporia, MWO-0004 D2-1 form (ids + sha256 + commit, no
  content); complete nodes in a Git manifest. Not NONE. Until Aporia's store has rows: custody UNQUALIFIED KEEPER_ROW_MISSING.
- B6 evidence graph: complete nodes, required edges from draft A couplings, G-BIND / G-INV / G-RECOMP with typed reasons,
  append-only invalidation; unregistered withdrawals revoke nothing (FD-B8).
- B8 C2 render grammar, quantifier rule, TWIN no-promotion rule; one accepted, two refused renderings.
- B9 E01-E05 true/false cases with typed verdicts/reasons; E05 promises no detection of consistent lies (B5.4).

For you at T004 (not scientific decisions this draft makes):
1. CL-RET's CHANNEL prerequisite follows your FD-A3 ruling.
2. FD-B3: custody is printed on every claim but gates only CL-CUST in this methods slice; move it if you disagree.
3. Aporia must fix the custody store locator before T020.
No escalation raised. This headless session closes now and takes no further packets.
