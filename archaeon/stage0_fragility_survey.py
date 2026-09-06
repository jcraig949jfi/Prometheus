"""STAGE 0 -- does the real substrate support the frozen fragility primitive?

A kill-gate, not a loop. It writes nothing, touches no schema, needs no
Vivarium, and contains no model. It answers exactly one prerequisite:

    Does the real Prometheus substrate contain enough observable structure
    for the frozen S17 prospective-fragility primitive to produce meaningful
    WITHIN-DIMENSION orderings at all?

If the answer is no, that is the finding, and no policy is forced onto the
data. An ordering over a population that cannot support one is not a weak
signal; it is noise wearing the shape of a decision.

--------------------------------------------------------------------------
THE INSTRUMENT IS INHERITED, NOT REIMPLEMENTED
--------------------------------------------------------------------------
S18 inherited S17 by importing it. Archaeon inherits the same artifact, and
loads it from a PINNED GIT BLOB rather than a filesystem path:

    commit 21fbeffbbcb3ae7a0e729e591688066b895eff84
    blob   0e2d654851ae11413f37f97d7087d747be4c394d   (the instrument)
    blob   261b91e6b2830d1c9adda0a8c28ae3292f2d0c74   (the frozen ledger)

Pinning by object id is stronger than importing by path: a path can change
under the reader, an object id cannot. S17/S18 live on origin/main, which is
not an ancestor of this branch, so a path import would not resolve here at all.

Three integrity checks run before any feature is computed, and the survey
refuses to proceed if any fails:

  1. the instrument source blob matches the pinned object id;
  2. the frozen ledger's ``predictor_hash`` is RECOMPUTED from the predictor
     object and must equal 0106e035868bbe10..., i.e. the predictor being used
     is byte-identical to the one that was evaluated out-of-sample;
  3. a POSITIVE CONTROL: the imported ``features()`` is run on a claim from
     S17's own generator. This distinguishes "zero eligible because the corpus
     lacks structure" from "zero eligible because this adapter is broken" --
     which would otherwise look identical and is the obvious way for a
     kill-gate to produce a false negative.

--------------------------------------------------------------------------
THE FROZEN ARTIFACT WINS OVER THE NARRATIVE
--------------------------------------------------------------------------
Directions are read from the ledger, never from prose. The ledger says
``rel_se: higher_is_fragile = false`` and ``serial_ac: higher_is_fragile =
false`` (LOWER is fragile), while S17's commit narrative reads as though
higher serial dependence predicts unit fragility. S18's scorer applies
``score = v if higher_is_fragile else -v``, so the direction is load-bearing:
inverted, the policy is anti-predictive. This survey uses the LEDGER and
reports the discrepancy for Harmonia to reconcile. It does not alter the
frozen artifact to make prose agree.

--------------------------------------------------------------------------
WHAT A CLAIM-UNIT IS, AND WHY THAT IS THE HARD PART
--------------------------------------------------------------------------
S17's ``features(cl)`` requires ``cl["A"]`` and ``cl["B"]``: TWO ARMS, each a
list of worlds, each world an ordered trajectory. ``hedges`` calls
``statistics.variance`` on the per-arm world means, so each arm needs at least
two worlds with non-zero spread. There is no single-arm mode: passing an empty
B raises, and every one of the five dimensions is defined over both arms.

So a claim-unit needs a CONTRAST, and the contrast has to come from the record
rather than from Archaeon. Three arm rules are tried, each explicit and named.
None of them invents a split: a rule that halved a group arbitrarily would be
manufacturing the comparison this survey is supposed to discover.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import os
import sqlite3
import statistics
import subprocess
import sys
import types
from typing import Any, Dict, List, Optional, Tuple

# ---- pinned frozen artifact ------------------------------------------------
S17_COMMIT = "21fbeffbbcb3ae7a0e729e591688066b895eff84"
S17_SRC_PATH = "roles/Harmonia/science/s17_prospective_fragility.py"
S17_LEDGER_PATH = "roles/Harmonia/science/ledgers/s17_fragility.json"
S17_SRC_BLOB = "0e2d654851ae11413f37f97d7087d747be4c394d"
S17_LEDGER_BLOB = "261b91e6b2830d1c9adda0a8c28ae3292f2d0c74"
S17_PREDICTOR_HASH = ("0106e035868bbe10ef177c8e88a2dad79bd8364c"
                      "b5b684844cd018b5f1dada73")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SFE_DB = os.environ.get(
    "ARCHAEON_SFE_DB",
    os.path.join(REPO_ROOT, "SerendipityFoundry",
                 "SerendipityFoundryEngine", "var", "engine.db"))

# Epistemic types. Written as VALUES, never by omission: an absent field reads
# as "nothing to report", which is precisely the reassuring negative the
# S14/S15 boundary forbids.
OBSERVED = "OBSERVED"
INFERRED = "INFERRED"
UNKNOWN = "UNKNOWN"


class InstrumentError(Exception):
    """The frozen instrument could not be loaded or failed verification."""


# ==========================================================================
# 1. Load and verify the frozen instrument
# ==========================================================================
def _git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", REPO_ROOT] + list(args))


def load_frozen_s17() -> Tuple[types.ModuleType, Dict[str, Any],
                               Dict[str, Any]]:
    """Import S17 from the pinned blob and verify it end to end."""
    prov: Dict[str, Any] = {"commit": S17_COMMIT,
                            "source_path": S17_SRC_PATH,
                            "ledger_path": S17_LEDGER_PATH}
    try:
        src = _git("cat-file", "blob", S17_SRC_BLOB)
        led = _git("cat-file", "blob", S17_LEDGER_BLOB)
    except Exception as exc:
        raise InstrumentError(
            "cannot read the pinned S17 blobs from git ({}). The frozen "
            "instrument is the scientific provenance; this survey will not "
            "substitute a copied formula for it.".format(exc))

    prov["source_blob"] = S17_SRC_BLOB
    prov["ledger_blob"] = S17_LEDGER_BLOB
    prov["source_sha256"] = hashlib.sha256(src).hexdigest()
    prov["ledger_sha256"] = hashlib.sha256(led).hexdigest()

    ledger = json.loads(led.decode("utf-8"))
    predictor = ledger["predictor"]

    # CHECK 2: recompute the predictor hash exactly as S17 computed it.
    recomputed = hashlib.sha256(
        json.dumps(predictor, sort_keys=True).encode()).hexdigest()
    prov["predictor_hash_recorded"] = ledger["predictor_hash"]
    prov["predictor_hash_recomputed"] = recomputed
    prov["predictor_hash_verified"] = (recomputed == ledger["predictor_hash"]
                                       == S17_PREDICTOR_HASH)
    if not prov["predictor_hash_verified"]:
        raise InstrumentError(
            "frozen predictor hash mismatch: recorded {}, recomputed {}, "
            "expected {}. The predictor in hand is not the one that was "
            "evaluated out of sample."
            .format(ledger["predictor_hash"][:16], recomputed[:16],
                    S17_PREDICTOR_HASH[:16]))

    # Import without executing main().
    spec = importlib.util.spec_from_loader("frozen_s17", loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__file__ = "git:{}:{}".format(S17_COMMIT[:12], S17_SRC_PATH)
    sys.modules["frozen_s17"] = mod
    try:
        exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    except Exception as exc:
        raise InstrumentError("frozen S17 failed to import: {}".format(exc))
    for fn in ("features", "hedges", "d_base", "make_claim", "DIMS"):
        if not hasattr(mod, fn):
            raise InstrumentError(
                "frozen S17 is missing {!r}; the pinned blob is not the "
                "expected instrument".format(fn))
    prov["dims"] = list(mod.DIMS)
    prov["import_method"] = "pinned git blob, exec into a synthetic module"
    return mod, ledger, prov


def positive_control(s17) -> Dict[str, Any]:
    """CHECK 3: run the frozen features on S17's OWN synthetic claim.

    Without this, a zero-eligibility result cannot be attributed: a broken
    adapter and an unsupportive corpus produce the same number.
    """
    import random
    rng = random.Random(20260905)
    cl = s17.make_claim(s17.KINDS[0], rng, nw=6, nobs=10, effect=0.5)
    f = s17.features(cl)
    needed = ("rel_se", "kurtosis", "within_between", "serial_ac")
    ok = all(k in f and isinstance(f[k], float) and f[k] == f[k]
             for k in needed)
    return {"ran": True, "ok": bool(ok),
            "claim_shape": {"arms": 2, "worlds_per_arm": 6, "obs_per_world": 10},
            "features": {k: round(f[k], 6) for k in needed},
            "note": ("proves the imported instrument computes on a WELL-FORMED "
                     "claim, so any zero-eligibility below is a property of "
                     "the corpus and not of this adapter")}


# ==========================================================================
# 2. Read the real corpus
# ==========================================================================
def read_corpus(db_path: str) -> Dict[str, Any]:
    """Scored observations grouped by world, in ledger order, with the
    evidence class of every observation retained."""
    if not os.path.exists(db_path):
        return {"error": "sfe db not found: {}".format(db_path)}
    # Same declared population as the producer's reader (consumer contract
    # s2): one transaction, schema guard, declared client names, engine-
    # attested evidence only. The GATE LOGIC below is untouched; only the
    # population it is asked about is now stated rather than pooled.
    from . import config as _cfg
    ten = _cfg.DEFAULT.tenancy
    uri = "file:{}?mode=ro".format(db_path.replace("?", "%3f"))
    conn = sqlite3.connect(uri, uri=True, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("BEGIN")
        have = conn.execute("SELECT value FROM meta WHERE key='schema_version'"
                            ).fetchone()
        have_v = int(have[0]) if have else None
        if have_v is None or have_v > ten.expected_schema_version:
            conn.execute("COMMIT")
            return {"error": "sfe schema_version {} newer than reader ({})"
                             .format(have_v, ten.expected_schema_version)}
        clients = conn.execute("SELECT client_id, name FROM clients").fetchall()
        admitted_ids = [c["client_id"] for c in clients
                        if c["name"] in ten.include_client_names]
        tenancy = {"admitted_client_names":
                       sorted({c["name"] for c in clients
                               if c["name"] in ten.include_client_names}),
                   "evidence_classes": list(ten.evidence_classes),
                   "schema_version": have_v, "snapshot": "single transaction"}
        worlds: Dict[str, List[float]] = collections.defaultdict(list)
        ev_class: Dict[str, collections.Counter] = collections.defaultdict(
            collections.Counter)
        anchors: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)
        n_obs = n_scored = 0
        for r in conn.execute(
                "SELECT o.obs_id, o.world_id, o.content, o.evidence_class, "
                "       o.exp_id, o.created_seq "
                "  FROM observations o JOIN worlds w ON w.world_id = o.world_id "
                " WHERE o.evidence_class IN ({ev}) AND w.client_id IN ({cl}) "
                " ORDER BY o.created_seq".format(
                    ev=",".join("?" * len(ten.evidence_classes)),
                    cl=",".join("?" * max(len(admitted_ids), 1))),
                list(ten.evidence_classes)
                + (admitted_ids or ["<no admitted client>"])):
            n_obs += 1
            try:
                d = json.loads(r["content"])
            except Exception:
                continue
            if not isinstance(d, dict):
                continue
            v = d.get("score")
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                continue
            n_scored += 1
            wid = r["world_id"]
            worlds[wid].append(float(v))
            ev_class[wid][r["evidence_class"]] += 1
            anchors[wid].append({"obs_id": r["obs_id"], "exp_id": r["exp_id"],
                                 "created_seq": int(r["created_seq"])})
        meta = {}
        for r in conn.execute("SELECT world_id, topology_group, "
                              "parent_world_id FROM worlds"):
            meta[r["world_id"]] = {"topology_group": r["topology_group"],
                                   "parent_world_id": r["parent_world_id"]}
    finally:
        conn.close()
    return {"worlds": dict(worlds), "meta": meta,
            "evidence_class": {k: dict(v) for k, v in ev_class.items()},
            "anchors": dict(anchors), "tenancy": tenancy,
            "observations_total": n_obs, "observations_scored": n_scored}


# ==========================================================================
# 3. Arm rules. Each is explicit and named. NONE invents a split.
# ==========================================================================
MIN_WORLDS_PER_ARM = 2      # statistics.variance needs >= 2 points
MIN_OBS_PER_WORLD = 4       # S17's lag-1 autocorrelation needs len(w) > 3


def _usable(corpus, min_obs=MIN_OBS_PER_WORLD):
    return {w: v for w, v in corpus["worlds"].items() if len(v) >= min_obs}


def rule_topology_split(corpus, min_obs=MIN_OBS_PER_WORLD):
    """Worlds of one topology_group, split into two arms by ledger order.

    Requires >= 2*MIN_WORLDS_PER_ARM usable worlds in the group. The split is
    deterministic (sorted world_id) and is a PARTITION OF AN EXISTING GROUP,
    not an invented contrast between unrelated worlds -- but it is still the
    weakest of the three rules and is labelled INFERRED, because SFE does not
    say these halves were ever meant to be compared.
    """
    usable = _usable(corpus, min_obs)
    groups = collections.defaultdict(list)
    for w in usable:
        tg = corpus["meta"].get(w, {}).get("topology_group")
        if tg:
            groups[tg].append(w)
    units, excl = [], []
    for tg, ws in sorted(groups.items()):
        ws = sorted(ws)
        if len(ws) < 2 * MIN_WORLDS_PER_ARM:
            excl.append({"group": tg, "usable_worlds": len(ws),
                         "reason": "fewer than {} usable worlds; cannot form "
                                   "two arms of {}".format(
                                       2 * MIN_WORLDS_PER_ARM,
                                       MIN_WORLDS_PER_ARM)})
            continue
        half = len(ws) // 2
        units.append({"unit_id": "topo:{}".format(tg), "rule": "TOPOLOGY_SPLIT",
                      "arm_a": ws[:half], "arm_b": ws[half:],
                      "contrast_provenance": INFERRED})
    return units, excl


def rule_fork(corpus, min_obs=MIN_OBS_PER_WORLD):
    """Parent world vs its forked children -- a contrast SFE actually records.

    Strongest provenance of the three (WORLD_FORKED is a ledger event), but the
    parent arm is a single world, so it needs >= MIN_WORLDS_PER_ARM parents
    sharing a fork point to be usable. Reported honestly rather than bent.
    """
    usable = _usable(corpus, min_obs)
    kids = collections.defaultdict(list)
    for w in usable:
        p = corpus["meta"].get(w, {}).get("parent_world_id")
        if p:
            kids[p].append(w)
    units, excl = [], []
    for p, ks in sorted(kids.items()):
        if p not in usable:
            excl.append({"parent": p, "usable_children": len(ks),
                         "reason": "parent world has no usable scored "
                                   "observations"})
            continue
        if len(ks) < MIN_WORLDS_PER_ARM or 1 < MIN_WORLDS_PER_ARM:
            excl.append({"parent": p, "usable_children": len(ks),
                         "reason": "parent arm holds 1 world; hedges() needs "
                                   "variance over >= {} worlds per arm"
                                   .format(MIN_WORLDS_PER_ARM)})
            continue
        units.append({"unit_id": "fork:{}".format(p), "rule": "FORK",
                      "arm_a": [p], "arm_b": sorted(ks),
                      "contrast_provenance": OBSERVED})
    return units, excl


def rule_spec_arm(corpus, db_path, min_obs=MIN_OBS_PER_WORLD):
    """Worlds partitioned by an explicit `spec.arm` in the experiment.

    The only rule where the record ITSELF declares the contrast, so its
    provenance is OBSERVED.
    """
    usable = _usable(corpus, min_obs)
    uri = "file:{}?mode=ro".format(db_path.replace("?", "%3f"))
    conn = sqlite3.connect(uri, uri=True)
    try:
        by_group = collections.defaultdict(lambda: collections.defaultdict(set))
        for wid, spec in conn.execute("SELECT world_id, spec FROM experiments"):
            if wid not in usable:
                continue
            try:
                s = json.loads(spec)
            except Exception:
                continue
            if isinstance(s, dict) and "arm" in s:
                tg = corpus["meta"].get(wid, {}).get("topology_group") or "<none>"
                by_group[tg][str(s["arm"])].add(wid)
    finally:
        conn.close()
    units, excl = [], []
    for tg, arms in sorted(by_group.items()):
        big = sorted(a for a, ws in arms.items()
                     if len(ws) >= MIN_WORLDS_PER_ARM)
        if len(big) < 2:
            excl.append({"group": tg, "arms_seen": len(arms),
                         "arms_with_enough_worlds": len(big),
                         "reason": "fewer than two arms have {} usable worlds"
                                   .format(MIN_WORLDS_PER_ARM)})
            continue
        units.append({"unit_id": "arm:{}".format(tg), "rule": "SPEC_ARM",
                      "arm_a": sorted(arms[big[0]]),
                      "arm_b": sorted(arms[big[1]]),
                      "contrast_provenance": OBSERVED})
    if not by_group:
        excl.append({"group": None, "reason": "no experiment on any usable "
                                              "world carries spec.arm"})
    return units, excl


ARM_RULES = ("TOPOLOGY_SPLIT", "FORK", "SPEC_ARM")


# ==========================================================================
# 4. Features over eligible units
# ==========================================================================
def build_claim(unit, corpus):
    """Shape a unit into S17's claim structure. Never pads, never invents."""
    return {"kind": unit["unit_id"],
            "A": [corpus["worlds"][w] for w in unit["arm_a"]],
            "B": [corpus["worlds"][w] for w in unit["arm_b"]]}


def unit_evidence_class(unit, corpus) -> str:
    seen = collections.Counter()
    for w in unit["arm_a"] + unit["arm_b"]:
        seen.update(corpus["evidence_class"].get(w, {}))
    if not seen:
        return UNKNOWN
    if len(seen) == 1:
        return next(iter(seen))
    return "MIXED({})".format(",".join(
        "{}={}".format(k, v) for k, v in sorted(seen.items())))


def survey(db_path: str = DEFAULT_SFE_DB,
           min_obs: int = MIN_OBS_PER_WORLD) -> Dict[str, Any]:
    s17, ledger, prov = load_frozen_s17()
    control = positive_control(s17)
    if not control["ok"]:
        raise InstrumentError(
            "positive control FAILED: the frozen features did not compute on "
            "S17's own claim. Any eligibility result below would be "
            "uninterpretable.")

    corpus = read_corpus(db_path)
    if "error" in corpus:
        return {"error": corpus["error"], "instrument": prov}

    rules = ledger["predictor"]["rules"]
    usable = _usable(corpus, min_obs)

    units: List[Dict[str, Any]] = []
    exclusions: Dict[str, Any] = {}
    u, e = rule_topology_split(corpus, min_obs)
    units += u
    exclusions["TOPOLOGY_SPLIT"] = e
    u, e = rule_fork(corpus, min_obs)
    units += u
    exclusions["FORK"] = e
    u, e = rule_spec_arm(corpus, db_path, min_obs)
    units += u
    exclusions["SPEC_ARM"] = e

    # ---- features on whatever survived --------------------------------
    rows = []
    for unit in units:
        cl = build_claim(unit, corpus)
        try:
            f = s17.features(cl)
        except Exception as exc:
            exclusions.setdefault("FEATURE_ERROR", []).append(
                {"unit_id": unit["unit_id"], "reason": str(exc)[:200]})
            continue
        rows.append({"unit_id": unit["unit_id"], "rule": unit["rule"],
                     "contrast_provenance": unit["contrast_provenance"],
                     "evidence_class": unit_evidence_class(unit, corpus),
                     "arm_a_worlds": unit["arm_a"], "arm_b_worlds": unit["arm_b"],
                     "n_worlds_per_arm": [len(unit["arm_a"]),
                                          len(unit["arm_b"])],
                     "features": {k: f[k] for k in
                                  ("rel_se", "kurtosis", "within_between",
                                   "serial_ac", "n", "abs_d", "ci_width")}})

    # ---- per-dimension eligibility + spread ---------------------------
    dims = {}
    for dim in s17.DIMS:
        r = rules[dim]
        feat = r["feature"]
        if not feat:
            dims[dim] = {"feature": None, "rule": "NO_RULE",
                         "eligible_units": 0, "epistemic": UNKNOWN,
                         "reason": ("frozen predictor holds NO RULE for this "
                                    "dimension (0 fragile cases on dev). This "
                                    "is UNKNOWN, not evidence of robustness, "
                                    "and its budget must not be reallocated."),
                         "ordering_meaningful": False}
            continue
        vals = [x["features"][feat] for x in rows if feat in x["features"]]
        d = {"feature": feat, "higher_is_fragile": r["higher_is_fragile"],
             "dev_auc": r["dev_auc"], "eligible_units": len(vals),
             "epistemic": INFERRED}
        if len(vals) >= 2:
            lo, hi = min(vals), max(vals)
            sd = statistics.pstdev(vals)
            med = statistics.median(vals)
            d.update({"min": lo, "max": hi, "median": med, "sd": sd,
                      "distinct_values": len(set(round(v, 12) for v in vals)),
                      "spread_ratio": (hi - lo) / (abs(med) + 1e-12)})
            # An ordering is only meaningful if the values actually differ.
            d["ordering_meaningful"] = bool(
                d["distinct_values"] >= 2 and sd > 0)
        else:
            d.update({"ordering_meaningful": False,
                      "reason": "fewer than 2 eligible units; an ordering "
                                "over <2 items carries no information"})
        dims[dim] = d

    # ---- kill condition, evaluated explicitly -------------------------
    ruled = [k for k, v in dims.items() if v.get("feature")]
    orderable = [k for k in ruled if dims[k].get("ordering_meaningful")]
    kill = {
        "condition": ("STAGE 0 PASSES iff at least one ruled dimension has "
                      ">= 2 eligible claim-units AND non-zero spread in its "
                      "frozen feature, so a within-dimension ordering "
                      "distinguishes at least two units."),
        "ruled_dimensions": len(ruled),
        "dimensions_with_meaningful_ordering": len(orderable),
        "orderable_dimensions": sorted(orderable),
        "eligible_claim_units": len(rows),
        "verdict": "PASS" if orderable else "KILL",
    }
    if not orderable:
        kill["finding"] = (
            "The real substrate does not currently support the frozen "
            "prospective-fragility primitive. Stage 1 must not be built on it "
            "yet. This is a statement about CORPUS STRUCTURE, not about "
            "whether fragility exists or whether the S17 rules transport.")

    return {
        "stage": "archaeon.stage0.fragility_survey.v0",
        "instrument": prov,
        "positive_control": control,
        "frozen_rules": {k: {"feature": v["feature"],
                             "higher_is_fragile": v["higher_is_fragile"],
                             "dev_auc": v["dev_auc"]}
                         for k, v in rules.items()},
        "narrative_ledger_discrepancy": {
            "status": "FLAGGED_TO_HARMONIA_UNRESOLVED",
            "detail": ("S17's commit narrative reads as though higher serial "
                       "dependence predicts unit fragility; the frozen ledger "
                       "sets serial_ac.higher_is_fragile=false (LOWER is "
                       "fragile), and rel_se likewise. The scorer applies "
                       "score = v if higher_is_fragile else -v, so an "
                       "inverted direction makes the policy anti-predictive. "
                       "THIS SURVEY USES THE LEDGER. The frozen artifact is "
                       "not altered to make prose agree."),
        },
        "corpus": {
            "source": db_path,
            "observations_total": corpus["observations_total"],
            "observations_scored": corpus["observations_scored"],
            "worlds_with_scored_observations": len(corpus["worlds"]),
            "worlds_usable": len(usable),
            "min_obs_per_world": min_obs,
            "evidence_class_totals": _ev_totals(corpus),
            "tenancy": corpus.get("tenancy"),
            "epistemic": OBSERVED,
        },
        "arm_rules": {
            "min_worlds_per_arm": MIN_WORLDS_PER_ARM,
            "rules_tried": list(ARM_RULES),
            "units_found": {r: sum(1 for x in units if x["rule"] == r)
                            for r in ARM_RULES},
        },
        "exclusions": exclusions,
        "claim_units": rows,
        "dimensions": dims,
        "kill_gate": kill,
        "upstream_selection_history": {
            "value": UNKNOWN,
            "note": ("S14/S15: selection performed upstream of submission can "
                     "be information-theoretically absent from the fossil "
                     "record. Every feature below is conditioned on a "
                     "SUBMITTED sample whose selection history is unobservable. "
                     "This field is written on every survey as a VALUE. Its "
                     "presence is not a caveat and its absence would be a "
                     "reassuring negative."),
        },
    }


def _ev_totals(corpus) -> Dict[str, int]:
    tot = collections.Counter()
    for w, c in corpus["evidence_class"].items():
        tot.update(c)
    return dict(tot)


# ==========================================================================
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="archaeon.stage0_fragility_survey")
    ap.add_argument("--db", default=DEFAULT_SFE_DB)
    ap.add_argument("--min-obs", type=int, default=MIN_OBS_PER_WORLD)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)

    r = survey(a.db, a.min_obs)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(r, fh, indent=1, default=str)
    if a.json:
        print(json.dumps(r, indent=1, default=str))
        return 0

    i, k = r["instrument"], r["kill_gate"]
    print("=" * 74)
    print("ARCHAEON STAGE 0 -- prospective-fragility survey of the real corpus")
    print("=" * 74)
    print("  frozen instrument   git {}:{}".format(i["commit"][:12],
                                                   os.path.basename(i["source_path"])))
    print("  source blob         {}".format(i["source_blob"]))
    print("  predictor hash      {}  VERIFIED={}".format(
        i["predictor_hash_recomputed"][:32], i["predictor_hash_verified"]))
    print("  positive control    {}".format(
        "PASS" if r["positive_control"]["ok"] else "FAIL"))
    c = r["corpus"]
    print("\n  corpus              {} observations, {} scored, {} worlds "
          "scored, {} usable (>= {} obs)".format(
              c["observations_total"], c["observations_scored"],
              c["worlds_with_scored_observations"], c["worlds_usable"],
              c["min_obs_per_world"]))
    print("  evidence class      {}".format(c["evidence_class_totals"]))
    print("\n  ARM RULES (a claim needs TWO arms of >= {} worlds)".format(
        MIN_WORLDS_PER_ARM))
    for rule, n in r["arm_rules"]["units_found"].items():
        print("    %-16s %d claim-units" % (rule, n))
        for ex in r["exclusions"].get(rule, [])[:2]:
            print("        excluded: %s" % ex.get("reason", "")[:80])
    print("\n  DIMENSIONS (frozen rules; directions from the LEDGER)")
    for dim, d in r["dimensions"].items():
        if not d.get("feature"):
            print("    %-10s NO_RULE  -> %s" % (dim, d["epistemic"]))
            continue
        print("    %-10s <- %-15s eligible=%d  ordering_meaningful=%s"
              % (dim, d["feature"], d["eligible_units"],
                 d.get("ordering_meaningful")))
        if d.get("reason"):
            print("               %s" % d["reason"][:78])
    print("\n  KILL GATE: %s" % k["verdict"])
    print("    %s" % k["condition"])
    print("    ruled dimensions %d | orderable %d | eligible claim-units %d"
          % (k["ruled_dimensions"], k["dimensions_with_meaningful_ordering"],
             k["eligible_claim_units"]))
    if k.get("finding"):
        print("\n    FINDING: %s" % k["finding"])
    print("\n  upstream selection history: %s"
          % r["upstream_selection_history"]["value"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
