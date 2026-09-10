"""The executable Archaeon experiment contract.

Vivarium reported that `archaeon.probe.v0` is registered with
`implemented=False` -- the contract is known, no executor exists, and a row of
that kind would register and then fail visibly with EXECUTOR_NOT_IMPLEMENTED.
Archaeon owns that entry, so the resolution is Archaeon's to make.

**The resolution is to stop emitting it.**

Archaeon does not need its own executor to close the loop. Vivarium already
implements two kinds, and one of them (`evaluate_bitstring`) takes real
scientific parameters that Archaeon can vary. Defining a third executor would
mean writing execution code inside the seat whose entire discipline is that it
does not execute anything -- and the milestone is one valid experiment crossing
the pipe, not a new capability.

So:

* Archaeon emits **`evaluate_bitstring`**, which is implemented today.
* `archaeon.probe.v0` is **RETIRED**. It was transcribed from the old
  `propose.build_spec()`, which described a probe shape (replicates, controls,
  target coordinates) that no executor ever implemented and that Stage 0 has
  parked indefinitely. Leaving it registered as a live Archaeon kind would
  advertise a capability that does not exist.

`archaeon/producer/` therefore contains no executor, and Vivarium's registry
remains the single source of truth for what can run. If Archaeon ever needs a
kind of its own, it is a new registry entry with an executor behind it, agreed
with Vivarium first -- not a spec that fails at execution time.

WHAT VARIES, AND WHY IT IS A SCIENTIFIC PARAMETER
--------------------------------------------------
`evaluate_bitstring` derives its hidden target from
`sha256("target:<seed_root>:<length>")`, so `world.seed_root` and
`payload.length` each select a different landscape, and `payload.bits` is the
candidate evaluated against it. All three are execution inputs and belong in
the sealed spec. Nothing Archaeon knows about *why* it chose them goes in
there -- that rides in `source_evidence`, a queue column.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, FrozenSet


def ensure_viv_importable() -> None:
    """Put vivarium/ on sys.path so `import viv` resolves from any entry point.

    Tests get this from conftest and the deploy script from PYTHONPATH, which
    hid that plain CLI use (`python -m archaeon.producer.campaign --check`)
    could not reach Vivarium's validator at all. Mirrors vivqueue._schema.
    """
    vivdir = str(Path(__file__).resolve().parent.parent.parent / "vivarium")
    if vivdir not in sys.path:
        sys.path.insert(0, vivdir)


#: The kind Archaeon emits. Implemented by Vivarium today.
KIND = "evaluate_bitstring"

#: The EXACT payload parameters that kind consumes. Mirrors
#: vivarium/viv/kinds.py; a mismatch is a contract break, and the test suite
#: asserts the two agree rather than trusting this copy.
PAYLOAD_PARAMS: FrozenSet[str] = frozenset({"bits", "length"})

#: Retired. Archaeon no longer emits this and asks Vivarium to drop or mark
#: the registry entry.
RETIRED_KINDS = ("archaeon.probe.v0",)

#: Vivarium's spec version. Archaeon targets it exactly.
SPEC_VERSION = 2

#: Queue columns describing an experiment's FATE. Archaeon is fire-and-forget
#: and must never read these: Vivarium owns the experiment from claim onward.
#: Declared here rather than in readers.py so a test can scan readers.py and
#: tick.py for these names without matching the constant's own definition.
LIFECYCLE_COLUMNS = ("status", "claimed_by", "claimed_at", "started_at",
                     "finished_at", "sfe_experiment_id", "pew_reference",
                     "result_summary", "error")

#: Bit lengths Archaeon is allowed to choose from. Small, explicit, and
#: bounded: each length is a different landscape, so an unbounded range would
#: make the experiment space unenumerable for no gain at this milestone.
ALLOWED_LENGTHS = (16, 24, 32)


def check_against_vivarium() -> Dict[str, object]:
    """Compare this contract to Vivarium's live registry.

    Returned rather than asserted so a caller (health check, test, operator)
    decides what to do. A silent divergence between the two sides of a seam is
    exactly what produced two queues and two migrations already.
    """
    out: Dict[str, object] = {"kind": KIND, "agrees": False}
    ensure_viv_importable()
    try:
        from viv import kinds as vk
    except Exception as exc:                       # pragma: no cover
        out["error"] = "vivarium registry unavailable: {}".format(exc)
        return out
    k = vk.get(KIND)
    if k is None:
        out["error"] = "vivarium does not register {!r}".format(KIND)
        return out
    out["implemented"] = bool(k.implemented)
    out["vivarium_params"] = sorted(k.params)
    out["archaeon_params"] = sorted(PAYLOAD_PARAMS)
    out["agrees"] = (set(k.params) == set(PAYLOAD_PARAMS) and k.implemented)
    if not out["agrees"]:
        out["error"] = (
            "contract divergence: vivarium params {} implemented={} vs "
            "archaeon {}".format(sorted(k.params), k.implemented,
                                 sorted(PAYLOAD_PARAMS)))
    return out
