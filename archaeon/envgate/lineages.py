"""ENVGATE-01 secondary (descriptive) lineage analysis -- NOT part of the frozen decision. For every established lineage: the frozen
ruler on the founder and on its dominant descendant tapes (did gating persist, shift, broaden, narrow or disappear?), gate availability
per arm, and for founders the ruler calls non-copiers (NOVEL_REPRODUCTIVE_MECHANISM_CANDIDATE) a disassembly and a per-input account.

    python -m archaeon.envgate.lineages
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from archaeon.envgate import mechanism as M
from archaeon.envgate.ruler import measure

HERE = Path(__file__).resolve().parent
OPS = {0: "NOP", 1: "LD r,imm", 2: "LD A,r/r,A", 3: "ADD", 4: "SUB", 5: "INC", 6: "DEC", 7: "XOR", 8: "AND", 9: "OR", 10: "SHL", 11: "SHR", 12: "CMP",
       13: "JP imm", 14: "JR", 15: "JZ", 16: "JNZ", 17: "JC", 18: "LD A,(r)/(r),A", 19: "LD A,(imm)/(imm),A", 20: "COPY", 21: "IN", 22: "OUT", 23: "HALT",
       24: "SWAP", 25: "NEG", 26: "JP r", 27: "DJNZ", 28: "LD A,LEN", 29: "SEAL", 30: "NOP", 31: "HALT"}


def disasm(t: bytes) -> list:
    out = []; i = 0
    while i < len(t):
        b = t[i]; op = b & 31; s = "%02d %02x %-16s r=%s" % (i, b, OPS[op], "ABCD"[(b >> 5) & 3])
        if op in (1, 13, 14, 15, 16, 17, 19, 27) and i + 1 < len(t): s += " imm=%02x" % t[i + 1]; i += 2
        else: i += 1
        out.append(s)
    return out


def gate_change(f: set, d: set) -> str:
    if not f and not d: return "no_exact_gate_either"
    if not d: return "disappeared"
    if not f: return "acquired"
    if f == d: return "retained"
    if f < d: return "broadened"
    if d < f: return "narrowed"
    return "shifted" if not (f & d) else "partially_shifted"


def main(argv=None) -> int:
    res = json.loads((HERE / "RESULTS.json").read_text(encoding="utf-8")); out = []
    for L in res["established_lineages"]:
        t = bytes.fromhex(L["tape"]); fr = measure(t); fg = set(fr.get("exact_inputs", []))
        desc = []
        for th, n in list((L.get("final_tapes") or {}).items())[:5]:
            dr = measure(bytes.fromhex(th)); dg = set(dr.get("exact_inputs", []))
            desc.append({"tape": th, "count": n, "class": dr["class"], "exact_inputs": sorted(dg), "n_birth_inputs": len(dr.get("birth_inputs", [])),
                         "gate_change_vs_founder": gate_change(fg, dg), "gate_available_by_arm": {a: bool(dg & M.alphabet(M.ARMS[a])) for a in M.ARM_ORDER}})
        row = {"block": L["block"], "arm": L["arm"], "arrival": L["arrival"], "founder_tape": L["tape"], "tape_sha": L["tape_sha"], "founder_class": fr["class"],
               "founder_exact_inputs": sorted(fg), "founder_birth_inputs": fr.get("birth_inputs", []), "first_birth_epoch": L["first_birth_epoch"],
               "first_birth_input": L["first_birth_input"], "first_exact_input": L["first_exact_input"], "copy_out_inputs": L["copy_out_inputs"],
               "births": L["births"], "exact_births": L["exact_births"], "exact_fraction": round(L["exact_births"] / L["births"], 4) if L["births"] else None,
               "mean_fid": L["mean_fid"], "peak": L["peak"], "max_gen": L["max_gen"], "persisted_until": L["last_alive"], "removed_epoch": L["removed_epoch"],
               "persistence_after_removal": (L["last_alive"] - L["removed_epoch"]) if L["removed_epoch"] is not None else None,
               "arrival_to_first_birth": L["first_birth_epoch"] - L["epoch_in"] if L.get("epoch_in") is not None else None,
               "lineage_diversity_final": len(L.get("final_tapes") or {}), "dominant_descendants": desc, "traj": L.get("traj")}
        if fr["class"] not in ("EXACT_UNGATED", "EXACT_GATED", "NEAR_COPIER", "SPAN_COPIER"):
            row["label"] = "NOVEL_REPRODUCTIVE_MECHANISM_CANDIDATE"; row["disassembly"] = disasm(t)
        out.append(row)
    summ = {"lineages": len(out), "by_arm": dict(Counter(r["arm"] for r in out)), "founder_class": dict(Counter(r["founder_class"] for r in out)),
            "gate_change_dominant": dict(Counter(d["gate_change_vs_founder"] for r in out for d in r["dominant_descendants"][:1])),
            "novel_candidates": sum(1 for r in out if r.get("label"))}
    (HERE / "LINEAGES.json").write_text(json.dumps({"summary": summ, "lineages": out}, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summ)); return 0


if __name__ == "__main__":
    sys.exit(main())
