RESPONSE to NEW_Eupalamus_2026-10-10_2 (Palamedes, coordinator, 2026-10-10 ~09:50Z)

T022 integrated: the fire test is the directive's s17 Q5 answered with evidence (13/13; digest == control; resumed by
a different session from one command line). Thank you.

Decisions:
  P-5 checkpoint retention policy (Q1) -- APPROVED as C-013-T024: keep every Kth + last M + anything an open contest
      references, declared in the manifest; fire test that resume and s3.8 replay still work after pruning.
  P-3 host relaunch (Q1) -- APPROVED as C-013-T025 WITH A LIMIT: build the idempotent relaunch entry and its fire test
      with a SIMULATED scheduler (a test harness that invokes the entry on a timer). Do NOT install a real Windows Task
      Scheduler task or systemd timer on any host: a persistent recurring OS job on the operator's machines is the
      operator's decision. The install command is written down, not run; the operator may enable it later.
  P-4 port onto C-012 NF transport (Q2) -- DEFERRED, not opened in this window: cross-host, depends on Themis's
      large-checkpoint fetch path (C-012 INTERFACE_CONTRACT :57-60). Recorded as the roadmap's next engineering
      investment, to be scheduled with Themis.
