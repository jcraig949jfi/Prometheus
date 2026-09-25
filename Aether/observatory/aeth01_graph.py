"""Functional-graph measurement over the causal-edge side-channel.

Consumes what `gpu_step(..., observer=[])` exported and measures the
temporal functional graph. It never materializes a lattice-wide edge
list: at 4096^2 a tick is several million edges and 50,000 ticks is on
the order of 1e11, so ordinary traffic is aggregated on device and exact
edges are extracted only inside a small window.

THE STRUCTURAL FACT THIS MODULE IS BUILT ON, measured not assumed
(test_aeth01_causal_edges.py): a writer's direction and target field come
from its own arg0/arg1, so it emits exactly ONE proposal per tick and
realized out-degree is 1. The per-tick realized edge set is therefore a
PARTIAL FUNCTION on sites. Consequences used here:

  - every weakly connected component is one cycle with in-trees;
  - strongly connected components larger than a node are exactly those
    cycles, so cycle detection replaces any general SCC algorithm;
  - out-degree is degenerately 1, so fan-in (`contenders`) carries all
    the degree information;
  - pointer doubling lands every node on its own cycle in
    ceil(log2 N) gathers, which is how cycle membership is obtained
    lattice-wide without a host-side graph.

These are consequences of the transition law, not findings, and
NATIVE_CIRCUITRY_01_PREREGISTRATION_2026-09-23.md requires them to be
reported as such.

Nothing here writes to a lattice and nothing here assigns a
HABITABILITY.md label or a claim-ladder tier.
"""

import numpy as np

NO_WINNER = 255
FIELD_NAMES = ("opcode", "arg0", "arg1", "payload", "energy")
# Must match _NEIGHBOR_SLOTS in the kernel: (row_offset, col_offset).
SLOT_OFFSETS = ((-1, 0), (1, 0), (0, 1), (0, -1))


def _host(value):
    return getattr(value, "get", lambda: value)()


def _host_int(value):
    return int(_host(value))


def unpack(entry):
    """(winner_slot, contenders, n_differ). n_differ is None on records
    written before the kernel exported it, so older evidence still loads."""
    return entry[0], entry[1], (entry[2] if len(entry) > 2 else None)


# Edge classes, per the operator's 2026-09-24 directive. Naming is
# deliberately mechanical: NONE of these names asserts function.
# "same value" does NOT mean "no function" -- a contested same-value
# write may gate a different value out, and a persistent same-value
# structure may hold state. Only intervention can tell.
CLASSES = ("STATE_CHANGING", "SAME_VALUE_UNCONTESTED",
           "SAME_VALUE_CONTESTED_ALTERNATIVE_CHANGE",
           "SAME_VALUE_CONTESTED_NO_ALTERNATIVE_CHANGE")


def realized_map(xp, observer, h, w):
    """Flat int64 array: map[source] = target, or -1 where nothing won.

    Out-degree 1 means no two fields can claim the same source, so the
    scatter below cannot collide. `assert_partial_function` checks that
    rather than trusting it.
    """
    n = h * w
    nxt = xp.full(n, -1, dtype=xp.int64)
    rows = xp.arange(h, dtype=xp.int64).reshape(h, 1)
    cols = xp.arange(w, dtype=xp.int64).reshape(1, w)
    for field, entry in enumerate(observer):
        winner_slot = unpack(entry)[0]
        for slot, (dr, dc) in enumerate(SLOT_OFFSETS):
            mask = winner_slot == slot
            if not _host_int(mask.sum()):
                continue
            src = (((rows + dr) % h) * w + ((cols + dc) % w))
            target = (rows * w + cols)
            nxt[src[mask]] = target[xp.broadcast_to(mask, (h, w))]
    return nxt


def assert_partial_function(xp, observer, h, w):
    """Every source appears at most once across all five fields.

    If this ever fails, the out-degree-1 reasoning this module rests on
    is wrong and every graph statistic below is meaningless.
    """
    n = h * w
    counts = xp.zeros(n, dtype=xp.int64)
    rows = xp.arange(h, dtype=xp.int64).reshape(h, 1)
    cols = xp.arange(w, dtype=xp.int64).reshape(1, w)
    for _field, entry in enumerate(observer):
        winner_slot = unpack(entry)[0]
        for slot, (dr, dc) in enumerate(SLOT_OFFSETS):
            mask = winner_slot == slot
            if not _host_int(mask.sum()):
                continue
            src = (((rows + dr) % h) * w + ((cols + dc) % w))
            counts = counts + xp.bincount(src[mask].ravel(), minlength=n)
    return _host_int(counts.max()) if n else 0


def cycle_node_count(xp, nxt, max_doublings=None):
    """How many sites lie on a cycle of the realized map.

    Pointer doubling: after k doublings a walk of 2^k steps has been
    taken, and once 2^k >= N every start has entered its cycle, so the
    image of the map power is exactly the set of cycle nodes. Undefined
    entries (-1) are held fixed at -1 and excluded.

    Exact, and bounded at ceil(log2 N) gathers rather than depending on
    tree depth, which a peeling algorithm would.
    """
    n = int(nxt.shape[0])
    if n == 0:
        return 0, 0
    safe = xp.where(nxt < 0, xp.arange(n, dtype=nxt.dtype), nxt)
    dead = nxt < 0
    steps = max_doublings
    if steps is None:
        steps = max(1, int(np.ceil(np.log2(max(n, 2)))))
    cur = safe
    for _ in range(steps):
        cur = cur[cur]
    reached = xp.zeros(n, dtype=xp.uint8)
    live = cur[~dead] if _host_int(dead.sum()) else cur
    if live.shape[0]:
        reached[live] = 1
    reached[dead] = 0
    return _host_int(reached.sum()), steps


def cycle_node_mask(xp, nxt, max_doublings=None):
    """The cycle-membership mask itself, not just its count.

    Needed to condition edge classes on "is this edge's target part of a
    cycle", which is how the directive's "changed-edge fraction within
    persistent structures" is measured.
    """
    n = int(nxt.shape[0])
    if n == 0:
        return xp.zeros(0, dtype=xp.uint8), 0, 0
    safe = xp.where(nxt < 0, xp.arange(n, dtype=nxt.dtype), nxt)
    dead = nxt < 0
    steps = max_doublings or max(1, int(np.ceil(np.log2(max(n, 2)))))
    cur = safe
    for _ in range(steps):
        cur = cur[cur]
    reached = xp.zeros(n, dtype=xp.uint8)
    live = cur[~dead] if _host_int(dead.sum()) else cur
    if live.shape[0]:
        reached[live] = 1
    reached[dead] = 0
    return reached, _host_int(reached.sum()), steps


def edge_classes(xp, observer, before, after, restrict=None):
    """The four-way edge classification, per field, energy kept separate.

    `restrict` is an optional boolean (h, w) mask on the TARGET, used to
    report the classes inside persistent structures rather than over the
    whole lattice.

    CAVEAT, recorded rather than hidden: an edge whose winner proposed a
    differing value which perturbation then flipped back to the original
    would be counted as same-value. That needs the perturbed bit to
    exactly undo the difference, so it is astronomically rare, but it is
    not impossible.

    NOTHING HERE ASSERTS FUNCTION. A same-value uncontested edge may be a
    trivial refresh; a same-value CONTESTED edge may gate a different
    value out; a persistent same-value structure may hold state. Only
    intervention distinguishes those.
    """
    out = {}
    for field, entry in enumerate(observer):
        winner_slot, contenders, n_differ = unpack(entry)
        has = winner_slot != NO_WINNER
        if restrict is not None:
            has = has & restrict
        changed = before[field] != after[field]
        same = has & (~changed)
        contested = contenders >= 2
        row = {
            "edges": _host_int(has.sum()),
            "STATE_CHANGING": _host_int((has & changed).sum()),
            "SAME_VALUE_UNCONTESTED": _host_int((same & (contenders == 1)).sum()),
        }
        if n_differ is None:
            row["SAME_VALUE_CONTESTED_ALTERNATIVE_CHANGE"] = None
            row["SAME_VALUE_CONTESTED_NO_ALTERNATIVE_CHANGE"] = None
        else:
            row["SAME_VALUE_CONTESTED_ALTERNATIVE_CHANGE"] = _host_int(
                (same & contested & (n_differ >= 1)).sum())
            row["SAME_VALUE_CONTESTED_NO_ALTERNATIVE_CHANGE"] = _host_int(
                (same & contested & (n_differ == 0)).sum())
        out[FIELD_NAMES[field]] = row
    return out


def edge_aggregates(xp, observer, before, after):
    """Per-tick aggregates. No edge list is built.

    `changed` counts edges whose target value actually differs from last
    tick. An edge that rewrote the same value is a real causal edge and
    is counted in `edges`, but it moved no information, so the two are
    reported separately rather than conflated.
    """
    out = {"edges_total": 0, "edges_by_field": {}, "changed_by_field": {},
           "fan_in_hist": {}, "slot_hist": {}}
    for field, entry in enumerate(observer):
        winner_slot, contenders, _nd = unpack(entry)
        name = FIELD_NAMES[field]
        has = winner_slot != NO_WINNER
        edges = _host_int(has.sum())
        differs = before[field] != after[field]
        out["edges_by_field"][name] = edges
        out["changed_by_field"][name] = _host_int((has & differs).sum())
        out["edges_total"] += edges
        fan = xp.bincount(contenders.ravel(), minlength=5)
        out["fan_in_hist"][name] = [int(v) for v in _host(fan)[:5]]
        slots = xp.bincount(winner_slot.ravel()[has.ravel()], minlength=4) \
            if edges else xp.zeros(4, dtype=xp.int64)
        out["slot_hist"][name] = [int(v) for v in _host(slots)[:4]]
    return out


def new_runlengths(xp, h, w):
    """Persistence state: last tick's winner and a run-length counter.

    10 bytes/site (5 fields x uint8 winner + 5 x uint16 counter). This is
    what gives recurring-edge statistics WITHOUT storing edges.
    """
    return {
        "last": [xp.full((h, w), NO_WINNER, dtype=xp.uint8) for _ in range(5)],
        "run": [xp.zeros((h, w), dtype=xp.uint16) for _ in range(5)],
    }


def update_runlengths(xp, state, observer):
    """Consecutive ticks each edge has been present with the SAME winner.

    An edge appearing for the first time has run length 1, not 0: the
    preregistered candidate thresholds are stated as "at least 16
    consecutive ticks", so a counter of REPEATS rather than of ticks
    present would be off by one against its own definition.

    Saturates at uint16 max. The bump is computed as
    `minimum(run, 65534) + 1` rather than `minimum(run + 1, 65535)`
    because the latter overflows to 0 at 65535 BEFORE the minimum is
    applied, and a wrapped counter reads as a brand-new edge and
    understates persistence.
    """
    stats = {}
    for field, entry in enumerate(observer):
        winner_slot = unpack(entry)[0]
        present = winner_slot != NO_WINNER
        same = present & (winner_slot == state["last"][field])
        run = state["run"][field]
        bumped = xp.minimum(run, xp.uint16(65534)) + xp.uint16(1)
        run = xp.where(present, xp.where(same, bumped, xp.uint16(1)),
                       xp.zeros_like(run))
        state["run"][field] = run
        state["last"][field] = winner_slot.copy()
        live = run[run > 0]
        stats[FIELD_NAMES[field]] = {
            "edges_present": _host_int((run >= 1).sum()),
            "repeating_edges": _host_int((run >= 2).sum()),
            "run_max": _host_int(run.max()) if run.size else 0,
            "run_mean": float(_host(live.mean())) if live.size else 0.0,
            "run_ge_16": _host_int((run >= 16).sum()),
            "run_ge_64": _host_int((run >= 64).sum()),
        }
    return stats


def window_edges(observer, h, w, r0, c0, size, runs=None):
    """Exact edge list inside one window. Host-side, small by construction.

    Returns dicts with the fields the directive asks for at edge level.
    A source outside the window is still reported: the window bounds
    which TARGETS are captured, not which sources may reach them, because
    clipping sources would silently hide inbound edges.
    """
    edges = []
    for field, entry in enumerate(observer):
        winner_slot, contenders, n_differ = unpack(entry)
        ws = np.asarray(_host(winner_slot))[r0:r0 + size, c0:c0 + size]
        cs = np.asarray(_host(contenders))[r0:r0 + size, c0:c0 + size]
        nd = (np.asarray(_host(n_differ))[r0:r0 + size, c0:c0 + size]
              if n_differ is not None else None)
        rl = (np.asarray(_host(runs[field]))[r0:r0 + size, c0:c0 + size]
              if runs is not None else None)
        rows, cols = np.nonzero(ws != NO_WINNER)
        for r, c in zip(rows.tolist(), cols.tolist()):
            slot = int(ws[r, c])
            dr, dc = SLOT_OFFSETS[slot]
            tr, tc = r0 + r, c0 + c
            edges.append({
                "target": [tr, tc],
                "source": [(tr + dr) % h, (tc + dc) % w],
                "field": field,
                "slot": slot,
                "contenders": int(cs[r, c]),
                "n_differ": (int(nd[r, c]) if nd is not None else -1),
                "run": (int(rl[r, c]) if rl is not None else -1),
            })
    return edges


def window_origin(mix64_scalar, seed, h, w, size, salt_row=0xA02, salt_col=0xB02):
    """WINDOW_B's preregistered origin, from the world's own physics seed.

    Fixed by the run configuration and computable before the run starts,
    so it cannot be chosen after seeing data
    (NATIVE_CIRCUITRY_01_PREREGISTRATION_2026-09-23.md section 4).
    """
    span_r = max(1, h - size)
    span_c = max(1, w - size)
    return (int(mix64_scalar(seed ^ salt_row)) % span_r,
            int(mix64_scalar(seed ^ salt_col)) % span_c)
