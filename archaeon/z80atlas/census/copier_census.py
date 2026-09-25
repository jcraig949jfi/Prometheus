"""COPIER-CENSUS-01: random tape -> environment input -> reproductive phenotype (operator ruling 2, 2026-09-23).

Outside any ecology. Uniform random tapes are executed with the FROZEN campaign VM (archaeon.z80atlas.vm.execute, unmodified:
no reimplementation to drift from the substrate) against an empty neighbour window and every possible single input byte, and
each tape's reproductive phenotype is classified BEHAVIOURALLY. The census is blind: tapes are uniform draws from a recorded
SplitMix64 stream; nothing is searched, selected or evolved; the 84616cf8257b specimen and the hand-written replicator appear
ONLY as rulers (the classifier must place them correctly), never as a template or target.

Per (tape, input x in 0..255), frozen engine semantics (engine.run, layout shared, step_cap 256, non-metabolic):
    coverage = written neighbour bytes / G;  birth = coverage >= copy_min_frac (0.9)
    fidelity = frozen engine.fidelity(window, tape);  exact = birth and window == tape
    span     = longest run of WRITTEN window bytes equal to the tape under ONE offset k (window[j] == tape[j+k]), any k
Input skip: if the tape never executes IN on input 0, its execution is input-independent and one run stands for all 256
(exactness of this skip is tested against full sweeps).

Tape classes (first match wins):
    EXACT_UNGATED   exact birth for all 256 inputs
    EXACT_GATED     exact birth for 1..255 inputs            (input-gated access to exact self-copy)
    NEAR_COPIER     no exact; some birth with fidelity >= 0.75 or span >= 0.75 G
    SPAN_COPIER     no near; some birth with span >= 0.5 G   (a copied segment, shifted or partial)
    WRITER          births, span < 0.5 G                     (fills the window with non-self material)
    TOUCH           writes neighbour bytes, never a birth
    INERT           never writes the neighbour
Mechanism features recorded for every tape of class SPAN_COPIER or better (classification of architectures is done on
these features after the census, not by matching a known loop): executed-opcode histogram at a birth input, COPY vs STORE
primitive executed, backward relative jumps executed, absolute jumps executed, distinct executed addresses, steps, best
offset k, gating set size, whether IN was executed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from archaeon.z80atlas import vm, engine as E, tasks as T
from archaeon.z80atlas.grammar import FROZEN

HERE = Path(__file__).resolve().parent
STEP_CAP = FROZEN["budgets"]["late"]["step_cap"]
COPY_MIN = FROZEN["copy_min_frac"]
CLASSES = ["EXACT_UNGATED", "EXACT_GATED", "NEAR_COPIER", "SPAN_COPIER", "WRITER", "TOUCH", "INERT"]
HIT_CLASSES = CLASSES[:4]
SPECIMEN = "d521f9897030d42ef94aed67c4e2be714e8ed4791f14d54550d911698a00c826"


def best_span(window: bytes, mask: bytes, tape: bytes):
    G = len(tape); best = (0, 0)
    for k in range(-(G - 1), G):
        run = 0
        for j in range(G):
            t = j + k
            if 0 <= t < G and mask[j] and window[j] == tape[t]:
                run += 1
                if run > best[0]: best = (run, k)
            else:
                run = 0
    return best


def phenotype(tape: bytes, x: int, copy_prim: bool) -> dict:
    G = len(tape); r = vm.execute(tape, bytes(G), (x,), STEP_CAP, copy_prim)
    cov = sum(r["nbr_mask"]) / G; birth = cov >= COPY_MIN; win = r["nbr_window"]
    span, k = best_span(win, r["nbr_mask"], tape) if r["writes_nbr"] else (0, 0)
    return {"x": x, "writes": r["writes_nbr"], "cov": cov, "birth": birth, "fid": E.fidelity(win, tape), "exact": birth and win == tape,
            "span": span, "k": k, "steps": r["steps"], "halted": r["halted"], "in_read": r["inputs_read"] > 0, "hist": r["hist"],
            "exec_addrs": sum(r["executed"]), "window": win}


def sweep(tape: bytes, copy_prim: bool, force_full: bool = False) -> list:
    p0 = phenotype(tape, 0, copy_prim)
    if not p0["in_read"] and not force_full:
        return [dict(p0, x=x) for x in range(256)]
    return [p0] + [phenotype(tape, x, copy_prim) for x in range(1, 256)]


def classify(ph: list, G: int) -> str:
    ex = sum(p["exact"] for p in ph); births = [p for p in ph if p["birth"]]
    if ex == 256: return "EXACT_UNGATED"
    if ex >= 1: return "EXACT_GATED"
    if any(p["fid"] >= 0.75 or p["span"] >= 0.75 * G for p in births): return "NEAR_COPIER"
    if any(p["span"] >= 0.5 * G for p in births): return "SPAN_COPIER"
    if births: return "WRITER"
    if any(p["writes"] for p in ph): return "TOUCH"
    return "INERT"


def features(tape: bytes, ph: list, cls: str) -> dict:
    G = len(tape); births = [p for p in ph if p["birth"]]
    rep = max(births, key=lambda p: (p["exact"], p["span"], p["fid"]))
    h = rep["hist"]
    return {"tape": tape.hex(), "class": cls, "n_birth_inputs": len(births), "n_exact_inputs": sum(p["exact"] for p in ph),
            "exact_inputs": [p["x"] for p in ph if p["exact"]][:256], "max_fid": round(max(p["fid"] for p in births), 4), "max_span": max(p["span"] for p in births),
            "best_offset_k": rep["k"], "rep_input": rep["x"], "in_read": ph[0]["in_read"], "steps": rep["steps"], "halted": rep["halted"], "exec_addrs": rep["exec_addrs"],
            "op_copy": h[20], "op_store": h[18] + h[19], "op_in": h[21], "op_rel_jump": h[14] + h[15] + h[16] + h[17] + h[27], "op_abs_jump": h[13] + h[26],
            "hist": h, "child_hex": rep["window"].hex()}


def stream_tapes(stratum: str, chunk: int, n: int, G: int):
    r = SplitMix64(seed_from("archaeon.copier_census.v1", stratum, chunk))
    for _ in range(n):
        yield bytes(r.randbelow(256) for _ in range(G))


def run_chunk(stratum: str, substrate: str, G: int, chunk: int, n: int) -> dict:
    cp = substrate == "vmcopy"; counts = Counter(); in_read = 0; hits = []; t0 = time.time()
    for tape in stream_tapes(stratum, chunk, n, G):
        ph = sweep(tape, cp); cls = classify(ph, G); counts[cls] += 1; in_read += ph[0]["in_read"]
        if cls in HIT_CLASSES:
            hits.append(features(tape, ph, cls))
    return {"stratum": stratum, "chunk": chunk, "n": n, "counts": dict(counts), "in_read": in_read, "hits": hits, "wall_s": round(time.time() - t0, 1)}


def rulers() -> dict:
    """Positive/negative controls for the classifier (rulers, not targets)."""
    out = {}
    for name, tape, cp, want in [("handwritten_replicator_vmcopy", T.pad(T.replicator(True), 32), True, "EXACT_UNGATED"),
                                 ("handwritten_replicator_z80", T.pad(T.replicator(False), 32), False, "EXACT_UNGATED"),
                                 ("specimen_84616cf8257b_founder", bytes.fromhex(SPECIMEN), True, "EXACT_GATED"),
                                 ("all_nop", bytes(32), True, "INERT")]:
        got = classify(sweep(tape, cp), 32); out[name] = {"want": want, "got": got, "PASS": got == want}
    return out


# ---------------------------------------------------------------------------------------------------------------- stage 2 (per hit)
TIER = {c: i for i, c in enumerate(CLASSES)}                                # lower = more copier-like


def characterize(hit: dict, substrate: str) -> dict:
    """Heritability of the offspring, a fixed 256-mutant damage map (32 positions x 8 substitutions), occupied-neighbour robustness."""
    cp = substrate == "vmcopy"; tape = bytes.fromhex(hit["tape"]); G = len(tape); cls = hit["class"]
    child = bytes.fromhex(hit["child_hex"]); child_cls = cls if child == tape else classify(sweep(child, cp), G)
    r = SplitMix64(seed_from("archaeon.copier_census.v1.damage", hit["tape"]))
    keep_tier = keep_exact = keep_birth = 0; essential = []
    for pos in range(G):
        pos_exact = 0
        for _ in range(8):
            v = r.randbelow(255); v = v if v < tape[pos] else v + 1         # a different byte
            m = bytearray(tape); m[pos] = v; ph = sweep(bytes(m), cp); c = classify(ph, G)
            keep_tier += TIER[c] <= TIER[cls]; ex = any(p["exact"] for p in ph); keep_exact += ex; pos_exact += ex; keep_birth += any(p["birth"] for p in ph)
        if cls.startswith("EXACT") and pos_exact == 0: essential.append(pos)
    nbr = bytes(SplitMix64(seed_from("archaeon.copier_census.v1.nbr", hit["tape"])).randbelow(256) for _ in range(G))
    occ = [vm.execute(tape, nbr, (x,), STEP_CAP, cp) for x in (hit["exact_inputs"] or [hit["rep_input"]])[:16]]
    occ_birth = sum(sum(o["nbr_mask"]) / G >= COPY_MIN for o in occ); occ_exact = sum(o["nbr_window"] == tape and sum(o["nbr_mask"]) / G >= COPY_MIN for o in occ)
    return {"child_class": child_cls, "offspring_heritable": TIER[child_cls] <= TIER["SPAN_COPIER"],
            "mutants": 8 * G, "frac_keep_class_tier": round(keep_tier / (8 * G), 4), "frac_keep_any_exact": round(keep_exact / (8 * G), 4),
            "frac_keep_any_birth": round(keep_birth / (8 * G), 4), "essential_positions": essential,
            "occupied_nbr_inputs_tested": len(occ), "occupied_nbr_births": occ_birth, "occupied_nbr_exact": occ_exact}


def architecture(h: dict) -> str:
    prim = "COPY" if h["op_copy"] and not h["op_store"] else ("STORE" if h["op_store"] and not h["op_copy"] else ("MIXED" if h["op_copy"] else "NONE"))
    n = h["n_exact_inputs"]; gate = "ungated" if n == 256 else ("gated1" if n == 1 else ("gated" if n else "no_exact"))
    ctl = "reljump" if h["op_rel_jump"] else ("absjump" if h["op_abs_jump"] else "straight")
    return "%s|%s|%s|%s|%s" % (prim, gate, ctl, "k0" if h["best_offset_k"] == 0 else "shift", "reads_input" if h["in_read"] else "input_blind")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rulers", action="store_true"); ap.add_argument("--pilot", type=int, default=0, help="engineering pilot on the PILOT stream (excluded from estimates)")
    ap.add_argument("--stratum"); ap.add_argument("--substrate"); ap.add_argument("--G", type=int, default=32); ap.add_argument("--chunks", type=int, default=0)
    ap.add_argument("--chunk-size", type=int, default=20000); ap.add_argument("--first-chunk", type=int, default=0); ap.add_argument("--workers", type=int, default=22)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    if a.rulers:
        r = rulers(); print(json.dumps(r, indent=1)); return 0 if all(v["PASS"] for v in r.values()) else 4
    if a.pilot:
        res = run_chunk("PILOT-" + a.substrate + str(a.G), a.substrate, a.G, 0, a.pilot)
        print(json.dumps({"n": res["n"], "counts": res["counts"], "in_read": res["in_read"], "wall_s": res["wall_s"], "per_tape_ms": round(1000 * res["wall_s"] / res["n"], 2)})); return 0
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(a.workers) as ex:
        futs = [ex.submit(run_chunk, a.stratum, a.substrate, a.G, c, a.chunk_size) for c in range(a.first_chunk, a.first_chunk + a.chunks)]
        for fu in as_completed(futs):
            res = fu.result(); p = out / ("chunk_%06d.json" % res["chunk"])
            p.write_text(json.dumps(res) + "\n", encoding="utf-8", newline="\n")
            print(json.dumps({"chunk": res["chunk"], "counts": res["counts"], "hits": len(res["hits"]), "wall_s": res["wall_s"]}), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
