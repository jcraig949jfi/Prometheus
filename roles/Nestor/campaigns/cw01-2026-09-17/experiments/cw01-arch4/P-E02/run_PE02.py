"""P-E02 [deformation B, T-X12]: PER-TAG TIMING LIVE BY CONSTRUCTION on the two-stream world.

W2_K2 base episodes: PUT tag1, PUT tag2, ASK, ASK. Variants (ticks.k2_variants): a NOISE tick
between the PUTs (tag1's ask is delayed relative to its PUT; tag2's timing relative to its own PUT
is unchanged), two such ticks, a NOISE tick before the first ask (both delayed), a NOISE tick
before the second ask (only the later ask delayed; the earlier ask is upstream and must show
displacement 0 - a fail-closed harness check). Self-displacement is read PER TAG. Cross-tag
interference = displacement of tag2's answer when only tag1's timing changed. One-stream control:
W0_heldout with a NOISE tick before the ask. Programs: shelf parents (W2_K2 natives), C4-08 tops,
w0_solver parents. Computational scope: integer programs on a bounded VM.
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
import ticks as TK             # noqa: E402
A, L = CM.A, CM.L
sys.path.insert(0, str(HERE.parent / "P-D01"))
from run_PD01 import c408_tops   # noqa: E402

PID, TID = "P-E02", "T-X12"
VARS = ["between_puts", "between_puts_x2", "before_first_ask", "before_second_ask"]


def per_tag_answers(m, eps, meta):
    """{tag_role: [answers]} with tag_role in {'tag1','tag2'} by PUT order, and by ask order."""
    a = A.C1.answers(m, eps)
    out = {"tag1": [], "tag2": [], "first_ask": [], "second_ask": []}
    k = 0
    for ep, md in zip(eps, meta):
        n = ep.n_asks()
        ans = a[k:k + n]
        k += n
        for ai, tag in enumerate(md["ask_order"]):
            out["tag1" if tag == md["tag1"] else "tag2"].append(ans[ai])
            out["first_ask" if ai == 0 else "second_ask"].append(ans[ai])
    return out


def job(j):
    p = j["program"]
    m = A.canonical(p["manifest"])
    eps = A.episodes("W2_K2")
    V, meta = TK.k2_variants(eps)
    base = per_tag_answers(m, V["base"], meta)
    d = {}
    for v in VARS:
        av = per_tag_answers(m, V[v], meta)
        d[v] = {k: A.C1.displacement(av[k], base[k]) for k in base}
    h = A.episodes("W0_heldout")
    Vh = TK.w0_variants(h)
    a0 = A.C1.answers(m, Vh["base"])
    one = A.C1.displacement(A.C1.answers(m, Vh["noise1"]), a0)
    ev = A.evaluate(m, V["base"], rng_seed=0, reward_mode="per_ask")
    return {"pid": p["organism_id"], "set": p["stratum"], "persist": m["persist"], "n_instr": CM.n_instr(m), "r0_k2": ev["reward_per_ask"], "answered_k2": ev["answered_share"],
            "disp": d, "one_stream_noise1": one, "tag1_first_share": float(np.mean([md["ask_order"][0] == md["tag1"] for md in meta]))}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "B", "scope": CM.SCOPE, "claim_type": "parameterized-switch-probe",
                         "ruler": "per-tag self-displacement on W2_K2 constructions; one-stream control on W0_heldout",
                         "variants": VARS, "harness_check": "before_second_ask must leave the FIRST ask's answers unchanged (displacement 0 on 'first_ask'); a violation voids the run",
                         "cross_tag_interference": "displacement of tag2's answers under between_puts (tag2's timing relative to its own PUT unchanged)",
                         "programs": "shelf parents, C4-08 ordinary top-32 seed 1, w0_solver parents",
                         "material_rule": "cross-tag displacement (tag2 under between_puts) mean >= .05 in any set, OR paired sign-flip of (tag1 - tag2 under between_puts) outside its band, OR (before_first_ask - one-stream noise1) outside its band",
                         "continuation": ["K=3", "tick between the PUTs of the SAME tag (D=2)", "programs evolved under W2 with inserted ticks"],
                         "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    vp = [p for p in CM.viable_parents() if not p["degenerate"]]
    programs = [dict(p, stratum="shelf_parent") for p in vp if p["stratum"] == "shelf"] + [dict(p, stratum="w0_parent") for p in vp if p["stratum"] == "w0_solver"] + c408_tops()
    with A.pool(8) as ex:
        rows = list(ex.map(job, [{"program": p} for p in programs]))
    upstream = max(r["disp"]["before_second_ask"]["first_ask"] for r in rows)
    harness_ok = upstream == 0.0
    sets = sorted({r["set"] for r in rows})
    summ = {}
    for st in sets:
        rs = [r for r in rows if r["set"] == st]
        summ[st] = {"n": len(rs), "answered_k2": float(np.mean([r["answered_k2"] for r in rs])),
                    "disp": {v: {k: float(np.mean([r["disp"][v][k] for r in rs])) for k in ("tag1", "tag2", "first_ask", "second_ask")} for v in VARS},
                    "one_stream_noise1": float(np.mean([r["one_stream_noise1"] for r in rs])),
                    "cross_tag_ge05_share": float(np.mean([r["disp"]["between_puts"]["tag2"] >= 0.05 for r in rs]))}
    sf_cross = CM.paired_signflip([r["disp"]["between_puts"]["tag1"] - r["disp"]["between_puts"]["tag2"] for r in rows])
    sf_streams = CM.paired_signflip([r["disp"]["before_first_ask"]["first_ask"] - r["one_stream_noise1"] for r in rows])
    sf_dose = CM.paired_signflip([r["disp"]["between_puts_x2"]["tag1"] - r["disp"]["between_puts"]["tag1"] for r in rows])
    cross_any = any(v["disp"]["between_puts"]["tag2"] >= 0.05 for v in summ.values())
    material = bool(harness_ok and (cross_any or (sf_cross and (sf_cross["above_p95"] or sf_cross["below_p05"])) or (sf_streams and (sf_streams["above_p95"] or sf_streams["below_p05"]))))
    out = {"perturbation_id": PID, "parent": TID, "harness_ok": harness_ok, "upstream_max_disp": upstream, "n_programs": len(rows), "summary": summ,
           "signflips": {"tag1_minus_tag2_between_puts": sf_cross, "k2_first_ask_minus_one_stream": sf_streams, "x2_minus_x1_tag1": sf_dose},
           "cross_tag_any_set": cross_any, "material": material, "disposition": ("RAN" if harness_ok else "INVALID_HARNESS"), "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "per-tag timing (harness %s): between_puts tag1/tag2 %s; before_first_ask %s; before_second_ask second %s; one-stream %s; tag1-tag2 %s; cross-tag>=.05 share %s"
                      % (harness_ok, {k: (round(v["disp"]["between_puts"]["tag1"], 3), round(v["disp"]["between_puts"]["tag2"], 3)) for k, v in summ.items()},
                         {k: round(v["disp"]["before_first_ask"]["first_ask"], 3) for k, v in summ.items()}, {k: round(v["disp"]["before_second_ask"]["second_ask"], 3) for k, v in summ.items()},
                         {k: round(v["one_stream_noise1"], 3) for k, v in summ.items()}, (round(sf_cross["mean_diff"], 3), sf_cross["above_p95"] or sf_cross["below_p05"]) if sf_cross else None,
                         {k: round(v["cross_tag_ge05_share"], 3) for k, v in summ.items()}), material, detail=summ)
    print("DONE material=%s harness=%s (%.0f s) %s" % (material, harness_ok, time.time() - t0, json.dumps({k: v["disp"]["between_puts"] for k, v in summ.items()})))


if __name__ == "__main__":
    main()
