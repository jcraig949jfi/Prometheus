"""BEL-48H Window 4 instrument: computation x reproduction anatomy under physics v3 (measurement only).

CompWorld(HeredityWorld) adds, per birth, the joint fate of COMPETENCE (coupling.Competence: verified exact answer on
the configured task, the tape alone) and FUNC (own-code self-copy) from writer to child:
  task_loss      writer competent AND FUNC, child FUNC but NOT competent (reproduction kept, computation lost)
  repro_loss     writer competent AND FUNC, child competent but NOT FUNC
  joint_keep     writer competent AND FUNC, child both
  gain           writer NOT competent, child competent (any FUNC state); split by the child's provenance label
and at the end of the run, for the dominant competent FUNC tape (if any) its ANATOMY:
  ccrit / rcrit  competence-critical / FUNC-critical bytes (nonzero byte whose NOP knockout breaks it)
  shared         bytes in both sets (one byte serving both machines)
  origins        tag origins of each set (founder organism + mechanism -- 'transplant0' = first init tape, etc. --
                 or novel event kind n / c / x / e with tick)
  first_comp_sr  the first birth whose child was competent AND FUNC: tick, class, and the same anatomy."""
from __future__ import annotations

from collections import Counter

from heredity import HeredityWorld


class CompWorld(HeredityWorld):
    def __init__(self, cfg, seed, rows: bool = False):
        self._c_ready = False
        super().__init__(cfg, seed, rows=rows)
        assert self.competence is not None, "CompWorld needs physics v3 (coupling)"
        self.C = Counter()
        self.first_comp_sr = None
        self._c_ready = True

    def is_comp(self, tape: bytes) -> bool:
        return self.competence.of(bytes(tape))[0]

    def critical_comp(self, tape: bytes):
        out = []
        for p in range(self.L):
            if tape[p] != 0:
                t = bytearray(tape); t[p] = 0
                if not self.is_comp(bytes(t)):
                    out.append(p)
        return out

    def _origins(self, tags, pos):
        out = []
        for p in pos:
            o = self.tag_origin(tags[p])
            out.append([o[0], o[1], o[2] if o[0] == "F" else self.novel_kind[o[1]][1], p])
        return out

    def comp_anatomy(self, tape: bytes, tags) -> dict:
        cc = self.critical_comp(tape); rc = self.critical(tape)
        oc = self._origins(tags, cc); orr = self._origins(tags, rc)
        return {"tape": tape.hex(), "ccrit": cc, "rcrit": rc, "shared": sorted(set(cc) & set(rc)),
                "ccrit_origins": oc, "rcrit_origins": orr,
                "ccrit_founder_mech": sorted({x[2] for x in oc if x[0] == "F"}), "rcrit_founder_mech": sorted({x[2] for x in orr if x[0] == "F"}),
                "ccrit_novel": dict(Counter(x[0] for x in oc if x[0] != "F")), "rcrit_novel": dict(Counter(x[0] for x in orr if x[0] != "F"))}

    def _register_offspring(self, j, child, parent, mechanism, fidelity, tr, replaced):
        if not getattr(self, "_c_ready", False):
            return super()._register_offspring(j, child, parent, mechanism, fidelity, tr, replaced)
        pre = self._pre_tape or bytes(parent.tape)
        cw, fw = self.is_comp(pre), self.func(pre)
        cc, fc = self.is_comp(bytes(child)), self.func(bytes(child))
        super()._register_offspring(j, child, parent, mechanism, fidelity, tr, replaced)
        C = self.C
        C["births"] += 1
        if cw and fw:
            C["from_comp_func"] += 1
            C["joint_keep" if (cc and fc) else ("task_loss" if fc else ("repro_loss" if cc else "both_loss"))] += 1
        if cc and not cw:
            C["gain"] += 1
        if cc and fc:
            C["comp_func_births"] += 1
            if self.first_comp_sr is None:
                c = self.cells[j]
                self.first_comp_sr = {"tick": self.tick, "writer_comp": cw, "writer_func": fw,
                                      "anatomy": self.comp_anatomy(bytes(child), self.tags[c.id])}

    def comp_summary(self) -> dict:
        alive = [o for o in self.cells if o is not None]
        both = [o for o in alive if self.is_comp(bytes(o.tape)) and self.func(bytes(o.tape))]
        out = {"C": dict(self.C), "first_comp_sr": self.first_comp_sr, "comp_func_alive": len(both),
               "comp_alive": sum(1 for o in alive if self.is_comp(bytes(o.tape)))}
        if both:
            dom = Counter(bytes(o.tape) for o in both).most_common(1)[0][0]
            o = next(o for o in both if bytes(o.tape) == dom)
            out["dominant"] = self.comp_anatomy(dom, self._synced(o.id, dom))
            out["dominant"]["count"] = sum(1 for x in both if bytes(x.tape) == dom)
        return out
