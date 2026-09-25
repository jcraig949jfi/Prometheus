"""P-I02 [T-X21, deformation M; requires P-I01]: IDENTIFY WHAT EVOLVED, behaviour first. For the top-4 of
every P-I01 run: cue causality (the earlier cue overwritten, decision-time observation unchanged),
adaptation after regime switches, anticipation on misleading switch trials, state corruption and
recovery, transfer to held-out regime sequences, and candidate internal quantities (registers that
predict the regime) overwritten with their other-regime value. Names from behaviour only.
Computational scope: integer programs on a bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
from collections import Counter

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import ctxworlds as CW         # noqa: E402
import ctxevo as CE            # noqa: E402
A, L = CM.A, CM.L
from proteus.foundry.vm import Player, Meter   # noqa: E402

PID, TID = "P-I02", "T-X21"
FLOOR = A.C1.FLOOR


def eval_reg(m, eps, reg_override=None, clear_at=None, cue_override=None):
    """eval_trace with register overrides applied BEFORE a tick: reg_override {(ei, ti): {j: value}}."""
    player = Player(m)
    trace, correct, asks = [], 0, 0
    for ei, ep in enumerate(eps):
        st = player.fresh_state()
        rng = A.SplitMix64(A.seed_from("wse.vmrng", 0, ei))
        ask_i = 0
        for ti, words in enumerate(ep.ticks):
            if clear_at and (ei, ti) in clear_at:
                st["tape"] = list(player.genome) + [0] * (player.tape_words - player.genome_len)
                st["regs"] = [0] * player.n_regs
            w = list(words)
            if cue_override and (ei, ti) in cue_override and w and w[0] == CW.CUE:
                w[2] = cue_override[(ei, ti)]
            player.begin_tick(st)
            if reg_override and (ei, ti) in reg_override:
                for j, val in reg_override[(ei, ti)].items():
                    if j < len(st["regs"]):
                        st["regs"][j] = val
            outs, _ = player.run_tick(st, [w], 1, rng, meter=Meter())
            if ti in ep.expected:
                a = outs[0][0] if outs[0] else None
                ok = int(a is not None and a == ep.expected[ti])
                asks += 1
                correct += ok
                trace.append({"ep": ei, "tick": ti, "ask_i": ask_i, "answer": a, "expected": ep.expected[ti], "correct": ok, "regime": ep.meta["regime"][ask_i], "cue": ep.meta["cue"][ask_i], "v": ep.meta["v"][ask_i], "regs": list(st["regs"])})
                ask_i += 1
    return {"reward": correct / max(1, asks), "trace": trace}


def cue_causality(m, world, sets):
    """Flip every cue; share of asks whose answer changes and share now matching the OTHER regime's answer."""
    changed, other, n = 0, 0, 0
    for eps in sets:
        base = eval_reg(m, eps)["trace"]
        ov = {(ei, ti): 1 - w[2] for ei, ep in enumerate(eps) for ti, w in enumerate(ep.ticks) if w and w[0] == CW.CUE}
        if world == "A":
            ov = None
            flipped = [CW.__dict__["Episode"](ticks=[list(t) for t in ep.ticks], expected=dict(ep.expected), intervention_tick=ep.intervention_tick, meta=ep.meta) for ep in eps]
            for ep in flipped:
                for t in ep.ticks:
                    if t[0] == 2 and len(t) > 2:
                        t[2] = 1 - t[2]
            alt = eval_reg(m, flipped)["trace"]
        else:
            alt = eval_reg(m, eps, cue_override=ov)["trace"]
        for b, a in zip(base, alt):
            n += 1
            changed += int(b["answer"] != a["answer"])
            other += int(a["answer"] == CW.f_regime(1 - b["regime"], b["v"]))
    return {"changed": changed / max(1, n), "matches_other_regime": other / max(1, n)}


def regime_registers(traces):
    """Per register: in-sample accuracy of predicting the regime from the register's value at the ask."""
    n_regs = len(traces[0]["regs"]) if traces else 0
    out = {}
    for j in range(n_regs):
        vals = [t["regs"][j] for t in traces]
        if len(set(vals)) <= 1:
            continue
        maj = {}
        for t in traces:
            maj.setdefault(t["regs"][j], Counter())[t["regime"]] += 1
        acc = sum(c.most_common(1)[0][1] for c in maj.values()) / len(traces)
        out[j] = {"accuracy": acc, "n_values": len(maj), "typical": {r: Counter(t["regs"][j] for t in traces if t["regime"] == r).most_common(1)[0][0] for r in (0, 1) if any(t["regime"] == r for t in traces)}}
    return out


def register_transplant(m, eps, reg, typical):
    """Overwrite register `reg` at every ask tick with its typical value under the OTHER regime."""
    base = eval_reg(m, eps)["trace"]
    ov = {}
    for t in base:
        other = 1 - t["regime"]
        if other in typical:
            ov[(t["ep"], t["tick"])] = {reg: typical[other]}
    alt = eval_reg(m, eps, reg_override=ov)["trace"]
    n = max(1, len(base))
    return {"changed": sum(int(b["answer"] != a["answer"]) for b, a in zip(base, alt)) / n, "follows_register": sum(int(a["answer"] == CW.f_regime(1 - b["regime"], b["v"])) for b, a in zip(base, alt)) / n}


def c_dynamics(m, seed):
    """Adaptation, anticipation, recovery and transfer in world C."""
    sets = CE.held_sets("C", seed)
    by_pos, antic, cue_follow_antic = {}, [], []
    for eps in sets:
        tr = eval_reg(m, eps)["trace"]
        prev = None
        since = 0
        for t in tr:
            if prev is not None and t["regime"] != prev:
                since = 0
            by_pos.setdefault(since, []).append(t["correct"])
            if since == 0 and prev is not None and t["cue"] != t["regime"]:
                antic.append(t["correct"])
                cue_follow_antic.append(0)
            prev = t["regime"]
            since += 1
    rec = {}
    for eps in sets:
        for k in (4, 8):
            tr = eval_reg(m, eps, clear_at={(0, 3 * k)})["trace"]
            for t in tr[k:k + 4]:
                rec.setdefault(t["ask_i"] - k, []).append(t["correct"])
    transfer = {}
    for name, kw in (("block3", {"block": 3}), ("block5", {"block": 5}), ("phase2", {"phase": 2}), ("p0.6", {"p_cue": 0.6}), ("p0.9", {"p_cue": 0.9})):
        s2 = [CW.make("C", seed, 20_000 + i, **kw) for i in range(3)]
        transfer[name] = {"reward": CE.held_reward(m, s2), "cue_follow": float(np.mean([CW.ceilings(s, "C")["cue_follow"] for s in s2])), "tracker": float(np.mean([CW.ceilings(s, "C")["tracker"] for s in s2]))}
    return {"accuracy_by_trials_since_switch": {str(k): float(np.mean(v)) for k, v in sorted(by_pos.items())}, "anticipation_on_misleading_switch": float(np.mean(antic)) if antic else None, "n_misleading_switch": len(antic),
            "recovery_after_clear": {str(k): float(np.mean(v)) for k, v in sorted(rec.items())}, "transfer": transfer}


def job(j):
    m, world, seed = j["m"], j["world"], j["seed"]
    sets = CE.held_sets(world, seed)
    held = CE.held_reward(m, sets)
    traces = [t for s in sets for t in eval_reg(m, s)["trace"]]
    stim = float(np.mean([t["answer"] != t["v"] for t in traces if t["answer"] is not None]))
    cue = cue_causality(m, world, sets)
    regs = regime_registers(traces)
    cand = max(regs, key=lambda k: regs[k]["accuracy"]) if regs else None
    tr = register_transplant(m, sets[0], cand, regs[cand]["typical"]) if cand is not None and regs[cand]["accuracy"] >= 0.9 else None
    strat = Counter()
    for t in traces:
        a = t["answer"]
        strat["identity" if a == t["v"] else "complement" if a == 15 - t["v"] else "silent" if a is None else "other"] += 1
    out = {"world": world, "seed": seed, "rank": j["rank"], "held": held, "answer_strategy": {k: v / max(1, sum(strat.values())) for k, v in strat.items()}, "cue_causality": cue,
           "regime_registers": {str(k): v for k, v in sorted(regs.items(), key=lambda kv: -kv[1]["accuracy"])[:3]}, "candidate_register": cand, "register_transplant": tr, "stimulus_dependence": stim}
    if world == "C":
        out["dynamics"] = c_dynamics(m, seed)
    crossed = held >= CE.THRESH[world]
    if not crossed:
        name = "NOT_CROSSED"
    elif world == "A":
        name = "CONTEXT_DETECTOR" if cue["matches_other_regime"] >= 0.5 else "UNCLASSIFIED"
    elif world == "B":
        name = "HISTORY_DEPENDENT" if cue["changed"] >= 0.5 else "UNCLASSIFIED"
    else:
        d = out["dynamics"]
        above = held >= d["transfer"]["p0.6"]["cue_follow"] + 0.1 or held >= 0.8
        antic = d["anticipation_on_misleading_switch"] is not None and d["anticipation_on_misleading_switch"] >= 0.5
        adapt = d["accuracy_by_trials_since_switch"].get("0", 0) < d["accuracy_by_trials_since_switch"].get("2", 0) - 0.1
        name = "PREDICTIVE" if antic else "ADAPTIVE_STATE" if adapt else "HISTORY_DEPENDENT" if cue["changed"] >= 0.5 else "UNCLASSIFIED"
    out["name"] = name
    return out


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "M", "requires": ["P-I01"], "scope": CM.SCOPE, "claim_type": "mechanism-forensics",
                         "organisms": "top-4 of every P-I01 plain run", "tests": ["stimulus dependence", "cue causality (cue flipped; A: regime word flipped)", "regime-predicting registers and their transplant", "C: adaptation by trials since switch, anticipation on misleading switch trials, recovery after clearing state, transfer to block 3/5, phase 2, p .6/.9"],
                         "naming": {"CONTEXT_DETECTOR": "A crossed and flipping the regime word flips the answer to the other regime (>= .5)", "HISTORY_DEPENDENT": "B or C crossed and flipping the EARLIER cue changes >= .5 of answers", "ADAPTIVE_STATE": "C crossed with accuracy rising over trials since a switch by >= .1", "PREDICTIVE": "C crossed and correct on >= .5 of misleading switch trials", "UNCLASSIFIED": "crossed without these signatures (-> node)", "NOT_CROSSED": "strategy named from the traces"},
                         "material_rule": "always material", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    runs = json.loads((HERE.parent / "P-I01" / "tops.json").read_text(encoding="utf-8"))
    jobs = [{"m": t["m"], "world": r["world"], "seed": r["seed"], "rank": i} for r in runs if r["control"] is None for i, t in enumerate(r["tops"][:4])]
    with A.pool(8) as ex:
        rows = list(ex.map(job, jobs))
    summ = {}
    for w in "ABC":
        rs = [r for r in rows if r["world"] == w]
        summ[w] = {"names": dict(Counter(r["name"] for r in rs)), "held": float(np.mean([r["held"] for r in rs])), "cue_changed": float(np.mean([r["cue_causality"]["changed"] for r in rs])), "cue_other": float(np.mean([r["cue_causality"]["matches_other_regime"] for r in rs])),
                   "register_transplant": [r["register_transplant"] for r in rs if r["register_transplant"]][:4], "strategies": {k: float(np.mean([r["answer_strategy"].get(k, 0) for r in rs])) for k in ("identity", "complement", "silent", "other")}}
        if w == "C":
            summ[w]["adaptation"] = {k: float(np.mean([r["dynamics"]["accuracy_by_trials_since_switch"].get(k, np.nan) for r in rs])) for k in ("0", "1", "2", "3")}
            summ[w]["anticipation"] = float(np.nanmean([r["dynamics"]["anticipation_on_misleading_switch"] if r["dynamics"]["anticipation_on_misleading_switch"] is not None else np.nan for r in rs]))
            summ[w]["recovery"] = {k: float(np.mean([r["dynamics"]["recovery_after_clear"].get(k, np.nan) for r in rs])) for k in ("0", "1", "2", "3")}
            summ[w]["transfer"] = {k: (float(np.mean([r["dynamics"]["transfer"][k]["reward"] for r in rs])), rs[0]["dynamics"]["transfer"][k]["cue_follow"], rs[0]["dynamics"]["transfer"][k]["tracker"]) for k in rs[0]["dynamics"]["transfer"]} if rs else {}
    unclassified = [r for r in rows if r["name"] == "UNCLASSIFIED"]
    out = {"perturbation_id": PID, "parent": TID, "summary": summ, "n_unclassified": len(unclassified), "material": True, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "what evolved: %s" % {w: (v["names"], round(v["held"], 3), round(v["cue_changed"], 2), round(v["cue_other"], 2), v["strategies"]) for w, v in summ.items()}, True, detail=summ)
    print("DONE (%.0f s) %s" % (time.time() - t0, {w: v["names"] for w, v in summ.items()}))


if __name__ == "__main__":
    main()
