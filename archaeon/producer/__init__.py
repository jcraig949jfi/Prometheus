"""Archaeon's autonomous producer: the boring half of the seat.

    PEW/SFE fossils -> tick() -> queue -> Vivarium -> SFE -> PEW -> tick()

One decision per tick, at most one experiment written, no model in the path.
Every component is importable and testable on its own:

    readers.py    what happened recently (fossils + this seat's own history)
    contract.py   the executable experiment vocabulary Vivarium can run
    randomgen.py  a boring valid experiment when no signal fires
    specbuild.py  build + validate against Vivarium's spec v2
    tick.py       the composition, and the only thing the loop calls
    loop.py       the daemon

Deliberately NOT here: Stage 0, family F1, S17 eligibility, arm fossil
semantics. Those are parked (`archaeon/docs/STAGE0_RESULT.md`,
`PROSPECTIVE_FAMILY_F1.md`) and this package does not import them.
"""
__all__ = ["readers", "contract", "randomgen", "specbuild", "tick", "loop"]
