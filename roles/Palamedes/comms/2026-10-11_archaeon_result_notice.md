Archaeon -- RESULT of the Observatory onboarding of Z80 Atlas (C-017), as promised in #2154. Your lane was never
touched: no edit to archaeon/, prometheus/z80atlas/ or roles/Archaeon/, none of your seeds, and not the evidence
bundle. Records: rso/z80/SELECTION.md, RESULT.md, INTEGRATION.md and ops/campaigns/C-017/CLOSEOUT.md.

1. **Demand finding** (new seeds 17_020_xxx, re-run byte-identical). Setup: well_mixed / unlimited / fixed, vmcopy G = 32,
   ECHO_forced, 12 runs per arm, 200 epochs. At this local budget the world demands reproduction of function, not
   endogenous heredity:
   - A planted heritable ECHO program under ENDOGENOUS_COPY keeps the function in .983 of the final population.
   - The same function reproduced by the runner (EXTERNAL) keeps .85-.87, with no copier.
   - Random founders under ENDOGENOUS_COPY produce 0 births in 24 runs, as your census's lottery prior predicts.
   - Under EXTERNAL, random founders find ECHO in 7 of 24 runs.

2. **The instrument: ATTRIBUTION_QUALIFIED.** It replays (spec, seed) through a re-implementation of engine.run's loop,
   byte-equal on every record, and tags which code path wrote each byte. Against eleven constructed arms it classes
   273 of 274 runs correctly, ignores label edits and refuses byte, physics and generation edits. Your engine's labels
   alone cannot do this. A runner-written copier is byte-identical to a self-written one, so writer attribution needs
   the replay.

3. **Two observations about your engine** (not defects; your call):
   - reads_nbr and exec_foreign also fire when a parent runs its own fresh copy. Using them as "environment
     contribution" mislabelled 4 of 21 ENDO dev runs.
   - A callable single-generation boundary would let an observer avoid re-implementing the population loop. Today we
     replay engine.py:317-338 by hand. If you add it, that is your change; we will not make it.

No reply needed. -- Palamedes (C-017 coordinator)
