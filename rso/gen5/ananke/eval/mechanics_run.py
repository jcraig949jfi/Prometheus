"""Rung-4 attribution mechanics exercised on the plants, each with a known outcome where one exists (item 3).

    python -m rso.gen5.ananke.eval.mechanics_run run --part gate0|gate1|flip0 --out DIR     (resumable JSONL)
    python -m rso.gen5.ananke.eval.mechanics_run reduce DIR OUT.json                       (exit 1 on a failed KNOWN)

Subjects: gate_plant at FLIP-0000 and FLIP-0004 (GATE), P_FLIP at FLIP-0000 (FLIP); R4 physics; 64 fresh worlds per
subject from this packet's own namespace (evaluate.own_seeds(0x4E40, cell_key)). The module split is the owner's D-LIB
split (CONTEXT = plant lines 11-13, CUE = 0-10 and 14; build_dlib.py:4-5).

Labels: KNOWN = the outcome follows from the program and the world by construction (the reason is in `why`), so a
different reading is an evaluator defect; MEASURED = recorded, no expectation; DESCRIPTIVE = recorded, a sample.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

from . import evaluate as E
from . import ka_table as KT
from . import mechanics as K
from . import owner, ruler, worlds

CTX = [11, 12, 13]
CUE = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 14]
PLANT = CTX + CUE
PARTS = {"gate0": (0, "GATE"), "gate1": (1, "GATE"), "flip0": (0, "FLIP")}
SEED_PURPOSE = 0x4E40
N_WORLDS = 64                      # KNOWN outcomes here are structural (exact chance or identity); 64 worlds = 32 pairs
N_RECIPIENTS = 4


def _hold_module_size(lib, n):
    return next(m for m in lib if len(m["lines"]) == n)


def interventions(part, cells, adm, lib):
    ci, task = PARTS[part]
    c = cells[ci]; cid = c["cell_id"]
    ph = worlds.rep_physics(c["physics"], "R4"); env = worlds.task_env(c["env"], task)
    L = E.register_layout(ph)
    g = np.asarray(adm[f"{cid}|{task}"]["plant_genome"], dtype=np.int64)
    I = []

    def add(iid, label, expect, why, genome, **kw):
        I.append(dict(iid=iid, label=label, expect=expect, why=why, genome=genome, kw=kw))
    if task == "GATE":
        add("baseline", "KNOWN", "TRUE", "the admitted plant on fresh worlds", g)
        add("nop_ctx", "KNOWN", "FALSE", "S2 is never written, so S0 = S1*S2 = 0: every readout .5", K.lines_nop(g, CTX))
        add("nop_cue", "KNOWN", "FALSE", "S0 is never written: every readout .5", K.lines_nop(g, CUE))
        add("use_disabled_ctx", "KNOWN", "FALSE",
            "context-half bytes kept and executed, writes go to the dead O.chan: S2 never written", K.use_disabled(g, CTX, ph)[0])
        add("use_disabled_cue", "KNOWN", "FALSE",
            "cue-half bytes kept and executed, writes go to O.chan: no emission, S0 never written", K.use_disabled(g, CUE, ph)[0])
        add("use_disabled_both", "KNOWN", "FALSE", "every plant line kept but use-disabled", K.use_disabled(g, PLANT, ph)[0])
        add("substitute_ctx_self", "KNOWN", "IDENTICAL", "substitution machinery with the module itself is a no-op",
            K.substitute(g, CTX, g[0, CTX]))
        add("substitute_ctx_lesioned", "KNOWN", "FALSE",
            "size-matched incompatible module: the context half reading ZERO instead of SENSE latches nothing",
            K.substitute(g, CTX, K.lesion_input(g[0, CTX], ph, L["SENSE"])))
        les = K.lesion_input(K.lesion_input(g[0, CUE], ph, L["SENSE"]), ph, L["NW"])          # IN0_0 = index NW
        add("substitute_cue_lesioned", "KNOWN", "FALSE",
            "size-matched incompatible module: the cue half reading ZERO instead of SENSE and IN0_0 relays nothing",
            K.substitute(g, CUE, les))
        hm = _hold_module_size(lib, 3)
        add("substitute_ctx_evolved_hold3", "MEASURED", None,
            f"size-matched evolved module: LIBRARY_C4 id {hm['id']} ({hm['task']}, {hm['cell_id']}, 3 lines), identity naming",
            K.substitute(g, CTX, hm["lines"]))
        # Position-free only if no line reads its own index (RAND draws H(..., i); WIMM / SETRULE) AND in-lifetime site
        # mutation is off (DESIGN s6 step 8 perturbs Kp at a hashed INSTRUCTION INDEX). CORRECTION 2026-10-15: the first
        # reduce asserted this in `why` without checking it and failed at FLIP-0004 (mut_site .001, wimm 1); preserved in
        # qual/MECHANICS_KA_first_reduce_FAIL.json. The precondition is now computed from the physics.
        pos_free = float(ph["mut_site"]) == 0 and not any(int(op) % 16 in (13, 14, 15) for op in g[0, :, 0])
        if pos_free:
            add("transplant_offset9", "KNOWN", "IDENTICAL",
                "position-free here: mut_site 0 and no RAND/SETRULE/WIMM line (checked from the physics)",
                K.transplant(g[0, :15], ph, 9))
        else:
            add("transplant_offset9", "MEASURED", None,
                f"NOT position-free: mut_site {ph['mut_site']} perturbs Kp at a hashed instruction index, so moving lines "
                "changes which constants are perturbed", K.transplant(g[0, :15], ph, 9))
        add("transplant_rename_S1S2", "KNOWN", "IDENTICAL", "consistent renaming of every line, readout register fixed",
            K.transplant(K.rename_state(g[0, :15], ph, [0, 2, 1]), ph, 0))
        add("transplant_rename_S0S1", "KNOWN", "FALSE",
            "renaming moves the product out of S0: the readout is the relayed cue alone, chance against y = c*x",
            K.transplant(K.rename_state(g[0, :15], ph, [1, 0, 2]), ph, 0))
        rng = np.random.default_rng(E.H(E.OWN_NS, 0x7E, c["cell_key"]))
        for k in range(N_RECIPIENTS):
            bg = np.zeros_like(g)
            bg[0, :16, 0] = rng.integers(0, 256, 16); bg[0, :16, 1:4] = rng.integers(0, 256, (16, 3))
            bg[0, :16, 4] = rng.integers(-128, 128, 16)
            add(f"transplant_random_bg{k}", "DESCRIPTIVE", None,
                "plant lines 0-14 written over lines 9-23 of a fresh R4-style random genome (9 random lines stay before it)",
                K.transplant(g[0, :15], ph, 9, background=bg))
        add("reg_zero_S2", "KNOWN", "FALSE", "owner's known answer (PREREG_PTE_C4 s6): the context lives in S2", g,
            after_tick=K.reg_zero(2))
        add("reg_zero_S0", "MEASURED", None, "S0 forced to 0 after each tick (after the readout is recorded)", g,
            after_tick=K.reg_zero(0))
        add("reg_zero_S1", "MEASURED", None, "S1 (cue latch) forced to 0 after each tick", g, after_tick=K.reg_zero(1))
        add("zero_comm", "KNOWN", "FALSE", "the cue sensor is d >= 1 hops away: without packets the actuator never sees it", g,
            zero_comm=True)
        add("context_off_all", "KNOWN", "FALSE", "no context ever arrives: S2 stays 0", g, sval_edit=K.context_off_all)
        add("context_off_after_block0", "MEASURED", None, "context only in block 0 (assay_candidates.py:72-73)", g,
            sval_edit=K.context_off_after_block0(env))
    else:
        add("baseline", "KNOWN", "TRUE", "the admitted P_FLIP plant on fresh worlds", g)
        add("zero_comm", "KNOWN", "FALSE", "without packets the readout cannot depend on the cue: B at chance", g, zero_comm=True)
        live = [i for i in range(g.shape[1]) if int(g[0, i, 0]) % 16]
        add("use_disabled_all", "KNOWN", "FALSE", "every non-NOP line kept and executed, all writes to O.chan: S0 never set",
            K.use_disabled(g, live, ph)[0])
        add("teacher_off", "MEASURED", None, "teacher only on trial 0 (c2a_common.teacher_off)", g,
            sval_edit=K.teacher_off(env))
        for i in range(3):
            add(f"reg_zero_S{i}", "MEASURED", None, f"S{i} forced to 0 after each tick", g, after_tick=K.reg_zero(i))
    return c, ph, env, task, g, I


def run_part(part, out_dir):
    cells, adm, lib = owner.cells(), owner.admission(), owner.library()
    c, ph, env, task, g, I = interventions(part, cells, adm, lib)
    seeds = E.own_seeds(SEED_PURPOSE, c["cell_key"], N_WORLDS)
    path = os.path.join(out_dir, f"mech_rows_{part}.jsonl")
    os.makedirs(out_dir, exist_ok=True)
    done = {json.loads(l)["iid"] for l in open(path)} if os.path.exists(path) else set()
    print(f"pid {os.getpid()} part {part}: {len(I) - len(done)} to run", flush=True)
    for it in I:
        if it["iid"] in done:
            continue
        t0 = time.time()
        pt, ep = E.eval_programs(ph, env, seeds, [it["genome"]], **it["kw"])
        r = ruler.competence(worlds.ROLE[task], pt[0], ep)
        row = {"part": part, "cell_id": c["cell_id"], "task": task, "iid": it["iid"], "label": it["label"],
               "expect": it["expect"], "why": it["why"], "status": r["status"], "ruler": E.slim(r),
               "genome": np.asarray(it["genome"]).tolist(), "pt": KT.encode_pt(pt[0]), "pt_sha": KT._sha(pt[0]),
               "worlds": len(seeds), "sec": round(time.time() - t0, 2)}
        with open(path, "a", newline="\n") as f:
            f.write(json.dumps(row) + "\n")
        print(it["iid"], r["status"], row["sec"], flush=True)
    print("DONE", flush=True)


def reduce(out_dir, out_json):
    rows = []
    for fn in sorted(os.listdir(out_dir)):
        if fn.startswith("mech_rows_"):
            rows += [json.loads(l) for l in open(os.path.join(out_dir, fn)) if l.strip()]
    cells, adm, lib = owner.cells(), owner.admission(), owner.library()
    base = {r["part"]: KT.decode_pt(r["pt"]) for r in rows if r["iid"] == "baseline"}
    problems, table = [], []
    planned = {(p, it["iid"]): it for p in PARTS for it in interventions(p, cells, adm, lib)[5]}
    seen = set()
    for r in rows:
        key = (r["part"], r["iid"])
        if key in seen:
            problems.append(f"DUPLICATE {key}"); continue
        seen.add(key)
        it = planned.get(key)
        if it is None:
            problems.append(f"UNPLANNED {key}"); continue
        if not np.array_equal(np.asarray(r["genome"]), np.asarray(it["genome"])):
            problems.append(f"{key}: row genome differs from the planned intervention")
        pt = KT.decode_pt(r["pt"])
        c = cells[PARTS[r["part"]][0]]
        ph = worlds.rep_physics(c["physics"], "R4"); env = worlds.task_env(c["env"], r["task"])
        ep = worlds.build(ph, env, E.own_seeds(SEED_PURPOSE, c["cell_key"], N_WORLDS))
        if it.get("kw", {}).get("sval_edit") is not None:
            pass                                    # the ruler only needs the unedited cue signs and scoring mask
        st = ruler.competence(worlds.ROLE[r["task"]], pt, ep)["status"]
        ident = bool(r["part"] in base and np.array_equal(pt, base[r["part"]]))
        if st != r["status"]:
            problems.append(f"{key}: row status {r['status']} != recomputed {st}")
        ok = None
        if it["label"] == "KNOWN":
            ok = ident if it["expect"] == "IDENTICAL" else (st == it["expect"])
            if not ok:
                problems.append(f"{key}: KNOWN outcome {it['expect']} not met (status {st}, identical {ident})")
        table.append({"part": r["part"], "cell_id": r["cell_id"], "task": r["task"], "iid": r["iid"], "label": it["label"],
                      "expect": it["expect"], "status": st, "identical_to_baseline": ident, "pass": ok,
                      "mean_all": r["ruler"].get("all", {}).get("mean"), "B_mean": r["ruler"].get("B", {}).get("mean"),
                      "why": it["why"]})
    problems += [f"MISSING {k}" for k in planned if k not in seen]
    res = {"schema": "argus.c019t040.mechanics.v1", "owner_sha": owner.OWNER_SHA, "verdict": "PASS" if not problems else "FAIL",
           "problems": problems, "n_known": sum(1 for t in table if t["label"] == "KNOWN"),
           "n_known_pass": sum(1 for t in table if t["pass"]), "table": table}
    with open(out_json, "w", newline="\n") as f:
        json.dump(res, f, indent=1)
    print(res["verdict"], res["n_known_pass"], "/", res["n_known"], "KNOWN;", len(problems), "problems")
    for p in problems:
        print("  ", p)
    return 0 if not problems else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("run"); a.add_argument("--part", required=True, choices=sorted(PARTS)); a.add_argument("--out", required=True)
    b = sp.add_parser("reduce"); b.add_argument("dir"); b.add_argument("out")
    x = ap.parse_args(argv)
    return run_part(x.part, x.out) if x.cmd == "run" else reduce(x.dir, x.out)


if __name__ == "__main__":
    sys.exit(main())
