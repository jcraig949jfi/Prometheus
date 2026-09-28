"""L4 -- Archaeon ENVGATE-01 founder "copier" (frozen census ruler class EXACT_GATED / NEAR_COPIER / SPAN_COPIER; the
basis of "copier-founded" establishment in archaeon/envgate/ENVGATE01_REVIEW_2026-09-24.md s0, s5, s6). Label spec + runner.
Cold-start worker coldstart_A-001, 2026-09-28. Uses recert.py (unchanged copy) as the harness.

WHAT THE LABEL IS (provenance): archaeon/envgate/ruler.py runs the FROZEN copier-census ruler on each arriving tape ONCE:
empty (all-zero) neighbour, the 256 single input bytes, step_cap 256, copy primitive on. A tape is a "copier" if some input
gives a birth (>= 0.9 of the neighbour window written) that is an exact copy (EXACT_*), or has positional fidelity >= 0.75 or
a same-offset span >= 0.75 G (NEAR_COPIER), or span >= 0.5 G (SPAN_COPIER). The review reads this as "founders the frozen
ruler says can reproduce alone". In the world, however, the tape runs against a RANDOM ecology neighbour (occupied or
empty) and the child is whatever the window holds after the run (engine.py World.step).

CLAIMED PROPERTY: executed as the world executes it (vm.execute, step_cap 256, copy primitive on, one input byte), the tape
writes a copier-grade self-copy into the neighbour window (birth, and fidelity >= 0.75 or span >= 0.75 G -- the ruler's own
NEAR threshold) for at least one input byte -- not only with an empty neighbour but with the neighbours the ecology holds.
ENVIRONMENTS (13 neighbour contents, each swept over all 256 inputs with the census's exact input-skip):
    zero                the ruler's own context
    rand0..rand5        uniform random 32-byte tapes (the inflow distribution)
    eco0..eco5          ecology-realistic occupants: 2 takeover residents (dominant descendants, EXACT_UNGATED),
                        2 copier-founder tapes, 2 INERT-founder tapes (all from LINEAGES.json, fixed by rule; never self)
Behaviour per environment: pass iff some input gives a copier-grade birth. min_rate 0.5 (>= 7 of 13 environments).
EXPECTED MECHANISM: template-directed copying. Intervention: in the passing environment used (zero if it passes) at the
best input, do(tape[p] := b) for every p (2 random b != tape[p]); carried iff child[p - k] == b, k = the birth's best
same-offset shift (0 for a positional copy). T = carried share; ok iff T >= 0.5. bits_transmitted = 8 x positions carried
in both draws. A painter (writes a fixed pattern that happens to resemble the tape) predicts T ~ 0.
STRUCTURE: the tape contains a COPY-primitive byte (opcode 20 = byte & 31).
DESCRIPTORS (not verdict-bearing): heredity share = copier-grade births / all births over the 256 inputs with an empty
neighbour (what a U-arm founder's births look like), mean birth fidelity, gate width per environment, the frozen ruler's
class recomputed now (must equal the recorded class), exact-input set now vs then.

    python3 l4_envgate_copier.py [--limit N]        -> L4_rows.json   (serial: one process)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import time
from collections import Counter

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 5))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import recert as R  # noqa: E402
from archaeon.z80atlas import vm, engine as ZE  # noqa: E402
from archaeon.z80atlas.census import copier_census as C  # noqa: E402
from archaeon.envgate import ruler as RU  # noqa: E402
from archaeon.envgate.engine import STEP_CAP  # noqa: E402

G = 32
LINEAGES = os.path.join(REPO, "archaeon/envgate/LINEAGES.json")
HIT = set(C.HIT_CLASSES)
NEAR = 0.75
T_MIN = 0.5
COPY_OP = 20


def _seed(*parts) -> int:
    return int(hashlib.sha256(repr(parts).encode()).hexdigest()[:12], 16)


def _h(t: bytes) -> str:
    return hashlib.sha256(t).hexdigest()


# ---------------------------------------------------------------- neighbour set (fixed by rule, object-independent)
def _neighbour_pool():
    rnd = [bytes(random.Random(_seed("L4.nbr", i)).randrange(256) for _ in range(G)) for i in range(6)]
    lin = json.load(open(LINEAGES))["lineages"]
    res = Counter()
    for l in lin:
        for d in l.get("dominant_descendants") or []:
            res[d["tape"]] += d["count"]
    residents = [bytes.fromhex(t) for t, _ in sorted(res.items(), key=lambda kv: (-kv[1], kv[0]))]
    cop = sorted({l["founder_tape"] for l in lin if l["founder_class"] == "EXACT_GATED"}, key=lambda t: _h(bytes.fromhex(t)))
    ine = sorted({l["founder_tape"] for l in lin if l["founder_class"] == "INERT"}, key=lambda t: _h(bytes.fromhex(t)))
    return rnd, residents, [bytes.fromhex(t) for t in cop], [bytes.fromhex(t) for t in ine]


_POOL = None


def neighbours(tape: bytes):
    """[(name, bytes)] -- 13 neighbour contents; eco slots skip a candidate equal to the tape itself."""
    global _POOL
    if _POOL is None:
        _POOL = _neighbour_pool()
    rnd, residents, cop, ine = _POOL
    out = [("zero", bytes(G))] + [("rand%d" % i, t) for i, t in enumerate(rnd)]
    for base, cands in (("eco", residents), ("eco", cop), ("eco", ine)):
        picked = [c for c in cands if c != tape][:2]
        for c in picked:
            out.append(("eco%d" % (len(out) - 7), c))
    return out


# ---------------------------------------------------------------- one execution, the ruler's phenotype, in any neighbour
def phen(tape: bytes, nbr: bytes, x: int, r=None) -> dict:
    if r is None:
        r = vm.execute(tape, nbr, (x,), STEP_CAP, True, -1.0)
    win = r["nbr_window"]; mask = r["nbr_mask"]
    cov = sum(mask) / G; birth = cov >= C.COPY_MIN
    span, k = C.best_span(win, mask, tape) if r["writes_nbr"] else (0, 0)
    fid = ZE.fidelity(win, tape)
    return {"x": x, "birth": birth, "exact": birth and win == tape, "fid": fid, "span": span, "k": k,
            "copier_grade": birth and (fid >= NEAR or span >= NEAR * G), "in_read": r["inputs_read"] > 0, "win": win,
            "mask": mask, "exec_foreign": r["exec_foreign"]}


def sweep(tape: bytes, nbr: bytes):
    p0 = phen(tape, nbr, 0)
    if not p0["in_read"]:
        return [dict(p0, x=x) for x in range(256)]
    return [p0] + [phen(tape, nbr, x) for x in range(1, 256)]


class Obj:
    __slots__ = ("oid", "tape", "prov", "labelled")

    def __init__(self, oid, tape, prov, labelled=True):
        self.oid, self.tape, self.prov, self.labelled = oid, tape, prov, labelled


def environments(o):
    return [name for name, _ in neighbours(o.tape)]


def behavioural(o, env):
    nbr = dict(neighbours(o.tape))[env]
    ph = sweep(o.tape, nbr)
    births = [p for p in ph if p["birth"]]
    cg = [p for p in ph if p["copier_grade"]]
    best = max(cg, key=lambda p: (p["exact"], p["span"], p["fid"])) if cg else None
    return {"pass": bool(cg), "n_birth_inputs": len(births), "n_copier_inputs": len(cg),
            "n_exact_inputs": sum(p["exact"] for p in ph), "exact_inputs": [p["x"] for p in ph if p["exact"]][:16],
            "copier_inputs": [p["x"] for p in cg][:16],
            "mean_birth_fid": round(sum(p["fid"] for p in births) / len(births), 4) if births else None,
            "best_x": best["x"] if best else None, "best_k": best["k"] if best else None,
            "best_fid": round(best["fid"], 4) if best else None, "best_span": best["span"] if best else None,
            "foreign_exec_at_best": best["exec_foreign"] if best else None}


def structural(o):
    t = o.tape
    return {"ok": any((b & 31) == COPY_OP for b in t), "n_copy_bytes": sum(1 for b in t if (b & 31) == COPY_OP),
            "n_store_bytes": sum(1 for b in t if (b & 31) in (18, 19) and b >> 7),
            "dominant_byte_share": round(R.dominant_share(t), 4), "entropy_bits_per_byte": round(R.entropy_bits(t), 3),
            "ruler_class_now": RU.measure(t)["class"]}


def causal(o, beh):
    allr = beh["_all"]
    zero = dict(allr)["zero"]
    here = {"heredity_share_zero": round(zero["n_copier_inputs"] / zero["n_birth_inputs"], 4) if zero["n_birth_inputs"] else None,
            "n_birth_inputs_zero": zero["n_birth_inputs"], "n_copier_inputs_zero": zero["n_copier_inputs"],
            "n_exact_inputs_zero": zero["n_exact_inputs"], "exact_inputs_zero": zero["exact_inputs"],
            "mean_birth_fid_zero": zero["mean_birth_fid"],
            "gate_width_by_env": {e: r["n_copier_inputs"] for e, r in allr}}
    passing = [(e, r) for e, r in allr if r["pass"]]
    if not passing:
        return {"ok": None, "why": "no behaviour to intervene on", **here}
    env, r = next(((e, r) for e, r in passing if e == "zero"), passing[0])
    nbr = dict(neighbours(o.tape))[env]
    x, k = r["best_x"], r["best_k"]
    rng = random.Random(_seed("L4.T", o.oid))
    carried = [0] * G
    n = 0
    for p in range(G):
        for _ in range(2):
            b = rng.randrange(255)
            b = b if b < o.tape[p] else b + 1
            t = bytearray(o.tape); t[p] = b
            ph = phen(bytes(t), nbr, x)
            j = p - k
            carried[p] += (0 <= j < G and ph["mask"][j] and ph["win"][j] == b)
            n += 1
    T = sum(carried) / n
    return {"ok": T >= T_MIN, "intervention_env": env, "intervention_x": x, "offset_k": k, "transmission": round(T, 4),
            "bits_transmitted": 8 * sum(1 for c in carried if c == 2), **here}


LABEL = R.Label(
    name="ENVGATE-01 founder copier (census ruler class EXACT_GATED/NEAR_COPIER/SPAN_COPIER)",
    claimed_property="executed as the world executes it, the tape writes a copier-grade self-copy (birth; fid>=0.75 or "
                     "span>=0.75G) for some input byte, with the neighbour contents the ecology holds, not only an empty one",
    expected_mechanism="template-directed copying: do(tape[p]=b) -> child[p-k]=b for >= 50% of edits",
    provenance=lambda o: o.prov, structural=structural, environments=environments, behavioural=behavioural,
    causal=causal, obj_id=lambda o: o.oid, labelled=lambda o: o.labelled, min_rate=0.5,
    notes={"n_env": 13, "near": NEAR, "T_min": T_MIN, "step_cap": STEP_CAP, "copy_prim": True})


def load_founders(limit=None):
    lin = json.load(open(LINEAGES))["lineages"]
    groups = {}
    for l in lin:
        groups.setdefault(l["founder_tape"], []).append(l)
    objs = []
    for t, ls in groups.items():
        cls = sorted({l["founder_class"] for l in ls})
        assert len(cls) == 1, t
        births = sum(l["births"] for l in ls)
        prov = {"label_then": ("copier-founded (ruler class %s)" % cls[0]) if cls[0] in HIT else
                ("non-copier founder (ruler class %s; HOST/NOVEL_CANDIDATE)" % cls[0]),
                "founder_class": cls[0], "founder_exact_inputs": ls[0]["founder_exact_inputs"],
                "n_founder_birth_inputs": len(ls[0]["founder_birth_inputs"]), "n_lineages": len(ls),
                "lineages": [[l["block"], l["arm"], l["arrival"]] for l in ls][:8],
                "arms": sorted({l["arm"] for l in ls}), "blocks": sorted({l["block"] for l in ls}),
                "world_births": births, "world_exact_births": sum(l["exact_births"] for l in ls),
                "world_mean_fid_births_weighted": round(sum(l["mean_fid"] * l["births"] for l in ls) / births, 4) if births else None,
                "world_max_gen": max(l["max_gen"] for l in ls), "tape_sha": ls[0]["tape_sha"]}
        objs.append(Obj("E:" + ls[0]["tape_sha"], bytes.fromhex(t), prov, labelled=cls[0] in HIT))
    objs.sort(key=lambda o: (not o.labelled, o.oid))
    return objs[:limit] if limit else objs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", default=os.path.join(HERE, "L4_rows.json"))
    a = ap.parse_args()
    t0 = time.time()
    objs = load_founders(a.limit)
    print("L4: %d distinct founder tapes (%d labelled copier, %d unlabelled controls)"
          % (len(objs), sum(o.labelled for o in objs), sum(not o.labelled for o in objs)), flush=True)
    rows = []
    for i, o in enumerate(objs):
        rows.append(R.recertify_one(LABEL, o))
        if (i + 1) % 25 == 0:
            print("  %d/%d  %.0fs" % (i + 1, len(objs), time.time() - t0), flush=True)
    extra = {"summary_by_class": R.summarise(rows, lambda r: r["then"]["founder_class"]),
             "neighbour_names": [n for n, _ in neighbours(b"")], "wall_s": round(time.time() - t0, 1)}
    R.write(a.out, LABEL, rows, extra)
    print(json.dumps(extra, indent=1))


if __name__ == "__main__":
    main()
