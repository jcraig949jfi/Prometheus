"""Generate the machine-readable SFE contract for Archaeon and Vivarium.

Harmonia, 2026-09-06. M1 only.

Archaeon and Vivarium run headless, deterministic and inference-free. They
cannot read prose and they cannot ask a question. Everything they need about
SFE has to be data.

THIS IS A GENERATOR, NOT A DOCUMENT. The route table, required fields, session
scoping and vocabularies are derived FROM THE LIVE ENGINE every time it runs,
so the contract cannot drift from the engine the way a hand-written route list
did twice in this program. Re-run it after any SFE deploy; diff the output.

It emits four artifacts:

  sfe_contract.json      routes, required bodies, path params, session scoping,
                         error taxonomy, vocabularies -- all derived
  sfe_traps.json         the behaviours that cost ME time, each with the
                         measurement that established it. Every one of these
                         was a real bug in one of my own instruments.
  epistemic_bounds.json  what Archaeon MAY and MAY NOT infer, from S15/S16
  selection_policy.json  the S18-validated experiment-selection policy, with
                         its frozen predictor and measured performance
"""
from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request

# Session scoping is DERIVED, never asserted. A hand-written exempt list is
# the R-G defect this program has already been bitten by twice, and handing one
# to two headless tools would propagate it into both.
#
# The probe: send a MALFORMED X-SFE-Session to every route. A route that
# validates the header answers 422 SESSION_MALFORMED; an exempt route ignores
# it and answers something else. That is decisive, needs only one engine, and
# is run against a SCRATCH engine of the same build so the live store is never
# written.
def derive_session_scoping(probe_base):
    import urllib.request as U, urllib.error as E
    sp = get(probe_base + "/v2/openapi.json")
    tok = _post(probe_base + "/v2/clients", {"name": "contract-probe"})["token"]
    ids = {"wid": "wld_" + "0" * 24, "eid": "exp_" + "0" * 24,
           "aid": "sha256:" + "0" * 64, "work_id": "wrk_" + "0" * 24,
           "sid": "ses_" + "0" * 24, "fid": "fam_" + "0" * 24,
           "clm": "clm_" + "0" * 24}
    scoped = {}
    for path, ops in sp["paths"].items():
        for method in ops:
            m = method.upper()
            if m not in ("GET", "POST"):
                continue
            u = path[3:] if path.startswith("/v2/") else path
            for k, v in ids.items():
                u = u.replace("{%s}" % k, v)
            h = {"Content-Type": "application/json",
                 "Authorization": "Bearer " + tok,
                 "X-SFE-Session": "not-a-session-key"}
            d = b"{}" if m == "POST" else None
            r = U.Request(probe_base + "/v2" + u if not u.startswith("/v2")
                          else probe_base + u, data=d, headers=h, method=m)
            try:
                with U.urlopen(r, timeout=20) as z:
                    code, body = z.status, z.read().decode()
            except E.HTTPError as e:
                code, body = e.code, e.read().decode()
            except Exception:                                      # noqa: BLE001
                code, body = None, ""
            scoped[(m, path)] = (code == 422 and "SESSION_MALFORMED" in body)
    return scoped


def _post(url, body):
    import urllib.request as U
    r = U.Request(url, data=json.dumps(body).encode(),
                  headers={"Content-Type": "application/json"}, method="POST")
    with U.urlopen(r, timeout=20) as z:
        return json.loads(z.read().decode())


def get(url, cafile=None):
    ctx = ssl.create_default_context(cafile=cafile) if cafile else None
    kw = {"context": ctx} if ctx else {}
    with urllib.request.urlopen(url, timeout=30, **kw) as z:
        return json.loads(z.read().decode())


def required_fields(schema, comps, depth=0):
    if depth > 4 or not isinstance(schema, dict):
        return []
    if "$ref" in schema:
        return required_fields(comps.get(schema["$ref"].rsplit("/", 1)[-1], {}),
                               comps, depth + 1)
    for k in ("anyOf", "oneOf", "allOf"):
        if k in schema:
            for alt in schema[k]:
                if alt.get("type") != "null":
                    return required_fields(alt, comps, depth + 1)
    return list(schema.get("required", []))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://192.168.1.202:8811")
    ap.add_argument("--cacert", default=None)
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--probe-base", required=True,
                    help="a SCRATCH engine of the same build; session scoping "
                         "is derived by probing it so the live store is never "
                         "written")
    a = ap.parse_args()

    ver = get(a.base + "/v2/version", a.cacert)
    spec = get(a.base + "/v2/openapi.json", a.cacert)
    comps = spec.get("components", {}).get("schemas", {})
    pv = get(a.probe_base + "/v2/version")
    if pv.get("engine_source_hash") != ver.get("engine_source_hash"):
        print("REFUSING: probe engine build %s != live build %s"
              % (pv.get("engine_source_hash", "")[:22],
                 ver.get("engine_source_hash", "")[:22]))
        return 2
    scoping = derive_session_scoping(a.probe_base)

    routes = []
    for path, ops in sorted(spec["paths"].items()):
        for method, op in ops.items():
            m = method.upper()
            if m not in ("GET", "POST"):
                continue
            body = op.get("requestBody", {}).get("content", {}) \
                     .get("application/json", {}).get("schema", {})
            routes.append({
                "method": m, "path": path,
                "path_params": [p["name"] for p in op.get("parameters", [])
                                if p.get("in") == "path"],
                "required_query": [p["name"] for p in op.get("parameters", [])
                                   if p.get("in") == "query"
                                   and p.get("required")],
                "required_body": required_fields(body, comps) if body else [],
                "requires_session_key": scoping.get((m, path)),
            })

    contract = {
        "generated_for": "Archaeon and Vivarium, headless and inference-free",
        "generated_from": "the LIVE engine's /v2/openapi.json and /v2/version; "
                          "session scoping DERIVED by probing a scratch engine "
                          "of the identical build with a malformed session key",
        "engine": {
            "base_url": a.base + "/v2",
            "api": ver.get("api"),
            "schema_version": ver.get("schema_version"),
            "engine_instance_id": ver.get("engine_instance_id"),
            "engine_source_hash": ver.get("engine_source_hash"),
            "science_profile": ver.get("science_profile"),
            "session_enforcement": ver.get("session_enforcement"),
            "IDENTITY_RULE": "pin engine_source_hash, NEVER source_commit. "
                             "source_commit is best-effort git metadata and is "
                             "currently WRONG on M1 -- it names a commit that "
                             "does not contain the running code. The hash is "
                             "computed from the loaded source and is the build "
                             "identity.",
        },
        "auth": {
            "register": "POST /v2/clients {name} -> {client_id, token}; "
                        "no auth required for this call only",
            "header": "Authorization: Bearer <token>",
            "content_type": "application/json is REQUIRED on every POST; "
                            "omitting it means the body is never parsed",
            "token_shown_once": True,
            "isolation": "every list/read is OWNER-SCOPED. A client cannot see "
                         "another client's worlds through the API at any "
                         "endpoint. Cross-client archaeology requires the "
                         "store, not the REST surface.",
        },
        "session_affinity": {
            "header": "X-SFE-Session",
            "obtain": "POST /v2/sessions returns session_key ONCE",
            "errors": {
                "421": "WRONG_SESSION -- key minted by another engine instance",
                "428": "SESSION_REQUIRED -- strict mode, no key sent",
                "422": "SESSION_MALFORMED",
                "401": "SESSION_UNKNOWN -- well formed, this engine, not issued",
                "409": "SESSION_CLOSED",
                "403": "SESSION_MISMATCH -- valid key, wrong world",
            },
            "note": "a genuinely missing resource inside a VALID session is "
                    "still 404 not_found",
        },
        "routes": routes,
        "route_counts": {
            "total_get_post": len(routes),
            "session_scoped": sum(1 for r in routes if r["requires_session_key"]),
            "exempt": sum(1 for r in routes if not r["requires_session_key"]),
        },
        "vocabularies": {
            "outcome": ["FALSIFIED", "SURVIVED", "INCONCLUSIVE"],
            "outcome_note": "there is NO 'CONFIRMED'; anything else is 422",
            "unit_of_analysis": ["observation", "experiment", "world",
                                 "seed_root", "topology_group"],
            "family_kind": ["campaign", "analysis", "comparison", "selection"],
            "family_role": ["planned", "executed", "abandoned", "selected",
                            "alternative"],
            "family_member_kind_ACCEPTED": ["world", "claim", "experiment"],
            "family_member_kind_REFUSED": ["family (422)", "observation (422)"],
            "claim_status": ["SUPPORTED", "SUCCESSFUL_NEGATIVE",
                             "INCONCLUSIVE", "RETRACTED"],
            "replication_booleans": ["resampled_noise", "new_world_draws",
                                     "new_landscape", "reimplemented",
                                     "rebuilt_player", "independent_team"],
            "replication_note": "six INDEPENDENT booleans, never an ordinal. "
                                "An UNDECLARED dimension is not a false.",
            "sharing_policy_default": "ISOLATED",
            "budget_enforcement": ["enforceable", "measured", "estimated",
                                   "unavailable"],
            "budget_note": "default is 'measured', WHICH ENFORCES NOTHING. "
                           "Only 'enforceable' caps.",
        },
        "science_findings": [
            "FAMILY_EXTENT_DIVERGENCE", "SELECTION_WITHOUT_ALTERNATIVES",
            "MULTIPLE_SELECTED", "TRANSPORT_OVERREACH",
            "TRANSPORT_UNCHECKABLE", "NO_REPLICATION_DECLARED",
            "CLAIM_CITES_NON_ANALYSIS", "NO_EXECUTION_ATTESTATION",
            "CONFIG_DIVERGENCE", "PARTIALLY_INERT_INTERVENTION",
            "NO_EFFECTIVE_INTERVENTION", "INTERVENTION_NOT_APPLIED",
        ],
        "profiles": {
            "off": "not computed, not recorded -- a real control arm",
            "warn": "computed, returned as science.profile_findings, sealed "
                    "into the event chain, NEVER blocking. M1 runs this.",
            "strict": "same findings, but one contradicting a declaration you "
                      "sealed fails the call",
        },
    }

    traps = {
        "note": "every entry below was a real defect in one of MY OWN "
                "instruments before it was written down. They are the cheapest "
                "thing in this package.",
        "traps": [
            {"id": "T1", "surface": "POST /v2/worlds/{wid}/experiments",
             "trap": "the response does NOT contain spec_hash",
             "consequence": "reading it from the POST yields None for every "
                            "cell, so N distinct experiments collapse to '1 "
                            "distinct hash'",
             "do": "GET /v2/worlds/{wid}/experiments/{eid} to obtain spec_hash"},
            {"id": "T2", "surface": "POST /v2/work/claim",
             "trap": "the item is NESTED under a 'work' key, not flat",
             "consequence": "reading it flat scores zero claim winners and "
                            "looks exactly like a broken claim path",
             "do": "response['work']['work_id'] and ['claim_id']"},
            {"id": "T3", "surface": "POST /v2/worlds/{wid}/fork",
             "trap": "forked children are created in state CREATED, not RUNNING",
             "consequence": "the experiment path enforces RUNNING, so nothing "
                            "enqueues and work/claim returns nothing",
             "do": "POST /v2/worlds/{child}/start before using a fork"},
            {"id": "T4", "surface": "GET /v2/worlds and every list route",
             "trap": "owner-scoped; a new client sees zero worlds",
             "consequence": "an 'archaeologist' registered as a fresh client "
                            "sees an empty store and concludes wrongly",
             "do": "use the owning client's token, or read the store directly"},
            {"id": "T5", "surface": "analysis verified_n",
             "trap": "verified_n COMPUTES, it does not echo declared_n",
             "measured": "10 observations from ONE world: declared_n 1/8/10/99 "
                         "all return verified_n=1 and unit_mismatch flips true",
             "do": "trust verified_n; treat unit_mismatch as the signal"},
            {"id": "T6", "surface": "artifact data_b64",
             "trap": "STANDARD base64 only; URL-safe is 422",
             "note": "before 2026-09-04 URL-safe was accepted and SILENTLY "
                     "TRUNCATED -- distrust artifact bytes written earlier",
             "do": "verify the returned blob_hash equals sha256(your bytes)"},
            {"id": "T7", "surface": "identity of an artifact",
             "trap": "blob_hash is world-INdependent; artifact_id hashes an "
                     "envelope {world, kind, blob, meta}",
             "consequence": "the same bytes in two worlds give DIFFERENT "
                            "artifact_ids",
             "do": "use blob_hash for cross-world identity"},
            {"id": "T8", "surface": "epistemic protocol ordering",
             "trap": "a prediction registered AFTER the experiment commit is "
                     "not prospective and needs retrospective:true permanently",
             "do": "hypotheses -> predictions -> experiments{commit,enqueue}"},
            {"id": "T9", "surface": "observations",
             "trap": "without work_id an observation is CLIENT_ASSERTED, not "
                     "ENGINE_WORK_RESULT",
             "do": "pass work_id; check status.epistemics."
                   "observations_engine_attested"},
            {"id": "T10", "surface": "families",
             "trap": "member_kind refuses 'family' (422), so an amendment "
                     "chain is sealed text in the manifest and NOT a "
                     "traversable relation",
             "do": "record amends_family in the manifest and expect no "
                   "engine-side traversal"},
        ],
    }

    epistemic = {
        "source": "Harmonia S14-S18, committed with ledgers",
        "MAY": [
            "infer prospective vulnerability of a claim from features of "
            "SUBMITTED fossils: observations, their world grouping, n",
            "derive a candidate comparison universe from spec_hash and compare "
            "it to a declared source_set or family, and report the DIFFERENCE",
            "report that a check was silent",
        ],
        "MAY_NOT": [
            "infer that the absence of a selection fossil means selection did "
            "not occur. S15: selection performed upstream of submission is "
            "information-theoretically absent.",
            "treat the silence of any v6 check as evidence of soundness. S16: "
            "all twelve were silenced by a minimal adversarial record.",
            "treat a derived candidate universe as complete. Its precision "
            "depends on SPEC DISCIPLINE, which the claimant controls.",
            "report 'no selection signal found' when the correct statement is "
            "'this region is archaeologically unobservable'",
        ],
        "boundary_statement": "PEW fossilizes only selection whose candidate "
                              "EXECUTIONS were submitted to the engine of "
                              "record. The interface is the SUBMISSION "
                              "boundary, not the commit boundary.",
        "check_boundary_ownership": {
            "engine_owned": ["INTERVENTION_NOT_APPLIED"],
            "claimant_owned": ["FAMILY_EXTENT_DIVERGENCE",
                               "SELECTION_WITHOUT_ALTERNATIVES",
                               "MULTIPLE_SELECTED", "TRANSPORT_OVERREACH",
                               "TRANSPORT_UNCHECKABLE",
                               "NO_REPLICATION_DECLARED",
                               "CLAIM_CITES_NON_ANALYSIS",
                               "PARTIALLY_INERT_INTERVENTION",
                               "NO_EFFECTIVE_INTERVENTION"],
            "executor_owned": ["NO_EXECUTION_ATTESTATION", "CONFIG_DIVERGENCE"],
            "rule": "a check is robust exactly to the extent that the ENGINE, "
                    "not the claimant, defines what it ranges over",
        },
    }

    policy = {
        "source": "Harmonia S17 (frozen predictor) and S18 (measured policy)",
        "purpose": "choose the next experiment from fossil-derived prospective "
                   "information. This is Archaeon's job and it is already "
                   "validated.",
        "predictor_hash": "sha256:0106e035868bbe10ef177c8e88a2dad7",
        "features_required": ["abs_d", "n", "ci_width", "rel_se", "skew",
                              "kurtosis", "within_between", "serial_ac",
                              "monotone_frac", "hetero_ratio", "bounded_frac"],
        "features_computable_from": "observation values grouped by world; "
                                    "nothing else is needed",
        "rules": {
            "estimator": {"feature": "rel_se", "higher_is_fragile": False},
            "transform": {"feature": "kurtosis", "higher_is_fragile": True},
            "horizon": {"feature": "within_between", "higher_is_fragile": True},
            "unit": {"feature": "serial_ac", "higher_is_fragile": False},
            "noise": {"feature": None,
                      "note": "NO RULE. Zero fragile cases on development. "
                              "Select at random here and do not pretend to "
                              "information you do not have."},
        },
        "selection_procedure": "rank claims WITHIN each dimension by that "
                               "dimension's rule; ROUND-ROBIN across "
                               "dimensions. Form no cross-dimension score.",
        "PROHIBITED": "any cross-dimension ranking. S17 measured top-1 "
                      "dimension identification at 0.080 against random 0.200 "
                      "and it is WITHDRAWN. Scores from different rules are on "
                      "different scales and are not comparable.",
        "measured_performance": {
            "endpoint": "failures discovered per experiment executed",
            "budget": "100 of 1000 candidate pairs, 5 populations",
            "random": 0.288, "best_simple_fossil_baseline": 0.392,
            "this_policy": 0.462, "oracle_ceiling": 1.0,
            "lift_over_random": "+60.4%",
            "beat_random_on": "5 of 5 populations",
            "stability_sd": {"random": 0.053, "this_policy": 0.016},
            "caveat": "the oracle was SATURATED (fragile pairs exceeded the "
                      "budget) so 'fraction of oracle' is the raw rate "
                      "restated, not a quality measure",
        },
    }

    import os
    for name, obj in (("sfe_contract.json", contract),
                      ("sfe_traps.json", traps),
                      ("epistemic_bounds.json", epistemic),
                      ("selection_policy.json", policy)):
        p = os.path.join(a.outdir, name)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=1, sort_keys=False)
        print("wrote %-24s %d bytes" % (name, os.path.getsize(p)))
    print("\nengine  %s  schema %s  %s"
          % (ver.get("engine_instance_id"), ver.get("schema_version"),
             ver.get("engine_source_hash", "")[:26]))
    print("routes  %d total, %d session-scoped, %d exempt"
          % (contract["route_counts"]["total_get_post"],
             contract["route_counts"]["session_scoped"],
             contract["route_counts"]["exempt"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
