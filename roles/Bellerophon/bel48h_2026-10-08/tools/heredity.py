"""BEL-48H Window 2 instrument: byte-level founder ancestry and functional heredity (measurement only).

HeredityWorld(DualWorld) adds:
- BYTE TAGS. Every byte of every living tape carries an integer tag. A founder byte (an initial organism's tape)
  has tag founder_id * 64 + position (>= 0): its organism of origin AND its original position. Every byte that is not
  a faithful move of an existing byte gets a fresh NEGATIVE tag whose kind is recorded: 'c' constructed by a non-copy
  write, 'n' changed in place (background mutation or self-write, detected lazily by comparing the tape with the
  shadow copy taken when the tags were last set), 'x' copied from outside [0,2L), 'e' fresh memory. A child's byte
  inherits the tag of the pre-execution byte it carries (vm Trace.win_origin: multi-hop through copy ops and register-A
  moves; review A repair 2026-10-08).
- FUNC-CHILD BIRTH CLASSES (FUNC from belinst): COPY (writer FUNC, prov writer), CAPTURE (target FUNC, writer not),
  ASSEMBLY (child FUNC, NEITHER writer pre-tape NOR target FUNC), CONSTRUCT (child FUNC, neither FUNC, prov
  constructed), OTHER (writer FUNC but prov not writer, etc.).
- CAUSAL TESTS on every ASSEMBLY/CONSTRUCT birth and on each run's FIRST FUNC tape and its dominant FUNC tape at the end:
    critical set   positions p with child[p] != 0 such that setting child[p] = 0x00 (NOP) makes FUNC fail. Zero bytes
                   are never critical (NOP filler is non-specific; disclosed in the prereg).
    sources        per critical byte: vec class (W/T/C/X/E) and tag -> distinct origins (founders + novel events).
    writer_only    child with every non-W byte set to 0 -> FUNC?    target_only: every W byte set to 0 -> FUNC?
    CAUSAL_ASSEMBLY  FUNC(child) AND NOT writer_only AND NOT target_only AND the critical set holds both W bytes and
                   non-W bytes. Each critical byte is necessary by construction, so the machinery is jointly built.
- FIRST FUNC origin per run: born FUNC (with its birth class) or became FUNC IN PLACE (a writer whose pre-tape is FUNC
  but whose birth tape was not -- mutation or self-modification).
- HEREDITY OF ASSEMBLED MACHINERY: an organism descended through TRBs from an ASSEMBLY/CONSTRUCT-born organism carries
  its event id; at the end: alive descendants per event and max TRB depth since the event."""
from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional

from belinst import DualWorld
from prometheus.z80atlas import vm

NOP = 0x00


class HeredityWorld(DualWorld):
    EVENT_CAP = 400

    def __init__(self, cfg, seed, rows: bool = False):
        self._h_ready = False
        super().__init__(cfg, seed, rows=rows)
        self.tags: Dict[int, List[int]] = {}
        self.shadow: Dict[int, bytes] = {}
        self.novel_kind: Dict[int, tuple] = {}
        self._novel = 0
        self.founder_mech: Dict[int, str] = {}
        tx = [bytes.fromhex(h)[: self.L] for h in cfg.init_tapes] if cfg.init_tapes else []
        for o in self.cells:
            if o is not None:
                self.tags[o.id] = [o.id * 64 + i for i in range(self.L)]
                self.shadow[o.id] = bytes(o.tape)
                m = o.mechanism
                if m == "transplant" and tx:
                    m = "transplant%d" % next((k for k, t in enumerate(tx) if bytes(o.tape[: len(t)]) == t), -1)
                self.founder_mech[o.id] = m
        self.H = Counter()
        self.h_events: List[dict] = []
        self.first_func: Optional[dict] = None
        self.birth_func: Dict[int, bool] = {}
        self.anc_event: Dict[int, tuple] = {}                        # id -> (event index, trb generations since)
        self._pruned_at = -1
        self._h_ready = True

    # ---- tags -------------------------------------------------------------------------------------------------------
    def _new(self, kind: str) -> int:
        self._novel -= 1
        self.novel_kind[self._novel] = (kind, self.tick)
        return self._novel

    def _synced(self, oid: int, tape: bytes) -> List[int]:
        t = self.tags.get(oid)
        if t is None:
            t = [self._new("n") for _ in range(self.L)]
            self.tags[oid] = t; self.shadow[oid] = bytes(tape); return t
        sh = self.shadow[oid]
        if sh != tape:
            for i in range(self.L):
                if sh[i] != tape[i]:
                    t[i] = self._new("n")
            self.shadow[oid] = bytes(tape)
        return t

    def tag_origin(self, tag: int):
        if tag >= 0:
            f = tag // 64
            return ("F", f, self.founder_mech.get(f, "?"))
        return (self.novel_kind[tag][0].upper(), tag, None)

    # ---- causal tests -------------------------------------------------------------------------------------------------
    def critical(self, tape: bytes) -> List[int]:
        out = []
        for p in range(self.L):
            if tape[p] != 0:
                t = bytearray(tape); t[p] = NOP
                if not self.func(bytes(t)):
                    out.append(p)
        return out

    def _anatomy(self, tape: bytes, tags: List[int], vec: Optional[str]) -> dict:
        crit = self.critical(tape)
        origins = [self.tag_origin(tags[p]) for p in crit]
        founders = sorted({o[1] for o in origins if o[0] == "F"})
        novel = [o for o in origins if o[0] != "F"]
        d = {"tape": tape.hex(), "critical": crit, "n_critical": len(crit),
             "critical_founders": founders, "critical_founder_mech": sorted({self.founder_mech.get(f, "?") for f in founders}),
             "critical_novel_kinds": dict(Counter(o[0] for o in novel)),
             "n_origins": len(founders) + len({o[1] for o in novel})}
        raw = []
        for p in crit:
            t = tags[p]
            raw.append(["F", t // 64, t % 64, p] if t >= 0 else [self.novel_kind[t][0], t, self.novel_kind[t][1], p])
        d["origins_raw"] = raw                                       # [kind, founder|tag, orig_pos|tick, position]
        if vec is not None:
            d["critical_vec"] = "".join(vec[p] for p in crit)
        return d

    # ---- the birth hook -----------------------------------------------------------------------------------------------------
    def _register_offspring(self, j, child, parent, mechanism, fidelity, tr, replaced):
        if not self._h_ready:
            return super()._register_offspring(j, child, parent, mechanism, fidelity, tr, replaced)
        L = self.L
        pre = self._pre_tape or bytes(parent.tape)
        wtags = self._synced(parent.id, pre)
        ttags = self._synced(replaced.id, bytes(replaced.tape)) if replaced is not None else None
        orig = tr.win_origin                                   # multi-hop material origin (review A repair, 2026-10-08)
        has_t = replaced is not None and self.cfg.target_fill != "zero"
        ctags = []; vec = []
        for off in range(L):
            if off not in orig:
                if has_t:
                    ctags.append(ttags[off]); vec.append("T")
                else:
                    ctags.append(self._new("e")); vec.append("E")
                continue
            o = orig[off]
            if o is None:
                ctags.append(self._new("c")); vec.append("C")
            elif o < L:
                ctags.append(wtags[o]); vec.append("W")
            elif o < 2 * L and replaced is not None:
                ctags.append(ttags[o - L]); vec.append("T")
            elif o < 2 * L:
                ctags.append(self._new("e")); vec.append("E")
            else:
                ctags.append(self._new("x")); vec.append("X")
        vec = "".join(vec)
        f_w = self.func(pre)
        f_t = self.func(bytes(replaced.tape)) if replaced is not None else False
        f_c = self.func(bytes(child))
        nW = vec.count("W"); nT = vec.count("T")
        prov_lab = "target" if (replaced is not None and nT > nW) else ("constructed" if nW == 0 and nT == 0 else "writer")
        # first FUNC tape that arose IN PLACE (writer FUNC now, not FUNC at its birth)
        if f_w and self.first_func is None and not self.birth_func.get(parent.id, False):
            unchanged = self.birth_tape.get(parent.id) == pre
            how = ("FOUNDER_" + self.founder_mech.get(parent.id, "?")) if (parent.id in self.founder_mech and unchanged) else "IN_PLACE"
            self.first_func = {"how": how, "tick": self.tick, "id": parent.id, "founder": parent.id in self.founder_mech,
                               "anatomy": self._anatomy(pre, wtags, None)}
        pid = parent.id
        anc = self.anc_event.get(pid)
        super()._register_offspring(j, child, parent, mechanism, fidelity, tr, replaced)
        c = self.cells[j]
        self.tags[c.id] = ctags; self.shadow[c.id] = bytes(child)
        if replaced is not None:
            self.tags.pop(replaced.id, None); self.shadow.pop(replaced.id, None)
        self.birth_func[c.id] = f_c
        H = self.H
        if f_c:
            if f_w and prov_lab == "writer":
                cls = "COPY"
            elif f_t and not f_w:
                cls = "CAPTURE"
            elif not f_w and not f_t:
                cls = "CONSTRUCT" if prov_lab == "constructed" else "ASSEMBLY"
            else:
                cls = "OTHER"
            H["func_birth_" + cls] += 1
            if cls in ("ASSEMBLY", "CONSTRUCT"):
                a = self._anatomy(bytes(child), ctags, vec)
                wo = bytes(b if vec[i] == "W" else 0 for i, b in enumerate(child))
                to = bytes(0 if vec[i] == "W" else b for i, b in enumerate(child))
                a["writer_only_func"] = self.func(wo); a["target_only_func"] = self.func(to)
                cv = a.get("critical_vec", "")
                a["causal_assembly"] = (not a["writer_only_func"] and not a["target_only_func"] and "W" in cv and any(ch != "W" for ch in cv))
                H["causal_assembly"] += a["causal_assembly"]
                ev = {"i": len(self.h_events), "tick": self.tick, "class": cls, "child": c.id, "writer": pid,
                      "target": replaced.id if replaced is not None else None, "vec": vec, "pre": pre.hex(),
                      "target_tape": bytes(replaced.tape).hex() if replaced is not None else None, **a}
                if len(self.h_events) < self.EVENT_CAP:
                    self.h_events.append(ev)
                self.anc_event[c.id] = (ev["i"], 0)
            if self.first_func is None:
                self.first_func = {"how": "BORN_" + cls, "tick": self.tick, "id": c.id, "vec": vec,
                                   "anatomy": self._anatomy(bytes(child), ctags, vec)}
        # heredity of an assembled machine: carried only through TRB (FUNC writer -> FUNC child, writer material)
        if anc is not None and f_w and f_c and prov_lab == "writer":
            self.anc_event[c.id] = (anc[0], anc[1] + 1)
        if self.tick % 25 == 0 and self._pruned_at != self.tick:
            self._pruned_at = self.tick
            alive = {o.id for o in self.cells if o is not None}
            for d in (self.tags, self.shadow):
                for k in [k for k in d if k not in alive]:
                    del d[k]

    def heredity_summary(self) -> dict:
        alive = [o for o in self.cells if o is not None]
        out = {"H": dict(self.H), "first_func": self.first_func, "n_events": len(self.h_events)}
        desc = Counter(); depth = Counter()
        for o in alive:
            a = self.anc_event.get(o.id)
            if a is not None:
                desc[a[0]] += 1; depth[a[0]] = max(depth[a[0]], a[1])
        out["event_alive_descendants"] = {str(k): v for k, v in desc.items()}
        out["event_max_trb_generations_alive"] = {str(k): v for k, v in depth.items()}
        funcs = [o for o in alive if self.func(bytes(o.tape))]
        if funcs:
            dom = Counter(bytes(o.tape) for o in funcs).most_common(1)[0][0]
            oid = next(o.id for o in funcs if bytes(o.tape) == dom)
            tg = self._synced(oid, dom)
            out["dominant_func"] = self._anatomy(dom, tg, None)
            out["dominant_func"]["count"] = sum(1 for o in funcs if bytes(o.tape) == dom)
        out["func_alive"] = len(funcs)
        return out
