"""E2 PRODUCTION DRIVER (Beta-04, C-015): the reachability screen and atlas exactly as E2_E3KP_PREREG.md AMENDMENT A1-B.

Run from roles/Aphrodite/beta04 with OMP_NUM_THREADS=1. Every mode is resumable: work is cut into SHARDS, each shard
writes one result file atomically, and a re-run skips shards whose result file exists. Results are deterministic
functions of (code, root files, shard id), never of scheduling or worker count.

  python -m atlas.e2_driver qualify   [--root R] [--out O] [--workers 2]          (outcome-free D-BEH, INFRA)
  python -m atlas.e2_project --timing runs/e2_timing_pilot_v2/TIMING_RAW.json --out O   (projection + truncation)
  python -m atlas.e2_driver plan      [--root R] [--out O] [--seeds 8] [--drop-chain-strict] [--drop-desert-ref]
  python -m atlas.e2_driver prelaunch [--root R] [--out O] [--workers 2]          -> <out>/../E2_PRELAUNCH.json
  python -m atlas.e2_driver atlas     [--root R] [--out O] [--workers 2]          (all admitted families)
  python -m atlas.e2_driver screen    [--root R] [--out O] [--workers 2]          (qual -> kcal -> runs)
  python -m atlas.e2_driver status    [--root R] [--out O]
  python -m atlas.e2_driver timing    --root foundry/pilot_v2 --out runs/e2_timing_pilot_v2   (EXPOSED families only)
  python -m atlas.e2_analyze          [--root R] [--out O]                        (after the screen completes)

Defaults: --root foundry/production, --out runs/e2.  `plan` freezes the shard list (PLAN.json) and is required before
`screen`; it is where a pre-registered TRUNCATION (A1-B.10) is recorded.

A1-B mapped to code
-------------------
Families (A1-B.3)  screen: the admitted R3 / R4 families (WORLD_MANIFEST id_map status ADMITTED); atlas: every
                   admitted family (R2 + R3 + R4).
Library (A1-B.1)   for every arm except desert_ref: the family's constituent mechanisms (sealed `mechanisms_used`;
                   the oracle decomposition the prereg names) as the FOUNDRY-ACQUIRED primitives (WORLD_MANIFEST
                   acquired_library.acquired[m].term: learner-found by the foundry's chain_c, NOT the sealed terms),
                   promoted with tfs1 Library(closed_args=True).promote_lambda. Ledgered as supplied DEVELOPMENTAL
                   context. desert_ref: no library.
Arms (A1-B.2)      credit_blind  = atlas arm D1-chain_neutral with credit="none"
                   chain_strict  = D1-chain_strict (accept iff f(child) > f(parent))
                   chain_neutral = D1-chain_neutral (accept iff f(child) >= f(parent))
                   D1-X3         = D1-X3 guided by D-BEH (worse-into-new-cell)
                   X3G           = D1-X3G (RAND:K genotype-hash cells); K calibrated OUTCOME-BLIND to D1-X3's realised
                                   cell count (arms.calibrate_random_k: seeds 1000-1002, no certifier, full budget,
                                   the same max_size); restore frequency equal by construction (L = 1, one restore per
                                   charged child, both arms)
                   desert_ref    = D1-chain_neutral, credit="none", NO library
                   D1-X3 / X3G run only where D-BEH QUALIFIED (C-013 R1 procedure, descriptors.qualify, computed
                   outcome-free on the family's witness rewritten under the library); otherwise each of their shards
                   writes status INSTRUMENT_UNVALIDATED and nothing is run.
Search params      budget B = 2e5 charges, 8 CRN seeds 0..7, mutator max_fill 3, max_size 28 (>= 27, red team M10),
                   CRN stream rng_for(seed, slot) with slot = "<arm world>/<opaque id>" (identical across arms).
Information        the search sees ONLY the ARM VIEW: tfs1.e3.worlds.ArmWorld (opaque id + dev, sha-verified against
boundary           ARM_VIEW_MANIFEST); the output type is inferred from the dev outputs. Test, tribunal and witness
                   (evaluator side) reach only the certifier, whose answer only stops the run.
Endpoint (A1-B.4)  a CONSULTATION = the certifier's verdict on a dev-consistent program: search tribunal (salt T0)
                   AND a FRESH tribunal (salt FINAL), each = all test + generated widened tribunal (value-or-FAIL
                   agreement with the sealed expanded witness) + the task's own tribunal. The run stops at the first
                   program passing both.
                   PRIMARY  hit = the FIRST consultation of the run passes (no certifier-filtered drift).
                   SECONDARY hit = any consultation passes within B; CERTIFIER_ASSISTED iff >= 1 earlier consultation
                   failed. Archive OFF at final evaluation: the hit program is re-judged ALONE (common.final_evaluation).
                   A hit at a charge <= #start programs is tagged START_HIT (not discovery).
Ledgers (O1)       descriptor qualification, K calibration and probe runs are INFRA (separate ledger); arms are
                   matched on search charges.
"""
import argparse
import hashlib
import json
import os
import random
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional, Sequence

os.environ.setdefault("OMP_NUM_THREADS", "1")

from tfs1 import core as C                         # noqa: E402
from tfs1.enum import Enumerator                    # noqa: E402
from tfs1.library import Library                    # noqa: E402
from tfs1.e3 import worlds as WD                    # noqa: E402

from . import arms as A                             # noqa: E402
from . import common as K                           # noqa: E402
from . import descriptors as DS                     # noqa: E402
from . import measure as M                          # noqa: E402

HERE = Path(__file__).resolve().parent              # .../beta04/atlas
BETA04 = HERE.parent
DRIVER_VERSION = "e2-driver-v1"

CONFIG = {
    "budget": 200_000,
    "seeds": [0, 1, 2, 3, 4, 5, 6, 7],
    "max_size": 28,
    "max_fill": 3,
    "descriptor": "D-BEH",
    "kcal_seeds": [1000, 1001, 1002],
    "search_salt": "T0",
    "final_salt": "FINAL",
    "qual_params": {"per_size": 1500, "walk_n": 6000, "max_pairs": 20, "n_syn": 6, "seed": 0,
                    "mutants_per_node": 60},
    "atlas_params": {"seeds": [0, 1, 2, 3], "enum_budget": 200_000, "enum_max_size": 8, "density_max_n": 6,
                     "robust_n": 500, "rank_max_class": 1_000_000, "max_fill": 3, "mutator_max_size": 28},
}

# A1-B.2 arm table, at code level
ARMS = {
    "credit_blind": {"code": "D1-chain_neutral", "credit": "none", "library": True, "descriptor": None},
    "chain_strict": {"code": "D1-chain_strict", "credit": "exact", "library": True, "descriptor": None},
    "chain_neutral": {"code": "D1-chain_neutral", "credit": "exact", "library": True, "descriptor": None},
    "D1-X3": {"code": "D1-X3", "credit": "exact", "library": True, "descriptor": "D-BEH", "needs_qual": True},
    "X3G": {"code": "D1-X3G", "credit": "exact", "library": True, "descriptor": "RAND:K", "needs_qual": True,
            "needs_k": True},
    "desert_ref": {"code": "D1-chain_neutral", "credit": "none", "library": False, "descriptor": None},
}
ARM_ORDER = ["credit_blind", "chain_strict", "chain_neutral", "D1-X3", "X3G", "desert_ref"]

# A1-B.6 cluster units: foundry motif-control merge rules (FOUNDRY_DESIGN rule 7), applied to the sealed witness
# skeleton label "<rung>:<kind pair>:<name>[+red]": rung dropped (R3 == R4), readout dropped ("+red"), fold == scan
# (fold_of_X -> scan_of_X; post_fold keeps its name), fold_of_map == step_of_f == scan_of_map, compose == two_maps.
# Unit key = "<kind pair>:<merged name>". On the production R3/R4 set this gives the red team's 5 merged skeletons.
_MERGE = {"step_of_f": "scan_of_map", "compose": "two_maps"}


def cluster_of(skeleton: str) -> str:
    parts = skeleton.split(":")
    kp, name = (parts[1], parts[2]) if len(parts) >= 3 else ("?", parts[-1])
    name = name.split("+")[0]
    if name.startswith("fold_"):                       # fold == scan (stage forms fold_of_X == scan_of_X)
        name = "scan_" + name[len("fold_"):]
    name = _MERGE.get(name, name)
    return "%s:%s" % (kp, name)


def code_sha256() -> Dict[str, str]:
    out = {}
    for d, pat in ((HERE, "*.py"), (BETA04 / "tfs1", "*.py"), (BETA04 / "tfs1" / "e3", "worlds.py")):
        for p in sorted(d.glob(pat)):
            out["%s/%s" % (p.parent.name, p.name)] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def _write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp%d" % os.getpid())
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=True, default=str))
    os.replace(tmp, path)


def _read_json(path: Path):
    return json.loads(Path(path).read_text()) if Path(path).exists() else None


# ================================================================ world access
class E2Root:
    """Coordinator-side index of a foundry output root (production or pilot_v2). Search processes receive only the
    learner task built from the ARM VIEW (learner_task); everything else here is evaluator / sealed side."""

    def __init__(self, root):
        self.root = Path(root)
        self.man = WD.world_manifest(self.root)
        self.label = "EXPOSED DEV DATA (pilot_v2)" if "pilot" in self.root.name else "PRODUCTION"
        self._sealed: Dict[str, Dict] = {}
        self._final: Dict[str, Dict] = {}
        self.meta: Dict[str, Dict] = {}
        for W, w in sorted(self.man["worlds"].items()):
            for opq, v in w["id_map"].items():
                self.meta[v["family_id"]] = {"family_id": v["family_id"], "world": W, "opaque": opq,
                                             "arm_world": w["arm_world"], "rung": v["rung"], "status": v["status"],
                                             "slot": "%s/%s" % (w["arm_world"], opq)}

    def admitted(self, rungs: Sequence[str]) -> List[str]:
        return sorted(f for f, m in self.meta.items() if m["status"] == "ADMITTED" and m["rung"] in rungs)

    def sealed(self, W: str) -> Dict:
        if W not in self._sealed:
            self._sealed[W] = WD.sealed(self.root, W)
        return self._sealed[W]

    def final_rows(self, W: str) -> Dict[str, Dict]:
        if W not in self._final:
            p = self.root / W / "FINAL.jsonl"
            rows = [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []
            self._final[W] = {r["family_id"]: r for r in rows}
        return self._final[W]

    def sealed_family(self, fid: str) -> Dict:
        W = self.meta[fid]["world"]
        return next(f for f in self.sealed(W)["families"] if f["family_id"] == fid)

    def info(self, fid: str) -> Dict:
        m = dict(self.meta[fid])
        sf = self.sealed_family(fid)
        m.update({"constituents": list(sf["mechanisms_used"]), "skeleton": sf.get("skeleton"),
                  "cluster": cluster_of(sf.get("skeleton") or "?:?:?"),
                  "kind_pair": (sf.get("skeleton") or "?:?:?").split(":")[1],
                  "witness_promoted": sf.get("witness_promoted")})
        return m

    def acquired(self, W: str) -> Dict:
        return self.man["worlds"][W]["acquired_library"]

    # ---- learner side (ARM VIEW only)
    def learner_task(self, fid: str, log: Optional[WD.AccessLog] = None) -> Dict:
        m = self.meta[fid]
        aw = WD.ArmWorld(self.root, m["arm_world"])
        fam = aw.family(m["opaque"])
        return {"family_id": fam["slot"], "output_type": fam["output_type"], "dev": fam["dev"],
                "arm_view_file_sha256": fam["file_sha256"]}

    # ---- evaluator side
    def eval_task(self, fid: str) -> Dict:
        """Evaluator task with family_id := the arm slot, so probes / tribunal / enumeration slots are keyed exactly
        like the learner view (the true family id is kept in family_id_true)."""
        m = self.meta[fid]
        t = dict(WD.Evaluator(self.root, m["world"]).task(m["opaque"]))
        t["family_id_true"] = t["family_id"]
        t["family_id"] = m["slot"]
        return K.load_task(t)


def build_library(acq: Dict, mechs: Sequence[str], source: str = "foundry-acquired") -> Optional[Dict]:
    """Library of the given mechanisms' terms. acq: name -> {"term": ...}. Returns None if any is missing."""
    lib = Library(closed_args=True)
    ids = {}
    for m in mechs:
        rec = acq.get(m)
        if rec is None:
            return None
        e, _st = lib.promote_lambda(C.parse(rec["term"]), {"mechanism_slot": m, "from": rec.get("from"),
                                                           "source": source})
        ids[m] = e.id
    return {"lib": lib, "ids": ids}


def tags_in(t) -> set:
    out = {t[0]}
    for c in C.children(t):
        out |= tags_in(c)
    return out


def rename_calls(t, ren: Dict[str, str]):
    tag = t[0]
    if tag in ("int", "var", "xs", "hole"):
        return t
    if tag == "lam":
        return ("lam", t[1], rename_calls(t[2], ren))
    return (ren.get(tag, tag),) + tuple(rename_calls(a, ren) for a in t[1:])


class FamilySetup:
    """Everything the coordinator derives for one family: library, the witness in the library's representation
    (certified), the sealed expanded witness (certifier reference)."""

    def __init__(self, R: E2Root, fid: str):
        self.R, self.fid = R, fid
        self.info = R.info(fid)
        self.task = R.eval_task(fid)
        self.witness = self.task["witness"]                       # sealed, fully expanded (tribunal reference)
        acq = R.acquired(self.info["world"])
        b = build_library(acq["acquired"], self.info["constituents"])
        self.lib = b["lib"] if b else None
        self.lib_ids = b["ids"] if b else {}
        self.library_status = "ACQUIRED_CONSTITUENTS" if b else "LIBRARY_UNAVAILABLE(constituent not acquired)"
        self.missing = [m for m in self.info["constituents"] if m not in acq["acquired"]]
        self.lib_witness, self.lib_witness_source, self.lib_witness_checks = self._lib_witness(acq)

    def certify(self, program, lib) -> Dict:
        t = C.parse(program) if isinstance(program, str) else program
        a = K.Certifier(self.task, lib, self.witness, salt=CONFIG["search_salt"]).qualify(t)
        b = K.Certifier(self.task, lib, self.witness, salt=CONFIG["final_salt"]).qualify(t)
        return {"T0": a, "FINAL": b, "qualified": bool(a["qualified"] and b["qualified"])}

    def _lib_witness(self, acq):
        """(1) sealed witness_promoted with each mechanism call renamed to its ACQUIRED entry; (2) the foundry's own
        chain_d route solution (acquired library, names q_i). The first that type-checks and passes T0 + FINAL is
        the witness used for D-BEH qualification and the atlas route (it is never shown to a search)."""
        if self.lib is None:
            return None, None, []
        checks = []
        cands = []
        if self.info.get("witness_promoted"):
            cands.append(("sealed_witness_promoted->acquired", self.info["witness_promoted"], self.lib_ids))
        row = self.R.final_rows(self.info["world"]).get(self.fid, {})
        cd = row.get("chain_d") or {}
        if cd.get("found"):
            qn = acq.get("names", {})
            ren = {q: self.lib_ids[m] for m, q in qn.items() if m in self.lib_ids}
            cands.append(("foundry_chain_d_found", cd["found"], ren))
        for src, text, ren in cands:
            try:
                t = rename_calls(C.parse(text), ren)
                if any(c not in self.lib for c in C.calls_in(t)) or (tags_in(t) & set(ren)):
                    raise ValueError("uses a non-library call")
                ty = C.type_of(t, 0, None, self.lib)
                v = self.certify(t, self.lib)
                ok = ty == self.task["output_type"] and v["qualified"]
                checks.append({"source": src, "program": C.to_str(t), "type": ty, "qualified": ok})
                if ok:
                    return C.to_str(t), src, checks
            except Exception as e:                            # noqa: BLE001
                checks.append({"source": src, "program": text, "error": repr(e), "qualified": False})
        return None, None, checks


# ================================================================ certifier used inside a search
class DualCertifier:
    """Consulted by arms.Search ONLY for a dev-consistent program; its boolean only decides whether the run stops.
    verify = qualified on the search tribunal (T0) AND on a fresh tribunal (FINAL). Every consultation is logged."""

    def __init__(self, task: Dict, lib, witness: str):
        self.t0 = K.Certifier(task, lib, witness, salt=CONFIG["search_salt"])
        self.fin = K.Certifier(task, lib, witness, salt=CONFIG["final_salt"])
        self.consults: List[Dict] = []

    def verify(self, t) -> bool:
        a = self.t0.qualify(t)
        b = self.fin.qualify(t)
        ok = bool(a["qualified"] and b["qualified"])
        self.consults.append({"program": C.to_str(t), "T0": a["qualified"], "FINAL": b["qualified"],
                              "test_ok": a["test_ok"], "tribunal_T0_ok": a["tribunal_ok"],
                              "tribunal_FINAL_ok": b["tribunal_ok"], "task_tribunal_ok": a["task_tribunal_ok"],
                              "qualified": ok})
        return ok


class StubCertifier:
    """Target-blindness probe: answers `answer` to every consultation (never used in a real run)."""

    def __init__(self, answer: bool):
        self.answer = answer
        self.consults: List[Dict] = []

    def verify(self, t) -> bool:
        self.consults.append({"program": C.to_str(t), "qualified": self.answer})
        return self.answer


# ================================================================ shard kinds
def shard_id(kind: str, fid: str, arm: Optional[str] = None, seed=None) -> str:
    return "/".join(str(x) for x in (kind, fid, arm, None if seed is None else "s%d" % seed) if x is not None)


def shard_path(out: Path, sid: str) -> Path:
    return Path(out) / (sid + ".json")


def _header(R: E2Root, sid: str) -> Dict:
    return {"shard": sid, "driver": DRIVER_VERSION, "root_label": R.label, "root": str(R.root),
            "config": CONFIG, "pid": os.getpid()}


def do_qual(R: E2Root, fid: str) -> Dict:
    """Outcome-free D-BEH qualification (C-013 R1 procedure; descriptors.qualify) on the learner view's probes and
    the family's witness in the library representation. INFRA ledger."""
    t0 = time.process_time()
    fs = FamilySetup(R, fid)
    out = {"family_id": fid, "library_status": fs.library_status, "lib_witness": fs.lib_witness,
           "lib_witness_source": fs.lib_witness_source, "lib_witness_checks": fs.lib_witness_checks}
    if fs.lib is None or fs.lib_witness is None:
        out.update({"verdict": "INSTRUMENT_UNVALIDATED", "reason": "no certified witness in the library "
                    "representation (D-BEH qualification cannot be computed)", "qualified": False})
    else:
        lt = R.learner_task(fid)
        q = DS.qualify(lt, fs.lib_witness, fs.lib, names=(CONFIG["descriptor"],), **CONFIG["qual_params"])
        d = q["descriptors"][CONFIG["descriptor"]]
        out.update({"qualification": q, "verdict": d["verdict"], "R1": d["R1_separation"],
                    "R1c": d["R1c_given_trace_differs"], "R2": d["R2_invariance"], "controls_ok": q["controls_ok"],
                    "qualified": d["verdict"] == "QUALIFIED"})
    out["ledger"] = "INFRA"
    out["cpu_s"] = round(time.process_time() - t0, 2)
    return out


def do_kcal(R: E2Root, fid: str, budget: Optional[int] = None, seeds: Optional[Sequence] = None) -> Dict:
    t0 = time.process_time()
    fs = FamilySetup(R, fid)
    lt = R.learner_task(fid)
    cal = A.calibrate_random_k(lt, fs.lib, "D1-X3", CONFIG["descriptor"], budget or CONFIG["budget"],
                               seeds or CONFIG["kcal_seeds"], E=Enumerator(fs.lib), max_size=CONFIG["max_size"],
                               max_fill=CONFIG["max_fill"])
    return {"family_id": fid, "calibration": cal, "K": cal["K"], "ledger": "INFRA",
            "cpu_s": round(time.process_time() - t0, 2)}


def run_search(view_task: Dict, cert_task: Optional[Dict], lib, arm: str, seed, budget: int, witness: Optional[str],
               k: Optional[int] = None, starts: Optional[Sequence[str]] = None, stop_on_hit: bool = True,
               cpu_cap_s: Optional[float] = None, certifier=None, keep_log: bool = False) -> Dict:
    """One arm run. The Search receives a LearnerView built from view_task (arm-view dev only)."""
    spec = ARMS[arm]
    desc = spec["descriptor"]
    if desc == "RAND:K":
        desc = "RAND:%d" % int(k)
    t0 = time.process_time()
    view = K.LearnerView(view_task)
    cert = certifier if certifier is not None else (DualCertifier(cert_task, lib, witness)
                                                    if cert_task is not None else None)
    E = Enumerator(lib)
    s = A.Search(view, cert, E, spec["code"], seed, budget, 1, desc, stop_on_hit=stop_on_hit,
                 max_size=CONFIG["max_size"], max_fill=CONFIG["max_fill"], credit=spec["credit"], starts=starts,
                 keep_log=keep_log)
    aborted = False
    while not s.done:
        s.step()
        if cpu_cap_s and (s.charges & 1023) == 0 and time.process_time() - t0 > cpu_cap_s:
            aborted = True
            break
    r = s.result()
    r["e2_arm"] = arm
    r["n_starts"] = len(s.starts)
    r["max_size"] = CONFIG["max_size"]
    r["mutator_max_size"] = s.mut.max_size
    r["library_sha256"] = lib.sha256() if lib is not None else None
    consults = list(getattr(cert, "consults", []))
    rows = sorted(s.hits + s.false_hits, key=lambda x: x["charge"])
    for c, row in zip(consults, rows):
        c["charge"] = row["charge"]
    r["consultations"] = consults[:20]
    r["n_consultations"] = len(consults)
    # RAW COMPONENTS (C-013 D1 integrator requirement): e2_analyze re-derives every endpoint from these alone and
    # treats any disagreement with the runner fields as a hard error. Consultations kept: the first 200 and the last
    # 50 (each: program text, charge, dev-consistent by construction, test / T0 tribunal / FINAL tribunal / task
    # tribunal verdicts); the hit (program, charge); budget and charges.
    keep = consults if len(consults) <= 250 else consults[:200] + consults[-50:]
    r["components"] = {
        "budget": budget, "charges": s.charges, "n_starts": len(s.starts), "n_consultations": len(consults),
        "consultations_stored": [dict(c, index=(i if i < 200 or len(consults) <= 250 else len(consults) - 250 + i),
                                      dev_consistent=True) for i, c in enumerate(keep)],
        "hit": ({"program": r["program"], "charge": r["hit_charge"]} if r["hit"] else None),
        "library_sha256": lib.sha256() if lib is not None else None,
        "witness_reference": witness,
    }
    first = consults[0] if consults else None
    r["first_dev_consistent"] = first
    r["primary_hit"] = bool(first and first["qualified"])
    r["secondary_hit"] = bool(r["hit"])
    r["certifier_assisted"] = bool(r["hit"] and not r["primary_hit"])
    r["start_hit"] = bool(r["hit"] and r["hit_charge"] is not None and r["hit_charge"] <= len(s.starts))
    if r["hit"] and cert_task is not None:
        fe = K.final_evaluation(r["program"], cert_task, lib, witness, salt=CONFIG["final_salt"])
        r["final_evaluation"] = fe
        r["autonomous_competence"] = fe["autonomous_pass"]
    r["archive_assisted_tag"] = ("SEARCH_INFRASTRUCTURE (lineage from a genotype archive)"
                                 if A.SPECS[spec["code"]]["admission"] != "none" and r["hit"] else None)
    r["status"] = "ABORTED_CPU_CAP" if aborted else "COMPLETE"
    if keep_log:
        r["decision_log"] = s.log
    r["cpu_s"] = round(time.process_time() - t0, 3)
    r["_search"] = s
    return r


def do_run(R: E2Root, fid: str, arm: str, seed: int, out: Path, cpu_cap_s: Optional[float] = None,
           budget: Optional[int] = None, stop_on_hit: bool = True, timing_k: Optional[int] = None) -> Dict:
    """timing_k (TIMING ONLY, exposed families): skip the qualification gate and use this K for X3G."""
    spec = ARMS[arm]
    k = timing_k
    base = {"family_id": fid, "arm": arm, "seed": seed, "arm_code": spec["code"], "credit": spec["credit"]}
    if spec.get("needs_qual") and timing_k is None:
        q = _read_json(shard_path(out, shard_id("qual", fid)))
        if q is None:
            raise RuntimeError("qualification shard missing for %s (run the qual phase first)" % fid)
        if not q["qualified"]:
            base.update({"status": "INSTRUMENT_UNVALIDATED", "descriptor_verdict": q["verdict"], "run": False})
            return base
    if spec.get("needs_k") and timing_k is None:
        kc = _read_json(shard_path(out, shard_id("kcal", fid)))
        if kc is None:
            raise RuntimeError("K calibration shard missing for %s" % fid)
        k = kc["K"]
    fs = FamilySetup(R, fid)
    lib = fs.lib if spec["library"] else None
    if spec["library"] and lib is None:
        base.update({"status": "LIBRARY_UNAVAILABLE", "missing": fs.missing, "run": False})
        return base
    lt = R.learner_task(fid)
    r = run_search(lt, fs.task, lib, arm, seed, budget or CONFIG["budget"], fs.witness, k=k,
                   stop_on_hit=stop_on_hit, cpu_cap_s=cpu_cap_s)
    r.pop("_search")
    base.update(r)
    base.update({"arm": arm, "arm_code": spec["code"]})        # Search.result()'s "arm" is the code-level name
    base.update({"run": True, "K": k, "library_status": fs.library_status if spec["library"] else "NO_LIBRARY",
                 "arm_view_file_sha256": lt["arm_view_file_sha256"]})
    return base


def do_atlas(R: E2Root, fid: str) -> Dict:
    t0 = time.process_time()
    fs = FamilySetup(R, fid)
    p = dict(CONFIG["atlas_params"])
    if fs.lib is not None and fs.lib_witness is not None:
        lib, w, rep = fs.lib, fs.lib_witness, "ACQUIRED_CONSTITUENTS (witness: %s)" % fs.lib_witness_source
    else:
        lib, w, rep = None, fs.witness, "BASE_GRAMMAR (%s)" % (fs.library_status if fs.lib is None
                                                               else "no certified library witness")
    rec = M.atlas(fs.task, lib, witness=w, seeds=tuple(p["seeds"]), enum_budget=p["enum_budget"],
                  enum_max_size=p["enum_max_size"], density_max_n=p["density_max_n"], robust_n=p["robust_n"],
                  rank_max_class=p["rank_max_class"], max_fill=p["max_fill"], E=Enumerator(lib),
                  mutator_max_size=p["mutator_max_size"])
    out = {"family_id": fid, "rung": fs.info["rung"], "cluster": fs.info["cluster"], "representation": rep,
           "library_status": fs.library_status, "witness_used": w, "atlas": rec,
           "classification_route": M.classify(rec, CONFIG["budget"]),
           "existence_sealed_expanded": K.witness_existence(fs.task, None, fs.witness),
           "complete": True, "cpu_s": round(time.process_time() - t0, 2)}
    return out


# ================================================================ shard execution
def execute(shard: Dict) -> Dict:
    """Worker entry point (one process per shard). Skips if the result exists; writes atomically."""
    os.environ["OMP_NUM_THREADS"] = "1"
    out = Path(shard["out"])
    sid = shard["id"]
    p = shard_path(out, sid)
    if p.exists():
        return {"id": sid, "skipped": True}
    R = E2Root(shard["root"])
    t0 = time.process_time()
    try:
        kind = shard["kind"]
        if kind == "qual":
            res = do_qual(R, shard["fid"])
        elif kind == "kcal":
            res = do_kcal(R, shard["fid"], budget=shard.get("budget"))
        elif kind == "run":
            res = do_run(R, shard["fid"], shard["arm"], shard["seed"], out, shard.get("cpu_cap_s"),
                         budget=shard.get("budget"))
            if res.get("status") == "ABORTED_CPU_CAP":
                p = shard_path(out, sid + ".ABORTED")      # never counted as a completed shard
        elif kind == "atlas":
            res = do_atlas(R, shard["fid"])
        else:
            raise ValueError(kind)
    except Exception:                                   # noqa: BLE001
        err = {"id": sid, "error": traceback.format_exc()}
        _write_json(shard_path(out, sid + ".ERROR"), err)
        return {"id": sid, "error": True}
    res.update(_header(R, sid))
    res["shard_cpu_s"] = round(time.process_time() - t0, 2)
    _write_json(p, res)
    return {"id": sid, "cpu_s": res["shard_cpu_s"]}


def _pool(fn, todo: List[Dict], workers: int, max_wall_s: Optional[float], log) -> List[Dict]:
    """At most `workers` spawned processes, one shard per process; a new shard is started only while the wall clock
    is below max_wall_s (running shards always finish). Results never depend on the schedule."""
    import multiprocessing as mp
    from concurrent.futures import FIRST_COMPLETED, wait
    t0 = time.time()
    done, pending, queue = [], set(), list(todo)
    with ProcessPoolExecutor(max_workers=max(1, workers), mp_context=mp.get_context("spawn"),
                             max_tasks_per_child=1) as ex:
        while queue or pending:
            while queue and len(pending) < workers and (not max_wall_s or time.time() - t0 < max_wall_s):
                pending.add(ex.submit(fn, queue.pop(0)))
            if not pending:
                break
            fin, pending = wait(pending, return_when=FIRST_COMPLETED)
            for fu in fin:
                r = fu.result()
                log(json.dumps(r))
                done.append(r)
    if queue:
        log("wall limit reached: %d shards not started (re-run to resume)" % len(queue))
    return done


def run_shards(shards: List[Dict], workers: int = 2, log=print, max_wall_s: Optional[float] = None) -> List[Dict]:
    """<= workers processes (spawned, one shard per process); completed shards are skipped; order-independent."""
    todo = [s for s in sorted(shards, key=lambda s: s["id"]) if not shard_path(Path(s["out"]), s["id"]).exists()]
    log("shards: %d total, %d to run, workers %d" % (len(shards), len(todo), workers))
    if not todo:
        return []
    if workers <= 1:
        out = []
        for s in todo:
            r = execute(s)
            log(json.dumps(r))
            out.append(r)
        return out
    return _pool(execute, todo, workers, max_wall_s, log)


# ================================================================ plan
def make_plan(R: E2Root, out: Path, n_seeds: int = 8, drop: Sequence[str] = (), drop_desert_ref_for: Sequence = (),
              truncation_note: Optional[List[str]] = None, budget: Optional[int] = None,
              families: Optional[Sequence[str]] = None) -> Dict:
    """budget / families overrides exist for TESTS on exposed data only; production uses CONFIG and every admitted
    R3/R4 family."""
    fams = list(families) if families else R.admitted(("R3", "R4"))
    if (budget not in (None, CONFIG["budget"]) or families) and R.label == "PRODUCTION":
        raise SystemExit("budget / family overrides are for exposed (test) data only")
    arms = [a for a in ARM_ORDER if a not in drop]
    seeds = CONFIG["seeds"][:n_seeds]
    runs = []
    for f in fams:
        for a in arms:
            if a == "desert_ref" and f in drop_desert_ref_for:
                continue
            for sd in seeds:
                runs.append(shard_id("run", f, a, sd))
    plan = {"driver": DRIVER_VERSION, "root": str(R.root), "root_label": R.label, "config": CONFIG,
            "budget": budget or CONFIG["budget"],
            "screen_families": fams, "atlas_families": R.admitted(("R2", "R3", "R4")), "arms": arms,
            "seeds": seeds, "run_shards": runs, "truncation": truncation_note or [],
            "dropped_desert_ref_for": list(drop_desert_ref_for),
            "clusters": {f: R.info(f)["cluster"] for f in fams}, "code_sha256": code_sha256()}
    _write_json(Path(out) / "PLAN.json", plan)
    return plan


def shards_for(plan: Dict, out: Path, phase: str, cpu_cap_s: Optional[float] = None) -> List[Dict]:
    base = {"root": plan["root"], "out": str(out), "budget": plan.get("budget", CONFIG["budget"])}
    if phase == "qual":
        return [{**base, "kind": "qual", "fid": f, "id": shard_id("qual", f)} for f in plan["screen_families"]]
    if phase == "kcal":
        out_l = []
        for f in plan["screen_families"]:
            q = _read_json(shard_path(out, shard_id("qual", f)))
            if q and q["qualified"] and "X3G" in plan["arms"]:
                out_l.append({**base, "kind": "kcal", "fid": f, "id": shard_id("kcal", f)})
        return out_l
    if phase == "run":
        out_l = []
        for sid in plan["run_shards"]:
            _k, f, a, s = sid.split("/")
            out_l.append({**base, "kind": "run", "fid": f, "arm": a, "seed": int(s[1:]), "id": sid,
                          "cpu_cap_s": cpu_cap_s})
        return out_l
    if phase == "atlas":
        return [{**base, "kind": "atlas", "fid": f, "id": shard_id("atlas", f)} for f in plan["atlas_families"]]
    raise ValueError(phase)


def status(plan: Dict, out: Path) -> Dict:
    st = {}
    for ph in ("qual", "kcal", "run", "atlas"):
        sh = shards_for(plan, out, ph)
        done = [s for s in sh if shard_path(out, s["id"]).exists()]
        err = [s["id"] for s in sh if shard_path(out, s["id"] + ".ERROR").exists()]
        st[ph] = {"total": len(sh), "done": len(done), "errors": err}
    return st


# ================================================================ pre-launch checks (A1-B.8)
def _int_expr(v: int) -> str:
    """A base-grammar expression for an integer (literals are 0..3)."""
    if v < 0:
        return "(neg %s)" % _int_expr(-v)
    if v <= 3:
        return str(v)
    q, r = divmod(v, 3)
    e = "(mul 3 %s)" % _int_expr(q)
    return e if r == 0 else "(add %s %d)" % (e, r)


def control_programs(task: Dict) -> List[Dict]:
    """Constant and dev-LOOKUP programs (dev-consistent by construction where expressible). They must NOT certify."""
    T = task["output_type"]
    dev = task["dev"]
    outs = [o for _i, o in dev]
    progs = []
    if T == C.INT:
        modal = max(set(outs), key=lambda v: (outs.count(v), -abs(v)))
        progs.append({"kind": "constant(dev modal)", "program": _int_expr(modal)})
        keys = [sum(i) for i, _o in dev]
        if len(set(keys)) == len(keys):
            e = _int_expr(outs[-1])
            for (i, o) in reversed(dev[:-1]):
                e = "(if (eq (sum xs) %s) %s %s)" % (_int_expr(sum(i)), _int_expr(o), e)
            progs.append({"kind": "lookup(sum-keyed dev table)", "program": e})
    elif T == C.BOOL:
        modal = max(set(outs), key=outs.count)
        progs.append({"kind": "constant(dev modal)", "program": "(lt 0 1)" if modal else "(lt 1 0)"})
    else:
        progs.append({"kind": "constant(identity xs)", "program": "xs"})
        progs.append({"kind": "constant(empty)", "program": "(filter (lam x (lt 1 0)) xs)"})
    return progs


def control_family(kind: str) -> Dict:
    """Synthetic CONTROL families (Int). CONTROL-CONSTANT: dev outputs constant, test outputs structureless.
    CONTROL-LOOKUP: dev and test outputs structureless (random), test inputs disjoint from dev. Nothing may qualify."""
    r = random.Random("E2/CONTROL/%s" % kind)

    def lst():
        return [r.randint(-20, 20) for _ in range(r.randint(2, 8))]
    dev = [[lst(), 3 if kind == "CONSTANT" else r.randint(-50, 50)] for _ in range(12)]
    seen = {tuple(i) for i, _ in dev}
    test = []
    while len(test) < 40:
        i = lst()
        if tuple(i) not in seen:
            test.append([i, r.randint(-50, 50)])
    return K.load_task({"family_id": "CONTROL-%s" % kind, "output_type": "Int", "dev": dev, "test": test})


def _perturb(task: Dict) -> Dict:
    t = json.loads(json.dumps(task))
    t["test"] = [[i, (o + 7) if isinstance(o, int) and not isinstance(o, bool) else
                  ((not o) if isinstance(o, bool) else (list(o) + [1]) if isinstance(o, list) else o)]
                 for i, o in t["test"]]
    t["tribunal"] = []
    return K.load_task(t)


def prelaunch(R: E2Root, out: Path, small_b: int = 2000, tb_b: int = 3000, tb_families: int = 2,
              log=print) -> Dict:
    t_start = time.process_time()
    rep = {"driver": DRIVER_VERSION, "root": str(R.root), "root_label": R.label, "checks": {}}
    screen = R.admitted(("R3", "R4"))
    allf = R.admitted(("R2", "R3", "R4"))
    setups = {f: FamilySetup(R, f) for f in allf}

    # ---- 1. certifier re-check: every sealed witness, every library witness, every foundry route solution
    wit, routes = [], []
    for f in allf:
        fs = setups[f]
        v = fs.certify(fs.witness, None)
        ex = K.witness_existence(fs.task, None, fs.witness)
        wit.append({"family_id": f, "kind": "sealed_witness_expanded", "qualified": v["qualified"],
                    "exists": ex.get("exists"), "size_expanded": ex.get("size_expanded")})
        if fs.lib is not None:
            wit.append({"family_id": f, "kind": "library_witness", "source": fs.lib_witness_source,
                        "program": fs.lib_witness, "qualified": fs.lib_witness is not None,
                        "required": f in screen, "checks": fs.lib_witness_checks})
        row = R.final_rows(fs.info["world"]).get(f, {})
        W = fs.info["world"]
        sealed_mech = {m["name"]: {"term": m["term"]} for m in R.sealed(W)["mechanisms"]}
        kp = row.get("kp") or {}
        if kp.get("found"):
            used = sorted(tags_in(C.parse(kp["found"])) & set(sealed_mech))
            b = build_library(sealed_mech, used, "sealed")
            ren = b["ids"] if b else {}
            try:
                t = rename_calls(C.parse(kp["found"]), ren)
                vv = fs.certify(t, b["lib"] if b else None)
                routes.append({"family_id": f, "route": "kp (SEALED mechanisms)", "program": kp["found"],
                               "qualified": vv["qualified"], "T0": vv["T0"], "FINAL": vv["FINAL"],
                               "foundry_qualified": kp.get("status") == "SOLVED" and kp.get("tribunal_ok") is True})
            except Exception as e:                    # noqa: BLE001
                routes.append({"family_id": f, "route": "kp", "program": kp["found"], "qualified": False,
                               "error": repr(e)})
        cd = row.get("chain_d") or {}
        if cd.get("found"):
            acq = R.acquired(W)
            names = acq.get("names", {})
            used_m = [m for m, q in names.items() if q in tags_in(C.parse(cd["found"]))]
            b = build_library(acq["acquired"], sorted(names), "foundry-acquired")
            ren = {names[m]: b["ids"][m] for m in names} if b else {}
            try:
                t = rename_calls(C.parse(cd["found"]), ren)
                vv = fs.certify(t, b["lib"])
                routes.append({"family_id": f, "route": "chain_d (ACQUIRED primitives)", "program": cd["found"],
                               "mechanisms": used_m, "qualified": vv["qualified"], "T0": vv["T0"],
                               "FINAL": vv["FINAL"], "foundry_qualified": cd.get("status") == "SOLVED"})
            except Exception as e:                    # noqa: BLE001
                routes.append({"family_id": f, "route": "chain_d", "program": cd["found"], "qualified": False,
                               "error": repr(e)})
    # R1 acquisitions (chain_c found programs) judged on their own R1 family
    for W in sorted({setups[f].info["world"] for f in allf}):
        for m, a in sorted(R.acquired(W)["acquired"].items()):
            r1 = a.get("from")
            row = R.final_rows(W).get(r1, {})
            cc = row.get("chain_c") or {}
            if not cc.get("found") or r1 not in R.meta:
                routes.append({"family_id": r1, "route": "chain_c R1 acquisition of %s/%s" % (W, m),
                               "qualified": False, "foundry_qualified": True,
                               "error": "no found program / R1 family not in manifest"})
                continue
            t1 = R.eval_task(r1)
            v1 = {s: K.Certifier(t1, None, t1["witness"], salt=s).qualify(C.parse(cc["found"]))["qualified"]
                  for s in (CONFIG["search_salt"], CONFIG["final_salt"])}
            routes.append({"family_id": r1, "route": "chain_c R1 acquisition of %s/%s" % (W, m),
                           "program": cc["found"], "qualified": all(v1.values()), "by_salt": v1,
                           "foundry_qualified": cc.get("status") == "ACQUIRED" and cc.get("test_ok") is True
                           and cc.get("tribunal_ok") is True})
    for x in routes:
        x.setdefault("foundry_qualified", True)
        x["agrees_with_foundry"] = x["qualified"] == x["foundry_qualified"]
    c1 = {"witnesses": wit, "route_solutions": routes,
          "pass_witnesses": all(x["qualified"] for x in wit if x["kind"] == "sealed_witness_expanded") and
          all(x["qualified"] for x in wit if x["kind"] == "library_witness" and x["required"]),
          "route_failures": [x for x in routes if not x["qualified"]],
          "route_disagreements": [x for x in routes if not x["agrees_with_foundry"]],
          "route_rule": "PASS iff the E2 certifier's verdict (test + T0 + FINAL generated tribunals + task tribunal) "
                        "EQUALS the foundry's recorded verdict for every route solution (kp: SOLVED and tribunal_ok; "
                        "chain_d: SOLVED; chain_c: ACQUIRED, test_ok and tribunal_ok). E2 stricter on a "
                        "foundry-accepted route (headroom loss) or looser on a rejected one both FAIL. Routes the "
                        "foundry itself rejected are listed in route_failures for information."}
    c1["pass_routes"] = not c1["route_disagreements"]
    c1["pass"] = c1["pass_witnesses"] and c1["pass_routes"]
    rep["checks"]["certifier_recheck"] = c1
    log("prelaunch 1 certifier_recheck pass=%s (witnesses %s, routes %s)" % (c1["pass"], c1["pass_witnesses"],
                                                                          c1["pass_routes"]))

    # ---- 2. start-at-target control: every arm started AT the witness hits at search charge 0 (START_HIT)
    sat = []
    for f in screen:
        fs = setups[f]
        lt = R.learner_task(f)
        for arm in ARM_ORDER:
            lib = fs.lib if ARMS[arm]["library"] else None
            if ARMS[arm]["library"] and (lib is None or fs.lib_witness is None):
                sat.append({"family_id": f, "arm": arm, "pass": False, "reason": "no library witness"})
                continue
            w0 = fs.lib_witness if ARMS[arm]["library"] else fs.witness
            r = run_search(lt, fs.task, lib, arm, 0, 50, fs.witness, k=64, starts=[w0])
            ok = r["hit"] and r["hit_charge"] == 1 and r["start_hit"] and r["primary_hit"]
            sat.append({"family_id": f, "arm": arm, "hit_charge": r["hit_charge"], "search_steps_charged": (
                r["hit_charge"] - r["n_starts"]) if r["hit"] else None, "start_hit": r["start_hit"],
                "counts_as_discovery": False, "pass": bool(ok)})
    rep["checks"]["start_at_target"] = {"rows": sat, "pass": all(x["pass"] for x in sat)}
    log("prelaunch 2 start_at_target pass=%s" % rep["checks"]["start_at_target"]["pass"])

    # ---- 3. constant / lookup controls
    progs = []
    for f in allf:
        fs = setups[f]
        for pr in control_programs(fs.task):
            t = C.parse(pr["program"])
            dev_ok = K.exact_credit(K.outs_of(t, [i for i, _ in fs.task["dev"]]),
                                    [o for _, o in fs.task["dev"]]) == len(fs.task["dev"])
            v = fs.certify(t, None)
            progs.append({"family_id": f, **pr, "dev_consistent": dev_ok, "qualified": v["qualified"],
                          "pass": not v["qualified"]})
    fams = []
    for kind in ("CONSTANT", "LOOKUP"):
        ct = control_family(kind)
        lt = {"family_id": ct["family_id"], "output_type": ct["output_type"], "dev": ct["dev"]}
        for pr in control_programs(ct):
            v = K.Certifier(ct, None, None).qualify(C.parse(pr["program"]))
            fams.append({"family": ct["family_id"], "program_control": pr, "qualified": v["qualified"],
                         "pass": not v["qualified"]})
        for arm in ARM_ORDER:
            r = run_search(lt, ct, None, arm, 0, small_b, None, k=64)
            fams.append({"family": ct["family_id"], "arm": arm, "budget": small_b, "hit": r["hit"],
                         "n_consultations": r["n_consultations"], "pass": not r["hit"]})
    rep["checks"]["constant_lookup_control"] = {
        "programs_on_E2_families": progs, "control_families": fams,
        "pass": all(x["pass"] for x in progs) and all(x["pass"] for x in fams),
        "note": "a qualified constant/lookup program or any control-family hit -> VOID_CONTROLS"}
    log("prelaunch 3 constant_lookup_control pass=%s" % rep["checks"]["constant_lookup_control"]["pass"])

    # ---- 4. target-blindness: perturb test + witness, and an always-ACCEPT stub certifier -> identical decision
    #         trace and archive (stop_on_hit=False), per arm, on >= 2 screen families and on CONTROL-CONSTANT (where
    #         dev-consistent programs are consulted early, so the certifier channel is exercised for every arm)
    tb = []
    cc = control_family("CONSTANT")
    cases = [(f, setups[f]) for f in screen[:tb_families]] + [("CONTROL-CONSTANT", None)]
    for f, fs in cases:
        if fs is not None:
            log_ = WD.AccessLog()
            with log_.active():
                lt = R.learner_task(f)
            outside = log_.outside(R.root / "arm_view")
            tb.append({"family_id": f, "check": "arm-view loading", "files_outside_arm_view": outside,
                       "arm_view_dev_equals_evaluator_dev": lt["dev"] == fs.task["dev"],
                       "pass": not outside and lt["dev"] == fs.task["dev"]})
            task, wit_ = fs.task, fs.witness
            alt_w = "(sum xs)" if task["output_type"] == C.INT else ("xs" if task["output_type"] == C.LIST
                                                                    else "(lt 0 (len xs))")
        else:
            lt = {"family_id": cc["family_id"], "output_type": cc["output_type"], "dev": cc["dev"]}
            task, wit_, alt_w = cc, None, "(sum xs)"
        pt = _perturb(task)
        for arm in ARM_ORDER:
            lib = fs.lib if (fs is not None and ARMS[arm]["library"]) else None
            if fs is not None and ARMS[arm]["library"] and lib is None:
                tb.append({"family_id": f, "arm": arm, "pass": False, "reason": "no library"})
                continue
            a = run_search(lt, task, lib, arm, 0, tb_b, wit_, k=64, stop_on_hit=False)
            b = run_search(lt, pt, lib, arm, 0, tb_b, alt_w, k=64, stop_on_hit=False)
            c = run_search(lt, task, lib, arm, 0, tb_b, wit_, k=64, stop_on_hit=False,
                           certifier=StubCertifier(True))
            sa, sb, sc = a.pop("_search"), b.pop("_search"), c.pop("_search")
            same_log = a["decision_log_sha256"] == b["decision_log_sha256"] == c["decision_log_sha256"]
            arch = lambda z: [e["text"] for e in z.entries]                           # noqa: E731
            same_arch = arch(sa) == arch(sb) == arch(sc)
            ans = lambda r: [x["qualified"] for x in r["consultations"]]              # noqa: E731
            tb.append({"family_id": f, "arm": arm, "budget": tb_b, "same_decision_log": same_log,
                       "same_archive": same_arch,
                       "consultations": [a["n_consultations"], b["n_consultations"], c["n_consultations"]],
                       "certifier_exercised": a["n_consultations"] > 0 and ans(a) != ans(c),
                       "pass": same_log and same_arch})
    exercised = {arm: any(r.get("certifier_exercised") for r in tb if r.get("arm") == arm) for arm in ARM_ORDER}
    rep["checks"]["target_blindness"] = {"rows": tb, "certifier_channel_exercised_by_arm": exercised,
                                         "pass": all(x["pass"] for x in tb) and all(exercised.values())}
    log("prelaunch 4 target_blindness pass=%s" % rep["checks"]["target_blindness"]["pass"])

    # ---- 5. restoration receipt (red team MINOR): snapshot mid-run, restore into a NEW Search, identical log
    f = screen[0]
    fs = setups[f]
    lt = R.learner_task(f)
    rr = []
    for arm in ("D1-X3", "chain_neutral"):
        spec = ARMS[arm]
        mk = lambda: A.Search(K.LearnerView(lt), None, Enumerator(fs.lib), spec["code"], 0, 3000, 1,   # noqa: E731
                              spec["descriptor"], stop_on_hit=False, max_size=CONFIG["max_size"],
                              credit=spec["credit"])
        s1 = mk()
        s1.run()
        s2 = mk()
        while s2.charges < 1500:
            s2.step()
        snap = s2.snapshot()
        s3 = mk()
        s3.restore_state(snap)
        s3.run()
        geno_ok = all(K.exact_credit(K.outs_of(C.parse(e["text"]), s1.view.dev_inputs, fs.lib), s1.view.targets)
                      == e["score"] for e in s1.entries[:500])
        rr.append({"family_id": f, "arm": arm, "state_restore_identical": s3.loghash.hexdigest() ==
                   s1.loghash.hexdigest(), "genotype_restore_exact_first500": geno_ok,
                   "pass": s3.loghash.hexdigest() == s1.loghash.hexdigest() and geno_ok})
    rep["checks"]["restoration_receipt"] = {"rows": rr, "pass": all(x["pass"] for x in rr)}
    log("prelaunch 5 restoration pass=%s" % rep["checks"]["restoration_receipt"]["pass"])

    rep["pass"] = all(c["pass"] for c in rep["checks"].values())
    rep["summary"] = {k: c["pass"] for k, c in rep["checks"].items()}
    rep["cpu_s"] = round(time.process_time() - t_start, 1)
    rep["code_sha256"] = code_sha256()
    return rep


# ================================================================ timing (EXPOSED pilot_v2 only)
def timing(R: E2Root, out: Path, families: Sequence[str], budget: int, cpu_cap_s: float, workers: int = 2,
           log=print, max_wall_s: Optional[float] = None) -> Dict:
    if R.label == "PRODUCTION":
        raise SystemExit("timing runs on EXPOSED families only (pilot_v2); refusing on production")
    sh = []
    base = {"root": str(R.root), "out": str(out)}
    for f in families:
        sh.append({**base, "kind": "qual", "fid": f, "id": shard_id("qual", f)})
        sh.append({**base, "kind": "atlas", "fid": f, "id": shard_id("atlas", f)})
    run_shards(sh, workers, log, max_wall_s)
    sh = [{**base, "kind": "tkcal", "fid": f, "id": shard_id("tkcal", f)} for f in families]
    sh += [{**base, "kind": "trun", "fid": f, "arm": a, "seed": 0, "id": shard_id("trun", f, a, 0),
            "cpu_cap_s": cpu_cap_s, "budget": budget} for f in families for a in ARM_ORDER]
    run_shards_timing(sh, workers, log, max_wall_s)
    return summarize_timing(R, out, families, budget)


def execute_timing(shard: Dict) -> Dict:
    """Timing shards: full-budget runs (stop_on_hit=False: the conservative per-run cost) and a ONE-seed K
    calibration probe (cost per calibration seed), on EXPOSED families. Never used on production."""
    os.environ["OMP_NUM_THREADS"] = "1"
    out = Path(shard["out"])
    p = shard_path(out, shard["id"])
    if p.exists():
        return {"id": shard["id"], "skipped": True}
    R = E2Root(shard["root"])
    t0 = time.process_time()
    try:
        if shard["kind"] == "tkcal":
            fs = FamilySetup(R, shard["fid"])
            lt = R.learner_task(shard["fid"])
            E = Enumerator(fs.lib)
            ta = time.process_time()
            s = A.Search(K.LearnerView(lt), None, E, "D1-X3", 1000, CONFIG["budget"], 1, "D-BEH",
                         stop_on_hit=False, max_size=CONFIG["max_size"])
            while not s.done:
                s.step()
                if (s.charges & 1023) == 0 and time.process_time() - ta > 840:
                    break
            ref_cells = s.realised_cells()
            x3_cpu = time.process_time() - ta
            tb_ = time.process_time()
            g = A.Search(K.LearnerView(lt), None, E, "D1-X3G", 1000, CONFIG["budget"], 1,
                         "RAND:%d" % max(1, ref_cells), stop_on_hit=False, max_size=CONFIG["max_size"])
            while not g.done:
                g.step()
                if (g.charges & 1023) == 0 and time.process_time() - tb_ > 840:
                    break
            res = {"family_id": shard["fid"], "ref_cells_seed1000": ref_cells, "x3_charges": s.charges,
                   "x3_cpu_s": round(x3_cpu, 2), "x3g_charges": g.charges, "x3g_cells_at_K_eq_ref": g.realised_cells(),
                   "x3g_cpu_s": round(time.process_time() - tb_, 2),
                   "note": "one calibration seed: X3 at the full budget + X3G at K = X3's cells (first iteration)"}
        else:
            kc = _read_json(shard_path(out, shard_id("tkcal", shard["fid"]))) or {}
            res = do_run(R, shard["fid"], shard["arm"], shard["seed"], out, shard.get("cpu_cap_s"),
                         budget=shard.get("budget"), stop_on_hit=False,
                         timing_k=max(1, kc.get("ref_cells_seed1000") or 1))
            res["timing_note"] = "TIMING ONLY: qualification gate bypassed; X3G K = X3 realised cells (seed 1000)"
            res.pop("consultations", None)
    except Exception:                                   # noqa: BLE001
        _write_json(shard_path(out, shard["id"] + ".ERROR"), {"error": traceback.format_exc()})
        return {"id": shard["id"], "error": True}
    res.update(_header(R, shard["id"]))
    res["shard_cpu_s"] = round(time.process_time() - t0, 2)
    _write_json(p, res)
    return {"id": shard["id"], "cpu_s": res["shard_cpu_s"]}


def run_shards_timing(shards, workers, log, max_wall_s=None):
    todo = [s for s in shards if not shard_path(Path(s["out"]), s["id"]).exists()]
    if todo:
        _pool(execute_timing, todo, workers, max_wall_s, log)


def summarize_timing(R: E2Root, out: Path, families: Sequence[str], budget: int) -> Dict:
    rows = {}
    for f in families:
        q = _read_json(shard_path(out, shard_id("qual", f))) or {}
        a = _read_json(shard_path(out, shard_id("atlas", f))) or {}
        kc = _read_json(shard_path(out, shard_id("tkcal", f))) or {}
        arms = {}
        for arm in ARM_ORDER:
            r = _read_json(shard_path(out, shard_id("trun", f, arm, 0)))
            if r is None:
                r = _read_json(shard_path(out, shard_id("trun", f, arm, 0) + ".ABORTED"))
            if r is None or not r.get("run", True) and r.get("status") != "INSTRUMENT_UNVALIDATED":
                arms[arm] = None
                continue
            ch = (r.get("ledger") or {}).get("search", {}).get("charges")
            arms[arm] = {"cpu_s": r.get("cpu_s"), "charges": ch, "status": r.get("status"),
                         "cpu_s_per_2e5": round(r["cpu_s"] * budget / ch, 1) if ch else None,
                         "realised_cells": (r.get("archive") or {}).get("realised_cells"),
                         "descriptor": r.get("descriptor")}
        rows[f] = {"arms": arms, "qual_cpu_s": q.get("cpu_s"), "qual_verdict": q.get("verdict"),
                   "atlas_cpu_s": a.get("cpu_s"), "kcal_probe": kc}
    return {"families": rows, "budget": budget}


# ================================================================ CLI
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", choices=["qualify", "plan", "prelaunch", "atlas", "screen", "status", "timing"])
    ap.add_argument("--root", default=str(BETA04 / "foundry" / "production"))
    ap.add_argument("--out", default=str(BETA04 / "runs" / "e2"))
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--drop-chain-strict", action="store_true", help="truncation step 1 (A1-B.10)")
    ap.add_argument("--drop-desert-ref", action="store_true",
                    help="truncation step 3: drop desert_ref on families whose admission shows from-scratch failure")
    ap.add_argument("--cpu-cap-s", type=float, default=0.0, help="per-run CPU guard (0 = none); aborted shards are "
                    "written as *.ABORTED.json and are NOT complete")
    ap.add_argument("--families", nargs="*")
    ap.add_argument("--max-wall-s", type=float, default=0.0, help="stop STARTING shards after this wall time "
                    "(running shards finish; re-run to resume)")
    ap.add_argument("--budget", type=int, default=CONFIG["budget"])
    a = ap.parse_args(argv)
    R = E2Root(a.root)
    out = Path(a.out)
    if a.mode == "qualify":
        # outcome-free D-BEH qualification of every screen family (no plan needed); its qualified count feeds
        # atlas.e2_project, which decides the A1-B.10 truncation BEFORE `plan`
        base = {"root": str(R.root), "out": str(out)}
        run_shards([{**base, "kind": "qual", "fid": f, "id": shard_id("qual", f)} for f in R.admitted(("R3", "R4"))],
                   a.workers, max_wall_s=a.max_wall_s or None)
    elif a.mode == "plan":
        drop = ["chain_strict"] if a.drop_chain_strict else []
        note = []
        if a.drop_chain_strict:
            note.append("A1-B.10 truncation 1: chain_strict dropped")
        if a.seeds < 8:
            note.append("A1-B.10 truncation 2: %d seeds" % a.seeds)
        dd = []
        if a.drop_desert_ref:
            for f in R.admitted(("R3", "R4")):
                row = R.final_rows(R.meta[f]["world"]).get(f, {})
                if (row.get("base1e6") or {}).get("solved") is False:
                    dd.append(f)
            note.append("A1-B.10 truncation 3: desert_ref dropped on %d families whose admission row shows "
                        "base1e6.solved == False (from-scratch failure at 1e6)" % len(dd))
        p = make_plan(R, out, a.seeds, drop, dd, note)
        print(json.dumps({k: p[k] for k in ("root_label", "arms", "seeds", "truncation")}), len(p["run_shards"]),
              "run shards")
    elif a.mode == "prelaunch":
        rep = prelaunch(R, out)
        dest = out.parent / ("E2_PRELAUNCH.json" if R.label == "PRODUCTION" else "E2_PRELAUNCH_%s.json"
                             % R.root.name)
        _write_json(dest, rep)
        print("PRELAUNCH", "PASS" if rep["pass"] else "FAIL", rep["summary"], "->", dest)
    elif a.mode == "atlas":
        plan = _read_json(out / "PLAN.json")
        if plan is None:
            raise SystemExit("run `plan` first")
        run_shards(shards_for(plan, out, "atlas"), a.workers, max_wall_s=a.max_wall_s or None)
    elif a.mode == "screen":
        plan = _read_json(out / "PLAN.json")
        if plan is None:
            raise SystemExit("run `plan` first")
        for ph in ("qual", "kcal", "run"):
            run_shards(shards_for(plan, out, ph, a.cpu_cap_s or None), a.workers, max_wall_s=a.max_wall_s or None)
        print(json.dumps(status(plan, out)))
    elif a.mode == "status":
        plan = _read_json(out / "PLAN.json")
        print(json.dumps(status(plan, out), indent=1))
    elif a.mode == "timing":
        fams = a.families or []
        res = timing(R, out, fams, a.budget, a.cpu_cap_s or 840, a.workers, max_wall_s=a.max_wall_s or None)
        _write_json(out / "TIMING_RAW.json", res)
        print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
