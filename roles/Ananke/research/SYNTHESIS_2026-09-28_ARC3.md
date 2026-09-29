# Ananke ARC3 (2026-09-28): autonomous PTE research portfolio, integrated synthesis

Starting state: SYNTHESIS_2026-09-28_ARC2.md. Priorities were set from
evidence (ARC3_PRIORITIES.md). Workers W-G..W-L ran from neutral handoffs,
with PLANs frozen before their runs. Reports were deposited verbatim with
provenance (deposit.py). Canonical backlog: BACKLOG_V2.md.

1 WHAT CHANGED
- The strongest new compression (H6, CROSS_THREAD_COMPRESSION.md): SEARCH
  REACHABILITY, NOT PHYSICS, bounds what PTE shows. Four independent lines
  point the same way:
  - fixed-rule latches beat switching champions (W-H);
  - selective retention is never evolved though a plant solves it (W-L);
  - the echo model designs mechanisms search never produced (T-DE-1);
  - the substrate can retain where champions don't (W-G).
  PTE results are statements about PHYSICS x SEARCH.
- Carriers are trajectories, not places (W-I, 33 specimens). Census-"SITE"
  relays carry the bit in the channel first. Site-only retention is a HOLD
  phenomenon.
- Receiver semantics matter only through AGGREGATION GAIN, filtered by the
  reader's invariances (W-J).

2 WHAT WAS FALSIFIED (interpretations held at the start of ARC3)
- "All 14 JOINT cells are phase mixtures (site_acc + chan_acc = 1)". The sum
  is a mirror-pair IDENTITY. By phi only 3/7 are mixtures (W-I). My
  designed-echo "mixture signature" claim is retracted.
- "The real PTE-Aether axis is the receiver operator": too strong. It is
  operator x aggregation gain (W-J).
- "PTE messages can never rewrite the program": false. SETRULE/WIMM take
  arrival operands, so code change is receiver-gated (W-J).
- "PTE adds arrivals": the operator is a dial (sum / saturate / aloha)
  (W-J).
- "Never-read scars": fresh2/3's w-scar IS read, as sign-scrambled
  interference (W-G).
- "PTE lacks a persistent substrate": false. Plants retain, even latently
  (W-G).
- "Identical arm => the intervention never took" and "reach is the remedy"
  (W-K). Identical outputs also describe true nulls; reach covers only
  windowed arms.
- "Champions don't retain because tasks never reward it": incomplete. The
  search builds integrators even on HOLD (W-L).

3 RETENTION
There is no nontrivial retention regime in the evolved champions
(preregistered, replicated in two namespaces; 5 controls valid,
including a latent Kp store that the L4 probes detect; W-G). When the task
rewards it, retention IS reachable, but as INTEGRATION (S accumulates the
whole cue history). Selective lag-2 storage was not reached, although a
16-line plant solves it (W-L). SI01 is CLOSED for the current champions.
Its successor is T-RET-SEL (a selectivity criterion; an anti-integrator
task).

4 SETRULE
Dynamic rule switching COMPRESSES; it does not EXPAND (5/5 cells, W-H).
Roles found:
- an event-triggered branch (a leaky timer);
- a phase-selected write-enable clock (sample/hold);
- a one-tick relay specialization.
Every switch lasts 1-2 ticks, and r never carries the bit. The free,
decay-free rule register goes unused.

5 CARRIER TRAJECTORIES
Recurring motifs across physics:
- site-only retention (HOLD, 8/8);
- channel -> latch;
- channel-only delay (delta 4);
- travelling wave;
- source-presence;
- payload-value.
The reader and physical axes dissociate (6 presence-as-content
champions). Cue-dependent traffic and routing that nothing reads are
common. Robustness vs trajectory was INCONCLUSIVE by the frozen rule (the
panel had no site-only specimens). Exploratory: SLACK (ticks from the last
channel phase to the readout) predicts latency tolerance (rho .52), queued
as a preregistered test (T-CT-3').

6 M2 MODEL
The designed calibration SUPPORTS it: 7/7 designs FIT (MAE .012-.023),
including a deliberate failure at the trained gap and comb-shaped
intervals. The instruments read the designed channel -> site trajectory
at the right time. The one instrument prediction I got wrong (the handoff
tick) is recorded. "Does search rediscover model designs?" was NOT queued
(a latch confound would make a null uninformative); the design requirement
is stated.

7 PTE <-> AETHER
What survives: the one-tick computable-function table per operator (sum =
nomographic; saturate = normalized mean; aloha = erasure; arbitrate = one
sample, a voter process). Designed plants match it (lossless: SUM .823 =
SAT, ARB .727, ALOHA .500). At C1 physics the operator is behaviourally
irrelevant (29/32 presence codes). With lossless physics the first pure
superposition count-majority code appeared, and it is exactly 0.500 under
every other operator. Aether proposals A-J1..4 are packaged for its
owner; nothing was run on Aether.

8 INTERVENTION REACH
There is no universal check (W-K, 21 fixtures x 16 checks with valid
twins).
- Best single check: a must-flip PLANT through the arm's own code (J .70,
  0 false alarms).
- Minimum zero-false-alarm cover: {plant, applied count, could-fail
  counter-plant}.
- Nulls need the plant plus bookkeeping. Effects need a counter-plant plus
  an arm-diff or sham.
Built as lens.verify_reach (REACHED / UNREACHED / NOT_VERIFIED;
known-answer tests). The frozen C1b intact() treats NOT_APPLICABLE as
intact, so new preregs should use verify_reach.

9 EXTERNAL RESEARCH that changed things
- Multiple-access channel theory and nomographic over-the-air computation
  (the operator table).
- The voter model (arbitration cannot compute majority without memory).
- Coreworld/Tierra write privileges (sender-addressed vs receiver-gated
  code).
- Mutation-testing RIPR and manipulation checks (intervention reach).
- Buonomano-Maass hidden state, and bundled-data clocks (the SETRULE roles).

10 DELEGATION: where workers disagreed with me (and won)
- W-I: the sum identity.
- W-J: the operator dial, receiver-gated code, the aggregation gain.
- W-G: substrate retention, read scars.
- W-K: identical arms, reach scope.
- W-L: incentive is not the whole story.
- W-H: no disagreement needed; it had not read my files.
Six workers; every report carried a DISAGREEMENTS section. Context
contamination was logged where it happened (W-G, W-J).

11 BACKLOG
Closed or answered in ARC3: T-RET-2, T-BR-1, T-CT-2, T-RS-1, T-X-4,
T-DE-1, T-RET-EVO. Each split into sharper successors. The new top tier is
T-REACH-GAP (the physics-expressible vs search-reachable gap).
Research-ready:
- T-RET-SEL;
- T-CT-3' (slack);
- T-INS-6 (phi + single-trial swap + promote traj.py);
- T-SWAP-LOWACC;
- T-WJ-1 (aggregation-gain sweep) and T-WJ-2 (4-operator fingerprint);
- T-H3 (a flattening compiler);
- T-K3 / T-K5 (the plant library; blind fixtures).

12 QUEUE / LEASES
Waited:
- W-I's GPU job (the GPU was busy all session). It ran the IDENTICAL
  frozen experiment on CPU under a cpu8 lease, so there was no weaker
  substitute.
- W-L's 10 searches: queued behind W-J, then ran on the GPU as written.
Cancelled as stale: none. Not queued, deliberately: T-REDISCOVER (a
design flaw found before queueing).
Queue pathologies observed:
- none stale;
- one near-miss: W-I's queued GPU job was superseded by the CPU run, and
  it was marked VOID rather than executed twice.
Leases (host SKULLPORT; fallback mechanism: host lease file + comms record;
the Redis bus is still down):
- W-G none;
- W-H gpu 2ce85284 (released);
- W-I cpu8 (released);
- W-J gpu x2 (#777/#781, #782/#783, released);
- W-K none;
- W-L gpu (released);
- Ananke none this arc.
Nestor holds cpu8 (X-A3-FAIR) at the end of the arc; that is Nestor's
lease. ALL ANANKE LEASES ARE RELEASED.

13 RESEARCH-READY WORK (an idle agent can begin immediately)
MACHINE_WORK.md, updated. It has 6 original CPU blocks + 6 new ones
(T-RET-SEL, T-INS-6, T-CT-3', T-SWAP-LOWACC, T-WJ-2, T-H3), all
self-contained. More research-ready work exists than workers.

14 PTE'S VALUE (what no other Prometheus lens gives)
- EXACT counterfactuals on channel state: bit-exact mirror twins,
  carrier swaps, designed plants.
- The only engine where the receiver operator is a DIAL, so operator
  effects can be isolated inside one engine.
- A place where a zero-parameter mechanistic model predicts evolved
  behaviour (M2) and designs new mechanisms.
- A measured, quantitative gap between what physics allows and what
  search reaches (H6), which is directly relevant to any
  physics-of-intelligence claim built on evolved specimens.
What PTE does NOT give: persistent memory in evolved champions, rich
composition (XOR/FLIP NULL), or individuals/heredity.
Demotion candidates if insight stalls: more C1-style census campaigns
(diminishing returns; the instruments are now the value).

15 HITL
No operator decision required. The next autonomous research arc is already
available (T-REACH-GAP, T-RET-SEL, T-CT-3', T-INS-6 and the MACHINE_WORK
blocks).
Optional program-level note, not a decision: H6 suggests that PTE's most
consequential next question is about SEARCH (diversity / novelty /
curriculum, backlog ANANKE-14) rather than new physics dials. That choice
can be made autonomously within PTE.

## CORRECTION (2026-09-29, W-N)
W-L's swap verdict CHANCE (s3 above and W-L REPORT "formal verdict is
CHANCE ... a limit of the rule") was a sample-size effect: at 512 worlds the
absolute rule gives FLIP (S carrier, z ~ -1) on every W-L champion.
Recorded CHANCE verdicts from 64-world designs are not mechanism evidence
until re-run at adequate sample size (backlog T-SWAP-AUDIT).
