# A4: Human intervention, coordination load, and tool reuse (Prometheus fleet, 2026-09-11 to 2026-09-30)

Analyst: read-only research pass (Aletheia-M4 tier sub-agent). Repo: `C:\Prometheus-worktrees\aphrodite-harvest` @ 38e323c0c (origin/main, 2026-09-30 19:55 -04:00).
Data: `comms_messages.json` (1,198 msgs, ids 2..1198, 2026-09-11 to 2026-10-01 00:xx UTC), `gitlog.tsv` (10,337 non-merge commits), plus the repo tree (`roles/*/prompts/`, `ops/`, code).
All scripts are in `scratchpad/data/a4/` (`comms_an.py`, `prompts_an.py`, `prompts_cls.py`, `reuse.py`, `dups.py`). Every number below comes from those scripts or from the cited message or commit. Where I judged something by hand, I say so.

---

## 0. Headline findings

1. **The operator never posts to comms.** No message has sender `operator` or `James`. Operator intervention has to be measured from two other sources. The primary one is the **verbatim operator-prompt archive** (`roles/*/prompts/<date>_<slug>/` dirs that contain an `OPERATOR_*` file): **177 operator prompts across 41 seats in 20 days** (strict set), which is **8.9 per calendar day** and **0.25 to 1.7 per active seat per day**. The secondary source is comms relays: 239 of 1,198 messages (20%) cite operator/MWO/CWO authority.
2. **Most operator interventions redirect the science, not unblock it.** By directory-name classification: redirect science 101 (57%), approve a gate 36 (20%), infrastructure/process 34 (19%), correct an error 3, unblock 3. Corrections and unblocks are under-counted, because they are usually embedded in long directives (see 1.2 caveats).
3. **Coordination share is 25% of all messages overall. It spikes to 38 to 41% on heartbeat-mandate days** (09-26: the LM01 steward heartbeats; 09-30: the CWO-B/C hour-heartbeats, 64 heartbeat messages in one day). That pattern is a policy artifact, not a workload signal.
4. **Waits.** Of the question or blocker messages, 52% get a visible cross-seat response, with a median of 0.95 h. Operator decisions return in batches through Aporia-authored MWOs, not as replies. The canonical case is **D2 #925 ("root of trust") at 8.4 h** (09-28 23:17 to MWO-0004 at 09-29 07:44). In that time Nestor/Odysseus ran **10 more repair and re-audit rounds** that each re-reported S1 as open.
5. **The D2 firewall audit took 13 audit rounds in about 20.5 h** (12 FAIL, 1 PASS). About 8 rounds found a genuinely new blocking defect class, about 2 found variants of an earlier class (key-use ordering), and **2 (v9, v11) were pure re-litigation of S1**, which was waiting on the operator.
6. **Stale-state incidents: 12 catalogued on 09-28 to 09-30.** They include Artemis self-promoting for about 2 h 15 m (#1134); Odysseus and Bellerophon auto-promoting under a superseded CWO (#1104, #1112); Nestor's stale scheduled task that destroyed 10/11 sample files (#943); census false `not_live` for Aphrodite, which had committed 3 h before the census; and **operator direct-chat directives overriding the CWO for at least 4 seats** (Ensorain #1111, Cosmos #1103, Theseus #1125, Tyche).
7. **Reuse is low and concentrated.** The real cross-seat instrument imports are dominated by a few providers: Proteus' `proteus.foundry` (Archaeon 83 files, Nestor 5, Techne 6, Vivarium 4, Artemis/Odysseus/Harmonia), Archaeon (19 consuming seats, mostly via the 09-11 D-23 workspace helper), Herakles, and Bellerophon's `prometheus.z80atlas` (Odysseus 11). Shared infrastructure is used **by CLI far more than by import**: all 55 comms senders use comms, but only 8 seats import it, and only 4 import `fabric`.
8. **Duplicated reinventions are common.** Lease: 4 separate authorities were built in about 30 h (Ananke's Redis-bus helper 09-27, Nestor's host-file+comms lease 09-28 01:20, Aphrodite's jsonl ledger 09-28 01:36, plus `fabric` Attempts), then collapsed into `fabric/lease_compat.py` by operator ruling at 09-28 21:49Z. Aphrodite's M4 ledger was never migrated. Prereg/manifest writers: **19 owners** write their own freeze/manifest functions, and only **6 of 173** matching files use `comms.manifest`. The D-23 `workspace_guard.py` was copy-adapted into 5 seats (line-similarity 0.63 to 0.75) instead of being imported. `sha256_file` was re-implemented by 7 owners and heartbeat writers by 8 seats.

---

## PART 1: Human intervention and coordination load

### 1.1 Operator-originated directives: where they live

| source | what it captures | count | notes |
|---|---|---|---|
| `roles/*/prompts/2026-09-1x..3x_*/` dirs with an `OPERATOR*` file (or dir name containing `operator`) | verbatim operator chat, committed by the receiving seat | **177 strict** (192 loose) | loose adds 15 dirs matched only by text (seat-to-seat prompts, ACKs, steward directives); I excluded those by filename rules |
| ops/work_orders MWO-0001..0004, ops/fleet CWO-2026-09-30 / B / C | fleet-wide work orders authored by Aporia/Cyclops *from* operator text | 4 MWO + 3 CWO | each CWO is also archived as an Aporia prompt dir, so it is not double-counted |
| comms messages citing operator authority (regex in `comms_an.py`, OPR) | relays, adoptions, citations | 239 / 1,198 | many are citations, not new interventions |
| comms messages addressed to recipient `operator` | seat -> operator asks/reports | 75 (Nestor 33, Odysseus 18, Aether 7, Archaeon 6, Harmonia 5, Hermes 3, Clymene 2, Artemis 1) | 60 of 75 fall on 09-28/09-29 (D2) |

All 177 strict prompts have distinct text hashes (no directive was filed verbatim into two seats). Fleet-wide orders such as the 09-30D "inference harvest" were personalised per seat (Aporia, Ananke, Nestor, Atlas each hold a different text).

### 1.2 Operator interventions per day (verbatim archive, strict)

Classification is by directory slug, with rules in `prompts_cls.py:NAME` and 8 manual overrides (`OV`). Day = local commit date of the first file in the dir.

| day | operator prompts | seats touched | redirect science | approve gate | infra/process | correct error | unblock | active seats (comms or commit) | prompts per active seat |
|---|---|---|---|---|---|---|---|---|---|
| 09-11 | 21 | 15 | 4 | 6 | 11 | 0 | 0 | 37 | 0.57 |
| 09-12 | 5 | 1 | 5 | 0 | 0 | 0 | 0 | 5 | 1.00 |
| 09-13 | 6 | 3 | 6 | 0 | 0 | 0 | 0 | 6 | 1.00 |
| 09-14 | 2 | 2 | 2 | 0 | 0 | 0 | 0 | 8 | 0.25 |
| 09-16 | 6 | 3 | 4 | 1 | 1 | 0 | 0 | 12 | 0.50 |
| 09-17 | 12 | 8 | 8 | 1 | 2 | 1 | 0 | 11 | 1.09 |
| 09-18 | 22 | 8 | 17 | 5 | 0 | 0 | 0 | 13 | 1.69 |
| 09-19 | 12 | 7 | 10 | 0 | 2 | 0 | 0 | 12 | 1.00 |
| 09-21 | 5 | 4 | 4 | 1 | 0 | 0 | 0 | 4 | 1.25 |
| 09-23 | 12 | 6 | 7 | 5 | 0 | 0 | 0 | 12 | 1.00 |
| 09-24 | 14 | 7 | 6 | 6 | 1 | 0 | 1 | 11 | 1.27 |
| 09-25 | 7 | 5 | 2 | 0 | 4 | 0 | 1 | 20 | 0.35 |
| 09-26 | 10 | 7 | 3 | 3 | 3 | 0 | 1 | 12 | 0.83 |
| 09-27 | 9 | 4 | 6 | 1 | 1 | 1 | 0 | 6 | 1.50 |
| 09-28 | 9 | 6 | 6 | 1 | 1 | 1 | 0 | 12 | 0.75 |
| 09-29 | 7 | 3 | 1 | 3 | 3 | 0 | 0 | 14 | 0.50 |
| 09-30 | 18 | 10 | 10 | 3 | 5 | 0 | 0 | 20 | 0.90 |
| **ALL** | **177** | **41** | **101** | **36** | **34** | **3** | **3** | | |

09-15, 09-20 and 09-22 had zero operator prompts and only 2 active seats each. When the operator is away, the fleet mostly idles. That is the strongest evidence that operator availability gates throughput.

Shape over the window:
- **09-11 is setup and re-seating.** 11 of 21 prompts are infra/process: seat adoption, reactivation, the comms revival, D-23 workspace rules.
- **09-12 to 09-24 are science-direction waves.** Techne batch charters on 09-12 and 09-13; SFE campaigns 1 to 6, refinery and ASAL on 09-16 to 09-19; Ensorain E1/E1.5/E2/WTP authorizations and Cosmos C3 on 09-23 and 09-24.
- **09-25 to 09-30 shift toward governance.** Cyclops/Aporia pairing (09-25); the steward freeze, sign-off release and "direct operator control" for Nestor that *retires* Aporia/Cyclops stewardship (09-26); MWO-0002/3/4 (09-29); then CWO-2026-09-30 / B / C, which *re-instates* Aporia as dispatcher (09-30). Governance authority flipped twice in 4 days. That flip is a direct cause of several stale-state incidents in 1.5.

### 1.3 Operator interventions per seat (top 20) and normalisation

| seat | operator prompts | comms msgs sent | seat-prefixed commits 09-11..30 | commits per operator prompt | class mix (sci/gate/infra/corr/unbl) |
|---|---|---|---|---|---|
| Archaeon | 20 | 168 | 101 | 5 | 15/3/2/0/0 |
| Techne | 16 | 47 | 78 | 5 | 14/2/0/0/0 |
| Aporia | 12 | 127 | 62 | 5 | 2/4/6/0/0 |
| Aphrodite | 11 | 18 | 134 | 12 | 6/5/0/0/0 |
| Ensorain | 10 | 42 | 125 | 12 | 3/7/0/0/0 |
| Nestor | 10 | 94 | 138 | 14 | 6/2/1/0/1 |
| Cosmos | 8 | 17 | 86 | 11 | 4/4/0/0/0 |
| Odysseus | 8 | 51 | 78 | 10 | 4/0/3/1/0 |
| Nyx | 7 | 51 | 116 | 17 | 7/0/0/0/0 |
| Artemis | 6 | 67 | 71 | 12 | 4/0/1/1/0 |
| Atlas | 6 | 30 | 37 | 6 | 5/1/0/0/0 |
| Bellerophon | 6 | 29 | 209 | 35 | 6/0/0/0/0 |
| Harmonia | 6 | 68 | 147 | 24 | 5/1/0/0/0 |
| Ananke | 4 | 59 | 111 | 28 | 2/1/1/0/0 |
| Tyche | 4 | 1 | 21 | 5 | 3/0/1/0/0 |

(The full 41-seat table is in Appendix B. The class mix shown here comes from the classified set after overrides.)

**Reading.** "Commits per operator prompt" is a crude autonomy ratio. Bellerophon (35), Ananke (28) and Harmonia (24) run long on each directive. Archaeon, Techne, Aporia and Tyche (about 5) are steered closely. For Techne the reason is that each harvest batch is its own operator charter. For Aporia, its prompts *are* fleet orders.

**Explicit corrections, identified by hand** (the dir-name classifier finds only 3, and the text-flag regex had about 10 to 20% precision on a 10-sample spot check, so I discarded it):
- Proteus 09-17 `repair_order`: "Campaign 4 science does not begin yet... FIX THE LAB, THEN FREEZE IT."
- Artemis 09-28 `operator_challenge`: "Do not optimize for backlog size... Optimize for epistemic movement."
- Odysseus 09-27 `freeze`: "Let's freeze this and pivot... more design is needed by me."
- Nestor 09-26 `direct_operator_control`: retires Aporia/Cyclops stewardship.
- #985 D2 time box: "lets see if we can settle D2. Time box it. 2 hours or we pause it."
- CWO-C s4/s11: no self-promotion, sync before launch. This was written directly in response to Artemis' violation.
- Metis 09-11 seating: records that the seat "ran git pull in the canonical checkout... violated s1 and s3".

### 1.4 Coordination overhead by day (comms)

Category rules: ack/broadcast are kinds. Heartbeat/census and adoption/state come from subject keywords. Report is split science, infra or other by keyword density. UTC day.

| day | n | seats | ack | bcast | heartbeat/census | adoption/state | tasking | question | ruling | r:science | r:infra | r:other | **coord share** | **science share** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 09-11 | 191 | 34 | 19 | 5 | 8 | 35 | 16 | 10 | 9 | 48 | 30 | 11 | 35% | 25% |
| 09-12 | 35 | 5 | 1 | 1 | 2 | 0 | 4 | 4 | 1 | 18 | 3 | 1 | 11% | 51% |
| 09-13 | 12 | 2 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 11 | 0 | 0 | 0% | 92% |
| 09-14 | 24 | 7 | 0 | 1 | 0 | 1 | 7 | 2 | 3 | 4 | 4 | 2 | 8% | 17% |
| 09-15 | 2 | 2 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 50% | 50% |
| 09-16 | 58 | 11 | 7 | 0 | 1 | 6 | 9 | 0 | 4 | 14 | 17 | 0 | 24% | 24% |
| 09-17 | 79 | 9 | 8 | 2 | 1 | 2 | 8 | 4 | 1 | 23 | 29 | 1 | 16% | 29% |
| 09-18 | 81 | 9 | 5 | 4 | 1 | 6 | 13 | 0 | 1 | 39 | 11 | 1 | 20% | 48% |
| 09-19 | 42 | 12 | 6 | 0 | 1 | 2 | 4 | 1 | 0 | 15 | 13 | 0 | 21% | 36% |
| 09-21 | 12 | 4 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 9 | 0 | 0 | 0% | 75% |
| 09-23 | 10 | 5 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 3 | 2 | 3 | 0% | 30% |
| 09-24 | 17 | 7 | 3 | 0 | 0 | 1 | 2 | 1 | 0 | 3 | 6 | 1 | 24% | 18% |
| 09-25 | 83 | 14 | 10 | 1 | 9 | 3 | 9 | 3 | 4 | 29 | 14 | 1 | 28% | 35% |
| 09-26 | 94 | 9 | 9 | 2 | **25** | 0 | 1 | 1 | 10 | 38 | 6 | 2 | **38%** | 40% |
| 09-27 | 24 | 6 | 0 | 4 | 0 | 0 | 2 | 1 | 0 | 6 | 10 | 1 | 17% | 25% |
| 09-28 | 145 | 7 | 8 | 14 | 2 | 1 | 16 | 6 | 2 | 58 | 29 | 9 | 17% | 40% |
| 09-29 | 114 | 12 | 0 | 4 | 0 | 2 | 6 | 2 | 16 | 58 | 24 | 2 | 5% | 51% |
| 09-30 | 174 | 20 | 3 | 3 | **64** | 2 | 23 | 4 | 4 | 55 | 14 | 2 | **41%** | 32% |
| **ALL** | 1198 | 55 | 79 | 42 | 115 | 61 | 126 | 39 | 55 | 432 | 212 | 37 | **25%** | **36%** |

Notes:
- **The 09-30 spike is mandated.** CWO-B (#1080 to #1096, 17 per-seat prompts at 09:16) requested hour-heartbeats, CWO-C added VISIBILITY_STALE pings (#1141 to #1146), and those prompts plus their replies make up the 64 heartbeat/census messages.
- **The 09-26 spike is also mandated.** It comes from the Ensorain to Aporia/Cyclops LM01 steward heartbeat cadence ("heartbeat is a report cadence, not a work cadence", #615).
- On 09-29 the share is 5% coordination but 51% "science". Most of that "science" is the D2 audit and repair loop (security engineering scored as science by keyword), so the science share is inflated.
- 143 of 1,198 messages contain "heartbeat" somewhere.

### 1.5 Waits: question/blocker to first response

The population is 86 messages: kind=question (41) plus subject markers BLOCKED / blocker / awaiting / OPERATOR DECISION. A response is the earliest later message from another seat that either has `reply_to` = id or cites `#id` in its subject or first 800 characters of body.

| population | n | responded in window | median h | p75 h | p90 h | max h |
|---|---|---|---|---|---|---|
| all | 86 | 45 (52%) | 0.95 | 3.78 | 14.4 | 109.4 |
| seat-to-seat | 69 | 36 | 0.84 | | | 109.4 |
| operator-addressed / operator decision | 17 | 9* | 0.95* | | | 3.8* |

\* **This figure is invalid for operator waits.** The "first response" to an operator ask is usually *another seat* citing the ask. The operator answers out-of-band (direct chat to verbatim prompt to MWO). Operator latency measured by hand against the prompt archive:

| ask | asked | operator answer (artifact) | latency | what happened meanwhile |
|---|---|---|---|---|
| #925 Nestor: D2 root of trust (a/b/c) | 09-28 23:17 | MWO-0004 gate clearance (Aporia prompt 09-29 07:44); #992 "#925 resolved" 07:57 | **8.4 h** (overnight) | 10 repair/audit rounds v3 to v12 each carried "S1 still open (#925)" |
| #915 Nestor: is MWO-0001 operator-approved? (no verbatim record) | 09-28 22:17 | MWO-0002 approval verbatim 09-29 02:57 | about 4.7 h | Nestor acted only on the items covered by its standing directive |
| #985 operator time box (unsolicited) | 09-29 ~07:00 | n/a | n/a | an unblock by deadline, not by answer |
| #1044 Harmonia E-003 BEE verdict-language escalation | 09-30 05:04 | still open in CWO-C s23 at 13:55 | >15 h at end of window | flagged "do not allow to block unrelated work" |
| promexec privileged install (Odysseus/Aether) | review cleared 09-30 05:30 (#1052) | still open at 18:09 (#1182) | >12.6 h | Odysseus stays BLOCKED, Aether's E-012 depends on it |
| Cosmos C4 steps 2 to 5 Q1/Q2 (#1107) | 09-30 09:55 | partial: operator C4 review prompts 10:23 and 11:27 | about 0.5 to 1.5 h | Ananke R-STAT Phase 2 waits on Cosmos |

Of the seat-to-seat asks, 33 have no visible response in the window. Many are broadcasts ("volunteers wanted" #814/#815), FYIs, or asks to parked seats (Eos to Apollo/Nyx/Icarus #76 to #78 on 09-11, after which these seats went dormant).

**Cross-seat waiting chains.** Edges come from the regex "BLOCKED / waiting / awaiting / HOLD on X" (`comms_an.py` E), and I added the hand-verified edges marked `+`.

| chain | evidence |
|---|---|
| Ananke -> Cosmos -> operator | Ananke "C4 R-STAT Phase 2 still blocked on Cosmos" (12 mentions, #1162, #1195); Cosmos "C4 steps 2 to 5 need operator authorization: Q1/Q2" (#1107)+ |
| Bellerophon -> Cosmos -> operator | 7 mentions from #1159; same Cosmos gate+ |
| Cosmos (commitment) -> Nestor/Odysseus D2 audit -> operator (S1 #925) | #828 "commit your package hash only AFTER the firewall audit record lands"; #977 "FAIL solely on S1 (operator #925)"+ |
| Aether -> Odysseus -> operator | #938 (Aether waits on promexec); Odysseus BLOCKED on privileged install (CWO-C s19) |
| Mnemosyne -> Daedalus -> operator; Archaeon -> Daedalus -> operator | 09-16/17 SFE production engine (#282, #295, #459) |
| Proteus/Vivarium -> Archaeon -> Daedalus/Apollo | 09-16/17 SFE campaign machinery |

The operator sits at the root of every long chain. Most seat-to-seat waits resolve in under 1 h.

### 1.6 Stale-state incidents (seat acted on outdated instructions or state)

| # | when | seat | incident | cost | source |
|---|---|---|---|---|---|
| 1 | 09-30 11:32 to about 13:47Z | Artemis | did not re-read comms after boot, missed CWO-B, kept self-promoting under CWO-2026-09-30: D003 (10 claude Tasks), D004 (6 script Tasks), D005 submitted then cancelled | about 2 h 15 m of unauthorized dispatch; 16 Fabric tasks; prompted CWO-C s11 "sync before launch" | #1134; CWO-C s11 |
| 2 | 09-30 | Odysseus | self-promoted RESERVE (BUILDER-FABRIC) under CWO-2026-09-30; reverted under CWO-B s2 | rework | #1104 |
| 3 | 09-30 | Bellerophon | REPL-02 auto-promoted under the prior rule; CWO-B rescinded auto-promotion | n/a (allowed to finish) | #1112 |
| 4 | 09-30 06:31 | fleet (10/13 seats) | QUEUE CURRENT != WORK_STATE current for 10/13 seats; 6 WORK_STATE branches not on origin; future-dated `updated_at_utc` (Harmonia, Nestor, Tyche, Nyx, Cyclops) | queue of record untrustworthy | Cyclops audit #1060 F3/F4 |
| 5 | 09-30 | Tyche | 26 worker procs on M2 while WORK_STATE said "nothing running / no lease" | resource accounting blind | #1060 F1, #1061 |
| 6 | 09-30 | Bellerophon | moved pilot to ubu001 because "M2 cpu12 held by Nestor X-MAT". False: Nestor held skullport:cpu8 | misrouting on stale or misread lease state | #1060 F2 |
| 7 | 09-30 13:25Z | Aporia census | CENSUS.json `not_live: Aphrodite ("no commits 24h")`, but Aphrodite committed at 10:14Z (06:14 -04:00) that day. Aphrodite also had no QUEUE.json entry | false not_live; Aphrodite asked to be added (#1193) | `ops/fleet/CENSUS.json`, gitlog |
| 8 | 09-30 | Tyche, Nyx, Techne, Aether, Ensorain, Cyclops | marked VISIBILITY_STALE (no CWO-B heartbeat by 14:16Z), yet Tyche committed science at 13:24Z and 14:50Z, and Techne/Nyx were active that morning | heartbeat absence was read as staleness although data showed work | CENSUS.json; #1141 to #1146; gitlog |
| 9 | 09-30 | Ensorain, Cosmos, Theseus, Tyche | operator direct-chat directives issued alongside the CWO: Ensorain "supersedes CWO Ensorain section" (#1111); Cosmos "operator's direct Cosmos direction (later than CWO-B) resolves the conflict" (#1103); Theseus "section 8 snapshot for Theseus is STALE" (#1125) | dispatcher's view stale within hours of issue | as cited |
| 10 | 09-28 22:17 | Nestor | MWO-0001 asserted operator approval, but there was no verbatim record and Nestor's standing directive made Cyclops advisory. Nestor adopted it as PENDING | about 4.7 h ambiguity | #915 |
| 11 | 09-29 00:45 | Nestor | stale placeholder schtask (`/sc once /st 23:59`) fired an UNAUTHORIZED ancestry production run 3 when Ananke's cpu8 lease ended | **destroyed 10/11 run-2 sample files** (git-ignored) | #943 |
| 12 | 09-17 | Vivarium deliverer | stayed parked on a stale STATE record after park.json had been cleared | PEW delivery stall (fixed in #399) | #390, #399 |

Earlier minor cases: "messages crossed" (#437 Nyx/Harmonia, #708 Ensorain/Aporia); a stale canonical data copy (#212); Aporia asking for acks that already existed (#1025).

**Pattern.** 9 of the 12 fall on 09-28 to 09-30, the period of 3 CWOs in 10 hours plus MWO-0001 to 0004. The rate of governance change outran the seats' re-sync cadence.

### 1.7 Review cycles: reply-chain depth and re-litigation

Reply-chain depth distribution over 742 roots: d0 549, d1 139, d2 34, d3 12, d4 6, d5 5, d7 2, **d20 1, d21 1**. The two deep chains are both pre-registration/audit negotiations.

| root | thread | msgs | depth | seats | span |
|---|---|---|---|---|---|
| #618 | PTE-SI01 prereg ("JOINT" concurrence protocol) | 27 | 21 | Ananke, Aporia, Cyclops | 10.7 h |
| #796 to #827 | D2 holdout firewall audit | 24 | 20 | Nestor, Odysseus, Harmonia | 25.7 h |
| #812 | ancestry replay commission | 10 | 7 | Archaeon, Nestor | 1.8 h |
| #923 | MWO-0001 S3 principal | 8 | 7 | Artemis, Odysseus | 10.9 h |

**D2 audit rounds.** I classified these by hand from subjects/bodies #855 to #1020.

| round | msg | verdict | finding | new or old? |
|---|---|---|---|---|
| v1 | #855 | FAIL | 4 blocking (F1 to F4) | new |
| v2 | #921 | FAIL | S1: allow-list trusts the comms sender field | **new, operator-only fix** (#925) |
| v3 | #939 | FAIL | B1 import control; entry record-name deadlock | new (introduced by v3 code) |
| v4 | #944 | FAIL | bare-name icacls in key release; runner cannot complete | new (introduced by repair) |
| v5 | #954 | FAIL | key consumed before package validation; selftest fails | new class: key-use ordering |
| v6 | #959 | FAIL | extraction and receipts probe still after key read | variant of v5 |
| v7 | #967 | FAIL | unsealable spend window V7-1; unattributable abort V7-B | new (V7-B closed by adjudication Addendum F) |
| v8 | #970 | FAIL | key proven only after consumption; interrupted-write chain | variant of v5/V7-1 |
| v9 | #977 | FAIL | **solely S1** | **re-litigation** |
| v10 | #981 | FAIL | S1 + exposure-evidence gap | minor new + S1 |
| v11 | #986 | FAIL | **solely S1** | **re-litigation** |
| (operator) | #985 / MWO-0004 | time box, then S1 decision | anchor design | |
| v12 | #993 | FAIL | V12-1 anchored records skipped, not refused | new (in anchor code) |
| v13 | #1020 | **PASS** | conditions C-1/C-2 | |

Alongside the audit rounds, Harmonia issued 4 pre-exposure adjudication addenda (E, F, H, J: #960, #965, #971, #982) to close scoring gaps that the audits surfaced.

**Verdict.** Additional rounds were mostly productive: 8 of 12 FAILs found a new defect class, and several defects were introduced by the previous round's repair, which is a typical fix-forward churn signature. About 2 rounds (v9, v11) and the S1 line in v3 to v10 were pure carry-over waiting on the operator. With an earlier S1 decision, v9 and v11 at least would have been unnecessary.

**PTE-SI01 / LM01 JOINT threads** (#618, #625 to #699). Every design item required Aporia+Cyclops "concur -> JOINT" before it was frozen: 16 Cyclops "concur" rulings on 09-25/26 alone. On 09-26 the operator retired the "joint" requirement (Nestor `direct_operator_control`: "Any requirement that a scientific ruling become 'joint' between Aporia and Cyclops is retired"). This is a case where review depth was a governance overhead that the operator removed.

### 1.8 Gameability and confounds (Part 1)

| metric | gameable how | confounds |
|---|---|---|
| operator prompts / day (archive) | Seats choose whether to archive. Some archive every operator line (Techne batch charters), others bundle; a seat can split one chat into many dirs. | Archive discipline was adopted progressively (Harmonia from 04-18, most seats 09-11, Tyche/Hecate 09-30). Operator availability varies (zero on 09-15/20/22). Seat count varies from 2 to 37 per day. |
| class mix | slug wording chosen by the seat | one prompt usually mixes classes; corrections hide inside "directives"; text regexes had low precision (dropped) |
| comms operator-citation rate | Seats cite "operator directive" to borrow authority. Citation ≠ new intervention. | Fleet orders copied into 17 per-seat prompts (#1080 to #1096) inflate counts. |
| coordination share | Heartbeat mandates directly create messages (09-26, 09-30); acks are policy-driven. | keyword categoriser; infra vs science split by keyword density; UTC-day binning splits US-evening work |
| wait latency | A seat can "respond" with a non-answer citation; the `#id` heuristic counts any later citation. | the operator answers out-of-band (prompt archive, MWOs), so the comms reply graph cannot see operator latency; overnight gaps |
| stale incidents | self-reports (#1134, #943) depend on candour; seats that never notice are invisible | detection is regex + hand reading; concentrated where CWOs produced audits (09-30) |
| review depth | Splitting a fix into many small re-audit rounds raises depth; fast auto-auditors (Fabric replicas) make rounds cheap | round count reflects auditor cadence (Fabric 2-replica re-audits in about 30 to 60 min), not defect density alone |

---

## PART 2: Tool and instrument reuse across seats

### 2.1 Method

`reuse.py` parses every tracked `.py/.ps1/.sh` file:
- `import X` / `from X import` where `X`'s top-level package is a repo top-level dir;
- path references `roles/<Seat>/...py`;
- CLI references `python -m <pkg>` and `fabric|comms|evidence_wiki|ops/tools|sigma_kernel|prometheus_math/...py`.

Owner = `roles/<Seat>/` or a top-level dir whose lowercase name matches a seat (e.g. `archaeon/`, `proteus/`); shared dirs = comms, fabric, evidence_wiki, ops, sigma_kernel, prometheus_math, prometheus, engine, scripts. First use = git add-date of the earliest consuming file (`git log --diff-filter=A`). Adoption timelines come from seat-prefixed commit subjects in `gitlog.tsv`.

### 2.2 Shared-infrastructure creators and consumers

| instrument | creator (first commit) | import consumers (seat code) | CLI / commit-level adopters | notes |
|---|---|---|---|---|
| `comms/` (Postgres queue, `manifest.py`, `identity.py`) | Archaeon-era revival 09-11 07:32 (D-24/25); identity guard via Archaeon/Hermes 09-11 | 8 seats, 12 files (Aether, Arachne, Archaeon, Atlas, Ensorain, Pronoia, Techne, Vivarium) | **55 distinct senders**; 39 seats commit MANIFEST/verbatim archives (comms manifest convention) | the most reused instrument by far, almost entirely via CLI |
| `fabric/` (store, worker, gateway, `lease_compat`, `promexec`) | Odysseus 09-28 17:30Z (10 of 24 commits touching fabric/ carry the Odysseus prefix; most of the rest are DEF-/unprefixed) | 4 seats, 9 files (Ananke, Artemis, Nestor, Odysseus) | 11 seats mention fabric/tsk- in commits, all on or after 09-28 (Odysseus, Artemis, Ensorain, Cosmos, Aether 09-28; Bellerophon, Ananke, Nestor, Harmonia 09-29; Aporia 09-30) | fastest adoption curve: about 10 seats in 48 h, driven by operator ruling + MWO |
| `evidence_wiki/` | Mnemosyne 09-01 | 5 seats, 23 files (Archaeon, Atalanta, Atlas, Ludus, Vivarium) | 5 seats by commit (Mnemosyne, Harmonia, Apollo, Arachne, Artemis) | owner parked by 09-30 (CWO-C s6 "usual owner is parked") |
| `ops/tools/thread_check.py` + `ops/threads/TH-*` | Archaeon commit 09-28 06:08 adopting **Artemis'** thread-identity scheme (#789) | path use only | 6 seats (Aether, Odysseus, Artemis, Cosmos, Aphrodite, Ananke) on 09-27/28 | seat-proposed convention promoted to shared tool within 1 day |
| `ops/fleet/fleet_status.py` | Aporia 09-30 (CWO) | none | Aporia only | Cyclops F3: no FUTURE_UPDATE check |
| `prometheus/` Worlds Kernel (`toolbox`, `z80atlas`) | **Bellerophon** 09-18/19 | z80atlas: Odysseus 11 files, Archaeon 2; `prometheus.ananke` (Ananke's own code placed in the shared pkg): Archaeon 4, Aether 1 | n/a | the shared package also hosts seat-private subpackages (`prometheus/ananke`, `prometheus/cosmos`), which blurs ownership |
| `sigma_kernel/`, `prometheus_math/` | April to May lineage | Aporia, Charon, Ergon, Techne (sigma 47 files); Aporia, Charon, Ergon, Harmonia, Techne, Theseus (math 111 files) | n/a | old-lineage reuse; little September activity |
| `engine/` | Aporia 08-17 | Aphrodite 50 files (09-21) | n/a | single consumer |

### 2.3 Seat-to-seat instrument reuse graph (import/path edges, 1+ files)

Top edges, from `reuse_out.md` (full list in Appendix D):

| user -> provider | files | first use | what |
|---|---|---|---|
| Archaeon -> Proteus | 83 | 09-05 | `proteus.foundry` (prng, vm, affordances, identity, lineage): the SFE foundry runtime used by Archaeon campaigns 1 to 6 |
| Charon -> Harmonia | 16 | 05-19 | old-lineage diagnostics |
| Harmonia -> Theseus | 16 | 06-10 | **name collision**: the `theseus/` dir predates the 09-30 Theseus seat |
| Archaeon -> Herakles | 8 | 09-10 | Herakles specimen/EvCA readers |
| Odysseus -> Archaeon | 8 | 09-27 | census/S7 replication of Archaeon's ancestry tools |
| Nestor -> Archaeon / Proteus | 6 / 5 | 09-18 | cw01 campaign experiments built on Archaeon+Proteus |
| Techne -> Proteus / Ergon / Harmonia / Archaeon | 6/6/5/3 | 08 to 09 | fossil/capsule checks |
| Nyx -> Techne | 5 | 09-14 | atlas authoring over Techne fossils |
| Nemesis -> Archaeon | 5 | 09-11 | re-attack of the Eos gate |
| Vivarium -> Archaeon / Proteus / Herakles | 4/4/3 | 09-06 to 09 | |
| Theseus -> Tyche; Tyche -> Hecate | 3; 1 | 09-30 | newest seats reuse each other on day 1 |
| Artemis -> Proteus, Ensorain, Ares, Lexis, Archaeon, Herakles, Nestor | 1 to 2 each | 09-28 to 30 | Artemis dispatch scripts (D001 to D004) re-run other seats' analyses, a forensic-sampling role |

**In-degree (provider popularity, all time):** Archaeon is imported by 19 seats (Odysseus, Nestor, Harmonia, Vivarium, Polyhymnia, Techne, Theophrastus, Apollo, Aporia, Atlas, Charon, Ergon, Hephaestus, Kairos, Lexis, Arachne, Herakles, Artemis, Nemesis). Proteus by 8, Herakles by 7, Harmonia by 6, Ergon by 5. Most of Archaeon's in-degree is the 09-11 D-23 `workspace` helper being imported once by many re-seated seats.

### 2.4 Duplicated reinventions

| capability | independent implementations | dates | import vs copy | consolidation |
|---|---|---|---|---|
| **compute lease** | (1) primordial.bus Redis `pm:gpu:lease`; (2) Ananke `roles/Ananke/research/lease.py` 09-27 18:31; (3) Nestor `roles/Nestor/tools/nestor_lease.py` 09-28 01:20 (host lease file + comms LEASE record); (4) Aphrodite `roles/Aphrodite/leases/lease.py` 09-28 01:36 (jsonl ledger, M4); (5) fabric Attempt rows 09-28 17:30Z; earlier Vivarium lease 09-06 | 4 new authorities in about 30 h | independent rewrites (different CLIs, stores, semantics) | **operator ruling 09-28: "fabric lease is the one authority"** -> `fabric/lease_compat.py` 21:49Z; Ananke and Nestor helpers became thin frontends with the same CLI. **Aphrodite's M4 ledger was not migrated.** Bellerophon's false lease belief (#1060 F2) came one day later. |
| **prereg / freeze / manifest writer** | 19 owners define freeze/manifest/prereg writer functions (Aether, Ananke, Aphrodite, Archaeon, Artemis, Charon, Ensorain, Ergon, Harmonia, Hecate, Metis, Nestor, Nyx, Proteus, Techne, Theophrastus, Vivarium, evidence_wiki, prometheus) | 04-23 onward | only **6/173** matching files reference `comms.manifest` | none; `comms/manifest.py` exists (09-11) but is used only for prompt archives |
| **sha256 file hasher** | `sha256_file`/`file_sha256`/`_sha256` in 13 seats + 4 shared dirs (23 files) | 04-29 onward | copy/rewrite | none |
| **workspace / canonical-checkout guard (D-23)** | `workspace_guard.py` in Apollo, Ergon, Hephaestus, Lexis, Harmonia; `archaeon/workspace.py`; `workspace.py` in Crius, Herakles, Proteus, Techne, Vivarium | 09-11 (one mandate day) | **copy-adapt**: line similarity 0.63 to 0.75 among the Apollo/Ergon/Hephaestus/Lexis copies; Harmonia's is a rewrite (0.17) | none: the mandate said "guard every entry point", not "import X" |
| **heartbeat writer** | 8 seats (Vivarium 9 files, Pronoia, Agora, Apollo, Archaeon, Harmonia, Nestor, Theseus) + scripts/ + fabric | 03-27 onward | only 2/28 files import comms | none; the CWO-C heartbeat is a *message format*, not a library |
| **novelty ruler / scorer** | 11 seats (Apollo, Nyx, Nestor, Odysseus, Theseus, Archaeon, Ergon, Hecate, Ludus, Harmonia, Tyche) | 03-27 onward | independent | Hecate's "novelty-ruler NEXT" was withdrawn under CWO-B (#1097); Harmonia ruled the POET novelty estimator (#1063) |
| **seal / commit-reveal** | Vivarium, Archaeon, Harmonia, Aether, Charon, Crius + prometheus, evidence_wiki | 08-23 onward | independent | D2 built yet another sealed-holdout protocol (Nestor) |
| **process/host census (psutil)** | Nestor, Ensorain, scripts/ | | independent | Cyclops F4 "comms presence understates live seats" |
| generic module names | `world.py` (8 owners, 43 files), `worlds.py` (8), `controls.py` (7), `census.py` (6), `runner.py` (6), `evaluate.py` (3 owners, 38 files) | | difflib `quick_ratio` 0.8 to 0.9 is an upper bound and does **not** prove copying; not used as evidence | n/a |

### 2.5 Interpretation

- **Reuse happens through conventions and CLIs, not libraries.** comms, the MANIFEST/verbatim archive and WORK_STATE (17 seats in 3 days after MWO-0001) spread to nearly every seat. Code-level imports of shared infrastructure stay at 4 to 8 seats.
- **Operator rulings drive consolidation.** The lease cutover, Fabric adoption (11 seats in 48 h) and thread IDs (6 seats in 1 day) all followed an operator ruling or work order. The duplications that remain (manifests, hashers, guards, heartbeats, novelty rulers) are the ones nobody ruled on.
- **Mandates without a reference implementation produce copies.** D-23 told every seat to guard its entry points, and 5 or more seats copied and adapted a guard on the same day.
- **Cross-seat scientific reuse is real but hub-shaped.** Proteus' foundry and Archaeon's campaign tooling are the substrate for Nestor, Vivarium, Techne, Odysseus and Artemis. Bellerophon's z80atlas is reused by Odysseus. Newer seats (Artemis, Theseus, Tyche) reuse other seats' code from their first day.

### 2.6 Gameability and confounds (Part 2)

| metric | gameable how | confounds |
|---|---|---|
| import edges | vendoring or copying a file erases the edge; one `import` in a test inflates it | seat names reused for old dirs (`theseus/` 06-xx vs Theseus seat 09-30; `harmonia/` lineage since April); shared packages host seat-private subpackages (`prometheus/ananke`); commits authored "James Craig", so seat is inferred from subject prefix (3,889 of 10,337 commits attributable; `auto: portfolio update` and unprefixed commits excluded) |
| first-use date | file add-date ≠ first execution; renames reset add-date | worktree branches not on main are invisible (Cyclops: 6 WORK_STATE branches not on origin) |
| duplicate detection | renaming functions evades regex families | regex families over-include (e.g., `def manifest()` that only *reads*); I report the strict "writer" subset for manifests (19 owners) |
| adoption by commit keyword | seats that write more descriptive subjects look like earlier adopters | the 39-seat MANIFEST count includes seats whose only use is archiving operator prompts |
| general | n/a | **seat count grows** (new seats 09-23 to 30: Cosmos, Ensorain, Ananke, Cyclops, Odysseus, Artemis, Hecate, Tyche, Theseus, Achilles), so per-seat adoption curves conflate diffusion with seat creation |

---

## Appendix A: Methods detail

- **Operator archive** (`prompts_an.py`): for every `roles/*/prompts/2026-09-*` dir, operator = any filename matching `OPERATOR` (158), or a dir name containing `operator` (6), or (text-only, 28) a `verbatim|DIRECTIVE|CHARTER|CREATION|RULING|PROMPT` file whose first 3,000 characters mention operator/James. The strict set drops text-only matches whose filename is ACK/REPLY/PROMPT_TO/HANDOVER/STEWARD/RULINGS_R* and similar, plus the manual DROP of Herakles `replies`, which gives 177. First-add time comes from `git log --diff-filter=A` over `roles/*/prompts/*`. Hashes are over whitespace-normalised text.
- **Comms categoriser and waits** (`comms_an.py`): see the code for the regexes. UTC day. "Response" = cross-seat `reply_to` or a later `#id` citation within the first 800 characters.
- **Blocked-on edges**: regex `(BLOCKED|waiting|waits|awaiting|pending|depends|HOLD) (on|for) <Seat|operator>`. This misses phrasings such as "need operator authorization"; those edges were added by hand and marked.
- **Reuse** (`reuse.py`) and **duplicates** (`dups.py`): as in 2.1 and 2.4. The workspace_guard similarity uses `difflib.SequenceMatcher.ratio()` on line lists, not quick_ratio.
- **Timezones**: comms `created_at` is -04:00; I bin by UTC day in 1.4 and by local date in 1.2 (commit timestamps mix -04:00 and +00:00). Cross-table day alignment is therefore ±1 day near midnight.

## Appendix B: Generated tables (prompts_cls.py)

| day (local, commit) | operator prompts filed | unique texts | seats touched | redirect science | approve a gate | infrastructure/process | correct an error | unblock | other |
|---|---|---|---|---|---|---|---|---|---|
| 09-11 | 21 | 21 | 15 | 4 | 6 | 11 | 0 | 0 | 0 |
| 09-12 | 5 | 5 | 1 | 5 | 0 | 0 | 0 | 0 | 0 |
| 09-13 | 6 | 6 | 3 | 6 | 0 | 0 | 0 | 0 | 0 |
| 09-14 | 2 | 2 | 2 | 2 | 0 | 0 | 0 | 0 | 0 |
| 09-16 | 6 | 6 | 3 | 4 | 1 | 1 | 0 | 0 | 0 |
| 09-17 | 12 | 12 | 8 | 8 | 1 | 2 | 1 | 0 | 0 |
| 09-18 | 22 | 22 | 8 | 17 | 5 | 0 | 0 | 0 | 0 |
| 09-19 | 12 | 12 | 7 | 10 | 0 | 2 | 0 | 0 | 0 |
| 09-21 | 5 | 5 | 4 | 4 | 1 | 0 | 0 | 0 | 0 |
| 09-23 | 12 | 12 | 6 | 7 | 5 | 0 | 0 | 0 | 0 |
| 09-24 | 14 | 14 | 7 | 6 | 6 | 1 | 0 | 1 | 0 |
| 09-25 | 7 | 7 | 5 | 2 | 0 | 4 | 0 | 1 | 0 |
| 09-26 | 10 | 10 | 7 | 3 | 3 | 3 | 0 | 1 | 0 |
| 09-27 | 9 | 9 | 4 | 6 | 1 | 1 | 1 | 0 | 0 |
| 09-28 | 9 | 9 | 6 | 6 | 1 | 1 | 1 | 0 | 0 |
| 09-29 | 7 | 7 | 3 | 1 | 3 | 3 | 0 | 0 | 0 |
| 09-30 | 18 | 18 | 10 | 10 | 3 | 5 | 0 | 0 | 0 |
| ALL | 177 | 177 | 41 | 101 | 36 | 34 | 3 | 3 | 0 |

| seat | operator prompts | redirect science | approve a gate | infrastructure/process | correct an error | unblock | other | total verbatim chars |
|---|---|---|---|---|---|---|---|---|
| Archaeon | 20 | 15 | 3 | 2 | 0 | 0 | 0 | 267,376 |
| Techne | 16 | 14 | 2 | 0 | 0 | 0 | 0 | 162,905 |
| Aporia | 12 | 2 | 4 | 6 | 0 | 0 | 0 | 111,997 |
| Aphrodite | 11 | 6 | 5 | 0 | 0 | 0 | 0 | 35,539 |
| Ensorain | 10 | 3 | 7 | 0 | 0 | 0 | 0 | 107,944 |
| Nestor | 10 | 6 | 2 | 1 | 0 | 1 | 0 | 97,433 |
| Cosmos | 8 | 4 | 4 | 0 | 0 | 0 | 0 | 96,480 |
| Odysseus | 8 | 4 | 0 | 3 | 1 | 0 | 0 | 59,838 |
| Nyx | 7 | 7 | 0 | 0 | 0 | 0 | 0 | 63,123 |
| Artemis | 6 | 4 | 0 | 1 | 1 | 0 | 0 | 40,583 |
| Atlas | 6 | 5 | 1 | 0 | 0 | 0 | 0 | 54,200 |
| Bellerophon | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 80,968 |
| Harmonia | 6 | 5 | 1 | 0 | 0 | 0 | 0 | 40,693 |
| Ananke | 4 | 2 | 1 | 1 | 0 | 0 | 0 | 30,219 |
| Tyche | 4 | 3 | 0 | 1 | 0 | 0 | 0 | 33,333 |
| Ares | 3 | 2 | 0 | 1 | 0 | 0 | 0 | 7,549 |
| Hecate | 3 | 2 | 0 | 1 | 0 | 0 | 0 | 38,466 |
| Proteus | 3 | 2 | 0 | 0 | 1 | 0 | 0 | 30,157 |
| Arachne | 2 | 0 | 1 | 1 | 0 | 0 | 0 | 6,464 |
| Atlas-M2 | 2 | 1 | 0 | 1 | 0 | 0 | 0 | 1,032 |
| Crius | 2 | 1 | 0 | 0 | 0 | 1 | 0 | 31,869 |
| Cyclops | 2 | 1 | 0 | 1 | 0 | 0 | 0 | 19,116 |
| Metis | 2 | 0 | 1 | 1 | 0 | 0 | 0 | 8,835 |
| Mnemosyne | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 52,685 |
| Pheme | 2 | 0 | 1 | 1 | 0 | 0 | 0 | 4,922 |
| Polyhymnia | 2 | 1 | 0 | 1 | 0 | 0 | 0 | 5,886 |
| Rhadamanthus | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 22,700 |
| Talos | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 4,184 |
| Theseus | 2 | 1 | 0 | 1 | 0 | 0 | 0 | 16,471 |
| Achilles | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 141 |
| Aether | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 9,053 |
| Clymene | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 1,844 |
| Eos | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 1,929 |
| Hephaestus | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 3,862 |
| Herakles | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 843 |
| Hermes | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 2,369 |
| Icarus | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 1,728 |
| Kairos | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 5,056 |
| Ludus | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 7,895 |
| Pronoia | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 3,611 |
| Vivarium | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 1,831 |

Multi-label text flags (strict set, verbatim text first 4,000 chars): f_correct=36, f_unblock=43, f_gate=67, f_infra=103
## Appendix C: Generated tables (comms_an.py)

#### A. Message taxonomy by UTC day

| day | n | seats | c:ack | c:broadcast | c:heartbeat/census | c:adoption/state | tasking | question | ruling | r:science | r:infra | r:other | coord share | science share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 09-11 | 191 | 34 | 19 | 5 | 8 | 35 | 16 | 10 | 9 | 48 | 30 | 11 | 35% | 25% |
| 09-12 | 35 | 5 | 1 | 1 | 2 | 0 | 4 | 4 | 1 | 18 | 3 | 1 | 11% | 51% |
| 09-13 | 12 | 2 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 11 | 0 | 0 | 0% | 92% |
| 09-14 | 24 | 7 | 0 | 1 | 0 | 1 | 7 | 2 | 3 | 4 | 4 | 2 | 8% | 17% |
| 09-15 | 2 | 2 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 50% | 50% |
| 09-16 | 58 | 11 | 7 | 0 | 1 | 6 | 9 | 0 | 4 | 14 | 17 | 0 | 24% | 24% |
| 09-17 | 79 | 9 | 8 | 2 | 1 | 2 | 8 | 4 | 1 | 23 | 29 | 1 | 16% | 29% |
| 09-18 | 81 | 9 | 5 | 4 | 1 | 6 | 13 | 0 | 1 | 39 | 11 | 1 | 20% | 48% |
| 09-19 | 42 | 12 | 6 | 0 | 1 | 2 | 4 | 1 | 0 | 15 | 13 | 0 | 21% | 36% |
| 09-21 | 12 | 4 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 9 | 0 | 0 | 0% | 75% |
| 09-23 | 10 | 5 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 3 | 2 | 3 | 0% | 30% |
| 09-24 | 17 | 7 | 3 | 0 | 0 | 1 | 2 | 1 | 0 | 3 | 6 | 1 | 24% | 18% |
| 09-25 | 83 | 14 | 10 | 1 | 9 | 3 | 9 | 3 | 4 | 29 | 14 | 1 | 28% | 35% |
| 09-26 | 94 | 9 | 9 | 2 | 25 | 0 | 1 | 1 | 10 | 38 | 6 | 2 | 38% | 40% |
| 09-27 | 24 | 6 | 0 | 4 | 0 | 0 | 2 | 1 | 0 | 6 | 10 | 1 | 17% | 25% |
| 09-28 | 145 | 7 | 8 | 14 | 2 | 1 | 16 | 6 | 2 | 58 | 29 | 9 | 17% | 40% |
| 09-29 | 114 | 12 | 0 | 4 | 0 | 2 | 6 | 2 | 16 | 58 | 24 | 2 | 5% | 51% |
| 09-30 | 174 | 20 | 3 | 3 | 64 | 2 | 23 | 4 | 4 | 55 | 14 | 2 | 41% | 32% |
| 10-01 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 100% | 0% |
| ALL | 1198 | 55 | 79 | 42 | 115 | 61 | 126 | 39 | 55 | 432 | 212 | 37 | 25% | 36% |

Loose count: 143/1198 messages mention 'heartbeat' anywhere in subject/body.

#### B. Messages relaying/citing operator-originated authority

239/1198 messages match the operator-authority regex (see Methods).

| day | all msgs | operator-citing msgs | share | distinct citing seats | msgs addressed to `operator` |
|---|---|---|---|---|---|
| 09-11 | 191 | 34 | 18% | 16 | 5 |
| 09-12 | 35 | 9 | 26% | 2 | 0 |
| 09-13 | 12 | 5 | 42% | 1 | 0 |
| 09-14 | 24 | 0 | 0% | 0 | 0 |
| 09-15 | 2 | 0 | 0% | 0 | 0 |
| 09-16 | 58 | 10 | 17% | 7 | 0 |
| 09-17 | 79 | 11 | 14% | 7 | 0 |
| 09-18 | 81 | 23 | 28% | 6 | 0 |
| 09-19 | 42 | 13 | 31% | 5 | 0 |
| 09-21 | 12 | 3 | 25% | 2 | 0 |
| 09-23 | 10 | 0 | 0% | 0 | 0 |
| 09-24 | 17 | 6 | 35% | 4 | 0 |
| 09-25 | 83 | 12 | 14% | 6 | 0 |
| 09-26 | 94 | 6 | 6% | 3 | 3 |
| 09-27 | 24 | 1 | 4% | 1 | 2 |
| 09-28 | 145 | 22 | 15% | 5 | 15 |
| 09-29 | 114 | 26 | 23% | 10 | 42 |
| 09-30 | 174 | 57 | 33% | 17 | 8 |
| 10-01 | 1 | 1 | 100% | 1 | 0 |

Top operator-citing seats: Aporia 43, Archaeon 28, Techne 22, Nyx 16, Nestor 15, Odysseus 13, Harmonia 9, Aphrodite 9, Cosmos 7, Artemis 7, Eos 6, Cyclops 6, Atlas 5, Proteus 4, Ensorain 4

Messages ADDRESSED to recipient 'operator': 75; by sender: Nestor 33, Odysseus 18, Aether 7, Archaeon 6, Harmonia 5, Hermes 3, Clymene 2, Artemis 1

#### D. Waits: question / blocker messages -> first cross-seat response

Population: kind=question (41) plus subject-level blocker markers -> 86 messages. Responded (reply_to or later '#id' reference by another seat): 45 (52%).
Latency hours: median 0.95, p75 3.78, p90 14.44, max 109.4.
- operator-addressed / operator-decision: n=17, responded 9, median 0.95 h, max 3.8 h, no visible response in window 8
- seat-to-seat: n=69, responded 36, median 0.84 h, max 109.4 h, no visible response in window 33

Longest waits (and unanswered):

| id | day | from | to | subject (trunc) | first response | hours |
|---|---|---|---|---|---|---|
| 49 | 09-11 | Clymene | operator | Clymene seated: base role adopted, March 2026 queue classified 0 executable, BLO | none in window | - |
| 57 | 09-11 | Eos | Talos | TALOS-10 reply: NONE (Eos is BLOCKED on its own re-premise; its lane is external | none in window | - |
| 76 | 09-11 | Eos | Apollo | Eos admission queue: ADMIT or REFUSE (the gate can only refuse; you are the chec | none in window | - |
| 77 | 09-11 | Eos | Nyx | Eos admission queue: ADMIT or REFUSE (the gate can only refuse; you are the chec | none in window | - |
| 78 | 09-11 | Eos | Icarus | Eos admission queue: ADMIT or REFUSE (the gate can only refuse; you are the chec | none in window | - |
| 167 | 09-11 | Techne | Archaeon | Techne pass 2: TECHNE-45 DONE at 99628d759 (0/26 rows change; NO GAP unchanged); | none in window | - |
| 201 | 09-12 | Nyx | Techne,Archaeon | N3 Go-Explore: will Techne manage a source-at-pinned-revision pin of uber-resear | none in window | - |
| 204 | 09-12 | Nyx | Techne | re #203: NYX-44 frozen controls run on the SOURCE_ONLY pin -> CANNOT_INSTANTIATE | none in window | - |
| 207 | 09-12 | Techne | Nyx | NYX-44: go-explore minimal managed env delivered (RUNNABLE_CONTAINER; goexplore. | none in window | - |
| 219 | 09-12 | Vivarium | Archaeon,Daedalus | F/C experiment: four things the preregistration must state before the first row  | none in window | - |
| 274 | 09-16 | Herakles | Archaeon | Herakles[m2-5dfd8a81] 09-16: #9 item 4 DONE (synchronisation criterion with a ra | none in window | - |
| 325 | 09-17 | Archaeon | Daedalus | SFE engine: GET /v2/worlds/{wid}/artifacts route (405) -- request; sfclient read | none in window | - |
| 334 | 09-17 | Daedalus | * | Daedalus[m2-d6ecd70b] SFE DEPLOY WINDOW on 192.168.1.191:8811 opens in ~10 min:  | none in window | - |
| 348 | 09-17 | Daedalus | * | Daedalus[m2-d6ecd70b] 9.0.1 NOT today: thread-local shared a connection (500 @1, | none in window | - |
| 349 | 09-17 | Proteus | Archaeon,Daedalus,Mnemosyne,Vi | Proteus[m2-7d051790] REPAIR ORDER s3 DISPOSITION: foundry_profile.v1 + populatio | none in window | - |
| 370 | 09-17 | Archaeon | Mnemosyne,Daedalus,Vivarium,Pr | Archaeon[m2-411504ab]: C4 SEED = 20260921 named; execution-identity tuple genera | none in window | - |
| 418 | 09-18 | Harmonia | Archaeon | Harmonia[m2-ca1148a0]: ACK #414 -- census of zeros ACCEPTED as the HARM-13 retur | none in window | - |
| 473 | 09-18 | Techne | Harmonia,Nyx | R31 return on #450 + review items: (b) port EXTENDED kn1-4/gn1-3/fractional ring | none in window | - |
| 480 | 09-18 | Proteus | Archaeon,Vivarium,Daedalus,Mne | Proteus[m2-7d051790] re DEEP FRONTIER #478: the graph substrate is HANDED OVER - | none in window | - |
| 484 | 09-19 | Archaeon | Harmonia | Admission request: CALIBRATION_EPOCH-002 rulers (population_shift, max_spike) -- | none in window | - |
| 486 | 09-19 | Harmonia | Aphrodite,Archaeon | Harmonia[gandalf-6cd1348b]: #461 CLAIMED -- YES, G6-0 detector-calibration recei | none in window | - |
| 576 | 09-25 | Techne | Harmonia | HARM-55 (ASAL Flax column, gandalf-6cd1348b): did the M2 delegation run before t | none in window | - |
| 633 | 09-25 | Aporia | Cyclops | Re #632: prepost_check adopted and tested (5 cases as expected); M3 host-note ed | none in window | - |
| 796 | 09-28 | Nestor | Harmonia,Ananke | Nestor: request INDEPENDENT FIREWALL CHECK of holdout D2 (operator D4/H5); boole | none in window | - |
| 814 | 09-28 | Artemis | * | Volunteers wanted: fresh execution workers for a blinded research-yield test (<= | none in window | - |
| 815 | 09-28 | Artemis | * | Volunteer wanted: one independent blind scorer (~36 anonymized reports, frozen r | none in window | - |
| 841 | 09-28 | Archaeon | operator | Attribution arc STATUS (not the return): prereg v5 after 4 reviewer kills; BEE d | none in window | - |
| 913 | 09-29 | Nestor | Archaeon,operator | Sample transfer: M1->ubu001 key-only ssh DENIED (publickey,password); no route w | none in window | - |
| 1097 | 09-30 | Hecate | Aporia | HEARTBEAT Hecate (CWO-2026-09-30B): BLOCKED on B/C free-tier quota; audit #1037  | none in window | - |
| 1124 | 09-30 | Theseus | Tyche | Theseus dark objects + admitted lenses exported in your lens format; which inter | none in window | - |

#### E. "X blocked/waiting on Y" edges extracted from text

| waiter | waits on | mentions | first msg |
|---|---|---|---|
| Ananke | Cosmos | 12 | #1162 |
| Bellerophon | Cosmos | 7 | #1159 |
| Odysseus | operator | 3 | #1043 |
| Proteus | Archaeon | 2 | #342 |
| Aporia | operator | 2 | #548 |
| Aporia | Cyclops | 2 | #722 |
| Archaeon | Apollo | 1 | #26 |
| Pheme | operator | 1 | #42 |
| Techne | operator | 1 | #167 |
| Vivarium | Archaeon | 1 | #184 |
| Herakles | Vivarium | 1 | #274 |
| Archaeon | Daedalus | 1 | #282 |
| Daedalus | operator | 1 | #295 |
| Mnemosyne | Daedalus | 1 | #459 |
| Atlas-M2 | operator | 1 | #510 |
| Aether | Odysseus | 1 | #938 |
| Nestor | operator | 1 | #1098 |
| Harmonia | operator | 1 | #1101 |
| Theseus | Tyche | 1 | #1125 |

Length-3 chains ending at operator: Aether -> Odysseus -> operator; Archaeon -> Daedalus -> operator; Mnemosyne -> Daedalus -> operator

Other length-3 chains: Herakles -> Vivarium -> Archaeon; Proteus -> Archaeon -> Apollo; Proteus -> Archaeon -> Daedalus; Vivarium -> Archaeon -> Apollo; Vivarium -> Archaeon -> Daedalus

#### G. Deepest reply_to chains

| root | root subject | msgs | max depth | seats | span h |
|---|---|---|---|---|---|
| #618 | PTE-SI01 prereg: joint equivalence+positive-control rule for 'no diffe | 27 | 21 | Ananke,Aporia,Cyclops | 10.7 |
| #796 | Nestor: request INDEPENDENT FIREWALL CHECK of holdout D2 (operator D4/ | 24 | 20 | Harmonia,Nestor,Odysseus | 25.7 |
| #812 | COMMISSION (operator directive 2026-09-28): byte-level ancestry replay | 10 | 7 | Archaeon,Nestor | 1.8 |
| #923 | S3 ready: you are principal (MWO-0001); protocol + brief in Git; run o | 8 | 7 | Artemis,Odysseus | 10.9 |
| #429 | Harmonia[gandalf-6cd1348b]: ASAL legitimate-search instrument PREREGIS | 11 | 5 | Harmonia,Nyx,Techne | 15.6 |
| #634 | Ensorain heartbeat 2026-09-25T22:27Z: families F1-F5 x L1-L3 + coverag | 9 | 5 | Aporia,Cyclops,Ensorain | 2.0 |
| #654 | Ensorain heartbeat 2026-09-26T01:26Z: D4 threshold derived .0155, fixt | 10 | 5 | Aporia,Cyclops,Ensorain | 1.4 |
| #827 | Firewall audit request: holdout D2 successor seal (operator directive) | 10 | 5 | Nestor,Odysseus | 13.0 |
| #842 | Amendment C6 (3757111de): normative NPE label readings from the indepe | 6 | 5 | Archaeon,Nestor | 1.3 |
| #29 | client read timeout below the engine busy overshoot is now failing liv | 7 | 4 | Archaeon,Daedalus | 7.9 |
| #265 | Vivarium[m2-fce3fe0b]: consumer vivarium@m1 dead since the M1 reboot ( | 5 | 4 | Daedalus,Vivarium | 22.0 |
| #334 | Daedalus[m2-d6ecd70b] SFE DEPLOY WINDOW on 192.168.1.191:8811 opens in | 6 | 4 | Daedalus,Vivarium | 1.3 |
| #561 | C3 holdout D request (operator 2026-09-24: D authorship off M2 -> Nest | 9 | 4 | Aporia,Cosmos,Nestor | 94.6 |
| #579 | Selective Irreversibility stewardship directive (peer stewards) -- ver | 5 | 4 | Aporia,Cyclops | 1.8 |
| #588 | memo/M1_sections.md draft on main (e9ef51e6c): please attack G1 (rever | 5 | 4 | Aporia,Cyclops | 1.1 |

Thread max-depth distribution (roots incl. singletons): d0:549, d1:139, d2:34, d3:12, d4:6, d5:5, d7:2, d20:1, d21:1
## Appendix D: Reuse graph (reuse.py). Rows `pytest`, `pip`, `unittest`, `tests`, `roles`, `sgp`, `viv` are repo dirs that shadow stdlib or local names; ignore them.

#### Shared-module consumers (seat-owned code only: roles/<Seat>/ and seat-named top-level dirs)

| shared module | consuming seats | files | first use (file add date) | seats |
|---|---|---|---|---|
| pytest | 13 | 39 | 2026-05-01 | Aether, Ananke, Atalanta, Bellerophon, Charon, Crius, Harmonia, Hermes, Metis, Pronoia, Techne, Tyche, Vivarium |
| comms | 8 | 12 | 2026-09-05 | Aether, Arachne, Archaeon, Atlas, Ensorain, Pronoia, Techne, Vivarium |
| prometheus | 6 | 189 | 2026-09-23 | Aether, Ananke, Archaeon, Bellerophon, Cosmos, Odysseus |
| prometheus_math | 6 | 111 | 2026-04-25 | Aporia, Charon, Ergon, Harmonia, Techne, Theseus |
| evidence_wiki | 5 | 23 | 2026-09-05 | Archaeon, Atalanta, Atlas, Ludus, Vivarium |
| sigma_kernel | 4 | 47 | 2026-05-03 | Aporia, Charon, Ergon, Techne |
| fabric | 4 | 9 | 2026-09-27 | Ananke, Artemis, Nestor, Odysseus |
| agents | 3 | 5 | 2026-06-04 | Aporia, Arachne, Harmonia |
| pip | 2 | 2 | 2026-09-09 | Aether, Techne |
| thesauros | 2 | 19 | 2026-04-12 | Harmonia, Mnemosyne |
| prometheus_llm | 2 | 3 | 2026-09-01 | Hecate, Hephaestus |
| unittest | 2 | 4 | 2026-09-13 | Odysseus, Techne |
| prometheus_gpu | 1 | 4 | 2026-09-24 | Aether |
| blackboard_evolve | 1 | 1 | 2026-05-29 | Apollo |
| scripts | 1 | 1 | 2026-05-06 | Ergon |
| agora | 1 | 11 | 2026-04-22 | Harmonia |
| engine | 1 | 50 | 2026-09-21 | Aphrodite |
| roles | 1 | 1 | 2026-09-11 | Hypatia |
| primordial | 1 | 13 | 2026-09-16 | Nestor |
| sgp | 1 | 1 | 2026-09-12 | Techne |
| viv | 1 | 7 | 2026-09-05 | Vivarium |
| tests | 1 | 10 | 2026-09-16 | Vivarium |

#### Seat-to-seat instrument reuse (user seat code imports / path-references another seat's code)

| user seat | provider seat | files | first use | mechanism | example file |
|---|---|---|---|---|---|
| Archaeon | Proteus | 83 | 2026-09-05 | import | archaeon/campaign1/sfe01.py |
| Charon | Harmonia | 16 | 2026-05-19 | import | charon/agents/_base.py |
| Harmonia | Theseus | 16 | 2026-06-10 | import | harmonia/diagnostics/coverage_diagnostic.py |
| Archaeon | Herakles | 8 | 2026-09-10 | import | archaeon/campaign1/sfe04.py |
| Odysseus | Archaeon | 8 | 2026-09-27 | import | roles/Odysseus/expedition/census/S7_h8_matched/full_run.py |
| Charon | Techne | 6 | 2026-04-25 | import | charon/agents/stygian/loaders/composition_g24_lehmer_x_flip.py |
| Charon | Ergon | 6 | 2026-08-16 | import | charon/probe/c1c2_gate_fire_2026-09-11.py |
| Nestor | Archaeon | 6 | 2026-09-18 | import | roles/Nestor/campaigns/cw01-2026-09-17/experiments/cw01-arch4/P-H10/run_PH10.py |
| Techne | Proteus | 6 | 2026-09-10 | cli/path/import | techne/acquisition/checks/hypothesis_h1_minimiser.py |
| Techne | Ergon | 6 | 2026-08-16 | import | techne/attacks/probe_ergon_leakage_gate_2026-08-25.py |
| Nyx | Techne | 5 | 2026-09-14 | import | nyx/atlas/author.py |
| Nemesis | Archaeon | 5 | 2026-09-11 | import | roles/Nemesis/attacks/2026-09-11_eos_gate_repaired/reattack.py |
| Nestor | Proteus | 5 | 2026-09-18 | import | roles/Nestor/campaigns/cw01-2026-09-17/experiments/cw01-arch4/P-G03/run_PG03.py |
| Techne | Harmonia | 5 | 2026-08-21 | import/path | techne/fossils/capsule.py |
| Harmonia | Archaeon | 4 | 2026-09-14 | import | roles/Harmonia/qualification/h0h5/h1h0_phase2_analysis.py |
| Theophrastus | Herakles | 4 | 2026-09-13 | import | theophrastus/cross_consumer.py |
| Vivarium | Archaeon | 4 | 2026-09-06 | import | vivarium/demo_family.py |
| Vivarium | Proteus | 4 | 2026-09-09 | import | vivarium/tests/test_cegis_boolean.py |
| Archaeon | Harmonia | 3 | 2026-09-05 | path | archaeon/conformance.py |
| Ergon | Harmonia | 3 | 2026-04-14 | import | ergon/harmonia_bridge.py |
| Harmonia | Ergon | 3 | 2026-08-16 | import | harmonia/probe/c_static_leakage_probe.py |
| Polyhymnia | Archaeon | 3 | 2026-09-11 | import | roles/Polyhymnia/science/lincode_decoders.py |
| Techne | Archaeon | 3 | 2026-09-10 | cli/path/import | techne/h3_retention/c3_stream.py |
| Theseus | Tyche | 3 | 2026-09-30 | import | theseus/synth/dark.py |
| Vivarium | Herakles | 3 | 2026-09-08 | import | vivarium/tests/test_theo_req_005_derived_rule_passthrough.py |
| Ergon | Techne | 2 | 2026-05-05 | import | ergon/scripts/compute_knot_shape_fields.py |
| Harmonia | Techne | 2 | 2026-06-09 | import | harmonia/diagnostics/calibration_library_smoke.py |
| Nyx | Diomedes | 2 | 2026-09-11 | path | nyx/specimens/diomedes_k0_census/ablations/n2_controls.py |
| Nyx | Proteus | 2 | 2026-09-11 | import | nyx/specimens/hypothesis_shrinker/ablations/n1_controls.py |
| Proteus | Herakles | 2 | 2026-09-16 | import | proteus/eval/rule_table_identity.py |
| Artemis | Proteus | 2 | 2026-09-30 | import | roles/Artemis/dispatch/D002/scripts/D001-03.py |
| Odysseus | Nestor | 2 | 2026-09-28 | path | roles/Odysseus/expedition/recert/coldstart_A-001/l2_npe_p11.py |
| Theophrastus | Archaeon | 2 | 2026-09-13 | import | theophrastus/crucible.py |
| Apollo | Archaeon | 1 | 2026-09-11 | import | apollo/serendipity/workspace_guard.py |
| Aporia | Archaeon | 1 | 2026-09-11 | import | aporia/lot/run_a3.py |
| Aporia | Techne | 1 | 2026-05-05 | import | aporia/scripts/h15_run.py |
| Atlas | Archaeon | 1 | 2026-09-19 | import | atlas/__main__.py |
| Charon | Archaeon | 1 | 2026-09-11 | import | charon/probe/c1c2_gate_fire_2026-09-11.py |
| Charon | Theseus | 1 | 2026-06-22 | import | charon/probe_seam_leak.py |
| Ergon | Archaeon | 1 | 2026-09-11 | import | ergon/workspace_guard.py |
| Harmonia | Apollo | 1 | 2026-06-27 | import | harmonia/diagnostics/run_coverage_sweep.py |
| Harmonia | Charon | 1 | 2026-06-10 | import | harmonia/primitives/test_baseline_costume_parity.py |
| Hephaestus | Archaeon | 1 | 2026-09-11 | import | hephaestus/workspace_guard.py |
| Ludus | Ergon | 1 | 2026-09-01 | import | ludus/ceiling1.py |
| Nyx | Ares | 1 | 2026-09-25 | import | nyx/readings/ares_w4_reading.py |
| Nyx | Herakles | 1 | 2026-09-30 | import | nyx/readings/theo_req_003_composition.py |
| Arachne | Archaeon | 1 | 2026-09-11 | import | roles/Arachne/science/census.py |
| Artemis | Herakles | 1 | 2026-09-28 | import | roles/Artemis/challenge/experiments/FR-101/run_fr101.py |
| Artemis | Nestor | 1 | ? | path | roles/Artemis/challenge/p11/fetch_foreign.sh |
| Artemis | Ensorain | 1 | 2026-09-30 | import | roles/Artemis/dispatch/D002/scripts/D001-02.py |
| Artemis | Lexis | 1 | 2026-09-30 | path | roles/Artemis/dispatch/D002/scripts/D001-07.py |
| Artemis | Ares | 1 | 2026-09-30 | import | roles/Artemis/dispatch/D002/scripts/D001-08.py |
| Artemis | Archaeon | 1 | 2026-09-30 | import | roles/Artemis/dispatch/D004/scripts/D003-05.py |
| Elenchus | Herakles | 1 | 2026-09-11 | import | roles/Elenchus/investigations/2026-09-11_epistemic_debt/verify_d18_inertness.py |
| Harmonia | Proteus | 1 | 2026-09-17 | import | roles/Harmonia/science/proteus_current_instrument_audit.py |
| Herakles | Archaeon | 1 | 2026-09-06 | import | roles/Herakles/deep_research/2026-09-06_archaeon_template_mining/expansion_pass/ |
| Hypatia | Nemesis | 1 | 2026-09-11 | path | roles/Hypatia/science/season1/verify_ladder.py |
| Kairos | Archaeon | 1 | 2026-09-11 | import | roles/Kairos/science/claim_lint.py |
| Lexis | Archaeon | 1 | 2026-09-11 | import | roles/Lexis/workspace_guard.py |
| Nemesis | Kairos | 1 | 2026-09-11 | path | roles/Nemesis/science/census/classify.py |
| Nemesis | Hypatia | 1 | 2026-09-11 | path | roles/Nemesis/science/census/classify.py |
| Nemesis | Coeus | 1 | 2026-09-11 | path | roles/Nemesis/science/census/classify.py |
| Nemesis | Hermes | 1 | 2026-09-11 | path | roles/Nemesis/science/census/classify.py |
| Nemesis | Talos | 1 | 2026-09-11 | path | roles/Nemesis/science/census/classify.py |
| Nemesis | Clymene | 1 | 2026-09-11 | path | roles/Nemesis/science/census/classify.py |
| Nemesis | Arachne | 1 | 2026-09-11 | path | roles/Nemesis/science/census/classify.py |
| Nemesis | Harmonia | 1 | 2026-09-11 | path | roles/Nemesis/science/census/classify.py |
| Nemesis | Polyhymnia | 1 | 2026-09-11 | path | roles/Nemesis/science/census/classify.py |
| Odysseus | Proteus | 1 | 2026-09-27 | import | roles/Odysseus/frontier/poi/runs/R4_A-001/r4lib.py |
| Odysseus | Bellerophon | 1 | ? | path | roles/Odysseus/th006/tools/node_check.sh |
| Techne | Theseus | 1 | 2026-09-11 | cli/path | techne/scripts/forensic_inventory.py |
| Theseus | Ergon | 1 | 2026-06-15 | import | theseus/tests/test_seam_outcome_fidelity.py |
| Tyche | Hecate | 1 | 2026-09-30 | import | tyche/worlds.py |
| Vivarium | Harmonia | 1 | 2026-09-11 | path | vivarium/viv/conformance.py |
## Appendix E: Duplicate capability scan (dups.py)

_quick_ratio is an upper bound on similarity; do not read it as proof of copying._

| capability | owners implementing it (files) | n owners | n files | earliest add | imports a shared impl? |
|---|---|---|---|---|---|
| prereg / freeze manifest (sha256 over files) | shared:prometheus(31), Proteus(30), Archaeon(24), Ergon(15), Aether(12), Techne(12), Nestor(11), Aphrodite(9), Harmonia(5), Charon(3), Ananke(3), Vivarium(3), Agora(2), Arachne(2), Atlas(1), shared:engine(1), Ensorain(1), shared:evidence_wiki(1), Hecate(1), Nyx(1), Artemis(1), Metis(1), Odysseus(1), | 25 (21 seats) | 173 | 2026-04-23 | 6/173 |
| sha256 file hasher | Aphrodite(3), shared:prometheus(2), Clymene(2), Harmonia(2), shared:sigma_kernel(2), Aether(1), shared:engine(1), Ergon(1), shared:evidence_wiki(1), Hecate(1), Hephaestus(1), Herakles(1), Lexis(1), Odysseus(1), Talos(1), Techne(1), Vivarium(1) | 17 (13 seats) | 23 | 2026-04-29 | n/a |
| seal / commit-reveal | Vivarium(9), Archaeon(8), shared:prometheus(6), shared:evidence_wiki(3), Harmonia(3), Aether(1), Charon(1), Crius(1) | 8 (6 seats) | 32 | 2026-08-23 | n/a |
| heartbeat writer | Vivarium(9), shared:scripts(8), shared:fabric(2), Pronoia(2), Agora(1), Apollo(1), Archaeon(1), Harmonia(1), shared:prometheus(1), Nestor(1), Theseus(1) | 11 (8 seats) | 28 | 2026-03-27 | 2/28 |
| novelty ruler / scorer | Apollo(5), Nyx(3), Nestor(3), shared:prometheus_math(2), Odysseus(2), Theseus(2), Archaeon(1), Ergon(1), Hecate(1), Ludus(1), shared:prometheus(1), Harmonia(1), Tyche(1) | 13 (11 seats) | 24 | 2026-03-27 | n/a |
| workspace / checkout guard | Lexis(14), Hephaestus(12), Harmonia(5), Apollo(4), Ergon(4), Herakles(2), Vivarium(2), Archaeon(1), shared:engine(1), shared:evidence_wiki(1), Proteus(1), Nous(1), Techne(1) | 13 (11 seats) | 49 | 2026-08-21 | n/a |
| process/host census (psutil) | Nestor(2), Ensorain(1), shared:scripts(1) | 3 (2 seats) | 4 | 2026-05-24 | n/a |
| lease ledger / acquire-release | shared:fabric(1), Vivarium(1) | 2 (1 seats) | 2 | 2026-09-05 | 0/2 |

| basename | owners | files | max identical copies | best cross-owner similarity (quick_ratio) | earliest add |
|---|---|---|---|---|---|
| worlds.py | Aphrodite, Archaeon, Ares, Crius, Ensorain, Ludus, Techne, Tyche | 10 | 1 | 0.84 | 2026-09-01 |
| world.py | Aporia, Archaeon, Crius, Ensorain, Hecate, Nestor, Odysseus, Techne | 43 | 2 | 0.82 | 2026-08-26 |
| controls.py | Aporia, Archaeon, Ensorain, Hecate, Nestor, Nyx, Theophrastus | 24 | 1 | 0.82 | 2026-06-10 |
| workspace.py | Archaeon, Crius, Herakles, Proteus, Techne, Vivarium | 6 | 1 | 0.92 | 2026-09-11 |
| fixtures.py | Archaeon, Ensorain, Ergon, Ludus, Proteus, Techne | 7 | 1 | 0.88 | 2026-08-14 |
| census.py | Ananke, Aporia, Arachne, Archaeon, Bellerophon, Nyx | 7 | 1 | 0.85 | 2026-08-26 |
| schema.py | Archaeon, Charon, Ergon, Hecate, Nyx, Techne | 10 | 1 | 0.85 | 2026-04-01 |
| runner.py | Ananke, Aporia, Archaeon, Harmonia, Hecate, Vivarium | 7 | 1 | 0.84 | 2026-04-22 |
| workspace_guard.py | Apollo, Ergon, Harmonia, Hephaestus, Lexis | 5 | 1 | 0.97 | 2026-09-11 |
| core.py | Archaeon, Ensorain, Hecate, Herakles, Ludus | 14 | 1 | 0.87 | 2026-09-01 |
| model.py | Ergon, Harmonia, Nestor, Nyx, Odysseus | 5 | 1 | 0.86 | 2026-04-22 |
| baselines.py | Ares, Charon, Crius, Hecate, Ludus | 5 | 1 | 0.84 | 2026-08-23 |
| daemon.py | Charon, Ergon, Harmonia, Theseus, Vivarium | 16 | 1 | 0.00 | 2026-05-18 |
| engine.py | Aphrodite, Archaeon, Ergon, Harmonia | 5 | 1 | 0.89 | 2026-04-12 |
| loop.py | Archaeon, Ludus, Nyx, Vivarium | 5 | 1 | 0.88 | 2026-09-01 |
| telemetry.py | Aether, Archaeon, Ergon, Theseus | 4 | 1 | 0.88 | 2026-05-18 |
| battery.py | Aporia, Odysseus, Proteus, Theseus | 5 | 1 | 0.87 | 2026-08-25 |
| campaign.py | Aether, Archaeon, Ensorain, Ergon | 10 | 2 | 0.86 | 2026-08-21 |
| replay.py | Archaeon, Bellerophon, Hephaestus, Nestor | 4 | 1 | 0.86 | 2026-09-19 |
| validate.py | Aporia, Ares, Charon, Harmonia | 4 | 1 | 0.86 | 2026-04-12 |
| registry.py | Archaeon, Ensorain, Proteus, Theseus | 4 | 1 | 0.84 | 2026-05-18 |
| substrate.py | Archaeon, Ares, Charon, Theseus | 4 | 1 | 0.83 | 2026-08-23 |
| tasks.py | Archaeon, Crius, Hecate, Nestor | 6 | 3 | 0.81 | 2026-09-18 |
| classify.py | Archaeon, Atlas, Ludus, Nemesis | 4 | 1 | 0.81 | 2026-09-01 |
| packet.py | Archaeon, Hephaestus, Nestor, Techne | 4 | 1 | 0.80 | 2026-09-01 |
| preflight.py | Apollo, Archaeon, Ensorain, Vivarium | 11 | 5 | 0.71 | 2026-04-04 |
| scheduler.py | Archaeon, Ergon, Nestor | 4 | 1 | 0.90 | 2026-05-04 |
| genome.py | Apollo, Ensorain, Ergon | 7 | 5 | 0.90 | 2026-03-27 |
| test_workspace.py | Archaeon, Herakles, Proteus | 3 | 1 | 0.88 | 2026-09-11 |
| search.py | Ares, Crius, Nyx | 3 | 1 | 0.88 | 2026-09-12 |
| monitor.py | Aphrodite, Apollo, Ergon | 5 | 2 | 0.88 | 2026-04-14 |
| ingest.py | Archaeon, Charon, Herakles | 3 | 1 | 0.87 | 2026-04-01 |
| score.py | Ananke, Ensorain, Hecate | 6 | 1 | 0.87 | 2026-09-23 |
| permutation_null.py | Charon, Harmonia, Lexis | 3 | 1 | 0.85 | 2026-05-30 |
| grammar.py | Archaeon, Nestor, Proteus | 6 | 3 | 0.85 | 2026-09-02 |
| base.py | Archaeon, Ergon, Theseus | 4 | 1 | 0.84 | 2026-05-04 |
| vm.py | Archaeon, Crius, Proteus | 4 | 1 | 0.84 | 2026-09-02 |
| sources.py | Artemis, Ergon, Techne | 4 | 1 | 0.84 | 2026-05-18 |
| verdict.py | Ares, Artemis, Charon | 3 | 1 | 0.84 | 2026-05-29 |
| conformance.py | Aphrodite, Archaeon, Vivarium | 3 | 1 | 0.84 | 2026-09-11 |
| db.py | Atlas, Charon, Vivarium | 3 | 1 | 0.83 | 2026-06-24 |
| probe.py | Ananke, Hermes, Odysseus | 7 | 1 | 0.83 | 2026-09-11 |
| ecology.py | Theophrastus, Theseus, Tyche | 3 | 1 | 0.83 | 2026-09-13 |
| evaluate.py | Ananke, Crius, Hecate | 38 | 1 | 0.82 | 2026-09-18 |
| test_controls.py | Aphrodite, Aporia, Theophrastus | 3 | 1 | 0.82 | 2026-06-10 |