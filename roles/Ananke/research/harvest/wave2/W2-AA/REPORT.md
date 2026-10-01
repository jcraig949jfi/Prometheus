<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-AA; sha256(report)=2680b051ee72e578; delimited; see REPORT.provenance.json -->
W2-AA: kind_audit as a production tool, an advisory deposit.py hook, and the current HIGH list

All files are in roles/Ananke/research/harvest/wave2/W2-AA/. No original file was edited: `git status` on research/deposit.py, research/tools and research/tests is clean.

DELIVERABLES
- tools/kind_audit.py (proposed path roles/Ananke/research/tools/kind_audit.py), sha256 60415819...
  - Pure stdlib. It has its own gzip loader for roles/Ananke/pte/c1_rows/cells.jsonl.gz, because hp_common.rows() imports torch.
  - Finds the rows file by walking up from the tool's own path, or from $KIND_AUDIT_ROWS / --rows.
  - CLI: `kind_audit.py PATH... [--ext] [--min-len 8] [--scope block|window] [--fail-on HIGH|NAMING|LOW|none] [--json] [--csv] [--all] [--exclude GLOB]`.
  - Exit codes: 0 clean, 1 at least one flag at or above --fail-on (default HIGH), 2 cannot run (rows missing, path missing).
- patches/deposit_kind_audit.diff: unified diff against the current research/deposit.py (blob ab5d49a74).
- patches/W2-AA_kind_audit_full.patch: the deposit diff plus the 3 new files, using repo paths. `git apply --check` is clean. Applying it into a scratch tree (scratch/applied2) reproduces my files exactly (apart from CRLF from Windows autocrlf), and 19/19 tests pass there.
- tests/test_kind_audit_tool.py (13 tests) and tests/test_deposit_kind_audit.py (2 tests); proposed path roles/Ananke/research/tests/.
- logs/tests_before.log, logs/tests_after.log, logs/tests_applied_patch.log, logs/parity_check.py + .log, logs/harvest_HIGH.log, logs/kind_audit_harvest_citations.csv.

1. FINDINGS

F1 [V] Fail before, pass after. Confidence: high.
- Check: copies of the original deposit.py and test_deposit.py in scratch/before (no tools/), and the patched copies in scratch/after. Run `python -m pytest tests -q -rA` in each.
- Before: 4 passed, 2 failed, 13 errors (rc=1).
  - test_deposit.py: 4/4 pass.
  - The 13 kind_audit tool tests error with FileNotFoundError (the module is absent).
  - The 2 deposit tests fail: `KeyError: 'kind_audit'` and `AttributeError: no KIND_AUDIT`.
- After: 19 passed (rc=0), including all 4 original deposit tests.
- Mutation checks, each confirmed to kill at least one test:
  - id regex reverted to lower-case only;
  - REPORT.md line offset removed;
  - LOW branch removed;
  - REPORT.md bytes altered;
  - own-output exclusion removed;
  - exit code inverted;
  - no parent-item spans;
  - no nested children;
  - table row reduced to the token only;
  - no backward hard-wrap join (this one survived my first version of the test, so I strengthened the test);
  - severity_window dropped.
- Strongest objection: the tests use the real C1 rows and the live PRINCIPAL_REVIEW.md, so they depend on the repo (freeze_check's tests do the same).

F2 [V] With `--scope window` the tool reproduces W2-I exactly. Confidence: high.
- Check: logs/parity_check.py.
- Over roles/Ananke .md/.txt: 5047 citations each, with identical severities (11 HIGH / 23 NAMING / 58 LOW in both). No citation is found by only one tool.

F3 [V] The recall gaps W2-I listed are empty in the current corpus. Confidence: high.
- Upper-case and mixed-case ids: 0 citations. Case-insensitive matching is implemented and tested, but finds nothing new today.
- Ids under 8 hex: with min_len 6 or 7, 0 tokens resolve. There are 249 7-hex tokens in .md/.txt, and none is a unique prefix of a cell id.
  - 7-hex prefixes are unique among the 6596 cell ids; one 6-hex prefix collides.
  - So `--min-len 7` is available as an opt-in, but the default stays 8.
- .py: this is the one gap with real content. Excluding test fixtures there are 5 HIGH, and 1 of them is true:
  - H-PLANT/run_flip_mh.py:12 has `MH_CELL = "fac4aaa23a0bdcb2"  # C1 wave C, RELAY d5 at d9cc, held .5 (NULL)`. This is the same misattribution as the H-PLANT REPORT, now in code.
  - The other 4 are false: W2-G ledger_build.py:189 is a quoted string, and rederive_c1.py:417 is `"held"` as a dict key.
- .json/.jsonl: 51 HIGH, all false. They come from "held" accuracy keys in data files.
- Decision: the default extensions stay .md/.txt; .py and .json are opt-in via --ext. Files named `kind_audit*.csv` / `kind_audit*.json` are always excluded so that earlier audit output is not counted again.
- Strongest objection: the .py precision (1 of 5) is measured on one corpus.

F4 [V] Block scope (the new default) removes W2-I's neighbouring-bullet false HIGHs and loses no known true positive. Confidence: medium-high.
- W2-I's window let the words "held" and "champion" in an adjacent bullet or numbered item raise HIGH:
  - wave2/INFERENCE_LEDGER.md:347 926328ee (census B2): the "held" belongs to the N1 bullet, the citation is in N3;
  - wave2/W2-E/REPORT.md:145 926328ee: the "champion .77" belongs to item 7, the citation is in item 8.
  - Both are correct uses of the census cell as an environment point.
- How block scope works:
  - The block is the citation's paragraph or list item, with hard-wrapped lines joined.
  - It also includes nested children and the first line of each enclosing parent item.
  - For a `|` table/ledger row, the block is the whole row.
  - Everything is still clipped to ±200 characters.
  - The LOW exoneration still uses the full window.
- Effect over roles/Ananke: HIGH 11→9, NAMING 23→12, LOW 58→48. I read the 23 changed rows; the dropped ones read correctly as non-flags (W-G 57/80/82, W2-R 97/98, W2-S 201, and others).
- Nothing is hidden. Every record also carries `severity_window` (the W2-I verdict) and `terms_outside_block`. The deposit provenance stores both `counts` and `counts_window_scope`, and lists any citation flagged under either scope.
- Strongest objection: a heading or a lead-in paragraph above a top-level list ("## C1 search NULLs" then "- fac4aaa2") is outside the block. That is recall loss by design, recoverable with `--scope window` or by reading `severity_window`.

F5 [V] The deposit integration is advisory and keeps the verbatim rule. Confidence: high.
- Behaviour:
  - After REPORT.md is written, it runs kind_audit on the extracted block.
  - It records `prov["kind_audit"]` = {status, tool, rows, min_len, scope, citations, counts, counts_window_scope, flags[line in REPORT.md, token, cell_id, kind, wave, severity, severity_window, terms, terms_outside_block]}.
  - Any exception gives `status: "NOT_VERIFIED"` plus the error. It never raises and never touches REPORT.md.
- Tests check that REPORT.md bytes equal header + block + "\n", both with the auditor working and with it missing.
- End-to-end check: I deposited H-PLANT/REPORT.md as W-DEMO with the patched deposit.py in scratch/after.
  - Result: "verified", body byte-identical, kind_audit ok with HIGH=3 (lines 30/51/60 of REPORT.md, which are source lines 29/50/59 shifted by the header).
- Costs:
  - about 0.7 s per deposit to load the rows;
  - the "rows" field is an absolute machine path;
  - the CLI prints the audit counts after "verified".

F6 [V] Current HIGH hits over roles/Ananke/research/harvest. Confidence: high for the list; judgements below.
- Command: `python tools/kind_audit.py roles/Ananke/research/harvest --exclude "*/W2-AA/scratch/*"`, rc=1.
- 3847 citations; HIGH 9, NAMING 2, LOW 45. (With --scope window: HIGH 11, NAMING 10, LOW 55.)
- The H-PLANT lines, as expected; all 4 are true:
  1. H-PLANT/PLAN.md:120 fac4aaa23a0bdcb2 [transfer/C]: "C1 cell fac4aaa23a0bdcb2 (NULL, held .5)".
  2. H-PLANT/REPORT.md:29 1b26026fc846d03d [transfer/C]: "the one XOR point where C1 searched".
  3. H-PLANT/REPORT.md:50 ef77ef2e [transfer/C]: "FLIP NULLs (cells 6f82f9c7, held .479, and ef77ef2e, held .507)".
  4. H-PLANT/REPORT.md:59 fac4aaa23a0bdcb2 [transfer/C]: "C1 RELAY NULL cell ... C1 search held .5".
- The rest are false positives. 5-9 quote the error in order to criticise it:
  5. wave2/W2-G/REPORT.md:253 f7e62fe3 [adjudicate/D]: a ledger row whose question column says "transfers cited as search NULLs" (meta).
  6-9. wave2/W2-I/REPORT.md:143 (1b26026f, ef77ef2e, fac4aaa2 x2): W2-I's own hand check quotes the bad lines.
- Opt-in .py finding (not counted above): H-PLANT/run_flip_mh.py:12 is true; see F3.
- Principal's correction: PRINCIPAL_REVIEW.md has 12 citations, HIGH 0, LOW 6 (exit 0). Lines 44-46 of the 2026-10-01 Correction read LOW because "TRANSFER" is named in the window. A test pins this.

2. PROPOSED FIXES
- NEUTRAL: add tools/kind_audit.py and the 2 test files; apply patches/deposit_kind_audit.diff. None of this changes any frozen semantics.
  - Apply with: `git apply roles/Ananke/research/harvest/wave2/W2-AA/patches/W2-AA_kind_audit_full.patch`.
  - Then run: `python -m pytest roles/Ananke/research/tests -q` (expect 4 + 15 = 19 kind/deposit tests to pass, plus the freeze_check tests).
- NEUTRAL, not done: H-PLANT/run_flip_mh.py:12 repeats the misattribution in a comment. A comment-only correction there, or an erratum note, is up to the principal.

3. DISAGREEMENTS
- With W2-I:
  - Its recall-gap list (under-8 hex, upper case, .py/.json) is mostly theoretical. Under-8 and upper case have 0 instances.
  - The real gap is .py, and it holds 1 true hit. Opt-in JSON scanning is pure noise.
  - Its ±200 window caused 2 false HIGHs (926328ee).
  - Its summary figures (1411 citations, 5 HIGH) are stale: the corpus now gives 5047 citations and 11 window-scope HIGHs.
- With W2-G's ledger NQ2 entry "doc regex may miss ids <8 hex": that gap is empty in practice (F3).
- None with the principal. The correction reads LOW as intended.

4. NEXT QUESTIONS (ranked)
1. Should deposit-time HIGH also be shown to the principal in the CLI output and synthesis checklist, not only stored in JSON? It is currently printed as counts only.
2. A baseline/allow-list (fingerprint = file + cell + line-text hash) for known meta-citations such as W2-I:143 and W2-G:253, so that `kind_audit` over harvest can exit 0 in CI. Is that wanted, given that the H-PLANT REPORT is immutable?
3. Should quoted spans ("...") be discounted, to silence citations that quote an error? This risks hiding real misattributions written inside quotes; it needs measuring.
4. Heading-scope recall: count how many window-only flags come from a heading or lead-in, to decide whether to add the nearest heading to the block.
5. For .py: scan only comments and docstrings (tokenize module) so the opt-in becomes precise enough to be a default.
6. Should the auditor also check C1b rows that carry their own ids (c1b_rows), if any differ from C1 cell ids? I relied on W2-I's statement that they do not.
7. Fold this into W2-F explib.provenance.support_check as a "kind" Check (PASS/FAIL/NOT_VERIFIED), so claim ledgers and deposits share one primitive.

5. INFERENCE LEDGER
question | evidence | result | confidence | strongest objection | unresolved | next
- tool matches W2-I | parity_check.py over roles/Ananke | 5047/5047, identical severities (window scope) | high | parity is on today's corpus only | none | keep scope=window as the compat path
- case-insensitive ids worth it | count of upper/mixed resolving tokens | 0 today; costs no precision (must resolve) | high | future reports may use upper case | none | keep on
- under-8-hex ids | min_len 6/7 scans, prefix-uniqueness check | 0 resolve of 249 7-hex tokens | high | git short shas could collide in the future (p ~2.5e-5 per token) | none | default 8, opt-in 7
- .py/.json scanning | --ext runs, manual read | .py: 1 true / 4 false (non-test); .json: 51 false | medium | small sample | comment-only scan | opt-in only
- block vs window scope | 23 changed rows read by hand | 2 false HIGH removed, no known true lost | medium-high | heading/lead-in recall loss | heading census | default block, severity_window kept
- deposit hook keeps verbatim | byte-equality tests + W-DEMO e2e | bytes identical, flags recorded, never blocks | high | 0.7 s rows load per deposit | none | principal applies
- current HIGHs | harvest run | 4 true (H-PLANT) + 5 meta false + 1 true in .py | high | judgement on meta lines is manual | baseline file | NQ2
- principal correction | PRINCIPAL_REVIEW.md scan | HIGH 0, LOW 6 | high | relies on the word "TRANSFER" being in the window | none | test pins it

6. COMPUTE
CPU only, under 0.01 core-hours in total (cap 0.1). The longest step was the pytest runs (2-19 s each); each full scan takes about 1 s. No torch, no GPU, no leases.

Scratch leftovers inside my directory: scratch/before, after, mut, applied, applied2, demo_message.txt, and after/workers/W-DEMO. The canonical scan excludes them with `--exclude "*/W2-AA/scratch/*"`.
