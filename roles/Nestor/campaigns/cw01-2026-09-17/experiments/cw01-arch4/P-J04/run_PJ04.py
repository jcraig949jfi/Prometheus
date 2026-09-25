"""P-J04 [T-X21; requires P-J01]: FORENSICS AFTER A CROSSING. P-J01 crossed no world, so the evolved-organism
forensics are NOT_APPLICABLE for A', B' and C'. The A' instruments are VALIDATED on the hand-constructed
XOR-1 witnesses (P-J02; instruments, not discoveries): (i) cue causality - the ask tick's regime word is
overwritten and the answer must follow it; (ii) register corruption at the ask - each register is
overwritten with the other regime's typical value before the ask tick (the witness reads the word during
the tick, so an override BEFORE the tick must NOT change the answer, and an override of the register
AFTER the read cannot be applied by this instrument: the instrument's reach is recorded); (iii) control
knockouts - every JZ / JNZ / JMP and every inserted instruction disabled in turn (answer must depend
causally on the witness's XOR). B' / C' instruments (identical decision-time observation via different
histories; erase / overwrite between cue and ask; cue-follow ceiling under reliability / block / shuffled
/ reset / unexpected transitions) exist from P-I02 and have no organism to act on. Computational scope:
integer programs on a bounded VM."""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import ctxworlds as CW         # noqa: E402
import ctxevo as CE            # noqa: E402
sys.path.insert(0, str(HERE.parent / "P-I02"))
sys.path.insert(0, str(HERE.parent / "P-J02"))
from run_PI02 import eval_reg  # noqa: E402
from run_PJ02 import insert, instrs, with_genome   # noqa: E402
A, L = CM.A, CM.L
PID, TID, XOR = "P-J04", "T-X21", 1
NOP = 0


def cue_causality(m, eps):
    """Overwrite the regime word of every ask tick (A: [ASK, tag, r] -> 1 - r); share of answers that follow the new regime."""
    base = eval_reg(m, eps)["trace"]
    flipped = []
    for ei, ep in enumerate(eps):
        e2 = CW.Episode(ticks=[list(t) for t in ep.ticks], expected=dict(ep.expected), intervention_tick=ep.intervention_tick, meta=dict(ep.meta))
        for ti, w in enumerate(e2.ticks):
            if w[0] == CW.K_ASK:
                e2.ticks[ti] = [w[0], w[1], 1 - w[2]]
        flipped.append(e2)
    alt = eval_reg(m, flipped)["trace"]
    follows = [int(a["answer"] == CW.f_regime(1 - b["regime"], b["v"], XOR)) for a, b in zip(alt, base)]
    changed = [int(a["answer"] != b["answer"]) for a, b in zip(alt, base)]
    return {"changed": float(np.mean(changed)), "follows_new_regime": float(np.mean(follows))}


def register_corruption(m, eps):
    """Before every ask tick, overwrite register j with 1 - r (the other regime's word); share of asks whose answer changes, per j."""
    base = [t["answer"] for t in eval_reg(m, eps)["trace"]]
    out = {}
    for j in range(m["n_regs"]):
        ov = {}
        for ei, ep in enumerate(eps):
            for ti, w in enumerate(ep.ticks):
                if w[0] == CW.K_ASK:
                    ov[(ei, ti)] = {j: 1 - ep.meta["regime"][0]}
        alt = [t["answer"] for t in eval_reg(m, eps, reg_override=ov)["trace"]]
        out[j] = float(np.mean([a != b for a, b in zip(alt, base)]))
    return out


def knockouts(m, eps, inserted):
    """Disable each control instruction and each inserted instruction (opcode -> NOP); held reward after."""
    rows = []
    for i, x in enumerate(instrs(m)):
        op = x[0] % 25
        if op in (18, 19, 20) or i in inserted:
            c = json.loads(json.dumps(m))
            c["genome"][i * 4] = NOP
            rows.append({"i": i, "op": op, "inserted": i in inserted, "reward": round(CW.reward(c, eps), 4)})
    return rows


def main():
    t0 = time.time()
    wit = json.load(open(HERE.parent / "P-J02" / "witnesses.json", encoding="utf-8"))
    tops = json.load(open(HERE.parent / "P-I01" / "tops.json", encoding="utf-8"))
    pj01 = json.load(open(HERE.parent / "P-J01" / "RESULT.json", encoding="utf-8"))
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "requires": ["P-J01"], "scope": CM.SCOPE, "claim_type": "mechanism-forensics", "p_j01_disposition": pj01["disposition"],
                         "evolved_forensics": "NOT_APPLICABLE per world without a crossing", "instrument_validation": "A' instruments on the P-J02 XOR-1 witnesses: cue causality, register corruption before the ask tick, control / inserted-instruction knockouts",
                         "expected_on_witness": {"cue_causality.follows_new_regime": 1.0, "register_corruption": "0 for every register (the word is read during the tick)", "knockout of the XOR": "reward falls to the identity level (~.5)"},
                         "material_rule": "not material (instrument validation only) unless an evolved organism exists", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    rows = []
    for w in wit:
        if w["xor1"] is None:
            continue
        m0 = next(r for r in tops if r["world"] == "A" and r["control"] is None and r["seed"] == w["seed"])["tops"][w["rank"]]["m"]
        m = insert(m0, w["xor1"]["pos"], w["xor1"]["seq"])
        eps = CE.held_sets("A", w["seed"], xor=XOR)[0]
        inserted = set(range(w["xor1"]["pos"], w["xor1"]["pos"] + w["xor1"]["n_instr"]))
        rc = register_corruption(m, eps)
        ko = knockouts(m, eps, inserted)
        rows.append({"seed": w["seed"], "rank": w["rank"], "witness_reward": round(CW.reward(m, eps), 4), "cue_causality": cue_causality(m, eps), "register_corruption_max": max(rc.values()), "register_corruption": rc,
                     "knockouts": ko, "xor_knockout_reward": [k["reward"] for k in ko if k["inserted"] and k["op"] == 12], "control_knockouts_min_reward": min([k["reward"] for k in ko if not k["inserted"]], default=None)})
    summary = {"evolved": {w: "NOT_APPLICABLE(%s)" % pj01["disposition"][w[0]] for w in ("A'", "B'", "C'")},
               "instrument_validation": {"n_witnesses": len(rows), "follows_new_regime": [r["cue_causality"]["follows_new_regime"] for r in rows], "register_corruption_max": [r["register_corruption_max"] for r in rows],
                                         "xor_knockout_reward": [r["xor_knockout_reward"] for r in rows], "control_knockouts_min_reward": [r["control_knockouts_min_reward"] for r in rows]},
               "instrument_reach": "register overrides act at the tick boundary only; a register written during the ask tick (the witness's IN) is beyond the override's reach - a within-tick lesion needs the knockout instrument"}
    out = {"perturbation_id": PID, "parent": TID, "summary": summary, "rows": rows, "material": False, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "forensics after crossing: NOT_APPLICABLE for A'/B'/C' (%s). A' instruments validated on %d XOR-1 witnesses: cue causality follows_new_regime %s; register corruption before the tick changes %s of answers (max); XOR knockout reward %s; control knockouts min reward %s. %s" % (
        pj01["disposition"], len(rows), summary["instrument_validation"]["follows_new_regime"], summary["instrument_validation"]["register_corruption_max"], summary["instrument_validation"]["xor_knockout_reward"], summary["instrument_validation"]["control_knockouts_min_reward"], summary["instrument_reach"]), False, detail=summary)
    print("DONE (%.0f s)" % (time.time() - t0), json.dumps(summary, default=CM.js)[:1200])


if __name__ == "__main__":
    main()
