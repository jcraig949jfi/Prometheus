"""PTE-C1b: adjudicate M2 (delay-line HOLD memory) and M3 (MAJ), as frozen
in roles/Ananke/pte/PREREG_PTE_C1b.md (v1, 9b6e4bb95).

This module holds the batteries (s3, s4), the mechanical labels as
first-match decision lists with their exhaustive tables (s3, s4), and the
known-answer fixtures on hand plants (s5). Running a battery on an evolved
specimen is a C1b RUN and waits for the HOLD release; the fixtures touch
only hand plants.
"""
from __future__ import annotations

import dataclasses
import hashlib
import itertools

import numpy as np

from . import assays, envs, plants
from .engine import Controls, World
from .physics import Physics

HELD_NS = 0xC1B0        # C1b held-out worlds (PREREG s6)
SEARCH_NS = 0xC1B5      # C1b fresh-seed searches (PREREG s6)
DEV_NS = 0xDE7          # fixtures only (hand plants)
H_WORLDS = 64

KILL_HI = 0.60          # "kills": hi99 <= 0.60
DROP_PT = 0.10          # "drops": point drop >= 0.10 ...
DROP_LO = -0.05         # ... and lo99 of the difference < -0.05
INTACT_LO = -0.10       # "intact": lo99 of (acc - normal) >= -0.10
C1_INTACT_LO = 0.62     # H-M3-0: C1's window leaves the cell at lo99 >= 0.62
PRED_LO = 0.60          # census predictors: lo99 > 0.60 and permutation p < 0.01
PERM_P = 0.01
N_PERM = 2000


# ------------------------------------------------------------ evaluation
@dataclasses.dataclass
class Run:
    acc: np.ndarray        # [M] per-world accuracy on the scored trials
    pairs: np.ndarray      # [M/2]
    trace: np.ndarray      # [T, M, 1]
    tel: dict              # census arrays [T, M]
    digests: list
    ep: envs.Episode


def evaluate(ph: Physics, genome: np.ndarray, env: envs.EnvSpec, seeds: list[int],
             ctrl: Controls | None = None, device="cpu", from_trial: int = 0) -> Run:
    """One genome on mirror-paired worlds, with census telemetry. Trials
    before `from_trial` are not scored (the ITI-flush sham scores only the
    trials that follow a flush)."""
    M = len(seeds)
    assert M % 2 == 0
    ws = [seeds[m - (m % 2)] for m in range(M)]
    ep = envs.build(ph, env, seeds)
    g = np.repeat(genome[None], M, axis=0)
    w = World(ph, g, ws, device=device, ctrl=ctrl, schedule=ep.schedule, census=True)
    w.run(env.T(), graph=device == "cuda")
    trace = w.trace.cpu().numpy()
    scored = ep.scored.copy()
    scored[:, :from_trial] = False
    ep2 = envs.Episode(ep.schedule, ep.ro_tick, ep.ro_slot, ep.y, scored, ep.meta)
    acc = envs.score(ep2, trace)
    tel = {k: v.cpu().numpy() for k, v in w.tel.items() if k.startswith("c_")}
    dg = []
    for i, d in enumerate(w.digest(per_world=True)):
        h = hashlib.sha256(d.encode())
        h.update(trace[:, i].tobytes())
        dg.append(h.hexdigest()[:16])
    return Run(acc, acc.reshape(M // 2, 2).mean(-1), trace, tel, dg, ep2)


def ci(pairs: np.ndarray):
    m, lo, hi = assays.pair_ci(pairs)
    return float(m), float(lo), float(hi)


# ------------------------------------------------------------ tick windows
def ticks(env: envs.EnvSpec) -> dict:
    """Per-trial tick lists, one entry per trial. ro = the readout tick."""
    Pd = env.period()
    out = {k: [] for k in ("t0", "ro", "mid", "late", "iti")}
    for k in range(env.trials):
        t0 = k * Pd
        if env.family == "HOLD":
            ro = t0 + env.cue_len + env.gap
            mid = t0 + env.cue_len + env.gap // 2
        else:
            ro = t0 + env.delta
            mid = t0 + env.cue_len + max(1, (env.delta - env.cue_len) // 2)
        out["t0"].append(t0)
        out["ro"].append(ro)
        out["mid"].append(mid)
        out["late"].append(ro - 1)
        out["iti"].append(ro + 1)
    return out


def drop_windows(env: envs.EnvSpec) -> dict:
    tk = ticks(env)
    return {
        "drop_window_c1": tuple(t for t0, ro in zip(tk["t0"], tk["ro"]) for t in range(t0, ro)),
        "drop_window_corrected": tuple(t for t0, ro in zip(tk["t0"], tk["ro"])
                                       for t in range(t0, ro + 1)),
        "drop_readout_tick_only": tuple(tk["ro"]),
    }


# ------------------------------------------------------------ batteries
def m2_battery(ph: Physics, env: envs.EnvSpec) -> dict:
    """name -> (physics, Controls, from_trial). PREREG s3."""
    tk = ticks(env)
    mid = tuple(tk["mid"])

    def reset(*parts):
        return Controls(reset_state_at=mid, reset_parts=tuple(parts))
    bat = {
        "normal": (ph, Controls(), 0),
        "normal_from1": (ph, Controls(), 1),
        "reset_S": (ph, reset("S"), 0),
        "reset_inbox": (ph, reset("inbox"), 0),
        "reset_Kp": (ph, reset("Kp"), 0),
        "reset_w": (ph, reset("w"), 0),
        "reset_En": (ph, reset("En"), 0),
        "reset_all_nonpacket": (ph, reset("S", "inbox", "Kp", "w", "En"), 0),
        "flush_inflight": (ph, Controls(flush_inflight_at=mid), 0),
        "flush_inflight_late": (ph, Controls(flush_inflight_at=tuple(tk["late"])), 0),
        "flush_inflight_iti": (ph, Controls(flush_inflight_at=tuple(tk["iti"])), 1),
        "drop_window_corrected": (ph, Controls(drop_packets_at=drop_windows(env)["drop_window_corrected"]), 0),
        "zero_comm": (ph, Controls(zero_comm=True), 0),
        "randomize_payload": (ph, Controls(randomize_payload=True), 0),
        "shuffle_time": (ph, Controls(shuffle_time=True), 0),
    }
    return bat


def m3_battery(ph: Physics, env: envs.EnvSpec) -> dict:
    """PREREG s4. WIMM and mut_site arms are NOT_APPLICABLE by physics (D-C)
    and are not built."""
    dw = drop_windows(env)
    return {
        "normal": (ph, Controls(), 0),
        "drop_window_c1": (ph, Controls(drop_packets_at=dw["drop_window_c1"]), 0),
        "drop_window_corrected": (ph, Controls(drop_packets_at=dw["drop_window_corrected"]), 0),
        "drop_readout_tick_only": (ph, Controls(drop_packets_at=dw["drop_readout_tick_only"]), 0),
        "freeze_rule": (ph, Controls(freeze_rule=True), 0),
        "freeze_routing": (ph, Controls(freeze_routing=True), 0),
        "adaptation_off": (ph, Controls(no_adapt=True), 0),
        "latency_minus1": (ph.replace(lat_base=max(0, ph.lat_base - 1)), Controls(), 0),
        "latency_plus1": (ph.replace(lat_base=ph.lat_base + 1), Controls(), 0),
        "jitter_plus1": (ph.replace(lat_jitter=ph.lat_jitter + 1), Controls(), 0),
        "zero_comm": (ph, Controls(zero_comm=True), 0),
    }


def run_battery(bat: dict, genome: np.ndarray, env: envs.EnvSpec, seeds, device="cpu") -> dict:
    """Every arm, with C1's no-op guard: an arm whose per-world digests equal
    the matched normal run changed nothing -> NOT_APPLICABLE."""
    out = {}
    base = {0: None, 1: None}
    for name, (ph, ctrl, ft) in bat.items():
        r = evaluate(ph, genome, env, seeds, ctrl=ctrl, device=device, from_trial=ft)
        ref_key = 0 if ft == 0 else 1
        if name in ("normal", "normal_from1"):
            base[ref_key] = r
            out[name] = {"status": "RAN", "run": r}
            continue
        ref = base[ref_key] if base[ref_key] is not None else base[0]
        if r.digests == ref.digests:
            out[name] = {"status": "NOT_APPLICABLE", "why": "no-op guard", "run": r}
        else:
            out[name] = {"status": "RAN", "run": r}
    return out


# ------------------------------------------------------------ readings
def kills(res: dict) -> bool:
    return res["status"] == "RAN" and ci(res["run"].pairs)[2] <= KILL_HI


def drops(res: dict, normal: Run) -> bool:
    if res["status"] != "RAN":
        return False
    d = res["run"].pairs - normal.pairs
    m, lo, _ = ci(d)
    return m <= -DROP_PT and lo < DROP_LO


def intact(res: dict, normal: Run) -> bool:
    """An ABSENCE reading. A NOT_APPLICABLE arm changed nothing, so it is
    intact by construction."""
    if res["status"] == "NOT_APPLICABLE":
        return True
    return ci(res["run"].pairs - normal.pairs)[1] >= INTACT_LO


def _perm_p(correct_by_world: np.ndarray, pred: np.ndarray, y: np.ndarray, seed=0) -> float:
    """Permutation null over mirror pairs: rotate which pair's targets are
    scored against which pair's predictor."""
    obs = correct_by_world.mean()
    g = np.random.default_rng(seed)
    P = y.shape[0] // 2
    hits = 0
    for _ in range(N_PERM):
        perm = g.permutation(P)
        idx = np.stack([2 * perm, 2 * perm + 1], 1).reshape(-1)
        yy = y[idx]
        c = np.where(pred == 0, 0.5, (np.sign(pred) == yy).astype(float))
        hits += c.mean() >= obs
    return (hits + 1) / (N_PERM + 1)


def census_predicts(run: Run, key: str, ticks_: list[int]) -> dict:
    """sign(census[key] at each trial's tick) as a predictor of the target."""
    ep = run.ep
    pred = np.stack([run.tel[key][t] for t in ticks_], 1)          # [M, trials]
    c = np.where(pred == 0, 0.5, (np.sign(pred) == ep.y).astype(float))
    c = np.where(ep.scored, c, np.nan)
    per_world = np.nanmean(c, 1)
    m, lo, hi = ci(per_world.reshape(-1, 2).mean(-1))
    p = _perm_p(np.nanmean(c, 1), pred, ep.y)
    return {"acc": m, "lo99": lo, "hi99": hi, "perm_p": p,
            "pass": bool(lo > PRED_LO and p < PERM_P)}


def rule_predicts(run: Run, ro_ticks: list[int]) -> dict:
    """The actuator's rule index at readout as a predictor of the target.
    The rule -> sign map is fitted on the first half of the mirror pairs and
    scored on the second half (held out)."""
    ep = run.ep
    r = np.stack([run.tel["c_r_ro"][t] for t in ro_ticks], 1)      # [M, trials]
    M = r.shape[0]
    half = (M // 2) // 2 * 2
    fit, tst = slice(0, half), slice(half, M)
    mapping = {}
    for v in np.unique(r):
        sel = (r[fit] == v) & ep.scored[fit]
        s = ep.y[fit][sel].sum()
        mapping[int(v)] = int(np.sign(s))
    pred = np.vectorize(lambda v: mapping.get(int(v), 0))(r[tst])
    y = ep.y[tst]
    c = np.where(pred == 0, 0.5, (pred == y).astype(float))
    c = np.where(ep.scored[tst], c, np.nan)
    per_world = np.nanmean(c, 1)
    m, lo, hi = ci(per_world.reshape(-1, 2).mean(-1))
    p = _perm_p(per_world, pred, y)
    return {"acc": m, "lo99": lo, "hi99": hi, "perm_p": p, "map": mapping,
            "pass": bool(lo > PRED_LO and p < PERM_P)}


# ------------------------------------------------------------ labels
M2_KEYS = ("A", "Z", "B", "C", "I", "K_S", "K_Kp", "K_w", "K_En")
M2_LABELS = ("INSTRUMENT_FAILURE", "FLUSH_NONSPECIFIC", "DELAY_LINE_SPECIMEN",
             "IN_FLIGHT_UNDECODED", "MIXED", "INBOX_CARRIER", "OTHER_CARRIER",
             "IN_FLIGHT_PLUS_JOINT", "JOINT_NONPACKET", "NOT_SUPPORTED")


def m2_label(b: dict, fixtures_ok: bool = True) -> str:
    """PREREG s3 decision list, first match wins."""
    A, Z, B, C, I = b["A"], b["Z"], b["B"], b["C"], b["I"]
    K = {x: b["K_" + x] for x in ("S", "Kp", "w", "En")}
    if not fixtures_ok:
        return "INSTRUMENT_FAILURE"
    if A and not Z:
        return "FLUSH_NONSPECIFIC"
    if A and Z and B and C:
        return "DELAY_LINE_SPECIMEN"
    if A and Z and B and not C:
        return "IN_FLIGHT_UNDECODED"
    hits = ([["in_flight"]] if (A and Z) else []) + ([["inbox"]] if I else []) + \
        [[x] for x, v in K.items() if v]
    if len(hits) >= 2:
        return "MIXED:" + ",".join(h[0] for h in hits)
    if I:
        return "INBOX_CARRIER"
    if sum(K.values()) == 1:
        return "OTHER_CARRIER:" + next(x for x, v in K.items() if v)
    if A and Z and not B:
        return "IN_FLIGHT_PLUS_JOINT"
    if not B:
        return "JOINT_NONPACKET"
    return "NOT_SUPPORTED"


M3_KEYS = ("T", "X", "R", "M")
M3_LABELS = ("INSTRUMENT_FAILURE", "C1_CONTROL_NOT_REPRODUCED", "TRANSPORT+SELF_MODIFYING",
             "TRANSPORT+RULE_SWITCH", "TRANSPORT_ONLY", "SELF_MODIFYING_ONLY",
             "RULE_SWITCH_ONLY", "NOT_SUPPORTED")


def m3_label(b: dict, fixtures_ok: bool = True, routing_resolved: bool = True) -> str:
    """PREREG s4 product label, first match wins. If the routing positive
    control could not be established, R was computed without the
    freeze_routing clause and the label says so."""
    T, X, R, M = b["T"], b["X"], b["R"], b["M"]
    if not fixtures_ok:
        return "INSTRUMENT_FAILURE"
    if X:
        return "C1_CONTROL_NOT_REPRODUCED"
    if T and R and M:
        lab = "TRANSPORT+SELF_MODIFYING"
    elif T and R:
        lab = "TRANSPORT+RULE_SWITCH"
    elif T:
        lab = "TRANSPORT_ONLY"
    elif R and M:
        lab = "SELF_MODIFYING_ONLY"
    elif R:
        lab = "RULE_SWITCH_ONLY"
    else:
        lab = "NOT_SUPPORTED"
    if R and not routing_resolved:
        lab += "_ROUTING_UNRESOLVED"
    return lab


def label_tables() -> dict:
    """Every combination of the component booleans -> exactly one label
    (PREREG s3/s4: committed with the code freeze, before any row)."""
    m2 = {}
    for bits in itertools.product((False, True), repeat=len(M2_KEYS)):
        b = dict(zip(M2_KEYS, bits))
        m2["".join("1" if x else "0" for x in bits)] = m2_label(b)
    m3 = {}
    for bits in itertools.product((False, True), repeat=len(M3_KEYS)):
        b = dict(zip(M3_KEYS, bits))
        m3["".join("1" if x else "0" for x in bits)] = m3_label(b)
    return {"m2_keys": list(M2_KEYS), "m2": m2, "m3_keys": list(M3_KEYS), "m3": m3}


# ------------------------------------------------------------ fixtures
def fixture_envs() -> dict:
    return {
        "hold": envs.EnvSpec(family="HOLD", gap=8, cue_len=2, trials=12),
        # iti 50: relay_flood waves from the previous trial must die first
        # (half the 24-ring at latency 4 is ~48 ticks). At iti 2 stale waves
        # reached the actuator and normal scored 0.948 at 64 worlds (dev run
        # 2026-09-26, reported), while C1's drop window, which removes them,
        # scored 1.0.
        "relay_da": envs.EnvSpec(family="RELAY", d=1, delta=4, cue_len=2, trials=12, iti=50),
        "relay_route": envs.EnvSpec(family="RELAY", d=2, delta=8, cue_len=4, trials=12),
    }


def run_fixtures(device="cpu", M: int = H_WORLDS) -> dict:
    """PREREG s5 known-answer fixtures on hand plants. Returns name ->
    {"pass": bool, "checks": {...}}. Any failure -> INSTRUMENT_FAILURE."""
    seeds = assays.world_seeds(DEV_NS, M)
    E = fixture_envs()
    out = {}

    def acc(r):
        return round(ci(r.pairs)[0], 4)

    # F-latch: a site latch. reset_S kills it; flush changes nothing.
    ph = plants.c1b_echo_physics().replace(prog_len=12, payload_width=1)
    g = plants.plant("hold_latch", ph)
    res = run_battery({k: v for k, v in m2_battery(ph, E["hold"]).items()
                       if k in ("normal", "reset_S", "flush_inflight")}, g, E["hold"], seeds, device)
    n = res["normal"]["run"]
    chk = {"normal>=0.95": acc(n) >= 0.95, "reset_S kills": kills(res["reset_S"]),
           "flush intact": intact(res["flush_inflight"], n)}
    out["F_latch"] = {"pass": all(chk.values()), "checks": chk,
                      "acc": {k: acc(v["run"]) for k, v in res.items()},
                      "status": {k: v["status"] for k, v in res.items()}}

    # F-echo: the bit only in flight. flush kills; reset_S and the ITI sham
    # do not; the in-flight sign predicts the target at mid-gap.
    ph = plants.c1b_echo_physics()
    g = plants.echo_hold(ph)[None]
    bat = m2_battery(ph, E["hold"])
    res = run_battery({k: bat[k] for k in ("normal", "normal_from1", "reset_S",
                                           "reset_all_nonpacket", "flush_inflight",
                                           "flush_inflight_iti")}, g, E["hold"], seeds, device)
    n, n1 = res["normal"]["run"], res["normal_from1"]["run"]
    cen = census_predicts(n, "c_inflight_sum", ticks(E["hold"])["mid"])
    chk = {"normal>=0.95": acc(n) >= 0.95, "flush kills": kills(res["flush_inflight"]),
           "reset_S intact": intact(res["reset_S"], n),
           "reset_all_nonpacket intact": intact(res["reset_all_nonpacket"], n),
           "iti sham intact": intact(res["flush_inflight_iti"], n1),
           "census predicts": cen["pass"]}
    out["F_echo"] = {"pass": all(chk.values()), "checks": chk, "census": cen,
                     "acc": {k: acc(v["run"]) for k, v in res.items()},
                     "status": {k: v["status"] for k, v in res.items()}}

    # F-DA: delay == delta. C1's window leaves it; the readout-tick drop and
    # the corrected window kill it.
    ph = plants.c1b_da_physics()
    g = plants.plant("relay_flood", ph)
    bat = m3_battery(ph, E["relay_da"])
    res = run_battery({k: bat[k] for k in ("normal", "drop_window_c1", "drop_window_corrected",
                                           "drop_readout_tick_only")}, g, E["relay_da"], seeds,
                      device)
    n = res["normal"]["run"]
    c1lo = ci(res["drop_window_c1"]["run"].pairs)[1]
    chk = {"normal>=0.95": acc(n) >= 0.95, "c1 window intact": c1lo >= C1_INTACT_LO,
           "readout-only kills": kills(res["drop_readout_tick_only"]),
           "corrected kills": kills(res["drop_window_corrected"])}
    out["F_DA"] = {"pass": all(chk.values()), "checks": chk,
                   "acc": {k: acc(v["run"]) for k, v in res.items()}}

    # F-sham-positive (A1.1): relays must be re-armed by a packet in flight
    # across the ITI. The ITI flush must drop it.
    ph = plants.c1b_echo_physics().replace(prog_len=64)
    g = plants.sham_positive_hold(ph)[None]
    bat = m2_battery(ph, E["hold"])
    res = run_battery({k: bat[k] for k in ("normal", "normal_from1", "flush_inflight_iti")},
                      g, E["hold"], seeds, device)
    chk = {"normal>=0.95": acc(res["normal"]["run"]) >= 0.95,
           "iti flush drops": drops(res["flush_inflight_iti"], res["normal_from1"]["run"])}
    out["F_sham_positive"] = {"pass": all(chk.values()), "checks": chk,
                              "acc": {k: acc(v["run"]) for k, v in res.items()}}

    # F-rule: SETRULE carries the bit. freeze_rule drops it; the rule at
    # readout predicts the target.
    ph = plants.c1b_rule_physics()
    g = plants.rule_switch_hold(ph)
    bat = m3_battery(ph, E["hold"])
    res = run_battery({k: bat[k] for k in ("normal", "freeze_rule")}, g, E["hold"], seeds, device)
    n = res["normal"]["run"]
    rp = rule_predicts(n, ticks(E["hold"])["ro"])
    chk = {"normal>=0.95": acc(n) >= 0.95, "freeze_rule drops": drops(res["freeze_rule"], n),
           "rule predicts": rp["pass"]}
    out["F_rule"] = {"pass": all(chk.values()), "checks": chk, "rule_predicts": rp,
                     "acc": {k: acc(v["run"]) for k, v in res.items()}}

    # F-route: plastic routing carries the bit. freeze_routing drops it.
    ph = plants.c1b_route_physics()
    g = plants.route_relay(ph)[None]
    bat = m3_battery(ph, E["relay_route"])
    res = run_battery({k: bat[k] for k in ("normal", "freeze_routing")}, g, E["relay_route"],
                      seeds, device)
    n = res["normal"]["run"]
    chk = {"normal>=0.95": acc(n) >= 0.95,
           "freeze_routing drops": drops(res["freeze_routing"], n)}
    out["F_route"] = {"pass": all(chk.values()), "checks": chk,
                      "acc": {k: acc(v["run"]) for k, v in res.items()}}
    return out


# ------------------------------------------------ specimens (read-only)
SPECIMENS = {"M2": ("4ab2ba014aac967e",), "M3": ("0a23398f20cc41a2", "f6b623cdb23afd2c")}
ROWS = "roles/Ananke/pte/c1_rows/cells.jsonl.gz"
PLANT_STRUCT = ("prog_len", "state_dim", "payload_width", "channels", "rules", "setrule",
                "wimm", "plastic_route", "adapt_shift")      # A2.2: genome space, set by the plant


def specimen_row(cell_id: str, rows: str = ROWS) -> dict:
    import gzip
    import json
    with gzip.open(rows, "rt") as f:
        for line in f:
            r = json.loads(line)
            if r["cell_id"] == cell_id and r["kind"] == "evolve":
                return r
    raise KeyError(cell_id)


def specimen_physics_env(cell_id: str, rows: str = ROWS):
    r = specimen_row(cell_id, rows)
    return Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"])


def at_specimen(plant_ph: Physics, spec_ph: Physics) -> Physics:
    """A2.2: the specimen's communication physics, the plant's genome-space fields."""
    return spec_ph.replace(**{k: getattr(plant_ph, k) for k in PLANT_STRUCT})


# ------------------------------------------------ A1.2 carryover census
def carryover(run: Run, env: envs.EnvSpec) -> dict:
    """In-flight state at each trial's onset (end of tick t0-1), trials >= 1:
    mean count, and whether the signed sum predicts the PREVIOUS trial's
    target (report item; changes no label)."""
    tk = ticks(env)
    t_on = [t0 - 1 for t0 in tk["t0"][1:]]
    cnt = np.stack([run.tel["c_inflight_cnt"][t] for t in t_on], 1)
    s = np.stack([run.tel["c_inflight_sum"][t] for t in t_on], 1)
    y_prev = run.ep.y[:, :-1]
    c = np.where(s == 0, 0.5, (np.sign(s) == y_prev).astype(float))
    per_world = c.mean(1)
    m, lo, hi = ci(per_world.reshape(-1, 2).mean(-1))
    p = _perm_p(per_world, s, y_prev)
    flag = bool(cnt.mean() > 0 and lo > PRED_LO and p < PERM_P)
    return {"mean_inflight_at_onset": float(cnt.mean()), "prev_target_acc": m, "lo99": lo,
            "hi99": hi, "perm_p": float(p), "CARRYOVER": flag}


# ------------------------------------------------ A2.2 eligibility
COMPETENT_LO = 0.55     # A3.1 (i): C1's SIGNAL bar
FIRED_HI = -0.10        # A3.1 (ii): hi99 of (switched - normal) below the intact band


def fired(normal: Run, switched: dict) -> dict:
    """A3.1: the positive control fired iff the plant is competent at this
    physics AND the switch is decisively not-intact."""
    lo_n = ci(normal.pairs)[1]
    if switched["status"] != "RAN":
        return {"competent_lo99": lo_n, "diff_hi99": 0.0, "fired": False}
    hi_d = ci(switched["run"].pairs - normal.pairs)[2]
    return {"competent_lo99": lo_n, "diff_hi99": hi_d,
            "fired": bool(lo_n > COMPETENT_LO and hi_d < FIRED_HI)}


def _check_latch(ph, env, seeds, device):
    g = plants.fix_const_shift(plants.hold_latch(ph), 0, 7)
    g = np.broadcast_to(g, (ph.rules, *g.shape)).copy()
    bat = m2_battery(ph, env)
    res = run_battery({k: bat[k] for k in ("normal", "reset_S")}, g, env, seeds, device)
    n = res["normal"]["run"]
    chk = {"normal>=0.95": ci(n.pairs)[0] >= 0.95, "reset_S kills": kills(res["reset_S"])}
    return chk, {k: round(ci(v["run"].pairs)[0], 4) for k, v in res.items()}, fired(n, res["reset_S"])


def _check_sham(ph, env, seeds, device):
    g = plants.sham_positive_hold(ph)[None]
    bat = m2_battery(ph, env)
    res = run_battery({k: bat[k] for k in ("normal", "normal_from1", "flush_inflight_iti")},
                      g, env, seeds, device)
    n1 = res["normal_from1"]["run"]
    chk = {"normal>=0.95": ci(res["normal"]["run"].pairs)[0] >= 0.95,
           "iti flush drops": drops(res["flush_inflight_iti"], n1)}
    return chk, {k: round(ci(v["run"].pairs)[0], 4) for k, v in res.items()},         fired(n1, res["flush_inflight_iti"])


def _check_echo(ph, env, seeds, device):
    g = plants.echo_hold(ph)[None]
    bat = m2_battery(ph, env)
    res = run_battery({k: bat[k] for k in ("normal", "flush_inflight", "reset_S")},
                      g, env, seeds, device)
    n = res["normal"]["run"]
    chk = {"normal>=0.95": ci(n.pairs)[0] >= 0.95, "flush kills": kills(res["flush_inflight"]),
           "reset_S intact": intact(res["reset_S"], n)}
    return chk, {k: round(ci(v["run"].pairs)[0], 4) for k, v in res.items()},         fired(n, res["flush_inflight"])


def _check_da(ph, env, seeds, device):
    g = plants.plant("relay_flood", ph)
    bat = m3_battery(ph, env)
    res = run_battery({k: bat[k] for k in ("normal", "drop_window_c1", "drop_readout_tick_only")},
                      g, env, seeds, device)
    n = res["normal"]["run"]
    chk = {"normal>=0.95": ci(n.pairs)[0] >= 0.95,
           "c1 window intact": ci(res["drop_window_c1"]["run"].pairs)[1] >= C1_INTACT_LO,
           "readout-only kills": kills(res["drop_readout_tick_only"])}
    return chk, {k: round(ci(v["run"].pairs)[0], 4) for k, v in res.items()},         fired(n, res["drop_readout_tick_only"])


def _check_rule(ph, env, seeds, device):
    g = plants.rule_switch_hold(ph)
    bat = m3_battery(ph, env)
    res = run_battery({k: bat[k] for k in ("normal", "freeze_rule")}, g, env, seeds, device)
    n = res["normal"]["run"]
    chk = {"normal>=0.95": ci(n.pairs)[0] >= 0.95, "freeze_rule drops": drops(res["freeze_rule"], n)}
    return chk, {k: round(ci(v["run"].pairs)[0], 4) for k, v in res.items()}, fired(n, res["freeze_rule"])


def eligibility(device="cpu", M: int = H_WORLDS, rows: str = ROWS) -> dict:
    """A2.2 table: each positive-control plant at each specimen's physics and
    timing. A plant that did not FIRE (A3.1) makes the absence clause it
    guards NOT_ELIGIBLE. The 0.95-bar checks are kept as dev information.
    Hand plants only; no specimen genome is evaluated."""
    seeds = assays.world_seeds(DEV_NS + 1, M)
    out = {}
    for cid in SPECIMENS["M2"]:
        sph, senv = specimen_physics_env(cid, rows)
        hold = dataclasses.replace(senv, family="HOLD")
        rows_ = {}
        for name, fn, pph, guards in (
                ("F_latch", _check_latch, plants.c1b_echo_physics().replace(prog_len=12, payload_width=1), "B"),
                ("F_sham_positive", _check_sham, plants.c1b_echo_physics().replace(prog_len=64), "Z"),
                ("F_echo", _check_echo, plants.c1b_echo_physics(), "(validates A; gates nothing)")):
            ph = at_specimen(pph, sph)
            chk, acc, fr = fn(ph, hold, seeds, device)
            rows_[name] = {"guards": guards, "fired": fr["fired"], "a3": fr,
                           "dev_bar_checks": chk, "acc": acc}
        out[cid] = {"mechanism": "M2", "dest_mode": sph.dest_mode, "plants": rows_,
                    "NOT_ELIGIBLE": sorted(v["guards"] for v in rows_.values()
                                           if not v["fired"] and len(v["guards"]) == 1)}
    for cid in SPECIMENS["M3"]:
        sph, senv = specimen_physics_env(cid, rows)
        relay = dataclasses.replace(senv, family="RELAY", d=1)
        hold = dataclasses.replace(senv, family="HOLD")
        rows_ = {}
        for name, fn, pph, env, guards in (
                ("F_DA", _check_da, plants.c1b_da_physics(), relay, "T_c1_window"),
                ("F_rule", _check_rule, plants.c1b_rule_physics(), hold, "not_R")):
            ph = at_specimen(pph, sph)
            chk, acc, fr = fn(ph, env, seeds, device)
            rows_[name] = {"guards": guards, "fired": fr["fired"], "a3": fr,
                           "dev_bar_checks": chk, "acc": acc}
        routing = "INERT_BY_PHYSICS" if sph.dest_mode == "all" else "F_route required"
        out[cid] = {"mechanism": "M3", "dest_mode": sph.dest_mode, "routing_clause": routing,
                    "plants": rows_,
                    "NOT_ELIGIBLE": sorted(v["guards"] for v in rows_.values() if not v["fired"])}
    return out
