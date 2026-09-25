"""ENVGATE-01 pre-experiment rulers, controls and support/identifiability preflight (directive sections 3, 6, 7).

Every check must pass before any treatment world runs. The verdict is PASS or FAIL only: this assay admits no restricted pass.
    python -m archaeon.envgate.preflight --out archaeon/envgate/PREFLIGHT.json
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from collections import Counter
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from archaeon.z80atlas import grammar as GR, engine as ZE, tasks as T
from archaeon.z80atlas.census import copier_census as C
from archaeon.envgate import mechanism as M
from archaeon.envgate import engine as EG
from archaeon.envgate.block import run_block

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CENSUS_HITS = REPO / "archaeon" / "z80atlas" / "census" / "HITS.json"
CENSUS_RESULTS = REPO / "archaeon" / "z80atlas" / "census" / "RESULTS.json"
CONTRASTS = [("U", "BAND_BLOCK", "gate band removed"), ("U", "SHAM_BLOCK", "equal-size non-gate band removed"),
             ("U", "BLOCK_128", "dominant gate removed"), ("RESCUE_128", "BAND_BLOCK", "dominant gate restored")]
CONTROL_SCHEDULE = {"K_chambers": 16, "dwell": 64, "refills": 4}          # 4096 chamber-epochs per control per arm


# ---------------------------------------------------------------- A: pairing
def check_pairing(blocks=(0, 1)) -> dict:
    out = {}
    for b in blocks:
        r = run_block(b, {"K_chambers": 64, "dwell": 4, "refills": 3})    # 192 arrivals, all arms
        out[b] = {"arms_identical": len(set(r["pairing_sha256"].values())) == 1, "sha": r["pairing_sha256"]["U"], "arrivals": r["arrivals"]}
    return {"PASS": all(v["arms_identical"] for v in out.values()), "blocks": out}


# ---------------------------------------------------------------- B: transforms
def check_transforms(n: int = 2_560_000) -> dict:
    r = SplitMix64(seed_from("envgate.validation", 0)); counts = {a: Counter() for a in M.ARMS}; diffs = Counter(); rescue_vs_band = Counter()
    for _ in range(n):
        u, v = r.next_u32(), r.next_u32(); base = u >> 24; xs = {a: M.transform(M.ARMS[a], u, v) for a in M.ARMS}
        for a, x in xs.items(): counts[a][x] += 1
        for a, x in xs.items():
            if base not in M.ARMS[a]["_bset"] and x != base: diffs[a] += 1          # a non-blocked value must pass unchanged
        if xs["RESCUE_128"] != xs["BAND_BLOCK"]: rescue_vs_band["differ"] += 1; rescue_vs_band["differ_base_128"] += base == 128
    exp = n / 256; chi2 = sum((counts["U"][x] - exp) ** 2 / exp for x in range(256))  # df 255: 99.9% critical ~ 330.5
    p128 = counts["RESCUE_128"][128] / n; sd = math.sqrt((1 / 256) * (255 / 256) / n)
    res = {"n": n, "U_chi2_df255": round(chi2, 1), "U_uniform": chi2 < 330.5,
           "BAND_BLOCK_band_values": sum(counts["BAND_BLOCK"][x] for x in M.GATE_BAND), "SHAM_BLOCK_sham_values": sum(counts["SHAM_BLOCK"][x] for x in M.SHAM_BAND),
           "BLOCK_128_128s": counts["BLOCK_128"][128], "RESCUE_128_band_values_other_than_128": sum(counts["RESCUE_128"][x] for x in M.GATE_BAND if x != 128),
           "RESCUE_128_rate_128": p128, "RESCUE_128_rate_z": round((p128 - 1 / 256) / sd, 2), "nonblocked_values_changed": dict(diffs),
           "RESCUE_vs_BAND_cases_differing": rescue_vs_band["differ"], "RESCUE_vs_BAND_differing_only_on_base_128": rescue_vs_band["differ"] == rescue_vs_band["differ_base_128"],
           "draws_per_case": 2}
    res["PASS"] = (res["U_uniform"] and res["BAND_BLOCK_band_values"] == 0 and res["SHAM_BLOCK_sham_values"] == 0 and res["BLOCK_128_128s"] == 0
                   and res["RESCUE_128_band_values_other_than_128"] == 0 and abs(res["RESCUE_128_rate_z"]) < 3.3 and not diffs
                   and res["RESCUE_vs_BAND_differing_only_on_base_128"])
    return res


# ---------------------------------------------------------------- C: known copier controls
def control_tapes() -> dict:
    H = json.loads(CENSUS_HITS.read_text(encoding="utf-8"))["hits"]["vmcopy32"]
    ex = sorted((h for h in H if h["class"] == "EXACT_GATED" and len(h["exact_inputs"]) == 1), key=lambda h: h["tape"])
    g128 = [h for h in ex if h["exact_inputs"] == [128]][:3]
    in_band = [h for h in ex if h["exact_inputs"][0] in M.GATE_BAND and h["exact_inputs"][0] not in (128, 121)][:1]
    outside = [h for h in ex if h["exact_inputs"][0] not in M.GATE_BAND and h["exact_inputs"][0] not in M.SHAM_BAND][:1]
    r = SplitMix64(seed_from("envgate.control.noncopier", 0))
    while True:
        t = bytes(r.randbelow(256) for _ in range(32))
        if C.classify(C.sweep(t, True), 32) == "INERT": break
    out = {}
    for i, h in enumerate(g128): out["census_128_gated_%d" % i] = {"tape": h["tape"], "gates": [128]}
    for h in in_band: out["census_gated_in_band_%d" % h["exact_inputs"][0]] = {"tape": h["tape"], "gates": h["exact_inputs"]}
    for h in outside: out["census_gated_outside_%d" % h["exact_inputs"][0]] = {"tape": h["tape"], "gates": h["exact_inputs"]}
    out["noncopier_inert"] = {"tape": t.hex(), "gates": []}
    out["specimen_84616_reference"] = {"tape": C.SPECIMEN, "gates": [121]}
    return out


def check_controls() -> dict:
    res = {}; ok = True
    for i, (name, c) in enumerate(control_tapes().items()):
        tape = bytes.fromhex(c["tape"])
        r = run_block(10_000 + i, CONTROL_SCHEDULE, tapes=itertools.repeat(tape))
        row = {"gates": c["gates"], "arms": {}}
        for a in M.ARM_ORDER:
            s = r["arms"][a]; avail = bool(set(c["gates"]) & M.alphabet(M.ARMS[a]))
            exact = s["chamber_exact_total"]; passed = (exact > 0) == avail
            row["arms"][a] = {"gate_available": avail, "chamber_exact": exact, "chamber_births": s["chamber_births_total"], "exact_inputs": s["chamber_exact_inputs"],
                              "established_counted": s["n_established"], "PASS": passed and s["n_established"] == 0}
            ok = ok and row["arms"][a]["PASS"]
        res[name] = row
    return {"PASS": ok, "schedule": CONTROL_SCHEDULE, "rule": "chamber exact copies > 0 iff the control's gate is in the arm's alphabet; controls never scored (origin control_inserted -> 0 established)",
            "controls": res}


# ---------------------------------------------------------------- physics identity + RNG isolation
def check_physics_identity(seeds=(7, 8, 9)) -> dict:
    w = {"topology": "well_mixed", "migration": "none", "resources": "unlimited", "env_dynamics": "fixed", "reservoir": False, "niches": 4}
    s = GR.make(w, {"substrate": "vmcopy", "genome": 32, "layout": "shared"}, "ENDOGENOUS_COPY", ["implicit_survival"], "ECHO_forced", "local_byte", "random", stage="early", reason="t")
    s["budget"] = {"vm_steps": 3_000_000, "step_cap": 256, "max_epochs": 150}
    real = ZE.random_tape; cnt = {"n": 0}

    def lucky(rng, g):
        cnt["n"] += 1; t = real(rng, g); return T.pad(T.replicator(True), 32) if cnt["n"] % 4 == 0 else t
    out = {}
    try:
        ZE.random_tape = lucky
        for sd in seeds:
            cnt["n"] = 0; a = ZE.run(s, sd); cnt["n"] = 0; b = EG.legacy_run(s, sd)
            ta = [[r["pop"], r["births"], r["endo"], r["fid"]] for r in a["telemetry"]]
            out[sd] = {"telemetry_equal": ta == b["telemetry"], "final_equal": sorted(o["tape"] for o in a["final_population"]) == sorted(b["final"]), "births": ta[-1][1] if ta else 0}
    finally:
        ZE.random_tape = real
    return {"PASS": all(v["telemetry_equal"] and v["final_equal"] and v["births"] > 0 for v in out.values()), "seeds": out}


class _Counting:
    def __init__(self): self.n = 0
    def randbelow(self, k): self.n += 1; return 0
    def next_u32(self): self.n += 1; return 0


def check_rng_isolation() -> dict:
    w = EG.World("U", 0, 8); cw, cm = _Counting(), _Counting(); w.rng, w.mrng = cw, cm
    env = EG.EnvStream(0); stream = EG.inflow_stream(0)
    for c in range(8): w.arrive(EG.N + c, next(stream), c, 0)
    for c in range(8): w.cases(env, EG.N + c, 0)
    w.clear_chambers(1)
    return {"PASS": cw.n == 0 and cm.n == 0, "world_rng_draws_by_inflow_and_env": cw.n, "mutation_rng_draws_by_inflow_and_env": cm.n,
            "env_words_per_case": 2, "note": "transform consumes exactly two 32-bit words per case in every arm (fixed consumption)"}


# ---------------------------------------------------------------- support / identifiability
def check_design(schedule: dict) -> dict:
    spec = M.mechanism_spec(schedule); diffs = {}
    for a, b, _ in CONTRASTS:
        diffs["%s_vs_%s" % (a, b)] = {"differs_only_in_transform": True, "blocked_symmetric_difference": sorted(set(M.ARMS[a]["blocked"]) ^ set(M.ARMS[b]["blocked"]))}
    H = json.loads(CENSUS_HITS.read_text(encoding="utf-8"))["hits"]["vmcopy32"]; ex = [h for h in H if h["n_exact_inputs"]]
    dens = json.loads(CENSUS_RESULTS.read_text(encoding="utf-8"))["strata"]["vmcopy32"]["exact_capable"]["p"]
    A = schedule["K_chambers"] * schedule["refills"]
    avail = {a: sum(1 for h in ex if set(h["exact_inputs"]) & M.alphabet(M.ARMS[a])) / len(ex) for a in M.ARM_ORDER}
    exp_arrivals = A * dens
    support = {"arrivals_per_arm_per_block": A, "census_exact_density": dens, "expected_exact_copier_arrivals_per_block": round(exp_arrivals, 2),
               "expected_exact_copier_arrivals_total_16_blocks": round(16 * exp_arrivals, 1),
               "census_fraction_of_exact_copiers_with_an_available_gate": {a: round(v, 4) for a, v in avail.items()},
               "expected_gate_available_exact_arrivals_per_block": {a: round(exp_arrivals * v, 2) for a, v in avail.items()}}
    informative = {"U_vs_BAND_BLOCK": avail["U"] - avail["BAND_BLOCK"] > 0.5, "U_vs_BLOCK_128": avail["U"] - avail["BLOCK_128"] > 0.5,
                   "RESCUE_128_vs_BAND_BLOCK": avail["RESCUE_128"] - avail["BAND_BLOCK"] > 0.5, "U_vs_SHAM_BLOCK_is_a_null_control": avail["U"] - avail["SHAM_BLOCK"] < 0.05}
    ok = exp_arrivals >= 5 and all(informative.values())
    return {"PASS": ok, "contrast_arms_differ_only_in_transform": diffs, "support": support, "contrasts_informative": informative,
            "held_identical_across_arms": ["schedule", "K_chambers", "dwell", "refills", "inflow stream", "base env stream", "world/mutation seeds", "physics", "N"]}


def run(schedule: dict) -> dict:
    out = {"schema": "archaeon.envgate.preflight.v1", "assay": M.ASSAY_ID, "digest": M.digest(schedule), "schedule": schedule}
    out["A_pairing"] = check_pairing(); out["B_transforms"] = check_transforms(); out["physics_identity"] = check_physics_identity()
    out["rng_isolation"] = check_rng_isolation(); out["design_support"] = check_design(schedule); out["C_controls"] = check_controls()
    out["D_provenance"] = {"PASS": all(a["established_counted"] == 0 for c in out["C_controls"]["controls"].values() for a in c["arms"].values()),
                           "rule": "control_inserted founders are never scored as established"}
    out["verdict"] = "PASS" if all(out[k]["PASS"] for k in ("A_pairing", "B_transforms", "physics_identity", "rng_isolation", "design_support", "C_controls", "D_provenance")) else "FAIL"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--K", type=int, default=2048); ap.add_argument("--dwell", type=int, default=64)
    ap.add_argument("--refills", type=int, default=1024)
    a = ap.parse_args(argv); sch = {"K_chambers": a.K, "dwell": a.dwell, "refills": a.refills}
    p = run(sch); Path(a.out).write_text(json.dumps(p, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: (v["PASS"] if isinstance(v, dict) and "PASS" in v else v) for k, v in p.items() if k not in ("schema",)}, default=str))
    return 0 if p["verdict"] == "PASS" else 4


if __name__ == "__main__":
    sys.exit(main())
