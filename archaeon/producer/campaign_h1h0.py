"""H1 three arms and H0 four cells on cegis_boolean_v1 (Track A items 7-8;
design v0.1 s5 H1/H0). Archaeon ISSUES; Vivarium executes; Harmonia analyses.

Two phases, because source failures must come from SOURCE tasks only:

  phase 1 (source)   cegis_boolean_v1 on the SOURCE tasks, both slots null,
                     witnesses recorded up to trace_bound. Its ordered
                     witnesses are the only failure pool.
  phase 2 (alpha)    packs built from phase-1 witnesses under a FROZEN,
                     seeded retrieval policy, published as
                     failure_input_set artifacts (human path), then the
                     H1 arms and H0 cells issued on the TARGET tasks.

The task split is seeded and disjoint by construction; confirmation data
never tunes retrieval (design s4 Archaeon row).

Retrieval policies (frozen, declared here, never learned):
  random_compatible   uniform over the de-duplicated pool of source witness
                      inputs; K distinct; shortfall reported.
  signature_v0        rank SOURCE tasks by agreement with the target's
                      LICENSED structural metadata (popcount bucket,
                      permutation-symmetric, self-dual, monotone), all of
                      which are recorded on every task and readable by every
                      arm. Whether that metadata is a FAIR feature is
                      Harmonia's ruling (design s5 H1: "if no fair relevance
                      feature exists yet, alpha demonstrates transport
                      only"). Until RELEVANCE_LICENSED is set by the
                      operator on that ruling, the relevant arm is planned
                      and marked WITHHELD, and the alpha is transport-only.

The component library for H0's alpha is an INSTRUMENT CONTROL (hand-built;
the design says so of its own fixtures). `extract_library()` is the
deterministic repeated-typed-subtree extractor for beta; it is derived from
phase-1 SOLUTIONS and is labelled `derived`, never confused with the control.

No contrast is computed here. G = S11 - S00 and I = S11 - S10 - S01 + S00
are Harmonia's, on the solve-fraction scale, with paired blocks.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from typing import Any, Dict, List, Optional, Sequence, Tuple

from . import costs as C
from . import specbuild

KIND = "cegis_boolean_v1"
CAMPAIGN_ID = "H1H0-1"
SEED_ROOT = 940_001
SPLIT_SEED = 940_002
RETRIEVAL_SEED = 940_003
N_BITS = 3
N_SOURCE = 24
N_TARGET = 12
K_PACK = 4                       # == seed_probe_count: the fresh arm's equal allowance
RELEVANCE_LICENSED = False       # operator sets on Harmonia's fairness ruling; see docstring
TRACE_BOUND = 32

#: Declared, not tuned (Vivarium's demonstration showed 6000 spreads the
#: task set across solved / budget / exhausted; 30000 saturates). A pilot
#: choice recorded as such; changing it is a new campaign id.
BASE_PAYLOAD = {
    "grammar_version": "proteus.boolean_grammar.v0",
    "candidate_policy": "seeded_enumeration_v1",
    "candidate_seed": SEED_ROOT,
    "max_expr_size": 5,
    "max_candidates": 100_000,
    "oracle_call_cap": 100_000,
    "vm_op_cap": 6000,
    "trace_bound": TRACE_BOUND,
    "vm_ticks": 2,
    "case_ordering": "proteus_declared",
    "termination": "first_solution",
    "seed_probe_count": K_PACK,
    "shortfall_rule": "report_and_proceed",
}

#: Hand-built: the three 2-AND subterms of MAJ3. INSTRUMENT CONTROL.
INSTRUMENT_LIBRARY = [
    {"name": "ab", "expr": ["and", ["input", 0], ["input", 1]]},
    {"name": "ac", "expr": ["and", ["input", 0], ["input", 2]]},
    {"name": "bc", "expr": ["and", ["input", 1], ["input", 2]]},
]

H1_ARMS = ("fresh", "random_pack", "relevant_pack")
H0_CELLS = ("S00", "S10", "S01", "S11")


# --------------------------------------------------------------------------
# Tasks and their licensed metadata
# --------------------------------------------------------------------------
def truth_table(fn) -> str:
    """Proteus's declared order: assignment k has input 0 as the MSB."""
    return "".join(str(fn((k >> 2) & 1, (k >> 1) & 1, k & 1)) for k in range(8))


def tt_from_int(n: int) -> str:
    return format(n, "08b")


def _eval(tt: str, a: int, b: int, c: int) -> int:
    return int(tt[(a << 2) | (b << 1) | c])


def licensed_metadata(tt: str) -> Dict[str, Any]:
    """Structural metadata recorded on EVERY task and readable by EVERY arm.
    Computed from the specification; whether an arm may RANK on it is the
    fairness ruling, not a property of this function."""
    assigns = list(itertools.product((0, 1), repeat=3))
    symmetric = all(_eval(tt, *p) == _eval(tt, *sorted(p)) for p in assigns)
    self_dual = all(_eval(tt, 1 - a, 1 - b, 1 - c) == 1 - _eval(tt, a, b, c) for a, b, c in assigns)
    monotone = all(_eval(tt, *x) <= _eval(tt, *y) for x in assigns for y in assigns
                   if all(xi <= yi for xi, yi in zip(x, y)))
    pop = tt.count("1")
    return {"n_bits": N_BITS, "popcount": pop, "popcount_bucket": ("low" if pop <= 2 else "mid" if pop <= 5 else "high"),
            "symmetric": symmetric, "self_dual": self_dual, "monotone": monotone}


def task_split(seed: int = SPLIT_SEED) -> Dict[str, List[Dict[str, Any]]]:
    """Seeded, disjoint. Constants are excluded (nothing to search for).
    SOURCE tasks feed failures; TARGET tasks are held out."""
    tables = [tt_from_int(n) for n in range(1, 255)]
    rng = random.Random(seed)
    rng.shuffle(tables)
    src, tgt = tables[:N_SOURCE], tables[N_SOURCE:N_SOURCE + N_TARGET]
    assert not set(src) & set(tgt)
    mk = lambda role, i, tt: {"task_id": "{}-{:02d}".format(role, i), "role": role, "tt": tt,  # noqa: E731
                              "licensed_metadata": licensed_metadata(tt)}
    return {"source": [mk("src", i, t) for i, t in enumerate(src)],
            "target": [mk("tgt", i, t) for i, t in enumerate(tgt)],
            "split_seed": seed, "excluded": ["00000000", "11111111"]}


# --------------------------------------------------------------------------
# Specs
# --------------------------------------------------------------------------
def spec_for(tt: str, *, pack_slot: Optional[Dict[str, Any]], lib_slot: Optional[Dict[str, Any]],
             hypothesis: str, encounter_tag: str) -> Dict[str, Any]:
    payload = dict(BASE_PAYLOAD, target_truth_table=tt, source_pack=pack_slot, component_library=lib_slot)
    return {"spec_version": 3, "world": {"seed_root": SEED_ROOT},
            "hypothesis": hypothesis,
            "prediction": None,
            "work": {"kind": KIND, "payload": payload},
            # solved is the only executor-level rule; the science is Harmonia's contrast
            "outcome_rule": {"field": "solved", "op": "==", "value": True,
                             "if_true": "SURVIVED", "if_false": "FALSIFIED",
                             "if_indeterminate": "INCONCLUSIVE", "aggregate": "first"},
            "pew": {"required": True,
                    "encounter_id": "ENC-archaeon-h1h0-" + hashlib.sha256(
                        "{}|{}|{}".format(tt, encounter_tag, SEED_ROOT).encode()).hexdigest()[:16],
                    "players": []},
            "repeat": {"count": 1, "order": "sequential", "seed_derivation": "constant",
                       "state": "reset", "budget": {"max_seconds": 300, "max_observations": 1}}}


def plan_phase1(split: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    split = split or task_split()
    rows = []
    for i, t in enumerate(split["source"], 1):
        rows.append({"index": i, "phase": 1, "family_id": "fam-H1H0-src", "arm_id": "source",
                     "task_id": t["task_id"], "tt": t["tt"], "licensed_metadata": t["licensed_metadata"],
                     "request_key": "{}-P1-{:03d}".format(CAMPAIGN_ID, i),
                     "spec": spec_for(t["tt"], pack_slot=None, lib_slot=None,
                                      hypothesis="source task {}: fresh bounded CEGIS records its ordered "
                                                 "witnesses; the failure pool for H1/H0".format(t["task_id"]),
                                      encounter_tag="src")})
    return rows


# --------------------------------------------------------------------------
# Retrieval (frozen) from phase-1 results
# --------------------------------------------------------------------------
def failure_pool(source_results: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Every witness input from every source result, with its source task.
    `source_results` items: {"task_id", "tt", "licensed_metadata", "result"}
    where result is the kind's result (needs `witnesses`)."""
    pool = []
    for sr in source_results:
        for w in sr["result"].get("witnesses", []):
            if w.get("inputs") is None:
                continue
            pool.append({"inputs": list(w["inputs"]), "source_task_id": sr["task_id"],
                         "source_tt": sr["tt"], "source_metadata": sr["licensed_metadata"],
                         "candidate_size": w.get("candidate_size")})
    return pool


def _signature_agreement(target_meta: Dict[str, Any], source_meta: Dict[str, Any]) -> int:
    return sum(int(target_meta[k] == source_meta[k]) for k in ("popcount_bucket", "symmetric", "self_dual", "monotone"))


def build_pack(pool: Sequence[Dict[str, Any]], policy: str, target: Dict[str, Any], k: int = K_PACK,
               seed: int = RETRIEVAL_SEED) -> Dict[str, Any]:
    """K DISTINCT compatible inputs under a frozen policy; shortfall reported,
    never topped up from elsewhere. Every input is re-labelled by the TARGET
    oracle inside the kind; a pack carries inputs and has nowhere to put a
    label (Vivarium's contract)."""
    if policy not in ("random_compatible", "signature_v0"):
        raise ValueError("unknown retrieval policy {!r}".format(policy))
    compat = [p for p in pool if len(p["inputs"]) == N_BITS and p["source_tt"] != target["tt"]]
    if policy == "random_compatible":
        distinct = sorted({tuple(p["inputs"]) for p in compat})
        rng = random.Random("{}|{}|{}".format(seed, target["task_id"], policy))
        rng.shuffle(distinct)
        chosen = distinct[:k]
        rationale = {"policy": policy, "pool_distinct": len(distinct)}
    else:
        ranked = sorted(compat, key=lambda p: (-_signature_agreement(target["licensed_metadata"], p["source_metadata"]),
                                               p["source_task_id"], tuple(p["inputs"])))
        chosen, seen = [], set()
        for p in ranked:
            t = tuple(p["inputs"])
            if t in seen:
                continue
            seen.add(t); chosen.append(t)
            if len(chosen) >= k:
                break
        rationale = {"policy": policy, "ranked_on": ["popcount_bucket", "symmetric", "self_dual", "monotone"],
                     "licence_status": "LICENSED" if RELEVANCE_LICENSED else "PROPOSED; Harmonia rules on fairness",
                     "top_agreement": (_signature_agreement(target["licensed_metadata"], ranked[0]["source_metadata"])
                                       if ranked else None)}
    items = [list(t) for t in chosen]
    obj = {"artifact_type": "failure_input_set", "schema_version": "1",
           "interface_id": "boolean-inputs-v1", "n_bits": N_BITS, "items": items}
    out = {"target_task_id": target["task_id"], "policy": policy, "k_requested": k, "k_actual": len(items),
           "shortfall": k - len(items), "shortfall_rule": "report_and_proceed",
           "object": obj, "retrieval_rationale": rationale, "seed": seed}
    try:
        from .contract import ensure_viv_importable
        ensure_viv_importable()
        from viv import artifacts as _a
        raw = _a.canonical_bytes(obj)
        out["raw"] = raw
        out["slot"] = {"digest": _a.digest_of(raw), "artifact_type": "failure_input_set",
                       "schema_version": "1", "codec": "canonical-json-v1",
                       "expected_bytes": len(raw), "interface_id": "boolean-inputs-v1"}
    except Exception as exc:                                     # noqa: BLE001
        out["slot"] = None
        out["slot_blocker"] = "viv.artifacts unavailable: {}".format(exc)[:160]
    return out


def library_object(components: Sequence[Dict[str, Any]], *, provenance: str) -> Dict[str, Any]:
    obj = {"artifact_type": "component_library", "schema_version": "1",
           "interface_id": "boolean-components-v1", "components": [dict(c) for c in components]}
    out = {"object": obj, "provenance": provenance,
           "instrument_control": provenance == "instrument_control"}
    try:
        from .contract import ensure_viv_importable
        ensure_viv_importable()
        from viv import artifacts as _a
        raw = _a.canonical_bytes(obj)
        out["raw"] = raw
        out["slot"] = {"digest": _a.digest_of(raw), "artifact_type": "component_library",
                       "schema_version": "1", "codec": "canonical-json-v1",
                       "expected_bytes": len(raw), "interface_id": "boolean-components-v1"}
    except Exception as exc:                                     # noqa: BLE001
        out["slot"] = None
        out["slot_blocker"] = "viv.artifacts unavailable: {}".format(exc)[:160]
    return out


def _subtrees(expr):
    yield expr
    if isinstance(expr, list):
        for e in expr[1:]:
            if isinstance(e, list):
                yield from _subtrees(e)


def _size(expr) -> int:
    return 1 + sum(_size(e) for e in expr[1:] if isinstance(e, list)) if isinstance(expr, list) else 1


def extract_library(source_results: Sequence[Dict[str, Any]], min_size: int = 3, min_count: int = 2,
                    max_components: int = 8) -> Dict[str, Any]:
    """Beta's deterministic extractor: repeated typed subtrees of the SOURCE
    solutions (parsed from the kind's canonical-JSON `solution`). Labelled
    `derived`. Ties broken by canonical JSON, so the output is replayable."""
    counts: Dict[str, int] = {}
    for sr in source_results:
        sol = sr["result"].get("solution")
        if not sol:
            continue
        expr = json.loads(sol) if isinstance(sol, str) else sol
        for st in _subtrees(expr):
            if isinstance(st, list) and st[0] != "input" and _size(st) >= min_size:
                key = json.dumps(st, sort_keys=True)
                counts[key] = counts.get(key, 0) + 1
    kept = sorted(((k, n) for k, n in counts.items() if n >= min_count), key=lambda kn: (-kn[1], kn[0]))[:max_components]
    comps = [{"name": "c{:02d}".format(i), "expr": json.loads(k), "count": n} for i, (k, n) in enumerate(kept)]
    return dict(library_object(comps, provenance="derived"), n_candidates=len(counts), n_kept=len(comps))


# --------------------------------------------------------------------------
# Phase 2 plan
# --------------------------------------------------------------------------
def plan_phase2(source_results: Sequence[Dict[str, Any]], split: Optional[Dict[str, Any]] = None,
                library: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """H1 three arms + H0 four cells on every TARGET task. Returns rows plus
    the artifacts to publish (packs and library) keyed by digest."""
    split = split or task_split()
    pool = failure_pool(source_results)
    library = library or library_object(INSTRUMENT_LIBRARY, provenance="instrument_control")
    rows: List[Dict[str, Any]] = []
    artifacts: Dict[str, Dict[str, Any]] = {}
    withheld: List[str] = []
    i = 0

    def add(family, arm, t, pack, lib, hyp):
        nonlocal i
        i += 1
        needed = [x["slot"]["digest"] for x in (pack, lib) if x and x.get("slot")]
        rows.append({"index": i, "phase": 2, "family_id": family, "arm_id": arm, "task_id": t["task_id"],
                     "tt": t["tt"], "licensed_metadata": t["licensed_metadata"],
                     "pack": (None if pack is None else {k: pack[k] for k in ("policy", "k_actual", "shortfall", "retrieval_rationale")}),
                     "library": (None if lib is None else {"provenance": lib["provenance"], "instrument_control": lib["instrument_control"]}),
                     "artifact_digests": needed,
                     "request_key": "{}-P2-{:03d}".format(CAMPAIGN_ID, i),
                     "spec": spec_for(t["tt"], pack_slot=(pack or {}).get("slot"), lib_slot=(lib or {}).get("slot"),
                                      hypothesis=hyp, encounter_tag="{}:{}".format(family, arm))})

    if library.get("slot"):
        artifacts[library["slot"]["digest"]] = library
    for t in split["target"]:
        rp = build_pack(pool, "random_compatible", t)
        sp = build_pack(pool, "signature_v0", t)
        for p in (rp, sp):
            if p.get("slot"):
                artifacts[p["slot"]["digest"]] = p
        add("fam-H1-1", "fresh", t, None, None, "H1 fresh: bounded CEGIS with an equal fresh-probe allowance")
        add("fam-H1-1", "random_pack", t, rp, None, "H1 random-compatible: the same plus K random source failure inputs")
        if RELEVANCE_LICENSED:
            add("fam-H1-1", "relevant_pack", t, sp, None, "H1 relevant: the same plus K signature-ranked source failure inputs")
        else:
            withheld.append("{}:relevant_pack".format(t["task_id"]))
        add("fam-H0-1", "S00", t, None, None, "H0 S00: neither exchange")
        add("fam-H0-1", "S10", t, rp, None, "H0 S10: failures only (random-compatible pack)")
        add("fam-H0-1", "S01", t, None, library, "H0 S01: library only")
        add("fam-H0-1", "S11", t, rp, library, "H0 S11: both")
    return {"rows": rows, "artifacts": artifacts, "withheld": withheld,
            "relevance_licensed": RELEVANCE_LICENSED, "pool_size": len(pool),
            "library_provenance": library["provenance"]}


# --------------------------------------------------------------------------
# Check and issue
# --------------------------------------------------------------------------
def check(rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    arms: Dict[str, int] = {}
    for r in rows:
        arms[r["arm_id"]] = arms.get(r["arm_id"], 0) + 1
    out: Dict[str, Any] = {"campaign": CAMPAIGN_ID, "rows": len(rows), "arms": arms,
                           "kind_registered": None, "invalid": [], "blockers": [],
                           "relevance_licensed": RELEVANCE_LICENSED,
                           "unit_of_analysis": "the target task, paired across arms/cells (one block per task); never the row"}
    from .contract import ensure_viv_importable
    ensure_viv_importable()
    from viv import kinds as vk
    k = vk.get(KIND)
    out["kind_registered"] = bool(k and k.implemented)
    if not out["kind_registered"]:
        out["blockers"].append({"lane": "vivarium", "what": "cegis_boolean_v1 is not registered in this tree"})
        return out
    for r in rows:
        try:
            specbuild.validate(r["spec"])
        except specbuild.SpecInvalid as exc:
            out["invalid"].append({"index": r["index"], "reason": str(exc)[:240]})
    if out["invalid"]:
        out["blockers"].append({"lane": "archaeon", "what": "specs rejected by Vivarium's validator", "n": len(out["invalid"])})
    out["ok_to_issue"] = not out["invalid"]
    return out


def issue(conn, rows: Sequence[Dict[str, Any]], *, schema: str, locators_by_digest: Dict[str, Dict[str, str]],
          created_by: str = "archaeon") -> Dict[str, Any]:
    """Human path. `locators_by_digest` maps each pack/library digest to
    {source_world, source_artifact} -- ADDRESSING, outside spec_hash. Every
    row carries a producer cost receipt in source_evidence."""
    c = check(rows)
    if not c.get("ok_to_issue"):
        raise RuntimeError("H1/H0 rows do not validate: {}".format(c["blockers"] or c["invalid"]))
    from viv import queue as vq
    ids = []
    with C.Meter() as m:
        for r in rows:
            loc = {d: locators_by_digest[d] for d in r["artifact_digests"]}
            ev = C.CostEvent("generation", r["request_key"], m.resources() if m.wall is not None else [])
            eid = vq.enqueue(conn, created_by=created_by, source_reason="human",
                             source_evidence={"schema": "archaeon.campaign.v0", "campaign": CAMPAIGN_ID,
                                              "mode": "human", "policy_version": "campaign.H1H0.v0",
                                              "task_id": r["task_id"], "phase": r["phase"],
                                              "licensed_metadata": r["licensed_metadata"],
                                              "pack": r.get("pack"), "library": r.get("library"),
                                              "cost_event": ev.to_json(),
                                              "selection_basis": "operator_directed_family",
                                              "upstream_selection_history": "UNKNOWN"},
                             experiment_spec=r["spec"], schema=schema, request_key=r["request_key"],
                             family_id=r["family_id"], arm_id=r["arm_id"],
                             artifact_locators=loc or None)
            ids.append(eid)
        conn.commit()
    return {"campaign": CAMPAIGN_ID, "experiment_ids": ids, "registered": len(ids)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="archaeon.producer.campaign_h1h0")
    ap.add_argument("--split", action="store_true"); ap.add_argument("--phase1", action="store_true")
    ap.add_argument("--check-phase1", action="store_true")
    a = ap.parse_args(argv)
    if a.split:
        print(json.dumps(task_split(), indent=1)); return 0
    if a.phase1:
        print(json.dumps([{k: v for k, v in r.items() if k != "spec"} for r in plan_phase1()], indent=1)); return 0
    if a.check_phase1:
        print(json.dumps(check(plan_phase1()), indent=2, default=str)); return 0
    ap.print_help(); return 1


if __name__ == "__main__":
    raise SystemExit(main())
