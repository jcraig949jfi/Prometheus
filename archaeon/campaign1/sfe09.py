"""SFE-09 -- REPRESENTATION UNLOCK through the live engine (campaign 1).

    python -m archaeon.campaign1.sfe09 [--seeds 1 2 3] [--N 200 --G 60 --E 16] [--dry-run]

A task where search is MEASURABLY STUCK under representation A: W1_d4 (K=1, D=1, delay 4,
4-bit) -- fresh search 0/3 footholds in SFE-03 (N=200 G=60), 0/3 in the v01 survey (8-bit,
N=200 G=100), 0/3 in SSF cycle 3 (N=512 G=200). Semantics and resource accounting are held
FIXED (the same Proteus VM executes every genome; ops, ticks and persistent words are
metered identically); only the REPRESENTATION the search operates in changes:
  A  raw words: Proteus's grammar over 32-bit words, opcode = word mod 25, operands = words
     mod n_regs, immediates = raw words (the baseline used everywhere in this program)
  B  fields: each instruction is decoded to (op in 0..24, a, b, c) and mutated FIELD-WISE --
     an op mutation draws a new opcode uniformly; a register field draws a register index;
     an immediate/offset field steps by a small signed delta; instruction insert/delete/
     duplicate at instruction granularity; crossover at instruction boundaries. Children are
     re-encoded canonically (op word = op; register words = index) so the VM runs the SAME
     instruction set with the same costs.
  C  fields + opcode-class-preserving mutation: an op mutation stays within the opcode's
     affordance class (halt_yield / read_write / indirection / arithmetic / logical /
     comparison / control / opaque_io / randomness) with probability 0.75.
Every arm: N=200 G=60 E=16, common random numbers, held-out on W1_d4 (48 episodes); the
reachable control cell W1_d1 runs under every representation too, so "B unlocks W1_d4" is
separable from "B is better everywhere". Engine: one world; representation descriptors as
artifacts; experiment + observation per (arm, cell, seed).
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry import generate as G                      # noqa: E402
from proteus.foundry.affordances import CATEGORY, N_OPCODES, OPCODES_IN, STORAGE_BOUNDS   # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH              # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from         # noqa: E402
from proteus.foundry.vm import validate_manifest               # noqa: E402

from archaeon import workspace as _ws                          # noqa: E402
from archaeon.wse.economics import REGIMES                     # noqa: E402
from archaeon.wse.evolve import evaluate, run_cell             # noqa: E402
from archaeon.wse.worlds import WorldSpec, episodes_for        # noqa: E402
from archaeon.campaign1.sfe01 import FOUNDRY_C1, CAMPAIGN_SEED, engine_client, sha   # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "SFE-09"
STUCK = WorldSpec("W1_d4", delay=4, value_bits=4)
CONTROL = WorldSpec("W1_d1", delay=1, value_bits=4)
ARMS = ["A_words", "B_fields", "C_fields_class"]
MASK32 = 0xFFFFFFFF
MASK62 = (1 << 62) - 1
IMM_OPS = {3}                      # LDC: word b is an immediate
JUMP_OPS = {18, 19, 20}            # JMP/JZ/JNZ: word b is a signed instruction offset


def decode(genome: List[int], n_regs: int) -> List[list]:
    ins = []
    for i in range(0, len(genome) - 3, 4):
        op = genome[i] % N_OPCODES
        ins.append([op, genome[i + 1] % n_regs, genome[i + 2], genome[i + 3]])
    return ins


def encode(ins: List[list], n_regs: int) -> List[int]:
    out = []
    for op, a, b, c in ins:
        if op in IMM_OPS or op in JUMP_OPS:
            out.extend([op, a % n_regs, b & MASK32, c % n_regs if op not in JUMP_OPS else 0])
        else:
            out.extend([op, a % n_regs, b % n_regs, c % n_regs])
    return out


def _signed_delta(rng: SplitMix64, x: int, span: int) -> int:
    d = rng.randint(-span, span)
    return (x + d) & MASK32


def make_field_descend(class_preserving: bool):
    def descend_fields(parent: dict, mutation_seed: int, mate=None):
        rng = SplitMix64(seed_from("cmp1.sfe09.fields", mutation_seed, parent["organism_id"], mate["organism_id"] if mate else ""))
        m = dict(parent["manifest"]); nr = m["n_regs"]
        ins = decode(m["genome"], nr)
        ops = []
        r = rng.unit()
        if mate is not None and r < 0.05 and len(ins) >= 1:                    # crossover at instruction boundaries
            mi = decode(mate["manifest"]["genome"], mate["manifest"]["n_regs"])
            cut = rng.randbelow(len(ins) + 1); cut2 = rng.randbelow(len(mi) + 1)
            ins = ins[:cut] + [[o, a % nr, b, c] for o, a, b, c in mi[cut2:]]
            ops.append({"operator": "field_crossover"})
        elif r < 0.13 and len(ins) < 64:
            pos = rng.randbelow(len(ins) + 1)
            ins.insert(pos, [rng.randbelow(N_OPCODES), rng.randbelow(nr), rng.randbelow(nr), rng.randbelow(nr)])
            ops.append({"operator": "field_insert"})
        elif r < 0.24 and len(ins) > 1:
            del ins[rng.randbelow(len(ins))]; ops.append({"operator": "field_delete"})
        elif r < 0.28 and len(ins) < 64:
            i = rng.randbelow(len(ins)); ins.insert(i, list(ins[i])); ops.append({"operator": "field_duplicate"})
        elif r < 0.36:                                                            # manifest limit step (same as the grammar's config_perturbation)
            key = ["persist", "tick_budget", "tape_words", "n_regs"][rng.randbelow(4)]
            if key == "persist":
                m["persist"] = ["none", "regs", "tape", "all"][rng.randbelow(4)]
            elif key == "tick_budget":
                m["tick_budget"] = [16, 64, 256][rng.randbelow(3)]
            elif key == "tape_words":
                ch = [t for t in (16, 32, 64, 128, 256) if t >= 4 * len(ins)]
                m["tape_words"] = ch[rng.randbelow(len(ch))] if ch else 256
            else:
                m["n_regs"] = max(2, min(16, m["n_regs"] + rng.randint(-2, 2))); nr = m["n_regs"]
            ops.append({"operator": "field_config", "key": key})
        else:
            i = rng.randbelow(len(ins)); f = rng.randbelow(4)
            op, a, b, c = ins[i]
            if f == 0:
                if class_preserving and rng.unit() < 0.75:
                    cls = OPCODES_IN[CATEGORY[op]]; op = cls[rng.randbelow(len(cls))]
                else:
                    op = rng.randbelow(N_OPCODES)
                ops.append({"operator": "field_op"})
            elif f == 1:
                a = rng.randbelow(nr); ops.append({"operator": "field_reg_a"})
            elif f == 2:
                b = _signed_delta(rng, b, 8) if (op in IMM_OPS or op in JUMP_OPS) else rng.randbelow(nr); ops.append({"operator": "field_b"})
            else:
                c = rng.randbelow(nr); ops.append({"operator": "field_reg_c"})
            ins[i] = [op, a, b, c]
        genome = encode(ins, nr)
        while len(genome) > m["tape_words"] or len(genome) > 4 * 64:
            genome = genome[:-4]
        if not genome:
            genome = [0, 0, 0, 0]
        m["genome"] = genome
        try:
            validate_manifest(m)
        except Exception:                                            # noqa: BLE001
            m = dict(parent["manifest"])
            ops.append({"operator": "field_invalid_reverted"})
        child = G.organism_record(m, parent["lineage_id"], parent["generation"] + 1)
        rec = {"organism_id": child["organism_id"], "parent_ids": [parent["organism_id"]] + ([mate["organism_id"]] if mate else []),
               "operators": ops, "generation": child["generation"]}
        return child, rec
    return descend_fields


def canonical_pop(N: int, seed: int) -> List[dict]:
    fm = dict(FOUNDRY_C1); fm["seed"] = seed_from("cmp1.sfe09.gen0", CAMPAIGN_SEED, seed) & MASK62; fm["n"] = N
    return G.generate(fm)


def run_arm(job: dict) -> dict:
    arm, cell, seed = job["arm"], job["cell"], job["seed"]
    spec = STUCK if cell == "stuck" else CONTROL
    fn = None if arm == "A_words" else make_field_descend(arm == "C_fields_class")
    init = canonical_pop(job["N"], seed)                                        # identical generation 0 for every arm
    t0 = time.time()
    res = run_cell(spec, REGIMES["E0"], CAMPAIGN_SEED, seed, N=job["N"], G_=job["G"], E=job["E"], init_pop=init, branch="cmp1-sfe09-common", rng_label="cmp1-sfe09-common",
                   foundry=FOUNDRY_C1, descend_fn=fn)
    ho = evaluate(res["elite"]["manifest"], episodes_for(spec, CAMPAIGN_SEED, "heldout", seed, 48), rng_seed=7)
    ops_hist: Dict[str, int] = {}
    for a in res["ancestry"]:
        for o in a["operators"]:
            ops_hist[o] = ops_hist.get(o, 0) + 1
    return {"arm": arm, "cell": cell, "seed": seed, "competence_heldout": ho["reward"], "train_last": res["elite_eval"]["reward"],
            "first_solved_gen": next((t["gen"] for t in res["trace"] if t["best_reward"] >= 0.5), None), "persist": ho["persist"],
            "ops_per_episode": ho["ops_per_episode"], "genome_instr": len(res["elite"]["manifest"]["genome"]) // 4,
            "trace_best": [t["best_reward"] for t in res["trace"]], "trace_mean": [t["mean_reward"] for t in res["trace"]],
            "ancestry_ops": ops_hist, "wall_s": round(time.time() - t0, 1)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--G", type=int, default=60)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--procs", type=int, default=18)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    ws = _ws.assert_not_canonical("run SFE-09")
    OUT.mkdir(parents=True, exist_ok=True)
    T = time.time()
    receipt: Dict = {"experiment": "SFE-09", "campaign_seed": CAMPAIGN_SEED, "workspace": ws, "runtime_hash": RUNTIME_HASH,
                     "engine_path": not a.dry_run, "timings": {}, "worlds": {}, "artifacts": {}, "errors": [],
                     "stuck_evidence": {"W1_d4 fresh footholds": {"SFE-03": "0/3 (N200 G60 4-bit)", "wse-survey-v01": "0/3 (N200 G100 8-bit)", "ssf-c3 ARM1": "0/3 (N512 G200 4-bit)"}},
                     "representations": {"A_words": "Proteus grammar over raw 32-bit words (opcode = word mod 25)",
                                         "B_fields": "instruction fields (op, a, b, c) mutated field-wise; canonical re-encoding; same VM",
                                         "C_fields_class": "B + opcode mutation stays in the affordance class with p=0.75"}}
    c = None
    if not a.dry_run:
        t0 = time.time(); c, _ = engine_client()
        sid = c.create_session("cmp1-sfe09")
        w = c.create_world(sid, "cmp1-sfe09-representation", sharing_policy="ISOLATED", seed_root=CAMPAIGN_SEED); c.start(w["world_id"]); wid = w["world_id"]
        receipt["worlds"]["rep"] = wid; receipt["session_id"] = sid
        receipt["hypothesis"] = c.hypothesis(wid, "Search on W1_d4 is stuck under the raw-word representation (0/3 in three prior campaigns); expressing the same "
                                                  "genomes in an instruction-field representation (same VM, same costs) unlocks it, and the unlock is not merely "
                                                  "a uniform speed-up (the reachable control cell W1_d1 separates the two).")
        rb = json.dumps(receipt["representations"] | {"stuck_evidence": receipt["stuck_evidence"]}, sort_keys=True).encode()
        receipt["artifacts"]["representations"] = c.artifact(wid, "cmp1.rep.descriptors.v0", rb, {"info_kind": "hypothesis"}, expected_blob_hash=sha(rb))["artifact_id"]
        receipt["timings"]["startup_s"] = round(time.time() - t0, 2)
    jobs = [{"arm": arm, "cell": cell, "seed": s, "N": a.N, "G": a.G, "E": a.E} for arm in ARMS for cell in ("stuck", "control") for s in a.seeds]
    t0 = time.time()
    with mp.Pool(processes=min(a.procs, len(jobs))) as pool:
        rows = pool.map(run_arm, jobs)
    receipt["timings"]["search_s"] = round(time.time() - t0, 1)
    if c is not None:
        t0 = time.time()
        for r in rows:
            try:
                exp = c.experiment(wid, {"experiment": "SFE-09", "arm": r["arm"], "cell": r["cell"], "seed": r["seed"], "N": a.N, "G": a.G, "E": a.E,
                                         "representation": receipt["representations"][r["arm"]]})
                obs = c.observation(wid, exp["exp_id"], {k: v for k, v in r.items() if k not in ("trace_best", "trace_mean")},
                                    "SURVIVED" if r["competence_heldout"] >= 0.5 else "FALSIFIED")
                r["engine"] = {"exp_id": exp["exp_id"], "obs_id": obs}
            except Exception as e:                                   # noqa: BLE001
                receipt["errors"].append({"step": "record", "arm": r["arm"], "cell": r["cell"], "seed": r["seed"], "error": repr(e)})
        receipt["timings"]["records_s"] = round(time.time() - t0, 2)
        t0 = time.time()
        try:
            c.terminate(wid); receipt["teardown"] = {"rep": c.get_world(wid).get("state")}
        except Exception as e:                                       # noqa: BLE001
            receipt["teardown"] = {"rep": "ERROR " + repr(e)}
        receipt["timings"]["teardown_s"] = round(time.time() - t0, 2)
    summ = {}
    for arm in ARMS:
        for cell in ("stuck", "control"):
            rs = [r for r in rows if r["arm"] == arm and r["cell"] == cell]
            summ["%s/%s" % (arm, cell)] = {"heldout": [round(r["competence_heldout"], 3) for r in rs], "footholds": sum(1 for r in rs if r["competence_heldout"] >= 0.5),
                                          "first_solved_gen": [r["first_solved_gen"] for r in rs], "ops": [round(r["ops_per_episode"]) for r in rs],
                                          "genome_instr": [r["genome_instr"] for r in rs]}
    receipt["summary"] = summ
    receipt["timings"]["total_s"] = round(time.time() - T, 1)
    (OUT / "rows.json").write_text(json.dumps(rows, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    (OUT / "RECEIPT.json").write_text(json.dumps(receipt, indent=1, sort_keys=True, default=str), encoding="utf-8", newline="\n")
    print(json.dumps({"summary": summ, "timings": receipt["timings"], "errors": receipt["errors"], "teardown": receipt.get("teardown")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
