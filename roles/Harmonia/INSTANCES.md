# Harmonia instances -- one seat, many concurrent instances

Currency: 2026-09-11 (Harmonia[m1-486e595f]). Inherits
roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md; this file adds
to them and may not contradict them. Helper: roles/Harmonia/instance.py
(selftest 9/9 at the commit that added it).

## Why this file exists

The operator's wake of 2026-09-11 ("there can be many instances of Harmonia
from a messaging, branch, commit, push, etc perspective; this needs to be
distinguishable in logs, comms, etc"). Measured at boot: three instances had
already written under the one name Harmonia on 2026-09-11 alone, and only the
Claude-Session commit trailer told them apart:

    session_015xemUgVDH2DmFqYARdV8Gi   M1  worktree harmonia-hygiene,
                                            branch harmonia/workspace-hygiene-2026-09-11,
                                            commits 42ca5030e .. 5a99e9627 (09-10 19:42 .. 09-11 05:38)
    session_01L96WUARbNnjNQgTXrxwX29   M2  packet 02 (29fc3ff4e, 09-11 06:36),
                                            "on M2 / SPECTREX5" in the packet header
    session_011b9Gdn4tBoFbuAMXSM2vrH   M1  this instance, tag m1-486e595f (below)

Every shared surface keys on the SEAT name only: comms.agents has one row
per seat (a second boot overwrites the first's worktree, branch and session),
comms.receipts and comms.task_queue are per seat (one instance's sync marks a
message seen for all of them; two instances can both `claim` the same item and
neither learns it lost), STATUS.md has one "where I am working" block, and
the journal is one file per date. So the tag below is mandatory on every
artifact an instance emits, and the comms gap is reported to Archaeon rather
than patched here (lane discipline; comms is base-role infrastructure).

## The tag (derived, never chosen)

    <machine>-<first 8 hex of CLAUDE_CODE_SESSION_ID>     e.g. m1-486e595f

    machine   m1 = SKULLPORT, m2 = SPECTREX5 (comms/environments.json);
              any other host -> its lowercased hostname
    session   the HARNESS session id the comms boot already records in
              comms.agents.session_id, so the tag is joinable to that row.
              The bridge id (session_011b9...) is a different id space; it
              stays in the Claude-Session trailer and is refused as a tag
              source so the two are never confused.

No session id means no tag: `instance.py` refuses rather than mint one that
could collide. Two sessions cannot share a tag; one session always regenerates
the same one.

## Where the tag goes (every one of these, every time)

    surface          form                                              why
    ---------------  ------------------------------------------------  ----------------------------
    worktree         F:/Prometheus-worktrees/harmonia-<tag>-<task>     one worktree per instance
                     (path is the operator's host convention)           per task, never shared
    branch           harmonia/<tag>-<task>-<date>                      `git branch -a | grep harmonia/`
                                                                       still finds every instance
    commit subject   Harmonia[<tag>]: <what changed>                   visible in --oneline
    commit trailer   Harmonia-Instance: <tag> (host, harness session)  plus the mandated
                                                                       Claude-Session trailer
    comms subject    Harmonia[<tag>]: <subject>                        sender stays "Harmonia" so
                                                                       routing and replies work
    comms body       first line "From: Harmonia[<tag>] ..."            the durable INBOX copy
                                                                       carries it too
    journal          roles/Harmonia/journal/<date>_<tag>.md            one file per instance per
                                                                       date; no merge conflicts
    STATUS.md        one block per live instance, headed by the tag    the seat-level facts stay
                                                                       above the blocks
    rulings/packets  "Author: Harmonia[<tag>]" in the header           a ruling names the instance
                                                                       that can be asked about it
    receipts         base_sha/branch/worktree_path already carry it    D-23 s4 unchanged
    comms boot       --capabilities as usual; the harness session id   the agents row is joinable
                     is captured automatically                         until comms is instance-aware

What does NOT change: the seat name in `python -m comms sync|boot|post
--from|--to` is `Harmonia`. The roster is roles/*; a tagged name is not a
recipient. Instances share the seat's queue and take it in order; before
claiming an item an instance reads the sibling instances' commits and
journals for that item (base boot step 3), because the queue cannot tell it
that a sibling is already on it.

## Registry (append your row at boot; leave it when you close, with the close time)

    tag           machine  harness session                        bridge session                     worktree / branch                                              opened            closed
    ------------  -------  -------------------------------------  ---------------------------------  ------------------------------------------------------------  ----------------  ------
    (untagged)    M1       unknown                                session_015xemUgVDH2DmFqYARdV8Gi   harmonia-hygiene / harmonia/workspace-hygiene-2026-09-11      2026-09-10 19:13  last commit 2026-09-11 05:38; worktree still present, clean
    (untagged)    M2       unknown                                session_01L96WUARbNnjNQgTXrxwX29   unknown from M1                                                2026-09-11        last commit 2026-09-11 06:36
    m1-486e595f   M1       486e595f-e8dd-4327-be91-de876aef42c8   session_011b9Gdn4tBoFbuAMXSM2vrH   harmonia-m1-486e595f-boot / harmonia/m1-486e595f-boot-2026-09-11  2026-09-11 15:17  open
    m2-54a6d694   M2       54a6d694-ea3e-4ec9-b06c-633b5dbbac7d   session_01NiqLgAgvtKZL7txRJoYXzZ   harmonia-a-boot-2026-09-14 / harmonia/m2-54a6d694-boot-2026-09-14  2026-09-14 06:20  open  (operator label "Harmonia A"; worktree path predates the tag and keeps "a-boot")
    m2-f541bed9   M2       f541bed9-2bbc-47c0-8e08-dbb9062252c9   session_01G7RAgrwhQkn4RRf2yn3sKE   harmonia-m2-f541bed9-boot / harmonia/m2-f541bed9-boot-2026-09-14  2026-09-14 06:37  open  (operator label "Harmonia B"; own row, superseding the placeholder m2-54a6d694 added from `comms who`)
    m2-038758c6   M2       038758c6-2210-4d29-8492-f1f69d463240   session_01APeC753MberhMK4TGqo6jD   harmonia-m2-038758c6-boot / harmonia/m2-038758c6-boot-2026-09-16  2026-09-16 15:50Z open
    gandalf-6cd1348b  M3     6cd1348b-4f8c-49eb-ba66-1856958ab195   session_01VNxXZa6NHHXB7E4oMoSKrP   harmonia-gandalf-6cd1348b-boot / harmonia/gandalf-6cd1348b-boot-2026-09-17  2026-09-17 15:18Z open  (operator label "Harmonia F"; first instance on M3 GANDALF; worktree root C:\prometheus-worktrees, host convention)
    m2-ca1148a0   M2       ca1148a0-0323-4295-aec2-2e71161e3142   session_01UvPiXdppxA2h2mk2YQTXFr   harmonia-m2-ca1148a0-boot / harmonia/m2-ca1148a0-boot-2026-09-17  2026-09-18 01:03Z open  (operator label "Harmonia B" -- the SAME label the operator gave m2-f541bed9 on 2026-09-14; labels are the operator's, tags are the identity; base_sha 80e0822ee; comms boot against the M1 canonical store, EW_DB_HOST=192.168.1.202)

The two untagged rows are reconstructed from commit trailers, not from
anything those instances declared; "unknown" is unknown, not zero.

## Lane ownership between instances (operator rulings, dated)

    2026-09-18  "Harmonia f owns asal" (chat, to Harmonia[m2-ca1148a0]): ASAL / HARM-50 is
                gandalf-6cd1348b's; with it, by the refinery directive's lanes, POET (HARM-47) and
                the Avida reconstruction ruler (HARM-48). Seat infrastructure (QR/AF/EX/FP/PR
                modules, registers, contracts) binds every instance and is not owned by one.
    2026-09-18  comms cannot carry an instance-to-instance message (inbox excludes the seat's own
                messages); ownership lines live HERE and in STATUS.md, read at boot.

## Known gaps, on whom

    comms.agents PK is the seat     one row; last boot wins             Archaeon (comms owner) --
                                                                         reported 2026-09-11 with a
                                                                         proposed additive fix
    comms.receipts / task_queue     per seat; a sync by one instance      same report
    keyed by seat                   hides the message from the others;
                                    `claim` cannot report that it lost
    STATUS.md                       one file; concurrent edits conflict   this file: per-instance
                                                                         blocks; conflicts stay
                                                                         resolvable by hand
