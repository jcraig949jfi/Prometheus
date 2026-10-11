# C-012 -- Native execution fabric (OP-NF2)

Thread TH-MOON-M4 (commodity fabric), Epic EP-MOONSHOT. Owner and coordinator: Themis. Opened 2026-10-10
under OP-NF2 (roles/Themis/prompts/2026-10-10_op_nf2/), which supersedes C-008's Git-CAS runtime plan.

Why: Moonshot's epochs will run on cheap, flaky hardware for days. OP-NF2 moves their coordination onto the
program's existing PostgreSQL: Fabric (Odysseus) claims and executes; Moonshot (Themis) owns identity, lineage,
publication, classification, validation and contests; Pan owns the analytical lake. C-008's semantics -- identity
independent of transport, PUBLISHED is not VALIDATED, disagreements fail closed, every attempt charged -- carry over;
its git transport does not.

C-008 stays as historical engineering evidence: T001/T002/T005 closed with their results; T003 (LAN baseline) and
T004 (GitHub arm) were never executed and are SUPERSEDED with no verdict.
