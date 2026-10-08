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
    2026-10-07  M2 boot       ran the Phase 2-B Beta assays B03..B13 on M2        Directive 2026-10-06 says heavy shared compute uses the Fabric lease  archaeon/beta/JOURNAL.md
                (P2B SFE)     with 15-26 worker processes from ~00:00Z to         authority; MWO-0004 R2 sets <= 16 core-h per item and <= 48 per seat  (2026-10-07 04:1xZ entry)
                              04:1xZ WITHOUT a Fabric lease, beside other          per 24 h. Rough count ~90+ core-h in ~4 h, unleased, on the shared
                              seats' work                                          host (another session's 4-proc job started 03:58Z and was being
                                                                                   crowded; my B13 workers were CPU-starved). Noticed only when B13
                                                                                   ran slow. Repair: lease spectrex5:cpu12 lse-bda13648061d taken for
                                                                                   the in-flight B13 (20 procs, over the 12 convention, disclosed in the
                                                                                   lease purpose); B12 long run STOPPED (partial result kept); every
                                                                                   later Beta launch <= 12 procs under that lease, and the 48 core-h/24 h
                                                                                   envelope is now the binding budget for the rest of this window.
    2026-10-08  M2 (P2B SFE)  reported composed-world competence and an evolved      B25/B26/B27/B28/B30/B31 scored elites with evaluate_world(seed,E=8):   archaeon/beta/JOURNAL.md
                              "evidence integration" headline from E=8 episodes     the SAME 8 episodes they trained on. B44 scored every elite on ONE     (B45, B46 entries)
                              of one world seed                                     shared 8-episode held-out sample. Cost: B44's "7/8 integrate
                                                                                    evidence" RETRACTED (0/8 at E=64x4); C6-unable content sensing and
                                                                                    the open-loop "beats constant" claim RETRACTED; magnitudes fell
                                                                                    (.48 -> .20). Core claims survived the re-score. Rule now: held-out
                                                                                    = new episodes, >= 64 x >= 4 world seeds, never the training sample.

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
