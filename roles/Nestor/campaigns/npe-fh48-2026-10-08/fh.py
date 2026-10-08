"""NPE-48h functional-heredity campaign library (directive roles/Nestor/prompts/2026-10-08_npe_48h_functional_heredity/).

Imports the FROZEN X-TASK-GATE v2 ruler (../npe-frontier-2026-09-30/x_task_gate_v2/xtg2.py: cue-flip USE score,
(task, genome) cache, constructs) read-only. World = XTG-v2's (ffa6 cell, dense VM, ATOMIC runner, STATIC FORCED_READ
ADD37, pop 256, tier M) with these declared coordinates, each defaulting to XTG-v2's value:

  gate      TG     p = 0.15 + 0.85 * max(u_a, u_b)                      (XTG-v2)
            SHUF   same formula, u read from two OTHER random live organisms (rate-matched, competence-blind)
            CONST  p = p_const for every pair (competence-blind)
  order     RANDOM side assignment (world default: shuffled list, alive[i] runs first = side 0)
            DIR    after the gate, the pair is ordered so the higher-u organism is side 0 (runs first) with
                   probability q_dir; ties keep the random order. Interaction COUNT is unchanged by order.
  mut_scale multiplies the world's mutation rate (ATOMIC write-back + post-interaction mutation)
  copy_scale multiplies the block-copy error rate (LDIR per-byte bit flip, z8 copy_mut_rate)
  plant     one planted genome at slot i = 0 (world implant), or None

LEDGER (exact, per interaction, per half; uses the pre-interaction genomes and the world's own mutate calls):
  competent half (u_gate >= 0.75 before the interaction):
    KEPT            not converted and still competent after its in-place (ATOMIC) mutation
    LOST_INPLACE    not converted; in-place mutation destroyed competence
    REPL_COMP       converted by a competent donor; the child is competent
    LOST_OVERWRITE  converted by a NON-competent donor (genome replacement)
    LOST_COPY_ERR   converted by a competent donor; the tape copy (pre world-mutation) is already non-competent
                    (block-copy error or partner write: infidelity of the copy itself)
    LOST_COPY_MUT   converted by a competent donor; the tape copy was competent; the world's post-interaction
                    mutation destroyed it
  non-competent half:
    GAIN_COPY       converted by a competent donor; child competent (spread)
    GAIN_CREATED    converted by a non-competent donor; child competent
    GAIN_INPLACE    not converted; in-place mutation created competence
  Transmission (every conversion with a competent donor): child competent? (P11 / LABEL separately), and the
  tape-copy competent? (copy fidelity before the world's mutation).
  Byte positions: for LOST_INPLACE / LOST_COPY_MUT the positions the mutation changed; for LOST_COPY_ERR the positions
  where the tape copy differs from the donor. Denominators: positions changed by every mutation applied to a
  competent genome (so per-position destructiveness is estimable).
"""
from __future__ import annotations

import gzip
import json
import os
import pathlib
import platform
import random
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
XTG2_DIR = HERE.parent / "npe-frontier-2026-09-30" / "x_task_gate_v2"
sys.path.insert(0, str(XTG2_DIR))
import xtg2  # noqa: E402  (frozen; read-only import)
from xtg2 import COMP_MIN, GATE_SEED, HELD_SEED, UseCache, PLANTS  # noqa: E402,F401

L = 64
TRAJ_EARLY, TRAJ_EVERY = 10, 50          # snapshot every 10 epochs to epoch 300, then every 50
DEFAULT = dict(gate="TG", order="RANDOM", q_dir=1.0, p_const=0.15, gate_floor=0.15, mut_scale=1.0, copy_scale=1.0,
               plant="CT_UA", n_plants=1, epochs=None, ledger=True)


def make_runner(seed, cfg=None):
    cfg = dict(DEFAULT, **(cfg or {}))
    world, run_dd, run_ds = xtg2._import_world()
    a = run_ds.cells()[run_dd.CELLS[xtg2.CELL]]
    cell = dict(a["cell"], atlas_axis="NONE", environment="STATIC", reproduction="PAIR_EXECUTION",
                pressure="TASK_GATED_INTERACTION")
    plant = cfg["plant"]
    pbytes = PLANTS[plant] if isinstance(plant, str) else (bytes(plant) if plant else None)
    kw = dict(implant="ACTUAL_GENOME", implant_bytes=pbytes) if pbytes else {}
    Base = run_ds.runner_cls(world)
    cache = UseCache()
    shuf_rng = random.Random(seed * 1_000_003 + 17)
    dir_rng = random.Random(seed * 1_000_003 + 29)
    F = cfg["gate_floor"]

    class FH(Base):
        def __init__(self, *aa, **kk):
            super().__init__(*aa, **kk)
            self.cache = cache
            self.cfg = cfg
            self.st = {}
            self.roots = []
            self.traj = []
            self.n_pairs = self.n_inter = 0
            self.led = {}
            self.tx = {"P11": [0, 0, 0], "LABEL": [0, 0, 0]}      # [n conversions by competent donor, child comp, tape comp]
            self.pos_loss = {k: [0] * L for k in ("LOST_INPLACE", "LOST_COPY_MUT", "LOST_COPY_ERR")}
            self.pos_mut_on_comp = [0] * L                        # denominator: every byte a mutation changed on a competent genome
            self.n_mut_on_comp = 0
            self.exposure = {"comp_half_interactions": 0, "comp_half_epochs": 0,
                             "noncomp_half_interactions": 0, "noncomp_half_epochs": 0}
            self.side = {"comp_donor_side0": 0, "comp_donor_side1": 0, "conv_side0_victim": 0, "conv_side1_victim": 0}
            self.loss_examples = []
            self.ledger_series = []
            base = self.mut_rate                                   # world: copy_mut == mut_rate (0.002, LOW)
            self.mut_rate = base * cfg["mut_scale"]
            self.copy_mut = base * cfg["copy_scale"]

        # -------------------------------------------------------------- competence (current genome)
        def _u(self, o):
            u = self.cache.u(self._genome(o))
            o.comp = u
            return u

        def _c(self, g):
            return self.cache.u(g) >= COMP_MIN

        def _validate(self, force=False):
            if force:
                for o in self.orgs:
                    if o.alive:
                        g = self._genome(o)
                        o.comp = self.cache.u(g)
                        o.held = self.cache.get(g, HELD_SEED)["u"]
                        o.probe = self.cache.get(g, GATE_SEED)["reads"]

        def _env_epoch(self):
            assert self.cell["environment"] == "STATIC"

        def _root(self, kind, o):
            self.roots.append({"id": len(self.roots), "kind": kind, "epoch": self.epoch, "oid": o.oid})
            return len(self.roots) - 1

        def _init_state(self):
            for o in self.orgs:
                if o.alive and o not in self.st:
                    c = self._c(self._genome(o))
                    self.st[o] = {"prov": "INIT", "born": 0, "comp": c, "origin": "INIT" if c else None,
                                  "origin_epoch": 0 if c else None, "root": self._root("INIT", o) if c else None,
                                  "tx_p11": 0, "tx_any": 0}

        def _bump(self, k, n=1):
            self.led[k] = self.led.get(k, 0) + n

        # -------------------------------------------------------------- epoch
        def _pair_epoch(self):
            if not self.st:
                self._init_state()
            alive = [o for o in self.orgs if o.alive]
            self.rng.shuffle(alive)
            for o in alive:
                if self.st[o]["comp"]:
                    self.exposure["comp_half_epochs"] += 1
                else:
                    self.exposure["noncomp_half_epochs"] += 1
            for i in range(0, len(alive) - 1, 2):
                a_, b_ = alive[i], alive[i + 1]
                g = cfg["gate"]
                if g == "TG":
                    p = F + (1 - F) * max(self._u(a_), self._u(b_))
                elif g == "SHUF":
                    c_, d_ = alive[shuf_rng.randrange(len(alive))], alive[shuf_rng.randrange(len(alive))]
                    p = F + (1 - F) * max(self._u(c_), self._u(d_))
                elif g == "CONST":
                    p = cfg["p_const"]
                else:
                    raise ValueError(g)
                self.n_pairs += 1
                if self.rng.random() > p:
                    continue
                self.n_inter += 1
                if cfg["order"] == "DIR":
                    ua, ub = self._u(a_), self._u(b_)
                    if ub > ua and dir_rng.random() < cfg["q_dir"]:
                        a_, b_ = b_, a_
                elif cfg["order"] != "RANDOM":
                    raise ValueError(cfg["order"])
                self._pair_interact(i, a_, b_)

        def _pair_interact(self, i, a_, b_):
            pre = {o: (o.oid, self._genome(o)) for o in (a_, b_)}
            pst = {o: dict(self.st[o]) for o in (a_, b_)}
            pc = {o: self._c(pre[o][1]) for o in (a_, b_)}
            for o in (a_, b_):
                self.exposure["comp_half_interactions" if pc[o] else "noncomp_half_interactions"] += 1
            calls = []

            def m(g, _self=self):
                out = type(_self)._mutate(_self, g)
                calls.append((bytes(g), bytes(out)))
                return out
            self._mutate = m
            nlin = len(self.lineage)
            try:
                super()._pair_interact(i, a_, b_)
            finally:
                del self._mutate
            assert len(calls) >= 2, calls
            tape = {a_: calls[0][0], b_: calls[1][0]}
            births = {e["child"]: e for e in self.lineage[nlin:] if e["kind"] == "birth"}
            for side, o in enumerate((a_, b_)):
                donor = b_ if o is a_ else a_
                oid0, g0 = pre[o]
                g1 = self._genome(o)
                old = self.st[o]
                was = pc[o]
                if o.oid != oid0:                                     # converted
                    e = births[o.oid]
                    prov = "P11" if e["causal"] else "LABEL"
                    self.side["conv_side%d_victim" % side] += 1
                    c1 = self._c(g1)
                    cd = pc[donor]
                    dst = pst[donor]
                    tc = self._c(tape[o]) if cd else None
                    if cd:
                        self.side["comp_donor_side%d" % (1 - side)] += 1
                        t = self.tx[prov]
                        t[0] += 1
                        t[1] += c1
                        t[2] += bool(tc)
                    if was:
                        if c1 and cd:
                            self._bump("REPL_COMP")
                        elif not cd:
                            self._bump("LOST_OVERWRITE" if not c1 else "REPL_CREATED")
                        elif not tc:
                            self._bump("LOST_COPY_ERR")
                            self._pos("LOST_COPY_ERR", pre[donor][1], tape[o])
                        else:
                            self._bump("LOST_COPY_MUT")
                            self._pos("LOST_COPY_MUT", tape[o], g1)
                    else:
                        if c1:
                            self._bump("GAIN_COPY" if cd else "GAIN_CREATED")
                        else:
                            self._bump("NONCOMP_CONVERTED")
                    new = {"prov": prov, "born": self.epoch, "comp": c1, "origin": None, "origin_epoch": None,
                           "root": None, "tx_p11": 0, "tx_any": 0, "donor_comp": cd}
                    if c1:
                        if cd and dst.get("root") is not None:
                            new.update(origin=prov + "_TX", origin_epoch=self.epoch, root=dst["root"],
                                       tx_p11=dst["tx_p11"] + (prov == "P11"), tx_any=dst["tx_any"] + 1)
                        else:
                            new.update(origin=prov + "_CREATED", origin_epoch=self.epoch,
                                       root=self._root(prov + "_CREATED", o))
                    if was and not c1 and len(self.loss_examples) < 60:
                        self.loss_examples.append({"epoch": self.epoch, "kind": "converted", "prov": prov,
                                                   "donor_comp": cd, "pre": g0.hex(), "donor_pre": pre[donor][1].hex(),
                                                   "tape": tape[o].hex(), "after": g1.hex(),
                                                   "tx_p11": old.get("tx_p11"), "origin": old.get("origin")})
                    self.st[o] = new
                else:                                                 # not converted: ATOMIC in-place mutation
                    c1 = self._c(g1)
                    if was:
                        if g1 != g0:
                            self.n_mut_on_comp += 1
                            for k in range(min(len(g0), len(g1), L)):
                                if g0[k] != g1[k]:
                                    self.pos_mut_on_comp[k] += 1
                        if c1:
                            self._bump("KEPT")
                        else:
                            self._bump("LOST_INPLACE")
                            self._pos("LOST_INPLACE", g0, g1)
                            if len(self.loss_examples) < 60:
                                self.loss_examples.append({"epoch": self.epoch, "kind": "inplace", "pre": g0.hex(),
                                                           "after": g1.hex(), "tx_p11": old.get("tx_p11"),
                                                           "origin": old.get("origin")})
                            old.update(comp=False, origin=None, origin_epoch=None, root=None, tx_p11=0, tx_any=0)
                    else:
                        if c1:
                            self._bump("GAIN_INPLACE")
                            old.update(comp=True, origin="MUT", origin_epoch=self.epoch, root=self._root("MUT", o),
                                       tx_p11=0, tx_any=0)
                        else:
                            self._bump("NONCOMP_KEPT")

        def _pos(self, k, x, y):
            for j in range(min(len(x), len(y), L)):
                if x[j] != y[j]:
                    self.pos_loss[k][j] += 1

        def step(self):
            super().step()
            e = self.epoch
            if self.st and (e % TRAJ_EVERY == 0 or (e <= 300 and e % TRAJ_EARLY == 0)):
                alive = [o for o in self.orgs if o.alive]
                n = max(1, len(alive))
                comp = [o for o in alive if self.cache.competent(self._genome(o))]
                self.traj.append({"e": e, "CS": round(len(comp) / n, 4),
                                  "CS_gate": round(sum(self.st[o]["comp"] for o in alive) / n, 4),
                                  "CD": round(sum(self.st[o]["prov"] == "P11" for o in comp) / n, 4),
                                  "CD_TX": round(sum(self.st[o]["prov"] == "P11" and self.st[o]["origin"] == "P11_TX"
                                                     for o in comp) / n, 4),
                                  "p11_born": round(sum(self.st[o]["prov"] == "P11" for o in alive) / n, 4),
                                  "max_tx_p11": max([self.st[o]["tx_p11"] for o in comp], default=0),
                                  "inter": self.n_inter})
                self.ledger_series.append({"e": e, **self.led})

    r = FH(cell, seed, tier=a["tier"], max_epochs=cfg["epochs"], **kw)
    assert r.d["has_task"] and r.cell["environment"] == "STATIC" and r.spec.cue_index() == 2
    return r


def summarize(r, out):
    _parent, causal_parent, _bn, _mv = r._lineage_graph()
    _d, per_causal = r._depths(causal_parent)
    alive = [o for o in r.orgs if o.alive]
    n = max(1, len(alive))
    rows = []
    for o in alive:
        g = r._genome(o)
        comp = r.cache.competent(g)
        st = r.st.get(o, {"prov": "INIT", "origin": None})
        rows.append({"oid": o.oid, "prov": st["prov"], "comp": comp, "u": r.cache.u(g), "origin": st.get("origin"),
                     "tx_p11": st.get("tx_p11", 0), "cdepth": per_causal.get(o.oid, 0), "g": g.hex()})
    comp = [x for x in rows if x["comp"]]

    def share(pred):
        return round(sum(1 for x in rows if pred(x)) / n, 4)
    t = r.traj
    cs_series = [x["CS"] for x in t]
    pk = max(t, key=lambda x: x["CD_TX"]) if t else {"e": 0, "CD_TX": 0.0}
    last_comp = max([x["e"] for x in t if x["CS"] > 0], default=0)
    gen = {}
    for x in comp:
        gen[x["g"]] = gen.get(x["g"], 0) + 1
    rec = {
        "alive": len(alive), "CS": share(lambda x: x["comp"]),
        "CD": share(lambda x: x["comp"] and x["prov"] == "P11"),
        "CD_TX": share(lambda x: x["comp"] and x["prov"] == "P11" and x["origin"] == "P11_TX"),
        "CS_peak": max(cs_series, default=0.0), "CD_TX_peak": pk["CD_TX"], "CD_TX_peak_epoch": pk["e"],
        "last_epoch_CS_gt_0": last_comp,
        "comp_auc": round(sum(cs_series) / max(1, len(cs_series)), 4),
        "max_tx_p11_ever": max([x["max_tx_p11"] for x in t], default=0),
        "p11_born_share": share(lambda x: x["prov"] == "P11"),
        "depth": out["max_causal_replication_depth"], "p11_events": out["p11_events"],
        "pairs": r.n_pairs, "interactions": r.n_inter, "interaction_rate": round(r.n_inter / max(1, r.n_pairs), 4),
        "ledger": r.led, "tx": r.tx, "side": r.side, "exposure": r.exposure,
        "n_mut_on_comp": r.n_mut_on_comp, "roots": _count(x["kind"] for x in r.roots),
        "traj": t, "cfg": {k: v for k, v in r.cfg.items()},
    }
    detail = {"pos_loss": r.pos_loss, "pos_mut_on_comp": r.pos_mut_on_comp, "loss_examples": r.loss_examples,
              "ledger_series": r.ledger_series, "competent_genomes_final": gen,
              "organisms": [{k: v for k, v in x.items() if k != "g" or x["comp"]} for x in rows]}
    return rec, detail


def _count(it):
    d = {}
    for k in it:
        d[str(k)] = d.get(str(k), 0) + 1
    return d


def run_one(exp, arm, seed, cfg, outdir):
    t0, c0 = time.time(), time.process_time()
    r = make_runner(seed, cfg)
    out = r.run()
    rec, detail = summarize(r, out)
    rec.update(exp=exp, arm=arm, seed=seed, epochs=r.epoch, wall_s=round(time.time() - t0, 1),
               cpu_s=round(time.process_time() - c0, 1), peak_rss_mb=xtg2._peak_rss_mb(), host=platform.node())
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stem = "%s_%d" % (arm, seed)
    with gzip.open(outdir / (stem + ".detail.json.gz"), "wt") as f:
        json.dump(detail, f)
    (outdir / (stem + ".json")).write_text(json.dumps(rec))
    return rec


def _job(args):
    return run_one(*args)


def pool_run(exp, jobs, outdir, workers=4, show=("CS_peak", "CD_TX_peak", "last_epoch_CS_gt_0", "CS", "depth")):
    """jobs: [(arm, seed, cfg)]. One job per process; resumable; writes RECEIPT_*.json."""
    import multiprocessing as mp
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    done = {p.stem for p in outdir.glob("*.json") if not p.name.startswith("RECEIPT")}
    todo = [j for j in jobs if "%s_%d" % (j[0], j[1]) not in done]
    t0 = time.time()
    start = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    with mp.Pool(workers, maxtasksperchild=1) as pool:
        for rec in pool.imap_unordered(_job, [(exp, a, s, c, outdir) for a, s, c in todo]):
            print(json.dumps({"arm": rec["arm"], "seed": rec["seed"], **{k: rec[k] for k in show},
                              "wall_s": rec["wall_s"]}), flush=True)
    rows = [json.loads(p.read_text()) for p in sorted(outdir.glob("*.json")) if not p.name.startswith("RECEIPT")]
    receipt = {"exp": exp, "host": platform.node(), "compute": "CPU only", "workers": workers,
               "start": start, "end": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
               "wall_s_this_call": round(time.time() - t0, 1), "jobs_this_call": len(todo), "rows": len(rows),
               "cpu_s_sum": round(sum(r.get("cpu_s", 0) for r in rows), 1),
               "peak_rss_mb_max": max([r.get("peak_rss_mb") or 0 for r in rows], default=0)}
    (outdir / ("RECEIPT_%s.json" % time.strftime("%Y%m%dT%H%M%S"))).write_text(json.dumps(receipt, indent=1))
    print(json.dumps(receipt), flush=True)
    return rows
