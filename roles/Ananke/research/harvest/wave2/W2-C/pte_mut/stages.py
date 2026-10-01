"""Real PTE pipeline entry points, run on one fixture, reduced to (verdict, numeric, alarms, fingerprints).

held       search.evolve (tiny spec, population seeded with the fixture genome so the champion IS the fixture;
           the held block, zero-comm control and twin assay are the real code) -> campaign.classify +
           campaign.anomaly_flags
controls   assays.run_controls (normal, 10 named controls with the no-op guard, env permutation) ->
           campaign.causal_label
plant      campaign.plant_viability (A0 positive control: relay_flood / hold_latch at the fixture physics)
lens_swap  lens_swap.mixture_scan (single-trial site/channel swaps, frozen census + follow census) and
           swap_rel.swap_verdict_rel4 (promoted REL4 certificate) on the site and channel arms
report     report.build over rows assembled from the stages above (A0 census rows, A evolve rows,
           D adjudicate rows)
oracle     the engine-vs-oracle conformance tests (prometheus/ananke/tests/test_conformance.py), engine
           operators only
"""
from __future__ import annotations

import contextlib
import dataclasses
import json
import pathlib
import tempfile
import traceback

import numpy as np

from . import env as _env  # noqa: F401
from . import operators as O
from prometheus.ananke import assays, campaign, lens_swap, report, search, swap_rel
from prometheus.ananke.rng import H_int

CFG = campaign.CampaignConfig()
M_HELD = 64
TINY = dict(pop=2, M=2, gens=1, elite=1, M_final=2, M_held=M_HELD)


@dataclasses.dataclass
class StageOut:
    stage: str
    fixture: str
    verdict: dict
    numeric: dict
    alarms: list
    fingerprints: list
    error: str | None = None
    raw: dict | None = None

    def to_dict(self):
        d = dataclasses.asdict(self)
        d.pop("raw")
        return d


def _clean(x):
    if isinstance(x, dict):
        return {str(k): _clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_clean(v) for v in x]
    if isinstance(x, (np.floating, float)):
        return None if np.isnan(x) else round(float(x), 6)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, np.ndarray):
        return _clean(x.tolist())
    return x


# ------------------------------------------------------------------ held
def held(fx, op=None) -> StageOut:
    over = dict(op.sp_override) if op is not None else {}
    sel = bool(fx.props.get("selection"))
    sp = search.SearchSpec(**{**TINY, **({"pop": 16, "M_final": M_HELD} if sel else {}), **over})
    pop_fn = search.random_genomes
    seeded = (lambda g, n, ph: np.repeat(fx.genome[None], n, axis=0))

    def degraded(g, n, ph):
        # selection fixture: a pre-screened pool of partially working mutants (fixtures.selection_pool)
        from .fixtures import selection_pool
        pool = selection_pool(fx)
        return np.stack([pool[i % len(pool)] for i in range(n)])
    patches = [(search, "random_genomes", degraded if sel else seeded)]
    with O.patched(patches):
        out = search.evolve(fx.ph, fx.env, fx.seed, sp, device=_env.DEVICE)
    assert search.random_genomes is pop_fn
    row = {"result": out, "env": fx.env.to_dict(), "physics": fx.ph.to_dict(), "levels": {}, "env_levels": {}}
    lab = campaign.classify(row, CFG)
    flags = campaign.anomaly_flags(row)
    h = out["held"]
    verdict = {k: bool(v) for k, v in lab.items() if k != "comm_family"}
    numeric = {"acc": h["acc"], "lo99": h["lo99"], "zero_comm": h["zero_comm"], "comm_delta": h["comm_delta"],
               "comm_delta_lo99": h["comm_delta_lo99"], "train_final": out["champ_train_final"],
               "twin_beyond_hop": out["twin"].get("beyond_hop"), "champion_is_fixture":
               bool(np.array_equal(np.asarray(out["champion"]), fx.genome))}
    return StageOut("held", fx.name, verdict, _clean(numeric), sorted(flags), [], raw={"row": row})


# ------------------------------------------------------------------ controls
def controls(fx, op=None) -> StageOut:
    hseeds = assays.world_seeds(H_int(fx.seed, 0xD0D0), M_HELD)
    c = assays.run_controls(fx.ph, fx.genome, fx.env, hseeds, device=_env.DEVICE)
    adj = {"result": {"controls": c}}
    lab = campaign.causal_label(adj, fx.env.family)
    status = {k: v.get("status", "RAN") for k, v in c.items()}
    alarms = sorted(f"NOT_APPLICABLE:{k}" for k, s in status.items() if s == "NOT_APPLICABLE")
    perm = c["env_permutation"]["acc"]
    if not (0.40 <= perm <= 0.60):
        alarms.append("ENV_PERMUTATION_OUT_OF_BAND")
    if lab == "INCONCLUSIVE":
        alarms.append("CAUSAL_INCONCLUSIVE")
    numeric = {k: v.get("acc") for k, v in c.items()}
    return StageOut("controls", fx.name, {"causal": lab, "status": status}, _clean(numeric), sorted(alarms), [],
                    raw={"controls": c, "causal": lab})


# ------------------------------------------------------------------ plant
def plant(fx, op=None) -> StageOut:
    p = campaign.plant_viability(fx.ph, fx.env, fx.seed, _env.DEVICE)
    verdict = {"viable": bool(p["acc"] >= CFG.living_plant), "plant": p["plant"]}
    return StageOut("plant", fx.name, verdict, _clean({"acc": p["acc"], "zero_comm": p["zero_comm"]}), [], [],
                    raw={"plant": p})


# ------------------------------------------------------------------ lens_swap
LENS_TRIALS = (1, 2, 3)          # K = 3 scored trials -> REL4 table key P32_K3


def lens_offset(env) -> int:
    if env.family == "HOLD":
        return env.cue_len + env.gap // 2
    return env.cue_len + max(1, (env.delta - env.cue_len) // 2)


def lens(fx, op=None, n_boot: int = 500) -> StageOut:
    seeds = assays.world_seeds(H_int(fx.seed, 0x1E45), M_HELD)
    o = lens_offset(fx.env)
    trials = [k for k in LENS_TRIALS]
    raw = {}
    res = lens_swap.mixture_scan(fx.ph, fx.genome, fx.env, seeds, [o], "single", trials, device=_env.DEVICE,
                                 n_boot=n_boot, raw=raw)
    c = res["offsets"][o]
    nm = raw["normal"]["per_trial"].copy()
    keep = np.zeros(nm.shape, bool)
    keep[:, trials] = True
    nm[~keep] = np.nan
    rel = {}
    for arm in ("site", "chan"):
        try:
            v = swap_rel.swap_verdict_rel4(nm, raw[o][arm])
            rel[arm] = v["label"]
        except Exception as e:                     # an error is data here: the certificate refused
            rel[arm] = f"ERROR:{type(e).__name__}"
    verdict = {"class": c["class"], "follow_class": c["follow"]["class"], "rel4_site": rel["site"],
               "rel4_chan": rel["chan"]}
    alarms = []
    for k in ("class", "follow_class"):
        if verdict[k] in ("UNDEFINED", "IDENTITY-BROKEN"):
            alarms.append(f"{k}:{verdict[k]}")
    for k in ("rel4_site", "rel4_chan"):
        if verdict[k] == "NOT_ELIGIBLE" or verdict[k].startswith("ERROR"):
            alarms.append(f"{k}:{verdict[k]}")
    numeric = {"normal": res["normal"], "eligible": c["eligible"], "identity": c["identity"], "fS": c["fS"],
               "fC": c["fC"], "fN": c["fN"], "site_acc": c["site_acc"], "chan_acc": c["chan_acc"],
               "offset": o}
    return StageOut("lens_swap", fx.name, verdict, _clean(numeric), sorted(alarms), [])


# ------------------------------------------------------------------ oracle (engine operators only)
def oracle(fx=None, op=None) -> StageOut:
    from prometheus.ananke.tests import test_conformance as tc
    fails = []
    checks = [("engine_matches_oracle", tc.test_engine_matches_oracle, s) for s in range(0, 6)]
    checks += [("transport_matches_oracle", tc.test_transport_matches_oracle, s) for s in range(100, 104)]
    checks += [("controls_touch_only_their_channel", tc.test_controls_touch_only_their_channel, None)]
    for name, fn, s in checks:
        try:
            fn(s) if s is not None else fn()
        except AssertionError:
            fails.append(f"{name}[{s}]")
    alarms = [f"CONFORMANCE_FAIL:{f}" for f in fails]
    return StageOut("oracle", "conformance", {"pass": not fails}, {"n_checks": len(checks), "n_fail": len(fails)},
                    alarms, [])


# ------------------------------------------------------------------ report (from other stages' raw)
def report_stage(outs: list[StageOut], tag: str) -> StageOut:
    rows = []
    for so in outs:
        if so.raw is None or so.error:
            continue
        fid = f"{so.fixture}"
        if so.stage == "held":
            r = json.loads(json.dumps(so.raw["row"], default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
            r.update(wave="A", kind="evolve", cell_id=f"{fid}:A", extra={"uniform": True}, parent=None)
            r["anomalies"] = campaign.anomaly_flags(r)
            rows.append(r)
        elif so.stage == "controls":
            fam = next((x.raw["row"]["env"]["family"] for x in outs if x.fixture == so.fixture and x.stage == "held"
                        and x.raw), None)
            if fam is None:
                continue
            twin = next((x.raw["row"]["result"]["twin"] for x in outs if x.fixture == so.fixture
                         and x.stage == "held" and x.raw), {})
            rows.append({"wave": "D", "kind": "adjudicate", "cell_id": f"{fid}:D", "env": {"family": fam},
                         "physics": {}, "levels": {}, "env_levels": {}, "extra": {"source_cell": f"{fid}:A"},
                         "result": {"controls": json.loads(json.dumps(so.raw["controls"], default=float)),
                                    "transplants": {}, "twin": twin}})
        elif so.stage == "plant":
            fam = so.raw["plant"]["plant"]
            fam = "HOLD" if fam == "hold_latch" else "RELAY"
            rows.append({"wave": "A0", "kind": "census", "cell_id": f"{fid}:A0", "env": {"family": fam},
                         "physics": {}, "levels": {}, "env_levels": {}, "extra": {},
                         "result": {"plant": so.raw["plant"], "gen0": {"frac_sensitive_any": 0.0,
                                                                        "frac_emitting": 0.0}}})
    with tempfile.TemporaryDirectory(dir=str(_env.W2C / "out")) as d:
        p = pathlib.Path(d)
        with open(p / "cells.jsonl", "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)) + "\n")
        S = report.build(p, CFG)
    a1 = {fam: {k: a[k] for k in ("n", "SIGNAL", "COMM_DEPENDENT", "LOCAL_ONLY")} for fam, a in S["A1"].items()}
    a0 = {fam: round(a["plant_viable_frac"], 3) for fam, a in S["A0"].items()}
    d = {x["source"]: x["causal"] for x in S["D"]}
    an = {k: v["count"] for k, v in S["anomalies"].items()}
    pred = {k: v["held"] for k, v in S["predictions"].items() if k in ("P3", "P4", "P6", "P8")}
    verdict = {"A1": a1, "A0_viable_frac": a0, "D_causal": d, "predictions": pred}
    alarms = sorted([f"anomaly:{k}" for k in an] + [f"D:{s}:INCONCLUSIVE" for s, c in d.items()
                                                     if c == "INCONCLUSIVE"])
    return StageOut("report", tag, verdict, {"anomaly_counts": an, "n_rows": S["n_rows"]}, alarms, [])


RUNNERS = {"held": held, "controls": controls, "plant": plant, "lens_swap": lens}


def run_stage(stage: str, fx, op=None) -> StageOut:
    """Run one stage on one fixture under one operator (None = baseline), recording every World built."""
    reg = O.Registry()
    ctx = op.active() if op is not None else contextlib.nullcontext()
    try:
        with ctx:
            with reg.install():
                so = RUNNERS[stage](fx, op)
    except Exception as e:  # error handling that turns failure into data is exactly what we look for:
        tb = traceback.format_exc(limit=3)   # keep it, label it, never score it as a pass
        so = StageOut(stage, fx.name, {"error": type(e).__name__}, {}, [f"EXCEPTION:{type(e).__name__}"], [],
                      error=f"{type(e).__name__}: {str(e)[:200]} | {tb[-400:]}")
    so.fingerprints = reg.fingerprints()
    assert O.originals_intact(), "an operator leaked a patch"
    return so
