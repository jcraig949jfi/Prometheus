"""Observation-only world wrapper for the NPE ancestry replay: every pair interaction of a T-003 run, traced.

`Observed` subclasses the FROZEN world.Runner (imported from roles/Nestor/campaigns/z80atlas-verify-2026-09-22, never
edited). For each pair interaction it:
  1. captures the exact pre-state (both genomes, persisted registers and flags, persisted per-byte origin vectors);
  2. lets the world run the interaction UNCHANGED (super()._pair_interact);
  3. re-executes it in z8shadow.Shadow and ASSERTS value identity with what the world computed: both pre-mutation halves
     (captured inside _mutate) and both organisms' registers and flags afterwards;
  4. labels the harness write-back: _mutate is re-implemented for this cell to record every mutation at its RNG draw,
     and is checked against the frozen _mutate (identical bytes AND identical RNG state afterwards; the frozen one is
     what the world keeps);
  5. emits one compact row per interaction and a full record for births and for P4-eligible non-accepted interactions.

The world's RNG is never consumed by the observer (getstate/setstate around the replicated mutation only).
"""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
Z = HERE.parents[1] / "z80atlas-verify-2026-09-22"
if str(Z) not in sys.path:
    sys.path.insert(0, str(Z))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import world as W                                             # noqa: E402  (frozen)
import z8                                                     # noqa: E402  (frozen)
import z8shadow as S                                          # noqa: E402

CELL_EXPECT = {"world": "PAIR_TAPE", "reproduction": "PAIR_EXECUTION", "structure": "RESERVOIR",
               "representation": "Z8_32", "mutation_operator": "OPCODE", "mutation_locality": "LOCAL",
               "copy_primitive": "BYTEWISE"}


class ShadowMismatch(AssertionError):
    pass


def enc_label(dl):
    """JSON-safe data label."""
    k = dl[0]
    if k == "E":
        o = dl[3]
        return ["E", dl[1], dl[2], list(o) if isinstance(o, tuple) else o]
    if k == "C":
        return ["C", sorted(enc_base(b) for b in dl[1])]
    if k == "F":
        return ["F", enc_label(dl[1])]
    if k == "M":
        return ["M", list(dl[1]), enc_label(dl[2])]
    return list(dl)


def enc_base(b):
    if b[0] == "M":
        return "M|%s|%d|%d" % b[1]
    return "|".join(str(x) for x in b)


def enc_set(s):
    return sorted(enc_base(b) for b in s)


class Observed(W.Runner):
    def __init__(self, *a, sink=None, full_filter=None, **kw):
        self._ov = {}                                            # id(org) -> (org, persisted origin vector)
        self._sink = sink
        self._muts = []
        self._iid = 0
        self.shadow_checked = 0
        super().__init__(*a, **kw)
        for k, v in CELL_EXPECT.items():
            if self.cell.get(k) != v:
                raise ValueError("observer built for the T-003 cell; %s=%r" % (k, self.cell.get(k)))
        if self.cell.get("atlas_axis") == "RECOMBINATION":
            raise ValueError("recombination not supported by this observer")

    # ---------------------------------------------------------------- persisted origin vectors
    def _orig_of(self, org, g):
        hit = self._ov.get(id(org))
        if hit is not None and hit[0] is org and len(hit[1]) == len(g):
            return hit[1]
        vec = [("init", org.oid, i) for i in range(len(g))]      # first sight: the organism's own initial bytes
        self._ov[id(org)] = (org, vec)
        return vec

    # ---------------------------------------------------------------- mutation, labelled at the draw
    def _my_mutate(self, g):
        c = self.cell
        rate = self.mut_rate
        rng = self.rng
        g = bytearray(g)
        opcodes = sorted(set(self._boundaries(bytes(g))))
        opset = set(opcodes)
        events = []
        calls = 0
        for i in range(len(g)):
            if i >= len(g):
                break
            calls += 1
            rnd_at = calls - 1                                   # index of THIS position's random() call (C10 s3(a))
            if rng.random() >= rate:
                continue
            is_op = i in opset
            if c["mutation_operator"] == "OPCODE" and not is_op:
                continue
            if is_op:
                old = g[i]
                calls += 1
                g[i] = rng.randrange(256)
                events.append({"pos": i, "call": calls - 1, "rnd": rnd_at, "old": old, "new": g[i],
                               "decode_dep_positions": list(opcodes)})       # C6 E: all PRE-mutation boundaries
        self._mutate_calls = calls                               # total RNG calls this half consumed
        return bytes(g[:self.slot_size]), events

    def _mutate(self, g):
        st = self.rng.getstate()
        if not self._muts:
            self._wb_state = st                                 # world RNG state at the interaction's write-back
        mine, events = self._my_mutate(g)
        st_after = self.rng.getstate()
        self.rng.setstate(st)
        theirs = super()._mutate(g)
        if theirs != mine or self.rng.getstate() != st_after:
            raise ShadowMismatch("replicated _mutate differs from the frozen one")
        self._muts.append((bytes(g), theirs, events, self._mutate_calls))
        return theirs

    # ---------------------------------------------------------------- the interaction
    def _pair_interact(self, i, a, b):
        ga, gb = self._genome(a), self._genome(b)
        n = self.L
        size = W._pow2(2 * n)
        pre_oid = (a.oid, b.oid)
        regs = {0: None if a.regs is None else list(a.regs), 1: None if b.regs is None else list(b.regs)}
        flags = {0: (a.fz, a.fc), 1: (b.fz, b.fc)}
        oa, ob = self._orig_of(a, ga), self._orig_of(b, gb)
        tape = bytearray(size)
        tape[0:len(ga)] = ga
        tape[n:n + len(gb)] = gb
        labels = S.initial_tape_labels(ga, gb, n, size, oa, ob)
        rl, fl = {}, {}
        for s in (0, 1):
            rl[s], fl[s] = S.initial_reg_labels(s, regs[s])
        n0 = len(self.lineage)
        self._muts = []
        self._iid += 1
        iid = (self.epoch, i, self._iid)
        super()._pair_interact(i, a, b)
        # ---- shadow re-execution and value identity
        sh = S.Shadow(bytes(tape), labels, regs, rl, flags, fl, self.t["slice"], self._ops_mask())
        ra, rb = sh.run_pair(n)
        if len(self._muts) != 2:
            raise ShadowMismatch("expected two write-backs, saw %d" % len(self._muts))
        halves = (bytes(sh.mem[0:n]), bytes(sh.mem[n:2 * n]))
        if self._muts[0][0] != halves[0] or self._muts[1][0] != halves[1]:
            raise ShadowMismatch("shadow tape != world tape at %r" % (iid,))
        for org, rr in ((a, ra), (b, rb)):
            if list(org.regs) != list(rr["regs"]) or org.fz != rr["fz"] or org.fc != rr["fc"]:
                raise ShadowMismatch("shadow registers/flags != world at %r" % (iid,))
        self.shadow_checked += 1
        # ---- write-back labels (per half): final shadow labels, then mutation at the draw, then tail clearing
        last_store = {}
        for st in sh.stores:
            last_store[st.addr] = st
        post = {}
        offsets = {0: 0, 1: self._muts[0][3]}                    # C10 s3(a): write-back-wide RNG call index
        for side, org in ((0, a), (1, b)):
            off = 0 if side == 0 else n
            pre_mut, new, events, _ncalls = self._muts[side]
            hl = [sh.lab[off + j] for j in range(n)]
            for ev in events:
                old = hl[ev["pos"]]
                hl[ev["pos"]] = (("M", ("ab"[side], offsets[side] + ev["rnd"], ev["pos"]), old[0]), S.EMPTY)
            final = []
            for j in range(self.slot_size):
                final.append(hl[j] if j < len(new) else (("K", "clear"), S.EMPTY))
            post[side] = (final, new, events)
            # persisted origin vector of the organism now occupying this slot
            vec = []
            for j in range(len(new)):
                dl = final[j][0]
                vec.append(dl[3] if dl[0] == "E" and dl[3] is not None else ("new", iid[2], side, j))
            self._ov[id(org)] = (org, vec)
        births = [e for e in self.lineage[n0:] if e.get("kind") == "birth"]
        if self._sink is not None:
            self._sink(self, iid, pre_oid, (a, b), (ga, gb), regs, flags, sh, last_store, post, births, n)
