# Chiron backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-09-21. Still provisional and below the 20-item schema
floor ON PURPOSE. The CDE design thesis names the seat's subject but
explicitly withholds authorization to build ("Do not start on it"), so
items that would size an implementation are not written yet: a backlog
of work nobody has approved is a plan pretending to be a queue.
CHIRON-01 closes this file's below-floor status once an executable
charter lands. Lanes: ENGINE, EVIDENCE, TOOLS, LIT.

CHIRON-01 | Receive an executable charter and rewrite RESPONSIBILITIES.md, STATUS.md and this backlog to the schema floor (>=20 items) | ENGINE | alpha | S | operator decision NEW: lift the 2026-09-21 build hold and issue an executable CDE charter | roles/Chiron/RESPONSIBILITIES.md s0 no longer reads PENDING and this file carries >=20 items
CHIRON-02 | Resolve the comms boot blocker on this host (install psycopg2, or record the operator's ruling that this seat boots from a fleet host instead) | TOOLS | alpha | S | operator decision NEW: where Chiron boots | roles/Chiron/STATUS.md carrying either a successful `comms boot Chiron` receipt or the ruling recorded verbatim
CHIRON-03 | Answer the review's s14 open questions, above all whether the CDE artifact writer is an LLM | EVIDENCE | alpha | S | operator decision NEW: CDE writer identity, host engine, lineage count, Crius sandbox reuse | the four answers recorded verbatim under roles/Chiron/prompts/ and folded into RESPONSIBILITIES.md s1
CHIRON-04 | Read Crius's four campaign packets (C0, C1, C1b, C2) and their receipts, and write the transferable-lessons note naming which CDE design choices each one constrains | LIT | alpha | S | none | roles/Chiron/CRIUS_LESSONS_FOR_CDE_2026-xx-xx.md citing receipt paths under crius/runs/
CHIRON-05 | Report the overloaded organism.development field to Atlas (true for both Voyager-style competence accumulation and NCA morphogenesis) with the cross-tab that exposed it | TOOLS | alpha | S | none | a message to Atlas recorded under roles/Chiron/prompts/, and Atlas's disposition recorded here
CHIRON-06 | Source-verified raid on Voyager (MIT, public): read the curriculum, critic and skill-retrieval components and record which are separable from GPT-4 and which are not | LIT | alpha | M | none | roles/Chiron/RAID_VOYAGER_2026-xx-xx.md with file-level citations, replacing model-knowledge claims
CHIRON-07 | Freeze an operational definition of "reachable" (task family, budget, success threshold) as a hashed pre-registration before any CDE code exists | ENGINE | alpha | M | CHIRON-01 | a DESIGN document with a config hash, committed before any run
