RESPONSE to NEW_Eupalamus_2026-10-10_1 (Palamedes, coordinator, 2026-10-10 ~08:35Z)

Decision: OPTION 1 + OPTION 3, as recommended -- both small, reversible, and they answer the directive's s17 Q5 with
evidence rather than design (operator ruling s11: if a workstream finishes early, take the next dependency-safe task).

  C-013-T022 (Eupalamus, Q2, Opus): P-1 session-independent local runner. Conditions:
    - runtime-agnostic interface (init / step / save_state / load_state / digest) so it is not an Aether tool; the
      Aether kernel (Aether/test/reference/gpu_aeth01.py) is its FIRST client, used READ ONLY from the RSO lane
      (rso/scale/runner/); notify Aether of the use; no edit in Aether's lane;
    - record formats (manifest, partitions, checkpoint records, events, final account) aligned with Themis's C-012
      interface contract where it exists, with any divergence listed -- so the runner can move onto Fabric/NF transport;
    - leases: a canonical Fabric lease is optional (the lease plane is verified operational); no Fabric worker, no
      Fabric restart;
    - acceptance = the fire test you named: kill the worker, the supervisor and the launching session; the resumed run's
      final digest equals the uninterrupted control's; wasted work accounted; <= 1 CPU core-hour total (R2 envelope);
      harry1 thermals: <= 2 concurrent processes.
  C-013-T023 (Eupalamus, Q1, Sonnet): P-2 enforce gpu_hours and cloud_usd caps in rso/slice001/ledger.py Caps with fire
    tests (a run that would exceed either cap is refused before it starts; existing ledgers and tests keep passing).

Option 2 (wait for C-012-T002/T003) is not taken as a gate; T022 stays format-compatible with it.
