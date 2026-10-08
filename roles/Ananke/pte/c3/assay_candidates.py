"""Causal assays for competent candidates (order s5/s6; used by C3R and C4). DESCRIPTIVE per candidate; run after
production and before interpretation. usage: python assay_candidates.py CANDIDATES.json OUT.json [device]

CANDIDATES.json: list of {name, physics (rep physics dict), env (EnvSpec dict), role, genome, dup_mask (optional,
[R][L] bool), extra_from (optional int: first extra line, e.g. 16), has_S2 (bool)}.
Assays (fresh namespace H(0xA55A7, name-hash)):
  1 FRESH_HELD   competence on 256 fresh worlds
  2 SWAPS        swap_v2 FLIP/NO_EFFECT/PARTIAL/EMPTY for S0, S1, S2 (if present), Msum at a mid-trial offset,
                 pooled over scored trials 4..11
  3 ABLATIONS    S2 forced to 0 after every tick (persistent-state feature); DUP lines -> NOP; EXTRA lines -> NOP
  4 CONTROLS     zero_comm; teacher_off (FLIP: teacher only on trial 0; GATE: context only in block 0)
REP_DEPENDENT  = competence (status TRUE) is lost under the ablation of the candidate's representation feature(s).
"""
import hashlib
import json
import os
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import swap_v2 as SW  # noqa: E402
C = SW.C
from prometheus.ananke import assays, envs, lens  # noqa: E402
from prometheus.ananke.engine import Controls  # noqa: E402


def _comp(role, pt, ep):
    c = C.competence(role, pt, ep)
    return C.slim(c)


def _run_pt(ph, env, g, seeds, device, hooks_all=None, ctrl=None, edit=None):
    ep = envs.build(ph, env, seeds)
    sch = ep.schedule
    if edit is not None:
        sv = sch.sense_val.numpy().copy(); edit(sv, ep)
        import torch
        sch = type(sch)(sch.sense_idx, torch.as_tensor(sv), sch.read_idx)
    hooks = {t: hooks_all for t in range(env.T())} if hooks_all else None
    tr = lens.run(ph, np.asarray(g, dtype=np.int64), env, seeds, hooks=hooks, device=device, ctrl=ctrl, schedule=sch, ep=ep)
    return tr.per_trial, ep


def assay(cand, device="cpu"):
    ph = C.Physics.from_dict(cand["physics"]).validate(); env = envs.EnvSpec(**cand["env"])
    role = cand["role"]; g = np.asarray(cand["genome"], dtype=np.int64)
    h = int(hashlib.sha256(cand["name"].encode()).hexdigest()[:8], 16)
    seeds = assays.world_seeds(C.H_int(0xA55A7, h), 256)
    out = {"name": cand["name"]}
    pt, ep = _run_pt(ph, env, g, seeds, device)
    out["fresh_held"] = _comp(role, pt, ep)
    sw_seeds = seeds[:128]
    off = max(1, env.delta // 2)
    comps = [("S0", [("S", 0)]), ("S1", [("S", 1)])] + ([("S2", [("S", 2)])] if cand.get("has_S2") else []) + \
            [("Msum", [("Msum", None)])]
    out["swaps"] = {}
    for nm, cc in comps:
        try:
            out["swaps"][nm] = SW.carrier_swap(ph, g, env, sw_seeds, cc, trials=list(range(4, 12)), offset=off, device=device)["verdict"]
        except AssertionError as e:
            out["swaps"][nm] = f"NOT_RUN ({e})"
    abl = {}
    if cand.get("has_S2"):
        def zero_s2(w):
            w.S[..., 2] = 0
        pt2, ep2 = _run_pt(ph, env, g, seeds, device, hooks_all=zero_s2)
        abl["S2_zeroed"] = _comp(role, pt2, ep2)
    if cand.get("dup_mask") is not None and np.asarray(cand["dup_mask"]).any():
        gd = g.copy(); gd[np.asarray(cand["dup_mask"], bool)] = 0
        pt3, ep3 = C.eval_programs(ph, env, seeds, [gd], device=device)
        abl["dup_lines_nop"] = _comp(role, pt3[0], ep3)
    if cand.get("extra_from") is not None:
        ge = g.copy(); ge[:, cand["extra_from"]:, :] = 0
        pt4, ep4 = C.eval_programs(ph, env, seeds, [ge], device=device)
        abl["extra_lines_nop"] = _comp(role, pt4[0], ep4)
    out["ablations"] = abl
    ptz, epz = _run_pt(ph, env, g, seeds, device, ctrl=Controls(zero_comm=True))
    out["zero_comm"] = _comp(role, ptz, epz)
    if env.family in ("FLIP", "GATE"):
        def t_off(sv, ep):
            if env.family == "FLIP":
                C.teacher_off(sv, ep)
            else:
                Pd = env.period(); sv[env.block * Pd:, :, 1] = 0
        ptt, ept = _run_pt(ph, env, g, seeds, device, edit=t_off)
        out["teacher_or_context_off"] = _comp(role, ptt, ept)
    out["REP_DEPENDENT"] = bool(abl) and any(v["status"] != "TRUE" for v in abl.values())
    return out


if __name__ == "__main__":
    cands = json.load(open(sys.argv[1])); dev = sys.argv[3] if len(sys.argv) > 3 else "cpu"
    res = [assay(c, dev) for c in cands]
    for r in res:
        print(r["name"], r["fresh_held"]["status"], r["swaps"], {k: v["status"] for k, v in r["ablations"].items()},
              r["zero_comm"]["status"], r.get("teacher_or_context_off", {}).get("status"), "REP_DEPENDENT", r["REP_DEPENDENT"])
    C.jdump(sys.argv[2], res)
