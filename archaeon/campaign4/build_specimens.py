"""Proteus PROTEUS-37 / Round-2 anatomy specimens (answers comms #340).

    python -m archaeon.campaign4.build_specimens [--w0-seeds 12]

Three specimen sets, every manifest carried VERBATIM with its content-addressed organism id, its
provenance (experiment, arm, seed, attempt of record) and its measured competence, so Proteus can
bind each one to the frozen identity pfp1:625bc70456ebfa20 == instr1-16:6528b9dc without asking
Archaeon a second question:

  delay_general  the 11 C3-SFE-03 elites that went delay-general (held-out 1.0 on delays
                 0/1/2/4). These are the campaign's only reproducible positive capability.
  w0_solver      matched W0 solvers: same cell competence (held-out >= 0.9 on W0), NOT
                 delay-general (measured here on d8/d16, not assumed). Harvested by the same
                 deterministic procedure C3-SFE-04 used, so the set is reproducible from seeds.
  shelf          the 12 C3-SFE-01 shelf elites that C3-SFE-02 anatomised (level SHELF).

Each manifest is re-scored HERE on held-out batteries, so the numbers in this file are measured
at emission rather than copied from a row.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

from proteus.foundry.identity import hash_obj, RUNTIME_HASH
from proteus.foundry.grammar import GRAMMAR_HASH, GRAMMAR_VERSION

from archaeon.wse.evolve import evaluate
from archaeon.wse.worlds import WorldSpec, episodes_for
from archaeon.campaign3.c3base import CAMPAIGN_SEED as C3_SEED
from archaeon.campaign3.c3_sfe04 import harvest_w0, W0, TARGETS

REPO = Path(__file__).resolve().parents[2]
C3 = REPO / "archaeon" / "campaign3"
OUT = REPO / "archaeon" / "campaign4" / "SPECIMENS_FOR_PROTEUS.json"

W2_K2 = WorldSpec("W2_K2", K=2, value_bits=4)
LADDER = [WorldSpec("W0", value_bits=4), WorldSpec("W1_d1", delay=1, value_bits=4),
          WorldSpec("W1_d2", delay=2, value_bits=4), WorldSpec("W1_d4", delay=4, value_bits=4)]
BEYOND = [WorldSpec("W1_d8", delay=8, value_bits=4), WorldSpec("W1_d16", delay=16, value_bits=4)]
HELDOUT_N = 48


def score(manifest: dict, spec: WorldSpec, seed: int) -> float:
    eps = episodes_for(spec, C3_SEED, "heldout", seed, HELDOUT_N)
    return round(evaluate(manifest, eps, rng_seed=7)["reward"], 4)


def rows(experiment: str) -> list:
    return json.loads((C3 / experiment / "rows.json").read_text(encoding="utf-8"))


def profile(manifest: dict, seed: int, cells: list) -> dict:
    return {c.name: score(manifest, c, seed) for c in cells}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--w0-seeds", type=int, default=12)
    ap.add_argument("--harvest-G", type=int, default=60)
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--E", type=int, default=16)
    a = ap.parse_args(argv)
    t0 = time.time()

    # ---- 1. delay-general elites (C3-SFE-03, attempt of record a05)
    general = []
    for r in sorted(rows("C3-SFE-03"), key=lambda r: r["seed"]):
        if r.get("general_heldout") == 1 and r.get("elite_manifest"):
            m = r["elite_manifest"]
            general.append({
                "organism_id": hash_obj(m), "manifest": m,
                "provenance": {"experiment": "C3-SFE-03", "attempt_of_record": "a05", "arm": r["arm"], "seed": r["seed"],
                               "campaign_seed": C3_SEED, "general_gen": r.get("general_gen"),
                               "hold_gens": r.get("hold_gens"), "rung_at_general": r.get("rung_at_general")},
                "instr": len(m["genome"]) // 4, "persist": m["persist"], "n_regs": m["n_regs"],
                "heldout_by_rung_recorded": r.get("heldout_by_rung"),
                "heldout_measured_here": profile(m, r["seed"], LADDER + BEYOND),
            })

    # ---- 2. matched W0 solvers (same procedure as C3-SFE-04's harvest, more seeds)
    jobs = [{"seed": s, "N": a.N, "E": a.E, "G": a.harvest_G, "t0": time.time()} for s in range(1, a.w0_seeds + 1)]
    harvested = [harvest_w0(j) for j in jobs]
    w0 = []
    for h in harvested:
        if h["heldout"] < 0.9:
            continue
        m = h["manifest"]
        w0.append({
            "organism_id": hash_obj(m), "manifest": m,
            "provenance": {"experiment": "C3-SFE-04 harvest procedure (re-run here for a larger matched set)",
                           "cell_seed": 9000 + h["seed"], "harvest_seed": h["seed"], "solved_at_generation": h["gen"],
                           "campaign_seed": C3_SEED, "N": a.N, "E": a.E, "G": a.harvest_G},
            "instr": len(m["genome"]) // 4, "persist": m["persist"], "n_regs": m["n_regs"],
            "heldout_measured_here": profile(m, h["seed"], LADDER + BEYOND),
        })

    # ---- 3. shelf elites (C3-SFE-01 rows at level SHELF; the set C3-SFE-02 anatomised)
    shelf = []
    anatomised = {(r["source_arm"], r["source_seed"]) for r in rows("C3-SFE-02") if r.get("arm") == "shelf_org"}
    for r in sorted(rows("C3-SFE-01"), key=lambda r: (r["arm"], r["seed"])):
        if r.get("level") != "SHELF" or not r.get("final_elite_manifest"):
            continue
        m = r["final_elite_manifest"]
        shelf.append({
            "organism_id": hash_obj(m), "manifest": m,
            "provenance": {"experiment": "C3-SFE-01", "attempt_of_record": "a04", "arm": r["arm"], "seed": r["seed"],
                           "campaign_seed": C3_SEED, "first_shelf_gen": r.get("first_shelf_gen"),
                           "anatomised_in_C3_SFE_02": (r["arm"], r["seed"]) in anatomised},
            "instr": len(m["genome"]) // 4, "persist": m["persist"], "n_regs": m["n_regs"],
            "heldout_recorded": r.get("competence_heldout"), "heldout_per_ask_recorded": r.get("heldout_per_ask"),
            "heldout_measured_here": {"W2_K2": score(m, W2_K2, r["seed"])},
        })

    doc = {
        "_what_this_is": "Anatomy specimens for Proteus Round 2 / PROTEUS-37, answering comms #340.",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "generated_by": "Archaeon[m2-411504ab]",
        "identity": {
            "foundry_profile_id": "pfp1:625bc70456ebfa20",
            "archaeon_regime_id": "instr1-16:6528b9dc",
            "grammar_version": GRAMMAR_VERSION, "grammar_hash": GRAMMAR_HASH, "runtime_hash": RUNTIME_HASH,
            "campaign_seed_of_specimens": C3_SEED,
            "campaign_4_seed": 20260921,
        },
        "mate_policy": (
            "reproduce() draws the primary parent AND the mate by two INDEPENDENT tournaments of size 4 over the "
            "same scored generation; if the mate draw differs from the parent, descend() is called with mate=that "
            "organism, otherwise mate=None. The mate is used by exactly ONE operator, splice (mass 0.0521), which "
            "replaces a region of k instructions with a region of k' instructions copied from the mate; with mate=None "
            "splice copies from the organism itself. No other operator reads the mate. Origin tags of parent and mate "
            "are unioned onto the child. So: recombination happens in about 5% of births, and only as a region copy."
        ),
        "counts": {"delay_general": len(general), "w0_solver": len(w0), "shelf": len(shelf)},
        "notes": {
            "delay_general": "the campaign's only reproducible positive capability; d8/d16 columns are the invariance "
                             "claim, measured here, on cells these organisms never trained on",
            "w0_solver": "matched controls: W0-competent, measured (not assumed) on d8/d16",
            "shelf": "one-value memories; C3-SFE-02 found 1 improving child in 4,800 around these",
        },
        "specimens": {"delay_general": general, "w0_solver": w0, "shelf": shelf},
        "wall_s": round(time.time() - t0, 1),
    }
    OUT.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"counts": doc["counts"], "wall_s": doc["wall_s"],
                      "delay_general_d8_d16": [s["heldout_measured_here"]["W1_d8"] for s in general],
                      "w0_solver_d8": [s["heldout_measured_here"]["W1_d8"] for s in w0],
                      "w0_solver_W0": [s["heldout_measured_here"]["W0"] for s in w0],
                      "shelf_W2_K2": [s["heldout_measured_here"]["W2_K2"] for s in shelf]}, indent=1))
    print("written:", OUT, "sha256:", hashlib.sha256(OUT.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
