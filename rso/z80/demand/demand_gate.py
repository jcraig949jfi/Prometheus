"""C-017-T020 demand gate: in a fixed Z80 Atlas world, does FUNCTIONAL HEREDITY matter? Read-only against archaeon/z80atlas.

Command (repo root, ONE process; PYTHONHASHSEED irrelevant, every RNG is SplitMix64):
    python -m rso.z80.demand.demand_gate rso/z80/demand/demand_result.json [seeds_per_arm] [epochs]
Defaults: 12 seeds per arm, 200 epochs, N = 128, G = 32, vmcopy, well_mixed, unlimited, fixed environment, task ECHO_forced.
SEEDS: 17_020_001 + 100*arm_index + k. Disjoint from rso/z80/smoke (16_021_xxx), C-016 re-runs (16_020_xxx / 16_030_xxx) and
from every small integer Archaeon registered (1, 2, 100..102, 2000..). No Archaeon run, seed or bundle file is read here.

FACTORIAL (planted starters x reproduction physics x pressure). Starters are transplanted into cells 0..12 of an otherwise
empty world through the engine's own `spec["transplant"]` path (the scheduler's constructor, scheduler.py:246-262), so the
engine stamps them transplanted_lineage; they are INSERTED ancestry by construction. The question of the demand gate is not
"did heredity emerge" (Archaeon: 0/80 de novo, census 9.6e-6) but "if function is planted, does the world keep it when it is
heritable, and does anything else keep it".
  H   heritable function : task_then_replicate(ECHO_forced)  (writes its own tape into the window, solves ECHO)
  NH  function only      : WITNESS[ECHO_forced]  (no copier: cannot cause a child)
  BR  broken copier      : H with the copy-loop offset byte zeroed (function intact, replication broken)
  NF  copier only        : the bare replicator (replicates, no ECHO function)
physics  ENDO = ENDOGENOUS_COPY,  EXT = EXTERNAL (grammar.matched_controls: the runner reproduces; heredity is not needed)
pressure GATED = competence_gated (reward couples to opportunity), IMPL = implicit_survival (no task reward)

ENDPOINT, re-derived from the final tapes (never from the engine's own `score`, `function`, or provenance fields):
  F  organism solves 8 fresh ECHO cases with a ZEROED neighbour (no environment contribution possible)
  C  organism, run with a zeroed neighbour, writes >= 0.9 of the window (engine criterion, engine.py ENDOGENOUS_COPY)
  D  F and C and generation >= GMIN (default 10): a functional copier whose function survived >= 10 transmissions;
     a planted founder has generation 0 so it cannot satisfy D by being planted
Unit of observation: the RUN (one run = one independent seed). Organisms within a run are lineage-dependent and are never
pooled as independent observations; per-run counts are the data.
Plus LOTTERY arms (random founders, no planted material) and an ACCESS probe (random founders, EXTERNAL, ECHO_forced).
"""
import json
import sys

from proteus.foundry.prng import SplitMix64
from archaeon.z80atlas import vm, tasks as T, grammar as GR
from archaeon.z80atlas import engine as E
from archaeon.z80atlas.grammar import FROZEN

G = 32
TASK = "ECHO_forced"
SEED0 = 17_020_001
N_CELLS_PLANTED = 13          # ~ 10% of 128 cells, the seeded_replicator share of the engine's own seeding
GMIN = 10
WORLD = {"topology": "well_mixed", "migration": "none", "resources": "unlimited", "env_dynamics": "fixed", "reservoir": False, "niches": 1}
REP = {"substrate": "vmcopy", "genome": G, "layout": "shared"}


def starters():
    H = T.pad(T.task_then_replicate(TASK, True), G)
    NH = T.pad(T.WITNESS[TASK], G)
    br = bytearray(H); br[bytes(H).index(bytes([0xFC]))] = 0x00
    NF = T.pad(T.replicator(True), G)
    return {"H": H, "NH": NH, "BR": bytes(br), "NF": NF}


def build_spec(starter, tape, phys, press, epochs, reason):
    pressure = ["competence_gated"] if press == "GATED" else ["implicit_survival"]
    reproduction = "ENDOGENOUS_COPY" if phys == "ENDO" else "EXTERNAL"
    s = GR.make(WORLD, REP, reproduction, pressure, TASK, "local_byte", "random", stage="early", reason=reason)
    s["budget"] = dict(s["budget"]); s["budget"]["max_epochs"] = epochs
    if tape is not None:
        s["transplant"] = {"from_run": None, "tapes": [tape.hex()] * N_CELLS_PLANTED}
        s["init"] = "transplanted_lineage"                 # the scheduler's relabel: the spec must not say "random"
        s["scheduler_reason"] = reason
        s["spec_id"] = GR.spec_id(s) + "-t"
    return s


def probe(tape, seed_parts):
    """Independent re-derivation from bytes. F: 8 fresh ECHO cases, zeroed neighbour. C: window fraction written, zeroed nbr."""
    zero = bytes(G)
    cs = T.cases(TASK, seed_parts, 8, 0)
    f = all(T.score_case(TASK, vm.execute(tape, zero, c, 256, True)["outputs"], c, {}) >= 1.0 for c in cs)
    r = vm.execute(tape, zero, cs[0], 256, True)
    c = sum(r["nbr_mask"][:G]) / G >= FROZEN["copy_min_frac"]
    return f, c, r["reads_nbr"], r["exec_foreign"]


def endpoint(res, seed):
    fp = res["final_population"]
    n = len(fp); nF = nC = nD = nFg = nFC = 0
    for k, o in enumerate(fp):
        tape = bytes.fromhex(o["tape"])
        f, c, rn, ef = probe(tape, ("demand_probe", seed, k))
        g = o["generation"]
        nF += f; nC += c; nFC += (f and c)
        nFg += (f and g >= GMIN)
        nD += (f and c and g >= GMIN)
    sg = res["signals"]
    return {"pop": n, "F": nF, "C": nC, "FC": nFC, "F_gen_ge_GMIN": nFg, "D": nD, "run_has_D": nD > 0,
            "births": sg["births"], "births_endo": sg["births_endo"], "epochs": sg["epochs"], "extinct": sg["extinct_epoch"],
            "max_gen": max((o["generation"] for o in fp), default=0),
            "integrity_births_equal": sg["births"] == sg["births_endo"] if "ENDO" in res.get("_phys", "") else None}


def arm_rows(name, spec, seeds):
    rows = []
    for sd in seeds:
        res = E.run(spec, sd)
        ep = endpoint(res, sd)
        ep["seed"] = sd
        rows.append(ep)
    return {"arm": name, "spec_id": spec["spec_id"], "reproduction": spec["reproduction"], "pressure": spec["pressure"], "n_runs": len(rows), "rows": rows}


def summarize(a):
    rows = a["rows"]
    k = len(rows)
    a["summary"] = {"runs_with_D": sum(r["run_has_D"] for r in rows), "runs_with_F": sum(r["F"] > 0 for r in rows),
                    "runs_with_F_gen_ge_GMIN": sum(r["F_gen_ge_GMIN"] > 0 for r in rows), "runs_extinct": sum(r["extinct"] is not None for r in rows),
                    "sum_pop": sum(r["pop"] for r in rows), "sum_F": sum(r["F"] for r in rows), "sum_C": sum(r["C"] for r in rows),
                    "sum_FC": sum(r["FC"] for r in rows), "sum_D": sum(r["D"] for r in rows), "sum_births_endo": sum(r["births_endo"] for r in rows),
                    "n_runs": k}
    return a


def main(out, n_seeds=12, epochs=200):
    st = starters()
    arms = []
    idx = 0
    for sname in ("H", "NH", "BR", "NF"):
        for phys in ("ENDO", "EXT"):
            for press in ("GATED", "IMPL"):
                name = "%s_%s_%s" % (sname, phys, press)
                spec = build_spec(sname, st[sname], phys, press, epochs, "demand:" + name)
                seeds = [SEED0 + 100 * idx + k for k in range(n_seeds)]
                arms.append(summarize(arm_rows(name, spec, seeds)))
                s = arms[-1]["summary"]
                print(name, {k: v for k, v in s.items()}, flush=True)
                idx += 1
                dump(out, arms, epochs)
    # LOTTERY: random founders, no planted material (the control the engine needs and the Observatory must not drop)
    for phys in ("ENDO", "EXT"):
        name = "RANDOM_%s_GATED" % phys
        spec = build_spec("R", None, phys, "GATED", epochs, "demand:" + name)
        seeds = [SEED0 + 100 * idx + k for k in range(max(n_seeds, 24))]
        arms.append(summarize(arm_rows(name, spec, seeds)))
        print(name, arms[-1]["summary"], flush=True)
        idx += 1
    dump(out, arms, epochs)


def dump(out, arms, epochs):
    json.dump({"schema": "rso.z80.demand.v1", "G": G, "task": TASK, "gmin": GMIN, "epochs": epochs, "n_planted_cells": N_CELLS_PLANTED,
               "seed0": SEED0, "grammar_digest": GR.digest(), "arms": arms}, open(out, "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 12, int(sys.argv[3]) if len(sys.argv) > 3 else 200)
