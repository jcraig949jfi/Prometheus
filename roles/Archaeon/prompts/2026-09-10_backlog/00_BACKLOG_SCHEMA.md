BACKLOG SCHEMA (every seat files roles/<Seat>/BACKLOG_H0H5.md in this shape;
operator 2026-09-10, via Archaeon; authority as in
roles/Archaeon/prompts/2026-09-10_delegation/00_COMMON.md: commit to main,
push, report SHA + path; delete your merged branches)

One line per item, in priority order, at least 20 items, at most 60:

  <SEAT>-<NN> | <item, one sentence, a verb first> | <lane: H0|H1|H2|H3|H4|H5|C1..C4|ENGINE|TOOLS|EVIDENCE|LIT> |
  <milestone: alpha|beta|1.0|1.1|program> | <size: S (<1 day) | M (1-3 days) | L (1-2 weeks) | XL (needs a decision first)> |
  <blocked_on: none | seat name | operator decision D-nn | a named artifact> |
  <evidence of done: the committed file, test, receipt or number that will exist>

Rules:
- Every item names the ARTIFACT that proves it done. "Investigate X" is
  not an item; "commit the measurement of X with its command" is.
- Blocked items stay on the list with the blocker named; a backlog that
  hides blocked work is a backlog that will be waived on a busy afternoon.
- Items that need an operator decision are marked XL and the decision is
  named (D-nn from archaeon/docs/expansion/DECISIONS.md, or "NEW: <one
   sentence>"), so the operator's queue is derivable from the union of the
  seats' XL rows.
- The first five items are the ones you start today.
- Sources to draw from: archaeon/docs/expansion/ROADMAP.md section D and
  its annex (the 69 proposals, four branches, work packages), the
  H0-H5 design v0.1 milestone tables (alpha/beta/1.0/1.1 per lane),
  archaeon/docs/expansion/DECISIONS.md, roles/Archaeon/H0H5_STATUS.md,
  your own inbox and today's findings.
