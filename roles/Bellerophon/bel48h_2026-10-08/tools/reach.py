"""BEL-48H Window 3 instrument: how the FIRST functional replicator of a run was reached (measurement only).

ReachWorld(HeredityWorld) keeps, besides the heredity state, a per-organism birth tick and tick-indexed offspring
counts, and at the end of the run dissects the run's FIRST FUNC tape T* (heredity.first_func):

  origin events     the critical bytes of T* grouped by tag origin: founder material (organism + original position;
                    'relocated' when the position changed) or a novel event (n = changed in place, c = constructed,
                    x = input-derived, e = fresh memory) with its tick. n_origin_events = number of DISTINCT events
                    that contributed critical bytes = the number of independent changes the machine needed.
  writer chain      the causal ancestry (writer of writer ...) of T*'s carrier, up to 60 ancestors: per ancestor its
                    birth tick, copy extent when executed alone (own bytes laid into the window by its own copy ops:
                    the 'ramp' profile), FUNC, and offspring count vs the mean offspring count of organisms born in
                    the same 10-tick bin (relative reproductive output; > 1 = out-reproduced its contemporaries).
  dependence        LDIR in the critical set; NOP-slide dependence: T* with every zero byte replaced by HALT (0xFF)
                    -> FUNC? (False = the machine relies on permissive filler); undefined-op chemistry: T* under
                    undefined_op HALT -> FUNC?
  portability       the critical bytes of T* implanted (same positions) into 20 random 64-byte backgrounds (seeded):
                    FUNC rate. 1.0 = a self-contained module; low = background-dependent.
  minimal core      T* with every non-critical byte set to 0 -> FUNC? (the critical set is sufficient as well as
                    necessary)."""
from __future__ import annotations

import random
from collections import Counter, defaultdict

from belinst import Func
from heredity import HeredityWorld
from prometheus.z80atlas import vm
from prometheus.z80atlas.world import Config


def copy_extent(tape: bytes, cfg: Config) -> int:
    L = cfg.L
    t = bytes(tape[:L]) + bytes(max(0, L - len(tape)))
    mem = bytearray(256); mem[:L] = t
    for k, v in enumerate((42, 7, 99, 3)):
        mem[vm.IN_BASE + k] = v
    tr = vm.execute(mem, L, 0, cfg.budget, [42, 7, 99, 3], allow_copyall=cfg.allow_copyall, strict_budget=cfg.physics != "v1", **cfg.chem)
    return sum(1 for off, o in tr.win_origin.items() if o == off and tr.win_prov[off][1] < L)     # same rule as FUNC


class ReachWorld(HeredityWorld):
    def _register_offspring(self, j, child, parent, mechanism, fidelity, tr, replaced):
        if getattr(self, "_h_ready", False):
            self.__dict__.setdefault("n_children", Counter())[parent.id] += 1
        return super()._register_offspring(j, child, parent, mechanism, fidelity, tr, replaced)

    def reach_summary(self, n_backgrounds: int = 20) -> dict:
        ff = self.first_func
        if not ff:
            return {"first_func": None}
        cfg = self.cfg; L = self.L
        an = ff["anatomy"]; tape = bytes.fromhex(an["tape"]); crit = an["critical"]
        out = {"how": ff["how"], "tick": ff["tick"], "n_critical": len(crit), "critical_bytes": [tape[p] for p in crit]}
        # origin events of the critical bytes (tags were captured with the anatomy only as founders/novel kinds; recompute
        # from the carrier's tags when it is still known, else from the stored anatomy)
        ev = an.get("origins_raw") or []
        out["origin_events"] = ev
        out["n_origin_events"] = len({(e[0], e[1]) for e in ev})
        out["n_founder_events"] = len({e[1] for e in ev if e[0] == "F"})
        out["n_novel_events"] = len({e[1] for e in ev if e[0] != "F"})
        out["relocated_founder_bytes"] = sum(1 for e in ev if e[0] == "F" and e[2] != e[3])
        out["novel_kinds"] = dict(Counter(e[0] for e in ev if e[0] != "F"))
        # writer chain (causal ancestry) with ramp profile and relative reproductive output
        bins = defaultdict(list)
        for oid, bt in self.birth_tick.items():
            bins[bt // 10].append(self.n_children.get(oid, 0) if hasattr(self, "n_children") else 0)
        bmean = {b: (sum(v) / len(v) if v else 0.0) for b, v in bins.items()}
        chain = []
        for a in self._ancestry(ff["id"], 60):
            bt = self.birth_tape.get(a) or b""
            nc = self.n_children.get(a, 0) if hasattr(self, "n_children") else 0
            m = bmean.get(self.birth_tick.get(a, 0) // 10, 0.0)
            chain.append({"id": a, "birth": self.birth_tick.get(a), "copy_extent": copy_extent(bt, cfg) if bt else None,
                          "func": self.func(bt) if bt else None, "children": nc, "rel_output": round(nc / m, 3) if m > 0 else None})
        out["chain"] = chain
        out["chain_len"] = len(chain)
        ramp = [c["copy_extent"] for c in chain if c["copy_extent"] is not None]
        out["ramp_max_extent_before"] = max(ramp) if ramp else None
        out["ramp_any_partial"] = any(0 < x < 0.9 * L for x in ramp)
        rel = [c["rel_output"] for c in chain if c["rel_output"] is not None]
        out["chain_rel_output_median"] = sorted(rel)[len(rel) // 2] if rel else None
        out["chain_frac_above_contemporaries"] = round(sum(1 for r in rel if r > 1) / len(rel), 3) if rel else None
        # dependence
        out["ldir_critical"] = any(tape[p] == vm.LDIR for p in crit)
        out["copyall_critical"] = any(tape[p] == vm.COPYALL for p in crit)
        out["func_zero_to_halt"] = self.func(bytes(0xFF if b == 0 else b for b in tape))
        out["func_undefined_halt"] = Func(Config(**dict(cfg.to_dict(), undefined_op="HALT", init_tapes=tuple(cfg.init_tapes))))(tape)
        core = bytes(tape[p] if p in set(crit) else 0 for p in range(L))
        out["minimal_core_func"] = self.func(core)
        rng = random.Random(1009)
        ok = 0
        for _ in range(n_backgrounds):
            bg = bytearray(rng.randrange(256) for _ in range(L))
            for p in crit:
                bg[p] = tape[p]
            ok += self.func(bytes(bg))
        out["portability"] = round(ok / n_backgrounds, 3)
        return out
