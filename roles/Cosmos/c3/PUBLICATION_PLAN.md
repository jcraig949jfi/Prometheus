# Publication plan for the withheld C3 branch (operator Q-A ruling 2026-09-30)

Authority: roles/Cosmos/prompts/2026-09-30_operator_c4_review2_publication/. Publication is AUTHORIZED
only AFTER the foreign C4 visible family is committed and its provenance receipt is immutable, and only
for C4 visible-development use.
What is published: local branch cosmos/c3-s1-2026-09-24, head e73e5eb26aa3edbc786a1941817bce738b4f58ec.
The withheld autopsy branch cosmos/c3-autopsy-2026-09-30 is NOT covered by this authorization and stays
local unless the operator extends it.

## 1. Trigger (all of these, checked and recorded before any push)
T1 The foreign family's commit exists on origin/main (an ancestor of origin/main), with its PROVENANCE
   note and selftest, authored by a non-Cosmos seat. Record its commit id and blob hashes: this is the
   immutable pre-exposure receipt, and it is never rewritten.
T2 The author's machine could not read the M2-local withheld objects, or the author attests that it did
   not read the C3 substrate code. The first is preferred (M2 worktrees share one object store).

## 2. Verification (re-run at publication time; dry run 2026-09-30 below)
| # | condition (operator) | check | dry run |
|---|---|---|---|
| V1 | no D2 content | the branch diff vs its merge-base with origin/main touches no path under prometheus/cosmos/c3_holdout_D*/ and no Nestor/D2 path | PASS (0 paths) |
| V2 | no foreign-family hidden material | the branch diff touches no prometheus/cosmos/c4/families/ path (the branch predates the commission) | PASS (branch head 2026-09-25) |
| V3 | descended from the committed withheld hash | 0ecafed159f9bc9756baefd55ec37fd75b83b822 (INFO_LEDGER, FREEZES F-0000) is an ancestor of the published head | PASS |
| V4 | historical C3 receipts not altered | every path the branch changes is an ADDITION except roles/Cosmos/calibration/LEDGER.md, which main also changed. The merge must keep both sides (union, no deletion), and after the merge `git diff origin/main <merge>` on pre-existing main files must show additions only | 23 added / 1 modified; recheck at merge |
| V5 | substrates = the audited versions | substrates.py at the head = at the maps-producing commit 1b0bf8f7b (blob c0b43edc34c1...), and it equals the audit-bundle copy (LF sha256). The same holds for geometry, maps, certify, probe, system, task, calib, gate, hashing and MAPS.json | PASS (13 code files + MAPS.json + gate prereg MATCH the bundle; law/attack blobs = the maps commit) |
Also: research_check PASS; the cosmos test suite passes on the merged tree.

## 3. Procedure
1. Fetch; re-run V1-V5 against the current origin/main; record the results.
2. On a public branch from origin/main: `git merge --no-ff e73e5eb26`. Resolve LEDGER.md as a union.
   No other conflict is expected; any other conflict ABORTS and is reported.
3. Re-run V4 on the merge commit, then push to main.
4. Record the publication event in roles/Cosmos/c3/INFO_LEDGER.md: merge commit id, the V1-V5 results,
   and the foreign-family receipt. Add a FREEZES note that F-0000's target is now public and
   re-checkable.
5. Update the public autopsy s4: the withheld-branch rows become checkable on main. G-0006's law text
   becomes public, and G-0006 stays dead.
