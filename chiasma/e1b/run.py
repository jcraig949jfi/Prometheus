"""One E1b run. Same scoring and endpoints as chiasma.runner.run (E1, frozen), with the
world family's stream/probes and the E1b arm factory passed in.

tests/test_e1b.py checks that this function reproduces chiasma.runner.run's endpoints
byte for byte on PW-H, so the two cannot drift apart silently.
"""
import hashlib
from typing import Dict, Optional

from ..runner import CK, _score, canonical
from ..world import PHASES, probes, stream
from . import arms
from .world_d import WorldD, probes_d, stream_d
from .world_h3 import WorldH3, probes_h3, stream_h3


def world_fns(w):
    if isinstance(w, WorldD):
        return stream_d, probes_d, "PW-D"
    if isinstance(w, WorldH3):
        return stream_h3, probes_h3, "PW-H3"
    return stream, probes, "PW-H"


def run(w, arm: str, cap: Optional[int], org_seed: int = 0, pevict: bool = False) -> Dict:
    stream_fn, probes_fn, family = world_fns(w)
    org = arms.make(arm, w.spec.m, cap, org_seed, pevict)
    prb = probes_fn(w)
    cps, bytes_end, ops_phase, events_phase = [], {}, {p: 0 for p in PHASES}, {}
    last_phase, ops_mark = None, 0
    for t, phase, x in stream_fn(w):
        if last_phase is not None and phase != last_phase:
            bytes_end[last_phase] = org.nbytes()
            ops_phase[last_phase] = org.ops - ops_mark
            ops_mark = org.ops
            events_phase[last_phase] = dict(org.events)
        last_phase = phase
        org.observe(x, w.observe(x, phase))
        if (t + 1) % CK == 0:
            s = _score(org, w, prb, phase)
            cps.append({"t": t + 1, "phase": phase, "bytes": org.nbytes()["total"], **s})
    bytes_end[last_phase] = org.nbytes()
    ops_phase[last_phase] = org.ops - ops_mark
    events_phase[last_phase] = dict(org.events)

    def errsum(phases, keys):
        return sum(cp["err"][k] for cp in cps if cp["phase"] in phases for k in keys)

    core = ["{}:{}".format(g, f) for g in ("ydep", "decoy", "unrel", "invalid") for f in ("rand", "crit")]
    CDE = ("C", "D", "E")

    def settle(phases, keys, start_phase):
        seq = [cp for cp in cps if cp["phase"] in phases]
        start = next(cp["t"] for cp in cps if cp["phase"] == start_phase) - CK
        for i, cp in enumerate(seq):
            if all(sum(c["err"][k] for k in keys) == 0 for c in seq[i:]):
                return cp["t"] - start
        return "NOT_RECOVERED"

    last_B = [cp for cp in cps if cp["phase"] == "B"][-1]

    def newly_broken(keys):
        return sum(max(0, cp["err"][k] - last_B["err"][k])
                   for cp in cps if cp["phase"] in CDE for k in keys)

    endpoints = {
        "bet_B": sum(last_B["err"][k] for k in core),
        "bet_B_ydep_crit": last_B["err"]["ydep:crit"],
        "bet_B_decoy_crit": last_B["err"]["decoy:crit"],
        "err_CDE": errsum(CDE, core),
        "revise_DE": errsum(("D", "E"), core),
        "ydep_crit_CDE": errsum(CDE, ["ydep:crit"]),
        "decoy_CDE": errsum(CDE, ["decoy:rand", "decoy:crit"]),
        "collateral_CDE": newly_broken(["decoy:rand", "decoy:crit", "unrel:rand", "unrel:crit",
                                        "invalid:rand", "invalid:crit"]),
        "unrel_CDE": errsum(CDE, ["unrel:rand", "unrel:crit", "invalid:rand", "invalid:crit"]),
        "recovery_obs": settle(CDE, ["ydep:crit", "decoy:crit"], "C"),
        "insert_F": errsum(("F",), ["new:rand", "new:crit"]),
        "insert_obs": settle(("F",), ["new:rand", "new:crit"], "F"),
        "bytes_end": bytes_end,
        "bytes_peak": max(cp["bytes"] for cp in cps),
        "ops_phase": ops_phase,
        "ops_total": sum(ops_phase.values()),
        "events_phase": events_phase,
    }
    receipt = {
        "schema": "chiasma.e1.run.v1" if family == "PW-H" and not pevict else "chiasma.e1b.run.v1",
        "arm": arm, "cap": cap if cap is not None and arm not in arms.UNCAPPED else "NONE",
        "org_seed": org_seed,
        **({"pevict": True} if pevict else {}),
        "world": {"family": family, "seed": w.seed, "spec": w.spec.as_dict()},
        "world_sha256": hashlib.sha256(canonical(w.describe())).hexdigest(),
        "endpoints": endpoints,
        "summary": org.summary(),
        "checkpoints": cps,
    }
    receipt["receipt_sha256"] = hashlib.sha256(canonical(receipt)).hexdigest()
    return receipt
