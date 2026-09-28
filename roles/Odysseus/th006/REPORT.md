# TH-006 slice -- portable verification of C-001/E-001/T-001 (BEE r038751)

Currency: 2026-09-27T16:05Z. Owner of this slice: Odysseus (ubu001).
Directive verbatim: roles/Odysseus/prompts/2026-09-27_th006/.
Status: CLOSED. Node side closed 2026-09-27; M2 attestation MATCH (Archaeon #799,
2026-09-28T10:08Z, commit f525de9ef on archaeon/attribution-v0-2026-09-28).
Pure ASCII.

## 1. CLAIM

What T-001's verification claimed before this work (E-001 TASKS.md,
A-002 receipt; b6_probe_analyze.py):
- (a) result_sha256 cd9547c2... of the probe's output = the M2 reference;
- (b) "74,800/74,800 rows identical to BEE's preserved log", checked ON M2
  by positional list equality against
  C:/Users/James/z80atlas_forensics_2026-09-23_local/births/r038751.jsonl.gz;
- (c) the science: archaeon/causal_lens/out_v02/B6_PROBE_r038751.json --
  of 28,163 births that location calls foreign-governed (W_by_location=NO),
  material says 27,083 own, 21 foreign, 1,059 NI; writes in those births:
  1,726,650 by self-copied code, 941 by foreign code, 5,978 own-region,
  66,669 elsewhere; plus the full 6-cell location x material table and
  the native-SR split (42,703 / 212).

Claim boundary found in Spike 1:
- The preserved log is ONE file of 74,800 rows x 20 fields (the "282 MB"
  is the whole births/ directory, all runs). Its decompressed content,
  predicted here, is 8,118,119 bytes; gzip -9 of it is 833,975 bytes.
- The science (c) is computed from the REPLAY, not from the preserved
  log, and reads only 4 row fields -- f7 writes, f8 copied_from_own,
  f9 by_own_code, f11 is_sr -- plus the probe's per-birth codeprov counts
  (which are not in the preserved log at all).
- The preserved log's only role is (b): proof that the instrumented
  replay reproduces the original traced replay row for row.
- Irrelevant to (c): f0-f6, f10, f12-f19 (tick, ids, mechanism,
  fidelities, material label, changed, depth, step counts, variant,
  fid_pre, is_sr_post, into_empty).

What can now be verified on a node without M2 (Spike 4, ubu001, no
network): (a) exactly; (c) exactly, recomputed from the rows by the
verifier's own rules and compared to BOTH the pack and the published
file; (b) as "the node's rows hash to the content hash the pack
commits" -- which becomes "... to the preserved log" only when M2
attests that hash (section 5).

## 2. PORTABILITY

What moved: one committed file, roles/Odysseus/th006/pack/r038751.pack.json
(10,970 bytes, sha256 212844af25d3f70f89cf936af6516ca97348cb6371d441273deb8c54f2332439):
content sha256 + byte count + row count of the preserved log's content,
75 chunk hashes (1,000 rows each), 20 per-field column hashes, the claim
fields and rules in words, the claim table, the probe result and codeprov
hashes, the replay recipe, the M2 path back to the original. Code and the
2 KB config were already in Git (E-001 made them portable).

Size: pack 10,970 B = 0.135% of the log's content (8.1 MB), ~1.3% of its
compressed size (~0.83 MB, my recompression; M2's .gz size is asked for),
and ~0.004% of the 282 MB directory the verification used to depend on.

Why content, not file: the pack hashes the DECOMPRESSED bytes, defined as
BEE's own writer defines them (json.dumps(row) + "\n"). That hash is
independent of gzip headers and can be checked on M2 with no Prometheus
code: `gzip -dc r038751.jsonl.gz | sha256sum`.

Node run (Spike 4; receipt in journal/2026-09-27.md; tools/node_check.sh at
1faf69a04), clean dir ~/prom_tasks/th006_T-001_A-001 built by git archive:
- sandbox: `sudo unshare -n` (no network: a connect to M1 gave "Network is
  unreachable"), python -I, env -i; every file open/list audited;
- replay: 52.27 s, peak RSS 143,776 KB; result_sha256 cd9547c2... ;
  harness module hashes = 16fc6c2a;
- verify: 1.44 s, peak RSS 136,684 KB; PACK, IDENTITY (74,800 rows,
  content 95a12c29...), CODEPROV, CLAIM (= pack and = published) all PASS;
- file accesses outside the task dir and the Python stdlib: none (the
  audit's own positive control flagged /etc/hostname, a listdir of $HOME
  and a nonexistent Windows-style path, so an empty list means empty);
- cleanup: dir removed, no task process left.
A second, earlier replay (exploratory, scratch) gave the same hashes.

## 3. CHEAT CONTROL

Real specimen (tools/real_cheats.py, on birth row 15, a
"location NO / material YES" birth):

| control | what was changed | verdict | caught by | table W=NO,mat=YES |
|---|---|---|---|---|
| C1 relevant | codeprov of one birth: self-copied writes -> foreign | FAIL | CODEPROV + CLAIM (identity PASS: the rows are untouched) | 27,083 -> 27,082 |
| C2 relevant | row f9 by_own_code := writes | FAIL | IDENTITY (field 9, chunk 0) + CLAIM | 27,083 -> 27,082 |
| C3 irrelevant | row f0 tick + 1 | FAIL | IDENTITY only (field 0, labelled outside the claim); CLAIM PASS | unchanged |

Synthetic suite (tests/test_th006_pack.py, 13 pass): honest replay passes;
relevant field that flips the table; relevant field that does NOT move the
table (identity fails, claim passes, reported as such); irrelevant field;
codeprov tamper; dropped / extra / swapped rows; a pack edited after
publication (refused by the caller-supplied pack sha256); attest MATCH on
the true source and MISMATCH (chunk 0, field 14) on an altered source;
the verifier's location rule equals archaeon's adapter on all edge rows.

The explicit choice (Spike 3): IDENTITY protects all 20 fields, so an
irrelevant-field change FAILS the verdict -- because (b), "these are the
preserved rows", is part of the published result. The report separates
it: claim_fields_changed = [] and CLAIM PASS say the science did not move.
A reader who only needs (c) can read the CLAIM status alone.

What the verifier protects, precisely: the replay's rows against the
pack's content hash (any byte); codeprov against its hash; the table
against recomputation. What it does NOT protect: see section 4.

## 4. TRUST (Spike 5) -- what we now rely on

1. The pack sha256 given to `verify` comes from Git (this report, commit
   1faf69a04). Git commits here are unsigned; Git's object hashing is
   SHA-1 (collision-hardened, not a signature). Nothing stronger is claimed.
2. OPEN LINK -- the pack was derived from a REPLAY, not from the preserved
   log. Until M2 attests, "identical to the preserved log" rests on the
   A-002 receipt (a prose claim, checked by positional list equality) plus
   the pack generator. This is the one place the pack currently MOVES
   trust rather than removing it. Closing it needs one M2 command
   (prompts/2026-09-27_th006/02_ATTEST_REQUEST_TO_ARCHAEON.md); the
   tool-independent form is `gzip -dc | sha256sum`, so the attestation
   need not trust my tool either.
3. make_pack and verify share one author and one file (common-mode risk).
   Mitigated, not removed: the trust anchor (content sha256) has a
   definition reproducible without the tool; the claim rules are written
   out in the pack and checked against archaeon's adapter; chunk and
   column hashes are diagnostics, not anchors.
4. The replay implementation: the frozen harness (git 16fc6c2a), BEE's
   traced VM (98a28dd39) and Archaeon's probe. Their DETERMINISM is
   evidenced (M2 and two ubu001 runs agree on cd9547c2...); their
   CORRECTNESS as instruments is the science's own question, untouched here.
5. codeprov exists only as replay output. It is verified by replay
   agreement across hosts, never against preserved evidence.
6. The published table (out_v02/B6_PROBE_r038751.json) as committed.
7. Python's json/hashlib/gzip, and the platform (Linux, Python 3.14.4 only
   so far).

Retained on M2 (full forensic reconstruction, not portable, not needed
for this claim): the preserved births log itself, the campaign run
directory (config.json, summary.json), the rest of the 282 MB births/
directory (other runs), the traced replay's summary-vs-stored fidelity
check (TRACER_DIVERGED), and anything about the original 2026-09-19
campaign run beyond what the traced replay recorded.

Opaque-summary test: the verifier does not trust the pack's table -- it
recomputes it; it does not trust the pack's identity hash blindly -- the
caller pins the pack by sha256 from Git; the one inherited link (2) is
named and has a pending one-command fix.

## 5. GENERALIZATION (only what this case shows)

For a claim computed from a DETERMINISTIC replay whose inputs and code are
in Git (as E-001 made them), evidence portability reduced to one number:
the content hash of the preserved artifact, defined on its decompressed,
writer-defined bytes. Everything else a node needs it can recompute.
Reusable pieces, as observed here:
- hash content not containers (tool-independent re-check);
- name the claim's fields and recompute the claim, rather than trust it;
- chunk + column hashes to localise a failure to a block and a field
  cheaply (row-level would cost more than the source);
- the no-network + audit-hook sandbox as evidence that a verification
  was local.
Not shown: anything for non-deterministic engines, GPU runs, or claims
that need the original run's raw traces; anything on Windows.
The cheapest structural fix is upstream: the WRITER of a preserved
artifact records its content hash in Git when it writes it. Then no
attestation round-trip is needed later.

## 6. NEXT THREADS (recorded, not executed)

N1 DONE: M2 attestation of 95a12c29... returned MATCH (#799; link 2 closed).
N2 T-002 / r016299 with the same tool (tests the claim that the pack is
   not r038751-specific; ~2 min on a node).
N3 Cross-host: node_check.sh on ubu002, then a Windows port of the node
   check (PowerShell; no unshare there) -- the Windows run is the
   informative one.
N4 Producer-side hashing: ask BEE's writer (traced_replay._one) and
   similar evidence writers to commit content hashes at write time.
N5 b6_probe_analyze.py counts `same` over zip(pres, replay), which stops
   at the shorter list; "74800/74800" is printed with len(pres), so a
   replay with EXTRA rows would still read 74800/74800. Not an error in
   this run (the node replay has exactly 74,800 rows); reported to its
   owner, not fixed here.

## 7. Artifacts

    roles/Odysseus/th006/pack/r038751.pack.json      the pack (10,970 B)
    roles/Odysseus/th006/pack/r038751.recipe.json    how the replay is produced
    roles/Odysseus/th006/tools/th006_pack.py         make / verify / attest
    roles/Odysseus/th006/tools/real_cheats.py        controls on the real specimen
    roles/Odysseus/th006/tools/audit_run.py          file-access audit
    roles/Odysseus/th006/tools/node_check.sh         the node procedure
    roles/Odysseus/th006/tests/test_th006_pack.py    13 tests (red at 455e2e94c)
    commits: 455e2e94c (tests red), 1faf69a04 (pack + tools; node check ran from it)
