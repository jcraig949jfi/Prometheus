"""W2-4: counterfactual knockout logic -> five-class maps (transmitted / conversion-necessary / establishment-only /
environment-supplied / physics), applied statically to a stratified panel.

    python -B w4_run.py [--only ID[,ID..]] [--limit N]   -> w4_results.json (one record per genome, checkpointed)

Single-interaction calls of the world's own _pair_interact only (w4_common). No world / evolution run.
"""
from __future__ import annotations

import json
import random
import sys
import time

import w4_common as W

M = W.M
import core_map as CM  # noqa: E402  (FOR harness: ivm trace of the main copy)
import z8 as Z8PLAIN  # noqa: E402  (stock VM, physics test)

OUT = W.HERE / "w4_results.json"
SEED = 20260930
NZ, NKID, NI, NCAR = 60, 5, 8, 60           # per-position assay sizes
WZ, WKID, WNI, WCAR = 200, 10, 15, 200      # wild-type reference (run twice, tags WT1 / WT2)
NENV = 60
NNULL = 12
REGN = ("B", "C", "D", "E", "H", "L", "HLslot", "A")
t0 = time.process_time()


# ---------------------------------------------------------------- panel
def panel():
    d = json.load(open(W.FOR / "core_map.json"))
    rows = [r for r in d["rows"] if r.get("competent") and r["vm"] == "DENSE"]
    rng = random.Random(SEED)
    out = []
    for sf in (True, False):
        for cell, k in (("7ae3", 8), ("ffa6", 7)):
            pool = [r for r in rows if r["src"] == "corpus" and r["cell"] == cell and r["state_free"] == sf]
            for r in rng.sample(pool, k):
                out.append({"id": "%s_%s_%s" % ("SF" if sf else "SD", cell, r["hex"][:8]), "grp": "SF" if sf else "SD",
                            "hex": r["hex"], "cell": "C7" if cell == "7ae3" else "CF", "origin": r["origin_run"],
                            "for_collapse": r.get("collapse"), "for_necessary": r.get("necessary"),
                            "for_base_rate": r.get("base_rate"), "state_free": sf})
    for r in rows:
        if r["src"] == "16000006_e700":
            out.append({"id": "E700_%s" % r.get("vid", r["hex"][:8]), "grp": "E700", "hex": r["hex"], "cell": "C7",
                        "origin": r["origin_run"], "for_collapse": r.get("collapse"),
                        "for_necessary": r.get("necessary"), "for_base_rate": r.get("base_rate"), "state_free": True})
    man = json.load(open(M.CAMP / "z80atlas-verify-2026-09-22" / "MANIFEST_FROZEN.json"))
    seen = set()
    for b in man["bundles"]:
        sp = b.get("specimen", "")
        if b.get("hypothesis_id") == "H2" and sp[:4] in ("7ae3", "cb7f", "c2a8") and sp not in seen:
            seen.add(sp)
            arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
            out.append({"id": "SPEC_" + sp[:4], "grp": "SPEC", "hex": arm["kwargs"]["implant_hex"], "cell": "C7",
                        "origin": sp, "state_free": None})
    prng = random.Random(SEED + 1)
    for motif, nm in (("1E40E5", "MIN3"), ("2E001E40E5", "MIN5")):
        for k in range(3):
            mb = bytes.fromhex(motif)
            g = mb + bytes(prng.randrange(256) for _ in range(64 - len(mb)))
            out.append({"id": "%s_pad%d" % (nm, k), "grp": nm, "hex": g.hex(), "cell": "CF", "origin": "constructed",
                        "motif_len": len(mb), "state_free": None})
    return out


# ---------------------------------------------------------------- classification logic
TH = {"Z_abolish": 0.25, "Z_intact": 0.6, "C_min": 0.10, "C_kill": 0.25, "K_min": 0.10, "K_kill": 0.25,
      "R_drop": 0.25, "P2_min": 0.20, "P2_kill": 0.5}


def classify(ko, wt):
    """Counterfactual class of one knockout given the wild-type reference. Returns (cls, killed_readouts, gains)."""
    zr = ko["Z"] / wt["Z"] if wt["Z"] > 0 else None
    killed = []
    if wt["C"] >= TH["C_min"] and ko["C"] <= TH["C_kill"] * wt["C"]:
        killed.append("C")
    if ko["K"] is not None and wt["K"] is not None and wt["K"] >= TH["K_min"] and ko["K"] <= TH["K_kill"] * wt["K"]:
        killed.append("K")
    if (1 - ko["R"]) >= (1 - wt["R"]) + TH["R_drop"]:
        killed.append("R")
    if wt["P2"] >= TH["P2_min"] and ko["P2"] <= TH["P2_kill"] * wt["P2"]:
        killed.append("P2")
    gains = []
    if ko["C"] >= wt["C"] + 0.2:
        gains.append("C")
    if zr is not None and ko["Z"] >= 1.5 * wt["Z"] + 0.1:
        gains.append("Z")
    if zr is None:
        cls = "NA"
    elif zr <= TH["Z_abolish"]:
        cls = "CONV_NEC"
    elif zr < TH["Z_intact"]:
        cls = "CONV_PARTIAL"
    elif killed:
        cls = "EST_ONLY"
    else:
        cls = "NEUTRAL"
    return cls, killed, gains


def slim(r):
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()
            if k in ("Z", "R", "K", "C", "Ckept", "P2", "nkids", "Kn", "nconv", "side_conv")}


def avg_wt(a, b):
    out = {}
    for k in ("Z", "R", "C", "Ckept", "P2"):
        out[k] = (a[k] + b[k]) / 2
    ks = [x for x in (a["K"], b["K"]) if x is not None]
    out["K"] = sum(ks) / len(ks) if ks else None
    return out


# ---------------------------------------------------------------- genome-level environment / physics tests
def env_tests(g, cell, side, regs_c):
    res = {}

    def rz(**kw):
        return round(W.assay_zero(g, cell, NENV, kw.pop("tag"), nc=0, **kw)["conv"], 4)

    res["zero"] = rz(tag="ENV0")
    for ri, nm in enumerate(REGN):
        if nm == "HLslot":
            continue

        def st(rng, ri=ri):
            r = [0] * 8
            r[ri] = rng.randrange(1, 256)
            return (r, 0, 0)
        res["reg_" + nm] = rz(tag="ENVR" + nm, d_st=st)
    res["flags_set"] = rz(tag="ENVF", d_st=([0] * 8, 1, 1))
    res["donor_random"] = rz(tag="ENVDR", d_st=lambda rng: ([rng.randrange(256) for _ in range(8)],
                                                            rng.randrange(2), rng.randrange(2)))
    res["partner_random"] = rz(tag="ENVPR", p_st=lambda rng: ([rng.randrange(256) for _ in range(8)],
                                                              rng.randrange(2), rng.randrange(2)))
    res["side0_only"] = rz(tag="ENVS0", sides=(0,))
    res["side1_only"] = rz(tag="ENVS1", sides=(1,))
    # write-back: BASE runner (both halves written back)
    b = W.assay_zero(g, cell, NENV, "ENVBASE", nc=0, base=True)
    res["base_conv"], res["base_intact"] = round(b["conv"], 4), round(b["kept"], 4)
    # physics
    h = W.harness(cell)
    old = h.r.t["slice"]
    for s in (150, 600, 1200):
        h.r.t["slice"] = s
        try:
            res["slice_%d" % s] = rz(tag="ENVSL%d" % s)
        finally:
            h.r.t["slice"] = old
    op2 = M.world._pow2
    M.world._pow2 = lambda x: 256
    try:
        res["tape256"] = rz(tag="ENVT256")
    finally:
        M.world._pow2 = op2
    W.VM_OVERRIDE[0] = Z8PLAIN
    try:
        res["stock_vm"] = rz(tag="ENVSTOCK")
    finally:
        W.VM_OVERRIDE[0] = None
    if regs_c is not None:
        ent = (list(regs_c[:6]) + [0, 0], 0, 0)
        res["operand_entry_side"] = round(W.assay_zero(g, cell, NENV, "ENVOP", nc=0, d_st=ent, sides=(side,))["conv"], 4)
        res["zero_side"] = round(W.assay_zero(g, cell, NENV, "ENVZS", nc=0, sides=(side,))["conv"], 4)
    return res


def trace_info(g, side):
    t = CM.analyse_trace(g, True, side)
    W.harness  # (CM sets world.z8 via fsetup; w4_common.harness() resets it on every assay)
    if not t["main_copy"]:
        return None
    ci, pc_c, op_c, regs_c, moved = t["main_copy"]
    base = t["base"]
    pos = pc_c - base if base <= pc_c < base + 64 else None
    setters = {}
    for rg, v in t["setters"].items():
        p = v[1] - base
        if 0 <= p < 64:
            setters["BCDEHL"[rg]] = p
    execd = sorted(t["execd"].keys())
    tape = t["tape"]
    instr = {}
    for i, (pc, op, _r) in enumerate(t["trace"][:ci + 1]):
        if base <= pc < base + 64:
            instr[pc - base] = min(CM.ivm.ilen(tape, pc, True), base + 64 - pc)
    return {"instr_before_copy": sorted(instr.items()),"copy_pc": pc_c, "copy_pos": pos, "copy_op": "%02X" % op_c, "regs_c": list(regs_c[:8]),
            "HL": (regs_c[4] << 8) | regs_c[5], "DE": (regs_c[2] << 8) | regs_c[3], "BC": (regs_c[0] << 8) | regs_c[1],
            "moved": moved, "setter_pos": setters, "executed_pos": execd, "n_copies": t.get("n_copies")}


# ---------------------------------------------------------------- per genome
def run_genome(rec):
    g = bytes.fromhex(rec["hex"])
    cell = rec["cell"]
    t1 = time.process_time()
    wt1 = W.full(g, cell, "WT1", WZ, WKID, WNI, WCAR)
    wt2 = W.full(g, cell, "WT2", WZ, WKID, WNI, WCAR)
    wt = avg_wt(wt1, wt2)
    out = dict(rec)
    out["wt1"], out["wt2"], out["wt"] = slim(wt1), slim(wt2), {k: (None if v is None else round(v, 4)) for k, v in wt.items()}
    nconv = wt1["nconv"] + wt2["nconv"]
    deliv = [a + b for a, b in zip(wt1["deliv"], wt2["deliv"])]
    out["transmitted"] = [j for j in range(64) if nconv and deliv[j] >= 0.5 * nconv]
    out["deliv_share"] = [round(d / nconv, 3) if nconv else None for d in deliv]
    sc = {s: (wt1["side_conv"][s] or 0) + (wt2["side_conv"][s] or 0) for s in (0, 1)}
    side = 0 if sc[0] >= sc[1] else 1
    out["pass_side"] = side
    if wt["Z"] <= 0.02:
        out["status"] = "NO_ZERO_CONVERSION"
        out["env"] = env_tests(g, cell, side, None)
        out["cpu"] = round(time.process_time() - t1, 1)
        return out
    out["status"] = "OK"
    ti = trace_info(g, side)
    out["trace"] = ti
    out["env"] = env_tests(g, cell, side, ti["regs_c"] if ti else None)
    # per-position knockouts
    pos = []
    for p in range(64):
        m = W.knock(g, p, 0)
        r = W.full(m, cell, ("P", p, 0), NZ, NKID, NI, NCAR)
        cls, killed, gains = classify(r, wt)
        pos.append({"p": p, "v": m[p], "ko": slim(r), "cls": cls, "killed": killed, "gains": gains})
    # null: wild type assayed at the per-position N with fresh tags, classified by the same rule
    null = []
    for i in range(NNULL):
        r = W.full(g, cell, ("NULL", i), NZ, NKID, NI, NCAR)
        cls, killed, gains = classify(r, wt)
        null.append({"i": i, "ko": slim(r), "cls": cls, "killed": killed})
    # re-assay: EST_ONLY and CONV_PARTIAL positions (and null EST_ONLY hits): (a) same value, fresh tag, 2x N;
    # (b) second knockout value, fresh tag, 1x N
    for x in pos:
        if x["cls"] in ("EST_ONLY", "CONV_PARTIAL"):
            m = W.knock(g, x["p"], 0)
            ra = W.full(m, cell, ("RA", x["p"]), 2 * NZ, NKID, NI, 2 * NCAR)
            x["re_same"] = dict(zip(("cls", "killed", "gains"), classify(ra, wt)), ko=slim(ra))
            mb = W.knock(g, x["p"], 1)
            rb = W.full(mb, cell, ("RB", x["p"]), NZ, NKID, NI, NCAR)
            x["re_val2"] = dict(zip(("cls", "killed", "gains"), classify(rb, wt)), ko=slim(rb), v=mb[x["p"]])
    for x in null:
        if x["cls"] == "EST_ONLY":
            ra = W.full(g, cell, ("NRA", x["i"]), 2 * NZ, NKID, NI, 2 * NCAR)
            x["re_same"] = dict(zip(("cls", "killed", "gains"), classify(ra, wt)), ko=slim(ra))
    # operand-supply rescue (class 4 test) for conversion-necessary positions
    if ti is not None:
        ent = (list(ti["regs_c"][:6]) + [0, 0], 0, 0)
        for x in pos:
            if x["cls"] == "CONV_NEC":
                m = W.knock(g, x["p"], 0)
                r = W.assay_zero(m, cell, 40, ("RES", x["p"]), nc=0, d_st=ent, sides=(side,))
                x["rescue_operand"] = round(r["conv"], 4)
    # instruction-level DELETION knockouts (every byte of an executed pre-copy instruction -> 00 = NOP):
    # removal, not corruption, so the environment's default value of what the instruction set reaches the copy
    dele = []
    if ti is not None:
        for p0, ln in ti["instr_before_copy"]:
            m = bytearray(g)
            m[p0:p0 + ln] = bytes(ln)
            if bytes(m) == g:
                continue
            r = W.full(bytes(m), cell, ("DEL", p0), NZ, NKID, NI, NCAR)
            cls, killed, gains = classify(r, wt)
            dele.append({"p": p0, "len": ln, "bytes": g[p0:p0 + ln].hex(), "ko": slim(r), "cls": cls,
                         "killed": killed, "gains": gains})
    out["deletion"] = dele
    out["pos"] = pos
    out["null"] = null
    out["cpu"] = round(time.process_time() - t1, 1)
    return out


def main():
    args = sys.argv[1:]
    P = panel()
    if "--only" in args:
        ids = set(args[args.index("--only") + 1].split(","))
        P = [r for r in P if r["id"] in ids]
    if "--limit" in args:
        P = P[:int(args[args.index("--limit") + 1])]
    done = {}
    if OUT.exists() and "--fresh" not in args:
        done = {r["id"]: r for r in json.loads(OUT.read_text())["genomes"]}
    res = []
    for rec in P:
        if rec["id"] in done:
            res.append(done[rec["id"]])
            continue
        r = run_genome(rec)
        res.append(r)
        cc = {}
        for x in r.get("pos", []):
            cc[x["cls"]] = cc.get(x["cls"], 0) + 1
        print(r["id"], r["status"], "wt", r["wt"], cc, "T", len(r["transmitted"]), "cpu", r["cpu"],
              "tot", round(time.process_time() - t0, 1), flush=True)
        allres = list(done.values())
        ids = {x["id"] for x in res}
        merged = [x for x in allres if x["id"] not in ids] + res
        OUT.write_text(json.dumps({"meta": {"NZ": NZ, "NKID": NKID, "NI": NI, "NCAR": NCAR, "WZ": WZ, "WKID": WKID,
                                            "WNI": WNI, "WCAR": WCAR, "NENV": NENV, "NNULL": NNULL, "TH": TH},
                                   "genomes": merged}, indent=0))
    print("cpu total", round(time.process_time() - t0, 1))


if __name__ == "__main__":
    main()
