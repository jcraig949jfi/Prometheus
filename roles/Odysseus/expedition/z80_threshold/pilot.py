"""Z80 affordance-threshold pilot on BEE's VM (EXPLORATORY). Implements PREREG.md in this directory.

    python3 pilot.py OUT.json [--workers 4]

Parts: E0 VM-equivalence gate, P0 controls, P1 BASIN specimens, P2 route-conditional importance estimator,
P3 uniform sampling, P4 mutation random walks. Stdlib only. Deterministic given seeds.
"""
from __future__ import annotations

import hashlib
import json
import math
import multiprocessing as mp
import os
import random
import subprocess
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 4))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)
from prometheus.z80atlas import vm  # noqa: E402
import vmx  # noqa: E402

L = 64
INP = 42
T0 = time.time()
WALL_CAP = 35 * 60

ARMS = {
    "A0": dict(ldir="on", disabled=frozenset(), budget=256),
    "A1": dict(ldir="cost4", disabled=frozenset(), budget=256),
    "A2": dict(ldir="off", disabled=frozenset(), budget=256),
    "A3": dict(ldir="off", disabled=frozenset({vm.LDI}), budget=256),
    "A3b": dict(ldir="off", disabled=frozenset({vm.LDI}), budget=512),
    "A4": dict(ldir="off", disabled=frozenset({vm.LDI, vm.LD_pT_A, vm.LD_pS_A}), budget=256),
}


def rbytes(rng, n):
    return bytes(rng.randrange(256) for _ in range(n))


def run(tape, arm, window):
    a = ARMS[arm]
    mem = bytearray(256)
    mem[:L] = tape
    mem[L:2 * L] = window
    mem[vm.IN_BASE] = INP
    tr = vmx.execute(mem, L, 0, a["budget"], [INP], allow_copyall=False, ldir=a["ldir"], undefined="NOP",
                     disabled=a["disabled"])
    return bytes(mem[L:2 * L]), tr


def fid(child, tape):
    return sum(1 for x, y in zip(child, tape) if x == y) / L


def rule_o(tape, tr, child):
    prov = tr.win_prov
    own = [(off, pc) for off, (src, pc, op) in prov.items() if op in vm.COPY_OPS and src is not None and src < L]
    own_code = sum(1 for _, pc in own if pc < L)
    return len(own) >= 0.9 * L and own_code >= 0.9 * max(1, len(own)) and fid(child, tape) >= 0.9


def detect_f(tape, arm, rng):
    """F: fid >= 0.9 in 3 independent random windows. Returns (pass, fids, rule_o on window 1)."""
    fids = []
    o = None
    for w in range(3):
        child, tr = run(tape, arm, rbytes(rng, L))
        f = fid(child, tape)
        fids.append(round(f, 4))
        if w == 0:
            o = rule_o(tape, tr, child)
        if f < 0.9:
            return False, fids, o
    return True, fids, o


# ---------------- CVT-2 (Artemis certs.py semantics, re-implemented for BEE) ----------------
DRAWS, GENS = 3, 2


def _win(sid, g, k):
    return rbytes(random.Random("W|%s|%d|%d" % (sid, g, k)), L)


def _lineage(G, arm, sid, k, cache):
    out = []
    for g in range(1, GENS + 1):
        key = (G, g, k)
        if key not in cache:
            cache[key] = run(G, arm, _win(sid, g, k))[0]
        G = cache[key]
        out.append(G)
    return out


def _delta(a, b):
    return tuple((i, a[i]) for i in range(len(a)) if a[i] != b[i])


def _defined(sigs):
    c = Counter(s for s in sigs if s)
    if not c:
        return None
    s, m = c.most_common(1)[0]
    return s if m >= 2 else None


def cvt2(args):
    tape, arm, sid = args
    cache = {}
    base = [_lineage(tape, arm, sid, k, cache) for k in range(DRAWS)]
    acc, classes, nv = 0, set(), 0
    for i in range(L):
        x = tape[i]
        a, b = x ^ 0x01, x ^ 0x80
        rr = random.Random("V|%s|%d" % (sid, i))
        r = rr.randrange(256)
        while r in (x, a, b):
            r = rr.randrange(256)
        for v in (a, b, r):
            nv += 1
            Gv = tape[:i] + bytes([v]) + tape[i + 1:]
            lin = [_lineage(Gv, arm, sid, k, cache) for k in range(DRAWS)]
            d = [_defined([_delta(lin[k][g], base[k][g]) for k in range(DRAWS)]) for g in range(GENS)]
            if d[0] and d[1]:
                acc += 1
                classes.add(d[1])
    dom_b, dom_c = Counter(tape).most_common(1)[0]
    return {"sid": sid, "arm": arm, "tape": tape.hex(), "n_variants": nv, "accepted": acc,
            "h2": round(acc / nv, 4), "classes": len(classes), "TB2": round(math.log2(1 + len(classes)), 4),
            "dominant_share": round(dom_c / L, 4), "dominant_byte": "%02x" % dom_b}


# ---------------- E0 gate ----------------
def e0(args):
    ldir, seed, n = args
    rng = random.Random(seed)
    bad = 0
    for _ in range(n):
        m1 = bytearray(256)
        m1[:2 * L] = rbytes(rng, 2 * L)
        m1[vm.IN_BASE] = INP
        m2 = bytearray(m1)
        t1 = vm.execute(m1, L, 0, 256, [INP], ldir=ldir)
        t2 = vmx.execute(m2, L, 0, 256, [INP], ldir=ldir)
        if m1 != m2 or t1.steps != t2.steps or t1.win_prov != t2.win_prov or t1.writes != t2.writes \
                or t1.opcodes != t2.opcodes or t1.halted != t2.halted:
            bad += 1
    return {"ldir": ldir, "n": n, "mismatches": bad}


# ---------------- controls ----------------
PC = {
    "PC_REP8": vm.replicator(L),
    "PC_LDIR3": bytes([0x08, 0x40, 0x15]),
    "PC_LDI5": bytes([0x08, 0x40, 0x14, 0x33, 0xFD]),
    "PC_MOV8": bytes([0x08, 0x40, 0x10, 0x11, 0x24, 0x25, 0x33, 0xFA]),
}
PAINTER = bytes([0x01, 0x40, 0x08, 0x40, 0x11, 0x25, 0x33, 0xFC]) + bytes([0x40]) * (L - 8)


def control(args):
    arm, name, seed, n = args
    rng = random.Random(seed)
    passes, o_pass, first = 0, 0, None
    for _ in range(n):
        if name == "PAINTER":
            tape = PAINTER
        else:
            code = PC[name]
            tape = code + rbytes(rng, L - len(code))
        ok, fids, o = detect_f(tape, arm, rng)
        passes += ok
        o_pass += bool(ok and o)
        if ok and first is None:
            first = tape
    return {"arm": arm, "control": name, "n": n, "F_pass": passes, "O_pass_among_F": o_pass,
            "first_pass_tape": first.hex() if first else None}


# ---------------- importance estimator ----------------
def configs(route):
    C = []
    if route == "R_LDIR":
        for p in range(0, L - 2):
            for q in range(p + 2, L):
                C.append({p: 0x08, p + 1: 0x40, q: 0x15})
    elif route == "R_LDI":
        for p in range(0, L - 2):
            for q in range(p + 2, L):
                for j in (q + 1, q + 2):
                    if j + 1 > L - 1:
                        continue
                    for t in range(max(p + 2, q - 2), q + 1):
                        for kind in (0x33, 0x34, 0x30):
                            opnd = t if kind == 0x30 else (t - (j + 2)) & 0xFF
                            C.append({p: 0x08, p + 1: 0x40, q: 0x14, j: kind, j + 1: opnd})
    elif route == "R_MOV":
        R, W, IS, IT = 0x10, 0x11, 0x24, 0x25
        orders = [(R, W, IS, IT), (R, W, IT, IS), (R, IS, W, IT)]
        for p in range(0, L - 2):
            for q in range(p + 2, L - 5):
                for od in orders:
                    c = {p: 0x08, p + 1: 0x40, q + 4: 0x33, q + 5: 0xFA}
                    for k, b in enumerate(od):
                        c[q + k] = b
                    C.append(c)
    return C


KBYTES = {"R_LDIR": 3, "R_LDI": 5, "R_MOV": 8}


def importance(args):
    arm, route, seed, n = args
    C = configs(route)
    rng = random.Random(seed)
    passes, ex = 0, []
    for _ in range(n):
        c = C[rng.randrange(len(C))]
        t = bytearray(rbytes(rng, L))
        for pos, b in c.items():
            t[pos] = b
        ok, fids, o = detect_f(bytes(t), arm, rng)
        if ok:
            passes += 1
            if len(ex) < 3:
                ex.append(bytes(t).hex())
    return {"arm": arm, "route": route, "n": n, "passes": passes, "nC": len(C), "examples": ex}


# ---------------- sampling ----------------
def sample(args):
    arm, seed, n = args
    rng = random.Random(seed)
    screen, hits, any_write = 0, [], 0
    for _ in range(n):
        tape = rbytes(rng, L)
        child, tr = run(tape, arm, rbytes(rng, L))
        if tr.neighbour_writes:
            any_write += 1
        if fid(child, tape) < 0.9:
            continue
        screen += 1
        o = rule_o(tape, tr, child)
        ok = True
        for _w in range(2):
            c2, _ = run(tape, arm, rbytes(rng, L))
            if fid(c2, tape) < 0.9:
                ok = False
                break
        if ok:
            hits.append({"tape": tape.hex(), "rule_O": o})
    return {"arm": arm, "n": n, "screen": screen, "hits": hits, "any_window_write": any_write}


# ---------------- walks ----------------
def walk(args):
    arm, seed, steps = args
    rng = random.Random(seed)
    tape = bytearray(rbytes(rng, L))
    for s in range(1, steps + 1):
        tape[rng.randrange(L)] = rng.randrange(256)
        t = bytes(tape)
        child, tr = run(t, arm, rbytes(rng, L))
        if fid(child, t) >= 0.9:
            ok, fids, o = detect_f(t, arm, rng)
            if ok:
                return {"arm": arm, "seed": seed, "steps": s, "hit": True, "tape": t.hex(), "rule_O": o}
    return {"arm": arm, "seed": seed, "steps": steps, "hit": False}


def _wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def _pois_cdf(k, mu):
    # log-space Poisson CDF P(X <= k)
    return sum(math.exp(-mu + i * math.log(mu) - math.lgamma(i + 1)) for i in range(k + 1)) if mu > 0 else 1.0


def cp_upper(k, n, conf=0.95):
    """95% upper bound: exact Poisson (bisection, log-space) for k <= 30, Wilson otherwise.
    (Patched after the first launch crashed with float overflow at k ~ 2000; no result had been read.)"""
    if k > 30:
        return _wilson(k, n)[1]
    a = (1 - conf) / 2
    lo, hi = 0.0, 60.0 + 3 * k
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _pois_cdf(k, mid) > a else (lo, mid)
    return min(1.0, hi / n)


def cp_lower(k, n, conf=0.95):
    if k == 0:
        return 0.0
    if k > 30:
        return _wilson(k, n)[0]
    a = (1 - conf) / 2
    lo, hi = 0.0, 60.0 + 3 * k
    for _ in range(100):
        mid = (lo + hi) / 2
        sf = 1 - _pois_cdf(k - 1, mid)
        lo, hi = (lo, mid) if sf > a else (mid, hi)
    return lo / n


def pmap(pool, fn, jobs, label):
    t = time.time()
    out = pool.map(fn, jobs, chunksize=1)
    print("[%6.0fs] %s: %d jobs in %.0fs" % (time.time() - T0, label, len(jobs), time.time() - t), flush=True)
    return out


def main():
    out_path = sys.argv[1]
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 4
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    res = {"label": "EXPLORATORY", "commit": commit, "prereg": "PREREG.md",
           "vm_sha256": hashlib.sha256(open(os.path.join(REPO, "prometheus/z80atlas/vm.py"), "rb").read()).hexdigest(),
           "vmx_sha256": hashlib.sha256(open(os.path.join(HERE, "vmx.py"), "rb").read()).hexdigest(),
           "arms": {k: {"ldir": v["ldir"], "disabled": sorted(v["disabled"]), "budget": v["budget"]} for k, v in ARMS.items()},
           "truncated": []}

    def save():
        res["wall_s"] = round(time.time() - T0, 1)
        json.dump(res, open(out_path, "w"), indent=1)

    with mp.Pool(workers) as pool:
        # E0
        r = pmap(pool, e0, [(ld, 7000 + i, 500) for i, ld in enumerate(["on", "off", "cost4"] * 3)], "E0")
        agg = {}
        for x in r:
            agg.setdefault(x["ldir"], [0, 0])
            agg[x["ldir"]][0] += x["n"]
            agg[x["ldir"]][1] += x["mismatches"]
        res["E0"] = {k: {"n": v[0], "mismatches": v[1]} for k, v in agg.items()}
        res["E0_pass"] = all(v[1] == 0 for v in agg.values())
        save()
        if not res["E0_pass"]:
            print("E0 FAILED; stopping")
            return

        # P0 controls
        jobs = [(arm, nm, 100 + 17 * i, 200) for i, (arm, nm) in enumerate(
            [(a, n) for a in ("A0", "A1", "A2", "A3", "A3b", "A4") for n in list(PC) + ["PAINTER"]])]
        res["P0_controls"] = pmap(pool, control, jobs, "P0 controls")
        save()
        cj = [(bytes.fromhex(c["first_pass_tape"]), c["arm"], "%s_%s" % (c["control"], c["arm"]))
              for c in res["P0_controls"] if c["first_pass_tape"]]
        res["P0_cvt2"] = pmap(pool, cvt2, cj, "P0 CVT-2")
        save()

        # P1 BASIN specimens
        basin = json.load(open(os.path.join(REPO, "roles/Bellerophon/forensics_2026-09-23/receipts/BASIN.json")))
        btapes = [bytes.fromhex(e["tape"]) for e in basin["by_rep"]["Z80_64"]["examples"]]
        rng = random.Random(4242)
        p1 = []
        for i, t in enumerate(btapes):
            row = {"i": i, "tape": t.hex()}
            for arm in ("A0", "A1", "A2"):
                ok, fids, o = detect_f(t, arm, rng)
                row[arm] = {"F": ok, "fids": fids, "rule_O_w1": o}
            p1.append(row)
        res["P1_basin"] = p1
        res["P1_cvt2"] = pmap(pool, cvt2, [(t, "A0", "BASIN%d_A0" % i) for i, t in enumerate(btapes)], "P1 CVT-2")
        save()

        # P2 importance
        plan = [("A0", "R_LDIR", 2000), ("A1", "R_LDIR", 2000), ("A2", "R_LDI", 3000),
                ("A3", "R_MOV", 2000), ("A3b", "R_MOV", 2000), ("A1", "R_LDI", 1000), ("A0", "R_LDI", 1000)]
        jobs = []
        for arm, route, n in plan:
            per = 250
            for c in range(n // per):
                jobs.append((arm, route, 90000 + len(jobs), per))
        r = pmap(pool, importance, jobs, "P2 importance")
        p2 = {}
        for x in r:
            k = "%s|%s" % (x["arm"], x["route"])
            d = p2.setdefault(k, {"arm": x["arm"], "route": x["route"], "n": 0, "passes": 0, "nC": x["nC"],
                                  "k_bytes": KBYTES[x["route"]], "examples": []})
            d["n"] += x["n"]
            d["passes"] += x["passes"]
            d["examples"] = (d["examples"] + x["examples"])[:3]
        for d in p2.values():
            base = d["nC"] * 256.0 ** (-d["k_bytes"])
            rr = d["passes"] / d["n"]
            d["r"] = round(rr, 5)
            d["density_est"] = base * rr
            d["density_ci95"] = [base * cp_lower(d["passes"], d["n"]), base * cp_upper(d["passes"], d["n"])]
            d["log10_density_est"] = round(math.log10(base * rr), 3) if rr > 0 else None
        res["P2_importance"] = p2
        save()

        # P3 sampling
        plan = [("A0", 30000), ("A1", 50000), ("A2", 50000), ("A3", 10000), ("A4", 3000)]
        jobs = []
        for arm, n in plan:
            per = 1000 if arm == "A4" else 2500
            for c in range(n // per):
                jobs.append((arm, 500000 + len(jobs), per))
        p3 = {}
        done = []
        chunk = 8
        for s in range(0, len(jobs), chunk):
            if time.time() - T0 > WALL_CAP:
                res["truncated"].append("P3 after %d of %d chunks" % (len(done), len(jobs)))
                break
            done += pool.map(sample, jobs[s:s + chunk], chunksize=1)
        print("[%6.0fs] P3 sampling done (%d chunks)" % (time.time() - T0, len(done)), flush=True)
        for x in done:
            d = p3.setdefault(x["arm"], {"n": 0, "screen": 0, "hits": [], "any_window_write": 0})
            d["n"] += x["n"]
            d["screen"] += x["screen"]
            d["hits"] += x["hits"]
            d["any_window_write"] += x["any_window_write"]
        for arm, d in p3.items():
            k = len(d["hits"])
            d["k"] = k
            d["density"] = k / d["n"]
            d["ci95"] = [cp_lower(k, d["n"]), cp_upper(k, d["n"])]
        res["P3_sampling"] = p3
        save()
        hj = [(bytes.fromhex(h["tape"]), arm, "S%s_%d" % (arm, i)) for arm, d in p3.items() for i, h in enumerate(d["hits"][:6])]
        res["P3_cvt2"] = pmap(pool, cvt2, hj, "P3 CVT-2") if hj else []
        save()

        # P4 walks
        if time.time() - T0 < WALL_CAP:
            jobs = [(arm, 800000 + 31 * i + j, 3000) for i, arm in enumerate(("A0", "A1", "A2")) for j in range(10)]
            r = pmap(pool, walk, jobs, "P4 walks")
            p4 = {}
            for x in r:
                d = p4.setdefault(x["arm"], {"walks": 0, "hits": 0, "total_steps": 0, "hit_steps": [], "hit_tapes": []})
                d["walks"] += 1
                d["total_steps"] += x["steps"]
                if x["hit"]:
                    d["hits"] += 1
                    d["hit_steps"].append(x["steps"])
                    d["hit_tapes"].append(x["tape"])
            for d in p4.values():
                d["hazard_per_step"] = d["hits"] / d["total_steps"]
                d["hazard_ci95"] = [cp_lower(d["hits"], d["total_steps"]), cp_upper(d["hits"], d["total_steps"])]
            res["P4_walks"] = p4
            wj = [(bytes.fromhex(t), arm, "W%s_%d" % (arm, i)) for arm, d in p4.items() for i, t in enumerate(d["hit_tapes"][:4])]
            if wj and time.time() - T0 < WALL_CAP + 180:
                res["P4_cvt2"] = pmap(pool, cvt2, wj, "P4 CVT-2")
        else:
            res["truncated"].append("P4 not run (wall cap)")
        save()
    print("done wall %.0fs" % (time.time() - T0))


if __name__ == "__main__":
    main()
