"""Single-interaction interventions on an exported birth (v4 s4.1 + B1, v5 R1/R2/R4/R5/C1). Observation only.

Every arm re-executes ONE pair interaction from the birth's recorded pre-state with z8shadow.Shadow (value-identical to
the frozen VM; selftest_shadow.py), with one intervention applied, and compares the victim half BEFORE the harness
mutation. Mutated loci carry MUTATION labels and never enter a MOVE arm. Acceptance of the counterfactual is recomputed
with the frozen predecessor criterion (p11.predecessor_accepts) on the counterfactual halves, with the harness mutation
omitted. DECLARED: the write-back RNG cannot be held fixed across a changed decode.

Arms
  flip        s4.1/B1/R4. For every written ENTITY-MOVE locus (X, j), each of 8 bits of (X, j) is flipped in the
              pre-state. The bit is APPLICABLE iff three sequences are unchanged: the fetched-instruction trace
              (pc, opcode CLASS), the store-address sequence and the load-address sequence. When applicable, the locus
              must equal the moved value with that bit flipped. Z8 opcode classes (R4):
                - every undefined one-byte opcode is one class (NOP);
                - ED with an op2 that is undefined or disabled under the run's op mask is one class (ED-NOP);
                - otherwise the opcode itself (with op2 for ED).
  depend      R1(3) and R2. Source groups: each ENTITY's bytes, and each side's persisted registers+flags. INPUT is
              empty in this cell (N3). For a locus with data label (X, j) and performer entity Y, every group outside
              {X, Y} is randomised in turn, K = 8 draws each.
                - IDENTIFIED needs 0 value changes among draws where the write occurs.
                - Q8c = Pr(value change | write occurs), pooled over (group, draw).
                - Q8c-whether = Pr(the locus is not written OR the birth is not accepted).
  complete    R5. Each single byte NOT named in any of the locus's sets (tape bytes and persisted register bytes) is
              randomised alone, K = 4 times. Reported: the share of bytes that change the locus value with the path
              (trace + store addresses) and the birth preserved. Gate: <= 5% per class.
  precision   C1. Each single NAMED base-label byte, K = 4. Reported (not gating): the share that ever change the
              value, the write or the birth.
"""
from __future__ import annotations

import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
Z = HERE.parents[1] / "z80atlas-verify-2026-09-22"
for p in (str(Z), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import p11                                                    # noqa: E402  (frozen)
import world as W                                             # noqa: E402  (frozen: _fidelity)
import z8shadow as S                                          # noqa: E402

DEFINED_ED = {0x30: 0x01, 0x31: 0x01, 0x32: 0x02, 0x33: 0x04, 0x34: 0x08, 0x35: 0x10, 0xB0: 0x20, 0xB8: 0x20}
ONE_BYTE_DEFINED = {0x01, 0x11, 0x21, 0x31, 0x02, 0x12, 0x0A, 0x1A, 0x03, 0x13, 0x23, 0x0B, 0x1B, 0x2B, 0x18, 0x20,
                    0x28, 0x30, 0x38, 0xC3, 0xC2, 0xCA, 0xD2, 0xDA, 0xC6, 0xD6, 0xE6, 0xEE, 0xF6, 0xFE, 0xDB, 0xD3}
REG_GROUP = {0: "PREG_a", 1: "PREG_b"}
ENT_GROUP = {"a": "ENT_a", "b": "ENT_b"}


def op_class(entry, mask):
    op = entry[1]
    if op == 0xED:
        need = DEFINED_ED.get(entry[2])
        return ("ED", entry[2]) if need is not None and (mask & need) else ("ED-NOP",)
    if 0x40 <= op < 0xC0 or (op < 0x40 and (op & 7) in (4, 5, 6)) or op in ONE_BYTE_DEFINED:
        return (op,)
    return ("NOP",)


class Pre:
    """A birth's pre-state, copyable and editable for interventions."""

    def __init__(self, rec=None):
        if rec is None:
            return
        p = rec["pre"]
        self.n, self.size = rec["n"], p["tape_len"]
        self.g = {0: bytearray.fromhex(p["ga"]), 1: bytearray.fromhex(p["gb"])}
        self.regs = {0: None if p["regs_a"] is None else list(p["regs_a"]),
                     1: None if p["regs_b"] is None else list(p["regs_b"])}
        self.flags = {0: tuple(p["flags_a"]), 1: tuple(p["flags_b"])}
        self.budget, self.mask = p["budget"], p["ops_mask"]
        self.vside = 0 if rec["victim_side"] == "a" else 1

    def copy(self):
        c = Pre()
        c.n, c.size, c.budget, c.mask, c.vside = self.n, self.size, self.budget, self.mask, self.vside
        c.g = {k: bytearray(v) for k, v in self.g.items()}
        c.regs = {k: (None if v is None else list(v)) for k, v in self.regs.items()}
        c.flags = dict(self.flags)
        return c


class Run:
    """One executed (counterfactual) interaction."""

    def __init__(self, pre: Pre, trace: bool = True):
        n, size = pre.n, pre.size
        tape = bytearray(size)
        tape[0:len(pre.g[0])] = pre.g[0]
        tape[n:n + len(pre.g[1])] = pre.g[1]
        lab = S.initial_tape_labels(bytes(pre.g[0]), bytes(pre.g[1]), n, size)
        rl, fl = {}, {}
        for s in (0, 1):
            rl[s], fl[s] = S.initial_reg_labels(s, pre.regs[s])
        self.sh = sh = S.Shadow(bytes(tape), lab, pre.regs, rl, pre.flags, fl, pre.budget, pre.mask,
                                record_trace=trace)
        sh.run_pair(n)
        self.pre = pre
        voff = 0 if pre.vside == 0 else n
        self.voff = voff
        self.victim = bytes(sh.mem[voff:voff + n])
        self.last = {}
        for st in sh.stores:
            self.last[st.addr] = st
        doff = 0 if pre.vside == 1 else n
        donor_wrote = sum(1 for s_ in sh.stores if s_.side == 1 - pre.vside and not (doff <= s_.addr < doff + n))
        self.accepted = p11.predecessor_accepts(W._fidelity(bytes(pre.g[1 - pre.vside]), self.victim),
                                                W._fidelity(bytes(pre.g[pre.vside]), self.victim), donor_wrote, n)
        if trace:
            self.path = (tuple((e[0], op_class(e, pre.mask)) for e in sh.trace), tuple(sh.store_addrs))
            self.loads = tuple(sh.load_addrs)

    def written(self, j):
        return (self.voff + j) in self.last

    def cell(self, j):
        return self.sh.lab[self.voff + j]


def ent_side(ent):
    return 0 if ent == "a" else 1


class NotPaired(AssertionError):
    pass


def assert_paired(pre: Pre, c: Pre, changed: set):
    """C9-D24 lesson (operator directive 2026-09-28 s4): a counterfactual is PAIRED only if every component outside the
    intervened set is shown identical. Components: ('G', side) genome, ('R', side) registers, ('F', side) flags,
    budget, op mask, sides, sizes. The single-interaction replay consumes no RNG (Shadow has none; LDIR, the only
    in-VM RNG user, is disabled under mask 0x0C) -- asserted here too."""
    if (c.n, c.size, c.budget, c.mask, c.vside) != (pre.n, pre.size, pre.budget, pre.mask, pre.vside):
        raise NotPaired("interaction parameters differ")
    if c.mask & 0x20:
        raise NotPaired("LDIR enabled: in-VM copy noise would consume RNG; pairing not established")
    for s in (0, 1):
        if ("G", s) not in changed and c.g[s] != pre.g[s]:
            raise NotPaired("genome %d changed outside the intervention" % s)
        if ("R", s) not in changed and c.regs[s] != pre.regs[s]:
            raise NotPaired("registers %d changed outside the intervention" % s)
        if ("F", s) not in changed and c.flags[s] != pre.flags[s]:
            raise NotPaired("flags %d changed outside the intervention" % s)


def randomise_group(pre: Pre, group: str, rng: random.Random):
    c = pre.copy()
    if group.startswith("ENT_"):
        s = ent_side(group[-1])
        c.g[s] = bytearray(rng.randrange(256) for _ in range(len(c.g[s])))
        assert_paired(pre, c, {("G", s)})
    else:
        s = 0 if group.endswith("_a") else 1
        if c.regs[s] is None:
            return None                                      # fresh organism: no persisted registers to randomise
        c.regs[s] = [rng.randrange(256) for _ in range(8)]
        c.flags[s] = (rng.randrange(2), rng.randrange(2))
        assert_paired(pre, c, {("R", s), ("F", s)})
    return c


def groups_outside(pre: Pre, keep: set):
    out = []
    for ent in ("a", "b"):
        if ent not in keep:
            out.append(ENT_GROUP[ent])
    for s in (0, 1):
        if pre.regs[s] is not None:
            out.append(REG_GROUP[s])                          # persisted registers are their own group (R1)
    return out


# ---------------------------------------------------------------- the arms, per birth
def analyse_birth(rec, seed: int, K_dep: int = 8, K_byte: int = 4, per_byte: bool = False):
    pre = Pre(rec)
    base = Run(pre)
    n, v = pre.n, pre.vside
    if base.victim.hex() != rec["victim_final_pre_mutation"]:
        raise AssertionError("re-execution does not reproduce the recorded victim half")
    rng = random.Random(seed)
    loci = []
    for j in range(n):
        dl, _ad = base.cell(j)
        written = base.written(j)
        st = base.last.get(base.voff + j)
        perf = st.performer if st is not None else None
        perf_ent = perf[1] if perf is not None and perf[0] == "E" else None
        row = {"j": j, "written": written, "kind": dl[0], "move_ent": dl[1] if dl[0] == "E" else None,
               "src_locus": dl[2] if dl[0] == "E" else None, "performer_ent": perf_ent,
               "performer_kind": perf[0] if perf is not None else None}
        if written and dl[0] == "E":
            X, sj = dl[1], dl[2]
            xs = ent_side(X)
            # --- flip test
            conf = fail = inap = 0
            for bit in range(8):
                c = pre.copy()
                c.g[xs][sj] ^= (1 << bit)
                assert_paired(pre, c, {("G", xs)})
                r = Run(c)
                if r.path != base.path or r.loads != base.loads:
                    inap += 1
                    continue
                predicted = base.victim[j] ^ (1 << bit)
                if r.victim[j] == predicted:
                    conf += 1
                else:
                    fail += 1
            row["flip"] = "FAILED" if fail else ("CONFIRMED" if conf else "INAPPLICABLE")
            row["flip_bits"] = [conf, fail, inap]
            # --- PROPOSED prefix rule (reported beside the strict rule, pending Archaeon's ruling): the path is
            # compared only UP TO the last store to this locus, and the counterfactual must not store to it later
            conf2 = fail2 = inap2 = 0
            bst = base.last[base.voff + j]
            for bit in range(8):
                c = pre.copy()
                c.g[xs][sj] ^= (1 << bit)
                r = Run(c)
                rst = r.last.get(base.voff + j)
                same = (rst is not None and rst.six == bst.six and rst.tix == bst.tix
                        and r.path[0][:bst.tix] == base.path[0][:bst.tix]
                        and r.path[1][:bst.six + 1] == base.path[1][:bst.six + 1]
                        and r.loads[:bst.lix] == base.loads[:bst.lix])
                if not same:
                    inap2 += 1
                    continue
                if r.victim[j] == (base.victim[j] ^ (1 << bit)):
                    conf2 += 1
                else:
                    fail2 += 1
            row["flip_prefix"] = "FAILED" if fail2 else ("CONFIRMED" if conf2 else "INAPPLICABLE")
            row["flip_prefix_bits"] = [conf2, fail2, inap2]
            # --- dependence (R1) and Q8c (R2)
            keep = {X} | ({perf_ent} if perf_ent else set())
            changes = draws_written = whether = total = 0
            per_group = {}
            for grp in groups_outside(pre, keep):
                gc = gw = 0
                for _k in range(K_dep):
                    c = randomise_group(pre, grp, rng)
                    if c is None:
                        break
                    r = Run(c, trace=False)
                    total += 1
                    if not r.written(j) or not r.accepted:
                        whether += 1
                        continue
                    draws_written += 1
                    gw += 1
                    if r.victim[j] != base.victim[j]:
                        changes += 1
                        gc += 1
                per_group[grp] = [gc, gw]
            row["dep_groups"] = per_group
            row["dep_changes"] = changes
            row["q8c"] = (changes / draws_written) if draws_written else None
            row["q8c_whether"] = (whether / total) if total else None
            row["identified"] = row["flip"] != "FAILED" and changes == 0
        loci.append(row)
    out = {"child": rec["child"], "run": rec["run"], "victim_side": rec["victim_side"], "loci": loci,
           "accepted_reproduced": base.accepted,
           "existence": birth_existence(pre, rng, K_dep),
           "source_diversity": len({(l["move_ent"], l["src_locus"]) for l in loci
                                    if l["written"] and l["kind"] == "E"})}
    if per_byte:
        out["per_byte"] = per_byte_arms(rec, pre, base, rng, K_byte)
    return out


def birth_existence(pre: Pre, rng, K: int = 8):
    """Amendment C4: Q8c-whether per birth, PERFORMER INCLUDED. Every source group (each entity's bytes, each side's
    persisted registers) is randomised in turn, K draws; the share of draws in which the birth is NOT accepted."""
    res = {}
    for grp in ["ENT_a", "ENT_b"] + [REG_GROUP[s] for s in (0, 1) if pre.regs[s] is not None]:
        sup = tot = 0
        for _k in range(K):
            c = randomise_group(pre, grp, rng)
            if c is None:
                break
            tot += 1
            sup += not Run(c, trace=False).accepted
        res[grp] = [sup, tot]
    return res


def _named_bytes(rec_locus_sets, pre: Pre):
    """Map named base labels to concrete bytes: ('E', ent, i) -> tape byte; ('P', ent, reg) -> register/flag."""
    out = set()
    for b in rec_locus_sets:
        if b[0] == "E":
            out.add(("T", ent_side(b[1]), b[2]))
        elif b[0] == "P":
            out.add(("R", ent_side(b[1]), b[2]))
    return out


def per_byte_arms(rec, pre: Pre, base: Run, rng, K):
    """R5 completeness (gating) and C1 precision (reported) for every written locus of this birth."""
    universe = [("T", s, i) for s in (0, 1) for i in range(len(pre.g[s]))]
    for s in (0, 1):
        if pre.regs[s] is not None:
            universe += [("R", s, r) for r in range(8)] + [("R", s, "fz"), ("R", s, "fc")]
    res = []
    for j in range(pre.n):
        if not base.written(j):
            continue
        st = base.last[base.voff + j]
        named_b = S.deps(st.cell) | st.ctrl | st.exec_
        named = _named_bytes(named_b, pre)
        leak = tested_un = 0
        hit_named = tested_named = 0
        for u in universe:
            is_named = u in named
            changed_any = False
            leaked = False
            for _k in range(K):
                c = pre.copy()
                if u[0] == "T":
                    c.g[u[1]][u[2]] = rng.randrange(256)
                elif u[2] == "fz":
                    c.flags[u[1]] = (1 - c.flags[u[1]][0], c.flags[u[1]][1])
                elif u[2] == "fc":
                    c.flags[u[1]] = (c.flags[u[1]][0], 1 - c.flags[u[1]][1])
                else:
                    c.regs[u[1]][u[2]] = rng.randrange(256)
                r = Run(c)
                changed = (not r.written(j)) or (not r.accepted) or r.victim[j] != base.victim[j]
                changed_any |= changed
                if not is_named and r.path == base.path and r.accepted and r.written(j) \
                        and r.victim[j] != base.victim[j]:
                    leaked = True
            if is_named:
                tested_named += 1
                hit_named += changed_any
            else:
                tested_un += 1
                leak += leaked
        res.append({"j": j, "unnamed_tested": tested_un, "unnamed_leaks": leak,
                    "named_tested": tested_named, "named_effective": hit_named})
    return res
