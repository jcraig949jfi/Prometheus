"""Round 2 L0 anatomy (PROTEUS-37): STRUCTURE of Archaeon's specimens, ablation SETS for Archaeon.

Input (Archaeon's, read-only): archaeon/campaign4/SPECIMENS_FOR_PROTEUS.json -- 11 delay-general
readers, 15 matched W0 solvers, 23 shelf organisms, all under runtime 73f110e2 / grammar v0.4 /
regime instr1-16:6528b9dc. The file also carries Archaeon's held-out measurements; this module
NEVER reads them (grep: no key of the form heldout_* is touched). Labels (delay_general /
w0_solver / shelf) are Archaeon's strata and are used only to group.

What Proteus computes, per organism, all STATIC (no execution, no world):
    structural descriptor (proteus.structural_descriptor.v1), the statically reachable
    instruction set from ip=0 (grammar.static_reachable), the mnemonic program over reachable
    instructions, register read/write census, channel-op presence (IN/INQ/OUT), branch presence,
    tape-memory presence (LD/ST), a category-bigram motif census over the reachable program in
    address order, and an ABLATION SET: one manifest per reachable instruction with that
    instruction replaced by NOP, plus one manifest with persist set to "none" (the state-use
    knockout). Archaeon lesions those on the delay family; Proteus does not.

Separation: for every numeric structural statistic, readers vs W0 solvers (the operator's
question) and the other two pairs, with the difference in means and a RE-LABELLING chance floor
(20,000 label permutations under SplitMix64(20260921)): the fraction of relabellings whose
|difference| >= the observed one. Many statistics are tested; the count is printed beside them
and no single p is read as a finding. The output is a table with its floor, not a verdict.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from proteus.eval.population_manifest import structural_descriptor  # noqa: E402
from proteus.foundry.affordances import CATEGORY, N_OPCODES, TABLE  # noqa: E402
from proteus.foundry.grammar import static_reachable  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH, hash_obj  # noqa: E402
from proteus.foundry.prng import SplitMix64  # noqa: E402
from proteus.foundry.vm import validate_manifest  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPECIMENS = os.path.join(ROOT, "archaeon", "campaign4", "SPECIMENS_FOR_PROTEUS.json")
OUT_DIR = os.path.join(ROOT, "proteus", "round2")
RESULT = os.path.join(OUT_DIR, "ANATOMY_L0_RESULT.json")
ABLATION = os.path.join(OUT_DIR, "ANATOMY_L0_ABLATION_SETS.json")
SUMMARY = os.path.join(OUT_DIR, "ANATOMY_L0.md")

MNEMONIC = {row[0]: row[1] for row in TABLE}
N_PERM = 20000
PERM_SEED = 20260921
GROUPS = ("delay_general", "w0_solver", "shelf")
FORBIDDEN_PREFIX = "heldout"

# operand roles per opcode, from vm.py (the authority): which slots are register READS / WRITES
_W_A = {3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 21, 22, 24}      # r[a] written
_R_A = {6, 19, 20, 23}                                                       # r[a] read
_R_B = {4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 21, 22, 23}       # r[b] read
_R_C = {7, 8, 9, 10, 11, 12, 14, 15, 16, 17}                                 # r[c] read
CHANNEL_OPS = {21, 22, 23}
BRANCH_OPS = {18, 19, 20}
TAPE_OPS = {5, 6}
HALT_OPS = {1, 2}


def decode(genome: list, n_regs: int) -> list:
    out = []
    for i in range(len(genome) // 4):
        w = genome[4 * i: 4 * i + 4]
        out.append({"i": i, "op": w[0] % N_OPCODES, "a": w[1] % n_regs, "b": w[2], "c": w[3]})
    return out


def structure(manifest: dict) -> dict:
    validate_manifest(manifest)
    nr = manifest["n_regs"]
    ins = decode(manifest["genome"], nr)
    reach = sorted(static_reachable(manifest["genome"], manifest["tape_words"]))
    rset = set(reach)
    prog = [ins[i] for i in reach]
    mnemonics = [MNEMONIC[x["op"]] for x in prog]
    cats = [CATEGORY[x["op"]] for x in prog]
    reads, writes = set(), set()
    for x in prog:
        op = x["op"]
        if op in _W_A:
            writes.add(x["a"])
        if op in _R_A:
            reads.add(x["a"])
        if op in _R_B:
            reads.add(x["b"] % nr)
        if op in _R_C:
            reads.add(x["c"] % nr)
    bigrams = Counter("%s>%s" % (cats[k], cats[k + 1]) for k in range(len(cats) - 1))
    reach_cats = Counter(cats)
    d = structural_descriptor(manifest)
    n_instr = d["genome_instructions"]
    return {
        "descriptor": d,
        "reachable_indices": reach,
        "reachable_count": len(reach),
        "reachable_fraction": (len(reach) / n_instr) if n_instr else 0.0,
        "program_reachable": mnemonics,
        "reachable_category_counts": dict(sorted(reach_cats.items())),
        "reachable_distinct_opcodes": len({x["op"] for x in prog}),
        "registers_read": sorted(reads),
        "registers_written": sorted(writes),
        "registers_used_count": len(reads | writes),
        "registers_read_only": sorted(reads - writes),
        "registers_written_only": sorted(writes - reads),
        "has_channel_op": any(x["op"] in CHANNEL_OPS for x in prog),
        "has_INQ": any(x["op"] == 22 for x in prog),
        "has_IN": any(x["op"] == 21 for x in prog),
        "has_OUT": any(x["op"] == 23 for x in prog),
        "has_branch": any(x["op"] in BRANCH_OPS for x in prog),
        "has_conditional_branch": any(x["op"] in (19, 20) for x in prog),
        "has_tape_memory": any(x["op"] in TAPE_OPS for x in prog),
        "has_halt_or_yield_reachable": any(x["op"] in HALT_OPS for x in prog),
        "has_RND": any(x["op"] == 24 for x in prog),
        "category_bigrams_reachable": dict(sorted(bigrams.items())),
        "_unreachable_indices": sorted(set(range(n_instr)) - rset),
    }


def ablation_set(organism_id: str, manifest: dict, reach: list) -> dict:
    """Per reachable instruction: that instruction -> NOP 0 0 0. Plus persist -> none."""
    knockouts = []
    for i in reach:
        m = json.loads(json.dumps(manifest))
        m["genome"][4 * i: 4 * i + 4] = [0, 0, 0, 0]
        validate_manifest(m)
        knockouts.append({"kind": "instruction_nop", "instruction": i, "organism_id": hash_obj(m), "manifest": m})
    if manifest["persist"] != "none":
        m = dict(manifest, persist="none")
        validate_manifest(m)
        knockouts.append({"kind": "persist_none", "instruction": None, "organism_id": hash_obj(m), "manifest": m})
    return {"parent_organism_id": organism_id, "runtime_hash": RUNTIME_HASH, "n": len(knockouts),
            "knockouts": knockouts}


# ------------------------------------------------------------------ statistics
def numeric_stats(s: dict) -> dict:
    d = s["descriptor"]
    shares = {c: s["reachable_category_counts"].get(c, 0) / max(1, s["reachable_count"])
              for c in sorted({CATEGORY[k] for k in range(N_OPCODES)})}
    out = {
        "genome_instructions": d["genome_instructions"],
        "reachable_count": s["reachable_count"],
        "reachable_fraction": s["reachable_fraction"],
        "reachable_distinct_opcodes": s["reachable_distinct_opcodes"],
        "n_regs": d["n_regs"],
        "registers_used_count": s["registers_used_count"],
        "tape_words": d["tape_words"],
        "tick_budget": d["tick_budget"],
        "persist_regs_or_all": 1.0 if d["persist"] in ("regs", "all") else 0.0,
        "persist_tape_or_all": 1.0 if d["persist"] in ("tape", "all") else 0.0,
        "code_writable": 1.0 if d["code_writable"] else 0.0,
        "has_INQ": 1.0 if s["has_INQ"] else 0.0,
        "has_conditional_branch": 1.0 if s["has_conditional_branch"] else 0.0,
        "has_tape_memory": 1.0 if s["has_tape_memory"] else 0.0,
        "has_RND": 1.0 if s["has_RND"] else 0.0,
    }
    out.update({"reachable_share_" + c: v for c, v in shares.items()})
    return out


def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def separation(stats_a: list, stats_b: list, rng: SplitMix64, n_perm: int = N_PERM) -> dict:
    keys = sorted(stats_a[0].keys())
    pooled = stats_a + stats_b
    na = len(stats_a)
    rows = {}
    for k in keys:
        xa, xb = [s[k] for s in stats_a], [s[k] for s in stats_b]
        obs = _mean(xa) - _mean(xb)
        vals = [s[k] for s in pooled]
        if len(set(vals)) == 1:
            rows[k] = {"mean_a": _mean(xa), "mean_b": _mean(xb), "diff": 0.0, "floor_p": 1.0, "note": "constant"}
            continue
        hits = 0
        idx = list(range(len(vals)))
        for _ in range(n_perm):
            # Fisher-Yates under the seat's PRNG (no `random`)
            for j in range(len(idx) - 1, 0, -1):
                r = rng.randbelow(j + 1)
                idx[j], idx[r] = idx[r], idx[j]
            pa = [vals[i] for i in idx[:na]]
            pb = [vals[i] for i in idx[na:]]
            if abs(_mean(pa) - _mean(pb)) >= abs(obs) - 1e-12:
                hits += 1
        rows[k] = {"mean_a": _mean(xa), "mean_b": _mean(xb), "diff": obs, "floor_p": hits / n_perm}
    return rows


# ------------------------------------------------------------------ main
def load_specimens(path=SPECIMENS) -> dict:
    doc = json.load(open(path, encoding="utf-8"))
    for g in GROUPS:
        for e in doc["specimens"][g]:
            for k in list(e.keys()):
                if k.startswith(FORBIDDEN_PREFIX):
                    del e[k]                      # behavioural columns are Archaeon's; never read here
    return doc


def run(doc: dict, n_perm: int = N_PERM) -> tuple:
    per = {g: [] for g in GROUPS}
    abl = {g: [] for g in GROUPS}
    for g in GROUPS:
        for e in doc["specimens"][g]:
            m = e["manifest"]
            if hash_obj(m) != e["organism_id"]:
                raise ValueError("organism_id does not hash from its manifest: " + e["organism_id"][:12])
            s = structure(m)
            per[g].append({"organism_id": e["organism_id"], "provenance": e.get("provenance"), **s,
                           "stats": numeric_stats(s)})
            abl[g].append(ablation_set(e["organism_id"], m, s["reachable_indices"]))
    rng = SplitMix64(PERM_SEED)
    pairs = {}
    for a, b in (("delay_general", "w0_solver"), ("delay_general", "shelf"), ("w0_solver", "shelf")):
        pairs["%s_vs_%s" % (a, b)] = separation([x["stats"] for x in per[a]], [x["stats"] for x in per[b]], rng, n_perm)
    n_stats = len(next(iter(pairs.values())))
    result = {
        "schema_version": "proteus.anatomy_l0.v1",
        "runtime_hash": RUNTIME_HASH,
        "input": {"path": "archaeon/campaign4/SPECIMENS_FOR_PROTEUS.json", "identity": doc["identity"],
                  "counts": {g: len(per[g]) for g in GROUPS}, "behavioural_columns_read": 0},
        "permutation": {"n": n_perm, "seed": PERM_SEED, "statistics_tested_per_pair": n_stats,
                        "note": "many statistics; floor_p is per statistic and uncorrected; read the table, not one cell"},
        "per_organism": per,
        "separation": pairs,
        "group_programs": {g: [" ".join(x["program_reachable"]) for x in per[g]] for g in GROUPS},
        "what_this_does_not_establish": [
            "which structure CAUSES delay invariance (Archaeon lesions the ablation sets on the delay family)",
            "anything from Archaeon's held-out columns (not read)",
            "that any statistic below its floor is a finding: %d statistics x 3 pairs were tested" % n_stats,
        ],
    }
    return result, {"schema_version": "proteus.anatomy_l0_ablation.v1", "runtime_hash": RUNTIME_HASH, "sets": abl}


def render(result: dict) -> str:
    L = ["# Round 2 L0 anatomy -- STRUCTURE of Archaeon's specimens (PROTEUS-37)", "",
         "Input archaeon/campaign4/SPECIMENS_FOR_PROTEUS.json; counts %s; behavioural columns read: 0."
         % json.dumps(result["input"]["counts"]),
         "Permutation floor: %d relabellings, seed %d, %d statistics per pair, UNCORRECTED."
         % (result["permutation"]["n"], result["permutation"]["seed"], result["permutation"]["statistics_tested_per_pair"]), ""]
    for pair, rows in result["separation"].items():
        a, b = pair.split("_vs_")
        L.append("## %s vs %s" % (a, b))
        L.append("")
        L.append("    %-34s %9s %9s %9s %8s" % ("statistic", "mean_" + a[:5], "mean_" + b[:5], "diff", "floor_p"))
        for k, r in sorted(rows.items(), key=lambda kv: kv[1]["floor_p"]):
            L.append("    %-34s %9.3f %9.3f %9.3f %8.4f %s" % (k, r["mean_a"], r["mean_b"], r["diff"], r["floor_p"],
                                                             r.get("note", "")))
        L.append("")
    L.append("## Reachable programs (address order), by stratum")
    L.append("")
    for g, progs in result["group_programs"].items():
        L.append("### " + g)
        for i, p in enumerate(progs):
            L.append("    %2d  %s" % (i, p))
        L.append("")
    L.append("## Not established")
    for s in result["what_this_does_not_establish"]:
        L.append("- " + s)
    return "\n".join(L) + "\n"


def main() -> int:
    from proteus.workspace import assert_not_canonical
    assert_not_canonical("run anatomy.py")
    os.makedirs(OUT_DIR, exist_ok=True)
    doc = load_specimens()
    result, abl = run(doc)
    for path, obj in ((RESULT, result), (ABLATION, abl)):
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(obj, f, indent=1, sort_keys=True)
            f.write("\n")
    with open(SUMMARY, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(result))
    print(RESULT); print(ABLATION); print(SUMMARY)
    dw = result["separation"]["delay_general_vs_w0_solver"]
    print("delay_general vs w0_solver, statistics with floor_p < 0.05 (uncorrected, of %d):" % len(dw))
    for k, r in sorted(dw.items(), key=lambda kv: kv[1]["floor_p"]):
        if r["floor_p"] < 0.05:
            print("   %-34s %.3f vs %.3f  diff %+.3f  p=%.4f" % (k, r["mean_a"], r["mean_b"], r["diff"], r["floor_p"]))
    print("ablation sets:", {g: sum(a["n"] for a in abl["sets"][g]) for g in GROUPS})
    return 0


if __name__ == "__main__":
    sys.exit(main())
