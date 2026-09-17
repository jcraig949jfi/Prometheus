"""H-R5-2 / H-R6-3 / H-R7-2: the SEALED ANTI-PRIOR LEDGER, version 3 -- round-namespaced (D11).

A predictor (lane R, a separate session, never the experimenter) posts a prior per candidate cell BEFORE
assignment. Code publishes the candidate cells, so the predictor never chooses them. Priors never enter scientific
scoring.

Round 6 D11: the ledger keys were not namespaced by round, so the round 5 ledger blocked the round 6 candidate publish
(CANDIDATES_ALREADY_PUBLISHED) and A renamed keys by hand. Version 3 puts every key under the round:

    pm:prior:<round>:{sealed, commit, assign, candidates, ranks}

and every entry point takes a REQUIRED keyword round_id, so no call can reach another round's ledger by default.
candidates() refuses a redraw only within the same round. Seeds are fixed per round in SEEDS before any data
(SWARM_R6: r6 = 20260917 / 20260918; SWARM_R7: r7 = 20260919 / 20260920); a round without fixed seeds is refused.
migrate_unnamespaced(r, "r6") moves the round 6 keys (written un-namespaced by v2) with RENAMENX, never overwriting;
the round 5 archive pm:prior:r5:* is untouched.

  candidates(store, round_id=, n=48)        a seeded PCG64 draw of n distinct cells from draw_cell.axes(), ONCE per round
  seal(store, prediction, role, round_id=)  predictor-only write, once per prediction_id; sha256 commitment
  freeze_ranks(store, now, round_id=)       ONCE per round: rank by prior_p_pass desc, quantile (rank - 0.5)/n, ties by
                                            a seeded permutation (the round's candidates seed), recorded
  assign(store, exp_id, now, round_id=)     arm by PCG64([arm seed, i]) Bernoulli(0.25): calibration = top rank quartile,
                                            anti_prior = bottom; -> [{exp_id, cell}] only
  read(store, prediction_id, role, ..., round_id=)
                                            the sealed record only (R is never told arms); experimenter denied until its
                                            receipt is filed
  calibration(store, outcomes, rounds=[...]) descriptive: by arm accumulated across the rounds, per round, by rank
                                            quartile, by absolute p bucket (H-R7-3)

R8 G2 (PC 1789523009420-0): the CELL-BINDING PRE-CHECK. All four round 7 assignments failed for cell-construction
reasons (AP-01 oracle could never fire, AP-02 pressure barely bound, AP-03 zero resolving power, AP-04 pressure cannot
bind), so the predictor's confident-failure calls were never at risk. From r8 on (rounds not in LEGACY_DRAW) candidates()
walks a seeded PCG64 permutation of the whole grid and admits a cell only if binding_precheck() passes all four checks
(pressure_binds, discriminator_resolves, oracle_fires, control_differs); a rejected cell is replaced by the NEXT cell of
the same permutation, so the list -- replacements included -- is a function of the seed and this code alone. No LLM
chooses a replacement. Every rejection is kept in the record (`rejected`, with draw position and reasons) and
residue_rows()/write_residue() turn it into committed rows. r6/r7 keep the v3 draw byte-identical (already published).

  binding_precheck(cell, rules=RULES, evidence=None)
                                            -> {ok, cell, checks: {check: {ok, reasons, basis}}, reasons}; every rule runs
                                            (no short-circuit) so the residue names every defect, not just the first

REDACTION BY CONSTRUCTION: arm, rank, quantile, prior and the draw internals are conductor-only while a round is live.
assign() returns public_view() of the assignment, and public_assignment() is the only experimenter-facing reader of the
assign hash; both build the record from the PUBLIC_FIELDS whitelist, so a new conductor field cannot leak by default.

Sealing is API-level plus the commitment (round 5 PC D8), not cryptographic against direct Redis reads.
Store: any object with hget/hset/hgetall/hsetnx (+ exists/renamenx for the migration): redis.Redis(decode_responses=True).
"""
from __future__ import annotations

import hashlib
import json
import re
import time

import numpy as np

NAMES = ("sealed", "commit", "assign", "candidates", "ranks")
ROUND_RE = re.compile(r"r\d{1,3}")
SEEDS = {"r6": (20260917, 20260918),              # SWARM_R6 s0 (candidates, arm)
         "r7": (20260919, 20260920),              # SWARM_R7 s0
         "r8": (20260921, 20260922)}              # LAUNCH_R8 s5.2 (FROZEN): candidates, arm
FIELDS = ("prior_p_pass", "prior_expected_direction", "prior_expected_mechanism", "predictor_id", "prediction_ts")
N_CANDIDATES = 48
ARM_P = 0.25
TOP_Q, BOTTOM_Q = 0.25, 0.75
ARMS = ("calibration", "anti_prior")
ROLES = ("predictor", "experimenter", "conductor")
BUCKETS = (0.0, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0)
_FROM_FILE = object()


class PriorLedgerError(PermissionError):
    def __init__(self, reason: str, detail: str = ""):
        super().__init__(f"{reason}: {detail}")
        self.reason, self.detail = reason, detail


def keys(round_id: str) -> dict:
    if not isinstance(round_id, str) or not ROUND_RE.fullmatch(round_id):
        raise PriorLedgerError("ROUND_ID_INVALID", repr(round_id))
    return {n: f"pm:prior:{round_id}:{n}" for n in NAMES}


def seeds(round_id: str) -> tuple[int, int]:
    keys(round_id)
    if round_id not in SEEDS:
        raise PriorLedgerError("SEED_NOT_FIXED", f"no seeds fixed for {round_id} (SEEDS is committed before data)")
    return SEEDS[round_id]


def _canon(rec) -> str:
    return json.dumps(rec, sort_keys=True, separators=(",", ":"))


def cell_key(cell) -> str:
    return _canon(cell)


# ---------------------------------------------------------------------------------------------------------------------
# G2: the cell-binding pre-check. Rules are CODE over the cell and committed world structure; a rule returns the list of
# defects it proves (empty = it proves none). Each rule carries its round-7 evidence so a rejection is traceable.
# Measured `evidence` (a dev check's no-rows sample) is accepted by binding_precheck() for a lane's own pre-run check,
# but candidates() never passes it: the published list must be a function of the seed and this code alone.

PRECHECK_VERSION = "G2-v1"
LEGACY_DRAW = ("r6", "r7")                         # published with the v3 draw before G2; kept byte-identical
CHECKS = ("pressure_binds", "discriminator_resolves", "oracle_fires", "control_differs")
NO_OBSERVATION_READERS = frozenset({"bitset"})     # a bitset genome is a per-tick action tape (C-R6-AP-02, C-R7-AP-04)
GW_OBSERVATION_PRESSURES = frozenset({"obs_delay", "corruption"})   # graphworld Mechanics obs_delay / corrupt_rate
# graphworld metered_stream as the lanes built it (C-R6-01, C-R7-AP-01): ALPHA 2 per bit, 4 bits per digit,
# CREDIT = ALPHA*4*2 = 16 per tick; the cheapest non-empty read is one digit = 8.
GW_METERED = {"alpha": 2, "bits_per_unit": 4, "credit": 16}
# signal_world_d1 metered_stream settlement (lingua.signal.NpChannel, C-R5-01, C-R7-AP-03): alpha_int 2 per delivered
# bit, y_int 3 per right action; naming one of N_ACT = 8 actions needs 3 bits.
D1_METERED = {"alpha_int": 2, "y_int": 3, "symbol_bits": 3}
_MECH_CACHE: dict = {}


def _is_graphworld(world) -> bool:
    return bool(re.fullmatch(r"w\d+", str(world)))


def graphworld_mechanics(world: str):
    """The world's own Mechanics (qd.e4_run.Spec(gen_seed).mech), cached; None if it cannot be built."""
    if world not in _MECH_CACHE:
        try:
            from primordial.qd import e4_run as E4
            _MECH_CACHE[world] = E4.Spec(int(str(world)[1:])).mech
        except Exception:                                        # noqa: BLE001 -- unverifiable, reported as such
            _MECH_CACHE[world] = None
    return _MECH_CACHE[world]


def _r_regime_reaches_payoff(cell, evidence, mechanics):
    if cell.get("pressure") != "regime_switching" or not _is_graphworld(cell.get("world")):
        return None
    m = mechanics(cell["world"])
    if m is None:
        return [f"UNVERIFIABLE: no Mechanics for {cell['world']}, cannot show regime_switching reaches its payoff"]
    dests = sorted({int(op[0]) for op in m.lin_ops})
    if int(m.yield_reg) in dests:
        return []
    seen = sorted(set(int(x) for x in (m.obs_regs or ())) & set(dests))
    if seen and cell.get("representation") not in NO_OBSERVATION_READERS:
        return []                                  # the flip is observable, so actions (and reg yield) can depend on it
    return [f"PRESSURE_CANNOT_BIND: regime_switching on {cell['world']}: the flip negates lin_ops that write {dests}; "
            f"yield reg {int(m.yield_reg)} is written only by actions {list(m.act_targets)}"
            + ("" if not seen else f" and {cell.get('representation')} reads no observation")
            + " -- no genome's charge can differ (C-R7-AP-04)"]


def _r_observation_pressure_needs_reader(cell, evidence, mechanics):
    if cell.get("pressure") not in GW_OBSERVATION_PRESSURES or not _is_graphworld(cell.get("world")):
        return None
    if cell.get("representation") in NO_OBSERVATION_READERS:
        return [f"CONTROL_IDENTICAL: {cell['pressure']} acts on observations and {cell['representation']} reads none; "
                "the arm and its control are the same experiment (C-R6-AP-02)"]
    return []


def _r_intervention_nonzero(cell, evidence, mechanics):
    if not evidence or "intervention_magnitude" not in evidence:
        return None
    mag = evidence["intervention_magnitude"]
    return [] if mag else [f"CONTROL_IDENTICAL: measured intervention magnitude {mag!r} (C-R7-AP-03 dev check: BETA "
                           "rounded to 0)"]


def _r_gw_meter_eligibility(cell, evidence, mechanics):
    if cell.get("channel") != "metered_stream" or not _is_graphworld(cell.get("world")):
        return None
    g = GW_METERED
    cheapest = g["alpha"] * g["bits_per_unit"]
    if cheapest <= g["credit"]:
        return [f"ORACLE_CANNOT_FIRE: the meter oracle needs a free-stream eligible episode, but the cheapest read costs "
                f"{cheapest} <= credit {g['credit']} per tick, so a winner can make the meter never bind and the oracle "
                "never fire (C-R7-AP-01, C-R6-01)"]
    return []


def _r_oracle_measured(cell, evidence, mechanics):
    if not evidence or "oracle_eligible" not in evidence:
        return None
    n = int(evidence["oracle_eligible"])
    return [] if n > 0 else [f"ORACLE_CANNOT_FIRE: measured oracle eligibility {n}"]


def _r_d1_signal_pays(cell, evidence, mechanics):
    if cell.get("channel") != "metered_stream" or cell.get("world") != "signal_world_d1":
        return None
    d = D1_METERED
    cost = d["alpha_int"] * d["symbol_bits"]
    if cost >= d["y_int"]:
        return [f"ZERO_RESOLVING_POWER: on signal_world_d1 a {d['symbol_bits']}-bit send costs {cost} >= the {d['y_int']} a "
                "right action earns, so signalling never pays, every winner settles on the silent attractor and the "
                "reader is pinned in both arms (C-R7-AP-03: 64/64 runs = 31.71875, IQR 0)"]
    return []


def _r_null_sample_resolves(cell, evidence, mechanics):
    if not evidence or "null_samples" not in evidence:
        return None
    arms = evidence["null_samples"]
    values = [float(v) for vs in arms.values() for v in vs]
    if not values:
        return ["ZERO_RESOLVING_POWER: empty null sample"]
    if len(set(values)) == 1:
        return [f"ZERO_RESOLVING_POWER: all {len(values)} null-sample values in {sorted(arms)} equal {values[0]!r} "
                "(IQR 0): a PASS here is vacuous (C-R7-AP-03)"]
    return []


RULES = (("pressure_binds", "regime_reaches_payoff", _r_regime_reaches_payoff),
         ("discriminator_resolves", "d1_signal_pays", _r_d1_signal_pays),
         ("discriminator_resolves", "null_sample_resolves", _r_null_sample_resolves),
         ("oracle_fires", "gw_meter_eligibility", _r_gw_meter_eligibility),
         ("oracle_fires", "oracle_measured", _r_oracle_measured),
         ("control_differs", "observation_pressure_needs_reader", _r_observation_pressure_needs_reader),
         ("control_differs", "intervention_nonzero", _r_intervention_nonzero))


def binding_precheck(cell: dict, *, rules=RULES, evidence: dict | None = None, mechanics=None) -> dict:
    """Run EVERY rule (no short-circuit). A check fails if any of its rules proves a defect; `basis` names the rules that
    applied to this cell (empty = no rule applies, recorded as such, never silently read as proof)."""
    mechanics = graphworld_mechanics if mechanics is None else mechanics
    checks = {c: {"ok": True, "reasons": [], "basis": []} for c in CHECKS}
    for check, name, fn in rules:
        if check not in checks:
            raise PriorLedgerError("PRECHECK_UNKNOWN_CHECK", f"{name}: {check!r}")
        out = fn(cell, evidence, mechanics)
        if out is None:
            continue
        checks[check]["basis"].append(name)
        if out:
            checks[check]["ok"] = False
            checks[check]["reasons"].extend(out)
    reasons = [f"{c}:{x}" for c in CHECKS for x in checks[c]["reasons"]]
    return {"ok": not reasons, "cell": cell, "version": PRECHECK_VERSION, "checks": checks, "reasons": reasons}


def candidates(store, *, round_id: str, seed: int | None = None, n: int = N_CANDIDATES, now: float | None = None,
               grid: dict | None = None, doc=_FROM_FILE, rules=RULES, mechanics=None) -> dict:
    """Publish the round's candidate cell list once, by seeded draw over the draw grid. From r8 on every cell passes
    binding_precheck() before it enters the list; a rejected cell is replaced by the next cell of the seeded
    permutation and kept, with its reasons, in record["rejected"]."""
    k = keys(round_id)
    seed = seeds(round_id)[0] if seed is None else int(seed)
    if store.hget(k["candidates"], "record") is not None:
        raise PriorLedgerError("CANDIDATES_ALREADY_PUBLISHED", f"the {round_id} candidate list is drawn once")
    record = draw_candidates(round_id=round_id, seed=seed, n=n, now=now, grid=grid, doc=doc, rules=rules,
                             mechanics=mechanics)
    if not store.hsetnx(k["candidates"], "record", _canon(record)):
        raise PriorLedgerError("CANDIDATES_ALREADY_PUBLISHED", f"the {round_id} candidate list is drawn once")
    return record


def draw_candidates(*, round_id: str, seed: int | None = None, n: int = N_CANDIDATES, now: float | None = None,
                    grid: dict | None = None, doc=_FROM_FILE, rules=RULES, mechanics=None) -> dict:
    """The pure draw behind candidates(): no store, no write. Same seed + same code -> the same record (bar `ts`)."""
    keys(round_id)
    seed = seeds(round_id)[0] if seed is None else int(seed)
    if grid is None:
        from primordial.ops import draw_cell as DC
        grid = DC.axes() if doc is _FROM_FILE else DC.axes(doc)
    names = list(grid)
    sizes = [len(grid[x]) for x in names]
    n_cells = int(np.prod(sizes))
    if n_cells == 0:
        raise PriorLedgerError("EMPTY_GRID", "the draw grid has no cells")
    rng = np.random.Generator(np.random.PCG64(seed))
    ts = round(time.time() if now is None else float(now), 3)

    def at(f):
        return {x: grid[x][int(i)] for x, i in zip(names, np.unravel_index(int(f), sizes))}

    if round_id in LEGACY_DRAW:
        flats = sorted(rng.choice(n_cells, size=min(int(n), n_cells), replace=False).tolist())
        cells = [at(f) for f in flats]
        return {"round": round_id, "seed": seed, "ts": ts, "n": len(cells), "grid_cells": n_cells, "cells": cells}
    want = min(int(n), n_cells)
    cells, positions, rejected, examined = [], [], [], 0
    for pos, f in enumerate(rng.permutation(n_cells).tolist()):
        if len(cells) >= want:
            break
        examined = pos + 1
        c = at(f)
        pc = binding_precheck(c, rules=rules, mechanics=mechanics)
        if pc["ok"]:
            cells.append(c)
            positions.append(pos)
        else:
            rejected.append({"draw_position": pos, "flat": int(f), "cell": c, "reasons": pc["reasons"],
                             "failed_checks": [x for x in CHECKS if not pc["checks"][x]["ok"]]})
    if not cells:
        raise PriorLedgerError("EMPTY_POOL", f"all {examined} cells of the grid failed the binding pre-check")
    return {"round": round_id, "seed": seed, "ts": ts, "n": len(cells), "grid_cells": n_cells, "cells": cells,
            "draw": "pcg64_permutation_with_binding_precheck", "precheck": PRECHECK_VERSION,
            "rules": [name for _, name, _ in rules], "positions": positions, "examined": examined,
            "short": len(cells) < want, "rejected": rejected}


RESIDUE_DIR = ("primordial", "ledger", "prior")


def residue_rows(record: dict) -> list[dict]:
    """The rejected set as analysable rows: one summary row, then one row per rejected cell. No prior, arm, rank or
    quantile exists at publication time, so nothing here needs redaction."""
    if record.get("precheck") is None:
        raise PriorLedgerError("NO_PRECHECK", f"{record.get('round')} was drawn without the binding pre-check")
    head = {"kind": "anti_prior_precheck_summary", "round": record["round"], "seed": record["seed"],
            "precheck": record["precheck"], "rules": record["rules"], "grid_cells": record["grid_cells"],
            "examined": record["examined"], "admitted": record["n"], "rejected": len(record["rejected"]),
            "short": record["short"], "by_check": {c: sum(c in r["failed_checks"] for r in record["rejected"])
                                                   for c in CHECKS}}
    return [head] + [{"kind": "anti_prior_precheck_rejection", "round": record["round"], **r}
                     for r in record["rejected"]]


def write_residue(record: dict, path=None) -> str:
    """Commit the rejected set (RowWriter commits on close). Called by the conductor at publication."""
    import pathlib
    from primordial.fabric.rows import RowWriter
    root = pathlib.Path(__file__).resolve().parents[2]
    path = root.joinpath(*RESIDUE_DIR, f"{record['round']}-candidates-precheck.jsonl") if path is None else path
    with RowWriter(path, f"anti-prior-precheck-{record['round']}", commit_every_s=10**9) as w:
        for row in residue_rows(record):
            w.write(row)
    return str(path)


def published(store, *, round_id: str) -> dict | None:
    body = store.hget(keys(round_id)["candidates"], "record")
    return None if body is None else json.loads(body)


def seal(store, prediction: dict, writer_role: str, *, round_id: str, experimenter_ids=()) -> str:
    k = keys(round_id)
    if writer_role != "predictor":
        raise PriorLedgerError("WRITE_DENIED", f"role {writer_role!r} may not write priors")
    if prediction.get("predictor_id") in set(experimenter_ids):
        raise PriorLedgerError("WRITE_DENIED", "the predictor must not be an experimenter")
    missing = [f for f in FIELDS + ("prediction_id", "cell") if prediction.get(f) in (None, "")]
    if missing:
        raise PriorLedgerError("FIELD_MISSING", str(missing))
    p = prediction["prior_p_pass"]
    if isinstance(p, bool) or not isinstance(p, (int, float)) or not 0.0 <= float(p) <= 1.0:
        raise PriorLedgerError("P_OUT_OF_RANGE", repr(p))
    rec = {x: prediction[x] for x in FIELDS + ("prediction_id", "cell")}
    rec["prior_p_pass"], rec["prediction_ts"] = float(p), float(rec["prediction_ts"])
    body = _canon(rec)
    if not store.hsetnx(k["sealed"], rec["prediction_id"], body):
        raise PriorLedgerError("ALREADY_SEALED", rec["prediction_id"])
    digest = hashlib.sha256(body.encode()).hexdigest()
    store.hset(k["commit"], rec["prediction_id"], digest)
    return digest


def verify(store, prediction_id: str, *, round_id: str) -> bool:
    k = keys(round_id)
    body = store.hget(k["sealed"], prediction_id)
    return body is not None and hashlib.sha256(body.encode()).hexdigest() == store.hget(k["commit"], prediction_id)


def _all(store, round_id: str) -> list[dict]:
    return [json.loads(v) for _, v in sorted(store.hgetall(keys(round_id)["sealed"]).items())]


def freeze_ranks(store, now: float, *, round_id: str, tie_seed: int | None = None) -> dict:
    k = keys(round_id)
    body = store.hget(k["ranks"], "record")
    if body is not None:
        return json.loads(body)
    pub = published(store, round_id=round_id)
    if pub is None:
        raise PriorLedgerError("CANDIDATES_NOT_PUBLISHED", f"publish the {round_id} candidate cells first")
    listed = {cell_key(c) for c in pub["cells"]}
    preds = sorted((p for p in _all(store, round_id) if p["prediction_ts"] < now and cell_key(p["cell"]) in listed
                    and verify(store, p["prediction_id"], round_id=round_id)), key=lambda p: p["prediction_id"])
    if not preds:
        raise PriorLedgerError("NO_PREDICTIONS", "no sealed prediction on a published cell before the freeze")
    tie_seed = int(pub["seed"] if tie_seed is None else tie_seed)
    perm = np.random.Generator(np.random.PCG64(tie_seed)).permutation(len(preds)).tolist()
    tie_break = {p["prediction_id"]: int(perm[i]) for i, p in enumerate(preds)}
    order = sorted(preds, key=lambda p: (-p["prior_p_pass"], tie_break[p["prediction_id"]]))
    n = len(order)
    ranks = {p["prediction_id"]: {"rank": i + 1, "quantile": (i + 0.5) / n, "prior_p_pass": p["prior_p_pass"],
                                  "tie_break": tie_break[p["prediction_id"]]} for i, p in enumerate(order)}
    groups: dict[float, list[str]] = {}
    for p in order:
        groups.setdefault(p["prior_p_pass"], []).append(p["prediction_id"])
    record = {"round": round_id, "ts": float(now), "n": n, "tie_seed": tie_seed, "ranks": ranks,
              "ties": [{"prior_p_pass": pv, "order": ids} for pv, ids in groups.items() if len(ids) > 1]}
    if not store.hsetnx(k["ranks"], "record", _canon(record)):
        return json.loads(store.hget(k["ranks"], "record"))
    return record


def arm_of(index: int, arm_seed: int, p: float = ARM_P) -> tuple[str, float]:
    u = float(np.random.Generator(np.random.PCG64([int(arm_seed), int(index)])).random())
    return ("calibration" if u < p else "anti_prior"), u


def assign(store, exp_id: str, now: float, *, round_id: str, arm_seed: int | None = None, p: float = ARM_P) -> list[dict]:
    k = keys(round_id)
    arm_seed = seeds(round_id)[1] if arm_seed is None else int(arm_seed)
    if store.hget(k["assign"], exp_id) is not None:
        raise PriorLedgerError("ALREADY_ASSIGNED", exp_id)
    ranks = freeze_ranks(store, now, round_id=round_id)
    existing = [json.loads(v) for v in store.hgetall(k["assign"]).values()]
    index = len(existing)
    arm, u = arm_of(index, arm_seed, p)
    taken = {a["prediction_id"] for a in existing}
    in_arm = (lambda q: q < TOP_Q) if arm == "calibration" else (lambda q: q > BOTTOM_Q)
    pool = sorted((pid for pid, rk in ranks["ranks"].items() if in_arm(rk["quantile"]) and pid not in taken
                   and verify(store, pid, round_id=round_id)), key=lambda pid: ranks["ranks"][pid]["rank"])
    if not pool:
        return []
    pick = pool[int(np.random.Generator(np.random.PCG64([arm_seed, index, 1])).integers(len(pool)))]
    pred = json.loads(store.hget(k["sealed"], pick))
    rk = ranks["ranks"][pick]
    full = {"round": round_id, "prediction_id": pick, "cell": pred["cell"], "assignment_ts": float(now),
            "arm_seed": arm_seed, "index": index, "u": u, "arm": arm, "rank": rk["rank"], "quantile": rk["quantile"]}
    store.hset(k["assign"], exp_id, _canon(full))
    return [public_view({"exp_id": exp_id, **full})]


# Redaction by construction: experimenter-readable assignment records are BUILT from this whitelist, never filtered from
# the conductor record, so a field added to the conductor record later stays conductor-only unless listed here.
PUBLIC_FIELDS = ("exp_id", "round", "cell")
CONDUCTOR_ONLY = ("arm", "rank", "quantile", "prior_p_pass", "u", "index", "arm_seed", "tie_break", "prediction_id",
                  "prior_expected_direction", "prior_expected_mechanism")


def public_view(rec: dict) -> dict:
    out = {f: rec[f] for f in PUBLIC_FIELDS if f in rec}
    leaked = sorted(set(out.get("cell") or {}) & set(CONDUCTOR_ONLY))
    if leaked:
        raise PriorLedgerError("REDACTION_LEAK", f"cell carries conductor-only fields {leaked}")
    return out


def public_assignment(store, exp_id: str, *, round_id: str) -> dict:
    """The experimenter-facing read of an assignment: exp_id, round and cell only."""
    body = store.hget(keys(round_id)["assign"], exp_id)
    if body is None:
        raise PriorLedgerError("NOT_FOUND", exp_id)
    return public_view({"exp_id": exp_id, **json.loads(body)})


def eligible_at(prediction: dict, assignment_ts: float) -> None:
    if not float(prediction["prediction_ts"]) < float(assignment_ts):
        raise PriorLedgerError("PREDICTION_NOT_BEFORE_ASSIGNMENT",
                               f"{prediction['prediction_ts']} >= {assignment_ts}")


def read(store, prediction_id: str, reader_role: str, receipt_filed=lambda exp_id: False, *, round_id: str,
         round_live: bool = True) -> dict:
    """The sealed prior. The experimenter is denied while the round is live (R8: prior is conductor-only while live) and,
    after close, until every assignment on the prediction has a filed receipt. round_live defaults to True: fail closed."""
    k = keys(round_id)
    if reader_role not in ROLES:
        raise PriorLedgerError("READ_DENIED", f"unknown role {reader_role!r}")
    body = store.hget(k["sealed"], prediction_id)
    if body is None:
        raise PriorLedgerError("NOT_FOUND", prediction_id)
    if reader_role == "experimenter" and round_live:
        raise PriorLedgerError("EXPERIMENTER_READ_DENIED", f"{round_id} is live: the prior is conductor-only")
    if reader_role == "experimenter":
        exps = [e for e, v in store.hgetall(k["assign"]).items() if json.loads(v)["prediction_id"] == prediction_id]
        if not exps or not all(receipt_filed(e) for e in exps):
            raise PriorLedgerError("EXPERIMENTER_READ_DENIED", f"no filed receipt for {exps or 'an assignment'}")
    return json.loads(body)


def migrate_unnamespaced(r, round_id: str) -> dict:
    """D11: move the un-namespaced v2 keys pm:prior:<name> to pm:prior:<round_id>:<name> by RENAMENX (never overwrite).
    -> {moved, skipped (no source), conflict (destination exists; nothing moved)}. pm:prior:r5:* is never read."""
    k = keys(round_id)
    out = {"round": round_id, "moved": [], "skipped": [], "conflict": []}
    for name in NAMES:
        src = f"pm:prior:{name}"
        if not r.exists(src):
            out["skipped"].append(src)
        elif r.exists(k[name]) or not r.renamenx(src, k[name]):
            out["conflict"].append(src)
        else:
            out["moved"].append([src, k[name]])
    return out


def _stats(ps, hits, quantiles=None) -> dict:
    if not ps:
        return {"n": 0}
    pr, hit = np.array(ps), np.array(hits)
    out = {"n": len(ps), "mean_prior": round(float(pr.mean()), 4), "pass_rate": round(float(hit.mean()), 4),
           "brier": round(float(((pr - hit) ** 2).mean()), 4)}
    if quantiles:
        out["mean_quantile"] = round(float(np.mean(quantiles)), 4)
    return out


def calibration(store, outcomes: dict, *, rounds: list[str]) -> dict:
    """outcomes: {round_id: {prediction_id: True (PASS) | False}}. Descriptive only (H-R7-3): by arm accumulated across
    `rounds`, per round by arm, by rank quartile and by absolute p bucket."""
    pooled = {arm: ([], [], []) for arm in ARMS}
    per_round, quart, bucket_rows = {}, {q: ([], [], []) for q in ("top", "middle", "bottom")}, []
    all_ps, all_hits = [], []
    for rid in rounds:
        k = keys(rid)
        sealed = {p["prediction_id"]: p for p in _all(store, rid)}
        out_r = {pid: v for pid, v in (outcomes.get(rid) or {}).items() if pid in sealed}
        body = store.hget(k["ranks"], "record")
        ranks = json.loads(body)["ranks"] if body else {}
        assigned = [json.loads(v) for v in store.hgetall(k["assign"]).values()]
        per_arm = {}
        for arm in ARMS:
            ids = [a["prediction_id"] for a in assigned if a.get("arm") == arm and a["prediction_id"] in out_r]
            ps = [sealed[i]["prior_p_pass"] for i in ids]
            hits = [1.0 if out_r[i] else 0.0 for i in ids]
            qs = [ranks[i]["quantile"] for i in ids if i in ranks]
            per_arm[arm] = _stats(ps, hits, qs)
            pooled[arm][0].extend(ps), pooled[arm][1].extend(hits), pooled[arm][2].extend(qs)
        per_round[rid] = per_arm
        for i, v in out_r.items():
            all_ps.append(sealed[i]["prior_p_pass"])
            all_hits.append(1.0 if v else 0.0)
            if i in ranks:
                q = ranks[i]["quantile"]
                name = "top" if q < TOP_Q else ("bottom" if q > BOTTOM_Q else "middle")
                quart[name][0].append(sealed[i]["prior_p_pass"]), quart[name][1].append(1.0 if v else 0.0)
                quart[name][2].append(q)
    for lo, hi in zip(BUCKETS, BUCKETS[1:]):
        idx = [j for j, pv in enumerate(all_ps) if lo <= pv < hi or (hi == 1.0 and pv == 1.0)]
        bucket_rows.append({"bucket": [lo, hi], **_stats([all_ps[j] for j in idx], [all_hits[j] for j in idx])})
    return {"kind": "anti_prior_calibration", "version": 3, "rounds": list(rounds), "descriptive_only": True,
            "n": len(all_ps), "by_arm": {arm: _stats(*pooled[arm]) for arm in ARMS}, "per_round": per_round,
            "by_quartile": {q: _stats(*v) for q, v in quart.items()}, "buckets": bucket_rows,
            "note": "small N: no inference (prompt 19 s11)"}
