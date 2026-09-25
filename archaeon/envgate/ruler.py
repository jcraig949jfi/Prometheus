"""Offline copier ruler for arriving tapes: the FROZEN census ruler (copier_census phenotype/classify, same empty neighbour, all 256
inputs, same input-skip), computed once per arriving tape and shared by every arm of the block. It never affects a world except
through the pure-function memo it pre-fills (the same results the world would compute itself)."""
from __future__ import annotations

from archaeon.z80atlas import vm, engine as ZE
from archaeon.z80atlas.census import copier_census as C
from archaeon.envgate.engine import Memo, ZERO, STEP_CAP

HIT = set(C.HIT_CLASSES)


def phenotype_from(tape: bytes, x: int, r: dict) -> dict:
    """copier_census.phenotype, given the raw vm.execute result (identical fields, identical arithmetic)."""
    G = len(tape); cov = sum(r["nbr_mask"]) / G; birth = cov >= C.COPY_MIN; win = r["nbr_window"]
    span, k = C.best_span(win, r["nbr_mask"], tape) if r["writes_nbr"] else (0, 0)
    return {"x": x, "writes": r["writes_nbr"], "cov": cov, "birth": birth, "fid": ZE.fidelity(win, tape), "exact": birth and win == tape,
            "span": span, "k": k, "steps": r["steps"], "halted": r["halted"], "in_read": r["inputs_read"] > 0, "hist": r["hist"],
            "exec_addrs": sum(r["executed"]), "window": win}


def measure(tape: bytes, memo: Memo = None) -> dict:
    r0 = vm.execute(tape, ZERO, (0,), STEP_CAP, True, -1.0)
    if memo is not None: memo.put(tape, ZERO, (0,), r0)
    p0 = phenotype_from(tape, 0, r0)
    if not p0["in_read"]:
        ph = [dict(p0, x=x) for x in range(256)]                           # input-independent (memo stored it under inputs=None)
    else:
        ph = [p0]
        for x in range(1, 256):
            r = vm.execute(tape, ZERO, (x,), STEP_CAP, True, -1.0)
            if memo is not None: memo.put(tape, ZERO, (x,), r)
            ph.append(phenotype_from(tape, x, r))
    cls = C.classify(ph, len(tape))
    out = {"class": cls}
    if cls in HIT or any(p["birth"] for p in ph):
        out.update({"exact_inputs": [p["x"] for p in ph if p["exact"]], "birth_inputs": [p["x"] for p in ph if p["birth"]],
                    "max_fid": round(max(p["fid"] for p in ph), 4), "max_span": max(p["span"] for p in ph)})
    return out
