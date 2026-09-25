# Bellerophon status

Currency: 2026-09-25 ~06:45Z (written before a machine reboot + context reset).

BOOT POINTER -- READ FIRST: roles/Bellerophon/coupling_2026-09-24/RESUME_AFTER_RESET.md
  Coupling campaign RUNNING again since 2026-09-25T10:35:24Z under Amendment 1 (operator-authorised; active-runtime
  caps; detached supervisor with standing authority to recover crashes). If it is not running after a reboot, follow
  the UPDATE block at the top of RESUME_AFTER_RESET.md WITHOUT asking the operator.
seat state: ACTIVE (autonomous campaign; no HITL until the final report). Worktree
  D:/Prometheus-worktrees/bellerophon-post-campaign-forensics on branch bellerophon/coupling-campaign-2026-09-24.

COUPLING CAMPAIGN (physics v3) -- STOPPED BY HARNESS 2026-09-24T21:23Z, AWAITING OPERATOR RESTART
  Branch bellerophon/coupling-campaign-2026-09-24; prereg frozen c9bed96de (plan a3bc8c8e..., 11,372 Phase-1 runs);
  artifacts roles/Bellerophon/coupling_2026-09-24/. Started 20:07:31Z from pinned code
  C:/Users/James/z80atlas_coupling_2026-09-24/code. Stopped by Claude Code's low-memory reaper at 959 results
  (A 600/600, I 90/90, C 269/1800; 0 voids). Exact resume point: from the pinned code dir run
    python -m prometheus.z80atlas.coupling_campaign --workdir C:/Users/James/z80atlas_coupling_2026-09-24
           --inputs C:/Users/James/z80atlas_coupling_2026-09-24/coupling_inputs.json --workers N
  (re-executes only missing runs; caps from the first start: Phase 1 by 2026-09-25T14:07Z, total by 18:07Z).
  Memory: ~400 MB per worker; the machine was shared with ~48 other workers at the time.

POST-CAMPAIGN FORENSICS + GROUNDING ROUND COMPLETE (2026-09-23, Bellerophon[m2-9e74888e]; branch
  bellerophon/post-campaign-forensics-2026-09-23; artifacts roles/Bellerophon/forensics_2026-09-23/):
  POST_CAMPAIGN_FORENSICS.md, ISSUE_AND_REPAIR_LEDGER.md (34 rows), SPECIMEN_LEDGER.jsonl (2,188), GROUNDING_PREREG.md
  (frozen a1b066309), GROUNDING_REPORT.md (12,130/12,130 runs, 16:46:50Z), NEXT_CAMPAIGN_RECOMMENDATION.md.
  Verdict: all five historical flag classes collapsed; spontaneous own-code self-replication CONFIRMED_CAUSAL;
  instrument READY; physics NOT ready for a multi-day run: no pathway by which computation affects reproduction.
  Next executable action: design + preregister ONE reproduction-computation coupling and a <= 6 h pilot (NEXT_...
  part B2) -- awaiting operator direction before building it. Local evidence: C:/Users/James/z80atlas_grounding_2026-09-23.
  Note (D3): this file at 2df98af3e called archaeon/z80atlas "Nestor's own build"; it is Archaeon's (c7610ea19).

DIRECTIVE (being executed):
  prompts/2026-09-23_post_campaign_forensics/00_OPERATOR_DIRECTIVE_verbatim.md
  Read it in full before taking any action. It is a 10-phase forensic + grounding mandate, not a
  campaign launch. The directive is authoritative; this STATUS entry is only a pointer to it.

Z80 x ATLAS 72-HOUR CAMPAIGN (COMPLETE 2026-09-22T14:38:42Z):
  63,247 runs / 49,412 families / 1,629 high-value flags. Final local evidence:
    workdir:  C:/Users/James/z80atlas_campaign_2026-09-19/
    packet:   C:/Users/James/z80atlas_campaign_2026-09-19/CAMPAIGN_PACKET.md  (NOT in git — local only)
    harness:  prometheus/z80atlas/ (commit 98b2149a7 + subsequent patches)
  DO NOT mistake earlier 44.6h snapshot numbers for the final campaign.
  Scientific interpretation is the subject of the next directive above.

ATLAS -> BEE PILOT (temporary experimental role, directive prompts/2026-09-19_atlas_bee_pilot/): does BEE
  (prometheus/toolbox) work as a THIRD ecosystem alongside SFE and NPE? Six Atlas experiments selected and FROZEN
  (SELECTION_FROZEN.json), a light shim built (prometheus/atlas_bee/: freeze/manifest/harness/run/atlas_feed +
  a1..a6), each question instantiated NATIVELY in BEE, frozen (PREREG_a*.json, hashed), run, replayed bit-for-bit
  (replay_ok all six), compared (RESULT_a*.json). Verdicts: a1 INVERTED (overfitting-to-seed), a2 CHANGED
  (subadditive 0.03), a3 CHANGED (recurrence-necessity inverted), a4 ABSENT (offspring cap unrepresentable), a5
  ABSENT (delay-invariant optimum), a6 PRESERVED (P1 refuses as e07). Every case exposed a mechanism the source
  ecosystem could not. BEE-native scaffolding added to the kernel with tests + mutants (M87-M93 CAUGHT): sequence.v1,
  battery, seed_players, episode recurrence, kv_weather, objective.charge.v1. Recommendation: ADMIT BEE as a third
  ecosystem for DIFFERENTIAL cross-ecosystem transplant studies. Atlas feed harvester-ready (ATLAS_FEED.jsonl) +
  smallest-extension proposal (ATLAS_EXTENSION_PROPOSAL.md); nothing written to Atlas (read-only seat).

seat state: ACTIVE. Charter in force: the WORLDS KERNEL directive
  (prompts/2026-09-18_worlds_kernel/, sha256 fc819348...). D-BELL-1..4
  adopted as the operator wrote them. Overnight directive
  (prompts/2026-09-19_overnight_tdd/) executed 02:49Z-09:49Z.
what it asserts: PRESENT (comms Bellerophon[m2-c95cc146]), ACTIVE,
  PRODUCTIVE at the kernel layer: prometheus/toolbox/ -- 1421 passed, 6 skipped (Redis);
  mutation ledger 85/85 CAUGHT (honest since C95: the
  instrument can say SURVIVED, and did once, M66); 42/42
  components admitted; 300-seed fuzz on both execution paths 0 crashes /
  0 divergences; cross-platform replay probe back (WSL). VALID: the
  kernel claims nothing about any world; its receipts are the evidence
  for itself only. Science of all committed playtests byte-stable across
  the night (838 runs reproduce their trace hashes and objectives).
workspace: worktree bellerophon-base-role on M2 / SPECTREX5, branch
  bellerophon/overnight-tdd-2026-09-19 (== origin/main at 8e921fb66 + the final commit).
comms: M1 store; queue empty at last sync.
monitors owned or fed: none; no MONITORS.md row (nothing loops).
lane: the kernel (contracts, IR, capabilities, devices, adapters,
  references, admission, lowering, conformance tests, instrument power).
lowering status: local OK (scalar and batched paths, equal run for run);
  sfe TARGET_UNSUPPORTED for a general IR (M1-M6 classified) and OK for a
  frontier-shaped IR, runtime executor passes the new IR fields through;
  npe UNAVAILABLE_INTERFACE by D-BELL-2.
what changed overnight (second half): batched execution as EXECUTION
  POLICY (its throughput premise falsified, science/BATCH_THROUGHPUT);
  vector objectives (rank or refuse; pareto selector); structured
  observations; control POWER (every control can say NO, POWER_REGISTER);
  spec identity vs behavioural class; survival v2 / per-player; compact
  archives; two soaks; design v0.4.
blockers: none for the next slice. Held by decision: Techne/Nyx drafts
  (D-BELL-4); Box2D (phase order; now the named reopen condition for
  batching); NPE bridge (D-BELL-2); Redis acceptance (needs M1).
next executable action: the three pressures in the report addendum s18
  (columnar-contract world family; Redis on M1 + NPE worker; a Crius
  experiment in the IR with a vector objective and structured
  observations).
