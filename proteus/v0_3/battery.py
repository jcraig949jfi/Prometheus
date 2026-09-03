"""The V0.3 neutrality battery: the full coordinate vector, measured without altering the VM.

V0.3 brief section 2 requires an executed-instruction fraction and a fraction of mutations
touching executed code. The VM may not be altered (section 1), and it exposes no instruction
trace. This module therefore carries a SHADOW DECODER that mirrors vm.Player.run_tick exactly
and additionally records which instruction indices were fetched. The shadow is differentially
tested against the authoritative VM on every organism it measures: outputs, status and final
state must match bit for bit, or the measurement aborts. The shadow never feeds a result; it
only observes. Any divergence is a reportable instrument defect, not something to explain away.

No coordinate here is a score. Nothing is thresholded in this module.
"""
from __future__ import annotations

import math
from collections import Counter

from proteus.foundry.affordances import CATEGORIES, CATEGORY, N_OPCODES, OPCODES_IN
from proteus.foundry.prng import SplitMix64
from proteus.foundry.probes import run_ensemble
from proteus.foundry.signatures import classes_present, knockout
from proteus.foundry.vm import MASK32, PERSIST_POLICIES, Player

IW = 4


class ShadowDivergence(RuntimeError):
    """The shadow decoder disagreed with the authoritative VM. Never caught inside this module."""


# ------------------------------------------------------------------ shadow decoder


def _shadow_tick(p: Player, state: dict, inputs: list, n_out: int, rng: SplitMix64, budget: int):
    """Mirror of vm.Player.run_tick that also returns the set of fetched instruction indices.

    Kept line-for-line parallel with vm.py. Any edit to vm.py must be mirrored here or the
    differential check fails, which is the intended tripwire.
    """
    p.begin_tick(state)
    tape = state["tape"]
    regs = state["regs"]
    ip = state["ip"]
    n = p.tape_words
    nr = p.n_regs
    glen = p.genome_len
    writable = p.code_writable
    n_in = len(inputs)
    cursors = [0] * n_in
    outputs = [[] for _ in range(n_out)]
    out_cap = p.out_cap
    cap = p.tick_budget if budget is None else min(budget, p.tick_budget)
    nops = N_OPCODES
    status = "budget"
    ops = 0
    visited = set()
    while ops < cap:
        visited.add(ip // IW if ip % IW == 0 else -1)
        op = tape[ip] % nops
        a = tape[(ip + 1) % n] % nr
        bw = tape[(ip + 2) % n]
        cw = tape[(ip + 3) % n]
        ops += 1
        nip = (ip + 4) % n
        if op == 0:
            pass
        elif op == 1:
            status = "halt"
            ip = 0
            break
        elif op == 2:
            status = "yield"
            ip = nip
            break
        elif op == 3:
            regs[a] = bw & MASK32
        elif op == 4:
            regs[a] = regs[bw % nr]
        elif op == 5:
            regs[a] = tape[regs[bw % nr] % n]
        elif op == 6:
            addr = regs[a] % n
            if addr < glen and not writable:
                pass
            else:
                tape[addr] = regs[bw % nr]
        elif op == 7:
            regs[a] = (regs[bw % nr] + regs[cw % nr]) & MASK32
        elif op == 8:
            regs[a] = (regs[bw % nr] - regs[cw % nr]) & MASK32
        elif op == 9:
            regs[a] = (regs[bw % nr] * regs[cw % nr]) & MASK32
        elif op == 10:
            regs[a] = regs[bw % nr] & regs[cw % nr]
        elif op == 11:
            regs[a] = regs[bw % nr] | regs[cw % nr]
        elif op == 12:
            regs[a] = regs[bw % nr] ^ regs[cw % nr]
        elif op == 13:
            regs[a] = (~regs[bw % nr]) & MASK32
        elif op == 14:
            regs[a] = (regs[bw % nr] << (regs[cw % nr] % 32)) & MASK32
        elif op == 15:
            regs[a] = regs[bw % nr] >> (regs[cw % nr] % 32)
        elif op == 16:
            regs[a] = 1 if regs[bw % nr] == regs[cw % nr] else 0
        elif op == 17:
            regs[a] = 1 if regs[bw % nr] < regs[cw % nr] else 0
        elif op == 18:
            off = bw - (1 << 32) if bw >= (1 << 31) else bw
            nip = (ip + 4 * off) % n
        elif op == 19:
            if regs[a] == 0:
                off = bw - (1 << 32) if bw >= (1 << 31) else bw
                nip = (ip + 4 * off) % n
        elif op == 20:
            if regs[a] != 0:
                off = bw - (1 << 32) if bw >= (1 << 31) else bw
                nip = (ip + 4 * off) % n
        elif op == 21:
            if n_in:
                ch = regs[bw % nr] % n_in
                cur = cursors[ch]
                src = inputs[ch]
                if cur < len(src):
                    regs[a] = src[cur] & MASK32
                    cursors[ch] = cur + 1
                else:
                    regs[a] = 0
            else:
                regs[a] = 0
        elif op == 22:
            if n_in:
                ch = regs[bw % nr] % n_in
                regs[a] = len(inputs[ch]) - cursors[ch]
            else:
                regs[a] = 0
        elif op == 23:
            if n_out:
                ch = regs[bw % nr] % n_out
                dst = outputs[ch]
                if len(dst) < out_cap:
                    dst.append(regs[a])
        elif op == 24:
            regs[a] = rng.next_u32()
        ip = nip
    if status == "budget":
        ip = 0
    state["ip"] = ip
    state["ticks"] += 1
    return outputs, status, visited


def traced_ensemble(manifest: dict, probes: list, cfg: dict):
    """Run the ensemble twice: authoritative VM and shadow. Returns (transcript, visited, statuses).

    Raises ShadowDivergence on any mismatch of outputs, status or final state.
    """
    cap = cfg["budget_cap"]
    p_auth = Player(manifest)
    p_shad = Player(manifest)
    transcript = []
    visited_all = set()
    statuses = []
    for probe in probes:
        s_auth = p_auth.fresh_state()
        s_shad = p_shad.fresh_state()
        r_auth = SplitMix64(probe["rnd_seed"])
        r_shad = SplitMix64(probe["rnd_seed"])
        t = []
        for k in range(probe["ticks"]):
            o_a, st_a = p_auth.run_tick(s_auth, probe["inputs"][k], probe["n_out"], r_auth, None, cap)
            o_s, st_s, vis = _shadow_tick(p_shad, s_shad, probe["inputs"][k], probe["n_out"], r_shad, cap)
            if o_a != o_s or st_a != st_s:
                raise ShadowDivergence(f"probe {probe['index']} tick {k}: outputs/status differ")
            t.append([o_a, st_a])
            visited_all |= vis
            statuses.append(st_a)
        if s_auth != s_shad or r_auth.state != r_shad.state:
            raise ShadowDivergence(f"probe {probe['index']}: final state differs")
        transcript.append(t)
    return transcript, visited_all, statuses


# ------------------------------------------------------------------ genotype coordinates


def opcode_vector(genome: list) -> list:
    c = [0] * N_OPCODES
    for i in range(0, len(genome), IW):
        c[genome[i] % N_OPCODES] += 1
    tot = max(1, len(genome) // IW)
    return [x / tot for x in c]


def class_vector(genome: list) -> list:
    pres = classes_present(genome)
    tot = max(1, sum(pres.values()))
    return [pres[c] / tot for c in CATEGORIES]


def operand_stats(genome: list) -> dict:
    """Distribution of the three operand words per instruction (words 1,2,3 of each group)."""
    ops = []
    for i in range(0, len(genome), IW):
        ops.extend(genome[i + 1:i + IW])
    if not ops:
        return {"mean_norm": None, "frac_low16": None, "top4_hist": [0] * 16, "zero_frac": None}
    hist = [0] * 16
    for w in ops:
        hist[w >> 28] += 1
    return {
        "mean_norm": sum(ops) / len(ops) / 2 ** 32,
        "frac_low16": sum(1 for w in ops if w < (1 << 16)) / len(ops),
        "zero_frac": sum(1 for w in ops if w == 0) / len(ops),
        "top4_hist": [h / len(ops) for h in hist],
    }


def config_vector(m: dict) -> dict:
    return {
        "n_regs": m["n_regs"],
        "log2_tape_words": math.log2(m["tape_words"]),
        "code_writable": 1.0 if m["code_writable"] else 0.0,
        "log2_tick_budget": math.log2(m["tick_budget"]),
        "log2_out_cap": math.log2(m["out_cap"]),
        **{f"persist_{p}": (1.0 if m["persist"] == p else 0.0) for p in PERSIST_POLICIES},
    }


# ------------------------------------------------------------------ mutation-site coordinate

# Which PARENT instruction indices a mutation directly writes, deletes, moves or copies from.
# Declared in the preregistration; insertion is charged its boundary index only.
def touched_parent_instructions(rec: dict) -> set:
    op = rec["operator"]
    a = rec["args"]
    if "noop" in a:
        return set()
    if op == "insertion":
        return {a["pos"]}
    if op == "deletion":
        return set(range(a["pos"], a["pos"] + a["k"]))
    if op == "duplication":
        return set(range(a["src"], a["src"] + a["k"])) | {a["pos"]}
    if op == "movement":
        return set(range(a["src"], a["src"] + a["k"])) | {a["pos"]}
    if op == "replacement":
        return {a["pos"]}
    if op == "operand_perturbation":
        return {a["word"] // IW}
    if op == "reference_redirection":
        return {a["pos"]}
    if op == "region_swap":
        return set(range(a["a"], a["a"] + a["k"])) | set(range(a["b"], a["b"] + a["k"]))
    if op == "splice":
        return set(range(a["pos"], a["pos"] + a["k"]))
    if op == "randomization":
        return set(range(a["pos"], a["pos"] + a["k"]))
    if op == "unreachable_removal":
        return {a["pos"]}
    if op == "config_perturbation":
        return set()
    raise KeyError(op)


# ------------------------------------------------------------------ population measurement


def entropy_bits(counter) -> float:
    tot = sum(counter.values())
    return -sum((c / tot) * math.log2(c / tot) for c in counter.values()) if tot else 0.0


def measure_population(manifests: list, probes: list, cfg: dict, with_knockout: bool = True) -> dict:
    """The full battery on one population under one probe ensemble. No thresholds, no verdict."""
    n = len(manifests)
    lengths, opv, clv, cfgv = [], [], [], []
    op_mean = [0.0] * N_OPCODES
    cl_mean = [0.0] * len(CATEGORIES)
    operand_acc = {"mean_norm": 0.0, "frac_low16": 0.0, "zero_frac": 0.0, "top4_hist": [0.0] * 16}
    cfg_acc = Counter()
    status_ct = Counter()
    seq_ct = Counter()
    tclass = Counter()
    kvec = Counter()
    silent = 0
    exec_fracs = []
    for m in manifests:
        g = m["genome"]
        lengths.append(len(g) // IW)
        v = opcode_vector(g)
        for i, x in enumerate(v):
            op_mean[i] += x / n
        cv = class_vector(g)
        for i, x in enumerate(cv):
            cl_mean[i] += x / n
        os_ = operand_stats(g)
        for k in ("mean_norm", "frac_low16", "zero_frac"):
            operand_acc[k] += (os_[k] or 0.0) / n
        for i, h in enumerate(os_["top4_hist"]):
            operand_acc["top4_hist"][i] += h / n
        for k, val in config_vector(m).items():
            cfg_acc[k] += val / n
        tr, visited, statuses = traced_ensemble(m, probes, cfg)
        ninstr = len(g) // IW
        vis_genome = {i for i in visited if 0 <= i < ninstr}
        exec_fracs.append(len(vis_genome) / max(1, ninstr))
        for s in statuses:
            status_ct[s] += 1
        seq_ct["|".join(statuses)] += 1
        from proteus.foundry.identity import hash_obj
        h = hash_obj(tr)
        tclass[h] += 1
        if all(len(ch) == 0 for probe_t in tr for tick in probe_t for ch in tick[0]):
            silent += 1
        if with_knockout:
            vec = []
            pres = classes_present(g)
            for c in CATEGORIES:
                if pres[c] == 0:
                    vec.append("-")
                    continue
                km = dict(m)
                km["genome"] = knockout(g, c)
                _t2, h2 = run_ensemble(km, probes, cfg)
                vec.append("1" if h2 != h else "0")
            kvec["".join(vec)] += 1
    lengths.sort()
    return {
        "n": n,
        "genome_length": {"mean": sum(lengths) / n, "median": lengths[n // 2],
                          "min": lengths[0], "max": lengths[-1],
                          "var": sum((x - sum(lengths) / n) ** 2 for x in lengths) / n},
        "opcode_frequency": op_mean,
        "opcode_class_frequency": cl_mean,
        "nop_share": op_mean[0],
        "operand_distribution": operand_acc,
        "config_fields": dict(sorted(cfg_acc.items())),
        "status_proportions": {k: status_ct[k] / max(1, sum(status_ct.values()))
                               for k in ("halt", "yield", "budget")},
        "status_sequence_occupancy": {"distinct": len(seq_ct), "top_share": (seq_ct.most_common(1)[0][1] / n) if seq_ct else 0.0,
                                      "entropy_bits": entropy_bits(seq_ct)},
        "executed_instruction_fraction": {"mean": sum(exec_fracs) / n,
                                          "min": min(exec_fracs), "max": max(exec_fracs)},
        "transcript_silence_fraction": silent / n,
        "transcript_occupancy": {"distinct": len(tclass), "top_share": tclass.most_common(1)[0][1] / n,
                                 "entropy_bits": entropy_bits(tclass),
                                 "ceiling_bits": math.log2(n)},
        "knockout_occupancy": ({"distinct": len(kvec), "top_share": kvec.most_common(1)[0][1] / n,
                                "entropy_bits": entropy_bits(kvec)} if with_knockout else None),
        "_transcript_counter": dict(tclass),
        "_knockout_counter": dict(kvec) if with_knockout else None,
    }


COORDINATE_NAMES = (
    "genome_length", "opcode_frequency", "opcode_class_frequency", "operand_distribution",
    "config_fields", "status_proportions", "executed_instruction_fraction",
    "transcript_silence_fraction", "transcript_occupancy", "knockout_occupancy",
    "status_sequence_occupancy", "nop_share", "mutation_touches_executed_fraction",
)
