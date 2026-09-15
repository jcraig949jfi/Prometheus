"""E-R4-1: clause B transfer on the round 4 survivor, E-T1b rule (SWARM_R4 s5 E, s7).

Only SURVIVED world x pressure cells host E's transfer work (worlds_r4.json, active variant gate_in|HOLD).
One cell survived: w13 train128_held64. A graft needs an identical genome layout (transfer.compatible);
among the screened candidates w1..w37, only w14 and w20 match w13's linear layout (D=5, A=8, W=1, 200 B).
Both are screened (CULLED) donors; the recipient is the survivor. Family = the two pairs, Holm across them.

Per pair and run seed: E-T1's harness unchanged (transfer.run_seed, bit-identical to the committed E-T1b
rows), at the pressure's M2 budget (primordial.metric.baseline.BUDGET: train128 = 800 x 128) on TRAIN128,
held-out AUC on HELD64. Read: graft vs BOTH cheats paired per run seed, one-sided exact sign-flip, p_max
over the cheats, Holm across pairs; planted self_graft must be detected; oracles on the first run seed.
The judge is `qd_ledger check-b` on the committed rows; the check_b row this job emits is report-only.

Guard (from the file, never recomputed): recipient must pass metric.worlds.guard; donor must be on the
list; layouts must match. A failing pair is an `aborted` row. F9 checkpoint after every run seed.

    python -m primordial.fabric.worker submit E primordial.cohorts.e.r4_transfer:job --exp E-R4-1-transfer-w13-train128 \\
        --rows primordial/ledger/rows/E/E-R4-1-transfer-w13-train128.jsonl --ttl-cpu-s S --kwargs '{}'
"""
from __future__ import annotations

import numpy as np

from primordial.cohorts.e import transfer as T
from primordial.metric import floors as F
from primordial.metric import worlds as W
from primordial.metric.baseline import BUDGET
from primordial.qd import e7_run as E7
from primordial.score.transfer_b import check_b

EXP = "E-R4-1-transfer-w13-train128"
PRESSURE = "train128_held64"
PAIRS = ((14, 13), (20, 13))


def screen_gate(doc, donor: int, recipient: int, pressure: str, family: str = "linear") -> str | None:
    """None iff the pair may run: recipient SURVIVED, donor screened, layouts identical."""
    g = W.guard(doc, f"w{recipient}", pressure)
    if g is not None:
        return f"recipient w{recipient} {pressure} INELIGIBLE({g['why']})"
    if W.lookup(doc, f"w{donor}", pressure) is None:
        return f"donor w{donor} {pressure} UNSCREENED"
    ok, why = T.compatible(E7.G7(donor, family), E7.G7(recipient, family))
    return None if ok else why


def job(ctx, pairs=PAIRS, family="linear", pressure=PRESSURE, run_seeds=tuple(range(16)), gens=None, batch=None,
        n_train=None, tag="full", dev=False, exp=EXP, worlds_path=None):
    doc = W.load(worlds_path or W.WORLDS_R4)
    bg, bb = BUDGET[pressure]
    gens, batch = int(gens or bg), int(batch or bb)
    n_train = int(n_train or len(F.PRESSURES[pressure]))
    run_seeds = [int(s) for s in run_seeds]
    mark = (lambda r: dict(r, status="dev", role=r.get("status"))) if dev else (lambda r: r)
    st = ctx.load_checkpoint() or {"done": {}, "summ": {}, "aborted": [], "checked": False}
    for donor, recipient in pairs:
        key = f"w{donor}->w{recipient}"
        base = dict(T.pair_base(int(donor), int(recipient), family, gens, batch, n_train, tag), pressure=pressure,
                    budget_ok=(gens, batch, n_train) == (bg, bb, len(F.PRESSURES[pressure])))
        why = screen_gate(doc, int(donor), int(recipient), pressure, family)
        if why:
            if key not in st["aborted"]:
                ctx.emit(dict(base, status="aborted", reason=why))
                st["aborted"].append(key)
                ctx.checkpoint(st)
            continue
        done = st["done"].setdefault(key, {})
        for rs in run_seeds:
            if str(rs) in done:
                continue
            if ctx.should_pause():
                ctx.pause(st)
            rows, cv = T.run_seed(int(donor), int(recipient), family, rs, gens, batch, n_train, base,
                                  oracles=rs == run_seeds[0])
            for c in T.CONDITIONS:
                ctx.emit(mark(rows[c]))
            done[str(rs)] = {"rows": rows, "curves": {c: cv[c].tolist() for c in T.CONDITIONS}}
            ctx.checkpoint(st)
        if key not in st["summ"]:
            per = {c: [done[str(s)]["rows"][c] for s in run_seeds] for c in T.CONDITIONS}
            curves = {c: [np.asarray(done[str(s)]["curves"][c]) for s in run_seeds] for c in T.CONDITIONS}
            st["summ"][key] = T.summarize(base, per, curves, run_seeds)
            ctx.emit(mark(st["summ"][key]))
            ctx.checkpoint(st)
    if not st["checked"]:
        rows = [dict(r, exp_id=exp) for d in st["done"].values() for s in d.values() for r in s["rows"].values()]
        rows += [dict(s, exp_id=exp) for s in st["summ"].values()]
        out = check_b(rows)
        ctx.emit({"kind": "check_b", "status": "dev" if dev else "record", "report_only": True, "exp_id": exp,
                  "pressure": pressure, "judge": "python -m primordial.ops.qd_ledger check-b --rows <this rows file>",
                  **out})
        st["checked"] = True
        ctx.checkpoint(st)
