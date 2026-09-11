# Rhadamanthus backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-09-11 (establishment day; charter PENDING).

This list is BELOW the schema floor of 20 items on purpose: the seat has
no charter, so every item that would depend on a lane is unwritable
without inventing the lane. The items below are the pre-charter work
that is executable now and the decisions the operator's charter is
expected to settle. The list is regenerated to the full schema on the
charter commit.

RHAD-01 | Commit the seat establishment (roles/Rhadamanthus/ plus the two INHERITANCE rows), push, verify ancestry, boot in comms | TOOLS | program | S | none | roles/Rhadamanthus/* on origin/main; comms.agents row for Rhadamanthus; journal/2026-09-11.md
RHAD-02 | Reply to Talos #50 (TALOS-10 consumer contract) with NONE-for-now and the reason, as a committed body | EVIDENCE | program | S | none | prompts/2026-09-11_establishment/TALOS10_reply_NONE.md + comms post id in the journal
RHAD-03 | Adopt the charter verbatim when issued: commit under prompts/<date>_charter/ with MANIFEST, rewrite RESPONSIBILITIES.md as the seat's reading, regenerate this backlog to the schema floor | program | program | S | operator (charter not yet issued) | prompts/<date>_charter/CHARTER_verbatim.md + MANIFEST.md; RESPONSIBILITIES.md currency line updated
RHAD-04 | Measure the Necropolis branch map: for each of the five necropolis/* branches, files added or changed relative to efd26dbb8 and to each other; whether frankenstein is a superset; which branches exist on the remote | EVIDENCE | program | S | none | ledgers/NECROPOLIS_BRANCH_MAP_2026-09-11.md with the git commands
RHAD-05 | Run engine/necropolis/validate.py at each of the five branch heads in a read-only worktree and record pass/fail and the dossier path-resolution counts per branch | EVIDENCE | program | S | none | ledgers/VALIDATE_BY_BRANCH_2026-09-11.json with stdout captured per branch
RHAD-06 | Report the QUEUE label/property gap (Coeus, Argos, Hephaestus READY with dossiers present) to the Keeper's inbox; report only, the Keeper owns QUEUE.jsonl | EVIDENCE | program | S | none (Mnemosyne never booted; message queues for its next sync) | roles/Mnemosyne/INBOX_RHADAMANTHUS_QUEUE_LABEL_GAP_2026-09-11.md + comms post id
RHAD-07 | Cross-check ROSTER.jsonl against comms.agents: which of the 48 graves are also seats that booted today, and what LAW N15 obliges for each | EVIDENCE | program | S | none | ledgers/ROSTER_VS_COMMS_2026-09-11.md
RHAD-08 | Count what the SEAMS.md reuse targets actually hold on origin/main (engine/ledger/AGENT_AUTOPSIES.jsonl rows, AUTOPSY_TAXONOMY.md, engine/queues/CONSUMPTION.jsonl rows) and whether each exists at b66765e69 | EVIDENCE | program | S | none | ledgers/SEAMS_INVENTORY_2026-09-11.md
RHAD-09 | Execute one evidence script from dossiers/coeus_evidence/ on its branch and compare its output to the number the dossier cites; record match or mismatch as a self-calibration of this seat's reading, not an adjudication | EVIDENCE | program | M | none | calibration/LEDGER.md row with the command, the cited number, the observed number
RHAD-10 | Read roles/Kairos/necropolis_evidence/README.md and record what it holds and whether anything consumes it | EVIDENCE | program | S | none | ledgers/KAIROS_NECROPOLIS_EVIDENCE_2026-09-11.md
RHAD-11 | Copy the review-packet and evidence-wiki skills beside the seat (base rule 6) | TOOLS | program | S | none | roles/Rhadamanthus/skills/review-packet/, roles/Rhadamanthus/skills/evidence-wiki/
RHAD-12 | Write the seat's D-23 compliance note (worktree, base SHA, guard output, what was never written in the canonical checkout) | TOOLS | program | S | none | D23_COMPLIANCE_2026-09-11.md
RHAD-13 | Post a delegation to Mnemosyne asking for the current Necropolis handoff packet and which branch the Keeper regards as head-of-line | EVIDENCE | program | S | none (queues until Mnemosyne syncs) | prompts/2026-09-11_establishment/DELEGATION_MNEMOSYNE_handoff.md + post id
RHAD-14 | Register any standing loop the charter creates in roles/base-role/MONITORS.md before it first runs | TOOLS | program | S | operator (charter) | MONITORS.md row with all ten columns
RHAD-15 | Decide whether engine/necropolis/ integrates to main, from which branch, and who owns the fast-forward | XL | program | XL | operator decision NEW: "integrate engine/necropolis/ to main from necropolis/frankenstein after validate.py passes on the merged tree, Keeper to push" (recommendation; RHAD-04/05 supply the evidence) | archaeon/docs/expansion/DECISIONS.md row
RHAD-16 | Decide this seat's lane inside the Necropolis cycle (Keeper / Necromancer / Cleric / Frankenstein / a new role) | XL | program | XL | operator decision (the charter) | the charter file under prompts/
