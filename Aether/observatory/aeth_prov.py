"""prov0 -- external value-provenance observatory for Aether (V2-B DEV-1).

A SHADOW that runs beside the physics and never feeds anything back into it. Each tick it reads the pre-tick
state, the kernel's existing read-only `observer` export (the winning neighbour slot per target and field) and the
post-tick state, and records, for every committed TEMPLATE value (fields opcode/arg0/arg1/payload), a node:

    INIT  leaf (the value present when tracking starts)
    COPY  replacement by the winning proposal                1 parent: the proposal's value node
    ADD   add-family composition                             2 parents: previous target node, proposal node
    +MUT  flag on a COPY/ADD node whose committed byte got a perturbation bit flip (event: bit index)

Losing proposals are never parents. Sites without a winning write keep their node. Energy (field 4) is
bookkeeping, not a content lineage, in prov0 (a stated limit).

The proposal's value node is the SOURCE's payload node, except for an `fwd` relay, which emits the byte it received
on the previous tick; prov0 tracks that byte's node (payload > arg1 > arg0 > opcode priority, as the law does).

SELF-CHECK (the observatory's own P0): every tick the shadow recomputes the committed byte from its parents' values
and the law's commit rule and compares it with the physics output, for every site and template field. Any mismatch
raises ProvenanceMismatch, so the shadow cannot silently drift from the law.

Lineage tracking: up to 64 ORIGINS (chosen nodes) are tracked as a bitmask per node. A node's mask is the OR of its
parents'; `hops` is 1 + the max hops of its lineage-carrying parents. That makes P3 (carried), P4 (transformed: value
differs from the origin's value), P5 (composed: two or more origin bits) and P6 (persisted: hops) cheap to read.
"""
from __future__ import annotations

import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_AETHER = os.path.dirname(_HERE)
for _p in (_AETHER, os.path.join(_AETHER, "test", "reference")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gpu_aeth01 as K                                   # noqa: E402
from observatory import aeth03_variants as V             # noqa: E402

PROV_VERSION = "prov0"
OP_INIT, OP_COPY, OP_ADD = 0, 1, 2
OP_MUT = 4                                                # flag bit
SUPPORTED = ("v1", "add", "hys", "chg", "cnd", "str", "rcv", "m4", "fwd",
             "rcv_add", "rcv_cnd", "rcv_str", "rcv_sfx", "rcv_adr", "rcv_sfz")
ADD_FAMILY = ("add", "rcv_add")


class ProvenanceMismatch(AssertionError):
    pass


class Provenance:
    """Append-only node table plus, per site and template field, the id of the node currently stored there."""

    def __init__(self, variant, fields, received_value=None):
        if variant not in SUPPORTED:
            raise ValueError("prov0 does not model variant %r" % (variant,))
        self.variant = variant
        h, w = fields[0].shape
        self.H, self.W = h, w
        n0 = 4 * h * w
        self.op = [np.zeros(n0, np.int8)]
        self.p1 = [np.full(n0, -1, np.int64)]
        self.p2 = [np.full(n0, -1, np.int64)]
        self.tick = [np.zeros(n0, np.int32)]
        self.site = [np.tile(np.arange(h * w, dtype=np.int64), 4)]
        self.field = [np.repeat(np.arange(4, dtype=np.int8), h * w)]
        self.value = [np.concatenate([fields[f].astype(np.int16).ravel() for f in range(4)])]
        self.mask = [np.zeros(n0, np.uint64)]
        self.hops = [np.zeros(n0, np.int32)]
        self.n = n0
        self.cur = [np.arange(f * h * w, (f + 1) * h * w, dtype=np.int64).reshape(h, w) for f in range(4)]
        # fwd: node of the byte each site received last tick (-1 where none). A received byte already present when
        # tracking starts (e.g. after warm-up) gets its own INIT node (field code 9 = "received byte").
        self.rv_node = np.full((h, w), -1, np.int64)
        if variant == "fwd" and received_value is not None:
            m = h * w
            self.op.append(np.zeros(m, np.int8)); self.p1.append(np.full(m, -1, np.int64))
            self.p2.append(np.full(m, -1, np.int64)); self.tick.append(np.zeros(m, np.int32))
            self.site.append(np.arange(m, dtype=np.int64)); self.field.append(np.full(m, 9, np.int8))
            self.value.append(received_value.astype(np.int16).ravel()); self.mask.append(np.zeros(m, np.uint64))
            self.hops.append(np.zeros(m, np.int32))
            self.rv_node = np.arange(self.n, self.n + m, dtype=np.int64).reshape(h, w)
            self.n += m
        self.origins = []                                  # (bit, node)

    # ------------------------------------------------------------------ table helpers
    def _cat(self, name):
        parts = getattr(self, name)
        if len(parts) > 1:
            setattr(self, name, [np.concatenate(parts)])
        return getattr(self, name)[0]

    def column(self, name):
        return self._cat(name)

    def track(self, site_rc, field):
        """Track the node currently at (site, field) as a new origin; returns its bit index."""
        bit = len(self.origins)
        if bit >= 64:
            raise ValueError("prov0 tracks at most 64 origins")
        node = int(self.cur[field][site_rc])
        mask = self._cat("mask")
        mask[node] |= np.uint64(1) << np.uint64(bit)
        self.origins.append((bit, node))
        return bit

    # ------------------------------------------------------------------ one tick
    def step(self, tick, fields_pre, fields_post, observer, params, received=None, received_value=None,
             aim_energy=None):
        """Record the tick whose pre-state is fields_pre and post-state fields_post (both as passed to and
        returned by the law), using the law's observer export. Raises ProvenanceMismatch on any disagreement."""
        h, w = self.H, self.W
        v = self.variant
        val = self._cat("value"); mask = self._cat("mask"); hops = self._cat("hops")
        packed = K.pack_coords_vec(np.arange(h).reshape(h, 1), np.arange(w).reshape(1, w))
        opcode = fields_pre[0]
        # rcv_adr: is the SOURCE a relay (receipt-activated, not a WRITE site, active)?
        relay = np.zeros((h, w), bool)
        if v in ("rcv_adr", "fwd") and received is not None:
            starved = fields_pre[4].astype(np.int64) < params["write_cost"]
            relay = received & (opcode != K.WRITE_OPCODE) & (~starved)
        new_ops, new_p1, new_p2, new_site, new_field, new_val, new_mask, new_hops = ([] for _ in range(8))
        next_cur = [c.copy() for c in self.cur]
        rv_next = np.full((h, w), -1, np.int64)
        base = self.n
        self._src_relay = [np.zeros((h, w), bool) for _ in range(4)]
        for f in range(4):
            best_slot = observer[f][0]
            won = best_slot != 255
            src_node = np.full((h, w), -1, np.int64)
            for slot, (dr, dc, _rd) in enumerate(K._NEIGHBOR_SLOTS):
                m = won & (best_slot == slot)
                if not m.any():
                    continue
                pay = np.roll(self.cur[3], (-dr, -dc), axis=(0, 1))
                if v == "fwd":
                    rel = np.roll(relay, (-dr, -dc), axis=(0, 1))
                    rvn = np.roll(self.rv_node, (-dr, -dc), axis=(0, 1))
                    pay = np.where(rel & (rvn >= 0), rvn, pay)
                src_node = np.where(m, pay, src_node)
                if v == "rcv_adr":
                    rel = np.roll(relay, (-dr, -dc), axis=(0, 1))
                    self._src_relay[f] = np.where(m, rel, self._src_relay[f])
            idx = np.flatnonzero(won)
            if idx.size == 0:
                continue
            tgt_prev = self.cur[f].ravel()[idx]
            src = src_node.ravel()[idx]
            if v in ADD_FAMILY:
                is_add = np.ones(idx.size, bool)
            elif v == "rcv_adr":
                is_add = ~self._src_relay[f].ravel()[idx]
            else:
                is_add = np.zeros(idx.size, bool)
            pred = np.where(is_add, (val[tgt_prev] + val[src]) & 0xFF, val[src]).astype(np.int16)
            trig, bit_idx = K.mu_vec(params["seed"], tick, packed, f, params["mut_numer"])
            t = trig.ravel()[idx]
            pred = np.where(t, pred ^ (np.int16(1) << bit_idx.ravel()[idx]), pred)
            got = fields_post[f].astype(np.int16).ravel()[idx]
            if not np.array_equal(pred, got):
                bad = np.flatnonzero(pred != got)[0]
                raise ProvenanceMismatch(
                    "tick %d field %d site %d: shadow predicts %d, physics committed %d (variant %s)"
                    % (tick, f, int(idx[bad]), int(pred[bad]), int(got[bad]), v))
            ops = np.where(is_add, OP_ADD, OP_COPY).astype(np.int8) | np.where(t, OP_MUT, 0).astype(np.int8)
            p2 = np.where(is_add, tgt_prev, -1)
            p1 = np.where(is_add, src, src)
            m1 = mask[src]
            m2 = np.where(is_add, mask[tgt_prev], np.uint64(0))
            h1 = np.where(m1 != 0, hops[src], -1)
            h2 = np.where(m2 != 0, hops[np.where(is_add, tgt_prev, src)], -1)
            nm = m1 | m2
            nh = np.where(nm != 0, np.maximum(h1, h2) + 1, 0).astype(np.int32)
            ids = base + np.arange(idx.size, dtype=np.int64)
            base += idx.size
            new_ops.append(ops); new_p1.append(p1); new_p2.append(p2); new_site.append(idx.astype(np.int64))
            new_field.append(np.full(idx.size, f, np.int8)); new_val.append(got); new_mask.append(nm)
            new_hops.append(nh)
            nc = next_cur[f].ravel()
            nc[idx] = ids
            next_cur[f] = nc.reshape(h, w)
            if v == "fwd":
                rv = rv_next.ravel()
                rv[idx] = ids                                # later fields overwrite: payload > arg1 > arg0 > opcode
                rv_next = rv.reshape(h, w)
        # untouched template bytes must be unchanged
        for f in range(4):
            unchanged = next_cur[f] == self.cur[f]
            if not np.array_equal(fields_pre[f][unchanged], fields_post[f][unchanged]):
                raise ProvenanceMismatch("tick %d field %d: a byte changed without a winning write" % (tick, f))
        if new_ops:
            self.op.append(np.concatenate(new_ops)); self.p1.append(np.concatenate(new_p1))
            self.p2.append(np.concatenate(new_p2)); self.site.append(np.concatenate(new_site))
            self.field.append(np.concatenate(new_field)); self.value.append(np.concatenate(new_val))
            self.mask.append(np.concatenate(new_mask)); self.hops.append(np.concatenate(new_hops))
            self.tick.append(np.full(base - self.n, tick, np.int32))
            self.n = base
        self.cur = next_cur
        self.rv_node = rv_next

    # ------------------------------------------------------------------ queries
    def last_writer(self, site_rc, field):
        """(node id, op, parents) of the value currently at (site, field)."""
        node = int(self.cur[field][site_rc])
        return node, int(self._cat("op")[node]), (int(self._cat("p1")[node]), int(self._cat("p2")[node]))

    def ancestry(self, node):
        """All ancestor node ids of `node` (DAG closure, excluding itself)."""
        p1, p2 = self._cat("p1"), self._cat("p2")
        seen, stack = set(), [node]
        while stack:
            x = stack.pop()
            for p in (p1[x], p2[x]):
                if p >= 0 and p not in seen:
                    seen.add(int(p)); stack.append(int(p))
        return seen

    def holders(self, bit):
        """Current (field, row, col, hops, node) of every stored template value descending from origin `bit`."""
        mask = self._cat("mask"); hops = self._cat("hops")
        b = np.uint64(1) << np.uint64(bit)
        out = []
        for f in range(4):
            cur = self.cur[f]
            hit = (mask[cur] & b) != 0
            for r, c in np.argwhere(hit):
                node = int(cur[r, c])
                out.append((f, int(r), int(c), int(hops[node]), node))
        return out

    def rung_profile(self, bit):
        """Rung readings for origin `bit` at the current tick (P3 carried, P4 transformed, P5 composed, P6 persisted)."""
        mask = self._cat("mask"); hops = self._cat("hops"); val = self._cat("value")
        _b, onode = self.origins[bit]
        ov = int(val[onode]); b = np.uint64(1) << np.uint64(bit)
        rows = self.holders(bit)
        prof = {"holders": len(rows), "carried_away": 0, "transformed": 0, "composed": 0, "max_hops": 0,
                "max_distance": 0}
        orow, ocol = divmod(int(self._cat("site")[onode]), self.W)
        for f, r, c, hp, node in rows:
            dr = min(abs(r - orow), self.H - abs(r - orow)); dc = min(abs(c - ocol), self.W - abs(c - ocol))
            d = max(dr, dc)
            if node != onode:
                prof["carried_away"] += int(d > 0)
                prof["transformed"] += int(int(val[node]) != ov)
                prof["composed"] += int(bin(int(mask[node])).count("1") >= 2)
            prof["max_hops"] = max(prof["max_hops"], hp)
            prof["max_distance"] = max(prof["max_distance"], d)
        return prof


def run(variant, fields, params, ticks, tick0=1, received=None, received_value=None, aim_energy=None,
        track=()):
    """Step the law with the provenance shadow for `ticks` ticks. `track` = [(row, col, field), ...] origins tracked
    at tick0. Returns (final fields, Provenance, per-tick list of {bit: rung_profile})."""
    f = [x.copy() for x in fields]
    h, w = f[0].shape
    rec = received if received is not None else np.zeros((h, w), bool)
    rv = received_value if received_value is not None else np.zeros((h, w), np.uint8)
    pv = Provenance(variant, f)
    for (r, c, fld) in track:
        pv.track((r, c), fld)
    history = []
    for t in range(tick0, tick0 + ticks):
        obs = []
        kw = {}
        if variant in V.RCV_FAMILY:
            kw["received"] = rec
        if variant == "fwd":
            kw["received_value"] = rv
        if variant == "rcv_sfz" and aim_energy is not None:
            kw["aim_energy"] = aim_energy
        out = V.step(variant, H=h, W=w, tick=t, opcode=f[0], arg0=f[1], arg1=f[2], payload=f[3], energy=f[4],
                     observer=obs, **kw, **params)
        post = list(out[:5])
        pv.step(t, f, post, obs, params, received=rec if variant in V.RCV_FAMILY else None)
        f = post
        if variant in V.RCV_FAMILY:
            rec = out[5]["received"]
        if variant == "fwd":
            rv = out[5]["received_value"]
        history.append({b: pv.rung_profile(b) for b, _n in pv.origins})
    return f, pv, history
