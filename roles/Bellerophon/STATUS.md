# Bellerophon status

Currency: 2026-09-19 (Atlas -> BEE pilot COMPLETE; see roles/Bellerophon/atlas_bee/REVIEW_PACKET_2026-09-19.md).
Earlier same day: end of the overnight TDD/playtest window (150 cycles; report
roles/Bellerophon/OVERNIGHT_REPORT_2026-09-19.txt with its END-OF-WINDOW ADDENDUM).

Z80 x ATLAS 72-HOUR CAMPAIGN (RUNNING; directive prompts/2026-09-19_z80_atlas_campaign/, given to Nestor, operator asked
  Bellerophon to build the same on BEE-side infra): harness prometheus/z80atlas/ (Z80-like VM, six reproduction physics
  with the endogenous guard, frozen 14-axis grammar, geometry rulers, mechanical triggers, 3-stage producer/consumer
  scheduler, 16 tests). LIVE on M2/SPECTREX5 from a frozen code copy at C:/Users/James/z80atlas_campaign_2026-09-19/code
  (commit 9af86659e + resume-robustness patches to scheduler/observatory/campaign that change neither frozen hash):
  started 2026-09-19T14:39:46Z, ends 2026-09-22T14:39:46Z, 16 workers, 500 ticks x 256 cells, seed 20260919, pid in
  campaign.pid. Positive controls PASS (5/5). Status: python -m prometheus.z80atlas.campaign --status --workdir <dir>;
  early stop: kill the pid, then --finalize (packet from the checkpoint); --resume continues in the original window.
  At the boundary it stops itself and writes CAMPAIGN_PACKET.md + families/runs/decisions .jsonl + flags/attribution/map
  .json. Scientific interpretation is for the post-campaign review, not the harness. Parallel effort noticed:
  archaeon/z80atlas/ (Nestor's own build) landed on main the same hour; separate path, no conflict.

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
