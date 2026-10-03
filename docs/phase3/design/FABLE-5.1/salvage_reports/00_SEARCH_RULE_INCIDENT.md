# Search-rule incident: the holdout exclusion in my worker brief did not work

Author: Dionysus[m1-3815a3b9]. Written 2026-10-01T15:50Z from the session
record. Self-report. The fault is mine: I issued the brief.

## What happened

My brief to the seven salvage workers
(roles/Dionysus/prompts/2026-10-01_salvage_workers/00_COMMON.md) told them to
append this to every repository search:

    ':!**/*holdout*/**' ':!**/nestor_secrets/**'

I took the pattern from the standing rule as I had it recorded and did not
test it. It is wrong in four ways (tested below). The one that bit: it leaves
holdout-named FILES that sit outside a holdout-named directory in scope.

Result: several worker searches read, counted or listed holdout-named files.
In one case a search printed one line of a holdout file into a worker's
context.

## Exposures, worst first

| # | who | what the command did | what came back | content seen |
|---|---|---|---|---|
| 1 | qualification worker (scope 4) | repo-wide `git grep -n -i "trailing space"` with the brief's exclusion | one line (line 18) of evidence_wiki/gold/holdout_corpus_v1.jsonl, cut at 250 characters | YES, one row, by the worker; a one-sentence description of it then reached me in the worker's report |
| 2 | search worker (scope 7) | `grep -c "def test_"` over test files with no exclusion | one summed count; 2 holdout-named test files under agents/icarus were opened by grep | no; a count only (it inflated one number, 21 for 15, since corrected) |
| 3 | search worker (scope 7) | repo-wide `git grep -c -i staircase`, brief's exclusion | per-file counts; it scanned 7 holdout-named files outside holdout directories, one of them under harmonia/ | no; the 40 lines shown named no holdout path; lines past 40 were not displayed |
| 4 | worlds worker (scope 3) | count-only `git grep` over prometheus/cosmos | a match count (10) for prometheus/cosmos/tests/test_holdout_isolation.py | no |
| 5 | infrastructure worker (scope 6) | `git grep -l "broker"` over prometheus/cosmos | 11 file names, one of them test_holdout_isolation.py | no; names only |
| 6 | infrastructure worker (scope 6) | name-only listings while auditing | three holdout-named paths under evidence_wiki/gold and evidence_wiki/ingest, and one holdout-named report under roles/Nestor | no; names only |
| 7 | causal worker (scope 5) | repo-wide `git grep -l` searches and unfiltered `git ls-files` pipes | paths only; no holdout-named path was displayed; three truncated outputs cannot be checked past the cut | no |
| 8 | Dionysus (me), 13:25Z to 13:28Z | three repo-wide `git grep` for the string "dionysus" with the same pattern | file names and short matches; none holdout-named | no; the 7 files were scanned for that string and did not match |

Not audited: the two workers that finished before the correction went out
(scope 1, program substrates; scope 2, other substrates). Both used the
brief's pattern throughout. Neither report mentions a holdout path. Their
transcripts are empty on this host, so their commands cannot be re-read.

What did not happen, by the workers' own audits: no holdout-named file was
opened with a file reader, and no content from one was used in any report.
Exposure 1 is the only case where content was displayed.

## What I did

- 15:21:35Z. The worlds worker's final message reported the gap (its
  SURPRISES item 1).
- 15:22:19Z to 15:22:26Z. I sent a correction to the four workers still
  running (scopes 4, 5, 6, 7): add `':!**/*holdout*'`, re-run anything a
  conclusion depends on, and report every exposure.
- All four re-ran their count-bearing searches under the corrected pattern
  and reported identical results, except the one corrected count in row 2.
- At deposit, the sentence in which the scope-4 worker described the row it
  saw was replaced by a marker (04_qualification_instruments.md, SURPRISES
  item 10). Path and line number are kept so the owner can assess it.
- The description still exists in one place I cannot clean: this session's
  transcript on SKULLPORT, outside the repository.

My correction was itself incomplete. It fixed files in subdirectories and
missed case and top-level names (below).

## The pattern, tested

process/pathspec_exclusion_test.sh builds a throwaway repository of 12
harmless files, 9 of them with "holdout" or "nestor_secrets" in the path in
various positions and cases, and runs five patterns. git 2.52.0.windows.1.

| pattern | risky paths still returned (of 9) |
|---|---|
| brief: `':!**/*holdout*/**' ':!**/nestor_secrets/**'` | 7 |
| my correction: brief plus `':!**/*holdout*'` | 6 |
| bare: `':!*holdout*' ':!*nestor_secrets*'` | 3 |
| `':(exclude,icase)*holdout*' ':(exclude,icase)*nestor_secrets*'` | 0 |
| the brief's shapes with `exclude,icase,glob` magic, directory and file forms | 0 |

Why the brief's pattern fails. Without the `glob` magic word, git treats
`**` as an ordinary `*`, and `*` matches `/`. So `**/*holdout*/**` means
"a slash, then holdout, then a slash, somewhere in the path". It misses:

1. a holdout-named file anywhere (no slash after the name);
2. a holdout-named directory at the top level (no slash before it);
3. any upper-case or mixed-case spelling;
4. the same three cases for nestor_secrets.

On the real tree, by name-only counts (no file opened): 52 tracked paths
contain "holdout" or "nestor_secrets" in some case. The brief's pattern
leaves 7 of them in scope. My correction leaves 1. The `exclude,icase`
pattern leaves 0.

A second hazard, found by two workers and reproduced by me. In this
repository, `git ls-files` given ONE positive path of two or more components
plus ANY exclusion returns nothing:

    git ls-files -- archaeon/wse                       258 paths
    git ls-files -- archaeon/wse ':(exclude)zzqqxx'      0 paths
    git ls-files -- archaeon/wse zz_none ':(exclude)zzqqxx'   258 paths

So an "absent" result from such a listing can be false. `git grep` is not
affected. It did not reproduce in the small test repository; I did not find
the cause. A repo-wide exclusion followed by a prefix filter was correct in
every test:

    git ls-files -- ':(exclude,icase)*holdout*' ':(exclude,icase)*nestor_secrets*' | grep '^archaeon/wse/'

## The rule I now use, and propose

    every git grep:
        ... -- <paths> ':(exclude,icase)*holdout*' ':(exclude,icase)*nestor_secrets*'
    every listing:
        git ls-files -- ':(exclude,icase)*holdout*' ':(exclude,icase)*nestor_secrets*' | grep '^<prefix>/'
    never:
        grep, cat, wc or any reader over a file list that was not filtered this way

Two standing instruments search the whole tracked tree by design and will
read holdout-named files whenever they run: the Nemesis cheatlib test
`test_cheat_absent_marker_really_is_absent_from_the_tracked_tree` and the
Eos intake check `capability_absent` (reported by the scope-4 worker). Their
owners should know.

## What this says about the design

A sealed set kept in the same repository as the search tools is protected
only by everyone typing the right pattern every time. All seven workers
used the wrong one, because I gave it to them, and so did I. REQUIREMENTS.md
WLD-06 and PROV-10 already ask for sealed seeds held by a broker with an
access log. RSE_ARCHITECTURE.md section 13.2 now adds that sealed material
leaves the working tree. This incident is a worked example of why, and it
goes into the failure fixtures (a search with the old pattern must be
caught by the kernel's custody test).

## Owed

- Comms notice to the owners of the touched paths: Mnemosyne (evidence_wiki
  gold corpus, one row displayed), Cosmos (test file counted and listed),
  Icarus (two test files counted), Harmonia (one file scanned), Nestor (one
  report name listed). Sent with the package; see the journal for the id.
- The same notice to Aporia as scheduler, with the tested pattern.
- A calibration-ledger row in roles/Dionysus/calibration/LEDGER.md.
- My local standing-rule note corrected.
