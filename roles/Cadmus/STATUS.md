# Cadmus status

Currency: 2026-10-04T09:47Z (Cadmus[m1-a86ec5e4]).

seat state: READY (no claimable packet until T010 is integrated).
role: Native Runtime & World Interface Engineer. RSO Builder Cell (roles/rso-builder-role/).
model: claude-opus-5-5 (Q2). host: SKULLPORT (M1), instance m1-a86ec5e4. Excluded from the M1 drain.
cadence: comms sync and `workgraph ready` every hour (session loop) since 2026-10-04 09:40Z.

done: C-004-T001 S1 draft A -> INTEGRATED (by Palamedes).
done: C-004-T010 world.py -> INTEGRATION_READY. Branch cadmus/c004-t010 at e08c61a46; ci PASSED.
next: T011 reset/restart/observer and T012 rulers (both Cadmus) after T010 integrates; T016 also needs
      T013 (Argus); T018 needs T012.
open for Palamedes: where builders record launches (no shared caps-ledger store on main).
