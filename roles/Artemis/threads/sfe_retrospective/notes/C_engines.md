# Spike C -- Engine ecology inventory

Author: Artemis research assistant (read-only spike). Date: 2026-09-27.
Thread: roles/Artemis/threads/sfe_retrospective. Nothing was run, changed,
committed or pushed; Postgres read with set_session(readonly=True), SELECT only.

Sources and method
- Repo: worktree artemis-base-role at origin/main f287a4fdb (2026-09-27
  15:05Z) plus 61 origin/* seat branches. Commit dates below are
  `git log --remotes` (main + every seat branch) on the path, committer
  date, format "YYYY-MM-DD sha". A path's first date can precede its
  arrival on main (e.g. primordial/ first a901ba0c9 2026-09-14 on nestor
  branches, first-parent on main only f423a09ac 2026-09-25).
- Atlas: prometheus_fire @192.168.1.202, schema atlas, tables engine,
  experiment, campaign, engine_instance, harvest_run, git_commit, view
  v_coverage; atlas/registry.json (last edit 7190591f4 2026-09-26);
  roles/Atlas/STATUS.md (currency 2026-09-25, repair note 2026-09-26).
- Starting point: roles/Archaeon/ENGINE_LANDSCAPE_2026-09-25.md
  (95fff9111), treated as a claim to verify.
- Seat docs: roles/<Seat>/{CHARTER,RESPONSIBILITIES,STATUS}.md and reports
  cited per row/card.

Class definitions used
- SCIENTIFIC ENGINE: owns a world / organism / computation representation
  whose dynamics generate the data.
- RUNNER: drives experiments on someone else's engine or world.
- ORCHESTRATION: queue, scheduler, data plane, service fabric.
- QUALIFICATION HARNESS: rulers, audits, conformance, adversarial review.
- INSTRUMENTATION: ledger, index, measurement or analysis tool.
- HISTORICAL SYSTEM: pre-September-2026 lines (math, LLM evolution) or
  closed and retired.

## 1. Inventory table

Hosts: M1 = SKULLPORT 192.168.1.202; M2 = SPECTREX5 192.168.1.191; M3 =
GANDALF; M4 = "harry1" (Aphrodite); BUCKKEEP = Aether's workstation;
ubu001 = Ubuntu laptop 192.168.1.218 (atlas/registry.json hosts; seat
STATUS files). Atlas column: registry engine_id / experiments in
atlas.experiment (query 2026-09-27). "n" = not registered.

### 1a. September-2026 ALife / engine ecology

| Name | Seat | Host | Path | First commit | Last commit | Class | Atlas? (exps) |
|---|---|---|---|---|---|---|---|
| SFE Serendipity Foundry Engine | Daedalus | M2 (M1 retired 09-11) | SerendipityFoundry/SerendipityFoundryEngine (+Client) | 2026-09-01 d332658cf | 2026-09-18 9cfcd3779 | INSTRUMENTATION (ledger engine; hub of the Incubator ecology) -- ENGINE per Atlas | y sfe (57, all driven by Archaeon) |
| wforge World Foundry v0 | Daedalus (author of packet) | M2 | SerendipityFoundry/worldfoundry/wforge | 2026-09-02 6efa4f88d | 2026-09-02 85c74304c | SCIENTIFIC ENGINE (world generator; genome->world grammar) | n |
| Proteus Player Foundry | Proteus | M2 | proteus/ | 2026-09-02 20a523289 | 2026-09-18 6a98ef0bb | SCIENTIFIC ENGINE (organism representation: 25-op player VM) | y proteus (0) |
| Ludus World Foundry + arena/bench | Ludus | M2 | ludus/ | 2026-09-01 e85bfa6b9 | 2026-09-16 fb858dd5c | SCIENTIFIC ENGINE (world catalogue/bench) -- HARNESS per Atlas | y ludus (0) |
| Vivarium viv data plane | Vivarium | M2 (queue on M1 PG) | vivarium/viv | 2026-09-05 8b940a165 | 2026-09-17 1023f81bd (roles/Vivarium to 2026-09-24 8c5a1a23b) | ORCHESTRATION -- RUNNER per Atlas | y vivarium (1,242; 1,178 driven by archaeon) |
| Archaeon campaign1-6 | Archaeon | M2 | archaeon/campaign{1..6} | 2026-09-16 3a34d207a | 2026-09-19 9471a5771 | RUNNER (on SFE + proteus.foundry) | y archaeon.campaign (0; its 54 exps filed under sfe) |
| Archaeon WSE workspace ecology | Archaeon | M2 | archaeon/wse | 2026-09-16 cd68cea96 | 2026-09-17 cb9135104 | SCIENTIFIC ENGINE (worlds on proteus.foundry) / RUNNER | n (4 exps filed under sfe as archaeon.wse/*) |
| Archaeon DEEP FRONTIER | Archaeon | M2 | archaeon/frontier | 2026-09-18 87bd51813 | 2026-09-26 1049aac73 | ORCHESTRATION (lineage scheduler on SFE client) | y archaeon.frontier (422) |
| Archaeon producer | Archaeon | M2 | archaeon/producer | 2026-09-06 4bcf72dc9 | 2026-09-17 7017dc79e | ORCHESTRATION (PEW->queue->Viv->SFE loop) | n |
| Theophrastus | Theophrastus | UNKNOWN (runs on M2-only SFE+PEW stack) | theophrastus/, roles/Theophrastus | 2026-09-13 fcbbdd2da | 2026-09-16 feab5d00e | RUNNER / analysis lens ("owns ... no engine", theophrastus/__init__.py) | n (67 exps in M1 SFE ledger as client "theophrastus") |
| Harmonia rulers/qualification | Harmonia | M2 + M3 | roles/Harmonia/{science,qualification} | 2026-09-05 e90609151 | 2026-09-19 68713424d (seat to 2026-09-27 c17d4c477) | QUALIFICATION HARNESS | y harmonia.rulers (0) |
| Genesis Harmonia A/B/C | Harmonia A/B/C | M2 | genesis/ | 2026-08-31 7ca9063f7 | 2026-09-05 f2e3148e3 | QUALIFICATION HARNESS (borderline historical) | n |
| Herakles EVCA / ca_stream | Herakles | M2 | herakles/evca, herakles/ca_stream | 2026-09-08 3466481b9 | 2026-09-16 6c9c55bfb | SCIENTIFIC ENGINE (CA executor library, kind ca_density_v0 for Vivarium) | y herakles.evca (0) |
| Herakles retrospective instrument | Herakles | M2 | herakles/ (rest), roles/Herakles | 2026-09-03 815053e2e | 2026-09-17 a8258db99 | INSTRUMENTATION | n |
| Alien Circuitry AC-01 | none found | UNKNOWN (M2 inferred from text) | alien_circuitry/ | 2026-09-12 898338725 | 2026-09-14 93cdb3392 | SCIENTIFIC ENGINE (small, dormant) | n |
| NPE Nestor Primordial Engine | Nestor | M1 | primordial/, roles/Nestor/campaigns | 2026-09-14 a901ba0c9 | code 2026-09-17 f75e8ad54; seat 2026-09-26 d63b76a5f | SCIENTIFIC ENGINE | y npe (276: cw01 118, graphworld r1-r8 158; z80atlas campaigns 0) |
| BEE Worlds Kernel (toolbox) | Bellerophon | M2 | prometheus/toolbox | 2026-09-18 4c0435544 | 2026-09-19 97109bd95 | QUALIFICATION HARNESS / RUNNER (IR, lowering, receipts; wraps others' worlds) | y bellerophon.toolbox (0) |
| BEE z80atlas | Bellerophon | M2 | prometheus/z80atlas | 2026-09-19 98b2149a7 | 2026-09-26 a3086cece | SCIENTIFIC ENGINE | n |
| atlas_bee shim | Bellerophon | M2 | prometheus/atlas_bee | 2026-09-19 97109bd95 | 2026-09-19 933ee9f02 | RUNNER (Atlas questions -> BEE) | n |
| Crius accessibility frontier | Crius | M2 | crius/ | 2026-09-18 de2ea2fb2 | 2026-09-23 7069c0ce6 (seat 2026-09-25 8ad374ed5) | SCIENTIFIC ENGINE (CLOSED) | y crius (0) |
| Ares pressure sandbox | Ares | M2 | ares/ | 2026-09-19 eed9c7121 | 2026-09-25 3f68be2b9 | SCIENTIFIC ENGINE (PARKED) | n |
| Archaeon z80atlas world | Archaeon | M2 | archaeon/z80atlas (census, denovo, postcampaign) | 2026-09-19 c7610ea19 | 2026-09-23 863d34a55 | SCIENTIFIC ENGINE (3rd Z80 build) | n |
| Archaeon envgate/envgate2/lineage/rie | Archaeon | M2 | archaeon/{envgate,envgate2,lineage,rie} | 2026-09-24 58f0463b2 | 2026-09-26 13cdec715 | SCIENTIFIC ENGINE assays on own world + INSTRUMENTATION (taint) | n |
| Archaeon causal lens (contract v0.2/v0.3) | Archaeon | M2 (ops pilot on ubu001/ubu002) | archaeon/causal_lens | 2026-09-26 13cdec715 | 2026-09-27 0a5c0895d | INSTRUMENTATION (cross-engine assay) | n |
| AGE Aether | Aether | BUCKKEEP + RunPod A40 | Aether/, roles/Aether | 2026-09-19 298c2a511 (seat); 2026-09-20 6a5ba2b56 (code) | 2026-09-27 39b7f7e85 | SCIENTIFIC ENGINE | n |
| prometheus_gpu RunPod ladder | Aether | BUCKKEEP -> RunPod | Aether/runpod | 2026-09-20 04ef04347 | 2026-09-27 6c98b4dae | ORCHESTRATION (GPU service; runs Ananke conformance as foreign module) | n |
| CWE Cosmos World-Graph Engine | Cosmos | M2 | prometheus/cosmos, roles/Cosmos | 2026-09-23 70ce535a2 / 7a90be1d8 | 2026-09-25 a56ef7787 / 2026-09-26 4a6a5df52 | SCIENTIFIC ENGINE | y cosmos (10; registry path roles/Cosmos) |
| WTP Ensorain Tensor World Engine | Ensorain | M2 | ensorain/, roles/Ensorain | 2026-09-23 20a4bab5c / 57ed9184e | 2026-09-26 222ed8082 | SCIENTIFIC ENGINE | y ensorain (0; registry path roles/Ensorain) |
| PTE Ananke Packet-Tensor Engine | Ananke | M1 (CUDA; RunPod named) | prometheus/ananke, roles/Ananke | 2026-09-24 7b6958b1c / 7acc2926c | 2026-09-26 4554a2fae / cc98596dd | SCIENTIFIC ENGINE | y ananke (0; registry path roles/Ananke, host null) |
| Aphrodite local engine | Aphrodite | M4 "harry1" | roles/Aphrodite/engine (+ a16 branch) | 2026-09-17 8b54a74b8 (seat); 2026-09-21 85b85b765 (engine) | 2026-09-26 4f937e88f (unmerged a16 branch) | SCIENTIFIC ENGINE (improver-of-improvers; not a world) | n |
| Odysseus brain | Odysseus | ubu001 | odysseus/, roles/Odysseus | 2026-09-25 fe38c055d (seat); 2026-09-26 bd76253c6 (code) | 2026-09-27 626d8c396 | SCIENTIFIC ENGINE candidate (sharded spiking circuit; "v0 is an instrument", odysseus/DESIGN.md) | n |
| Incubation (Lens Genesis) | UNKNOWN | UNKNOWN | incubation/ | 2026-08-26 3b5e310f6 | 2026-08-27 5531f053f | SCIENTIFIC ENGINE (small, closed) | n |
| Atlas index + policy layer | Atlas, Atlas-M2 | M1 (PG), harvest from M1/M2 | atlas/ | 2026-09-19 61c3985fc | 2026-09-26 7190591f4 | INSTRUMENTATION | n/a (is the index) |
| Nyx Chop Shop | Nyx | M3 | nyx/ | 2026-09-11 e75e41160 | 2026-09-25 44e6bda1b | INSTRUMENTATION | n |
| Hephaestus Forge Queue | Hephaestus | M2 (earlier M3) | hephaestus/ | 2026-09-01 7b55e8423 | 2026-09-23 8d9e9ff6a | ORCHESTRATION (math minting; historical content) | n |
| Techne arsenal | Techne | M3 + M2 | techne/ | 2026-04-21 7232ddde5 | 2026-09-25 3906341d7 | INSTRUMENTATION | n |
| Charon admissibility | Charon | M1 | roles/Charon | UNKNOWN (not dated) | UNKNOWN | QUALIFICATION HARNESS | n |
| Kairos | Kairos | M1 (F:\ worktree) | kairos/, roles/Kairos | 2026-04-15 b2b4b993c | 2026-09-11 68df09865 | QUALIFICATION HARNESS | n |
| Serendipity Foundry D | none | M1 (F:/SerendipityD, separate repo) | outside repo | UNKNOWN | UNKNOWN | HISTORICAL (pre-SFE build) | y serendipity.foundry.d (0, IGNORED) |
| Chiron fifth-engine design | Chiron | UNKNOWN | roles/Chiron (origin/chiron/base-role-adopt-2026-09-21 only) | UNKNOWN (not dated) | UNKNOWN | design only, no engine | n |

### 1b. Historical systems (pre-September lines; not ALife engines)

| Name | Path | First | Last | Class / note |
|---|---|---|---|---|
| Harmonia TT exploration engine (April) | harmonia/ | 2026-04-12 98ae574eb | 2026-08-31 1be87a0fe | HISTORICAL (cross-domain math) |
| Apollo v2d LLM evolution | apollo/ | 2026-03-27 8af6ba9e5 | 2026-09-11 1f0873ea5 | HISTORICAL (LLM) |
| Forge T2/T3 ratchet | forge/ | 2026-04-03 b674a9976 | 2026-08-22 25623303e | HISTORICAL |
| zoo conjecture GP | zoo/ | 2026-04-23 37a971380 | 2026-05-05 2b63fc95d | HISTORICAL (math) |
| sigma_kernel | sigma_kernel/ | 2026-04-29 d2ce08cfa | 2026-05-09 6eeb1c823 | HISTORICAL (math) |
| Theseus substrate generation | theseus/ | 2026-05-18 0bd7b5c27 | 2026-08-18 2f666d46d | HISTORICAL (math) |
| Arcanum Infinity | arcanum/ | 2026-03-22 ffb3639d4 | 2026-04-23 57caa85f9 | HISTORICAL (LLM) |
| Ergon tensor hypothesis search | ergon/ | 2026-04-14 98a6590ab | 2026-09-11 7c1ad3729 | HISTORICAL (seat now memory-metabolism INSTRUMENTATION) |
| Ignis latent vector evolution | ignis/ | 2026-03-22 ffb3639d4 | 2026-08-24 e07d166ae | HISTORICAL (LLM; "DORMANT -- closed out 2026-08-24") |
| Rhea | rhea/ | 2026-03-24 39aab6523 | 2026-03-25 35092f0a8 | HISTORICAL (LLM) |
| Aethon | aethon/ | 2026-03-22 ffb3639d4 | 2026-03-22 ffb3639d4 | HISTORICAL (LLM MAP-Elites) |
| Koios | koios/ | 2026-04-12 e3b627bab | 2026-04-23 d13f20df3 | HISTORICAL (instrumentation) |
| exploratory | exploratory/ | 2026-04-23 f8a39bb5e | 2026-05-05 2b63fc95d | HISTORICAL |
| Atalanta primitive hunter | roles/Atalanta, agents/atalanta | 2026-09-11 b33712c94 (roles path) | 2026-09-11 051304cd0 | HISTORICAL (RETIRED 2026-09-11; ran 05-23..05-30 on M1) |
| Agora client, cartography, prometheus_math | agora/, cartography/, prometheus_math/ | not dated | not dated | HISTORICAL (April substrate) |

Counts (1a): 19 rows are SCIENTIFIC ENGINE or candidates, of which 11 are
active or recent enough to carry a card-worthy record (SFE ecosystem, NPE,
BEE z80atlas, Aether, CWE, WTP, PTE, Archaeon z80atlas, Ares, Crius,
Aphrodite). Atlas registers 15 engine ids; 5 of them hold experiments
(vivarium 1,242, archaeon.frontier 422, npe 276, sfe 57, cosmos 10), plus
46 Atlas proposals with engine_id NULL -> 2,053 rows in atlas.experiment.

## 2. Classification notes and disagreements with ENGINE_LANDSCAPE

- SFE: ENGINE_LANDSCAPE correctly calls it "instrument, not experiment".
  Atlas registers it kind=ENGINE. Under this spike's definitions it is
  INSTRUMENTATION; the scientific world/organism representation of the
  SFE era lives in wforge (worlds), Proteus (players), archaeon/wse
  (worlds on proteus.foundry) and executors, with Vivarium and Archaeon
  as runners -- the "Incubator" separation in
  SerendipityFoundry/worldfoundry/WORLD_FOUNDRY_V0_EXTERNAL_REVIEW_PACKET.txt
  s0. The SFE card below therefore describes the hub of that ecology.
- "BEE" label: ENGINE_LANDSCAPE merges toolbox and z80atlas. toolbox is a
  kernel/harness that "never decides what is interesting"
  (prometheus/toolbox/README.md); all of Bellerophon's findings come from
  z80atlas, which imports nothing from toolbox.
- Engines ENGINE_LANDSCAPE missed: Ares (ares/, 3 cycles, 190+130+cycle-0
  GA runs), Crius (crius/, 2 campaigns, CLOSED), Herakles EVCA
  (executor library), Alien Circuitry (dormant), Odysseus (new,
  ubu001), Proteus/wforge/Ludus (the SFE-era organism and world
  foundries), Archaeon WSE.
- Host: ENGINE_LANDSCAPE puts Ananke on M1; the seat also cites RunPod,
  M2, M3 (classifier sweep) and Aether's RunPod ladder now runs Ananke
  conformance -- host is "M1, moving".
- Z80 triplication (NPE Z80xAtlas, BEE z80atlas, Archaeon z80atlas) is
  confirmed; all three are listed as separate rows because each has its
  own VM and evidence.

## 3. Where Atlas and git disagree (with provenance)

D1. Z80 worlds not indexed. BEE z80atlas (63,247-run 72 h campaign,
    11,657-run coupling campaign), Archaeon z80atlas (101,003 runs) and
    Nestor's z80atlas/verify/forensics/c9x/W1 campaigns have 0 Atlas
    experiments. Provenance: atlas/harvest/archaeon_campaigns.py:59
    matches only r"archaeon/(campaign\d+)/(.*)$"; frontier.py reads only
    archaeon/frontier (ls_tree l.39); npe.py (VERSION npe/5) models only
    programs nestor.graphworld (primordial/ledger/<Lane>.jsonl) and
    nestor.cw01 (CWDIR roles/Nestor/campaigns/cw01-2026-09-17); there is
    no BEE / Aether / Ensorain / Ananke / Aphrodite / Ares / Crius
    harvester in atlas/harvest/.
D2. Registered-but-empty. crius, ensorain, ananke, proteus, ludus,
    herakles.evca, harmonia.rulers, bellerophon.toolbox all have 0
    experiments though crius (2 closed campaigns), ensorain (E0-E2,
    WTP-01..03) and ananke (C1 6,596 rows, C1b) have completed campaigns
    in git. Provenance: registry notes "not yet harvested"
    (atlas/registry.json); Atlas STATUS 2026-09-25 "Nestor C9, Ananke,
    Cosmos still unadapted" (Cosmos since adapted, ATLAS-37).
D3. Unregistered engines. Aether, BEE z80atlas, Archaeon z80atlas/envgate,
    Aphrodite, Ares, Odysseus, wforge, Alien Circuitry are absent from
    atlas.engine. (ENGINE_LANDSCAPE s4 says "AGE, CWE, WTP, PTE, Aphrodite
    not in the registry" -- stale for CWE/WTP/PTE: registry.json and
    atlas.engine carry cosmos, ensorain, ananke since f8df65681
    2026-09-24; it is correct only for AGE and Aphrodite.)
D4. Wrong code_paths. registry cosmos -> roles/Cosmos (code is
    prometheus/cosmos), ensorain -> roles/Ensorain (code is ensorain/),
    ananke -> roles/Ananke (code is prometheus/ananke), host null. Any
    path-based commit attribution for these engines misses the code.
D5. Stale NPE note. registry npe notes "code only on nestor/* branches
    (not origin/main) as of 2026-09-19"; primordial/ is on origin/main
    since the merge f423a09ac (2026-09-25). npe.py docstring still
    names the M1-local default ref nestor/sidequest-graphworld-2026-09-14
    (it now discovers refs, l.45-68).
D6. Experiment grain mismatch for SFE. atlas.experiment has 57 sfe rows,
    but the Atlas-read ledger extracts in atlas.engine_instance record
    89,939 experiments in the M1 ledger (86,296 from client "vivarium")
    and 2,070 in the M2 ledger copy. Atlas models Archaeon campaign
    slots, not SFE experiment rows; all 57 sfe rows have driver_seat
    Archaeon, none Daedalus/Harmonia/Theophrastus. The 1,242 vivarium
    rows are the queue view of the same activity.
D7. Engine attribution. Registry engine archaeon.campaign (RUNNER) holds
    0 experiments; its campaigns archaeon.campaign/cmp1..6 and
    archaeon.wse/* are filed under engine_id sfe (atlas.campaign), so the
    runner is invisible and SFE looks like it ran Proteus-VM science.
D8. Kind disagreements. Atlas kind vs this spike: sfe ENGINE vs
    INSTRUMENTATION; vivarium RUNNER vs ORCHESTRATION; ludus HARNESS vs
    SCIENTIFIC ENGINE (world foundry, roles/Ludus/CHARTER_v3_WORLD_
    FOUNDRY.md); bellerophon.toolbox HARNESS (agree); archaeon.frontier
    RUNNER vs ORCHESTRATION.
D9. Status disagreements. atlas.engine says sfe LIVE (currency
    2026-09-19); git/Vivarium evidence says SFE timed out on :8811 with
    watchdog disabled (8c5a1a23b 2026-09-24) and no Daedalus commit after
    2026-09-18. crius LIVE vs roles/Crius/STATUS.md CLOSED 2026-09-23.
    herakles.evca/proteus/ludus UNKNOWN vs git last commits 09-16..09-18
    (dormant).
D10. Lag. v_coverage: newest successful harvests 2026-09-25 (most) and
    2026-09-26 (cosmos/1, comb/2); atlas.git_commit newest authored
    2026-09-25 08:25; newest modelled experiment activity 2026-09-22
    (Atlas STATUS pass note). Everything on 2026-09-25..27 (Aether
    AETH-03, Aphrodite A17, BEE multiday, Ananke C1b, Archaeon contract
    v0.3) is invisible. Atlas's own rule: lag is never absence.
D11. Inflated facts. frontier/3 indexed 299,991 identical
    BLOCKED_BY_SUPPRESSION events as separate facts; frontier/4 HELD
    pending Archaeon (roles/Atlas/STATUS.md, repair 2026-09-26).
D12. Host coverage. Atlas collects from M1 only; M2-local evidence
    (frontier runs/, M2 SFE ledger, logs) is recorded EXPECTED:M2; hosts
    BUCKKEEP, M4, ubu001 and RunPod are not in atlas.host
    (registry.json hosts M1-M4 only; M3/M4 lan_ip null).

## 4. Engine cards (scientific engines with enough evidence)

Nine cards. SFE first (mandatory). Evidence was gathered read-only from
origin/main f287a4fdb and the origin/* seat branches on 2026-09-27; "SHA
YYYY-MM-DD" = the commit that last touched the cited path unless stated.
UNKNOWN means not found, not absent.

### 4.1 SFE -- Serendipity Foundry Engine (Daedalus, M2)

- Name: Serendipity Foundry Engine, "durable multi-world research runtime".
  Core SerendipityFoundry/SerendipityFoundryEngine/sfe/ (9,423 LOC: runtime.py
  5,125, api.py 1,599, store.py 1,190, executors.py 492), serve.py, client
  SerendipityFoundry/SerendipityFoundryClient/sfclient (853 LOC). Charter
  roles/Daedalus/CHARTER.md (249bb0f98 2026-09-11). Sits inside a larger
  Incubator ecology: PROTEUS player foundry -> DAEDALUS world foundry
  (SerendipityFoundry/worldfoundry/wforge) -> HARMONIA matchmaker -> SFE
  record -> MNEMOSYNE PEW (SerendipityFoundry/worldfoundry/
  WORLD_FOUNDRY_V0_EXTERNAL_REVIEW_PACKET.txt s0, 6efa4f88d 2026-09-02).
- Status: DORMANT, liveness UNKNOWN. First commit on SerendipityFoundry/
  d332658cf 2026-09-01; last 9cfcd3779 2026-09-18 (Campaign 6
  "engine as observatory" interface delta, "nothing built"); 117 commits.
  roles/Daedalus/STATUS.md last touched 3ddbf5b6a 2026-09-17, currency
  2026-09-18 03:45Z: 9.0.1 in production at https://192.168.1.191:8811,
  schema 9, build 699ca0f9 frozen at b0d752183. 8c5a1a23b (2026-09-24,
  Vivarium) reports M2 at 98% memory commit, SFE on :8811 holding its port
  but timing out, SFEngineM2Watchdog Disabled, 0 rows enqueued since 09-18.
  No Daedalus commit after 09-18; no restoration record found. Atlas
  engine_instance eng_906356f7... last_seen 2026-09-18. M1 instance
  eng_8a37a5d3 retired (last_seen 2026-09-11), kept as archive.
- Scientific lens: an instrument, not a world. No physics. A WORLD is a
  tenant partition of ledger rows (world_id NOT NULL on every scientific
  table except families). docs/SCIENTIFIC_PROVENANCE.md (642736763
  2026-09-06): it "compares hashes, counts distinct things, and checks
  containment... never computes a variance, fits a model". Its distinctive
  representation is of the RESEARCH ACT, not the organism: hash-chained
  per-world event ledger; predictions/observations ordered by
  committed_seq; selection "families" that keep the losers; attestation of
  executed_config_hash vs requested. Built-in organisms are toys:
  BitStringExecutor, NKLandscapeExecutor (nk_landscape_v0, N 8-20),
  NondeterministicExecutor (sfe/executors.py b91880a2d 2026-09-10);
  mutation/selection live in clients. In practice Archaeon's campaigns used
  Proteus player-VM programs (25 opcodes) via archaeon/wse, with SFE as
  ledger/provenance store (archaeon/campaign1 report, 0728e9989).
- Good at: proving a prediction preceded its observation (post-hoc
  laundering exposed; STATUS.txt T11); making best-of-N selection visible
  and checking declared n against distinct recorded sources
  (FAMILY_EXTENT_DIVERGENCE); tenant isolation; requested-vs-executed
  attestation; import lineage (origin=IMPORTED); exactly-once commit and
  crash/restart survival (k1/k2 restart rehearsal 2026-09-17).
- Poor at: anything dynamical, ecological or spatial -- organisms never
  interact inside the engine; statistical adequacy is deliberately out of
  scope (SCIENTIFIC_PROVENANCE s8); resource metering only as reported by
  callers; full world replay PARTIAL (STATUS.txt, d332658cf); built-in
  genomes NK/bitstring only, so a rich organism must live outside and SFE
  sees only its scores/digests. Campaign 6 found per-evaluation T0
  behavioural data cannot be stored, only hash-anchored (f42b07422).
- Observables: event-chain integrity, prediction/observation order, family
  census (selection_visible), attestations, cost events, budgets, lineage
  edges, per-result reproducibility class; tables worlds, experiments,
  predictions, observations, measurements, claims, hypotheses, families,
  lineage_edges, artifacts, budgets, work_items, events, read_scopes
  (sfe/store.py 8582528ab).
- Blind spots: mechanism/behaviour invisible; design adequacy unjudged;
  wall/CPU/mem not auto-metered; WAL grows unbounded under a saturating
  writer (3.4 GB per 20K generations, roles/Daedalus/STATUS.md); the
  engine's own liveness is not reported anywhere since 2026-09-18
  (see Status).
- Notable findings (science is Archaeon's/Proteus's; SFE supplied the
  record):
  * Campaign 2: Campaign 1 transfer positives died at n>=10 under common
    random numbers (+0.009, +0.002); 7 negatives with a capable assay, 3
    weak, 0 supported (archaeon/campaign2/CAMPAIGN_REPORT.md, 4d80d4b1d).
  * Campaign 3 (cb9135104): 0/78 K=2 runs reached the summit; a delay
    ladder produced delay invariance 11/12 seeds vs 0/6 matched direct
    search.
  * Campaign 4 (8f1a82ced): mutational damage is a cliff not a slope --
    0/5,472 single edits and 0/2,280 multi-step edits improved a parent;
    large connected neutral network.
  * Campaign 5 (cdb55e152): BOUNDARY_CREATED_NO_DISCOVERY_GAIN.
  * Engine-side: Harmonia integration found 2 cross-tenant leaks, fixed
    before onboarding (roles/Daedalus/CHARTER.md); Vivarium Track A joint
    receipt 29/29 PASS (45195dd83); G1 long run 15,408 s, 0 HTTP 5xx
    (e7a699099).
  * Scale (Atlas atlas.engine_instance extract, read 2026-09-27): M1 ledger
    D:/Prometheus-data/sfe/engine.db held 89,939 experiments, 86,296 of
    them from client "vivarium", 3,068 harmonia-m2, 67 theophrastus; M2
    ledger copy held 2,070 (cmp1-3-archaeon 1,307; qualify-v9 324).
- Dependencies: Python + FastAPI/uvicorn (pyproject.toml), SQLite WAL,
  content-addressed blobs; HTTPS with self-signed per-IP certs
  (deploy/m1.crt, deploy/m2.crt; client copy
  SerendipityFoundryClient/config/m2.crt); port 8811 on 192.168.1.191 (M2),
  formerly 192.168.1.202:8799 (M1); Windows Scheduled Task watchdog
  deploy/sfengine_m2_watchdog.ps1 (b11c9931b). No GPU. Consumers:
  Vivarium, PEW (:8377), contract roles/Harmonia/contracts/sfe_contract.json.
  deploy/ imports archaeon.producer.costs and viv.* (ENGINE_LANDSCAPE
  table, 95fff9111).
- Portability: core is MERELY LOCATED on M2 (stdlib + FastAPI; no
  hardcoded host paths found in sfe/, serve.py, sfclient/). Deployment is
  host-bound: deploy/sfengine_m2.cmd (2b21acf76) hardcodes
  D:\Prometheus\.venv-m2, the M2 IP and cert paths (superseded by a
  pinned copy at D:\Prometheus-data\sfe\, not in repo); PowerShell
  watchdog; production ledger C:\Prometheus-data\sfe\engine.db; certs
  bound to IPs. engine_instance_id is minted per DB, so identity travels
  with the ledger, not the host. A move = new certs + launcher + contract.
  The ledger DATA is the non-portable asset (off-repo, Windows paths).
- Cross-pollination: CONTRIBUTE -- prediction-before-observation
  ordering, loser-keeping selection families, SUCCESSFUL_NEGATIVE /
  NO_EFFECTIVE_INTERVENTION statuses, executed-config attestation, and
  the warn/strict/off science profile (off as a control arm) to engines
  that lack a ledger (NPE, BEE z80atlas, Archaeon z80atlas, Aphrodite,
  Ares, Crius). Its NK executor is a small known benchmark landscape.
  BORROW -- BEE-style replay coverage (606/606) to close PARTIAL replay;
  real resource metering; the unbuilt Campaign 6 T0 segment anchors
  before holding behavioural data. Actual importers: prometheus/toolbox/
  backends/sfe_executor.py (2237af42a, lazy sfe.executors);
  archaeon/campaign2, campaign5, archaeon/frontier (nominate.py:19,
  migrate_specs.py:15, integrity.py:41 sfe.freeze.v1); vivarium/tools,
  deploy, tests; genesis/harmonia_a, harmonia_c. None in primordial/.

### 4.2 NPE -- Nestor Primordial Engine (Nestor, M1)

- Name: "Nestor Primordial Engine"/"NPE window" (roles/Nestor/FINDINGS.md
  on origin/nestor/s1-forensics-2026-09-23, head d63b76a5f); code tree
  "Primordial Machine swarm" (primordial/README.md, a901ba0c9 2026-09-14),
  ~65.6k LOC Python in primordial/. Seat Nestor, host M1 SKULLPORT.
- Status: DORMANT (at rest). primordial/ first a901ba0c9 2026-09-14, last
  f75e8ad54 2026-09-17 (generation 1 frozen since); reached origin/main
  only via merge (first-parent f423a09ac 2026-09-25). roles/Nestor first
  0100d36cd 2026-09-14, last d63b76a5f 2026-09-26 ("W1:
  C-STATELESS-FFA6 CONFIRMED... window closed"). STATUS.md 345e0ceef
  currency 2026-09-26 07:15 EDT: budget window CLOSED, nothing running,
  loop "at rest, not retired"; operator directive 2026-09-26: no new
  campaign without explicit authorization. Pending: S1 merge request; C3
  holdout D sealed for Cosmos (origin/nestor/c3-holdout-d-2026-09-25,
  5e05307b2).
- Scientific lens: origin of heredity/replication, with the charter
  making Nestor accountable for evidence being "worth less than it first
  appears" (RESPONSIBILITIES.md s1, fb86294c7). Three generations:
  (1) GPU swarm 09-14..09-17, tensor-train brains, 5+ lanes on a Redis
  bus, rounds R1-R8 (roles/Nestor/sidequests/graphworld/SWARM.md);
  (2) CW01 09-17..09-19, declarative WORLD.json per experiment
  (roles/Nestor/campaigns/cw01-2026-09-17/experiments/*/WORLD.json,
  3af735d67); (3) Z80xAtlas 09-19..09-26, byte programs in a Z80-style VM
  with ALLOC/LDIR/BIRTH (roles/Nestor/campaigns/z80atlas-2026-09-19/z8.py),
  then verify/forensics/c9x/W1 campaigns. Distinctive: barrier
  decomposition (variation -> acquisition -> establishment -> sustained
  copying) under frozen matched-arm confirmations.
- Good at: mechanism isolation with Fisher-tested matched arms;
  separating organism-caused copying from lookalikes (P-11 causal-copy
  certificate, randomized-victim assay, instrument f28e5fd72); auditing
  its own instruments.
- Poor at: generality beyond one cell (C-ATOMIC generality C2 1/120;
  C-STATELESS held only in ffa6); results tied to VM encoding length
  (1-byte alias vs 6-byte chain, E-8, E-W1-1) and pair-tape write-back --
  i.e. about this VM's physics; on the pair tape an organism keeps its id
  while its bytes are replaced, so id-tracking certifies identity not
  heredity (C9-D14); spontaneous discovery shown only in permissive,
  relieved worlds.
- Observables: P-11 certificate and lineage depth (runaway >=20); births
  backed by evidence the organism placed the child's bytes; fidelity
  before mutation; fresh-state donor pass rate; matched-pair Hamming-1
  effects; EXPERIMENT_GRAPH.jsonl node classes.
- Blind spots: old lineage logs keep only a 400-event tail and omit
  migrations (A-5, P-1); passing P-11 != fertile child (X-STALL); S1
  replays are a new assay, not retroactive evidence for the 72 h run;
  recombination edges not causal in the H3 certificate (C9-D11, open);
  several results theory-aware by date (Aporia #621). Generation-1
  consolidated findings ledger: UNKNOWN (not located).
- Notable findings (FINDINGS.md @ d63b76a5f):
  * Forensic reversal: 1,031 "spontaneous replicators" (A-1) were all
    PAIR_EXECUTION; ~88% splice artefacts because fidelity was read after
    _mutate (Z80A-D05); only 57 survive P-11, max depth 2 (E-3). A-4, A-5,
    A-6 withdrawn; C9 H1 INVALID (C9-D16), rerun as C9-H1R ->
    COST_INTERACTION_ONLY.
  * Confirmed: E-6 self-location necessary (depth>=3 13/36 vs 0/36,
    p=1.6e-10); E-8 dense 1-byte encodings -> spontaneous replication
    13/40 vs 0/40; C-ATOMIC tape-write erosion blocks heredity 46/80 vs
    1/80 (p=4e-17, one cell); E-W1-1 block-copy accessibility 1/64 ->
    39/64 (p=1e-14); E-W1-2 register "self-poisoning" 11/33 -> 34/42.
  * CW01 cw01-e05 NULL on replication (MECHANISM_OF_NULL.md).
  * Twelve standing methodology lessons (FINDINGS s D).
- Dependencies: Gen 1 -- Redis Streams on 127.0.0.1:6390 in container
  gw-substrate (falkordb/falkordb, Redis 8.6.3 + FalkorDB 4.20.4) under
  WSL2; torch 2.11 cu128, cupy, cuTensorNet; RTX 5060 Ti 16 GB; venv
  C:/Users/jcrai/lab/gw-venv. Gen 3 -- pure-stdlib Python, Windows
  launch.cmd + schtasks, worktree on F: (SMR HDD). CW01: 3 files import
  torch/cupy/redis/numba.
- Portability: Gen 1 INHERENTLY host-dependent (loopback Redis container,
  CUDA GPU, WSL bridge latency 0.33 ms used as a design prior). Gen 3
  MERELY LOCATED (deterministic stdlib; only launch path is M1-specific).
  Demonstrated: Archaeon's causal lens replayed 36 NPE runs off-host
  (archaeon/causal_lens/PORTABILITY01_REPORT.md, 37145999d).
- Cross-pollination: imports wforge (primordial/soup/b1, metric/*_r8.py,
  nv/warp/crossover.py), archaeon.campaign / wse.worlds / wse.evolve and
  proteus.foundry.* (cw01-arch4 runners arch4rt.py, ctxworlds.py,
  ticks.py) -- on S1 via git grep. CONTRIBUTE: P-11 instrument,
  report_audit.py with injected-defect tests, the s D lessons, holdout D
  for Cosmos. BORROW: an SFE-style ledger (none today), Archaeon's
  4-identity attribution for the pair-tape identity problem.

### 4.3 BEE z80atlas -- Bellerophon's Z80 world (Bellerophon, M2)

- Name: prometheus/z80atlas, "Z80 x Atlas combinatorial campaign harness"
  (prometheus/z80atlas/__init__.py, 98b2149a7). NOTE: the label "BEE"
  properly names prometheus/toolbox (the "Prometheus Worlds Kernel",
  README), which is a qualification/orchestration harness; the findings
  come from z80atlas, which does not import toolbox.
- Status: ACTIVE. z80atlas first 98b2149a7 2026-09-19, last a3086cece
  2026-09-26 (14 commits); toolbox 4c0435544 2026-09-18 .. 97109bd95
  2026-09-19 (frozen since); roles/Bellerophon 44dc09559 2026-09-18 ..
  ee7a7d954 2026-09-26. Multi-day campaign RUNNING since
  2026-09-26T16:40Z, 4,160 runs at 20k ticks, prereg 12ce26e23, analysis
  blind until stop (roles/Bellerophon/STATUS.md @ ee7a7d954 on
  origin/bellerophon/multiday-campaign-2026-09-26). No CHARTER file;
  charter = roles/Bellerophon/prompts/2026-09-18_worlds_kernel/.
- Scientific lens: origin of replication on 256-byte self-modifiable tapes,
  Z80-like VM with real LDI/LDIR, neighbour window [L,2L), worlds
  SOUP/GRID/NICHES/GRAPH (prometheus/z80atlas/vm.py); ENDOGENOUS
  (organism copies itself) vs EXOGENOUS (world copies it) controls;
  physics v3 couples computation to a copy-resource ledger.
- Good at: whether own-code self-replication arises from random starts
  and what it causally needs (substrate ablations); whether contingent
  reward maintains task code; paired ON/OFF/YOKED/SHUFFLED arms;
  deterministic replay; (toolbox) differential transplants of other
  ecosystems' experiments.
- Poor at: copy-code knockouts (copier usually one mutation away; 126/345
  NOP-ablated tapes still replicate, forensics_2026-09-23/
  GROUNDING_REPORT.md s5, 3efdacf7e); task effects under IMPLICIT
  pressure (run-for-run identical across tasks); heritability inflated
  by whole-window LDIR (measures copy fidelity); P5 protection-of-
  computation at ceiling (0.999 both arms); acquisition of new competence
  (effects are MAINTENANCE of seeded code); toolbox cannot represent
  some source rules (a4/a5 ABSENT, e.g. offspring cap).
- Observables: SR births, lineage depth, sustained lineages, COPY_EVENT
  births vs own-code SR, origin provenance (BUILT_BY_COPY, RAMP),
  comp_final, r_cc/r_nc, extinction, replay-hash identity rate, causal and
  origin ledgers.
- Blind spots: detector/trigger artefacts (5 flag classes DETECTOR_ONLY or
  retired); defects unseen during the 72 h campaign -- P1 (migration
  spawned world-made copies under endogenous physics) and H1
  (un-relocated seeded hybrid) (POST_CAMPAIGN_FORENSICS.md, 3efdacf7e);
  raw run dirs local only (C:/Users/James/z80atlas_grounding_2026-09-23,
  2.2 GB); 72 h CAMPAIGN_PACKET.md not in git.
- Notable findings:
  * 72 h campaign (63,247 runs, 1,629 flags) did not survive forensics:
    all 5 flag classes collapsed; "endogenous not external" reversed
    (EXTERNAL 178 vs ENDOGENOUS 2, p 2.5e-15); pollination/topology effect
    was defect P1 (extinction 0/150 v1 vs 148/150 v2) (GROUNDING_REPORT
    s4, s8; prereg a1b066309).
  * Spontaneous own-code self-replication CONFIRMED_CAUSAL in 1-5% of
    fresh runs; requires LDIR and the undefined-byte NOP slide (0/300 vs
    8/300 without); 160/160 first replicators copy-built; only 39.4% of
    origins sustain, below prereg >=50%.
  * Physics v3 coupling: 11,657 runs, 0 voids, 341/341 identical replays
    (prereg c9bed96de, report 6a0b9813e); P1-P4 hold, P5 reversed at
    ceiling, P6 n.s.; acquisition evidence ECHO only (29/150 vs 6/150);
    fully random worlds 0/3,200.
  * Atlas->BEE transplant pilot (toolbox): of 6, a1 INVERTED, a2/a3
    CHANGED, a4/a5 ABSENT, a6 PRESERVED, all bit-replayed;
    atlas_bee/ATLAS_EXTENSION_PROPOSAL.md (933ee9f02) never applied.
- Dependencies: z80atlas stdlib only; 12-18 worker processes on M2;
  toolbox core stdlib with optional lazy imports archaeon.frontier.specs
  (backends/sfe.py:81), sfe.executors (backends/sfe_executor.py:30),
  proteus.foundry (ref/players.py:134-151), SerendipityFoundry.
  worldfoundry.wforge (ref/worlds.py:207), archaeon.campaign6.worlds
  (ref/worlds.py:262).
- Portability: code MERELY LOCATED (stdlib, deterministic; cross-platform
  WSL replay probe science/CROSS_PLATFORM_*_2026-09-19.json). Evidence
  host-bound: C:/Users/James/... workdirs and D: worktree on M2
  SPECTREX5; throughput/OOM limits are M2 properties (coupling F4).
  Archaeon's lens ran on it off-host (845 runs, 28.96M births,
  PORTABILITY01_REPORT.md).
- Cross-pollination: CONTRIBUTE replay discipline (606/606), mutant
  ledger (85/85 caught), EXTERNAL/SHUFFLED/YOKED arms, the endogenous vs
  exogenous control. BORROW an SFE-style ledger for flags (the 72 h
  packet is not in git), NPE's P-11 certificate for "built by copy".

### 4.4 AGE -- Aether (Aether, BUCKKEEP + RunPod)

- Name: Aether, artificial physics without organisms; "AGE" = its GPU
  kernel/controller (Aether/runpod/aeth01_canary/age_controller.py).
  Baseline law aeth01.v1, "repaired freeze CANDIDATE, not frozen"
  (roles/Aether/STATUS.md).
- Status: ACTIVE. roles/Aether first 298c2a511 2026-09-19; Aether/ first
  6a5ba2b56 2026-09-20; last 39b7f7e85 2026-09-27 (AETH-03 research
  block, origin/aether/research-block-2026-09-27; results section s5 of
  Aether/AETH-03/PHYSICS_DESIGN_03_2026-09-27.md still empty); also
  6c98b4dae (origin/aether/runpod-iter5-2026-09-27). STATUS 17a94b97d
  2026-09-26 "ACTIVE, not blocked. Host BUCKKEEP". No CHARTER.md on any
  aether branch. Most work is on unmerged branches.
- Scientific lens: 2-D torus lattice, five uint8 fields per site (opcode,
  arg0, arg1, payload, energy) (Aether/AETH-01/PHYSICS_SPEC_DRAFT.md
  l.15-20); no birth/alloc primitive, no genome IDs, synchronous
  deterministic ticks. Removes predefined assembly boundaries entirely:
  can executable matter find persistence/transmission without them
  (Aether/AETHER_CONCEPT.md)?
- Good at: substrate-only persistence/propagation/circuitry questions;
  forked-twin interventions and lesion arms; light cones of a one-bit
  difference; energy routing and certified world death; GPU-CPU bit-exact
  replay (300/300, 400/400, 464/464, GPU_MEMORY_OPTIMIZATION_01_
  2026-09-22.md); cheap-lattice proxy validity (256^2 reproduces 2048^2
  bulk measures within 0.1-2.9%, AETH-02_CLOSE_2026-09-24.md s0).
- Poor at: organisms, heredity, selection (none appeared); distributed or
  informational function (AETH-02_CLOSE s6); arg1 mod 5 addressing
  artefact -- every single-bit arg1 flip changes target field (spec
  l.63-80); perturbation supplies ~42% of template change immediately,
  ~95% cumulatively, so intrinsic copy dynamics are near static.
- Observables: edge run-lengths/recurrence, occupancy, cycle enrichment vs
  nulls, per-field change rate, energy Gini, H(opcode), frozen fraction,
  twin-difference radius/generation, content signature, DEAD_CERTIFIED.
- Blind spots: aeth02_runner.py compared each sample to state 250 ticks
  old, inflating opcode change rate +128% relative; one validation claim
  withdrawn (AETH-02_CLOSE s5); old null lacked source starvation; twin
  predicate ignored law-carried state until World.extra (39b7f7e85);
  long-horizon Block C (<=10,000 ticks) unrun.
- Notable findings: FIRST_LIGHT (f1f6dd637, 2026-09-22) six 4096^2 worlds x
  5,000 ticks, $2.02, "No phenomenon on the evidentiary ladder was
  observed"; MEMORY_WALL_MOVED (3cf8f9921) 16384^2 on one A40, 257 -> 128
  B/site; AETH-02 close (0e63a3d52) "No evidence... of demonstrated
  nontrivial function"; PHYSICS_DESIGN_01 (43202cf7b) 89% of edge
  terminations are source starvation, cycles 0.37x nulls, 4/5 candidate
  laws killed -> "the substrate lacks propagation"; PHYSICS_DESIGN_02
  (1,280 twin pairs) only rcv propagates, weakly (6/128 origins), by
  activation timing through inert matter (starving inert sites: 0/128 vs
  17/128 sham); 92% of what propagates is who-fired/energy, 8% content;
  UNRESOLVED, no scale-up.
- Dependencies: NumPy CPU oracle (aeth01_cpu_oracle.py); pod image NumPy
  2.2.0, cupy-cuda12x 13.3.0, CUDA 12.4.1 (Aether/runpod/aeth01_canary/
  Dockerfile); RunPod A40 48 GB $0.49/h; spend AETH-02 $2.83/$3.00,
  engineering ladder $0.8446/$5.00; billing reconciliation c1cc6e3b9;
  comms Postgres 192.168.1.202. BUCKKEEP: the seat's local workstation,
  C:/ paths (Windows inferred), hardware UNKNOWN; moved from M2.
- Portability: MERELY LOCATED for the science (128-512^2 NumPy CPU, 256^2
  validated as proxy, kernel identity hashed, CPU/GPU bit-exact).
  INHERENTLY GPU-bound only for >=16384^2. Five POSIX pod-side tests are
  skipped on BUCKKEEP (unmeasured, not passed).
- Cross-pollination: Aether/runpod/prometheus_gpu is becoming a shared GPU
  service -- iteration 5 wraps Ananke's conformance suite as a foreign
  module (Aether/runpod/foreign/ananke_conformance/, 6c98b4dae);
  CONTRIBUTE twin/light-cone assay, leak-free pod ownership discipline
  (RUNPOD_ENGINEERING_03), the "own null is defective" lesson. Declared
  clean-room: borrows no mechanism from BEE/NPE/SFE (AETHER_CONCEPT.md).

### 4.5 CWE -- Cosmos World-Graph Engine (Cosmos, M2)

- Name: CWE, "an adversarial physics chamber over executable
  counterfactual worlds" (roles/Cosmos/campaigns/REVIEW_PACKET_CWE_
  2026-09-23.txt s0). Code prometheus/cosmos/ (numpy; 44 modules + 9
  tests).
- Status: EXPERIMENTAL, waiting on operator. prometheus/cosmos first
  70ce535a2 2026-09-23, last a56ef7787 2026-09-25; roles/Cosmos first
  7a90be1d8 2026-09-23, last 4a6a5df52 2026-09-26 ("C3: D seal received
  (#599) and commitment verified by hash"). STATUS.md (ffd9887b6, currency
  2026-09-25T10:50Z) still says BLOCKED on holdout D -- stale vs
  REVIEW_PACKET_COSMOS_D_SEAL_2026-09-26.txt. Seal commit a56ef7787 is not
  an ancestor of origin/main (checked). C0 closed by operator
  (af2af37f4).
- Scientific lens: "Change almost everything and measure what refuses to
  change": search a small grammar (C, N, K, G, +Q; size <=6, 1 atom or
  2-atom conjunction) for normalized phase-boundary laws that hold across
  three independently written substrates (register VM, delay ring, block
  CA), with leave-one-lineage-out, permutation null over the whole
  search, adversarial counterexample search, then transfer to CSPRNG-
  sealed holdout worlds with receipted predictions (packet s1). C3 moves
  to a P1/P2 "functional use of past information" certificate
  (roles/Cosmos/c3/S1_PREREG_P1P2_GATE.md).
- Good at: killing wrong laws (7/9); finding missing coordinates by
  attack; per-family location bias hidden by pooled residuals; sealed
  transfer with receipted predictions; intervention direction/magnitude.
- Poor at: coordinates are declared by the substrate author and can
  "smuggle the answer" (packet Q4); recovered law A agrees 97.5% with the
  hand-derived task economics -- not a discovery (V2); nothing about
  "intelligence, memory in general, or reality" (s7); only
  low-complexity conjunctive boundaries are expressible.
- Observables: balanced accuracy vs 5-NN/majority, Brier vs climatology,
  confirmed-contradiction rate (kill >5%), per-family log2 location
  offset (gate 0.10), intervention direction/precision; C3 P1 decodability
  (bits), P2 interchange-ablation effect.
- Blind spots: one author wrote every substrate incl. sealed D/E/F (s7);
  location gate not independent of location-aware selection; no sealed
  universes left from C0; pinned C0b replay OOMed after pre-mining.
- Notable findings: C0 run 2 no surviving invariant (54ca84228); C0b law A
  held on sealed D/E/F (BA .983/.972/.930 vs 5-NN .77-.84; seals
  800072c1e, 0ed2fced1, 383fd90b4); G6 intervention FAIL 0/12 from an
  engine one-flip defect, retests G6b 12/12 (5b84b66e0); search method
  UNRESOLVED (active .790 vs random .788); C1 location gate killed 3 laws
  with 2-4% contradiction (e51fc75ae); audit PASS 9 stores, byte-identical
  reruns (c52f37d46); C3 gate v2 FAIL, v3 PASS (940b486f2), C3 law
  hash-committed (0ecafed1...) and UNTESTED on Nestor's D.
- Dependencies: numpy, one scipy.optimize import, pytest;
  COSMOS_HOME=C:/Users/James/cosmos_runs; holdout author Nestor (M1).
- Portability: MERELY LOCATED (self-contained numpy; `python -m
  prometheus.cosmos.runtest --full`); sealed-family broker needs a
  subprocess (COSMOS_BROKER=1); worker pool has OOM/pipe-exhaustion
  history on M2.
- Cross-pollination: concepts only (no imports) from
  prometheus/toolbox/receipt.py, archaeon/wse/ssf.py SELECTIVE_PAYS.v1
  (fit(SEL) - max(fit(LOG), fit(LAST)) >= 0.10), archaeon/wse/controls.py,
  roles/Aphrodite/engine/semantics.py, Nestor's Hamming-1 partner
  (roles/Cosmos/design/PROVENANCE.md). CONTRIBUTE: author-separated
  foreign holdouts (answers WTP W1/W2), per-family location gate,
  permutation-null-over-search. Emits Atlas-shaped JSONL export
  (campaigns/atlas_export_c0/MANIFEST.json) -- the only engine Atlas
  ingests via a seat-authored export.

### 4.6 WTP -- Ensorain Tensor World Engine (Ensorain, M2)

- Name: Wild Tensor Physics / "Tensor Physics of Intelligence Foundry"
  (roles/Ensorain/prompts/2026-09-24_foundry_directive/, 34a75ac19);
  engines ensorain/{e0,e1,e1p5,e2,d1,wtp,wtp2,wtp3,lm01}.
- Status: EXPERIMENTAL, frozen and awaiting launch. ensorain/ first
  20a4bab5c 2026-09-23; roles/Ensorain first 57ed9184e 2026-09-23; last
  222ed8082 2026-09-26 (LM01 operator review packet). STATUS currency
  2026-09-26 13:30Z: WTP-LM01 prereg v0.3.1 FROZEN at 768ea8ce9
  (FREEZE.json 87d06770c), not launched, waiting for operator "LAUNCH".
- Scientific lens: bounded learning substrates (TT, CP, low-rank, random
  features, hash) learning from ONE shared experience stream under world
  physics that make memory necessary, compared to a null ladder N0-N6 at
  equal memory caps and FLOPs (ensorain/PREREG_WTP03.md s1-2). LM01: does
  a bounded coarse-grained persistent state beat exact persistent storage
  (PREREG_WTP_LM01.md s1).
- Good at: controlled head-to-head substrate comparison with honest
  resource accounting; structure-dependence tests vs exact
  marginal-preserving surrogates; positive/negative/cheat controls
  (smuggler refused by audit, TT_INJECT).
- Poor at: worlds come from completion-friendly classes (low-rank, CP,
  TT, rank-1 sums), so success reduces to known tensor completion
  (WTP-03 report); W1 TRANSFERS near-tautological (same field); W2
  admission pre-selects the phenomenon; structure discovery fails (E2
  G_ID TT 0.20/0.15 vs >=0.70 gate).
- Observables: AC excess over N0-N5 (+ post-data N6), held-out R^2, L2
  success, EFF, correct-structure rate G_ID, LM01 IM-rate/IM-bytes.
- Blind spots: founder concentration (174/181 admitted worlds are mutants
  of 13 founders; effective n=13, W3); no same-class batch null until N6
  post-data (W4); tuning coupling broke E0/E1 controls; Wave A ~10 h for
  181 worlds.
- Notable findings: E0 INDETERMINATE (8fe17208b); E1 INDETERMINATE
  (27e1f1715); E1.5 CLOSE(B) "headroom falsified" (6538058db) -- TT_TUNED
  EFF 8.63 vs LOWRANK 2.03 but C1/C2 fail; E2 INDETERMINATE (553a05d2e);
  WTP-01 REDESIGN, top anomalies a variance-collapse artefact
  (092577f21); WTP-02 mechanical EXPAND overruled to PARK/REDESIGN (one
  specimen = a one-float running mean; ensorain/WTP02_OPERATOR_RULING.md,
  42c190ae3); WTP-03 (bcba874b9 -> a65d27ced) mechanical "CANDIDATE
  PHYSICS FOUND" but all 9 flags are known online completion; post-data
  tuned N6 beats all 9 by 0.2-2.3 AC (ensorain/wtp3/n6_check.py), 0/12
  crossovers replicated.
- Dependencies: numpy, scipy.stats, multiprocessing, pytest; stewards
  Cyclops (M2), Aporia (M1) (ensorain/lm01/STEWARD_RULINGS.md); comms
  EW_DB_HOST=192.168.1.202.
- Portability: MERELY LOCATED (numpy; `python -m ensorain.lm01.launch`
  from a pinned worktree); host coupling is operational only (<=8
  workers, BELOW_NORMAL, stop <6 GB RAM, no launch on M2 while
  Bellerophon's campaign runs).
- Cross-pollination: no archaeon/prometheus imports in ensorain/*.py;
  concepts from archaeon/workspace.py and comms/manifest.py. Shares CWE's
  failure mode (author plants the law class, engine rediscovers it) --
  should BORROW CWE's foreign-holdout protocol and location gate;
  CONTRIBUTE the N6 tuned same-class batch null to CWE. SELECTIVE_PAYS
  use: UNKNOWN (no reference found).

### 4.7 PTE -- Ananke Packet-Tensor Engine (Ananke, M1)

- Name: PTE v1; primitive set PTE-OPS-1, substrate PTE-SUB-1
  (roles/Ananke/pte/DESIGN.md); code prometheus/ananke/ (~4.8k LOC incl.
  tests).
- Status: EXPERIMENTAL. prometheus/ananke first 7b6958b1c 2026-09-24,
  last 4554a2fae 2026-09-26; roles/Ananke 7acc2926c 2026-09-24 ..
  cc98596dd 2026-09-26 (C1b evidence package, on main). STATUS.md stale
  (currency 2026-09-25T00:10Z, still "next: PTE-C1b prereg"). PTE-C2 and
  PTE-SI01 not run.
- Scientific lens: can organised information processing emerge from
  lossy, delayed, superposing packet traffic over a mutable all-integer
  substrate with no neural machinery (roles/Ananke/prompts/
  2026-09-24_charter/01_OPERATOR_MISSION_verbatim.md)? B worlds x N int32
  sites; update laws are 16-opcode straight-line register programs found
  by a declared mutation+truncation GA (DESIGN s0 C4/C5); arrivals are
  summed and counted, no source identity (C3). The varied factor is
  communication physics (loss, latency, decay, cap, topology, fanout).
- Good at: which physics dials gate communication-dependent computation;
  per-carrier causal attribution (C1b resets S, inbox, Kp, w, En, r;
  in-flight flush); transfer across size/topology; bit-exact replay (int32
  saturation, counter-hash RNG, CPU oracle conformance, 145 tests).
- Poor at: addressed/symbolic messaging (superposition hides source);
  graded continuous dynamics (saturation); separating linear-GP search
  strength from substrate capacity; non-linear integration (XOR/FLIP
  null, C1_REPORT s1); hand-built plant viability does not map where
  communication is possible (C1_REPORT s2).
- Observables: held-out accuracy vs no-communication baseline exactly
  0.500 (mirror-paired worlds); labels COMM_DEPENDENT, CAUSAL_SUPPORT,
  REPRODUCED; L1-L4 ladder; per-carrier ablation deltas; state digests.
- Blind spots: C1 packet-ablation window missed the readout tick
  (roles/Ananke/pte/C1_ERRATA.md); mechanism labels _UNRESOLVED where
  positive control could not fire (roles/Ananke/pte/c1b/
  REVIEW_PACKET_PTE_C1b.txt); no independent adversarial review yet
  (requested Kairos #564, Elenchus #565).
- Notable findings: C1 (6,596 rows, 0 failed cells; freeze 362f2189b,
  code eb7c4b40a, prereg 78243a758): RELAY routed-relay laws
  COMM_DEPENDENT + CAUSAL_SUPPORT + REPRODUCED at 0.875-0.893 up to
  N=2304 vs 0.500; rare (8/352 A1 cells), topology-tied (random graph ->
  0.500); cross-family transfer 0; XOR/FLIP NULL (roles/Ananke/pte/
  C1_REPORT.md). C1b (27/27 cells, freeze 5bd6c3945, code 4554a2fae):
  M3 is transport arriving on the readout tick; M2 in-flight memory
  reproduced 3/3 but stored bit != signed payload sum.
- Dependencies: torch, numpy; campaign.py defaults --device cuda (M1
  RTX 5060 Ti per ENGINE_LANDSCAPE); sklearn per ENGINE_LANDSCAPE table;
  operator hold/release chain (prompts/2026-09-26_c1b_operator_release/).
- Portability: MERELY LOCATED on M1 (integer + hash RNG make runs
  bit-exact on any GPU; RunPod named in DESIGN C1; --device flag; CPU
  oracle for small configs). Aether's RunPod ladder already runs its
  conformance suite as a foreign module (6c98b4dae). Hardcoded host
  paths outside launch.py/campaign.py: UNKNOWN (not grepped).
- Cross-pollination: borrows Ensorain's separate-RNG-stream rule (DESIGN
  C2), Cosmos atlas_export form, Aether oracle pattern, Nestor watchdog
  (patterns only). CONTRIBUTE the "ablation window misses readout tick"
  lesson to every perturbation assay; Archaeon's lens runs on it
  (PORTABILITY01_REPORT.md:158).

### 4.8 Archaeon z80atlas + causal lens (Archaeon, M2)

- Name: archaeon/{z80atlas (incl. census/, denovo/, postcampaign/),
  envgate, envgate2, lineage, rie, causal_lens}; seat roles/Archaeon/.
- Status: ACTIVE (lens), world dormant. z80atlas c7610ea19 2026-09-19 ..
  863d34a55 2026-09-23; envgate 58f0463b2 .. 16111cf50 (2026-09-24);
  envgate2 87f51c5ee 2026-09-24 .. 13cdec715 2026-09-26; lineage, rie
  single commit 87f51c5ee 2026-09-24; causal_lens 13cdec715 2026-09-26 ..
  0a5c0895d 2026-09-27 (contract v0.3). RIE-01 staged not frozen
  (roles/Archaeon/RESUME.md:58). Branch deltas (portability01,
  contract-v02) already on main (empty diff).
- Scientific lens: frozen 32-opcode byte VM with COPY op 20 and neighbour
  window base 128, random-tape inflow chambers; topologies soup, grid,
  niches, graph, well-mixed (archaeon/z80atlas/campaign/CAMPAIGN_PACKET.md).
  Distinctive: the ENVIRONMENT is the manipulated variable with organism
  physics frozen, and each birth carries 4 identities -- executor,
  executed material, child contributors, ecological host -- via
  byte-level taint (archaeon/lineage/core.py, taint_vm.py).
  ENGINE_LANDSCAPE s2 (95fff9111): "NOT distinct as a WORLD" (third Z80
  build from the 2026-09-19 directive), "distinct as a METHOD".
- Good at: whether environmental structure causally gates lineage
  establishment; who actually authored a birth; exposing lineage-labelling
  artefacts; cross-engine provenance differentials (PORTABILITY-01).
- Poor at: origination -- host execution amplifies residents only
  (ENVGATE01 s8); parent-chain tracing credits the host; arrival-level
  tests assume independence that takeover worlds violate (s10); "governing
  code" has three referents (WHO/WHERE/WHAT), location != material (break
  B6, archaeon/causal_lens/V02_REGRESSION_REPORT.md:93); symmetric
  recombination makes majority-provenance continuity ill-posed (B1).
- Observables: genetic vs parent-chain establishments (parent-chain 8-42x
  higher, envgate2/VERDICT_2026-09-26.md); copier classes
  EXACT/NEAR/SPAN/INERT/WRITER; births_hosted, takeover, coexistence; RIE
  classes ENV_GATED, HOST_DEPENDENT, liberation, acquisition
  (archaeon/rie/world.py).
- Blind spots: not indexed by Atlas (see s3); evidence off-repo on
  C:\Prometheus-data, off-machine copy BLOCKED (ENVGATE01 s1); frozen
  analyze.py KeyError worked around by wrapper (envgate2 VERDICT).
- Notable findings: z80atlas campaign 101,003 runs, 0 errors, 31,522
  families, 26 spontaneous-replication flags, positive controls PASS
  (CAMPAIGN_PACKET.md, d50f5710a); ENVGATE-01 re-adjudicated
  GATING_PARTIALLY_SUPPORTED (copier-founded establishments U 47, SHAM 45,
  BLOCK_128 18, RESCUE 1, BAND 1; causal unit = input window ~120-131;
  rescue = one takeover artefact) (archaeon/envgate/ENVGATE01_REVIEW_
  2026-09-24.md, ADJUDICATION_ADDENDUM, 16111cf50); host-mediated
  reproduction -- 26/63 INERT hosts gave births, 23 exact resident
  copies, all by foreign execution; ENVGATE-02 WINDOW_NOT_SUPPORTED
  (c5ba19571); PORTABILITY-01 and contract v0.2 PORTABLE_WITH_DOMAIN_
  LIMITS, breaks B1-B7 (37145999d, 949b9ba4d).
- Dependencies: numpy CPU + proteus.foundry.prng (archaeon/z80atlas/
  engine.py:12, tasks.py:11); no SFE/PEW/Viv/Postgres; run_campaign.bat
  (Windows launcher).
- Portability: world MERELY LOCATED; the lens is DEMONSTRATED portable --
  ran unchanged via adapters on BEE z80atlas (845 runs, 28.96M births),
  NPE (36 replays) and non-Z80 PTE (5e22ebd58, PORTABILITY01_REPORT.md:
  158), limited by persisted provenance (BEE abstains on ~1/3 births).
- Cross-pollination: the lens is the clearest existing cross-engine
  instrument; complements Crius (existence vs accessibility) and NPE P-11
  (causal copy). Proposed Atlas varied=/observed= field
  (ENGINE_LANDSCAPE s4), unapplied.

### 4.9 Ares -- pressure-engineering sandbox (Ares, M2)  [missed by ENGINE_LANDSCAPE]

- Name: Ares, "pressure engineering sandbox" (ares/ARES_FIRST_REPORT.md,
  bb133d083 2026-09-19); ares/ ~3.5k LOC Python (substrate.py, search.py,
  worlds.py, carriers.py, ...).
- Status: DORMANT (PARKED). ares/ and roles/Ares first eed9c7121 /
  d1f22735a 2026-09-19, last 3f68be2b9 2026-09-25. roles/Ares/STATUS.md
  currency 2026-09-25: cycle 2 closed, gates A/B OPEN, C SHUT ->
  CONTINUE_RECOMMENDED (recommendation only); no cycle 3 without
  operator.
- Scientific lens: an ABSTRACT PRESSURE in the world -- nothing in the
  objective or substrate -- changes the KIND of machinery a dumb search
  finds (ares/DESIGN_C0.md s1). Organisms: generic graph organisms (8
  hidden slots, ops ADD MUL MAX MIN THRESH GATE TANH DIFF CONST,
  optional keep/plasticity/recurrence), GA P=128 G=120; worlds W1-W13
  each run pressure present/absent/shuffled with identical substrate and
  seeds (DESIGN_C0 s2).
- Good at: which world pressures induce memory-like machinery and via
  which carrier (activation, keep, plasticity, recurrence); mechanism
  substitution under forbid-arms; dissection + causal transplant of
  evolved champions.
- Poor at: only toy worlds and one search regime; carrier choice depends
  on parameterisation basin width (cycle 2), so "what evolution prefers"
  is confounded with how the substrate parameterises each carrier;
  no reproduction/ecology (GA outer loop only).
- Observables: held-out world reward vs preregistered floors from
  ares/runs/baselines.json; carrier class (ACT etc.); no_memory /
  forbid_recurrence collapse; viable-region width per carrier.
- Blind spots: GA seeds 1-3 reproduce earlier lineages byte for byte, so
  "10 seeds" was 7 independent (ARES_CYCLE1_REPORT s1); held-out selection
  bias and best-of-N swap statistic defects found in cycle 2 (flipped gate
  C); basin-width explanation is POST-HOC, hand-wired (STATUS.md).
- Notable findings: cycle 0 -- W4 hidden regime produced a necessary,
  localised activation-memory mechanism (champions 40/40, no-memory ->
  2.6, plasticity removal no effect) and the sweep falsified 3 of its own
  controls (ARES_FIRST_REPORT s0); cycle 1 (130 runs, prereg 3ea24dda8) --
  W4/W5/W12 MECHANISM_DIVERSE, function replicates 7/7 but structure
  idiosyncratic (ARES_CYCLE1_REPORT.md, 8ba05b2c8); cycle 2 (190 runs,
  prereg ab137f52b) -- all three carriers individually sufficient;
  recurrence wins by basin width (14/23 viable, saturating) not peak
  (keep 33.75 in a 3/25 sliver); forbid_recurrence costs ~10 generations
  only; cycle 1's "plasticity 0/10 on W4" did not replicate (4/10)
  (ares/ARES_CYCLE2_REPORT.md s0, 3f68be2b9).
- Dependencies: numpy + stdlib only (import census of ares/*.py); CPU;
  comms EW_DB_HOST=192.168.1.202 (roles/Ares/RESPONSIBILITIES.md:117).
- Portability: MERELY LOCATED on M2 (numpy, seeded, receipts carry
  hashes). UNKNOWN whether any run was replayed off-host.
- Cross-pollination: the present/absent/shuffled pressure design is the
  environmental twin of Archaeon's ENVGATE arms and of Crius's rung
  ladder; basin-width analysis would help BEE/NPE explain why LDIR/1-byte
  encodings dominate. Not in Atlas registry at all.

### 4.x Engines with evidence but no full card (why)

- Crius (crius/, M2): full card material exists but it is a closed
  2-campaign study. Own substrate (4-tuple mod-16 hidden-op world, 8-reg
  bytecode Player VM, costed Workspace; crius/world.py, vm.py,
  workspace.py; stdlib only, no SFE import). CLOSED 2026-09-23 (7069c0ce6
  "Campaign 2 CLOSED -- ACCESSIBILITY FRONTIER MAPPED"): reuse exists and
  pays (block control 46.1 vs 20.7; typed transplant 6/6/6 vs 1/1/0) but
  0/36 runs across rungs A-D reached it by search
  (crius/CRIUS_C2_TERMINAL_REVIEW.md). Lens = existence vs accessibility.
  Status HISTORICAL/closed; registered in Atlas with 0 experiments.
- Aphrodite (roles/Aphrodite/engine, M4 "harry1"): deterministic code
  worker, machinery-vs-state separated by construction; A17 campaign ran
  2026-09-26 (report 4f937e88f on origin/aphrodite/a16-campaign-
  2026-09-26, unmerged): BOUNDED_RSI = NO, S1_NECESSITY SUPPORTED (3/3 vs
  0/3), E2/E3 UNTESTABLE; accel canary 0/1,157,192 mismatches
  (bfbc5859e). Stdlib only; portable. It is an improver-of-improvers
  engine, not a world engine; not in Atlas.
- Herakles EVCA (herakles/evca, herakles/ca_stream; 3466481b9
  2026-09-08 .. 6c9c55bfb 2026-09-16): pure library for EvCA density
  classification (herakles/evca/core.py "PURITY CONTRACT"); a CA
  reproduction lens. Too little campaign evidence located for a card.

## 5. Cross-engine observations (for the SFE retrospective)

- Recurring failure mode across worlds: the headline result is later
  reduced by the engine's own forensics to an instrument or authoring
  artefact -- NPE 1,031 -> 57 replicators (splice/fidelity-after-mutate),
  BEE 72 h campaign 5/5 flag classes collapsed (P1 migration defect),
  Aether +128% change-rate from a 250-tick-stale comparator, WTP-03 9/9
  flags = known tensor completion, CWE law A = hand-written economics,
  PTE ablation window missed the readout tick, Crius invocation log
  recorded R0, Ares best-of-N swap statistic flipped gate C. SFE's
  prediction-before-observation ledger would not have caught any of
  these (they are mechanism/instrument errors, not ordering errors), but
  its loser-keeping families and executed-config attestation are absent
  from every post-SFE engine except CWE (receipted predictions) and BEE
  (receipts, replay).
- Post-SFE engines abandoned the service/ledger model: every card after
  SFE is a local, deterministic, file-receipted Python package (stdlib,
  numpy, or torch/CuPy), and portability is "merely located" for all but
  NPE generation 1 (Redis/FalkorDB/CUDA/WSL) and Aether >=16384^2 (A40).
  SFE's own core is portable; its DEPLOYMENT (per-IP certs, Windows
  launcher, off-repo ledger) is what made it host-bound.
- The only instrument already running across engines is Archaeon's
  causal lens (BEE, NPE, PTE via adapters). Atlas is the only
  cross-engine index but sees 5 of ~19 engine rows, with 2-6 days lag.
- Convergent lenses worth one shared protocol: environment-as-variable
  (Archaeon ENVGATE, Ares present/absent/shuffled, Ananke physics dials);
  existence-vs-accessibility (Crius) vs origination-vs-amplification
  (Archaeon) vs causal-copy certificate (NPE P-11); author-separated
  holdouts (CWE) vs post-data tuned null (WTP N6).

## 6. Open items / UNKNOWN

- SFE current liveness on M2 :8811 (no record after 2026-09-24).
- Host of Theophrastus, Alien Circuitry, Incubation; owners of
  alien_circuitry/, incubation/.
- Charon, Chiron, Serendipity Foundry D commit dates (not computed).
- NPE generation-1 consolidated findings ledger (not located).
- Whether any Ares or Crius run was replayed off-host.
- Seats matching engine keywords only in STATUS files (Aporia, Coeus,
  Cyclops, Elenchus, Eos, Mnemosyne, Pheme, Polyhymnia, Rhadamanthus,
  Talos) were not examined for engines.
