"""Measure the ACTUAL mutational topology of a genotype, never its semantic task difficulty.

For a tape, sample single-byte substitutions and evaluate each neighbour in ISOLATION (own tape, an empty neighbour
window, fresh inputs): does it still replicate (writes the window as the reproduction physics requires), does it
score higher / the same / lower on the current task, and does it score on the matched HARDER task (the next rung of
the task family)? The densities are the response geometry of that genotype: beneficial-neighbour density, neutral
fraction, replication-lethal fraction, and moat density (neighbours that already touch the next task).

Damage cliffs: k random byte damages (k = 1, 2, 4, 8, 16), the fraction of damaged copies that still replicate / still
solve -- the Atlas "damage cliff" and "length-mediated robustness" rulers on this substrate.

Everything is seeded and bounded (a few hundred VM executions per specimen)."""
from __future__ import annotations

import random
from typing import Dict, List, Optional

from prometheus.z80atlas import vm
from prometheus.z80atlas.tasks import Task, score as task_score
from prometheus.z80atlas.world import Config

NEXT_TASK = {"ECHO": "INC", "INC": "COND_ONE", "COND_ONE": "COND_MULTI", "CONST": "ECHO", "SUM2": None, "COND_MULTI": None}


# rep_rule (2026-10-06, DEF-BEL-010 from Nestor #1207): how `replicates` scores fidelity.
#   "v1"      historical: the child window is compared with the tape at ALL L positions. The window starts as zero memory and
#             a short tape is zero-padded, so untouched zero bytes count as copied; with need = 1 (ENDOGENOUS_PARTIAL) a single
#             written byte can score `replicates` (and with need = L//2 the unwritten half can carry the rest). Kept as the
#             default so every historical geometry.json reproduces.
#   "written" a position counts only if it was WRITTEN in this execution with material whose pre-execution origin is the
#             SAME tape position (vm Trace.win_origin, multi-hop) and equals the tape; an unwritten position, a byte
#             constructed in place, or a copy of other memory (e.g. a sweep of scratch zeros over the window -- review A,
#             2026-10-08) is a mismatch.
REP_RULES = ("v1", "written")


def _eval(tape: bytes, cfg: Config, task: Task, rng: random.Random, n_inputs: int = 3, rep_rule: str = "v1") -> Dict:
    if rep_rule not in REP_RULES:
        raise ValueError("unknown rep_rule %r" % rep_rule)
    L = cfg.L; scores = []; rep = 0
    tape = bytes(tape[:L]) + bytes(max(0, L - len(tape)))   # a short witness is zero-padded: slice-assigning fewer bytes would SHRINK the memory
    for _ in range(n_inputs):
        mem = bytearray(256); mem[:L] = tape
        inputs = task.inputs(rng)
        for k, v in enumerate(inputs):
            mem[vm.IN_BASE + k] = v
        if cfg.layout == "SEPARATED":
            tr = vm.execute(mem, L, 0, cfg.budget // 2, inputs, region=(0, L // 2), allow_copyall=cfg.allow_copyall)
            tr2 = vm.execute(mem, L, L // 2, cfg.budget // 2, inputs, region=(L // 2, L), allow_copyall=cfg.allow_copyall, origin=tr.origin)
            outs = tr.outputs + tr2.outputs; fi = tr.first_in_step if tr.first_in_step is not None else tr2.first_in_step
            fo = tr.first_out_step if tr.first_out_step is not None else tr2.first_out_step
            written = {a for a in list(tr.writes) + list(tr2.writes) if L <= a < 2 * L}
            origin = tr2.origin
        else:
            tr = vm.execute(mem, L, 0, cfg.budget, inputs, allow_copyall=cfg.allow_copyall)
            outs = tr.outputs; fi = tr.first_in_step; fo = tr.first_out_step
            written = {a for a in tr.writes if L <= a < 2 * L}
            origin = tr.origin
        need = {"ENDOGENOUS_COPY": L, "ENDOGENOUS_PARTIAL": 1, "OVERWRITE": L // 2, "CONSTRUCTIVE": L // 2, "PAIR_EXECUTION": L // 2}.get(cfg.reproduction, L // 2)
        if len(written) >= need:
            child = bytes(mem[L:2 * L])
            if rep_rule == "written":
                fid = sum(1 for a in written if origin.get(a, a) == a - L and child[a - L] == tape[a - L]) / L
            else:
                fid = 1.0 - sum(1 for x, y in zip(child, tape[:L]) if x != y) / L
            if fid >= 0.9:
                rep += 1
        scores.append(task_score(task, outs, task.expected(inputs), "ATOMIC" if cfg.scoring == "NEUTRAL" else cfg.scoring, cfg.read_gate, fo, fi))
    return {"score": sum(scores) / len(scores), "replicates": rep == n_inputs}


def _pad(tape: bytes, L: int) -> bytes:
    return bytes(tape[:L]) + bytes(max(0, L - len(tape)))


def scan(tape: bytes, cfg: Config, task: Task, seed: int, n: int = 48, rep_rule: str = "v1") -> Dict:
    rng = random.Random(seed)
    L = cfg.L; tape = _pad(tape, L)
    base = _eval(tape, cfg, task, rng, rep_rule=rep_rule)
    nxt = Task(NEXT_TASK[task.kind], k=task.k) if NEXT_TASK.get(task.kind) else None
    base_next = _eval(tape, cfg, nxt, rng, rep_rule=rep_rule)["score"] if nxt else None
    better = same = worse = lethal = 0; moat = 0
    for _ in range(n):
        t = bytearray(tape[:L]); p = rng.randrange(L); t[p] = (t[p] + rng.randrange(1, 256)) & 0xFF
        e = _eval(bytes(t), cfg, task, rng, rep_rule=rep_rule)
        if base["replicates"] and not e["replicates"]:
            lethal += 1
        if e["score"] > base["score"] + 1e-9:
            better += 1
        elif abs(e["score"] - base["score"]) < 1e-9:
            same += 1
        else:
            worse += 1
        if nxt is not None:
            en = _eval(bytes(t), cfg, nxt, rng, rep_rule=rep_rule)["score"]
            if en > (base_next or 0.0) + 1e-9:
                moat += 1
    out = {"n": n, "base_score": round(base["score"], 3), "base_replicates": base["replicates"],
            "beneficial_density": round(better / n, 3), "neutral_fraction": round(same / n, 3), "deleterious_fraction": round(worse / n, 3),
            "replication_lethal_fraction": round(lethal / n, 3) if base["replicates"] else None,
            "next_task": nxt.kind if nxt else None, "base_next_score": None if base_next is None else round(base_next, 3),
            "moat_density": round(moat / n, 3) if nxt else None}
    if rep_rule != "v1":
        out["rep_rule"] = rep_rule                     # recorded only off the default, so historical outputs are unchanged
    return out


def damage_cliff(tape: bytes, cfg: Config, task: Task, seed: int, trials: int = 12, rep_rule: str = "v1") -> Dict:
    rng = random.Random(seed); L = cfg.L; tape = _pad(tape, L)
    out = {}
    base = _eval(tape, cfg, task, rng, rep_rule=rep_rule)
    for k in (1, 2, 4, 8, 16):
        rep = solve = 0
        for _ in range(trials):
            t = bytearray(tape[:L])
            for p in rng.sample(range(L), min(k, L)):
                t[p] = rng.randrange(256)
            e = _eval(bytes(t), cfg, task, rng, rep_rule=rep_rule)
            rep += e["replicates"]; solve += e["score"] >= 0.999
        out["k%d" % k] = {"replicates": round(rep / trials, 3), "solves": round(solve / trials, 3)}
    res = {"base_replicates": base["replicates"], "base_solves": base["score"] >= 0.999, "cliff": out}
    if rep_rule != "v1":
        res["rep_rule"] = rep_rule
    return res


# ---- paired geometry (added 2026-09-23, forensics C6/M9) -----------------------------------------------------------------
# scan() above scores the base on 3 fresh inputs and every mutant on 3 OTHER fresh inputs: an identical 'mutant' of an
# input-dependent partial solver is scored 'better' up to 90% of the time, and the campaign's beneficial-density gain
# was that noise (receipts/GEOM_AUDIT_*.json). scan_paired() scores the base and every mutant on ONE fixed input panel
# (common random numbers), over a fixed mutant set (every position x DELTAS), on the task it is given (the caller
# passes the CONFIGURED task, never an easier niche task), and reports the identity-mutant false-beneficial rate as
# its own self-check (0 by construction; a non-zero value means the evaluation is not a function of the tape).
DELTAS = (1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 128, 144, 170, 200, 233, 255)


def _panel_score(t: bytes, cfg: Config, task: Task, panel) -> float:
    L = cfg.L; sc = "ATOMIC" if cfg.scoring == "NEUTRAL" else cfg.scoring
    tot = 0.0
    for inputs in panel:
        mem = bytearray(256); mem[:L] = t
        for k, v in enumerate(inputs):
            mem[vm.IN_BASE + k] = v
        if cfg.layout == "SEPARATED":
            tr = vm.execute(mem, L, 0, cfg.budget // 2, inputs, region=(0, L // 2), allow_copyall=cfg.allow_copyall)
            tr2 = vm.execute(mem, L, L // 2, cfg.budget // 2, inputs, region=(L // 2, L), allow_copyall=cfg.allow_copyall)
            outs = tr.outputs + tr2.outputs
            fi = tr.first_in_step if tr.first_in_step is not None else tr2.first_in_step
            fo = tr.first_out_step if tr.first_out_step is not None else tr2.first_out_step
        else:
            tr = vm.execute(mem, L, 0, cfg.budget, inputs, allow_copyall=cfg.allow_copyall)
            outs, fi, fo = tr.outputs, tr.first_in_step, tr.first_out_step
        tot += task_score(task, outs, task.expected(inputs), sc, cfg.read_gate, fo, fi)
    return tot / len(panel)


def scan_paired(tape: bytes, cfg: Config, task: Task, seed: int, n_panel: int = 8, deltas=DELTAS) -> Dict:
    L = cfg.L; tape = _pad(tape, L)
    rng = random.Random(seed)
    panel = [task.inputs(rng) for _ in range(n_panel)]
    b = _panel_score(tape, cfg, task, panel)
    null_better = int(_panel_score(tape, cfg, task, panel) > b + 1e-9)
    better = same = worse = 0
    for p in range(L):
        for d in deltas:
            t = bytearray(tape); t[p] = (t[p] + d) & 0xFF
            s = _panel_score(bytes(t), cfg, task, panel)
            if s > b + 1e-9:
                better += 1
            elif abs(s - b) < 1e-9:
                same += 1
            else:
                worse += 1
    n = L * len(deltas)
    return {"n": n, "panel": n_panel, "task": task.to_dict(), "base_score": round(b, 4),
            "beneficial_density": round(better / n, 4), "neutral_fraction": round(same / n, 4), "deleterious_fraction": round(worse / n, 4),
            "null_false_beneficial": float(null_better)}


# ---- operator-aware reachability (added 2026-10-10, BEL-RD-72 Workstream A) ---------------------------------------------
# geometry.scan / scan_paired count only single-byte SUBSTITUTION neighbours. The physics also varies tapes by moving
# segments (copying with offsets, partial overwrites), by structural insertion/deletion, and by importing a partner's
# segment (uptake / assembly). A state that is far under substitution can be one step away under another operator
# (BEL-48H: a fragment 0/16,320 substitutions but 8/50,512 segment moves from a replicator). These functions are new and
# pure; nothing above them changed, so every historical geometry output is untouched.
OPERATORS = ("SUB", "MOVE", "INS", "DEL", "DONOR")


def operator_neighbours(tape: bytes, op: str, L: int, donors=(), max_seg: int = 16):
    """yield every one-step neighbour of `tape` under operator `op`.
    SUB   t[p] = v (v != t[p])                          L * 255
    MOVE  copy t[s:s+n] over t[d:d+n], d != s, n <= max_seg (self segment copy / overwrite)
    INS   insert byte v at p, shifting right, the last byte drops (structural insertion)
    DEL   delete byte p, shifting left, pad with 0 (structural deletion)
    DONOR copy donor[s:s+n] over t[d:d+n] for each donor (uptake / partial overwrite by another tape)"""
    t = bytes(tape[:L]) + bytes(max(0, L - len(tape)))
    if op == "SUB":
        for p in range(L):
            for v in range(256):
                if v != t[p]:
                    yield t[:p] + bytes([v]) + t[p + 1:]
    elif op == "MOVE":
        for s in range(L):
            for n in range(1, max_seg + 1):
                if s + n > L:
                    break
                for d in range(L - n + 1):
                    if d != s:
                        yield t[:d] + t[s:s + n] + t[d + n:]
    elif op == "INS":
        for p in range(L):
            for v in range(256):
                yield t[:p] + bytes([v]) + t[p:L - 1]
    elif op == "DEL":
        for p in range(L):
            yield t[:p] + t[p + 1:] + b"\x00"
    elif op == "DONOR":
        for dn in donors:
            dn = bytes(dn[:L]) + bytes(max(0, L - len(dn)))
            for s in range(L):
                for n in range(1, max_seg + 1):
                    if s + n > L:
                        break
                    for d in range(L - n + 1):
                        yield t[:d] + dn[s:s + n] + t[d + n:]
    else:
        raise ValueError("unknown operator %r" % op)


def scan_operators(tape: bytes, L: int, predicate, ops=OPERATORS, donors=(), max_seg: int = 16) -> dict:
    """one-step reachability per operator: {op: {"routes": k, "neighbours": n}} where routes = neighbours satisfying
    `predicate(tape_bytes) -> bool`. The predicate is the caller's (e.g. FUNC and task-competent)."""
    out = {}
    for op in ops:
        if op == "DONOR" and not donors:
            continue
        k = n = 0
        for u in operator_neighbours(tape, op, L, donors, max_seg):
            n += 1
            k += bool(predicate(u))
        out[op] = {"routes": k, "neighbours": n}
    return out


def scan_moves(tape: bytes, L: int, predicate, max_seg: int = 16) -> dict:
    """the substitution vs segment-move comparison (BEL-48H NEXT_EXPERIMENTS #13)."""
    return scan_operators(tape, L, predicate, ops=("SUB", "MOVE"), max_seg=max_seg)


def sample_paths(tape: bytes, L: int, predicate, ops=("SUB", "MOVE", "INS", "DEL"), depth: int = 3, n: int = 2000, seed: int = 0,
                 donors=(), max_seg: int = 16) -> dict:
    """multi-step GEOMETRIC reachability estimate: n random operator sequences of length `depth` (each step: an operator
    drawn uniformly from `ops`, then a uniform random neighbour under it); returns the fraction that satisfy the predicate
    at ANY step, per depth reached first. Geometric, not dynamical: no selection, no population."""
    import random as _r
    rng = _r.Random(seed)
    t0 = bytes(tape[:L]) + bytes(max(0, L - len(tape)))
    first = [0] * (depth + 1)
    for _ in range(n):
        t = t0
        for step in range(1, depth + 1):
            op = rng.choice([o for o in ops if o != "DONOR" or donors])
            t = _random_neighbour(t, op, L, rng, donors, max_seg)
            if predicate(t):
                first[step] += 1
                break
    return {"n": n, "depth": depth, "first_hit_at_depth": first[1:], "reached": sum(first), "fraction": round(sum(first) / n, 6)}


def _random_neighbour(t: bytes, op: str, L: int, rng, donors=(), max_seg: int = 16) -> bytes:
    if op == "SUB":
        p = rng.randrange(L); v = rng.randrange(255); v = v if v < t[p] else v + 1
        return t[:p] + bytes([v]) + t[p + 1:]
    if op == "INS":
        p = rng.randrange(L); return t[:p] + bytes([rng.randrange(256)]) + t[p:L - 1]
    if op == "DEL":
        p = rng.randrange(L); return t[:p] + t[p + 1:] + b"\x00"
    if op == "MOVE":
        src = t
    else:
        dn = bytes(rng.choice(list(donors))); src = dn[:L] + bytes(max(0, L - len(dn)))
    n = rng.randint(1, max_seg); s = rng.randrange(L - n + 1); d = rng.randrange(L - n + 1)
    return t[:d] + src[s:s + n] + t[d + n:]
