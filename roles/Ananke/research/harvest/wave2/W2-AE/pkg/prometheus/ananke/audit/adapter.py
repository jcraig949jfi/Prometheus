"""PTE adapter for prometheus.explib (promoted from W2-F adapters/pte.py; the explib core never imports PTE).

  record_from_difftrace(dt)          H-INST DiffTrace -> explib DiffRecord (closure, cones, paths, authority)
  reach(ph, genome, env, seeds, hooks, trial)
                                     explib reach certificate on the PTE engine (via H-INST diff_trace)
  pair_table(ph, genome, env, seeds, ctrl=None, hooks=None)
                                     a scored run in explib's pair-table convention (outputs/targets/pair):
                                     the input format of explib.metamorphic relations and of
                                     explib.controls.mirror_identity; W2-C's operators can produce these
  zero_comm_panel(rows, family)      C1 rows -> (control_stats, treatment_stats) for the identity audit
  lightcone_ceilings(path, family, topology)
                                     H-PLANT light-cone bounds -> per-cell ceilings for attainable.eligibility
  swap_rel_ci(a, s, K, arm_cert)     the promoted swap_rel H2 interval for a W-Z pair array -> (m, lo, hi)
  hook_record(...)                   explib InterventionRecord for a lens hook, with the C1 receipt's code sha

Device policy belongs to the caller: every engine call here runs on device="cpu"; under a CPU-only brief set
CUDA_VISIBLE_DEVICES=-1 before torch is imported (an EMPTY value does not hide the GPU on SKULLPORT). Unlike the
W2-F draft, importing this module asserts nothing about the GPU and sets no thread count.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

from prometheus.ananke import envs, lens, swap_rel
from prometheus.ananke.engine import Controls
from prometheus.explib import provenance
from prometheus.explib.reach import reach_certificate
from prometheus.explib.trace import DiffRecord

from . import trace as HI

COMPS = HI.COMP_BITS            # {"S": 1, "inbox": 2, "Kp": 4, "r": 8, "w": 16, "E": 32}


def record_from_difftrace(dt) -> DiffRecord:
    T = dt.T
    post = dt.site_post != 0
    held = dt.site_hook != 0
    comp_post = {c: (dt.site_post & b) != 0 for c, b in COMPS.items()}
    comp_held = {c: (dt.site_hook & b) != 0 for c, b in COMPS.items()}
    edges = dt.edges[:, :5] if dt.edges_exact else None
    return DiffRecord(held=held, inp=dt.sense, arr=dt.arr, edges=edges, post=post, hook_node=dt.hook_site,
                      hook_flight=dt.hook_arr[:T], comp_post=comp_post, comp_held=comp_held,
                      meta={"engine": "PTE", "source": "H-INST diff_trace", "edges_exact": dt.edges_exact})


def reach(ph, genome, env, seeds, hooks: dict, trial: int, ctrl=None) -> dict:
    ep = envs.build(ph, env, seeds)
    ws = HI.mirrored_ws(seeds)
    rt = ep.ro_tick[:, trial]
    T = int(rt.max()) + 1
    ctrl = ctrl or Controls()
    dt = HI.diff_trace(ph, genome, ep.schedule, ep.schedule, ws, T, hooks_b=hooks, ctrl_a=ctrl, ctrl_b=ctrl,
                       device="cpu")
    M = len(seeds)
    slot = ep.ro_slot[:, trial]
    ridx = ep.schedule.read_idx.numpy()
    ro_node = np.array([int(ridx[b, slot[b]]) for b in range(M)])
    oa = dt.traceA[rt, np.arange(M), slot]
    ob = dt.traceB[rt, np.arange(M), slot]
    out = reach_certificate(record_from_difftrace(dt), rt, ro_node, oa, ob)
    out["record"] = record_from_difftrace(dt)
    return out


def pair_table(ph, genome, env, seeds, ctrl=None, hooks=None) -> dict:
    """Scored readouts of a mirrored run: outputs [M, K] (S0 at each scored readout), targets [M, K] (+-1),
    pair [M] (mirror pair id), K = trials scored in every world."""
    tr = lens.run(ph, genome, env, seeds, hooks=hooks, device="cpu", ctrl=ctrl)
    ep = tr.ep
    M = len(seeds)
    s0 = tr.trace[ep.ro_tick, np.arange(M)[:, None], ep.ro_slot]
    keep = ep.scored.all(0)
    return {"outputs": s0[:, keep].astype(np.int64), "targets": ep.y[:, keep].astype(np.int64),
            "pair": np.arange(M) // 2}


def table_accuracy(tab: dict) -> float:
    s = np.sign(tab["outputs"])
    sc = np.where(s == 0, 0.5, (s == tab["targets"]).astype(float)).mean(-1)
    return float(sc.reshape(-1, 2).mean(-1).mean())


def zero_comm_panel(rows, family: str, kinds=("evolve", "transfer")):
    ctrl, treat = {}, {}
    for r in rows:
        h = r.get("result", {}).get("held")
        if r["env"]["family"] == family and r["kind"] in kinds and h and "zero_comm" in h:
            ctrl[r["cell_id"]] = float(h["zero_comm"])
            treat[r["cell_id"]] = float(h["acc"])
    return ctrl, treat


def lightcone_ceilings(path, family: str, topology: str | None = None) -> dict:
    rows = json.loads(pathlib.Path(path).read_text())["rows"]
    return {r["cell"]: float(r["bound"]) for r in rows
            if r["family"] == family and (topology is None or r["topology"] == topology)}


def swap_rel_ci(a, s, K: int, cert: str):
    """H2 interval (prometheus.ananke.swap_rel) of the statistic that decides `cert`: DF for FLIP_REL, DN
    for NO_EFFECT_REL, the nearer of the two for CHANCE_REL."""
    from prometheus.explib.stats import margin
    c = swap_rel.certificate(np.asarray(a, float), np.asarray(s, float), K)
    df = tuple(float(x) for x in c["DF"])
    dn = tuple(float(x) for x in c["DN"])
    if cert == "FLIP_REL":
        return df, str(c["verdict"])
    if cert == "NO_EFFECT_REL":
        return dn, str(c["verdict"])
    return min((df, dn), key=lambda t: margin(t, [0])), str(c["verdict"])


def hook_record(experiment: str, arm: str, hook, seeds, namespace: int, params=None, plan_path=None,
                plan_commit=None, kind="intervention", code_sha=None):
    return provenance.make_record(experiment=experiment, arm=arm, kind=kind, seed_namespace=namespace,
                                  seeds=seeds, hook=hook, params=params, plan_path=plan_path,
                                  plan_commit=plan_commit, code_sha=code_sha)
