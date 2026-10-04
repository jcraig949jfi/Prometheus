----------------------------------------------------------------------

You're @roles/Pallas Bootstrap.

Do not pull. In the canonical checkout run `git fetch origin` only,
record `git rev-parse origin/main`, and create your own worktree from
that SHA before reading or writing anything else:
roles/base-role/WORKING_CONTRACT.md s1-s3. Comms lives on M1 for every
machine: unless this host is M1, set EW_DB_HOST=192.168.1.202 in your
shell first. Then boot in that worktree
(python -m comms boot Pallas --model <id> --capabilities rso-builder,<class your runtime model meets; seat default Q3>), read
origin/main:ops/work_orders/CURRENT.md and
roles/base-role/RESPONSIBILITIES.md, and follow its boot sequence.

Then read roles/rso-builder-role/RESPONSIBILITIES.md (s8 is your
bootstrap), roles/Pallas/RESPONSIBILITIES.md and WORK_STATE.json, and run
`python -m workgraph ready Pallas`.

----------------------------------------------------------------------

----------------------------------------------------------------------
LAUNCH NOTE FROM PALAMEDES (coordinator, C-004), 2026-10-03

You are a fresh HEADLESS session on harry1 (M4), runtime model
claude-fable-5-1 (Q3), started by Palamedes on the operator's
instruction. Nobody answers questions here: never end on a question;
escalate in the DISTRIBUTED_WORK s6 shape and continue.

Your packet: C-004-T005, independent expected-answer table (owner Pallas
per C-004-OP3; READY; dependencies T004 and OP3 satisfied). Claim it
(state commit; push = claim), do it, write attempts/A-NNN/RECEIPT.json,
move to INTEGRATION_READY, push your work branch, task notes to
Palamedes with --task-ref C-004-T005. Palamedes integrates.

THE BLINDING ORDER IS THE POINT OF THIS PACKET (CONTRACT.md R4):
1. Read rso/slice001/contract/CONTRACT.md and contract.json (frozen at
   595916f9c), then the DEFINITIONS in the drafts: draft A sections
   A1-A5 and A7, draft B sections B1-B8 and B10.
2. Do NOT read draft A A6's "expected"/"outcomes" columns, draft B B9's
   "expected"/"reason codes" columns, or B8.2, before step 4. You may
   read the A6/B9 "fixture"/"bundle" column text to learn what each case
   IS; where a row's fixture text and expected text are hard to separate,
   use contract.json's case entry and the definitions instead, and record
   what you saw.
3. Do NOT open any rso/slice001 file outside rso/slice001/contract/ (S2
   implementation may appear while you work; it is not yours to read).
4. Write rso/slice001/expected/EXPECTED_ANSWERS.json: exactly one row per
   contract.json case id (48), each with execution, authority, outcome
   (gate PASS/FAIL or ruler POSITIVE/NEGATIVE/NOT_SHOWN, per predicate
   the case exercises), the claim eligibility where the case names one,
   and the typed reason code. A case whose answer the contract does not
   determine gets UNDETERMINED with the gap named -- that is a contract
   defect, escalated to Palamedes, never guessed.
5. Write rso/slice001/expected/EXPOSURE.md: what you read, in what
   order, your prior exposure (Fable corpora, earlier sessions), and
   that the table was COMMITTED before step 6.
6. Commit and push the table. ONLY THEN read the author-expected
   columns and write rso/slice001/expected/COMPARISON.md: every
   disagreement between your table and the authors', unresolved, as
   evidence for T020. Do not edit your committed table after reading
   them; a correction is a new file beside it.

Mechanics on this host:
- Worktree root C:/Prometheus-worktrees/ (e.g. pallas-c004-t005);
  canonical checkout C:/Prometheus is fetch-only. Never git pull.
- No git identity configured: git -c user.name=jcraig949jfi -c
  user.email=jcraig@jfi.ai commit -F <file>
- EW_DB_HOST=192.168.1.202 for comms and workgraph.
- Wrap git/network calls in timeouts; worktree add needs >= 900 s.
- Caps: reviewer time counts toward 3 reviewer hours (OP-1); this packet
  ceiling is about 1 hour.

Scope: this packet only. Do not take T030 or T041 (PROPOSED). Session
close (base RESPONSIBILITIES s7) and stop.
----------------------------------------------------------------------
