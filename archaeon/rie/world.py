"""RIE-01 world runner + observatory. One world = f(spec, seed index); deterministic; replay recipe = run_world(spec, seed) at the commit.

Pairing: the inflow tape stream and the world/mutation seeds are keyed by the SEED INDEX only (not by cell), so worlds with the same seed
index receive the same random tapes in the same order across every regime/topology/substrate cell (common random numbers); a world's
environment stream is keyed by (cell, seed). Exposure denominator: arrivals = K * (T_in / dwell), fixed by spec, checked after the run.

Observatory (operator directive C5) -- computed from the attributed core (archaeon.lineage.core), never from tape similarity:
  origin        a genetic lineage appears: an arrival glin that reproduces, or an ORIGINATION glin (new genome from existing material)
  reproduction  births with child glin G      establishment  core.genetic_establishments()
  amplification births of G by other executors (births_hosted)
  dependency    ENV_GATED (dominant genome copies exactly at 1..255 inputs), ENV_FREE (all 256 / input-blind), HOST_DEPENDENT (hosted > self)
  liberation    founder EXACT_GATED -> dominant descendant with a strictly larger exact-input set (or ungated); or early hosted -> later self
  acquisition   founder a self-copier (EXACT/NEAR/SPAN) -> established descendant that the ruler calls a non-copier and that is mostly hosted
  takeover      one glin >= 90% of the ecology at an observation      coexistence  >= 2 glins each >= 10% for >= 3 x max_age epochs
  mechanism     EXACT_UNGATED_COPIER / EXACT_GATED_COPIER / LOWFI_COPIER / HOST_AMPLIFIED / ORIGINATED_GENOME / UNCLASSIFIED_REPRODUCTIVE_MECHANISM
                (an established glin whose dominant genome the empty-neighbour ruler cannot place as a copier yet which reproduces mostly by
                itself, or anything matching no rule) ; role FOREIGN_EXECUTOR for glins that host >= 10 sampled births of other glins
"""
from __future__ import annotations

import hashlib
import json
import time
from collections import Counter, defaultdict

from proteus.foundry.prng import SplitMix64, seed_from
from archaeon.z80atlas.census import copier_census as C
from archaeon.z80atlas.grammar import FROZEN as F
from archaeon.envgate.ruler import measure as measure_vmcopy
from archaeon.lineage import core as LC
from archaeon.rie import physics as P

LABEL = "rie01"
INFLOW = {"BELOW": 32, "REPLACE": 256, "STRONG": 2048}                     # chambers; dwell 64 -> 0.5 / 4 / 32 arrivals per epoch
DWELL = 64
COPIER = {"EXACT_UNGATED", "EXACT_GATED", "NEAR_COPIER", "SPAN_COPIER"}
OBS_EVERY = 50; SNAP_EVERY = 500; COEXIST_OBS = (3 * F["max_age"]) // OBS_EVERY + 1
RULER_EVERY = 8                                                          # latent-class ruler on a fixed 1-in-8 arrival sample (x8 estimate)


def spec_id(spec: dict) -> str:
    return hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()[:12]


def ruler(tape: bytes, substrate: str, memo) -> dict:
    if substrate == "vmcopy": return measure_vmcopy(tape, memo)
    ph = C.sweep(tape, False); cls = C.classify(ph, len(tape)); out = {"class": cls}
    if cls in COPIER or any(p["birth"] for p in ph):
        out.update({"exact_inputs": [p["x"] for p in ph if p["exact"]], "birth_inputs": [p["x"] for p in ph if p["birth"]]})
    return out


def inflow(seed: int, tapes=None):
    if tapes is not None:
        yield from tapes; return
    r = SplitMix64(seed_from(LABEL + ".inflow", seed))
    while True:
        yield bytes(r.randbelow(256) for _ in range(LC.G))


def run_world(spec: dict, seed: int, tapes=None, origin=LC.ORIGIN_INFLOW, control_residents=None, all_cases: bool = False) -> dict:
    """all_cases=False executes only case 0: under implicit_survival cases 1..2 only compute an unused task score (no RNG, no state);
    births and telemetry are identical either way (tested)."""
    sid = spec_id(spec); K = INFLOW[spec["inflow"]]; T = spec["T"]; T_in = T - LC.PERSIST - 1; cp = spec["substrate"] == "vmcopy"
    base_inputs = P.make_inputs(spec["regime"], "%s.env|%s|%d" % (LABEL, sid, seed))
    inputs = base_inputs if all_cases else (lambda w_, c_, e_: base_inputs(w_, c_, e_)[:1])
    w = LC.World(sid, K, (LABEL + ".world", seed), (LABEL + ".mutation", seed), inputs, P.neighbour_fn(spec["topology"]), copy_prim=cp)
    memo = LC.Memo(cp); stream = inflow(seed, tapes); ruler_counts = Counter(); hits = {}; arrival = 0; t0 = time.time()
    for cell, tape, org in (control_residents or []): w.insert_ecology(cell, tape, 0, org)
    comp_runs = defaultdict(int); coexist_episodes = 0; takeover_obs = 0; takeover_glins = Counter(); snaps = []; cur_run = 0
    for epoch in range(T):
        if epoch < T_in and epoch % DWELL == 0:
            for c in range(K):
                t = next(stream)
                if arrival % RULER_EVERY == 0:
                    rv = ruler(t, spec["substrate"], memo if cp else None); ruler_counts[rv["class"]] += 1
                    if rv["class"] in COPIER: hits[arrival] = dict(rv, tape=t.hex(), epoch_in=epoch)
                w.arrive(LC.N + c, t, arrival, epoch, origin); arrival += 1
        if epoch == T_in: w.clear_chambers(epoch)
        w.step(epoch, memo)
        if epoch % OBS_EVERY == 0:
            occ = [w.glin[i] for i in range(LC.N) if w.genomes[i] is not None]; cnt = Counter(occ); n = len(occ)
            big = [g for g, c in cnt.items() if n and c >= 0.1 * n]
            if n and max(cnt.values()) >= 0.9 * n: takeover_obs += 1; takeover_glins[max(cnt, key=cnt.get)] += 1
            if len(big) >= 2: cur_run += 1
            else:
                if cur_run >= COEXIST_OBS: coexist_episodes += 1
                cur_run = 0
        if epoch % SNAP_EVERY == 0 or epoch == T - 1:
            dom = defaultdict(Counter)
            for i in range(LC.N):
                if w.genomes[i] is not None: dom[w.glin[i]][w.genomes[i]] += 1
            snaps.append({"epoch": epoch, "glins": {g: {"n": sum(c.values()), "dominant": c.most_common(1)[0][0].hex()} for g, c in dom.items() if sum(c.values()) >= 5}})
    if cur_run >= COEXIST_OBS: coexist_episodes += 1
    expected_arrivals = K * len(range(0, T_in, DWELL))
    est = set(w.genetic_establishments())
    host_roles = Counter(e["executor_glin"] for e in w.events if e["mechanism"].startswith("HOST_EXECUTION"))
    glins = {}
    for g, st in w.gl.items():
        if st["births"] < 3 and g not in est: continue
        last_dom = None
        for s in reversed(snaps):
            if g in s["glins"]: last_dom = s["glins"][g]["dominant"]; break
        glins[g] = observe(w, g, st, last_dom, hits, spec, memo if cp else None, host_roles, g in est)
    return {"schema": "archaeon.rie.world.v1", "spec": spec, "spec_id": sid, "seed": seed, "origin": origin, "arrivals": arrival, "expected_arrivals": expected_arrivals,
            "exposure_ok": arrival == expected_arrivals, "epochs": T, "ruler_sample_every": RULER_EVERY, "ruler_counts_sample": dict(ruler_counts),
            "latent_copier_arrivals_sample": len(hits), "latent_exact_arrivals_sample": sum(1 for h in hits.values() if h["class"].startswith("EXACT")),
            "births": w.births, "births_by_mechanism": dict(w.births_mech), "taint_calls": w.taint_calls, "fast_calls": w.fast_calls,
            "final_pop": sum(1 for i in range(LC.N) if w.genomes[i] is not None), "genetic_established": sorted(est),
            "takeover_observations": takeover_obs, "takeover_glins": dict(takeover_glins), "coexistence_episodes": coexist_episodes,
            "glins": glins, "snapshots": snaps[-12:], "telemetry": w.telemetry[::4], "events_sample": w.events[:600], "wall_s": round(time.time() - t0, 1),
            "replay": {"call": "archaeon.rie.world.run_world(spec, seed)", "spec": spec, "seed": seed}}


def observe(w, g, st, last_dom, hits, spec, memo, host_roles, established):
    arr = st.get("arrival"); founder_tape = st.get("tape")
    fcls = ruler(bytes.fromhex(founder_tape), spec["substrate"], memo) if founder_tape else {"class": None}
    dcls = ruler(bytes.fromhex(last_dom), spec["substrate"], memo) if last_dom else {"class": None}
    fx = set(fcls.get("exact_inputs", [])); dx = set(dcls.get("exact_inputs", []))
    hosted = st["births_hosted"]; selfb = st["births_self"]
    dep = []
    if dx and len(dx) < 256: dep.append("ENV_GATED")
    if len(dx) == 256: dep.append("ENV_FREE")
    if hosted > selfb: dep.append("HOST_DEPENDENT")
    liberation = bool((fcls["class"] == "EXACT_GATED" and dx and (len(dx) > len(fx) or len(dx) == 256)))
    acquisition = bool(fcls["class"] in COPIER and dcls["class"] not in COPIER and dcls["class"] is not None and hosted > selfb)
    if st["root"] == "origination": mech = "ORIGINATED_GENOME"
    elif hosted > 0.5 * max(1, st["births"]): mech = "HOST_AMPLIFIED"
    elif dcls["class"] == "EXACT_UNGATED": mech = "EXACT_UNGATED_COPIER"
    elif dcls["class"] == "EXACT_GATED": mech = "EXACT_GATED_COPIER"
    elif dcls["class"] in ("NEAR_COPIER", "SPAN_COPIER"): mech = "LOWFI_COPIER"
    else: mech = "UNCLASSIFIED_REPRODUCTIVE_MECHANISM"
    return {"root": st["root"], "origin": st["origin"], "inserted": st["inserted"], "arrival": arr, "epoch": st["epoch"], "births": st["births"], "births_self": selfb,
            "births_hosted": hosted, "n_hosts": len(st["hosts"]), "exact": st["exact"], "peak": st["peak"], "max_ggen": st["max_ggen"], "established": established,
            "first_birth_epoch": st["first_birth_epoch"], "first_birth_input": st["first_birth_input"], "first_birth_mech": st.get("first_birth_mech"),
            "founder_tape": founder_tape, "founder_class": fcls["class"], "founder_exact_inputs": sorted(fx)[:40], "dominant_genome": last_dom, "dominant_class": dcls["class"],
            "dominant_exact_inputs": sorted(dx)[:40], "dominant_n_exact": len(dx), "dependency": dep, "liberation": liberation, "acquisition": acquisition,
            "mechanism": mech, "foreign_executor_role": host_roles.get(g, 0) >= 10, "parents": st.get("parents"), "last_alive": st["last_alive"], "root_end": st["root_end"]}


def world_score(res: dict) -> float:
    """Frozen promotion score over OBSERVABLE CLASSES (directive C7/C9); never tape similarity."""
    s = 0.0
    for gg in res["glins"].values():
        if not gg["established"] or gg["inserted"]: continue
        s += 1
        if gg["mechanism"] == "ORIGINATED_GENOME": s += 3
        if gg["mechanism"] == "UNCLASSIFIED_REPRODUCTIVE_MECHANISM": s += 2
        if gg["liberation"]: s += 2
        if gg["acquisition"]: s += 2
        if gg["mechanism"] == "HOST_AMPLIFIED": s += 1
        if gg["foreign_executor_role"]: s += 1
    s += res["coexistence_episodes"]
    return s
