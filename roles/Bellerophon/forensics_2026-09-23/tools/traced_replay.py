"""Instrumented replay: re-run a historical run with the FROZEN harness plus byte-provenance tracing, and classify
every birth the harness registered. The tracer is a line-for-line copy of vm.execute with bookkeeping added; its
fidelity to the original is CHECKED on every replay: the regenerated summary must equal the stored one (minus
wall_s), else the row is marked TRACER_DIVERGED and not used.

Birth classes (frozen before the first traced replay; see POST_CAMPAIGN_FORENSICS.md s3.1):
  COPY_EVENT         any birth the harness registered (endogenous physics)
  SELF_REPLICATION   COPY_EVENT where (a) material == writer and fidelity vs the writer's tape >= 0.9, (b) >= 90% of
                     the child's L bytes were last written by a copy op (LDI/LDIR/COPYALL) whose SOURCE address lay in
                     the writer's own tape [0,L), and (c) >= 90% of those writes were executed with the PC inside the
                     writer's own tape (the writer's code did it, not the partner's code it ran into).
  lineage depth      sr_depth(child) = sr_depth(writer) + 1 for a SELF_REPLICATION birth, else 0.
  SUSTAINED_LINEAGE  a run in which some SELF_REPLICATION chain reaches depth >= 3.
  EVOLUTIONARILY_ACTIVE_LINEAGE  a run in which a SELF_REPLICATION birth with child != writer tape (a heritable
                     variant) is itself the root of a SELF_REPLICATION chain of depth >= 2 (the variant is transmitted).

    python traced_replay.py --set spontaneous --workers 14
    python traced_replay.py --set baseline --n 300 --seed 11
    python traced_replay.py r000123 ...
Writes receipts/TRACED_<tag>.json (per-run rows) -- small; per-birth detail stays in LOCAL."""
from __future__ import annotations

import argparse
import collections
import json
import multiprocessing as mp
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
import load as Ld  # noqa: E402

HARNESS = "C:/Users/James/z80atlas_campaign_2026-09-19/code"
COPY_OPS = (0x14, 0x15, 0x16)   # LDI, LDIR, COPYALL

_ACC = {"L": 64, "writes": {}, "own_steps": 0, "win_steps": 0, "other_steps": 0}


def _install():
    if HARNESS not in sys.path:
        sys.path.insert(0, HARNESS)
    from prometheus.z80atlas import vm
    from prometheus.z80atlas import world as W
    if getattr(vm, "_traced", False):
        return vm, W
    SPACE, IN_BASE, OUT_BASE = vm.SPACE, vm.IN_BASE, vm.OUT_BASE
    OPLEN = vm.OPLEN; Trace = vm.Trace
    op_ = vm  # opcode constants

    def execute(mem, L, entry, budget, inputs, region=None, allow_copyall=False, cost_per_step=1):
        # ---- line-for-line copy of vm.execute (frozen), with provenance bookkeeping marked TRACE ----
        A = B = C = D = S = T = 0
        Z = False; CF = False
        pc = entry & 0xFF
        tr = Trace()
        inp = list(inputs); ip = 0
        lo, hi = (region if region else (0, SPACE))
        nb_lo, nb_hi = L, 2 * L
        WL = _ACC["L"]                                                  # TRACE: the WORLD's L (pair execution passes 2L)
        while tr.steps < budget:
            if not (lo <= pc < hi):
                break
            op = mem[pc]
            tr.steps += 1
            tr.opcodes[op] = tr.opcodes.get(op, 0) + 1
            tr.pc_max = max(tr.pc_max, pc)
            if pc < WL: _ACC["own_steps"] += 1                          # TRACE
            elif pc < 2 * WL: _ACC["win_steps"] += 1                    # TRACE
            else: _ACC["other_steps"] += 1                              # TRACE
            n = OPLEN.get(op, 0)
            arg = mem[(pc + 1) & 0xFF] if n else 0
            npc = (pc + 1 + n) & 0xFF
            cur_pc = pc

            def W(addr, v, src=None):
                addr &= 0xFF
                if IN_BASE <= addr < OUT_BASE and mem[addr] != (v & 0xFF):
                    tr.io_corrupt += 1
                    if tr.io_corrupt_step is None:
                        tr.io_corrupt_step = tr.steps
                mem[addr] = v & 0xFF
                tr.writes[addr] = v & 0xFF
                if WL <= addr < 2 * WL:                                 # TRACE: last writer of each world-window byte
                    _ACC["writes"][addr - WL] = (src, cur_pc, op)
                if addr < L:
                    tr.self_writes += 1
                elif nb_lo <= addr < nb_hi:
                    tr.neighbour_writes += 1
                elif IN_BASE <= addr < OUT_BASE:
                    tr.io_writes += 1

            if op == op_.HALT:
                tr.halted = True; break
            elif op == op_.LD_A_n: A = arg
            elif op == op_.LD_B_n: B = arg
            elif op == op_.LD_C_n: C = arg
            elif op == op_.LD_D_n: D = arg
            elif op == op_.LD_S_n: S = arg
            elif op == op_.LD_T_n: T = arg
            elif op == op_.LD_A_pS:
                A = mem[S]; tr.neighbour_reads += 1 if nb_lo <= S < nb_hi else 0
            elif op == op_.LD_A_pT:
                A = mem[T]; tr.neighbour_reads += 1 if nb_lo <= T < nb_hi else 0
            elif op == op_.LD_pT_A: W(T, A)
            elif op == op_.LD_pS_A: W(S, A)
            elif op == op_.LDI:
                v = mem[S]; W(T, v, S)
                if nb_lo <= T < nb_hi: tr.copy_events += 1
                S = (S + 1) & 0xFF; T = (T + 1) & 0xFF; C = (C - 1) & 0xFF
            elif op == op_.LDIR:
                while True:
                    v = mem[S]; W(T, v, S)
                    if nb_lo <= T < nb_hi: tr.copy_events += 1
                    S = (S + 1) & 0xFF; T = (T + 1) & 0xFF; C = (C - 1) & 0xFF
                    tr.steps += 1
                    if C == 0 or tr.steps >= budget:
                        break
            elif op == op_.COPYALL and allow_copyall:
                for i in range(L):
                    W((T + i) & 0xFF, mem[(S + i) & 0xFF], (S + i) & 0xFF)
                if nb_lo <= T < nb_hi: tr.copy_events += L
                tr.steps += L // 8
            elif op == op_.ADD_A_B: A = (A + B) & 0xFF; Z = A == 0
            elif op == op_.SUB_A_B: CF = A < B; A = (A - B) & 0xFF; Z = A == 0
            elif op == op_.INC_A: A = (A + 1) & 0xFF; Z = A == 0
            elif op == op_.DEC_A: A = (A - 1) & 0xFF; Z = A == 0
            elif op == op_.INC_S: S = (S + 1) & 0xFF
            elif op == op_.INC_T: T = (T + 1) & 0xFF
            elif op == op_.XOR_A_B: A ^= B; Z = A == 0
            elif op == op_.AND_A_B: A &= B; Z = A == 0
            elif op == op_.OR_A_B: A |= B; Z = A == 0
            elif op == op_.ADD_A_n: A = (A + arg) & 0xFF; Z = A == 0
            elif op == op_.SHL_A: CF = bool(A & 0x80); A = (A << 1) & 0xFF; Z = A == 0
            elif op == op_.SHR_A: CF = bool(A & 1); A >>= 1; Z = A == 0
            elif op == op_.INC_C: C = (C + 1) & 0xFF; Z = C == 0
            elif op == op_.DEC_C: C = (C - 1) & 0xFF; Z = C == 0
            elif op == op_.CP_A_n: Z = A == arg; CF = A < arg
            elif op == op_.CP_A_B: Z = A == B; CF = A < B
            elif op == op_.JP_n: npc = arg
            elif op == op_.JZ_n:
                if Z: npc = arg
            elif op == op_.JNZ_n:
                if not Z: npc = arg
            elif op == op_.JC_n:
                if CF: npc = arg
            elif op == op_.JR_d:
                d = arg - 256 if arg > 127 else arg; npc = (pc + 2 + d) & 0xFF
            elif op == op_.DJNZ_d:
                B = (B - 1) & 0xFF
                if B != 0:
                    d = arg - 256 if arg > 127 else arg; npc = (pc + 2 + d) & 0xFF
            elif op == op_.IN_A:
                if tr.first_in_step is None: tr.first_in_step = tr.steps
                tr.reads_in += 1
                A = mem[(IN_BASE + ip) & 0xFF] if ip < 16 else 0
                ip += 1
            elif op == op_.OUT_A:
                if tr.first_out_step is None: tr.first_out_step = tr.steps
                if tr.first_in_step is None: tr.outputs_before_read += 1
                if len(tr.outputs) < 16:
                    mem[OUT_BASE + len(tr.outputs)] = A
                    tr.outputs.append(A)
            elif op in (op_.LD_B_A, op_.LD_A_B, op_.LD_C_A, op_.LD_A_C, op_.LD_S_A, op_.LD_T_A, op_.LD_A_S, op_.LD_A_T, op_.LD_D_A, op_.LD_A_D, op_.SWAP_A_B):
                if op == op_.LD_B_A: B = A
                elif op == op_.LD_A_B: A = B
                elif op == op_.LD_C_A: C = A
                elif op == op_.LD_A_C: A = C
                elif op == op_.LD_S_A: S = A
                elif op == op_.LD_T_A: T = A
                elif op == op_.LD_A_S: A = S
                elif op == op_.LD_A_T: A = T
                elif op == op_.LD_D_A: D = A
                elif op == op_.LD_A_D: A = D
                else: A, B = B, A
            pc = npc
        return tr

    vm.execute = execute
    vm._traced = True
    return vm, W


class _Rec:
    pass


def _traced_world_class(W):
    class TW(W.World):
        def __init__(self, cfg, seed):
            self.births = []            # per-birth classification rows
            self.sr_depth = {}          # org id -> self-replication depth
            self.variant_root = {}      # org id -> True if born as a heritable self-replicated variant
            super().__init__(cfg, seed)
            _ACC["L"] = self.L

        def _reset(self, prior_window):
            _ACC["writes"] = {}; _ACC["own_steps"] = _ACC["win_steps"] = _ACC["other_steps"] = 0
            _ACC["prior"] = prior_window

        def _execute(self, o, partner_tape, inputs):
            self._reset(bytes(partner_tape) if partner_tape is not None else bytes(self.L))
            _ACC["writer_tape"] = bytes(o.tape)
            return super()._execute(o, partner_tape, inputs)

        def _pair_execute(self, a, b, inputs):
            self._reset(bytes(b.tape))
            _ACC["writer_tape"] = bytes(a.tape)
            return super()._pair_execute(a, b, inputs)

        def _register_offspring(self, j, child, parent, mechanism, fidelity, tr, replaced):
            L = self.L
            wt = _ACC.get("writer_tape") or bytes(parent.tape)
            ws = _ACC["writes"]
            fid_writer_now = 1.0 - sum(1 for x, y in zip(child, parent.tape) if x != y) / L
            fid_target = None if replaced is None else 1.0 - sum(1 for x, y in zip(child, replaced.tape) if x != y) / L
            material = "target" if (fid_target is not None and fid_target > fid_writer_now) else "writer"
            copied_from_own = sum(1 for a, (src, pc, op) in ws.items() if op in COPY_OPS and src is not None and src < L)
            by_own_code = sum(1 for a, (src, pc, op) in ws.items() if op in COPY_OPS and src is not None and src < L and pc < L)
            changed = sum(1 for k in range(L) if child[k] != _ACC["prior"][k])
            is_sr = (material == "writer" and fid_writer_now >= 0.9 and copied_from_own >= 0.9 * L and by_own_code >= 0.9 * copied_from_own)
            d_parent = self.sr_depth.get(parent.id, 0)
            super()._register_offspring(j, child, parent, mechanism, fidelity, tr, replaced)
            cid = self.next_id - 1
            self.sr_depth[cid] = d_parent + 1 if is_sr else 0
            variant = is_sr and bytes(child) != bytes(parent.tape)
            if variant:
                self.variant_root[cid] = cid
            elif is_sr and parent.id in self.variant_root:
                self.variant_root[cid] = self.variant_root[parent.id]
            self.births.append((self.tick, parent.id, cid, mechanism, round(fid_writer_now, 3), None if fid_target is None else round(fid_target, 3),
                                material, len(ws), copied_from_own, by_own_code, changed, int(is_sr), self.sr_depth[cid],
                                _ACC["own_steps"], _ACC["win_steps"], _ACC["other_steps"], int(variant)))
    return TW


def _variant_transmitted(births) -> bool:
    """a heritable self-replicated variant whose own self-replication chain reaches depth >= 2 below it"""
    sr = [b for b in births if b[11]]
    child_of = collections.defaultdict(list)
    for b in sr:
        child_of[b[1]].append(b[2])
    variants = [b[2] for b in sr if b[16]]
    def depth(x, lim=6):
        if lim == 0 or not child_of.get(x):
            return 0
        return 1 + max(depth(c, lim - 1) for c in child_of[x])
    return any(depth(v) >= 2 for v in variants)


def _one(rid: str) -> dict:
    vm, W = _install()
    from prometheus.z80atlas import grammar as G
    TW = _traced_world_class(W)
    cfg_j = Ld.run_file(rid, "config.json"); stored = Ld.run_file(rid, "summary.json")
    cfg = G.to_config(cfg_j["vec"], cfg_j["ticks"], cfg_j["cells"], cfg_j["budget"], tuple(cfg_j["init_tapes"] or ()))
    w = TW(cfg, cfg_j["seed"])
    summ = w.run()
    keys = ("endogenous_births", "replication_rate_tail", "mean_fidelity_tail", "final_alive", "captures", "null_rewrites", "first_replication")
    diverged = [k for k in keys if summ.get(k) != stored.get(k)]
    B = w.births
    tail0 = cfg.ticks - 20
    sr = [b for b in B if b[11]]
    row = {"run": rid, "vec": cfg_j["vec"], "kind": cfg_j.get("reason", "")[:40], "tracer_diverged": diverged,
           "births": len(B), "births_tail": sum(1 for b in B if b[0] >= tail0),
           "self_rep": len(sr), "self_rep_tail": sum(1 for b in sr if b[0] >= tail0),
           "material_target": sum(1 for b in B if b[6] == "target"),
           "births_changed_le_2_bytes": sum(1 for b in B if b[10] <= 2),
           "births_by_partner_code": sum(1 for b in B if b[8] and b[9] < 0.5 * b[8]),
           "hifi_births_tail": sum(1 for b in B if b[0] >= tail0 and max(b[4], b[5] or 0) >= 0.9),
           "hifi_births_tail_not_selfrep": sum(1 for b in B if b[0] >= tail0 and max(b[4], b[5] or 0) >= 0.9 and not b[11]),
           "max_sr_depth": max((b[12] for b in B), default=0),
           "first_self_rep": None, "sustained_lineage": False, "evolutionarily_active": False}
    if sr:
        f = sr[0]
        row["first_self_rep"] = {"tick": f[0], "writer": f[1], "fid": f[4], "own_steps": f[13], "win_steps": f[14]}
        row["sustained_lineage"] = row["max_sr_depth"] >= 3
        row["evolutionarily_active"] = _variant_transmitted(B)
    # the first self-replicating writer's tape (specimen) -- from the event stream is not stored; keep top tape instead
    row["top_tape"] = (summ.get("top") or [{}])[0].get("tape")
    Ld.LOCAL.mkdir(parents=True, exist_ok=True)
    (Ld.LOCAL / "births").mkdir(exist_ok=True)
    import gzip
    with gzip.open(Ld.LOCAL / "births" / (rid + ".jsonl.gz"), "wt", encoding="utf-8", newline="\n") as fh:
        fh.write("".join(json.dumps(b) + "\n" for b in B))
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="*")
    ap.add_argument("--set", choices=("spontaneous", "baseline", "replication_seeded"), default=None)
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--workers", type=int, default=14)
    ap.add_argument("--tag", default=None)
    a = ap.parse_args()
    ids = list(a.runs)
    R = Ld.runs()
    if a.set == "spontaneous":
        ids += [r["id"] for r in R if r["triggers"].get("spontaneous_replication")]
    elif a.set == "baseline":
        pool = [r["id"] for r in R if r["vec"]["init"] == "RANDOM" and r["vec"]["reproduction"] in Ld.ENDOGENOUS
                and not r["triggers"].get("spontaneous_replication")]
        ids += random.Random(a.seed).sample(pool, a.n)
    tag = a.tag or a.set or "adhoc"
    with mp.Pool(a.workers) as pool:
        rows = pool.map(_one, ids, chunksize=1)
    out = {"tag": tag, "n": len(rows), "definitions": __doc__, "rows": rows}
    p = Ld.write("TRACED_%s.json" % tag, out)
    print(p, len(rows), "diverged", sum(1 for r in rows if r["tracer_diverged"]))


if __name__ == "__main__":
    main()
