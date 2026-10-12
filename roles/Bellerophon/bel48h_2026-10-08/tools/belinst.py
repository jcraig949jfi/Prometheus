"""BEL-48H campaign instrument (Bellerophon, 2026-10-08). Measurement only: never changes what a World does.

DualWorld(World) records, for EVERY endogenous birth, both lineage rulers side by side on the SAME trajectory:
  res   the historical RESEMBLANCE rule (writer vs overwritten target, by which the child resembles more)
  prov  the DEF-BEL-008 PROVENANCE rule (writer vs target vs constructed, by recorded write provenance)
plus a per-byte provenance vector of the child (W writer-copied, T target material, C constructed by a non-copy
write, X copied from outside [0,2L), E empty/fresh memory), the historical self-copy classifier evaluated under each
label, and an INDEPENDENT functional test of the child (FUNC: executed alone in an empty world, does the child itself
lay down an own-code copy of itself -- >= 0.9 L window bytes whose material origin (multi-hop, vm Trace.win_origin) is the
child's own byte at the same position, written by its own code). FUNC does not use either lineage ruler and does not use the DEF-BEL-010 rule.

Parallel genetic-lineage trees are kept for both rulers (root id + generation depth), independent of which rule the
World itself was configured with, so the two rulers are compared without sampling noise.

A TRUE REPLICATIVE BIRTH (TRB) is a birth where (a) the writer's pre-execution tape is FUNC, (b) the child is FUNC,
and (c) provenance says the child's material is the writer's. trb_depth chains TRBs through writers.

The configured World dynamics are untouched: every hook calls the parent method with the same arguments. The
physics-invariance of the hook is asserted by tests/test_belinst.py (end-state hash with and without the hook)."""
from __future__ import annotations

import hashlib
from collections import Counter
from typing import Dict, Optional, Tuple

from prometheus.z80atlas import vm
from prometheus.z80atlas.world import World, Config

PANEL_INPUT = (42, 7, 99, 3)


def end_state_hash(w: World) -> str:
    h = hashlib.sha256()
    for o in w.cells:
        if o is None:
            h.update(b"-")
        else:
            h.update(bytes(o.tape)); h.update(repr((round(o.energy, 9), o.age, o.niche)).encode())
    h.update(repr(w.rng.getstate()).encode())
    return h.hexdigest()


class Func:
    """Isolated functional replication test with a per-tape cache. Pure function of (tape, cfg chemistry)."""

    def __init__(self, cfg: Config):
        self.cfg = cfg; self.cache: Dict[bytes, Tuple[bool, tuple]] = {}

    def __call__(self, tape: bytes) -> bool:
        return self.info(tape)[0]

    def info(self, tape: bytes) -> Tuple[bool, tuple]:
        L = self.cfg.L
        tape = bytes(tape[:L]) + bytes(max(0, L - len(tape)))        # zero-pad: a short slice-assign would SHRINK mem
        r = self.cache.get(tape)
        if r is not None:
            return r
        cfg = self.cfg; L = cfg.L
        mem = bytearray(256); mem[:L] = tape
        for k, v in enumerate(PANEL_INPUT):
            mem[vm.IN_BASE + k] = v
        tr = vm.execute(mem, L, 0, cfg.budget, list(PANEL_INPUT), allow_copyall=cfg.allow_copyall,
                        strict_budget=cfg.physics != "v1", trace_pcs=True, **cfg.chem)
        # own = window bytes carrying the tape's OWN byte from the SAME position (multi-hop material origin, any move),
        # laid down by the tape's own code. Equality with the tape is implied by the origin; no zero-filler can count.
        own = [off for off, o in tr.win_origin.items() if o == off and tr.win_prov[off][1] < L]
        ok = len(own) >= 0.9 * L
        sig = None
        if ok:
            ops = Counter(op for (src, pc, op) in tr.win_prov.values())
            copy_op = ops.most_common(1)[0][0]
            copy_pc = min(pc for (src, pc, op) in tr.win_prov.values())
            n_exec = len([p for p in (tr.pcs or ()) if p < L])
            sig = (copy_op, copy_pc // 4, n_exec // 4)
        r = (ok, sig)
        if len(self.cache) < 200000:
            self.cache[tape] = r
        return r


class DualWorld(World):
    ROW_CAP = 3000

    def __init__(self, cfg: Config, seed: int, rows: bool = True):
        self._dual_ready = False
        super().__init__(cfg, seed)
        self.func = Func(cfg)
        self.g = {"res": {}, "prov": {}}            # id -> genetic root id
        self.gd = {"res": {}, "prov": {}}           # id -> genetic generation depth
        self.trb_depth: Dict[int, int] = {}
        self.B = Counter()
        self.sig_trb = Counter()
        self.first = {}                             # first tick of: sr_res, sr_prov, trb, func_child
        self.rows = [] if rows else None
        self._dual_ready = True

    def _root(self, rule: str, o) -> Tuple[int, int]:
        return self.g[rule].get(o.id, o.id), self.gd[rule].get(o.id, 0)

    def _register_offspring(self, j, child, parent, mechanism, fidelity, tr, replaced):
        if not self._dual_ready:
            return super()._register_offspring(j, child, parent, mechanism, fidelity, tr, replaced)
        cfg = self.cfg; L = self.L
        orig = tr.win_origin                                   # multi-hop material origin (review A repair, 2026-10-08)
        has_target_bytes = replaced is not None and cfg.target_fill != "zero"
        vec = []
        for off in range(L):
            if off not in orig:
                vec.append("T" if has_target_bytes else "E")
                continue
            o = orig[off]
            if o is None:
                vec.append("C")
            else:
                vec.append("W" if o < L else (("T" if replaced is not None else "E") if o < 2 * L else "X"))
        n = Counter(vec)
        nW, nT = n["W"], n["T"]
        # historical resemblance label (exactly the World's RESEMBLANCE rule)
        fid_w = fidelity
        res = "writer"
        if replaced is not None:
            fid_t = 1.0 - sum(1 for x, y in zip(child, replaced.tape) if x != y) / L
            if fid_t > fid_w:
                res = "target"
        pr = "target" if (replaced is not None and nT > nW) else ("constructed" if nW == 0 and nT == 0 else "writer")
        sc_res = self._is_self_copy(child, parent, res, tr)[0]
        sc_prov = self._is_self_copy(child, parent, "writer" if pr == "writer" else pr, tr)[0]
        pre = self._pre_tape or bytes(parent.tape)
        f_writer = self.func(pre)
        f_child, sig = self.func.info(bytes(child))
        trb = f_writer and f_child and pr == "writer"
        pid, rid = parent.id, (replaced.id if replaced is not None else None)
        roots = {r: (self._root(r, replaced) if (lab == "target") else self._root(r, parent)) for r, lab in (("res", res), ("prov", pr))}
        pdepth = self.trb_depth.get(pid, 0)
        super()._register_offspring(j, child, parent, mechanism, fidelity, tr, replaced)
        c = self.cells[j]
        for r in ("res", "prov"):
            self.g[r][c.id] = roots[r][0]; self.gd[r][c.id] = roots[r][1] + 1
        self.trb_depth[c.id] = pdepth + 1 if trb else 0
        B = self.B
        B["births"] += 1
        B["res_%s__prov_%s" % (res, pr)] += 1
        B["sr_res"] += sc_res; B["sr_prov"] += sc_prov
        B["func_child"] += f_child; B["func_writer"] += f_writer
        B["sr_res_func_child"] += sc_res and f_child
        B["sr_res_not_func_child"] += sc_res and not f_child
        B["func_child_not_sr_res"] += f_child and not sc_res
        B["trb"] += trb
        B["func_child_target_material"] += f_child and pr == "target"
        mixed = nW >= L // 8 and nT >= L // 8
        B["mixed_origin"] += mixed
        B["mixed_origin_func_child"] += mixed and f_child
        B["constructed"] += pr == "constructed"
        B["bytes_W"] += nW; B["bytes_T"] += nT; B["bytes_C"] += n["C"]; B["bytes_X"] += n["X"]; B["bytes_E"] += n["E"]
        if trb and sig is not None:
            self.sig_trb[sig] += 1
        for key, flag in (("sr_res", sc_res), ("sr_prov", sc_prov), ("trb", trb), ("func_child", f_child)):
            if flag and key not in self.first:
                self.first[key] = {"tick": self.tick, "writer": pid, "child": c.id, "writer_mech": self.birth_class.get(pid, ("init",))[0],
                                   "pre_tape": pre.hex(), "child_tape": bytes(child).hex(), "vec": "".join(vec)}
        if self.rows is not None and len(self.rows) < self.ROW_CAP and (sc_res or sc_prov or f_child or trb or res != pr):
            self.rows.append({"t": self.tick, "w": pid, "tg": rid, "c": c.id, "m": mechanism, "res": res, "prov": pr, "vec": "".join(vec),
                              "sr_res": sc_res, "sr_prov": sc_prov, "fw": f_writer, "fc": f_child, "trb": trb})

    def dual_summary(self) -> Dict:
        alive = [o for o in self.cells if o is not None]
        out = {"B": dict(self.B), "first": self.first, "n_alive": len(alive)}
        for r in ("res", "prov"):
            roots = [self.g[r].get(o.id, o.id) for o in alive]
            depths = [self.gd[r].get(o.id, 0) for o in alive]
            out["glin_%s_alive_roots" % r] = len(set(roots))
            out["glin_%s_max_depth_alive" % r] = max(depths) if depths else 0
            out["glin_%s_mean_depth_alive" % r] = round(sum(depths) / len(depths), 3) if depths else 0.0
        out["glin_root_disagree_alive"] = sum(1 for o in alive if self.g["res"].get(o.id, o.id) != self.g["prov"].get(o.id, o.id))
        out["func_alive"] = sum(1 for o in alive if self.func(bytes(o.tape)))
        td = [self.trb_depth.get(o.id, 0) for o in alive]
        out["trb_alive"] = sum(1 for d in td if d > 0)
        out["trb_max_depth"] = max(self.trb_depth.values()) if self.trb_depth else 0
        out["trb_max_depth_alive"] = max(td) if td else 0
        out["trb_mech_signatures"] = len(self.sig_trb)
        out["trb_mech_top"] = [[list(k), v] for k, v in self.sig_trb.most_common(5)]
        return out
