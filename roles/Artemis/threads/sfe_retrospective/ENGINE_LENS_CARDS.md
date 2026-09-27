# Engine lens cards -- a minimal format, prototyped on five engines

Artemis, 2026-09-27. Deliverable s5 of the SFE retrospective thread
(REPORT.md). Evidence behind every card: notes/C_engines.md (full cards
with SHAs), notes/A_chronology.md, notes/B_alive.md. Pure ASCII.

## Why this format and not a software inventory

The thread asks one question of every engine: what unique lens does it
afford Prometheus, and when should we use it? Four things the history
showed decide what a card must carry, and nothing else earned a field:

1. LENS AS A TRIPLE (varies / holds fixed / observes). Two engines with
   the same triple are the same lens, whatever their code looks like.
   Three independent Z80 worlds were built from one directive in one
   week (Nestor, Bellerophon, Archaeon; ENGINE_LANDSCAPE 95fff9111) and
   nobody could tell from their docs that they overlapped. The triple
   makes that visible at a glance. (It is Archaeon's proposed
   varied=/observed= field, ENGINE_LANDSCAPE s4, plus "holds fixed",
   which is what distinguishes Archaeon's ENVGATE from BEE on the same
   kind of world.)
2. HOW IT HAS LIED. Almost every engine's headline result was later cut
   down by its own forensics (NPE 1,031 -> 57 replicators; BEE 5/5 flag
   classes collapsed; Aether +128% from a stale comparator; WTP 9/9 flags
   = known tensor completion; CWE law A = the author's own economics; PTE
   ablation missed the readout tick). The recorded failure modes are the
   most reusable thing an engine owns, and the first thing a new user
   needs. A card without them invites the same mistake twice.
3. WHAT A CONSUMER CAN READ. The charter's first commitment is
   "experience must have a consumer". After 2026-09-18 most evidence
   landed in seat-local files and off-repo C:\ directories, and Atlas
   indexes 5 of about 19 engine rows. A card states where the evidence
   lives and whether anything else can read it.
4. RUNS WHERE, INHERENTLY OR MERELY. SFE's code is portable; its
   deployment pinned it (per-IP certs, Windows launcher, off-repo
   ledger). Most new engines are "merely located". The card separates the
   two, because only the first is a real constraint.

Everything else (LOC, module lists, APIs) lives in the engine's own
README and is deliberately left out.

## The format (copy this block)

    ## <Name> -- <one-line lens>
    Owner / host / status: <seat>; <host, INHERENT|LOCATED>; <ACTIVE|
      EXPERIMENTAL|DORMANT|HISTORICAL|UNCLEAR> as of <date> (<evidence>)
    Lens: varies <X>; holds fixed <Y>; observes <Z>.
    Use it when: <the experiment classes it fits>
    Don't use it when: <what its representation hides or distorts>
    Trust instrument: <the control/certificate that makes its signature
      observable honest>
    How it has lied: <recorded failure modes, each with the evidence>
    What it has taught Prometheus: <= 3 findings, each with its verdict
    Consumer path: <where its evidence lives; git / store / off-repo;
      Atlas-indexed?; who reads it>
    Nearest lenses: <which engines share part of the triple; what to
      borrow; what to give>

Ten lines on purpose. If a field cannot be filled from evidence, write
UNKNOWN; do not fill it from the engine's aspirations.

-----------------------------------------------------------------------

## SFE -- the provenance instrument of the Incubator era

Owner / host / status: Daedalus (silent in comms since 2026-09-18); M2
  SPECTREX5, LOCATED (core stdlib + FastAPI + SQLite; host-bound only by
  deployment: per-IP TLS certs, Windows launcher and watchdog, off-repo
  ledger C:\Prometheus-data\sfe); DORMANT, liveness UNKNOWN -- last domain
  output 2026-09-18, port hung 09-24 and refused 09-25 (comms #563 #573
  #586); roles/Daedalus/STATUS.md still says "PRODUCTION".
Lens: varies nothing -- "the instrument serves the experiment; it never
  shapes it"; holds fixed the ORDER of the research act (prediction
  before observation, requested vs executed config); observes the
  research act itself: hash-chained per-world events, selection
  families including the losers, attestations, lineage, costs.
Use it when: a claim's credibility depends on proving what was predicted
  before it was seen, how many were tried before one was reported, and
  that what ran is what was asked; several seats write into one record
  and must not see or corrupt each other's worlds.
Don't use it when: the science is in the dynamics -- organisms never
  interact inside SFE; a WORLD is a tenant partition of ledger rows, not
  a simulated space; built-in genomes are bitstring/NK toys. Nor at
  evolution scale: a single-writer SQLite ledger tops out near 400-900
  events/s, and the Campaign 6 review found "the ledger is the
  bottleneck of evolution, not the VM" (f42b07422).
Trust instrument: its own -- prediction ordering by committed_seq,
  FAMILY_EXTENT_DIVERGENCE (declared n vs distinct recorded sources),
  executed_config attestation; restart rehearsal k1/k2; G1 long run
  15,408 s with 0 5xx (e7a699099).
How it has lied: the ledger went silent exactly when the engine broke
  ("the hash chain is silent precisely when the engine is the thing
  that broke", 8e4fc377a) -- a 13-row gap that would read as a property
  of rule space; D-LOCK-1 made "WAL for concurrent readers" false in
  practice (e307d6e5f); a healthy old build was indistinguishable from a
  healthy new one (aa1aa74a3); replay was PARTIAL from day one and never
  completed; its own status file is stale by 9 days, and Atlas still
  says LIVE.
What it has taught Prometheus: (1) what it recorded -- Campaign 1
  transfer positives died at n >= 10 under common random numbers, 0 of
  10 supported (4d80d4b1d); (2) mutational damage in the Proteus VM is a
  cliff, 0/5,472 single edits improved a parent (8f1a82ced); (3) about
  itself -- 98%+ of an experiment row's time was SFE round-trips, science
  0.1 s vs row 95-193 s (b57dd8c0e).
Consumer path: two SQLite ledgers off-repo -- M1 eng_8a37a5d3 (89,939
  experiments, archived on SKULLPORT, the H0-H5 corpus) and M2
  eng_906356f7 (2,070 experiments); both may be sole copies (UNKNOWN).
  PEW fossils and claims in the canonical store (ew, last write
  2026-09-18). Atlas reads the ledgers' extracts but models only 57
  Archaeon campaign slots, filed under sfe.
Nearest lenses: none share its triple -- no other engine records the
  research act as a third party. CWE's hash-receipted sealed
  predictions and BEE's replay receipts cover parts of it locally. Give:
  loser-keeping families, prediction ordering, config attestation, the
  science-profile "off" arm. Borrow: BEE-grade replay (606/606) to close
  PARTIAL replay; a shared store (operator 09-18 Postgres ruling).

## CWE (Cosmos) -- change almost everything, keep what refuses to change

Owner / host / status: Cosmos; M2, LOCATED (numpy; self-contained
  `python -m prometheus.cosmos.runtest`); EXPERIMENTAL, C3 waiting on the
  operator; seal commit a56ef7787 not yet on main; STATUS.md stale
  (currency 09-25).
Lens: varies the substrate (three independently written worlds: register
  VM, delay ring, block CA) and holds fixed a small law grammar (size
  <= 6, conjunctions); observes normalized phase-boundary laws that hold
  across substrates and transfer to CSPRNG-sealed holdout worlds.
Use it when: a claimed regularity should be tested for substrate
  independence; a law needs to be killed rather than confirmed; a
  prediction has to be committed before the answer exists.
Don't use it when: the interesting variable is not a declared coordinate
  -- the substrate author declares the coordinates and can "smuggle the
  answer"; the phenomenon is not a low-complexity boundary.
Trust instrument: sealed holdouts with hash-receipted predictions;
  permutation null over the whole search; per-family location gate;
  planted-truth recovery 7/7.
How it has lied: recovered law A agrees 97.5% with the hand-written task
  economics -- rediscovery, not discovery; G6 intervention 0/12 was an
  engine one-flip defect (retest 12/12, 5b84b66e0); active search did no
  better than random (.790 vs .788); one author wrote every substrate,
  including the sealed ones.
What it has taught Prometheus: (1) C0b law A held on sealed D/E/F (BA
  .983/.972/.930 vs 5-NN .77-.84); (2) the location gate killed three
  laws that pooled residuals had passed (e51fc75ae); (3) author-separated
  holdouts are needed -- hence holdout D sealed by Nestor.
Consumer path: git (roles/Cosmos, prometheus/cosmos); runs under
  C:/Users/James/cosmos_runs (off-repo); the ONLY engine that emits an
  Atlas-shaped export itself (atlas_export_c0), 10 Atlas experiments.
Nearest lenses: WTP shares the author-plants-the-law failure mode -- give
  WTP foreign holdouts and the location gate, borrow WTP's post-data tuned
  same-class null (N6). Borrowed SELECTIVE_PAYS from Archaeon WSE as a
  concept, not an import.

## AGE (Aether) -- executable matter with no organism boundary

Owner / host / status: Aether; BUCKKEEP + RunPod A40; LOCATED for science
  at 128-512^2 (NumPy CPU oracle; 256^2 validated as a proxy for 2048^2
  within 0.1-2.9%), INHERENTLY GPU-bound only at >= 16384^2; ACTIVE
  (AETH-03 research block 2026-09-27, mostly on unmerged branches).
Lens: varies the physics law of a 2-D torus of executable sites (five
  uint8 fields each); holds fixed the absence of any organism, birth
  primitive or genome identity; observes persistence, propagation,
  circuitry and energy flow -- and whether anything organism-like
  appears without being defined.
Use it when: the question is whether structure can arise with NO
  predefined assembly boundary; light-cone / twin-difference tests of how
  a one-bit difference travels.
Don't use it when: the question needs heredity, selection or identity --
  none has appeared; addressing artefacts (arg1 mod 5) dominate
  single-bit perturbations.
Trust instrument: GPU kernel bit-exact against a CPU oracle (300/300,
  400/400, 464/464); forked twins with lesion and sham arms; certified
  world death; hard dollar caps with a reaper.
How it has lied: the runner compared each sample to a state 250 ticks
  old, inflating opcode change rate by +128%; one validation claim
  withdrawn; the original null lacked source starvation.
What it has taught Prometheus: (1) FIRST_LIGHT, six 4096^2 worlds, $2.02:
  no phenomenon on the evidentiary ladder (f1f6dd637); (2) 89% of edge
  terminations are source starvation -- "the substrate lacks
  propagation" (43202cf7b); (3) of four one-change laws only one
  propagates a difference, weakly, by activation timing rather than
  content (PHYSICS_DESIGN_02).
Consumer path: git, mostly on aether/* branches not yet merged; RunPod
  outputs pulled back per receipt; NOT in Atlas.
Nearest lenses: none on the no-boundary axis (declared clean-room, D-1).
  Its RunPod ladder is becoming shared GPU infrastructure -- it already
  runs Ananke's conformance suite as a foreign module (6c98b4dae). Give:
  the twin/light-cone assay and the leak-free pod discipline.

## PTE (Ananke) -- communication physics without neural machinery

Owner / host / status: Ananke; M1 (CUDA), LOCATED (int32 + counter-hash
  RNG make runs bit-exact on any GPU; CPU oracle for small configs);
  EXPERIMENTAL -- C1 and C1b done, C2 not run; STATUS.md stale (09-25).
Lens: varies the physics of communication (loss, latency, decay, cap,
  topology, fanout); holds fixed a 16-opcode straight-line update program
  per site found by a declared GA; observes whether held-out accuracy
  above an exact 0.500 baseline depends causally on packet traffic.
Use it when: the question is which channel conditions make
  communication-dependent computation possible, and which carrier
  (state, inbox, in-flight packets) holds the information.
Don't use it when: messages need addresses or symbols (arrivals are
  summed, source identity lost); the computation is non-linear (XOR/FLIP
  null); you need to separate GP search strength from substrate capacity.
Trust instrument: mirror-paired worlds so a constant policy scores 0.500
  exactly; per-carrier resets with in-flight flush; CPU-oracle
  conformance (145 tests).
How it has lied: the C1 packet-ablation window missed the readout tick
  (C1_ERRATA.md) -- a lesson for every perturbation assay; mechanism
  labels stay _UNRESOLVED where the positive control could not fire.
What it has taught Prometheus: (1) routed-relay laws are
  COMM_DEPENDENT + CAUSAL_SUPPORT + REPRODUCED at 0.875-0.893 up to
  N=2304, but rare (8/352) and topology-tied (random graph 0.500); (2)
  cross-family transfer 0; (3) C1b: the carrier is transport arriving on
  the readout tick; in-flight memory reproduced 3/3.
Consumer path: git (roles/Ananke/pte); Atlas-registered with 0
  experiments (no harvester; registry code_path points at roles/Ananke).
Nearest lenses: environment-as-variable family with Archaeon ENVGATE and
  Ares present/absent/shuffled; Archaeon's causal lens already runs on
  PTE through an adapter (PORTABILITY01_REPORT.md:158).

## Archaeon causal lens -- who actually authored a birth

Owner / host / status: Archaeon; M2, and demonstrated portable (the lens
  ran unchanged through adapters on BEE z80atlas, NPE and PTE); ACTIVE
  (contract v0.3, 2026-09-27). Its own Z80 world is the third Z80 build
  and is DORMANT.
Lens: varies the environment (input-window block/rescue, inflow,
  topology); holds fixed the organism physics; observes genetic descent
  with four identities per birth -- executor, executed material, child
  contributors, ecological host -- by byte-level taint.
Use it when: any replication or lineage claim, on any engine that
  persists enough provenance to taint -- it separates an organism
  copying itself from a host executing inert material.
Don't use it when: the engine does not persist per-birth provenance (BEE
  abstains on about a third of births); recombination is symmetric
  (majority-provenance continuity is ill-posed, break B1); the question
  is origination rather than amplification.
Trust instrument: paired arms with shams on shared tape streams;
  byte-identical legacy replay admission; declared breaks B1-B7 in the
  contract.
How it has lied: an ENVGATE-01 host-label artefact, found by this very
  lens; parent-chain tracing credits the host (8-42x more
  "establishments" than genetic tracing).
What it has taught Prometheus: (1) host-mediated reproduction -- 26 of 63
  inert hosts gave births, all by foreign execution; (2) ENVGATE-02
  WINDOW_NOT_SUPPORTED (c5ba19571); (3) PORTABILITY-01: portable with
  domain limits across three engines.
Consumer path: git for reports and contracts; run evidence under
  C:\Prometheus-data on M2, off-machine copy BLOCKED (ENVGATE01 s1); NOT
  in Atlas (the harvester regex matches only archaeon/campaign\d+/).
Nearest lenses: NPE's P-11 causal-copy certificate and Crius's
  existence-vs-accessibility lens answer neighbouring questions. It is the
  only instrument in the program already running across engines, which
  makes it the working prototype of cross-engine instrumentation.

-----------------------------------------------------------------------

## What prototyping the format showed

- Every card could be filled from the repository alone, but every
  "Consumer path" field needed host knowledge that only a seat's STATUS
  or a comms message held. That field is where the program is weakest.
- "How it has lied" was the easiest field to fill with evidence and the
  most useful to read. The engines document their own failures well;
  nothing collects them across engines.
- SFE is the only card whose lens triple varies nothing. It belongs in
  the same register as an instrument, like the causal lens -- not as a
  peer world engine. The README's peer listing (4933204b5) and Atlas's
  kind=ENGINE both blur this.
- No large schema is warranted. If Atlas wants machine-readable fields,
  the triple (varies / holds fixed / observes), status-with-date and the
  consumer path are the only ones the evidence justifies.
