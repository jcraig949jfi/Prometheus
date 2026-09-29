"""Target A fossils (PORTABILITY-01 s6): Archaeon reference specimens -> native records + canonical graphs.

  A1 autonomous copier         hand-written vmcopy replicator self-copies (real VM, real taint)
  A2 inserted lineage          control_inserted resident amplified by a random host (inserted ancestry must not become random)
  A3 block-15 host panel       every INERT ENVGATE-01 block-15 U founder that emits the resident genome, executed on the real VM
  A4 block-13 host rescue      ENVGATE-01 block 13, BLOCK_128 arm, deterministic replay to epoch 14800 (the slow fossil)
  A5 random-origin establishment  the dominant block-13 lineage (a random arrival) -- from the same replay
Frozen ENVGATE code is imported, never edited. Observation-only change: a subclass keeps the birth events that touch the two block-13
fossil arrivals plus a ring of recent births (the frozen World keeps only the first 4000).
    python -m archaeon.causal_lens.fossils_archaeon [--quick]   (--quick skips A4/A5)
"""
from __future__ import annotations

import json
import sys
import time
from collections import deque
from pathlib import Path

from archaeon.z80atlas import vm, tasks as T
from archaeon.envgate import mechanism as M1
from archaeon.lineage import core as LC
from archaeon.lineage import assay_block as AB
from archaeon.causal_lens.adapters import archaeon as AD
from archaeon.causal_lens.schema import Graph, dump, spontaneous

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "archaeon/causal_lens/out/archaeon"
EVID = Path(r"C:\Prometheus-data\evidence\portability01_2026-09-26\archaeon")
REPL = T.pad(T.replicator(True), 32)
RESIDENT15 = bytes.fromhex("c180094094938d528ef73c4ab400de8e7eb7a99cab37f38650832a8d607194a5")
B13_NEAR_COPIER, B13_HOST = 447492, 446966


def _w(name="t"):
    return LC.World(name, 4, (name + ".world", 0), (name + ".mut", 0), inputs=lambda w, c, e: [(0,)] * 3)


def _birth(w, i, j, x):
    nbr = w.genomes[j] if w.genomes[j] is not None else LC.ZERO
    r = vm.execute(w.genomes[i], nbr, (x,), LC.STEP_CAP, True, -1.0)
    assert sum(r["nbr_mask"]) / 32 >= 0.9, "fixture birth below copy_min_frac"
    w._birth(i, j, r["nbr_window"], r, nbr, (x,), 1)
    return w.events[-1]


def a1_autonomous():
    w = _w("a1"); w.insert_ecology(0, REPL, 0, "random_inflow"); ev = _birth(w, 0, 1, 0)
    return w, {"native_mechanism": ev["mechanism"], "native_template": ev["template"], "native_host_glin": ev["host_glin"]}


def _host_x(host, resident):
    for x in range(256):
        r = vm.execute(host, resident, (x,), LC.STEP_CAP, True, -1.0)
        if sum(r["nbr_mask"]) / 32 >= 0.9 and r["nbr_window"] == resident: return x
    return None


def a2_inserted():
    L = json.loads((REPO / "archaeon/envgate/LINEAGES.json").read_text(encoding="utf-8"))["lineages"]
    hosts = [bytes.fromhex(r["founder_tape"]) for r in L if r["block"] == 15 and r["arm"] == "U" and r["founder_class"] == "INERT"]
    h = next(t for t in hosts if _host_x(t, RESIDENT15) is not None)
    w = _w("a2"); gr = w.insert_ecology(1, RESIDENT15, 0, "control_inserted"); w.insert_ecology(0, h, 0, "random_inflow")
    ev = _birth(w, 0, 1, _host_x(h, RESIDENT15))
    return w, {"native_mechanism": ev["mechanism"], "native_child_glin_inserted": w.gl[ev["child_glin"]]["inserted"], "resident_glin": gr}


def a3_block15_panel():
    L = json.loads((REPO / "archaeon/envgate/LINEAGES.json").read_text(encoding="utf-8"))["lineages"]
    hosts = [bytes.fromhex(r["founder_tape"]) for r in L if r["block"] == 15 and r["arm"] == "U" and r["founder_class"] == "INERT"]
    w = LC.World("a3", 0, ("a3.w", 0), ("a3.m", 0), inputs=lambda w, c, e: [(0,)] * 3); gr = w.insert_ecology(0, RESIDENT15, 0, "random_inflow")
    n = 0
    for k, h in enumerate(hosts):
        x = _host_x(h, RESIDENT15)
        if x is None: continue
        cell = 1 + (k % 100); w.insert_ecology(cell, h, 0, "random_inflow"); w.genomes[0] = RESIDENT15
        _birth(w, cell, 0, x); n += 1
        w.glin[0] = gr; w.orig[0] = tuple(w.gl[gr]["founder_oid"] * 32 + p for p in range(32)); w.ins[0] = False
    return w, {"inert_founders": len(hosts), "hosting_births": n, "native_parent_chain_labels": n, "resident_glin": gr}


class _Keep(list):
    """Birth-event store: every event touching the watched arrivals' glins + a ring of the most recent births."""
    def __init__(self, world, watch, ring=20000):
        super().__init__(); self.w = world; self.watch = watch; self.ring = deque(maxlen=ring); self.kept_total = 0

    def _watched(self, g):
        st = self.w.gl.get(g) if g is not None else None
        return bool(st) and st.get("arrival") in self.watch

    def append(self, ev):
        self.kept_total += 1
        if any(self._watched(ev.get(k)) for k in ("executor_glin", "child_glin", "template_glin", "host_glin")) or any(self._watched(c) for c in ev["contributors"]):
            super().append(ev)
        else:
            self.ring.append(ev)

    def __len__(self): return 0          # the frozen cap check `len(events) < event_cap` must always admit


class _WatchWorld(LC.World):
    def __init__(self, *a, **k):
        super().__init__(*a, **k); self.events = _Keep(self, {B13_NEAR_COPIER, B13_HOST})


def a4_block13(until=14800):
    AB.World = _WatchWorld
    try:
        t0 = time.time()
        r = AB.run_block("envgate", 13, {"K_chambers": 2048, "dwell": 64, "refills": 1024}, {"BLOCK_128": M1.ARMS["BLOCK_128"]}, until_epoch=until, keep_worlds=True)
    finally:
        AB.World = LC.World
    w = r["arms"]["BLOCK_128"]["_world"]
    dom = max(w.alive.items(), key=lambda kv: kv[1])[0]; st = w.gl[dom]
    host_glins = [g for g, s in w.gl.items() if s.get("arrival") == B13_HOST]
    native = {"wall_s": round(time.time() - t0, 1), "epochs": until, "births": w.births, "births_by_mechanism": dict(w.births_mech),
              "dominant_glin": dom, "dominant_root": st["root"], "dominant_arrival": st.get("arrival"), "dominant_alive": w.alive[dom],
              "dominant_births": st["births"], "dominant_births_hosted": st["births_hosted"], "dominant_births_self": st["births_self"],
              "dominant_first_birth_mech": st.get("first_birth_mech"), "host_arrival_glins": host_glins,
              "host_credit_to_host_arrival": {g: st["hosts"].get(g, 0) for g in host_glins}, "n_hosts": len(st["hosts"]),
              "events_watched": len(list.__iter__(w.events).__length_hint__() and w.events) if False else sum(1 for _ in list.__iter__(w.events)),
              "events_ring": len(w.events.ring), "genetic_established_at_epoch": w.genetic_establishments()}
    return w, native


def graph_of(w, name, events=None):
    g = AD.from_world(w, events=events); g.meta["fossil"] = name; return g


def summarize(g: Graph) -> dict:
    v = g.check(); hus = g.of_kind("HU"); ts = g.of_kind("TRANSFORMATION")
    kinds = {}
    for t in ts:
        for ty in g.nodes[t]["types"]: kinds[ty] = kinds.get(ty, 0) + 1
    exec_not_contrib = sum(1 for t in ts if isinstance(g.nodes[t]["fields"].get("executor", {}).get("value"), str)
                           and g.nodes[t]["fields"].get("host", {}).get("value") not in (None, "NONE")
                           and not any(g.hu_of(m) in g.contributors_hu(t) for m in g.out(g.nodes[t]["fields"]["executor"]["value"], "owns")))
    labels = {e[2] for e in g.edges if e[1] == "labelled_parent"}
    return {"violations": v[:20], "n_violations": len(v), "hus": len(hus), "events_by_type": kinds, "establishments": sorted(g.establishments()),
            "executor_not_contributor_events": exec_not_contrib, "native_parent_chain_labels": len(labels),
            "spontaneous": {h: spontaneous(g, h) for h in sorted(hus)[:50]}}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    OUT.mkdir(parents=True, exist_ok=True); EVID.mkdir(parents=True, exist_ok=True)
    rep = {}
    for name, fn in (("A1_autonomous_copier", a1_autonomous), ("A2_inserted_lineage", a2_inserted), ("A3_block15_host_panel", a3_block15_panel)):
        w, native = fn(); g = graph_of(w, name); dump(g, str(OUT / (name + ".graph.json")))
        rep[name] = {"native": native, "lens": summarize(g)}
    if "--quick" not in argv:
        w, native = a4_block13()
        watched = list(list.__iter__(w.events)); ring = list(w.events.ring)
        (EVID / "A4_block13_events.json").write_text(json.dumps({"watched": watched, "ring": ring, "native": native}, default=str), encoding="utf-8")
        g = graph_of(w, "A4_block13_host_rescue", events=watched); dump(g, str(EVID / "A4_block13.graph.json"))
        rep["A4_A5_block13"] = {"native": native, "lens": summarize(g)}
    (OUT / "REFERENCE_RESULTS.json").write_text(json.dumps(rep, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: {"n_violations": v["lens"]["n_violations"], "hus": v["lens"]["hus"]} for k, v in rep.items()}))


if __name__ == "__main__":
    main()
