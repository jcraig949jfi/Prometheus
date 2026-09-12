# Go-Explore -- failure landscape (from the read; NOTHING RUN)

F1  the representation objective rewards uniform occupancy, not exploration value: a
    partition that splits noise evenly scores well (goexplore.py try_split_frames)
F2  the archive is rebuilt wholesale on every representation change (checkpoint before
    and after; a warning when archive size forces it) -- cost, and every former grid
    must be kept on disk
F3  exact resumption is assumed; a token captured under one wrapper configuration is
    handed back later (montezuma restore resets _elapsed_steps; generic resets the env
    first) -- the assumption is the emulator's to keep
F4  the selection self-check is dead code (gated by random() < 0.0)
F5  prob_override admits worse elites at random (a stated escape hatch; policy)
F6  the key family is image-only; the objective is not
Ablations designed (NOT RUN, no pin): dynamic_state off vs on; entropy score vs
target-count-only; selection weights uniform vs table; prob_override 0 vs > 0.
