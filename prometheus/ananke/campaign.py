"""PTE campaign driver: waves A-E, cell-level checkpoint/resume, receipts.

Everything a wave runs is a deterministic function of (the frozen
campaign config, the completed rows of earlier waves). A restarted
driver regenerates identical cell specs and skips the ones already in
cells.jsonl, so resume is exact at cell granularity.

Run state lives under ANANKE_HOME (default ~/ananke_runs), never in git.
The committed evidence package is produced by report.py from cells.jsonl.

Loop discipline (base role rules 8-10): heartbeat.json carries
last_success_at and a domain productivity counter (cells completed);
after PARK_BOUND consecutive failed cells the driver writes PARKED.json
and stops (accountable seat: Ananke).
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import itertools
import json
import os
import pathlib
import platform
import subprocess
import sys
import time
import traceback

import numpy as np
import torch

from . import assays, envs, search
from .engine import Controls, World
from .physics import OPS_VERSION, SUBSTRATE_VERSION, Physics
from .rng import H_int

PARK_BOUND = 5
ROOT = pathlib.Path(__file__).resolve().parents[2]

# --------------------------------------------------------------- dial space
DIALS = {
    "topology": ["torus", "ring", "random", "smallworld", "global"],
    "n_sites": [64, 100, 144],
    "radius": [1, 2, 3],
    "k_random": [3, 6],
    "rewire": [50, 200],
    "state_dim": [1, 2, 4, 8],
    "payload_width": [1, 2, 4],
    "channels": [1, 2, 4],
    "fanout": [1, 2, 4, 8],
    "dest_mode": ["sample", "all"],
    "loss": [0.0, 0.1, 0.3, 0.6],
    "loss_per_hop": [0, 1],
    "lat_base": [1, 2, 4],
    "lat_hop": [0, 1],
    "lat_jitter": [0, 1, 3],
    "dup": [0.0, 0.1],
    "noise": [0, 16, 64],
    "cap": [0, 1, 2, 4],
    "collision": ["none", "aloha", "saturate"],
    "decay_shift": [0, 1, 3, 6],
    "update_mode": ["sync", "async"],
    "update_period": [1, 2],
    "update_p": [0.5, 0.8],
    "rules": [1, 2, 4],
    "prog_len": [8, 12, 16],
    "plastic_route": [0, 1],
    "adapt_shift": [2, 5],
    "wimm": [0, 1],
    "setrule": [0, 1],
    "mut_site": [0.0, 0.001, 0.01],
    "economy": ["off", "low", "high"],
}
ECONOMY = {"off": dict(e_income=0, e_max=1000, c_emit=0, c_op=0, c_mem=0),
           "low": dict(e_income=4, e_max=200, c_emit=1, c_op=0, c_mem=0),
           "high": dict(e_income=4, e_max=100, c_emit=4, c_op=1, c_mem=1)}
ENV_DIALS = {"d": [1, 2, 3, 5], "delta": [4, 8, 16], "gap": [4, 8, 16], "block": [2, 4]}


def physics_from_levels(lv: dict, topo_seed: int) -> Physics:
    kw = {k: v for k, v in lv.items() if k != "economy"}
    kw.update(ECONOMY[lv["economy"]])
    if kw["topology"] in ("torus", "smallworld"):
        pass  # all n_sites levels are squares
    if kw["topology"] == "global":
        kw["dest_mode"] = "sample"
    return Physics(**kw, topo_seed=topo_seed).validate()


def env_from_levels(fam: str, ev: dict) -> envs.EnvSpec:
    trials = 16 if fam == "FLIP" else 12
    return envs.EnvSpec(family=fam, d=ev["d"], delta=ev["delta"], gap=ev["gap"],
                        block=ev["block"], trials=trials)


def draw_levels(seed: int, space: dict) -> dict:
    return {k: v[H_int(seed, i) % len(v)] for i, (k, v) in enumerate(sorted(space.items()))}


# ------------------------------------------------------------------ config
@dataclasses.dataclass(frozen=True)
class CampaignConfig:
    campaign_id: str = "pte-c1"
    seed: int = 20260924
    families: tuple = envs.FAMILIES
    a0_cells: int = 5000             # physics census: plant viability + random-substrate liveness
    a0_random: int = 64              # random genomes per census cell
    a_cells: int = 400               # evolution census (A1): half uniform, half from living A0 regions
    a_search: dict = dataclasses.field(default_factory=lambda: search.SearchSpec(pop=96, gens=36).to_dict())
    living_plant: float = 0.75       # A0 -> A1 "living" if plant acc >= this ...
    living_sens: float = 0.30        # ... or random-substrate sensitivity fraction >= this
    b_dials: int = 6                 # transect dials per family: top 2 each by acc, plant, sens effect
    b_reps: int = 3                  # replicate search seeds per transect level
    b_search: dict = dataclasses.field(default_factory=lambda: search.SearchSpec(pop=96, gens=36).to_dict())
    c_top: int = 12                  # top physics cells carried to every family
    d_top: int = 24                  # promoted candidates adjudicated
    d_reps: int = 2                  # fresh-seed search replications per promoted candidate
    e_top: int = 5
    e_sizes: tuple = (400, 1024, 2304)
    budget_hours: dict = dataclasses.field(default_factory=lambda: {"A0": 3.0, "A": 5.0, "B": 3.0, "B2": 1.5,
                                                                     "C": 1.5, "D": 2.0, "E": 1.5})
    # preregistered thresholds (PREREG s7)
    signal_margin: float = 0.05      # held lo99 > 0.5 + margin
    comm_margin: float = 0.03        # comm_delta lo99 > margin (comm families)
    jump_abs: float = 0.10
    jump_se: float = 3.0
    jump_frac: float = 0.5

    def to_dict(self):
        d = dataclasses.asdict(self)
        d["families"] = list(self.families)
        d["e_sizes"] = list(self.e_sizes)
        return d


# ---------------------------------------------------------------- receipts
def git_sha() -> str:
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except Exception:
        return "UNKNOWN"


def git_dirty() -> bool:
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", "prometheus/ananke"],
                             capture_output=True, text=True, timeout=60).stdout
        return bool(out.strip())
    except Exception:
        return True


def hardware() -> dict:
    d = {"python": sys.version.split()[0], "torch": torch.__version__, "numpy": np.__version__,
         "platform": platform.platform(), "host": platform.node()}
    if torch.cuda.is_available():
        d.update(gpu=torch.cuda.get_device_name(0), cuda=torch.version.cuda,
                 gpu_mem_mib=torch.cuda.get_device_properties(0).total_memory // 2 ** 20)
    return d


def gpu_snapshot() -> str:
    try:
        return subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used",
                               "--format=csv,noheader"], capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception as e:
        return f"unavailable: {e}"


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cell_id(spec: dict) -> str:
    blob = json.dumps({k: spec[k] for k in ("wave", "kind", "physics", "env", "search", "search_seed",
                                             "extra")}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


# --------------------------------------------------------------- the store
class Store:
    def __init__(self, home: pathlib.Path, cfg: CampaignConfig):
        self.dir = home / cfg.campaign_id
        self.dir.mkdir(parents=True, exist_ok=True)
        self.cells = self.dir / "cells.jsonl"
        self.done: dict[str, dict] = {}
        if self.cells.exists():
            with open(self.cells, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        r = json.loads(line)
                    except json.JSONDecodeError:
                        continue        # a torn final line from a crash: that cell reruns
                    self.done[r["cell_id"]] = r

    def append(self, row: dict):
        with open(self.cells, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, default=_js) + "\n")
            f.flush()
            os.fsync(f.fileno())
        self.done[row["cell_id"]] = row

    def rows(self, wave=None):
        return [r for r in self.done.values() if wave is None or r["wave"] == wave]

    def log(self, msg: str):
        line = f"{now()} {msg}"
        print(line, flush=True)
        with open(self.dir / "log.txt", "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def heartbeat(self, **kw):
        p = self.dir / "heartbeat.json"
        hb = json.loads(p.read_text()) if p.exists() else {}
        hb.update(kw, updated_at=now())
        p.write_text(json.dumps(hb, indent=1, default=_js))


def _js(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


# ------------------------------------------------------------- one cell
def run_cell(spec: dict, device="cuda") -> dict:
    ph = Physics.from_dict(spec["physics"])
    env = envs.EnvSpec(**spec["env"])
    sp = search.SearchSpec(**spec["search"])
    kind = spec["kind"]
    t0 = time.time()
    out = {}
    if kind == "evolve":
        out = search.evolve(ph, env, spec["search_seed"], sp, device=device)
        out["plant"] = plant_viability(ph, env, spec["search_seed"], device)
    elif kind == "census":
        from .search import random_genomes
        g = np.random.default_rng(spec["search_seed"])
        G = random_genomes(g, spec["extra"]["n_random"], ph)
        seeds = assays.world_seeds(H_int(spec["search_seed"], 0xCE), 8)
        r = assays.evaluate(ph, G, env, seeds, device=device)
        acc = r.mean()
        out["gen0"] = {k: float(np.mean(v)) for k, v in r.tel.items()}
        out["gen0"].update(acc_mean=float(acc.mean()), acc_max=float(acc.max()),
                           frac_sensitive_any=float(np.mean(r.sens_any > 0)),
                           frac_contrast_pos=float(np.mean(r.sens_act > 0)),
                           mean_sens_any=float(r.sens_any.mean()),
                           frac_emitting=float(np.mean(r.tel["emit_rate"] > 0)))
        out["plant"] = plant_viability(ph, env, spec["search_seed"], device)
    elif kind == "adjudicate":
        champ = np.asarray(spec["extra"]["genome"])
        hseeds = assays.world_seeds(H_int(spec["search_seed"], 0xD0D0), sp.M_held)
        out["controls"] = assays.run_controls(ph, champ, env, hseeds, device=device)
        out["twin"] = {k: float(v[0]) for k, v in
                       assays.twin_assay(ph, champ[None], env, hseeds[:16], device=device).items()}
        out["transplants"] = transplant_battery(ph, champ, env, spec, device)
    elif kind == "transfer":
        champ = np.asarray(spec["extra"]["genome"])
        hseeds = assays.world_seeds(H_int(spec["search_seed"], 0x7F7F), sp.M_held)
        r = assays.evaluate(ph, champ[None], env, hseeds, device=device)
        rz = assays.evaluate(ph, champ[None], env, hseeds, ctrl=Controls(zero_comm=True), device=device)
        m, lo, hi = assays.pair_ci(r.pair_acc()[0])
        dm, dlo, dhi = assays.pair_ci(r.pair_acc()[0] - rz.pair_acc()[0])
        out["held"] = {"acc": float(m), "lo99": float(lo), "hi99": float(hi),
                       "zero_comm": float(rz.mean()[0]), "comm_delta": float(dm),
                       "comm_delta_lo99": float(dlo), "comm_delta_hi99": float(dhi)}
        out["held_tel"] = {k: float(v[0]) for k, v in r.tel.items()}
    else:
        raise ValueError(kind)
    out["cell_wall_s"] = time.time() - t0
    return out


def plant_viability(ph: Physics, env: envs.EnvSpec, seed: int, device) -> dict:
    """Does THIS physics admit a known hand-written mechanism? (A physics
    map for a known design, separating physics-dead from search-failed;
    never a search seed.) Evaluated at prog_len=max(L,12) so the 12-line
    relay plant fits; everything else is the cell's physics."""
    from . import plants
    name = "hold_latch" if env.family == "HOLD" else "relay_flood"
    p2 = ph.replace(prog_len=max(ph.prog_len, 12))
    g = plants.plant(name, p2)[None]
    seeds = assays.world_seeds(H_int(seed, 0x9147), 32)
    r = assays.evaluate(p2, g, env, seeds, device=device)
    rz = assays.evaluate(p2, g, env, seeds, ctrl=Controls(zero_comm=True), device=device)
    return {"plant": name, "acc": float(r.mean()[0]), "zero_comm": float(rz.mean()[0]),
            "prog_len_used": p2.prog_len}


def transplant_battery(ph: Physics, champ: np.ndarray, env: envs.EnvSpec, spec: dict, device) -> dict:
    """Update-law transplants into modified physics (the genome is a law;
    moving it is the cheapest principled transplant), plus a state
    transplant for FLIP (does adapted state carry the mapping?)."""
    sp = search.SearchSpec(**spec["search"])
    hseeds = assays.world_seeds(H_int(spec["search_seed"], 0x7A7A), 32)
    res = {}
    mods = {
        "loss+0.2": ph.replace(loss=min(1.0, ph.loss + 0.2)),
        "latency+1": ph.replace(lat_base=ph.lat_base + 1),
        "jitter+2": ph.replace(lat_jitter=ph.lat_jitter + 2),
        "noise+32": ph.replace(noise=ph.noise + 32),
        "size_x2.25": ph.replace(n_sites=144 if ph.n_sites < 144 else 324),
        "async0.7": ph.replace(update_mode="async", update_p=0.7),
    }
    if ph.topology != "global":
        mods["topology->random"] = ph.replace(topology="random", k_random=max(3, ph.table_width()))
    for name, p2 in mods.items():
        try:
            p2 = p2.validate()
        except AssertionError as e:
            res[name] = {"status": "NOT_APPLICABLE", "why": str(e)[:80]}
            continue
        r = assays.evaluate(p2, champ[None], env, hseeds, device=device)
        res[name] = {"status": "RAN", "acc": float(r.mean()[0])}
    if env.family == "FLIP":
        res["state_transplant"] = flip_state_transplant(ph, champ, env, spec, device)
    return res


def flip_state_transplant(ph, champ, env, spec, device) -> dict:
    """Run a donor world through the first half (mapping m known from
    history); transplant S/w/Kp/r into a recipient at the same positions
    with fresh cues but the SAME mapping at the transplant boundary; score
    the first post-transplant trial vs a fresh-state recipient."""
    seeds = assays.world_seeds(H_int(spec["search_seed"], 0x5757), 32)
    ep = envs.build(ph, env, seeds)
    Pd = env.period()
    k0 = env.block - 1                                     # last trial of first block
    T_half = (k0 + 1) * Pd
    donor = World(ph, np.repeat(champ[None], len(seeds), 0), seeds, device=device, schedule=ep.schedule)
    donor.run(T_half)
    accs = {}
    for label, use in (("transplanted", True), ("fresh", False)):
        rec = World(ph, np.repeat(champ[None], len(seeds), 0), seeds, device=device, schedule=ep.schedule)
        rec.run(T_half)                                    # recipient has its own history ...
        if use:
            assays.transplant_state(donor, rec)            # ... replaced by the donor's (identical here)
        else:
            for p in ("S", "Kp"):
                getattr(rec, p).zero_()
        rec.run(env.T() - T_half)
        pt = envs.per_trial(ep, rec.trace.cpu().numpy())
        accs[label] = float(pt[:, k0 + 1:k0 + 3].mean())   # first trials of block 2
    accs["note"] = ("transplant into an identical-history recipient is a control that the "
                    "transplant path is exact; 'fresh' zeroes S and Kp at the boundary")
    return accs


# ---------------------------------------------------------------- waves
def _draw_cell(cfg, s):
    while True:
        lv = draw_levels(s, DIALS)
        try:
            ph = physics_from_levels(lv, topo_seed=H_int(s, 0x7090))
            return s, lv, ph
        except AssertionError:
            s = H_int(s, 1)


def wave_A0(cfg: CampaignConfig) -> list[dict]:
    specs = []
    for i in range(cfg.a0_cells):
        fam = cfg.families[i % len(cfg.families)]
        s, lv, ph = _draw_cell(cfg, H_int(cfg.seed, 0xA0, i))
        ev = draw_levels(H_int(s, 0xE), ENV_DIALS)
        env = env_from_levels(fam, ev)
        specs.append(dict(wave="A0", kind="census", physics=ph.to_dict(), env=env.to_dict(),
                          levels=lv, env_levels=ev, search={}, search_seed=H_int(s, 0x5EED),
                          extra={"n_random": cfg.a0_random}, parent=None))
    return specs


def living(r: dict, cfg: CampaignConfig) -> bool:
    return (r["result"]["plant"]["acc"] >= cfg.living_plant
            or r["result"]["gen0"]["frac_sensitive_any"] >= cfg.living_sens)


def wave_A(cfg: CampaignConfig, A0: list[dict] | None = None) -> list[dict]:
    """A1: half uniform draws, half re-drawn from living A0 cells of the
    same family (deterministic order by cell id). Only the physics/env of
    an A0 cell is reused; nothing learned is carried."""
    specs = []
    pool = {}
    for r in sorted(A0 or [], key=lambda r: r["cell_id"]):
        if living(r, cfg):
            pool.setdefault(r["env"]["family"], []).append(r)
    for i in range(cfg.a_cells):
        fam = cfg.families[i % len(cfg.families)]
        src = None
        if i % 2 == 1 and pool.get(fam):
            src = pool[fam][(i // 2 // len(cfg.families)) % len(pool[fam])]
        if src is not None:
            specs.append(dict(wave="A", kind="evolve", physics=src["physics"], env=src["env"],
                              levels=src["levels"], env_levels=src["env_levels"], search=cfg.a_search,
                              search_seed=H_int(cfg.seed, 0xA1, i),
                              extra={"from_living_A0": src["cell_id"]}, parent=src["cell_id"]))
            continue
        s = H_int(cfg.seed, 0xA, i)
        while True:
            lv = draw_levels(s, DIALS)
            try:
                ph = physics_from_levels(lv, topo_seed=H_int(s, 0x7090))
                break
            except AssertionError:
                s = H_int(s, 1)
        ev = draw_levels(H_int(s, 0xE), ENV_DIALS)
        env = env_from_levels(fam, ev)
        specs.append(dict(wave="A", kind="evolve", physics=ph.to_dict(), env=env.to_dict(),
                          levels=lv, env_levels=ev, search=cfg.a_search,
                          search_seed=H_int(s, 0x5EED), extra={"uniform": True}, parent=None))
    return specs


def classify(row: dict, cfg: CampaignConfig) -> dict:
    """Mechanical, preregistered labels for an evolve/transfer row."""
    h = row["result"]["held"]
    fam = row["env"]["family"]
    comm_family = fam in ("RELAY", "XOR", "MAJ", "FLIP")
    sig = h["lo99"] > 0.5 + cfg.signal_margin
    comm = h["comm_delta_lo99"] > cfg.comm_margin
    lab = {"SIGNAL": bool(sig),
           "COMM_DEPENDENT": bool(sig and comm),
           "LOCAL_ONLY": bool(sig and not comm),
           "comm_family": comm_family}
    if fam == "MAJ":
        lab["INTEGRATION_BEYOND_ONE_SENSOR"] = bool(h["lo99"] > 0.70)
    tw = row["result"].get("twin", {})
    lab["REACH_BEYOND_HOP"] = bool(tw.get("beyond_hop", 0) >= 0.5)
    return lab


def causal_label(adj: dict, family: str) -> str:
    """PREREG s7 CAUSAL_SUPPORT on one adjudication row's controls."""
    c = adj["result"]["controls"]
    n = c["normal"]["acc"]
    ok_perm = 0.40 <= c["env_permutation"]["acc"] <= 0.60

    def ran(k):
        return c.get(k, {}).get("status") == "RAN"
    if family == "HOLD":
        if not ran("memory_ablation"):
            return "INCONCLUSIVE"
        return "CAUSAL_SUPPORT" if (c["memory_ablation"]["acc"] <= n - 0.10 and ok_perm) else "NOT_SUPPORTED"
    if not (ran("zero_comm") and ran("packet_ablation")):
        return "INCONCLUSIVE"
    ok = c["zero_comm"]["acc"] <= 0.55 and c["packet_ablation"]["acc"] <= n - 0.10 and ok_perm
    return "CAUSAL_SUPPORT" if ok else "NOT_SUPPORTED"


def anomaly_flags(row: dict) -> list[str]:
    """Unexpected-behaviour detectors (mission s6/s17); flags, not verdicts."""
    r = row["result"]
    h, tel, tw = r["held"], r.get("held_tel", {}), r.get("twin", {})
    f = []
    if h["acc"] > 0.6 and tel.get("emit_rate", 1) < 0.01 and row["env"]["family"] != "HOLD":
        f.append("SILENT_COMPETENCE")          # competent with almost no traffic
    if h["acc"] > 0.6 and h["comm_delta"] < 0.02 and row["env"]["family"] in ("RELAY", "XOR", "MAJ"):
        f.append("COMPETENT_WITHOUT_COMM")     # a comm family solved locally: leak or new dial?
    if (tw.get("persist", 0) > 3 * row["env"]["delta"] and tw.get("div_frac_readout", 0) > 0.25
            and h["acc"] <= 0.55):
        f.append("MEMORY_WITHOUT_USE")         # persistent causal trace, no competence
    if h["acc"] > 0.6 and row["physics"]["loss"] >= 0.3:
        f.append("ROBUST_UNDER_LOSS")
    if h["acc"] > 0.6 and row["levels"].get("economy") == "high":
        f.append("COMPETENT_UNDER_COST")
    if h["acc"] < 0.45:
        f.append("ANTI_CORRELATED")            # below chance on held-out: sign-locked mechanism
    tr = r.get("champ_train_final", 0.5)
    if tr - h["acc"] > 0.15:
        f.append("TRAIN_HELD_GAP")
    if row["env"]["family"] == "HOLD" and h["acc"] > 0.6 and row["physics"]["decay_shift"] in (1, 3) \
            and h["comm_delta"] > 0.05:
        f.append("DISTRIBUTED_MEMORY_UNDER_DECAY")
    return f


def dial_effects(rows: list[dict], fam: str, metric="acc") -> list[tuple]:
    """Per dial: spread of the mean held-out metric across its levels,
    in units of the pooled SE; returns [(score, dial, {level: mean})]."""
    rs = [r for r in rows if r["env"]["family"] == fam]
    get = METRICS[metric]
    out = []
    for dial in list(DIALS) + list(ENV_DIALS):
        by = {}
        for r in rs:
            lv = r["levels"].get(dial, r["env_levels"].get(dial))
            by.setdefault(json.dumps(lv), []).append(get(r))
        if len(by) < 2:
            continue
        means = {k: float(np.mean(v)) for k, v in by.items()}
        ses = [np.std(v) / np.sqrt(len(v)) if len(v) > 1 else 0.1 for v in by.values()]
        spread = max(means.values()) - min(means.values())
        se = float(np.sqrt(np.mean(np.square(ses)))) + 1e-9
        out.append((spread / se, dial, means))
    return sorted(out, key=lambda x: -x[0])


def _transect_specs(cfg, fam, base, bi, dial, track, kind, search_spec, reps):
    specs = []
    levels = DIALS.get(dial, ENV_DIALS.get(dial))
    for li, lvval in enumerate(levels):
        lv = dict(base["levels"])
        ev = dict(base["env_levels"])
        if dial in DIALS:
            lv[dial] = lvval
        else:
            ev[dial] = lvval
        try:
            ph = physics_from_levels(lv, topo_seed=base["physics"]["topo_seed"])
        except AssertionError:
            continue
        env = env_from_levels(fam, ev)
        for rep in range(reps):
            specs.append(dict(wave="B", kind=kind, physics=ph.to_dict(), env=env.to_dict(),
                              levels=lv, env_levels=ev, search=search_spec,
                              search_seed=H_int(cfg.seed, 0xB, hash_str(track + dial + fam), bi, li, rep),
                              extra={"transect": dial, "level_index": li, "base": bi, "track": track,
                                     "base_cell": base["cell_id"], "rep": rep, "n_random": cfg.a0_random},
                              parent=base["cell_id"]))
    return specs


def wave_B(cfg: CampaignConfig, A0: list[dict], A: list[dict]) -> list[dict]:
    """Two tracks (PREREG s8).
    phys: census cells along the dials with the largest A0 effect on
          plant viability and random-substrate sensitivity (3 each), from
          two bases: the most viable A0 cell and the A0 cell whose plant
          accuracy is closest to the living threshold (a likely edge).
    evo:  evolve cells along the 3 dials with the largest A1 effect on
          held-out accuracy, only for families with >= 1 A1 SIGNAL, from
          the best and second-best (different physics) A1 cells."""
    specs = []
    for fam in cfg.families:
        r0 = [r for r in A0 if r["env"]["family"] == fam]
        if len(r0) >= 2:
            b0 = max(r0, key=lambda r: (r["result"]["plant"]["acc"], r["result"]["gen0"]["frac_sensitive_any"]))
            rest = [r for r in r0 if r["cell_id"] != b0["cell_id"]]
            b1 = min(rest, key=lambda r: abs(r["result"]["plant"]["acc"] - cfg.living_plant))
            dials = []
            for metric in ("plant", "sens"):
                k = 0
                for _, d, _ in dial_effects(A0, fam, metric):
                    if d not in dials:
                        dials.append(d)
                        k += 1
                        if k >= cfg.b_dials // 2:
                            break
            for bi, base in enumerate((b0, b1)):
                for d in dials:
                    specs += _transect_specs(cfg, fam, base, bi, d, "phys", "census", {}, cfg.b_reps)
        r1 = [r for r in A if r["env"]["family"] == fam]
        sig = [r for r in r1 if classify(r, cfg)["SIGNAL"]]
        if sig and len(r1) >= 2:
            b0 = max(r1, key=lambda r: r["result"]["held"]["lo99"])
            key0 = json.dumps(b0["physics"], sort_keys=True)
            rest = [r for r in r1 if json.dumps(r["physics"], sort_keys=True) != key0]
            b1 = max(rest, key=lambda r: r["result"]["held"]["lo99"])
            dials = [d for _, d, _ in dial_effects(A, fam, "acc")[:3]]
            for bi, base in enumerate((b0, b1)):
                for d in dials:
                    specs += _transect_specs(cfg, fam, base, bi, d, "evo", "evolve", cfg.b_search, cfg.b_reps)
    return specs


def hash_str(s: str) -> int:
    return int(hashlib.sha256(s.encode()).hexdigest()[:8], 16)


METRICS = {
    "acc": lambda r: r["result"]["held"]["acc"],                        # evolved competence
    "plant": lambda r: r["result"]["plant"]["acc"],                     # known-mechanism viability
    "sens": lambda r: r["result"]["gen0"]["frac_sensitive_any"],        # random-substrate liveness
    "emit": lambda r: r["result"]["gen0"]["frac_emitting"],             # random-substrate traffic
}


def detect_boundaries(cfg: CampaignConfig, B: list[dict], metric="acc") -> list[dict]:
    """PREREG s8 boundary criterion on each transect, for one metric."""
    groups = {}
    get = METRICS[metric] if metric in METRICS else (lambda r: r["result"]["held"][metric])
    for r in B:
        e = r["extra"]
        if metric == "acc" and r["kind"] != "evolve":
            continue
        groups.setdefault((r["env"]["family"], e["transect"], e["base"], e.get("track", "evo")), {}).setdefault(
            e["level_index"], []).append(get(r))
    found = []
    for (fam, dial, base, track), lv in groups.items():
        idx = sorted(lv)
        if len(idx) < 3:
            continue
        means = np.array([np.mean(lv[i]) for i in idx])
        vars_ = np.array([np.var(lv[i], ddof=1) if len(lv[i]) > 1 else 0.01 for i in idx])
        ns = np.array([len(lv[i]) for i in idx])
        rng_ = means.max() - means.min()
        for j in range(len(idx) - 1):
            jump = abs(means[j + 1] - means[j])
            se = np.sqrt(vars_[j] / ns[j] + vars_[j + 1] / ns[j + 1])
            if (jump >= max(cfg.jump_abs, cfg.jump_se * se) and rng_ >= cfg.jump_abs
                    and jump >= cfg.jump_frac * rng_):
                found.append({"family": fam, "dial": dial, "base": base, "track": track,
                              "between": [idx[j], idx[j + 1]],
                              "jump": float(means[j + 1] - means[j]), "se": float(se),
                              "range": float(rng_), "means": means.tolist(), "metric": metric})
    return found


def wave_B2(cfg: CampaignConfig, B: list[dict], candidates: list[dict]) -> list[dict]:
    """Fresh-seed reproduction of every transect that produced a boundary
    candidate (same physics levels, new search seeds)."""
    want = {(c["family"], c["dial"], c["base"], c["track"]) for c in candidates}
    specs = []
    for r in B:
        e = r["extra"]
        if (r["env"]["family"], e["transect"], e["base"], e.get("track", "evo")) not in want or e.get("rep", 0) != 0:
            continue
        for rep in range(cfg.b_reps):
            specs.append(dict(wave="B2", kind=r["kind"], physics=r["physics"], env=r["env"],
                              levels=r["levels"], env_levels=r["env_levels"], search=r["search"],
                              search_seed=H_int(cfg.seed, 0xB2, hash_str(e["transect"]), e["base"],
                                                e["level_index"], rep),
                              extra=dict(e, rep=rep, reproduction_of=r["cell_id"]), parent=r["cell_id"]))
    return specs


def boundary_verdicts(cfg: CampaignConfig, cands: list[dict], repro: list[dict]) -> list[dict]:
    """PREREG s8: CANDIDATE -> SUPPORTED iff the fresh-seed transect meets
    the same criterion with the same sign, located within +-1 level, AND
    the other base point's transect (orthogonal offset) shows a same-sign
    jump within +-1 level meeting the criterion."""
    out = []
    for c in cands:
        def match(lst, base):
            return [x for x in lst if x["family"] == c["family"] and x["dial"] == c["dial"]
                    and x["metric"] == c["metric"] and x["track"] == c["track"]
                    and x["base"] == base and np.sign(x["jump"]) == np.sign(c["jump"])
                    and abs(x["between"][0] - c["between"][0]) <= 1]
        rep = detect_boundaries(cfg, repro, c["metric"])
        fresh = match(rep, c["base"])
        ortho = match(cands, 1 - c["base"])
        v = dict(c, fresh_seed_reproduced=bool(fresh), orthogonal_offset_reproduced=bool(ortho))
        v["label"] = ("PHASE_BOUNDARY_SUPPORTED" if fresh and ortho else "PHASE_BOUNDARY_CANDIDATE")
        out.append(v)
    return out


def wave_C(cfg: CampaignConfig, A: list[dict], B: list[dict]) -> list[dict]:
    """Top physics cells (by held lo99, any family) re-evolved on every
    other family, plus frozen-champion transfer to every other family."""
    rows = sorted([r for r in A + B if r["kind"] == "evolve"], key=lambda r: -r["result"]["held"]["lo99"])
    seen, top = set(), []
    for r in rows:
        key = json.dumps(r["physics"], sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        top.append(r)
        if len(top) >= cfg.c_top:
            break
    specs = []
    for ti, r in enumerate(top):
        for fam in cfg.families:
            env = env_from_levels(fam, r["env_levels"])
            if fam != r["env"]["family"]:
                specs.append(dict(wave="C", kind="evolve", physics=r["physics"], env=env.to_dict(),
                                  levels=r["levels"], env_levels=r["env_levels"], search=cfg.a_search,
                                  search_seed=H_int(cfg.seed, 0xC, ti, FAMILY_ID(fam)),
                                  extra={"source_cell": r["cell_id"], "source_family": r["env"]["family"]},
                                  parent=r["cell_id"]))
            specs.append(dict(wave="C", kind="transfer", physics=r["physics"], env=env.to_dict(),
                              levels=r["levels"], env_levels=r["env_levels"], search=cfg.a_search,
                              search_seed=H_int(cfg.seed, 0xC7, ti, FAMILY_ID(fam)),
                              extra={"genome": r["result"]["champion"], "source_cell": r["cell_id"],
                                     "source_family": r["env"]["family"]},
                              parent=r["cell_id"]))
        # held-out env variants of the source family: spatial and temporal scale
        for vi, variant in enumerate(({"d": 5, "delta": 16}, {"d": 1, "delta": 4})):
            ev = dict(r["env_levels"])
            ev.update(variant)
            env = env_from_levels(r["env"]["family"], ev)
            specs.append(dict(wave="C", kind="transfer", physics=r["physics"], env=env.to_dict(),
                              levels=r["levels"], env_levels=ev, search=cfg.a_search,
                              search_seed=H_int(cfg.seed, 0xC8, ti, vi),
                              extra={"genome": r["result"]["champion"], "source_cell": r["cell_id"],
                                     "source_family": r["env"]["family"], "variant": ev},
                              parent=r["cell_id"]))
    return specs


def FAMILY_ID(f):
    return envs.FAMILY_ID[f]


def promoted(cfg: CampaignConfig, rows: list[dict]) -> list[dict]:
    ev = [r for r in rows if r["kind"] == "evolve"]
    sig = [r for r in ev if classify(r, cfg)["SIGNAL"]]
    sig = sorted(sig, key=lambda r: -r["result"]["held"]["lo99"])
    # at most 3 per family so one easy family cannot take every slot
    out, per = [], {}
    for r in sig:
        f = r["env"]["family"]
        if per.get(f, 0) >= max(3, cfg.d_top // len(cfg.families)):
            continue
        per[f] = per.get(f, 0) + 1
        out.append(r)
        if len(out) >= cfg.d_top:
            break
    return out


def wave_D(cfg: CampaignConfig, rows: list[dict]) -> list[dict]:
    specs = []
    for pi, r in enumerate(promoted(cfg, rows)):
        base = dict(physics=r["physics"], env=r["env"], levels=r["levels"], env_levels=r["env_levels"],
                    search=cfg.a_search, parent=r["cell_id"])
        specs.append(dict(base, wave="D", kind="adjudicate", search_seed=H_int(cfg.seed, 0xD, pi),
                          extra={"genome": r["result"]["champion"], "source_cell": r["cell_id"]}))
        for rep in range(cfg.d_reps):
            specs.append(dict(base, wave="D", kind="evolve", search_seed=H_int(cfg.seed, 0xD5, pi, rep),
                              extra={"replicates": r["cell_id"]}))
    return specs


def wave_E(cfg: CampaignConfig, rows: list[dict]) -> list[dict]:
    """Scale probe: strongest survivors' frozen laws at larger N (a
    homogeneous law is defined at any size), and one re-evolution at the
    first larger size."""
    specs = []
    for pi, r in enumerate(promoted(cfg, rows)[:cfg.e_top]):
        for n in cfg.e_sizes:
            topo = r["physics"]["topology"]
            nn = n if topo in ("torus", "smallworld") else n
            ph = Physics.from_dict(r["physics"]).replace(n_sites=nn)
            try:
                ph.validate()
            except AssertionError:
                continue
            specs.append(dict(wave="E", kind="transfer", physics=ph.to_dict(), env=r["env"],
                              levels=r["levels"], env_levels=r["env_levels"], search=cfg.a_search,
                              search_seed=H_int(cfg.seed, 0xE, pi, n),
                              extra={"genome": r["result"]["champion"], "source_cell": r["cell_id"], "size": nn},
                              parent=r["cell_id"]))
        ph = Physics.from_dict(r["physics"]).replace(n_sites=cfg.e_sizes[0])
        try:
            ph.validate()
            specs.append(dict(wave="E", kind="evolve", physics=ph.to_dict(), env=r["env"],
                              levels=r["levels"], env_levels=r["env_levels"], search=cfg.a_search,
                              search_seed=H_int(cfg.seed, 0xE5, pi),
                              extra={"re_evolve_at": cfg.e_sizes[0], "source_cell": r["cell_id"]},
                              parent=r["cell_id"]))
        except AssertionError:
            pass
    return specs


# ---------------------------------------------------------------- driver
def run_wave(store: Store, cfg: CampaignConfig, wave: str, specs: list[dict], meta: dict, device):
    budget_s = cfg.budget_hours[wave] * 3600
    t0 = time.time()
    todo = []
    for s in specs:
        s["cell_id"] = cell_id(s)
        if s["cell_id"] not in store.done:
            todo.append(s)
    store.log(f"wave {wave}: {len(specs)} specs, {len(specs) - len(todo)} already done, {len(todo)} to run; "
              f"budget {cfg.budget_hours[wave]} h; gpu {gpu_snapshot()}")
    fails = 0
    ran = 0
    for s in todo:
        if time.time() - t0 > budget_s:
            store.log(f"wave {wave}: budget exhausted after {ran} cells; {len(todo) - ran} not run (BUDGET_CENSORED)")
            store.heartbeat(**{f"wave_{wave}_censored": len(todo) - ran})
            break
        try:
            res = run_cell(s, device=device)
            row = dict(s, result=res, receipt=dict(meta, finished_at=now()))
            if s["kind"] in ("evolve", "transfer"):
                row["labels"] = classify(row, cfg)
                row["anomalies"] = anomaly_flags(row) if s["kind"] == "evolve" else []
            store.append(row)
            fails = 0
            ran += 1
            n = len(store.done)
            store.heartbeat(last_success_at=now(), cells_done=n, current_wave=wave,
                            productive=True, consecutive_failures=0)
            if ran % 10 == 0:
                h = res.get("held", {})
                store.log(f"wave {wave}: {ran}/{len(todo)} cells; last {s['env']['family']} "
                          f"held={h.get('acc', float('nan')):.3f} wall={res['cell_wall_s']:.1f}s")
        except Exception as e:
            fails += 1
            store.log(f"CELL FAILED {s['cell_id']} ({wave}/{s['kind']}): {type(e).__name__}: {e}")
            with open(store.dir / "failures.log", "a", encoding="utf-8") as f:
                f.write(json.dumps({"cell_id": s["cell_id"], "at": now(), "err": traceback.format_exc()}) + "\n")
            store.heartbeat(consecutive_failures=fails, productive=False)
            if fails >= PARK_BOUND:
                park = {"parked_at": now(), "reason": f"{fails} consecutive failed cells in wave {wave}",
                        "accountable_seat": "Ananke", "resume": "explicit clearance only"}
                (store.dir / "PARKED.json").write_text(json.dumps(park, indent=1))
                store.log("PARKED: " + park["reason"])
                raise SystemExit(3)
            if torch.cuda.is_available():
                torch.cuda.empty_cache()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="frozen campaign config JSON")
    ap.add_argument("--home", default=os.environ.get("ANANKE_HOME", str(pathlib.Path.home() / "ananke_runs")))
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--waves", default="ABCDE")
    ap.add_argument("--allow-dirty", action="store_true")
    a = ap.parse_args(argv)
    raw = json.loads(pathlib.Path(a.config).read_text())
    cfg = CampaignConfig(**{k: (tuple(v) if k in ("families", "e_sizes") else v)
                            for k, v in raw["config"].items()})
    store = Store(pathlib.Path(a.home), cfg)
    if (store.dir / "PARKED.json").exists():
        store.log("refusing to run: PARKED.json present (resume only on explicit clearance)")
        return 3
    sha = git_sha()
    if raw.get("code_sha"):
        d = subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", raw["code_sha"], "HEAD", "--",
                            "prometheus/ananke"], capture_output=True, timeout=120)
        if d.returncode != 0:
            store.log(f"refusing to run: prometheus/ananke at {sha} differs from frozen {raw['code_sha']}")
            return 4
    if git_dirty() and not a.allow_dirty:
        store.log("refusing to run: prometheus/ananke has uncommitted changes")
        return 5
    meta = {"code_sha": sha, "freeze_sha256": hashlib.sha256(pathlib.Path(a.config).read_bytes()).hexdigest(),
            "hardware": hardware(), "substrate": SUBSTRATE_VERSION, "ops": OPS_VERSION,
            "rng": "PTE counter hash (DESIGN s2)", "campaign": cfg.campaign_id}
    (store.dir / "run_meta.json").write_text(json.dumps(meta, indent=1))
    store.heartbeat(started_at=now(), status="RUNNING", bound=PARK_BOUND, accountable_seat="Ananke")
    waves = a.waves.replace("A", "0A") if "0" not in a.waves else a.waves
    for wave in waves:
        prior = store.rows()
        if wave == "0":
            wave = "A0"
            specs = wave_A0(cfg)
        elif wave == "A":
            specs = wave_A(cfg, store.rows("A0"))
        elif wave == "B":
            specs = wave_B(cfg, store.rows("A0"), store.rows("A"))
        elif wave == "C":
            specs = wave_C(cfg, store.rows("A"), store.rows("B"))
        elif wave == "D":
            specs = wave_D(cfg, [r for r in prior if r["kind"] == "evolve"])
        elif wave == "E":
            specs = wave_E(cfg, [r for r in prior if r["kind"] == "evolve" and r["wave"] in "ABC"])
        else:
            continue
        run_wave(store, cfg, wave, specs, meta, a.device)
        if wave == "B":
            bd = [x for m in METRICS for x in detect_boundaries(cfg, store.rows("B"), m)]
            (store.dir / "boundaries_B.json").write_text(json.dumps(bd, indent=1))
            store.log(f"wave B boundary candidates: {len(bd)}")
            if bd:
                run_wave(store, cfg, "B2", wave_B2(cfg, store.rows("B"), bd), meta, a.device)
            verd = boundary_verdicts(cfg, bd, store.rows("B2"))
            (store.dir / "boundaries_verdicts.json").write_text(json.dumps(verd, indent=1))
            store.log("boundary verdicts: " + json.dumps({k: sum(v["label"] == k for v in verd)
                      for k in ("PHASE_BOUNDARY_CANDIDATE", "PHASE_BOUNDARY_SUPPORTED")}))
    store.heartbeat(status="DONE", finished_at=now())
    store.log("campaign DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
