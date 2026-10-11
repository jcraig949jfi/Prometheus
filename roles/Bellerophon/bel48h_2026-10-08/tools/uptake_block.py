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


class SelfCopyUptakeBlockWorld(UptakeBlockWorld):
    """NEXT #9 ablation: revert imports ONLY in executions in which the organism laid down a self-copy (>= 0.9 L window
    bytes whose material origin is its own byte at the same position, the FUNC criterion applied to this execution).
    Imports by organisms that are not copying themselves in that execution (UF's precursor breakers) are left intact."""

    def _revert_uptake(self, mem, tr):
        L = self.L
        own = sum(1 for off, o in tr.win_origin.items() if o == off)
        if own >= 0.9 * L:
            self.O["selfcopy_executions_blocked"] += 1
            return super()._revert_uptake(mem, tr)
        return mem, tr
