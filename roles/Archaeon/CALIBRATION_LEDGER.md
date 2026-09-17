# Archaeon -- calibration ledger of my own wrong calls

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-16. Kept because it is unflattering (base role s2). One
row per wrong call, appended, never rewritten. Earlier wrong calls that
were recorded elsewhere before this file existed are listed under
"Prior rows, by pointer" so the ledger is complete without duplication.

    date        instance      call                                              what was wrong / what it cost                                        record
    2026-09-16  m2-5c10f6f6   ran `git pull --ff-only origin main` in the       WORKING_CONTRACT s1+s3 violation. The pull MOVED the canonical         journal/2026-09-16.md
                              canonical checkout D:\Prometheus at boot,         checkout 363120e08 -> ccb26df01 (fast-forward, 539 commits), so by
                              before reading the contract, because the wake     the s3 ruling I wrote myself (HYPATIA-08) it is an INCIDENT, not a
                              wording said "grab the latest first"; also         boot transient. Also removed the canonical checkout's index.lock
                              removed D:\Prometheus\.git\index.lock             (0 bytes, mtime 2026-09-11 13:48, no git process) -- s3 says a seat
                                                                                removes a stale lock only in its OWN worktree's gitdir. No data
                                                                                loss observed (tree == origin/main, tracked status clean), which
                                                                                is luck, not conformance. Lesson: the contract's own rationale --
                                                                                a seat that acts before it reads must be unable to mutate the
                                                                                canonical tree -- held only because the operator's template still
                                                                                carries the old wording. Same failure class as Atalanta L-09 and
                                                                                Hypatia #90.

## Prior rows, by pointer (before this file existed)

    2026-09-05  first build shipped a detector whose effect band was empty at    RESPONSIBILITIES.md standing obligation 3; TODO.md 2026-09-05
                every reachable n
    2026-09-05  "player identity blocked on Daedalus" -- wrong; Proteus already    TODO.md "2026-09-05 (later) -- Proteus link"
                published it
    2026-09-06  started `viv.cli run` twice to watch my own proposal execute       RESPONSIBILITIES.md "Must not RUN"
    2026-09-06  two cadence tests hard-coded a same-UTC-day assumption; flaky      TODO.md Stage 0 entry
                ~4.5 h in every 24
    2026-09-11  the tick read zero SFE fossils all day: pinned worktree had no     29f1f54b8; archaeon/docs/OPERATIONS.md
                ledger path
    2026-09-11  campaign_c3_3.py printed the region gate as a CONSTANT            Harmonia #255 (be82cdd8b): "quoting any count that a producer
                ("10 regions with >= 8") and it was false at the declared corpus   computes as a constant" -- P(all 10 >= 8) = 0.123
                (Harmonia found it 2026-09-14)
    2026-09-12  S5 run 1 INSTRUMENT_FAILURE: target_index in seed_inputs made G    36726e973
                a different policy per target of the same state
    2026-09-13  S7 "exact tie" was floating point; split a true five-way tie by    fd5248805 / ARCH-46
                2e-15
