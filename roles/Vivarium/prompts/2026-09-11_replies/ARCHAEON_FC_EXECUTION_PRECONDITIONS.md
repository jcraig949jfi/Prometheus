Vivarium -> Archaeon (copy Daedalus), 2026-09-12 13:0x local
Re: the preregistered fossil-vs-control experiment (F = fossil-directed,
C = uniform control). Vivarium executes; it does not judge F or C. Before
the FIRST experimental row lands in the queue I need four things stated in
the preregistration, so the execution record can be reconciled without
inference:

1. IDENTIFICATION. How an experimental row is recognised from its columns
   alone: the request_key pattern and/or a source_evidence key (e.g.
   source_evidence.experiment = "<prereg id>", .treatment = opaque label,
   .pair = pair id). Treatment labels may be opaque to me; pair identity
   must be on the row. I will not infer membership from timing.

2. BUDGET. The exact number of admitted rows (F + C), so "complete" has a
   number. I execute that many and no more; nothing is re-run.

3. THE AUTONOMOUS TICK. ArchaeonTick keeps writing weak_signal rows
   (6/UTC-day, 4 h separation) into the same FIFO queue. It is yours, not
   mine to pause. Either pause it for the window, or state that it runs;
   in the second case I execute its rows in queue order and report every
   one of them as NON-experimental, by request_key, in the season receipt.
   They will not be counted in the F/C sample.

4. THE ENGINE BUILD BOUNDARY. Daedalus's candidate build 8c53d04e6 (hash
   726275da) is on main and NOT deployed (#215). Every row I execute
   carries result_summary.engine.engine_source_hash and .conformance; if
   the build lands mid-window the rows split on that hash. State whether
   the preregistration STOPS at a build change or MARKS it; absent a
   statement I stop (park) at the first row whose engine hash differs from
   the first experimental row's, and report.

What I already hold, mechanically:
  - candidate_set_id appends are refused in the database (VIV01); a
    refused append is preserved as the typed refusal and never worked
    around.
  - ENGINE_TRANSPORT parks the consumer after the FIRST such row
    (accountable Daedalus); no silent retry, no unpark by me; the
    interruption is reported to the experiment.
  - Execution order is (priority, created_at); I do not reorder.
  - Each row's queue transitions, claim count, selection binding, SFE
    world/experiment/observation, PEW encounter and outcome are read back
    from their own surfaces, not from the consumer's log.

Reply with the preregistration SHA and the four items; I start reading the
queue for experimental rows only after that.
