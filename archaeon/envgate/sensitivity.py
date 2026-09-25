"""ENVGATE-01 POST-HOC sensitivity + forensics (written after the frozen analysis; does NOT change RESULTS.json or its verdict).

S1  the preregistration's own robustness test: block-level exact sign tests (respects within-world dependence of arrivals).
S2  copier-founded lineages only: founders the frozen ruler says can reproduce with an EMPTY neighbour (EXACT/NEAR/SPAN) -- excludes
    lineages whose founder only reproduces when facing an occupied cell.
H   host test: INERT/WRITER/TOUCH founders re-executed against the resident genome of a takeover world, all 256 inputs.
T   takeover worlds: worlds whose ecology ends >= 90% full; which arrival started it, its gate, and how many non-copier establishments
    they contain.
    python -m archaeon.envgate.sensitivity
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from archaeon.z80atlas import vm
from archaeon.envgate import mechanism as M
from archaeon.envgate.analyze import binom_tail, CONTRASTS
from archaeon.envgate.ruler import measure

HERE = Path(__file__).resolve().parent
COP = {"EXACT_UNGATED", "EXACT_GATED", "NEAR_COPIER", "SPAN_COPIER"}


def contrasts(E, pb):
    out = {}
    for X, Y, n in CONTRASTS:
        n10 = len(E[X] - E[Y]); n01 = len(E[Y] - E[X]); d = [pb[b][X] - pb[b][Y] for b in range(16)]
        pos = sum(x > 0 for x in d); neg = sum(x < 0 for x in d)
        out[n] = {"X": X, "Y": Y, "established_X": len(E[X]), "established_Y": len(E[Y]), "discordant": [n10, n01], "mcnemar_one_sided_p": binom_tail(n10, n10 + n01),
                  "block_diffs": d, "blocks_pos_neg": [pos, neg], "block_sign_one_sided_p": binom_tail(pos, pos + neg)}
    return out


def main(argv=None) -> int:
    R = json.loads((HERE / "RESULTS.json").read_text(encoding="utf-8")); Lz = json.loads((HERE / "LINEAGES.json").read_text(encoding="utf-8"))["lineages"]
    out = {"schema": "archaeon.envgate.sensitivity.v1", "status": "POST_HOC -- descriptive; the preregistered verdict in RESULTS.json is unchanged",
           "preregistered_verdict": R["verdict"], "S1_block_level": {k: {"block_diffs": v["block_diffs"], "block_sign_one_sided_p": v["block_sign_test_one_sided_p"]} for k, v in R["contrasts"].items()}}
    E = defaultdict(set); pb = defaultdict(lambda: defaultdict(int))
    for l in R["established_lineages"]:
        if l["ruler_class"] in COP: E[l["arm"]].add((l["block"], l["arrival"])); pb[l["block"]][l["arm"]] += 1
    out["S2_copier_founded"] = {"established": {a: len(E[a]) for a in M.ARM_ORDER}, "contrasts": contrasts(E, pb)}
    # T: takeover worlds
    tk = []; nc_in_tk = 0; nc_total = sum(1 for l in R["established_lineages"] if l["ruler_class"] not in COP)
    for p in sorted((HERE / "runs").glob("block_*.json")):
        b = json.loads(p.read_text(encoding="utf-8"))
        for a, s in b["arms"].items():
            if s["final_ecology_pop"] >= 0.9 * 128:
                cops = sorted((r for r in s["lineages"] if r["established"] and b["hits"].get(str(r["arrival"]), {}).get("class", "") in COP), key=lambda r: r["first_birth_epoch"])
                first = cops[0] if cops else None
                n_nc = sum(1 for r in s["lineages"] if r["established"] and b["hits"].get(str(r["arrival"]), {}).get("class", "") not in COP)
                nc_in_tk += n_nc
                tk.append({"block": b["block"], "arm": a, "final_pop": s["final_ecology_pop"], "births": s["births"], "established": s["n_established"],
                           "noncopier_established": n_nc, "earliest_copier_established_arrival": first and first["arrival"],
                           "its_gates": first and b["hits"][str(first["arrival"])]["exact_inputs"], "its_gate_in_band": bool(first and set(b["hits"][str(first["arrival"])]["exact_inputs"]) & set(M.GATE_BAND))})
    out["T_takeover_worlds"] = {"worlds": tk, "noncopier_establishments_inside_takeover_worlds": nc_in_tk, "noncopier_establishments_total": nc_total}
    # H: host test in the block-15 U takeover world
    res = [r for r in Lz if r["block"] == 15 and r["arm"] == "U" and r["dominant_descendants"]]
    host = {}
    if res:
        resident = bytes.fromhex(res[0]["dominant_descendants"][0]["tape"]); rr = measure(resident)
        hosts = [r for r in Lz if r["block"] == 15 and r["arm"] == "U" and r["founder_class"] == "INERT"]
        c = Counter()
        for h in hosts:
            t = bytes.fromhex(h["founder_tape"]); b_ = cp = fo = 0
            for x in range(256):
                q = vm.execute(t, resident, (x,), 256, True, -1.0)
                if sum(q["nbr_mask"]) / 32 >= 0.9:
                    b_ += 1; cp += q["nbr_window"] == resident; fo += q["exec_foreign"] > 0
            c["hosts"] += 1; c["give_births_facing_resident"] += b_ > 0; c["write_exact_copy_of_resident"] += cp > 0; c["births_via_foreign_execution"] += fo > 0
        host = {"resident_genome": resident.hex(), "resident_class": rr["class"], "resident_exact_input_count": len(rr.get("exact_inputs", [])), **dict(c)}
    out["H_host_test_block15_U"] = host
    (HERE / "SENSITIVITY.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"S2": out["S2_copier_founded"]["established"], "T_nc_in_takeover": [nc_in_tk, nc_total], "H": {k: v for k, v in host.items() if k != "resident_genome"}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
