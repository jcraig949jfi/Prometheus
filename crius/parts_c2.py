"""Campaign 2 PARTS diagnostic (DESIGN_C2 s5): frozen partial mechanisms, never population members.

Each partial is the compact enumerator P_BASE plus one link of the reuse
chain. selective value = paired-stream fitness(part) - fitness(ancestor)
on the gate streams (controls only); transplant value = the same with the
store pre-loaded from the rung's positive control; structural distance =
instruction-level edit distance.

CLI: python -m crius.parts_c2 --config crius/configs/c2c.json [--out crius/runs/parts_c2c]
"""

from __future__ import annotations

import argparse
import os
import time

from . import evaluate, receipts, streams, vm
from .artifacts import BlockStore
from .player import VMPlayer, run_task
from .workspace import Workspace

# ---------------------------------------------------------------- sources (assembler syntax; R1 = num_ops = RESET)

P_BASE_SRC = """
; compact enumerator: every length-3 action sequence, d0 fastest; success may occur at any prefix
    INPUT R1, num_ops
    CONST R5, 1
    CONST R0, 0
    MUL   R2, R1, R1
    MUL   R2, R2, R1
L:
    LT    R3, R0, R2
    BRZ   R3, END
    ACT   R1
    MOD   R3, R0, R1
    ACT   R3
    DIV   R4, R0, R1
    MOD   R3, R4, R1
    ACT   R3
    DIV   R4, R4, R1
    MOD   R3, R4, R1
    ACT   R3
    ADD   R0, R0, R5
    JMP   L
END:
    HALT
"""

# rung A: calibrator only -- probes each action once and stores the observed delta in cells 100+k; never used
P_CAL_SRC = """
    INPUT R1, num_ops
    CONST R5, 1
    CONST R7, 100
    WS_READ R6, R7
    BRNZ  R6, ENUM
    CONST R0, 0
C:
    LT    R3, R0, R1
    BRZ   R3, MARK
    ACT   R1
    ACT   R0
    INPUT R6, last_delta
    ADD   R3, R7, R0
    WS_WRITE R3, R6
    ADD   R0, R0, R5
    JMP   C
MARK:
    CONST R6, 1
    CONST R3, 99
    WS_WRITE R3, R6
ENUM:
    CONST R0, 0
    MUL   R2, R1, R1
    MUL   R2, R2, R1
L:
    LT    R3, R0, R2
    BRZ   R3, END
    ACT   R1
    MOD   R3, R0, R1
    ACT   R3
    DIV   R4, R0, R1
    MOD   R3, R4, R1
    ACT   R3
    DIV   R4, R4, R1
    MOD   R3, R4, R1
    ACT   R3
    ADD   R0, R0, R5
    JMP   L
END:
    HALT
"""

# rung B: recorder only -- each attempt is recorded; on success the recording is closed into a procedure
P_REC_SRC = """
    INPUT R1, num_ops
    CONST R5, 1
    CONST R0, 0
    MUL   R2, R1, R1
    MUL   R2, R2, R1
L:
    LT    R3, R0, R2
    BRZ   R3, END
    PREC_BEGIN
    ACT   R1
    MOD   R3, R0, R1
    ACT   R3
    DIV   R4, R0, R1
    MOD   R3, R4, R1
    ACT   R3
    DIV   R4, R4, R1
    MOD   R3, R4, R1
    ACT   R3
    INPUT R6, current
    INPUT R7, target
    EQ    R6, R6, R7
    BRNZ  R6, CLOSE
    ADD   R0, R0, R5
    JMP   L
CLOSE:
    PREC_END R6
END:
    HALT
"""

# rung B: invoker only -- tries the first 8 store objects with every argument before enumerating; records nothing
P_INV_SRC = """
    INPUT R1, num_ops
    CONST R5, 1
    CONST R7, 0
H:
    CONST R6, 8
    LT    R3, R7, R6
    BRZ   R3, ENUM
    CONST R4, 0
A:
    CONST R6, 4
    LT    R3, R4, R6
    BRZ   R3, NEXTH
    ACT   R1
    PINVOKE R7, R4
    INPUT R6, current
    INPUT R3, target
    EQ    R6, R6, R3
    BRNZ  R6, END
    ADD   R4, R4, R5
    JMP   A
NEXTH:
    ADD   R7, R7, R5
    JMP   H
ENUM:
    CONST R0, 0
    MUL   R2, R1, R1
    MUL   R2, R2, R1
L:
    LT    R3, R0, R2
    BRZ   R3, END
    ACT   R1
    MOD   R3, R0, R1
    ACT   R3
    DIV   R4, R0, R1
    MOD   R3, R4, R1
    ACT   R3
    DIV   R4, R4, R1
    MOD   R3, R4, R1
    ACT   R3
    ADD   R0, R0, R5
    JMP   L
END:
    HALT
"""

# rung B: recorder + invoker (physical trial only)
P_REC_INV_SRC = """
    INPUT R1, num_ops
    CONST R5, 1
    CONST R7, 0
H:
    CONST R6, 8
    LT    R3, R7, R6
    BRZ   R3, ENUM
    CONST R4, 0
A:
    CONST R6, 4
    LT    R3, R4, R6
    BRZ   R3, NEXTH
    ACT   R1
    PINVOKE R7, R4
    INPUT R6, current
    INPUT R3, target
    EQ    R6, R6, R3
    BRNZ  R6, END
    ADD   R4, R4, R5
    JMP   A
NEXTH:
    ADD   R7, R7, R5
    JMP   H
ENUM:
    CONST R0, 0
    MUL   R2, R1, R1
    MUL   R2, R2, R1
L:
    LT    R3, R0, R2
    BRZ   R3, END
    PREC_BEGIN
    ACT   R1
    MOD   R3, R0, R1
    ACT   R3
    DIV   R4, R0, R1
    MOD   R3, R4, R1
    ACT   R3
    DIV   R4, R4, R1
    MOD   R3, R4, R1
    ACT   R3
    INPUT R6, current
    INPUT R7, target
    EQ    R6, R6, R7
    BRNZ  R6, CLOSE
    ADD   R0, R0, R5
    JMP   L
CLOSE:
    PREC_END R6
END:
    HALT
"""

# rung C: planner (depth <= 2 in the head over stored procedures) + enumeration fallback; records nothing
_PLAN_PREFIX = """
    INPUT R1, num_ops
    CONST R5, 1
    CONST R7, 0
PH:
    CONST R6, 8
    LT    R3, R7, R6
    BRZ   R3, ENUM
    CONST R4, 0
PA:
    CONST R6, 4
    LT    R3, R4, R6
    BRZ   R3, PNEXTH
    PMATCH R6, R7, R4
    BRNZ  R6, EXEC1
    CONST R2, 0
QH:
    CONST R6, 8
    LT    R3, R2, R6
    BRZ   R3, PNEXTA
    CONST R0, 0
QA:
    CONST R6, 4
    LT    R3, R0, R6
    BRZ   R3, QNEXTH
    INPUT R6, current
    PSIM  R6, R7, R4
    PSIM  R6, R2, R0
    INPUT R3, target
    EQ    R6, R6, R3
    BRNZ  R6, EXEC2
    ADD   R0, R0, R5
    JMP   QA
QNEXTH:
    ADD   R2, R2, R5
    JMP   QH
PNEXTA:
    ADD   R4, R4, R5
    JMP   PA
PNEXTH:
    ADD   R7, R7, R5
    JMP   PH
EXEC2:
    ACT   R1
    PINVOKE R7, R4
    PINVOKE R2, R0
    HALT
EXEC1:
    ACT   R1
    PINVOKE R7, R4
    HALT
"""

P_PLAN_SRC = _PLAN_PREFIX + """
ENUM:
    CONST R0, 0
    MUL   R2, R1, R1
    MUL   R2, R2, R1
L:
    LT    R3, R0, R2
    BRZ   R3, END
    ACT   R1
    MOD   R3, R0, R1
    ACT   R3
    DIV   R4, R0, R1
    MOD   R3, R4, R1
    ACT   R3
    DIV   R4, R4, R1
    MOD   R3, R4, R1
    ACT   R3
    ADD   R0, R0, R5
    JMP   L
END:
    HALT
"""

# rung C/D positive control: recorder + invoker(planned) + planner; NEVER seeded into search
P_REC_INV_PLAN_SRC = _PLAN_PREFIX + """
ENUM:
    CONST R0, 0
    MUL   R2, R1, R1
    MUL   R2, R2, R1
L:
    LT    R3, R0, R2
    BRZ   R3, END
    PREC_BEGIN
    ACT   R1
    MOD   R3, R0, R1
    ACT   R3
    DIV   R4, R0, R1
    MOD   R3, R4, R1
    ACT   R3
    DIV   R4, R4, R1
    MOD   R3, R4, R1
    ACT   R3
    INPUT R6, current
    INPUT R7, target
    EQ    R6, R6, R7
    BRNZ  R6, CLOSE
    ADD   R0, R0, R5
    JMP   L
CLOSE:
    PREC_END R6
END:
    HALT
"""

SOURCES = {
    "P_BASE": P_BASE_SRC, "P_CAL": P_CAL_SRC, "P_REC": P_REC_SRC, "P_INV": P_INV_SRC,
    "P_REC_INV": P_REC_INV_SRC, "P_PLAN": P_PLAN_SRC, "P_REC_INV_PLAN": P_REC_INV_PLAN_SRC,
}
# immediate ancestor of each partial (one link shorter)
ANCESTOR = {"P_CAL": "P_BASE", "P_REC": "P_BASE", "P_INV": "P_BASE", "P_REC_INV": "P_INV",
            "P_PLAN": "P_BASE", "P_REC_INV_PLAN": "P_PLAN"}
RUNG_PARTS = {"c2a": ["P_CAL"], "c2b": ["P_REC", "P_INV", "P_REC_INV"],
              "c2c": ["P_REC", "P_INV", "P_REC_INV", "P_PLAN", "P_REC_INV_PLAN"],
              "c2d": ["P_REC", "P_INV", "P_REC_INV", "P_PLAN", "P_REC_INV_PLAN"]}
POSITIVE_CONTROL = {"c2a": "PROCEDURE_REUSE_C1", "c2b": "PROCEDURE_REUSE_C1", "c2c": "P_REC_INV_PLAN", "c2d": "P_REC_INV_PLAN"}


def program(name: str) -> list:
    if name == "ENUMERATE_VM":
        return vm.enumerate_program()
    return vm.assemble(SOURCES[name], max_len=96)


def player(name: str) -> VMPlayer:
    return VMPlayer(program(name), name=name)


def edit_distance(p: list, q: list) -> int:
    """Levenshtein distance over whole instructions (opcode + args)."""
    n, m = len(p), len(q)
    prev = list(range(m + 1))
    for i in range(1, n + 1):
        cur = [i] + [0] * m
        for j in range(1, m + 1):
            cost = 0 if p[i - 1] == q[j - 1] else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
        prev = cur
    return prev[m]


# ---------------------------------------------------------------- diagnostic


def _end_state(plyr, tasks, cfg):
    """Blocks after a full ACCUMULATED lifetime (the transplant donor state)."""
    vm.set_substrate(cfg.get("substrate", {}))
    ws, bs = Workspace.empty(cfg), BlockStore.empty(cfg)
    for i, t in enumerate(tasks):
        run_task(plyr, t, i, ws, bs)
    return bs.snapshot()


def _lifetime_from(plyr, tasks, cfg, blocks_snap=None):
    vm.set_substrate(cfg.get("substrate", {}))
    ws, bs = Workspace.empty(cfg), BlockStore.empty(cfg)
    if blocks_snap is not None:
        bs.restore(blocks_snap)
    res = [run_task(plyr, t, i, ws, bs) for i, t in enumerate(tasks)]
    m = evaluate.lifetime_metrics(res, cfg)
    m["procedures_created"] = sum(1 for e in bs.events if e["kind"] == "create")
    m["invocations"] = sum(bs.invocations.values())
    return m


def run_diagnostic(cfg: dict, config_path: str, out_dir: str, gate_seeds) -> dict:
    from . import baselines_c1 as bl
    os.makedirs(out_dir, exist_ok=True)
    rung = cfg["campaign"]
    names = ["P_BASE"] + RUNG_PARTS[rung]
    pos_name = POSITIVE_CONTROL[rung]
    meta = receipts.run_meta(cfg, config_path)
    rows = {n: [] for n in names}
    rows_tp = {n: [] for n in names}
    seed_rows = []
    t0 = time.time()
    for seed in gate_seeds:
        tasks = streams.lifetime(cfg, seed, "gate")
        donor = _end_state(bl.make_baseline(pos_name), tasks, cfg)
        seed_rows.append(_lifetime_from(VMPlayer(vm.enumerate_program(), name="ENUMERATE_VM"), tasks, cfg))
        for n in names:
            rows[n].append(_lifetime_from(player(n), tasks, cfg))
            rows_tp[n].append(_lifetime_from(player(n), tasks, cfg, donor))
    out = {"meta": meta, "rung": rung, "positive_control": pos_name, "gate_seeds": list(gate_seeds), "parts": {}}
    base_prog = program("P_BASE")

    def mean(rs, k):
        return sum(r[k] for r in rs) / len(rs)

    lines = ["C2 PARTS DIAGNOSTIC rung=%s (gate streams %s; controls only)" % (rung, list(gate_seeds)),
             "ENUMERATE_VM (search seed): fit %.3f solved %.1f cost %.0f" % (mean(seed_rows, "fitness"), mean(seed_rows, "successes"), mean(seed_rows, "charged_cost_total")),
             "%-15s %-12s %4s %4s | %7s %5s %7s | %7s %5s %6s %6s | %7s %5s %7s %6s" % (
                 "part", "ancestor", "len", "dist", "fit", "solv", "cost", "dFit", "sign", "dSolv", "dCost", "tpFit", "tpSol", "tpDFit", "procs")]
    for n in names:
        anc = ANCESTOR.get(n)
        rs, tp = rows[n], rows_tp[n]
        ars = rows[anc] if anc else None
        d = [r["fitness"] - a["fitness"] for r, a in zip(rs, ars)] if anc else []
        dtp = [r["fitness"] - a["fitness"] for r, a in zip(tp, rows_tp[anc])] if anc else []
        rec = {"ancestor": anc, "length": len(program(n)), "dist_from_base": edit_distance(base_prog, program(n)),
               "dist_from_ancestor": edit_distance(program(anc), program(n)) if anc else 0,
               "fitness": mean(rs, "fitness"), "solved": mean(rs, "successes"), "cost": mean(rs, "charged_cost_total"),
               "selective_value": (sum(d) / len(d)) if d else None,
               "sign_reproducibility": (sum(1 for x in d if x > 0) if d else None),
               "d_solved": (mean(rs, "successes") - mean(ars, "successes")) if anc else None,
               "d_cost": (mean(rs, "charged_cost_total") - mean(ars, "charged_cost_total")) if anc else None,
               "transplant_fitness": mean(tp, "fitness"), "transplant_solved": mean(tp, "successes"),
               "transplant_value": (sum(dtp) / len(dtp)) if dtp else None,
               "procedures_created": mean(rs, "procedures_created"), "invocations": mean(rs, "invocations"),
               "per_stream": {"fitness": [r["fitness"] for r in rs], "transplant_fitness": [r["fitness"] for r in tp]}}
        out["parts"][n] = rec
        lines.append("%-15s %-12s %4d %4d | %7.3f %5.1f %7.0f | %7s %5s %6s %6s | %7.3f %5.1f %7s %6.1f" % (
            n, anc or "-", rec["length"], rec["dist_from_base"], rec["fitness"], rec["solved"], rec["cost"],
            "%.3f" % rec["selective_value"] if anc else "-", "%d/%d" % (rec["sign_reproducibility"], len(d)) if anc else "-",
            "%.1f" % rec["d_solved"] if anc else "-", "%.0f" % rec["d_cost"] if anc else "-",
            rec["transplant_fitness"], rec["transplant_solved"], "%.3f" % rec["transplant_value"] if anc else "-", rec["procedures_created"]))
    lines.append("dist = instruction edit distance from P_BASE; dFit = part - ancestor (paired, same streams); sign = streams with dFit > 0;")
    lines.append("tp* = store pre-loaded from %s's end-of-lifetime artifacts on the same stream; procs = objects created per lifetime" % pos_name)
    text = "\n".join(lines)
    out["elapsed_s"] = round(time.time() - t0, 1)
    receipts.write_json(os.path.join(out_dir, "PARTS.json"), out)
    with open(os.path.join(out_dir, "PARTS.md"), "w", encoding="ascii", newline="\n") as f:
        f.write(text + "\n")
    print(text)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--seeds", type=int, nargs="*", default=list(range(301, 311)))
    args = ap.parse_args(argv)
    cfg = receipts.load_config(args.config)
    out = args.out or os.path.join("crius", "runs", "parts_%s" % cfg["campaign"])
    run_diagnostic(cfg, args.config, out, args.seeds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
