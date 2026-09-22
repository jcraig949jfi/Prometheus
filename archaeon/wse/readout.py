"""Readout of a WSE campaign: rows -> landscape tables (directive XVI: a landscape, never a
level), seed agreement per (cell, regime), intervention geometry with its ceiling, strategy
switches from the traces, and a timing-free results digest.

    python -m archaeon.wse.readout --campaign wse-survey-v01
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

LEDGERS = Path(__file__).resolve().parent / "ledgers"
TIMING = ("wall_s", "cpu_s")


def strip_timing(o):
    if isinstance(o, dict):
        return {k: strip_timing(v) for k, v in o.items() if k not in TIMING}
    if isinstance(o, list):
        return [strip_timing(x) for x in o]
    return o


def load_rows(campaign: str) -> List[dict]:
    rows = []
    for p in sorted((LEDGERS / campaign / "rows").glob("*.json")):
        rows.append(json.loads(p.read_text(encoding="utf-8")))
    return rows


def results_digest(rows: List[dict]) -> str:
    """sha256 over the sorted, timing-free result blocks: the same campaign on the same code
    reproduces this string (the two 2026-09-16 launches agree on it; RUN.json's first digest
    included wall-clock fields and was not reproducible)."""
    items = sorted(json.dumps(strip_timing(r["result"]), sort_keys=True) for r in rows)
    return hashlib.sha256("\n".join(items).encode()).hexdigest()


def landscape(rows: List[dict]) -> Dict[str, Dict[str, dict]]:
    """cell -> regime -> {classes per seed, held-out rewards, persist policies, ...}"""
    out: Dict[str, Dict[str, dict]] = defaultdict(dict)
    by = defaultdict(list)
    for r in rows:
        by[(r["world"]["name"], r["economics"]["name"])].append(r)
    for (cell, reg), rs in by.items():
        rs.sort(key=lambda z: z["world"]["seed"])
        classes = [z["interpretation"]["class"] for z in rs]
        classes_v012 = [class_v012(z) for z in rs]
        held = [z["result"]["reward_heldout"] for z in rs]
        out[cell][reg] = {
            "seeds": [z["world"]["seed"] for z in rs],
            "classes": classes,
            "classes_v012_property_keyed": classes_v012,
            "agreement": len(set(classes)) == 1,
            "class_if_agreed": classes[0] if len(set(classes)) == 1 else "DISAGREE",
            "reward_heldout": held,
            "reward_heldout_K2x": [z["result"]["reward_heldout_K2x"] for z in rs],
            "reward_heldout_D2x": [z["result"]["reward_heldout_D2x"] for z in rs],
            "floor": rs[0]["interpretation"]["F"],
            "persist": [z["result"]["persist"] for z in rs],
            "ops_per_episode": [round(z["result"]["ops_per_episode"], 1) for z in rs],
            "erase_ceiling": [z["result"].get("erase_ceiling") for z in rs],
            "n_solved": sum(1 for h in held if h >= 0.5),
            "generation_first_solved": [first_solved(z["trace"]) for z in rs],
            "persist_switches": [persist_switches(z["trace"]) for z in rs],
            "intervention_drop": [z["result"]["intervention_drop"] for z in rs],
            "capacity_curve_K": [z["result"]["capacity_curve_K"] for z in rs],
            "fanout_curve": [z["result"]["fanout_curve"] for z in rs],
        }
    return out


def class_v012(r: dict) -> str:
    """ANNOTATION v0.1.2 (2026-09-16, after the v01 rows): the s9 TRIVIAL_RECURRENCE predicate
    keyed on the manifest LABEL persist == "regs"; three register-only solvers with persist=all
    (tape allocated, never load-bearing: ERASE_TAPE 0.0) read UNRESOLVED. The property-keyed
    form below is reported BESIDE the original class, never instead of it: a persistent-state
    solver whose loss under ERASE_REGS >= 0.10 and under ERASE_TAPE < 0.05 is one recurrent
    register store whatever its label says. Everything else keeps the s9 answer."""
    c = r["interpretation"]["class"]
    d = r["result"]["intervention_drop"]
    if c == "UNRESOLVED" and d["ERASE_REGS"] >= 0.10 and d["ERASE_TAPE"] < 0.05:
        return "TRIVIAL_RECURRENCE*"
    return c


def first_solved(trace: List[dict], thr: float = 0.5):
    for t in trace:
        if t["best_reward"] >= thr:
            return t["gen"]
    return None


def persist_switches(trace: List[dict]) -> List[str]:
    """The sequence of elite persist policies with repeats collapsed: a strategy-switch trace."""
    seq = []
    for t in trace:
        if not seq or seq[-1] != t["elite_persist"]:
            seq.append(t["elite_persist"])
    return seq


def table(land: Dict[str, Dict[str, dict]]) -> str:
    order = ["E0", "E1", "E2", "E3"]
    lines = ["%-15s %-3s %-5s %-24s %-20s %-20s %-16s %-16s %s" % ("cell", "reg", "floor", "held-out per seed", "class s9 (3 seeds)", "class v0.1.2 (prop)", "persist", "first-solved gen", "ceiling"),
             "-" * 150]
    for cell in sorted(land, key=_cell_key):
        for reg in order:
            if reg not in land[cell]:
                continue
            d = land[cell][reg]
            v = d["classes_v012_property_keyed"]
            lines.append("%-15s %-3s %.3f %-24s %-20s %-20s %-16s %-16s %s" % (
                cell, reg, d["floor"], " ".join("%.3f" % h for h in d["reward_heldout"]),
                d["class_if_agreed"] if d["agreement"] else "/".join(c[:6] for c in d["classes"]),
                v[0] if len(set(v)) == 1 else "/".join(c[:6] for c in v),
                " ".join(d["persist"]), " ".join(str(g) for g in d["generation_first_solved"]),
                " ".join("%.2f" % c if c is not None else "-" for c in d["erase_ceiling"])))
    return "\n".join(lines)


def geometry(rows: List[dict], min_held: float = 0.5) -> str:
    """Intervention vectors for every elite that solved its cell (held-out >= min_held)."""
    names = ["ERASE_ALL", "ERASE_REGS", "ERASE_TAPE", "SCRAMBLE_LOC", "SCRAMBLE_VAL", "SWAP_TWO", "HALVE_CAP", "RESET_IP", "TRANSPLANT"]
    lines = ["%-15s %-3s s  held  ceil  persist tape regs " % ("cell", "reg") + " ".join("%-9s" % n[:9] for n in names) + " K-curve(1,2,4,8,16)",
             "-" * 170]
    for r in sorted(rows, key=lambda z: (_cell_key(z["world"]["name"]), z["economics"]["name"], z["world"]["seed"])):
        res = r["result"]
        if res["reward_heldout"] < min_held:
            continue
        d = res["intervention_drop"]
        cap = res.get("capacity_curve_K") or {}
        capstr = " ".join("%.2f" % cap[k] for k in sorted(cap, key=int)) if cap else "-"
        lines.append("%-15s %-3s %d  %.3f %.2f  %-7s %-4d %-4d " % (
            r["world"]["name"], r["economics"]["name"], r["world"]["seed"], res["reward_heldout"], res.get("erase_ceiling") or 0,
            res["persist"], res["tape_words"], res["n_regs"]) + " ".join("%-9.3f" % d[n] for n in names) + " " + capstr)
    return "\n".join(lines)


def _cell_key(name: str):
    w = name.split("_")[0]
    return (int(w[1:]), name)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", default="wse-survey-v01")
    a = ap.parse_args(argv)
    rows = load_rows(a.campaign)
    land = landscape(rows)
    out = LEDGERS / a.campaign
    (out / "LANDSCAPE.json").write_text(json.dumps(land, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    txt = "rows: %d   results_digest (timing-free): %s\n\n" % (len(rows), results_digest(rows)) + table(land) + "\n\nINTERVENTION GEOMETRY (elites with held-out >= 0.5; drop = reward lost)\n" + geometry(rows) + "\n"
    (out / "LANDSCAPE.txt").write_text(txt, encoding="utf-8", newline="\n")
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())


def disasm(manifest: dict) -> List[str]:
    """Mnemonic listing of a genome (for reading an elite; never for classifying it)."""
    from proteus.foundry.affordances import MNEMONIC, N_OPCODES
    g = manifest["genome"]
    nr = manifest["n_regs"]
    out = []
    for i in range(0, len(g), 4):
        op = g[i] % N_OPCODES
        a, b, c = g[i + 1] % nr, g[i + 2], g[i + 3]
        name = MNEMONIC[op]
        if name in ("JMP", "JZ", "JNZ"):
            off = b - (1 << 32) if b >= (1 << 31) else b
            out.append("%3d %-5s r%d %+d" % (i // 4, name, a, off) if name != "JMP" else "%3d %-5s %+d" % (i // 4, name, off))
        elif name == "LDC":
            out.append("%3d %-5s r%d %d" % (i // 4, name, a, b))
        else:
            out.append("%3d %-5s r%d r%d r%d" % (i // 4, name, a, b % nr, c % nr))
    return out
