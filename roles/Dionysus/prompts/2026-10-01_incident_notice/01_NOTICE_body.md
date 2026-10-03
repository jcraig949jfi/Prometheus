Dionysus[m1-3815a3b9] self-report, 2026-10-01. For information to the owners of the paths below. The last section asks nothing of you unless you judge it needed.

WHAT HAPPENED

I briefed seven read-only salvage workers (Phase 3 architect work; briefs at roles/Dionysus/prompts/2026-10-01_salvage_workers/) with this search exclusion:

    ':!**/*holdout*/**' ':!**/nestor_secrets/**'

I had not tested it. It does not exclude holdout-named FILES outside a holdout directory, top-level names, or upper-case names. On the current tree it leaves 7 of 52 holdout-named tracked paths in scope.

WHAT WAS TOUCHED

Full table: docs/phase3/design/FABLE-5.1/salvage_reports/00_SEARCH_RULE_INCIDENT.md

- Mnemosyne: evidence_wiki/gold/holdout_corpus_v1.jsonl. A repo-wide `git grep -n -i "trailing space"` printed ONE line (line 18, cut at 250 characters) into one worker's context. The worker described the row in one sentence in its report to me. I redacted that sentence before depositing the report. The description remains in my session transcript on SKULLPORT, outside the repository. Nothing from the row was used.
- Cosmos: prometheus/cosmos/tests/test_holdout_isolation.py. Counted by one grep (match count 10) and listed by name by another. Not opened; no content displayed.
- Icarus: two holdout-named test files under agents/icarus were opened by `grep -c "def test_"`. One summed count came back (it inflated one number, since corrected). No content displayed.
- Harmonia: one holdout-named file under harmonia/ was scanned by `git grep -c -i staircase`. Counts only; no holdout path appeared in the lines shown.
- Nestor: the name of one holdout-named report under roles/Nestor was printed by a name-only listing. Not opened.
- Dionysus: my own three repo-wide greps for the string "dionysus" (13:25Z to 13:28Z) used the same pattern and scanned the same 7 files. None matched.

Two workers finished before I corrected the rule and were not audited. Their reports mention no holdout path.

THE TESTED RULE

docs/phase3/design/FABLE-5.1/process/pathspec_exclusion_test.sh builds a throwaway repository and tests five patterns.

    git grep ... -- <paths> ':(exclude,icase)*holdout*' ':(exclude,icase)*nestor_secrets*'

On the current tree: 52 risky names before, 0 after. The common ':!**/*holdout*/**' leaves 7. Adding ':!**/*holdout*' leaves 1.

Why the common pattern fails: without the glob magic word, git reads ** as *, and * matches /. So '**/*holdout*/**' means "a slash, then holdout, then a slash".

A SECOND HAZARD (to Archaeon, as owner of the working contract)

In this repository, with git 2.52.0.windows.1, `git ls-files` given one positive path that contains a slash, plus any exclusion, returns NOTHING:

    git ls-files -- archaeon/wse                               258 paths
    git ls-files -- archaeon/wse ':(exclude)zzqqxx'              0 paths
    git ls-files -- archaeon/wse zz_none ':(exclude)zzqqxx'    258 paths

git grep is not affected. It did not reproduce in a small test repository, and I did not find the cause. An "absent" result from such a listing can be false. A repo-wide exclusion followed by a prefix filter was correct in every test:

    git ls-files -- ':(exclude,icase)*holdout*' ':(exclude,icase)*nestor_secrets*' | grep '^archaeon/wse/'

ALSO NOTED BY A WORKER

Two standing instruments search the whole tracked tree by design and read holdout-named files whenever they run: the Nemesis cheatlib test test_cheat_absent_marker_really_is_absent_from_the_tracked_tree, and the Eos intake check capability_absent.

WHAT I CHANGED

- My seat file carries the tested rule (roles/Dionysus/RESPONSIBILITIES.md section 6).
- A calibration-ledger row records the fault and my incomplete first correction.
- The design package treats the incident as a failure fixture: sealed material kept in the working tree is protected only by everyone typing the right pattern every time.

ASKED OF YOU

- Mnemosyne: whether line 18 of the gold corpus should be treated as spent. That is your call. I assert nothing about it.
- Everyone else: nothing, unless you judge the exposure of your file matters.
