"""P-I03 [T-X17, deformation P]: PREFIX DISSECTION - the prefix as a candidate control interface; geometry and
competence measured apart. Computational scope: integer programs on a bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import manifold as MF          # noqa: E402
A, L = CM.A, CM.L
sys.path.insert(0, str(HERE.parent / "P-H04"))
from run_PH04 import hosts     # noqa: E402

PID, TID = "P-I03", "T-X17"
DONORS = {5: ("ask_time", "W0"), 0: ("start_anchored", "W1_d4")}
KS, NDON, FLOOR, BAND = (1, 2, 4, 8), 4, A.C1.FLOOR, A.C1.BAND
JMP, NOPI = 18, [0, 0, 0, 0]


def jmp(off):
    return [JMP, 0, off & 0xFFFFFFFF, 0]


def instrs(g):
    return [g[i:i + A.IW] for i in range(0, len(g), A.IW)]


def build(base, ins):
    c = json.loads(json.dumps(base))
    c["genome"] = [w for i in ins for w in i]
    if len(c["genome"]) > c["tape_words"]:
        c["tape_words"] = min(4096, ((len(c["genome"]) + 3) // 4) * 4 + 4)
    return c


def variants(donor, host, k):
    D, H = instrs(donor["genome"]), instrs(host["genome"])
    k = min(k, len(D))
    out = {"prefix_to_host": build(host, D[:k] + H), "prefix_jmp0_host": build(host, D[:k] + [jmp(1)] + H), "prefix_jmpmid_host": build(host, D[:k] + [jmp(1 + len(H) // 2)] + H),
           "host_prefix_donor_body": build(donor, H[:k] + D[k:]), "truncation": build(donor, D[:k]), "relocated": build(donor, D[k:] + D[:k]),
           "jump_entry": build(donor, [jmp(1 + k)] + [list(NOPI) for _ in range(k)] + D)}
    return out


def measure(m, ref_curve, dworld, hworld):
    try:
        v = MF.curve(m)[0]
        rd = A.evaluate(m, A.episodes(dworld), rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
        rh = A.evaluate(m, A.episodes(hworld), rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
    except Exception as e:      # noqa: BLE001
        return {"valid": False, "err": str(e)[:60]}
    D = MF.distinctive(ref_curve)
    geo = bool(D) and all(v[i] == v[i] and v[i] >= 0.3 for i in D)
    return {"valid": True, "geometry": geo, "d_donor": MF.dist(v, ref_curve), "reward_donor_world": rd, "reward_host_world": rh, "vector": v}


def job(j):
    donor, host = A.canonical(j["donor"]["manifest"]), A.canonical(j["host"]["manifest"])
    dworld, hworld = j["dworld"], j["host"]["env"]
    vd = MF.curve(donor)[0]
    rd0 = A.evaluate(donor, A.episodes(dworld), rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
    rh0 = A.evaluate(host, A.episodes(dworld), rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
    out = {"donor": j["donor"]["organism_id"], "shape": j["shape"], "host": j["host"]["organism_id"], "host_role": j["host"]["role"], "dworld": dworld, "donor_r0": rd0, "host_r0_on_donor_world": rh0, "n_donor": len(donor["genome"]) // A.IW, "cells": {}}
    for k in KS:
        for name, m in variants(donor, host, k).items():
            r = measure(m, vd, dworld, hworld)
            if r["valid"]:
                r["competence"] = bool(r["reward_donor_world"] >= FLOOR and r["reward_donor_world"] >= rh0 + BAND and r["reward_donor_world"] >= 0.5 * rd0)
            out["cells"]["%s|k%d" % (name, k)] = {kk: vv for kk, vv in r.items() if kk != "vector"}
    return out


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-X19", "T-ARCH4/M1"], "deformation": "P", "scope": CM.SCOPE, "claim_type": "dissection",
                         "donors": {v[0]: (NDON, v[1]) for v in DONORS.values()}, "hosts": "P-H04's naive hosts (gen0, immune shelf, immune W2 tops)", "k": KS,
                         "variants": ["prefix_to_host", "prefix_jmp0_host (JMP into host at 0)", "prefix_jmpmid_host (JMP into host at mid)", "host_prefix_donor_body", "truncation (prefix alone)", "relocated (prefix moved to the end)", "jump_entry (JMP over k NOPs into the donor)"],
                         "geometry": "distinctive-component test: every donor component >= .5 must be >= .3 in the variant (D088)", "competence": "reward on the donor world >= floor, >= host baseline + band, and >= half the donor's",
                         "reading": "SEQUENCE_CONTENT if truncations keep geometry/competence at small k; ENTRY_ROUTING if relocated/jump_entry lose them; EARLY_STATE if prefix_to_host transfers what truncation alone does not; REACHABILITY if the JMP variants differ from prefix_to_host",
                         "material_rule": "any variant family transfers competence in >= 20 percent of cells, or the reading discriminates two of the four hypotheses", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    H = hosts()
    jobs = [{"donor": d, "shape": sh, "dworld": w, "host": h} for c, (sh, w) in DONORS.items() for d in MF.representatives(c, NDON) for h in H]
    with A.pool(8) as ex:
        rows = list(ex.map(job, jobs))
    table = {}
    for sh in ("ask_time", "start_anchored"):
        rs = [r for r in rows if r["shape"] == sh]
        for name in ("prefix_to_host", "prefix_jmp0_host", "prefix_jmpmid_host", "host_prefix_donor_body", "truncation", "relocated", "jump_entry"):
            for k in KS:
                cells = [r["cells"].get("%s|k%d" % (name, k)) for r in rs]
                cells = [c for c in cells if c and c.get("valid")]
                table["%s|%s|k%d" % (sh, name, k)] = {"n": len(cells), "geometry": float(np.mean([c["geometry"] for c in cells])) if cells else None, "competence": float(np.mean([c["competence"] for c in cells])) if cells else None,
                                                     "reward_donor_world": float(np.mean([c["reward_donor_world"] for c in cells])) if cells else None, "d_donor": float(np.mean([c["d_donor"] for c in cells])) if cells else None}
    fam = {}
    for name in ("prefix_to_host", "prefix_jmp0_host", "prefix_jmpmid_host", "host_prefix_donor_body", "truncation", "relocated", "jump_entry"):
        cs = [v for k, v in table.items() if ("|%s|" % name) in k and v["competence"] is not None]
        fam[name] = {"competence": float(np.mean([v["competence"] for v in cs])) if cs else None, "geometry": float(np.mean([v["geometry"] for v in cs])) if cs else None}
    reading = []
    if fam["truncation"]["competence"] and fam["truncation"]["competence"] >= 0.2:
        reading.append("SEQUENCE_CONTENT")
    if (fam["relocated"]["competence"] or 0) + 0.2 < (fam["truncation"]["competence"] or 0) or (fam["jump_entry"]["competence"] or 0) + 0.2 < (fam["truncation"]["competence"] or 0):
        reading.append("ENTRY_ROUTING")
    if (fam["prefix_to_host"]["competence"] or 0) >= (fam["truncation"]["competence"] or 0) + 0.2:
        reading.append("EARLY_STATE")
    if abs((fam["prefix_jmp0_host"]["competence"] or 0) - (fam["prefix_to_host"]["competence"] or 0)) >= 0.2 or abs((fam["prefix_jmpmid_host"]["competence"] or 0) - (fam["prefix_to_host"]["competence"] or 0)) >= 0.2:
        reading.append("REACHABILITY")
    material = bool(any((v["competence"] or 0) >= 0.2 for v in fam.values()) or len(reading) >= 2)
    out = {"perturbation_id": PID, "parent": TID, "reading": reading or ["UNRESOLVED"], "families": fam, "table": table, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "prefix dissection: reading %s; families (competence, geometry) %s; truncation by k %s" % (out["reading"], {k: (round(v["competence"], 2) if v["competence"] is not None else None, round(v["geometry"], 2) if v["geometry"] is not None else None) for k, v in fam.items()},
                                                                                                           {k: (round(v["competence"], 2) if v["competence"] is not None else None, round(v["reward_donor_world"], 2) if v["reward_donor_world"] is not None else None) for k, v in table.items() if "|truncation|" in k}), material, detail={"families": fam})
    for tid in ("T-X19", "T-ARCH4/M1"):
        L.append_evidence(tid, PID, "cross: prefix families (competence) %s; reading %s" % ({k: round(v["competence"], 2) if v["competence"] is not None else None for k, v in fam.items()}, out["reading"]), material)
    print("DONE material=%s reading=%s (%.0f s) %s" % (material, out["reading"], time.time() - t0, {k: (v["competence"], v["geometry"]) for k, v in fam.items()}))


if __name__ == "__main__":
    main()
