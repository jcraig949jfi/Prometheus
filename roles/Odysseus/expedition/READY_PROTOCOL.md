# READY is an empirical status (directive s13)

Currency: 2026-09-28. Odysseus. Pure ASCII.

A packet (anything handed to a worker: frontier/poi/ready/R*.md, an
expedition design, a chop) moves through:

    DRAFT            written by its author
    SEARCHED         a repo-wide prior-work search was run and its log is
                     committed beside the packet
                     (expedition/prior_work_search.sh REPO OUT terms...;
                     greps origin/main + branch-unique files of every
                     remote ref + all commit messages; ~1 min per term)
    COLD-START-TRIED a worker who did NOT draft it ran it with no oral
                     context and wrote PACKET_GAPS.md
    READY            the cold-start worker (a) found every required input,
                     (b) identified the important prior experiments, (c)
                     stated what is frozen and what may change, (d)
                     reproduced the known-answer fixture, (e) stated the
                     falsifier, (f) produced the specified artifacts --
                     and no gap in PACKET_GAPS.md is BLOCKING
    STALE            READY, but the prior-work search is older than 30
                     days or the packet's inputs moved

Every packet carries a known-answer fixture (a small input whose correct
output is written down) so (d) is checkable.

## Ledger of cold-start trials (failure rate tracked, not hidden)

    packet  date        worker          outcome   blocking gaps  notes
    R4      2026-09-27  fresh subagent  NOT READY  2 (prior runs C4-05 / C3-SFE-02 uncited;
                                                     "known summit" did not exist)  12 gaps total
    (rows added per trial)

Current states: R4 COLD-START-TRIED (not READY); R1, R2, R3, R5, R6 DRAFT.
The pass-1 label "READY" on them is withdrawn.
