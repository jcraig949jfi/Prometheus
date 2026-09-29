"""Constructed panel: gates E0-E2 and G, P-11 original, FERT, CVT-1/2/R, LOCAL, SHUF/DOM diagnostics.

    python3 -B run_panel.py pilot   -> timing pilot on Z1 (E2)
    python3 -B run_panel.py         -> results/PANEL.jsonl, results/CONFUSION.json, results/GATES_PANEL.json
"""
from __future__ import annotations

import dataclasses
import json
import multiprocessing as mp
import random
import sys
import time

from common import OUT, Z8SUB, Z8VER, Z8ORIG, FRESH, shabytes, fid, file_hashes
import specimens as S
import harness as Hn
import certs as CE
import tv as TV

CMR_P11 = 0.002
K = 20


def sterile(sp, vm, child):
    """AMENDMENT b A1: child as donor authors <= 0.10 n victim cells and rebuilds < 0.90, in each of 3 draws."""
    n = sp.n
    ok = True
    for k in range(3):
        vb = shabytes("VICTIM", sp.id, 2, k, n=n)
        tape, prov, _ = Hn.pair_run(vm, n, sp.tape_len, sp.budget, sp.mask, child, sp.side, vb)
        v0, did = (n, 1) if sp.side == 0 else (0, 2)
        auth = sum(1 for i in range(v0, v0 + n) if prov[i] == did)
        ok = ok and auth <= 0.10 * n and fid(child, bytes(tape[v0:v0 + n])) < 0.90
    return ok


def gates(sp, vm):
    st = lambda G, g, k: Hn.step(vm, sp, G, g, k)
    G = sp.genome
    c1 = st(G, 1, 0)
    c2 = st(c1, 2, 0)
    g = {}
    vic = lambda gg, kk: shabytes("VICTIM", sp.id, gg, kk, n=sp.n)
    if sp.id == "Z1":
        g["dominant_90_of_96"] = CE.dom_share(G)[0] == 90 / 96
        g["child_is_36x96"] = c1 == bytes([0x36]) * 96
        g["fid_0.9375"] = abs(fid(G, c1) - 0.9375) < 1e-9
        g["child_sterile"] = sterile(sp, vm, c1)
    elif sp.id == "Z2":
        g["child_is_(36 23)x48"] = c1 == bytes([0x36, 0x23]) * 48
        g["fid_89_of_96"] = abs(fid(G, c1) - 89 / 96) < 1e-9
        g["dominant_below_0.5"] = CE.dom_share(G)[0] < 0.5
        g["child_sterile"] = sterile(sp, vm, c1)
    elif sp.id in ("TV-1", "TV-2"):
        g["closed"] = c1 == G
        same = True
        for i in range(sp.sites):
            for x in CE.variant_values(G, i, True, sp.id):     # AMENDMENT b A2: exhaustive
                if st(G[:i] + bytes([x]) + G[i + 1:], 1, 0) != c1:
                    same = False
        g["all_single_site_variants_same_child"] = same
    elif sp.id in ("Z3", "Z3b", "TV-3", "Z5a", "TV-5b"):
        g["child_equals_parent"] = c1 == G
        g["grandchild_equals_parent"] = c2 == G
        if sp.id == "Z5a":
            host = S.Z5A_HOST + shabytes("HOSTCARGO", sp.id, 1, 0, n=22)
            _, _, wo = Hn.pair_run(vm, 32, 64, sp.budget, sp.mask, host, 0, G)
            g["guest_writes_nothing"] = wo[1] == 0
        if sp.id == "TV-5b":
            vb = shabytes("LONE", n=32)
            tape, _, _ = Hn.pair_run(vm, 32, 64, sp.budget, 0, S.TV5_A0, 0, vb)
            g["lone_member_does_not_copy_itself"] = bytes(tape[32:64]) == vb
    elif sp.id == "Z3u96":
        k = 0
        while k < 96 and c1[k] == G[k]:
            k += 1
        k2 = 0
        while k2 < 96 and c2[k2] == c1[k2]:
            k2 += 1
        g["copied_prefix_65_to_75"] = 65 <= k <= 75
        g["fid_below_0.9"] = fid(G, c1) < 0.9
        g["child_copies_again_prefix_ge_65"] = k2 >= 65
        g["_copied_prefix"] = k
    elif sp.id == "Z3n":
        code, _ = Z8SUB.asm(S.Z3N_SRC)
        g["asm_equals_hex"] = code == S.Z3N_EXPECT
        ch, meta = Hn.host_run(vm, sp, G, shabytes("SLOT", sp.id, 1, 0, n=128))
        g["birth_within_10_slices"] = meta["births"] >= 1
        g["child_equals_parent"] = ch == G
        g["repl_rule_passes"] = meta["repl"]
        g["_writes_blocked"] = meta["writes_blocked"]
        g["_slices"] = meta["slices"]
    elif sp.id == "TV-4":
        g["child_is_complement"] = c1 == bytes(b ^ 0xFF for b in G)
        g["grandchild_is_parent"] = c2 == G
    elif sp.id == "TV-6":
        g["A_to_A"] = c1 == G
        g["B_to_B"] = st(S.TV6_B, 1, 0) == S.TV6_B
        ch = {x: st(bytes([x]) + G[1:], 1, 0) for x in range(256) if x != G[0]}
        chg = {x for x, c in ch.items() if c != c1}
        g["site0_changers_exactly_11_EE"] = chg == {0x11, 0xEE} and all(ch[x] == S.TV6_B for x in chg)
    elif sp.id == "TV-6k":
        g["child_equals_parent"] = c1 == G
        ch = {x: st(bytes([x]) + G[1:], 1, 0) for x in range(256) if x != G[0]}
        chg = {x for x, c in ch.items() if c != c1}
        g["site0_changers_exactly_30"] = chg == set(range(0x11, 0x20)) | set(range(0xE0, 0xEF))
        g["fifteen_distinct_painter_children"] = len({ch[x] for x in chg}) == 15
    elif sp.id == "Z6h":
        g["child_equals_parent"] = c1 == G
        g["dominant_88_of_96"] = CE.dom_share(G)[0] == 88 / 96
        g["B_to_B"] = st(S.Z6H_B, 1, 0) == S.Z6H_B
    elif sp.id == "TV-7":
        g["child_is_hash"] = c1 == bytes([0x40]) + TV._stream(G, 31)
        g["form_changes"] = c2 != c1
    elif sp.id == "TV-8":
        exp = bytearray(G)
        exp[5] = (exp[5] + 1) & 0xFF
        g["child_is_parent_plus_counter"] = c1 == bytes(exp)
    ok = all(v for k, v in g.items() if not k.startswith("_"))
    return {"pass": ok, "checks": g}


def p11_block(sp, vm, side=None):
    side = sp.side if side is None else side
    n, TL = sp.n, sp.tape_len
    common = dict(sid=sp.id, n=n, budget=sp.budget, mask=sp.mask, cmr=CMR_P11)
    if sp.kind == "host":
        c1, m1 = Hn.host_run(vm, sp, sp.genome, shabytes("SLOT", sp.id, 1, 0, n=128))
        c2, m2 = Hn.host_run(vm, sp, c1, shabytes("SLOT", sp.id, 2, 0, n=128))
        return {"scope": "N/A (pair-tape only)", "certify": None,
                "repl_gen1": m1["repl"], "repl_gen2": m2["repl"], "fid_gen1": round(fid(sp.genome, c1), 4)}, \
            {"accept": bool(m1["repl"] and m2["repl"]), "analogue": "NPE REPL rule at gen 1 and 2"}, fid(sp.genome, c1)
    if sp.kind == "pair":
        other = shabytes("OBS", sp.id, n=n)
        ga, gb = (sp.genome, other) if side == 0 else (other, sp.genome)
        ev = Hn.p11_event(vm, tape_len=TL, ga=ga, gb=gb, victim_side=1 - side, K=K, tag="P11-PANEL-s%d" % side,
                          **common)
        fe = Hn.fert(vm, tape_len=TL, donor_side=side, ga=ga, gb=gb, tag="P11-PANEL-s%d" % side,
                     certified=ev["certify"], **common)
        return {"events": [ev], "certify": ev["certify"]}, fe, (ev["mean_fid_final"] if ev["P0"] else ev["obs_fid_other"])
    if sp.kind == "guest":
        host = S.Z5A_HOST + shabytes("OBS", sp.id, n=n - len(S.Z5A_HOST))
        evs = [Hn.p11_event(vm, tape_len=TL, ga=host, gb=sp.genome, victim_side=vs, K=K, tag="P11-PANEL-v%d" % vs,
                            **common) for vs in (0, 1)]
        cert = any(e["certify"] for e in evs)
        fe = {"accept": False, "children_pass": None} if not cert else None
        if cert:
            e = next(e for e in evs if e["certify"])
            fe = Hn.fert(vm, tape_len=TL, donor_side=1 - e["victim_side"], ga=host, gb=sp.genome,
                         tag="P11-PANEL-v%d" % e["victim_side"], certified=True, **common)
        best = max(evs, key=lambda e: e["mean_fid_final"] if e["P0"] else e["obs_fid_other"])
        return {"events": evs, "certify": cert}, fe, (best["mean_fid_final"] if best["P0"] else best["obs_fid_other"])
    if sp.kind == "quad":
        other = shabytes("OBS", sp.id, n=n)
        evs, fes = [], []
        for mem_i, Gm in enumerate((S.TV5_A0, S.TV5_A1)):
            e = Hn.p11_event(vm, n=n, tape_len=2 * n, budget=sp.budget, mask=0, cmr=CMR_P11, ga=Gm, gb=other,
                             victim_side=1, K=K, tag="P11-PANEL-m%d" % mem_i, sid=sp.id)
            e["member"] = mem_i
            evs.append(e)
            fes.append(Hn.fert(vm, n=n, tape_len=2 * n, budget=sp.budget, mask=0, cmr=CMR_P11, donor_side=0,
                               ga=Gm, gb=other, tag="P11-PANEL-m%d" % mem_i, certified=e["certify"], sid=sp.id))
        cert = any(e["certify"] for e in evs)
        best = max(evs, key=lambda e: e["mean_fid_final"] if e["P0"] else e["obs_fid_other"])
        return {"events": evs, "certify": cert}, {"accept": any(f["accept"] for f in fes)}, \
            (best["mean_fid_final"] if best["P0"] else best["obs_fid_other"])
    raise ValueError(sp.kind)


def evaluate(sp_id, z8name="sub"):
    z8mod = {"sub": Z8SUB, "ver": Z8VER}[z8name]
    sp = next(s for s in S.panel() if s.id == sp_id)
    vm = S.vm_for(sp, z8mod)
    t0 = time.time()
    rec = {"id": sp.id, "adversary": sp.adversary, "role": sp.role, "vm": sp.vmname, "kind": sp.kind,
           "n": sp.n, "budget": sp.budget, "mask": sp.mask, "side": sp.side, "genome": sp.genome.hex(),
           "truth_hereditary": sp.truth_hereditary, "truth_bits": sp.truth_bits}
    rec["gate"] = gates(sp, vm)
    p, fe, fobs = p11_block(sp, vm)
    rec["P11"], rec["FERT"] = p, fe
    rows, base = CE.cvt(lambda G, g, k: Hn.step(vm, sp, G, g, k), sp.genome, sp.id, sp.exhaustive)
    rec.update(CE.score(rows, sp.sites))
    rec["cvt_descendant_digest"] = __import__("hashlib").sha256(
        repr([r for r in rows] + [base]).encode()).hexdigest()
    rec["SHUF_diag"] = CE.shuf(sp.genome, fobs, sp.id)
    rec["DOM_diag"] = CE.dom(sp.genome)
    if sp.id in ("Z3", "Z3b"):
        p1, _, _ = p11_block(sp, vm, side=1)
        sp1 = dataclasses.replace(sp, side=1)
        rows1, _ = CE.cvt(lambda G, g, k: Hn.step(vm, sp1, G, g, k), sp.genome, sp.id, False)
        rec["sensitivity_side1"] = {"P11": p1, "CVT2": CE.score(rows1, sp.sites)["CVT2"]}
    if sp.id in ("Z3", "Z3b", "Z3u96", "Z6h", "TV-3", "TV-4", "TV-6"):
        rec["sensitivity_cmr_note"] = "CVT at world copy rate not run (not decision-bearing; see RESULT)"
    return rec, round(time.time() - t0, 2)


# ------------------------------------------------------------------ E0 against the aa5833488 VM
def plain_interact(vm, n, tape_len, ga, gb, budget, mask):
    tape = bytearray(tape_len)
    tape[0:len(ga)] = ga
    tape[n:n + len(gb)] = gb
    for who, start in ((0, 0), (1, n)):
        ctx = vm.Ctx(tape, start, n, policy=vm.ARENA, rng=random.Random(0), copy_mut_rate=0.0, sense=who)
        ctx.regs, ctx.fz, ctx.fc = None, 0, 0
        vm.run(ctx, start, budget, ops_enabled=mask)
    return bytes(tape)


def e0_orig():
    out = {}
    for sp in S.panel():
        if sp.vmname != "z8":
            continue
        res = []
        if sp.kind in ("pair", "guest"):
            cases = []
            if sp.kind == "pair":
                cases.append((sp.genome, shabytes("OBS", sp.id, n=sp.n)) if sp.side == 0 else
                             (shabytes("OBS", sp.id, n=sp.n), sp.genome))
                for k in range(3):
                    cases.append((sp.genome, shabytes("VICTIM", sp.id, 1, k, n=sp.n)))
            else:
                for k in range(3):
                    cases.append((S.Z5A_HOST + shabytes("HOSTCARGO", sp.id, 1, k, n=22), sp.genome))
            for ga, gb in cases:
                tt = [plain_interact(m, sp.n, sp.tape_len, ga, gb, sp.budget, sp.mask) for m in (Z8SUB, Z8VER, Z8ORIG)]
                res.append(tt[0] == tt[1] == tt[2])
        else:
            for k in range(3):
                pre = shabytes("SLOT", sp.id, 1, k, n=128)
                tt = [Hn.host_run(m, sp, sp.genome, pre)[0] for m in (Z8SUB, Z8VER, Z8ORIG)]
                res.append(tt[0] == tt[1] == tt[2])
        out[sp.id] = all(res)
    return out


def _job(a):
    return evaluate(*a)


def main():
    OUT.mkdir(exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "pilot":
        rec, dt = evaluate("Z1")
        print(json.dumps({"pilot_Z1_seconds": dt, "gate": rec["gate"]["pass"]}))
        return
    t0 = time.time()
    ids = [s.id for s in S.panel()]
    z8ids = [s.id for s in S.panel() if s.vmname == "z8"]
    jobs = [(i, "sub") for i in ids] + [(i, "ver") for i in z8ids] + [(i, "sub") for i in ids]
    with mp.Pool(2) as pool:
        res = pool.map(_job, jobs, chunksize=1)
    n = len(ids)
    first, ver, second = res[:n], res[n:n + len(z8ids)], res[n + len(z8ids):]
    recs = {r[0]["id"]: r[0] for r in first}
    times = {r[0]["id"]: r[1] for r in first}
    e0 = {"substrate_vs_verify": {r[0]["id"]: r[0] == recs[r[0]["id"]] for r in ver}, "vs_aa5833488": e0_orig()}
    e1 = {r[0]["id"]: r[0] == recs[r[0]["id"]] for r in second}
    gates_rep = {"E0": e0, "E0_pass": all(e0["substrate_vs_verify"].values()) and all(e0["vs_aa5833488"].values()),
                 "E1": e1, "E1_pass": all(e1.values()),
                 "G": {i: recs[i]["gate"] for i in ids}, "seconds_per_specimen": times,
                 "wall_seconds": round(time.time() - t0, 1), "files": file_hashes()}
    (OUT / "GATES_PANEL.json").write_text(json.dumps(gates_rep, indent=1, sort_keys=True))
    with open(OUT / "PANEL.jsonl", "w", encoding="ascii") as fh:
        for i in ids:
            fh.write(json.dumps(recs[i], sort_keys=True) + "\n")
    conf = {}
    for i in ids:
        r = recs[i]
        conf[i] = {"truth": r["truth_hereditary"], "role": r["role"], "P11": r["P11"]["certify"],
                   "FERT": r["FERT"]["accept"], "LOCAL": r["LOCAL"]["accept"], "CVT1": r["CVT1"]["accept"],
                   "CVT2": r["CVT2"]["accept"], "CVTR": r["CVTR"]["accept"],
                   "TB1": r["CVT1"]["TB"], "TB2": r["CVT2"]["TB"], "TBR": r["CVTR"]["TB"],
                   "SHUF_diag": r["SHUF_diag"]["accept"], "DOM_diag": r["DOM_diag"]["accept"],
                   "gate": r["gate"]["pass"]}
    (OUT / "CONFUSION.json").write_text(json.dumps(conf, indent=1, sort_keys=True))
    print(json.dumps({"E0_pass": gates_rep["E0_pass"], "E1_pass": gates_rep["E1_pass"],
                      "wall": gates_rep["wall_seconds"]}, indent=1))
    for i in ids:
        print(i, conf[i])


if __name__ == "__main__":
    main()
