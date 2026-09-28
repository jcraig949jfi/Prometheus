"""S8 stack-route spike on BEE's VM (EXPLORATORY). Implements PREREG.md in this directory.

    python3 s8.py OUT.json

Single process, stdlib only, deterministic seeds. F detector, CVT-2, estimator and CI helpers are copied from
../pilot.py unchanged except that run() calls vm_stack.execute with the arm's settings.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import random
import subprocess
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 5))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from prometheus.z80atlas import vm  # noqa: E402
import vm_stack  # noqa: E402
import vmx  # noqa: E402  (pilot's variant, for the E0 L3 equivalence check)

L = 64
INP = 42
T0 = time.time()
WALL_CAP = 33 * 60
LDI_OFF = frozenset({vm.LDI})

ARMS = {
    "L0": dict(ldir="on", disabled=frozenset(), stack="none", budget=256),
    "L2": dict(ldir="off", disabled=frozenset(), stack="none", budget=256),
    "L3": dict(ldir="off", disabled=LDI_OFF, stack="none", budget=256),
    "L3s": dict(ldir="off", disabled=LDI_OFF, stack="sp_up", budget=256),
    "L3t": dict(ldir="off", disabled=LDI_OFF, stack="t_up", budget=256),
    "L3z": dict(ldir="off", disabled=LDI_OFF, stack="sp_dn", budget=256),
    "L3z512": dict(ldir="off", disabled=LDI_OFF, stack="sp_dn", budget=512),
}


def log(msg):
    print("[%6.0fs] %s" % (time.time() - T0, msg), flush=True)


def rbytes(rng, n):
    return bytes(rng.randrange(256) for _ in range(n))


def run(tape, arm, window):
    a = ARMS[arm]
    mem = bytearray(256)
    mem[:L] = tape
    mem[L:2 * L] = window
    mem[vm.IN_BASE] = INP
    tr = vm_stack.execute(mem, L, 0, a["budget"], [INP], allow_copyall=False, ldir=a["ldir"], undefined="NOP",
                          disabled=a["disabled"], stack=a["stack"])
    return bytes(mem[L:2 * L]), tr


def fid(child, tape):
    return sum(1 for x, y in zip(child, tape) if x == y) / L


def detect_f(tape, arm, rng):
    fids = []
    for w in range(3):
        child, tr = run(tape, arm, rbytes(rng, L))
        f = fid(child, tape)
        fids.append(round(f, 4))
        if f < 0.9:
            return False, fids
    return True, fids


# ---------------- CVT-2 (copied from pilot.py) ----------------
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


def cvt2(tape, arm, sid):
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


# ---------------- CI helpers (copied from pilot.py) ----------------
def _wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def _pois_cdf(k, mu):
    return sum(math.exp(-mu + i * math.log(mu) - math.lgamma(i + 1)) for i in range(k + 1)) if mu > 0 else 1.0


def cp_upper(k, n, conf=0.95):
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


# ---------------- E0 ----------------
def e0(n=1000):
    out = {}
    for i, ldir in enumerate(["on", "off", "cost4"]):
        rng = random.Random(7000 + i)
        bad = 0
        for _ in range(n):
            m1 = bytearray(256)
            m1[:2 * L] = rbytes(rng, 2 * L)
            m1[vm.IN_BASE] = INP
            m2 = bytearray(m1)
            t1 = vm.execute(m1, L, 0, 256, [INP], ldir=ldir)
            t2 = vm_stack.execute(m2, L, 0, 256, [INP], ldir=ldir)
            if m1 != m2 or t1.steps != t2.steps or t1.win_prov != t2.win_prov or t1.writes != t2.writes \
                    or t1.opcodes != t2.opcodes or t1.halted != t2.halted:
                bad += 1
        out["vm_ldir_" + ldir] = {"n": n, "mismatches": bad}
    rng = random.Random(7100)
    bad = 0
    for _ in range(n):
        m1 = bytearray(256)
        m1[:2 * L] = rbytes(rng, 2 * L)
        m1[vm.IN_BASE] = INP
        m2 = bytearray(m1)
        t1 = vmx.execute(m1, L, 0, 256, [INP], ldir="off", disabled=LDI_OFF)
        t2 = vm_stack.execute(m2, L, 0, 256, [INP], ldir="off", disabled=LDI_OFF)
        if m1 != m2 or t1.steps != t2.steps or t1.win_prov != t2.win_prov or t1.writes != t2.writes \
                or t1.opcodes != t2.opcodes or t1.halted != t2.halted:
            bad += 1
    out["vmx_L3"] = {"n": n, "mismatches": bad}
    return out


# ---------------- controls ----------------
PC = {
    "PC_LDIR3": bytes.fromhex("084015"),
    "PC_LDI5": bytes.fromhex("08401433fd"),
    "PC_MOV8": bytes.fromhex("0840101124253 3fa".replace(" ", "")),
    "PC_PUT5": bytes.fromhex("10241733fb"),
    "PC_TPUT7": bytes.fromhex("0840102417 33fb".replace(" ", "")),
    "PC_ZPUSH9": bytes.fromhex("0740492347101733f9"),
}
PAINTERS = {
    "PAINTER": bytes.fromhex("0140084011253 3fc".replace(" ", "")) + bytes([0x40]) * (L - 8),
    "PPAINT": bytes.fromhex("01401733fd") + bytes([0x40]) * (L - 5),
    "TPAINT": bytes.fromhex("084001401733fd") + bytes([0x40]) * (L - 7),
}
CONTROL_PLAN = [
    ("L0", "PC_LDIR3"), ("L3s", "PC_LDIR3"),
    ("L2", "PC_LDI5"), ("L3", "PC_LDI5"),
    ("L3", "PC_MOV8"), ("L3s", "PC_MOV8"),
    ("L3s", "PC_PUT5"), ("L3", "PC_PUT5"), ("L3t", "PC_PUT5"), ("L3z", "PC_PUT5"),
    ("L3t", "PC_TPUT7"),
    ("L3z", "PC_ZPUSH9"), ("L3z512", "PC_ZPUSH9"),
    ("L3", "PAINTER"), ("L3s", "PAINTER"), ("L3t", "PAINTER"), ("L3z", "PAINTER"),
    ("L3s", "PPAINT"), ("L3z", "PPAINT"),
    ("L3t", "TPAINT"),
]


def control(arm, name, seed, n=100):
    rng = random.Random(seed)
    passes, first = 0, None
    for _ in range(n):
        if name in PAINTERS:
            tape = PAINTERS[name]
        else:
            code = PC[name]
            tape = code + rbytes(rng, L - len(code))
        ok, fids = detect_f(tape, arm, rng)
        passes += ok
        if ok and first is None:
            first = tape
    return {"arm": arm, "control": name, "n": n, "F_pass": passes, "first_pass_tape": first.hex() if first else None}


# ---------------- estimator ----------------
R_, W_, IS, IT, PU = 0x10, 0x11, 0x24, 0x25, 0x17
R_T = 0x12


def _jumps(j, target):
    """back-jump at j (operand at j+1) to target: JR, DJNZ, JP."""
    return [(0x33, (target - (j + 2)) & 0xFF), (0x34, (target - (j + 2)) & 0xFF), (0x30, target)]


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
    elif route == "R_PUT":
        for q in range(0, L - 4):
            for rd, inc in ((R_, IS), (R_T, IT)):
                for body in ((rd, inc, PU), (rd, PU, inc)):
                    for kind, opnd in _jumps(q + 3, q):
                        c = {q + k: b for k, b in enumerate(body)}
                        c[q + 3] = kind
                        c[q + 4] = opnd
                        C.append(c)
    elif route == "R_TPUT":
        for p in range(0, L - 2):
            for q in range(p + 2, L - 4):
                for body in ((R_, IS, PU), (R_, PU, IS)):
                    for kind, opnd in _jumps(q + 3, q):
                        c = {p: 0x08, p + 1: 0x40}
                        for k, b in enumerate(body):
                            c[q + k] = b
                        c[q + 3] = kind
                        c[q + 4] = opnd
                        C.append(c)
    return C


KBYTES = {"R_LDIR": 3, "R_LDI": 5, "R_PUT": 5, "R_TPUT": 7}


def importance(arm, route, seed, n):
    C = configs(route)
    rng = random.Random(seed)
    passes, ex = 0, []
    for _ in range(n):
        c = C[rng.randrange(len(C))]
        t = bytearray(rbytes(rng, L))
        for pos, b in c.items():
            t[pos] = b
        ok, fids = detect_f(bytes(t), arm, rng)
        if ok:
            passes += 1
            if len(ex) < 20:
                ex.append(bytes(t).hex())
    return {"arm": arm, "route": route, "n": n, "passes": passes, "nC": len(C), "examples": ex}


# ---------------- sampling / walks ----------------
def sample(arm, seed, n):
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
        ok = True
        for _w in range(2):
            c2, _ = run(tape, arm, rbytes(rng, L))
            if fid(c2, tape) < 0.9:
                ok = False
                break
        if ok:
            hits.append(tape.hex())
    return {"arm": arm, "n": n, "screen": screen, "hits": hits, "any_window_write": any_write}


def walk(arm, seed, steps):
    rng = random.Random(seed)
    tape = bytearray(rbytes(rng, L))
    for s in range(1, steps + 1):
        tape[rng.randrange(L)] = rng.randrange(256)
        t = bytes(tape)
        child, tr = run(t, arm, rbytes(rng, L))
        if fid(child, t) >= 0.9:
            ok, fids = detect_f(t, arm, rng)
            if ok:
                return {"arm": arm, "seed": seed, "steps": s, "hit": True, "tape": t.hex()}
    return {"arm": arm, "seed": seed, "steps": steps, "hit": False}


def over():
    return time.time() - T0 > WALL_CAP


def main():
    out_path = sys.argv[1]
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731
    res = {"label": "EXPLORATORY", "commit": commit, "prereg": "PREREG.md", "prereg_sha256": sha(os.path.join(HERE, "PREREG.md")),
           "vm_sha256": sha(os.path.join(REPO, "prometheus/z80atlas/vm.py")),
           "vm_stack_sha256": sha(os.path.join(HERE, "vm_stack.py")),
           "arms": {k: {kk: (sorted(vv) if isinstance(vv, frozenset) else vv) for kk, vv in v.items()} for k, v in ARMS.items()},
           "truncated": []}

    def save():
        res["wall_s"] = round(time.time() - T0, 1)
        with open(out_path, "w") as f:
            json.dump(res, f, indent=1)

    # E0
    res["E0"] = e0()
    res["E0_pass"] = all(v["mismatches"] == 0 for v in res["E0"].values())
    log("E0 %s" % res["E0"])
    save()
    if not res["E0_pass"]:
        log("E0 FAILED; stopping")
        return

    # P0
    res["P0_controls"] = [control(arm, nm, 100 + 17 * i) for i, (arm, nm) in enumerate(CONTROL_PLAN)]
    for c in res["P0_controls"]:
        log("P0 %-6s %-10s F %d/%d" % (c["arm"], c["control"], c["F_pass"], c["n"]))
    save()
    res["P0_cvt2"] = []
    for c in res["P0_controls"]:
        if c["first_pass_tape"]:
            r = cvt2(bytes.fromhex(c["first_pass_tape"]), c["arm"], "%s_%s" % (c["control"], c["arm"]))
            r["control"] = c["control"]
            res["P0_cvt2"].append(r)
            log("CVT2 %-6s %-10s TB2 %.2f h2 %.3f" % (c["arm"], c["control"], r["TB2"], r["h2"]))
            save()

    # P2
    plan = [("L0", "R_LDIR", 1000), ("L2", "R_LDI", 1500), ("L3s", "R_PUT", 3000), ("L3t", "R_TPUT", 3000)]
    p2 = {}
    for i, (arm, route, n) in enumerate(plan):
        per = 250
        d = None
        for c in range(n // per):
            if over():
                res["truncated"].append("P2 %s after %d plants" % (arm, c * per))
                break
            x = importance(arm, route, 90000 + 1000 * i + c, per)
            if d is None:
                d = {"arm": arm, "route": route, "n": 0, "passes": 0, "nC": x["nC"], "k_bytes": KBYTES[route], "examples": []}
            d["n"] += x["n"]
            d["passes"] += x["passes"]
            d["examples"] = (d["examples"] + x["examples"])[:20]
        base = d["nC"] * 256.0 ** (-d["k_bytes"])
        rr = d["passes"] / d["n"]
        d["r"] = round(rr, 5)
        d["r_ci95"] = [cp_lower(d["passes"], d["n"]), cp_upper(d["passes"], d["n"])]
        d["density_raw"] = base * rr
        d["density_raw_ci95"] = [base * d["r_ci95"][0], base * d["r_ci95"][1]]
        p2[arm] = d
        log("P2 %s %s %d/%d nC %d density %.3g" % (arm, route, d["passes"], d["n"], d["nC"], d["density_raw"]))
        save()
    res["P2_importance"] = p2
    # P2 CVT-2 on up to 20 passes per arm
    for arm, d in p2.items():
        rows = []
        for j, h in enumerate(d["examples"][:20]):
            if over():
                res["truncated"].append("P2-CVT %s after %d" % (arm, j))
                break
            rows.append(cvt2(bytes.fromhex(h), arm, "EST_%s_%d" % (arm, j)))
        d["cvt2"] = [{k: r[k] for k in ("tape", "TB2", "h2", "dominant_share")} for r in rows]
        ns = len(rows)
        nself = sum(1 for r in rows if r["TB2"] >= 5)
        d["self_share"] = (nself / ns) if ns else None
        sh = d["self_share"] if ns else 1.0
        d["density"] = d["density_raw"] * sh
        d["density_ci95"] = [d["density_raw_ci95"][0] * sh, d["density_raw_ci95"][1] * sh]
        d["log10_density"] = round(math.log10(d["density"]), 3) if d["density"] > 0 else None
        d["log10_ci95"] = [round(math.log10(x), 3) if x > 0 else None for x in d["density_ci95"]]
        log("P2-CVT %s %d/%d self; TB2 range %s" % (arm, nself, ns,
            (min(r["TB2"] for r in rows), max(r["TB2"] for r in rows)) if rows else None))
        save()

    # P3
    plan = [("L3s", 150000), ("L3t", 40000), ("L3z", 30000), ("L3", 20000)]
    p3 = {}
    for i, (arm, n) in enumerate(plan):
        d = p3.setdefault(arm, {"n": 0, "screen": 0, "hits": [], "any_window_write": 0})
        per = 5000
        for c in range(n // per):
            if over():
                res["truncated"].append("P3 %s after %d tapes" % (arm, d["n"]))
                break
            x = sample(arm, 500000 + 1000 * i + c, per)
            d["n"] += x["n"]
            d["screen"] += x["screen"]
            d["hits"] += x["hits"]
            d["any_window_write"] += x["any_window_write"]
        k = len(d["hits"])
        d["k"] = k
        d["density"] = k / d["n"] if d["n"] else None
        d["ci95"] = [cp_lower(k, d["n"]), cp_upper(k, d["n"])] if d["n"] else None
        log("P3 %s %d/%d screen %d" % (arm, k, d["n"], d["screen"]))
        res["P3_sampling"] = p3
        save()
    res["P3_cvt2"] = []
    for arm, d in p3.items():
        for j, h in enumerate(d["hits"][:6]):
            if not over():
                res["P3_cvt2"].append(cvt2(bytes.fromhex(h), arm, "S_%s_%d" % (arm, j)))
    save()

    # P4
    walks = []
    for j in range(10):
        if over():
            res["truncated"].append("P4 after %d walks" % j)
            break
        walks.append(walk("L3s", 800000 + j, 2000))
    tot = sum(w["steps"] for w in walks)
    hits = sum(w["hit"] for w in walks)
    res["P4_walks"] = {"arm": "L3s", "walks": len(walks), "hits": hits, "total_steps": tot,
                       "hazard_ci95": [cp_lower(hits, tot), cp_upper(hits, tot)] if tot else None,
                       "hit_tapes": [w["tape"] for w in walks if w["hit"]]}
    log("P4 %d walks %d hits %d steps" % (len(walks), hits, tot))
    save()
    log("done")


if __name__ == "__main__":
    main()
