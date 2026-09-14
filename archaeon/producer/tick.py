"""One decision cycle. The only thing the loop calls.

    read fossils -> read own history -> cadence -> detect -> (signal | random)
      -> build spec -> validate -> write at most one row -> record -> return

Properties this function is built to have, in order of importance:

* **No model in the path.** Every branch is arithmetic or a database answer.
* **At most one runnable experiment per call**, and only when cadence admits.
* **Never raises for an ordinary outcome.** "Cadence refused", "no signal",
  "corpus empty" are RESULTS, returned as data. The loop must be able to run
  for weeks without an exception being how it learns something.
* **Durably records the decision, including the refusals.** A cycle that
  decided not to write and a cycle that never ran must be distinguishable in
  the record, or the loop's health is unknowable.
* **Returns cleanly.** One dict, JSON-serialisable, safe to log.
* **FIRE-AND-FORGET.** Once the row is written, tick() is done with it. It
  does not track completion, poll status, wait for Vivarium, correlate the
  resulting fossil back to "my experiment", or retry on execution failure.
  Vivarium owns the experiment from claim onward, and Archaeon's only
  persistent feedback channel is PEW -- where new fossils are simply new
  evidence on a later tick, whoever produced them.

Explicitly out of scope for this milestone and NOT imported here: Stage 0,
family F1, S17 eligibility, arm fossil semantics.
"""
from __future__ import annotations

import json
import traceback
from typing import Any, Dict, Optional

from .. import cadence as cad
from .. import fossils
from .. import config as cfg
from .. import detectors, rank
from .. import vivqueue as vq
from ..clock import iso, utc_day_str
from . import census as census_mod
from . import contract, randomgen, readers, specbuild, templates

TICK_VERSION = "archaeon.tick.v0"

#: Decision codes. Closed set, so a log can be counted without parsing prose.
WROTE_SIGNAL = "WROTE_WEAK_SIGNAL"
WROTE_RANDOM = "WROTE_RANDOM"
NO_WRITE_CADENCE = "NO_WRITE_CADENCE"
NO_WRITE_NO_CANDIDATE = "NO_WRITE_NO_CANDIDATE"
NO_WRITE_ERROR = "NO_WRITE_ERROR"


def _log_decision(conn, lane: str, decision: str, detail: Dict[str, Any],
                  experiment_id: Optional[str] = None) -> None:
    """Durably record what was decided, including the no-writes.

    Uses archaeon.cadence_log, which already exists, is append-only in
    practice, and is where cadence refusals land. Reusing it keeps one
    chronological record of this seat's decisions rather than two.
    """
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO archaeon.cadence_log "
            "(instance, decision, detail, proposal_id, lane) "
            "VALUES (%s, %s, %s::jsonb, NULL, %s)",
            (cad.instance_id(), _mapped(decision),
             json.dumps(dict(detail, tick_decision=decision,
                             experiment_id=experiment_id), default=str),
             lane))
        conn.commit()
    except Exception:                              # pragma: no cover
        conn.rollback()


#: cadence_log.decision has a CHECK constraint; tick's richer vocabulary is
#: recorded in detail.tick_decision and mapped onto the allowed set here.
_DECISION_MAP = {
    WROTE_SIGNAL: "ADMITTED", WROTE_RANDOM: "ADMITTED",
    NO_WRITE_CADENCE: "REFUSED_MIN_SEPARATION",
    NO_WRITE_NO_CANDIDATE: "REFUSED_RACE_LOST",
    NO_WRITE_ERROR: "REFUSED_RACE_LOST",
}


def selection_labels(ranked, region_ctx):
    """(source_reason, decision) from what CAUSED the selection.

    Operator ruling 2026-09-12 (fossil metabolism S1, phase 2): a fired
    detector that could not direct the draw does not make the row a
    weak-signal row -- the experiment was drawn uniformly. Before this the
    decision was WROTE_WEAK_SIGNAL whenever `ranked` was non-empty, which
    labelled every row of 2026-09-12 as fossil-informed while the draw was
    identical with and without the corpus (EVIDENCE_LINK_DRYRUN). The
    fired signal stays in source_evidence.weak_signal and selection_basis
    says weak_signal_recorded_only; only those describe what was seen."""
    if region_ctx is not None:
        return "weak_signal", WROTE_SIGNAL
    return "exploration", WROTE_RANDOM


def _mapped(d: str) -> str:
    return _DECISION_MAP.get(d, "REFUSED_RACE_LOST")


def tick(conn, config: Optional[cfg.ArchaeonConfig] = None, *,
         lookback_rows: int = 2000,
         dry_run: bool = False) -> Dict[str, Any]:
    """Perform one decision cycle. Returns a JSON-serialisable record."""
    from . import costs as _costs
    tick_meter = _costs.Meter(); tick_meter.__enter__()
    config = config or cfg.DEFAULT
    lane = config.cadence.lane
    day = utc_day_str()
    from .. import workspace as _ws
    out: Dict[str, Any] = {"tick_version": TICK_VERSION, "at": iso(),
                           "workspace": _ws.receipt(),                     # D-23: base_sha, branch, worktree_path, dirty
                           "lane": lane, "utc_day": day, "dry_run": dry_run,
                           "wrote": False, "experiment_id": None}

    # 0. the conformance gate, BEFORE any work (operator 2026-09-11) --------
    from .. import conformance as _conf
    try:
        out["conformance"] = _conf.compact(_conf.require(getattr(config, "conformance", None)))
    except _conf.ConformanceHalt as halt:
        out["conformance"] = _conf.compact(halt.record)
        out["halted"] = {"by": "conformance", "state": halt.record.get("state"), "reason": halt.record.get("reason"),
                         "attempts": halt.record.get("attempts")}
        out["decision"] = "HALTED_CONFORMANCE"
        return out

    try:
        # 1. the scientific input -----------------------------------------
        corpus = readers.recent_fossils(config.chart, lookback_rows)
        out["fossils"] = readers.fossil_summary(corpus)

        # 2. this seat's own operational history ---------------------------
        used = readers.published_spec_hashes(conn, lane)
        out["known_spec_hashes"] = len(used)

        # 3. cadence, BEFORE any work is done that could tempt a bypass ----
        vq.assert_queue_ready(conn)
        cur = conn.cursor()
        cad.take_gate(cur, lane)
        decision = vq._evaluate_cadence(cur, config.cadence)
        conn.commit()
        out["cadence"] = decision.to_json()
        if not decision.admitted:
            out["decision"] = NO_WRITE_CADENCE
            out["reason"] = decision.detail.get("refusal")
            if not dry_run:
                _log_decision(conn, lane, NO_WRITE_CADENCE, out["cadence"])
            return out

        # 4. weak signal, using the existing simple algorithm --------------
        # Harmonia's repeat blocker (2026-09-08): detectors see one row per
        # independent unit. The raw corpus is kept for Stage 0 and the census.
        agg_corpus = fossils.aggregate_repeats(corpus)
        results = detectors.run_all(agg_corpus, config.detectors)
        out["aggregation"] = agg_corpus.window.get("aggregation")
        census = detectors.eligibility_census(results)
        signals = detectors.all_signals(results)
        ranked = rank.rank(signals, config.rank_weights)
        out["census"] = {"eligible": census["detectors_eligible_names"],
                         "fired": census["detectors_fired_names"],
                         "any_eligible": census["any_eligible"]}
        out["n_signals"] = len(signals)

        # 4b. the substrate census -- the signal campaign's instrument. One
        # row per tick; failure to write it is logged, never allowed to stop a
        # proposal. Written even on dry runs? No: a dry run is not a tick.
        if not dry_run:
            try:
                row = census_mod.build(corpus, results, census, lane=lane)
                out["census_id"] = census_mod.persist(conn, row)
                out["wishlist"] = row["wishlist"]
            except Exception as exc:               # noqa: BLE001
                conn.rollback()
                out["census_error"] = "{}: {}".format(type(exc).__name__, exc)

        # 5. choose a policy ----------------------------------------------
        # A fired signal names a REGION, not an executable experiment: the
        # probe kind that would have executed it (archaeon.probe.v0) has no
        # executor and is retired. So at this milestone the signal is recorded
        # as the REASON and the experiment is still drawn from the declared
        # space. That is stated rather than hidden -- the alternative is
        # emitting a spec nothing can run.
        # The draw comes from the TEMPLATE REGISTRY. Two named policies, never
        # mixed:
        #   menu.region_directed.v0 -- when a detector fired AND an admitted
        #       region-directed template exists AND the fired region's
        #       landscape parameters are recoverable. The experiment's
        #       parameters are TAKEN FROM THE REGION: this is the step that
        #       makes a signal change what runs.
        #   menu.uniform.v0 -- the frozen random baseline, otherwise.
        # Sixteen attempts to find a spec hash this lane has not already
        # published; then give up honestly.
        region_ctx = None
        region_note = None
        if ranked:
            top = ranked[0].primary
            rp = fossils.region_params(top.regions[0]) if top.regions else None
            if rp and "length" in rp and templates.admitted(region_directed=True):
                region_ctx = {"seed_root": rp["seed_root"],
                              "length": rp["length"],
                              "world_id": rp["world_id"]}
            elif rp is None:
                region_note = "fired region has no recoverable seed_root"
            elif "length" not in rp:
                region_note = ("fired region's landscape length is {}"
                               .format("ambiguous" if "length_ambiguous" in rp
                                       else "not recorded on its experiments"))
            else:
                region_note = "no region-directed template is ADMITTED"
        drawn = None
        builder = _SpecBuilder()
        for attempt in range(16):
            d = templates.draw(lane, day, nonce=str(attempt), region=region_ctx)
            spec = builder(d["params"], template=d.get("template"))
            h = builder.spec_hash(spec)
            if h in used:
                continue
            d.update({"attempt": attempt, "spec": spec, "spec_hash": h})
            drawn = d
            break
        if drawn is None:
            out["decision"] = NO_WRITE_NO_CANDIDATE
            out["reason"] = ("every draw in 16 attempts produced a spec hash "
                             "this lane has already proposed")
            if not dry_run:
                _log_decision(conn, lane, NO_WRITE_NO_CANDIDATE,
                              {"attempts": 16})
            return out

        # PHASE 2 (operator 2026-09-12): the label describes what CAUSED the
        # selection, never what the process could see. A uniform draw stays a
        # uniform draw when fossils are visible; only a REGION-DIRECTED draw
        # (parameters taken from the fired region) is a weak-signal write.
        # Signals that fired but could not direct are still recorded in
        # source_evidence.weak_signal / selection_basis, unchanged.
        source_reason, out["decision"] = selection_labels(ranked, region_ctx)
        out["policy"] = drawn["policy"]
        out["spec_hash"] = drawn["spec_hash"]

        evidence = {
            "schema": "archaeon.tick.v0",
            "mode": source_reason,
            # Policy and template identity are what makes outcomes MEASURABLE
            # by selection policy after the fact -- the comparison against a
            # frozen random baseline that Harmonia will adjudicate. They ride
            # here, in a queue column, and Vivarium is asked to carry them into
            # the PEW producer block. Never in the sealed spec.
            "policy": {"name": drawn["policy"], "seed": drawn["seed"],
                       "seed_inputs": drawn["seed_inputs"],
                       "space": drawn["space"], "attempt": drawn["attempt"],
                       # The id names the template; the content hash pins the
                       # exact frozen version it was drawn from. A template
                       # that is later retired and replaced under a new id
                       # leaves this row re-derivable.
                       "template_content_hash":
                           drawn.get("template_content_hash"),
                       "menu": drawn.get("menu"),
                       "menu_size": drawn.get("menu_size")},
            "policy_version": "{}@{}".format(drawn["policy"], TICK_VERSION),
            "template_id": drawn.get("template_id", "bitstring.uniform.v0"),
            # WP-X6: family identity and the allocation share this draw was
            # made under. The reserve policy is INACTIVE until the operator
            # writes archaeon/policies/allocation.reserve.v0.json; until then
            # every draw is recorded as the established share.
            "family": drawn.get("family"),
            "allocation": _allocation_record(),
            # WP-X6 / design v0.1 C4: the producer's own cost receipt for this
            # decision (generation stage). Measured on this process; gpu
            # unavailable and not zero. Reconciles with the executor's vector
            # by attempt_id (the spec_hash) and stage.
            "cost_event": _cost_receipt(drawn["spec_hash"], tick_meter),
            # THREE bases, and the middle one is the honest one: a signal
            # fired but could not direct the experiment, so the reason is
            # recorded and the draw was random anyway.
            "selection_basis": ("region_directed" if region_ctx is not None
                                else ("weak_signal_recorded_only" if ranked
                                      else "random")),
            "region_direction": ({"region": region_ctx, "note": None}
                                 if region_ctx is not None
                                 else {"region": None, "note": region_note}),
            "corpus": out["fossils"],
            "eligibility_census": census,
            "weak_signal": ({"detector": ranked[0].primary.detector,
                             "signal_id": ranked[0].primary.signal_id(),
                             "regions": list(ranked[0].primary.regions),
                             "note": ("the signal is the REASON this tick "
                                      "wrote; the experiment itself is drawn "
                                      "from the declared space, because the "
                                      "probe kind that would execute a "
                                      "region-targeted proposal is retired "
                                      "and has no executor")}
                            if ranked else None),
            "authority": ("PRODUCER RECORD. This is a scheduling decision, "
                          "not a scientific claim. A fired detector means a "
                          "region may be worth interrogating again; an "
                          "absence of one means the random policy was used."),
            "upstream_selection_history": "UNKNOWN",
        }

        if dry_run:
            out["spec"] = drawn["spec"]
            out["source_evidence"] = evidence
            return out

        cand = vq.make_candidate(drawn["spec"], source_evidence=evidence)
        res = vq.submit(conn, candidates=[cand], selected_index=0,
                        source_reason=source_reason, config=config)
        out["wrote"] = True
        # A publication receipt, not a handle Archaeon will follow up on.
        out["experiment_id"] = res["selected_experiment_id"]
        out["candidate_set_id"] = res["candidate_set_id"]
        _log_decision(conn, lane, out["decision"],
                      {"spec_hash": drawn["spec_hash"],
                       "policy": drawn["policy"]},
                      experiment_id=res["selected_experiment_id"])
        return out

    except cad.CadenceRefused as exc:
        # Lost the race to a concurrent instance between evaluate and insert.
        # A scheduling outcome, never an error.
        out["decision"] = NO_WRITE_CADENCE
        out["cadence"] = exc.decision.to_json()
        out["reason"] = exc.decision.decision
        return out
    except Exception as exc:                       # noqa: BLE001
        try:
            conn.rollback()
        except Exception:                          # pragma: no cover
            pass
        out["decision"] = NO_WRITE_ERROR
        out["error"] = "{}: {}".format(type(exc).__name__, exc)
        out["traceback"] = traceback.format_exc(limit=6)
        if not dry_run:
            _log_decision(conn, lane, NO_WRITE_ERROR, {"error": out["error"]})
        return out


def _cost_receipt(attempt_id, meter):
    from . import costs
    try:
        meter.__exit__(None, None, None)
        ev = costs.CostEvent("generation", attempt_id, meter.resources())
        return ev.to_json()
    except Exception as exc:          # a receipt failure must never block a publication
        return {"error": "cost receipt unavailable: {}".format(exc)}


def _allocation_record():
    from . import allocation
    pol = allocation.load_policy()
    return {"policy_id": pol.get("policy_id"), "active": bool(pol.get("active")),
            "share": "established", "note": pol.get("note")}


class _SpecBuilder:
    """Adapter so randomgen can build and hash without importing specbuild."""

    def __call__(self, params, template=None):
        # WP-0e: build for the drawn template's kind. Without a template (the
        # legacy adapter path) the bitstring builder applies unchanged.
        if template is None:
            return specbuild.build_validated(params)
        from . import kindspec
        return kindspec.build_validated(template, params)

    @staticmethod
    def spec_hash(spec):
        return specbuild.spec_hash(spec)
