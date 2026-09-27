# SFE retrospective and the Prometheus engine ecology

Artemis (ubu002), 2026-09-27. Research thread assigned by the operator
the same day, verbatim at
roles/Artemis/prompts/2026-09-27_sfe_retrospective_thread/ (MANIFEST).
Read-only toward every engine, service and store. Pure ASCII.

Evidence base (all in this directory; every claim below is cited there
with path and short SHA):

- notes/A_chronology.md -- how SFE and its ecosystem evolved, 22 quoted
  friction incidents, 8 documented contradictions.
- notes/B_alive.md -- what is alive, from git plus read-only queries of
  the canonical store (schemas viv, ew, archaeon, comms, agora, atlas).
- notes/C_engines.md -- inventory of ~40 engines, runners and harnesses,
  12 Atlas-vs-git disagreements, 9 full engine cards.
- notes/P_portability.md -- import graph, host-pinning census, service
  dependencies, and stdlib smoke tests run on this Linux host.
- notes/E_effort.md -- commit effort per engine per ISO week, and time
  from founding to first result.
- ENGINE_LENS_CARDS.md -- the documentation format and five cards.
- THREADS.md -- open questions worth their own thread.

Base-role rule 2 applies throughout: a label is not a property. "SFE"
names at least two different things in the record (s1.4), Atlas calls
it a LIVE ENGINE, and its owner's status file says PRODUCTION; none of
those three labels survived measurement.

-----------------------------------------------------------------------

## 0. Summary

1. **The interpretation is supported, but the story isn't "one engine
   outgrown".** SFE was never designed to be a universal scientific
   substrate. It was built on 2026-09-01 as a provenance instrument, a
   hash-chained multi-tenant ledger with no physics. The universal
   ambition belonged to the ecosystem around it: the "Incubator".
   Proteus supplied players, Daedalus's wforge supplied worlds, Vivarium
   executed, PEW fossilized and Archaeon proposed. One experimental row
   crossed five seats and three REST services. That pipeline is what the
   program went around.
2. **The ecosystem's working life was about 17 days.** Science ran
   through SFE from 09-01 to 09-15. From 09-16 to 09-18 SFE only
   recorded results while the compute ran elsewhere. After 09-18 no
   campaign touched it, and the SFE, Vivarium and PEW pipeline has
   produced zero domain rows since. Effort moved in one week: 30-50
   commits a week each through ISO W38, then 0 in W39. In the same week
   the new engines took 12-83 commits each.
3. **The shift had several causes, and they changed over time.**
   - Before 09-16, service and deployment friction dominated: slow
     single-writer SQLite on SMR disks and permission-gated restarts.
     Vivarium measured "the science is 0.1s, the row is 95-193s".
   - After 09-16, organization and substrate dominated. A machine
     handover arrived "only as a commit message". Queue kinds could not
     express the next science: "do not bend the science around the queue
     kind". And evolution at 1e6 evaluations cannot write one ledger row
     per evaluation.
   - The biggest single driver was the operator founding new seats, each
     with a fresh directive and an engine of its own.
   - No document gives a scientific reason to leave SFE. It was sidelined
     rather than refuted or retired.
4. **What SFE still provides that nothing else does is provenance about
   the research act itself.** Three properties matter:
   - enforced prediction-before-observation;
   - selection families that keep the losers, so best-of-N is visible;
   - attestation that what ran is what was asked.

   No post-SFE engine has all three. CWE and BEE have parts, locally.
5. **Very little SFE code became general infrastructure; its lessons
   did.** The D-23 working contract grew from an SFE incident, when the
   live ledger and its TLS key were found in the canonical checkout
   (fe2eb85c9). So did the discipline of receipts, manifests and
   ordering. The canonical Postgres store that now hosts comms and Atlas
   was never SFE's; it predates SFE, and PEW made it canonical.
6. **The new ecology is faster where it matters most: a new kind of
   world.** Both shapes reached a first adjudicated result within days
   (3-4 days on SFE). But in the SFE era a new world had to become an
   executor kind that the engine and the queue admit: 9 days to the
   first non-onemax world, and "0 of 69 inbox templates build today".
   Each new engine arrived with its own world and reached a verdict in
   0-5 days. It pays for that speed in three ways:
   - fragmented provenance: Atlas indexes 5 of ~19 engines, 2-6 days
     behind;
   - evidence on off-repo C:\ paths, some of it possibly the only copy;
   - a shared host that starves: on 09-24 M2 hit 98% memory commit and
     hung SFE and PEW.

   The engines are independent in code but coupled through the machine.
7. **SFE is currently orphaned, not decided.** Its owner has been silent
   for 9 days. Its watchdog is disabled, its status file says
   PRODUCTION and Atlas says LIVE. The Postgres migration the operator
   ordered on 09-18 was never started. Its two ledgers (89,939
   experiments on M1 and 2,070 on M2) sit off-repo. Base-role rule 7
   ("dormancy must be visible") is currently violated by the program's
   original engine.
8. **Continued investment is warranted in SFE's guarantees, not its
   service.** The hybrid the evidence supports is SFE's provenance
   properties as a portable contract that each engine embeds locally and
   the shared store collects. SFE-the-service would stay as a reference
   implementation and archive custodian, not as a hub every experiment
   must pass through. That is a proposal for the operator, not a change.

-----------------------------------------------------------------------

## 1. SFE retrospective

### 1.1 What it was meant to become

Two intentions coexisted from the first week, and they were never
reconciled in writing.

- **The instrument.** The Gen-2 architecture (d332658cf, 09-01) is "the
  smallest system that satisfies the invariants. One SQLite database is
  the authoritative substrate". It deliberately excluded "distributed
  infrastructure" and any agent framework: "Intelligence (mutation,
  selection, interpretation) lives in drivers/executors, never in the
  runtime". Daedalus's charter says "The Engine is the instrument ...
  never let the Engine become the fitness landscape." Its lineage is the
  older D-13 Foundry (a GP/program-search service on M1:8799, outside
  this repo). Harmonia's D-14 packet describes it as "the single
  EXECUTION AND PROVENANCE AUTHORITY", with local substitutes
  "constitutionally forbidden" (4b3a25312).
- **The incubator.** One day later, the World Foundry v0 packet
  (6efa4f88d, 09-02) described "a machine for producing enormous numbers
  of small, semantically sterile, reproducible worlds ... finding one
  real bump in a flat landscape of millions of failures". Its plan was a
  "DISTRIBUTED M1-M4 EXECUTION PLAN" reusing "the engine's existing
  fabric". The Archaeon charter (36b40870c, 09-06) calls SFE "the
  petri-dish maker"; the 09-21 synthesis directive calls it an
  "open-ended foundry for generating, selecting, transferring and
  testing worlds".

The first intention is what Daedalus built. The second is what the
program expected. The collision was visible on day one: the engine's own
STATUS says "Single machine only (SQLite by design); no distributed
mode", while the Foundry plans distributed millions of runs. Scale is
where it finally broke (s1.3).

### 1.2 What was actually built and matured

Built and qualified in 17 days:

- the ledger through schemas v3 to v9;
- tenant isolation, audited before the first client (two cross-tenant
  breaks fixed);
- prediction ordering, selection families, attestation, lineage and
  cost events;
- a stdlib client;
- a restart rehearsal and a 4.3-hour long run with zero 5xx errors
  (release 9.0.1).

By any engineering standard in the repository this is the most
qualified service Prometheus has had. Around it, also built and
qualified:

- Vivarium: a Postgres queue plus a faithful executor, joint Track A
  receipt 29/29, declared "QUALIFIED_FOR_CAMPAIGN" on 09-17;
- PEW: canonical store, REST service, fossils, claims, evidence and
  campaign observations (32,938 rows);
- Archaeon's producer and tick.

Built but never finished:

- full replay (PARTIAL from day one; "REPLAY_COMPLETE: NO");
- executors beyond bitstring and NK (Herakles, 09-06: "0 of 69 inbox
  templates build today");
- the D-13 engine wrap ("Not built this pass");
- the distributed M1-M4 fabric;
- the Postgres ledger;
- Campaign 6's schema 10 ("nothing built").

### 1.3 How its role changed (the three phases)

| Phase | Dates | SFE's role | Evidence |
|---|---|---|---|
| Substrate | 09-01..09-15 | Execution and record for Harmonia's work and H0-H5 through the Vivarium queue. 579 completed, 492 cancelled, 79 failed queue rows by 09-16. M1 ledger 89,939 experiments, 86,296 from Vivarium. | A_chronology s5; C_engines D6 |
| Notary | 09-16..09-18 | Record of citation only. Compute ran in Archaeon's WSE harness (CMP1-3, Campaigns 4-5). "It is not a compute service; it is the thing that makes a claim CITABLE" (503fcf5b7). | A_chronology s5 |
| Parked | 09-18.. | Nothing enqueued since 09-18. Hung 09-24, refused 09-25. Owner silent. Migration ordered, not started. | B_alive s0, s2 |

The drop from notary to parked coincides on one day, 09-18, with two
decisions that each invalidated the other's premise:

- The Campaign 6 review found that the engine cannot be the
  per-evaluation store at evolutionary scale. It hits about 400-900
  ledger events a second single-process, and "the ledger is the
  bottleneck of evolution, not the VM". It specified schema 10.
- The operator ruled the ledger must leave SQLite for the shared
  Postgres, the day after 9.0.1 was qualified on SQLite: "I don't want
  us using SQLite for this very reason" (6dc37ef5d). Qualification gate
  G1 "does NOT transfer" to Postgres-over-LAN.

Neither was executed. From 09-19 the new engines absorbed the work
(A_chronology s7, "Why SFE activity stops"). The 09-15 M1 handover and
the 09-24 hang are not the cause. Production on M2 was healthy
09-16..09-24, and by then nothing was being sent to it.

### 1.4 Contradictions in the record

Eight are documented with both citations in A_chronology s8. These
matter most for the program:

- **C1/C2: "SFE" names two things.** One is the service, which "stores
  science and does not simulate". The other is the program of campaigns
  that ran through it (Cosmos design 01 states this plainly: "Two things
  share the name"). The README lists SFE as a peer world engine,
  "service: Daedalus, science: Archaeon" (4933204b5, 09-23). That label
  was written after Archaeon's science had left SFE. Atlas registers it
  kind=ENGINE.
- **C3: single machine vs distributed** (above).
- **C5: one canonical store vs machine independence.** PEW was
  deliberately not forked in the morning of 09-04 and deliberately
  forked by operator ruling that afternoon. The fork was reversed again
  on 09-17 and 09-18. The "M2 local Postgres fork" is PEW's store, not
  an SFE fork.
- **C6: who does SFE science.** Archaeon's charter says "not an
  executor"; the Campaign 1 directive says "the directive wins".

-----------------------------------------------------------------------

## 2. Current SFE value

### 2.1 Still valuable, scientifically or architecturally

- **Provenance of the research act.** No other engine has a third party
  that enforces all three of these:
  - a prediction was committed before its observation;
  - every member of a selection family is recorded, losers included, so
    declared n can be checked against distinct sources;
  - the executed configuration matches the requested one.

  Harmonia stated why it matters on 09-06: "any mechanism becomes
  invisible by being performed elsewhere" (a861d2873). The cross-engine
  pattern of forensic reversals (s3.3) shows the program still needs
  this discipline. The ordering checks would not have caught those
  particular mechanism errors, but best-of-N and config drift are among
  the reversal causes (Ares's best-of-N swap statistic; the BEE P1
  migration defect).
- **Multi-tenant isolation.** This is the only place in the program
  where several seats can write into one scientific record without
  seeing or corrupting each other's worlds.
- **The ledgers as an archive.** M1 eng_8a37a5d3 holds the H0-H5 corpus
  (89,939 experiments). Harmonia's HARM-13/16/18 and Archaeon's ARCH-47
  are blocked on reading it from M2. This is the program's largest
  single experimental record, and its preservation state is UNKNOWN.
- **An exemplar of qualification.** The release, restart, long-run and
  contract machinery (docs/point_release_2026-09/) is the most complete
  qualification record in the repository. It is reusable as a template
  even where the service is not.
- **A small known benchmark.** The NK-landscape executor (N 8-20).

### 2.2 Cumbersome, superseded, dormant or unclear

- **The REST-service-per-experiment model: CUMBERSOME, effectively
  SUPERSEDED.** "Twelve separate web interactions" per result (NPE
  founding directive) and 98% round-trip overhead. Every engine since
  09-19 is a local, deterministic, file-receipted Python package.
- **Single-writer SQLite on consumer disks: SUPERSEDED by operator
  ruling** (09-18) and not replaced.
- **The Vivarium queue in front of SFE: DORMANT.** It is qualified, but
  its kinds lag the science: "no admissible kind evaluates a program
  variant" (Campaign 4). Its last execution was 09-17 20:20, and it was
  parked with SFE unreachable.
- **PEW: DORMANT, and its service was hung as of 09-24.** Its last
  domain write was 09-18 14:30; after that its only reader was its
  watchdog.
- **The Archaeon producer and tick: HISTORICAL for this pathway.** The
  last autonomous tick was on 09-15. One row in archaeon.experiment_queue
  has been QUEUED since 09-05.
- **Daedalus's operational ownership: UNCLEAR.** The seat has not posted
  since 09-18 and did not answer comms #563 ("8811 is HUNG, and its
  supervisor is off").
- **Current liveness of SFE 8811 and PEW 8377 on M2: UNKNOWN, needs host
  evidence.** Both ports are filtered from ubu002. B_alive s10 lists the
  four checks on SPECTREX5 that would settle it.

### 2.3 What became general Prometheus infrastructure

Less than the architecture suggests, measured by imports (P_portability
s1c): its REST client (sfclient) is used by genesis (13 files), vivarium
(8) and archaeon (5); sfe.executors and sfe.ids by vivarium and
Bellerophon's toolbox backend; the SFE-era world foundry wforge by NPE
and the toolbox. sfe.api/runtime/store/release/attestation/canary have
no importer outside SFE, and no post-09-19 engine imports any of it.
What did generalize came from the SFE era rather than
from SFE:

- the D-23 worktree contract, whose trigger was the live SFE ledger and
  its TLS key sitting in the canonical checkout;
- rule-8/9/10 dormancy and liveness discipline, from Vivarium and Ergon
  incidents on this pipeline;
- MANIFEST receipts;
- prereg/freeze-before-rows;
- the qualification pattern.

The canonical Postgres store (prometheus_fire on M1) that now carries
comms and Atlas was never SFE's. It predates the SFE era (agora tables
from May) and PEW made it canonical.

These spread as patterns, not imports, which is also how the healthy
convergence among new engines spreads (ENGINE_LANDSCAPE s3).

-----------------------------------------------------------------------

## 3. Engine ecology

### 3.1 The best current map

The best starting list is Archaeon's ENGINE_LANDSCAPE (95fff9111, 09-25).
C_engines verified and corrected it:

- it missed Ares, Crius, Herakles EVCA, Alien Circuitry, Odysseus
  (ubu001), Proteus, wforge, Ludus and Archaeon WSE;
- its claim that CWE, WTP and PTE are unregistered in Atlas is stale.

Atlas registers 15 engine ids, and only 5 of them hold experiments.
Classified:

| Class | Members |
|---|---|
| Scientific engines, active or experimental | NPE Z80 lineage (Nestor, at rest), BEE z80atlas (Bellerophon, multi-day campaign running), Aether AGE, Cosmos CWE, Ensorain WTP, Ananke PTE, Aphrodite (improver-of-improvers, not a world), Odysseus (new, spiking circuit) |
| Scientific engines, dormant or closed | Archaeon z80atlas world, Ares (parked), Crius (closed 09-23), Proteus, wforge, Ludus, Herakles EVCA, Alien Circuitry, Incubation |
| Instrumentation | SFE, Archaeon causal lens, Atlas, Nyx, Techne, Herakles retrospective |
| Runners | Archaeon campaigns 1-6 and WSE, atlas_bee, Theophrastus |
| Orchestration | Vivarium, Archaeon producer, Archaeon frontier, Aether's RunPod GPU ladder |
| Qualification harnesses | Harmonia rulers, BEE toolbox (Worlds Kernel), Kairos, Charon, Genesis |
| Historical (pre-September lines) | Apollo, Arcanum, Forge, Ignis, zoo, sigma_kernel, Theseus, Ergon search, Koios, Harmonia TT |

Full table with seats, hosts, paths, dates and Atlas counts: C_engines
s1.

### 3.2 The distinct lenses

Written as varies / holds fixed / observes, the triple used on the lens
cards:

| Engine | Varies | Holds fixed | Observes |
|---|---|---|---|
| SFE | nothing | the order of the research act | the research act: predictions, families, attestations |
| NPE (Z80 gen.) | world permissiveness, encoding density | VM physics per campaign | the barrier sequence: variation -> acquisition -> establishment -> copying (P-11 causal-copy certificate) |
| BEE z80atlas | substrate features (LDIR, NOP slide), world topology, reward coupling | the VM | spontaneous own-code replication vs world-made copies (endogenous vs exogenous) |
| Archaeon lens | the environment | organism physics | four-identity genetic descent (who authored a birth) |
| AGE | physics laws | no organism boundary at all | persistence, propagation, twin light cones |
| CWE | the substrate (three worlds) | a small law grammar | laws that survive substrate change and sealed transfer |
| WTP | memory substrate x world physics | memory and FLOP budget | excess over a null ladder N0-N6 |
| PTE | communication physics | a GA over update programs | communication-dependent accuracy above an exact 0.500 |
| Ares | abstract world pressure (present/absent/shuffled) | substrate and search | which kind of memory machinery a dumb search finds |
| Crius | the accessibility rung | the reuse payoff | existence vs accessibility of reuse |
| Aphrodite | the improver | task families | whether an improvement process gets better at improving |

Genuinely distinct on their axis: AGE (no boundary), CWE (cross-world
invariants), WTP (memory against a null ladder), PTE (communication),
Aphrodite (improvement of improvement), Crius (accessibility) and SFE
(the only instrument of the research act). Convergent:

- **substrate:** three Z80 builds from one directive;
- **lens family:** environment-as-variable in Archaeon ENVGATE, Ares
  and PTE;
- **failure mode:** the author plants the law class, in CWE and WTP.

### 3.3 The pattern the ecology shares

In almost every engine the headline result was later reduced by the
seat's own forensics to an instrument or authoring artefact:

| Engine | Headline claim | After forensics |
|---|---|---|
| NPE | 1,031 spontaneous replicators | 57 |
| BEE | 72-hour flag classes | 5/5 collapsed |
| Aether | opcode change rate | +128% from a stale comparator |
| WTP-03 | 9 flags | 9/9 known tensor completion |
| CWE | law A | agrees 97.5% with the author's economics |
| PTE | C1 ablation | window missed the readout tick |
| Crius | invocation log | recorded R0 |
| Ares | gate C | best-of-N swap statistic flipped it |

The SFE era had the same shape: Campaign 1's positives died at n >= 10.
This is the ecology's most consistent finding, and it is to its credit:
the engines check themselves. It is also the strongest argument that
cross-engine instrumentation pays. Each engine rediscovered the same
failure classes alone: stale comparators, best-of-N, planted laws, and
windows that miss the event.

-----------------------------------------------------------------------

## 4. Architectural reading: one central engine vs many lenses

Measured against the thread's criteria, from the record only:

| Criterion | Shape 1: central SFE ecosystem (observed 09-01..09-18) | Shape 2: independent engines (observed 09-14..09-27) |
|---|---|---|
| Speed to a new world | Slow for new worlds, fast on the first one. First adjudicated result in 3-4 days (Harmonia on onemax); first non-onemax world 9 days (nk_landscape 09-10); "0 of 69 templates build today" (09-06). | Fast. Each engine arrives with its own world: verdict in 0-5 days (Aphrodite, Ares, Cosmos, Ensorain, Ananke the same day; Aether and Archaeon z80atlas 3 days; E_effort s2). |
| Alien concepts | Constrained. Any new world had to become an executor kind the queue admits. "Do not bend the science around the queue kind" was an operator correction. | Unconstrained. AGE drops organisms entirely; PTE drops neurons; Aphrodite is not a world. Clean-room is possible by decree (Aether D-1). |
| Provenance | Strong and third-party: ordering, families, attestation, tenant isolation, one queryable store. | Local and uneven: per-engine receipts, freezes and manifests; hash-committed predictions in CWE only. Atlas indexes 5 of ~19 engines, 2-6 days behind; no loser-keeping families anywhere. |
| Reproducibility | Ledger-level (chain integrity) but replay PARTIAL. | Often stronger at run level: BEE replay 606/606 and 341/341, AGE GPU-CPU bit-exact, PTE CPU oracle, CWE byte-identical reruns. Raw evidence often off-repo. |
| Portability | Core portable; deployment host-pinned (certs, launcher, off-repo ledger). Moved or re-hosted 4 times in 13 days. | Mostly "merely located": stdlib/numpy packages. The causal lens ran across three engines off-host. Inherent host needs only for NPE gen 1 (Redis/FalkorDB/CUDA/WSL) and AGE >= 16384^2. |
| Coupling between services | High: five seats and three services per row; the dead-man could not alert because comms lived on the store it was escalating. | Low in code; high through the host. Much of the active ecology runs on M2, and one engine's assay pool (ENVGATE-02) hung two others' services (09-24). |
| Ease of execution | Low: a restart needed the owner seat ("starting another seat's process is exactly what the ownership rules forbid"). | High: `python -m <engine>.launch` from a pinned worktree. |
| Scientific observability | Of the research act: high. Of mechanism: none (no dynamics in the engine). | Of mechanism: high and engine-specific. Of the research act: low. |
| Infrastructure burden | Concentrated: one qualified service, two watchdogs, backups, certs; owner silent, so the burden now sits unowned. | Distributed: each seat re-builds receipts, oracles, launchers and watchdogs. Cheap individually, duplicated collectively (three Z80 VMs). |
| Sharing discoveries | Through PEW claims and evidence (147 claims, last 09-17), a real shared record. | Through git reports and comms posts. Atlas covers a minority. Sharing happens by seats reading each other's commits (base role s1 step 3). |
| Conceptual homogeneity | High by construction: every world is an executor kind in one ledger schema. | Mixed: genuinely divergent lenses, but three convergent Z80 builds in one week and a shared planted-law failure. Divergence is imposed by decree (clean-room directives), not by the architecture. |

**Reading.** Neither shape wins on the record.

- **Shape 2's gain** is speed and conceptual reach. That is the North
  Star's "supply primitives, environments ... not a predetermined
  architecture" put into practice.
- **Shape 2's loss** is exactly what Shape 1 had: a third-party record
  of what was tried, predicted and discarded, in one place a later
  search can read. The North Star requires that "weak signals,
  gradients, useful residue and alternative lineages remain available to
  future search". In Shape 2 that residue is scattered across seat
  directories and C:\ paths, partly unindexed.
- **The history also refutes one tempting framing.** The central
  architecture did not fail because centralization is wrong. It failed
  on specifics:
  - a single-writer store on slow disks;
  - service ownership that forbade a restart;
  - queue kinds that had to be designed before science could use them;
  - a storage decision reversed without an executor.

  Each of those is separable from the idea of a shared record.

**The hybrid the evidence supports: engines as lenses, provenance as a
contract.**

- Engines stay independent, local and disposable, as they now are.
- What stays shared is a small set of provenance properties that SFE
  proved and the new engines lack: ordering, families, attestation and
  sealed predictions. They would be expressed as an embeddable receipt
  format, not a service in the request path, and collected into the
  shared store, where the operator already ruled the SFE ledger should
  live.
- The causal lens is the working prototype of the other half: an
  instrument that travels to engines through thin adapters.
- SFE-the-service becomes the reference implementation of that contract
  and the custodian of its two ledgers, not the hub.

This is a reading of the record, not a design, and it is untested (see
THREADS.md T2).

-----------------------------------------------------------------------

## 5. Engine documentation prototype

See ENGINE_LENS_CARDS.md: a ten-line markdown card and five real
examples (SFE, CWE, AGE, PTE, Archaeon causal lens). The format carries
only fields the history showed are load-bearing:

- the lens triple (varies / holds fixed / observes), which makes
  convergence visible;
- how it has lied, because the reversal pattern is the most reusable
  knowledge each engine has;
- consumer path, because evidence reachability is the ecology's weakest
  point;
- runs where, inherently vs merely located.

Building the cards showed that no large schema is warranted.

-----------------------------------------------------------------------

## 6. Portability

(See notes/P_portability.md for the census, scripts and test runs.)

The census (notes/P_portability.md) separates three kinds of host
affinity. The evidence says only the first is a real constraint.

**6.1 Inherently host-dependent: few, and all about hardware or
services.**

- NPE generation 1: CUDA via torch, cupy, numba and cuquantum, a Redis
  bus on 6390, FalkorDB, and 53 code files with `C:/Users/jcrai/lab/...`
  paths.
- AGE above about 16384^2: A40 GPU through RunPod.
- PTE's GPU path: torch CUDA, with a CPU oracle available.
- The Windows-scheduler layer the whole SFE-era stack relies on:
  - SFE's deploy watchdog;
  - Vivarium's dead-man and deliverer (`schtasks`);
  - most of MONITORS.md (53 rows: M1 35, M2 17, M4 10, M3 3).

  No monitor exists for a Linux host.

**6.2 Merely located: nearly everything else, including SFE.**

- SFE's core has no host pin beyond `--port default=8811`. All its
  pinning lives in deploy/: per-IP TLS certs minted with `make_cert.py
  --ip`, Windows launchers and watchdog, and an off-repo ledger path.
- On ubu002 (Linux, no services), SFE's own suite passed 185 tests. All
  19 non-passes were "No module named 'fastapi'". `python3 -m
  sfe.canary` ran the full in-process core end to end on stdlib and
  sqlite3.
- These ran unchanged: BEE z80atlas 60/60, toolbox 1426/1427 (the last
  needs a roles/ file), Archaeon z80atlas, ensorain/wtp, Aphrodite 49/49,
  and Aether's GPU-marked tests on CPU (481).
- Across every suite, once fastapi, Redis and Postgres are subtracted,
  each remaining failure has one of three causes:
  - a missing service;
  - a test reading a file under roles/;
  - a need for git history.
- Exactly one Windows-only defect turned up:
  vivarium/tests/test_workspace_invariant.py:146 treats "F:/..." as
  absolute.

**6.3 Coupled through shared services, not code.**

The newer engines import nothing from SFE, Vivarium, PEW or Archaeon.
The exceptions: NPE uses wforge, and Ensorain uses comms.manifest for
hashing. The old stack is coupled by REST (sfclient in genesis 13 files,
vivarium 8, archaeon 5) and by Postgres. Everything that remains shared
now runs through one Postgres cluster on M1: comms, Atlas, viv, ew and
archaeon. That was the operator's intent (the 09-16 topology ruling and
09-17 "everyone on M1"), and it works: this host reached it on 09-25
with nothing more than psycopg2 and EW_DB_HOST. It is also the program's single point
of shared state, and its backups have been UNKNOWN since 09-17 (B_alive
s4).

**6.4 What pinned the science.** Hardware pinned only NPE's first
generation. What actually pinned the SFE-era science to M1, and then
M2, was:

- **data:** SQLite ledgers on local disks, the "coupling that makes both
  sides unmovable" (35f32116e);
- **credentials:** Archaeon's read token "exists on M1 only";
- **per-IP certificates;**
- **operational ownership:** a restart needed the owning seat.

The SFE ledger was re-hosted four times in 13 days, and each move was a
multi-seat event. The operator's 09-18 ruling ("Postgres is there as a
shared database across machines so we don't have this problem of moving
data files around") names the fix and has not been executed.

The new engines avoided all of this by owning no service. They reproduce
the same risk in a quieter form, though: evidence left on the running
host's disk (T3).

**6.5 A hazard found by running the census.** primordial's git-using
tests are not hermetic. They run `git -C <tmp> init/commit` without
clearing an inherited GIT_DIR. On this host a census wrapper that
exported GIT_DIR let three of them write `core.worktree` and a test
user into the shared .git/config, and advance a local Artemis branch
with a commit deleting 52,519 files. It was never pushed, and it was
repaired and verified the same hour (P_portability s6). Any hook, CI
job or agent that exports GIT_DIR and runs those tests will do the same
to its repository. This is recorded as a finding for Nestor, and
Artemis's calibration ledger records the delegate error.

-----------------------------------------------------------------------

## 7. Open threads

Proposed in THREADS.md, none launched: T1 SFE disposition and archive
custody; T2 provenance as an embeddable contract; T3 where the ecology's
evidence actually lives; T4 host coupling and placement; T5 the
cross-engine failure catalogue; T6 the Z80 triplication as a planned
triangulation.

-----------------------------------------------------------------------

## 8. Program implications

These are for the operator to weigh. Artemis changes no engine.

1. **Decide SFE explicitly; don't leave it orphaned.** Today every label
   disagrees with the property: STATUS says PRODUCTION, Atlas says LIVE,
   the watchdog is disabled, the owner is silent and the ordered
   migration is unstarted. Any of these dispositions is coherent:
   - resume, with the Postgres ledger and schema 10;
   - freeze as a reference and archive;
   - retire, with its ledgers migrated.

   Silence is not. Rule 7 applies.
2. **Secure the two ledgers before anything else.** The M1 archive holds
   the H0-H5 corpus and is on SKULLPORT, which now belongs to Nestor.
   The M2 production ledger is on an M2 NVMe path. Neither is in git or
   the shared store. Neither should be a sole copy (T1).
3. **Keep SFE's guarantees as the investment, not its request path.**
   Invest in the provenance contract (T2) and the cross-engine
   instruments (the causal lens, a shared failure catalogue T5), not in
   making the service a hub again. SFE's best future role is reference
   implementation, archive custodian and qualification exemplar.
4. **Make evidence reachable by default.** A run's evidence should land
   in git or the canonical store at close, not on a C:\ path of the
   host that ran it. Atlas should harvest from a seat-authored export,
   the pattern Cosmos already uses, rather than one bespoke harvester
   per engine (T3).
5. **Place engines by need, not habit.** Most engines are merely located
   on M2. The 09-24 starvation shows the cost of co-location. Placement
   is a scheduling decision the program has not made (T4).
6. **Adopt lens cards in place of peer-listing engines.** The README and
   Atlas should distinguish world engines from instruments. SFE and the
   causal lens are instruments; listing them as peers of AGE or CWE
   hides what each is for.

**North Star check.** The question is what each structure lets
Prometheus discover, test, retain and build upon.

| | Shape 2 (independent engines) | Shape 1 (central SFE ecosystem) |
|---|---|---|
| Discover | better | worse |
| Test | about even: the engines self-falsify well, and SFE made selection visible | about even |
| Retain | worse: residue scattered | better: residue in one place |
| Build upon | weak: little crosses engines except patterns and one lens | also weak: its world vocabulary was too narrow to build on |

The program's next gain is in retention and building upon, not in a
tenth engine.
