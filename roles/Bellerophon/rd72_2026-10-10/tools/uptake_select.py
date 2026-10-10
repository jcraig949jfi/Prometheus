"""BEL-RD-72 D2 selective uptake ablations (campaign-level physics ablations, not kernel changes).

Hypothesis under test (post-D1): imports raise origination failure by damaging PRECURSORS -- organisms that already carry
the copy machinery but are not yet FUNC (BEL-48H: LDIR indispensable in 85/85 origins). Marker: the importer's
PRE-EXECUTION tape contains an LDIR opcode byte.
  LdirUptakeBlockWorld    revert imports ONLY into organisms whose pre-execution tape contains LDIR
  NoLdirUptakeBlockWorld  revert imports ONLY into organisms whose pre-execution tape lacks LDIR
Both count executions with a would-be import, split by marker (dose), so the arms can be compared for how much they block."""
from __future__ import annotations

from prometheus.z80atlas import vm
from uptake_block import UptakeBlockWorld


class _Selective(UptakeBlockWorld):
    BLOCK_IF_LDIR = True

    def _revert_uptake(self, mem, tr):
        L = self.L
        imports = any(o is not None and L <= o < 2 * L for a, o in tr.origin.items() if a < L)
        if not imports:
            return mem, tr
        has = vm.LDIR in self._pre_tape[:L]
        self.O["import_exec_ldir" if has else "import_exec_noldir"] += 1
        if has == self.BLOCK_IF_LDIR:
            return super()._revert_uptake(mem, tr)
        return mem, tr


class LdirUptakeBlockWorld(_Selective):
    BLOCK_IF_LDIR = True


class NoLdirUptakeBlockWorld(_Selective):
    BLOCK_IF_LDIR = False
