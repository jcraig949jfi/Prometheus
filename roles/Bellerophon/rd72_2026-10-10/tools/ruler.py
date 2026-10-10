"""BEL-RD-72 anti-triviality ruler: a PROFILE of minimal causal organization for one tape (no single complexity score).

ruler(tape, task_kind) -> dict, under the v3 competence check (tasks.verify_exact) and FUNC (belinst.Func):
  competent / func            the two capabilities
  ccrit / rcrit               competence-critical / replication-critical bytes (nonzero byte -> NOP knockout breaks it)
  shared                      bytes critical for BOTH (coupling of computation and heredity)
  redundant_pairs             pairs (i, j) of non-critical nonzero bytes whose JOINT knockout breaks competence (hidden
                              redundancy single knockout cannot see), capped at the first 64 nonzero non-critical bytes
  halves                      LO / HI / BOTH / NONE on the fixed panels (composite tasks only)
  generations                 k-generation heredity: tape -> child -> grandchild (own window copy, fresh memory each time);
                              per generation whether the descendant is FUNC and competent (computation that persists
                              through copying, not only in the original)
  span                        last minus first critical position + 1 (program extent)"""
import sys, pathlib
_H = pathlib.Path(__file__).resolve()
for _p in (_H.parent, _H.parents[1].parent / "bel48h_2026-10-08" / "tools", _H.parents[4]):
    sys.path.insert(0, str(_p))
from belinst import Func
from prometheus.z80atlas import vm, tasks, coupling_campaign as CC
from prometheus.z80atlas.world import Config
L = 64


def _cfg():
    d = dict(CC.COMMON, **CC.V3, **CC.K["K40"]); d.update(coupling="ON", budget=256)
    return Config(**d)


def child_of(tape, cfg):
    mem = bytearray(256); mem[:L] = tape
    vm.execute(mem, L, 0, cfg.budget, [0], allow_copyall=cfg.allow_copyall, strict_budget=cfg.physics != "v1", **cfg.chem)
    return bytes(mem[L:2 * L])


def ruler(tape: bytes, task_kind: str, gens: int = 3, pair_cap: int = 64) -> dict:
    cfg = _cfg(); func = Func(cfg); task = tasks.Task(task_kind)
    tape = bytes(tape[:L]) + bytes(max(0, L - len(tape)))
    comp = lambda t: tasks.verify_exact(t, L, task, "ABR", budget=256)
    ko = lambda t, ps: bytes(vm.NOP if i in ps else b for i, b in enumerate(t))
    nz = [i for i in range(L) if tape[i] != 0]
    c0, f0 = comp(tape), func(tape)
    ccrit = [i for i in nz if c0 and not comp(ko(tape, {i}))]
    rcrit = [i for i in nz if f0 and not func(ko(tape, {i}))]
    red = []
    if c0:
        rest = [i for i in nz if i not in ccrit][:pair_cap]
        for a in range(len(rest)):
            for b in range(a + 1, len(rest)):
                if not comp(ko(tape, {rest[a], rest[b]})):
                    red.append((rest[a], rest[b]))
    g = []; t = tape
    for _ in range(gens):
        t = child_of(t, cfg); g.append({"func": func(t), "competent": comp(t), "identical": t == tape})
    out = {"competent": c0, "func": f0, "ccrit": ccrit, "rcrit": rcrit, "shared": sorted(set(ccrit) & set(rcrit)),
           "n_ccrit": len(ccrit), "n_rcrit": len(rcrit), "redundant_pairs": red, "generations": g,
           "span": (max(ccrit) - min(ccrit) + 1) if ccrit else 0, "nonzero": len(nz)}
    if task_kind in ("COND_ONE", "COND_MULTI"):
        from halves import LO_PANEL, HI_PANEL, _expected
        def ok(x):
            mem = bytearray(256); mem[:L] = tape; mem[vm.IN_BASE] = x
            tr = vm.execute(mem, L, 0, cfg.budget, [x], allow_copyall=cfg.allow_copyall, strict_budget=cfg.physics != "v1", **cfg.chem)
            return bool(tr.outputs) and tr.outputs[0] == _expected(task_kind, x)
        lo = all(ok(x) for x in LO_PANEL); hi = all(ok(x) for x in HI_PANEL)
        out["halves"] = "BOTH" if lo and hi else ("LO" if lo else ("HI" if hi else "NONE"))
    return out
