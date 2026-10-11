"""BEL-48H Window 3 instrument: the EVENT that first made a functional replicator (measurement only; replay-tested).

OriginWorld(ReachWorld) tags tape changes EAGERLY instead of lazily, so in-place changes are split by cause:
  m   background mutation (World._mutate)
  s   self-construction: the organism's own execution wrote a computed byte into its own tape
  u   UPTAKE: its own execution moved a PARTNER byte (window origin) into its own tape (horizontal acquisition; the
      byte keeps its founder/novel tag, and the position's acquisition mode is recorded as 'u')
  v   self-move: its own execution moved one of its own bytes to another own position
  i   inherited at birth (copied into it as a child)
Per organism and position the last acquisition mode is kept (self.via). Every change is followed by a FUNC check on
the new tape; the FIRST time any organism becomes FUNC (by a change or by birth) the event is dissected:
  kind, tick, carrier id, old tape, new tape, changed positions, the new tape's critical set, the acquisition mode and
  origin of every critical byte, and REVERSION: each changed critical byte individually reverted to its old value
  (necessary iff FUNC is then lost), and all changes reverted together. The carrier's history (up to 40 tape
  snapshots with tick and change kind) and the copy extent of each snapshot form the RAMP profile.

The kernel's World is untouched: hooks only observe, call the parent with the same arguments, and the invariance test
(tests/test_origin.py) compares end-state hashes with and without the hook."""
from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional

from reach import ReachWorld, copy_extent


class OriginWorld(ReachWorld):
    HIST_CAP = 40

    def __init__(self, cfg, seed, rows: bool = False):
        self._o_ready = False
        super().__init__(cfg, seed, rows=rows)
        self.via: Dict[int, List[str]] = {o.id: ["f"] * self.L for o in self.cells if o is not None}
        self.hist: Dict[int, list] = {o.id: [(0, "founder", bytes(o.tape))] for o in self.cells if o is not None}
        self.origin_event: Optional[dict] = None
        self.O = Counter()
        self._owner_tick = -1; self._owner: Dict[int, object] = {}
        self._pre_tags: Dict[int, tuple] = {}
        self._o_ready = True

    # ---- helpers ---------------------------------------------------------------------------------------------------------
    def _owner_of(self, tape):
        o = self._owner.get(id(tape))
        if o is None or o.tape is not tape:
            self._owner = {id(x.tape): x for x in self.cells if x is not None}
            o = self._owner.get(id(tape))
        return o

    def _push_hist(self, oid, kind, tape):
        h = self.hist.setdefault(oid, [])
        if len(h) < self.HIST_CAP:
            h.append((self.tick, kind, bytes(tape)))

    def _check_origin(self, o, old: bytes, new: bytes, kind: str, changed: List[int]):
        if self.origin_event is not None or not changed:
            return
        if not self.func(new) or self.func(old):
            return
        crit = self.critical(new)
        tags = self.tags.get(o.id) or []
        via = self.via.get(o.id) or ["?"] * self.L
        nec = {}
        for p in changed:
            if p in crit:
                t = bytearray(new); t[p] = old[p]
                nec[p] = not self.func(bytes(t))
        hist = self.hist.get(o.id, [])
        self.origin_event = {
            "kind": kind, "tick": self.tick, "carrier": o.id, "carrier_mech": o.mechanism, "carrier_birth": self.birth_tick.get(o.id),
            "old": old.hex(), "new": new.hex(), "changed": changed, "critical": crit,
            "changed_critical": [p for p in changed if p in crit],
            "necessary_changed": [p for p, v in nec.items() if v],
            "revert_all_func": self.func(old),
            "critical_via": "".join(via[p] for p in crit),
            "critical_origins": [self.tag_origin(tags[p])[:2] if tags else None for p in crit],
            "history": [(t, k, copy_extent(tp, self.cfg)) for t, k, tp in hist],
            "old_copy_extent": copy_extent(old, self.cfg)}

    # ---- mutation ---------------------------------------------------------------------------------------------------------
    def _mutate(self, tape, rate):
        if not getattr(self, "_o_ready", False):
            return super()._mutate(tape, rate)
        o = self._owner_of(tape)
        old = bytes(tape)
        n = super()._mutate(tape, rate)
        if o is None or not n:
            return n
        new = bytes(tape)
        changed = [i for i in range(self.L) if old[i] != new[i]]
        if not changed:
            return n
        tg = self._synced(o.id, old)
        for i in changed:
            tg[i] = self._new("m")
            self.via.setdefault(o.id, ["?"] * self.L)[i] = "m"
        self.shadow[o.id] = new
        self.O["mutation_events"] += 1
        self._push_hist(o.id, "m", new)
        self._check_origin(o, old, new, "MUTATION", changed)
        return n

    # ---- own-region writes during execution ------------------------------------------------------------------------------------
    def _own_writes(self, o, partner, mem, tr, half_hi: int):
        L = self.L
        pre = self._pre_tape
        new = bytes(mem[:L])
        changed = [i for i in range(L) if pre[i] != new[i]]
        ptags = self._synced(o.id, pre)
        self._pre_tags[o.id] = (pre, list(ptags))                      # writer tags for the child, if a birth follows
        if not changed:
            return
        ttags = self._synced(partner.id, bytes(partner.tape)) if partner is not None else None
        tg = list(ptags); via = self.via.setdefault(o.id, ["?"] * L)
        kinds = Counter()
        for i in changed:
            src = tr.origin.get(i, i)
            if src is None:
                tg[i] = self._new("s"); via[i] = "s"; kinds["s"] += 1
            elif src < L:
                tg[i] = ptags[src]; via[i] = "v"; kinds["v"] += 1
            elif src < half_hi and ttags is not None:
                tg[i] = ttags[src - L]; via[i] = "u"; kinds["u"] += 1
            else:
                tg[i] = self._new("x"); via[i] = "x"; kinds["x"] += 1
        self.tags[o.id] = tg; self.shadow[o.id] = new
        self.O["self_write_events"] += 1; self.O["uptake_bytes"] += kinds["u"]
        k = "UPTAKE" if kinds["u"] else ("SELF_CONSTRUCT" if kinds["s"] else ("SELF_MOVE" if kinds["v"] else "OTHER"))
        self._push_hist(o.id, k[0].lower(), new)
        self._check_origin(o, pre, new, k, changed)

    def _execute(self, o, partner_tape, inputs):
        mem, tr = super()._execute(o, partner_tape, inputs)
        if getattr(self, "_o_ready", False):
            partner = self._owner_of(partner_tape) if partner_tape is not None else None
            self._own_writes(o, partner, mem, tr, 2 * self.L)
        return mem, tr

    def _pair_execute(self, a, b, inputs):
        mem, tr = super()._pair_execute(a, b, inputs)
        if getattr(self, "_o_ready", False):
            self._own_writes(a, b, mem, tr, 2 * self.L)
        return mem, tr

    # ---- births: the child's tags must be built from the writer's PRE-execution tags ---------------------------------------------
    def _register_offspring(self, j, child, parent, mechanism, fidelity, tr, replaced):
        if not getattr(self, "_o_ready", False):
            return super()._register_offspring(j, child, parent, mechanism, fidelity, tr, replaced)
        post_tags, post_shadow = self.tags.get(parent.id), self.shadow.get(parent.id)
        pt = self._pre_tags.get(parent.id)
        if pt is not None:
            self.tags[parent.id] = list(pt[1]); self.shadow[parent.id] = pt[0]
        before = self.origin_event is None and self.first_func is None
        super()._register_offspring(j, child, parent, mechanism, fidelity, tr, replaced)
        if post_tags is not None:
            self.tags[parent.id] = post_tags; self.shadow[parent.id] = post_shadow
        c = self.cells[j]
        self.via[c.id] = ["i"] * self.L
        self.hist[c.id] = [(self.tick, "born", bytes(child))]
        if replaced is not None:
            self.via.pop(replaced.id, None); self.hist.pop(replaced.id, None)
        if before and self.origin_event is None and self.first_func is not None and self.first_func["how"].startswith("BORN_"):
            a = self.first_func.get("anatomy", {})
            self.origin_event = {"kind": self.first_func["how"], "tick": self.tick, "carrier": c.id, "carrier_mech": mechanism,
                                 "new": bytes(child).hex(), "critical": a.get("critical"), "critical_vec": self.first_func.get("vec"),
                                 "critical_origins": a.get("origins_raw"),
                                 "writer_history": [(t, k, copy_extent(tp, self.cfg)) for t, k, tp in self.hist.get(parent.id, [])]}
        if self.tick % 25 == 0:
            alive = {o.id for o in self.cells if o is not None}
            for d in (self.via, self.hist, self._pre_tags):
                for k in [k for k in d if k not in alive]:
                    del d[k]

    def origin_summary(self) -> dict:
        return {"O": dict(self.O), "origin_event": self.origin_event}
