"""Freeze the corpus alongside the orders.

The operator's tightening for M-SIGNAL: both policies must use the SAME
recorded corpus snapshot and the SAME eligible candidate universe, and both
full orders are committed before anything executes. That makes the first
campaign a precise test of selection from EXISTING fossil information;
adapting to results as they arrive is a different experiment, later.

A FrozenUniverse is the object that pins all of it:

    corpus_hash      what was read (rows AND metric values, per fossils.Corpus)
    universe_hash    the ordered list of candidate ids, hashed
    candidates       (candidate_id, template_id, region or None, params)
    orders           {policy_version: [candidate_id, ...]}  -- FULL orders
    frozen_at, seed_inputs

Nothing here executes or writes to the queue. ``register_orders`` hands each
policy's order to ``vivqueue.submit`` as a candidate set with the first
``budget`` retained... no: with EVERY candidate registered and the ones beyond
the budget cancelled, so the alternatives are class-A in the queue (E6 carries
them into SFE ``selection`` families and the exported evidence).
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional, Sequence

from ..clock import iso


def _h(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)
        .encode("utf-8")).hexdigest()


def candidate_id(template_id: str, params: Dict[str, Any],
                 region: Optional[Dict[str, Any]]) -> str:
    return "cand:" + _h({"t": template_id, "p": params, "r": region})[7:23]


def freeze(corpus, candidates: Sequence[Dict[str, Any]],
           orders: Dict[str, Sequence[str]], *,
           seed_inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Pin corpus + universe + every policy's full order into one hashed
    record. Refuses an order that names a candidate outside the universe or
    omits one inside it: a partial order is a hidden second selection."""
    ids = [c["candidate_id"] for c in candidates]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate candidate ids in the universe")
    uni = set(ids)
    for pol, order in orders.items():
        if set(order) != uni or len(order) != len(ids):
            raise ValueError(
                "order for {} is not a permutation of the universe; a partial "
                "or extended order is a hidden second selection".format(pol))
    rec = {
        "schema": "archaeon.frozen_universe.v0",
        "frozen_at": iso(),
        "corpus_hash": corpus.corpus_hash(),
        "corpus_rows": len(corpus.rows),
        "corpus_tenancy": (corpus.window or {}).get("tenancy"),
        "universe_hash": _h(ids),
        "universe_size": len(ids),
        "candidates": list(candidates),
        "orders": {pol: list(order) for pol, order in orders.items()},
        "seed_inputs": dict(seed_inputs),
    }
    rec["freeze_hash"] = _h({k: v for k, v in rec.items() if k != "frozen_at"})
    return rec


def verify(rec: Dict[str, Any]) -> bool:
    body = {k: v for k, v in rec.items() if k not in ("frozen_at", "freeze_hash")}
    return _h(body) == rec.get("freeze_hash")


def register_orders(conn, rec: Dict[str, Any], *, budget: int,
                    lane_prefix: str, spec_builder, config_factory) -> Dict[str, Any]:
    """Commit every policy's FULL order to the queue before execution.

    For each policy: one lane, one candidate set holding the whole universe in
    the policy's order; the first ``budget`` retained (queued), the rest
    cancelled. Cancelled rows are the alternatives -- the class-A trace of
    what was NOT chosen -- and E6 carries them into SFE selection families.
    """
    from .. import vivqueue as vq
    out: Dict[str, Any] = {"freeze_hash": rec["freeze_hash"], "policies": {}}
    by_id = {c["candidate_id"]: c for c in rec["candidates"]}
    for pol, order in rec["orders"].items():
        lane = "{}-{}".format(lane_prefix, pol.replace(".", "-").replace("@", "-"))
        cands = []
        for cid in order:
            c = by_id[cid]
            spec = spec_builder(c["params"])
            cands.append(vq.make_candidate(
                spec, request_key="{}:{}:{}".format(rec["freeze_hash"][7:19], pol, cid),
                source_evidence={"schema": "archaeon.msignal.v0",
                                 "policy_version": pol,
                                 "template_id": c["template_id"],
                                 "candidate_id": cid,
                                 "region": c.get("region"),
                                 "freeze_hash": rec["freeze_hash"],
                                 "corpus_hash": rec["corpus_hash"],
                                 "universe_hash": rec["universe_hash"],
                                 "rank_in_order": order.index(cid),
                                 "budget": budget,
                                 "upstream_selection_history": "UNKNOWN"}))
        # vivqueue.submit selects ONE; here the first `budget` are all
        # selected. Register in budget-sized chunks each selecting one and the
        # remainder as a single all-cancelled set would misrepresent the
        # order, so register the whole order as one set and select the head:
        res = vq.submit(conn, candidates=cands, selected_index=0,
                        source_reason="human", created_by="archaeon",
                        config=config_factory(lane),
                        candidate_set_id="cs-{}-{}".format(rec["freeze_hash"][7:19], pol))
        out["policies"][pol] = {"lane": lane, "candidate_set_id": res["candidate_set_id"],
                                "registered": res["registered"],
                                "selected": res["selected_experiment_id"],
                                "cancelled": len(res["cancelled_experiment_ids"]),
                                "note": ("v0 registers the full order and selects "
                                         "its head; budget>1 release is the "
                                         "operator's, one head per cadence slot")}
    return out
