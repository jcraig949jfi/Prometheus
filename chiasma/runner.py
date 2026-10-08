"""Run one organism through one Paradigm World and return an integer-only receipt.

Checkpoint every CK observations: every probe object is scored against the world's
truth for each target active in the current phase (INVALID only, for invalid
probes). Errors are counted per (group, family), where family is 'rand' for the
unconstrained probes and 'crit' for the c & not-f probes of a ydep/decoy/new target.
Ops spent answering probes are measured separately (qops) and are not charged to
learning.

Derived endpoints (all integers or "NOT_RECOVERED"; ratios as "n/d" strings):
  err_CDE         total probe errors summed over checkpoints in phases C, D, E
                  (groups ydep, decoy, unrel, invalid; both families)
  ydep_crit_CDE   the ydep crit share of that sum (the false-foundation region)
  decoy_CDE       decoy errors over C-E (collateral: knowledge that should survive)
  unrel_CDE       unrel + invalid errors over C-E (forgetting of unrelated knowledge)
  bet_B           probe errors at the last B checkpoint: the pre-shock bet (A/B data
                  cannot tell whether f is needed; every arm must bet)
  revise_DE       errors over D and E (after the decisive falsifier)
  collateral_CDE  errors above the end-of-B level on decoy, unrel and invalid targets,
                  summed over C-E: knowledge that was right before the shock and broke
  recovery_obs    observations from the start of C (first exceptions) until ydep AND
                  decoy crit errors reach 0 and stay 0 at every later checkpoint of C-E
  events_phase    cumulative event counters at the end of each phase (structural
                  change: welds, new cells, retractions, repairs, seam openings)
  insert_F        new-group errors summed over F checkpoints (insertion cost, in errors)
  insert_obs      observations into F until new-group errors reach 0 and stay 0 in F
  bytes_end       bytes (P, N, U, total) at the end of each phase
  ops_phase       learning ops per phase
"""
import hashlib
import json
from typing import Dict, Optional

from . import organisms
from .world import World, probes, stream, PHASES

CK = 100
GROUPS = ("ydep", "decoy", "unrel", "invalid", "new")


def canonical(obj) -> bytes:
    def check(o):
        if isinstance(o, float):
            raise TypeError("floats are refused in receipts")
        if isinstance(o, dict):
            for v in o.values():
                check(v)
        elif isinstance(o, (list, tuple)):
            for v in o:
                check(v)
    check(obj)
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _score(org, w: World, prb, phase: str) -> Dict[str, int]:
    active = w.active(phase)
    by_name = {t.name: t for t in active}
    errs = {"{}:{}".format(g, f): 0 for g in GROUPS for f in ("rand", "crit")}
    tot = dict(errs)
    q0 = org.ops
    for fam, x in prb:
        if fam.startswith("crit:"):
            tname = fam[5:]
            if tname not in by_name:
                continue
            ts, f = [by_name[tname]], "crit"
        else:
            ts, f = ([w.invalid] if w.invalid.holds(x) else active), "rand"
        for t in ts:
            key = "{}:{}".format(t.group, f)
            tot[key] += 1
            if org.predict(x, t.name) != int(t.holds(x)):
                errs[key] += 1
    qops = org.ops - q0
    org.ops = q0                      # query ops are reported, not charged to learning
    return {"err": errs, "n": tot, "qops": qops}


def run(w: World, arm: str, cap: Optional[int], org_seed: int = 0) -> Dict:
    org = organisms.make(arm, w.spec.m, cap, org_seed)
    prb = probes(w)
    cps, bytes_end, ops_phase, events_phase = [], {}, {p: 0 for p in PHASES}, {}
    last_phase, ops_mark = None, 0
    for t, phase, x in stream(w):
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
        """Errors above the end-of-B level, summed over C-E checkpoints: knowledge that
        was right before the shock and broke during it (the pre-shock bet excluded)."""
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
        "schema": "chiasma.e1.run.v1",
        "arm": arm, "cap": cap if cap is not None else "NONE", "org_seed": org_seed,
        "world": {"family": "PW-H", "seed": w.seed, "spec": w.spec.as_dict()},
        "world_sha256": hashlib.sha256(canonical(w.describe())).hexdigest(),
        "endpoints": endpoints,
        "summary": org.summary(),
        "checkpoints": cps,
    }
    receipt["receipt_sha256"] = hashlib.sha256(canonical(receipt)).hexdigest()
    return receipt
