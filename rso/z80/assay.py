"""C-017-T030 attribution assay: WHO WROTE THE BYTES of the functional organisms of one Z80 Atlas run.

Input: a RECORD = an engine run's own output {"spec", "seed", "out" (engine.run's dict)}; any other field is ignored.
  1. replay (spec, seed) under rso/z80/observe.py; REFUSE unless the replayed final population (cell, tape, generation) equals the
     record's byte for byte. The trust root is the pinned engine code and the VM, never a stored claim.
  2. functional organism = solves the run's 8 probe ECHO cases with a ZEROED neighbour (F0), or with the neighbour it really had
     at its last observed opportunity (situ, observe.py); the second without the first is neighbour-dependent competence.
  3. organism label = which writer's bytes ALONE carry the function (the other bytes zeroed): P -> ENDO, R -> EXT, I -> INS;
     else ENV if the function needs kept/environment bytes (or exists only with the neighbour); else OTHER.
  4. run class = the strict-majority label among functional organisms (NONE if none, MIXED if no majority).
     origin = INSERTED if a founder SUPPLIED by the transplant or seeded path (observed in the replay) is F0, else ARISEN.
Never read: provenance, origin_class, inserted_ancestry, founders, score, spontaneous_replication, events' mech, spec init label.

    python -m rso.z80.assay dev OUT_PREFIX N [i/k]     development check (17_030_xxx), shard i of k (<= 2 processes)
    python -m rso.z80.assay confirm OUT_PREFIX --cleared-by REF [i/k]   refuses unless `freeze check` passes (PREREGISTRATION s9)
"""
import copy
import gzip
import hashlib
import json
import os
import platform
import sys
import time
from functools import lru_cache

from archaeon.z80atlas import engine as E, tasks as T, vm
from archaeon.z80atlas.grammar import FROZEN
from rso.slice001.receipt import sha256_hex
from rso.z80 import observe, subjects as S

N_PROBE = 8
KEYS = ("cls", "origin", "refused", "n_func", "n_ENDO", "n_EXT", "n_ENV", "n_INS", "n_OTHER")
LABELS = ("ENDO", "EXT", "ENV", "INS", "OTHER")
FORGERIES = {"LABELS": "H_EXT_SHORT", "PLANT": "NH_ENDO_SHORT", "PHYS": ("H_EXT_SHORT", "NH_ENDO_SHORT"), "TAPE": "H_EXT_GATED",
             "GEN": "NH_ENDO_SHORT"}
CONFIRM_N = {"RECON_ENDO_IMPL": 48, "NH_ENDO_SHORT": 48}           # every other arm 24 (PREREGISTRATION s6)
N_FORGE = 8                                                        # records per forgery kind and source arm


def probe_cases(seed):
    return observe.probe_cases(seed, S.TASK, N_PROBE)


@lru_cache(maxsize=400_000)
def f0(tape, cases):
    """The function is in these bytes: every probe case solved with a zeroed neighbour."""
    z = bytes(len(tape))
    return all(T.score_case(S.TASK, vm.execute(tape, z, c, FROZEN["budgets"]["early"]["step_cap"], True)["outputs"], c, {}) >= 1.0 for c in cases)


def restrict(tape, tags, letters):
    return bytes(b if t in letters else 0 for b, t in zip(tape, tags))


def label(tape, tags, situ, cases):
    if not f0(tape, cases):
        return "ENV" if situ else None
    for cls, letter in (("ENDO", "P"), ("EXT", "R"), ("INS", "I")):
        if f0(restrict(tape, tags, letter), cases):
            return cls
    if not f0(restrict(tape, tags, "PRIM"), cases):
        return "ENV"
    return "OTHER"


def run_class(labels):
    if not labels:
        return "NONE"
    top = max(LABELS, key=labels.count)
    return top if 2 * labels.count(top) > len(labels) else "MIXED"


def origin(founders, cases):
    """INSERTED iff a SUPPLIED founder (transplant / seeded path) carries the function; a lucky random founder is not insertion."""
    return "INSERTED" if any(src == "S" and f0(t, cases) for t, src in founders) else "ARISEN"


def classify(rec):
    out = dict(cls="REFUSED", origin="", refused="", n_func=0, **{"n_" + k: 0 for k in LABELS})
    try:
        obs = observe.replay(rec["spec"], rec["seed"])
    except observe.Unsupported:
        out["refused"] = "UNSUPPORTED"; return out
    claimed = [(o["cell"], o["tape"], o["generation"]) for o in rec["out"]["final_population"]]
    if claimed != [(o["cell"], o["tape"].hex(), o["gen"]) for o in obs["final"]]:
        out["refused"] = "REPLAY_MISMATCH"; return out
    cases = probe_cases(rec["seed"])
    labels = [x for x in (label(o["tape"], o["tags"], o["situ"], cases) for o in obs["final"]) if x]
    out.update(cls=run_class(labels), n_func=len(labels), **{"n_" + k: labels.count(k) for k in LABELS})
    out["origin"] = origin(obs["founders"], cases) if labels else ""
    return out


# ---------------------------------------------------------------- records and forgeries
def record(arm, seed, epochs=None):
    spec = S.spec(arm, epochs)
    return {"arm": arm["name"], "seed": seed, "spec": spec, "out": E.run(spec, seed)}


def canon(rec):
    return json.dumps(rec, sort_keys=True, default=str)


def _relabel(r, claim):
    """Every stored claim says endogenous / discovered / clean; no byte, generation or physics field is touched."""
    o = r["out"]; sg = o.setdefault("signals", {}); pv = sg.setdefault("provenance", {})
    r["spec"]["init"] = "random"; r["spec"]["scheduler_reason"] = claim
    sg.update(births_endo=sg.get("births", 0), spontaneous_replication=True, inserted_lineage_replication=False)
    pv.update(world_has_inserted_material=False, births_endo_clean=sg.get("births", 0), births_endo_inserted=0,
              founders={"random": sum(pv.get("founders", {}).values()) or 1, "seeded_replicator": 0, "transplanted_lineage": 0})
    for f in o.get("founders", {}).values():
        f["origin"] = "random"
    for fo in o["final_population"]:
        fo.update(origin_class="random_only", inserted_ancestry=False, score=1.0)
    for ev in o.get("events", []):
        if ev.get("k") == "birth":
            ev.update(mech="ENDOGENOUS_COPY", ins=False)


def forge(rec, kind):
    r = copy.deepcopy(rec); fp = r["out"]["final_population"]
    if kind == "LABELS":                 # an EXTERNAL run whose stored labels claim endogenous replication
        _relabel(r, "claim:endogenous")
    elif kind == "PLANT":                # a planted population whose stored labels claim discovery
        _relabel(r, "claim:discovered")
    elif kind == "PHYS":                 # the physics the record claims is not the physics that produced its bytes
        if r["spec"]["reproduction"] == "EXTERNAL":
            r["spec"]["reproduction"] = "ENDOGENOUS_COPY"
        else:
            r["spec"].pop("transplant", None); r["spec"]["init"] = "random"
    elif kind == "TAPE":                 # a child window the parent's execution did not write
        alt = S.NH().hex() if fp[0]["tape"] != S.NH().hex() else S.H().hex()
        fp[0]["tape"] = alt
    elif kind == "GEN":                  # planted founders claim >= 10 transmissions
        for o in fp:
            o["generation"] = max(o["generation"], 12)
    return r


# ---------------------------------------------------------------- the two negative-control detectors
def b1(rec):
    """LABEL READER: the engine's own score, generation and the spec's physics label."""
    fp = rec["out"]["final_population"]; func = [o for o in fp if o.get("score", 0.0) >= 1.0]
    if not func:
        cls = "NONE"
    elif rec["spec"]["reproduction"] == "EXTERNAL":
        cls = "EXT"
    elif all(o["generation"] == 0 for o in func):
        cls = "INS"
    else:
        cls = "ENDO"
    ins = rec["out"].get("signals", {}).get("provenance", {}).get("world_has_inserted_material")
    return {"cls": cls, "origin": "" if cls == "NONE" else ("INSERTED" if ins else "ARISEN")}


def transmits(tape, cases):
    r = vm.execute(tape, bytes(len(tape)), cases[0], FROZEN["budgets"]["early"]["step_cap"], True)
    return sum(r["nbr_mask"]) >= FROZEN["copy_min_frac"] * len(tape) and f0(r["nbr_window"], cases)


def b2(rec):
    """BYTES ONLY, no replay (the C-017-T020 demand-gate reading): F0, generation, and 'writes a functional copy of itself'."""
    cases = probe_cases(rec["seed"]); labels = []
    for o in rec["out"]["final_population"]:
        t = bytes.fromhex(o["tape"])
        if f0(t, cases):
            labels.append("INS" if o["generation"] == 0 else "ENDO" if transmits(t, cases) else "EXT")
    cls = run_class(labels)
    init = [bytes.fromhex(x["tape"]) for x in rec["out"]["snapshots"][0]["organisms"]] if rec["out"].get("snapshots") else []
    return {"cls": cls, "origin": "" if cls == "NONE" else origin([(t, "S") for t in init], cases)}


# ---------------------------------------------------------------- rows
def row(rec, arm, forgery="", source=None):
    c = classify(rec); x, y = b1(rec), b2(rec)
    gt = "REFUSED" if forgery in ("PHYS", "TAPE", "GEN") else arm["gt"]
    r = dict(arm=arm["name"], gt=gt, origin_gt="" if gt == "REFUSED" else arm["origin"], seed=rec["seed"], forgery=forgery,
             b1=x["cls"], b1_origin=x["origin"], b2=y["cls"], b2_origin=y["origin"], pop=len(rec["out"]["final_population"]),
             births=rec["out"]["signals"]["births"], births_endo=rec["out"]["signals"]["births_endo"], epochs=rec["out"]["signals"]["epochs"])
    r.update(c)
    if source:
        r.update(source_cls=source["cls"], source_origin=source["origin"])
    return r


def blinded(rec):
    b = {"seed": rec["seed"], "spec": copy.deepcopy(rec["spec"]), "out": rec["out"]}
    b["spec"]["scheduler_reason"] = "blinded"
    return b


def run(part, n_for, shard=(0, 1), n_forge=N_FORGE, log=print):
    """All arms in `part`, then the forgeries built from the first n_forge records of their source arms."""
    rows = []
    for idx, arm in enumerate(S.ARMS):
        for k, sd in enumerate(S.seeds(arm["name"], part, n_for(arm["name"]))):
            if (idx + k) % shard[1] != shard[0]:
                continue
            rec = record(arm, sd)
            base = row(blinded(rec), arm)
            rows.append(base)
            for kind, src in FORGERIES.items():
                if arm["name"] in (src if isinstance(src, tuple) else (src,)) and k < n_forge:
                    rows.append(row(forge(rec, kind), arm, kind, base))
            log("%s %d %s %s n_func=%d" % (arm["name"], sd, base["cls"], base["origin"], base["n_func"]))
    return rows


def environment():
    return {"python": platform.python_version(), "host": platform.node()}


def main(argv):
    mode, prefix = argv[0], argv[1]
    shard = tuple(int(x) for x in argv[-1].split("/")) if "/" in argv[-1] else (0, 1)
    if mode == "confirm":
        from rso.z80 import freeze
        bad = freeze.mismatches()
        if bad or "--cleared-by" not in argv:
            print("REFUSED: freeze mismatch %s or no --cleared-by" % bad); return 2
        part, n_for = "confirm", lambda a: CONFIRM_N.get(a, 24)
    elif mode == "dev":
        part, n = "dev", int(argv[2]); n_for = lambda a: n
    else:
        print(__doc__); return 2
    t0 = time.time()
    rows = run(part, n_for, shard)
    path = "%s.%d-%d.jsonl.gz" % (prefix, shard[0], shard[1])
    with gzip.open(path, "wt", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    print("rows", len(rows), "sha256", sha256_hex(rows), "wall_s", int(time.time() - t0), "->", path, environment())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
