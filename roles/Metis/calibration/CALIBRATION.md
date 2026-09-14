# Metis calibration ledger

Currency: 2026-09-11, opened on the seating pass.

This ledger is kept because it is unflattering (base s2). It records
this seat's wrong calls, its conflicts of interest, and predictions
written down in advance so they can be LOST.

## Conflicts of interest

1. THIS SEAT REPORTS ON OTHER SEATS AND ON ITSELF, IN THE SAME
   DOCUMENT. A brief that describes the program's health is written by
   a component of the program's health. Every Metis row about Metis is
   an author reporting on the author's own mechanism, and it is graded
   accordingly.
2. THIS SEAT HAS AN INCENTIVE TO PRODUCE. A reporting seat whose
   productivity signal is "a brief was generated" is rewarded for
   emitting something every cycle, which is exactly the pressure that
   produced six consecutive reworded briefs in March. The typing rule
   and the no-op requirement exist to make the null outcome cheaper
   than the fabricated one.
3. THIS SEAT IS ARGUING, IN ARCHAEOLOGY_2026-09-11.md, THAT IT SHOULD
   BE GIVEN AN UNOWNED LOOP. METIS-01 is a proposal that expands this
   seat's scope, written by this seat, on evidence this seat gathered.
   It is filed as an XL decision for the operator and is not acted on.

## Wrong calls (the seat's record)

    C-01  2026-03-22 .. 2026-03-28
    CALL      Six consecutive briefs told the operator to do the same
              three things (finish the Qwen3-4B run, wire the remaining
              Eos APIs, rent an A100 for Qwen2.5-7B), each time as new
              "Act on this" items.
    WRONG     No brief said "this is unchanged from yesterday". The
              repetition was invisible because every brief was
              byte-distinct: the LLM reworded the same claims daily.
    MEASURED  8 briefs, 8 distinct body hashes; Eos API item in 6 of 8,
              Qwen3-4B in 5 of 8, 7B cloud in 4 of 8.
    LESSON    Byte-identity is not a no-op detector downstream of an
              LLM. The detector must be over the CLAIM SET.
              (constraint 3; METIS-05, METIS-08)

    C-02  2026-03-31
    CALL      agents/metis/briefs/2026-03-31_brief.md was written and
              named like every other brief.
    WRONG     Its entire body is "(Metis could not reach any LLM
              provider)" -- the cascade's failure string. The stage's
              health checker (scripts/check_intelligence_pipeline.py,
              get_latest_report) returns a Path if a file with today's
              date exists and never opens it, so the failure would have
              read as health.
    LESSON    A produced artifact is a process success, never evidence
              that the artifact says anything. The monitor must read
              the payload. (base: verify the property, never the label)

    C-03  2026-09-01 .. 2026-09-09
    CALL      The reporter shipped briefs saying "no daemons require
              intervention" and "nothing trending toward intervention".
    WRONG     Its own input recorded degraded: true, data_source:
              "none", Redis unreachable AND Postgres unreachable. The
              degradation branch reads state.get("infra_status"), a key
              docs/state.json stopped emitting on 2026-09-01 when it
              moved to an "observability" block. The absent-key
              fallback is the optimistic literal "(state.json reports
              up)".
    MEASURED  By execution against the last real input, not by reading
              the code: the branch predicate evaluates False.
    LESSON    An absent key is not an up input. No fallback in this
              seat's code may be optimistic; fail loud or fail ABSENT,
              and check the input's schema version.
              (constraint 4; METIS-09)

    C-04  2026-09-11, this pass, within the first minute
    CALL      The seat ran `git pull` in the canonical checkout as its
              first action, because the wake directive said "Pull the
              latest from the repo first".
    WRONG     WORKING_CONTRACT.md s1 (no mutating git operation in the
              canonical checkout) and s3 (never `git pull`) were both
              violated before the seat had read them. The pull was a
              fast-forward on a clean tree, so no work was lost, and
              the seat then did it correctly: fetch, record
              origin/main, worktree add from the recorded SHA.
    NOTE      This is the SECOND recorded instance of this exact
              failure on this exact day (Atalanta L-09 is the first,
              same cause, same wording). Two independent seats failing
              the same way on the same directive is a defect in the
              constitution's ORDERING, not in two seats' care: the rule
              lives in a file the seat is told to read after it has
              been told to pull. Reported as METIS-06.
    LESSON    For this seat: read WORKING_CONTRACT.md before the first
              git command, not in boot step 4.

    C-05  2026-09-11, the season-1 precondition survey
    CALL      Reported greedy-LoRA NOT LOCATABLE after searching for it
              two ways.
    WRONG     roles/Ergon/GREEDY_LORA_RESULT_2026-06-03.md exists, 179
              lines plus a 2026-06-04 addendum, and is the strongest
              case in the whole episode set. The first search piped
              `git ls-files` through `head -40` and the path sorts
              below the cut; the second used `git grep`, which searches
              contents, not filenames. A third search in the same pass
              matched "expLORAtion" on a case-insensitive substring.
    COST      Had this reached the operator's season prompt, the best
              available episode would have been dropped from the set on
              this seat's say-so.
    LESSON    Base s2 already says it: enumerate the inventory, never
              read a prefix. A negative existence claim is the one
              claim a prefix can never support. For this seat
              specifically: a compression instrument that reports
              "nothing there" is making its most dangerous kind of
              claim, because absence is what compression produces by
              default.

## Pre-registered predictions (written now so they can be lost)

P-1. If METIS-08 (the claim-set no-op detector) is built and replayed
     against the 8 archived analyst briefs, it will flag at least 4 of
     the 8 as reworded repeats. It could flag 0-2 and I would be wrong;
     the count is committed before the detector exists.

P-2. If METIS-12 is run -- the search for any committed artifact in
     this repository that cites a Metis brief as the reason for a
     decision -- the answer will be ZERO. I expect this seat's entire
     six-month output to have changed no recorded decision, and I am
     writing that down before looking, because the opposite result
     would be the strongest thing anyone could say for the seat and I
     do not want to be able to claim it retroactively.

P-3. If METIS-03 resolves, the deployed docs/state.json producer will
     turn out to be a NEWER version of scripts/portfolio_monitor.py
     living only on the producing host, not a different program. I
     give this the weaker grade: the alternative (a separate program
     nobody has named) is live, and "the deployed code is ahead of the
     repository" is the comfortable answer, which is a reason to
     distrust it.

P-4. SUPERSEDED 2026-09-11 by the operator's ruling: the seat is
     re-premised to composition, not to brief production, so there are
     no cycles to be no-ops. The original prediction is kept visible
     rather than deleted, and it is UNRESOLVED, not right or wrong.

P-5. (Season 1, written before the season prompt exists.) A
     deterministic composition rule fitted on these five episodes will
     NOT beat the best single evidence channel out of sample. My reason
     is greedy-LoRA: the four agreeing channels there were correlated
     through a shared format-following gain, so channel AGREEMENT was
     anti-predictive, and a rule that counts agreement gets that
     episode exactly backwards. I expect the season's honest output to
     be a negative result plus a named veto primitive, not a working
     selector. If a working selector does emerge from five episodes, I
     should be suspected of fitting it, and the train/test split in
     section 7 of the precondition ledger is the thing that would
     catch me.

P-6. The single most useful artifact this season produces will be the
     VETO list, not the ranking. I predict that "which experiments a
     rule refuses to select, and why" survives contact with a sixth
     episode, and that the ranking does not.
