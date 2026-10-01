"""W2-7 static feasibility probes. No world, no evolution: single-genome P-11 / COMPETENT screens only.

    python -B probes.py controls | panel | random | minimal      -> PROBE_<section>.json

controls  hand-written positive / negative controls x every variant, 4 random paddings each (random padding, not
          zero padding: FOR Q3 showed zero padding certifies zero-painting); verdict + stage-2 rate + passing side.
panel     the 128 COMPETENT dense genomes of forensics/core_map.json (48 STATE_FREE) re-screened under each variant:
          paired survival of existing NPE solutions.
random    uniform random 64-byte genomes, the SAME genomes for every variant (common random numbers); competence
          rate vs the 2e-4 baseline. N per variant set by cost.
minimal   minimal copier: every 1- and 2-token program from a 44-token alphabet, and every 3-token program from a
          19-token micro-alphabet for variants with no <= 2-token copier, at offset 0; a program counts as a copier
          if COMPETENT on 3 of 3 random paddings (plant_rp's rule).
"""
from __future__ import annotations

import itertools
import json
import pathlib
import random
import sys
import time

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FOR = HERE.parents[1] / "inference_harvest_2026-09-30" / "forensics"

import alien_pair as AP  # noqa: E402
import variants as V  # noqa: E402

H = bytes.fromhex
CTRL = {
    "M_STOCK":   H("1e40e5"),                  # LD E,0x40 ; LDIR(alias)          stock minimal motif, side 0
    "M_SIDE1":   H("2e40e5"),                  # LD L,0x40 ; LDIR                 stock minimal motif, side 1
    "M_C0":      H("1ec0e5"),                  # LD E,0xC0 ; LDIR                 needs 7-bit aliasing (0xC0 = 64 mod 128)
    "LOOP":      H("1e407e12231318fa"),        # LD E,40; LD A,(HL); LD (DE),A; INC HL; INC DE; JR -6   bytewise
    "EXPL":      H("1e404be5"),                # LD E,40; LD C,E; LDIR            explicit count 64
    "SELFLOC":   H("ed327dc6405fe5"),          # SELF; LD A,L; ADD 0x40; LD E,A; LDIR   position-independent locator
    "STATEFREE": H("2100001140000140 00e5".replace(" ", "")),  # LD HL,0; LD DE,64; LD BC,64; LDIR
    "XJUMP":     H("1e403ee512c34000"),        # LD E,40; LD A,E5; LD (DE),A; JP 0x0040: writes the copy op into the
                                               # partner and executes it there (needs pc to cross into the partner)
    "EXPL_H":    H("1e404be576"),              # EXPL + HALT: stops post-copy wandering (the long count did this)
    "STATEFREE_H": H("210000114000014000e576"),  # STATEFREE + HALT
    "SELFLOC_H": H("ed327dc6405fe576"),        # SELFLOC + HALT
    "INCD":      H("14e5"),                    # INC D ; LDIR   DE = 256: = 0 mod 128 (self-copy), = 64 mod 192
    "SC1":       H("e5"),                      # one copy byte
    "NULL":      b"",                          # random padding only (E5/E7/ED-B0/B8-free, see pad())
}
PLAN = {   # variant: (positive, negative)
    "STOCK": ("M_STOCK", "NULL"), "STOCK_B1500": ("M_STOCK", "NULL"),
    "A_NOBLOCK": ("LOOP", "M_STOCK"), "A5_NOBLOCK_B1500": ("LOOP", "M_STOCK"),
    "B_EXPLEN": ("EXPL_H", "M_STOCK"), "C_NOWRAP": ("M_STOCK", "M_C0"),
    "C2_RING192": ("M_STOCK", "M_C0"), "C3_RING192_RGAP": ("M_STOCK", "M_C0"),
    "D_HARV_HALT": ("M_STOCK", "XJUMP"), "D2_HARV_WRAP": ("M_STOCK", "XJUMP"),
    "E_REGRAND": ("STATEFREE_H", "M_STOCK"), "F_ROTATE": ("SELFLOC_H", "M_STOCK"),
    "G_BLOCK_OWN": ("LOOP", "M_STOCK"), "H_RELADDR": ("M_STOCK", "M_SIDE1"),
    "I_SIDERAND": ("M_STOCK", None), "J_SELFCOPY": ("SC1", "NULL"),
}
COPYB = {0xE5, 0xE7, 0xED}


def pad(prog, rng):
    """Program at offset 0, then random padding free of copy encodings (E5, E7, ED) so a control tests ITS bytes."""
    out = bytearray(prog)
    while len(out) < 64:
        b = rng.randrange(256)
        if b not in COPYB:
            out.append(b)
    return bytes(out)


def dump(name, obj):
    (HERE / ("PROBE_%s.json" % name)).write_text(json.dumps(obj, indent=1))


def controls():
    rng = random.Random(2026093007)
    pads = {k: [pad(p, rng) for _ in range(4)] for k, p in CTRL.items()}
    out = {}
    for vname in V.VARIANTS:
        vm, lay, desc = V.get(vname)
        row = {"desc": desc, "plan": PLAN[vname]}
        for k, gs in pads.items():
            rs = [AP.competent(vm, g, lay, rate=True) for g in gs]
            row[k] = {"competent": sum(r[0] for r in rs), "of": len(rs),
                      "rate": [round(r[1], 2) for r in rs], "side_hits": [r[2] for r in rs]}
        out[vname] = row
        print(vname, {k: row[k]["competent"] for k in CTRL}, flush=True)
    return out


def panel():
    d = json.loads((FOR / "core_map.json").read_text())
    rows = [r for r in d["rows"] if r["vm"] == "DENSE" and str(r["competent"]) == "True"]
    out = {"n": len(rows), "n_state_free": sum(str(r["state_free"]) == "True" for r in rows)}
    for vname in V.VARIANTS:
        vm, lay, _ = V.get(vname)
        ok = [AP.competent(vm, bytes.fromhex(r["hex"]), lay) for r in rows]
        sf = [o for o, r in zip(ok, rows) if str(r["state_free"]) == "True"]
        nsf = [o for o, r in zip(ok, rows) if str(r["state_free"]) != "True"]
        out[vname] = {"survive": sum(ok), "survive_state_free": sum(sf), "survive_not_state_free": sum(nsf),
                      "survivors_idx": [i for i, o in enumerate(ok) if o]}
        print(vname, out[vname]["survive"], sum(sf), sum(nsf), flush=True)
    return out


NRAND = {"STOCK_B1500": 3000, "A5_NOBLOCK_B1500": 3000, "J_SELFCOPY": 3000}


def random_rate(n_default):
    rng = random.Random(20260930707)
    gs = [bytes(rng.randrange(256) for _ in range(64)) for _ in range(n_default)]
    out = {"n_default": n_default}
    for vname in V.VARIANTS:
        vm, lay, _ = V.get(vname)
        n = NRAND.get(vname, n_default)
        t = time.process_time()
        hits = [i for i, g in enumerate(gs[:n]) if AP.competent(vm, g, lay)]
        side = []
        for i in hits[:40]:
            side.append(AP.competent(vm, gs[i], lay, rate=True)[2])
        out[vname] = {"n": n, "hits": len(hits), "rate": len(hits) / n, "hit_idx": hits[:200],
                      "hit_hex": [gs[i].hex() for i in hits[:12]], "side_hits_first40": side,
                      "cpu_s": round(time.process_time() - t, 1)}
        print(vname, n, len(hits), out[vname]["cpu_s"], flush=True)
        dump("random", out)
    return out


def tokens():
    T = []
    for r in (0x06, 0x0E, 0x16, 0x1E, 0x26, 0x2E, 0x3E):          # LD r,n
        for n in (0x40, 0xC0, 0x00):
            T.append(bytes((r, n)))
    for op in (0x01, 0x11, 0x21):                                  # LD rr,nn
        for nn in (0x0040, 0x0000):
            T.append(bytes((op, nn & 0xFF, nn >> 8)))
    T += [bytes((x,)) for x in (0x14, 0x24, 0x15, 0x25, 0x1C, 0x2C,            # INC/DEC D,H ; INC E,L
                                0x4B, 0x43, 0x4D, 0x5D, 0x6B, 0x7D, 0x5F,       # LD C,E B,E C,L E,L L,E A,L E,A
                                0x7E, 0x12, 0x23, 0x13)]                         # bytewise pieces
    T += [H("c640"), H("ed32"), H("e5"), H("e7"), H("edb0"), H("edb8")]
    return T


MICRO = [H(x) for x in ("1e40", "1ec0", "2e40", "0e40", "4b", "4d", "43", "14", "24", "ed32", "114000",
                        "210000", "014000", "e5", "e7", "7d", "c640", "5f", "3e40")]


def minimal():
    rng = random.Random(20260930708)
    T = tokens()
    out = {"alphabet": [t.hex() for t in T], "micro": [t.hex() for t in MICRO]}
    for vname in V.VARIANTS:
        if vname in ("STOCK_B1500",):
            continue
        vm, lay, _ = V.get(vname)
        t0 = time.process_time()
        found = {}
        for L, alpha in ((1, T), (2, T), (3, MICRO)):
            if L == 3 and found:
                break
            if L == 3 and vname in ("A5_NOBLOCK_B1500",):
                break
            for seq in itertools.product(alpha, repeat=L):
                prog = b"".join(seq)
                pads = [pad(prog, random.Random(prog.hex() + "#%d" % j)) for j in range(3)]
                if not AP.competent(vm, pads[0], lay):
                    continue
                if all(AP.competent(vm, g, lay) for g in pads[1:]):
                    found.setdefault(L, []).append(prog.hex())
            if found:
                break
        best = min((len(bytes.fromhex(h)) for v in found.values() for h in v), default=None)
        out[vname] = {"min_tokens": min(found) if found else None, "min_bytes": best,
                      "copiers": {str(k): v[:30] for k, v in found.items()},
                      "n_copiers": {str(k): len(v) for k, v in found.items()},
                      "searched": "1-2 tokens x %d alphabet%s" % (len(T), "" if found and min(found) <= 2 else
                                                                   " + 3 tokens x %d micro" % len(MICRO)),
                      "cpu_s": round(time.process_time() - t0, 1)}
        print(vname, out[vname]["min_tokens"], best, out[vname]["n_copiers"], out[vname]["cpu_s"], flush=True)
        dump("minimal", out)
    return out


if __name__ == "__main__":
    sec = sys.argv[1]
    t = time.process_time()
    if sec == "controls":
        res = controls()
    elif sec == "panel":
        res = panel()
    elif sec == "random":
        res = random_rate(int(sys.argv[2]) if len(sys.argv) > 2 else 12000)
    elif sec == "minimal":
        res = minimal()
    res["cpu_total_s"] = round(time.process_time() - t, 1)
    dump(sec, res)
    print("cpu", res["cpu_total_s"])
