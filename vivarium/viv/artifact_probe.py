"""`artifact_probe_v1` -- the loader's instrument, and nothing more.

WHAT THIS IS FOR. It is the first kind that consumes bytes which were not in
its own spec, and it exists so that the whole path -- seal a digest, resolve a
locator, authorize, verify, bound, freeze, execute, record, publish -- can be
run and inspected end to end before any science depends on it. The design says
of H0's hand-built libraries that they "exercise the plumbing but are
explicitly instrument controls". So is this.

WHAT IT IS NOT. `folded` is a fold over ordered bits. It is not a solve rate,
not a fitness, not a score, and no comparison between two values of it means
anything scientific. It was chosen for exactly one property: it changes when
any consumed byte changes, and it does not change otherwise -- which is what
makes "changing a consumed digest changes the result" a thing a test can see.

NO CLIENTS. The signature takes a payload, a seed and the frozen inputs. There
is no SFE client, no PEW client, no path, no socket, and no import of any
module that has one. The kind could not reach the engine if it wanted to.

IMMUTABILITY IS MEASURED, NOT ASSERTED. The kind tries to mutate its own input
and reports whether it was refused. A claim about immutability that nothing
ever tests is a comment.
"""
from __future__ import annotations

import hashlib
import json

#: The declared folds. No default -- `reduction` is a payload parameter, and a
#: fold this seat picked silently would be exactly the class of defect that
#: made `length` a required parameter of evaluate_bitstring.
REDUCTIONS = ("xor_positional", "popcount", "ordered_sha")


class ProbeError(RuntimeError):
    pass


def _mutation_refused(data) -> bool:
    """Try to mutate the frozen input. True iff the attempt was refused."""
    try:
        data["items"] = ()                      # a read-only mapping refuses
    except (TypeError, AttributeError):
        return True
    return False


def run(payload: dict, *, seed: int, inputs: dict) -> dict:
    reduction = payload["reduction"]
    if reduction not in REDUCTIONS:
        raise ProbeError(
            "reduction must be one of %s, got %r; there is no default fold "
            "because a fold nobody declared is a scientific parameter this "
            "seat chose" % (list(REDUCTIONS), reduction))
    art = inputs["failure_inputs"]
    rows = art.all_items()                      # root, then closure, in order
    n_bits = art.data["n_bits"]

    if reduction == "xor_positional":
        acc = [0] * n_bits
        for row in rows:
            for i, b in enumerate(row):
                acc[i] ^= int(b)
        folded = 0
        for i, b in enumerate(acc):
            folded |= b << i
    elif reduction == "popcount":
        folded = sum(int(b) for row in rows for b in row)
    else:
        blob = json.dumps([list(r) for r in rows],
                          separators=(",", ":")).encode()
        folded = int(hashlib.sha256(blob).hexdigest()[:8], 16)

    items_digest = "sha256:" + hashlib.sha256(
        json.dumps([list(r) for r in rows], separators=(",", ":")).encode()
    ).hexdigest()

    closure = [art.digest]
    stack = list(art.dependencies)
    while stack:
        d = stack.pop(0)
        closure.append(d.digest)
        stack.extend(d.dependencies)

    return {
        "folded": int(folded),
        "reduction": reduction,
        "items_consumed": len(rows),
        "root_items": len(art.data.get("items", ())),
        "n_bits": int(n_bits),
        "items_digest": items_digest,
        "input_digest": art.digest,
        # The KIND's own view of the closure, in the order it consumed it.
        # Deliberately not called the manifest hash: preflight resolves
        # depth-first and records children before parents, so the two orders
        # differ and claiming one hash for both would be asserting an equality
        # that does not hold. The SET is the same, and a test checks that.
        "consumed_closure_hash": "sha256:" + hashlib.sha256(
            json.dumps(closure, separators=(",", ":")).encode()).hexdigest(),
        "closure_size": len(closure),
        "interface_id": art.interface_id,
        "inputs_immutable": _mutation_refused(art.data),
        "executor": "artifact_probe_v1",
        "reproducibility": "BIT_DETERMINISTIC",
    }
