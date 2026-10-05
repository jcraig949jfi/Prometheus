"""X-TASK-GATE v2: endogenous task-coupled descent (operator order 2026-10-05,
roles/Nestor/prompts/2026-10-05_xtg_v2_science_order/). Instrument for PREREG_V2.md in this directory.

The historical freeze (../x_task_gate/, commit 62d30e443) is INVALID (its ERRATA file) and is not executed.
This file repairs exactly the defects recorded there:

  D1/D3 genome-only cache      -> UseCache keyed (task identity, episode set, genome); regression test.
  D1 / W2-10 D1 COEVO rotation -> environment pinned STATIC; one task, FORCED_READ ADD37, never changes.
  D6 base-cell cue index       -> one task, its own cue index (2); use test below makes the reader check implied.
  D15 / W2-10 D4 bridge floor  -> competence = CUE-FLIP USE: each episode (v, key) is run with the regime cue r=0
                                  AND r=1; a pair counts only if BOTH answers are exact (base, base+37).
                                  A program whose answer does not depend on the cue scores 0 by construction.
  D7 stale post-run cache      -> no epoch-seeded episodes; competence is a pure function of (task, genome).
  D9 relabel keeps old comp    -> competence is computed from the organism's CURRENT genome at every use.
  D13 INIT under ATOMIC        -> provenance INIT means "never converted"; in-place mutation is tracked separately.
  Erratum D1 / D14             -> Stage 0 plants CT_UA on the PAIR path; CD is measured there.
  Erratum D2 (oid provenance)  -> per-organism competence ORIGIN: carried in by a birth from a competent donor
                                  (P11_TX / LABEL_TX) vs created at a birth (P11_CREATED / LABEL_CREATED) vs
                                  created by in-place mutation (MUT) vs present at epoch 0 (INIT).

World: the C-A3-INTERNALIZE ffa6 cell (run_dd.CELLS['ffa6']), dense VM, ATOMIC runner, tier M (pop 256,
2000 epochs, slice 300), with atlas_axis NONE, environment STATIC, reproduction PAIR_EXECUTION,
pressure TASK_GATED_INTERACTION. Task scoring uses the plain z8 (tasks.z8) with world ops disabled, exactly
as the world's own scorer does.

    python -B xtg2.py selftest              known-answer + regression tests (also run by test_xtg2.py)
    python -B xtg2.py flight1               static ruler qualification + short pair-path runs
    python -B xtg2.py run <stage> <workers> production stage (0 or 1), resumable
"""
from __future__ import annotations

import gzip
import hashlib
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
ROOT = HERE.parent.parent
W1 = ROOT / "npe-w1-donor-discovery-2026-09-26"
for p in (W1 / "x_donor_discovery", W1 / "x_dd_dense_copy", ROOT / "c9x-explore-2026-09-24" / "x_donor_swap",
          ROOT / "z80atlas-verify-2026-09-22", ROOT.parent / "lib"):
    sys.path.insert(0, str(p))

import tasks  # noqa: E402  (plain z8 lives at tasks.z8: the scoring VM)

# ---------------------------------------------------------------------------------------------- constructs
# W2-10 (inference_saturation_wave2/W2-10_copier_task_genome/construct.py), bytes verbatim.
CT_UA = bytes.fromhex("ED327DEE405FE5DB0047DB004FDB005779FE02380E78A9477AFE00782802C625D3007678D3007679A4B8C8"
                      "3F4C602745135FECC26DAE628982C868A00D767F86")
CT_U = bytes.fromhex("ED327DEE405FE5DB0047DB004FDB005779FE02380578A9D3007678D3007679A4B8C83F4C602745135FECC2"
                     "6DAE628982C868A00D767F86F5E75EB8C61DE6C7F9")


def _w210_pad(g, seed=20261001, n=64):
    rng = random.Random(seed)
    tail = bytearray()
    while len(g) + len(tail) < n:
        tail.append(rng.randrange(256))
    return bytes(g) + bytes(tail)


COPY_ONLY = _w210_pad(bytes.fromhex("ED327DEE405FE5"))
PLANTS = {"CT_UA": CT_UA, "CT_U": CT_U, "COPY_ONLY": COPY_ONLY}

# ---------------------------------------------------------------------------------------------- the task
CELL = "ffa6"
TASK = dict(transform="ADD37", read_order="FORCED_READ", budget=140)
N_PAIRS = 16                      # matched cue-flip pairs per episode set (32 program runs)
GATE_SEED = 43_777_001            # episode set used by the interaction gate and lineage tracking
HELD_SEED = 43_777_002            # disjoint held-out set, readout only
COMP_MIN = 0.75                   # competent iff use score >= COMP_MIN on BOTH sets
TRAJ_EVERY = 50
GATE_FLOOR = 0.15                 # p_interact = 0.15 + 0.85 * max(u_a, u_b)  (historical form)


def task_key(task=None, seed=GATE_SEED, n=N_PAIRS):
    t = dict(TASK if task is None else task)
    return ("STATIC", t["transform"], t["read_order"], t["budget"], seed, n)


def flip_pairs(seed, n=N_PAIRS, task=None):
    """n matched pairs: the same (v, key), cue r = 0 and r = 1. -> [(v, key, base, exp0, exp1)]"""
    t = dict(TASK if task is None else task)
    assert t["read_order"] == "FORCED_READ"
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        v = rng.randrange(256)
        key = rng.randrange(1, 256)
        base = (v ^ key) & 0xFF
        out.append((v, key, base, base, tasks.apply_transform(t["transform"], base)))
    return out


def _answer(g, inputs, budget):
    """tasks.score's VM call, verbatim settings: plain z8, 512-byte scratch arena, OWN policy, ops disabled,
    UNRESTRICTED output, VM cue cost. -> (first output or None, reads before first output)"""
    z8 = tasks.z8
    mem = bytearray(512)
    mem[0:len(g)] = g
    ctx = z8.Ctx(mem, 0, len(g), policy=z8.OWN, inputs=list(inputs), out_gate_reads=0)
    z8.run(ctx, 0, budget, ops_enabled=0x00)
    return (ctx.outputs[0] if ctx.outputs else None), ctx.in_reads_at_first_out


def use_score(g, seed, task=None, n=N_PAIRS):
    """Cue-flip USE score: share of matched pairs answered exactly under BOTH cue values.
    -> dict(u, bridge, reads, answered0, answered1). `bridge` is the historical NEUTRAL_BRIDGE score on the
    same 2n episodes, reported for comparison only."""
    t = dict(TASK if task is None else task)
    g = bytes(g)
    ok = 0
    br = 0.0
    reads = []
    a0n = a1n = 0
    if not g:
        return {"u": 0.0, "bridge": 0.0, "reads": -1, "answered0": 0.0, "answered1": 0.0}
    for v, key, base, e0, e1 in flip_pairs(seed, n, t):
        a0, r0 = _answer(g, (v, key, 0), t["budget"])
        a1, r1 = _answer(g, (v, key, 1), t["budget"])
        ok += (a0 == e0 and a1 == e1)
        for a, e, r in ((a0, e0, r0), (a1, e1, r1)):
            if a is not None:
                reads.append(r)
                br += 1.0 if a == e else (0.5 if a == base else 0.0)
        a0n += a0 is not None
        a1n += a1 is not None
    return {"u": ok / n, "bridge": br / (2 * n), "reads": (sum(reads) / len(reads)) if reads else -1,
            "answered0": a0n / n, "answered1": a1n / n}


class UseCache:
    """Competence cache keyed by (task identity, episode set, genome). Never by genome alone (W2-8 D1)."""

    def __init__(self, task=None):
        self.task = dict(TASK if task is None else task)
        self.d = {}
        self.hits = self.misses = 0

    def get(self, g, seed=GATE_SEED):
        k = (task_key(self.task, seed), hashlib.blake2b(bytes(g), digest_size=12).digest())
        r = self.d.get(k)
        if r is None:
            self.misses += 1
            r = use_score(g, seed, self.task)
            if len(self.d) > 200_000:
                self.d.clear()
            self.d[k] = r
        else:
            self.hits += 1
        return r

    def u(self, g):
        return self.get(g, GATE_SEED)["u"]

    def competent(self, g):
        """Final readout: use >= COMP_MIN on the gate set AND on the disjoint held-out set."""
        return self.get(g, GATE_SEED)["u"] >= COMP_MIN and self.get(g, HELD_SEED)["u"] >= COMP_MIN


# ---------------------------------------------------------------------------------------------- world
ARMS = {
    # stage 0: pair-path ruler qualification (planted, TG gate)
    "PAIR_POS": dict(stage=0, gate="TG", plant="CT_UA"),
    "PAIR_READ_NO_USE": dict(stage=0, gate="TG", plant="CT_U"),
    "PAIR_COPY_ONLY": dict(stage=0, gate="TG", plant="COPY_ONLY"),
    # stage 1: random populations, no plant
    "TG": dict(stage=1, gate="TG", plant=None),
    "SHUF": dict(stage=1, gate="SHUF", plant=None),
}
SEED0 = {0: 43_000_000, 1: 43_100_000, "flight": 43_900_000}


def _import_world():
    import world
    import run_dc
    import run_dd
    import run_ds
    world.z8 = run_dc.dense_z8()
    return world, run_dd, run_ds


def make_runner(arm, seed, epochs=None):
    world, run_dd, run_ds = _import_world()
    a = run_ds.cells()[run_dd.CELLS[CELL]]
    cfg = ARMS[arm]
    cell = dict(a["cell"], atlas_axis="NONE", environment="STATIC", reproduction="PAIR_EXECUTION",
                pressure="TASK_GATED_INTERACTION")
    kw = {}
    if cfg["plant"]:
        kw = dict(implant="ACTUAL_GENOME", implant_bytes=PLANTS[cfg["plant"]])
    Base = run_ds.runner_cls(world)
    cache = UseCache()
    shuf_rng = random.Random(seed * 1_000_003 + 17)     # private: the world RNG never sees the shuffle
    gate = cfg["gate"]

    class XT2(Base):
        def __init__(self, *aa, **kk):
            super().__init__(*aa, **kk)
            self.cache = cache
            self.st = {}            # Org -> lineage/competence state (Org objects persist on the pair tape)
            self.roots = []         # competence-creation events
            self.p11_edges = []     # (epoch, child_oid, parent_oid, p11_pass)
            self.n_pairs = self.n_gate_pass = 0
            self.traj = []          # every TRAJ_EVERY epochs: CS, CD, CD_TX, p11_born (descriptive; verdicts read final)

        # ---- competence of the CURRENT genome (D9): computed at every use, cached by (task, genome)
        def _u(self, o):
            u = self.cache.u(self._genome(o))
            o.comp = u
            return u

        def _comp(self, g):
            return self.cache.u(g) >= COMP_MIN

        def _validate(self, force=False):
            # STATIC task, no epoch-seeded episodes: the world's bridge-scored validation is replaced by the use
            # ruler, read lazily at the gate. Nothing else in this cell reads comp/held (pressure TG on the pair
            # tape: no QD map, reaping oldest-first only above pop cap, which the pair tape never exceeds).
            if not force:
                return
            for o in self.orgs:
                if o.alive:
                    g = self._genome(o)
                    o.comp = self.cache.u(g)
                    o.held = self.cache.get(g, HELD_SEED)["u"]
                    o.probe = self.cache.get(g, GATE_SEED)["reads"]

        def _env_epoch(self):
            assert self.cell["environment"] == "STATIC"

        def step(self):
            super().step()
            if self.epoch % TRAJ_EVERY == 0 and self.st:
                alive = [o for o in self.orgs if o.alive]
                n = max(1, len(alive))
                comp = [o for o in alive if self.cache.competent(self._genome(o))]
                self.traj.append({"e": self.epoch, "CS": round(len(comp) / n, 4),
                                  "CD": round(sum(self.st[o]["prov"] == "P11" for o in comp) / n, 4),
                                  "CD_TX": round(sum(self.st[o]["prov"] == "P11" and self.st[o]["origin"] == "P11_TX"
                                                     for o in comp) / n, 4),
                                  "p11_born": round(sum(self.st[o]["prov"] == "P11" for o in alive) / n, 4)})

        def _root(self, kind, o):
            self.roots.append({"id": len(self.roots), "kind": kind, "epoch": self.epoch, "oid": o.oid})
            return len(self.roots) - 1

        def _init_state(self):
            for o in self.orgs:
                if o.alive and o not in self.st:
                    c = self._comp(self._genome(o))
                    self.st[o] = {"prov": "INIT", "born": 0, "comp": c,
                                  "origin": "INIT" if c else None, "origin_epoch": 0 if c else None,
                                  "root": self._root("INIT", o) if c else None, "tx_p11": 0, "tx_any": 0}

        def _pair_epoch(self):
            if not self.st:
                self._init_state()
            alive = [o for o in self.orgs if o.alive]
            self.rng.shuffle(alive)
            for i in range(0, len(alive) - 1, 2):
                a_, b_ = alive[i], alive[i + 1]
                if gate == "TG":
                    c_, d_ = a_, b_
                else:   # SHUF: the gate reads two OTHER random live organisms (private RNG)
                    c_, d_ = alive[shuf_rng.randrange(len(alive))], alive[shuf_rng.randrange(len(alive))]
                self.n_pairs += 1
                if self.rng.random() > GATE_FLOOR + (1 - GATE_FLOOR) * max(self._u(c_), self._u(d_)):
                    continue
                self.n_gate_pass += 1
                self._pair_interact(i, a_, b_)

        def _pair_interact(self, i, a_, b_):
            pre = {o: (o.oid, self._genome(o)) for o in (a_, b_)}
            pst = {o: dict(self.st[o]) for o in (a_, b_)}   # donor state BEFORE either half is updated
            nlin = len(self.lineage)
            super()._pair_interact(i, a_, b_)            # world pair interaction + ATOMIC write-back
            births = {e["child"]: e for e in self.lineage[nlin:] if e["kind"] == "birth"}
            for o in (a_, b_):
                donor = b_ if o is a_ else a_
                oid0, g0 = pre[o]
                g1 = self._genome(o)
                old = self.st[o]
                if o.oid != oid0:                         # converted: a birth onto this half
                    e = births[o.oid]
                    prov = "P11" if e["causal"] else "LABEL"
                    self.p11_edges.append((self.epoch, o.oid, e["parent"], int(bool(e["causal"]))))
                    c1 = self._comp(g1)
                    dg = pre[donor][1]
                    cd = self._comp(dg)
                    dst = pst[donor]
                    new = {"prov": prov, "born": self.epoch, "comp": c1, "origin": None, "origin_epoch": None,
                           "root": None, "tx_p11": 0, "tx_any": 0, "donor_comp": cd}
                    if c1:
                        if cd and dst.get("root") is not None:
                            new.update(origin=prov + "_TX", origin_epoch=self.epoch, root=dst["root"],
                                       tx_p11=dst["tx_p11"] + (prov == "P11"), tx_any=dst["tx_any"] + 1)
                        else:
                            new.update(origin=prov + "_CREATED", origin_epoch=self.epoch,
                                       root=self._root(prov + "_CREATED", o))
                    self.st[o] = new
                elif g1 != g0:                            # in-place change (ATOMIC mutation)
                    c1 = self._comp(g1)
                    if c1 and not old["comp"]:
                        old.update(comp=True, origin="MUT", origin_epoch=self.epoch, root=self._root("MUT", o),
                                   tx_p11=0, tx_any=0)
                    elif not c1 and old["comp"]:
                        old.update(comp=False, origin=None, origin_epoch=None, root=None, tx_p11=0, tx_any=0)

    r = XT2(cell, seed, tier=a["tier"], max_epochs=epochs, **kw)
    assert r.d["has_task"] and r.cell["environment"] == "STATIC"
    assert r.spec.transform == TASK["transform"] and r.spec.read_order == TASK["read_order"]
    assert r.spec.cue_index() == 2
    return r


def readout(r, out):
    """Per-run row over live organisms at the final epoch. Pure function of the world state + caches."""
    _parent, causal_parent, _bn, _mv = r._lineage_graph()
    _d, per_causal = r._depths(causal_parent)
    alive = [o for o in r.orgs if o.alive]
    n = max(1, len(alive))
    rows = []
    for o in alive:
        g = r._genome(o)
        gs, hs = r.cache.get(g, GATE_SEED), r.cache.get(g, HELD_SEED)
        comp = gs["u"] >= COMP_MIN and hs["u"] >= COMP_MIN
        st = r.st.get(o, {"prov": "INIT", "origin": None})
        rows.append({"oid": o.oid, "prov": st["prov"], "comp": comp, "u_gate": gs["u"], "u_held": hs["u"],
                     "bridge": round(gs["bridge"], 4), "reads": gs["reads"], "origin": st.get("origin"),
                     "origin_epoch": st.get("origin_epoch"), "root": st.get("root"),
                     "tx_p11": st.get("tx_p11", 0), "tx_any": st.get("tx_any", 0),
                     "cdepth": per_causal.get(o.oid, 0), "g": g.hex()})
    comp = [x for x in rows if x["comp"]]

    def share(pred):
        return round(sum(1 for x in rows if pred(x)) / n, 4)
    roots_live = {}
    for x in comp:
        if x["root"] is not None:
            k = r.roots[x["root"]]["kind"]
            roots_live[k] = roots_live.get(k, 0) + 1
    gen = {}
    for x in comp:
        gen[x["g"]] = gen.get(x["g"], 0) + 1
    rec = {
        "alive": len(alive),
        "CS": share(lambda x: x["comp"]),
        "CD": share(lambda x: x["comp"] and x["prov"] == "P11"),
        "CD_TX": share(lambda x: x["comp"] and x["prov"] == "P11" and x["origin"] == "P11_TX"),
        "label_only": share(lambda x: x["comp"] and x["prov"] == "LABEL"),
        "init_share": share(lambda x: x["comp"] and x["prov"] == "INIT"),
        "mut_created": share(lambda x: x["comp"] and x["origin"] in ("MUT", "P11_CREATED", "LABEL_CREATED")),
        "origin_counts": _count(x["origin"] for x in comp),
        "prov_counts_all": _count(x["prov"] for x in rows),
        "p11_born_share": share(lambda x: x["prov"] == "P11"),
        "comp_root_kinds_live": roots_live,
        "max_tx_p11_live": max([x["tx_p11"] for x in comp], default=0),
        "max_cdepth_competent": max([x["cdepth"] for x in comp], default=0),
        "bridge_ge_0.5_and_reader": share(lambda x: x["bridge"] >= 0.5 and x["reads"] >= 3),
        "depth": out["max_causal_replication_depth"], "depth_pred": out["max_predecessor_replication_depth"],
        "p11_events": out["p11_events"], "replication_events": out["replication_events"],
        "pairs_considered": r.n_pairs, "pairs_interacted": r.n_gate_pass,
        "interaction_rate": round(r.n_gate_pass / max(1, r.n_pairs), 4),
        "n_roots": len(r.roots), "root_kinds_all": _count(x["kind"] for x in r.roots),
        "cache_hits": r.cache.hits, "cache_misses": r.cache.misses,
        "voided": out.get("voided"), "flags": out.get("flags"),
        "traj": r.traj,
        "CD_TX_peak": max([x["CD_TX"] for x in r.traj], default=0.0),
        "CS_peak": max([x["CS"] for x in r.traj], default=0.0),
    }
    return rec, {"competent_genomes": gen, "organisms": [{k: v for k, v in x.items() if k != "g" or x["comp"]}
                                                         for x in rows],
                 "roots": r.roots}


def _count(it):
    d = {}
    for k in it:
        d[str(k)] = d.get(str(k), 0) + 1
    return d


def run_one(arm, seed, outdir, epochs=None):
    t0 = time.time()
    c0 = time.process_time()
    r = make_runner(arm, seed, epochs)
    out = r.run()
    rec, detail = readout(r, out)
    rec.update(arm=arm, seed=seed, stage=ARMS[arm]["stage"], plant=ARMS[arm]["plant"], epochs=r.epoch,
               wall_s=round(time.time() - t0, 1), cpu_s=round(time.process_time() - c0, 1),
               peak_rss_mb=_peak_rss_mb(), host=platform.node())
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stem = "%s_%d" % (arm, seed)
    with gzip.open(outdir / (stem + ".detail.json.gz"), "wt") as f:
        json.dump(dict(detail, p11_edges=r.p11_edges), f)
    (outdir / (stem + ".json")).write_text(json.dumps(rec))
    return rec


def _peak_rss_mb():
    try:
        import psutil
        mi = psutil.Process().memory_info()
        return round(getattr(mi, "peak_wset", mi.rss) / 2**20, 1)
    except Exception:
        return None


# ---------------------------------------------------------------------------------------------- verdicts
SHARE_MIN = 0.10


def stage0_verdict(res):
    by = {a: [r for r in res if r["arm"] == a] for a in ("PAIR_POS", "PAIR_READ_NO_USE", "PAIR_COPY_ONLY")}
    pos = sum(r["CD_TX"] >= SHARE_MIN for r in by["PAIR_POS"])
    neg = {a: sum(r["CD"] >= SHARE_MIN for r in by[a]) for a in ("PAIR_READ_NO_USE", "PAIR_COPY_ONLY")}
    neg_cs = {a: sum(r["CS"] >= SHARE_MIN for r in by[a]) for a in ("PAIR_READ_NO_USE", "PAIR_COPY_ONLY")}
    copying = {a: sum(r["p11_born_share"] >= SHARE_MIN for r in v) for a, v in by.items()}
    if pos < 3:
        v = "INSTRUMENT_UNREACHABLE"
    elif any(neg.values()) or any(neg_cs.values()):
        v = "INSTRUMENT_INVALID_NEGATIVE_PASSED"
    else:
        v = "PASS"
    return {"stage0": v, "pos_runs_CD_TX_ge_0.10": pos, "neg_runs_CD_ge_0.10": neg, "neg_runs_CS_ge_0.10": neg_cs,
            "runs_p11_born_share_ge_0.10": copying,
            "negatives_dynamically_nonvacuous": {a: copying[a] >= 3 for a in neg},
            "pos_runs_CD_ge_0.10": sum(r["CD"] >= SHARE_MIN for r in by["PAIR_POS"])}


def stage1_verdict(res):
    arm = {a: [r for r in res if r["arm"] == a] for a in ("TG", "SHUF")}
    reg = {a: sum(r["depth"] >= 20 for r in v) for a, v in arm.items()}
    cs = {a: sum(r["CS"] >= SHARE_MIN for r in v) for a, v in arm.items()}
    tx = {a: sum(r["CD_TX"] >= SHARE_MIN for r in v) for a, v in arm.items()}
    cd = {a: sum(r["CD"] >= SHARE_MIN for r in v) for a, v in arm.items()}
    if min(reg.values()) < 4:
        cls = "NO_REPLICATOR_REGIME"
    elif cs["TG"] < 3:
        cls = "FLOOR"
    elif tx["TG"] < 2:
        cls = "GATE_OR_SORTING_ARTIFACT"
    elif tx["TG"] >= 4 and tx["TG"] >= tx["SHUF"] + 3:
        cls = "ENDOGENOUS_TASK_COUPLED"
    elif tx["TG"] >= 4 and tx["SHUF"] >= tx["TG"] - 2:
        cls = "ENDOGENOUS_UNCOUPLED"
    else:
        cls = "MIXED"
    return {"verdict": cls, "regime_runs_depth_ge_20": reg, "runs_CS_ge_0.10": cs, "runs_CD_TX_ge_0.10": tx,
            "runs_CD_ge_0.10_descriptive": cd}


# ---------------------------------------------------------------------------------------------- self-tests
def selftest():
    res = {}
    c = UseCache()
    s = {k: c.get(g) for k, g in PLANTS.items()}
    h = {k: c.get(g, HELD_SEED) for k, g in PLANTS.items()}
    res["use_gate"] = {k: v["u"] for k, v in s.items()}
    res["use_held"] = {k: v["u"] for k, v in h.items()}
    res["bridge_gate"] = {k: v["bridge"] for k, v in s.items()}
    res["reads"] = {k: v["reads"] for k, v in s.items()}
    assert c.competent(CT_UA), "KA-1 CT_UA must be competent"
    assert not c.competent(CT_U) and s["CT_U"]["u"] == 0.0, "KA-2 CT_U must fail use (score 0)"
    assert s["CT_U"]["bridge"] >= 0.5 and s["CT_U"]["reads"] >= 3, "KA-2b CT_U passes the OLD bridge+reader ruler"
    assert not c.competent(COPY_ONLY) and s["COPY_ONLY"]["u"] == 0.0, "KA-3 COPY_ONLY must fail"
    w = tasks.witness(tasks.TaskSpec(transform="ADD37", read_order="FORCED_READ"))
    assert use_score(w, GATE_SEED)["u"] == 1.0, "KA-4 world witness must score 1.0"
    # regime-blind 'echo base' (D15): reads all three inputs, ignores the cue
    eb = tasks.z8.asm("IN\nLD B,A\nIN\nXOR B\nLD B,A\nIN\nLD A,B\nOUT\nHALT")[0]
    assert use_score(eb, GATE_SEED)["u"] == 0.0 and use_score(eb, GATE_SEED)["bridge"] >= 0.7, "KA-5 echo-base"
    # always-transform guesser: never reads the cue meaningfully
    ag = tasks.z8.asm("IN\nLD B,A\nIN\nXOR B\nADD A,37\nOUT\nHALT")[0]
    assert use_score(ag, GATE_SEED)["u"] == 0.0, "KA-6 always-transform"
    # REGRESSION (W2-8 D1): same genome, different task identity -> no cross-task hit
    t2 = dict(TASK, transform="XOR5A")
    c2 = UseCache()
    u1 = c2.get(w)["u"]
    k1 = (task_key(TASK), hashlib.blake2b(w, digest_size=12).digest())
    k2 = (task_key(t2), hashlib.blake2b(w, digest_size=12).digest())
    assert k1 != k2, "RG-1 cache key must include task identity"
    c3 = UseCache(t2)
    c3.d = c2.d                      # share the underlying store: a genome-only key would hit here
    u2 = c3.get(w)["u"]
    assert u1 == 1.0 and u2 == 0.0 and c3.misses == 1, "RG-1 cross-task cache leak"
    # REGRESSION: episode sets are keyed separately (gate vs held)
    assert task_key(seed=GATE_SEED) != task_key(seed=HELD_SEED)
    # cue-flip pairs really flip: expected answers always differ (37 != 0 mod 256)
    assert all(e0 != e1 for *_x, e0, e1 in flip_pairs(GATE_SEED) + flip_pairs(HELD_SEED))
    res["witness_u"] = 1.0
    res["regression_cache_cross_task"] = {"u_ADD37": u1, "u_XOR5A_same_genome": u2}
    res["pass"] = True
    return res


def _job(args):
    return run_one(*args)


def pool_run(jobs, outdir, workers):
    """One job per process (maxtasksperchild=1: the world module is patched per process). Resumable: a job whose
    row file exists is skipped. Writes RECEIPT_<name>.json (host, CPU only, workers, wall, peak RSS per run)."""
    import multiprocessing as mp
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    done = {p.stem for p in outdir.glob("*.json") if not p.name.startswith("RECEIPT")}
    todo = [j for j in jobs if "%s_%d" % (j[0], j[1]) not in done]
    t0 = time.time()
    start = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    with mp.Pool(workers, maxtasksperchild=1) as pool:
        for rec in pool.imap_unordered(_job, [(a, s, outdir, e) for a, s, e in todo]):
            print(json.dumps({k: rec[k] for k in ("arm", "seed", "CS", "CD", "CD_TX", "CD_TX_peak", "depth",
                                                  "p11_events", "wall_s", "peak_rss_mb")}), flush=True)
    rows = [json.loads(p.read_text()) for p in sorted(outdir.glob("*.json")) if not p.name.startswith("RECEIPT")]
    receipt = {"host": platform.node(), "compute": "CPU only", "workers": workers, "logical_cpus": os.cpu_count(),
               "start": start, "end": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "wall_s_this_call": round(time.time() - t0, 1),
               "jobs_this_call": len(todo), "rows": len(rows),
               "peak_rss_mb_max": max([r.get("peak_rss_mb") or 0 for r in rows], default=0),
               "run_wall_s_mean": round(sum(r["wall_s"] for r in rows) / max(1, len(rows)), 1)}
    (outdir / ("RECEIPT_%s.json" % time.strftime("%Y%m%dT%H%M%S"))).write_text(json.dumps(receipt, indent=1))
    print(json.dumps(receipt, indent=1))
    return rows


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "selftest":
        print(json.dumps(selftest(), indent=1))
    elif cmd == "flight":
        n, ep, w = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        arms = sys.argv[5].split(",")
        f = SEED0["flight"]
        pool_run([(a, f + s, ep) for s in range(n) for a in arms], HERE / "flights" / sys.argv[6], w)
    elif cmd == "one":
        print(json.dumps(run_one(sys.argv[2], int(sys.argv[3]), HERE / "scratch",
                                 int(sys.argv[4]) if len(sys.argv) > 4 else None), indent=1))
