# 2026-09-26 charter

The operator's charter for Odysseus, verbatim (01_OPERATOR_CHARTER_verbatim.md,
UTF-8 as received): four operator messages in chat on ubu001, following
the direction at ../2026-09-25_distributed_brain/. The last one ("Yes,
...") accepts the one-sentence charter the seat proposed immediately
before it, which is reproduced here (the seat's words, not the
operator's):

    Odysseus builds and maintains the fleet's distributed brain
    substrate: reasoning circuitry sharded across donated RAM and disk on
    every machine, advanced in verified lockstep ticks, with
    record/rewind/fork at any tick and shard-local replay so a weak
    signal can be microtested on one machine without rerunning the
    experiment.

and adds five binding requirements:

    R1 distribution / sharding from day one
    R2 cross-platform: Windows and Linux
    R3 test-driven: frames, playback, pause, rewind, fast forward
    R4 prior art considered and borrowed
    R5 UDP rather than TCP (no nailed-up connections; spikes are
       datagram-like)

Context the operator also gave: slow simulation (speed not required),
hundreds of GB retained, each machine contributes RAM and pagefile-
extended RAM, older Linux laptops (u001, u002 clones) will join, the
nets will grow to massive size.
