OPERATOR RULING (relayed verbatim by Vivarium from chat, 2026-09-16 ~13:0x UTC)

  Q1: a
  Q2: copy both existing tokens.
  Proceed with the relocation as prepared; do not mint replacement identity.

Context the ruling answers (roles/Vivarium/prompts/2026-09-16_m1_reboot/
OPERATOR_GATE_TOKENS_TO_M2.md and the two chat questions):
  (a) = M1's ledger eng_8a37a5d3 is carried to M2 (Daedalus #270 steps 1-4
        stand); the twin eng_906356f7 is never promoted.
  tokens = F:\Prometheus-worktrees\vivarium-consumer\vivarium\config.local.json
        on M1 is copied, as a file, to
        D:\Prometheus-worktrees\vivarium-consumer\vivarium\config.local.json
        on M2. No new client, no new scope, no new grant is minted by any
        seat for this consumer.
  Earlier in the same session the operator ruled the topology: Postgres and
  Redis shared (the M1 cluster); every other service on ONE machine, the SFE
  ecosystem on M2; no farm.

Who does what now
  operator   physical copies M1 -> M2 (no share reaches either way from M2;
             \\192.168.1.202\F$ and D$ are access-denied, net view error 5):
               1. D:\Prometheus-data\sfe (engine.db, blobs, backup) for
                  Daedalus's step 1;
               2. the one gitignored token file above for Vivarium.
  Daedalus   #270 steps 1-4 once (1) lands: verify identity, swap, restart
             the same build, post URL + /v2/version + contract state.
  Harmonia   promote the staged contract against 192.168.1.191.
  Vivarium   watching for BOTH: config.local.json present in the pinned
             worktree AND /v2/version at 192.168.1.191:8811 reporting
             eng_8a37a5d3. Then: prepare_m2.py --sha <SHA> --register must
             read green -> schtasks /Change /TN VivariumDeadmanM2 /ENABLE
             (the launch) -> post heartbeat + the 5 rows' outcomes.
