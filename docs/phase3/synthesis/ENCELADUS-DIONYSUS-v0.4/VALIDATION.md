# Validation of the synthesis delivery

Date: 2026-10-02. Enceladus / BUCKKEEP. Python 3.13.5 on Windows.
Worktree: C:/Prometheus-worktrees/enceladus-base-role.
Branch: enceladus/rso-synthesis-2026-10-02.
Base: 9af020b248a35bf55cf5def242aa0ee565982224.
Initial tracked tree and index clean; linked-worktree guard passed.
This delivery adds documents only. Science NOT_VERIFIED; review PENDING.

## 1. Prior delivery and source identity

The earlier hardening branch was already committed and pushed. Its exact
remote tip was verified as 9af020b248a35bf55cf5def242aa0ee565982224.
Fetch obtained origin/main at 563ee7c36fcd88dcf20f4a7f7e8b3902e9c30bae.
The latest scoped Fable commit is 3669bc7f2595dca2ead5348d0297a122a4ed74fe;
its hardening subtree has no diff against that fetched main snapshot.
No local main checkout, merge, rebase or main push was performed.

## 2. Executed unit checks

| Suite | Command, run in its harness directory | Result |
| --- | --- | --- |
| ASTRA v0.3 | python -B -m unittest discover -v | 28 tests; 0 failures/errors/skips; exit 0; unittest time 0.047 s |
| Fable delivered amendments | python -B -m unittest discover -v | 110 tests; 0 failures/errors/skips; exit 0; unittest time 9.622 s |

ASTRA ran from the existing reference_harness in the linked worktree.
Fable ran from exact git objects exported into a newly created temporary
directory outside all worktrees:
C:/Users/jcrai/AppData/Local/Temp/enceladus-fable-synthesis-td0vcbcv.
The export held 27 files: the 23-file harness subtree and four historical
counterfeit receipts identified in SOURCE_INDEX.json. Set RSO_COUNTERFEIT
to that export's counterfeit directory; disable bytecode writes. All 20
file entries in the three exported harness manifests matched SHA-256 over
LF-normalized bytes. Every exported source/dependency byte was unchanged
after testing. No source receipt writer was run.

Fable command wall time including process startup was 25.617 seconds; this
is not the entire review's engineering cost. Its captured stdout+stderr,
UTF-8 encoded, SHA-256 was
96976a1fdf313dcf05d6654fe5dc6e16d608b93c0664440b78a676d5433174db.
That transcript hash identifies the observed output; the transcript is in
the agent tool history, not a separate repository artifact or custody seal.

The export is scratch, not a delivery dependency. No original file was
deleted or rewritten. A later reviewer can export the same pinned subtree
and four receipts into their own scratch; the machine-specific path is not
required. Fable's delivered receipt reports Python 3.12.10 on SKULLPORT;
this rerun is a software portability check on 3.13.5, not native replication.

## 3. Meaning and non-execution

- Fable's suite asserts its 21 gates, 50 sound cases, 258 non-passing cases
  and 29 known escapes. It deliberately expects those listed escapes to
  remain escapes. Suite PASS therefore does not mean every gate is safe.
- The Fable mutation receipt was read, not regenerated: 247 proposed edits,
  244 executed, 218 distinct; 236 noticed, 211 distinct. Historical first-sight
  scores are source-reported, not new measurements of this synthesis.
- ASTRA's five selected source-mutant tests ran within the 28-test suite.
  Their selected kills do not estimate a general fault-detection rate.
- No first-sight challenge, statistical/native experiment, new gate,
  independent scientific replication or strong-recursion test was performed.
- No Fable report checker, report fire test, full mutation probe, full
  scientific receipt writer, or complete historical attack replay was rerun.
- The parent read the actual Fable source documents and final reader reports.
  An auxiliary retrieval-only agent could not access the git-pinned sources;
  it supplied no usable review and is not counted as independent validation.
- Evidence Wiki client import failed with ModuleNotFoundError. No wiki
  evidence was imported or submitted; the repository package is the record.
- The original ChatGPT harness remains absent from C:/Prometheus_Phase3.
  Neither author's new harness is treated as a successful run of that input.

## 4. Documentary and delivery checks

First static pass: 14 source hashes/byte lengths, the harness tree identity,
receipt counts, 11 decision IDs and 14 acceptance IDs checked successfully.
It returned exit 1 because all seven newly added files lacked final newlines.
Those are formatting errors, not failed science; corrected before delivery.
The complete package pass then returned exit 0: eight files ASCII/LF with
final newlines, nine local Markdown links, 14 source pins, 11 decision IDs,
14 acceptance IDs and seven manifest entries. The staged set contained only
the eight new package files; staged blob bytes matched working bytes and
git diff --cached --check passed. The same checks are repeated after this
receipt update before commit. Git warned about future CRLF checkout on this
machine; verify the manifest against git blobs or LF-normalized file bytes,
not a checkout's CRLF encoding. No space/column normalization is permitted.

A separate internal documentary reader inspected four new documents, not
the source experiments. It found two protocol gaps: unresolved equivalence
could escape the mutation exit rule, and fresh closure coverage was not
fixed. Both are now explicit in the plan, including closure ownership,
pre-outcome commitment and shared caps. It also requested final check status
here. This is internal editing assistance, NOT Dionysus review or independent
scientific validation. Content checks cannot validate the scientific argument.

## 5. Remaining gate

Dionysus must return ACCEPT/AMEND/REJECT for D01-D11 and a review verdict.
Only then can the lead freeze a concrete implementation contract, approve
caps with the operator, and start the proposed bounded next slice. No task
in this delivery claims that those later conditions have already been met.
