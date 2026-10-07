"""C-010-T034 W2 short re-check on FREEZE_W2: fixtures and constructions (Pallas, Q3). DATA FILE: frozen at the set
commit; the driver (run_w2.py) may be repaired afterwards, this file may not.

Reuses the frozen W1 builders (rso/witness/challenge/W1/cases.py: seeds >= 5,000,000, synthetic traces with known
decisions, the hand-wired leak construction, the driver's bundle layout) WITHOUT editing them. W1's full_plan runs
P-OBS on a prefix of the witness list, which FREEZE_W2 (R2: "every witness seed") now refuses, so the registered node
set is rebuilt here with P-OBS on the full list.

HARD GATE (TASK.json non_goals; PREREGISTRATION s10): no registered subject configuration is run, no registered arm
runs on a registered seed, make_configs is never invoked, no ares/ source and no PREREGISTRATION.md edit. Organisms
are the hand-wired leak construction, the POS carrier, one random P = 1 population and synthetic action arrays.
Numeric outcomes of registered-arm constructions are never committed.
"""
import hashlib
import json
import os
import subprocess
import sys
import time

import numpy as np

from ares import substrate as S
from rso.witness import ares_client as AC
from rso.witness import run_witness as RW
from rso.witness.challenge.W1 import cases as C
from rso.witness.tests.test_ares_client import _leak_construction

T = C.T
DA, DB = C.DA, C.DB
SUBJECTS = C.SUBJECTS
FIRST_CHECK = C.FIRST_CHECK
LAUNCH_X, LAUNCH_Y = "w2-launch-x", "w2-launch-y"
KILL_AFTER_S = 25.0            # S1: the first SA launch is killed this long after it starts (a FAILED launch, s10)
SHORT_ROWS = 1                 # B1: the pair-gate action arrays cover this many episodes / probes / pairs


def seed_lists():
    """The SEED_LISTS.json 'seeds' object the repaired evaluator requires (R2), on this set's non-registered ranges
    and the registered SHAPES (witness alternating r; erase (0, 1, alt); pres (opposite, alt))."""
    return {"witness": C.witness_like(), "erase": C.flat(C.erase_like()), "pres": C.flat(C.pres_like())}


# --------------------------------------------------------------------------------------------------------
# Synthetic node set with P-OBS on every witness seed (R2 as frozen in W2)

def obs_node_rows(digest, seeds, n_rows, differs=False):
    """A P-OBS receipt declaring `seeds` (with the full world oracle) whose two action arrays cover only n_rows
    episodes. n_rows == len(seeds) is the honest shape."""
    regs, steps = C.oracle(seeds)
    a = np.ones((n_rows, T, 1), dtype=np.int8)
    b = a.copy()
    if differs:
        b[0, 3, 0] = 2
    outs = [C.array_artifact("trace:actions_record", a), C.array_artifact("trace:actions_norecord", b)]
    orc = [C.array_artifact("oracle:regimes", np.array(regs, dtype=np.int8)),
           C.json_artifact("oracle:reset_steps", steps)]
    return C.receipt(digest, "S", "P-OBS", seeds, "present", outs, orc), outs + orc


def full_plan(spec=None, override=None):
    """[(receipt, arts)] for the registered node map (evaluate.SUBJECT_NODES + SHARED_NODES), P-OBS on the FULL
    witness list. override maps (digest, arm, predicate) -> (receipt, arts)."""
    spec = spec or C.Spec()
    override = override or {}
    seeds = C.witness_like()
    erase, pres = C.erase_like(), C.pres_like()
    nodes = []

    def put(d, arm, pred, build):
        nodes.append(override.get((d, arm, pred)) or build())

    for d in (DA, DB):
        put(d, "S", "P-RET", lambda: C.ret_node(d, "S", "P-RET", spec.ret[d], seeds))
        put(d, "S-NOPL", "P-CHAN", lambda: C.ret_node(d, "S-NOPL", "P-CHAN", spec.nopl[d], seeds))
        put(d, "S", "P-OBS", lambda: obs_node_rows(d, seeds, len(seeds)))
        put(d, "S", "P-PRES", lambda: C.pair_node(d, "S", "P-PRES", C.PRES_ROLES, pres, *C.pair_arrays(len(pres), False)))
        put(d, "S", "P-ERASE", lambda: C.pair_node(d, "S", "P-ERASE", C.ERASE_ROLES, erase, *C.pair_arrays(len(erase), False)))
        put(d, "S-LEAK", "P-ERASE", lambda: C.pair_node(d, "S-LEAK", "P-ERASE", C.ERASE_ROLES, erase, *C.pair_arrays(len(erase), True)))
    nodes.append(C.ret_node(DA, "NULL", "P-CAL", spec.null, seeds))
    nodes.append(C.ret_node(DA, "SHUF", "P-CAL", spec.shuf, seeds, mode="shuffled"))
    nodes.append(C.ret_node(DA, "POS", "P-CAL", spec.pos, seeds))
    return nodes


# --------------------------------------------------------------------------------------------------------
# B1 (broken): pair-gate evidence shorter than the registered list it declares

def build_b1a(root):
    """DA's four pair-gate nodes (S/P-OBS, S/P-PRES, S/P-ERASE, S-LEAK/P-ERASE) declare the full registered-shape
    lists and carry the full world oracle for them (so R2 and R3 are satisfied), but their action arrays cover
    SHORT_ROWS episodes / probes / pairs: P-OBS equal, P-PRES equal, S/P-ERASE equal, S-LEAK/P-ERASE differing."""
    seeds, erase, pres = C.witness_like(), C.erase_like(), C.pres_like()
    n = SHORT_ROWS
    ov = {(DA, "S", "P-OBS"): obs_node_rows(DA, seeds, n),
          (DA, "S", "P-PRES"): C.pair_node(DA, "S", "P-PRES", C.PRES_ROLES, pres, *C.pair_arrays(n, False)),
          (DA, "S", "P-ERASE"): C.pair_node(DA, "S", "P-ERASE", C.ERASE_ROLES, erase, *C.pair_arrays(n, False)),
          (DA, "S-LEAK", "P-ERASE"): C.pair_node(DA, "S-LEAK", "P-ERASE", C.ERASE_ROLES, erase, *C.pair_arrays(n, True))}
    man, inv = C.write_bundle(root, full_plan(override=ov), launch=LAUNCH_X)
    return {"roots": [root], "store": C.keeper((man, inv)), "rows_per_array": n,
            "declared": {"witness": len(seeds), "erase_triples": len(erase), "pres_pairs": len(pres)}}


def build_b1b(root):
    """Control (the ruler path): DA's S/P-RET node declares the full witness list (full oracle) but its trace covers
    SHORT_ROWS episodes. evaluate.episodes pins trace:actions to (len(seeds), 40, 1)."""
    seeds = C.witness_like()
    regs, steps = C.oracle(seeds)
    acts = C.after_last([r + 1 for r in regs[:SHORT_ROWS]], steps[:SHORT_ROWS])
    outs = [C.array_artifact("trace:actions", acts)]
    orc = [C.array_artifact("oracle:regimes", np.array(regs, dtype=np.int8)), C.json_artifact("oracle:reset_steps", steps)]
    rec = C.receipt(DA, "S", "P-RET", seeds, "present", outs, orc)
    man, inv = C.write_bundle(root, full_plan(override={(DA, "S", "P-RET"): (rec, outs + orc)}), launch=LAUNCH_X)
    return {"roots": [root], "store": C.keeper((man, inv)), "rows_per_array": SHORT_ROWS}


# --------------------------------------------------------------------------------------------------------
# E1 witness fixture: a clean bundle and a REFUSED bundle presenting the same node ids

def build_e1(root):
    """X: a clean bundle (DA POSITIVE by construction); Y: the same node ids under another launch with DA constant
    (NEGATIVE), NOT registered with the keeper, so Y is refused (CUSTODY_UNQUALIFIED). The store holds X only."""
    rx, ry = os.path.join(root, "X"), os.path.join(root, "Y")
    mx, ix = C.write_bundle(rx, full_plan(), launch=LAUNCH_X)
    C.write_bundle(ry, full_plan(C.Spec(ret={DA: C.const(1), DB: C.const(1)})), launch=LAUNCH_Y)
    return {"X": rx, "Y": ry, "store": C.keeper((mx, ix))}


# --------------------------------------------------------------------------------------------------------
# S1 (sound): the real driver; one launch FAILED by a kill mid-way, re-run with identical inputs (s10), both presented

def driver_configs(root):
    """Two canonical genome files (SA: the hand-wired leak construction; SB: a random P = 1 population) and the three
    launch configs make_configs would write, on this set's seeds, P-OBS on the FULL witness list."""
    subs = {"SA": _leak_construction(), "SB": S.random_population(S.Config(), 1, np.random.default_rng(7))}
    cfgdir = os.path.join(root, "configs")
    os.makedirs(cfgdir)
    files, digests = {}, {}
    for name, pop in subs.items():
        data = RW.genome_bytes(pop.genome(0))
        files[name] = name + ".json"
        digests[name] = hashlib.sha256(data).hexdigest()
        RW._write(os.path.join(cfgdir, files[name]), data)
    wit, erase, pres = C.witness_like(), C.flat(C.erase_like()), C.flat(C.pres_like())
    nodes = {"CONTROLS": [{"subject": files["SA"], "arm": a, "predicate": p, "seeds": wit}
                          for a, p in (("POS", "P-CAL"), ("NULL", "P-CAL"), ("SHUF", "P-CAL"), ("RECUR", "REPORT"))]}
    for name in ("SA", "SB"):
        nodes[name] = [{"subject": files[name], "arm": a, "predicate": p, "seeds": sd} for a, p, sd in (
            ("S", "P-RET", wit), ("S-NOPL", "P-CHAN", wit), ("S", "P-OBS", wit), ("S", "P-ERASE", erase),
            ("S-LEAK", "P-ERASE", erase), ("S", "P-PRES", pres))]
    paths = {}
    for label, entries in nodes.items():
        cfg = {"schema": RW.CONFIG_SCHEMA, "label": "W2-" + label, "world": "W15", "entries": entries}
        paths[label] = os.path.join(cfgdir, "config_%s.json" % label)
        RW._write(paths[label], (json.dumps(cfg, sort_keys=True, indent=1) + "\n").encode("ascii"))
    return paths, digests


_CHILD = r'''
import json, sys
job = json.loads(sys.stdin.read())
sys.path.insert(0, job["root"])
sys.dont_write_bytecode = True
from rso.slice001 import ledger as L
from rso.witness import run_witness as RW
led = L.Ledger.from_contract(job["ledger"], job["contract"])
RW.launch(job["config"], led, job["out"], code_commit=job["commit"], launch_run_id=job["launch_run_id"])
'''


def killed_launch(root, config, ledger, contract, out, commit, launch_run_id, kill_after_s=KILL_AFTER_S):
    """Run the frozen driver's launch in a child process and KILL it kill_after_s seconds after it starts: a launch
    that failed mid-way for a reason outside its inputs (the s10 case). Returns what the bundle directory and the
    temp ledger hold afterwards (structure only; no receipt content)."""
    job = json.dumps({"root": root, "ledger": ledger, "contract": contract, "config": config, "out": out,
                      "commit": commit, "launch_run_id": launch_run_id})
    t0 = time.perf_counter()
    p = subprocess.Popen([sys.executable, "-B", "-c", _CHILD], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, universal_newlines=True, cwd=root)
    try:
        _o, errs = p.communicate(job, timeout=kill_after_s)
        killed = False
    except subprocess.TimeoutExpired:
        p.kill()
        _o, errs = p.communicate()
        killed = True
    wall = time.perf_counter() - t0
    files = []
    if os.path.isdir(out):
        for d, _s, fs in os.walk(out):
            files.extend(os.path.relpath(os.path.join(d, f), out).replace(os.sep, "/") for f in fs)
    files.sort()
    rows = []
    if os.path.isfile(ledger):
        with open(ledger, encoding="utf-8") as f:
            rows = [json.loads(ln) for ln in f if ln.strip()]
    mine = [r for r in rows if r.get("run_id") == launch_run_id or r.get("parent_run_id") == launch_run_id]
    return {"killed": killed, "exit_code": p.returncode, "wall_s": round(wall, 1),
            "receipts_written": len([f for f in files if f.startswith("receipts/")]),
            "artifacts_written": len([f for f in files if f.startswith("artifacts/")]),
            "has_manifest": "MANIFEST.json" in files, "has_inventory": "inventory.json" in files,
            "has_run_json": "run.json" in files,
            "ledger_rows_of_launch": [{"kind": r.get("kind"), "launch_kind": r.get("launch_kind"),
                                       "status": r.get("status"), "is_top": r.get("run_id") == launch_run_id}
                                      for r in mine],
            "stderr_tail": (errs or "").strip().splitlines()[-1:]}


def null_arm_structure():
    """R5 by construction on the plastic POS carrier: state facts only (no action, count or accuracy)."""
    pop = AC.pos_carrier()
    q, mode, cls = AC.arm("NULL", pop)
    rt = cls(q)
    AC.run_episodes(q, AC.world("W15", mode), C.witness_like()[:4], runtime=rt)
    nopl, _m, _c = AC.arm("S-NOPL", pop)
    return {"mode": mode, "reset_each_step": bool(q.cfg.reset_each_step), "runtime_plastic_flag": bool(rt.plastic),
            "R_all_zero": bool(not np.any(q.R)), "R_equals_s_nopl_R": bool(np.array_equal(q.R, nopl.R)),
            "w1_written_during_4_episodes": bool(not np.array_equal(rt.W1, q.W1)),
            "subject_R_untouched": bool(np.any(pop.R)), "subject_reset_each_step": bool(pop.cfg.reset_each_step)}


def controls_receipt_facts(bundle, sa_digest):
    """R4 / R5 facts from the CONTROLS bundle's receipts: identity fields only."""
    with open(os.path.join(bundle, "MANIFEST.json"), encoding="utf-8") as f:
        man = json.load(f)
    out = {}
    for n in man["nodes"]:
        with open(os.path.join(bundle, n["receipt_file"]), encoding="utf-8") as f:
            rec = json.load(f)
        out[rec["arm"]] = {
            "subject_is_SA": rec["subject"]["genome_sha256"] == sa_digest,
            "arm_genome_differs_from_subject": rec["subject"]["arm_genome_sha256"] != rec["subject"]["genome_sha256"],
            "node_id_rebuilt_equal": AC.node_id(rec["subject"]["genome_sha256"], rec["arm"], rec["predicate"],
                                                rec["world"]["name"]) == rec["node_id"],
            "n_seeds": len(rec["seeds"]), "mode": rec["world"]["mode"]}
    return out
