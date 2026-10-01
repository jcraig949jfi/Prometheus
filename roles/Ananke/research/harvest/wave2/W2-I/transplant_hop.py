"""W2-I TASK 1: hop-matched topology->random transplants of frozen C1 laws. NOT a search.

usage: python transplant_hop.py MODE CID8 [CID8 ...]
  MODE main    native@d0, C1-random@d0 (the D-wave transplant), C1-random@d_h, and for MAJ
               also C1-random@d_h with INWARD placement (sensors d_h hops upstream of the
               actuator; envs.build places MAJ sensors by OUT-distance from the actuator).
  MODE lite    native@d0 and C1-random@d_h (+ inward for MAJ) only (W-I panel extras).
  MODE hopscan native ring at d = r+1 and 2r (two hops): does the law cross 2 hops at all?
  MODE fact2   portshuffle, flatdist, schreier_flatdist@d_h, clique@d_h (cells failing hop-matched).
  MODE ringlabels schreier_ringdist@d_h only.
  MODE clique  clustered non-lattice graph (two random K4 partitions, degree 6) at d_h and d0.
  MODE fact    factorial graph variants for ring cells (ring_relabel, ring_portshuffle,
               ring_flatdist at d0; schreier_ringdist / schreier_flatdist at d_h and d0).
Every condition uses the same 64 fresh worlds (32 mirror pairs) in namespace W2GI, tag 0x11.
Writes out/<mode>_<cid8>.json (one file per cell). CPU, 2 threads.
"""
import dataclasses
import json
import sys
import time

from w2i_common import (OUT, NS, c1_random, hop_matched_d, inward_placement, load, patched,
                        score, seeds_for, signal_hops, variant)

mode, cids = sys.argv[1], sys.argv[2:]
S = seeds_for(0x11, 64)
for cid in cids:
    t0, c0 = time.time(), time.process_time()
    r, ph, env, g = load(cid)
    G = g[None]
    dh = hop_matched_d(ph, env)
    fam = env.family
    res = {"cell": cid, "row_kind": r["kind"], "wave": r["wave"], "family": fam,
           "topology": ph.topology, "radius": ph.radius, "n_sites": ph.n_sites, "d0": env.d, "d_h": dh,
           "dest_mode": ph.dest_mode, "plastic_route": ph.plastic_route,
           "recorded_held": r["result"].get("held", {}).get("acc"),
           "recorded_held_lo99": r["result"].get("held", {}).get("lo99"),
           "conds": {}, "hops": {}}
    envh = dataclasses.replace(env, d=dh)

    def run(name, p2, e2, inward=False, patch=None):
        if patch is not None:
            nb, ds, M = patch
            with patched(nb, ds, M):
                res["conds"][name] = score(p2, G, e2, S)[0]
                res["hops"][name] = signal_hops(p2, e2, S[:32], nbr=nb)
        elif inward:
            with inward_placement(p2):
                res["conds"][name] = score(p2, G, e2, S)[0]
                res["hops"][name] = signal_hops(p2, e2, S[:32])
        else:
            res["conds"][name] = score(p2, G, e2, S)[0]
            res["hops"][name] = signal_hops(p2, e2, S[:32])
        print(cid, name, res["conds"][name], res["hops"][name], flush=True)

    if mode in ("main", "lite"):
        run("native@d0", ph, env)
        if ph.topology != "global" or mode == "main":
            rnd = c1_random(ph)
            if mode == "main":
                run("C1random@d0", rnd, env)
            run("C1random@dh", rnd, envh)
            if fam == "MAJ":
                run("C1random@dh_inward", rnd, envh, inward=True)
    elif mode == "fact":
        assert ph.topology == "ring"
        seed = H = NS ^ 0xFAC7
        for vn, dd in (("ring_relabel", env.d), ("ring_portshuffle", env.d), ("ring_flatdist", env.d),
                       ("schreier_ringdist", dh), ("schreier_flatdist", dh), ("schreier_ringdist", env.d)):
            p2, nb, ds, M, info = variant(ph, vn, seed)
            if info:
                res.setdefault("info", {})[vn] = info
            run("%s@d%d" % (vn, dd), p2, dataclasses.replace(env, d=dd), patch=(nb, ds, M))
    elif mode == "fact2":
        # decomposition for cells that FAIL the hop-matched C1 transplant
        assert ph.topology == "ring"
        for vn, dd, sd in (("ring_portshuffle", env.d, NS ^ 0xFAC7), ("ring_flatdist", env.d, NS ^ 0xFAC7),
                           ("schreier_flatdist", dh, NS ^ 0xFAC7), ("clique2x4_flatdist", dh, NS ^ 0xC11C)):
            p2, nb, ds, M, info = variant(ph, vn, sd)
            if info:
                res.setdefault("info", {})[vn] = info
            run("%s@d%d" % (vn, dd), p2, dataclasses.replace(env, d=dd), patch=(nb, ds, M))
    elif mode == "ringlabels":
        # do the ring's per-port distance labels (latency) restore a law on a tree-like graph?
        assert ph.topology == "ring"
        p2, nb, ds, M, info = variant(ph, "schreier_ringdist", NS ^ 0xFAC7)
        run("schreier_ringdist@d%d" % dh, p2, dataclasses.replace(env, d=dh), patch=(nb, ds, M))
    elif mode == "clique":
        # clustered non-lattice graph at the hop-matched distance (and at d0 for reference)
        assert ph.topology == "ring"
        seed = NS ^ 0xC11C
        for dd in (dh, env.d):
            p2, nb, ds, M, info = variant(ph, "clique2x4_flatdist", seed)
            res.setdefault("info", {})["clique2x4_flatdist"] = info
            run("clique2x4_flatdist@d%d" % dd, p2, dataclasses.replace(env, d=dd), patch=(nb, ds, M))
    elif mode == "hopscan":
        # the decisive control: the SAME native ring, task moved to 2 hops (d = r+1 and 2r).
        # If the law collapses here too, the topology->random collapse needs no geometry.
        assert ph.topology == "ring"
        for dd in (ph.radius + 1, 2 * ph.radius):
            run("native@d%d" % dd, ph, dataclasses.replace(env, d=dd))
    else:
        raise SystemExit(mode)
    res["_compute"] = {"wall_s": round(time.time() - t0, 1), "cpu_s": round(time.process_time() - c0, 1)}
    (OUT / ("%s_%s.json" % (mode, cid))).write_text(json.dumps(res, indent=1))
    print(cid, "done", res["_compute"], flush=True)
