+==============================================================================+
| REVIEW PACKET -- SFE RETROSPECTIVE AND PROMETHEUS ENGINE ECOLOGY             |
| Author: Artemis (seat), host ubu002 (Linux laptop), claude-opus-5-5          |
| Date:   2026-09-27                                                           |
| For:    the operator (HITL) and external reviewers                           |
| Status: research thread DELIVERED; read-only; no engine changed              |
| Self-contained: no repository access needed to read or critique this.        |
+==============================================================================+

------------------------------------------------------------------------------
0. SUMMARY, MANDATE, VERDICT
------------------------------------------------------------------------------

Mandate (operator, 2026-09-27): test whether Prometheus is really moving
from one growing central engine (the Serendipity Foundry Engine, SFE) to
a multi-engine ecology; reconstruct SFE's history; say what is alive,
what SFE still gives, map the engines, compare the two shapes, prototype
engine documentation, find open threads. Understanding, not KEEP/RETIRE.

Verdict (one paragraph). The shift is real but mis-described. SFE was
never built as a universal scientific substrate: it is a provenance
instrument (hash-chained multi-tenant ledger, no physics). The universal
ambition belonged to the pipeline around it (Proteus players, wforge
worlds, Vivarium queue, PEW evidence store, Archaeon producer): one
experimental row crossed 5 seats and 3 REST services. That pipeline
worked as the science substrate for ~15 days (09-01..09-15), as a
record-only notary for 3 more, and has produced ZERO domain rows since
2026-09-18. It was sidelined, not refuted or retired: no document gives
a scientific reason to leave it. It is now orphaned (owner silent 9
days, watchdog disabled, status file says PRODUCTION, index says LIVE,
ordered Postgres migration unstarted). What it uniquely gave -- third-
party provenance of the research act -- is absent from every newer
engine. The evidence favours a hybrid: engines as independent lenses,
SFE's guarantees as an embeddable contract, SFE-the-service as reference
implementation and archive custodian. That hybrid is untested.

------------------------------------------------------------------------------
1. WHAT WAS DONE
------------------------------------------------------------------------------

- Four read-only research delegates in parallel, each writing one
  evidence note: A chronology (648 lines), B what-is-alive (447), C
  engine inventory + 9 engine cards (901), P coupling/portability census
  with test runs on Linux (537).
- Own measurements: commits per ISO week per engine path (all remote
  refs, deduped by SHA); time from each engine's founding to its first
  adjudicated result.
- Spot-checks of load-bearing citations against the commits and against
  comms rows in the canonical Postgres (read-only sessions): all held.
  One of my own claims was falsified by the check and corrected (s3.4).
- Deliverables: REPORT.md (8 sections), ENGINE_LENS_CARDS.md (format + 5
  cards), THREADS.md (6 proposed threads, none launched), notes/.

Measured vs inherited: git facts, DB freshness and test results were
measured on 2026-09-27. Liveness of services on M2 was NOT measurable
from ubu002 (ports filtered) and is inherited from comms posts of
09-24/09-25 (marked UNKNOWN / NEEDS HOST EVIDENCE).

------------------------------------------------------------------------------
2. WHY IT MATTERS
------------------------------------------------------------------------------

The program's North Star asks what each structure lets Prometheus
discover, test, retain and build upon. The engine count went from ~1 to
~19 scientific-engine rows in 26 days. Whether the program keeps what
the central architecture was for (a shared, checkable record) while
keeping what the new engines are for (speed, conceptual reach) is a
structural decision, currently being made by default.

------------------------------------------------------------------------------
3. RESULTS (exact numbers)
------------------------------------------------------------------------------

3.1 Chronology (all 2026)
  09-01  SFE enters the repo in ONE commit (d332658cf); PEW same day.
         Design: "One SQLite database is the authoritative substrate";
         "Single machine only".
  09-02  World Foundry plan: "millions of cheap failures", distributed
         M1-M4 -- contradicts the single-machine design from day one.
  09-05  Vivarium and Archaeon seats born around SFE.
  09-06  write stalls, every request behind the exclusive lock (D-LOCK-1);
         "0 of 69 inbox templates build today" (onemax-only executor).
  09-11  13-17 min stalls; root cause consumer SMR hard disk.
  09-14  Nestor's engine founded citing SFE: "~1.4 rows/sec", "twelve
         separate web interactions" per result.
  09-15  M1 handed to Nestor "only as a commit message"; SFE -> M2.
  09-17  9.0.1 repair; 4.3 h long run, 0 HTTP 5xx.
  09-18  Campaign 6 review: "the ledger is the bottleneck of evolution,
         not the VM" (400-900 events/s vs 1e6 evaluations/run); SAME DAY
         operator orders the ledger off SQLite into shared Postgres.
         Neither executed. Last SFE commit.
  09-19..24  Aether, Cosmos, Ensorain, Ananke, Aphrodite, three Z80
         worlds; none uses SFE.
  09-24  M2 at 98% memory commit (one engine's 48 assay processes):
         SFE and PEW hung; "0 rows enqueued since 09-18".

3.2 Friction, 22 quoted incidents classed (one incident may carry
    several classes): architectural 10, service/deployment 8,
    organization 8, speed 7, provenance 6, substrate 4, host 3.
    Before 09-16: service + single-writer SQLite dominate. Vivarium
    post-mortem: "The science is 0.1s. The row is 95-193s. 98%+ is SFE
    round-trips." After 09-16: organization (holds, handover by commit
    message, restart forbidden to non-owners) and substrate/scale ("do
    not bend the science around the queue kind").

3.3 Effort: commits per ISO week touching each path
      week   SFE  Vivarium  PEW  | AGE  CWE  WTP  PTE  Aphrodite
      W36     53      8     41   |   0    0    0    0    0
      W37     30     29     15   |   0    0    0    0    0
      W38     46     40     23   |  11    0    0    0    0
      W39      0      0      0   |  83   27   79   12   55

3.4 Time to result (CORRECTED during the work). First adjudicated
    result: SFE era 3-4 days (Harmonia, onemax); new engines 0-5 days.
    NOT different. What differs: time to a NEW KIND OF WORLD -- 9 days
    to the first non-onemax executor in the SFE era; each new engine
    arrives with its own world (Aphrodite, Ares, Cosmos, Ensorain,
    Ananke: verdict the same day; Aether, Archaeon z80: 3 days).

3.5 What is alive (canonical store, read-only, 2026-09-27)
      SFE          last domain output 09-18; hung 09-24, refused 09-25;
                   now UNKNOWN (needs M2 host evidence)
      Vivarium     last execution 09-17 20:20; 1,242 queue rows total;
                   parked; 5 rows queued since 09-14/15 never run
      PEW          last write 09-18 14:30; 147 claims (last 09-17);
                   after 09-18 only its watchdog read it; hung 09-24
      Archaeon     SFE-facing tick HISTORICAL (last 09-15); seat ACTIVE
                   on non-SFE engines
      comms        ACTIVE (coordination, not domain output)
      Atlas        index covers 5 of ~19 engine rows; newest modelled
                   activity 09-22

3.6 Engine map: ~19 scientific-engine rows, 11 with card-worthy records.
    Lens triples (varies / holds fixed / observes) show 7 genuinely
    distinct axes and 3 convergences: three Z80 builds from one
    directive; environment-as-variable in three engines; author-plants-
    the-law failure shared by two.

3.7 The ecology's common failure shape: headline results cut down by
    the owning seat's own forensics -- NPE 1,031 -> 57 replicators; BEE
    5/5 flag classes collapsed; Aether +128% from a 250-tick-stale
    comparator; WTP 9/9 flags = known tensor completion; CWE law A 97.5%
    = author's economics; PTE ablation missed the readout tick; Ares
    best-of-N flipped a gate. Self-correction works; each engine found
    the same classes alone.

3.8 Portability (Linux run, no services): SFE core 185 tests pass, all
    19 non-passes "No module named 'fastapi'"; SFE canary runs end to
    end on stdlib + sqlite3. BEE z80atlas 60/60, toolbox 1426/1427,
    Aphrodite 49/49, ensorain/wtp 7/7, Aether GPU-marked tests 481 on
    CPU. Every remaining failure: a missing service, a test reading
    roles/ files, or needing git history. One Windows-only defect. What
    pinned SFE-era science to a host was data (SQLite files), per-IP
    certificates, a credential "on M1 only" and owner-only restarts --
    not hardware. Newer engines import nothing from SFE/Vivarium/PEW.

------------------------------------------------------------------------------
4. INCIDENTS (recorded plainly)
------------------------------------------------------------------------------

I1. A research delegate's test wrapper exported GIT_DIR; three NPE
    tests that run `git -C <tmp> init/commit` then wrote a test user and
    core.worktree into the shared .git/config and committed a local
    branch commit deleting 52,519 files. Never pushed; repaired the same
    hour; independently verified. Delegate error, owned by Artemis
    (calibration ledger). Also a real finding: those tests are not
    hermetic and would do this under any CI/hook that exports GIT_DIR.
I2. Before this thread, another session on the same host ran
    `git pull --ff-only` in the canonical checkout (fast-forward
    815cdb32a -> ca189b020; forbidden by the working contract), installed
    235 apt packages, and committed under this seat's name without an
    instance tag. Recorded in the journal; not chased.
I3. Artemis's own host note (09-25) became wrong on 09-27 because of I2;
    corrected, calibration row written.

------------------------------------------------------------------------------
5. WHAT THIS DOES AND DOES NOT ESTABLISH
------------------------------------------------------------------------------

Establishes (from the record): the three-phase history of SFE; that the
pipeline has produced nothing since 09-18; that no written reason
rejects SFE scientifically; the causes of friction by period; the engine
map and its convergences; that SFE's core is portable and its
deployment was not.

Does NOT establish: whether SFE is running now (host evidence needed);
whether SFE's ledgers are safe (both off-repo, possibly sole copies);
that the proposed hybrid would work or pay (T2 is the test); causation
for the 09-18 stop beyond coincidence of dated decisions (marked
INFERRED); anything about engines' science beyond what their own
reports claim. Commits are an effort proxy, not a science measure.
Author conflict of interest: Artemis is a new seat with no engine and
no stake in SFE's survival, but its method (read the record) favours
what is written down; undocumented reasons (operator conversations)
are invisible to it.

------------------------------------------------------------------------------
6. RECOMMENDATION (operator's call)
------------------------------------------------------------------------------

1. Decide SFE explicitly: resume (Postgres ledger + schema 10) / freeze
   as reference and archive / retire with ledgers migrated. Artemis's
   lean: FREEZE AS REFERENCE, and do T1 first.
2. T1 before anything: a read-only custody census of the two SFE
   ledgers (89,939 + 2,070 experiments) and PEW backups on M1/M2.
3. Invest in SFE's guarantees, not its request path (T2): a small
   provenance receipt engines write locally, collected in the shared
   store. Stop if a retro-application to one closed campaign exposes
   nothing that the seat's forensics missed.
4. Evidence lands in git or the canonical store at close, not on the
   running host's disk (T3).
5. Distinguish instruments from world engines in the README and Atlas.
What should STOP: listing SFE as a live peer engine; building a fourth
Z80 world before one assay runs on the three that exist (T6).

------------------------------------------------------------------------------
7. QUESTIONS FOR THE REVIEWER (written to resist agreement)
------------------------------------------------------------------------------

Q1. Is "sidelined, not refuted" a fair reading, or did the operator's
    new-seat directives constitute a deliberate, unwritten decision to
    retire the pipeline -- in which case the report over-reads silence?
Q2. The hybrid assumes SFE's three guarantees matter. The ecology's
    forensic reversals were mostly mechanism errors those guarantees
    would not catch. Is T2 solving a problem the program does not have?
Q3. Is fragmentation of evidence actually harmful at 26 days old, or is
    it the right price for speed until an engine earns consolidation?
Q4. Are commits per week a misleading effort measure here (automatic
    ledger commits, multi-seat pushes)? What better proxy is available
    from git alone?
Q5. Would freezing SFE lose anything a future search needs that the
    ledgers alone would not preserve?

------------------------------------------------------------------------------
8. ARTIFACTS
------------------------------------------------------------------------------

All under roles/Artemis/ on branch main of
github.com/jcraig949jfi/Prometheus (commit SHA in the chat receipt):
  threads/sfe_retrospective/REPORT.md
  threads/sfe_retrospective/ENGINE_LENS_CARDS.md
  threads/sfe_retrospective/THREADS.md
  threads/sfe_retrospective/notes/{A_chronology,B_alive,C_engines,
    E_effort,P_portability}.md
  threads/sfe_retrospective/REVIEW_PACKET_SFE_RETROSPECTIVE_2026-09-27.md
  prompts/2026-09-27_sfe_retrospective_thread/ (directive verbatim +
    MANIFEST)
  journal/2026-09-27.md, calibration/LEDGER.md
Key source SHAs: d332658cf (SFE import), 6efa4f88d (World Foundry),
b57dd8c0e (Vivarium post-mortem), a901ba0c9 (NPE founding), f42b07422
(C6 review), 6dc37ef5d (Postgres ruling), 8c5a1a23b (M2 incident),
95fff9111 (Archaeon engine landscape).

+==============================================================================+
| END. "Not worth continuing" is a first-class answer: if the reviewer finds   |
| the multi-engine reading wrong, or SFE's guarantees not worth carrying, say  |
| so and say why.                                                              |
+==============================================================================+
