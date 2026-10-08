"""BEL-48H experimental PHYSICS ABLATION (campaign-level, not a kernel change): UPTAKE BLOCKED.

UptakeBlockWorld(OriginWorld): after every execution, any byte of the executing organism's OWN tape whose material origin
(vm Trace.origin, multi-hop) lies in the partner region [L, 2L) is restored to its pre-execution value. The organism can
still write its partner (births are unchanged) and still rewrite itself with its own or computed bytes; it can no longer
import partner material into itself. Counted per run as blocked_bytes (the ablation's productivity signal). Everything
else -- including the eager origin tags of OriginWorld -- is unchanged, so blocked and normal worlds on one seed are
identical until the first uptake would have happened."""
from __future__ import annotations

from prometheus.z80atlas.world import World
from origin import OriginWorld


class UptakeBlockWorld(OriginWorld):
    def _revert_uptake(self, mem, tr):
        L = self.L; pre = self._pre_tape; n = 0
        for a in range(L):
            o = tr.origin.get(a, a)
            if o is not None and L <= o < 2 * L and mem[a] != pre[a]:
                mem[a] = pre[a]; tr.origin[a] = a; n += 1
            elif o is not None and L <= o < 2 * L:
                tr.origin[a] = a
        self.O["blocked_bytes"] += n
        return mem, tr

    def _execute(self, o, partner_tape, inputs):
        mem, tr = World._execute(self, o, partner_tape, inputs)
        if getattr(self, "_o_ready", False):
            self._revert_uptake(mem, tr)
            partner = self._owner_of(partner_tape) if partner_tape is not None else None
            self._own_writes(o, partner, mem, tr, 2 * self.L)
        return mem, tr

    def _pair_execute(self, a, b, inputs):
        mem, tr = World._pair_execute(self, a, b, inputs)
        if getattr(self, "_o_ready", False):
            self._revert_uptake(mem, tr)
            self._own_writes(a, b, mem, tr, 2 * self.L)
        return mem, tr
