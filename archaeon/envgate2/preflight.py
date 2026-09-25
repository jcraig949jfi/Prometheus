"""ENVGATE-02 preflight: every check must pass; verdict PASS or FAIL only (no waiver path exists).
    python -m archaeon.envgate2.preflight
"""
from __future__ import annotations

import itertools
import json
import math
import subprocess
import sys
from collections import Counter
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from archaeon.z80atlas import vm
from archaeon.envgate import mechanism as M1
from archaeon.envgate.block import run_block as envgate1_block
from archaeon.envgate2 import mechanism as M
from archaeon.lineage import core as LC
from archaeon.lineage.assay_block import run_block, inflow, Env, transform_inputs
from archaeon.lineage.taint_vm import execute_taint

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
LABEL = "envgate2"


def pairing():
    r = run_block(LABEL, 900, {"K_chambers": 64, "dwell": 4, "refills": 3}, M.ARMS)
    return {"PASS": len(set(r["pairing_sha256"].values())) == 1 and r["arrivals"] == 192, "sha": r["pairing_sha256"]["U"]}


def transforms(n=2_560_000):
    r = SplitMix64(seed_from("envgate2.validation", 0)); cnt = {a: Counter() for a in M.ARMS}; bad = Counter(); differ = Counter()
    for _ in range(n):
        u, v = r.next_u32(), r.next_u32(); base = u >> 24; xs = {a: M1.transform(M.ARMS[a], u, v) for a in M.ARMS}
        for a, x in xs.items():
            cnt[a][x] += 1
            if x in M.ARMS[a]["_bset"]: bad[a + "_blocked_emitted"] += 1
            if base not in M.ARMS[a]["_bset"] and x != base: bad[a + "_passthrough_changed"] += 1
        for a in ("R128", "RRIGHT", "RWEAK"):
            if xs[a] != xs["BAND0"] and base not in M.ARMS[a]["restored"]: bad[a + "_differs_from_BAND0_off_restored"] += 1
    sd = math.sqrt((1 / 256) * (255 / 256) / n); z = {}
    for a in ("R128", "RRIGHT", "RWEAK"):
        for x in M.ARMS[a]["restored"]: z["%s_%d" % (a, x)] = round((cnt[a][x] / n - 1 / 256) / sd, 2)
    chi = sum((cnt["U"][x] - n / 256) ** 2 / (n / 256) for x in range(256))
    return {"PASS": not bad and chi < 330.5 and all(abs(v) < 3.9 for v in z.values()), "violations": dict(bad), "U_chi2_df255": round(chi, 1), "restored_rate_z": z, "n": n}


def conformance():
    """Attributed core == envgate engine (itself == frozen z80atlas physics) on copier-driven dynamics, all five ENVGATE-01 arms."""
    from archaeon.z80atlas.census import copier_census as C
    sch = {"K_chambers": 64, "dwell": 16, "refills": 12}; t = bytes.fromhex(C.SPECIMEN)
    a = envgate1_block(8, sch, tapes=itertools.repeat(t)); b = run_block("envgate", 8, sch, M1.ARMS, tapes=itertools.repeat(t), origin=LC.ORIGIN_CONTROL)
    ok = all(a["arms"][k]["births"] == b["arms"][k]["births"] and [x[:3] for x in a["arms"][k]["telemetry"]] == [x[:3] for x in b["arms"][k]["telemetry"]] for k in M1.ARMS)
    r = SplitMix64(seed_from("envgate2.taintdiff", 0)); mism = 0
    for cp in (True, False):
        for _ in range(5000):
            tp = bytes(r.randbelow(256) for _ in range(32)); nb = bytes(r.randbelow(256) for _ in range(32)); x = (r.randbelow(256),)
            mism += vm.execute(tp, nb, x, 256, cp, -1.0) != execute_taint(tp, nb, x, 256, cp, -1.0)[0]
    return {"PASS": ok and mism == 0, "core_equals_envgate_engine": ok, "taint_vm_mismatches_of_10000": mism}


class _Count:
    def __init__(self): self.n = 0
    def randbelow(self, k): self.n += 1; return 0
    def next_u32(self): self.n += 1; return 0


def rng_isolation():
    env = Env(LABEL, 0); w = LC.World("iso", 8, (LABEL + ".world", 0), (LABEL + ".mutation", 0), transform_inputs(env, M.ARMS["RRIGHT"]))
    cw, cm = _Count(), _Count(); w.rng, w.mrng = cw, cm; s = inflow(LABEL, 0)
    for c in range(8): w.arrive(LC.N + c, next(s), c, 0)
    for c in range(8): w.inputs(w, LC.N + c, 0)
    w.clear_chambers(1)
    return {"PASS": cw.n == 0 and cm.n == 0, "world_draws": cw.n, "mutation_draws": cm.n}


def controls():
    H = json.loads((REPO / "archaeon/z80atlas/census/HITS.json").read_text(encoding="utf-8"))["hits"]["vmcopy32"]
    ex = sorted((h for h in H if h["class"] == "EXACT_GATED" and len(h["exact_inputs"]) == 1), key=lambda h: h["tape"])
    pick = [h for h in ex if h["exact_inputs"] == [128]][:2] + [h for h in ex if h["exact_inputs"][0] in (125, 126, 127, 129, 130, 131)][:2] + \
           [h for h in ex if h["exact_inputs"][0] not in M.BAND][:1]
    out = {}; ok = True
    for i, h in enumerate(pick):
        r = run_block(LABEL + ".control", 10_000 + i, {"K_chambers": 16, "dwell": 64, "refills": 4}, M.ARMS, tapes=itertools.repeat(bytes.fromhex(h["tape"])),
                      origin=LC.ORIGIN_CONTROL, keep_worlds=True)
        row = {}
        for a in M.ARM_ORDER:
            w = r["arms"][a]["_world"]; avail = bool(set(h["exact_inputs"]) & M.alphabet(M.ARMS[a]))
            exact = sum(1 for e in w.events if e["exact"] and e["executor_cell"] >= LC.N)
            row[a] = {"gate_available": avail, "chamber_exact_copies": exact, "genetic_established": len(w.genetic_establishments()),
                      "PASS": ((exact > 0) == avail) and len(w.genetic_establishments()) == 0}
            ok = ok and row[a]["PASS"]
        out["gate_%d_%s" % (h["exact_inputs"][0], h["tape"][:8])] = row
    return {"PASS": ok, "rule": "exact chamber copies iff gate in alphabet; inserted controls never establish", "controls": out}


def design(schedule, blocks):
    d = M.D; pred = M.predictions()
    dens = json.loads((REPO / "archaeon/z80atlas/census/RESULTS.json").read_text(encoding="utf-8"))["strata"]["vmcopy32"]["exact_capable"]["p"]
    A = schedule["K_chambers"] * schedule["refills"]
    ok = d["identifiable"] and len(d["rright"]) == len(d["rweak"]) and pred["predicted_ordering"] == ["U", "RRIGHT", "RWEAK", "R128", "BAND0"] and A * dens >= 5
    return {"PASS": ok, "design": d, "predictions": pred, "arrivals_per_arm_per_block": A, "expected_latent_exact_copiers_per_block": round(A * dens, 2),
            "blocks": len(blocks), "contrast_arms_differ_only_in_restored_set": True}


def attribution_tests():
    p = subprocess.run([sys.executable, "-m", "pytest", "archaeon/tests/test_lineage_attribution.py", "-q", "-p", "no:cacheprovider"], cwd=REPO,
                       capture_output=True, text=True)
    last = [l for l in p.stdout.strip().splitlines() if "passed" in l or "failed" in l][-1:]
    return {"PASS": p.returncode == 0 and "failed" not in (last[0] if last else "failed"), "summary": last}


def run(schedule, blocks):
    out = {"schema": "archaeon.envgate2.preflight.v1", "assay": M.ASSAY_ID, "digest": M.digest(schedule, blocks)}
    for k, f in (("attribution_tests", attribution_tests), ("pairing", pairing), ("transforms", transforms), ("conformance", conformance),
                 ("rng_isolation", rng_isolation), ("controls", controls)):
        out[k] = f(); print(k, out[k]["PASS"], flush=True)
    out["design_support"] = design(schedule, blocks)
    out["verdict"] = "PASS" if all(out[k]["PASS"] for k in ("attribution_tests", "pairing", "transforms", "conformance", "rng_isolation", "controls", "design_support")) else "FAIL"
    return out


if __name__ == "__main__":
    from archaeon.envgate2.run_assay import SCHEDULE, BLOCKS
    p = run(SCHEDULE, BLOCKS); (HERE / "PREFLIGHT.json").write_text(json.dumps(p, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    print(p["verdict"]); sys.exit(0 if p["verdict"] == "PASS" else 4)
